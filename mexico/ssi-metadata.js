/*  SSI v4.0.2 — Metadata Registry · Mexico
    Loaded by every page in /mexico/.
    ──────────────────────────────────────────────
    Exports:  window.SSIMetadata   (structured, matches Mexico format exactly)
              window.SSI_METADATA  (legacy flat, backward-compat)              */

window.SSIMetadata = {

  /* ── Country metadata ── */
  country: "Mexico",
  code: "MX",
  prefix: "MX_",
  tso: "CENACE (Centro Nacional de Control de Energía)",
  regulator: "CRE (Comisión Reguladora de Energía)",
  statistics: "INEGI (Instituto Nacional de Estadística y Geografía)",
  weather: "SMN (Servicio Meteorológico Nacional)",
  geology: "SGM (Servicio Geológico Mexicano)",
  hazards: "CENAPRED (Centro Nacional de Prevención de Desastres — earthquakes, hurricanes, volcanic activity)",
  admin: { level1: "Estados", level2: "Municipios" },
  currency: { code: "MXN", symbol: "MX$" },

  /* ── 25 verified data sources — Mexican institutions ── */
  DATA_SOURCES: [
    { id:"CENACE", name:"CENACE — Centro Nacional de Control de Energía", url:"cenace.gob.mx", freq:"Real-time", res:"Substation", vars:14, category:"Grid", feeds:"C1–C4, I2, S1–S2, transmission network topology, dispatch data, frequency regulation, regional dispatch centers (Norte, Occidente, Bajío, Centro, Oriente)" },
    { id:"CRE", name:"CRE — Comisión Reguladora de Energía", url:"cre.gob.mx", freq:"Quarterly", res:"DSO", vars:12, category:"Grid", feeds:"C1–C4, V1–V2, I1, reliability metrics SAIDI/SAIFI, technical standards, network quality, distribution permit holders, DSO performance, tariff regulation" },
    { id:"INEGI", name:"INEGI — Instituto Nacional de Estadística y Geografía", url:"inegi.org.mx", freq:"Annual", res:"Municipio", vars:10, category:"Socio-Econ", feeds:"C1–C4, E2–E3, demographics, population served per municipio, income distribution, regional economic data, census data" },
    { id:"SMN", name:"SMN — Servicio Meteorológico Nacional", url:"smn.conagua.gob.mx", freq:"Daily", res:"Station", vars:8, category:"Climate", feeds:"I3 (tropical cyclone + precipitation stress), wind, precipitation, hurricane forecasts, tropical storm warnings, rainfall patterns, flood hazard forecasts" },
    { id:"CENAPRED", name:"CENAPRED — Centro Nacional de Prevención de Desastres", url:"cenapred.gob.mx", freq:"Annual", res:"Grid 0.1°", vars:7, category:"Hazard", feeds:"I5 (seismic + volcanic + flood hazard), earthquake risk mapping, volcanic hazard zones, flood-prone areas, disaster risk assessment, geo-spatial hazard data" },
    { id:"CFE", name:"CFE — Comisión Federal de Electricidad", url:"cfe.mx", freq:"Monthly", res:"Distribution Region", vars:9, category:"Grid", feeds:"C1–C4, S1–S2, distribution infrastructure, network topology, generation capacity, transmission corridors, transformer inventories, restoration metrics" },
    { id:"SENER", name:"SENER — Secretaría de Energía", url:"gob.mx/sener", freq:"Annual", res:"National", vars:4, category:"Transition", feeds:"T1–T2, energy policy, PRODESEN (grid planning), RE targets, energy transition programs, capacity auctions, strategic energy planning" },
    { id:"SEMARNAT", name:"SEMARNAT — Secretaría de Medio Ambiente", url:"gob.mx/semarnat", freq:"Annual", res:"Municipio", vars:5, category:"Environment", feeds:"I5–I6 (environmental hazards), pollution data, protected areas, deforestation monitoring, water availability, environmental risk zones" },
    { id:"CONUEE", name:"CONUEE — Comisión Nacional para el Uso Eficiente de la Energía", url:"gob.mx/conuee", freq:"Annual", res:"Regional", vars:3, category:"Transition", feeds:"S1 variant (energy efficiency programs), demand-side management, industrial efficiency metrics, building codes, EE certification data" },
    { id:"SGM", name:"SGM — Servicio Geológico Mexicano", url:"sgm.gob.mx", freq:"Annual", res:"Grid 0.1°", vars:6, category:"Hazard", feeds:"I5–I6 (geological hazards, soil stability), geological mapping, seismic faults, volcanic activity zones, soil composition, landslide risk, mineral resources" },
    { id:"CONEVAL", name:"CONEVAL — Consejo Nacional de Evaluación", url:"coneval.org.mx", freq:"Biennial", res:"Municipio", vars:4, category:"Socio-Econ", feeds:"E2–E3, poverty indices, social development metrics, vulnerability assessment, socio-economic stratification per municipio" },
    { id:"Banxico", name:"Banco de México — Central Bank", url:"banxico.org.mx", freq:"Quarterly", res:"National", vars:3, category:"Economic", feeds:"E1–E3, economic cycles, inflation, interest rates, energy price indices, industrial production" },
    { id:"CONAGUA", name:"CONAGUA — Comisión Nacional del Agua", url:"gob.mx/conagua", freq:"Monthly", res:"Watershed", vars:5, category:"Hazard", feeds:"I5 (flood risk, water scarcity), precipitation forecasts, water availability, flood-prone municipalities, reservoir levels, drought warnings, water infrastructure" },
    { id:"OSM", name:"OpenStreetMap — Power Infrastructure", url:"openstreetmap.org", freq:"Continuous", res:"Node", vars:8, category:"Infrastructure", feeds:"I4 (graph degree, topology), ~3,140 substations mapped across 32 Estados, transmission + distribution networks, infrastructure nodes" },
    { id:"COPERNICUS", name:"Copernicus ERA5 — Climate Reanalysis", url:"climate.copernicus.eu", freq:"Monthly", res:"Grid 0.25°", vars:6, category:"Climate", feeds:"Tropical cyclone risk, precipitation patterns, wind patterns, temperature anomalies, climate projections for Mexico region" },
    { id:"AEMO_CFE", name:"AEMO/CFE Generation Data — Capacity + Output", url:"cfe.mx", freq:"Real-time", res:"Power Plant", vars:5, category:"Grid", feeds:"C1–C2, S1–S2, generation capacity by fuel type (coal, gas, hydro, wind, solar), plant dispatch, renewable output, grid constraint data" },
    { id:"PRODESEN", name:"PRODESEN — Programa de Desarrollo del SEN (Grid Planning)", url:"gob.mx/sener", freq:"Annual", res:"Regional", vars:4, category:"Transition", feeds:"T1–T2, 15-year grid planning, capacity expansion targets, renewable integration, transmission investment requirements, demand forecasts" },
    { id:"INEEL", name:"INEEL — Instituto Nacional de Electricidad y Energías Limpias", url:"ineel.mx", freq:"Annual", res:"Regional", vars:3, category:"Research", feeds:"T1–T2, renewable energy research, grid modernization studies, energy efficiency data, technology assessment" },
    { id:"IMTA", name:"IMTA — Instituto Mexicano de Tecnología del Agua", url:"imta.gob.mx", freq:"Annual", res:"Watershed", vars:3, category:"Water", feeds:"I5 (hydro asset condition, water availability), hydroelectric generation capacity, water resource management, dam operational data" },
    { id:"SSA", name:"SSA — Secretaría de Salud", url:"gob.mx/salud", freq:"Annual", res:"Municipio", vars:2, category:"Socio-Econ", feeds:"E2–E3 (health vulnerability), health infrastructure distribution, disease/epidemic exposure, vulnerable populations" },
    { id:"CONAPO", name:"CONAPO — Consejo Nacional de Población", url:"gob.mx/conapo", freq:"Annual", res:"Municipio", vars:3, category:"Demographics", feeds:"E2 (population dynamics), demographic projections, migration patterns, population concentration, urban growth forecasts" },
    { id:"SAT", name:"SAT — Servicio de Administración Tributaria", url:"sat.gob.mx", freq:"Annual", res:"Municipio", vars:2, category:"Economic", feeds:"E3 (economic activity), business registrations, industrial activity, tax-based economic indicators" },
    { id:"PEMEX", name:"PEMEX — Petróleos Mexicanos", url:"pemex.gob.mx", freq:"Monthly", res:"Regional", vars:3, category:"Energy", feeds:"S1 variant (natural gas infrastructure overlap with electricity), gas supply security, fuel costs, energy corridor planning" },
    { id:"ASEA", name:"ASEA — Agencia de Seguridad, Energía y Ambiente", url:"gob.mx/asea", freq:"Annual", res:"Infrastructure Site", vars:2, category:"Safety", feeds:"I1 (asset safety compliance), industrial safety inspections, hazardous site proximity, accident risk assessment" },
    { id:"SE", name:"SE — Secretaría de Economía", url:"gob.mx/se", freq:"Annual", res:"Municipio", vars:2, category:"Economic", feeds:"E3 (industrial concentration), manufacturing centers, export zone mapping, industrial cluster data, economic development programs" }
  ],

  /* ── 6 components · 20 metrics ── */
  COMPONENTS: [
    {
      id:"C", name:"Continuity", weight:0.30, color:"#941914",
      desc:"Measures reliability and outage exposure — how often and how long power interruptions occur, accounting for Mexico's tropical cyclone, seismic, and hydro hazard exposure.",
      metrics:[
        { id:"C1", name:"Outage Duration (SAIDI)", intra:0.35, global:0.105, norm:"A (P5/P95)", source:"CENACE / CRE", desc:"Total annual interruption duration per customer", inverted:false, adaptive:false, isNew:false },
        { id:"C2", name:"Outage Frequency (SAIFI)", intra:0.30, global:0.090, norm:"A (P5/P95)", source:"CENACE / CRE", desc:"Number of sustained interruptions per customer per year", inverted:false, adaptive:false, isNew:false },
        { id:"C3", name:"Restoration Time (CAIDI)", intra:0.20, global:0.060, norm:"A (P5/P95)", source:"CRE / CFE", desc:"Average duration of each interruption (tropical cyclone recovery time critical)", inverted:false, adaptive:false, isNew:false },
        { id:"C4", name:"Momentary Interruptions (MAIFI)", intra:0.15, global:0.045, norm:"A (P5/P95)", source:"CENACE", desc:"Momentary average interruption frequency index", inverted:false, adaptive:false, isNew:false }
      ]
    },
    {
      id:"V", name:"Voltage Quality", weight:0.10, color:"#aa4234",
      desc:"Captures voltage stability, power factor, and harmonic distortion at the distribution level.",
      metrics:[
        { id:"V1", name:"Voltage Deviation (ΔV)", intra:0.40, global:0.040, norm:"A (P5/P95)", source:"CRE / CFE", desc:"Percentage deviation from nominal voltage", inverted:false, adaptive:false, isNew:false },
        { id:"V2", name:"THD (Harmonic Distortion)", intra:0.30, global:0.030, norm:"A (P5/P95)", source:"CRE", desc:"Total harmonic distortion percentage", inverted:false, adaptive:false, isNew:false },
        { id:"V3", name:"Power Factor", intra:0.30, global:0.030, norm:"B (inverse)", source:"CRE / CFE", desc:"Ratio of real to apparent power — higher is better", inverted:true, adaptive:false, isNew:false }
      ]
    },
    {
      id:"I", name:"Infrastructure", weight:0.25, color:"#5d8563",
      desc:"Assesses physical asset condition, age, capacity, and Mexico-specific hazards: tropical cyclones, earthquakes, volcanic activity, flooding, seismic risk (critical for Mexican grid vulnerability).",
      metrics:[
        { id:"I1", name:"Asset Age Index", intra:0.12, global:0.030, norm:"A (P5/P95)", source:"CRE / INEGI", desc:"Fleet-normalised average asset age", inverted:false, adaptive:false, isNew:false },
        { id:"I2", name:"Capacity Utilisation", intra:0.12, global:0.030, norm:"A (P5/P95)", source:"CENACE / CRE", desc:"Percentage of rated capacity in use", inverted:false, adaptive:false, isNew:false },
        { id:"I3", name:"Climate IRI (Tropical Cyclone + Precipitation Stress)", intra:0.12, global:0.030, norm:"A (P5/P95)", source:"SMN / CENAPRED / ERA5", desc:"Infrastructure Risk Index based on tropical cyclone hazard, rainfall intensity, storm surge risk in coastal regions", inverted:false, adaptive:true, isNew:false },
        { id:"I4", name:"Graph Degree (Topology)", intra:0.12, global:0.030, norm:"B (inverse)", source:"OSM / CENACE", desc:"Number of connections — higher degree = more redundancy", inverted:true, adaptive:false, isNew:false },
        { id:"I5", name:"Seismic + Volcanic + Flood Hazard Index", intra:0.18, global:0.045, norm:"A (P5/P95)", source:"CENAPRED / SGM / CONAGUA", desc:"Combined seismic risk + volcanic hazard zones + flood-prone area exposure (critical for Mexico)", inverted:false, adaptive:false, isNew:false },
        { id:"I6", name:"Corrosion Class (Coastal + Industrial Pollution)", intra:0.10, global:0.025, norm:"D (categorical)", source:"ISO9223 / SEMARNAT / SMN", desc:"Environmental corrosion exposure adapted for tropical coastal zones and industrial pollution: C4–C5 coastal, C3–C4 industrial areas, C2 interior", inverted:false, adaptive:false, isNew:false, categorical:true },
        { id:"I7", name:"Wind Loading + Tropical Cyclone Exposure", intra:0.12, global:0.030, norm:"D (categorical)", source:"CENAPRED / SGM / SMN", desc:"Tropical cyclone wind hazard mapping and hurricane exposure zones (critical for overhead transmission lines in vulnerable regions)", inverted:false, adaptive:true, isNew:false, categorical:true },
        { id:"I8", name:"N-1 Compliance", intra:0.05, global:0.0125, norm:"C (binary)", source:"CENACE", desc:"Whether substation meets N-1 redundancy standard (CENACE transmission backbone)", inverted:true, adaptive:false, isNew:false },
        { id:"I9", name:"Renewable Energy Capacity Concentration Risk", intra:0.07, global:0.0175, norm:"D (categorical)", source:"SENER / CENACE", desc:"Concentration risk for substations supplying or dependent on major renewable farms (wind, solar) — high in northern corridor", inverted:false, adaptive:false, isNew:true, categorical:true }
      ]
    },
    {
      id:"E", name:"Economic", weight:0.10, color:"#3b9eff",
      desc:"Links grid risk to regional economic exposure — energy pricing, employment, industrial clusters, and renewable energy investment cycles.",
      metrics:[
        { id:"E1", name:"Energy Price Index + RE Cycle", intra:0.40, global:0.040, norm:"A (P5/P95)", source:"Banxico / CENACE / CRE", desc:"Wholesale + retail electricity cost per MWh, modulated by renewable availability and fuel cost cycles", inverted:false, adaptive:true, isNew:false },
        { id:"E2", name:"Population Served + Urban Concentration", intra:0.30, global:0.030, norm:"A (P5/P95)", source:"INEGI / CONAPO", desc:"Municipio-level population served, with penalty for Mexico City concentration and high-density urban areas", inverted:false, adaptive:false, isNew:false },
        { id:"E3", name:"Business Density + Industrial Concentration", intra:0.30, global:0.030, norm:"A (P5/P95)", source:"CENACE / INEGI / SAT / SE", desc:"Economic activity clusters, industrial zones, and large manufacturing load concentration (automotive, petrochemicals, mining)", inverted:false, adaptive:false, isNew:false }
      ]
    },
    {
      id:"S", name:"Saturation", weight:0.20, color:"#b88f3e",
      desc:"Quantifies DER/RE penetration stress, solar/wind variability, reverse power flow risk, and EV charging load on the grid.",
      metrics:[
        { id:"S1", name:"Renewable Energy Capacity Ratio", intra:0.35, global:0.070, norm:"A (P5/P95)", source:"SENER / CENACE / INEEL", desc:"Total installed RE (wind/solar) capacity relative to substation rating (growing wind baseline in Norte/Bajío regions, solar expansion)", inverted:false, adaptive:false, isNew:false },
        { id:"S2", name:"RE Stress Index (Wind + Solar Variability)", intra:0.35, global:0.070, norm:"A (P5/P95)", source:"SENER / CENACE", desc:"Composite stress: RE penetration × wind variability × solar output variability × transmission constraints (northern wind corridor volatility)", inverted:false, adaptive:true, isNew:false },
        { id:"S3", name:"EV Penetration Rate (Emerging)", intra:0.30, global:0.060, norm:"A (P5/P95)", source:"SE / INEGI", desc:"EV registrations as percentage of total fleet in catchment area (growing penetration in urban areas Mexico City, Guadalajara, Monterrey)", inverted:false, adaptive:false, isNew:true }
      ]
    },
    {
      id:"T", name:"Energy Transition", weight:0.05, color:"#0e7490", isNew:true,
      desc:"Measures clean energy transition pace and grid readiness for decarbonisation (RE targets: increasing solar/wind, grid modernization priority).",
      metrics:[
        { id:"T1", name:"Renewable Energy Share (%)", intra:0.50, global:0.025, norm:"B (inverse)", source:"SENER / CENACE / INEEL", desc:"Share of generation from renewables — higher share = lower risk (inverted, growing wind + solar baseline, PRODESEN targets)", inverted:true, adaptive:false, isNew:false },
        { id:"T2", name:"Transition Readiness Score", intra:0.50, global:0.025, norm:"A (P5/P95)", source:"CENACE / SENER / INEEL", desc:"Composite readiness: grid flexibility + battery storage capacity + DSO interconnection capability + renewable integration + demand-side flexibility", inverted:true, adaptive:false, isNew:true }
      ]
    }
  ],

  /* ── 5 modifiers (R2–R7 adapted for Mexico) ── */
  MODIFIERS: [
    { id:"R2", name:"Adaptive Climate IRI + Tropical Cyclone Hazard Trajectory", range:"Weight redistribution", type:"Weight modifier", desc:"Uses regional climate projections to adjust IRI metrics for tropical cyclone risk, flooding, and seismic exposure. When local cyclone/flood/seismic risk is elevated, weight shifts to structural metrics. Incorporates SMN forecasts and CENAPRED hazard mapping.", formula:"IRI_forward(m,s) = IRI_current(m,s) × (1 + 0.15 × clip(Δ_climate, −0.50, +1.00))", sources:["SMN","CENAPRED","COPERNICUS ERA5","SGM"], isEnhanced:true },
    { id:"R3", name:"Consequence + Urban Concentration + Socio-Economic Vulnerability", range:"[0.70, 1.35]", type:"Multiplicative", desc:"Amplifies risk for high-density urban areas (Mexico City, Guadalajara, Monterrey), economically vulnerable communities, or regions with high poverty indices. Includes vulnerability indices (CONEVAL, INEGI demographics) and socio-economic stratification.", formula:"C_mult = sigmoid(pop_weight × urban_weight × V_socio × poverty_factor)", sources:["INEGI","CONEVAL","CONAPO"], isEnhanced:true },
    { id:"R4", name:"Graph Criticality + Network Constraint", range:"[0.80, 1.40]", type:"Multiplicative", desc:"Penalises topological bottlenecks in CENACE transmission backbone and CFE distribution networks: high betweenness centrality, bridge nodes, low degree. Built from OSM power graph and CENACE transmission constraints, with special attention to critical regional dispatch centres.", formula:"F_topo = f(degree, BC_percentile, is_bridge, regional_dispatch_exposure)", sources:["OSM","CENACE"], isEnhanced:true },
    { id:"R6a", name:"Restoration Speed (Tropical Cyclone + Seismic Focus)", range:"[0.90, 1.10]", type:"Multiplicative", desc:"CRE-CAIDI-based: rewards fast-restoring areas, penalises slow ones in cyclone/seismic-vulnerable regions. Two substations with identical SAIDI can have different risk profiles based on restoration speed in tropical or seismic hazard zones.", formula:"R6a = sigmoid_bounded(CAIDI_local / CAIDI_fleet_median)", sources:["CRE","CENACE"], isEnhanced:true },
    { id:"R6b", name:"Tropical Cyclone + Seismic + Flood Hazard Overlay (CRITICAL FOR MEXICO)", range:"[1.00, 1.25]", type:"Multiplicative", desc:"SMN tropical cyclone hazard + CENAPRED seismic/volcanic/flood risk. Penalises substations in high-cyclone zones, seismic fault lines, volcanic hazard areas, or flood-prone corridors. Integration of real-time SMN warnings and historical event impacts. Cyclones, earthquakes, and floods are major Mexican grid threats.", formula:"R6b = f(SMN_cyclone_percentile, CENAPRED_seismic_zone, SGM_volcanic_hazard, CONAGUA_flood_proximity)", sources:["SMN","CENAPRED","SGM","CONAGUA"], isEnhanced:true },
    { id:"R7", name:"Digital Readiness + Cyber-Physical Resilience", range:"[0.99, 1.05]", type:"Multiplicative", desc:"Cyber-physical security baseline, SCADA maturity (Mexico modernizing), and microgrid/islanding capability. Indicates digital resilience capability at the grid edge for cyclone/seismic recovery scenarios and critical infrastructure security.", formula:"Cyber = f(SCADA_maturity, microgrid_pct, islanding_capability, security_baseline)", sources:["CENACE","CRE","ASEA"], isEnhanced:false }
  ],

  /* ── processing pipeline ── */
  PIPELINE: [
    { step:1, name:"Ingest", desc:"95 variables from 25 verified Mexican public data sources — CENACE, CRE, CFE, INEGI, SMN, CENAPRED, SENER, SEMARNAT, and others. Zero proprietary SCADA dependencies. Maximum ingestion frequency: real-time (CENACE dispatch data).", icon:"📥" },
    { step:2, name:"Normalise", desc:"Four normalisation methods: Method A (robust fleet percentile P5/P95), Method B (inverse fleet percentile for density), Method C (binary compliance), and Method D (categorical mapping). Inverted metrics for density measures where higher = better resilience.", icon:"📐" },
    { step:3, name:"Weight", desc:"6-level hierarchical weighting across 6 components and 20 metrics. Continuity dominates at 0.30, Infrastructure at 0.25 (with higher tropical cyclone/seismic/flood I5 weight), Saturation at 0.20. Weight budget validated by Sobol sensitivity analysis.", icon:"⚖️" },
    { step:4, name:"Compose R_base", desc:"Weighted sum of 6 normalised component scores produces the base resilience score.", icon:"🧮" },
    { step:5, name:"Modify", desc:"Five multiplicative modifiers adjust R_base for Mexican context: R2 (adaptive climate + tropical cyclone hazard trajectory), R3 (consequence + urban concentration + socio-economic vulnerability + poverty indices), R4 (graph criticality + CENACE/CFE constraints), R6a (restoration speed in cyclone/seismic zones), R6b (tropical cyclone/seismic/flood overlay — CRITICAL), R7 (digital readiness). Plus enrichments for vulnerable populations, disaster-prone zones, and critical renewable infrastructure.", icon:"🔧" },
    { step:6, name:"Monte Carlo", desc:"10,000 iterations per substation using a 20×20 Gaussian copula correlation matrix. Captures measurement, spatial, staleness, and model uncertainty. Produces median, P5, P95, skewness, and P_critical for each substation.", icon:"🎲" },
    { step:7, name:"Classify", desc:"Four bands: Low (0.00–0.25), Medium (0.25–0.50), High (0.50–0.75), Critical (0.75–1.00). Alert flags trigger when any single component exceeds its P95 fleet threshold. Tropical cyclone/seismic/flood events escalate classification instantaneously.", icon:"🏷️" }
  ],

  /* ── classification bands ── */
  CLASSIFICATION: [
    { name:"Low",      range:"0.00 – 0.25", meaning:"Good resilience — stable grid, low exposure",       expected:"~35–40%", color:"#5d8563" },
    { name:"Medium",   range:"0.25 – 0.50", meaning:"Moderate risk — some vulnerabilities present",       expected:"~32–38%", color:"#b88f3e" },
    { name:"High",     range:"0.50 – 0.75", meaning:"Elevated risk — investment priority zone",           expected:"~18–23%", color:"#aa4234" },
    { name:"Critical", range:"0.75 – 1.00", meaning:"Severe vulnerability — urgent intervention required", expected:"~5–10%",   color:"#941914" }
  ],

  /* ── master equation ── */
  MASTER_EQUATION: "R_final = soft_clip_upper( R_base × F_topo × C_mult × R6a_mult × R6b_tropical_cyclone_seismic_flood × Cyber_factor )",

  /* ── normalisation methods ── */
  NORM_METHODS: [
    { id:"A", name:"Fleet Percentile (robust)", formula:"N(x) = soft_clip((x − P₅) / (P₉₅ − P₅))", applies:"C1, C2, C3, C4, V1, V2, I1, I2, I3, I5, E1, E2, E3, S1, S2, S3" },
    { id:"B", name:"Fleet Percentile (inverse)", formula:"N(x) = 1 − soft_clip((x − P₅) / (P₉₅ − P₅))", applies:"V3, I4, T1, T2" },
    { id:"C", name:"Binary (bounded)", formula:"N(x) = 0 if compliant, 1 if non-compliant", applies:"I8 (N-1 compliance)" },
    { id:"D", name:"Categorical Mapping", formula:"N(x) = lookup_table(class → [0, 1])", applies:"I6 (coastal/industrial corrosion), I7 (cyclone wind loading), I9 (renewable concentration)" }
  ],

  /* ── 11 data layers · 95 variables ── */
  DATA_LAYERS: [
    { id:"A",   name:"SSI v4.0.2 Resilience (Mexico)",                 vars:20, status:"LIVE",    sources:"CENACE · CRE · CFE · INEGI · SMN · CENAPRED · SENER · SEMARNAT" },
    { id:"B.1", name:"Grid Telemetry: Open",                       vars:3,  status:"LIVE",    sources:"SMN / ERA5 · CENACE" },
    { id:"B.2", name:"Grid Telemetry: Proxy",                      vars:4,  status:"LIVE",    sources:"IEEE C57.91 · CFE · CRE" },
    { id:"B.3", name:"Grid Telemetry: Fuzzy",                      vars:12, status:"FUZZY",   sources:"IEEE/CIGRÉ standards · CENAPRED" },
    { id:"C",   name:"Socio-Economic + Mexican Demographics",        vars:10, status:"LIVE",    sources:"INEGI · CONEVAL · Banxico · SENER" },
    { id:"D",   name:"Environmental Hazards (Cyclone+Seismic+Flood)", vars:8,  status:"LIVE",    sources:"SMN · CENAPRED · SGM · CONAGUA · Copernicus" },
    { id:"E",   name:"Mexican Open Data + Energy Policy",            vars:9,  status:"LIVE",    sources:"CENACE · SENER · CFE · SEMARNAT" },
    { id:"F",   name:"Network Transitions + RE Integration",         vars:12, status:"BAYESIAN",sources:"CFE history OR IEEE/CIGRÉ + priors" },
    { id:"G",   name:"Modifier Inputs (Cyclone/Seismic-Weighted)",   vars:4,  status:"LIVE",    sources:"CENACE reliability · SMN · OSM" },
    { id:"H",   name:"Network & Topology (CENACE Transmission)",     vars:7,  status:"LIVE",    sources:"CENACE · SENER · OSM" },
    { id:"I",   name:"Output Scores + Alert Flags",                 vars:7,  status:"LIVE",    sources:"Fleet Markov Chain · IEEE/CIGRÉ analysis" }
  ],

  /* ── validation framework ── */
  VALIDATION_CHECKS: [
    { check:"Coastal cyclone vulnerability gradient",               criterion:"Coastal regions (Veracruz, Tamaulipas, Yucatán Peninsula) show higher R systematically due to tropical cyclone exposure vs interior regions", status:"expected" },
    { check:"Seismic hazard–I5 coherence (CENAPRED)",               criterion:"Substations in high-seismic zones show elevated I5 scores — earthquake risk zones and fault line proximity", status:"expected" },
    { check:"Tropical cyclone–I3 agreement (SMN)",                  criterion:"Coastal/hurricane-vulnerable substations show elevated I3 scores, especially in Atlantic and Pacific cyclone corridors", status:"expected" },
    { check:"Flood hazard–I5 agreement (CONAGUA)",                  criterion:"Flood-prone municipios and river-adjacent substations show elevated I5 scores during wet season and flood risk periods", status:"expected" },
    { check:"Wind loading–I7 agreement (CENAPRED/SMN)",             criterion:"Substations with high cyclone wind exposure show elevated I7 scores, especially in northern corridor and coastal regions", status:"expected" },
    { check:"Renewable concentration–I9 signal (SENER/CENACE)",     criterion:"Substations near/fed by major wind/solar farms show elevated I9 scores; northern corridor wind concentration", status:"expected" },
    { check:"RE stress–variability correlation (north)",            criterion:"Northern corridor with high wind penetration shows elevated S2 scores; solar-heavy regions with diurnal S2 swings", status:"expected" },
    { check:"Coastal corrosion–I6 signal (SMN)",                    criterion:"High-exposure substations in salt-spray coastal zones show elevated I6 corrosion class (C4–C5)", status:"expected" },
    { check:"Regional dispatch bottleneck–R4 signal",               criterion:"CENACE dispatch centre supply regions show elevated R4 graph criticality (regionales criticality)", status:"expected" },
    { check:"Industrial cluster concentration–E3 signal",           criterion:"Automotive hubs (Guanajuato, Aguascalientes), petrochemical zones (Veracruz) show elevated E3 due to manufacturing load", status:"expected" },
    { check:"RE stress vs EV load correlation",                     criterion:"S2 (RE stress) and S3 (EV penetration) positively correlated in urban areas (Mexico City, Monterrey, Guadalajara)", status:"nascent" },
    { check:"Monte Carlo convergence (CV < 2%)",                    criterion:"Coefficient of variation < 2% at 10,000 iterations for all substations", status:"expected" },
    { check:"Weight budget unity",                                   criterion:"Component weights sum to 1.0000; all intra-weights sum to 1.0000 per component", status:"expected" },
    { check:"Modifier range adherence",                              criterion:"All modifiers stay within declared [min, max] bounds across the fleet", status:"expected" },
    { check:"Band boundary contiguity",                              criterion:"No gap or overlap between Low/Medium/High/Critical thresholds", status:"expected" },
    { check:"R3 consequence signal + Mexico City concentration",     criterion:"Urban centres (Mexico City) and high-density municipios consistently score higher R3 multiplier", status:"expected" },
    { check:"R6b Tropical cyclone/seismic/flood sensitivity (CRITICAL)", criterion:"Tropical cyclone + seismic + flood proximity drives R6b up to 1.25 ceiling; all three overlay components independent of other modifiers", status:"critical" },
    { check:"CENACE vs CFE constraint signal",                      criterion:"CENACE transmission substations score higher R4; CFE distribution periphery lower due to topology, except industrial bottlenecks", status:"expected" },
    { check:"Regional dispatch price coherence",                    criterion:"E1 scores align with regional energy market signals; RE curtailment level modulation visible", status:"expected" },
    { check:"Industrial load coupling effect",                       criterion:"Substations serving major manufacturing zones show enhanced S2 via load concentration and demand variability", status:"expected" },
    { check:"Volcanic hazard signal",                                criterion:"Substations near active volcanoes (Popocatépetl, Colima, Iztaccíhuatl) show elevated I5 volcanic risk; CENAPRED mapping validation", status:"expected" }
  ],

  /* ── changelog v3.4 → v4.0.2 (Mexico edition) ── */
  CHANGELOG: [
    { id:"MX1",  change:"Mexico country launch — 3,140 substations across 32 Estados, administrative municipio level", type:"new" },
    { id:"MX2",  change:"Integrated CENACE transmission dispatch data + CRE reliability benchmarks", type:"data" },
    { id:"MX3",  change:"CRE reliability register integrated — SAIDI/SAIFI standardisation for CFE distribution and permit holders", type:"data" },
    { id:"MX4",  change:"SMN tropical cyclone + rainfall hazard data integrated — critical for maritime climate exposure assessment", type:"data" },
    { id:"MX5",  change:"CENAPRED seismic + volcanic + flood hazard mapping integrated — earthquake, volcanic, flood zone vulnerability", type:"data" },
    { id:"MX6",  change:"SGM wind loading + geological stability mapping integrated — overhead transmission line vulnerability in seismic regions", type:"data" },
    { id:"MX7",  change:"SMN + CENAPRED + SGM climate integration — tropical cyclone risk, seismic hazard, flood exposure, volcanic activity", type:"data" },
    { id:"MX8",  change:"INEGI Census + CONEVAL socio-economic data integrated — vulnerability indices per municipio, urban concentration", type:"data" },
    { id:"MX9",  change:"SENER + CENACE data integrated — RE penetration for northern corridor, solar expansion, PRODESEN targets", type:"data" },
    { id:"MX10", change:"Banxico + regional market data integrated — E1 volatility modulation for RE-dependent regions", type:"new" },
    { id:"MX11", change:"R6b modifier enhanced with triple SMN+CENAPRED+CONAGUA hazard overlay: tropical cyclone + seismic/volcanic + flood (range 1.00–1.25)", type:"enhanced" },
    { id:"MX12", change:"R3 consequence enriched with urban concentration, socio-economic vulnerability, poverty indices + industrial exposure metrics", type:"enhanced" },
    { id:"MX13", change:"R4 graph criticality rebuilt with CENACE transmission topology + CFE network constraints + regional dispatch centre bottleneck penalty", type:"enhanced" },
    { id:"MX14", change:"I9 Renewable Capacity Concentration Risk — new metric from SENER/CENACE for major wind/solar farm proximity (northern corridor growth)", type:"new" },
    { id:"MX15", change:"R2 Adaptive IRI now includes climate projections for tropical cyclone intensity, seismic activity, flood risk shifts", type:"enhanced" }
  ]
};

/* ── Legacy flat structure (backward-compat) ── */
window.SSI_METADATA = window.SSIMetadata;
