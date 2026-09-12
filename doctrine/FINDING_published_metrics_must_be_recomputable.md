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

## 4. A CLAIM IN THIS DOCUMENT WAS WRONG — corrected 12 September

This section previously asserted that I4, I5 and I6 normalise against
per-country P5/P95 "published nowhere as numbers... only inside the provenance
sentence, as words", and concluded that the estate had "two tiers of
auditability and says so nowhere".

**That was false.** The anchors are published, at full precision, in
`meta.metric_derivations[]`:

    anchors : {'I4': [5.007807995615456, 131.79367741271264],
               'I6': [38.0, 1079.0]}
    anchor  : {'value': 51.93, 'units': 'degree Celsius days per year',
               'maps_to': 0.3, 'frozen': True, 'basis': '...'}

The claim came from grepping a manifest for the string `anchor`, seeing 765
hits, and inferring prose without opening one of them. It reached two commit
messages before it was checked.

One real property of that log does matter: **`metric_derivations` is
APPEND-ONLY.** Austria carries three I1 entries and two for I4/I6. The LAST
entry naming a metric is the live one; reading an earlier one gives a
superseded anchor. I3's current Method C anchor supersedes an earlier Method B
pair in the same log.

Measured against the published anchors, taking the last entry per metric:

| metric | checked | reproducible | not |
|---|---|---|---|
| I1 | 622,079 | **622,079** | 0 |
| I2 | 513,554 | **513,554** | 0 |
| I3 | 620,129 | **620,129** | 0 |
| I4 | 620,696 | **620,696** | 0 |
| **I5** | 620,129 | 518,119 | **102,010 — 16.450%** |
| I6 | 620,696 | **620,696** | 0 |

Five of six reproduce from the published record. **Only I5 does not**, and for
the precision reason in section 2, not an anchor one.

## 4a. The scale mismatch, found while checking the above

Construct section 03 defines both normalisation methods as producing N(x) in
[0, 1]. Published, I3/I4/I5/I6 carried N(x); **I1 and I2 carried 0.30 x N(x)**.

The construct's line — "Method C ... Applies to: I1, I2, I3 [0, 0.30]" — is
genuinely ambiguous. Beside C3 it reads "[0%, 100%]" and beside E2
"(E2_local - 1.50) / (1.85 - 1.50)", which are unambiguously INPUT bounds. But
`DECISION_I1_anchor.md` reads it as the output interval ("raw 0.9029 -> IRI
0.3000"), and I1's raw runs to 0.9029 m, which cannot be an input bound of
0.30. I3 resolved it one way, I1 and I2 the other. Both readings are
defensible; together they were incoherent.

It mattered because `ssi_derive_component_from_metrics.py` computes
`sum(INTRA_WEIGHTS[k] * metrics[k]) / coverage` across both scales, so I1 and
I2 entered the shadow component at roughly 30 per cent of their defined weight.

**Aligned 12 September**, operator's pin, to [0, 1] — matching what both
methods compute, matching four of the six metrics, and matching the shape I3
already published:

    I<n>       = round(min(1, raw / ANCHOR), 4)     [0, 1]
    _I<n>_iri  = round(0.30 * min(1, raw / ANCHOR), 5)

1,135,633 metric values changed. No raw, anchor, coverage or refusal moved, and
no published R score moved. `_I_from_metrics` was rebuilt afterwards and is now
arithmetically correct on all 622,104 records, range 0.0205 to 1.0000.

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

**Done since:** I1 repaired (46,391 records), I1 and I2 aligned to [0, 1],
`_I_from_metrics` rebuilt, and the verifier rewritten to CHECK tier two
against the published anchors rather than assert anything about them.

**Outstanding:**

1. **I5.** The only metric that still does not reproduce. Its raw is published
   at 5 dp against normalisation spans as narrow as 0.023 — about 2,300 steps
   where ~10,000 are needed for a 4 dp metric. The information is not in the
   record and cannot be recovered from it, so this needs a re-derivation from
   the ERA5-Land archive (all 272 files are on disk) with the raw published at
   7 dp.
2. **A gate**, once I5 passes, so I7, I8 and I9 inherit the guarantee rather
   than each having to be caught.

## 7. Why this was not caught in September

I1 was verified two ways for negative zeros on 9 September and published. It
was never asked whether its published pair was self-consistent, because the
question had not occurred to anyone. The instrument that found it was written
three days later for a different metric, and found I1 by being pointed at it
afterwards.

A check catches what it was built to catch. The estate's coverage of its own
correctness is the set of questions someone has thought to ask, and that set
is smaller than it feels.
