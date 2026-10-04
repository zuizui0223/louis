# Final figure plan — Louisiana hydrological-buffering manuscript

## Figure 1 — From static habitat selection to temporal environmental buffering

### Panel A — Source design
Schematic of one repeated homing event:

~~~text
random plot 1      USED point      random plot 2
      \               |               /
       ---- same event / <=72 h ----
~~~

Annotate:
- 10 birds;
- 190 valid matched events;
- local water-depth measurements.

### Panel B — Temporal question
Contrast:

~~~text
ordinary habitat selection:
used state vs available state at one time

this study:
trajectory of used states through time
vs
time-matched available pseudo-trajectories
~~~

Message:
> the response is temporal variation in experienced state, not preference alone.

Do not put EOG in the main figure.

---

## Figure 2 — Individual state retention

### Panel A
Plot individual SRI for all 10 birds.

Reference line:
- SRI = 0.

Show:
- median = 0.886;
- 10/10 positive.

### Panel B
Time-ordered successive-state retention for the same birds.

Show:
- median = 0.658;
- 10/10 positive.

Preferred visual:
- paired individual dots connected between variance retention and temporal retention;
or
- two aligned dot/interval panels.

Avoid treating 190 events as independent replicates.

---

## Figure 3 — Hydrological coupling

### Panel A
Observed within-bird used-on-availability slope versus matched pseudo-used null.

Headline values:
- observed = 0.162;
- null = 1.001.

A slope schematic can show:

~~~text
local availability changes strongly
used state changes weakly
~~~

### Panel B
Coupling reduction across three analyses:

- primary: 83.8%;
- flooded-random only: 85.5%;
- all points flooded: 82.0%.

Message:
> the effect is quantitative within flooded habitat, not merely wet-versus-dry selection.

### Panel C
Individual observed slope / null-median slope for 10 birds.

Show all individuals to make cross-individual consistency visible.

---

## Figure 4 — Buffering has limits

For each bird, plot:

- x: within-bird top-quartile availability mismatch threshold or mean extreme mismatch;
- y: extreme retention.

Reference:
- retention = 0.

Headline:
- 9/10 positive;
- median = 0.629.

Do not infer a universal relocation threshold.

Message:
> local buffering is strong but finite and heterogeneous.

---

## Figure 5 — Ecological boundary/context

Optional main or supplementary conceptual figure:

~~~text
local suitable state remains reachable
        ↓
within-home-range hydrological buffering
        ↓
local compensation fails
        ↓
broader home-range relocation
~~~

Place South Carolina 2026 as external biological context:
- 5/9 seasonal home-range shifts;
- mean 2.9 km, range 0.7–7.5 km.

Label clearly:
> external context, not replication of SRI.

---

## Supplementary figures

S1. QC/sample flow from 607 source rows to 190 matched events.

S2. Per-bird null distributions for SRI.

S3. Strict two-random sensitivity.

S4. Flooded-only sensitivities.

S5. Coordinate-linkage audit showing why row-order joins are prohibited.

S6. Individual buffering-limit diagnostics.

## Numeric rule

All figure numbers must come from:

- `manuscript/MANUSCRIPT_NUMERIC_CONTRACT_V1.json`

or a generated figure-data contract derived from the canonical result JSONs.

Do not manually retype rounded values into plotting code.
