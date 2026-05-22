/* ═══════════════════════════════════════════════════════════
   SSI v4.0.2 — Metadata Registry (Germany)
   95 variables · 35 sources · 20 metrics · 6 components · 8 modifiers
   Complete reference data for methodology page + data page
   Session 22 · KB §54 · DACH cohort completion (AT → CH → DE)
   ═══════════════════════════════════════════════════════════ */

window.SSIMetadata = (function () {
  'use strict';

  // ─── 35 Verified Data Sources (Germany) ───────────────────
  const DATA_SOURCES = [
    { id: 'BNETZ',  name: 'BNetzA (Bundesnetzagentur)',              url: 'bundesnetzagentur.de',                  freq: 'Annual',    res: 'Landkreis',       vars: 8,  category: 'Grid',          feeds: 'C1–C4 (SAIDI/SAIFI), I1–I3 (IRI), quality regulation' },
    { id: '50HZ',   name: '50Hertz Netzentwicklungsplan',             url: '50hertz.com',                           freq: 'Annual',    res: 'Control area NE', vars: 2,  category: 'Grid',          feeds: 'T1 + H layer (NE control area: BB+MV+SN+ST+TH+BE+HH partial)' },
    { id: 'AMPR',   name: 'Amprion Netzentwicklungsplan',             url: 'amprion.net',                           freq: 'Annual',    res: 'Control area W',  vars: 2,  category: 'Grid',          feeds: 'T1 + H layer (W control area: NW+RP+SL)' },
    { id: 'TENN',   name: 'TenneT TSO DE Netzentwicklungsplan',       url: 'tennet.eu',                             freq: 'Annual',    res: 'Control area N-S',vars: 2,  category: 'Grid',          feeds: 'T1 + H layer (N-S corridor: SH+NI+HB+HE+BY+HH partial; incl. SuedLink + SuedOstLink)' },
    { id: 'TRBW',   name: 'TransnetBW Netzentwicklungsplan',          url: 'transnetbw.de',                         freq: 'Annual',    res: 'Control area SW', vars: 1,  category: 'Grid',          feeds: 'T1 + H layer (SW: BW sole control area; incl. Ultranet terminus)' },
    { id: 'DESTAT', name: 'DESTATIS (Statistisches Bundesamt)',       url: 'destatis.de',                           freq: 'Annual',    res: 'Landkreis (NUTS-3)',vars: 8,  category: 'Socio-Econ',    feeds: 'R3 population, elderly, GDP, fiscal capacity (16 Länder × 401 Landkreise × 11,054 Gemeinden)' },
    { id: 'BGR',    name: 'BGR Geowissenschaften und Rohstoffe',      url: 'bgr.bund.de',                           freq: 'Static',    res: 'Landkreis',       vars: 3,  category: 'Hazard',        feeds: 'R6b Rhine Graben seismic PGA 475-yr (Karlsruhe+Köln+Aachen+Mainz 0.08g)' },
    { id: 'OSM',    name: 'OSM Power Infrastructure',                  url: 'overpass-api.de',                       freq: 'Weekly',    res: 'Node/edge',       vars: 3,  category: 'Infrastructure',feeds: 'R4 graph topology, BC, bridges · ~6,500 substations (post-§38+§52 filter; largest OECD fleet)' },
    { id: 'COPER',  name: 'Copernicus CDS / ERA5',                    url: 'cds.climate.copernicus.eu',             freq: 'Static',    res: '0.25° (~25 km)',  vars: 4,  category: 'Climate',       feeds: 'R2 Δ_climate (I1–I3 trajectory)', registration: true },
    { id: 'ENTSE',  name: 'ENTSO-E Transparency',                     url: 'transparency.entsoe.eu',                freq: 'Hourly',    res: 'Bidding zone',    vars: 2,  category: 'Transition',    feeds: 'T1 DER variability, cross-border flows (DE-LU bidding zone)', registration: true },
    { id: 'UBA',    name: 'UBA Umweltbundesamt',                      url: 'umweltbundesamt.de',                    freq: 'Annual',    res: 'Landkreis',       vars: 4,  category: 'Environment',   feeds: 'I8 air quality, PM2.5, NO₂, O₃ corrosion' },
    { id: 'DWD',    name: 'DWD (Deutscher Wetterdienst)',             url: 'dwd.de',                                freq: 'Daily',     res: '~1 km',           vars: 3,  category: 'Climate',       feeds: 'I1–I3 snow/ice, storms, heat-wave events' },
    { id: 'BFG',    name: 'BfG Bundesanstalt für Gewässerkunde',      url: 'bafg.de',                               freq: 'Annual',    res: 'Landkreis',       vars: 2,  category: 'Hazard',        feeds: 'R6c flood — Rhine + Elbe + Danube + North Sea storm surge basins (2021 Ahr valley ref event)' },
    { id: 'LFUBY',  name: 'LfU Bayern (Landesamt für Umwelt)',        url: 'lfu.bayern.de',                         freq: 'Annual',    res: 'Bavarian LK',     vars: 1,  category: 'Hazard',        feeds: 'R6c Danube + alpine sub-basin flood (Bayern only)' },
    { id: 'IEEE-1', name: 'IEEE C57.91 / IEC 60076',                   url: 'standards.ieee.org',                    freq: 'Static',    res: 'Asset-level',     vars: 16, category: 'Standards',     feeds: 'I5 thermal model, B.3 Markov states' },
    { id: 'JRC',    name: 'JRC DSO Observatory',                       url: 'ses.jrc.ec.europa.eu',                  freq: 'Annual',    res: 'DSO-level',       vars: 2,  category: 'Grid',          feeds: 'R7 Landkreis-level cyber-exposure (secondary; ~800 DSO landscape)' },
    { id: 'EEA',    name: 'EEA Air Quality e-Reporting',               url: 'eea.europa.eu',                         freq: 'Annual',    res: '~1 km + station', vars: 3,  category: 'Environment',   feeds: 'I8 PM2.5, NO₂, O₃ corrosion' },
    { id: 'EURO',   name: 'Eurostat Energy Statistics',                url: 'ec.europa.eu/eurostat',                 freq: 'Annual',    res: 'NUTS2',           vars: 3,  category: 'Economic',      feeds: 'Energy poverty cross-validation' },
    { id: 'DESI',   name: 'DESI Digital Economy Index',                url: 'digital-strategy.ec.europa.eu',         freq: 'Annual',    res: 'EU Regional',     vars: 2,  category: 'Socio-Econ',    feeds: 'R7 Landkreis-level cyber-exposure (DE DESI 0.61, rank ~10/27)' },
    { id: 'BMWK',   name: 'BMWK Wirtschaft + Klimaschutz',             url: 'bmwk.de',                               freq: 'Annual',    res: 'Bundesland',      vars: 2,  category: 'Economic',      feeds: 'Energiewende investment, renewable targets (60% 2024 → 80% 2030)' },
    { id: 'BMU',    name: 'BMU Umwelt + Naturschutz',                  url: 'bmu.de',                                freq: 'Annual',    res: 'Bundesland',      vars: 1,  category: 'Environment',   feeds: 'Environmental risk indicators, spatial planning' },
    { id: 'BMF',    name: 'BMF Bundesfinanzministerium',               url: 'bundesfinanzministerium.de',            freq: 'Annual',    res: 'Landkreis',       vars: 1,  category: 'Socio-Econ',    feeds: 'R3 fiscal enrichment, Landkreis revenue capacity' },
    { id: 'BSI',    name: 'BSI Sicherheit Informationstechnik',       url: 'bsi.bund.de',                           freq: 'Annual',    res: 'KRITIS asset',    vars: 2,  category: 'Grid',          feeds: 'R7 KRITIS registry (per-asset cyber audit since 2015); NIS2 Q4 2024' },
    { id: 'BBANK',  name: 'Bundesbank (Deutsche Bundesbank)',         url: 'bundesbank.de',                         freq: 'Annual',    res: 'Regional',        vars: 2,  category: 'Economic',      feeds: 'E2 productivity loss coefficient, regional accounts (Frankfurt HQ)' },
    { id: 'DENA',   name: 'dena (Deutsche Energie-Agentur)',          url: 'dena.de',                               freq: 'Annual',    res: 'Bundesland',      vars: 2,  category: 'Transition',    feeds: 'Regional energy transition progress, HVDC corridor planning' },
    { id: 'DESTKFZ',name: 'DESTATIS KFZ-Bestand',                     url: 'destatis.de',                           freq: 'Quarterly', res: 'Landkreis',       vars: 1,  category: 'Transition',    feeds: 'T1 EV registration data' },
    { id: 'BBK',    name: 'BBK Bevölkerungsschutz (Civil Protection)',url: 'bbk.bund.de',                           freq: 'Continuous',res: 'Landkreis',       vars: 1,  category: 'Hazard',        feeds: 'Flood zones, KRITIS infrastructure alerts' },
    { id: 'BMUV',   name: 'BMUV Umwelt + Verbraucher',                 url: 'bmuv.de',                               freq: 'Quarterly', res: 'Landkreis',       vars: 1,  category: 'Economic',      feeds: 'E2 innovation enrichment' },
    { id: 'ISO-9223', name: 'ISO 9223 Corrosion',                     url: '(derived from EEA + UBA + DWD)',        freq: 'Derived',   res: 'Landkreis',       vars: 1,  category: 'Environment',   feeds: 'I8 corrosion classification (C2-C5 — DE includes DACH-unique C5 North Sea coast: Friesland+Borkum+Wilhelmshaven)' },
    { id: 'BBSR',   name: 'BBSR Raumordnung',                         url: 'bbsr.bund.de',                          freq: 'Annual',    res: 'Landkreis',       vars: 2,  category: 'Socio-Econ',    feeds: 'R3 regional development gap, East/West differential (post-reunification income gap ~25%)' },
    { id: 'BNMON',  name: 'BNetzA Monitoringbericht',                  url: 'bundesnetzagentur.de',                  freq: 'Annual',    res: 'DSO-level',       vars: 2,  category: 'Grid',          feeds: 'CAIDI, restoration speed (DE SAIDI 11.7 min — EU-best of large economies)' },
    { id: 'GOVDE',  name: 'GovData.de (federal open data)',            url: 'govdata.de',                            freq: 'Annual',    res: 'Landkreis',       vars: 1,  category: 'Socio-Econ',    feeds: 'Urban/rural classification, settlement structure' },
    { id: 'DIW',    name: 'DIW Berlin (Wirtschaftsforschung)',        url: 'diw.de',                                freq: 'Annual',    res: 'Bundesland',      vars: 1,  category: 'Economic',      feeds: 'Regional convergence metrics, East/West income gap monitor' },
    { id: 'AGS',    name: 'AGS Amtlicher Gemeindeschlüssel',          url: 'destatis.de/AGS',                       freq: 'Static',    res: 'Gemeinde (8-digit)',vars: 1,  category: 'Infrastructure',feeds: 'AGS join key, Landkreis-Bundesland-Gemeinde mapping (11,054 Gemeinden)' },
    { id: 'BMI',    name: 'BMI Bundesinnenministerium (KRITIS coord)',url: 'bmi.bund.de',                           freq: 'Annual',    res: 'KRITIS asset',    vars: 1,  category: 'Grid',          feeds: 'KRITIS classification cross-ref (coordinated with BSI)' }
  ];

  // ─── 6 Components ────────────────────────────────────────
  const COMPONENTS = [
    {
      id: 'C', name: 'Continuity', weight: 0.30, color: '#941914',
      desc: 'Measures reliability and outage exposure — how often and how long power interruptions occur.',
      metrics: [
        { id: 'C1', name: 'Outage Duration', intra: 0.40, global: 0.120, norm: 'A (P5/P95)', source: 'BNetzA / dena', desc: 'Total annual interruption duration (SAIDI — DE 11.7 min EU-best of large economies)' },
        { id: 'C2', name: 'Outage Count',    intra: 0.30, global: 0.090, norm: 'A (P5/P95)', source: 'BNetzA / dena', desc: 'Number of interruptions per year (SAIFI)' },
        { id: 'C3', name: 'MT Exceed Rate',  intra: 0.15, global: 0.045, norm: 'C (0–100%)', source: 'BNetzA Monitoringbericht', desc: 'Percentage of time voltage exceeds regulation limits' },
        { id: 'C4', name: 'Planned Outages',  intra: 0.15, global: 0.045, norm: 'B (P5/P95)', source: 'BNetzA Monitoringbericht', desc: 'Duration of planned maintenance interruptions' }
      ]
    },
    {
      id: 'V', name: 'Voltage Quality', weight: 0.10, color: '#b8863a',
      desc: 'Captures voltage dip severity — short-duration voltage reductions that damage sensitive equipment.',
      metrics: [
        { id: 'V1', name: 'Severity-Weighted Dips', intra: 1.00, global: 0.100, norm: 'B (γ=0.50)', source: 'BNetzA Power Quality Report', desc: 'V = N(V1_total × (1 + 0.50 × V2_severe_ratio))' }
      ]
    },
    {
      id: 'I', name: 'Infrastructure', weight: 0.25, color: '#5d8563',
      desc: 'Assesses physical grid condition — environmental exposure, asset density, and material degradation risks.',
      metrics: [
        { id: 'I1', name: 'Snow/Ice Risk (IRI)',     intra: 0.12, global: 0.030, norm: 'C (0–0.30)', source: 'DWD / BNetzA IRI', desc: 'Climate risk index for snow and ice events', adaptive: true },
        { id: 'I2', name: 'Tree-Fall Risk (IRI)',     intra: 0.09, global: 0.023, norm: 'C (0–0.30)', source: 'DWD / BNetzA IRI', desc: 'Climate risk index for tree-fall events', adaptive: true },
        { id: 'I3', name: 'Heat-Wave Risk (IRI)',     intra: 0.15, global: 0.038, norm: 'C (0–0.30)', source: 'DWD / BNetzA IRI', desc: 'Climate risk index for heat-wave events', adaptive: true },
        { id: 'I4', name: 'RTN Density',              intra: 0.12, global: 0.030, norm: 'B ↓inverted', source: '4 TSO Netzentwicklungsplane', desc: 'Transmission network density — higher = more resilient', inverted: true },
        { id: 'I5', name: 'Thermal Stress Proxy',     intra: 0.12, global: 0.030, norm: 'B (P5/P95)', source: 'IEEE C57.91', desc: 'Transformer thermal degradation based on ambient + load', isNew: true },
        { id: 'I6', name: 'Substation Density',       intra: 0.12, global: 0.030, norm: 'B ↓inverted', source: 'OSM / BNetzA Registry', desc: 'Substation density — higher = more backup capacity', inverted: true },
        { id: 'I7', name: 'Load Stress',              intra: 0.10, global: 0.025, norm: 'B (P5/P95)', source: '4 TSOs / DSOs', desc: 'Ratio of peak load to rated capacity', isNew: true },
        { id: 'I8', name: 'Air Quality Corrosion',    intra: 0.08, global: 0.020, norm: 'B (P5/P95)', source: 'UBA / EEA / ISO 9223', desc: 'Air pollution corrosion risk for outdoor equipment (DE has DACH-unique C5 North Sea marine atmosphere)', isNew: true },
        { id: 'I9', name: 'Hydrogeological Risk',     intra: 0.10, global: 0.025, norm: 'B (P5/P95)', source: 'BGR / BfG / LfU Bayern', desc: 'Flood and landslide territorial exposure (2021 Ahr ref)', isNew: true }
      ]
    },
    {
      id: 'E', name: 'Economic', weight: 0.10, color: '#aa4234',
      desc: 'Quantifies economic impact of grid disruption — regulatory penalties and productivity losses.',
      metrics: [
        { id: 'E1', name: 'BNetzA Penalties/User', intra: 0.55, global: 0.055, norm: 'B (P5/P95)', source: 'BNetzA / dena', desc: 'Per-user penalty costs from quality standard violations (ARegV)' },
        { id: 'E2', name: 'Productivity Loss Coefficient', intra: 0.45, global: 0.045, norm: 'C (bounded)', source: 'DESTATIS / DIW / Bundesbank', desc: 'Weighted avg VoLL by local economic structure (β coefficient — captures East/West differential)' }
      ]
    },
    {
      id: 'S', name: 'Saturation', weight: 0.20, color: '#8e44ad',
      desc: 'Measures grid utilisation stress — generation/consumption imbalance, reverse power flow, and critical load classes.',
      metrics: [
        { id: 'S1', name: 'Landkreis KPI (Gen/Consumption)', intra: 0.75, global: 0.150, norm: 'B* (breakpoints)', source: 'BNetzA + 4 TSOs', desc: 'Landkreis-level generation/consumption ratio with 5-tier breakpoints reflecting wind-rich-north / industrial-south imbalance' },
        { id: 'S2', name: 'Reverse Power Flow',              intra: 0.125, global: 0.025, norm: 'D (categorical)', source: '4 TSOs / DSO', desc: '{No RPF→0, >1%→0.5, >5%→1.0}', categorical: true },
        { id: 'S3', name: 'Criticality Class',                intra: 0.125, global: 0.025, norm: 'D (categorical)', source: 'BSI KRITIS', desc: '{Non-critical→0, Hospital/transport→0.5, Multiple critical→1.0}', categorical: true }
      ]
    },
    {
      id: 'T', name: 'Energy Transition', weight: 0.05, color: '#0e7490',
      desc: 'Captures energy-transition stress from distributed generation, output variability, and EV charging burden — Energiewende 60% (2024) → 80% target (2030).',
      isNew: true,
      metrics: [
        { id: 'T1', name: 'DER Stress Index', intra: 1.00, global: 0.050, norm: 'B (composite)', source: 'BNetzA Marktstammdaten + 4 TSOs + DESTATIS KFZ', desc: 'Composite: α_DER(0.50) × N(DER_ratio) + α_VAR(0.30) × N(variability) + α_EV(0.20) × N(EV_load)', isNew: true,
          submetrics: [
            { id: 'DER_ratio', name: 'DER Penetration Ratio', weight: 0.50, source: 'BNetzA MaStR + 4 TSOs', desc: 'DER capacity / peak load by Landkreis' },
            { id: 'DER_variability', name: 'DER Output Variability', weight: 0.30, source: 'ENTSO-E Transparency', desc: 'σ/μ of weekly DER output (coefficient of variation)' },
            { id: 'EV_load_ratio', name: 'EV Load Burden', weight: 0.20, source: 'DESTATIS KFZ + BNetzA', desc: 'EV count × 7.4kW / transformer capacity' }
          ]
        }
      ]
    }
  ];

  // ─── 7 Modifiers (Germany §54 — 5-tier R3 + R6c flood) ────
  const MODIFIERS = [
    {
      id: 'R2', name: 'Adaptive IRI + Climate Trajectory',
      range: 'Weight redistribution', type: 'Weight modifier',
      desc: 'Uses CMIP6 SSP2-4.5 projections to transform IRI_current → IRI_forward. When local hazard risk is low, weight shifts from IRI metrics (I1–I3) to structural metrics (I4, I6).',
      formula: 'IRI_forward(m,s) = IRI_current(m,s) × (1 + 0.15 × clip(Δ_climate, −0.50, +1.00))',
      sources: ['Copernicus CDS', 'DWD / BNetzA IRI'],
      isEnhanced: true
    },
    {
      id: 'R3', name: 'Consequence + Energy Poverty (5-tier — DE-unique)',
      range: '[1.02, 1.10]', type: 'Multiplicative (5-tier)',
      desc: 'Sigmoid function of population density, energy load, and socio-economic vulnerability. Germany §54 uses a UNIQUE 5-tier calibration (vs 4-tier AT/CH/LV/LT) to capture the post-reunification East/West socio-economic differential.',
      formula: 'C_mult ∈ {1.02, 1.04, 1.06, 1.08, 1.10}',
      sources: ['DESTATIS', 'DIW', 'BMF', 'BBSR', 'BBK', 'BfG'],
      isEnhanced: true,
      tiers: [
        { tier: '1.02 Capital-Intensive', lands: 'München + Hamburg + Frankfurt + Stuttgart (Top-4 cities)' },
        { tier: '1.04 Industrial', lands: 'Berlin + Köln + Düsseldorf + Bremen + Hannover' },
        { tier: '1.06 Commercial', lands: 'NRW remainder + Hessen + Baden-Württemberg' },
        { tier: '1.08 Light-Industrial', lands: 'Saarland + Rheinland-Pfalz + Niedersachsen' },
        { tier: '1.10 Light-Rural former-East', lands: 'Brandenburg + Mecklenburg-Vorpommern + Sachsen-Anhalt + Thüringen + Sachsen rural (Lausitz Just Transition Fund €40B+)' }
      ],
      enrichments: [
        { name: 'V_socio Fiscal Enrichment', effect: 'Up to +8% V_socio penalty', sources: 'BMF + BBSR + DIW' },
        { name: 'Demographic Shift Amplifier', effect: 'Up to +8% C_mult for population decline (former-East)', sources: 'DESTATIS Demographics' },
        { name: 'Elderly Vulnerability', effect: '×[1.0, 1.10] for high elderly %', sources: 'DESTATIS Demographics' },
        { name: 'Flood Zone Amplifier', effect: 'Up to +15% C_mult for flood zones', sources: 'BfG + LfU Bayern + BBK' }
      ]
    },
    {
      id: 'R4', name: 'Graph-Theoretic Network Criticality',
      range: '[0.80, 1.35]', type: 'Multiplicative',
      desc: 'Combines degree centrality, betweenness centrality, and topological bridge detection from OSM power graph. Built from ~6,500 substations and ~55,000 grid lines (largest fleet in OECD). Four HVDC corridors (SuedLink + SuedOstLink + A-Nord + Ultranet, 2028-2030) will significantly reshape this graph.',
      formula: 'F_topo = clip(base_factor(degree) × (1 + 0.10 × BC_percentile + 0.15 × is_bridge), 0.80, 1.35)',
      sources: ['OSM Overpass API', '4 TSO Netzentwicklungsplane'],
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
      range: '[1.00, 1.04]', type: 'Multiplicative',
      desc: 'BNetzA Monitoring CAIDI-based: rewards fast-restoring areas, penalises slow ones. Germany SAIDI ~11.7 min is EU-best of large economies.',
      formula: 'R6a_mult = sigmoid_bounded(CAIDI_local / CAIDI_med, 1.00, 1.04)',
      sources: ['BNetzA Monitoringbericht'],
      isNew: true
    },
    {
      id: 'R6b', name: 'Seismic (Rhine Graben)',
      range: 'α ∈ [0.02, 0.12]', type: 'Multiplicative',
      desc: 'Rhine Graben seismic exposure: Karlsruhe + Köln + Aachen + Mainz at 0.08g PGA on the 475-year hazard map (highest in DE); Bavarian Alps southern edge 0.06g; rest of DE essentially aseismic (0.02-0.04g).',
      formula: 'R6b_seis = clip(1.0 + α × (PGA_475yr / 0.10), 1.00, 1.12)',
      sources: ['BGR', 'EFEHR ESHM20'],
      isNew: true
    },
    {
      id: 'R6c', name: 'Flood (Rhine · Elbe · Danube · North Sea)',
      range: '[1.00, 1.20]', type: 'Multiplicative',
      desc: 'Largest flood exposure footprint in DACH. Rhine basin dominant (NRW + Hessen + RP — 2021 Ahr valley reference event: 134 deaths, €33B damages); Elbe (Sachsen + Sachsen-Anhalt + Niedersachsen); Danube (Bayern + BW); North Sea storm surge (Niedersachsen + Schleswig-Holstein).',
      formula: 'R6c_flood = clip(1.0 + 0.20 × flood_zone_pct + 0.15 × NorthSea_proximity, 1.00, 1.20)',
      sources: ['BfG', 'LfU Bayern', 'BBK', 'Landesumweltämter'],
      isNew: true
    },
    {
      id: 'R7', name: 'Digital Readiness (DE ceiling 1.06)',
      range: '[0.99, 1.06]', type: 'Multiplicative',
      desc: 'Landkreis-level continuous model based on DESI regional digital readiness scores (DE 0.61, rank ~10/27 EU), urban/rural adjustments, HV voltage class bonus, BSI KRITIS audit status, and per-substation noise. DE ceiling raised to 1.06 (vs 1.04 elsewhere in DACH) because of the 4-TSO + ~800-DSO attack surface — largest in OECD. NIS2 transposed Q4 2024 (late EU); BSI KRITIS since 2015.',
      formula: 'R7_cyber(s) = clip( DESI_base(region) + urban_adj(LK) + HV_bonus(voltage) + KRITIS_status + noise, 0.99, 1.06 )',
      sources: ['DESI / Eurostat', 'BSI KRITIS', 'JRC DSO Observatory'],
      isNew: true,
      enrichments: [
        { name: 'KRITIS Audit Status', effect: '−0.005 R7 for audited assets', sources: 'BSI KRITIS' },
        { name: 'TSO Control-Area Adjustment', effect: '4-TSO fragmentation premium', sources: '50Hertz / Amprion / TenneT TSO DE / TransnetBW' }
      ]
    }
  ];

  // ─── Data Layers (11 layers, 95 variables) ─────────────────
  const DATA_LAYERS = [
    { id: 'A',   name: 'SSI v4.0.2 Resilience',        vars: 20, status: 'LIVE',        sources: 'BNetzA · 4 TSOs · DESTATIS · DESTATIS KFZ · DWD' },
    { id: 'B.1', name: 'Grid Telemetry: Open',         vars: 3,  status: 'LIVE',        sources: 'Open-Meteo / ERA5 · DWD · BNetzA SMARD' },
    { id: 'B.2', name: 'Grid Telemetry: Proxy',        vars: 4,  status: 'LIVE',        sources: 'IEEE C57.91 · 4 TSO Netzentwicklungsplane · UBA · EN 50160' },
    { id: 'B.3', name: 'Grid Telemetry: Fuzzy/Markov', vars: 12, status: 'LIVE (MARKOV)', sources: 'IEEE/CIGRÉ standards · BNetzA · EEA' },
    { id: 'C',   name: 'Socio-Economic',               vars: 9,  status: 'LIVE',        sources: 'DESTATIS · DIW · Eurostat · DESI · BBSR' },
    { id: 'D',   name: 'Environmental Hazards',         vars: 7,  status: 'LIVE',        sources: 'EEA · BGR · BfG · LfU Bayern · ISO 9223 · Copernicus CDS' },
    { id: 'E',   name: 'German Open Data',              vars: 8,  status: 'LIVE',        sources: 'BMWK · BMU · BMF · BNetzA · DESTATIS · GovData.de' },
    { id: 'F',   name: 'Network Transitions',           vars: 12, status: 'LIVE (BAYESIAN)', sources: '~800 DSO histories OR IEEE/CIGRÉ + priors' },
    { id: 'G',   name: 'Modifier Inputs',               vars: 3,  status: 'LIVE',        sources: 'BNetzA Monitoring · OSM Power · JRC DSO · BSI KRITIS', isNew: true },
    { id: 'H',   name: 'Network & Topology',            vars: 7,  status: 'LIVE',        sources: '4 TSO Netzentwicklungsplane (incl. SuedLink/SuedOstLink/A-Nord/Ultranet) · BGR · OSM · BfG', isNew: true },
    { id: 'I',   name: 'Output Scores',                 vars: 7,  status: 'LIVE',        sources: 'Fleet Markov Chain · IEEE/CIGRÉ analysis', isNew: true }
  ];

  // ─── Processing Pipeline ──────────────────────────────────
  const PIPELINE = [
    { step: 1, name: 'Ingest',     desc: '95 variables from 35 verified data sources', icon: '①' },
    { step: 2, name: 'Normalise',  desc: 'Methods A–D: fleet percentile, bounded, categorical → [0,1]', icon: '②' },
    { step: 3, name: 'Weight',     desc: '6-level hierarchy: component × intra-metric weights', icon: '③' },
    { step: 4, name: 'Compose',    desc: 'R_base = Σ wᵢ·Cᵢ (6 components, 20 metrics)', icon: '④' },
    { step: 5, name: 'Modify',     desc: 'R2 adaptive + R3 5-tier consequence × R4 topology × R6a restoration × R6b Rhine Graben seismic × R6c flood × R7 digital (ceiling 1.06)', icon: '⑤' },
    { step: 6, name: 'Monte Carlo', desc: '10,000 iterations with 20×20 Gaussian copula (largest OECD fleet)', icon: '⑥' },
    { step: 7, name: 'Classify',   desc: '4 bands (Low/Medium/High/Critical) + confidence tiers + alerts', icon: '⑦' }
  ];

  // ─── Normalisation Methods ────────────────────────────────
  const NORM_METHODS = [
    { id: 'A', name: 'Fleet Percentile (robust)',    formula: 'N(x) = soft_clip((x − P₅) / (P₉₅ − P₅))', applies: 'C1, C2' },
    { id: 'B', name: 'Fleet Percentile (standard)',  formula: 'N(x) = soft_clip((x − P₅) / (P₉₅ − P₅))', applies: 'C4, V, I4↓, I6↓, E1, S1, T1 sub-metrics, I5, I7–I9' },
    { id: 'C', name: 'Bounded Rescaling',            formula: 'N(x) = (x − x_min) / (x_max − x_min)', applies: 'I1–I3 [0, 0.30], C3 [0%, 100%], E2 [1.50, 1.85]' },
    { id: 'D', name: 'Categorical Mapping',           formula: 'S2: {No RPF→0, >1%→0.5, >5%→1.0}', applies: 'S2, S3' }
  ];

  // ─── Classification Bands ─────────────────────────────────
  const CLASSIFICATION = [
    { name: 'Low',      range: '0.00 – 0.25', meaning: 'Good resilience — stable grid, low exposure',   expected: '~35–45%', color: '#5d8563' },
    { name: 'Medium',   range: '0.25 – 0.50', meaning: 'Moderate — some vulnerabilities, monitor',      expected: '~30–40%', color: '#b8863a' },
    { name: 'High',     range: '0.50 – 0.75', meaning: 'Elevated risk — investment priority area',      expected: '~10–20%', color: '#aa4234' },
    { name: 'Critical', range: '0.75 – 1.00', meaning: 'Severe vulnerability — urgent intervention',    expected: '~3–8%',   color: '#941914' }
  ];

  // ─── Master Equation ─────────────────────────────────────
  const MASTER_EQUATION = {
    formula: 'R_final = soft_clip_upper(R_base × F_topo × C_mult × R6a_mult × R6b_seis × R6c_flood × Cyber_factor)',
    R_base: 'R_base = 0.30·C + 0.10·V + 0.25·I + 0.10·E + 0.20·S + 0.05·T',
    modifiers: {
      F_topo: 'graph_criticality(degree, BC, bridge) [R4]',
      C_mult: 'consequence_5tier(pop, load, V_socio) [R3 — DE-unique 5-tier]',
      R6a_mult: 'restoration_speed_sigmoid(CAIDI_local) [R6a]',
      R6b_seis: 'rhine_graben_seismic(PGA_475yr) [R6b]',
      R6c_flood: 'flood_basin(rhine, elbe, danube, north_sea) [R6c]',
      Cyber_factor: 'DESI_cyber(region, LK, voltage, KRITIS) [R7 — ceiling 1.06]'
    },
    soft_clip: 'if R_raw ≤ 1.00 → R_raw; if R_raw > 1.00 → 1.00 − 1/(1 + e^(20×(R_raw − 1.05)))'
  };

  // ─── Validation Framework ─────────────────────────────────
  const VALIDATION_CHECKS = [
    { check: 'North-South wind/load gradient',    criterion: 'Northern Länder (SH/NI) have higher T1 stress; southern Länder (BY/BW) have higher I7 load stress', status: 'verified' },
    { check: 'East/West differential (5-tier R3)',criterion: 'Former-East Länder cluster in R3 1.10 tier; Top-4 cities cluster in R3 1.02 tier', status: 'verified' },
    { check: 'IRI-climate coherence',             criterion: 'I1 peaks Bavarian Alps · I3 peaks Berlin + Brandenburg + Hamburg', status: 'verified' },
    { check: 'Saturation-RPF coherence',          criterion: 'S1 > breakpoint ↔ S2 > 5% agreement > 90%', status: 'verified' },
    { check: 'Ratio test',                        criterion: 'R(worst) / R(best) ≥ 5×', status: 'verified' },
    { check: 'Monotonicity',                     criterion: 'Each metric worsening → R increases', status: 'verified' },
    { check: 'CI width quality signal',           criterion: 'Regional-only subs have wider CI', status: 'verified' },
    { check: 'T1-DER coherence',                 criterion: 'T1 peaks in SH+NI wind belt and BY solar belt Landkreise', status: 'verified' },
    { check: 'R6 speed coherence',               criterion: 'R6a < 1.01 for urban München/Berlin, R6a > 1.02 for rural former-East Landkreise', status: 'verified' },
    { check: 'Energy poverty gradient',          criterion: 'V_socio correlates with former-East deprivation + Saarland transition', status: 'verified' },
    { check: 'R4 bridge identification',         criterion: 'is_bridge=1 subs concentrate on existing 380 kV N-S backbone (pre-HVDC)', status: 'verified' },
    { check: 'Climate trajectory direction',      criterion: 'I3 trajectory > 1.0 in East, I1 stable in Alpine south', status: 'verified' },
    { check: 'Weight sum invariant',              criterion: 'Σ w_component = 1.000 exactly', status: 'verified' },
    { check: 'R6b Rhine Graben spike',           criterion: 'Karlsruhe + Köln + Aachen + Mainz substations have R6b > 1.06', status: 'verified' },
    { check: 'R6c flood coverage',                criterion: 'Rhine + Elbe + Danube + North Sea zone substations have R6c > 1.05', status: 'verified' },
    { check: 'Markov risk coherence',            criterion: 'markov_risk_score positively correlates with asset age and outage rates', status: 'verified' },
    { check: 'C5 marine corrosion (DACH-unique)', criterion: 'North Sea coast (Friesland + Borkum + Wilhelmshaven) substations have corrosion class C5', status: 'verified' },
    { check: 'TSO control-area attribution',     criterion: 'Each substation has a tso field matching the Land mapping (50Hertz/Amprion/TenneT TSO DE/TransnetBW)', status: 'verified' }
  ];

  // ─── Changelog v3.4 → v4.0.2 ───────────────────────────────
  const CHANGELOG = [
    { id: 'F1', section: '§2, §4', change: 'New T component — Energy Transition Exposure (T1) — Energiewende focus', type: 'new' },
    { id: 'F2', section: '§5',     change: 'New R6a — Restoration Speed Modifier (BNetzA Monitoring CAIDI)', type: 'new' },
    { id: 'F3', section: '§5',     change: 'R3 enhanced — 5-tier calibration (East/West differential — DE-unique in DACH)', type: 'enhanced' },
    { id: 'F4', section: '§5',     change: 'R4 enhanced — Graph-theoretic betweenness + bridge detection (~55,000 lines)', type: 'enhanced' },
    { id: 'F5', section: '§5',     change: 'R2 enhanced — Climate Trajectory (CMIP6 SSP2-4.5)', type: 'enhanced' },
    { id: 'F6', section: '§5',     change: 'R7 Digital Readiness — ceiling 1.06 (4-TSO + 800-DSO attack surface)', type: 'enhanced' },
    { id: 'F7', section: '§5',     change: 'R6c Flood — DACH-largest exposure footprint (Rhine/Elbe/Danube/North Sea)', type: 'new' },
    { id: 'L1', section: '§2, §8', change: 'New I5, I7–I9 metrics — thermal, load, corrosion (incl. DACH-unique C5), hydrogeo', type: 'new' },
    { id: 'L2', section: '§6',     change: 'E2 Innovation Enrichment — DIW + Bundesbank regional accounts', type: 'enhanced' },
    { id: 'L3', section: '§5',     change: 'V_socio Fiscal Enrichment — BMF + BBSR + DIW East/West differential', type: 'enhanced' },
    { id: 'L4', section: '§5',     change: 'R3 Demographic Shift Amplifier — DESTATIS net migration (former-East decline)', type: 'enhanced' },
    { id: 'L5', section: '§8, §12', change: '95/95 variables operational (100%). 35 data sources total.', type: 'data' },
    { id: 'G1', section: '§12',    change: 'BNetzA Marktstammdaten (MaStR) — bulk Landkreis-level DER registry', type: 'data' },
    { id: 'G2', section: '§12',    change: 'BGR upgraded to seismic registry (Rhine Graben PGA 475-yr)', type: 'data' },
    { id: 'G3', section: '§12',    change: 'OSM upgraded to Overpass API — ~6,500 real substations (post-§38+§52)', type: 'data' },
    { id: 'G4', section: '§5',     change: 'R6b Rhine Graben Seismic modifier — Karlsruhe/Köln/Aachen/Mainz hotspot', type: 'new' },
    { id: 'G5', section: '§12',    change: 'Network & Topology layer (H): 7 variables — 4 TSO Netzentwicklungsplane + HVDC corridors', type: 'new' },
    { id: 'G6', section: '§12',    change: 'Output Scores layer (I): 7 variables — risk_score, ETTC, stationary probs', type: 'new' }
  ];

  // ─── Frequency Distribution ───────────────────────────────
  const FREQ_DISTRIBUTION = {
    Hourly: { count: 1, sources: ['ENTSO-E Transparency'] },
    Daily:  { count: 1, sources: ['DWD'] },
    Weekly: { count: 1, sources: ['OSM Overpass'] },
    Monthly: { count: 0, sources: [] },
    Quarterly: { count: 2, sources: ['DESTATIS KFZ', 'BMUV'] },
    Annual: { count: 22, sources: ['BNetzA', '50Hertz', 'Amprion', 'TenneT TSO DE', 'TransnetBW', 'DESTATIS', 'DIW', 'BBSR', 'BMWK', 'BMU', 'BMF', 'BSI', 'Bundesbank', 'dena', 'UBA', 'EEA', 'Eurostat', 'DESI', 'BfG', 'LfU Bayern', 'JRC', 'BNetzA Monitoring'] },
    Static: { count: 6, sources: ['IEEE/IEC/CIGRÉ', 'Copernicus CMIP6', 'BGR', 'ISO 9223', 'AGS', 'BBK'] },
    Derived: { count: 1, sources: ['ISO 9223 corrosion (from EEA+UBA+DWD)'] },
    Continuous: { count: 1, sources: ['BBK Civil Protection'] }
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
      modifiers: 7,  // DE has 7 incl. R6c flood
      sources: 35,
      substations: 6500,   // ~6,500 target (range 5,000-8,000)
      powerLines: 55000,
      mcIterations: 10000,
      landkreise: 401,
      gemeinden: 11054,
      regions: 16,
      tsos: 4,
      dsos: 800,
      population_M: 84.5,
      gdp_per_capita_USD: 56200
    }
  };
})();

// ─────────────────────────────────────────────────────────────────────
// KB §45.6 — dual-global alias (back-compat for deploy gate + loaders)
// The IIFE above assigns window.SSIMetadata as the canonical form.
// Deploy gate at §45.6 requires BOTH globals exist + the reverse alias
// for cross-country grep consistency with LV/LT/EE/CZ/LU/BE/NL/AT/CH.
// ─────────────────────────────────────────────────────────────────────
window.SSI_METADATA = window.SSIMetadata;
window.SSIMetadata = window.SSI_METADATA;
