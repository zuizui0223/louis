#!/usr/bin/env python3
"""Audit or download the independent Lake Erie King Rail data release.

Default behavior is metadata/schema discovery only. Data files are downloaded
only with --download.

Source:
  Zenodo record 6604660
  DOI 10.5281/zenodo.6604660
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import urllib.request

RECORD_ID = 6604660
API = f"https://zenodo.org/api/records/{RECORD_ID}"


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "louis-hydrological-portfolio/1.0"})
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.load(response)


def download(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "louis-hydrological-portfolio/1.0"})
    with urllib.request.urlopen(req, timeout=300) as response, dest.open("wb") as out:
        while True:
            block = response.read(1024 * 1024)
            if not block:
                break
            out.write(block)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--download", action="store_true")
    ap.add_argument("--out-dir", default="data/external/lake_erie_king_rail")
    args = ap.parse_args()

    meta = fetch_json(API)
    files = meta.get("files") or []
    audit = {
        "record_id": RECORD_ID,
        "doi": meta.get("doi") or meta.get("pids", {}).get("doi", {}).get("identifier"),
        "title": (meta.get("metadata") or {}).get("title"),
        "files": [],
        "portfolio_gate": {
            "required_after_download": [
                "individual identifier",
                "date or timestamp",
                "telemetry location or location identifier",
                "time-varying water depth or linkable hydrological state"
            ],
            "strongly_preferred": [
                "alternative/random-point habitat observations matched in time",
                "home-range geometry",
                "managed water-level or elevation data"
            ]
        }
    }

    for f in files:
        links = f.get("links") or {}
        audit["files"].append({
            "key": f.get("key"),
            "size": f.get("size"),
            "checksum": f.get("checksum"),
            "content_url": links.get("content") or links.get("self"),
        })

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "zenodo_metadata_audit.json").write_text(
        json.dumps(audit, indent=2), encoding="utf-8"
    )

    if not args.download:
        print(json.dumps(audit, indent=2))
        print("Metadata audit complete; pass --download to fetch public files.")
        return

    for row in audit["files"]:
        key = row["key"]
        url = row["content_url"]
        if not key or not url:
            continue
        dest = out_dir / Path(str(key)).name
        download(str(url), dest)
        print(f"downloaded: {dest}")


if __name__ == "__main__":
    main()
