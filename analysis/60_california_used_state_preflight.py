#!/usr/bin/env python3
"""Pre-effect source-integrity and event-pairing preflight for USGS P9ELSUHN.

The source habitat counts are necessarily read to validate the one-hot and
availability data schema. This test reports no habitat-specific effects or
target-class distributions. The scientific protocol was frozen before access.
"""
from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import hashlib
import io
import json
import pathlib
import urllib.request

HERE = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = HERE / "analysis/contracts/california_temporal_state_fidelity_v1.json"
DEFAULT_OUT = HERE / "analysis/results/california_used_state_preflight_v1.json"
SOURCE_URLS = (
    "https://www.sciencebase.gov/catalog/file/get/652edfe8d34edd15305a9ab0?f=__disk__e2%2F6c%2F43%2Fe26c43b4947f0c7be05c13333a3592e1429bf8ab",
    "https://www.sciencebase.gov/catalog/file/get/652edfe8d34edd15305a9ab0?f=Data%20Release%20P9ELSUHN.csv",
)
CATS = ("Corn", "Field", "Other", "Rice", "Urban", "Wetland")
CASE_TRUE = {"true", "t", "1"}
CASE_FALSE = {"false", "f", "0"}


def fetch_source(path: pathlib.Path, spec: dict) -> str:
    if not path.exists():
        errors = []
        for url in SOURCE_URLS:
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": "louis-source-audit/1.0 (public academic verification)",
                    "Accept": "text/csv,application/octet-stream,*/*"
                })
                with urllib.request.urlopen(req, timeout=100) as res:
                    data = res.read(35000000)
                if len(data) == spec["bytes"] and hashlib.md5(data).hexdigest() == spec["md5"]:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(data)
                    break
                errors.append("response did not match pinned source size and MD5")
            except Exception as exc:
                errors.append(type(exc).__name__ + ": " + str(exc)[:160])
        else:
            raise ValueError("STOP_SOURCE_TRANSPORT_OR_INTEGRITY: " + "; ".join(errors))
    data = path.read_bytes()
    if len(data) != spec["bytes"] or hashlib.md5(data).hexdigest() != spec["md5"]:
        raise ValueError("STOP_SOURCE_MD5_OR_SIZE_MISMATCH")
    return data.decode("utf-8-sig")


def to_count(value: str) -> int:
    x = float(value)
    if not x.is_integer() or x < 0 or x > 100:
        raise ValueError("invalid categorical count")
    return int(x)


def timestamp(value: str) -> dt.datetime:
    s = value.strip().replace("Z", "+00:00")
    return dt.datetime.fromisoformat(s)


def audit_rows(rows: list[dict], expected: set[str]) -> dict:
    if not rows:
        return {"status": "STOP_EMPTY_SOURCE"}
    if not expected.issubset(set(rows[0])):
        return {"status": "STOP_SCHEMA_MISSING_SOURCE_COLUMNS", "missing": sorted(expected - set(rows[0]))}
    groups = collections.defaultdict(lambda: {"observed": [], "random": [], "bad": False})
    reasons = collections.Counter()
    for row in rows:
        try:
            key = (row["birdyear"].strip(), row["species"].strip(), row["timestamp"].strip())
            if not all(key):
                reasons["empty_event_key"] += 1
                continue
            case = row["case"].strip().lower()
            if case not in CASE_TRUE | CASE_FALSE:
                groups[key]["bad"] = True
                reasons["invalid_case_value"] += 1
                continue
            vals = tuple(to_count(row[c]) for c in CATS)
            if case in CASE_TRUE:
                groups[key]["observed"].append(vals)
            else:
                groups[key]["random"].append(vals)
        except (ValueError, TypeError, KeyError, AttributeError):
            reasons["invalid_habitat_count_or_key"] += 1
            continue

    by_bird = collections.defaultdict(list)
    species_events = collections.Counter()
    row_shapes = collections.Counter()
    qualified = 0
    for (bird, species, time), parts in groups.items():
        if parts["bad"]:
            reasons["invalid_group"] += 1
            continue
        if len(parts["observed"]) != 1:
            reasons["missing_or_duplicated_observed"] += 1
            continue
        used = parts["observed"][0]
        if sum(used) != 1 or sum(v == 1 for v in used) != 1:
            reasons["non_onehot_observed_six_states"] += 1
            continue
        if not parts["random"]:
            reasons["missing_random_availability"] += 1
            continue
        random_total = sum(sum(x) for x in parts["random"])
        if random_total < 20 or random_total > 100:
            reasons["random_total_outside_frozen_20_100"] += 1
            continue
        try:
            time_obj = timestamp(time)
        except Exception:
            reasons["timestamp_parse_failure"] += 1
            continue
        row_shapes[len(parts["random"])] += 1
        species_events[species] += 1
        qualified += 1
        by_bird[(bird, species)].append(time_obj)

    sp_summary = collections.defaultdict(lambda: {"eligible_events": 0, "eligible_one_hour_pairs": 0, "qualified_birdyears": 0})
    total_pairs = 0
    for (bird, species), times in by_bird.items():
        times.sort()
        pairs = sum(55 * 60 <= (b - a).total_seconds() <= 65 * 60 for a, b in zip(times, times[1:]))
        sp_summary[species]["eligible_events"] += len(times)
        sp_summary[species]["eligible_one_hour_pairs"] += pairs
        total_pairs += pairs
        if len(times) >= 31 and pairs >= 30:
            sp_summary[species]["qualified_birdyears"] += 1
    qualifying_species = sum(v["qualified_birdyears"] >= 5 for v in sp_summary.values())
    return {
        "status": "PASS_SOURCE_PAIRING_NO_EFFECT_ESTIMATE" if qualifying_species >= 2 else "STOP_INSUFFICIENT_INDIVIDUAL_REPLICATION",
        "source_rows": len(rows),
        "unique_event_keys": len(groups),
        "qualified_event_keys": qualified,
        "excluded_event_keys": len(groups) - qualified,
        "excluded_reason_counts": dict(reasons),
        "random_rows_per_paired_event_distribution": dict(row_shapes),
        "total_exact_hour_pairs": total_pairs,
        "by_species": dict(sp_summary),
        "species_with_at_least_5_birdyears": qualifying_species,
        "source_habitat_values_read_for_schema_validation": True,
        "primary_effect_estimated": False
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=pathlib.Path, default=pathlib.Path("/tmp/usgs_P9ELSUHN_frozen.csv"))
    p.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUT)
    a = p.parse_args()
    frozen = json.loads(CONTRACT.read_text(encoding="utf-8"))
    try:
        text = fetch_source(a.source, frozen["source"])
        rows = list(csv.DictReader(io.StringIO(text)))
        result = audit_rows(rows, set(frozen["schema_required"]))
        result["source_integrity"] = "PINNED_BYTES_AND_MD5_PASS"
    except Exception as exc:
        result = {"status": "STOP_ACCESS_OR_SCHEMA", "error": str(exc), "source_habitat_values_read_for_schema_validation": "unknown_or_false"}
    result["schema"] = "louis.california_used_state_preflight_v1"
    result["source_doi"] = frozen["source"]["doi"]
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS_SOURCE_PAIRING_NO_EFFECT_ESTIMATE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
