# PLAN — I2 from CERRA, five years, full temporal coverage

**Status:** proposed, awaiting the operator's pin
**Date:** 10 September 2026
**Depends on:** `FINDING_cerra_leadtime_and_temporal_sampling.md`,
`RESULT_I2_mosaic_test_1_FAILED.md`, `RESULT_I2_mosaic_test_2_FAILED.md`
**Sequence:** pin 16, phase 2 — acquire

---

## 1. What is being acquired and why this shape

Option D: I2 derived from CERRA at 5.5 km for the **513,554** substations
inside its domain, and declared **ABSENT** for the other 108,550. One
instrument, one meaning per published value. The mosaic route that would have
extended it to the rest was tested twice and failed twice; the second failure
passed its own pre-registered bars and was caught only on audit.

Window **2018–2022**, matching Convention #7 and metrics I1, I3 and I5.
Variable `10m_wind_gust_since_previous_post_processing`, the CERRA field that
is a true 3-second gust maximum per output window.

`leadtime_hour = ["1","2","3"]`, not `["1"]`. Measured, not assumed — see the
finding. Eight of twenty-four hours leaves one cell in five more than 5% low
on its own maximum.

## 2. Numbers, each one measured or priced rather than estimated

| | | how known |
|---|---|---|
| cost per variable-year | 52,560 against a limit of 90,000 | `estimate_costs`, nothing queued |
| requests | 60, one per month | a year fits in one request but is not resumable |
| transfer per month | ~2.15 GB | 69.4 MB measured for one day of 24 fields |
| **transfer, total** | **~129 GB** | |
| **retained, total** | **~4 GB** | see section 3 |
| free disk | 318 GB | |

Area does not enter CDS pricing — measured earlier, a global box prices
identically to Denmark. The full domain is fetched because there is no cheaper
subset, not because all of it is wanted.

## 3. Retention — 129 GB moves, ~4 GB stays

I2 needs the **daily maximum** gust and nothing finer. `I2_raw` is a mean
annual sum over days of `max(0, gust(d) − THRESHOLD)`, and the threshold curve
needs the annual maximum. Both are exact functions of a daily maximum.

A daily maximum is a maximum of maxima over one variable, so reducing to it is
**exact** — this is the case the nonlinearity rule explicitly exempts, unlike
the `sqrt(max u², max v²)` defect that broke the original I2 and the RH
defect that still blocks I8.

So each month is fetched, reduced to a full-grid daily maximum, and the raw
file deleted before the next month is requested:

```
    raw month      1069 x 1069 x 744 hourly fields    ~2.15 GB   deleted
    daily max      1069 x 1069 x 31                   ~70 MB     kept
    5 years                                           ~4 GB      kept
```

Full grid, not the 61,377 occupied cells. The occupied-cell subset would be
448 MB, but it would bake the cell map into the archive: change the map, or
add a substation, and the fetch would have to be repeated. 4 GB buys
independence from that, and it keeps the deferred five-year-maxima texture
question answerable from data in hand.

Peak disk at any moment: one raw month plus the archive so far, under 7 GB.

The `.cache` is gitignored, so none of this enters the repository. The archive
is reproducible from this plan, the fetch script, and the CDS.

## 4. The gust day runs 01:00 to 00:00

A month requested with days 1..N and leadtimes 1,2,3 returns exactly 24N
fields, from 01:00 on the 1st to 00:00 on the 1st of the next month. Each
field is the maximum over the hour ENDING at its stamp, so a field is assigned
to the date of `valid_time − 1 hour`. That gives 24 fields per calendar day
with no gap, no overlap, and no leakage across the month boundary.

The consequence, declared rather than buried:

- **A gust day runs 01:00 UTC to 00:00 UTC the following day**, not midnight to
  midnight. The annual maximum is unaffected — a maximum over all hours of a
  year does not depend on how the hours are binned into days. The exceedance
  sum changes only for a storm that straddles a 00:00–01:00 boundary, and only
  in how its excess is split between two days.
- **One hour of the record is missing**: 00:00–01:00 UTC on 1 January 2018,
  which belongs to the 21:00 analysis of 31 December 2017. One hour in 43,824.
  Not backfilled; counted and declared.

## 5. Chunk size is measured before it is chosen

Three latency observations, and they do not line up:

| request | bytes | wall time |
|---|---|---|
| one day, 24 fields | 69.4 MB | **1 min** |
| one month, 8 fields/day | 555 MB | ~2 h |
| one month, 24 fields/day | ~2.15 GB | unknown |

69 MB in one minute and 555 MB in two hours do not scale together by any
factor. Whatever dominated the month was **queue**, not transfer — which is
consistent with the earlier finding that latency was independent of payload
from 0.1 MB to 154 MB, and means the 2.15 GB month may cost little more than
the 555 MB one. It may also not: two observations, one of each, is not a
model.

So the first month is fetched alone and timed. Only then are the concurrency
and the chunk size for the remaining 59 set. If a month proves unreliable, the
fallback is three 10-day blocks of ~700 MB, within a factor of 1.3 of what is
already proven.

## 5a. The delete is tested before it is trusted

The reducer unlinks a 2.15 GB raw it cannot get back without re-queueing, and
every path guarding that delete was written and never executed. Untested code
with an irreversible side effect is not something to point at 60 months.

`scripts/test_cerra_reducer.py` runs the reducer against synthetic months on a
40 x 40 grid where the correct answer is known by construction. Six criteria,
fixed in the file before the tests ran; two of them plant real defects and
require a refusal, because a bar that cannot fail proves nothing — the lesson
taken from mosaic attempt 2, which passed three bars and was still wrong.

**12 of 12 pass.** The one that mattered: a month whose last day peaks in the
hour stamped `01 Feb 00:00` yields 99.0 on day 31, not a collapsed 1.0 and not
a February leak. The gust-day rule holds at the boundary where it could have
silently truncated a maximum.

Even so, **month one runs with `--keep-raw`**. The test proves the logic on
synthetic data; the first real month proves it on CERRA's own shape, and the
raw stays on disk until its daily maximum has been looked at. Months 2–60
delete as they go.

## 6. What this does not settle

- **GUST_THRESHOLD and ANCHOR remain unpinned.** The derivation runs
  `--raw-only` first and produces the fleet threshold-response curve; the
  operator pins against it, as I3's anchor and I1's anchor were pinned.
- **The 0.891 CERRA/ERA5 ratio must be re-measured** on the full-coverage data
  before it is cited again.
- **The texture-from-five-year-maxima question** stays deferred, to be answered
  from this archive as a by-product rather than used to justify acquiring it.
- **108,550 substations get no I2.** That is the cost of option D and it is the
  point of option D.

## 7. Pipeline-bot window

Convention: no derivation runs in the bot's window — first Thursday of the
month, 06:00 UTC. Next occurrence 1 October 2026. The fetch is not a
derivation and does not touch a published record, so it may run across it; the
derivation may not.
