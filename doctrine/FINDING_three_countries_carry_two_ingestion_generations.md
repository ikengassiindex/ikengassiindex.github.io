# FINDING — three countries carry two ingestion generations in one file

Measured 24 September 2026, all 39 countries. Generalises
`FINDING_sweden_publishes_2582_substations_its_manifest_does_not_count.md`,
which reported this for one country and treated it as one country's problem.
It is not.

---

## 1. The scan

Every record's `substation_id`, grouped by scheme. Three countries do not
have one scheme:

| country | records | family A | family B |
|---|---:|---|---|
| greece | 719 | `GR-` 556 | `GR_` 163 |
| sweden | 3,774 | numeric 10-digit 1,192 | `SE_` 2,582 |
| turkey | 4,031 | `TR-` 4,001 | **no id at all** 30 |

The other 36 are uniform.

## 2. Each second generation is missing something DIFFERENT

This is the part that matters, and the reason a single fix will not do.

    country  family      n      components  zero-CI  catchment  R7_cyber_v2
    greece   GR-       556             556        0        556          556
    greece   GR_       163               0      163        163          163
    sweden   numeric 1,192           1,192        0      1,189        1,192
    sweden   SE_     2,582           2,582        0          0            0
    turkey   TR-     4,001           4,001        6      4,000        4,001
    turkey   <none>     30               0        0         30           30

  * **greece `GR_`** — 163 records with NO components. R_base is therefore
    exactly 0 and no Monte Carlo runs, which is why all 163 have a zero-width
    confidence interval. They have catchment and R7_cyber_v2. They are part
    of the 78,558-record "components absent" population that
    `FINDING_R_base_is_hash_or_zero.md` measures at 12.6% of the estate.
  * **sweden `SE_`** — 2,582 records with components but NO catchment and NO
    R7_cyber_v2. They missed Task #451 and the R7 cutover.
  * **turkey `<none>`** — 30 records with catchment and R7_cyber_v2 but NO
    components and NO `substation_id`. They have `osm_id`, real names
    ("Yunus TM") and coordinates.

Three countries, three different deficits. The common structure is that a
later ingestion APPENDED records beside an existing set rather than replacing
or enriching it, and each append happened at a different point in the
enrichment chain's history — so each set is missing whatever had not yet run,
or whatever ran keyed to the id scheme it does not share.

## 3. What it has already cost

  * **turkey was not measured in the 39-country dry run at all.**
    `merge_and_rescore` does `sid = sub["substation_id"]` as a subscript, so
    30 records without one raise `KeyError` and take the whole country with
    them. 4,031 records unmeasured because of 30.
  * **sweden's 2,582** lose R3 entirely under the re-derivation, correctly
    (Convention #56, no catchment), which would publish a visible absence on
    68% of one country and read as a methodology fault.
  * **greece's 163** are scored and banded and published with `R_base` of
    exactly zero.
  * Sweden's file declares `meta.n_substations: 1192` while carrying 3,774,
    and the site publishes 3,774.

## 4. The detection that would have caught all three

Each of these was found by a different accident — sweden by chasing a
catchment gap, turkey by a crash in a sweep, greece by noticing that a
live-MC count matched an id-family count. None was found by a check.

A check that reads the artefact would be: **within one country, every record
carries the same id scheme and the same set of enrichment markers.** Both
halves are cheap and neither exists. That belongs beside the cardinality
ratchet in `tests/test_migration_score_niva.py`, as a per-country invariant
pinned from measurement — 36 countries uniform today, three exceptions
declared with their counts, and the ceiling falling to zero as they are
fixed.

## 5. Open

  * What produced each second generation, and when. Not established for any
    of the three.
  * Whether the 30 turkish and 2,582 swedish records are network substations
    or distribution assets. Sweden's `SE_` set includes "ICA Maxi", a
    supermarket chain; turkey's includes "Yunus TM", which reads as a real
    substation name.
  * Whether any country carries a second generation that shares the first's
    id scheme, which this scan cannot see.
