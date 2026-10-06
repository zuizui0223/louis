# Novelty boundary

## What is already established

This project does not claim novelty for:

- King Rail habitat selection;
- shallow-water associations;
- site fidelity;
- flexible habitat use inside home ranges;
- resource tracking;
- ecological niche tracking;
- the general idea that animals move to remain within suitable environmental conditions.

The niche-tracking literature already shows that migratory birds can maintain similar climatic/environmental niches across distant seasonal ranges.

There is also a very close wetland precedent: tracked Shoebills moved between geographically distinct wetland areas while the mean NDWI of newly selected areas did not differ from the areas used immediately before departure. In other words, movement to a similar surface-water state has already been demonstrated.

A 2025 little-bustard study likewise showed that access to microclimate refugia predicted migration distance and that long-distance migrants maintained more similar microclimatic niches across seasons.

Therefore the phrase "move in space to stay in state" is **not itself a novelty claim**.

## Sharper novelty candidate

The candidate new contribution is a **fine-scale, resident, availability-relative version of niche tracking**:

> **within a stable home range, does an individual's realised movement make the sequence of environmental states it experiences more stable than the environmental states locally available at the same times?**

This differs from most seasonal niche-tracking analyses in three ways:

1. **scale** — within-home-range rather than breeding-versus-wintering ranges;
2. **behavioural regime** — resident fine-scale movement rather than migration;
3. **counterfactual** — time-matched local availability at each movement event rather than broad seasonal background environments.

## Primary operational test

For each individual King Rail:

~~~text
temporal variance of used water depth
<
temporal variance of matched local-availability pseudo-trajectories
~~~

This is quantified by the State Retention Index (SRI).

If coordinates are available, the stronger signature is:

~~~text
geographic displacement > 0
while
environmental-state displacement < matched-availability null
~~~

## Difference from ordinary habitat selection

Habitat selection asks:

> which states are used more than available?

Seasonal niche tracking asks:

> are environmental niches similar across distant seasonal ranges?

The present test asks:

> **does routine movement within a resident home range actively damp the temporal environmental variation experienced by the individual relative to what was locally available?**

That fine-scale dampening test is the novelty candidate.

## Evidence standard

Because the Lake Erie dataset contains only 10 birds with stabilized home ranges:

- individual bird is the replication unit;
- point-level n=607 is not biological replication;
- positive SRI should be consistent across individuals;
- one-bird dominance fails the claim;
- an external wetland species/population is required for generalization.

## Naming boundary

"Environmental-state fidelity" and "within-home-range micro-niche tracking" are descriptive working terms.

Do not claim novelty from either phrase. Claim novelty only from a supported, availability-relative temporal dampening result and its independent replication.


## Result now obtained

The independent Lake Erie test supports the availability-relative temporal dampening prediction.

Primary:
- 10/10 birds positive SRI;
- median SRI 0.886;
- exact sign-test p = 0.00098.

Time-ordered successive-state test:
- 10/10 birds show lower used water-depth change than matched availability;
- median retention 0.658;
- exact sign-test p = 0.00098;
- all 10 individual randomization tests pass p < 0.05.

Thus the novelty candidate is no longer merely hypothetical:

> **resident individuals repeatedly experience a temporally smoother microhabitat state than is available in nearby time-matched habitat.**

The remaining novelty boundary is important. This does not yet prove that geographic displacement itself causes the dampening, because the public coordinate files lack explicit event IDs for a verified join to the matched microhabitat table.

Generalization beyond this Lake Erie King Rail population remains required.


## Wet-versus-dry alternative rejected as sufficient

A post-hoc robustness analysis asked whether the result was trivial because local random points sometimes had zero water depth.

It was not sufficient.

After conditioning availability on flooded random points only:
- 10/10 birds retained a positive time-ordered state-retention effect;
- median temporal retention = 0.622.

When used and random points were all required to be flooded:
- 10/10 remained positive;
- median temporal retention = 0.528.

Therefore the supported result is quantitative within flooded habitat:

> **birds constrain the water-depth trajectory they experience, not merely the binary fact of being in wet habitat.**

This strengthens the ecological distinction from ordinary wet-versus-dry selection, while remaining a post-hoc sensitivity rather than a new confirmatory endpoint.


## Experienced-environment theory boundary

The deeper concept is not new.

Chesson & Yang (2019; DOI 10.3389/fevo.2019.00363) formalized the **experienced environment** of populations moving across changing landscapes and showed theoretically how movement can make experienced conditions more stationary than local environments.

Clark et al. (2020; DOI 10.1086/706196) likewise treats habitat choice as environmental regulation and tests the prediction that organism-regulated environmental sources have reduced temporal/spatial variation.

Therefore the Lake Erie contribution is empirical and scale-specific:

> **an individual-level, event-matched local-availability test of how much temporal environmental variation is damped by repeated realised habitat use in a resident wetland bird.**

See [theory position](experienced_environment_theory_position.md).


## 2025 variance-reduction precedent

Knight et al. (2025, *Acta Oecologica*, DOI 10.1016/j.actao.2025.104103) explicitly proposed **habitat selection as a reduction in habitat variance**. In GPS-collared white-tailed deer, used habitat showed lower variance in canopy closure than the surrounding environment, and the authors argued that selection for diminished environmental variance can be a fundamental property of habitat selection.

This closes an important novelty claim.

Louisiana must **not** claim that it is the first study to show that habitat choice can reduce environmental variance.

The Lake Erie contribution is narrower and more temporal:

1. availability is event-matched and local to the same observation time;
2. the analysis follows repeated individuals rather than comparing only aggregate used-versus-available distributions;
3. it tests temporal trajectory smoothness as well as variance;
4. the used-on-available slope quantifies how much contemporaneous local hydrological change is transmitted into the environment actually experienced by each bird.

Thus the strongest distinction is:

> **not whether habitat use has lower variance, but whether a resident individual's experienced environmental trajectory is dynamically decoupled from time-matched local environmental change.**

The pooled slope of 0.162 versus a matched pseudo-used expectation near 1 operationalizes this as an **environmental transmission / buffering coefficient**.

### Remaining novelty ceiling

Even this framing does not establish that geographic movement caused the buffering because the coordinate-event join remains unresolved.

The stronger future contribution would identify the boundary between:

- local within-home-range environmental buffering, and
- broader relocation or habitat-state replacement when acceptable local states are no longer reachable.

That boundary, rather than variance reduction alone, is the route to a more general movement-ecology principle.
