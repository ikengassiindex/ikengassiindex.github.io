/*  SSI v4.0.2 — Metadata Registry · Chile
    Loaded by every page in /chile/.
    ──────────────────────────────────────────────
    Exports:  window.SSIMetadata   (structured, matches Australia/France format exactly)
              window.SSI_METADATA  (legacy flat, backward-compat)              */

window.SSIMetadata = {

  /* ── 30 verified data sources — Chilean institutions ── */
  DATA_SOURCES: [
    { id:"CEN",    name:"CEN (Coordinador Eléctrico Nacional)", url:"cne.cl/coordinador", freq:"Daily", res:"Substation", vars:14, category:"Grid", feeds:"C1–C4, I2, S1–S2, transmission network topology, dispatch data" },
    { id:"CNE",    name:"CNE (Comisión Nacional de Energía)", url:"energia.gob.cl", freq:"Monthly", res:"Regional", vars:12, category:"Grid", feeds:"C1–C4, V1–V2, I1, policy data, Energía Abierta portal", registration:true },
    { id:"SEC",    name:"SEC (Superintendencia de Electricidad y Combustibles)", url:"sec.cl", freq:"Quarterly", res:"DNSP", vars:10, category:"Grid", feeds:"C1–C4, safety compliance, technical standards, asset registration" },
    { id:"INE",    name:"INE (Instituto Nacional de Estadísticas)", url:"ine.cl", freq:"Annual", res:"Comuna", vars:9, category:"Socio-Econ", feeds:"E1–E3, Census 2017, population, income, unemployment, vulnerability indices" },
    { id:"CSN",    name:"CSN (Centro Sismológico Nacional)", url:"sismologia.cl", freq:"Continuous", res:"Grid 0.1°", vars:7, category:"Hazard", feeds:"I5 (seismic PGA), earthquake catalog, hazard maps (critical for Chile)" },
    { id:"SERNA",  name:"SERNAGEOMIN (Servicio Nacional de Geología y Minería)", url:"sernageomin.cl", freq:"Static", res:"Grid 0.1°", vars:6, category:"Hazard", feeds:"I5 variant (volcanic), geological mapping, tsunamis, landslide zones" },
    { id:"DMC",    name:"DMC (Dirección Meteorológica de Chile)", url:"meteochile.cl", freq:"Daily", res:"Station", vars:8, category:"Climate", feeds:"I3 (thermal stress), humidity, wind, precipitation, drought indices" },
    { id:"COPER",  name:"Copernicus ERA5 — Climate Reanalysis", url:"cds.climate.copernicus.eu", freq:"Monthly", res:"Grid 0.25°", vars:6, category:"Climate", feeds:"Thermal stress, humidity, wind, CMIP6 forward projections for Andes exposure" },
    { id:"OSM",    name:"OpenStreetMap — Power Infrastructure", url:"openstreetmap.org", freq:"Continuous", res:"Node", vars:8, category:"Infrastructure", feeds:"I4 (graph degree), topology, 1,095 substations mapped, SIC/SING networks" },
    { id:"SHOA",   name:"SHOA (Servicio Hidrográfico y Oceanográfico)", url:"shoa.cl", freq:"Static", res:"Coastal Grid", vars:5, category:"Hazard", feeds:"I5 variant (tsunami hazard), coastal inundation risk maps (critical for central Chile)" },
    { id:"CONAF",  name:"CONAF (Corporación Nacional Forestal)", url:"conaf.cl", freq:"Seasonal", res:"Grid 1 km", vars:4, category:"Environment", feeds:"I3 variant (forest fire risk index), fire season exposure, dry season duration" },
    { id:"ACERA",  name:"ACERA (Asociación Chilena de Energías Renovables)", url:"acera.cl", freq:"Annual", res:"Regional", vars:5, category:"Transition", feeds:"S1 (RE capacity), T1–T2, renewable energy penetration, wind/solar assets" },
    { id:"COCHILCO",name:"Cochilco (Comisión Chilena del Cobre)", url:"cochilco.cl", freq:"Quarterly", res:"Mining Region", vars:4, category:"Industrial", feeds:"E1 variant (copper load), mining demand cycles, price volatility impact" },
    { id:"BancoCentral",name:"Banco Central de Chile — Economic Data", url:"bcentral.cl", freq:"Monthly", res:"National", vars:5, category:"Economic", feeds:"E1 (energy price index), inflation, exchange rate, economic cycles" },
    { id:"DINEM",  name:"DINEM (Dirección de Negocio Energético Minero)", url:"dinem.cl", freq:"Annual", res:"Mining District", vars:3, category:"Industrial", feeds:"E1, S1, large industrial loads, lithium production impact" },
    { id:"IEEE-CIGRE",name:"IEEE C57.91 / CIGRE TB 761 Standards", url:"ieee.org", freq:"Static", res:"Reference", vars:3, category:"Standards", feeds:"Thermal limits, degradation curves, transformer loss models" },
    { id:"ISO9223", name:"ISO 9223 — Corrosion Classification", url:"iso.org", freq:"Static", res:"Global", vars:2, category:"Standards", feeds:"I6 (corrosion class), atmospheric corrosion rates, salt/humidity exposure" },
    { id:"CIREN",  name:"CIREN (Centro de Información de Recursos Naturales)", url:"ciren.cl", freq:"Annual", res:"Grid 1 km", vars:6, category:"Environment", feeds:"I3 (climate IRI), soil moisture, vegetation index, drought stress" },
    { id:"ONEMI",  name:"ONEMI (Oficina Nacional de Emergencia)", url:"onemi.cl", freq:"Monthly", res:"Regional", vars:4, category:"Hazard", feeds:"Disaster declarations, emergency exposure, climate event frequency" },
    { id:"SUBGOV", name:"Subgobernaciones Regionales — CORE Data", url:"interior.gob.cl", freq:"Annual", res:"Comuna", vars:5, category:"Socio-Econ", feeds:"E1–E3, regional vulnerability indices, social conflict zones" },
    { id:"SERNATUR",name:"SERNATUR (Servicio Nacional de Turismo)", url:"sernatur.cl", freq:"Annual", res:"Tourist Zone", vars:3, category:"Economic", feeds:"E1 variant (seasonal demand), tourism-dependent grid load patterns" },
    { id:"ENAP",   name:"ENAP (Empresa Nacional de Petróleo)", url:"enap.cl", freq:"Quarterly", res:"Refinery", vars:2, category:"Industrial", feeds:"S1 variant (thermal plant load), fuel supply chain coupling" },
    { id:"DGA",    name:"DGA (Dirección General de Aguas)", url:"dga.cl", freq:"Monthly", res:"River Basin", vars:5, category:"Environment", feeds:"I3 variant (hydroelectric potential), water availability, drought forecasts" },
    { id:"SISS",   name:"SISS (Superintendencia de Servicios Sanitarios)", url:"siss.gob.cl", freq:"Annual", res:"Utility Service", vars:3, category:"Socio-Econ", feeds:"E2 (population served), water-energy nexus, industrial supply vulnerability" },
    { id:"SEREMI",  name:"SEREMI de Energía (Regional Secretariats)", url:"energia.gob.cl", freq:"Annual", res:"Region", vars:4, category:"Grid", feeds:"Regional policy, local asset data, regional transition targets" },
    { id:"PNUD",   name:"PNUD Chile — Human Development", url:"cl.undp.org", freq:"Annual", res:"Comuna", vars:4, category:"Socio-Econ", feeds:"E2–E3, human development index, poverty rates, energy poverty proxy" },
    { id:"SII",    name:"SII (Servicio de Impuestos Internos)", url:"sii.cl", freq:"Annual", res:"Business Zone", vars:3, category:"Economic", feeds:"E3 (business density), industry concentration, economic activity clusters" },
    { id:"MINSAL", name:"MINSAL (Ministerio de Salud)", url:"minsal.cl", freq:"Annual", res:"Health District", vars:3, category:"Socio-Econ", feeds:"Energy poverty health link, vulnerable population proximity, healthcare criticality" },
    { id:"CASEN",  name:"CASEN — Characterization of Socioeconomic Status", url:"ministeriodesarrollosocial.gob.cl", freq:"Biennial", res:"Comuna", vars:5, category:"Socio-Econ", feeds:"E2–E3, income vulnerability, employment precarity, energy poverty" },
    { id:"GEOAPI", name:"Geospatial API — Combined Hazard", url:"ide.cl", freq:"Quarterly", res:"Grid 0.1°", vars:4, category:"Hazard", feeds:"Composite hazard index combining seismic, flood, wildfire, and tsunami risk" }
  ],

  /* ── 6 components · 20 metrics ── */
  COMPONENTS: [
    {
      id:"C", name:"Continuity", weight:0.30, color:"#941914",
      desc:"Measures reliability and outage exposure — how often and how long power interruptions occur.",
      metrics:[
        { id:"C1", name:"Outage Duration (SAIDI)", intra:0.35, global:0.105, norm:"A (P5/P95)", source:"CEN / SEC", desc:"Total annual interruption duration per customer", inverted:false, adaptive:false, isNew:false },
        { id:"C2", name:"Outage Frequency (SAIFI)", intra:0.30, global:0.090, norm:"A (P5/P95)", source:"CEN / SEC", desc:"Number of sustained interruptions per customer per year", inverted:false, adaptive:false, isNew:false },
        { id:"C3", name:"Restoration Time (CAIDI)", intra:0.20, global:0.060, norm:"A (P5/P95)", source:"CEN / SEC", desc:"Average duration of each interruption", inverted:false, adaptive:false, isNew:false },
        { id:"C4", name:"Momentary Interruptions (MAIFI)", intra:0.15, global:0.045, norm:"A (P5/P95)", source:"CEN", desc:"Momentary average interruption frequency index", inverted:false, adaptive:false, isNew:false }
      ]
    },
    {
      id:"V", name:"Voltage Quality", weight:0.10, color:"#aa4234",
      desc:"Captures voltage stability, power factor, and harmonic distortion at the distribution level.",
      metrics:[
        { id:"V1", name:"Voltage Deviation (ΔV)", intra:0.40, global:0.040, norm:"A (P5/P95)", source:"CNE / SEC", desc:"Percentage deviation from nominal voltage", inverted:false, adaptive:false, isNew:false },
        { id:"V2", name:"THD (Harmonic Distortion)", intra:0.30, global:0.030, norm:"A (P5/P95)", source:"SEC", desc:"Total harmonic distortion percentage", inverted:false, adaptive:false, isNew:false },
        { id:"V3", name:"Power Factor", intra:0.30, global:0.030, norm:"B (inverse)", source:"CNE / SEC", desc:"Ratio of real to apparent power — higher is better", inverted:true, adaptive:false, isNew:false }
      ]
    },
    {
      id:"I", name:"Infrastructure", weight:0.25, color:"#5d8563",
      desc:"Assesses physical asset condition, age, capacity, seismic/tsunami/wildfire exposure (critical for Chile).",
      metrics:[
        { id:"I1", name:"Asset Age Index", intra:0.12, global:0.030, norm:"A (P5/P95)", source:"SEC / CNE", desc:"Fleet-normalised average asset age", inverted:false, adaptive:false, isNew:false },
        { id:"I2", name:"Capacity Utilisation", intra:0.12, global:0.030, norm:"A (P5/P95)", source:"CEN / SEC", desc:"Percentage of rated capacity in use", inverted:false, adaptive:false, isNew:false },
        { id:"I3", name:"Climate IRI (Thermal + Drought Stress)", intra:0.12, global:0.030, norm:"A (P5/P95)", source:"DMC / CIREN / ERA5", desc:"Infrastructure Risk Index based on thermal extremes, drought indices, and fire season", inverted:false, adaptive:true, isNew:false },
        { id:"I4", name:"Graph Degree (Topology)", intra:0.12, global:0.030, norm:"B (inverse)", source:"OSM / CEN", desc:"Number of connections — higher degree = more redundancy", inverted:true, adaptive:false, isNew:false },
        { id:"I5", name:"Seismic PGA + Tsunami Hazard", intra:0.18, global:0.045, norm:"A (P5/P95)", source:"CSN / SHOA / SERNA", desc:"Peak ground acceleration + tsunami inundation hazard (critical for Chile)", inverted:false, adaptive:false, isNew:false },
        { id:"I6", name:"Corrosion Class", intra:0.10, global:0.025, norm:"D (categorical)", source:"ISO9223 / DMC", desc:"Environmental corrosion exposure based on humidity, salt (coastal vulnerability)", inverted:false, adaptive:false, isNew:false, categorical:true },
        { id:"I7", name:"Wildfire Risk Zone", intra:0.12, global:0.030, norm:"D (categorical)", source:"CONAF / ONEMI", desc:"Wildfire hazard classification from CONAF seasonal fire risk mapping", inverted:false, adaptive:true, isNew:false, categorical:true },
        { id:"I8", name:"N-1 Compliance", intra:0.05, global:0.0125, norm:"C (binary)", source:"CEN", desc:"Whether substation meets N-1 redundancy standard", inverted:true, adaptive:false, isNew:false },
        { id:"I9", name:"Volcanic / Geological Risk", intra:0.07, global:0.0175, norm:"D (categorical)", source:"SERNA / CSN", desc:"Proximity to active volcanoes or geological hazard zones (Chilean-specific)", inverted:false, adaptive:false, isNew:true, categorical:true }
      ]
    },
    {
      id:"E", name:"Economic", weight:0.10, color:"#3b9eff",
      desc:"Links grid risk to regional economic exposure — copper/mining cycles, energy pricing, and employment.",
      metrics:[
        { id:"E1", name:"Energy Price Index + Copper Cycle", intra:0.40, global:0.040, norm:"A (P5/P95)", source:"BancoCentral / Cochilco / CNE", desc:"Wholesale + retail electricity cost per MWh, modulated by copper price volatility", inverted:false, adaptive:true, isNew:false },
        { id:"E2", name:"Unemployment Rate", intra:0.30, global:0.030, norm:"A (P5/P95)", source:"INE / CASEN", desc:"Comuna-level unemployment rate", inverted:false, adaptive:false, isNew:false },
        { id:"E3", name:"Business Density + Mining Concentration", intra:0.30, global:0.030, norm:"A (P5/P95)", source:"SII / DINEM / INE", desc:"Economic activity clusters and large industrial load concentration", inverted:false, adaptive:false, isNew:false }
      ]
    },
    {
      id:"S", name:"Saturation", weight:0.20, color:"#b88f3e",
      desc:"Quantifies DER/RE penetration stress, reverse power flow risk, and EV charging load on the grid.",
      metrics:[
        { id:"S1", name:"Renewable Energy Capacity Ratio", intra:0.35, global:0.070, norm:"A (P5/P95)", source:"ACERA / CEN / CNE", desc:"Total installed RE (wind/solar) capacity relative to substation rating", inverted:false, adaptive:false, isNew:false },
        { id:"S2", name:"RE Stress Index (Variability + Curtailment)", intra:0.35, global:0.070, norm:"A (P5/P95)", source:"ACERA / CEN", desc:"Composite stress: RE penetration × output variability × transmission constraints", inverted:false, adaptive:true, isNew:false },
        { id:"S3", name:"EV Penetration Rate (Emerging)", intra:0.30, global:0.060, norm:"A (P5/P95)", source:"CNE / Transport Ministry", desc:"EV registrations as percentage of total fleet in catchment area (nascent adoption)", inverted:false, adaptive:false, isNew:true }
      ]
    },
    {
      id:"T", name:"Energy Transition", weight:0.05, color:"#0e7490", isNew:true,
      desc:"Measures clean energy transition pace and grid readiness for decarbonisation (RE targets: 60% by 2035).",
      metrics:[
        { id:"T1", name:"Renewable Energy Share (%)", intra:0.50, global:0.025, norm:"B (inverse)", source:"ACERA / CEN / CNE", desc:"Share of generation from renewables — higher share = lower risk (inverted)", inverted:true, adaptive:false, isNew:false },
        { id:"T2", name:"Transition Readiness Score", intra:0.50, global:0.025, norm:"A (P5/P95)", source:"CNE / ACERA / CEN", desc:"Composite readiness: grid flexibility + storage deployment + SIC/SING interconnection capacity", inverted:true, adaptive:false, isNew:true }
      ]
    }
  ],

  /* ── 7 modifiers (R2–R7, incl. R6a + R6b seismic) ── */
  MODIFIERS: [
    { id:"R2", name:"Adaptive Climate IRI + Hazard Trajectory", range:"Weight redistribution", type:"Weight modifier", desc:"Uses CMIP6 SSP2-4.5 projections to adjust IRI metrics for drought, wildfire corridor, and seismic corridor exposure. When local seismic/wildfire risk is low, weight shifts from I5/I7 to structural metrics (I1, I4). Incorporates DGA water availability forecasts.", formula:"IRI_forward(m,s) = IRI_current(m,s) × (1 + 0.15 × clip(Δ_climate, −0.50, +1.00))", sources:["DMC","CIREN","CSN","Copernicus ERA5"], isEnhanced:true },
    { id:"R3", name:"Consequence + Energy Poverty + Mining Criticality", range:"[0.70, 1.35]", type:"Multiplicative", desc:"Amplifies risk for communes serving large populations or energy-poor communities with high economic dependency. Includes vulnerability indices (PNUD, CASEN), elderly exposure, and mining industry proximity.", formula:"C_mult = sigmoid(pop_weight × load_weight × V_socio × mining_factor)", sources:["INE","CASEN","PNUD","DINEM","MINSAL"], isEnhanced:true },
    { id:"R4", name:"Graph Criticality + Network Constraint", range:"[0.80, 1.40]", type:"Multiplicative", desc:"Penalises topological bottlenecks in SIC/SING networks: high betweenness centrality, bridge nodes, low degree, and north-south transmission congestion. Built from OSM power graph and CEN transmission constraints.", formula:"F_topo = f(degree, BC_percentile, is_bridge, sic_sing_tier)", sources:["OSM","CEN"], isEnhanced:true },
    { id:"R6a", name:"Restoration Speed", range:"[0.90, 1.10]", type:"Multiplicative", desc:"SEC-CAIDI-based: rewards fast-restoring areas, penalises slow ones. Two substations with identical SAIDI can have different risk profiles based on how quickly power is restored in remote regions.", formula:"R6a = sigmoid_bounded(CAIDI_local / CAIDI_fleet_median)", sources:["SEC","CEN"], isEnhanced:true },
    { id:"R6b", name:"Seismic + Tsunami Overlay (CRITICAL FOR CHILE)", range:"[1.00, 1.50]", type:"Multiplicative", desc:"CSN PGA + SHOA tsunami hazard overlay. Penalises substations in high-seismic zones (subduction zone proximity) or coastal inundation risk areas. Range higher than Australia due to Chile's seismic/tsunami prominence. Integration of ONEMI emergency declarations.", formula:"R6b = f(CSN_PGA_percentile, SHOA_tsunami_hazard, subduction_zone_proximity)", sources:["CSN","SHOA","SERNA","ONEMI"], isEnhanced:true },
    { id:"R7", name:"Digital Readiness + Cyber-Physical Resilience", range:"[0.99, 1.05]", type:"Multiplicative", desc:"Cyber-physical security baseline, SCADA maturity proxy, and microgrid/islanding capability. Indicates digital resilience capability at the grid edge for earthquake/tsunami recovery scenarios.", formula:"Cyber = f(SCADA_maturity, microgrid_pct, islanding_capability)", sources:["CEN","SEC"], isEnhanced:false }
  ],

  /* ── processing pipeline ── */
  PIPELINE: [
    { step:1, name:"Ingest", desc:"95 variables from 30 verified Chilean public data sources — CEN, CNE, SEC, INE, CSN, SERNAGEOMIN, DMC, CONAF, ACERA, Cochilco, and others. Zero proprietary SCADA dependencies. Maximum ingestion frequency: daily (CEN dispatch data).", icon:"📥" },
    { step:2, name:"Normalise", desc:"Four normalisation methods: Method A (robust fleet percentile P5/P95), Method B (inverse fleet percentile for density), Method C (binary compliance), and Method D (categorical mapping). Inverted metrics for density measures where higher = better resilience.", icon:"📐" },
    { step:3, name:"Weight", desc:"6-level hierarchical weighting across 6 components and 20 metrics. Continuity dominates at 0.30, Infrastructure at 0.25 (with higher seismic/I5 weight), Saturation at 0.20. Weight budget validated by Sobol sensitivity analysis.", icon:"⚖️" },
    { step:4, name:"Compose R_base", desc:"Weighted sum of 6 normalised component scores produces the base resilience score.", icon:"🧮" },
    { step:5, name:"Modify", desc:"Seven multiplicative modifiers adjust R_base for Chilean context: R2 (adaptive climate + seismic trajectory), R3 (consequence + energy poverty + mining criticality), R4 (graph criticality + SIC/SING constraints), R6a (restoration speed), R6b (seismic/tsunami overlay — CRITICAL), R7 (digital readiness). Plus 6 micro-enrichments for vulnerable populations, wildfire/seismic zones, coastal/tsunami exposure, mining regions, and healthcare criticality.", icon:"🔧" },
    { step:6, name:"Monte Carlo", desc:"10,000 iterations per substation using a 20×20 Gaussian copula correlation matrix. Captures measurement, spatial, staleness, and model uncertainty. Produces median, P5, P95, skewness, and P_critical for each substation.", icon:"🎲" },
    { step:7, name:"Classify", desc:"Four bands: Low (0.00–0.25), Medium (0.25–0.50), High (0.50–0.75), Critical (0.75–1.00). Alert flags trigger when any single component exceeds its P95 fleet threshold. Seismic/tsunami events escalate classification instantaneously.", icon:"🏷️" }
  ],

  /* ── classification bands ── */
  CLASSIFICATION: [
    { name:"Low",      range:"0.00 – 0.25", meaning:"Good resilience — stable grid, low exposure",       expected:"~35–40%", color:"#5d8563" },
    { name:"Medium",   range:"0.25 – 0.50", meaning:"Moderate risk — some vulnerabilities present",       expected:"~32–38%", color:"#b88f3e" },
    { name:"High",     range:"0.50 – 0.75", meaning:"Elevated risk — investment priority zone",           expected:"~18–23%", color:"#aa4234" },
    { name:"Critical", range:"0.75 – 1.00", meaning:"Severe vulnerability — urgent intervention required", expected:"~5–10%",   color:"#941914" }
  ],

  /* ── master equation ── */
  MASTER_EQUATION: "R_final = soft_clip_upper( R_base × F_topo × C_mult × R6a_mult × R6b_seismic_tsunami × Cyber_factor )",

  /* ── normalisation methods ── */
  NORM_METHODS: [
    { id:"A", name:"Fleet Percentile (robust)", formula:"N(x) = soft_clip((x − P₅) / (P₉₅ − P₅))", applies:"C1, C2, C3, C4, V1, V2, I1, I2, I3, I5, E1, E2, E3, S1, S2, S3" },
    { id:"B", name:"Fleet Percentile (inverse)", formula:"N(x) = 1 − soft_clip((x − P₅) / (P₉₅ − P₅))", applies:"V3, I4, T1, T2" },
    { id:"C", name:"Binary (bounded)", formula:"N(x) = 0 if compliant, 1 if non-compliant", applies:"I8 (N-1 compliance)" },
    { id:"D", name:"Categorical Mapping", formula:"N(x) = lookup_table(class → [0, 1])", applies:"I6 (corrosion), I7 (wildfire), I9 (volcanic/geological)" }
  ],

  /* ── 11 data layers · 95 variables ── */
  DATA_LAYERS: [
    { id:"A",   name:"SSI v4.0.2 Resilience (Chile)",      vars:20, status:"LIVE",    sources:"CEN · CNE · SEC · INE · CSN · SHOA" },
    { id:"B.1", name:"Grid Telemetry: Open",              vars:3,  status:"LIVE",    sources:"DMC / ERA5 · CNE" },
    { id:"B.2", name:"Grid Telemetry: Proxy",             vars:4,  status:"LIVE",    sources:"IEEE C57.91 · CEN · SEC" },
    { id:"B.3", name:"Grid Telemetry: Fuzzy",             vars:12, status:"FUZZY",   sources:"IEEE/CIGRÉ standards · CSN" },
    { id:"C",   name:"Socio-Economic + Mining",            vars:10, status:"LIVE",    sources:"INE · CASEN · PNUD · Cochilco" },
    { id:"D",   name:"Environmental Hazards (Seismic+)",   vars:8,  status:"LIVE",    sources:"CSN · SHOA · SERNA · CONAF · Copernicus" },
    { id:"E",   name:"Chilean Open Data + Energy Policy",  vars:9,  status:"LIVE",    sources:"ACERA · CNE · SEREMI · DGA" },
    { id:"F",   name:"Network Transitions + RE Ramp",      vars:12, status:"BAYESIAN",sources:"CEN history OR IEEE/CIGRÉ + priors" },
    { id:"G",   name:"Modifier Inputs (Seismic-Weighted)",  vars:4,  status:"LIVE",    sources:"SEC reliability · CSN PGA · CEN topology" },
    { id:"H",   name:"Network & Topology (SIC/SING)",      vars:7,  status:"LIVE",    sources:"CEN · CSN · OSM" },
    { id:"I",   name:"Output Scores + Alert Flags",        vars:7,  status:"LIVE",    sources:"Fleet Markov Chain · IEEE/CIGRÉ analysis" }
  ],

  /* ── validation framework ── */
  VALIDATION_CHECKS: [
    { check:"North–South transmission gradient",              criterion:"Central Chile metro R systematically lower than remote Atacama / Patagonia regions",                          status:"expected" },
    { check:"Seismic PGA–I5 coherence (subduction zone)",     criterion:"Substations in high-seismic zones show elevated I5 scores — 1927/1960/2010 fault zones",                    status:"expected" },
    { check:"Tsunami–coastal coherence (SHOA overlay)",       criterion:"Coastal substations (V-region, VIII-region) show elevated I5/R6b scores",                                   status:"expected" },
    { check:"Wildfire–I3/I7 agreement (CONAF)",              criterion:"Substations in fire-prone zones (VII–IX regions, summer) show elevated I3 and I7 scores",                   status:"expected" },
    { check:"RE stress–DER agreement (North)",                criterion:"Atacama/Antofagasta regions with high solar penetration show elevated S2 scores",                          status:"expected" },
    { check:"Copper price–E1 correlation",                    criterion:"Energy price volatility tracks Cochilco copper index in mining-dependent regions",                         status:"expected" },
    { check:"SAIDI–CAIDI cross-consistency",                 criterion:"High SAIDI regions also show high CAIDI (slow restoration in remote zones)",                                status:"expected" },
    { check:"CSN seismic spatial coherence",                 criterion:"CSN PGA hazard map aligns with I5 scores — elevated in central/southern transverse valleys",               status:"expected" },
    { check:"RE stress vs EV load correlation",              criterion:"S2 (RE stress) and S3 (EV penetration) positively correlated in Santiago/Valparaíso catchments",           status:"nascent" },
    { check:"Monte Carlo convergence (CV < 2%)",             criterion:"Coefficient of variation < 2% at 10,000 iterations for all substations",                                   status:"expected" },
    { check:"Weight budget unity",                           criterion:"Component weights sum to 1.0000; all intra-weights sum to 1.0000 per component",                           status:"expected" },
    { check:"Modifier range adherence",                      criterion:"All modifiers stay within declared [min, max] bounds across the fleet",                                     status:"expected" },
    { check:"Band boundary contiguity",                      criterion:"No gap or overlap between Low/Medium/High/Critical thresholds",                                            status:"expected" },
    { check:"R3 consequence signal + mining criticality",     criterion:"High-population, energy-poor, mining-dependent communes consistently score higher R3 multiplier",         status:"expected" },
    { check:"R6b seismic sensitivity (CRITICAL)",            criterion:"Subduction zone proximity drives R6b up to 1.50 ceiling; independent of other modifiers",               status:"critical" },
    { check:"SIC vs SING constraint signal",                 criterion:"SING (northern grid) substations score higher R4 due to bottleneck topology",                              status:"expected" }
  ],

  /* ── changelog v3.4 → v4.0.2 (Chile edition) ── */
  CHANGELOG: [
    { id:"CL1",  change:"Chile country launch — 1,095 substations across 16 regiones, 346 comunas",                                              type:"new" },
    { id:"CL2",  change:"Integrated CEN transmission dispatch data + CNE Energía Abierta portal",                                               type:"data" },
    { id:"CL3",  change:"SEC reliability register integrated — SAIDI/SAIFI standardisation for SIC/SING networks",                              type:"data" },
    { id:"CL4",  change:"CSN seismic PGA hazard map integrated (0.1° grid) — critical for subduction zone exposure",                           type:"data" },
    { id:"CL5",  change:"SHOA tsunami hazard overlays integrated — coastal inundation risk for V/VIII regions",                                 type:"data" },
    { id:"CL6",  change:"CONAF wildfire risk mapping integrated — seasonal fire exposure for central/southern zones",                           type:"data" },
    { id:"CL7",  change:"DMC + CIREN climate integration — drought indices and thermal stress for water-scarce north",                          type:"data" },
    { id:"CL8",  change:"INE Census 2017 + CASEN socio-economic data integrated — vulnerability indices per comuna",                            type:"data" },
    { id:"CL9",  change:"Cochilco copper price coupling integrated — E1 volatility modulation for mining regions",                             type:"new" },
    { id:"CL10", change:"ACERA RE capacity data integrated — solar/wind penetration for Atacama/Patagonia",                                    type:"data" },
    { id:"CL11", change:"R6b modifier enhanced with dual CSN PGA + SHOA tsunami hazard (range 1.00–1.50)",                                    type:"enhanced" },
    { id:"CL12", change:"R3 consequence enriched with CASEN energy poverty, DINEM mining criticality, MINSAL health links",                    type:"enhanced" },
    { id:"CL13", change:"R4 graph criticality rebuilt with CEN SIC/SING transmission topology — north-south bottleneck penalty",               type:"enhanced" },
    { id:"CL14", change:"I9 Volcanic/Geological Risk — new metric from SERNAGEOMIN volcano proximity data",                                    type:"new" },
    { id:"CL15", change:"R2 Adaptive IRI now includes CMIP6 SSP2-4.5 forward projections for Atacama drought & central wildfire risk",         type:"enhanced" }
  ],

  /* ── fleet stats (placeholder — updated by ssi-data.json at runtime) ── */
  FREQ_DISTRIBUTION: { Low:0.37, Medium:0.35, High:0.20, Critical:0.08 },
  stats: { fleet_median:0.395, fleet_mean:0.412, fleet_std:0.156, n_substations:1095, n_comunas:346, n_regions:16 }
};


/* ═══════════════════════════════════════════════
   Legacy flat format — backward compatibility
   Used by overview.html, regional.html, map.html
   ═══════════════════════════════════════════════ */

window.SSI_METADATA = {
  country: "Chile",
  country_code: "CL",
  flag: "🇨🇱",
  currency: "CL$",
  version: "4.0.2",
  edition: "001",
  edition_month: "March 2026",
  substations_label: "substations",
  region_label: "Región",
  region_label_plural: "Regiones",
  admin_division_label: "Comuna",
  admin_division_label_short: "Comuna",
  total_substations: 1095,
  total_comunas: 346,
  total_regions: 16,
  voltage_tiers: {
    EHV: { label: "EHV (≥ 220 kV)", min_kv: 220 },
    HV:  { label: "HV (66–132 kV)", min_kv: 66 },
    MV:  { label: "MV (< 66 kV)", min_kv: 0 }
  },
  /* derived arrays from SSIMetadata */
  data_sources: window.SSIMetadata.DATA_SOURCES.map(function(s) {
    return { id:"DS_" + s.id, name:s.name, url:s.url, freq:s.freq, resolution:s.res, feeds:s.feeds.split(',').map(function(x){return x.trim();}) };
  }),
  components: window.SSIMetadata.COMPONENTS.map(function(c) {
    return {
      key: c.id, label: c.name, weight: c.weight, color: c.color, description: c.desc,
      metrics: c.metrics.map(function(m) {
        return { id:m.id, label:m.name, intra_w:m.intra, global_w:m.global, unit:"—", norm:m.norm.charAt(0), source:m.source };
      })
    };
  }),
  modifiers: window.SSIMetadata.MODIFIERS.map(function(m) {
    var rangeStr = m.range;
    var rangeArr = rangeStr.match(/\[([^\]]+)\]/) ? rangeStr.match(/\[([\d.]+),\s*([\d.]+)\]/).slice(1).map(Number) : [0,0];
    return { key:m.id, label:m.id, domain:m.name, range:rangeArr, description:m.desc };
  }),
  bands: window.SSIMetadata.CLASSIFICATION.map(function(b) {
    var parts = b.range.split('–').map(function(x){return parseFloat(x.trim());});
    return { label:b.name, min:parts[0], max:parts[1], color:b.color, css:b.name.toLowerCase() };
  }),
  data_layers: window.SSIMetadata.DATA_LAYERS.map(function(l) {
    return { id:l.id, domain:l.name, variables:l.vars, source:l.sources, status:l.status };
  }),
  normalisation: window.SSIMetadata.NORM_METHODS.map(function(n) {
    return { code:n.id, label:n.name, formula:n.formula };
  }),
  validation: window.SSIMetadata.VALIDATION_CHECKS.map(function(v) {
    return { check:v.check, target:v.criterion, tolerance:"—" };
  }),
  changelog: window.SSIMetadata.CHANGELOG.map(function(c) {
    return { version:"4.0.2", date:"2026-03", note:c.change };
  }),
  monte_carlo: { iterations:10000, correlation_matrix:"20×20", seed:42, confidence_interval:0.95 },
  regions: [
    "Arica y Parinacota",
    "Tarapacá",
    "Antofagasta",
    "Atacama",
    "Coquimbo",
    "Valparaíso",
    "Metropolitana de Santiago",
    "Libertador General Bernardo O'Higgins",
    "Maule",
    "Ñuble",
    "La Araucanía",
    "Los Ríos",
    "Los Lagos",
    "Aysén del General Carlos Ibáñez del Campo",
    "Magallanes y de la Antártica Chilena",
    "Región del Biobío"
  ]
};
