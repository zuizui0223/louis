# General-principle programme: memory is not propagation

## Why this project must go beyond re-analysis

The originating datasets were already published and the EOG responses have already been opened. Re-fitting those same data with another ecological model can diagnose mechanisms, but **that is not the publication endpoint**.

The single-system analyses in this repository have only two roles:

1. identify which kind of temporal/spatial memory the seed system plausibly represents;
2. generate quantitative predictions for a genuinely cross-system test.

The target is a general ecological principle that can be tested across taxa, ecosystems and monitoring designs.

## Candidate general principle

> **Predictive memory is not spatial propagation.**

More precisely:

> When recent ecological observations improve prediction beyond current environment and static habitat, the gain shows that the measured present state is incomplete. It does not identify why the system has memory.

At least four sources can produce the same forecast pattern:

1. **local persistence / endogenous state memory** — the same organism, population or local state persists;
2. **shared exogenous forcing** — spatially separated sites respond coherently to weather, hydrology, resources or disturbance;
3. **observation-process memory** — detectability, sensor operation, activity or sampling creates temporally correlated observations;
4. **spatial propagation** — movement, colonisation or other transmission carries state among sites.

Only (4) is spatial propagation.

The general problem is therefore not to ask whether "history helps", but:

> **Under what spatial and temporal regimes does predictive history represent persistence, forcing, observation, or propagation?**

## Literature boundary

Existing work already establishes important pieces of this problem:

- ecological-memory frameworks separate antecedent endogenous and exogenous effects;
- dynamic occupancy separates persistence, colonisation and imperfect detection;
- synchrony theory separates dispersal from correlated environmental forcing (Moran effect);
- passive-monitoring work shows that autocorrelated detections can bias occupancy inference;
- movement and occupancy studies show that sampling interval can change inferred ecological states;
- dimensionless scaling has successfully united very different patchy ecological systems.

Therefore none of those pieces alone is claimed as new.

The novelty candidate to test is their **cross-system unification as a predictive-memory source regime map**, including the observation process as a first-class source of apparent memory.

## Scale formulation

Let the observation interval be (Delta t), and let typical inter-patch/site spacing be (d).

Define provisional scale ratios:

### Persistence number

[
Pi_P = 	au_P / Delta t
]

where (	au_P) is the characteristic persistence/dwell time of a local ecological state.

### Propagation number

[
Pi_G = ell_G(Delta t) / d
]

where (ell_G(Delta t)) is the characteristic movement/colonisation distance possible during one observation interval.

### Forcing coherence numbers

[
Pi_F^t = 	au_F / Delta t
]

and

[
Pi_F^s = ell_F / d
]

where (	au_F) and (ell_F) are the temporal persistence and spatial coherence scales of the dominant external forcing.

### Observation-memory number

[
Pi_O = 	au_O / Delta t
]

where (	au_O) is the characteristic persistence of observation state (activity/detectability/sensor condition). Detection probability (p) remains an additional observation-quality axis rather than being forced into the same ratio.

These definitions are provisional and must be stress-tested in known-truth simulations before being treated as estimands.

## Regime predictions

### Regime P — persistence-dominated memory

If:

[
Pi_P gg 1,quad Pi_G ll 1
]

then recent state should predict the future strongly even though little or no propagation occurs.

Expected signature:

- high same-site/state memory;
- weak directional neighbour-lag effect after same-site persistence;
- forecast gain from history without spatial spread.

### Regime F — forcing-dominated synchrony

If both forcing coherence ratios are large:

[
Pi_F^t gg 1,quad Pi_F^s gg 1
]

then multiple sites may change together without exchange among them.

Expected signature:

- cross-site synchrony;
- synchrony attenuates after common forcing is included;
- no directional propagation lag is required.

### Regime O — observation-dominated memory

If observation state persists and detection is imperfect:

[
Pi_O gg 1
]

especially with low/intermediate (p), then detections and nondetections can cluster even when latent ecological state is unchanged.

Expected signature:

- large difference between observed turnover and latent-state turnover;
- apparent unsupported appearances disappear after observation modelling;
- strong sensitivity to detection-window / sampling-interval choice.

### Regime G — propagation-dominated memory

Propagation is plausible only when movement/colonisation operates on the sampled scale:

[
Pi_G gtrsim 1
]

and a directional lagged neighbour signal remains after persistence, shared forcing and observation processes are controlled.

Expected signature:

- source-to-target temporal ordering;
- distance/connectivity-dependent lag;
- residual neighbour effect after local persistence;
- external forcing cannot reproduce the directional sequence.

## Strongest comparative prediction

The same ecological system can move among apparent regimes when (Delta t) changes.

Therefore a powerful test is **temporal re-binning** of high-frequency observations.

If the framework is correct:

- very short intervals relative to (	au_P) exaggerate persistence;
- intervals near movement/colonisation timescales expose propagation if it exists;
- coarse intervals erase short memory and can merge distinct processes;
- observation-induced memory changes predictably with the detection window.

The goal is not to choose the interval producing the strongest result. The interval series is itself the experiment.

## Cross-system study design

A publishable general-principle test should include independent systems spanning the regime space, rather than treating any one published dataset as the evidence base.

Minimum system classes:

- high-residence telemetry / biologging;
- passive acoustic or camera monitoring with imperfect detection;
- genuinely dispersive or recolonising patch system;
- spatially coherent externally forced system;
- ideally a non-animal system to test taxonomic generality.

For each system, estimate the same objects:

1. forecast gain from lagged history beyond contemporaneous environment;
2. same-site persistence contribution;
3. shared-forcing contribution;
4. observation-process contribution;
5. residual directional propagation contribution;
6. how all five change under temporal re-binning.

## Primary falsifiable claims

### G1 — predictive memory without propagation exists

Systems with high persistence and low movement can show strong history-based forecast gain.

### G2 — propagation requires directional residual information

A history signal is not classified as propagation unless directional neighbour information remains after persistence, forcing and observation are controlled.

### G3 — apparent memory source changes with scale

Changing (Delta t) shifts systems across predicted regimes in accordance with process timescales.

### G4 — cross-taxon similarity follows scale ratios better than taxonomy

Systems that are taxonomically unrelated but occupy similar ((Pi_P,Pi_G,Pi_F,Pi_O)) regions should show similar memory decompositions.

This is the strongest general-ecology target.

## What would falsify the programme

The framework fails as a useful general principle if:

- decomposition is unstable to reasonable model families;
- scale ratios do not predict which source dominates;
- re-binning changes inferred regimes idiosyncratically rather than systematically;
- taxonomy/system identity explains the decomposition substantially better than the scale ratios;
- propagation cannot be distinguished even in known-truth systems designed to contain it.

## Publication boundary

A single re-analysis of the seed dataset is **not sufficient for the main claim**.

The seed dataset can appear as:

- motivation;
- one anchor point in a cross-system regime map;
- a mechanism-diagnostic example.

The paper-level result must come from known-truth falsification plus independent cross-system comparison.

## Role of Louisiana in the general programme

Louisiana is the **imperfect-detection / local-propagation-failure anchor**.

The six detection-source local worlds all failed, while a small history-dependent predictive signal remained. This makes the system useful for testing whether apparent spatial turnover can arise from latent persistence plus observation error rather than movement.

Its role is to anchor the observation/persistence corner of the general regime map, not to become a second analysis of the original King Rail paper.

The strongest next independent test is across additional monitoring systems or species whose temporal response sequences were not used to generate the hypothesis.
