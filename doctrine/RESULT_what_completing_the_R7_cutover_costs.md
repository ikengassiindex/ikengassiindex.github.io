> ## ⚠ SUPERSEDED FOR COST, 17 September 2026
>
> **Section 2 onward measured the wrong bands.** Every band figure in this
> document — 31,726 changes, 5.1 per cent, 17,699 worse / 14,027 better,
> Critical +12.2 per cent, "Italy moves 5,692 to a better band and not one to a
> worse" — was computed with `classify_band`, the ABSOLUTE cutoffs. The site
> publishes per-country normalised bands (Phase 2D). Recomputing absolute bands
> from published `R_median` reproduces this document's "published" column
> bit-for-bit, against a published distribution that is entirely different.
>
> Corrected measurement: `RESULT_what_the_R7_cutover_costs_in_published_bands.md`
> — 4,249 band changes on the attributable population, 87 per cent of them to a
> worse band.
>
> **Section 1 stands.** Which chain each country's published product reproduces
> from is unaffected, and is confirmed independently in
> `RESULT_the_r7_data_sentinel.md`. Kept whole rather than edited: a superseded
> measurement that is still cited elsewhere is evidence, and rewriting it would
> hide how the error was made.

# RESULT — what completing the R7 cutover would cost

**Date** 17 September 2026
**Measured on** every scored record in the deployed tree: 622,039 records, 39
countries, every shard. Not a sample.
**Status** measurement only. Nothing was changed.

---

## The question this answers

`FINDING_mult_product_is_three_populations.md` established that 51.4 per cent of
scored records still carry a `mult_product` computed with the RETIRED R7_cyber
v1, that six countries have been re-scored under v2, and that five — France,
Germany, Italy, Japan, the United States — fit neither shape.

Two things needed settling before anyone acts. **Is the chain code sound, or
would a re-score reproduce a defect?** And **what does completing the cutover do
to published R?**

## 1. The chain code is sound. The proof is where it has already run.

`compute_modifier_terms`, the deployed code a re-score would execute, reproduces
the published `mult_product` exactly in the countries that have been re-scored:

| country | reproduces |
|---|---:|
| turkey | **100.0%** |
| sweden | **100.0%** |
| uk | **100.0%** |
| finland | 98.7% |
| norway | 95.6% |
| canada | 85.3% |

and on 0.0–2.8 per cent everywhere else. Estate-wide, 86,776 of 622,039 — 14.0
per cent — which is exactly the already-cut-over population and nothing else.

**So the divergence is not a bug in the chain.** Where the chain has been run
against the current registry, its output matches the record to the fourth
decimal. The 33 countries that diverge diverge because their scores predate
their current modifier values, not because the arithmetic is wrong.

For the five "unexplained" countries this also closes the earlier hypothesis as
far as it can be closed without history: their published product cannot be
produced from the values now on their records under any tested shape, and
recomputing from those values gives a different number. **A re-score would make
them reproduce by construction.** Canada's 85.3 per cent is the one residual
worth a look — it has been cut over and still has 14.7 per cent that do not
reproduce.

## 2. What it costs

| | published | after cutover | change |
|---|---:|---:|---:|
| Low | 67,823 | 67,761 | −62 |
| Medium | 99,871 | 105,216 | +5,345 |
| High | 384,996 | 371,209 | **−13,787** |
| Critical | 67,854 | 76,157 | **+8,303** |
| Extreme | 1,495 | 1,696 | +201 |

**31,726 substations change classification band — 5.1 per cent of the estate.**
17,699 move to a worse band and 14,027 to a better one. The Critical band grows
12.2 per cent.

The delta is EXACT on all 622,039 records: every one has `R_raw ≤ 1.0`, where
`soft_clip_upper` is the identity, so the base that actually fed the chain is
recoverable as `(R_median − add_sum) / mult_published` without needing to know
which base field was used — a question the estate still does not answer.

## 3. Where it lands, and one country that should be looked at

| country | band change | worse | better |
|---|---:|---:|---:|
| **italy** | **13.7%** | **0** | **5,692** |
| japan | 11.2% | 9 | 680 |
| israel | 7.8% | 20 | 0 |
| us | 7.3% | 3,891 | 1,475 |
| germany | 6.8% | 5,077 | 2,286 |
| france | 6.1% | 6,822 | 3,531 |
| turkey, sweden, uk, finland, norway, canada | ≤0.9% | — | already cut over |

**Italy moves 5,692 substations to a better band and not one to a worse.** Japan
is nearly the same shape. A correction that is uniformly favourable in one
jurisdiction and mixed everywhere else is not obviously wrong — Italy carries the
full twelve-modifier set and its v1 R7 value may simply have been harsher — but
it is the kind of asymmetry that a reader will ask about, and it should be
understood before it is published rather than after.

## 4. How this compares to the other pending restatement

| | band changes | direction | Critical |
|---|---:|---|---:|
| Complete the R7 cutover | 31,726 (5.1%) | 17,699 worse / 14,027 better | +12.2% |
| Rebuild `components.I` | 89,056 (16.4%) | 67,097 worse / 21,959 better | +37% |

The cutover is the smaller and more balanced of the two, and it is the one that
must come first: it is the reason `R_median` does not reproduce from the
published record, and no rebuild can be verified until it does.

## 5. What this does not settle

- **Which base field feeds the chain.** `R_base`, `R_base_median` and the
  component weighted sum all fail to reproduce `R_median` through the published
  modifiers at better than 31 per cent. The method above sidesteps it; a
  re-score would have to answer it.
- **Canada's 14.7 per cent** that do not reproduce despite being cut over.
- **The 56 records** publishing `mult_product` exactly 1.000000 against modifiers
  whose product is not 1.
- **Whether to re-score at all.** This is a restatement of published scores for
  622,039 substations. Nothing here recommends it; it prices it.

## A note on the measurement

The first pass of this ran on the first shard of each country — 256,498 records
— and reported 3.7 per cent band changes. That sampling is representative WITHIN
a country (checked: France's first shard is within 0.7 points of France entire on
every band) but it weights a 43,000-record country the same as a 169,000-record
one, and the large countries are where the change concentrates. Re-run over every
shard the figure is 5.1 per cent, and Critical grows 12.2 per cent rather than
4.3. The sampled number was not wrong about its population; it was wrong about
the estate, which is the distinction `DOCTRINE_a_check_must_read_the_artefact.md`
exists to keep.
