# v4.5 Planning Document

**Created**: 8 June 2026
**Status**: 🟢 Pre-kickoff planning (v4.0.2 closure in flight; v4.5 starts after climate batch + Gate 2 complete)
**Predecessor**: v4.0.2 with Phase 1.5 (P15-A through P15-F) closure

---

## 1. v4.5 Scope (high-level)

v4.5 is the next major version after v4.0.2 closure. Three workstreams:

| Workstream | Driver | Deliverable |
|---|---|---|
| **A. Direct national agency ingestion** | Operator audit requirement — "national met services, much more auditable" | Populate `_NATIONAL_MET_FETCHERS` (climate) + `_NATIONAL_SEISMIC_FETCHERS` (seismic) registries for top-10 countries (85% of substations) |
| **B. Methodology refinement** | Score-shift analysis from v4.0.2 Phase 1.5 acceptance — material R2/R6 changes from per-region socio + true heat/ice days | Recalibrate modifier bands, potentially add new modifiers (R11+), reconcile against v4.0.2 baselines |
| **C. ESG additions** | Pre-existing `ESG addition` folder in SSI Index/ parent dir (operator-prepared) | Integrate ESG modifiers into v4.5 formula construct (likely R12/R13 sustainability metrics) |

This doc focuses primarily on **Workstream A** (the most concrete + biggest auditability win). Workstreams B + C are placeholders for operator scoping.

---

## 2. Workstream A — Direct National Agency Expansion

### 2.1 Why this matters

The Phase 1.5 closure (v4.0.2) established a 3-tier resolution chain:
- **Tier 1a** (direct national): empty stubs — _NATIONAL_MET_FETCHERS, _NATIONAL_SEISMIC_FETCHERS
- **Tier 1b** (consolidated international with per-station attribution): GHCN-D climate, GEM 2023.1 seismic
- **Tier 2** (gridded international fallback): ERA5-Land climate, GEM 2023.1 seismic (used as both Tier 1b + Tier 2)

The architectural promise: each substation's climate + seismic data is traceable to a national agency.

Phase 1.5 delivered the **architecture**. v4.5 delivers the **direct connectors** that activate Tier 1a — replacing GHCN-D's NOAA-aggregated indirection with direct national agency endpoints.

### 2.2 Expected audit improvements

| Before (v4.0.2) | After (v4.5 direct connectors) |
|---|---|
| US climate: GHCN-D station data tagged "NOAA-COOP" | US climate: NCEI nClimGrid-Daily 4km grid, direct DOI provenance |
| US seismic: GEM 2023.1 0.05° (aggregated from USGS NSHM) | US seismic: USGS NSHM 2023 fault-resolved raster, direct USGS provenance |
| Japan climate: GHCN-D station data tagged "JMA" | Japan climate: JMA AMeDAS ~1km network, direct JMA endpoint |
| Japan seismic: GEM 2023.1 (aggregated from NIED) | Japan seismic: NIED J-SHIS 1km municipality grid, direct NIED API |
| Germany climate: GHCN-D station data tagged "DWD" | Germany climate: DWD CDC HYRAS-DE 5km grid, direct DWD endpoint |

For LP-DD / academic-publication / USCO-deposit use: direct endpoints with DOIs are materially more defensible than NOAA-aggregated proxies.

### 2.3 Prioritisation — top 10 countries cover 85% of substations

| Rank | Country | Substations | % of total | Climate priority | Seismic priority |
|---:|---|---:|---:|---|---|
| 1 | us | 45,003 | 34.4% | NCEI nClimGrid 🥇 | USGS NSHM 2023 🥇🥇 (massive improvement) |
| 2 | canada | 24,986 | 19.1% | ECCC ANUSPLIN | NRCan 5th Gen |
| 3 | germany | 13,251 | 10.1% | DWD CDC HYRAS-DE | BGR D-A-CH |
| 4 | portugal | 10,191 | 7.8% | IPMA SCIA | IPMA + LNEC |
| 5 | australia | 8,500 | 6.5% | BOM AGCD | Geoscience Aus NSHA18 |
| 6 | france | 7,898 | 6.0% | Météo-France SAFRAN | BRGM Plan Séisme |
| 7 | norway | 6,495 | 5.0% | MET Norway senorge | NORSAR + NGU |
| 8 | japan | 5,981 | 4.6% | JMA AMeDAS | NIED J-SHIS 🥇 (1km grid) |
| 9 | italy | 4,293 | 3.3% | ISPRA SCIA / ARPA | INGV MPS04 ✅ (already done) |
| 10 | turkey | 4,092 | 3.1% | MGM | AFAD national |
| **Total top-10** | **130,690** | **~85%** | | |

### 2.4 Effort estimate per workstream-A connector

| Connector type | Per-country effort | Why |
|---|---|---|
| Standard REST API (DWD CDC, MET Norway thredds, BOM, ECCC) | ~4-6h | API auth + bbox query + CSV parse + tests |
| Custom shapefile / raster download (USGS NSHM, NIED J-SHIS, BGR) | ~8-12h | rasterio integration + GeoTIFF clip + station-equivalent extraction |
| Restricted/registration-required (JMA AMeDAS bulk download) | ~12-16h | Account setup + token management + multi-file download orchestration |

Top-10 total: **~80-120h of focused connector work**. Splittable into 4-6 weeks of part-time effort or 2-3 weeks of dedicated effort.

### 2.5 Sequencing recommendation

**Phase A1 (Week 1-2)** — Highest-impact-per-hour:
1. US seismic (USGS NSHM 2023 raster) — dramatic improvement over GEM 0.05° for the biggest country
2. US climate (NCEI nClimGrid-Daily 4km) — covers 45k substations with finer grid + direct attribution
3. Japan seismic (NIED J-SHIS 1km) — only country where direct fetch is 10× finer than GEM

**Phase A2 (Week 3-4)** — European cluster:
4. Germany climate (DWD CDC HYRAS-DE) — open API, well-documented
5. Germany seismic (BGR D-A-CH) — covers DE+AT+CH in one dataset
6. France climate (Météo-France SAFRAN) — public API
7. France seismic (BRGM Plan Séisme) — public download

**Phase A3 (Week 5-6)** — Remaining top-10:
8. Canada climate (ECCC ANUSPLIN) + Canada seismic (NRCan 5th Gen)
9. Australia climate (BOM AGCD) + Australia seismic (NSHA18)
10. Norway climate (MET senorge) + Japan climate (JMA AMeDAS)

**Phase A4 (deferred)** — Long tail (29 small countries):
- Continue using Tier 1b GHCN-D + Tier 2 GEM 2023.1 (current state)
- Document the trade-off explicitly in audit deliverables
- Add direct connectors opportunistically as operator needs grow

---

## 3. Workstream B — Methodology Refinement (placeholder)

Phase 1.5 will trigger material score shifts (documented in PHASE_1_5_ACCEPTANCE_REPORT.md §5):
- R2 social-equity modifier changes from national-uniform → per-region socio
- R6c/R6d/R6e from analytic zero → true day counts

v4.5 should re-calibrate modifier bands so the distributions look right after the data improvement. Open questions for operator scoping:
- Do current modifier ranges `[0.80, 1.35]` etc. still bracket the new distributions, or do they need widening?
- Are there new modifiers worth adding (R11 = grid-forming inverter penetration? R12 = climate-adaptation investment?)
- Should we add a v4.5 backward-compat shim for v4.0.2 baselines?

These belong in a separate `V4_5_METHODOLOGY_SCOPE.md` once Phase 1.5 acceptance gates complete.

---

## 4. Workstream C — ESG Additions (placeholder)

Operator's pre-existing `SSI Index/ESG addition` folder contains material that should fold into v4.5:
- Likely new modifiers in the R10+ space (energy justice, social equity, adaptive capacity per modifier briefs B8.4-B8.6)
- Cross-references to existing R10_just per-modifier brief (Phase 0 B8.6)
- Likely integration with SFDR / EU Taxonomy disclosure framework

Out of scope for this doc; flagged for v4.5 kickoff.

---

## 5. Dependencies for v4.5 kickoff

| Item | Status | Blocker? |
|---|---|---|
| v4.0.2 Phase 1.5 closure (PR-8) | ⏳ Pending climate batch + Gate 2 | ⚠️ Yes — v4.5 should not start until v4.0.2 is tagged + committed |
| v4.0.2 score-shift analysis (PHASE_1_5_ACCEPTANCE_REPORT §5) | ⏳ Pending Gate 2 | Yes — informs Workstream B scope |
| USCO_005 refresh decision | Pending operator | No — can run in parallel |
| Per-country docs batch refresh script | Queued (PRE_PR_8_READINESS §4) | No — cosmetic, can wait |

---

## 6. v4.5 deliverable artifacts (target)

| Artifact | Source |
|---|---|
| `V4_5_DIRECT_AGENCY_EXPANSION_PLAN.md` (per-country build cards) | This planning sprint ✅ |
| `_NATIONAL_MET_FETCHERS` registry populated for top-10 climate sources | Phase A1-A3 |
| `_NATIONAL_SEISMIC_FETCHERS` registry populated for top-10 seismic sources | Phase A1-A3 |
| Updated `SOURCES_AND_LICENSES.md` with Tier 1a fully wired | Per connector |
| Updated `PHASE_1_5_ACCEPTANCE_REPORT.md` → `v4.5 release notes` | Post-Workstreams A+B+C |
| Updated `ssi-metadata.js` × 39 countries with direct-agency entries | Backfill script extension |
| Validator updates for new R-modifier ranges | Workstream B |
| USCO_005 refresh memo if filed | Workstream C |

---

## 7. Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| National agency APIs change (DWD CDC URL restructure, JMA bulk-download throttling) | Medium | Per-country breakage | Tier 1b GHCN-D and Tier 2 ERA5-Land/GEM remain as documented fallbacks |
| USGS NSHM 2023 raster is large (~500 MB) and crosses GitHub file-size limits | High | Storage friction | Stage on Zenodo or S3 mirror, `.gitignore` the local copy, document operator one-time download (same pattern as GEM 2023.1) |
| JMA AMeDAS requires Japanese-language registration | Medium | Connector blocked | Fallback to Tier 1b GHCN-D for Japan (JMA is contributing agency — same upstream source) |
| Score-shifts from v4.5 Workstream A look like regressions to LPs comparing v4.0.2 → v4.5 | Medium | Comms | Document explicitly in release notes; provide v4.0.2 → v4.5 reconciliation table |
| ESG addition (Workstream C) requires methodology brief rewrites | Low | Doc work | Plan B8.4-B8.6 per-modifier brief refresh as part of Workstream C scope |
