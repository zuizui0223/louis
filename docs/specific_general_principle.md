# Specific general principle for Louisiana: monitoring networks are not ecological state networks

## Why Louisiana is not just another occupancy reanalysis

The published Louisiana study already estimated occupancy and detection for 11 secretive marsh-bird species and documented marsh/salinity associations.

Repeating that model is not the new question.

The EOG anomaly was different:

- detections contained weak temporal-history information;
- all six simple local propagation worlds built from **detected sites as sources** were eventually falsified;
- the only always-compatible world was an intentionally open external-source world.

The key ecological issue is therefore the mapping between **what the monitoring network sees** and **where the biological population can actually persist or move**.

## The biological contrast that matters

An ARU site is not a habitat patch.

The 33 recording stations are points sampling a continuous marsh landscape. Birds can:

- remain near a station but go undetected;
- occupy marsh between stations;
- move through unsampled habitat;
- be replaced by another individual of the same species;
- call at one occasion and remain silent at another.

Because individuals are not identified, the observation sequence cannot directly distinguish:

```text
same individual persists
different individual arrives
site remains occupied but is missed
local extinction + recolonisation
regional movement through unsampled habitat
```

This is fundamentally different from individual telemetry.

## Candidate general principle

> **When observation nodes are sparse proxies for a continuous latent ecological state space, treating detections as occupied source nodes can convert persistence and nondetection into apparent spatial turnover or long-distance colonisation.**

Provisionally:

> **monitoring-network topology is not population-process topology.**

This is the central general principle for `louis`.

## Why King Rail is an informative anchor

The system combines:

- imperfect acoustic detection;
- no individual identity;
- repeated observations;
- a continuous wetland matrix;
- strong habitat/salinity structure;
- sampling sites rather than discrete habitat patches;
- an explicitly open population relative to the 33-point monitoring network.

Therefore a failed detected-source propagation model is not surprising in the same way that a failed marked-individual movement model would be.

Its failure is informative about **observability and spatial closure**.

## Three ways a false propagation signal is generated

### 1. False disappearance -> apparent reappearance

True state:

```text
occupied -> occupied -> occupied
```

Observed state:

```text
1 -> 0 -> 1
```

A detection-source model sees the final 1 as a new arrival even though no colonisation occurred.

### 2. Hidden source in unsampled marsh

True process:

```text
sampled site A <- unsampled occupied marsh -> sampled site B
```

Observed network:

```text
A        B
```

B can appear unsupported because the true source is not a node.

### 3. Identity replacement

Observed:

```text
site i: 1 -> 1
```

could represent one persistent bird or turnover among individuals.

The same detection history can therefore correspond to very different demographic processes.

## The general variables are not just detection probability

For a monitoring network define:

- (p): detection probability;
- (C_S): **spatial closure** — fraction of biologically relevant source/intermediate habitat represented by monitored nodes;
- (I): **identity resolution** — whether observations can be linked to the same biological entity through time;
- (N_A): **node-state alignment** — how closely a monitoring node corresponds to a real ecological state unit/patch;
- (d_S): spacing among sensors relative to movement/use scale;
- (Delta t): observation interval relative to persistence/turnover timescale.

The Louisiana case has low identity resolution and incomplete spatial closure. Its ARU sites are observation points, not closed population states.

## Testable general predictions

### L1 — propagation inference degrades with low closure

At fixed biological movement, detected-source propagation models should generate more unsupported appearances as (C_S) declines.

### L2 — imperfect detection interacts with closure

The error is not additive:

low (p) + low (C_S) should generate substantially more apparent colonisation than either alone.

### L3 — identity resolution changes what can be inferred

When individuals are marked/identified, persistence and movement can be separated directly. When identity is collapsed to species-level detection, the same spatial sequence becomes partially unidentified.

### L4 — node-state alignment matters

Propagation inference should work better in systems where nodes are true discrete habitat patches than in systems where sensors sample a continuous matrix.

This gives a concrete reason why metapopulation-style network logic transfers poorly to some passive-monitoring datasets.

## Strong empirical design

The publication target should compare systems across a factorial observability gradient:

| System type | Identity | Spatial closure | Node = ecological patch? |
|---|---|---|---|
| telemetry of marked individuals | high | variable | often moderate/high |
| nest/territory resighting | high | moderate | high |
| discrete pond/island occupancy | low | high | high |
| camera/ARU in continuous habitat | low | low/moderate | low |
| eDNA/grid surveillance | none | low | low |

Known-truth simulations can manipulate (p, C_S, I, N_A, d_S, Delta t) independently.

The empirical question becomes:

> **Under which observation geometries can sequential detections legitimately identify propagation, and under which geometries are persistence and hidden sources fundamentally confounded with it?**

## Role of EOG

EOG exposed the problem by failing all six local detected-source worlds.

That failure is not the final result. It is the clue that the **source graph was an observation graph, not necessarily the biological graph**.

The general paper must test this observability principle across independent monitoring systems and known-truth simulations.
