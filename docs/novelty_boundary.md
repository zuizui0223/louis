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
