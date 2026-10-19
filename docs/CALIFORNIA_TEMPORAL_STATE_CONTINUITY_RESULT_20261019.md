# Four-species temporal habitat-state continuity in California wintering waterfowl

**Evidence date:** 2026-10-19  
**Status:** developmental, source-verified, numerical and synthetic CI PASS; **not causal or independently preregistered confirmation**  
**Authoritative run:** [GitHub Actions 39216459095](https://github.com/zuizui0223/louis/actions/runs/39216459095); [aggregate result](../analysis/results/california_temporal_state_fidelity_v2.json)  
**Source:** Overton & Casazza (2023), USGS DOI 10.5066/P9ELSUHN; 27,997,528-byte CSV, independently verified MD5 `78eb6064eca992225d6907d6e46f5bef`.

## Main ecological question

Do moving wetland birds maintain the **type of habitat they occupy from one observed hour to the next** more than expected from (a) locally available movement destinations at those hours and (b) their own fixed categorical preference for habitat types?

This is a **new, separate endpoint-state continuity estimand**, not a resurrection of the blocked origin-to-destination state-retention test. The original USGS release does not document each movement step's origin habitat. Nothing in this analysis proves that geographical relocation caused environmental buffering.

## Validity and finite data

The pinned original file contains **380,578 rows**, encoding **190,289 matched event keys** and **189,851 qualified observed+random event pairs** under the source-defined seven-class rule. All 438 rejected event keys are retained as metadata in the verification: 328 source rows lack one-hot observed habitat among the seven declared classes and 110 fail the 20–100 availability-count rule. The source pairs have a real observed-case row and one summarized available-movement count row; the latter is **not** an independent tagged animal.

Among all qualified data there are **58,385 adjacent 55–65 minute event pairs**. The frozen minimum of 30 paired successive observations per bird-year retains **329 species × bird-year units and 56,591 eligible transitions**. Species and sample units are:

| Source species code | Taxon | Eligible bird-years | Adjacent pairs |
|---|---|---:|---:|
| GWFG | *Anser albifrons* (greater white-fronted goose) | 99 | 14,394 |
| LSGO | *Anser caerulescens caerulescens* (lesser snow goose) | 155 | 36,511 |
| MALL | *Anas platyrhynchos* (mallard) | 14 | 762 |
| NOPI | *Anas acuta* (northern pintail) | 61 | 4,924 |

The source's seven mutually exclusive categories are Corn, Field, Other, Protected, Rice, Urban and Wetland. A first six-class preflight was **incorrect** because it omitted Protected; this was repaired using original source semantics and preserved as an explicitly developmental correction before inspecting temporal-continuity effects. The dataset also uses month/day/year timestamps. Both previous source-gate failures remain in Actions provenance. The [seven-class verification](https://github.com/zuizui0223/louis/actions/runs/39215732103) passed; no raw individual locations are committed here.

## Main positive observational result

For each bird-year, observed consecutive-event same-category retention is compared to the mean of the source-matched random availability category probabilities. A stricter null reweights the event-level available categories by **one time-invariant, bird-year-specific categorical preference vector**, fitted to that same individual's marginal observed habitat use with Dirichlet 0.5 smoothing and iterative proportional fitting. Both references allow each hour's available habitat categories to change, but their endpoint draws are independent between successive events.

| Species | Observed same-category rate | Expected given raw availability | Expected given fixed preference | Excess beyond fixed preference (95% bird-year bootstrap CI) |
|---|---:|---:|---:|---:|
| GWFG | 66.96% | 42.34% | 53.30% | **+13.66 points** [12.47, 14.86] |
| LSGO | 75.84% | 47.87% | 59.87% | **+15.97 points** [15.08, 16.87] |
| MALL | 48.00% | 33.90% | 41.45% | **+6.55 points** [2.33, 10.67] |
| NOPI | 61.19% | 33.25% | 49.30% | **+11.88 points** [10.14, 13.64] |

The individual preference-adjusted residual is positive for **99/99 GWFG, 155/155 LSGO, 11/14 MALL and 57/61 NOPI** bird-years. The frozen **developmental** gate — positive raw and preference-adjusted mean, with preference-adjusted 95% interval above zero for at least two of four species — is passed by **4/4 species**. Each species was reported without selection on outcome sign.

The two frozen sensitivities remain directionally positive: restricting available-count totals to at least 50 changes no qualifying bird-years or mean effects in this source, and requiring 60 rather than 30 adjacent pairs gives preference-residual means **+13.94, +15.82, +7.27 and +10.73 percentage points**, respectively. The stricter 60-pair sample includes only five mallard bird-years; it is descriptive and not a replacement primary.

## Ecological meaning — and strict limits

**Supported:** the observed trajectory of habitat *categories* is temporally more persistent than the expectation under independently chosen matched-availability states, and remains so after fitting a fixed, individual-year categorical preference. This identifies **excess temporal organization in realized habitat use**, across four named waterfowl species in one source study.

**Not established:** actual tracking of a moving microclimate or water depth, adaptive habitat-state regulation, a causal movement mechanism, functional resilience, a life-history tradeoff, or a universal law across animal taxa. Animals may revisit a stable patch or retain a home-range core; spatial and temporal autocorrelation, path constraints, and unmeasured repeated habitat opportunities are not removed by a time-invariant categorical-preference null. The original release lacks independent origin coordinates/step lineage in the FGDC columns, so active movement-mediated state maintenance cannot be identified. Further, bird-years are the reporting/bootstrapping unit; repeated tracking of the same biological bird across years cannot be ruled out solely from the available `birdyear` definition. Species do not constitute four independent datasets; all share the same California telemetry programme.

**Relation to the Lake Erie King Rail evidence:** both demonstrate that an animal's realized environmental-state sequence carries information beyond time-matched habitat availability. Lake Erie measures **continuous within-home-range water depth** from 10 individually tagged resident rails; California compares **categorical endpoint habitat continuity** from 329 bird-years of four other waterfowl species. They are **complementary observational estimands, not identical statistical replications**. The retained higher-level question is when animals maintain a preferred state versus switch habitats as local availability changes.

## Next decisive mechanistic boundary

To distinguish *active environmental-state tracking* from **location/home-range or habitat-patch inertia**, future data must pair each movement origin/destination with source-defined spatial coordinates, habitat at origin, actual available transitions under physical movement constraints, and repeated temporal environmental fields. Under those data, compare observed destination-state persistence to both static-place and dynamically constrained movement null models without changing this completed California result.

**Reporting status:** manuscript interpretation and species contrasts remain developmental. No causal or cross-phylum generality claim and no submission approval are warranted by the current computational PASS.
