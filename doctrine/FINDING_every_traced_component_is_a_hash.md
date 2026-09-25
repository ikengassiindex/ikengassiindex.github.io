# FINDING — every component whose provenance can be traced is a hash

**Date** 25 September 2026
**Occasion** `FINDING_what_determines_a_substations_rank.md` closed by naming its
own unfinished business: *"Where the 31 non-hash countries' C, V, E and S and T
values come from. That is the next measurement and it is not made here."* This
is that measurement.
**Measured on** the deployed tree, 39 jurisdictions, 622,104 records, and every
`ssi-data.json.<tag>` backup those jurisdictions hold on disk.
**Status** measurement only. Nothing published was changed.

## The correction

DP reported the name-hash fill reaching eight jurisdictions and `0.0%`
everywhere else, and concluded that the other thirty-one drew their components
from somewhere unestablished.

They do not. The reproduction test returned `0.0%` because in those thirty-one
jurisdictions the hash was **rescaled after it was written**. The generator is
still there. Rescaling changed the numbers; it did not change where they came
from.

Two facts were needed to see it, and both are in the tree.

## 1 — a test that survives the rename

`scripts/enrich_esg_gaps.py` fills an absent component with

```
vary(0.35, name + '_' + K, 0.30)  =  0.35 * (1 ± 0.30)
```

whose image is exactly the closed interval `[0.2450, 0.4550]` — 2,101 distinct
values at four decimal places, and nothing outside it, ever.

That is a property of the **output**. It holds whether or not the seed still
exists. It has to, because the seed does not: the August dedupe remediations
renamed every Italian and Portuguese substation to `Substation <id>`, which
destroys seed reproduction while leaving the hash's output untouched. Testing
the seed undercounted the fill. Testing the interval does not.

```
C, V, E, S and T lie entirely inside [0.2450, 0.4550]

  france      168,894   100.0%        italy        41,662   100.0%
  germany     108,016   100.0%        portugal     13,564   100.0%
  us           73,859   100.0%        spain        12,438   100.0%
  uk           59,744    97.1%        japan         6,168   100.0%

  484,345 records — 77.9% of the estate — in 8 jurisdictions
```

Component I sits outside the band wherever it was rebuilt from its own metrics.
It is the only component anywhere in these eight that does.

## 2 — the other thirty-one were normalised, not measured

In the remaining thirty-one jurisdictions the last operation applied to a
component is a hard-clipped min–max renormalisation on that country's own
fifth and ninety-fifth percentile:

```
published  =  clip01( (x - P5) / (P95 - P5) )
```

Its signature is unmistakable and is present across the estate: **exactly 5.0
per cent of records at 0.0 and 5.0 per cent at 1.0**, because a hard clip at
P5 and P95 puts precisely a twentieth of the population at each end.

```
share of records at exactly 0.0 / exactly 1.0, component C

  hungary   5.02% / 5.02%      korea       5.04% / 5.04%
  slovakia  5.03% / 5.03%      new-zealand 5.07% / 5.01%
  iceland   4.97% / 5.12%      belgium     5.09% / 5.09%
  ireland   5.03% / 5.03%      netherlands 5.13% / 5.06%
  poland    5.03% / 5.07%      canada      4.95% / 4.99%
  australia 5.25% / 5.06%      norway      4.93% / 5.12%
```

Reproduced directly against the prior published state, matched by
`substation_id`, the renormalisation hop returns **100.0%** in hungary, greece,
colombia, slovakia, estonia, netherlands, belgium, chile and poland, and
between 27% and 96% elsewhere, the shortfall being records a later ingest
overwrote.

**A value produced this way is a within-country percentile of whatever went in.
It is not a quantity.** Zero does not mean no condition risk; it means bottom
twentieth of this country. One does not mean severe; it means top twentieth.
Nothing in the published record says so, and `R_base` weights it against five
other components as though it were a level.

## 3 — and what went in was the other hash

Walking each jurisdiction's backups oldest first and inverting the generator
per region — `base = v / (1 + (h·2−1)·pct)`, `h` the MD5 of
`substation_id + name + K`, `pct` fixed per component in the source — the
preimage of the renormalisation reproduces `det_var` from
`scripts/score-country.py` at **100.0 per cent**:

```
  hungary    3,502 records   C V I E S T    100.0%
  slovakia   1,516 records   C V I E   T    100.0%
  iceland      687 records   C V I E S T    100.0%
  israel       257 records   C V I E S T    100.0%
  slovenia     158 records   C V I E S T    100.0%
```

This is a second MD5 generator, distinct from `enrich_esg_gaps.py`'s, reached
through `build_hungary_ssi.py`, `build_slovakia_ssi.py` and
`scripts/s109/regen_legacy_country.py` — the last of which *derives* per-region
bases from a country's own legacy means and then re-runs the hash over them,
which is why its output tracks the old distribution's shape and carries none of
its content.

So the published component in these jurisdictions is an MD5 digest of the
substation's identifier, rescaled to its own country's percentile range.

## 4 — the constants

Where the hash was clipped flat before normalisation, `P5 == P95`, and the
normaliser emits `0.5`.

```
one single value across the whole jurisdiction

  component S = 0.5000    norway 5,842 · hungary 3,502 · slovakia 1,512
                          latvia 1,219 · ireland 994 · estonia 614
                          lithuania 505                    = 14,188 records
  component V = 0.5000    latvia 1,219
  component C = 0.5000    switzerland 947
```

`S` carries weight 0.20 in `R_base`, `C` carries 0.30. On 14,188 records a fifth
of the score is a constant: it enters at full weight and moves no substation
relative to any other. Hungary shows why — `pga_base 0.05 × seismic_alpha 0.35
× 2 = 0.035`, below the generator's own `max(0.10, …)` floor, so every one of
3,502 records clipped to the floor before anything else ran.

Near-constants sit just behind: lithuania `V` 94.1% on one value, turkey `V`
72.0%, slovenia `S` 76.4%, greece `V` 66.7%, latvia `C` 54.6%, turkey `E` 53.6%,
czechia `C` 45.9%, estonia `C` 44.6%.

## 5 — the stage that would have done this properly has no source

`scripts/pipeline/ingestion/components.py` is the component builder. Its
docstring states the rule the estate needed — *"A component letter is emitted
only when every metric feeding it is present"* — and names, in its own words,
the exact defect measured in §4: a normaliser that returns `0.5` on a degenerate
column is *"a silent default — a constant masquerading as a measurement"*.

There is no `components.py` on disk. There is only
`scripts/pipeline/ingestion/__pycache__/components.cpython-310.pyc`, dated
20 August 2026. The text quoted above was read out of the bytecode.

§7.8: a check that cannot be RUN is not a check. A stage that cannot be read is
not a stage.

## What this leaves standing

DP measured that component `C` decides 43.81% of a substation's rank — more than
any other component, and its four metrics C1–C4 sit on zero records in all 39
countries. This document establishes what is in `C` instead, everywhere the
provenance can be traced: a hash of the identifier, sometimes rescaled.

## What is not established

Eight jurisdictions hold components whose preimage predates the oldest backup on
disk, so it cannot be reached from the deployed tree at all: sweden (3,774),
czechia (1,074), greece (556), and the components of turkey, mexico, latvia,
lithuania and estonia that neither generator reproduces at any recorded state.
Their granularity is low — greece publishes 8 distinct values of `V` across 556
records, turkey 3 across 4,001 — which is consistent with a coarse regional
lookup, but consistency is not provenance and none is claimed here.

## Cross-checks

```
records measured                     622,104   = published cohort exactly
records with no components at all      78,558   = 5fefb9ac exactly
jurisdictions                              39
```

## Instruments

```
scripts/ssi_component_signature.py          one row per jurisdiction per
                                            component, from the published
                                            register alone
scripts/ssi_measure_component_lineage.py    walks every backup a jurisdiction
                                            holds, oldest first, and reports
                                            each hop as identity, renormalisation
                                            or neither
scripts/ssi_measure_component_preimage.py   inverts det_var per region without
                                            needing a config
scripts/ssi_measure_component_provenance.py first pass; superseded by the above
```

All four read only. Nothing published was changed.
