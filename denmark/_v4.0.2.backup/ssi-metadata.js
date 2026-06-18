/*  SSI v4.0.2 — Metadata Registry · Denmark
    Loaded by every page in /denmark/.
    ──────────────────────────────────────────────
    Exports:  window.SSIMetadata   (structured, matches Denmark format exactly)
              window.SSI_METADATA  (legacy flat, backward-compat)              */

window.SSIMetadata = (function () {
  'use strict';
  return {

  /* ── Country metadata ── */
  country: "Denmark",
  code: "DK",
  prefix: "DK_",
  tso: "Energinet (state-owned, electricity + gas transmission)",
  regulator: "Forsyningstilsynet (Danish Energy Regulatory Authority)",
  statistics: "Danmarks Statistik",
  weather: "DMI (Danish Meteorological Institute)",
  geology: "GEUS (Geological Survey of Denmark and Greenland)",
  nuclear: "NONE (Denmark has zero nuclear power — strong political opposition)",
  admin: { level1: "Region", level2: "Kommune" },
  currency: { code: "DKK", symbol: "kr" },

  /* ── 30 verified data sources — Danish institutions ── */
  DATA_SOURCES: [
    { id:"ENT", name:"Energinet — Danish Transmission System Operator", url:"energinet.dk", freq:"Real-time", res:"Substation", vars:14, category:"Grid", feeds:"C1–C4, I2, S1–S2, transmission network topology, dispatch data, frequency regulation, bidding zones DK1/DK2" },
    { id:"FST", name:"Forsyningstilsynet (Danish Energy Regulatory Authority)", url:"forsyningstilsynet.dk", freq:"Quarterly", res:"DSO", vars:12, category:"Grid", feeds:"C1–C4, V1–V2, I1, reliability metrics SAIDI/SAIFI, technical standards, network quality, DSO performance" },
    { id:"DST", name:"Danmarks Statistik", url:"dst.dk", freq:"Annual", res:"Kommune", vars:10, category:"Socio-Econ", feeds:"C1–C4, safety compliance, demographics, income distribution, population served, regional data" },
    { id:"DMI", name:"DMI — Danish Meteorological Institute", url:"dmi.dk", freq:"Daily", res:"Station", vars:8, category:"Climate", feeds:"I3 (North Sea storm + coastal flooding stress), wind, precipitation, storm surge warnings, coastal hazard forecasts" },
    { id:"GEUS", name:"GEUS — Geological Survey of Denmark and Greenland", url:"geus.dk", freq:"Annual", res:"Grid 0.1°", vars:7, category:"Hazard", feeds:"I5 (North Sea storm + coastal flooding + subsidence hazard), geological data, soil mapping, clay/sand substrate analysis" },
    { id:"KYS", name:"Kystdirektoratet — Danish Coastal Authority", url:"kyst.dk", freq:"Annual", res:"Grid 0.1°", vars:6, category:"Hazard", feeds:"I7 (wind loading zone mapping + storm surge risk), coastal erosion data, sea level rise projections, storm impact zones" },
    { id:"CFCS", name:"Center for Cybersikkerhed — Danish Cybersecurity Centre", url:"cfcs.dk", freq:"Quarterly", res:"Infrastructure Site", vars:5, category:"Energy", feeds:"Digital security baseline, critical infrastructure protection, cyber-physical resilience for SCADA systems" },
    { id:"OSM", name:"OpenStreetMap — Power Infrastructure", url:"overpass-api.de", freq:"Continuous", res:"Node", vars:8, category:"Infrastructure", feeds:"I4 (graph degree), topology, ~2,451 substations mapped across 5 Regions, transmission + distribution networks" },
    { id: "CDS", name: "Copernicus CDS / ERA5-Land", url: "cds.climate.copernicus.eu", freq: "Annual", res: "0.1° (~11 km, ERA5-Land + daily-stats)", vars: 5, category: "Climate", feeds: "R2 Δ_climate (t_mean_c, heat_days, ice_days at 0.1° land grid)", registration: true },
    { id:"ENTSOE", name:"ENTSO-E Transparency Platform", url:"transparency.entsoe.eu", freq:"Hourly", res:"Substation", vars:2, category:"Grid", feeds:"C1 (capacity), cross-border flows with Germany/Sweden/Norway/UK, Nordic grid exchange, bidding zone flows" },
    { id:"EUROSTAT", name:"Eurostat — EU Statistics", url:"ec.europa.eu/eurostat", freq:"Annual", res:"Kommune", vars:3, category:"Socio-Econ", feeds:"E2 (population served), water-energy nexus, Nordic energy poverty indicators" },
    { id:"ENS", name:"Energistyrelsen — Danish Energy Agency", url:"ens.dk", freq:"Annual", res:"National", vars:3, category:"Transition", feeds:"Energy efficiency programs, RE transition support, wind data collection, grid flexibility initiatives" },
    { id:"VEJDIR", name:"Vejdirektoratet — Danish Transport Authority", url:"vejdirektoratet.dk", freq:"Quarterly", res:"Regional", vars:3, category:"Transport", feeds:"S3 (EV registrations), electric vehicle charging infrastructure density, regional accessibility" },
    { id:"NBANK", name:"Nationalbanken — Danish National Bank", url:"nationalbanken.dk", freq:"Quarterly", res:"Region", vars:4, category:"Economic", feeds:"E1–E3, economic cycles, business density, industrial concentration, wind energy economics" },
    { id:"DENG", name:"Dansk Energi — Danish Energy Association", url:"danskenergi.dk", freq:"Monthly", res:"Regional", vars:5, category:"Transition", feeds:"S1 (RE capacity), wind capacity by region, capacity factors, offshore wind corridor" },
    { id:"ENT_HYDRO", name:"Energinet — Hydrology & Water Resources", url:"energinet.dk", freq:"Quarterly", res:"Catchment", vars:4, category:"Hazard", feeds:"I5 (district heating + CHP coupling, water level monitoring), spring flow, coastal flooding hazard" },
    { id:"DISTRIBUTOR", name:"Distribution Companies (RADIUS, N1, Cerius, NOE, KONSTANT, Energi Fyn, ~40 DSOs)", url:"", freq:"Annual", res:"Distribution Company", vars:4, category:"Grid", feeds:"S1 variant (district heating plant dispatch), CAPEX, SAIDI/SAIFI, transformer inventories, restoration metrics" },
    { id:"MILJOE", name:"Miljøstyrelsen — Danish Environment Agency", url:"mst.dk", freq:"Annual", res:"Kommune", vars:3, category:"Environment", feeds:"I6 (environmental exposure + coastal hazard), pollution data, industrial sites, coastal protection zones" },
    { id:"KLIM_CENTRE", name:"Danish Climate Service Centre", url:"klimaportalen.dk", freq:"Annual", res:"Regional", vars:4, category:"Environment", feeds:"I5 (North Sea storm + coastal flooding + subsidence hazard mapping), climate adaptation data, extreme weather risk" },
    { id:"WORLDBANK", name:"World Bank / OECD", url:"", freq:"Annual", res:"National", vars:4, category:"Socio-Econ", feeds:"International benchmarks, Nordic socio-economic indicators, renewable energy transition comparisons" },
    { id:"SOLARGIS", name:"SolarGIS — Global Solar Atlas", url:"globalsolaratlas.info", freq:"Static", res:"Global", vars:2, category:"Transition", feeds:"T1 (solar resource mapping), solar irradiance (GHI, DNI) for southern Denmark" },
    { id:"NORD_POOL", name:"Nord Pool — Nordic Energy Exchange", url:"nordpoolgroup.com", freq:"Hourly", res:"Bidding Zone", vars:4, category:"Market", feeds:"E1 (electricity pricing), bidding zone DK1/DK2 price signals, cross-border flows" },
    { id:"GEOD", name:"Geodatastyrelsen — Danish Geodata Agency", url:"geodata.dk", freq:"Annual", res:"Regional", vars:3, category:"Infrastructure", feeds:"Geospatial grid topology, topographic hazard data, coastal bathymetry, subsidence monitoring" },
    { id:"ENT_SITRAP", name:"Energinet — Systemtilstand (Power Situation Reports)", url:"energinet.dk", freq:"Weekly", res:"National", vars:3, category:"Grid", feeds:"Real-time power balance, wind generation forecasts, offshore wind status" },
    { id:"DISTRICTCPH", name:"Dansk Fjernvarme — Danish District Heating Association", url:"danskfjernvarme.dk", freq:"Quarterly", res:"Region", vars:3, category:"Energy", feeds:"District heating dispatch, CHP plant status, storage readiness, thermal load forecasts" },
    { id:"DTU_WIND", name:"DTU Wind and Energy Systems", url:"wind.dtu.dk", freq:"Annual", res:"Regional", vars:2, category:"Environment", feeds:"North Sea wind dynamics, offshore wind farm impact studies, marine ecosystem stress indicators, power infrastructure exposure" },
    { id:"DTU_ELEC", name:"DTU Electrical Engineering — Power Systems", url:"elektro.dtu.dk", freq:"Annual", res:"Regional", vars:3, category:"Transition", feeds:"Grid stability research, microgrid capability, demand-side flexibility, storage readiness, power-to-X integration" },
    { id:"DMI_HIST", name:"DMI / Historical Archive", url:"dmi.dk", freq:"Monthly", res:"Station", vars:3, category:"Climate", feeds:"Historical North Sea storm severity index, coastal flooding records, wind patterns, storm surge events" },
    { id:"ENTSOE_TSOS", name:"ENTSO-E TSO Interconnects (Energinet)", url:"entsoe.eu", freq:"Continuous", res:"Border Point", vars:2, category:"Grid", feeds:"HVDC flows: Great Belt-Sweden, Øresund (DK-SE), DK1-DK2 synchronous boundary, cross-border capacity" },
    { id: "GEM", name: "GEM Global Seismic Hazard Map 2023.1", url: "globalquakemodel.org", freq: "Static", res: "0.05° (~5.5 km, rock-site PGA 475-yr)", vars: 1, category: "Hazard", feeds: "R6a seismic PGA, substation-level overlay (CC BY-NC-SA 4.0)" },
    { id: "Eurostat-NUTS3", name: "Eurostat NUTS-3 Regional Statistics", url: "ec.europa.eu/eurostat", freq: "Annual", res: "NUTS-3 (province / NUTS-2 unemployment)", vars: 5, category: "Socio-Econ", feeds: "R2 GDP/cap, unemp, elderly%, ep_rate, migration (CC BY 4.0)" },
  ],

  /* ── 6 components · 20 metrics ── */
  COMPONENTS: [
    {
      id:"C", name:"Continuity", weight:0.30, color:"#941914",
      desc:"Measures reliability and outage exposure — how often and how long power interruptions occur, accounting for North Sea storm conditions and coastal hazards.",
      metrics:[
        { id:"C1", name:"Outage Duration (SAIDI)", intra:0.35, global:0.105, norm:"A (P5/P95)", source:"Energinet / Forsyningstilsynet", desc:"Total annual interruption duration per customer", inverted:false, adaptive:false, isNew:false },
        { id:"C2", name:"Outage Frequency (SAIFI)", intra:0.30, global:0.090, norm:"A (P5/P95)", source:"Energinet / Forsyningstilsynet", desc:"Number of sustained interruptions per customer per year", inverted:false, adaptive:false, isNew:false },
        { id:"C3", name:"Restoration Time (CAIDI)", intra:0.20, global:0.060, norm:"A (P5/P95)", source:"Forsyningstilsynet / DSO", desc:"Average duration of each interruption (North Sea storm recovery time critical)", inverted:false, adaptive:false, isNew:false },
        { id:"C4", name:"Momentary Interruptions (MAIFI)", intra:0.15, global:0.045, norm:"A (P5/P95)", source:"Energinet", desc:"Momentary average interruption frequency index", inverted:false, adaptive:false, isNew:false }
      ]
    },
    {
      id:"V", name:"Voltage Quality", weight:0.10, color:"#aa4234",
      desc:"Captures voltage stability, power factor, and harmonic distortion at the distribution level.",
      metrics:[
        { id:"V1", name:"Voltage Deviation (ΔV)", intra:0.40, global:0.040, norm:"A (P5/P95)", source:"Forsyningstilsynet / DSO", desc:"Percentage deviation from nominal voltage", inverted:false, adaptive:false, isNew:false },
        { id:"V2", name:"THD (Harmonic Distortion)", intra:0.30, global:0.030, norm:"A (P5/P95)", source:"Forsyningstilsynet", desc:"Total harmonic distortion percentage", inverted:false, adaptive:false, isNew:false },
        { id:"V3", name:"Power Factor", intra:0.30, global:0.030, norm:"B (inverse)", source:"Forsyningstilsynet / DSO", desc:"Ratio of real to apparent power — higher is better", inverted:true, adaptive:false, isNew:false }
      ]
    },
    {
      id:"I", name:"Infrastructure", weight:0.25, color:"#5d8563",
      desc:"Assesses physical asset condition, age, capacity, and Denmark-specific hazards: North Sea storms, coastal flooding, subsidence, wind loading (critical for Danish terrain).",
      metrics:[
        { id:"I1", name:"Asset Age Index", intra:0.12, global:0.030, norm:"A (P5/P95)", source:"Forsyningstilsynet / Danmarks Statistik", desc:"Fleet-normalised average asset age", inverted:false, adaptive:false, isNew:false },
        { id:"I2", name:"Capacity Utilisation", intra:0.12, global:0.030, norm:"A (P5/P95)", source:"Energinet / Forsyningstilsynet", desc:"Percentage of rated capacity in use", inverted:false, adaptive:false, isNew:false },
        { id:"I3", name:"Climate IRI (North Sea Storm + Coastal Flooding Stress)", intra:0.12, global:0.030, norm:"A (P5/P95)", source:"DMI / Kystdirektoratet / ERA5", desc:"Infrastructure Risk Index based on North Sea storms, storm surge risk, coastal flooding hazard, and subsidence", inverted:false, adaptive:true, isNew:false },
        { id:"I4", name:"Graph Degree (Topology)", intra:0.12, global:0.030, norm:"B (inverse)", source:"OSM / Energinet", desc:"Number of connections — higher degree = more redundancy", inverted:true, adaptive:false, isNew:false },
        { id:"I5", name:"North Sea Storm + Storm Surge + Coastal Flooding Hazard", intra:0.18, global:0.045, norm:"A (P5/P95)", source:"DMI / Kystdirektoratet / GEUS / Energinet Hydrology", desc:"Combined North Sea storm severity + storm surge risk + subsidence + spring flood hazard (critical for Denmark)", inverted:false, adaptive:false, isNew:false },
        { id:"I6", name:"Corrosion Class (Coastal)", intra:0.10, global:0.025, norm:"D (categorical)", source:"ISO9223 / DMI", desc:"Environmental corrosion exposure adapted for North Sea salt spray: west coast C4, east coast C3, interior C2/C1", inverted:false, adaptive:false, isNew:false, categorical:true },
        { id:"I7", name:"Wind Loading Zone", intra:0.12, global:0.030, norm:"D (categorical)", source:"Kystdirektoratet / GEUS / DMI", desc:"Wind loading hazard mapping for overhead transmission lines (wind exposure critical in Danish coastal regions)", inverted:false, adaptive:true, isNew:false, categorical:true },
        { id:"I8", name:"N-1 Compliance", intra:0.05, global:0.0125, norm:"C (binary)", source:"Energinet", desc:"Whether substation meets N-1 redundancy standard (Energinet transmission backbone)", inverted:true, adaptive:false, isNew:false },
        { id:"I9", name:"Offshore Wind Concentration Risk", intra:0.07, global:0.0175, norm:"D (categorical)", source:"Energistyrelsen / Energinet", desc:"Concentration risk for substations supplying or dependent on major offshore wind farms (~50% of Danish generation)", inverted:false, adaptive:false, isNew:true, categorical:true }
      ]
    },
    {
      id:"E", name:"Economic", weight:0.10, color:"#3b9eff",
      desc:"Links grid risk to regional economic exposure — energy pricing, employment, and wind energy-driven economic cycles.",
      metrics:[
        { id:"E1", name:"Energy Price Index + Wind Cycle", intra:0.40, global:0.040, norm:"A (P5/P95)", source:"Nationalbanken / Nord Pool / Energinet", desc:"Wholesale + retail electricity cost per MWh, modulated by wind availability and offshore wind curtailment", inverted:false, adaptive:true, isNew:false },
        { id:"E2", name:"Population Served + Urban Concentration", intra:0.30, global:0.030, norm:"A (P5/P95)", source:"Danmarks Statistik / Eurostat", desc:"Kommune-level population served, with penalty for Copenhagen urban heat island and high population density", inverted:false, adaptive:false, isNew:false },
        { id:"E3", name:"Business Density + Industrial Concentration", intra:0.30, global:0.030, norm:"A (P5/P95)", source:"Energinet / Danmarks Statistik / Energistyrelsen", desc:"Economic activity clusters and large industrial load concentration (district heating, data centres, food processing)", inverted:false, adaptive:false, isNew:false }
      ]
    },
    {
      id:"S", name:"Saturation", weight:0.20, color:"#b88f3e",
      desc:"Quantifies DER/RE penetration stress, wind variability, reverse power flow risk, and EV charging load on the grid.",
      metrics:[
        { id:"S1", name:"Renewable Energy Capacity Ratio", intra:0.35, global:0.070, norm:"A (P5/P95)", source:"Dansk Energi / Energinet / Energistyrelsen", desc:"Total installed RE (wind/solar) capacity relative to substation rating (~50% wind baseline + offshore growth)", inverted:false, adaptive:false, isNew:false },
        { id:"S2", name:"RE Stress Index (Wind Variability + Offshore Curtailment)", intra:0.35, global:0.070, norm:"A (P5/P95)", source:"Dansk Energi / Energinet", desc:"Composite stress: RE penetration × wind variability × offshore output variability × transmission constraints (west coast wind dominance)", inverted:false, adaptive:true, isNew:false },
        { id:"S3", name:"EV Penetration Rate (Emerging)", intra:0.30, global:0.060, norm:"A (P5/P95)", source:"Vejdirektoratet / Transport Ministry", desc:"EV registrations as percentage of total fleet in catchment area (growing penetration in urban areas Copenhagen/Aarhus)", inverted:false, adaptive:false, isNew:true }
      ]
    },
    {
      id:"T", name:"Energy Transition", weight:0.05, color:"#0e7490", isNew:true,
      desc:"Measures clean energy transition pace and grid readiness for decarbonisation (RE targets: 100% by 2050, wind + power-to-X priority).",
      metrics:[
        { id:"T1", name:"Renewable Energy Share (%)", intra:0.50, global:0.025, norm:"B (inverse)", source:"Dansk Energi / Energinet / Energistyrelsen", desc:"Share of generation from renewables — higher share = lower risk (inverted, ~50% wind baseline + offshore + solar growth)", inverted:true, adaptive:false, isNew:false },
        { id:"T2", name:"Transition Readiness Score", intra:0.50, global:0.025, norm:"A (P5/P95)", source:"Energinet / Dansk Energi / Energistyrelsen", desc:"Composite readiness: grid flexibility + battery storage + DSO interconnection capacity + offshore wind integration + power-to-X readiness", inverted:true, adaptive:false, isNew:true }
      ]
    }
  ],

  /* ── 7 modifiers (R2–R7, incl. R6a + R6b North Sea storm/storm surge/wind loading) ── */
  MODIFIERS: [
    { id:"R2", name:"Adaptive Climate IRI + North Sea Storm Hazard Trajectory", range:"Weight redistribution", type:"Weight modifier", desc:"Uses CMIP6 SSP2-4.5 projections to adjust IRI metrics for North Sea storm risk, coastal flooding, subsidence, and wind exposure. When local storm/flooding risk is elevated, weight shifts to structural metrics. Incorporates DMI forecasts and Kystdirektoratet hazard mapping.", formula:"IRI_forward(m,s) = IRI_current(m,s) × (1 + 0.15 × clip(Δ_climate, −0.50, +1.00))", sources:["DMI","Kystdirektoratet","COPERNICUS ERA5","GEUS"], isEnhanced:true },
    { id:"R3", name:"Consequence + Island Isolation + Population Density", range:"[0.70, 1.35]", type:"Multiplicative", desc:"Amplifies risk for communities with high population density, island isolation (Bornholm), or Copenhagen urban concentration. Includes vulnerability indices (Danmarks Statistik demographics), coastal urban exposure, and isolation metrics.", formula:"C_mult = sigmoid(pop_weight × island_weight × V_socio × urban_factor)", sources:["Danmarks Statistik","EUROSTAT","Vejdirektoratet"], isEnhanced:true },
    { id:"R4", name:"Graph Criticality + Network Constraint", range:"[0.80, 1.40]", type:"Multiplicative", desc:"Penalises topological bottlenecks in Energinet transmission backbone and DSO networks: high betweenness centrality, bridge nodes, low degree. Built from OSM power graph and Energinet transmission constraints, with special attention to Great Belt and Øresund single-point-of-failure corridors.", formula:"F_topo = f(degree, BC_percentile, is_bridge, great_belt_exposure, øresund_tier)", sources:["OSM","Energinet"], isEnhanced:true },
    { id:"R6a", name:"Restoration Speed (North Sea Storm + Coastal Flooding Focus)", range:"[0.90, 1.10]", type:"Multiplicative", desc:"Forsyningstilsynet-CAIDI-based: rewards fast-restoring areas, penalises slow ones in coastal/island regions. Two substations with identical SAIDI can have different risk profiles based on restoration speed in areas affected by North Sea storms or coastal flooding.", formula:"R6a = sigmoid_bounded(CAIDI_local / CAIDI_fleet_median)", sources:["Forsyningstilsynet","Energinet"], isEnhanced:true },
    { id:"R6b", name:"North Sea Storm + Storm Surge + Wind Loading Overlay (CRITICAL FOR DENMARK)", range:"[1.00, 1.25]", type:"Multiplicative", desc:"DMI North Sea storm hazard + Kystdirektoratet storm surge risk + wind loading overlay. Penalises substations in high-storm zones, coastal flooding corridors, or high wind-loading regions. Integration of real-time DMI warnings and historical storm impacts. North Sea storms are a major Danish grid threat.", formula:"R6b = f(DMI_storm_percentile, KYS_surge_zone, GEUS_wind_loading, coastal_flood_proximity)", sources:["DMI","Kystdirektoratet","GEUS","Energinet Hydrology"], isEnhanced:true },
    { id:"R7", name:"Digital Readiness + Cyber-Physical Resilience", range:"[0.99, 1.05]", type:"Multiplicative", desc:"Cyber-physical security baseline, SCADA maturity proxy (Denmark high), and microgrid/islanding capability. Indicates digital resilience capability at the grid edge for North Sea storm recovery scenarios and coastal infrastructure security.", formula:"Cyber = f(SCADA_maturity, microgrid_pct, islanding_capability, coastal_security_baseline)", sources:["Energinet","Forsyningstilsynet","Center for Cybersikkerhed"], isEnhanced:false }
  ],

  /* ── processing pipeline ── */
  PIPELINE: [
    { step:1, name:"Ingest", desc:"95 variables from 30 verified Danish public data sources — Energinet, Forsyningstilsynet, Danmarks Statistik, DMI, GEUS, Kystdirektoratet, Center for Cybersikkerhed, and others. Zero proprietary SCADA dependencies. Maximum ingestion frequency: real-time (Energinet dispatch data).", icon:"📥" },
    { step:2, name:"Normalise", desc:"Four normalisation methods: Method A (robust fleet percentile P5/P95), Method B (inverse fleet percentile for density), Method C (binary compliance), and Method D (categorical mapping). Inverted metrics for density measures where higher = better resilience.", icon:"📐" },
    { step:3, name:"Weight", desc:"6-level hierarchical weighting across 6 components and 20 metrics. Continuity dominates at 0.30, Infrastructure at 0.25 (with higher North Sea storm/coastal flooding I5 weight), Saturation at 0.20. Weight budget validated by Sobol sensitivity analysis.", icon:"⚖️" },
    { step:4, name:"Compose R_base", desc:"Weighted sum of 6 normalised component scores produces the base resilience score.", icon:"🧮" },
    { step:5, name:"Modify", desc:"Seven multiplicative modifiers adjust R_base for Danish context: R2 (adaptive climate + North Sea storm hazard trajectory), R3 (consequence + island isolation + population density + Copenhagen concentration), R4 (graph criticality + Energinet/DSO constraints + Great Belt/Øresund bottlenecks), R6a (restoration speed in coastal/island areas), R6b (North Sea storm/storm surge/wind loading overlay — CRITICAL), R7 (digital readiness). Plus enrichments for vulnerable populations, coastal zones, and critical offshore wind infrastructure.", icon:"🔧" },
    { step:6, name:"Monte Carlo", desc:"10,000 iterations per substation using a 20×20 Gaussian copula correlation matrix. Captures measurement, spatial, staleness, and model uncertainty. Produces median, P5, P95, skewness, and P_critical for each substation.", icon:"🎲" },
    { step:7, name:"Classify", desc:"Four bands: Low (0.00–0.25), Medium (0.25–0.50), High (0.50–0.75), Critical (0.75–1.00). Alert flags trigger when any single component exceeds its P95 fleet threshold. North Sea storm/coastal flooding/wind events escalate classification instantaneously.", icon:"🏷️" }
  ],

  /* ── classification bands ── */
  CLASSIFICATION: [
    { name:"Low",      range:"0.00 – 0.25", meaning:"Good resilience — stable grid, low exposure",       expected:"~35–40%", color:"#5d8563" },
    { name:"Medium",   range:"0.25 – 0.50", meaning:"Moderate risk — some vulnerabilities present",       expected:"~32–38%", color:"#b88f3e" },
    { name:"High",     range:"0.50 – 0.75", meaning:"Elevated risk — investment priority zone",           expected:"~18–23%", color:"#aa4234" },
    { name:"Critical", range:"0.75 – 1.00", meaning:"Severe vulnerability — urgent intervention required", expected:"~5–10%",   color:"#941914" }
  ],

  /* ── master equation ── */
  MASTER_EQUATION: "R_final = soft_clip_upper( R_base × F_topo × C_mult × R6a_mult × R6b_north_sea_storm_surge_wind × Cyber_factor )",

  /* ── normalisation methods ── */
  NORM_METHODS: [
    { id:"A", name:"Fleet Percentile (robust)", formula:"N(x) = soft_clip((x − P₅) / (P₉₅ − P₅))", applies:"C1, C2, C3, C4, V1, V2, I1, I2, I3, I5, E1, E2, E3, S1, S2, S3" },
    { id:"B", name:"Fleet Percentile (inverse)", formula:"N(x) = 1 − soft_clip((x − P₅) / (P₉₅ − P₅))", applies:"V3, I4, T1, T2" },
    { id:"C", name:"Binary (bounded)", formula:"N(x) = 0 if compliant, 1 if non-compliant", applies:"I8 (N-1 compliance)" },
    { id:"D", name:"Categorical Mapping", formula:"N(x) = lookup_table(class → [0, 1])", applies:"I6 (coastal corrosion), I7 (wind loading), I9 (offshore wind concentration)" }
  ],

  /* ── 11 data layers · 95 variables ── */
  DATA_LAYERS: [
    { id:"A",   name:"SSI v4.0.2 Resilience (Denmark)",                 vars:20, status:"LIVE",    sources:"Energinet · Forsyningstilsynet · Danmarks Statistik · DMI · Kystdirektoratet · GEUS" },
    { id:"B.1", name:"Grid Telemetry: Open",                       vars:3,  status:"LIVE",    sources:"DMI / ERA5 · Energinet" },
    { id:"B.2", name:"Grid Telemetry: Proxy",                      vars:4,  status:"LIVE",    sources:"IEEE C57.91 · DSO · Forsyningstilsynet" },
    { id:"B.3", name:"Grid Telemetry: Fuzzy",                      vars:12, status:"FUZZY",   sources:"IEEE/CIGRÉ standards · GEUS" },
    { id:"C",   name:"Socio-Economic + Nordic Demographics",        vars:10, status:"LIVE",    sources:"Danmarks Statistik · EUROSTAT · Nationalbanken · Energistyrelsen" },
    { id:"D",   name:"Environmental Hazards (North Sea Storm+Coastal Flooding+Subsidence)",vars:8,  status:"LIVE",    sources:"DMI · Kystdirektoratet · GEUS · Copernicus · Energinet Hydrology" },
    { id:"E",   name:"Danish Open Data + Energy Policy",            vars:9,  status:"LIVE",    sources:"Energinet · Dansk Energi · Energistyrelsen · Geodatastyrelsen" },
    { id:"F",   name:"Network Transitions + Wind Baseload",         vars:12, status:"BAYESIAN",sources:"DSO history OR IEEE/CIGRÉ + priors" },
    { id:"G",   name:"Modifier Inputs (North Sea Storm/Wind-Weighted)",vars:4,  status:"LIVE",    sources:"Energinet reliability · DMI · OSM" },
    { id:"H",   name:"Network & Topology (Energinet Transmission)",  vars:7,  status:"LIVE",    sources:"Energinet · ENTSO-E · OSM" },
    { id:"I",   name:"Output Scores + Alert Flags",                 vars:7,  status:"LIVE",    sources:"Fleet Markov Chain · IEEE/CIGRÉ analysis" }
  ],

  /* ── fleet stats (placeholder — updated by ssi-data.json at runtime) ── */
  FREQ_DISTRIBUTION: {
      "Real-time": { count: 1, sources: ['Energinet Dispatch'] },
      "Hourly":    { count: 2, sources: ['ENTSO-E Flows', 'Nord Pool Bidding Zones'] },
      "Daily":     { count: 1, sources: ['DMI Weather'] },
      "Weekly":    { count: 1, sources: ['Energinet Systemtilstand'] },
      "Monthly":   { count: 3, sources: ['Copernicus ERA5', 'DMI Historical Archive', 'Dansk Energi Reports'] },
      "Quarterly": { count: 6, sources: ['Forsyningstilsynet DSO Reports', 'CFCS Cybersecurity', 'NBANK Economics', 'Traficom EV Data', 'ENT_HYDRO Hydrology', 'Districtcph Heating'] },
      "Annual":    { count: 12, sources: ['Danmarks Statistik Census', 'Forsyningstilsynet Inspections', 'GEUS Geology', 'Kystdirektoratet Coastal Monitoring', 'Miljøstyrelsen Environment', 'DSO Annual Reports', 'ENS Energy Agency', 'Geodatastyrelsen Geodata', 'DTU Wind Research', 'DTU Electrical Engineering', 'World Bank Benchmarks', 'Eurostat Nordic Data'] },
      "Static":    { count: 1, sources: ['SolarGIS Solar Atlas', 'OpenStreetMap Power'] }
    },
  stats: {
      variables: 95,
      metrics: 20,
      components: 6,
      modifiers: 7,
      sources: 29,
      substations: 2451,
      powerLines: 3676,
      mcIterations: 10000,
      region: 5,
      regions: 5
    },

  /* ── validation framework ── */
  VALIDATION_CHECKS: [
    { check:"West-East coastal storm gradient",                     criterion:"Western coastal regions (Jutland/Great Belt) show higher R systematically due to North Sea storm exposure vs eastern regions",                                status:"expected" },
    { check:"North Sea storm–I5 coherence (DMI)",                   criterion:"Substations in high-storm zones show elevated I5 scores — historical North Sea events and radar data",                                                         status:"expected" },
    { check:"Storm surge flooding–I5 agreement (Kystdirektoratet)",  criterion:"Coastal/low-lying substations show elevated I5 scores, especially in flood-prone areas and subsidence zones",                                              status:"expected" },
    { check:"Wind loading–I7 agreement (Kystdirektoratet)",          criterion:"Substations with high wind exposure show elevated I7 scores, especially in coastal western regions and open terrain",                                       status:"expected" },
    { check:"Offshore wind concentration–I9 signal (Energistyrelsen)", criterion:"Substations near/fed by major offshore wind farms show elevated I9 scores; ~50% wind generation concentration",                                           status:"expected" },
    { check:"Coastal flooding–I5 signal (Energinet Hydrology)",      criterion:"Coastal/delta-adjacent substations show elevated I5 during storm surge and spring flood risk periods",                                                      status:"expected" },
    { check:"RE stress–wind correlation (west coast)",               criterion:"Western coastal regions with high wind penetration show elevated S2 scores",                                                                                  status:"expected" },
    { check:"Coastal corrosion–I6 signal (DMI)",                     criterion:"High-exposure substations in salt-spray zones show elevated I6 corrosion class (C3–C4)",                                                                    status:"expected" },
    { check:"Great Belt/Øresund bottleneck–R4 signal",               criterion:"Great Belt and Øresund transmission corridors show elevated R4 graph criticality (single points of failure)",                                               status:"expected" },
    { check:"Bornholm island isolation–R4 signal",                   criterion:"Bornholm substations show elevated R4 due to island isolation and limited mainland connections",                                                           status:"expected" },
    { check:"RE stress vs EV load correlation",                      criterion:"S2 (RE stress) and S3 (EV penetration) positively correlated in urban areas (Copenhagen, Aarhus, Odense)",                                                status:"nascent" },
    { check:"Monte Carlo convergence (CV < 2%)",                     criterion:"Coefficient of variation < 2% at 10,000 iterations for all substations",                                                                                      status:"expected" },
    { check:"Weight budget unity",                                   criterion:"Component weights sum to 1.0000; all intra-weights sum to 1.0000 per component",                                                                              status:"expected" },
    { check:"Modifier range adherence",                              criterion:"All modifiers stay within declared [min, max] bounds across the fleet",                                                                                       status:"expected" },
    { check:"Band boundary contiguity",                              criterion:"No gap or overlap between Low/Medium/High/Critical thresholds",                                                                                                status:"expected" },
    { check:"R3 consequence signal + Copenhagen concentration",      criterion:"Urban centres (Copenhagen) and high-density communes consistently score higher R3 multiplier",                                                               status:"expected" },
    { check:"R6b North Sea storm/surge/wind sensitivity (CRITICAL)", criterion:"North Sea storm + storm surge + wind loading proximity drives R6b up to 1.25 ceiling; all three overlay components independent of other modifiers",       status:"critical" },
    { check:"Energinet vs DSO constraint signal",                    criterion:"Energinet transmission substations score higher R4; DSO periphery lower due to topology, except coastal bottlenecks",                                       status:"expected" },
    { check:"Bidding zone (DK1–DK2) price coherence",                criterion:"E1 scores align with Nord Pool price signals across bidding zones; wind curtailment level modulation visible",                                            status:"expected" },
    { check:"District heating CHP coupling effect",                  criterion:"Substations serving district heating plants show enhanced S2 via CHP dispatch flexibility and thermal load correlation",                                    status:"expected" },
    { check:"Soft soil/clay subsidence signal",                      criterion:"Low-lying regions on clay substrates show elevated I5 subsidence hazard; GEUS mapping validation",                                                          status:"expected" }
  ],

  /* ── changelog v3.4 → v4.0.2 (Denmark edition) ── */
  CHANGELOG: [
    { id:"DK1",  change:"Denmark country launch — 2,451 substations across 5 Regions, administrative kommune level",                                               type:"new" },
    { id:"DK2",  change:"Integrated Energinet transmission dispatch data + Forsyningstilsynet reliability benchmarks",                                          type:"data" },
    { id:"DK3",  change:"Forsyningstilsynet reliability register integrated — SAIDI/SAIFI standardisation for ~40 DSOs (RADIUS, N1, Cerius, NOE, KONSTANT, Energi Fyn, etc.)", type:"data" },
    { id:"DK4",  change:"DMI North Sea storm + coastal hazard data integrated — critical for maritime climate exposure assessment",                              type:"data" },
    { id:"DK5",  change:"Kystdirektoratet storm surge + coastal flooding hazard mapping integrated — coastal zone vulnerability",                               type:"data" },
    { id:"DK6",  change:"GEUS wind loading + soil subsidence mapping integrated — overhead transmission line vulnerability in flat terrain",                    type:"data" },
    { id:"DK7",  change:"DMI + Kystdirektoratet + GEUS climate integration — North Sea storm risk, coastal flooding, subsidence, wind exposure",                type:"data" },
    { id:"DK8",  change:"Danmarks Statistik Census + Eurostat socio-economic data integrated — vulnerability indices per kommune, urban concentration",         type:"data" },
    { id:"DK9",  change:"Dansk Energi + Energinet data integrated — RE penetration for coastal regions, offshore wind capacity growth trajectory",               type:"data" },
    { id:"DK10", change:"Nationalbanken + Nord Pool wind cycle coupling integrated — E1 volatility modulation for wind-dependent regions",                     type:"new" },
    { id:"DK11", change:"R6b modifier enhanced with triple DMI+KYS+GEUS hazard overlay: North Sea storm + storm surge + wind loading (range 1.00–1.25)",       type:"enhanced" },
    { id:"DK12", change:"R3 consequence enriched with island isolation, population density, Copenhagen urban concentration + coastal exposure metrics",        type:"enhanced" },
    { id:"DK13", change:"R4 graph criticality rebuilt with Energinet transmission topology + DSO network constraints + Great Belt/Øresund bottleneck penalty", type:"enhanced" },
    { id:"DK14", change:"I9 Offshore Wind Concentration Risk — new metric from Energistyrelsen/Energinet for major wind farm proximity (~50% of Danish generation)", type:"new" },
    { id:"DK15", change:"R2 Adaptive IRI now includes CMIP6 SSP2-4.5 forward projections for North Sea storms, coastal flooding risk shifts, subsidence acceleration", type:"enhanced" }
  ]
  };
})();
// Compatibility alias
window.SSI_METADATA = window.SSIMetadata;


