# R7 SFDR PAI Phase 4a — Cohort-Wide False-Positive Finding

**Date**: 16 July 2026 (late evening)
**Author**: ikenga-ssi-foundation
**Trigger**: R7 Phase 4a smoke test on Poland (post-Commit-6 empirical state)

---

## Executive summary

The R7 Phase 4a hotfix (Task #304) surfaced a **cohort-wide false-positive** in the pipeline's ESG readiness assessor (`scripts/pipeline/enrichment/merge.py::assess_esg_readiness()`) that had been silently reporting **ALL** ESG reports as "READY" for recently-L1-refreshed countries when they were empirically **GAP**.

**Root cause**: `sub.get(field_path, {})` returned an empty-dict `{}` fallback when a top-level field was missing from a substation. That `{}` passed the `val is not None` gate and, since `{}` was NOT in the `_is_default_value` known-defaults list, it counted as `non_default += 1` = populated.

**Empirical impact**: Every prior country closure YAML (Wave 1 P1-P5 + Wave 2 P1-P21 = 26+ files) reporting `esg_reports_ready_count: 6` was falsely positive for **recently-refreshed countries** — the actual empirical R1-R6 readiness state was likely GAP for R2, R4, R5, R6 (which require nested fields under `socio_economic`, `markov.corrosion_class`, `transition`, `graph_topology`) for net-new subs carrying Convention #56 neutral defaults.

**Fix landed**: `merge.py::assess_esg_readiness()` now uses explicit `p not in val` check and treats missing fields as NOT populated (Convention #56 visibly-honest degradation preserved). All 39 countries will now show empirically-accurate readiness state on next pipeline.run.

---

## Latent bug forensic

### Pre-fix code (buggy):

```python
for sub in substations:
    val = sub
    for p in parts:
        val = val.get(p, {}) if isinstance(val, dict) else None
        if val is None:
            break

    if val is not None and not _is_default_value(field_path, val):
        non_default += 1
```

### Why it was wrong

`sub.get(p, {})` returns `{}` when field `p` is missing. Chain:
1. First iteration: `val = sub.get("Re_norm", {})` = `{}` (Poland net-new sub has no Re_norm... but wait, it DOES have Re_norm=0.0)

Actually re-tracing for a top-level field: Poland net-new subs DO have `Re_norm=0.0` explicitly set by `merge_into_ssi_data.py::_v42_placeholder_fields()`. So the R7 path worked correctly — 0.0 in `[0.0]` defaults list → NOT populated.

The bug manifests for **nested paths** like `socio_economic.V_socio`:
1. First iter: `val = sub.get("socio_economic", {})` — returns actual `socio_economic` dict IF present, else `{}`
2. If `socio_economic` doesn't exist (net-new sub): `val = {}` (empty dict)
3. Second iter: `val = {}.get("V_socio", {})` = `{}` (empty dict again)
4. Post-loop: `val is not None` = True (`{}` is truthy dict, not None)
5. `_is_default_value("socio_economic.V_socio", {})` — `{}` is not in `[0.5]` defaults list → False
6. Result: `non_default += 1` — **false positive**

### Post-fix code (correct):

```python
for sub in substations:
    val = sub
    missing = False
    for p in parts:
        if isinstance(val, dict):
            if p not in val:
                missing = True
                break
            val = val[p]
        else:
            missing = True
            break

    if missing or val is None:
        continue

    if not _is_default_value(field_path, val):
        non_default += 1
```

Now `if p not in val` catches missing fields explicitly + `missing` flag prevents false-positive counting.

---

## Empirical impact — Poland readiness matrix (pre-fix vs post-fix)

| Report | Pre-fix status | Post-fix status | Coverage post-fix |
|---|---|---|---:|
| R1 Climate Physical | READY | READY | 89.3% |
| R2 Grid Equity & Social | READY | 🚨 **GAP** | **8.1%** |
| R3 Infrastructure Resilience | READY | READY | 100.0% |
| R4 Pollution & Corrosion | READY | 🚨 **GAP** | **8.1%** |
| R5 Energy Transition & DER Stress | READY | 🚨 **GAP** | **8.1%** |
| R6 Cybersecurity Exposure | READY | 🚨 **GAP** | **8.1%** |
| R7 SFDR PAI Infrastructure | (not registered) | 🚨 **GAP** | **7.7%** |

**Post-fix state**: 2 READY + 5 GAP (Poland)
**Pre-fix state**: 6 READY + 0 GAP (Poland) — falsely reported

The 8.1% figure ≈ 2,247/27,764 = baseline pre-refresh sub count. Every baseline sub had FULL modifier chain + component + graph_topology + transition + socio_economic populated via prior pipeline runs. The 91.9% net-new subs are in Convention #56 neutral-default state per Convention #78 §4bis.4 two-phase workflow.

---

## Italy (fully populated baseline) — post-fix matrix

| Report | Status | Coverage | Notes |
|---|---|---:|---|
| R1 Climate Physical | READY | 100.0% | |
| R2 Grid Equity & Social | READY | 100.0% | |
| R3 Infrastructure Resilience | READY | 100.0% | |
| R4 Pollution & Corrosion | READY | 100.0% | |
| R5 Energy Transition | READY | 100.0% | |
| R6 Cybersecurity | READY | 98.4% | 1.6% subs lack graph_topology (known small population) |
| R7 SFDR PAI | READY | 100.0% | 🎉 First R7 SFDR PAI READY report cohort-wide |

Italy = 7/7 READY (near-100% coverage). Reference country empirical state confirmed.

---

## Cohort-wide implication

The 15 GAP/PARTIAL countries per Phase 2 audit (Poland + Czechia + Austria + Belgium + Latvia + Lithuania + Luxembourg + Netherlands + Slovenia + Canada + Greenland + Mexico + Australia + Colombia + Estonia) all now need to be re-audited under the post-fix code path. Their empirical R2/R4/R5/R6 readiness will surface as GAP (matching R7 GAP) — the same Convention #78 §4bis.4 two-phase workflow signal.

**This changes the R7 Phase 4c rescore scope**: instead of just running a Re_norm-focused rescore, we need a **full modifier-chain + component + graph_topology + transition + socio_economic rescore** for all 15 countries. The `refresh_f_l4_2_legacy_drift.py` clip-only pass is insufficient; we need `pipeline.run <country>` with full modifier population for net-new subs.

**But wait** — `pipeline.run poland` DID run at 19:03:57 UTC today and reports say "27,411 rescored" for R_median. Yet Re_norm is still 0.0 for 25,517 net-new subs. This suggests `pipeline.run` does R_median MC rescore but does NOT populate modifiers + Re_raw + Re_norm for net-new subs — this is the "separate modifier-chain rescore" gap already documented in Phase 2 audit §4.

The v4.2 `apply-v4.2-modifiers.py` (referenced in methodology.html §100) or equivalent needs to run to populate modifiers on net-new subs. Locating that script + wiring it into the Phase 4c rescore sequence is the next investigation.

---

## Convention preservation matrix

| Convention | Impact | Status |
|---|---|---|
| **#7** Data-Layer Anchoring | R7 SFDR PAI Re_norm proxy path preserved | ✓ |
| **#56** Visibly-honest degradation | 🎉 **REINFORCED** — missing-field-treated-as-populated bug retired; Convention #56 now truly enforced at readiness assessor layer | ✓ |
| **#66** v4.2 canonical schema | R7 required_fields = ["Re_norm"] (public dashboard) vs "Re_normalised" (compliance clone) — cross-repo naming inconsistency documented | ⚠️ |
| **#78 §4bis.4** two-phase workflow | 🎉 **EMPIRICALLY VISIBLE NOW** — pre-fix false-positive was hiding this discipline; post-fix truly reflects Phase 1 vs Phase 2 state | ✓ |

---

## Cross-repo naming inconsistency (Convention #66 documented follow-on)

The public dashboard's ssi-data.json uses field name `Re_norm`; the ssi-enn-compliance clone's Convention #66 EXPECTED_KEYS references `Re_normalised`. Both are the same conceptual field per FC v3 §14.

- Public dashboard: `Re_raw` + `Re_norm` (empirical, ~4,293 Italian subs at 100%)
- Compliance clone: `Re_normalised` (per V4_2_IMPLEMENTATION_ARCHITECTURE.md §4.5 spec)

Naming reconciliation deferred to Q3 2026 methodology-hardening sprint. For now, public dashboard uses `Re_norm` throughout (config.py + _is_default_value + esg-sections.js R7 block per Phase 4b).

---

## R7 Phase 4a complete — files landed

- `scripts/pipeline/config.py` — ESG_REPORTS extended to 7 entries (R1-R7), R3 relabelled Infrastructure Resilience, R4↔R5 swapped to FC v3 §14 canonical order, R7 SFDR PAI added with required_fields=["Re_norm"]
- `scripts/pipeline/enrichment/merge.py` — assess_esg_readiness() docstring updated to "7 reports", latent bug fixed (missing top-level fields now correctly treated as NOT populated), `_is_default_value` gate extended with `Re_norm=0.0` neutral-default
- Smoke test verified on Italy (7/7 READY) + Poland (2 READY R1+R3 + 5 GAP + Convention #56 preserved)

## Next: R7 Phase 4b — frontend rendering + FC v3 §14 relabel in esg-sections.js

- Add R7 SFDR PAI block to `esg-sections.js::ESG_REPORTS` array (7th entry after R6)
- Rename R3 title (matches config.py)
- Swap R4/R5 titles + logic (matches config.py)
- Update `computeESGScores()` to compute r7 = Re_norm coverage across fleet
- Update `country-renderer.js` R7 field lookup (Safe.get pattern)
- Cache-bust preparation (39-country esg-report.html + methodology.html)

*Phase 4a hotfix + cohort-wide false-positive finding memo complete 16 July 2026 late evening.*
