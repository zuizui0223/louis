# Second data-access route: 2025 King Rail movement supplement

## Source

Whetten et al. 2025, *Ecology and Evolution*  
DOI: 10.1002/ece3.72060

The article states that the King Rail movement data used in its examples are included with the submission material.

Publisher-named Supporting Information archive:

```text
ECE3-15-e72060-s001.zip
Appendices S1-S13
```

The archive is approximately 5.1 MB.

## Why this matters

The primary Lake Erie 2023 data/code release is cited at Zenodo 6604660, but the current execution environment has not resolved/downloaded that archive.

The 2025 supplement provides an **independent access route to at least part of the same King Rail movement material**.

This does not guarantee that the paired microhabitat/random plots are present.

## What the supplement can establish

If it contains:

```text
individual × timestamp × coordinates
```

then it can support:

- individual trajectory reconstruction;
- daily/fix-to-fix displacement;
- familiar-area stability;
- geographic relocation metrics.

If it also contains or can join to time-varying environmental-state data, it can support the stronger micro-niche tracking analysis.

## What it cannot establish by itself

Movement coordinates without matched habitat availability cannot estimate the primary Lake Erie State Retention Index.

SRI still requires:

```text
individual × event × used point × time-matched available point(s) × environmental state
```

## Executable scan

After obtaining the publisher ZIP:

```bash
python analysis/08_scan_bagged_movement_supplement.py \
  --zip <ECE3-15-e72060-s001.zip>
```

The scanner:

1. inventories every file;
2. searches for King Rail / *Rallus* content;
3. detects readable individual/time/latitude/longitude tables;
4. returns a fail-closed status.

## Access boundary

The publisher and PMC index confirm the supplement filename and that King Rail data are included, but this execution environment cannot currently download the ZIP from Wiley/PMC.

Do not claim file-level variables until the scanner has run on the actual archive.
