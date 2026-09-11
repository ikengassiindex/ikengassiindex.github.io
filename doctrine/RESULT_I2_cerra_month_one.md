# RESULT — CERRA month one, measured and verified against its raw

**Status:** verified, 6 of 6 criteria, all 31 days
**Date:** 11 September 2026 (fetched 10 September)
**Releases:** the remaining 59 months of `PLAN_I2_cerra_five_years.md`
**Instruments:** `scripts/fetch_cerra_daily_max.py`,
`scripts/verify_cerra_dmax.py`, `scripts/test_cerra_reducer.py`

---

## 1. What was measured

January 2018, full CERRA domain, `leadtime_hour = ["1","2","3"]`, 744 hourly
fields.

| | predicted | measured |
|---|---|---|
| wall time | unknown; feared ~2 h | **0.23 h — 14 minutes** |
| transfer | 2.15 GB | **1.63 GB** |
| daily-max file | ~70 MB | 73 MB, a 22.5× reduction |
| finite cell-days | — | **35,425,591 = 31 × 1,142,761 exactly** |
| grid file | ~18 MB | 12.2 MB, written once |

The cell-day count is every cell on every day. No NaN, no gap, nothing
land-masked away.

## 2. The chunk-size question is settled

Three observations now, and the shape is clear:

| request | bytes | wall time |
|---|---|---|
| one day, 24 fields | 69.4 MB | 1 min |
| one month, 8 fields/day | 555 MB | ~2 h |
| **one month, 24 fields/day** | **1.63 GB** | **14 min** |

1.63 GB behaves like the 69 MB probe, not like the 555 MB month. Queue
dominates; transfer barely registers. Whatever cost the 555 MB month two hours
was queue depth on the day, not its size.

**Consequence: no concurrency is needed.** 60 months sequential is about 14
hours. The 10-day-block fallback in the plan is not required and is not used.

**Revised totals: ~98 GB of transfer** (not 129) and **~4.4 GB retained**.

## 3. A byte estimate wrong for the third time this session

Predicted 2.15 GB from the one-day probe; measured 1.63 GB. 32 per cent high.

The earlier two: 8 GB predicted against 3.1 GB actual for the ERA5-Land fetch,
and 0.0105 MB/deg² for CERRA, too low. Three misses, in both directions, from
three different extrapolations.

The pattern is not a bad constant. It is that a single sample of a compressed
field does not predict the compression of a different-shaped request — 1
January was a stormy day, and a stormy day compresses worse than an average
one. The correction is not a better coefficient. It is to stop quoting byte
estimates as though they were measurements, and to say "measured X on a sample
of one, expect within a factor of 1.5" until a second sample exists.

## 4. Verification — against the raw, not against itself

The reducer reopens what it writes and checks shape and finiteness. That
catches a truncated write and nothing else: it is the same code path that
produced the answer, so an off-by-one in the day binning would yield a
well-formed file full of wrong maxima and be confirmed.

`verify_cerra_dmax.py` recomputes the answer by brute force from the raw, with
none of the reducer's machinery. This is why month one was fetched
`--keep-raw`.

| | |
|---|---|
| shape | 31 slices for 31 days |
| **C1 exact equality** | **all 31 days recomputed, identical at every cell** |
| C2 boundary day | day 31, whose 24th field is stamped `00:00` on 1 February |
| C3 first day | short by design in hour 00:00–01:00, still 24 fields |
| **C4 no ceiling** | stored month max **55.7194** = raw month max **55.7194** |
| C5 physical range | 0.519 – 55.719 m/s |

C2 and C3 are the two the gust-day rule could have silently broken. Both hold.

## 5. A defect in this verifier, found and fixed before it mattered

On its first run over a 4-day sample, **C4 reported PASS while comparing
nothing**. The stored month maximum was 55.7194 and the "raw month maximum"
was 49.3126 — the largest value among the four days actually read. The check
was written to skip its own comparison on a partial sample, and skipping was
coded as passing.

That is exactly the defect recorded in `RESULT_I2_mosaic_test_2_FAILED.md`: a
bar that cannot fail. It was written into this verifier hours after that
lesson was committed, by the same hand.

C4 now reports **SKIP**, counts as not-run, and the script exits 2 with *"a
partial verification does not licence 59 more months."* The full run then gave
a real C4: 55.7194 against 55.7194.

The generalisable form, stronger than the mosaic version: **knowing the
failure mode does not prevent it.** A pre-registered bar protects against
moving the bar; auditing a pass protects against a bar that measures nothing;
neither protects against writing a third one tomorrow. The only structural
defence is that every check must have a state for "I could not run this", and
that state must not be green.

## 6. Released

Months 2018-02 through 2022-12 may run and delete their raw as they go.
`cerra_raw_201801.nc` (1.63 GB) remains on disk and is the operator's to
delete.
