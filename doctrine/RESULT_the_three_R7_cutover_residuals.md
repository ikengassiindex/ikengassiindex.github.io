# RESULT — the three residuals blocking the R7 cutover, resolved

**Date** 17 September 2026
**Measured on** the deployed tree. Nothing changed.
**Status** all three explained. None is a reason not to proceed; two change what
the restatement has to say, and one is a separate defect to fix in the same pass.

---

## Residual 1 — why Italy moves 5,692 substations to a better band and none to a worse

**It has nothing to do with R7.** The first guess was that Italy's v1 R7 value was
harsher than its v2 value. Measured, the opposite holds: `R7_cyber_v2` is a single
per-country CONSTANT (Italy 1.0325, France 1.0345, Germany 1.0343, US 1.0394,
Japan 1.0318) while `R7_cyber` v1 VARIES per record, and v2 is the higher of the
two on median. Swapping v1 for v2 should push bands *worse*.

The real cause is the general staleness, and its size differs by country:

| country | published `mult_product` ÷ what current values give |
|---|---:|
| **italy** | **1.1004** |
| **japan** | **1.0790** |
| france | 1.0088 |
| germany | ~1.009 |
| us | ~1.008 |

Italy's published product is **10 per cent above** what its own current modifier
values produce, so recomputation deflates every Italian record and every band
change is favourable. France, Germany and the US are under 1 per cent adrift, so
their changes are mixed.

The offset is not one modifier. Inverting the product to ask what value each
modifier *must* have had shows every one of the ten off by the same ~1.10 factor,
so no single field drifted. Nor is it a constant: the ratio runs smoothly across
deciles from 1.037 to 1.169, all records carry the same ten modifiers, and no
modifier key on any record is unknown to the registry.

**What the restatement must say:** Italy's improvement is an artefact of WHEN
Italy was last scored, not a favourable correction to Italy. The direction is
drift, and any reader shown a jurisdiction that improves uniformly is entitled to
that sentence.

## Residual 2 — Canada's 14.7 per cent is an enrichment gap, not a cutover failure

Canada has been cut over, and 1,107 of its 7,506 records still do not reproduce.
They are not a random 14.7 per cent. They are **exactly** the records that lack
four modifiers:

| modifier | present on all | present on the non-reproducing |
|---|---:|---:|
| `R3_C_mult` | 85.3% | **0.0%** |
| `R4_F_topo` | 85.3% | **0.0%** |
| `R6_restoration` | 85.3% | **0.0%** |
| `R7_cyber` | 85.3% | **0.0%** |

6,399 records carry the full set and reproduce; 1,107 carry a reduced set and do
not. **Canada holds two populations, one enriched and one never enriched**, and
the 85.3 per cent figure is the enrichment coverage, not a chain defect. The
cutover is not implicated.

## Residual 3 — 86 records publish an identity product they never computed

Estate-wide, **86 records across 14 countries** publish `mult_product` exactly
`1.000000` while carrying modifiers whose product is not 1.

| | | | |
|---|---:|---|---:|
| new-zealand | 31 | germany, ireland, netherlands | 3 each |
| norway | 28 | australia, denmark, france | 2 each |
| poland | 7 | czechia, finland, hungary, iceland, us | 1 each |

Example, Australia: `R_median` 0.303, `mult_product` 1.0, `add_sum` 0.0547, and
the record's own modifiers give 1.003265. A product that was never computed,
defaulted to the identity, and published as though it had been.

Small, and it is the same class as every other defect this session: a value that
looks like a result and is an absence. Fix it in the cutover pass rather than
separately — the re-score computes it correctly by construction.

---

## What this means for the decision

None of the three is a reason to hold the cutover.

- Residual 1 changes **what the restatement note must say**, not whether to make
  it.
- Residual 2 is **not a cutover problem at all** — it is an enrichment gap in
  Canada that would exist either way, and it should be tracked separately.
- Residual 3 is **fixed by the cutover** rather than blocking it.

The cutover remains: 31,726 substations changing band, 5.1 per cent, 17,699
worse and 14,027 better, Critical up 12.2 per cent, on a chain whose code is
proven sound where it has already run.
