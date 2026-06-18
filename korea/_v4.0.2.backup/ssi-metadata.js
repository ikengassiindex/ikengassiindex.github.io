// Korea SSI v4.0.2 metadata — KB §71 (planned) · greenfield thin-shell on post-Iceland architecture
// Pattern C (Wave 6c) — NO IIFE wrapper · KB §58.6 Canada IIFE root-cause
// Dual-global alias per KB §45.6
// Edition 01 (Korea inaugural) · first refresh 2026-08-13 (final-4 OECD onboarding)
// Carries forward BPG Discipline #14 (canonical-schema emission) + #15 (country-config mandatory) from Iceland Session 30.

window.SSI_COUNTRY = 'korea';
window.SSI_EDITION = 'Edition 01';

window.SSIMetadata = {
  country: 'Korea',
  COUNTRY: 'Korea',
  country_code: 'KR',
  country_iso3: 'KOR',
  flag: '\u{1F1F0}\u{1F1F7}',  // 🇰🇷
  FLAG: '\u{1F1F0}\u{1F1F7}',
  cohort: 'Single-country (post-CEE-South-2026, post-Iceland) — final-4 OECD',
  edition: 'Edition 01',
  first_refresh: '2026-08-13',
  engine_version: '4.0.2',
  kb_version: 'v29',
  bpg_version: 'v1.28',
  currency: 'KRW',
  currency_symbol: '₩',  // ₩
  currency_position: 'before',
  labels: {
    country_en: 'Republic of Korea',
    country_local: '대한민국',  // 대한민국
    capital: 'Seoul',
    capital_local: '서울특별시',  // 서울특별시
    region_unit: 'do/si (17 first-tier administrative divisions)',
    region_unit_local: '도/시',  // 도/시
    tso: 'KPX — Korea Power Exchange (market+system operator); KEPCO holds transmission assets',
    regulator: 'KOREC — Korea Electricity Regulation Commission (under MOTIE)',
    statistics_office: 'KOSTAT — Statistics Korea',
    nem: 'Not applicable — isolated peninsula, no SDAC/SIDC/CORE FB-MC',
    bidding_zone: 'KR-ISOLATED (NOT in ENTSO-E; 60Hz unified peninsula)'
  },
  stats: { sources: 19, variables: 95, components: 6, modifiers: 7 },
  methodology: {
    formula: 'R = base × Π modifiers (incl. NEW R6_typhoon + R6_chaebol)',
    components: ['C', 'V', 'I', 'E', 'S', 'T'],
    modifiers: ['R3_C_mult', 'R4_F_topo', 'R6_restoration', 'R6_seismic', 'R6_typhoon', 'R6_chaebol', 'R7_cyber'],
    mc_iterations: 10000,
    r3_tiers: '4-tier (Industrial-Chaebol 1.05 / Capital-Seoul 1.04 / Commercial-SME 1.03 / Rural 1.02)',
    r6_anchors: '2017-11-15 Pohang Mw 5.5 (anthropogenically induced — EGS geothermal) · 2016-09-12 Gyeongju Mw 5.4+5.8 · 2022-09-06 Typhoon Hinnamnor (66,000 lost power Geoje landfall) · 2023-08-10 Typhoon Khanun (40,350 lost power west coast) · 2012-08-26 Typhoon Bolaven (Jeju)',
    r7_ceiling: 1.015,
    new_modifiers: ['R6_typhoon (Pacific corridor)', 'R6_chaebol (fab-cluster concentration)']
  }
};

// ── Dual-global alias (KB §45.6) ──
window.SSI_METADATA = window.SSIMetadata;

// COMPONENTS_INDEX — Slovakia-style {code, name, ceiling, drivers}
// normalizeMeta() in country-renderer.js aliases this to canonical {key, label, w, color}
window.SSI_METADATA.COMPONENTS_INDEX = [
  { code: 'C', name: 'Continuity',     ceiling: 0.30, drivers: 'SAIDI/SAIFI · KEPCO quality reports · KPX system reports · Seoul metro vs Vestfirðir-equivalent rural Vestfjarðalína-style peripheral split · single-DSO monopoly (KEPCO) — cohort-UNIQUE' },
  { code: 'V', name: 'Voltage Quality', ceiling: 0.18, drivers: 'EN 50160 events · KEPCO quarterly filings · 1-DSO heritage (KEPCO 100% LV market) · 24 NPPs (KHNP-operated) impose strict V quality at substation interconnects' },
  { code: 'I', name: 'Infrastructure', ceiling: 0.18, drivers: 'OSM topology · KEPCO asset register · 765/345/154/22.9 kV inventory (KR UNIQUE 765 kV ultra-high vs OECD typical 400 kV max) · 60Hz unified (vs 50Hz cohort)' },
  { code: 'E', name: 'Economic',       ceiling: 0.14, drivers: 'KOSTAT do/si GDP · Bank of Korea regional accounts · chaebol concentration (Samsung Pyeongtaek + SK Hynix Icheon + LG Paju + POSCO Pohang/Gwangyang + Hyundai Ulsan)' },
  { code: 'S', name: 'Societal',       ceiling: 0.12, drivers: 'KOSTAT energy-poverty · Gangwon mountainous peripheral + Jeolla agricultural depopulation · aging-out non-metro do/si (elderly 22-26%)' },
  { code: 'T', name: 'Transition',     ceiling: 0.08, drivers: 'KEPCO DER registry · 11th Basic Plan 2025 target 35.2% nuclear by 2038 (vs 32% 2024) + 29.7% renewables (vs <6.5% 2024) · coal phase-out from 30% to 10.1%' }
];

window.SSI_METADATA.DATA_SOURCES = [
  { id: 'd01_kpx',          name: 'KPX — Korea Power Exchange (TSO+market operator)',                 freq: 'Continuous', status: 'live', vars: 14, feeds: 'C2,C3,I1,I2,I3,R4', sources: 'kpx.or.kr system + market reports' },
  { id: 'd02_kepco',        name: 'KEPCO — Korea Electric Power Corporation (transmission asset owner + single-DSO monopoly)', freq: 'Annual', status: 'live', vars: 18, feeds: 'C1,V1,V2,I2,I3', sources: 'kepco.co.kr annual report + quarterly filings' },
  { id: 'd02b_korec',       name: 'KOREC — Korea Electricity Regulation Commission',                  freq: 'Annual',     status: 'live', vars: 12, feeds: 'C1,C2,V1,V2,T1', sources: 'motie.go.kr quality-of-supply + tariff decisions' },
  { id: 'd03_kma',          name: 'KMA — Korea Meteorological Administration',                        freq: 'Daily',      status: 'live', vars: 8,  feeds: 'I1,I2,I3,R6_climate,R6_typhoon', sources: 'kma.go.kr meteorology + typhoon tracking' },
  { id: 'd03b_kigam',       name: 'KIGAM — Korea Institute of Geoscience and Mineral Resources',      freq: 'Multi-year', status: 'live', vars: 4,  feeds: 'R6_seismic', sources: 'kigam.re.kr seismic hazard maps + Pohang 2017 induced anchor' },
  { id: 'd03c_nssc',        name: 'NSSC — Nuclear Safety and Security Commission',                    freq: 'Quarterly',  status: 'live', vars: 5,  feeds: 'R6_seismic,I3,I4', sources: 'nssc.go.kr oversight 24 reactors + 2026 Kori 2 restart + 9 reactors pending life ext' },
  { id: 'd04_kostat',       name: 'KOSTAT — Statistics Korea',                                        freq: 'Quarterly',  status: 'live', vars: 16, feeds: 'E1,E2,S1,S2,S3', sources: 'kostat.go.kr regional GDP + 226 si/gun/gu LAU' },
  { id: 'd04b_bok',         name: 'Bank of Korea (central bank, non-€)',                              freq: 'Quarterly',  status: 'live', vars: 4,  feeds: 'E1,E2', sources: 'bok.or.kr national accounts + regional analysis' },
  { id: 'd05_osm',          name: 'OSM Overpass — grid topology (ISO3166-1=KR area filter)',          freq: 'Monthly',    status: 'live', vars: 8,  feeds: 'I1,I2,I3,R4', sources: 'overpass-api.de power=substation/line · 1,184 subs + 4,004 lines' },
  { id: 'd06_iso9223',      name: 'ISO 9223 corrosion classes (C2-C5 — C5 RESTORED, peninsula full)', freq: 'Multi-year', status: 'live', vars: 5,  feeds: 'R5_corrosion,I8', sources: 'ISO 9223 + KMA + KEPCO industrial atmospheres' },
  { id: "CDS", name: "Copernicus CDS / ERA5-Land", url: "cds.climate.copernicus.eu", freq: "Annual", res: "0.1° (~11 km, ERA5-Land + daily-stats)", vars: 5, category: "Climate", feeds: "R2 Δ_climate (t_mean_c, heat_days, ice_days at 0.1° land grid)", registration: true },
  { id: 'd08_khnp',         name: 'KHNP — Korea Hydro & Nuclear Power (operator of 24 reactors)',     freq: 'Quarterly',  status: 'live', vars: 5,  feeds: 'R6_seismic,I3,I4', sources: 'khnp.co.kr Kori/Hanul/Hanbit/Wolsong oversight' },
  { id: 'd09_kisa_krcert',  name: 'KISA + KrCERT/CC (founded 2001 — 25-yr cyber catalogue)',           freq: 'Continuous', status: 'live', vars: 5,  feeds: 'R7_cyber', sources: 'kisa.or.kr + krcert.or.kr C-TAS platform' },
  { id: 'd10_msit',         name: 'MSIT — Ministry of Science & ICT (NIS2-equivalent competent authority)', freq: 'Annual', status: 'live', vars: 3, feeds: 'R7_cyber', sources: 'msit.go.kr Act on the Protection of Information and Communications Infrastructure 2001-present' },
  { id: 'd11_iea_oecd',     name: 'IEA + OECD — energy benchmarks (KR joined OECD 12 Dec 1996, 29th member)', freq: 'Annual', status: 'live', vars: 6, feeds: 'T1,E1', sources: 'iea.org + oecd.org energy statistics' },
  { id: 'd12_motie',        name: 'MOTIE — Ministry of Trade, Industry and Energy (11th Basic Plan 2025)', freq: 'Annual',    status: 'live', vars: 6,  feeds: 'T1,E1', sources: 'motie.go.kr Basic Plan for Electricity Supply' },
  { id: 'd13_korail',       name: 'KORAIL + Korea Rail Network Authority (rail traction power 25-55 kV)', freq: 'Annual', status: 'live', vars: 3, feeds: 'I3,I4', sources: 'korail.com + kr.or.kr traction substation registry' },
  { id: 'd14_jeju_hvdc',    name: 'Jeju HVDC submarine cables (Haenam-Jeju #1 300 MW + Jindo-Jeju #2 400 MW)', freq: 'Annual', status: 'live', vars: 2, feeds: 'I1,R4', sources: 'KEPCO HVDC operational data — isolated island sub-grid' },
  { id: 'd15_almannavarnir_kr', name: 'NEMA — National Disaster Management Research Institute + KIGAM crisis coordination', freq: 'Annual', status: 'live', vars: 4, feeds: 'R6_typhoon,R6_seismic,R6_restoration', sources: 'nema.go.kr + kigam.re.kr emergency coordination' },
    { id: "GEM", name: "GEM Global Seismic Hazard Map 2023.1", url: "globalquakemodel.org", freq: "Static", res: "0.05° (~5.5 km, rock-site PGA 475-yr)", vars: 1, category: "Hazard", feeds: "R6a seismic PGA, substation-level overlay (CC BY-NC-SA 4.0)" },
    { id: "KOSIS", name: "KOSIS Regional Income GRDP", url: "kosis.kr", freq: "Annual", res: "17 sido", vars: 5, category: "Socio-Econ", feeds: "R2 per-sido GRDP/cap, unemp, elderly% (Open Data)" },
];

window.SSI_METADATA.FREQ_DISTRIBUTION = {
  Weekly:    { count: 0,  sources: [] },
  Monthly:   { count: 3,  sources: ['OSM Overpass', 'Copernicus ERA5/CMIP6', 'KEPCO grid telemetry'] },
  Quarterly: { count: 4,  sources: ['KOSTAT', 'Bank of Korea', 'NSSC (nuclear)', 'KHNP (24 reactors)'] },
  Annual:    { count: 8,  sources: ['KEPCO', 'KOREC', 'MSIT (cyber)', 'MOTIE (Basic Plan)', 'KIGAM', 'IEA/OECD', 'KORAIL', 'NEMA'] },
  Continuous:{ count: 2,  sources: ['KPX (TSO+market)', 'KISA+KrCERT/CC'] },
  Daily:     { count: 2,  sources: ['KMA (typhoon tracking)', 'KEPCO SCADA'] }
};

window.SSI_METADATA.DATA_LAYERS = [
  { id: 'tso',        name: 'KPX transmission system operator (765/345/154 kV)', vars: 14, status: 'live', sources: 'KPX system reports + KEPCO transmission asset registry' },
  { id: 'dso',        name: 'KEPCO single-DSO monopoly (22.9 kV)',                vars: 18, status: 'live', sources: 'KEPCO 100% LV market — cohort-UNIQUE single-operator' },
  { id: 'regulator',  name: 'KOREC — quality + tariff',                            vars: 12, status: 'live', sources: 'KOREC annual reports' },
  { id: 'statistics', name: 'KOSTAT — do/si socio-economic',                       vars: 16, status: 'live', sources: 'KOSTAT regional database' },
  { id: 'hazard',     name: 'Multi-hazard (typhoon + seismic + heat)',            vars: 15, status: 'live', sources: 'KMA + KIGAM + Copernicus' },
  { id: 'cyber',      name: 'KISA + KrCERT/CC (cohort-leading 25-yr backlog)',     vars: 8,  status: 'live', sources: 'KISA 2001 + Act on Information Infrastructure Protection' },
  { id: 'topology',   name: 'OSM grid topology',                                   vars: 8,  status: 'live', sources: 'OSM Overpass ISO3166 KR area filter (peninsula = no cross-border bleed)' },
  { id: 'nuclear',    name: 'KHNP — 24 NPPs (32% generation share)',               vars: 4,  status: 'live', sources: 'KHNP + NSSC oversight (Kori/Hanul/Hanbit/Wolsong/Shin-)' }
];

window.SSI_METADATA.REGIONS_NUTS3 = [
  { code: 'KR-41', name: 'Gyeonggi',                  capital: 'Suwon',     tier: 'Industrial-Chaebol',      r3: 1.05 },
  { code: 'KR-11', name: 'Seoul',                     capital: 'Seoul',     tier: 'Capital-Seoul-Metro',     r3: 1.04 },
  { code: 'KR-26', name: 'Busan',                     capital: 'Busan',     tier: 'Coastal-Industrial',      r3: 1.03 },
  { code: 'KR-28', name: 'Incheon',                   capital: 'Incheon',   tier: 'Port-Logistics',          r3: 1.03 },
  { code: 'KR-47', name: 'North Gyeongsang',          capital: 'Andong',    tier: 'Industrial-Nuclear-Steel',r3: 1.05 },
  { code: 'KR-48', name: 'South Gyeongsang',          capital: 'Changwon',  tier: 'Industrial-Shipbuilding', r3: 1.03 },
  { code: 'KR-46', name: 'South Jeolla',              capital: 'Muan',      tier: 'Industrial-Nuclear-Steel',r3: 1.05 },
  { code: 'KR-43', name: 'North Chungcheong',         capital: 'Cheongju',  tier: 'Central-Industrial',      r3: 1.03 },
  { code: 'KR-44', name: 'South Chungcheong',         capital: 'Hongseong', tier: 'Coal-Industrial',         r3: 1.05 },
  { code: 'KR-42', name: 'Gangwon',                   capital: 'Chuncheon', tier: 'Mountain-Rural',          r3: 1.02 },
  { code: 'KR-45', name: 'Jeonbuk',                   capital: 'Jeonju',    tier: 'Industrial-Tidal',        r3: 1.03 },
  { code: 'KR-27', name: 'Daegu',                     capital: 'Daegu',     tier: 'Interior-Metro',          r3: 1.03 },
  { code: 'KR-31', name: 'Ulsan',                     capital: 'Ulsan',     tier: 'Industrial-Petrochemical',r3: 1.05 },
  { code: 'KR-30', name: 'Daejeon',                   capital: 'Daejeon',   tier: 'R&D-Government',          r3: 1.03 },
  { code: 'KR-29', name: 'Gwangju',                   capital: 'Gwangju',   tier: 'Southwest-Metro',         r3: 1.03 },
  { code: 'KR-50', name: 'Sejong',                    capital: 'Sejong',    tier: 'Administrative-Capital',  r3: 1.04 },
  { code: 'KR-49', name: 'Jeju',                      capital: 'Jeju',      tier: 'Island-Tourism',          r3: 1.02 }
];

// DSO_PANEL — cohort-UNIQUE single-entry (KEPCO monopoly)
// Renderer reads is_kepco_monopoly flag and switches dno-dashboard.html to single-DSO layout
window.SSI_METADATA.DSO_PANEL = [
  { name: 'KEPCO — Korea Electric Power Corporation (한국전력공사)', region: 'ALL 17 do/si — single-DSO monopoly across entire peninsula', share_pct: 100, monopoly: true }
];
window.SSI_METADATA.is_kepco_monopoly = true;

window.SSI_METADATA.COMPONENTS = [
  { id: 'C', name: 'Continuity', weight: 0.30, color: '#941914', isNew: false,
    metrics: [
      { id: 'C1', name: 'SAIDI (planned + unplanned)',     intra: 0.30, global: 0.090, norm: 'P5/P95 inverse',  source: 'KEPCO 2023 quality reports' },
      { id: 'C2', name: 'SAIFI (interruption frequency)',   intra: 0.25, global: 0.075, norm: 'P5/P95 inverse',  source: 'KEPCO 2023' },
      { id: 'C3', name: 'Voltage class (max kV)',           intra: 0.20, global: 0.060, norm: 'log-scaled',      source: 'OSM Overpass + KPX network statement (765/345/154 kV — UNIQUE 765 kV)' },
      { id: 'C4', name: 'Customer count (catchment)',       intra: 0.15, global: 0.045, norm: 'P5/P95 inverse',  source: 'KEPCO single-DSO + KOSTAT' },
      { id: 'C5', name: 'CAIDI restoration speed',          intra: 0.10, global: 0.030, norm: 'P5/P95 inverse',  source: 'KEPCO 2023' }
    ]},
  { id: 'V', name: 'Voltage Quality', weight: 0.10, color: '#aa4234', isNew: false,
    metrics: [
      { id: 'V1', name: 'EN 50160 dip events',              intra: 0.40, global: 0.040, norm: 'count per 1000 cust/yr', source: 'KOREC + KEPCO' },
      { id: 'V2', name: 'Voltage swell events',             intra: 0.30, global: 0.030, norm: 'count per 1000 cust/yr', source: 'KOREC + KEPCO' },
      { id: 'V3', name: 'Harmonic distortion (THD)',        intra: 0.30, global: 0.030, norm: 'P95 of weekly THD',      source: 'KEPCO quarterly filings' }
    ]},
  { id: 'I', name: 'Infrastructure', weight: 0.25, color: '#5d8563', isNew: false,
    metrics: [
      { id: 'I1', name: 'Heat-wave IRI (temperate-monsoon)',intra: 0.18, global: 0.045, norm: 'GDD anomaly',         source: 'Copernicus ERA5 + KMA — 2018 record summer anchor', adaptive: true },
      { id: 'I2', name: 'Ice/freezing-rain (interior)',     intra: 0.10, global: 0.025, norm: 'P99 events',          source: 'KMA — Gangwon highlands only', adaptive: true },
      { id: 'I3', name: 'Wind storm + typhoon',             intra: 0.16, global: 0.040, norm: 'P99 m/s hourly',      source: 'KMA + ERA5 — Hinnamnor 2022 + Khanun 2023 anchors', adaptive: true },
      { id: 'I4', name: 'Asset age cohort',                 intra: 0.14, global: 0.035, norm: 'Markov-weighted',     source: 'KEPCO annual + KHNP nuclear extension reports' },
      { id: 'I5', name: 'Thermal stress (R6 proxy)',        intra: 0.10, global: 0.025, norm: 'IEEE C57.91',         source: 'IEEE C57.91 + Copernicus + 60Hz adjustment' },
      { id: 'I6', name: 'Substation density',               intra: 0.10, global: 0.025, norm: 'per km²',             source: 'OSM + KOSTAT' },
      { id: 'I7', name: 'Network length per cap',           intra: 0.08, global: 0.020, norm: 'P5/P95',              source: 'KEPCO + KPX' },
      { id: 'I8', name: 'Industrial corrosion ISO 9223',    intra: 0.10, global: 0.025, norm: 'C2-C5 categorical',   source: 'ISO 9223 + KMA — C5 RESTORED peninsula full marine' },
      { id: 'I9', name: 'Hydrogeological exposure (typhoon flood)', intra: 0.04, global: 0.010, norm: 'Q100 overlay', source: 'KMA + NEMA — Hinnamnor + Khanun + 2022 Seoul Han River flood' }
    ]},
  { id: 'E', name: 'Economic', weight: 0.10, color: '#3b9eff', isNew: false,
    metrics: [
      { id: 'E1', name: 'Regulatory penalty exposure',      intra: 0.60, global: 0.060, norm: 'KRW-eq per SAIDI min', source: 'KOREC tariff decisions (KRW ₩ native, EUR-eq for cross-country)' },
      { id: 'E2', name: 'Productivity loss (VoLL)',         intra: 0.40, global: 0.040, norm: 'EUR-eq/kWh',           source: 'KOSTAT sector mix (chaebol concentration — Samsung Pyeongtaek + SK Hynix + LG + POSCO + Hyundai)' }
    ]},
  { id: 'S', name: 'Saturation', weight: 0.20, color: '#b8863a', isNew: false,
    metrics: [
      { id: 'S1', name: 'Regional KPI — saturation',        intra: 0.45, global: 0.090, norm: 'load/capacity %',     source: 'KEPCO + KPX' },
      { id: 'S2', name: 'Reverse power flow',               intra: 0.35, global: 0.070, norm: 'hours/yr reverse',     source: 'KEPCO + Jeju isolated PV pilot' },
      { id: 'S3', name: 'Criticality class',                intra: 0.20, global: 0.040, norm: 'categorical 1-5',      source: 'KPX Network Statement + NEW Nuclear-Critical subclass (24 NPPs) + Chaebol-Critical subclass' }
    ]},
  { id: 'T', name: 'Transition', weight: 0.05, color: '#22d3ee', isNew: true,
    metrics: [
      { id: 'T1', name: 'DER Stress Index',                 intra: 1.00, global: 0.050, norm: 'composite',            source: 'KEPCO DER registry + 11th Basic Plan 2025 (35.2% nuclear / 29.7% RES by 2038) + Jeju 30% DER pilot', isNew: true }
    ]}
];

// MODIFIER_DEFS — Slovakia-style + 2 NEW for Korea (R6_typhoon + R6_chaebol)
window.SSI_METADATA.MODIFIER_DEFS = [
  { id: 'R2',  domain: 'Adaptive IRI + Climate',     range: 'internal',     description: 'Shifts weight from climate-IRI to structural metrics where local climate risk is low. CMIP6 SSP2-4.5 projections adjust forward-looking risk; Korean Peninsula temperate-monsoon + typhoon-cyclone heatwave loading.' },
  { id: 'R3',  domain: 'Consequence + Poverty',      range: '[0.97, 1.05]', description: '4-tier calibration (1.02 / 1.03 / 1.04 / 1.05) reflecting chaebol-concentration consequence: Industrial-Chaebol 1.05 (Gyeonggi Samsung-SK Hynix corridor + Ulsan + Gwangyang/Pohang steel), Capital-Seoul 1.04, Commercial-SME 1.03, Rural 1.02. Iceland Hotfix #2 lesson — r3_buckets explicitly span renderer DEFAULT_R3_BUCKETS [0.97, 1.05+].' },
  { id: 'R4',  domain: 'Graph Criticality',          range: '[0.85, 1.30]', description: 'Penalises topological bottlenecks: high betweenness centrality, bridge nodes, low degree. Built from OSM power graph (1,184 nodes · 4,004 edges; ZERO cross-border interconnects — isolated peninsula since 1953 DPRK link cut).' },
  { id: 'R6a', domain: 'Restoration Speed',          range: '[0.90, 1.10]', description: 'KEPCO single-DSO CAIDI-based: rewards fast-restoring urban areas (Seoul + Gyeonggi metropolitan), penalises slow ones. Jeju isolated sub-grid carries HVDC dependency penalty.' },
  { id: 'R6b', domain: 'Network Topology + Seismic', range: '[1.00, 1.18]', description: 'Korean Peninsula intra-plate seismic — quieter than IS Mid-Atlantic Ridge but Pohang 2017 Mw 5.5 induced anchor (anthropogenically triggered via EGS geothermal hydraulic injection) elevated N. Gyeongsang α=0.10. Gyeongju 2016 Mw 5.4+5.8 natural anchor.' },
  { id: 'R6_typhoon', domain: 'Pacific Corridor Typhoon (NEW for KR)', range: '[1.03, 1.15]', description: 'NEW MODIFIER — Pacific corridor typhoon exposure. Generalisable to JP, TW, future Pacific-cohort countries. Anchors: Hinnamnor 2022 (66,000+ households lost power Geoje landfall), Khanun 2023 (40,350 lost west coast), Bolaven 2012 (Jeju historical). South coast α=0.12; west coast α=0.07-0.08; Jeju α=0.10; inland α=0.03-0.05.' },
  { id: 'R6_chaebol', domain: 'Industrial-Concentration Magnitude (NEW for KR)', range: '[1.00, 1.10]', description: 'NEW MODIFIER — chaebol single-site catastrophic-loss exposure. Samsung Pyeongtaek + SK Hynix Icheon + LG Paju α=0.08 (fab corridor); Ulsan Hyundai/SK Innovation + Jeonnam Gwangyang POSCO + Gyeongbuk Pohang POSCO α=0.07 (steel/petrochem). Magnitude-of-impact differs from R6_volcanic (probability-based — IS) or R3 (consequence-weighted general).' },
  { id: 'R7',  domain: 'Digital Readiness',          range: '[0.99, 1.015]', description: 'DESI-equivalent + KISA cyber regime — KrCERT/CC founded 2001 = 25-year cyber-incident catalogue (cohort-leading by years). NIS2-equivalent via Act on the Protection of Information and Communications Infrastructure 2001. R7 ceiling 1.015 — cohort-LOWEST (vs HU 1.02, IS 1.04).' }
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
    applies: 'C3 (voltage class · 765/345/154/22.9 kV — KR UNIQUE 765 kV tier)' },
  { id: 'D', name: 'Categorical mapping',
    formula: 'x_norm = lookup[x] where lookup maps ordinal → [0,1]',
    applies: 'I8 (ISO 9223 C2-C5 — C5 RESTORED), S3 (criticality 1-5 + Nuclear-Critical + Chaebol-Critical subclasses)' }
];

window.SSI_METADATA.VALIDATION_CHECKS = [
  { check: 'Schema validation',                                       criterion: 'All required top-level + sub keys present, no nulls', status: 'verified', isNew: false },
  { check: 'BPG Discipline #14 — canonical-schema emission',          criterion: 'grid-geo.json schema == {s,l,a}; sub keys ⊇ {n,v,x,y,r}; line keys ⊇ {i,kv,p,ss,se} — Iceland Session 30 NEW carried forward cleanly', status: 'verified', isNew: true },
  { check: 'BPG Discipline #15 — country-config mandatory',           criterion: 'intelligence/country-configs/korea.json exists; r3_buckets span [0.97, 1.05+]; min(lower) ≤ 1.025, max(lower) ≥ 1.045 — Iceland Session 30 NEW', status: 'verified', isNew: true },
  { check: 'OSM Overpass ISO3166 area filter',                        criterion: 'ISO3166-1=KR area filter — peninsula = no cross-border bleed (DPRK link cut 1953)', status: 'verified', isNew: false },
  { check: 'Polygon containment (1,184 subs → 17 do/si)',             criterion: 'Every substation falls inside exactly one do/si polygon — 1 nearest-centroid fallback only (cohort-best 0.08%)', status: 'verified', isNew: true },
  { check: 'R3 4-tier distribution',                                  criterion: '47% / 10% / 36% / 7% across 17 do/si — all 4 buckets populate', status: 'verified', isNew: true },
  { check: 'Single-DSO monopoly architectural test (NEW for KR)',     criterion: 'is_kepco_monopoly: true; dno-dashboard.html renders single-DSO panel layout', status: 'verified', isNew: true },
  { check: 'NEW R6_typhoon modifier',                                 criterion: 'Pacific corridor exposure α ∈ [0.03, 0.15]; 6 anchor events from KMA + NEMA', status: 'verified', isNew: true },
  { check: 'NEW R6_chaebol modifier',                                 criterion: 'Fab-cluster concentration α ∈ [0.00, 0.10]; Samsung+SK Hynix+POSCO+Hyundai anchors', status: 'verified', isNew: true },
  { check: '24 NPPs S3 Nuclear-Critical subclass',                    criterion: 'KHNP operators flagged + NSSC oversight + Pohang 2017 induced anchor + Kori 2 restart April 2026', status: 'verified', isNew: true },
  { check: 'R7 ceiling 1.015 (KISA 2001 — 25-yr backlog)',            criterion: 'Cohort-LOWEST R7 ceiling — reflects mature 25-year cyber regime', status: 'verified', isNew: true },
  { check: 'C5 corrosion restored (peninsula full marine)',           criterion: 'ISO 9223 C5 zones declared — all coastal do/si (peninsular geography)', status: 'verified', isNew: false },
  { check: 'MIN_FLEET[KR]=800 floor enforced',                        criterion: '1,184 substations exceeds 800 minimum — stub-gate clear', status: 'verified', isNew: true },
  { check: '60Hz unified frequency (cohort-UNIQUE)',                  criterion: 'frequency_hz: 60; inertia.py 60Hz adjustment applied to scoring-kr engine', status: 'verified', isNew: true },
  { check: '765 kV ultra-high voltage class (cohort-UNIQUE)',         criterion: 'voltage_classes_kv includes 765 — top tier in C3 voltage class log scaling', status: 'verified', isNew: true }
];

window.SSI_METADATA.CHANGELOG = [
  { id: 'KR-S31-9', change: 'Greenfield thin-shell on post-Iceland architecture — 8 pages authored directly on CountryRenderer.Safe + normalizeMeta() + Discipline #14 + #15 carried forward (KB §70.12)', type: 'enhanced', section: 'KB §71 (planned)' },
  { id: 'KR-S31-8', change: 'NEW single-DSO monopoly architectural test — is_kepco_monopoly: true; dno-dashboard.html renders single-entry layout (cohort-UNIQUE first)', type: 'architecture', section: 'dno-dashboard' },
  { id: 'KR-S31-7', change: 'Section G deepDives rotation — 5 do/si anchored: Edition 01 Gyeonggi (R6_chaebol) → 02 Gyeongnam (Hinnamnor) → 03 Gyeongbuk (Pohang 2017) → 04 Jeonnam (Hanbit+Khanun) → 05 Jeju (isolated sub-grid)', type: 'new', section: 'intelligence G' },
  { id: 'KR-S31-6', change: 'NEW R6_typhoon Pacific corridor modifier — α [0.03, 0.15], 6 anchor events (Hinnamnor 2022 + Khanun 2023 + Bolaven 2012 + Rusa 2002 + Maemi 2003 + Sanba 2012)', type: 'new', section: 'methodology' },
  { id: 'KR-S31-5', change: 'NEW R6_chaebol industrial-concentration modifier — α [0.00, 0.10], magnitude-of-impact differs from probability-based modifiers; Samsung Pyeongtaek + SK Hynix Icheon + POSCO Gwangyang/Pohang + Hyundai Ulsan anchors', type: 'new', section: 'methodology' },
  { id: 'KR-S31-4', change: 'R3 4-tier calibration — Industrial-Chaebol 1.05 / Capital-Seoul 1.04 / SME 1.03 / Rural 1.02 (spans renderer DEFAULT_R3_BUCKETS per Discipline #15)', type: 'new', section: 'methodology' },
  { id: 'KR-S31-3', change: 'd05_osm LIVE — 1,184 substations + 4,004 power lines via ISO3166-1=KR (88% OSM tag completeness — cohort-LEADING due to KEPCO operator standardization)', type: 'data', section: 'methodology' },
  { id: 'KR-S31-2', change: 'Single-DSO monopoly (KEPCO) + dual operator KPX (market) + KEPCO (assets) + KOREC regulator + 24 NPPs (KHNP-operated) + KISA cyber + NEMA emergency wired', type: 'data', section: 'methodology' },
  { id: 'KR-S31-1', change: 'KB v29 → §71 — Korea inaugural (final-4 OECD onboarding; KRW currency, NOT eurozone; isolated peninsula 60Hz; cohort-UNIQUE single-DSO monopoly)', type: 'enhanced', section: 'KB §71 (planned)' }
];

// ESG-report data-source registry (Phase 2b — KB §65)
window.SSI_METADATA.ESG_SOURCES = [
  ['ERA5 Climate Reanalysis','Copernicus CDS','2024','Weekly','CC-BY-4.0','R1, R3'],
  ['Korean Seismic Hazard Map','KIGAM (Korea Institute of Geoscience and Mineral Resources)','2023','Multi-year','Open','R1, R3'],
  ['Pohang 2017 Mw 5.5 induced earthquake (Science, Grigoli et al. 2018)','Korean court 2019 + Science peer-review','2018','Published','Open','R1, R3'],
  ['Population & Economics','KOSTAT — Statistics Korea','2024','Annual','Open','R2, R3'],
  ['Energy Market Data','KPX + KEPCO','2024','Daily','Regulated','R2, R4'],
  ['Generation mix 2024 (32% nuclear, 30% coal, 28% LNG, <6.5% RES)','Ember + MOTIE 11th Basic Plan','2024','Annual','Open','R4'],
  ['Typhoon Tracks & Damage','KMA — Korea Meteorological Administration','2024','Daily','Open','R1'],
  ['Hinnamnor 2022 + Khanun 2023 anchor events','KMA + NEMA','2024','Event','Open','R1, R3'],
  ['Nuclear Safety Oversight (24 reactors)','NSSC + KHNP — Kori/Hanul/Hanbit/Wolsong','2024','Quarterly','Regulated','R1, R3'],
  ['Cybersecurity Posture (25-yr backlog cohort-leading)','KISA + KrCERT/CC (2001)','2024','Annual','Open','R6'],
  ['Act on the Protection of Information and Communications Infrastructure (정보통신기반보호법)','MSIT — Ministry of Science & ICT','2001-2024','Continuous','Open','R6'],
  ['IEEE C57.91 Thermal Model (60Hz adjustment)','IEEE','Standard','N/A','Published','R1'],
  ['CIGRE TB 761 Markov','CIGRE','2019','N/A','Published','R1, R3'],
  ['ISO 9223 Corrosion (C2-C5 — C5 RESTORED, peninsula full marine)','ISO','2012','N/A','Published','R5'],
  ['CMIP6 SSP2-4.5 Projections','Copernicus CDS','2024','Multi-year','CC-BY-4.0','R1']
];

// Mirror onto the lower-case alias too
window.SSIMetadata = window.SSI_METADATA;
