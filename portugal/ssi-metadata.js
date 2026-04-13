/* ═══════════════════════════════════════════════════════════
   SSI v4.0.2 — Metadata Registry (Portugal)
   95 variables · 28 sources · 20 metrics · 6 components · 5 modifiers
   Complete reference data for methodology page + data page
   ═══════════════════════════════════════════════════════════ */

window.SSIMetadata = (function () {
  'use strict';

  // ─── 28 Verified Data Sources ─────────────────────────────
  const DATA_SOURCES = [
    { id: 'ERSE',   name: 'ERSE (Entidade Reguladora dos Serviços Energéticos)', url: 'erse.pt',                              freq: 'Annual',    res: 'Distrito',        vars: 8,  category: 'Grid',          feeds: 'C1–C4 (SAIDI/SAIFI), I1–I3 (IRI), quality regulation' },
    { id: 'DGEG',   name: 'DGEG (Direção-Geral de Energia e Geologia)',          url: 'dgeg.gov.pt',                          freq: 'Quarterly', res: 'Concelho',        vars: 5,  category: 'Transition',    feeds: 'T1 DER capacity, solar/wind registry, licensing' },
    { id: 'INE',    name: 'INE (Instituto Nacional de Estatística)',              url: 'ine.pt',                               freq: 'Annual',    res: 'Distrito',        vars: 8,  category: 'Socio-Econ',    feeds: 'R3 population, elderly, GDP, fiscal capacity' },
    { id: 'REN',    name: 'REN (Redes Energéticas Nacionais)',                    url: 'ren.pt',                               freq: 'Hourly',    res: 'Bidding zone',    vars: 3,  category: 'Grid',          feeds: 'T1 peak load, generation mix, DER variability' },
    { id: 'LNEG',   name: 'LNEG (Laboratório Nacional de Energia e Geologia)',   url: 'lneg.pt',                              freq: 'Static',    res: 'Distrito',        vars: 3,  category: 'Hazard',        feeds: 'I9 hydrogeological risk, soil stability, seismic zones' },
    { id: 'OSM',    name: 'OSM Power Infrastructure',                             url: 'overpass-api.de',                      freq: 'Weekly',    res: 'Node/edge',       vars: 3,  category: 'Infrastructure',feeds: 'R4 graph topology, BC, bridges · 10,191 substations' },
    { id: 'D10',    name: 'Copernicus CDS / ERA5',                                url: 'cds.climate.copernicus.eu',            freq: 'Static',    res: '0.25° (~25 km)',  vars: 4,  category: 'Climate',       feeds: 'R2 Δ_climate (I1–I3 trajectory)', registration: true },
    { id: 'ENTSE',  name: 'ENTSO-E Transparency',                                 url: 'transparency.entsoe.eu',               freq: 'Hourly',    res: 'Bidding zone',    vars: 2,  category: 'Transition',    feeds: 'T1 DER variability, cross-border flows (MIBEL)', registration: true },
    { id: 'ADENE',  name: 'ADENE (Agência para a Energia)',                       url: 'adene.pt',                             freq: 'Annual',    res: 'Distrito',        vars: 4,  category: 'Environment',   feeds: 'Energy poverty, energy efficiency certificates' },
    { id: 'DIM',    name: 'Dimovski et al. (2025)',                                url: 'Academic paper',                       freq: 'Static',    res: 'Municipal',       vars: 3,  category: 'Grid',          feeds: 'S1 breakpoints, calibration data' },
    { id: 'IPMA-W', name: 'Open-Meteo Historical Weather',                        url: 'open-meteo.com',                      freq: 'Hourly',    res: '~1 km',           vars: 3,  category: 'Climate',       feeds: 'I1–I3 snow/ice, storms, heat-wave events' },
    { id: 'D-OM',   name: 'Open-Meteo / ERA5',                                    url: 'open-meteo.com',                      freq: 'Hourly',    res: '~1 km',           vars: 1,  category: 'Climate',       feeds: 'I5 ambient temperature proxy' },
    { id: 'IEEE-1', name: 'IEEE C57.91 / IEC 60076',                              url: 'standards.ieee.org',                  freq: 'Static',    res: 'Asset-level',     vars: 16, category: 'Standards',     feeds: 'I5 thermal model, B.3 Markov states' },
    { id: 'JRC',    name: 'JRC DSO Observatory',                                  url: 'ses.jrc.ec.europa.eu',                freq: 'Annual',    res: 'DSO-level',       vars: 2,  category: 'Grid',          feeds: 'R7 distrito-level cyber-exposure (secondary)' },
    { id: 'EEA',    name: 'EEA Air Quality e-Reporting',                           url: 'eea.europa.eu',                       freq: 'Annual',    res: '~1 km + station', vars: 3,  category: 'Environment',   feeds: 'I8 PM2.5, NO₂, O₃ corrosion' },
    { id: 'EURO',   name: 'Eurostat Energy Statistics',                            url: 'ec.europa.eu/eurostat',               freq: 'Annual',    res: 'NUTS2',           vars: 3,  category: 'Economic',      feeds: 'Energy poverty cross-validation' },
    { id: 'DESI',   name: 'DESI Digital Economy Index',                            url: 'digital-strategy.ec.europa.eu',       freq: 'Annual',    res: 'EU Regional',     vars: 2,  category: 'Socio-Econ',    feeds: 'R7 distrito-level cyber-exposure (primary DESI input)' },
    { id: 'IPMA',   name: 'IPMA (Instituto Português do Mar e da Atmosfera)',     url: 'ipma.pt',                             freq: 'Annual',    res: 'Distrito',        vars: 2,  category: 'Economic',      feeds: 'Seismic monitoring, climate data, wildfire alerts' },
    { id: 'APA',    name: 'APA (Agência Portuguesa do Ambiente)',                 url: 'apambiente.pt',                       freq: 'Annual',    res: 'Distrito',        vars: 1,  category: 'Environment',   feeds: 'Environmental risk indicators, flood zones' },
    { id: 'AT',     name: 'AT (Autoridade Tributária e Aduaneira)',               url: 'portaldasfinancas.gov.pt',            freq: 'Annual',    res: 'Distrito',        vars: 1,  category: 'Socio-Econ',    feeds: 'R3 fiscal enrichment, distrito revenue capacity' },
    { id: 'GFZ',    name: 'GFZ German Research Centre',                           url: 'gfz-potsdam.de',                     freq: 'Static',    res: '~5 km',           vars: 2,  category: 'Hazard',        feeds: 'Seismic hazard (475-yr PGA), geomagnetic risk' },
    { id: 'ICNF',   name: 'ICNF (Instituto da Conservação da Natureza)',          url: 'icnf.pt',                            freq: 'Annual',    res: 'Distrito',        vars: 1,  category: 'Hazard',        feeds: 'Wildfire risk zones, forest vulnerability' },
    { id: 'DGEEC',  name: 'DGEEC (Direção-Geral de Estatísticas)',               url: 'dgeec.mec.pt',                       freq: 'Annual',    res: 'Distrito',        vars: 2,  category: 'Socio-Econ',    feeds: 'R3 energy poverty, V_socio income vulnerability' },
    { id: 'E-REDES',name: 'E-REDES Open Data',                                    url: 'e-redes.pt',                         freq: 'Annual',    res: 'Distrito',        vars: 2,  category: 'Grid',          feeds: 'Grid investment, DSO quality statistics, smart metering' },
    { id: 'OMIE',   name: 'OMIE (Operador del Mercado Ibérico de Energía)',       url: 'omie.es',                            freq: 'Monthly',   res: 'MIBEL zone',      vars: 2,  category: 'Grid',          feeds: 'Cross-border flows, MIBEL price spreads' },
    { id: 'MOBI.E', name: 'MOBI.E (Rede de Mobilidade Elétrica)',                url: 'mobie.pt',                           freq: 'Quarterly', res: 'Concelho',        vars: 1,  category: 'Transition',    feeds: 'EV charging infrastructure data' },
    { id: 'ISO-9223', name: 'ISO 9223 Corrosion',                                 url: '(derived from EEA + APA)',           freq: 'Derived',   res: 'Distrito',        vars: 1,  category: 'Environment',   feeds: 'I8 corrosion classification' },
    { id: 'CCDR',   name: 'CCDR (Comissões de Coordenação Regional)',             url: 'ccdr.pt',                            freq: 'Annual',    res: 'Distrito',        vars: 2,  category: 'Socio-Econ',    feeds: 'R3 regional development gap, fiscal capacity' },
  ];

  // ─── 6 Components ────────────────────────────────────────
  const COMPONENTS = [
    {
      id: 'C', name: 'Continuity', weight: 0.30, color: '#941914',
      desc: 'Measures reliability and outage exposure — how often and how long power interruptions occur.',
      metrics: [
        { id: 'C1', name: 'Outage Duration', intra: 0.40, global: 0.120, norm: 'A (P5/P95)', source: 'ERSE / E-REDES', desc: 'Total annual interruption duration (SAIDI)' },
        { id: 'C2', name: 'Outage Count',    intra: 0.30, global: 0.090, norm: 'A (P5/P95)', source: 'ERSE / E-REDES', desc: 'Number of interruptions per year (SAIFI)' },
        { id: 'C3', name: 'MT Exceed Rate',  intra: 0.15, global: 0.045, norm: 'C (0–100%)', source: 'ERSE', desc: 'Percentage of time voltage exceeds regulation limits' },
        { id: 'C4', name: 'Planned Outages',  intra: 0.15, global: 0.045, norm: 'B (P5/P95)', source: 'ERSE Quality Report', desc: 'Duration of planned maintenance interruptions' },
      ]
    },
    {
      id: 'V', name: 'Voltage Quality', weight: 0.10, color: '#b8863a',
      desc: 'Captures voltage dip severity — short-duration voltage reductions that damage sensitive equipment.',
      metrics: [
        { id: 'V1', name: 'Severity-Weighted Dips', intra: 1.00, global: 0.100, norm: 'B (γ=0.50)', source: 'ERSE Quality Report', desc: 'V = N(V1_total × (1 + 0.50 × V2_severe_ratio))' },
      ]
    },
    {
      id: 'I', name: 'Infrastructure', weight: 0.25, color: '#5d8563',
      desc: 'Assesses physical grid condition — environmental exposure, asset density, and material degradation risks.',
      metrics: [
        { id: 'I1', name: 'Snow/Ice Risk (IRI)',     intra: 0.12, global: 0.030, norm: 'C (0–0.30)', source: 'Open-Meteo / ERSE IRI', desc: 'Climate risk index for snow and ice events', adaptive: true },
        { id: 'I2', name: 'Tree-Fall/Wildfire Risk',  intra: 0.09, global: 0.023, norm: 'C (0–0.30)', source: 'ICNF / IPMA', desc: 'Wildfire + tree-fall risk index (tri-hazard)', adaptive: true },
        { id: 'I3', name: 'Heat-Wave Risk (IRI)',     intra: 0.15, global: 0.038, norm: 'C (0–0.30)', source: 'Open-Meteo / IPMA', desc: 'Climate risk index for heat-wave events', adaptive: true },
        { id: 'I4', name: 'RTN Density',              intra: 0.12, global: 0.030, norm: 'B ↓inverted', source: 'REN Grid Data', desc: 'Transmission network density — higher = more resilient', inverted: true },
        { id: 'I5', name: 'Thermal Stress Proxy',     intra: 0.12, global: 0.030, norm: 'B (P5/P95)', source: 'IEEE C57.91', desc: 'Transformer thermal degradation based on ambient + load', isNew: true },
        { id: 'I6', name: 'Substation Density',       intra: 0.12, global: 0.030, norm: 'B ↓inverted', source: 'OSM / DGEG', desc: 'Substation density — higher = more backup capacity', inverted: true },
        { id: 'I7', name: 'Load Stress',              intra: 0.10, global: 0.025, norm: 'B (P5/P95)', source: 'REN / E-REDES', desc: 'Ratio of peak load to rated capacity', isNew: true },
        { id: 'I8', name: 'Air Quality Corrosion',    intra: 0.08, global: 0.020, norm: 'B (P5/P95)', source: 'APA / EEA / ISO 9223', desc: 'Air pollution corrosion risk for outdoor equipment', isNew: true },
        { id: 'I9', name: 'Hydrogeological Risk',     intra: 0.10, global: 0.025, norm: 'B (P5/P95)', source: 'LNEG / APA', desc: 'Flood and landslide territorial exposure', isNew: true },
      ]
    },
    {
      id: 'E', name: 'Economic', weight: 0.10, color: '#aa4234',
      desc: 'Quantifies economic impact of grid disruption — regulatory penalties and productivity losses.',
      metrics: [
        { id: 'E1', name: 'ERSE Penalties/User', intra: 0.55, global: 0.055, norm: 'B (P5/P95)', source: 'ERSE / E-REDES', desc: 'Per-user penalty costs from quality standard violations' },
        { id: 'E2', name: 'Productivity Loss Coefficient', intra: 0.45, global: 0.045, norm: 'C (bounded)', source: 'INE / Eurostat', desc: 'Weighted avg VoLL by local economic structure (β coefficient)' },
      ]
    },
    {
      id: 'S', name: 'Saturation', weight: 0.20, color: '#8e44ad',
      desc: 'Measures grid utilisation stress — generation/consumption imbalance, reverse power flow, and critical load classes.',
      metrics: [
        { id: 'S1', name: 'Distrito KPI (Gen/Consumption)', intra: 0.75, global: 0.150, norm: 'B* (Dimovski)', source: 'Dimovski et al.', desc: 'Distrito-level generation/consumption ratio — Dimovski breakpoints 1.29/7.78' },
        { id: 'S2', name: 'Reverse Power Flow',              intra: 0.125, global: 0.025, norm: 'D (categorical)', source: 'REN / E-REDES', desc: '{No RPF→0, >1%→0.5, >5%→1.0}', categorical: true },
        { id: 'S3', name: 'Criticality Class',                intra: 0.125, global: 0.025, norm: 'D (categorical)', source: 'ERSE', desc: '{Non-critical→0, Hospital/transport→0.5, Multiple critical→1.0}', categorical: true },
      ]
    },
    {
      id: 'T', name: 'Energy Transition', weight: 0.05, color: '#0e7490',
      desc: 'Captures energy-transition stress from distributed generation, output variability, and EV charging burden.',
      isNew: true,
      metrics: [
        { id: 'T1', name: 'DER Stress Index', intra: 1.00, global: 0.050, norm: 'B (composite)', source: 'DGEG + REN + MOBI.E', desc: 'Composite: α_DER(0.50) × N(DER_ratio) + α_VAR(0.30) × N(variability) + α_EV(0.20) × N(EV_load)', isNew: true,
          submetrics: [
            { id: 'DER_ratio', name: 'DER Penetration Ratio', weight: 0.50, source: 'DGEG Registry + REN', desc: 'DER capacity / peak load by distrito' },
            { id: 'DER_variability', name: 'DER Output Variability', weight: 0.30, source: 'ENTSO-E Transparency', desc: 'σ/μ of weekly DER output (coefficient of variation)' },
            { id: 'EV_load_ratio', name: 'EV Load Burden', weight: 0.20, source: 'MOBI.E + DGEG', desc: 'EV count × 7.4kW / transformer capacity' },
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
      sources: ['Copernicus CDS', 'Open-Meteo / IPMA'],
      isEnhanced: true
    },
    {
      id: 'R3', name: 'Consequence + Energy Poverty',
      range: '[0.70, 1.30]', type: 'Multiplicative',
      desc: 'Sigmoid function of population density, energy load, and socio-economic vulnerability. Enhanced with energy poverty, fiscal weakness, demographic shifts, elderly share, and flood zone enrichments.',
      formula: 'C_mult = 0.70 + 0.60 / (1 + e^(−4z)), z = 0.04·log₂(pop/pop_med) + 0.03·log₂(GWh/GWh_med) + 0.02·V_socio',
      sources: ['INE', 'DGEEC', 'AT', 'CCDR', 'LNEG / APA'],
      isEnhanced: true,
      enrichments: [
        { name: 'V_socio Fiscal Enrichment', effect: 'Up to +8% V_socio penalty', sources: 'AT + CCDR + ERSE' },
        { name: 'Demographic Shift Amplifier', effect: 'Up to +8% C_mult for population decline', sources: 'INE Demographics' },
        { name: 'Elderly Vulnerability', effect: '×[1.0, 1.10] for high elderly %', sources: 'INE Demographics' },
        { name: 'Flood Zone Amplifier', effect: 'Up to +15% C_mult for flood zones', sources: 'LNEG / APA' },
      ]
    },
    {
      id: 'R4', name: 'Graph-Theoretic Network Criticality',
      range: '[0.80, 1.35]', type: 'Multiplicative',
      desc: 'Combines degree centrality, betweenness centrality, and topological bridge detection from OSM power graph. Built from 10,191 substations and ~11,043 grid lines.',
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
      sources: ['ERSE Quality Report'],
      isNew: true
    },
    {
      id: 'R6b', name: 'Seismic Risk (Variable)',
      range: '[1.00, 1.70]', type: 'Multiplicative',
      desc: 'Variable seismic modifier by distrito — unlike constant-α countries. Portugal straddles the Azores–Gibraltar fracture zone with PGA ranging from 0.04g (Bragança) to 0.25g (Açores). α varies: Açores 0.70, Algarve 0.55, Lisboa 0.45.',
      formula: 'R6b_seismic = 1.0 + α(distrito) × clip(PGA / 0.30, 0, 1)',
      sources: ['LNEG', 'IPMA', 'GFZ'],
      isNew: true
    },
    {
      id: 'R7', name: 'Digital Readiness Proxy',
      range: '[0.99, 1.05]', type: 'Multiplicative',
      desc: 'Distrito-level continuous model based on DESI regional digital readiness scores, urban/rural adjustments, HV voltage class bonus, and per-substation noise. Unique values across 10,191 substations.',
      formula: 'R7_cyber(s) = clip( DESI_base(region) + urban_adj(distrito) + HV_bonus(voltage) + noise, 0.99, 1.05 )',
      sources: ['DESI / Eurostat', 'JRC DSO Observatory'],
      isNew: true,
      enrichments: [
        { name: 'Distrito-Level DESI Computation', effect: 'Continuous [0.99, 1.05] per substation', sources: 'DESI / Eurostat' },
      ]
    },
  ];

  // ─── Data Layers (11 layers, 95 variables) ─────────────────
  const DATA_LAYERS = [
    { id: 'A',   name: 'SSI v4.0.2 Resilience',        vars: 20, status: 'LIVE',        sources: 'ERSE · INE · Dimovski · DGEG · REN · MOBI.E · IPMA-W' },
    { id: 'B.1', name: 'Grid Telemetry: Open',         vars: 3,  status: 'LIVE',        sources: 'Open-Meteo / ERA5 · ERSE vintage · ERSE digitalization' },
    { id: 'B.2', name: 'Grid Telemetry: Proxy',        vars: 4,  status: 'LIVE',        sources: 'IEEE C57.91 · REN / E-REDES · ADENE · EN 50160' },
    { id: 'B.3', name: 'Grid Telemetry: Fuzzy/Markov', vars: 12, status: 'LIVE (MARKOV)', sources: 'IEEE/CIGRÉ standards · DGEG · EEA' },
    { id: 'C',   name: 'Socio-Economic',               vars: 9,  status: 'LIVE',        sources: 'INE · DGEEC · Eurostat · DESI · CCDR' },
    { id: 'D',   name: 'Environmental Hazards',         vars: 7,  status: 'LIVE',        sources: 'EEA · GFZ · LNEG · ISO 9223 · Copernicus CDS' },
    { id: 'E',   name: 'Portuguese Open Data',          vars: 8,  status: 'LIVE',        sources: 'ADENE · DGEG · AT · ERSE · REN' },
    { id: 'F',   name: 'Network Transitions',           vars: 12, status: 'LIVE (BAYESIAN)', sources: 'E-REDES history OR IEEE/CIGRÉ + priors' },
    { id: 'G',   name: 'Modifier Inputs',               vars: 3,  status: 'LIVE',        sources: 'ERSE Quality · OSM Power · JRC DSO', isNew: true },
    { id: 'H',   name: 'Network & Topology',            vars: 7,  status: 'LIVE',        sources: 'REN Grid Plan · GFZ · OSM · LNEG', isNew: true },
    { id: 'I',   name: 'Output Scores',                 vars: 7,  status: 'LIVE',        sources: 'Fleet Markov Chain · IEEE/CIGRÉ analysis', isNew: true },
  ];

  // ─── Processing Pipeline ──────────────────────────────────
  const PIPELINE = [
    { step: 1, name: 'Ingest',     desc: '95 variables from 28 verified data sources', icon: '①' },
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
    formula: 'R_final = soft_clip_upper(R_base × F_topo × C_mult × R6a_mult × R6b_seismic × Cyber_factor)',
    R_base: 'R_base = 0.30·C + 0.10·V + 0.25·I + 0.10·E + 0.20·S + 0.05·T',
    modifiers: {
      F_topo: 'graph_criticality(degree, BC, bridge) [R4]',
      C_mult: 'consequence_sigmoid(pop, load, V_socio) [R3]',
      R6a_mult: 'restoration_speed_sigmoid(CAIDI_local) [R6a]',
      R6b_seismic: 'seismic_risk(distrito_PGA, α) [R6b]',
      Cyber_factor: 'Distrito_DESI_cyber(region, distrito, voltage) [R7]'
    },
    soft_clip: 'if R_raw ≤ 1.00 → R_raw; if R_raw > 1.00 → 1.00 − 1/(1 + e^(20×(R_raw − 1.05)))'
  };

  // ─── Validation Framework ─────────────────────────────────
  const VALIDATION_CHECKS = [
    { check: 'Metropolitan–Rural convergence gap',  criterion: 'Metropolitan Lisboa R systematically lower than rural Interior Norte', status: 'verified' },
    { check: 'IRI-climate coherence',       criterion: 'I1 peaks Serra da Estrela · I3 peaks Alentejo/Algarve', status: 'verified' },
    { check: 'Saturation-RPF coherence',    criterion: 'S1 > 7.78 ↔ S2 > 5% agreement > 90%', status: 'verified' },
    { check: 'Ratio test',                  criterion: 'R(worst) / R(best) ≥ 5×', status: 'verified' },
    { check: 'Monotonicity',               criterion: 'Each metric worsening → R increases', status: 'verified' },
    { check: 'CI width quality signal',     criterion: 'Regional-only subs have wider CI', status: 'verified' },
    { check: 'T1-DER coherence',           criterion: 'T1 peaks in Alentejo solar-belt and Norte wind-coast', status: 'verified' },
    { check: 'R6 speed coherence',         criterion: 'R6a < 1.0 for Lisboa/Porto, R6a > 1.0 for rural Interior distritos', status: 'verified' },
    { check: 'Energy poverty gradient',    criterion: 'V_socio correlates with Interior-Litoral divide and rural deprivation', status: 'verified' },
    { check: 'R4 bridge identification',   criterion: 'is_bridge=1 subs have higher R than degree-matched non-bridges', status: 'verified' },
    { check: 'Climate trajectory direction', criterion: 'I3 trajectory > 1.0 in South, I1 stable in Northern mountains', status: 'verified' },
    { check: 'Weight sum invariant',        criterion: 'Σ w_component = 1.000 exactly', status: 'verified' },
    { check: 'R6b seismic gradient',       criterion: 'Açores/Algarve R6b >> Norte/Interior per LNEG zonation', status: 'verified' },
    { check: 'Markov risk coherence',      criterion: 'markov_risk_score positively correlates with asset age and outage rates', status: 'verified' },
    { check: 'Corrosion class gradient',   criterion: 'Coastal distritos (Algarve/Porto/Lisboa) C3–C5 > inland C1–C2', status: 'verified' },
  ];

  // ─── Changelog v3.4 → v4.0.2 ───────────────────────────────
  const CHANGELOG = [
    { id: 'F1', section: '§2, §4', change: 'New T component — Energy Transition Exposure (T1)', type: 'new' },
    { id: 'F2', section: '§5',     change: 'New R6a — Restoration Speed Modifier (CAIDI-based)', type: 'new' },
    { id: 'F3', section: '§5',     change: 'R3 enhanced — Energy Poverty Vulnerability (V_socio)', type: 'enhanced' },
    { id: 'F4', section: '§5',     change: 'R4 enhanced — Graph-theoretic betweenness + bridge detection', type: 'enhanced' },
    { id: 'F5', section: '§5',     change: 'R2 enhanced — Climate Trajectory (CMIP6 SSP2-4.5)', type: 'enhanced' },
    { id: 'F6', section: '§5',     change: 'R7 Digital Readiness — Distrito-level DESI model', type: 'enhanced' },
    { id: 'L1', section: '§2, §8', change: 'New I5, I7–I9 metrics — thermal, load, corrosion, hydrogeo', type: 'new' },
    { id: 'L2', section: '§6',     change: 'E2 Innovation Enrichment — HRST + startup density', type: 'enhanced' },
    { id: 'L3', section: '§5',     change: 'V_socio Fiscal Enrichment — AT + CCDR + energy price', type: 'enhanced' },
    { id: 'L4', section: '§5',     change: 'R3 Demographic Shift Amplifier — INE net migration', type: 'enhanced' },
    { id: 'L5', section: '§8, §12', change: '95/95 variables operational (100%). 28 data sources total.', type: 'data' },
    { id: 'G1', section: '§12',    change: 'd01 REN upgraded to real-time API — grid status data', type: 'data' },
    { id: 'G2', section: '§12',    change: 'd05 OSM upgraded to Overpass API — 10,191 real substations', type: 'data' },
    { id: 'G3', section: '§12',    change: 'd06 IPMA seismic monitoring — real-time PGA + historical catalog', type: 'data' },
    { id: 'G4', section: '§5',     change: 'R6b Seismic modifier — variable α by distrito (Açores 0.70, Algarve 0.55, Lisboa 0.45)', type: 'new' },
    { id: 'G5', section: '§12',    change: 'Network & Topology layer (H): 7 variables — REN grid plan, ring analysis', type: 'new' },
    { id: 'G6', section: '§12',    change: 'Output Scores layer (I): 7 variables — risk_score, ETTC, stationary probs', type: 'new' },
  ];

  // ─── Frequency Distribution ───────────────────────────────
  const FREQ_DISTRIBUTION = {
    Weekly: { count: 2, sources: ['OSM Overpass', 'Open-Meteo/ERA5'] },
    Monthly: { count: 2, sources: ['DGEG Registry', 'OMIE MIBEL'] },
    Quarterly: { count: 2, sources: ['MOBI.E', 'DGEG Licensing'] },
    Annual: { count: 15, sources: ['ERSE', 'INE', 'DGEEC', 'E-REDES', 'ADENE', 'AT', 'EEA', 'Eurostat', 'DESI', 'CCDR', 'IPMA', 'APA', 'ICNF', 'JRC', 'REN Annual'] },
    Static: { count: 7, sources: ['Dimovski', 'IEEE/IEC/CIGRÉ', 'Copernicus CMIP6', 'GFZ', 'LNEG', 'ISO 9223', 'ENTSO-E'] },
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
      sources: 28,
      substations: 10191,
      powerLines: 11043,
      mcIterations: 10000,
      departements: 20,
      regions: 7
    }
  };
})();
// Compatibility alias
window.SSI_METADATA = window.SSIMetadata;
