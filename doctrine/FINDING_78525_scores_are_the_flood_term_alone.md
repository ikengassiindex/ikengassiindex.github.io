# FINDING — 78,525 published scores are the flood term alone

**Date** 24 September 2026
**Occasion** Scoping the component I rebuild. This population was not in the rebuild's blast-radius measurement, because that measurement ran on the records that have components.
**Measured on** the deployed tree, all 39 countries, 622,104 records — a census, not a sample.
**Status** measurement only. Nothing published was changed.

## What was found

```
records whose components dict is EMPTY — {}        78,525    12.6% of the estate
  R_base_median == 0.0                             78,525    100.0%
  R_median == add_sum, exactly                     78,525    100.0%
  carrying modifiers that were computed anyway      78,525    100.0%
  CI_width == 0.0                                  78,525    100.0%
```

Not a sparse components dict. An empty one. `compute_r_base` reads
`components.get(comp, 0)`, so `R_base` is zero; `soft_clip_upper(0 × mult_product)`
is zero; and

```
R_final = soft_clip_upper( R_base × Π mult_i ) + Σ ( add_j − 1 )
        = 0 + add_sum
```

**The published score is the R6c_flood additive term and nothing else.** The
full modifier chain — R3, R4, R6 family, R7, R8, R9, R10 — was computed for
every one of these records and then multiplied by nothing.

Twenty-eight jurisdictions:

```
poland      25,517     netherlands  3,810     estonia      1,180
austria     13,979     latvia       3,427     canada       1,107
czechia      7,825     denmark      2,389     ...and 16 more
belgium      5,432     slovenia     1,574
australia    4,487
lithuania    4,396
```

## The direction it fails in

```
published classification of those 78,525 records

  Low        48,478   61.7%
  Medium     23,143   29.5%
  High        3,576    4.6%
  Critical    3,314    4.2%
  Extreme        14    0.0%
```

**48,478 substations are published as Low risk because nothing was measured for
them.** Prohibition §7.5 — *"No silent absence. A required field with no content
renders as a named blocking gap. Absence that reads as completeness is the
failure mode that cost this estate five months."* This is that failure in its
purest form, and it points in the direction that tells a reader the asset is
fine.

The index exists to support decisions about where infrastructure is least
resilient. An asset with no measurement is currently indistinguishable, to any
reader, from an asset measured and found safe.

## Absence published as certainty

```
                        empty components        records with components
  CI_width == 0.0            100.0%              median 0.1258
  R_P5 == R_median == R_P95  every record        p10 0.1008  p90 0.1578
  confidence_tier            None, 100.0%        medium 90.0% · high 9.2% · low 0.8%
```

The Monte Carlo has nothing to perturb, so the interval collapses to a point and
`CI_width` is published as exactly zero. A zero-width confidence interval is a
claim of perfect certainty. **The emptier the record, the more certain its
published interval appears.**

`confidence_tier` is absent rather than falsely high, which is Convention #56
working correctly on one field while the field beside it publishes a number.

## A second, separate defect surfaced here

`classification` matches a straight banding of the record's own `R_median` on
**52,252 of 78,525 — 66.5 per cent**. On the other 26,273 the published
classification comes from some other path; these records carry
`_band_absolute` and `_band_norm_R_P95` and the normalised route has not been
traced. Recorded as a separate item and NOT diagnosed here, because a second
diagnosis attached to a first is how a finding acquires a conclusion nobody
measured.

## What the component I rebuild does for them

Every one of the 78,525 already carries `_I_from_metrics`. Rebuilding component
I alone — the other five components left absent, `R_base = 0.25 × _I_from_metrics`
— on a consistent basis (banding `R_median` on the declared `BANDS` both before
and after):

```
band        published    rebuilt     change
Low            65,466     20,298     −45,168
Medium         13,059     58,087     +45,028
High                0        140        +140
Critical            0          0          +0

  45,272 records change band       57.7%
  mean R_median shift   +0.1378    median +0.1377    max +0.3760
```

So for an eighth of the estate the rebuild is not a correction of a hash. It is
**the difference between a score and no score at all**, and it moves 45,168
substations out of Low.

## Why this was not seen before

`FINDING_what_the_components_fill_costs.md` measured the rebuild at 89,056 band
changes across 543,546 records. That measurement ran on the records that carry
`components.I`. These 78,525 have no components to compare against, so they fell
outside its population entirely and contributed nothing to its number. The
rebuild's true reach is that finding's 89,056 **plus** these 45,272, on
populations that do not overlap.

It is the tenth instance recorded in this estate of a measurement whose stated
population quietly excluded the cases that mattered most — and the first where
the excluded population was larger in consequence than the one measured.

## What follows

This finding decides nothing and proposes nothing. It exists because the case
for rebuilding component I rested on replacing a name hash, and that was the
smaller half of the case.

Nothing here was changed. The rebuild, when it runs, will alter these records,
so the measurement is recorded first.

## Related

- `FINDING_what_the_components_fill_costs.md`
- `FINDING_the_chain_is_closed_and_the_residual_moved.md`
- `FINDING_the_name_hash_reaches_past_components.md`
- `FINDING_the_index_declares_1097_sources_and_fetches_231.md`
