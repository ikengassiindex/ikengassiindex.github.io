# RESULT — the CERRA five-year archive is complete, with one declared hour missing from the source

**Status:** 60 of 60 months, 4.33 GB, verified
**Date:** 12 September 2026
**Releases:** the I2 threshold curve

---

## 1. The archive

2018–2022, `10m_wind_gust_since_previous_post_processing`, leadtimes 1, 2 and
3, full CERRA domain. **60 of 60 months, 4.33 GB retained from ~98 GB
transferred.**

Every 31-day month reports 35,425,591 finite cell-days and every 30-day month
34,282,830 — exactly `days × 1,142,761` in all sixty. No NaN, no gap in
coverage. Compression held at 22.3–22.7× throughout.

One failure in sixty, and it was the guard working.

## 2. The gap: 2021-04-01, 01:00–02:00 UTC

April 2021 returned **719 fields against 720**. The reducer refused the month
rather than write a day whose maximum came from 23 hours — a silent low bias
across the whole domain, invisible in the output.

Diagnosed to a single window: **the 01:00–02:00 window of 1 April 2021**, which
is the 00:00 analysis at leadtime 2.

**Confirmed genuine, not a retrieval glitch.** An independent one-day fetch,
a different request shape through a different script, returned 23 fields with
the same stamp absent. CERRA does not have that hour.

## 3. What it costs, measured rather than assumed

A missing hour can only ever make a maximum LARGER, so every value computed
from 23 hours is a lower bound. The question is how much room that leaves.

Measured across all 61,377 substation cells:

| | |
|---|---|
| cells where 1 April is already the 2021 annual maximum | **5 of 61,377** (0.008%) |
| median headroom below the year's peak | **13.4 m/s** |
| cells within 3 m/s of the annual maximum | 77 (0.13%) |
| 1 April's share of the 2021 exceedance sum, 22.5–30 m/s | **0.006% – 0.05%** |
| cells with any excess at 25 m/s | **1** |
| fleet median daily maximum, 1 April | 9.45 m/s |

1 April 2021 was a quiet day. For the missing hour to change a cell's annual
maximum it would have to exceed the rest of that cell's year — by a median of
13.4 m/s.

**It cannot move I2. That is a measurement, and it is not a reason to be
quiet about it.**

## 4. How the gap is carried

`--allow-short-days` is opt-in and the refusal remains the default. When used,
the gap is written into the file itself:

    short_days = [{"day": 1, "fields": 23, "expected": 24}]
    complete   = "false"

`ssi_derive_metric_I2_cerra.py` reads those and prints them before deriving.
`verify_cerra_dmax.py` checks every day against the file's own declaration and
the declaration against the data — so a file claiming completeness must be
complete, and a file declaring a gap must have exactly the gap it declares.

A reader who never sees this document still learns from the file that one day
in 2021 is a lower bound.

**Verified:** day 1 recomputed from the independently fetched probe file is
**identical to the archive at all 1,142,761 cells**. That is a stronger check
than recomputation from the same raw would have been — separate request,
separate bytes.

## 5. The mistake that produced --allow-short-days, recorded

`reduce_month` has TWO length checks: a total-field count and a per-day count.
The flag was gated on the second and not the first, so it could never take
effect, and the first real use of it was refused in production.

Same shape as the CI repair that covered one workflow of three and the
negative-zero clamp that covered one write site of five — made in the same
hour that "fixed should mean counted" was committed to `CLAUDE.md`.

The deeper miss was the test, not the gate. The suite asserted that short
months are REFUSED (T3, T4) and nothing asserted the accept path worked at
all. **A flag that adds a behaviour needs a test for that behaviour, not only
for the behaviour it relaxes.**

T7 and T8 now cover it — the gap is accepted and named, `complete` is false,
every other day is byte-identical to the known answer, the short day's value
is verified to be ≤ the 24-field value, and extra fields are still refused
even with the flag. 19 of 19 pass.

## 6. Next

The threshold curve. `GUST_THRESHOLD` and `ANCHOR` remain unpinned and are the
operator's, against the fleet response, as with I1's anchor and I3's
normalisation.
