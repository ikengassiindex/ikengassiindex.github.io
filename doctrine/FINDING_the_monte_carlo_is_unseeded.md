# FINDING — the Monte Carlo is unseeded, so a published band is not reproducible

**Date** 17 September 2026
**Found by** the dry run of `scripts/r7_substitute_and_rescore.py`, plan step 4.
**Status** measurement only. **Nothing was written.** The dry run is why.
**Sample** 1,839 records with components, 250 per country (first shard), across
sweden, luxembourg, italy, poland, uk, turkey, denmark, france. Each record
scored TWICE from identical input and the two outputs compared.

---

## How it surfaced

The step-4 dry run reported, on 300 Sweden records, that the substitution changed
`mult_product` on **zero** of them — correct, because
`compute_modifier_terms` already skips the retired v1, so removing the field is
arithmetically inert — while a third of their bands moved.

A change that changes no arithmetic cannot move a band. So the control was run:
rescore the records with **no substitution at all**, twice, and compare the two
runs against each other.

## The cause, at the line

    engine.py:539   def monte_carlo(components, modifiers, iterations=10_000, seed=None, ...)
    engine.py:560       seed: RNG seed for reproducibility (None = non-deterministic).
    engine.py:577       if seed is not None: np.random.seed(seed)
    engine.py:707       mc = monte_carlo(components, modifiers, iterations=10_000)

The seeding is implemented and works. The production path does not pass a seed.
`R_median` is the median of 10,000 draws, so it differs every run, and
`classification` is derived from it.

## MY FIRST MEASUREMENT WAS WRONG, AND THE WRONG NUMBER IS THE MEMORABLE ONE

Recorded here so nobody rediscovers it and believes it.

`classify_band_normalised(R, R_P5, R_P95)` takes the **country's** P5 and P95 —
stored per record by `apply_country_normalised_bands` as `_band_norm_R_P5` and
`_band_norm_R_P95`, and FIXED. I passed the record's own `R_P5`/`R_P95`, which
are its Monte Carlo confidence bounds and resample on every run. Both the value
and the threshold were therefore moving, and the two errors compounded.

    thresholds used              pooled band-flip rate between two identical rescores
    record CI bounds (WRONG)     ~30%, and 50.0% on italy
    country anchors  (RIGHT)     0.65%

I reported the wrong figure in conversation before catching it. The corrected
one is an order of magnitude smaller.

## What is actually true

Two rescores of the same record, nothing else changed:

    country        n     norm-band flip   abs-band flip    max dR     median dR
    sweden       250        3  (1.2%)        0 (0.0%)      0.002800    0.000500
    luxembourg    89        0  (0.0%)        0 (0.0%)      0.015800    0.000800
    italy        250        2  (0.8%)        0 (0.0%)      0.003300    0.000500
    poland       250        1  (0.4%)        0 (0.0%)      0.004400    0.000500
    uk           250        1  (0.4%)        2 (0.8%)      0.021500    0.000700
    turkey       250        0  (0.0%)        1 (0.4%)      0.016800    0.000700
    denmark      250        2  (0.8%)        0 (0.0%)      0.007000    0.000500
    france       250        3  (1.2%)        0 (0.0%)      0.002000    0.000500

    POOLED       1,839      12 (0.65%)

- Typical run-to-run movement in `R_median` is **0.0005 to 0.0008**.
- The worst single record seen moved **0.0215**.
- **0.65%** of records land in a different band on a second identical run.

## Why it matters, stated at its real size and no larger

At 0.65 per cent, something on the order of four thousand records across the
estate carry a published band that a re-run would not reproduce. That is an
inference from a 1,839-record sample, not a census, and the per-country rate
ranges 0.0 to 1.2 per cent — it is not uniform and should not be quoted as a
single estate figure without measuring properly first.

It is not a crisis. It is a floor. **Any restatement smaller than about one per
cent of records is indistinguishable from resampling noise**, so a change cannot
be credited with an effect at that scale. For context, the R7 cutover's own
predicted effect is 31,726 band changes, 5.1 per cent — comfortably above the
floor, by roughly eight to one.

The sharper point is about what the index claims. A resilience index published
per asset, whose per-asset band cannot be reproduced from its own stored inputs,
has an auditability gap that no amount of correct methodology closes. A reader
who re-ran the pipeline to check a substation's classification could get a
different answer and be right both times.

## Consequence for the R7 substitution — plan step 4 changes

**The substitution must not rescore.** Its effect is deterministic and
computable:

- Where `mult_product` does not change, nothing should move. Rescoring such a
  record injects noise for no benefit. On Sweden that is every record.
- Where `mult_product` does change, the shift propagates exactly as
  `0.25 x dI x mult_product`-style arithmetic already established — `soft_clip_upper`
  is the identity at or below 1.0, which holds on 99.4 per cent of records
  (`FINDING_what_the_components_fill_costs.md`).

This also protects the 31,726 prediction in
`RESULT_what_completing_the_R7_cutover_costs.md`, which came from a delta
computation and is therefore deterministic and sound. A rescore-based
restatement would have laid noise on top of it and made the two
indistinguishable.

## The remedy, which is NOT part of the R7 change

Seed the Monte Carlo deterministically per substation — from `substation_id`,
not a fleet-wide constant, so that draws stay independent across the fleet while
each record is reproducible. The estate already does exactly this elsewhere:
`scripts/refresh_v42_modifiers_re_composite.py:549` derives a deterministic value
from an MD5 of a stable key.

It is a one-line change at `engine.py:707` and a large decision, because it moves
**every** published `R_median` to its seeded value. That is a cohort-wide
restatement in its own right and needs its own pin, its own cost measurement and
its own operator decision. It must not ride inside the R7 cutover, where it would
be impossible to attribute afterwards which change moved what.

## What is NOT claimed

- Not that published scores are wrong. They are one valid draw.
- Not that the effect is uniform: 0.0 to 1.2 per cent across eight countries.
- Not an estate census. 1,839 records, first shard per country.
- Not that this explains the five countries whose `mult_product` does not
  reproduce from their own modifiers. Those ratios run to 1.1004, three orders of
  magnitude above this noise. Separate defect, see
  `RESULT_the_r7_data_sentinel.md`.

## Re-derive

Score any record twice with `engine.score_substation` and compare `R_median`.
Use `_band_norm_R_P5` / `_band_norm_R_P95` as the band thresholds — not the
record's own `R_P5` / `R_P95`, which is the error recorded above.
