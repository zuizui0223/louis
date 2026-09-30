# Analysis programme

## Publication target

This repository does **not** aim to publish a second analysis of the King Rail paper.

Louisiana is a seed system for the cross-system **memory–propagation regime programme**:

> predictive memory can arise from local persistence, shared forcing, observation-process memory, or actual propagation; history-based forecast gain alone does not identify which source generated it.

See [general-principle programme](../docs/general_principle_program.md).

## Phase 0 — seed-system diagnosis only

Run:

```bash
python analysis/01_failure_event_classification.py
```

The script opens only the already-consumed King Rail response and identifies why detection-source propagation worlds failed.

This is not the publication endpoint. Its role is to estimate whether Louisiana sits primarily in the persistence/observation corner or whether residual propagation remains plausible.

## Phase 1 — known-truth regime benchmark

Build simulated detection histories with known latent states spanning:

- persistent occupancy + imperfect detection;
- regional/common forcing;
- true local propagation;
- open-population influx;
- mixed regimes.

Vary detection probability and observation interval so that apparent turnover can be separated from latent turnover.

## Phase 2 — independent cross-system panel

Add independent passive-acoustic, camera or repeated-occupancy systems whose temporal sequences were not used to generate the hypothesis.

For each system estimate:

1. history-based forecast gain;
2. latent persistence;
3. shared temporal forcing;
4. observation-process memory;
5. residual directional propagation;
6. re-binning response.

## Phase 3 — comparative principle

Test whether the proposed scale ratios predict memory source across systems better than species identity, taxonomic group or monitoring modality.

King Rail is one anchor point, not the evidence base.
