# Analysis programme

## Publication target

This repository does **not** aim to publish a second analysis of the 2012 King Rail occupancy paper.

The primary ecological programme is **hydrological portfolio buffering**:

> temporally complementary microhabitats may let a resident bird track suitable states inside a familiar area instead of abandoning it when hydrology changes.

See [general-principle programme](../docs/general_principle_program.md).

## Phase 0 — EOG seed diagnosis only

```bash
python analysis/01_failure_event_classification.py
```

This only explains the discovery route. It is not the paper endpoint.

## Phase 1 — independent Lake Erie dataset

Audit the public Zenodo release:

```bash
python analysis/02_fetch_public_comparative_data.py
```

Download public files:

```bash
python analysis/02_fetch_public_comparative_data.py --download
```

Then gate the dataset:

```bash
python analysis/03_hydrological_portfolio_gate.py \
  --data-dir data/external/lake_erie_king_rail
```

**Hard rule:** static habitat heterogeneity is not a hydrological portfolio. The full HPI hypothesis is eligible only when movement can be linked to time-varying hydrological state within the familiar area.

## Phase 2 — if the gate passes

Estimate:

- internal microhabitat switching;
- retained suitable area through time;
- lower-tail habitat retention (HPI);
- broad relocation / familiar-area displacement.

Primary test:

```text
broad relocation ~ HPI
                 + mean habitat quality
                 + hydrological change
                 + HPI × hydrological change
```

The decisive result is whether temporal complementarity explains residency beyond mean habitat quality.

## Phase 3 — independent replication

Use another wetland bird system with dynamic water surfaces to test whether the buffering mechanism generalises beyond King Rail.
