# California waterfowl scale-tracking preflight — v1

## Role

External generality test for the Louisiana King Rail programme.

Source:
- USGS data release DOI 10.5066/P922KDU6
- USGS OFR 2020-1102, DOI 10.3133/ofr20201102

The release combines GPS telemetry with dynamic flooded/open-water habitat products and explicitly includes movement distance from primary roosts to night feeding locations.

## Biological question

Lake Erie King Rails show local hydrological buffering inside a resident home range.

The stronger general prediction is:

> **movement scale should increase when a preferred flooded state becomes less available locally.**

This is not the same as asking whether drought years have longer movements on average.

## Required data gate

Proceed to an individual-level test only if the public release exposes, on a common key or reconstructable time unit:

1. individual bird identifier;
2. primary roost location or identity;
3. night-feeding location or roost-to-feeding distance;
4. date / 16–18 day habitat-map interval;
5. dynamic flooded-habitat availability around the primary roost;
6. species or analysis stratum sufficient to avoid silently pooling incompatible movement regimes.

If individual identity and dynamic local flooded availability cannot be linked, stop at published-context status.

## Frozen availability quantity

If the data gate passes, define local suitable-state availability before inspecting the movement-distance association as:

- primary: flooded/open-water habitat area within a fixed biologically justified radius around the primary roost for the matching dynamic-water interval;
- secondary: distance from the primary roost to the nearest mapped flooded habitat patch above the source-defined minimum patch size, only if the release provides enough geometry to compute it without tuning the patch threshold against bird movement.

Do not choose the radius, patch threshold or temporal lag by optimizing the movement response.

## Primary prediction

For repeated observations within birds:

```
log1p(roost_to_feeding_distance_km)
  ~ local_flooded_habitat_availability
  + season/date
  + hydrologic_region
  + individual effect
```

Expected sign:

> lower local flooded-habitat availability -> larger movement distance.

If a nearest-suitable-state distance is independently computable, the stronger prediction is:

```
movement_distance
  increases with
distance_to_nearest_currently_suitable_state
```

## Relation to Lake Erie

A supported result would not replicate the King Rail SRI.

It would connect two movement scales:

- Lake Erie: suitable hydrological states remain reachable locally -> experienced-state buffering within the home range;
- California: local flooded habitat becomes spatially constrained -> larger commuting / relocation scale.

Together they would support a scale-dependent environmental-tracking principle.

## Falsification

The hypothesis weakens if, after individual/season/region structure is represented:

- movement distance is unrelated to local flooded-habitat availability with useful precision; or
- movement becomes shorter as local suitable habitat declines without a separately supported mechanism.

Do not reinterpret any drought-year difference as support unless the local availability quantity itself is linked to the movement observation.

## Current source status

The USGS landing page confirms:
- high-resolution GPS telemetry;
- dynamic open-water maps;
- changing flooded habitat under drought/water management;
- movement distance from primary roosts to night feeding locations;
- public CC0 data release.

The exact child-file schema needed for the individual-level join has not yet been recovered through the current access route.

Status:

**SOURCE_RELEVANT / INDIVIDUAL_LINKAGE_NOT_YET_VERIFIED**

Do not report a new California effect size until the gate above passes.
