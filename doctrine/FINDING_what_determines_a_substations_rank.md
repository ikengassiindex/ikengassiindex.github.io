# FINDING — what determines a substation's rank

**Date** 25 September 2026
**Occasion** A confidence tier that rose as measurement fell. The first two attempts to quantify the problem measured the wrong quantity; the operator asked whether the right thing was being measured, and it was not.
**Measured on** the deployed tree, 543,420 records carrying all six components, 37 countries.
**Status** measurement only. Nothing published was changed.

## The question, corrected twice

**First attempt — wrong quantity.** The width of the interval on absolute
`R_final`, letting absent and uninformative components range over `[0,1]`. It
gave a median width of 0.81 spanning four or five bands on 77.8 per cent of
records, and it was not the right measurement: the published output is a
**per-country percentile band**, and a component missing for every substation in
a country shifts them together. A common shift does not move a percentile. Italy
and Germany demonstrated exactly that — every score rose, the distribution
barely moved.

**Second attempt — wrong population.** A variance decomposition that attributed
71.9 per cent of rank variance to the name-hash fill across thirteen countries.
The fill does not reach thirteen countries.

```
C, V, E, S, T reproduce from vary(0.35, name + '_' + K, 0.30)

  france · germany · italy · japan · portugal · spain · us      100.0%
  uk                                                             92.9%
  the other 31 countries                                          0.0%
                                                    ESTATE       88.5%
```

The hash fill is concentrated in the eight largest jurisdictions. Elsewhere the
components come from somewhere else, at wildly varying granularity, and their
provenance is not established by this document or any other.

**The right quantity** is the share of the variance that decides a substation's
position within its own country — because that, and only that, is what the
published band reports.

## What decides it

```
estate-weighted share of rank variance, 543,420 records, 37 countries

   component C   weight 0.30    43.81%
   component I   weight 0.25    29.11%
   component S   weight 0.20    16.26%
   component V   weight 0.10     5.03%
   component E   weight 0.10     4.85%
   component T   weight 0.05     0.93%
```

**Component C decides more of the index than anything else, and its four metrics
sit on zero records in all 39 countries.** C1 outage duration, C2 outage count,
C3 MV exceedance rate, C4 planned outages — every one of them is `status:
blocked` in `judgement.yaml` and absent from every published record
(`FINDING_the_index_declares_1097_sources_and_fetches_231.md`). Whatever is in
`components.C`, it is not derived from C1–C4, because C1–C4 do not exist.

Component I is the only component with any metric behind it anywhere.

**So 29.11 per cent of what determines a substation's rank rests on measurement,
and 70.89 per cent rests on quantities with no metric layer beneath them.**

## And it is wildly uneven between countries

```
component I's share of rank variance, the thirteen rebuilt countries

   turkey     3.4%        slovakia   5.3%        uk        34.6%
   norway     3.5%        hungary   10.8%        spain     43.3%
   finland    3.7%        sweden    19.8%        france    45.5%
   israel     4.6%        germany   32.7%        italy     45.9%
                                                 portugal  54.9%
```

In Turkey, Norway, Finland and Israel, **the one component built from real
measurements decides under five per cent of the ranking.** The ERA5-Land,
CERRA, OSM, GHSL and GEM work of the last month reaches those countries'
published order almost not at all.

In Portugal it decides more than half.

A cross-jurisdiction index whose measured content drives 3.4 per cent of one
country's ranking and 54.9 per cent of another's is not comparing like with
like, and no weighting decision produced that spread — it is an artefact of
where the metric layer happens to exist.

## Dead weight

A component with one distinct value across a fleet contributes nothing to rank.
Its weight is inert.

```
   latvia        1,219 records   0.30 of weight dead   V(1), S(1)
   lithuania       505           0.30                  V(2), S(1)
   switzerland     947           0.30                  C(1)
   estonia         614           0.20                  S(1)
   hungary       3,502           0.20                  S(1)
   ireland         994           0.20                  S(1)
   norway        5,842           0.20                  S(1)
   slovakia      1,512           0.20                  S(1)
   turkey        4,001           0.10                  V(3)

   19,136 records
```

Switzerland's component C takes **one** distinct value across 947 substations
and contributes exactly 0.0 per cent of its rank variance: 0.30 of the weight,
the largest in the construct, doing nothing at all. Latvia and Lithuania each
carry 0.30 of inert weight, five countries carry 0.20.

The declared weights are not the operative weights. In Switzerland the operative
set is V, I, E, S and T renormalised; in Norway, Hungary, Slovakia, Estonia and
Ireland it is C, V, I, E and T. Nobody decided that.

## What this means for the confidence question

The tier is currently derived from Monte Carlo interval width, which
`FINDING_the_monte_carlo_never_sees_the_metrics.md` shows is computed from
component values with the real metrics never read. That is why it inverts —
fewer components, thinner interval, higher published confidence.

The honest basis is the quantity measured here: **the share of rank-determining
variance that rests on components with a metric layer beneath them.** It is
exact, computable today from the published tree, needs no Monte Carlo, applies
identically to an absent component and a fabricated one — both carry no
information about the asset — and it is per country, which is the scale the band
is computed at.

Today that quantity is 29.11 per cent estate-wide, 3.4 per cent in Turkey and
54.9 per cent in Portugal.

It also rises as sources are acquired, and by a calculable amount. C1 and C2
carry 0.70 of component C's intra-weight and C holds 43.81 per cent of rank
variance; giving them a metric layer would move more of this number than
everything done to the index this month.

## What is not established here

Where the 31 non-hash countries' C, V, E, S and T values come from. They are not
`vary(0.35, ...)`, their granularity ranges from one distinct value across 5,842
substations to near-fully distinct, and nothing in this estate records their
derivation. That is the next measurement and it is not made here.

Nothing is proposed. Recorded because the index's published order is decided
overwhelmingly by quantities that have no metric layer, and because the measured
content's contribution varies sixteen-fold between jurisdictions the index exists
to compare.

## Related

- `FINDING_the_monte_carlo_never_sees_the_metrics.md`
- `FINDING_the_name_hash_reaches_past_components.md`
- `FINDING_the_index_declares_1097_sources_and_fetches_231.md`
- `FINDING_what_the_components_fill_costs.md`
- `FINDING_the_unmeasured_set_the_band_for_the_measured.md`
