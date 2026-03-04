/* ═══════════════════════════════════════════════════════════
   SSI v4.0 — Calculation Engine (Client-Side)
   Implements the complete SSI v4.0 formula construct
   6 components · 20 metrics · 7 modifiers · 81 variables
   ═══════════════════════════════════════════════════════════ */

window.SSIEngine = (function () {
  'use strict';

  // ─── Weight Architecture ─────────────────────────────────
  const COMPONENT_WEIGHTS = {
    C: 0.30, V: 0.10, I: 0.25, E: 0.10, S: 0.20, T: 0.05
  };

  const INTRA_WEIGHTS = {
    C: { C1: 0.40, C2: 0.30, C3: 0.15, C4: 0.15 },
    V: { V1: 1.00 },
    I: { I1: 0.12, I2: 0.09, I3: 0.15, I4: 0.12, I5: 0.12, I6: 0.12, I7: 0.10, I8: 0.08, I9: 0.10 },
    E: { E1: 0.55, E2: 0.45 },
    S: { S1: 0.75, S2: 0.125, S3: 0.125 },
    T: { T1: 1.00 }
  };

  // Global weights (component × intra)
  const GLOBAL_WEIGHTS = {};
  Object.keys(COMPONENT_WEIGHTS).forEach(comp => {
    Object.keys(INTRA_WEIGHTS[comp]).forEach(metric => {
      GLOBAL_WEIGHTS[metric] = COMPONENT_WEIGHTS[comp] * INTRA_WEIGHTS[comp][metric];
    });
  });

  // ─── Normalisation Parameters ────────────────────────────
  // Method A/B: Fleet percentile (P5/P95)
  // Method C: Bounded rescaling
  // Method D: Categorical mapping
  const NORM_CONFIG = {
    C1: { method: 'A', p5: null, p95: null },      // fleet-derived
    C2: { method: 'A', p5: null, p95: null },
    C3: { method: 'C', min: 0, max: 100 },          // 0-100%
    C4: { method: 'B', p5: null, p95: null },
    V1: { method: 'B', gamma: 0.50, p5: null, p95: null },
    I1: { method: 'C', min: 0, max: 0.30 },         // IRI scale
    I2: { method: 'C', min: 0, max: 0.30 },
    I3: { method: 'C', min: 0, max: 0.30 },
    I4: { method: 'B_inv', p5: null, p95: null },    // inverted (higher = better)
    I5: { method: 'B', p5: null, p95: null },
    I6: { method: 'B_inv', p5: null, p95: null },    // inverted
    I7: { method: 'B', p5: null, p95: null },
    I8: { method: 'B', p5: null, p95: null },
    I9: { method: 'B', p5: null, p95: null },
    E1: { method: 'B', p5: null, p95: null },
    E2: { method: 'C', min: 1.50, max: 1.85 },
    S1: { method: 'B_dimovski', breakpoints: [1.29, 7.78] },
    S2: { method: 'D', map: { 0: 0, 1: 0.5, 2: 1.0 } },  // categorical
    S3: { method: 'D', map: { 0: 0, 1: 0.5, 2: 1.0 } },
    T1: { method: 'B_composite' }  // pre-normalised sub-metrics
  };

  // T1 DER Stress sub-metric weights
  const T1_WEIGHTS = { DER_ratio: 0.50, DER_variability: 0.30, EV_load_ratio: 0.20 };
  const T1_NORMS = {
    DER_ratio:       { p5: 0.05, p95: 1.20 },
    DER_variability: { p5: 0.15, p95: 0.85 },
    EV_load_ratio:   { p5: 0.00, p95: 0.15 }
  };

  // ─── Modifier Parameters ─────────────────────────────────

  // R2 — Adaptive IRI + Climate Trajectory
  const R2_PARAMS = {
    IRI_THRESH: 0.02,
    IRI_MIN_FRAC: 0.10,
    LAMBDA_CLIMATE: 0.15,
    CLIMATE_CLIP_MIN: -0.50,
    CLIMATE_CLIP_MAX: 1.00
  };

  // R3 — Consequence Multiplier
  const R3_PARAMS = {
    beta_pop: 0.04,
    beta_load: 0.03,
    beta_vuln: 0.02,
    pop_med: 2456,
    GWh_med: 3200,
    sigmoid_steepness: 4,
    range_lo: 0.70,
    range_hi: 1.30
  };

  // R4 — Graph Criticality
  const R4_PARAMS = {
    gamma_BC: 0.10,
    gamma_bridge: 0.15,
    clip_lo: 0.80,
    clip_hi: 1.35
  };

  // R6 — Restoration Speed
  const R6_PARAMS = {
    sigmoid_steepness: 4,
    range_lo: 0.90,
    range_hi: 1.10
  };

  // R7 — Cyber Exposure (v4.1: province-level DESI — values pre-computed in ssi-data.json)
  const R7_MAP = { LOW: 0.99, MEDIUM: 1.02, HIGH: 1.05 }; // fallback only; actual R7 from data

  // ─── Enrichment Parameters ───────────────────────────────
  const ENRICHMENT_PARAMS = {
    fiscal_energy: { weight: 0.08, sub_weights: { tax: 0.40, macro_gap: 0.35, energy_price: 0.25 } },
    migration: { weight: 0.08 },
    elderly_vuln: { range: [1.0, 1.10] },
    flood_zone: { weight: 0.15 },
    landslide: { weight: 0.10 },
    digital_readiness: { weight: 0.04 },
    innovation: { weight: 0.10 },
    healthcare_crit: { override: true }
  };

  // ─── Monte Carlo Uncertainty Model ───────────────────────
  const SIGMA_TOTAL = {
    C1: 0.19, C2: 0.19, C3: 0.43, C4: 0.19,
    V1: 0.45,
    I1: 0.20, I2: 0.20, I3: 0.22, I4: 0.23, I5: 0.25, I6: 0.23, I7: 0.22, I8: 0.18, I9: 0.15,
    E1: 0.40, E2: 0.26,
    S1: 0.13, S2: 0, S3: 0,    // S2/S3 categorical — zero MC variance
    T1: 0.28
  };

  // Expected metric correlations (20×20 — upper triangle, key pairs)
  const METRIC_CORRELATIONS = {
    'C1_C2': 0.82, 'C1_E1': 0.75, 'C1_C3': 0.45,
    'I1_I2': 0.35, 'I1_I3': -0.30, 'I3_I5': 0.55,
    'S1_T1': 0.40, 'T1_I3': 0.25, 'E1_E2': 0.50,
    'I4_I6': 0.60, 'I7_I5': 0.45, 'I8_I9': 0.30
  };

  // ─── Classification Bands ────────────────────────────────
  const BANDS = [
    { name: 'Low',      min: 0.00, max: 0.25, color: '#5d8563' },
    { name: 'Medium',   min: 0.25, max: 0.50, color: '#b8863a' },
    { name: 'High',     min: 0.50, max: 0.75, color: '#aa4234' },
    { name: 'Critical', min: 0.75, max: 1.00, color: '#941914' }
  ];

  // ─── Confidence Tiers ────────────────────────────────────
  const CONFIDENCE_TIERS = [
    { name: 'high',   maxCI: 0.10, desc: 'Provincial data, recent vintage' },
    { name: 'medium', maxCI: 0.25, desc: 'Mixed vintages, some regional' },
    { name: 'low',    maxCI: Infinity, desc: 'Multiple imputed metrics' }
  ];


  // ═══════════════════════════════════════════════════════════
  //  NORMALISATION FUNCTIONS
  // ═══════════════════════════════════════════════════════════

  function softClip(x) {
    return Math.max(0, Math.min(1, x));
  }

  function normaliseFleetPercentile(x, p5, p95) {
    if (p95 === p5) return 0.5;
    return softClip((x - p5) / (p95 - p5));
  }

  function normaliseFleetPercentileInverted(x, p5, p95) {
    return normaliseFleetPercentile(p5 + p95 - x, p5, p95);
  }

  function normaliseBounded(x, min, max) {
    if (max === min) return 0.5;
    return softClip((x - min) / (max - min));
  }

  function normaliseCategorical(x, map) {
    return map[x] !== undefined ? map[x] : 0.5;
  }

  // V metric: severity-weighted dips
  function normaliseVoltage(V1_total, V2_severe_ratio, gamma, p5, p95) {
    const raw = V1_total * (1 + gamma * V2_severe_ratio);
    return normaliseFleetPercentile(raw, p5, p95);
  }

  // T1 DER Stress: composite sub-metric normalisation
  function normaliseT1(DER_ratio, DER_variability, EV_load_ratio) {
    const n_der = normaliseFleetPercentile(DER_ratio, T1_NORMS.DER_ratio.p5, T1_NORMS.DER_ratio.p95);
    const n_var = normaliseFleetPercentile(DER_variability, T1_NORMS.DER_variability.p5, T1_NORMS.DER_variability.p95);
    const n_ev  = normaliseFleetPercentile(EV_load_ratio, T1_NORMS.EV_load_ratio.p5, T1_NORMS.EV_load_ratio.p95);
    return T1_WEIGHTS.DER_ratio * n_der + T1_WEIGHTS.DER_variability * n_var + T1_WEIGHTS.EV_load_ratio * n_ev;
  }


  // ═══════════════════════════════════════════════════════════
  //  MODIFIER FUNCTIONS
  // ═══════════════════════════════════════════════════════════

  // R2 — Climate Trajectory + Adaptive IRI Weighting
  function computeClimateTrajectory(delta_climate) {
    const clipped = Math.max(R2_PARAMS.CLIMATE_CLIP_MIN, Math.min(R2_PARAMS.CLIMATE_CLIP_MAX, delta_climate));
    return 1 + R2_PARAMS.LAMBDA_CLIMATE * clipped;
  }

  function computeR2AdaptiveWeights(IRI_forward_I1, IRI_forward_I2, IRI_forward_I3) {
    const base_I = INTRA_WEIGHTS.I;
    const iri_metrics = ['I1', 'I2', 'I3'];
    const iri_values = { I1: IRI_forward_I1, I2: IRI_forward_I2, I3: IRI_forward_I3 };
    const struct_metrics = ['I4', 'I6'];

    const adapted = Object.assign({}, base_I);
    let released = 0;

    iri_metrics.forEach(m => {
      const ratio = iri_values[m] / R2_PARAMS.IRI_THRESH;
      const factor = Math.max(R2_PARAMS.IRI_MIN_FRAC, Math.min(1, ratio));
      const w_adapted = base_I[m] * factor;
      released += base_I[m] - w_adapted;
      adapted[m] = w_adapted;
    });

    // Redistribute released weight to structural metrics I4, I6
    const struct_sum = struct_metrics.reduce((s, m) => s + base_I[m], 0);
    struct_metrics.forEach(m => {
      adapted[m] = base_I[m] + released * (base_I[m] / struct_sum);
    });

    return adapted;
  }

  // R3 — Consequence Multiplier with Energy Poverty
  function computeR3(pop, GWh, V_socio, enrichments) {
    const p = R3_PARAMS;
    let z = p.beta_pop * Math.log2(Math.max(1, pop) / p.pop_med)
          + p.beta_load * Math.log2(Math.max(0.001, GWh) / p.GWh_med)
          + p.beta_vuln * (V_socio || 0);

    let C_mult = p.range_lo + (p.range_hi - p.range_lo) / (1 + Math.exp(-p.sigmoid_steepness * z));

    // Enrichments
    if (enrichments) {
      // V_socio Fiscal Enrichment
      if (enrichments.fiscal_energy_composite != null) {
        const fec = enrichments.fiscal_energy_composite;
        C_mult *= (1.0 + ENRICHMENT_PARAMS.fiscal_energy.weight * (1.0 - fec));
      }
      // Migration Workforce Amplifier
      if (enrichments.migration_score != null) {
        C_mult *= (1.0 + ENRICHMENT_PARAMS.migration.weight * (1.0 - enrichments.migration_score));
      }
      // Elderly Vulnerability
      if (enrichments.elderly_vuln_weight != null) {
        C_mult *= enrichments.elderly_vuln_weight;
      }
      // Flood Zone Amplifier
      if (enrichments.flood_score != null) {
        C_mult *= (1.0 + ENRICHMENT_PARAMS.flood_zone.weight * enrichments.flood_score);
      }
    }

    return Math.max(p.range_lo, Math.min(1.50, C_mult));  // allow enrichments to push slightly beyond 1.30
  }

  // R4 — Graph Criticality
  function computeR4(degree, BC_percentile, is_bridge) {
    const p = R4_PARAMS;
    let base_factor;
    if (degree === 1) base_factor = 1.15;
    else if (degree === 2) base_factor = 1.00;
    else base_factor = Math.max(1 - 0.05 * (degree - 2), 0.85);

    const F_topo = base_factor * (1 + p.gamma_BC * (BC_percentile || 0) + p.gamma_bridge * (is_bridge ? 1 : 0));
    return Math.max(p.clip_lo, Math.min(p.clip_hi, F_topo));
  }

  // R6 — Restoration Speed
  function computeR6(CAIDI_local, CAIDI_med) {
    if (!CAIDI_local || !CAIDI_med || CAIDI_med === 0) return 1.00;
    const ratio = CAIDI_local / CAIDI_med;
    const p = R6_PARAMS;
    const z = p.sigmoid_steepness * (ratio - 1);
    const raw = 1 / (1 + Math.exp(-z));
    return p.range_lo + (p.range_hi - p.range_lo) * raw;
  }

  // R7 — Cyber Exposure (v4.1: province-level DESI model)
  // R7 values are now pre-computed per substation in ssi-data.json
  // This function serves as fallback only if R7_cyber is missing from data
  function computeR7(cyber_class, digital_readiness) {
    let factor = R7_MAP[cyber_class] || R7_MAP.MEDIUM;
    // Province-level DESI modulation (legacy fallback)
    if (digital_readiness != null) {
      factor = 1.0 + 0.06 * (digital_readiness - 0.50);
    }
    return Math.max(0.99, Math.min(1.05, factor));
  }

  // Soft clip upper (overflow compression)
  function softClipUpper(R_raw) {
    if (R_raw <= 1.00) return R_raw;
    return 1.00 - 1 / (1 + Math.exp(20 * (R_raw - 1.05)));
  }


  // ═══════════════════════════════════════════════════════════
  //  CORE CALCULATION
  // ═══════════════════════════════════════════════════════════

  /**
   * Compute R_base for a single substation
   * @param {Object} normalised — { C1:n, C2:n, ..., T1:n } normalised metrics [0,1]
   * @param {Object} [adaptedI] — adapted I-component intra-weights from R2 (optional)
   * @returns {number} R_base in [0,1]
   */
  function computeRBase(normalised, adaptedI) {
    let R_base = 0;

    Object.keys(COMPONENT_WEIGHTS).forEach(comp => {
      let comp_score = 0;
      const intra = comp === 'I' && adaptedI ? adaptedI : INTRA_WEIGHTS[comp];

      Object.keys(intra).forEach(metric => {
        const val = normalised[metric];
        if (val != null) {
          comp_score += intra[metric] * val;
        }
      });

      R_base += COMPONENT_WEIGHTS[comp] * comp_score;
    });

    return R_base;
  }

  /**
   * Full SSI v4.0 score computation for a single substation
   * @param {Object} sub — substation data object with raw metrics + context
   * @returns {Object} full SSI output (R_median, components, modifiers, classification, etc.)
   */
  function computeSSI(sub) {
    // 1. Normalise all metrics
    const normalised = {};
    // (In production, fleet percentiles would be pre-computed; here we use stored normalised values)
    // This engine expects pre-normalised component scores OR raw values + fleet stats

    // If pre-normalised components are provided directly
    if (sub.components) {
      return computeFromComponents(sub);
    }

    // Otherwise compute from raw metrics (requires fleet context)
    return computeFromRaw(sub);
  }

  /**
   * Compute from pre-computed component scores (dashboard mode)
   */
  function computeFromComponents(sub) {
    const comps = sub.components;

    // R_base = weighted sum of components
    let R_base = 0;
    Object.keys(COMPONENT_WEIGHTS).forEach(comp => {
      R_base += COMPONENT_WEIGHTS[comp] * (comps[comp] || 0);
    });

    // Modifiers
    const mods = sub.modifiers || {};
    const C_mult = mods.R3_C_mult || 1.00;
    const F_topo = mods.R4_F_topo || 1.00;
    const R6_mult = mods.R6_restoration || 1.00;
    const Cyber_factor = mods.R7_cyber || 1.00;

    // R_final
    const R_raw = R_base * F_topo * C_mult * R6_mult * Cyber_factor;
    const R_final = softClipUpper(R_raw);

    // Classification
    const band = classifyBand(sub.R_median || R_final);

    return {
      R_base: R_base,
      R_final: R_final,
      R_median: sub.R_median || R_final,
      R_P5: sub.R_P5 || null,
      R_P95: sub.R_P95 || null,
      classification: band.name,
      band_color: band.color,
      components: comps,
      modifiers: { R3_C_mult: C_mult, R4_F_topo: F_topo, R6_restoration: R6_mult, R7_cyber: Cyber_factor },
      modifier_impact: R_final - R_base,
      modifier_pct: R_base > 0 ? ((R_final - R_base) / R_base * 100).toFixed(1) + '%' : '0%',
      confidence_tier: classifyConfidence(sub.R_P5, sub.R_P95)
    };
  }

  /**
   * Monte Carlo simulation for a single substation (simplified client-side)
   * Uses 1000 iterations for browser performance (vs 10k in production)
   */
  function monteCarlo(normalised, adaptedI, modifiers, iterations) {
    iterations = iterations || 1000;
    const samples = [];
    const metrics = Object.keys(normalised).filter(m => SIGMA_TOTAL[m] > 0);

    for (let k = 0; k < iterations; k++) {
      const perturbed = Object.assign({}, normalised);

      // Perturb each metric with Gaussian noise
      metrics.forEach(m => {
        const sigma = SIGMA_TOTAL[m];
        const noise = gaussianRandom() * sigma;
        perturbed[m] = softClip(normalised[m] * (1 + noise));
      });

      // Compute R_base for this iteration
      const R_base_k = computeRBase(perturbed, adaptedI);

      // Apply modifiers
      const R_raw_k = R_base_k * (modifiers.F_topo || 1) * (modifiers.C_mult || 1)
                     * (modifiers.R6_mult || 1) * (modifiers.Cyber_factor || 1);

      samples.push(softClipUpper(R_raw_k));
    }

    samples.sort((a, b) => a - b);

    return {
      R_median: percentile(samples, 0.50),
      R_P5: percentile(samples, 0.05),
      R_P95: percentile(samples, 0.95),
      P_critical: samples.filter(r => r > 0.75).length / samples.length,
      samples: samples
    };
  }


  // ═══════════════════════════════════════════════════════════
  //  CLASSIFICATION HELPERS
  // ═══════════════════════════════════════════════════════════

  function classifyBand(R) {
    for (let i = BANDS.length - 1; i >= 0; i--) {
      if (R >= BANDS[i].min) return BANDS[i];
    }
    return BANDS[0];
  }

  function classifyConfidence(R_P5, R_P95) {
    if (R_P5 == null || R_P95 == null) return 'medium';
    const ci = R_P95 - R_P5;
    for (const tier of CONFIDENCE_TIERS) {
      if (ci <= tier.maxCI) return tier.name;
    }
    return 'low';
  }


  // ═══════════════════════════════════════════════════════════
  //  FLEET ANALYTICS
  // ═══════════════════════════════════════════════════════════

  /**
   * Compute fleet-level statistics from an array of SSI results
   */
  function fleetAnalytics(substations) {
    const n = substations.length;
    if (n === 0) return null;

    // Sort by R_median
    const sorted = substations.slice().sort((a, b) => a.R_median - b.R_median);

    // Band distribution
    const bands = { Low: 0, Medium: 0, High: 0, Critical: 0 };
    substations.forEach(s => {
      const b = classifyBand(s.R_median);
      bands[b.name]++;
    });

    const band_pct = {};
    Object.keys(bands).forEach(b => { band_pct[b] = (bands[b] / n * 100); });

    // Component averages
    const comp_avg = { C: 0, V: 0, I: 0, E: 0, S: 0, T: 0 };
    substations.forEach(s => {
      if (s.components) {
        Object.keys(comp_avg).forEach(k => { comp_avg[k] += s.components[k] || 0; });
      }
    });
    Object.keys(comp_avg).forEach(k => { comp_avg[k] /= n; });

    // Modifier stats
    const mod_stats = {};
    ['R3_C_mult', 'R4_F_topo', 'R6_restoration', 'R7_cyber'].forEach(mk => {
      const vals = substations.map(s => (s.modifiers && s.modifiers[mk]) || 1.0);
      const mean = vals.reduce((a, b) => a + b, 0) / vals.length;
      const sigma = Math.sqrt(vals.reduce((a, b) => a + (b - mean) ** 2, 0) / vals.length);
      mod_stats[mk] = { mean, sigma, min: Math.min(...vals), max: Math.max(...vals) };
    });

    // Confidence distribution
    const conf = { high: 0, medium: 0, low: 0 };
    substations.forEach(s => {
      const tier = classifyConfidence(s.R_P5, s.R_P95);
      conf[tier]++;
    });
    const conf_pct = {};
    Object.keys(conf).forEach(k => { conf_pct[k] = (conf[k] / n * 100); });

    return {
      total: n,
      median_R: sorted[Math.floor(n / 2)].R_median,
      mean_R: substations.reduce((s, sub) => s + sub.R_median, 0) / n,
      min_R: sorted[0].R_median,
      max_R: sorted[n - 1].R_median,
      bands: bands,
      band_pct: band_pct,
      component_avg: comp_avg,
      modifier_stats: mod_stats,
      confidence_pct: conf_pct
    };
  }

  /**
   * Compute regional aggregation
   */
  function regionalAnalytics(substations) {
    const regionMap = {};
    substations.forEach(s => {
      const r = s.region || 'Unknown';
      if (!regionMap[r]) regionMap[r] = [];
      regionMap[r].push(s);
    });

    return Object.entries(regionMap).map(([region, subs]) => {
      const sorted = subs.slice().sort((a, b) => a.R_median - b.R_median);
      const n = subs.length;
      const bands = { Low: 0, Medium: 0, High: 0, Critical: 0 };
      subs.forEach(s => { bands[classifyBand(s.R_median).name]++; });

      // Component averages for this region
      const comp_avg = { C: 0, V: 0, I: 0, E: 0, S: 0, T: 0 };
      subs.forEach(s => {
        if (s.components) {
          Object.keys(comp_avg).forEach(k => { comp_avg[k] += s.components[k] || 0; });
        }
      });
      Object.keys(comp_avg).forEach(k => { comp_avg[k] /= n; });

      return {
        region: region,
        count: n,
        median_R: sorted[Math.floor(n / 2)].R_median,
        mean_R: subs.reduce((s, sub) => s + sub.R_median, 0) / n,
        min_R: sorted[0].R_median,
        max_R: sorted[n - 1].R_median,
        bands: bands,
        pct_critical: (bands.Critical / n * 100),
        pct_high: ((bands.High + bands.Critical) / n * 100),
        component_avg: comp_avg
      };
    }).sort((a, b) => b.median_R - a.median_R);
  }


  // ═══════════════════════════════════════════════════════════
  //  UTILITY FUNCTIONS
  // ═══════════════════════════════════════════════════════════

  function gaussianRandom() {
    // Box-Muller transform
    let u = 0, v = 0;
    while (u === 0) u = Math.random();
    while (v === 0) v = Math.random();
    return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
  }

  function percentile(sorted, p) {
    const idx = p * (sorted.length - 1);
    const lo = Math.floor(idx);
    const hi = Math.ceil(idx);
    if (lo === hi) return sorted[lo];
    return sorted[lo] + (sorted[hi] - sorted[lo]) * (idx - lo);
  }

  // ═══════════════════════════════════════════════════════════
  //  PUBLIC API
  // ═══════════════════════════════════════════════════════════

  return {
    // Constants
    COMPONENT_WEIGHTS,
    INTRA_WEIGHTS,
    GLOBAL_WEIGHTS,
    BANDS,
    CONFIDENCE_TIERS,
    SIGMA_TOTAL,
    T1_WEIGHTS,
    T1_NORMS,
    R2_PARAMS,
    R3_PARAMS,
    R4_PARAMS,
    R6_PARAMS,
    R7_MAP,
    ENRICHMENT_PARAMS,

    // Core functions
    computeSSI,
    computeRBase,
    computeFromComponents,
    monteCarlo,
    softClipUpper,

    // Normalisation
    normaliseFleetPercentile,
    normaliseFleetPercentileInverted,
    normaliseBounded,
    normaliseCategorical,
    normaliseVoltage,
    normaliseT1,
    softClip,

    // Modifiers
    computeClimateTrajectory,
    computeR2AdaptiveWeights,
    computeR3,
    computeR4,
    computeR6,
    computeR7,

    // Analytics
    classifyBand,
    classifyConfidence,
    fleetAnalytics,
    regionalAnalytics,

    // Utilities
    gaussianRandom,
    percentile
  };
})();
