# Amendment — I5 Thermal stress proxy (IEEE C57.91)

**Date:** 30 August 2026 · **Written:** 31 August 2026
**Weight:** 0.12 of component I
**Status:** the register has cited this document since `b894c0d1`. It did not
exist until now — the filename was set as a constant in
`scripts/ssi_derive_metric_I5.py` and propagated into 620,129 records'
`metric_derivations` before the document was written. That is a provenance
pointer to nothing, of exactly the class this audit exists to find, and it was
introduced by the audit. Recorded here rather than quietly backfilled.

---

## 1. Why absolute, where I3 is relative

I3 captures extreme **deviation** from the local seasonal norm and deliberately
scores a perfectly regular annual cycle at zero, because that is the local
climate. Chronic heat is therefore invisible to it.

I5 is the complement, and it is absolute. Insulation ageing is physics, not
convention: 40 °C ambient ages a transformer at the same rate in Tromsø as in
Athens. A hot country *should* score higher here.

The two orderings are nearly disjoint, which is the point — they are not the
same measurement twice:

| | ordering |
|---|---|
| I3 (deviation) | greece > finland > turkey > norway > japan |
| I5 (absolute) | mexico 0.81 > israel 0.78 > costa-rica 0.69 > australia 0.53 … greenland 0.06 |

`test_I5_and_I3_measure_different_things` asserts the non-redundancy directly:
a site with a large but perfectly regular annual cycle scores I3 = 0 and a
high I5.

## 2. The standard

IEEE C57.91, *Guide for Loading Mineral-Oil-Immersed Transformers*, cited by
the construct as I5's source ("Thermal stress proxy (ILVE C57.91)") and by
`ITALY_FACT_CARD.md` source #30 ("IEEE C57.91 / IEC 60076"). The corpus cites
the standard and gives no computation, which is why this amendment exists.

Ageing acceleration factor, C57.91 Annex A:

```
F_AA = exp( 15000/383 − 15000/(θ_H + 273) )
θ_H  = ambient + HOTSPOT_RISE
```

`θ_H` is the winding hot-spot temperature in °C. F_AA = 1.0 at the 110 °C
reference hot spot, above which insulation ages faster than nominal.

**HOTSPOT_RISE = 80 K** is C57.91's rise for a 65 °C-average-winding-rise
transformer at rated load (top-oil rise ≈ 55 K plus hot-spot-over-top-oil
≈ 25 K). This is verified rather than assumed: at 30 °C ambient it returns
**F_AA = 1.0000**, which *is* the standard's own reference point. A second test
asserts the Arrhenius doubling — a 116 °C hot spot ages ≈ 2× faster than 110 °C.

```
I5_raw = mean daily F_AA across all cached years
I5     = Method B over fleet P5/P95, NOT inverted
```

Source: ERA5-Land daily-maximum 2 m temperature, already cached in the repo.
Nothing was fetched.

## 3. Convention #7 declarations — read before citing this

1. **Loading is held constant at rated.** Real hot-spot rise scales with load
   squared, and load data is I7's subject. I5 is a *climate-driven* thermal
   stress proxy with loading fixed — which is what the construct calls it, a
   proxy. A half-loaded substation ages far more slowly than this says; an
   overloaded one, far faster.
2. **Daily maximum, not daily mean.** The cache holds daily max, so F_AA is
   evaluated at each day's peak. This overstates absolute ageing rate against a
   full diurnal integration, consistently in every country. It is the standard
   worst-case convention and it preserves ranking, which is what Method B
   consumes.
3. **Within a country, I5 ranks substations exactly as mean ambient temperature
   would.** F_AA is a fixed monotone function of temperature, so the ordering
   carries no information beyond ambient temperature. What C57.91 adds is a
   physically grounded, interpretable scale — relative insulation ageing rate —
   and a non-linearity that changes the spacing, not the order. Stated because
   the opposite impression would be easy to give.

## 4. Sea cells

ERA5-Land holds no data over sea. A coastal substation snaps to an all-NaN cell
whose mean is NaN — or, summed, a `0.0` that is finite, plausible and false.
The land mask, cell resolution and contiguous-band reader are imported from the
I3 module rather than reimplemented; before those guards existed the same trap
would have handed a manufactured zero to 900 of norway's 6,113 substations.

A substation on a sea cell snaps to the nearest land cell within 3 cells
(~33 km); beyond that it is skipped and counted, never defaulted.

## 5. Coverage

620,129 of 622,104 substations (99.68%), all 39 countries. Skipped per
Convention #56: spain 818 (islands outside the cached grid), us 870,
france 153, portugal 91, uk 32, canada 5, estonia 2, new-zealand 1.

## 6. Where this belongs

**This document is a stopgap.** Per the flag officer, 31 August 2026: the
standard supplies the computation, and the *formula construct* is where it
becomes doctrine — cascading to the technical appendix and the foundational
documents. I3, I4, I5 and I6 are all currently defined in loose amendment files
beside the construct rather than inside it, and the construct defines the
computation of none of them.

Folding them in is the next task. This file exists so the register's citation
resolves in the meantime.
