# SSI Pipeline — Data Sources & License Attribution

This document catalogs every external data source ingested by the pipeline
along with its licence, attribution requirement, refresh cadence, and the
canonical local path. Maintained per Phase 1.5 (P15-A through P15-F).

All ingestion code lives in `scripts/pipeline/ingestion/`. Each fetcher
emits a `_data_source` (socio) or `source_agency` (climate, seismic) field
per row so downstream consumers can audit provenance from any deliverable
back to the source national agency or international dataset.

## Defensive multi-tier architecture (P15-A-4 + P15-B-4)

For climate and seismic, the pipeline resolves data in **3 tiers** to
maximise auditability while guaranteeing universal coverage. The chain
prefers the most-granular and most-auditable source per country; falls
through to broader international datasets if the national source is
unavailable.

### Climate resolution chain (P15-A-4)

| Tier | Source | Resolution | Auditability |
|---|---|---|---|
| **1a — Direct national** | `_NATIONAL_MET_FETCHERS` registry (per-country direct ingestion: DWD CDC HYRAS, JMA AMeDAS, Météo-France SAFRAN, NOAA NCEI gridded) | 1-5 km | Highest — direct agency endpoint |
| **1b — NOAA-aggregated** | GHCN-D Global Historical Climatology Network — Daily; each station tagged with `source_agency` (DWD, JMA, MetOffice, BoM, ECCC, MET Norway, NOAA-COOP, etc.) per WMO contributing-agency protocol | Station ~1-5 km in populated areas | High — per-station provenance to contributing national agency |
| **2 — International fallback** | ERA5-Land 0.1° gridded reanalysis (Copernicus) | 0.1° (~11 km) | Medium — gridded reanalysis (no national-agency tag per cell) |

Currently: Tier 1a is empty stubs (v4.5 expansion target). Tier 1b GHCN-D
covers 39/39 countries. Tier 2 ERA5-Land is universal fallback when
GHCN-D station coverage is sparse.

### Seismic resolution chain (P15-B-4)

| Tier | Source | Resolution | Auditability |
|---|---|---|---|
| **1a — Direct national fetcher** | `_NATIONAL_SEISMIC_FETCHERS` registry (USGS NSHM 2023, NIED J-SHIS, BGR D-A-CH, BRGM Plan Séisme, IGN NCSE-02, BGS) | 1-5 km (fault-resolved for US) | Highest |
| **1b — National CSV (committed)** | `_SEISMIC_LOCAL_PATHS` per-country file (italy INGV MPS04 ✓, greece EAK ✓, mexico CENAPRED ✓; 14 other paths registered awaiting operator population) | 0.05-0.1° | High — direct agency dataset |
| **1c — Cache JSON** | Previous-run JSON cache | (same as source) | (same) |
| **1d — Live agency API** | `_SEISMIC_API_URLS` per-country endpoint | (varies) | High |
| **2 — International fallback** | GEM 2023.1 Global Seismic Hazard Map (international aggregation of national models per Pagani et al. 2018) | 0.05° (~5.5 km) | Medium — per-pixel traceable to contributing national model via GEM metadata |

Per-country source agency attribution for ALL 39 SoT countries is in
`_NATIONAL_SEISMIC_AGENCY` (seismic.py). Even countries currently using
Tier 2 GEM have a documented attributed national agency for audit.

---

## 1. Climate baseline — Copernicus ERA5-Land

| Field | Value |
|---|---|
| **Provider** | ECMWF / Copernicus Climate Data Store (CDS) |
| **Datasets** | `reanalysis-era5-land-monthly-means` (t_mean_c) + `derived-era5-land-daily-statistics` (heat_days, ice_days) |
| **Spatial resolution** | 0.1° native (~11 km mesh, land-only) |
| **Temporal resolution** | Monthly means 2000-2020 (climatology) + Daily max 2018-2022 (5-yr extreme-day window) |
| **Variables** | 2m_temperature (mean for monthly, max for daily) |
| **Licence** | EU Copernicus open licence (free for academic + commercial use) |
| **Attribution** | "Contains modified Copernicus Climate Change Service information [year]" |
| **DOI** | [10.24381/cds.e2161bac](https://doi.org/10.24381/cds.e2161bac) (ERA5-Land monthly), [10.24381/cds.e9c9c792](https://doi.org/10.24381/cds.e9c9c792) (daily statistics) |
| **Refresh cadence** | Monthly (CDS publishes ~3 mo lag) |
| **Canonical path** | `scripts/pipeline/data/cross-cutting/era5_baseline_<country>.csv` |
| **Schema** | `lat, lon, t_mean_c, heat_days, ice_days` |
| **Fetcher** | `scripts/pipeline/ingestion/climate.py::fetch_era5_baseline` |

### Citation block (paste into deliverables)

> Climate data derived from Copernicus ERA5-Land reanalysis (Muñoz Sabater, J.,
> 2019, doi:10.24381/cds.e2161bac) and ERA5-Land daily statistics
> (doi:10.24381/cds.e9c9c792). Contains modified Copernicus Climate Change
> Service information 2026.

---

## 2. Seismic hazard — GEM Global Seismic Hazard Map 2023.1

| Field | Value |
|---|---|
| **Provider** | Global Earthquake Model Foundation |
| **Dataset** | GEM 2023.1 Global Seismic Hazard Map (PGA 475-yr, rock-site Vs30=760-800 m/s) |
| **Spatial resolution** | 0.05° (3-arcmin, ~5.5 km mesh, global) |
| **Variables** | Peak Ground Acceleration (g) at 10% probability of exceedance in 50 years |
| **Licence** | **CC BY-NC-SA 4.0** (Attribution + Non-Commercial + ShareAlike) |
| **Attribution** | "K. Johnson, M. Villani et al. (2023). GEM Global Seismic Hazard Map v2023.1. DOI: 10.5281/zenodo.8409647" |
| **DOI** | [10.5281/zenodo.8409647](https://doi.org/10.5281/zenodo.8409647) |
| **Source URL** | https://www.globalquakemodel.org/product/global-seismic-hazard-map |
| **Download** | https://cloud.openquake.org/s/6SnFk2f92JEr76H (one-time, ~173 MB GeoTIFF) |
| **Refresh cadence** | ~5 years (GEM 2018 → 2023.1) |
| **Source raster** | `scripts/pipeline/data/cross-cutting/gshm-2023-1.tif` (.gitignored, operator-side download) |
| **Per-country CSV** | `scripts/pipeline/data/<country>/gem_pga475.csv` |
| **Schema** | `lon, lat, pga_g` |
| **Fetcher** | `scripts/pipeline/ingestion/seismic.py::fetch_gem_global_for_country` |

### Commercial-use caveat

CC BY-NC-SA 4.0's **non-commercial** clause is binding. The SSI Index in its
academic-research positioning (USCO deposit, methodology publication) is
non-commercial use. If the SSI Index is ever used as the basis for a paid
commercial product, a separate licence must be requested from GEM via the
"License Request" button on the product page.

For the 2 SoT countries that use their NATIVE seismic agency data instead
of the GEM fallback (italy via INGV MPS04, greece via EAK 2003), see
sections 2.1 + 2.2 below.

### 2.1. Italy — INGV MPS04 (national fallback, used in preference to GEM)
- Provider: Istituto Nazionale di Geofisica e Vulcanologia
- Dataset: Mappa di Pericolosità Sismica MPS04
- Licence: CC BY 4.0
- Canonical path: `scripts/pipeline/data/italy/ingv_mps04_pga475.csv`

### 2.2. Greece — EAK 2003 (national fallback, used in preference to GEM)
- Provider: Greek Earthquake Planning and Protection Organization (OASP)
- Dataset: EAK 2003 building zonation
- Licence: Public-sector data, open use
- Canonical path: `scripts/pipeline/data/greece/eak_pga475.csv`

---

## 3. Socio-economic — per-country statistics agencies

Per-region data at NUTS-3-equivalent granularity for all 39 SoT countries.
Three sourcing strata:

### 3.1. EU + EFTA via Eurostat NUTS-3 (20 countries)
| Field | Value |
|---|---|
| **Provider** | Eurostat |
| **Datasets** | `nama_10r_3gdp` (GDP/capita NUTS-3), `lfst_r_lfu3rt` (unemployment NUTS-2), `demo_r_pjanaggr3` (population by age) |
| **Licence** | **CC BY 4.0** (free use with attribution) |
| **Attribution** | "Source: Eurostat" + retrieved date |
| **Refresh cadence** | Annual (Eurostat publishes Q2-Q3 for prior year) |
| **Canonical path** | `scripts/pipeline/data/<country>/eurostat_nuts3_socioeconomic.csv` |
| **Countries covered** | belgium, czechia, denmark, estonia, finland, france, germany, greece, hungary, ireland, latvia, lithuania, luxembourg, netherlands, poland, portugal, slovakia, slovenia, spain, sweden |
| **Fetcher** | `scripts/pipeline/ingestion/socioeconomic.py::_fetch_eurostat_nuts3_regional` |

### 3.2. Non-EU per-agency fetchers (16 countries)
| Country | Source agency | Region level | Licence | Canonical path |
|---|---|---|---|---|
| us | US Census Bureau ACS 5-year | 51 states + DC + PR | Public domain (US Govt work) | `data/us/agency_regional_socioeconomic.csv` |
| uk | ONS Regional Accounts + Nomis | 12 NUTS-1 | Open Government Licence v3.0 | `data/uk/agency_regional_socioeconomic.csv` |
| norway | SSB Regional Accounts | 15 fylker | CC BY 4.0 | `data/norway/agency_regional_socioeconomic.csv` |
| new-zealand | Stats NZ | 16 regions | CC BY 4.0 | `data/new-zealand/agency_regional_socioeconomic.csv` |
| australia | ABS | 8 states/territories | CC BY 4.0 | `data/australia/agency_regional_socioeconomic.csv` |
| japan | Cabinet Office + MIC | 47 prefectures | Governmental open data | `data/japan/agency_regional_socioeconomic.csv` |
| canada | StatCan | 13 provinces/territories | Open Government Licence — Canada | `data/canada/agency_regional_socioeconomic.csv` |
| korea | KOSIS | 17 sido | Korean Open Government Licence | `data/korea/agency_regional_socioeconomic.csv` |
| switzerland | BFS Kantonale VGR | 26 cantons | Free use with attribution | `data/switzerland/agency_regional_socioeconomic.csv` |
| turkey | TÜİK Provincial GDP | 15 detailed + national-mean | Open data | `data/turkey/agency_regional_socioeconomic.csv` |
| chile | Banco Central + INE | 16 regiones | Open data | `data/chile/agency_regional_socioeconomic.csv` |
| iceland | Hagstofa | 8 regions | Free use | `data/iceland/agency_regional_socioeconomic.csv` |
| colombia | DANE Cuentas Departamentales | 33 departamentos | Open data | `data/colombia/agency_regional_socioeconomic.csv` |
| israel | CBS Statistical Abstract | 7 districts | Free use | `data/israel/agency_regional_socioeconomic.csv` |
| costa-rica | BCCR + INEC | 7 provincias | Open data | `data/costa-rica/agency_regional_socioeconomic.csv` |
| greenland | Statistics Greenland | 5 kommuner | Free use | `data/greenland/agency_regional_socioeconomic.csv` |

Registry: `scripts/pipeline/ingestion/socioeconomic.py::_NON_EU_AGENCY_FETCHERS`

### 3.3. Native pre-existing (3 countries)
| Country | Source | Path |
|---|---|---|
| italy | ISTAT | `data/italy/istat_province_socioeconomic.csv` |
| mexico | INEGI | `data/mexico/inegi_estado_socioeconomic.csv` |
| greece | ELSTAT | `data/greece/elstat_periphereia_socioeconomic.csv` |

### 3.4. Fallback chain order (in `fetch_socioeconomic_data`)
1. Local committed CSV (if exists)
2. Cache JSON
3. Compiled hardcoded (italy + mexico legacy)
4. Live ISTAT for italy
4.45 — `_NON_EU_AGENCY_FETCHERS` registry
4.5 — Eurostat NUTS-3
4.6 — World Bank Open Data national-uniform (last-resort, Convention #56)

---

## 4. Schema for downstream L2 spatial overlay

All ingestion outputs share canonical schemas so L2 enrichment can spatial-
join uniformly:

| Class | File pattern | Columns |
|---|---|---|
| Climate | `data/cross-cutting/era5_baseline_<country>.csv` | `lat, lon, t_mean_c, heat_days, ice_days` |
| Seismic | `data/<country>/gem_pga475.csv` (or `<agency>_pga475.csv` for native) | `lon, lat, pga_g` |
| Socio | `data/<country>/agency_regional_socioeconomic.csv` (or `eurostat_nuts3_*` or native) | `province, region, gdp_per_capita, unemployment_rate, elderly_pct, ep_rate, migration_score, _data_source` |

---

## 5. Phase 1.5 refresh history

| Phase | Date | Change |
|---|---|---|
| P15-A | 8 Jun 2026 | cdsapi + netCDF4 wired in (Korea pilot proved end-to-end) |
| P15-A-2 | 8 Jun 2026 | Climate ERA5 0.25° → ERA5-Land 0.1° (4× finer linearly) |
| P15-A-3 | 8 Jun 2026 | Added daily-statistics fetch for TRUE heat_days/ice_days counts |
| P15-B-2 | 8 Jun 2026 | Seismic switched from imagined CSV → GEM 2023.1 GeoTIFF raster (2.5× finer than 2018) |
| P15-C-1 | 8 Jun 2026 | Socio World Bank Open Data fallback wired in |
| P15-F-1 | 8 Jun 2026 | Eurostat NUTS-3 fetcher (20 EU countries) |
| P15-F-2 | 8 Jun 2026 | 16 non-EU per-agency fetchers (US/UK/JP/KR/etc.) |
