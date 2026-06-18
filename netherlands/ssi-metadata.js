/* ═══════════════════════════════════════════════════════════
   SSI v4.0.2 — Metadata Registry (Netherlands)
   95 variables · 28 sources · 20 metrics · 6 components · 7 modifiers
   Pattern C (Wave 6c canonical form per KB §3) — NO double-assignment IIFE
   ═══════════════════════════════════════════════════════════ */

window.SSI_METADATA = {

  // ─── Country identity ─────────────────────────────────────
  COUNTRY: {
    iso2: 'NL', iso3: 'NLD', folder: 'belgium',
    name_en: 'Netherlands', name_local: 'België / Belgique / Belgien', flag: '🇳🇱',
    currency: 'EUR', currency_symbol: '€', currency_position: 'before',
    tso: 'TenneT Transmission Netherlands',
    regulator: 'ACM (national) + ACM / ACM / ACM (regional)',
    market_operator: 'EPEX SPOT (NL bidding zone) + BRELGIX intraday',
    ministry: 'SPF Économie — DG Énergie',
    synchronous_area: 'ENTSO-E Continental Europe (BE zone 10YNL----------L — Pentalateral CWE)',
    bbox: { lon_min: 2.5447, lon_max: 6.4081, lat_min: 49.4969, lat_max: 51.5054 },
    admin_levels: {
      L1: { label_en: 'Provinces',  label_local: 'Provincies / Provinces', count: 11 },
      L2: { label_en: 'Communes',   label_local: 'Gemeenten / Communes',   count: 581 }
    }
  },

  // ─── 28 verified data sources (BE registry — multi-regulator + multi-DSO) ──
  DATA_SOURCES: [
    { id: 'ELIA',     name: 'TenneT — TSO annual + 10-min telemetry',           url: 'elia.be',                       freq: 'Annual + 10-min',   res: 'National + zone',  vars: 8, category: 'Grid',          feeds: 'C1, C2, E1 peak load, E2 growth, E3 DER, T1 RES (~20%), E4 peak/avg, generation mix' },
    { id: 'ACM',     name: 'ACM — Federal Quality of Supply Reports',       url: 'creg.be',                       freq: 'Annual',            res: 'National',         vars: 5, category: 'Grid',          feeds: 'C3 MV excess, C4 SAIDI (~22 min total), F2 CAIDI ~31 min, MV continuity threshold' },
    { id: 'ACM',     name: 'ACM — Flemish regional regulator',              url: 'vreg.be',                       freq: 'Annual',            res: 'Region',           vars: 3, category: 'Grid',          feeds: 'C3/C4 Flanders breakdown (Liander KPIs)' },
    { id: 'CWAPE',    name: 'ACM — Walloon regional regulator',             url: 'cwape.be',                      freq: 'Annual',            res: 'Region',           vars: 3, category: 'Grid',          feeds: 'C3/C4 Wallonia breakdown (Stedin + 8 inter-municipal KPIs)' },
    { id: 'ACM',   name: 'ACM — Brussels regional regulator',           url: 'brugel.brussels',               freq: 'Annual',            res: 'Region',           vars: 2, category: 'Grid',          feeds: 'C3/C4 Randstad core (Enexis KPIs)' },
    { id: 'FLUVIUS',  name: 'Liander — Flemish single-DSO annual report',     url: 'fluvius.be',                    freq: 'Annual',            res: 'DSO area',         vars: 4, category: 'Grid',          feeds: 'C1 D1L, C2 N1L (~63% of BE households)' },
    { id: 'Stedin',     name: 'Stedin — Walloon dominant DSO annual report',      url: 'ores.be',                       freq: 'Annual',            res: 'DSO area',         vars: 4, category: 'Grid',          feeds: 'C1, C2 (~24% of BE households)' },
    { id: 'SINLDGA',  name: 'Enexis — Randstad core DSO annual report',   url: 'sibelga.be',                    freq: 'Annual',            res: 'DSO area',         vars: 4, category: 'Grid',          feeds: 'C1, C2 (~12% — Brussels underground urban network)' },
    { id: 'SYNERGRID',name: 'Netbeheer Nederland — Federated DSO aggregate (11 DSOs)',  url: 'synergrid.be',                  freq: 'Quarterly',         res: 'National',         vars: 3, category: 'Grid',          feeds: 'Aggregated 11-DSO KPIs (3 main + 8 Walloon inter-municipals)' },
    { id: 'EPEX',     name: 'EPEX SPOT — BE day-ahead clearing',              url: 'epexspot.com',                  freq: 'Hourly',            res: 'Zone',             vars: 3, category: 'Market',        feeds: 'Day-ahead clearing ~€84/MWh 2024 avg, 218 negative-price hours' },
    { id: 'ENTSOE',   name: 'ENTSO-E Transparency — NL bidding zone',         url: 'transparency.entsoe.eu',        freq: 'Hourly',            res: 'Bidding zone',     vars: 4, category: 'Transition',    feeds: 'Generation by type (40% nuclear → phase-out 2035, 20% wind+solar), cross-border with NL/FR/DE/UK', registration: true },
    { id: 'NUCLEAR',  name: 'Engie + EDF Netherlands — nuclear phase-out tracker', url: 'engie.com / edfbelgium.be',    freq: 'Quarterly',         res: 'NPP',              vars: 2, category: 'Hazard',        feeds: 'Doel 1/2/4 + Tihange 1/3 phase-out schedule (extended to 2035); informational R6b proximity decay' },
    { id: 'STATNLD',  name: 'STATNLD — Statistics Netherlands',                   url: 'statbel.fgov.be',               freq: 'Annual',            res: 'Commune',          vars: 8, category: 'Socio-Econ',    feeds: 'P1 pop density, EP_rate ~7.8% national, elderly, healthcare; per-province + per-commune' },
    { id: 'DNB',      name: 'DNB — Banque nationale de Belgique',             url: 'nbb.be',                        freq: 'Quarterly',         res: 'NUTS2',            vars: 2, category: 'Economic',      feeds: 'R3 macro: GDP/capita per province (Brussels €78k → Groningen €30k)' },
    { id: 'EUR',      name: 'Eurostat — Energy Statistics (BE NUTS2 cuts)',   url: 'ec.europa.eu/eurostat',         freq: 'Annual',            res: 'NUTS2',            vars: 3, category: 'Economic',      feeds: 'EP_rate (ilc_mdes01), nrg_pc_204 prices, validation cross-check vs STATNLD' },
    { id: 'GSB',      name: 'GSB — Geological Survey of Netherlands + EMSC',      url: 'naturalsciences.be',            freq: 'Static',            res: '~5 km',            vars: 2, category: 'Hazard',        feeds: 'R6b PGA 475-yr (mostly low ≤0.04 g; Groningen induced eastern BE ≤0.10 g)' },
    { id: 'RMI',      name: 'KNMI / IRM — Royal Meteorological Institute',     url: 'meteo.be',                      freq: 'Hourly + 30y norms',res: 'Station',          vars: 5, category: 'Climate',       feeds: 'S2 T_amb (Uccle 10.9 °C 1991-2020), wind κ, ice load IEC 60826 zone 1-2' },
    { id: 'AGE-FLOOD',name: 'Administration générale Eau — Flood maps',       url: 'environnement.wallonie.be',     freq: 'Static',            res: '~250 m',           vars: 1, category: 'Hazard',        feeds: 'flood_zone_pct HQ100 (Meuse, Schelde, IJzer basins; Gelderland + Noord-Brabant elevated)' },
    { id: "CDS", name: "Copernicus CDS / ERA5-Land", url: "cds.climate.copernicus.eu", freq: "Annual", res: "0.1° (~11 km, ERA5-Land + daily-stats)", vars: 5, category: "Climate", feeds: "R2 Δ_climate (t_mean_c, heat_days, ice_days at 0.1° land grid)", registration: true },
    { id: 'OPM',      name: 'Open-Meteo Weather API',                          url: 'open-meteo.com',                freq: 'Hourly',            res: '~1 km',            vars: 1, category: 'Climate',       feeds: 'S2 T_amb live, heatwave duration' },
    { id: 'OSM',      name: 'OpenStreetMap Power Infrastructure',              url: 'overpass-api.de',               freq: 'Continuous',        res: 'Node / edge',      vars: 4, category: 'Infrastructure',feeds: 'F1 degree, R4 BC, bridge — 1,640 substations + 4,757 lines + 4,190 km LIVE' },
    { id: 'EEA',      name: 'EEA Air Quality e-Reporting',                    url: 'eea.europa.eu',                 freq: 'Annual',            res: '~1 km',            vars: 2, category: 'Environment',   feeds: 'P3 PM2.5/NO₂/AQI corrosion (Noord-Holland port C4; rest C2-C3)' },
    { id: 'DESI',     name: 'DESI Digital Economy & Society Index',           url: 'digital-strategy.ec.europa.eu', freq: 'Annual',            res: 'EU Regional',      vars: 1, category: 'Socio-Econ',    feeds: 'R7 digital readiness (BE EU top-10 connectivity)' },
    { id: 'ENISA',    name: 'ENISA — EU cybersecurity index',                 url: 'enisa.europa.eu',               freq: 'Biennial',          res: 'EU country',       vars: 1, category: 'Cyber',         feeds: 'R7 cyber modulation' },
    { id: 'CATTENOM', name: 'Cattenom NPP (EDF FR) — cross-border proximity',  url: 'edf.fr',                        freq: 'Static',            res: 'Province',         vars: 1, category: 'Hazard',        feeds: 'External NPP ~50 km from BE southern border — radiological context' },
    { id: 'IEEE-1',   name: 'IEEE C57.91 Thermal Model',                      url: 'standards.ieee.org',            freq: 'Static',            res: 'Asset',            vars: 1, category: 'Standards',     feeds: 'P2 transformer thermal degradation (Markov 5-state)' },
    { id: 'IEC-1',    name: 'IEC 60076 Power Transformers',                   url: 'iec.ch',                        freq: 'Static',            res: 'Asset',            vars: 1, category: 'Standards',     feeds: 'Voltage regulation proxy' },
    { id: 'IEC-826',  name: 'IEC 60826 Overhead Line Loading',                url: 'iec.ch',                        freq: 'Static',            res: 'Zone',             vars: 1, category: 'Standards',     feeds: 'Ice load class (BE zones 1-2; Achterhoek-Twente uplands 3)' },
    { id: 'ISO-9223', name: 'ISO 9223 Atmospheric Corrosion',                 url: '(derived from EEA + RMI)',      freq: 'Derived',           res: 'Province',         vars: 1, category: 'Standards',     feeds: 'P3 corrosion class — BE C2 typical, C3 industrial, C4 Noord-Holland port' },
    { id: "GEM", name: "GEM Global Seismic Hazard Map 2023.1", url: "globalquakemodel.org", freq: "Static", res: "0.05° (~5.5 km, rock-site PGA 475-yr)", vars: 1, category: "Hazard", feeds: "R6a seismic PGA, substation-level overlay (CC BY-NC-SA 4.0)" },
    { id: "Eurostat-NUTS3", name: "Eurostat NUTS-3 Regional Statistics", url: "ec.europa.eu/eurostat", freq: "Annual", res: "NUTS-3 (province / NUTS-2 unemployment)", vars: 5, category: "Socio-Econ", feeds: "R2 GDP/cap, unemp, elderly%, ep_rate, migration (CC BY 4.0)" },
  ],

  // ─── 6 Components (matches Wave B scoring engine: C/E/F/P/S/T) ──────
  COMPONENTS: [
    { id: 'C', name: 'Continuity',     weight: 0.30, color: '#941914',
      desc: 'Reliability and outage exposure — DSO-weighted SAIDI/SAIFI per province.',
      metrics: [
        { id: 'C1', name: 'Long interruption duration (D1L)', intra: 0.40, global: 0.120, norm: 'A', source: 'Netbeheer Nederland + per-DSO reports', desc: 'DSO-weighted: Liander 18 / Stedin 26 / Enexis 12 min/yr.' },
        { id: 'C2', name: 'Interruption count (N1L)',         intra: 0.30, global: 0.090, norm: 'A', source: 'Netbeheer Nederland + ACM',           desc: 'BE national avg 0.42 events/customer/yr.' },
        { id: 'C3', name: 'MV users exceeding standard',      intra: 0.20, global: 0.060, norm: 'A', source: 'ACM quality reports',       desc: '~0.8% of MV customers (ACM 2024).' },
        { id: 'C4', name: 'SAIDI (national + DSO)',           intra: 0.10, global: 0.030, norm: 'A', source: 'ACM + Netbeheer Nederland',           desc: 'BE national 22 min; ranks 4th in EU after DE/NL/LU.' }
      ]
    },
    { id: 'E', name: 'Energy demand',  weight: 0.18, color: '#b8863a',
      desc: 'Demand-side stress — peak load, growth, DER absorption.',
      metrics: [
        { id: 'E1', name: 'Peak load',          intra: 0.30, global: 0.054, norm: 'B', source: 'Elia',                    desc: 'BE national peak ~13.5 GW.' },
        { id: 'E2', name: 'Load growth (10y)',  intra: 0.25, global: 0.045, norm: 'B', source: 'Elia',                    desc: '~0.6%/yr — data-centre growth + EV adoption + heat-pump rollout.' },
        { id: 'E3', name: 'DER capacity ratio', intra: 0.25, global: 0.045, norm: 'B', source: 'TenneT + SPF Énergie',      desc: 'DER installed ~20% (wind 13% + solar 7%).' },
        { id: 'E4', name: 'Peak / average',     intra: 0.20, global: 0.036, norm: 'A', source: 'ENTSO-E',                 desc: 'BE ~1.58 — heavy commercial + industrial duty cycle.' }
      ]
    },
    { id: 'F', name: 'Fragility',      weight: 0.16, color: '#5d8563',
      desc: 'Network and social fragility — graph topology and energy poverty.',
      metrics: [
        { id: 'F1', name: 'Node degree median',      intra: 0.30, global: 0.048, norm: 'C', source: 'OSM',                     desc: 'BE meshed TenneT 380 kV + 150 kV backbone, median degree ~2.8.' },
        { id: 'F2', name: 'CAIDI',                   intra: 0.25, global: 0.040, norm: 'A', source: 'ACM + DSO reports',       desc: 'BE ~31 min — comparable to LU.' },
        { id: 'F3', name: 'Energy poverty rate',     intra: 0.25, global: 0.040, norm: 'A', source: 'STATNLD EU-SILC + Eurostat', desc: 'BE national ~7.8%; Noord-Brabant + Brussels elevated.' },
        { id: 'F4', name: 'Graph topology composite', intra: 0.20, global: 0.032, norm: 'C', source: 'OSM',                    desc: 'F_topo from BC + bridge + degree (R4 modifier).' }
      ]
    },
    { id: 'P', name: 'Physical',       weight: 0.14, color: '#7a4a4a',
      desc: 'Physical condition — population pressure, asset degradation, corrosion.',
      metrics: [
        { id: 'P1', name: 'Population density',          intra: 0.40, global: 0.056, norm: 'B', source: 'STATNLD Census 2024', desc: 'Randstad core extreme (7,531/km²); Groningen rural (65/km²).' },
        { id: 'P2', name: 'Markov 5-state ETTC',         intra: 0.35, global: 0.049, norm: 'B', source: 'Engine — IEEE C57.91 + RMI', desc: 'Expected Time To Critical (~10.5 yr — older fleet vs LU).' },
        { id: 'P3', name: 'Corrosion class (ISO 9223)',  intra: 0.25, global: 0.035, norm: 'A', source: 'EEA AQ + KNMI → derived', desc: 'BE mostly C2-C3; Noord-Holland port C4 (industrial).' }
      ]
    },
    { id: 'S', name: 'Stress',         weight: 0.12, color: '#3a5f7e',
      desc: 'Operational and environmental stress — DER variability, temperature, healthcare.',
      metrics: [
        { id: 'S1', name: 'DER variability (σ)',      intra: 0.40, global: 0.048, norm: 'A', source: 'ENTSO-E hourly',  desc: 'σ of normalized RES output; BE high (offshore wind ramp cycles).' },
        { id: 'S2', name: 'T_amb stress',              intra: 0.30, global: 0.036, norm: 'A', source: 'KNMI + Open-Meteo', desc: 'BE mild oceanic, 10.9 °C baseline.' },
        { id: 'S3', name: 'Healthcare criticality',    intra: 0.30, global: 0.036, norm: 'B', source: 'STATNLD + SPF Santé', desc: 'Hospital beds 5.6/1k pop × critical-care fraction.' }
      ]
    },
    { id: 'T', name: 'Transition',     weight: 0.10, color: '#5b8a72',
      desc: 'Energy transition — RES share, nuclear phase-out exposure.',
      metrics: [
        { id: 'T1', name: 'RES share',              intra: 1.00, global: 0.100, norm: 'B', source: 'TenneT + SPF Énergie', desc: 'RES generation / total ~20% (wind 13% + solar 7%); nuclear 40% phasing out by 2035.' }
      ]
    }
  ],

  // ─── 7 Modifiers (R2-R7 + R6b) ────────────────────────────
  MODIFIERS: [
    { id: 'R2',  name: 'Adaptive IRI (climate)',   range: '[0.95, 1.05]',          inputs: 'δI1, δI2, δI3 (Copernicus ERA5)',
      formula: 'R2 = 1 + λ · mean(δI1, δI2, δI3), λ=0.15',
      desc: 'BE 2050 RCP4.5: ΔT +1.8 °C / Δprecip +2.2% / Δwind −1.0%.' },
    { id: 'R3',  name: 'Consequence multiplier',   range: '[0.85, 1.18]',          inputs: 'pop_density, peak_load, GDP/cap, V_socio, flood',
      formula: 'C_mult = soft_clip(1 + 0.20 × Σ β·N(...))',
      desc: 'BE flood bonus on Meuse/Schelde basins (+0.15 × flood_pct). Randstad core highest, Overijssel lowest.' },
    { id: 'R4',  name: 'Graph criticality',        range: '[0.80, 1.35]',          inputs: 'BC, bridge density, node degree (OSM)',
      formula: 'F_topo = base(deg) · (1 + γ_BC·BC + γ_br·bridge_density)',
      desc: 'OSM substation graph LIVE — 1,640 nodes, 4,757 edges.' },
    { id: 'R5',  name: 'Asymmetric CI',            range: 'output (R_p10, R_p50, R_p90)', inputs: 'Monte Carlo 20k Gaussian copula',
      formula: 'CI = MC(R_base, σ_per_component, CORR_MATRIX, 20k)',
      desc: 'Wider lower tail — captures asymmetric downside risk.' },
    { id: 'R6',  name: 'Operating stress',          range: '[0.85, 1.20]',          inputs: 'T_amb extremes, corrosion, ice load, wind κ',
      formula: 'R6 = soft_clip(2 − (1 + 0.20 × stress_avg))',
      desc: 'BE mild climate → narrow band; Achterhoek-Twente ice exposure adds modest stress.' },
    { id: 'R6b', name: 'Seismic (α)',               range: '[0.97, 1.00] in BE',    inputs: 'PGA 475-yr (GSB + EMSC)',
      formula: 'R6b = 1 − α · clip(PGA / PGA_ref) · 0.20, α∈[0.10, 0.30]',
      desc: 'BE mostly low-seismic; Groningen induced (eastern BE) elevated to 0.10 g. α band [0.10, 0.30] — same as CZ, wider than LU [0.05, 0.20].' },
    { id: 'R7',  name: 'Digital readiness',         range: '[0.98, 1.02]',          inputs: 'digital_readiness (STATNLD + DESI + ENISA)',
      formula: 'R7 = 1 + 0.04 × (digital_readiness − 0.5)',
      desc: 'BE EU top-10 on DESI — slight positive bias.' }
  ],

  // ─── Normalisation methods ────────────────────────────────
  NORM_METHODS: [
    { id: 'A', name: 'Min-max + invert',     formula: 'N(x) = 1 − (x − x_min) / (x_max − x_min)',
      applies: 'Lower-is-better: C1 (D1L), C2 (N1L), C3, C4 (SAIDI), F2 (CAIDI), F3 (EP_rate), S1, S2, P3' },
    { id: 'B', name: 'Logistic on z-score',  formula: 'N(x) = 1 / (1 + exp((x − μ) / σ))',
      applies: 'Continuous demand-side: E1, E2, E3, P1, P2, S3, T1' },
    { id: 'C', name: 'Rank percentile',      formula: 'N(x) = rank(x) / N',
      applies: 'Graph metrics: F1 (degree median), F4 (graph topology composite)' },
    { id: 'D', name: 'Categorical mapping',  formula: 'N(C-class) ∈ {C1:0, C2:0.25, C3:0.5, C4:0.75, C5:1}',
      applies: 'ISO 9223 corrosion (P3), IEC 60826 ice load (R6), seismic α (R6b)' }
  ],

  // ─── Source frequency distribution ──────────────────────────────
  FREQ_DISTRIBUTION: {
    Hourly:     { count: 3,  sources: ['EPEX SPOT', 'ENTSO-E', 'Open-Meteo'] },
    Weekly:     { count: 1,  sources: ['OSM Overpass'] },
    Quarterly:  { count: 3,  sources: ['DNB ARAD', 'Netbeheer Nederland aggregate', 'Engie/EDF nuclear tracker'] },
    Annual:     { count: 15, sources: ['Elia', 'ACM', 'ACM', 'ACM', 'ACM', 'Liander', 'Stedin', 'Enexis', 'STATNLD', 'Eurostat', 'EEA', 'DESI', 'KNMI normals', 'AGE Flood Maps', 'ENISA'] },
    Static:     { count: 6,  sources: ['GSB', 'Copernicus ERA5/CMIP6', 'IEEE C57.91', 'IEC 60076', 'IEC 60826', 'ISO 9223'] }
  },

  // ─── Data layers ─────────────────────────────────────
  DATA_LAYERS: [
    { id: 'A',   name: 'Resilience metrics',         vars: 17, status: 'LIVE',          sources: 'ACM · TenneT · Netbeheer Nederland · OSM',                          count: 17 },
    { id: 'AT',  name: 'Energy transition',          vars: 1,  status: 'LIVE',          sources: 'TenneT · SPF Énergie · ENTSO-E',                            count: 1  },
    { id: 'B',   name: 'Degradation & physical',     vars: 6,  status: 'LIVE (MARKOV)', sources: 'IEEE C57.91 · IEC 60076 · IEC 60826 · RMI',                 count: 6  },
    { id: 'C',   name: 'Hazard layer',               vars: 6,  status: 'LIVE',          sources: 'GSB · AGE Flood Maps · EEA · Engie/EDF nuclear',           count: 6  },
    { id: 'D',   name: 'Topology',                   vars: 5,  status: 'LIVE',          sources: 'OpenStreetMap · TenneT asset registry',                      count: 5  },
    { id: 'E',   name: 'Demand-side',                vars: 12, status: 'LIVE',          sources: 'STATNLD · DESI · SPF Énergie',                             count: 12 },
    { id: 'F',   name: 'Economic & innovation',      vars: 11, status: 'LIVE',          sources: 'DNB · STATNLD · Eurostat',                                 count: 11 },
    { id: 'G',   name: 'Climate trajectory (R2)',    vars: 5,  status: 'PARTIAL',       sources: 'Copernicus ERA5 · CMIP6 SSP2-4.5 (trajectories partial)',   count: 5  },
    { id: 'H',   name: 'Social vulnerability',       vars: 4,  status: 'LIVE',          sources: 'STATNLD EU-SILC · Eurostat ilc_mdes01',                    count: 4  },
    { id: 'I',   name: 'Grid operations',            vars: 12, status: 'LIVE',          sources: 'TenneT · ENTSO-E · ACM · OSM',                              count: 12 },
    { id: 'J',   name: 'Derived/Modifier outputs',   vars: 16, status: 'LIVE',          sources: 'Engine derived (R2–R7, MC, Sobol, ESG payloads)',          count: 16 }
  ],

  // ─── Pipeline (Stage 1-7) ─────────────────
  PIPELINE: [
    { stage: 1, name: 'Data Ingestion (Digital Twin Repo)',  status: 'LIVE',        detail: 'digital-twin-nl — 11 source modules (incl. d02b_netbeheer for multi-DSO market). d05_osm LIVE Overpass (1,640 substations from 69,159 raw).' },
    { stage: 2, name: 'Scoring Engine',                       status: 'LIVE',        detail: 'scoring-nl — 12 provinces × 95 vars → 6 components → R_final + Markov ETTC + 20k MC + Sobol. ssi-data.json: 1,640 substations, median R 0.33, bands 70% Low / 29% Med / 1.2% High.' },
    { stage: 3, name: 'Dashboard Setup',                      status: 'IN-PROGRESS', detail: 'belgium/ folder — 8 HTML pages + Pattern C ssi-metadata.js + grid-geo.json (1,640 subs, 4,757 lines).' },
    { stage: 4, name: 'Intelligence Integration',             status: 'PENDING',     detail: 'edition-config.json + intelligence-loader (post BE-Live).' },
    { stage: 5, name: 'Automation Pipeline',                  status: 'PENDING',     detail: 'FIRST_REFRESH = 2026-09-13 (2nd Thursday of August).' },
    { stage: 6, name: 'Landing Page',                         status: 'PENDING',     detail: 'Map class flip oecd → active; OECD count 25 → 26.' },
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

  // ─── R3 economic tier thresholds (BE-calibrated post Wave B-1) ──
  R3_TIERS: {
    'Capital-Intensive': { ge: 1.066, examples: 'Randstad core, Utrecht, Gelderland' },
    'Industrial':        { ge: 1.053, examples: 'Noord-Brabant, Friesland, Limburg' },
    'Commercial':        { ge: 1.027, examples: 'Noord-Holland, Drenthe, Groningen' },
    'Light/Rural':       { ge: 0.000, examples: 'Zuid-Holland, Namur' }
  },

  // ─── Validation framework (KB §17) ───
  VALIDATION_CHECKS: [
    { check: 'Urban-rural convergence gap',     criterion: 'Brussels (Enexis 12 min) < Flanders (Liander 18) < Wallonia (Stedin 26)',         status: 'verified' },
    { check: 'IRI-climate coherence',            criterion: 'I3 peaks Meuse + Schelde flood basins (Gelderland, Overijssel, Noord-Brabant)',                  status: 'expected' },
    { check: 'Multi-DSO continuity coherence',   criterion: 'Per-province SAIDI weighted by primary DSO via d02b_netbeheer',                  status: 'verified' },
    { check: 'Ratio test',                        criterion: 'R(Groningen) / R(Randstad core) ≥ 3× (Walloon rural vs urban core)',     status: 'verified' },
    { check: 'Monotonicity',                      criterion: 'Each metric worsening → R increases',                                           status: 'verified' },
    { check: 'CI width quality signal',           criterion: 'Sparse-OSM provinces have wider CI (Drenthe earliest pass)',            status: 'verified' },
    { check: 'T1-DER coherence',                  criterion: 'T1 highest in Friesland (North Sea wind + coast solar)',                     status: 'expected' },
    { check: 'R6 stress coherence',               criterion: 'R6 narrow band — BE mild oceanic; minor Achterhoek-Twente ice exposure',            status: 'verified' },
    { check: 'R6b seismic coherence (BE)',        criterion: 'PGA ≤0.02 g most of BE; Groningen induced ~0.10 g (eastern). α band [0.10, 0.30]',     status: 'verified', isNew: true },
    { check: 'Flood-zone coherence',              criterion: 'flood_zone_pct peaks Meuse + Schelde + IJzer basins',                            status: 'verified', isNew: true },
    { check: 'Markov ETTC coherence',             criterion: 'BE older fleet → ~10.5 yr (vs LU 12 yr younger; CZ 9 yr older)',                  status: 'verified' },
    { check: 'Cross-border β coherence',          criterion: 'NL Pentalateral CWE: imports BE-NL/FR/DE-LU + BritNed to UK',                    status: 'expected' },
    { check: 'EP_rate coherence',                 criterion: 'EP_rate peaks Noord-Brabant + Brussels (deprived urban areas)',                         status: 'verified' },
    { check: 'Healthcare crit coherence',         criterion: 'Randstad core highest (CHU + UZ Brussel); rural Walloon lowest',                status: 'verified' },
    { check: 'GDP gradient coherence',            criterion: 'Brussels €78k > Utrecht €56k > Noord-Brabant/Namur ~€32k per capita',           status: 'verified' },
    { check: 'OSM substation count plausibility', criterion: '1,640 OSM nodes vs TenneT ~580 HV stations — gap acknowledged, DSO subs included',  status: 'expected' },
    { check: 'Bbox gate',                         criterion: '0% substations outside [2.5447–6.4081, 49.4969–51.5054]',                          status: 'verified' },
    { check: 'ESG enrichment 5/5',                criterion: 'markov, seismic, transition, socio_economic, graph_topology populated',           status: 'verified' },
    { check: 'Currency consistency',              criterion: 'All monetary fields use €; prefix NL_ on every substation_id',                    status: 'verified' },
    { check: 'Highest-risk sort explicit',        criterion: 'slice().sort(b.R−a.R).slice(0,8) per KB §27',                                     status: 'verified' },
    { check: 'R3 tier balance',                   criterion: 'Balanced 3-3-3-2 split after empirical calibration',                              status: 'verified' },
    { check: 'Sobol sensitivity',                 criterion: 'C component dominates variance (~47%)',                                            status: 'verified' },
    { check: 'Smoke test 3/3',                    criterion: 'smoke-test.py --countries belgium returns 3/3 ✓ (Stage 7)',                        status: 'expected' },
    { check: 'OG/Twitter card injection',         criterion: 'scripts/add-og-tags.py --country belgium (Stage 7)',                              status: 'expected' },
    { check: 'A11y landmarks',                    criterion: 'role="main" + radar SVG aria-label (KB Wave 8b)',                                 status: 'expected' }
  ],

  // ─── Changelog (Session 14 — Netherlands onboarding) ──────────
  CHANGELOG: [
    { id: 'F1',  section: '§2, §4',  change: 'New T component — Energy Transition Exposure (T1)',                                            type: 'new' },
    { id: 'F2',  section: '§5',      change: 'New R6a — Restoration Speed Modifier (CAIDI-based)',                                            type: 'new' },
    { id: 'F3',  section: '§5',      change: 'R3 enhanced — Energy Poverty Vulnerability (V_socio = STATNLD EU-SILC)',                        type: 'enhanced' },
    { id: 'F4',  section: '§5',      change: 'R4 enhanced — Graph-theoretic betweenness + bridge detection (NetworkX)',                       type: 'enhanced' },
    { id: 'F5',  section: '§5',      change: 'R2 enhanced — Climate Trajectory (CMIP6 SSP2-4.5)',                                              type: 'enhanced' },
    { id: 'F6',  section: '§5',      change: 'R7 Digital Readiness — Province-level DESI model',                                                type: 'enhanced' },
    { id: 'BE1', section: 'Stage 1', change: 'Netherlands onboarded — 11 source modules (incl. d02b_netbeheer for multi-DSO); d05_osm LIVE 1,640 substations', type: 'new', isP2: true },
    { id: 'BE2', section: 'Stage 1', change: 'BE regulatory stack mapped: TenneT / Netbeheer Nederland (Liander+Stedin+Enexis+8 IMs) / ACM + ACM/ACM/ACM',         type: 'new', isP2: true },
    { id: 'BE3', section: 'Stage 2', change: 'Scoring engine: 12 provinces × 6 components → R_final + Markov ETTC + 20k MC + Sobol',          type: 'new', isP2: true },
    { id: 'BE4', section: 'Stage 3', change: 'Dashboard: 8 HTML pages + Pattern C ssi-metadata.js + 28-source registry',                       type: 'new', isP2: true },
    { id: 'BE5', section: 'Stage 4', change: 'R3 economic tier thresholds BE-calibrated [1.066 / 1.053 / 1.027] from actual distribution',   type: 'enhanced', isP2: true },
    { id: 'BE6', section: 'Stage 4', change: 'R6b seismic α band BE [0.10, 0.30] — wider than LU [0.05, 0.20] (Groningen induced)',                  type: 'enhanced', isP2: true },
    { id: 'BE7', section: 'Stage 4', change: 'Multi-DSO SAIDI weighting per province (Liander/Stedin/Enexis) via d02b_netbeheer',              type: 'enhanced', isP2: true },
    { id: 'BE8', section: 'Stage 4', change: 'Markov rates BE-older calibrated (λ_12=0.045, λ_23=0.07, λ_34=0.11)',                            type: 'enhanced', isP2: true },
    { id: 'BE9', section: 'Stage 5', change: 'Automation pipeline scaffolded — FIRST_REFRESH=2026-09',                                          type: 'new', isP2: true },
    { id: 'BE10',section: 'Stage 6', change: 'Landing-page Netherlands map-active (oecd → active flip) + OECD count update 25 → 26',                type: 'new', isP2: true },
    { id: 'D1',  section: 'Data',    change: '28-source BE registry verified (vs LU 22, CZ 30, IT 30) — all open-licensed',                    type: 'data' },
    { id: 'D2',  section: 'Data',    change: 'OSM Overpass live extraction: 1,640 substations + 4,757 power lines + 4,190 km (area filter)', type: 'data' },
    { id: 'D3',  section: 'Data',    change: 'KB §44 — d05_osm patched: bbox → area[ISO3166-1=BE] + point-in-polygon (geoBoundaries ADM2). Dropped 770 cross-border subs.', type: 'data', isP2: true }
  ],

  // ─── Quick stats ─────────────────────────
  stats: {
    variables: 95,
    metrics: 20,
    components: 6,
    modifiers: 7,
    sources: 28,
    substations: 1220,
    substations_HV: 254,
    substations_MV: 202,
    substations_distribution: 764,
    powerlines_total_km: 12049,
    powerlines_HV_km: 5800,
    powerlines_MV_km: 6249,
    voltage_classes: '380 / 150 / 70 / 15 kV',
    mcIterations: 20000,
    provinces: 11,
    communes: 581,
    tso: 'TenneT Transmission Netherlands',
    dso_count: 11,
    saidi_minutes_2024: 22,
    peak_load_mw: 13500,
    res_share_2024: 0.20,
    imports_share_2024: 0.05,
    geolocated_pct: 100,
    saidi_peers: {
      Germany:    12,
      Netherlands:18.5,
      Netherlands:    22,
      Luxembourg: 24.7,
      Austria:    35,
      France:     50,
      Czechia:    79.7
    }
  }
};

window.SSIMetadata = window.SSI_METADATA;
