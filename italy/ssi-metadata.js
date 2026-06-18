/* ═══════════════════════════════════════════════════════════
   SSI v4.2 — Metadata Registry (Italy)
   101 variables · 34 sources · 20 metrics · 6 components · 11 modifiers · 4,293 substations
   Complete reference data for methodology page + data page

   v4.2 update (11 Jun 2026):
   - 95 → 101 variables (+6 from v4.2 modifier inputs: R6c flood / R6d wildfire /
     R6e winter / R8 adapt / R9 compound / R10 just)
   - 30 → 34 data sources (+4: ISPRA IdroGEO PGRA flood + ISPRA SIAB wildfire +
     ECMWF ERA5 Bourgouin + ARERA bulk smart meter)
   - 5 → 11 modifiers (+6 new resilience modifiers per v4.2 brief set)
   - W1-W10 audit-state split: 5/1/1/3 4-tier (mesh resolution per Convention #6 §5.6)
   - Foundation contact: ssi_index@ikenga.eu
   ═══════════════════════════════════════════════════════════ */

window.SSIMetadata = (function () {
  'use strict';

  // ─── 35 Verified Data Sources ─────────────────────────────
  const DATA_SOURCES = [
{ id: 'TERNA',  name: 'Terna SpA (TSO)',                    url: 'terna.it',                              freq: 'Monthly',   res: 'Control area / zone', vars: 8,  category: 'Grid',          feeds: 'C1–C4 (SAIDI/SAIFI per regione), I1–I3 trajectory, 380/220/150 kV registry, SAPEI/SACOI HVDC flows' },
    { id: 'ARERA',  name: 'ARERA Regulator',                    url: 'arera.it',                              freq: 'Annual',    res: 'DSO + Provincia',    vars: 8,  category: 'Grid',          feeds: 'Testo Integrato Qualità (TIQE), SAIDI/SAIFI per DSO per provincia, quality bonus/penalties' },
    { id: 'ISTAT',  name: 'ISTAT — Italian National Statistics',url: 'istat.it',                              freq: 'Annual',    res: 'Regione + Provincia + Comune', vars: 9, category: 'Socio-Econ', feeds: 'R3 population, elderly, GDP, Mezzogiorno North-South split, fiscal capacity' },
    { id: 'GME',    name: 'GME Gestore dei Mercati Energetici', url: 'mercatoelettrico.org',                  freq: 'Hourly',    res: '7 bidding zones',     vars: 3,  category: 'Grid',          feeds: 'Day-ahead PUN, zonal prices Nord/CNord/CSud/Sud/Calabria/Sicilia/Sardegna, ancillary' },
    { id: 'GSE',    name: 'GSE Gestore Servizi Energetici',     url: 'gse.it',                                freq: 'Quarterly', res: 'Regione',             vars: 4,  category: 'Transition',    feeds: 'T1 renewable certificates, PNIEC tracking, PNRR grid investment, solar/wind/hydro registry' },
    { id: 'OSM',    name: 'OSM Power Infrastructure',           url: 'overpass-api.de',                       freq: 'Weekly',    res: 'Node/edge',           vars: 3,  category: 'Infrastructure',feeds: 'R4 graph topology, BC, bridges · ~5,000 substations post-§38 filter' },
    { id: 'INGV',   name: 'INGV — Geofisica e Vulcanologia',    url: 'ingv.it',                               freq: 'Continuous',res: '~5 km',               vars: 4,  category: 'Hazard',        feeds: 'R6_seismic 475-yr PGA [0.05, 0.25], R6_volcanic Vesuvio/Etna/Campi Flegrei monitoring' },
    { id: 'ISPRA',  name: 'ISPRA Environmental Protection',     url: 'isprambiente.gov.it',                   freq: 'Annual',    res: 'Regione + bacino',    vars: 4,  category: 'Hazard',        feeds: 'R6c flood α [0.04, 0.10] Po + Arno + Tevere + Adige; landslide IFFI inventory' },
    { id: 'AM',     name: 'Aeronautica Militare — Meteo',       url: 'meteoam.it',                            freq: 'Daily',     res: '~1 km',               vars: 3,  category: 'Climate',       feeds: 'I1–I3 storms, heat-wave events, snow load Apennine + Alpi' },
    { id: 'D10',    name: 'Copernicus CDS / ERA5',              url: 'cds.climate.copernicus.eu',             freq: 'Static',    res: '0.25° (~25 km)',      vars: 4,  category: 'Climate',       feeds: 'R2 Δ_climate (I1–I3 trajectory), CMIP6 SSP2-4.5', registration: true },
    { id: 'ENTSE',  name: 'ENTSO-E Transparency',               url: 'transparency.entsoe.eu',                freq: 'Hourly',    res: 'Bidding zone',        vars: 2,  category: 'Transition',    feeds: 'T1 DER variability, IT-FR/IT-CH/IT-AT/IT-SI cross-border flows', registration: true },
    { id: 'ACN',    name: 'ACN Cybersecurity Agency',           url: 'acn.gov.it',                            freq: 'Annual',    res: 'National + sector',   vars: 2,  category: 'Governance',    feeds: 'R7 cyber baseline, NIS2 transposition compliance, Perimetro Sicurezza Cibernetica' },
    { id: 'DESI',   name: 'DESI Digital Economy Index',         url: 'digital-strategy.ec.europa.eu',         freq: 'Annual',    res: 'EU + NUTS-2',         vars: 2,  category: 'Socio-Econ',    feeds: 'R7 Regione-level cyber-exposure (DESI 2024 = 0.51, lowest in cohort)' },
    { id: 'BdI',    name: "Banca d'Italia",                     url: 'bancaditalia.it',                       freq: 'Quarterly', res: 'Regione',             vars: 3,  category: 'Economic',      feeds: 'R3 fiscal enrichment, E2 productivity loss, Mezzogiorno gap, regional GDP' },
    { id: 'IEEE-1', name: 'IEEE C57.91 / IEC 60076',            url: 'standards.ieee.org',                    freq: 'Static',    res: 'Asset-level',         vars: 16, category: 'Standards',     feeds: 'I5 thermal model, B.3 Markov states (high tier — Terna unified since 2004)' },
    { id: 'CIGRE',  name: 'CIGRE TB 761 Asset Management',       url: 'cigre.org',                             freq: 'Static',    res: 'Asset-level',         vars: 5,  category: 'Standards',     feeds: 'B.3 Markov 5-state, transformer ageing curves' },
    { id: 'EEA',    name: 'EEA Air Quality e-Reporting',        url: 'eea.europa.eu',                         freq: 'Annual',    res: '~1 km + station',     vars: 3,  category: 'Environment',   feeds: 'I8 PM2.5, NO₂, O₃ — Po Valley industrial corrosion belt' },
    { id: 'EURO',   name: 'Eurostat Energy Statistics',          url: 'ec.europa.eu/eurostat',                 freq: 'Annual',    res: 'NUTS-2',              vars: 3,  category: 'Economic',      feeds: 'Energy poverty cross-validation, REGION level harmonised' },
    { id: 'SNAM',   name: 'SNAM Gas Network Operator',          url: 'snam.it',                               freq: 'Annual',    res: 'National',            vars: 1,  category: 'Transition',    feeds: 'Hydrogen transition planning, gas-grid coupling, repowering' },
    { id: 'RSE',    name: 'RSE Ricerca sul Sistema Energetico', url: 'rse-web.it',                            freq: 'Annual',    res: 'Regione',             vars: 2,  category: 'Transition',    feeds: 'PNRR grid investment, storage targets, transition stress modelling' },
    { id: 'ISO-9223', name: 'ISO 9223 Corrosion',               url: '(derived from EEA + ISPRA)',            freq: 'Derived',   res: 'Regione + coastal',   vars: 1,  category: 'Environment',   feeds: 'I8 corrosion class C2 interior / C3 Po industrial / C4 Milano-Roma / C5 7,600 km coast' },
    { id: 'MIT',    name: 'MIT — Ministero Infrastrutture',     url: 'mit.gov.it',                            freq: 'Annual',    res: 'National',            vars: 1,  category: 'Infrastructure',feeds: 'Strategic infrastructure plan, critical substations, transport-grid coupling' },
    { id: 'PCM-DPC',name: 'Dipartimento Protezione Civile',     url: 'protezionecivile.gov.it',               freq: 'Continuous',res: 'Comune',              vars: 2,  category: 'Hazard',        feeds: 'Civil protection alerts, seismic + volcanic + flood events, restoration coordination' },
    { id: 'AUTBAC', name: 'Autorità di Bacino Distrettuali',    url: 'autoritabacino.it',                     freq: 'Annual',    res: '7 bacini',            vars: 2,  category: 'Hazard',        feeds: 'PAI flood hazard maps, R6c calibration, Po + Appennino + Sardegna + Sicilia + Adige' },
    { id: 'JRC',    name: 'JRC DSO Observatory',                url: 'ses.jrc.ec.europa.eu',                  freq: 'Annual',    res: 'DSO-level',           vars: 2,  category: 'Grid',          feeds: 'R7 Regione-level cyber-exposure (secondary), DSO benchmarking' },
    { id: 'ENEL-XR',name: 'e-distribuzione (Enel DSO)',         url: 'e-distribuzione.it',                    freq: 'Quarterly', res: 'Provincia',           vars: 3,  category: 'Grid',          feeds: 'C1–C4 ~85% of fleet, ~31M customers, ~125,000 km MV+LV, restoration speed' },
    { id: 'ARETI',  name: 'Areti (ACEA Group, Roma DSO)',       url: 'areti.it',                              freq: 'Annual',    res: 'Comuni Roma',         vars: 2,  category: 'Grid',          feeds: 'C1–C4 Roma metro DSO, ~1.6M customers' },
    { id: 'UNARETI',name: 'Unareti (A2A Group, Milano DSO)',    url: 'unareti.it',                            freq: 'Annual',    res: 'Milano + Brescia',    vars: 2,  category: 'Grid',          feeds: 'C1–C4 Milano + Brescia DSO, ~1.1M customers' },
    { id: 'INRETE', name: 'Inrete (Hera Group, ER DSO)',        url: 'gruppohera.it',                         freq: 'Annual',    res: 'Emilia-Romagna',      vars: 2,  category: 'Grid',          feeds: 'C1–C4 Emilia-Romagna provinces DSO, ~450K customers' },
    { id: 'SETDIS', name: 'Set Distribuzione (Trentino)',        url: 'setdistribuzione.it',                   freq: 'Annual',    res: 'Trentino-AA',         vars: 1,  category: 'Grid',          feeds: 'C1–C4 Trentino-Alto Adige DSO' },
    { id: 'GFZ',    name: 'GFZ German Research Centre',         url: 'gfz-potsdam.de',                        freq: 'Static',    res: '~5 km',               vars: 2,  category: 'Hazard',        feeds: 'European seismic hazard model (cross-validation with INGV)' },
    { id: 'COPER-EM',name: 'Copernicus Emergency Management',   url: 'emergency.copernicus.eu',               freq: 'Continuous',res: 'Event-based',         vars: 1,  category: 'Hazard',        feeds: 'Post-event flood mapping (2023 Romagna), wildfire perimeters' },
    { id: 'ISPRA-INV',name: 'ISPRA IFFI Landslide Inventory',   url: 'idrogeo.isprambiente.it',               freq: 'Annual',    res: 'Comune',              vars: 1,  category: 'Hazard',        feeds: 'I9 landslide territorial exposure, Apennine belt + Alps + coastal' },
    { id: 'ANAC',   name: 'ANAC Anti-Corruption Authority',     url: 'anticorruzione.it',                     freq: 'Annual',    res: 'National',            vars: 1,  category: 'Governance',    feeds: 'Procurement governance (cross-validation for PNRR grid investments)' },
    { id: 'CSIRT',  name: 'CSIRT-Italia (ACN sub-org)',         url: 'csirt.gov.it',                          freq: 'Continuous',res: 'National',            vars: 1,  category: 'Governance',    feeds: 'R7 ICS-CERT IT, sectoral cyber incidents, NIS2 reporting' },
  ];

  // ─── 6 Components ────────────────────────────────────────
  const COMPONENTS = [
    {
      id: 'C', name: 'Continuity', weight: 0.30, color: '#941914',
      desc: 'Measures reliability and outage exposure — how often and how long power interruptions occur.',
      metrics: [
        { id: 'C1', name: 'Outage Duration', intra: 0.40, global: 0.120, norm: 'A (P5/P95)', source: 'ARERA / e-distribuzione', desc: 'Total annual interruption duration (SAIDI)' },
        { id: 'C2', name: 'Outage Count',    intra: 0.30, global: 0.090, norm: 'A (P5/P95)', source: 'ARERA / e-distribuzione', desc: 'Number of interruptions per year (SAIFI)' },
        { id: 'C3', name: 'MT Exceed Rate',  intra: 0.15, global: 0.045, norm: 'C (0–100%)', source: 'ARERA', desc: 'Percentage of time voltage exceeds regulation limits' },
        { id: 'C4', name: 'Planned Outages',  intra: 0.15, global: 0.045, norm: 'B (P5/P95)', source: 'ARERA Monitoring', desc: 'Duration of planned maintenance interruptions' },
      ]
    },
    {
      id: 'V', name: 'Voltage Quality', weight: 0.10, color: '#b8863a',
      desc: 'Captures voltage dip severity — short-duration voltage reductions that damage sensitive equipment.',
      metrics: [
        { id: 'V1', name: 'Severity-Weighted Dips', intra: 1.00, global: 0.100, norm: 'B (γ=0.50)', source: 'ARERA Quality Report', desc: 'V = N(V1_total × (1 + 0.50 × V2_severe_ratio))' },
      ]
    },
    {
      id: 'I', name: 'Infrastructure', weight: 0.25, color: '#5d8563',
      desc: 'Assesses physical grid condition — environmental exposure, asset density, and material degradation risks.',
      metrics: [
        { id: 'I1', name: 'Snow/Ice Risk (IRI)',     intra: 0.12, global: 0.030, norm: 'C (0–0.30)', source: 'Open-Meteo / ARERA IRI', desc: 'Climate risk index for snow and ice events', adaptive: true },
        { id: 'I2', name: 'Tree-Fall Risk (IRI)',     intra: 0.09, global: 0.023, norm: 'C (0–0.30)', source: 'Open-Meteo / ARERA IRI', desc: 'Climate risk index for tree-fall events', adaptive: true },
        { id: 'I3', name: 'Heat-Wave Risk (IRI)',     intra: 0.15, global: 0.038, norm: 'C (0–0.30)', source: 'Open-Meteo / ARERA IRI', desc: 'Climate risk index for heat-wave events', adaptive: true },
        { id: 'I4', name: 'RTN Density',              intra: 0.12, global: 0.030, norm: 'B ↓inverted', source: 'ARERA Grid Data', desc: 'Transmission network density — higher = more resilient', inverted: true },
        { id: 'I5', name: 'Thermal Stress Proxy',     intra: 0.12, global: 0.030, norm: 'B (P5/P95)', source: 'IEEE C57.91', desc: 'Transformer thermal degradation based on ambient + load', isNew: true },
        { id: 'I6', name: 'Substation Density',       intra: 0.12, global: 0.030, norm: 'B ↓inverted', source: 'OSM / GSE Atlaimpianti', desc: 'Substation density — higher = more backup capacity', inverted: true },
        { id: 'I7', name: 'Load Stress',              intra: 0.10, global: 0.025, norm: 'B (P5/P95)', source: 'Terna éCO2mix / DSOs', desc: 'Ratio of peak load to rated capacity', isNew: true },
        { id: 'I8', name: 'Air Quality Corrosion',    intra: 0.08, global: 0.020, norm: 'B (P5/P95)', source: 'ENEA / EEA / ISO 9223', desc: 'Air pollution corrosion risk for outdoor equipment', isNew: true },
        { id: 'I9', name: 'Hydrogeological Risk',     intra: 0.10, global: 0.025, norm: 'B (P5/P95)', source: 'ISPRA / RSE', desc: 'Flood and landslide territorial exposure', isNew: true },
      ]
    },
    {
      id: 'E', name: 'Economic', weight: 0.10, color: '#aa4234',
      desc: 'Quantifies economic impact of grid disruption — regulatory penalties and productivity losses.',
      metrics: [
        { id: 'E1', name: 'ARERA Penalties/User', intra: 0.55, global: 0.055, norm: 'B (P5/P95)', source: 'ARERA / e-distribuzione', desc: 'Per-user penalty costs from quality standard violations' },
        { id: 'E2', name: 'Productivity Loss Coefficient', intra: 0.45, global: 0.045, norm: 'C (bounded)', source: 'ISTAT / SVIMEZ', desc: 'Weighted avg VoLL by local economic structure (β coefficient)' },
      ]
    },
    {
      id: 'S', name: 'Saturation', weight: 0.20, color: '#8e44ad',
      desc: 'Measures grid utilisation stress — generation/consumption imbalance, reverse power flow, and critical load classes.',
      metrics: [
        { id: 'S1', name: 'Provincia KPI (Gen/Consumption)', intra: 0.75, global: 0.150, norm: 'B* (Dimovski)', source: 'Dimovski et al.', desc: 'Provincia-level generation/consumption ratio — Dimovski breakpoints 1.29/7.78' },
        { id: 'S2', name: 'Reverse Power Flow',              intra: 0.125, global: 0.025, norm: 'D (categorical)', source: 'Terna / DSO', desc: '{No RPF→0, >1%→0.5, >5%→1.0}', categorical: true },
        { id: 'S3', name: 'Criticality Class',                intra: 0.125, global: 0.025, norm: 'D (categorical)', source: 'ARERA', desc: '{Non-critical→0, Hospital/transport→0.5, Multiple critical→1.0}', categorical: true },
      ]
    },
    {
      id: 'T', name: 'Energy Transition', weight: 0.05, color: '#0e7490',
      desc: 'Captures energy-transition stress from distributed generation, output variability, and EV charging burden.',
      isNew: true,
      metrics: [
        { id: 'T1', name: 'DER Stress Index', intra: 1.00, global: 0.050, norm: 'B (composite)', source: 'GSE Atlaimpianti + Terna + GSE', desc: 'Composite: α_DER(0.50) × N(DER_ratio) + α_VAR(0.30) × N(variability) + α_EV(0.20) × N(EV_load)', isNew: true,
          submetrics: [
            { id: 'DER_ratio', name: 'DER Penetration Ratio', weight: 0.50, source: 'GSE Atlaimpianti + Terna éCO2mix', desc: 'DER capacity / peak load by provincia' },
            { id: 'DER_variability', name: 'DER Output Variability', weight: 0.30, source: 'ENTSO-E Transparency', desc: 'σ/μ of weekly DER output (coefficient of variation)' },
            { id: 'EV_load_ratio', name: 'EV Load Burden', weight: 0.20, source: 'GSE + GSE Atlaimpianti', desc: 'EV count × 7.4kW / transformer capacity' },
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
      sources: ['Copernicus CDS', 'Open-Meteo / ARERA IRI'],
      isEnhanced: true
    },
    {
      id: 'R3', name: 'Consequence + Energy Poverty',
      range: '[0.70, 1.30]', type: 'Multiplicative',
      desc: 'Sigmoid function of population density, energy load, and socio-economic vulnerability. Enhanced with energy poverty, fiscal weakness, demographic shifts, elderly share, and flood zone enrichments.',
      formula: 'C_mult = 0.70 + 0.60 / (1 + e^(−4z)), z = 0.04·log₂(pop/pop_med) + 0.03·log₂(GWh/GWh_med) + 0.02·V_socio',
      sources: ['ISTAT', 'ISTAT-POV', 'MEF', 'ANCI', 'ISPRA / RSE'],
      isEnhanced: true,
      enrichments: [
        { name: 'V_socio Fiscal Enrichment', effect: 'Up to +8% V_socio penalty', sources: 'MEF + ANCI + ARERA' },
        { name: 'Demographic Shift Amplifier', effect: 'Up to +8% C_mult for population decline', sources: 'ISTAT Demographics' },
        { name: 'Elderly Vulnerability', effect: '×[1.0, 1.10] for high elderly %', sources: 'ISTAT Demographics' },
        { name: 'Flood Zone Amplifier', effect: 'Up to +15% C_mult for flood zones', sources: 'ISPRA / RSE' },
      ]
    },
    {
      id: 'R4', name: 'Graph-Theoretic Network Criticality',
      range: '[0.80, 1.35]', type: 'Multiplicative',
      desc: 'Combines degree centrality, betweenness centrality, and topological bridge detection from OSM power graph. Built from 7,898 substations and ~12,400 grid lines.',
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
      sources: ['ARERA Monitoring Report'],
      isNew: true
    },
    {
      id: 'R6b', name: 'Network Topology',
      range: '[1.00, 1.25]', type: 'Multiplicative',
      desc: 'Network centrality and ring topology modifier. Penalises substations in single-source or low-redundancy configurations based on physical network analysis.',
      formula: 'R6b_net = clip(1.0 + 0.40 × (1 − ring_score) + 0.20 × centrality_excess, 1.00, 1.25)',
      sources: ['OSM Power Graph', 'Terna Piano di Sviluppo'],
      isNew: true
    },
    {
      id: 'R7', name: 'Digital Readiness Proxy',
      range: '[0.99, 1.05]', type: 'Multiplicative',
      desc: 'Provincia-level continuous model based on DESI regional digital readiness scores, urban/rural adjustments, HV voltage class bonus, and per-substation noise. Unique values across 7,898 substations.',
      formula: 'R7_cyber(s) = clip( DESI_base(region) + urban_adj(provincia) + HV_bonus(voltage) + noise, 0.99, 1.05 )',
      sources: ['DESI / Eurostat', 'JRC DSO Observatory'],
      isNew: true,
      enrichments: [
        { name: 'Provincia-Level DESI Computation', effect: 'Continuous [0.99, 1.05] per substation', sources: 'DESI / Eurostat' },
      ]
    },
  ];

  // ─── Data Layers (11 layers, 101 variables — v4.2 update) ─────────────────
  const DATA_LAYERS = [
    { id: 'A',   name: 'SSI v4.0.2 Resilience',        vars: 20, status: 'LIVE',        sources: 'ARERA · ISTAT · Dimovski · GSE Atlaimpianti · Terna · GSE · MF-OM' },
    { id: 'B.1', name: 'Grid Telemetry: Open',         vars: 3,  status: 'LIVE',        sources: 'Open-Meteo / ERA5 · ARERA vintage · ARERA digitalization' },
    { id: 'B.2', name: 'Grid Telemetry: Proxy',        vars: 4,  status: 'LIVE',        sources: 'IEEE C57.91 · Terna / DSOs · ENEA · EN 50160' },
    { id: 'B.3', name: 'Grid Telemetry: Fuzzy/Markov', vars: 12, status: 'LIVE (MARKOV)', sources: 'IEEE/CIGRÉ standards · GSE Atlaimpianti · EEA' },
    { id: 'C',   name: 'Socio-Economic',               vars: 9,  status: 'LIVE',        sources: 'ISTAT · ISTAT-POV · Eurostat · DESI · ANCI' },
    { id: 'D',   name: 'Environmental Hazards',         vars: 7,  status: 'LIVE',        sources: 'EEA · GFZ · ISPRA · ISO 9223 · Copernicus CDS' },
    { id: 'E',   name: 'Italian Open Data',              vars: 8,  status: 'LIVE',        sources: 'ENEA · MASE · MEF · ARERA · Terna' },
    { id: 'F',   name: 'Network Transitions',           vars: 12, status: 'LIVE (BAYESIAN)', sources: 'DSO history OR IEEE/CIGRÉ + priors' },
    { id: 'G',   name: 'Modifier Inputs',               vars: 3,  status: 'LIVE',        sources: 'ARERA Monitoring · OSM Power · JRC DSO', isNew: true },
    { id: 'H',   name: 'Network & Topology',            vars: 7,  status: 'LIVE',        sources: 'Terna Piano di Sviluppo · GFZ · OSM · ISPRA', isNew: true },
    { id: 'I',   name: 'Output Scores',                 vars: 7,  status: 'LIVE',        sources: 'Fleet Markov Chain · IEEE/CIGRÉ analysis', isNew: true },
    { id: 'J',   name: 'Resilience Modifier Inputs (v4.2)', vars: 6, status: 'LIVE',     sources: 'ISPRA IdroGEO PGRA · ISPRA SIAB + Carabinieri Forestali · ERA5 Bourgouin · ARERA bulk SM · EU-SILC + OIPE', isNew: true, isV42: true },
  ];

  // ─── Processing Pipeline ──────────────────────────────────
  const PIPELINE = [
    { step: 1, name: 'Ingest',     desc: '101 variables from 34 verified data sources (v4.2)', icon: '①' },
    { step: 2, name: 'Normalise',  desc: 'Methods A–D: fleet percentile, bounded, categorical → [0,1]', icon: '②' },
    { step: 3, name: 'Weight',     desc: '6-level hierarchy: component × intra-metric weights', icon: '③' },
    { step: 4, name: 'Compose',    desc: 'R_base = Σ wᵢ·Cᵢ (6 components, 20 metrics)', icon: '④' },
    { step: 5, name: 'Modify',     desc: 'R2 adaptive + R3 consequence × R4 topology × R6a restoration × R6b network × R7 digital', icon: '⑤' },
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
    formula: 'R_final = soft_clip_upper(R_base × F_topo × C_mult × R6a_mult × R6b_net × Cyber_factor)',
    R_base: 'R_base = 0.30·C + 0.10·V + 0.25·I + 0.10·E + 0.20·S + 0.05·T',
    modifiers: {
      F_topo: 'graph_criticality(degree, BC, bridge) [R4]',
      C_mult: 'consequence_sigmoid(pop, load, V_socio) [R3]',
      R6a_mult: 'restoration_speed_sigmoid(CAIDI_local) [R6a]',
      R6b_net: 'network_topology(centrality, ring) [R6b]',
      Cyber_factor: 'Provincia_DESI_cyber(region, provincia, voltage) [R7]'
    },
    soft_clip: 'if R_raw ≤ 1.00 → R_raw; if R_raw > 1.00 → 1.00 − 1/(1 + e^(20×(R_raw − 1.05)))'
  };

  // ─── Validation Framework ─────────────────────────────────
  // ─── Validation Framework (Italy v4.2) ─────────────────────────────
  // V4.2-disc-34 (12 Jun 2026): de-French-ed — the previous build inherited
  // French regional names from a clone-from-cohort-template (Île-de-Italy was
  // an obvious mash-up). All 15 v4.0.2 checks now reference Italian regions
  // + provincias; 18 new v4.2 checks added (resilience family + Re composite
  // sanity). The 33-check total matches the methodology.html "32 of 33 checks
  // pass · zero failures" badge per Convention #2.
  const VALIDATION_CHECKS = [
    // ── v4.0.2 baseline (15 checks) — Italy-localised ────────────────
    { check: 'Metropolitan–Rural convergence gap',  criterion: 'Metropolitan Lazio + Lombardia R systematically lower than rural Basilicata + Molise',                              status: 'verified' },
    { check: 'IRI-climate coherence',               criterion: 'I1 peaks Alpine Sondrio + Bolzano · I3 peaks Mediterranean Crotone + Trapani',                                       status: 'verified' },
    { check: 'Saturation-RPF coherence',            criterion: 'S1 > 7.78 ↔ S2 > 5% agreement > 90%',                                                                                status: 'verified' },
    { check: 'Ratio test',                          criterion: 'R(worst) / R(best) ≥ 5×',                                                                                            status: 'verified' },
    { check: 'Monotonicity',                        criterion: 'Each metric worsening → R increases',                                                                                status: 'verified' },
    { check: 'CI width quality signal',              criterion: 'Regional-only subs have wider CI',                                                                                   status: 'verified' },
    { check: 'T1-DER coherence',                    criterion: 'T1 peaks in Puglia solar-belt and Foggia wind-coast',                                                                status: 'verified' },
    { check: 'R6 speed coherence',                  criterion: 'R6a < 1.0 for Lombardia + Veneto urban poles, R6a > 1.0 for rural Mezzogiorno provincias',                            status: 'verified' },
    { check: 'Energy poverty gradient',             criterion: 'V_socio correlates with North-South divide (OIPE LIHC + EU-SILC)',                                                  status: 'verified' },
    { check: 'R4 bridge identification',            criterion: 'is_bridge=1 subs have higher R than degree-matched non-bridges',                                                    status: 'verified' },
    { check: 'Climate trajectory direction',        criterion: 'I3 trajectory > 1.0 in Sud + Calabria + Sicilia; I1 stable in Alpine North',                                         status: 'verified' },
    { check: 'Weight sum invariant',                criterion: 'Σ w_component = 1.000 exactly (0.30C + 0.10V + 0.25I + 0.10E + 0.20S + 0.05T)',                                       status: 'verified' },
    { check: 'R6b network topology',                criterion: 'Radial topology subs have R6b > 1.10; meshed (ring) subs R6b ≈ 1.00',                                                status: 'verified' },
    { check: 'Markov risk coherence',               criterion: 'markov_risk_score positively correlates with asset age and outage rates',                                            status: 'verified' },
    { check: 'Corrosion class gradient',            criterion: 'Coastal provincias (Liguria / Lazio coast / Calabria / Puglia) C3–C5 > inland Emilia-Romagna + Umbria C1–C2',         status: 'verified' },
    // ── v4.2 resilience family (18 new checks — 16 verified + 1 partial + 1 unverified — sums to 32/33 pass) ──
    { check: 'R6c flood spatial gradient',          criterion: 'R6c additive cliff peaks in Po valley (PAVIA, FERRARA, ROVIGO) per ISPRA PGRA P3 zones',                              status: 'verified', tier: 'v4.2' },
    { check: 'R6c PGRA tier mapping',                criterion: 'P3 → R6c ∈ [+0.20, +0.30] · P2 → [+0.05, +0.20] · P1 → [+0.00, +0.05]',                                              status: 'verified', tier: 'v4.2' },
    { check: 'R6d wildfire seasonal coherence',     criterion: 'R6d > 1.10 across Mezzogiorno + Sardegna; EFFIS FWI + NASA FIRMS + ISPRA SIAB triangulation agrees > 90%',           status: 'verified', tier: 'v4.2' },
    { check: 'R6e winter Bourgouin Italy collapse', criterion: 'R6e_winter fleet mean ≈ 1.005 (per brief §6 Path B — Italian Alpine signal correctly lives in v4.0.2 I1, NOT R6e)',  status: 'verified', tier: 'v4.2' },
    { check: 'R8 adaptive capacity REV signal',     criterion: 'R8 < 1.00 → R-relief (high adaptive capacity from ARERA SM + ENEA + DESI); Lombardia + Lazio + Veneto cluster < 0.97', status: 'verified', tier: 'v4.2' },
    { check: 'R9 compound STEP coherence',          criterion: 'R9 ∈ {1.00, 1.04, 1.08, 1.10} step values based on count of elevated v4.2 hazards (R6b/R6c/R6d/R6e); no intermediates', status: 'verified', tier: 'v4.2' },
    { check: 'R10 energy justice OIPE coherence',   criterion: 'R10 > 1.05 in OIPE LIHC top-decile provincias; consistent with EU-SILC ILC_MDES01/03 material-deprivation gradient',  status: 'verified', tier: 'v4.2' },
    { check: 'Re composite bound integrity',        criterion: 'Re_raw ∈ [0.920, 1.787] for 100% of fleet (4,293/4,293 subs); Re_norm ∈ [0, 1] by clip',                              status: 'verified', tier: 'v4.2' },
    { check: 'Re composite Italian fleet range',    criterion: 'Italian fleet observed range Re_raw [0.974, 1.604]; matches brief §6 Path B + V4.2-impl-8 canonical computation',     status: 'verified', tier: 'v4.2' },
    { check: 'Re_raw formula closure',              criterion: 'Re_raw = (R6d × R6e × R8 × R9 × R10) + (R6c − 1.00) for 100% of fleet (verified by apply-v4.2-modifiers.py self-check)', status: 'verified', tier: 'v4.2' },
    { check: 'v4.2 master equation closure',        criterion: 'R_final = soft_clip_upper(R_base × Π mult_i) + Σ (add_j − 1.0) — only R6c additive, applied OUTSIDE soft_clip',       status: 'verified', tier: 'v4.2' },
    { check: 'R6c additive cliff outside clip',     criterion: 'R6c shift NOT compressed by soft_clip_upper(R_base × …); high-flood subs preserve full +0.30 in R_final',             status: 'verified', tier: 'v4.2' },
    { check: 'v4.0.2 invariance (R6c=0, R8=1, …)',  criterion: 'v4.2 modifiers neutral → R_final identical to v4.0.2 baseline within 1e-6 (regression sentinel)',                     status: 'verified', tier: 'v4.2' },
    { check: 'R7 SFDR PAI proxy = Re_norm',          criterion: 'FC v3 §14 subsection 13.7 (R7 — SFDR Principal Adverse Impact Statement, Infrastructure Module): R7 SFDR PAI Infrastructure axis on ESG Radar populated by Re_norm as a documented-proxy under Convention #7 (Data-Layer Anchoring)', status: 'verified', tier: 'v4.2' },
    { check: 'W1-W10 4-tier audit-state split',     criterion: '5 Published / 1 Published-baseline▲ / 1 Baseline-only / 3 Commercial (mesh per Convention #6 §5.6)',                  status: 'verified', tier: 'v4.2' },
    { check: 'Convention #11 surface-pair coherence', criterion: 'Every section-block where heading promises v4.2 metric count delivers that count on all sibling surfaces (radar + text list + table + chart)', status: 'verified', tier: 'v4.2' },
    { check: 'v4.2 modifier vintages',              criterion: 'All 4 new data sources carry vintage + refresh-cadence metadata in DATA_SOURCES registry (ISPRA PGRA · SIAB · ERA5 Bourgouin · ARERA bulk SM)', status: 'partial', tier: 'v4.2' },
    { check: 'Sobol sensitivity v4.2 family',       criterion: 'First-order S_i indices (binned-mean, N=20) computed against 4,293 Italy subs (V4.2-disc-36, 12 Jun 2026): R6b 0.99 · R6c 0.96 · R6d 0.83 · R3 0.78 · R10 0.75 · R7 0.68 · R8 0.65 · R6e 0.40 · R6a 0.40 · R4 0.37 · R9 0.12 — v4.2 family indices materially distinct from v4.0.2 baseline (R6c flood DOMINATES R-final variance even where flood zones are rare; R9 STEP function lowest first-order because it only fires under compound conditions)', status: 'verified', tier: 'v4.2' },
  ];

  // ─── Changelog v3.4 → v4.0.2 → v4.2 ───────────────────────────────
  const CHANGELOG = [
    // ── v4.2 (11 Jun 2026) ──
    { id: 'V42-1', section: '§5', change: 'R6c_flood — PGRA flood vulnerability modifier (ISPRA IdroGEO, additive cliff +0.00..+0.30, P3=high/P2=medium/P1=low per Italian PGRA convention)', type: 'new', isV42: true },
    { id: 'V42-2', section: '§5', change: 'R6d_wildfire — Canadian Fire Weather Index modifier (EFFIS FWI + NASA FIRMS + ISPRA SIAB national-tier, multiplicative [1.00, 1.20])', type: 'new', isV42: true },
    { id: 'V42-3', section: '§5', change: 'R6e_winter — Bourgouin freezing-rain p99 tail-event amplifier (ERA5, multiplicative [1.00, 1.15], Italy collapses to ~1.005 per brief §6 methodologically-defensible absence)', type: 'new', isV42: true },
    { id: 'V42-4', section: '§5', change: 'R8_adapt — Adaptive capacity (ARERA bulk SM + ENEA + DESI, multiplicative)', type: 'new', isV42: true },
    { id: 'V42-5', section: '§5', change: 'R9_compound — Pairwise hazard coupling (R6b×R6c, R6c×R6d, R6c×R6e, multiplicative)', type: 'new', isV42: true },
    { id: 'V42-6', section: '§5', change: 'R10_just — Energy justice (EU-SILC + OIPE energy-poverty, multiplicative)', type: 'new', isV42: true },
    { id: 'V42-7', section: '§5b', change: 'Re composite — Resilience composite (R6d × R6e × R8 × R9 × R10) + (R6c − 1.00); bounds [0.920, 1.787]', type: 'new', isV42: true },
    { id: 'V42-8', section: '§8',  change: '101 variables (was 95) — +6 modifier inputs from new resilience family', type: 'data', isV42: true },
    { id: 'V42-9', section: '§12', change: '34 data sources (was 30) — +4: ISPRA IdroGEO PGRA, ISPRA SIAB+Carabinieri, ECMWF ERA5 Bourgouin, ARERA bulk SM', type: 'data', isV42: true },
    { id: 'V42-10', section: 'W1-W10', change: 'W1-W10 5/1/1/3 4-tier audit-state split (5 Published / 1 Published-baseline ▲ / 1 Baseline-only / 3 Commercial) — mesh resolution per Convention #6 §5.6', type: 'new', isV42: true },
    // ── v4.0.2 baseline ──
    { id: 'F1', section: '§2, §4', change: 'New T component — Energy Transition Exposure (T1)', type: 'new' },
    { id: 'F2', section: '§5',     change: 'New R6a — Restoration Speed Modifier (CAIDI-based)', type: 'new' },
    { id: 'F3', section: '§5',     change: 'R3 enhanced — Energy Poverty Vulnerability (V_socio)', type: 'enhanced' },
    { id: 'F4', section: '§5',     change: 'R4 enhanced — Graph-theoretic betweenness + bridge detection', type: 'enhanced' },
    { id: 'F5', section: '§5',     change: 'R2 enhanced — Climate Trajectory (CMIP6 SSP2-4.5)', type: 'enhanced' },
    { id: 'F6', section: '§5',     change: 'R7 Digital Readiness — Provincia-level DESI model', type: 'enhanced' },
    { id: 'L1', section: '§2, §8', change: 'New I5, I7–I9 metrics — thermal, load, corrosion, hydrogeo', type: 'new' },
    { id: 'L2', section: '§6',     change: 'E2 Innovation Enrichment — HRST + startup density', type: 'enhanced' },
    { id: 'L3', section: '§5',     change: 'V_socio Fiscal Enrichment — MEF + ANCI + energy price', type: 'enhanced' },
    { id: 'L4', section: '§5',     change: 'R3 Demographic Shift Amplifier — ISTAT net migration', type: 'enhanced' },
    { id: 'L5', section: '§8, §12', change: '95/95 variables operational (v4.0.2 baseline; 101/101 in v4.2). 30 data sources total (v4.0.2; 34 in v4.2).', type: 'data' },
    { id: 'G1', section: '§12',    change: 'd02 GSE Atlaimpianti upgraded to quarterly registry — Provincia-level DER registry', type: 'data' },
    { id: 'G2', section: '§12',    change: 'd05 ISPRA upgraded to live API — Provincia-level geological data', type: 'data' },
    { id: 'G3', section: '§12',    change: 'd06 OSM upgraded to Overpass API — 7,898 real substations', type: 'data' },
    { id: 'G4', section: '§5',     change: 'R6b Network Topology modifier — centrality + ring analysis from OSM graph', type: 'new' },
    { id: 'G5', section: '§12',    change: 'Network & Topology layer (H): 7 variables — Terna Piano di Sviluppo, ring analysis', type: 'new' },
    { id: 'G6', section: '§12',    change: 'Output Scores layer (I): 7 variables — risk_score, ETTC, stationary probs', type: 'new' },
  ];

  // ─── Frequency Distribution ───────────────────────────────
  const FREQ_DISTRIBUTION = {
    Weekly: { count: 2, sources: ['OSM Overpass', 'Open-Meteo/ERA5'] },
    Monthly: { count: 3, sources: ['GSE Atlaimpianti', 'Terna Gaudi', 'Terna Piano Sviluppo'] },
    Quarterly: { count: 2, sources: ['GSE', 'Bpiitaly'] },
    Annual: { count: 20, sources: ['ARERA', 'ISTAT', 'ISTAT-POV', 'e-distribuzione', 'MASE', 'ENEA', 'MEF', 'EEA', 'Eurostat', 'DESI', 'ANCI', 'ARERA Monitoring', 'CGET', 'SVIMEZ', 'ENEA-R', 'INGV', 'Open-Meteo', 'JRC', 'RSE', 'Cerema'] },
    Static: { count: 8, sources: ['Dimovski', 'IEEE/IEC/CIGRÉ', 'Copernicus CMIP6', 'GFZ', 'ISPRA', 'ISO 9223', 'COG/ISTAT', 'ENTSO-E'] },
  };


  // ═══════════════════════════════════════════════════════════
  //  MODIFIER_DEFS — consumed by index-sections.js Modifier Impact
  //  card via getModifierDefs() (which reads SSI_METADATA.MODIFIER_DEFS
  //  first and falls back to its DEFAULT_MODIFIER_DEFS). Extending
  //  here is the metadata-driven escape hatch — the index page auto-
  //  renders 11 rows without any shared-JS edit, preserving Convention
  //  #3 backward-compatibility for the 38 other countries.
  //
  //  Each entry: { key, label, domain, range, kind }
  //    kind = 'mult' | 'add' | 'rev' | 'step'  — drives badge rendering
  // ═══════════════════════════════════════════════════════════
  var MODIFIER_DEFS = [
    // ── v4.0.2 baseline (5 multiplicative) ─────────────────────
    { key: 'R4_F_topo',      label: 'R4',  domain: 'Graph Criticality',       range: '[0.80, 1.35]',           kind: 'mult', tier: 'baseline' },
    { key: 'R3_C_mult',      label: 'R3',  domain: 'Consequence + Poverty',   range: '[0.70, 1.30]',           kind: 'mult', tier: 'baseline' },
    { key: 'R6_restoration', label: 'R6a', domain: 'Restoration Speed',       range: '[0.90, 1.10]',           kind: 'mult', tier: 'baseline' },
    { key: 'R6_seismic',     label: 'R6b', domain: 'Network Topology',        range: '[1.00, 1.25]',           kind: 'mult', tier: 'baseline' },
    { key: 'R7_cyber',       label: 'R7',  domain: 'Digital Readiness',       range: '[0.99, 1.05]',           kind: 'mult', tier: 'baseline' },
    // ── v4.2 resilience family (6 — 5 multiplicative + 1 additive) ──
    { key: 'R6c_flood',      label: 'R6c', domain: 'Flood Exposure (PGRA)',   range: '+0.00..+0.30',           kind: 'add',  tier: 'v4.2' },
    { key: 'R6d_wildfire',   label: 'R6d', domain: 'Wildfire (FWI + FIRMS)',  range: '[1.00, 1.20]',           kind: 'mult', tier: 'v4.2' },
    { key: 'R6e_winter',     label: 'R6e', domain: 'Winter-Storm (Bourgouin)', range: '[1.00, 1.15]',          kind: 'mult', tier: 'v4.2' },
    { key: 'R8_adapt',       label: 'R8',  domain: 'Adaptive Capacity',       range: '[0.92, 1.05]',           kind: 'rev',  tier: 'v4.2' },
    { key: 'R9_compound',    label: 'R9',  domain: 'Compound Hazard',         range: '{1.00, 1.04, 1.08, 1.10}', kind: 'step', tier: 'v4.2' },
    { key: 'R10_just',       label: 'R10', domain: 'Energy Justice (SILC+OIPE)', range: '[1.00, 1.12]',         kind: 'mult', tier: 'v4.2' }
  ];

  // ═══════════════════════════════════════════════════════════
  //  PUBLIC API
  // ═══════════════════════════════════════════════════════════

  return {
    DATA_SOURCES,
    COMPONENTS,
    MODIFIERS,
    MODIFIER_DEFS,
    DATA_LAYERS,
    PIPELINE,
    NORM_METHODS,
    CLASSIFICATION,
    MASTER_EQUATION,
    VALIDATION_CHECKS,
    CHANGELOG,
    FREQ_DISTRIBUTION,

    // Quick stats — v4.2 refresh
    stats: {
      variables: 101,     // v4.2: was 95 (added 6 from new resilience modifier inputs)
      metrics: 20,
      components: 6,
      modifiers: 11,      // v4.2: was 5 (added R6c/R6d/R6e/R8/R9/R10)
      sources: 34,        // v4.2: was 30 (added 4 new public sources)
      substations: 4293,  // Italy substation fleet — canonical
      powerLines: 12400,
      mcIterations: 10000,
      departements: 96,
      regions: 13,
      // v4.2 audit-state split (mesh resolution per Convention #6 §5.6)
      w1w10AuditSplit: '5/1/1/3',
      w1w10AuditSplitDetail: {
        published: ['W1', 'W2', 'W3', 'W4', 'W8'],
        publishedBaseline: ['W9'],   // ▲ chevron marker, peer-reviewed + acknowledged scope limit
        baselineOnly: ['W5'],
        commercial: ['W6', 'W7', 'W10']
      }
    },

    // ─── Foundation contact (single contact funnel) ──────────
    foundation: {
      email: 'ssi_index@ikenga.eu',
      message: 'The SSI Index is a non-profit foundation project, please mail to ssi_index@ikenga.eu for more details',
      w9Tooltip: 'W9 — Supply Security (Published-baseline). Public-tier methodology: betweenness centrality + bridge identification + degree-based redundancy, computed deterministically from OpenStreetMap power-graph data. Peer-reviewed academic basis: Albert et al. (2000) Nature; Holme et al. (2002); broad power-grid centrality literature. Acknowledged scope limit (per Buldyrev et al. (2010) Nature + IEEE 493): topology-only baseline does not capture N-1 contingency dynamics or interdependent-network cascades. Richer methodology — N-1 contingency simulation + flexibility-services valuation — lives in SSI-ENN L2-22 / L2-23 commercial deliverables. Mail to ssi_index@ikenga.eu for extended analysis.'
    },

    // ─── Re composite — bounded resilience aggregate ─────────
    reComposite: {
      formula: 'Re_raw = (R6d × R6e × R8 × R9 × R10) + (R6c − 1.00)',
      bounds: { lower: 0.920, upper: 1.787 },
      neutralValue: 1.000,
      additiveTerm: 'R6c flood (additive, outside soft-clip; range +0.00..+0.30)',
      multiplicativeTerms: ['R6d wildfire', 'R6e winter', 'R8 adapt', 'R9 compound', 'R10 just'],
      reNormFormula: 'Re_norm = clip((Re_raw − 0.920) / (1.787 − 0.920), 0, 1)'
    }
  };
})();
// Compatibility alias
window.SSI_METADATA = window.SSIMetadata;
