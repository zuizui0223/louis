# Submission QC — Louisiana hydrological-buffering manuscript

## Current status

The biological story is frozen around one primary claim:

> **Resident King Rails experience substantially less temporal water-depth variation than is present in time-matched local habitat availability.**

This is an individual-level environmental-buffering result.

It is **not** a demonstrated geographic movement mechanism because the public coordinate files cannot yet be joined unambiguously to matched microhabitat events.

## Canonical manuscript

Use:

- `manuscript/LOUIS_HYDROLOGICAL_BUFFERING_MANUSCRIPT_V1.md`

## Numeric source of truth

Use:

- `manuscript/MANUSCRIPT_NUMERIC_CONTRACT_V2.json`

Canonical result sources:

- `results/lake_erie_state_fidelity_v1.json`
- `results/lake_erie_availability_coupling_v1.json`
- `results/lake_erie_flooded_availability_sensitivity_v1.json`
- `results/lake_erie_buffering_limits_v1.json`
- `results/lake_erie_local_heterogeneity_insurance_v1.json`

Do not copy numbers from exploratory notes.

## Automated manuscript QC

Run:

~~~bash
python validation/validate_manuscript_v1.py
~~~

The current manuscript passes the logical equivalent of this checker after repair of the LaTeX escape corruption.

The validator fails on:

- hidden C0/control characters;
- broken LaTeX commands;
- EOG appearing in the biological manuscript;
- drift in source sample-flow counts;
- drift in primary SRI/temporal/coupling values;
- missing coordinate-linkage boundary;
- forbidden causal/absolute claims.

## Figure-data reproducibility

The primary result summaries are canonical, but individual SRI/coupling rows are generated only by rerunning the public-data analyses.

The reproducible path is:

~~~text
analysis/08_lake_erie_standardize.py
 -> analysis/09_lake_erie_state_fidelity.py
 -> analysis/12_lake_erie_availability_coupling.py
 -> analysis/13_lake_erie_buffering_limits.py
 -> analysis/15_lake_erie_local_heterogeneity_insurance.py
 -> analysis/14_build_manuscript_figure_data.py
~~~

GitHub Actions workflow:

- `.github/workflows/manuscript-figure-data.yml`

The materializer fails if rerun aggregate values drift from the manuscript numeric contract.

## Submission-stopping scientific rules

Do not submit if the manuscript says or implies:

1. **measured geographic displacement caused the buffering**  
   The coordinate-to-event join remains unresolved.

2. **birds maintained one fixed target depth**  
   The result is relative temporal dampening, not zero variance.

3. **84% of physiological stress was removed**  
   83.8% is a reduction in the used-on-available water-depth slope relative to the matched pseudo-used null.

4. **habitat heterogeneity was demonstrated to prevent emigration**  
   The new matched mechanism decomposition supports heterogeneity as a local buffering opportunity relative to pseudo-use, but it does not measure emigration prevention or geographic movement causation.

5. **a universal relocation threshold was identified**  
   Extreme-condition analysis shows finite/heterogeneous buffering only.

6. **the South Carolina or Godwit systems replicate SRI**  
   They are external biological context/generality systems with different estimands.

## Main-text hierarchy

Keep the evidence hierarchy explicit:

### Primary independent result
- SRI;
- time-ordered state retention.

### Mechanistic decomposition / robustness on the same data
- availability coupling;
- flooded-only sensitivities;
- buffering-limit analysis;
- local hydrological heterogeneity / state-portfolio decomposition (**post-hoc; not independent replication**).

### External context
- South Carolina King Rail relocation;
- Godwit / other wetland tracking systems.

Do not count post-hoc decompositions as independent replications.

## Manual checks before submission

1. replace author/affiliation/contribution/acknowledgement placeholders;
2. select target journal and apply its section/reference style;
3. verify Brewer et al. source ethics wording and reuse only the source-study approval information;
4. generate final figures only from canonical figure-data outputs;
5. verify Zenodo and code-repository accession wording;
6. archive a submission release/tag;
7. decide whether South Carolina context belongs in main Discussion or Supplement;
8. proof all references against publisher records.

## Title boundary

Current title:

> **King Rails decouple experienced water depth from local hydrological variation**

This is supported by the availability-coupling result.

Avoid stronger titles using:
- movement causes;
- hydrological homeostasis;
- optimal tracking;
- resilience threshold.

