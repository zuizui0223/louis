#!/usr/bin/env python3
"""Diagnose source initialization and memory duration in King Rail EOG failures.

Consumes the positive-event table created by 01_failure_event_classification.py.
This is a post-EOG ecological diagnostic, not an EOG validation rerun.

Key questions:
1. Did all local worlds fail because the observed-positive source set was empty
   before the first detection?
2. Once a first observed site seeds the system, how many later positives remain
   unsupported?
3. Does cumulative history support later positives much better than only the
   immediately previous occasion?
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

WORLD_KEYS = [
    "geo1_immediate",
    "geo1_cumulative",
    "geo2_immediate",
    "geo2_cumulative",
    "geo3_immediate",
    "geo3_cumulative",
]


def main(input_csv: Path, output_json: Path) -> None:
    rows = list(csv.DictReader(input_csv.open(encoding="utf-8")))
    if not rows:
        raise RuntimeError("positive-event table is empty")

    for row in rows:
        row["occasion_index"] = int(row["occasion_index"])
        row["sample_period"] = int(row["sample_period"])
        for key in WORLD_KEYS:
            row[f"{key}_supported"] = int(row[f"{key}_supported"])

    first_index = min(row["occasion_index"] for row in rows)
    first_rows = [row for row in rows if row["occasion_index"] == first_index]
    later = [row for row in rows if row["occasion_index"] > first_index]

    unsupported_all = {
        key: sum(row[f"{key}_supported"] == 0 for row in rows)
        for key in WORLD_KEYS
    }
    unsupported_after_seed = {
        key: sum(row[f"{key}_supported"] == 0 for row in later)
        for key in WORLD_KEYS
    }

    previously_known = [
        row for row in later
        if row["event_type"] in {
            "same_site_continuation",
            "same_site_return_after_detection_gap",
        }
    ]
    new_sites = [
        row for row in later
        if row["event_type"] in {
            "first_detection_near_prior_positive",
            "first_detection_outside_prior_observed_support",
        }
    ]
    returns_after_gap = [
        row for row in later
        if row["event_type"] == "same_site_return_after_detection_gap"
    ]

    first_detection_support = {}
    for key in WORLD_KEYS:
        first_detection_support[key] = {
            "new_site_events": len(new_sites),
            "supported": sum(row[f"{key}_supported"] == 1 for row in new_sites),
            "unsupported": sum(row[f"{key}_supported"] == 0 for row in new_sites),
        }

    result = {
        "schema": "louis.king_rail_initialization_memory_diagnostic.v1",
        "first_observed_positive_occasion": {
            "occasion_index": first_index,
            "sample_periods": sorted({row["sample_period"] for row in first_rows}),
            "sites": sorted({row["site"] for row in first_rows}),
            "positive_event_count": len(first_rows),
        },
        "positive_events": {
            "total": len(rows),
            "after_first_observed_positive_occasion": len(later),
            "later_at_previously_detected_sites": len(previously_known),
            "later_first_detections_at_new_sites": len(new_sites),
            "later_returns_after_detection_gap": len(returns_after_gap),
            "fraction_later_at_previously_detected_sites": (
                len(previously_known) / len(later) if later else None
            ),
        },
        "unsupported_positive_counts": {
            "including_initialization": unsupported_all,
            "after_first_observed_positive_seed": unsupported_after_seed,
        },
        "new_site_support_after_initialization": first_detection_support,
        "memory_contrast": {
            "geo1_immediate_minus_cumulative_unsupported_after_seed": (
                unsupported_after_seed["geo1_immediate"]
                - unsupported_after_seed["geo1_cumulative"]
            ),
            "geo2_immediate_minus_cumulative_unsupported_after_seed": (
                unsupported_after_seed["geo2_immediate"]
                - unsupported_after_seed["geo2_cumulative"]
            ),
            "geo3_immediate_minus_cumulative_unsupported_after_seed": (
                unsupported_after_seed["geo3_immediate"]
                - unsupported_after_seed["geo3_cumulative"]
            ),
        },
        "interpretation": {
            "initialization_test": (
                "If geo3 cumulative has zero unsupported later positives while failing "
                "only at the first observed positive, the original all-local-world "
                "falsification is primarily an initialization/latent-starting-state "
                "problem, not evidence that later detections require >17 km movement."
            ),
            "memory_test": (
                "If cumulative-history worlds support substantially more later positives "
                "than immediate-previous worlds, the relevant ecological memory persists "
                "longer than one sampling occasion."
            ),
            "claim_boundary": (
                "Observed history does not identify true occupancy. A cumulative observed "
                "source can proxy persistent site use, imperfect detection, habitat memory, "
                "or movement through unsampled marsh."
            ),
        },
        "next_test": (
            "Use a latent initial occupancy distribution rather than an empty observed-source "
            "state, then compare same-site persistence, cumulative site-use memory, local "
            "latent-neighbour state, and regional/open-population state."
        ),
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("analysis/results/king_rail_failure_events/positive_event_classification.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/king_rail_initialization_memory_diagnostic.json"),
    )
    args = parser.parse_args()
    main(args.input, args.output)
