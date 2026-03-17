# SSI Index — Open-Source Data Sources & UN SDG Mapping for ESG Reporting

**Ikenga — SSI Enhanced Infrastructure Intelligence**
*Per-country data procurement roadmap and Sustainable Development Goals alignment*

---

## Part I: UN Sustainable Development Goals — ESG Report Alignment

Each of the 6 SSI ESG reports maps to specific UN SDGs. These connections are not cosmetic — they reflect the substantive overlap between what the SSI Index measures at substation level and what each SDG targets at systemic level. This alignment strengthens the case for foundation funding, OECD relevance, and investor reporting.

---

### Report 1: Climate Physical Risk Assessment → SDG 13, SDG 9, SDG 11

**SDG 13 — Climate Action** (primary)
The SSI Climate Physical Risk report directly quantifies climate hazard exposure (snow/ice, wind, heat stress) at infrastructure level using ERA5 reanalysis and CMIP6 forward projections. TCFD physical risk disclosure — which this report implements — is the operational translation of SDG 13 Target 13.1 ("Strengthen resilience and adaptive capacity to climate-related hazards"). By scoring each substation's vulnerability to acute and chronic climate events, the SSI Index provides the granular asset-level data that climate adaptation planning under SDG 13 requires.

**SDG 9 — Industry, Innovation, and Infrastructure**
SDG 9 Target 9.1 calls for "quality, reliable, sustainable and resilient infrastructure." The Markov degradation model (p_critical_10yr, p_critical_20yr) embedded in Report 1 directly measures infrastructure resilience over time under climate stress. The forward-looking IRI_forward metric — when activated with CMIP6 data — provides the scenario analysis that infrastructure planners need to assess whether grid assets will remain fit for purpose under warming scenarios.

**SDG 11 — Sustainable Cities and Communities**
SDG 11 Target 11.5 aims to "reduce the number of deaths and people affected by disasters." Substations are the critical nodes connecting generation to consumption. A substation that fails during a heatwave or ice storm cascades into community-level blackouts. By mapping seismic PGA, flood exposure, and climate hazard indices to each substation, Report 1 directly supports the disaster risk reduction intelligence that SDG 11 demands.

---

### Report 2: Grid Equity & Social Vulnerability → SDG 7, SDG 10, SDG 1

**SDG 7 — Affordable and Clean Energy** (primary)
SDG 7 Target 7.1 requires "universal access to affordable, reliable, and modern energy services." The SSI Social Vulnerability report measures energy poverty (V_socio, EP_rate), fiscal energy burden, and the concentration of grid risk in economically disadvantaged areas. When a substation serving an energy-poor region has a high Markov risk score, the ESG implication is that the most vulnerable households face the greatest risk of service disruption — a direct SDG 7 equity failure.

**SDG 10 — Reduced Inequalities**
SDG 10 Target 10.2 calls for "economic inclusion of all, irrespective of status." The SSI R3 modifier (social vulnerability) amplifies risk scores in regions with high unemployment, elderly concentration, and net outward migration. This captures the infrastructure dimension of inequality: communities experiencing demographic decline and fiscal stress are often the same ones with the oldest, least-maintained grid assets. Report 2 makes this spatial inequality visible and quantifiable.

**SDG 1 — No Poverty**
SDG 1 Target 1.4 targets "access to basic services." Energy poverty — households spending a disproportionate share of income on energy — is a direct poverty indicator. The SSI fiscal_energy_composite and V_socio fields measure this at substation catchment level. Report 2 surfaces which grid assets serve populations where energy is already unaffordable, adding urgency to maintenance and upgrade decisions.

---

### Report 3: EU Taxonomy Alignment → SDG 9, SDG 13, SDG 12

**SDG 9 — Industry, Innovation, and Infrastructure** (primary)
The EU Taxonomy Climate Delegated Act (Article 11) defines technical screening criteria for "climate change adaptation" in infrastructure. The SSI Taxonomy report uses R_median, 6 components, and the modifier architecture to classify substations against these criteria. SDG 9 Target 9.4 ("upgrade infrastructure to make it sustainable, with increased resource-use efficiency and clean technologies") is precisely what Taxonomy-aligned infrastructure assessment supports.

**SDG 13 — Climate Action**
EU Taxonomy Article 11 adaptation screening requires demonstrating that physical climate risks have been identified and that adaptation measures are in place. The SSI R5 (Asymmetric CI), R6a (Restoration speed), and Markov risk outputs provide the quantitative evidence base for this screening — connecting directly to SDG 13's climate resilience mandate.

**SDG 12 — Responsible Consumption and Production**
SDG 12 Target 12.6 encourages companies to "adopt sustainable practices and integrate sustainability information into their reporting cycle." The EU Taxonomy is the regulatory instrument that operationalises this for European financial markets. By producing Taxonomy alignment scores at asset level, Report 3 enables the sustainable finance reporting that SDG 12 envisions.

---

### Report 4: Energy Transition & DER Stress → SDG 7, SDG 13, SDG 9

**SDG 7 — Affordable and Clean Energy** (primary)
SDG 7 Target 7.2 requires "increase substantially the share of renewable energy in the global energy mix." Report 4 measures DER penetration (solar_mw, wind_mw, ev_share, DER_ratio) and the stress this places on distribution substations. The transition to clean energy is not just about generation capacity — it requires grid infrastructure that can absorb bidirectional power flows, EV charging load, and intermittent renewable output. Report 4 identifies where the grid is a bottleneck to SDG 7 achievement.

**SDG 13 — Climate Action**
SDG 13 Target 13.2 calls for "integrate climate change measures into national policies." Energy transition is the primary climate mitigation policy. The T1_score and DER_variability metrics in Report 4 assess whether grid infrastructure is keeping pace with the pace of decarbonisation, providing empirical feedback on whether transition policies are creating infrastructure stress.

**SDG 9 — Industry, Innovation, and Infrastructure**
The DER sub-metrics (DER_ratio, DER_variability, EV_load_ratio) measure how well existing infrastructure absorbs innovation — specifically distributed generation, storage, and electric mobility. This is SDG 9 Target 9.1 applied to the energy sector: can the grid support the innovation wave, or does it require upgrading?

---

### Report 5: Pollution & Corrosion → SDG 11, SDG 3, SDG 15

**SDG 11 — Sustainable Cities and Communities** (primary)
SDG 11 Target 11.6 aims to "reduce the adverse environmental impact of cities, including air quality." Transformer oil degradation, SF6 leakage, and corrosion-driven failures release pollutants that affect local environments. The SSI corrosion_class and E2_enrichment fields track environmental degradation at asset level. Where corrosion is advanced and maintenance deferred, the risk of pollutant release increases — directly relevant to urban environmental quality.

**SDG 3 — Good Health and Wellbeing**
SDG 3 Target 3.9 targets "reduce deaths and illnesses from hazardous chemicals and pollution." Transformer failures can release mineral oil, PCBs (in legacy units), and SF6 — a greenhouse gas 23,500 times more potent than CO2. Report 5 identifies substations where corrosion-driven failure risk is highest, enabling preventive maintenance before pollutant release occurs.

**SDG 15 — Life on Land**
SDG 15 Target 15.1 calls for conservation of terrestrial ecosystems. Grid infrastructure in rural and semi-rural areas intersects with natural habitats. Corrosion-driven equipment failure in these settings risks oil spills into soil and waterways. The E2_local enrichment factor in Report 5 captures the environmental sensitivity of the substation's surroundings.

---

### Report 6: Cybersecurity Exposure → SDG 9, SDG 16

**SDG 9 — Industry, Innovation, and Infrastructure** (primary)
SDG 9 Target 9.1 calls for "resilient infrastructure." In the context of digitalised grid systems, resilience includes cyber resilience. The SSI R7 modifier (cyber exposure) combines SCADA assessment, communication architecture analysis, and national-level cyber maturity (ENISA/DESI indices) to score each substation's digital vulnerability. A grid that is physically resilient but cyber-vulnerable is not truly resilient — Report 6 closes this gap.

**SDG 16 — Peace, Justice and Strong Institutions**
SDG 16 Target 16.6 calls for "effective, accountable and transparent institutions." Critical infrastructure cybersecurity is a governance imperative. The NIS2 Directive (transposed into EU member state law) mandates that energy operators implement cybersecurity risk management. Report 6 provides the assessment tool that demonstrates institutional compliance with these requirements.

---

### SDG Alignment Summary Table

| ESG Report | Primary SDG | Secondary SDGs | Key SSI Variables |
|---|---|---|---|
| R1 Climate Physical Risk | **SDG 13** Climate Action | SDG 9, SDG 11 | I1, I2, I3, I5, IRI_forward, R2, Markov, PGA |
| R2 Grid Equity & Social | **SDG 7** Affordable Energy | SDG 10, SDG 1 | V_socio, EP_rate, elderly_vuln, migration_score, fiscal_composite |
| R3 EU Taxonomy Alignment | **SDG 9** Infrastructure | SDG 13, SDG 12 | R_median, 6 components, R3-R7 modifiers, R5, R6a |
| R4 Energy Transition/DER | **SDG 7** Affordable Energy | SDG 13, SDG 9 | T1_score, DER_ratio, DER_variability, EV_load_ratio, solar/wind_mw |
| R5 Pollution & Corrosion | **SDG 11** Sustainable Cities | SDG 3, SDG 15 | corrosion_class, E2_enrichment, E2_local |
| R6 Cybersecurity Exposure | **SDG 9** Infrastructure | SDG 16 | R7_cyber, SCADA metrics, DESI/ENISA indices |

---

## Part II: Open-Source Data Sources by Country

For each of the 10 SSI Index countries, the tables below identify the specific open-source datasets required to fill the ESG gaps identified in the Cross-Country Gap Analysis. Sources are grouped by the ESG report they serve. All sources are free to access and license-compatible with open-source redistribution.

---

### Cross-Cutting Sources (All Countries)

These EU-wide and global datasets serve multiple countries and multiple ESG reports simultaneously.

| Source | URL | Data Provided | ESG Reports Served | License |
|---|---|---|---|---|
| **Copernicus CDS — ERA5** | cds.climate.copernicus.eu | Hourly climate reanalysis (1940–present), 31 km grid: temperature, wind, ice days, heat days | R1 Climate Physical Risk | CC-BY-4.0 |
| **Copernicus CDS — CMIP6** | cds.climate.copernicus.eu | SSP2-4.5 / SSP5-8.5 ensemble projections (50+ GCMs), IRI forward computation | R1 Climate Physical Risk | CC-BY-4.0 |
| **Eurostat** | ec.europa.eu/eurostat | Harmonised EU statistics: GDP, unemployment, demographics, energy poverty, energy prices | R2 Social Equity, R4 Transition | Open Government |
| **ENISA Cybersecurity Index** | enisa.europa.eu | National cyber maturity scoring (0–100), biennial | R6 Cybersecurity | Open Government |
| **EU DESI** | digital-strategy.ec.europa.eu/en/policies/desi | Digital competitiveness by country: connectivity, skills, digital public services | R6 Cybersecurity | Open Government |

**Status (March 2026):** CMIP6 SSP2-4.5 climate trajectories and ERA5 baselines have been ingested for all 10 countries via the SSI Data Enrichment Pipeline (`scripts/pipeline/`). IRI forward computation is now ACTIVE for all countries (I3_trajectory range 1.02–1.19). Reference data committed to `scripts/pipeline/data/cross-cutting/`.

---

### Austria (1,406 substations — 79 fields, richest schema)

**Current status:** PARTIAL across most reports. Report 4 (Transition) closest to READY.

| Gap to Fill | Source | URL | Specific Dataset | Format |
|---|---|---|---|---|
| Seismic PGA (currently DEFAULT) | GeoSphere Austria | data.hub.geosphere.at | ZAMG Earthquake Database, Austrian seismic hazard map | GeoJSON, CSV |
| Climate trajectory (R2) | Copernicus CDS | cds.climate.copernicus.eu | CMIP6 SSP2-4.5 for Alpine region | NetCDF |
| Markov 20yr projection calibration | — | — | Internal: recalibrate p_critical_20yr from existing Markov outputs | — |
| Elderly vulnerability, migration | Statistik Austria | statistik.at | Population by age group (Gemeinde level), internal migration flows | CSV, OGD API |
| Flood risk mapping | BMNT / eHYD | ehyd.gv.at | Flood risk zones (HQ30, HQ100, HQ300), hydrographic service | WMS, SHP |
| Corrosion environment | Umweltbundesamt | umweltbundesamt.at/opendata | Air quality monitoring (SO2, NOx, particulate), industrial emissions | CSV |

**Priority action:** Austria's schema is already the richest. Activating CMIP6 and recalibrating Markov 20yr would move 3 reports from PARTIAL to READY.

---

### Canada (24,986 substations — 39 fields, modifier-only)

**Current status:** GAP across most reports except R3 Taxonomy (READY).

| Gap to Fill | Source | URL | Specific Dataset | Format |
|---|---|---|---|---|
| Demographics, socio-economic | Statistics Canada | statcan.gc.ca | Census 2021 — dissemination area profiles (income, age, employment) | CSV, GeoJSON |
| Energy poverty | Statistics Canada | statcan.gc.ca | Survey of Household Energy Use (SHEU) | CSV |
| Seismic PGA | Earthquakes Canada (NRCan) | earthquakescanada.nrcan.gc.ca | National Building Code seismic hazard values (2020 model), PGA at 2% in 50 yr | CSV, SHP |
| Climate data (ERA5 or ECCC) | ECCC Climate | climate-change.canada.ca | Canadian Climate Normals (1991–2020), heat/ice day counts | CSV |
| Climate trajectory | Copernicus CDS | cds.climate.copernicus.eu | CMIP6 SSP2-4.5 for North America | NetCDF |
| Grid topology | NRCan / provincial ISOs | nrcan.gc.ca | Transmission line data (where published by IESO, AESO, BC Hydro) | varies |
| Markov calibration | — | — | Internal: deploy Markov model with CIGRE TB 761 calibration on Canadian fleet | — |
| DER / Transition | CER Open Data | open.canada.ca (CER) | Renewable capacity by province, EV registrations (StatCan Table 20-10-0024) | CSV |
| Corrosion environment | ECCC | weather.gc.ca | Air quality monitoring (NAPS network — SO2, PM2.5 near substations) | CSV |
| Flood risk | NRCan | open.canada.ca | National Flood Hazard Identification Mapping Program | SHP, GeoJSON |

**Priority action:** Canada has the most severe data poverty among standard-schema countries. Schema expansion to 61+ fields is prerequisite. Statistics Canada census data + NRCan seismic are the two highest-impact ingestions.

---

### France (7,898 substations — 61 fields)

**Current status:** Strong Markov. Socio-economic on DEFAULT. R1 PARTIAL, R2 GAP.

| Gap to Fill | Source | URL | Specific Dataset | Format |
|---|---|---|---|---|
| Socio-economic (GDP, unemployment — currently DEFAULT at 30,000 / 7.0) | INSEE | insee.fr | Données locales — PIB par département, taux de chômage par zone d'emploi | CSV, API |
| Energy poverty (V_socio — DEFAULT) | ADEME / ONPE | data.ademe.fr | Observatoire National de la Précarité Énergétique — LIHC rate by département | CSV |
| E2_local enrichment | ADEME | data.ademe.fr | DPE (Diagnostic de Performance Énergétique) — building energy class by commune | CSV |
| Climate trajectory (R2) | Copernicus CDS | cds.climate.copernicus.eu | CMIP6 SSP2-4.5, Météo-France DRIAS regional downscaling | NetCDF, CSV |
| Flood risk (S2) | Cerema / Vigicrues | cerema.fr, vigicrues.gouv.fr | Plan de Prévention du Risque Inondation (PPRi) — flood zone mapping | SHP, WMS |
| Elderly vulnerability | INSEE | insee.fr | Population par tranche d'âge par commune (RP 2021) | CSV |
| Migration score | INSEE | insee.fr | Migrations résidentielles — flux entrants/sortants par département | CSV |
| Corrosion (currently DEFAULT) | LCSQA / Prev'Air | prevair.org | Air quality monitoring (SO2, industrial emissions by commune) | CSV |
| DER detail | RTE éCO2mix / Enedis | rte-france.com/eco2mix, data.enedis.fr | Installed solar/wind by commune, injection points, EV charging points | CSV, API |

**Priority action:** INSEE socio-economic ingestion is the single highest-impact action for France. The data exists at commune level — it was identified in the Gap Audit Excel as available but not yet ingested. This alone moves R2 from GAP to PARTIAL and R4 towards READY.

---

### Germany (13,251 substations — 61 fields)

**Current status:** R5 (Pollution) READY. Graph topology DEFAULT.

| Gap to Fill | Source | URL | Specific Dataset | Format |
|---|---|---|---|---|
| Graph topology (degree = 10 DEFAULT everywhere) | BNetzA / MaStR | marktstammdatenregister.de | Grid connection points, Netzanschlusspunkte | CSV, API |
| Markov 20yr (p_critical = 1.0 DEFAULT) | — | — | Internal: recalibrate from existing risk_score distribution | — |
| EP_rate_region (energy poverty — DEFAULT) | Destatis | destatis.de | Mikrozensus — Energieausgaben nach Einkommen by Kreis | CSV |
| Climate trajectory (R2) | Copernicus CDS + DWD | opendata.dwd.de | CMIP6 + DWD regional climate projections (REMO, WETTREG) | NetCDF, CSV |
| Elderly vulnerability | Destatis | destatis.de | Bevölkerung nach Altersgruppen by Kreis | CSV |
| Migration score | Destatis | destatis.de | Wanderungen by Kreis (Zu-/Fortzüge) | CSV |
| Flood risk | BfG / LAWA | geoportal.de | Hochwassergefahrenkarten (HQ100), federal flood maps | WMS, SHP |

**Priority action:** Graph topology rebuild from MaStR data is the most impactful German-specific action. Germany's corrosion and socio-economic data are already strong — fixing topology and Markov calibration would push 3 reports toward READY.

---

### Italy (4,293 substations — 59 fields)

**Current status (updated March 2026):** ALL 6 ESG REPORTS READY. Pipeline enrichment completed: INGV MPS04 seismic overlay (Zone 1: 137, Zone 2: 687, Zone 3: 3,221, Zone 4: 248), CMIP6 climate trajectories active, ISTAT socio-economic for 97 provinces (3,807/4,293 matched). 4,050 classification upgrades from defaults.

| Gap to Fill | Source | URL | Specific Dataset | Format |
|---|---|---|---|---|
| Seismic PGA (currently DEFAULT 0.03 / zone 4 — CRITICAL for Italy) | INGV | ingv.it | Mappa di pericolosità sismica (MPS04) — PGA at 10% in 50 yr, 0.05° grid | CSV, SHP, GeoTIFF |
| Climate trajectory activation | Copernicus CDS | cds.climate.copernicus.eu | CMIP6 SSP2-4.5 — activate existing I1/I2/I3_trajectory schema fields | NetCDF |
| Corrosion detail | ISPRA | isprambiente.gov.it | Qualità dell'aria — SO2, PM10 monitoring by province | CSV |
| Elderly vulnerability | ISTAT | istat.it | Popolazione residente per età by comune (Census 2021) | CSV, API |
| Migration score | ISTAT | istat.it | Iscrizioni/cancellazioni anagrafiche — internal migration by comune | CSV |
| Flood risk | ISPRA | idrogeo.isprambiente.gov.it | IdroGEO — national landslide and flood risk platform | WMS, SHP, API |
| Energy poverty | ISTAT / ARERA | istat.it, arera.it | Indicatori povertà energetica, spesa energetica per decile di reddito | CSV |

**Completed:** INGV MPS04 seismic overlay (65,260 grid points, 0.05° resolution) — PGA range 0.035g–0.315g. CMIP6 SSP2-4.5 climate trajectories active. ISTAT provincial socio-economic overlay for all 97 provinces. **Remaining gaps:** Corrosion detail (ISPRA), flood risk (IdroGEO), migration score refinement.

---

### Japan (5,981 substations — 62 fields)

**Current status:** R2 Social Equity READY. Exceptional seismic data. Corrosion DEFAULT.

| Gap to Fill | Source | URL | Specific Dataset | Format |
|---|---|---|---|---|
| R6_seismic modifier (not computed despite having PGA) | — | — | Internal: compute R6b from existing pga_g values using formula construct | — |
| Corrosion class (DEFAULT) | Ministry of Environment | env.go.jp | Atmospheric corrosion monitoring (JIS Z 2381 exposure data) | CSV |
| Climate trajectory (R2) | Copernicus CDS + JMA | data.jma.go.jp | CMIP6 + JMA regional climate projections | NetCDF, CSV |
| Seismic zone granularity (only A/B) | J-SHIS (NIED) | j-shis.bosai.go.jp | National Seismic Hazard Maps — probabilistic hazard at 250m mesh | GeoJSON, CSV |
| Graph topology (is_bridge all False) | METI / OCCTO | occto.or.jp | Transmission grid topology data (Organization for Cross-regional Coordination) | CSV |
| Flood risk | MLIT | disaportal.gsi.go.jp | National Hazard Map Portal — flood, landslide, tsunami | WMS, GeoJSON |
| DER detail | METI | enecho.meti.go.jp | FIT (Feed-in Tariff) installation data by prefecture, EV registrations | CSV |

**Priority action:** Japan has the best foundation for Report 1 (exceptional seismic + socio-economic data). Computing R6_seismic from existing PGA and adding CMIP6 climate trajectory are low-effort, high-impact actions.

---

### Spain (3,529 substations — 61 fields)

**Current status:** Exceptional data variance. Closest to full R1 readiness among continental EU.

| Gap to Fill | Source | URL | Specific Dataset | Format |
|---|---|---|---|---|
| Seismic zone (categorical DEFAULT) | IGN | ign.es | Mapa de Peligrosidad Sísmica — PGA at 475-year return period | SHP, CSV |
| Corrosion class (DEFAULT) | MITECO | miteco.gob.es | Red de vigilancia atmosférica — SO2, industrial emissions by municipality | CSV |
| Climate trajectory (R2) | Copernicus CDS + AEMET | aemet.es | CMIP6 + AEMET AdapteCCa regional projections | NetCDF, CSV |
| DER sub-metrics | REE / CNMC | ree.es, cnmc.es | Installed RE capacity by node, EV charging infrastructure by province | CSV, API |
| Elderly vulnerability | INE | ine.es | Padrón — population by age group by municipality | CSV |
| Migration score | INE | ine.es | Estadística de Migraciones — internal flows by province | CSV |
| Flood risk | MITECO | sig.mapama.gob.es | SNCZI — Sistema Nacional de Cartografía de Zonas Inundables | WMS, SHP |

**Priority action:** Spain needs minimal work. CMIP6 activation + corrosion data from MITECO air quality network would make Spain the first continental EU country READY for Report 1. The municipality-level socio-economic data is already exceptional.

---

### Switzerland (947 substations — 61 fields)

**Current status:** Full socio-economic. R7_cyber is only GAP.

| Gap to Fill | Source | URL | Specific Dataset | Format |
|---|---|---|---|---|
| R7_cyber (DEFAULT — uniform values) | NCSC / DESI equivalent | ncsc.admin.ch | Swiss National Cyber Security Centre — maturity indicators | Reports (manual) |
| Continuity component C (only 2 unique values) | SFOE / Swissgrid | bfe.admin.ch, swissgrid.ch | Grid reliability statistics (SAIDI, SAIFI by canton) | CSV |
| Graph topology (degree DEFAULT = 2) | Swissgrid | swissgrid.ch | Transmission network topology (published grid maps) | SHP, PDF |
| Corrosion class (DEFAULT) | FOEN / BAFU | bafu.admin.ch | National Air Quality Monitoring Network (NABEL) — SO2, NOx | CSV |
| Climate trajectory (R2) | Copernicus CDS + MeteoSwiss | meteoswiss.admin.ch | CMIP6 + CH2018 Swiss Climate Scenarios | NetCDF, CSV |
| Elderly vulnerability | BFS | bfs.admin.ch | Ständige Wohnbevölkerung nach Alter by Gemeinde | CSV |
| Migration score | BFS | bfs.admin.ch | Wanderung — internal migration by canton | CSV |
| Flood risk | FOEN / BAFU | map.geo.admin.ch | Hochwassergefährdung — flood hazard maps (national coverage) | WMS, SHP |

**Priority action:** Switzerland's only GAP is R6 Cybersecurity. NCSC indicators + DESI re-computation would close this. The CH2018 climate scenarios from MeteoSwiss are among the best-resolved national climate projections in Europe — excellent for CMIP6 overlay.

---

### UK (3,150 substations — 58 fields)

**Current status:** Unique social data (elderly_pct, ep_rate). Schema naming inconsistencies.

| Gap to Fill | Source | URL | Specific Dataset | Format |
|---|---|---|---|---|
| V_socio, E2_local (missing standard fields) | ONS | ons.gov.uk | Census 2021 — Index of Multiple Deprivation (IMD), energy data by LSOA | CSV, API |
| Unemployment, R&D% (missing) | ONS / Nomis | nomisweb.co.uk | Annual Population Survey — employment by local authority | CSV |
| Climate trajectory (R2) | Copernicus CDS + Met Office | climatedataportal.metoffice.gov.uk | UKCP18 — UK Climate Projections (12km grid, probabilistic) | NetCDF, CSV |
| Transition detail (only der_capacity_mw, ev_density) | NESO / DESNZ | neso.energy, gov.uk | Renewable Energy Planning Database, EV charging by local authority | CSV |
| Corrosion class (DEFAULT) | Defra | uk-air.defra.gov.uk | UK Automatic Urban and Rural Network (AURN) — SO2, particulate | CSV |
| Schema harmonisation | — | — | Internal: rename ETTC_years→ettc_years, ep_rate→EP_rate_region, betweenness_centrality→BC_percentile, R6b_value→R6_seismic | — |
| Flood risk | Environment Agency | data.gov.uk | Flood Map for Planning — Risk of Flooding from Rivers and Sea | SHP, GeoJSON |
| Migration score | ONS | ons.gov.uk | Internal migration by local authority (annual estimates) | CSV |

**Priority action:** Schema harmonisation is the UK-specific prerequisite — field naming inconsistencies must be resolved before the ESG data layer can work cross-country. UKCP18 climate projections are world-class and would make the UK competitive for Report 1 readiness.

---

### US (45,003 substations — 10 fields, compact format)

**Current status:** GAP across all reports. Schema expansion required.

| Gap to Fill | Source | URL | Specific Dataset | Format |
|---|---|---|---|---|
| **Full schema expansion (10 → 61+ fields)** | — | — | Internal: restructure from compact array to nested JSON with all 9 data layers | — |
| Demographics, socio-economic | US Census Bureau | data.census.gov | American Community Survey (ACS) 5-year — income, age, poverty by tract | CSV, API |
| Energy poverty | EIA + Census | eia.gov | Residential Energy Consumption Survey (RECS), Low Income Home Energy Assistance | CSV |
| Seismic PGA | USGS | usgs.gov/programs/earthquake-hazards | National Seismic Hazard Model (2023 update) — PGA gridded data | GeoTIFF, CSV |
| Climate data (IRI base) | NOAA | ncei.noaa.gov | Climate Normals (1991–2020) — heat days, ice days, wind by station (9,800+) | CSV |
| Climate trajectory (R2) | Copernicus CDS | cds.climate.copernicus.eu | CMIP6 SSP2-4.5 for North America | NetCDF |
| Markov degradation | — | — | Internal: deploy 5-state Markov using CIGRE TB 761 + IEEE C57.91 on US fleet | — |
| Grid topology | EIA / HIFLD | hifld-geoplatform.opendata.arcgis.com | Homeland Infrastructure Foundation-Level Data — transmission lines, substations | SHP, GeoJSON |
| DER / Transition | EIA | eia.gov | Form EIA-860 (generators), Form EIA-861 (DER), EV registrations (AFDC) | CSV |
| Corrosion / Pollution | EPA | epa.gov/data | Air Quality System (AQS) — SO2, PM2.5 by county | CSV, API |
| Flood risk | FEMA | msc.fema.gov | National Flood Hazard Layer (NFHL) — flood zones by polygon | SHP, GeoJSON |
| Cybersecurity baseline | CISA | cisa.gov | Cross-Sector Cybersecurity Performance Goals (CPGs) | Manual assessment |

**Priority action:** The US requires a complete architecture rebuild. The recommended sequencing is: (1) schema expansion to nested JSON, (2) Census ACS overlay for socio-economic, (3) USGS NSHM for seismic, (4) NOAA for climate base, (5) Markov deployment, (6) EIA for transition, (7) CMIP6 for climate trajectory. Given the 45k substation scale, an automated geocoded overlay pipeline (matching substation lat/lon to Census tracts, USGS grid cells, NOAA stations) is necessary.

---

## Part III: Data Procurement Priority Matrix

Ranked by impact on ESG report readiness across all 10 countries.

| Priority | Data Source | Countries Affected | Reports Unlocked | Effort |
|---|---|---|---|---|
| **1** ~~DONE~~ | Copernicus CMIP6 (climate trajectory) | All 10 | R1 Climate Physical Risk — TCFD scenario analysis | ~~Medium~~ COMPLETED — all 10 countries enriched |
| **2** ~~PARTIAL~~ | National statistics (demographics, economics) | IT (done), CA/FR/UK (pending) | R2 Social Equity | IT: 97 provinces ingested. CA/US: CSV pending |
| **3** ~~DONE~~ | INGV seismic PGA for Italy | IT | R1 — real MPS04 overlay active | ~~Low~~ COMPLETED — 65,260 grid points |
| **4** | US schema expansion | US | All 6 reports | High (architecture rebuild for 45k substations) |
| **5** | National air quality for corrosion | All except DE, IT | R5 Pollution & Corrosion | Medium (per-country environmental agency data) |
| **6** | NRCan seismic for Canada | CA | R1 Climate Physical Risk | Low (NBCC hazard values are published) |
| **7** | DESI/ENISA cyber indices | CH, all EU | R6 Cybersecurity | Low (published indices, apply to R7 formula) |
| **8** | National DER registries | CA, UK, ES, JP | R4 Energy Transition | Medium (varies by country data quality) |
| **9** | Flood risk mapping | All 10 | R1, R2 (flood exposure enrichment) | Medium (WMS/SHP overlay per country) |
| **10** | Elderly/migration enrichment | All except UK (partial) | R2 Social Equity (depth) | Low (demographic data universally available) |

---

## Part IV: Licensing & Auditability Summary

All recommended data sources meet three criteria for auditable ESG reporting:

1. **Open access** — free to download, no commercial license required
2. **Institutional provenance** — sourced from national statistics offices, geological surveys, meteorological agencies, or EU institutions (not private vendors)
3. **Citable vintage** — each dataset has a publication date and version that can be referenced in ESG disclosures

This matters because ESG reports under CSRD/ESRS Article 29a require that data sources be disclosed and subject to limited assurance. Using only institutional open-source data ensures that any auditor can independently verify the inputs to every SSI ESG score.

---

*Analysis performed 17 March 2026 — Updated with SSI Data Enrichment Pipeline results (all 10 countries)*
*Companion to: SSI_ESG_Cross_Country_Gap_Analysis.md and SSI_Index_ESG_Reporting_Mapping.md*
