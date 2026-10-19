# Four California waterfowl show endpoint-state continuity beyond a static habitat-preference reference

**Status:** verified developmental natural-data result, 19 October 2026. This is a separate *categorical temporal endpoint* test, NOT a replication of King Rail hydrological SRI and NOT origin→destination state preservation. Source, code and sampling audit are in this repository; the successful authoritative run is [GitHub Actions 39216459095](https://github.com/zuizui0223/louis/actions/runs/39216459095).

## Ecological question

Does the categorical habitat of successive approximately hourly **used moving-step destinations** persist more often than expected from (a) the habitat composition of time-matched **available destinations**, or (b) independent choices driven by each bird-year's **fixed overall habitat preference** applied to the same available-destination composition?

## Public data and strict eligibility

- USGS P9ELSUHN, Overton & Casazza (2023), DOI `10.5066/P9ELSUHN`; original file MD5 `78eb6064eca992225d6907d6e46f5bef`, 27,997,528 bytes and 380,578 rows.
- One observed destination and aggregated available destination counts at 190,289 source event keys; 189,851 qualified, 438 removed by frozen habitat state/available-count gates.
- Seven **source-defined exclusive** habitat categories: Corn, Field, Other, Protected, Rice, Urban and Wetland. The original v1 six-class schema stopped, and the seven-class and US-date parser were corrected from source documentation *before any continuity effect was calculated*. Archived source tests remain part of provenance.
- Restrict to successive eligible event times **55–65 minutes apart**, at least 30 such pairs and 31 eligible records per `species × birdyear`, with no cross-gap fabricated continuity.
- **329 eligible birdyears** across 4 species. We treat one birdyear, not one pair or one of the 100 random destinations, as the statistical reporting unit. A bird tracked across different years might contribute more than once; the source `birdyear` field does not by itself establish independent marked-bird identities across years.

## Results

| Species | Birdyears | 1-h used destination match | Availability-only expected | Fixed-preference expected | Excess above static preference (95% birdyear bootstrap CI) |
|---|---:|---:|---:|---:|---:|
| Greater white-fronted goose (*Anser albifrons*) | 99 | 67.0% | 42.3% | 53.3% | **+13.7 pp** (12.5–14.9) |
| Lesser snow goose (*Anser caerulescens caerulescens*) | 155 | 75.8% | 47.9% | 59.9% | **+16.0 pp** (15.1–16.9) |
| Mallard (*Anas platyrhynchos*) | 14 | 48.0% | 33.9% | 41.4% | **+6.6 pp** (2.3–10.7) |
| Northern pintail (*Anas acuta*) | 61 | 61.2% | 33.2% | 49.3% | **+11.9 pp** (10.1–13.6) |

Table entries are equal-birdyear means and percentage-point differences; rounded; no pooled 4-species p-value. The predeclared exploratory two-reference criterion passed for **4/4 species**. This is a shared descriptive pattern across four waterfowl species from **one California sampling programme**, not four unrelated ecosystem-level independent replications.

## Interpretation and nontriviality

Ordinary selection for one preferred habitat inflates same-habitat persistence, so it is important that the effect was smaller, but remained positive, after controlling for each birdyear's overall habitat-category frequencies. These data support **serial habitat-state structure in realized space use beyond an independently sampled, fixed-preference destination-choice model**.

**This is not yet evidence that animals actively buffer a changing external environment.** Real step destinations and local alternatives are spatially structured; consecutive moving locations remain geographically connected, and within-patch habitat continuity can generate positive serial autocorrelation without explicit behavioral compensation. Source files provide no documented origin-state field for the original step-to-step preservation test. We also have not identified changing water depth, true ecological stress, causal movement choice, energetic benefit or avoided relocation. Independent-draw nulls miss spatially autocorrelated habitat availability. Bootstrap intervals conditional on birdyear may be anti-conservative if birds recur across years.

## Relation to Lake Erie King Rail

The main Louisiana finding remains continuous **water-depth trajectory stabilization** relative to event-matched local availability for 10 King Rails. California tests a **different response and temporal estimand**: retention of discrete land-cover categories at successive moving-step destinations against matched available-destination and fitted fixed-preference references. Agreement in direction is conceptual but should not be represented as external numerical replication of SRI or as evidence of one causal mechanism.

## Sensitivities and next discriminating test

Repository result retains the predeclared minimum-60-pair subset and random-available-total >=50 subset; the categorical preference weights converged for every eligible birdyear (max marginal error <0.001). The per-event random availability total >=50 subset was effectively identical to the main analysis, so it should not be presented as an independent robustness replicate.

To test an *active regulation* hypothesis rather than ordinary within-patch serial continuity, the next truly discriminating measurement is a source-verified map of each step's origin and destination location and changing available habitat distribution (or repeated inundation/raster exposure) so continuity can be conditioned on geographic displacement and environmental forcing. The present data do **not** justify choosing a new post-hoc time interval or subgroup in pursuit of a causal result.

## Reproducibility

- Frozen corrected protocol: [`analysis/contracts/california_temporal_state_fidelity_v2.json`](../analysis/contracts/california_temporal_state_fidelity_v2.json)
- Source schema preflight: [`analysis/61_california_used_state_preflight_v2.py`](../analysis/61_california_used_state_preflight_v2.py); [successful CI](https://github.com/zuizui0223/louis/actions/runs/39215755680)
- Ecological analysis: [`analysis/62_california_temporal_state_fidelity_v2.py`](../analysis/62_california_temporal_state_fidelity_v2.py); [successful CI](https://github.com/zuizui0223/louis/actions/runs/39216459095)
- Canonical aggregate estimates (raw coordinates excluded): [`analysis/results/california_temporal_state_fidelity_v2.json`](../analysis/results/california_temporal_state_fidelity_v2.json)
