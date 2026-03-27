/*  SSI v4.0.2 — Metadata Registry · Sweden
    Loaded by every page in /sweden/.
    ──────────────────────────────────────────────
    Exports:  window.SSIMetadata   (structured, matches Sweden format exactly)
              window.SSI_METADATA  (legacy flat, backward-compat)              */

window.SSIMetadata = {

  /* ── Country metadata ── */
  country: "Sweden",
  code: "SE",
  prefix: "SE_",
  tso: "Svenska kraftnät",
  regulator: "Energimarknadsinspektionen (Ei)",
  statistics: "SCB (Statistiska centralbyrån)",
  weather: "SMHI",
  geology: "SGU",
  nuclear: "SSM (Strålsäkerhetsmyndigheten)",
  admin: { level1: "Län", level2: "Kommun" },
  currency: { code: "SEK", symbol: "kr" },

  /* ── 30 verified data sources — Swedish institutions ── */
  DATA_SOURCES: [
    { id:"SKN", name:"Svenska kraftnät — Swedish Transmission System Operator", url:"svk.se", freq:"Real-time", res:"Substation", vars:14, category:"Grid", feeds:"C1–C4, I2, S1–S2, transmission network topology, dispatch data, frequency regulation" },
    { id:"EI", name:"Energimarknadsinspektionen (Energy Markets Inspectorate)", url:"ei.se", freq:"Quarterly", res:"DSO", vars:12, category:"Grid", feeds:"C1–C4, V1–V2, I1, reliability metrics SAIDI/SAIFI, technical standards, network quality", registration:true },
    { id:"SCB", name:"SCB (Statistiska centralbyrån)", url:"scb.se", freq:"Annual", res:"Kommun", vars:10, category:"Socio-Econ", feeds:"C1–C4, safety compliance, demographics, income distribution, population served" },
    { id:"SMHI", name:"SMHI — Swedish Meteorological and Hydrological Institute", url:"smhi.se", freq:"Daily", res:"Station", vars:8, category:"Climate", feeds:"I3 (thermal stress, winter storms), wind, precipitation, snow depth, Arctic warnings" },
    { id:"SGU", name:"SGU — Geological Survey of Sweden", url:"sgu.se", freq:"Annual", res:"Grid 0.1°", vars:7, category:"Hazard", feeds:"I5 (winter flooding hazard), geological data, soil mapping, permafrost zones" },
    { id:"SMHI_ENV", name:"Naturvårdsverket — Swedish Environmental Protection Agency", url:"naturvardsverket.se", freq:"Annual", res:"Grid 0.1°", vars:6, category:"Hazard", feeds:"I7 (snow/ice loading zone mapping), environmental hazards, water availability" },
    { id:"SSM", name:"SSM — Strålsäkerhetsmyndigheten (Radiation Safety Authority)", url:"ssm.se", freq:"Quarterly", res:"Nuclear Site", vars:5, category:"Energy", feeds:"I9 (nuclear concentration risk), safety metrics, Forsmark + Ringhals + Barsebäck operational data" },
    { id:"OSM", name:"OpenStreetMap — Power Infrastructure", url:"overpass-api.de", freq:"Continuous", res:"Node", vars:8, category:"Infrastructure", feeds:"I4 (graph degree), topology, ~3,570 substations mapped, transmission + distribution networks" },
    { id:"COPERNICUS", name:"Copernicus ERA5 — Climate Reanalysis", url:"cds.climate.copernicus.eu", freq:"Monthly", res:"Grid 0.25°", vars:6, category:"Climate", feeds:"Thermal stress, snow loading, winter storm risk, CMIP6 forward projections for Nordic region" },
    { id:"ENTSOE", name:"ENTSO-E Transparency Platform", url:"transparency.entsoe.eu", freq:"Hourly", res:"Substation", vars:2, category:"Grid", feeds:"C1 (capacity), cross-border flows with Norway/Finland/Germany, Nordic grid exchange" },
    { id:"EUROSTAT", name:"Eurostat — EU Statistics", url:"ec.europa.eu/eurostat", freq:"Annual", res:"Kommun", vars:3, category:"Socio-Econ", feeds:"E2 (population served), water-energy nexus, Nordic energy poverty indicators" },
    { id:"TULLV", name:"Tullverket (Swedish Customs)", url:"tullverket.se", freq:"Annual", res:"National", vars:2, category:"Trade", feeds:"Trade data proxy, industrial activity" },
    { id:"TRANSPT", name:"Transportstyrelsen — Transport Agency", url:"transportstyrelsen.se", freq:"Quarterly", res:"Regional", vars:3, category:"Transport", feeds:"S3 (EV registrations), electric vehicle charging infrastructure density" },
    { id:"RIKSBANK", name:"Riksbank / Swedish Government Office", url:"riksbank.se", freq:"Quarterly", res:"Region", vars:4, category:"Economic", feeds:"E1–E3, economic cycles, business density, industrial concentration" },
    { id:"WINDSE", name:"Swedish Wind Energy Association (Vindkraftföreningen)", url:"vindkraftforeningen.se", freq:"Monthly", res:"Regional", vars:5, category:"Transition", feeds:"S1 (RE capacity), wind capacity by region, curtailment data, western wind corridor" },
    { id:"ENERGIMYN", name:"Energimyndigheten (Swedish Energy Agency)", url:"energimyndigheten.se", freq:"Annual", res:"Region", vars:3, category:"Transition", feeds:"S1 (DER/distributed generation penetration), energy efficiency metrics" },
    { id:"DISTRIBUTOR", name:"Distribution Companies (E.ON, Vattenfall, Fortum, Helen)", url:"", freq:"Annual", res:"Distribution Company", vars:4, category:"Grid", feeds:"S1 variant (thermal plant load), CAPEX, SAIDI/SAIFI, transformer inventories" },
    { id:"POST", name:"Post- och Telestyrelsen / Digital Network Authority", url:"pts.se", freq:"Annual", res:"Kommun", vars:2, category:"Infrastructure", feeds:"Infrastructure density proxy, remote-area identification for Arctic restoration speed" },
    { id:"SMHI_CLIMATE", name:"Climate Adaptation Centre / Lantmäteriet", url:"lantmateriet.se", freq:"Annual", res:"Regional", vars:4, category:"Environment", feeds:"I5 (winter storm + flooding hazard mapping), climate adaptation data, forest fire risk" },
    { id:"WORLDBANK", name:"World Bank / OECD", url:"", freq:"Annual", res:"National", vars:4, category:"Socio-Econ", feeds:"International benchmarks, Nordic socio-economic indicators, renewable energy transition" },
    { id:"SOLARGIS", name:"SolarGIS — Global Solar Atlas", url:"globalsolaratlas.info", freq:"Static", res:"Global", vars:2, category:"Transition", feeds:"T1 (solar resource mapping), solar irradiance (GHI, DNI) for southern Sweden" },
    { id:"ARCTICMONITOR", name:"Arctic Monitoring & Assessment Programme", url:"amap.no", freq:"Annual", res:"Regional", vars:3, category:"Climate", feeds:"I6 (Arctic corrosion class), permafrost thaw zones, extreme weather baselines" },
    { id:"VATTENBEHOV", name:"SMHI Water Data / Vattendirektoratet", url:"vattendirektoratet.se", freq:"Quarterly", res:"Watershed", vars:4, category:"Hazard", feeds:"I5 (winter flooding, spring snowmelt hazard), water level monitoring, stream flow" },
    { id:"MILJOE", name:"Environmental Permit Register (Miljöbalken)", url:"naturvardsverket.se", freq:"Annual", res:"Kommun", vars:3, category:"Environment", feeds:"I6 (environmental exposure), pollution data, industrial sites" },
    { id:"SKNOPEN", name:"Svenska kraftnät Open Data — Real-time Production", url:"svk.se/api", freq:"Real-time", res:"Substation", vars:5, category:"Grid", feeds:"C1 variant (frequency stability), production mix, demand forecasts" },
    { id:"SLU", name:"SLU — Swedish University of Agricultural Sciences", url:"slu.se", freq:"Annual", res:"Regional", vars:3, category:"Environment", feeds:"Forest cover impact on ice/snow loading, vegetation index, land use constraints" },
    { id:"DNO_REPORTS", name:"DNO Reports — Distribution Network Companies", url:"", freq:"Annual", res:"Distribution Area", vars:4, category:"Grid", feeds:"SAIDI/SAIFI by company, winter storm restoration metrics, CAIDI by geography" },
    { id:"SMHI_HIST", name:"SMHI / State Weather Archive", url:"smhi.se", freq:"Monthly", res:"Station", vars:3, category:"Climate", feeds:"Historical winter storm severity index, snow accumulation records, Arctic wind patterns" },
    { id:"SKATTEV", name:"Skatteverket / Swedish Tax Agency", url:"skatteverket.se", freq:"Annual", res:"Kommun", vars:3, category:"Socio-Econ", feeds:"E2 (population served), demographic shifts, remote region identification" },
    { id:"KLIM_RESILIENCE", name:"Ministry of Enterprise — Nordic Resilience", url:"regeringen.se", freq:"Annual", res:"Regional", vars:2, category:"Environment", feeds:"Arctic thermal preservation baseline, permafrost stability data" }
  ],

  /* ── 6 components · 20 metrics ── */
  COMPONENTS: [
    {
      id:"C", name:"Continuity", weight:0.30, color:"#941914",
      desc:"Measures reliability and outage exposure — how often and how long power interruptions occur.",
      metrics:[
        { id:"C1", name:"Outage Duration (SAIDI)", intra:0.35, global:0.105, norm:"A (P5/P95)", source:"Svenska kraftnät / Energimarknadsinspektionen", desc:"Total annual interruption duration per customer", inverted:false, adaptive:false, isNew:false },
        { id:"C2", name:"Outage Frequency (SAIFI)", intra:0.30, global:0.090, norm:"A (P5/P95)", source:"Svenska kraftnät / Energimarknadsinspektionen", desc:"Number of sustained interruptions per customer per year", inverted:false, adaptive:false, isNew:false },
        { id:"C3", name:"Restoration Time (CAIDI)", intra:0.20, global:0.060, norm:"A (P5/P95)", source:"Energimarknadsinspektionen / DSO", desc:"Average duration of each interruption (winter storm recovery time critical)", inverted:false, adaptive:false, isNew:false },
        { id:"C4", name:"Momentary Interruptions (MAIFI)", intra:0.15, global:0.045, norm:"A (P5/P95)", source:"Svenska kraftnät", desc:"Momentary average interruption frequency index", inverted:false, adaptive:false, isNew:false }
      ]
    },
    {
      id:"V", name:"Voltage Quality", weight:0.10, color:"#aa4234",
      desc:"Captures voltage stability, power factor, and harmonic distortion at the distribution level.",
      metrics:[
        { id:"V1", name:"Voltage Deviation (ΔV)", intra:0.40, global:0.040, norm:"A (P5/P95)", source:"Energimarknadsinspektionen / DSO", desc:"Percentage deviation from nominal voltage", inverted:false, adaptive:false, isNew:false },
        { id:"V2", name:"THD (Harmonic Distortion)", intra:0.30, global:0.030, norm:"A (P5/P95)", source:"Energimarknadsinspektionen", desc:"Total harmonic distortion percentage", inverted:false, adaptive:false, isNew:false },
        { id:"V3", name:"Power Factor", intra:0.30, global:0.030, norm:"B (inverse)", source:"Energimarknadsinspektionen / DSO", desc:"Ratio of real to apparent power — higher is better", inverted:true, adaptive:false, isNew:false }
      ]
    },
    {
      id:"I", name:"Infrastructure", weight:0.25, color:"#5d8563",
      desc:"Assesses physical asset condition, age, capacity, winter storm/snow loading exposure (critical for Sweden).",
      metrics:[
        { id:"I1", name:"Asset Age Index", intra:0.12, global:0.030, norm:"A (P5/P95)", source:"Energimarknadsinspektionen / SCB", desc:"Fleet-normalised average asset age", inverted:false, adaptive:false, isNew:false },
        { id:"I2", name:"Capacity Utilisation", intra:0.12, global:0.030, norm:"A (P5/P95)", source:"Svenska kraftnät / Energimarknadsinspektionen", desc:"Percentage of rated capacity in use", inverted:false, adaptive:false, isNew:false },
        { id:"I3", name:"Climate IRI (Thermal + Winter Storm Stress)", intra:0.12, global:0.030, norm:"A (P5/P95)", source:"SMHI / Naturvårdsverket / ERA5", desc:"Infrastructure Risk Index based on extreme cold, winter storms, and Nordic wind events", inverted:false, adaptive:true, isNew:false },
        { id:"I4", name:"Graph Degree (Topology)", intra:0.12, global:0.030, norm:"B (inverse)", source:"OSM / Svenska kraftnät", desc:"Number of connections — higher degree = more redundancy", inverted:true, adaptive:false, isNew:false },
        { id:"I5", name:"Winter Storm + Flooding Hazard", intra:0.18, global:0.045, norm:"A (P5/P95)", source:"SMHI / SGU / SMHI Water", desc:"Combined winter storm severity + spring snowmelt/flood hazard (critical for Sweden)", inverted:false, adaptive:false, isNew:false },
        { id:"I6", name:"Corrosion Class (Arctic)", intra:0.10, global:0.025, norm:"D (categorical)", source:"ISO9223 / ARCTICMONITOR", desc:"Environmental corrosion exposure adapted for Nordic conditions, salt spray, and extreme humidity", inverted:false, adaptive:false, isNew:false, categorical:true },
        { id:"I7", name:"Snow/Ice Loading Zone", intra:0.12, global:0.030, norm:"D (categorical)", source:"Naturvårdsverket / SGU / SMHI", desc:"Snow/ice accumulation hazard mapping for overhead transmission lines", inverted:false, adaptive:true, isNew:false, categorical:true },
        { id:"I8", name:"N-1 Compliance", intra:0.05, global:0.0125, norm:"C (binary)", source:"Svenska kraftnät", desc:"Whether substation meets N-1 redundancy standard (Svenska kraftnät 400kV backbone)", inverted:true, adaptive:false, isNew:false },
        { id:"I9", name:"Nuclear Concentration Risk", intra:0.07, global:0.0175, norm:"D (categorical)", source:"SSM", desc:"Concentration risk for substations supplying or near Forsmark + Ringhals + Barsebäck nuclear plants (33% of Swedish baseload)", inverted:false, adaptive:false, isNew:true, categorical:true }
      ]
    },
    {
      id:"E", name:"Economic", weight:0.10, color:"#3b9eff",
      desc:"Links grid risk to regional economic exposure — energy pricing, employment, and industrial cycles.",
      metrics:[
        { id:"E1", name:"Energy Price Index + Thermal Cycle", intra:0.40, global:0.040, norm:"A (P5/P95)", source:"Riksbank / Energimarknadsinspektionen", desc:"Wholesale + retail electricity cost per MWh, modulated by thermal generation + hydropower cycles", inverted:false, adaptive:true, isNew:false },
        { id:"E2", name:"Population Served + Remote Sparsity", intra:0.30, global:0.030, norm:"A (P5/P95)", source:"SCB / Eurostat", desc:"Kommun-level population served, with penalty for remote Nordic communities", inverted:false, adaptive:false, isNew:false },
        { id:"E3", name:"Business Density + Industrial Concentration", intra:0.30, global:0.030, norm:"A (P5/P95)", source:"Swedish Energy Agency / SCB / Energimarknadsinspektionen", desc:"Economic activity clusters and large industrial load concentration (steel mills, mining)", inverted:false, adaptive:false, isNew:false }
      ]
    },
    {
      id:"S", name:"Saturation", weight:0.20, color:"#b88f3e",
      desc:"Quantifies DER/RE penetration stress, reverse power flow risk, and EV charging load on the grid.",
      metrics:[
        { id:"S1", name:"Renewable Energy Capacity Ratio", intra:0.35, global:0.070, norm:"A (P5/P95)", source:"Swedish Wind Energy Assoc. / Svenska kraftnät / Energimarknadsinspektionen", desc:"Total installed RE (wind/hydro/solar) capacity relative to substation rating", inverted:false, adaptive:false, isNew:false },
        { id:"S2", name:"RE Stress Index (Variability + Curtailment)", intra:0.35, global:0.070, norm:"A (P5/P95)", source:"Swedish Wind Energy Assoc. / Svenska kraftnät", desc:"Composite stress: RE penetration × output variability × transmission constraints (wind-dominated western region)", inverted:false, adaptive:true, isNew:false },
        { id:"S3", name:"EV Penetration Rate (Emerging)", intra:0.30, global:0.060, norm:"A (P5/P95)", source:"Transportstyrelsen / Transport Ministry", desc:"EV registrations as percentage of total fleet in catchment area (growing penetration in urban areas)", inverted:false, adaptive:false, isNew:true }
      ]
    },
    {
      id:"T", name:"Energy Transition", weight:0.05, color:"#0e7490", isNew:true,
      desc:"Measures clean energy transition pace and grid readiness for decarbonisation (RE targets: 100% by 2040).",
      metrics:[
        { id:"T1", name:"Renewable Energy Share (%)", intra:0.50, global:0.025, norm:"B (inverse)", source:"Swedish Wind Energy Assoc. / Svenska kraftnät / Energimarknadsinspektionen", desc:"Share of generation from renewables — higher share = lower risk (inverted)", inverted:true, adaptive:false, isNew:false },
        { id:"T2", name:"Transition Readiness Score", intra:0.50, global:0.025, norm:"A (P5/P95)", source:"Energimarknadsinspektionen / Swedish Wind Energy Assoc. / Svenska kraftnät", desc:"Composite readiness: grid flexibility + storage deployment + DSO interconnection capacity", inverted:true, adaptive:false, isNew:true }
      ]
    }
  ],

  /* ── 7 modifiers (R2–R7, incl. R6a + R6b winter storm/snow loading) ── */
  MODIFIERS: [
    { id:"R2", name:"Adaptive Climate IRI + Nordic Hazard Trajectory", range:"Weight redistribution", type:"Weight modifier", desc:"Uses CMIP6 SSP2-4.5 projections to adjust IRI metrics for winter storm risk, snow loading exposure, and extreme Nordic weather. When local winter storm risk is elevated, weight shifts to structural metrics. Incorporates SMHI weather forecasts and Naturvårdsverket ice/snow mapping.", formula:"IRI_forward(m,s) = IRI_current(m,s) × (1 + 0.15 × clip(Δ_climate, −0.50, +1.00))", sources:["SMHI","Naturvårdsverket","COPERNICUS ERA5","SGU"], isEnhanced:true },
    { id:"R3", name:"Consequence + Nordic Remoteness + Population Sparsity", range:"[0.70, 1.35]", type:"Multiplicative", desc:"Amplifies risk for communities with sparse population, Nordic remoteness, or high energy dependency. Includes vulnerability indices (SCB demographics), exposure in northern regions, and isolation metrics.", formula:"C_mult = sigmoid(pop_weight × remote_weight × V_socio × nordic_factor)", sources:["SCB","EUROSTAT","Post- och Telestyrelsen"], isEnhanced:true },
    { id:"R4", name:"Graph Criticality + Network Constraint", range:"[0.80, 1.40]", type:"Multiplicative", desc:"Penalises topological bottlenecks in Svenska kraftnät 400kV backbone and DSO networks: high betweenness centrality, bridge nodes, low degree. Built from OSM power graph and Svenska kraftnät transmission constraints.", formula:"F_topo = f(degree, BC_percentile, is_bridge, skn_tier)", sources:["OSM","Svenska kraftnät"], isEnhanced:true },
    { id:"R6a", name:"Restoration Speed (Winter Storm Focus)", range:"[0.90, 1.10]", type:"Multiplicative", desc:"Energimarknadsinspektionen-CAIDI-based: rewards fast-restoring areas, penalises slow ones in northern regions. Two substations with identical SAIDI can have different risk profiles based on restoration speed in remote northern areas.", formula:"R6a = sigmoid_bounded(CAIDI_local / CAIDI_fleet_median)", sources:["Energimarknadsinspektionen","Svenska kraftnät"], isEnhanced:true },
    { id:"R6b", name:"Winter Storm + Snow Loading Overlay (CRITICAL FOR SWEDEN)", range:"[1.00, 1.25]", type:"Multiplicative", desc:"SMHI winter storm hazard + Naturvårdsverket snow/ice loading overlay. Penalises substations in high-storm zones or heavy snow-loading regions. Integration of real-time SMHI warnings and historical winter event impacts.", formula:"R6b = f(SMHI_storm_percentile, Naturvardsverket_snow_loading, ice_hazard_proximity)", sources:["SMHI","Naturvårdsverket","SGU","SMHI Water"], isEnhanced:true },
    { id:"R7", name:"Digital Readiness + Cyber-Physical Resilience", range:"[0.99, 1.05]", type:"Multiplicative", desc:"Cyber-physical security baseline, SCADA maturity proxy (Sweden high), and microgrid/islanding capability. Indicates digital resilience capability at the grid edge for winter event recovery scenarios.", formula:"Cyber = f(SCADA_maturity, microgrid_pct, islanding_capability)", sources:["Svenska kraftnät","Energimarknadsinspektionen"], isEnhanced:false }
  ],

  /* ── processing pipeline ── */
  PIPELINE: [
    { step:1, name:"Ingest", desc:"95 variables from 30 verified Swedish public data sources — Svenska kraftnät, Energimarknadsinspektionen, SCB, SMHI, SGU, Naturvårdsverket, SSM, and others. Zero proprietary SCADA dependencies. Maximum ingestion frequency: real-time (Svenska kraftnät dispatch data).", icon:"📥" },
    { step:2, name:"Normalise", desc:"Four normalisation methods: Method A (robust fleet percentile P5/P95), Method B (inverse fleet percentile for density), Method C (binary compliance), and Method D (categorical mapping). Inverted metrics for density measures where higher = better resilience.", icon:"📐" },
    { step:3, name:"Weight", desc:"6-level hierarchical weighting across 6 components and 20 metrics. Continuity dominates at 0.30, Infrastructure at 0.25 (with higher winter storm/snow loading I5 weight), Saturation at 0.20. Weight budget validated by Sobol sensitivity analysis.", icon:"⚖️" },
    { step:4, name:"Compose R_base", desc:"Weighted sum of 6 normalised component scores produces the base resilience score.", icon:"🧮" },
    { step:5, name:"Modify", desc:"Seven multiplicative modifiers adjust R_base for Swedish context: R2 (adaptive climate + winter storm trajectory), R3 (consequence + Nordic remoteness + population sparsity), R4 (graph criticality + Svenska kraftnät/DSO constraints), R6a (restoration speed in remote areas), R6b (winter storm/snow loading overlay — CRITICAL), R7 (digital readiness). Plus enrichments for vulnerable populations, winter storm zones, and critical infrastructure.", icon:"🔧" },
    { step:6, name:"Monte Carlo", desc:"10,000 iterations per substation using a 20×20 Gaussian copula correlation matrix. Captures measurement, spatial, staleness, and model uncertainty. Produces median, P5, P95, skewness, and P_critical for each substation.", icon:"🎲" },
    { step:7, name:"Classify", desc:"Four bands: Low (0.00–0.25), Medium (0.25–0.50), High (0.50–0.75), Critical (0.75–1.00). Alert flags trigger when any single component exceeds its P95 fleet threshold. Winter storm/snow events escalate classification instantaneously.", icon:"🏷️" }
  ],

  /* ── classification bands ── */
  CLASSIFICATION: [
    { name:"Low",      range:"0.00 – 0.25", meaning:"Good resilience — stable grid, low exposure",       expected:"~35–40%", color:"#5d8563" },
    { name:"Medium",   range:"0.25 – 0.50", meaning:"Moderate risk — some vulnerabilities present",       expected:"~32–38%", color:"#b88f3e" },
    { name:"High",     range:"0.50 – 0.75", meaning:"Elevated risk — investment priority zone",           expected:"~18–23%", color:"#aa4234" },
    { name:"Critical", range:"0.75 – 1.00", meaning:"Severe vulnerability — urgent intervention required", expected:"~5–10%",   color:"#941914" }
  ],

  /* ── master equation ── */
  MASTER_EQUATION: "R_final = soft_clip_upper( R_base × F_topo × C_mult × R6a_mult × R6b_winter_snow × Cyber_factor )",

  /* ── normalisation methods ── */
  NORM_METHODS: [
    { id:"A", name:"Fleet Percentile (robust)", formula:"N(x) = soft_clip((x − P₅) / (P₉₅ − P₅))", applies:"C1, C2, C3, C4, V1, V2, I1, I2, I3, I5, E1, E2, E3, S1, S2, S3" },
    { id:"B", name:"Fleet Percentile (inverse)", formula:"N(x) = 1 − soft_clip((x − P₅) / (P₉₅ − P₅))", applies:"V3, I4, T1, T2" },
    { id:"C", name:"Binary (bounded)", formula:"N(x) = 0 if compliant, 1 if non-compliant", applies:"I8 (N-1 compliance)" },
    { id:"D", name:"Categorical Mapping", formula:"N(x) = lookup_table(class → [0, 1])", applies:"I6 (Arctic corrosion), I7 (snow/ice loading), I9 (nuclear concentration)" }
  ],

  /* ── 11 data layers · 95 variables ── */
  DATA_LAYERS: [
    { id:"A",   name:"SSI v4.0.2 Resilience (Sweden)",              vars:20, status:"LIVE",    sources:"Svenska kraftnät · Energimarknadsinspektionen · SCB · SMHI · Naturvårdsverket · SSM" },
    { id:"B.1", name:"Grid Telemetry: Open",                       vars:3,  status:"LIVE",    sources:"SMHI / ERA5 · Svenska kraftnät" },
    { id:"B.2", name:"Grid Telemetry: Proxy",                      vars:4,  status:"LIVE",    sources:"IEEE C57.91 · DSO · Energimarknadsinspektionen" },
    { id:"B.3", name:"Grid Telemetry: Fuzzy",                      vars:12, status:"FUZZY",   sources:"IEEE/CIGRÉ standards · SGU" },
    { id:"C",   name:"Socio-Economic + Nordic Demographics",        vars:10, status:"LIVE",    sources:"SCB · EUROSTAT · Riksbank · Swedish Energy Agency" },
    { id:"D",   name:"Environmental Hazards (Winter Storm+Flooding)",vars:8,  status:"LIVE",    sources:"SMHI · Naturvårdsverket · SGU · Copernicus · SMHI Water" },
    { id:"E",   name:"Swedish Open Data + Energy Policy",           vars:9,  status:"LIVE",    sources:"Energimarknadsinspektionen · Swedish Wind Energy · SLU · Swedish Energy Agency" },
    { id:"F",   name:"Network Transitions + Nuclear Baseload",      vars:12, status:"BAYESIAN",sources:"DSO history OR IEEE/CIGRÉ + priors" },
    { id:"G",   name:"Modifier Inputs (Winter Storm-Weighted)",     vars:4,  status:"LIVE",    sources:"Energimarknadsinspektionen reliability · SMHI · OSM" },
    { id:"H",   name:"Network & Topology (Svenska kraftnät 400kV)", vars:7,  status:"LIVE",    sources:"Svenska kraftnät · ENTSO-E · OSM" },
    { id:"I",   name:"Output Scores + Alert Flags",                 vars:7,  status:"LIVE",    sources:"Fleet Markov Chain · IEEE/CIGRÉ analysis" }
  ],

  /* ── validation framework ── */
  VALIDATION_CHECKS: [
    { check:"North–South latitude gradient",                        criterion:"Northern Sweden (Norrland) R systematically higher than southern regions due to winter conditions",                                      status:"expected" },
    { check:"Winter storm–I5 coherence (SMHI)",                     criterion:"Substations in high-storm zones show elevated I5 scores — historical winter events",                                                        status:"expected" },
    { check:"Snow/ice loading–I7 agreement (Naturvårdsverket)",     criterion:"Northern substations with heavy snow loading show elevated I7 scores, especially overhead transmission",                                        status:"expected" },
    { check:"Nuclear concentration–I9 signal (SSM)",                criterion:"Substations near/feeding Forsmark + Ringhals + Barsebäck show elevated I9 scores; 33% baseload concentration",                          status:"expected" },
    { check:"RE stress–wind correlation (western region)",          criterion:"Western coastal regions with high wind penetration show elevated S2 scores",                                                                   status:"expected" },
    { check:"Arctic thermal preservation check",                    criterion:"Permafrost/Arctic stability metrics align with I6 corrosion class and I3 thermal stress",                                                    status:"expected" },
    { check:"Fennoscandian Shield seismic baseline",                criterion:"Seismic risk negligible (α=0.10 relative to European baseline); validation confirms no anomalies",                                          status:"expected" },
    { check:"Spring snowmelt flooding–I5 agreement",                criterion:"Swedish river systems show elevated I5 during spring; SMHI flood forecasts validate",                                                      status:"expected" },
    { check:"RE stress vs EV load correlation",                     criterion:"S2 (RE stress) and S3 (EV penetration) positively correlated in urban areas (Stockholm, Gothenburg, Malmö)",                                 status:"nascent" },
    { check:"Monte Carlo convergence (CV < 2%)",                    criterion:"Coefficient of variation < 2% at 10,000 iterations for all substations",                                                                      status:"expected" },
    { check:"Weight budget unity",                                  criterion:"Component weights sum to 1.0000; all intra-weights sum to 1.0000 per component",                                                              status:"expected" },
    { check:"Modifier range adherence",                             criterion:"All modifiers stay within declared [min, max] bounds across the fleet",                                                                       status:"expected" },
    { check:"Band boundary contiguity",                             criterion:"No gap or overlap between Low/Medium/High/Critical thresholds",                                                                                status:"expected" },
    { check:"R3 consequence signal + remoteness",                   criterion:"High-remoteness, sparse-population areas consistently score higher R3 multiplier (Norrland/northern regions)",                               status:"expected" },
    { check:"R6b winter storm/snow sensitivity (CRITICAL)",         criterion:"Winter storm proximity drives R6b up to 1.25 ceiling; snow loading overlay independent of other modifiers",                                  status:"critical" },
    { check:"Svenska kraftnät vs DSO constraint signal",            criterion:"Svenska kraftnät 400kV backbone substations score higher R4; DSO periphery lower due to topology",                                          status:"expected" }
  ],

  /* ── changelog v3.4 → v4.0.2 (Sweden edition) ── */
  CHANGELOG: [
    { id:"SE1",  change:"Sweden country launch — 3,570 substations across 21 Län, administrative kommun level",                                                type:"new" },
    { id:"SE2",  change:"Integrated Svenska kraftnät transmission dispatch data + Energimarknadsinspektionen reliability benchmarks",                         type:"data" },
    { id:"SE3",  change:"Energimarknadsinspektionen reliability register integrated — SAIDI/SAIFI standardisation for all DSOs",                             type:"data" },
    { id:"SE4",  change:"SMHI winter storm hazard integrated — critical for Nordic/boreal climate exposure assessment",                                       type:"data" },
    { id:"SE5",  change:"Naturvårdsverket snow/ice loading mapping integrated — overhead transmission line vulnerability in north",                           type:"data" },
    { id:"SE6",  change:"SSM nuclear concentration risk indicator — Forsmark + Ringhals + Barsebäck baseload (33% of Swedish generation)",                  type:"data" },
    { id:"SE7",  change:"SMHI + Naturvårdsverket climate integration — winter storm risk, snow accumulation, Nordic wind patterns",                           type:"data" },
    { id:"SE8",  change:"SCB Census 2021 + Eurostat socio-economic data integrated — vulnerability indices per kommun",                                      type:"data" },
    { id:"SE9",  change:"Swedish Wind Energy + Swedish Energy Agency data integrated — RE penetration for western/coastal regions",                          type:"data" },
    { id:"SE10", change:"Riksbank thermal cycle coupling integrated — E1 volatility modulation for hydropower-dependent regions",                            type:"new" },
    { id:"SE11", change:"R6b modifier enhanced with dual SMHI winter storm + Naturvårdsverket snow loading hazard (range 1.00–1.25)",                       type:"enhanced" },
    { id:"SE12", change:"R3 consequence enriched with Nordic remoteness, population sparsity, Norrland isolation metrics",                                  type:"enhanced" },
    { id:"SE13", change:"R4 graph criticality rebuilt with Svenska kraftnät 400kV topology + DSO network constraints — transmission corridor penalty",       type:"enhanced" },
    { id:"SE14", change:"I9 Nuclear Concentration Risk — new metric from SSM nuclear safety data for Forsmark + Ringhals + Barsebäck proximity",            type:"new" },
    { id:"SE15", change:"R2 Adaptive IRI now includes CMIP6 SSP2-4.5 forward projections for Nordic winter extremes & permafrost thaw",                      type:"enhanced" }
  ]
};

/* ── Legacy flat structure (backward-compat) ── */
window.SSI_METADATA = window.SSIMetadata;