#!/usr/bin/env python3
"""Lake Erie King Rail hydrological availability-coupling analysis.

For matched event t:
  A_t = mean water depth of local random plots
  U_t = water depth of used/homing plot

Within birds, estimate the slope of U_t on A_t. A pseudo-used null is created
by choosing one matched random plot as pseudo-used at each event. The null slope
is therefore approximately one. A much smaller observed slope means that the
hydrological state actually experienced by the bird changes much less than
nearby available hydrological state.

This analysis does not use the unresolved coordinate-to-event join and therefore
does not claim that geographic displacement itself causes the buffering.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import re
import statistics
import urllib.request
from collections import defaultdict
from pathlib import Path

URL = (
    "https://zenodo.org/records/6604660/files/"
    "CARTdataset_12.31.21_All_D.csv?download=1"
)
ID_RE = re.compile(r"^(\d+)\.(\d+)(H|R)(\d+)(?:_(\d+))?_(\d{2})$")
BASE_SEED = 20261003


class XorShift32:
    def __init__(self, seed: int):
        self.state = seed & 0xFFFFFFFF
        if self.state == 0:
            self.state = 0x6D2B79F5

    def next_u32(self) -> int:
        x = self.state
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= x >> 17
        x ^= (x << 5) & 0xFFFFFFFF
        self.state = x & 0xFFFFFFFF
        return self.state

    def choice(self, values: list[float]) -> float:
        i = int((self.next_u32() / 4294967296.0) * len(values))
        return values[i]


def fnv1a32(text: str) -> int:
    h = 2166136261
    for ch in text:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return h


def fetch_rows() -> list[dict[str, str]]:
    req = urllib.request.Request(
        URL, headers={"User-Agent": "louis-availability-coupling/1.0"}
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        text = r.read().decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))


def slope(x: list[float], y: list[float]) -> float | None:
    if len(x) < 3:
        return None
    mx = statistics.mean(x)
    my = statistics.mean(y)
    den = sum((v - mx) ** 2 for v in x)
    if den <= 0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / den


def build_events(rows):
    events = {}
    qc = {"source_rows": len(rows), "missing_excluded": 0, "malformed_excluded": 0}
    for row in rows:
        if (row.get("Missing") or "").strip().lower() == "yes":
            qc["missing_excluded"] += 1
            continue
        sid = (row.get("ID") or "").strip()
        m = ID_RE.fullmatch(sid)
        if m is None:
            qc["malformed_excluded"] += 1
            continue
        try:
            depth = float(row["WaterDepth"])
        except Exception:
            continue
        bird = f"{m.group(2)}_{m.group(6)}"
        event_id = f"{bird}::{int(m.group(4))}"
        point_type = "used" if m.group(3) == "H" else "random"
        e = events.setdefault(
            event_id,
            {"bird": bird, "used": [], "random": []},
        )
        e[point_type].append(depth)

    birds = defaultdict(list)
    for e in events.values():
        if len(e["used"]) == 1 and len(e["random"]) >= 1:
            birds[e["bird"]].append(e)
    qc["valid_events"] = sum(len(v) for v in birds.values())
    qc["birds"] = len(birds)
    return birds, qc


def filter_condition(birds, condition: str):
    out = {}
    for bird, events in birds.items():
        keep = []
        for e in events:
            rr = list(e["random"])
            if condition == "conditional_flooded":
                rr = [v for v in rr if v > 0]
                if not rr:
                    continue
            elif condition == "all_points_flooded":
                if not (
                    e["used"][0] > 0
                    and rr
                    and all(v > 0 for v in rr)
                ):
                    continue
            keep.append({**e, "random": rr})
        if len(keep) >= 3:
            out[bird] = keep
    return out


def pooled_within_bird_slope(birds, picker=None):
    num = 0.0
    den = 0.0
    for bird, events in birds.items():
        avail = [statistics.mean(e["random"]) for e in events]
        used = [
            e["used"][0] if picker is None else picker(bird, e, i)
            for i, e in enumerate(events)
        ]
        ma = statistics.mean(avail)
        mu = statistics.mean(used)
        for a, u in zip(avail, used):
            num += (a - ma) * (u - mu)
            den += (a - ma) ** 2
    return None if den <= 0 else num / den


def score_condition(birds, condition, individual_reps, pooled_reps):
    filtered = filter_condition(birds, condition)
    individual = []
    for bird, events in sorted(filtered.items()):
        avail = [statistics.mean(e["random"]) for e in events]
        used = [e["used"][0] for e in events]
        observed = slope(avail, used)
        if observed is None:
            continue

        rng = XorShift32(BASE_SEED ^ fnv1a32(bird))
        null = []
        for _ in range(individual_reps):
            pseudo = [rng.choice(e["random"]) for e in events]
            b = slope(avail, pseudo)
            if b is not None and math.isfinite(b):
                null.append(b)

        null_med = statistics.median(null)
        p_lower = (sum(v <= observed for v in null) + 1) / (len(null) + 1)
        individual.append({
            "individual_id": bird,
            "n_events": len(events),
            "observed_used_on_availability_slope": observed,
            "pseudo_null_median_slope": null_med,
            "coupling_reduction": (
                None if null_med == 0 else 1.0 - observed / null_med
            ),
            "monte_carlo_add_one_p_lower": p_lower,
        })

    pooled_obs = pooled_within_bird_slope(filtered)
    rng = XorShift32(BASE_SEED ^ 0x88442211)
    pooled_null = []
    for _ in range(pooled_reps):
        b = pooled_within_bird_slope(
            filtered,
            lambda bird, e, i: rng.choice(e["random"]),
        )
        if b is not None and math.isfinite(b):
            pooled_null.append(b)

    null_med = statistics.median(pooled_null)
    pooled_p = (
        sum(v <= pooled_obs for v in pooled_null) + 1
    ) / (len(pooled_null) + 1)

    slopes = [r["observed_used_on_availability_slope"] for r in individual]
    reductions = [
        r["coupling_reduction"]
        for r in individual
        if r["coupling_reduction"] is not None
    ]

    return {
        "condition": condition,
        "birds": len(filtered),
        "events": sum(len(v) for v in filtered.values()),
        "pooled_within_bird": {
            "observed_slope": pooled_obs,
            "pseudo_null_median_slope": null_med,
            "coupling_reduction": (
                None if null_med == 0 else 1.0 - pooled_obs / null_med
            ),
            "monte_carlo_add_one_p_lower": pooled_p,
        },
        "individual_summary": {
            "median_observed_slope": statistics.median(slopes),
            "median_coupling_reduction": statistics.median(reductions),
            "birds_below_own_null_median": sum(
                r["observed_used_on_availability_slope"]
                < r["pseudo_null_median_slope"]
                for r in individual
            ),
            "birds_p_lt_0_05": sum(
                r["monte_carlo_add_one_p_lower"] < 0.05
                for r in individual
            ),
        },
        "individuals": individual,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--individual-reps", type=int, default=20000)
    ap.add_argument("--pooled-reps", type=int, default=20000)
    ap.add_argument(
        "--out",
        default="results/lake_erie_availability_coupling_v1.json",
    )
    args = ap.parse_args()

    birds, qc = build_events(fetch_rows())
    result = {
        "schema": "louis.lake_erie_availability_coupling_v1",
        "source": {
            "paper_doi": "10.1002/ece3.10043",
            "data_doi": "10.5281/zenodo.6604660",
            "table": "CARTdataset_12.31.21_All_D.csv",
        },
        "qc": qc,
        "metric": (
            "within-bird slope of used water depth on mean event-matched "
            "local random water depth"
        ),
        "null": (
            "choose one local random plot as pseudo-used at each real event "
            "and recompute the same within-bird slope"
        ),
        "primary": score_condition(
            birds, "primary", args.individual_reps, args.pooled_reps
        ),
        "conditional_flooded": score_condition(
            birds, "conditional_flooded", args.individual_reps, args.pooled_reps
        ),
        "all_points_flooded": score_condition(
            birds, "all_points_flooded", args.individual_reps, args.pooled_reps
        ),
        "interpretation": (
            "Observed slopes far below the pseudo-used null indicate that "
            "experienced water depth changes much less than nearby available water depth."
        ),
        "claim_boundary": (
            "This supports hydrological state buffering through realised habitat use. "
            "It does not prove that geographic displacement causes the buffering because "
            "coordinate-to-event linkage remains unresolved."
        ),
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
