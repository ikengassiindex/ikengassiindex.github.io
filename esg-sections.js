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
          // IRI display wired to canonical fields (Phase A-ESG audit, 21 Jul 2026):
          //   I1/I2/I3 → climate_trajectory.I{1,2,3}_trajectory (ERA5-derived per-metric projections)
          //   I5 → components.I (I-component aggregate; no standalone thermal-stress scalar
          //        currently emitted at substation resolution — flagged 'partial' per Convention #56
          //        visibly-honest degradation until pipeline adds explicit I5_iri emission).
          //   Values ≥ 1.0 indicate worsening projected exposure; < 1.0 indicates improving.
          ['I1', 'Snow/Ice IRI', (d.climate_trajectory && d.climate_trajectory.I1_trajectory != null) ? d.climate_trajectory.I1_trajectory.toFixed(3) : '—', 'ESRS E1-9: Financial effects from physical risks', (d.climate_trajectory && d.climate_trajectory.I1_trajectory != null) ? 'ready' : 'gap'],
          ['I2', 'Tree-fall IRI', (d.climate_trajectory && d.climate_trajectory.I2_trajectory != null) ? d.climate_trajectory.I2_trajectory.toFixed(3) : '—', 'TCFD Strategy (b): Physical risk impact', (d.climate_trajectory && d.climate_trajectory.I2_trajectory != null) ? 'ready' : 'gap'],
          ['I3', 'Heat-wave IRI', (d.climate_trajectory && d.climate_trajectory.I3_trajectory != null) ? d.climate_trajectory.I3_trajectory.toFixed(3) : '—', 'EU Taxonomy Annex A: Heat stress', (d.climate_trajectory && d.climate_trajectory.I3_trajectory != null) ? 'ready' : 'gap'],
          ['I5', 'Thermal stress (I aggregate)', (d.components && d.components.I != null) ? d.components.I.toFixed(3) : '—', 'ESRS E1-4: Climate mitigation targets', (d.components && d.components.I != null) ? 'partial' : 'gap'],
          ['R2', 'Climate trajectory', (d.markov && d.markov.p_crit_20yr !== undefined ? (d.markov.p_crit_20yr * 100).toFixed(1) + '% (20yr)' : 'N/A'), 'TCFD Strategy (c): Scenario analysis', (d.markov && d.markov.p_crit_20yr !== undefined) ? 'ready' : 'gap'],
          ['R6b', 'Seismic PGA', ((d.seismic && d.seismic.pga_g) || '—') + 'g', 'EU Taxonomy Annex A: Geophysical hazards', (d.seismic && d.seismic.pga_g) ? 'ready' : 'gap'],
          ['Markov', 'p_critical_10yr', (d.markov && d.markov.p_critical_20yr !== undefined ? (d.markov.p_critical_20yr * 100).toFixed(1) + '%' : '—'), 'TCFD Risk Management: Risk identification', d.markov ? 'ready' : 'gap'],
          ['Markov', 'p_critical_20yr', (d.markov && d.markov.p_critical_20yr !== undefined ? (d.markov.p_critical_20yr * 100).toFixed(1) + '%' : '—'), 'ESRS E1-9: Time horizons', (d.markov && d.markov.p_critical_20yr === 0) ? 'partial' : 'ready']
        ];
      },
      validity: 'IRI metrics are computed from ERA5 reanalysis (31 km, hourly, 1940–present) using IEEE C57.91 thermal loading curves. Markov 5-state degradation is calibrated from CIGRE Technical Brochure 761 (2019) condition assessment data. Forward-looking projections use the CMIP6 SSP2-4.5 5-model ensemble (ACCESS-CM2, CNRM-CM6-1, EC-Earth3, GFDL-ESM4, MRI-ESM2-0), baseline 2000–2020 vs future 2030–2050, feeding the substation-level climate_trajectory (I1/I2/I3) fields for 32 of 39 countries. Any PARTIAL status now reflects country-specific gaps: 7 Wave 2-3 countries (Australia, Chile, Colombia, Costa Rica, Iceland, Ireland, Israel) await the next L2 climate pass; 8 Wave 4 countries emit fleet-uniform trajectories pending the per-substation bilinear interpolation regression fix (methodology follow-on, sister to R3_C_mult uniformity). All other inputs are production-grade with institutional provenance.'
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
      validity: 'V_socio is computed from the LIHC (Low Income High Cost) energy poverty definition using national statistical office household expenditure data. The R3 modifier amplifies infrastructure risk scores in catchments with high unemployment, elderly concentration, and net outward migration. Coverage status (21 July 2026 audit): V_socio + EP_rate + gdp_per_capita + unemployment_rate are populated for 32/39 countries, but 8 large countries (Italy, Japan, Portugal, Spain, Sweden, Germany, France, US) emit fleet-uniform national aggregates instead of per-substation LAU-2/NUTS-3 values — pending the systemic Wave 4 per-substation interpolation regression fix (sister to R3_C_mult + CMIP6 climate_trajectory). (Task #452 already closed this gap for migration_score specifically via per-substation Niva 2023 raster enrichment; the remaining V_socio / EP_rate / GDP / unemployment fields await Task #450 SYSTEMIC scope.) Catchment population is now populated for all 39/39 countries via the GHSL Population Grid (EC JRC / Copernicus Emergency Management Service, R2023A epoch E2025, Mollweide equal-area) computing 5 km per-substation zonal sums — Task #451 landed 23 July 2026, replacing a legacy synthetic generator with a real GHSL spatial-join pipeline (795k-substation cohort; 0.17% receive Convention #56 visibly-honest None fallbacks for remote/offshore points where the raster has NoData — concentrated in US Aleutians+Pacific, Canada Arctic, Australia outback, Nordic fjords). Migration_score is now populated for all 39/39 countries via the Niva et al. 2023 gridded net-migration dataset (Aalto University / Wittgenstein Centre, published Nature Human Behaviour 7:2023-2037, DOI 10.1038/s41562-023-01689-4, dataset DOI 10.5281/zenodo.7997134, CC BY 4.0 licence) using the 20-yr sum raster 2000-2019 at 5 arc-min (~10 km) resolution — Task #452 landed 23 July 2026, closing the R2 defect via NARROW-scope enrichment (fill Nones) plus fleet-uniform override that retired the 0.5 national scalar fallback of 8 Wave 4 majors (France, Germany, US, Italy, Spain, Portugal, Sweden, Japan, Australia partial, Austria partial) with real per-substation Niva-derived values in [0, 1] range via tanh(x/200) mapping. Genuine pre-Task-#452 per-substation distributions (Norway, Denmark, Lithuania, Ireland, Turkey, Mexico, Greece, New Zealand, Poland partial) are preserved untouched — their semantic-drift issues (e.g. Mexico [-5, +8] percent-scale, Denmark tiny [-0.02, +0.04] scale) are deferred to Task #450 SYSTEMIC scope. Cohort-wide 97.13% real Niva values written + 0.17% Convention #56 visibly-honest None + 2.70% preserved distributions untouched. The remaining 4 countries with major partial-coverage gaps from failed spatial joins (Luxembourg 12% populated / Slovenia 16% / Colombia 51% / Lithuania 50%) are now closed via Task #453 (23 July 2026) using per-substation polygon spatial-join against Eurostat GISCO NUTS-3 2024 shapefile (European Commission / Eurostat, EPSG:4326, annual vintage, open-license attribution-required — for LU/SI/LT) plus GADM 4.1 admin1 shapefile for Colombia (UC Davis geodata.ucdavis.edu/gadm, peer-reviewed academic-open-license derivative of DANE Marco Geoestadístico Nacional — chosen as documented-proxy after DANE geoportal empirically requires form-based interactive download). Task #453 empirical closure: 6,967 v43 substations enriched across LU/SI/LT/CO (LU 634/634 = 100% · SI 1,571/1,574 = 99.8% · LT 4,396/4,396 = 100% · CO 366/366 = 100%; 3 Convention #56 fallback total = 0.04% cohort-wide; 100% preservation of Task #451 catchment_population + Task #452 migration_score audit-trail markers via merge-not-replace BINDING contract). Each Task #453 enriched substation carries per-region gdp_per_capita + unemployment_rate + EP_rate_region + elderly_pct + computed V_socio (via mirrored 0.45·ep_norm + 0.35·gdp_norm + 0.20·elderly_norm formula from socioeconomic.py:511-517 canonical). Task #453 is the ADMIN structural variant within REPORTS_FRAMING_KB.md §8bis Discipline #47 spatial-enrichment family (STOCK = Task #451 GHSL zonal-sum, FLOW = Task #452 Niva point-sampling, ADMIN = Task #453 polygon spatial-join). Discovery motivating Task #453 also codified METHODOLOGY_DISCIPLINES.md §5septies (empirical OSM tag density is per-country) as candidate architectural discipline — Poland + Luxembourg + Slovenia + Colombia + Lithuania empirically ALL show 0.0% populated ref:nuts:3 / addr:department tag rates at country scale, retiring the connector-tag-extraction path as load-bearing for admin-code derivation. Task #454 SYSTEMIC (24 July 2026) extended the Task #453 polygon utility to 11 additional countries with matching v43-at-partial-coverage pattern — 9 EU countries (Belgium + Czechia + Denmark + Estonia + Finland + Ireland + Latvia + Netherlands + Poland) via the same Eurostat GISCO NUTS-3 2024 shapefile already loaded for Task #453, plus 2 non-EU countries via GADM 4.1 admin1 shapefiles (Switzerland cantons + Canada provinces; same UC Davis academic-open-license documented-proxy pattern used for Task #453 Colombia). Two utility refinements landed during Task #454 execution to accommodate new failure modes surfaced empirically: (a) a 3-case skip-logic decision tree with new case-b (province populated by earlier connector pass but socio_economic gap unfilled — Canada case; utility bypasses polygon join and uses the existing province directly as CSV lookup key); (b) Switzerland csv_lookup_aliases with 5 entries mapping GADM English/French canton names (Lucerne, Sankt Gallen etc.) to CSV German canonical forms (Luzern, St. Gallen). Task #454 SYSTEMIC empirical closure: 52,043 v43 substations enriched across 11 new countries (BE 5,428 + CZ 7,825 + DK 2,364 + EE 1,178 + FI 135 + IE 282 + LV 3,425 + NL 3,807 + PL 25,509 + CH 865 + CA 1,227) plus Task #453 4-country idempotent no-op preservation of 6,967 subs = 59,041/59,077 = 99.94% cohort-wide coverage across 15-country combined Task #453+#454 cohort with 65 Convention #56 out-of-polygon fallback (0.11%) and 100% Task #451/#452 marker preservation via merge-not-replace BINDING contract. Wall-clock 15s cumulative (Poland alone 1.3s = ~19,600 subs/sec). Post-Task-#454 Discipline #47 ADMIN variant instance count is 15 (Task #453 4 + Task #454 11), and Convention #78 §5septies OSM-tag-density empirical instance count is 16 (Poland P21 baseline + Task #453 cohort 4 + Task #454 cohort 11 — well above Convention #76 BINDING promotion threshold of 5-10 empirical instances). All inputs sourced from institutional statistical offices with citable vintage — meeting CSRD Article 29a limited assurance requirements for the 32-country cohort where fields are per-substation, plus Task #453+#454 15-country cohort now closed at Grid Equity axis via polygon spatial-join.'
    },
    {
      id: 'report-3', num: '3', title: 'Infrastructure Resilience [Re composite home]',
      framework: 'FC v3 §14 · SSI v4.2 Re composite (canonical) · EU Taxonomy Art. 11 (mapped)',
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
      id: 'report-4', num: '4', title: 'Pollution & Corrosion',
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
      id: 'report-5', num: '5', title: 'Energy Transition & DER Stress',
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
    },
    {
      id: 'report-7', num: '7', title: 'SFDR PAI Infrastructure Disclosure',
      framework: 'SFDR Article 4 · PAI Table 1 · Delegated Reg (EU) 2022/1288 · FC v3 §14 subsection 13.7',
      sdgPrimary: { num: 12, label: 'SDG 12', name: 'Responsible Consumption and Production', color: '#cf8d2a' },
      sdgSecondary: [
        { num: 9, label: 'SDG 9', color: '#f36d25' },
        { num: 13, label: 'SDG 13', color: '#48773c' }
      ],
      legendColor: '#a06938',
      why: 'The SFDR (Sustainable Finance Disclosure Regulation) mandates that financial market participants disclose Principal Adverse Impact (PAI) indicators for infrastructure investments. PAI Table 1 requires quantitative assessment of physical + governance risk at asset level for Article 8/9 fund classification. The SSI v4.2 Re composite (resilience metric per FC v3 §14 subsection 13.7) provides the canonical proxy for Infrastructure PAI: it integrates 6-axis physical risk (C/V/I/E/S/T), 6-modifier degradation chain (R3/R4/R6c/R6d/R6e/R8/R9/R10), and Markov forward-looking trajectory into a single normalised value directly consumable by SFDR reporting.',
      sdgRationale: function (d) {
        var reNorm = d.Re_norm;
        var reRaw = d.Re_raw;
        return 'Target 12.6 encourages companies to adopt sustainable practices and integrate sustainability information into their reporting cycle. SFDR is the EU regulatory instrument that operationalises this at fund level for infrastructure investors. This substation carries an Re_norm (normalised resilience composite) of ' + (reNorm != null ? reNorm.toFixed(3) : '—') + ' and Re_raw of ' + (reRaw != null ? reRaw.toFixed(3) : '—') + ', providing the empirical basis for PAI Table 1 Infrastructure indicator disclosure under Delegated Reg (EU) 2022/1288.';
      },
      getProfile: function (d) {
        var mods = d.modifiers || {};
        return [
          ['Re_norm (SFDR PAI composite)', d.Re_norm != null ? d.Re_norm.toFixed(3) : '—'],
          ['Re_raw (pre-normalisation)', d.Re_raw != null ? d.Re_raw.toFixed(3) : '—'],
          ['R6c Flood modifier', mods.R6c_flood != null ? mods.R6c_flood.toFixed(3) : '—'],
          ['R6d Wildfire modifier', mods.R6d_wildfire != null ? mods.R6d_wildfire.toFixed(3) : '—'],
          ['R6e Winter storm modifier', mods.R6e_winter != null ? mods.R6e_winter.toFixed(3) : '—'],
          ['R8 Adaptation modifier', mods.R8_adapt != null ? mods.R8_adapt.toFixed(3) : '—'],
          ['R9 Compound event modifier', mods.R9_compound != null ? mods.R9_compound.toFixed(3) : '—'],
          ['R10 Just-transition modifier', mods.R10_just != null ? mods.R10_just.toFixed(3) : '—']
        ];
      },
      getVariables: function (d) {
        var mods = d.modifiers || {};
        return [
          ['Re_norm', 'SFDR PAI composite (normalised)', d.Re_norm != null ? d.Re_norm.toFixed(3) : '—', 'SFDR Art. 4 · PAI Table 1 Infrastructure', d.Re_norm != null && d.Re_norm !== 0.0 ? 'ready' : 'gap'],
          ['Re_raw', 'Pre-normalisation resilience', d.Re_raw != null ? d.Re_raw.toFixed(3) : '—', 'FC v3 §14 subsection 13.7', d.Re_raw != null && d.Re_raw !== 1.0 ? 'ready' : 'gap'],
          ['R6c', 'Flood modifier', mods.R6c_flood != null ? mods.R6c_flood.toFixed(3) : '—', 'SFDR PAI: Physical acute hazards', mods.R6c_flood != null ? 'ready' : 'gap'],
          ['R6d', 'Wildfire modifier', mods.R6d_wildfire != null ? mods.R6d_wildfire.toFixed(3) : '—', 'SFDR PAI: Physical acute hazards', mods.R6d_wildfire != null ? 'ready' : 'gap'],
          ['R6e', 'Winter storm modifier', mods.R6e_winter != null ? mods.R6e_winter.toFixed(3) : '—', 'SFDR PAI: Physical acute hazards', mods.R6e_winter != null ? 'ready' : 'gap'],
          ['R8', 'Adaptation modifier', mods.R8_adapt != null ? mods.R8_adapt.toFixed(3) : '—', 'SFDR PAI: Adaptation planning', mods.R8_adapt != null ? 'ready' : 'gap'],
          ['R9', 'Compound event modifier', mods.R9_compound != null ? mods.R9_compound.toFixed(3) : '—', 'SFDR PAI: Compound climate risk', mods.R9_compound != null ? 'ready' : 'gap'],
          ['R10', 'Just-transition modifier', mods.R10_just != null ? mods.R10_just.toFixed(3) : '—', 'SFDR PAI: Social transition risk', mods.R10_just != null ? 'ready' : 'gap']
        ];
      },
      validity: 'Re_norm is the canonical SFDR PAI Infrastructure composite per SSI Index v4.2 methodology (FC v3 §14 subsection 13.7). It integrates the 8 v4.2 modifiers (R6c/R6d/R6e physical acute hazards + R8 adaptation + R9 compound events + R10 just-transition + R7 cyber + R3 social) into a single value normalised against the country-fleet percentile distribution. Convention #56 visibly-honest degradation preserves Re_norm=0.0 + Re_raw=1.0 as neutral defaults for net-new substations awaiting the L2/L3/L4 modifier-chain rescore pass per Convention #78 §4bis.4 two-phase workflow. GAP status reflects sites with fewer than 50% of fleet subs carrying non-default modifiers (typical during a v4.23 L1 refresh window before the follow-on rescore).'
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
    ['GHSL Population Grid', 'EC JRC / Copernicus', '2025', 'Multi-year', 'Attribution open license', 'R2'],
    ['Global Net-Migration Grid', 'Niva et al. 2023 (Aalto / Wittgenstein)', '2000-2019', 'Multi-year', 'CC BY 4.0', 'R2'],
    ['Eurostat GISCO NUTS-3 Regions', 'European Commission / Eurostat', '2024', 'Annual', 'Attribution open license', 'R2'],
    ['GADM Administrative Areas 4.1 (CO / CH / CA)', 'UC Davis geodata.ucdavis.edu/gadm', '2022', 'Multi-year', 'CC BY (academic derivative)', 'R2'],
    ['Economic Statistics (GDP, unemployment)', 'National Statistics Office', '2023', 'Annual', 'OGD', 'R2, R3'],
    ['Energy Market Data', 'National TSO', '2023', 'Annual', 'Regulated', 'R2, R4'],
    ['Renewable Installations', 'National DER Registry', '2024', 'Monthly', 'Open', 'R4'],
    ['Air Quality Monitoring', 'National Environmental Agency', '2023', 'Annual', 'CC-BY-4.0', 'R5'],
    ['Cybersecurity Index', 'ENISA', '2024', 'Biennial', 'Open', 'R6'],
    ['DESI Connectivity', 'European Commission', '2024', 'Annual', 'Open', 'R6'],
    ['IEEE C57.91 Thermal Model', 'IEEE', 'Standard', 'N/A', 'Published', 'R1'],
    ['CIGRE TB 761 Markov', 'CIGRE', '2019', 'N/A', 'Published', 'R1, R3'],
    ['ISO 9223 Corrosion', 'ISO', '2012', 'N/A', 'Published', 'R5'],
    // 21 July 2026: CMIP6 R1 status update (Discipline #46 candidate — data-source
    // status rows MUST reflect empirical truth). Cross-cutting 5-model ensemble
    // (ACCESS-CM2 + CNRM-CM6-1 + EC-Earth3 + GFDL-ESM4 + MRI-ESM2-0) SSP2-4.5
    // baseline 2000-2020 / future 2030-2050 is live for 32/39 countries via
    // scripts/pipeline/data/cross-cutting/cmip6_ssp245_deltas.csv (18,990 grid
    // points). Substation records carry climate_trajectory.{I1,I2,I3}_trajectory.
    // Known follow-ons: (i) 7 Wave 2-3 countries missing trajectory (Task #448);
    // (ii) 8 Wave 4 countries emit fleet-uniform trajectories from failed per-
    // substation interpolation (Task #449, sister to R3_C_mult Task #445).
    ['CMIP6 SSP2-4.5 Projections', 'Copernicus CDS', '2024', 'v4.2 5-model ensemble', 'CC-BY-4.0', 'R1']
  ];

  /* ── Helper: compute 7-axis ESG readiness scores (R1..R7) ─────────────────
     R7 SFDR PAI Infrastructure landed 16 July 2026 per FC v3 §14 subsection 13.7.
     R3 relabelled Infrastructure Resilience [Re composite home]; R4↔R5 swapped
     so R4=Pollution, R5=Transition per FC v3 §14 canonical order. ─────────── */
  function computeESGScores(d) {
    var r1 = 0, r2 = 0, r3 = 0, r4 = 0, r5 = 0, r6 = 0, r7 = 0;
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

    // R3 Infrastructure Resilience [Re composite home] — relabelled 16 July 2026
    if (d.R_median) r3 += 0.25;
    if (d.components) r3 += 0.25;
    if (d.modifiers) r3 += 0.20;
    if (d.markov) r3 += 0.20;
    if (d.CI_width) r3 += 0.10;

    // R4 Pollution & Corrosion — swapped from R5 position 16 July 2026
    if (mk.corrosion_class) r4 += 0.35;
    if (se.E2_local) r4 += 0.25;
    if (c.E) r4 += 0.20;
    r4 = Math.min(r4, 0.80);

    // R5 Energy Transition & DER Stress — swapped from R4 position 16 July 2026
    if (tr.T1_score !== undefined) r5 += 0.25;
    if (tr.DER_ratio !== undefined) r5 += 0.25;
    if (tr.DER_variability !== undefined) r5 += 0.25;
    if (tr.EV_load_ratio !== undefined) r5 += 0.25;

    // R6 Cyber
    if (mods.R7_cyber) r6 += 0.30;
    if (gt.BC_percentile) r6 += 0.25;
    if (gt.degree) r6 += 0.15;
    r6 = Math.min(r6, 0.70);

    // R7 SFDR PAI Infrastructure Disclosure — NEW 16 July 2026 per FC v3 §14
    //    Sourced from Re_norm (canonical SFDR PAI composite). Convention #56
    //    visibly-honest degradation: Re_norm=0.0 + Re_raw=1.0 are neutral
    //    defaults for net-new subs pre-modifier-chain-rescore (Convention #78
    //    §4bis.4 two-phase workflow). Modifier-availability contributes 40%.
    if (d.Re_norm != null && d.Re_norm !== 0.0) r7 += 0.35;
    if (d.Re_raw != null && d.Re_raw !== 1.0) r7 += 0.25;
    if (mods.R6c_flood != null) r7 += 0.10;
    if (mods.R6d_wildfire != null) r7 += 0.10;
    if (mods.R6e_winter != null) r7 += 0.05;
    if (mods.R8_adapt != null) r7 += 0.05;
    if (mods.R9_compound != null) r7 += 0.05;
    if (mods.R10_just != null) r7 += 0.05;
    r7 = Math.min(r7, 1.00);

    return [
      Math.round(r1 * 100) / 100,
      Math.round(r2 * 100) / 100,
      Math.round(r3 * 100) / 100,
      Math.round(r4 * 100) / 100,
      Math.round(r5 * 100) / 100,
      Math.round(r6 * 100) / 100,
      Math.round(r7 * 100) / 100
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
      ['R3 Infrastructure', 'Resilience [Re]'], ['R4 Pollution', '& Corrosion'],
      ['R5 Energy', 'Transition'], ['R6 Cybersecurity', 'Exposure'],
      ['R7 SFDR PAI', 'Infrastructure']
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

  /* ── 5. 7 individual ESG reports (large templated HTML) — R7 landed 16 Jul 2026 ── */
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
