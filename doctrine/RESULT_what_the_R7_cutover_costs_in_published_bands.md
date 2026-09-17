# RESULT — what the R7 cutover costs, in the bands the site publishes

**Date** 17 September 2026
**Instrument** `scripts/measure_r7_cutover_cost.py` (new, read-only).
**Measured on** the deployed tree, all 39 countries, 622,104 records, every shard.
**Status** measurement only. Nothing written.
**Supersedes the band arithmetic of** `RESULT_what_completing_the_R7_cutover_costs.md`.

---

## Why the earlier figure is withdrawn

That document reported 31,726 band changes, 5.1 per cent, 17,699 worse and
14,027 better, Critical +12.2 per cent. Recomputing every record's band from its
published `R_median` under `classify_band` — the ABSOLUTE cutoffs — reproduces
its "published" column bit-for-bit:

    band        absolute recomputation     that document      the site publishes
    Low                     67,823               67,823              160,603
    Medium                  99,871               99,871              182,212
    High                   384,996              384,996              150,858
    Critical                67,854               67,854               91,390
    Extreme                  1,495                1,495               36,976

The site publishes per-country NORMALISED bands (Phase 2D, Task #461). 99.3 per
cent of records carry the `_band_norm_R_P5` / `_band_norm_R_P95` anchors, and the
published `classification` distribution is 30.4 / 25.7 / 26.5 / 13.4 / 4.0 per
cent — not the absolute shape.

So the earlier arithmetic was right and its bands were not. Every figure it
quotes describes a band scheme the site does not use, and it should not be cited
for cost. Its Section 1 — which chain each country's product reproduces from —
stands, and is confirmed independently by `RESULT_the_r7_data_sentinel.md`.

This is the same confusion, twice in one day: `classify_band_normalised(R, R_P5,
R_P95)` takes the COUNTRY's percentiles, while every record also carries its own
`R_P5`/`R_P95` Monte Carlo bounds under those exact names. The signature invites
the error. That is worth a guard, not just care.

## Method, and why it takes this shape

The substitution's effect on a record is a ratio of two cyber multipliers and
nothing else:

    raw0  = R_median - add_sum          ( == R_base x mult_product )
    R_new = soft_clip_upper(raw0 x ratio) + add_sum

Anchoring on the PUBLISHED `R_median` rather than recomputing it means ratio = 1
gives R_new = R_median exactly — no spurious movement, and no Monte Carlo noise,
because the rescore is never run (`FINDING_the_monte_carlo_is_unseeded.md`).

**The ratio is read from the record, never assumed.** Six countries are already
cut over; applying a v2/v1 ratio to them would add v2 a second time and remove a
v1 that was never in their product. The first run of this instrument did exactly
that and reported 4,302 band changes for the UK, which is already at v2 and whose
true cost is nil. Each record's published `mult_product` is compared against the
chain recomputed three ways — with v1, with v2, with both — and the ratio follows
the fit:

    fits v2      already cut over          ratio = 1
    fits v1      moves                     ratio = m_v2 / m_v1
    fits both    double-counted            ratio = m_v2 / m_both
    fits none    EXCLUDED, unattributable

Bands are compared on a consistent basis — `classify_band_normalised` with the
record's own stored country anchors, before and after. The published
`classification` field is reported alongside but is NOT the baseline.

## Scope, stated before any number

    estate                                                622,104
    baseline does not reproduce — EXCLUDED                400,655   64.4%
    ATTRIBUTABLE                                          221,384   35.6%
       already cut over, cost nil                          81,442
       on v1 — the population that can move               139,858
       double-counted (both in the product)                    84
    exact (raw0 <= 1.0, soft_clip_upper is the identity)  221,384  100.0%
    compressed, first-order                                     0

Every attributable record is in the exact regime. There is no first-order
approximation anywhere in this result.

## What it costs

On the 139,942 attributable records not already cut over:

    R_median moves                          61,471    43.9%
    BAND CHANGES                             4,249     3.0%   ( 0.68% of the estate )
       to a worse band                       3,716
       to a better band                        533

    band          before      after     change
    Low           68,021     67,516       -505
    Medium        67,689     67,369       -320
    High          38,755     38,673        -82
    Critical      29,854     29,968       +114
    Extreme       17,065     17,858       +793

    High     -> Critical   1,106      Critical -> Extreme   1,029
    Medium   -> High         979      Low      -> Medium      602
    Extreme  -> Critical     175      Critical -> High        138

The direction is the substance: **87 per cent of band changes are to a worse
band.** v2 sits near 1.03 against a v1 centred on 1.02, so the substitution
raises risk almost everywhere it acts. The earlier figure's near-balance (17,699
against 14,027) was an artefact of the wrong bands.

At 4,249 records the change clears the resampling floor of roughly 0.65 per cent
measured in `FINDING_the_monte_carlo_is_unseeded.md`, but by less than the
withdrawn figure suggested. It is a real, attributable, measurable effect and a
modest one.

## Why R_median moves on only 43.9 per cent, which is a finding in itself

Of the 139,858 records on v1, only 61,387 carry a v1 value; adding the 84
double-counted gives 61,471, exactly the number that move.

The other **78,471 have `R_median == add_sum` exactly**. Their `raw0` is zero, so
`R_base` is zero, and the entire published score is additive modifiers over a
zero base. **Anything multiplied by zero is zero: their whole multiplicative
chain — R3, R4, R6, R7, R8, R9, R10 — is inert.** The cyber substitution cannot
move them because nothing multiplicative can.

    poland 25,509 · austria 13,979 · czechia 7,825 · belgium 5,428
    australia 4,487 · lithuania 4,396 · netherlands 3,807 · and others

This looks like the Wave 4 `R_base_median = 0` regression that
`scripts/fix_wave4_r_base_regression.py` was written for (Task #461/462/463),
still present on 78,471 records, 12.6 per cent of the estate. NOT verified as the
same cause, and not this change's business — but a published resilience score
whose entire multiplicative chain is inert is a larger question than R7, and it
is registered here rather than left to be rediscovered.

## Also surfaced, not chased

The published `classification` reproduces from the record's own `R_median` and
its own stored country anchors on **63.1 per cent** of attributable records. The
0.65 per cent resampling floor does not account for a gap that size. Open.

## Re-derive

    python3 scripts/measure_r7_cutover_cost.py
    python3 scripts/measure_r7_cutover_cost.py --country uk     # expect nil
