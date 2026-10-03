#!/usr/bin/env python3
"""Standardize the open Lake Erie King Rail microhabitat table for matched-state tests.

Source:
  Zenodo DOI 10.5281/zenodo.6604660
  CARTdataset_12.31.21_All_D.csv

Source-defined rules:
- rows with Missing == Yes are excluded;
- HoR identifies Homing versus Random plots;
- WaterDepth is mean water depth.

The point ID encodes bird/year and matched event:
  165.020H1_21     -> bird 020_21, event 1, Homing
  165.020R1_1_21   -> bird 020_21, event 1, Random replicate 1

Malformed IDs are reported and excluded. They are never silently repaired.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
from pathlib import Path
import urllib.request

URL = (
    "https://zenodo.org/records/6604660/files/"
    "CARTdataset_12.31.21_All_D.csv?download=1"
)
ID_RE = re.compile(r"^(\d+)\.(\d+)(H|R)(\d+)(?:_(\d+))?_(\d{2})$")


def fetch_text(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "louis-state-fidelity/1.0"}
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode("utf-8-sig")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        default="analysis/derived/lake_erie_matched_water_depth.csv",
    )
    ap.add_argument(
        "--audit",
        default="analysis/results/lake_erie_standardization_audit.json",
    )
    args = ap.parse_args()

    source = list(csv.DictReader(io.StringIO(fetch_text(URL))))

    out_rows = []
    bad_ids = []
    missing_excluded = 0
    bad_depth = 0

    for row in source:
        if (row.get("Missing") or "").strip().lower() == "yes":
            missing_excluded += 1
            continue

        source_id = (row.get("ID") or "").strip()
        match = ID_RE.fullmatch(source_id)
        if match is None:
            bad_ids.append(source_id)
            continue

        try:
            depth = float(row["WaterDepth"])
            julian = int(float(row["Julian"]))
            year = int(float(row["Year"]))
        except Exception:
            bad_depth += 1
            continue

        bird_code = match.group(2)
        point_code = match.group(3)
        event_number = int(match.group(4))
        random_rep = match.group(5) or ""
        year_suffix = match.group(6)

        individual_id = f"{bird_code}_{year_suffix}"
        event_id = f"{individual_id}::{event_number}"

        out_rows.append({
            "source_id": source_id,
            "individual_id": individual_id,
            "event_id": event_id,
            "event_number": event_number,
            "point_type": "used" if point_code == "H" else "random",
            "random_rep": random_rep,
            "year": year,
            "julian": julian,
            "period": row.get("Period", ""),
            "water_depth_cm": depth,
        })

    fields = [
        "source_id", "individual_id", "event_id", "event_number",
        "point_type", "random_rep", "year", "julian", "period",
        "water_depth_cm",
    ]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out_rows)

    # Reconstruct matched events without outcome/model assumptions.
    events: dict[str, dict[str, object]] = {}
    for row in out_rows:
        e = events.setdefault(
            row["event_id"],
            {"used": 0, "random": 0, "years": set(), "julians": set()},
        )
        e[row["point_type"]] = int(e[row["point_type"]]) + 1
        e["years"].add(row["year"])
        e["julians"].add(row["julian"])

    valid = [
        k for k, e in events.items()
        if e["used"] == 1
        and e["random"] >= 1
        and len(e["years"]) == 1
        and len(e["julians"]) == 1
    ]

    audit = {
        "schema": "louis.lake_erie_standardization.v1",
        "source_rows": len(source),
        "missing_yes_excluded": missing_excluded,
        "malformed_id_excluded": len(bad_ids),
        "malformed_ids": bad_ids,
        "bad_water_depth_excluded": bad_depth,
        "standardized_rows": len(out_rows),
        "reconstructed_events": len(events),
        "valid_matched_events": len(valid),
        "individuals_with_valid_events": sorted(
            {k.split("::", 1)[0] for k in valid}
        ),
        "claim_boundary": (
            "Malformed source IDs are excluded rather than repaired. "
            "Only source-valid used/random matches enter the state-fidelity analysis."
        ),
    }
    audit_path = Path(args.audit)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")

    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
