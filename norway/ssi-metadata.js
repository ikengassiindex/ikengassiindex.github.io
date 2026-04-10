/*  SSI v4.0.2 — Metadata Registry · Norway
    Loaded by every page in /norway/.
    ──────────────────────────────────────────────
    Exports:  window.SSIMetadata   (structured, matches Norway format exactly)
              window.SSI_METADATA  (legacy flat, backward-compat)              */

window.SSIMetadata = (function () {
  'use strict';
  return {

  /* ── Country metadata ── */
  country: "Norway",
  code: "NO",
  prefix: "NO_",
  tso: "Statnett SF",
  regulator: "NVE/RME (Reguleringsmyndigheten for energi)",
  statistics: "SSB (Statistisk sentralbyrå)",
  weather: "MET Norway (Meteorologisk institutt)",
  geology: "NGU (Norges geologiske undersøkelse)",
  nuclear: "NONE (Norway has zero nuclear power)",
  admin: { level1: "Fylke", level2: "Kommune" },
  currency: { code: "NOK", symbol: "kr" },

  /* ── 30 verified data sources — Norwegian institutions ── */
  DATA_SOURCES: [
    { id:"SNT", name:"Statnett SF — Norwegian Transmission System Operator", url:"statnett.no", freq:"Real-time", res:"Substation", vars:14, category:"Grid", feeds:"C1–C4, I2, S1–S2, transmission network topology, dispatch data, frequency regulation, bidding zones NO1–NO5" },
    { id:"NVE", name:"NVE/RME (Reguleringsmyndigheten for energi)", url:"nve.no", freq:"Quarterly", res:"DSO", vars:12, category:"Grid", feeds:"C1–C4, V1–V2, I1, reliability metrics SAIDI/SAIFI, technical standards, network quality, DSO performance" },
    { id:"SSB", name:"SSB (Statistisk sentralbyrå)", url:"ssb.no", freq:"Annual", res:"Kommune", vars:10, category:"Socio-Econ", feeds:"C1–C4, safety compliance, demographics, income distribution, population served, regional data" },
    { id:"METNOR", name:"MET Norway — Meteorologisk institutt", url:"met.no", freq:"Daily", res:"Station", vars:8, category:"Climate", feeds:"I3 (thermal stress, winter storms, avalanche risk), wind, precipitation, snow depth, Arctic warnings" },
    { id:"NGU", name:"NGU — Norges geologiske undersøkelse", url:"ngu.no", freq:"Annual", res:"Grid 0.1°", vars:7, category:"Hazard", feeds:"I5 (winter flooding + avalanche + fjord flooding hazard), geological data, soil mapping, landslide zones" },
    { id:"DSB", name:"DSB — Direktoratet for samfunnssikkerhet og beredskap", url:"dsb.no", freq:"Annual", res:"Grid 0.1°", vars:6, category:"Hazard", feeds:"I7 (snow/ice/rime loading zone mapping), avalanche hazard, environmental hazards, civil protection data" },
    { id:"NSM", name:"NSM/NorCERT — Cybersecurity Authority", url:"nsm.no", freq:"Quarterly", res:"Infrastructure Site", vars:5, category:"Energy", feeds:"Digital security baseline, critical infrastructure protection, cyber-physical resilience for SCADA systems" },
    { id:"OSM", name:"OpenStreetMap — Power Infrastructure", url:"overpass-api.de", freq:"Continuous", res:"Node", vars:8, category:"Infrastructure", feeds:"I4 (graph degree), topology, ~6,495 substations mapped across 15 Fylker, transmission + distribution networks" },
    { id:"COPERNICUS", name:"Copernicus ERA5 — Climate Reanalysis", url:"cds.climate.copernicus.eu", freq:"Monthly", res:"Grid 0.25°", vars:6, category:"Climate", feeds:"Thermal stress, snow loading, winter storm risk, avalanche probability, CMIP6 forward projections for Arctic region" },
    { id:"ENTSOE", name:"ENTSO-E Transparency Platform", url:"transparency.entsoe.eu", freq:"Hourly", res:"Substation", vars:2, category:"Grid", feeds:"C1 (capacity), cross-border flows with Sweden/Finland/Germany/UK/Denmark, Nordic grid exchange, bidding zone flows" },
    { id:"EUROSTAT", name:"Eurostat — EU Statistics", url:"ec.europa.eu/eurostat", freq:"Annual", res:"Kommune", vars:3, category:"Socio-Econ", feeds:"E2 (population served), water-energy nexus, Nordic energy poverty indicators" },
    { id:"ENOVA", name:"Enova SF — Energy Efficiency & Transition", url:"enova.no", freq:"Annual", res:"National", vars:3, category:"Transition", feeds:"Energy efficiency programs, RE transition support, grid flexibility initiatives" },
    { id:"VEGDIR", name:"Vegdirektoratet — Transport Agency", url:"vegvesen.no", freq:"Quarterly", res:"Regional", vars:3, category:"Transport", feeds:"S3 (EV registrations), electric vehicle charging infrastructure density, remote region accessibility" },
    { id:"NORGES_BANK", name:"Norges Bank", url:"norges-bank.no", freq:"Quarterly", res:"Region", vars:4, category:"Economic", feeds:"E1–E3, economic cycles, business density, industrial concentration, hydropower economics" },
    { id:"WIND_NO", name:"Norwegian Wind Energy Association (Norsk Vindenergiforening)", url:"vindkraft.no", freq:"Monthly", res:"Regional", vars:5, category:"Transition", feeds:"S1 (RE capacity), wind capacity by region, capacity factors, western coastal wind corridor" },
    { id:"NVE_HYDRO", name:"NVE — Norwegian Water Resources and Energy Directorate (Hydrology)", url:"nve.no", freq:"Quarterly", res:"Watershed", vars:4, category:"Hazard", feeds:"I5 (hydropower reservoir levels, spring snowmelt flooding hazard), water level monitoring, stream flow, fjord dynamics" },
    { id:"DISTRIBUTOR", name:"Distribution Companies (Elvia, BKK, Glitre Nett, Lede, Tensio, Agder Energi Nett)", url:"", freq:"Annual", res:"Distribution Company", vars:4, category:"Grid", feeds:"S1 variant (hydropower plant dispatch), CAPEX, SAIDI/SAIFI, transformer inventories, restoration metrics" },
    { id:"MILJOE", name:"Miljødirektoratet — Norwegian Environment Agency", url:"miljodirektoratet.no", freq:"Annual", res:"Kommune", vars:3, category:"Environment", feeds:"I6 (environmental exposure), pollution data, industrial sites, fjord protection zones" },
    { id:"KLIM_CENTRE", name:"Norsk Klimaservicesenter — Climate Service Centre", url:"klimaservicesenter.no", freq:"Annual", res:"Regional", vars:4, category:"Environment", feeds:"I5 (winter storm + flooding + avalanche hazard mapping), climate adaptation data, extreme weather risk" },
    { id:"WORLDBANK", name:"World Bank / OECD", url:"", freq:"Annual", res:"National", vars:4, category:"Socio-Econ", feeds:"International benchmarks, Nordic socio-economic indicators, renewable energy transition comparisons" },
    { id:"SOLARGIS", name:"SolarGIS — Global Solar Atlas", url:"globalsolaratlas.info", freq:"Static", res:"Global", vars:2, category:"Transition", feeds:"T1 (solar resource mapping), solar irradiance (GHI, DNI) for southern Norway" },
    { id:"AMAP", name:"Arctic Monitoring & Assessment Programme", url:"amap.no", freq:"Annual", res:"Regional", vars:3, category:"Climate", feeds:"I6 (Arctic corrosion class), permafrost thaw zones, extreme weather baselines, Arctic wind patterns" },
    { id:"KARTVERKET", name:"Kartverket — Norwegian Mapping Authority", url:"kartverket.no", freq:"Annual", res:"Regional", vars:3, category:"Infrastructure", feeds:"Geospatial grid topology, topographic hazard data, fjord bathymetry, mountain terrain analysis" },
    { id:"NVE_KRAFTSIT", name:"NVE — Kraftsituasjonen (Power Situation Reports)", url:"nve.no", freq:"Weekly", res:"National", vars:3, category:"Grid", feeds:"Real-time power balance, hydropower reservoir status, wind generation forecasts" },
    { id:"STATKRAFT", name:"Statkraft — Major Hydropower Producer", url:"statkraft.no", freq:"Weekly", res:"Facility", vars:3, category:"Energy", feeds:"Hydropower dispatch, reservoir management, generation forecasts, capacity utilisation" },
    { id:"NORDPOOL", name:"Nord Pool — Nordic Energy Exchange", url:"nordpoolgroup.com", freq:"Hourly", res:"Bidding Zone", vars:4, category:"Market", feeds:"E1 (electricity pricing), bidding zone NO1–NO5 price signals, cross-border flows" },
    { id:"HAVFORSK", name:"Havforskningsinstituttet — Institute of Marine Research", url:"hi.no", freq:"Annual", res:"Regional", vars:2, category:"Environment", feeds:"Fjord dynamics, marine ecosystem stress indicators, offshore power infrastructure impacts" },
    { id:"SINTEF", name:"SINTEF Energy Research", url:"sintef.no", freq:"Annual", res:"Regional", vars:3, category:"Transition", feeds:"Grid stability research, microgrid capability, demand-side flexibility, storage readiness" },
    { id:"METNOR_HIST", name:"MET Norway / Historical Archive", url:"met.no", freq:"Monthly", res:"Station", vars:3, category:"Climate", feeds:"Historical winter storm severity index, snow accumulation records, Arctic wind patterns, rime ice events" },
    { id:"ENTSOE_TSOS", name:"ENTSO-E TSO Interconnects (Statnett)", url:"entsoe.eu", freq:"Continuous", res:"Border Point", vars:2, category:"Grid", feeds:"HVDC flows: NordLink (DE), North Sea Link (UK), NorNed (NL), Skagerrak 1-4 (DK)" }
  ],

  /* ── 6 components · 20 metrics ── */
  COMPONENTS: [
    {
      id:"C", name:"Continuity", weight:0.30, color:"#941914",
      desc:"Measures reliability and outage exposure — how often and how long power interruptions occur, accounting for Norwegian winter conditions and avalanche impacts.",
      metrics:[
        { id:"C1", name:"Outage Duration (SAIDI)", intra:0.35, global:0.105, norm:"A (P5/P95)", source:"Statnett SF / NVE", desc:"Total annual interruption duration per customer", inverted:false, adaptive:false, isNew:false },
        { id:"C2", name:"Outage Frequency (SAIFI)", intra:0.30, global:0.090, norm:"A (P5/P95)", source:"Statnett SF / NVE", desc:"Number of sustained interruptions per customer per year", inverted:false, adaptive:false, isNew:false },
        { id:"C3", name:"Restoration Time (CAIDI)", intra:0.20, global:0.060, norm:"A (P5/P95)", source:"NVE / DSO", desc:"Average duration of each interruption (winter storm + avalanche recovery time critical)", inverted:false, adaptive:false, isNew:false },
        { id:"C4", name:"Momentary Interruptions (MAIFI)", intra:0.15, global:0.045, norm:"A (P5/P95)", source:"Statnett SF", desc:"Momentary average interruption frequency index", inverted:false, adaptive:false, isNew:false }
      ]
    },
    {
      id:"V", name:"Voltage Quality", weight:0.10, color:"#aa4234",
      desc:"Captures voltage stability, power factor, and harmonic distortion at the distribution level.",
      metrics:[
        { id:"V1", name:"Voltage Deviation (ΔV)", intra:0.40, global:0.040, norm:"A (P5/P95)", source:"NVE / DSO", desc:"Percentage deviation from nominal voltage", inverted:false, adaptive:false, isNew:false },
        { id:"V2", name:"THD (Harmonic Distortion)", intra:0.30, global:0.030, norm:"A (P5/P95)", source:"NVE", desc:"Total harmonic distortion percentage", inverted:false, adaptive:false, isNew:false },
        { id:"V3", name:"Power Factor", intra:0.30, global:0.030, norm:"B (inverse)", source:"NVE / DSO", desc:"Ratio of real to apparent power — higher is better", inverted:true, adaptive:false, isNew:false }
      ]
    },
    {
      id:"I", name:"Infrastructure", weight:0.25, color:"#5d8563",
      desc:"Assesses physical asset condition, age, capacity, and Norway-specific hazards: winter storms, avalanches, fjord flooding, rime ice loading (critical for Norwegian terrain).",
      metrics:[
        { id:"I1", name:"Asset Age Index", intra:0.12, global:0.030, norm:"A (P5/P95)", source:"NVE / SSB", desc:"Fleet-normalised average asset age", inverted:false, adaptive:false, isNew:false },
        { id:"I2", name:"Capacity Utilisation", intra:0.12, global:0.030, norm:"A (P5/P95)", source:"Statnett SF / NVE", desc:"Percentage of rated capacity in use", inverted:false, adaptive:false, isNew:false },
        { id:"I3", name:"Climate IRI (Thermal + Winter Storm + Avalanche Stress)", intra:0.12, global:0.030, norm:"A (P5/P95)", source:"MET Norway / DSB / ERA5", desc:"Infrastructure Risk Index based on extreme cold, winter storms, avalanche hazard, and Arctic conditions", inverted:false, adaptive:true, isNew:false },
        { id:"I4", name:"Graph Degree (Topology)", intra:0.12, global:0.030, norm:"B (inverse)", source:"OSM / Statnett SF", desc:"Number of connections — higher degree = more redundancy", inverted:true, adaptive:false, isNew:false },
        { id:"I5", name:"Winter Storm + Avalanche + Fjord Flooding Hazard", intra:0.18, global:0.045, norm:"A (P5/P95)", source:"MET Norway / NGU / DSB / NVE Hydrology", desc:"Combined winter storm severity + avalanche risk + spring snowmelt/fjord flooding hazard (critical for Norway)", inverted:false, adaptive:false, isNew:false },
        { id:"I6", name:"Corrosion Class (Arctic)", intra:0.10, global:0.025, norm:"D (categorical)", source:"ISO9223 / AMAP", desc:"Environmental corrosion exposure adapted for Arctic conditions, salt spray, fjord proximity, and extreme humidity", inverted:false, adaptive:false, isNew:false, categorical:true },
        { id:"I7", name:"Snow/Ice/Rime Loading Zone", intra:0.12, global:0.030, norm:"D (categorical)", source:"DSB / NGU / MET Norway", desc:"Snow/ice/rime accumulation hazard mapping for overhead transmission lines (rime ice critical in Norwegian mountains)", inverted:false, adaptive:true, isNew:false, categorical:true },
        { id:"I8", name:"N-1 Compliance", intra:0.05, global:0.0125, norm:"C (binary)", source:"Statnett SF", desc:"Whether substation meets N-1 redundancy standard (Statnett 420kV backbone)", inverted:true, adaptive:false, isNew:false },
        { id:"I9", name:"Hydropower Concentration Risk", intra:0.07, global:0.0175, norm:"D (categorical)", source:"NVE / Statkraft", desc:"Concentration risk for substations supplying or dependent on major hydropower reservoirs (~90% of Norwegian generation)", inverted:false, adaptive:false, isNew:true, categorical:true }
      ]
    },
    {
      id:"E", name:"Economic", weight:0.10, color:"#3b9eff",
      desc:"Links grid risk to regional economic exposure — energy pricing, employment, and hydropower-driven economic cycles.",
      metrics:[
        { id:"E1", name:"Energy Price Index + Hydropower Cycle", intra:0.40, global:0.040, norm:"A (P5/P95)", source:"Norges Bank / NordPool / NVE", desc:"Wholesale + retail electricity cost per MWh, modulated by hydropower availability and reservoir levels", inverted:false, adaptive:true, isNew:false },
        { id:"E2", name:"Population Served + Remote Sparsity", intra:0.30, global:0.030, norm:"A (P5/P95)", source:"SSB / Eurostat", desc:"Kommune-level population served, with penalty for remote Arctic communities and fjord-isolated regions", inverted:false, adaptive:false, isNew:false },
        { id:"E3", name:"Business Density + Industrial Concentration", intra:0.30, global:0.030, norm:"A (P5/P95)", source:"NVE / SSB / Enova", desc:"Economic activity clusters and large industrial load concentration (aluminum smelters, oil/gas processing, mining)", inverted:false, adaptive:false, isNew:false }
      ]
    },
    {
      id:"S", name:"Saturation", weight:0.20, color:"#b88f3e",
      desc:"Quantifies DER/RE penetration stress, hydropower variability, reverse power flow risk, and EV charging load on the grid.",
      metrics:[
        { id:"S1", name:"Renewable Energy Capacity Ratio", intra:0.35, global:0.070, norm:"A (P5/P95)", source:"Norwegian Wind Energy Assoc. / Statnett SF / NVE", desc:"Total installed RE (wind/hydro/solar) capacity relative to substation rating (~90% hydro baseline + wind growth)", inverted:false, adaptive:false, isNew:false },
        { id:"S2", name:"RE Stress Index (Hydropower Variability + Wind Curtailment)", intra:0.35, global:0.070, norm:"A (P5/P95)", source:"Norwegian Wind Energy Assoc. / Statnett SF", desc:"Composite stress: RE penetration × hydropower variability × wind output variability × transmission constraints (coastal wind growth)", inverted:false, adaptive:true, isNew:false },
        { id:"S3", name:"EV Penetration Rate (Emerging)", intra:0.30, global:0.060, norm:"A (P5/P95)", source:"Vegdirektoratet / Transport Ministry", desc:"EV registrations as percentage of total fleet in catchment area (growing penetration in urban areas Oslo/Bergen)", inverted:false, adaptive:false, isNew:true }
      ]
    },
    {
      id:"T", name:"Energy Transition", weight:0.05, color:"#0e7490", isNew:true,
      desc:"Measures clean energy transition pace and grid readiness for decarbonisation (RE targets: 100% by 2050, wind expansion priority).",
      metrics:[
        { id:"T1", name:"Renewable Energy Share (%)", intra:0.50, global:0.025, norm:"B (inverse)", source:"Norwegian Wind Energy Assoc. / Statnett SF / NVE", desc:"Share of generation from renewables — higher share = lower risk (inverted, ~90% hydro baseline + wind growth)", inverted:true, adaptive:false, isNew:false },
        { id:"T2", name:"Transition Readiness Score", intra:0.50, global:0.025, norm:"A (P5/P95)", source:"NVE / Norwegian Wind Energy Assoc. / Statnett SF", desc:"Composite readiness: grid flexibility + storage deployment (pumped hydro) + DSO interconnection capacity + wind integration", inverted:true, adaptive:false, isNew:true }
      ]
    }
  ],

  /* ── 7 modifiers (R2–R7, incl. R6a + R6b winter storm/avalanche/rime ice) ── */
  MODIFIERS: [
    { id:"R2", name:"Adaptive Climate IRI + Arctic Hazard Trajectory", range:"Weight redistribution", type:"Weight modifier", desc:"Uses CMIP6 SSP2-4.5 projections to adjust IRI metrics for winter storm risk, avalanche hazard, fjord flooding, and rime ice exposure in Arctic regions. When local winter/avalanche risk is elevated, weight shifts to structural metrics. Incorporates MET Norway forecasts and DSB hazard mapping.", formula:"IRI_forward(m,s) = IRI_current(m,s) × (1 + 0.15 × clip(Δ_climate, −0.50, +1.00))", sources:["MET Norway","DSB","COPERNICUS ERA5","NGU"], isEnhanced:true },
    { id:"R3", name:"Consequence + Arctic Remoteness + Population Sparsity", range:"[0.70, 1.35]", type:"Multiplicative", desc:"Amplifies risk for communities with sparse population, Arctic remoteness, fjord isolation, or high energy dependency. Includes vulnerability indices (SSB demographics), exposure in northern regions (Finnmark/Troms), and isolation metrics.", formula:"C_mult = sigmoid(pop_weight × remote_weight × V_socio × arctic_factor)", sources:["SSB","EUROSTAT","Vegdirektoratet"], isEnhanced:true },
    { id:"R4", name:"Graph Criticality + Network Constraint", range:"[0.80, 1.40]", type:"Multiplicative", desc:"Penalises topological bottlenecks in Statnett 420kV backbone and DSO networks: high betweenness centrality, bridge nodes, low degree. Built from OSM power graph and Statnett transmission constraints, with special attention to mountain pass corridors and fjord bottlenecks.", formula:"F_topo = f(degree, BC_percentile, is_bridge, mountain_pass_exposure, statnett_tier)", sources:["OSM","Statnett SF"], isEnhanced:true },
    { id:"R6a", name:"Restoration Speed (Winter Storm + Avalanche Focus)", range:"[0.90, 1.10]", type:"Multiplicative", desc:"NVE-CAIDI-based: rewards fast-restoring areas, penalises slow ones in northern/mountain regions. Two substations with identical SAIDI can have different risk profiles based on restoration speed in remote areas affected by avalanches or mountain terrain.", formula:"R6a = sigmoid_bounded(CAIDI_local / CAIDI_fleet_median)", sources:["NVE","Statnett SF"], isEnhanced:true },
    { id:"R6b", name:"Winter Storm + Avalanche + Rime Ice Overlay (CRITICAL FOR NORWAY)", range:"[1.00, 1.25]", type:"Multiplicative", desc:"MET Norway winter storm hazard + DSB avalanche risk + rime ice loading overlay. Penalises substations in high-storm zones, avalanche corridors, or heavy rime-loading regions. Integration of real-time MET Norway warnings and historical winter event impacts. Rime ice is a major Norwegian grid threat.", formula:"R6b = f(MET_storm_percentile, DSB_avalanche_zone, NGU_rime_ice_loading, fjord_flood_proximity)", sources:["MET Norway","DSB","NGU","NVE Hydrology"], isEnhanced:true },
    { id:"R7", name:"Digital Readiness + Cyber-Physical Resilience", range:"[0.99, 1.05]", type:"Multiplicative", desc:"Cyber-physical security baseline, SCADA maturity proxy (Norway high), and microgrid/islanding capability. Indicates digital resilience capability at the grid edge for winter event recovery scenarios and Arctic infrastructure security.", formula:"Cyber = f(SCADA_maturity, microgrid_pct, islanding_capability, arctic_security_baseline)", sources:["Statnett SF","NVE","NSM"], isEnhanced:false }
  ],

  /* ── processing pipeline ── */
  PIPELINE: [
    { step:1, name:"Ingest", desc:"95 variables from 30 verified Norwegian public data sources — Statnett SF, NVE, SSB, MET Norway, NGU, DSB, NSM, and others. Zero proprietary SCADA dependencies. Maximum ingestion frequency: real-time (Statnett dispatch data).", icon:"📥" },
    { step:2, name:"Normalise", desc:"Four normalisation methods: Method A (robust fleet percentile P5/P95), Method B (inverse fleet percentile for density), Method C (binary compliance), and Method D (categorical mapping). Inverted metrics for density measures where higher = better resilience.", icon:"📐" },
    { step:3, name:"Weight", desc:"6-level hierarchical weighting across 6 components and 20 metrics. Continuity dominates at 0.30, Infrastructure at 0.25 (with higher winter storm/avalanche/rime ice I5 weight), Saturation at 0.20. Weight budget validated by Sobol sensitivity analysis.", icon:"⚖️" },
    { step:4, name:"Compose R_base", desc:"Weighted sum of 6 normalised component scores produces the base resilience score.", icon:"🧮" },
    { step:5, name:"Modify", desc:"Seven multiplicative modifiers adjust R_base for Norwegian context: R2 (adaptive climate + Arctic hazard trajectory), R3 (consequence + Arctic remoteness + population sparsity + fjord isolation), R4 (graph criticality + Statnett/DSO constraints + mountain passes), R6a (restoration speed in remote/mountain areas), R6b (winter storm/avalanche/rime ice overlay — CRITICAL), R7 (digital readiness). Plus enrichments for vulnerable populations, avalanche zones, and critical hydropower infrastructure.", icon:"🔧" },
    { step:6, name:"Monte Carlo", desc:"10,000 iterations per substation using a 20×20 Gaussian copula correlation matrix. Captures measurement, spatial, staleness, and model uncertainty. Produces median, P5, P95, skewness, and P_critical for each substation.", icon:"🎲" },
    { step:7, name:"Classify", desc:"Four bands: Low (0.00–0.25), Medium (0.25–0.50), High (0.50–0.75), Critical (0.75–1.00). Alert flags trigger when any single component exceeds its P95 fleet threshold. Winter storm/avalanche/rime ice events escalate classification instantaneously.", icon:"🏷️" }
  ],

  /* ── classification bands ── */
  CLASSIFICATION: [
    { name:"Low",      range:"0.00 – 0.25", meaning:"Good resilience — stable grid, low exposure",       expected:"~35–40%", color:"#5d8563" },
    { name:"Medium",   range:"0.25 – 0.50", meaning:"Moderate risk — some vulnerabilities present",       expected:"~32–38%", color:"#b88f3e" },
    { name:"High",     range:"0.50 – 0.75", meaning:"Elevated risk — investment priority zone",           expected:"~18–23%", color:"#aa4234" },
    { name:"Critical", range:"0.75 – 1.00", meaning:"Severe vulnerability — urgent intervention required", expected:"~5–10%",   color:"#941914" }
  ],

  /* ── master equation ── */
  MASTER_EQUATION: "R_final = soft_clip_upper( R_base × F_topo × C_mult × R6a_mult × R6b_winter_avalanche_rime × Cyber_factor )",

  /* ── normalisation methods ── */
  NORM_METHODS: [
    { id:"A", name:"Fleet Percentile (robust)", formula:"N(x) = soft_clip((x − P₅) / (P₉₅ − P₅))", applies:"C1, C2, C3, C4, V1, V2, I1, I2, I3, I5, E1, E2, E3, S1, S2, S3" },
    { id:"B", name:"Fleet Percentile (inverse)", formula:"N(x) = 1 − soft_clip((x − P₅) / (P₉₅ − P₅))", applies:"V3, I4, T1, T2" },
    { id:"C", name:"Binary (bounded)", formula:"N(x) = 0 if compliant, 1 if non-compliant", applies:"I8 (N-1 compliance)" },
    { id:"D", name:"Categorical Mapping", formula:"N(x) = lookup_table(class → [0, 1])", applies:"I6 (Arctic corrosion), I7 (snow/ice/rime loading), I9 (hydropower concentration)" }
  ],

  /* ── 11 data layers · 95 variables ── */
  DATA_LAYERS: [
    { id:"A",   name:"SSI v4.0.2 Resilience (Norway)",              vars:20, status:"LIVE",    sources:"Statnett SF · NVE · SSB · MET Norway · DSB · NGU" },
    { id:"B.1", name:"Grid Telemetry: Open",                       vars:3,  status:"LIVE",    sources:"MET Norway / ERA5 · Statnett SF" },
    { id:"B.2", name:"Grid Telemetry: Proxy",                      vars:4,  status:"LIVE",    sources:"IEEE C57.91 · DSO · NVE" },
    { id:"B.3", name:"Grid Telemetry: Fuzzy",                      vars:12, status:"FUZZY",   sources:"IEEE/CIGRÉ standards · NGU" },
    { id:"C",   name:"Socio-Economic + Nordic Demographics",        vars:10, status:"LIVE",    sources:"SSB · EUROSTAT · Norges Bank · Enova" },
    { id:"D",   name:"Environmental Hazards (Winter Storm+Avalanche+Flooding)",vars:8,  status:"LIVE",    sources:"MET Norway · DSB · NGU · Copernicus · NVE Hydrology" },
    { id:"E",   name:"Norwegian Open Data + Energy Policy",         vars:9,  status:"LIVE",    sources:"NVE · Norwegian Wind Energy · Enova · Kartverket" },
    { id:"F",   name:"Network Transitions + Hydropower Baseload",   vars:12, status:"BAYESIAN",sources:"DSO history OR IEEE/CIGRÉ + priors" },
    { id:"G",   name:"Modifier Inputs (Winter Storm/Avalanche-Weighted)",vars:4,  status:"LIVE",    sources:"NVE reliability · MET Norway · OSM" },
    { id:"H",   name:"Network & Topology (Statnett 420kV)",         vars:7,  status:"LIVE",    sources:"Statnett SF · ENTSO-E · OSM" },
    { id:"I",   name:"Output Scores + Alert Flags",                 vars:7,  status:"LIVE",    sources:"Fleet Markov Chain · IEEE/CIGRÉ analysis" }
  ],

  /* ── fleet stats (placeholder — updated by ssi-data.json at runtime) ── */
  FREQ_DISTRIBUTION: {
      "Real-time": { count: 1, sources: ['Statnett Dispatch'] },
      "Hourly":    { count: 2, sources: ['ENTSO-E Flows', 'Statnett Generation'] },
      "Daily":     { count: 1, sources: ['MET Norway Weather'] },
      "Weekly":    { count: 2, sources: ['DSB Emergency Reports', 'NVE Energy Reports'] },
      "Monthly":   { count: 3, sources: ['Copernicus ERA5', 'MET Norway Forecasts', 'Kartverket Geospatial'] },
      "Quarterly": { count: 5, sources: ['NVE Reliability Reports', 'SSB Demographics', 'Norges Bank Economics', 'Enova Programs', 'AMAP Arctic Assessment'] },
      "Annual":    { count: 13, sources: ['SSB Census Updates', 'NVE Inspections', 'NGU Geology', 'DSB Avalanche Monitoring', 'MET Norway Climate', 'DSO Annual Reports', 'Norwegian Wind Energy Assoc', 'Statkraft Hydro Data', 'EUROSTAT Nordic', 'Traficom EV Data', 'Kartverket Geodesy', 'OSM Infrastructure', 'World Bank Benchmarks'] },
      "Static":    { count: 1, sources: ['SolarGIS Solar Atlas', 'OpenStreetMap Power'] }
    },
  stats: {
      variables: 95,
      metrics: 20,
      components: 6,
      modifiers: 7,
      sources: 30,
      substations: 6495,
      powerLines: 9742,
      mcIterations: 10000,
      fylke: 15,
      regions: 15
    },

  /* ── validation framework ── */
  VALIDATION_CHECKS: [
    { check:"North–South latitude gradient (Arctic exposure)",       criterion:"Northern Norway (Finnmark/Troms) R systematically higher than southern regions due to winter/avalanche conditions",                                      status:"expected" },
    { check:"Winter storm–I5 coherence (MET Norway)",               criterion:"Substations in high-storm zones show elevated I5 scores — historical winter events and radar data",                                                        status:"expected" },
    { check:"Avalanche–I5 agreement (DSB/NGU)",                     criterion:"Substations in avalanche corridors show elevated I5 scores, especially in mountain passes and eastern valleys",                                             status:"expected" },
    { check:"Snow/ice/rime loading–I7 agreement (DSB)",             criterion:"Substations with rime ice risk show elevated I7 scores, especially overhead transmission in high-altitude regions",                                         status:"expected" },
    { check:"Hydropower concentration–I9 signal (NVE/Statkraft)",   criterion:"Substations near/fed by major reservoirs show elevated I9 scores; ~90% hydro generation concentration",                                                   status:"expected" },
    { check:"Fjord flooding–I5 signal (NVE Hydrology)",             criterion:"Coastal/fjord-adjacent substations show elevated I5 during spring snowmelt and storm surge risk periods",                                               status:"expected" },
    { check:"RE stress–wind correlation (coastal region)",          criterion:"Coastal western regions with high wind penetration show elevated S2 scores",                                                                                status:"expected" },
    { check:"Arctic corrosion–I6 signal (AMAP)",                    criterion:"High-latitude substations in salt-spray zones show elevated I6 corrosion class exposure",                                                                  status:"expected" },
    { check:"Mountain terrain bottleneck–R4 signal",                criterion:"Mountain pass corridors and fjord-constrained network segments show elevated R4 graph criticality",                                                        status:"expected" },
    { check:"RE stress vs EV load correlation",                     criterion:"S2 (RE stress) and S3 (EV penetration) positively correlated in urban areas (Oslo, Bergen, Stavanger)",                                                    status:"nascent" },
    { check:"Monte Carlo convergence (CV < 2%)",                    criterion:"Coefficient of variation < 2% at 10,000 iterations for all substations",                                                                                      status:"expected" },
    { check:"Weight budget unity",                                  criterion:"Component weights sum to 1.0000; all intra-weights sum to 1.0000 per component",                                                                              status:"expected" },
    { check:"Modifier range adherence",                             criterion:"All modifiers stay within declared [min, max] bounds across the fleet",                                                                                       status:"expected" },
    { check:"Band boundary contiguity",                             criterion:"No gap or overlap between Low/Medium/High/Critical thresholds",                                                                                                status:"expected" },
    { check:"R3 consequence signal + Arctic remoteness",            criterion:"High-remoteness, sparse-population areas consistently score higher R3 multiplier (Finnmark/Troms/mountain regions)",                                       status:"expected" },
    { check:"R6b winter storm/avalanche/rime sensitivity (CRITICAL)",criterion:"Winter storm + avalanche + rime ice proximity drives R6b up to 1.25 ceiling; all three overlay components independent of other modifiers",                  status:"critical" },
    { check:"Statnett vs DSO constraint signal",                    criterion:"Statnett 420kV backbone substations score higher R4; DSO periphery lower due to topology, except mountain corridors",                                     status:"expected" },
    { check:"Bidding zone (NO1–NO5) price coherence",               criterion:"E1 scores align with NordPool price signals across bidding zones; hydropower reservoir level modulation visible",                                          status:"expected" }
  ],

  /* ── changelog v3.4 → v4.0.2 (Norway edition) ── */
  CHANGELOG: [
    { id:"NO1",  change:"Norway country launch — 6,495 substations across 15 Fylker, administrative kommune level",                                                type:"new" },
    { id:"NO2",  change:"Integrated Statnett SF transmission dispatch data + NVE reliability benchmarks",                                                         type:"data" },
    { id:"NO3",  change:"NVE reliability register integrated — SAIDI/SAIFI standardisation for all DSOs (Elvia, BKK, Glitre Nett, Lede, Tensio, Agder Energi Nett)",type:"data" },
    { id:"NO4",  change:"MET Norway winter storm + Arctic hazard data integrated — critical for boreal/Arctic climate exposure assessment",                       type:"data" },
    { id:"NO5",  change:"DSB avalanche hazard mapping integrated — mountain corridor vulnerability in eastern/western valleys",                                   type:"data" },
    { id:"NO6",  change:"NGU rime ice loading mapping integrated — overhead transmission line vulnerability in high-altitude regions",                            type:"data" },
    { id:"NO7",  change:"MET Norway + DSB + NGU climate integration — winter storm risk, snow accumulation, avalanche probability, rime ice hazard",               type:"data" },
    { id:"NO8",  change:"SSB Census 2021 + Eurostat socio-economic data integrated — vulnerability indices per kommune, Arctic remoteness",                       type:"data" },
    { id:"NO9",  change:"Norwegian Wind Energy + NVE data integrated — RE penetration for coastal regions, wind capacity growth trajectory",                      type:"data" },
    { id:"NO10", change:"Norges Bank + NordPool hydropower cycle coupling integrated — E1 volatility modulation for reservoir-dependent regions",                 type:"new" },
    { id:"NO11", change:"R6b modifier enhanced with triple MET+DSB+NGU hazard overlay: winter storm + avalanche + rime ice (range 1.00–1.25)",                  type:"enhanced" },
    { id:"NO12", change:"R3 consequence enriched with Arctic remoteness, population sparsity, Finnmark/Troms isolation + fjord enclosure metrics",               type:"enhanced" },
    { id:"NO13", change:"R4 graph criticality rebuilt with Statnett 420kV topology + DSO network constraints + mountain pass bottleneck penalty",                type:"enhanced" },
    { id:"NO14", change:"I9 Hydropower Concentration Risk — new metric from NVE/Statkraft for major reservoir proximity (~90% of Norwegian generation)",         type:"new" },
    { id:"NO15", change:"R2 Adaptive IRI now includes CMIP6 SSP2-4.5 forward projections for Arctic winter extremes, avalanche probability shifts, permafrost change",type:"enhanced" }
  ]
  };
})();
// Compatibility alias
window.SSI_METADATA = window.SSIMetadata;


