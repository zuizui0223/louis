# Independent test protocol: environmental-state fidelity

## Scientific target

The western Lake Erie King Rail dataset is not used to ask again which microhabitats birds select.

The published study already addressed habitat selection.

The new question is temporal:

> **Do birds move through geographic space in a way that stabilises the environmental state they experience?**

This is the **environmental-state fidelity** hypothesis.

## Biological distinction

Two forms of fidelity are separated.

### Place fidelity

The animal remains near the same coordinates or within the same home range.

### State fidelity

The animal repeatedly occupies a similar hydrological/microhabitat state even when the geographic location of that state changes.

This creates the ecological contrast:

~~~text
Azores anchoring:     stay in place -> stay in state
dynamic wetland:      move in place-space -> stay in state
~~~

## Why the Lake Erie design is useful

For each King Rail homing event the source study measured:

- one used microhabitat plot at the bird location;
- two random plots 75 m away;
- surveys within 72 h of the homing event;
- water depth and vegetation/structure variables.

The random plots are therefore a local, time-matched availability sample.

This enables a temporal test that is different from ordinary used-versus-random selection.

## Primary estimand: state stabilisation

For individual i and homing event t, let:

- U_it = environmental state at the used point;
- R1_it, R2_it = paired available states.

For water depth as the first transparent state axis:

~~~text
V_used,i = temporal variance of used water depth
~~~

Generate a matched null by repeatedly selecting one of the two random points at every event:

~~~text
V_null,i^(b) = temporal variance of one matched available state per event
~~~

Define the **State Retention Index**:

~~~text
SRI_i = 1 - V_used,i / median_b(V_null,i^(b))
~~~

Interpretation:

- SRI > 0: the bird experiences a more stable water-depth state than expected from locally available time-varying habitat;
- SRI ~ 0: experienced-state variability follows availability;
- SRI < 0: the bird experiences more variable states than the matched local habitat.

The exact estimator can be generalised to multivariate habitat state after the univariate water-depth analysis is frozen.

## Secondary estimand: move in space to stay in state

For consecutive used locations:

- geographic displacement = distance between successive used positions;
- environmental displacement = distance between successive used habitat states.

The key signature is not simply low movement.

It is:

> **substantial geographic displacement accompanied by lower environmental-state displacement than matched available pseudo-trajectories.**

This is the direct operational meaning of "move in space to stay in state."

## Matched pseudo-trajectory null

For each individual:

1. preserve the real sequence of homing-event times;
2. at each event choose one of the two paired random points;
3. create many pseudo-trajectories;
4. calculate environmental-state variance and consecutive environmental displacement;
5. compare the real used trajectory with this availability-preserving null.

This controls the fact that wetland conditions themselves change through time.

## Model ladder

### L0 — published-style habitat selection

Used versus random conditions. This is provenance, not the new endpoint.

### L1 — state fidelity

Test whether used-state temporal variance is lower than matched availability variance.

### L2 — movement-mediated state fidelity

Test whether geographic movement is associated with maintaining environmental similarity between successive used states.

### L3 — individual heterogeneity

Ask whether individuals differ in SRI and whether those differences correspond to home-range size/heterogeneity.

### L4 — full hydrological portfolio

Only if a repeated spatial hydrological surface can be reconstructed, estimate retained suitable area/HPI within each home range.

L4 is stronger but is **not required** for L1/L2.

## Falsification

Environmental-state fidelity is not supported if:

- used-state variance is not lower than matched local availability;
- used environmental displacement is indistinguishable from pseudo-trajectories;
- geographic displacement does not preserve environmental state;
- the result exists only after choosing a post-hoc water-depth window;
- one individual drives the result.

## Claim boundary

This test does not claim that birds consciously target a numerical water depth.

It tests whether realised space use stabilises experienced environmental conditions relative to what was locally available.

The source dataset is independent of the original Louisiana EOG endpoint, but the hypothesis was generated after observing EOG results. This is an independent-data test, not a preregistered study.

## Strong ecological conclusion if supported

> **Site fidelity can be achieved by environmental homeostasis rather than immobility: animals may move within a familiar landscape to remain faithful to a preferred habitat state.**


## Sampling-unit correction from the published design

The independent Lake Erie study contributes:

- 10 individuals with stabilized home ranges;
- 206 used/homing microhabitat surveys;
- 401 random microhabitat surveys;
- 14–36 homing locations per individual.

The source paper had 607 point-level records for habitat-selection CART, but **607 is not the biological replication level for the present temporal hypothesis**.

Primary replication is the **individual bird (n = 10)**.

### Required inference hierarchy

1. build the used-state time series separately for each bird;
2. generate matched-availability pseudo-trajectories separately within that same bird;
3. estimate SRI per bird;
4. report the distribution/sign consistency of the 10 individual SRI values;
5. use individual-level bootstrap/randomization or a hierarchical model for population inference.

Do not treat the 206 homing events as 206 independent birds.

### Event matching

The published design measured one used plot plus two plots 75 m away in random directions within 72 h of each homing event. In practice the final data contain 401 random surveys for 206 homing surveys rather than exactly 412, so the standardizer must allow events with one available random point while reporting missing-pair frequency.

### Temporal autocorrelation is now biology, not a nuisance to erase

The source paper checked point-to-point autocorrelation because its goal was habitat selection and reported representative autocorrelation values including water depth around r = 0.43.

Our question is explicitly temporal.

Therefore:

- do not mechanically thin the time series until autocorrelation disappears;
- quantify the persistence timescale of used environmental state;
- compare that persistence with matched availability trajectories;
- distinguish biological state retention from simple low variance caused by seasonally static water levels.

### Strong result criterion

The strongest Lake Erie result would be:

> most individual birds show positive SRI, and the used-state sequence is more environmentally stable than event-matched local availability even though birds changed geographic positions.

A single pooled point-level p-value is insufficient.
