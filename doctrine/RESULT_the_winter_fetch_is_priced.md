# RESULT — the winter fetch is priced, and the expensive part is not the queue

**Measured** 21 September 2026 · `scripts/estimate_winter_fetch_cost.py --sweep`
· C3S CDS · priced server-side, nothing queued, nothing downloaded.

`PLAN_hazard_raster_acquisition.md` §4 carried a cost *warning* — "substantially
more expensive than the FWI fetch … estimate before committing" — and no
number. This supplies the number. The warning was right about the magnitude and
wrong about the mechanism.

## Measured

**`reanalysis-era5-pressure-levels`** — RH and T at 925 / 850 / 700 hPa,
6-hourly. 2 variables × 3 levels × 4 times = 24 fields/day.

| years | cost | limit | |
|---:|---:|---:|:--|
| 1 | 8 784.0 | 60 000.0 | OK |
| 5 | 43 848.0 | 60 000.0 | OK |
| **6** | **52 608.0** | 60 000.0 | **OK — the boundary** |
| **7** | **61 368.0** | 60 000.0 | **OVER** |
| 10 | 87 672.0 | 60 000.0 | OVER |

**`reanalysis-era5-single-levels`** — 2m T, surface pressure, total
precipitation, 6-hourly. 3 variables × 4 times = 12 fields/day.

| years | cost | limit | |
|---:|---:|---:|:--|
| 1 | 4 392.0 | 121 000.0 | OK |
| 10 | 43 836.0 | 121 000.0 | OK |
| **27** | **118 344.0** | 121 000.0 | **OK — the boundary** |
| **28** | **122 724.0** | 121 000.0 | **OVER** |

Both boundaries are **bisected, not inferred** — `cds_cost.find_boundary()`
prices the last window that passes and the first that fails. That discipline
exists because inference is what put a limit of 400 into the fire plan when the
measured one was 3720.

**The cost model generalises.** 8784 = 366 × 4 × 2 × 3. 4392 = 366 × 4 × 3. The
fire probe found cost = days × variables; here it is **cost = the number of
SELECTOR COMBINATIONS requested**, i.e. days × times × variables × levels. The
fire result was the special case where times = levels = 1. One rule, now tested
on two data stores and three datasets.

*(Corrected the same day: this originally read "the number of FIELDS". For the
three product types used here a combination returns one field and the two are
the same number, so nothing measured above changes. They diverge for
`ensemble_members`, where ten members arrive for one combination's price — see
`RESULT_the_cost_model_counts_selectors_not_fields.md`. The field counts used
in the volume section below remain correct, because they are counts of
deterministic fields.)*

## What it means for the fetch

    pressure levels    6-year windows   →  15 requests
    single levels     27-year windows   →   4 requests
                                           ─────────────
                                            19 requests

**Nineteen, against the fire leg's eighteen.** The two legs are, in queue terms,
the same size. That is the part the plan got wrong: it warned about expense in a
section about requests and latency, and by that measure winter is not expensive
at all.

## Where the expense actually is

1940–2025 is 31 412 days. The winter legs request **1 130 832 fields**; the fire
leg requests 62 824. Winter is **eighteen times the volume**, at the same
request count.

At 0.25° global each field is 1440 × 721 = 1 038 240 points, so on the order of
1–2 MB packed — **arithmetic, not measured**: the per-field byte size has not
been observed and nothing below is a measured value under §7.2.

    at 1 MB/field    PL 0.75 TB  +  SL 0.38 TB  ≈  1.1 TB
    at 2 MB/field    PL 1.51 TB  +  SL 0.75 TB  ≈  2.3 TB

Against ~260 GB for the whole fire leg.

**This changes which lever matters.** On the fire leg, request count was the
only lever, because latency is per request and payload-independent — which is
why collapsing 172 requests to 18 was worth doing. On the winter leg the
request count is already near-minimal and the binding constraint is transfer
time and the streaming sampler's throughput. Optimising the winter request
count further would be optimising the wrong quantity.

The streaming design still holds and is now load-bearing rather than tidy:
fetch a window, sample at the 622 104 asset points, accumulate, discard the
raster. Storing 2 TB is not on the table; storing the per-asset series is ~5
million values.

## What cannot be traded away

FMICLIM is a conditional test across four co-temporal fields — T2m, the warm
layer's T and RH aloft, the cold-layer depth, and 6-hourly precipitation. It
**cannot** be evaluated from independently pre-aggregated marginals. That is
precisely the defect that broke I2 and blocks I8. So the volume cannot be
reduced by dropping a field, coarsening the timestep below 6-hourly, or
pre-averaging anything before the test runs.

It can be reduced only by fetching a **shorter record**, which is an operator
decision against the standing granularity principle, not an optimisation, and
is not taken here.

## Open

- **Per-field byte size is unmeasured.** One single-day, single-field request
  would settle it and would be the first thing actually queued on this leg. It
  is not queued here, because queueing is an acquisition step and acquisition
  has not been authorised on this leg.
- **Sustained throughput from the CDS is unmeasured**, and it, not the queue,
  sets the wall-clock on this leg.
- The pre-1979 back-extension question is open on this leg exactly as it is on
  fire, and for the same reason.
