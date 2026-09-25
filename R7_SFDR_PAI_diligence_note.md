# R7 SFDR PAI Infrastructure Disclosure — Phase 1 Diligence Findings

**Date**: 16 July 2026
**Author**: ikenga-ssi-foundation
**Trigger**: Poland P21 empirical audit surfaced "6 ESG READY" pipeline report while operator noted framework has 7 canonical reports
**Companion**: R7_SFDR_PAI_current_state_audit.md (Phase 2 — per-country audit)

---

## 1. Executive summary

**R7 SFDR PAI Infrastructure Disclosure IS a documented v4.2 framework requirement** per Formula Construct v3 §14 subsection 13.7. It exists as the **seventh axis of the ESG Radar** in every country's `esg-report.html` announcement text. However, three implementation layers currently lag the FC v3 §14 methodology upgrade:

1. **Pipeline registry** (`scripts/pipeline/config.py::ESG_REPORTS`): only 6 entries (R1-R6); R7 absent
2. **Frontend renderer** (`esg-sections.js::ESG_REPORTS` array): only 6 entries; R7 absent from Section B dynamic rendering
3. **Historical closure YAMLs**: every prior country's audit YAML reports `esg_reports_ready_count: 6` reflecting pipeline count, not framework catalog count

**Good news — the data foundation is already in place**: R7 SFDR PAI is a **Re_norm proxy under Convention #7 (Data-Layer Anchoring)**. Every substation in every v4.2 canonical ssi-data.json already has `Re_normalised` populated (per Convention #66 — Re_normalised is in the 20 EXPECTED_KEYS and NOT in NULLABLE_KEYS). This means Phase 4 implementation is primarily wiring (registry + renderer + doc cascade) — NOT new data ingestion.

---

## 2. R7 duality — the critical distinction

There are **TWO distinct R7s** in SSI Index v4.2, intentionally sharing the same number by design:

### R7a — Formula-modifier R7 (v4.0.2 baseline formula-chain)

- **Full name**: R7 Digital Readiness (a.k.a. R7_cyber)
- **Documented in**: methodology.html §269-270 + line 145 formula box
- **Formula**: `R7 = desi_digital_index(region, voltage)` returning `[0.99, 1.05]`
- **Role**: Multiplicative modifier in the master rescore equation
- **Used by ESG reports**: R6 "Cybersecurity Exposure" (uses `modifiers.R7_cyber` as its primary input variable)
- **Convention #78 §Class A**: Currently under R7_cyber drift monitoring (chile/slovenia/norway/australia)

### R7b — ESG-axis R7 (FC v3 §14 subsection 13.7)

- **Full name**: R7 — SFDR Principal Adverse Impact Statement (Infrastructure Module)
- **Short name**: R7 SFDR PAI Infrastructure
- **Documented in**: FC v3 §14 subsection 13.7 + V4_2_IMPLEMENTATION_ARCHITECTURE.md §4.5
- **Data source**: `Re_normalised` composite (documented-proxy under Convention #7)
- **Bounds**: [0, 1] via `Re_norm = clip((Re_raw − 0.920) / (1.787 − 0.920), 0, 1)`
- **Re_raw underlying**: `Re_raw = (R6d × R6e × R8 × R9 × R10) + (R6c − 1.00)` bounded [0.920, 1.787]
- **Role**: Seventh ESG report / seventh ESG Radar axis
- **Regulatory framework anchor**: SFDR Article 4 Principal Adverse Impact Statement + SFDR PAI Table 1 fields (via Infrastructure Module)

**Methodology.html verbatim quote** (lines 269-275):
> "Note — R7 duality: the ESG Radar's seventh axis is **R7 SFDR PAI Infrastructure** (FC v3 §14 subsection 13.7 "R7 — SFDR Principal Adverse Impact Statement (Infrastructure Module)"), populated by the Re_norm composite as a documented-proxy under Convention #7 (Data-Layer Anchoring). The R7 *formula modifier* (this row) and the R7 *ESG axis* share the same numbering by design — they index different surfaces of v4.2 (rescore formula vs ESG disclosure) and are intentionally not unified at the numbering layer."

---

## 3. Current implementation state matrix

| Layer | Location | R1-R6 present | R7 SFDR PAI present | Status |
|---|---|:-:|:-:|---|
| **Framework announcement** (section-sub text) | `<country>/esg-report.html` line 145 | ✅ | ✅ | Announces 7 reports per FC v3 §14 |
| **Frontend dynamic renderer** (Section B) | `esg-sections.js::ESG_REPORTS` array (line 40) | ✅ | ❌ | Only 6 reports rendered; R7 missing |
| **Pipeline readiness assessor** | `scripts/pipeline/config.py::ESG_REPORTS` dict (line 84) | ✅ | ❌ | Only 6 reports assessed; R7 missing |
| **Data foundation** | `ssi-data.json.v4.2::substations[].Re_normalised` | ✅ | ✅ | Per Convention #66 EXPECTED_KEYS — R7 data ALREADY populated |
| **Methodology documentation** | `<country>/methodology.html` §270-275 R7 duality block | ✅ | ✅ | Explicitly documents R7 duality + Re_norm proxy |
| **Historical closure YAMLs** | Wave 1 P1-P5 + Wave 2 P1-P21 audit YAMLs | ✅ | ❌ | All report "esg_reports_ready_count: 6" |

---

## 4. Additional finding — R3/R4/R5 name drift between announcement and renderer

The `<country>/esg-report.html` section-sub text (line 145) announces the FC v3 §14 canonical names + order:
- R1 Climate Physical
- R2 Grid Equity & Social
- R3 Infrastructure Resilience **[Re composite ESG home]**
- R4 Pollution & Corrosion
- R5 Energy Transition & DER Stress
- R6 Cybersecurity
- R7 SFDR PAI Infrastructure

But `esg-sections.js::ESG_REPORTS` renders the FC v2 legacy names + order:
- report-1: Climate Physical Risk Assessment ✅ matches
- report-2: Grid Equity & Social Vulnerability ✅ matches
- report-3: **EU Taxonomy Alignment** ❌ FC v3 wants "Infrastructure Resilience"
- report-4: **Energy Transition & DER Stress** ❌ FC v3 wants "Pollution & Corrosion" here
- report-5: **Pollution & Corrosion** ❌ FC v3 wants "Energy Transition & DER Stress" here (R4↔R5 swapped)
- report-6: Cybersecurity Exposure ✅ matches
- (R7 missing entirely)

This is a **known FC v2 → FC v3 §14 methodology upgrade** that was announced in the section-sub text but never propagated to the renderer/pipeline layers. Any R7 implementation should either:
- **Option minimal**: Add R7 only, leave R3/R4/R5 label drift as-is (defer to separate workstream)
- **Option full**: Fix R3/R4/R5 renames + R4↔R5 swap alongside R7 addition (single coherent FC v3 §14 alignment)

Operator decision required in Phase 3.

---

## 5. R7 SFDR PAI regulatory framework anchor

**SFDR** = EU Sustainable Finance Disclosure Regulation (EU 2019/2088)
- **Article 4**: Principal Adverse Impact (PAI) statement mandatory for large financial market participants
- **Delegated Regulation (EU) 2022/1288**: SFDR RTS (Regulatory Technical Standards) — defines PAI Table 1 (18 mandatory indicators) + Table 2 (optional environmental) + Table 3 (optional social)
- **PAI Table 1 indicators most relevant to infrastructure**:
  - #1 GHG emissions (Scope 1/2/3)
  - #2 Carbon footprint
  - #3 GHG intensity of investee companies
  - #4 Exposure to fossil fuel sector
  - #5 Share of non-renewable energy consumption/production
  - #6 Energy consumption intensity per NACE sector
  - #7 Activities negatively affecting biodiversity-sensitive areas
  - #8 Emissions to water
  - #9 Hazardous & radioactive waste ratio

**Infrastructure Module** (per FC v3 §14 subsection 13.7):
- The SSI-Foundation Infrastructure Module maps `Re_normalised` composite as the aggregate **infrastructure resilience proxy** feeding into a financial participant's SFDR PAI statement
- Convention #7 (Data-Layer Anchoring) defines Re_normalised as authoritative proxy
- Bounds [0, 1] — higher Re_norm = higher resilience = LOWER adverse impact
- Interpretation: Re_norm ≥ 0.7 = "resilience infrastructure asset" for SFDR PAI purposes

---

## 6. R7 SFDR PAI readiness assessment logic (proposed)

Following the existing 6-report pattern in `scripts/pipeline/enrichment/merge.py::assess_esg_readiness()`:

```python
"R7": {
    "name": "SFDR PAI Infrastructure Disclosure",
    "framework": "SFDR Article 4 · PAI Table 1 · Delegated Reg (EU) 2022/1288 · Infrastructure Module",
    "primary_sdg": 12,  # Responsible Consumption & Production
    "variables": ["Re_normalised", "Re_raw", "R6c", "R6d", "R6e", "R8", "R9", "R10"],
    "required_fields": ["Re_normalised"],
},
```

**Readiness gate**: `min_pct >= 80` where `pct = count(substations with Re_normalised != null) / total * 100`

**Expected empirical**: Every country that completed v4.2 canonical migration (Convention #66 EXPECTED_KEYS) will report R7 = 100% READY by construction, since Re_normalised is a non-nullable expected key.

**Countries at risk of R7 GAP/PARTIAL**: Any country whose ssi-data.json is still on the flat-list root schema (Latvia post-Task #248 Phase 1 intermediate state per Convention #78 §4bis.4) OR any country whose L2/L3/L4 rescore did not yet run post-L1-refresh (per Convention #78 §4bis.4 two-phase workflow discipline).

---

## 7. Phase 2 audit scope (queued as Task #296)

The next phase will verify per-country:
1. Does `<country>/esg-report.html` line 145 section-sub announce 7 reports? (spot-check ~40 countries)
2. Is `Re_normalised` populated on every substation in `<country>/ssi-data.json`?
3. Is `<country>/methodology.html` R7 duality block present?
4. What per-country distribution of Re_normalised values (median, min, max)?
5. Does country render any partial R7 block or is Section B strictly 6 reports?

Deliverable: `R7_SFDR_PAI_current_state_audit.md` matrix (40 countries × 5 columns).

---

## 8. Phase 3 design options (preview — decision required)

**Option A — Minimal (pipeline registry only)**
- Add R7 entry to `scripts/pipeline/config.py::ESG_REPORTS`
- Re-run `pipeline.run` per country to emit 7/7 READY
- Retrospective backfill prior country closure YAMLs `esg_reports_ready_count: 6→7`
- **Skip**: frontend renderer + R3/R4/R5 label drift
- **Effort**: ~2 hours code + 40-country reprocess

**Option B — Full R7 implementation (pipeline + frontend)**
- Option A PLUS
- Add R7 rendering block to `esg-sections.js::ESG_REPORTS` array
- getProfile/getVariables/why/sdgRationale populated per FC v3 §14 subsection 13.7 spec
- **Skip**: R3/R4/R5 label drift
- **Effort**: ~1 day code + 40-country reprocess + frontend cache-bust

**Option C — Full FC v3 §14 alignment**
- Option B PLUS
- Rename R3 "EU Taxonomy Alignment" → "R3 Infrastructure Resilience [Re composite home]"
- Swap R4/R5 to FC v3 canonical order (R4=Pollution, R5=Transition)
- Update every methodology + esg-report doc cascade to FC v3 §14
- **Effort**: ~2-3 days + retrospective doc cascade across 40 countries

**Recommendation** (subject to operator sign-off in Phase 3): **Option B** — closes R7 gap end-to-end while deferring the R3/R4/R5 label drift as a separate scoped workstream (Option C could be Q3 2026 methodology-hardening pass, not blocking Poland P21 Step 5 close).

---

## 9. Convention preservation matrix

| Convention | Impact | Preservation strategy |
|---|---|---|
| **#7** Data-Layer Anchoring | R7 SFDR PAI = Re_norm proxy per Convention #7 | Existing Re_normalised field remains authoritative source |
| **#56** Visibly-honest degradation | R7 must NOT silently default to READY for countries without Re_normalised | Per-country empirical Re_normalised presence check gates READY status |
| **#60** Non-commercial provenance | SFDR PAI Table 1 anchor is EU regulatory, not commercial | OK |
| **#66** v4.2 canonical schema | Re_normalised is EXPECTED_KEY not NULLABLE — every sub MUST have it | R7 assessor reinforces this constraint at ESG-report level |
| **#78 §4bis.4** Two-phase workflow | L1 ingestion first, L2/L3/L4 rescore second — R7 readiness is Phase 2 output | R7 assessed only after pipeline.run (not at L1 fetch time) |

---

## 10. Non-goals for this workstream

- **Does NOT touch R7_cyber formula modifier** (v4.0.2 baseline) — that's the R7 duality's other half; Class A drift monitoring already exists for it via Task #159/#181
- **Does NOT change methodology.html cyber-modifier row** (R7a) — the R7 duality is intentional per V4_2_IMPLEMENTATION_ARCHITECTURE.md §4.5
- **Does NOT add new data ingestion source** — R7 uses existing Re_normalised (already computed at Phase 2 rescore)
- **Does NOT retroactively rescore Wave 1 countries** — those already have Re_normalised populated; only the pipeline READY assessment needs updating

---

## 11. Phase 1 → Phase 2 handoff

**Phase 1 outputs**:
- ✅ R7 duality clarified (formula-modifier vs ESG-axis)
- ✅ Data source identified: Re_normalised (already present per Convention #66)
- ✅ Framework anchor: FC v3 §14 subsection 13.7 + SFDR Article 4 + PAI Table 1
- ✅ Implementation gap mapped across 4 layers (pipeline + frontend + docs + closure YAMLs)
- ✅ 3-option design ladder for Phase 3

**Phase 2 next steps** (Task #296):
1. Sweep all 40 `<country>/esg-report.html` files for R7 announcement text (grep the section-sub)
2. Sweep all 40 `<country>/ssi-data.json` files for Re_normalised field presence + non-null rate
3. Sweep all 40 `<country>/methodology.html` files for R7 duality block
4. Build 40 × 5 matrix table with per-country R7 readiness classification
5. Identify any outlier countries (e.g., Latvia flat-list schema — may need special handling)

---

*Phase 1 diligence complete 16 July 2026.*
