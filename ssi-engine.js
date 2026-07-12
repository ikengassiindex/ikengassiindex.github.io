/* ═══════════════════════════════════════════════════════════
   SSI v4.0.2 — Browser Engine — RETIRED (PR-4)
   ═══════════════════════════════════════════════════════════

   Per F-L3-3 operator decision (audit memo 2026-06-08), the browser-side
   Monte Carlo + R_base + modifier-chain implementations are RETIRED in
   favour of the canonical Python pipeline (scripts/pipeline/scoring/engine.py).

   Reasoning
   ─────────
   The pre-PR-4 browser engine carried a parallel scoring path: its own
   COMPONENT_WEIGHTS, INTRA_WEIGHTS, SIGMA_TOTAL, modifier multiplication,
   1000-iteration Box-Muller Monte Carlo, R3/R4/R6/R6b/R7 sub-modifier
   physics, fleet + regional analytics. Every numeric value displayed on
   every per-country page (39 countries × 5 pages = 195 HTMLs) flowed
   from this engine OR from precomputed ssi-data.json — and the two
   had drifted at multiple points (Audit findings F-L3-1 through F-L3-5).

   Post-PR-4 architecture (sole-source-of-truth):
   • Scoring engine: scripts/pipeline/scoring/engine.py (Python, numpy-vectorized,
     10,000-iteration Monte Carlo, registry-driven modifier chain, Gaussian
     copula correlation via Cholesky).
   • Per-country ssi-data.json: emitted by the pipeline, carries R_median,
     R_P5, R_P95, CI_width, P_critical, skewness, mult_product, add_sum,
     modifier_impacts (one record per substation).
   • Browser side: reads precomputed values directly; performs zero
     numerical computation, only classification + formatting.

   This file retains:
   • classifyBand(R) — classification helper used by data-sections.js
   • classifyConfidence(P5, P95) — confidence-tier classifier
   • percentile(sorted, p) — utility for fleet-distribution widgets
   • BANDS + CONFIDENCE_TIERS — band-threshold constants
   • monteCarlo() + computeRBase() — retained as THROW TRIPWIRES so any
     latent caller surfaces loudly with an actionable error message

   To recompute scores: run the Python pipeline server-side.
   ═══════════════════════════════════════════════════════════ */

window.SSIEngine = (function () {
  'use strict';

  // ─── Classification thresholds ──────────────────────────
  // Phase 2B-1 (25 June 2026): 4-band → 5-band per operator Q1(b) decision.
  // The 5th 'Extreme' band [1.00, 1.30] captures the additive-R6c_flood
  // overflow zone where soft_clip_upper multiplicative saturation combines
  // with flood-driven additive push per the v4.2 master equation
  //   R_final = soft_clip_upper(R_base × Π mult_i) + Σ (add_i − 1.0)
  // Mirror of scripts/pipeline/scoring/engine.py::BANDS — kept in sync
  // manually; drift here breaks the frontend rendering vs the canonical
  // classification field.
  var BANDS = [
    { name: 'Low',      min: 0.00, max: 0.25 },
    { name: 'Medium',   min: 0.25, max: 0.50 },
    { name: 'High',     min: 0.50, max: 0.75 },
    { name: 'Critical', min: 0.75, max: 1.00 },
    { name: 'Extreme',  min: 1.00, max: 1.30 }
  ];

  var CONFIDENCE_TIERS = [
    { name: 'high',   maxCI: 0.10 },
    { name: 'medium', maxCI: 0.25 },
    { name: 'low',    maxCI: 1.00 }
  ];

  // ─── Classification helpers (preserved — pure functions) ──

  function classifyBand(R) {
    for (var i = BANDS.length - 1; i >= 0; i--) {
      if (R >= BANDS[i].min) return BANDS[i];
    }
    return BANDS[0];
  }

  function classifyConfidence(R_P5, R_P95) {
    if (R_P5 == null || R_P95 == null) return 'medium';
    var ci = R_P95 - R_P5;
    for (var i = 0; i < CONFIDENCE_TIERS.length; i++) {
      if (ci <= CONFIDENCE_TIERS[i].maxCI) return CONFIDENCE_TIERS[i].name;
    }
    return 'low';
  }

  // ─── Linear interpolation percentile (preserved utility) ──

  function percentile(sorted, p) {
    if (!Array.isArray(sorted) || sorted.length === 0) return null;
    var idx = p * (sorted.length - 1);
    var lo = Math.floor(idx);
    var hi = Math.ceil(idx);
    if (lo === hi) return sorted[lo];
    return sorted[lo] + (sorted[hi] - sorted[lo]) * (idx - lo);
  }

  // ─── Retirement tripwires (throw if invoked) ─────────────
  //
  // These functions are preserved by NAME on the public API surface so any
  // latent caller surfaces loudly. The message points the operator at the
  // canonical replacement path (read ssi-data.json) and the recompute path
  // (Python pipeline). Per audit Convention #55, the message includes the
  // exact action required — no silent fallback.

  function monteCarlo() {
    throw new Error(
      'ssi-engine.js::monteCarlo() RETIRED (F-L3-1 / F-L3-3 closure, PR-4). ' +
      'Read precomputed R_median / R_P5 / R_P95 / CI_width / P_critical ' +
      'directly from ssi-data.json. To recompute scores, run the canonical ' +
      'Python pipeline server-side: python -m scripts.pipeline.run <country>.'
    );
  }

  function computeRBase() {
    throw new Error(
      'ssi-engine.js::computeRBase() RETIRED (F-L3-3 closure, PR-4). ' +
      'Read precomputed R_base_median directly from ssi-data.json. ' +
      'To recompute, run the Python pipeline: python -m scripts.pipeline.run <country>.'
    );
  }

  function computeFromComponents() {
    throw new Error(
      'ssi-engine.js::computeFromComponents() RETIRED (F-L3-4 closure, PR-4). ' +
      'The modifier chain now lives in scripts/pipeline/scoring/modifier_registry.py ' +
      '— see CLAUDE.md Convention #56 for the extension contract.'
    );
  }

  function computeSSI() {
    throw new Error(
      'ssi-engine.js::computeSSI() RETIRED (PR-4). ' +
      'Read precomputed score from ssi-data.json or invoke the Python pipeline.'
    );
  }

  function fleetAnalytics() {
    throw new Error(
      'ssi-engine.js::fleetAnalytics() RETIRED (PR-4). ' +
      'Read precomputed fleet_summary from ssi-data.json.'
    );
  }

  function regionalAnalytics() {
    throw new Error(
      'ssi-engine.js::regionalAnalytics() RETIRED (PR-4). ' +
      'Read precomputed regional rollups from ssi-data.json::regions.'
    );
  }

  // ─── Public API ─────────────────────────────────────────
  //
  // Note: keys above use the historical names so data-sections.js's
  // `Object.keys(window.SSIEngine).length` continues to render a non-zero
  // count on the data page. The functions themselves either compute
  // (classify*, percentile) or throw (compute*, monte*, *Analytics).

  return {
    // Constants — preserved
    BANDS: BANDS,
    CONFIDENCE_TIERS: CONFIDENCE_TIERS,

    // Classification + formatting — preserved as pure functions
    classifyBand: classifyBand,
    classifyConfidence: classifyConfidence,
    percentile: percentile,

    // Retired computational functions — preserved as throw tripwires
    // (intentionally retained so any latent caller fails loudly)
    monteCarlo: monteCarlo,
    computeRBase: computeRBase,
    computeFromComponents: computeFromComponents,
    computeSSI: computeSSI,
    fleetAnalytics: fleetAnalytics,
    regionalAnalytics: regionalAnalytics,

    // Retirement marker — readable from the browser console for audit
    _retired: true,
    _retirement_pr: 'PR-4',
    _retirement_date: '2026-06-08',
    _canonical_engine: 'scripts/pipeline/scoring/engine.py'
  };
})();
