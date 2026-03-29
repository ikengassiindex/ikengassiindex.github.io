# Mexico Pipeline Data Sources

## Seismic & Volcanic Hazard
- **CENAPRED** Atlas Nacional de Riesgos — PGA grid (475-year return period)
- **SSN** Servicio Sismológico Nacional — historical seismicity catalogue
- **SGM** Servicio Geológico Mexicano — geological hazard maps

Placeholder: `cenapred_pga475.csv` (format: lon,lat,pga_g)
To be populated from CENAPRED open data or SSN seismicity grids.

## Socio-Economic
- **INEGI** Instituto Nacional de Estadística y Geografía
- **CONEVAL** Consejo Nacional de Evaluación de la Política de Desarrollo Social
- **CONAPO** Consejo Nacional de Población

Placeholder: `inegi_estado_socioeconomic.csv` (format: estado,region,gdp_per_capita,unemployment_rate,elderly_pct,ep_rate,migration_score)
To be populated from INEGI Banco de Información Económica + CONEVAL poverty metrics.

## Climate Baseline (cross-cutting)
- **ERA5** reanalysis grid for Mexico bounding box: `era5_baseline_mexico.csv`
- Located in `../cross-cutting/era5_baseline_mexico.csv`
- Bounding box: lat [14.5, 32.8], lon [-118.5, -86.5]

## Data Refresh Schedule
- First automated pipeline run: **May 2026** (2nd Thursday)
- Frequency: monthly (1st Thursday data enrichment, 2nd Thursday publish)
