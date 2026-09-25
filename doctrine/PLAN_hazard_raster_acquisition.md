# PLAN — acquiring the hazard rasters

**Date** 21 September 2026
**Status** plan. Nothing fetched, nothing derived.
**Unblocks** the additive/multiplicative reclassification deferred in
`judgement.yaml` — `R6d_wildfire`, `R6e_winter`, `R6c_flood` and the three
country-specific hazards — which cannot be settled while their inputs are a
hand-set national constant jittered by a name hash
(`FINDING_the_second_name_hash_generator.md`).
**Sequence** Pin 16: decide → acquire → measure → pin → derive. The definitions
below are DECIDE items and belong to the flag officer; nothing is fetched until
they are pinned.

---

## Reachability, checked not assumed

    cds.climate.copernicus.eu    HTTP 200      C3S, ERA5 — existing credential
    ewds.climate.copernicus.eu   HTTP 200      CEMS — SEPARATE credential needed
    data.jrc.ec.europa.eu        HTTP 200
    jeodpp.jrc.ec.europa.eu      HTTP 302
    ecmwf-datastores-client 0.5.3 and cdsapi both installed on the device VM

There is no `~/.cdsapirc`, so the client cannot self-authenticate from this
shell. Every fetch is run by the operator, as with CERRA. No credential is read
or handled here.

## Leg 1 — WILDFIRE. Settled source.

**`cems-fire-historical-v1`**, Copernicus Emergency Management Service, on the
Early Warning Data Store.

    coverage   GLOBAL — bbox [0, -90, 360, 90]
    period     1940-01-03 to 2026-09-18 (current to this week)
    variables  14, including the Canadian FWI system
    grid       0.25/0.25, 0.5/0.5, or original
    selectors  year / month / day, so one request = N years x one variable,
               N bounded by the measured cost limit (below)

**Why the ready-made index and not our own from ERA5.** The Fire Weather Index
is a nonlinear function of temperature, humidity, wind and precipitation.
The estate's own rule — *a nonlinear function of two or more variables cannot be
computed from their independently pre-aggregated marginals* — is what broke I2
and blocks I8. Computing FWI from separately aggregated ERA5 fields would
reproduce that defect exactly. ECMWF computes it from hourly fields; we take
theirs.

**Cost shape — MEASURED 21 September 2026, not assumed.** This paragraph
previously carried CERRA's limit of 400, which was never checked against this
dataset. `scripts/estimate_fire_fetch_cost.py --sweep` prices the request
server-side with nothing queued:

    1 year   cost   366.0   limit 3720.0   OK
    2 years  cost   731.0   limit 3720.0   OK
    5 years  cost  1827.0   limit 3720.0   OK
    10 years cost  3653.0   limit 3720.0   OK
    11 years cost  4018.0   limit 3720.0   OVER
    20 years cost  7305.0   limit 3720.0   OVER

Cost equals the exact day count — 366 for leap-year 2024, 731 for 2023+2024 —
so the rule *cost = variables x days, area does not enter* holds here to the
unit. The limit is 3720 units, not 400: **ten years fit in one request and
eleven do not.** See `RESULT_the_fire_fetch_is_18_requests_not_172.md`.

## Leg 2 — FLOOD. Settled source, and better than a time series.

**JRC Global River Flood Hazard Maps v2.1** (Baugh et al. 2024).

    version    2.1.2  (README last updated 12.01.2026; files 2025-12-18)
    coverage   global, EXCLUDING Greenland, Antarctica, basins < 500 km2
    resolution 3 arc seconds (~90 m), WGS84
    values     water depth in metres; 1 variable
    returns    10, 20, 50, 75, 100, 200, 500 years
    licence    README A02: "no restrictions, free and open Copernicus product"
    store      jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/CEMS-GLOFAS/flood_hazard/

**ROUTE RESOLVED 21 September 2026, and it was never blocked.** What refused
automated fetches was the *catalogue* host, `data.jrc.ec.europa.eu`. The data
itself is on a different host, `jeodpp.jrc.ec.europa.eu`, served as a plain open
directory index. Read there, in the operator's own browser, at his request:

    271 tiles, 10 deg x 10 deg, named ID<n>_<N|S><lat>_<E|W><lon>_RP<xxx>_depth.tif
    542 files per return period   = 271 tiles x (raw depth + reclassified)
      7 return periods            = 3,794 hazard files
    271 Permanent_WaterBodies + 271 Spurious_Depths
    tile_extents.geojson (88 KB) — the tile system, for spatial reference

**Two masks that are not optional.** `Permanent_WaterBodies` is what the hazard
maps are patched with; `Spurious_Depths` marks where depths above 10 m are
predicted in channels under 3,000 km2 at the 10-year return period, plus a 2 km
buffer. Without them a substation beside a lake reads as inundated and a
modelling artefact reads as hazard. The README also warns of boundary effects
between tiles and residual DEM issues.

**Take `_depth`, not `_reclass`.** The reclassified layer bins depth into
<1 m / 1-3 / 3-10 / >10. The estate needs the metres and can bin them itself;
taking the bins would discard precision we cannot recover.

**PRICED 21 September 2026 — 8.69 GB, measured by HEAD, nothing downloaded.**
`scripts/fetch_jrc_flood.py --size-only`, run on the Mac:

    RP10  1.05 GB · RP20 1.13 · RP50 1.21 · RP75 1.24 · RP100 1.26
    RP200 1.31 GB · RP500 1.36 · Permanent_WaterBodies 0.11 · Spurious_Depths 0.01
    105 files per folder, 115 tiles requested          TOTAL 8.69 GB

Against ~260 GB for fire and 1–2 TB for winter, the flood leg is the cheapest
of the three and the only one that can be held whole rather than streamed.

**The 577 assets with no flood data, named.** Ten of the 115 tiles do not exist
in the dataset — consistently across all seven return periods and both masks,
which is coherence, not a fetch failure. Every one is an island territory, and
that is exactly the exclusion the dataset documents ("small islands with river
basins smaller than 500 km2"):

    N30_W160  228  us          Hawaii
    S20_E50   107  france      Réunion / Mayotte
    N40_W30    83  portugal    Azores
    N40_W20    60  portugal    Madeira
    N20_W160   50  us          Hawaii, southern group
    N20_E140   25  us          Guam / Northern Marianas
    N70_W10    18  uk          Shetland
    N40_W40     5  portugal    Azores, western group
    S40_W180    1  new-zealand subantarctic

**577 of 622,104 — 0.093 %** — carry `R6c_flood` as DECLARED ABSENT under §7.5,
never defaulted. Add Greenland's 43, excluded by construction, and the declared
set is 620.

**THIS LEG IS THE ONE THAT CAN BE PER-ASSET.** At ~90 m the raster is finer
than substation spacing, so the 24.7x collapse in
`RESULT_a_raster_can_give_25165_values_not_622104.md` does NOT apply here. Fire
and winter cannot distinguish 147 French substations in one 28 km cell; flood
can. The contrast must be declared per record, not left for a reader to infer.

**Greenland gets no flood data.** The dataset excludes it by construction, so
43 assets carry R6c_flood as ABSENT, declared, never defaulted (§7.5).

**Citation correction.** The plan cited "Baugh et al. 2024". The README's own
R01 states the reference publication is *"An updated dataset of global and
European flood hazard maps ... Manuscript under preparation."* Under §7.6 an
unpublished manuscript cannot be cited as a paper. Cite the DATASET —
doi 10.2905/JRC.VD32YWG — and, for the method, Dottori et al. (2016),
*Advances in Water Resources* 94:87-102, which is published.

Flood exposure is a static property of a location, so a depth raster sampled at
each substation is the right shape — not GloFAS discharge, which is a time
series of river flow and would need routing to an asset. Different shape from
wildfire, and correct rather than inconsistent.

**Greenland is excluded from the dataset.** Its 43 substations take a declared
abstention on the I4 pattern, not a substituted value.

## Leg 3 — WINTER. Source available, DEFINITION MISSING.

ERA5 on the existing C3S credential covers the inputs. What it cannot supply is
the definition, and there isn't one.

**This should follow the I3 doctrine, which is already pinned:** *"we aim to
capture extreme deviations"* — a heat-wave is a departure from the local
seasonal norm, because infrastructure is designed to local norms. Winter hazard
has the identical structure. Oslo is built for cold and Madrid is not, so an
absolute sub-zero threshold measures latitude rather than risk.

Unresolved, and a decide item: whether winter hazard is cold persistence, ice
accretion, snow load, or cold-plus-wind compound. Each has a different ERA5
input set, and the compound forms run straight into the nonlinearity rule.

## The five decisions, resolved on the operator principle of 21 September 2026

> *"we seek the greatest level of granularity, in this case the largest
> available time series as per accepted conventions, no short cuts"*

Two of the five do not resolve the obvious way, and the reason is that the
convention and the cohort disagree.

### 1. Climatology period — TAKE THE WHOLE RECORD, normal on the WMO window

The record runs **1940-01-03 to 2026-09-18**. The WMO standard normal is a
30-year window, currently 1991–2020.

These are not competing answers, because they answer different questions. The
WMO convention governs how a NORMAL is defined; it does not cap what is held.
So:

- **fetch the full record**, 1940–2025, 86 complete years;
- **compute the operative exposure statistic on the 1991–2020 standard normal**,
  which is the citable convention;
- **retain the full series per asset**, so non-stationarity is measurable rather
  than assumed. A hazard index built on a 30-year window and silent about trend
  asserts stationarity it never tested.

**Cost.** CDS prices variables × days; area does not enter — confirmed to the
unit by the sweep above. The measured limit on this dataset is 3720 units, so
the fetch is **nine ten-year windows per variable**, not 86 single years:

    1940-1949  1950-1959  1960-1969  1970-1979  1980-1989
    1990-1999  2000-2009  2010-2019  2020-2025 (6 years, 2192 units)

**9 requests per variable, 18 in total**, queued together, ~24 h median latency
each. Latency is per request and independent of payload, so request COUNT is the
only lever: this is a ~10x reduction in wall-clock, from 172 queue slots to 18.
The 1991-2020 normal is not a fetch boundary — it is computed from the retained
series, so window edges need not align with it.

**ANSWERED 21 September 2026 — and the boundary is not 1979.** This paragraph
previously stood open. ECMWF's own documentation gives four observing-system
regimes, not two: no upper-air observations at all before the mid-1940s, no
satellite data before 1970, early satellite 1970–1978, the modern system from
1979. The 1940–1978 extension is **final and consolidated**; what is deprecated
is a different dataset, the preliminary 1950–1978 extension with its
over-intense tropical cyclones.

The two legs are not equally exposed. FWI's inputs are surface fields and are
lightly affected. FMICLIM tests **upper-air** structure at 925/850/700 hPa with
thresholds calibrated to tenths of a degree, and is directly affected for
roughly 1940–1945. Separately, the three Southern Hemisphere jurisdictions —
**Australia, New Zealand, Chile** — carry the caveat across their whole early
record, and Method B does *not* absorb it, because the problem is a change of
data character within one country's own series rather than a level difference
between countries.

**The record is still fetched in full.** Three consequences instead, none of
which costs a byte: every year carries an observing-system regime tag with the
per-asset series; the operative statistic stays on the 1991–2020 normal, which
lies wholly inside the modern regime; and no published trend crosses a regime
boundary without the tag shown. See
`FINDING_the_pre1979_boundary_is_not_1979.md`.

Still open on this point: whether the CEMS fire product inherits ERA5's regime
structure identically. The CEMS user guide is silent — I checked — and silence
is not confirmation.

### 2. FWI quantity — PER-COUNTRY PERCENTILE, not a fixed threshold

This is the one that looks like a shortcut and is the opposite.

The published EFFIS danger classes are:

    Low < 11.2 · Moderate 11.2–21.3 · High 21.3–38.0
    Very High 38.0–50.0 · Extreme 50.0–70.0 · Very Extreme > 70.0

**They are calibrated for Europe, the Middle East and North Africa.** EFFIS says
so: the classes give "a harmonized picture … throughout Europe, Middle East and
North Africa". The cohort includes the US, Canada, Japan, Korea, Australia, New
Zealand, Chile, Colombia, Costa Rica and Mexico, none of which is in that
domain. The CEMS user guide gives the same warning in general terms —
"interpretation guidelines may vary based on regional standards and operational
practices" — offering only that FWI above 30 is high and 50 is extreme "in many
places".

Applying a European threshold to Australia would measure the distance from
Europe, which is the error the estate already made with I3's absolute
temperature threshold and corrected by pinning **extreme deviation from the
local norm**, on the reasoning that infrastructure is designed to local norms.
Wildfire has the identical structure.

So the operative quantity is a **per-country percentile exceedance**, Method B,
as already used for I4, I5 and I6. The EFFIS class day-counts are computed and
published ALONGSIDE as a cross-check and for European comparability — both
retained per asset, one entering the modifier.

### 3. Flood return period — ALL SEVEN

Sample 10, 20, 50, 75, 100, 200 and 500 years at every substation and publish
every depth. It is the same tiles and the same pass, so the marginal cost is
nil, the granularity is maximal, and the choice of which period drives the
modifier becomes revisable without re-fetching. Pin one — 100-year is the
infrastructure convention — and keep the other six on the record.

### 4. Winter — RESOLVED on an open anchor, 21 September 2026

**Constraint set by the operator: only open public data sources.** That removes
ISO 12494:2017 (paywalled), and on checking it also removes the two obvious
alternatives — Makkonen 2000, *Phil. Trans. R. Soc. A* 358:2913, has no open
manuscript at the VTT portal, and the 2025 AMS *Winter Storm Severity Index*
paper returns 403. None could be cited under §7.6 in any case, since none can
be read.

**Anchor: Kämäräinen et al. (2017), "A method to estimate freezing rain
climatology from ERA-Interim reanalysis over Europe", NHESS 17:243–258.**
Fully open access, and read rather than cited from a title.

Its FMICLIM diagnostic tests the vertical structure directly:

    T2m below a cold-layer threshold                       (calibrated  0.09 °C)
    a moist warm melting layer above it                    (min −0.64 °C, RH ≥ 89%)
    minimum cold-layer depth                               (69 hPa)
    minimum precipitation rate                             (0.39 mm / 6 h)

    inputs: RH and T at 925 / 850 / 700 hPa, T2m, surface pressure,
            6-hourly precipitation

Every input exists in ERA5, which is open and global to 1940. The authors
anticipate exactly this use: *"New predictor data sets need to be tested when
available, for example the ERA-5 of the ECMWF."*

**Two conditions on using it, both load-bearing.**

*Regional calibration.* The thresholds are fitted over Europe and the paper
states no evaluation of transferability elsewhere. Identical to the EFFIS
situation, and it takes the identical remedy: the diagnostic supplies the
PHYSICS, and the operative exposure statistic is a per-country percentile under
Method B, not the European thresholds read as absolutes.

*The nonlinearity rule, at full force.* FMICLIM is a conditional test across
four co-temporal fields. It CANNOT be evaluated from independently
pre-aggregated marginals — that is exactly the defect that broke I2 and blocks
I8. It must be computed timestep by timestep on 6-hourly co-temporal data, then
aggregated. There is no cheap route.

**Cost — MEASURED 21 September 2026**, superseding the warning that stood here.
`scripts/estimate_winter_fetch_cost.py --sweep` prices both legs server-side and
bisects each boundary:

    reanalysis-era5-pressure-levels   2 vars x 3 levels x 4 times = 24 fields/day
        6 years  52 608  OK          7 years  61 368  OVER   limit  60 000
    reanalysis-era5-single-levels     3 vars x 4 times          = 12 fields/day
       27 years 118 344  OK         28 years 122 724  OVER   limit 121 000

So **15 + 4 = 19 requests** for 1940-2025 — against the fire leg's 18. In queue
terms the two legs are the same size, and the warning above was pointed at the
wrong quantity.

The cost model generalises from the fire result — but **not** as "fields", which
is how this paragraph first read. Measured on 21 September: **cost = the number
of SELECTOR COMBINATIONS** = days × times × variables × levels. Fire was the
case where times = levels = 1.

The distinction is load-bearing, not pedantic. Cost answers *"will the CDS
accept this?"*, **not** *"how much data will arrive?"* They coincide for
`reanalysis`, `ensemble_mean` and `ensemble_spread`, where one combination
returns one field. They do not for `ensemble_members`: the ensemble is
10-member, so the identical request delivers **ten times the volume at one
times the price**, and the cost limit gives no warning. Before any fetch,
multiply the selector count by the fields-per-combination of the chosen
`product_type`. See `RESULT_the_cost_model_counts_selectors_not_fields.md`.

The expense is real but it is VOLUME, not latency: 1 130 832 fields against the
fire leg's 62 824, eighteen times as much data at the same request count. That
makes the streaming sampler load-bearing rather than tidy, and makes further
request-count optimisation on this leg pointless. See
`RESULT_the_winter_fetch_is_priced.md`, including what is measured there and
what is only arithmetic.

### 4b. Drought — open source found incidentally

`derived-drought-historical-monthly` on the C3S CDS: **global, 1940 to present,
ERA5-derived**. This answers where `R6_drought` data would come from, if and
when its mechanism is resolved. It does not resolve the mechanism, which
remains the open question in `judgement.yaml`.

### 5. EWDS credential — operator action

Separate registration from the C3S credential already in `.env`. Nothing here
reads or handles it.

## Three things that are not one thing — operator correction, 21 September 2026

I raised an "inconsistency" here: that I5's IEEE C57.91 anchor and I8's ISO 9223
anchor might breach the open-only rule. **That was a category error**, corrected
by the operator: *"let's not mix data governance from data provenance."*

They are three separate tests and a source can pass one and fail another:

**GOVERNANCE — may we use and redistribute this?** A property of the DATA and
its licence. ERA5, `cems-fire-historical-v1` and the JRC flood maps all pass;
the JRC maps are explicitly "available without restriction on use or
distribution". This is the test the open-only rule sets, and it applies to
INPUTS, not to methods.

**PROVENANCE — can a reader trace a published number to its origin?** Pin 14.
Satisfied by naming the method and the data, and it is indifferent to price. A
paywalled standard is a perfectly good provenance anchor: it is versioned,
stable, and obtainable by anyone who wants to check. What fails provenance is a
value that traces to nothing — `vary(1.02, name, 0.015)` is the failure, not a
citation that costs money.

**READABILITY — have I actually read what I am citing?** Constitution §7.6. This
is a discipline on the author, not a property of the source.

So `I5` and `I8` are fine. IEEE C57.91 and ISO 9223 are methods, not data
sources; the data beneath them is ERA5 and is open. Nothing needs re-anchoring
and the question I raised is withdrawn.

And the real reason ISO 12494 could not anchor the winter metric was never its
price — **it was that I had not read it.** Kämäräinen et al. (2017) anchors it
instead because it is open, current, ERA5-ready and read, which satisfies all
three tests at once rather than only the first.

## What this does NOT do

It does not make the reclassification safe on its own. A real per-asset hazard
value replaces the hash, and only then does additive-versus-multiplicative
become a question about physics rather than about the arithmetic of an
arbitrary number. The coefficients `b`, `c`, `d` in `clip(1 + k·index)` are
separately unsourced and need their own Pin 14 basis.

## Order

Definitions pinned → EWDS credential → fire fetch queued by year → flood tiles
for substation extents → winter once defined → per-asset sampling → Method B
normalisation per country → THEN the composition question reopens.
