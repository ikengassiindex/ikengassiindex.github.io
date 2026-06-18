// Slovenia SSI v4.0.2 metadata — KB §64 · post-§57 normalization
// Pattern C (Wave 6c) — NO IIFE wrapper · KB §58.6 Canada IIFE root-cause
// Dual-global alias per KB §45.6
// Edition 01 (inaugural) · first refresh 2026-07-09 (CEE-South cohort)

window.SSIMetadata = {
  country: 'Slovenia',
  country_code: 'SI',
  country_iso3: 'SVN',
  flag: '\u{1F1F8}\u{1F1EE}',  // 🇸🇮
  cohort: 'CEE-South-2026',
  edition: 'Edition 01',
  first_refresh: '2026-07-09',
  engine_version: '4.0.2',
  kb_version: 'v25',
  bpg_version: 'v1.24',
  labels: {
    country_en: 'Slovenia',
    country_local: 'Slovenija',
    capital: 'Ljubljana',
    capital_local: 'Ljubljana',
    region_unit: 'NUTS-3 statistical region',
    region_unit_local: 'statistična regija',
    tso: 'ELES (Elektro-Slovenija)',
    regulator: 'AGEN-RS (Agencija za energijo)',
    statistics_office: 'SURS (Statistični urad RS)',
    nem: 'Borzen / BSP SouthPool',
    bidding_zone: '10YSI-ELES-----O'
  },
  stats: { sources: 18, variables: 92, components: 6, modifiers: 5 },
  methodology: {
    formula: 'R = base − Σ component contributions × modifiers',
    components: ['C', 'V', 'I', 'E', 'S', 'T'],
    modifiers: ['R3_C_mult', 'R4_F_topo', 'R6_restoration', 'R6_seismic', 'R7_cyber'],
    mc_iterations: 10000,
    r3_tiers: '3-tier (Capital-Intensive / Industrial-Major / Light-Rural)',
    r6_anchors: '2023 Savinja floods (€10B) · 1998 Bovec M5.6 · 2014 ice storm · Krško NPP zone seismic',
    r7_ceiling: 1.04
  }
};

// ── Dual-global alias (KB §45.6) ──
window.SSI_METADATA = window.SSIMetadata;

// ── Post-declaration enrichment ──
window.SSI_METADATA.COMPONENTS = [
  { code: 'C', name: 'Continuity',     ceiling: 0.30, drivers: 'SAIDI/SAIFI · AGEN-RS quality reports · ELES network statement' },
  { code: 'V', name: 'Voltage Quality', ceiling: 0.18, drivers: 'EN 50160 events · DSO quarterly filings · 5 Elektro regions' },
  { code: 'I', name: 'Infrastructure', ceiling: 0.18, drivers: 'OSM topology · ELES asset register · 400/220/110 kV inventory' },
  { code: 'E', name: 'Economic',       ceiling: 0.14, drivers: 'SURS NUTS-3 GDP · BS regional accounts · business demography' },
  { code: 'S', name: 'Societal',       ceiling: 0.12, drivers: 'SURS energy-poverty · elderly share · vulnerable populations' },
  { code: 'T', name: 'Transition',     ceiling: 0.08, drivers: 'AGEN-RS DER registry · Borzen renewables · EV uptake' }
];

window.SSI_METADATA.DATA_SOURCES = [
  { id: 'd01_eles',        name: 'ELES — Elektro-Slovenija (TSO)',        freq: 'Daily',      status: 'live', vars: 14, feeds: 'C2,C3,I1,I2,I3,R4',      sources: 'eles.si network statement + ENTSO-E TP' },
  { id: 'd02_agen_rs',     name: 'AGEN-RS — Agencija za energijo',         freq: 'Annual',     status: 'live', vars: 12, feeds: 'C1,C2,V1,V2,T1',        sources: 'agen-rs.si quality-of-supply + tariff' },
  { id: 'd02b_dso',        name: '5 Elektro DSOs (Lj/Mb/Ce/Pr/Gr)',        freq: 'Quarterly',  status: 'live', vars: 18, feeds: 'C1,V1,V2,I2,I3',        sources: 'elektro-ljubljana / maribor / celje / primorska / gorenjska' },
  { id: 'd03_arso_seismic',name: 'ARSO + ZAG-EQS — Seismology',           freq: 'Continuous', status: 'live', vars: 4,  feeds: 'R6_seismic',            sources: 'arso.gov.si seismology + ZAG-EQS PGA 475-yr' },
  { id: 'd03b_drsv',       name: 'DRSV — Direkcija za vode (floods)',     freq: 'Monthly',    status: 'live', vars: 6,  feeds: 'R6c_flood',              sources: 'gov.si/drsv Q100 maps + 2023 floods overlay' },
  { id: 'd04_surs',        name: 'SURS — Statistični urad RS',             freq: 'Quarterly',  status: 'live', vars: 16, feeds: 'E1,E2,S1,S2,S3',        sources: 'surs.si NUTS-3 demographics + regional GDP' },
  { id: 'd04b_bs',         name: 'Banka Slovenije — central bank',        freq: 'Quarterly',  status: 'live', vars: 4,  feeds: 'E1,E2',                 sources: 'bsi.si national accounts + financial stability' },
  { id: 'd05_osm',         name: 'OSM Overpass — grid topology',          freq: 'Monthly',    status: 'live', vars: 8,  feeds: 'I1,I2,I3,R4',           sources: 'overpass-api.de power=substation/line · ISO3166 SI' },
  { id: 'd06_arso_met',    name: 'ARSO — Meteorology + climate',          freq: 'Continuous', status: 'live', vars: 5,  feeds: 'R6_storm,R5_corrosion', sources: 'arso.gov.si meteo + bora wind + ice storm' },
  { id: "CDS", name: "Copernicus CDS / ERA5-Land", url: "cds.climate.copernicus.eu", freq: "Annual", res: "0.1° (~11 km, ERA5-Land + daily-stats)", vars: 5, category: "Climate", feeds: "R2 Δ_climate (t_mean_c, heat_days, ice_days at 0.1° land grid)", registration: true },
  { id: 'd08_ursjv',       name: 'URSJV — Nuclear safety (Krško)',        freq: 'Quarterly',  status: 'live', vars: 3,  feeds: 'R6_seismic,I3',          sources: 'ursjv.gov.si Krško NPP oversight' },
  { id: 'd09_si_cert',     name: 'SI-CERT — National CERT (1995)',         freq: 'Continuous', status: 'live', vars: 5,  feeds: 'R7_cyber',               sources: 'cert.si incident database + NIS2 reporting' },
  { id: 'd10_entsoe',      name: 'ENTSO-E TYNDP + Transparency',           freq: 'Annual',     status: 'live', vars: 6,  feeds: 'I1,I2,T1',              sources: 'tyndp.entsoe.eu + transparency.entsoe.eu' },
  { id: 'd11_eurostat',    name: 'Eurostat — EU-27 benchmarks',            freq: 'Annual',     status: 'live', vars: 8,  feeds: 'E1,S1,T1',              sources: 'ec.europa.eu/eurostat NUTS-3 + energy' },
  { id: 'd12_nek_krsko',   name: 'NEK Krško — SI/HR joint operator',       freq: 'Quarterly',  status: 'live', vars: 4,  feeds: 'I1,I3,R6_seismic',       sources: 'nek.si annual + URSJV PSR (2043 life-extension)' },
  { id: 'd13_hse',         name: 'HSE — Hydro + lignite generation',       freq: 'Annual',     status: 'live', vars: 5,  feeds: 'I1,T1',                  sources: 'hse.si annual reports · Drava+Soča+Sava cascades + TEŠ-6' },
  { id: 'd14_gen_energija',name: 'GEN Energija — Krško 50% + Brestanica',  freq: 'Annual',     status: 'live', vars: 3,  feeds: 'I1,T1',                  sources: 'gen-energija.si annual + JEK 2 planning' },
  { id: 'd15_iea_oecd',    name: 'IEA + OECD — energy benchmarks',         freq: 'Annual',     status: 'live', vars: 6,  feeds: 'T1,E1',                  sources: 'iea.org + oecd.org energy statistics' },
    { id: "GEM", name: "GEM Global Seismic Hazard Map 2023.1", url: "globalquakemodel.org", freq: "Static", res: "0.05° (~5.5 km, rock-site PGA 475-yr)", vars: 1, category: "Hazard", feeds: "R6a seismic PGA, substation-level overlay (CC BY-NC-SA 4.0)" },
    { id: "Eurostat-NUTS3", name: "Eurostat NUTS-3 Regional Statistics", url: "ec.europa.eu/eurostat", freq: "Annual", res: "NUTS-3 (province / NUTS-2 unemployment)", vars: 5, category: "Socio-Econ", feeds: "R2 GDP/cap, unemp, elderly%, ep_rate, migration (CC BY 4.0)" },
];

window.SSI_METADATA.FREQ_DISTRIBUTION = {
  Weekly:    { count: 0,  sources: [] },
  Monthly:   { count: 3,  sources: ['OSM Overpass', 'DRSV (floods)', 'Copernicus ERA5/CMIP6'] },
  Quarterly: { count: 5,  sources: ['DSO filings (5 Elektros)', 'SURS', 'Banka Slovenije', 'URSJV (Krško)', 'NEK Krško'] },
  Annual:    { count: 7,  sources: ['AGEN-RS', 'ENTSO-E TYNDP', 'Eurostat', 'HSE', 'GEN Energija', 'IEA/OECD'] },
  Continuous:{ count: 3,  sources: ['ELES (TSO)', 'ARSO (seismic+met)', 'SI-CERT'] }
};

window.SSI_METADATA.DATA_LAYERS = [
  { id: 'tso',        name: 'ELES transmission (400/220/110 kV)', vars: 14, status: 'live', sources: 'ELES TP + ENTSO-E' },
  { id: 'dso',        name: '5 regional Elektro DSOs (35/20/10 kV)', vars: 18, status: 'live', sources: '5 Elektros + SODO holding' },
  { id: 'regulator',  name: 'AGEN-RS — quality + tariff',            vars: 12, status: 'live', sources: 'AGEN-RS annual reports' },
  { id: 'statistics', name: 'SURS — NUTS-3 socio-economic',           vars: 16, status: 'live', sources: 'SURS regional accounts' },
  { id: 'hazard',     name: 'Multi-hazard (seismic+flood+storm)',     vars: 15, status: 'live', sources: 'ARSO + ZAG-EQS + DRSV' },
  { id: 'cyber',      name: 'SI-CERT + URSIV',                        vars: 5,  status: 'live', sources: 'SI-CERT incidents + NIS2' },
  { id: 'topology',   name: 'OSM grid topology',                       vars: 8,  status: 'live', sources: 'OSM Overpass ISO3166 area' },
  { id: 'nuclear',    name: 'Krško NPP oversight',                     vars: 4,  status: 'live', sources: 'URSJV + NEK + GEN Energija' }
];

window.SSI_METADATA.REGIONS_NUTS3 = [
  { code: 'SI031', name: 'Pomurska',              capital: 'Murska Sobota',  tier: 'Light-Rural',        r3: 1.06 },
  { code: 'SI032', name: 'Podravska',             capital: 'Maribor',         tier: 'Industrial-Major',   r3: 1.04 },
  { code: 'SI033', name: 'Koroška',               capital: 'Slovenj Gradec',  tier: 'Light-Rural',        r3: 1.06 },
  { code: 'SI034', name: 'Savinjska',             capital: 'Celje',           tier: 'Industrial-Major',   r3: 1.04 },
  { code: 'SI035', name: 'Zasavska',              capital: 'Trbovlje',        tier: 'Light-Rural',        r3: 1.06 },
  { code: 'SI036', name: 'Posavska',              capital: 'Krško',           tier: 'Light-Rural',        r3: 1.06 },
  { code: 'SI037', name: 'Jugovzhodna Slovenija', capital: 'Novo mesto',      tier: 'Light-Rural',        r3: 1.06 },
  { code: 'SI038', name: 'Primorsko-notranjska',  capital: 'Postojna',        tier: 'Light-Rural',        r3: 1.06 },
  { code: 'SI041', name: 'Osrednjeslovenska',     capital: 'Ljubljana',       tier: 'Capital-Intensive',  r3: 1.02 },
  { code: 'SI042', name: 'Gorenjska',             capital: 'Kranj',           tier: 'Industrial-Major',   r3: 1.04 },
  { code: 'SI043', name: 'Goriška',               capital: 'Nova Gorica',     tier: 'Light-Rural',        r3: 1.06 },
  { code: 'SI044', name: 'Obalno-kraška',         capital: 'Koper',           tier: 'Industrial-Major',   r3: 1.04 }
];

window.SSI_METADATA.DSO_PANEL = [
  { name: 'Elektro Ljubljana',   region: 'Osrednjeslovenska + Gorenjska/Posavska/JV', share_pct: 33 },
  { name: 'Elektro Maribor',     region: 'Podravska + Pomurska + Koroška',            share_pct: 25 },
  { name: 'Elektro Celje',       region: 'Savinjska + Zasavska + Posavska',           share_pct: 20 },
  { name: 'Elektro Primorska',   region: 'Goriška + Obalno-kraška + Primorsko-notr.', share_pct: 14 },
  { name: 'Elektro Gorenjska',   region: 'Gorenjska (Kranj-Triglav)',                  share_pct: 8  }
];


// ── Extended metadata for methodology.html / data.html / intelligence.html C-section ──
// KB §58.6 compliant — no IIFE wrapper, dual-global alias preserved above.

window.SSI_METADATA.COMPONENTS = [
  { id: 'C', name: 'Continuity', weight: 0.30, color: '#941914', isNew: false,
    metrics: [
      { id: 'C1', name: 'SAIDI (planned + unplanned)',     intra: 0.30, global: 0.090, norm: 'P5/P95 inverse',  source: 'AGEN-RS 2024 — per-DSO quality reports' },
      { id: 'C2', name: 'SAIFI (interruption frequency)',   intra: 0.25, global: 0.075, norm: 'P5/P95 inverse',  source: 'AGEN-RS 2024 — per-DSO' },
      { id: 'C3', name: 'Voltage class (max kV)',           intra: 0.20, global: 0.060, norm: 'log-scaled',      source: 'OSM Overpass + ELES TP' },
      { id: 'C4', name: 'Customer count (catchment)',       intra: 0.15, global: 0.045, norm: 'P5/P95 inverse',  source: 'SODO + SURS' },
      { id: 'C5', name: 'CAIDI restoration speed',          intra: 0.10, global: 0.030, norm: 'P5/P95 inverse',  source: 'AGEN-RS 2024' }
    ]},
  { id: 'V', name: 'Voltage Quality', weight: 0.10, color: '#aa4234', isNew: false,
    metrics: [
      { id: 'V1', name: 'EN 50160 dip events',              intra: 0.40, global: 0.040, norm: 'count per 1000 cust/yr', source: 'AGEN-RS + 5 DSOs' },
      { id: 'V2', name: 'Voltage swell events',             intra: 0.30, global: 0.030, norm: 'count per 1000 cust/yr', source: 'AGEN-RS + 5 DSOs' },
      { id: 'V3', name: 'Harmonic distortion (THD)',        intra: 0.30, global: 0.030, norm: 'P95 of weekly THD',      source: 'AGEN-RS quarterly filings' }
    ]},
  { id: 'I', name: 'Infrastructure', weight: 0.25, color: '#5d8563', isNew: false,
    metrics: [
      { id: 'I1', name: 'Snow/Ice IRI',                    intra: 0.18, global: 0.045, norm: 'ERA5 reanalysis',  source: 'Copernicus ERA5 + ARSO', adaptive: true },
      { id: 'I2', name: 'Heat-wave IRI',                   intra: 0.16, global: 0.040, norm: 'GDD anomaly',       source: 'Copernicus + ARSO', adaptive: true },
      { id: 'I3', name: 'Wind storm IRI (bora)',           intra: 0.14, global: 0.035, norm: 'P99 m/s hourly',    source: 'ARSO + ERA5', adaptive: true },
      { id: 'I4', name: 'Asset age cohort',                intra: 0.14, global: 0.035, norm: 'Markov-weighted',   source: 'ELES + 5 DSOs annual reports' },
      { id: 'I5', name: 'Thermal stress (R6 proxy)',       intra: 0.10, global: 0.025, norm: 'IEEE C57.91',       source: 'IEEE C57.91 + Copernicus' },
      { id: 'I6', name: 'Substation density',              intra: 0.10, global: 0.025, norm: 'per km²',           source: 'OSM + SURS' },
      { id: 'I7', name: 'Network length per cap',          intra: 0.08, global: 0.020, norm: 'P5/P95',            source: 'ELES TP + 5 DSOs' },
      { id: 'I8', name: 'Coastal corrosion ISO 9223',      intra: 0.06, global: 0.015, norm: 'C1–C5 categorical', source: 'ARSO + ISO 9223 (Obalno-kraška)' },
      { id: 'I9', name: 'Hydrogeological exposure',        intra: 0.04, global: 0.010, norm: 'DRSV Q100 overlay', source: 'DRSV + ARSO' }
    ]},
  { id: 'E', name: 'Economic', weight: 0.10, color: '#3b9eff', isNew: false,
    metrics: [
      { id: 'E1', name: 'Regulatory penalty exposure',     intra: 0.60, global: 0.060, norm: 'EUR per SAIDI min',  source: 'AGEN-RS tariff' },
      { id: 'E2', name: 'Productivity loss (VoLL)',        intra: 0.40, global: 0.040, norm: 'EUR/kWh',            source: 'ACER 2023 + SURS sector mix' }
    ]},
  { id: 'S', name: 'Saturation', weight: 0.20, color: '#b8863a', isNew: false,
    metrics: [
      { id: 'S1', name: 'Regional KPI — saturation',       intra: 0.45, global: 0.090, norm: 'load/capacity %',   source: 'ELES + 5 DSOs' },
      { id: 'S2', name: 'Reverse power flow',              intra: 0.35, global: 0.070, norm: 'hours/yr reverse',   source: 'ELES + ENTSO-E' },
      { id: 'S3', name: 'Criticality class',               intra: 0.20, global: 0.040, norm: 'categorical 1-5',    source: 'ELES Network Statement' }
    ]},
  { id: 'T', name: 'Transition', weight: 0.05, color: '#22d3ee', isNew: true,
    metrics: [
      { id: 'T1', name: 'DER Stress Index',                intra: 1.00, global: 0.050, norm: 'composite',          source: 'Borzen + AGEN-RS DER registry', isNew: true }
    ]}
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
  { check: 'Schema validation',                       criterion: 'All required top-level + sub keys present, no nulls',         status: 'verified', isNew: false },
  { check: 'OSM Overpass boundary filter',            criterion: 'ISO3166-1=SI area filter — zero AT/IT/HR/HU contamination',   status: 'verified', isNew: false },
  { check: 'Polygon containment (158 subs → 12 NUTS-3 regions)', criterion: 'Every sub falls inside exactly one NUTS-3 polygon', status: 'verified', isNew: true },
  { check: 'R3 tier distribution (3-tier)',           criterion: 'Capital 1 · Industrial 4 · Light-Rural 7 — all populated',     status: 'verified', isNew: true },
  { check: 'R6 multi-hazard coverage',                criterion: 'Seismic + flood + storm + restoration all active',             status: 'verified', isNew: true },
  { check: 'R6c flood — 2023 Savinja anchor',         criterion: 'Savinjska + Pomurska + Podravska + Osrednjeslovenska HIGH',    status: 'verified', isNew: true },
  { check: 'R7 ceiling 1.04 (DESI 2024 ~0.55)',       criterion: 'SI-CERT mature (est. 1995) + NIS2 transposed Q4 2024',         status: 'verified', isNew: false },
  { check: 'Krško NPP zone seismic α [0.04, 0.14]',   criterion: 'Posavska seismic + URSJV oversight + NEK reports',             status: 'verified', isNew: true },
  { check: 'Cross-page schema compatibility (FR template)', criterion: 'grid-geo.json + ssi-data.json match France schema',       status: 'verified', isNew: false }
];

window.SSI_METADATA.CHANGELOG = [
  { id: 'SI-S25-9', change: 'France-parity rebuild — 8 pages rewritten to match FR structure verbatim',                  type: 'enhanced', section: 'KB §64' },
  { id: 'SI-S25-8', change: 'Section G deepDives — 12 NUTS-3 Slovenian regions (Savinjska + 11)',                         type: 'new',      section: 'intelligence G' },
  { id: 'SI-S25-7', change: 'Edition patcher anchored at FIRST_REFRESH 2026-07-09 (KB §58.6 padStart(2) + d>=21)',        type: 'enhanced', section: 'intelligence' },
  { id: 'SI-S25-6', change: 'ESG report — slovenia entry in COUNTRY_SOURCES (14 references)',                             type: 'new',      section: 'esg-report' },
  { id: 'SI-S25-5', change: 'Methodology metadata extension — COMPONENTS/NORM/VALIDATION/CHANGELOG (FR parity)',          type: 'new',      section: 'metadata' },
  { id: 'SI-S25-4', change: 'R6 modifier set — seismic (Posavska/Goriška/Obalno-kraška) + flood (2023 Savinja anchor)',  type: 'new',      section: 'methodology' },
  { id: 'SI-S25-3', change: 'd05_osm LIVE — 158 substations via ISO3166-1=SI area filter',                                type: 'data',     section: 'methodology' },
  { id: 'SI-S25-2', change: '5 Elektro DSOs + ELES TSO + AGEN-RS regulator + URSJV nuclear safety wired',                 type: 'data',     section: 'methodology' },
  { id: 'SI-S25-1', change: 'KB v25 §64 — Slovenia inaugural onboarding (CEE-South cohort)',                              type: 'enhanced', section: 'KB §64' }
];

// ── ESG-report data-source registry (Phase 2b — KB §65) ──
// Row form: [name, source, vintage, frequency, license, reports_tag, blocked_flag?]
// Consumed by esg-sections.js → getReportSources() to render the
// "Data Sources & Vintage" card on each of the 6 ESG reports. Kept separate
// from DATA_SOURCES above (which is object-form, consumed by data.html).
window.SSI_METADATA.ESG_SOURCES = [
  ['ERA5 Climate Reanalysis','Copernicus CDS','2024','Weekly','CC-BY-4.0','R1, R3'],
  ['Slovenian Seismic Hazard Map','ARSO Seismology + ZAG-EQS (PGA 475-yr)','2023','Multi-year','CC0','R1, R3'],
  ['Population & Economics','SURS (Statistični urad RS)','2023','Annual','OGD','R2, R3'],
  ['Energy Market Data','ELES + Borzen','2023','Annual','Regulated','R2, R4'],
  ['Renewable Installations','Borzen + AGEN-RS DER registry','2024','Monthly','Open','R4'],
  ['Weather Data','ARSO (Agencija RS za okolje)','2024','Daily','CC-BY-4.0','R1'],
  ['Flood Mapping','DRSV (Direkcija za vode) Q100 + 2023 floods overlay','2024','Monthly','CC-BY-4.0','R1'],
  ['Nuclear Safety','URSJV — Krško NPP oversight','2024','Quarterly','Regulated','R1, R3'],
  ['Cybersecurity Index','SI-CERT + ENISA','2024','Annual','Open','R6'],
  ['DESI Connectivity','European Commission','2024','Annual','Open','R6'],
  ['IEEE C57.91 Thermal Model','IEEE','Standard','N/A','Published','R1'],
  ['CIGRE TB 761 Markov','CIGRE','2019','N/A','Published','R1, R3'],
  ['ISO 9223 Corrosion','ISO','2012','N/A','Published','R5'],
  ['CMIP6 SSP2-4.5 Projections','Copernicus CDS','2024','Multi-year','CC-BY-4.0','R1']
];

// Mirror onto the lower-case alias too
window.SSIMetadata = window.SSI_METADATA;
