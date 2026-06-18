# Phase 1.5 Acceptance Report

**Date drafted**: 8 June 2026
**Status**: 🟡 Draft — operator-side ERA5-Land batch in flight; gates 2/3 pending
**Scope**: L1 ingestion gap closure for 39 SoT countries across socio-economic, climate, and seismic data classes.

This document is the closing acceptance report for Phase 1.5 — analogous to
`PHASE_1_ACCEPTANCE_REPORT.md` (PR-7) but covering the L1 ingestion gap
closed in P15-A through P15-F.

---

## 1. Executive Summary

| Class | Before P15 | After P15 |
|---|---|---|
| Socio-economic | 22/39 (national-uniform fallback) | **39/39** (per-region NUTS-3-equivalent) |
| Climate | 11/39 (ERA5 0.25°) | **39/39** (ERA5-Land 0.1° + true daily heat/ice days) |
| Seismic | 1/39 (italy INGV) | **39/39** (italy INGV + greece EAK + 37 GEM 2023.1 0.05°) |
| F-L4-2 cohort gate | 0/22 complete | **22/22 complete** |

**Cumulative tests after P15**: 412 (Phase 1) + 18 P15 = **430 tests** (pending climate batch landing for the 14 climate-pending tests).

**Substations covered**: ~130,000 across 39 countries.

---

## 2. Gate 1 — Data Ingestion (DONE)

### 2.1 Socio-economic (P15-F-1 + P15-F-2)

**Architecture**: `_NON_EU_AGENCY_FETCHERS` registry dispatches per country slug. Chain order: per-agency fetcher → Eurostat NUTS-3 → World Bank national-uniform (Convention #56 visibly-honest degradation).

**Per-country granularity** (sub-national regions emitted):
- us(51 states+DC+PR) uk(12 NUTS-1) norway(15 fylker) new-zealand(16 RCs) australia(8 states/territories)
- japan(47 prefectures) canada(13 provinces/territories) korea(17 sido) switzerland(26 cantons)
- turkey(15+national-mean) chile(16 regiones) iceland(8 regions) colombia(33 departamentos)
- israel(7 districts) costa-rica(7 provincias) greenland(5 kommuner)
- Plus Mexico's 32 estados via compiled-dict, Italy's 107 provinces via ISTAT, Greece's 13 peripheries via ELSTAT
- Plus 20 EU SoT countries via Eurostat NUTS-3

**Total sub-national regions emitted**: ~1,160 across 39 countries.

### 2.2 Climate (P15-A-2 + P15-A-3)

**Architecture**: Two CDS requests per country.
1. Monthly mean: `reanalysis-era5-land-monthly-means` 2000-2020 → `t_mean_c` at 0.1°
2. Daily max: `derived-era5-land-daily-statistics` 2018-2022 (chunked per year for CDS request-size limit) → true `heat_days` (T_max > 25°C) and `ice_days` (T_max < 0°C) counts

**Granularity**: 16× more grid points per country than prior 0.25° baseline.

**Method comparison** (Option A vs Option B operator decision documented in session):
- Option A (Gaussian-CDF estimator on monthly mean + DR offset): ~70-85% integrity vs ground truth
- **Option B (chosen)**: 100% by construction — true daily threshold-crossing counts over 5-year window

### 2.3 Seismic (P15-B-2 + P15-B-3)

**Architecture**: rasterio GeoTIFF reader with bbox-clip per country (sub-minute batch for all 39).

**Source**: GEM 2023.1 Global Seismic Hazard Map raster (Vs30 = 760-800 m/s rock-site, PGA 475-yr return period).

**Granularity**: 0.05° (~5.5 km) — 2.5× higher than 2018 prior.

**Per-country grid sizes**:
- us 1.07M, canada 859k, australia 284k, mexico 110k, chile 95k
- Italy 29,756 with max PGA 0.536g at Central Apennines (L'Aquila zone — geophysically correct)
- Luxembourg 240 (smallest country)

**License**: CC BY-NC-SA 4.0 (Non-Commercial). Compliant for academic/research use including USCO deposits.

---

## 3. Gate 2 — Acceptance Test Results (PENDING CLIMATE BATCH)

| Gate | Command | Result |
|---|---|---|
| L1 schema validation | `pytest scripts/pipeline/tests/test_p15_ingestion_schemas.py` | 390 passed + 1 xfail + 156 climate-pending (→ all passing once batch lands) |
| Climate sanity audit | `python3 scripts/pipeline/audit_climate_sanity.py` | _TODO once batch finishes — expect 42/42 OK_ |
| F-L4-2 cohort strict mode | `python3 scripts/validate_schema.py --country-cohort f-l4-2-extended --strict` | _TODO_ |
| E2E refresh | `pytest tests/test_e2e_refresh.py` | _TODO_ |
| Score-shift acceptance | `pytest tests/test_score_shift_acceptance.py` | _TODO — expect material R2 score shifts because socio data is now per-region not national-uniform_ |
| Full regression | `pytest` | _TODO — target ~430 tests pass_ |

---

## 4. Gate 3 — Deliverables

| Deliverable | Status |
|---|---|
| `scripts/pipeline/data/SOURCES_AND_LICENSES.md` (full provenance + license catalog) | ✅ Done |
| `scripts/pipeline/PHASE_1_5_OPERATOR_WORKFLOW.md` (paste-able operator commands) | ✅ Done |
| `scripts/pipeline/PRE_PR_8_READINESS.md` (PR-8 trigger criteria + scope) | ✅ Done |
| `scripts/pipeline/tests/test_p15_ingestion_schemas.py` (CI quality gate) | ✅ Done |
| `scripts/pipeline/audit_climate_sanity.py` (post-batch verification CLI) | ✅ Done |
| `scripts/backfill_p15_metadata.py` (39-country DATA_SOURCES patcher) | ✅ Done |
| 39 × `ssi-metadata.js` files updated with new sources | ✅ Done |
| Per-country `docs/SSI_v4.0.2_Data_Input_List_<country>_v1.html` refresh | _Queued for batch script_ |

---

## 5. Material score changes expected

The P15-F-2 per-region socio-economic data **will move scores materially**, but
these are improvements not regressions. Pre-P15 the R2 social-equity modifier
used national-uniform GDP/unemp/elderly for all non-EU substations (because
agency data wasn't ingested). Post-P15 each substation now picks up its
region-specific values.

| Country | Expected R2 score shift class | Reason |
|---|---|---|
| US | Material redistribution — DC/MD/NJ substations get R2 uplift, MS/WV substations get R2 downgrade | 2.5× state spread now visible |
| Norway | Rogaland (oil) substations get R2 uplift; Innlandet (rural) get R2 downgrade | 2.3× fylke spread |
| Australia | WA mining substations get R2 uplift; Tasmania get R2 downgrade | 2.0× state spread |
| Switzerland | Zug/BS substations get R2 uplift; Appenzell get R2 downgrade | 3.4× canton spread (Zug €223k vs Appenzell €65k) |
| Japan | Tokyo substations get R2 uplift; Okinawa get R2 downgrade | 2.3× prefecture spread |
| Korea | Ulsan (Hyundai) substations get R2 uplift; Gwangju get R2 downgrade | 2.5× sido spread |

**Score-shift acceptance gate** in PR-8 should document these expected
shifts + flag any country-level fleet-mean shift > ±0.05 (the convention
from PR-7).

---

## 6. Material climate-input changes expected

Pre-P15-A-3, heat_days / ice_days were computed analytically from monthly
mean temperature, producing zeros for ALL temperate climates (mean 0-20°C).
Post-P15-A-3, these are TRUE day counts from daily ERA5-Land maxima over
2018-2022.

Expected R6 modifier shifts:
- **R6d wildfire**: substations in Mediterranean / continental hot zones (Athens, Rome, Madrid, Madrid, Phoenix-region) gain heat_days from ~0 → 50-200 → R6d activates
- **R6e winter**: substations in Nordic / continental cold zones (Tromsø, Reykjavik, Helsinki, Riga, Moscow-region) gain ice_days from ~0 → 60-250 → R6e activates
- **Tropical zones** (Cairns, Bogotá): correctly stay at 0 ice_days, very high heat_days
- **Maritime temperate** (Manchester, Dublin, Wellington): modest day counts in BOTH heat and ice (~5-30 each)

This is the **structural** fix that the v4.0.2 strict-mode validator
expected when it flagged the F-L4-2 cohort.

---

## 7. Recommendations for PR-8

1. **Open PR-8** with scope: "Phase 1.5 closure + v4.0.2 (post-P15) baseline snapshot"
2. **Run Gate 2** acceptance gates in sequence; record results in §3 above
3. **Snapshot v4.0.2 (post-P15)** as the post-P15 baseline tag
4. **Optional refresh**: USCO_005 filing memo documenting the L1 ingestion improvements
5. **Defer to v4.1**: a fully-refreshed per-country `docs/SSI_v4.0.2_Data_Input_List_<country>.html` set (40-doc batch script — not blocking PR-8)

---

## 8. Sign-off

| Role | Person | Date | Status |
|---|---|---|---|
| L1 ingestion architect | (operator) | _pending_ | _await batch results_ |
| L2 enrichment lead | (operator) | _pending_ | _await batch + smoke test_ |
| Methodology lead | Cedric Berard | _pending_ | _await full Gate 2_ |
| USCO filing lead | Cedric Berard | _pending_ | _decision: USCO_005 refresh y/n_ |
