# Independent-data feasibility audit

## Current decision

The project has at least one genuinely independent, open King Rail movement dataset.

### GO — western Lake Erie King Rail telemetry + microhabitat

**Paper**
- Brewer et al. 2023, *Ecology and Evolution*
- DOI: 10.1002/ece3.10043

**Open data/code**
- Zenodo: 10.5281/zenodo.6604660
- the paper explicitly states that study data and code are deposited there.

Study design:
- 14 radio-tagged King Rails, 2019–2021;
- 10 individuals with stabilised home ranges;
- repeated telemetry locations;
- microhabitat measurements including water depth, vegetation and proximity/landscape features;
- published preferred water-depth range roughly 6–17 cm.

This is currently the strongest executable independent seed for **hydrological state tracking**.

## Critical gate: can it test a portfolio, not just habitat selection?

The hydrological-portfolio hypothesis requires more than used-versus-random habitat measurements.

The downloaded files must contain enough information to reconstruct at least:

```text
individual × date/time × location × local water-depth/microhabitat state
```

Preferably they also contain temporally matched conditions at alternative points or an external water-level series that can be projected across the home range.

### Gate L1 — temporal resolution

PASS if used locations have dates/times and repeatedly sampled water depth or another time-varying hydrological state.

STOP/DEMOTE if microhabitat is effectively static or lacks temporal indexing. In that case the dataset can establish **hydrological niche and internal habitat switching**, but not temporal portfolio buffering.

### Gate L2 — familiar-area geometry

PASS if individual locations are sufficient to define a stable familiar area/home range and quantify whether later locations stay within versus leave it.

### Gate L3 — dynamic habitat surface

For the full HPI/portfolio test, at least one of these is needed:

1. repeated spatial water-depth measurements;
2. managed impoundment water-level records plus elevation/topography;
3. remotely sensed/inundation products at appropriate temporal/spatial resolution.

Without one of these, do not pretend that static habitat diversity equals temporal complementarity.

## Strong open backup — 2025 King Rail movement supplement

Whetten et al. 2025, *Ecology and Evolution*, DOI 10.1002/ece3.72060, uses King Rail telemetry as a movement-data example. The article states that the King Rail data are included in the submission/supplementary material. The example has 37 locations from one bird recorded approximately daily in the 2021 breeding season.

This is too small to carry the ecological paper, but useful for:
- validating movement preprocessing;
- testing code against a fully open small trajectory;
- reproducing familiar-area displacement metrics.

## Independent biological contrasts

### Mid-Atlantic King Rail telemetry

Kolts & McRae 2017 tracked 21 King Rails and 576 locations and showed that part of the population was resident while home-range size/habitat use changed seasonally. The published result strongly supports the biological plausibility of **broad fidelity + internal flexibility**.

Current status: publication open; raw movement data not located in this audit.

### California Central Valley shorebirds

Barbaree et al. 2018 tracked 156 Dunlin and 109 Long-billed Dowitchers. A variable regional water distribution was associated with lower residency and higher functional connectivity than a stable, contiguous wetland region.

This is a useful taxonomically independent contrast for the idea that **water availability configuration controls whether birds can remain resident**, although it operates at a broader spatial scale than the proposed within-home-range portfolio mechanism.

## Immediate implementation target

1. ingest/audit Zenodo 6604660;
2. test Gate L1–L3 before fitting anything;
3. if temporal hydrology is sufficient, build the hydrological-portfolio analysis;
4. if not, keep Lake Erie as the microhabitat/state-tracking anchor and find a dynamic wetland dataset with repeated habitat surfaces before testing HPI.

Use `analysis/02_fetch_public_comparative_data.py` to audit/download the Zenodo record.


## Published-design audit completed

The paper provides enough structural information to predeclare the first analysis before opening the archived files:

- 10 birds contributed stabilized home ranges;
- individuals contributed 14–36 homing points;
- 206 homing microhabitat surveys were analysed;
- 401 random microhabitat surveys were analysed;
- each intended event design was one used plot plus two random-direction plots 75 m away;
- all three microhabitat surveys were conducted within 72 h of the homing location;
- water depth and vegetation/structure variables were measured at every plot.

This is sufficient to justify the **matched-event environmental-state fidelity** design.

### Remaining file-level gate

The archived data still need to expose or allow reconstruction of:

- bird identity;
- homing-event/date identity;
- used versus random plot identity;
- water depth;
- preferably coordinates.

If date/event pairing was discarded in the public table, SRI cannot be computed honestly from that table and the Lake Erie dataset is demoted to a biological anchor rather than the primary quantitative test.

