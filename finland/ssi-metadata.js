/*  SSI v4.0.2 — Metadata Registry · Finland
    Loaded by every page in /finland/.
    ──────────────────────────────────────────────
    Exports:  window.SSIMetadata   (structured, matches Finland/Chile format exactly)
              window.SSI_METADATA  (legacy flat, backward-compat)              */

window.SSIMetadata = {

  /* ── 30 verified data sources — Finnish institutions ── */
  DATA_SOURCES: [
    { id:"FINGRID", name:"Fingrid — Finnish Transmission System Operator", url:"fingrid.fi", freq:"Real-time", res:"Substation", vars:14, category:"Grid", feeds:"C1–C4, I2, S1–S2, transmission network topology, dispatch data, frequency regulation" },
    { id:"ENERGIAVIRA", name:"Energiavirasto (Energy Authority)", url:"energiavirasto.fi", freq:"Quarterly", res:"DSO", vars:12, category:"Grid", feeds:"C1–C4, V1–V2, I1, reliability metrics SAIDI/SAIFI, technical standards, network quality", registration:true },
    { id:"TILASTOKESKUS", name:"Tilastokeskus (Statistics Finland)", url:"stat.fi", freq:"Annual", res:"Kunta", vars:10, category:"Socio-Econ", feeds:"C1–C4, safety compliance, demographics, income distribution, population served" },
    { id:"FMI", name:"FMI — Ilmatieteen laitos (Finnish Meteorological Institute)", url:"ilmatieteenlaitos.fi", freq:"Daily", res:"Station", vars:8, category:"Climate", feeds:"I3 (thermal stress, winter storms), wind, precipitation, snow depth, arctic warnings" },
    { id:"GTK", name:"GTK — Geological Survey of Finland", url:"gtk.fi", freq:"Annual", res:"Grid 0.1°", vars:7, category:"Hazard", feeds:"I5 (winter flooding hazard), geological data, peat soil mapping, permafrost zones" },
    { id:"SYKE", name:"SYKE — Finnish Environment Institute", url:"syke.fi", freq:"Annual", res:"Grid 0.1°", vars:6, category:"Hazard", feeds:"I7 (snow/ice loading zone mapping), environmental hazards, water availability" },
    { id:"STUK", name:"STUK — Radiation & Nuclear Safety Authority", url:"stuk.fi", freq:"Quarterly", res:"Nuclear Site", vars:5, category:"Energy", feeds:"I9 (nuclear concentration risk), safety metrics, Olkiluoto + Loviisa operational data" },
    { id:"OSM", name:"OpenStreetMap — Power Infrastructure", url:"overpass-api.de", freq:"Continuous", res:"Node", vars:8, category:"Infrastructure", feeds:"I4 (graph degree), topology, ~1,200 substations mapped, transmission + distribution networks" },
    { id:"COPERNICUS", name:"Copernicus ERA5 — Climate Reanalysis", url:"cds.climate.copernicus.eu", freq:"Monthly", res:"Grid 0.25°", vars:6, category:"Climate", feeds:"Thermal stress, snow loading, winter storm risk, CMIP6 forward projections for Arctic" },
    { id:"ENTSOE", name:"ENTSO-E Transparency Platform", url:"transparency.entsoe.eu", freq:"Hourly", res:"Substation", vars:2, category:"Grid", feeds:"C1 (capacity), cross-border flows with Sweden/Norway, Nordic grid exchange" },
    { id:"EUROSTAT", name:"Eurostat — EU Statistics", url:"ec.europa.eu/eurostat", freq:"Annual", res:"Kunta", vars:3, category:"Socio-Econ", feeds:"E2 (population served), water-energy nexus, Arctic energy poverty indicators" },
    { id:"TULLI", name:"Tulli (Finnish Customs)", url:"tulli.fi", freq:"Annual", res:"National", vars:2, category:"Trade", feeds:"Trade data proxy, industrial activity" },
    { id:"TRAFICOM", name:"Traficom — Transport & Comms Agency", url:"traficom.fi", freq:"Quarterly", res:"Regional", vars:3, category:"Transport", feeds:"S3 (EV registrations), electric vehicle charging infrastructure density" },
    { id:"BUSINESSFIN", name:"Business Finland / Suomen Pankki", url:"businessfinland.fi", freq:"Quarterly", res:"Region", vars:4, category:"Economic", feeds:"E1–E3, economic cycles, business density, industrial concentration" },
    { id:"WINDENERGY", name:"Finnish Wind Power Association (Tuulivoima)", url:"tuulivoima.fi", freq:"Monthly", res:"Regional", vars:5, category:"Transition", feeds:"S1 (RE capacity), wind capacity by region, curtailment data, Pohjanmaa wind corridor" },
    { id:"MOTIVA", name:"Motiva (Energy Efficiency Agency)", url:"motiva.fi", freq:"Annual", res:"Region", vars:3, category:"Transition", feeds:"S1 (DER/distributed generation penetration), energy efficiency metrics" },
    { id:"DISTRIBUTOR", name:"Distribution Companies (Caruna, Fingrid, Vattenfall, Helen)", url:"", freq:"Annual", res:"Distribution Company", vars:4, category:"Grid", feeds:"S1 variant (thermal plant load), CAPEX, SAIDI/SAIFI, transformer inventories" },
    { id:"POSTITALO", name:"Posti / Digital Network Authority", url:"posti.fi", freq:"Annual", res:"Kunta", vars:2, category:"Infrastructure", feeds:"Infrastructure density proxy, remote-area identification for Arctic restoration speed" },
    { id:"ILMASTO", name:"Climate Adaptation Centre / Metsähallitus", url:"ilmasto.fi", freq:"Annual", res:"Regional", vars:4, category:"Environment", feeds:"I5 (winter storm + flooding hazard mapping), climate adaptation data, forest fire risk" },
    { id:"WORLDBANK", name:"World Bank / OECD", url:"", freq:"Annual", res:"National", vars:4, category:"Socio-Econ", feeds:"International benchmarks, Arctic socio-economic indicators, renewable energy transition" },
    { id:"SOLARGIS", name:"SolarGIS — Global Solar Atlas", url:"globalsolaratlas.info", freq:"Static", res:"Global", vars:2, category:"Transition", feeds:"T1 (solar resource mapping), solar irradiance (GHI, DNI) for southern Finland" },
    { id:"ARCTICMONITOR", name:"Arctic Monitoring & Assessment Programme", url:"amap.no", freq:"Annual", res:"Regional", vars:3, category:"Climate", feeds:"I6 (Arctic corrosion class), permafrost thaw zones, extreme weather baselines" },
    { id:"VESARC", name:"VesiArc / SYKE Water Data", url:"vesistot.fi", freq:"Quarterly", res:"Watershed", vars:4, category:"Hazard", feeds:"I5 (winter flooding, spring snowmelt hazard), water level monitoring, stream flow" },
    { id:"YMPARISTO", name:"Environmental Permit Register (Ympäristö)", url:"ymparisto.fi", freq:"Annual", res:"Kunta", vars:3, category:"Environment", feeds:"I6 (environmental exposure), pollution data, industrial sites" },
    { id:"FINGRIDOPEN", name:"Fingrid Open Data — Real-time Production", url:"api.fingrid.fi", freq:"Real-time", res:"Substation", vars:5, category:"Grid", feeds:"C1 variant (frequency stability), production mix, demand forecasts" },
    { id:"LUKE", name:"LUKE — Natural Resources Institute", url:"luke.fi", freq:"Annual", res:"Regional", vars:3, category:"Environment", feeds:"Forest cover impact on ice/snow loading, vegetation index, land use constraints" },
    { id:"SIIRTOYHTIO", name:"Siirto-yhtiot Reports (Network Companies)", url:"", freq:"Annual", res:"Distribution Area", vars:4, category:"Grid", feeds:"SAIDI/SAIFI by company, winter storm restoration metrics, CAIDI by geography" },
    { id:"HAKELA", name:"Hakela / State Weather Archive", url:"", freq:"Monthly", res:"Station", vars:3, category:"Climate", feeds:"Historical winter storm severity index, snow accumulation records, Arctic wind patterns" },
    { id:"POPDENS", name:"Population Register Centre", url:"dvv.fi", freq:"Annual", res:"Kunta", vars:3, category:"Socio-Econ", feeds:"E2 (population served), demographic shifts, remote region identification" },
    { id:"KESTAVAOSAKSI", name:"Ministry of Environment — Arctic Resilience", url:"", freq:"Annual", res:"Regional", vars:2, category:"Environment", feeds:"Arctic thermal preservation baseline, permafrost stability data" }
  ],

  /* ── 6 components · 20 metrics ── */
  COMPONENTS: [
    {
      id:"C", name:"Continuity", weight:0.30, color:"#941914",
      desc:"Measures reliability and outage exposure — how often and how long power interruptions occur.",
      metrics:[
        { id:"C1", name:"Outage Duration (SAIDI)", intra:0.35, global:0.105, norm:"A (P5/P95)", source:"Fingrid / Energiavirasto", desc:"Total annual interruption duration per customer", inverted:false, adaptive:false, isNew:false },
        { id:"C2", name:"Outage Frequency (SAIFI)", intra:0.30, global:0.090, norm:"A (P5/P95)", source:"Fingrid / Energiavirasto", desc:"Number of sustained interruptions per customer per year", inverted:false, adaptive:false, isNew:false },
        { id:"C3", name:"Restoration Time (CAIDI)", intra:0.20, global:0.060, norm:"A (P5/P95)", source:"Energiavirasto / DSO", desc:"Average duration of each interruption (winter storm recovery time critical)", inverted:false, adaptive:false, isNew:false },
        { id:"C4", name:"Momentary Interruptions (MAIFI)", intra:0.15, global:0.045, norm:"A (P5/P95)", source:"Fingrid", desc:"Momentary average interruption frequency index", inverted:false, adaptive:false, isNew:false }
      ]
    },
    {
      id:"V", name:"Voltage Quality", weight:0.10, color:"#aa4234",
      desc:"Captures voltage stability, power factor, and harmonic distortion at the distribution level.",
      metrics:[
        { id:"V1", name:"Voltage Deviation (ΔV)", intra:0.40, global:0.040, norm:"A (P5/P95)", source:"Energiavirasto / DSO", desc:"Percentage deviation from nominal voltage", inverted:false, adaptive:false, isNew:false },
        { id:"V2", name:"THD (Harmonic Distortion)", intra:0.30, global:0.030, norm:"A (P5/P95)", source:"Energiavirasto", desc:"Total harmonic distortion percentage", inverted:false, adaptive:false, isNew:false },
        { id:"V3", name:"Power Factor", intra:0.30, global:0.030, norm:"B (inverse)", source:"Energiavirasto / DSO", desc:"Ratio of real to apparent power — higher is better", inverted:true, adaptive:false, isNew:false }
      ]
    },
    {
      id:"I", name:"Infrastructure", weight:0.25, color:"#5d8563",
      desc:"Assesses physical asset condition, age, capacity, winter storm/snow loading exposure (critical for Finland).",
      metrics:[
        { id:"I1", name:"Asset Age Index", intra:0.12, global:0.030, norm:"A (P5/P95)", source:"Energiavirasto / Tilastokeskus", desc:"Fleet-normalised average asset age (Soviet-era vintage estimates)", inverted:false, adaptive:false, isNew:false },
        { id:"I2", name:"Capacity Utilisation", intra:0.12, global:0.030, norm:"A (P5/P95)", source:"Fingrid / Energiavirasto", desc:"Percentage of rated capacity in use", inverted:false, adaptive:false, isNew:false },
        { id:"I3", name:"Climate IRI (Thermal + Winter Storm Stress)", intra:0.12, global:0.030, norm:"A (P5/P95)", source:"FMI / SYKE / ERA5", desc:"Infrastructure Risk Index based on extreme cold, winter storms, and Arctic wind events", inverted:false, adaptive:true, isNew:false },
        { id:"I4", name:"Graph Degree (Topology)", intra:0.12, global:0.030, norm:"B (inverse)", source:"OSM / Fingrid", desc:"Number of connections — higher degree = more redundancy", inverted:true, adaptive:false, isNew:false },
        { id:"I5", name:"Winter Storm + Flooding Hazard", intra:0.18, global:0.045, norm:"A (P5/P95)", source:"FMI / GTK / VesiArc", desc:"Combined winter storm severity + spring snowmelt/flood hazard (critical for Finland, not mining subsidence)", inverted:false, adaptive:false, isNew:false },
        { id:"I6", name:"Corrosion Class (Arctic)", intra:0.10, global:0.025, norm:"D (categorical)", source:"ISO9223 / ARCTICMONITOR", desc:"Environmental corrosion exposure adapted for Arctic conditions, salt spray, and extreme humidity", inverted:false, adaptive:false, isNew:false, categorical:true },
        { id:"I7", name:"Snow/Ice Loading Zone", intra:0.12, global:0.030, norm:"D (categorical)", source:"SYKE / GTK / FMI", desc:"Snow/ice accumulation hazard mapping for overhead transmission lines (replaces Mining Subsidence Zone)", inverted:false, adaptive:true, isNew:false, categorical:true },
        { id:"I8", name:"N-1 Compliance", intra:0.05, global:0.0125, norm:"C (binary)", source:"Fingrid", desc:"Whether substation meets N-1 redundancy standard (Fingrid 400kV backbone)", inverted:true, adaptive:false, isNew:false },
        { id:"I9", name:"Nuclear Concentration Risk", intra:0.07, global:0.0175, norm:"D (categorical)", source:"STUK", desc:"Concentration risk for substations supplying or near Olkiluoto + Loviisa nuclear plants (33% of Finnish baseload)", inverted:false, adaptive:false, isNew:true, categorical:true }
      ]
    },
    {
      id:"E", name:"Economic", weight:0.10, color:"#3b9eff",
      desc:"Links grid risk to regional economic exposure — energy pricing, employment, and industrial cycles.",
      metrics:[
        { id:"E1", name:"Energy Price Index + Thermal Cycle", intra:0.40, global:0.040, norm:"A (P5/P95)", source:"Suomen Pankki / Energiavirasto", desc:"Wholesale + retail electricity cost per MWh, modulated by thermal generation + hydropower cycles", inverted:false, adaptive:true, isNew:false },
        { id:"E2", name:"Population Served + Remote Sparsity", intra:0.30, global:0.030, norm:"A (P5/P95)", source:"Tilastokeskus / Eurostat", desc:"Kunta-level population served, with penalty for remote Arctic communities", inverted:false, adaptive:false, isNew:false },
        { id:"E3", name:"Business Density + Industrial Concentration", intra:0.30, global:0.030, norm:"A (P5/P95)", source:"Business Finland / Tilastokeskus / Energiavirasto", desc:"Economic activity clusters and large industrial load concentration (paper mills, smelters)", inverted:false, adaptive:false, isNew:false }
      ]
    },
    {
      id:"S", name:"Saturation", weight:0.20, color:"#b88f3e",
      desc:"Quantifies DER/RE penetration stress, reverse power flow risk, and EV charging load on the grid.",
      metrics:[
        { id:"S1", name:"Renewable Energy Capacity Ratio", intra:0.35, global:0.070, norm:"A (P5/P95)", source:"Finnish Wind Power Assoc. / Fingrid / Energiavirasto", desc:"Total installed RE (wind/hydro/solar) capacity relative to substation rating", inverted:false, adaptive:false, isNew:false },
        { id:"S2", name:"RE Stress Index (Variability + Curtailment)", intra:0.35, global:0.070, norm:"A (P5/P95)", source:"Finnish Wind Power Assoc. / Fingrid", desc:"Composite stress: RE penetration × output variability × transmission constraints (wind-dominated Pohjanmaa region)", inverted:false, adaptive:true, isNew:false },
        { id:"S3", name:"EV Penetration Rate (Emerging)", intra:0.30, global:0.060, norm:"A (P5/P95)", source:"Traficom / Transport Ministry", desc:"EV registrations as percentage of total fleet in catchment area (growing penetration in urban areas)", inverted:false, adaptive:false, isNew:true }
      ]
    },
    {
      id:"T", name:"Energy Transition", weight:0.05, color:"#0e7490", isNew:true,
      desc:"Measures clean energy transition pace and grid readiness for decarbonisation (RE targets: 80% by 2030).",
      metrics:[
        { id:"T1", name:"Renewable Energy Share (%)", intra:0.50, global:0.025, norm:"B (inverse)", source:"Finnish Wind Power Assoc. / Fingrid / Energiavirasto", desc:"Share of generation from renewables — higher share = lower risk (inverted)", inverted:true, adaptive:false, isNew:false },
        { id:"T2", name:"Transition Readiness Score", intra:0.50, global:0.025, norm:"A (P5/P95)", source:"Energiavirasto / Finnish Wind Power Assoc. / Fingrid", desc:"Composite readiness: grid flexibility + storage deployment + DSO interconnection capacity", inverted:true, adaptive:false, isNew:true }
      ]
    }
  ],

  /* ── 7 modifiers (R2–R7, incl. R6a + R6b winter storm/snow loading) ── */
  MODIFIERS: [
    { id:"R2", name:"Adaptive Climate IRI + Arctic Hazard Trajectory", range:"Weight redistribution", type:"Weight modifier", desc:"Uses CMIP6 SSP2-4.5 projections to adjust IRI metrics for winter storm risk, snow loading exposure, and extreme Arctic weather. When local winter storm risk is elevated, weight shifts to structural metrics. Incorporates FMI weather forecasts and SYKE ice/snow mapping.", formula:"IRI_forward(m,s) = IRI_current(m,s) × (1 + 0.15 × clip(Δ_climate, −0.50, +1.00))", sources:["FMI","SYKE","COPERNICUS ERA5","GTK"], isEnhanced:true },
    { id:"R3", name:"Consequence + Arctic Remoteness + Population Sparsity", range:"[0.70, 1.35]", type:"Multiplicative", desc:"Amplifies risk for communities with sparse population, Arctic remoteness, or high energy dependency. Includes vulnerability indices (Tilastokeskus demographics), elderly exposure in Lappi, and isolation metrics for northern regions.", formula:"C_mult = sigmoid(pop_weight × remote_weight × V_socio × arctic_factor)", sources:["Tilastokeskus","EUROSTAT","Posti"], isEnhanced:true },
    { id:"R4", name:"Graph Criticality + Network Constraint", range:"[0.80, 1.40]", type:"Multiplicative", desc:"Penalises topological bottlenecks in Fingrid 400kV backbone and DSO networks: high betweenness centrality, bridge nodes, low degree. Built from OSM power graph and Fingrid transmission constraints.", formula:"F_topo = f(degree, BC_percentile, is_bridge, fingrid_tier)", sources:["OSM","Fingrid"], isEnhanced:true },
    { id:"R6a", name:"Restoration Speed (Winter Storm Focus)", range:"[0.90, 1.10]", type:"Multiplicative", desc:"Energiavirasto-CAIDI-based: rewards fast-restoring areas, penalises slow ones in Lappi/Kainuu. Two substations with identical SAIDI can have different risk profiles based on restoration speed in remote northern regions.", formula:"R6a = sigmoid_bounded(CAIDI_local / CAIDI_fleet_median)", sources:["Energiavirasto","Fingrid"], isEnhanced:true },
    { id:"R6b", name:"Winter Storm + Snow Loading Overlay (CRITICAL FOR FINLAND)", range:"[1.00, 1.25]", type:"Multiplicative", desc:"FMI winter storm hazard + SYKE snow/ice loading overlay. Penalises substations in high-storm zones or heavy snow-loading regions. Integration of real-time FMI warnings and historical winter event impacts.", formula:"R6b = f(FMI_storm_percentile, SYKE_snow_loading, ice_hazard_proximity)", sources:["FMI","SYKE","GTK","VesiArc"], isEnhanced:true },
    { id:"R7", name:"Digital Readiness + Cyber-Physical Resilience", range:"[0.99, 1.05]", type:"Multiplicative", desc:"Cyber-physical security baseline, SCADA maturity proxy (Finland high), and microgrid/islanding capability. Indicates digital resilience capability at the grid edge for winter event recovery scenarios.", formula:"Cyber = f(SCADA_maturity, microgrid_pct, islanding_capability)", sources:["Fingrid","Energiavirasto"], isEnhanced:false }
  ],

  /* ── processing pipeline ── */
  PIPELINE: [
    { step:1, name:"Ingest", desc:"95 variables from 30 verified Finnish public data sources — Fingrid, Energiavirasto, Tilastokeskus, FMI, GTK, SYKE, STUK, and others. Zero proprietary SCADA dependencies. Maximum ingestion frequency: real-time (Fingrid dispatch data).", icon:"📥" },
    { step:2, name:"Normalise", desc:"Four normalisation methods: Method A (robust fleet percentile P5/P95), Method B (inverse fleet percentile for density), Method C (binary compliance), and Method D (categorical mapping). Inverted metrics for density measures where higher = better resilience.", icon:"📐" },
    { step:3, name:"Weight", desc:"6-level hierarchical weighting across 6 components and 20 metrics. Continuity dominates at 0.30, Infrastructure at 0.25 (with higher winter storm/snow loading I5 weight), Saturation at 0.20. Weight budget validated by Sobol sensitivity analysis.", icon:"⚖️" },
    { step:4, name:"Compose R_base", desc:"Weighted sum of 6 normalised component scores produces the base resilience score.", icon:"🧮" },
    { step:5, name:"Modify", desc:"Seven multiplicative modifiers adjust R_base for Finnish context: R2 (adaptive climate + winter storm trajectory), R3 (consequence + Arctic remoteness + population sparsity), R4 (graph criticality + Fingrid/DSO constraints), R6a (restoration speed in remote areas), R6b (winter storm/snow loading overlay — CRITICAL), R7 (digital readiness). Plus enrichments for vulnerable populations, winter storm zones, and critical infrastructure.", icon:"🔧" },
    { step:6, name:"Monte Carlo", desc:"2,000 iterations per substation using a 20×20 Gaussian copula correlation matrix. Captures measurement, spatial, staleness, and model uncertainty. Produces median, P5, P95, skewness, and P_critical for each substation.", icon:"🎲" },
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
    { id:"A",   name:"SSI v4.0.2 Resilience (Finland)",             vars:20, status:"LIVE",    sources:"Fingrid · Energiavirasto · Tilastokeskus · FMI · SYKE · STUK" },
    { id:"B.1", name:"Grid Telemetry: Open",                       vars:3,  status:"LIVE",    sources:"FMI / ERA5 · Fingrid" },
    { id:"B.2", name:"Grid Telemetry: Proxy",                      vars:4,  status:"LIVE",    sources:"IEEE C57.91 · DSO · Energiavirasto" },
    { id:"B.3", name:"Grid Telemetry: Fuzzy",                      vars:12, status:"FUZZY",   sources:"IEEE/CIGRÉ standards · GTK" },
    { id:"C",   name:"Socio-Economic + Arctic Demographics",        vars:10, status:"LIVE",    sources:"Tilastokeskus · EUROSTAT · Suomen Pankki · Business Finland" },
    { id:"D",   name:"Environmental Hazards (Winter Storm+Flooding)",vars:8,  status:"LIVE",    sources:"FMI · SYKE · GTK · Copernicus · VesiArc" },
    { id:"E",   name:"Finnish Open Data + Energy Policy",            vars:9,  status:"LIVE",    sources:"Energiavirasto · Finnish Wind Power · LUKE · MOTIVA" },
    { id:"F",   name:"Network Transitions + Nuclear Baseload",       vars:12, status:"BAYESIAN",sources:"DSO history OR IEEE/CIGRÉ + priors" },
    { id:"G",   name:"Modifier Inputs (Winter Storm-Weighted)",      vars:4,  status:"LIVE",    sources:"Energiavirasto reliability · FMI · OSM" },
    { id:"H",   name:"Network & Topology (Fingrid 400kV)",           vars:7,  status:"LIVE",    sources:"Fingrid · ENTSO-E · OSM" },
    { id:"I",   name:"Output Scores + Alert Flags",                 vars:7,  status:"LIVE",    sources:"Fleet Markov Chain · IEEE/CIGRÉ analysis" }
  ],

  /* ── validation framework ── */
  VALIDATION_CHECKS: [
    { check:"North–South latitude gradient",                        criterion:"Northern Finland (Lappi/Kainuu) R systematically higher than southern regions due to Arctic conditions",                                      status:"expected" },
    { check:"Winter storm–I5 coherence (FMI)",                      criterion:"Substations in high-storm zones show elevated I5 scores — 2010/2011/2024 winter events",                                                        status:"expected" },
    { check:"Snow/ice loading–I7 agreement (SYKE)",                 criterion:"Northern substations with heavy snow loading show elevated I7 scores, especially overhead transmission",                                        status:"expected" },
    { check:"Nuclear concentration–I9 signal (STUK)",               criterion:"Substations near/feeding Olkiluoto + Loviisa show elevated I9 scores; 33% baseload concentration",                                            status:"expected" },
    { check:"RE stress–wind correlation (Pohjanmaa)",               criterion:"Western coastal regions with high wind penetration show elevated S2 scores",                                                                   status:"expected" },
    { check:"Arctic thermal preservation check",                    criterion:"Permafrost/Arctic stability metrics align with I6 corrosion class and I3 thermal stress",                                                    status:"expected" },
    { check:"Fennoscandian Shield seismic baseline",                criterion:"Seismic risk negligible (α=0.10 relative to European baseline); validation confirms no anomalies",                                          status:"expected" },
    { check:"Spring snowmelt flooding–I5 agreement",                criterion:"Vesivaara/Kymenlaakso river systems show elevated I5 during spring; FMI flood forecasts validate",                                          status:"expected" },
    { check:"RE stress vs EV load correlation",                     criterion:"S2 (RE stress) and S3 (EV penetration) positively correlated in urban areas (Helsinki, Tampere, Turku)",                                      status:"nascent" },
    { check:"Monte Carlo convergence (CV < 2%)",                    criterion:"Coefficient of variation < 2% at 2,000 iterations for all substations",                                                                      status:"expected" },
    { check:"Weight budget unity",                                  criterion:"Component weights sum to 1.0000; all intra-weights sum to 1.0000 per component",                                                              status:"expected" },
    { check:"Modifier range adherence",                             criterion:"All modifiers stay within declared [min, max] bounds across the fleet",                                                                       status:"expected" },
    { check:"Band boundary contiguity",                             criterion:"No gap or overlap between Low/Medium/High/Critical thresholds",                                                                                status:"expected" },
    { check:"R3 consequence signal + remoteness",                   criterion:"High-remoteness, sparse-population areas consistently score higher R3 multiplier (Lappi/Kainuu/Pohjanmaa)",                                   status:"expected" },
    { check:"R6b winter storm/snow sensitivity (CRITICAL)",         criterion:"Winter storm proximity drives R6b up to 1.25 ceiling; snow loading overlay independent of other modifiers",                                  status:"critical" },
    { check:"Fingrid vs DSO constraint signal",                     criterion:"Fingrid 400kV backbone substations score higher R4; DSO periphery lower due to topology",                                                    status:"expected" }
  ],

  /* ── changelog v3.4 → v4.0.2 (Finland edition) ── */
  CHANGELOG: [
    { id:"FI1",  change:"Finland country launch — 1,200 substations across 19 maakunnat, administrative kunta level",                                                type:"new" },
    { id:"FI2",  change:"Integrated Fingrid transmission dispatch data + Energiavirasto reliability benchmarks",                                                    type:"data" },
    { id:"FI3",  change:"Energiavirasto reliability register integrated — SAIDI/SAIFI standardisation for all DSOs",                                               type:"data" },
    { id:"FI4",  change:"FMI winter storm hazard integrated — critical for Arctic/boreal climate exposure assessment",                                             type:"data" },
    { id:"FI5",  change:"SYKE snow/ice loading mapping integrated — overhead transmission line vulnerability in north",                                             type:"data" },
    { id:"FI6",  change:"STUK nuclear concentration risk indicator — Olkiluoto + Loviisa baseload (33% of Finnish generation)",                                  type:"data" },
    { id:"FI7",  change:"FMI + SYKE climate integration — winter storm risk, snow accumulation, Arctic wind patterns",                                             type:"data" },
    { id:"FI8",  change:"Tilastokeskus Census 2021 + Eurostat socio-economic data integrated — vulnerability indices per kunta",                                  type:"data" },
    { id:"FI9",  change:"Finnish Wind Power + MOTIVA data integrated — RE penetration for western/coastal regions (Pohjanmaa)",                                   type:"data" },
    { id:"FI10", change:"Suomen Pankki thermal cycle coupling integrated — E1 volatility modulation for hydropower-dependent regions",                            type:"new" },
    { id:"FI11", change:"R6b modifier enhanced with dual FMI winter storm + SYKE snow loading hazard (range 1.00–1.25)",                                         type:"enhanced" },
    { id:"FI12", change:"R3 consequence enriched with Arctic remoteness, population sparsity, Lappi/Kainuu isolation metrics",                                   type:"enhanced" },
    { id:"FI13", change:"R4 graph criticality rebuilt with Fingrid 400kV topology + DSO network constraints — north-south transmission corridor penalty",         type:"enhanced" },
    { id:"FI14", change:"I9 Nuclear Concentration Risk — new metric from STUK nuclear safety data for Olkiluoto + Loviisa proximity",                            type:"new" },
    { id:"FI15", change:"R2 Adaptive IRI now includes CMIP6 SSP2-4.5 forward projections for Arctic winter extremes & permafrost thaw",                           type:"enhanced" }
  ],

  /* ── fleet stats (placeholder — updated by ssi-data.json at runtime) ── */
  FREQ_DISTRIBUTION: {
      "Real-time": { count: 3, sources: ['Fingrid Dispatch', 'FMI Warnings', 'Fingrid Open Data'] },
      "Hourly":    { count: 2, sources: ['Fingrid Generation', 'ENTSO-E Flows'] },
      "Daily":     { count: 3, sources: ['FMI Weather', 'Copernicus ERA5', 'Fingrid Load'] },
      "Monthly":   { count: 5, sources: ['Energiavirasto Reports', 'Suomen Pankki Economics', 'Tilastokeskus Updates', 'Finnish Wind Power', 'STUK Safety'] },
      "Quarterly": { count: 4, sources: ['Energiavirasto Reports', 'DSO Performance', 'FMI Forecasts', 'EUROSTAT Arctic' } },
      "Annual":    { count: 8, sources: ['Tilastokeskus Census Updates', 'Energiavirasto Inspections', 'FMI Climate', 'GTK Geology', 'SYKE Environment', 'DSO Annual Reports', 'LUKE Forest', 'World Bank'] },
      "Static":    { count: 3, sources: ['OSM Power', 'Metsähallitus Geodesy', 'SolarGIS'] },
      "5-Year":    { count: 2, sources: ['Tilastokeskus Census 2021', 'CMIP6 Cycle'] }
    },
  stats: {
      variables: 95,
      metrics: 20,
      components: 6,
      modifiers: 7,
      sources: 30,
      substations: 1200,
      powerLines: 2500,
      mcIterations: 2000,
      maakunta: 19,
      kunta: 310
    }
};


/* ═══════════════════════════════════════════════
   Legacy flat format — backward compatibility
   Used by overview.html, regional.html, map.html
   ═══════════════════════════════════════════════ */

window.SSI_METADATA = {
  country: "Finland",
  country_code: "FI",
  flag: "🇫🇮",
  currency: "€",
  version: "4.0.2",
  edition: "001",
  edition_month: "March 2026",
  substations_label: "substations",
  region_label: "Maakunta",
  region_label_plural: "Maakunnat",
  admin_division_label: "Kunta",
  admin_division_label_short: "Kunta",
  total_substations: 1200,
  total_powiats: 310,
  total_regions: 19,
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
  monte_carlo: { iterations:2000, correlation_matrix:"20×20", seed:42, confidence_interval:0.95 },
  regions: [
    "Uusimaa",
    "Varsinais-Suomi",
    "Satakunta",
    "Kanta-Häme",
    "Pirkanmaa",
    "Päijät-Häme",
    "Kymenlaakso",
    "Etelä-Karjala",
    "Etelä-Savo",
    "Pohjois-Savo",
    "Pohjois-Karjala",
    "Keski-Suomi",
    "Etelä-Pohjanmaa",
    "Pohjanmaa",
    "Keski-Pohjanmaa",
    "Pohjois-Pohjanmaa",
    "Kainuu",
    "Lappi",
    "Ahvenanmaa"
  ]
};
