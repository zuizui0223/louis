# A new ecological result: dusk-specific habitat-state transitions in California waterfowl

**2026-10-25. Source study: Overton and Casazza 2023, USGS 10.5066/P9ELSUHN. Analysis status: verified post-result exploratory biological study, not an untouched or causal confirmation.**

## Biological question

Do birds simply maintain their generally preferred habitats, or are the categories that they use successively organized around the transition between day and night? The source paper already quantified species differences in movement incidence and habitat-selection functional responses. The new response is a within-bird sequential change in used movement-endpoint habitat category, not a new interpretation of those original selection results.

## Result 1 — a dusk/dawn state-switching signal concentrated in lesser snow geese

All four taxa belong to one USGS public telemetry programme. The exact previously verified cohort held 329 bird-years (254 candidate independent tag IDs) and 56,591 approximately hourly adjacent used-endpoint pairs. Of these, 58 crossed recorded season labels, 9,586 crossed photoperiod, and 46,947 were within a single photoperiod. A time-matched seven-habitat availability vector and a bird-year static-choice reference were used to calculate excess observed switching; within bird-year and source season, the comparison matched arriving photoperiod and previously observed habitat category.

**Table E1. Day/night boundary excess habitat-category replacement, relative to same-photoperiod transitions.** Numbers are percentage points with candidate individual-level bootstrap intervals. The five estimable Mallard candidate IDs are notably sparse.

| Species | Estimable candidate IDs | Excess category switching, pp | 95% cluster interval, pp | Direction |
|---|---:|---:|---|---|
| Greater white-fronted goose | 44 | +0.55 | -3.29 to +4.26 | Uncertain |
| Lesser snow goose | 69 | +8.47 | +5.72 to +11.16 | Positive |
| Mallard | 5 | +3.14 | -11.94 to +18.22 | Uncertain |
| Northern pintail | 28 | +1.53 | -4.35 to +7.41 | Uncertain |

Lesser snow geese retained a positive day/night boundary-specific habitat switching association: +8.47 percentage points (95% CI +5.72 to +11.16; 69 tags, 54 positive individual contrasts). The other three source taxa did not support a comparable directional claim. The source analysis is limited to moving-step endpoints and does not reconstruct full circadian activity or every geographical movement.

## Result 2 — protected-area category followed by rice fields near nightfall

We further examined the biological identity of the new habitat state among consecutive moving-step observations. The category Protected is a source-defined managed-land/refuge class and Rice is a crop land-cover category. These are not direct observations of roosting or feeding.

**Table E2. Previous observed habitat category Protected followed by next observed category Rice: day-to-night versus night-to-day.** Effects compare destination-category enrichment after subtracting the same event's fitted static-choice probability from its source-matched available categories. Confidence intervals use independently marked candidate tags as units. This directional follow-up was selected after seeing initial raw source counts and is explicitly hypothesis-generating.

| Species | Independently estimable IDs | Observed source successions at day→night / night→day | Enrichment difference, pp | 95% candidate-ID interval, pp |
|---|---:|---:|---:|---|
| Greater white-fronted goose | 11 | 27 / 26 | +9.70 | -1.41 to +21.26 |
| Lesser snow goose | 47 | 191 / 53 | +32.36 | +22.13 to +43.33 |
| Mallard | 5 | 4 / 0 | Not estimable | — |
| Northern pintail | 18 | 49 / 10 | +55.54 | +37.53 to +72.77 |

Lesser snow geese showed a +32.36-point day-to-night excess relative to night-to-day (95% CI +22.13 to +43.33, 47 estimable tags), and northern pintails showed +55.54 points (+37.53 to +72.77, 18 estimable tags). Greater white-fronted goose intervals included zero and mallards did not meet the fixed minimum of eight IDs.

The **reverse succession of Rice followed by Protected** did not show a comparably clear day-to-night excess in any adequately replicated species. That means the observed association is directional rather than a symmetric increase in all category exchanges.

## Ecological interpretation

These data are compatible with daily reorganization of habitat use across agricultural rice landscapes and protected lands for lesser snow geese and northern pintails. The snow goose also showed a more general increase in category switching at the day/night boundary, whereas pintails' positive signal was concentrated in a particular destination sequence. The distinction is ecologically informative: different taxa can share rice and protected habitats while organizing their successive use differently.

An attractive natural-history hypothesis is a diel circuit between refuge-like managed land and agricultural resources. It remains unproven: no source event directly verifies feeding, resting, predation avoidance, precise route origin, or individual intention. The model also cannot separate a daily behavioral schedule from spatial accessibility and within-timepoint movement-step selection.

These results add a new biological contrast to the ODSP–batter–Louisiana paper: time can partition habitat use **within a species' observed sequence of habitats**, not only species detections at the same Serengeti site. Unlike the bat individual-altitude and King Rail water-depth examples, the California transition data do not measure an environmental exposure buffering benefit.

## Source links

- [Primary category-switch result](RESULT_DIEL_HABITAT_TRANSITIONS_V1.json) and [verified run](https://github.com/zuizui0223/louis/actions/runs/40160915884)
- [Protected/Rice direction contrast](RESULT_DIEL_RICE_PROTECTED_ROUTES_V1.json) and [verified run](https://github.com/zuizui0223/louis/actions/runs/40161218491)
- [Figure 3: species differences in diel boundary switching](Figure3_species_diel_habitat_switching.svg)
- [Figure 4: direction of successive Protected/Rice habitat use](Figure4_diel_protected_rice_sequences.svg)
- Original study: Overton, C. T. & Casazza, M. L. (2023), DOI 10.3389/fevo.2023.1232704. Original study already identified circadian movement and species-specific habitat preference responses.
