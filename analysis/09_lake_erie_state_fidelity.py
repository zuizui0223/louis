#!/usr/bin/env python3
"""Lake Erie King Rail matched-availability environmental-state fidelity.

Primary quantity:
  SRI = 1 - Var(used water depth) / median Var(matched-random pseudo-trajectory)

Temporal quantity:
  transition retention
    = 1 - mean absolute successive used-depth change
          / median matched-random mean absolute successive change

The individual bird is the biological replication unit.

Monte Carlo uses a fixed xorshift32 implementation so results are exactly
portable across Python implementations and do not depend on Python's random
module. P-values use the add-one correction.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

BASE_SEED = 20261001


class XorShift32:
    def __init__(self, seed: int):
        self.state = seed & 0xFFFFFFFF
        if self.state == 0:
            self.state = 0x6D2B79F5

    def next_u32(self) -> int:
        x = self.state
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= (x >> 17) & 0xFFFFFFFF
        x ^= (x << 5) & 0xFFFFFFFF
        self.state = x & 0xFFFFFFFF
        return self.state

    def random(self) -> float:
        return self.next_u32() / 4294967296.0

    def choice(self, values: list[float]) -> float:
        idx = int(self.random() * len(values))
        return values[idx]


def fnv1a32(text: str) -> int:
    h = 2166136261
    for ch in text:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return h


def quantile(values: list[float], q: float) -> float:
    x = sorted(values)
    pos = (len(x) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return x[lo]
    w = pos - lo
    return x[lo] * (1 - w) + x[hi] * w


def variance(values: list[float]) -> float:
    return statistics.variance(values)


def mean_abs_successive_change(values: list[float]) -> float:
    return sum(
        abs(values[i] - values[i - 1])
        for i in range(1, len(values))
    ) / (len(values) - 1)


def binomial_sign_tail(n: int, k: int) -> float:
    return sum(
        math.comb(n, j) / (2 ** n)
        for j in range(k, n + 1)
    )


def score_metric(
    individual: str,
    events: list[dict[str, object]],
    metric: str,
    strict_two_random: bool,
    replicates: int,
) -> dict[str, object]:
    eligible = [
        e for e in events
        if (not strict_two_random or len(e["random"]) == 2)
    ]
    used = [float(e["used"][0]) for e in eligible]

    if metric == "variance":
        observed = variance(used)
        fn = variance
        salt = 0
    elif metric == "successive_change":
        observed = mean_abs_successive_change(used)
        fn = mean_abs_successive_change
        salt = 0xA5A5A5A5
    else:
        raise ValueError(metric)

    seed = (
        BASE_SEED
        ^ fnv1a32(individual)
        ^ (0x9E3779B9 if strict_two_random else 0)
        ^ salt
    ) & 0xFFFFFFFF
    rng = XorShift32(seed)

    null = []
    count_le = 0
    for _ in range(replicates):
        pseudo = [
            rng.choice(e["random"])
            for e in eligible
        ]
        value = fn(pseudo)
        null.append(value)
        if value <= observed:
            count_le += 1

    med = quantile(null, 0.5)
    retention = None if med == 0 else 1.0 - observed / med

    return {
        "individual_id": individual,
        "n_events": len(eligible),
        "n_two_random_events": sum(
            len(e["random"]) == 2 for e in eligible
        ),
        "observed": observed,
        "null_median": med,
        "null_q025": quantile(null, 0.025),
        "null_q975": quantile(null, 0.975),
        "retention": retention,
        "monte_carlo_count_le_observed": count_le,
        "monte_carlo_add_one_p": (count_le + 1) / (replicates + 1),
    }


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    values = [
        float(r["retention"])
        for r in rows
        if r["retention"] is not None
    ]
    positive = sum(v > 0 for v in values)
    return {
        "n_birds": len(values),
        "total_events": sum(int(r["n_events"]) for r in rows),
        "positive_retention_birds": positive,
        "median_retention": quantile(values, 0.5),
        "mean_retention": sum(values) / len(values),
        "min_retention": min(values),
        "max_retention": max(values),
        "one_sided_sign_test_p": binomial_sign_tail(len(values), positive),
        "individual_add_one_p_lt_0_05": [
            r["individual_id"]
            for r in rows
            if float(r["monte_carlo_add_one_p"]) < 0.05
        ],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--input",
        default="analysis/derived/lake_erie_matched_water_depth.csv",
    )
    ap.add_argument("--replicates", type=int, default=100000)
    ap.add_argument(
        "--out",
        default="results/lake_erie_state_fidelity_v1.json",
    )
    args = ap.parse_args()

    with Path(args.input).open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    events: dict[str, dict[str, dict[str, object]]] = defaultdict(dict)
    for row in rows:
        individual = row["individual_id"].strip()
        event_id = row["event_id"].strip()
        e = events[individual].setdefault(
            event_id,
            {
                "used": [],
                "random": [],
                "year": int(row["year"]),
                "julian": int(row["julian"]),
                "event_number": int(row["event_number"]),
            },
        )
        depth = float(row["water_depth_cm"])
        e[row["point_type"]].append(depth)

    by_bird: dict[str, list[dict[str, object]]] = {}
    invalid_events = []
    for individual, ee in sorted(events.items()):
        valid = []
        for event_id, e in ee.items():
            if len(e["used"]) == 1 and len(e["random"]) >= 1:
                valid.append(e)
            else:
                invalid_events.append({
                    "individual_id": individual,
                    "event_id": event_id,
                    "used_n": len(e["used"]),
                    "random_n": len(e["random"]),
                })
        valid.sort(
            key=lambda e: (
                int(e["year"]),
                int(e["julian"]),
                int(e["event_number"]),
            )
        )
        if len(valid) >= 3:
            by_bird[individual] = valid

    primary_variance = []
    strict_variance = []
    primary_transition = []
    strict_transition = []

    for bird, evs in sorted(by_bird.items()):
        primary_variance.append(
            score_metric(bird, evs, "variance", False, args.replicates)
        )
        strict_variance.append(
            score_metric(bird, evs, "variance", True, args.replicates)
        )
        primary_transition.append(
            score_metric(bird, evs, "successive_change", False, args.replicates)
        )
        strict_transition.append(
            score_metric(bird, evs, "successive_change", True, args.replicates)
        )

    result = {
        "schema": "louis.lake_erie_state_fidelity_v1",
        "source": {
            "paper_doi": "10.1002/ece3.10043",
            "data_doi": "10.5281/zenodo.6604660",
            "table": "CARTdataset_12.31.21_All_D.csv",
        },
        "replication_unit": "individual bird",
        "replicates_per_bird": args.replicates,
        "base_seed": BASE_SEED,
        "primary_sri": {
            "summary": summarize(primary_variance),
            "individuals": primary_variance,
        },
        "strict_two_random_sri": {
            "summary": summarize(strict_variance),
            "individuals": strict_variance,
        },
        "primary_temporal_state_retention": {
            "metric": "mean absolute successive water-depth change",
            "summary": summarize(primary_transition),
            "individuals": primary_transition,
        },
        "strict_two_random_temporal_state_retention": {
            "metric": "mean absolute successive water-depth change",
            "summary": summarize(strict_transition),
            "individuals": strict_transition,
        },
        "invalid_events_after_standardization": invalid_events,
        "interpretation": (
            "Positive retention means the sequence of water depths used by a "
            "bird is more stable than time-matched local random availability."
        ),
        "claim_boundary": (
            "This supports fine-scale environmental-state fidelity. "
            "The archived home-range coordinate CSVs do not carry event IDs, "
            "so the stronger geographic-displacement mechanism is not inferred "
            "until coordinate-to-event linkage is independently verified."
        ),
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
