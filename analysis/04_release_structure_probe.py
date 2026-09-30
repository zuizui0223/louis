#!/usr/bin/env python3
"""Probe the structure and join semantics of the open Lake Erie King Rail release.

This is intentionally descriptive. It does not fit models and does not assume
that CART microhabitat rows can be joined to telemetry tracks until the release
itself shows how.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path


TRACK_RE = re.compile(r"^(?P<bird>\d{3})_(?P<year>\d{2})\.csv$", re.I)


def read_rows(path: Path, n: int = 5):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, [])
        rows = []
        for _, row in zip(range(n), reader):
            rows.append(row)
        return header, rows


def dict_sample(path: Path, n: int = 5):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for _, row in zip(range(n), reader):
            rows.append(dict(row))
        return reader.fieldnames or [], rows


def main() -> None:
    root = Path("data/external/lake_erie_king_rail")
    out = Path("analysis/results/lake_erie_release_structure.json")
    out.parent.mkdir(parents=True, exist_ok=True)

    track_files = []
    for path in sorted(root.glob("*.csv")):
        m = TRACK_RE.match(path.name)
        if not m:
            continue
        header, sample = dict_sample(path, 4)
        row_count = 0
        dates = []
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_count += 1
                if "Date" in row and row["Date"]:
                    dates.append(row["Date"])
        track_files.append({
            "file": path.name,
            "bird_id_from_filename": m.group("bird"),
            "year_from_filename": "20" + m.group("year"),
            "header": header,
            "row_count": row_count,
            "first_date": min(dates) if dates else None,
            "last_date": max(dates) if dates else None,
            "sample": sample,
        })

    cart_path = root / "CARTdataset_12.31.21_All_D.csv"
    codes_path = root / "CARTdataset_Codes.csv"
    readme_path = root / "ReadMe.txt"
    r_paths = [root / "BrewerEtAl_CART.R", root / "BrewerEtAl_HomeRange.R"]

    cart_header, cart_sample = dict_sample(cart_path, 8)
    code_header, code_sample = dict_sample(codes_path, 12)
    readme = readme_path.read_text(encoding="utf-8-sig", errors="replace") if readme_path.exists() else ""

    r_evidence = {}
    terms = ["CARTdataset", "WaterDepth", "Julian", "HoR", "read.csv", "merge", "join", "ID"]
    for rp in r_paths:
        txt = rp.read_text(encoding="utf-8-sig", errors="replace") if rp.exists() else ""
        snippets = {}
        for term in terms:
            i = txt.lower().find(term.lower())
            if i >= 0:
                snippets[term] = txt[max(0, i-350): min(len(txt), i+1000)]
        r_evidence[rp.name] = snippets

    # Directly report candidate join keys; do not declare a join valid merely
    # because names appear similar.
    cart_ids = set()
    cart_years = set()
    cart_julians = set()
    with cart_path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("ID"):
                cart_ids.add(row["ID"].strip())
            if row.get("Year"):
                cart_years.add(row["Year"].strip())
            if row.get("Julian"):
                cart_julians.add(row["Julian"].strip())

    track_ids = {x["bird_id_from_filename"] for x in track_files}
    result = {
        "schema": "louis.lake_erie_release_structure.v1",
        "track_files": track_files,
        "track_id_count": len(track_ids),
        "track_ids": sorted(track_ids),
        "cart": {
            "header": cart_header,
            "sample": cart_sample,
            "id_values_sample": sorted(cart_ids)[:30],
            "year_values": sorted(cart_years),
            "julian_value_count": len(cart_julians),
        },
        "codes": {"header": code_header, "sample": code_sample},
        "readme": readme,
        "r_code_evidence": r_evidence,
        "join_diagnostic": {
            "track_filename_ids_intersect_cart_ID": sorted(track_ids & cart_ids),
            "track_filename_ids_only": sorted(track_ids - cart_ids),
            "cart_ID_only_sample": sorted(cart_ids - track_ids)[:30],
            "provisional_rule": (
                "A valid movement-habitat join still requires release-documented semantics "
                "linking CART ID/Julian/Year/HoR to individual telemetry locations."
            ),
        },
    }
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
