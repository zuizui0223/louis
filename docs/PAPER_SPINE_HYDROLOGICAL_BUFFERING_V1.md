# Paper spine v1 — hydrological buffering by realised microhabitat use

## Working title

**Resident King Rails buffer experienced hydrological variation within coastal marsh home ranges**

Alternative conservative title:

**King Rails decouple experienced water depth from local hydrological variation**

The second title is preferred until a verified coordinate-to-event join supports an explicit geographic movement mechanism.

## One-sentence result

> **Within ten resident King Rails, repeated used microhabitats varied far less in water depth through time than event-matched local availability, and only about one-sixth of temporal variation in nearby available water depth was transmitted into used water depth.**

## Ecological question

Habitat-selection studies usually ask:

> which habitat states are used more than available?

This paper asks a different temporal question:

> **when local hydrological conditions change, how strongly is that change transmitted into the environmental state actually experienced by a resident animal?**

That separates static preference from **environmental buffering through realised space use**.

## Biological setting

Western Lake Erie King Rails occupy relatively small breeding-season home ranges in managed coastal marshes.

The source study already established:

- third-order microhabitat selection;
- importance of vegetation structure;
- frequent use of shallow water, approximately 6–17 cm;
- management relevance of within-marsh water depth.

Those are provenance, not the new result.

The new analysis uses the event-matched design already embedded in the source data:

- one used/homing microhabitat plot;
- nearby random availability plots measured at the same event;
- repeated through the breeding season;
- ten individual birds as the biological replication level.

## Result 1 — repeated used state is unusually stable

After source-defined QC:

- 190 valid matched events;
- 10 birds;
- 173 events retain both random plots.

Primary State Retention Index:

~~~text
SRI_i
= 1 - Var(used depth through time)
      / median Var(event-matched random pseudo-trajectory)
~~~

Result:

- 10/10 birds SRI > 0;
- median SRI = **0.886**;
- range = **0.402–0.976**;
- sign test p = **0.00098**.

Strict two-random sensitivity:

- 10/10 positive;
- median SRI = **0.882**.

### Interpretation

King Rails did not merely use shallower habitat on average.

Each individual's **sequence** of used water depths was substantially more stable than sequences generated from habitat that was locally available at those same sampling events.

## Result 2 — the result is temporal, not just low variance

Order events within each bird by year and Julian date.

Compare:

~~~text
mean |U_t - U_(t-1)|
versus
matched-random pseudo-trajectories
~~~

Result:

- 10/10 birds positive temporal retention;
- median = **0.658**;
- range = **0.388–0.879**;
- sign test p = **0.00098**;
- 10/10 birds individually p < 0.05.

Strict two-random subset:

- median = **0.667**;
- 10/10 positive.

### Interpretation

The used trajectory is not only narrowly distributed. It is **temporally smooth** relative to what was locally available.

## Result 3 — local hydrological variation is strongly damped

For event t:

~~~text
A_t = mean water depth of local matched random plots
U_t = used water depth
~~~

Estimate within-bird coupling of U on A.

Primary result:

- pooled observed slope = **0.162**;
- pseudo-used null median = **1.001**;
- coupling reduction = **83.8%**;
- pooled Monte Carlo p < **5e-5**;
- 10/10 birds below their own null median;
- 10/10 individual p < 0.05.

Flooded-only sensitivities:

- remove dry random points: slope **0.145**, reduction **85.5%**;
- require all retained points flooded: slope **0.180**, reduction **82.0%**.

### Interpretation

The result is not simply “birds choose water instead of dry ground.”

As nearby water depth changed, the water depth actually used changed much less.

A concise description is:

> **realised microhabitat use buffered about four-fifths of local hydrological variation.**

Use “about four-fifths” descriptively; do not imply a mechanistic transmission coefficient outside this matched design.

## Result 4 — buffering is strong but not unlimited

Post-hoc mechanism decomposition asks whether buffering persists when local availability is unusually different from each bird's normal hydrological context.

Define extreme events independently within each bird as the top quartile of availability mismatch.

Results:

- pooled mismatch-to-used-deviation coupling reduction = **84.5%**;
- 10/10 birds had slopes below their pseudo-null median;
- 9/10 birds retained positive buffering during extreme events;
- median extreme retention = **0.629**;
- 7/10 birds individually p < 0.05.

One bird showed negative extreme retention and several showed weaker buffering.

### Interpretation

The data support a **buffering capacity**, not perfect hydrological homeostasis.

This provides a natural transition to the broader ecological prediction:

> when locally reachable suitable states no longer compensate for environmental change, broader relocation should become more likely.

The South Carolina King Rail system is a published boundary example, not yet a direct replication of this matched-availability metric.

## What the paper does not claim

### Not ordinary habitat selection

The source paper already established habitat associations.

The new result concerns **temporal dampening relative to time-matched local availability**.

### Not a monitoring-method paper

The biological response is the environmental state experienced by individual birds.

### Not yet “movement causes buffering”

The archive contains UTM coordinate files, but they lack a verified event/date key linking each coordinate row to CART homing-event IDs.

Therefore do not claim:

> measured geographic displacement caused hydrological buffering.

Current supported wording:

> **repeated realised microhabitat use buffers experienced hydrological variation.**

### Not a universal niche-tracking concept claim

Movement ecology already connects movement to environmental conditions, and niche/resource tracking is established.

The novelty target is the **within-home-range, individual-level, time-matched availability quantification**.

## General ecological implication

For a resident organism in a dynamic habitat mosaic, residency does not require accepting temporal environmental variation passively.

An animal may remain within a familiar broader area while repeatedly selecting local states that make its **experienced environment more stable than the environment around it**.

That generates a concrete conservation prediction:

> maintaining a spatial portfolio of shallow-water states within a marsh can allow residency to persist through hydrological fluctuation; when that portfolio fails, relocation pressure should rise.

The portfolio statement is a prediction from the result, not yet directly measured as retained suitable area.

## Evidence classes

### Independent developmental primary evidence

Lake Erie SRI and temporal-retention analysis.

The dataset is independent of the Southwest Louisiana EOG seed.

### Post-hoc mechanism decomposition

Availability coupling and buffering-limit analyses on the same Lake Erie dataset.

### External biological context

- South Carolina King Rail seasonal relocation;
- Godwit and other dynamic-wetland tracking systems.

These do not count as independent replication of SRI unless the same availability-relative estimand is calculated.

## Manuscript order

1. **Introduction**
   - dynamic wetland habitat;
   - distinction between habitat preference and temporal environmental buffering;
   - prediction: used-state trajectory varies less than time-matched local availability.

2. **Methods**
   - independent Lake Erie dataset;
   - source-defined QC;
   - individual as replication unit;
   - matched pseudo-trajectories;
   - SRI;
   - successive-state retention;
   - availability-coupling decomposition.

3. **Results**
   - SRI;
   - temporal retention;
   - coupling reduction;
   - flooded-habitat robustness;
   - buffering-limit decomposition.

4. **Discussion**
   - hydrological buffering within resident home ranges;
   - distinction from static selection;
   - individual limits;
   - predicted transition to broad relocation;
   - management value of within-marsh hydrological heterogeneity.

## Stop rule

The paper spine is sufficiently closed for drafting.

Do not add another Lake Erie post-hoc metric unless it answers one of these explicit unresolved questions:

1. verified geographic movement-event linkage;
2. independent replication of the same availability-relative estimand;
3. a response-independent full dynamic habitat surface that directly estimates local portfolio failure.
