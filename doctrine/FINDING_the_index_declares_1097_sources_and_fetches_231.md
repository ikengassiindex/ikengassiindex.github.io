# FINDING — the index declares 1,097 sources and fetches 231

**Date** 24 September 2026
**Occasion** Asking what stands between the index and its stated purpose — the most complete index at the greatest granularity, built entirely on open data.
**Measured on** the deployed tree, 39 jurisdictions, by `SSI_ACQUISITION_MAP.py` and by direct field presence across 229,204 published records (first shard per country).
**Status** measurement only. Nothing published was changed.

## The metric layer

Of the twenty-one declared metrics, six carry a value on any published record.

```
  I1  100.00%     I4   99.39%        C1  C2  C3  C4      0.00%
  I2   78.70%     I5   99.60%        V1                  0.00%
  I3   99.60%     I6  100.00%        E1  E2              0.00%
                                     S1  S2  S3          0.00%
  I7  I8  I9       0.00%             T1  T2              0.00%
```

**All six are in component I.** `_I_from_metrics` is carried on 100 per cent of
records; `_C_`, `_V_`, `_E_`, `_S_` and `_T_from_metrics` on zero, because every
metric beneath those five sits on zero.

Component I is weighted 0.25 and its present metrics carry 0.720 of its declared
intra-weight, so **0.18 of `R_base` has any metric behind it** — and none of that
0.18 reaches a published score, because it lives in a shadow field beside the
name-hash fill. The published `R_base` is derived from measurement nowhere.

## Why those six and not the others

```
1,097 declared source rows across 39 jurisdictions

  connector                 96    8.8%   code fetches it, unattended
  connector_credentialed    81    7.4%   code fetches it, needs a key
  manual                    54    4.9%   no fetch path; a human step is documented
  declared_no_path         866   78.9%   named in the register; nothing retrieves
                                         it and nothing documents how
```

Per jurisdiction: france declares 35 and has no path for 28; japan 38 and 34;
ireland 35 and 30; chile 30 and 28; spain 35 and 28; switzerland 35 and 28;
turkey 31 and 29; united states 36 and 27. The best in the cohort — uk, hungary,
latvia, lithuania, slovakia, slovenia, israel, iceland, korea — still have
sixteen rows apiece with no route.

**The six metrics that exist are exactly the ones whose sources have
connectors**: `climate.py` to Copernicus CDS and Open-Meteo, `seismic.py` to the
GEM raster, Overpass for OSM, GHSL for catchment population. The metric layer is
not selective about doctrine. It is a map of where an executable fetch path
happens to exist.

*The instrument's own limit, restated here rather than buried: `declared_no_path`
means no acquisition route of any kind was found in the estate. An undocumented
one-off human download would look identical. That is the ceiling on this
reading, and it is the tool's, not this document's.*

## The blocked metrics are not blocked on open data

This document exists because the opposite was asserted in session and was wrong.
Reading the metric definitions — SAIDI, SAIFI, voltage-event severity,
unserved-energy cost, DER headroom, reverse power flow — and the identical
`blocked_on: no verifiable provenance in the deployed pipeline at the pinned
commit` on all fifteen, the conclusion drawn was that these quantities are not
open per asset and the definitions are therefore incompatible with the index's
open-data constraint. The operator rejected it and directed a reading of the
foundational documents. The foundational documents refute it.

Each jurisdiction's own source register names the feed. France:

```
CRE (Commission de Régulation de l'Énergie)   Département  →  C1–C4 (SAIDI/SAIFI)
ODRÉ Registre National · RTE · ENTSO-E                     →  T1 DER capacity, variability
Bpifrance Innovation                          Département  →  E2 innovation enrichment
Dimovski et al. (2025)                        Municipal    →  S1 breakpoints, calibration
EEA Air Quality e-Reporting · ISO 9223        ~1 km        →  I8 corrosion
BRGM Geological Survey                        Département  →  I9 hydrogeological risk
```

All open. All published on fixed cycles. And `normalisation_method` carries a
declared enum member built for precisely this shape — **`A_regulatory`** — which
C1, C2 and E1 all use: an aggregate regulatory series, normalised and allocated
to assets through the catchment, which is how an index of 622,104 substations
consumes a series published per operator or per department.

C1's own `upgrade_path` says it plainly: *"National regulators publish these
series on fixed cycles; a per-country ingest can replace the normalised
placeholder."*

**The error was to read a definition and a blocker and infer a constraint,
without reading the source register that answers it.** It is the ninth instance
recorded in this estate of a conclusion drawn from one artefact where two were
needed, and the first in which the operator caught it rather than a measurement.

## What the gap actually is

It is an acquisition backlog, and it has a number: **866 rows**.

It is not a doctrine gap — the metrics are defined, the normalisation classes
exist, the sources are named per jurisdiction with publisher, cadence and
granularity.

It is not a weighting gap. The component weights were set against the index as
defined, from literature, academia and practice. Re-weighting to fit what is
currently fetched would fit doctrine to an ingest backlog, which Constitution 1
forbids in as many words: *"Where an implementation departs from it, the
implementation is defective and is corrected. Doctrine is never rewritten to
match what the machine happened to do."* Re-weighting becomes legitimate when a
specific source is proven unobtainable after being tried. That proof exists for
none of the 866.

It is not an openness gap. Every source above is open.

## Where the leverage is

```
C1  Outage duration (SAIDI)   intra 0.40  ┐  0.70 of component C
C2  Outage count (SAIFI)      intra 0.30  ┘  C weighted 0.30  =  0.21 of R_base
```

One ingest class — national regulator reliability series, plus CEER's
cross-country benchmarking for the European cohort — reaches 0.21 of `R_base`.
The normalisation class is declared, the limitation is already written
(*"comparable within a country and only indicatively so between countries"*),
and the upgrade path is already stated in doctrine. Nothing needs to be decided
before it can start.

That is larger than everything remaining in the R2 chain, and larger than the
component I rebuild it would follow.

## One thing this does not soften

The per-country methodology pages publish these source registers as they stand.
A reader of the France page sees thirty-five named institutions. Twenty-eight of
them are retrieved by nothing in the estate. Constitution §7.9: a declared
source is a claim and is subject to the same discipline as a measured value.

Nothing here is proposed and nothing was changed.

## Related

- `FINDING_what_the_components_fill_costs.md`
- `FINDING_the_chain_is_closed_and_the_residual_moved.md`
- `FINDING_the_name_hash_reaches_past_components.md`
- `FINDING_the_climate_chain_declares_what_it_never_derives.md`
- `DOCTRINE_a_check_must_read_the_artefact.md`
