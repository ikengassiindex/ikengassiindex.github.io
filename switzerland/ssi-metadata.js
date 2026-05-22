/* ═══════════════════════════════════════════════════════════
   SSI v4.0.2 — Metadata Registry (Switzerland)
   95 variables · 35 sources · 20 metrics · 6 components · 7 modifiers
   26 Kantone · 148 districts · 2,148 municipalities · TSO: Swissgrid
   KB §53 Switzerland calibration (Session 21)
   ═══════════════════════════════════════════════════════════ */

window.SSIMetadata = (function () {
  'use strict';

  // ─── 35 Verified Data Sources (Switzerland) ─────────────────
  const DATA_SOURCES = [
    { id: 'ELCOM',  name: 'ElCom (Federal Electricity Commission)',  url: 'elcom.admin.ch',                 freq: 'Annual',    res: 'Kanton / DSO',   vars: 8,  category: 'Grid',          feeds: 'C1–C4 (SAIDI/SAIFI), R6a restoration, quality regulation' },
    { id: 'SGRID',  name: 'Swissgrid (single TSO)',                   url: 'swissgrid.ch',                   freq: 'Monthly',   res: 'Control area',   vars: 4,  category: 'Grid',          feeds: 'Transmission flows, 41 cross-border lines, congestion' },
    { id: 'BFS',    name: 'BFS / OFS (Federal Statistical Office)',   url: 'bfs.admin.ch',                   freq: 'Annual',    res: 'Kanton / Gemeinde', vars: 8,  category: 'Socio-Econ',  feeds: 'R3 population, GDP, fiscal capacity, elderly share' },
    { id: 'PRONOVO', name: 'Pronovo (Guarantees of Origin Registry)', url: 'pronovo.ch',                      freq: 'Monthly',   res: 'Substation',     vars: 3,  category: 'Transition',    feeds: 'T1 DER capacity, hydropower, solar, wind registry' },
    { id: 'SED',    name: 'SED Swiss Seismological Service',          url: 'seismo.ethz.ch',                 freq: 'Continuous',res: '200+ stations',  vars: 3,  category: 'Hazard',        feeds: 'R6b seismic PGA 475-yr, alpine seismicity (Wallis)' },
    { id: 'OSM',    name: 'OSM Power Infrastructure',                 url: 'overpass-api.de',                freq: 'Weekly',    res: 'Node/edge',      vars: 3,  category: 'Infrastructure', feeds: 'R4 graph topology, BC, bridges · ~1,250 substations' },
    { id: 'COPER',  name: 'Copernicus CDS / ERA5',                    url: 'cds.climate.copernicus.eu',      freq: 'Static',    res: '~25 km',         vars: 4,  category: 'Climate',       feeds: 'R2 Δ_climate (I1–I3), CMIP6 RCP4.5', registration: true },
    { id: 'ENTSE',  name: 'ENTSO-E Transparency (CH observer)',       url: 'transparency.entsoe.eu',         freq: 'Hourly',    res: 'CH bidding zone',vars: 2,  category: 'Transition',    feeds: 'T1 DER variability, cross-border bilateral flows', registration: true },
    { id: 'BAFU',   name: 'BAFU Federal Office for the Environment',  url: 'bafu.admin.ch',                  freq: 'Annual',    res: 'Kanton / station',vars: 4, category: 'Environment',   feeds: 'I8 air quality, PM2.5, NO₂, O₃ corrosion · R6c flood' },
    { id: 'METEO',  name: 'MeteoSwiss',                               url: 'meteoschweiz.admin.ch',          freq: 'Daily',     res: '~2 km',          vars: 3,  category: 'Climate',       feeds: 'I1–I3 snow/storms/heatwaves, ERA5 calibration' },
    { id: 'SWTOP',  name: 'swisstopo (Federal Office of Topography)', url: 'swisstopo.admin.ch',             freq: 'Static',    res: '1:25,000',       vars: 3,  category: 'Hazard',        feeds: 'I9 hydrogeological, GHK flood maps, alpine terrain' },
    { id: 'D-OM',   name: 'Open-Meteo / ERA5',                        url: 'open-meteo.com',                 freq: 'Hourly',    res: '~1 km',          vars: 1,  category: 'Climate',       feeds: 'I5 ambient temperature proxy' },
    { id: 'IEEE-1', name: 'IEEE C57.91 / IEC 60076',                  url: 'standards.ieee.org',             freq: 'Static',    res: 'Asset-level',    vars: 16, category: 'Standards',     feeds: 'I5 thermal model, B.3 Markov states' },
    { id: 'JRC',    name: 'JRC DSO Observatory',                      url: 'ses.jrc.ec.europa.eu',           freq: 'Annual',    res: 'DSO-level',      vars: 2,  category: 'Grid',          feeds: 'R7 Kanton-level cyber-exposure (secondary)' },
    { id: 'EEA',    name: 'EEA Air Quality e-Reporting',              url: 'eea.europa.eu',                  freq: 'Annual',    res: '~1 km + station',vars: 3,  category: 'Environment',   feeds: 'I8 PM2.5, NO₂, O₃ corrosion (CH observer)' },
    { id: 'SECO',   name: 'SECO State Secretariat for Economic Affairs', url: 'seco.admin.ch',               freq: 'Quarterly', res: 'Kanton',         vars: 3,  category: 'Economic',      feeds: 'Energy poverty cross-validation, GDP, unemployment' },
    { id: 'ICTMIN', name: 'ICT-Minimum Standard 2018 (NCSC)',         url: 'ncsc.admin.ch',                  freq: 'Annual',    res: 'CH-national',    vars: 2,  category: 'Socio-Econ',    feeds: 'R7 ICT minimum standard maturity, NCSC compliance' },
    { id: 'NCSC',   name: 'NCSC National Cyber Security Centre',      url: 'ncsc.admin.ch',                  freq: 'Annual',    res: 'CH-national',    vars: 2,  category: 'Socio-Econ',    feeds: 'R7 CYBER 2025 grid expansion, cyber incident logs' },
    { id: 'BFE',    name: 'BFE / OFEN Federal Energy Office',         url: 'bfe.admin.ch',                   freq: 'Annual',    res: 'Kanton',         vars: 2,  category: 'Economic',      feeds: 'Hydropower atlas, Energiestrategie 2050 targets' },
    { id: 'ARE',    name: 'ARE Federal Office for Spatial Development', url: 'are.admin.ch',                 freq: 'Annual',    res: 'Kanton',         vars: 1,  category: 'Environment',   feeds: 'Environmental + spatial planning' },
    { id: 'EFV',    name: 'EFV Federal Finance Administration',       url: 'efv.admin.ch',                   freq: 'Annual',    res: 'Kanton',         vars: 1,  category: 'Socio-Econ',    feeds: 'R3 fiscal enrichment, Kanton revenue capacity' },
    { id: 'GFZ',    name: 'GFZ German Research Centre (Geosci.)',     url: 'gfz-potsdam.de',                 freq: 'Static',    res: '~5 km',          vars: 2,  category: 'Hazard',        feeds: 'Cross-border seismic, geomagnetic risk' },
    { id: 'SNB',    name: 'SNB Swiss National Bank',                  url: 'snb.ch',                         freq: 'Quarterly', res: 'Kanton / national', vars: 2, category: 'Socio-Econ',  feeds: 'R3 macroprudential, V_socio income vulnerability' },
    { id: 'VSE',    name: 'VSE Verband Schweizerischer Elektrizitätsunternehmen', url: 'strom.ch',           freq: 'Annual',    res: 'DSO / Kanton',   vars: 2,  category: 'Grid',          feeds: 'Grid investment, DSO quality statistics' },
    { id: 'SGRID-N', name: 'Swissgrid Network Development Plan',      url: 'swissgrid.ch/strategicgrid',     freq: 'Annual',    res: 'TSO zone',       vars: 2,  category: 'Grid',          feeds: 'Strategic Grid 2030/2040, 41 cross-border lines' },
    { id: 'ASTRA',  name: 'ASTRA EV Registry (Bundesamt für Strassen)', url: 'astra.admin.ch',               freq: 'Quarterly', res: 'Kanton',         vars: 1,  category: 'Transition',    feeds: 'T1 EV registration data' },
    { id: 'BABS',   name: 'BABS Civil Protection (Bundesamt)',        url: 'babs.admin.ch',                  freq: 'Continuous',res: 'Kanton',         vars: 1,  category: 'Hazard',        feeds: 'R6c flood zones, critical infrastructure alerts' },
    { id: 'INNO',   name: 'Innosuisse — Swiss Innovation Agency',     url: 'innosuisse.ch',                  freq: 'Quarterly', res: 'Kanton',         vars: 1,  category: 'Economic',      feeds: 'E2 innovation enrichment' },
    { id: 'ISO-9223', name: 'ISO 9223 Corrosion',                     url: '(derived from EEA + BAFU)',      freq: 'Derived',   res: 'Kanton',         vars: 1,  category: 'Environment',   feeds: 'I8 corrosion class C2/C3/C4 (no C5 — landlocked)' },
    { id: 'KOF',    name: 'KOF Konjunkturforschungsstelle ETH',       url: 'kof.ethz.ch',                    freq: 'Quarterly', res: 'Regional',       vars: 2,  category: 'Socio-Econ',    feeds: 'R3 regional development, business cycle' },
    { id: 'ELCOM-M', name: 'ElCom Monitoring Report',                 url: 'elcom.admin.ch',                 freq: 'Annual',    res: 'DSO-level',      vars: 2,  category: 'Grid',          feeds: 'CAIDI, restoration speed, R6a calibration' },
    { id: 'BFS-S',  name: 'BFS / OFS Spatial Typology',               url: 'bfs.admin.ch',                   freq: 'Annual',    res: 'Gemeinde',       vars: 1,  category: 'Socio-Econ',    feeds: 'Urban/rural classification, settlement structure' },
    { id: 'AVENIR', name: 'Avenir Suisse — Policy Research',          url: 'avenir-suisse.ch',               freq: 'Annual',    res: 'Kanton',         vars: 1,  category: 'Economic',      feeds: 'Regional convergence metrics, energy policy' },
    { id: 'AEE',    name: 'AEE Suisse — Renewable Energy Agency',     url: 'aeesuisse.ch',                   freq: 'Annual',    res: 'Kanton',         vars: 1,  category: 'Transition',    feeds: 'Regional renewable transition progress' },
    { id: 'BFS-GMD', name: 'BFS Gemeindeverzeichnis (Municipality Registry)', url: 'bfs.admin.ch',           freq: 'Static',    res: '2,148 Gemeinden',vars: 1,  category: 'Infrastructure', feeds: 'Join key, Kanton-district-municipality mapping' },
  ];

  // ─── 6 Components ────────────────────────────────────────
  const COMPONENTS = [
    {
      id: 'C', name: 'Continuity', weight: 0.30, color: '#941914',
      desc: 'Measures reliability and outage exposure — how often and how long power interruptions occur.',
      metrics: [
        { id: 'C1', name: 'Outage Duration', intra: 0.40, global: 0.120, norm: 'A (P5/P95)', source: 'ElCom / VSE', desc: 'Total annual interruption duration (SAIDI)' },
        { id: 'C2', name: 'Outage Count',    intra: 0.30, global: 0.090, norm: 'A (P5/P95)', source: 'ElCom / VSE', desc: 'Number of interruptions per year (SAIFI)' },
        { id: 'C3', name: 'MT Exceed Rate',  intra: 0.15, global: 0.045, norm: 'C (0–100%)', source: 'ElCom', desc: 'Percentage of time voltage exceeds regulation limits' },
        { id: 'C4', name: 'Planned Outages', intra: 0.15, global: 0.045, norm: 'B (P5/P95)', source: 'ElCom Monitoring', desc: 'Duration of planned maintenance interruptions' },
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
        { id: 'I1', name: 'Snow/Ice Risk (IRI)',  intra: 0.12, global: 0.030, norm: 'C (0–0.30)', source: 'MeteoSwiss / ElCom IRI', desc: 'Climate risk index for snow/ice (alpine high-risk)', adaptive: true },
        { id: 'I2', name: 'Tree-Fall Risk (IRI)', intra: 0.09, global: 0.023, norm: 'C (0–0.30)', source: 'MeteoSwiss / ElCom IRI', desc: 'Tree-fall climate risk index', adaptive: true },
        { id: 'I3', name: 'Heat-Wave Risk (IRI)', intra: 0.15, global: 0.038, norm: 'C (0–0.30)', source: 'MeteoSwiss / ElCom IRI', desc: 'Heat-wave climate risk index', adaptive: true },
        { id: 'I4', name: 'RTN Density',          intra: 0.12, global: 0.030, norm: 'B ↓inverted', source: 'ElCom Grid Data', desc: 'Transmission network density — higher = more resilient', inverted: true },
        { id: 'I5', name: 'Thermal Stress Proxy', intra: 0.12, global: 0.030, norm: 'B (P5/P95)', source: 'IEEE C57.91', desc: 'Transformer thermal degradation (ambient + load)', isNew: true },
        { id: 'I6', name: 'Substation Density',   intra: 0.12, global: 0.030, norm: 'B ↓inverted', source: 'OSM / ElCom Registry', desc: 'Substation density — higher = more backup capacity', inverted: true },
        { id: 'I7', name: 'Load Stress',          intra: 0.10, global: 0.025, norm: 'B (P5/P95)', source: 'Swissgrid / DSOs', desc: 'Ratio of peak load to rated capacity', isNew: true },
        { id: 'I8', name: 'Air Quality Corrosion', intra: 0.08, global: 0.020, norm: 'B (P5/P95)', source: 'BAFU / EEA / ISO 9223', desc: 'C2 most fleet · C3 alpine valleys · C4 Zürich/Basel urban (no C5 — landlocked)', isNew: true },
        { id: 'I9', name: 'Hydrogeological Risk', intra: 0.10, global: 0.025, norm: 'B (P5/P95)', source: 'swisstopo / BABS GHK', desc: 'Flood (Rhône/Aare/Rhine/Ticino) + landslide exposure', isNew: true },
      ]
    },
    {
      id: 'E', name: 'Economic', weight: 0.10, color: '#aa4234',
      desc: 'Quantifies economic impact of grid disruption — regulatory penalties and productivity losses.',
      metrics: [
        { id: 'E1', name: 'ElCom Penalties/User',  intra: 0.55, global: 0.055, norm: 'B (P5/P95)', source: 'ElCom / VSE', desc: 'Per-user penalty costs from quality standard violations' },
        { id: 'E2', name: 'Productivity Loss Coeff.', intra: 0.45, global: 0.045, norm: 'C (bounded)', source: 'BFS / KOF / SNB', desc: 'Weighted avg VoLL by local economic structure' },
      ]
    },
    {
      id: 'S', name: 'Saturation', weight: 0.20, color: '#8e44ad',
      desc: 'Measures grid utilisation stress — generation/consumption imbalance, reverse power flow, and critical load classes.',
      metrics: [
        { id: 'S1', name: 'Kanton KPI (Gen/Consumption)', intra: 0.75, global: 0.150, norm: 'B* (Dimovski)', source: 'Swissgrid / BFE', desc: 'Kanton-level generation/consumption ratio — Dimovski breakpoints 1.29/7.78' },
        { id: 'S2', name: 'Reverse Power Flow',          intra: 0.125, global: 0.025, norm: 'D (categorical)', source: 'Swissgrid / DSO', desc: '{No RPF→0, >1%→0.5, >5%→1.0}', categorical: true },
        { id: 'S3', name: 'Criticality Class',           intra: 0.125, global: 0.025, norm: 'D (categorical)', source: 'ElCom', desc: '{Non-critical→0, Hospital/transport→0.5, Multiple critical→1.0}', categorical: true },
      ]
    },
    {
      id: 'T', name: 'Energy Transition', weight: 0.05, color: '#0e7490',
      desc: 'Captures energy-transition stress from distributed generation, output variability, and EV charging burden.',
      isNew: true,
      metrics: [
        { id: 'T1', name: 'DER Stress Index', intra: 1.00, global: 0.050, norm: 'B (composite)', source: 'Pronovo + Swissgrid + ASTRA', desc: 'Composite: α_DER(0.50) × N(DER_ratio) + α_VAR(0.30) × N(variability) + α_EV(0.20) × N(EV_load)', isNew: true,
          submetrics: [
            { id: 'DER_ratio', name: 'DER Penetration Ratio', weight: 0.50, source: 'Pronovo + Swissgrid', desc: 'DER capacity / peak load by Kanton' },
            { id: 'DER_variability', name: 'DER Output Variability', weight: 0.30, source: 'ENTSO-E Transparency', desc: 'σ/μ of weekly DER output (coefficient of variation)' },
            { id: 'EV_load_ratio', name: 'EV Load Burden', weight: 0.20, source: 'ASTRA + ElCom', desc: 'EV count × 7.4kW / transformer capacity' },
          ]
        },
      ]
    },
  ];

  // ─── 7 Modifiers (Switzerland calibration §53) ────────────
  const MODIFIERS = [
    {
      id: 'R2', name: 'Adaptive IRI + Climate Trajectory',
      range: 'Weight redistribution', type: 'Weight modifier',
      desc: 'Uses CMIP6 RCP4.5 projections to transform IRI_current → IRI_forward. Aletsch + Rhône glacier retreat (50% mass loss by 2050) shifts Wallis weight from winter snow-loading toward summer hydropower-drought.',
      formula: 'IRI_forward(m,s) = IRI_current(m,s) × (1 + 0.15 × clip(Δ_climate, −0.50, +1.00))',
      sources: ['Copernicus CDS', 'MeteoSwiss / ElCom IRI'],
      isEnhanced: true
    },
    {
      id: 'R3', name: 'Consequence + Energy Poverty (4-tier)',
      range: '[1.02, 1.08]', type: 'Multiplicative',
      desc: 'Switzerland §53 4-tier calibration: 1.02 capital-intensive (Zürich + Basel-Stadt + Geneva) · 1.04 industrial+commercial (Vaud + Bern + Aargau + St. Gallen + Luzern + Ticino) · 1.06 mixed (Valais + Graubünden + Fribourg + Thurgau + Solothurn + Schwyz + Zug + Neuchâtel + Jura) · 1.08 rural-alpine (Uri + Glarus + Appenzell-AR/IR + Obwalden + Nidwalden + Schaffhausen).',
      formula: 'C_mult ∈ {1.02, 1.04, 1.06, 1.08}, z = 0.04·log₂(pop/pop_med) + 0.03·log₂(GWh/GWh_med) + 0.02·V_socio',
      sources: ['BFS / OFS', 'EFV', 'KOF', 'SNB', 'swisstopo / BABS'],
      isEnhanced: true,
      enrichments: [
        { name: 'V_socio Fiscal Enrichment', effect: 'Up to +8% V_socio penalty', sources: 'EFV + KOF + ElCom' },
        { name: 'Demographic Shift Amplifier', effect: 'Up to +8% C_mult for population decline', sources: 'BFS Demographics' },
        { name: 'Elderly Vulnerability', effect: '×[1.0, 1.10] for high elderly %', sources: 'BFS Demographics' },
        { name: 'Flood Zone Amplifier (R6c)', effect: 'Up to +15% C_mult — Rhône/Aare/Rhine/Ticino', sources: 'swisstopo GHK + BABS' },
      ]
    },
    {
      id: 'R4', name: 'Graph-Theoretic Network Criticality',
      range: '[0.80, 1.35]', type: 'Multiplicative',
      desc: 'Combines degree centrality, betweenness centrality, and topological bridge detection from OSM power graph. Built from ~1,250 substations and the most-interconnected per-population border footprint in the OECD (41 cross-border lines with DE×11, IT×12, FR×9, AT×6, LI×3).',
      formula: 'F_topo = clip(base_factor(degree) × (1 + 0.10 × BC_percentile + 0.15 × is_bridge), 0.80, 1.35)',
      sources: ['OSM Overpass API', 'Swissgrid Strategic Grid'],
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
      desc: 'ElCom CAIDI-based sigmoid that distinguishes fast-restoring (Zürich urban core) vs slow-restoring (rural alpine valleys).',
      formula: 'R6a_mult = sigmoid_bounded(CAIDI_local / CAIDI_med, 0.90, 1.10)',
      sources: ['ElCom Monitoring Report'],
      isNew: true
    },
    {
      id: 'R6b', name: 'Alpine Seismic (PGA 475-yr)',
      range: 'α ∈ [0.04, 0.22]', type: 'Multiplicative',
      desc: 'Switzerland carries the highest seismic exposure in DACH. Wallis at PGA 0.16 g (475-yr), Basel + Graubünden + Ticino at 0.12 g, northern Cantons (Aargau, Schaffhausen, Thurgau, Zürich) at 0.04–0.08 g. SED operates 200+ permanent stations. Reference event: 1946 Sierre M_L 5.8.',
      formula: 'R6b_seis = clip(1.0 + α × (PGA_475yr − PGA_floor) / PGA_span, 1.00, 1.25), α ∈ [0.04, 0.22]',
      sources: ['SED (Swiss Seismological Service)', 'swisstopo'],
      isNew: true
    },
    {
      id: 'R6c', name: 'Flood (Rhône + Aare + Rhine + Ticino)',
      range: '[1.00, 1.20]', type: 'Multiplicative',
      desc: 'Riverine + flash-flood exposure penalty applied to substations within 100-yr return-period zones of the Rhône (Wallis to Lake Geneva), Aare (Bern + Aargau), Rhine (Basel), and Ticino (south-alpine flash-flood). Reference event: 2024 Sommer floods (Lake Lucerne, Linth, Saane) — 11 substation-hours of weather-driven outage with no asset losses. Source: swisstopo GHK + BAFU + BABS.',
      formula: 'R6c_flood = clip(1.0 + 0.20 × flood_100yr_intersect, 1.00, 1.20)',
      sources: ['swisstopo GHK', 'BAFU', 'BABS'],
      isNew: true
    },
    {
      id: 'R7', name: 'Digital Readiness (NCSC + CYBER 2025)',
      range: '[0.99, 1.05]', type: 'Multiplicative',
      desc: 'NCSC mandates ICT-Minimum Standard 2018; CYBER 2025 expands cyber-resilience to the grid sector. Switzerland is non-EU and outside DESI — calibration uses NCSC compliance + ICT-Minimum Standard maturity + urban/rural Gemeinde adjustment + HV voltage class bonus. Ceiling 1.05 (no DESI ceiling). Unique values across ~1,250 substations.',
      formula: 'R7_cyber(s) = clip( NCSC_base(Kanton) + urban_adj(Gemeinde) + HV_bonus(voltage) + noise, 0.99, 1.05 )',
      sources: ['NCSC', 'ICT-Minimum Standard 2018', 'CYBER 2025', 'JRC DSO Observatory'],
      isNew: true,
      enrichments: [
        { name: 'Kanton-Level NCSC Computation', effect: 'Continuous [0.99, 1.05] per substation', sources: 'NCSC + ICT-Minimum' },
      ]
    },
  ];

  // ─── Data Layers (11 layers, 95 variables) ─────────────────
  const DATA_LAYERS = [
    { id: 'A',   name: 'SSI v4.0.2 Resilience',         vars: 20, status: 'LIVE',          sources: 'ElCom · BFS · Swissgrid · Pronovo · ASTRA · MeteoSwiss' },
    { id: 'B.1', name: 'Grid Telemetry: Open',          vars: 3,  status: 'LIVE',          sources: 'Open-Meteo / ERA5 · ElCom vintage · ElCom digitalization' },
    { id: 'B.2', name: 'Grid Telemetry: Proxy',         vars: 4,  status: 'LIVE',          sources: 'IEEE C57.91 · Swissgrid / DSOs · BAFU · EN 50160' },
    { id: 'B.3', name: 'Grid Telemetry: Fuzzy/Markov',  vars: 12, status: 'LIVE (MARKOV)', sources: 'IEEE/CIGRÉ · Pronovo · EEA' },
    { id: 'C',   name: 'Socio-Economic',                vars: 9,  status: 'LIVE',          sources: 'BFS · KOF · SNB · SECO · NCSC (R7)' },
    { id: 'D',   name: 'Environmental Hazards',         vars: 7,  status: 'LIVE',          sources: 'EEA · SED · swisstopo · ISO 9223 · Copernicus CDS' },
    { id: 'E',   name: 'Swiss Federal Open Data',       vars: 8,  status: 'LIVE',          sources: 'BAFU · ARE · EFV · ElCom · BFS · BFE' },
    { id: 'F',   name: 'Network Transitions',           vars: 12, status: 'LIVE (BAYESIAN)', sources: 'DSO history OR IEEE/CIGRÉ + priors' },
    { id: 'G',   name: 'Modifier Inputs',               vars: 3,  status: 'LIVE',          sources: 'ElCom Monitoring · OSM Power · JRC DSO', isNew: true },
    { id: 'H',   name: 'Network & Topology',            vars: 7,  status: 'LIVE',          sources: 'Swissgrid Strategic Grid · SED · OSM · swisstopo', isNew: true },
    { id: 'I',   name: 'Output Scores',                 vars: 7,  status: 'LIVE',          sources: 'Fleet Markov Chain · IEEE/CIGRÉ analysis', isNew: true },
  ];

  // ─── Processing Pipeline ──────────────────────────────────
  const PIPELINE = [
    { step: 1, name: 'Ingest',     desc: '95 variables from 35 verified data sources', icon: '①' },
    { step: 2, name: 'Normalise',  desc: 'Methods A–D: fleet percentile, bounded, categorical → [0,1]', icon: '②' },
    { step: 3, name: 'Weight',     desc: '6-level hierarchy: component × intra-metric weights', icon: '③' },
    { step: 4, name: 'Compose',    desc: 'R_base = Σ wᵢ·Cᵢ (6 components, 20 metrics)', icon: '④' },
    { step: 5, name: 'Modify',     desc: 'R2 adaptive + R3 (4-tier) × R4 topology × R6a × R6b alpine seismic × R6c flood × R7', icon: '⑤' },
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
    formula: 'R_final = soft_clip_upper(R_base × F_topo × C_mult × R6a_mult × R6b_seis × R6c_flood × Cyber_factor)',
    R_base: 'R_base = 0.30·C + 0.10·V + 0.25·I + 0.10·E + 0.20·S + 0.05·T',
    modifiers: {
      F_topo: 'graph_criticality(degree, BC, bridge) [R4]',
      C_mult: 'consequence_4tier(pop, load, V_socio) [R3 §53 4-tier]',
      R6a_mult: 'restoration_speed_sigmoid(CAIDI_local) [R6a]',
      R6b_seis: 'alpine_seismic(PGA_475yr, α∈[0.04, 0.22]) [R6b]',
      R6c_flood: 'flood_basin(Rhône, Aare, Rhine, Ticino) [R6c]',
      Cyber_factor: 'NCSC_ICT_Minimum_cyber(Kanton, voltage) [R7, ceiling 1.05]'
    },
    soft_clip: 'if R_raw ≤ 1.00 → R_raw; if R_raw > 1.00 → 1.00 − 1/(1 + e^(20×(R_raw − 1.05)))'
  };

  // ─── Validation Framework ─────────────────────────────────
  const VALIDATION_CHECKS = [
    { check: 'Alpine N–S seismic gradient',  criterion: 'Wallis + Basel + GR + TI substations R systematically higher than Mittelland', status: 'verified' },
    { check: 'IRI-climate coherence',        criterion: 'I1 peaks Wallis/Graubünden alpine · I3 peaks Geneva/Basel/Ticino lowlands', status: 'verified' },
    { check: 'Saturation-RPF coherence',     criterion: 'S1 > 7.78 ↔ S2 > 5% agreement > 90%', status: 'verified' },
    { check: 'Ratio test',                   criterion: 'R(worst) / R(best) ≥ 5×', status: 'verified' },
    { check: 'Monotonicity',                 criterion: 'Each metric worsening → R increases', status: 'verified' },
    { check: 'CI width quality signal',      criterion: 'Regional-only subs have wider CI', status: 'verified' },
    { check: 'T1-Hydropower coherence',      criterion: 'T1 reflects 58% hydropower share · Linth-Limmern/Nant de Drance pumped-storage clusters', status: 'verified' },
    { check: 'R6a speed coherence',          criterion: 'R6a < 1.0 for urban Zürich/Geneva/Basel, R6a > 1.0 for rural alpine Cantons', status: 'verified' },
    { check: 'Energy poverty gradient',      criterion: 'V_socio correlates with rural deprivation and peripheral alpine valleys', status: 'verified' },
    { check: 'R4 bridge identification',     criterion: 'is_bridge=1 subs have higher R than degree-matched non-bridges', status: 'verified' },
    { check: 'Climate trajectory direction', criterion: 'I3 trajectory > 1.0 in Mittelland, I1 stable in alpine West', status: 'verified' },
    { check: 'Weight sum invariant',         criterion: 'Σ w_component = 1.000 exactly', status: 'verified' },
    { check: 'R6b alpine seismic',           criterion: 'Wallis substations carry α ≥ 0.20 vs Mittelland α ≤ 0.06', status: 'verified' },
    { check: 'Markov risk coherence',        criterion: 'markov_risk_score positively correlates with asset age and outage rates', status: 'verified' },
    { check: 'Corrosion gradient (no C5)',   criterion: 'C2 most fleet · C3 alpine valleys · C4 Zürich+Basel+Aarau urban · NO C5 (landlocked)', status: 'verified' },
  ];

  // ─── Changelog v3.4 → v4.0.2 ───────────────────────────────
  const CHANGELOG = [
    { id: 'F1', section: '§2, §4', change: 'New T component — Energy Transition Exposure (T1)', type: 'new' },
    { id: 'F2', section: '§5',     change: 'New R6a — Restoration Speed Modifier (CAIDI-based)', type: 'new' },
    { id: 'F3', section: '§5',     change: 'R3 enhanced — §53 4-tier 1.02 / 1.04 / 1.06 / 1.08 calibration', type: 'enhanced' },
    { id: 'F4', section: '§5',     change: 'R4 enhanced — Graph-theoretic betweenness + bridge detection', type: 'enhanced' },
    { id: 'F5', section: '§5',     change: 'R2 enhanced — Climate Trajectory (CMIP6 RCP4.5 + Aletsch retreat)', type: 'enhanced' },
    { id: 'F6', section: '§5',     change: 'R7 Digital Readiness — NCSC + CYBER 2025 (non-EU, no DESI)', type: 'enhanced' },
    { id: 'L1', section: '§2, §8', change: 'New I5, I7–I9 metrics — thermal, load, corrosion, hydrogeo', type: 'new' },
    { id: 'L2', section: '§6',     change: 'E2 Innovation Enrichment — KOF + Innosuisse + startup density', type: 'enhanced' },
    { id: 'L3', section: '§5',     change: 'V_socio Fiscal Enrichment — EFV + KOF + energy price', type: 'enhanced' },
    { id: 'L4', section: '§5',     change: 'R3 Demographic Shift Amplifier — BFS net migration', type: 'enhanced' },
    { id: 'L5', section: '§8, §12', change: '95/95 variables operational (100%). 35 data sources total.', type: 'data' },
    { id: 'G1', section: '§12',    change: 'Pronovo upgraded to bulk download — Kanton-level DER + hydro registry', type: 'data' },
    { id: 'G2', section: '§12',    change: 'swisstopo upgraded to WMS live API — Kanton-level geological + GHK flood', type: 'data' },
    { id: 'G3', section: '§12',    change: 'OSM upgraded to Overpass API — ~1,250 real substations', type: 'data' },
    { id: 'G4', section: '§5',     change: 'R6b alpine seismic α∈[0.04, 0.22] — highest in DACH (Wallis PGA 0.16g)', type: 'new' },
    { id: 'G5', section: '§5',     change: 'R6c flood Rhône/Aare/Rhine/Ticino — 2024 Sommer floods reference', type: 'new' },
    { id: 'G6', section: '§12',    change: 'Output Scores layer (I): 7 variables — risk_score, ETTC, stationary probs', type: 'new' },
  ];

  // ─── Frequency Distribution ───────────────────────────────
  const FREQ_DISTRIBUTION = {
    Weekly: { count: 2, sources: ['OSM Overpass', 'Open-Meteo/ERA5'] },
    Monthly: { count: 2, sources: ['Swissgrid', 'Pronovo'] },
    Quarterly: { count: 5, sources: ['SECO', 'SNB', 'ASTRA', 'Innosuisse', 'KOF'] },
    Annual: { count: 18, sources: ['ElCom', 'BFS', 'BAFU', 'ARE', 'EFV', 'BFE', 'VSE', 'Swissgrid NDP', 'NCSC', 'ICT-Minimum', 'AEE Suisse', 'Avenir Suisse', 'JRC', 'EEA', 'BFS-S', 'ElCom Monitoring', 'BABS', 'MeteoSwiss'] },
    Static: { count: 8, sources: ['Dimovski', 'IEEE/IEC/CIGRÉ', 'Copernicus CMIP6', 'GFZ', 'SED', 'swisstopo', 'ISO 9223', 'ENTSO-E'] },
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
      modifiers: 7,
      sources: 35,
      substations: 1250,
      powerLines: 9800,
      mcIterations: 10000,
      kantone: 26,
      districts: 148,
      municipalities: 2148,
      regions: 26
    },

    // 26 Kantone canonical order (BFS Gemeindeverzeichnis order)
    KANTONE: [
      { code: 'ZH', name: 'Zürich' },
      { code: 'BE', name: 'Bern' },
      { code: 'LU', name: 'Luzern' },
      { code: 'UR', name: 'Uri' },
      { code: 'SZ', name: 'Schwyz' },
      { code: 'OW', name: 'Obwalden' },
      { code: 'NW', name: 'Nidwalden' },
      { code: 'GL', name: 'Glarus' },
      { code: 'ZG', name: 'Zug' },
      { code: 'FR', name: 'Fribourg' },
      { code: 'SO', name: 'Solothurn' },
      { code: 'BS', name: 'Basel-Stadt' },
      { code: 'BL', name: 'Basel-Landschaft' },
      { code: 'SH', name: 'Schaffhausen' },
      { code: 'AR', name: 'Appenzell Ausserrhoden' },
      { code: 'AI', name: 'Appenzell Innerrhoden' },
      { code: 'SG', name: 'St. Gallen' },
      { code: 'GR', name: 'Graubünden' },
      { code: 'AG', name: 'Aargau' },
      { code: 'TG', name: 'Thurgau' },
      { code: 'TI', name: 'Ticino' },
      { code: 'VD', name: 'Vaud' },
      { code: 'VS', name: 'Valais' },
      { code: 'NE', name: 'Neuchâtel' },
      { code: 'GE', name: 'Genève' },
      { code: 'JU', name: 'Jura' }
    ],

    // R3 4-tier mapping (§53 calibration)
    R3_TIERS: {
      '1.02': ['Zürich', 'Basel-Stadt', 'Genève'],
      '1.04': ['Vaud', 'Bern', 'Aargau', 'St. Gallen', 'Luzern', 'Ticino'],
      '1.06': ['Valais', 'Graubünden', 'Fribourg', 'Thurgau', 'Solothurn', 'Schwyz', 'Zug', 'Neuchâtel', 'Jura'],
      '1.08': ['Uri', 'Glarus', 'Appenzell Ausserrhoden', 'Appenzell Innerrhoden', 'Obwalden', 'Nidwalden', 'Schaffhausen', 'Basel-Landschaft']
    }
  };
})();

// ─────────────────────────────────────────────────────────────────────
// KB §45.6 — dual-global alias (back-compat for deploy gate + loaders)
// The IIFE above assigns window.SSIMetadata as the canonical form for
// this country. The deploy script gate at §45.6 requires BOTH globals
// exist + the reverse alias direction for cross-country grep consistency
// with LV/LT/EE/CZ/LU/BE/NL/AT pattern.
// ─────────────────────────────────────────────────────────────────────
window.SSI_METADATA = window.SSIMetadata;
window.SSIMetadata = window.SSI_METADATA;
