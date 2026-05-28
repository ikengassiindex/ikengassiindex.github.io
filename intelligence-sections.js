/* ═══════════════════════════════════════════════════════════════════════════
   intelligence-sections.js — Phase 2c (KB §65) — Thin-shell section handlers
   ───────────────────────────────────────────────────────────────────────────
   Registers section renderers against CountryRenderer for the `intelligence`
   page (Monthly Intelligence Report). The shared rendering logic — Section A
   substation focus card, Section B Cyber & Economic Exposure Monitor,
   Section C Data Refresh, Section D thematic deep-dive, Section E European
   Context, Section F SSI-ENN, Section G Looking Ahead — lives here so every
   country's intelligence.html collapses to a thin-shell that calls:

       CountryRenderer.init('<country>', 'intelligence');

   Country-specific values live in `intelligence/country-configs/<slug>.json`:
     - `thresholds.r3_buckets`        — 3–5 tiers for B.2 Economic Impact
     - `thresholds.high_consequence_threshold` — KPI counter cutoff
     - `deep_dive_rotation`           — Section D 12-month region rotation
     - `current_deep_dive`            — which rotation slot is featured this edition
     - `saidi_peers`                  — Section E SAIDI peer-country table
     - `eu_context_card`              — Section E card metadata (title, sources note)
     - `deepDives` / `nextDeepDives`  — Section G next-edition rotation hooks

   For countries that haven't been migrated yet, sensible defaults apply.

   Dependencies (loaded by the HTML shell):
     - country-renderer.js  (provides window.CountryRenderer)
     - ssi-metadata.js      (window.SSI_METADATA / window.SSIMetadata.*)
     - intelligence-loader.js (sets window.SSI_COUNTRY + window.SSI_EDITION)
   No Chart.js dependency — all canvases drawn manually via 2D context.

   The file has no module footer — sections register themselves at load time.
   ═══════════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  if (!window.CountryRenderer) {
    console.error('[intelligence-sections] CountryRenderer not loaded — section registrations skipped');
    return;
  }
  var CR = window.CountryRenderer;
  var H = CR.H;

  /* ── Universal palette ──────────────────────────────────────────────── */
  var BAND_COLORS_HEX = {
    Low: '#5d8563', Medium: '#b8863a', High: '#aa4234', Critical: '#941914'
  };
  var BAND_COLORS_RGBA = {
    Low: 'rgba(93,133,99,0.5)', Medium: 'rgba(184,134,58,0.5)',
    High: 'rgba(170,66,52,0.5)', Critical: 'rgba(148,25,20,0.7)'
  };
  var BAND_VAR = {
    Low: 'var(--sage)', Medium: 'var(--bronze)', High: 'var(--terracotta)', Critical: 'var(--crimson)'
  };

  /* ── Default R3 tier ladder for non-migrated countries.
       Each country override lives in country-configs/<slug>.json under
       `thresholds.r3_buckets`. ────────────────────────────────────────── */
  var DEFAULT_R3_BUCKETS = [
    { label: 'Capital-Intensive / High-Consequence', icon: '🏭', lower: 1.05, upper: null, voll_range: '€15–30/kWh', color: '#941914',
      desc: 'Capital nodes — highest economic loss per interruption' },
    { label: 'Industrial / Medium-Large Enterprise', icon: '🔧', lower: 1.00, upper: 1.05, voll_range: '€8–15/kWh', color: '#aa4234',
      desc: 'Industrial belt — significant continuity requirements' },
    { label: 'Commercial / SME-Dense', icon: '🏪', lower: 0.97, upper: 1.00, voll_range: '€3–8/kWh', color: '#b8863a',
      desc: 'Service economy, retail — moderate individual impact' },
    { label: 'Light / Agricultural / Rural', icon: '🌾', lower: 0.0, upper: 0.97, voll_range: '€1–3/kWh', color: '#5d8563',
      desc: 'Sparse activity, agricultural land — lower VoLL' }
  ];

  /* ── Universal SSI-ENN topic registry (20 monthly topics, Layers 1–5).
       Identical across countries — universal architectural narrative. ── */
  var ENN_TOPICS = [
    { layer: 1, ref: '§0.3', title: 'Data Architecture — Component Taxonomy',
      subtitle: 'How the SSI\'s 6 components and 20 sub-metrics are sourced, validated, and scored',
      body: 'The SSI-ENN\'s Layer 1 formally specifies the SSI v4.0 Index — its six components (Continuity, Voltage, Infrastructure, Economic, Saturation, Transition), twenty sub-metrics, normalisation methodology, and aggregation rules. Each sub-metric is independently sourced from one of the 30 public data sources in the SSI registry, validated against known reference distributions, and normalised to a common [0, 1] scale before aggregation. This rigorous data architecture is the foundation layer: without substation-level grid intelligence at this granularity, neither the BESS valuation engine nor the neural network can exist. The component taxonomy directly maps to downstream valuation outputs — for example, the C (Continuity) component feeds the DSO/TSO\'s avoided-outage calculation (D1), while the E (Economic) component feeds the community value stack\'s energy poverty reduction estimate (W3).',
      concepts: ['6 components, 20 sub-metrics, 95 variables', 'Min-max normalisation with winsorised tails', 'Component weights: 0.30·C + 0.10·V + 0.25·I + 0.10·E + 0.20·S + 0.05·T', 'Each sub-metric traceable to authoritative public source'] },
    { layer: 1, ref: '§0.3.4', title: 'Gaussian Copula Monte Carlo Engine',
      subtitle: 'How 1.58 million simulations capture the correlation structure across grid risk factors',
      body: 'The SSI components are not independent — a substation with poor continuity (high C) often also has poor voltage quality (high V), aged infrastructure (high I5), and is located in a rural area with high economic vulnerability (high E). The Gaussian copula captures these dependencies through a 20×20 correlation matrix estimated from the national fleet, decomposed via Cholesky factorisation to generate correlated random draws. For each substation, 10,000 Monte Carlo iterations propagate uncertainty through the full scoring formula, producing not just a point estimate (R_median) but a complete posterior distribution — P5, P50, P95, confidence interval width, and skewness. This is the computational backbone, yielding the uncertainty quantification that distinguishes the SSI from deterministic indices.',
      concepts: ['20×20 Gaussian copula with Cholesky decomposition', '10,000 iterations per substation', 'Full posterior: R_P5, R_median, R_P95, CI_width, skewness', 'Correlation captures systemic clustering of risk factors'] },
    { layer: 2, ref: '§0.4.1', title: 'DSO/TSO Value Stack (D1–D5)',
      subtitle: 'What a BESS is worth to the distribution network operator in avoided or deferred costs',
      body: 'The DSO/TSO value stack quantifies five categories of value that a battery energy storage system creates for the distribution network operator at each substation. D1 (Avoided Outage Cost) uses the SSI\'s C component and SAIDI data to estimate the reduction in customer-minutes-lost. D2 (Deferred Reinforcement) leverages the S (Saturation) and I (Infrastructure) components to calculate how BESS deployment can postpone expensive grid upgrades. D3 (Reactive Power Support) draws on V (Voltage) data to value power quality improvement. D4 (Loss Reduction) uses graph topology (R4) to estimate reduced network losses. D5 (Fault Level Management) reflects the BESS\'s contribution to grid stability. Each component maps directly to one or more SSI v4.0 inputs — the Index doesn\'t just measure risk, it prices the economic case for intervention.',
      concepts: ['D1: Avoided Outage = f(C, SAIDI, customer count)', 'D2: Deferred Reinforcement = f(S, I, load growth)', 'D3: Reactive Power = f(V, network impedance)', 'D4 + D5: Loss Reduction + Fault Level = f(R4, topology)'] },
    { layer: 2, ref: '§0.4.2', title: 'Community Value Stack (W1–W5)',
      subtitle: 'Social and economic value to the local community — the case for public-interest investment',
      body: 'While the DSO/TSO value stack speaks the language of regulated returns, the community value stack addresses a different audience: regional governments, NEPN / national digital plan / RRP allocators, and EU structural fund decision-makers. W1 (Energy Cost Reduction) estimates savings for local consumers from peak-shaving and arbitrage, weighted by the energy poverty rate (EP_rate) from the SSI\'s socio-economic data. W2 (Local Employment) models the O&M jobs created per MW deployed. W3 (Energy Poverty Alleviation) uses the SSI\'s E component to quantify the welfare impact on vulnerable households. W4 (Carbon Reduction) converts dispatched MWh to avoided CO₂ using marginal emissions factors. W5 (Resilience Value) — perhaps the most novel — uses the SSI\'s full R_median distribution to price the avoided cost of extreme events. All five are discounted at the social discount rate (3.0% real, per EU Commission CBA guidance).',
      concepts: ['W1: Energy cost savings weighted by EP_rate', 'W3: Energy poverty alleviation from E component', 'W5: Resilience value from SSI R_median distribution', 'Social discount rate 3.0% (EU CBA guidance)'] },
    { layer: 2, ref: '§0.4.5', title: 'Real Options Pricing Framework',
      subtitle: 'Why traditional DCF systematically undervalues BESS — and how six embedded options fix this',
      body: 'Traditional discounted cashflow analysis treats a BESS investment as a fixed sequence of revenues and costs over 30 years. In reality, the asset owner has options: to expand capacity if market conditions improve, to repurpose for different services as regulations evolve, to delay investment until uncertainty resolves. The SSI-ENN prices six embedded real options for each substation-BESS pair: capacity expansion option, technology refresh option, revenue-stream switching option, grid-connection upgrade option, decommissioning timing option, and a regulatory windfall option capturing the value of favorable policy changes. The SSI data drives the underlying volatility: substations with wider confidence intervals (high CI_width) have higher option value because uncertainty creates optionality.',
      concepts: ['6 embedded options per substation-BESS pair', 'Black-Scholes for capacity expansion, American options for switching', 'Higher SSI uncertainty (CI_width) = higher option value', 'Option-adjusted NPV typically 15-40% above base DCF'] },
    { layer: 2, ref: '§0.4.4', title: 'Revenue Stack & Dispatch Optimisation',
      subtitle: 'Up to 11 revenue streams from a single battery — subject to one physical constraint',
      body: 'A grid-connected BESS generates revenue from up to 11 streams (R1–R11), but is physically constrained to one full charge-discharge cycle per day. The dispatch optimiser allocates this single cycle across competing revenue opportunities: energy arbitrage (R1), frequency containment reserve (R2), automatic frequency restoration (R3), replacement reserve (R4), capacity market (R5), reactive power (R6), peak shaving (R7), backup power (R8), and three emerging streams — locational marginal pricing (R9), power quality as a service (R10), and carbon reduction services (R11). The optimiser is location-specific because the SSI data determines which streams are most valuable at each substation. The revenue stack varies by country — the model accommodates all EU market designs.',
      concepts: ['11 revenue streams (R1–R11), 1-cycle/day constraint', 'Location-specific optimisation from SSI component data', 'R9–R11: Emerging streams modelled as forward-looking options', 'Country-adaptive market design accommodation'] },
    { layer: 3, ref: '§0.5.2', title: 'Neural Network — Ensemble Architecture',
      subtitle: 'GBT + DNN ensemble: why two model families outperform either alone on grid data',
      body: 'The SSI-ENN\'s neural network is a weighted ensemble of two complementary model families. Gradient-Boosted Trees (GBT) excel at tabular data with heterogeneous features. Deep Neural Networks (DNN) excel at learning complex non-linear interactions and benefit from the high-dimensional feature space. The ensemble weight α is learned during validation: α·GBT + (1-α)·DNN. The shared feature representation enables multi-task learning: all 7 output heads (R_median, DSO NPV, Community NPV, option value, optimal config, risk band, confidence tier) are predicted simultaneously, forcing the network to learn representations useful for all tasks.',
      concepts: ['Ensemble: α·GBT + (1-α)·DNN, α learned during validation', '7 simultaneous outputs via multi-task learning', 'GBT dominates with sparse data, DNN with dense data', 'Shared representation = implicit regularisation'] },
    { layer: 3, ref: '§0.5.3', title: 'Transfer Learning & Feature Missingness',
      subtitle: 'How national ground truth enables valuation across 28 countries with incomplete data',
      body: 'Transfer learning is the mechanism that enables the SSI-ENN to value substations in countries where the full feature vector is not available. The core insight: grid physics is universal — topology determines load flow, weather drives thermal degradation, population density correlates with outage impact — even though data availability varies dramatically across jurisdictions. The network is first trained on the complete national dataset; then, for each new country, available features are mapped to the reference schema. Missing features are handled through a learned missingness embedding: the network learns not just to predict from available data, but to quantify how much accuracy it loses from each missing feature.',
      concepts: ['Train on full data, transfer to partial-data countries', 'Learned missingness embedding quantifies data value', 'Grid physics universality enables cross-border transfer', 'Accuracy convergence: f(Data Completeness Index)'] },
    { layer: 3, ref: '§0.5.5', title: 'Uncertainty Quantification',
      subtitle: 'Investment-grade predictions require calibrated confidence intervals, not just point estimates',
      body: 'A point estimate without uncertainty bounds is unusable for investment-grade analysis. The SSI-ENN produces calibrated P10/P50/P90 prediction intervals using two complementary approaches: quantile regression (pinball loss) and conformal prediction (distribution-free guaranteed coverage). The SSI\'s own Monte Carlo confidence intervals (CI_width, P5/P95) serve as the ground truth for calibration. This calibration is verified per country, per voltage class, and per risk band.',
      concepts: ['Quantile regression (pinball loss) + conformal prediction', 'Calibrated against SSI Monte Carlo ground truth', 'Per-country, per-voltage, per-band calibration verification', 'Investment-grade: P10/P50/P90 for all outputs'] },
    { layer: 3, ref: '§0.5.6', title: 'Explainability & SHAP Values',
      subtitle: 'Clients need to understand not just the prediction but WHY a substation ranks highly',
      body: 'Investment-grade models require interpretability. SHAP (SHapley Additive exPlanations) provides a rigorous, game-theoretic attribution of each feature\'s contribution to each prediction. For every substation, the SSI-ENN produces a SHAP waterfall: starting from the fleet-average valuation and showing how each feature pushes the estimate up or down. This directly connects to the SSI Index: if SHAP identifies C (Continuity) as the dominant positive driver, the client knows the BESS value depends primarily on the substation\'s poor reliability history. Transparency converts model outputs into investment decisions.',
      concepts: ['SHAP: game-theoretic feature attribution per prediction', 'Waterfall: fleet average → substation prediction', 'Direct traceability to SSI components and data sources', 'Feature importance validated against domain expertise'] },
    { layer: 4, ref: '§0.6.1', title: 'European Expansion — Country Prioritisation',
      subtitle: 'How 28 countries are ranked by expected commercial return per unit of expansion effort',
      body: 'The SSI-ENN targets ~500,000+ substations across 28 countries (EU-27 + UK). But expansion resources are finite — each country requires data acquisition, regulatory mapping, source substitution, and calibration. The country prioritisation score balances four dimensions: market size, data availability (Data Completeness Index), strategic value, and expansion cost.',
      concepts: ['Priority = Market Size × Data Completeness × Strategic Value / Cost', '28 countries: EU-27 + UK', 'Highest DCI scores in FR, DE, IT then ES, NL, UK', 'Each country requires bespoke regulatory mapping'] },
    { layer: 4, ref: '§0.6.2', title: 'Data Completeness Index',
      subtitle: 'Quantifying what fraction of the SSI feature vector is available for each country',
      body: 'The Data Completeness Index (DCI) quantifies what fraction of the SSI-ENN\'s feature vector can be populated for a given country, weighted by each feature\'s contribution to prediction accuracy. DCI = Σ(w_i × available_i) where w_i is the feature\'s SHAP importance rank. A country with DCI > 0.70 can produce production-quality valuations; DCI 0.50–0.70 produces indicative estimates; below 0.50, the uncertainty bounds are too wide for commercial use. The DCI also creates a concrete procurement roadmap.',
      concepts: ['DCI = Σ(SHAP_weight × data_available) per country', 'DCI > 0.70 = production quality, 0.50–0.70 = indicative', 'OSM topology available globally = high-weight features covered', 'DCI creates data procurement priority roadmap'] },
    { layer: 4, ref: '§0.6.4', title: 'SSI Transfer & Calibration Protocol',
      subtitle: 'Adapting the SSI model across different national grid characteristics',
      body: 'Deploying the SSI across each country requires adapting three elements: the data sources (map to country-equivalents), the calibration parameters (voltage thresholds, outage benchmarks), and the regulatory context. The transfer protocol follows a 5-step process: (1) source mapping; (2) gap analysis; (3) recalibration; (4) cross-validation; (5) coverage scorecard.',
      concepts: ['5-step protocol: source mapping → gap → recalibration → validation → scorecard', 'National regulators: CRE (FR), BNetzA (DE), ARERA (IT), Ofgem (UK)', 'Normalisation bounds adjusted per country distribution', 'Production-readiness requires passing Coverage Quality Scorecard'] },
    { layer: 5, ref: '§0.7.1', title: 'Platform — Product Delivery Pipeline',
      subtitle: 'From raw analytical outputs to four commercial product formats',
      body: 'The SSI-ENN\'s analytical engine produces a high-dimensional output vector per substation per BESS configuration. The product delivery pipeline transforms this into four distinct formats: (1) Explorer Dashboard — self-service web interface; (2) API — programmatic access; (3) Value-Add Card — per-substation PDF report; (4) Advisory Report — bespoke multi-substation analysis. Each format applies different levels of contextualisation, visualisation, and narrative.',
      concepts: ['4 products: Dashboard, API, Value-Add Card, Advisory Report', 'Single analytical core, multiple delivery formats', 'Value-Add Card: per-substation investor-grade PDF', 'Advisory: bespoke multi-substation institutional analysis'] },
    { layer: 5, ref: '§0.7.3', title: 'Revenue Model & Unit Economics',
      subtitle: 'Three revenue channels with distinct scaling characteristics',
      body: 'Subscriptions (recurring, scalable, high-margin): three tiers — Explorer (€990/month), Developer (€4,900/month), Enterprise (custom). Advisory services: €25K–€150K per project. Data licensing: €50K–€200K/year. The platform exhibits extreme operating leverage: once built, the marginal cost of serving each additional subscriber approaches zero. Critical metric: LTV:CAC ratio must exceed 3:1.',
      concepts: ['3 tiers: Explorer €990/mo, Developer €4,900/mo, Enterprise custom', 'Advisory: €25K–€150K per project', 'Data licensing: €50K–€200K/year', 'Operating leverage: near-zero marginal cost per subscriber'] },
    { layer: 1, ref: '§0.3.6', title: 'Data Flow Matrix — Traceability Register',
      subtitle: 'For any output number, trace it back to the exact input variable and source',
      body: 'The Data Flow Matrix maps every SSI component and sub-metric to the downstream valuation outputs it influences. This traceability register is a design requirement for investment-grade analytics: a €10M BESS investment decision must withstand due diligence, which means every assumption must be auditable. The matrix also enables targeted recomputation rather than full fleet recalculation when data sources update.',
      concepts: ['Every output traceable to specific inputs and sources', 'Investment-grade auditability for due diligence', 'Targeted recomputation when sources update', 'Bidirectional: input→output and output→input'] },
    { layer: 2, ref: '§0.4.3', title: 'Total Cost of Ownership Model',
      subtitle: 'Stochastic cost modelling — because BESS economics are not deterministic',
      body: 'CAPEX follows a learning-curve distribution calibrated to Bloomberg NEF projections. OPEX is modelled as a mean-reverting process with seasonal components reflecting temperature-dependent degradation. Battery degradation follows a non-linear capacity fade model: each cycle reduces usable capacity, with rate depending on depth-of-discharge, temperature, and C-rate. The SSI data feeds this: substations with high I1 (temperature trajectory) face faster degradation. The Monte Carlo engine propagates cost uncertainty alongside revenue uncertainty.',
      concepts: ['CAPEX learning curve calibrated to BNEF', 'Non-linear battery degradation: f(DoD, temperature, C-rate)', 'SSI I1 (climate trajectory) drives degradation forecast', 'Full NPV distribution, not point estimate'] },
    { layer: 1, ref: '§0.3.2', title: 'Sub-Metric Definitions — Replicability Standard',
      subtitle: 'Every sub-metric defined with sufficient precision for independent replication',
      body: 'Each of the SSI\'s 20 sub-metrics is defined with sufficient precision for independent replication — a core requirement for academic credibility and regulatory acceptance. Take C1 (SAIDI proxy): it combines national regulator quality-of-supply territorial classification with Eurostat unplanned SAIDI benchmarks, normalised against EU-wide reference distributions. Each definition specifies: the mathematical formula, the data source and update frequency, the normalisation method, the relationship to upstream inputs, and the downstream components it feeds.',
      concepts: ['20 sub-metrics, each formally defined for replication', 'C1: SAIDI proxy from national quality-of-supply reports', 'I5: 4-state Markov degradation chain', 'Enables peer review, regulatory audit, and international transfer'] },
    { layer: 5, ref: '§0.7.2', title: 'API & Computation Architecture',
      subtitle: 'Serving batch fleet recomputation and interactive queries from a single platform',
      body: 'The platform serves two workloads: batch computation (recompute ~500K substations during quarterly refresh — GPU-intensive) and interactive query (single substation lookup in <200ms — CPU-bound). Batch runs on GPU clusters producing pre-computed results stored in a columnar database. Interactive queries hit this store with real-time adjustments for user-specified parameters. Rate limits and access tiers map to subscription levels.',
      concepts: ['Batch (GPU, quarterly) + Interactive (<200ms, CPU)', 'Pre-computed columnar store for low-latency queries', 'Explorer: 100/day, Developer: 10K/day, Enterprise: unlimited', 'Real-time parameter adjustment on pre-computed base'] },
    { layer: 4, ref: '§0.6.3', title: 'Substation Registry Construction',
      subtitle: 'How to identify 500,000+ substations across 28 countries from open data',
      body: 'The construction pipeline follows four steps: (1) OSM extraction — query all nodes/ways tagged power=substation within the country boundary, filtering by voltage class; (2) deduplication; (3) attribute enrichment from operator and national datasets; (4) validation against published grid statistics. The reference recovery rate against official national registries is typically 95%+, giving confidence in transferability.',
      concepts: ['OSM extraction → deduplication → enrichment → validation', '95%+ recovery rate against official registries', 'Voltage class, operator, capacity from OSM + national data', 'Target: 500K+ substations across 28 countries'] }
  ];

  /* ── Layer definitions (Section F nav) — universal across countries. ─ */
  var ENN_LAYERS = [
    { n: 1, label: 'Layer 1 — Data', color: '#2c3e7a', desc: 'SSI v4.0 component taxonomy, normalisation, MC engine' },
    { n: 2, label: 'Layer 2 — Valuation', color: '#c0392b', desc: 'DSO/TSO + Community value stacks, TCO, real options' },
    { n: 3, label: 'Layer 3 — Neural Net', color: '#6c3483', desc: 'GBT+DNN ensemble, transfer learning, SHAP' },
    { n: 4, label: 'Layer 4 — Coverage', color: '#1a6b4a', desc: 'Country prioritisation, DCI, registry, calibration' },
    { n: 5, label: 'Layer 5 — Platform', color: '#0e7490', desc: 'Products, API, revenue model, unit economics' }
  ];

  /* ── Helpers ────────────────────────────────────────────────────────── */
  function seededIndex(seed, len) {
    var h = seed;
    h = ((h >>> 16) ^ h) * 0x45d9f3b | 0;
    h = ((h >>> 16) ^ h) * 0x45d9f3b | 0;
    h = (h >>> 16) ^ h;
    return Math.abs(h) % len;
  }
  function intelligenceMonthSeed() {
    var d = new Date(), y = d.getFullYear(), m = d.getMonth() + 1;
    if (y < 2026 || (y === 2026 && m < 5)) return 202603;
    return y * 100 + m;
  }
  function sortNum(a, b) { return a - b; }
  function median(arr) {
    if (!arr.length) return 0;
    var s = arr.slice().sort(sortNum);
    return s[Math.floor(s.length / 2)];
  }
  function r3BucketsFromConfig(cfg) {
    var t = cfg && cfg.thresholds;
    if (t && Array.isArray(t.r3_buckets) && t.r3_buckets.length) return t.r3_buckets;
    return DEFAULT_R3_BUCKETS;
  }
  function highConseqThreshold(cfg) {
    var t = cfg && cfg.thresholds;
    if (t && typeof t.high_consequence_threshold === 'number') return t.high_consequence_threshold;
    return 1.04;
  }
  /* Pick monthly substation using the intelligence page's specific seed
     (with the pre-May-2026 hold). This intentionally differs from
     CountryRenderer.pickMonthlySubstation which uses a plain y*100+m seed. */
  function pickFocusSubstation(data) {
    if (!data || !Array.isArray(data.substations) || !data.substations.length) return null;
    return data.substations[seededIndex(intelligenceMonthSeed(), data.substations.length)];
  }

  /* ══════════════════════════════════════════════════════════════════════
     SECTION A — Substation in Focus card + canvas radar + narrative
     ══════════════════════════════════════════════════════════════════════ */
  CR.register('intelligence', 'focus-card', function (ctx) {
    var s = pickFocusSubstation(ctx.data);
    if (!s) return;

    var doc = ctx.doc;
    var nameEl = doc.getElementById('focus-name');
    if (nameEl) nameEl.textContent = s.name;
    var locEl = doc.getElementById('focus-location');
    if (locEl) locEl.textContent = (s.province || '') + ', ' + (s.region || '') + ' · ' + (s.voltage_kv || '—') + ' kV';
    H.setText('focus-r', (s.R_median != null) ? s.R_median.toFixed(3) : '—');
    H.setText('focus-band', s.classification || '—');
    H.setText('focus-ci', (s.CI_width != null) ? s.CI_width.toFixed(3) : '—');
    H.setText('focus-pctile', (s.fleet_percentile != null) ? (s.fleet_percentile * 100).toFixed(0) + 'th' : '—');

    var fb = doc.getElementById('focus-band'), fr = doc.getElementById('focus-r');
    if (fb) fb.style.color = BAND_VAR[s.classification] || 'var(--ink)';
    if (fr) fr.style.color = BAND_VAR[s.classification] || 'var(--ink)';

    // Components
    var compDefs = [
      { key: 'C', label: 'Continuity',     w: 0.30, color: 'var(--crimson)' },
      { key: 'I', label: 'Infrastructure', w: 0.25, color: 'var(--sage)' },
      { key: 'S', label: 'Saturation',     w: 0.20, color: 'var(--bronze)' },
      { key: 'V', label: 'Voltage',        w: 0.10, color: 'var(--terracotta)' },
      { key: 'E', label: 'Economic',       w: 0.10, color: '#3b9eff' },
      { key: 'T', label: 'Transition',     w: 0.05, color: '#22d3ee' }
    ];
    var comps = s.components || {};
    var compHTML = compDefs.map(function (c) {
      var val = comps[c.key];
      if (val == null) return '';
      var pct = (val / c.w * 100).toFixed(0);
      var isAlert = s.alert_components && s.alert_components.indexOf(c.key) >= 0;
      return '<div><strong style="color:' + c.color + '">' + c.key + '</strong> ' + c.label + ': ' +
        val.toFixed(3) + ' / ' + c.w.toFixed(2) + ' (' + pct + '%)' +
        (isAlert ? ' <span style="color:var(--crimson);font-weight:600">⚠</span>' : '') + '</div>';
    }).join('');
    H.setHTML('focus-components', compHTML);

    // Modifiers
    var modDefs = [
      { key: 'R3_C_mult',      label: 'R3 Consequence' },
      { key: 'R4_F_topo',      label: 'R4 Graph Criticality' },
      { key: 'R6_restoration', label: 'R6a Restoration' },
      { key: 'R6_seismic',     label: 'R6b Seismic' },
      { key: 'R7_cyber',       label: 'R7 Digital Readiness' }
    ];
    var mods = s.modifiers || {};
    var modHTML = modDefs.map(function (m) {
      var val = mods[m.key];
      if (val == null) return '';
      var dir = val > 1.01 ? '↑ amplifies' : val < 0.99 ? '↓ dampens' : '→ neutral';
      var col = val > 1.05 ? 'var(--crimson)' : val < 0.95 ? 'var(--sage)' : 'var(--warm-grey)';
      return '<div><strong>' + m.label + ':</strong> <span style="color:' + col + '">' + val.toFixed(3) + '</span> ' + dir + '</div>';
    }).join('');
    H.setHTML('focus-modifiers', modHTML);

    // Radar canvas
    var canvas = doc.getElementById('focus-radar');
    if (canvas && canvas.getContext) {
      var cctx = canvas.getContext('2d');
      var W = canvas.width, Hh = canvas.height;
      var cx = W / 2, cy = Hh / 2 + 6;
      var R = 68;
      var labels = ['C', 'V', 'I', 'E', 'S', 'T'];
      var weights = [0.30, 0.10, 0.25, 0.10, 0.20, 0.05];
      var _compSum = labels.reduce(function (sum, k) { return sum + (comps[k] || 0); }, 0);
      var _isWeighted = _compSum <= 1.0;
      var vals = labels.map(function (k, i) { return _isWeighted ? (comps[k] || 0) / weights[i] : (comps[k] || 0); });
      var n = labels.length;

      // Concentric rings
      cctx.strokeStyle = 'rgba(44,36,32,0.08)';
      cctx.lineWidth = 1;
      [0.25, 0.5, 0.75, 1.0].forEach(function (ring) {
        cctx.beginPath();
        for (var i = 0; i <= n; i++) {
          var ang = (Math.PI * 2 * (i % n) / n) - Math.PI / 2;
          var x = cx + R * ring * Math.cos(ang);
          var y = cy + R * ring * Math.sin(ang);
          if (i === 0) cctx.moveTo(x, y); else cctx.lineTo(x, y);
        }
        cctx.stroke();
      });
      // Axes
      for (var i = 0; i < n; i++) {
        var ang2 = (Math.PI * 2 * i / n) - Math.PI / 2;
        cctx.beginPath();
        cctx.moveTo(cx, cy);
        cctx.lineTo(cx + R * Math.cos(ang2), cy + R * Math.sin(ang2));
        cctx.stroke();
      }
      // Polygon
      cctx.fillStyle = 'rgba(148,25,20,0.15)';
      cctx.strokeStyle = 'rgba(148,25,20,0.7)';
      cctx.lineWidth = 2;
      cctx.beginPath();
      for (var j = 0; j <= n; j++) {
        var ang3 = (Math.PI * 2 * (j % n) / n) - Math.PI / 2;
        var v = Math.min(vals[j % n], 1);
        var x2 = cx + R * v * Math.cos(ang3);
        var y2 = cy + R * v * Math.sin(ang3);
        if (j === 0) cctx.moveTo(x2, y2); else cctx.lineTo(x2, y2);
      }
      cctx.fill();
      cctx.stroke();
      // Labels
      cctx.fillStyle = '#2c2420';
      cctx.font = '600 11px DM Sans, sans-serif';
      cctx.textAlign = 'center';
      cctx.textBaseline = 'middle';
      for (var k = 0; k < n; k++) {
        var ang4 = (Math.PI * 2 * k / n) - Math.PI / 2;
        var lx = cx + (R + 16) * Math.cos(ang4);
        var ly = cy + (R + 16) * Math.sin(ang4);
        cctx.fillText(labels[k], lx, ly);
      }
    }

    // Narrative
    var dominant = compDefs.slice().filter(function (c) { return comps[c.key] != null; })
                            .sort(function (a, b) { return (comps[b.key] / b.w) - (comps[a.key] / a.w); });
    var top1 = dominant[0], top2 = dominant[1];
    var modImpact;
    if (s.modifier_pct != null) modImpact = s.modifier_pct + '%';
    else if (s.modifier_impact != null && s.R_base_median) modImpact = (s.modifier_impact / s.R_base_median * 100).toFixed(1) + '%';
    else modImpact = '—';
    var monthNames = ['January','February','March','April','May','June','July','August','September','October','November','December'];
    var d = new Date();
    var narrative = 'This month\'s spotlight — automatically selected for ' + monthNames[d.getMonth()] + ' ' + d.getFullYear() +
      ' — is <strong>' + (s.name || '—') + '</strong> in ' + (s.province || '') + ', ' + (s.region || '') +
      '. With an R_final of ' + ((s.R_median != null) ? s.R_median.toFixed(3) : '—') + ' (' + (s.classification || '—') + ' band, ' +
      ((s.fleet_percentile != null) ? (s.fleet_percentile * 100).toFixed(0) : '—') + 'th fleet percentile), its risk profile is dominated by the ' +
      (top1 ? top1.key + ' (' + top1.label + ') component at ' + (comps[top1.key] / top1.w * 100).toFixed(0) + '% of its weight ceiling' : '—') +
      (top2 ? ', followed by ' + top2.key + ' (' + top2.label + ') at ' + (comps[top2.key] / top2.w * 100).toFixed(0) + '%' : '') +
      '. Modifiers collectively shift R_base by ' + modImpact +
      ', reflecting the substation\'s specific geographic, socio-economic, and network context.';
    H.setHTML('focus-narrative', narrative);
  });

  /* ══════════════════════════════════════════════════════════════════════
     SECTION B — Cyber & Economic Exposure Monitor (B1–B4)
     ══════════════════════════════════════════════════════════════════════ */
  CR.register('intelligence', 'cyber-econ', function (ctx) {
    var fleet = (ctx.data && ctx.data.substations) || [];
    var n = fleet.length;
    if (!n) return;
    var doc = ctx.doc;

    var r7vals = fleet.map(function (s) { return (s.modifiers && s.modifiers.R7_cyber) || 0; });
    var avgR7 = r7vals.reduce(function (a, b) { return a + b; }, 0) / n;
    var medianR7 = median(r7vals);
    var medianR = median(fleet.map(function (s) { return s.R_median || 0; }));

    // Cyber classification counts
    var cyberCounts = { LOW: 0, MEDIUM: 0, HIGH: 0 };
    fleet.forEach(function (s) {
      var cls = ((s.cyber_classification || '').split(' ')[0] || '').toUpperCase();
      if (cyberCounts[cls] !== undefined) cyberCounts[cls]++;
    });

    // Blind spots: High/Critical + R7 < median
    var blindSpots = fleet.filter(function (s) {
      return (s.classification === 'High' || s.classification === 'Critical') &&
             (s.modifiers && s.modifiers.R7_cyber < medianR7);
    });

    // High-consequence threshold from config
    var hcThr = highConseqThreshold(ctx.config);
    var highConseq = fleet.filter(function (s) {
      return s.modifiers && s.modifiers.R3_C_mult >= hcThr;
    });

    // B.1 KPIs
    H.setText('b1-cyber-high', cyberCounts.HIGH);
    H.setText('b1-cyber-high-sub', (cyberCounts.HIGH / n * 100).toFixed(1) + '% of fleet');
    H.setText('b1-blindspots', blindSpots.length);
    H.setText('b1-blindspots-sub', 'High/Critical + R7 < median');
    H.setText('b1-avg-r7', avgR7.toFixed(4));
    H.setText('b1-high-conseq', highConseq.length.toLocaleString());
    H.setText('b1-high-conseq-sub', (highConseq.length / n * 100).toFixed(1) + '% · R3 ≥ ' + hcThr.toFixed(2));

    // B.1 Scatter matrix canvas
    drawCyberMatrix(doc, fleet, medianR7, medianR);

    // B.1 Narrative
    var blindRegions = {};
    blindSpots.forEach(function (s) { blindRegions[s.region] = (blindRegions[s.region] || 0) + 1; });
    var topBlind = Object.keys(blindRegions).map(function (r) { return { name: r, n: blindRegions[r] }; })
                      .sort(function (a, b) { return b.n - a.n; }).slice(0, 3);
    var blindStr = topBlind.map(function (r) { return r.name + ' (' + r.n + ')'; }).join(', ') || '—';

    H.setHTML('b1-narrative',
      'The cyber-physical matrix identifies <strong>' + blindSpots.length + ' blind-spot substations</strong> — ' +
      'scoring High or Critical on overall risk while sitting below the fleet median for digital readiness (R7 &lt; ' + medianR7.toFixed(4) + '). ' +
      'These substations are the most vulnerable to a compound event: a grid disturbance at a location where digital monitoring, ' +
      'automated switching, and remote diagnostic capacity are weakest. ' +
      'The blind spots concentrate in <strong>' + blindStr + '</strong>. ' +
      'Across the full fleet, ' + cyberCounts.HIGH + ' substations (' + (cyberCounts.HIGH / n * 100).toFixed(1) + '%) carry a HIGH cyber-exposure classification, ' +
      'while ' + cyberCounts.LOW + ' (' + (cyberCounts.LOW / n * 100).toFixed(1) + '%) are in the LOW tier.');

    // B.2 Economic Impact by Business Fabric — config-driven tier ladder
    var tiers = r3BucketsFromConfig(ctx.config);
    var tiersHTML = '';
    tiers.forEach(function (tier) {
      var lower = (typeof tier.lower === 'number') ? tier.lower : 0;
      var upper = (tier.upper == null) ? Infinity : tier.upper;
      var subs = fleet.filter(function (s) {
        var v = s.modifiers && s.modifiers.R3_C_mult;
        return typeof v === 'number' && v >= lower && v < upper;
      });
      var nTier = subs.length;
      var highCrit = subs.filter(function (s) { return s.classification === 'High' || s.classification === 'Critical'; }).length;
      var avgR = nTier ? subs.reduce(function (a, s) { return a + (s.R_median || 0); }, 0) / nTier : 0;
      var avgE = nTier ? subs.reduce(function (a, s) { return a + ((s.components && s.components.E) || 0); }, 0) / nTier : 0;
      var pctFleet = (nTier / n * 100).toFixed(1);

      var tierBands = { Low: 0, Medium: 0, High: 0, Critical: 0 };
      subs.forEach(function (s) { if (tierBands[s.classification] !== undefined) tierBands[s.classification]++; });
      var bandBar = '';
      ['Low', 'Medium', 'High', 'Critical'].forEach(function (b) {
        if (tierBands[b] > 0 && nTier > 0) {
          var w = (tierBands[b] / nTier * 100).toFixed(1);
          bandBar += '<div style="width:' + w + '%;height:100%;background:' + BAND_COLORS_HEX[b] + '" title="' + b + ': ' + tierBands[b] + '"></div>';
        }
      });

      tiersHTML += '<div class="card" style="margin-bottom:12px;border-left:3px solid ' + (tier.color || '#888') + '">' +
        '<div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px">' +
          '<span style="font-size:14px;font-weight:600">' + (tier.icon || '•') + ' ' + tier.label + '</span>' +
          '<span style="font-size:12px;color:var(--warm-grey)">Est. VoLL: ' + (tier.voll_range || '—') + '</span></div>' +
        (tier.desc ? '<p style="font-size:12px;color:var(--warm-grey);margin:0 0 8px">' + tier.desc + '</p>' : '') +
        '<div style="display:flex;gap:16px;flex-wrap:wrap;font-size:12px;margin-bottom:8px">' +
          '<span><strong>' + nTier.toLocaleString() + '</strong> substations (' + pctFleet + '%)</span>' +
          '<span>High/Critical: <strong style="color:var(--crimson)">' + highCrit + '</strong> (' + (nTier ? (highCrit / nTier * 100).toFixed(1) : 0) + '%)</span>' +
          '<span>Avg R: <strong>' + avgR.toFixed(3) + '</strong></span>' +
          '<span>Avg E: <strong>' + avgE.toFixed(3) + '</strong> / 0.10</span></div>' +
        '<div style="height:8px;border-radius:4px;overflow:hidden;display:flex">' + bandBar + '</div>' +
        '<div style="display:flex;justify-content:space-between;font-size:10px;color:var(--warm-grey);margin-top:3px">' +
          '<span>Low ' + tierBands.Low + '</span><span>Med ' + tierBands.Medium + '</span>' +
          '<span>High ' + tierBands.High + '</span><span>Crit ' + tierBands.Critical + '</span></div>' +
      '</div>';
    });
    H.setHTML('b2-tiers', tiersHTML);

    // VoLL note
    var topTier = tiers[0];
    var topLower = (topTier && typeof topTier.lower === 'number') ? topTier.lower : 1.05;
    var totalHCHR = fleet.filter(function (s) {
      var v = s.modifiers && s.modifiers.R3_C_mult;
      return v >= topLower && (s.classification === 'High' || s.classification === 'Critical');
    }).length;
    H.setHTML('b2-voll-note',
      '<strong>Value of Lost Load (VoLL) context:</strong> ACER\'s 2023 estimate places average VoLL at €13.1/kWh for industrial customers ' +
      'and €3.2/kWh for residential. The SSI\'s R3 consequence multiplier allows us to identify which substations serve the most economically ' +
      'exposed territories. <strong>' + totalHCHR + ' substations</strong> combine capital-intensive economic fabric (R3 ≥ ' + topLower.toFixed(2) + ') with ' +
      'High or Critical risk classification — representing the highest VoLL-weighted exposure in the fleet.');

    // B.2 Narrative
    var topTierSubs = fleet.filter(function (s) {
      var v = s.modifiers && s.modifiers.R3_C_mult;
      return v >= topLower;
    });
    var topRegMap = {};
    topTierSubs.forEach(function (s) { topRegMap[s.region] = (topRegMap[s.region] || 0) + 1; });
    var topEconRegions = Object.keys(topRegMap).map(function (r) { return { name: r, n: topRegMap[r] }; })
                            .sort(function (a, b) { return b.n - a.n; }).slice(0, 3);
    var econRegionStr = topEconRegions.map(function (r) { return r.name + ' (' + r.n + ')'; }).join(', ') || '—';
    var avgEP = fleet.reduce(function (a, s) {
      return a + (((s.socio_economic && s.socio_economic.EP_rate_region) || 0));
    }, 0) / n;
    H.setHTML('b2-narrative',
      'The capital-intensive tier concentrates in <strong>' + econRegionStr + '</strong> — regions where industrial corridors ' +
      'depend on uninterrupted power for continuous processes. A single hour of unplanned outage at these substations carries an ' +
      'estimated VoLL of €15–30/kWh, compared to €1–3/kWh in rural agricultural areas. ' +
      'The fleet-wide average energy poverty rate is ' + avgEP.toFixed(1) + '%, but this masks sharp regional variation: ' +
      'Southern regions combine higher energy poverty with higher grid risk, creating a double vulnerability that the E component captures. ' +
      'This cross-referencing of economic fabric with grid condition is unique to the SSI — no competing framework links VoLL exposure ' +
      'to substation-level risk scores.');

    // B.3 Province Digital Readiness
    var provData = {};
    fleet.forEach(function (s) {
      var p = s.province;
      if (!p) return;
      if (!provData[p]) provData[p] = { subs: [], sumR7: 0, sumR: 0, sumLon: 0, sumLat: 0 };
      provData[p].subs.push(s);
      provData[p].sumR7 += (s.modifiers && s.modifiers.R7_cyber) || 0;
      provData[p].sumR += s.R_median || 0;
      provData[p].sumLon += s.lon || 0;
      provData[p].sumLat += s.lat || 0;
    });
    var provList = Object.keys(provData).map(function (p) {
      var d = provData[p];
      var nn = d.subs.length;
      return { name: p, n: nn, avgR7: d.sumR7 / nn, avgR: d.sumR / nn, lon: d.sumLon / nn, lat: d.sumLat / nn };
    });
    provList.sort(function (a, b) { return a.avgR7 - b.avgR7; });

    drawB3Map(doc, fleet);

    var r7floor = 0.985, r7ceil = 1.012;
    var rankHTML = '<div class="label-xs" style="margin-bottom:8px">Worst Digital Readiness — Top 15 ' + admL1Label(ctx.config) + '</div>' +
      '<div style="font-size:11px;color:var(--warm-grey);margin-bottom:6px">Longer bar = higher R7 = better digital infrastructure.</div>';
    provList.slice(0, 15).forEach(function (pv, idx) {
      var barPct = ((pv.avgR7 - r7floor) / (r7ceil - r7floor) * 100).toFixed(1);
      var riskTag = pv.avgR > medianR ? '<span style="color:var(--crimson);font-weight:600;font-size:10px"> ⚠ high R</span>' : '';
      rankHTML += '<div style="display:flex;align-items:center;gap:6px;font-size:11px;margin-bottom:5px">' +
        '<span style="min-width:14px;color:var(--warm-grey);font-size:10px">' + (idx + 1) + '</span>' +
        '<span style="min-width:110px;font-weight:500">' + pv.name + riskTag + '</span>' +
        '<div style="flex:1;height:5px;background:var(--cream-deep);border-radius:3px;overflow:hidden;display:flex;justify-content:flex-end">' +
          '<div style="width:' + barPct + '%;height:100%;background:' + r7Color(pv.avgR7, r7floor, r7ceil) + ';border-radius:3px"></div></div>' +
        '<span style="min-width:48px;text-align:right;font-family:Consolas,monospace;font-size:10px">' + pv.avgR7.toFixed(4) + '</span></div>';
    });
    H.setHTML('b3-ranking', rankHTML);

    // B.3 Narrative
    var worstProv = provList[0] || { name: '—', avgR7: 0 };
    var bestProv = provList[provList.length - 1] || { name: '—', avgR7: 0 };
    var dualExposed = provList.filter(function (pv) { return pv.avgR7 < medianR7 && pv.avgR > medianR; });
    H.setHTML('b3-narrative',
      admL1Cap(ctx.config) + '-level analysis reveals a clear digital divide mirroring the broader DESI pattern. ' +
      '<strong>' + worstProv.name + '</strong> has the lowest average R7 (' + worstProv.avgR7.toFixed(4) + '), while ' +
      '<strong>' + bestProv.name + '</strong> leads at ' + bestProv.avgR7.toFixed(4) + ' — a spread of ' +
      (bestProv.avgR7 - worstProv.avgR7).toFixed(4) + ' across the R7 range. ' +
      '<strong>' + dualExposed.length + ' ' + admL1Label(ctx.config).toLowerCase() + '</strong> combine below-median digital readiness with above-median grid risk, ' +
      'making them priority targets for digitalisation investment. ' +
      'The R7 modifier is intentionally narrow to reflect the current limitations of open DESI data — ' +
      'as NIS2 compliance reporting matures, future editions will expand R7\'s dynamic range and incorporate operational technology (OT) security indicators.');

    // B.4 Monthly Pulse
    var highRiskLowDigital = fleet.filter(function (s) {
      return s.classification === 'Critical' && (s.modifiers && s.modifiers.R7_cyber < medianR7);
    }).length;
    var monthYear = editionMonthYear();
    H.setHTML('b4-pulse',
      '<strong>Inaugural edition — Baseline Snapshot (' + monthYear + ').</strong> ' +
      'This edition establishes the baseline for the Cyber & Economic Exposure Monitor. Key reference points: ' +
      'fleet average R7 = ' + avgR7.toFixed(4) + ', median = ' + medianR7.toFixed(4) + '; ' +
      cyberCounts.HIGH + ' substations classified HIGH cyber-exposure; ' +
      blindSpots.length + ' blind-spot substations (High/Critical risk + below-median R7); ' +
      highRiskLowDigital + ' Critical-band substations with below-median digital readiness. ' +
      'Future editions will track deltas against this baseline.');
  });

  /* Helpers internal to Section B */
  function r7Color(r7, floor, ceil) {
    var t = Math.max(0, Math.min(1, (r7 - floor) / (ceil - floor)));
    var r = Math.round(180 - t * 100);
    var g = Math.round(60 + t * 90);
    var b = Math.round(40 + t * 20);
    return 'rgba(' + r + ',' + g + ',' + b + ',0.6)';
  }
  function drawCyberMatrix(doc, fleet, medianR7, medianR) {
    var canvas = doc.getElementById('b1-matrix');
    if (!canvas || !canvas.getContext) return;
    var dpr = window.devicePixelRatio || 1;
    canvas.width = canvas.offsetWidth * dpr;
    canvas.height = canvas.offsetHeight * dpr;
    var ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    var W = canvas.offsetWidth, Hh = canvas.offsetHeight;
    var pad = { top: 20, right: 30, bottom: 40, left: 50 };
    var r7Min = 0.98, r7Max = 1.02, rMin = 0.10, rMax = 0.85;
    function xPos(r7) { return pad.left + (r7 - r7Min) / (r7Max - r7Min) * (W - pad.left - pad.right); }
    function yPos(r)  { return pad.top + (1 - (r - rMin) / (rMax - rMin)) * (Hh - pad.top - pad.bottom); }

    // Quadrant shading
    ctx.fillStyle = 'rgba(148,25,20,0.04)';
    ctx.fillRect(pad.left, pad.top, xPos(medianR7) - pad.left, yPos(medianR) - pad.top);

    ctx.font = '600 10px DM Sans, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillStyle = 'rgba(148,25,20,0.35)';
    ctx.fillText('BLIND SPOTS', (pad.left + xPos(medianR7)) / 2, pad.top + 14);
    ctx.fillStyle = 'rgba(93,133,99,0.35)';
    ctx.fillText('DIGITALLY RESILIENT', (xPos(medianR7) + W - pad.right) / 2, Hh - pad.bottom - 6);

    // Grid lines
    ctx.strokeStyle = 'rgba(44,36,32,0.06)';
    ctx.lineWidth = 1;
    for (var g = r7Min; g <= r7Max; g += 0.005) {
      var x = xPos(g);
      ctx.beginPath(); ctx.moveTo(x, pad.top); ctx.lineTo(x, Hh - pad.bottom); ctx.stroke();
    }
    for (var g2 = rMin; g2 <= rMax; g2 += 0.1) {
      var y = yPos(g2);
      ctx.beginPath(); ctx.moveTo(pad.left, y); ctx.lineTo(W - pad.right, y); ctx.stroke();
    }
    // Median dashed lines
    ctx.setLineDash([4, 4]);
    ctx.strokeStyle = 'rgba(44,36,32,0.3)';
    ctx.lineWidth = 1;
    var mx = xPos(medianR7);
    ctx.beginPath(); ctx.moveTo(mx, pad.top); ctx.lineTo(mx, Hh - pad.bottom); ctx.stroke();
    var my = yPos(medianR);
    ctx.beginPath(); ctx.moveTo(pad.left, my); ctx.lineTo(W - pad.right, my); ctx.stroke();
    ctx.setLineDash([]);

    // Plot points
    fleet.forEach(function (s) {
      var r7v = s.modifiers && s.modifiers.R7_cyber;
      if (r7v == null || s.R_median == null) return;
      var x = xPos(r7v), y = yPos(s.R_median);
      if (x < pad.left || x > W - pad.right || y < pad.top || y > Hh - pad.bottom) return;
      ctx.beginPath();
      ctx.arc(x, y, 2.5, 0, Math.PI * 2);
      ctx.fillStyle = BAND_COLORS_RGBA[s.classification] || 'rgba(100,100,100,0.3)';
      ctx.fill();
    });

    // Axis labels
    ctx.fillStyle = '#2c2420';
    ctx.font = '500 11px DM Sans, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('← Lower digital readiness    R7 Modifier    Higher digital readiness →', W / 2, Hh - 6);
    ctx.save();
    ctx.translate(12, Hh / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('← Lower risk    R_median    Higher risk →', 0, 0);
    ctx.restore();
    // Ticks
    ctx.font = '400 10px DM Sans, sans-serif';
    ctx.fillStyle = '#888';
    ctx.textAlign = 'center';
    for (var t = r7Min; t <= r7Max; t += 0.01) {
      ctx.fillText(t.toFixed(2), xPos(t), Hh - pad.bottom + 14);
    }
    ctx.textAlign = 'right';
    for (var t2 = rMin; t2 <= rMax; t2 += 0.1) {
      ctx.fillText(t2.toFixed(1), pad.left - 6, yPos(t2) + 4);
    }
  }
  function drawB3Map(doc, fleet) {
    var canvas = doc.getElementById('b3-map');
    if (!canvas || !canvas.getContext) return;
    var dpr = window.devicePixelRatio || 1;
    canvas.width = canvas.offsetWidth * dpr;
    canvas.height = canvas.offsetHeight * dpr;
    var ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    var mW = canvas.offsetWidth, mH = canvas.offsetHeight;
    var lons = fleet.map(function (s) { return s.lon || 0; }).filter(function (v) { return v; });
    var lats = fleet.map(function (s) { return s.lat || 0; }).filter(function (v) { return v; });
    if (!lons.length) return;
    var lonMin = Math.min.apply(null, lons) - 0.3, lonMax = Math.max.apply(null, lons) + 0.3;
    var latMin = Math.min.apply(null, lats) - 0.2, latMax = Math.max.apply(null, lats) + 0.2;
    function proj(lon, lat) {
      return [30 + (lon - lonMin) / (lonMax - lonMin) * (mW - 60),
              mH - 30 - (lat - latMin) / (latMax - latMin) * (mH - 60)];
    }
    var r7floor = 0.985, r7ceil = 1.012;
    fleet.forEach(function (s) {
      if (!s.lon || !s.lat) return;
      var p = proj(s.lon, s.lat);
      ctx.beginPath();
      ctx.arc(p[0], p[1], 2.5, 0, Math.PI * 2);
      ctx.fillStyle = r7Color((s.modifiers && s.modifiers.R7_cyber) || r7floor, r7floor, r7ceil);
      ctx.fill();
    });
    // Legend
    ctx.font = '500 10px DM Sans, sans-serif';
    ctx.textAlign = 'left';
    ctx.fillStyle = '#2c2420';
    ctx.fillText('R7 Digital Readiness', 8, 14);
    var grd = ctx.createLinearGradient(8, 22, 108, 22);
    grd.addColorStop(0, r7Color(r7floor, r7floor, r7ceil));
    grd.addColorStop(1, r7Color(r7ceil, r7floor, r7ceil));
    ctx.fillStyle = grd;
    ctx.fillRect(8, 18, 100, 8);
    ctx.fillStyle = '#888';
    ctx.font = '400 9px DM Sans, sans-serif';
    ctx.fillText('Low', 8, 36);
    ctx.textAlign = 'right';
    ctx.fillText('High', 108, 36);
  }
  function admL1Label(cfg) {
    var l1 = cfg && cfg.admin && cfg.admin.l1;
    if (l1 && l1.label_short) return l1.label_short + ' regions';
    if (l1 && l1.label_en) return l1.label_en.charAt(0).toUpperCase() + l1.label_en.slice(1) + 's';
    return 'Regions';
  }
  function admL1Cap(cfg) {
    var l1 = cfg && cfg.admin && cfg.admin.l1;
    if (l1 && l1.label_short) return l1.label_short;
    if (l1 && l1.label_en) return l1.label_en.charAt(0).toUpperCase() + l1.label_en.slice(1);
    return 'Region';
  }
  function editionMonthYear() {
    var now = new Date();
    var monthNames = ['January','February','March','April','May','June','July','August','September','October','November','December'];
    return monthNames[now.getMonth()] + ' ' + now.getFullYear();
  }

  /* ══════════════════════════════════════════════════════════════════════
     SECTION C — Data Refresh & Changelog (uses window.SSI_METADATA)
     ══════════════════════════════════════════════════════════════════════ */
  CR.register('intelligence', 'data-refresh', function (ctx) {
    var meta = window.SSI_METADATA || window.SSIMetadata;
    if (!meta) return;
    var monthYear = editionMonthYear();
    var doc = ctx.doc;

    H.setHTML('sec-c-intro',
      'The SSI v4.0.2 draws on <strong>' + ((meta.stats && meta.stats.sources) || '—') + ' verified public data sources</strong> feeding ' +
      ((meta.stats && meta.stats.variables) || '—') + ' variables across ' + ((meta.stats && meta.stats.components) || '—') + ' components and ' +
      ((meta.stats && meta.stats.modifiers) || '—') +
      ' modifiers. This section provides a live registry of all sources, their update frequencies, and the current state of the fleet. ' +
      'Transparency in data vintage is central to the SSI\'s credibility.');

    // Frequency KPIs
    var freq = meta.FREQ_DISTRIBUTION || {};
    var weekly = (freq.Weekly && freq.Weekly.count) || 0;
    var monthly = (freq.Monthly && freq.Monthly.count) || 0;
    var quarterly = (freq.Quarterly && freq.Quarterly.count) || 0;
    var annual = (freq.Annual && freq.Annual.count) || 0;
    var staticC = (freq.Static && freq.Static.count) || 0;
    var derived = (freq.Derived && freq.Derived.count) || 0;

    H.setText('c-total-src', (meta.stats && meta.stats.sources) || '—');
    H.setText('c-total-vars', ((meta.stats && meta.stats.variables) || '—') + ' variables');
    H.setText('c-freq-fast', (weekly + monthly));
    H.setText('c-freq-slow', (quarterly + annual));
    H.setText('c-freq-static', (staticC + derived));

    H.setHTML('c-table-header', '<h3 style="margin:0">Data Source Registry — ' + monthYear + '</h3>');

    var sources = meta.DATA_SOURCES || [];
    var freqOrder = { Hourly: 0, Weekly: 1, Monthly: 2, Quarterly: 3, Annual: 4, Static: 5, Derived: 6, Continuous: 2, Daily: 1 };
    var sorted = sources.slice().sort(function (a, b) {
      return (freqOrder[a.freq] || 9) - (freqOrder[b.freq] || 9);
    });
    var freqColors = {
      Hourly: 'var(--sage)', Weekly: 'var(--sage)', Monthly: 'var(--sage)', Daily: 'var(--sage)',
      Quarterly: 'var(--bronze)', Annual: 'var(--bronze)', Continuous: 'var(--sage)',
      Static: 'var(--warm-grey)', Derived: 'var(--warm-grey)'
    };
    var freqBgs = {
      Hourly: 'rgba(93,133,99,0.12)', Weekly: 'rgba(93,133,99,0.12)', Monthly: 'rgba(93,133,99,0.12)', Daily: 'rgba(93,133,99,0.12)',
      Quarterly: 'rgba(184,134,58,0.12)', Annual: 'rgba(184,134,58,0.12)', Continuous: 'rgba(93,133,99,0.12)',
      Static: 'rgba(44,36,32,0.06)', Derived: 'rgba(44,36,32,0.06)'
    };
    var listHTML = sorted.map(function (s, i) {
      var fCol = freqColors[s.freq] || 'var(--warm-grey)';
      var fBg = freqBgs[s.freq] || 'rgba(44,36,32,0.06)';
      var border = i < sorted.length - 1 ? 'border-bottom:1px solid var(--card-border);' : '';
      return '<div style="display:flex;align-items:center;gap:10px;font-size:12px;padding:8px 0;' + border + '">' +
        '<span style="flex-shrink:0;font-weight:700;font-size:10px;color:var(--warm-grey);min-width:42px;font-family:Consolas,monospace">' + (s.id || '') + '</span>' +
        '<span style="flex:1;font-weight:500">' + (s.name || '') + '</span>' +
        '<span style="flex-shrink:0;font-size:10px;color:' + fCol + ';background:' + fBg + ';padding:2px 8px;border-radius:3px;font-weight:600;text-transform:uppercase">' + (s.freq || '') + '</span>' +
        '<span style="flex-shrink:0;color:var(--warm-grey);font-size:11px;min-width:90px;text-align:right">' + (s.res || s.sources || '') + '</span>' +
        '<span style="flex-shrink:0;font-weight:600;min-width:30px;text-align:right">' + (s.vars || 0) + ' var' + ((s.vars || 0) > 1 ? 's' : '') + '</span>' +
      '</div>';
    }).join('');
    H.setHTML('sec-c-source-list', listHTML);

    // Timeline
    var timelineDefs = [
      { label: 'Weekly',    sources: (freq.Weekly && freq.Weekly.sources) || [],    color: '#5d8563', note: 'OSM diffs + weather reanalysis' },
      { label: 'Monthly',   sources: (freq.Monthly && freq.Monthly.sources) || [],   color: '#5d8563', note: 'Grid load + procurement data' },
      { label: 'Quarterly', sources: (freq.Quarterly && freq.Quarterly.sources) || [], color: '#b8863a', note: 'DER registry + business + macro' },
      { label: 'Annual',    sources: (freq.Annual && freq.Annual.sources) || [],    color: '#aa4234', note: 'Core grid quality + demographics' },
      { label: 'Static',    sources: (freq.Static && freq.Static.sources) || [],    color: '#6b7280', note: 'Standards + scenarios + seismic' }
    ];
    var timelineHTML = '<div class="label-xs" style="margin-bottom:10px">Expected Update Windows</div>';
    timelineDefs.forEach(function (t) {
      if (!t.sources.length) return;
      var barW = Math.min(t.sources.length / 20 * 100, 100).toFixed(0);
      timelineHTML += '<div style="margin-bottom:10px">' +
        '<div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px">' +
          '<span style="font-weight:600">' + t.label + ' <span style="font-weight:400;color:var(--warm-grey)">(' + t.sources.length + ' sources)</span></span>' +
          '<span style="color:var(--warm-grey);font-size:11px">' + t.note + '</span></div>' +
        '<div style="height:6px;background:var(--cream-deep);border-radius:3px;overflow:hidden">' +
          '<div style="width:' + barW + '%;height:100%;background:' + t.color + ';border-radius:3px;opacity:0.7"></div></div>' +
        '<div style="font-size:11px;color:var(--warm-grey);margin-top:2px">' + t.sources.join(' · ') + '</div>' +
      '</div>';
    });
    H.setHTML('sec-c-timeline', timelineHTML);

    // Fleet Snapshot — synchronous because data is already loaded
    var fleet = (ctx.data && ctx.data.substations) || [];
    var n = fleet.length;
    if (n > 0) {
      var rVals = fleet.map(function (s) { return s.R_median || 0; }).sort(sortNum);
      var med = rVals[Math.floor(n / 2)];
      var p5  = rVals[Math.floor(n * 0.05)];
      var p95 = rVals[Math.floor(n * 0.95)];
      var mean = rVals.reduce(function (a, b) { return a + b; }, 0) / n;
      var bands = { Low: 0, Medium: 0, High: 0, Critical: 0 };
      fleet.forEach(function (s) { if (bands[s.classification] !== undefined) bands[s.classification]++; });
      var confTiers = { high: 0, medium: 0, low: 0 };
      fleet.forEach(function (s) {
        var ciRatio = (s.R_median || 0) > 0.01 ? (s.CI_width || 0) / s.R_median : 1.0;
        if (ciRatio < 0.50) confTiers.high++;
        else if (ciRatio < 0.70) confTiers.medium++;
        else confTiers.low++;
      });
      var bandBar = '';
      ['Low', 'Medium', 'High', 'Critical'].forEach(function (b) {
        var pct = (bands[b] / n * 100).toFixed(1);
        bandBar += '<div style="width:' + pct + '%;height:100%;background:' + BAND_COLORS_HEX[b] + '" title="' + b + ': ' + bands[b] + ' (' + pct + '%)"></div>';
      });
      var fleetHTML = '<div class="kpi-grid" style="margin-bottom:16px">' +
        '<div class="kpi-card"><div class="kpi-label">Fleet Size</div><div class="kpi-value" style="color:var(--ink)">' + n.toLocaleString() + '</div><div class="kpi-sub">substations scored</div></div>' +
        '<div class="kpi-card"><div class="kpi-label">Median R</div><div class="kpi-value" style="color:var(--sage)">' + med.toFixed(3) + '</div><div class="kpi-sub">P5=' + p5.toFixed(3) + ' · P95=' + p95.toFixed(3) + '</div></div>' +
        '<div class="kpi-card"><div class="kpi-label">High + Critical</div><div class="kpi-value" style="color:var(--crimson)">' + (bands.High + bands.Critical) + '</div><div class="kpi-sub">' + ((bands.High + bands.Critical) / n * 100).toFixed(1) + '% of fleet</div></div>' +
        '<div class="kpi-card"><div class="kpi-label">High Confidence</div><div class="kpi-value" style="color:var(--sage)">' + (confTiers.high / n * 100).toFixed(0) + '%</div><div class="kpi-sub">' + confTiers.high + ' subs · CI/R &lt; 0.50</div></div>' +
      '</div>';
      fleetHTML += '<div style="margin-bottom:8px"><div class="label-xs" style="margin-bottom:6px">Band Distribution</div>' +
        '<div style="height:10px;border-radius:5px;overflow:hidden;display:flex">' + bandBar + '</div>' +
        '<div style="display:flex;justify-content:space-between;font-size:11px;color:var(--warm-grey);margin-top:4px">' +
          '<span>Low ' + bands.Low + ' (' + (bands.Low / n * 100).toFixed(1) + '%)</span>' +
          '<span>Medium ' + bands.Medium + ' (' + (bands.Medium / n * 100).toFixed(1) + '%)</span>' +
          '<span>High ' + bands.High + ' (' + (bands.High / n * 100).toFixed(1) + '%)</span>' +
          '<span>Critical ' + bands.Critical + ' (' + (bands.Critical / n * 100).toFixed(1) + '%)</span>' +
        '</div></div>';
      H.setHTML('sec-c-fleet', fleetHTML);
      H.setHTML('sec-c-fleet-narrative',
        'No primary data sources have been updated since the v4.0.2 launch baseline. All <strong>' + n.toLocaleString() +
        ' substation scores remain unchanged</strong> this edition. The fleet median R of ' + med.toFixed(3) +
        ' (mean ' + mean.toFixed(3) + ') reflects a distribution skewed toward the lower bands, with ' +
        (bands.Low / n * 100).toFixed(1) + '% in Low and ' + (bands.Medium / n * 100).toFixed(1) + '% in Medium. ' +
        'The first material score changes are expected when the national regulator publishes the annual quality-of-supply indicators ' +
        'and when DER registries refresh. High-frequency sources (OSM, weather) update weekly but feed only infrastructure topology (R4) ' +
        'and thermal proxy (I5), which have minimal impact on fleet-level score distribution.');
    }

    // Changelog
    var cl = meta.CHANGELOG || [];
    var typeLabels = { 'new': 'New', 'enhanced': 'Enhanced', 'data': 'Data' };
    var typeColors = { 'new': 'var(--sage)', 'enhanced': 'var(--bronze)', 'data': 'var(--terracotta)' };
    var typeBgs = { 'new': 'rgba(93,133,99,0.12)', 'enhanced': 'rgba(184,134,58,0.12)', 'data': 'rgba(170,66,52,0.12)' };
    var clHTML = '<div style="font-size:11px;color:var(--warm-grey);margin-bottom:10px">' + cl.length + ' changes tracked across P0, P1, and P2 releases</div>';
    cl.forEach(function (c, i) {
      var col = typeColors[c.type] || 'var(--warm-grey)';
      var bg = typeBgs[c.type] || 'rgba(44,36,32,0.06)';
      var lbl = typeLabels[c.type] || c.type;
      var border = i < cl.length - 1 ? 'border-bottom:1px solid var(--card-border);' : '';
      var p2 = c.isP2 ? ' <span style="font-size:9px;color:var(--terracotta);font-weight:600">P2</span>' : '';
      clHTML += '<div style="display:flex;align-items:center;gap:10px;font-size:12px;padding:6px 0;' + border + '">' +
        '<span style="flex-shrink:0;font-weight:700;font-size:10px;color:var(--warm-grey);min-width:30px;font-family:Consolas,monospace">' + (c.id || '') + '</span>' +
        '<span style="flex-shrink:0;font-size:10px;color:' + col + ';background:' + bg + ';padding:2px 8px;border-radius:3px;font-weight:600;text-transform:uppercase;min-width:65px;text-align:center">' + lbl + '</span>' +
        '<span style="flex:1">' + (c.change || '') + p2 + '</span>' +
        '<span style="flex-shrink:0;color:var(--warm-grey);font-size:10px">' + (c.section || '') + '</span>' +
      '</div>';
    });
    H.setHTML('sec-c-changelog', clHTML);
  });

  /* ══════════════════════════════════════════════════════════════════════
     SECTION D — Thematic Deep-Dive (country-specific corridor)
     ══════════════════════════════════════════════════════════════════════ */
  CR.register('intelligence', 'deep-dive', function (ctx) {
    var fleet = (ctx.data && ctx.data.substations) || [];
    if (!fleet.length) return;
    var doc = ctx.doc;

    // Determine the corridor: read from country-config.deep_dive.region
    // Fall back: pick the region with highest mean R, or Savinjska if present.
    var corridor = (ctx.config && ctx.config.deep_dive && ctx.config.deep_dive.region) ||
                   defaultDeepDiveRegion(fleet);
    var corridorLabel = (ctx.config && ctx.config.deep_dive && ctx.config.deep_dive.label) || corridor;

    var puglia = fleet.filter(function (s) {
      return s.province === corridor || s.region === corridor;
    });
    if (!puglia.length) {
      // Try common code-vs-name conversion (e.g. SI034 vs Savinjska)
      puglia = fleet.filter(function (s) { return (s.region || '').toLowerCase() === corridor.toLowerCase(); });
    }
    if (!puglia.length) return;
    puglia.sort(function (a, b) { return b.R_median - a.R_median; });

    // D.1 KPIs
    var nTotal = puglia.length;
    var nHV = puglia.filter(function (s) { return s.voltage_kv >= 132; }).length;
    var nMV = nTotal - nHV;
    H.setText('pug-total', nTotal);
    H.setText('pug-total-sub', nHV + ' EHV · ' + nMV + ' HV');
    var bands = { Low: 0, Medium: 0, High: 0, Critical: 0 };
    puglia.forEach(function (s) { if (bands[s.classification] !== undefined) bands[s.classification]++; });
    H.setText('pug-high', bands.High + (bands.Critical ? ' + ' + bands.Critical : ''));
    H.setText('pug-high-sub', ((bands.High + bands.Critical) / nTotal * 100).toFixed(1) + '% of corridor');

    var rVals = puglia.map(function (s) { return s.R_median || 0; }).sort(sortNum);
    var medianR = rVals[Math.floor(rVals.length / 2)];
    var fleetRVals = fleet.map(function (s) { return s.R_median || 0; }).sort(sortNum);
    var fleetMedian = fleetRVals[Math.floor(fleetRVals.length / 2)];
    H.setText('pug-median', medianR.toFixed(3));
    H.setText('pug-median-sub', 'Fleet median: ' + fleetMedian.toFixed(3));

    // Worst province by mean R
    var provSums = {}, provCounts = {};
    puglia.forEach(function (s) {
      var p = s.province || 'unknown';
      if (!provSums[p]) { provSums[p] = 0; provCounts[p] = 0; }
      provSums[p] += s.R_median || 0;
      provCounts[p]++;
    });
    var provAvgs = Object.keys(provSums).map(function (p) {
      return { name: p, avg: provSums[p] / provCounts[p], n: provCounts[p] };
    });
    provAvgs.sort(function (a, b) { return b.avg - a.avg; });
    var worst = provAvgs[0] || { name: '—', avg: 0, n: 0 };
    H.setText('pug-worst-prov', worst.name);
    H.setText('pug-worst-sub', 'Avg R: ' + worst.avg.toFixed(3) + ' · ' + worst.n + ' substations');

    // D.1 Narrative
    var pctAboveFleetMedian = (puglia.filter(function (s) { return s.R_median > fleetMedian; }).length / nTotal * 100).toFixed(0);
    var deepDiveNarrative = (ctx.config && ctx.config.deep_dive && ctx.config.deep_dive.narrative) || '';
    var contextSentence = deepDiveNarrative ||
      'The corridor concentrates the country\'s industrial heartland. ' +
      'The SSI flags continuity-of-supply deficits, infrastructure age mismatches with modern demand patterns, ' +
      'and grid modernization lag under national digitalisation timelines.';
    H.setHTML('pug-narrative-d1',
      'The ' + corridorLabel + ' hosts <strong>' + nTotal + ' substations</strong> across ' + provAvgs.length + ' ' + admL1Label(ctx.config).toLowerCase() + ', ' +
      'making it the locus of this edition\'s deep-dive analysis. ' +
      'Its risk profile is concentrated in the upper bands: <strong>' + bands.High + ' substations (' +
      (bands.High / nTotal * 100).toFixed(1) + '%)</strong> are classified High' +
      (bands.Critical ? ' and <strong>' + bands.Critical + '</strong> Critical' : '') +
      ', with only <strong>' + bands.Low + '</strong> in the Low band. ' +
      pctAboveFleetMedian + '% of corridor substations score above the national fleet median of ' + fleetMedian.toFixed(3) +
      '. The corridor median R of ' + medianR.toFixed(3) + ' reflects the local risk profile. ' + contextSentence);

    // D.2 Map
    drawDeepDiveMap(doc, puglia, fleet, corridor, provAvgs);

    // D.2 Table — top 10
    var top10 = puglia.slice(0, 10);
    var tbody = doc.getElementById('puglia-tbody');
    if (tbody) {
      var thStyle = 'padding:8px 10px;border-bottom:1px solid var(--card-border);vertical-align:top;';
      var numStyle = thStyle + 'text-align:right;font-family:"Playfair Display",serif;font-weight:500;';
      tbody.innerHTML = top10.map(function (s) {
        var bCol = BAND_COLORS_HEX[s.classification] || 'var(--ink)';
        var alertStr = s.alert_components ? s.alert_components.join(', ') : '—';
        var c = s.components || {};
        return '<tr>' +
          '<td style="' + thStyle + 'font-weight:500">' + (s.name || '') + '</td>' +
          '<td style="' + thStyle + '">' + (s.province || '') + '</td>' +
          '<td style="' + numStyle + 'color:' + bCol + ';font-weight:600">' + ((s.R_median != null) ? s.R_median.toFixed(3) : '—') + '</td>' +
          '<td style="' + thStyle + 'color:' + bCol + ';font-weight:600">' + (s.classification || '') + '</td>' +
          '<td style="' + numStyle + '">' + ((c.C != null) ? c.C.toFixed(3) : '—') + '</td>' +
          '<td style="' + numStyle + '">' + ((c.V != null) ? c.V.toFixed(3) : '—') + '</td>' +
          '<td style="' + numStyle + '">' + ((c.I != null) ? c.I.toFixed(3) : '—') + '</td>' +
          '<td style="' + numStyle + '">' + ((c.E != null) ? c.E.toFixed(3) : '—') + '</td>' +
          '<td style="' + numStyle + '">' + ((c.S != null) ? c.S.toFixed(3) : '—') + '</td>' +
          '<td style="' + numStyle + '">' + ((c.T != null) ? c.T.toFixed(3) : '—') + '</td>' +
          '<td style="' + thStyle + 'color:var(--crimson);font-weight:600">' + alertStr + '</td></tr>';
      }).join('') +
        '<tr><td colspan="11" style="text-align:center;color:var(--warm-grey);font-style:italic;font-size:12px;padding:8px 10px">… ' +
        (nTotal - 10) + ' additional substations — <a href="map.html" style="color:var(--terracotta)">explore full corridor in Digital Twin →</a></td></tr>';
    }

    // D.3 Component analysis
    var compDefs = [
      { key: 'C', label: 'Continuity',     w: 0.30, color: '#941914' },
      { key: 'I', label: 'Infrastructure', w: 0.25, color: '#5d8563' },
      { key: 'S', label: 'Saturation',     w: 0.20, color: '#b8863a' },
      { key: 'V', label: 'Voltage',        w: 0.10, color: '#aa4234' },
      { key: 'E', label: 'Economic',       w: 0.10, color: '#3b9eff' },
      { key: 'T', label: 'Transition',     w: 0.05, color: '#22d3ee' }
    ];
    function avgComp(subs, key) {
      return subs.reduce(function (a, s) { return a + ((s.components && s.components[key]) || 0); }, 0) / subs.length;
    }
    function avgMod(subs, key) {
      return subs.reduce(function (a, s) { return a + ((s.modifiers && s.modifiers[key]) || 0); }, 0) / subs.length;
    }
    var compBarsHTML = '<div class="label-xs" style="margin-bottom:10px">Component Averages — ' + corridorLabel + ' vs Fleet</div>';
    compDefs.forEach(function (c) {
      var pugAvg = avgComp(puglia, c.key);
      var fltAvg = avgComp(fleet, c.key);
      var pugPct = Math.min(pugAvg / c.w * 100, 100).toFixed(0);
      var fltPct = Math.min(fltAvg / c.w * 100, 100).toFixed(0);
      var delta = ((pugAvg - fltAvg) / fltAvg * 100).toFixed(0);
      var sign = delta > 0 ? '+' : '';
      compBarsHTML += '<div style="margin-bottom:10px">' +
        '<div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px">' +
          '<span style="font-weight:500">' + c.key + ' — ' + c.label + '</span>' +
          '<span style="color:var(--warm-grey)">' + pugAvg.toFixed(3) + ' vs ' + fltAvg.toFixed(3) + ' (' + sign + delta + '%)</span></div>' +
        '<div style="height:6px;background:var(--cream-deep);border-radius:3px;overflow:hidden;position:relative">' +
          '<div style="position:absolute;width:' + fltPct + '%;height:100%;background:rgba(44,36,32,0.12);border-radius:3px"></div>' +
          '<div style="position:absolute;width:' + pugPct + '%;height:100%;background:' + c.color + ';border-radius:3px;opacity:0.75"></div>' +
        '</div></div>';
    });
    H.setHTML('puglia-comp-bars', compBarsHTML);

    var modDefs = [
      { key: 'R3_C_mult',      label: 'R3 Consequence',   range: '[0.70, 1.30]' },
      { key: 'R4_F_topo',      label: 'R4 Graph Crit.',   range: '[0.80, 1.35]' },
      { key: 'R6_restoration', label: 'R6a Restoration', range: '[0.90, 1.10]' },
      { key: 'R6_seismic',     label: 'R6b Seismic',      range: '[1.00, 1.25]' },
      { key: 'R7_cyber',       label: 'R7 Digital Read.', range: '[0.99, 1.05]' }
    ];
    var modBarsHTML = '<div class="label-xs" style="margin-bottom:10px">Modifier Averages — ' + corridorLabel + ' vs Fleet</div>';
    modDefs.forEach(function (m) {
      var pugAvg = avgMod(puglia, m.key);
      var fltAvg = avgMod(fleet, m.key);
      var dir = pugAvg > 1.01 ? '↑' : pugAvg < 0.99 ? '↓' : '→';
      var col = pugAvg > fltAvg * 1.01 ? 'var(--crimson)' : pugAvg < fltAvg * 0.99 ? 'var(--sage)' : 'var(--warm-grey)';
      modBarsHTML += '<div style="display:flex;align-items:center;gap:8px;font-size:12px;margin-bottom:8px">' +
        '<span style="min-width:120px;font-weight:500">' + m.label + '</span>' +
        '<span style="color:' + col + ';font-weight:600;min-width:45px">' + pugAvg.toFixed(3) + '</span>' +
        '<span style="color:var(--warm-grey);min-width:55px">fleet ' + fltAvg.toFixed(3) + '</span>' +
        '<span style="font-size:11px;color:' + col + '">' + dir + '</span></div>';
    });
    H.setHTML('puglia-mod-bars', modBarsHTML);

    // D.3 Narrative
    var compRanked = compDefs.slice().sort(function (a, b) {
      return (avgComp(puglia, b.key) / b.w) - (avgComp(puglia, a.key) / a.w);
    });
    var c1 = compRanked[0], c2 = compRanked[1];
    H.setHTML('pug-narrative-d3',
      'The dominant risk driver across the ' + corridorLabel + ' corridor is <strong>' + c1.key + ' (' + c1.label + ')</strong>, averaging ' +
      avgComp(puglia, c1.key).toFixed(3) + ' against a fleet average of ' + avgComp(fleet, c1.key).toFixed(3) + ' — occupying ' +
      (avgComp(puglia, c1.key) / c1.w * 100).toFixed(0) + '% of its weight ceiling (w = ' + c1.w.toFixed(2) + '). ' +
      'The second contributor is <strong>' + c2.key + ' (' + c2.label + ')</strong> at ' +
      avgComp(puglia, c2.key).toFixed(3) + ' vs fleet ' + avgComp(fleet, c2.key).toFixed(3) + ' (' + (avgComp(puglia, c2.key) / c2.w * 100).toFixed(0) + '% of ceiling). ' +
      'Among modifiers, the R3 consequence multiplier averages ' + avgMod(puglia, 'R3_C_mult').toFixed(3) +
      ' (fleet: ' + avgMod(fleet, 'R3_C_mult').toFixed(3) + '), reflecting the socio-economic exposure of the corridor. ' +
      'The R6b seismic modifier averages ' + avgMod(puglia, 'R6_seismic').toFixed(3) + ', capturing the local seismic exposure — ' +
      'a dimension invisible to every competing framework.');

    // D.4 Province breakdown
    var provHTML = '<div class="label-xs" style="margin-bottom:10px">' + admL1Cap(ctx.config) + ' Risk Profile — Sorted by Mean R</div>' +
      '<div style="font-size:11px;color:var(--warm-grey);margin-bottom:8px">Longer bar = lower R = better resilience.</div>';
    provAvgs.forEach(function (pv) {
      var provSubs = puglia.filter(function (s) { return s.province === pv.name; });
      var provBands = { Low: 0, Medium: 0, High: 0, Critical: 0 };
      provSubs.forEach(function (s) { if (provBands[s.classification] !== undefined) provBands[s.classification]++; });
      var barPct = ((1 - pv.avg) * 100).toFixed(1);
      var col = pv.avg > 0.6 ? '#941914' : pv.avg > 0.5 ? '#aa4234' : '#b8863a';
      provHTML += '<div style="margin-bottom:12px">' +
        '<div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px">' +
          '<span style="font-weight:600">' + pv.name + '</span>' +
          '<span style="color:var(--warm-grey)">' + pv.n + ' subs · avg R = ' + pv.avg.toFixed(3) +
          ' · H:' + provBands.High + (provBands.Critical ? ' C:' + provBands.Critical : '') + ' M:' + provBands.Medium + '</span></div>' +
        '<div style="height:8px;background:var(--cream-deep);border-radius:4px;overflow:hidden;display:flex;justify-content:flex-end">' +
          '<div style="width:' + barPct + '%;height:100%;background:' + col + ';border-radius:4px;opacity:0.7"></div>' +
        '</div></div>';
    });
    H.setHTML('puglia-province-bars', provHTML);

    // D.4 Narrative
    var bestProv = provAvgs[provAvgs.length - 1] || worst;
    H.setHTML('pug-narrative-d4',
      'The ' + admL1Label(ctx.config).toLowerCase() + '-level breakdown reveals significant intra-regional variation. <strong>' + worst.name + '</strong> leads with a mean R of ' +
      worst.avg.toFixed(3) + ' across ' + worst.n + ' substations, while <strong>' + bestProv.name + '</strong> scores ' +
      bestProv.avg.toFixed(3) + ' — a spread of ' + (worst.avg - bestProv.avg).toFixed(3) +
      ' within a single corridor. The SSI\'s substation-level granularity reveals that the ' + corridorLabel + ' is not uniformly stressed ' +
      'but contains distinct sub-corridors of concentrated risk — precisely the kind of spatial pattern that investment planning requires.');

    // D.5 Implications
    var pugAbove065 = puglia.filter(function (s) { return s.R_median >= 0.65; }).length;
    H.setHTML('pug-narrative-d5',
      '<strong>' + pugAbove065 + ' ' + corridorLabel + ' substations</strong> score R ≥ 0.650, placing them in the upper quartile of national risk. ' +
      'For NEPN / national digital plan / RRP investment prioritisation, this analysis identifies the ' + worst.name + ' sub-corridor as the highest-priority target — ' +
      'where DER deployment is accelerating against ageing infrastructure with above-average continuity deficits and significant socio-economic exposure. ' +
      'The SSI\'s silo-breaking approach reveals what no single-discipline framework can: that these substations matter not only because of their engineering condition, ' +
      'but because the communities they serve are disproportionately vulnerable to disruption. ' +
      'This is precisely the anticipatory grid planning capability that the SSI was built to provide.');
  });
  function defaultDeepDiveRegion(fleet) {
    var regSums = {}, regCounts = {};
    fleet.forEach(function (s) {
      var r = s.region;
      if (!r) return;
      regSums[r] = (regSums[r] || 0) + (s.R_median || 0);
      regCounts[r] = (regCounts[r] || 0) + 1;
    });
    var best = null, bestAvg = -1;
    Object.keys(regSums).forEach(function (r) {
      var avg = regSums[r] / regCounts[r];
      if (avg > bestAvg) { bestAvg = avg; best = r; }
    });
    return best || 'Savinjska';
  }
  function drawDeepDiveMap(doc, puglia, fleet, corridor, provAvgs) {
    var canvas = doc.getElementById('puglia-map');
    if (!canvas || !canvas.getContext) return;
    var dpr = window.devicePixelRatio || 1;
    canvas.width = canvas.offsetWidth * dpr;
    canvas.height = canvas.offsetHeight * dpr;
    var ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    var W = canvas.offsetWidth, Hh = canvas.offsetHeight;
    var lons = puglia.map(function (s) { return s.lon || 0; }).filter(function (v) { return v; });
    var lats = puglia.map(function (s) { return s.lat || 0; }).filter(function (v) { return v; });
    if (!lons.length) return;
    var minLon = Math.min.apply(null, lons) - 0.15, maxLon = Math.max.apply(null, lons) + 0.15;
    var minLat = Math.min.apply(null, lats) - 0.1, maxLat = Math.max.apply(null, lats) + 0.1;
    var lonSpan = maxLon - minLon, latSpan = maxLat - minLat;
    function proj(lon, lat) {
      return [40 + (lon - minLon) / lonSpan * (W - 80),
              Hh - 40 - (lat - minLat) / latSpan * (Hh - 80)];
    }
    fleet.forEach(function (s) {
      if (!s.lon || !s.lat) return;
      if (s.lon >= minLon && s.lon <= maxLon && s.lat >= minLat && s.lat <= maxLat && s.region !== corridor) {
        var p = proj(s.lon, s.lat);
        ctx.beginPath();
        ctx.arc(p[0], p[1], 2, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(44,36,32,0.08)';
        ctx.fill();
      }
    });
    puglia.forEach(function (s) {
      if (!s.lon || !s.lat) return;
      var p = proj(s.lon, s.lat);
      var r = s.classification === 'Critical' ? 6 : s.classification === 'High' ? 4.5 : 3.5;
      ctx.beginPath();
      ctx.arc(p[0], p[1], r, 0, Math.PI * 2);
      ctx.fillStyle = BAND_COLORS_HEX[s.classification] || '#999';
      ctx.globalAlpha = 0.7;
      ctx.fill();
      ctx.globalAlpha = 1;
      ctx.strokeStyle = BAND_COLORS_HEX[s.classification] || '#999';
      ctx.lineWidth = 0.5;
      ctx.stroke();
    });
    ctx.font = '600 11px DM Sans, sans-serif';
    ctx.fillStyle = 'rgba(44,36,32,0.5)';
    ctx.textAlign = 'center';
    provAvgs.forEach(function (pv) {
      var provSubs = puglia.filter(function (s) { return s.province === pv.name; });
      if (!provSubs.length) return;
      var avgLon = provSubs.reduce(function (a, s) { return a + s.lon; }, 0) / provSubs.length;
      var avgLat = provSubs.reduce(function (a, s) { return a + s.lat; }, 0) / provSubs.length;
      var p = proj(avgLon, avgLat);
      ctx.fillText(pv.name, p[0], p[1] - 12);
    });
  }

  /* ══════════════════════════════════════════════════════════════════════
     SECTION E — Regional Risk Ranking (European context narrative)
     ══════════════════════════════════════════════════════════════════════ */
  CR.register('intelligence', 'eu-context', function (ctx) {
    var fleet = (ctx.data && ctx.data.substations) || [];
    if (!fleet.length) return;

    var corridor = (ctx.config && ctx.config.deep_dive && ctx.config.deep_dive.region) ||
                   defaultDeepDiveRegion(fleet);
    var corridorLabel = (ctx.config && ctx.config.deep_dive && ctx.config.deep_dive.label) || corridor;
    var puglia = fleet.filter(function (s) { return s.region === corridor; });

    // Key insight: C component > 70% of weight ceiling
    var highC = puglia.filter(function (s) { return (s.components && s.components.C > 0.21); }).length;
    var avgC_pug = puglia.length ? puglia.reduce(function (a, s) { return a + ((s.components && s.components.C) || 0); }, 0) / puglia.length : 0;
    var avgC_fleet = fleet.reduce(function (a, s) { return a + ((s.components && s.components.C) || 0); }, 0) / fleet.length;
    var cRatio = avgC_fleet > 0 ? (avgC_pug / avgC_fleet).toFixed(1) : '—';

    H.setHTML('eu-insight',
      '<strong>This month\'s key insight:</strong> The ' + corridorLabel + ' corridor deep-dive shows <strong>' + highC +
      ' substations</strong> (of ' + puglia.length + ') with C-component above 70% of its weight ceiling — ' +
      'indicating continuity-of-supply performance consistent with rural territory classification. ' +
      'The corridor\'s average C of ' + avgC_pug.toFixed(3) + ' is <strong>' + cRatio + '× the fleet average</strong> of ' +
      avgC_fleet.toFixed(3) + '. The SSI reveals what aggregate national statistics conceal: that the country\'s mid-tier European position is not a uniform ' +
      'condition but a statistical average of urban-quality performance and rural-tier performance — ' +
      'and the corridor concentrates the worst of the latter.');

    // Regional ranking
    var regData = {};
    fleet.forEach(function (s) {
      var r = s.region;
      if (!r) return;
      if (!regData[r]) regData[r] = { subs: [], sumR: 0, bands: { Low: 0, Medium: 0, High: 0, Critical: 0 } };
      regData[r].subs.push(s);
      regData[r].sumR += s.R_median || 0;
      if (regData[r].bands[s.classification] !== undefined) regData[r].bands[s.classification]++;
    });
    var regions = Object.keys(regData).map(function (r) {
      var d = regData[r];
      return { name: r, n: d.subs.length, avgR: d.sumR / d.subs.length, bands: d.bands };
    });
    regions.sort(function (a, b) { return b.avgR - a.avgR; });
    var fleetAvgR = fleet.reduce(function (a, s) { return a + (s.R_median || 0); }, 0) / fleet.length;

    var html = '<div style="font-size:11px;color:var(--warm-grey);margin-bottom:8px">Longer bar = lower R = better resilience. Sorted worst → best.</div>';
    regions.forEach(function (reg, idx) {
      var isFocus = reg.name === corridor;
      var barPct = ((1 - reg.avgR) * 100).toFixed(1);
      var col = reg.avgR > 0.50 ? '#941914' : reg.avgR > 0.40 ? '#aa4234' : reg.avgR > 0.35 ? '#b8863a' : '#5d8563';
      var highlight = isFocus ? 'background:rgba(148,25,20,0.04);border-left:3px solid var(--crimson);padding-left:8px;border-radius:4px;' : '';
      var total = reg.n;
      var bandBar = '';
      ['Critical', 'High', 'Medium', 'Low'].forEach(function (b) {
        if (reg.bands[b] > 0) {
          var w = (reg.bands[b] / total * 100).toFixed(1);
          bandBar += '<div style="width:' + w + '%;height:100%;background:' + BAND_COLORS_HEX[b] + '" title="' + b + ': ' + reg.bands[b] + '"></div>';
        }
      });
      html += '<div style="margin-bottom:8px;' + highlight + '">' +
        '<div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px;align-items:baseline">' +
          '<span style="font-weight:' + (isFocus ? '700' : '500') + ';min-width:180px">' +
            '<span style="color:var(--warm-grey);font-size:10px;margin-right:6px">#' + (idx + 1) + '</span>' +
            reg.name + '</span>' +
          '<span style="color:var(--warm-grey);font-size:11px">' + reg.n + ' subs · avg R = ' + reg.avgR.toFixed(3) +
          ' · H:' + reg.bands.High + (reg.bands.Critical ? ' C:' + reg.bands.Critical : '') + '</span></div>' +
        '<div style="display:flex;gap:4px;align-items:center">' +
          '<div style="flex:1;height:6px;background:var(--cream-deep);border-radius:3px;overflow:hidden;display:flex;justify-content:flex-end">' +
            '<div style="width:' + barPct + '%;height:100%;background:' + col + ';border-radius:3px;opacity:0.7"></div>' +
          '</div>' +
          '<div style="width:80px;height:6px;border-radius:3px;overflow:hidden;display:flex">' + bandBar + '</div>' +
        '</div></div>';
    });
    H.setHTML('eu-regional-ranking', html);

    // Ranking narrative
    var focusRank = regions.findIndex(function (r) { return r.name === corridor; }) + 1;
    var top3 = regions.slice(0, 3).map(function (r) { return r.name; });
    var bot3 = regions.slice(-3).reverse().map(function (r) { return r.name; });
    var aboveAvg = regions.filter(function (r) { return r.avgR > fleetAvgR; }).length;
    H.setHTML('eu-ranking-narrative',
      'The ' + corridorLabel + ' ranks <strong>#' + focusRank + ' of ' + regions.length + ' ' + admL1Label(ctx.config).toLowerCase() + '</strong> by mean R_median, ' +
      'placing it among the upper tier of national risk. ' +
      'The three most stressed are ' + top3.join(', ') + ', while the three most resilient are ' + bot3.join(', ') + '. ' +
      aboveAvg + ' of ' + regions.length + ' score above the fleet average of ' + fleetAvgR.toFixed(3) + '. ' +
      'This ranking — possible only because the SSI scores every substation individually rather than relying on aggregate DSO or national statistics — ' +
      'reveals the true spatial distribution of grid stress. It is precisely this substation-level granularity that positions the SSI ' +
      'as a tool for investment prioritisation: not treating entire regions as monoliths, but identifying the specific corridors within each that demand attention.');
  });

  /* ══════════════════════════════════════════════════════════════════════
     SECTION F — SSI Enhanced Neural Network (rotating monthly topic)
     ══════════════════════════════════════════════════════════════════════ */
  CR.register('intelligence', 'enn', function (ctx) {
    var now = new Date();
    var seed = now.getFullYear() * 100 + (now.getMonth() + 1);
    var topicIdx = seededIndex(seed + 7777, ENN_TOPICS.length);
    var nextSeed = now.getFullYear() * 100 + (now.getMonth() + 2 > 12 ? 1 : now.getMonth() + 2);
    var nextIdx = seededIndex(nextSeed + 7777, ENN_TOPICS.length);
    var topic = ENN_TOPICS[topicIdx];
    var nextTopic = ENN_TOPICS[nextIdx];
    var monthYear = editionMonthYear();

    // Layer navigation
    var navHTML = '';
    ENN_LAYERS.forEach(function (l) {
      var isActive = l.n === topic.layer;
      navHTML += '<div style="flex:1;min-width:120px;padding:8px 12px;border-radius:var(--radius);border:2px solid ' +
        (isActive ? l.color : 'var(--card-border)') + ';background:' +
        (isActive ? l.color : '#fff') + ';color:' + (isActive ? '#fff' : 'var(--warm-grey)') +
        ';font-size:11px;text-align:center;transition:all 0.2s">' +
        '<div style="font-weight:700">' + l.label + '</div>' +
        '<div style="font-size:10px;opacity:0.7;margin-top:2px">' + l.desc + '</div></div>';
    });
    H.setHTML('enn-layer-nav', navHTML);

    var activeLayer = ENN_LAYERS.filter(function (l) { return l.n === topic.layer; })[0];
    var layerColor = activeLayer ? activeLayer.color : 'var(--ink)';
    var conceptsHTML = topic.concepts.map(function (c) {
      return '<div style="display:flex;align-items:baseline;gap:8px;font-size:12px;padding:6px 0;border-bottom:1px solid rgba(44,36,32,0.04)">' +
        '<span style="color:' + layerColor + ';font-weight:700;flex-shrink:0">→</span>' +
        '<span>' + c + '</span></div>';
    }).join('');

    H.setHTML('enn-topic',
      '<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px">' +
        '<span style="font-size:10px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;background:' + layerColor + ';color:#fff;padding:4px 10px;border-radius:3px">Layer ' + topic.layer + '</span>' +
        '<span style="font-size:10px;color:var(--warm-grey);letter-spacing:0.05em">' + topic.ref + ' · ' + monthYear + '</span></div>' +
      '<h3 style="margin:0 0 4px;font-size:17px">' + topic.title + '</h3>' +
      '<p style="font-size:12px;color:var(--warm-grey);margin:0 0 16px;font-style:italic">' + topic.subtitle + '</p>' +
      '<p style="font-size:13px;line-height:1.7;margin-bottom:16px">' + topic.body + '</p>' +
      '<div class="card" style="border-left:3px solid ' + layerColor + ';margin-bottom:16px">' +
        '<div style="font-size:11px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:' + layerColor + ';margin-bottom:8px">Key Concepts</div>' +
        conceptsHTML +
      '</div>');

    // Live SSI Data Connection — compute from already-loaded data
    var fleet = (ctx.data && ctx.data.substations) || [];
    var n = fleet.length;
    if (n > 0) {
      var avgR = fleet.reduce(function (a, s) { return a + (s.R_median || 0); }, 0) / n;
      var avgCI = fleet.reduce(function (a, s) { return a + (s.CI_width || 0); }, 0) / n;
      var highCrit = fleet.filter(function (s) { return s.classification === 'High' || s.classification === 'Critical'; }).length;
      var compAvgs = {};
      ['C', 'V', 'I', 'E', 'S', 'T'].forEach(function (k) {
        compAvgs[k] = fleet.reduce(function (a, s) { return a + ((s.components && s.components[k]) || 0); }, 0) / n;
      });
      var statHTML = '';
      if (topic.layer === 1) {
        statHTML = 'The SSI Index currently scores <strong>' + n.toLocaleString() + ' substations</strong>. ' +
          'Fleet mean R = ' + avgR.toFixed(3) + ', with an average confidence interval width of ' + avgCI.toFixed(3) +
          ' from 10,000 MC iterations per substation. The dominant component is C (Continuity) at avg ' + compAvgs.C.toFixed(3) +
          ' / 0.30 ceiling (' + (compAvgs.C / 0.30 * 100).toFixed(0) + '% utilisation).';
      } else if (topic.layer === 2) {
        var avgR3 = fleet.reduce(function (a, s) { return a + ((s.modifiers && s.modifiers.R3_C_mult) || 0); }, 0) / n;
        statHTML = 'Across the ' + n.toLocaleString() + '-substation fleet, the average consequence multiplier (R3) is ' +
          avgR3.toFixed(3) + ', indicating significant socio-economic exposure. ' +
          highCrit + ' substations (' + (highCrit / n * 100).toFixed(1) + '%) are classified High or Critical — ' +
          'these are the highest-priority candidates for BESS deployment.';
      } else if (topic.layer === 3) {
        statHTML = 'The training set comprises ' + n.toLocaleString() + ' substations with complete feature vectors. ' +
          'Average CI_width of ' + avgCI.toFixed(3) + ' across the fleet provides the uncertainty ground truth that the neural network\'s ' +
          'quantile regression heads must calibrate against. The fleet\'s risk distribution — ' +
          fleet.filter(function (s) { return s.classification === 'Low'; }).length + ' Low, ' +
          fleet.filter(function (s) { return s.classification === 'Medium'; }).length + ' Medium, ' +
          fleet.filter(function (s) { return s.classification === 'High'; }).length + ' High, ' +
          fleet.filter(function (s) { return s.classification === 'Critical'; }).length + ' Critical — ensures balanced training across all risk bands.';
      } else if (topic.layer === 4) {
        var regSet = {}, provSet = {};
        fleet.forEach(function (s) { regSet[s.region] = true; provSet[s.province] = true; });
        statHTML = 'Coverage: ' + n.toLocaleString() + ' substations across ' +
          Object.keys(regSet).length + ' regions and ' + Object.keys(provSet).length + ' sub-regions. ' +
          'This serves as the reference benchmark for the Coverage Quality Scorecard: any country achieving comparable ' +
          'granularity (DCI > 0.70) qualifies for production-grade valuations on the commercial platform.';
      } else {
        statHTML = 'The fleet of ' + n.toLocaleString() + ' substations generates the full analytical depth that the platform ' +
          'delivers: R_median, P5/P95 bounds, 6 component scores, 5 modifier impacts, band classification, and confidence tier — ' +
          'all computed per substation per BESS configuration.';
      }
      H.setHTML('enn-data-link',
        '<div class="card" style="border-left:3px solid var(--sage);background:var(--cream)">' +
          '<div style="font-size:11px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:var(--sage);margin-bottom:6px">Live SSI Data Connection</div>' +
          '<p style="font-size:13px;line-height:1.7;margin:0">' + statHTML + '</p></div>');
    }

    var nextLayer = ENN_LAYERS.filter(function (l) { return l.n === nextTopic.layer; })[0];
    H.setHTML('enn-next',
      '<p style="font-size:13px;line-height:1.7;margin:0"><strong>Coming next month:</strong> ' +
      '<span style="font-size:10px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;background:' + nextLayer.color +
      ';color:#fff;padding:2px 8px;border-radius:3px;margin:0 4px">Layer ' + nextTopic.layer + '</span> ' +
      nextTopic.title + ' — <em>' + nextTopic.subtitle + '</em></p>');
  });

  /* ══════════════════════════════════════════════════════════════════════
     SECTION G — Looking Ahead (next edition + data refresh + spotlight)
     ══════════════════════════════════════════════════════════════════════ */
  CR.register('intelligence', 'looking-ahead', function (ctx) {
    var now = new Date();
    var month = now.getMonth();
    var year = now.getFullYear();
    var monthNames = ['January','February','March','April','May','June','July','August','September','October','November','December'];

    var d = now.getDate();
    var addMonths = d >= 21 ? 2 : 1;
    var pubMonth0 = month + addMonths;
    var nextYear = year + Math.floor(pubMonth0 / 12);
    var nextMonth = ((pubMonth0 % 12) + 12) % 12;

    // Edition number from country config (or default)
    var anchorOffset = (ctx.config && ctx.config.edition_anchor_month_offset != null) ? ctx.config.edition_anchor_month_offset : 5;
    var nextEditionNum = (nextYear - 2026) * 12 + (nextMonth + 1) - anchorOffset;
    var nextEdition = String(Math.max(2, nextEditionNum)).padStart(2, '0');
    var nextSeed = nextYear * 100 + (nextMonth + 1);

    // Deep-dive rotation (from country config; falls back to Slovenia-style 12-month placeholder set if missing)
    var deepDives = (ctx.config && ctx.config.deep_dive_rotation) || DEFAULT_DEEP_DIVES;
    var nextDiveIdx = seededIndex(nextSeed + 3333, deepDives.length);
    var nextDive = deepDives[nextDiveIdx];
    var nextRegion = nextDive.region || nextDive.name || '—';
    var nextTheme = nextDive.theme || nextDive.title || ('Deep-Dive: ' + nextRegion);
    var nextDetail = nextDive.context_detail || nextDive.contextDetail || nextDive.context || '';

    H.setHTML('g-next-edition',
      '<span class="label-xs" style="color:var(--bronze);margin-bottom:8px;display:block">Next Month — Edition ' + nextEdition + '</span>' +
      '<h3 style="margin-top:0;font-size:15px">' + nextTheme + '</h3>' +
      '<p style="font-size:13px;color:var(--warm-grey);line-height:1.6;margin:8px 0">' +
      'Deep-dive into ' + nextRegion + '\'s grid risk profile — substation map, component analysis, ' + admL1Label(ctx.config).toLowerCase() + ' breakdown. ' +
      (nextDetail ? 'European Context Card: ' + nextDetail + '.' : '') + '</p>');

    // Data refresh card
    var meta = window.SSI_METADATA || window.SSIMetadata;
    if (meta) {
      var currentQ = Math.floor(month / 3) + 1;
      var nextQ = currentQ >= 4 ? 1 : currentQ + 1;
      var nextQYear = currentQ >= 4 ? year + 1 : year;
      var qLabels = { 1: 'Q1', 2: 'Q2', 3: 'Q3', 4: 'Q4' };
      var qtrSources = (meta.FREQ_DISTRIBUTION && meta.FREQ_DISTRIBUTION.Quarterly && meta.FREQ_DISTRIBUTION.Quarterly.sources) ?
        meta.FREQ_DISTRIBUTION.Quarterly.sources.join(', ') : 'none';
      var qtrCount = (meta.FREQ_DISTRIBUTION && meta.FREQ_DISTRIBUTION.Quarterly) ? (meta.FREQ_DISTRIBUTION.Quarterly.count || 0) : 0;
      var annualHighImpact = (meta.DATA_SOURCES || []).filter(function (s) { return s.freq === 'Annual'; })
        .sort(function (a, b) { return (b.vars || 0) - (a.vars || 0); })[0];
      H.setHTML('g-data-refresh',
        '<span class="label-xs" style="color:var(--sage);margin-bottom:8px;display:block">Next Data Refresh</span>' +
        '<h3 style="margin-top:0;font-size:15px">' + qLabels[nextQ] + ' ' + nextQYear + ' — ' + qtrCount + ' Quarterly Sources</h3>' +
        '<p style="font-size:13px;color:var(--warm-grey);line-height:1.6;margin:8px 0">' +
        '<strong>' + qtrSources + '</strong> are due for refresh in ' + qLabels[nextQ] + '. ' +
        'Impact: DER registry (T1), business fabric indicators (E2), macro-economic data. ' +
        'Highest-impact annual source pending: <strong>' + (annualHighImpact ? annualHighImpact.name : 'TBD') + '</strong> (' +
        (annualHighImpact ? annualHighImpact.vars : '?') + ' variables → ' + (annualHighImpact ? annualHighImpact.feeds : '') + ').</p>');
    }

    // Spotlight (rotating insight)
    var fleet = (ctx.data && ctx.data.substations) || [];
    if (fleet.length) {
      var seed = year * 100 + (month + 1);
      var spotlights = buildSpotlights(fleet);
      var spotIdx = seededIndex(seed + 5555, spotlights.length);
      var spot = spotlights[spotIdx];
      H.setHTML('g-spotlight',
        '<span class="label-xs" style="color:var(--crimson);margin-bottom:8px;display:block">Fleet Spotlight</span>' +
        '<h3 style="margin-top:0;font-size:15px">' + spot.title + '</h3>' +
        '<p style="font-size:13px;color:var(--warm-grey);line-height:1.6;margin:8px 0">' + spot.body + '</p>');

      H.setHTML('g-closing',
        'Edition ' + nextEdition + ' will be published on the second Thursday of ' + monthNames[nextMonth] + ' ' + nextYear +
        '. Deep-dive region: <strong>' + nextRegion + '</strong>. ' +
        'To ensure you receive it, confirm your subscription segment (General / Institutional / Academic) by email to ssi_index@ikenga.eu.');
    }
  });

  function buildSpotlights(fleet) {
    var n = fleet.length;
    var spots = [];

    // 1. Highest risk concentration by province
    var provData = {};
    fleet.forEach(function (s) {
      var p = s.province;
      if (!p) return;
      if (!provData[p]) provData[p] = { subs: [], sumR: 0, highCrit: 0 };
      provData[p].subs.push(s);
      provData[p].sumR += s.R_median || 0;
      if (s.classification === 'High' || s.classification === 'Critical') provData[p].highCrit++;
    });
    var provList = Object.keys(provData).map(function (p) {
      var d = provData[p];
      return { name: p, n: d.subs.length, avg: d.sumR / d.subs.length, highCrit: d.highCrit, pctHC: d.highCrit / d.subs.length };
    });
    provList.sort(function (a, b) { return b.pctHC - a.pctHC; });
    var riskiest = provList[0];
    if (riskiest) {
      spots.push({
        title: riskiest.name + ': Highest Risk Concentration',
        body: riskiest.name + ' has the highest concentration of High/Critical substations: <strong>' +
          riskiest.highCrit + ' of ' + riskiest.n + ' (' + (riskiest.pctHC * 100).toFixed(0) + '%)</strong> are in the upper risk bands — ' +
          'avg R = ' + riskiest.avg.toFixed(3) + '. This makes it the most acute risk corridor in the fleet.'
      });
    }

    // 2. Widest uncertainty
    var byCIDesc = fleet.slice().sort(function (a, b) { return (b.CI_width || 0) - (a.CI_width || 0); });
    var topUncertain = byCIDesc.slice(0, 10);
    if (topUncertain.length) {
      var avgCItop = topUncertain.reduce(function (a, s) { return a + (s.CI_width || 0); }, 0) / topUncertain.length;
      var topRegions = {};
      topUncertain.forEach(function (s) { topRegions[s.region] = (topRegions[s.region] || 0) + 1; });
      var topRegionStr = Object.keys(topRegions).sort(function (a, b) { return topRegions[b] - topRegions[a]; }).slice(0, 3).join(', ');
      spots.push({
        title: 'Highest Uncertainty = Highest Optionality',
        body: 'The 10 substations with the widest confidence intervals (avg CI = ' + avgCItop.toFixed(3) +
          ') represent the highest <em>option value</em> for BESS investment — uncertainty creates optionality. ' +
          'They concentrate in <strong>' + topRegionStr + '</strong>. In the SSI-ENN framework, these substations ' +
          'would generate the largest real-options premium above base DCF valuation.'
      });
    }

    // 3. Bridge substations
    var bridges = fleet.filter(function (s) { return s.graph_topology && s.graph_topology.is_bridge; });
    var bridgeHighCrit = bridges.filter(function (s) { return s.classification === 'High' || s.classification === 'Critical'; });
    spots.push({
      title: bridges.length + ' Bridge Substations — Single Points of Failure',
      body: '<strong>' + bridges.length + ' substations</strong> are topological bridges — their failure disconnects ' +
        'part of the network. Of these, <strong>' + bridgeHighCrit.length + '</strong> are classified High or Critical. ' +
        'These are the fleet\'s single points of failure: high graph centrality (R4) combined with elevated risk ' +
        'makes them priority candidates for both grid reinforcement and BESS deployment.'
    });

    // 4. Seismic
    var seismicHigh = fleet.filter(function (s) { return s.seismic && s.seismic.zone <= 1; });
    var seismicHighRisk = seismicHigh.filter(function (s) { return s.classification === 'High' || s.classification === 'Critical'; });
    spots.push({
      title: 'Seismic Zone 4–5: ' + seismicHigh.length + ' Substations in Highest Hazard',
      body: '<strong>' + seismicHigh.length + ' substations</strong> sit in the highest seismic hazard zones ' +
        '(Zones 4–5, moderate to strong). Of these, <strong>' + seismicHighRisk.length + '</strong> already score High/Critical — ' +
        'meaning their grid condition is poor <em>before</em> considering earthquake risk. ' +
        'The R6b seismic modifier captures this compound vulnerability.'
    });

    // 5. Energy poverty
    var highEP = fleet.filter(function (s) { return s.socio_economic && s.socio_economic.EP_rate_region > 14; });
    var highEP_highRisk = highEP.filter(function (s) { return s.classification === 'High' || s.classification === 'Critical'; });
    spots.push({
      title: 'Energy Poverty Double Jeopardy',
      body: '<strong>' + highEP.length + ' substations</strong> serve regions with energy poverty rates above 14% — ' +
        'and <strong>' + highEP_highRisk.length + '</strong> of these are in the High/Critical risk bands. ' +
        'These communities face a double burden: poor grid reliability and limited capacity to absorb the economic impact of outages. ' +
        'The SSI\'s E component + R3 modifier make this invisible correlation visible.'
    });

    // 6. Markov critical
    var markovCrit = fleet.filter(function (s) {
      if (!s.markov) return false;
      var pCrit = (s.markov.steady_state && s.markov.steady_state.length > 3)
        ? s.markov.steady_state[3]
        : (s.markov.p_critical_20yr || 0);
      return pCrit > 0.20;
    });
    var ettcSum = markovCrit.reduce(function (a, s) { return a + ((s.markov && (s.markov.ettc_years || s.markov.ETTC_years)) || 0); }, 0);
    var ettcAvg = markovCrit.length ? (ettcSum / markovCrit.length).toFixed(1) : '?';
    spots.push({
      title: markovCrit.length + ' Substations Approaching Critical Degradation',
      body: 'The SSI\'s Markov degradation model identifies <strong>' + markovCrit.length +
        ' substations</strong> with a stationary critical probability above 20% — meaning their long-term equilibrium state ' +
        'is dominated by degraded or critical condition. Without intervention, these substations will trend toward failure. ' +
        'Average estimated time-to-critical: ' + ettcAvg + ' years.'
    });

    return spots;
  }

  /* ── Default deep-dive rotation (used when country config doesn't supply
     one). Matches the legacy Slovenia 12-month rotation so the unmigrated
     intelligence pages continue to render text in Section G card 1. ── */
  var DEFAULT_DEEP_DIVES = [
    { region: 'Region 01', theme: 'Corridor Edition 01', context: 'Flood/storm anchor',     context_detail: 'Multi-hazard anchor + industrial corridor' },
    { region: 'Region 02', theme: 'Capital Metropolitan', context: 'Capital saturation',     context_detail: 'Capital-intensive tier + flood overlay' },
    { region: 'Region 03', theme: 'Nuclear Zone',        context: 'Seismic exposure',         context_detail: 'NPP + seismic + life-extension planning' },
    { region: 'Region 04', theme: 'Industrial Belt',     context: 'Hydro + flood',            context_detail: 'Hydro cascade + manufacturing fabric' },
    { region: 'Region 05', theme: 'Alpine Valleys',      context: 'Restoration speed',        context_detail: 'Narrow valleys, long restoration MTTR' },
    { region: 'Region 06', theme: 'Coastal Region',      context: 'Wind + corrosion',         context_detail: 'Coastal salt-spray + storm exposure' },
    { region: 'Region 07', theme: 'Mountain Border',     context: 'Cross-border + seismic',   context_detail: 'Friuli spillover + Soča hydro chain' },
    { region: 'Region 08', theme: 'Industrial Cluster',  context: 'Pharma VoLL',              context_detail: 'Continuous-process manufacturing dependency' },
    { region: 'Region 09', theme: 'Rural Corridor',      context: 'Energy poverty',           context_detail: 'Highest energy-poverty + agricultural fabric' },
    { region: 'Region 10', theme: 'Mountain Region',     context: 'Sparse topology',          context_detail: 'Light-rural tier — limited substation density' },
    { region: 'Region 11', theme: 'Coal Transition',     context: 'Just transition',          context_detail: 'Post-coal communities — closure trajectory' },
    { region: 'Region 12', theme: 'Karst Plateau',       context: 'Ice storm legacy',         context_detail: 'Karst hydrogeology + 2014 ice storm legacy' }
  ];

})();
