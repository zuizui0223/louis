# Lake Erie King Rail: independent environmental-state fidelity result

## Data reconstruction

The public Lake Erie Zenodo archive was resolved directly.

The source microhabitat table contains **607 rows**. Source coding states that `Missing = Yes` rows should be excluded.

Frozen QC produced:

- 17 source-defined missing rows excluded;
- 2 malformed point IDs excluded without repair;
- 190 valid used + local-random matched events;
- 10 individual birds;
- 173 events in the stricter subset where both random plots were retained.

The point IDs preserve bird identity and matched event structure, e.g.

```text
165.020H1_21    used point
165.020R1_1_21  random point 1
165.020R1_2_21  random point 2
```

All three correspond to the same bird/event and Julian date.

## Primary result — State Retention Index

For each bird:

```text
SRI
= 1 - variance(used water depth)
      / median variance(time-matched random pseudo-trajectories)
```

Monte Carlo:
- 100,000 pseudo-trajectories per bird;
- deterministic xorshift32 generator;
- fixed seed family from 20261001.

### Result

- **10/10 birds had SRI > 0**
- median SRI = **0.886**
- mean SRI = **0.764**
- range = **0.402–0.976**
- exact one-sided sign test for 10/10 positive = **p = 0.00098**

Nine of ten birds had an individual Monte Carlo lower-tail p < 0.05. The exception was `881_20` (approximately p = 0.20).

### Strict paired-availability sensitivity

Restricting to events in which **both** random plots were available:

- 173 matched events;
- **10/10 birds remained positive**
- median SRI = **0.882**
- range = **0.369–0.976**
- sign test **p = 0.00098**

Eight of ten birds had individual p < 0.05.

Thus the population-level directional result does not depend on accepting events with only one surviving random plot.

## Temporal result — successive state change

Variance alone ignores event order.

A second frozen-compatible test therefore ordered each bird's events by year and Julian date and compared:

```text
mean absolute change in used water depth
versus
mean absolute change in matched-random pseudo-trajectories
```

Define temporal retention:

```text
1 - used successive-state change / median null successive-state change
```

### Result

Primary 190-event panel:

- **10/10 birds positive**
- median temporal retention = **0.658**
- range = **0.388–0.879**
- sign test **p = 0.00098**
- **10/10 birds individually p < 0.05**

Strict 173-event two-random panel:

- **10/10 birds positive**
- median temporal retention = **0.667**
- range = **0.329–0.879**
- sign test **p = 0.00098**
- **10/10 birds individually p < 0.05**

This is the stronger ecological result.

> **King Rails repeatedly occupied a temporally smoother water-depth trajectory than would be expected by sampling the locally available habitat at the same observation times.**

## Biological interpretation

The result goes beyond the source paper's ordinary used-versus-random habitat-selection question.

It says that, within individuals, repeated used microhabitats **dampen environmental-state variation through time** relative to time-matched local availability.

This is consistent with **within-home-range micro-niche tracking / environmental-state fidelity**.

The result is especially striking because the comparison does not use a post-hoc preferred water-depth interval. It compares the complete observed water-depth trajectory directly with event-matched availability.

## Hydrological coupling decomposition

A second mechanistic decomposition asks how strongly temporal change in nearby available water depth is transmitted into the water depth actually used by a bird.

For each event:

~~~text
A_t = mean water depth of event-matched random plots
U_t = used/homing water depth
~~~

Within-bird slope of U_t on A_t:

- observed pooled slope: **0.162**
- pseudo-used null median: **1.001**
- coupling reduction: **83.8%**
- **10/10 birds** below their individual null median

Flooded-habitat sensitivities retain **82–85% coupling reduction**.

This means the SRI pattern is not only a low-variance summary. As nearby hydrology changes, only a small fraction of that local depth change is expressed in the microhabitat actually used.

See [availability-coupling analysis](lake_erie_availability_coupling.md).

## What is not yet established

The stronger statement:

> birds physically move farther in geographic space in order to remain stable in environmental-state space

is not yet directly tested.

Reason:
- individual coordinate files are public;
- but those coordinate CSVs contain bird ID and UTM X/Y only, without explicit homing-event/date IDs;
- row-order correspondence to the CART homing events has not been independently documented.

Do not silently join coordinates to microhabitat events by row order.

Therefore the supported claim is currently:

> **experienced microhabitat state is temporally stabilized relative to local availability.**

The explicit movement-mediated mechanism remains one step stronger and requires a verified coordinate-to-event join.

## Evidence class

This is an **independent-data developmental test** generated from the EOG-derived hypothesis.

The Lake Erie dataset is independent of the original Southwest Louisiana EOG endpoint. The test is not described as preregistered.

## Why this matters for the Louisiana paper

The original Louisiana EOG anomaly suggested that simple geographic propagation from prior detections was the wrong ecological picture.

The independent Lake Erie result now supplies a concrete alternative biology:

> **a resident rail can be spatially flexible at fine scales while keeping the environmental state it experiences unusually stable through time.**

This converts the Louisiana line from a hypothesis-only programme into an empirical behavioural-ecology result.
