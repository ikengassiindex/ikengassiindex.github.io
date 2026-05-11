/* ═══════════════════════════════════════════════════════════
   SSI v4.0.2 — Metadata Registry (Luxembourg)
   95 variables · 22 sources · 20 metrics · 6 components · 7 modifiers
   Pattern C (Wave 6c canonical form per KB §3) — NO double-assignment IIFE
   ═══════════════════════════════════════════════════════════ */

// Pattern C: declare window.SSI_METADATA directly with uppercase keys.
window.SSI_METADATA = {

  // ─── Country identity ─────────────────────────────────────
  COUNTRY: {
    iso2: 'LU', iso3: 'LUX', folder: 'luxembourg',
    name_en: 'Luxembourg', name_local: 'Lëtzebuerg', flag: '🇱🇺',
    currency: 'EUR', currency_symbol: '€', currency_position: 'before',
    tso: 'Creos Luxembourg S.A. (combined TSO+DSO)',
    regulator: 'ILR — Institut Luxembourgeois de Régulation',
    market_operator: 'EPEX SPOT (DE-LU joint bidding zone since 2018)',
    ministry: 'Ministère de l\'Énergie et de l\'Aménagement du territoire',
    synchronous_area: 'ENTSO-E Continental Europe (10Y1001A1001A82H DE-LU zone)',
    bbox: { lon_min: 5.7340, lon_max: 6.5285, lat_min: 49.4480, lat_max: 50.1843 },
    admin_levels: {
      L1: { label_en: 'Cantons',  label_local: 'Kantonen', count: 12 },
      L2: { label_en: 'Communes', label_local: 'Gemengen', count: 102 }
    }
  },

  // ─── 22 verified data sources (LU registry — single-op country) ────
  DATA_SOURCES: [
    { id: 'CREOS',   name: 'Creos Luxembourg Annual Activity Report',  url: 'creos-net.lu',                  freq: 'Annual',         res: 'National',      vars: 8, category: 'Grid',          feeds: 'C1 D1L, C2 N1L, E1 peak load, E2 growth, E3 DER ratio, T1 RES share (combined TSO+DSO single op)' },
    { id: 'ILR',     name: 'ILR Quality of Supply Reports',             url: 'web.ilr.lu',                    freq: 'Annual',         res: 'National',      vars: 5, category: 'Grid',          feeds: 'C3 MV excess, C4 SAIDI (15.5 min unplanned · 24.7 min total), N1L 0.85, F2 CAIDI 29.1 min' },
    { id: 'EPEX',    name: 'EPEX SPOT — DE-LU Bidding Zone',            url: 'epexspot.com',                  freq: 'Hourly',         res: 'Zone',          vars: 3, category: 'Market',        feeds: 'Day-ahead clearing 78.4 €/MWh avg 2024; 312 negative-price hours (DE-LU shared)' },
    { id: 'ENTSOE',  name: 'ENTSO-E Transparency Platform',             url: 'transparency.entsoe.eu',        freq: 'Hourly',         res: 'Bidding zone',  vars: 4, category: 'Transition',    feeds: 'Generation mix (89.8% imports — net importer), DER variability, xborder DE-FR-BE-NL', registration: true },
    { id: 'STATEC',  name: 'STATEC — Institut national de la statistique', url: 'statistiques.public.lu',     freq: 'Annual',         res: 'Canton',        vars: 8, category: 'Socio-Econ',    feeds: 'P1 pop_density per canton, EP_rate (~6.2% national), elderly_pct, net_migration_pct' },
    { id: 'BCL',     name: 'Banque centrale du Luxembourg ARAD',        url: 'bcl.lu',                        freq: 'Quarterly',      res: 'Canton',        vars: 2, category: 'Economic',      feeds: 'R3 macro: GDP/capita (national €128k EU #1; Luxembourg €185k → Wiltz €75k)' },
    { id: 'ECGS',    name: 'ECGS Walferdange — European Center for Geodynamics & Seismology', url: 'ecgs.lu', freq: 'Static',         res: '~5 km',         vars: 2, category: 'Hazard',        feeds: 'R6b PGA 475-yr (≤0.04 g — Ardennes-Eifel stable basement)' },
    { id: 'METEO',   name: 'MeteoLux — Findel Station',                 url: 'meteolux.lu',                   freq: 'Hourly/Annual',  res: 'Canton (interp.)', vars: 5, category: 'Climate',     feeds: 'S2 T_amb (10.3 °C 1991-2020 norm), annual precip (820 mm), wind κ, flood Q100' },
    { id: 'CDS',     name: 'Copernicus CDS / ERA5 + CMIP6 SSP2-4.5',    url: 'cds.climate.copernicus.eu',     freq: 'Hourly/Static',  res: '0.25° (~25 km)',vars: 4, category: 'Climate',       feeds: 'R2 climate trajectory δI1/δI2/δI3 (2050 RCP4.5: ΔT +1.7 °C, Δprecip +2.5%, Δwind −0.8%)', registration: true },
    { id: 'OPM',     name: 'Open-Meteo Weather API',                    url: 'open-meteo.com',                freq: 'Hourly',         res: '~1 km',         vars: 1, category: 'Climate',       feeds: 'S2 T_amb live, heatwave duration (Findel + Diekirch)' },
    { id: 'OSM',     name: 'OpenStreetMap Power Infrastructure',         url: 'overpass-api.de',               freq: 'Continuous',     res: 'Node/edge',     vars: 4, category: 'Infrastructure',feeds: 'F1 degree, R4 BC, bridge — 91 substations + 628 lines + 676.9 km LIVE' },
    { id: 'EEA',     name: 'EEA Air Quality e-Reporting',               url: 'eea.europa.eu',                 freq: 'Annual',         res: '~1 km',         vars: 2, category: 'Environment',   feeds: 'P3 PM2.5/NO₂/AQI corrosion (LU mostly C2; Remich/Capellen C3 industrial outliers)' },
    { id: 'EUR',     name: 'Eurostat Energy Statistics',                url: 'ec.europa.eu/eurostat',         freq: 'Annual',         res: 'NUTS2',         vars: 3, category: 'Economic',      feeds: 'EP_rate (ilc_mdes01), nrg_pc_204 prices, validation cross-check vs STATEC' },
    { id: 'DESI',    name: 'DESI Digital Economy & Society Index',      url: 'digital-strategy.ec.europa.eu', freq: 'Annual',         res: 'EU Regional',   vars: 1, category: 'Socio-Econ',    feeds: 'R7 digital readiness (LU EU top-3 in connectivity)' },
    { id: 'LUX-EN',  name: 'Ministère de l\'Énergie — RES register',    url: 'guichet.public.lu',             freq: 'Quarterly',      res: 'National',      vars: 3, category: 'Transition',    feeds: 'EV uptake, heat pump density, PV register (LU PV ~250 MWp end 2024)' },
    { id: 'HAZARD',  name: 'Administration de la gestion de l\'eau — Flood maps', url: 'eau.gouvernement.lu', freq: 'Static',         res: '~250 m',        vars: 1, category: 'Hazard',        feeds: 'flood_zone_pct HQ100 (Remich 18.4%, Capellen 3.1% — Moselle/Sûre exposure)' },
    { id: 'CTL',     name: 'Cattenom NPP proximity decay (EDF)',         url: 'edf.fr',                        freq: 'Static',         res: 'Canton',        vars: 1, category: 'Hazard',        feeds: 'External NPP ~8 km from LU border — decay function for radiological context (informational)' },
    { id: 'IEEE-1',  name: 'IEEE C57.91 Thermal Model',                 url: 'standards.ieee.org',            freq: 'Static',         res: 'Asset-level',   vars: 1, category: 'Standards',     feeds: 'P2 transformer thermal degradation (Markov 5-state)' },
    { id: 'IEC-1',   name: 'IEC 60076 Power Transformers',              url: 'iec.ch',                        freq: 'Static',         res: 'Asset-level',   vars: 1, category: 'Standards',     feeds: 'Voltage regulation proxy' },
    { id: 'IEC-826', name: 'IEC 60826 Overhead Line Loading',           url: 'iec.ch',                        freq: 'Static',         res: 'Zone',          vars: 1, category: 'Standards',     feeds: 'Ice load class (LU zones 1-2 — low ice exposure)' },
    { id: 'ISO-9223',name: 'ISO 9223 Atmospheric Corrosion',            url: '(derived from EEA + MeteoLux)', freq: 'Derived',        res: 'Canton',        vars: 1, category: 'Standards',     feeds: 'P3 corrosion class — LU C2 typical, C3 industrial south' },
    { id: 'EEPR',    name: 'European Energy Poverty Observatory',       url: 'energypoverty.eu',              freq: 'Annual',         res: 'NUTS2',         vars: 1, category: 'Socio-Econ',    feeds: 'F3 cross-check EP_rate, regional energy affordability' }
  ],

  // ─── 6 Components (matches Wave B scoring engine: C/E/F/P/S/T) ──────
  COMPONENTS: [
    { id: 'C', name: 'Continuity',     weight: 0.30, color: '#941914',
      desc: 'Reliability and outage exposure — how often and how long power is interrupted.',
      metrics: [
        { id: 'C1', name: 'Long interruption duration (D1L)', intra: 0.40, global: 0.120, norm: 'A', source: 'Creos LU + ILR', desc: 'Annual interruption duration per LV customer (min/yr) — LU ~15.5 min unplanned, 24.7 total.' },
        { id: 'C2', name: 'Interruption count (N1L)',         intra: 0.30, global: 0.090, norm: 'A', source: 'ILR',           desc: 'Interruptions per customer per year — LU ~0.85.' },
        { id: 'C3', name: 'MV users exceeding standard',      intra: 0.20, global: 0.060, norm: 'A', source: 'ILR',           desc: '% of MV customers exceeding ILR continuity threshold (~1.2%).' },
        { id: 'C4', name: 'SAIDI (national + DSO)',           intra: 0.10, global: 0.030, norm: 'A', source: 'ILR',           desc: 'System Average Interruption Duration. LU 24.7 min/yr — among EU-best (DE 12; FR 50; CZ 80).' }
      ]
    },
    { id: 'E', name: 'Energy demand',  weight: 0.18, color: '#b8863a',
      desc: 'Demand-side stress — peak load, growth, peak/avg ratio, DER absorption.',
      metrics: [
        { id: 'E1', name: 'Peak load',          intra: 0.30, global: 0.054, norm: 'B', source: 'Creos LU', desc: 'Highest hourly load. LU national peak ~1.15 GW (compact grid).' },
        { id: 'E2', name: 'Load growth (10y)',  intra: 0.25, global: 0.045, norm: 'B', source: 'Creos LU', desc: '10-year compound growth in peak load (~0.4%/yr — driven by data centres + EV adoption).' },
        { id: 'E3', name: 'DER capacity ratio', intra: 0.25, global: 0.045, norm: 'B', source: 'Creos LU + Ministère Énergie', desc: 'DER installed / total installed (LU ~5.4% domestic — net importer).' },
        { id: 'E4', name: 'Peak / average',     intra: 0.20, global: 0.036, norm: 'A', source: 'ENTSO-E',  desc: 'Peak-to-average load ratio (LU ~1.62 — heavy commuter/industrial duty cycle).' }
      ]
    },
    { id: 'F', name: 'Fragility',      weight: 0.16, color: '#5d8563',
      desc: 'Network and social fragility — graph topology and energy poverty exposure.',
      metrics: [
        { id: 'F1', name: 'Node degree median',      intra: 0.30, global: 0.048, norm: 'C', source: 'OSM',     desc: 'Median substation degree from OSM power graph (LU ~2.5 — compact meshed core).' },
        { id: 'F2', name: 'CAIDI',                   intra: 0.25, global: 0.040, norm: 'A', source: 'ILR',     desc: 'Customer Average Interruption Duration. LU ~29.1 min.' },
        { id: 'F3', name: 'Energy poverty rate',     intra: 0.25, global: 0.040, norm: 'A', source: 'STATEC EU-SILC + Eurostat', desc: 'EP_rate ~6.2% national; northern rural cantons (Clervaux, Wiltz) higher.' },
        { id: 'F4', name: 'Graph topology composite', intra: 0.20, global: 0.032, norm: 'C', source: 'OSM',    desc: 'F_topo from BC + bridge + degree (computed by R4).' }
      ]
    },
    { id: 'P', name: 'Physical',       weight: 0.14, color: '#7a4a4a',
      desc: 'Physical condition — population pressure, asset degradation, atmospheric corrosion.',
      metrics: [
        { id: 'P1', name: 'Population density',          intra: 0.40, global: 0.056, norm: 'B', source: 'STATEC Census 2024', desc: 'Pop/km² per canton (Luxembourg canton ~610 outlier; Vianden ~98 rural).' },
        { id: 'P2', name: 'Markov 5-state ETTC',         intra: 0.35, global: 0.049, norm: 'B', source: 'Engine — IEEE C57.91 + MeteoLux', desc: 'Expected Time To Critical (years). LU younger fleet (post-2000 rebuild) → ~12 yr.' },
        { id: 'P3', name: 'Corrosion class (ISO 9223)',  intra: 0.25, global: 0.035, norm: 'A', source: 'EEA AQ + MeteoLux → derived', desc: 'LU mostly C2; Remich/Capellen C3 (industrial south).' }
      ]
    },
    { id: 'S', name: 'Stress',         weight: 0.12, color: '#3a5f7e',
      desc: 'Operational and environmental stress — variability, temperature extremes, healthcare load.',
      metrics: [
        { id: 'S1', name: 'DER variability (σ)',      intra: 0.40, global: 0.048, norm: 'A', source: 'ENTSO-E hourly', desc: 'σ of normalized RES output, intra-day (LU rising as PV share grows).' },
        { id: 'S2', name: 'T_amb stress',              intra: 0.30, global: 0.036, norm: 'A', source: 'MeteoLux + Open-Meteo', desc: 'Annual mean ambient temperature stress (LU mild oceanic, 10.3 °C baseline).' },
        { id: 'S3', name: 'Healthcare criticality',    intra: 0.30, global: 0.036, norm: 'B', source: 'STATEC + Ministère Santé', desc: 'Hospital beds per 1k pop × critical-care fraction.' }
      ]
    },
    { id: 'T', name: 'Transition',     weight: 0.10, color: '#5b8a72',
      desc: 'Energy transition — RES share, decarbonisation pace.',
      metrics: [
        { id: 'T1', name: 'RES share',              intra: 1.00, global: 0.100, norm: 'B', source: 'Creos LU + Ministère Énergie', desc: 'RES generation / total generation (~6.3% — Solar 4.1% + Wind 2.2%; LU is heavy net importer).' }
      ]
    }
  ],

  // ─── 7 Modifiers (R2-R7 + R6b) ────────────────────────────
  MODIFIERS: [
    { id: 'R2',  name: 'Adaptive IRI (climate)',   range: '[0.95, 1.05]',          inputs: 'δI1, δI2, δI3 (Copernicus ERA5)',
      formula: 'R2 = 1 + λ · mean(δI1, δI2, δI3), λ=0.15',
      desc: 'Climate trajectory adjustment. 2050 RCP4.5 LU deltas: +1.7 °C / +2.5% precip / −0.8% wind.' },
    { id: 'R3',  name: 'Consequence multiplier',   range: '[0.85, 1.18]',          inputs: 'pop_density, peak_load, GDP/cap, V_socio, flood',
      formula: 'C_mult = soft_clip(1 + 0.20 × Σ β·N(...))',
      desc: 'Population × load × economic × social vulnerability + LU flood bonus (+0.15 × flood_pct).' },
    { id: 'R4',  name: 'Graph criticality',        range: '[0.80, 1.35]',          inputs: 'BC, bridge density, node degree (OSM)',
      formula: 'F_topo = base(deg) · (1 + γ_BC·BC + γ_br·bridge_density)',
      desc: 'OSM substation graph extraction LIVE — 91 nodes, 628 edges.' },
    { id: 'R5',  name: 'Asymmetric CI',            range: 'output (R_p10, R_p50, R_p90)', inputs: 'Monte Carlo 20k Gaussian copula',
      formula: 'CI = MC(R_base, σ_per_component, CORR_MATRIX, 20k)',
      desc: 'Wider lower tail — captures asymmetric downside risk.' },
    { id: 'R6',  name: 'Operating stress',          range: '[0.85, 1.20]',          inputs: 'T_amb extremes, corrosion, ice load, wind κ',
      formula: 'R6 = soft_clip(2 − (1 + 0.20 × stress_avg))',
      desc: 'LU mild oceanic climate → narrow R6 band; minor ice exposure in Ardennes uplands only.' },
    { id: 'R6b', name: 'Seismic (α)',               range: '≈1.00 in LU',           inputs: 'PGA 475-yr (ECGS Walferdange)',
      formula: 'R6b = 1 − α · clip(PGA / PGA_ref) · 0.20, α∈[0.05, 0.20]',
      desc: 'Luxembourg sits on Ardennes-Eifel stable basement (PGA ≤0.04 g). α band [0.05, 0.20] — narrower than CZ [0.10, 0.30], much narrower than Italy [0.40, 0.85].' },
    { id: 'R7',  name: 'Digital readiness',         range: '[0.98, 1.02]',          inputs: 'digital_readiness (STATEC + DESI)',
      formula: 'R7 = 1 + 0.04 × (digital_readiness − 0.5)',
      desc: 'LU is EU top-3 on DESI — slight positive bias.' }
  ],

  // ─── Normalisation methods (Italy Formula Construct §3) — array shape ───
  NORM_METHODS: [
    { id: 'A', name: 'Min-max + invert',
      formula: 'N(x) = 1 − (x − x_min) / (x_max − x_min)',
      applies: 'Lower-is-better metrics: C1 (D1L), C2 (N1L), C3 (MT excess), C4 (SAIDI), F2 (CAIDI), F3 (EP_rate), S1 (DER variability), S2 (T_amb), P3 (corrosion C-class)' },
    { id: 'B', name: 'Logistic on z-score',
      formula: 'N(x) = 1 / (1 + exp((x − μ) / σ))',
      applies: 'Continuous demand-side: E1 (peak load), E2 (load growth), E3 (DER ratio), P1 (pop density), P2 (ETTC), S3 (healthcare crit), T1 (RES share)' },
    { id: 'C', name: 'Rank percentile',
      formula: 'N(x) = rank(x) / N',
      applies: 'Graph metrics & ordinals: F1 (degree median), F4 (graph topology composite)' },
    { id: 'D', name: 'Categorical mapping (R6 / R6b inputs)',
      formula: 'N(C-class) ∈ {C1:0, C2:0.25, C3:0.5, C4:0.75, C5:1}',
      applies: 'ISO 9223 corrosion (P3), IEC 60826 ice load (R6), seismic α (R6b)' }
  ],

  // ─── Source frequency distribution (drives 'Data Refresh' panel) ───
  FREQ_DISTRIBUTION: {
    Hourly:     { count: 3,  sources: ['EPEX SPOT', 'ENTSO-E', 'Open-Meteo'] },
    Weekly:     { count: 1,  sources: ['OSM Overpass'] },
    Quarterly:  { count: 2,  sources: ['BCL ARAD', 'Ministère Énergie RES'] },
    Annual:     { count: 10, sources: ['ILR', 'Creos LU', 'STATEC Census', 'STATEC EU-SILC', 'EEA AQ', 'Eurostat', 'DESI', 'MeteoLux normals', 'European Energy Poverty Obs.', 'BCL annual'] },
    Static:     { count: 6,  sources: ['ECGS Walferdange', 'Copernicus ERA5/CMIP6', 'IEEE C57.91', 'IEC 60076', 'IEC 60826', 'ISO 9223'] }
  },

  // ─── Data layers (95 variables × 11 layers) — France-compatible shape ───
  DATA_LAYERS: [
    { id: 'A',   name: 'Resilience metrics',         vars: 17, status: 'LIVE',          sources: 'ILR · Creos LU · OSM',                                                count: 17 },
    { id: 'AT',  name: 'Energy transition',          vars: 1,  status: 'LIVE',          sources: 'Creos LU · Ministère Énergie · ENTSO-E',                              count: 1  },
    { id: 'B',   name: 'Degradation & physical',     vars: 6,  status: 'LIVE (MARKOV)', sources: 'IEEE C57.91 · IEC 60076 · IEC 60826 · MeteoLux',                       count: 6  },
    { id: 'C',   name: 'Hazard layer',               vars: 6,  status: 'LIVE',          sources: 'ECGS Walferdange · MeteoLux · Admin. gestion eau · Cattenom decay',    count: 6  },
    { id: 'D',   name: 'Topology',                   vars: 5,  status: 'LIVE',          sources: 'OpenStreetMap · Creos LU asset registry',                              count: 5  },
    { id: 'E',   name: 'Demand-side',                vars: 12, status: 'LIVE',          sources: 'STATEC · DESI · Ministère Énergie',                                    count: 12 },
    { id: 'F',   name: 'Economic & innovation',      vars: 11, status: 'LIVE',          sources: 'BCL · STATEC · Eurostat',                                              count: 11 },
    { id: 'G',   name: 'Climate trajectory (R2)',    vars: 5,  status: 'PARTIAL',       sources: 'Copernicus ERA5 · CMIP6 SSP2-4.5 (trajectories pending live pull)',    count: 5  },
    { id: 'H',   name: 'Social vulnerability',       vars: 4,  status: 'LIVE',          sources: 'STATEC · Eurostat ilc_mdes01 · European Energy Poverty Obs.',          count: 4  },
    { id: 'I',   name: 'Grid operations',            vars: 12, status: 'LIVE',          sources: 'Creos LU · ENTSO-E · ILR · OSM',                                       count: 12 },
    { id: 'J',   name: 'Derived/Modifier outputs',   vars: 16, status: 'LIVE',          sources: 'Engine derived (R2–R7, MC, Sobol, ESG payloads)',                      count: 16 }
  ],

  // ─── Pipeline (Stage 1-7 of Best Practice Guide §V) ─────────────────
  PIPELINE: [
    { stage: 1, name: 'Data Ingestion (Digital Twin Repo)',  status: 'LIVE',        detail: 'digital-twin-lu — 10 source modules (no d02b: Creos LU is single TSO+DSO). d01_creos_lu, d02_ilr, d02c_market, d02d_entsoe, d03_hazard, d04_statec, d04b_bcl, d05_osm, d06_meteolux, d07_copernicus. d05_osm LIVE Overpass (91 substations).' },
    { stage: 2, name: 'Scoring Engine',                       status: 'LIVE',        detail: 'scoring-lu — 12 cantons × 95 variables → 6 components → R_base → R2..R7 → R_final + Markov ETTC + 20k MC + Sobol. ssi-data.json emitted: 91 substations, 12 cantons, 5/5 ESG fields.' },
    { stage: 3, name: 'Dashboard Setup',                      status: 'IN-PROGRESS', detail: 'luxembourg/ folder — 8 HTML pages + Pattern C ssi-metadata.js + grid-geo.json (91 subs, 628 lines).' },
    { stage: 4, name: 'Intelligence Integration',             status: 'PENDING',     detail: 'edition-config.json + intelligence-loader injection (post LU-Live).' },
    { stage: 5, name: 'Automation Pipeline',                  status: 'PENDING',     detail: 'FIRST_REFRESH = 2026-07.' },
    { stage: 6, name: 'Landing Page',                         status: 'PENDING',     detail: 'Map class flip oecd → active; OECD count update (24 → 25 after LU live).' },
    { stage: 7, name: 'Full Verification (25-Point Audit)',   status: 'PENDING',     detail: 'KB §17 — smoke test, console errors, OG/A11y, calibration.' }
  ],

  // ─── Master equation ─────────────────────────────────────
  MASTER_EQUATION: {
    R_base:  'R_base = soft_clip(Σ w_c · component_c)',
    R_final: 'R_final = R_base · R2 · R3 · R4 · R6 · R6b · R7',
    asym_CI: 'CI = monte_carlo(R_base, σ_c, CORR_MATRIX, 20k draws)',
    ETTC:    'P2 = Markov_5state(asset_age, stress_mult)'
  },

  // ─── Classification bands ────────────────────────────────
  CLASSIFICATION: {
    Critical:  { range: '[0.00, 0.50]', color: '#941914', desc: 'Severe resilience deficit; immediate intervention warranted.' },
    High:      { range: '[0.50, 0.65]', color: '#b8863a', desc: 'Material risk; targeted hardening needed.' },
    Moderate:  { range: '[0.65, 0.80]', color: '#5d8563', desc: 'Average resilience; monitor.' },
    Resilient: { range: '[0.80, 1.00]', color: '#2f6d3a', desc: 'Strong resilience; share best practice.' }
  },

  // ─── R3 economic tier thresholds (LU-calibrated, KB §13) ─────────────
  R3_TIERS: {
    'Capital-Intensive': { ge: 1.110, examples: 'Luxembourg, Esch-sur-Alzette, Capellen (financial + industrial south)' },
    'Industrial':        { ge: 1.075, examples: 'Mersch, Diekirch, Grevenmacher, Remich' },
    'Commercial':        { ge: 1.020, examples: 'Echternach, Redange' },
    'Light/Rural':       { ge: 0.000, examples: 'Wiltz, Clervaux, Vianden (Ardennes north)' }
  },

  // ─── Validation framework (KB §17 25-point audit) — array shape ───
  VALIDATION_CHECKS: [
    { check: 'Urban–rural convergence gap',     criterion: 'Luxembourg canton systematically lower-risk than rural Clervaux/Wiltz/Vianden', status: 'verified' },
    { check: 'IRI–climate coherence',            criterion: 'I3 peaks in Moselle/Sûre flood basins (Remich, Capellen); I1 mild oceanic',     status: 'expected' },
    { check: 'Single-op continuity coherence',   criterion: 'Creos LU national SAIDI 24.7 min broadcast to all cantons (no inter-DSO variance)', status: 'verified' },
    { check: 'Ratio test',                        criterion: 'R(Clervaux) / R(Luxembourg) ≥ 1.8× (compact-country narrower spread)',           status: 'verified' },
    { check: 'Monotonicity',                      criterion: 'Each metric worsening → R increases',                                           status: 'verified' },
    { check: 'CI width quality signal',           criterion: 'Cantons with sparse OSM coverage have wider CI (Vianden, Redange)',             status: 'verified' },
    { check: 'T1–DER coherence',                  criterion: 'T1 modest across all cantons (LU is net importer ~89.8%)',                     status: 'expected' },
    { check: 'R6 stress coherence',               criterion: 'R6 narrow band — LU mild oceanic climate, no severe T_amb gradient',           status: 'verified' },
    { check: 'R6b seismic coherence (LU-narrow)', criterion: 'PGA ≤ 0.04 g uniformly; R6b ≈ 1.00 across all cantons (Ardennes-Eifel stable)', status: 'verified', isNew: true },
    { check: 'Flood-zone coherence',              criterion: 'flood_zone_pct peaks Moselle valley (Remich 18.4%, Grevenmacher) + Sûre',      status: 'verified', isNew: true },
    { check: 'Markov ETTC coherence',             criterion: 'LU younger fleet → ~12 yr typical (vs CZ ~9 yr) — post-2000 Creos rebuild',    status: 'verified' },
    { check: 'Cross-border β coherence',          criterion: 'LU as net importer: ENTSO-E DE-LU shared zone flows reconcile (DE/FR/BE)',     status: 'expected' },
    { check: 'EP_rate coherence',                 criterion: 'EP_rate peaks in northern rural cantons (Clervaux, Wiltz)',                    status: 'verified' },
    { check: 'Healthcare crit coherence',         criterion: 'Luxembourg canton highest (CHL, Hôpitaux Robert Schuman); rural northern lowest', status: 'verified' },
    { check: 'GDP gradient coherence',            criterion: 'Luxembourg €185k > national €128k > Wiltz/Clervaux €75k per capita',           status: 'verified' },
    { check: 'OSM substation count plausibility', criterion: '91 OSM nodes vs Creos LU ~120 stations — gap acknowledged, traction/minor excluded', status: 'expected' },
    { check: 'Bbox gate',                         criterion: '0% substations outside [5.7340–6.5285, 49.4480–50.1843]',                      status: 'verified' },
    { check: 'ESG enrichment 5/5',                criterion: 'markov, seismic, transition, socio_economic, graph_topology populated',         status: 'verified' },
    { check: 'Currency consistency',              criterion: 'All monetary fields use €; prefix LU_OSM_ on every substation_id',             status: 'verified' },
    { check: 'Highest-risk sort explicit',        criterion: 'slice().sort(b.R−a.R).slice(0,8) per KB §27',                                   status: 'verified' },
    { check: 'R3 tier balance',                   criterion: '4 tiers balanced (3-3-3-2 cantons after recalibration to actual distribution)', status: 'verified' },
    { check: 'Sobol sensitivity',                 criterion: 'C component dominates variance (~47%); other components scale with weights',   status: 'verified' },
    { check: 'Smoke test 3/3',                    criterion: 'smoke-test.py --countries luxembourg returns 3/3 ✓ (Stage 7)',                  status: 'expected' },
    { check: 'OG/Twitter card injection',         criterion: 'scripts/add-og-tags.py --country luxembourg (Stage 7)',                        status: 'expected' },
    { check: 'A11y landmarks',                    criterion: 'role="main" + radar SVG aria-label (KB Wave 8b)',                              status: 'expected' }
  ],

  // ─── Changelog (Luxembourg onboarding deltas — Session 12) ──────────
  CHANGELOG: [
    { id: 'F1',  section: '§2, §4',  change: 'New T component — Energy Transition Exposure (T1)',                                          type: 'new' },
    { id: 'F2',  section: '§5',      change: 'New R6a — Restoration Speed Modifier (CAIDI-based)',                                          type: 'new' },
    { id: 'F3',  section: '§5',      change: 'R3 enhanced — Energy Poverty Vulnerability (V_socio = STATEC EU-SILC)',                      type: 'enhanced' },
    { id: 'F4',  section: '§5',      change: 'R4 enhanced — Graph-theoretic betweenness + bridge detection (NetworkX)',                     type: 'enhanced' },
    { id: 'F5',  section: '§5',      change: 'R2 enhanced — Climate Trajectory (CMIP6 SSP2-4.5) — pending live ERA5 file',                  type: 'enhanced' },
    { id: 'F6',  section: '§5',      change: 'R7 Digital Readiness — Canton-level DESI model',                                              type: 'enhanced' },
    { id: 'L1',  section: '§2, §8',  change: 'New I5, I7–I9 metrics — thermal, load, corrosion (ISO 9223), hydrogeo',                       type: 'new' },
    { id: 'L2',  section: '§6',      change: 'E2 Innovation Enrichment — high-tech employment + financial-centre density (BCL + STATEC)',   type: 'enhanced' },
    { id: 'LU1', section: 'Stage 1', change: 'Luxembourg onboarded — 10 source modules (no d02b: Creos LU single TSO+DSO), d05_osm LIVE (91 substations)', type: 'new', isP2: true },
    { id: 'LU2', section: 'Stage 1', change: 'LU regulatory stack mapped: Creos LU / ILR / STATEC / BCL / MeteoLux / ECGS Walferdange',     type: 'new', isP2: true },
    { id: 'LU3', section: 'Stage 2', change: 'Scoring engine: 12 cantons × 6 components → R_final + Markov ETTC + 20k MC + Sobol',          type: 'new', isP2: true },
    { id: 'LU4', section: 'Stage 3', change: 'Dashboard: 8 HTML pages + Pattern C ssi-metadata.js + 22-source registry',                    type: 'new', isP2: true },
    { id: 'LU5', section: 'Stage 4', change: 'R3 economic tier thresholds LU-calibrated [1.110 / 1.075 / 1.020] from actual distribution',  type: 'enhanced', isP2: true },
    { id: 'LU6', section: 'Stage 4', change: 'R6b seismic α band LU-narrow [0.05, 0.20] (Ardennes-Eifel basement, narrower than CZ)',       type: 'enhanced', isP2: true },
    { id: 'LU7', section: 'Stage 4', change: 'Cantons = L1 = L2 (12 cantons, no commune downscale — communes shown only for context)',      type: 'design', isP2: true },
    { id: 'LU8', section: 'Stage 4', change: 'Markov rates younger-fleet calibration (λ_12=0.035, λ_23=0.05, λ_34=0.08 vs CZ baseline)',    type: 'enhanced', isP2: true },
    { id: 'LU9', section: 'Stage 5', change: 'Automation pipeline scaffolded — FIRST_REFRESH=2026-07 — monthly + quarterly + annual workflows', type: 'new', isP2: true },
    { id: 'LU10',section: 'Stage 6', change: 'Landing-page Luxembourg map-active (oecd → active flip) + OECD count update',                  type: 'new', isP2: true },
    { id: 'D1',  section: 'Data',    change: '22-source LU registry verified (vs Italy 30, France 35, CZ 30) — all open-licensed',          type: 'data' },
    { id: 'D2',  section: 'Data',    change: 'OSM Overpass live extraction: 91 substations + 628 power lines + 676.9 km',                  type: 'data' }
  ],

  // ─── Quick stats (rendered on overview page) ─────────────────────────
  stats: {
    variables: 95,
    metrics: 20,
    components: 6,
    modifiers: 7,
    sources: 22,
    substations: 91,               // LIVE — d05_osm Overpass extraction (post-filter)
    substations_HV: 11,            // OSM voltage tag ≥110 kV (220 kV import corridors + Vianden switchyard)
    substations_MV: 15,            // OSM voltage tag 20-65 kV
    substations_distribution: 65,  // OSM nodes without voltage tag — distribution-tier
    powerlines_total_km: 676.9,    // LIVE OSM
    powerlines_HV_km: 198,         // OSM ≥110 kV (220 kV import corridors)
    powerlines_MV_km: 478,         // OSM 20-65 kV
    voltage_classes: '220 / 65 / 20 kV',
    mcIterations: 20000,
    cantons: 12,
    communes: 102,
    tso: 'Creos Luxembourg S.A.',
    dso_count: 1,                  // Single-op: Creos LU is combined TSO+DSO
    saidi_minutes_2024: 24.7,
    peak_load_mw: 1150,
    res_share_2024: 0.063,         // ~6.3% domestic generation share (solar+wind)
    imports_share_2024: 0.898,     // 89.8% imports — LU is heavy net importer
    geolocated_pct: 100,           // d05_osm LIVE — every substation has lat/lon
    // Comparator panel for SAIDI chart (CE-synchronous neighbours + benchmarks)
    saidi_peers: {
      Luxembourg: 24.7,
      Germany:    12,
      Netherlands:18.5,
      Belgium:    22,
      Austria:    35,
      France:     50,
      Czechia:    79.7
    }
  }
};

// Compatibility alias — older files reference window.SSIMetadata.
// Pattern C requires this AFTER the canonical assignment.
window.SSIMetadata = window.SSI_METADATA;
