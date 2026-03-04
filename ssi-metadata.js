/* ═══════════════════════════════════════════════════════════
   SSI v4.0 — Metadata Registry
   81 variables · 30 sources · 20 metrics · 6 components · 7 modifiers
   Complete reference data for methodology page + data page
   ═══════════════════════════════════════════════════════════ */

window.SSIMetadata = (function () {
  'use strict';

  // ─── 30 Verified Data Sources ─────────────────────────────
  const DATA_SOURCES = [
    { id: 'D-ED',  name: 'E-Distribuzione Reports',       url: 'e-distribuzione.it',                     freq: 'Annual',    res: 'Provincial',      vars: 7,  category: 'Grid',          feeds: 'C1–C4, I1–I3 (SAIDI/SAIFI/IRI)' },
    { id: 'BdI',   name: 'Bank of Italy (BDS + QEF 737)', url: 'infostat.bancaditalia.it',               freq: 'Quarterly', res: 'Regional',        vars: 5,  category: 'Economic',      feeds: 'E2 β weights, VoLL, macro indicators' },
    { id: 'DIM',   name: 'Dimovski et al. (2025)',         url: 'Academic paper',                         freq: 'Static',    res: 'Municipal',       vars: 3,  category: 'Grid',          feeds: 'S1 breakpoints, calibration data' },
    { id: 'D2',    name: 'GSE Atlaimpianti',               url: 'atlaimpianti.gse.it',                    freq: 'Quarterly', res: 'Municipal',       vars: 1,  category: 'Transition',    feeds: 'T1 DER capacity registry' },
    { id: 'D1',    name: 'Terna Open Data Portal',         url: 'dati.terna.it',                          freq: 'Monthly',   res: 'Zone (6)',        vars: 2,  category: 'Grid',          feeds: 'T1 peak load, I7 load stress' },
    { id: 'D11',   name: 'ENTSO-E Transparency',           url: 'transparency.entsoe.eu',                 freq: 'Hourly',    res: 'Bidding zone',    vars: 1,  category: 'Transition',    feeds: 'T1 DER variability', registration: true },
    { id: 'D10',   name: 'Copernicus CDS / ERA5',          url: 'cds.climate.copernicus.eu',              freq: 'Static',    res: '0.25° (~25 km)',  vars: 4,  category: 'Climate',       feeds: 'R2 Δ_climate (I1–I3 trajectory)', registration: true },
    { id: 'D5',    name: 'OIPE LIHC',                      url: 'oipeosservatorio.it',                    freq: 'Annual',    res: 'Region (NUTS2)',  vars: 1,  category: 'Socio-Econ',    feeds: 'R3 V_socio energy poverty' },
    { id: 'D6',    name: 'ARERA TIQE Tables',              url: 'reporting.arera.it',                     freq: 'Annual',    res: 'Ambito',          vars: 3,  category: 'Grid',          feeds: 'R6 CAIDI, quality regulation' },
    { id: 'D7',    name: 'OSM Power Infrastructure',       url: 'overpass-api.de',                        freq: 'Weekly',    res: 'Node/edge',       vars: 2,  category: 'Infrastructure',feeds: 'R4 graph topology, BC, bridges' },
    { id: 'JRC',   name: 'JRC DSO Observatory',            url: 'ses.jrc.ec.europa.eu',                   freq: 'Annual',    res: 'DSO-level',       vars: 2,  category: 'Grid',          feeds: 'R7 province-level cyber-exposure (secondary)' },
    { id: 'D-OM',  name: 'Open-Meteo / ERA5',              url: 'open-meteo.com',                         freq: 'Hourly',    res: '~1 km',           vars: 1,  category: 'Climate',       feeds: 'I5 ambient temperature proxy' },
    { id: 'IEEE-1',name: 'IEEE C57.91 / IEC 60076',        url: 'standards.ieee.org',                     freq: 'Static',    res: 'Asset-level',     vars: 16, category: 'Standards',     feeds: 'I5 thermal model, B.3 Markov states' },
    { id: 'D13',   name: 'ISTAT Census / Demographics',    url: 'demo.istat.it',                          freq: 'Annual',    res: 'Municipal',       vars: 8,  category: 'Socio-Econ',    feeds: 'R3 pop density, elderly, migration' },
    { id: 'EEA',   name: 'EEA Air Quality e-Reporting',    url: 'eea.europa.eu',                          freq: 'Annual',    res: '~1 km + station', vars: 3,  category: 'Environment',   feeds: 'I8 PM2.5, NO₂, O₃ corrosion' },
    { id: 'D3',    name: 'ISPRA IdroGEO + Emissions',      url: 'idrogeo.isprambiente.it',                freq: 'Annual',    res: 'Municipal',       vars: 3,  category: 'Hazard',        feeds: 'I9 flood/landslide risk' },
    { id: 'INGV',  name: 'INGV Seismic Hazard (MPS04)',    url: 'mps04-ws.pi.ingv.it',                    freq: 'Static',    res: '0.05° (~5.5 km)', vars: 1,  category: 'Hazard',        feeds: 'Seismic PGA (475-yr return)' },
    { id: 'D4',    name: 'Eurostat Energy Statistics',      url: 'ec.europa.eu/eurostat',                  freq: 'Annual',    res: 'NUTS2',           vars: 3,  category: 'Economic',      feeds: 'Energy poverty cross-validation' },
    { id: 'MEF',   name: 'MEF IRPEF Tax Statistics',       url: 'finanze.gov.it',                         freq: 'Annual',    res: 'Municipal',       vars: 1,  category: 'Socio-Econ',    feeds: 'R3 fiscal enrichment' },
    { id: 'MIMIT', name: 'MIMIT/InfoCamere Startup',       url: 'startup.registroimprese.it',             freq: 'Quarterly', res: 'Provincial',      vars: 1,  category: 'Economic',      feeds: 'E2 innovation enrichment' },
    { id: 'DESI',  name: 'DESI Digital Economy Index',      url: 'digital-strategy.ec.europa.eu',          freq: 'Annual',    res: 'EU Regional',     vars: 2,  category: 'Socio-Econ',    feeds: 'R7 province-level cyber-exposure (primary DESI input)' },
    { id: 'SVIMEZ',name: 'SVIMEZ Rapporto Mezzogiorno',    url: 'svimez.info',                            freq: 'Annual',    res: 'Macro-area',      vars: 1,  category: 'Socio-Econ',    feeds: 'R3 development gap' },
    { id: 'MIN-SAL', name: 'Min. Salute Health Registry',  url: 'salute.gov.it',                          freq: 'Annual',    res: 'Regional',        vars: 1,  category: 'Socio-Econ',    feeds: 'S3 healthcare criticality' },
    { id: 'ISO-9223', name: 'ISO 9223 Corrosion',          url: '(derived from EEA + ISPRA)',             freq: 'Derived',   res: 'Provincial',      vars: 1,  category: 'Environment',   feeds: 'I8 corrosion classification' },
    { id: 'D9',    name: 'ENEA RAEE / SIAPE',              url: 'opendata.enea.it',                       freq: 'Annual',    res: 'Province',        vars: 1,  category: 'Transition',    feeds: 'T1 EV/heat pump registry' },
    { id: 'ISPRA-S', name: 'ISPRA SCIA',                   url: 'scia.isprambiente.it',                   freq: 'Annual',    res: '0.1° grid',       vars: 1,  category: 'Climate',       feeds: 'Provincial CO₂ emissions' },
    { id: 'D12',   name: 'Protezione Civile (DPC)',         url: 'rischi.protezionecivile.gov.it',         freq: 'Continuous', res: 'Municipal',      vars: 1,  category: 'Hazard',        feeds: 'Seismic zones, hydro alerts' },
    { id: 'CONSIP',name: 'Consip / ANAC Open Data',        url: 'dati.consip.it',                         freq: 'Monthly',   res: 'PA-level',        vars: 1,  category: 'Economic',      feeds: 'PA energy consumption' },
    { id: 'D8',    name: 'MASE / SISEN Energy Portal',     url: 'dgsaie.mise.gov.it/sisen',               freq: 'Annual',    res: 'Provincial',      vars: 1,  category: 'Economic',      feeds: 'Provincial fuel prices' },
    { id: 'ISTAT-DM', name: 'ISTAT Demographics',          url: 'demo.istat.it',                          freq: 'Annual',    res: 'Regional',        vars: 2,  category: 'Socio-Econ',    feeds: 'Migration + elderly share' },
  ];

  // ─── 6 Components ────────────────────────────────────────
  const COMPONENTS = [
    {
      id: 'C', name: 'Continuity', weight: 0.30, color: '#941914',
      desc: 'Measures reliability and outage exposure — how often and how long power interruptions occur.',
      metrics: [
        { id: 'C1', name: 'Outage Duration', intra: 0.40, global: 0.120, norm: 'A (P5/P95)', source: 'E-Distribuzione / ARERA', desc: 'Total annual interruption duration (SAIDI)' },
        { id: 'C2', name: 'Outage Count',    intra: 0.30, global: 0.090, norm: 'A (P5/P95)', source: 'E-Distribuzione / ARERA', desc: 'Number of interruptions per year (SAIFI)' },
        { id: 'C3', name: 'MT Exceed Rate',  intra: 0.15, global: 0.045, norm: 'C (0–100%)', source: 'ARERA', desc: 'Percentage of time voltage exceeds regulation limits' },
        { id: 'C4', name: 'Planned Outages',  intra: 0.15, global: 0.045, norm: 'B (P5/P95)', source: 'E-Distribuzione', desc: 'Duration of planned maintenance interruptions' },
      ]
    },
    {
      id: 'V', name: 'Voltage Quality', weight: 0.10, color: '#b8863a',
      desc: 'Captures voltage dip severity — short-duration voltage reductions that damage sensitive equipment.',
      metrics: [
        { id: 'V1', name: 'Severity-Weighted Dips', intra: 1.00, global: 0.100, norm: 'B (γ=0.50)', source: 'BdI QEF 737', desc: 'V = N(V1_total × (1 + 0.50 × V2_severe_ratio))' },
      ]
    },
    {
      id: 'I', name: 'Infrastructure', weight: 0.25, color: '#5d8563',
      desc: 'Assesses physical grid condition — environmental exposure, asset density, and material degradation risks.',
      metrics: [
        { id: 'I1', name: 'Snow/Ice Risk (IRI)',     intra: 0.12, global: 0.030, norm: 'C (0–0.30)', source: 'E-Distribuzione IRI', desc: 'Climate risk index for snow and ice events', adaptive: true },
        { id: 'I2', name: 'Tree-Fall Risk (IRI)',     intra: 0.09, global: 0.023, norm: 'C (0–0.30)', source: 'E-Distribuzione IRI', desc: 'Climate risk index for tree-fall events', adaptive: true },
        { id: 'I3', name: 'Heat-Wave Risk (IRI)',     intra: 0.15, global: 0.038, norm: 'C (0–0.30)', source: 'E-Distribuzione IRI', desc: 'Climate risk index for heat-wave events', adaptive: true },
        { id: 'I4', name: 'RTN Density',              intra: 0.12, global: 0.030, norm: 'B ↓inverted', source: 'BdI QEF 737', desc: 'Transmission network density — higher = more resilient', inverted: true },
        { id: 'I5', name: 'Thermal Stress Proxy',     intra: 0.12, global: 0.030, norm: 'B (P5/P95)', source: 'IEEE C57.91', desc: 'Transformer thermal degradation based on ambient + load', isNew: true },
        { id: 'I6', name: 'Substation Density',       intra: 0.12, global: 0.030, norm: 'B ↓inverted', source: 'BdI QEF 737', desc: 'Substation density — higher = more backup capacity', inverted: true },
        { id: 'I7', name: 'Load Stress',              intra: 0.10, global: 0.025, norm: 'B (P5/P95)', source: 'Terna Open Data', desc: 'Ratio of peak load to rated capacity', isNew: true },
        { id: 'I8', name: 'Air Quality Corrosion',    intra: 0.08, global: 0.020, norm: 'B (P5/P95)', source: 'EEA / ISO 9223', desc: 'Air pollution corrosion risk for outdoor equipment', isNew: true },
        { id: 'I9', name: 'Hydrogeological Risk',     intra: 0.10, global: 0.025, norm: 'B (P5/P95)', source: 'ISPRA IdroGEO', desc: 'Flood and landslide territorial exposure', isNew: true },
      ]
    },
    {
      id: 'E', name: 'Economic', weight: 0.10, color: '#aa4234',
      desc: 'Quantifies economic impact of grid disruption — regulatory penalties and productivity losses.',
      metrics: [
        { id: 'E1', name: 'ARERA Penalties/BT User', intra: 0.55, global: 0.055, norm: 'B (P5/P95)', source: 'BdI QEF 737 / ARERA', desc: 'Per-user penalty costs from quality standard violations' },
        { id: 'E2', name: 'Productivity Loss Coefficient', intra: 0.45, global: 0.045, norm: 'C (bounded)', source: 'ISTAT SBS / BdI', desc: 'Weighted avg VoLL by local economic structure (β coefficient)' },
      ]
    },
    {
      id: 'S', name: 'Saturation', weight: 0.20, color: '#8e44ad',
      desc: 'Measures grid utilisation stress — generation/consumption imbalance, reverse power flow, and critical load classes.',
      metrics: [
        { id: 'S1', name: 'Municipal KPI (Gen/Consumption)', intra: 0.75, global: 0.150, norm: 'B* (Dimovski)', source: 'Dimovski et al.', desc: 'Municipal generation/consumption ratio — Dimovski breakpoints 1.29/7.78' },
        { id: 'S2', name: 'Reverse Power Flow',              intra: 0.125, global: 0.025, norm: 'D (categorical)', source: 'DSO', desc: '{No RPF→0, >1%→0.5, >5%→1.0}', categorical: true },
        { id: 'S3', name: 'Criticality Class',                intra: 0.125, global: 0.025, norm: 'D (categorical)', source: 'ARERA', desc: '{Non-critical→0, Hospital/transport→0.5, Multiple critical→1.0}', categorical: true },
      ]
    },
    {
      id: 'T', name: 'Energy Transition', weight: 0.05, color: '#0e7490',
      desc: 'Captures energy-transition stress from distributed generation, output variability, and EV charging burden.',
      isNew: true,
      metrics: [
        { id: 'T1', name: 'DER Stress Index', intra: 1.00, global: 0.050, norm: 'B (composite)', source: 'GSE + Terna + ENEA', desc: 'Composite: α_DER(0.50) × N(DER_ratio) + α_VAR(0.30) × N(variability) + α_EV(0.20) × N(EV_load)', isNew: true,
          submetrics: [
            { id: 'DER_ratio', name: 'DER Penetration Ratio', weight: 0.50, source: 'GSE Atlaimpianti + Terna', desc: 'DER capacity / peak load by municipality' },
            { id: 'DER_variability', name: 'DER Output Variability', weight: 0.30, source: 'ENTSO-E Transparency', desc: 'σ/μ of weekly DER output (coefficient of variation)' },
            { id: 'EV_load_ratio', name: 'EV Load Burden', weight: 0.20, source: 'ENEA RAEE', desc: 'EV count × 7.4kW / transformer capacity' },
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
      sources: ['Copernicus CDS', 'E-Distribuzione IRI'],
      isEnhanced: true
    },
    {
      id: 'R3', name: 'Consequence + Energy Poverty',
      range: '[0.70, 1.30]', type: 'Multiplicative',
      desc: 'Sigmoid function of population density, energy load, and socio-economic vulnerability. Enhanced with energy poverty, fiscal weakness, migration, elderly share, and flood zone enrichments.',
      formula: 'C_mult = 0.70 + 0.60 / (1 + e^(−4z)), z = 0.04·log₂(pop/pop_med) + 0.03·log₂(GWh/GWh_med) + 0.02·V_socio',
      sources: ['ISTAT', 'OIPE LIHC', 'MEF', 'SVIMEZ', 'ISPRA'],
      isEnhanced: true,
      enrichments: [
        { name: 'V_socio Fiscal Enrichment', effect: 'Up to +8% V_socio penalty', sources: 'MEF + SVIMEZ + ARERA' },
        { name: 'Migration Workforce Amplifier', effect: 'Up to +8% C_mult for brain-drain', sources: 'ISTAT Demographics' },
        { name: 'Elderly Vulnerability', effect: '×[1.0, 1.10] for high elderly %', sources: 'ISTAT Demographics' },
        { name: 'Flood Zone Amplifier', effect: 'Up to +15% C_mult for flood zones', sources: 'ISPRA IdroGEO' },
      ]
    },
    {
      id: 'R4', name: 'Graph-Theoretic Network Criticality',
      range: '[0.80, 1.35]', type: 'Multiplicative',
      desc: 'Combines degree centrality, betweenness centrality, and topological bridge detection from OSM power graph.',
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
      id: 'R6', name: 'Restoration Speed',
      range: '[0.90, 1.10]', type: 'Multiplicative',
      desc: 'CAIDI-based sigmoid that distinguishes fast-restoring vs slow-restoring areas.',
      formula: 'R6_mult = sigmoid_bounded(CAIDI_local / CAIDI_med, 0.90, 1.10)',
      sources: ['ARERA TIQE'],
      isNew: true
    },
    {
      id: 'R7', name: 'Cyber-Exposure Proxy',
      range: '[0.99, 1.05]', type: 'Multiplicative',
      desc: 'Province-level continuous model based on DESI regional digital readiness scores, urban/rural adjustments, HV voltage class bonus, and per-substation noise. 556 unique values across 4,293 substations.',
      formula: 'R7_cyber(s) = clip( DESI_base(region) + urban_adj(province) + HV_bonus(voltage) + noise, 0.99, 1.05 )',
      sources: ['DESI / Eurostat', 'JRC DSO Observatory'],
      isNew: true,
      enrichments: [
        { name: 'Province-Level DESI Computation', effect: 'Continuous [0.99, 1.05] per substation', sources: 'DESI / Eurostat' },
      ]
    },
  ];

  // ─── Data Layers (8 layers, 81 variables) ─────────────────
  const DATA_LAYERS = [
    { id: 'A',   name: 'SSI v4.0 Resilience',         vars: 17, status: 'LIVE',        sources: 'E-Distribuzione · BdI QEF 737 · Dimovski · ISTAT SBS · GSE · Terna · ENEA' },
    { id: 'B.1', name: 'Grid Telemetry: Open',         vars: 3,  status: 'OPEN SOURCE', sources: 'Open-Meteo / ERA5 · ARERA vintage · ARERA digitalization' },
    { id: 'B.2', name: 'Grid Telemetry: Proxy',        vars: 4,  status: 'LIVE',        sources: 'IEEE C57.91 · Terna · ISPRA · EN 50160' },
    { id: 'B.3', name: 'Grid Telemetry: Fuzzy/Markov', vars: 12, status: 'LIVE (MARKOV)', sources: 'IEEE/CIGRÉ standards · GSE · EEA' },
    { id: 'C',   name: 'Socio-Economic',               vars: 9,  status: 'LIVE',        sources: 'ISTAT · OIPE LIHC · Eurostat · DESI · SVIMEZ' },
    { id: 'D',   name: 'Environmental Hazards',         vars: 7,  status: 'LIVE',        sources: 'EEA · INGV · ISPRA · ISO 9223 · Copernicus CDS' },
    { id: 'E',   name: 'Italian Open Data',             vars: 8,  status: 'LIVE',        sources: 'ISPRA · MISE · MEF · ARERA · Terna' },
    { id: 'F',   name: 'Markov Transitions',            vars: 12, status: 'LIVE (BAYESIAN)', sources: 'DSO history OR IEEE/CIGRÉ + priors' },
    { id: 'G',   name: 'Modifier Inputs',               vars: 3,  status: 'NEW',         sources: 'ARERA TIQE · OSM Power · JRC DSO', isNew: true },
  ];

  // ─── Processing Pipeline ──────────────────────────────────
  const PIPELINE = [
    { step: 1, name: 'Ingest',     desc: '81 variables from 30 verified data sources', icon: '①' },
    { step: 2, name: 'Normalise',  desc: 'Methods A–D: fleet percentile, bounded, categorical → [0,1]', icon: '②' },
    { step: 3, name: 'Weight',     desc: '6-level hierarchy: component × intra-metric weights', icon: '③' },
    { step: 4, name: 'Compose',    desc: 'R_base = Σ wᵢ·Cᵢ (6 components, 20 metrics)', icon: '④' },
    { step: 5, name: 'Modify',     desc: 'R2 adaptive + R3 consequence × R4 topology × R6 restoration × R7 cyber', icon: '⑤' },
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
    formula: 'R_final = soft_clip_upper(R_base × F_topo × C_mult × R6_mult × Cyber_factor)',
    R_base: 'R_base = 0.30·C + 0.10·V + 0.25·I + 0.10·E + 0.20·S + 0.05·T',
    modifiers: {
      F_topo: 'graph_criticality(degree, BC, bridge) [R4]',
      C_mult: 'consequence_sigmoid(pop, load, V_socio) [R3]',
      R6_mult: 'restoration_speed_sigmoid(CAIDI_local) [R6]',
      Cyber_factor: 'province_DESI_cyber(region, province, voltage) [R7]'
    },
    soft_clip: 'if R_raw ≤ 1.00 → R_raw; if R_raw > 1.00 → 1.00 − 1/(1 + e^(20×(R_raw − 1.05)))'
  };

  // ─── Validation Framework ─────────────────────────────────
  const VALIDATION_CHECKS = [
    { check: 'North–South gradient',       criterion: 'Mezzogiorno R systematically higher than Centro-Nord', status: 'expected' },
    { check: 'IRI-climate coherence',       criterion: 'I1 peaks Alpine · I3 peaks Sicilia/Calabria', status: 'expected' },
    { check: 'Saturation-RPF coherence',    criterion: 'S1 > 7.78 ↔ S2 > 5% agreement > 90%', status: 'expected' },
    { check: 'Ratio test',                  criterion: 'R(worst) / R(best) ≥ 5×', status: 'expected' },
    { check: 'Monotonicity',               criterion: 'Each metric worsening → R increases', status: 'expected' },
    { check: 'CI width quality signal',     criterion: 'Regional-only subs have wider CI', status: 'expected' },
    { check: 'T1-DER coherence',           criterion: 'T1 peaks in southern solar-belt provinces', status: 'new', isNew: true },
    { check: 'R6 speed coherence',         criterion: 'R6 < 1.0 for Nord-Ovest, R6 > 1.0 for Sud/Isole', status: 'new', isNew: true },
    { check: 'F3 poverty gradient',        criterion: 'V_socio monotonically increases North → South', status: 'new', isNew: true },
    { check: 'R4 bridge identification',   criterion: 'is_bridge=1 subs have higher R than degree-matched non-bridges', status: 'new', isNew: true },
    { check: 'Climate trajectory direction', criterion: 'I3 trajectory > 1.0 in South, I1 < 1.0 in Alpine North', status: 'new', isNew: true },
    { check: 'Weight sum invariant',        criterion: 'Σ w_component = 1.000 exactly', status: 'verified' },
  ];

  // ─── Changelog v3.4 → v4.0 ───────────────────────────────
  const CHANGELOG = [
    { id: 'F1', section: '§2, §4', change: 'New T component — Energy Transition Exposure (T1)', type: 'new' },
    { id: 'F2', section: '§5',     change: 'New R6 — Restoration Speed Modifier (CAIDI-based)', type: 'new' },
    { id: 'F3', section: '§5',     change: 'R3 enhanced — Energy Poverty Vulnerability (V_socio)', type: 'enhanced' },
    { id: 'F4', section: '§5',     change: 'R4 enhanced — Graph-theoretic betweenness + bridge detection', type: 'enhanced' },
    { id: 'F5', section: '§5',     change: 'R2 enhanced — Climate Trajectory (CMIP6 SSP2-4.5)', type: 'enhanced' },
    { id: 'F6', section: '§5',     change: 'R7 Cyber-Exposure — Province-level DESI model (v4.1)', type: 'enhanced' },
    { id: 'L1', section: '§2, §8', change: 'New I5, I7–I9 metrics — thermal, load, corrosion, hydrogeo', type: 'new' },
    { id: 'L2', section: '§6',     change: 'E2 Innovation Enrichment — HRST + startup density', type: 'enhanced' },
    { id: 'L3', section: '§5',     change: 'V_socio Fiscal Enrichment — MEF + SVIMEZ + energy price', type: 'enhanced' },
    { id: 'L4', section: '§5',     change: 'R3 Migration Amplifier — ISTAT net migration', type: 'enhanced' },
    { id: 'L5', section: '§8, §12', change: '80/81 variables operational (98.8%). 30 data sources total.', type: 'data' },
  ];

  // ─── Frequency Distribution ───────────────────────────────
  const FREQ_DISTRIBUTION = {
    Weekly: { count: 2, sources: ['OSM Overpass', 'Open-Meteo/ERA5'] },
    Monthly: { count: 2, sources: ['Terna', 'Consip/ANAC'] },
    Quarterly: { count: 3, sources: ['GSE Atlaimpianti', 'MIMIT/InfoCamere', 'BdI'] },
    Annual: { count: 18, sources: ['E-Distribuzione', 'ARERA', 'ISTAT', 'OIPE', 'EEA', 'ISPRA', 'Eurostat', 'MEF', 'DESI', 'SVIMEZ', 'Min. Salute', 'ENEA', 'MASE', 'ISTAT Demographics', 'Protezione Civile', 'ENTSO-E', 'JRC', 'ISPRA SCIA'] },
    Static: { count: 5, sources: ['Dimovski', 'IEEE/IEC/CIGRÉ', 'Copernicus CMIP6', 'INGV MPS04', 'ISO 9223'] },
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
      variables: 81,
      metrics: 20,
      components: 6,
      modifiers: 7,
      sources: 30,
      substations: 4293,
      powerLines: 14221,
      mcIterations: 10000,
      provinces: 107,
      regions: 20
    }
  };
})();
