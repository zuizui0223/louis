# From the EOG result to ecological tests

## Status

This document converts the observed EOG King Rail result into explicit ecological hypotheses and next tests.

The EOG result is hypothesis-generating. It did not identify a movement process, true occupancy state, or cause of the observed acoustic detections.

## 1. What the EOG result actually says

The frozen endpoint was King Rail (*Rallus elegans*) detection at **33 sites × 20 sampling occasions**.

The conventional predictor already included:
- season/day of year;
- precipitation and minimum air temperature;
- coordinates;
- marsh and habitat classes;
- spatial-network degree;
- previous-occasion detection;
- time since last detection;
- cumulative prior detections;
- previous positive-site count;
- local previous-source counts/exposures;
- cumulative historical-source counts/exposures.

Adding the EOG world-support summary changed held-out macro log loss from **0.2463173 to 0.2453455** (about **0.39%** improvement), with the augmented arm better in **7/8** held-out occasions.

This is a small but repeatable directional signal. It should not be oversold.

## 2. The more important EOG result: all local worlds failed

The frozen local family contained:

- three spatial thresholds: approximately **2.73, 2.98 and 17.01 km**;
- two observed-source rules:
  - immediately previous detected sites;
  - cumulative historically detected sites.

All six local worlds were eventually falsified by positive detections. Only the deliberately conservative `external_open` world survived.

Logically, this means:

> At least one observed positive could not be supported by one or more of the declared local observed-detection source rules, and eventually every local rule failed.

It does **not** mean that a bird necessarily moved more than 17 km.

## 3. Why imperfect detection is the first explanation to test

The EOG source state was built from **observed positive detections**, not latent occupancy.

A site can therefore be genuinely occupied but absent from the EOG source set after a false negative. A later call from the same or another unsampled/previously undetected occupied site then appears to the observed-source model as a new unsupported event.

That mechanism is especially plausible here because the original study was explicitly an occupancy/detection study of secretive marsh birds.

The published analysis used a multi-species Bayesian hierarchical occupancy model, found a quadratic Julian-date effect on detection, and did not find minimum temperature or precipitation effects on detection. King Rail occupancy was concentrated mainly in freshwater/intermediate marshes.

Source study:
- Waddle et al. 2022, *Wetlands*, DOI: 10.1007/s13157-022-01548-4
- https://doi.org/10.1007/s13157-022-01548-4
- data: https://doi.org/10.5066/P9RRIIR2

Therefore the leading ecological interpretation is:

> **The EOG "propagation failure" may be the signature of latent occupancy plus imperfect/seasonal detection, rather than biological long-distance movement.**

That interpretation is now a direct test target.

## 4. Competing ecological explanations

### H-L1 — persistent latent site occupancy + imperfect detection

King Rails persist at suitable marsh sites across occasions, but calls are missed on some occasions.

Prediction:
- many EOG-unsupported "new" positives occur at sites whose latent occupancy probability was already high;
- a dynamic/static latent occupancy model produces the observed apparent jumps without requiring local colonisation from a previously detected source;
- same-site persistence is strong while detection varies over date.

### H-L2 — stable habitat filtering creates repeated site use

Fresh/intermediate marsh structure keeps the same subset of sites suitable.

Prediction:
- site-level marsh/salinity variables explain much of long-term occupancy;
- after latent occupancy and habitat are included, neighbourhood propagation contributes little.

### H-L3 — regional calling synchrony

Occasion-level calling conditions or phenology affect many distant sites simultaneously.

Prediction:
- a shared occasion effect explains co-detection across spatially separated sites;
- the effect follows seasonal calling phenology more strongly than local-neighbour distances.

### H-L4 — genuinely open spatial dynamics

Birds may enter from unsampled marsh, move at scales larger than the tested local graph, or use intermediate sites not represented in the 33-node registry.

Prediction:
- after accounting for detection and habitat, genuine occupancy transitions remain that are not explained by same-site persistence or local neighbours;
- broader regional/open-population terms improve the latent-state model.

## 5. First diagnostic: classify the EOG failure events

Before fitting a complex model, every positive site-occasion should be classified as:

1. **same-site continuation** — positive in the previous occasion;
2. **same-site return after detection gap** — previously detected at the same site, but not in the immediately previous occasion;
3. **first detection near prior positives** — first positive at that site but within each frozen threshold of a prior positive;
4. **first detection outside the local observed network** — first positive at a site outside the relevant prior-source support.

This classification directly tells us which biological/observation process is capable of falsifying each EOG world.

### Critical interpretation

- Type 2 strongly supports a detection/persistence explanation over movement.
- Type 4 is compatible with imperfect prior detection, open-population movement, or unsampled intermediates and therefore remains mechanistically unresolved.

## 6. Next model: occupancy/detection decomposition

Let:

- (z_{i,t}) = latent occupancy/use state at site (i), occasion (t);
- (y_{i,t}) = observed acoustic detection.

Observation model:

[
y_{i,t} sim Bernoulli(z_{i,t} p_{i,t})
]

with detection probability allowed to depend on seasonal date and, where justified, weather.

State model should compare the following nested explanations.

### M0 — habitat + detection

Static habitat/salinity occupancy plus occasion-dependent detection.

### M1 — same-site persistence

M0 plus previous latent state (z_{i,t-1}).

Question:
> Is the dominant temporal process persistence at the same site?

### M2 — local-neighbour propagation

M1 plus neighbouring latent occupancy at the three predeclared EOG spatial scales.

Question:
> After correcting detection, is there evidence for local spatial propagation?

### M3 — shared regional occasion process

M1 plus a shared occasion random effect / regional state.

Question:
> Are distant sites synchronized by a common temporal driver?

### M4 — open-population component

M1/M3 plus colonisation from outside the observed local network or an unconstrained regional source term.

Question:
> Is an open source still required after detection and site persistence are represented?

## 7. Decision logic

### Outcome A — M1 sufficient; M2 negligible

Interpretation:
> EOG local-world failure was mainly caused by using detections as sources when the ecology is persistent latent occupancy with imperfect detection.

This would be a strong biological/observation-process result.

### Outcome B — M3 important

Interpretation:
> temporal pattern is regionally synchronized rather than locally propagated.

### Outcome C — M2 remains important

Interpretation:
> there is genuine local spatial dependence after separating detection and persistence.

Only here does a local movement/colonisation interpretation become plausible.

### Outcome D — M4 required

Interpretation:
> the sampled 33-site network is not spatially closed at the temporal scale of the study.

This can represent immigration, unsampled intermediate habitat, or broader movement; it does not identify which without further data.

## 8. Multi-species prospective extension

The released dataset contains detection histories for 11 secretive marsh-bird species. EOG consumed only the King Rail response payload for this endpoint.

The King Rail result can therefore generate a **predeclared temporal-structure test** for the remaining species before their detailed detection sequences are inspected.

The broad habitat associations from the original paper are already public, so this is not fully response-blind with respect to habitat niche. However, the detailed temporal sequences and the proposed memory/turnover endpoints can still be frozen before inspection.

General hypothesis:

> **Salinity/habitat niche breadth changes the balance among stable habitat filtering, same-site persistence, and temporal turnover.**

Predictions:
- low-salinity specialists show strong stable-site filtering;
- generalists show greater site turnover;
- species with stronger seasonal calling structure show stronger occasion-level synchrony;
- local-neighbour propagation should not be assumed to be the dominant process.

## 9. Scientific question carried forward

> **When secretive marsh-bird detections are temporally structured but simple local propagation fails, is that structure generated by persistent latent occupancy, habitat filtering, synchronized detectability, or genuinely open spatial dynamics?**

This is now the primary ecological target of the Louisiana repository.
