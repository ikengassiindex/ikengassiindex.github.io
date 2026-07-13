# R7_cyber modifier drift — cohort-wide diagnostic

**Task**: #159 FOLLOW-ON (task #117 parent, Cause D2 class)
**Date**: 13 July 2026
**Author**: ikenga-ssi-foundation
**Methodology pin**: v4.2

---

## Executive summary

Cohort-wide investigation of R7_cyber modifier values finds a **3-way spec /
implementation drift** across the modifier-registry, the primary L3 emission
path (`scripts/score-country.py`), and the ESG-gap post-hoc fill path
(`scripts/enrich_esg_gaps.py`). Norway shows the WORST drift (92.5% of
substations emit R7_cyber values below the registry floor). Six other
countries show smaller-but-material drift in the same direction.

**Root cause**: `score-country.py` line 133 emits `R7 = det_var(seed+'R7',
0.98, 0.05)` bounded `[0.90, 1.10]` — centered at 0.98 with ±0.05 spread —
while the modifier registry pins the R7_cyber band at `(0.99, 1.05)`. Norway's
distribution (mean 0.966) sits ~0.024 below the registry floor and reflects
the score-country.py source distribution rather than the registry spec.

**Recommendation**: Option A + Option C combined — retighten the source
generators to match the registry pin AND document the current state as a
known-drift class awaiting the next scheduled L3 rescore window. This
diagnostic memo IS the auditability anchor for the drift class per Convention
#56 (visibly-honest degradation).

---

## Empirical distribution (cohort-wide sample)

| Country | n | min | max | mean | below 0.99 | within (0.99, 1.05) |
|---|---:|---:|---:|---:|---:|---:|
| **Norway** | 5,842 | 0.9193 | 1.0277 | **0.9662** | **92.5%** | **7.5%** |
| Ireland | 994 | 0.9310 | 1.0290 | 0.9797 | 58.9% | 41.1% |
| Slovenia | 157 | 0.9314 | 1.0285 | 0.9794 | 59.2% | 40.8% |
| Italy | 4,293 | 0.9857 | 1.0109 | 1.0009 | 17.8% | 82.2% |
| US | 44,634 | 0.9751 | 1.0149 | 0.9950 | 37.3% | 62.7% |
| Portugal | 10,066 | 0.9733 | 1.0267 | 0.9999 | 30.8% | 69.2% |
| Australia | 8,078 | 0.9000 | 1.1090 | 1.0102 | 24.1% | 66.4% |

**Cohort-wide count of R7_cyber values below registry floor**: 28,544 substations.
**Cohort-wide count within registry band**: ~46,000 substations.

## Root-cause reconstruction

### Layer 1 — Registry pin (spec)

`scripts/pipeline/config.py` line 67 + `scripts/validate_schema.py` line 222:

```python
_MODIFIER_RANGES = {
    ...
    "R7_cyber":       (0.99, 1.05),
    ...
}
```

Registry range `(0.99, 1.05)` reflects the methodology intent: R7_cyber is a
resilience modifier bounded near-neutral, with a slight upward bias reflecting
Norway's + Ireland's + Slovenia's higher-than-median cyber-security posture.
Values below 0.99 would indicate a compromised cyber-security state — should be
RARE in the cohort, per spec.

### Layer 2 — Primary L3 emission generator

`scripts/score-country.py` line 133:

```python
R7 = max(0.90, min(1.10, det_var(seed+'R7', 0.98, 0.05)))
```

- Center: **0.98** (below registry floor 0.99)
- Spread: **±0.05** (registry allows only ±0.03 above 1.00)
- Bounds: **[0.90, 1.10]** (registry allows [0.99, 1.05])
- Expected distribution: mean 0.98 (below floor), ~40-50% of values below 0.99

### Layer 3 — ESG-gap post-hoc fill generator

`scripts/enrich_esg_gaps.py` line 325:

```python
if not sub['modifiers'].get('R7_cyber'):
    sub['modifiers']['R7_cyber'] = round(vary(0.995, name, 0.02), 4)
```

- Center: **0.995** (below registry floor 0.99 — but within 0.02 → sometimes above/below)
- Spread: **±0.02** (produces [0.975, 1.015] band)
- Only fills MISSING values — does not correct existing drift from L3

### Layer 4 — Empirical distribution per country

Norway shows 92.5% of substations below 0.99 → distribution consistent with
score-country.py (center 0.98). Italy shows 82.2% within (0.99, 1.05) →
distribution consistent with enrich_esg_gaps.py (center 0.995).

Cohort-wide, R7_cyber values were emitted by score-country.py for countries
that received a fresh L3 pass with the current generator version, and by
enrich_esg_gaps.py for countries scored with an older L3 version that didn't
emit R7_cyber directly. This is a **spec-implementation drift accumulated
across L3 vintages**.

---

## Consequences

**Validator impact**: `scripts/validate_schema.py` doesn't fail on R7_cyber
below floor by design — modifier drift is reported as a diagnostic finding,
not a gate. So the drift is not blocking CI or deploy.

**R_median math impact**: R7_cyber is a multiplicative modifier
(`mod_product = R3 * R4 * R6a * R6b * R7`). Norway's mean 0.966 vs registry
mean ~1.02 produces a ~5.4% downward bias on Norway's aggregate R_median
values. This is material for cross-country comparisons.

**Classification band impact**: Because R_median is multiplied by R7_cyber
which drifts LOW, Norway substations get lower R_median values than they
would under the registry-compliant distribution. This SHIFTS Norway's
5-band classification slightly toward the Low + Medium bands.

**Auditability impact**: The drift is visible in the raw values but the
current pipeline doesn't flag it as a mismatch between emitted values and
registry spec. Per Convention #56, this diagnostic memo IS the visibly-honest
degradation acknowledgment.

---

## Remediation options

### Option A — Retighten source generators to match registry (recommended)

Two source-file edits:

1. **`scripts/score-country.py` line 133**:
   ```python
   # BEFORE
   R7 = max(0.90, min(1.10, det_var(seed+'R7', 0.98, 0.05)))
   # AFTER
   R7 = max(0.99, min(1.05, det_var(seed+'R7', 1.02, 0.015)))
   ```
   - Center: 1.02 (mid-registry)
   - Spread: ±1.5%
   - Bounds: [0.99, 1.05] → 100% within registry range

2. **`scripts/enrich_esg_gaps.py` line 325**:
   ```python
   # BEFORE
   sub['modifiers']['R7_cyber'] = round(vary(0.995, name, 0.02), 4)
   # AFTER
   sub['modifiers']['R7_cyber'] = round(vary(1.02, name, 0.015), 4)
   ```

**Requires**: Full L3 rescore for the 7 affected countries at the next
scheduled rescore window (Norway + Ireland + Slovenia + Italy + US +
Portugal + Australia). Cross-cohort rescore aligns with the Wave 2 refresh
cadence.

**Impact**: R_median values for these 7 countries increase by ~2-5% on average,
which shifts some substations up one classification band. This is the
"correct" state per spec but affects downstream deliverables (maps, dashboards,
regional comparisons). Needs to land alongside a documentation refresh on the
country pages so LP-DD readers see a clean vintage break rather than
unexplained per-country drift.

### Option B — Widen registry range to match empirical reality

Two config edits:

1. `scripts/pipeline/config.py` line 67:
   ```python
   # BEFORE
   "R7_cyber":       (0.99, 1.05),
   # AFTER
   "R7_cyber":       (0.90, 1.10),
   ```
2. Same for `scripts/validate_schema.py` line 222.

**Requires**: No data changes. Validator accepts the current cohort as-is.

**Impact**: Widens the spec-defined "acceptable" band for R7_cyber to match
score-country.py's empirical output. Sacrifices spec-defined tightness in
favor of empirical alignment. Does not require an L3 rescore. Loses the
per-country resilience signal that a tight range would surface.

### Option C — Document + defer

**Requires**: This memo shipped as the auditability anchor. No code changes.

**Impact**: Preserves current state; documents the drift class for the next
maintainer / operator / LP-DD reviewer. Bounds the technical debt with a
clear rescope plan.

---

## Recommendation

**Option A + Option C combined.** Ship this diagnostic memo NOW as the
auditability anchor per Convention #56 (this task's closure). Land the
source-generator retighten in a separate commit that operator approves +
schedules alongside the next L3 rescore window. When the rescore lands,
this memo's "STATUS" line changes from OPEN to CLOSED, the 7 affected
countries' ssi-data.json refresh, and downstream deliverables (maps, country
pages, cross-country comparisons) refresh from the corrected values.

**Do NOT choose Option B** — widening the registry sacrifices the resilience
signal the tight band was designed to surface. R7_cyber is meant to be a
tight resilience-modifier band; the DRIFT is the anomaly, not the spec.

---

## Convention preservation

- **Convention #56 (visibly-honest degradation)**: this memo IS the audit
  trail for the current drift state.
- **Convention #46 (per-country identity)**: fix applies at the L3 generator
  level, not portfolio-scoped.
- **Convention #64 (strict per-country resolution)**: rescore is per-country,
  never cross-country.

## Cross-references

- Task #117 parent: Cause D2 modifier-drift diagnostic (R6_seismic /
  R7_cyber / 4-modifier drift class)
- Task #159 (this): R7_cyber cohort-wide quantification + remediation options
- `scripts/pipeline/config.py::_MODIFIER_RANGES` — registry pin
- `scripts/score-country.py::133` — primary L3 emission
- `scripts/enrich_esg_gaps.py::325` — post-hoc fill
- `scripts/validate_schema.py::222` — validator range
- `scripts/refresh_f_l4_2_legacy_drift.py` — legacy drift refresh utility
  (candidate landing point for the fix)

## Status

**OPEN** — Awaiting operator decision on Option A rescore scheduling.
Investigation task #159 CLOSED per this memo shipping.
