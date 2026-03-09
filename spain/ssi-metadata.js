/* ═══════════════════════════════════════════════════════════
   SSI v4.0.2 — Metadata Registry (Spain)
   95 variables · 30 sources · 20 metrics · 6 components · 5 modifiers
   Complete reference data for methodology page + data page
   ═══════════════════════════════════════════════════════════ */

window.SSIMetadata = (function () {
  'use strict';

  // ─── 30 Verified Data Sources ─────────────────────────────
  const DATA_SOURCES = [
    { id: 'CNMC',   name: 'CNMC (Comisión Nacional de los Mercados y la Competencia)', url: 'cnmc.es',                     freq: 'Annual',    res: 'Provincia',       vars: 8,  category: 'Grid',          feeds: 'C1–C4 (TIEPI/NIEPI/CAIDI), quality regulation' },
    { id: 'IDAE',   name: 'IDAE (Instituto para la Diversificación y Ahorro de la Energía)', url: 'idae.es',              freq: 'Quarterly', res: 'Provincia',       vars: 5,  category: 'Transition',    feeds: 'T1 DER capacity, solar/wind registry' },
    { id: 'INE',    name: 'INE (Instituto Nacional de Estadística)',                     url: 'ine.es',                     freq: 'Annual',    res: 'Provincia',       vars: 8,  category: 'Socio-Econ',    feeds: 'R3 population, elderly, GDP, fiscal capacity' },
    { id: 'REE',    name: 'REE (Red Eléctrica de España) — Transparency',               url: 'ree.es',                     freq: 'Hourly',    res: 'Bidding zone',    vars: 3,  category: 'Grid',          feeds: 'T1 peak load, generation mix, DER variability' },
    { id: 'IGN',    name: 'IGN/IGME (Instituto Geográfico Nacional)',                    url: 'ign.es',                     freq: 'Static',    res: 'Provincia',       vars: 3,  category: 'Hazard',        feeds: 'NCSE-02 seismic hazard, PGA values' },
    { id: 'OSM',    name: 'OSM Power Infrastructure',                                    url: 'overpass-api.de',            freq: 'Weekly',    res: 'Node/edge',       vars: 3,  category: 'Infrastructure',feeds: 'R4 graph topology, BC, bridges · 3,529 substations' },
    { id: 'CDS',    name: 'Copernicus CDS / ERA5',                                       url: 'cds.climate.copernicus.eu',  freq: 'Static',    res: '0.25° (~25 km)',  vars: 4,  category: 'Climate',       feeds: 'R2 Δ_climate (I1–I3 trajectory)', registration: true },
    { id: 'ENTSE',  name: 'ENTSO-E Transparency',                                        url: 'transparency.entsoe.eu',     freq: 'Hourly',    res: 'Bidding zone',    vars: 2,  category: 'Transition',    feeds: 'T1 DER variability, cross-border flows', registration: true },
    { id: 'MITECO', name: 'MITECO (Ministerio para la Transición Ecológica)',            url: 'miteco.gob.es',              freq: 'Annual',    res: 'CCAA',            vars: 4,  category: 'Environment',   feeds: 'Energy poverty, environmental indicators' },
    { id: 'DIM',    name: 'Dimovski et al. (2025)',                                       url: 'Academic paper',             freq: 'Static',    res: 'Municipal',       vars: 3,  category: 'Grid',          feeds: 'S1 breakpoints, calibration data' },
    { id: 'OM',     name: 'Open-Meteo Historical Weather',                                url: 'open-meteo.com',             freq: 'Hourly',    res: '~1 km',           vars: 3,  category: 'Climate',       feeds: 'I1–I3 snow/ice, storms, heat-wave events' },
    { id: 'IEEE',   name: 'IEEE C57.91 / IEC 60076',                                     url: 'standards.ieee.org',         freq: 'Static',    res: 'Asset-level',     vars: 16, category: 'Standards',     feeds: 'I5 thermal model, B.3 Markov states' },
    { id: 'JRC',    name: 'JRC DSO Observatory',                                          url: 'ses.jrc.ec.europa.eu',       freq: 'Annual',    res: 'DSO-level',       vars: 2,  category: 'Grid',          feeds: 'R7 provincia-level cyber-exposure (secondary)' },
    { id: 'EEA',    name: 'EEA Air Quality e-Reporting',                                  url: 'eea.europa.eu',              freq: 'Annual',    res: '~1 km + station', vars: 3,  category: 'Environment',   feeds: 'I8 PM2.5, NO₂, O₃ corrosion' },
    { id: 'EURO',   name: 'Eurostat Energy Statistics',                                   url: 'ec.europa.eu/eurostat',      freq: 'Annual',    res: 'NUTS2',           vars: 3,  category: 'Economic',      feeds: 'Energy poverty cross-validation' },
    { id: 'DESI',   name: 'DESI Digital Economy Index',                                   url: 'digital-strategy.ec.europa.eu', freq: 'Annual', res: 'EU Regional',     vars: 2,  category: 'Socio-Econ',    feeds: 'R7 provincia-level cyber-exposure (primary DESI input)' },
    { id: 'CCNC',   name: 'CCN-CERT (Centro Criptológico Nacional)',                     url: 'ccn-cert.cni.es',            freq: 'Annual',    res: 'National',        vars: 2,  category: 'Cyber',         feeds: 'National cyber resilience baseline' },
    { id: 'AEMET',  name: 'AEMET (Agencia Estatal de Meteorología)',                     url: 'aemet.es',                   freq: 'Hourly',    res: 'Station',         vars: 3,  category: 'Climate',       feeds: 'Climate normals, extreme events' },
    { id: 'PROT',   name: 'Protección Civil / DG Catástrofes',                           url: 'proteccioncivil.es',         freq: 'Annual',    res: 'Provincia',       vars: 2,  category: 'Hazard',        feeds: 'Flood zones, DANA event risk' },
    { id: 'CSN',    name: 'CSN (Consejo de Seguridad Nuclear)',                           url: 'csn.es',                     freq: 'Annual',    res: 'Site-level',      vars: 1,  category: 'Hazard',        feeds: 'Nuclear proximity, 5 active sites' },
    { id: 'GFZ',    name: 'GFZ German Research Centre',                                   url: 'gfz-potsdam.de',             freq: 'Static',    res: '~5 km',           vars: 2,  category: 'Hazard',        feeds: 'Seismic hazard (475-yr PGA), geomagnetic risk' },
    { id: 'ISO9223', name: 'ISO 9223 Corrosion',                                          url: '(derived from EEA + MITECO)',freq: 'Derived',   res: 'Provincia',       vars: 1,  category: 'Environment',   feeds: 'I8 corrosion classification' },
    { id: 'INE-E',  name: 'INE Economic Statistics',                                      url: 'ine.es',                     freq: 'Annual',    res: 'CCAA',            vars: 3,  category: 'Economic',      feeds: 'GDP sectoral, R&D intensity, energy poverty' },
    { id: 'SEPE',   name: 'SEPE (Servicio Público de Empleo Estatal)',                   url: 'sepe.es',                    freq: 'Monthly',   res: 'Provincia',       vars: 1,  category: 'Socio-Econ',    feeds: 'Unemployment rates' },
    { id: 'REE-S',  name: 'REE Statistical Series',                                       url: 'ree.es/es/datos/publicaciones', freq: 'Annual', res: 'CCAA',            vars: 2,  category: 'Grid',          feeds: 'Provincial capacity breakdown, grid investment' },
    { id: 'NCSE',   name: 'NCSE-02 Seismic Code',                                         url: 'fomento.gob.es',             freq: 'Static',    res: 'Municipal',       vars: 1,  category: 'Standards',     feeds: 'Seismic zone classification' },
    { id: 'ADIF',   name: 'ADIF Rail Statistics',                                          url: 'adif.es',                    freq: 'Annual',    res: 'Provincial',      vars: 1,  category: 'Infrastructure',feeds: 'Transport infrastructure proxy' },
    { id: 'DGT',    name: 'DGT (Dirección General de Tráfico)',                           url: 'dgt.es',                     freq: 'Annual',    res: 'Provincial',      vars: 1,  category: 'Transition',    feeds: 'EV registration data' },
    { id: 'COG-ES', name: 'INE Municipal Registry',                                       url: 'ine.es',                     freq: 'Static',    res: 'Provincial',      vars: 1,  category: 'Infrastructure',feeds: 'Provincia code join key, CCAA mapping' },
    { id: 'CNMC-M', name: 'CNMC Monitoring Report',                                       url: 'cnmc.es',                    freq: 'Annual',    res: 'DSO-level',       vars: 2,  category: 'Grid',          feeds: 'CAIDI, restoration speed, quality regulation' },
  ];

  // ─── 6 Components ────────────────────────────────────────
  const COMPONENTS = [
    {
      id: 'C', name: 'Continuity', weight: 0.30, color: '#941914',
      desc: 'Measures reliability and outage exposure — how often and how long power interruptions occur.',
      metrics: [
        { id: 'C1', name: 'Outage Duration (TIEPI)', intra: 0.40, global: 0.120, norm: 'A (P5/P95)', source: 'CNMC', desc: 'Total annual interruption duration — Tiempo de Interrupción Equivalente' },
        { id: 'C2', name: 'Outage Count (NIEPI)',    intra: 0.30, global: 0.090, norm: 'A (P5/P95)', source: 'CNMC', desc: 'Number of interruptions per year — Número de Interrupciones Equivalente' },
        { id: 'C3', name: 'MT Exceed Rate',           intra: 0.15, global: 0.045, norm: 'C (0–100%)', source: 'CNMC', desc: 'Percentage of time voltage exceeds regulation limits' },
        { id: 'C4', name: 'Planned Outages',           intra: 0.15, global: 0.045, norm: 'B (P5/P95)', source: 'CNMC Monitoring', desc: 'Duration of planned maintenance interruptions' },
      ]
    },
    {
      id: 'V', name: 'Voltage Quality', weight: 0.10, color: '#b8863a',
      desc: 'Captures voltage dip severity — short-duration voltage reductions that damage sensitive equipment.',
      metrics: [
        { id: 'V1', name: 'Severity-Weighted Dips', intra: 1.00, global: 0.100, norm: 'B (γ=0.50)', source: 'CNMC Quality Report', desc: 'V = N(V1_total × (1 + 0.50 × V2_severe_ratio))' },
      ]
    },
    {
      id: 'I', name: 'Infrastructure', weight: 0.25, color: '#5d8563',
      desc: 'Assesses physical grid condition — environmental exposure, asset density, and material degradation risks.',
      metrics: [
        { id: 'I1', name: 'Snow/Ice Risk (IRI)',     intra: 0.12, global: 0.030, norm: 'C (0–0.30)', source: 'Open-Meteo / CNMC IRI', desc: 'Climate risk index for snow and ice events', adaptive: true },
        { id: 'I2', name: 'Tree-Fall Risk (IRI)',     intra: 0.09, global: 0.023, norm: 'C (0–0.30)', source: 'Open-Meteo / CNMC IRI', desc: 'Climate risk index for tree-fall events', adaptive: true },
        { id: 'I3', name: 'Heat-Wave Risk (IRI)',     intra: 0.15, global: 0.038, norm: 'C (0–0.30)', source: 'Open-Meteo / CNMC IRI', desc: 'Climate risk index for heat-wave events', adaptive: true },
        { id: 'I4', name: 'RTN Density',              intra: 0.12, global: 0.030, norm: 'B ↓inverted', source: 'CNMC Grid Data', desc: 'Transmission network density — higher = more resilient', inverted: true },
        { id: 'I5', name: 'Thermal Stress Proxy',     intra: 0.12, global: 0.030, norm: 'B (P5/P95)', source: 'IEEE C57.91', desc: 'Transformer thermal degradation based on ambient + load', isNew: true },
        { id: 'I6', name: 'Substation Density',       intra: 0.12, global: 0.030, norm: 'B ↓inverted', source: 'OSM / IDAE', desc: 'Substation density — higher = more backup capacity', inverted: true },
        { id: 'I7', name: 'Load Stress',              intra: 0.10, global: 0.025, norm: 'B (P5/P95)', source: 'REE / DSOs', desc: 'Ratio of peak load to rated capacity', isNew: true },
        { id: 'I8', name: 'Air Quality Corrosion',    intra: 0.08, global: 0.020, norm: 'B (P5/P95)', source: 'MITECO / EEA / ISO 9223', desc: 'Air pollution corrosion risk for outdoor equipment', isNew: true },
        { id: 'I9', name: 'Hydrogeological Risk',     intra: 0.10, global: 0.025, norm: 'B (P5/P95)', source: 'IGN / Protección Civil', desc: 'Flood (DANA) and landslide territorial exposure', isNew: true },
      ]
    },
    {
      id: 'E', name: 'Economic', weight: 0.10, color: '#aa4234',
      desc: 'Quantifies economic impact of grid disruption — regulatory penalties and productivity losses.',
      metrics: [
        { id: 'E1', name: 'CNMC Penalties/User', intra: 0.55, global: 0.055, norm: 'B (P5/P95)', source: 'CNMC', desc: 'Per-user penalty costs from quality standard violations' },
        { id: 'E2', name: 'Productivity Loss Coefficient', intra: 0.45, global: 0.045, norm: 'C (bounded)', source: 'INE / Economics', desc: 'Weighted avg VoLL by local economic structure (β coefficient)' },
      ]
    },
    {
      id: 'S', name: 'Saturation', weight: 0.20, color: '#8e44ad',
      desc: 'Measures grid utilisation stress — generation/consumption imbalance, reverse power flow, and critical load classes.',
      metrics: [
        { id: 'S1', name: 'Provincia KPI (Gen/Consumption)', intra: 0.75, global: 0.150, norm: 'B* (Dimovski)', source: 'Dimovski et al.', desc: 'Provincia-level generation/consumption ratio — Dimovski breakpoints 1.29/7.78' },
        { id: 'S2', name: 'Reverse Power Flow',              intra: 0.125, global: 0.025, norm: 'D (categorical)', source: 'REE / DSO', desc: '{No RPF→0, >1%→0.5, >5%→1.0}', categorical: true },
        { id: 'S3', name: 'Criticality Class',               intra: 0.125, global: 0.025, norm: 'D (categorical)', source: 'CNMC', desc: '{Non-critical→0, Hospital/transport→0.5, Multiple critical→1.0}', categorical: true },
      ]
    },
    {
      id: 'T', name: 'Energy Transition', weight: 0.05, color: '#0e7490',
      desc: 'Captures energy-transition stress from distributed generation, output variability, and EV charging burden.',
      isNew: true,
      metrics: [
        { id: 'T1', name: 'DER Stress Index', intra: 1.00, global: 0.050, norm: 'B (composite)', source: 'IDAE + REE + DGT', desc: 'Composite: α_DER(0.50) × N(DER_ratio) + α_VAR(0.30) × N(variability) + α_EV(0.20) × N(EV_load)', isNew: true,
          submetrics: [
            { id: 'DER_ratio', name: 'DER Penetration Ratio', weight: 0.50, source: 'IDAE Registry + REE', desc: 'DER capacity / peak load by provincia' },
            { id: 'DER_variability', name: 'DER Output Variability', weight: 0.30, source: 'ENTSO-E Transparency', desc: 'σ/μ of weekly DER output (coefficient of variation)' },
            { id: 'EV_load_ratio', name: 'EV Load Burden', weight: 0.20, source: 'DGT + IDAE', desc: 'EV count × 7.4kW / transformer capacity' },
          ]
        },
      ]
    },
  ];

  // ─── 7 Modifiers ──────────────────────────────────────────
  const MODIFIERS = [
    {
      id: 'R2', name: 'Adaptive IRI + Climate Trajectory',
      range: 'Weight redistribution', type: 'Weight modifier',
      desc: 'Uses CMIP6 SSP2-4.5 projections to transform IRI_current → IRI_forward. When local hazard risk is low, weight shifts from IRI metrics (I1–I3) to structural metrics (I4, I6).',
      formula: 'IRI_forward(m,s) = IRI_current(m,s) × (1 + 0.15 × clip(Δ_climate, −0.50, +1.00))',
      sources: ['Copernicus CDS', 'Open-Meteo / CNMC IRI'],
      isEnhanced: true
    },
    {
      id: 'R3', name: 'Consequence + Energy Poverty',
      range: '[0.70, 1.30]', type: 'Multiplicative',
      desc: 'Sigmoid function of population density, energy load, and socio-economic vulnerability. Enhanced with energy poverty, fiscal weakness, demographic shifts, elderly share, and DANA flood zone enrichments.',
      formula: 'C_mult = 0.70 + 0.60 / (1 + e^(−4z)), z = 0.04·log₂(pop/pop_med) + 0.03·log₂(GWh/GWh_med) + 0.02·V_socio',
      sources: ['INE', 'MITECO', 'SEPE', 'Protección Civil'],
      isEnhanced: true,
      enrichments: [
        { name: 'V_socio Fiscal Enrichment', effect: 'Up to +8% V_socio penalty', sources: 'INE + MITECO + CNMC' },
        { name: 'Demographic Shift Amplifier', effect: 'Up to +8% C_mult for population decline', sources: 'INE Demographics' },
        { name: 'Elderly Vulnerability', effect: '×[1.0, 1.10] for high elderly %', sources: 'INE Demographics' },
        { name: 'DANA Flood Zone Amplifier', effect: 'Up to +15% C_mult for DANA-affected zones', sources: 'Protección Civil / IGN' },
      ]
    },
    {
      id: 'R4', name: 'Graph-Theoretic Network Criticality',
      range: '[0.80, 1.35]', type: 'Multiplicative',
      desc: 'Combines degree centrality, betweenness centrality, and topological bridge detection from OSM power graph. Built from 3,529 substations.',
      formula: 'F_topo = clip(base_factor(degree) × (1 + 0.10 × BC_percentile + 0.15 × is_bridge), 0.80, 1.35)',
      sources: ['OSM Overpass API'],
      isEnhanced: true
    },
    {
      id: 'R5', name: 'Asymmetric Confidence Intervals',
      range: 'Output statistic', type: 'Reporting',
      desc: 'Reports CI skewness and P(Critical) from Monte Carlo distribution. Not a modifier of R_final.',
      formula: 'skewness = (CI_upper − CI_lower) / (CI_upper + CI_lower)'
    },
    {
      id: 'R6a', name: 'Restoration Speed',
      range: '[0.90, 1.10]', type: 'Multiplicative',
      desc: 'CAIDI-based sigmoid that distinguishes fast-restoring vs slow-restoring areas.',
      formula: 'R6a_mult = sigmoid_bounded(CAIDI_local / CAIDI_med, 0.90, 1.10)',
      sources: ['CNMC Monitoring Report'],
      isNew: true
    },
    {
      id: 'R6b', name: 'Seismic Hazard (NCSE-02)',
      range: '[1.00, 1.25]', type: 'Multiplicative',
      desc: 'Seismic zone modifier based on NCSE-02 classification. Penalises substations in high-PGA zones (Murcia-Almería seismic corridor).',
      formula: 'R6b_seis = clip(1.0 + (zone − 1) × 0.25, 1.00, 1.25)',
      sources: ['IGN/IGME', 'GFZ', 'NCSE-02'],
      isNew: true
    },
    {
      id: 'R7', name: 'Digital Readiness Proxy',
      range: '[0.99, 1.05]', type: 'Multiplicative',
      desc: 'Provincia-level continuous model based on DESI regional digital readiness scores, CCN-CERT baseline, urban/rural adjustments. Unique values across 3,529 substations.',
      formula: 'R7_cyber(s) = clip( DESI_base(CCAA) + urban_adj(provincia) + HV_bonus(voltage) + noise, 0.99, 1.05 )',
      sources: ['DESI / Eurostat', 'CCN-CERT', 'JRC DSO Observatory'],
      isNew: true
    },
  ];

  // ─── Data Layers (11 layers, 95 variables) ─────────────────
  const DATA_LAYERS = [
    { id: 'A',   name: 'SSI v4.0.2 Resilience',        vars: 20, status: 'LIVE',        sources: 'CNMC · INE · Dimovski · IDAE · REE · DGT · OM' },
    { id: 'B.1', name: 'Grid Telemetry: Open',         vars: 3,  status: 'LIVE',        sources: 'Open-Meteo / ERA5 · CNMC vintage · CNMC digitalization' },
    { id: 'B.2', name: 'Grid Telemetry: Proxy',        vars: 4,  status: 'LIVE',        sources: 'IEEE C57.91 · REE / DSOs · MITECO · EN 50160' },
    { id: 'B.3', name: 'Grid Telemetry: Fuzzy/Markov', vars: 12, status: 'LIVE (MARKOV)', sources: 'IEEE/CIGRÉ standards · IDAE · EEA' },
    { id: 'C',   name: 'Socio-Economic',               vars: 9,  status: 'LIVE',        sources: 'INE · MITECO · Eurostat · DESI · SEPE' },
    { id: 'D',   name: 'Environmental Hazards',         vars: 7,  status: 'LIVE',        sources: 'EEA · GFZ · IGN · ISO 9223 · Copernicus CDS' },
    { id: 'E',   name: 'Spanish Open Data',              vars: 8,  status: 'LIVE',        sources: 'MITECO · IDAE · INE · CNMC · REE' },
    { id: 'F',   name: 'Network Transitions',           vars: 12, status: 'LIVE (BAYESIAN)', sources: 'DSO history OR IEEE/CIGRÉ + priors' },
    { id: 'G',   name: 'Modifier Inputs',               vars: 3,  status: 'LIVE',        sources: 'CNMC Monitoring · OSM Power · JRC DSO', isNew: true },
    { id: 'H',   name: 'Network & Topology',            vars: 7,  status: 'LIVE',        sources: 'REE Grid Plan · GFZ · OSM · IGN', isNew: true },
    { id: 'I',   name: 'Output Scores',                 vars: 7,  status: 'LIVE',        sources: 'Fleet Markov Chain · IEEE/CIGRÉ analysis', isNew: true },
  ];

  // ─── Processing Pipeline ──────────────────────────────────
  const PIPELINE = [
    { step: 1, name: 'Ingest',     desc: '95 variables from 30 verified data sources', icon: '①' },
    { step: 2, name: 'Normalise',  desc: 'Methods A–D: fleet percentile, bounded, categorical → [0,1]', icon: '②' },
    { step: 3, name: 'Weight',     desc: '6-level hierarchy: component × intra-metric weights', icon: '③' },
    { step: 4, name: 'Compose',    desc: 'R_base = Σ wᵢ·Cᵢ (6 components, 20 metrics)', icon: '④' },
    { step: 5, name: 'Modify',     desc: 'R2 adaptive + R3 consequence × R4 topology × R6a restoration × R6b seismic × R7 digital', icon: '⑤' },
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
    { name: 'Low',      range: '0.00 – 0.25', meaning: 'Good resilience — stable grid, low exposure',   expected: '~35–45%', color: '#5d8563' },
    { name: 'Medium',   range: '0.25 – 0.50', meaning: 'Moderate — some vulnerabilities, monitor',      expected: '~30–40%', color: '#b8863a' },
    { name: 'High',     range: '0.50 – 0.75', meaning: 'Elevated risk — investment priority area',      expected: '~10–20%', color: '#aa4234' },
    { name: 'Critical', range: '0.75 – 1.00', meaning: 'Severe vulnerability — urgent intervention',    expected: '~3–8%',   color: '#941914' },
  ];

  // ─── Master Equation ─────────────────────────────────────
  const MASTER_EQUATION = {
    formula: 'R_final = soft_clip_upper(R_base × F_topo × C_mult × R6a_mult × R6b_seis × Cyber_factor)',
    R_base: 'R_base = 0.30·C + 0.10·V + 0.25·I + 0.10·E + 0.20·S + 0.05·T',
    modifiers: {
      F_topo: 'graph_criticality(degree, BC, bridge) [R4]',
      C_mult: 'consequence_sigmoid(pop, load, V_socio) [R3]',
      R6a_mult: 'restoration_speed_sigmoid(CAIDI_local) [R6a]',
      R6b_seis: 'seismic_zone_NCSE02(PGA, zone) [R6b]',
      Cyber_factor: 'Provincia_DESI_cyber(CCAA, provincia, voltage) [R7]'
    },
    soft_clip: 'if R_raw ≤ 1.00 → R_raw; if R_raw > 1.00 → 1.00 − 1/(1 + e^(20×(R_raw − 1.05)))'
  };

  // ─── Validation Framework ─────────────────────────────────
  const VALIDATION_CHECKS = [
    { check: 'Metropolitan–Rural convergence gap',  criterion: 'Madrid/Barcelona R systematically lower than rural Soria/Zamora', status: 'verified' },
    { check: 'IRI-climate coherence',       criterion: 'I1 peaks Pyrenean Huesca · I3 peaks Mediterranean Murcia/Almería', status: 'verified' },
    { check: 'Saturation-RPF coherence',    criterion: 'S1 > 7.78 ↔ S2 > 5% agreement > 90%', status: 'verified' },
    { check: 'Ratio test',                  criterion: 'R(worst) / R(best) ≥ 5×', status: 'verified' },
    { check: 'Monotonicity',               criterion: 'Each metric worsening → R increases', status: 'verified' },
    { check: 'CI width quality signal',     criterion: 'Regional-only subs have wider CI', status: 'verified' },
    { check: 'T1-DER coherence',           criterion: 'T1 peaks in Extremadura solar-belt and Aragón wind-corridor', status: 'verified' },
    { check: 'R6a speed coherence',         criterion: 'R6a < 1.0 for Madrid, R6a > 1.0 for rural Soria/Teruel', status: 'verified' },
    { check: 'R6b seismic coherence',       criterion: 'R6b > 1.10 for Murcia-Almería corridor, R6b ≈ 1.00 for Galicia', status: 'verified' },
    { check: 'Energy poverty gradient',    criterion: 'V_socio correlates with Ceuta/Melilla > Canarias > Andalucía > País Vasco', status: 'verified' },
    { check: 'R4 bridge identification',   criterion: 'is_bridge=1 subs have higher R than degree-matched non-bridges', status: 'verified' },
    { check: 'Climate trajectory direction', criterion: 'I3 trajectory > 1.0 in South-East, I1 stable in Pyrenean North', status: 'verified' },
    { check: 'Weight sum invariant',        criterion: 'Σ w_component = 1.000 exactly', status: 'verified' },
    { check: 'DANA flood coherence',        criterion: 'Valencia/Alicante/Murcia flood scores highest in fleet', status: 'verified' },
    { check: 'Corrosion class gradient',   criterion: 'Coastal provincias (Galicia/Med) C3–C5 > inland Meseta C1–C2', status: 'verified' },
  ];

  // ─── Changelog v3.4 → v4.0.2 ───────────────────────────────
  const CHANGELOG = [
    { id: 'F1', section: '§2, §4', change: 'New T component — Energy Transition Exposure (T1)', type: 'new' },
    { id: 'F2', section: '§5',     change: 'New R6a — Restoration Speed Modifier (CAIDI-based)', type: 'new' },
    { id: 'F3', section: '§5',     change: 'R3 enhanced — Energy Poverty Vulnerability (V_socio)', type: 'enhanced' },
    { id: 'F4', section: '§5',     change: 'R4 enhanced — Graph-theoretic betweenness + bridge detection', type: 'enhanced' },
    { id: 'F5', section: '§5',     change: 'R2 enhanced — Climate Trajectory (CMIP6 SSP2-4.5)', type: 'enhanced' },
    { id: 'F6', section: '§5',     change: 'R7 Digital Readiness — Provincia-level DESI model', type: 'enhanced' },
    { id: 'L1', section: '§2, §8', change: 'New I5, I7–I9 metrics — thermal, load, corrosion, hydrogeo', type: 'new' },
    { id: 'L2', section: '§6',     change: 'E2 Innovation Enrichment — R&D + economic structure', type: 'enhanced' },
    { id: 'L3', section: '§5',     change: 'V_socio Fiscal Enrichment — INE + MITECO + energy price', type: 'enhanced' },
    { id: 'L4', section: '§5',     change: 'R3 Demographic Shift Amplifier — INE net migration', type: 'enhanced' },
    { id: 'L5', section: '§8, §12', change: '95/95 variables operational (100%). 30 data sources total.', type: 'data' },
    { id: 'G1', section: '§12',    change: 'IDAE upgraded to quarterly registry — Provincia-level DER registry', type: 'data' },
    { id: 'G2', section: '§12',    change: 'IGN upgraded to live API — Provincia-level seismic data', type: 'data' },
    { id: 'G3', section: '§12',    change: 'OSM upgraded to Overpass API — 3,529 real substations', type: 'data' },
    { id: 'G4', section: '§5',     change: 'R6b Seismic Hazard modifier — NCSE-02 classification from IGN', type: 'new' },
    { id: 'G5', section: '§12',    change: 'Network & Topology layer (H): 7 variables — REE Grid Plan, seismic analysis', type: 'new' },
    { id: 'G6', section: '§12',    change: 'Output Scores layer (I): 7 variables — risk_score, ETTC, stationary probs', type: 'new' },
  ];

  // ─── Frequency Distribution ───────────────────────────────
  const FREQ_DISTRIBUTION = {
    Weekly: { count: 2, sources: ['OSM Overpass', 'Open-Meteo/ERA5'] },
    Monthly: { count: 2, sources: ['IDAE Registry', 'REE Transparency'] },
    Quarterly: { count: 1, sources: ['DGT'] },
    Annual: { count: 17, sources: ['CNMC', 'INE', 'MITECO', 'SEPE', 'IDAE', 'REE-S', 'CNMC-M', 'EEA', 'Eurostat', 'DESI', 'CCN-CERT', 'CSN', 'JRC', 'Protección Civil', 'ADIF', 'AEMET', 'INE-E'] },
    Static: { count: 8, sources: ['Dimovski', 'IEEE/IEC/CIGRÉ', 'Copernicus CMIP6', 'GFZ', 'IGN', 'ISO 9223', 'COG-ES/INE', 'NCSE-02'] },
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
      sources: 30,
      substations: 3529,
      powerLines: 0,
      mcIterations: 10000,
      provincias: 50,
      regions: 17
    }
  };
})();
