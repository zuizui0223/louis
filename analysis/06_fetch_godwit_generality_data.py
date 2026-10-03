#!/usr/bin/env python3
"""Fetch the open Black-tailed Godwit generality dataset from Dryad.

Dataset:
  Craft et al. 2024/2025
  DOI 10.5061/dryad.4tmpg4fm3

The Dryad landing page currently exposes stable file-stream IDs for the two
small CSVs needed here:

  habitat_use_df.csv  -> file_stream/3568950
  location_data.csv   -> file_stream/3568952

The script first attempts direct file-stream downloads. If Dryad changes those
IDs, it falls back to the Dryad v2 API to rediscover files.

The multi-GB AKDE Rdata files are intentionally not downloaded.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import urllib.parse
import urllib.request
import urllib.error

DOI = "10.5061/dryad.4tmpg4fm3"
API = "https://datadryad.org/api/v2"

DIRECT_FILES = {
    "habitat_use_df.csv": "https://datadryad.org/downloads/file_stream/3568950",
    "location_data.csv": "https://datadryad.org/downloads/file_stream/3568952",
}

DEFAULT_KEEP = set(DIRECT_FILES)


def absolute_url(url: str) -> str:
    if url.startswith("/"):
        return "https://datadryad.org" + url
    return url


def get_json(url: str) -> dict:
    url = absolute_url(url)
    req = urllib.request.Request(url, headers={"User-Agent": "louis-godwit-generality/1.0"})
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.load(response)


def download(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "louis-godwit-generality/1.0"})
    with urllib.request.urlopen(req, timeout=300) as response, dest.open("wb") as out:
        while True:
            block = response.read(1024 * 1024)
            if not block:
                break
            out.write(block)


def validate_nonempty(dest: Path) -> None:
    if not dest.exists() or dest.stat().st_size == 0:
        raise RuntimeError(f"download produced empty file: {dest}")


def direct_download(out: Path) -> list[dict[str, object]]:
    downloaded = []
    for name, url in DIRECT_FILES.items():
        dest = out / name
        download(url, dest)
        validate_nonempty(dest)
        downloaded.append({
            "file": name,
            "bytes": dest.stat().st_size,
            "source": url,
            "mode": "direct_file_stream",
        })
    return downloaded


def discover_via_api() -> dict:
    encoded = urllib.parse.quote(f"doi:{DOI}", safe="")
    dataset = get_json(f"{API}/datasets/{encoded}")

    current_url = (dataset.get("_links") or {}).get("stash:version", {}).get("href")
    version_id = None
    if current_url:
        current = get_json(current_url)
        version_id = current.get("id")

    if version_id is None:
        versions_url = (dataset.get("_links") or {}).get("stash:versions", {}).get("href")
        if not versions_url:
            versions_url = f"{API}/datasets/{encoded}/versions"
        versions = get_json(versions_url)
        embedded = versions.get("_embedded") or {}
        version_rows = embedded.get("stash:versions") or embedded.get("versions") or []
        if not version_rows:
            raise RuntimeError("Dryad returned no dataset versions")
        version_id = version_rows[-1].get("id")

    if version_id is None:
        raise RuntimeError("Dryad current version has no id")

    files_meta = get_json(f"{API}/versions/{version_id}/files")
    fembed = files_meta.get("_embedded") or {}
    files = fembed.get("stash:files") or fembed.get("files") or []

    return {
        "version_id": version_id,
        "files": files,
    }


def api_download(out: Path) -> tuple[list[dict[str, object]], dict[str, object]]:
    discovered = discover_via_api()
    files = discovered["files"]
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

        if url:
            url = absolute_url(str(url))
        if not url and file_id is not None:
            url = f"https://datadryad.org/downloads/file_stream/{file_id}"
        if not url:
            raise RuntimeError(f"no download link for {name}")

        dest = out / name
        try:
            download(str(url), dest)
        except urllib.error.HTTPError:
            if file_id is None:
                raise
            fallback = f"https://datadryad.org/downloads/file_stream/{file_id}"
            download(fallback, dest)
            url = fallback
        validate_nonempty(dest)
        downloaded.append({
            "file": name,
            "bytes": dest.stat().st_size,
            "source": str(url),
            "mode": "api_discovery",
        })

    missing = DEFAULT_KEEP - {str(x["file"]) for x in downloaded}
    if missing:
        raise RuntimeError(f"Dryad API did not resolve required files: {sorted(missing)}")

    audit = {
        "version_id": discovered["version_id"],
        "available_files": [
            {
                "id": x.get("id"),
                "path": x.get("path"),
                "size": x.get("size"),
                "digest": x.get("digest"),
            }
            for x in files
        ],
    }
    return downloaded, audit


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="data/external/godwit_senegal")
    ap.add_argument(
        "--api-only",
        action="store_true",
        help="Skip known direct file-stream IDs and rediscover through Dryad API.",
    )
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    audit: dict[str, object] = {
        "schema": "louis.godwit_dryad_fetch.v2",
        "doi": DOI,
        "required_files": sorted(DEFAULT_KEEP),
        "known_direct_file_streams": DIRECT_FILES,
    }

    if args.api_only:
        downloaded, api_audit = api_download(out)
        audit["api"] = api_audit
    else:
        try:
            downloaded = direct_download(out)
        except Exception as direct_error:
            audit["direct_download_error"] = repr(direct_error)
            downloaded, api_audit = api_download(out)
            audit["api"] = api_audit

    audit["downloaded"] = downloaded
    (out / "dryad_metadata_audit.json").write_text(
        json.dumps(audit, indent=2), encoding="utf-8"
    )
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
