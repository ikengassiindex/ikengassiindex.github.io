# FINDING — a CERRA gust leadtime is one disjoint hour, and eight of them are not enough for I2

**Status:** measured, decisive on both readings
**Date:** 10 September 2026
**Bears on:** I2 (wind), option D, the recorded CERRA/ERA5 ratio of 0.891
**Instruments:** `scripts/probe_cerra_leadtime_semantics.py`,
`scripts/measure_gust_sampling_bias.py`

---

## 1. What was wrong

The two January CERRA probes were fetched with `leadtime_hour = ["1"]`. They
came back with 248 timesteps for a 31-day month — eight per day, one per
3-hourly analysis.

The question that had to be answered before five years were fetched was whether
those eight fields cover the day or a third of it. Two readings, both taken:

**The time axis.** One day fetched with `leadtime_hour = ["1","2","3"]` returns
**24 distinct hourly timestamps**, 01:00 through 00:00 the next day, with no
duplicates and no separate step dimension. The three leadtimes tile the day.

**Monotonicity.** Nested windows (max over 0–1, 0–2, 0–3) are non-decreasing in
every cell by construction. Measured across 1,142,761 cells: field1 ≥ field0 in
**43.53%** of cells, field2 ≥ field1 in **48.30%**. Coin-flip. The windows are
disjoint.

The `lt=["1"]` fetch sampled hours **01, 04, 07, 10, 13, 16, 19, 22** and never
looked at the other sixteen.

I2 is a maximum. A maximum cannot be taken over a third of the hours.

---

## 2. How much it costs — measured directly

One day, both samplings, same file, 1,142,761 cells. Daily maximum from the
eight sampled hours against the daily maximum from all 24:

| | ratio |
|---|---|
| fleet mean | 0.9703 |
| median cell | 0.9941 |
| 1 cell in 20 (p05) | 0.8750 |
| 1 cell in 100 (p01) | 0.7764 |
| cells more than 5% low | **19.6%** |
| cells more than 10% low | **7.9%** |

**The fleet mean is a liar here.** It says 3.0% — a rounding error. The
distribution says one cell in five loses more than 5% of its maximum and one in
thirteen loses more than 10%, while the median cell loses almost nothing. That
is precisely the error this index cannot publish: invisible in aggregate, large
and *unevenly placed* per record, and unknowable from the published value.

## 3. A claim of mine that the measurement corrected

Before the probe returned I bounded this by thinning the existing 8-per-day
series to 4, 2 and 1 per day (`measure_gust_sampling_bias.py`). One halving,
8 → 4, cost 22.5% and 20.3% of cells more than 5% in the two Januaries.

I then argued that 24 → 8 would cost **less** than one halving, because it
happens at the dense end where neighbouring hours are strongly correlated, and
I reported the table to the operator as an **upper bound**.

The direct measurement is **19.6%** — the same magnitude, not smaller. The
argument was plausible and it was wrong, and it was wrong in the direction that
favoured the cheaper fetch. Recorded because that is the direction of error
that needs recording.

The mechanism, in hindsight: a gust maximum is achieved in a single short-lived
peak, not sustained across the window. Peaks do not care how correlated the
hours around them are. The same reason shows up in the thinning test — a
*monthly* maximum over 248 samples loses as much to one halving as a *daily*
maximum over 24 does, which it would not if the max were smeared across hours.

By that mechanism, an annual maximum is **not** meaningfully more robust to
thinning than a monthly one, and the earlier hope that 2,920 samples would
rescue it does not survive contact with the measurement.

## 4. What it does to the 0.891 ratio

CERRA measured 0.891 of ERA5 at the same substations — 11% lower — and the gap
was attributed to the models. The ERA5 side is a daily maximum over all 24
hours (`derived-era5-land-daily-statistics`, 365 timesteps per year, confirmed
on disk). The CERRA side saw eight hours.

A fleet-mean sampling loss of 3.0% cannot account for 11%, so **the gap is
mostly real** — CERRA does run lower than ERA5-Land gust at these sites. But
roughly a quarter to a third of it is sampling, and the *per-substation*
comparison behind it was never like for like. It must not be cited as if it
were, and it should be re-measured once the full-coverage fetch lands.

## 5. Consequence

The five-year fetch takes `leadtime_hour = ["1","2","3"]`.

Priced free with `estimate_costs`, nothing queued:

| leadtimes | cost / variable-year | limit |
|---|---|---|
| `1` | 17,520 | 90,000 |
| `1,2` | 35,040 | 90,000 |
| **`1,2,3`** | **52,560** | 90,000 |
| `1,2,3,4` | 70,080 | 90,000 |

A year still fits in one request. Measured volume: 69.4 MB for one day of 24
fields, so ~2.15 GB per month and **~129 GB for five years** of transfer.

That is transfer, not retention. See `PLAN_I2_cerra_five_years.md`.
