# Analysis order

The King Rail response has already been opened in EOG, so same-King-Rail work is post-hoc mechanism diagnosis.

## Stage 1 — identify why the six local worlds failed

Run:

```bash
python analysis/01_failure_event_classification.py
```

The script opens only the already-consumed `KIRA.csv` response and classifies every positive event as:

1. same-site continuation;
2. same-site return after a detection gap;
3. first detection near prior positives;
4. first detection outside prior observed-source support.

It also reports which frozen immediate/cumulative local worlds fail on each event.

This directly determines whether the first explanation to test is imperfect detection/persistence or an open spatial process.

## Stage 2 — occupancy/detection decomposition

Use the model order in `hypothesis_registry.json`:

`M0 detection/habitat -> M1 same-site persistence -> M2 latent-neighbour -> M3 regional synchrony -> M4 open source`.

## Stage 3 — multi-species extension

Do not inspect the detailed temporal sequences of the remaining ten species until temporal endpoints and comparison rules are frozen. Published habitat associations are already known and are not blind.
