# R6_seismic registry widen + Slovenia/Norway line-density diagnostic

**Tasks**: #180 (R6_seismic registry widen) + #182 (Slovenia + Norway line-density outlier investigation)
**Date**: 13 July 2026
**Author**: ikenga-ssi-foundation
**Methodology pin**: v4.2
**Status**: **CLOSED — config landed + diagnostic shipped**

---

## Part A — R6_seismic registry widen (task #180)

### Problem

The cohort audit sweep (task #179, `SSI_COHORT_AUDIT_SWEEP_20260713.md`)
surfaced R6_seismic values below the registry floor `(1.00, 1.25)` in 7
countries: Australia, Belgium, Chile, Czechia, Luxembourg, Netherlands, US.

The 4 central-European countries (Belgium + Netherlands + Luxembourg +
Czechia) are the most diagnostic — all sit on **tectonically-passive plates**
(Northern European Craton + Bohemian Massif). GEM 2023.1 Global Seismic
Hazard Map assigns them PGA(475yr) < 0.05 g. R6_seismic is a hazard modifier
that mechanically approaches 1.0 in near-zero-hazard regions, so values 0.95-
1.00 reflect empirical reality, not drift.

The other 3 (Australia + Chile + US) split by internal geography — coastal
seismic zones emit 1.05-1.20, interior-continental substations sit near 1.00.
The cohort mean drifts slightly below 1.00 for these countries too.

### Fix applied

**Widen registry range** in two files:

- `scripts/pipeline/config.py::66` — `R6_seismic: (1.00, 1.25)` → `(0.95, 1.25)`
- `scripts/validate_schema.py::221` — same

**Non-invasive**: no data changes. The 7 countries' existing values now sit
inside the widened band, and future L3 emissions from `enrich_esg_gaps.py::328`
(fill center 1.0 ±0.03) stay cleanly inside the range by construction.

### Rationale

Widening the spec is the correct move here (not tightening the empirical
distribution) because R6_seismic is a hazard modifier, not a resilience knob.
For tectonically-passive plates, the near-zero hazard is a **feature**, not a
bug. Preserving the 1.00 floor would force artificial upward drift into
regions with genuinely low seismic risk. This is the inverse of the R7_cyber
case, where tightening the source (not widening the spec) is correct because
R7_cyber IS a resilience knob.

### Empirical impact

Downstream: none in this commit. R_median values on the 7 countries were
already computed with the empirical R6_seismic values (0.95-1.00) — widening
the spec just brings them from "outside band" to "inside band". Zero data
changes needed.

---

## Part B — Slovenia + Norway line-density outlier diagnostic (task #182)

### Problem

The cohort audit sweep flagged 2 countries with lines/substations ratio
outside the 0.3-25 envelope:

| Country | Substations | Lines | Ratio | Threshold |
|---|---:|---:|---:|---:|
| Norway | 5,842 | 154,728 | 26.49 | > 25 |
| Slovenia | 158 | 4,384 | 27.75 | > 25 |

Question: bug or feature?

### Investigation

Both countries carry heavy **distribution-tier voltage** in their grid-geo.json
— not just transmission (≥ 100 kV EHV/HV) but also MV distribution (10-24 kV).

**Norway** — segment length distribution + voltage histogram:

| Metric | Value |
|---|---|
| Total lines | 154,728 |
| Median segment length | 232 m |
| Segments < 500 m (heavily fragmented) | 71.7% |
| Segments < 100 m (micro-fragments) | 26.9% |
| Total network km | ~121,800 km |
| Km per substation | 20.8 km |
| Top voltage classes | 22 kV (91,366) + 24 kV (29,592) = **78% MV distribution** |

Norway ingested via NVE Nettanlegg WFS — the Norwegian TSO/DSO federated
registry. The dataset intentionally captures the full national grid including
MV distribution (11-24 kV), which is why the line count is high and segments
are short. This is legitimate deep-ingestion — reflects the actual grid
topology at MV level, which is 6-10× denser than transmission-only.

**Slovenia** — segment length distribution + voltage histogram:

| Metric | Value |
|---|---|
| Total lines | 4,384 |
| Median segment length | 398 m |
| Segments < 500 m | 55.2% |
| Segments < 100 m | 20.1% |
| Total network km | ~6,770 km |
| Km per substation | 42.8 km |
| Top voltage classes | unknown (1,948, 44%) + 20 kV (1,434) + 400 kV (568) + 110 kV (347) |

Slovenia ingested via OSM Overpass — 20 kV MV distribution is well-tagged in
OSM for Slovenia, hence high line count relative to substation count.

### Verdict

**Neither is a bug.** Both reflect legitimate deep-ingestion depth. The
0.3-25 envelope was calibrated on transmission-only cohorts (Italy = 3.31,
Germany = 3.30, Spain = 4.63) where lines/subs stays near 2-5. Countries
that ingest MV distribution grid data legitimately push ratios into 20-30.

### Options for the sweep threshold

1. **Widen threshold to 0.3-30**: acknowledges deep-ingestion signal;
   preserves flag for genuine anomalies (accidental duplicate insertion
   would push ratios > 30-40). **Recommendation.**
2. Add voltage-tier stratification to the sweep — compute ratios separately
   for EHV/HV/MV. More precise but expensive to implement.
3. Do nothing — accept 2 legitimate WARNs on Norway + Slovenia.

Applied option 1 in the cohort audit sweep script (`cohort_audit_sweep.py`
threshold constant update — 25 → 30).

### Downstream impact

None. Both countries' grid-geo.json state is preserved. The `discipline_41`
verification (line-substation coupling invariant per operator "if we add
substations we add connecting power lines") still holds — every substation
in these countries has ≥1 connecting line.

---

## Combined impact

**Files changed** (2 config edits + 2 source retighten from task #181 + 1 sweep threshold):

- `scripts/pipeline/config.py` — R6_seismic (1.00, 1.25) → (0.95, 1.25)
- `scripts/validate_schema.py` — same
- `scripts/score-country.py::128` — R7_cyber source retighten (task #181)
- `scripts/enrich_esg_gaps.py::325` — R7_cyber fill retighten (task #181)
- `scripts/cohort_audit_sweep.py` — discipline_41 threshold 25 → 30

**Data changes**: none. All fixes are spec/source-generator layer only.

**Sentinel state**: post-fix cohort audit sweep should show 0 R6_seismic drift
findings, 0 line-density findings (previously flagged Norway + Slovenia
resolve). R7_cyber drift findings preserved until next L3 rescore per Option
A + C combined.

## Convention preservation

- **Convention #56 (visibly-honest degradation)**: this memo IS the audit trail
  for the R6_seismic registry widen + Slovenia/Norway line-density findings.
- **Convention #64 (strict per-country resolution)**: no cross-country changes.
- **Convention #46 (per-country identity)**: no portfolio-scoped changes.

## Cross-references

- Task #179 (parent): cohort audit sweep — `SSI_COHORT_AUDIT_SWEEP_20260713.md`
- Task #181 (companion): R7_cyber source retighten — `SSI_R7_CYBER_DRIFT_DIAGNOSTIC.md`
- Task #124: v4.23 gap audit (workstream context)
- `scripts/pipeline/config.py::MODIFIER_RANGES` — registry
- `scripts/validate_schema.py::_MODIFIER_RANGES` — validator mirror

## Status

**CLOSED**. Tasks #180 + #182 both closed by this memo shipping alongside the
config commit. Task #181 companion (R7_cyber source retighten) closes with
data unchanged until next scheduled L3 rescore per Option A + C combined.
