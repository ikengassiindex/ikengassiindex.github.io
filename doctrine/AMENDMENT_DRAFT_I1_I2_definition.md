# Amendment (DRAFT) — I1 and I2, defined

Status: DRAFT for the operator's pin. Not registered, nothing derived.
Raised: 2026-08-31. Follows the component-I decision, which made the case
for closing the metric gap rather than rebuilding at half coverage.

---

## 1. The position

The construct names both metrics and weights them, and defines neither:

    I1  Snow/Ice risk    intra 0.12    Method C, bounded [0, 0.30]
    I2  Tree-fall risk   intra 0.09    Method C, bounded [0, 0.30]

Neither exists on any record. Together they are **0.21 of component I's
intra-weight** — the difference between 0.509 coverage today and **0.719**
once both land. That is the largest single step available toward rebuilding
component I from its own metrics.

This is the same position I3 was in on 30 August: a named metric, a weight, a
source family, and no computation. It is closed the same way — by writing the
computation first, then fetching to it, rather than fetching and retrofitting
a definition to whatever arrives.

## 2. What the fetch actually provides

`ERA5_FETCH_PLAN_I1_I2.json` — 59 boxes, 3 request sets, 177 requests,
2018–2022, `derived-era5-land-daily-statistics`:

    dmax   10m_u_component_of_wind · 10m_v_component_of_wind ·
           snow_depth · 2m_temperature
    dmin   2m_temperature
    dmean  2m_temperature · 2m_dewpoint_temperature      (I8)

The local cache holds `t2m` only — 193 files, daily maximum, which is what I3
and I5 were built from. **Snow depth and wind are not cached and must be
fetched.** Nothing here can be derived from what is on disk.

## 3. I1 — snow and ice loading

**What it measures.** The structural load that snow and ice place on the
asset and its spans. This is a load quantity, not a frequency: ISO 12494
(*Atmospheric icing of structures*) and the overhead-line design criteria in
IEC 60826 both treat ice and snow as design loads with return periods, not as
counts of cold days.

**Definition.**

    I1_raw(s) = mean over years of ( annual maximum snow water equivalent
                at the substation's grid cell, in metres )

One quantity, one field, no weighted composite of units that do not share a
unit.

**Why not a cold-days count.** Because the estate already has one. R6e_winter
is defined as `0.55 × ERA5_tmin_p1_freq + 0.25 × snow_days + 0.20 ×
ice_storm_proxy` — a frequency-based winter modifier. An I1 built on cold-day
frequency would put the same signal into the index twice, once as a metric and
once as a multiplier. I1 takes the load; R6e keeps the frequency.

**What it does not capture.** Glaze and freezing rain — the icing mechanism
ISO 12494 is most concerned with — need precipitation phase, which is not in
the fetch. I1 is therefore a snow-load metric with an ice-load gap, and must
be declared as one. Adding `total_precipitation` to the dmax set would close
it and is a fetch decision, not a definitional one.

## 4. I2 — wind

**What it measures.** The wind driver of tree-fall and span failure.

**Definition.**

    speed(d) = sqrt( u10(d)² + v10(d)² )        daily maximum, m/s
    I2_raw(s) = mean annual sum over days of max(0, speed(d) − GALE)
                in m/s-days, at the substation's grid cell

with `GALE` pinned at the Beaufort 8 threshold, 17.2 m/s — an absolute
engineering threshold, not a local percentile. Unlike I3, where the pin was
*extreme deviation from the local norm*, wind loading is absolute: a 30 m/s
gust loads a conductor the same in Valparaíso as in Vestland.

**What it does not capture — and this is most of it.** Tree-fall is
vegetation × wind, and vegetation is not in the fetch. The construct's own
declared limitation already says so: *"Vegetation proximity is the dominant
driver and is not available at line level in open data."* So I2 as defined
here is the **wind half of a two-term hazard**, and the metric's limitation
must say that in those words rather than implying a tree-fall measurement.

If that is too weak to carry 0.09 of the component, the honest alternative is
to leave I2 unpopulated and take coverage to 0.629 on I1 alone. **That is a
real option and I would not argue against it.** Populating a metric with half
its mechanism is the failure this estate has spent the week correcting
elsewhere; the difference is that here it would be declared on the record from
the first day rather than discovered later.

## 5. Normalisation — Method C, and two more pins

Section 03 assigns I1 and I2 to `C_bounded` on [0, 0.30], as it does I3. Under
the decision of 31 August each therefore needs an anchor: a frozen raw value
that maps to the top of the IRI interval.

Neither anchor can be chosen before the data exists. The sequence is the same
one I3 followed:

1. fetch · 2. derive raw · 3. measure the fleet · 4. pin the anchor at the
99.9th percentile, frozen · 5. amend under §8 with the value · 6. re-derive.

The anchor is a declared judgement in both cases, revisable only by amendment
and only when the fleet saturates against it — a condition visible in the
published data.

## 6. Convention declarations

**#7 — the baseline is short.** Five years, 2018–2022, the same window as I3
and I5. For a *load* metric this bites harder than it does for a within-period
anomaly: an annual maximum over five years is a weak estimator of a design
load that engineering practice takes at a 50-year return period. I1 must be
read as five-year observed loading, not as a design load, and its limitation
must say so.

**#56 — refusals.** A country with fewer than four years is refused. A
substation off the grid or without coordinates is skipped and counted, never
defaulted. A sea cell is land-masked and snapped, as in I3 — the trap that
would otherwise have given 900 Norwegian records a manufactured zero.

## 7. What this does not settle

- **The fetch itself.** 177 requests against the CDS need the credential in
  `SSI_v4_2 Italy Pilot/pipeline-v4.2/.env`. I neither handle nor enter it;
  you run the fetch or authorise how it is sourced.
- **I2's viability**, per §4. That is a judgement about whether a
  declared-partial metric is better than an absent one.
- **Whether to add precipitation** to the dmax set to close I1's ice gap
  before spending the 177 requests, rather than after.

## 8. If pinned

Coverage on component I moves 0.509 → 0.719 with both, or → 0.629 with I1
alone. Neither changes a published score: `components.I` stays untouched until
coverage is complete, per the 31 August decision. What moves is
`_I_from_metrics` and the conformance row that now measures it.

Remaining after this: I7 (load stress), I8 (ISO 9223 corrosion — the dmean
set in the same fetch already carries its inputs), I9 (hydrogeological).
