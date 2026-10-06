# California waterfowl step-state external test preflight

## Role

This is an **optional independent generality/falsification route** for the Louisiana King Rail programme.

It does not replicate Lake Erie water-depth SRI.

Public source:

- Overton & Casazza (2023) USGS data release;
- DOI: 10.5066/P9ELSUHN;
- four wintering waterfowl species in California's Central Valley;
- 2016–2022 GPS tracks;
- moving steps retained after a two-mixture movement classification;
- **100 random available steps generated from the origin of each observed moving step**.

The source publication analysed habitat selection and functional responses. The present proposed reanalysis asks a different question:

> **when an animal moves, does its realised destination preserve the habitat state it occupied at the step origin more often than movement-matched available destinations would, or does movement replace habitat state?**

This is deliberately a categorical habitat-state boundary test, not a hydrological SRI replication.

## Why this system is useful

The design already contains a strong local movement counterfactual:

    one observed moving step
      vs
    100 random steps from the same origin

This is conceptually closer to the Lake Erie matched-availability logic than a seasonal range comparison.

It also contains four species with different habitat-selection strategies, allowing the state-retention hypothesis to fail biologically rather than requiring every species to behave like King Rail.

## Response-independent schema gate

Do **not** run the ecological test unless the released files contain or allow an unambiguous source-defined reconstruction of all of the following:

1. individual identity;
2. observed-step identity / stratum;
3. observed versus random endpoint flag;
4. origin location or origin habitat class;
5. endpoint habitat class for observed and random steps;
6. species;
7. time or source-defined seasonal period.

If origin habitat would have to be guessed from row order, silently inferred across missing fixes, or reconstructed from an undocumented join, stop.

Status in that case:

> **STOP_ORIGIN_STATE_NOT_IDENTIFIABLE**

## Primary estimand

For observed moving step s of individual i:

    R_is
      = I(observed destination habitat == origin habitat)
        - mean_j I(random destination habitat_j == origin habitat)

where j indexes the source-generated random available steps for the same observed step.

Interpretation:

- R > 0: realised movement preserves categorical habitat state more than movement-matched availability;
- R ≈ 0: no state-retention advantage;
- R < 0: realised movement changes habitat category more than the movement-matched availability expectation.

The biological replication unit is the **individual**, not the step or the 100 random endpoints.

## Individual-level primary summary

For each individual with a prespecified minimum of 20 eligible moving steps:

    mean_R_i = mean_s(R_is)

Population summaries are species-specific.

Primary directional evidence for a species is:

- median individual mean_R;
- fraction of individuals with mean_R > 0;
- individual-cluster bootstrap interval for the species median/mean.

No pooled four-species p value is required.

## Secondary decomposition

Only after the primary exact-category result is computed, describe which transitions dominate:

    origin habitat -> realised destination habitat

and compare them with the movement-matched random transition matrix.

Do not create a post-hoc "similar habitat" grouping to rescue a null exact-category result.

## Strong falsification value

Three broad outcomes are all informative.

### Positive state retention

Supports the idea that movement can preserve an experienced habitat state even while geographic position changes.

### Near-zero state retention

Suggests that King Rail hydrological buffering is not a generic property of wetland-bird movement.

### Negative state retention

Supports an explicit **resource-state replacement** regime: animals use movement to switch ecological states rather than stabilize the state occupied at the movement origin.

That result would complement, not contradict, the published Senegal Godwit seasonal habitat-replacement boundary.

## Boundary relative to Lake Erie

Do not equate categorical California land-cover state with Lake Erie water depth.

Lake Erie primary evidence remains stronger for **temporal environmental buffering** because it uses a continuous hydrological state measured at used and local random points at the same event.

The California system tests whether the broader logic of movement-mediated state continuity survives in a different response dimension and at an hourly movement scale.

## Scientific payoff

If species differ, the stronger general question becomes:

> **what determines whether movement buffers an environmental state or deliberately replaces it?**

Candidate moderators can then be defined from biology **before** inspecting species-specific state-retention outcomes, such as:

- resident versus migratory strategy;
- diet/resource specialization;
- sanctuary dependence;
- seasonal period.

No moderator should be selected because it happens to separate positive from negative outcomes.

## Current status

**PREFLIGHT_ONLY — DATA SCHEMA NOT YET OPENED**

The source is public/CC0 and the design is promising, but no ecological result is claimed until the release schema passes the gate.


## Source-level verification — 2026-10-06

The public USGS release and its supporting 2023 paper were rechecked before any ecological result was computed.

Verified from the public source description:

- four wintering waterfowl species;
- GPS locations at hourly or hourly-subset resolution;
- a two-mixture movement model separating inactive from moving steps;
- only the larger moving component retained for step-selection analysis;
- **100 random available movements generated from the origin of every observed moving step**;
- habitat endpoints classified into seven aggregated habitat categories;
- analyses stratified by individual, day/night and early/late winter in the source study.

This confirms that the release is conceptually suitable for a movement-matched state-continuity test.

What is **not yet verified** from the downloadable raw-file schema is whether the released rows carry an explicit origin habitat class, or the coordinates/step key needed to recover it without undocumented row-order assumptions.

Therefore the current executable status remains:

> **PREFLIGHT_ONLY — SOURCE DESIGN VERIFIED; RAW ORIGIN-STATE SCHEMA NOT YET OPENED**

Do not infer a California state-retention result from the published used-versus-available habitat proportions alone. The proposed endpoint requires origin -> destination state continuity for each observed step and its own 100 random alternatives.
