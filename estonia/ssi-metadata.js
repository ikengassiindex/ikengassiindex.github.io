// ssi-metadata.js — Estonia (#29, OECD #28) — Session 15
// Edition 01 · FIRST_REFRESH 2026-07-09

window.SSI_METADATA = {
  iso2: 'EE', iso3: 'EST', folder: 'estonia',
  name_en: 'Estonia', name_local: 'Eesti',
  flag: '🇪🇪',
  country_number: 29, oecd_number: 28,
  edition: 'Edition 01', first_refresh: '2026-07-09', next_refresh: '2026-08-13',
  session: 'Session 15',
  TSO: 'Elering AS', regulator: 'Konkurentsiamet (Estonian Competition Authority)',
  market_operator: 'Nord Pool EE bidding zone (10Y1001A1001A39I)',
  synchronous_area: 'Continental European synchronous area (post-Feb-2025 BRELL desync via LitPol Link + Harmony Link)',
  bbox: { lon_min: 21.8, lon_max: 28.2, lat_min: 57.5, lat_max: 59.7 },
  admin_levels: { L1: { count: 15, label: 'Maakond' }, L2: { count: 79, label: 'Omavalitsus' } },

  stats: { sources: 28, variables: 95, components: 6, modifiers: 6, substations: 614, maakond: 15,
           fleet_median_R: 0.439, Critical: 13, High: 89, Medium: 276, Low: 236 },

  R3_calibration: { thresholds: { Capital_Intensive: 1.02, Industrial: 1.04, Commercial: 1.06, Light_Rural: 1.08 }},
  R6b_seismic: { alpha_band: [0.00, 0.02] }, R6c_flood: { active: false },
  R7_cyber: { ceiling: 1.05, desi_2024: 0.82 },
  Markov_handling: { confidence_tier: 'medium', review_date: '2030-02-08' },

  // ── COMPONENTS (each with metrics[]) ──
  COMPONENTS: [
    { id: 'C', name: 'Continuity', weight: 0.20, color: '#941914', isNew: false,
      metrics: [
        { id: 'C1', name: 'SAIDI (planned + unplanned)',     intra: 0.30, global: 0.060, norm: 'P5/P95 inverse',  source: 'Konkurentsiamet 2024 — per-DSO' },
        { id: 'C2', name: 'SAIFI (interruption frequency)',   intra: 0.25, global: 0.050, norm: 'P5/P95 inverse',  source: 'Konkurentsiamet 2024 — per-DSO' },
        { id: 'C3', name: 'Voltage class (max kV)',           intra: 0.20, global: 0.040, norm: 'log-scaled',      source: 'OSM Overpass + Elering' },
        { id: 'C4', name: 'Customer count (catchment)',       intra: 0.15, global: 0.030, norm: 'P5/P95 inverse',  source: 'Elektrilevi + Statistikaamet' },
        { id: 'C5', name: 'Restoration speed (CAIDI)',        intra: 0.10, global: 0.020, norm: 'P5/P95 inverse',  source: 'Konkurentsiamet 2024' },
      ]},
    { id: 'V', name: 'Voltage Quality', weight: 0.20, color: '#aa4234', isNew: false,
      metrics: [
        { id: 'V1', name: 'Snow/Ice IRI',          intra: 0.20, global: 0.040, norm: 'ERA5 reanalysis',          source: 'Copernicus ERA5 2024', adaptive: true },
        { id: 'V2', name: 'Tree-fall IRI',          intra: 0.15, global: 0.030, norm: 'forest-cover + wind',     source: 'Copernicus + KAUR 2024', adaptive: true },
        { id: 'V3', name: 'Heat-wave IRI',          intra: 0.15, global: 0.030, norm: 'GDD anomaly',              source: 'Copernicus ERA5 + RIH', adaptive: true },
        { id: 'V4', name: 'Precipitation extremes', intra: 0.15, global: 0.030, norm: 'P95 of daily mm',         source: 'Riigi Ilmateenistus 2024' },
        { id: 'V5', name: 'Wind speed max',          intra: 0.15, global: 0.030, norm: 'P99 hourly m/s',           source: 'Riigi Ilmateenistus + ERA5' },
        { id: 'V6', name: 'Flood-zone overlay',     intra: 0.10, global: 0.020, norm: 'inactive for Estonia',     source: 'Maa-amet (R6c inactive)' },
        { id: 'V7', name: 'Coastal salt-spray',      intra: 0.10, global: 0.020, norm: 'distance-to-coast',         source: 'Maa-amet + ISO 9223' },
      ]},
    { id: 'I', name: 'Infrastructure', weight: 0.20, color: '#b8863a', isNew: false,
      metrics: [
        { id: 'I1', name: 'Network length per cap', intra: 0.20, global: 0.040, norm: 'P5/P95',  source: 'Elering 2024' },
        { id: 'I2', name: 'Substation density',      intra: 0.20, global: 0.040, norm: 'per km²',  source: 'OSM + Statistikaamet' },
        { id: 'I3', name: 'Asset age cohort',         intra: 0.20, global: 0.040, norm: 'Markov-weighted', source: 'Elering Annual Report' },
        { id: 'I4', name: 'Corrosion class ISO 9223', intra: 0.15, global: 0.030, norm: 'C1-C5 categorical', source: 'Maa-amet + ISO 9223' },
        { id: 'I5', name: 'Thermal stress (R6 proxy)', intra: 0.15, global: 0.030, norm: 'corrosion-derived', source: 'IEEE C57.91' },
        { id: 'I6', name: 'Smart-meter penetration',  intra: 0.10, global: 0.020, norm: 'pct of customers',   source: 'Elektrilevi 2024 (99.9%)' },
      ]},
    { id: 'E', name: 'Economic', weight: 0.15, color: '#5d8563', isNew: false,
      metrics: [
        { id: 'E1', name: 'GDP per capita (NUTS-3)', intra: 0.30, global: 0.045, norm: 'P5/P95 inverse', source: 'Eurostat 2024' },
        { id: 'E2', name: 'Energy poverty rate',      intra: 0.25, global: 0.0375, norm: 'EU-SILC pct',   source: 'Eurostat EU-SILC (EE)' },
        { id: 'E3', name: 'Unemployment rate',         intra: 0.15, global: 0.0225, norm: 'P5/P95',         source: 'Statistikaamet 2024' },
        { id: 'E4', name: 'R&D intensity (% GDP)',    intra: 0.15, global: 0.0225, norm: 'P5/P95 inverse', source: 'Eurostat NUTS-3 2024' },
        { id: 'E5', name: 'Elderly share (65+)',       intra: 0.15, global: 0.0225, norm: 'demographic',   source: 'Statistikaamet 2024' },
      ]},
    { id: 'S', name: 'Seismic', weight: 0.10, color: '#3b9eff', isNew: false,
      metrics: [
        { id: 'S1', name: 'PGA 475-yr return (g)', intra: 0.50, global: 0.050, norm: 'EFEHR ESHM20',     source: 'EFEHR 2024 (EE aseismic)' },
        { id: 'S2', name: 'Seismic zone (1-5)',      intra: 0.30, global: 0.030, norm: 'categorical 1-5',  source: 'EFEHR ESHM20' },
        { id: 'S3', name: 'Structural age multiplier', intra: 0.20, global: 0.020, norm: 'cohort-weighted', source: 'Elering + IEEE C57.91' },
      ]},
    { id: 'T', name: 'Transition', weight: 0.15, color: '#22d3ee', isNew: true,
      metrics: [
        { id: 'T1', name: 'Transition stress score', intra: 0.25, global: 0.0375, norm: 'composite',         source: 'Eesti Energia phase-out 2024', isNew: true },
        { id: 'T2', name: 'DER ratio (RES/load)',     intra: 0.20, global: 0.030, norm: 'pct',                source: 'Elering RES register 2024' },
        { id: 'T3', name: 'DER variability',           intra: 0.15, global: 0.0225, norm: 'CoV hourly',        source: 'Nord Pool EE 2024' },
        { id: 'T4', name: 'EV load ratio',              intra: 0.15, global: 0.0225, norm: 'pct of total load', source: 'Elering 2024' },
        { id: 'T5', name: 'Topology centrality (BC)',  intra: 0.15, global: 0.0225, norm: 'graph BC pct',      source: 'OSM topology graph' },
        { id: 'T6', name: 'EU-ETS emissions intensity', intra: 0.10, global: 0.015, norm: 'inverse',             source: 'Keskkonnaamet 2024' },
      ]},
  ],

  // ── NORM_METHODS (each with id + formula + applies) ──
  NORM_METHODS: [
    { id: 'NM1', name: 'P5/P95 percentile clip + linear remap', formula: 'x_norm = (clip(x, P5, P95) - P5) / (P95 - P5)',
      applies: 'C1-C5, V4-V5, I1-I2, E1-E3' },
    { id: 'NM2', name: 'Log-scaled voltage', formula: 'C3 = log10(v_kV / v_max) * 0.5 + 0.5',
      applies: 'C3 (voltage class)' },
    { id: 'NM3', name: 'Markov 5-state degradation', formula: 'R_t+1 = T_blended * R_t  (T = 0.30*T_pre + 0.70*T_post)',
      applies: 'R6 priors (KB §46.3 BRELL regime change)' },
    { id: 'NM4', name: 'Monte Carlo CI', formula: 'R_P5, R_P95 from 20,000 Gaussian-noise samples per substation',
      applies: 'All component composites' },
    { id: 'NM5', name: 'Sobol first-order sensitivity', formula: 'S_i = Var[E(R | X_i)] / Var(R)  (4,096 quasi-random samples)',
      applies: 'Modifier importance ranking' },
  ],

  // ── VALIDATION_CHECKS (each with check + criterion + status) ──
  VALIDATION_CHECKS: [
    { check: 'Schema validation',                    criterion: 'All required top-level + sub keys present, no nulls',         status: 'verified', isNew: false },
    { check: 'KB §38 small-country filter',          criterion: 'OSM raw 1,949 → 614 substantive after pole-top/MV-low drop',  status: 'verified', isNew: false },
    { check: 'KB §44 boundary enforcement',          criterion: 'Overpass ISO3166-1=EE area filter — zero LV/RU/FI contamination', status: 'verified', isNew: false },
    { check: 'Polygon containment (615 subs → 15 maakond)', criterion: 'Every sub falls inside exactly one geoBoundaries ADM1 polygon', status: 'verified', isNew: false },
    { check: 'Markov confidence tier review',         criterion: 'Medium tier until 2030-02-08 (5-yr post-BRELL desync)',       status: 'expected', isNew: true },
    { check: 'R3 tier distribution balance',           criterion: 'Capital 16% / Industrial 7% / Commercial 27% / Light-Rural 49% — all populated', status: 'verified', isNew: true },
    { check: 'Cross-page schema compatibility (FR template)', criterion: 'grid-geo.json s as obj + l with [lon,lat] + a adjacency match France',     status: 'verified', isNew: true },
  ],

  // ── DATA_LAYERS (each with id + name + vars + status + isNew + sources) ──
  DATA_LAYERS: [
    { id: 'A', name: 'Continuity (C)',                vars: 12, status: 'LIVE', isNew: false, sources: 'Elektrilevi, Konkurentsiamet, Elering' },
    { id: 'B', name: 'Voltage Quality (V)',            vars: 18, status: 'LIVE', isNew: false, sources: 'Copernicus ERA5, RIH, EFEHR, Maa-amet' },
    { id: 'C', name: 'Infrastructure (I)',              vars: 15, status: 'LIVE', isNew: false, sources: 'OSM Overpass, Elering, ISO 9223' },
    { id: 'D', name: 'Economic (E)',                     vars: 11, status: 'LIVE', isNew: false, sources: 'Eurostat NUTS-3, Statistikaamet, EU-SILC' },
    { id: 'E', name: 'Seismic (S)',                       vars:  8, status: 'LIVE', isNew: false, sources: 'EFEHR ESHM20' },
    { id: 'F', name: 'Transition (T)',                    vars: 14, status: 'NEW v4.0', isNew: true,  sources: 'Eesti Energia, Elering RES, Nord Pool, Keskkonnaamet' },
    { id: 'G', name: 'R3 economic tier',                  vars:  6, status: 'LIVE', isNew: false, sources: 'Eurostat + Statistikaamet' },
    { id: 'H', name: 'R6 Markov (medium-tier, post-BRELL)', vars: 11, status: 'NEW v4.0', isNew: true,  sources: 'd09_brell_legacy, IEEE C57.91, CIGRE TB 761' },
  ],

  // ── DATA_SOURCES (each with name + category + freq + res + vars + feeds + registration) ──
  DATA_SOURCES: [
    { name: 'Elering AS',                            category: 'TSO',         freq: 'Annual + 15-min', res: 'TSO-wide',  vars: 18, feeds: 'R2, R4, F1, T1',            registration: '' },
    { name: 'Konkurentsiamet',                       category: 'Regulator',   freq: 'Annual',          res: 'Per-DSO',   vars: 12, feeds: 'R2, R4 (quality + tariff)', registration: '' },
    { name: 'Elektrilevi OÜ',                        category: 'DSO',         freq: 'Annual',          res: 'Maakond',   vars: 15, feeds: 'R2, R4, T1',                 registration: '' },
    { name: 'Statistikaamet (Statistics Estonia)',    category: 'Stats',       freq: 'Annual + Q',      res: 'NUTS-3',    vars: 22, feeds: 'R3, E2, P',                 registration: '' },
    { name: 'Eesti Pank',                             category: 'Central bank',freq: 'Annual',          res: 'National',  vars:  8, feeds: 'R3 macro',                   registration: '' },
    { name: 'Riigi Ilmateenistus (RIH)',              category: 'Met service', freq: 'Daily + 30y',     res: 'Stations',  vars: 14, feeds: 'I1-I3, R5',                  registration: '' },
    { name: 'Maa-amet (Estonian Land Board)',         category: 'GIS',         freq: 'Biennial',        res: 'Maakond',   vars:  6, feeds: 'R6c (inactive for EE)',      registration: '' },
    { name: 'Keskkonnaagentuur (KAUR)',               category: 'Climate',     freq: 'Biennial',        res: 'National',  vars:  5, feeds: 'R2 climate trajectory',      registration: '' },
    { name: 'EFEHR ESHM20',                            category: 'Hazard',      freq: '5-yr update',     res: 'Pan-EU',    vars:  4, feeds: 'R6b (α [0.00, 0.02])',       registration: '' },
    { name: 'DESI 2024',                                category: 'Cyber',       freq: 'Annual',          res: 'National',  vars:  3, feeds: 'R7 (EE = 0.82)',             registration: '' },
    { name: 'Eurostat NUTS-3',                          category: 'Stats',       freq: 'Annual',          res: 'NUTS-3',    vars: 18, feeds: 'R3, E2',                     registration: '' },
    { name: 'ENTSO-E Transparency',                    category: 'Grid market', freq: 'Hourly',          res: 'Zone',      vars: 14, feeds: 'R2, R4, cross-border',       registration: 'Free' },
    { name: 'Nord Pool EE bidding zone',               category: 'Market',      freq: 'Hourly',          res: 'EE zone',   vars:  9, feeds: 'R3 prices',                   registration: '' },
    { name: 'Copernicus ERA5',                          category: 'Climate',     freq: 'Weekly',          res: '0.25°',     vars: 12, feeds: 'I1-I3, R5',                  registration: '' },
    { name: 'OpenStreetMap Overpass',                  category: 'Topology',    freq: 'Continuous',      res: 'Per sub',   vars:  8, feeds: 'F1, T topology',             registration: '' },
    { name: 'd09_brell_legacy (regime_change_2025_02)', category: 'Frequency',  freq: 'Annual',          res: 'Sync area', vars:  6, feeds: 'R6 Markov priors',           registration: '' },
    { name: 'Keskkonnaamet EU-ETS',                    category: 'Emissions',   freq: 'Annual',          res: 'Per plant', vars:  4, feeds: 'T1 transition',              registration: '' },
    { name: 'ENISA cyber index',                        category: 'Cyber',       freq: 'Annual',          res: 'National',  vars:  3, feeds: 'R7',                         registration: '' },
    { name: 'IEEE C57.91 + CIGRE TB 761',               category: 'Standards',   freq: 'Static',          res: 'Eq. class', vars:  2, feeds: 'Markov priors',              registration: '' },
    { name: 'd08_nordpool shared module',               category: 'Market',      freq: 'Hourly',          res: 'Baltic',    vars:  5, feeds: 'R3 Baltic cohort',           registration: '' },
    { name: 'Tartu Univ. / Genome Center',              category: 'R&D',         freq: 'Annual',          res: 'Tartu',     vars:  3, feeds: 'T innovation',               registration: '' },
    { name: 'EU Just Transition Fund',                  category: 'Policy',      freq: 'Multi-yr',        res: 'Ida-Viru',  vars:  4, feeds: 'T transition narrative',     registration: '' },
    { name: 'CEER Benchmarking 2024',                   category: 'Peer',        freq: 'Annual',          res: 'National',  vars:  5, feeds: 'SAIDI peer comparison',      registration: '' },
    { name: 'TalTech',                                    category: 'R&D',         freq: 'Annual',          res: 'Harju',      vars:  2, feeds: 'T innovation',               registration: '' },
    { name: 'Tartu Observatory',                          category: 'Climate',     freq: 'Annual',          res: 'National',  vars:  3, feeds: 'I5 thermal',                  registration: '' },
    { name: 'EstLink HVDC',                                category: 'Cross-bd',    freq: 'Hourly',          res: 'EE-FI',     vars:  4, feeds: 'R4 cross-border',            registration: '' },
    { name: 'LitPol Link HVDC',                            category: 'Cross-bd',    freq: 'Hourly',          res: 'LT-PL',     vars:  4, feeds: 'R4 cross-border',            registration: '' },
    { name: 'Eesti Energia phase-out tracker',              category: 'Transition',  freq: 'Quarterly',       res: 'Ida-Viru',  vars:  5, feeds: 'T1 transition',              registration: '' },
  ],

  FREQ_DISTRIBUTION: {
    Weekly: { sources: ['Copernicus ERA5','RIH'], count: 2 },
    Monthly: { sources: ['ENTSO-E','Nord Pool EE'], count: 2 },
    Quarterly: { sources: ['DESI','Maa-amet','Eesti Energia transition'], count: 3 },
    Annual: { sources: ['Elering','Konkurentsiamet','Elektrilevi','Statistikaamet','Eesti Pank','KAUR','Keskkonnaamet','EFEHR'], count: 8 },
  },

  // ── CHANGELOG (each with id + change + type) ──
  CHANGELOG: [
    { id: 'EE-S15-9', change: 'Hotfix #3 — R3 Light/Rural tier distinct (1.08, was collapsing to Commercial 1.06)',  type: 'new' },
    { id: 'EE-S15-8', change: 'Hotfix #2 — substation socio_economic (GDP/cap, R&D, unemployment) + regions median_R alias', type: 'data' },
    { id: 'EE-S15-7', change: 'Hotfix #1 — grid-geo.json to FR-compatible schema + landing path active (red)',         type: 'new' },
    { id: 'EE-S15-6', change: 'Wave D — 5-commit deploy to ikengassiindex.github.io/estonia/',                          type: 'new' },
    { id: 'EE-S15-5', change: 'Wave C — 8 HTML pages + ssi-metadata.js + grid-geo.json + bounds.json (geoBoundaries ADM1)', type: 'new' },
    { id: 'EE-S15-4', change: 'Wave B — scoring-ee engine: Markov (medium tier) + MC + Sobol + 614-sub R-distribution', type: 'new' },
    { id: 'EE-S15-3', change: 'Wave A — digital-twin-ee + 12 modules incl. d08_nordpool + d09_brell_legacy (NEW shared)', type: 'data' },
    { id: 'EE-S15-2', change: 'd05_osm LIVE — 1,949 raw → 614 substantive via KB §38 small-country filter (31.5% retention)', type: 'data' },
    { id: 'EE-S15-1', change: 'KB v12 → v13 + BPG v1.11 → v1.12 — Part XIV Baltic Onboarding Roadmap',                  type: 'enhanced' },
  ],
};

// KB §45.6 dual-global alias — DO NOT REMOVE
window.SSIMetadata = window.SSI_METADATA;
