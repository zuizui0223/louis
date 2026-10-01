# louis

## Main ecological question

> **Do resident wetland birds perform micro-niche tracking inside a familiar home range—moving through space so that the environment they actually experience varies less than the environment available around them?**

This project uses King Rail as the anchor for a fine-scale niche-tracking question.

The goal is not to repeat occupancy modelling or ask again which water depths are selected. It is also not enough to show that animals can move to similar environmental conditions: that broader phenomenon is already established in the niche-tracking literature and has a close wetland precedent in Shoebills.

The new temporal test is:

> **within a resident home range, is the used environmental trajectory more stable than time-matched local availability?**

The independent Lake Erie design is especially useful because the published study has:

- 10 birds with stabilized home ranges;
- 206 used/homing microhabitat surveys;
- 401 nearby random surveys;
- intended event matching of one used point and two random-direction points 75 m away, surveyed within 72 h;
- repeated water-depth and vegetation measurements.

The first metric is the State Retention Index (SRI), calculated separately for each bird.

If coordinates are available, the stronger test is:

> **move in space to stay in state** — geographic movement accompanied by less environmental-state displacement than matched local-availability pseudo-trajectories.

See:

- [independent test protocol](docs/independent_test_protocol.md)
- [novelty boundary](docs/novelty_boundary.md)
- [stay in place versus stay in state](docs/azores_louisiana_contrast.md)
- [state-mismatch synthesis](docs/state_mismatch_synthesis.md)
- [analysis programme](analysis/README.md)
- [candidate systems and precedents](analysis/candidate_independent_systems.csv)

## Independent replication boundary

A 2026 South Carolina King Rail telemetry study supplies a complementary regime:

- 9 birds had both breeding and non-breeding telemetry;
- 5/9 shifted seasonal home ranges;
- mean shift about **2.9 km** (0.7–7.5 km);
- flooding and vegetation management altered habitat availability;
- birds used adjacent tidal marsh/flooded forest when local impoundments changed.

Lake Erie therefore tests **within-home-range micro-niche tracking**, while South Carolina represents the **broad-relocation boundary** when local compensation fails.

## Open cross-taxon generality test

A fully open Senegal Delta Black-tailed Godwit dataset provides a parallel falsification/generalization route:

- 22 GPS-tagged birds;
- June 2022–March 2023 tracking;
- raw individual GPS fixes;
- wet/dry-season individual habitat-composition tables.

This does **not** replace Lake Erie SRI because it lacks event-matched local availability. It tests whether large seasonal geographic shifts preserve or replace broad habitat state.

Implemented:
- `analysis/06_fetch_godwit_generality_data.py`
- `analysis/07_godwit_seasonal_state_displacement.py`
- [Godwit test contract](docs/godwit_generality_test_contract.md)

## Evidence boundary

The Lake Erie data archive is public, but this environment has not yet resolved its physical file list. The design is therefore frozen from the published methods before file-level schema inspection.

Individual bird—not the 607 point records—is the biological replication unit.

## Later extension

The hydrological-portfolio/HPI idea remains a stronger second stage and requires a repeated spatial habitat surface. Static heterogeneity alone is not enough.

## Role of EOG

EOG is only the discovery route. Its failure of simple local propagation suggested that geographic distance from previous detections may not be the biologically relevant state variable.


## Three separate EOG-derived ecology programmes

Louisiana is one of three independent ecological projects:

- **Azores:** state-dependent mobility gating;
- **Louisiana:** within-home-range micro-niche tracking;
- **Tampa:** buffered persistence under quantitative degradation.

These are not intended as one umbrella analysis or one shared endpoint.

See [three independent ecology programmes](docs/three_ecology_programs.md).


- [three-programme current status](docs/three_ecology_programs_status.md)
