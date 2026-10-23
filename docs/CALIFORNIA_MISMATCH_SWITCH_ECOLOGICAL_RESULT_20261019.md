# When does a moving bird abandon its previous habitat state?

**Verified:** 2026-10-19. [Successful Actions run](https://github.com/zuizui0223/louis/actions/runs/39233793094) · [machine-readable numerical results](../analysis/results/california_mismatch_switch_falsification_v1.json) · [frozen post-hoc protocol](../analysis/contracts/california_mismatch_switch_falsification_v1.json).

## Ecological question and novelty boundary

The first California four-species result showed that consecutive realized *destination* habitat categories persist more than expected under time-matched movement availability and a time-invariant individual-year categorical preference. The strongest unresolved explanation, however, is simple **habitat-patch inertia**: animals need not be actively regulating an environmental state to repeatedly use the same class.

The new **post-hoc, explicitly falsifiable** question is different:

> **Within the same bird-year, previous habitat class and source-defined season, does becoming less likely to encounter the previously used habitat among available moving-step destinations predict a higher probability of switching to another habitat class?**

This is a time-aligned **opportunity–response association**, not a causal estimate of niche tracking or the reaction to an exogenous hydrological disturbance.

## Data, statistical target, and controls

Source: USGS P9ELSUHN, exact original bytes/MD5. The study uses four species from **one monitoring programme**. The previously locked **329 bird-years and 56,591 55–65-minute consecutive event pairs** were held fixed. Exactly **58 pairs crossing recorded season labels** were excluded before estimating the new statistic, leaving **56,533 within-season pairs**; no alternative cohorts or redefined endpoints were tried.

For each adjacent hour (t−1 to t), the predictor is `mismatch_t = 1 − q_t(previous_category)`, where `q_t` is the source's normalized seven-category vector of generated available movement destinations. The response is `switch_t = 1[category_t ≠ category_{t−1}]`.

Both variables were centered within each bird-year × prior category × source-recorded season group. For a given tagged individual, centered cross-products were pooled across that individual's bird-years to obtain a **within-stratum slope**. One candidate tagged individual contributes one slope to the species-level mean, and **10,000 tag-bootstrap draws** yield 95% intervals. This prevents 100 random movement alternatives or repeated hours from being counted as independent birds. The endpoint's site/route movement constraints, however, are not controlled by those fixed effects.

## Observed result: changing opportunity corresponds to state switching

| Species | Candidate individual IDs | Within-season hourly pairs | Difference in switch probability for +10 pp mismatch | 95% independent-ID interval | Positive individual slopes |
|---|---:|---:|---:|---:|---:|
| Greater white-fronted goose (マガン) | 67 | 14,379 | **+5.07 pp** | 4.08 to 6.03 pp | 63/67 |
| Lesser snow goose (ハクガン) | 112 | 36,472 | **+5.24 pp** | 4.54 to 5.96 pp | 105/112 |
| Mallard (マガモ) | 14 | 761 | **+3.00 pp** | -0.80 to 6.87 pp | 9/14 |
| Northern pintail (オナガガモ) | 61 | 4,921 | **+5.41 pp** | 4.11 to 6.79 pp | 57/61 |

**Three of four species** (GWFG, LSGO, NOPI) have a positive 95% interval for the within-individual switching–mismatch association. Mallard's point estimate is also positive, but its interval overlaps zero. Restricting to bird-years with at least 60 eligible hour-pairs retains positive slope estimates for all four species but leaves only five tagged Mallards. Removing coarse source-season effects retains a positive mean in all four species.

These values are *percentage-point changes in the probability of switching*, **not** odds ratios, and they describe observational covariation conditional on the available moving-step destinations.

## Fixed time-misalignment checks

Four response-preserving negative controls were fixed in the analysis contract before the mismatch effects were read. The seven-dimensional availability vector was circularly shifted within each source bird-year × season by ±one quarter or ±one half of that season's observed event sequence. The observed switch indicators and prior habitat were unchanged.

| Species | True time-aligned slope | +quarter shift | −quarter shift | +half shift | −half shift |
|---|---:|---:|---:|---:|---:|
| Greater white-fronted goose (マガン) | 0.507 | 0.031 | -0.054 | -0.127 | -0.129 |
| Lesser snow goose (ハクガン) | 0.524 | -0.032 | -0.035 | -0.023 | -0.054 |
| Mallard (マガモ) | 0.300 | -0.074 | -0.251 | -0.077 | -0.155 |
| Northern pintail (オナガガモ) | 0.541 | -0.023 | -0.036 | -0.177 | -0.210 |

For all **4/4 species**, the real time alignment produced a higher mean individual slope than every predefined shift. This supports an association specific to the observed time-matched availability more strongly than one with a season-wide categorical preference alone.

However, a circular time shift also destroys real origin-conditioned spatial accessibility. Therefore these comparisons are **descriptive falsification controls**, not an exchangeable permutation reference or a calibrated p-value. They cannot distinguish active tracking from patch residence, availability autocorrelation and route geometry. The negative-control result must never be phrased as independent proof that birds actively regulate habitat exposure.

## Joint interpretation with the King Rail analysis

The independent Lake Erie King Rail archive supports **experienced water depth varying less than contemporaneous nearby habitat availability** in 10 resident birds. The California four-waterfowl source now supports two separable results in 254 candidate tagged individuals: **excess categorical destination-state continuity** and, for three species, **switching probabilities linked to the time-matched scarcity of the previous category**.

A coherent ecological hypothesis is now possible:

> The experienced habitat state may be maintained when its local alternatives remain accessible, while changing movement opportunities make a switch to a different state more likely.

**This is still a hypothesis connecting two different responses and programmes**, not one confirmed cross-study causal mechanism. King Rail measures continuous water depth without event-matched geographic displacement; California measures categorical movement destinations without direct origination habitats or spatial counterfactual controls.

## Conservation and next test

Environmental monitoring should not treat an occupied wetland as a fixed realized niche. Habitat **diversity and accessibility** may determine which microhabitat states a resident or moving bird can continue to use; the fact that an animal remains in a known area does not guarantee unchanged exposure.

No habitat restoration or management-intervention benefit was measured. The decisive next study needs individually identified origin/destination coordinates, repeated habitat rasters/water depth, and access-limited alternative movements; that would allow static-patch, inertial Markov and active state-maintenance mechanisms to be separated under one predeclared design.

**Publication status:** secondary post-hoc ecological evidence in Louisiana PR #2; distinct from the original King Rail submission manuscript, not yet a fourth independent paper, not merged into main, and not a journal submission.


## Stronger post-result check: control source day/night photoperiod

Because both the available habitat around a bird and its movements can change between daylight and darkness, the first source-season-only analysis could be confounded by photoperiod. Before opening these additional effects, a [separate post-result contract](../analysis/contracts/california_photoperiod_mismatch_sensitivity_v1.json) required comparing only hourly transitions remaining within **the same source-recorded season and the same day/night class**. Fixed-effect centering was correspondingly birdyear × previously used habitat category × season × photoperiod, and circularly shifted availability controls were constrained within those same photoperiod groups.

The original source **329 bird-years and 56,591 candidate adjacent-hour pairs** were unchanged. From them, 58 pairs crossed seasons and **9,586 additional pairs crossed day/night boundaries**, leaving **46,947 matched within-season/photoperiod pairs**. No sunrise times were inferred from clock time; the source photoperiod labels were used unchanged.

| Species | Estimable tagged IDs | Within-photoperiod pairs | Switch change for +10 pp prior-state mismatch | 95% independent-ID interval | Exceeds all 4 day/night-preserving shifts? | Interval verdict |
|---|---:|---:|---:|---:|---|---|
| Greater white-fronted goose | 67 | 11,628 | 5.29 pp | [4.05, 6.60] pp | yes | positive CI |
| Lesser snow goose | 112 | 30,971 | 5.01 pp | [4.10, 5.93] pp | yes | positive CI |
| Mallard | 11 | 575 | 0.61 pp | [-4.20, 4.14] pp | no | uncertain |
| Northern pintail | 59 | 3,773 | 5.06 pp | [3.55, 6.47] pp | yes | positive CI |

**Interpretation update:** the mismatch–switch association survives photoperiod control in **three** species (GWFG, LSGO, NOPI); the **Mallard** estimate shrinks near zero and is highly uncertain. The earlier result that 4/4 observed time-aligned slopes exceeded shifted values **does not survive as a 4/4 claim** after day/night preservation: it is **3/4**, and Mallard's shift comparisons can exceed its observed slope. This is an informative biological and sampling boundary, not a reason to retune the original four-species hypothesis.

[Verified Actions run](https://github.com/zuizui0223/louis/actions/runs/39235534204) · [complete response summary](../analysis/results/california_photoperiod_mismatch_sensitivity_v1.json).

The positive three-species association is still observational because available destination vectors originate at animal-specific positions and track underlying spatial structure. This photoperiod check removes **one measured temporal confound**, not geographical inertia or selection on moving steps. Four species from one California telemetry programme remain **one independent data source**.

**Paper-level supported conclusion after stricter checking:** local habitat opportunity is associated with categorical switching within the same source-defined season and photoperiod for two goose species and northern pintail, while evidence for Mallard is insufficient. Across taxa it remains a hypothesis, not a demonstrated universal rule or proof of active niche regulation.
