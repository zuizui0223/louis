#!/usr/bin/env python3
"""Gate a King Rail release for the environmental-state fidelity test.

The gate is intentionally narrower than the older hydrological-portfolio gate.
It asks whether data can support the first direct test:

  individual x repeated event x used/random point x water depth

Coordinates are preferred for the secondary "move in space to stay in state"
test, but are not required for the primary State Retention Index.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

ALIASES = {
    "individual": [
        "bird_id", "individual_id", "animal_id", "tag_id", "transmitter_id",
        "bird", "id"
    ],
    "event": [
        "event_id", "homing_id", "homing_event", "homing_point_id",
        "location_id", "point_set", "sample_id"
    ],
    "date": [
        "date", "datetime", "date_time", "timestamp", "homing_date",
        "survey_date"
    ],
    "point_type": [
        "point_type", "location_type", "used_random", "use", "used",
        "random", "type"
    ],
    "water_depth": [
        "water_depth", "water_depth_cm", "waterdepth", "depth_cm",
        "depth", "mean_water_depth", "mean_depth"
    ],
    "latitude": ["latitude", "lat", "y"],
    "longitude": ["longitude", "lon", "long", "x"],
}


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.strip().lower()).strip("_")


def resolve(header: list[str]) -> dict[str, str | None]:
    lookup = {norm(h): h for h in header}
    result = {}
    for key, aliases in ALIASES.items():
        result[key] = next((lookup[norm(a)] for a in aliases if norm(a) in lookup), None)
    return result


def read_header(path: Path) -> list[str] | None:
    if path.suffix.lower() not in {".csv", ".tsv", ".txt"}:
        return None
    delim = "\t" if path.suffix.lower() == ".tsv" else ","
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            return next(csv.reader(f, delimiter=delim))
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--out", default="analysis/results/state_fidelity_schema_gate.json")
    args = ap.parse_args()

    root = Path(args.data_dir)
    if not root.exists():
        raise SystemExit(f"missing data directory: {root}")

    tables = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        h = read_header(p)
        if not h:
            continue
        r = resolve(h)
        primary = all(r[k] is not None for k in ("individual", "date", "point_type", "water_depth"))
        event_link = r["event"] is not None or r["date"] is not None
        coordinates = r["latitude"] is not None and r["longitude"] is not None
        tables.append({
            "path": str(p),
            "header": h,
            "resolved": r,
            "primary_state_fidelity_ready": primary and event_link,
            "geographic_tracking_ready": coordinates,
        })

    direct = [t for t in tables if t["primary_state_fidelity_ready"]]
    geo = [t for t in direct if t["geographic_tracking_ready"]]

    if geo:
        status = "PASS_STATE_AND_SPACE"
        next_step = "standardize used/random events and compute SRI plus geographic/environmental displacement"
    elif direct:
        status = "PASS_STATE_ONLY"
        next_step = "compute SRI; geographic move-in-space test needs a linked movement table"
    else:
        status = "STOP_SCHEMA"
        next_step = "identify or construct an event-linked table with individual, time, used/random point and water depth"

    result = {
        "schema": "louis.environmental_state_fidelity_gate.v1",
        "status": status,
        "tables": tables,
        "required_primary_columns": [
            "individual identifier",
            "repeated event/date",
            "used versus random point type",
            "water depth"
        ],
        "preferred_secondary_columns": ["latitude", "longitude"],
        "next_step": next_step,
        "claim_boundary": (
            "Primary state fidelity does not require a full hydrological surface. "
            "Full HPI/portfolio buffering remains ineligible unless dynamic habitat surfaces are reconstructed."
        ),
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
