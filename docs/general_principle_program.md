# General ecological programme: hydrological portfolio buffering

## Publication target

This project is not a re-analysis of the 2012 King Rail occupancy study and is not primarily about monitoring error.

The target is a wetland- and movement-ecology question:

> **Can temporal complementarity among microhabitats allow resident wetland birds to remain in a familiar area while tracking changing hydrological conditions internally?**

## Literature boundary

Several relevant ideas already exist:

- King Rails select fine-scale vegetation and open-water features within home ranges;
- water depth can predict marsh-bird distribution better than broad marsh class;
- resident King Rails can change seasonal home-range use;
- flexible fine-scale habitat use can coexist with broad-scale site fidelity in other birds;
- animal movement can decline in heterogeneous landscapes;
- habitat portfolios/spatial insurance can stabilise populations and ecosystem functions.

Therefore the novelty claim cannot simply be "heterogeneity matters" or "fidelity and flexibility coexist."

The sharper hypothesis is:

> **temporal complementarity among hydrological microhabitats creates an individual-scale habitat portfolio that stabilises broad-scale residency.**

## Core mechanism

A wetland home range contains cells or patches that differ in elevation, water depth, hydroperiod, vegetation structure, open-water edge, and prey/refuge conditions.

If those patches do not become suitable/unsuitable at exactly the same time, environmental change can shift **which internal patch is best** without eliminating all suitable habitat.

regional water-level change -> different microhabitats respond differently -> best patch shifts inside familiar area -> individual changes fine-scale use -> broad home-range residency is retained

## Hydrological portfolio quantities

For individual/home range h and time t, let A_ht be the fraction of the home range currently inside the species' usable hydrological/microhabitat state.

Define suitability retention as a lower-tail statistic:

HPI_h = Q10(A_ht).

A high HPI means that even during poor periods, some substantial fraction of the familiar area remains usable.

A second quantity is microhabitat response asynchrony:

Async_h = 1 - mean correlation among microhabitat suitability time series.

Exact estimators can change after data audit, but the biological meaning is fixed: **a good portfolio retains suitable habitat because its components respond differently through time.**

## Falsifiable predictions

### L1 — internal tracking

Fine-scale locations should shift toward currently suitable water-depth/vegetation states while the broad home-range centroid/territory remains comparatively stable.

### L2 — portfolio buffering

At the same mean habitat quality, individuals/home ranges with higher HPI or hydrological asynchrony should move shorter distances outside the familiar area, show smaller broad-scale home-range displacement, and maintain occupancy/use through larger water-level fluctuations.

### L3 — threshold failure

Broad relocation should rise sharply when A_ht falls below a critical retained-suitability threshold. Movement outside the familiar area is predicted to be a **portfolio failure event**, not a smooth response to every water-level change.

### L4 — niche breadth interaction

Hydrological specialists should gain more from a diverse/asynchronous habitat portfolio than broad-niche species.

### L5 — temporal complementarity beats static heterogeneity

A static diversity index should be weaker than a metric based on **how habitat components retain suitability through time**.

## What would falsify the programme

The hydrological-portfolio interpretation is weakened if:

- mean water depth or mean habitat quality predicts residency as well as temporal complementarity;
- internal microhabitat switching does not increase during water-level change;
- high-heterogeneity home ranges show equal or greater broad relocation;
- no retained-suitability threshold precedes relocation;
- niche breadth does not modify the benefit of habitat portfolios across species.

## Why King Rail matters

King Rail is a strong anchor because existing studies show strong within-home-range microhabitat selection, association with vegetation richness and open-water proximity, home-range size related to open-water availability, ecological consequences during drought, and shallow-water/fine-scale hydrological relationships in Gulf Coast marshes.

The EOG failure of simple geographic propagation provided the clue that **geographic distance from prior use may not be the relevant state variable**.

## Independent empirical route

Priority systems:

1. **King Rail telemetry in southwest Louisiana / southeast Texas** — 34 radio-tagged birds with direct microhabitat measurements; ideal if raw movement/habitat data can be obtained.
2. **Mid-Atlantic King Rail telemetry** — resident segment with seasonal changes in home-range size and habitat use; useful for within-individual flexibility.
3. **Northern Gulf Coast multi-species wetland-bird surveys** — strong water-depth information across multiple species; useful for estimating hydrological niche breadth, not sufficient alone for individual tracking.
4. **Dynamic wetland movement systems outside rails** — shorebird/waterbird telemetry under changing surface-water distributions provides a taxonomically independent test of whether retained local habitat reduces regional movement.

## Main paper-level model

For individual h and time t:

broad_relocation_ht ~ HPI_ht + mean_habitat_quality_ht + water_level_change_t + HPI * water_level_change + species_niche_breadth + HPI * niche_breadth + individual/system random effects

Fine-scale tracking model:

microhabitat_choice ~ current_water_depth + vegetation_state + open_water_edge + familiarity

The key test is whether internal habitat switching **mediates** the relationship between environmental change and broad-scale residency.

## Strong ecological conclusion if supported

> **Spatial heterogeneity stabilises residency when its components are temporally complementary: animals can remain faithful to a familiar area by moving among internal habitat states rather than abandoning the area when conditions change.**

This is the ecological endpoint. King Rail is the motivating anchor, not the evidence base.