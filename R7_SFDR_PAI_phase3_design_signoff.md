# R7 SFDR PAI Infrastructure Disclosure — Phase 3 Design Sign-Off

**Date**: 16 July 2026
**Author**: ikenga-ssi-foundation
**Operator sign-off**: Cedric Berard 16 Jul 2026 20:35 UTC
**Companion**: R7_SFDR_PAI_diligence_note.md (Phase 1) + R7_SFDR_PAI_current_state_audit.md (Phase 2)

---

## 1. Operator decisions (final)

Per operator's response to Phase 2 audit deliverable:

| Decision | Choice | Interpretation |
|---|---|---|
| **1. Which option?** | **A + D** | Register R7 in pipeline + rescore 15 GAP/PARTIAL countries BEFORE registration flip → 39/39 GREEN at rollout |
| **2. R3/R4/R5 label drift?** | **DO NOT DEFER — address NOW** | Fix FC v3 §14 label drift (R3 → Infrastructure Resilience [Re composite home], swap R4↔R5) as part of same workstream (Option C added) |
| **3. Retrospective YAML backfill?** | **BOTH (c)** | Retroactively update ALL 26+ prior country closure YAMLs (Wave 1 P1-P5 + Wave 2 P1-P21) AND add forward-looking correction note to CLAUDE.md tagline |
| **4. Sequence vs Poland P21 Step 5?** | **Sequence 2** | Poland P21 Step 5 (🏛 Visegrád COMPLETION) FIRST, R7 workstream SECOND |

**Final scope**: **A + C + D + Both (a)+(b) backfill** = MAXIMUM SCOPE — full R7 registration + FC v3 §14 label alignment + Phase 2 rescore for all 15 GAP/PARTIAL + full retroactive audit trail + forward-looking correction.

---

## 2. Phase 4 implementation plan (FULL SCOPE)

### Phase 4a — Pipeline code changes (Option A)

**File**: `scripts/pipeline/config.py`

Add R7 entry to `ESG_REPORTS` dict at line 84:

```python
"R7": {
    "name": "SFDR PAI Infrastructure Disclosure",
    "framework": "SFDR Article 4 · PAI Table 1 · Delegated Reg (EU) 2022/1288 · FC v3 §14 subsection 13.7 · Infrastructure Module",
    "primary_sdg": 12,  # Responsible Consumption & Production
    "variables": ["Re_normalised", "Re_raw", "R6c_flood", "R6d_wildfire", "R6e_winter", "R8_adapt", "R9_compound", "R10_just"],
    "required_fields": ["Re_normalised"],
},
```

**File**: `scripts/pipeline/enrichment/merge.py`

Extend `assess_esg_readiness()` to handle Re_normalised at top level (currently field paths assume nested dict, e.g., `seismic.pga_g`). Convention #56: check `s.get('Re_normalised') is not None AND s.get('Re_normalised') > 0` (Re_normalised=0.0 is neutral-default per net-new sub initialization; only counts as READY when actual composite computed).

**File**: `scripts/pipeline/config.py`

Update R3/R4/R5 to FC v3 §14 canonical order (Option C):
```python
"R3": {
    "name": "Infrastructure Resilience [Re composite home]",  # renamed from "EU Taxonomy Alignment"
    "framework": "Climate Delegated Act · Article 11 Adaptation · Re composite anchor",
    ...
},
"R4": {
    "name": "Pollution & Corrosion",  # was R5, swapped
    "framework": "ESRS E2 Pollution · ISO 9223",
    "primary_sdg": 11,
    "variables": ["corrosion_class", "E2_local", "E_component"],
    "required_fields": ["markov.corrosion_class", "socio_economic.E2_local"],
},
"R5": {
    "name": "Energy Transition & DER Stress",  # was R4, swapped
    "framework": "ESRS E1 Transition · TCFD Transition Risk",
    "primary_sdg": 7,
    "variables": ["T1_score", "DER_ratio", "DER_variability", "EV_load_ratio"],
    "required_fields": ["transition.T1_score", "transition.DER_ratio"],
},
```

### Phase 4b — Frontend rendering (Option B implicit in C)

**File**: `esg-sections.js`

Add 7th entry to `ESG_REPORTS` array (line 40-272 currently):

```javascript
{
  id: 'report-7', num: '7', title: 'SFDR PAI Infrastructure Disclosure',
  framework: 'SFDR Article 4 · PAI Table 1 · Delegated Reg (EU) 2022/1288 · FC v3 §14 subsection 13.7 · Infrastructure Module',
  sdgPrimary: { num: 12, label: 'SDG 12', name: 'Responsible Consumption & Production', color: '#bf8b2e' },
  sdgSecondary: [
    { num: 9, label: 'SDG 9', color: '#f36d25' },
    { num: 13, label: 'SDG 13', color: '#48773c' }
  ],
  legendColor: '#bf8b2e',
  why: 'SFDR Article 4 mandates PAI (Principal Adverse Impact) disclosure for large financial market participants investing in infrastructure. The FC v3 §14 Infrastructure Module operationalises PAI Table 1 indicators via the Re_normalised composite — a Convention #7 documented-proxy under the SSI-Foundation Data-Layer Anchoring principle. Higher Re_norm indicates higher infrastructure resilience → lower principal adverse impact for the underlying SFDR PAI statement.',
  sdgRationale: function (d) {
    var reNorm = d.Re_norm != null ? d.Re_norm : (d.Re_normalised != null ? d.Re_normalised : null);
    var reRaw = d.Re_raw != null ? d.Re_raw : null;
    return 'Target 12.6 calls for large companies to integrate sustainability information into their reporting cycle. SFDR PAI Table 1 mandates 18 indicators for financial market participants. This substation contributes to the fund-level SFDR PAI statement via Re_norm proxy = ' + (reNorm != null ? reNorm.toFixed(3) : '—') + ' (Re_raw = ' + (reRaw != null ? reRaw.toFixed(3) : '—') + '), bounded [0, 1]. Re_norm ≥ 0.7 qualifies as "resilient infrastructure asset" for SFDR PAI purposes; Re_norm < 0.3 flags for enhanced due diligence.';
  },
  getProfile: function (d) {
    var mods = d.modifiers || {};
    return [
      ['Re_norm (SFDR PAI proxy)', d.Re_norm != null ? d.Re_norm.toFixed(3) : (d.Re_normalised != null ? d.Re_normalised.toFixed(3) : '—')],
      ['Re_raw (unbounded)', d.Re_raw != null ? d.Re_raw.toFixed(3) : '—'],
      ['R6c_flood', mods.R6c_flood != null ? mods.R6c_flood.toFixed(3) : '—'],
      ['R6d_wildfire', mods.R6d_wildfire != null ? mods.R6d_wildfire.toFixed(3) : '—'],
      ['R6e_winter', mods.R6e_winter != null ? mods.R6e_winter.toFixed(3) : '—'],
      ['R8_adapt', mods.R8_adapt != null ? mods.R8_adapt.toFixed(3) : '—'],
      ['R9_compound', mods.R9_compound != null ? mods.R9_compound.toFixed(3) : '—'],
      ['R10_just', mods.R10_just != null ? mods.R10_just.toFixed(3) : '—'],
      ['SFDR PAI Status', (d.Re_norm != null && d.Re_norm >= 0.7) ? 'Resilient (Re_norm ≥ 0.7)' :
                          (d.Re_norm != null && d.Re_norm >= 0.3) ? 'Standard' :
                          (d.Re_norm != null) ? 'Enhanced DD (Re_norm < 0.3)' : 'Not yet computed']
    ];
  },
  getVariables: function (d) {
    var mods = d.modifiers || {};
    var reNorm = d.Re_norm != null ? d.Re_norm : (d.Re_normalised != null ? d.Re_normalised : null);
    return [
      ['Re_norm', 'SFDR PAI Infrastructure proxy', reNorm != null ? reNorm.toFixed(3) : '—', 'SFDR Article 4: PAI Statement Infrastructure Module', (reNorm != null && reNorm > 0) ? 'ready' : 'gap'],
      ['Re_raw', 'Unbounded composite', d.Re_raw != null ? d.Re_raw.toFixed(3) : '—', 'FC v3 §14 subsection 13.7: Documented-proxy per Convention #7', (d.Re_raw != null && d.Re_raw != 1.0) ? 'ready' : 'gap'],
      ['R6c', 'Flood modifier', mods.R6c_flood != null ? mods.R6c_flood.toFixed(3) : '—', 'PAI Table 1 #7: Biodiversity-sensitive area', mods.R6c_flood ? 'ready' : 'gap'],
      ['R6d', 'Wildfire modifier', mods.R6d_wildfire != null ? mods.R6d_wildfire.toFixed(3) : '—', 'PAI Table 1 #7: Biodiversity-sensitive area', mods.R6d_wildfire ? 'ready' : 'gap'],
      ['R6e', 'Winter modifier', mods.R6e_winter != null ? mods.R6e_winter.toFixed(3) : '—', 'PAI Table 1 optional Environmental', mods.R6e_winter ? 'ready' : 'gap'],
      ['R8', 'Adaptation modifier', mods.R8_adapt != null ? mods.R8_adapt.toFixed(3) : '—', 'ESRS E1: Adaptation measures', mods.R8_adapt ? 'ready' : 'gap'],
      ['R9', 'Compound modifier', mods.R9_compound != null ? mods.R9_compound.toFixed(3) : '—', 'FC v3 §14 compound-risk anchor', mods.R9_compound ? 'ready' : 'gap'],
      ['R10', 'Just transition modifier', mods.R10_just != null ? mods.R10_just.toFixed(3) : '—', 'PAI Table 1 #10-13 Social indicators', mods.R10_just ? 'ready' : 'gap']
    ];
  },
  validity: 'R7 SFDR PAI Infrastructure Disclosure uses Re_normalised as the SSI-Foundation documented-proxy under Convention #7 (Data-Layer Anchoring). Re_norm = clip((Re_raw − 0.920) / (1.787 − 0.920), 0, 1) where Re_raw = (R6d × R6e × R8 × R9 × R10) + (R6c − 1.00). Bounds [0, 1]. FC v3 §14 subsection 13.7 defines this axis as the R7 ESG Radar seventh dimension, distinct-by-design from the v4.0.2 formula-chain R7_cyber modifier per V4_2_IMPLEMENTATION_ARCHITECTURE.md §4.5. Fresh net-new substations post-L1 refresh carry neutral defaults (Re_raw=1.0, Re_norm=0.0) per Convention #56 visibly-honest degradation until Phase 2 modifier-chain rescore completes per Convention #78 §4bis.4 two-phase workflow discipline.'
}
```

Also rename report-3 title + swap report-4 / report-5 order to FC v3 §14 canonical (Option C).

Update `computeESGScores()` (line 310) to compute r7 = fraction of Re_norm populated substations.

### Phase 4c — Rescore 15 GAP/PARTIAL countries (Option D)

**Approach**: Run modifier-chain rescore via `scripts/refresh_f_l4_2_legacy_drift.py --all` OR extended path per operator to populate Re_norm on net-new subs.

**Target countries** (in order — smallest first to fail-fast):
1. Greenland (43 subs) — smallest, sanity check
2. Costa Rica (169 subs) — sanity check
3. Israel (257 subs)
4. Estonia (1,794)
5. Slovenia (1,731)
6. Colombia (744)
7. Luxembourg (723)
8. Latvia (4,646)
9. Lithuania (4,901)
10. Belgium (6,651)
11. Netherlands (5,449)
12. Mexico (3,085)
13. Canada (7,626)
14. Australia (12,565)
15. Austria (14,720)
16. **Czechia (8,899)** — Wave 2 P20 fresh
17. **Poland (27,764)** — Wave 2 P21 fresh (LARGEST — will drive wall-clock)

**Convention #78 §4bis.4 compliance**: This IS the Phase 2 rescore that closes the two-phase workflow for these countries.

### Phase 4d — Cache-bust 39-country esg-report.html

Update all 39 `<slug>/esg-report.html` files (except backup files):
- `esg-sections.js?v=20260625-p2b2` → `esg-sections.js?v=20260716-r7`
- `country-renderer.js?v=20260625-p2b2` → `country-renderer.js?v=20260716-r7`

### Phase 4e — Sentinel commitment

Add pytest sentinel `tests/test_esg_reports_7_axis_synchronization.py`:
- Assert `scripts/pipeline/config.py::ESG_REPORTS` has exactly 7 entries
- Assert `esg-sections.js::ESG_REPORTS` array has exactly 7 entries  
- Assert R3/R4/R5 label consistency between pipeline and frontend
- Assert R7 present in every `<slug>/esg-report.html` section-sub

---

## 3. Phase 5 doc cascade (Both retroactive + forward-looking)

### Retroactive YAML backfill (26+ files)

For every prior country closure YAML (Wave 1 P1-P5 + Wave 2 P1-P21):
- `<slug>/v4_23-ingestion-audit-<slug>-closure.yaml`
- `<slug>/v4_23-ingestion-audit-<slug>-merge.yaml`

Update schema:
```yaml
esg_reports_ready_count_at_original_closure: 6         # historical (kept)
esg_reports_pipeline_registered_count_at_original_closure: 6  # historical
esg_reports_framework_catalog_count: 7                  # NEW — always was per FC v3 §14
r7_sfdr_pai_status_at_original_closure: 
  status: UNKNOWN_UNTIL_R7_WORKSTREAM_CLOSURE_16_JUL_2026
  correction_note: >
    Pre-R7-workstream YAML claimed "6/6 READY" reflecting pipeline registry
    state at close. R7 SFDR PAI Infrastructure was in framework catalog per
    FC v3 §14 subsection 13.7 but not in scripts/pipeline/config.py::ESG_REPORTS
    registry. Corrected 16 July 2026 via R7 workstream (Phase 4 registration
    + Phase 5 retroactive backfill).
esg_reports_r7_workstream_ref: R7_SFDR_PAI_diligence_note.md + R7_SFDR_PAI_current_state_audit.md + R7_SFDR_PAI_phase3_design_signoff.md
```

Countries with retroactive backfill required:
- Wave 1: canada, norway, mexico, austria, greenland (5)
- Wave 2 P1-P10: australia, belgium, netherlands, chile, hungary, luxembourg, slovenia, costa-rica, israel, colombia (10)
- Wave 2 P11-P20: lithuania, estonia, latvia, slovakia, czechia (5)
- Wave 2 P21: poland (1 — pending Step 5 close)
- **Total: 21 country closure YAML backfills** (each with merge + closure YAML pair = ~42 file edits)

### Forward-looking CLAUDE.md tagline correction

Add to CLAUDE.md tagline after Poland P21 Step 5 celebration:

```
· R7 SFDR PAI Infrastructure Disclosure cohort-wide gap discovered + closed
  (16 Jul 2026 — R7 workstream Phases 1-5): pipeline registry 6→7 + FC v3
  §14 R3/R4/R5 label alignment + 15 GAP/PARTIAL countries rescored + retroactive
  audit trail codification across 42 prior closure YAMLs
```

### Frontend cache-bust

39-country cache-bust of `esg-sections.js?v=20260716-r7` after Phase 4b lands.

### Convention codification

Add to CLAUDE.md Conventions section:
- **Convention #79 candidate**: SSI Foundation framework catalogs (FC v3 §14 in this case) MUST have pipeline + frontend + methodology + closure-YAML implementations synchronized. Sentinel gate: `tests/test_esg_reports_7_axis_synchronization.py` runs pre-commit.

---

## 4. Execution sequence (per Sequence 2)

**PHASE 0 — Sequence 2 obligation** (this session):
1. ⏳ Poland P21 Step 5 doc cascade — 🏛 Visegrád Trio COMPLETION MILESTONE (Task #294, in progress)

**PHASE 1 — Post-Visegrád-celebration** (next session or later):
2. R7 Phase 4a — Pipeline code changes (Task #298 sub-phase)
3. R7 Phase 4b — Frontend rendering
4. R7 Phase 4c — Rescore 15 GAP/PARTIAL countries (in order, smallest first)
5. R7 Phase 4d — Cache-bust 39-country esg-report.html
6. R7 Phase 4e — Sentinel commitment

**PHASE 2 — Doc cascade closure**:
7. R7 Phase 5 — Retroactive YAML backfill (21 country pairs × 2 YAMLs = 42 files)
8. R7 Phase 5 — CLAUDE.md tagline forward-looking correction
9. R7 Phase 5 — Convention #79 candidate codification
10. R7 Phase 5 — REPORTS_FRAMING_KB.md cross-ref update

---

## 5. Estimated wall-clock

| Phase | Estimated wall-clock | Notes |
|---|---|---|
| Poland P21 Step 5 | ~1-2 hours | Sequence 2 obligation before R7 starts |
| R7 4a Pipeline code | ~30 min | config.py + merge.py edits |
| R7 4b Frontend rendering | ~1-2 hours | esg-sections.js R7 block + R3-R5 relabel |
| R7 4c Rescore 15 countries | ~3-6 hours | Depends on rescore-per-country wall-clock; Poland (27,764) alone may need ~30-60 min |
| R7 4d Cache-bust | ~30 min | 39-country sed sweep |
| R7 4e Sentinel commitment | ~30 min | pytest module + wire into CI |
| R7 5 YAML backfill | ~2-3 hours | 42 files × structured edit |
| R7 5 doc cascade | ~1-2 hours | CLAUDE.md + REPORTS_FRAMING_KB + Convention #79 |
| **R7 workstream total** | **~9-15 hours** | Multi-day workstream |

---

*Phase 3 design sign-off complete 16 July 2026 20:35 UTC. Ready for Poland P21 Step 5 execution per Sequence 2, then R7 workstream Phases 4-5 per this design.*
