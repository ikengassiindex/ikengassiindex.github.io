# FINDING — a published metric must be recomputable from what the record publishes

**Status:** measured. I2 corrected. I1 and I5 outstanding.
**Date:** 12 September 2026
**Instrument:** `scripts/verify_metric_I2_published.py`

---

## 1. The claim being tested

Every metric is published alongside a raw counterpart — `_I1_raw`,
`_I2_raw`, `_I3_raw_degC_days`, `_I4_raw_km`, `_I5_raw_F_AA`,
`_I6_raw_count`. The purpose of publishing the raw is that a reader can verify
the metric without trusting the producer.

**That verification fails for some records**, and it fails in a way that looks
like an error on the reader's part.

## 2. The mechanism, which is one convention and not several bugs

Every derivation computes the metric from the **unrounded** raw, then rounds
the raw separately for publication. So the published pair need not agree in
the last digit:

    true raw    1.584505   ->  I2 published 0.01049
    _I2_raw     1.5845     ->  recomputes to 0.01048

Whether this is *visible* depends on how coarse the raw's rounding is against
the normalisation span:

| | raw rounding | records not reproducible |
|---|---|---|
| **I1** | 5 dp, global anchor 0.9029 | **46,391 of 622,079 — 7.457%** |
| **I2** | 5 dp, global anchor 45.3363 | 919 of 513,554 — 0.179% — **corrected** |
| **I5** | 5 dp, narrow Method B span | **≥1,181 raws ambiguous — 1.851%** |
| I4 | 3 dp, wide span | not measurable |
| I6 | integer raw | immune by construction |
| I3 | — | not measurable |

## 3. A measurement of mine that was wrong, and why

The first test asked whether two records sharing a published raw published the
same metric, **across the whole estate**. It reported I4 at 9.8% and I6 at
62.1%, and I presented those numbers.

They were artefacts. **I4, I5 and I6 use Method B, normalised against each
country's own fleet P5/P95**, so two records with the same raw in different
countries are *supposed* to differ. Re-run within country, I4 and I6 are
exactly 0.000%.

The lesson is the ordinary one: a test that does not model the thing it
measures will produce numbers, and the numbers will be wrong in whichever
direction the test's assumption leans.

## 4. The second problem, which is larger than the rounding

I1 and I2 normalise against a **global anchor recorded in doctrine**, so one
record plus the decision document is enough to verify.

I4, I5 and I6 normalise against **that country's fleet P5/P95, and those
values are published nowhere as numbers.** They appear only inside the
provenance sentence — "Method B over this country's fleet P5/P95" — 44,904
times in Austria's manifest alone, always as words.

They are not unverifiable: a reader can re-derive the percentiles from all of
that country's published raws, which is what `derive_from_raw` does. But that
requires the whole country's file rather than the record in hand, and
percentiles recomputed from *rounded* raws will not exactly equal the
originals.

**So the estate has two tiers of auditability and says so nowhere.**

## 5. The principle

> A published metric must be recomputable from published values. Where the
> normaliser is global it is cited in doctrine; where it is country-relative,
> the P5/P95 actually used must be published in that country's manifest — not
> only named in prose.

## 6. What was done, and what is outstanding

**Done — I2.** The metric is now computed from the rounded raw, so the
published pair agrees by construction. Cost: at most 1 unit in the 5th
decimal, 0.003% of the metric's range. Verified across all 513,554 records:
identity holds on every one, and ten records were rebuilt from their own
lat/lon through all sixty archive files.

**Outstanding, in order:**

1. I1 re-derive from the rounded raw — 622,079 records, ~46,391 last-digit
   changes, anchor frozen and unchanged
2. I5 re-derive likewise
3. Publish the Method B P5/P95 for I4, I5 and I6 in each country's manifest
4. A generic gate, so I7, I8 and I9 inherit the guarantee rather than each
   having to be caught

I3, I4 and I6 need no value change. Nothing measurable is wrong with them;
they need only item 3.

## 7. Why this was not caught in September

I1 was verified two ways for negative zeros on 9 September and published. It
was never asked whether its published pair was self-consistent, because the
question had not occurred to anyone. The instrument that found it was written
three days later for a different metric, and found I1 by being pointed at it
afterwards.

A check catches what it was built to catch. The estate's coverage of its own
correctness is the set of questions someone has thought to ask, and that set
is smaller than it feels.
