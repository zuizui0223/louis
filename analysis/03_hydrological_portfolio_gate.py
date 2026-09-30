#!/usr/bin/env python3
"""Gate an independent King Rail dataset for the hydrological-portfolio test.

The full portfolio hypothesis requires temporally indexed movement AND dynamic
hydrological state. This script scans delimited text files and asks whether the
downloaded release contains joinable evidence for:

  individual x time x location x water depth/hydrological state

It does not treat static habitat heterogeneity as temporal complementarity.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ALIASES = {
    "individual": ["bird_id", "individual_id", "animal_id", "id", "tag_id", "bird"],
    "time": ["date_time", "datetime", "timestamp", "date", "time", "julian_date"],
    "latitude": ["latitude", "lat", "y"],
    "longitude": ["longitude", "lon", "long", "x"],
    "location": ["location", "point_id", "homing_point", "site", "station"],
    "water_depth": ["water_depth", "waterdepth", "depth", "water depth", "depth_cm"],
    "water_level": ["water_level", "waterlevel", "stage", "gauge_height"],
    "elevation": ["elevation", "elev", "dem"],
    "used_random": ["used", "use", "used_random", "point_type", "location_type", "random"],
}


def normalized(header: list[str]) -> dict[str, str]:
    return {h.strip().lower(): h for h in header}


def resolve(header: list[str]) -> dict[str, str | None]:
    low = normalized(header)
    out: dict[str, str | None] = {}
    for key, aliases in ALIASES.items():
        out[key] = next((low[a.lower()] for a in aliases if a.lower() in low), None)
    return out


def read_header(path: Path) -> list[str] | None:
    suffix = path.suffix.lower()
    if suffix not in {".csv", ".tsv", ".txt"}:
        return None
    delimiter = "\t" if suffix == ".tsv" else ","
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            return next(csv.reader(f, delimiter=delimiter))
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--out", default="analysis/results/kingrail_portfolio_gate.json")
    args = ap.parse_args()

    root = Path(args.data_dir)
    if not root.exists():
        raise SystemExit(f"missing data directory: {root}")

    tables = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        header = read_header(path)
        if not header:
            continue
        cols = resolve(header)
        tables.append({
            "path": str(path),
            "header": header,
            "resolved": cols,
            "has_individual": cols["individual"] is not None,
            "has_time": cols["time"] is not None,
            "has_location": (
                cols["location"] is not None
                or (cols["latitude"] is not None and cols["longitude"] is not None)
            ),
            "has_dynamic_hydrology": (
                cols["water_depth"] is not None or cols["water_level"] is not None
            ),
            "has_elevation": cols["elevation"] is not None,
            "has_used_random": cols["used_random"] is not None,
        })

    direct = [
        t for t in tables
        if t["has_individual"] and t["has_time"] and t["has_location"] and t["has_dynamic_hydrology"]
    ]

    movement_tables = [t for t in tables if t["has_individual"] and t["has_time"] and t["has_location"]]
    hydro_tables = [t for t in tables if t["has_time"] and t["has_dynamic_hydrology"]]

    if direct:
        status = "PASS_L1"
        reason = "at least one table directly contains individual, time, location and dynamic hydrology"
    elif movement_tables and hydro_tables:
        status = "PASS_JOIN_REQUIRED"
        reason = "movement and hydrology exist in separate tables; explicit temporal/spatial join must be validated"
    elif movement_tables:
        status = "STOP_DYNAMIC_HYDROLOGY_MISSING"
        reason = "movement is temporally indexed but no dynamic water-depth/water-level table was found"
    else:
        status = "STOP_MOVEMENT_SCHEMA"
        reason = "no delimited table contains individual x time x location"

    portfolio_ready = any(
        t["has_dynamic_hydrology"] and (t["has_elevation"] or t["has_used_random"])
        for t in tables
    ) and status in {"PASS_L1", "PASS_JOIN_REQUIRED"}

    result = {
        "schema": "louis.kingrail_hydrological_portfolio_gate.v1",
        "status": status,
        "reason": reason,
        "portfolio_ready_from_current_text_tables": portfolio_ready,
        "tables": tables,
        "next_gate": (
            "construct temporally matched usable-area A_ht and test HPI"
            if portfolio_ready
            else "do not compute HPI yet; obtain repeated habitat surface or joinable water-level/elevation data"
        ),
        "claim_boundary": (
            "Static microhabitat diversity is not temporal portfolio complementarity. "
            "HPI requires habitat suitability to vary through time within the familiar area."
        ),
    }

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
