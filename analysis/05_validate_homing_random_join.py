#!/usr/bin/env python3
"""Validate whether Lake Erie CART homing/random habitat rows align with telemetry fixes.

Expected release encoding from observed IDs:
  <prefix>.<bird><H|R><homing_index>[_<random_index>]_<yy>
Examples:
  165.020H1_21
  165.020R1_1_21

For bird-year track files with Date,X,Y, Date is Julian day. We test whether:
  - Homing Hn maps to row n of that bird-year track;
  - CART Julian equals track Date for Hn;
  - Random Rn_k rows share the same bird/year/homing index and Julian.

No ecological model is fit here.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ID_RE = re.compile(
    r"^(?P<prefix>\d+)\.(?P<bird>\d{3})(?P<kind>[HR])(?P<hpoint>\d+)"
    r"(?:_(?P<rand>\d+))?_(?P<yy>\d{2})$"
)
TRACK_RE = re.compile(r"^(?P<bird>\d{3})_(?P<yy>\d{2})\.csv$", re.I)


def read_dicts(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def to_int(value: str | None):
    try:
        return int(float(str(value).strip()))
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data/external/lake_erie_king_rail")
    ap.add_argument("--out", default="analysis/results/lake_erie_homing_random_join.json")
    args = ap.parse_args()

    root = Path(args.data_dir)
    cart_path = root / "CARTdataset_12.31.21_All_D.csv"
    if not cart_path.exists():
        raise SystemExit(f"missing CART table: {cart_path}")

    tracks = {}
    track_without_time = []
    for p in sorted(root.glob("*.csv")):
        m = TRACK_RE.match(p.name)
        if not m:
            continue
        rows = read_dicts(p)
        if not rows:
            continue
        has_date = "Date" in rows[0]
        key = (m.group("bird"), m.group("yy"))
        if has_date:
            tracks[key] = rows
        else:
            track_without_time.append({
                "file": p.name,
                "bird": m.group("bird"),
                "yy": m.group("yy"),
                "header": list(rows[0].keys()),
                "row_count": len(rows),
            })

    cart = read_dicts(cart_path)
    parsed = []
    unparsable = []
    for row in cart:
        raw = (row.get("ID") or "").strip()
        m = ID_RE.match(raw)
        if not m:
            unparsable.append(raw)
            continue
        d = m.groupdict()
        d.update({
            "raw_id": raw,
            "HoR": (row.get("HoR") or "").strip(),
            "Julian": to_int(row.get("Julian")),
            "Year": to_int(row.get("Year")),
            "WaterDepth": row.get("WaterDepth"),
        })
        d["hpoint"] = int(d["hpoint"])
        d["rand"] = int(d["rand"]) if d["rand"] else None
        parsed.append(d)

    groups = defaultdict(list)
    for r in parsed:
        groups[(r["bird"], r["yy"], r["hpoint"])].append(r)

    homing_checks = []
    random_checks = []
    exact_homing = 0
    eligible_homing = 0
    homing_missing_track = 0
    homing_index_out_of_range = 0
    homing_julian_mismatch = 0

    for r in parsed:
        if r["kind"] != "H":
            continue
        key = (r["bird"], r["yy"])
        track = tracks.get(key)
        if track is None:
            homing_missing_track += 1
            homing_checks.append({
                "id": r["raw_id"], "status": "NO_TIMED_TRACK",
                "bird": r["bird"], "yy": r["yy"], "hpoint": r["hpoint"],
                "cart_julian": r["Julian"],
            })
            continue
        eligible_homing += 1
        idx = r["hpoint"] - 1
        if idx < 0 or idx >= len(track):
            homing_index_out_of_range += 1
            homing_checks.append({
                "id": r["raw_id"], "status": "INDEX_OUT_OF_RANGE",
                "track_rows": len(track), "hpoint": r["hpoint"],
            })
            continue
        track_julian = to_int(track[idx].get("Date"))
        ok = track_julian == r["Julian"] and track_julian is not None
        if ok:
            exact_homing += 1
            status = "EXACT"
        else:
            homing_julian_mismatch += 1
            status = "JULIAN_MISMATCH"
        homing_checks.append({
            "id": r["raw_id"], "status": status,
            "bird": r["bird"], "yy": r["yy"], "hpoint": r["hpoint"],
            "cart_julian": r["Julian"], "track_julian": track_julian,
            "track_x": track[idx].get("X"), "track_y": track[idx].get("Y"),
        })

    random_total = 0
    random_exact_julian = 0
    homing_groups_with_random = 0
    homing_groups_without_random = 0
    for key, rows in sorted(groups.items()):
        h = [r for r in rows if r["kind"] == "H"]
        rs = [r for r in rows if r["kind"] == "R"]
        if h:
            if rs:
                homing_groups_with_random += 1
            else:
                homing_groups_without_random += 1
        if not h:
            for r in rs:
                random_checks.append({
                    "id": r["raw_id"], "status": "NO_MATCHED_HOMING"
                })
            continue
        hj = h[0]["Julian"]
        for r in rs:
            random_total += 1
            ok = r["Julian"] == hj and r["Julian"] is not None
            if ok:
                random_exact_julian += 1
            random_checks.append({
                "id": r["raw_id"],
                "status": "EXACT_JULIAN" if ok else "JULIAN_MISMATCH",
                "homing_id": h[0]["raw_id"],
                "homing_julian": hj,
                "random_julian": r["Julian"],
            })

    all_eligible_exact = (
        eligible_homing > 0
        and exact_homing == eligible_homing
        and homing_index_out_of_range == 0
        and homing_julian_mismatch == 0
    )
    all_random_exact = random_total > 0 and random_exact_julian == random_total

    if all_eligible_exact and all_random_exact:
        status = "PASS_EXACT_TIMED_SUBSET"
        reason = (
            "all CART Homing rows with timed bird-year tracks align exactly by "
            "Homing index and Julian day; matched Random rows share the same Julian day"
        )
    else:
        status = "PARTIAL"
        reason = "one or more track/CART temporal correspondences are unresolved or mismatched"

    result = {
        "schema": "louis.lake_erie_homing_random_join.v1",
        "status": status,
        "reason": reason,
        "cart_rows": len(cart),
        "parsed_cart_rows": len(parsed),
        "unparsable_cart_ids_count": len(unparsable),
        "unparsable_cart_ids_sample": unparsable[:20],
        "timed_track_files": len(tracks),
        "untimed_track_files": track_without_time,
        "homing": {
            "eligible_with_timed_track": eligible_homing,
            "exact_julian_index_matches": exact_homing,
            "missing_timed_track": homing_missing_track,
            "index_out_of_range": homing_index_out_of_range,
            "julian_mismatch": homing_julian_mismatch,
            "groups_with_random": homing_groups_with_random,
            "groups_without_random": homing_groups_without_random,
        },
        "random": {
            "rows": random_total,
            "exact_julian_matches_to_homing": random_exact_julian,
        },
        "homing_checks_sample": homing_checks[:50],
        "random_checks_sample": random_checks[:50],
        "ecological_boundary": (
            "A temporal match validates a paired used/available hydrological choice set. "
            "It does not by itself establish a full home-range habitat surface."
        ),
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
