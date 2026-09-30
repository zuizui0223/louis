# Phase 0 ecological interpretation

## Bottom line

The strongest ecological reading of the Louisiana EOG result is **not** that
King Rails require long-distance movement or that local spatial dynamics failed.

The post-EOG diagnostics show:

> **the original local-world falsification was dominated by source
> initialization, while later detections were overwhelmingly compatible with
> persistent/cumulative site history.**

This shifts the next ecological question from "how far do birds propagate?" to:

> **what ecological or observation process gives marsh-bird site use a memory
> longer than one sampling occasion?**

## 1. What EOG originally showed

EOG reported two facts on the King Rail endpoint:

1. the Layer-B summary improved heldout macro log loss only slightly
   (0.2463173 -> 0.2453455; about 0.39%, 7/8 heldout occasions);
2. all six local detection-source worlds were eventually falsified, leaving
   only the conservative `external_open` world.

Those facts are both true under the frozen EOG contract. Their ecological
interpretation changes after inspecting *why* the worlds failed.

## 2. Event-level anatomy of the local-world failures

Across the 20 occasions there were 34 observed positive site-occasion events:

- **18** same-site continuations;
- **9** same-site returns after a detection gap;
- **6** first detections near a previously positive site;
- **1** first detection outside prior observed support.

All six local worlds first failed on the **same event**:

- sample period 5;
- site J07;
- the first observed positive in the whole sequence;
- no earlier observed positive site existed to act as a source.

Thus the headline "all six local worlds were falsified" is primarily a
statement about an **empty observed-source initialization**.

It is not evidence that the first bird moved from nowhere or that later birds
must have crossed >17 km.

## 3. What happens once the first observed source exists

After that first positive, 33 positive events remained.

Of those:

- **27/33 = 81.8%** occurred at sites that had already been detected positive;
- **9** were returns after at least one detection gap;
- only **6** were first detections at new sites.

Support failures after initialization:

| world | later unsupported positives |
|---|---:|
| ~2.73 km immediate | 13 |
| ~2.73 km cumulative | 4 |
| ~2.98 km immediate | 13 |
| ~2.98 km cumulative | 4 |
| ~17.01 km immediate | 5 |
| ~17.01 km cumulative | **0** |

The broad cumulative-history world supports **every later positive**.

This result is much more informative than the original all-world-falsified
headline.

## 4. Ecological interpretation

Three features matter.

### A. Initial state is latent

Before the first call is detected, the ecological system is not literally
empty. Treating "not yet detected" as "not a possible source" creates an
artificial origin problem.

### B. Memory lasts longer than one occasion

At every spatial scale, cumulative observed history supports more later
positives than immediate-previous history.

The difference in unsupported later positives is:

- 9 events at ~2.73 km;
- 9 events at ~2.98 km;
- 5 events at ~17.01 km.

So the relevant memory is not a one-step propagation memory.

### C. Persistence dominates the positive sequence

The large majority of later positives occur at sites with prior detections, and
nine positives reappear after a detection gap.

This pattern is compatible with persistent latent site use plus intermittent
detection. It is also compatible with longer-lived habitat/site memory. It is
not by itself proof of either.

## 5. What happened to the occupancy/detection decomposition

Two same-data attempts were made deliberately as diagnostics.

### Visit-level dynamic occupancy

The dynamic model had a large numerical heldout advantage but multiple
parameters hit optimization bounds. It was declared non-identifiable.

### Four-visit robust-design occupancy

Grouping the 20 surveys into five four-visit primary periods reduced some of
the confounding but did **not** solve identification.

The fitted dynamic model again hit bounds:

- initial occupancy intercept at the lower bound;
- persistence logit at the upper bound;
- implied persistence approximately **0.9997**.

Its numerical heldout log loss was lower (0.241 vs 0.550), but because the
parameters are on the boundary that gain is **not interpreted as mechanistic
evidence**.

The same modelling family has now failed its identifiability gate twice. No
further tuning of this dataset is justified.

## 6. Next ecological hypotheses

The same-data evidence supports a narrower prospective hypothesis family.

### H-L1 — persistent latent site use + imperfect detection

Sites remain used across multiple occasions, while acoustic detection blinks on
and off.

Expected signature in an independent repeated-detection system:

- high latent persistence;
- many raw gap-return events;
- apparent observed-source propagation failures that disappear when latent
  state replaces raw detection as the source.

### H-L2 — stable habitat memory

Sites repeatedly become positive because stable marsh/salinity conditions keep
them suitable.

Expected signature:

- long-term site history adds little after sufficiently resolved habitat state;
- persistence varies systematically along habitat/salinity specialization.

### H-L3 — true directional propagation

A local neighbour state genuinely changes the probability of later site use.

This hypothesis is allowed only if, after detection and same-site persistence
are separated, a lagged neighbouring **latent** state still predicts new site
use.

The current King Rail sequence does not establish H-L3.

## 7. Next validation target

Do not fit another increasingly flexible King Rail model.

Instead test the prediction generated by this failure mode in a fresh or
response-frozen repeated-monitoring system:

> **When detection is imperfect, using observed positives as spatial sources
> will systematically exaggerate turnover and can falsely suggest propagation
> failure; replacing observed sources with persistent latent state should reduce
> those apparent failures.**

Within the Louisiana programme, the ten non-King-Rail response sequences can be
used only after a fixed cross-species protocol is written before their detailed
temporal values are inspected. They are useful replication data, not licence
for outcome-driven species selection.

## 8. How to describe the EOG result in a paper

Use:

> The EOG analysis initially rejected all six local observed-source worlds.
> Event-level diagnosis showed that all six were first rejected by the first
> detected King Rail event, when no observed source yet existed. After
> initialization, 82% of positive events occurred at previously detected sites,
> and a 17-km cumulative-history representation accommodated every later
> positive. The anomaly therefore generated a new hypothesis: observed
> detection histories can create apparent spatial turnover when ecological site
> use is persistent but incompletely observed.

Do not use:

> EOG showed that King Rails move farther than 17 km.

or:

> EOG proved external immigration.

Neither follows from the data.
