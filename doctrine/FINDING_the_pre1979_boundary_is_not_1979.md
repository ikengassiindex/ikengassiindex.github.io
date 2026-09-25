# FINDING — the pre-1979 question is answered, and the boundary is not 1979

**Read** 21 September 2026. `PLAN_hazard_raster_acquisition.md` recorded this
as *"to verify before fetching, not asserted here … must be answered from
ERA5's own documentation before that portion is used in a published
statistic."* It is now answered, from the producer's own documentation, read
rather than cited from a title (§7.6).

Sources, both ECMWF, both open:

- **Copernicus Knowledge Base, *ERA5: data documentation*** (ECMWF Confluence).
- **ECMWF Newsletter 175, *ERA5 reanalysis now available from 1940***.

## 1. "Preliminary" is not the objection

The 1940–1978 back extension is the **final, consolidated** version. What is
deprecated is a *different* dataset — the preliminary 1950–1978 extension,
which "did suffer from excessively intense tropical cyclones". The newsletter
puts it plainly: the current extension "replaces a preliminary extension back
to 1950 that was characterised by sub-optimal tropical cyclone properties."

So the early record is not provisional, and the concern that motivated the
question does not apply in the form it was asked.

## 2. The boundary is not 1979 — there are three regimes, not two

The estate had been carrying the conventional shorthand *pre-1979 = pre-satellite*.
ECMWF's own statement is more specific, and differs:

> "In ERA5, no satellite data were used before 1970. The in-situ observing
> system was sparse over the southern hemisphere, and before the mid-1940s no
> upper-air observations were available."

That gives four periods, not the two the plan assumed:

    1940 – mid-1940s   no upper-air observations at all
    mid-1940s – 1970   upper-air, no satellite
    1970 – 1978        early satellite
    1979 – 2025        the modern observing system

ECMWF's positive claim is scoped accordingly: "From 1940 ERA5 should provide a
good estimate of the actual synoptic situation **for large regions over the
northern hemisphere**."

## 3. What this does to each leg — they are NOT affected equally

**Fire (FWI / DSR) — lightly exposed.** The Canadian FWI system's inputs are
surface quantities: temperature, relative humidity, wind and precipitation at
the surface. These are the fields the in-situ network constrains best and
earliest. The upper-air gap does not bear on them directly.

**Winter (FMICLIM) — directly exposed, and at the worst possible place.**
FMICLIM is a test of *vertical structure*: relative humidity and temperature at
925, 850 and 700 hPa. Those are upper-air fields. ECMWF states that **before
the mid-1940s no upper-air observations were available**, so for roughly
1940–1945 the three levels the diagnostic interrogates are model fields with no
upper-air observational constraint over them.

This matters more than a general "uncertainty is larger" caveat, because of the
diagnostic's own calibration. Kämäräinen et al. fit their thresholds to
**0.09 °C**, **−0.64 °C**, 89 % RH and 69 hPa. Those are tenths of a degree. A
conditional test calibrated to tenths, evaluated on fields with no observations
above the surface, is not measuring what its calibration assumes it is
measuring. ECMWF notes the same period exposes "a model cold bias in the lower
stratosphere", and that "agreement is much better from the mid- to late-1940s
onwards".

## 4. The Southern Hemisphere problem, and why Method B does not solve it

Three of the 39 jurisdictions are Southern Hemisphere: **Australia, New Zealand
and Chile.** For those, the caveat is not about a handful of early years but
about the whole early record — "the in-situ observing system was sparse over
the southern hemisphere", and Soci et al. (2024) put it that over the Southern
Hemisphere the early-period description "seems mainly statistical".

Method B — per-country percentiles — is the estate's usual answer to a
cross-country comparability problem, and it does **not** answer this one. Method
B normalises each country against itself, so it absorbs a *level* difference
between countries. What it cannot absorb is a change in data character *within*
one country's own record. If Chile's 1940s are effectively model climatology and
its 2010s are observationally constrained, the country's own percentile
distribution is built from two different kinds of quantity.

And that lands precisely on the use the plan gives as the reason for holding the
full series: *"retain the full series per asset, so non-stationarity is
measurable rather than assumed."* A trend fitted across 1940–2025 in such a
country measures the **observing system** at least as much as the climate. The
plan's stated defence against assuming stationarity would, unguarded,
manufacture a trend.

## 5. Recommendation — fetch it all, and carry the regime with it

Do **not** shorten the record. The standing principle is greatest granularity
and the largest available series per accepted conventions, and nothing above
argues for discarding data; it argues for not silently mixing kinds of data.
Three changes instead, none of which cost a byte:

1. **Tag every year with its observing-system regime** (no-upper-air /
   pre-satellite / early-satellite / modern) and carry the tag with the
   per-asset series. An untagged 1943 value and an untagged 2013 value sitting
   in the same array is the defect; the values themselves are not.

2. **Keep the operative statistic on the 1991–2020 standard normal**, as already
   decided for the WMO convention. That window lies wholly inside the modern
   regime, so the published exposure statistic is untouched by any of this.
   This was decided for a different reason and turns out to protect against
   this one.

3. **No published trend may cross a regime boundary without showing the tag.**
   For Australia, New Zealand and Chile specifically, a 1940-onwards trend
   should not be published at all until it has been shown to survive
   restriction to the satellite era.

## 6. Still open

- Soci et al. (2024), *QJRMS* 150:4014 (CC BY 4.0) is the full technical account
  and the primary record for §3–§4 above. I have read ECMWF's own summaries of
  it, **not the paper itself** — Wiley returned 403 and the NOAA repository copy
  refused the direct fetch. It must be read before any of the quantitative
  claims in it are cited. Nothing above rests on it alone: every load-bearing
  quotation here is from the two ECMWF sources named at the top.
- Whether the CEMS fire product inherits ERA5's regime structure identically, or
  whether its own production introduced a different boundary, is not stated in
  what has been read.
