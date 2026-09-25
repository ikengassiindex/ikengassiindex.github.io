# LEAD — ERA5 carries a real uncertainty, and the estate is inventing one

> ## CORRECTION, 21 September 2026 — same day, after reading further
>
> **The central claim below is substantially weaker than written, and in one
> specific way it is wrong.** ECMWF's *ERA5: uncertainty estimation* page was
> read after this document was filed. It states that the ensemble spread
> **"MOSTLY account[s] for random errors and NOT for systematic ones"**, that
> it is **"generally under-dispersive, i.e. the spread is lower than the
> skill"**, and instructs users **"not [to] take the uncertainty values at face
> value."**
>
> This document argued that the spread would distinguish a poorly constrained
> 1943 field from a well constrained 2013 one, and so would carry the
> observing-system distinction that
> `FINDING_the_pre1979_boundary_is_not_1979.md` requires. **It would largely
> not.** The early-period defect that finding identifies is *systematic* — a
> model cold bias, and model climatology standing in where observations are
> absent — and systematic error is precisely what the spread does not capture.
> The two documents were written an hour apart and the second leaned on the
> first in a direction the first cannot support.
>
> Three further qualifications, all from the same page: the ensemble is
> **10 members at ~60 km and 3-hourly**, against the deterministic field's
> ~30 km and 1-hourly, so a 0.25° request returns interpolated coarse
> information; ten members give **"considerable sampling noise at individual
> times"**, so per-timestep spread is not usable as filed and ECMWF directs
> users to temporal averaging; and averaging it is not free of the
> nonlinearity rule either.
>
> **What survives.** The spread is still a real, observed, per-gridpoint
> quantity available at no extra cost, and still a better object than a name
> hash. It is a partial and under-dispersive measure of *random* uncertainty in
> hazard *inputs* — which is a narrower claim than this document made, and
> should be the claim carried forward.
>
> The anomaly flagged in item 2 below is resolved, and badly: see
> `RESULT_the_cost_model_counts_selectors_not_fields.md`. The cost model counts
> selector combinations, so `ensemble_members` delivers ten times the data at
> one times the price, and the cost limit gives no protection there.


**Status: a LEAD, not a result.** One thing below is measured; the rest is
unverified and is marked as such. It is recorded now because it bears on the
largest known defect in the estate and should not wait for the leg it was found
on.

## The defect it bears on

398,599 published records carry `R_P5 == R_P95` with `R_median` outside the
interval. `CI_width` is a name hash on 64.1 % of records. The estate publishes
confidence intervals that are not confidence intervals. That has been recorded
and not yet remedied, and the remedy has always looked like it would have to be
a Monte Carlo we seed properly — that is, an uncertainty we manufacture better.

## What was measured

Pricing the winter pressure-level request across ERA5 product types, 2024,
6-hourly, RH and T at 925/850/700:

    reanalysis         cost  8784.0   limit 60000.0   OK
    ensemble_mean      cost  8784.0   limit 60000.0   OK
    ensemble_spread    cost  8784.0   limit 60000.0   OK
    ensemble_members   cost  8784.0   limit 60000.0   OK

**`ensemble_spread` exists on the datasets this estate is about to fetch, and
prices the same as the deterministic field.** It is the spread of ECMWF's own
data assimilation ensemble: a per-gridpoint, per-timestep measure of how well
the observing system constrained that field at that place and time. ECMWF
describes the spread as "a measure of this uncertainty", "larger for time
periods and spatial locations where the uncertainty is relatively large."

That is an uncertainty that is *observed*, not invented. If a hazard input at a
substation in 1943 is poorly constrained and the same input in 2013 is well
constrained, the spread says so, per asset, per timestep — which is exactly the
distinction `FINDING_the_pre1979_boundary_is_not_1979.md` says must be carried
and not assumed.

## What is NOT established, and must not be assumed

1. **Resolution and timestep.** The ERA5 ensemble is a lower-resolution,
   coarser-timestep product than the deterministic field. Requesting it on a
   0.25° / 6-hourly grid returned a price, not a guarantee of native
   resolution; interpolated spread at 0.25° is still 0.5°-native information.
   Unverified.

2. **`ensemble_members` priced identically to `reanalysis` — which is
   suspicious.** Ten members should be ten times the fields under the cost
   model established on the fire and winter legs (cost = days × times ×
   variables × levels). Either the cost model does not charge per member, or
   the request did not carry the members it appeared to. **Unresolved**, and it
   must be resolved before any member-based design is proposed, because the
   whole point of this estate's cost discipline is not to discover a limit by
   rejection.

3. **Spread does not propagate itself through a nonlinear diagnostic.** The
   spread of an FMICLIM *input* is not the uncertainty of the FMICLIM *output*.
   FMICLIM is a conditional test across four co-temporal fields; propagating
   input spread to output uncertainty means running the diagnostic on ensemble
   members, not combining marginal spreads — the same nonlinearity rule that
   broke I2. Combining spreads would be that identical error wearing a
   respectable name.

4. **This covers hazard inputs only.** It says nothing about the uncertainty of
   the other components, which is where most of the 398,599 records' problem
   actually lives.

## Why it is worth pursuing anyway

Because it changes the shape of the remedy. The estate has been treating its
confidence-interval problem as *"we must generate uncertainty honestly"*. On at
least the hazard legs, there may be no need to generate it: it can be fetched,
at no additional cost, from the same requests already designed. An uncertainty
that came with the data is a different kind of object, for audit, than one the
estate computed about itself.

## Next step, when this leg is taken up

Resolve item 2 first — price a genuine multi-member request and confirm whether
the cost model charges per member. Nothing else here should be designed on top
of an anomaly.
