# Failure-Solving Proposal — L2/L3/L4 Pipeline Batch Rerun

**Date:** 16 July 2026
**Author:** Ikenga SSI Foundation
**Status:** DRAFT — awaiting operator review before any code change
**Trigger:** L2/L3/L4 batch rerun surfaced 12 failures across 4 distinct error classes; operator directive requires audit-first proposal with no code changes until reviewed.

---

## 0. Executive summary

The L2/L3/L4 pipeline batch rerun on 19 already-Phase-1-shipped countries produced 7 successes + 12 failures across 4 error classes. **All 4 error classes are already documented at the foundational-doc + codebase level**; none represent new unknowns. Two are pre-existing operator-known open items (R7_cyber drift, Latvia flat-list schema divergence — both intentional per Convention #56 discipline). Two are validator-layer defensive-coding gaps (NoneType format + NoneType comparison) — narrowly scoped 1-line + 2-site fixes.

**No proposed fix modifies methodology.** No fix widens modifier ranges. No fix touches KB §56 MIN_FLEET floors. No fix breaks Convention #56 visibly-honest degradation. All fixes are defensive-coding guards that make the validator handle legitimate pre-L3 intermediate states (R_median=None, flat-list root) without silencing genuine methodology violations.

**Proposed sequencing:** four separate commits (one per error class), each with dedicated regression sentinel + CLAUDE.md housekeeping. Post-fix retry of the 12 failed countries expected to yield 8 successes + 4 remaining Class A R7_cyber diagnostics — the latter is a data-refresh workstream, not a code fix.

---

## 1. Failure classification recap

| Class | Error message | Countries | Site |
|---|---|---|---|
| **A** | KB §56 fleet-floor validation failed — MODIFIER-RANGE: R7_cyber outside [0.99, 1.05] | norway (59.12%), chile, slovenia, australia | `validate_schema.py` Check 9 modifier-range, lines 275-327 |
| **B** | `unsupported format string passed to NoneType.__format__` | austria, greenland, luxembourg, hungary, netherlands | `validate_schema.py::565` — `f"...R_median={r:.4f}..."` |
| **C** | `'<' not supported between instances of 'NoneType' and 'float'` | lithuania, estonia | `validate_schema.py::527` (`min/max`) + `::542` (`_expected_band_v42`) |
| **D** | `list indices must be integers, not str` / `'list' object has no attribute 'get'` | latvia | `scripts/pipeline/utils/geo.py::load_substations` line 146 + `socioeconomic.py::469` |

## 2. Foundational-document context

Constraints surfaced by the Explore-agent review of foundational docs + sentinels + codebase (full report in session archive):

**Documents establishing legitimacy of pre-L3 intermediate state:**
- `CONVENTION_78_BINDING_EMPIRICAL_AUDIT_20260716.md` §4bis.4 — Latvia flat-list schema is "Phase 1 intermediate-state characteristic, NOT a data-quality bug"
- `SSI_NORWAY_FINLAND_CLIMATE_TRAJECTORY_FIX.md` — establishes `climate_trajectory: {}` as legitimate pre-rescore state
- `SSI_R7_CYBER_DRIFT_DIAGNOSTIC.md` (Task #181) — R7_cyber code fix landed; data drift remains visible until next L3 rescore. Explicitly rejects widening the spec (Option B) in favor of source retighten (Option A) with data-side patience.

**Documents establishing Convention #56 visibly-honest degradation:**
- `CLAUDE.md` §"Binding disciplines" — Convention #56 (`[N/A]` markers, no silent defaults)
- `MODE_2_3_FOLLOWON_PLAN.md` — degradation pattern precedent

**Documents establishing modifier registry as SoT:**
- `CLAUDE.md` §"MODIFIER_REGISTRY is single source of truth for modifier ranges"
- `tests/test_modifier_registry.py::test_5_registry_default_within_range` — pin
- `tests/test_validate_schema.py::test_5_modifier_below_range_is_caught` — pin

**Documents establishing KB §56 fleet-floor as anti-stub-data only:**
- `CLAUDE.md` §"KB §56 fleet-floor as anti-stub-data gate, NOT aspirational"
- MIN_FLEET values reflect post-D#36 reality, NOT aspirational (Austria 700, Canada 6000, etc.)

**Documented foundational contradictions surfaced during review** (out-of-scope for immediate fix, flagged for follow-up):
1. `R6_seismic` range disagreement: MODIFIER_REGISTRY (1.00, 1.25) vs config.py + validate_schema.py (0.95, 1.25) — Task #180 widen was incomplete
2. `CLASSIFICATION_BANDS` in config.py:74-79 is stale 4-band; engine.py::80 authoritative 5-band
3. `COMPONENT_WEIGHTS` duplicated between engine.py:42 + config.py:60
4. `MODIFIER_RANGES` duplicated across registry + config + validator

## 3. Per-class fix proposal

### Class A — R7_cyber drift (norway/chile/slovenia/australia)

**Root cause:** Not a code bug. 18 countries (cohort per `SSI_COHORT_AUDIT_SWEEP_20260713.md`) have existing R7_cyber values below 0.99 floor (norway worst at 92.5% below, tolerance-adjusted; Class A batch surfaced 59.12% Norway — matching diagnostic). Source generators were retightened at Task #181 (`scripts/score-country.py::128` + `scripts/enrich_esg_gaps.py::325`) but existing per-substation R7_cyber values persist until next L3 rescore.

**Foundational constraint:** Explicit prohibition on widening R7_cyber spec (`SSI_R7_CYBER_DRIFT_DIAGNOSTIC.md` §Recommendation lines 198-210, Option A codified vs Option B rejected). Convention #56 visibly-honest degradation — drift must remain visible.

**Proposed fix:** **NONE (code).** This is a data-refresh workstream. Fix path is data-side:
1. Run `python -m scripts.pipeline.run <country>` on each of norway + chile + slovenia + australia after the L3 modifier stack has been regenerated from Phase 1 fresh substation coordinates
2. The rescore should apply the retightened source generators (`score-country.py::128` current logic) to produce R7_cyber values inside [0.99, 1.05]
3. Post-rescore Class A failures should convert to successes

**Deferred to:** Post-Wave-2-completion cohort-wide L3 rescore cycle (aligns with operator's stated 2-phase workflow — L1 ingestion complete → L2/L3/L4 rescore).

**No sentinel changes required.** Existing modifier-range check is correctly firing.

### Class B — NoneType.__format__ (austria/greenland/luxembourg/hungary/netherlands)

**Root cause:** `validate_schema.py::565` calls `f"substation {n}: R_median={r:.4f} ..."` where `r` can be `None` for substations in legitimate pre-L3 state. `_v42_placeholder_fields()` at `scripts/pipeline/ingestion/latvia/merge_into_ssi_data.py::94` writes `"R_median": None` as Convention #56 placeholder — this is the pattern for v4.23 net-new substations from OSM merges that haven't been through L3 rescore. Wave 2 v4.23 additions in these 5 countries carry the same pattern.

**Foundational constraint:** Convention #56 — R_median=None is legitimate pre-L3 state. Fix must guard format-string WITHOUT silencing genuine classification-band mismatches when R_median IS numeric.

**Proposed fix:**

File: `scripts/validate_schema.py::565`
```python
# BEFORE (current):
warnings.append(
    f"CLASSIFICATION-BAND: substation {n} has R_median={r:.4f} but "
    f"classification='{sub_class}' (expected '{expected}')"
)

# AFTER (proposed):
r_str = f"{r:.4f}" if isinstance(r, (int, float)) else "None"
warnings.append(
    f"CLASSIFICATION-BAND: substation {n} has R_median={r_str} but "
    f"classification='{sub_class}' (expected '{expected}')"
)
```

Additionally, upstream at `validate_schema.py::542`, guard `_expected_band_v42(r)` to return `None` (or `"Unclassified"`) when `r is None`:
```python
# BEFORE (probable current):
def _expected_band_v42(r):
    if r < 0.25: return "Low"
    if r < 0.50: return "Medium"
    ...

# AFTER (proposed):
def _expected_band_v42(r):
    if r is None: return None  # Convention #56 — pre-L3 state
    if r < 0.25: return "Low"
    ...
```

And at Check 8 caller (~line 542), skip substations where `expected is None` from the mismatch tally, but count them in a new `warnings.append(f"{n} substations skipped Check 8 — R_median is None (pre-L3 state)")` summary.

**Sentinel additions:**
- New test `tests/test_validate_schema.py::test_13_handles_none_r_median_gracefully` — pins that a substation with `R_median=None` does NOT crash Check 8 and produces a "pre-L3 state" warning

**Regression risk:** LOW. Fix is purely defensive; happy-path (numeric R_median) behavior unchanged.

### Class C — NoneType comparison (lithuania/estonia)

**Root cause:** Two-site None-comparison at `validate_schema.py`:
1. `Check 7 min/max` line 527: `r_min, r_max = min(r_values), max(r_values)` — `min([1.0, None, 0.5])` raises TypeError
2. `Check 8 classification` line 542-565: `_expected_band_v42(r)` does `if r < 0.25` — same TypeError

Both fire when Lithuania + Estonia's pre-L3 v4.23 net-new substations carry `R_median=None`. Additionally, preceded by benign "Unknown modifier" warnings for R3_tier/R3/R6b/R7/compound — these are legacy-vintage per-substation modifier names from pre-refactor emissions; `MODIFIER_REGISTRY::compute_modifier_terms::153` correctly warns-and-skips them.

**Foundational constraint:** Convention #56 legitimate None state. Unknown-modifier warn-not-crash pattern must be preserved (`tests/test_modifier_registry.py::test_10`). Do NOT silently rename legacy modifier keys to canonical names (audit-trail preservation).

**Proposed fix:**

File: `scripts/validate_schema.py::527` (Check 7):
```python
# BEFORE:
r_values = [s.get('R_median', 0) for s in substations]
r_min, r_max = min(r_values), max(r_values)

# AFTER:
r_values = [s.get('R_median') for s in substations if s.get('R_median') is not None]
if not r_values:
    warnings.append(
        f"CHECK 7: 0 substations have numeric R_median (all pre-L3 state) — Check 7 skipped"
    )
else:
    r_min, r_max = min(r_values), max(r_values)
    # ... existing range check
```

And guard `_expected_band_v42` per Class B fix above (single fix serves both classes).

**Sentinel additions:**
- New test `tests/test_validate_schema.py::test_14_handles_all_none_r_median_gracefully` — pins that a country with ALL substations at `R_median=None` does NOT crash Check 7 and produces the summary warning
- Extend existing `test_5_modifier_below_range_is_caught` verifies unchanged real-range violation detection

**Regression risk:** LOW. Defensive guard; range check still fires for numeric R_median.

### Class D — Latvia flat-list root schema (latvia)

**Root cause:** `scripts/pipeline/utils/geo.py::load_substations` line 148 calls `data.get("substations", [])` on `data = json.load(f)`. Latvia's `ssi-data.json` root is a bare list (per intentional Phase 1 flat-list write pattern documented Task #263). `list.get()` doesn't exist → AttributeError.

Downstream `socioeconomic.py::469` calls `load_substations(country)` which crashes → pipeline aborts before Phase 2 for Latvia. Same class D also surfaces in `Check 10 regional consistency` (validate_schema.py::334-404) but geo.py hits first.

**Foundational constraint:** Task #263 CLOSED with explicit designation "flat-list schema is Phase 1 intermediate state, NOT a bug" (CONVENTION_78 audit §4bis.4). Phase 2 pipeline MUST accommodate — cannot reject flat-list input. Convention #64 (strict per-country resolution) — fix must not introduce cross-country side effects.

**Proposed fix:**

File: `scripts/pipeline/utils/geo.py::load_substations` line 146:
```python
# BEFORE (probable):
with open(path) as f:
    data = json.load(f)
substations = data.get("substations", [])
# ... process

# AFTER (proposed):
with open(path) as f:
    data = json.load(f)
if isinstance(data, list):
    # Latvia + any future country in Phase 1 intermediate state
    # per CONVENTION_78 audit §4bis.4 (flat-list = pre-Phase-2 wrapper)
    logger.info("Country %s uses flat-list root schema (Phase 1 intermediate state)", country)
    substations = data
else:
    substations = data.get("substations", [])
```

Same guard needed at:
- `validate_schema.py::validate_file` line 455 (before top-level key checks)
- `validate_schema.py::334-404` Check 10 (regional consistency reads data structure)

Fix ensures the L2/L3 pipeline processes Latvia; the output write via `enrichment/merge.py` should produce a proper wrapper-schema `ssi-data.json` (Convention #78 audit §4bis.6 documents Phase 2 rewrites the file with proper wrapper — this closes the schema divergence).

**Sentinel additions:**
- New test `tests/test_validate_schema.py::test_15_handles_flat_list_root_schema` — pins that a country with flat-list root loads correctly and Check 10 doesn't crash
- New test `tests/test_e2e_refresh.py::test_latvia_flat_list_pipeline_recovery` — end-to-end: flat-list Latvia goes through L2/L3 pipeline, output is wrapper-schema

**Regression risk:** LOW-MEDIUM. The flat-list branch is a NEW code path never before exercised in the utils/geo.py layer. Need careful testing that lithuania/estonia (which use dict-with-key OR dict-keyed-by-id) don't accidentally hit the flat-list branch. Isinstance check protects.

## 4. Cross-cutting constraints preserved

All 20 rules from the Explore-agent's "Fix-proposal constraints checklist" (session archive) are honored by the above proposal. Specifically:

1. ✅ Convention #56 preserved (rules 1, 8, 9 — no silent defaults, warnings surface pre-L3 states)
2. ✅ KB §56 fleet-floor as anti-stub-data (rule 2 — no MIN_FLEET changes)
3. ✅ KB §57 SoT respected (rule 3 — no hardcoded country lists)
4. ✅ MODIFIER_REGISTRY as SoT (rule 4 — no range changes)
5. ✅ R7_cyber not widened (rule 6 — Class A is data workstream, not code fix)
6. ✅ Unknown-modifier warn-not-crash contract (rule 7 — no silent renames)
7. ✅ 5-band system preserved (rule 12 — no BANDS changes)
8. ✅ Reclassify-vs-rescore discipline (rule 13 — all fixes are validator-layer defensive coding, use reclassify path)
9. ✅ Cross-border sentinel behavior untouched (rule 14)
10. ✅ Compact-JSON discipline preserved (rule 16)
11. ✅ Substation-line coupling invariant preserved (rule 17)
12. ✅ Fix-per-file discipline — 4 separate commits (rule 18)
13. ✅ Sentinel additions cover all fixes (rule 19)
14. ✅ CLAUDE.md housekeeping cascade required (rule 20)

## 5. Contradictions flagged but NOT fixed in this proposal

The Explore-agent review surfaced 4 foundational-doc contradictions that pre-date this session and are OUT OF SCOPE for the immediate fix:

1. **R6_seismic range disagreement** (Task #180 widen incomplete): MODIFIER_REGISTRY at (1.00, 1.25) vs config.py + validate_schema.py at (0.95, 1.25). Recommend a separate "Task #180 completion" workstream that either (a) brings registry to (0.95, 1.25) or (b) reverts the widen in config + validator. Not touched by current proposal.
2. **CLASSIFICATION_BANDS 4-band vs 5-band mismatch** (config.py:74-79 stale). Recommend either remove or extend to 5-band. Not touched.
3. **COMPONENT_WEIGHTS duplicated** (engine.py:42 + config.py:60). Not touched.
4. **MODIFIER_RANGES duplicated** (registry + config + validator). Not touched.

## 6. Proposed execution sequencing

**Step 1 (operator review):** Operator reviews this proposal document. Approves/requests changes.

**Step 2 (Class D fix — Latvia flat-list guard, ~10 min):**
- Patch `scripts/pipeline/utils/geo.py::load_substations` per §3 Class D
- Extend `validate_schema.py::validate_file` + Check 10 with isinstance guard
- Add sentinels `test_15_handles_flat_list_root_schema` + `test_latvia_flat_list_pipeline_recovery`
- Retry: `python -m scripts.pipeline.run latvia`
- Verify: Latvia post-fix goes through L2/L3, output is proper wrapper schema
- Commit + push

**Step 3 (Classes B + C fixes — validator NoneType guards, ~15 min):**
- Patch `validate_schema.py::527` (Check 7 min/max) per §3 Class C
- Patch `validate_schema.py::542` (`_expected_band_v42`) per §3 Class B/C
- Patch `validate_schema.py::565` (format-string) per §3 Class B
- Add sentinels `test_13_handles_none_r_median_gracefully` + `test_14_handles_all_none_r_median_gracefully`
- Retry: `python -m scripts.pipeline.run austria greenland luxembourg hungary netherlands lithuania estonia`
- Verify: all 7 countries now pass Phase 2b (Class A drift may still surface for some — that's Class A workstream)
- Commit + push

**Step 4 (Class A workstream — no code fix, data refresh):**
- Documented as follow-up in CLAUDE.md
- Deferred to post-Wave-2-completion L3 rescore cycle
- No commit this session

**Step 5 (CLAUDE.md housekeeping cascade):**
- Update CLAUDE.md §Recent tasks with tasks #267 + #268 closure
- Update CLAUDE.md §Binding disciplines with note on flat-list guard + None-guard patterns
- Verify no methodology-version bump needed (all fixes are defensive coding, not methodology)

**Step 6 (retry batch on 8 fixable countries):**
- After Steps 2+3 land, rerun L2/L3/L4 on the 8 previously-failing countries (excl. Class A cohort)
- Expected: 8 successes
- Update task #264 status accordingly

## 7. What this proposal does NOT do

- Does not modify any methodology (BANDS, MODIFIER_REGISTRY ranges, COMPONENT_WEIGHTS)
- Does not touch MIN_FLEET floors
- Does not touch KB §56 fleet-floor gate logic
- Does not touch Discipline #36 cross-border filter
- Does not touch Discipline #41 substation-line parity
- Does not touch Convention #78 BINDING sub-conventions
- Does not modify L2 ingestion engines (seismic/climate/socio-economic)
- Does not modify L3 scoring engine or Monte Carlo
- Does not modify L4 5-band classification or reclassify_phase2c.py
- Does not resolve the 4 foundational-doc contradictions (flagged for separate workstream)
- Does not run any pipeline on any country (session is proposal-only until approved)

## 8. Operator decision requested

1. **Approve proposal** for Class B/C/D fixes as scoped (Steps 2 + 3)?
2. **Defer Class A** to post-Wave-2 L3 rescore cycle (Step 4)?
3. **Defer foundational-doc contradictions** to separate workstream (§5)?
4. **Approve sequencing** Steps 2 → 3 → 5 → 6?
5. **Approve sentinel additions** as scoped in §3?

If all approved: I proceed with Step 2 (Class D Latvia flat-list guard) as the first commit. Otherwise: adjust proposal per operator direction.
