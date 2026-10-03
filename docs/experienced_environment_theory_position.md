# Theory position: experienced-environment buffering

## Why the Lake Erie result is not a new concept invented from scratch

Two existing theoretical lines already predict that organisms can regulate the environment they experience.

### Chesson & Yang 2019 — experienced environments of fluid populations

Chesson & Yang (2019), *Populations as Fluid on a Landscape Under Global Environmental Change*, DOI 10.3389/fevo.2019.00363, explicitly defines the **experienced environment** and asks when movement/dispersal across a changing landscape can make that experienced environment approximately stationary even when local environments are not.

That is conceptually very close to the biological logic uncovered here.

### Clark et al. 2020 — environmental buffering through habitat choice / niche construction

Clark et al. (2020), *Niche Construction Affects the Variability and Strength of Natural Selection*, DOI 10.1086/706196, treats habitat choice as a form of environmental regulation and predicts that organism-regulated environmental sources can show reduced temporal/spatial variation.

Therefore the Louisiana project must not claim:

> animals can buffer environmental variation by choosing where they are

as a new principle.

## What the Lake Erie analysis adds

The Lake Erie result is an **individual-level empirical operationalization** of that general theory in a resident wetland bird.

For each bird we observe:

- a repeated used microhabitat state;
- local availability sampled at the same event;
- repeated events through time.

The counterfactual is therefore not a regional climatology or a broad seasonal background.

It is:

> **what water-depth trajectory would this same bird have experienced if, at every observation event, it had used one of the locally available random points instead?**

Primary empirical result:

- 10/10 birds experienced lower temporal water-depth variance than matched local availability;
- 10/10 also experienced smaller successive water-depth changes than matched pseudo-trajectories;
- the result remains directional after conditioning availability on flooded habitat only.

## Ecological contribution

The project therefore tests a specific prediction implied by experienced-environment theory:

> **behavioural space use can reduce the temporal variance of the environment actually experienced by an individual.**

The important scale is unusually fine:

- resident home range;
- repeated microhabitat use;
- event-matched local counterfactual;
- individual-level replication.

## Why this is more than ordinary habitat selection

Ordinary habitat selection estimates whether some state is used disproportionately.

This analysis estimates a temporal property:

> **how much variability in environmental experience is removed by realised habitat use relative to simultaneous local availability.**

A bird can select shallow water on average without producing a strongly buffered trajectory if its used depths still vary as much as local availability.

Lake Erie birds show both:
- nonrandom state use;
- reduced temporal experienced-state variance.

## Remaining mechanistic boundary

The public coordinate layer is not event-keyed strongly enough for a universal row-order join.

Thus we have established:

> environmental-state buffering by repeated realised habitat use.

We have not yet established:

> a quantitative function linking geographic displacement distance to the amount of environmental-state buffering.

That stronger movement mechanism requires an event-keyed coordinate layer or another independent telemetry system.

## Novelty statement to use

Do not use:
> We introduce the idea that movement stabilizes experienced environments.

Use:
> **We provide an individual-level, time-matched availability test showing that repeated space use can substantially damp temporal variation in the environment experienced by resident wetland birds.**


## Stronger decomposition — availability coupling

The variance and successive-change analyses show that experienced water depth is temporally smoother than matched local availability.

A more mechanistic quantity asks:

> **how much of a change in local available water depth is transmitted into the water depth actually used?**

For each event:

~~~text
A_t = mean local random water depth
U_t = used water depth
~~~

Within birds, the observed slope is:

~~~text
U_t ~ A_t
~~~

while a pseudo-used trajectory drawn from the same random points has an expected slope near 1.

Lake Erie result:

- observed pooled within-bird slope: **0.162**
- matched pseudo-used null: **1.001**
- coupling reduction: **83.8%**

Flooded-habitat sensitivities retain **82–85%** reduction.

Thus the empirical contribution can be stated more directly:

> **resident King Rails transmit only a small fraction of nearby hydrological variation into the environmental state they actually experience.**

This is closer to environmental regulation than a simple statement about low used-state variance.

It still does not identify the geographic movement distance that produced that regulation because the coordinate/event join remains unresolved.
