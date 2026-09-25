# L2/L3/L4 Batch Rerun — Wave 1 + Wave 2 Cohort Post-Ingestion Rescore

**Date:** 16 July 2026
**Trigger:** Operator directive during Czechia Overpass cooldown window: *"re run L2, L3, L4 for all countries where we have ingested additional substations and power lines"*
**Status:** ⚠ Partial completion — 15/19 GREEN, 4/19 deferred to post-Wave-2 data-refresh cycle
**Two-phase workflow discipline:** L2/L3/L4 rescore is the DEFERRED phase per operator correction 16 July 2026 (*"we would first bring all additional substations and power lines, and only after we would run the layers scoring etc"*). This document records Phase 2 execution against the current Wave 1 + Wave 2 ingested cohort; further L1 ingestion (Czechia + Poland + downstream Wave 2 priorities) will trigger the next cohort-wide rescore cycle.

---

## Scope

**Countries included** — 19 with L1 ingestion completed post-v4.23 gap-audit or Wave 2 workstream:

**Wave 1 (v4.23 gap-audit closure, Q3 2026):** canada, norway, mexico, austria, greenland

**Wave 2 (Q4 2026 → 2027):** australia, belgium, netherlands, chile, hungary, luxembourg, slovenia, costa-rica, israel, colombia, lithuania, estonia, latvia, slovakia

**Excluded:** czechia (L1 ingestion in-progress — synthetic-cache dry-run only; Overpass real fetch pending Task #255 cooldown).

---

## Outcome matrix

| # | Country | Status | Substations | Notes |
|---|---|---|---|---|
| 1 | slovakia | ✅ GREEN | 60 rescored | Priority 19 baseline |
| 2 | canada | ✅ GREEN | — | Wave 1 |
| 3 | mexico | ✅ GREEN | — | Wave 1 |
| 4 | costa-rica | ✅ GREEN | — | Wave 2 |
| 5 | israel | ✅ GREEN | — | Wave 2 |
| 6 | colombia | ✅ GREEN | — | Wave 2 |
| 7 | belgium | ✅ GREEN | — | Wave 2 |
| 8 | greenland | ✅ GREEN | 43 rescored | Wave 1 (post-Class-B fix) |
| 9 | austria | ✅ GREEN | 14,720 rescored | Wave 1 (largest cohort; post-Class-B fix) |
| 10 | luxembourg | ✅ GREEN | — | Wave 2 (post-Class-B fix) |
| 11 | netherlands | ✅ GREEN | — | Wave 2 (post-Class-B fix) |
| 12 | latvia | ✅ GREEN | — | Wave 2 (post-Class-D flat-list fix) |
| 13 | lithuania | ✅ GREEN | — | Wave 2 (post-Class-C sort fix) |
| 14 | estonia | ✅ GREEN | — | Wave 2 (post-Class-C sort fix) |
| 15 | hungary | ✅ GREEN | — | Wave 2 (post-Class-C sort fix) |
| **16** | **chile** | ⚠ **DEFERRED** | 965 scored / 1,035 total | **Class A — R7_cyber drift 57.7% below 0.99 floor (min 0.9310)** |
| **17** | **slovenia** | ⚠ **DEFERRED** | 157 scored / 1,731 total | **Class A — R7_cyber drift 59.2% below 0.99 floor (min 0.9314)** |
| **18** | **norway** | ⚠ **DEFERRED** | 5,842 scored / 6,113 total | **Class A — R7_cyber drift 92.5% below 0.99 floor (min 0.9193)** |
| **19** | **australia** | ⚠ **DEFERRED** | 8,078 scored / 12,565 total | **Class A — R7_cyber drift 24.1% below 0.99 floor (min 0.9000)** |

**Success rate: 15/19 = 78.9% GREEN**. Remaining 4 fail on one class only (Class A KB §56 fleet-floor for R7_cyber modifier), which is documented as a **deferred data-refresh workstream** — not a code defect.

---

## Failure classification (as diagnosed in FAILURE_SOLVING_PROPOSAL_20260716.md §3)

### Class A — KB §56 fleet-floor validation on R7_cyber (DEFERRED, NO CODE FIX)

**Manifestation:** `validate_schema.py` KB §56 gate fires because R7_cyber modifier values in scored substations fall below the 0.99 floor threshold codified in `_MODIFIER_RANGES` (registry sync via Phase 2A-3, CLAUDE.md §Recent tasks Phase 2A/B/C closure block).

**Root cause (per operator constraint, Task #159 + `SSI_R7_CYBER_DRIFT_DIAGNOSTIC.md`):**
- R7_cyber calibration in L2 signal layer combines NCSI (National Cyber Security Index) 2024 base × per-substation grid-topology exposure modifier × critical-infrastructure-tier surcharge
- 4-country data-refresh workstream identified: NCSI 2024 → 2025 revision + per-substation topology recalibration + tier surcharge audit
- Operator explicit constraint: **DO NOT widen the 0.99 floor** in `_MODIFIER_RANGES` to accommodate these values — that would mask genuine cyber-risk signal drift and defeat the fleet-floor gate's purpose
- Fix path: post-Wave-2-completion L3 rescore cycle with refreshed NCSI 2025 base + retuned per-substation modifier chain

**Empirical scale (as of 16 July 2026 pre-refresh):**

| Country | Scored subs | Below 0.99 | Min R7 value |
|---|---|---|---|
| chile | 965 | 557 (57.7%) | 0.9310 |
| slovenia | 157 | 93 (59.2%) | 0.9314 |
| norway | 5,842 | 5,406 (92.5%) | 0.9193 |
| australia | 8,078 | 1,947 (24.1%) | 0.9000 |

**Norway** carries the deepest drift signature (min 0.9193, 92.5% below floor) — consistent with its high cross-border interconnection density + high per-substation criticality tier surcharge, both of which R7_cyber's current calibration multiplies down aggressively.

**Deferred workstream owner:** Post-Wave-2 L3 rescore cycle (Q1-Q2 2027 estimated, gated on Poland Priority 21 + Portugal + Ireland completion for full Wave 2 cohort).

**No code change this cycle.** These 4 countries remain at their current committed L2/L3/L4 state until the data refresh lands.

### Class B — R_median=None NoneType format crash (FIXED)

**Manifestation:** `validate_schema.py::_expected_band_v42(r)` line 565: `TypeError: unsupported format string passed to NoneType.__format__` when a substation's R_median is None (visibly-honest degradation marker per Convention #56).

**Root cause:** Format string `f"{r:.4f}"` unguarded against None values. R_median=None is a legitimate Convention #56 state (substation exists on grid but scoring inputs incomplete — see Phase 2C reclassify discipline in CLAUDE.md).

**Fix landed (Step 3, commit pending):** `scripts/validate_schema.py`
- Check 7 (line 538 area): filter None from R_median min/max computation
- Check 8 `_expected_band_v42(r)`: returns 'Unclassified' if r is None
- Format string guard: `r_str = f"{r:.4f}" if isinstance(r, (int, float)) else "None"`
- Skip None subs from classification-band mismatch tally

**Affected countries fixed:** austria (14,720 subs), greenland (43 subs), luxembourg, netherlands.

### Class C — R_median=None NoneType sort/comparison crash (FIXED)

**Manifestation:** `TypeError: '<' not supported between instances of 'NoneType' and 'float'` at multiple L2/L3/L4 sites when sorting substations by R_median or classifying bands.

**Root cause:** Sort/comparison operations unguarded against None R_median values.

**Fix landed (Step 3, commit pending):**
- `scripts/pipeline/scoring/engine.py::classify_band(R)` line 127: returns "Unclassified" if R is None
- `scripts/pipeline/scoring/engine.py::compute_fleet_summary(substations)` line 613: filter None from stats; add "Unclassified" band; add `n_scored` + `n_unclassified_pre_l3` audit fields; `_stats_pending_l3_rescore` flag when no scored subs
- `scripts/pipeline/scoring/engine.py::compute_regional_summary(substations)` line 641: same filter pattern
- `scripts/pipeline/enrichment/merge.py` line 179: filter None from fleet_percentile sort + assign `sub["fleet_percentile"] = None` for None-R_median subs

**Affected countries fixed:** lithuania, estonia, hungary.

### Class D — Latvia flat-list root schema (FIXED)

**Manifestation:** `TypeError: list indices must be integers, not str` at multiple call sites where downstream code assumes `data["substations"]` dict-root schema.

**Root cause:** Latvia's `ssi-data.json` was ingested as flat-list root schema during Wave 2 P17 Latvia (Task #248 Convention #78 BINDING promotion event). This is a **Phase 1 intermediate state per Convention #78 §4bis.4** — the schema is deliberately not rewrapped during L1 ingestion because rewrapping would mask the flat-list-vs-wrapped topology signal that the Convention #78 sub-convention exists to codify.

**Operator correction (Refresh #16 July 2026):** "we would first bring all additional substations and power lines, and only after we would run the layers scoring etc" — Latvia flat-list is NOT a bug to be rewrapped; it is the Phase 1 intermediate state that downstream L2/L3/L4 code MUST accommodate defensively.

**Fix landed (Step 2, commit pending):** flat-list root guards at three sites:
- `scripts/pipeline/utils/geo.py::load_substations()` after `json.load(f)`: `if isinstance(data, list): data = {"substations": data}` with INFO log citing Convention #78 §4bis.4
- `scripts/validate_schema.py::validate_file()` line 455 area: same guard
- `scripts/pipeline/enrichment/merge.py` line 57 area: same guard + `if "meta" not in data: data["meta"] = {}` bootstrap for Latvia (which has no meta block yet in Phase 1)

**Affected countries fixed:** latvia.

---

## L5 SSI Foundation methodology cascade

Per operator directive during batch investigation (*"you will also note that we render some and some others (W1 to 10) are commercial, have a diligent audit"*), the L5 SSI Foundation layer was located and audited:

**Codebase location:** `~/Library/CloudStorage/OneDrive-SUN.ENCAPITALOU/Shared DR/Internal/0. General/0.22. IP agenda/SSI Index/` (three Python modules for offline SVG patching + Re composite computation + W1-W10 axis assembly).

**5/1/1/3 mesh audit (empirically confirmed cohort-wide):**
- **5 Published axes** — W1, W2, W3, W4, W8 (public methodology, always rendered)
- **1 Published-baseline axis** — W9 (chevron-flagged in HTML deliverables per `templates/README.md`)
- **1 Baseline-only axis** — W5 (Foundation methodology spec pending)
- **3 Commercial-tier axes** — W6, W7, W10 (populated by Phase 1 P4 L4 evaluators per Convention #60; NOT rendered on public site)

**Empirical codification:** `italy/intelligence.html:660-663` carries the 5/1/1/3 mesh classification block per HTML deliverable — sentinel for cohort-wide consistency.

**No L5 code change this cycle.** L5 SSI Foundation modules operate on committed L4 canonicals; the 4 deferred Class A countries remain at their pre-refresh L4 state, and L5 outputs reflect that state honestly per Convention #56.

---

## Retrospective bbox concentration audit

Following Prague bbox refinement (Czechia synthetic-cache dry-run 16 July 2026) surfacing 61% substation attribution to PRE distribuce instead of expected ~4%, a retrospective audit of shipped Wave 2 country ingestions was executed to detect similar geographic concentration bias.

**Empirical finding:** 7 countries initially flagged (Austria 95%, Belgium 82%, Chile 79%, Costa Rica 77%, Latvia 76%, Slovenia 71%, Slovakia 68%) as "dominant regional concentration". Categorization revealed 6/7 are Convention #56 **null-tag prevalence** — the dominant "region" is the null-region catch-all (i.e., substations lack `admin:region` tag in OSM source, correctly resolved to null per Convention #56 visibly-honest degradation).

**True geographic-concentration bias:** czechia only (61% Prague admin bbox + 96% unknown-voltage). This validated the Prague-bbox-refinement operator directive (Task #262) — no other Wave 2 country requires retrospective Layer 3 geofence refinement.

Full audit report: `CONVENTION_78_BINDING_EMPIRICAL_AUDIT_20260716.md` §4bis.

---

## Sentinel additions (queued for Step 5)

Per proposal §4 20-rule constraint checklist, three new sentinel tests are queued for `tests/`:

1. `test_validate_schema_handles_none_r_median` — feed synthetic country with R_median=None across 10% of subs; assert validate_schema.py exits 0 with 'Unclassified' band populated + no format-string crash
2. `test_validate_schema_handles_flat_list_root` — feed synthetic ssi-data.json with flat-list root; assert validate_schema.py wraps and validates successfully with INFO log citing Convention #78 §4bis.4
3. `test_handles_all_none_r_median` — edge case: country with 100% None R_median (extreme Convention #56 degradation); assert engine.py emits `_stats_pending_l3_rescore` flag and no crash

Sentinel implementation deferred to next commit cycle (not blocking this batch closure).

---

## Post-cycle state

**Committed:** 15 country canonicals in current git state (pre-fix commit `15fd371a` Slovakia P19, per Step 5 CLAUDE.md cascade). Fixes for Classes B/C/D land as follow-up commit citing this doc + FAILURE_SOLVING_PROPOSAL_20260716.md.

**Not committed:** No canonical changes for chile/slovenia/norway/australia this cycle — their pre-existing committed L4 state is preserved. Class A workstream (NCSI 2025 refresh + R7_cyber recalibration) is a separate future workstream, not this cycle's scope.

**Ship-readiness:** 39-country cohort passes L2/L3/L4 validate gates for 15/19 recently-ingested countries + all 20 unchanged countries; 4 deferred countries flag as documented open items in landing page + regional page per Convention #56 visibly-honest disclosure (chevron badge + "Post-Wave-2 rescore pending" footnote).

**Next steps (out of scope):**
- Complete Czechia Wave 2 P20 L1 ingestion (Task #255 pending Overpass cooldown → Task #257 delta audit → Task #258 doc cascade)
- Trigger next cohort-wide rescore cycle after Czechia + Poland + Portugal + Ireland L1 ingestion completes
- Execute R7_cyber data-refresh workstream (NCSI 2025 base + per-substation topology recalibration + tier surcharge audit) for chile/slovenia/norway/australia
- Add three sentinel tests to `tests/` per §Sentinel additions above
