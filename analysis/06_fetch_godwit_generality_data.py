#!/usr/bin/env python3
"""Fetch the open Black-tailed Godwit generality dataset from Dryad.

Dataset:
  DOI 10.5061/dryad.4tmpg4fm3

Dryad deprecated automated use of the legacy /downloads/file_stream/{id}
route. Use the public v2 file API instead:

  GET /api/v2/files/{id}/download

Known current file IDs:
  habitat_use_df.csv  -> 3568950
  location_data.csv   -> 3568952

If these IDs change, the script rediscovers the current version/files through
the Dryad v2 API. Multi-GB AKDE files are intentionally skipped.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request

DOI = "10.5061/dryad.4tmpg4fm3"
API = "https://datadryad.org/api/v2"

KNOWN_FILE_IDS = {
    "habitat_use_df.csv": 3568950,
    "location_data.csv": 3568952,
}
DEFAULT_KEEP = set(KNOWN_FILE_IDS)


def absolute_url(url: str) -> str:
    if url.startswith("/"):
        return "https://datadryad.org" + url
    return url


def request(url: str) -> urllib.request.Request:
    return urllib.request.Request(
        absolute_url(url),
        headers={
            "User-Agent": "louis-godwit-generality/3.0",
            "Accept": "*/*",
        },
    )


def get_json(url: str) -> dict:
    with urllib.request.urlopen(request(url), timeout=120) as response:
        return json.load(response)


def download_file_id(file_id: int, dest: Path) -> str:
    url = f"{API}/files/{file_id}/download"
    with urllib.request.urlopen(request(url), timeout=300) as response, dest.open("wb") as out:
        while True:
            block = response.read(1024 * 1024)
            if not block:
                break
            out.write(block)
    if not dest.exists() or dest.stat().st_size == 0:
        raise RuntimeError(f"Dryad API returned empty file {file_id}")
    return url


def numeric_id_from_href(href: str | None, resource: str) -> int | None:
    if not href:
        return None
    m = re.search(rf"/{re.escape(resource)}/(\d+)(?:/|$)", str(href))
    return int(m.group(1)) if m else None


def link_href(obj: dict, key: str) -> str | None:
    item = (obj.get("_links") or {}).get(key)
    if isinstance(item, dict):
        href = item.get("href")
        return str(href) if href else None
    return None


def version_id_from_obj(obj: dict, fallback_href: str | None = None) -> int | None:
    raw = obj.get("id")
    if isinstance(raw, int):
        return raw
    if isinstance(raw, str) and raw.isdigit():
        return int(raw)
    for href in (
        link_href(obj, "self"),
        link_href(obj, "stash:version"),
        fallback_href,
    ):
        found = numeric_id_from_href(href, "versions")
        if found is not None:
            return found
    return None


def file_id_from_obj(obj: dict) -> int | None:
    raw = obj.get("id")
    if isinstance(raw, int):
        return raw
    if isinstance(raw, str) and raw.isdigit():
        return int(raw)
    for href in (
        link_href(obj, "self"),
        link_href(obj, "stash:download"),
    ):
        found = numeric_id_from_href(href, "files")
        if found is not None:
            return found
        # Legacy links may still expose the numeric file_stream id.
        if href:
            m = re.search(r"/file_stream/(\d+)", href)
            if m:
                return int(m.group(1))
    return None


def discover_via_api() -> dict:
    encoded = urllib.parse.quote(f"doi:{DOI}", safe="")
    dataset = get_json(f"{API}/datasets/{encoded}")

    current_href = link_href(dataset, "stash:version")
    version_id = numeric_id_from_href(current_href, "versions")

    if version_id is None and current_href:
        current = get_json(current_href)
        version_id = version_id_from_obj(current, current_href)

    if version_id is None:
        versions_href = link_href(dataset, "stash:versions")
        if not versions_href:
            versions_href = f"{API}/datasets/{encoded}/versions"
        versions = get_json(versions_href)
        embedded = versions.get("_embedded") or {}
        version_rows = embedded.get("stash:versions") or embedded.get("versions") or []
        candidates = [
            version_id_from_obj(row)
            for row in version_rows
            if isinstance(row, dict)
        ]
        candidates = [x for x in candidates if x is not None]
        if not candidates:
            raise RuntimeError(
                "Dryad API exposed versions but no numeric version id/self link"
            )
        version_id = candidates[-1]

    files_meta = get_json(f"{API}/versions/{version_id}/files")
    embedded = files_meta.get("_embedded") or {}
    files = embedded.get("stash:files") or embedded.get("files") or []

    discovered = {}
    audit_files = []
    for row in files:
        path = str(row.get("path") or "")
        name = Path(path).name
        file_id = file_id_from_obj(row)
        audit_files.append({
            "id": file_id,
            "path": path,
            "size": row.get("size"),
            "digest": row.get("digest"),
        })
        if name in DEFAULT_KEEP and file_id is not None:
            discovered[name] = file_id

    missing = DEFAULT_KEEP - set(discovered)
    if missing:
        raise RuntimeError(
            f"Dryad API did not resolve required files: {sorted(missing)}"
        )

    return {
        "version_id": version_id,
        "resolved_ids": discovered,
        "available_files": audit_files,
    }


def fetch_known(out: Path) -> tuple[list[dict], dict]:
    downloaded = []
    errors = {}
    for name, file_id in KNOWN_FILE_IDS.items():
        dest = out / name
        try:
            url = download_file_id(file_id, dest)
        except Exception as exc:
            errors[name] = repr(exc)
            break
        downloaded.append({
            "file": name,
            "file_id": file_id,
            "bytes": dest.stat().st_size,
            "source": url,
            "mode": "known_v2_file_api",
        })
    if errors:
        # Avoid accidentally mixing a partially downloaded known-ID set with
        # a rediscovered version.
        for name in KNOWN_FILE_IDS:
            (out / name).unlink(missing_ok=True)
        raise RuntimeError(json.dumps(errors))
    return downloaded, {"resolved_ids": KNOWN_FILE_IDS}


def fetch_discovered(out: Path) -> tuple[list[dict], dict]:
    audit = discover_via_api()
    downloaded = []
    for name in sorted(DEFAULT_KEEP):
        file_id = int(audit["resolved_ids"][name])
        dest = out / name
        url = download_file_id(file_id, dest)
        downloaded.append({
            "file": name,
            "file_id": file_id,
            "bytes": dest.stat().st_size,
            "source": url,
            "mode": "rediscovered_v2_file_api",
        })
    return downloaded, audit


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="data/external/godwit_senegal")
    ap.add_argument(
        "--rediscover",
        action="store_true",
        help="Skip known IDs and resolve the current version/files via Dryad API.",
    )
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    audit: dict[str, object] = {
        "schema": "louis.godwit_dryad_fetch.v3",
        "doi": DOI,
        "required_files": sorted(DEFAULT_KEEP),
        "known_file_ids": KNOWN_FILE_IDS,
        "download_endpoint": f"{API}/files/{{id}}/download",
    }

    if args.rediscover:
        downloaded, discovery = fetch_discovered(out)
    else:
        try:
            downloaded, discovery = fetch_known(out)
        except Exception as known_error:
            audit["known_id_error"] = repr(known_error)
            downloaded, discovery = fetch_discovered(out)

    audit["discovery"] = discovery
    audit["downloaded"] = downloaded
    (out / "dryad_metadata_audit.json").write_text(
        json.dumps(audit, indent=2), encoding="utf-8"
    )
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
