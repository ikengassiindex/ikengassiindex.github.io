# METHOD — the C mosaic

**Date** 25 September 2026
**Applies to** components C, V and E1, whose only inputs are the regulators'
continuity-of-supply returns.
**Status** method, declared before acquisition. No data is acquired here.

## Why a mosaic and not a source

`doctrine/FINDING_every_traced_component_is_a_hash.md` established what is in
the component layer today. The replacement cannot be one source per country,
for two reasons that are properties of the data and not of our preference.

**No single regulator publishes at the granularity the index claims.** The
finest unit located anywhere is the Norwegian *nettselskap* and the Spanish
zonal index, at roughly sixty substations to a measured value; the coarsest is
the German *Bundesland*, at 6,751. An index whose purpose is the greatest
granularity available on open data cannot take one source per country and call
the result uniform.

**And a single source cannot be checked.** A number with one provenance is
either believed or not. A number that reproduces a second, independently
published number is checked — and the check is the deliverable, not the number.

So: every source that carries continuity information enters, at whatever
granularity it has. The finest admissible layer sets the value. Every coarser
layer is kept, and its function is to constrain the finer one.

## The layers

```
  L0  definitional     CEER-ECRB benchmarking — what each country's SAIDI
                       counts: planned in or out, exceptional events in or
                       out, which voltage, which customer base
  L1  national         the regulator's own published national figure
  L2  sub-national     the regulator's published administrative unit
                       (département, Bundesland, fylke, region, zone)
  L3  per-operator     the regulator's per-DSO return, where published
                       (Italy 91 DSO x concentration x region;
                        Norway per nettselskap; Sweden, Finland per DSO)
  L4  operator's own   the DSO's open data, where it publishes below its
                       own licence area (several GB DNOs publish at primary
                       substation; Enedis publishes at commune)
```

L0 is not a data layer and is never a value. It is the record of what the
other layers mean, and it is read first, not last.

## The combination rule

**The finest admissible layer sets the value.** Admissible means: published by
the regulator or by the operator under regulatory obligation, open, read, and
carrying its own unit key and customer weight.

**Every coarser layer is retained as a constraint, never discarded and never
averaged into the value.** Its role is the reconciliation identity below.

**A disagreement between layers is resolved or recorded. It is never split.**
Averaging two layers that disagree destroys the only evidence that something
is wrong. If the fine layer does not roll up to the coarse one, either the
join is wrong, the weight is wrong, or one of the publications is wrong — and
each of those is a finding, not a rounding.

## The reconciliation identity

This is the audit mechanism and the whole claim to irrefutability.

For any two adjacent layers, the customer-weighted aggregate of the finer must
reproduce the coarser:

```
        sum_i ( customers_i  x  metric_i )
        ──────────────────────────────────   ==   metric_coarse
              sum_i  customers_i
```

Every published cell carries its residual against the layer above it. A reader
who disputes the value must dispute the regulator's own aggregate.

### The condition that makes it mean anything

**The coarse layer constrains the fine one only if the regulator published it
independently.** A coarse layer computed from the fine one is the fine one
rearranged. Its residual is zero by construction and it corroborates nothing.

This is not a hypothetical. It was walked into on the day this method was
written, on the estate's own best data.

```
  Italy, 25 September 2026

  arera_tiqe_2024_dso_raw.csv       91 rows, transcribed from three ARERA
                                    PDFs — a genuine L3
  arera_tiqe_2024_regional.csv      20 rows — reconciles to the 91 rows at
                                    0.0000 on every region
  national D1L 44.54                reproduces the 91 rows to +0.003%
```

Twenty regions out of twenty at exactly `0.0000`, and a national figure three
thousandths of a per cent away, were read as an independent check passing. The
session log that produced the files says otherwise, verbatim: *"All 20 regional
values replaced with user-weighted aggregates from 91 DSO-region records."*
The regional file is the DSO file summed. The national figure is the same 91
rows weighted. One publication, three views, no check.

**A residual of exactly zero across every row is evidence of derivation, not of
agreement.** Independent publications do not reconcile perfectly; they
reconcile to within their rounding, their vintage and their exclusions, and the
size of that residual is the information. A zero residual must be treated as a
failed check until the provenance of both layers is read and shown to differ.

So Italy today holds one measured layer and no constraint on it. Its L1 and L2
must be read from ARERA's own publication before either can constrain L3, and
until then the register records Italy as measured-but-unchecked, which is
better than what is published now and is not yet what this method requires.

## The ceiling, stated per country

**No combination manufactures granularity below the finest published unit.**
A cocktail of three coarse sources is still coarse. Where the finest
admissible layer is coarse, the register says so in substations-per-measured-
value, and the component says so in its provenance. That number is published
alongside C, per country, and it is the honest statement of what C can and
cannot resolve there.

Interpolating below the finest unit — by area, by population, by any smooth
function — is forbidden. It manufactures variation that was never measured,
which is the defect this method exists to end.

## What may not enter

- a value typed by hand, whatever source is cited beside it
  (`ingestion/cre_tiqe.py::fetch()` is the instance on record)
- a value generated from an identifier
- a projection, a scenario, or a modelled counterfactual
  (`italian_saidi.py::saidi_after_min` is the instance on record)
- a value whose unit key cannot be joined to the fleet, which is absent, not
  zero
- a source behind payment (Pin 15)
- a citation not read (§7.6)
- a coarse layer derived from the fine layer and presented as a check on it
  (`arera_tiqe_2024_regional.csv` is the instance on record, and the error was
  made here before it was caught)

## The per-country record

Each jurisdiction carries three files and no more.

```
  c_metrics/<slug>.csv
      unit_key, unit_type, layer, C1_saidi_min, C2_saifi,
      C3_mt_exceed_pct, C4_planned_count, customers, year,
      source_id, residual_to_parent

  c_units/<slug>.json
      the join from substation to unit_key, its method, and the count of
      substations that join to nothing — which get no C

  c_definitions/<slug>.yaml
      from L0: planned in/out, exceptional events in/out, voltage level,
      customer basis, and the regulator's own name for each index
```

`A_regulatory` carries the unit value to the asset, as it already does. It is
a normalisation, not a disaggregation, and the component's provenance says so.

## Order

Italy first: L3 is acquired and in the estate already, and its independent
L1 and L2 must be read from ARERA before it can be called checked.
Then France, whose consumer and schema exist and whose data does not. Then
Switzerland, whose route is already written down. Then the remaining 36 in
descending record count.

## Addendum, 25 September 2026 — the methodology transfers where the data does not

`FINDING_C3_is_not_published_where_C1_C2_C4_are.md` established that no
jurisdiction yet checked publishes C3 alongside C1, C2 and C4. The first
reading of that was that the mosaic had failed: with no jurisdiction holding
both, no cross-sectional relationship can be fitted and nothing can be carried
across.

That reading was too narrow, and it was corrected by the operator. **What
transfers between jurisdictions is the construct, not the coefficients.**

France's C3 is the share of a département's customers outside the regulated
continuity standard — *distance from the standard*. That is a construct. It
needs, in any jurisdiction, two things: a measured continuity quantity and a
published regulatory threshold for it. Where both exist, the construct can be
computed natively, from that jurisdiction's own data and its own regulator's
own standard, with nothing imported but the idea.

Italy has both. ARERA publishes N1L per ambito; TIQE article 32 publishes the
maximum for that ambito's concentration class. Norway publishes counts per
fylke and has a leveringskvalitet standard. Spain publishes NIEPI per
municipio and zone and has individual quality limits in Orden ECO/797/2002.

So the rule:

**Where a metric is unavailable, do not import a fitted relationship from
another jurisdiction. Import the construct, and compute it from local measured
data against the local published standard.** Nothing crosses the border except
the definition, which is the only thing that travels without losing meaning.

### And what that is not

The OECD/JRC Handbook on Constructing Composite Indicators names three methods
for missing data — case deletion, single imputation, multiple imputation.
Renormalising a component's weights over its surviving metrics is none of
them. It is implicit single imputation: it silently sets the absent metric to
the weighted mean of the others. The Handbook warns that single imputation
"is known to underestimate the variance", and quotes Dempster and Rubin, that
imputation "is seductive because it can lull the user into the pleasurable
state of believing that the data are complete after all".

For data that is unavailable rather than missing, the Handbook says something
else, at page 24: *"Proxy measures can be used when the desired data are
unavailable."*

A proxy declares what it stands for and carries an evidence tier below the
measurements beside it. A renormalisation declares nothing and hides inside
the weights. Prefer the proxy, and say what it approximates.

### The obligations a proxy carries

1. It names the construct it stands for and the jurisdiction that publishes
   the real thing.
2. Its numerator is measured and its denominator is a published regulatory
   coefficient, each cited and read.
3. It states every way in which it differs from the quantity it proxies —
   Italy's differs in customer class, BT against MT, and in being a ratio of
   an average rather than a share of a population.
4. It carries an evidence tier below E0 and is never published as a
   measurement.
5. It is computed at the finest unit it can reach, and that unit is stated.
   Italy's reaches region and no finer: the records carry no `owner`, so the
   distributor is unknown, and no comune population, so the concentration
   class is unknown.
