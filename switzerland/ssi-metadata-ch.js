/* ═══════════════════════════════════════════════════════════
   SSI v4.0.2 — Metadata Registry (Switzerland)
   95 variables · 25 sources · 20 metrics · 6 components · 5 modifiers
   Complete reference data for methodology page + data page
   ═══════════════════════════════════════════════════════════ */

window.SSIMetadata = (function () {
  'use strict';

  // ─── 25 Verified Data Sources ─────────────────────────────
  const DATA_SOURCES = [
    { id: 'BFE',    name: 'BFE (Swiss Federal Office of Energy)',  url: 'bfe.admin.ch',                         freq: 'Annual',    res: 'Canton',          vars: 6,  category: 'Grid',          feeds: 'C1–C4 (SAIDI/SAIFI), energy consumption, grid investment' },
    { id: 'ELCOM',  name: 'ElCom (Electricity Commission)',        url: 'elcom.admin.ch',                       freq: 'Annual',    res: 'Canton',          vars: 5,  category: 'Grid',          feeds: 'Quality regulation, tariffs, reliability statistics, CAIDI' },
    { id: 'SWGRID', name: 'Swissgrid',                             url: 'swissgrid.ch',                         freq: 'Monthly',   res: 'TSO zone',        vars: 3,  category: 'Grid',          feeds: 'Transmission capacity, cross-border flows, ancillary services' },
    { id: 'PRON',   name: 'Pronovo',                               url: 'pronovo.ch',                           freq: 'Monthly',   res: 'Canton',          vars: 4,  category: 'Transition',    feeds: 'T1 DER capacity, renewable generation registry, solar/wind' },
    { id: 'BFS',    name: 'BFS (Federal Statistical Office)',      url: 'bfs.admin.ch',                         freq: 'Annual',    res: 'Bezirk',          vars: 8,  category: 'Socio-Econ',    feeds: 'R3 population, elderly, GDP, fiscal capacity, demographics' },
    { id: 'SED',    name: 'SED (Swiss Seismological Service)',     url: 'seismo.ethz.ch',                       freq: 'Static',    res: '~5 km',           vars: 2,  category: 'Hazard',        feeds: 'R6b seismic hazard (475-yr PGA), zone classification' },
    { id: 'BAFU',   name: 'BAFU (Federal Office for Environment)',  url: 'bafu.admin.ch',                       freq: 'Annual',    res: 'Canton / station', vars: 4,  category: 'Environment',   feeds: 'I8 air quality, PM2.5, NO₂, O₃ corrosion, flood zones' },
    { id: 'STOPO',  name: 'Swisstopo',                             url: 'swisstopo.admin.ch',                   freq: 'Static',    res: 'Bezirk',          vars: 2,  category: 'Infrastructure',feeds: 'Terrain elevation, Alpine topography classification' },
    { id: 'SNB',    name: 'SNB (Swiss National Bank)',             url: 'snb.ch',                               freq: 'Quarterly', res: 'National',        vars: 2,  category: 'Economic',      feeds: 'Economic indicators, exchange rates, financial stability' },
    { id: 'SECO',   name: 'SECO (State Secretariat for Economy)', url: 'seco.admin.ch',                        freq: 'Annual',    res: 'Canton',          vars: 3,  category: 'Socio-Econ',    feeds: 'Unemployment, GDP per capita, economic structure' },
    { id: 'METEO',  name: 'MeteoSwiss',                            url: 'meteoswiss.admin.ch',                  freq: 'Daily',     res: '~1 km',           vars: 3,  category: 'Climate',       feeds: 'I1–I3 snow/ice, storms, heat-wave events' },
    { id: 'ASTRA',  name: 'ASTRA (Federal Roads Office)',          url: 'astra.admin.ch',                       freq: 'Annual',    res: 'Canton',          vars: 1,  category: 'Infrastructure',feeds: 'Transport infrastructure, EV charging network' },
    { id: 'OSM',    name: 'OSM Power Infrastructure',              url: 'overpass-api.de',                      freq: 'Weekly',    res: 'Node/edge',       vars: 3,  category: 'Infrastructure',feeds: 'R4 graph topology, BC, bridges · 947 substations' },
    { id: 'D10',    name: 'Copernicus CDS / ERA5',                 url: 'cds.climate.copernicus.eu',            freq: 'Static',    res: '0.25° (~25 km)',  vars: 4,  category: 'Climate',       feeds: 'R2 Δ_climate (I1–I3 trajectory)', registration: true },
    { id: 'ENTSE',  name: 'ENTSO-E Transparency',                  url: 'transparency.entsoe.eu',               freq: 'Hourly',    res: 'Bidding zone',    vars: 2,  category: 'Transition',    feeds: 'T1 DER variability, cross-border flows', registration: true },
    { id: 'EEA',    name: 'EEA Air Quality e-Reporting',           url: 'eea.europa.eu',                        freq: 'Annual',    res: '~1 km + station', vars: 3,  category: 'Environment',   feeds: 'I8 PM2.5, NO₂, O₃ corrosion' },
    { id: 'EURO',   name: 'Eurostat Energy Statistics',             url: 'ec.europa.eu/eurostat',                freq: 'Annual',    res: 'NUTS2',           vars: 3,  category: 'Economic',      feeds: 'Energy poverty cross-validation' },
    { id: 'DESI',   name: 'DESI Digital Economy Index',             url: 'digital-strategy.ec.europa.eu',        freq: 'Annual',    res: 'EU Regional',     vars: 2,  category: 'Socio-Econ',    feeds: 'R7 Bezirk-level cyber-exposure (primary DESI input)' },
    { id: 'D-OM',   name: 'Open-Meteo / ERA5',                     url: 'open-meteo.com',                       freq: 'Hourly',    res: '~1 km',           vars: 1,  category: 'Climate',       feeds: 'I5 ambient temperature proxy' },
    { id: 'IEEE-1', name: 'IEEE C57.91 / IEC 60076',               url: 'standards.ieee.org',                   freq: 'Static',    res: 'Asset-level',     vars: 16, category: 'Standards',     feeds: 'I5 thermal model, B.3 Markov states' },
    { id: 'JRC',    name: 'JRC DSO Observatory',                   url: 'ses.jrc.ec.europa.eu',                 freq: 'Annual',    res: 'DSO-level',       vars: 2,  category: 'Grid',          feeds: 'R7 Bezirk-level cyber-exposure (secondary)' },
    { id: 'ISO-9223', name: 'ISO 9223 Corrosion',                  url: '(derived from EEA + BAFU)',            freq: 'Derived',   res: 'Bezirk',          vars: 1,  category: 'Environment',   feeds: 'I8 corrosion classification' },
    { id: 'WEKO',   name: 'WEKO (Competition Commission)',          url: 'weko.admin.ch',                        freq: 'Annual',    res: 'Canton',          vars: 1,  category: 'Economic',      feeds: 'Market structure, energy sector regulation' },
    { id: 'ARE',    name: 'ARE (Spatial Development Office)',        url: 'are.admin.ch',                         freq: 'Annual',    res: 'Bezirk',          vars: 1,  category: 'Socio-Econ',    feeds: 'Urban/rural classification, settlement structure' },
    { id: 'NABEL',  name: 'NABEL Air Monitoring Network',           url: 'bafu.admin.ch',                        freq: 'Continuous',res: 'Station',         vars: 2,  category: 'Environment',   feeds: 'Real-time air quality, pollution events' },
  ];

  // ─── 6 Components ────────────────────────────────────────
  const COMPONENTS = [
    {
      id: 'C', name: 'Continuity', weight: 0.30, color: '#941914',
      desc: 'Measures reliability and outage exposure — how often and how long power interruptions occur.',
      metrics: [
        { id: 'C1', name: 'Outage Duration', intra: 0.40, global: 0.120, norm: 'A (P5/P95)', source: 'ElCom / BFE', desc: 'Total annual interruption duration (SAIDI)' },
        { id: 'C2', name: 'Outage Count',    intra: 0.30, global: 0.090, norm: 'A (P5/P95)', source: 'ElCom / BFE', desc: 'Number of interruptions per year (SAIFI)' },
        { id: 'C3', name: 'MT Exceed Rate',  intra: 0.15, global: 0.045, norm: 'C (0–100%)', source: 'ElCom', desc: 'Percentage of time voltage exceeds regulation limits' },
        { id: 'C4', name: 'Planned Outages',  intra: 0.15, global: 0.045, norm: 'B (P5/P95)', source: 'ElCom Monitoring', desc: 'Duration of planned maintenance interruptions' },
      ]
    },
    {
      id: 'V', name: 'Voltage Quality', weight: 0.10, color: '#b8863a',
      desc: 'Captures voltage dip severity — short-duration voltage reductions that damage sensitive equipment.',
      metrics: [
        { id: 'V1', name: 'Severity-Weighted Dips', intra: 1.00, global: 0.100, norm: 'B (γ=0.50)', source: 'ElCom Quality Report', desc: 'V = N(V1_total × (1 + 0.50 × V2_severe_ratio))' },
      ]
    },
    {
      id: 'I', name: 'Infrastructure', weight: 0.25, color: '#5d8563',
      desc: 'Assesses physical grid condition — environmental exposure, asset density, and material degradation risks.',
      metrics: [
        { id: 'I1', name: 'Snow/Ice Risk',          intra: 0.12, global: 0.030, norm: 'C (0–0.30)', source: 'MeteoSwiss', desc: 'Climate risk index for snow and ice events', adaptive: true },
        { id: 'I2', name: 'Tree-Fall Risk',           intra: 0.09, global: 0.023, norm: 'C (0–0.30)', source: 'MeteoSwiss', desc: 'Climate risk index for tree-fall events', adaptive: true },
        { id: 'I3', name: 'Heat-Wave Risk',           intra: 0.15, global: 0.038, norm: 'C (0–0.30)', source: 'MeteoSwiss', desc: 'Climate risk index for heat-wave events', adaptive: true },
        { id: 'I4', name: 'RTN Density',              intra: 0.12, global: 0.030, norm: 'B ↓inverted', source: 'Swissgrid / OSM', desc: 'Transmission network density — higher = more resilient', inverted: true },
        { id: 'I5', name: 'Thermal Stress Proxy',     intra: 0.12, global: 0.030, norm: 'B (P5/P95)', source: 'IEEE C57.91', desc: 'Transformer thermal degradation based on ambient + load', isNew: true },
        { id: 'I6', name: 'Substation Density',       intra: 0.12, global: 0.030, norm: 'B ↓inverted', source: 'OSM / Pronovo', desc: 'Substation density — higher = more backup capacity', inverted: true },
        { id: 'I7', name: 'Load Stress',              intra: 0.10, global: 0.025, norm: 'B (P5/P95)', source: 'Swissgrid', desc: 'Ratio of peak load to rated capacity', isNew: true },
        { id: 'I8', name: 'Air Quality Corrosion',    intra: 0.08, global: 0.020, norm: 'B (P5/P95)', source: 'BAFU / EEA / ISO 9223', desc: 'Air pollution corrosion risk for outdoor equipment', isNew: true },
        { id: 'I9', name: 'Hydrogeological Risk',     intra: 0.10, global: 0.025, norm: 'B (P5/P95)', source: 'BAFU / Swisstopo', desc: 'Flood and landslide territorial exposure', isNew: true },
      ]
    },
    {
      id: 'E', name: 'Economic', weight: 0.10, color: '#aa4234',
      desc: 'Quantifies economic impact of grid disruption — regulatory penalties and productivity losses.',
      metrics: [
        { id: 'E1', name: 'ElCom Penalties/User', intra: 0.55, global: 0.055, norm: 'B (P5/P95)', source: 'ElCom / BFE', desc: 'Per-user penalty costs from quality standard violations' },
        { id: 'E2', name: 'Productivity Loss Coefficient', intra: 0.45, global: 0.045, norm: 'C (bounded)', source: 'BFS / SECO', desc: 'Weighted avg VoLL by local economic structure (β coefficient)' },
      ]
    },
    {
      id: 'S', name: 'Saturation', weight: 0.20, color: '#8e44ad',
      desc: 'Measures grid utilisation stress — generation/consumption imbalance, reverse power flow, and critical load classes.',
      metrics: [
        { id: 'S1', name: 'Bezirk KPI (Gen/Consumption)', intra: 0.75, global: 0.150, norm: 'B* (adapted)', source: 'BFE / Pronovo', desc: 'Bezirk-level generation/consumption ratio' },
        { id: 'S2', name: 'Reverse Power Flow',              intra: 0.125, global: 0.025, norm: 'D (categorical)', source: 'Swissgrid', desc: '{No RPF→0, >1%→0.5, >5%→1.0}', categorical: true },
        { id: 'S3', name: 'Criticality Class',                intra: 0.125, global: 0.025, norm: 'D (categorical)', source: 'ElCom', desc: '{Non-critical→0, Hospital/transport→0.5, Multiple critical→1.0}', categorical: true },
      ]
    },
    {
      id: 'T', name: 'Energy Transition', weight: 0.05, color: '#0e7490',
      desc: 'Captures energy-transition stress from distributed generation, output variability, and EV charging burden.',
      isNew: true,
      metrics: [
        { id: 'T1', name: 'DER Stress Index', intra: 1.00, global: 0.050, norm: 'B (composite)', source: 'Pronovo + Swissgrid + ASTRA', desc: 'Composite: α_DER(0.50) × N(DER_ratio) + α_VAR(0.30) × N(variability) + α_EV(0.20) × N(EV_load)', isNew: true,
          submetrics: [
            { id: 'DER_ratio', name: 'DER Penetration Ratio', weight: 0.50, source: 'Pronovo + Swissgrid', desc: 'DER capacity / peak load by Bezirk' },
            { id: 'DER_variability', name: 'DER Output Variability', weight: 0.30, source: 'ENTSO-E Transparency', desc: 'σ/μ of weekly DER output (coefficient of variation)' },
            { id: 'EV_load_ratio', name: 'EV Load Burden', weight: 0.20, source: 'ASTRA + Pronovo', desc: 'EV count × 7.4kW / transformer capacity' },
          ]
        },
      ]
    },
  ];

  // ─── 5 Modifiers ──────────────────────────────────────────
  const MODIFIERS = [
    {
      id: 'R3', name: 'Consequence + Energy Poverty',
      range: '[0.70, 1.30]', type: 'Multiplicative',
      desc: 'Sigmoid function of population density, energy load, and socio-economic vulnerability. Enhanced with energy poverty, fiscal weakness, and demographic shifts.',
      formula: 'C_mult = 0.70 + 0.60 / (1 + e^(−4z)), z = 0.04·log₂(pop/pop_med) + 0.03·log₂(GWh/GWh_med) + 0.02·V_socio',
      sources: ['BFS', 'SECO', 'Eurostat'],
      isEnhanced: true,
      enrichments: [
        { name: 'V_socio Fiscal Enrichment', effect: 'Up to +8% V_socio penalty', sources: 'BFS + SECO' },
        { name: 'Demographic Shift Amplifier', effect: 'Up to +8% C_mult for population decline', sources: 'BFS Demographics' },
        { name: 'Elderly Vulnerability', effect: '×[1.0, 1.10] for high elderly %', sources: 'BFS Demographics' },
        { name: 'Flood Zone Amplifier', effect: 'Up to +15% C_mult for flood zones', sources: 'BAFU' },
      ]
    },
    {
      id: 'R4', name: 'Graph-Theoretic Network Criticality',
      range: '[0.80, 1.35]', type: 'Multiplicative',
      desc: 'Combines degree centrality, betweenness centrality, and topological bridge detection from OSM power graph. Built from 947 substations and 625 power lines.',
      formula: 'F_topo = clip(base_factor(degree) × (1 + 0.10 × BC_percentile + 0.15 × is_bridge), 0.80, 1.35)',
      sources: ['OSM Overpass API'],
      isEnhanced: true
    },
    {
      id: 'R6a', name: 'Restoration Speed',
      range: '[0.90, 1.10]', type: 'Multiplicative',
      desc: 'CAIDI-based sigmoid that distinguishes fast-restoring vs slow-restoring areas.',
      formula: 'R6a_mult = sigmoid_bounded(CAIDI_local / CAIDI_med, 0.90, 1.10)',
      sources: ['ElCom Monitoring Report'],
      isNew: true
    },
    {
      id: 'R6b', name: 'Seismic Hazard (Swiss PGA)',
      range: '[1.00, 1.20]', type: 'Multiplicative',
      desc: 'Swiss PGA-calibrated seismic modifier. Penalises substations in zones with elevated peak ground acceleration above the Swiss reference threshold.',
      formula: 'R6_seis = clip(1 + 0.45 × max(0, PGA − 0.07), 1.0, 1.20)',
      sources: ['SED (Swiss Seismological Service)'],
      isNew: true
    },
    {
      id: 'R7', name: 'Digital Readiness Proxy',
      range: '[0.99, 1.05]', type: 'Multiplicative',
      desc: 'Bezirk-level continuous model based on DESI regional digital readiness scores, urban/rural adjustments, HV voltage class bonus, and per-substation noise. Unique values across 947 substations.',
      formula: 'R7_cyber(s) = clip( DESI_base(region) + urban_adj(Bezirk) + HV_bonus(voltage) + noise, 0.99, 1.05 )',
      sources: ['DESI / Eurostat', 'JRC DSO Observatory'],
      isNew: true,
      enrichments: [
        { name: 'Bezirk-Level DESI Computation', effect: 'Continuous [0.99, 1.05] per substation', sources: 'DESI / Eurostat' },
      ]
    },
  ];

  // ─── Data Layers (11 layers, 95 variables) ─────────────────
  const DATA_LAYERS = [
    { id: 'A',   name: 'SSI v4.0.2 Resilience',        vars: 20, status: 'LIVE',        sources: 'ElCom · BFS · BFE · Pronovo · Swissgrid · MeteoSwiss · ASTRA' },
    { id: 'B.1', name: 'Grid Telemetry: Open',         vars: 3,  status: 'LIVE',        sources: 'Open-Meteo / ERA5 · BFE vintage · ElCom digitalization' },
    { id: 'B.2', name: 'Grid Telemetry: Proxy',        vars: 4,  status: 'LIVE',        sources: 'IEEE C57.91 · Swissgrid · BAFU · EN 50160' },
    { id: 'B.3', name: 'Grid Telemetry: Fuzzy/Markov', vars: 12, status: 'LIVE (MARKOV)', sources: 'IEEE/CIGRÉ standards · Pronovo · EEA' },
    { id: 'C',   name: 'Socio-Economic',               vars: 9,  status: 'LIVE',        sources: 'BFS · SECO · Eurostat · DESI · ARE' },
    { id: 'D',   name: 'Environmental Hazards',         vars: 7,  status: 'LIVE',        sources: 'EEA · SED · BAFU · ISO 9223 · Copernicus CDS' },
    { id: 'E',   name: 'Swiss Open Data',               vars: 8,  status: 'LIVE',        sources: 'BAFU · BFE · ElCom · Swissgrid · SNB' },
    { id: 'F',   name: 'Network Transitions',           vars: 12, status: 'LIVE (BAYESIAN)', sources: 'DSO history OR IEEE/CIGRÉ + priors' },
    { id: 'G',   name: 'Modifier Inputs',               vars: 3,  status: 'LIVE',        sources: 'ElCom Monitoring · OSM Power · JRC DSO', isNew: true },
    { id: 'H',   name: 'Network & Topology',            vars: 7,  status: 'LIVE',        sources: 'SED · Swisstopo · OSM · BAFU', isNew: true },
    { id: 'I',   name: 'Output Scores',                 vars: 7,  status: 'LIVE',        sources: 'Fleet Markov Chain · IEEE/CIGRÉ analysis', isNew: true },
  ];

  // ─── Processing Pipeline ──────────────────────────────────
  const PIPELINE = [
    { step: 1, name: 'Ingest',     desc: '95 variables from 25 verified data sources', icon: '①' },
    { step: 2, name: 'Normalise',  desc: 'Methods A–D: fleet percentile, bounded, categorical → [0,1]', icon: '②' },
    { step: 3, name: 'Weight',     desc: '6-level hierarchy: component × intra-metric weights', icon: '③' },
    { step: 4, name: 'Compose',    desc: 'R_base = Σ wᵢ·Cᵢ (6 components, 20 metrics)', icon: '④' },
    { step: 5, name: 'Modify',     desc: 'R3 consequence × R4 topology × R6a restoration × R6b seismic × R7 digital', icon: '⑤' },
    { step: 6, name: 'Monte Carlo', desc: '10,000 iterations with 20×20 Gaussian copula', icon: '⑥' },
    { step: 7, name: 'Classify',   desc: '4 bands (Low/Medium/High/Critical) + confidence tiers + alerts', icon: '⑦' },
  ];

  // ─── Normalisation Methods ────────────────────────────────
  const NORM_METHODS = [
    { id: 'A', name: 'Fleet Percentile (robust)',    formula: 'N(x) = soft_clip((x − P₅) / (P₉₅ − P₅))', applies: 'C1, C2' },
    { id: 'B', name: 'Fleet Percentile (standard)',  formula: 'N(x) = soft_clip((x − P₅) / (P₉₅ − P₅))', applies: 'C4, V, I4↓, I6↓, E1, S1, T1 sub-metrics, I5, I7–I9' },
    { id: 'C', name: 'Bounded Rescaling',            formula: 'N(x) = (x − x_min) / (x_max − x_min)', applies: 'I1–I3 [0, 0.30], C3 [0%, 100%], E2 [1.50, 1.85]' },
    { id: 'D', name: 'Categorical Mapping',           formula: 'S2: {No RPF→0, >1%→0.5, >5%→1.0}', applies: 'S2, S3' },
  ];

  // ─── Classification Bands ─────────────────────────────────
  const CLASSIFICATION = [
    { name: 'Low',      range: '0.00 – 0.25', meaning: 'Good resilience — stable grid, low exposure',   expected: '~0%', color: '#5d8563' },
    { name: 'Medium',   range: '0.25 – 0.50', meaning: 'Moderate — some vulnerabilities, monitor',      expected: '~76%', color: '#b8863a' },
    { name: 'High',     range: '0.50 – 0.75', meaning: 'Elevated risk — investment priority area',      expected: '~24%', color: '#aa4234' },
    { name: 'Critical', range: '0.75 – 1.00', meaning: 'Severe vulnerability — urgent intervention',    expected: '~0%',   color: '#941914' },
  ];

  // ─── Master Equation ─────────────────────────────────────
  const MASTER_EQUATION = {
    formula: 'R_final = soft_clip_upper(R_base × F_topo × C_mult × R6a_mult × R6_seis × Cyber_factor)',
    R_base: 'R_base = 0.30·C + 0.10·V + 0.25·I + 0.10·E + 0.20·S + 0.05·T',
    modifiers: {
      F_topo: 'graph_criticality(degree, BC, bridge) [R4]',
      C_mult: 'consequence_sigmoid(pop, load, V_socio) [R3]',
      R6a_mult: 'restoration_speed_sigmoid(CAIDI_local) [R6a]',
      R6_seis: 'seismic_PGA(PGA, PGA_REF=0.07, alpha=0.45) [R6b]',
      Cyber_factor: 'Bezirk_DESI_cyber(region, Bezirk, voltage) [R7]'
    },
    soft_clip: 'if R_raw ≤ 1.00 → R_raw; if R_raw > 1.00 → 1.00 − 1/(1 + e^(20×(R_raw − 1.05)))'
  };

  // ─── Validation Framework ─────────────────────────────────
  const VALIDATION_CHECKS = [
    { check: 'Alpine–Mittelland gradient',  criterion: 'Alpine cantons R systematically higher than Mittelland cantons', status: 'verified' },
    { check: 'IRI-climate coherence',       criterion: 'I1 peaks high-altitude Cantons · I3 peaks Ticino / Valais', status: 'verified' },
    { check: 'Seismic zone gradient',       criterion: 'R6_seis > 1.0 for Valais/Basel, ≈ 1.0 for Jura/Bern', status: 'verified' },
    { check: 'Ratio test',                  criterion: 'R(worst) / R(best) ≥ 3×', status: 'verified' },
    { check: 'Monotonicity',               criterion: 'Each metric worsening → R increases', status: 'verified' },
    { check: 'CI width quality signal',     criterion: 'Canton-level subs have wider CI', status: 'verified' },
    { check: 'T1-DER coherence',           criterion: 'T1 peaks in solar-intensive Cantons (Ticino, Valais)', status: 'verified' },
    { check: 'R6a speed coherence',         criterion: 'R6a ≈ 1.0 for urban, R6a > 1.0 for remote Alpine areas', status: 'verified' },
    { check: 'Energy poverty gradient',    criterion: 'V_socio correlates with Alpine vs urban divide', status: 'verified' },
    { check: 'R4 bridge identification',   criterion: 'is_bridge=1 subs have higher R than degree-matched non-bridges', status: 'verified' },
    { check: 'Weight sum invariant',        criterion: 'Σ w_component = 1.000 exactly', status: 'verified' },
    { check: 'Markov risk coherence',      criterion: 'markov_risk_score positively correlates with asset age and outage rates', status: 'verified' },
    { check: 'Hydropower exposure',        criterion: 'Cantons with high hydro share show distinct S1 patterns', status: 'verified' },
  ];

  // ─── Changelog v3.4 → v4.0.2 ───────────────────────────────
  const CHANGELOG = [
    { id: 'F1', section: '§2, §4', change: 'New T component — Energy Transition Exposure (T1)', type: 'new' },
    { id: 'F2', section: '§5',     change: 'New R6a — Restoration Speed Modifier (CAIDI-based)', type: 'new' },
    { id: 'F3', section: '§5',     change: 'R3 enhanced — Energy Poverty Vulnerability (V_socio)', type: 'enhanced' },
    { id: 'F4', section: '§5',     change: 'R4 enhanced — Graph-theoretic betweenness + bridge detection', type: 'enhanced' },
    { id: 'F5', section: '§5',     change: 'R6b Swiss PGA — Seismic hazard (SED, α=0.45, PGA_REF=0.07)', type: 'new' },
    { id: 'F6', section: '§5',     change: 'R7 Digital Readiness — Bezirk-level DESI model', type: 'enhanced' },
    { id: 'L1', section: '§2, §8', change: 'New I5, I7–I9 metrics — thermal, load, corrosion, hydrogeo', type: 'new' },
    { id: 'L2', section: '§6',     change: 'E2 Innovation Enrichment — HRST + startup density', type: 'enhanced' },
    { id: 'L3', section: '§5',     change: 'V_socio Fiscal Enrichment — BFS + SECO + energy price', type: 'enhanced' },
    { id: 'L4', section: '§5',     change: 'R3 Demographic Shift Amplifier — BFS net migration', type: 'enhanced' },
    { id: 'L5', section: '§8, §12', change: '95/95 variables operational (100%). 25 data sources total.', type: 'data' },
    { id: 'G1', section: '§12',    change: 'd13 OSM — 947 real substations + 625 power lines from Overpass', type: 'data' },
    { id: 'G2', section: '§5',     change: 'R6b Seismic modifier — SED PGA calibration for Alpine front', type: 'new' },
    { id: 'G3', section: '§12',    change: 'Network & Topology layer (H): 7 variables — SED, ring analysis', type: 'new' },
    { id: 'G4', section: '§12',    change: 'Output Scores layer (I): 7 variables — risk_score, ETTC, stationary probs', type: 'new' },
  ];

  // ─── Frequency Distribution ───────────────────────────────
  const FREQ_DISTRIBUTION = {
    Weekly: { count: 2, sources: ['OSM Overpass', 'Open-Meteo/ERA5'] },
    Monthly: { count: 3, sources: ['Pronovo', 'Swissgrid', 'ENTSO-E'] },
    Quarterly: { count: 1, sources: ['SNB'] },
    Annual: { count: 13, sources: ['BFE', 'ElCom', 'BFS', 'SECO', 'BAFU', 'ASTRA', 'MeteoSwiss', 'EEA', 'Eurostat', 'DESI', 'JRC', 'WEKO', 'ARE'] },
    Static: { count: 5, sources: ['IEEE/IEC/CIGRÉ', 'Copernicus CMIP6', 'SED', 'Swisstopo', 'ISO 9223'] },
    Derived: { count: 1, sources: ['ISO 9223 Corrosion (from EEA + BAFU)'] },
  };


  // ═══════════════════════════════════════════════════════════
  //  PUBLIC API
  // ═══════════════════════════════════════════════════════════

  return {
    DATA_SOURCES,
    COMPONENTS,
    MODIFIERS,
    DATA_LAYERS,
    PIPELINE,
    NORM_METHODS,
    CLASSIFICATION,
    MASTER_EQUATION,
    VALIDATION_CHECKS,
    CHANGELOG,
    FREQ_DISTRIBUTION,

    // Quick stats
    stats: {
      variables: 95,
      metrics: 20,
      components: 6,
      modifiers: 5,
      sources: 25,
      substations: 947,
      powerLines: 625,
      mcIterations: 10000,
      bezirke: 160,
      cantons: 26
    }
  };
})();
