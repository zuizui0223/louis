#!/usr/bin/env python3
"""Fetch the open Black-tailed Godwit generality dataset from Dryad.

Dataset:
  Craft et al. 2024/2025
  DOI 10.5061/dryad.4tmpg4fm3

Only small CSV/README/script files are downloaded by default.
The multi-GB AKDE Rdata files are intentionally skipped.

The Dryad page currently exposes stable file-stream IDs for the two primary
small CSVs. These are used as a fallback if the API metadata route fails.

Resolved on 2026-10-04:
  habitat_use_df.csv -> file_stream/3568950
  location_data.csv  -> file_stream/3568952
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import urllib.parse
import urllib.request

DOI = "10.5061/dryad.4tmpg4fm3"
API = "https://datadryad.org/api/v2"

DIRECT_FALLBACKS = {
    "habitat_use_df.csv": "https://datadryad.org/downloads/file_stream/3568950",
    "location_data.csv": "https://datadryad.org/downloads/file_stream/3568952",
}

DEFAULT_KEEP = {
    "location_data.csv",
    "habitat_use_df.csv",
    "README.md",
    "scripts.zip",
}


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "louis-godwit-generality/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def download(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "louis-godwit-generality/1.0"})
    with urllib.request.urlopen(req, timeout=300) as r, dest.open("wb") as f:
        while True:
            block = r.read(1024 * 1024)
            if not block:
                break
            f.write(block)


def try_api_inventory() -> tuple[dict, list[dict]]:
    encoded = urllib.parse.quote(f"doi:{DOI}", safe="")
    dataset = get_json(f"{API}/datasets/{encoded}")
    versions_url = (dataset.get("_links") or {}).get("stash:versions", {}).get("href")
    if not versions_url:
        versions_url = f"{API}/datasets/{encoded}/versions"
    versions_url = urllib.parse.urljoin("https://datadryad.org", versions_url)

    versions = get_json(versions_url)
    embedded = versions.get("_embedded") or {}
    version_rows = embedded.get("stash:versions") or embedded.get("versions") or []
    if not version_rows:
        raise RuntimeError("Dryad returned no dataset versions")

    version = version_rows[-1]
    version_id = version.get("id")
    if version_id is None:
        raise RuntimeError("Dryad version has no id")

    files_meta = get_json(f"{API}/versions/{version_id}/files")
    fembed = files_meta.get("_embedded") or {}
    files = fembed.get("stash:files") or fembed.get("files") or []
    return {"version_id": version_id}, files


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="data/external/godwit_senegal")
    ap.add_argument("--metadata-only", action="store_true")
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    api_error = None
    version_meta = {}
    files = []
    try:
        version_meta, files = try_api_inventory()
    except Exception as exc:
        api_error = f"{type(exc).__name__}: {exc}"

    inventory = {}
    for row in files:
        path = str(row.get("path") or "")
        name = Path(path).name
        links = row.get("_links") or {}
        url = None
        for key in ("stash:download", "download"):
            item = links.get(key)
            if isinstance(item, dict) and item.get("href"):
                url = urllib.parse.urljoin("https://datadryad.org", item["href"])
                break
        if not url and row.get("id") is not None:
            url = f"https://datadryad.org/downloads/file_stream/{row['id']}"
        inventory[name] = {
            "id": row.get("id"),
            "path": path,
            "size": row.get("size"),
            "digest": row.get("digest"),
            "download_url": url,
        }

    for name, url in DIRECT_FALLBACKS.items():
        inventory.setdefault(name, {
            "id": url.rsplit("/", 1)[-1],
            "path": name,
            "size": None,
            "digest": None,
            "download_url": url,
            "source": "resolved Dryad page fallback",
        })

    audit = {
        "schema": "louis.godwit_dryad_fetch.v2",
        "doi": DOI,
        **version_meta,
        "api_error": api_error,
        "inventory": inventory,
        "requested_files": sorted(DEFAULT_KEEP),
        "resolved_primary_csv_fallbacks": DIRECT_FALLBACKS,
    }

    if not args.metadata_only:
        downloaded = []
        download_errors = []
        for name in sorted(DEFAULT_KEEP):
            row = inventory.get(name)
            if not row or not row.get("download_url"):
                continue
            dest = out / name
            try:
                download(str(row["download_url"]), dest)
                downloaded.append({"file": name, "bytes": dest.stat().st_size})
            except Exception as exc:
                dest.unlink(missing_ok=True)
                download_errors.append({
                    "file": name,
                    "url": str(row["download_url"]),
                    "error": f"{type(exc).__name__}: {exc}",
                })
        audit["downloaded"] = downloaded
        audit["download_errors"] = download_errors

    primary_ready = all((out / name).exists() for name in (
        "location_data.csv", "habitat_use_df.csv"
    ))
    audit["primary_csv_ready"] = primary_ready
    audit["status"] = (
        "READY_FOR_ANALYSIS"
        if primary_ready
        else "EXTERNAL_SOURCE_UNAVAILABLE"
    )

    (out / "dryad_metadata_audit.json").write_text(
        json.dumps(audit, indent=2), encoding="utf-8"
    )
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
