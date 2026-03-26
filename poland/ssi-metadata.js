/*  SSI v4.0.2 — Metadata Registry · Poland
    Loaded by every page in /poland/.
    ──────────────────────────────────────────────
    Exports:  window.SSIMetadata   (structured, matches Poland/Chile format exactly)
              window.SSI_METADATA  (legacy flat, backward-compat)              */

window.SSIMetadata = {

  /* ── 30 verified data sources — Polish institutions ── */
  DATA_SOURCES: [
    { id:"PSE",    name:"PSE — Polskie Sieci Elektroenergetyczne", url:"pse.pl", freq:"Real-time", res:"Substation", vars:14, category:"Grid", feeds:"C1–C4, I2, S1–S2, transmission network topology, dispatch data" },
    { id:"URE",    name:"URE — Urząd Regulacji Energetyki", url:"ure.gov.pl", freq:"Quarterly", res:"DSO", vars:12, category:"Grid", feeds:"C1–C4, V1–V2, I1, reliability metrics, technical standards", registration:true },
    { id:"GUS",    name:"GUS — Główny Urząd Statystyczny", url:"stat.gov.pl", freq:"Annual", res:"Powiat", vars:10, category:"Socio-Econ", feeds:"C1–C4, safety compliance, Census 2021, demographics, income" },
    { id:"IMGW",   name:"IMGW-PIB — Meteorology & Water", url:"danepubliczne.imgw.pl", freq:"Daily", res:"Station", vars:8, category:"Climate", feeds:"I3 (thermal stress), humidity, wind, precipitation, flood warnings, drought" },
    { id:"PIG",    name:"PIG-PIB — Geological Institute", url:"pgi.gov.pl", freq:"Annual", res:"Grid 0.1°", vars:7, category:"Hazard", feeds:"I5 (flood risk), mining subsidence mapping, geological data" },
    { id:"WUG",    name:"WUG — State Mining Authority", url:"wug.gov.pl", freq:"Static", res:"Grid 0.1°", vars:6, category:"Hazard", feeds:"I7 (mining subsidence zone), seismic monitoring, ground deformation" },
    { id:"GIOS",   name:"GIOŚ — Environmental Inspection", url:"gios.gov.pl", freq:"Real-time", res:"Station", vars:8, category:"Environment", feeds:"I6 (corrosion class, SO₂, PM exposure), air quality network" },
    { id:"UDT",    name:"UDT — Technical Inspection Office", url:"udt.gov.pl", freq:"Annual", res:"Distribution Company", vars:9, category:"Grid", feeds:"E1–E3, equipment compliance, transformer inspections, asset registration" },
    { id:"OSM",    name:"OpenStreetMap — Power Infrastructure", url:"overpass-api.de", freq:"Continuous", res:"Node", vars:8, category:"Infrastructure", feeds:"I4 (graph degree), topology, 1,685 substations mapped, PSE/DSO networks" },
    { id:"COPER",  name:"Copernicus ERA5 — Climate Reanalysis", url:"cds.climate.copernicus.eu", freq:"Monthly", res:"Grid 0.25°", vars:6, category:"Climate", feeds:"Thermal stress, humidity, wind, CMIP6 forward projections for flood risk" },
    { id:"KZGW",   name:"KZGW — Wody Polskie (Water Authority)", url:"wody.gov.pl", freq:"Annual", res:"Coastal Grid", vars:5, category:"Hazard", feeds:"I5 (flood hazard ISOK maps), river basin plans, drought data, water stress" },
    { id:"KOBiZE", name:"KOBiZE — National Emissions Centre", url:"kobize.pl", freq:"Quarterly", res:"Mining Region", vars:4, category:"Industrial", feeds:"I9 (coal transition risk), CO₂ emissions by installation, EU ETS data" },
    { id:"GUGiK",  name:"GUGiK — Geodesy & Cartography", url:"geoportal.gov.pl", freq:"Annual", res:"Utility Service", vars:5, category:"Environment", feeds:"Land use, infrastructure mapping, BDOT10k database, DEM, orthophotos" },
    { id:"ARE",    name:"ARE — Energy Market Agency", url:"are.waw.pl", freq:"Monthly", res:"Region", vars:4, category:"Transition", feeds:"E1 (energy balances by województwo), coal consumption trends, RE targets" },
    { id:"NBP",    name:"NBP — National Bank of Poland", url:"nbp.pl", freq:"Monthly", res:"National", vars:5, category:"Economic", feeds:"E1 variant (energy price index), GDP by województwo, economic cycles" },
    { id:"PSEW",   name:"PSEW — Polish Wind Energy Assoc.", url:"psew.pl", freq:"Monthly", res:"Regional", vars:5, category:"Transition", feeds:"S1 (RE capacity), T1–T2, wind capacity by region, curtailment data" },
    { id:"IEO",    name:"IEO — Institute for Renewable Energy", url:"ieo.pl", freq:"Annual", res:"Region", vars:3, category:"Transition", feeds:"S1 (DER/PV penetration), T1 (solar capacity), prosumer statistics" },
    { id:"DSO",    name:"DSO Reports (PGE, Tauron, Enea, Energa, Stoen)", url:"", freq:"Annual", res:"Distribution Company", vars:4, category:"Grid", feeds:"S1 variant (thermal plant load), CAPEX, SAIDI/SAIFI, transformer inventories" },
    { id:"ENTSO",  name:"ENTSO-E Transparency Platform", url:"transparency.entsoe.eu", freq:"Hourly", res:"Substation", vars:2, category:"Grid", feeds:"C1 (capacity), cross-border flows, generation adequacy" },
    { id:"EURO",   name:"Eurostat — EU Statistics", url:"ec.europa.eu/eurostat", freq:"Annual", res:"Comuna", vars:3, category:"Socio-Econ", feeds:"E2 (population served), water-energy nexus, SILC energy poverty" },
    { id:"MARINE", name:"IPCC / Copernicus Marine", url:"climate.copernicus.eu", freq:"Static", res:"Coastal Grid", vars:2, category:"Environment", feeds:"D5 (Baltic sea-level rise projections), coastal models, erosion risk" },
    { id:"SOLAR",  name:"SolarGIS — Global Solar Atlas", url:"globalsolaratlas.info", freq:"Static", res:"Global", vars:3, category:"Transition", feeds:"T1 (PV resource mapping), solar irradiance (GHI, DNI) for Poland" },
    { id:"HEALTH", name:"Ministry of Health / NFZ", url:"", freq:"Annual", res:"Health District", vars:3, category:"Socio-Econ", feeds:"E2 (hospital locations), critical infrastructure mapping, healthcare criticality" },
    { id:"BGK",    name:"BGK — National Development Bank", url:"bgk.pl", freq:"Annual", res:"Region", vars:5, category:"Economic", feeds:"E3 (business density), infrastructure investment data by województwo" },
    { id:"RDOS",   name:"RDOŚ — Environmental Directorates", url:"", freq:"Annual", res:"Protected Area", vars:4, category:"Environment", feeds:"E2 variant (Natura 2000), protected areas, environmental constraints" },
    { id:"INTERIOR", name:"Ministry of Interior — Migration", url:"", freq:"Annual", res:"Comuna", vars:5, category:"Socio-Econ", feeds:"E2–E3, residence permits, Ukrainian refugee data, net migration" },
    { id:"PORTS",  name:"Port Authority (Gdańsk, Gdynia, Szczecin)", url:"", freq:"Quarterly", res:"Mining District", vars:3, category:"Industrial", feeds:"Regional economic proxy, Baltic shipping impact" },
    { id:"GDDKiA", name:"GDDKiA — Road Infrastructure", url:"gddkia.gov.pl", freq:"Annual", res:"Road Network", vars:3, category:"Environment", feeds:"Infrastructure density proxy, transport nodes" },
    { id:"CIREN",  name:"CIREN — Soil Data (PIG supplement)", url:"", freq:"Annual", res:"Grid 1 km", vars:6, category:"Infrastructure", feeds:"I6 (ISO 9223 corrosion by soil), soil properties, vegetation index" },
    { id:"WORLD",  name:"World Bank / OECD", url:"", freq:"Annual", res:"National", vars:4, category:"Socio-Econ", feeds:"International benchmarks, socio-economic indicators, cross-validation" }
  ],

  /* ── 6 components · 20 metrics ── */
  COMPONENTS: [
    {
      id:"C", name:"Continuity", weight:0.30, color:"#941914",
      desc:"Measures reliability and outage exposure — how often and how long power interruptions occur.",
      metrics:[
        { id:"C1", name:"Outage Duration (SAIDI)", intra:0.35, global:0.105, norm:"A (P5/P95)", source:"PSE / URE", desc:"Total annual interruption duration per customer", inverted:false, adaptive:false, isNew:false },
        { id:"C2", name:"Outage Frequency (SAIFI)", intra:0.30, global:0.090, norm:"A (P5/P95)", source:"PSE / URE", desc:"Number of sustained interruptions per customer per year", inverted:false, adaptive:false, isNew:false },
        { id:"C3", name:"Restoration Time (CAIDI)", intra:0.20, global:0.060, norm:"A (P5/P95)", source:"URE / DSO", desc:"Average duration of each interruption (DSO-dependent)", inverted:false, adaptive:false, isNew:false },
        { id:"C4", name:"Momentary Interruptions (MAIFI)", intra:0.15, global:0.045, norm:"A (P5/P95)", source:"PSE", desc:"Momentary average interruption frequency index", inverted:false, adaptive:false, isNew:false }
      ]
    },
    {
      id:"V", name:"Voltage Quality", weight:0.10, color:"#aa4234",
      desc:"Captures voltage stability, power factor, and harmonic distortion at the distribution level.",
      metrics:[
        { id:"V1", name:"Voltage Deviation (ΔV)", intra:0.40, global:0.040, norm:"A (P5/P95)", source:"URE / DSO", desc:"Percentage deviation from nominal voltage", inverted:false, adaptive:false, isNew:false },
        { id:"V2", name:"THD (Harmonic Distortion)", intra:0.30, global:0.030, norm:"A (P5/P95)", source:"URE", desc:"Total harmonic distortion percentage", inverted:false, adaptive:false, isNew:false },
        { id:"V3", name:"Power Factor", intra:0.30, global:0.030, norm:"B (inverse)", source:"URE / DSO", desc:"Ratio of real to apparent power — higher is better", inverted:true, adaptive:false, isNew:false }
      ]
    },
    {
      id:"I", name:"Infrastructure", weight:0.25, color:"#5d8563",
      desc:"Assesses physical asset condition, age, capacity, flood/mining subsidence exposure (critical for Poland).",
      metrics:[
        { id:"I1", name:"Asset Age Index", intra:0.12, global:0.030, norm:"A (P5/P95)", source:"URE / GUS", desc:"Fleet-normalised average asset age (PRL-era vintage estimates)", inverted:false, adaptive:false, isNew:false },
        { id:"I2", name:"Capacity Utilisation", intra:0.12, global:0.030, norm:"A (P5/P95)", source:"PSE / URE", desc:"Percentage of rated capacity in use", inverted:false, adaptive:false, isNew:false },
        { id:"I3", name:"Climate IRI (Thermal + Flood Stress)", intra:0.12, global:0.030, norm:"A (P5/P95)", source:"IMGW / CIREN / ERA5", desc:"Infrastructure Risk Index based on thermal extremes, flood risk, and drought indices", inverted:false, adaptive:true, isNew:false },
        { id:"I4", name:"Graph Degree (Topology)", intra:0.12, global:0.030, norm:"B (inverse)", source:"OSM / PSE", desc:"Number of connections — higher degree = more redundancy", inverted:true, adaptive:false, isNew:false },
        { id:"I5", name:"Flood Risk + Mining Subsidence Hazard", intra:0.18, global:0.045, norm:"A (P5/P95)", source:"KZGW / WUG / PIG", desc:"Combined flood inundation hazard (Vistula/Oder basins) + mining subsidence risk (critical for Poland)", inverted:false, adaptive:false, isNew:false },
        { id:"I6", name:"Corrosion Class", intra:0.10, global:0.025, norm:"D (categorical)", source:"ISO9223 / GIOS", desc:"Environmental corrosion exposure based on humidity, SO₂ exposure (industrial regions)", inverted:false, adaptive:false, isNew:false, categorical:true },
        { id:"I7", name:"Mining Subsidence Zone", intra:0.12, global:0.030, norm:"D (categorical)", source:"WUG / PIG", desc:"Mining hazard classification from WUG/PIG subsidence mapping (Upper Silesia focus)", inverted:false, adaptive:true, isNew:false, categorical:true },
        { id:"I8", name:"N-1 Compliance", intra:0.05, global:0.0125, norm:"C (binary)", source:"PSE", desc:"Whether substation meets N-1 redundancy standard (PSE 400kV backbone)", inverted:true, adaptive:false, isNew:false },
        { id:"I9", name:"Coal Transition Risk", intra:0.07, global:0.0175, norm:"D (categorical)", source:"KOBiZE / ARE", desc:"Stranding risk for substations feeding aging coal infrastructure (Poland-specific)", inverted:false, adaptive:false, isNew:true, categorical:true }
      ]
    },
    {
      id:"E", name:"Economic", weight:0.10, color:"#3b9eff",
      desc:"Links grid risk to regional economic exposure — energy pricing, unemployment, and industrial cycles.",
      metrics:[
        { id:"E1", name:"Energy Price Index + Coal Cycle", intra:0.40, global:0.040, norm:"A (P5/P95)", source:"NBP / ARE / PSEW", desc:"Wholesale + retail electricity cost per MWh, modulated by coal market volatility", inverted:false, adaptive:true, isNew:false },
        { id:"E2", name:"Unemployment Rate", intra:0.30, global:0.030, norm:"A (P5/P95)", source:"GUS / Eurostat", desc:"Powiat-level unemployment rate (Census 2021 baseline)", inverted:false, adaptive:false, isNew:false },
        { id:"E3", name:"Business Density + Industrial Concentration", intra:0.30, global:0.030, norm:"A (P5/P95)", source:"BGK / GUS / URE", desc:"Economic activity clusters and large industrial load concentration", inverted:false, adaptive:false, isNew:false }
      ]
    },
    {
      id:"S", name:"Saturation", weight:0.20, color:"#b88f3e",
      desc:"Quantifies DER/RE penetration stress, reverse power flow risk, and EV charging load on the grid.",
      metrics:[
        { id:"S1", name:"Renewable Energy Capacity Ratio", intra:0.35, global:0.070, norm:"A (P5/P95)", source:"PSEW / PSE / ARE", desc:"Total installed RE (wind/solar) capacity relative to substation rating", inverted:false, adaptive:false, isNew:false },
        { id:"S2", name:"RE Stress Index (Variability + Curtailment)", intra:0.35, global:0.070, norm:"A (P5/P95)", source:"PSEW / PSE", desc:"Composite stress: RE penetration × output variability × transmission constraints", inverted:false, adaptive:true, isNew:false },
        { id:"S3", name:"EV Penetration Rate (Emerging)", intra:0.30, global:0.060, norm:"A (P5/P95)", source:"ARE / Transport Ministry", desc:"EV registrations as percentage of total fleet in catchment area (nascent adoption)", inverted:false, adaptive:false, isNew:true }
      ]
    },
    {
      id:"T", name:"Energy Transition", weight:0.05, color:"#0e7490", isNew:true,
      desc:"Measures clean energy transition pace and grid readiness for decarbonisation (RE targets: 32% by 2030).",
      metrics:[
        { id:"T1", name:"Renewable Energy Share (%)", intra:0.50, global:0.025, norm:"B (inverse)", source:"PSEW / PSE / ARE", desc:"Share of generation from renewables — higher share = lower risk (inverted)", inverted:true, adaptive:false, isNew:false },
        { id:"T2", name:"Transition Readiness Score", intra:0.50, global:0.025, norm:"A (P5/P95)", source:"ARE / PSEW / PSE", desc:"Composite readiness: grid flexibility + storage deployment + DSO interconnection capacity", inverted:true, adaptive:false, isNew:true }
      ]
    }
  ],

  /* ── 7 modifiers (R2–R7, incl. R6a + R6b flood/subsidence) ── */
  MODIFIERS: [
    { id:"R2", name:"Adaptive Climate IRI + Hazard Trajectory", range:"Weight redistribution", type:"Weight modifier", desc:"Uses CMIP6 SSP2-4.5 projections to adjust IRI metrics for flood risk, mining subsidence exposure, and extreme weather events. When local flood risk is elevated, weight shifts to structural metrics. Incorporates KZGW water availability forecasts and IMGW precipitation projections.", formula:"IRI_forward(m,s) = IRI_current(m,s) × (1 + 0.15 × clip(Δ_climate, −0.50, +1.00))", sources:["IMGW","CIREN","KZGW","Copernicus ERA5"], isEnhanced:true },
    { id:"R3", name:"Consequence + Energy Poverty + Coal Dependency", range:"[0.70, 1.35]", type:"Multiplicative", desc:"Amplifies risk for communities serving large populations, energy-poor households, or high coal-industry dependency. Includes vulnerability indices (GUS Census 2021), elderly exposure, and mining-region proximity.", formula:"C_mult = sigmoid(pop_weight × load_weight × V_socio × coal_factor)", sources:["GUS","EURO","Eurostat SILC","KOBiZE"], isEnhanced:true },
    { id:"R4", name:"Graph Criticality + Network Constraint", range:"[0.80, 1.40]", type:"Multiplicative", desc:"Penalises topological bottlenecks in PSE 400kV backbone and 5 DSO networks: high betweenness centrality, bridge nodes, low degree. Built from OSM power graph and PSE transmission constraints.", formula:"F_topo = f(degree, BC_percentile, is_bridge, pse_tier)", sources:["OSM","PSE"], isEnhanced:true },
    { id:"R6a", name:"Restoration Speed", range:"[0.90, 1.10]", type:"Multiplicative", desc:"URE-CAIDI-based: rewards fast-restoring areas, penalises slow ones. Two substations with identical SAIDI can have different risk profiles based on restoration speed in remote województwa.", formula:"R6a = sigmoid_bounded(CAIDI_local / CAIDI_fleet_median)", sources:["URE","PSE"], isEnhanced:true },
    { id:"R6b", name:"Flood + Mining Subsidence Overlay (CRITICAL FOR POLAND)", range:"[1.00, 1.50]", type:"Multiplicative", desc:"KZGW flood hazard + WUG mining subsidence overlay. Penalises substations in high-flood zones (Vistula/Oder basins) or mining subsidence risk areas (Upper Silesia). Integration of IMGW flood warnings.", formula:"R6b = f(KZGW_flood_percentile, WUG_subsidence_hazard, flood_zone_proximity)", sources:["KZGW","WUG","IMGW","PIG"], isEnhanced:true },
    { id:"R7", name:"Digital Readiness + Cyber-Physical Resilience", range:"[0.99, 1.05]", type:"Multiplicative", desc:"Cyber-physical security baseline, SCADA maturity proxy, and microgrid/islanding capability. Indicates digital resilience capability at the grid edge for flood/mining-event recovery scenarios.", formula:"Cyber = f(SCADA_maturity, microgrid_pct, islanding_capability)", sources:["PSE","URE"], isEnhanced:false }
  ],

  /* ── processing pipeline ── */
  PIPELINE: [
    { step:1, name:"Ingest", desc:"95 variables from 30 verified Polish public data sources — PSE, URE, GUS, IMGW, PIG, WUG, GIOŚ, KOBiZE, and others. Zero proprietary SCADA dependencies. Maximum ingestion frequency: real-time (PSE dispatch data).", icon:"📥" },
    { step:2, name:"Normalise", desc:"Four normalisation methods: Method A (robust fleet percentile P5/P95), Method B (inverse fleet percentile for density), Method C (binary compliance), and Method D (categorical mapping). Inverted metrics for density measures where higher = better resilience.", icon:"📐" },
    { step:3, name:"Weight", desc:"6-level hierarchical weighting across 6 components and 20 metrics. Continuity dominates at 0.30, Infrastructure at 0.25 (with higher flood/subsidence I5 weight), Saturation at 0.20. Weight budget validated by Sobol sensitivity analysis.", icon:"⚖️" },
    { step:4, name:"Compose R_base", desc:"Weighted sum of 6 normalised component scores produces the base resilience score.", icon:"🧮" },
    { step:5, name:"Modify", desc:"Seven multiplicative modifiers adjust R_base for Polish context: R2 (adaptive climate + flood trajectory), R3 (consequence + energy poverty + coal dependency), R4 (graph criticality + PSE/DSO constraints), R6a (restoration speed), R6b (flood/mining overlay — CRITICAL), R7 (digital readiness). Plus enrichments for vulnerable populations, flood zones, mining regions, and healthcare criticality.", icon:"🔧" },
    { step:6, name:"Monte Carlo", desc:"2,000 iterations per substation using a 20×20 Gaussian copula correlation matrix. Captures measurement, spatial, staleness, and model uncertainty. Produces median, P5, P95, skewness, and P_critical for each substation.", icon:"🎲" },
    { step:7, name:"Classify", desc:"Four bands: Low (0.00–0.25), Medium (0.25–0.50), High (0.50–0.75), Critical (0.75–1.00). Alert flags trigger when any single component exceeds its P95 fleet threshold. Flood/mining events escalate classification instantaneously.", icon:"🏷️" }
  ],

  /* ── classification bands ── */
  CLASSIFICATION: [
    { name:"Low",      range:"0.00 – 0.25", meaning:"Good resilience — stable grid, low exposure",       expected:"~35–40%", color:"#5d8563" },
    { name:"Medium",   range:"0.25 – 0.50", meaning:"Moderate risk — some vulnerabilities present",       expected:"~32–38%", color:"#b88f3e" },
    { name:"High",     range:"0.50 – 0.75", meaning:"Elevated risk — investment priority zone",           expected:"~18–23%", color:"#aa4234" },
    { name:"Critical", range:"0.75 – 1.00", meaning:"Severe vulnerability — urgent intervention required", expected:"~5–10%",   color:"#941914" }
  ],

  /* ── master equation ── */
  MASTER_EQUATION: "R_final = soft_clip_upper( R_base × F_topo × C_mult × R6a_mult × R6b_flood_subsidence × Cyber_factor )",

  /* ── normalisation methods ── */
  NORM_METHODS: [
    { id:"A", name:"Fleet Percentile (robust)", formula:"N(x) = soft_clip((x − P₅) / (P₉₅ − P₅))", applies:"C1, C2, C3, C4, V1, V2, I1, I2, I3, I5, E1, E2, E3, S1, S2, S3" },
    { id:"B", name:"Fleet Percentile (inverse)", formula:"N(x) = 1 − soft_clip((x − P₅) / (P₉₅ − P₅))", applies:"V3, I4, T1, T2" },
    { id:"C", name:"Binary (bounded)", formula:"N(x) = 0 if compliant, 1 if non-compliant", applies:"I8 (N-1 compliance)" },
    { id:"D", name:"Categorical Mapping", formula:"N(x) = lookup_table(class → [0, 1])", applies:"I6 (corrosion), I7 (mining subsidence), I9 (coal transition)" }
  ],

  /* ── 11 data layers · 95 variables ── */
  DATA_LAYERS: [
    { id:"A",   name:"SSI v4.0.2 Resilience (Poland)",             vars:20, status:"LIVE",    sources:"PSE · URE · GUS · IMGW · WUG · KZGW" },
    { id:"B.1", name:"Grid Telemetry: Open",                       vars:3,  status:"LIVE",    sources:"IMGW / ERA5 · PSE" },
    { id:"B.2", name:"Grid Telemetry: Proxy",                      vars:4,  status:"LIVE",    sources:"IEEE C57.91 · DSO · URE" },
    { id:"B.3", name:"Grid Telemetry: Fuzzy",                      vars:12, status:"FUZZY",   sources:"IEEE/CIGRÉ standards · PIG" },
    { id:"C",   name:"Socio-Economic + Coal Dependency",            vars:10, status:"LIVE",    sources:"GUS · Eurostat · NBP · KOBiZE" },
    { id:"D",   name:"Environmental Hazards (Flood+Subsidence)",    vars:8,  status:"LIVE",    sources:"KZGW · WUG · PIG · Copernicus" },
    { id:"E",   name:"Polish Open Data + Energy Policy",            vars:9,  status:"LIVE",    sources:"ARE · PSEW · IEO · URE" },
    { id:"F",   name:"Network Transitions + Coal Phase-out",        vars:12, status:"BAYESIAN",sources:"DSO history OR IEEE/CIGRÉ + priors" },
    { id:"G",   name:"Modifier Inputs (Flood-Weighted)",            vars:4,  status:"LIVE",    sources:"URE reliability · KZGW · OSM" },
    { id:"H",   name:"Network & Topology (PSE 400kV)",              vars:7,  status:"LIVE",    sources:"PSE · ENTSO-E · OSM" },
    { id:"I",   name:"Output Scores + Alert Flags",                 vars:7,  status:"LIVE",    sources:"Fleet Markov Chain · IEEE/CIGRÉ analysis" }
  ],

  /* ── validation framework ── */
  VALIDATION_CHECKS: [
    { check:"East–West flood gradient",                             criterion:"Central Poland (Vistula basin) R systematically higher than western regions",                           status:"expected" },
    { check:"Flood–I5 coherence (KZGW)",                            criterion:"Substations in high-flood zones show elevated I5 scores — 2010/2013/2024 events",                      status:"expected" },
    { check:"Mining subsidence–I7 agreement (WUG)",                 criterion:"Śląskie substations in mining zones show elevated I7 and I5 scores",                                  status:"expected" },
    { check:"Coal transition–I9 signal (KOBiZE)",                   criterion:"Substations feeding coal plants show elevated I9 scores; decoupling post-2030",                       status:"expected" },
    { check:"RE stress–DER agreement (North)",                      criterion:"Pomeranian/Greater Poland regions with high wind penetration show elevated S2 scores",                 status:"expected" },
    { check:"Energy price–E1 correlation",                          criterion:"Electricity price volatility tracks coal market in coal-dependent województwa",                        status:"expected" },
    { check:"SAIDI–CAIDI cross-consistency",                        criterion:"High SAIDI regions also show high CAIDI (slow restoration in remote województwa)",                   status:"expected" },
    { check:"KZGW flood spatial coherence",                         criterion:"KZGW ISOK hazard map aligns with I5 scores — elevated in Vistula/Oder basins",                      status:"expected" },
    { check:"RE stress vs EV load correlation",                     criterion:"S2 (RE stress) and S3 (EV penetration) positively correlated in urban województwos",               status:"nascent" },
    { check:"Monte Carlo convergence (CV < 2%)",                    criterion:"Coefficient of variation < 2% at 2,000 iterations for all substations",                             status:"expected" },
    { check:"Weight budget unity",                                  criterion:"Component weights sum to 1.0000; all intra-weights sum to 1.0000 per component",                    status:"expected" },
    { check:"Modifier range adherence",                             criterion:"All modifiers stay within declared [min, max] bounds across the fleet",                              status:"expected" },
    { check:"Band boundary contiguity",                             criterion:"No gap or overlap between Low/Medium/High/Critical thresholds",                                      status:"expected" },
    { check:"R3 consequence signal + coal dependency",              criterion:"High-population, energy-poor, coal-dependent powіats consistently score higher R3 multiplier",       status:"expected" },
    { check:"R6b flood/subsidence sensitivity (CRITICAL)",          criterion:"Flood zone proximity drives R6b up to 1.50 ceiling; mining overlay independent of other modifiers", status:"critical" },
    { check:"PSE vs DSO constraint signal",                         criterion:"PSE 400kV backbone substations score higher R4; DSO periphery lower due to topology",               status:"expected" }
  ],

  /* ── changelog v3.4 → v4.0.2 (Poland edition) ── */
  CHANGELOG: [
    { id:"PL1",  change:"Poland country launch — 1,685 substations across 16 województwa, administrative powiat level",                                type:"new" },
    { id:"PL2",  change:"Integrated PSE transmission dispatch data + URE reliability benchmarks",                                                     type:"data" },
    { id:"PL3",  change:"URE reliability register integrated — SAIDI/SAIFI standardisation for DSO networks",                                        type:"data" },
    { id:"PL4",  change:"KZGW flood hazard map integrated (ISOK programme) — critical for Vistula/Oder basin exposure",                            type:"data" },
    { id:"PL5",  change:"WUG mining subsidence mapping integrated — Upper Silesia Coal Basin ground deformation data",                               type:"data" },
    { id:"PL6",  change:"KOBiZE coal transition risk indicator — stranding risk for coal-fed substations",                                          type:"data" },
    { id:"PL7",  change:"IMGW + CIREN climate integration — flood indices and thermal stress for flood-prone regions",                              type:"data" },
    { id:"PL8",  change:"GUS Census 2021 + Eurostat socio-economic data integrated — vulnerability indices per powiat",                              type:"data" },
    { id:"PL9",  change:"PSEW wind + IEO solar capacity data integrated — RE penetration for northern/central regions",                             type:"data" },
    { id:"PL10", change:"ARE coal consumption coupling integrated — E1 volatility modulation for coal-dependent województwa",                       type:"new" },
    { id:"PL11", change:"R6b modifier enhanced with dual KZGW flood + WUG subsidence hazard (range 1.00–1.50)",                                    type:"enhanced" },
    { id:"PL12", change:"R3 consequence enriched with Eurostat SILC energy poverty, KOBiZE coal criticality, health links",                       type:"enhanced" },
    { id:"PL13", change:"R4 graph criticality rebuilt with PSE 400kV topology + DSO network constraints — north-south flood corridor penalty",       type:"enhanced" },
    { id:"PL14", change:"I9 Coal Transition Risk — new metric from KOBiZE coal plant proximity and phase-out timelines",                           type:"new" },
    { id:"PL15", change:"R2 Adaptive IRI now includes CMIP6 SSP2-4.5 forward projections for flood risk & extreme weather corridor",                type:"enhanced" }
  ],

  /* ── fleet stats (placeholder — updated by ssi-data.json at runtime) ── */
  FREQ_DISTRIBUTION: {
      "Real-time": { count: 3, sources: ['PSE Dispatch', 'GIOŚ Air Quality', 'IMGW Warnings'] },
      "Hourly":    { count: 2, sources: ['PSE Generation', 'ENTSO-E Flows'] },
      "Daily":     { count: 3, sources: ['IMGW Weather', 'Copernicus ERA5', 'PSE Load'] },
      "Monthly":   { count: 5, sources: ['ARE Energy Balance', 'NBP Economics', 'GUS Updates', 'PSEW Wind', 'KOBiZE Emissions'] },
      "Quarterly": { count: 4, sources: ['URE Reports', 'DSO Performance', 'CEN Forecasts', 'Eurostat SILC'] },
      "Annual":    { count: 8, sources: ['GUS Census Updates', 'UDT Inspections', 'KZGW Flood Maps', 'PIG Geology', 'WUG Mining', 'DSO Annual Reports', 'CONAF Forest', 'World Bank'] },
      "Static":    { count: 3, sources: ['OSM Power', 'GUGiK Geodesy', 'SolarGIS'] },
      "5-Year":    { count: 2, sources: ['GUS Census 2021', 'KZGW ISOK Cycle'] }
    },
  stats: {
      variables: 95,
      metrics: 20,
      components: 6,
      modifiers: 7,
      sources: 30,
      substations: 1685,
      powerLines: 4200,
      mcIterations: 2000,
      wojewodztwa: 16,
      powiats: 380
    }
};


/* ═══════════════════════════════════════════════
   Legacy flat format — backward compatibility
   Used by overview.html, regional.html, map.html
   ═══════════════════════════════════════════════ */

window.SSI_METADATA = {
  country: "Poland",
  country_code: "PL",
  flag: "🇵🇱",
  currency: "zł",
  version: "4.0.2",
  edition: "001",
  edition_month: "March 2026",
  substations_label: "substations",
  region_label: "Województwo",
  region_label_plural: "Województwa",
  admin_division_label: "Powiat",
  admin_division_label_short: "Powiat",
  total_substations: 1685,
  total_powiats: 380,
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
  monte_carlo: { iterations:2000, correlation_matrix:"20×20", seed:42, confidence_interval:0.95 },
  regions: [
    "Dolnośląskie",
    "Kujawsko-Pomorskie",
    "Lubelskie",
    "Lubuskie",
    "Łódzkie",
    "Małopolskie",
    "Mazowieckie",
    "Opolskie",
    "Podkarpackie",
    "Podlaskie",
    "Pomorskie",
    "Śląskie",
    "Świętokrzyskie",
    "Warmińsko-Mazurskie",
    "Wielkopolskie",
    "Zachodniopomorskie"
  ]
};
