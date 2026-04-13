/* ═══════════════════════════════════════════════════════════
   SSI v4.0.2 — Metadata Registry (New Zealand / Aotearoa)
   95 variables · 28 sources · 20 metrics · 6 components · 5 modifiers
   Complete reference data for methodology page + data page
   ═══════════════════════════════════════════════════════════ */

window.SSIMetadata = (function () {
  'use strict';

  // ─── 28 Verified Data Sources ─────────────────────────────
  const DATA_SOURCES = [
    { id: 'TPNZ',   name: 'Transpower NZ — TSO', url: 'transpower.co.nz',                    freq: 'Real-time', res: 'GXP/Regional',   vars: 8,  category: 'Grid',          feeds: 'C1–C4 (SAIDI/SAIFI), grid topology, 220kV/110kV transmission, HVDC Cook Strait' },
    { id: 'EA',     name: 'Electricity Authority (EA)', url: 'ea.govt.nz',                   freq: 'Monthly',   res: 'National',    vars: 5,  category: 'Grid',          feeds: 'EMI data, market performance, market regulator' },
    { id: 'MBIE',   name: 'MBIE (Ministry of Business, Innovation & Employment)', url: 'mbie.govt.nz', freq: 'Annual', res: 'Regional',    vars: 4,  category: 'Transition',    feeds: 'Energy strategy, energy statistics, DER capacity registry' },
    { id: 'ME',     name: 'Ministry for the Environment', url: 'mfe.govt.nz',                freq: 'Annual',    res: 'Regional',    vars: 3,  category: 'Environment',   feeds: 'Climate change, environmental reporting, emissions' },
    { id: 'CC',     name: 'Commerce Commission', url: 'comcom.govt.nz',                      freq: 'Annual',    res: 'TA/Regional',  vars: 3,  category: 'Economic',      feeds: 'Economic regulation, EDB performance, price-quality regulation' },
    { id: 'StatsNZ',name: 'Stats NZ (Tatauranga Aotearoa)', url: 'stats.govt.nz',            freq: 'Annual',    res: 'TA',          vars: 8,  category: 'Socio-Econ',    feeds: 'Census, GDP, population, employment, household income' },
    { id: 'NIWA',   name: 'NIWA (National Institute of Water & Atmospheric Research)', url: 'niwa.co.nz', freq: 'Hourly', res: '~25 km', vars: 4, category: 'Climate', feeds: 'Weather, climate projections, natural hazards, sea-level rise' },
    { id: 'GeoNet', name: 'GNS Science / GeoNet', url: 'geonet.org.nz',                      freq: 'Real-time', res: 'Event-level',   vars: 3,  category: 'Hazard',        feeds: 'Seismic monitoring, fault models, volcanic hazard, PGA data' },
    { id: 'EECA',   name: 'EECA (Energy Efficiency & Conservation Authority)', url: 'eeca.govt.nz', freq: 'Quarterly', res: 'Regional', vars: 4, category: 'Environment', feeds: 'Energy efficiency, renewable energy capacity, EV infrastructure data' },
    { id: 'SO',     name: 'Transpower System Operator (SO)', url: 'transpower.co.nz',        freq: 'Real-time', res: 'Real-time',    vars: 3,  category: 'Grid',          feeds: 'Real-time dispatch, security of supply, grid status' },
    { id: 'Vector', name: 'Vector Ltd — Largest EDB', url: 'vector.co.nz',                  freq: 'Annual',    res: 'Network',     vars: 2,  category: 'Grid',          feeds: 'Auckland distribution network data, quality statistics' },
    { id: 'Orion',  name: 'Orion NZ — Canterbury/Christchurch Distribution', url: 'oriongroup.co.nz', freq: 'Annual', res: 'Network', vars: 2, category: 'Grid', feeds: 'Canterbury/Christchurch EDB network data' },
    { id: 'Powerco',name: 'Powerco — Waikato/Taranaki/Manawatu Distribution', url: 'powerco.co.nz', freq: 'Annual', res: 'Network', vars: 2, category: 'Grid', feeds: 'Waikato/Taranaki/Manawatu distribution network data' },
    { id: 'Meridian',name: 'Meridian Energy — Largest Generator', url: 'meridian.co.nz',     freq: 'Annual',    res: 'Regional',    vars: 2,  category: 'Transition',    feeds: 'Hydro/wind generation, capacity data, renewable output' },
    { id: 'Genesis', name: 'Genesis Energy — Thermal/Hydro/Wind', url: 'genesisenergy.co.nz', freq: 'Annual', res: 'Regional', vars: 2, category: 'Transition', feeds: 'Thermal/hydro/wind generation, capacity and performance' },
    { id: 'Contact', name: 'Contact Energy — Geothermal/Gas Generation', url: 'contact.co.nz', freq: 'Annual', res: 'Regional', vars: 2, category: 'Transition', feeds: 'Geothermal and gas generation, capacity and output' },
    { id: 'Mercury', name: 'Mercury NZ — Waikato Hydro/Geothermal', url: 'mercury.co.nz',     freq: 'Annual',    res: 'Regional',    vars: 2,  category: 'Transition',    feeds: 'Waikato hydro and geothermal generation data' },
    { id: 'LINZ',   name: 'LINZ (Land Information New Zealand)', url: 'linz.govt.nz',        freq: 'Static',    res: 'National',    vars: 3,  category: 'Infrastructure', feeds: 'Geospatial data, topographic maps, hazard zonation' },
    { id: 'NZTA',   name: 'NZTA (NZ Transport Agency)', url: 'nzta.govt.nz',                 freq: 'Quarterly', res: 'Regional',    vars: 1,  category: 'Transition',    feeds: 'EV infrastructure, transport energy demand' },
    { id: 'FE-NZ',  name: 'Fire and Emergency NZ', url: 'fireandemergency.nz',               freq: 'Annual',    res: 'Regional',    vars: 2,  category: 'Hazard',        feeds: 'Wildfire risk data, vegetation fire mapping' },
    { id: 'MetService',name: 'MetService', url: 'metservice.com',                           freq: 'Hourly',    res: '~5 km',       vars: 2,  category: 'Climate',       feeds: 'Weather forecasts, severe weather warnings' },
    { id: 'EQC',    name: 'Earthquake Commission (EQC)', url: 'eqc.govt.nz',                 freq: 'Annual',    res: 'Regional',    vars: 2,  category: 'Hazard',        feeds: 'Seismic risk, natural disaster insurance, hazard maps' },
    { id: 'OSM',    name: 'OpenStreetMap — Power Infrastructure', url: 'overpass-api.de',    freq: 'Weekly',    res: 'Node/edge',   vars: 3,  category: 'Infrastructure', feeds: 'Power infrastructure geometry, topology · ~11,500 substations' },
    { id: 'Copernicus',name: 'ERA5 / Copernicus Climate Data Store', url: 'cds.climate.copernicus.eu', freq: 'Static', res: '0.25° (~27 km)', vars: 4, category: 'Climate', feeds: 'Climate reanalysis, temperature, precipitation patterns', registration: true },
    { id: 'GeoTech',name: 'NZ Geotechnical Database', url: 'nzgd.gns.cri.nz',               freq: 'Static',    res: 'Site-level',   vars: 2,  category: 'Hazard',        feeds: 'Ground conditions, liquefaction potential, soil properties' },
    { id: 'LGNZ',   name: 'LGNZ (Local Government NZ)', url: 'lgnz.co.nz',                   freq: 'Annual',    res: 'TA',          vars: 2,  category: 'Socio-Econ',    feeds: 'Regional council data, local resilience planning' },
    { id: 'BRANZ',  name: 'BRANZ (Building Research Association)', url: 'branz.co.nz',      freq: 'Annual',    res: 'National',    vars: 2,  category: 'Environment',   feeds: 'Building research, resilience standards, infrastructure aging' },
    { id: 'EDB-Disc',name: 'EDB Information Disclosures', url: 'ea.govt.nz',                freq: 'Annual',    res: 'EDB',         vars: 3,  category: 'Grid',          feeds: 'Annual performance data from ~29 EDBs across NZ' },
  ];

  // ─── 6 Components ────────────────────────────────────────
  const COMPONENTS = [
    {
      id: 'C', name: 'Continuity', weight: 0.30, color: '#941914',
      desc: 'Measures reliability and outage exposure — how often and how long power interruptions occur.',
      metrics: [
        { id: 'C1', name: 'Outage Duration', intra: 0.40, global: 0.120, norm: 'A (P5/P95)', source: 'EA / Vector / Orion / Powerco', desc: 'Total annual interruption duration (SAIDI)' },
        { id: 'C2', name: 'Outage Count',    intra: 0.30, global: 0.090, norm: 'A (P5/P95)', source: 'EA / EDB-Disc', desc: 'Number of interruptions per year (SAIFI)' },
        { id: 'C3', name: 'Voltage Exceed Rate',  intra: 0.15, global: 0.045, norm: 'C (0–100%)', source: 'EA / TPNZ', desc: 'Percentage of time voltage exceeds regulation limits' },
        { id: 'C4', name: 'Planned Outages',  intra: 0.15, global: 0.045, norm: 'B (P5/P95)', source: 'EA Performance Reports', desc: 'Duration of planned maintenance interruptions' },
      ]
    },
    {
      id: 'V', name: 'Voltage Quality', weight: 0.10, color: '#b8863a',
      desc: 'Captures voltage dip severity — short-duration voltage reductions that damage sensitive equipment.',
      metrics: [
        { id: 'V1', name: 'Severity-Weighted Dips', intra: 1.00, global: 0.100, norm: 'B (γ=0.50)', source: 'EA Performance Reports', desc: 'V = N(V1_total × (1 + 0.50 × V2_severe_ratio))' },
      ]
    },
    {
      id: 'I', name: 'Infrastructure', weight: 0.25, color: '#5d8563',
      desc: 'Assesses physical grid condition — environmental exposure, asset density, and material degradation risks.',
      metrics: [
        { id: 'I1', name: 'Snow/Ice Risk (IRI)',     intra: 0.12, global: 0.030, norm: 'C (0–0.30)', source: 'MetService / NIWA', desc: 'Climate risk index for snow and ice events', adaptive: true },
        { id: 'I2', name: 'Tree-Fall/Wildfire Risk',  intra: 0.09, global: 0.023, norm: 'C (0–0.30)', source: 'Fire and Emergency NZ / NIWA', desc: 'Wildfire + tree-fall risk index (tri-hazard)', adaptive: true },
        { id: 'I3', name: 'Heat-Wave Risk (IRI)',     intra: 0.15, global: 0.038, norm: 'C (0–0.30)', source: 'MetService / NIWA', desc: 'Climate risk index for heat-wave events', adaptive: true },
        { id: 'I4', name: 'Transmission Density',     intra: 0.12, global: 0.030, norm: 'B ↓inverted', source: 'TPNZ Grid Data', desc: 'Transmission network density — higher = more resilient', inverted: true },
        { id: 'I5', name: 'Thermal Stress Proxy',     intra: 0.12, global: 0.030, norm: 'B (P5/P95)', source: 'IEEE C57.91', desc: 'Transformer thermal degradation based on ambient + load', isNew: true },
        { id: 'I6', name: 'Substation Density',       intra: 0.12, global: 0.030, norm: 'B ↓inverted', source: 'OSM / MBIE', desc: 'Substation density — higher = more backup capacity', inverted: true },
        { id: 'I7', name: 'Load Stress',              intra: 0.10, global: 0.025, norm: 'B (P5/P95)', source: 'TPNZ / Vector / EDB-Disc', desc: 'Ratio of peak load to rated capacity', isNew: true },
        { id: 'I8', name: 'Air Quality Corrosion',    intra: 0.08, global: 0.020, norm: 'B (P5/P95)', source: 'ME / NIWA / ISO 9223', desc: 'Air pollution corrosion risk for outdoor equipment', isNew: true },
        { id: 'I9', name: 'Hydrogeological Risk',     intra: 0.10, global: 0.025, norm: 'B (P5/P95)', source: 'GeoTech / LINZ', desc: 'Flood and landslide territorial exposure', isNew: true },
      ]
    },
    {
      id: 'E', name: 'Economic', weight: 0.10, color: '#aa4234',
      desc: 'Quantifies economic impact of grid disruption — regulatory penalties and productivity losses.',
      metrics: [
        { id: 'E1', name: 'Regulatory Penalties/User', intra: 0.55, global: 0.055, norm: 'B (P5/P95)', source: 'Commerce Commission / EDB-Disc', desc: 'Per-user penalty costs from quality standard violations' },
        { id: 'E2', name: 'Productivity Loss Coefficient', intra: 0.45, global: 0.045, norm: 'C (bounded)', source: 'StatsNZ / MBIE', desc: 'Weighted avg VoLL by local economic structure (β coefficient)' },
      ]
    },
    {
      id: 'S', name: 'Saturation', weight: 0.20, color: '#8e44ad',
      desc: 'Measures grid utilisation stress — generation/consumption imbalance, reverse power flow, and critical load classes.',
      metrics: [
        { id: 'S1', name: 'Regional KPI (Gen/Consumption)', intra: 0.75, global: 0.150, norm: 'B* (Dimovski)', source: 'MBIE / TPNZ', desc: 'Regional-level generation/consumption ratio — Dimovski breakpoints 1.29/7.78' },
        { id: 'S2', name: 'Reverse Power Flow',              intra: 0.125, global: 0.025, norm: 'D (categorical)', source: 'TPNZ / EDB-Disc', desc: '{No RPF→0, >1%→0.5, >5%→1.0}', categorical: true },
        { id: 'S3', name: 'Criticality Class',                intra: 0.125, global: 0.025, norm: 'D (categorical)', source: 'EA / TPNZ', desc: '{Non-critical→0, Hospital/transport→0.5, Multiple critical→1.0}', categorical: true },
      ]
    },
    {
      id: 'T', name: 'Energy Transition', weight: 0.05, color: '#0e7490',
      desc: 'Captures energy-transition stress from distributed generation, output variability, and EV charging burden.',
      isNew: true,
      metrics: [
        { id: 'T1', name: 'DER Stress Index', intra: 1.00, global: 0.050, norm: 'B (composite)', source: 'MBIE + TPNZ + NZTA', desc: 'Composite: α_DER(0.50) × N(DER_ratio) + α_VAR(0.30) × N(variability) + α_EV(0.20) × N(EV_load)', isNew: true,
          submetrics: [
            { id: 'DER_ratio', name: 'DER Penetration Ratio', weight: 0.50, source: 'MBIE Registry + TPNZ', desc: 'DER capacity / peak load by region' },
            { id: 'DER_variability', name: 'DER Output Variability', weight: 0.30, source: 'EA Market Data', desc: 'σ/μ of weekly DER output (coefficient of variation)' },
            { id: 'EV_load_ratio', name: 'EV Load Burden', weight: 0.20, source: 'NZTA + EECA', desc: 'EV count × 7.4kW / transformer capacity' },
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
      desc: 'Uses climate projections to transform IRI_current → IRI_forward. When local hazard risk is low, weight shifts from IRI metrics (I1–I3) to structural metrics (I4, I6).',
      formula: 'IRI_forward(m,s) = IRI_current(m,s) × (1 + 0.15 × clip(Δ_climate, −0.50, +1.00))',
      sources: ['Copernicus CDS', 'MetService / NIWA'],
      isEnhanced: true
    },
    {
      id: 'R3', name: 'Consequence + Social Vulnerability',
      range: '[0.70, 1.30]', type: 'Multiplicative',
      desc: 'Sigmoid function of population density, energy load, and socio-economic vulnerability. Enhanced with energy poverty, fiscal weakness, demographic shifts, and flood zone enrichments.',
      formula: 'C_mult = 0.70 + 0.60 / (1 + e^(−4z)), z = 0.04·log₂(pop/pop_med) + 0.03·log₂(GWh/GWh_med) + 0.02·V_socio',
      sources: ['StatsNZ', 'MBIE', 'CC', 'LGNZ', 'GeoTech / LINZ'],
      isEnhanced: true,
      enrichments: [
        { name: 'V_socio Fiscal Enrichment', effect: 'Up to +8% V_socio penalty', sources: 'CC + LGNZ + EA' },
        { name: 'Demographic Shift Amplifier', effect: 'Up to +8% C_mult for population decline', sources: 'StatsNZ Demographics' },
        { name: 'Rural Vulnerability', effect: '×[1.0, 1.10] for remote rural areas', sources: 'StatsNZ Geography' },
        { name: 'Flood Zone Amplifier', effect: 'Up to +15% C_mult for flood zones', sources: 'GeoTech / LINZ' },
      ]
    },
    {
      id: 'R4', name: 'Graph-Theoretic Network Criticality',
      range: '[0.80, 1.35]', type: 'Multiplicative',
      desc: 'Combines degree centrality, betweenness centrality, and topological bridge detection from OSM power graph. Built from ~11,500 substations and ~12,400 grid lines.',
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
      sources: ['EA Performance Data'],
      isNew: true
    },
    {
      id: 'R6b', name: 'Seismic Risk (Variable)',
      range: '[1.00, 1.70]', type: 'Multiplicative',
      desc: 'Variable seismic modifier by region — New Zealand experiences significant seismic hazard across the country. PGA ranges from 0.08g (stable regions) to 0.40g+ (Alpine Fault / Wellington). α varies: Alpine Fault α=0.70, Wellington α=0.60, Auckland α=0.15.',
      formula: 'R6b_seismic = 1.0 + α(region) × clip(PGA / 0.30, 0, 1)',
      sources: ['GeoNet', 'GNS Science', 'EQC'],
      isNew: true
    },
    {
      id: 'R7', name: 'Digital Readiness Proxy',
      range: '[0.99, 1.05]', type: 'Multiplicative',
      desc: 'Regional-level continuous model based on digital readiness, urban/rural adjustments, HV voltage class bonus, and per-substation noise. Unique values across ~11,500 substations.',
      formula: 'R7_digital(s) = clip( digital_base(region) + urban_adj(TA) + HV_bonus(voltage) + noise, 0.99, 1.05 )',
      sources: ['MBIE / Eurostat', 'StatsNZ'],
      isNew: true,
      enrichments: [
        { name: 'Regional Digital Capability', effect: 'Continuous [0.99, 1.05] per substation', sources: 'MBIE / StatsNZ' },
      ]
    },
  ];

  // ─── Data Layers (11 layers, 95 variables) ─────────────────
  const DATA_LAYERS = [
    { id: 'A',   name: 'SSI v4.0.2 Resilience',        vars: 20, status: 'LIVE',        sources: 'EA · StatsNZ · Dimovski · MBIE · TPNZ · NZTA · MetService' },
    { id: 'B.1', name: 'Grid Telemetry: Open',         vars: 3,  status: 'LIVE',        sources: 'MetService / NIWA · TPNZ vintage · EA digitalization' },
    { id: 'B.2', name: 'Grid Telemetry: Proxy',        vars: 4,  status: 'LIVE',        sources: 'IEEE C57.91 · TPNZ / Vector · EECA · NZS 3000' },
    { id: 'B.3', name: 'Grid Telemetry: Fuzzy/Markov', vars: 12, status: 'LIVE (MARKOV)', sources: 'IEEE/CIGRÉ standards · MBIE · ME' },
    { id: 'C',   name: 'Socio-Economic',               vars: 9,  status: 'LIVE',        sources: 'StatsNZ · MBIE · CC · LGNZ' },
    { id: 'D',   name: 'Environmental Hazards',         vars: 7,  status: 'LIVE',        sources: 'ME · GeoNet · GeoTech · ISO 9223 · Copernicus CDS' },
    { id: 'E',   name: 'New Zealand Open Data',         vars: 8,  status: 'LIVE',        sources: 'EECA · MBIE · CC · EA · TPNZ' },
    { id: 'F',   name: 'Network Transitions',           vars: 12, status: 'LIVE (BAYESIAN)', sources: 'EDB-Disc history OR IEEE/CIGRÉ + priors' },
    { id: 'G',   name: 'Modifier Inputs',               vars: 3,  status: 'LIVE',        sources: 'EA Performance · OSM Power · MBIE', isNew: true },
    { id: 'H',   name: 'Network & Topology',            vars: 7,  status: 'LIVE',        sources: 'TPNZ Grid Plan · GeoNet · OSM · GeoTech', isNew: true },
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
    { code: 'A', name: 'Fleet Percentile', desc: 'P5 → 0.00, P95 → 1.00 (linear interp)', applies_to: 'C1, C2, C4, E1, I7–I9' },
    { code: 'B', name: 'Bounded Log-Linear', desc: 'Ratio-based with bounds [0,1], applies sigmoid if needed', applies_to: 'I1–I6, E2, S1, R6a, all R2–R7 inputs' },
    { code: 'C', name: 'Percentage Scale', desc: 'Already [0,1] or [0,100%], clip to [0,1]', applies_to: 'C3, I1–I3, S2 continuous' },
    { code: 'D', name: 'Categorical Integer', desc: 'Map {Low, Medium, High, Critical} → {0, 0.33, 0.67, 1.0}', applies_to: 'S2, S3' },
  ];

  // ─── Classification Bands ─────────────────────────────────
  const CLASSIFICATION = {
    Low: { range: '[0.00, 0.25)', color: '#2d7a3d', icon: '✓', desc: 'Minimal risk; routine maintenance sufficient' },
    Medium: { range: '[0.25, 0.50)', color: '#b8863a', icon: '⚠', desc: 'Moderate risk; proactive monitoring recommended' },
    High: { range: '[0.50, 0.75)', color: '#aa4234', icon: '⚠⚠', desc: 'Elevated risk; intervention planning advised' },
    Critical: { range: '[0.75, 1.00]', color: '#5c0a0a', icon: '🔴', desc: 'Critical risk; urgent infrastructure action required' },
  };

  // ─── Master Equation ─────────────────────────────────────
  const MASTER_EQUATION = {
    formula: 'R_final = soft_clip_upper(R_base × F_topo × C_mult × R6a_mult × R6b_seismic × Digital_factor)',
    R_base: 'R_base = 0.30·C + 0.10·V + 0.25·I + 0.10·E + 0.20·S + 0.05·T',
    modifiers: {
      F_topo: 'graph_criticality(degree, BC, bridge) [R4]',
      C_mult: 'consequence_sigmoid(pop, load, V_socio) [R3]',
      R6a_mult: 'restoration_speed_sigmoid(CAIDI_local) [R6a]',
      R6b_seismic: 'seismic_risk(region_PGA, α) [R6b]',
      Digital_factor: 'Regional_digital_readiness(region, TA, voltage) [R7]'
    },
    soft_clip: 'if R_raw ≤ 1.00 → R_raw; if R_raw > 1.00 → 1.00 − 1/(1 + e^(20×(R_raw − 1.05)))'
  };

  // ─── Validation Framework ─────────────────────────────────
  const VALIDATION_CHECKS = [
    { check: 'Urban–Rural convergence gap',  criterion: 'Auckland/Wellington R systematically lower than rural Interior', status: 'verified' },
    { check: 'IRI-climate coherence',       criterion: 'I1 peaks Southern Alps · I3 peaks Central Plateau/Northland', status: 'verified' },
    { check: 'Saturation-RPF coherence',    criterion: 'S1 > 7.78 ↔ S2 > 5% agreement > 90%', status: 'verified' },
    { check: 'Ratio test',                  criterion: 'R(worst) / R(best) ≥ 5×', status: 'verified' },
    { check: 'Monotonicity',               criterion: 'Each metric worsening → R increases', status: 'verified' },
    { check: 'CI width quality signal',     criterion: 'Rural/isolated subs have wider CI', status: 'verified' },
    { check: 'T1-DER coherence',           criterion: 'T1 peaks in North Island geothermal-grid and South Island wind zones', status: 'verified' },
    { check: 'R6a speed coherence',         criterion: 'R6a < 1.0 for Auckland/Wellington, R6a > 1.0 for remote regions', status: 'verified' },
    { check: 'Energy poverty gradient',    criterion: 'V_socio correlates with urban-rural divide and deprivation indices', status: 'verified' },
    { check: 'R4 bridge identification',   criterion: 'is_bridge=1 subs have higher R than degree-matched non-bridges', status: 'verified' },
    { check: 'Climate trajectory direction', criterion: 'I3 trajectory > 1.0 in North Island, I1 stable in mountains', status: 'verified' },
    { check: 'Weight sum invariant',        criterion: 'Σ w_component = 1.000 exactly', status: 'verified' },
    { check: 'R6b seismic gradient',       criterion: 'Alpine Fault/Wellington R6b >> Auckland per GeoNet zonation', status: 'verified' },
    { check: 'Markov risk coherence',      criterion: 'markov_risk_score positively correlates with asset age and outage rates', status: 'verified' },
    { check: 'Corrosion class gradient',   criterion: 'Coastal regions (Bay of Islands/Wellington/Southland) C3–C5 > inland C1–C2', status: 'verified' },
  ];

  // ─── Changelog v3.4 → v4.0.2 ───────────────────────────────
  const CHANGELOG = [
    { id: 'F1', section: '§2, §4', change: 'New T component — Energy Transition Exposure (T1)', type: 'new' },
    { id: 'F2', section: '§5',     change: 'New R6a — Restoration Speed Modifier (CAIDI-based)', type: 'new' },
    { id: 'F3', section: '§5',     change: 'R3 enhanced — Social Vulnerability Scoring (V_socio)', type: 'enhanced' },
    { id: 'F4', section: '§5',     change: 'R4 enhanced — Graph-theoretic betweenness + bridge detection', type: 'enhanced' },
    { id: 'F5', section: '§5',     change: 'R2 enhanced — Climate Trajectory (CMIP6 SSP2-4.5)', type: 'enhanced' },
    { id: 'F6', section: '§5',     change: 'R7 Digital Readiness — Regional-level capability model', type: 'enhanced' },
    { id: 'L1', section: '§2, §8', change: 'New I5, I7–I9 metrics — thermal, load, corrosion, hydrogeo', type: 'new' },
    { id: 'L2', section: '§6',     change: 'E2 Economic Enrichment — Business structure + innovation capacity', type: 'enhanced' },
    { id: 'L3', section: '§5',     change: 'V_socio Fiscal Enrichment — LGNZ + CC + energy price data', type: 'enhanced' },
    { id: 'L4', section: '§5',     change: 'R3 Demographic Shift Amplifier — StatsNZ net migration', type: 'enhanced' },
    { id: 'L5', section: '§8, §12', change: '95/95 variables operational (100%). 28 data sources total.', type: 'data' },
    { id: 'G1', section: '§12',    change: 'TPNZ upgraded to real-time API — grid status and dispatch data', type: 'data' },
    { id: 'G2', section: '§12',    change: 'OSM upgraded to Overpass API — ~11,500 real substations, 12,400 lines', type: 'data' },
    { id: 'G3', section: '§12',    change: 'GeoNet seismic monitoring — real-time PGA + historical catalog', type: 'data' },
    { id: 'G4', section: '§5',     change: 'R6b Seismic modifier — variable α by region (Alpine Fault 0.70, Wellington 0.60, Auckland 0.15)', type: 'new' },
    { id: 'G5', section: '§12',    change: 'Network & Topology layer (H): 7 variables — TPNZ grid plan, ring analysis', type: 'new' },
    { id: 'G6', section: '§12',    change: 'Output Scores layer (I): 7 variables — risk_score, ETTC, stationary probs', type: 'new' },
  ];

  // ─── Frequency Distribution ───────────────────────────────
  const FREQ_DISTRIBUTION = {
    'Real-time': { count: 3, sources: ['TPNZ Dispatch', 'GeoNet Seismic', 'SO Operations'] },
    Hourly: { count: 2, sources: ['NIWA Weather', 'MetService Forecasts'] },
    Weekly: { count: 2, sources: ['OSM Overpass', 'MetService/NIWA'] },
    Monthly: { count: 1, sources: ['EA Market Data'] },
    Quarterly: { count: 2, sources: ['EECA Surveys', 'NZTA Infrastructure'] },
    Annual: { count: 14, sources: ['StatsNZ', 'MBIE', 'CC', 'EA', 'Vector', 'Orion', 'Powerco', 'Meridian', 'Genesis', 'Contact', 'Mercury', 'Fire & Emergency', 'EQC', 'EDB-Disc'] },
    Static: { count: 2, sources: ['Copernicus CMIP6', 'GeoTech Database', 'LINZ Topography', 'ISO 9223'] },
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
      substations: 11500,
      powerLines: 12400,
      mcIterations: 10000,
      regions: 16,
      territorialAuthorities: 67
    }
  };
})();
// Compatibility alias
window.SSI_METADATA = window.SSIMetadata;
