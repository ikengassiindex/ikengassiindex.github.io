# FINDING — Sweden publishes 2,582 substations its own manifest does not count

Measured 24 September 2026, while investigating why 2,582 Swedish records
have no catchment population and would lose R3_C_mult to Convention #56
under the re-derivation landed the same day.

The catchment gap is a symptom. It should not be closed on its own.

---

## 1. Sweden holds two disjoint record sets

`sweden/ssi-data.json` carries 3,774 substations. They divide cleanly:

| | records | ids | names | voltage_kv | catchment | R7_cyber_v2 |
|---|---:|---|---|---|---|---|
| A | 1,192 | `5000001776` | `Substation 5000001776` | 400/220/132/130/70/45/40/20 | all | all |
| B | 2,582 | `SE_23470015` | `Hall`, `Isovaara`, `ICA Maxi` | 110.0 on 2,580 | none | none |

Both sets carry coordinates. Their coordinates do **not** overlap: 0 exact
matches, 3 within about 100 m. These are 2,582 different locations, not
duplicates of the 1,192.

## 2. Set A is the Wave-4 ingestion. Set B predates it.

`scripts/pipeline/ingestion/sweden/merge_into_ssi_data.py` assigns
`sub_id = str(next_sub_id)` — a 10-digit numeric id — and names each record
`f"Substation {sub_id}"` when OSM carries no name. That is set A's shape
exactly, and not set B's.

The same merger wrote `meta.n_substations: 1192`, with `n_HV: 846` and
`n_MV: 346` summing to it. So the Wave-4 ingestion produced 1,192 records,
declared 1,192, and left 2,582 older records in the array beside them. It
added without replacing, and nothing since has counted them.

## 3. They are published

`sweden/data.html` and `sweden/esg-report.html` both render
`fleet.total = 3,774`, from `fleet_summary.total`, which
`merge_and_rescore` recomputes from the array on every run. All 3,774 are
scored and banded: `bands` reads Low 2, Medium 1,488, High 2,146,
Critical 138.

So set B is live on the public site, inside the headline count, inside the
band distribution and inside every cohort figure this project has quoted —
including the 622,104 estate total and the 27,513 cohort pop_med.

## 4. What set B is missing

  * **Catchment population.** All 2,582. This is the estate's only silent
    absence: 3,570 records cohort-wide have no catchment, and the other 988
    across twelve countries carry the Task #451 marker declaring it.
  * **R7_cyber_v2** at ingestion. `scripts/r7_substitute_and_rescore.py`
    records "Sweden's 2,582 v2-less records" as the only such population,
    and computed v2 for them from the national constant. The same 2,582.
  * **`E2_local` and `rd_pct_gdp`**, present on set A.

One set of records missed three enrichment passes. That is a single event,
not three.

## 5. The voltage

2,580 of set B carry `voltage_kv = 110.0`. Sweden's transmission and
sub-transmission tiers are 400, 220, 130, 70, 40 and 20 kV; 110 kV is
Finland's, and set A shows Sweden's real ladder with no 110 at all.

**The origin of that 110 is not established.** The Wave-4 merger reads the
OSM `voltage` tag and drops a record when it is absent — it applies no
default — so the constant came from whatever path produced set B, and this
measurement did not identify it. Recorded as an open question, not a
conclusion.

Set B's names also include `ICA Maxi`, a supermarket chain, which suggests
OSM nodes tagged `power=substation` at distribution transformers rather
than at network substations. One name is not evidence; it is a reason to
look.

## 6. A separate and smaller finding: `meta.n_substations` is stale

Six countries disagree between the record array and the declared count:

| country | in array | meta says | difference |
|---|---:|---:|---:|
| sweden | 3,774 | 1,192 | **+2,582** |
| spain | 12,438 | 12,621 | −183 |
| italy | 41,662 | 47,906 | −6,244 |
| france | 168,894 | 175,660 | −6,766 |
| us | 73,859 | 97,915 | −24,056 |
| germany | 108,016 | 168,776 | −60,760 |

`fleet_summary.total` matches the array in every case, and it is what the
site renders, so no published figure is wrong because of this. Five of the
six declare MORE than they hold, which is consistent with counts written
before the cross-border and duplicate remediations removed records.

**Sweden is the only country where the array exceeds the declared count.**
That asymmetry is what makes it a different problem from the other five.

`meta.n_substations` is written by the per-country ingestion mergers and
updated by nothing else. It should either track `fleet_summary.total` or be
retired; a count that is stale in six countries and authoritative nowhere is
the `version` field's defect in another field.

## 7. What this blocks

The R3 re-derivation gives set B no consequence multiplier, correctly:
Convention #56, no catchment, no claim. But publishing 2,582 records with a
visible R3 absence — 68 per cent of Sweden — would read as a methodology
fault rather than as the ingestion gap it is.

Enriching set B with GHSL catchment would close the symptom and make the
question harder to see. It should not be done until set B's status is
settled.

## 8. Two candidate resolutions, for the operator

  1. **Set B is legitimate additional coverage.** Then the Wave-4 chain must
    run over it — catchment, R7_cyber_v2, socio — its voltage must be
    established from source rather than left at 110, and `meta.n_substations`
    must be corrected to 3,774.

  2. **Set B is superseded pre-Wave-4 data the merger failed to remove.**
    Then it is quarantined per Pin 8 by `mv` into `_to_delete/`, Sweden
    publishes 1,192, and the cohort total falls from 622,104 to 619,522.

The second would change a published estate figure, so it is the operator's
decision and not this document's. What is not in doubt is that the two sets
cannot both be right about the same country.

## 9. What was NOT established

  * Which path produced set B, and when.
  * Where its 110 kV constant came from.
  * Whether set B's records are network substations or distribution
    transformers.
  * Whether any other country carries a second, undeclared record set. The
    §6 table rules it out wherever `meta.n_substations` exists and exceeds
    nothing, but a country whose stale meta happens to match its array
    would not show up in it.
