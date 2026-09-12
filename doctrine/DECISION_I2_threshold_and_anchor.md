# DECISION — I2's threshold and anchor

**Status:** PINNED by the operator, 12 September 2026
**Coefficients:** `GUST_THRESHOLD = 25.0` m/s · `ANCHOR = 45.3363` m/s-days
**Depends on:** `RESULT_I2_cerra_archive_complete.md`,
`FINDING_cerra_leadtime_and_temporal_sampling.md`,
`RESULT_I2_mosaic_test_1_FAILED.md`, `_test_2_FAILED.md`

---

## 1. What is being pinned

    gust(d) = daily maximum 10 m wind gust at the unit's CERRA cell,  m/s
    I2_raw  = mean annual sum over days of max(0, gust(d) - 25.0)     m/s-days
    I2      = 0.30 x min(1, I2_raw / 45.3363)

Five complete years, 2018–2022, 513,554 substations inside the CERRA domain.
I2 is **ABSENT** for the other 108,550 — not estimated, not interpolated.

## 2. The threshold is a declared reference level, not a damage onset

**This is the load-bearing statement of this document.**

Pin 14 requires a coefficient to be verified against a primary or secondary
source. The search for a damage-onset threshold did not produce one — it
produced the evidence that none exists in this range.

| asset | median failure wind (PNNL fragility compilation) |
|---|---|
| wood utility poles | ~40 m/s |
| transmission conductors | ~50–60 m/s |
| transmission towers | ~60 m/s |

Against this fleet's five-year annual maximum gust:

| P50 | P99.9 | P100 |
|---|---|---|
| 24.04 | 33.61 | **40.75 m/s** |

**The windiest substation of 513,554 barely reaches the median failure speed
of the weakest asset class.** Direct structural failure essentially does not
occur at the gust speeds this fleet experiences.

The outage literature agrees from the other direction. Studies of
extratropical-storm outages settle on ~15 m/s, justified by *forest* damage —
a vegetation-mediated mechanism. I2 excludes vegetation by construction.

So the mechanism that actually causes wind outages at these speeds is one this
metric does not model, and the mechanism this metric does model does not
operate at these speeds. **I2 is a wind EXPOSURE metric — a ranking of
accumulated high-wind loading — and it is not a damage model.** Any reading of
it as a probability of failure is a misreading, and the limitation must say so.

Pin 14 is satisfied not by sourcing the number but by sourcing the reason the
number cannot be a physical claim.

## 3. Why 25.0 and not 26.0

The threshold response, measured at 1 m/s spacing, falls most steeply at
**26 m/s** — 13.9 per cent of the fleet crosses per 1 m/s there.

That is a reason to avoid it, not to choose it:

- the inflection is a property of **this fleet's distribution**, not of wind or
  steel. Pinning there optimises how far apart our own substations sit, which
  is a ranking choice wearing the costume of a physical one.
- it is the point of **maximum sensitivity**. A 1 m/s shift in the underlying
  data moves ~13.9 per cent of the fleet at 26, against ~10.6 at 25. For a
  metric that will be re-derived as the archive extends, sitting on the
  steepest point is a liability.

25.0 sits on the shoulder: **74.1 per cent of the fleet scores**, a quarter is
genuinely unexposed, and the number is an order of magnitude below the weakest
structural median, which makes "exposure, not damage" legible from the value
itself.

**Declared:** the 1 m/s grid was run *after* seeing the 2.5 m/s grid, because
the coarse curve pointed at that band. That is a sampling decision taken after
looking, and it is recorded as such. The data does not constrain the grid —
the field carries ~450,000 distinct values per day with a median gap of
6 x 10^-5 m/s, so any threshold was available.

**Judgement, not evidence:** the evidence constrains a *range* — not below
~20 where nearly everything scores, not above ~32 where almost nothing does,
and never a damage claim. It does not single out 25.0 over 24.0. Choosing a
round number on the shoulder is a preference, and it is declared as one.

## 4. The anchor is the frozen P99.9 of the fleet

`ANCHOR = 45.3363` m/s-days, the P99.9 of I2_raw at this threshold, frozen at
the moment of pinning. **503 of 513,554 records (0.098%) saturate at
IRI_TOP = 0.30**, against I1's 628 of 622,079 (0.101%).

The same construction as I1's anchor (0.9029 m SWE, P99.9, frozen
9 September). That consistency is the reason for the choice:

| anchor | value | saturated | distinct published I2 values |
|---|---|---|---|
| P99.5 | 21.445 | 2,568 | **10,834** |
| **P99.9** | **45.336** | **531** | **7,395** |
| P99.99 | 93.154 | 61 | 4,869 |

A correction is recorded here. It was argued during the decision that
information preservation favours a *higher* anchor, because fewer records
saturate. **That was wrong**, and the measurement shows the opposite: a larger
divisor pushes the bulk of the fleet toward zero, where rounding to five
decimal places collapses records together. P99.99 saves 478 records from
saturation and costs roughly 2,500 their distinguishability elsewhere. It is
the *least* resolving of the three.

By resolving power alone the answer would be **P99.5**. It was not chosen
because 0.30 is already frozen at P99.9 in I1, and a metric-specific anchoring
convention would mean the I-axis aggregates two different scales as though
they were one — a silent defect of exactly the kind this estate removes. The
price is 3,439 distinct values out of 513,554 records, paid knowingly.

The anchor is **not a physical constant.** It is a declared fleet percentile
and the limitation must say so, as I1's does.

## 5. Measured consequence

**No published R score changes.** `_<C>_from_metrics` and `_<C>_coverage` are
diagnostic fields the engine does not read — the 31 August decision to publish
alongside and rebuild only when coverage is complete. I2 moves the shadow, not
the score.

| | |
|---|---|
| mean `_I_coverage` before | 0.6286 |
| after | **0.7029** (+0.0743) |
| records whose coverage rises | 513,554 |
| records unchanged | 108,550 |

I2 carries 0.09 of component I's intra-weight.

**A new heterogeneity, declared:** coverage is now geographically uneven.
Substations inside the CERRA domain reach 0.72; the rest stay at 0.63. When
components are eventually rebuilt from metrics, those two groups would be
built on different fractions of the definition. That is a direct consequence
of option D and it belongs in the comparability caveat of any cross-country
reading of the I axis.

## 6. Carried into the limitation

1. **Exposure, not damage.** Structural failure medians are 40–60 m/s; this
   fleet's five-year maximum is 40.75 m/s at one substation.
2. **Vegetation is absent**, and vegetation is the mechanism that causes wind
   outages at these speeds.
3. **108,550 substations have no I2**, and coverage of the I axis is uneven
   between them and the rest.
4. **One archive hour is missing** — 2021-04-01 01:00–02:00 UTC — so that day's
   maximum is a lower bound at every cell. Measured effect: 1 April is the
   2021 annual maximum at 5 cells of 61,377 and contributes 0.006–0.05 per
   cent of that year's exceedance sum.
5. **Five years is a short baseline** for a maximum-based quantity
   (Convention #7), and CERRA's gust is a model field, not an observation.
6. **8.4 substations share each occupied 5.5 km cell**, so neighbours within a
   cell receive identical values.
