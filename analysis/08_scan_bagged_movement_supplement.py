#!/usr/bin/env python3
"""Scan the 2025 bagged-movement Supporting Information for King Rail data.

Source article:
  Whetten et al. 2025, Ecology and Evolution
  DOI 10.1002/ece3.72060

Supporting archive named by the publisher:
  ECE3-15-e72060-s001.zip
  (Appendices S1-S13)

The paper states that the King Rail movement data used in the examples are
included with the submission material.

This script does not assume a file name. It inventories the ZIP, previews
tabular headers, and ranks candidate files containing individual/time/position
fields or King Rail keywords.

It does not infer microhabitat state. Movement-only files can support geographic
trajectory reconstruction but cannot replace the Lake Erie matched-availability
SRI test.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import zipfile
from pathlib import Path

ALIASES = {
    "individual": [
        "individual", "individual_id", "bird_id", "animal_id", "tag_id",
        "id", "bird", "transmitter"
    ],
    "time": [
        "timestamp", "datetime", "date_time", "date", "time"
    ],
    "latitude": [
        "latitude", "lat", "y"
    ],
    "longitude": [
        "longitude", "lon", "long", "x"
    ],
}


def norm(x: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", x.strip().lower()).strip("_")


def resolve(header: list[str]) -> dict[str, str | None]:
    low = {norm(h): h for h in header}
    out = {}
    for key, aliases in ALIASES.items():
        out[key] = next((low.get(norm(a)) for a in aliases if norm(a) in low), None)
    return out


def text_preview(zf: zipfile.ZipFile, name: str, max_bytes: int = 200_000) -> str:
    try:
        with zf.open(name) as f:
            b = f.read(max_bytes)
        return b.decode("utf-8-sig", errors="replace")
    except Exception:
        return ""


def header_from_text(name: str, text: str) -> list[str] | None:
    suffix = Path(name).suffix.lower()
    if suffix not in {".csv", ".tsv", ".txt"}:
        return None
    lines = text.splitlines()
    if not lines:
        return None
    delim = "\t" if suffix == ".tsv" else ","
    try:
        return next(csv.reader(io.StringIO(lines[0]), delimiter=delim))
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True)
    ap.add_argument(
        "--out",
        default="analysis/results/bagged_movement_supplement_scan.json"
    )
    args = ap.parse_args()

    zpath = Path(args.zip)
    if not zpath.exists():
        raise SystemExit(f"missing ZIP: {zpath}")

    rows = []
    with zipfile.ZipFile(zpath) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            name = info.filename
            lower_name = name.lower()
            preview = text_preview(zf, name)
            lower_preview = preview.lower()

            keywords = {
                "king": "king rail" in lower_preview or "kingrail" in lower_preview
                        or "king_rail" in lower_name or "kingrail" in lower_name,
                "rail": "rallus" in lower_preview or "rail" in lower_name,
            }

            header = header_from_text(name, preview)
            resolved = resolve(header) if header else {}
            has_track = bool(
                header
                and resolved.get("individual")
                and resolved.get("time")
                and resolved.get("latitude")
                and resolved.get("longitude")
            )

            score = 0
            if keywords["king"]:
                score += 4
            if keywords["rail"]:
                score += 2
            if has_track:
                score += 6
            if Path(name).suffix.lower() in {".csv", ".tsv", ".txt", ".rds", ".rdata", ".rda"}:
                score += 1

            rows.append({
                "path": name,
                "bytes": info.file_size,
                "suffix": Path(name).suffix.lower(),
                "keywords": keywords,
                "header": header,
                "resolved_columns": resolved,
                "individual_time_xy_ready": has_track,
                "candidate_score": score,
            })

    rows.sort(key=lambda r: (-r["candidate_score"], r["path"]))
    candidates = [r for r in rows if r["candidate_score"] >= 3]

    if any(r["individual_time_xy_ready"] and (r["keywords"]["king"] or r["keywords"]["rail"]) for r in rows):
        status = "PASS_KINGRAIL_TRACK_TABLE"
        next_step = "standardize individual x time x coordinates and connect to movement diagnostics"
    elif candidates:
        status = "PASS_CANDIDATE_FILES_NEED_EXTRACTION"
        next_step = "inspect top candidate files/R objects; movement data are present but not yet a directly readable track table"
    else:
        status = "STOP_NO_KINGRAIL_DATA_LOCATED"
        next_step = "do not infer that supplement contains usable individual trajectory data"

    result = {
        "schema": "louis.bagged_movement_supplement_scan.v1",
        "source_doi": "10.1002/ece3.72060",
        "status": status,
        "zip": str(zpath),
        "file_count": len(rows),
        "top_candidates": candidates[:30],
        "all_files": rows,
        "next_step": next_step,
        "claim_boundary": (
            "Movement coordinates alone cannot estimate environmental-state fidelity. "
            "They can reconstruct geographic movement and must be joined to time-varying "
            "microhabitat/availability before SRI-like claims."
        ),
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
