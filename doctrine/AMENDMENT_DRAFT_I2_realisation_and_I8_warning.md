# Amendment (DRAFT) — I2's realisation, and a guard against the class

Status: DRAFT for the operator's pin. Not registered, nothing derived.
Raised: 2026-09-03, on FINDING_era5_fetch_not_viable.md section 4.
I2 is `blocked` and exists on zero records, so nothing published moves.

---

## 1. What is wrong, precisely

The definition pinned on 31 August is **correct and is not amended**:

    speed(d) = the daily maximum 10 m wind speed, sqrt(u10^2 + v10^2)
    I2_raw   = mean annual sum of max(0, speed(d) - 17.2) m/s-days

What is wrong is the *realisation* the fetch plan implies, which computes

    sqrt( max_t u(t)^2 + max_t v(t)^2 )     NOT     max_t sqrt( u(t)^2 + v(t)^2 )

ERA5 wind components are signed, so `daily_maximum` is the maximum of a signed
series and not a maximum magnitude. The two expressions are different
quantities and the difference has **no sign**:

    gale from the east, then calm    true 20.00 m/s  ->  estimator  1.41   -92.9%
    wind veers, never a gale         true 15.00 m/s  ->  estimator 21.21   +41.4%
    steady westerly gale             true 22.00 m/s  ->  estimator 22.00     0.0%

I2 is a threshold-excess sum, so this moves the support and not just the
magnitude: the first case is a real gale scored at zero excess, the second is a
day that never gales scored at 4.01 m/s-days. The metric can miss the hazard it
exists to measure and manufacture one where there is none, on the same fleet,
with nothing on the record to say which happened at a given unit.

## 2. The general rule this is an instance of

    A nonlinear function of two or more variables cannot be computed from
    their independently pre-aggregated marginals.

Applied to the fetch plan:

    I1  annual max snow_depth_water_equivalent   SAFE — one variable, and the
        max of a daily max is the max of the hourly series. Exact.
    I2  speed from u and v                       BROKEN — section 1.
    I8  ISO 9223 from 2m T and dewpoint          BROKEN BY THE SAME RULE.
        Relative humidity is nonlinear in T and Td, so RH(mean T, mean Td) is
        not the daily mean RH. I8 is not in scope this week; it is named here
        so it is caught before its fetch is spent and not after.

## 3. What is proposed

**(a) I2 `source` is corrected, not its definition.** The current line reads
`ERA5-Land daily maximum 10m_u_component_of_wind and 10m_v_component_of_wind,
2018-2022 - NOT YET FETCHED`. That source cannot satisfy the definition above
and the line asserts, by omission, that it can. It becomes hourly u and v with
the speed formed before the temporal reduction, and says why.

**(b) I2 `blocked_on` gains the real blocker.** Today it names only the fetch.
The fetch was never the whole of it: no daily product of any supplier can
satisfy this definition. That belongs on the record.

**(c) A conformance row, so the class cannot recur silently.** Proposed:

    metric_inventory | <m>.realisation | a metric whose definition is a
    nonlinear function of two or more source variables declares whether its
    realisation reduces the function or the marginals | BLOCKING

  It would fire today on I2 and, when I8 is defined, on I8. It would not fire
  on I1, I3, I4, I5 or I6, each of which is a function of one variable. The row
  is cheap and it is the only thing here that outlives the present decision:
  every future two-variable metric meets it on the way in.

**(d) I8's definition is written before its fetch, not after** — the discipline
already applied to I1, I2 and I3. Not drafted here; named as next.

## 4. What this does NOT propose

No change to the I2 formula, the 17.2 m/s Beaufort 8 pin, the C_bounded
assignment, the [0, 0.30] interval, or the vegetation limitation. All four were
pinned on 31 August and none is touched by this. The anchor stays undeclared
because the fleet still does not exist, and the taxonomy guard continues to
report it as pending on every rendered document, as designed.

No score moves. I2 exists on zero records before this amendment and on zero
records after it.

## 5. Why now, before the source decision and not after

Because the defect decides the source. On any daily product I2 is
uncomputable; on Earth Engine's hourly collection the speed is formed before
the reduction, server-side, for one line of code and no extra transfer. Pinning
the realisation first means the source is chosen to serve a definition, which
is the sequence this estate has used for I1, I2 and I3 and the one it got
wrong for the fetch plan.

## 6. Standing at risk if this is not pinned

I2 stays `blocked` either way, so the exposure is not to the published index —
nothing is published. The exposure is to the plan. Counted from
`ERA5_FETCH_PLAN_I1_I2.json`, 59 boxes x 5 years x 7 variables = 2,065:

    dmax  u and v components                 590   INVALID for I2. Buys a
                                                   quantity whose error has no
                                                   sign. Not recoverable by
                                                   declaring it.
    dmean 2m temperature and dewpoint        590   DEGRADED for I8. RH from
                                                   daily means is a proxy for
                                                   daily mean RH, one-directional
                                                   and declarable under
                                                   Convention #7 — usable if
                                                   declared, unlike I2.
    dmax  snow_depth_water_equivalent        295   SOUND. This is I1.
    dmax / dmin  2m temperature              590   sound; the I3/I5 gap set.

  So 590 requests — 29 per cent of the plan — buy nothing usable, and a further
  590 buy something materially weaker than the plan implies. If the CDS route
  is resumed for any reason, the u and v sets should not be resumed with it,
  and the dmean set should not be spent until I8's definition is pinned and
  states which quantity it is actually computing.
