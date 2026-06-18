# v4.5 Direct National Agency Expansion Plan — All 39 SoT Countries

**Created**: 8 June 2026
**Status**: Pre-kickoff — build cards ready, execution begins after v4.0.2 closes
**Scope**: Populate `_NATIONAL_MET_FETCHERS` (climate) + `_NATIONAL_SEISMIC_FETCHERS` (seismic) registries with direct-from-national-agency connectors for all 39 SoT countries. Prioritised by substation count for execution sequencing.

---

## Build card schema

Each card lists for both classes:
- **Source agency + dataset**
- **Endpoint** (direct URL or API base)
- **Auth** requirement
- **Format** (REST API / NetCDF / GeoTIFF / shapefile / CSV)
- **Resolution** achieved
- **Complexity**: S (~4h) / M (~8h) / L (~12h) / XL (~16h+)
- **Citation / DOI** when available
- **Per-row provenance string** template

---

## Phase A1 — Highest-impact-per-hour (Week 1)

### 🇺🇸 us (45,003 substations · 34.4%)

**Climate** | Source: NOAA NCEI nClimGrid-Daily | Endpoint: `ncei.noaa.gov/products/land-based-station/nclimgrid-daily` | Auth: None | Format: NetCDF per-day | Resolution: 4 km (~0.04°) | Complexity: **M-L** | DOI: 10.25921/yfxd-z146 | Provenance: `"NOAA NCEI nClimGrid-Daily v1.0 (DOI: 10.25921/yfxd-z146), grid cell (lat, lon)"` | Notes: Download daily files 2018-2022 via THREDDS or HTTP; aggregate to per-cell heat_days/ice_days. ~1.8GB compressed. Use xarray.

**Seismic** | Source: USGS NSHM 2023 | Endpoint: `usgs.gov/programs/earthquake-hazards/science/2023-national-seismic-hazard-model` | Auth: None | Format: GeoTIFF raster (PGA 475-yr, Vs30=760 m/s) | Resolution: ~0.01° (~1 km) **fault-resolved** | Complexity: **L** | Citation: Petersen et al. 2024 | Provenance: `"USGS NSHM 2023 (Petersen et al. 2024), rock-site Vs30=760 m/s, PGA 475-yr"` | Notes: Mirror P15-B-2 rasterio code. ~500 MB raster — gitignore + operator one-time download. **20× finer than GEM 0.05°.**

### 🇯🇵 japan (5,981 substations · 4.6%)

**Climate** | Source: JMA AMeDAS | Endpoint: `data.jma.go.jp/obd/stats/etrn/index.php` | Auth: None (Japanese-language UI) | Format: CSV per station per year | Resolution: ~1 km in populated areas (~1300 stations nationally) | Complexity: **L** | Citation: JMA AMeDAS docs | Provenance: `"JMA AMeDAS station <station_id>, source agency: Japan Meteorological Agency"` | Notes: Japanese-language registration may be required for bulk download. Fallback to GHCN-D (which carries JMA-contributed station data).

**Seismic** | Source: NIED J-SHIS | Endpoint: `j-shis.bosai.go.jp/map/api/psha` | Auth: None (public REST API) | Format: JSON over REST | Resolution: ~1 km municipality mesh | Complexity: **M** | Citation: NIED J-SHIS PSHA | Provenance: `"NIED J-SHIS PSHA (2024 update), 1 km mesh code <MMMMNN>"` | Notes: ~38000 mesh cells nationally. **5× finer than GEM 0.05°.**

---

## Phase A2 — European cluster (Week 2)

### 🇩🇪 germany (13,251 substations · 10.1%)

**Climate** | Source: DWD CDC HYRAS-DE v5.0 | Endpoint: `opendata.dwd.de/climate_environment/CDC/grids_germany/daily/hyras_de/` | Auth: None | Format: NetCDF per year | Resolution: 5 km grid | Complexity: **M** | DOI: 10.5676/DWD/HYRAS_DE_v5 | Provenance: `"DWD CDC HYRAS-DE v5.0 (DOI: 10.5676/DWD/HYRAS_DE_v5), 5 km grid cell"` | Notes: Download `tasmax_hyras_5_<year>_v5-0_de.nc` for 2018-2022. Per-cell aggregation.

**Seismic** | Source: BGR D-A-CH 2018 (joint DE/AT/CH model) | Endpoint: `bgr.bund.de/.../D-A-CH_2018/` | Auth: None | Format: GeoTIFF raster | Resolution: ~0.1° | Complexity: **M** | Citation: Grünthal et al. 2018 | Provenance: `"BGR D-A-CH 2018 PSHA (Grünthal et al. 2018)"` | Notes: One-time ~50 MB download. **Same fetcher serves DE + AT + CH** (3 countries).

### 🇦🇹 austria (1,406 substations · 1.1%)

**Climate** | Source: GeoSphere Austria Data Hub | Endpoint: `data.hub.geosphere.at` | Auth: None | Format: NetCDF / CSV | Resolution: 1 km SPARTACUS gridded | Complexity: **M** | Citation: GeoSphere Austria SPARTACUS v2.1 | Provenance: `"GeoSphere Austria SPARTACUS v2.1, 1 km grid"` | Notes: SPARTACUS daily temperature gridded reanalysis since 1961.

**Seismic** | Source: BGR D-A-CH 2018 (shared with germany) | Same fetcher as germany | Auth: None | Notes: One fetcher = three countries. Use GeoSphere Austria's own ÖNORM B 4015 zonation as cross-check.

### 🇨🇭 switzerland (947 substations · 0.7%)

**Climate** | Source: MeteoSwiss IDAweb | Endpoint: `meteoswiss.admin.ch/services-and-publications/service/weather-and-climate-products/data-portal-for-research-and-teaching.html` | Auth: Free academic registration | Format: CSV per station | Resolution: ~80 stations distributed | Complexity: **M** | Citation: MeteoSwiss IDAweb | Provenance: `"MeteoSwiss IDAweb station <station_id>"`.

**Seismic** | Source: SED (Swiss Seismological Service) | Endpoint: `seismo.ethz.ch/en/knowledge/seismic-hazard/probabilistic-seismic-hazard-of-switzerland-2015/` | Auth: None | Format: GeoTIFF (SUIhaz2015) | Resolution: 0.05° | Complexity: **M** | Citation: Wiemer et al. 2016 SUIhaz2015 | Provenance: `"SED SUIhaz2015 (Wiemer et al. 2016)"` | Notes: BGR D-A-CH 2018 also covers Switzerland; pick SED for primary auditability.

### 🇫🇷 france (7,898 substations · 6.0%)

**Climate** | Source: Météo-France SAFRAN | Endpoint: `meteo.data.gouv.fr/datasets/climatologie-mensuelle-de-la-france` | Auth: data.gouv.fr account (free) | Format: CSV + NetCDF | Resolution: 8 km grid | Complexity: **M** | Citation: Vidal et al. 2010 | Provenance: `"Météo-France SAFRAN (Vidal et al. 2010), 8 km grid cell"`.

**Seismic** | Source: BRGM Plan Séisme | Endpoint: `planseisme.fr/Le-zonage-sismique-de-la-France.html` | Auth: None | Format: Shapefile (5 zones) + GMPE per zone | Resolution: Zone-based (regulatory) | Complexity: **S** | Citation: BRGM/Plan Séisme 2010 decree | Notes: ⚠️ Zone-based is coarser than GEM 0.05°. Operator decision: regulatory authority (BRGM as Tier 1a) or finer resolution (GEM as Tier 2). Build with BRGM as primary + GEM as fallback for finer resolution.

### 🇮🇹 italy (4,293 substations · 3.3%)

**Climate** | Source: ISPRA SCIA | Endpoint: `scia.isprambiente.it` | Auth: None | Format: CSV per station per year | Resolution: ~5 km in populated areas | Complexity: **M** | Citation: ISPRA SCIA platform | Provenance: `"ISPRA SCIA station <station_id>"`.

**Seismic** | ✅ **ALREADY POPULATED in v4.0.2** | `ingv_mps04_pga475.csv` via `_SEISMIC_LOCAL_PATHS['italy']` | INGV MPS04 | No v4.5 work needed.

### 🇪🇸 spain (3,529 substations · 2.7%)

**Climate** | Source: AEMET Open Data | Endpoint: `opendata.aemet.es` | Auth: Free API key | Format: JSON per station | Resolution: ~250 stations nationally | Complexity: **M** | Citation: AEMET Open Data Portal | Provenance: `"AEMET station <indicativo>"`.

**Seismic** | Source: IGN Norma de Construcción Sismorresistente NCSE-02 | Endpoint: `ign.es/web/ign/portal/sis-peligrosidad-sismica` | Auth: None | Format: PDF + shapefile zones | Resolution: Zone-based + interpolated grid | Complexity: **M** | Citation: NCSE-02 2002, updated 2012 | Provenance: `"IGN NCSE-02 PSHA (2012 update)"`.

### 🇬🇧 uk (3,150 substations · 2.4%)

**Climate** | Source: Met Office HadUK-Grid v1.3.0.0 | Endpoint: `data.ceda.ac.uk/badc/ukmo-hadobs/data/insitu/MOHC/HadOBS/HadUK-Grid/` | Auth: CEDA account (free) | Format: NetCDF | Resolution: 1 km grid | Complexity: **M** | DOI: 10.5285/4dc8450d889a491ebb20e724debe2dfb | Provenance: `"Met Office HadUK-Grid v1.3.0.0 (DOI: 10.5285/...), 1 km grid cell"`.

**Seismic** | Source: BGS national hazard map | Endpoint: `bgs.ac.uk/discoveringGeology/hazards/earthquakes/` | Auth: None | Format: GeoTIFF + zone shapefile | Resolution: 0.05° | Complexity: **M** | Citation: Musson 2010 (BGS UK hazard model) | Provenance: `"BGS UK Seismic Hazard Map (Musson 2010)"`.

### 🇵🇹 portugal (10,191 substations · 7.8%)

**Climate** | Source: IPMA Open Data | Endpoint: `ipma.pt/en/educativa/observar.tempo/index.jsp` | Auth: Free registration | Format: CSV per station | Resolution: ~150 stations | Complexity: **M** | Citation: IPMA Climate Bulletin | Provenance: `"IPMA station <id>"`.

**Seismic** | Source: LNEC RSAEEP 2018 + IPMA | Endpoint: `ipma.pt/en/geofisica/sismica/` | Auth: None | Format: Zone shapefile + GMPE | Resolution: Zone-based + interpolated | Complexity: **M** | Citation: RSAEEP-Portugal 2018 | Provenance: `"LNEC RSAEEP-Portugal 2018 PSHA"`.

### 🇮🇪 ireland (994 substations · 0.8%)

**Climate** | Source: Met Éireann Historical Data | Endpoint: `met.ie/climate/available-data/historical-data` | Auth: None | Format: CSV per station | Resolution: ~25 stations | Complexity: **S** | Citation: Met Éireann Climate Atlas | Provenance: `"Met Éireann station <id>"`.

**Seismic** | Source: DIAS INSN (Irish National Seismic Network) | Endpoint: `dias.ie/insn` | Auth: None | Format: PSHA report PDF + shapefile | Resolution: National PSHA model (sparse — low seismicity) | Complexity: **S-M** | Citation: ESHM20 Ireland subset | Provenance: `"DIAS INSN + ESHM20 Ireland PSHA"`.

### 🇧🇪 belgium (1,220 substations · 0.9%)

**Climate** | Source: RMI Open Data | Endpoint: `meteo.be/en/info/scientific-research/open-data` | Auth: None | Format: CSV per station | Resolution: ~25 stations | Complexity: **S** | Citation: RMI Climate Atlas | Provenance: `"RMI station <id>"`.

**Seismic** | Source: ROB-KSB (Royal Observatory of Belgium) | Endpoint: `seismologie.be/en/seismology/seismic-hazard` | Auth: None | Format: PSHA report + zone shapefile | Resolution: Zone-based | Complexity: **S-M** | Citation: Camelbeeck et al. 2014 Belgium PSHA | Provenance: `"ROB-KSB Belgium PSHA (Camelbeeck et al. 2014)"`.

### 🇳🇱 netherlands (1,640 substations · 1.3%)

**Climate** | Source: KNMI Daggegevens Open Data | Endpoint: `daggegevens.knmi.nl` | Auth: None | Format: CSV per station | Resolution: ~50 stations | Complexity: **S** | Citation: KNMI Climate Daily Data | Provenance: `"KNMI station <id>"`.

**Seismic** | Source: KNMI Seismology and Acoustics + induced-seismicity Groningen | Endpoint: `knmi.nl/kennis-en-datacentrum/uitleg/seismische-dreiging` | Auth: None | Format: GeoTIFF (Groningen-focused induced-seismicity PSHA) | Resolution: 1 km for Groningen, regional elsewhere | Complexity: **M** | Citation: Bommer et al. 2017 Groningen PSHA | Provenance: `"KNMI Groningen Induced PSHA (Bommer et al. 2017) + national tectonic PSHA"`.

### 🇸🇪 sweden (3,872 substations · 3.0%)

**Climate** | Source: SMHI Open Data | Endpoint: `opendata.smhi.se/apidocs/metobs/index.html` | Auth: None | Format: JSON per station REST | Resolution: ~700 stations nationally | Complexity: **M** | Citation: SMHI Open Data API | Provenance: `"SMHI station <id>"`.

**Seismic** | Source: SNSN (Swedish National Seismic Network, Uppsala University) | Endpoint: `snsn.geofys.uu.se` | Auth: None | Format: PSHA report + interpolated grid | Resolution: ~0.05° | Complexity: **M** | Citation: Sweden ESHM20 subset | Provenance: `"SNSN + ESHM20 Sweden PSHA"`.

### 🇫🇮 finland (4,022 substations · 3.1%)

**Climate** | Source: FMI Open Data | Endpoint: `en.ilmatieteenlaitos.fi/open-data` | Auth: Free API key | Format: WFS / JSON per station | Resolution: ~200 stations | Complexity: **M** | Citation: FMI Open Data | Provenance: `"FMI station <id>"`.

**Seismic** | Source: ISUH (Institute of Seismology, University of Helsinki) | Endpoint: `seismo.helsinki.fi` | Auth: None | Format: PSHA report + zone shapefile | Resolution: Zone-based (low seismicity) | Complexity: **S-M** | Citation: ISUH Finland PSHA | Provenance: `"ISUH + ESHM20 Finland PSHA"`.

### 🇩🇰 denmark (2,451 substations · 1.9%)

**Climate** | Source: DMI Open Data | Endpoint: `confluence.govcloud.dk/display/FDAPI/` | Auth: Free API key | Format: REST API + GRIB2 | Resolution: ~100 stations + 1km gridded climate | Complexity: **M** | Citation: DMI Open Data | Provenance: `"DMI station <id>"`.

**Seismic** | Source: GEUS (Geological Survey of Denmark and Greenland) | Endpoint: `geus.dk/products-services/research-portal` | Auth: None | Format: PSHA + shapefile (low seismicity) | Resolution: Zone-based | Complexity: **S** | Citation: GEUS + ESHM20 Denmark | Provenance: `"GEUS + ESHM20 Denmark PSHA"`.

### 🇳🇴 norway (6,495 substations · 5.0%)

**Climate** | Source: MET Norway senorge.no gridded products | Endpoint: `api.met.no/weatherapi` + `senorge.no` THREDDS | Auth: None (NLOD licence) | Format: NetCDF | Resolution: 1 km grid | Complexity: **M** | Citation: senorge.no documentation | Provenance: `"MET Norway senorge 1 km grid"`.

**Seismic** | Source: NORSAR + NGU | Endpoint: `norsar.no` | Auth: None | Format: PSHA report + shapefile | Resolution: ~0.05° via national PSHA | Complexity: **M** | Citation: NORSAR Norwegian National PSHA + ESHM20 subset | Provenance: `"NORSAR + NGU Norway PSHA + ESHM20 subset"`.

### 🇵🇱 poland (2,248 substations · 1.7%)

**Climate** | Source: IMGW Open Data | Endpoint: `dane.imgw.pl` | Auth: None | Format: CSV + REST API | Resolution: ~60 stations | Complexity: **M** | Citation: IMGW Open Data | Provenance: `"IMGW station <id>"`.

**Seismic** | Source: IGF-PAN (Institute of Geophysics, Polish Academy of Sciences) | Endpoint: `igf.edu.pl` | Auth: None | Format: PSHA report + shapefile | Resolution: Zone-based (mostly low; Sudetes + Carpathians higher) | Complexity: **M** | Citation: IGF-PAN + ESHM20 Poland | Provenance: `"IGF-PAN + ESHM20 Poland PSHA"`.

### 🇭🇺 hungary (3,502 substations · 2.7%)

**Climate** | Source: OMSZ Open Data | Endpoint: `met.hu/en/eghajlat/magyarorszag_eghajlata/eghajlati_adatsorok/` | Auth: Free registration | Format: CSV per station | Resolution: ~30 stations | Complexity: **M** | Citation: OMSZ Climate Atlas | Provenance: `"OMSZ station <id>"`.

**Seismic** | Source: MTA CSFK GGI (Geodetic and Geophysical Institute, Hungarian Academy) | Endpoint: `seismology.hu` | Auth: None | Format: PSHA + zone shapefile | Resolution: 0.1° via ESHM20 | Complexity: **M** | Citation: Tóth et al. 2019 + ESHM20 Hungary | Provenance: `"MTA CSFK GGI + ESHM20 Hungary PSHA (Tóth et al. 2019)"`.

### 🇨🇿 czechia (1,077 substations · 0.8%)

**Climate** | Source: CHMI Open Data | Endpoint: `chmi.cz/historicka-data/pocasi` | Auth: None | Format: CSV | Resolution: ~30 stations | Complexity: **M** | Citation: CHMI Historical Data | Provenance: `"CHMI station <id>"`.

**Seismic** | Source: IRSM CAS (Institute of Rock Structure and Mechanics) + IGT | Endpoint: `irsm.cas.cz` | Auth: None | Format: PSHA report + shapefile | Resolution: 0.05° via ESHM20 subset | Complexity: **M** | Citation: ESHM20 Czechia subset | Provenance: `"IRSM CAS + ESHM20 Czechia PSHA"`.

### 🇸🇰 slovakia (1,516 substations · 1.2%)

**Climate** | Source: SHMÚ Open Data | Endpoint: `shmu.sk/en/?page=1` | Auth: Registration required | Format: CSV per station | Resolution: ~30 stations | Complexity: **M** | Citation: SHMÚ Climate Atlas | Provenance: `"SHMÚ station <id>"`.

**Seismic** | Source: GFÚ SAV (Geophysical Institute, Slovak Academy of Sciences) | Endpoint: `seismology.sk` | Auth: None | Format: PSHA + zone shapefile | Resolution: 0.05° via ESHM20 | Complexity: **M** | Citation: GFÚ SAV + ESHM20 Slovakia | Provenance: `"GFÚ SAV + ESHM20 Slovakia PSHA"`.

### 🇸🇮 slovenia (158 substations · 0.1%)

**Climate** | Source: ARSO Vreme | Endpoint: `meteo.arso.gov.si/met/en/agromet/data/` | Auth: None | Format: CSV per station | Resolution: ~25 stations | Complexity: **S** | Citation: ARSO Climate Data | Provenance: `"ARSO station <id>"`.

**Seismic** | Source: ARSO Seismology Office | Endpoint: `arso.gov.si/potresi/` | Auth: None | Format: GeoTIFF + zone shapefile | Resolution: 0.05° (Slovenia is high-seismicity Alpine) | Complexity: **M** | Citation: Šket Motnikar et al. 2015 Slovenia PSHA | Provenance: `"ARSO Slovenia PSHA (Šket Motnikar et al. 2015)"`.

### 🇪🇪 estonia (614 substations · 0.5%)

**Climate** | Source: EMHI (Estonian Environment Agency) | Endpoint: `keskkonnaagentuur.ee` | Auth: None | Format: CSV per station | Resolution: ~20 stations | Complexity: **S** | Provenance: `"EMHI station <id>"`.

**Seismic** | Source: Tartu Observatory (Estonian seismic network) | Endpoint: `geoloogia.info/en` | Auth: None | Format: PSHA + ESHM20 subset (very low seismicity) | Resolution: Zone-based | Complexity: **S** | Provenance: `"Tartu Observatory + ESHM20 Estonia PSHA"`.

### 🇱🇻 latvia (1,219 substations · 0.9%)

**Climate** | Source: LVĢMC (Latvian Environment Agency) | Endpoint: `videscentrs.lvgmc.lv` | Auth: None | Format: CSV per station | Resolution: ~20 stations | Complexity: **S** | Provenance: `"LVĢMC station <id>"`.

**Seismic** | Source: LVĢMC Seismology | Endpoint: Same | Auth: None | Format: PSHA via ESHM20 (very low seismicity) | Resolution: Zone-based | Complexity: **S** | Provenance: `"LVĢMC + ESHM20 Latvia PSHA"`.

### 🇱🇹 lithuania (505 substations · 0.4%)

**Climate** | Source: LHMT (Lithuanian Hydrometeorological Service) | Endpoint: `meteo.lt` | Auth: None | Format: CSV per station | Resolution: ~20 stations | Complexity: **S** | Provenance: `"LHMT station <id>"`.

**Seismic** | Source: VU GMC (Vilnius University Geophysical Center) | Endpoint: `gmc.lt` | Auth: None | Format: PSHA via ESHM20 | Resolution: Zone-based | Complexity: **S** | Provenance: `"VU GMC + ESHM20 Lithuania PSHA"`.

### 🇱🇺 luxembourg (91 substations · 0.07%)

**Climate** | Source: MeteoLux Luxembourg Airport | Endpoint: `meteolux.lu` | Auth: None | Format: CSV per station | Resolution: ~3 stations | Complexity: **S** | Provenance: `"MeteoLux station <id>"`.

**Seismic** | Source: ECGS (European Center for Geodynamics and Seismology) | Endpoint: `ecgs.lu` | Auth: None | Format: PSHA via ESHM20 subset | Resolution: Zone-based (very low seismicity) | Complexity: **S** | Provenance: `"ECGS + ESHM20 Luxembourg PSHA"`.

### 🇮🇸 iceland (687 substations · 0.5%)

**Climate** | Source: IMO Veður (Icelandic Met Office) | Endpoint: `en.vedur.is/about-imo/projects/datasets/` | Auth: None | Format: CSV per station | Resolution: ~50 stations | Complexity: **S-M** | Provenance: `"IMO station <id>"`.

**Seismic** | Source: IMO Earthquake Monitoring + IMO SAGA PSHA | Endpoint: `en.vedur.is/earthquakes-and-volcanism/iceland/probabilistic-hazard/` | Auth: None | Format: GeoTIFF | Resolution: ~0.05° (high seismicity due to MAR + hotspot) | Complexity: **M** | Citation: Halldórsson et al. 2014 SAGA project | Provenance: `"IMO SAGA Iceland PSHA (Halldórsson et al. 2014)"`.

### 🇬🇷 greece (581 substations · 0.4%)

**Climate** | Source: HNMS (Hellenic National Meteorological Service) | Endpoint: `hnms.gr/emy/en/observation/met-data/observation-data` | Auth: Registration required | Format: CSV per station | Resolution: ~80 stations | Complexity: **M** | Citation: HNMS Climate Atlas | Provenance: `"HNMS station <id>"`.

**Seismic** | ✅ EAK 2003 ALREADY POPULATED in v4.0.2 — Optional upgrade to NEAK 2023 (new Greek Aseismic Code) | Endpoint: `oasp.gr/neak-2023/` | Auth: None | Format: GeoTIFF + zone shapefile | Resolution: 0.05° (high-seismicity Aegean) | Complexity: **M** | Citation: NEAK 2023 (Greek Earthquake Planning and Protection Organization) | Provenance: `"NEAK 2023 (OASP)"`.

### 🇨🇦 canada (24,986 substations · 19.1%)

**Climate** | Source: ECCC AHCCD + ANUSPLIN | Endpoint: `climate-change.canada.ca/climate-data/#/adjusted-station-data` | Auth: None | Format: CSV per station + 10 km NetCDF | Resolution: Station ~1-5km + 10km grid | Complexity: **M** | Citation: Vincent et al. 2020 AHCCD v4 | Provenance: `"ECCC AHCCD v4 (Vincent et al. 2020), station <id>"`.

**Seismic** | Source: NRCan 5th Generation Seismic Hazard Model | Endpoint: `earthquakescanada.nrcan.gc.ca/hazard-alea/zoning-zonage/index-en.php` | Auth: None | Format: GeoTIFF + NBC 2020 zoning tables | Resolution: ~0.05° (locally-calibrated) | Complexity: **M** | Citation: Halchuk et al. 2019 | Provenance: `"NRCan 5th Gen Seismic Hazard Model (Halchuk et al. 2019)"`.

### 🇦🇺 australia (8,500 substations · 6.5%)

**Climate** | Source: BOM AGCD (Australian Gridded Climate Dataset) | Endpoint: `bom.gov.au/climate/data-services/gridded-data.shtml` | Auth: None | Format: NetCDF per day | Resolution: 5 km grid | Complexity: **M** | Citation: BOM AGCD v1.0.1, Evans et al. 2020 | Provenance: `"BOM AGCD v1.0.1 (Evans et al. 2020), 5 km grid"`.

**Seismic** | Source: Geoscience Australia NSHA18 | Endpoint: `ga.gov.au/scientific-topics/earthquakes/.../nsha-2018` | Auth: None | Format: GeoTIFF raster | Resolution: ~0.05° | Complexity: **M** | Citation: Allen et al. 2020 NSHA18 | Provenance: `"Geoscience Australia NSHA18 (Allen et al. 2020)"`.

### 🇰🇷 korea (1,290 substations · 1.0%)

**Climate** | Source: KMA (Korea Meteorological Administration) Open Data | Endpoint: `data.kma.go.kr/cmmn/main.do` | Auth: Free API key | Format: REST API JSON | Resolution: ~100 stations | Complexity: **M** | Citation: KMA Climate Data | Provenance: `"KMA station <id>"`.

**Seismic** | Source: KMA Earthquake and Volcano Center | Endpoint: `necis.kma.go.kr` | Auth: None | Format: PSHA + zone shapefile | Resolution: ~0.05° | Complexity: **M** | Citation: KMA 2017 Korea PSHA | Provenance: `"KMA Earthquake and Volcano Center 2017 Korea PSHA"`.

### 🇹🇷 turkey (4,092 substations · 3.1%)

**Climate** | Source: MGM (Turkish State Meteorological Service) | Endpoint: `mgm.gov.tr/veridegerlendirme/` | Auth: Free registration | Format: CSV per station | Resolution: ~250 stations | Complexity: **M** | Citation: MGM Climate Bulletin | Provenance: `"MGM station <id>"`.

**Seismic** | Source: AFAD Türkiye Bina Deprem Yönetmeliği 2018 (TBDY-2018) | Endpoint: `tdth.afad.gov.tr` | Auth: None | Format: GeoTIFF + zone shapefile (high-seismicity Anatolia) | Resolution: ~0.05° | Complexity: **M** | Citation: AFAD TBDY-2018 | Provenance: `"AFAD TBDY-2018 Türkiye PSHA"`.

### 🇮🇱 israel (257 substations · 0.2%)

**Climate** | Source: IMS (Israel Meteorological Service) | Endpoint: `ims.gov.il/en` | Auth: Free registration | Format: CSV per station | Resolution: ~50 stations | Complexity: **M** | Citation: IMS Climate Data | Provenance: `"IMS station <id>"`.

**Seismic** | Source: GII (Geophysical Institute of Israel) | Endpoint: `seismograph.gii.co.il` | Auth: None | Format: PSHA + zone shapefile | Resolution: ~0.05° | Complexity: **M** | Citation: GII + GEM Middle East EMME PSHA | Provenance: `"GII + EMME 2014 Israel PSHA"`.

### 🇳🇿 new-zealand (1,558 substations · 1.2%)

**Climate** | Source: MetService + NIWA CliFlo | Endpoint: `cliflo.niwa.co.nz` | Auth: Free academic registration | Format: CSV per station | Resolution: ~600 stations nationally | Complexity: **M** | Citation: NIWA CliFlo | Provenance: `"NIWA CliFlo station <id>"`.

**Seismic** | Source: GNS Science GeoNet + EQC | Endpoint: `geonet.org.nz` | Auth: None | Format: GeoTIFF + zone shapefile (NZ NSHM 2022) | Resolution: ~0.05° | Complexity: **M** | Citation: Gerstenberger et al. 2024 NZ NSHM 2022 | Provenance: `"GNS Science NZ NSHM 2022 (Gerstenberger et al. 2024)"`.

### 🇨🇱 chile (1,095 substations · 0.8%)

**Climate** | Source: DMC (Dirección Meteorológica de Chile) | Endpoint: `meteochile.gob.cl/PortalDMC-web/index.xhtml` | Auth: Free registration | Format: CSV per station | Resolution: ~100 stations | Complexity: **M** | Citation: DMC Climate Atlas | Provenance: `"DMC station <id>"`.

**Seismic** | Source: CSN (Centro Sismológico Nacional, Universidad de Chile) | Endpoint: `csn.uchile.cl` | Auth: None | Format: PSHA + GeoTIFF (high-seismicity subduction) | Resolution: ~0.05° | Complexity: **M** | Citation: Núñez et al. 2018 Chile PSHA | Provenance: `"CSN Chile PSHA (Núñez et al. 2018)"`.

### 🇨🇴 colombia (381 substations · 0.3%)

**Climate** | Source: IDEAM (Instituto de Hidrología, Meteorología) | Endpoint: `dhime.ideam.gov.co` | Auth: Registration required | Format: CSV per station | Resolution: ~150 stations | Complexity: **M** | Citation: IDEAM Climate Bulletin | Provenance: `"IDEAM station <id>"`.

**Seismic** | Source: SGC (Servicio Geológico Colombiano) | Endpoint: `sgc.gov.co/Sismologia` | Auth: None | Format: PSHA + GeoTIFF (high-seismicity Andes) | Resolution: ~0.05° | Complexity: **M** | Citation: SGC 2018 National PSHA | Provenance: `"SGC Colombia National PSHA (2018)"`.

### 🇨🇷 costa-rica (169 substations · 0.1%)

**Climate** | Source: IMN (Instituto Meteorológico Nacional) | Endpoint: `imn.ac.cr` | Auth: None | Format: CSV per station | Resolution: ~60 stations | Complexity: **S-M** | Citation: IMN Climate Atlas | Provenance: `"IMN station <id>"`.

**Seismic** | Source: OVSICORI-UNA + RSN (Red Sismológica Nacional) | Endpoint: `rsn.ucr.ac.cr` | Auth: None | Format: PSHA + GeoTIFF (very high-seismicity Central America Trench) | Resolution: ~0.05° | Complexity: **M** | Citation: RSN 2017 Costa Rica PSHA | Provenance: `"OVSICORI-UNA + RSN Costa Rica PSHA"`.

### 🇲🇽 mexico (3,140 substations · 2.4%)

**Climate** | Source: SMN (Servicio Meteorológico Nacional) | Endpoint: `smn.cna.gob.mx/es/climatologia/informacion-climatologica` | Auth: None | Format: CSV per station | Resolution: ~200 stations | Complexity: **M** | Citation: SMN Climate Data | Provenance: `"SMN station <id>"`.

**Seismic** | ✅ CENAPRED ALREADY POPULATED in v4.0.2 | `cenapred_pga475.csv` | Optional upgrade to SSN Mexico National Seismic Hazard 2017 | Endpoint: `ssn.unam.mx/sismicidad/peligro/` | Citation: Bazzurro et al. 2017 Mexico National PSHA | Provenance: `"SSN Mexico National PSHA 2017"`.

### 🇬🇱 greenland (37 substations · 0.03%)

**Climate** | Source: DMI (Greenland stations operated by Danish Met) | Endpoint: `dmi.dk/groenland/` | Auth: API key (same as Denmark) | Format: REST + CSV per station | Resolution: ~30 stations | Complexity: **S** | Provenance: `"DMI Greenland station <id>"`.

**Seismic** | Source: DMI Seismology | Endpoint: Same | Auth: None | Format: PSHA (very low seismicity) via ESHM20 + GEM | Resolution: Zone-based | Complexity: **S** | Provenance: `"DMI + ESHM20 Greenland PSHA"`.

---

## Coverage summary

**All 39 SoT countries have detailed build cards** for both climate + seismic.

### Effort total by complexity tier

| Complexity | Climate | Seismic | Per-class hours |
|---|---|---|---|
| S (~4h) | 5 countries | 5 countries | 20-40h |
| M (~8h) | 27 countries | 28 countries | 224-440h |
| L (~12h) | 4 countries (US, JP, FR-data.gouv-auth) | 1 country (USGS NSHM raster) | 60-72h |
| XL (~16h+) | 0 | 0 | 0 |
| **Grand total** | **~304-552h climate** | **~284-512h seismic** | **~588-1064h total** |

### Realistic execution sequencing (operator capacity)

Assuming ~10h/week dedicated by operator:
- **Year 1 (52 weeks × 10h = 520h)**: Phases A1 + A2 + A3 (top-10 climate + seismic + most European clusters) = ~250h actual work + ~270h slack for code review, testing, doc updates, edge-case debugging.
- **Year 2**: Phase A4 (29 long-tail countries) at ~10-15h per country × 29 = ~290-450h.

Or with parallelisation across team (4 engineers × 10h/week = 40h/week):
- **Quarter 1**: Top-10 done
- **Quarter 2**: European long-tail (15 countries)
- **Quarter 3**: Americas + Oceania long-tail (10 countries)
- **Quarter 4**: Remaining + integration + acceptance gates

### Common code patterns enabling reuse

1. **GeoTIFF + bbox-clip** — already proven in P15-B-2 GEM 2023.1 path. Reuse pattern: USGS NSHM, BGR D-A-CH, AGCD, NSHA18, NRCan, NZ NSHM, AFAD, CSN, SGC, GII, IMO SAGA, ARSO Slovenia, KMA, SED.

2. **NetCDF + per-cell aggregation** — already proven in P15-A-3 ERA5-Land daily-statistics path. Reuse pattern: nClimGrid, HYRAS-DE, SAFRAN, AGCD, AHCCD/ANUSPLIN, senorge, HadUK-Grid, SPARTACUS, DMI grids.

3. **REST API + per-station JSON** — already proven in P15-F-2 socio path. Reuse pattern: SMHI, FMI, AEMET, KMA, IDEAM, IMS, MeteoSwiss, KNMI, RMI, ECCC stations, BOM stations, AMeDAS, NIED J-SHIS.

4. **CSV download** — simplest. Reuse pattern: ISPRA SCIA, AHCCD CSV, ARSO, EMHI, LVĢMC, LHMT, MeteoLux, DMC, IMN, SMN, OMSZ, SHMÚ, CHMI, IPMA, Met Éireann, IGN, MGM, etc.

**Net**: 4 reusable code patterns cover ALL 39 × 2 = 78 connectors. The per-country effort is mostly mapping the agency's endpoint conventions onto one of these patterns, not novel architecture.

---

## Per-connector implementation checklist (10 steps each)

1. [ ] Add fetcher function to `climate.py` or `seismic.py`
2. [ ] Register in `_NATIONAL_MET_FETCHERS` or `_NATIONAL_SEISMIC_FETCHERS`
3. [ ] Add canonical path entry if file-based
4. [ ] Update `_NATIONAL_*_AGENCY` dict with the exact agency name
5. [ ] Add unit test for the fetcher
6. [ ] Add parametrized test to `test_p15_ingestion_schemas.py`
7. [ ] Update `SOURCES_AND_LICENSES.md` per-country section
8. [ ] Update `ssi-metadata.js` for the country
9. [ ] Update `audit_climate_sanity.py` if climate
10. [ ] Commit + push

---

## Operational notes

- **DOI tracking**: every connector should pin the exact DOI version of the source dataset. Score-shift acceptance gate in v4.6+ should flag if the upstream releases a new major version.
- **Storage**: large rasters (USGS NSHM ~500 MB; possibly NRCan ~400 MB; BOM AGCD per-day ~10 GB total) need `.gitignore` treatment like GEM 2023.1. Add to ignore patterns.
- **Network**: from CI/CD environments, some agencies (DWD, JMA, MGM) may rate-limit. Add backoff + retry logic per connector. Set `User-Agent: SSI-Pipeline/4.5` to identify cleanly.
- **Auth secrets**: any API key needed (AEMET, KMA, FMI, data.gouv.fr, AEMET, MGM, hnms.gr) should go in `~/.<service>rc` per-operator dotfiles, not committed.
- **Backwards compatibility**: Tier 1b GHCN-D and Tier 2 GEM/ERA5-Land must always remain as documented fallbacks. Never delete them.
- **ESHM20 reuse**: ~12 European countries can share a single ESHM20 (European Seismic Hazard Model 2020) raster fetcher — substantial code reuse opportunity. Build once, register for all 12.
