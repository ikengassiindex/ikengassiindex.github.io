# RESULT — the cost model counts SELECTORS, not delivered fields

**Measured** 21 September 2026 · `reanalysis-era5-pressure-levels` · priced
server-side, nothing queued.

`LEAD_era5_carries_a_real_uncertainty.md` recorded an unresolved anomaly:
`ensemble_members` priced identically to `reanalysis`, when ten members should
be ten times the fields. It said nothing should be designed on top of it until
it was resolved. It is now resolved, and the answer is worse than the anomaly.

## Measured

One day, 2024-01-01, `reanalysis`, varying the deterministic knobs:

    1 time  x 1 level  x 1 variable      cost   1.0
    1 time  x 3 levels x 1 variable      cost   3.0
    4 times x 3 levels x 2 variables     cost  24.0

One day, identical selectors, varying only `product_type`:

    reanalysis                           cost  24.0
    ensemble_mean                        cost  24.0
    ensemble_spread                      cost  24.0
    ensemble_members                     cost  24.0

And 3-hourly, the EDA's native timestep:

    ensemble_members, 8 times            cost  48.0

## What it means

**Cost = the number of SELECTOR COMBINATIONS** — days × times × variables ×
levels — and nothing else. It is a count of what you asked for, not a measure
of what will be delivered.

For `reanalysis`, `ensemble_mean` and `ensemble_spread` these coincide, because
each combination returns exactly one field. For **`ensemble_members` they do
not**: ECMWF's ensemble is a **10-member** system, so each combination returns
ten fields. The same request delivers **ten times the data at one times the
price**.

The estate's working rule — established on the fire leg as *cost = variables ×
days* and generalised on the winter leg to *cost = fields* — was right about
the arithmetic and **wrong about the referent**. It should read *cost =
selector combinations*, with the note that this equals fields only where one
combination yields one field.

## Why this is the dangerous direction

The estate has been using the cost limit as a proxy for "is this request
sane?". It is not one. A limit that does not rise when the payload rises
tenfold provides no protection at exactly the moment protection is wanted: the
6-year pressure-level window that prices at 52,608 against a 60,000 limit
would, as `ensemble_members`, still price at 52,608 and deliver on the order of
ten times the volume — a leg already estimated near 1–2 TB.

Nothing has been queued, so nothing has gone wrong. But the discipline that has
served the estate three times — *price it before you queue it* — does not by
itself catch this, and it has just been demonstrated that it would not have.

## The corrected rule, for any future fetch

1. `estimate_costs()` answers **"will the CDS accept this request?"**
2. It does **not** answer **"how much data will arrive?"**
3. Before any fetch, multiply the selector count by the fields-per-combination
   of the chosen `product_type` — 1 for `reanalysis`, `ensemble_mean` and
   `ensemble_spread`; **10** for `ensemble_members`.
4. Volume, not price, is the binding constraint on the winter leg, and volume
   is the quantity the cost probe does not report.
