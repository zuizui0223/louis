# Analysis programme

## Publication target

This repository does **not** aim to publish a second analysis of the 2012 King Rail occupancy paper.

The primary ecological programme is **environmental-state fidelity**:

> a resident animal may move within familiar space so that the environment it experiences changes less than the environment available around it.

See [general-principle programme](../docs/general_principle_program.md) and [independent test protocol](../docs/independent_test_protocol.md).

## Phase 0 — EOG seed diagnosis only

~~~bash
python analysis/01_failure_event_classification.py
~~~

This explains the discovery route only.

## Phase 1 — independent Lake Erie release

The Zenodo record is now resolved. For the canonical matched water-depth analysis run:

~~~bash
python analysis/08_lake_erie_standardize.py
~~~

This downloads and standardizes the public CART microhabitat table using source-defined `Missing` exclusions and strict point-ID parsing.

Then run:

~~~bash
python analysis/09_lake_erie_state_fidelity.py
~~~

Canonical state-fidelity result:
- [Lake Erie state-fidelity result](../results/lake_erie_state_fidelity_v1.json)
- [ecological interpretation](../docs/lake_erie_state_fidelity_result.md)

Then run the hydrological availability-coupling decomposition:

~~~bash
python analysis/12_lake_erie_availability_coupling.py
~~~

Canonical coupling result:
- [availability-coupling result](../results/lake_erie_availability_coupling_v1.json)
- [ecological interpretation](../docs/lake_erie_availability_coupling.md)

This asks how much local water-depth variation is transmitted into used water depth rather than only whether used-state variance is low.

The older generic fetch/schema scripts are retained for provenance and broader archive inspection.

## Phase 2 — state-fidelity schema gate

~~~bash
python analysis/04_state_fidelity_gate.py \
  --data-dir data/external/lake_erie_king_rail
~~~

Primary GO requires repeated:

~~~text
individual × event × used/random × water depth
~~~

Coordinates are preferred for the second "move in space to stay in state" test.

The older hydrological-portfolio gate remains a later, stronger extension and is no longer the first GO criterion.

## Phase 3 — standardized matched-event table

Construct a CSV with:

~~~text
individual_id,event_id,point_type,water_depth_cm
~~~

and preferably timestamp/latitude/longitude.

Then run:

~~~bash
python analysis/05_state_retention_index.py \
  --input <standardized_csv>
~~~

The script compares real used-state variance with event-matched random pseudo-trajectories.

## Phase 4 — movement-mediated state fidelity

If coordinates are available, test whether real geographic movements preserve environmental similarity more than matched availability pseudo-trajectories.

## Phase 5 — full portfolio extension

Only if a repeated spatial hydrological surface can be reconstructed should HPI/retained-suitable-area buffering be tested.

Static habitat heterogeneity is not sufficient.


## Parallel external-generality test — Godwit

Lake Erie remains the primary King Rail matched-availability design. Its Zenodo microhabitat archive is resolved and analysed. The fully public Senegal Delta Godwit dataset is now a separate external generality/falsification system.

Fetch the small Dryad files:

~~~bash
python analysis/06_fetch_godwit_generality_data.py
~~~

Then run:

~~~bash
python analysis/07_godwit_seasonal_state_displacement.py
~~~

The test estimates, for birds represented in both wet and dry seasons:

- seasonal GPS-centroid displacement;
- seasonal land-cover-composition Bray-Curtis dissimilarity;
- whether each bird's own wet-to-dry habitat composition is more similar than cross-individual seasonal pairings.

This is **not SRI** because the Godwit data do not provide the same event-matched local random availability design as Lake Erie.

Interpretation is deliberately two-sided:

- large geographic shift + low habitat dissimilarity -> compatible with broad environmental-state continuity;
- large geographic shift + high habitat dissimilarity -> seasonal resource tracking with habitat-state replacement.

See [Godwit test contract](../docs/godwit_generality_test_contract.md).


## Second Lake Erie movement-data route

The 2025 bagged-movement paper states that its King Rail example data are included in the Supporting Information archive `ECE3-15-e72060-s001.zip`.

After obtaining that ZIP:

~~~bash
python analysis/08_scan_bagged_movement_supplement.py \
  --zip <ECE3-15-e72060-s001.zip>
~~~

This can recover/verify movement trajectories even if the 2023 Zenodo route remains inaccessible.

**Boundary:** trajectory data alone do not replace the event-matched habitat availability needed for SRI.
