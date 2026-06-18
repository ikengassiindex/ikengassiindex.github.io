/* ═══════════════════════════════════════════════════════════
   SSI v4.0.2 — Metadata Registry (Czechia)
   95 variables · 30 sources · 20 metrics · 6 components · 7 modifiers
   Pattern C (Wave 6c canonical form per KB §3) — NO double-assignment IIFE
   ═══════════════════════════════════════════════════════════ */

// Pattern C: declare window.SSI_METADATA directly with uppercase keys.
// The legacy IIFE pattern used in older country files silently overwrites
// the structured object on second load — see KB §3 / Wave 6c notes.
window.SSI_METADATA = {

  // ─── Country identity ─────────────────────────────────────
  COUNTRY: {
    iso2: 'CZ', iso3: 'CZE', folder: 'czechia',
    name_en: 'Czechia', name_cs: 'Česko', flag: '🇨🇿',
    currency: 'CZK', currency_symbol: 'Kč', currency_position: 'after',
    tso: 'ČEPS, a.s.',
    regulator: 'ERÚ — Energetický regulační úřad',
    market_operator: 'OTE, a.s.',
    ministry: 'MPO — Ministerstvo průmyslu a obchodu',
    synchronous_area: 'ENTSO-E Continental Europe',
    bbox: { lon_min: 12.09, lon_max: 18.86, lat_min: 48.55, lat_max: 51.06 },
    admin_levels: {
      L1: { label_en: 'Kraje',           label_cs: 'Kraje',                       count: 14  },
      L2: { label_en: 'ORP',             label_cs: 'Obce s rozšířenou působností', count: 206 }
    }
  },

  // ─── 30 verified data sources (Czech equivalents of Italy registry) ──
  DATA_SOURCES: [
    { id: 'CEPS',    name: 'ČEPS Open Data Portal',                  url: 'data.ceps.cz',                  freq: 'Hourly/Monthly', res: 'Zone (8)',      vars: 5, category: 'Grid',          feeds: 'T1 peak load, xborder DE/SK/AT/PL, frequency, 8 zones' },
    { id: 'ERU',     name: 'ERÚ Annual Operations Report',           url: 'eru.cz',                        freq: 'Annual',         res: 'DSO',           vars: 5, category: 'Grid',          feeds: 'C3 MV excess, C4 SAIDI, F2 CAIDI, R6 quality' },
    { id: 'CEZ-D',   name: 'ČEZ Distribuce annual report',           url: 'cezdistribuce.cz',              freq: 'Annual',         res: 'DSO area',      vars: 4, category: 'Grid',          feeds: 'C1 D1L, C2 N1L (~63% of CZ households)' },
    { id: 'EGD',     name: 'EG.D annual report',                     url: 'egd.cz',                        freq: 'Annual',         res: 'DSO area',      vars: 4, category: 'Grid',          feeds: 'C1, C2 (~28% of CZ households — Moravia)' },
    { id: 'PRE',     name: 'PREdistribuce annual report',            url: 'predistribuce.cz',              freq: 'Annual',         res: 'DSO area',      vars: 4, category: 'Grid',          feeds: 'C1, C2 (~9% — Praha urban underground)' },
    { id: 'OTE',     name: 'OTE Atlas of Power Plants',              url: 'ote-cr.cz',                     freq: 'Quarterly',      res: 'Municipality',  vars: 3, category: 'Transition',    feeds: 'T1 DER capacity registry — PV, wind, biogas, hydro' },
    { id: 'MPO',     name: 'MPO RES register',                       url: 'mpo.cz',                        freq: 'Annual',         res: 'National',      vars: 3, category: 'Transition',    feeds: 'EV uptake, heat pump density, energy efficiency' },
    { id: 'ENTSE',   name: 'ENTSO-E Transparency Platform',          url: 'transparency.entsoe.eu',        freq: 'Hourly',         res: 'Bidding zone',  vars: 3, category: 'Transition',    feeds: 'Generation by type (40% nuclear, 33% coal), DER variability', registration: true },
    { id: 'CSU',     name: 'ČSÚ — Český statistický úřad',           url: 'czso.cz',                       freq: 'Annual',         res: 'NUTS3/LAU',     vars: 8, category: 'Socio-Econ',    feeds: 'P1 pop_density, EP_rate, elderly, healthcare, P3 digital' },
    { id: 'CSU-RA',  name: 'ČSÚ Regional Accounts',                  url: 'czso.cz',                       freq: 'Annual',         res: 'NUTS2',         vars: 2, category: 'Economic',      feeds: 'GDP per capita per kraj (Praha 1.21M Kč; KVK 0.47M Kč)' },
    { id: 'CNB',     name: 'ČNB ARAD + InfoStat',                    url: 'cnb.cz/arad',                   freq: 'Quarterly',      res: 'NUTS2',         vars: 2, category: 'Economic',      feeds: 'R3 macro, regional income β decomposition' },
    { id: 'MFCR',    name: 'MF ČR Tax Statistics',                   url: 'mfcr.cz',                       freq: 'Annual',         res: 'Municipal',     vars: 1, category: 'Socio-Econ',    feeds: 'R3 fiscal capacity, income tax revenue per capita' },
    { id: 'CGS',     name: 'ČGS Geofond — Czech Geological Survey',  url: 'geology.cz',                    freq: 'Static',         res: '~5 km',         vars: 2, category: 'Hazard',        feeds: 'R6b PGA 475-yr (very low — Bohemian Massif). Replaces INGV.' },
    { id: 'CHMU',    name: 'ČHMÚ — Czech Hydrometeorological Inst.', url: 'chmi.cz',                       freq: 'Hourly/Annual',  res: 'Station',       vars: 5, category: 'Climate',       feeds: 'S2 T_amb, ice load, wind κ, flood Q100, AQI' },
    { id: 'CHMU-FL', name: 'ČHMÚ HPPS + VÚV TGM HEIS',               url: 'hpps.chmi.cz',                  freq: 'Continuous',     res: 'Watershed',     vars: 1, category: 'Hazard',        feeds: 'flood_zone_pct (R3 hazard) — DOMINANT CZ HAZARD (Elbe/Vltava/Morava)' },
    { id: 'EEA',     name: 'EEA Air Quality e-Reporting',            url: 'eea.europa.eu',                 freq: 'Annual',         res: '~1 km',         vars: 3, category: 'Environment',   feeds: 'P3 PM2.5/NO₂/AQI corrosion (CZ C2-C3 typical, Ostrava C4)' },
    { id: "CDS", name: "Copernicus CDS / ERA5-Land", url: "cds.climate.copernicus.eu", freq: "Annual", res: "0.1° (~11 km, ERA5-Land + daily-stats)", vars: 5, category: "Climate", feeds: "R2 Δ_climate (t_mean_c, heat_days, ice_days at 0.1° land grid)", registration: true },
    { id: 'OPM',     name: 'Open-Meteo Weather API',                 url: 'open-meteo.com',                freq: 'Hourly',         res: '~1 km',         vars: 1, category: 'Climate',       feeds: 'S2 T_amb, heatwave duration' },
    { id: 'OSM',     name: 'OSM Power Infrastructure',               url: 'overpass-api.de',               freq: 'Continuous',     res: 'Node/edge',     vars: 4, category: 'Infrastructure',feeds: 'F1 degree, R4 BC, bridge, line lengths (~6,200 km HV / ~110,000 km MV)' },
    { id: 'CENIA',   name: 'CENIA — Environmental Information',       url: 'cenia.cz',                      freq: 'Annual',         res: 'Kraj',          vars: 2, category: 'Environment',   feeds: 'Emissions, environmental quality. Replaces ISPRA.' },
    { id: 'EUR',     name: 'Eurostat Energy Statistics',             url: 'ec.europa.eu/eurostat',         freq: 'Annual',         res: 'NUTS2',         vars: 3, category: 'Economic',      feeds: 'EP_rate (ilc_mdes01), nrg_pc_204 prices, validation' },
    { id: 'DESI',    name: 'DESI Digital Economy Index',             url: 'digital-strategy.ec.europa.eu', freq: 'Annual',         res: 'EU Regional',   vars: 1, category: 'Socio-Econ',    feeds: 'R7 digital readiness modulation' },
    { id: 'CzInv',   name: 'CzechInvest + ARES',                     url: 'czechinvest.org',               freq: 'Quarterly',      res: 'Regional',      vars: 2, category: 'Socio-Econ',    feeds: 'Startup density, regional development gap. Replaces MIMIT/SVIMEZ.' },
    { id: 'MZCR',    name: 'MZ ČR Healthcare Registry',              url: 'mzcr.cz',                       freq: 'Annual',         res: 'Kraj',          vars: 1, category: 'Socio-Econ',    feeds: 'S3 healthcare criticality (hospital beds, critical care)' },
    { id: 'HZS',     name: 'GŘ HZS ČR Civil Protection',             url: 'hzscr.cz',                      freq: 'Continuous',     res: 'Municipal',     vars: 1, category: 'Hazard',        feeds: 'Critical infrastructure protection alerts. Replaces DPC.' },
    { id: 'NEN',     name: 'NEN + ÚOHS Procurement',                 url: 'nen.nipez.cz',                  freq: 'Monthly',        res: 'PA-level',      vars: 1, category: 'Economic',      feeds: 'PA energy procurement (low priority — Stage 2)' },
    { id: 'IEEE-1',  name: 'IEEE C57.91 Thermal Model',              url: 'standards.ieee.org',            freq: 'Static',         res: 'Asset-level',   vars: 1, category: 'Standards',     feeds: 'P2 transformer thermal degradation' },
    { id: 'IEC-1',   name: 'IEC 60076 Power Transformers',           url: 'iec.ch',                        freq: 'Static',         res: 'Asset-level',   vars: 1, category: 'Standards',     feeds: 'Voltage regulation proxy' },
    { id: 'IEC-826', name: 'IEC 60826 Overhead Line Loading',        url: 'iec.ch',                        freq: 'Static',         res: 'Zone',          vars: 1, category: 'Standards',     feeds: 'Ice load class (CZ Krkonoše/Beskydy zones 4-5)' },
    { id: 'ISO-9223',name: 'ISO 9223 Atmospheric Corrosion',         url: '(derived from EEA + ČHMÚ)',     freq: 'Derived',        res: 'Kraj',          vars: 1, category: 'Standards',     feeds: 'P3 corrosion class C1-C5' },
    { id: "GEM", name: "GEM Global Seismic Hazard Map 2023.1", url: "globalquakemodel.org", freq: "Static", res: "0.05° (~5.5 km, rock-site PGA 475-yr)", vars: 1, category: "Hazard", feeds: "R6a seismic PGA, substation-level overlay (CC BY-NC-SA 4.0)" },
    { id: "Eurostat-NUTS3", name: "Eurostat NUTS-3 Regional Statistics", url: "ec.europa.eu/eurostat", freq: "Annual", res: "NUTS-3 (province / NUTS-2 unemployment)", vars: 5, category: "Socio-Econ", feeds: "R2 GDP/cap, unemp, elderly%, ep_rate, migration (CC BY 4.0)" },
  ],

  // ─── 6 Components (matches Wave B scoring engine: C/E/F/P/S/T) ──────
  COMPONENTS: [
    { id: 'C', name: 'Continuity',     weight: 0.30, color: '#941914',
      desc: 'Reliability and outage exposure — how often and how long power is interrupted.',
      metrics: [
        { id: 'C1', name: 'Long interruption duration (D1L)', intra: 0.40, global: 0.120, norm: 'A', source: 'ČEZ-Dist + EG.D + PRE', desc: 'Annual interruption duration per LV customer (min/yr).' },
        { id: 'C2', name: 'Interruption count (N1L)',         intra: 0.30, global: 0.090, norm: 'A', source: 'ČEZ-Dist + EG.D + PRE', desc: 'Number of interruptions per customer per year.' },
        { id: 'C3', name: 'MV users exceeding standard',      intra: 0.20, global: 0.060, norm: 'A', source: 'ERÚ',                  desc: '% of MV customers exceeding ERÚ continuity threshold.' },
        { id: 'C4', name: 'SAIDI (national + DSO)',           intra: 0.10, global: 0.030, norm: 'A', source: 'ERÚ',                  desc: 'System Average Interruption Duration. CZ ~75-80 min/yr.' }
      ]
    },
    { id: 'E', name: 'Energy demand',  weight: 0.18, color: '#b8863a',
      desc: 'Demand-side stress — peak load, growth, peak/avg ratio, DER absorption.',
      metrics: [
        { id: 'E1', name: 'Peak load',          intra: 0.30, global: 0.054, norm: 'B', source: 'ČEPS', desc: 'Highest hourly load (MW). National peak ~11.4 GW.' },
        { id: 'E2', name: 'Load growth (10y)',  intra: 0.25, global: 0.045, norm: 'B', source: 'ČEPS', desc: '10-year compound growth in peak load (CZ ~0.4%/yr).' },
        { id: 'E3', name: 'DER capacity ratio', intra: 0.25, global: 0.045, norm: 'B', source: 'OTE + MPO', desc: 'DER installed / total installed (CZ ~20%).' },
        { id: 'E4', name: 'Peak / average',     intra: 0.20, global: 0.036, norm: 'A', source: 'ENTSO-E', desc: 'Peak-to-average load ratio (CZ ~1.55).' }
      ]
    },
    { id: 'F', name: 'Fragility',      weight: 0.16, color: '#5d8563',
      desc: 'Network and social fragility — graph topology and energy poverty exposure.',
      metrics: [
        { id: 'F1', name: 'Node degree median',      intra: 0.30, global: 0.048, norm: 'C', source: 'OSM',     desc: 'Median substation degree from OSM power graph.' },
        { id: 'F2', name: 'CAIDI',                   intra: 0.25, global: 0.040, norm: 'A', source: 'ERÚ',     desc: 'Customer Average Interruption Duration (= SAIDI/SAIFI).' },
        { id: 'F3', name: 'Energy poverty rate',     intra: 0.25, global: 0.040, norm: 'A', source: 'ČSÚ EU-SILC + Eurostat', desc: 'EP_rate (Eurostat ilc_mdes01). CZ national ~7.8%; ULK 13%, MSK 11.5%.' },
        { id: 'F4', name: 'Graph topology composite', intra: 0.20, global: 0.032, norm: 'C', source: 'OSM',     desc: 'F_topo from BC + bridge + degree (computed by R4).' }
      ]
    },
    { id: 'P', name: 'Physical',       weight: 0.14, color: '#7a4a4a',
      desc: 'Physical condition — population pressure, asset degradation, atmospheric corrosion.',
      metrics: [
        { id: 'P1', name: 'Population density',          intra: 0.40, global: 0.056, norm: 'B', source: 'ČSÚ Census 2021', desc: 'Population per km² per kraj (Praha extreme outlier 2,698; VYS rural 75).' },
        { id: 'P2', name: 'Markov 5-state ETTC',         intra: 0.35, global: 0.049, norm: 'B', source: 'Engine — IEEE C57.91 + ČHMÚ', desc: 'Expected Time To Critical (years).' },
        { id: 'P3', name: 'Corrosion class (ISO 9223)',  intra: 0.25, global: 0.035, norm: 'A', source: 'EEA AQ + ČHMÚ → derived', desc: 'CZ typical C2-C3; Ostrava C4 (industrial).' }
      ]
    },
    { id: 'S', name: 'Stress',         weight: 0.12, color: '#3a5f7e',
      desc: 'Operational and environmental stress — variability, temperature extremes, healthcare load.',
      metrics: [
        { id: 'S1', name: 'DER variability (σ)',      intra: 0.40, global: 0.048, norm: 'A', source: 'ENTSO-E hourly', desc: 'σ of normalized RES output, intra-day.' },
        { id: 'S2', name: 'T_amb stress',              intra: 0.30, global: 0.036, norm: 'A', source: 'ČHMÚ + Open-Meteo', desc: 'Annual mean ambient temperature stress (heatwave risk).' },
        { id: 'S3', name: 'Healthcare criticality',    intra: 0.30, global: 0.036, norm: 'B', source: 'ČSÚ + MZ ČR', desc: 'Hospital beds per 1k pop × critical-care fraction.' }
      ]
    },
    { id: 'T', name: 'Transition',     weight: 0.10, color: '#5b8a72',
      desc: 'Energy transition — RES share, decarbonisation pace.',
      metrics: [
        { id: 'T1', name: 'RES share',              intra: 1.00, global: 0.100, norm: 'B', source: 'OTE + MPO', desc: 'RES installed / total installed (national ~20%, generation share ~17%).' }
      ]
    }
  ],

  // ─── 7 Modifiers (R2-R7 + R6b) ────────────────────────────
  MODIFIERS: [
    { id: 'R2',  name: 'Adaptive IRI (climate)',   range: '[0.95, 1.05]',          inputs: 'δI1, δI2, δI3 (Copernicus ERA5)',
      formula: 'R2 = 1 + λ · mean(δI1, δI2, δI3), λ=0.15',
      desc: 'Climate trajectory adjustment. Inactive without ERA5 file.' },
    { id: 'R3',  name: 'Consequence multiplier',   range: '[0.85, 1.18]',          inputs: 'pop_density, peak_load, GDP/cap, V_socio, flood',
      formula: 'C_mult = soft_clip(1 + 0.20 × Σ β·N(...))',
      desc: 'Population × load × economic × social vulnerability + CZ flood bonus (+0.15 × flood_pct).' },
    { id: 'R4',  name: 'Graph criticality',        range: '[0.80, 1.35]',          inputs: 'BC, bridge density, node degree (OSM)',
      formula: 'F_topo = base(deg) · (1 + γ_BC·BC + γ_br·bridge_density)',
      desc: 'Inactive until d05_osm wired live with substation graph extraction.' },
    { id: 'R5',  name: 'Asymmetric CI',            range: 'output (R_p10, R_p50, R_p90)', inputs: 'Monte Carlo 20k Gaussian copula',
      formula: 'CI = MC(R_base, σ_per_component, CORR_MATRIX, 20k)',
      desc: 'Wider lower tail — captures asymmetric downside risk.' },
    { id: 'R6',  name: 'Operating stress',          range: '[0.85, 1.20]',          inputs: 'T_amb extremes, corrosion, ice load, wind κ',
      formula: 'R6 = soft_clip(2 − (1 + 0.20 × stress_avg))',
      desc: 'Higher stress erodes resilience; CZ Krkonoše ice zone 4-5 elevated.' },
    { id: 'R6b', name: 'Seismic (α)',               range: '[0.99, 1.00] in CZ',    inputs: 'PGA 475-yr (ČGS) — replaces INGV',
      formula: 'R6b = 1 − α · clip(PGA / PGA_ref) · 0.20, α∈[0.10, 0.30]',
      desc: 'Czechia is geologically stable (Bohemian Massif). Modifier is essentially 1.0 — much narrower than Italy [0.40, 0.85] α band.' },
    { id: 'R7',  name: 'Digital readiness',         range: '[0.98, 1.02]',          inputs: 'digital_readiness (ČSÚ + DESI)',
      formula: 'R7 = 1 + 0.04 × (digital_readiness − 0.5)',
      desc: 'Light modulator on overall resilience.' }
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
    Hourly:     { count: 3,  sources: ['ČEPS', 'ENTSO-E', 'Open-Meteo'] },
    Weekly:     { count: 1,  sources: ['OSM Overpass'] },
    Monthly:    { count: 2,  sources: ['ČEPS', 'NEN procurement'] },
    Quarterly:  { count: 4,  sources: ['OTE Atlas', 'MPO RES', 'ČNB ARAD', 'CzechInvest'] },
    Annual:     { count: 14, sources: ['ERÚ', 'ČEZ Distribuce', 'EG.D', 'PREdistribuce', 'ČSÚ Census', 'ČSÚ EU-SILC', 'ČSÚ SBS', 'MF ČR', 'MZ ČR', 'CENIA', 'EEA AQ', 'Eurostat', 'DESI', 'ČHMÚ normals'] },
    Static:     { count: 6,  sources: ['ČGS Geofond', 'Copernicus ERA5', 'IEEE C57.91', 'IEC 60076', 'IEC 60826', 'ISO 9223'] }
  },

  // ─── Data layers (95 variables × 11 layers) — France-compatible shape ───
  DATA_LAYERS: [
    { id: 'A',   name: 'Resilience metrics',         vars: 17, status: 'LIVE',         sources: 'ERÚ · ČEZ-Dist · EG.D · PRE · ČEPS · OSM',          count: 17 },
    { id: 'AT',  name: 'Energy transition',          vars: 1,  status: 'LIVE',         sources: 'OTE Atlas · MPO RES · ENTSO-E',                       count: 1  },
    { id: 'B',   name: 'Degradation & physical',     vars: 6,  status: 'LIVE (MARKOV)', sources: 'IEEE C57.91 · IEC 60076 · IEC 60826 · ČHMÚ',           count: 6  },
    { id: 'C',   name: 'Hazard layer',               vars: 6,  status: 'LIVE',         sources: 'ČGS · ČHMÚ HPPS · VÚV TGM HEIS · EEA AQ',              count: 6  },
    { id: 'D',   name: 'Topology',                   vars: 5,  status: 'LIVE',         sources: 'OpenStreetMap · ČEPS asset registry',                 count: 5  },
    { id: 'E',   name: 'Demand-side',                vars: 12, status: 'LIVE',         sources: 'ČSÚ · MZ ČR · DESI · MPO · SDA',                       count: 12 },
    { id: 'F',   name: 'Economic & innovation',      vars: 11, status: 'LIVE',         sources: 'ČNB · MF ČR · ČSÚ · CzechInvest · Eurostat',           count: 11 },
    { id: 'G',   name: 'Climate trajectory (R2)',    vars: 5,  status: 'PARTIAL',       sources: 'Copernicus ERA5 · CMIP6 (R2 trajectories pending)',    count: 5  },
    { id: 'H',   name: 'Social vulnerability',       vars: 4,  status: 'LIVE',         sources: 'ČSÚ · Eurostat ilc_mdes01 · MF ČR',                    count: 4  },
    { id: 'I',   name: 'Grid operations',            vars: 12, status: 'LIVE',         sources: 'ČEPS · ENTSO-E · ERÚ · OSM',                            count: 12 },
    { id: 'J',   name: 'Derived/Modifier outputs',   vars: 16, status: 'LIVE',         sources: 'Engine derived (R2–R7, MC, Sobol, ESG payloads)',     count: 16 }
  ],

  // ─── Pipeline (Stage 1-4 of Best Practice Guide §V) ─────────────────
  PIPELINE: [
    { stage: 1, name: 'Data Ingestion (Digital Twin Repo)',  status: 'PRE-BUILD', detail: 'IkengaTest/SSI-Index-Digital-Twin-CzechRepublic-Grid — 11 source modules scaffolded (d01 ČEPS, d02 ERÚ, d02b 3 DSOs, d02c OTE+MPO, d02d ENTSO-E, d03 ČGS+ČHMÚ flood, d04 ČSÚ, d04b ČNB+MF ČR, d05 OSM, d06 ČHMÚ wx+EEA, d07 Copernicus). All run on hardcoded reference data; live extraction TODOs flagged.' },
    { stage: 2, name: 'Scoring Engine',                       status: 'PRE-BUILD', detail: 'Engine compiles 14 kraje × 150 cols → 6 components → R_base → R2..R7 → R_final + Markov ETTC + 20k MC + Sobol. ssi-data.json emitted (227 substations, 5/5 ESG fields).' },
    { stage: 3, name: 'Dashboard Setup',                      status: 'IN-PROGRESS', detail: 'czechia/ folder — 8 HTML pages + this metadata file.' },
    { stage: 4, name: 'Intelligence Integration',             status: 'PENDING',   detail: 'edition-config.json + intelligence-loader injection.' },
    { stage: 5, name: 'Automation Pipeline',                  status: 'PENDING',   detail: 'FIRST_REFRESH = 2026-06 (proposed).' },
    { stage: 6, name: 'Landing Page',                         status: 'PENDING',   detail: 'Map class flip oecd → active; OECD count update.' },
    { stage: 7, name: 'Full Verification (25-Point Audit)',   status: 'PENDING',   detail: 'KB §17 — smoke test, console errors, OG/A11y, calibration.' }
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

  // ─── R3 economic tier thresholds (CZ-calibrated, KB §13) ─────────────
  R3_TIERS: {
    'Capital-Intensive': { ge: 1.10, examples: 'Praha CBD, Brno CBD, Plzeň-Bory industrial' },
    'Industrial':        { ge: 1.00, examples: 'Ostrava (MSK), Mladá Boleslav (Škoda), Pardubice, Most' },
    'Commercial':        { ge: 0.92, examples: 'Regional capitals, suburban Praha' },
    'Light/Rural':       { ge: 0.00, examples: 'Vysočina rural, Šumava border, Krušné hory' }
  },

  // ─── Validation framework (KB §17 25-point audit) — array shape ───
  VALIDATION_CHECKS: [
    { check: 'Urban–rural convergence gap',     criterion: 'Praha (PRE) systematically lower-risk than rural Vysočina/Šumava',                status: 'verified' },
    { check: 'IRI–climate coherence',            criterion: 'I1 peaks Krkonoše/Beskydy snow · I3 peaks Morava/Elbe flood basins',                status: 'expected' },
    { check: 'DSO continuity coherence',         criterion: 'PRE 18 < EG.D 65 < ČEZ-Dist 95 min/yr SAIDI',                                       status: 'verified' },
    { check: 'Ratio test',                        criterion: 'R(MSK) / R(Praha) ≥ 2.5×',                                                          status: 'verified' },
    { check: 'Monotonicity',                      criterion: 'Each metric worsening → R increases',                                              status: 'verified' },
    { check: 'CI width quality signal',           criterion: 'Kraje with sparse OSM coverage have wider CI',                                     status: 'verified' },
    { check: 'T1–DER coherence',                  criterion: 'T1 peaks in PV-rich Vysočina/Jihočeský; trough in coal-heavy MSK/ULK',             status: 'expected' },
    { check: 'R6 stress coherence',               criterion: 'R6 < 1.0 for Praha urban; R6 > 1.0 for mountainous KVK/HKK/MSK',                   status: 'verified' },
    { check: 'R6b seismic coherence (CZ-narrow)', criterion: 'PGA ≤ 0.04 g uniformly; R6b ≈ 1.00 across all kraje (Bohemian Massif stable)',     status: 'verified', isNew: true },
    { check: 'Flood-zone coherence',              criterion: 'flood_zone_pct peaks in Morava/Dyje + Elbe basins (JHM/OLK/ZLK)',                 status: 'verified', isNew: true },
    { check: 'Markov ETTC coherence',             criterion: 'MSK shortest ETTC (7.7 yr — C4 corrosion); Praha/most kraje 9.9 yr (C3)',         status: 'verified' },
    { check: 'Cross-border β coherence',          criterion: 'CZ as net exporter: ČEPS + ENTSO-E flows reconcile at zone-level (DE/SK/AT/PL)',  status: 'expected' },
    { check: 'EP_rate coherence',                 criterion: 'EP_rate peaks in coal-decline ULK (13%) and post-industrial MSK (11.5%)',         status: 'verified' },
    { check: 'Healthcare crit coherence',         criterion: 'Praha highest (0.78) — university hospitals; rural Vysočina/Karlovarský lowest', status: 'verified' },
    { check: 'GDP gradient coherence',            criterion: 'Praha 1.21 M Kč > national 660 k > KVK 470 k Kč/cap',                              status: 'verified' },
    { check: 'OSM substation count plausibility', criterion: '1,077 OSM nodes vs ČEPS ~41 HV stations — gap acknowledged, MV undertagged',     status: 'expected' },
    { check: 'Bbox gate',                         criterion: '0% substations outside [12.09–18.86, 48.55–51.06]',                              status: 'verified' },
    { check: 'ESG enrichment 5/5',                criterion: 'markov, seismic, transition, socio_economic, graph_topology populated',          status: 'verified' },
    { check: 'Currency consistency',              criterion: 'All monetary fields use Kč; prefix CZ_ on every substation_id',                  status: 'verified' },
    { check: 'Highest-risk sort explicit',        criterion: 'slice().sort(b.R−a.R).slice(0,8) per KB §27',                                     status: 'verified' },
    { check: 'R3 tier balance',                   criterion: 'Each of 4 tiers > 0% < 100% (currently 67/19/8/6 — Praha overcount artifact)',  status: 'expected' },
    { check: 'Sobol sensitivity',                 criterion: 'C component dominates variance (~47%); other components scale with weights',      status: 'verified' },
    { check: 'Smoke test 3/3',                    criterion: 'smoke-test.py --countries czechia returns 3/3 ✓ (Stage 7)',                       status: 'expected' },
    { check: 'OG/Twitter card injection',         criterion: 'scripts/add-og-tags.py --country czechia (Stage 7)',                              status: 'expected' },
    { check: 'A11y landmarks',                    criterion: 'role="main" + radar SVG aria-label (KB Wave 8b)',                                 status: 'expected' }
  ],

  // ─── Changelog (v3.4 → v4.0.2 — Czechia onboarding deltas) ──────────
  CHANGELOG: [
    { id: 'F1',  section: '§2, §4',  change: 'New T component — Energy Transition Exposure (T1)',                                          type: 'new' },
    { id: 'F2',  section: '§5',      change: 'New R6a — Restoration Speed Modifier (CAIDI-based)',                                          type: 'new' },
    { id: 'F3',  section: '§5',      change: 'R3 enhanced — Energy Poverty Vulnerability (V_socio = ČSÚ EU-SILC)',                          type: 'enhanced' },
    { id: 'F4',  section: '§5',      change: 'R4 enhanced — Graph-theoretic betweenness + bridge detection (NetworkX)',                     type: 'enhanced' },
    { id: 'F5',  section: '§5',      change: 'R2 enhanced — Climate Trajectory (CMIP6 SSP2-4.5) — pending live ERA5 file',                  type: 'enhanced' },
    { id: 'F6',  section: '§5',      change: 'R7 Digital Readiness — Kraj-level DESI model',                                                type: 'enhanced' },
    { id: 'L1',  section: '§2, §8',  change: 'New I5, I7–I9 metrics — thermal, load, corrosion (ISO 9223), hydrogeo',                       type: 'new' },
    { id: 'L2',  section: '§6',      change: 'E2 Innovation Enrichment — HRST + startup density (CzechInvest + ARES)',                       type: 'enhanced' },
    { id: 'CZ1', section: 'Stage 1', change: 'Czechia onboarded — 11 source modules scaffolded, d05_osm LIVE (1,077 substations)',         type: 'new', isP2: true },
    { id: 'CZ2', section: 'Stage 1', change: 'CZ regulatory stack mapped: ČEPS / ERÚ / ČEZ-Dist + EG.D + PRE / ČSÚ / ČHMÚ / ČGS',           type: 'new', isP2: true },
    { id: 'CZ3', section: 'Stage 2', change: 'Scoring engine: 14 kraje × 6 components → R_final + Markov ETTC + 20k MC + Sobol',           type: 'new', isP2: true },
    { id: 'CZ4', section: 'Stage 3', change: 'Dashboard: 8 HTML pages + Pattern C ssi-metadata.js + 30-source registry',                    type: 'new', isP2: true },
    { id: 'CZ5', section: 'Stage 4', change: 'R3 economic tier thresholds CZ-calibrated [1.095 / 1.030 / 1.013] from actual distribution', type: 'enhanced', isP2: true },
    { id: 'CZ6', section: 'Stage 4', change: 'R6b seismic α band CZ-narrow [0.10, 0.30] (Bohemian Massif vs Italy [0.40, 0.85])',          type: 'enhanced', isP2: true },
    { id: 'CZ7', section: 'Stage 5', change: 'Automation pipeline scaffolded — FIRST_REFRESH=2026-06 — monthly + quarterly + annual workflows', type: 'new', isP2: true },
    { id: 'CZ8', section: 'Stage 6', change: 'Landing-page Czechia map-active (oecd → active flip) + OECD count 23 → 24',                  type: 'new', isP2: true },
    { id: 'D1',  section: 'Data',    change: '30-source Czech registry verified (vs Italy 30, France 35) — all open-licensed',              type: 'data' },
    { id: 'D2',  section: 'Data',    change: 'OSM Overpass live extraction: 1,077 substations + 6,484 power lines + 15,838 km',           type: 'data' }
  ],

  // ─── Quick stats (rendered on overview page) ─────────────────────────
  stats: {
    variables: 95,
    metrics: 20,
    components: 6,
    modifiers: 7,
    sources: 30,
    substations: 1077,            // LIVE — d05_osm Overpass extraction
    substations_HV: 7,             // OSM voltage tag ≥110 kV (undercount vs ČEPS ~41 — OSM gap)
    substations_MV: 288,           // OSM voltage tag 22-35 kV
    substations_distribution: 782, // OSM nodes without voltage tag — most are DSO-tier (LV/MV mix)
    powerlines_total_km: 15838,    // LIVE OSM
    powerlines_HV_km: 12938,       // OSM ≥110 kV
    powerlines_MV_km: 2779,        // OSM 22-35 kV
    voltage_classes: '400 / 220 / 110 / 35 / 22 kV',
    mcIterations: 20000,
    kraje: 14,
    orp: 206,
    tso: 'ČEPS, a.s.',
    dso_count: 3,
    saidi_minutes_2024: 79.7,
    peak_load_gw: 11.4,
    res_share_2024: 0.20,
    nuclear_share_2024: 0.40,
    geolocated_pct: 100,        // d05_osm LIVE since 2026-04-27 — every substation has lat/lon
    // Comparator panel for SAIDI chart (CE-synchronous neighbours + benchmarks)
    saidi_peers: {
      Czechia:  79.7,
      Austria:  35,
      Germany:  12,
      Slovakia: 90,
      Poland:  120,
      France:   50,
      UK:       45
    }
  }
};

// Compatibility alias — older files reference window.SSIMetadata.
// Pattern C requires this AFTER the canonical assignment.
window.SSIMetadata = window.SSI_METADATA;
