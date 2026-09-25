# FINDING — the negative-zero defect was fixed in one place of many, and the interpreter that runs the estate is tested by nobody

**Status:** measured
**Date:** 11 September 2026
**Instrument:** `scripts/audit_published_json.py`
**Same shape as:** `fix(ci)` 64889151, found the same day

---

## 1. What was believed

On 9 September, 23,997 substations were published with `metrics.I1 = -0.0` — a
negative snow load. ERA5-Land carries tiny negative snow water equivalents from
numerical noise; averaged and rounded to 5 dp they become negative zero, which
is numerically equal to `0.0` and serialises as the string `"-0.0"`. The check
that missed it was `v < 0`, which is **False** for `-0.0`, and I reported "zero
records are negative".

A clamp was added at I1's write site, verified two ways, and the defect was
recorded as fixed.

## 2. What is true

`-0.0` is not a property of snow. It is a property of `round()` on a small
negative, and every field written by every producer in this estate can carry
it. Sweeping all 73 published JSON files found **251 more, in 30 of 39
countries**:

| count | path |
|---|---|
| 120 | `shard[].modifier_impacts.R8_adapt` |
| 33 | `shard[].skewness` |
| 29 | `substations[].modifier_impacts.R8_adapt` |
| 27 | `substations[].modifier_impacts.R4_F_topo` |
| 20 | `substations[].skewness` |
| 10 | `substations[].modifier_impacts.R3_C_mult` |
| 5 | `substations[].modifier_impacts.R7_cyber` |
| 4 | `substations[].modifier_impacts.R6_restoration` |
| 3 | `substations[].modifier_impact` |

`metrics.*` and `components.*` are **clean** across all 9,466,784 numeric
values. The I1 clamp held, and nothing else in those namespaces went negative.

## 3. Severity, stated rather than inflated

`metrics.I1 = -0.0` was a false physical claim: a snow load cannot be negative.
These 251 are not that. A modifier impact and a skewness **can** legitimately be
negative, so `-0.0` there is a zero carrying a stray sign bit, not a claim about
the world.

It is still a nonsense token in a published record, it still renders as `-0.0`
in anything that reads the text rather than parsing it, and it is still the same
defect. It should be cleaned. It is not an emergency.

## 4. The sweep nearly issued a false all-clear

The first pass parsed `metrics` and `components` and found **zero**. That is
where the last bug was, so that is where I looked. Only a raw text scan across
the whole document found the 251, in fields nobody had opened.

Both passes are now kept in the instrument and **required to agree**. A
disagreement means the structured walk is not reaching part of the document —
which is exactly what a clean report over dirty data looks like.

## 5. That reconciliation immediately caught a bug in itself

On its first run the two passes reported 251 and 85,192. The walk was right;
the text pattern was wrong. `-0\.0+(?![1-9])` also matches `-0.00123`, by
backtracking to `-0.0` and finding a `0` next. The fix is `(?![0-9])`: no digit
of any kind may follow the run of zeros. Ten cases now pin the pattern.

A cross-check between two methods catches errors in **both** of them. That is
the argument for building it rather than trusting either alone.

## 6. The interpreter gap — the more structural finding

On 9 September, `statistics.correlation` was found to exist only from Python
3.10; on 3.9 the `AttributeError` was swallowed by a bare `except` and the
register published "correlation not computable". It was replaced with an
explicit `_pearson()` and recorded as fixed.

Sweeping 303 Python files for the same class:

- **Constructs requiring 3.10+:** one hit, `modifier_registry.py:294`, and it is
  a **false positive** — `str|None` inside a `Returns:` docstring, never
  evaluated.
- **`except Exception` followed by a silent fallback:** **none**. That pattern
  was unique to the instance already repaired.

So the specific repairs hold. The gap behind them does not:

| | Python |
|---|---|
| CI test matrix (`test.yml`) | 3.10, 3.11, 3.12 |
| all other workflows | 3.11 |
| **the operator's Mac, which runs every derivation** | **3.9** |

Nobody tests the interpreter that actually produces the published data.
`statistics.correlation` was not a one-off; it was the first symptom of an
untested configuration. Python 3.9 also reached end of life in October 2025.

Checked, because these seven scripts run on that 3.9: every one of
`probe_cerra_leadtime_semantics`, `measure_gust_sampling_bias`,
`resolve_cerra_cells`, `fetch_cerra_daily_max`, `test_cerra_reducer`,
`verify_cerra_dmax` and `ssi_derive_metric_I2_cerra` carries
`from __future__ import annotations`, and none uses `X | None` at runtime.

## 7. What should happen, in order

1. **Close the interpreter gap** — either add 3.9 to the CI matrix, or move the
   Mac to a supported Python and drop 3.9 from the estate. The second is
   better: 3.9 is end-of-life. This is the class fix, and it is the operator's
   decision.
2. **Clean the 251 tokens** — a data change to published records, its own
   change under the pinned sequence, not a drive-by.
3. **Then turn on the gate.** `--gate` is deliberately not the default and is
   deliberately not yet in `validate.yml`: wiring it today would fail every
   build. An instrument that has to be switched off to get work done teaches
   everyone to switch instruments off.

## 8. The lesson, which is yesterday's lesson again

The CI repair earlier today covered one workflow of three. This one covered one
write site of many. Both were recorded as complete. Both were found by asking
how many places have the same shape and then counting them.

Twice in one day is not a coincidence. **"Fixed" should mean "counted", and a
repair that names one location should say how many were searched.**
