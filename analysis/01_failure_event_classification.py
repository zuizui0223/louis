#!/usr/bin/env python3
"""Classify the King Rail positive events that falsified EOG local worlds.

This is an ecological mechanism diagnostic, not an EOG validation rerun.

It opens ONLY the already-consumed KIRA response plus Sites.csv/Samples.csv from
the public USGS ScienceBase release. It does not open any of the other ten
species. The output separates:
  - same-site continuation,
  - same-site return after a detection gap,
  - first detection with nearby prior detected sites,
  - first detection outside prior observed-source support.

It also reproduces which of the six frozen local observed-source worlds fail on
each positive event. These are detection-source worlds, not latent-occupancy
worlds.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import math
from pathlib import Path
import urllib.request

ITEM_ID = "5ecf119d82ce30fd980854bd"
EXPECTED = {
    "Sites.csv": ("b2c125a786a222ebea5a4cdd5627306e", 1866),
    "Samples.csv": ("b719dc436a7fbbfdc2a1add11de2347a", 463),
    "KIRA.csv": ("3c959681e26599ea2a19030b7507837f", 2619),
}
THRESHOLDS_KM = (2.728021756372908, 2.976793133666009, 17.008648432743254)
EARTH_RADIUS_KM = 6371.0088


def get_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "louis-ecology/1.0"})
    with urllib.request.urlopen(req, timeout=60) as response:
        if int(getattr(response, "status", 200)) != 200:
            raise RuntimeError(f"HTTP failure for {url}")
        return response.read()


def fetch_files() -> dict[str, bytes]:
    item = json.loads(
        get_bytes(f"https://www.sciencebase.gov/catalog/item/{ITEM_ID}?format=json").decode("utf-8")
    )
    rows = {str(row.get("name") or ""): row for row in (item.get("files") or [])}
    out: dict[str, bytes] = {}
    for name, (md5_expected, size_expected) in EXPECTED.items():
        row = rows.get(name)
        if not row:
            raise RuntimeError(f"missing public asset: {name}")
        url = row.get("downloadUri") or row.get("url")
        if not url:
            raise RuntimeError(f"no download URL for {name}")
        payload = get_bytes(str(url))
        if len(payload) != size_expected:
            raise RuntimeError(f"{name} size mismatch: {len(payload)} != {size_expected}")
        md5 = hashlib.md5(payload).hexdigest()
        if md5 != md5_expected:
            raise RuntimeError(f"{name} md5 mismatch: {md5} != {md5_expected}")
        out[name] = payload
    return out


def haversine(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(h))


def parse(payloads: dict[str, bytes]):
    sites_rows = list(csv.DictReader(io.StringIO(payloads["Sites.csv"].decode("utf-8-sig"))))
    sample_rows = list(csv.DictReader(io.StringIO(payloads["Samples.csv"].decode("utf-8-sig"))))
    kira_rows = list(csv.DictReader(io.StringIO(payloads["KIRA.csv"].decode("utf-8-sig"))))

    coords = {
        row["Site"]: (float(row["Latitude"]), float(row["Longitude"]))
        for row in sites_rows
    }
    marsh = {row["Site"]: row["Marsh"] for row in sites_rows}
    habitat = {row["Site"]: row["Habitat"] for row in sites_rows}

    samples = []
    for row in sample_rows:
        d = dt.datetime.strptime(row["Date"], "%m/%d/%Y").date()
        samples.append((d, int(row["Sample Period"])))
    samples.sort()
    order = [period for _, period in samples]

    y: dict[tuple[str, int], int | None] = {}
    for row in kira_rows:
        site = row["Site"]
        if site not in coords:
            raise RuntimeError(f"response site not in registry: {site}")
        for period in range(1, 21):
            token = (row.get(str(period)) or "").strip()
            if token in {"", "NA", "NaN", "NAN", "NULL"}:
                y[(site, period)] = None
            elif token in {"0", "1"}:
                y[(site, period)] = int(token)
            else:
                raise RuntimeError(f"unexpected KIRA token {token!r} at {site}, period {period}")
    return coords, marsh, habitat, order, y


def min_distance(site: str, sources: set[str], coords: dict[str, tuple[float, float]]) -> float | None:
    if not sources:
        return None
    return min(haversine(coords[site], coords[src]) for src in sources)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="analysis/results/king_rail_failure_events")
    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    payloads = fetch_files()
    coords, marsh, habitat, order, y = parse(payloads)

    historical_positive: set[str] = set()
    previous_positive: set[str] = set()
    ever_positive: set[str] = set()
    records: list[dict[str, object]] = []
    first_failure: dict[str, dict[str, object] | None] = {
        f"geo{k}_{mode}": None
        for k in range(1, 4)
        for mode in ("immediate", "cumulative")
    }

    for occasion_index, period in enumerate(order):
        positives = {site for site in coords if y[(site, period)] == 1}
        for site in sorted(positives):
            same_prev = site in previous_positive
            same_hist = site in historical_positive
            d_prev = min_distance(site, previous_positive, coords)
            d_hist = min_distance(site, historical_positive, coords)

            if same_prev:
                event_type = "same_site_continuation"
            elif same_hist:
                event_type = "same_site_return_after_detection_gap"
            elif d_prev is not None and d_prev <= THRESHOLDS_KM[-1]:
                event_type = "first_detection_near_prior_positive"
            else:
                event_type = "first_detection_outside_prior_observed_support"

            row: dict[str, object] = {
                "occasion_index": occasion_index,
                "sample_period": period,
                "site": site,
                "marsh": marsh[site],
                "habitat": habitat[site],
                "event_type": event_type,
                "same_site_previous_positive": int(same_prev),
                "same_site_ever_positive": int(same_hist),
                "min_km_to_previous_positive": d_prev,
                "min_km_to_historical_positive": d_hist,
            }

            for k, threshold in enumerate(THRESHOLDS_KM, start=1):
                immediate_supported = d_prev is not None and d_prev <= threshold
                cumulative_supported = d_hist is not None and d_hist <= threshold
                # At initialization there is no pre-observation source history; do not use
                # period 1 to diagnose propagation-world failure.
                if occasion_index == 0:
                    immediate_supported = True
                    cumulative_supported = True
                row[f"geo{k}_immediate_supported"] = int(immediate_supported)
                row[f"geo{k}_cumulative_supported"] = int(cumulative_supported)
                for mode, supported in (
                    ("immediate", immediate_supported),
                    ("cumulative", cumulative_supported),
                ):
                    key = f"geo{k}_{mode}"
                    if not supported and first_failure[key] is None:
                        first_failure[key] = {
                            "occasion_index": occasion_index,
                            "sample_period": period,
                            "site": site,
                            "event_type": event_type,
                            "distance_km": d_prev if mode == "immediate" else d_hist,
                        }
            records.append(row)

        historical_positive |= positives
        ever_positive |= positives
        previous_positive = positives

    fields = list(records[0].keys()) if records else []
    with (out_dir / "positive_event_classification.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)

    event_counts: dict[str, int] = {}
    for row in records:
        key = str(row["event_type"])
        event_counts[key] = event_counts.get(key, 0) + 1

    unsupported_counts = {}
    for k in range(1, 4):
        for mode in ("immediate", "cumulative"):
            col = f"geo{k}_{mode}_supported"
            unsupported_counts[f"geo{k}_{mode}"] = sum(int(row[col]) == 0 for row in records)

    summary = {
        "schema": "louis.king_rail_failure_event_diagnostic.v1",
        "species": "Rallus elegans",
        "positive_events": len(records),
        "event_type_counts": event_counts,
        "unsupported_positive_counts_by_world": unsupported_counts,
        "first_failure_by_world": first_failure,
        "thresholds_km": list(THRESHOLDS_KM),
        "interpretation_rule": {
            "same_site_return_after_detection_gap": "directly compatible with persistent occupancy plus imperfect detection; not evidence of movement",
            "first_detection_outside_prior_observed_support": "mechanistically unresolved: can reflect prior nondetection, open-population movement, or unsampled intermediate habitat",
        },
        "claim_boundary": "Observed detections are not latent occupancy. This diagnostic identifies why detection-source worlds fail; it does not identify movement.",
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
