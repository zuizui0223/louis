#!/usr/bin/env python3
"""Fetch the open Black-tailed Godwit generality dataset from Dryad.

Dataset:
  Craft et al. 2024/2025
  DOI 10.5061/dryad.4tmpg4fm3

Only the small CSV/README/script files are downloaded by default.
The multi-GB AKDE Rdata files are intentionally skipped.

Dryad API documentation:
  https://datadryad.org/api/v2/
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import urllib.parse
import urllib.request

DOI = "10.5061/dryad.4tmpg4fm3"
API = "https://datadryad.org/api/v2"
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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="data/external/godwit_senegal")
    ap.add_argument("--metadata-only", action="store_true")
    args = ap.parse_args()

    encoded = urllib.parse.quote(f"doi:{DOI}", safe="")
    dataset = get_json(f"{API}/datasets/{encoded}")
    versions_url = (dataset.get("_links") or {}).get("stash:versions", {}).get("href")
    if not versions_url:
        versions_url = f"{API}/datasets/{encoded}/versions"

    versions = get_json(versions_url)
    embedded = versions.get("_embedded") or {}
    version_rows = embedded.get("stash:versions") or embedded.get("versions") or []
    if not version_rows:
        raise RuntimeError("Dryad returned no dataset versions")

    # Use most recent version from API response.
    version = version_rows[-1]
    version_id = version.get("id")
    if version_id is None:
        raise RuntimeError("Dryad version has no id")

    files_meta = get_json(f"{API}/versions/{version_id}/files")
    fembed = files_meta.get("_embedded") or {}
    files = fembed.get("stash:files") or fembed.get("files") or []

    audit = {
        "schema": "louis.godwit_dryad_fetch.v1",
        "doi": DOI,
        "version_id": version_id,
        "available_files": [
            {
                "id": x.get("id"),
                "path": x.get("path"),
                "size": x.get("size"),
                "digest": x.get("digest"),
            }
            for x in files
        ],
        "requested_files": sorted(DEFAULT_KEEP),
    }

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "dryad_metadata_audit.json").write_text(
        json.dumps(audit, indent=2), encoding="utf-8"
    )

    if args.metadata_only:
        print(json.dumps(audit, indent=2))
        return

    downloaded = []
    for row in files:
        path = str(row.get("path") or "")
        name = Path(path).name
        if name not in DEFAULT_KEEP:
            continue
        file_id = row.get("id")
        links = row.get("_links") or {}
        url = None
        for key in ("stash:download", "download"):
            item = links.get(key)
            if isinstance(item, dict) and item.get("href"):
                url = item["href"]
                break
        if not url and file_id is not None:
            url = f"https://datadryad.org/downloads/file_stream/{file_id}"
        if not url:
            raise RuntimeError(f"no download link for {name}")
        dest = out / name
        download(url, dest)
        downloaded.append({"file": name, "bytes": dest.stat().st_size})

    audit["downloaded"] = downloaded
    (out / "dryad_metadata_audit.json").write_text(
        json.dumps(audit, indent=2), encoding="utf-8"
    )
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
