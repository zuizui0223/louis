# Twilight reorganization of winter habitat use differs among snow geese, white-fronted geese, mallards and pintails in California

**Original comparative ecology research draft, 25 October 2026 · data reanalysis, not submitted**

**Authors:** [To be verified and agreed with actual contributors]

**Affiliations:** [To be verified]

## Abstract

The ecological significance of a resource depends not only on its selection or abundance, but also on its position in an animal's daily sequence of habitat use. California's Central Valley is a winter landscape in which migratory geese and dabbling ducks move among agricultural fields, wetlands and protected land, yet the timing and direction of successive habitat use are not captured by conventional used-versus-available comparisons. We analysed a public movement-step dataset for greater white-fronted geese, lesser snow geese, mallards and northern pintails, retaining 329 bird-years from 254 candidate tagged individuals and 56,591 successive approximately hourly observation pairs. Habitat-category switching across source-defined day/night boundaries was compared with switching within the same photoperiod, while accounting for season, arrival photoperiod, previous habitat category, time-matched available destinations and an individually fitted constant habitat preference. Across 9,586 day/night boundary pairs, **lesser snow geese exhibited an additional 8.47 percentage points of category switching** (95% candidate-individual interval 5.72–11.16), whereas the other three species' intervals spanned zero. A second, explicitly exploratory directional analysis found that, following a recorded Protected-category endpoint, the next endpoint was more strongly enriched in rice habitat at the day-to-night than night-to-day boundary among lesser snow geese (+32.36 points, 22.13–43.33) and northern pintails (+55.54, 37.53–72.77), relative to source-matched destination availability under a fixed individual preference. The reciprocal Rice-then-Protected category succession did not show a comparable uniform dusk enhancement. Thus, species using overlapping winter agricultural wetland mosaics can differ in the temporal organization of their habitat-state sequences, even when some static selection responses are similar. These are observational category sequences among moving-step endpoints, not direct evidence of roost-to-foraging flights or causal effects of twilight. The findings identify diel habitat organization as an ecologically relevant dimension of shared landscapes.

**Keywords:** wintering waterfowl; temporal niche; diel habitat use; lesser snow goose; northern pintail; agricultural wetlands; refuge landscape; habitat switching.

## Introduction

Wintering waterfowl depend on landscape mosaics whose ecological functions can differ substantially among times of day. Managed protected lands, rice fields, seasonally flooded cropland and wetlands can supply different combinations of cover, food and disturbance conditions. An individual may repeatedly select a habitat class yet follow a strongly ordered daily use sequence. The temporal order of states is therefore potentially as relevant to resource ecology as their average use.

The original step-selection study by Overton and Casazza (2023) established that four Central Valley waterfowl species differ in movement activity, relative habitat selection and functional responses to habitat availability. Greater white-fronted and lesser snow geese had broadly similar resource selection, whereas mallards showed a relatively generalist response; northern pintails resembled geese for some important resources. The same work described circadian differences in movement activity. Those published findings are the starting ecological context, **not new results of the present paper**.

Two distinct aspects of the ecological time dimension remained to be compared. First, does the transition between source-classified day and night coincide with a greater tendency to **replace the kind of habitat recorded at successive observations**, rather than merely an increase in movement incidence? Second, when a bird previously used a managed Protected category, is Rice disproportionately represented as the next observed habitat around one diel boundary rather than the other? Both questions concern within-individual state histories, not the conventional selection ratio of one habitat over the others.

These questions could reveal daily ecological circuits among land-cover categories, with species-specific organization of habitat use despite horizontal overlap. However, ordered state use can also arise from changing habitat accessibility, route geometry, the selective recording of moving steps, or preferences tied to time of day. We therefore formulate observational comparisons with source-matched available habitat and an individual-specific static-choice reference; we do not assume they eliminate all environmental and behavioural confounding.

We tested the first prediction across four co-occurring species using a predefined post-result source cohort and grouping scheme. The second, category-direction hypothesis was specified after seeing the initial descriptive counts and is reported explicitly as hypothesis-generating rather than an independent confirmatory test. We include adverse results and limited bird samples rather than replace the ecological target with a more favourable alternative.

## Materials and methods

### Public telemetry and ecological habitat classification

We reanalysed the open public USGS dataset linked to Overton and Casazza (2023), DOI 10.5066/P9ELSUHN. Its complete 380,578-row source CSV was validated against the source byte count and MD5. Each event combines one observed used movement destination with source-generated alternative destination counts representing seven mutually exclusive classifications: Corn, Field (including pasture/alfalfa/idle croplands in the source interpretation), Other, Protected, Rice, Urban and Wetland.

The sample refers to source classified *moving steps* and their observed destinations, not continuous occupancy throughout the day. We preserved the original distinction between used destinations and matched available destinations. We did not infer habitat at the true geographical origin of an individual step. Source bird-years are original marked-bird tracking periods, and the candidate marked ID prefix was used to cluster repeat-year observations. A source-curator validation of every inferred prefix remains a caveat.

### Successive habitat state and source-defined day/night boundary

As in the previously verified California continuity analysis, each bird-year required at least 31 qualified events and 30 pairs of consecutive observations with timestamps separated by 55–65 minutes. We retained 329 bird-years, 254 candidate biological marked IDs and 56,591 adjacent-hour pairs. Among those pairs, 58 crossed source-recorded winter season groups and were excluded from the diel comparison. Exactly 9,586 remaining pairs crossed the source's recorded photoperiod classification; 46,947 joined two observations with the same photoperiod. These source labels, rather than inferred sunrise times or a new astronomical model, define the comparison.

The response was categorical **replacement**: whether the next observed moving-step endpoint belonged to a different original habitat class. The source-generated seven-category available-destination count vector was normalized separately for each timestamp. We fitted a time-invariant within-birdyear categorical habitat choice distribution to its own observed marginal use under a Dirichlet half-count regularization and iterative proportional fitting. This reference retains the time-specific available habitat composition but cannot reproduce the full autocorrelation of patches and actual movement routes.

At each pair we subtracted the static-reference probability of switching away from the previous recorded class from the binary observed change. We compared that residual between crossing-boundary and same-photoperiod pairs **within source bird-year × source season × arriving photoperiod × prior recorded habitat category**. Each stratum required at least two pairs of both types; each candidate individual required at least four informative strata with at least four boundary events. The per-individual mean contrast was the unit of species inference. Ten thousand candidate tagged-ID bootstrap samples provided 95% intervals, retaining the same biological individual across source tracking years. This analysis was developed after earlier, broader four-species continuity and mismatch outcomes had already been examined, and is described as exploratory.

### Directional sequence of Protected and Rice categories

We made a separate, later explicitly post-result ecological comparison after inspecting the unadjusted sequences. For each hourly crossing-boundary pair with preceding observed endpoint class Protected, the response was whether the next observed endpoint was Rice. We subtracted the bird-year's corresponding fixed-choice probability for Rice given current available destinations, and compared day-to-night with night-to-day observations within source bird-year and winter season. Source candidate tagged IDs were the bootstrap units, and a paired bird-year/season stratum required at least two observations in both diel directions. At least eight independent IDs per species were needed for an estimable interval. The reverse Rice-followed-by-Protected sequence was analysed in parallel.

The classification Protected records management status and need not identify a specific roost or refuge function at a given moment. Rice is a land-cover category and does not document direct consumption of rice. These comparisons do not reconstruct the unobserved step origins or continuous paths between recorded endpoints.

### Limits of causal inference

The source is one observational programme rather than four independent populations sampled under a common experimental design. A change across recorded day/night categories may be associated with changed movement behaviour, local route access, or which observations qualify as moving steps. Fitted categorical preference removes time-invariant marginal selection under the source-matched choice set but not unmeasured behavioural state or fine-scale access. Results are expressed as observation-level ecological associations with individual cluster uncertainty, not treatment effects of light, protected status or refuge availability.

## Results

### Twilight-specific category replacement was detectable chiefly in lesser snow geese

The day/night boundary was associated with a distinct increase in the probability of using a different recorded habitat class in lesser snow geese. After the matching and static-reference adjustments, their within-bird boundary excess was **+8.47 percentage points** (95% candidate-tag CI +5.72 to +11.16), with 54 of 69 independently estimable candidate birds exhibiting a positive contrast (Figure 1).

Other species had no similarly clear positive interval. Greater white-fronted geese had an effect of +0.55 points (−3.29 to +4.26; 44 IDs), northern pintails +1.53 (−4.35 to +7.41; 28 IDs), and mallards +3.14 (−11.94 to +18.22; five IDs). The uncertainty for mallards was especially high. Broad similarity in goose habitat selection in the original study therefore did not imply identical diel boundary replacement patterns in this subset of the tracking records.

**Table 1. Category-switch probability excess across the source day/night boundary (percentage points).** The comparator is an approximately hourly same-photoperiod pair with the same bird-year, winter period, arriving day/night label and previous habitat class. Effects and 95% intervals are candidate-individual means and cluster bootstrap percentiles.

| Species | Estimable tagged IDs | Excess day/night replacement (pp) | 95% interval (pp) | Evidence |
|---|---:|---:|---|---|
| Greater white-fronted goose | 44 | +0.55 | -3.29 to +4.26 | Not conclusive |
| Lesser snow goose | 69 | +8.47 | +5.72 to +11.16 | Positive |
| Mallard | 5 | +3.14 | -11.94 to +18.22 | Not conclusive |
| Northern pintail | 28 | +1.53 | -4.35 to +7.41 | Not conclusive |

### Protected-to-Rice state succession was strongly asymmetric in two species

The habitat category used next displayed a still more specific diel organization. In lesser snow geese, an observed Protected-category destination was followed by a Rice-category destination **191 times across day-to-night transitions**, compared with **53 times across night-to-day transitions**. The availability- and static-preference-adjusted day-to-night minus night-to-day contrast was **+32.36 percentage points** (95% candidate-ID interval +22.13 to +43.33; 47 independent candidates).

Northern pintails showed a comparably directional association: **49 versus 10 Protected-then-Rice successions** and an adjusted +55.54-point dusk advantage (95% interval +37.53 to +72.77; 18 candidate birds). The greater white-fronted goose association was uncertain (+9.70 points, −1.41 to +21.26; 11 IDs), while mallards did not meet the minimum of eight estimable individual tags (Figure 2).

**Table 2. Source Protected-category observation followed by Rice: day-to-night versus night-to-day.** Counts are observed successive-category events; the adjusted contrast is the candidate-ID averaged difference after a fitted static choice baseline. This targeted comparison was selected after observing earlier directional counts and is not an independent confirmation.

| Species | Estimable tagged IDs | Day→night observed events | Night→day observed events | Adjusted diel contrast (pp) | 95% interval (pp) |
|---|---:|---:|---:|---:|---|
| Greater white-fronted goose | 11 | 27 | 26 | +9.70 | -1.41 to +21.26 |
| Lesser snow goose | 47 | 191 | 53 | +32.36 | +22.13 to +43.33 |
| Mallard | 5 | 4 | 0 | Not estimable | — |
| Northern pintail | 18 | 49 | 10 | +55.54 | +37.53 to +72.77 |

The reciprocal Rice-then-Protected category sequence did **not** exhibit the same consistent positive day-to-night contrast. Lesser snow geese had an adjusted +1.16 points (−0.75 to +3.33), northern pintails −1.57 (−7.70 to +3.66) and greater white-fronted geese +3.00 (−1.47 to +9.07). Mallard reciprocal estimates were not independently estimable. The habitat sequence appears therefore to be **direction-specific**, not a general increase in all Protected–Rice exchanges.

### Different ecological patterns coexisted in the same agricultural wetland landscape

The snow goose result combines a general increase in category replacement at the diel boundary with the more particular frequent succession of Protected then Rice around nightfall. In northern pintails, only the latter category-specific direction was supported, whereas the overall boundary increase was uncertain. Greater white-fronted geese and mallards were not clearly supported on these boundary metrics.

This distinction is biologically meaningful: individuals belonging to species that use agricultural and protected lands can differ not only in their relative habitat-use frequencies but also in the *ordered succession of habitat classes they use across a daily time boundary*. This does not require that every bird performs one identical circuit and cannot establish whether the same observed pattern would recur in independent winters or landscapes.

## Discussion

### Temporal organization is an ecological axis distinct from average habitat preference

The original California study showed differences among wintering waterfowl in habitat selection and day/night movement incidence. Our new analysis highlights a further ecological dimension: the probability and destination of successive habitat-category use at the day/night boundary, evaluated within repeatedly observed tagged birds. In lesser snow geese, twilight carried information about whether a new category appeared beyond a fixed marginal preference and available choice reference. That structure was not uniformly supported in its close goose counterpart or the two duck species.

The observation has implications for niche comparison. Species may look similar when their relative selection for Rice and Protected land is averaged across the winter while differing in how those habitats are successively visited. This is not a demonstration of competition or niche separation forced by other species. Instead it proposes that **the timing and direction of habitat-state transitions can distinguish ecological strategies that static resource rankings do not fully capture**.

### A candidate refuge–agricultural daily circuit

The enriched Protected-followed-by-Rice category succession at nightfall is compatible with a biological interpretation in which birds connect managed refuge-like land and agricultural feeding opportunities on a daily schedule. The pattern was clearest in lesser snow geese and northern pintails, and was not mirrored by the reverse transition at dusk.

That interpretation has clear limits. The source does not include simultaneous feeding observations, roosting behaviour, refuge use under active disturbance, or the precise origin habitat of the next movement step. Moreover, the environmental alternatives were generated from the moving animal's location, so the reference cannot fully model available routes across a changing landscape. Differences between dusk and dawn could reflect the ecological rhythms of movement and local habitat accessibility without demonstrating intentional use of a refuge–feeding circuit. Future direct observation, camera-linked GPS and water-management records would be needed to verify the candidate behavioural pathway.

The distinction between lesser snow geese and greater white-fronted geese is especially relevant: related species may overlap in major winter resources and yet show different timing of category turnover in the tracking subset. The northern pintail result provides an additional taxonomic contrast, but the small number of individually estimable dusk-to-dawn pairs limits claims of broad duck–goose convergence.

### Implications for time-sensitive wetland conservation

Wetland habitat management is typically measured in terms of hectares of flooded rice, protected land and other habitat classes available through the winter. Our results suggest a further question for management research: **are the required habitat types available and usable at the times birds transition between different daily ecological activities?**

For lesser snow geese and northern pintails, the nightfall-associated sequence involving protected land and rice may motivate field studies of connectivity, access and disturbance at that particular daily window. The analysis does not measure how many hectares, what timing of flooding or which refuge configuration would improve survival or condition. No management action was experimentally tested. The data instead identify an ecological process and candidate taxa for a deliberately designed follow-up.

### Relationship to multidimensional habitat use across vertebrates

The interpretation is consistent with a broader ecological idea developed by ODSP, batter and Louisiana: mapped habitat overlap can conceal differences in when animals use a place, how individuals partition vertical state distributions, and what environmental states they actually experience. Snapshot Serengeti's species-specific camera detection times represent between-species site-time organization; bat telemetry reveals individually repeatable vertical-use profiles in five comparative panels; and the King Rail case reveals more stable experienced water depth than local sampled availability. The present waterfowl analysis contributes a distinct **within-individual directed ecological state sequence** tied to a daily boundary.

These case studies do not estimate a common effect and should not be combined as if they prove one shared adaptive mechanism. They motivate a testable ecological programme in which resource functions, activity state, local accessibility and actual environmental exposure are measured within the same marked individuals.

### Limitations and further validation

All findings use a single previously published California programme. Their inference concerns moving-step destination sequences under source-specific classification, with some candidate bird IDs repeated across years. Seasonal context and arrival photoperiod are represented, but habitat spatial autocorrelation, exact local step origin, route restrictions, weather and behavioural-state composition are not fully controlled. The source records source-labelled day/night status, not independently verified astronomical sunrise or sunset at every step.

The category-specific direction test was designed after preliminary counts were seen; its positive estimates are exploratory. The fixed observation/availability comparison helps distinguish temporal organization from a constant preference, but it is not a counterfactual causal manipulation. Species-dependent confidence intervals, limited mallard sample size and potential cross-year tag identity ambiguity further restrict generality.

An independent replication should combine detailed step origins and destinations, source-linked resource behaviour, time-resolved agricultural flood/refuge management, and accessibility-aware alternative movements. Only then could the biological roles of the recorded category sequences and consequences for individual fitness be evaluated.

## Conclusion

Winter habitat selection is not fully described by the average habitats animals use. In a single Central Valley monitoring programme, lesser snow geese exhibited additional habitat-category replacement across day/night boundaries, while lesser snow geese and northern pintails showed enriched succession from a Protected-category observation to a Rice-category observation near nightfall. Greater white-fronted geese did not show comparably clear category-specific associations, and mallard samples were insufficient for firm conclusions. This difference suggests that the **daily ordering of environmental-state use is a distinct ecological dimension of shared agricultural wetlands**. It is a hypothesis about habitat-use organization, not yet proof of a refuge-to-foraging movement mechanism or a management effect.

## Figures

**Figure 1.** [Species-specific boundary-associated habitat replacement](Figure3_species_diel_habitat_switching.svg). Differences relative to same-photoperiod moving-step pairs, with bird-identity bootstrap intervals.

**Figure 2.** [Directional Protected/Rice habitat-state succession at source day/night transitions](Figure4_diel_protected_rice_sequences.svg). Reciprocal sequence and sparse data are shown to avoid inferring a symmetric daily commute.

## Data availability and source provenance

Original used/available habitat data: Overton & Casazza, USGS DOI 10.5066/P9ELSUHN. This manuscript's new aggregate biological results, [source protocol for day/night replacement](CONTRACT_DIEL_HABITAT_TRANSITIONS_V1.json), [its machine-readable results](RESULT_DIEL_HABITAT_TRANSITIONS_V1.json), [post-result directed route protocol](CONTRACT_DIEL_RICE_PROTECTED_ROUTES_V1.json) and [all directional results](RESULT_DIEL_RICE_PROTECTED_ROUTES_V1.json) are retained alongside the reproducible code in the public GitHub research branch. Exact original source bytes and biological sample counts were reverified; no original animal records are reproduced in this manuscript. Original study animal tagging/ethics are acknowledged from their publication, not independently certified by this new manuscript.

**Author contributions, permission to reuse the source data, source-study ethics citations, figure review, novelty relative to Overton/Casazza and target journal format all require final human verification.** This is a draft and was not submitted.

## References

Overton, C. T. & Casazza, M. L. (2023). Movement behavior, habitat selection, and functional responses to habitat availability among four species of wintering waterfowl in California. *Frontiers in Ecology and Evolution* 11:1232704. https://doi.org/10.3389/fevo.2023.1232704

Bolnick, D. I. et al. (2003). The ecology of individuals: incidence and implications of individual specialization. *The American Naturalist* 161:1–28. https://doi.org/10.1086/343878

Nathan, R. et al. (2008). A movement ecology paradigm for unifying organismal movement research. *Proceedings of the National Academy of Sciences USA* 105:19052–19059. https://doi.org/10.1073/pnas.0800375105

**Bibliography to be completed and verified under target journal author requirements.**
