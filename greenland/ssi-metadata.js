/*  SSI v4.0.2 — Metadata Registry · Greenland (Kalaallit Nunaat)
    Loaded by every page in /greenland/.
    ──────────────────────────────────────────────
    Exports:  window.SSIMetadata   (structured, matches Denmark format)
              window.SSI_METADATA  (legacy flat, backward-compat)

    Note: Greenland is an autonomous territory within the Kingdom of Denmark
    (Rigsfællesskabet). Not a separate OECD member — covered under Denmark's
    OECD umbrella. Grid is fully independent from Denmark's (no interconnector);
    scored as a separate entity for integrity. Pituffik Space Base (US Space
    Force) is excluded — independent grid, non-public asset data. See
    methodology §7.                                                         */

window.SSIMetadata = (function () {
  'use strict';
  return {

  /* ── Country metadata ── */
  country: "Greenland",
  country_kl: "Kalaallit Nunaat",
  country_da: "Grønland",
  code: "GL",
  prefix: "GL_",
  parent_realm: "Denmark",
  oecd_member: false,
  oecd_via: "DK",
  bundled_archive_with: "DK",
  pituffik_excluded: true,
  first_refresh: "2026-07",
  tso: "Nukissiorfiit (state-owned single operator — electricity, district heating, water)",
  regulator: "Departementet for Boliger og Infrastruktur (Naalakkersuisut — Ministry of Housing and Infrastructure)",
  statistics: "Grønlands Statistik (Statistics Greenland)",
  weather: "Asiaq — Greenland Survey (primary) · DMI Greenland (polar forecasts)",
  geology: "GEUS — Geological Survey of Denmark and Greenland (shared institution)",
  nuclear: "NONE (no nuclear power; ~70% hydro + diesel remainder)",
  admin: { level1: "Kommune", level2: "Settlement" },
  currency: { code: "DKK", symbol: "kr." },
  kommuner: ["Avannaata", "Qeqertalik", "Qeqqata", "Sermersooq", "Kujalleq"],
  languages: ["kl", "da", "en"],

  /* ── 25 verified data sources — Greenlandic + shared Danish institutions ── */
  DATA_SOURCES: [
    { id:"NUK",         name:"Nukissiorfiit — Greenland Energy Supply (TSO/DSO/Utility)", url:"nukissiorfiit.gl", freq:"Annual",    res:"Substation",       vars:14, category:"Grid",         feeds:"C1–C4, I2, S1, transmission + distribution topology across ~70 islanded systems, hydro dispatch, diesel generation backup" },
    { id:"NAAL_DBI",    name:"Naalakkersuisut — Departementet for Boliger og Infrastruktur", url:"naalakkersuisut.gl", freq:"Quarterly", res:"Regional",    vars:8,  category:"Grid",         feeds:"C1–C4, V1–V2, regulatory oversight, infrastructure policy, reliability benchmarks (no formal SAIDI reporting)" },
    { id:"NAAL_GOV",    name:"Naalakkersuisut — Government of Greenland (Self-Government Act 2009)", url:"naalakkersuisut.gl", freq:"Annual", res:"National", vars:4, category:"Socio-Econ", feeds:"Energy policy, budget allocations, infrastructure priorities, public service obligations" },
    { id:"STATGL",      name:"Grønlands Statistik — Statistics Greenland",                 url:"stat.gl",          freq:"Quarterly", res:"Kommune",           vars:10, category:"Socio-Econ",   feeds:"C1–C4, demographics, income distribution, population served (~56,500), housing, regional economic data" },
    { id:"ASIAQ",       name:"Asiaq — Greenland Survey (Meteorology, Hydrology, Permafrost)", url:"asiaq-greenlandsurvey.gl", freq:"Daily", res:"Station",   vars:10, category:"Climate",      feeds:"I3 (Arctic storm + permafrost + ice accretion stress), weather, hydrology, cryosphere, polar-low warnings" },
    { id:"GEUS",        name:"GEUS — Geological Survey of Denmark and Greenland",          url:"geus.dk",          freq:"Annual",    res:"Grid 0.1°",         vars:8,  category:"Hazard",       feeds:"I5 (permafrost degradation + coastal erosion + glacial runoff), bedrock mapping, thaw-sensitive ground classification" },
    { id:"DMI_GL",      name:"DMI — Danish Meteorological Institute (Greenland Branch)",   url:"dmi.dk",           freq:"Daily",     res:"Station",           vars:6,  category:"Climate",      feeds:"I3/I5 polar-low storm forecasts, sea-ice charts, climate normals, wind and precipitation for coastal stations" },
    { id:"OSM",         name:"OpenStreetMap — Power Infrastructure (augmented by Nukissiorfiit grid map)", url:"overpass-api.de", freq:"Monthly", res:"Node", vars:6, category:"Infrastructure", feeds:"I4 (graph degree within each islanded system), ~250 substations mapped across 5 Kommuner, no inter-settlement HV links" },
    { id:"COPERNICUS",  name:"Copernicus Arctic + ESA CryoSat",                            url:"cds.climate.copernicus.eu", freq:"Monthly", res:"Grid 0.25°", vars:6, category:"Climate",     feeds:"Arctic storm risk, sea-ice coverage, glacier mass balance, permafrost degradation trajectory (CMIP6 Arctic amplification)" },
    { id:"ASIAQ_PERMA", name:"Asiaq — Permafrost Monitoring Network",                      url:"asiaq-greenlandsurvey.gl/permafrost", freq:"Quarterly", res:"Borehole", vars:5, category:"Hazard", feeds:"I5 permafrost temperature, active-layer thickness, thaw subsidence for substation foundations" },
    { id:"NUK_HYDRO",   name:"Nukissiorfiit — Hydropower Plants (Buksefjord, Tasersiaq, Qorlortorsuaq, Sisimiut, Paakitsoq)", url:"nukissiorfiit.gl/hydropower", freq:"Monthly", res:"Plant", vars:5, category:"Grid", feeds:"S1 (RE capacity ~70%), reservoir levels, glacial-runoff inflow, hydro dispatch for major settlements" },
    { id:"NUK_DIESEL",  name:"Nukissiorfiit — Diesel Generation (smaller settlements)",    url:"nukissiorfiit.gl",  freq:"Monthly",  res:"Settlement",        vars:4,  category:"Grid",         feeds:"S1 variant, backup generation for ~70 islanded settlements without hydro access, fuel logistics" },
    { id:"GL_CONNECT",  name:"Greenland Connect — Submarine Cable & Digital Infrastructure", url:"tele.gl",         freq:"Quarterly", res:"National",          vars:3,  category:"Energy",       feeds:"R7 digital readiness, SCADA communications backbone, settlement connectivity via satellite + submarine cable" },
    { id:"ARCTIC_COUNCIL", name:"Arctic Council — Arctic Resilience Reports",              url:"arctic-council.org", freq:"Annual",  res:"Pan-Arctic",        vars:3,  category:"Climate",      feeds:"International Arctic benchmarks, permafrost trajectory comparisons, circumpolar grid resilience context" },
    { id:"EUROSTAT",    name:"Eurostat — EU + OECD Comparators",                           url:"ec.europa.eu/eurostat", freq:"Annual", res:"National",       vars:3,  category:"Socio-Econ",   feeds:"E2 population served, OECD socio-economic indicators via Denmark umbrella" },
    { id:"NAAL_ENV",    name:"Naalakkersuisut — Miljø og Natur (Environment)",             url:"naalakkersuisut.gl/miljoe", freq:"Annual", res:"Kommune",    vars:4,  category:"Environment",  feeds:"I6 (environmental exposure + Arctic pollution + ice-sheet proximity), coastal protection, ecosystem services" },
    { id:"ICEMAP",      name:"DMI — Sea Ice Charts + Iceberg Monitoring",                  url:"ocean.dmi.dk",      freq:"Daily",    res:"Coastal",           vars:4,  category:"Hazard",       feeds:"I5 iceberg exposure for coastal substations, fjord navigation constraints for fuel/equipment logistics" },
    { id:"NBANK",       name:"Nationalbanken — Danish National Bank (via Denmark umbrella)", url:"nationalbanken.dk", freq:"Annual", res:"National",         vars:3,  category:"Economic",     feeds:"E1–E3 economic cycles, Greenland fiscal transfers via Rigsfællesskabet, DKK peg" },
    { id:"WORLDBANK",   name:"World Bank / OECD",                                          url:"worldbank.org",     freq:"Annual",    res:"National",          vars:3,  category:"Socio-Econ",   feeds:"International benchmarks via Denmark OECD membership, Arctic development indicators" },
    { id:"DTU_ARCTIC",  name:"DTU Arctic Research Centre",                                 url:"arctic.dtu.dk",     freq:"Annual",    res:"Regional",          vars:3,  category:"Environment",  feeds:"Arctic infrastructure research, micro-grid stability in cold climates, cryosphere dynamics" },
    { id:"ICESHEET",    name:"PROMICE — Programme for Monitoring of the Greenland Ice Sheet", url:"promice.dk",     freq:"Monthly",   res:"Ice-sheet margin",  vars:3,  category:"Climate",      feeds:"I5 glacial-runoff forecasts for hydropower plants, ice-sheet mass balance trajectory" },
    { id:"SOLARGIS",    name:"SolarGIS — Global Solar Atlas (polar adaptation)",           url:"globalsolaratlas.info", freq:"Static", res:"Global",           vars:2,  category:"Transition",   feeds:"T1 solar irradiance (limited polar usefulness; southern Kujalleq only)" },
    { id:"GEOD",        name:"Asiaq Geodata + Nuuk Municipal GIS",                         url:"asiaq.gl/geodata",  freq:"Annual",    res:"Regional",          vars:3,  category:"Infrastructure", feeds:"Geospatial topology, settlement boundaries, unpaved road access for maintenance logistics" },
    { id:"NAAL_TRANSP", name:"Naalakkersuisut — Transport + Infrastructure",               url:"naalakkersuisut.gl/transport", freq:"Quarterly", res:"Regional", vars:3, category:"Transport",    feeds:"S3 EV penetration (nascent; Nuuk pilot only), access infrastructure between settlements (air + sea only, no roads)" },
    { id:"DMI_HIST",    name:"DMI — Historical Archive (Greenland)",                       url:"dmi.dk/greenland",  freq:"Monthly",   res:"Station",           vars:3,  category:"Climate",      feeds:"Historical polar-low severity, coastal storm records, extreme-cold events for grid design benchmarking" }
  ],

  /* ── 6 components · 20 metrics ── */
  COMPONENTS: [
    {
      id:"C", name:"Continuity", weight:0.30, color:"#941914",
      desc:"Measures reliability and outage exposure — how often and how long power interruptions occur across ~70 islanded micro-grids. Restoration logistics are dominated by Arctic weather, sea-ice windows, and air-only access to most settlements.",
      metrics:[
        { id:"C1", name:"Outage Duration (SAIDI-equivalent)",      intra:0.35, global:0.105, norm:"A (P5/P95)", source:"Nukissiorfiit / Naalakkersuisut",        desc:"Annual interruption duration per customer (derived from settlement-outage logs; no formal SAIDI reporting)", inverted:false, adaptive:false, isNew:false },
        { id:"C2", name:"Outage Frequency (SAIFI-equivalent)",     intra:0.30, global:0.090, norm:"A (P5/P95)", source:"Nukissiorfiit",                           desc:"Number of sustained interruptions per customer per year",                                                 inverted:false, adaptive:false, isNew:false },
        { id:"C3", name:"Restoration Time (Arctic logistics penalty)", intra:0.20, global:0.060, norm:"A (P5/P95)", source:"Nukissiorfiit",                       desc:"Average interruption duration; penalised by sea-ice window and air-access constraints for equipment dispatch", inverted:false, adaptive:true,  isNew:false },
        { id:"C4", name:"Momentary Interruptions (diesel-switching)", intra:0.15, global:0.045, norm:"A (P5/P95)", source:"Nukissiorfiit",                        desc:"Momentary interruption frequency — dominated by hydro↔diesel backup switching in micro-grids",           inverted:false, adaptive:false, isNew:false }
      ]
    },
    {
      id:"V", name:"Voltage Quality", weight:0.10, color:"#aa4234",
      desc:"Voltage stability, power factor, and harmonic distortion at the distribution level. Small isolated grids have inherently higher variability than continental interconnected systems.",
      metrics:[
        { id:"V1", name:"Voltage Deviation (ΔV)",     intra:0.40, global:0.040, norm:"A (P5/P95)", source:"Nukissiorfiit",       desc:"Percentage deviation from nominal voltage (elevated baseline on isolated micro-grids)",  inverted:false, adaptive:false, isNew:false },
        { id:"V2", name:"THD (Harmonic Distortion)", intra:0.30, global:0.030, norm:"A (P5/P95)", source:"Nukissiorfiit",       desc:"Total harmonic distortion — influenced by diesel-dominated settlements",                inverted:false, adaptive:false, isNew:false },
        { id:"V3", name:"Power Factor",              intra:0.30, global:0.030, norm:"B (inverse)", source:"Nukissiorfiit",       desc:"Ratio of real to apparent power — higher is better",                                     inverted:true,  adaptive:false, isNew:false }
      ]
    },
    {
      id:"I", name:"Infrastructure", weight:0.25, color:"#5d8563",
      desc:"Physical asset condition, age, capacity, and Arctic-specific hazards: permafrost degradation, ice accretion, polar-low surge, glacial runoff, coastal erosion. Foundations on thaw-sensitive ground are a dominant concern.",
      metrics:[
        { id:"I1", name:"Asset Age Index",                         intra:0.12, global:0.030, norm:"A (P5/P95)", source:"Nukissiorfiit / Grønlands Statistik",    desc:"Fleet-normalised average asset age (older fleet on average vs Denmark)",                                                                                    inverted:false, adaptive:false, isNew:false },
        { id:"I2", name:"Capacity Utilisation",                    intra:0.12, global:0.030, norm:"A (P5/P95)", source:"Nukissiorfiit",                           desc:"Percentage of rated capacity in use (hydro plants sized for peak winter demand)",                                                                             inverted:false, adaptive:false, isNew:false },
        { id:"I3", name:"Climate IRI (Arctic: permafrost + ice + polar-low)", intra:0.15, global:0.0375, norm:"A (P5/P95)", source:"Asiaq / DMI Greenland / Copernicus Arctic", desc:"Infrastructure Risk Index combining permafrost degradation, ice accretion on overhead lines, polar-low storm surge, and glacial-runoff regime shift",   inverted:false, adaptive:true,  isNew:false },
        { id:"I4", name:"Graph Degree (within-settlement topology)", intra:0.10, global:0.025, norm:"B (inverse)", source:"OSM / Nukissiorfiit grid map",          desc:"Connections within each islanded system only — no synthetic cross-settlement edges. Low N per system drives limited redundancy",                        inverted:true,  adaptive:false, isNew:false },
        { id:"I5", name:"Permafrost + Coastal + Glacial Runoff Hazard (CRITICAL)", intra:0.20, global:0.050, norm:"A (P5/P95)", source:"GEUS / Asiaq / PROMICE / DMI", desc:"Combined permafrost foundation risk + coastal erosion + glacial-runoff regime shift affecting hydro supply + iceberg exposure for coastal substations", inverted:false, adaptive:false, isNew:false },
        { id:"I6", name:"Corrosion Class (Arctic coastal)",        intra:0.10, global:0.025, norm:"D (categorical)", source:"ISO9223 / DMI",                       desc:"Environmental corrosion class: coastal C4, fjord C3, interior C2. Salt spray + freeze-thaw compound damage",                                               inverted:false, adaptive:false, isNew:false, categorical:true },
        { id:"I7", name:"Ice Accretion Zone",                      intra:0.10, global:0.025, norm:"D (categorical)", source:"Asiaq / DMI",                         desc:"Ice-loading hazard for overhead transmission lines — coastal and fjord corridors rank highest",                                                            inverted:false, adaptive:true,  isNew:false, categorical:true },
        { id:"I8", name:"N-1 Compliance (where applicable)",       intra:0.05, global:0.0125, norm:"C (binary)",    source:"Nukissiorfiit",                        desc:"Whether substation meets N-1 redundancy standard — rare on isolated micro-grids; typically only Nuuk/Buksefjord system",                                   inverted:true,  adaptive:false, isNew:false },
        { id:"I9", name:"Hydro Single-Point Dependency",           intra:0.06, global:0.015,  norm:"D (categorical)", source:"Nukissiorfiit / PROMICE",             desc:"Substations dependent on a single hydro plant (no alternative feed) — critical in Nuuk, Sisimiut, Ilulissat, Qaqortoq",                                   inverted:false, adaptive:false, isNew:true,   categorical:true }
      ]
    },
    {
      id:"E", name:"Economic", weight:0.10, color:"#3b9eff",
      desc:"Links grid risk to regional economic exposure — fiscal-transfer dependency via Rigsfællesskabet, fisheries concentration, and Nuuk-centric economic gravity.",
      metrics:[
        { id:"E1", name:"Energy Price Index (subsidised tariff)", intra:0.40, global:0.040, norm:"A (P5/P95)", source:"Nukissiorfiit / Naalakkersuisut",        desc:"Cross-subsidised uniform tariff for electricity across all settlements; true cost varies ~4× between hydro and diesel-served communities", inverted:false, adaptive:false, isNew:false },
        { id:"E2", name:"Population Served + Settlement Gravity",  intra:0.30, global:0.030, norm:"A (P5/P95)", source:"Grønlands Statistik / Eurostat",          desc:"Kommune-level population served; Sermersooq (Nuuk) dominates with ~40% of national population",                                                inverted:false, adaptive:false, isNew:false },
        { id:"E3", name:"Economic Concentration (fisheries + mining)", intra:0.30, global:0.030, norm:"A (P5/P95)", source:"Grønlands Statistik / Nationalbanken", desc:"Fisheries and emerging rare-earth mining economic activity concentration; fiscal-transfer dependency captured separately",                     inverted:false, adaptive:false, isNew:false }
      ]
    },
    {
      id:"S", name:"Saturation", weight:0.20, color:"#b88f3e",
      desc:"Quantifies hydro/diesel mix, renewable penetration (high — ~70% hydro), and grid flexibility stress. Unlike continental peers, saturation stress here is dominated by glacial inflow variability rather than DER.",
      metrics:[
        { id:"S1", name:"Renewable Energy Capacity Ratio (~70% hydro)", intra:0.35, global:0.070, norm:"A (P5/P95)", source:"Nukissiorfiit / Naalakkersuisut",    desc:"Hydro capacity relative to substation rating; hydro-served settlements dominate, diesel-only settlements score near-zero",             inverted:false, adaptive:false, isNew:false },
        { id:"S2", name:"RE Stress Index (Glacial-Runoff Variability)", intra:0.35, global:0.070, norm:"A (P5/P95)", source:"Nukissiorfiit / PROMICE / Asiaq",    desc:"Glacial-runoff and snowmelt variability stress on hydropower — directly linked to ice-sheet mass balance and seasonal melt timing",   inverted:false, adaptive:true,  isNew:false },
        { id:"S3", name:"EV Penetration Rate (nascent)",              intra:0.30, global:0.060, norm:"A (P5/P95)", source:"Naalakkersuisut Transport",           desc:"EV registrations — nascent, Nuuk pilot only; constrained by limited road network between settlements",                                  inverted:false, adaptive:false, isNew:true }
      ]
    },
    {
      id:"T", name:"Energy Transition", weight:0.05, color:"#0e7490", isNew:true,
      desc:"Measures clean energy transition pace. Greenland starts from a ~70% renewable baseline (hydro) — transition focus is on displacing remaining diesel in smaller settlements via small-hydro, wind, or hybrid systems.",
      metrics:[
        { id:"T1", name:"Renewable Energy Share (%)",        intra:0.50, global:0.025, norm:"B (inverse)", source:"Nukissiorfiit / Naalakkersuisut",    desc:"Share of generation from renewables — already high in major settlements, low in remote diesel communities (inverted metric)",                  inverted:true,  adaptive:false, isNew:false },
        { id:"T2", name:"Transition Readiness (diesel-displacement potential)", intra:0.50, global:0.025, norm:"A (P5/P95)", source:"Nukissiorfiit / DTU Arctic", desc:"Readiness to displace diesel: micro-grid flexibility, storage potential, feasibility of small-hydro or hybrid wind/solar additions in remote settlements", inverted:true,  adaptive:false, isNew:true }
      ]
    }
  ],

  /* ── 7 modifiers — Arctic-calibrated ── */
  MODIFIERS: [
    { id:"R2",  name:"Adaptive Climate IRI + Arctic Amplification Trajectory",          range:"Weight redistribution", type:"Weight modifier", desc:"CMIP6 SSP2-4.5 Arctic projections adjust IRI metrics for permafrost degradation, sea-ice retreat, polar-low storm frequency, glacial runoff regime shift. Arctic amplification means warming at 2–4× global mean — large weight shifts expected.", formula:"IRI_forward(m,s) = IRI_current(m,s) × (1 + 0.25 × clip(Δ_arctic, −0.50, +1.50))", sources:["Asiaq","DMI Greenland","Copernicus Arctic","PROMICE","GEUS"], isEnhanced:true },
    { id:"R3",  name:"Consequence + Settlement Isolation + Small-N Relaxation",         range:"[0.70, 1.35]",           type:"Multiplicative",  desc:"Amplifies risk for isolated settlements with no road access and limited alternative supply. Tier-balance guardrail relaxed to 2–50% per tier (vs standard 5–45%) given small fleet size N~250. Sermersooq concentration and Pituffik exclusion documented.", formula:"C_mult = sigmoid(pop_weight × isolation_weight × V_socio × access_factor)", sources:["Grønlands Statistik","Naalakkersuisut","Eurostat"], isEnhanced:true },
    { id:"R4",  name:"Graph Criticality (within-settlement only)",                      range:"[0.80, 1.40]",           type:"Multiplicative",  desc:"Penalises topological bottlenecks within each of ~70 islanded systems. No synthetic cross-settlement edges — R4 is computed per-island only. Hydro-plant feeders and their MV distribution backbones score highest.", formula:"F_topo = f(degree, BC_percentile, is_bridge) within island", sources:["OSM","Nukissiorfiit"], isEnhanced:true },
    { id:"R6a", name:"Restoration Speed (Arctic Logistics + Sea-Ice Window)",           range:"[0.55, 0.90]",           type:"Multiplicative",  desc:"Arctic-specific calibration: restoration depends on sea-ice windows (sea access), air-only logistics, and extreme-cold crew operations. α range elevated vs OECD baseline (0.55–0.90 vs 0.90–1.10) reflecting genuinely longer Arctic restoration times.", formula:"R6a = alpha × sigmoid_bounded(restoration_time_local / fleet_median)", sources:["Nukissiorfiit","Asiaq","DMI Greenland"], isEnhanced:true },
    { id:"R6b", name:"Seismic Floor (intraplate stable craton)",                        range:"[0.05, 0.15]",           type:"Multiplicative",  desc:"Near-zero seismic contribution — Greenland sits on North American Plate interior, intraplate stable craton. R6b effectively a floor modifier retained for schema consistency across countries.", formula:"R6b = alpha_floor (structurally ≈ 0.10)", sources:["GEUS","USGS"], isEnhanced:false },
    { id:"R7",  name:"Digital Readiness (Satellite + Submarine Cable Dependency)",      range:"[0.99, 1.08]",           type:"Multiplicative",  desc:"SCADA communications depend on Greenland Connect submarine cable + satellite backup. Cable interruptions have occurred (2023 fishing-trawl incidents). Digital resilience penalty slightly higher than continental peers due to single-cable dependency on most coastal routes.", formula:"Cyber = f(SCADA_maturity, cable_redundancy, satellite_backup_pct)", sources:["Greenland Connect","Nukissiorfiit"], isEnhanced:true }
  ],

  /* ── processing pipeline ── */
  PIPELINE: [
    { step:1, name:"Ingest", desc:"95 variables from 25 verified Greenlandic + shared Danish public sources — Nukissiorfiit, Naalakkersuisut, Grønlands Statistik, Asiaq, GEUS, DMI Greenland, PROMICE, Copernicus Arctic, and OSM. Zero proprietary SCADA dependencies. Maximum ingestion frequency: daily (Asiaq + DMI).", icon:"📥" },
    { step:2, name:"Normalise", desc:"Four normalisation methods: Method A (fleet percentile P5/P95), Method B (inverse percentile), Method C (binary compliance), Method D (categorical). Small-N guardrail relaxes R3 tier-balance to 2–50% per tier given N~250.", icon:"📐" },
    { step:3, name:"Weight", desc:"6-level hierarchical weighting across 6 components and 20 metrics. Infrastructure raised to 0.25 with elevated I5 weight (permafrost + coastal + glacial runoff). Continuity at 0.30, Saturation at 0.20.", icon:"⚖️" },
    { step:4, name:"Compose R_base", desc:"Weighted sum of 6 normalised component scores produces the base resilience score.", icon:"🧮" },
    { step:5, name:"Modify", desc:"Seven multiplicative modifiers adjust R_base for Arctic context: R2 (adaptive IRI + Arctic amplification), R3 (consequence + isolation + small-N), R4 (within-island criticality), R6a (restoration under Arctic logistics, elevated α), R6b (seismic floor, near-zero), R7 (digital readiness + cable dependency).", icon:"🔧" },
    { step:6, name:"Monte Carlo", desc:"10,000 iterations per substation using a 20×20 Gaussian copula correlation matrix. Captures measurement, spatial, staleness, and model uncertainty.", icon:"🎲" },
    { step:7, name:"Classify", desc:"Four bands: Low (0.00–0.25), Medium (0.25–0.50), High (0.50–0.75), Critical (0.75–1.00). Small-N guardrail relaxes balance check. Pituffik Space Base excluded — see methodology §7.", icon:"🏷️" }
  ],

  /* ── classification bands ── */
  CLASSIFICATION: [
    { name:"Low",      range:"0.00 – 0.25", meaning:"Good resilience — stable micro-grid, hydro-served",           expected:"~20–25%", color:"#5d8563" },
    { name:"Medium",   range:"0.25 – 0.50", meaning:"Moderate risk — some vulnerabilities present",                 expected:"~35–40%", color:"#b88f3e" },
    { name:"High",     range:"0.50 – 0.75", meaning:"Elevated risk — Arctic hazard + restoration exposure",          expected:"~25–30%", color:"#aa4234" },
    { name:"Critical", range:"0.75 – 1.00", meaning:"Severe vulnerability — diesel-dependent isolated settlements",  expected:"~10–15%", color:"#941914" }
  ],

  /* ── master equation ── */
  MASTER_EQUATION: "R_final = soft_clip_upper( R_base × F_topo × C_mult × R6a_arctic_restoration × R6b_seismic_floor × Cyber_factor )",

  /* ── normalisation methods ── */
  NORM_METHODS: [
    { id:"A", name:"Fleet Percentile (robust)",  formula:"N(x) = soft_clip((x − P₅) / (P₉₅ − P₅))",       applies:"C1, C2, C3, C4, V1, V2, I1, I2, I3, I5, E1, E2, E3, S1, S2, S3" },
    { id:"B", name:"Fleet Percentile (inverse)", formula:"N(x) = 1 − soft_clip((x − P₅) / (P₉₅ − P₅))",   applies:"V3, I4, T1, T2" },
    { id:"C", name:"Binary (bounded)",           formula:"N(x) = 0 if compliant, 1 if non-compliant",      applies:"I8 (N-1 compliance)" },
    { id:"D", name:"Categorical Mapping",        formula:"N(x) = lookup_table(class → [0, 1])",            applies:"I6 (Arctic coastal corrosion), I7 (ice accretion), I9 (hydro single-point)" }
  ],

  /* ── 11 data layers · 95 variables ── */
  DATA_LAYERS: [
    { id:"A",   name:"SSI v4.0.2 Resilience (Greenland)",            vars:20, status:"LIVE",     sources:"Nukissiorfiit · Naalakkersuisut · Grønlands Statistik · Asiaq · GEUS · DMI Greenland" },
    { id:"B.1", name:"Grid Telemetry: Open",                         vars:3,  status:"LIVE",     sources:"Asiaq · DMI Greenland · Nukissiorfiit" },
    { id:"B.2", name:"Grid Telemetry: Proxy",                        vars:4,  status:"LIVE",     sources:"IEEE C57.91 · Nukissiorfiit · Naalakkersuisut" },
    { id:"B.3", name:"Grid Telemetry: Fuzzy",                        vars:12, status:"FUZZY",    sources:"IEEE/CIGRÉ standards · GEUS · PROMICE" },
    { id:"C",   name:"Socio-Economic + Arctic Demographics",          vars:10, status:"LIVE",     sources:"Grønlands Statistik · Eurostat · Naalakkersuisut · Nationalbanken" },
    { id:"D",   name:"Environmental Hazards (Permafrost + Ice + Polar-Low)", vars:8, status:"LIVE", sources:"GEUS · Asiaq · PROMICE · DMI Greenland · Copernicus Arctic" },
    { id:"E",   name:"Greenlandic Open Data + Energy Policy",         vars:9,  status:"LIVE",     sources:"Nukissiorfiit · Naalakkersuisut · Asiaq Geodata" },
    { id:"F",   name:"Network Transitions + Hydro Baseload",          vars:12, status:"BAYESIAN", sources:"Nukissiorfiit history + IEEE/CIGRÉ priors" },
    { id:"G",   name:"Modifier Inputs (Arctic-Weighted)",             vars:4,  status:"LIVE",     sources:"Nukissiorfiit · Asiaq · OSM" },
    { id:"H",   name:"Network & Topology (Within-Island)",            vars:7,  status:"LIVE",     sources:"Nukissiorfiit grid map · OSM" },
    { id:"I",   name:"Output Scores + Alert Flags",                   vars:7,  status:"LIVE",     sources:"Fleet Markov Chain · Small-N adapted thresholds" }
  ],

  /* ── frequency distribution (25 sources total) ── */
  FREQ_DISTRIBUTION: {
      "Daily":     { count: 3, sources: ['Asiaq Weather & Hydrology', 'DMI Greenland', 'DMI Sea Ice Charts'] },
      "Monthly":   { count: 4, sources: ['OpenStreetMap Power', 'Copernicus Arctic', 'Nukissiorfiit Hydro', 'PROMICE Ice-Sheet', 'DMI Historical'] },
      "Quarterly": { count: 5, sources: ['Naalakkersuisut DBI', 'Grønlands Statistik', 'Asiaq Permafrost', 'Greenland Connect', 'Naalakkersuisut Transport'] },
      "Annual":    { count: 11, sources: ['Nukissiorfiit Annual Report', 'Naalakkersuisut Government', 'GEUS Geology', 'Naalakkersuisut Environment', 'Nationalbanken', 'World Bank/OECD', 'DTU Arctic Research', 'Asiaq Geodata', 'Eurostat', 'Arctic Council', 'Nukissiorfiit Diesel'] },
      "Static":    { count: 1, sources: ['SolarGIS (polar, limited)'] }
    },

  stats: {
      variables: 95,
      metrics: 20,
      components: 6,
      modifiers: 7,
      sources: 25,
      substations: 250,              /* PLACEHOLDER — update after first score-country.py --country GL run */
      substations_hv: 15,
      substations_mv: 235,
      powerLines: 850,               /* PLACEHOLDER — micro-grid topology */
      mcIterations: 10000,
      region: 5,
      regions: 5,
      n_islanded_systems: 70,        /* architectural constant — no cross-settlement HV */
      pituffik_excluded: true,       /* see methodology §7 */
      fleet_note: "Small-N fleet — R3 tier-balance guardrail relaxed to 2–50% per tier (standard policy: 5–45%). Document the exception as 'small_N_relaxation'."
    },

  /* ── R6 calibration notes ── */
  R6_calibration: {
      R6a_climate: {
        alpha_range: [0.55, 0.90],
        drivers: [
          "Permafrost degradation (foundation risk for substations on thaw-sensitive ground)",
          "Ice accretion on overhead lines (coastal and fjord corridors)",
          "Polar-low storm surge for coastal stations",
          "Glacial-runoff regime shift affecting Nuuk/Sisimiut/Ilulissat/Qaqortoq hydropower supply",
          "Sea-ice window constraints on restoration logistics"
        ],
        dominant_kommune: "Avannaata",
        note: "Elevated vs OECD baseline — Arctic-specific hazards layered on standard R6a factors"
      },
      R6b_seismic: {
        alpha_range: [0.05, 0.15],
        drivers: ["Intraplate stable craton — Greenland is on the North American Plate interior"],
        note: "Near-zero seismic contribution; R6b effectively a floor modifier retained for schema consistency"
      }
    },

  /* ── SAIDI comparators ── */
  saidi: {
      country_minutes: null,
      comparator_label: "Selected Countries",
      note: "Nukissiorfiit does not publish standardised SAIDI/SAIFI; reliability tracked via settlement-outage logs. Derived SAIDI-equivalent used for C1 scoring."
    },

  /* ── methodology sections (methodology.html) ── */
  methodology_sections: [
      { id:"m1", title:"Grid Architecture — Islanded Micro-Grids", body:"Greenland operates ~70 isolated micro-grids with no HV interconnection between settlements. Five major hydro stations (Nuuk/Buksefjord 45 MW, Tasersiaq, Sisimiut, Qorlortorsuaq, Ilulissat-Paakitsoq) serve major population centres; smaller settlements run diesel generation. Road network is absent between settlements — access is by air or sea only, with sea-ice windows constraining logistics." },
      { id:"m2", title:"Scoring Scope",          body:"All publicly-documented Nukissiorfiit substations across 5 Kommuner (Avannaata, Qeqertalik, Qeqqata, Sermersooq, Kujalleq). The 6-factor SSI model (C/V/I/E/S/T) is evaluated per-substation; R4 (cascading risk) and R7 (topology) are computed within each islanded system only — no synthetic cross-settlement edges." },
      { id:"m3", title:"R6a Climate Modifier — Arctic Calibration", body:"Arctic-specific α range [0.55, 0.90] (elevated vs OECD baseline [0.90, 1.10]) layering permafrost degradation, ice accretion, polar-low surge, glacial-runoff regime shift, and sea-ice window logistics on top of standard R6a factors. Dominant driver varies by kommune: Avannaata for permafrost, coastal kommuner for ice accretion and polar-low surge." },
      { id:"m4", title:"R6b Seismic Modifier — Stable Craton Floor", body:"Near-zero for all stations — Greenland sits on intraplate stable craton (North American Plate interior). α range [0.05, 0.15]. Included for schema consistency across countries." },
      { id:"m5", title:"Data Integrity",         body:"No-synthetic-data policy applies identically to Greenland: every substation carries verified lon/lat coordinates from OSM or the Nukissiorfiit asset register. Sparse OSM coverage is supplemented by Nukissiorfiit's published grid map, with provenance flagged per-record." },
      { id:"m6", title:"Bilingual Content",      body:"Institution and place names shown in Kalaallisut (primary) with Danish and English equivalents where available. Currency denominated in DKK (pegged identically to Denmark)." },
      { id:"m7", title:"Pituffik Space Base — Exclusion", body:"Pituffik Space Base (formerly Thule Air Base), a US Space Force installation in northern Avannaata Kommune, operates its own independent electrical grid. Asset data is not publicly available and its operational scope falls outside Nukissiorfiit. Pituffik is excluded from the Greenland fleet and from all SSI scoring. This exclusion is documented in ssi-data.json metadata and surfaced as a footnote on index.html, methodology.html, and data.html." },
      { id:"m8", title:"Small-N Guardrail",      body:"With N~250 substations, Greenland is the smallest fleet in the SSI catalogue. The standard R3 tier-balance guardrail (5–45% per tier) is relaxed to 2–50% per tier for small-N countries (N<500). This preserves the rule as default while accommodating legitimately small fleets without manual overrides." }
  ],

  /* ── validation framework ── */
  VALIDATION_CHECKS: [
    { check:"North-South permafrost gradient",                        criterion:"Avannaata (north) shows higher permafrost I5 signal than Kujalleq (south); gradient consistent with Asiaq monitoring network",                                           status:"expected" },
    { check:"Polar-low–I3 coherence (DMI Greenland)",                 criterion:"Coastal substations in polar-low tracks show elevated I3; validated against DMI storm archive",                                                                            status:"expected" },
    { check:"Ice accretion–I7 agreement (Asiaq)",                     criterion:"Overhead lines in coastal/fjord corridors show elevated I7; radar-derived ice accretion validation",                                                                       status:"expected" },
    { check:"Glacial runoff–S2 coupling (PROMICE)",                   criterion:"Hydro plants downstream of glaciated catchments show elevated S2 variability; PROMICE mass-balance agreement",                                                               status:"expected" },
    { check:"Sermersooq concentration–R3 signal",                     criterion:"Nuuk (Sermersooq) with ~40% of national population consistently scores higher R3 multiplier",                                                                                 status:"expected" },
    { check:"Hydro single-point dependency–I9 signal",                 criterion:"Substations dependent on single hydro plant (Buksefjord, Tasersiaq, Qorlortorsuaq, Paakitsoq) show elevated I9",                                                               status:"expected" },
    { check:"Submarine cable dependency–R7 signal",                    criterion:"Coastal routes single-cable-served show elevated R7 vs Nuuk (multi-path)",                                                                                                    status:"nascent" },
    { check:"Small-N tier balance compliance",                         criterion:"Relaxed 2–50% tier balance per R3; documented in fleet_note",                                                                                                                  status:"expected" },
    { check:"Pituffik exclusion compliance",                           criterion:"No Pituffik assets appear in ssi-data.json; footnote surfaced on index/methodology/data",                                                                                    status:"expected" },
    { check:"Monte Carlo convergence (CV < 2%)",                       criterion:"Coefficient of variation < 2% at 10,000 iterations for all substations",                                                                                                     status:"expected" },
    { check:"Weight budget unity",                                     criterion:"Component weights sum to 1.0000; all intra-weights sum to 1.0000 per component",                                                                                             status:"expected" },
    { check:"Modifier range adherence",                                criterion:"All modifiers stay within declared [min, max] bounds; R6a elevated α range [0.55, 0.90] respected",                                                                          status:"expected" },
    { check:"R6b floor adherence",                                     criterion:"All stations score within R6b [0.05, 0.15] — intraplate stable craton signature",                                                                                            status:"expected" },
    { check:"Arctic restoration time bias",                            criterion:"C3 restoration distribution skews higher than continental peers; reflects sea-ice window + air-only logistics",                                                              status:"expected" },
    { check:"Diesel-settlement RE share signal",                       criterion:"Remote diesel-only settlements show low T1; hybrid/small-hydro upgrade opportunities visible in T2",                                                                          status:"expected" }
  ],

  /* ── changelog v3.4 → v4.0.2 (Greenland edition) ── */
  CHANGELOG: [
    { id:"GL1",  change:"Greenland country launch — ~250 substations across 5 Kommuner, ~70 islanded micro-grids",                                                      type:"new" },
    { id:"GL2",  change:"Nukissiorfiit as single TSO/DSO/Utility — state-owned, electricity + district heating + water",                                              type:"data" },
    { id:"GL3",  change:"Naalakkersuisut regulatory data integrated — no independent tariff regulator equivalent to DERA; sectoral oversight via Departementet for Boliger og Infrastruktur", type:"data" },
    { id:"GL4",  change:"Asiaq Greenland Survey integrated — primary source for weather, hydrology, permafrost, and cryosphere",                                        type:"data" },
    { id:"GL5",  change:"PROMICE ice-sheet mass balance + glacial runoff forecasts integrated — critical for hydropower S2",                                            type:"data" },
    { id:"GL6",  change:"GEUS permafrost + bedrock mapping integrated (shared institution with Denmark) — foundation risk assessment",                                 type:"data" },
    { id:"GL7",  change:"R6a recalibrated with Arctic α range [0.55, 0.90] — permafrost + ice accretion + polar-low surge + glacial runoff + sea-ice logistics",        type:"enhanced" },
    { id:"GL8",  change:"R6b set to seismic floor [0.05, 0.15] — intraplate stable craton, retained for schema consistency",                                            type:"enhanced" },
    { id:"GL9",  change:"I3 Climate IRI reworked for Arctic hazards — permafrost + ice accretion + polar-low + glacial runoff",                                         type:"enhanced" },
    { id:"GL10", change:"I5 Permafrost + Coastal + Glacial Runoff Hazard introduced — combined foundation risk + coastal erosion + regime shift + iceberg exposure",     type:"new" },
    { id:"GL11", change:"I7 Ice Accretion Zone categorical — coastal/fjord vs interior classification",                                                                  type:"enhanced" },
    { id:"GL12", change:"I9 Hydro Single-Point Dependency — new metric for substations fed by single hydro plant",                                                       type:"new" },
    { id:"GL13", change:"R3 small-N relaxation — tier balance 2–50% per tier (vs standard 5–45%) given N~250",                                                           type:"enhanced" },
    { id:"GL14", change:"R4 computed within each islanded system only — no synthetic cross-settlement edges",                                                            type:"enhanced" },
    { id:"GL15", change:"R7 submarine-cable dependency — Greenland Connect single-cable exposure on most coastal routes",                                                type:"enhanced" },
    { id:"GL16", change:"Pituffik Space Base excluded — methodology §7 footnote surfaced on index/methodology/data/ssi-data.json",                                       type:"policy" },
    { id:"GL17", change:"Archive bundling with Denmark — Greenland pages join Denmark's monthly email from 2026-07 onward (ARCHIVE_BUNDLES)",                           type:"ops" },
    { id:"GL18", change:"FIRST_REFRESH gate = 2026-07 — skips April, May, June monthly runs to allow content stabilisation",                                             type:"ops" }
  ],

  /* ── version tracking ── */
  version: {
      ssi_version: "v4.0.2",
      country_deployment_version: "1.0",
      first_deployed: "2026-04-16",
      first_refresh: "2026-07",
      last_scoring_run: null,
      last_schema_validation: null
    }

  };
})();
// Compatibility alias
window.SSI_METADATA = window.SSIMetadata;
