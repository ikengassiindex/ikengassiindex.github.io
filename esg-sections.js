/* ═══════════════════════════════════════════════════════════════════════════
   esg-sections.js — Phase 2b (KB §65) — Thin-shell section handlers
   ───────────────────────────────────────────────────────────────────────────
   Registers section renderers against CountryRenderer for the `esg-report`
   page. The shared definitions (ESG_REPORTS catalogue, component / Markov
   colour palettes, readiness scoring) live here so every country's
   esg-report.html collapses to a thin-shell that calls:

       CountryRenderer.init('<country>', 'esg-report');

   Adding a new country to this pipeline requires only:
     1. The country's `slovenia/`-style folder containing esg-report.html,
        ssi-metadata.js, ssi-data.json, intelligence/.
     2. `window.SSI_METADATA.DATA_SOURCES = [ ... ]` populated in that
        country's ssi-metadata.js (an array of rows of
        [name, source, vintage, frequency, license, reports_tag, blocked_flag?]).
        If absent, the renderer falls back to the Italy defaults so the page
        still produces something usable while the country is wired up.

   Dependencies (loaded by the HTML shell):
     - country-renderer.js  (provides window.CountryRenderer)
     - esg-helpers.js       (bandClass, displayName, readinessLabel, readinessText)
     - Chart.js (CDN)       (Chart global)
     - ssi-metadata.js      (window.SSI_METADATA.*; optional DATA_SOURCES)

   The file has no module footer — sections register themselves at load time.
   ═══════════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  if (!window.CountryRenderer) {
    console.error('[esg-sections] CountryRenderer not loaded — section registrations skipped');
    return;
  }
  var CR = window.CountryRenderer;
  var H = CR.H;
  var Safe = CR.Safe;  // SK hotfix #2 — KB §68.9

  /* ── Constants — ESG report catalogue (6 reports × 7 attributes each) ─── */
  var ESG_REPORTS = [
    {
      id: 'report-1', num: '1', title: 'Climate Physical Risk Assessment',
      framework: 'ESRS E1 · TCFD Physical Risk · EU Taxonomy Annex A',
      sdgPrimary: { num: 13, label: 'SDG 13', name: 'Climate Action', color: '#48773c' },
      sdgSecondary: [
        { num: 9, label: 'SDG 9', color: '#f36d25' },
        { num: 11, label: 'SDG 11', color: '#f99d26' }
      ],
      legendColor: '#aa4234',
      why: 'ESRS E1 (Climate Change) is material for 98% of CSRD-reporting companies. TCFD physical risk disclosure is mandatory in 36+ jurisdictions. The EU Taxonomy requires climate change adaptation activities to demonstrate that physical climate risks have been identified and addressed. This report quantifies acute and chronic climate hazard exposure at substation level using ERA5 reanalysis and Markov degradation modelling.',
      sdgRationale: function (d) {
        return 'Target 13.1 calls for strengthening resilience and adaptive capacity to climate-related hazards. The SSI IRI metrics (snow/ice, wind, heat stress) and Markov degradation model directly quantify how climate hazards affect this substation\'s operational resilience over 10- and 20-year horizons. With a Markov risk score of ' + ((d.markov && d.markov.risk_score != null) ? d.markov.risk_score.toFixed(3) : '—') + ' and ETTC of ' + ((d.markov && (d.markov.ettc_years || d.markov.ETTC_years)) || '—') + ' years, this substation\'s climate trajectory can be assessed against TCFD physical risk and EU Taxonomy adaptation screening requirements.';
      },
      getProfile: function (d) {
        return [
          ['Insulation Risk (I component)', (d.components && d.components.I != null) ? d.components.I.toFixed(3) : '—'],
          ['Environment Component (E)', (d.components && d.components.E != null) ? d.components.E.toFixed(3) : '—'],
          ['Seismic PGA', ((d.seismic && d.seismic.pga_g) || '—') + 'g (Zone ' + ((d.seismic && d.seismic.zone) || '—') + ')'],
          ['Markov Risk Score', (d.markov && d.markov.risk_score != null) ? d.markov.risk_score.toFixed(3) : '—'],
          ['ETTC (time to criticality)', (((d.markov && (d.markov.ettc_years || d.markov.ETTC_years)) || '—')) + ' years'],
          ['P(critical) at 20 years', (d.markov && d.markov.p_critical_20yr !== undefined ? (d.markov.p_critical_20yr * 100).toFixed(1) + '%' : '—')],
          ['Corrosion Class', (d.markov && d.markov.corrosion_class) || '—'],
          ['Climate Trajectory (R2)', (d.markov && d.markov.p_crit_20yr !== undefined) ? (d.markov.p_crit_20yr * 100).toFixed(1) + '% (20yr Markov)' : '||NOT ACTIVE||']
        ];
      },
      getVariables: function (d) {
        return [
          ['I1', 'Snow/Ice IRI', '—', 'ESRS E1-9: Financial effects from physical risks', (d.components && d.components.I) ? 'ready' : 'gap'],
          ['I2', 'Tree-fall IRI', '—', 'TCFD Strategy (b): Physical risk impact', (d.components && d.components.I) ? 'ready' : 'gap'],
          ['I3', 'Heat-wave IRI', '—', 'EU Taxonomy Annex A: Heat stress', (d.components && d.components.I) ? 'ready' : 'gap'],
          ['I5', 'Thermal stress', '—', 'ESRS E1-4: Climate mitigation targets', (d.components && d.components.I) ? 'ready' : 'gap'],
          ['R2', 'Climate trajectory', (d.markov && d.markov.p_crit_20yr !== undefined ? (d.markov.p_crit_20yr * 100).toFixed(1) + '% (20yr)' : 'N/A'), 'TCFD Strategy (c): Scenario analysis', (d.markov && d.markov.p_crit_20yr !== undefined) ? 'ready' : 'gap'],
          ['R6b', 'Seismic PGA', ((d.seismic && d.seismic.pga_g) || '—') + 'g', 'EU Taxonomy Annex A: Geophysical hazards', (d.seismic && d.seismic.pga_g) ? 'ready' : 'gap'],
          ['Markov', 'p_critical_10yr', (d.markov && d.markov.p_critical_20yr !== undefined ? (d.markov.p_critical_20yr * 100).toFixed(1) + '%' : '—'), 'TCFD Risk Management: Risk identification', d.markov ? 'ready' : 'gap'],
          ['Markov', 'p_critical_20yr', (d.markov && d.markov.p_critical_20yr !== undefined ? (d.markov.p_critical_20yr * 100).toFixed(1) + '%' : '—'), 'ESRS E1-9: Time horizons', (d.markov && d.markov.p_critical_20yr === 0) ? 'partial' : 'ready']
        ];
      },
      validity: 'IRI metrics are computed from ERA5 reanalysis (31 km, hourly, 1940–present) using IEEE C57.91 thermal loading curves. Markov 5-state degradation is calibrated from CIGRE Technical Brochure 761 (2019) condition assessment data. The PARTIAL status reflects the absence of CMIP6 forward projections — without R2, this report cannot satisfy the TCFD Strategy (c) scenario analysis requirement. All other inputs are production-grade with institutional provenance.'
    },
    {
      id: 'report-2', num: '2', title: 'Grid Equity & Social Vulnerability',
      framework: 'ESRS S1/S2 · SFDR PAI Social Indicators · UN PRI',
      sdgPrimary: { num: 7, label: 'SDG 7', name: 'Affordable and Clean Energy', color: '#fcc30b', dark: true },
      sdgSecondary: [
        { num: 10, label: 'SDG 10', color: '#dd1367' },
        { num: 1, label: 'SDG 1', color: '#e5243b' }
      ],
      legendColor: '#5d8563',
      why: 'ESRS S2 requires companies to disclose impacts on affected communities. SFDR mandates 5 social PAI indicators. The SSI Index is uniquely positioned here because no competing grid risk framework integrates socio-economic vulnerability at substation resolution. This report surfaces where infrastructure risk concentrates in economically disadvantaged populations.',
      sdgRationale: function (d) {
        var se = d.socio_economic || {};
        var vsocio = se.V_socio;
        var ep = se.EP_rate_region;
        return 'Target 7.1 requires universal access to affordable, reliable energy. This substation serves a catchment with V_socio of ' + (vsocio != null ? vsocio.toFixed(2) : '—') + ' and energy poverty rate of ' + (ep || '—') + '%. The R3 social modifier (' + ((d.modifiers && d.modifiers.R3_C_mult != null) ? d.modifiers.R3_C_mult.toFixed(3) : '—') + ') amplifies risk scores in regions with high unemployment, elderly concentration, and net outward migration — making spatial inequality visible and quantifiable at asset level.';
      },
      getProfile: function (d) {
        var se = d.socio_economic || {};
        return [
          ['V_socio (energy poverty index)', se.V_socio != null ? se.V_socio.toFixed(2) : '—'],
          ['EP Rate (energy poverty %)', (se.EP_rate_region || '—') + '%'],
          ['Unemployment Rate', (se.unemployment_rate != null ? se.unemployment_rate.toFixed(1) : '—') + '%'],
          ['GDP per Capita', (function () { var id = d.substation_id || ''; var c = id.indexOf('UK_') === 0 ? '£' : id.indexOf('US_') === 0 ? '$' : id.indexOf('CA_') === 0 ? 'C$' : id.indexOf('JP_') === 0 ? '¥' : id.indexOf('AU_') === 0 ? 'A$' : '€'; return c + ' ' + (se.gdp_per_capita ? se.gdp_per_capita.toLocaleString() : '—'); })()],
          ['R&D % of GDP', (se.rd_pct_gdp != null ? se.rd_pct_gdp.toFixed(1) : '2.1') + '%'],
          ['R3 Social Multiplier', (d.modifiers && d.modifiers.R3_C_mult != null) ? d.modifiers.R3_C_mult.toFixed(3) : '—'],
          ['Elderly Vulnerability', se.elderly_pct ? se.elderly_pct + '%' : '—'],
          ['Migration Score', se.migration_score !== undefined ? se.migration_score.toFixed(2) : '—']
        ];
      },
      getVariables: function (d) {
        var se = d.socio_economic || {};
        return [
          ['V_socio', 'Energy poverty index', se.V_socio != null ? se.V_socio.toFixed(2) : '—', 'ESRS S2-4: Impacts on affected communities', se.V_socio ? 'ready' : 'gap'],
          ['EP_rate', 'Energy poverty rate', (se.EP_rate_region || '—') + '%', 'SFDR PAI #14: Fossil fuel exposure proxy', se.EP_rate_region ? 'ready' : 'gap'],
          ['R3', 'Social multiplier', (d.modifiers && d.modifiers.R3_C_mult != null) ? d.modifiers.R3_C_mult.toFixed(3) : '—', 'ESRS S1-6: Workforce characteristics', (d.modifiers && d.modifiers.R3_C_mult) ? 'ready' : 'gap'],
          ['Elderly', 'Elderly vulnerability', (se.elderly_pct ? se.elderly_pct + '%' : '—'), 'SFDR PAI: Vulnerable populations', se.elderly_pct ? 'ready' : 'gap'],
          ['Community', 'Catchment population', (se.population ? se.population.toLocaleString() : '—'), 'ESRS S2: Community impact', se.population ? 'ready' : 'gap']
        ];
      },
      validity: 'V_socio is computed from the LIHC (Low Income High Cost) energy poverty definition using national statistical office household expenditure data. The R3 modifier amplifies infrastructure risk scores in catchments with high unemployment, elderly concentration, and net outward migration. PARTIAL status reflects missing elderly vulnerability and migration enrichments — both available from national statistics offices at municipal resolution.'
    },
    {
      id: 'report-3', num: '3', title: 'EU Taxonomy Alignment',
      framework: 'Climate Delegated Act · Article 11 Climate Adaptation · Technical Screening Criteria',
      sdgPrimary: { num: 9, label: 'SDG 9', name: 'Industry, Innovation, Infrastructure', color: '#f36d25' },
      sdgSecondary: [
        { num: 13, label: 'SDG 13', color: '#48773c' },
        { num: 12, label: 'SDG 12', color: '#cf8d2a' }
      ],
      legendColor: '#b8863a',
      why: 'The EU Taxonomy defines technical screening criteria for climate change adaptation in infrastructure. This is the lowest-hanging ESG product from the SSI Index — READY for 9 of 10 countries today. The SSI composite score (R_median), 6 components, modifier architecture, and Markov risk outputs provide the quantitative evidence base for Article 11 screening at asset level.',
      sdgRationale: function (d) {
        return 'Target 9.4 calls for upgrading infrastructure to make it sustainable. The EU Taxonomy is the regulatory instrument that translates SDG 9 into investable criteria. By classifying this substation against Article 11 technical screening criteria — using R_median (' + (d.R_median != null ? d.R_median.toFixed(3) : '—') + '), all 6 components, and 5 modifiers — this report provides asset-level Taxonomy alignment that enables sustainable finance reporting.';
      },
      getProfile: function (d) {
        return [
          ['R_median (composite)', d.R_median != null ? d.R_median.toFixed(3) : '—'],
          ['R_base (pre-modifier)', (function () { var v = (d.R_base != null ? d.R_base : d.R_base_median); return v != null ? v.toFixed(3) : '—'; })()],
          ['Modifier Impact', (function () {
            if (d.modifier_pct != null) return d.modifier_pct;
            if (d.modifier_impact != null && d.R_base_median) {
              return (d.modifier_impact / d.R_base_median * 100).toFixed(1);
            }
            return '—';
          })() + '%'],
          ['C (Condition)', (d.components && d.components.C != null) ? d.components.C.toFixed(3) : '—'],
          ['V (Voltage)', (d.components && d.components.V != null) ? d.components.V.toFixed(3) : '—'],
          ['I (Insulation/Climate)', (d.components && d.components.I != null) ? d.components.I.toFixed(3) : '—'],
          ['E (Environment)', (d.components && d.components.E != null) ? d.components.E.toFixed(3) : '—'],
          ['S (Seismic)', (d.components && d.components.S != null) ? d.components.S.toFixed(3) : '—'],
          ['T (Transition)', (d.components && d.components.T != null) ? d.components.T.toFixed(3) : '—']
        ];
      },
      getVariables: function (d) {
        return [
          ['R_median', 'Composite score', d.R_median != null ? d.R_median.toFixed(3) : '—', 'EU Taxonomy Art. 11: Adaptation screening', d.R_median ? 'ready' : 'gap'],
          ['6 Comp.', 'C/V/I/E/S/T', 'All present', 'EU Taxonomy TSC: Physical risk identification', d.components ? 'ready' : 'gap'],
          ['R3-R7', 'Modifier suite', 'All applied', 'ESRS E1: Adaptation measures evidence', d.modifiers ? 'ready' : 'gap'],
          ['Markov', 'Degradation model', (d.markov && d.markov.risk_score != null) ? d.markov.risk_score.toFixed(3) : '—', 'TCFD: Forward-looking risk assessment', d.markov ? 'ready' : 'gap'],
          ['R5', 'Asymmetric CI', d.CI_width != null ? d.CI_width.toFixed(3) : '—', 'ESRS: Uncertainty quantification', d.CI_width ? 'ready' : 'gap']
        ];
      },
      validity: 'Article 11 screening uses the full SSI v4.0.2 scoring engine: 6-component weighted composite (C=0.30, V=0.10, I=0.25, E=0.10, S=0.20, T=0.05), Gaussian copula Monte Carlo (10,000 iterations), and 5 modifiers (R3 social, R4 topology, R5 asymmetric CI, R6a restoration, R7 cyber). The Markov 5-state degradation model provides the forward-looking element. All inputs are from institutional open-source data with citable vintage — meeting CSRD Article 29a limited assurance requirements.'
    },
    {
      id: 'report-4', num: '4', title: 'Energy Transition & DER Stress',
      framework: 'ESRS E1 Transition Plan · TCFD Transition Risk · EU Green Deal Alignment',
      sdgPrimary: { num: 7, label: 'SDG 7', name: 'Affordable and Clean Energy', color: '#fcc30b', dark: true },
      sdgSecondary: [
        { num: 13, label: 'SDG 13', color: '#48773c' },
        { num: 9, label: 'SDG 9', color: '#f36d25' }
      ],
      legendColor: '#e8a838',
      why: 'The energy transition creates infrastructure stress — bidirectional power flows, EV charging load, and intermittent renewable output strain substations designed for unidirectional delivery. This report measures whether grid infrastructure is keeping pace with decarbonisation.',
      sdgRationale: function (d) {
        var tr = d.transition || {};
        var der = tr.DER_ratio;
        return 'Target 7.2 requires substantially increasing the share of renewable energy. This substation has a DER ratio of ' + (der != null ? der.toFixed(3) : '—') + (der > 1 ? ' — local renewable generation exceeds consumption, a transition success that creates operational complexity' : '') + '. The T1_score (' + (tr.T1_score != null ? tr.T1_score.toFixed(3) : '—') + ') measures the stress this places on the substation, providing the empirical feedback loop between SDG 7 ambition and infrastructure reality.';
      },
      getProfile: function (d) {
        var tr = d.transition || {};
        return [
          ['T1 Score (transition stress)', tr.T1_score != null ? tr.T1_score.toFixed(3) : '—'],
          ['DER Ratio', tr.DER_ratio != null ? tr.DER_ratio.toFixed(3) : '—'],
          ['DER Variability', tr.DER_variability != null ? tr.DER_variability.toFixed(3) : '—'],
          ['EV Load Ratio', tr.EV_load_ratio != null ? tr.EV_load_ratio.toFixed(3) : '—'],
          ['T Component Weight', '0.05']
        ];
      },
      getVariables: function (d) {
        var tr = d.transition || {};
        return [
          ['T1', 'Transition stress score', tr.T1_score != null ? tr.T1_score.toFixed(3) : '—', 'ESRS E1: Transition plan assessment', tr.T1_score !== undefined ? 'ready' : 'gap'],
          ['DER_ratio', 'Renewable/load ratio', tr.DER_ratio != null ? tr.DER_ratio.toFixed(3) : '—', 'TCFD Transition: Technology risk', tr.DER_ratio !== undefined ? 'ready' : 'gap'],
          ['DER_var', 'Intermittency', tr.DER_variability != null ? tr.DER_variability.toFixed(3) : '—', 'EU Green Deal: Grid flexibility', tr.DER_variability !== undefined ? 'ready' : 'gap'],
          ['EV_load', 'EV charging ratio', tr.EV_load_ratio != null ? tr.EV_load_ratio.toFixed(3) : '—', 'SDG 7: Clean energy access', tr.EV_load_ratio !== undefined ? 'ready' : 'gap']
        ];
      },
      validity: 'T1_score is the weighted composite of DER_ratio (renewable generation vs. local demand), DER_variability (intermittency), and EV_load_ratio (electric vehicle charging load as fraction of capacity). DER data sourced from national energy regulators and renewable installation registers. DER_ratio > 1.0 indicates net export during peak generation — a marker of successful energy transition with associated infrastructure stress.'
    },
    {
      id: 'report-5', num: '5', title: 'Pollution & Corrosion',
      framework: 'ESRS E2 Pollution · ISO 9223 Corrosion Classification · Environmental Impact',
      sdgPrimary: { num: 11, label: 'SDG 11', name: 'Sustainable Cities and Communities', color: '#f99d26' },
      sdgSecondary: [
        { num: 3, label: 'SDG 3', color: '#4c9f38' },
        { num: 15, label: 'SDG 15', color: '#56c02b' }
      ],
      legendColor: '#6b8e6b',
      why: 'Transformer oil degradation, SF6 leakage, and corrosion-driven failures release pollutants affecting local environments. ESRS E2 requires disclosure of pollution risks. This report assesses the substation\'s corrosion classification under ISO 9223 and the environmental sensitivity of its surroundings.',
      sdgRationale: function (d) {
        var mk = d.markov || {};
        var se = d.socio_economic || {};
        return 'Target 11.6 aims to reduce the adverse environmental impact of cities. The corrosion class (' + (mk.corrosion_class || '—') + ') and E2_local enrichment factor (' + (se.E2_local != null ? se.E2_local.toFixed(2) : '—') + ') track environmental degradation and pollution sensitivity at asset level. Where corrosion is advanced and maintenance deferred, equipment failure risks releasing mineral oil, PCBs (legacy units), and SF6 — directly relevant to urban and peri-urban environmental quality.';
      },
      getProfile: function (d) {
        var mk = d.markov || {};
        var se = d.socio_economic || {};
        return [
          ['Corrosion Class (ISO 9223)', mk.corrosion_class || '—'],
          ['E2 Local Enrichment', se.E2_local != null ? se.E2_local.toFixed(2) : '—'],
          ['E Component Score', (d.components && d.components.E != null) ? d.components.E.toFixed(3) : '—'],
          ['Markov Steady-State', mk.steady_state ? mk.steady_state.map(function (v) { return Math.round(v * 100) + '%'; }).join('/') : '—']
        ];
      },
      getVariables: function (d) {
        var mk = d.markov || {};
        var se = d.socio_economic || {};
        return [
          ['Corrosion', 'ISO 9223 class', mk.corrosion_class || '—', 'ESRS E2: Pollution risk classification', mk.corrosion_class ? 'ready' : 'gap'],
          ['E2_local', 'Environmental sensitivity', se.E2_local != null ? se.E2_local.toFixed(2) : '—', 'ESRS E2: Local environmental impact', se.E2_local ? 'ready' : 'gap'],
          ['E', 'Environment component', (d.components && d.components.E != null) ? d.components.E.toFixed(3) : '—', 'ISO 9223: Atmospheric corrosion', (d.components && d.components.E) ? 'ready' : 'gap']
        ];
      },
      validity: 'Corrosion class follows ISO 9223:2012 atmospheric corrosion classification (C1–CX). Status depends on whether the corrosion class shows real variance across the fleet or uses default values. Full validation requires national environmental agency air quality monitoring overlay at substation coordinates (SO2, NOx, particulate deposition).'
    },
    {
      id: 'report-6', num: '6', title: 'Cybersecurity Exposure',
      framework: 'NIS2 Directive · ENISA Cybersecurity Index · ESRS G1 Governance',
      sdgPrimary: { num: 9, label: 'SDG 9', name: 'Industry, Innovation, Infrastructure', color: '#f36d25' },
      sdgSecondary: [
        { num: 16, label: 'SDG 16', color: '#00689d' }
      ],
      legendColor: '#3a7ca5',
      why: 'The NIS2 Directive mandates cybersecurity risk management for energy operators. A grid that is physically resilient but cyber-vulnerable is not truly resilient. The SSI R7 modifier combines SCADA assessment, communication architecture analysis, and national-level cyber maturity (ENISA/DESI indices) to produce a substation-level digital vulnerability score.',
      sdgRationale: function (d) {
        var mods = d.modifiers || {};
        var gt = d.graph_topology || {};
        return 'Target 9.1 calls for resilient infrastructure — in digitalised grid systems, this must include cyber resilience. The R7 modifier (' + (mods.R7_cyber != null ? mods.R7_cyber.toFixed(3) : '—') + ') assesses digital vulnerability combining SCADA exposure, communication protocol security, and national cyber maturity. SDG 16 (Strong Institutions) also applies: NIS2 compliance is a governance imperative, and the betweenness centrality (' + (gt.BC_percentile != null ? gt.BC_percentile.toFixed(3) : '—') + ') identifies single-point-of-failure risk in the grid topology.';
      },
      getProfile: function (d) {
        var mods = d.modifiers || {};
        var gt = d.graph_topology || {};
        return [
          ['R7 Cyber Modifier', mods.R7_cyber != null ? mods.R7_cyber.toFixed(3) : '—'],
          ['Graph Degree (topology)', gt.degree || '—'],
          ['BC Percentile (centrality)', gt.BC_percentile != null ? gt.BC_percentile.toFixed(3) : '—'],
          ['Is Bridge Node', gt.is_bridge ? 'Yes' : 'No'],
          ['Cluster Coefficient', gt.cluster_coeff != null ? gt.cluster_coeff.toFixed(4) : '—']
        ];
      },
      getVariables: function (d) {
        var mods = d.modifiers || {};
        var gt = d.graph_topology || {};
        return [
          ['R7', 'Cyber modifier', mods.R7_cyber != null ? mods.R7_cyber.toFixed(3) : '—', 'NIS2: Cybersecurity risk management', mods.R7_cyber ? 'ready' : 'gap'],
          ['BC', 'Betweenness centrality', gt.BC_percentile != null ? gt.BC_percentile.toFixed(3) : '—', 'ESRS G1: Governance & topology risk', gt.BC_percentile ? 'ready' : 'gap'],
          ['Degree', 'Graph degree', gt.degree || '—', 'Grid resilience: Connectivity', gt.degree ? 'ready' : 'gap']
        ];
      },
      validity: 'R7_cyber is computed from a weighted combination of: (1) national cyber maturity via ENISA Cybersecurity Index and EU DESI connectivity indicators, (2) graph topology vulnerability (betweenness centrality = single-point-of-failure risk), and (3) SCADA protocol exposure assessment. Substation-level SCADA data is operator-proprietary — the national-level proxy provides a baseline but not asset-specific granularity.'
    }
  ];

  /* ── Component colours and weights (C/V/I/E/S/T fingerprint) ──────────── */
  var COMP_CONFIG = {
    C: { label: 'Condition',   weight: 0.30, color: '#941914' },
    V: { label: 'Voltage',     weight: 0.10, color: '#aa4234' },
    I: { label: 'Insulation',  weight: 0.25, color: '#b8863a' },
    E: { label: 'Environment', weight: 0.10, color: '#5d8563' },
    S: { label: 'Seismic',     weight: 0.20, color: '#3a7ca5' },
    T: { label: 'Transition',  weight: 0.05, color: '#8a7e76' }
  };

  /* ── Markov 4-state diagram config ────────────────────────────────────── */
  var MARKOV_STATES = [
    { label: 'Good',     bg: '#5d8563', fg: '#fff' },
    { label: 'Aged',     bg: '#b8863a', fg: '#fff' },
    { label: 'Degraded', bg: '#aa4234', fg: '#fff' },
    { label: 'Critical', bg: '#941914', fg: '#fff' }
  ];

  /* ── Italy data-sources fallback (used when window.SSI_METADATA.DATA_SOURCES
       is undefined — i.e. country hasn't completed Phase 2b migration yet). ── */
  var ITALY_FALLBACK_SOURCES = [
    ['ERA5 Climate Reanalysis', 'Copernicus CDS', '2024', 'Weekly', 'CC-BY-4.0', 'R1, R3'],
    ['National Seismic Hazard Map', 'National Geological Survey', '2023', 'Multi-year', 'CC0', 'R1, R3'],
    ['Population & Economics', 'National Statistics Office', '2023', 'Annual', 'OGD', 'R2, R3'],
    ['Energy Market Data', 'National TSO', '2023', 'Annual', 'Regulated', 'R2, R4'],
    ['Renewable Installations', 'National DER Registry', '2024', 'Monthly', 'Open', 'R4'],
    ['Air Quality Monitoring', 'National Environmental Agency', '2023', 'Annual', 'CC-BY-4.0', 'R5'],
    ['Cybersecurity Index', 'ENISA', '2024', 'Biennial', 'Open', 'R6'],
    ['DESI Connectivity', 'European Commission', '2024', 'Annual', 'Open', 'R6'],
    ['IEEE C57.91 Thermal Model', 'IEEE', 'Standard', 'N/A', 'Published', 'R1'],
    ['CIGRE TB 761 Markov', 'CIGRE', '2019', 'N/A', 'Published', 'R1, R3'],
    ['ISO 9223 Corrosion', 'ISO', '2012', 'N/A', 'Published', 'R5'],
    ['CMIP6 SSP2-4.5 Projections', 'Copernicus CDS', '—', 'Not ingested', 'CC-BY-4.0', 'R1 (blocked)', true]
  ];

  /* ── Helper: compute 6-axis ESG readiness scores (R1..R6) ─────────────── */
  function computeESGScores(d) {
    var r1 = 0, r2 = 0, r3 = 0, r4 = 0, r5 = 0, r6 = 0;
    var c = d.components || {}, se = d.socio_economic || {}, mk = d.markov || {},
        mods = d.modifiers || {}, tr = d.transition || {}, gt = d.graph_topology || {};

    // R1 Climate
    if (c.I) r1 += 0.25;
    if (c.E) r1 += 0.15;
    if (d.seismic && d.seismic.pga_g) r1 += 0.15;
    if (mk.risk_score) r1 += 0.20;
    if (mk.ettc_years || mk.ETTC_years) r1 += 0.10;
    if (mk.p_crit_20yr !== undefined) { r1 += 0.15; } else { r1 = Math.min(r1 + 0.15, 0.85); }

    // R2 Social
    if (se.V_socio) r2 += 0.20;
    if (se.EP_rate_region) r2 += 0.15;
    if (se.unemployment_rate) r2 += 0.10;
    if (se.gdp_per_capita) r2 += 0.10;
    if (mods.R3_C_mult) r2 += 0.15;
    if (se.elderly_pct) r2 += 0.10;
    if (se.population) r2 += 0.05;

    // R3 Taxonomy
    if (d.R_median) r3 += 0.25;
    if (d.components) r3 += 0.25;
    if (d.modifiers) r3 += 0.20;
    if (d.markov) r3 += 0.20;
    if (d.CI_width) r3 += 0.10;

    // R4 Transition
    if (tr.T1_score !== undefined) r4 += 0.25;
    if (tr.DER_ratio !== undefined) r4 += 0.25;
    if (tr.DER_variability !== undefined) r4 += 0.25;
    if (tr.EV_load_ratio !== undefined) r4 += 0.25;

    // R5 Pollution
    if (mk.corrosion_class) r5 += 0.35;
    if (se.E2_local) r5 += 0.25;
    if (c.E) r5 += 0.20;
    r5 = Math.min(r5, 0.80);

    // R6 Cyber
    if (mods.R7_cyber) r6 += 0.30;
    if (gt.BC_percentile) r6 += 0.25;
    if (gt.degree) r6 += 0.15;
    r6 = Math.min(r6, 0.70);

    return [
      Math.round(r1 * 100) / 100,
      Math.round(r2 * 100) / 100,
      Math.round(r3 * 100) / 100,
      Math.round(r4 * 100) / 100,
      Math.round(r5 * 100) / 100,
      Math.round(r6 * 100) / 100
    ];
  }

  /* ── Helper: filter the country's ESG-source catalogue for a given report
       number (R1..R6). Reads window.SSI_METADATA.ESG_SOURCES (the legacy
       array-of-arrays shape: [name, source, vintage, frequency, license,
       reports_tag, blocked_flag?]). Falls back to a generic Italy default
       when the country hasn't populated it yet — preserves backward
       compatibility during the 31-country rollout.

       NOTE: this is intentionally a DIFFERENT key from DATA_SOURCES (which
       is consumed by data.html in object form: {id, name, freq, status, ...}).
       Keeping the two shapes separate avoids a destructive schema collision.

       Signature changed from (reportNum) → (reportNum, country, data) — only
       reportNum is currently meaningful but the extra params give future
       per-country customisation a clean entry point. ──────────────────── */
  function getReportSources(reportNum /*, country, data */) {
    var meta = window.SSI_METADATA || {};
    var sources = (Array.isArray(meta.ESG_SOURCES) && isLegacyShape(meta.ESG_SOURCES))
                  ? meta.ESG_SOURCES
                  : ITALY_FALLBACK_SOURCES;
    var tag = 'R' + reportNum;
    var filtered = sources.filter(function (row) {
      var reports = row[5] || '';
      return reports.indexOf(tag) >= 0;
    });
    if (filtered.length === 0) {
      return '<div style="font-size:12px;color:var(--warm-grey);padding:4px 0;">No dedicated data sources for this report.</div>';
    }
    return filtered.map(function (row) {
      var isBlocked = row[6];
      var nameStyle = isBlocked ? 'color:var(--terracotta);' : 'color:var(--ink);';
      var subStyle = isBlocked ? 'color:var(--terracotta);' : 'color:var(--warm-grey);';
      return '<div style="display:flex;justify-content:space-between;align-items:baseline;padding:7px 0;border-bottom:1px solid rgba(44,36,32,0.05);font-size:12px;">' +
        '<div style="flex:1;min-width:0;">' +
          '<div style="' + nameStyle + 'font-weight:500;">' + row[0] + '</div>' +
          '<div style="' + subStyle + 'font-size:11px;">' + row[1] + '</div>' +
        '</div>' +
        '<div style="text-align:right;flex-shrink:0;margin-left:12px;">' +
          '<span class="source-tag"><span class="vintage">' + row[2] + '</span> ' + row[3] + '</span>' +
        '</div>' +
      '</div>';
    }).join('');
  }

  function isLegacyShape(arr) {
    // Legacy row form: [name, source, vintage, frequency, license, reports_tag, blocked?]
    // Distinguish from the richer DATA_SOURCES (object form, used elsewhere
    // in the codebase for data.html) which has {id, name, freq, status, ...}.
    return arr.length > 0 && Array.isArray(arr[0]);
  }

  /* ── Module-scope chart refs so destroy() can re-render on second pass ── */
  var radarChart = null;
  var componentChart = null;

  /* ══════════════════════════════════════════════════════════════════════
     SECTION REGISTRATIONS — each receives ctx = {data, config, country, page, doc}
     where ctx.data is the FULL normalized ssi-data.json. Each section picks
     the monthly substation itself via CountryRenderer.pickMonthlySubstation
     so all sections agree on the same `s` (deterministic monthly seed).
     ══════════════════════════════════════════════════════════════════════ */

  /* ── 0. <title> tag ──────────────────────────────────────────────────── */
  CR.register('esg-report', 'page-title', function (ctx) {
    var s = CR.pickMonthlySubstation(ctx.data);
    if (!s) return;
    document.title = 'SSI Index — ESG Report · ' + displayName(s) + ' (' + (s.substation_id || '') + ')';
  });

  /* ── 1. KPI grid (substation identity + headline scores) ─────────────── */
  CR.register('esg-report', 'kpi-grid', function (ctx) {
    var s = CR.pickMonthlySubstation(ctx.data);
    if (!s) return;
    var band = bandClass(s.classification);
    var bandLabel = s.classification || 'Low';
    H.setHTML('kpiGrid',
      '<div class="kpi-card">' +
        '<div class="kpi-label">Substation</div>' +
        '<div class="kpi-value" style="font-size:22px;">' + displayName(s) + '</div>' +
        '<div class="kpi-sub">' + (s.substation_id || '') + ' · ' + (s.province || '') + ', ' + (s.region || '') + '</div>' +
      '</div>' +
      '<div class="kpi-card">' +
        '<div class="kpi-label">SSI Score (R<sub>median</sub>)</div>' +
        '<div class="kpi-value" style="color:var(--band-' + band + ');">' + (s.R_median != null ? s.R_median.toFixed(3) : '—') + '</div>' +
        '<div class="kpi-sub"><span class="band-badge ' + band + '"><span class="band-dot ' + band + '"></span> ' + bandLabel + ' Risk</span> &nbsp; ' + (s.fleet_percentile ? (s.fleet_percentile * 100).toFixed(1) + 'th percentile' : '') + '</div>' +
      '</div>' +
      '<div class="kpi-card">' +
        '<div class="kpi-label">Voltage Class</div>' +
        '<div class="kpi-value">' + (s.voltage_kv != null ? s.voltage_kv : '—') + ' <span style="font-size:16px;font-weight:400;">kV</span></div>' +
        '<div class="kpi-sub">' + (Safe.voltageClass(s.voltage_kv) === 'distribution-tier' ? 'distribution-tier' : 'High-voltage transmission') + '</div>' +
      '</div>' +
      '<div class="kpi-card">' +
        '<div class="kpi-label">Confidence Interval</div>' +
        '<div class="kpi-value" style="font-size:22px;">' + (s.R_P5 != null ? s.R_P5.toFixed(3) : '—') + ' – ' + (s.R_P95 != null ? s.R_P95.toFixed(3) : '—') + '</div>' +
        '<div class="kpi-sub">P5–P95 · CI width ' + (s.CI_width != null ? s.CI_width.toFixed(3) : '—') + ' · ' + (s.confidence_tier || '') + ' confidence</div>' +
      '</div>' +
      '<div class="kpi-card">' +
        '<div class="kpi-label">Markov ETTC</div>' +
        '<div class="kpi-value">' + (((s.markov && (s.markov.ettc_years || s.markov.ETTC_years)) || '—')) + ' <span style="font-size:16px;font-weight:400;">yr</span></div>' +
        '<div class="kpi-sub">Expected time to criticality</div>' +
      '</div>' +
      '<div class="kpi-card">' +
        '<div class="kpi-label">DER Penetration</div>' +
        '<div class="kpi-value">' + ((s.transition && s.transition.DER_ratio != null) ? s.transition.DER_ratio.toFixed(2) : ((s.transition && s.transition.T1_score != null) ? s.transition.T1_score.toFixed(3) : '—')) + '</div>' +
        '<div class="kpi-sub">' + ((s.transition && s.transition.DER_ratio > 1) ? 'DER ratio — renewable generation exceeds local load' : 'T1 transition stress score') + '</div>' +
      '</div>'
    );
  });

  /* ── 2. Component bar (C/V/I/E/S/T weighted fingerprint + Chart.js) ──── */
  CR.register('esg-report', 'component-bar', function (ctx) {
    var s = CR.pickMonthlySubstation(ctx.data);
    if (!s || !s.components) return;
    var comps = s.components;
    var barEl = document.getElementById('componentBar');
    var legendEl = document.getElementById('componentLegend');
    if (!barEl || !legendEl) return;

    var totalWeighted = 0;
    var weighted = {};
    Object.keys(COMP_CONFIG).forEach(function (k) {
      weighted[k] = (comps[k] || 0) * COMP_CONFIG[k].weight;
      totalWeighted += weighted[k];
    });

    var barHTML = '';
    var legendHTML = '';
    Object.keys(COMP_CONFIG).forEach(function (k) {
      var cfg = COMP_CONFIG[k];
      var pct = totalWeighted > 0 ? (weighted[k] / totalWeighted * 100) : (cfg.weight * 100);
      barHTML += '<div style="width:' + pct.toFixed(1) + '%;background:' + cfg.color + ';" title="' + cfg.label + ': ' + (comps[k] != null ? comps[k].toFixed(3) : '—') + ' × ' + cfg.weight + ' = ' + (weighted[k] != null ? weighted[k].toFixed(4) : '—') + '">' + k + '</div>';
      legendHTML += '<div class="component-legend-item">' +
        '<div class="component-legend-dot" style="background:' + cfg.color + ';"></div>' +
        '<span>' + cfg.label + '</span>' +
        '<span class="component-legend-score">' + (comps[k] != null ? comps[k].toFixed(3) : '—') + '</span>' +
        '<span class="component-legend-weight">×' + cfg.weight + '</span>' +
      '</div>';
    });
    barEl.innerHTML = barHTML;
    legendEl.innerHTML = legendHTML;

    var canvas = document.getElementById('componentChart');
    if (!canvas || typeof Chart === 'undefined') return;
    var ctx2 = canvas.getContext('2d');
    if (componentChart) componentChart.destroy();
    var keys = Object.keys(COMP_CONFIG);
    componentChart = new Chart(ctx2, {
      type: 'bar',
      data: {
        labels: keys.map(function (k) { return COMP_CONFIG[k].label; }),
        datasets: [{
          label: 'Component Score',
          data: keys.map(function (k) { return comps[k] || 0; }),
          backgroundColor: keys.map(function (k) { return COMP_CONFIG[k].color + 'cc'; }),
          borderColor: keys.map(function (k) { return COMP_CONFIG[k].color; }),
          borderWidth: 1, borderRadius: 4
        }]
      },
      options: {
        indexAxis: 'y', responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#2c2420',
            titleFont: { family: "'DM Sans', sans-serif", size: 12 },
            bodyFont: { family: "'DM Sans', sans-serif", size: 12 },
            cornerRadius: 6,
            callbacks: {
              label: function (c) {
                var k = keys[c.dataIndex];
                return c.raw.toFixed(3) + ' × ' + COMP_CONFIG[k].weight + ' weight';
              }
            }
          }
        },
        scales: {
          x: { min: 0, max: 1, grid: { color: 'rgba(44,36,32,0.06)' }, ticks: { font: { family: "'DM Sans'" }, color: '#b5aca5' } },
          y: { grid: { display: false }, ticks: { font: { family: "'DM Sans'", weight: '600', size: 12 }, color: '#2c2420' } }
        }
      }
    });
  });

  /* ── 3. Markov steady-state diagram (KPI cards handled separately by the
        `markov-kpis` section already registered in country-renderer.js) ── */
  CR.register('esg-report', 'markov-diagram', function (ctx) {
    var s = CR.pickMonthlySubstation(ctx.data);
    if (!s) return;
    var mk = s.markov || {};
    var ss = mk.steady_state_array || mk.steady_state || [0, 0, 0, 0];
    if (!Array.isArray(ss)) ss = [0, 0, 0, 0];
    var diagramEl = document.getElementById('markovDiagram');
    if (!diagramEl) return;
    var html = '';
    ss.forEach(function (val, i) {
      if (i > 0) html += '<div class="markov-arrow">&#9654;</div>';
      var pct = Math.round(val * 100);
      var state = MARKOV_STATES[i] || MARKOV_STATES[MARKOV_STATES.length - 1];
      html += '<div class="markov-state" style="background:' + state.bg + ';color:' + state.fg + ';flex:' + Math.max(pct, 8) + ';">' +
        '<div class="markov-state-label">' + state.label + '</div>' +
        '<div class="markov-state-pct">' + pct + '%</div>' +
        '<div class="markov-state-sub">π' + (i + 1) + ' = ' + (val != null ? val.toFixed(3) : '—') + '</div>' +
      '</div>';
    });
    diagramEl.innerHTML = html;
  });

  /* ── 4. ESG radar chart + legend ─────────────────────────────────────── */
  CR.register('esg-report', 'esg-radar', function (ctx) {
    var s = CR.pickMonthlySubstation(ctx.data);
    if (!s) return;
    var scores = computeESGScores(s);
    var labels = [
      ['R1 Climate', 'Physical Risk'], ['R2 Grid Equity', '& Social'],
      ['R3 EU Taxonomy', 'Alignment'], ['R4 Energy', 'Transition'],
      ['R5 Pollution', '& Corrosion'], ['R6 Cybersecurity', 'Exposure']
    ];
    var colors = ESG_REPORTS.map(function (r) { return r.legendColor; });

    var canvas = document.getElementById('esgRadar');
    if (canvas && typeof Chart !== 'undefined') {
      var ctx2 = canvas.getContext('2d');
      if (radarChart) radarChart.destroy();
      radarChart = new Chart(ctx2, {
        type: 'radar',
        data: {
          labels: labels,
          datasets: [{
            label: 'ESG Readiness', data: scores,
            backgroundColor: 'rgba(148,25,20,0.08)', borderColor: '#941914', borderWidth: 2,
            pointBackgroundColor: colors, pointBorderColor: '#fff', pointBorderWidth: 2,
            pointRadius: 6, pointHoverRadius: 8, fill: true
          }]
        },
        options: {
          responsive: true, maintainAspectRatio: true,
          layout: { padding: { left: 30, right: 10 } },
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: '#2c2420',
              titleFont: { family: "'DM Sans', sans-serif", size: 13, weight: '600' },
              bodyFont: { family: "'DM Sans', sans-serif", size: 12 },
              cornerRadius: 6, padding: 10,
              callbacks: {
                label: function (c) {
                  var pct = Math.round(c.raw * 100);
                  var status = c.raw >= 0.80 ? 'READY' : c.raw >= 0.40 ? 'PARTIAL' : 'GAP';
                  return pct + '% readiness · ' + status;
                }
              }
            }
          },
          scales: {
            r: {
              min: 0, max: 1,
              ticks: { stepSize: 0.25, font: { family: "'DM Sans'", size: 10 }, color: '#b5aca5', backdropColor: 'rgba(255,255,255,0.8)', callback: function (v) { return Math.round(v * 100) + '%'; } },
              grid: { color: 'rgba(44,36,32,0.06)' },
              angleLines: { color: 'rgba(44,36,32,0.08)' },
              pointLabels: { font: { family: "'DM Sans'", size: 10, weight: '600' }, color: '#2c2420', padding: 30 }
            }
          }
        }
      });
    }

    var sdgHTML = ESG_REPORTS.map(function (r, i) {
      var allSdgs = [r.sdgPrimary].concat(r.sdgSecondary);
      var badges = allSdgs.map(function (sg) { return '<span class="sdg-badge" style="background:' + sg.color + ';' + (sg.dark ? 'color:#333;' : '') + '">' + sg.label + '</span>'; }).join(' ');
      var readiness = readinessLabel(scores[i]);
      return '<div class="radar-legend-item">' +
        '<div class="radar-legend-dot" style="background:' + r.legendColor + ';"></div>' +
        '<div>' +
          '<div class="radar-legend-label">R' + r.num + ' · ' + r.title + ' <span class="readiness-pill ' + readiness + '" style="margin-left:6px;">' + readinessText(scores[i]) + '</span></div>' +
          '<div class="radar-legend-sub">' + r.sdgPrimary.label + ' ' + r.sdgPrimary.name + r.sdgSecondary.map(function (sg) { return ' · ' + sg.label; }).join('') + '</div>' +
          '<div style="margin-top:4px;">' + badges + '</div>' +
        '</div>' +
      '</div>';
    }).join('');
    H.setHTML('radarLegend', sdgHTML);
  });

  /* ── 5. 6 individual ESG reports (large templated HTML) ───────────────── */
  CR.register('esg-report', 'esg-reports', function (ctx) {
    var s = CR.pickMonthlySubstation(ctx.data);
    if (!s) return;
    var scores = computeESGScores(s);
    var container = document.getElementById('esgReportsContainer');
    if (!container) return;
    container.innerHTML = ESG_REPORTS.map(function (r, i) {
      var readiness = readinessLabel(scores[i]);
      var profile = r.getProfile(s);
      var variables = r.getVariables(s);
      var allSdgs = [r.sdgPrimary].concat(r.sdgSecondary);
      var badges = allSdgs.map(function (sg) { return '<span class="sdg-badge' + (sg === r.sdgPrimary ? ' primary' : '') + '" style="background:' + sg.color + ';' + (sg.dark ? 'color:#333;' : '') + '">' + sg.label + '</span>'; }).join(' ');

      var profileRows = profile.map(function (row) {
        var label = row[0], value = row[1];
        var isGap = typeof value === 'string' && value.indexOf('||') >= 0;
        var cleanVal = isGap ? value.replace(/\|\|/g, '') : value;
        return '<tr><td style="color:var(--warm-grey);">' + label + '</td><td class="num"' + (isGap ? ' style="color:var(--terracotta);"' : '') + '><strong>' + cleanVal + '</strong></td></tr>';
      }).join('');

      var varRows = variables.map(function (row) {
        var tag = row[0], name = row[1], val = row[2], esrReq = row[3], status = row[4];
        var pillClass = status === 'ready' ? 'ready' : status === 'partial' ? 'partial' : 'gap';
        var pillText = status === 'ready' ? 'READY' : status === 'partial' ? 'DEFAULT' : 'GAP';
        return '<tr>' +
          '<td><span class="var-tag">' + tag + '</span> ' + name + '</td>' +
          '<td class="num"' + (status === 'gap' ? ' style="color:var(--terracotta);"' : '') + '>' + val + '</td>' +
          '<td>' + esrReq + '</td>' +
          '<td><span class="readiness-pill ' + pillClass + '">' + pillText + '</span></td>' +
        '</tr>';
      }).join('');

      return '' +
      '<div class="section-block" id="' + r.id + '">' +
        '<div class="section-header">' +
          '<span class="section-number">' + r.num + '</span>' +
          '<div class="section-title-group">' +
            '<h2>' + r.title + '</h2>' +
            '<div class="section-sub">' + r.framework + '</div>' +
          '</div>' +
          '<span class="readiness-pill ' + readiness + '">' + readinessText(scores[i]) + '</span>' +
        '</div>' +
        '<div class="why-box">' +
          '<div class="why-label">Why this report exists</div>' +
          '<p>' + r.why + '</p>' +
        '</div>' +
        '<div class="grid-2" style="margin-bottom:20px;">' +
          '<div class="card esg-report-card">' +
            '<div class="report-index">SDG Alignment</div>' +
            '<h3 style="font-family:\'Playfair Display\',serif; margin-bottom:10px;">' + r.sdgPrimary.label + ' — ' + r.sdgPrimary.name + ' <span style="font-size:12px;color:var(--warm-grey);">(primary)</span></h3>' +
            '<p style="font-size:13px;">' + r.sdgRationale(s) + '</p>' +
            '<div style="margin-top:8px;">' + badges + '</div>' +
          '</div>' +
          '<div class="card">' +
            '<h3 style="font-family:\'DM Sans\',sans-serif; font-weight:600; margin-bottom:12px;">Substation Profile</h3>' +
            '<table class="data-table">' + profileRows + '</table>' +
          '</div>' +
        '</div>' +
        '<div class="card" style="margin-bottom:20px;">' +
          '<div class="card-header"><h3>SSI Variables Feeding This Report</h3></div>' +
          '<table class="data-table">' +
            '<thead><tr><th>SSI Variable</th><th>Value</th><th>ESG Disclosure Requirement</th><th>Status</th></tr></thead>' +
            '<tbody>' + varRows + '</tbody>' +
          '</table>' +
        '</div>' +
        '<div class="grid-2">' +
          '<div class="card">' +
            '<div class="card-header"><h3>Data Sources & Vintage</h3></div>' +
            getReportSources(r.num, ctx.country, s) +
          '</div>' +
          '<div class="method-box">' +
            '<div class="method-label">Technical Validity</div>' +
            '<p>' + r.validity + '</p>' +
          '</div>' +
        '</div>' +
      '</div>';
    }).join('');
  });

  /* ── 6. Audit trail table ────────────────────────────────────────────── */
  CR.register('esg-report', 'audit-trail', function (ctx) {
    var s = CR.pickMonthlySubstation(ctx.data);
    if (!s) return;
    var mods = s.modifiers || {};
    var modStr = Object.keys(mods).map(function (k) { return k.replace('_', ' ') + ': ' + (mods[k] != null ? mods[k].toFixed(3) : '—'); }).join(', ');
    var rows = [
      ['Scoring Engine', 'SSI Index v4.0.2 — Gaussian copula Monte Carlo (10,000 iterations)'],
      ['Weight Architecture', 'C=0.30, V=0.10, I=0.25, E=0.10, S=0.20, T=0.05'],
      ['Modifiers Applied', modStr || '—'],
      ['Degradation Model', 'Markov 5-state, CIGRE TB 761 calibration'],
      ['Thermal Model', 'IEEE C57.91 transformer loading curves'],
      ['Report Date', '17 March 2026'],
      ['Reporting Period', 'Calendar year 2025'],
      ['Refresh Cadence', 'Annual (data ingestion → scoring engine → display)'],
      ['Substation', displayName(s) + ' (' + (s.substation_id || '') + ')'],
      ['Data Assurance Level', 'All inputs from institutional open-source with citable vintage']
    ];
    H.setHTML('auditTrailBody', rows.map(function (row) { return '<tr><td>' + row[0] + '</td><td>' + row[1] + '</td></tr>'; }).join(''));
  });

  /* ── 7. Page footer ──────────────────────────────────────────────────── */
  CR.register('esg-report', 'esg-footer', function (ctx) {
    H.setHTML('footerContainer',
      '<div>SSI Index v4.0.2 · Ikenga Enhanced Infrastructure Intelligence · Annual ESG Disclosure</div>' +
      '<div>Report generated 21 May 2026 · All data sources are open-access institutional</div>'
    );
  });

})();
