// Slovakia SSI v4.0.2 metadata — KB §65 · greenfield thin-shell (Phase 2d)
// Pattern C (Wave 6c) — NO IIFE wrapper · KB §58.6 Canada IIFE root-cause
// Dual-global alias per KB §45.6
// Edition 01 (inaugural) · first refresh 2026-07-09 (CEE-South-2026 cohort dual-drop with Slovenia)

window.SSI_COUNTRY = 'slovakia';
window.SSI_EDITION = 'Edition 01';

window.SSIMetadata = {
  country: 'Slovakia',
  COUNTRY: 'Slovakia',
  country_code: 'SK',
  country_iso3: 'SVK',
  flag: '\u{1F1F8}\u{1F1F0}',  // 🇸🇰
  FLAG: '\u{1F1F8}\u{1F1F0}',
  cohort: 'CEE-South-2026',
  edition: 'Edition 01',
  first_refresh: '2026-07-09',
  engine_version: '4.0.2',
  kb_version: 'v25',
  bpg_version: 'v1.24',
  labels: {
    country_en: 'Slovakia',
    country_local: 'Slovensko',
    capital: 'Bratislava',
    capital_local: 'Bratislava',
    region_unit: 'NUTS-3 kraj',
    region_unit_local: 'samosprávny kraj',
    tso: 'SEPS (Slovenská elektrizačná prenosová sústava)',
    regulator: 'ÚRSO (Úrad pre reguláciu sieťových odvetví)',
    statistics_office: 'ŠÚ SR (Štatistický úrad Slovenskej republiky)',
    nem: 'OKTE, a.s. (SEPS-owned day-ahead + intraday operator)',
    bidding_zone: '10YSK-SEPS-----K'
  },
  stats: { sources: 18, variables: 95, components: 6, modifiers: 5 },
  methodology: {
    formula: 'R = base − Σ component contributions × modifiers',
    components: ['C', 'V', 'I', 'E', 'S', 'T'],
    modifiers: ['R3_C_mult', 'R4_F_topo', 'R6_restoration', 'R6_seismic', 'R7_cyber'],
    mc_iterations: 10000,
    r3_tiers: '4-tier (Capital-Intensive / Industrial-Secondary / Industrial-Major / Light-Rural-East)',
    r6_anchors: '2004 Tatra windstorm (~12,000 ha forest) · 2010 Pohronie + Spiš floods · 2002 Central European Danube flood · Pieniny klippen seismic',
    r7_ceiling: 1.03
  }
};

// ── Dual-global alias (KB §45.6) ──
window.SSI_METADATA = window.SSIMetadata;

// ── Components, sources, layers, regions, DSOs ──

window.SSI_METADATA.COMPONENTS_INDEX = [
  { code: 'C', name: 'Continuity',     ceiling: 0.30, drivers: 'SAIDI/SAIFI · ÚRSO quality reports · SEPS network statement' },
  { code: 'V', name: 'Voltage Quality', ceiling: 0.18, drivers: 'EN 50160 events · ZSD/SSD/VSD quarterly filings · 3-DSO heritage portfolio' },
  { code: 'I', name: 'Infrastructure', ceiling: 0.18, drivers: 'OSM topology · SEPS asset register · 400/220/110 kV inventory + Mochovce/Bohunice corridor' },
  { code: 'E', name: 'Economic',       ceiling: 0.14, drivers: 'ŠÚ SR NUTS-3 GDP · NBS regional accounts · automotive OEM concentration' },
  { code: 'S', name: 'Societal',       ceiling: 0.12, drivers: 'ŠÚ SR energy-poverty · Prešovský unemployment · Hungarian-minority share' },
  { code: 'T', name: 'Transition',     ceiling: 0.08, drivers: 'ÚRSO DER registry · post-Nováky coal-exit · Mochovce nuclear ramp-up' }
];

window.SSI_METADATA.DATA_SOURCES = [
  { id: 'd01_seps',         name: 'SEPS — Slovenská elektrizačná prenosová sústava (TSO)', freq: 'Daily',      status: 'live', vars: 14, feeds: 'C2,C3,I1,I2,I3,R4', sources: 'sepsas.sk network statement + ENTSO-E TP' },
  { id: 'd02_urso',         name: 'ÚRSO — Úrad pre reguláciu sieťových odvetví',           freq: 'Annual',     status: 'live', vars: 12, feeds: 'C1,C2,V1,V2,T1', sources: 'urso.gov.sk quality-of-supply + tariff decisions' },
  { id: 'd02b_dso',         name: '3 regional DSOs (ZSD / SSD / VSD)',                      freq: 'Quarterly',  status: 'live', vars: 18, feeds: 'C1,V1,V2,I2,I3', sources: 'zsdis.sk + ssd.sk + vsds.sk filings' },
  { id: 'd03_shmu',         name: 'SHMÚ — Slovenský hydrometeorologický ústav',             freq: 'Daily',      status: 'live', vars: 8,  feeds: 'I1,I2,I3,R6c_flood', sources: 'shmu.sk meteo + hydrology + Q100 maps' },
  { id: 'd03b_sgudz',       name: 'ŠGÚDŠ — Štátny geologický ústav D. Štúra',              freq: 'Multi-year', status: 'live', vars: 4,  feeds: 'R6_seismic', sources: 'geology.sk seismic hazard + SAV ESI catalogue' },
  { id: 'd04_susr',         name: 'ŠÚ SR — Štatistický úrad Slovenskej republiky',          freq: 'Quarterly',  status: 'live', vars: 16, feeds: 'E1,E2,S1,S2,S3', sources: 'statistics.sk NUTS-3 demographics + RegDat' },
  { id: 'd04b_nbs',         name: 'NBS — Národná banka Slovenska (central bank)',           freq: 'Quarterly',  status: 'live', vars: 4,  feeds: 'E1,E2', sources: 'nbs.sk national accounts + financial stability' },
  { id: 'd05_osm',          name: 'OSM Overpass — grid topology',                            freq: 'Monthly',    status: 'live', vars: 8,  feeds: 'I1,I2,I3,R4', sources: 'overpass-api.de power=substation/line · ISO3166 SK' },
  { id: 'd06_sazp',         name: 'SAŽP — Slovenská agentúra životného prostredia',         freq: 'Monthly',    status: 'live', vars: 5,  feeds: 'R5_corrosion,I8', sources: 'sazp.sk air-quality + ESPRI EIA portal' },
  { id: "CDS", name: "Copernicus CDS / ERA5-Land", url: "cds.climate.copernicus.eu", freq: "Annual", res: "0.1° (~11 km, ERA5-Land + daily-stats)", vars: 5, category: "Climate", feeds: "R2 Δ_climate (t_mean_c, heat_days, ice_days at 0.1° land grid)", registration: true },
  { id: 'd08_ujd_sr',       name: 'ÚJD SR — Úrad jadrového dozoru (nuclear safety)',         freq: 'Quarterly',  status: 'live', vars: 4,  feeds: 'R6_seismic,I3', sources: 'ujd.gov.sk Mochovce + Bohunice oversight + IAEA INSAG' },
  { id: 'd09_sk_cert',      name: 'SK-CERT (operated by NBÚ) + GovCERT.SK',                  freq: 'Continuous', status: 'live', vars: 5,  feeds: 'R7_cyber', sources: 'sk-cert.sk + govcert.gov.sk incident database + Act 366/2024' },
  { id: 'd10_nbu',          name: 'NBÚ — Národný bezpečnostný úrad (NIS2 competent authority)', freq: 'Annual', status: 'live', vars: 3,  feeds: 'R7_cyber', sources: 'nbu.gov.sk NIS2 single point of contact' },
  { id: 'd11_entsoe',       name: 'ENTSO-E TYNDP + Transparency Platform',                   freq: 'Annual',     status: 'live', vars: 6,  feeds: 'I1,I2,T1', sources: 'tyndp.entsoe.eu + transparency.entsoe.eu' },
  { id: 'd12_eurostat',     name: 'Eurostat — EU-27 NUTS-3 benchmarks',                      freq: 'Annual',     status: 'live', vars: 8,  feeds: 'E1,S1,T1', sources: 'ec.europa.eu/eurostat NUTS-3 regional + energy + DESI' },
  { id: 'd13_se',           name: 'Slovenské elektrárne (Mochovce + Bohunice V2)',           freq: 'Annual',     status: 'live', vars: 5,  feeds: 'I1,I3,R6_seismic', sources: 'seas.sk annual + Mochovce Unit 3 (Oct 2023) + Unit 4 commissioning' },
  { id: 'd14_okte',         name: 'OKTE — SK day-ahead + intraday operator',                 freq: 'Daily',      status: 'live', vars: 4,  feeds: 'T1,E1', sources: 'okte.sk market coupling + SDAC + SIDC' },
  { id: 'd15_iea_oecd',     name: 'IEA + OECD — energy benchmarks',                          freq: 'Annual',     status: 'live', vars: 6,  feeds: 'T1,E1', sources: 'iea.org + oecd.org energy statistics' },
    { id: "GEM", name: "GEM Global Seismic Hazard Map 2023.1", url: "globalquakemodel.org", freq: "Static", res: "0.05° (~5.5 km, rock-site PGA 475-yr)", vars: 1, category: "Hazard", feeds: "R6a seismic PGA, substation-level overlay (CC BY-NC-SA 4.0)" },
    { id: "Eurostat-NUTS3", name: "Eurostat NUTS-3 Regional Statistics", url: "ec.europa.eu/eurostat", freq: "Annual", res: "NUTS-3 (province / NUTS-2 unemployment)", vars: 5, category: "Socio-Econ", feeds: "R2 GDP/cap, unemp, elderly%, ep_rate, migration (CC BY 4.0)" },
];

window.SSI_METADATA.FREQ_DISTRIBUTION = {
  Weekly:    { count: 0,  sources: [] },
  Monthly:   { count: 3,  sources: ['OSM Overpass', 'SAŽP (air quality)', 'Copernicus ERA5/CMIP6'] },
  Quarterly: { count: 4,  sources: ['DSO filings (ZSD/SSD/VSD)', 'ŠÚ SR', 'NBS', 'ÚJD SR (nuclear)'] },
  Annual:    { count: 6,  sources: ['ÚRSO', 'ENTSO-E TYNDP', 'Eurostat', 'NBÚ', 'Slovenské elektrárne', 'IEA/OECD'] },
  Continuous:{ count: 2,  sources: ['SEPS (TSO)', 'SK-CERT'] },
  Daily:     { count: 3,  sources: ['SEPS', 'SHMÚ', 'OKTE'] }
};

window.SSI_METADATA.DATA_LAYERS = [
  { id: 'tso',        name: 'SEPS transmission (400/220/110 kV)',     vars: 14, status: 'live', sources: 'SEPS network statement + ENTSO-E' },
  { id: 'dso',        name: '3 regional DSOs (ZSD / SSD / VSD)',       vars: 18, status: 'live', sources: 'ZSD (E.ON) + SSD (EPH) + VSD (RWE)' },
  { id: 'regulator',  name: 'ÚRSO — quality + tariff',                 vars: 12, status: 'live', sources: 'ÚRSO annual quality reports' },
  { id: 'statistics', name: 'ŠÚ SR — NUTS-3 socio-economic',           vars: 16, status: 'live', sources: 'ŠÚ SR regional database RegDat' },
  { id: 'hazard',     name: 'Multi-hazard (seismic+flood+windstorm)',  vars: 15, status: 'live', sources: 'ŠGÚDŠ + SHMÚ + SAV ESI' },
  { id: 'cyber',      name: 'SK-CERT + GovCERT.SK + NBÚ',              vars: 8,  status: 'live', sources: 'SK-CERT (2009) + NIS2 Act 366/2024' },
  { id: 'topology',   name: 'OSM grid topology',                        vars: 8,  status: 'live', sources: 'OSM Overpass ISO3166 SK area filter' },
  { id: 'nuclear',    name: 'Mochovce + Bohunice oversight',            vars: 4,  status: 'live', sources: 'ÚJD SR + Slovenské elektrárne + IAEA INSAG' }
];

window.SSI_METADATA.REGIONS_NUTS3 = [
  { code: 'SK010', name: 'Bratislavský kraj',     capital: 'Bratislava',     tier: 'Capital-Intensive',     r3: 1.02 },
  { code: 'SK021', name: 'Trnavský kraj',         capital: 'Trnava',         tier: 'Industrial-Major',      r3: 1.04 },
  { code: 'SK022', name: 'Trenčiansky kraj',      capital: 'Trenčín',        tier: 'Industrial-Secondary',  r3: 1.05 },
  { code: 'SK023', name: 'Nitriansky kraj',       capital: 'Nitra',          tier: 'Industrial-Major',      r3: 1.04 },
  { code: 'SK031', name: 'Žilinský kraj',         capital: 'Žilina',         tier: 'Industrial-Major',      r3: 1.04 },
  { code: 'SK032', name: 'Banskobystrický kraj',  capital: 'Banská Bystrica',tier: 'Light-Rural-East',      r3: 1.07 },
  { code: 'SK041', name: 'Prešovský kraj',        capital: 'Prešov',         tier: 'Light-Rural-East',      r3: 1.07 },
  { code: 'SK042', name: 'Košický kraj',          capital: 'Košice',         tier: 'Industrial-Secondary',  r3: 1.05 }
];

window.SSI_METADATA.DSO_PANEL = [
  { name: 'Západoslovenská distribučná (ZSD)',  region: 'BA + TT + TN + NR',  share_pct: 40 },
  { name: 'Stredoslovenská distribučná (SSD)',  region: 'ZA + BB',            share_pct: 25 },
  { name: 'Východoslovenská distribučná (VSD)', region: 'PO + KE',            share_pct: 35 }
];


// ── Extended metadata for methodology.html / data.html / intelligence.html C-section ──
// KB §58.6 compliant — no IIFE wrapper, dual-global alias preserved above.

window.SSI_METADATA.COMPONENTS = [
  { id: 'C', name: 'Continuity', weight: 0.30, color: '#941914', isNew: false,
    metrics: [
      { id: 'C1', name: 'SAIDI (planned + unplanned)',     intra: 0.30, global: 0.090, norm: 'P5/P95 inverse',  source: 'ÚRSO 2023 — per-DSO quality reports' },
      { id: 'C2', name: 'SAIFI (interruption frequency)',   intra: 0.25, global: 0.075, norm: 'P5/P95 inverse',  source: 'ÚRSO 2023 — per-DSO' },
      { id: 'C3', name: 'Voltage class (max kV)',           intra: 0.20, global: 0.060, norm: 'log-scaled',      source: 'OSM Overpass + SEPS network statement' },
      { id: 'C4', name: 'Customer count (catchment)',       intra: 0.15, global: 0.045, norm: 'P5/P95 inverse',  source: 'ZSD/SSD/VSD + ŠÚ SR' },
      { id: 'C5', name: 'CAIDI restoration speed',          intra: 0.10, global: 0.030, norm: 'P5/P95 inverse',  source: 'ÚRSO 2023' }
    ]},
  { id: 'V', name: 'Voltage Quality', weight: 0.10, color: '#aa4234', isNew: false,
    metrics: [
      { id: 'V1', name: 'EN 50160 dip events',              intra: 0.40, global: 0.040, norm: 'count per 1000 cust/yr', source: 'ÚRSO + 3 DSOs' },
      { id: 'V2', name: 'Voltage swell events',             intra: 0.30, global: 0.030, norm: 'count per 1000 cust/yr', source: 'ÚRSO + 3 DSOs' },
      { id: 'V3', name: 'Harmonic distortion (THD)',        intra: 0.30, global: 0.030, norm: 'P95 of weekly THD',      source: 'ÚRSO quarterly filings' }
    ]},
  { id: 'I', name: 'Infrastructure', weight: 0.25, color: '#5d8563', isNew: false,
    metrics: [
      { id: 'I1', name: 'Snow/Ice IRI (Tatras)',           intra: 0.18, global: 0.045, norm: 'ERA5 reanalysis',   source: 'Copernicus ERA5 + SHMÚ', adaptive: true },
      { id: 'I2', name: 'Heat-wave IRI (Pannonian S)',     intra: 0.16, global: 0.040, norm: 'GDD anomaly',        source: 'Copernicus + SHMÚ', adaptive: true },
      { id: 'I3', name: 'Wind storm IRI (Tatra föhn)',     intra: 0.14, global: 0.035, norm: 'P99 m/s hourly',     source: 'SHMÚ + ERA5 — 2004 anchor', adaptive: true },
      { id: 'I4', name: 'Asset age cohort',                intra: 0.14, global: 0.035, norm: 'Markov-weighted',    source: 'SEPS + 3 DSOs annual reports' },
      { id: 'I5', name: 'Thermal stress (R6 proxy)',       intra: 0.10, global: 0.025, norm: 'IEEE C57.91',        source: 'IEEE C57.91 + Copernicus' },
      { id: 'I6', name: 'Substation density',              intra: 0.10, global: 0.025, norm: 'per km²',            source: 'OSM + ŠÚ SR' },
      { id: 'I7', name: 'Network length per cap',          intra: 0.08, global: 0.020, norm: 'P5/P95',             source: 'SEPS + 3 DSOs' },
      { id: 'I8', name: 'Industrial corrosion ISO 9223',   intra: 0.06, global: 0.015, norm: 'C2-C4 categorical',  source: 'SAŽP + ISO 9223 (U.S. Steel KE)' },
      { id: 'I9', name: 'Hydrogeological exposure',        intra: 0.04, global: 0.010, norm: 'SHMÚ Q100 overlay',   source: 'SHMÚ + SAŽP' }
    ]},
  { id: 'E', name: 'Economic', weight: 0.10, color: '#3b9eff', isNew: false,
    metrics: [
      { id: 'E1', name: 'Regulatory penalty exposure',     intra: 0.60, global: 0.060, norm: 'EUR per SAIDI min', source: 'ÚRSO tariff decisions' },
      { id: 'E2', name: 'Productivity loss (VoLL)',        intra: 0.40, global: 0.040, norm: 'EUR/kWh',            source: 'ACER 2023 + ŠÚ SR sector mix' }
    ]},
  { id: 'S', name: 'Saturation', weight: 0.20, color: '#b8863a', isNew: false,
    metrics: [
      { id: 'S1', name: 'Regional KPI — saturation',       intra: 0.45, global: 0.090, norm: 'load/capacity %',    source: 'SEPS + 3 DSOs' },
      { id: 'S2', name: 'Reverse power flow',              intra: 0.35, global: 0.070, norm: 'hours/yr reverse',    source: 'SEPS + ENTSO-E' },
      { id: 'S3', name: 'Criticality class',               intra: 0.20, global: 0.040, norm: 'categorical 1-5',     source: 'SEPS Network Statement' }
    ]},
  { id: 'T', name: 'Transition', weight: 0.05, color: '#22d3ee', isNew: true,
    metrics: [
      { id: 'T1', name: 'DER Stress Index',                intra: 1.00, global: 0.050, norm: 'composite',           source: 'ÚRSO DER registry + post-Nováky coal-exit', isNew: true }
    ]}
];

window.SSI_METADATA.MODIFIER_DEFS = [
  { id: 'R2', domain: 'Adaptive IRI + Climate',    range: 'internal',     description: 'Shifts weight from climate-IRI to structural metrics where local climate risk is low. CMIP6 SSP2-4.5 projections adjust forward-looking risk.' },
  { id: 'R3', domain: 'Consequence + Poverty',     range: '[0.70, 1.30]', description: 'Amplifies risk for kraje serving large/energy-poor populations with high economic dependency. SK uses a 4-tier calibration (1.02 / 1.04 / 1.05 / 1.07) reflecting the pronounced BA-vs-East-Slovakia GDP gradient.' },
  { id: 'R4', domain: 'Graph Criticality',         range: '[0.80, 1.35]', description: 'Penalises topological bottlenecks: high betweenness centrality, bridge nodes, low degree. Built from OSM power graph.' },
  { id: 'R6a',domain: 'Restoration Speed',         range: '[0.90, 1.10]', description: 'ÚRSO-CAIDI-based: rewards fast-restoring areas, penalises slow ones. High Tatras and Slovak Karst valleys carry a mountain-valley access penalty.' },
  { id: 'R6b',domain: 'Network Topology',          range: '[1.00, 1.25]', description: 'Network centrality and ring topology. Penalises kraje in single-source or low-redundancy configurations (notably eastern Prešov / Košice rural).' },
  { id: 'R7', domain: 'Digital Readiness',         range: '[0.99, 1.03]', description: 'Regional DESI digital readiness score, SK-CERT (founded 2009) maturity, NIS2 transposition (Act 366/2024 in force 1 Jan 2025). Ceiling 1.03 sits between LV/LT (1.02) and SI/CZ (1.04).' }
];

window.SSI_METADATA.NORM_METHODS = [
  { id: 'A', name: 'Robust fleet percentile (P5/P95)',
    formula: 'x_norm = clip((x - P5) / (P95 - P5), 0, 1)',
    applies: 'C1, C2, C4, C5, E1, E2, I7' },
  { id: 'B', name: 'Standard fleet percentile',
    formula: 'x_norm = (rank(x) - 1) / (n - 1)',
    applies: 'I4, S1, S2' },
  { id: 'C', name: 'Bounded rescaling (log)',
    formula: 'x_norm = log10(x / x_min) / log10(x_max / x_min)',
    applies: 'C3 (voltage class)' },
  { id: 'D', name: 'Categorical mapping',
    formula: 'x_norm = lookup[x] where lookup maps ordinal → [0,1]',
    applies: 'I8 (ISO 9223), S3 (criticality class)' }
];

window.SSI_METADATA.VALIDATION_CHECKS = [
  { check: 'Schema validation',                                       criterion: 'All required top-level + sub keys present, no nulls',          status: 'verified', isNew: false },
  { check: 'OSM Overpass ISO3166 area filter',                        criterion: 'ISO3166-1=SK area filter — zero CZ/PL/UA/HU/AT contamination', status: 'verified', isNew: false },
  { check: 'Polygon containment (1,516 subs → 8 NUTS-3 kraje)',       criterion: 'Every substation falls inside exactly one kraj polygon',       status: 'verified', isNew: true },
  { check: 'R3 4-tier distribution (BA / W-auto / TN-KE / BB-PO)',    criterion: '1 / 3 / 2 / 2 across 8 kraje — economic gradient respected',   status: 'verified', isNew: true },
  { check: 'R6 multi-hazard coverage',                                criterion: 'Seismic (Pieniny) + flood (Danube/Tisza) + storm (Tatras)',    status: 'verified', isNew: true },
  { check: 'R6c flood anchor — 2010 Pohronie + 2023 East SK',         criterion: 'BB + PO + KE flood-zone enrichment HIGH',                      status: 'verified', isNew: true },
  { check: 'R7 ceiling 1.03 (DESI 2024 ~0.50 · SK-CERT 2009)',        criterion: 'Below SI/CZ 1.04 — NIS2 Act 366/2024 in force 1 Jan 2025',     status: 'verified', isNew: false },
  { check: 'Mochovce-corridor seismic α (NR + TT)',                   criterion: 'Mochovce + Bohunice V2 + ÚJD SR oversight + IAEA INSAG',       status: 'verified', isNew: true },
  { check: 'MIN_FLEET[SK]=1100 floor enforced',                       criterion: '1,516 substations exceeds 1,100 minimum — stub-gate clear',    status: 'verified', isNew: true },
  { check: 'No C5 corrosion (landlocked)',                            criterion: 'C2-C4 declared; C5 omitted (Slovakia has no sea coast)',       status: 'verified', isNew: true }
];

window.SSI_METADATA.CHANGELOG = [
  { id: 'SK-S28-9', change: 'Greenfield thin-shell rollout — 8 pages authored directly on Phase-2 architecture (no fat-HTML predecessor)', type: 'enhanced', section: 'KB §65' },
  { id: 'SK-S28-8', change: 'Section G deepDives rotation — 8 SK kraje (Mochovce Unit-4 commissioning anchor on Nitriansky kraj)',         type: 'new',      section: 'intelligence G' },
  { id: 'SK-S28-7', change: 'Edition patcher anchored at FIRST_REFRESH 2026-07-09 (CEE-South-2026 dual-drop with Slovenia)',               type: 'enhanced', section: 'intelligence' },
  { id: 'SK-S28-6', change: 'ESG report — slovakia entry in COUNTRY_SOURCES (14 SK-specific references)',                                  type: 'new',      section: 'esg-report' },
  { id: 'SK-S28-5', change: 'R3 4-tier calibration — Capital / W-Auto / TN-KE / BB-PO (vs SI 3-tier; reflects east-west GDP gradient)',     type: 'new',      section: 'methodology' },
  { id: 'SK-S28-4', change: 'R6 modifier set — Pieniny seismic (PO/KE) + Danube/Tisza flood (BA/NR/KE/PO) + Tatra windstorm 2004 anchor', type: 'new',      section: 'methodology' },
  { id: 'SK-S28-3', change: 'd05_osm LIVE — 1,516 substations + 1,636 power lines via ISO3166-1=SK area filter',                            type: 'data',     section: 'methodology' },
  { id: 'SK-S28-2', change: '3 regional DSOs (ZSD/SSD/VSD) + SEPS TSO + ÚRSO regulator + ÚJD SR nuclear safety wired',                      type: 'data',     section: 'methodology' },
  { id: 'SK-S28-1', change: 'KB v25 §65 — Slovakia inaugural onboarding (CEE-South-2026 cohort member 2 of 3)',                            type: 'enhanced', section: 'KB §65' }
];

// ── ESG-report data-source registry (Phase 2b — KB §65) ──
// Row form: [name, source, vintage, frequency, license, reports_tag, blocked_flag?]
// Consumed by esg-sections.js → getReportSources() to render the
// "Data Sources & Vintage" card on each of the 6 ESG reports.
window.SSI_METADATA.ESG_SOURCES = [
  ['ERA5 Climate Reanalysis','Copernicus CDS','2024','Weekly','CC-BY-4.0','R1, R3'],
  ['Slovak Seismic Hazard Map','ŠGÚDŠ + SAV ESI (PGA 475-yr)','2023','Multi-year','Open','R1, R3'],
  ['Population & Economics','ŠÚ SR (Štatistický úrad SR)','2024','Annual','Open','R2, R3'],
  ['Energy Market Data','SEPS + OKTE','2024','Daily','Regulated','R2, R4'],
  ['Renewable Installations','ÚRSO DER registry','2024','Monthly','Open','R4'],
  ['Weather + Hydrology','SHMÚ — Slovenský hydrometeorologický ústav','2024','Daily','CC-BY-4.0','R1'],
  ['Flood Mapping','SHMÚ Q100 + 2010/2018/2023 flood overlays','2024','Monthly','CC-BY-4.0','R1'],
  ['Nuclear Safety Oversight','ÚJD SR — Mochovce + Bohunice yearly safety reports','2024','Quarterly','Regulated','R1, R3'],
  ['Cybersecurity Posture','SK-CERT (NBÚ-operated, est. 2009) + GovCERT.SK','2024','Annual','Open','R6'],
  ['DESI Connectivity','European Commission','2024','Annual','Open','R6'],
  ['IEEE C57.91 Thermal Model','IEEE','Standard','N/A','Published','R1'],
  ['CIGRE TB 761 Markov','CIGRE','2019','N/A','Published','R1, R3'],
  ['ISO 9223 Corrosion (C2-C4 only — landlocked)','ISO','2012','N/A','Published','R5'],
  ['CMIP6 SSP2-4.5 Projections','Copernicus CDS','2024','Multi-year','CC-BY-4.0','R1']
];

// Mirror onto the lower-case alias too
window.SSIMetadata = window.SSI_METADATA;
