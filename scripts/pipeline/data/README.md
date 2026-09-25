# SSI Pipeline — Reference Data

This directory contains committed reference datasets used by the SSI data pipeline.
These are **real institutional open-source datasets**, downloaded once and versioned.

The pipeline reads from these files as its primary data path. Live API fetching
(Copernicus CDS, ISTAT SDMX, etc.) is an optional upgrade for fresher data, not
the default.

---

## How to source each dataset

### Cross-Cutting (all countries)

#### CMIP6 Climate Projections (`cross-cutting/cmip6_ssp245_deltas.csv`)

**Source:** Copernicus Climate Data Store
**URL:** https://cds.climate.copernicus.eu → "CMIP6 climate projections"
**Steps:**
1. Create a free CDS account at https://cds.climate.copernicus.eu
2. Accept the CMIP6 licence terms
3. Request: Variable = "Near-surface air temperature", Experiment = "ssp2_4_5",
   Models = ACCESS-CM2, CNRM-CM6-1, EC-Earth3, GFDL-ESM4, MRI-ESM2-0,
   Period = 2030–2050, Temporal resolution = monthly
4. Download NetCDF, compute ensemble median per 0.5° grid cell
5. Subtract 2000–2020 baseline (from ERA5) to get delta_t
6. Convert to CSV: lat, lon, delta_t_c, delta_heat_pct, delta_ice_pct, delta_wind_pct
**Format:** CSV with header row
**Licence:** CC-BY-4.0 (Copernicus)
**Refresh:** Static — CMIP6 data does not update frequently. Re-download when
  IPCC AR7 cycle produces new ensembles.

#### ERA5 Climate Baseline (`cross-cutting/era5_baseline_{country}.csv`)

**Source:** Copernicus Climate Data Store — ERA5 monthly averaged reanalysis
**URL:** https://cds.climate.copernicus.eu → "ERA5 monthly averaged data"
**Steps:**
1. Request: Variables = 2m temperature, 10m wind speed, min/max temperature;
   Years = 2000–2020; Monthly means; Area = country bounding box
2. Download NetCDF, compute 20-year annual means per grid cell
3. Derive: heat_days (days T_max > 30°C), ice_days (days T_min < 0°C)
4. Convert to CSV: lat, lon, t_mean_c, heat_days, ice_days, wind_speed
**Format:** CSV with header row
**Licence:** CC-BY-4.0 (Copernicus)
**Refresh:** Annual (ERA5 extends continuously)

#### ENISA / DESI Cyber Indices (`cross-cutting/cyber_indices.csv`)

**Source:** ENISA (enisa.europa.eu), EU DESI (digital-strategy.ec.europa.eu)
**Steps:**
1. Download the latest ENISA National Capabilities Assessment
2. Download the latest DESI country reports
3. Extract: country, enisa_score (0–100), desi_score (0–100)
**Format:** CSV: iso2, enisa_score, desi_score
**Licence:** Open Government
**Refresh:** Biennial (ENISA), Annual (DESI)

---

### Italy

#### INGV MPS04 Seismic Hazard (`italy/ingv_mps04_pga475.csv`)

**Source:** INGV — Istituto Nazionale di Geofisica e Vulcanologia
**URL:** https://esse1-gis.mi.ingv.it/
**Alternative URL:** https://www.ingv.it/cat/view/it/mappe-interattive/mps04
**Steps:**
1. Navigate to https://esse1-gis.mi.ingv.it/
2. Select "Download dati" → "PGA con probabilità di eccedenza del 10% in 50 anni"
3. Download the CSV or GeoTIFF grid (0.05° resolution)
4. If GeoTIFF: convert to CSV using GDAL: `gdal_translate -of XYZ input.tif output.csv`
5. Clean CSV to format: lon, lat, pga_g
   - Ensure PGA values are in units of g (gravitational acceleration)
   - Grid should cover: lat 35.0–47.5, lon 6.0–19.0, spacing 0.05°
**Format:** CSV with columns: lon, lat, pga_g
**Licence:** Open access (INGV institutional data)
**Refresh:** Static — MPS04 is a reference model. INGV MPS22 (when published)
  would be the next update.
**Size:** ~65,000 grid points (~2 MB CSV)

#### ISTAT Provincial Demographics (`italy/istat_province_socioeconomic.csv`)

**Source:** ISTAT — Istituto Nazionale di Statistica
**URL:** https://esploradati.istat.it/databrowser/
**Alternative:** https://www.istat.it/it/archivio/indicatori+territoriali
**Steps:**
1. Navigate to ISTAT Data Browser
2. Download "Conti economici territoriali" → GDP per capita by province
3. Download "Rilevazione sulle forze di lavoro" → Unemployment rate by province
4. Download "Popolazione residente per età" → Age breakdown by province (65+ %)
5. From ARERA: "Relazione annuale" → energy poverty rate by region (proxy to province)
6. Download "Bilancio demografico" → Internal migration by province
7. Merge into single CSV: province, region, gdp_per_capita, unemployment_rate,
   elderly_pct, ep_rate, migration_score
**Format:** CSV with header row
**Licence:** CC-BY-3.0 IT (ISTAT open data)
**Refresh:** Annual (census updates, quarterly for labour force)

#### ISPRA Corrosion / Air Quality (`italy/ispra_air_quality.csv`)

**Source:** ISPRA — Istituto Superiore per la Protezione e la Ricerca Ambientale
**URL:** https://www.isprambiente.gov.it/it/banche-dati/aria
**Steps:**
1. Download annual SO2 and PM10 monitoring station data
2. Geocode stations to province level
3. Map SO2/PM10 concentrations to ISO 9223 corrosion classes (C1–CX)
**Format:** CSV: province, so2_annual_ug, pm10_annual_ug, corrosion_class
**Licence:** Open Government
**Refresh:** Annual

#### IdroGEO Flood Risk (`italy/ispra_flood_risk.csv`)

**Source:** ISPRA — IdroGEO platform
**URL:** https://idrogeo.isprambiente.it/
**Steps:**
1. Navigate to IdroGEO → "Aree a pericolosità idraulica"
2. Download flood hazard zone shapefiles (HQ30, HQ100, HQ300)
3. Overlay substation coordinates onto flood zones
4. Assign flood_score: 0 (no risk), 1 (HQ300), 2 (HQ100), 3 (HQ30)
**Format:** CSV or SHP
**Licence:** Open Government
**Refresh:** Multi-year (updated after major events)

---

### Other Countries (add as ingestion expands)

Each country follows the same pattern: identify the national institutional source,
download once, commit as CSV, document the sourcing steps above.

See `SSI_ESG_Data_Sources_and_SDG_Mapping.md` (repo root) for the complete
per-country source catalogue.

---

## Data Provenance

All datasets in this directory must meet three criteria:
1. **Open access** — free to download, no commercial licence required
2. **Institutional provenance** — from national statistics offices, geological
   surveys, meteorological agencies, or EU institutions
3. **Citable vintage** — each file should note its publication date/version
   in the filename or in a companion `.meta.json` file

This ensures CSRD Article 29a limited assurance compliance: any auditor can
independently verify every input to every SSI ESG score.
