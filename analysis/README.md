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

Audit:

~~~bash
python analysis/02_fetch_public_comparative_data.py
~~~

Download the public files:

~~~bash
python analysis/02_fetch_public_comparative_data.py --download
~~~

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
