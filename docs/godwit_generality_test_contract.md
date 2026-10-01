# Godwit external-generality test contract

## Role

This is **not** the primary Louisiana/King Rail test.

It asks whether the broader idea of environmental-state continuity during movement is visible in an independent wetland bird with fully open GPS and seasonal habitat data.

Source:
- Craft et al. 2025, *Journal of Applied Ecology*
- DOI 10.1111/1365-2664.14827
- Dryad DOI 10.5061/dryad.4tmpg4fm3

The Dryad release contains:
- `location_data.csv`: timestamp, longitude, latitude, individual ID;
- `habitat_use_df.csv`: bird, land-cover class, percent of seasonal core area, wet/dry season;
- wet- and dry-season AKDE objects;
- analysis scripts. 

## Question

> **When an individual shifts geographically between wet and dry seasons, does it preserve a similar broad habitat composition, or does it also move through habitat-state space?**

## Frozen quantities

For birds represented in both seasons:

1. wet-season GPS centroid;
2. dry-season GPS centroid;
3. great-circle centroid displacement;
4. wet-season habitat-composition vector;
5. dry-season habitat-composition vector;
6. Bray-Curtis wet/dry habitat dissimilarity.

## Individual-continuity null

Compare each bird's own wet-to-dry habitat dissimilarity with a permutation null that pairs its wet-season vector to another bird's dry-season vector.

### Compatible with environmental-state continuity

Own seasonal pairs are more similar than cross-individual seasonal pairs.

### Opposite result

Own wet/dry composition changes as much as or more than cross-individual pairings.

That means geographic movement is accompanied by broad habitat-state change and supports **seasonal resource tracking**, not a strict stay-in-state mechanism.

## Secondary relation

Calculate the rank association between:

```text
seasonal geographic centroid shift
and
seasonal habitat-composition dissimilarity
```

Do not assign a directional significance rule in advance because both plausible ecological strategies are informative:

- large movement + small state change -> state fidelity;
- large movement + large state change -> habitat-state replacement.

## Boundary

The Godwit dataset does **not** contain the same event-matched local-availability structure as Lake Erie King Rail.

Therefore:

- it cannot estimate SRI;
- it cannot validate within-home-range micro-niche tracking directly;
- it is an external generality/falsification system only.

The primary Louisiana claim still requires the King Rail matched-event design or another equivalently strong individual availability design.
