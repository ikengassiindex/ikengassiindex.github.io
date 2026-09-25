# R7 SFDR PAI Infrastructure Disclosure — Phase 2 Per-Country Audit

**Date**: 16 July 2026
**Author**: ikenga-ssi-foundation
**Data source**: `R7_SFDR_PAI_per_country_audit_data.json` (sandbox-generated 16 July 2026 20:30 UTC)
**Companion**: `R7_SFDR_PAI_diligence_note.md` (Phase 1 — methodology anchor)

---

## 1. Executive summary

**39-country empirical R7 SFDR PAI readiness** (measured by `Re_normalised` presence rate on ssi-data.json substations):

- 🟢 **24/39 READY** (Re_normalised populated ≥80%) — 61.5% of cohort
- 🟡 **6/39 PARTIAL** (30-80%) — 15.4% of cohort
- 🔴 **9/39 GAP** (<30%) — 23.1% of cohort
- ⚠️ **0/39 ERROR/MISSING** — 100% of cohort has esg-report.html + ssi-data.json + R7 announced

**Framework consistency**: 39/39 countries announce R7 in `<slug>/esg-report.html` line 145 section-sub text ("Composite readiness across 7 ESG dimensions per FC v3 §14"). No country is architecturally missing R7 documentation.

**Root cause of GAP/PARTIAL countries**: These are countries that recently completed **L1 substation ingestion refresh** (adding net-new subs via OSM Overpass merge) but have NOT completed a Phase 2 modifier-chain rescore — so net-new subs carry neutral defaults per Convention #56 (Re_raw=1.0, Re_norm=0.0, R_median=0.0, modifiers={}). This is the **Convention #78 §4bis.4 two-phase workflow** in transient state, exactly as designed.

---

## 2. Per-country empirical matrix

| # | Slug | esg-report.html | R7 announced | Schema | Total subs | Re_norm populated | % | R7 Status |
|---:|---|:-:|:-:|---|---:|---:|---:|:-:|
| 1 | australia | ✅ | ✅ | dict_with_key | 12,565 | 7,684 | 61.2% | 🟡 PARTIAL |
| 2 | austria | ✅ | ✅ | dict_with_key | 14,720 | 717 | 4.9% | 🔴 GAP |
| 3 | belgium | ✅ | ✅ | dict_with_key | 6,651 | 1,155 | 17.4% | 🔴 GAP |
| 4 | canada | ✅ | ✅ | dict_with_key | 7,626 | 5,924 | 77.7% | 🟡 PARTIAL |
| 5 | chile | ✅ | ✅ | dict_with_key | 1,035 | 915 | 88.4% | 🟢 READY |
| 6 | colombia | ✅ | ✅ | dict_with_key | 744 | 358 | 48.1% | 🟡 PARTIAL |
| 7 | costa-rica | ✅ | ✅ | dict_with_key | 169 | 159 | 94.1% | 🟢 READY |
| 8 | czechia | ✅ | ✅ | dict_with_key | 8,899 | 1,016 | 11.4% | 🔴 GAP |
| 9 | denmark | ✅ | ✅ | dict_with_key | 2,433 | 2,283 | 93.8% | 🟢 READY |
| 10 | estonia | ✅ | ✅ | dict_with_key | 1,794 | 583 | 32.5% | 🟡 PARTIAL |
| 11 | finland | ✅ | ✅ | dict_with_key | 3,885 | 3,682 | 94.8% | 🟢 READY |
| 12 | france | ✅ | ✅ | dict_with_key | 7,378 | 6,974 | 94.5% | 🟢 READY |
| 13 | germany | ✅ | ✅ | dict_with_key | 12,628 | 11,920 | 94.4% | 🟢 READY |
| 14 | greece | ✅ | ✅ | dict_with_key | 556 | 525 | 94.4% | 🟢 READY |
| 15 | greenland | ✅ | ✅ | dict_with_key | 43 | 34 | 79.1% | 🟡 PARTIAL |
| 16 | hungary | ✅ | ✅ | dict_with_key | 3,507 | 3,309 | 94.4% | 🟢 READY |
| 17 | iceland | ✅ | ✅ | dict_with_key | 684 | 647 | 94.6% | 🟢 READY |
| 18 | ireland | ✅ | ✅ | dict_with_key | 994 | 942 | 94.8% | 🟢 READY |
| 19 | israel | ✅ | ✅ | dict_with_key | 257 | 244 | 94.9% | 🟢 READY |
| 20 | italy | ✅ | ✅ | dict_with_key | 4,293 | 4,293 | **100.0%** | 🟢 READY |
| 21 | japan | ✅ | ✅ | dict_with_key | 5,893 | 5,591 | 94.9% | 🟢 READY |
| 22 | korea | ✅ | ✅ | dict_with_key | 1,290 | 1,221 | 94.7% | 🟢 READY |
| 23 | latvia | ✅ | ✅ | dict_with_key | 4,646 | 1,157 | 24.9% | 🔴 GAP |
| 24 | lithuania | ✅ | ✅ | dict_with_key | 4,901 | 478 | 9.8% | 🔴 GAP |
| 25 | luxembourg | ✅ | ✅ | dict_with_key | 723 | 84 | 11.6% | 🔴 GAP |
| 26 | mexico | ✅ | ✅ | dict_with_key | 3,085 | 2,290 | 74.2% | 🟡 PARTIAL |
| 27 | netherlands | ✅ | ✅ | dict_with_key | 5,449 | 1,552 | 28.5% | 🔴 GAP |
| 28 | new-zealand | ✅ | ✅ | dict_with_key | 1,558 | 1,480 | 95.0% | 🟢 READY |
| 29 | norway | ✅ | ✅ | dict_with_key | 6,113 | 5,519 | 90.3% | 🟢 READY |
| 30 | poland ⭐ | ✅ | ✅ | dict_with_key | 27,764 | 2,129 | 7.7% | 🔴 GAP |
| 31 | portugal | ✅ | ✅ | dict_with_key | 10,066 | 9,579 | 95.2% | 🟢 READY |
| 32 | slovakia | ✅ | ✅ | dict_with_key | 1,517 | 1,437 | 94.7% | 🟢 READY |
| 33 | slovenia | ✅ | ✅ | dict_with_key | 1,731 | 149 | 8.6% | 🔴 GAP |
| 34 | spain | ✅ | ✅ | dict_with_key | 3,423 | 3,277 | 95.7% | 🟢 READY |
| 35 | sweden | ✅ | ✅ | dict_with_key | 3,744 | 3,556 | 95.0% | 🟢 READY |
| 36 | switzerland | ✅ | ✅ | dict_with_key | 947 | 898 | 94.8% | 🟢 READY |
| 37 | turkey | ✅ | ✅ | dict_with_key | 4,001 | 3,797 | 94.9% | 🟢 READY |
| 38 | uk | ✅ | ✅ | dict_with_key | 2,551 | 2,425 | 95.1% | 🟢 READY |
| 39 | us | ✅ | ✅ | dict_with_key | 44,634 | 42,344 | 94.9% | 🟢 READY |

⭐ Poland just closed P21 Step 4 (16 Jul 2026, this session)

---

## 3. Pattern analysis — GAP/PARTIAL correlate with recent L1 refresh

The **9 GAP countries** (Re_norm <30%) correlate with **recent L1 substation-ingestion refresh** where OSM Overpass merge added large net-new sub cohorts that carry neutral defaults:

| Country | Total | Re_norm populated | Baseline pre-L1-refresh (approx) | Net-new fresh (approx) | Δ Recent L1 refresh |
|---|---:|---:|---:|---:|---|
| **poland** (P21) | 27,764 | 2,129 | ~2,247 baseline | ~25,517 net-new | 🔥 Just landed (this session, 16 Jul) |
| **czechia** (P20) | 8,899 | 1,016 | ~1,074 baseline | ~7,825 net-new | 🔥 Just landed (16 Jul) |
| **austria** (Wave 1) | 14,720 | 717 | ~1,406 → 741 post-D#36 | ~13,979 net-new | Wave 1 refresh + Wave 1c |
| **slovenia** (P8) | 1,731 | 149 | small baseline | most fresh | Wave 2 refresh |
| **luxembourg** (P6) | 723 | 84 | small baseline | most fresh | Wave 2 refresh |
| **belgium** (P2) | 6,651 | 1,155 | ~1,155 baseline | ~5,496 net-new | Wave 2 refresh |
| **lithuania** (P12) | 4,901 | 478 | small baseline | most fresh | Wave 2 refresh |
| **netherlands** (P3) | 5,449 | 1,552 | ~1,552 baseline | ~3,897 net-new | Wave 2 refresh |
| **latvia** (P17) | 4,646 | 1,157 | ~1,157 baseline | ~3,489 net-new | Wave 2 refresh + flat-list schema |

The **6 PARTIAL countries** are in transition — L1 refresh was some time ago, partial modifier-chain rescore has landed:

| Country | Total | Re_norm populated | Interpretation |
|---|---:|---:|---|
| **canada** (P1) | 7,626 | 5,924 (77.7%) | Post-L1-refresh partial rescore, near threshold |
| **greenland** (P5) | 43 | 34 (79.1%) | Post-L1-refresh partial, near threshold; small denominator |
| **mexico** (P3) | 3,085 | 2,290 (74.2%) | Post-L1-refresh partial rescore |
| **australia** (Wave 2) | 12,565 | 7,684 (61.2%) | Post-Wave-2 refresh partial rescore |
| **colombia** (P10) | 744 | 358 (48.1%) | Post-Wave-2 refresh partial rescore |
| **estonia** (P13) | 1,794 | 583 (32.5%) | Post-Wave-2 refresh minimal rescore |

The **24 READY countries** are at ~94-95%+ Re_norm — indicating full modifier-chain rescore has completed since last L1 event. Italy at 100% is the reference country (pre-L1-refresh baseline maintained since v4.2 promotion).

---

## 4. Root cause forensic — modifier-chain rescore vs pipeline.run

**Findings from grep sweep of `scripts/`**:

Every per-country `merge_into_ssi_data.py` (L1 merger) initializes net-new subs with:
```python
"Re_raw": 1.0,          # v4.2 master equation multiplicative neutral
"Re_norm": 0.0,          # 0 additive contribution
"modifiers": {},         # empty per Convention #56
"R_median": None,        # per Convention #37 defensive None-guard
```

This is **Convention #56 visibly-honest degradation by design** — net-new subs get NEUTRAL defaults so downstream code can distinguish "not yet computed" from "computed but ambiguous".

The `pipeline.run <country>` command runs Phase 1 (seismic + climate + socio_economic overlays) + Phase 2 (MC rescore of R_median). **But `pipeline.run` does NOT compute modifiers or Re_raw/Re_norm for net-new subs** — the modifier-chain rescore is a **separate pass** that runs via:
- `scripts/refresh_f_l4_2_legacy_drift.py` (clips existing modifiers to registry bounds; does NOT populate empty modifiers)
- Historical `apply_v4_2_modifiers.py` (referenced in `methodology.html` — computes Re_raw + Re_norm from modifiers per §100 anchor)

Poland's post-Step-4 empirical evidence:
- **Baseline sub sample** (pre-L1-refresh, has R_median 0.8156 + full modifiers + Re_raw 1.1236 + Re_norm 0.1263) — indicates historical modifier-rescore ran on baseline
- **Fresh sub sample** (net-new, Re_raw=1.0 + Re_norm=0.0 + R_median=0.0 + modifiers={}) — indicates neutral-defaults per merge script

This means **closing the R7 SFDR PAI readiness gap for the 9 GAP + 6 PARTIAL countries requires ONE OF**:

**Path A** (most-honest): Register R7 in pipeline registry NOW; accept that 15 countries will show GAP/PARTIAL empirically until modifier-rescore completes. This IS Convention #56 visibly-honest — the R7 GAP accurately reflects that the country needs Phase 2 modifier-rescore before SFDR PAI disclosure is publishable.

**Path B** (data-first): Run modifier-chain rescore across 15 GAP/PARTIAL countries FIRST via `scripts/refresh_f_l4_2_legacy_drift.py` or successor script THEN register R7. This produces "9/40 GREEN at rollout" instead of "24/40 GREEN at rollout".

**Path C** (defensive): Extend `pipeline.run` to compute modifiers + Re_raw + Re_norm for net-new subs automatically. This closes the Convention #78 §4bis.4 two-phase workflow at the pipeline layer.

---

## 5. Convention #78 §4bis.4 two-phase workflow discipline preserved

The empirical GAP pattern for recently-L1-refreshed countries is EXACTLY what the two-phase workflow discipline predicts:

> "we would first bring all additional substations and power lines, and only after we would run the layers scoring etc" — operator directive 16 July 2026

- **Phase 1 (L1 ingestion)**: Adds net-new subs + lines via OSM Overpass merge with Re defaults per Convention #56
- **Phase 2 (L2/L3/L4 rescore)**: Computes modifiers + Re_raw + Re_norm for all subs cohort-wide

The 9 GAP countries are correctly in Phase-1-complete/Phase-2-pending state. Closing R7 SFDR PAI readiness for them requires completing Phase 2 — NOT bypassing the two-phase discipline.

---

## 6. Cross-verification — R7 announcement vs pipeline vs data

| Layer | R7 present? | Empirical evidence |
|---|:-:|---|
| Frontend section-sub announcement | ✅ 39/39 | Every `<slug>/esg-report.html` line 145 quotes FC v3 §14 subsection 13.7 |
| Frontend renderer (esg-sections.js) | ❌ | ESG_REPORTS array has 6 entries (Line 40); Section B renders 6 blocks |
| Pipeline registry (config.py) | ❌ | ESG_REPORTS dict has 6 keys (Line 84); readiness assessor reports 6/6 |
| ssi-data.json data field | ✅ 39/39 | Every country has Re_normalised field in schema; 24/39 populated ≥80% |
| Methodology R7 duality block | ✅ (spot-checked Italy) | methodology.html §270-275 documents duality |

**Cohort-wide consistency**: The R7 SFDR PAI framework is UNIFORMLY documented across all 39 countries at the announcement + methodology layers. The gap is exclusively in the readiness-reporting + rendering layers.

---

## 7. Phase 3 design ladder — refined per Phase 2 empirical

Based on Phase 2 empirical findings, the design ladder from Phase 1 becomes more concrete:

### Option A — Minimal (Pipeline registry only) — RECOMMENDED for Wave 2 close-out

**Scope**:
- Add R7 to `scripts/pipeline/config.py::ESG_REPORTS` with `required_fields=["Re_normalised"]`
- Update `pipeline.run` output to report 7/7 or 6/7 per country's actual state
- Retrospective backfill prior country closure YAMLs (Wave 1 P1-P5 + Wave 2 P1-P21) with new schema:
  - `esg_reports_pipeline_registered_count: 7` (updated)
  - `esg_reports_ready_count: <actual per country>` (empirically computed)

**Effort**: ~2 hours code + no country reprocess (existing `Re_normalised` state is already what it is)
**Rollout state**: 24/39 GREEN + 6/39 YELLOW + 9/39 RED — accurately reflects Convention #56 visibly-honest
**Preserves**: Convention #78 §4bis.4 two-phase workflow discipline

### Option B — Full R7 rendering (Pipeline + Frontend)

**Additional scope**:
- Add R7 rendering block to `esg-sections.js::ESG_REPORTS` array (7th entry)
- getProfile: fleet Re_norm min/median/max + Re_raw distribution
- getVariables: Re_norm bounds check + modifier presence per R6c/R6d/R6e/R8/R9/R10
- SDG primary: SDG 12 (Responsible Consumption & Production)
- Framework: SFDR Article 4 · PAI Table 1 · Delegated Reg (EU) 2022/1288
- Cache-bust across 39 country pages: `esg-sections.js?v=20260716-r7`

**Effort**: ~1 day code + 39-page cache-bust + frontend rendering test
**Rollout state**: same as A, but frontend renders 7th block with GAP badge where applicable

### Option C — Full FC v3 §14 alignment (Pipeline + Frontend + R3/R4/R5 relabel)

**Additional scope**:
- Rename `R3 EU Taxonomy Alignment` → `R3 Infrastructure Resilience [Re composite home]`
- Swap R4/R5 order: R4 becomes Pollution, R5 becomes Transition (per FC v3 §14 canonical)
- Retire "R6 EU Taxonomy Alignment" mismatch in methodology.html cross-refs
- Doc cascade across 39 country methodology.html files

**Effort**: ~2-3 days + doc cascade + methodology.md update
**Rollout state**: FC v3 §14 canonical alignment complete

### Option D — Complete Phase 2 rescore for 15 GAP/PARTIAL countries FIRST

**Additional scope beyond A**:
- Run modifier-chain rescore for 15 countries via `refresh_f_l4_2_legacy_drift.py` (or extended path)
- Populate Re_norm for net-new subs across Poland, Czechia, Austria, Belgium, Latvia, Lithuania, Luxembourg, Netherlands, Slovenia + PARTIAL Canada, Greenland, Mexico, Australia, Colombia, Estonia
- Then register R7 in pipeline

**Effort**: ~1-2 days rescore + operator wall-clock per country + ~2 hours registry work
**Rollout state**: 39/39 GREEN at rollout (if rescore closes gap successfully)
**Convention impact**: Aligns with Convention #78 §4bis.4 Phase 2 completion

---

## 8. Phase 3 decision points for operator

**Required operator decisions before Phase 4 implementation**:

1. **Which option A / B / C / D?**
   - Recommendation: **Option A** (minimal) — accurately reflects Convention #78 §4bis.4 two-phase workflow state; deferred R7 GAP for recently-refreshed countries becomes a rescore backlog signal rather than a hidden gap
   - Alternative: **Option A + D** (register + rescore) — closes all countries at rollout; longer wall-clock

2. **R3/R4/R5 label drift scope?**
   - Recommendation: DEFER Option C to Q3 2026 separate methodology-hardening workstream; R7 close-out doesn't require FC v3 §14 relabelling

3. **Retrospective YAML backfill scope?**
   - Every prior country closure YAML (Wave 1 P1-P5 + Wave 2 P1-P21) claims `esg_reports_ready_count: 6`. Do we:
     - (a) Retroactively update all 26+ YAMLs with new `esg_reports_pipeline_registered_count: 7 + esg_reports_ready_count_actual: <empirical>` schema?
     - (b) Add a forward-looking note in CLAUDE.md tagline citing this cohort-wide correction?
     - (c) Both?

4. **When to close R7 workstream vs Poland P21 Step 5?**
   - Option 1: Merge R7 workstream INTO Poland P21 Step 5 doc cascade (single celebration event: 🏛 Visegrád COMPLETION + R7 registration)
   - Option 2: Close Poland P21 Step 5 FIRST (Visegrád celebration standalone) THEN start R7 workstream as separate sprint
   - Recommendation: Option 2 (cleaner separation of concerns; Visegrád COMPLETION deserves its own commit)

---

## 9. Recommended next steps

**Immediate (this session)**:
- ✅ Phase 1 diligence complete
- ✅ Phase 2 audit complete (this document)
- ⏸ Phase 3 design pending operator sign-off on decisions 1-4 above

**Post-operator-signoff (next session)**:
- Phase 4 implementation per approved option
- Phase 5 closure doc cascade

**Meanwhile / parallel**:
- Poland P21 Step 5 doc cascade (Task #294) — 🏛 Visegrád Trio COMPLETION MILESTONE (standalone workstream, unaffected by R7)

---

*Phase 2 audit complete 16 July 2026 20:30 UTC. Empirical data captured in `R7_SFDR_PAI_per_country_audit_data.json` for downstream automation.*
