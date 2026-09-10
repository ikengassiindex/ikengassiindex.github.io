# Amendment (DRAFT) — I2 at the finest resolution each jurisdiction allows

Status: DRAFT for the operator's pin. Nothing derived. Raised 2026-09-10 on the
operator's direction: populate I2, at the most granular data available; where
Europe has finer data that is better, and mixed granularity across the estate
is not a conflict provided it is declared.

Supersedes the single-source assumption in the addendum of
AMENDMENT_DRAFT_I2_realisation_and_I8_warning.md. The gust DEFINITION there is
unchanged.

---

## 1. Why a second source at all

I2 on ERA5 gust at 0.25° is close to a regional constant. Measured on the
derived field:

    country        substations   distinct cells   CV      P5-P95 (m/s)
    france             168,780            1,138   0.096   23.2-30.5
    germany            108,016              850   0.113   22.4-33.0
    uk                  59,744              664   0.066   26.5-32.7
    italy               41,662              661   0.169   19.8-34.3

168,780 French substations share 1,138 values. The UK's entire fleet spans
6.2 m/s. A metric that assigns the same number to substations 20 km apart
cannot discriminate between them, and I2 exists to discriminate.

This is NOT a defect of the source choice. ERA5-Land does not help: its 10 m
wind is ERA5's 0.25° field interpolated to 0.1°, with local adjustments applied
only to relative humidity, temperature and pressure — see
FINDING_era5land_wind_is_interpolated.md. Nothing in the ERA5 family resolves
wind more finely. A finer source has to come from outside it.

## 2. CERRA — what is established, and how

    grid            1069 x 1069 at 5.5 km, Lambert Conformal Conic
    projection      central meridian 8°, standard parallels 50°, R 6371229 m
    period          1984 to present
    analyses        8 per day — 00, 03, 06, 09, 12, 15, 18, 21 UTC
    gust variable   10m_wind_gust_since_previous_post_processing, a 3-second
                    gust maximum over each output window. Eight windows tile
                    the day, so their maximum IS the true daily maximum gust.
    also carries    10m_wind_speed — a SCALAR speed variable, which ERA5
                    single levels does not offer at all

    cost            17,520 for one variable-year, all 8 times, full domain,
                    against a limit of 90,000. One request per variable-year
                    fits. Area is free here as on ERA5 (186.0 with or without
                    an area subset).

Measured, not assumed: the domain was reconstructed by projecting the
documented corner coordinates into the stated LCC and comparing against
1069 x 5.5 km. It agrees to within 5 km over 5,875 km.

## 3. Coverage — 82.6 per cent of the estate

Substations projected into the CERRA grid and tested against its extent:

    FULLY INSIDE (25 jurisdictions)
      austria belgium czechia denmark estonia finland germany greece hungary
      iceland ireland israel italy latvia lithuania luxembourg netherlands
      norway poland slovakia slovenia spain sweden switzerland uk

    PARTIAL (4)
      france     168,478 of 168,894  (99.8%)  — the 416 outside are overseas
      portugal    13,506 of  13,564  (99.6%)  — Azores and Madeira
      turkey       3,988 of   4,031  (98.9%)  — eastern Anatolia
      greenland       21 of      43  (48.8%)  — the western coast falls out

    OUTSIDE (10)
      australia canada chile colombia costa-rica japan korea mexico
      new-zealand us

    513,554 of 622,104 substations inside — 82.6 per cent.

The partials fall out for reasons that are correct rather than accidental, and
that is itself a check on the projection: France's excluded records are its
overseas territories, Portugal's are its Atlantic islands.

## 4. What is proposed

**I2 is derived from the finest source that covers each substation, and every
record declares which.**

    _I2_source        "cerra_5.5km" | "era5_0.25deg"
    _I2_resolution_km  5.5 | 31

    metrics.I2         one number, one definition, one threshold, one anchor

The DEFINITION does not change with the source: mean annual sum of
max(0, daily maximum 10 m gust − GUST_THRESHOLD). Only the field it is
evaluated on changes. That is what makes mixed granularity coherent rather than
a conflict — it is one metric measured with two instruments, each declared.

**What this does NOT resolve, and must be declared:** two substations in
different tiers are not equally resolved. A Norwegian unit at 5.5 km and a
Chilean one at 31 km carry the same metric on different evidence. The tier
field exists so that a reader can see that rather than infer it.

## 5. Open, and deliberately not decided here

**The fetch shape.** Cost allows one request per variable-year, but 1069 x 1069
x 8 x 365 is roughly 13 GB per variable-year uncompressed and what netCDF
compression does to a gust field is a guess. Every size estimate this estate
has made from arithmetic has been wrong — 8 GB predicted against 3.1 GB
actual, and 0.0105 MB/deg² wrong the other way. One month is being fetched and
measured before the plan is written. `scripts/probe_cerra_one_month.py`.

**Latency at this scale.** Queue latency was measured independent of payload
from 0.1 MB to 154 MB. CERRA requests are far beyond that range. The probe
measures it.

**The threshold.** Still unpinned, and now must be chosen on the CERRA field
rather than the ERA5 one — a finer field has a different distribution, and a
threshold fitted to 31 km cells would not carry over. The curve is re-derived
once CERRA data exists.

**Whether the finer field actually discriminates.** The expectation is that it
does: CERRA is a genuine 5.5 km atmospheric reanalysis, not an interpolation.
But that is an expectation, and the same expectation about ERA5-Land was wrong.
It is tested by re-measuring the within-country CV of section 1 on CERRA and
comparing. If the CV does not rise materially, the finer source buys nothing
and that must be reported rather than absorbed.

## 6. Code that does not yet exist

CERRA is curvilinear. `ssi_derive_metric_I2.py` resolves cells with
`np.abs(lat - la).argmin()` on 1-D axes, which is wrong for a 2-D projected
grid. Substation coordinates project into LCC and index directly, since the
grid is regular in projected space — but the projection must be READ FROM THE
FILE, not reconstructed from documentation. The reconstruction in section 2
agrees to 5 km and is good enough to plan with; it is not good enough to derive
620,000 published values from.
