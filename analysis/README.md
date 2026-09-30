# Analysis programme

## Publication target

This repository does **not** aim to publish a second analysis of the King Rail paper.

Louisiana is a seed system for the cross-system **memory–propagation regime programme**:

> predictive memory can arise from local persistence, shared forcing, observation-process memory, or actual propagation; history-based forecast gain alone does not identify which source generated it.

See [general-principle programme](../docs/general_principle_program.md).

## Phase 0 — seed-system diagnosis only

Phase 0 asks why the EOG detection-source worlds failed. It is ordered so that an observation-process explanation is tested before any movement interpretation.

### Phase 0A — classify the actual failure events

Run:

```bash
python analysis/01_failure_event_classification.py
```

This opens only the already-consumed King Rail response and classifies positive events into:

1. same-site continuation;
2. same-site return after a detection gap;
3. first detection near prior positives;
4. first detection outside prior observed support.

This directly identifies which kinds of events falsified the six detection-source worlds.

### Phase 0B — detection versus changing latent state

Run:

```bash
python analysis/run_detection_state_decomposition.py
```

This compares two deliberately minimal alternatives with a chronological holdout:

- **M0:** static latent occupancy + quadratic seasonal detection;
- **M1:** continuous-time dynamic occupancy + the same detection model.

Both use the same low- versus high-salinity habitat term for initial occupancy and are fitted on the first 12 chronological occasions, then predict the final 8 without refitting.

The decision target is:

> Can imperfect/seasonal detection of a persistent latent state explain the apparent turnover, or does a changing ecological state add held-out information?

Only if a changing latent state survives this gate should the project proceed to latent-neighbour propagation or broader regional/open-population terms.

These same-data analyses are **not the paper endpoint**. Their role is to locate Louisiana on the general memory-source regime map and to identify what must be tested prospectively elsewhere.

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
