#!/usr/bin/env python3
"""Lake Erie King Rail: local hydrological heterogeneity as buffering opportunity.

Question
--------
Does fine-scale variation in locally available water depth help birds keep their
experienced water-depth state closer to their own typical state?

For each source-valid matched event with >=2 random plots:
    A_it = mean local random water depth
    H_it = max(random depth) - min(random depth)
    X_it = |A_it - median_i(A)|          # hydrological mismatch
    Y_it = |U_it - median_i(U)|          # experienced-state deviation

Primary model
-------------
Pooled within-bird fixed-effect regression:
    Y ~ X + H

Prediction:
    beta_H < pseudo-used null beta_H

A negative beta_H means that, conditional on how far mean local availability is
from the bird's usual available state, greater local hydrological heterogeneity
is associated with a smaller displacement of the state actually used.

Null
----
At each real event choose one of the matched random plots as pseudo-used,
recompute each bird's pseudo-used median, and refit the identical model. This
preserves the observed mismatch and local heterogeneity sequence.

Secondary model
---------------
    Y ~ X + H + X*H

A negative interaction is compatible with heterogeneity becoming especially
useful when mean local hydrology is unusual.

This is a post-hoc mechanism decomposition of the independent Lake Erie result.
It does not establish that birds sampled the random plots themselves or that
geographic movement caused the effect.
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
BASE_SEED = 20261008
SALT = 0x4C4F4348


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


def fetch_rows() -> list[dict[str, str]]:
    req = urllib.request.Request(
        URL, headers={"User-Agent": "louis-local-heterogeneity/1.0"}
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return list(csv.DictReader(io.StringIO(r.read().decode("utf-8-sig"))))


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
        typ = "used" if m.group(3) == "H" else "random"
        e = events.setdefault(event_id, {"bird": bird, "used": [], "random": []})
        e[typ].append(depth)

    birds = defaultdict(list)
    for e in events.values():
        if len(e["used"]) == 1 and len(e["random"]) >= 2:
            birds[e["bird"]].append(e)
    qc["eligible_two_random_events"] = sum(len(v) for v in birds.values())
    qc["birds"] = len(birds)
    return birds, qc


def solve_linear(a, b):
    """Small Gaussian solver for dense normal equations."""
    n = len(b)
    m = [list(map(float, a[i])) + [float(b[i])] for i in range(n)]
    for i in range(n):
        p = max(range(i, n), key=lambda j: abs(m[j][i]))
        if abs(m[p][i]) < 1e-12:
            return None
        m[i], m[p] = m[p], m[i]
        d = m[i][i]
        m[i] = [x / d for x in m[i]]
        for j in range(n):
            if j == i:
                continue
            f = m[j][i]
            m[j] = [x - f * y for x, y in zip(m[j], m[i])]
    return [m[i][-1] for i in range(n)]


def within_fit(rows, interaction=False):
    """Bird-demeaned pooled OLS; returns beta_X, beta_H[, beta_XH]."""
    cols = 3 if interaction else 2
    xtx = [[0.0] * cols for _ in range(cols)]
    xty = [0.0] * cols

    by = defaultdict(list)
    for r in rows:
        by[r["bird"]].append(r)

    n = 0
    for rr in by.values():
        raw = []
        for r in rr:
            vals = [r["X"], r["H"]]
            if interaction:
                vals.append(r["X"] * r["H"])
            raw.append((vals, r["Y"]))
        means = [
            statistics.mean(v[0][j] for v in raw)
            for j in range(cols)
        ]
        my = statistics.mean(v[1] for v in raw)
        for vals, y in raw:
            x = [vals[j] - means[j] for j in range(cols)]
            yc = y - my
            for i in range(cols):
                xty[i] += x[i] * yc
                for j in range(cols):
                    xtx[i][j] += x[i] * x[j]
            n += 1

    beta = solve_linear(xtx, xty)
    if beta is None:
        return None
    out = {"n_events": n, "beta_mismatch": beta[0], "beta_heterogeneity": beta[1]}
    if interaction:
        out["beta_mismatch_x_heterogeneity"] = beta[2]
    return out


def observed_rows(birds, pseudo_picker=None):
    rows = []
    for bird, events in birds.items():
        A = [statistics.mean(e["random"]) for e in events]
        H = [max(e["random"]) - min(e["random"]) for e in events]
        U = [
            e["used"][0] if pseudo_picker is None else pseudo_picker(e)
            for e in events
        ]
        medA = statistics.median(A)
        medU = statistics.median(U)
        for a, h, u in zip(A, H, U):
            rows.append({
                "bird": bird,
                "X": abs(a - medA),
                "H": h,
                "Y": abs(u - medU),
            })
    return rows


def lower_tail(null, obs):
    return (sum(v <= obs for v in null) + 1) / (len(null) + 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--replicates", type=int, default=50000)
    ap.add_argument(
        "--out",
        default="results/lake_erie_local_heterogeneity_insurance_v1.json",
    )
    args = ap.parse_args()

    birds, qc = build_events(fetch_rows())
    obs_rows = observed_rows(birds)
    primary = within_fit(obs_rows, interaction=False)
    secondary = within_fit(obs_rows, interaction=True)

    rng = XorShift32(BASE_SEED ^ SALT)
    null_h = []
    null_interaction = []
    for _ in range(args.replicates):
        rr = observed_rows(birds, pseudo_picker=lambda e: rng.choice(e["random"]))
        p = within_fit(rr, interaction=False)
        s = within_fit(rr, interaction=True)
        if p is not None and math.isfinite(p["beta_heterogeneity"]):
            null_h.append(p["beta_heterogeneity"])
        if s is not None and math.isfinite(s["beta_mismatch_x_heterogeneity"]):
            null_interaction.append(s["beta_mismatch_x_heterogeneity"])

    result = {
        "schema": "louis.lake_erie_local_heterogeneity_insurance_v1",
        "evidence_class": "posthoc_mechanism_decomposition",
        "source": {
            "paper_doi": "10.1002/ece3.10043",
            "data_doi": "10.5281/zenodo.6604660",
            "table": "CARTdataset_12.31.21_All_D.csv",
        },
        "qc": qc,
        "definitions": {
            "mismatch_X": "abs(mean matched-random depth - bird median matched-random mean depth)",
            "local_heterogeneity_H": "max matched-random depth - min matched-random depth at the same event",
            "experienced_deviation_Y": "abs(used depth - bird median used depth)",
        },
        "primary": {
            **primary,
            "pseudo_null_median_beta_heterogeneity": statistics.median(null_h),
            "monte_carlo_add_one_p_lower": lower_tail(
                null_h, primary["beta_heterogeneity"]
            ),
            "prediction": "beta_heterogeneity below pseudo-used null",
        },
        "secondary_interaction": {
            **secondary,
            "pseudo_null_median_interaction": statistics.median(null_interaction),
            "monte_carlo_add_one_p_lower": lower_tail(
                null_interaction,
                secondary["beta_mismatch_x_heterogeneity"],
            ),
            "prediction": "negative mismatch x heterogeneity interaction",
        },
        "monte_carlo": {
            "replicates": args.replicates,
            "seed": BASE_SEED,
            "portable_rng": "xorshift32",
        },
        "interpretation": (
            "Support would be compatible with local hydrological heterogeneity providing "
            "behaviorally accessible insurance: at the same degree of mean hydrological "
            "mismatch, more heterogeneous local availability is associated with less "
            "experienced-state displacement than expected from pseudo-use of the same local plots."
        ),
        "claim_boundary": [
            "This is post-hoc mechanism decomposition, not a preregistered independent test.",
            "Two matched random plots provide only a sparse proxy for local hydrological heterogeneity.",
            "Random plots are availability samples, not locations proven to have been visited by the bird.",
            "No coordinate-event join is used; geographic movement is not inferred.",
        ],
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
