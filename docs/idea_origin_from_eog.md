# Idea origin: ecological questions extracted from EOG

## Purpose

This repository is an independent ecological project about the spatiotemporal ecology of secretive marsh birds, initially centred on King Rail (*Rallus elegans*) in southwest Louisiana.

EOG is retained only as the **hypothesis-generating origin**.

The transfer rule is strict:

- migrate empirical associations and failed spatial explanations that suggested ecological questions;
- do **not** migrate EOG's Layer A/Layer B product claims;
- do **not** treat predictive complementarity as evidence for a movement mechanism;
- re-test ecological hypotheses directly with the original marsh-bird observations.

## What EOG actually showed

The fresh Louisiana endpoint was site-occasion observed King Rail detection across **33 sites and 20 sampling occasions**.

The conventional predictor already contained:

- season / day-of-year;
- precipitation and minimum air temperature;
- coordinates;
- marsh class and habitat class;
- site-network degree at three spatial scales;
- previous-occasion detection;
- occasions since last detection;
- cumulative previous detections;
- number of previously detected sites;
- local previous-source counts/exposures;
- cumulative historical-source counts/exposures.

Adding the EOG world-support summary changed held-out macro log loss from **0.2463173 to 0.2453455**, with improvement in **7/8** held-out occasions. The effect was small.

More importantly, **all six frozen local propagation worlds were falsified**. Those worlds crossed three spatial thresholds (approximately 2.73, 2.98 and 17.01 km) with either immediate-previous or cumulative-observed source definitions. Only the conservative `external_open` world remained.

This means the observed positive detections were not compatible with the particular family of simple local-propagation explanations tested by EOG.

It does **not** prove long-distance movement, immigration, true occupancy, or any single alternative mechanism. Acoustic detection is not occupancy.

## Ecological signal carried forward

Two observations are migrated as hypothesis-generating associations:

1. **site/history state retained a small amount of information about future detection beyond habitat, weather, season and explicit detection-history covariates;**
2. **that information cannot be interpreted as simple local spread from recently detected sites at the tested spatial scales.**

This creates a sharper ecological question:

> **Why is marsh-bird occurrence temporally structured if simple local propagation cannot generate the observed pattern?**

## Competing ecological hypotheses

### H1 — Site-use memory / persistent latent occupancy

Individuals or local populations persist at the same marsh sites across occasions. Repeated detections therefore arise from persistent site use rather than repeated local colonisation from neighbouring detected sites.

Prediction: previous state at the same site should dominate neighbourhood propagation once detection error and season are separated.

### H2 — Habitat filtering creates apparent memory

Persistent detections reflect stable habitat selection. Fresh/intermediate-marsh specialists repeatedly appear at the same sites because those sites remain suitable, not because previous use has a direct biological memory effect.

Prediction: site-history effects should shrink after finer habitat/salinity structure is modelled; persistence should be strongest in the species' preferred marsh zone.

### H3 — Regional or synchronized detectability

Season, weather, calling behaviour or other regional drivers synchronously alter acoustic detection across many sites. This can create temporal structure without local occupancy propagation.

Prediction: a shared occasion-level effect should explain covariance among spatially separated sites better than nearest-neighbour source terms.

### H4 — Open-population spatial dynamics

Movement, recruitment or persistence may involve unsampled sites or spatial scales larger/different from the tested local networks.

Prediction: local neighbourhood effects remain weak after accounting for detection, while broader regional state or open-population terms explain residual temporal structure.

## Generalisation beyond King Rail

The source dataset contains a multi-species marsh-bird community, so the eventual ecological test should not stop at King Rail if the released data permit consistent reconstruction.

A strong comparative question is:

> **Does salinity-niche breadth predict the balance between habitat filtering, site memory and spatiotemporal turnover across marsh-bird species?**

Candidate prediction:

- narrower salinity/habitat specialists show stronger stable-site filtering;
- broader-niche species show greater temporal turnover and weaker same-site memory;
- species with strongly synchronized calling phenology show larger occasion-level covariance that should not be mistaken for movement.

This comparative extension must be tested independently; it is a hypothesis generated from the King Rail EOG failure pattern, not an EOG result.

## First causal decomposition to test

```text
stable habitat / salinity filtering
        +
same-site ecological memory
        +
regional occasion effects / detectability
        +
open-population movement
        ->
observed site-occasion detections
```

The main task is to determine which component creates the temporal structure that simple local propagation failed to explain.

## Boundary

EOG supplied the anomaly and the association pattern. This repository must supply the ecology.

