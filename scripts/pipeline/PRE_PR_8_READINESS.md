# Pre-PR-8 Readiness Checklist

What needs to land before the next Phase 1 PR (PR-8) can ship. Maintained
end of Phase 1.5 (8 June 2026) post-P15-A/B/F closure.

## TL;DR

Phase 1.5 closed the **L1 ingestion gap** end-to-end:
- Socio: 39/39 SoT countries, NUTS-3 / state / canton / prefecture granularity
- Seismic: 39/39 at GEM 2023.1 0.05° (~5.5 km) + 2 native (italy, greece)
- Climate: 39/39 once operator's overnight ERA5-Land 0.1° + daily-stats batch lands

**PR-8 is the natural Phase 1 closure**: re-run validate_schema strict
mode against the F-L4-2-extended cohort with the new richer data, regenerate
PHASE_1_ACCEPTANCE_REPORT.md, and snapshot the v4.0.2 (post-P15) baseline.

---

## Gate 1 — Operator overnight tasks (must complete first)

| Item | Status | What to verify |
|---|---|---|
| **Step 3 climate batch** | ⏳ Running | `python3 scripts/pipeline/fetch_data.py --all --verify` shows `Complete: 39/39` |
| **P15-A-3 daily extremes** | ⏳ Running | `python3 scripts/pipeline/audit_climate_sanity.py` reports 0 FLAGs (the per-city sanity check lands within published envelopes) |
| **Operator commits the P15-* work** | ⏳ Pending | `git log --oneline | head -5` shows P15-A-3, P15-B-2, P15-F-2 commits |

## Gate 2 — Acceptance gates to re-run

| Gate | Command | Expected result |
|---|---|---|
| **L1 schema validation** | `pytest scripts/pipeline/tests/test_p15_ingestion_schemas.py -v` | 390 passed + 156 climate tests now passing (was skipped pre-batch) |
| **Climate sanity audit** | `python3 scripts/pipeline/audit_climate_sanity.py` | 42/42 OK or near-OK across all reference cities |
| **F-L4-2 cohort schema (strict)** | `python3 scripts/validate_schema.py --country-cohort f-l4-2-extended --strict` | Cohort goes from N FAIL → 0 FAIL (the original Phase 1 sentinel turn-green) |
| **E2E refresh harness** | `pytest tests/test_e2e_refresh.py -v` | Same 39/39 pass rate as Phase 1, BUT with richer L1 data flowing through |
| **Score-shift acceptance** | `pytest tests/test_score_shift_acceptance.py -v` | New baseline acceptable; document any material score shifts (P15-F-2's per-region socio data WILL move some R2 scores up materially — that's expected, not a regression) |
| **Full regression suite** | `pytest` | Cumulative test count (Phase 1: 412 tests, +14 new P15 tests, +4 new daily-stats tests = ~430 target) |

## Gate 3 — Documentation deliverables for PR-8

| Deliverable | Status | Owner |
|---|---|---|
| `PHASE_1_5_ACCEPTANCE_REPORT.md` | ⏳ Pending | I can draft this once climate batch lands + Gate 2 results are in |
| `scripts/pipeline/data/SOURCES_AND_LICENSES.md` | ✅ Done (P15-hygiene #134) | — |
| `scripts/pipeline/PHASE_1_5_OPERATOR_WORKFLOW.md` | ✅ Done | — |
| `AUDIT_v4_0_2_FINDINGS_MATRIX.xlsx` update with P15-* status | ⏳ Pending | Operator may want to add Phase 1.5 row to the matrix |
| `USCO_005_REFRESH_NOTE.md` | ⏳ Pending | If we're doing a USCO refresh filing, Phase 1.5 ingestion improvements deserve a stand-alone note (parallel to PR-6's USCO_004) |
| Methodology brief updates | ✅ Auto-refreshed via ssi-metadata.js DATA_SOURCES (#137) | — |

## Gate 4 — Stretch items (nice-to-have, not blocking)

| Item | Effort | Value |
|---|---|---|
| **Backfill USCO deposit specimens** with post-P15 score data | ~2h | LP-DD pack will reflect the richer per-region socio + 0.05° seismic + 0.1° climate |
| **Re-run scoring engine on a sample country** (e.g. germany) | ~30 min | Smoke-test that L1 → L2 → L3 → L4 → L5 still flows end-to-end with new data shapes |
| **Update v4.2 brief + supporting paper** with the granularity improvements | ~1h | Useful for thought-leadership; not core PR-8 |
| **Schedule next CDS overnight refresh** for the 5-year ERA5 daily-max window in early 2028 | scheduled | The 2018-2022 window will eventually drift; refresh to 2023-2027 once available |

## What PR-8 should NOT include

- New L1 ingestion sources (Phase 1.5 closed this)
- New scoring methodology changes (those are v4.2 territory)
- New per-modifier briefs (those landed in Phase 0)
- Frontend changes (those flow through naturally via ssi-metadata.js)

## PR-8 scope statement (draft)

> "PR-8: Phase 1.5 closure + v4.0.2 (post-P15) baseline snapshot. Phase 1.5 closed the
> L1 ingestion gap across 39 SoT countries for socio-economic (per-region
> NUTS-3-equivalent), climate (ERA5-Land 0.1° + true heat/ice day counts),
> and seismic (GEM 2023.1 0.05°). This PR re-runs the strict-mode validator
> against the F-L4-2-extended cohort with the new data, regenerates the
> PHASE_1_5_ACCEPTANCE_REPORT, and snapshots v4.0.2 (post-P15) as the post-P15
> baseline. No methodology changes; this is the closing PR for Phase 1."

---

## When to fire PR-8

The minimum viable trigger is **all three Gate 1 items complete**:
1. Operator's climate batch landed (Complete: 39/39 verify)
2. Climate sanity audit shows 0 FLAGs
3. P15-* work committed

At that point: run Gate 2 acceptance gates in sequence, draft `PHASE_1_5_ACCEPTANCE_REPORT.md`, tag `v4.0.2 (post-P15)`, open PR-8.
