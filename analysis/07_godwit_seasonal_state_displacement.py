#!/usr/bin/env python3
"""Godwit external-generality test: geography versus seasonal habitat state.

This is NOT the primary Lake Erie SRI test.

Inputs from Dryad DOI 10.5061/dryad.4tmpg4fm3:
  location_data.csv
  habitat_use_df.csv

The source study defines:
  wet season = July-November
  dry season = December-March.

For birds represented in both seasons, this script estimates:
  1. geographic shift between seasonal GPS centroids;
  2. Bray-Curtis dissimilarity between wet/dry habitat-composition vectors;
  3. whether each bird's own seasonal habitat pairing is more similar than
     cross-individual wet-to-dry pairings.

Interpretation:
- large geographic shift + low habitat dissimilarity is compatible with
  broad-scale environmental-state fidelity;
- large geographic shift + high habitat dissimilarity means birds changed both
  place and habitat composition, supporting seasonal resource tracking rather
  than "stay in state".

No claim is made that these seasonal land-cover classes equal the fine-scale
water-depth state used in the King Rail SRI hypothesis.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import random
from collections import defaultdict
from pathlib import Path

EARTH_RADIUS_KM = 6371.0088
SEED = 20261001
N_PERM = 50000


def parse_time(value: str) -> dt.datetime:
    v = value.strip().replace("Z", "+00:00")
    try:
        return dt.datetime.fromisoformat(v)
    except ValueError:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return dt.datetime.strptime(v, fmt)
            except ValueError:
                pass
    raise ValueError(f"unparseable timestamp {value!r}")


def season(t: dt.datetime) -> str | None:
    if 7 <= t.month <= 11:
        return "wet"
    if t.month in (12, 1, 2, 3):
        return "dry"
    return None


def spherical_centroid(points: list[tuple[float, float]]) -> tuple[float, float]:
    x = y = z = 0.0
    for lat, lon in points:
        la = math.radians(lat)
        lo = math.radians(lon)
        x += math.cos(la) * math.cos(lo)
        y += math.cos(la) * math.sin(lo)
        z += math.sin(la)
    n = len(points)
    x /= n
    y /= n
    z /= n
    lon = math.atan2(y, x)
    hyp = math.sqrt(x * x + y * y)
    lat = math.atan2(z, hyp)
    return math.degrees(lat), math.degrees(lon)


def haversine(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(h))


def bray_curtis(a: dict[str, float], b: dict[str, float]) -> float | None:
    keys = set(a) | set(b)
    denom = sum(a.get(k, 0.0) + b.get(k, 0.0) for k in keys)
    if denom <= 0:
        return None
    return sum(abs(a.get(k, 0.0) - b.get(k, 0.0)) for k in keys) / denom


def ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=values.__getitem__)
    out = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i + 1
        while j < len(order) and values[order[j]] == values[order[i]]:
            j += 1
        rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            out[order[k]] = rank
        i = j
    return out


def pearson(x: list[float], y: list[float]) -> float | None:
    if len(x) < 3:
        return None
    mx = sum(x) / len(x)
    my = sum(y) / len(y)
    sx = sum((v - mx) ** 2 for v in x)
    sy = sum((v - my) ** 2 for v in y)
    if sx <= 0 or sy <= 0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / math.sqrt(sx * sy)


def spearman(x: list[float], y: list[float]) -> float | None:
    return pearson(ranks(x), ranks(y))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data/external/godwit_senegal")
    ap.add_argument("--out", default="analysis/results/godwit_seasonal_state_displacement.json")
    args = ap.parse_args()

    root = Path(args.data_dir)
    loc_path = root / "location_data.csv"
    hab_path = root / "habitat_use_df.csv"
    if not loc_path.exists() or not hab_path.exists():
        raise SystemExit(
            "missing location_data.csv or habitat_use_df.csv; run "
            "analysis/06_fetch_godwit_generality_data.py first"
        )

    gps: dict[str, dict[str, list[tuple[float, float]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    with loc_path.open("r", encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            bird = (r.get("individual.local.identifier") or "").strip()
            if not bird:
                continue
            t = parse_time(r["timestamp"])
            s = season(t)
            if s is None:
                continue
            gps[bird][s].append((
                float(r["location.lat"]),
                float(r["location.long"]),
            ))

    habitat: dict[str, dict[str, dict[str, float]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    with hab_path.open("r", encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            bird = (r.get("bird") or "").strip()
            sraw = (r.get("Season") or "").strip().lower()
            if "wet" in sraw:
                s = "wet"
            elif "dry" in sraw:
                s = "dry"
            else:
                continue
            lc = (r.get("LC") or "").strip()
            if not bird or not lc:
                continue
            habitat[bird][s][lc] = habitat[bird][s].get(lc, 0.0) + float(r["percent"])

    birds = sorted(
        b for b in set(gps) & set(habitat)
        if gps[b].get("wet")
        and gps[b].get("dry")
        and habitat[b].get("wet")
        and habitat[b].get("dry")
    )

    rows = []
    for b in birds:
        wet_c = spherical_centroid(gps[b]["wet"])
        dry_c = spherical_centroid(gps[b]["dry"])
        geo = haversine(wet_c, dry_c)
        bc = bray_curtis(habitat[b]["wet"], habitat[b]["dry"])
        rows.append({
            "bird": b,
            "wet_gps_n": len(gps[b]["wet"]),
            "dry_gps_n": len(gps[b]["dry"]),
            "wet_centroid_lat": wet_c[0],
            "wet_centroid_lon": wet_c[1],
            "dry_centroid_lat": dry_c[0],
            "dry_centroid_lon": dry_c[1],
            "centroid_shift_km": geo,
            "wet_dry_habitat_bray_curtis": bc,
        })

    geo = [r["centroid_shift_km"] for r in rows if r["wet_dry_habitat_bray_curtis"] is not None]
    env = [r["wet_dry_habitat_bray_curtis"] for r in rows if r["wet_dry_habitat_bray_curtis"] is not None]
    rho = spearman(geo, env)

    # Individual-pairing null: is each bird's own wet->dry habitat vector more
    # similar than wet of that bird paired with another bird's dry vector?
    own = [
        bray_curtis(habitat[b]["wet"], habitat[b]["dry"])
        for b in birds
    ]
    own = [x for x in own if x is not None]
    observed_mean = sum(own) / len(own) if own else None

    rng = random.Random(SEED)
    null = []
    dry_birds = birds[:]
    if len(birds) >= 3 and observed_mean is not None:
        for _ in range(N_PERM):
            shuffled = dry_birds[:]
            rng.shuffle(shuffled)
            vals = [
                bray_curtis(habitat[w]["wet"], habitat[d]["dry"])
                for w, d in zip(birds, shuffled)
            ]
            vals = [x for x in vals if x is not None]
            if vals:
                null.append(sum(vals) / len(vals))

    p_low = (
        sum(v <= observed_mean for v in null) / len(null)
        if null and observed_mean is not None else None
    )

    result = {
        "schema": "louis.godwit_seasonal_state_displacement.v1",
        "source_doi": "10.5061/dryad.4tmpg4fm3",
        "n_paired_birds": len(rows),
        "individual_results": rows,
        "spearman_centroid_shift_vs_habitat_dissimilarity": rho,
        "own_wet_dry_mean_bray_curtis": observed_mean,
        "cross_individual_pairing_null": {
            "seed": SEED,
            "replicates": len(null),
            "p_own_pairing_more_similar": p_low,
        },
        "interpretation_rules": {
            "low_own_dissimilarity": (
                "compatible with individual environmental-state continuity across large spatial shifts"
            ),
            "high_own_dissimilarity": (
                "individuals changed both geographic position and broad habitat composition; "
                "this is seasonal resource tracking, not stay-in-state"
            ),
        },
        "claim_boundary": (
            "This uses seasonal core-area land-cover composition, not time-matched local availability "
            "or continuous water depth. It cannot substitute for the Lake Erie individual SRI test."
        ),
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
