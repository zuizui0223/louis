#!/usr/bin/env python3
"""Compute a first environmental-state fidelity statistic from standardized data.

Required standardized CSV columns:
  individual_id,event_id,point_type,water_depth_cm

point_type must contain one 'used' row and at least one 'random' row per event.

Optional:
  timestamp,latitude,longitude

The null preserves event timing and local availability by choosing one random
point per real event. No preferred water-depth window is estimated or tuned.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

REQUIRED = {"individual_id", "event_id", "point_type", "water_depth_cm"}


def variance(xs: list[float]) -> float | None:
    if len(xs) < 2:
        return None
    return statistics.variance(xs)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--replicates", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=20261001)
    ap.add_argument("--out", default="analysis/results/state_retention_index.json")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    with Path(args.input).open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        header = set(reader.fieldnames or [])
        missing = REQUIRED - header
        if missing:
            raise SystemExit(f"missing required columns: {sorted(missing)}")
        rows = list(reader)

    events: dict[str, dict[str, dict[str, list[float]]]] = defaultdict(
        lambda: defaultdict(lambda: {"used": [], "random": []})
    )
    for r in rows:
        ind = r["individual_id"].strip()
        event = r["event_id"].strip()
        kind = r["point_type"].strip().lower()
        try:
            depth = float(r["water_depth_cm"])
        except Exception:
            continue
        if "used" in kind or kind in {"u", "1"}:
            events[ind][event]["used"].append(depth)
        elif "random" in kind or kind in {"r", "0", "available", "availability"}:
            events[ind][event]["random"].append(depth)

    results = []
    for ind, ee in sorted(events.items()):
        valid = [
            x for _, x in sorted(ee.items())
            if len(x["used"]) == 1 and len(x["random"]) >= 1
        ]
        if len(valid) < 3:
            results.append({
                "individual_id": ind,
                "status": "INSUFFICIENT_EVENTS",
                "n_valid_events": len(valid),
            })
            continue

        used = [x["used"][0] for x in valid]
        v_used = variance(used)
        null_vars = []
        for _ in range(args.replicates):
            pseudo = [rng.choice(x["random"]) for x in valid]
            v = variance(pseudo)
            if v is not None:
                null_vars.append(v)

        null_median = statistics.median(null_vars)
        sri = None if null_median == 0 else 1.0 - (v_used / null_median)
        p_lower = sum(v <= v_used for v in null_vars) / len(null_vars)

        results.append({
            "individual_id": ind,
            "status": "SCORABLE",
            "n_valid_events": len(valid),
            "used_variance": v_used,
            "null_variance_median": null_median,
            "state_retention_index": sri,
            "randomization_p_lower_variance": p_lower,
        })

    scored = [r for r in results if r["status"] == "SCORABLE"]
    summary = {
        "schema": "louis.state_retention_index.v1",
        "replicates": args.replicates,
        "seed": args.seed,
        "n_individuals": len(results),
        "n_scorable": len(scored),
        "individual_results": results,
        "interpretation": (
            "Positive SRI means used water depth varied less through time than event-matched local availability. "
            "This is a test of experienced-state stabilization, not a claim of conscious target depth."
        ),
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
