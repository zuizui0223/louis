#!/usr/bin/env python3
"""Flooded-availability sensitivity for Lake Erie King Rail state fidelity.

Post-hoc robustness question:
  Is the result driven only by random points that are dry (WaterDepth == 0)?

Two sensitivities:
1. conditional flooded availability:
   keep events with >=1 random point > 0 cm and sample only positive-depth randoms;
2. all-points-flooded:
   require used depth > 0 and every retained random depth > 0.

Both variance SRI and time-ordered successive-state retention are recomputed.
This is a robustness analysis, not a new primary endpoint.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

# Reuse the exact deterministic machinery from the canonical analysis.
from importlib.util import spec_from_file_location, module_from_spec

HERE = Path(__file__).resolve().parent
SPEC = spec_from_file_location(
    "lake_state",
    HERE / "09_lake_erie_state_fidelity.py",
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load canonical state-fidelity module")
M = module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def build_events(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    events = defaultdict(dict)
    for row in rows:
        ind = row["individual_id"].strip()
        eid = row["event_id"].strip()
        e = events[ind].setdefault(
            eid,
            {
                "used": [],
                "random": [],
                "year": int(row["year"]),
                "julian": int(row["julian"]),
                "event_number": int(row["event_number"]),
            },
        )
        e[row["point_type"]].append(float(row["water_depth_cm"]))

    out = {}
    for ind, ee in sorted(events.items()):
        valid = [
            e for e in ee.values()
            if len(e["used"]) == 1 and len(e["random"]) >= 1
        ]
        valid.sort(
            key=lambda e: (
                int(e["year"]),
                int(e["julian"]),
                int(e["event_number"]),
            )
        )
        if len(valid) >= 3:
            out[ind] = valid
    return out


def summarize(rows):
    return M.summarize(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--input",
        default="analysis/derived/lake_erie_matched_water_depth.csv",
    )
    ap.add_argument("--replicates", type=int, default=100000)
    ap.add_argument(
        "--out",
        default="results/lake_erie_flooded_availability_sensitivity_v1.json",
    )
    args = ap.parse_args()

    birds = build_events(Path(args.input))
    conditions = {
        "conditional_flooded": {},
        "all_points_flooded": {},
    }

    for bird, events in birds.items():
        conditional = []
        for e in events:
            rr = [x for x in e["random"] if x > 0]
            if rr:
                conditional.append({**e, "random": rr})

        all_flooded = [
            e for e in events
            if e["used"][0] > 0
            and e["random"]
            and all(x > 0 for x in e["random"])
        ]

        conditions["conditional_flooded"][bird] = conditional
        conditions["all_points_flooded"][bird] = all_flooded

    result = {
        "schema": "louis.lake_erie_flooded_availability_sensitivity_v1",
        "role": "post-hoc robustness against a trivial wet-versus-dry explanation",
        "conditions": {},
    }

    for name, by_bird in conditions.items():
        variance_rows = []
        temporal_rows = []
        for bird, events in sorted(by_bird.items()):
            if len(events) < 3:
                continue
            variance_rows.append(
                M.score_metric(
                    bird, events, "variance", False, args.replicates
                )
            )
            temporal_rows.append(
                M.score_metric(
                    bird, events, "successive_change", False, args.replicates
                )
            )

        result["conditions"][name] = {
            "variance_sri": {
                "summary": summarize(variance_rows),
                "individuals": variance_rows,
            },
            "temporal_state_retention": {
                "summary": summarize(temporal_rows),
                "individuals": temporal_rows,
            },
        }

    result["interpretation"] = (
        "Positive retention after conditioning on flooded availability shows that "
        "the primary result is not reducible to avoidance of dry random points."
    )
    result["boundary"] = (
        "This sensitivity was motivated after the primary result and is reported "
        "as robustness, not confirmatory evidence."
    )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
