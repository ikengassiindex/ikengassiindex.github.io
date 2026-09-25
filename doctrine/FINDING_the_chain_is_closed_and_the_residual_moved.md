# FINDING — the modifier chain is closed, and the residual moved into the components

**Date** 24 September 2026
**Occasion** Establishing what stands between component I and a verifiable rebuild.
**Measured on** the deployed tree, 39 countries, first shard per country — 229,174 records carrying `mult_product`, 163,832 carrying components and `R_median`. The sampling is stated because it is not a census.
**Status** measurement only. Nothing published was changed.

## What was gated on this

`FINDING_mult_product_is_three_populations.md`, 17 September:

> "No rebuild of `components.I` can be verified while `R_median` fails to
> reproduce from the published record, and this is why it fails… The order is
> forced: resolve the chain, then rebuild."

The chain has resolved. Nobody re-measured it, so the gate has been closed for
an unknown number of days while the work it blocks stayed parked.

## How it was found

Not by re-running the shape test. By solving for the value each modifier would
need to have for the published product to reproduce — for every multiplicative
modifier in turn, on 6,000 French records:

```
modifier          implied value: distinct    median      range
R3_C_mult                          5,284     0.95284     0.93883 .. 0.96749
R4_F_topo                          5,224     0.96090     0.94613 .. 0.97502
R6_restoration                     5,330     1.00012     0.98475 .. 1.01481
R7_cyber_v2                        5,334     1.01415     0.99924 .. 1.02974
R6d_wildfire                       5,343     1.09962     1.00002 .. 1.19442
R7_cyber                             102     1.00000     0.99995 .. 1.00005   ←
```

Every modifier smears across thousands of implied values. `R7_cyber` spikes on
exactly 1.0 — the identity. The published product is a product in which the
retired modifier is neutral, on every record tested.

That is **doctrine-conformant scoring with a non-conformant record**: the score
correctly excludes the retired modifier, and the record carries its value
(1.0259 on the record read) as though it had been applied. The defect is in
what is published beside the score, not in the score.

## The chain, estate-wide

Same shapes and the same sampling as the 17 September finding, so the two are
comparable:

| shape | 17 September | now |
|---|---:|---:|
| v1 only — R7_cyber applied, v2 excluded | 51.4% | **0.0%** (84 records) |
| **v2 only — R7_cyber_v2 applied, v1 excluded** | 16.8% | **100.0%** (229,070) |
| neither | 31.5% | 0.0% |
| fits no tested shape | 22.9% | **0.009%** (20 records) |

The five countries the 17 September finding named as unexplained — France,
Germany, Italy, Japan, the United States, each then fitting no shape on 97.8 to
99.5 per cent of its records — now reproduce at **100.0 per cent** under the
v2-only shape, every one.

The twenty exceptions are named rather than aggregated: poland 5, belgium 4,
slovenia 3, estonia 2, ireland 2, latvia 2, netherlands 1, new-zealand 1. They
are the same twenty on which `add_sum` also fails, which reproduces on
**229,154 of 229,174** records (99.99 per cent) from the single additive
modifier, `R6c_flood`.

**The R7 cutover is complete in the score.** The BLOCKING row that has carried
it as incomplete since before 17 September is describing an estate that no
longer exists.

## Four register rows are stale

```
[BLOCKING] R7_cyber · retired
[BLOCKING] R7_cyber + R7_cyber_v2 · mutual exclusivity      574 sampled assets
[BLOCKING] R7_cyber_v2 · operative in the published product       81.8%
[MATERIAL] mult_product · chain provenance                         5.8%
```

Constitution §9: the register carries every divergence between doctrine and
deployment. A register reporting divergences that have since closed fails in
the opposite direction to the one it was built to catch, and it fails more
quietly — nobody re-reads a row they already believe.

This is the second thing found today that the register could not see. The first
was a doctrine element with no engine counterpart, which section 1 of `build()`
skips because it iterates the measured registry and looks doctrine up. Both are
the same defect from opposite ends: **the register is only ever as current as
its last run**, and it carries no statement of when each row was last measured.

## Where the residual went

`R_median = soft_clip_upper(R_base × mult_product) + add_sum`, tested against
the published values on 163,832 records:

| | |
|---|---:|
| within 0.0001 | 13.37% |
| within 0.0005 | 53.81% |
| within 0.001 | 73.20% |
| within 0.01 | 86.11% |
| within 0.05 | 97.75% |

```
median error 0.00045    p90 0.01755    p99 0.08276    max 0.65645
```

`mult_product` reproduces on 100.0 per cent and `add_sum` on 99.99 per cent, so
**the entire residual is in `R_base`** — which is a weighted sum of the six
published components and nothing else.

Lowest-reproducing jurisdictions, which is where the components diverge most:

```
czechia     0.19%      luxembourg  7.87%
switzerland 2.11%      belgium     9.35%
greenland   5.41%      netherlands 10.07%
estonia     7.65%      costa-rica  10.65%
```

This is consistent with `FINDING_what_the_components_fill_costs.md`: the
components are filled by `enrich_esg_gaps` from `vary(0.35, name + '_' + K,
0.30)` — a hash of the substation's own name — and the fill is not the value
the scoring run used. For most records the difference is at the rounding
boundary; for about one record in fifty it is larger than 0.05, and it reaches
0.66.

## What this permits, and what it does not

**Permits.** The rebuild of `components.I` from `_I_from_metrics` is now
verifiable. The forced order from 17 September — resolve the chain, then
rebuild — is satisfied on the first clause.

**Does not.** It does not make `R_median` reproduce. That requires the
components themselves, and the measurement above is the size of that gap seen
from the outside. Rebuilding component I moves 0.25 of `R_base` onto a measured
footing; the residual in the other five components is untouched by it and is
not measurable the same way, because C, V, E, S and T carry
`_from_metrics` on zero records.

Nothing here is proposed and nothing was changed. Recorded because the gate it
lifts has been holding work that was ready, and because four rows in the
register describe a state that has passed.

## Related

- `FINDING_mult_product_is_three_populations.md`
- `FINDING_what_the_components_fill_costs.md`
- `FINDING_the_name_hash_reaches_past_components.md`
- `FINDING_the_conformance_register_reads_the_engine_against_itself.md`
- `FINDING_the_climate_chain_declares_what_it_never_derives.md`
