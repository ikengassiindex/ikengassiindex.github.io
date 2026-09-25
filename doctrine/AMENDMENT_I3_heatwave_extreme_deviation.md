# Amendment — I3 Heat-wave IRI as extreme deviation

**Date:** 30 August 2026 · **Pinned by:** flag officer, *"we aim to capture
extreme deviations"* · **Weight:** 0.15 of component I, the largest single
I-metric

---

## 1. Why a deviation and not a temperature

Infrastructure is designed to local norms, so a departure **from those norms**
is what exceeds design assumptions. A Norwegian substation built for Norwegian
conditions is stressed by a Norwegian extreme much as a Greek one is by a Greek
extreme. This is also the standard climatological definition of a heat wave
(Perkins & Alexander 2013; WMO): local percentile exceedance, not an absolute
threshold.

The absolute alternative was measured and rejected on evidence. At 30/33/35 °C
every Norwegian and Finnish substation scores **0 days**, so P5 = P95 and
Method B correctly declines to normalise — I3 would have been *undefined* for
those fleets rather than merely low.

## 2. Definition

| | |
|---|---|
| baseline | per grid cell, the 90th percentile of daily-max 2 m temperature for each **pentad of the calendar year**, pooled across all years over a ±1-pentad window (~75 samples per bin) |
| heat day | daily max above that day's baseline |
| heat wave | a run of **≥ 3 consecutive** heat days |
| `I3_raw` | mean annual cumulative excess in **°C·days**, summed over days inside heat waves only |
| `I3` | Method B over fleet P5/P95, **not inverted** — more excess is more risk |

Source: ERA5-Land daily-maximum 2 m temperature, **already cached in the repo**
(`scripts/pipeline/.cache/`, 193 files, 2.58 GB, all 39 countries, 2018–2022).
Nothing was fetched.

## 3. Two traps, both measured before the code was written

**Frequency is degenerate by construction.** With the threshold at the p90 of
the same data, ~10% of days exceed it *everywhere by definition*. Measured: the
exceedance count is capped at **0–37 days/yr in every country**, carrying almost
no spatial signal. Hence magnitude, not count.

**A whole-year baseline measures climate variability, not extremeness.** With
p90 over the full year the seasonal cycle dominates, and the median excess
ranked:

| | °C·days/yr (whole-year baseline) |
|---|---|
| finland | 106.1 |
| norway | 95.3 |
| greece | 65.2 |
| turkey | 51.4 |

It made **Finland the most heat-exposed country in the register.**
Standardising by the annual σ did not fix it (norway 11.6 σ-days vs greece 8.1)
because σ is itself dominated by the seasonal swing. The calendar-day baseline
does fix it:

| | °C·days/yr (pentad baseline) |
|---|---|
| greece | 29.0 |
| finland | 23.5 |
| turkey | 22.9 |
| norway | 22.8 |
| japan | 14.1 |

## 4. A defect the first implementation had

ERA5-Land holds **no data over sea**. A coastal substation snaps to an all-NaN
cell whose sum is `0.0` — finite, plausible and false. Before the land-mask
guard: greece 60 of 719 (8.3%), japan 498 of 6,168 (8.1%), **norway 900 of
6,113 (14.7%)** would have received a manufactured zero, and with P5 also 0 it
would have read as a real measurement.

Now a substation on a sea cell snaps to the nearest **land** cell within 3 cells
(~33 km); beyond that it is skipped and counted, never defaulted.

## 5. Convention #7 declaration — the baseline is short

Standard practice builds a heat-wave climatology from 30 years. This has five
(luxembourg and slovenia: four). Two consequences, declared rather than hidden:

- the p90 per pentad rests on ~75 samples and carries sampling error
- the same period defines the baseline **and** measures the exceedance, so this
  is a **within-period** extremeness measure, not an anomaly against an
  independent climatology

Sound for ranking substations against each other, which is what Method B needs.
**Not a climate-trend statement and must not be read as one.**

## 6. The boundary of what I3 measures

An event that recurs *identically* every year scores **zero** — it is the local
norm. I3 captures irregular excursions, not chronic heat. A substation that
sees the same August every year registers nothing here. This is asserted in
`test_an_event_that_recurs_identically_every_year_IS_the_climatology`, because
it is a property to know about rather than discover later.

## 7. Coverage

**620,129 of 622,104 substations (99.68%), all 39 countries** — higher than
I4/I6 at 99.27%, since I3 needs no voltage pin.

Skipped, per Convention #56: spain 818 (islands outside the cached grid),
us 870, france 153, uk 32, canada 5, estonia 2, new-zealand 1.
Snapped to a land cell: 5,761 france, 4,993 uk, 2,564 italy, 885 spain,
819 us, 663 germany, and smaller counts elsewhere.

## 8. What this does not do

`components.I` is unchanged. I is nine metrics; three are now real
(I3 0.15 + I4 0.12 + I6 0.12 = **0.39 of 1.00**). The `enrich_esg_gaps` fill
stays until all nine are. No published score moves.

Gates: R_base DRIFT +0 · CI coherence all six +0 · published counts 39/39.
Tests: 7/7.
