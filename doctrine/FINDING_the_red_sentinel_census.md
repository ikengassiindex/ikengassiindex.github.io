# FINDING — the sentinel suite cannot run whole, and 46 of its assertions are red

**Measured** 21 September 2026, running `tests/` **file by file**, because the
suite cannot complete in one process.

Found while checking that the new hazard cell index caused no regression. It
did not. Something else did, some time ago, and nobody has been looking.

## First: the suite does not finish

`python3 -m pytest tests/` is **killed by the OOM reaper at about 16 %** in a
3.9 GB environment. It fails identically with the new test file excluded, so
this is not today's doing. Run file by file, all 33 files complete.

That matters more than it sounds: **a suite that cannot run whole is a suite
nobody runs whole**, and everything below has been red behind that wall.

## The census

Run individually, 33 files, 1,207 assertions:

| file | red | cause |
|:--|--:|:--|
| `test_no_cross_border_leakage` | 88 | `shapely` not installed — **environment** |
| `test_score_shift_acceptance` | 29 | real — shift gate at 0.05, observing ~0.99 |
| `test_socio_economic_backfill_polygon` | 6 | real — count 1177 vs 3757; region sets |
| `test_ssi_data_sharding_invariants` | 4 | real — manifest entries missing `size_mb` |
| `test_migration_score_semantic_normalise` | 3 | real — negative migration scores |
| `test_modifier_registry` | 1 | real — Korea 1.321715 vs expected 1.341541 |
| `test_per_country_modifiers` | 1 | real — 1.2225 vs 1.2346765 |
| `test_r_base_derives_from_components` | 1 | real — "uk should not — that is the finding" |
| `test_validate_schema` | 1 | real — **72.04 % of Italy** band-mismatched |
| `test_retired_modifier_excluded` | 1 | **test-order bug — FIXED in this change** |
| `test_e2e_refresh` | — | did not complete in the harness; unclassified |

**88 of the 135 are one missing package.** 46 are not.

## Constitution §7.8

*No permanently red sentinel.* Every row above but the first and the last is
one. This finding does not resolve them; it makes them visible and says which
is which, so the choice about each is a choice rather than an oversight.

## The one fixed here

`test_retired_modifier_excluded::test_dropping_it_without_a_successor_is_logged_as_an_error`
**passed alone and failed in file order.** The retirement notice is logged once
per process on purpose — half a million identical lines had buried a cohort
measurement — and an earlier test in the same file spent the single notice
before the logging test ran.

The throttle is correct and was not weakened. The module already ships
`reset_retired_skip_counts()` for this; an autouse fixture now calls it around
each test. Fixed because the defect was in the test, the remedy touched no
published value, and leaving a green-in-isolation test red in the file is the
worst of both.

## The one that should be looked at first, and a hypothesis

`test_validate_schema` reports **30,015 Italian substations — 72.04 % — with a
classification mismatched to their `R_median` band**, on the canonical
reference country. Its example is `7000000001`, `R_median=0.4713`, expected
*Medium*, published *Low*.

**Hypothesis: the validator is wrong, not the data.** Twice today the same
error was made in this estate's instruments — passing a record's own Monte
Carlo bounds, or absolute thresholds, to a band rule that takes the
**country's** percentile anchors `_band_norm_R_P5` / `_band_norm_R_P95`.
`R_median=0.4713` is *Medium* on absolute thresholds and *Low* against Italy's
own anchors. A 72 % mismatch rate on the reference country is far more
consistent with a validator applying the wrong rule than with three quarters of
Italy being misclassified in production.

It is a hypothesis. It is written down as one and must be tested — by reading
which rule `validate_schema` applies — before either the data or the test is
touched. Recording it now because the same category error has already cost
this estate two wrong numbers in one day, and the third time it should be
recognised on sight.

## Not proposed here

No fix for the other 45. Several look like acceptance gates left pinned to
pre-cutover expectations — `test_modifier_registry` expecting Korea at
1.341541 and `test_r_base_derives_from_components` asserting UK "should not"
have the fix, when the R7 cutover and the UK remediation both landed — and a
stale expectation must be retired deliberately, with the reasoning recorded,
never quietly re-baselined to whatever the code now emits. That is a decision,
and it is the operator's.
