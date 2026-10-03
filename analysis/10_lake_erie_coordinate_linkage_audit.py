#!/usr/bin/env python3
"""Audit whether Lake Erie King Rail coordinate rows can be joined to CART homing events.

The archive contains:
- CART microhabitat point IDs with bird/event numbers;
- one coordinate-only CSV per bird.

This script checks archive consistency only. It does NOT assume row order is an
event identifier unless the source explicitly documents that mapping.

Source DOI: 10.5281/zenodo.6604660
"""
from __future__ import annotations

import csv
import io
import json
import re
from pathlib import Path
import urllib.request

BASE = "https://zenodo.org/records/6604660/files"
CART = "CARTdataset_12.31.21_All_D.csv"
BIRDS = [
    "020_21", "332_20", "332_21", "361_21", "368_21",
    "390_21", "506_20", "856_20", "871_21", "881_20",
]
H_RE = re.compile(r"^(\d+)\.(\d+)H(\d+)_(\d{2})$")


def fetch(name: str) -> str:
    url = f"{BASE}/{name}?download=1"
    req = urllib.request.Request(url, headers={"User-Agent": "louis-coordinate-audit/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode("utf-8-sig")


def rows(text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(text)))


def main() -> None:
    cart = rows(fetch(CART))
    homing: dict[str, list[dict[str, object]]] = {}
    malformed = []

    for row in cart:
        if (row.get("HoR") or "").strip() != "Homing":
            continue
        source_id = (row.get("ID") or "").strip()
        m = H_RE.fullmatch(source_id)
        if m is None:
            malformed.append({
                "ID": source_id,
                "Missing": row.get("Missing"),
                "Julian": row.get("Julian"),
                "Year": row.get("Year"),
            })
            continue
        bird = f"{m.group(2)}_{m.group(4)}"
        homing.setdefault(bird, []).append({
            "event": int(m.group(3)),
            "missing": (row.get("Missing") or "").strip(),
        })

    audit = {}
    for bird in BIRDS:
        coord = rows(fetch(f"{bird}.csv"))
        hh = sorted(homing.get(bird, []), key=lambda x: int(x["event"]))
        ev = [int(x["event"]) for x in hh]
        max_ev = max(ev) if ev else None
        complete = (
            max_ev is not None
            and sorted(set(ev)) == list(range(1, max_ev + 1))
        )
        audit[bird] = {
            "coordinate_rows": len(coord),
            "homing_rows": len(hh),
            "min_homing_event": min(ev) if ev else None,
            "max_homing_event": max_ev,
            "complete_event_numbers_1_to_max": complete,
            "coordinate_rows_equals_homing_rows": len(coord) == len(hh),
            "coordinate_rows_equals_max_event": (
                max_ev is not None and len(coord) == max_ev
            ),
            "source_missing_homing_events": [
                int(x["event"])
                for x in hh
                if str(x["missing"]).lower() == "yes"
            ],
        }

    exact = [
        bird for bird, x in audit.items()
        if x["complete_event_numbers_1_to_max"]
        and x["coordinate_rows_equals_max_event"]
    ]

    result = {
        "schema": "louis.lake_erie_coordinate_linkage_audit.v1",
        "audit": audit,
        "malformed_homing_ids": malformed,
        "birds_with_exact_1_to_n_archive_structure": exact,
        "status": "HOLD_GEOGRAPHIC_EVENT_JOIN",
        "reason": (
            "Coordinate files contain no event/date IDs. Archive counts strongly suggest "
            "event-order structure for several birds, but the mapping is not uniformly "
            "documented or structurally exact across all birds."
        ),
        "rule": (
            "Do not silently join coordinates to CART homing events by row order. "
            "Require source documentation or a separate event-keyed coordinate table."
        ),
    }

    out = Path("analysis/results/lake_erie_coordinate_linkage_audit.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
