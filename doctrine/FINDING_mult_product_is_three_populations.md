# FINDING — the mult_product chain is three populations, not one mystery

**Date** 17 September 2026
**Measured on** the deployed tree, 39 countries, 256,533 scored records (first
shard per country; the sampling is stated because it is not a census).
**Status** diagnosis only. Nothing was changed.

---

## What was open

The conformance register has carried, as BLOCKING, that *"22.9% reproduce under
no tested chain shape"* with the note *"provenance of these published values is
unexplained; no doctrine currently accounts for them"*. Separately it has carried
that the R7_cyber v1→v2 cutover is *"complete in the registry and in the record,
and incomplete in the score"*.

Those are not two findings. They are one, plus a third thing nobody had named.

## What reproduces, and under what rule

`R_median = soft_clip_upper(R_base × mult_product) + add_sum`.

**`add_sum` reproduces from the published modifiers on 100 per cent of records.**
The additive term is not in question.

`mult_product` is the product of the multiplicative modifiers, each clipped to
its declared range. Range-clipping matters: without it Poland reproduces at
98.63 per cent, with it at 99.97.

The estate splits three ways:

| shape | records | share | countries |
|---|---:|---:|---|
| **v1 only** — R7_cyber applied, R7_cyber_v2 excluded | 131,964 | **51.4%** | 30 countries, almost all at 100.0% |
| **v2 only** — R7_cyber_v2 applied, R7_cyber excluded | 42,978 | **16.8%** | canada, finland, norway, sweden, turkey, uk |
| **neither** | 80,896 | **31.5%** | france, germany, italy, japan, us |
| both applied / neither R7 | 695 | 0.3% | residual |

## The three conclusions

**1. THE R7 CUTOVER IS INCOMPLETE IN THE SCORE, AND THAT IS MOST OF THE ESTATE.**
51.4 per cent of scored records still carry a `mult_product` computed with
R7_cyber v1 — the retired modifier. Six countries have been re-scored under v2;
thirty have not. This is the BLOCKING R7 row, quantified: it is not a fringe, it
is the majority.

**2. THE "UNEXPLAINED" POPULATION IS FIVE NAMED COUNTRIES, NOT A DIFFUSE 23 PER
CENT.** France, Germany, Italy, Japan and the United States account for
essentially all of it — 98.0, 98.1, 99.4, 99.5 and 97.8 per cent of each
country's scored records fit no tested shape. Everywhere else, one of the two
shapes fits at 98–100 per cent. A finding stated as a percentage of the estate
read as a widespread haze; it is five countries and they are nameable.

**3. IT IS NOT A SINGLE MISSING FACTOR.** The ratio of published `mult_product`
to the v1-shape product is not constant: 1,602 to 1,761 distinct values per
country at four decimals, with a p5–p95 spread of roughly ±8 per cent. No single
omitted or extra modifier explains it.

## The hypothesis this points at, UNTESTED

Those five countries are exactly the ones carrying the full twelve-modifier set —
`R3_C_mult`, `R4_F_topo`, `R6_restoration` and both R7 variants, which most
countries do not have. The shape of the residual is consistent with the modifier
VALUES on the record having been updated after the score was computed, so the
published product is a product of values the record no longer holds.

That is a hypothesis and it is recorded as one. It was not tested, and it must be
before anyone acts on it.

## Why this matters now

No rebuild of `components.I` can be verified while `R_median` fails to reproduce
from the published record, and this is why it fails. The component rebuild
measured at 89,056 substations changing band
(`FINDING_what_the_components_fill_costs.md`) sits behind this. So does any
restatement of published scores.

The order is forced: resolve the chain, then rebuild.

## One small separate defect

56 records across the estate publish `mult_product` exactly 1.000000 while
carrying modifiers whose product is not 1 — five in the UK, three in Germany, one
each in Finland, Norway and others. A product that was never computed, defaulted
to the identity, and published as if it had been.

## A note on how this was measured

The first pass fitted Poland at 99.97 per cent under the v1 shape and was one
sentence away from being written up as the estate's answer. Checked against the
other 38 countries it fits 51.4 per cent, and fits Italy, Turkey and the UK at
**zero**. That is the eighth instance this session of a single-country
measurement nearly stated as a general one, and the first that was caught before
it reached a document rather than after. The rule is in
`DOCTRINE_a_check_must_read_the_artefact.md`: name the population inside the
claim.
