# Can public satellite data supply the missing abandoned-site control?

**Status as of 2026-10-22:** scene geometry and Landsat8 per-pixel QA feasibility PASS, but **prespecified Landsat-only-to-source temporal MNDWI calibration STOP**. No environmental retention/relocation benefit has been estimated. This is a methodological measurement-gate result in the independent USGS waterfowl archive `10.5066/P9XBZKZ8`.

## 2026-10-22 final measurement decision — calibration gate STOP

The prespecified comparison of Landsat8-only MNDWI against the original public USGS same-month Landsat8/Sentinel2 MNDWI has now been **executed**, not merely planned. [CI run #39722796913](https://github.com/zuizui0223/louis/actions/runs/39722796913) passed synthetic scale/QA tests, but its empirical decision is **`STOP_LANDSAT_SOURCE_MNDWI_NOT_COMPARABLE_OR_TEMPORAL_SIGNAL_WEAK`** under the frozen rules. Canonical [aggregate calibration result](../analysis/results/usgs_landsat8_source_mndwi_calibration_v1.json).

The true result is **11 independent tagged birds with two observed bird-month pairs each (22 paired month-point comparisons)**; median per-tag absolute error **0.174** (required ≤0.20), Pearson correlation **0.709** (required ≥0.60), and monthly-change sign agreement **5/8 = 62.5%** among source changes of absolute magnitude ≥0.10 (required ≥65% with ≥8 such tags). The last gate **fails**. Fifteen of sixteen birds had QA-observable pixels in both months, but five lacked an acceptable numeric Landsat green+SWIR1 source comparison in at least one observed month. Across sampled scenes, 69 provided valid observed-location Landsat indices, 29 had paired QA exclusion, and eight failed reflectance/denominator validity.

**Scientific consequence:** Do **not** calculate the old-patch versus moved-patch water-state benefit or claim birds actively regulate water exposure from this dataset. The QA 15/16 result remains a valid **availability/quality** finding, not a substitute for the **temporal measurement comparability** failure. The 62.5% matching sign rate is based on eight animals and is itself imprecise: it does not prove the two indices generally disagree, only that the frozen standard of sufficient temporal agreement was not attained here.

The source's mixed-sensor/GEE processing differs from independently recomputed Landsat8-only monthly composites. A **new, separately frozen** remote-sensing reconstruction that matches the source multi-sensor temporal compositor, or a fully independent fixed-location water sensor network, would be needed before reconsidering a genuine move-versus-stay effect. This completed result must not be rescued by relaxing the 65% rule, retroactively selecting later satellite scenes, broadening the source cohort or labeling missing MNDWI as dry. No bird-level environmental effect was estimated.

---

## Why this gate matters

The original moving-versus-staying question requires water-index observations at the old habitat patch during both the previous and the next calendar months. The USGS GPS table has time-stamped MNDWI only where tagged birds visited; consequently only **4 of 94 moving-month events / four birds** have an old-patch next-month observation by a different tagged bird within the frozen 100m radius. Its [old-site witness analysis](../analysis/results/usgs_monthly_core_geometry_gate_v1.json) correctly STOPPED the biological comparison. The source is not a hydrological null and missing water records are not imputed.

A complete date-matched satellite surface is one possible way to reconstruct *both abandoned and destination patches*. Before calculating any mover advantage we selected, without water-index outcomes, the **first 16 lexical tagged individuals** with a legitimate 500m–20km month-to-month modal-core relocation and froze the source QA protocol.

## Independently verified satellite feasibility

1. **STAC scene coverage:** Landsat-8 Collection-2 Level-2 scenes with footprints containing both core coordinates and whole-scene cloud `eo:cloud_cover ≤80%` were present in both months for **16/16** selected individual relocations. [Source-metadata run 39454129338](https://github.com/zuizui0223/louis/actions/runs/39454129338); [recorded JSON](../analysis/results/usgs_planetary_landsat_stac_pilot_v1.json).
2. **Per-pixel quality:** for **15/16** tags, each of the two consecutive months has at least one *same* Landsat-8 scene whose QA_PIXEL reports neither fill, dilated cloud, high-confidence cirrus/cloud, cloud shadow nor snow at **either core point**, with neither Green nor SWIR1 radiometrically saturated or terrain-obscured. This checks four space-time locations per individual. [Successful CI run 39722027181](https://github.com/zuizui0223/louis/actions/runs/39722027181); [frozen QA rule](../analysis/contracts/usgs_landsat8_qa_pixel_feasibility_v1.json); [machine-readable result](../analysis/results/usgs_landsat8_qa_pixel_feasibility_v1.json).

The fixed pixel-QA minimum was eight independent individuals; 15 passed. One of the sixteen lacked acceptable per-pixel QA in the previous calendar month despite scene-level coverage. This demonstrates why footprint or whole-scene cloud cover alone is not a sufficient source-quality gate.

**This is a success for satellite measurement coverage, not confirmation of environmental regulation by moving birds.** No Landsat Green or SWIR1 reflectance and no index benefit from moving versus staying were read during the two gate analyses.

## Remaining scientific identity problem: is Landsat-only MNDWI comparable to the published data?

The USGS source's original MNDWI was computed with within-calendar-month Landsat8/Sentinel2 composite imagery in Google Earth Engine; merely taking one Landsat8 Green/SWIR1 scene is not identical to the source measurement. We have therefore frozen a **measurement calibration at actually visited locations only**: for the exact same 16 tags, compare original median MNDWI from each month’s modal 250m core with the median of cloud/saturation-valid Landsat8 Green/SWIR1 SR-derived MNDWI at that core. Surface reflectance digital numbers must use USGS Collection 2 scale `0.0000275` and offset `−0.2`; MNDWI is `(Green−SWIR1)/(Green+SWIR1)` after scaling, not on raw DN.

The [predeclared calibration rule](../analysis/contracts/usgs_landsat8_source_mndwi_calibration_v1.json) requires ≥10 independent paired birds, median per-bird absolute error ≤0.20, Pearson r ≥0.60, and appropriate between-month direction consistency. **The frozen calibration was executed and failed its monthly direction gate (5/8 = 62.5%, required ≥65%); no old-site water-state benefit is reported.**

## Conservation/causal boundary

A complete optical water-index sequence would enable a stronger observational comparison: whether observed relocation retains the *previous water index* better than remaining at the former site through the next month. It still would not prove that the bird moved *in order to stabilize* the water environment, because habitat patches, spatial accessibility, seasonality, vegetation, management and unmeasured stressors affect both movement and water exposure.

The available source does not identify species for individuals; it cannot support a five-species phylogenetic or cross-species generalization. Do not bundle its measurement feasibility with the separate California four-species categorical endpoint findings as if these were the same inferential target.
