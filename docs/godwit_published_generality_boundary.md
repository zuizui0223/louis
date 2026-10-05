# Godwit published-generality boundary

## Role

This is external biological context for the Louisiana King Rail result. It is not a replication of the Lake Erie matched-availability SRI.

Source:

- Craft et al. (2025), *Journal of Applied Ecology*, DOI 10.1111/1365-2664.14827
- Dryad DOI 10.5061/dryad.4tmpg4fm3

## Published result

The source study followed 22 GPS-tagged Black-tailed Godwits in the Senegal Delta.

Its broad seasonal result is explicitly **habitat replacement**, not strict habitat-state continuity:

- during the wet season, birds used natural wetlands and newly planted rice fields;
- as rice matured, birds shifted toward more recently sown rice fields;
- later, as floodwaters receded and rice fields dried, birds abandoned rice fields and shifted toward natural wetlands, especially protected marshes and shallow floodplains.

Thus large seasonal movement in this system is accompanied by a change in broad habitat composition.

## Consequence for Louisiana

The Louisiana result should not be generalized as:

> animals move in order to keep the same environment.

A better general statement is:

> **movement can regulate some experienced environmental dimensions at some spatial and temporal scales, while other systems use movement to replace habitat state as resource phenology changes.**

Lake Erie King Rails provide a fine-scale example of hydrological-state buffering within resident home ranges.

The Senegal Delta Godwits provide a useful opposite boundary: broad seasonal resource tracking with habitat-state replacement.

This contrast makes the ecological question sharper:

> **When does movement stabilize an experienced environmental state, and when does it track a changing resource state instead?**

## Individual-level test status

The frozen individual-level Dryad analysis in `analysis/07_godwit_seasonal_state_displacement.py` remains scientifically valid: it compares each bird's own wet-to-dry habitat composition with cross-individual seasonal pairings.

However, repeated GitHub Actions retrieval attempts on 2026-10-05 returned HTTP 403 for the Dryad file-stream downloads. Current Dryad tooling/documentation indicates that binary file/archive downloads can require an authenticated session even when public metadata remain anonymously queryable.

Therefore:

- the individual permutation result is **not available** from the current anonymous execution route;
- it is not inferred from the published group-level result;
- the repository does not keep rerunning or redesigning the Godwit analysis to rescue this optional external panel;
- the published habitat-replacement result remains a legitimate ecological boundary, not an SRI replication.

If the two CSVs later become available through an authenticated or author-provided public mirror, the already-frozen analysis may be run without changing its estimand.

## Claim boundary

Do not call Godwit a replication of King Rail SRI.

Do not use the published seasonal habitat shift to infer the fine-scale water-depth state experienced by individual Godwits.

The useful conclusion is scale/state dependence of environmental tracking, not universal state fidelity.
