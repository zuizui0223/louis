# Lake Erie robustness: the result is not only wet-versus-dry selection

## Alternative explanation

The primary Lake Erie state-fidelity result could be trivial if random points were highly variable only because they frequently included dry ground.

Under that explanation:

> birds simply select flooded habitat, and the apparent temporal water-depth retention adds little beyond ordinary wet-versus-dry habitat selection.

This was tested post hoc as a robustness analysis.

## Sensitivity 1 — condition availability on flooded random points

For every matched event:

- remove random plots with `WaterDepth <= 0`;
- retain the event if at least one flooded random plot remains;
- generate pseudo-trajectories only from flooded local availability.

Result:

### Variance SRI
- 182 events;
- **10/10 birds positive**;
- median retention **0.863**;
- range **0.180–0.976**;
- sign test **p = 0.00098**.

### Time-ordered successive-state retention
- **10/10 birds positive**;
- median retention **0.622**;
- range **0.313–0.859**;
- sign test **p = 0.00098**;
- **10/10 birds individually p < 0.05**.

## Sensitivity 2 — all retained points flooded

Require:

- used point > 0 cm;
- every retained random point > 0 cm.

This leaves 131 events.

### Variance SRI
- **10/10 birds positive**;
- median retention **0.788**;
- range **0.232–0.976**;
- sign test **p = 0.00098**.

### Time-ordered successive-state retention
- **10/10 birds positive**;
- median retention **0.528**;
- range **0.208–0.862**;
- sign test **p = 0.00098**.

Individual precision is lower in this reduced panel, as expected, but the directional result remains universal across the 10 birds.

## Ecological interpretation

The Lake Erie result cannot be reduced to:

> King Rails choose water rather than dry ground.

Even **within flooded local habitat**, the sequence of water-depth states actually used by the birds varies less than event-matched availability.

The stronger supported statement is therefore:

> **King Rails repeatedly constrain the hydrological state they experience through time, relative to locally available flooded habitat.**

This is closer to fine-scale hydrological niche tracking than to a one-time shallow-water preference.

## Boundary

This is a post-hoc robustness analysis motivated after obtaining the primary SRI result.

It strengthens interpretation but does not replace the independent-data primary test.

Geographic movement remains unlinked at event level because the separate coordinate files lack explicit event/date keys.
