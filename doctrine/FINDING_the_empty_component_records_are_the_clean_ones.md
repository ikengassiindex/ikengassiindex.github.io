# FINDING — the empty-component records are the only ones the fill never reached

**Date** 25 September 2026
**Occasion** The operator declined all three interim treatments for the 78,525 and directed that they be solved properly — "data ingest, scoring, etc through all layers". Establishing what they actually lack was the first step, and it reversed the question.
**Measured on** the deployed tree, all 39 countries, 622,104 records. Full census.
**Status** measurement only. Nothing published was changed.

## The expectation this overturns

`FINDING_78525_scores_are_the_flood_term_alone.md` records that 78,525 published
records carry an empty `components` dict and a score equal to the flood additive
term, 48,478 of them published as Low risk. The natural reading is that these are
the estate's most damaged records, and the natural remedy is to run whatever
populates components and bring them up to the standard of the other 543,546.

Both halves of that are wrong.

## What they lack

```
block                empty-components    filled
socio_economic            100.0%          100.0%
metrics                   100.0%          100.0%
lat / lon                 100.0%          100.0%
seismic                    81.9%          100.0%
markov                      0.0%          100.0%
graph_topology              0.0%          100.0%
transition                  0.0%          100.0%
```

Not source data. They carry ingestion — socio-economic, metrics, coordinates,
mostly seismic. What they lack, at exactly zero per cent, is `markov`,
`graph_topology` and `transition`.

Those three blocks have one producer: `scripts/enrich_esg_gaps.py`.

## Which modifiers they carry, and which they do not

```
modifier             empty-components    filled
R7_cyber_v2               100.0%           99.5%
R10_just                   99.6%           99.5%
R6c_flood                  99.6%           99.5%
R6d_wildfire               99.6%           99.5%
R6e_winter                 99.6%           99.5%
R8_adapt                   99.6%           99.5%
R9_compound                99.6%           99.5%
R6_seismic                 81.0%          100.0%
                     ---------------------------
R3_C_mult                   0.0%          100.0%
R4_F_topo                   0.0%          100.0%
R6_restoration              0.0%          100.0%
R7_cyber                    0.0%          100.0%
```

The four they lack are precisely the four `enrich_esg_gaps` writes. Everything
they carry is from the v4.2 derivation chain.

## And they do not reproduce from the name hash

`FINDING_the_name_hash_reaches_past_components.md` established by full census
that `R4_F_topo`, `R6_restoration` and `R7_cyber` are generated as
`vary(base, name, spread)` — a hash of the substation's own name — on 88.9 per
cent of the records that carry them. Reproducing that generator against both
populations:

```
                  empty-components            filled
                  reproduced / present    reproduced / present
R4_F_topo               0 / 0              457,391 / 515,798
R6_restoration          0 / 0              457,400 / 515,798
R7_cyber                0 / 0              457,427 / 515,798
```

Zero of zero, because they do not carry those fields at all.

## What the fill actually is

`enrich_esg_gaps.py` opens with:

> "All values are based on published institutional data, NOT synthetic random
> numbers."

and fills components with:

```python
comp[key] = round(vary(0.35, name + f'_{key}', 0.30), 4)

def vary(base, sub_name, spread=0.15):
    h = stable_hash(sub_name)
    factor = 1.0 + (h - 0.5) * 2 * spread
    return round(base * factor, 4)
```

There is no published institutional source behind `0.35`. It is a constant,
spread by a hash of the asset's name. The same function also produces
`V_socio`, `unemployment_rate`, `gdp_per_capita`, `rd_pct_gdp`, `E2_local`,
seismic PGA and the Markov steady state, each from a national base — so the
docstring is defensible for those and false for `components`, which has no base
to be institutional about.

## The consequence

**The 78,558 records with empty components are the only records in the estate
that `enrich_esg_gaps` never ran on.** They are not the damaged population. They
are the control group: they carry what was genuinely derived and nothing that
was fabricated.

Their published score is wrong — `R_base` is zero, so `R_median` is the flood
term and 48,478 read as Low. That is a real defect and it is on the site. But
its cause is an ABSENCE, and the other 543,546 have the same absence concealed
by a fill.

**Running the enrichment on them would not fix them. It would fabricate their
components and six further published fields, and destroy the only uncontaminated
population the estate has.** That is the obvious remedy and it must not be taken.

## What "properly published through all layers" means for them

| layer | state |
|---|---|
| ingestion | present — socio-economic, metrics, coordinates, seismic on 81.9% |
| modifiers | present, and only the genuinely derived ones |
| components | absent. Component I is derivable **now** — `_I_from_metrics` is on 100% of them. C, V, E, S and T are derivable for no record in the estate, because 15 of the 21 metrics sit on zero records |
| scoring, bands | blocked on components |

So the layer that blocks them is the same layer that blocks everyone, and the
work is the same work: `FINDING_the_index_declares_1097_sources_and_fetches_231.md`,
866 declared sources with no acquisition route.

What CAN be done for them now is what has been done for thirteen jurisdictions
already — give them a real component I from their own metrics. That would leave
them with one measured component of six and five absent, which is the true state
of every record in the estate once the fill is removed. It would also give them
a non-zero `R_base` for the first time.

Nothing here is proposed and nothing was changed. Recorded because the obvious
remedy is the harmful one, and because the population that looked worst is the
only one that was never touched.

## Related

- `FINDING_78525_scores_are_the_flood_term_alone.md`
- `FINDING_the_name_hash_reaches_past_components.md`
- `FINDING_what_the_components_fill_costs.md`
- `FINDING_the_unmeasured_set_the_band_for_the_measured.md`
- `FINDING_the_index_declares_1097_sources_and_fetches_231.md`
