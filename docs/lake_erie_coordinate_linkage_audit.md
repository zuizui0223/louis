# Lake Erie coordinate-to-event linkage audit

## Question

The Lake Erie archive contains two useful layers:

1. matched microhabitat rows with explicit Homing/Random event IDs;
2. individual UTM coordinate CSVs used for home-range estimation.

Can these be joined strongly enough to claim:

> geographic movement helped maintain a stable environmental state?

## Audit result

The answer is currently **no**.

### Clean cases

Two birds have a completely explicit archive-count structure:

- `332_21`: coordinate rows = 17; Homing events = 1…17;
- `871_21`: coordinate rows = 15; Homing events = 1…15.

### Suggestive but incomplete cases

For several birds, coordinate row count equals the maximum Homing event number, but the CART table begins after event 1 or omits some numbered events. This is compatible with row number representing the tracking-event sequence, but the coordinate files themselves contain no event/date key.

### Problematic source structure

Examples include:

- `020_21`: 36 coordinate rows and 36 Homing records, but Homing numbering reaches 37 with event 6 absent;
- `881_20`: 19 coordinate rows but parsed Homing numbering does not provide a one-to-one 1…N sequence;
- malformed source Homing IDs include `164.881H_20` and `164856H11_20`;
- another CART row carries a year-suffix inconsistency for a 390 event.

These source irregularities are not repaired post hoc.

## Decision

> **Do not join UTM coordinate rows to microhabitat events by row order.**

The supported Lake Erie result therefore remains:

> repeated used water-depth states are temporally smoother than event-matched local availability.

The stronger movement-mechanism statement remains unresolved:

> geographic displacement itself enables that environmental-state retention.

## What would unlock the stronger test

Any one of the following is sufficient:

- an original event-keyed telemetry table;
- source documentation explicitly stating that coordinate CSV row n is Homing event n;
- a dated coordinate table allowing independent join to Julian/year;
- author-provided mapping from coordinate rows to Homing IDs.

Until then, geographic movement is biological context, not a fitted causal/mechanistic variable.
