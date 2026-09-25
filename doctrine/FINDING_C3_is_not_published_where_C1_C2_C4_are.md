# FINDING — C3 is not published where C1, C2 and C4 are

**Date** 25 September 2026
**Occasion** The operator directed that C3, absent for Italy, be obtained by
mosaic — taking another jurisdiction's methodology and applying it, disclosed.
That required a donor publishing all four C metrics sub-nationally, so the
relationship between C3 and the others could be fitted cross-sectionally and
carried across. This is the search for that donor.
**Measured on** the published output of four regulators, read at source.
**Status** measurement only. Nothing published was changed.

## The result

```
                C1                 C2        C3                        C4
  italy    ✓ DSO×conc×region       ✓         ✗ collected, withheld     ✓ province
  norway   ✓ fylke / nettselskap   ✓         ✗ no such metric          ✓ varsla split
  spain    ✓ municipio × zona      ✓         ✗ not published           ✓ programado
  france     national only      national     ✓ 94 départements         national only
```

C3 is published sub-nationally in one of the four jurisdictions checked. That
one publishes nothing else sub-nationally. Every jurisdiction that publishes
C1, C2 and C4 withholds C3.

## The evidence, per jurisdiction

**Italy.** ARERA's comparative publication carries six columns and no MV
exceedance; E-Distribuzione's Rapporto annuale degli output carries sections a
to h and none of them is one either. The quantity exists: ARERA's annual
continuity data collection requires, at §7, *"Numero di utenti MT con un
numero di interruzioni oltre lo standard"*, per ambito territoriale — the same
unit as the D1L and N1L tables. It is collected and not disclosed.

**Norway.** RME's external documentation of the avbrotsstatistikk states the
units — national, nettselskap, fylke, sluttbrukargruppe — the threshold
(*kortvarige* ≤ 3 minutes, *langvarige* > 3 minutes) and the planned split
(*varsla* against *ikkje-varsla*). It carries no regulated-breach metric.

**Spain.** MITECO publishes TIEPI and NIEPI at national, autonomous community,
province and *municipio* crossed with zone — urbana, semiurbana, rural
concentrada, rural dispersa — with programmed distinguished from unplanned.
There are no published measures of the number or share of customers exceeding
the individual quality limits. The limits themselves exist, in Orden
ECO/797/2002. The exceedance data does not.

**France.** Enedis publishes the *Indicateur réglementaire continuité
d'alimentation* — the share of a département's HTA and BT customers outside
the regulatory standard — for 94 départements since 2009. Critère B and the
coupure frequency it publishes nationally only, 18 records each.

## Why this is structural and not a gap in searching

C1, C2 and C4 are **fleet-performance** statistics: what the average customer
experienced, aggregated over a territory. C3 is a **compliance** statistic: how
many individual customers fell outside a guaranteed standard.

They are produced by different regulatory instruments. Performance statistics
come from continuity reporting obligations and feed benchmarking and
output-based regulation. Exceedance counts come from individual-guarantee
schemes and feed indemnity payments. A regulator running an indemnity scheme
computes the second and need not publish the first at fine grain; a regulator
running output-based benchmarking computes the first and need not publish the
second at all.

France is the clean case: it publishes the compliance statistic per département
because the regulated indemnity is administered there, and publishes the
performance statistics only nationally because that is where the benchmark
lives.

## What it does to the transfer

A transfer needs C3 and C1, C2, C4 **at the same units in the same
jurisdiction**, so that the cross-sectional relationship can be estimated and
then applied elsewhere. No such overlap exists in four jurisdictions.

France cannot donate to Italy, because France has no sub-national C1, C2 or C4
for its C3 to be fitted against. Eighteen national annual points are a time
series, not a cross-section, and a time series of one country cannot identify
how C3 varies between places.

The mosaic has nothing to bridge with. Not because the bridge was not looked
for, but because the two banks are in different jurisdictions.

## What it licenses

This converts the position from *"C3 could not be obtained"* to *"C3 is not
published at the required unit in four of four jurisdictions checked, for a
stated structural reason"*. That is what makes a declared renormalisation an
amendment with a finding behind it rather than a convenience.

The arithmetic, should it be pinned:

```
  INTRA_WEIGHTS["C"] = {C1 0.40, C2 0.30, C3 0.15, C4 0.15}

  with C3 absent and the remainder renormalised over 0.85

      C1  0.470588    C2  0.352941    C4  0.176471      sum 1.000000
```

**What that assumes, stated.** Renormalising is not the same as letting C3
contribute zero — that is M-046 and it biases downward. But it is not free
either. It assumes C3's normalised value, had it been published, would equal
the weighted mean of the other three's normalised values. That is a
declaration about an unobserved quantity and it must carry an evidence tier
below the measured inputs it sits among. It is defensible precisely because
the alternative — a hash — asserts far more with far less.

## What is not established

Thirty-five jurisdictions are unchecked. Four of four is evidence and a
mechanism, not proof; a regulator somewhere may publish both sets at a common
unit, and if one is found the transfer becomes possible again and this finding
should be revisited rather than cited.

Whether ARERA would disclose the Italian exceedance counts on request is
unknown and untried. They are collected, per ambito, and that is the shortest
route to a measured C3 anywhere in the estate.

## What it points at next

Spain. TIEPI and NIEPI at *municipio* crossed with zone is the finest unit
located in any jurisdiction so far, programmed is separated from unplanned, the
files are CSV and Excel for all years under the public-sector reuse initiative,
and Spain's 12,438 substations would join at a unit far below the province.
Norway is second: the data is equally good but has no API, and the published
annual reports stop at 2018.

## Sources read

```
arera.it      dati-e-statistiche/dettaglio/prestazioni-delle-imprese-
              distributrici-continuita-del-servizio-23
arera.it      fileadmin/allegati/operatori/raccolte_dati/manuali/2024/
              ContinuitaEE24.pdf
e-distribuzione.it  Rapporto annuale degli output 2025, 30/06/2025
nve.no        media/20400/ekstern-dokumentasjon-avbrotsstatistikken.pdf
nve.no        reguleringsmyndigheten/publikasjoner-og-data/statistikk/
              avbrotsstatistikk/
miteco.gob.es energia/energia-electrica/electricidad/calidad-servicio/
              indices.html
opendata.enedis.fr  datasets/indicateur-continuite-dalimentation/
```
