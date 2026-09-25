# DESIGN — the rescore-only path, and what stamps a record

Status: DESIGN. Nothing built. Measured 24 September 2026.
Blocks on: `land_20260921_BE_BF.sh` (Pin 5 — the R3 re-derivation lands first).

---

## 1. The question

The R3_C_mult re-derivation is declared in `SSI_FOUNDATION_judgement.yaml` and
implemented in `engine.py`. It is applied to nothing. 622,104 published records
still carry values produced by the SHA-1 jitter of 4 June.

Separately, 11,361 records were never rescored in Phase zeta and still carry the
retired R7_cyber v1 (`FINDING_phase_zeta_left_11361_records_unrescored.md`).

Both have the same cause, stated at `merge.py:158`:

    needs_rescore = has_seismic or has_climate or has_socio

A formula change is not an input change. There is no rescore-only path through
the orchestrator. Every formula change has therefore been applied by a bespoke
script, and the conformance register carries `published record / write paths` as
BLOCKING with 22 unsanctioned writers — a count that rises by one each time this
happens.

One mechanism closes both. This document is its design.

---

## 2. Five measurements

### 2.1 The obvious detector does not exist

A rescore-only pass needs to know which records are stale. The natural candidate
is the record's own `version` field. Scanned across all 39 countries, 622,104
records:

| value            | records |
|------------------|--------:|
| `4.2`            | 564,096 |
| `4.0.2`          |  51,986 |
| `v4.0.2`         |   4,553 |
| `v4.0.2-parity`  |     556 |
| `v4.0.2-LT-S17`  |     505 |
| `v4.0.2-co-s39`  |     378 |
| absent           |      30 |

Seven spellings across four eras, and `versions.json` says the methodology is
**4.24**. No record claims it. At the file level, `meta.version` reads `4.0.2`
in 25 countries, `v4.0.2` in one, and is absent in thirteen.

The reason is that nothing maintains it. `engine.py`, `merge.py` and `run.py`
never write a record-level `version`. The writers are twenty-odd per-country
`scripts/pipeline/ingestion/<country>/merge_into_ssi_data.py` files, each with
the literal `"version": "4.2"` typed into a record template. It is an ingestion
schema constant, typed once per country and never revisited — not a methodology
stamp. Constitution §7.2 forbids typing a measured value; this is a *declared*
value typed, one level down, and it has rotted the same way.

`version` cannot gate the rescue. It is itself a defect to be repaired.

### 2.2 The engine reproduces its own published values

Before proposing a pass that rewrites the estate, the prior question is whether
the estate reproduces. Three countries, every record re-scored from its own
published inputs and compared to its published `R_median`:

| country   | records | reproduces (≤0.005) | drift 0.005–0.05 | drift >0.05 |
|-----------|--------:|--------------------:|-----------------:|------------:|
| portugal  |  13,564 |    13,564 (100.0%)  |                0 |           0 |
| slovenia  |   1,731 |     1,727  (99.8%)  |                1 |           3 |
| greenland |      43 |        39  (90.7%)  |                4 |           0 |

This is the finding that makes the mechanism safe. Outside the five known
stale-baseline countries (france, germany, us, italy, japan — 397,852 records,
`RESULT_the_r7_data_sentinel.md`), a rescore-only pass is near-idempotent. Every
record it *does* move is therefore attributable rather than lost in churn, and a
dry run can say so per country before anything is written.

Greenland's 90.7% is expected — it is the S1 special case with its own script.
It is reported, not explained away.

### 2.3 The Monte Carlo is unseeded

`score_substation` calls `monte_carlo(components, modifiers, iterations=10_000)`
at `engine.py:783`. The `seed` parameter defaults to `None`, documented at
line 619 as "non-deterministic". No caller anywhere passes a seed.

Measured on slovenia, 25 rescores of the same record:

| published R_median | rescored sd | spread (max−min) | relative sd |
|-------------------:|------------:|-----------------:|------------:|
| 0.1742             |    0.000000 |         0.000000 |      0.000% |
| 0.9861             |    0.000713 |         0.002800 |      0.072% |

Most records are exactly stable because their confidence interval is zero-width
— no Monte Carlo ran (`engine.py:208`). Where it does run, the estate is
reproducible only to about ±0.003 absolute.

Two consequences. First, the 0.86% median ratio attributed to the R7_cyber v1
retirement in Phase eta contains an unmeasured noise component of this size; the
control group (78,118 records without the modifier, 0.0% movement) is unaffected
because those records were never rescored, so the *direction* of that finding
stands, but its magnitude is soft in the third digit. Second, and more to the
point here: a rescore-only pass that moves a published number purely by RNG
cannot claim the movement is the formula.

### 2.4 373 records are published at exactly zero

Scanning all 622,104 records for `R_median == 0`:

| country     | zeros | of      |
|-------------|------:|--------:|
| norway      |   271 |   6,113 |
| chile       |    70 |   1,035 |
| poland      |     8 |  27,764 |
| hungary     |     5 |   3,507 |
| slovakia    |     5 |   1,517 |
| belgium     |     4 |   6,651 |
| slovenia    |     3 |   1,731 |
| estonia     |     2 |   1,794 |
| latvia      |     2 |   4,646 |
| finland     |     1 |   3,939 |
| greenland   |     1 |      43 |
| netherlands |     1 |   5,449 |
| **total**   | **373** | **622,104** |

A further 33 carry `R_median: null`, which is Convention #56 behaving correctly.

The 373 are not. Slovenia's three rescore to 0.1095, 0.1464 and 0.2548 from
their own published inputs — the value exists, and a zero is standing in front
of it. In an index where higher R is worse and `P_critical` counts samples above
0.75, a published zero reads as the most resilient substation in the estate.
This is Constitution §7.5, no silent absence: a zero is not an absence, it is a
claim.

The same mechanism repairs them. They are not a separate job.

### 2.5 The precedent already exists

`scripts/r7_substitute_and_rescore.py` is this mechanism, written once, for one
modifier. Its docstring states the gate problem, measures the cost (4.8 ms per
record, "under an hour for the whole estate"), defaults to dry run, and refuses
to quote a single cohort-wide figure across the five stale-baseline countries.
The design below generalises it rather than inventing anything; the discipline
is already written down and should not be re-derived.

---

## 3. The design

Three parts. The first two are engine changes; the third retires a script.

### 3.1 The engine stamps what produced the number

`score_substation` writes `_scoring_fingerprint` on every record it touches: a
short digest over everything that determines its output —

  * the active modifier set and each modifier's parameters, from
    `MODIFIER_REGISTRY`;
  * `R3_PARAMS` and the other derivation constants;
  * the metric weights and `SIGMA_TOTAL`;
  * the band rule in force;
  * `methodology` from `versions.json`.

Computed once at import, not per record. Two properties matter:

  * **It is produced by the same function whose change it detects.** A formula
    change that does not move the fingerprint is a formula change that cannot
    move a score. There is no way to edit the derivation and forget the stamp,
    which is exactly how `version` rotted.
  * **It makes staleness measurable.** Today the question "how many published
    records were produced by the current methodology?" has no answer. After
    this, it is a scan.

The fingerprint is a stamp, not a version number. It does not replace
`versions.json`, which stays the SoT for the human-readable methodology; the
fingerprint records *which* build of it ran. Record-level `version` is repaired
separately — it should read `_methodology_version()` rather than a per-country
literal — but that is an ingestion-layer fix and does not belong in this change.

### 3.2 The orchestrator gains a rescore-only branch

`merge_and_rescore` currently has two branches (`needs_rescore and rescore`,
`elif needs_rescore`) and an else that passes the record through. A third
condition joins the gate:

    stale = rescore_stale and sub.get("_scoring_fingerprint") != CURRENT_FINGERPRINT
    needs_rescore = has_seismic or has_climate or has_socio or stale

with `rescore_stale` off by default and reached by `--rescore-stale` on
`scripts/pipeline/run.py`. With no ingestion results, `score_substation` is
called with no updates — the `r7_substitute_and_rescore.py` shape, but inside
the function that owns the write.

This is the point of the whole design. **It adds no writer.** `merge_and_rescore`
and `score_substation` already own these fields; the change lets them be reached
without an ingestion pass. The unsanctioned-writer count in the conformance
register goes *down* by one when 3.3 lands, and the next formula change does not
raise it.

Dry run is the default and reports per country: records stale by fingerprint,
of those how many reproduce within 0.005, how many move, and band movement in
both rules — absolute `classify_band` and per-country
`classify_band_normalised`. The five stale-baseline countries are reported
separately and never folded into a cohort figure.

### 3.3 Seed the Monte Carlo

`score_substation` passes a seed derived deterministically from
`substation_id`. Same record, same inputs, same formula ⇒ bit-identical output.

Without this, §3.2's dry run cannot distinguish a record the new R3 moved from a
record the RNG moved, and 2.2's reproduction test — the evidence that this is
safe at all — degrades every time it is re-run. With it, "this record moved"
becomes a statement about the formula by construction.

It also repairs something larger: the published estate is currently not
reproducible. A third party re-running the pipeline on identical inputs gets
different numbers in the third decimal. For an index whose purpose is supporting
policy decision-making, that is a defect independent of any of the above.

**This is itself a formula change.** It will move every record with a non-zero
CI by up to ~0.003, and it must therefore land in the *same* pass as the R3
re-derivation, not before or after it — one movement across the estate, declared
once, not two movements that have to be disentangled afterwards. That is the
main sequencing constraint in this document.

---

## 4. What this design does not do

  * **It does not settle `classification`.** `score_substation` assigns the
    absolute band; the published band is the per-country percentile of Phase 2D.
    `scripts/normalise_bands_per_country.py --all-countries` must follow, as it
    did after Phase zeta. Band movement reported by the dry run is provisional
    in both rules until it does.

  * **It does not repair the five stale-baseline countries.** Their published
    `mult_product` does not reproduce from their own modifiers. A rescore-only
    pass will move those 397,852 records by the substitution *plus* the
    accumulated drift, and this design inherits `r7_substitute_and_rescore.py`'s
    refusal to quote that as one number. Separating the two is its own task and
    is not attempted here.

  * **It does not fix record-level `version`.** §2.1 is a finding this design
    depends on, not one it closes. The fix is in the ~20 per-country
    `merge_into_ssi_data.py` templates and belongs to the ingestion layer.

  * **It does not decide whether the 373 zeros are pre-L3 artefacts or a live
    bug.** It repairs their values. Why a zero was written where a value existed
    is unanswered, and three slovenia records are too small a sample to answer
    it. Norway's 271 (4.4% of the country) is where that question should be put.

---

## 5. Sequence

Pin 5. Each lands before the next starts.

1. `land_20260921_BE_BF.sh` — the R3 re-derivation. **Not yet run**, measured
   from both reflogs on 24 September: `master documents` stops at the
   conformance ratchet, the site repo at the BD recommendation doctrine.
2. This document.
3. §3.1 — the fingerprint, plus a test that a changed `R3_PARAMS` moves it.
4. §3.3 — the seed, plus a test that two scorings of one record are identical.
5. §3.2 — the rescore-only branch, dry run only, with the per-country report.
6. Measure. 39 dry runs, read before anything is written.
7. Write, country by country, with `normalise_bands_per_country.py` following.
8. The 373 zeros and the `version` repair, as separate work.

Steps 3–5 are three commits, not one. Step 6 is the gate: if the dry run says
the estate moves more than the R3 re-derivation and the seed can account for,
the answer is to stop and find out why, not to write.

---

## 6. Open

  * What seed derivation? `substation_id` is not stable across history —
    `FINDING_R3_C_mult_has_no_single_writer` established that ids turned over
    for spain, portugal and iceland. A seed derived from an unstable id means a
    record's numbers change identity when its id does. The alternative is to
    seed from the record's own component values, which is stable under renaming
    but changes whenever an input changes — which is correct behaviour, since an
    input change should rescore anyway. Leaning to the latter; unresolved.
  * Does the fingerprint belong on the record or on the shard manifest? Per
    record is 622,104 copies of the same short string. Per shard is smaller but
    cannot express a partially-rescored shard, which is exactly the state
    Phase zeta left behind. Leaning to per record for that reason.
  * Cost of the full pass, measured rather than extrapolated. 4.8 ms per record
    gives 50 minutes for the estate; that figure predates the R3 change and
    should be re-measured on one country before 39 are booked.
