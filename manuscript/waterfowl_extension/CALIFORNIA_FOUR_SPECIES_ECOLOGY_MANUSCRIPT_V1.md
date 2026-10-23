# Temporal continuity of habitat use and opportunity-dependent switching in four wintering waterfowl species

**Comparative ecological manuscript V1 — developmental draft for author review, not submitted**

**Authors:** [to be completed]

**Affiliations:** [to be completed]

## Abstract

Movement can maintain an animal's access to a familiar habitat state or replace that state as local opportunities change. Conventional habitat-selection analysis compares used and available conditions but does not directly quantify the temporal continuity of an individual's realized habitat sequence. We examined these complementary dynamics using a USGS public step-selection archive for four wintering waterfowl species in California's Central Valley. The source records contain observed movement endpoints and habitat availability summarized from 100 source-generated random steps, classified into seven habitat types. After source verification, 329 bird-years from 254 candidate marked-bird identities contributed 56,591 qualifying adjacent-hour pairs. Same-category continuity of the observed endpoints exceeded an independently drawn matched-availability reference and also a reference fitted to each bird-year's own time-invariant marginal habitat preference. Equal-individual excess continuity was 13.95 (95% cluster interval 12.52–15.40) percentage points in greater white-fronted geese, 15.87 (14.88–16.87) in lesser snow geese, 6.55 (2.22–10.66) in mallards and 11.88 (10.17–13.64) in northern pintails. A post-result analysis asked whether lower availability of the previously used category predicted switching. After comparing within bird-year, prior habitat, winter period and daylight class, a 10-percentage-point decline in the prior habitat's locally available destination fraction corresponded to an estimated increase in switching of 5.29, 5.01 and 5.06 percentage points in the two geese and northern pintail, respectively; the mallard result was uncertain (+0.61, interval −4.20 to +4.14). The results show temporal organization of habitat-category use beyond a static preference reference and a context-dependent opportunity–switch association. They do **not** establish active adaptive tracking, because source movements and available destinations share spatial context, and individual movement origins are not identified as habitat states in the released table.

**Keywords:** movement ecology; habitat-state continuity; step selection; Anser; Anas; wintering waterfowl; time-varying availability.

## Introduction

Animals inhabit environments that vary across time, but their experienced conditions depend not only on where resources occur but also on which places they repeatedly use. Habitat-selection studies typically evaluate which states are overrepresented in used locations relative to the states available for selection. This is essential for management yet leaves a separate ecological question: **how persistent is the sequence of states actually occupied, given contemporaneous opportunities?** A bird can repeatedly use the same habitat category because it is consistently available, because it strongly prefers the category, or because the movement process and geography make some transitions easier than others. These mechanisms can generate superficially similar histories of habitat use.

A second question concerns the other side of persistence. When the previously used habitat category becomes less frequent among currently available movement destinations, does the animal become more likely to occupy a different category? A dynamic association between local opportunity and switching would go beyond a description of overall habitat preference. It would not, however, prove deliberate regulation of a preferred niche: availability at the origin may be jointly determined by previous movement, habitat-patch geometry and landscape structure. A meaningful observational test therefore needs time-matched available habitats, individually repeated observations and independent-individual uncertainty rather than pooled point counts.

California wintering waterfowl provide a useful comparison because two goose species and two dabbling ducks co-occur in an agricultural wetland landscape. The original research by Overton and Casazza (2023) modelled latent movement activity, source-specific available steps and functional responses of selection to availability. In that study geese shared aspects of habitat choice, northern pintails showed responses closer to geese for some resources, and mallards were comparatively generalist. Those results establish habitat-selection ecology. The present secondary analysis asks a **different temporal question** using the archived observed–available endpoint table. It is not a new telemetry study or a direct reanalysis of movement decision mechanisms.

We evaluated two observational predictions. First, individual birds should show more hour-to-hour continuity of observed habitat category than expected from independently selected destinations drawn from time-matched available habitats, even after fitting one constant habitat-preference vector per bird-year. Second, a smaller available share of the previously occupied habitat category should be associated with a larger probability of switching, when compared within bird-year, prior habitat, winter period and photoperiod. We report all four species, including a weak or uncertain result where present, and make no claim that any difference is universal or that the study measures water depth or the habitat state at the actual step origin.

## Methods

### Source data and eligibility

We used the public USGS data release by Overton and Casazza, DOI 10.5066/P9ELSUHN, originally analysed in *Frontiers in Ecology and Evolution* (2023, 11:1232704). The downloaded CSV was verified against the source-reported byte size and MD5. The source study retained moving steps from an empirical two-mixture movement process and provided, for a moving step, the category at its observed destination plus available destination counts generated from 100 simulated movements beginning at that step's origin. The release describes four wintering species: greater white-fronted goose (GWFG), lesser snow goose (LSGO), mallard (MALL) and northern pintail (NOPI).

The final source habitat map used seven mutually exclusive categories: corn, field, other, protected, rice, urban and wetland. Protected is a source-defined management/refuge category and need not represent one homogeneous vegetation structure. An initial software preflight incorrectly omitted this category and assumed ISO timestamps. We corrected both source-semantics errors before estimating state-continuity outcomes; the failed preflight results remain retained in the reproducibility history. Neither habitat categories nor the underlying source case/availability semantics were subsequently adjusted according to the signs of the ecological results.

The source table contains 380,578 rows and 190,289 potential observed/random event keys. Under the frozen seven-class rules, 189,851 were source-compatible observed–available matched events; 438 failed an observed-category or availability-count requirement. We considered consecutive observations within the same bird-year whose timestamps differed by 55–65 minutes. An individual bird-year required at least 31 qualified events and 30 adjacent qualifying transitions. This retained 329 bird-years and 56,591 transitions. A source bird-year combines a marked-bird code and agricultural-year suffix. Subsequent identity audit supported 254 distinct candidate marked-bird prefixes; repeated years of the same prefix were resampled as one potential biological individual. An original source-custodian validation of each stripped prefix is still required.

### Temporal category continuity

For each bird-year, observed category continuity was the fraction of successive qualifying endpoint pairs in which the observed seven-class habitat label stayed the same. At each time, the source-matched availability vector was the seven category counts in the corresponding random-step record divided by its actual random-step total. The raw independent-draw null expected the same category in two successive events with probability equal to the inner product of their two availability vectors.

To distinguish persistence from a constant marginal tendency to use one category, a second null multiplied each event's availability vector by time-invariant habitat weights fitted separately within each bird-year. We matched this static-selection model's marginal category frequencies to the bird-year's observed marginal usage with Dirichlet half-count smoothing and iterative proportional fitting. Then we computed the expected same-category fraction for independently drawn adjacent endpoints under those fitted probabilities. **This null is fitted to the same observed trajectory**, so it is a descriptive test of residual temporal organization beyond a static categorical preference, not an external held-out prediction or a fully specified movement-process null.

The individual bird-year contrast was observed continuity minus the static-preference expectation. We kept all eligible birds, and after identifying repeat bird-year prefixes we averaged bird-year contrasts within candidate biological individuals. The reported species mean gives each candidate individual one vote and uses 10,000 candidate-individual bootstrap resamples for intervals. We did not count hourly steps or the source-generated 100 alternatives as independent animals. The analysis was developmental and was conducted after source ecological responses were already public.

### Availability mismatch and habitat switching

After the positive category-continuity result, we separately froze an explicitly *post-hoc* falsification: does a decrease in available destinations of the previously used class correspond to a switch? For each qualifying transition, mismatch was 1 minus the current source-available fraction of the prior observed category. Switching was a binary indicator that the current observed endpoint category differed from the preceding endpoint category. We first centered both variables within bird-year × prior category × source winter season, then strengthened the test by centering within those strata **and source photoperiod**. Steps crossing a season boundary or day–night transition were not joined. The stronger analysis retained 46,947 hourly pairs from the same original 329 bird-years.

Each candidate tagged individual contributed a regression slope from the centered cross-products pooled across its qualifying bird-years, requiring at least 20 informative observations. We reported unweighted means of individual slopes and 10,000 candidate-ID bootstrap intervals. An increase of 0.1 in mismatch corresponds to a 10-percentage-point reduction in the currently available destination share of the previous habitat type; multiplying the estimated slope by 0.1 gives the descriptive probability-point change in switching.

Four predeclared time-misalignment controls circularly shifted the complete seven-category available-destination vector by positive/negative quarter or half of the available observations, separately within each source bird-year, season and photoperiod. They preserved observed switches but disrupted exact opportunity–response timing. These rotations are **descriptive negative controls, not exchangeable permutation distributions**, because shifts also disrupt source-specific geographic accessibility. No causal p-value was derived from them.

## Results

### Individual habitat categories were more temporally continuous than a static preference null

The observed probability of retaining the same habitat category in consecutive hourly endpoints was 66.96% in GWFG, 75.84% in LSGO, 48.00% in MALL and 61.19% in NOPI. The corresponding static-preference expectations were 53.30%, 59.87%, 41.45% and 49.30%. A model in which the bird's mean preference was fixed across time therefore did not account for all the observed state continuity (Figure 1).

Table 1 reports the equally weighted independent-ID residual. All four candidate-ID bootstrap 95% intervals lay above zero, although mallards had only 14 candidate independent IDs. Among originally qualified bird-years the adjusted residual was positive for 99/99 GWFG, 155/155 LSGO, 11/14 MALL and 57/61 NOPI. Requiring at least 60 eligible adjacent pairs per bird-year preserved positive mean residuals, but only five mallard bird-years remained in that stricter sample. Repeated-year clustering did not reverse the species mean signs.

**Table 1.** Recorded continuity and extra same-category probability after fitting each bird-year's static category preference. Percentages are across observations averaged by bird-year; the final effect/interval weights candidate individual IDs equally.

| Species | Candidate IDs | Adjacent-hour pairs | Observed same category (%) | Static-preference expected (%) | Excess probability (pp), independent-ID 95% interval |
|---|---:|---:|---:|---:|---:|
| Greater white-fronted goose | 67 | 14,394 | 66.96 | 53.30 | +13.95 [12.52, 15.40] |
| Lesser snow goose | 112 | 36,511 | 75.84 | 59.87 | +15.87 [14.88, 16.87] |
| Mallard | 14 | 762 | 48.00 | 41.45 | +6.55 [2.22, 10.66] |
| Northern pintail | 61 | 4,924 | 61.19 | 49.30 | +11.88 [10.17, 13.64] |

### Current habitat opportunity was associated with switching in three species

Under the stronger within-season and within-photoperiod comparison, lower availability of the previous category was associated with greater switching in both goose species and northern pintail (Table 2). For a 10-percentage-point increase in mismatch, the estimated changes in switching probability were 5.29 points (95% CI 4.05–6.60) for GWFG, 5.01 (4.10–5.93) for LSGO and 5.06 (3.55–6.47) for NOPI. Mallard had a much weaker and uncertain estimate: 0.61 (−4.20–4.14). After the stricter day/night control only 11 mallard and 59 pintail IDs had informative slopes, compared with 14 and 61 in the preceding season-only analysis.

**Table 2.** Availability mismatch and switching. Change in switch probability per 10-percentage-point reduction in the available share of the previously occupied category, with candidate-ID bootstrap intervals. These slopes are observational associations, not interventions.

| Species | Estimable IDs | Within-season/day-or-night pairs | Switch probability change (pp) | 95% interval (pp) | Direction |
|---|---:|---:|---:|---:|---|
| Greater white-fronted goose | 67 | 11,628 | +5.29 | 4.05 to 6.60 | Positive interval |
| Lesser snow goose | 112 | 30,971 | +5.01 | 4.10 to 5.93 | Positive interval |
| Mallard | 11 | 575 | +0.61 | -4.20 to 4.14 | Crosses zero |
| Northern pintail | 59 | 3,773 | +5.06 | 3.55 to 6.47 | Positive interval |

For GWFG, LSGO and NOPI, the observed time-aligned slope also exceeded each of four predeclared shifts restricted to the same season and photoperiod. Mallard did **not** retain that alignment advantage after photoperiod control; some shift-reference slopes exceeded its time-aligned slope. This difference was reported without revising the source eligibility or outcome thresholds. The time-shift comparison supports a time-specific descriptive association in three species but, because source alternative steps are generated from each actual movement origin, does not isolate adaptive niche tracking from changing accessibility.

## Discussion

Four wintering waterfowl species displayed stronger categorical endpoint-state continuity than expected under independently drawn, time-matched available destinations and a fitted constant marginal habitat-preference model. The result is consistent with stable sequences of realized habitat use, not merely a fixed pooled preference for one habitat type. It is not sufficient to conclude that individuals actively maintain a target environmental state. A bird can persist in one patch, exploit nearby patches of similar cover, or be constrained by route geometry; any of these can create temporal correlations not represented in the static-preference null.

The post-hoc mismatch analysis adds a different ecological pattern: in the two goose species and northern pintail, current movement opportunity for the previously occupied habitat class was associated with whether the next classified habitat differed. The persistence and switching results can be articulated as an observational conditionality: **habitat-state continuity is widespread, while current availability is associated with when that continuity is interrupted**. An independent future study with habitat maps changing over time could ask whether active state regulation adds anything beyond patch fidelity and the feasible movement graph. These data do not yet make that distinction.

The weaker day/night-conditioned mallard result is informative. The source publication described mallards as comparatively generalist in selection and pointed to differences between geese, northern pintail and mallards in the strength of habitat-availability functional responses (Overton & Casazza 2023). That published pattern motivates a candidate interpretation of species differences in temporal switching, but **our four species from one telemetry project do not constitute a replicated moderator test of ecological specialization**, and the mallard analysis has sparse independent replication after matched day/night controls.

The implications for wetland ecology are descriptive but useful: movement opportunity and refuge configuration can influence the environmental categories an animal successively occupies, and a static inventory of preferred cover types does not fully characterize temporal habitat use. Conservation hypotheses could therefore focus on keeping multiple reachable habitats available as agricultural flooding, hunting refuge and wetland conditions change. No management action or restoration treatment was experimentally evaluated here.

### Limitations

Both analyses are secondary and developmental, based on a single public California tracking programme rather than four independent studies. The source's endpoint table does not supply a verifiable per-step origin habitat state or origin–destination coordinates for each comparison, so we do **not** estimate whether a realized geographic displacement maintained the prior habitat. Source alternative destinations are conditioned on real movement origin; their distribution carries location, patch size and movement-constraint information. Static marginal preference fitting does not eliminate within-patch inertia, autocorrelation or time-varying behavior, and circular temporal shifts are not calibrated causal nulls. The source categories blend land cover with a protected/refuge designation; category continuity is not continuous water depth or thermal/nutritional exposure. Repeated-year marked ID prefixes are source-semantic candidates pending independent custodian validation. These limits preclude a cross-taxon, causal law of environmental buffering.

The Louisiana repository's separate Lake Erie King Rail study tests temporal **water-depth smoothing** in a resident population. The California comparison tests **categorical movement-destination continuity and switching** among four species. The studies offer complementary observational evidence on realized versus available environments but are **not statistical replications of an identical response variable**.

## Conclusion

The ecological history of habitat use contains temporal structure not captured by a bird's average preference among habitat types. In four California waterfowl species, repeated classified movement endpoints retained the same habitat category more often than expected from a static-preference availability reference. In three species, category switching was also associated with time-matched scarcity of the previously used type after source season and photoperiod were controlled; a weaker mallard estimate showed that this association need not be uniform. These findings motivate a testable principle that movement through heterogeneous habitats can both maintain and replace realized environmental states depending on opportunity. Testing active regulation rather than passive patch inertia will require movement-origin coordinates, repeated environmental maps and explicitly accessible alternative routes.

## Figures and source provenance

- [Figure 1 — candidate-individual continuity contrasts](../manuscript/waterfowl_extension/Figure1_individual_continuity.svg).
- [Figure 2 — availability mismatch, switching and shifted controls](../manuscript/waterfowl_extension/Figure2_opportunity_switch.svg).
- Source data: Overton & Casazza (2023), USGS Digital Repository, DOI 10.5066/P9ELSUHN.
- Source publication: Overton, C. T. & Casazza, M. L. (2023). Movement behavior, habitat selection, and functional responses to habitat availability among four species of wintering waterfowl in California. *Frontiers in Ecology and Evolution*, 11, 1232704. https://doi.org/10.3389/fevo.2023.1232704
- Core source-linked outputs: [temporal continuity](../analysis/results/california_temporal_state_fidelity_v2.json), [individual-ID robustness](../analysis/results/california_individual_cluster_robustness_v1.json), [opportunity switching](../analysis/results/california_mismatch_switch_falsification_v1.json), [day/night falsification](../analysis/results/california_photoperiod_mismatch_sensitivity_v1.json).
- Detailed study limitations and source corrections: [temporal result note](../docs/CALIFORNIA_TEMPORAL_STATE_CONTINUITY_RESULT_20261019.md), [switching result note](../docs/CALIFORNIA_MISMATCH_SWITCH_ECOLOGICAL_RESULT_20261019.md).

**Publication status:** This is a separate developmental comparative manuscript candidate attached to Louisiana PR #2. The original Lake Erie King Rail manuscript remains independent. Missing human author metadata, source ethical contribution checks, journal formatting and additional independent empirical validation prevent claiming this draft has been submitted.
