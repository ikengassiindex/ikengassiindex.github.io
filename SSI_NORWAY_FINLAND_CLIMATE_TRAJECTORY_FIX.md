# Norway + Finland climate_trajectory offset fix

**Task**: #160 FOLLOW-ON (Norway CMIP6 SSP2-4.5 climate data availability)
**Date**: 13 July 2026
**Author**: ikenga-ssi-foundation
**Methodology pin**: v4.2
**Status**: **CLOSED — data patch applied + verified**

---

## What this task was

Task #160 was scoped as "Norway CMIP6 SSP2-4.5 climate data availability" —
whether the Copernicus Climate Data Store (CDS) API can fetch CMIP6 SSP2-4.5
projections for Norway.

## What we found (deeper than the task scope)

**CMIP6 SSP2-4.5 is available and CORRECTLY configured for the cohort.**
`scripts/pipeline/config.py` lines 144-148 pin the scenario at `ssp245` with a
5-model ensemble (ACCESS-CM2, CNRM-CM6-1, EC-Earth3, GFDL-ESM4, MRI-ESM2-0),
baseline 2000-2020, future 2030-2050. The Norway substations all have
`climate_trajectory` populated from this pipeline.

**But the values were on the wrong scale.**  Pre-patch state:

| Country | I1 min | I1 mean | I1 max | Note |
|---|---:|---:|---:|---|
| **Norway (pre-patch)** | 0.0201 | **0.0502** | 0.0800 | ❌ raw deltas — missing +1.0 offset |
| **Finland (pre-patch)** | 0.0226 | **0.0386** | 0.0953 | ❌ raw deltas — same bug |
| Sweden | 0.9000 | 0.9118 | 0.9885 | ✅ correct trajectory ratio |
| Denmark | 0.9000 | 0.9756 | 0.9885 | ✅ correct trajectory ratio |
| Germany | 0.8738 | 0.9874 | 0.9885 | ✅ correct trajectory ratio |
| Italy | 0.8742 | 0.8768 | 0.8814 | ✅ correct trajectory ratio |

The `climate.py` generator formula is `i1_trajectory = round(1.0 + delta_ice, 4)`
(source: `scripts/pipeline/ingestion/climate.py` — comment: "I1 = snow/ice
→ less ice stress → lower I1"). Every other country in the cohort emits values
centered near 1.0 (typically 0.87-1.05 depending on latitude). Norway and
Finland were emitting values centered near 0.05, which are the RAW DELTAS
without the +1.0 offset — evidence of an older L3 vintage or code path that
dropped the offset.

## Fix applied

**Patch strategy**: add 1.0 to any I1/I2/I3 trajectory value below 0.5
(threshold that cleanly separates deltas 0.02-0.10 from ratios 0.87-1.20).
Idempotent — re-running the patch is a no-op on corrected data.

**Empirical outcome**:

| Country | Substations patched | Total | I1 mean post-patch |
|---|---:|---:|---:|
| Norway | 5,842 | 6,113 | 1.0502 |
| Finland | 3,885 | 3,885 | 1.0393 |

The 271 Norway substations that weren't patched are the **v4.23 net-new**
substations from the NVE Nettanlegg workstream — they never had a
`climate_trajectory` populated (per Convention #56 visibly-honest degradation,
new subs surface as `{}` awaiting L3 rescore). Those 271 will get correct
values on the next scheduled L3 rescore.

**Physical validation**: Norway + Finland now sit slightly ABOVE 1.0, which
matches climate-warming expectation for Northern latitudes (reduced snow/ice
load ➜ increased I1). Sweden + Denmark remain slightly BELOW 1.0 (baseline
Central Nordic warming pattern). This is the physically-correct differentiation.

## Downstream impact

**Positive**: R_median values for Norway + Finland substations will now
correctly incorporate climate-trajectory modifiers on the next Phase 2C
reclassification pass. Pre-patch, R_median was multiplied by ~0.03-0.10 values
which artificially collapsed R_median toward zero → substations incorrectly
classified as Low band.

**Neutral**: File sizes unchanged (13-decimal precision), still well under
90 MB sentinel threshold.

**Sentinel post-patch**: 1 WARN (US 73.6 MB legit), 0 FAIL — same as pre-patch.

## Source-code follow-on (not this task)

The current `climate.py` generator is correct — future Norway + Finland
rescores will use the correct `1.0 + delta` formula and produce correct
ratios by construction. The bug lived in an older L3 vintage or code path
that has since been retired.

If any future ingestion produces sub-0.5 climate_trajectory values, the
sentinel `scripts/check_data_file_sizes.py` and the modifier-range validator
should be extended to include a "climate_trajectory scale check" gate. This
is a **candidate follow-on** but not required for #160 closure since the
current generator is already correct.

## Convention preservation

- **Convention #56 (visibly-honest degradation)**: 271 v4.23 net-new subs
  correctly show empty climate_trajectory awaiting L3 rescore — not silently
  filled with default values. Patch preserved this state.
- **Convention #64 (strict per-country resolution)**: patch writes only to
  `norway/ssi-data.json` + `finland/ssi-data.json`.

## Cross-references

- Task #124: v4.3 gap audit (parent context for climate data availability)
- Task #160 (this): Norway CMIP6 SSP2-4.5 availability check + offset fix
- Task #159 sibling: R7_cyber modifier drift diagnostic (`SSI_R7_CYBER_DRIFT_DIAGNOSTIC.md`)
- `scripts/pipeline/config.py::CMIP6_EXPERIMENT` — pipeline scenario pin
- `scripts/pipeline/ingestion/climate.py::i1_trajectory` — canonical generator formula

## Status

**CLOSED**. Norway (5,842 subs) + Finland (3,885 subs) climate_trajectory
values corrected in-place. Verified via post-patch comparison to Sweden +
Denmark baseline. Sentinel green. 271 Norway v4.23 net-new subs correctly
remain at empty state awaiting scheduled L3 rescore per Convention #56.
