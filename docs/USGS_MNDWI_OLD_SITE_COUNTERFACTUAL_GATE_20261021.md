# Independent USGS monthly MNDWI movement–state counterfactual: geometry gate

**Date:** 2026-10-21. **Status:** `STOP_STATIC_WITNESS_GEOMETRIC_NONIDENTIFIABILITY`. This is a reproducible source/observation-design boundary, **not an ecological rejection** of habitat-state tracking.

## Question

Can a bird's relocation between consecutive months be compared with what would have happened **at its former location**, holding the calendar month fixed? Source: USGS DOI `10.5066/P9XBZKZ8`. Source-provided MNDWI is a same-month satellite composite at tagged GPS locations; unlike a complete raster, it is **not** measured at every unvisited location.

The frozen, before-water-outcomes protocol is [usgs_monthly_water_state_counterfactual_v1.json](../analysis/contracts/usgs_monthly_water_state_counterfactual_v1.json). It requires `Status=Local` GPS events, ≥5 valid locations within each month's modal 250-m core cell, exact adjacent calendar months, core displacement 500 m–20 km, and an **independent tagged bird** visiting within 100 m of the first month's former core site ≥3 times during the *destination month*. At least 10 independently tracked birds must pass this geometric/witness gate **before any MNDWI movement-benefit statistic can be computed**.

## Independently verified source

- Original source CSV: **30,403,945 bytes**, MD5 **3e5a91b2d5176cce43101ffcb6a60f25**, source metadata and structure verified in [CI run 39451520389](https://github.com/zuizui0223/louis/actions/runs/39451520389).
- Whole release: **224,888 GPS records**, **131 source bird identities**, **90 individuals with ≥2 calendar-month MNDWI observations**, **67 with ≥3 months**. No species labels in the public file.
- Local-only geometry: **103,543 unique tag/timestamp fixes** from **88 individual IDs**, **351 eligible monthly core-patch records**, **193 consecutive-month core comparisons**.
- Of those monthly comparisons, **94** had a modal core-patch relocation between 500 m and 20 km. Another **38** moved under 500 m; **61** exceeded 20 km.
- Old-site independent witness requirement: **4 transitions belonging to 4 focal tags** within 100 m, despite **415 other-bird source fixes** at those four matched neighborhoods. At the predefined 50-m sensitivity there were 4, and at 200 m there were **7 transitions / 7 tags**.
- Thus **90 of 94 relocation candidates** failed the required 100-m witness gate. Sample size for the preregistered counterfactual fell below the fixed **10-tag minimum**. This is not remedied by collecting more GPS fixes at the same four matched locations.

CI source of truth: [run 39452443095](https://github.com/zuizui0223/louis/actions/runs/39452443095), whose synthetic geometry tests and data source verification passed, while the final source geometry gate deliberately exited nonzero because the scientific sample threshold was not met. Canonical [machine result](../analysis/results/usgs_monthly_core_geometry_gate_v1.json).

## What this means ecologically

**Unidentified:** whether a mover experienced an MNDWI state closer to its previous month than it would have experienced by remaining in the old patch. The necessary monthly water state **at the abandoned patch** is missing in 90/94 candidate relocations, so the planned counterfactual `abs(W_old_next-W_previous)-abs(W_moved_next-W_previous)` was never calculated. A 200-m witness rule also does not reach the required N and is not a valid substitute for the originally fixed 100-m primary.

**Why this matters:** opportunistically sampling only abandoned patches revisited by another tagged bird is intrinsically selective. It overrepresents repeatedly used patches and need not characterize sites other birds avoided because they deteriorated. Labelling missing old-patch states as dry or unchanged would produce a spurious ecological conclusion.

**Next evidence required:** a complete, date-matched remote sensing MNDWI surface for *both* old and new GPS positions at months t and t+1, built with source-consistent cloud/water masking and spatial resolution, or repeated stationary water measurements. Only that supplies a genuine old-site environmental counterfactual without requiring another bird to visit. After that a separate predeclared test should compare mover vs stationary exposure while controlling movement accessibility and broad hydrological trends.

## Paper allocation

The original King Rail paper is a positive, independent temporal **water-depth buffering** test. The California four-waterfowl PR #2 is a positive but noncausal **categorical habitat continuity and opportunity–switch** analysis. The new USGS P9XBZKZ8 archive establishes **joinability of GPS + time-varying satellite MNDWI** but **not** a matched static-site counterfactual from the observed GPS points alone. Do not count this dataset as a third positive biological replication or postpone the already complete King Rail submission for it.
