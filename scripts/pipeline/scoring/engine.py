"""
SSI Index v4.0.2 — Python Scoring Engine
Server-side implementation of the SSI formula construct.

Phase 1 PR-2 (8 June 2026) replaced the per-iteration pure-Python Monte Carlo
with a vectorized numpy implementation at 10,000 iterations + metric-level
Gaussian-copula perturbation. This addresses F-L3-1 (iteration count),
F-L3-2 (correlation matrix application), and F-L3-3 (Py/JS engine
unification). See AUDIT_v4_0_2_PRE_v4_2_FOUNDATION.md §7.7 + PR-2 in
PHASE_1_IMPLEMENTATION_PLAN.md.

This engine:
  1. Takes enriched substation data (post-ingestion)
  2. Recomputes R6b_seismic from actual PGA values
  3. Recomputes climate trajectories from CMIP6 deltas
  4. Runs vectorized 10k Monte Carlo with Gaussian copula correlation
     (METRIC_CORRELATIONS applied via Cholesky decomposition)
  5. Produces updated R_median, CI, classification, fleet stats

The modifier chain is now centrally registered in modifier_registry.py
(PR-1). The mult_product + add_sum are computed ONCE per substation
outside the MC loop — this is the key efficiency win, made possible by
the registry pattern.
"""

import math
import random
import logging
from copy import deepcopy

import numpy as np

from .modifier_registry import compute_modifier_terms, per_modifier_impacts

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
#  WEIGHT ARCHITECTURE (v4.0.2)
# ═══════════════════════════════════════════════════════════

COMPONENT_WEIGHTS = {"C": 0.30, "V": 0.10, "I": 0.25, "E": 0.10, "S": 0.20, "T": 0.05}

INTRA_WEIGHTS = {
    "C": {"C1": 0.40, "C2": 0.30, "C3": 0.15, "C4": 0.15},
    "V": {"V1": 1.00},
    "I": {"I1": 0.12, "I2": 0.09, "I3": 0.15, "I4": 0.12, "I5": 0.12, "I6": 0.12, "I7": 0.10, "I8": 0.08, "I9": 0.10},
    "E": {"E1": 0.55, "E2": 0.45},
    "S": {"S1": 0.75, "S2": 0.125, "S3": 0.125},
    "T": {"T1": 1.00},
}

# Monte Carlo uncertainty (sigma per metric)
SIGMA_TOTAL = {
    "C1": 0.19, "C2": 0.19, "C3": 0.43, "C4": 0.19,
    "V1": 0.45,
    "I1": 0.20, "I2": 0.20, "I3": 0.22, "I4": 0.23, "I5": 0.25,
    "I6": 0.23, "I7": 0.22, "I8": 0.18, "I9": 0.15,
    "E1": 0.40, "E2": 0.26,
    "S1": 0.13, "S2": 0, "S3": 0,
    "T1": 0.28,
}

# Key metric correlations (upper triangle)
METRIC_CORRELATIONS = {
    ("C1", "C2"): 0.82, ("C1", "E1"): 0.75, ("C1", "C3"): 0.45,
    ("I1", "I2"): 0.35, ("I1", "I3"): -0.30, ("I3", "I5"): 0.55,
    ("S1", "T1"): 0.40, ("T1", "I3"): 0.25, ("E1", "E2"): 0.50,
    ("I4", "I6"): 0.60, ("I7", "I5"): 0.45, ("I8", "I9"): 0.30,
}

# Classification bands
# Phase 2B-1 (25 June 2026): 4-band → 5-band per operator Q1(b) decision.
# The 5th 'Extreme' band [1.00, 1.30] captures the additive-R6c_flood
# overflow zone where soft_clip_upper multiplicative saturation combines
# with flood-driven additive push. See v4.2 master equation
#   R_final = soft_clip_upper(R_base × Π mult_i) + Σ (add_i − 1.0)
# and Sobol sensitivity (V4.2_COMPLETENESS_AUDIT.md §15.4) where R6c
# was the second-highest first-order index (S_i=0.96).
BANDS = [
    {"name": "Low",      "min": 0.00, "max": 0.25},
    {"name": "Medium",   "min": 0.25, "max": 0.50},
    {"name": "High",     "min": 0.50, "max": 0.75},
    {"name": "Critical", "min": 0.75, "max": 1.00},
    {"name": "Extreme",  "min": 1.00, "max": 1.30},
]

# T1 DER Stress sub-metric weights and normalisation
T1_WEIGHTS = {"DER_ratio": 0.50, "DER_variability": 0.30, "EV_load_ratio": 0.20}
T1_NORMS = {
    "DER_ratio": {"p5": 0.05, "p95": 1.20},
    "DER_variability": {"p5": 0.15, "p95": 0.85},
    "EV_load_ratio": {"p5": 0.00, "p95": 0.15},
}


# ═══════════════════════════════════════════════════════════
#  MODIFIER PARAMETERS
# ═══════════════════════════════════════════════════════════

R3_PARAMS = {"beta_pop": 0.04, "beta_load": 0.03, "beta_vuln": 0.02,
             "pop_med": 2456, "GWh_med": 3200, "sigmoid_steepness": 4,
             "range_lo": 0.70, "range_hi": 1.30}

R4_PARAMS = {"gamma_BC": 0.10, "gamma_bridge": 0.15, "clip_lo": 0.80, "clip_hi": 1.35}

R6_PARAMS = {"sigmoid_steepness": 4, "range_lo": 0.90, "range_hi": 1.10}

R6B_PARAMS = {"pga_scale": 0.50, "clip_lo": 1.00, "clip_hi": 1.25}


# ═══════════════════════════════════════════════════════════
#  CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════

def soft_clip(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def soft_clip_upper(R_raw):
    """Overflow compression for R > 1.0."""
    if R_raw <= 1.0:
        return R_raw
    return 1.0 - 1 / (1 + math.exp(20 * (R_raw - 1.05)))


def classify_band(R):
    """Classify R_median into Low/Medium/High/Critical/Extreme.

    Classes B/C fix (16 July 2026, FAILURE_SOLVING_PROPOSAL_20260716.md §3):
    guard against R=None (Convention #56 pre-L3 state per CONVENTION_78 §4bis.4).
    Substations awaiting L3 rescore legitimately carry R_median=None; return
    "Unclassified" so downstream aggregators can surface them visibly.
    """
    if R is None:
        return "Unclassified"
    for band in reversed(BANDS):
        if R >= band["min"]:
            return band["name"]
    return "Low"


def classify_confidence(R_P5, R_P95):
    """Classify confidence tier from CI width.

    A zero-width interval means no Monte Carlo ran, not that the estimate is
    precise. Before the guard below, `ci <= 0.10` caught it and returned
    "high": about 78,500 substations were published as high-confidence on the
    strength of a simulation that never happened — 13,979 of austria's 14,720
    among them.

    Measured across eight countries, every degenerate record has a CI of
    exactly 0.0 and the narrowest real 10,000-iteration interval is 0.042, so
    the two populations do not overlap and the guard cannot catch a genuine
    estimate.

    Returns None where there is no basis for a tier. None is what every
    connector writes at ingestion, and it is the peer of "Unclassified" from
    classify_band — Convention #56, visibly honest rather than silently
    defaulted.
    """
    if R_P5 is None or R_P95 is None:
        return None
    ci = R_P95 - R_P5
    if ci <= 1e-9:
        return None
    if ci <= 0.10:
        return "high"
    elif ci <= 0.25:
        return "medium"
    return "low"


def classify_band_normalised(R, R_P5, R_P95):
    """Classify R_median into 5 bands using per-country P5/P95 normalisation.

    Task #461 (22 July 2026): per-country normalisation for classification bands.
    The absolute-R cutoffs [0.25, 0.50, 0.75, 1.00] collapse ~80% of substations
    in Wave 4 countries (spain/italy/portugal/france/germany post R_base fix)
    into 'High' because the empirical R_median distribution is compressed to
    [0.42, 0.83] by the additive R6c_flood floor + soft_clip_upper ceiling.
    The per-substation ranking IS present (Madrid 0.53 < Bilbao 0.61 <
    Extremadura 0.66) but the band boundary hides it.

    Normalisation: R_norm = clip((R - R_P5) / (R_P95 - R_P5), 0, 1) then
    apply the existing 5-band cutoffs. This preserves within-country
    ranking + Convention #56 visibly-honest degradation (R_median stored
    unchanged for LP-DD auditability; band label semantic shifts from
    "absolute physical risk threshold" to "within-country risk ranking":
    Extreme = top ~5%, Critical = next ~20%, High = middle ~30%, Medium =
    next ~30%, Low = bottom ~15% under the linear normalisation).

    Convention #56 preservation:
      - R=None → "Unclassified" (unchanged from classify_band())
      - R_P5=None OR R_P95=None → fallback to classify_band(R) absolute cutoffs
      - R_P5 == R_P95 (degenerate country, no distribution spread) →
        fallback to classify_band(R) absolute cutoffs
    """
    if R is None:
        return "Unclassified"
    if R_P5 is None or R_P95 is None:
        return classify_band(R)
    span = R_P95 - R_P5
    if span <= 0:  # Degenerate — no distribution spread; use absolute
        return classify_band(R)
    R_norm = (R - R_P5) / span
    R_norm = max(0.0, min(1.0, R_norm))
    return classify_band(R_norm)


def apply_country_normalised_bands(substations):
    """Batch-apply per-country P5/P95 normalisation to classification bands.

    Task #461 (22 July 2026): mutates each substation's `classification`
    field in-place to reflect within-country ranking rather than absolute-R
    band. Preserves each sub's `R_median` unchanged (Convention #56 —
    absolute score stays auditable). Also stores per-country anchors on
    each substation as `_band_norm_R_P5` + `_band_norm_R_P95` for audit
    trail.

    Returns tuple (R_P5, R_P95, n_normalised, n_skipped) for the
    per-country anchors + counts. Callers should also write these anchors
    into the country's fleet_summary so downstream consumers can
    reconstruct the normalisation without re-scanning.
    """
    scored = [s.get("R_median") for s in substations if s.get("R_median") is not None]
    if not scored:
        return (None, None, 0, len(substations))
    scored_sorted = sorted(scored)
    R_P5 = _percentile(scored_sorted, 0.05)
    R_P95 = _percentile(scored_sorted, 0.95)
    n_norm = 0
    n_skip = 0
    for s in substations:
        R = s.get("R_median")
        if R is None:
            s["classification"] = "Unclassified"
            n_skip += 1
        else:
            s["classification"] = classify_band_normalised(R, R_P5, R_P95)
            # Audit trail per Convention #56
            s["_band_norm_R_P5"] = round(R_P5, 4)
            s["_band_norm_R_P95"] = round(R_P95, 4)
            n_norm += 1
    return (R_P5, R_P95, n_norm, n_skip)


# ═══════════════════════════════════════════════════════════
#  MODIFIER COMPUTATIONS
# ═══════════════════════════════════════════════════════════

def compute_r6b_seismic(pga_g, zone_weight=1.0):
    """
    Compute R6b seismic modifier from PGA.
    R6b = 1.0 + pga_scale × PGA × zone_weight, clipped to [1.0, 1.25]
    """
    if not pga_g or pga_g <= 0:
        return 1.0
    p = R6B_PARAMS
    raw = 1.0 + p["pga_scale"] * pga_g * zone_weight
    return soft_clip(raw, p["clip_lo"], p["clip_hi"])


def compute_r3(pop, GWh, V_socio, enrichments=None):
    """Compute R3 consequence multiplier."""
    p = R3_PARAMS
    z = (p["beta_pop"] * math.log2(max(1, pop) / p["pop_med"])
         + p["beta_load"] * math.log2(max(0.001, GWh) / p["GWh_med"])
         + p["beta_vuln"] * (V_socio or 0))

    C_mult = p["range_lo"] + (p["range_hi"] - p["range_lo"]) / (1 + math.exp(-p["sigmoid_steepness"] * z))

    if enrichments:
        if enrichments.get("fiscal_energy_composite") is not None:
            C_mult *= (1.0 + 0.08 * (1.0 - enrichments["fiscal_energy_composite"]))
        if enrichments.get("migration_score") is not None:
            C_mult *= (1.0 + 0.08 * (1.0 - enrichments["migration_score"]))
        if enrichments.get("elderly_vuln_weight") is not None:
            C_mult *= enrichments["elderly_vuln_weight"]

    return soft_clip(C_mult, p["range_lo"], 1.50)


def compute_r4(degree, BC_percentile, is_bridge):
    """Compute R4 graph topology modifier."""
    p = R4_PARAMS
    if degree == 1:
        base = 1.15
    elif degree == 2:
        base = 1.00
    else:
        base = max(1 - 0.05 * (degree - 2), 0.85)

    F_topo = base * (1 + p["gamma_BC"] * (BC_percentile or 0) + p["gamma_bridge"] * (1 if is_bridge else 0))
    return soft_clip(F_topo, p["clip_lo"], p["clip_hi"])


def compute_r6_restoration(CAIDI_local, CAIDI_med):
    """Compute R6 restoration speed modifier."""
    if not CAIDI_local or not CAIDI_med or CAIDI_med == 0:
        return 1.0
    ratio = CAIDI_local / CAIDI_med
    p = R6_PARAMS
    z = p["sigmoid_steepness"] * (ratio - 1)
    raw = 1 / (1 + math.exp(-z))
    return p["range_lo"] + (p["range_hi"] - p["range_lo"]) * raw


# ═══════════════════════════════════════════════════════════
#  FULL SSI COMPUTATION
# ═══════════════════════════════════════════════════════════

def compute_r_base(components):
    """Compute R_base from pre-normalised component scores."""
    R_base = 0
    for comp, weight in COMPONENT_WEIGHTS.items():
        R_base += weight * (components.get(comp, 0))
    return R_base


def compute_r_median(R_base, modifiers):
    """
    Apply the SSI Index modifier chain to R_base.

    PR-3 (F-L3-4 closure): retires the hardcoded 5-modifier multiplication
    in favour of the canonical MODIFIER_REGISTRY chain. Multiplicative
    modifiers compose inside soft_clip_upper (the overflow regime); additive
    modifiers (v4.2's R6c_flood per Italy PGRA + the rest of the additive
    family) layer on AFTER soft_clip_upper so that flood risk doesn't get
    compressed away near R=1.0.

    Master equation per the v4.0.2 methodology spec:
        R_final = soft_clip_upper(R_base × Π mult_i) + Σ (add_i − 1.0)

    Per Convention #56, this function is the canonical multiplicative chain.
    Engine extensions (v4.2's R6c additive, R8 reverse-signed adaptive
    capacity, R10 just-energy, etc.) land in MODIFIER_REGISTRY without
    touching this function — proving the extension contract.

    Args:
        R_base: Pre-modifier resilience score (output of compute_r_base).
        modifiers: Dict of {modifier_name: float}. Unknown names are
                   skipped with a warning (compute_modifier_terms behaviour).

    Returns:
        R_median (float) — the modifier-adjusted resilience score.
    """
    mult_product, add_sum = compute_modifier_terms(modifiers)
    R_compressed = soft_clip_upper(R_base * mult_product)
    return R_compressed + add_sum


# ═══════════════════════════════════════════════════════════
#  MONTE CARLO HELPERS (PR-2)
# ═══════════════════════════════════════════════════════════

# Canonical metric order — full 20-metric set in SIGMA_TOTAL key order.
# Defines the index used by the numpy arrays for vectorized perturbation.
# Zero-sigma metrics (S2, S3) are kept in the order so their INTRA_WEIGHTS
# contributions still flow into R_base; they receive no MC perturbation
# (sigma=0 → base × (1 + 0×z) = base, mathematically correct).
_METRIC_ORDER = tuple(SIGMA_TOTAL.keys())


def _build_correlation_matrix(metrics=None):
    """
    Construct a symmetric correlation matrix from METRIC_CORRELATIONS dict.

    Args:
        metrics: Ordered tuple of metric names. Default _METRIC_ORDER.

    Returns:
        numpy.ndarray of shape (n, n) where n = len(metrics).
        Diagonal is 1.0; off-diagonal entries reflect METRIC_CORRELATIONS;
        unspecified pairs are 0.

    Note: The raw matrix may not be positive-definite when high-magnitude
    correlations (e.g. C1-C2=0.82, C1-E1=0.75) coexist with implied
    transitive constraints (C2-E1 unspecified ≈ 0). _nearest_pd_correlation
    projects this to the nearest PD correlation matrix before Cholesky.
    """
    if metrics is None:
        metrics = _METRIC_ORDER
    n = len(metrics)
    corr = np.eye(n)
    idx = {m: i for i, m in enumerate(metrics)}

    for (a, b), rho in METRIC_CORRELATIONS.items():
        if a in idx and b in idx:
            i, j = idx[a], idx[b]
            corr[i, j] = rho
            corr[j, i] = rho

    return corr


def _nearest_pd_correlation(M, eig_floor=1e-3):
    """
    Project a symmetric matrix to the nearest positive-definite correlation
    matrix via eigenvalue clipping (Higham 2002, simplified variant).

    Steps:
      1. Eigendecompose M = V Λ V^T.
      2. Clip eigenvalues at `eig_floor` (>0 ensures strict PD).
      3. Reconstruct M' = V Λ' V^T.
      4. Renormalize so diag(M') = 1.0 (correlation-matrix constraint).

    The projection minimally perturbs the matrix in Frobenius-norm sense;
    correlation pairs that are already mutually consistent (low magnitude,
    no transitive conflict) pass through unchanged. The procedure may
    materially shift the highest-magnitude pairs when the raw matrix
    contains transitive inconsistencies (the v4.0.2 condition).

    Audit note: the absolute deltas between target and projected
    correlations are printed by the module-load diagnostic below; any
    delta exceeding ±0.15 is a methodology candidate for the v4.2
    Stage 2 calibration pass (re-elicit the inconsistent block).
    """
    eigvals, eigvecs = np.linalg.eigh(M)
    eigvals_clipped = np.maximum(eigvals, eig_floor)
    M_pd = eigvecs @ np.diag(eigvals_clipped) @ eigvecs.T
    # Renormalize diagonal back to 1.0
    d = np.sqrt(np.diag(M_pd))
    M_pd = M_pd / np.outer(d, d)
    # Symmetrize defensively (round-off can break symmetry by ~1e-15)
    M_pd = 0.5 * (M_pd + M_pd.T)
    return M_pd


def _build_metric_weights(metrics=None, intra=None):
    """
    For each metric m, weight_m = COMPONENT_WEIGHTS[comp(m)] × intra[comp(m)][m].

    These are the per-metric contribution weights for the weighted-sum
    R_base computation. Vectorized form: R_base_samples = perturbed @ weights.

    Args:
        metrics: Ordered tuple of metric names. Default _METRIC_ORDER.
        intra: INTRA_WEIGHTS override (default module-level constant).

    Returns:
        numpy.ndarray of shape (n,) where n = len(metrics).
    """
    if metrics is None:
        metrics = _METRIC_ORDER
    if intra is None:
        intra = INTRA_WEIGHTS

    weights = np.zeros(len(metrics))
    for i, m in enumerate(metrics):
        for comp, mdict in intra.items():
            if m in mdict:
                weights[i] = COMPONENT_WEIGHTS[comp] * mdict[m]
                break
    return weights


def _derive_metric_values_from_components(components, metrics=None, intra=None):
    """
    Bridge: derive per-metric values from component-level scores.

    Used when raw 20-metric values are not available on the substation
    record (the common pre-PR-3 state). For each metric m, the value is
    the score of its parent component. This approximation matches the
    pre-PR-2 component-level engine; once L2 enrichment is updated to
    pass raw metric values, this fallback can be retired.

    Returns:
        numpy.ndarray of shape (n,) where n = len(metrics).
    """
    if metrics is None:
        metrics = _METRIC_ORDER
    if intra is None:
        intra = INTRA_WEIGHTS

    metric_values = np.zeros(len(metrics))
    for i, m in enumerate(metrics):
        for comp, mdict in intra.items():
            if m in mdict:
                metric_values[i] = components.get(comp, 0.0)
                break
    return metric_values


def _soft_clip_upper_vectorized(R_raw):
    """
    Vectorized soft_clip_upper. Identical math to the scalar form
    (line ~96) but applied element-wise to a numpy array.

    For R_raw <= 1.0: identity.
    For R_raw > 1.0: 1.0 - 1/(1 + exp(20 * (R_raw - 1.05)))
    """
    return np.where(
        R_raw <= 1.0,
        R_raw,
        1.0 - 1.0 / (1.0 + np.exp(20.0 * (R_raw - 1.05)))
    )


# Cache the Cholesky decomposition + weight vector at module import.
# Both depend only on module-level constants (METRIC_CORRELATIONS,
# COMPONENT_WEIGHTS, INTRA_WEIGHTS, SIGMA_TOTAL), so they're effectively
# constants and we don't pay for them per-substation.
_CORR_MATRIX_RAW = _build_correlation_matrix()
_CORR_MATRIX = _nearest_pd_correlation(_CORR_MATRIX_RAW, eig_floor=1e-3)
_CHOLESKY_L = np.linalg.cholesky(_CORR_MATRIX)
_METRIC_WEIGHTS_VEC = _build_metric_weights()
_SIGMA_VEC = np.array([SIGMA_TOTAL[m] for m in _METRIC_ORDER])


# ═══════════════════════════════════════════════════════════
#  MONTE CARLO (PR-2)
# ═══════════════════════════════════════════════════════════

def monte_carlo(components, modifiers, iterations=10_000, seed=None,
                metric_values=None, intra_weights=None):
    """
    Vectorized Monte Carlo simulation for a single substation.

    Per F-L3-1: default 10,000 iterations (was 1,000 in pre-PR-2 production).
    Per F-L3-2: applies METRIC_CORRELATIONS via Cholesky decomposition
                (correlated Gaussian perturbation — the "20×20 Gaussian
                copula" of the methodology spec).
    Per F-L3-3: replaces component-level perturbation with metric-level
                perturbation (one sigma per SIGMA_TOTAL key — the 18
                non-zero-sigma metrics of the 20-metric set).
    Per F-L3-4: uses MODIFIER_REGISTRY (PR-1) — every modifier present in
                `modifiers` dict participates (within its declared range),
                not just the 5 hardcoded historical ones.

    Args:
        components: Dict of component-level scores {C, V, I, E, S, T → float}.
                    Used as fallback when metric_values is None.
        modifiers: Dict of {modifier_name: float} from substation record.
        iterations: Number of Monte Carlo samples (default 10,000).
        seed: RNG seed for reproducibility (None = non-deterministic).
        metric_values: Optional dict of {metric_name: float} for the 18+
                       non-zero-sigma metrics. If provided, used directly;
                       if None, derived from `components` via INTRA_WEIGHTS
                       (the pre-PR-3 compatibility path).
        intra_weights: Override INTRA_WEIGHTS (None = module default).

    Returns:
        dict with R_median, R_P5, R_P95, CI_width, P_critical, skewness.

    Performance:
        For 10,000 iterations × 18 metrics: ~1-2 ms per substation on a
        modern CPU. Fleet-level (30k US substations × 10k iter) completes
        in ~30-60 seconds — ~30× faster than the pre-PR-2 pure-Python
        component-level 1,000-iteration engine.
    """
    if seed is not None:
        np.random.seed(seed)

    # ── 1. Resolve metric values (vectorized form) ──
    if metric_values is not None:
        base_vals = np.array([metric_values.get(m, 0.0) for m in _METRIC_ORDER])
    else:
        base_vals = _derive_metric_values_from_components(
            components, _METRIC_ORDER, intra_weights or INTRA_WEIGHTS
        )

    # ── 2. Compute modifier terms ONCE outside the MC loop (PR-3 efficiency) ──
    mult_product, add_sum = compute_modifier_terms(modifiers)

    # ── 3. Sample (iterations × n_metrics) independent standard Gaussians ──
    z_independent = np.random.standard_normal((iterations, len(_METRIC_ORDER)))

    # ── 4. Apply correlation via Cholesky (Gaussian copula) ──
    # If z ~ N(0, I), then z @ L.T ~ N(0, L L.T) = N(0, corr)
    z_correlated = z_independent @ _CHOLESKY_L.T

    # ── 5. Perturb metrics: m_i × (1 + sigma_i × z_i), then clip to [0, 1] ──
    perturbed = np.clip(
        base_vals * (1.0 + z_correlated * _SIGMA_VEC),
        0.0, 1.0
    )

    # ── 6. Compute R_base per iteration via vectorized weighted sum ──
    R_base_samples = perturbed @ _METRIC_WEIGHTS_VEC  # shape (iterations,)

    # ── 7. Apply multiplicative modifier chain + soft_clip_upper ──
    R_raw_samples = R_base_samples * mult_product
    R_samples = _soft_clip_upper_vectorized(R_raw_samples)

    # ── 8. Apply additive modifiers (R6c flood per v4.2 spec) OUTSIDE soft_clip ──
    R_samples = R_samples + add_sum

    # ── 9. Statistics ──
    R_median = float(np.median(R_samples))
    R_P5 = float(np.percentile(R_samples, 5))
    R_P95 = float(np.percentile(R_samples, 95))
    P_critical = float(np.mean(R_samples >= 0.75))

    # Skewness via Pearson moment coefficient
    mean_R = float(np.mean(R_samples))
    std_R = float(np.std(R_samples, ddof=1))
    if std_R > 0:
        skew = float(np.mean(((R_samples - mean_R) / std_R) ** 3))
    else:
        skew = 0.0

    return {
        "R_median": round(R_median, 4),
        "R_P5": round(R_P5, 4),
        "R_P95": round(R_P95, 4),
        "CI_width": round(R_P95 - R_P5, 4),
        "skewness": round(skew, 4),
        "P_critical": round(P_critical, 4),
    }


def score_substation(sub, seismic_update=None, climate_update=None, socio_update=None):
    """
    Rescore a single substation with updated ingestion data.

    Args:
        sub: Current substation dict from ssi-data.json
        seismic_update: New seismic data {"pga_g": float, "zone": int}
        climate_update: New climate trajectories {"I1_trajectory": float, ...}
        socio_update: New socio-economic data {"V_socio": float, ...}

    Returns:
        Updated substation dict (deep copy with new scores)
    """
    updated = deepcopy(sub)

    # ── Apply seismic update ──
    if seismic_update:
        pga_new = seismic_update.get("pga_g", 0.03)
        zone_new = seismic_update.get("zone", 4)

        # Zone weight mapping for R6b computation
        zone_weights = {1: 1.50, 2: 1.25, 3: 1.00, 4: 0.75}
        zone_weight = zone_weights.get(zone_new, 1.0)

        R6b = compute_r6b_seismic(pga_new, zone_weight)

        updated["seismic"] = {
            "zone": zone_new,
            "pga_g": round(pga_new, 4),
            "R6_seismic": round(R6b, 4),
        }
        updated["modifiers"]["R6_seismic"] = round(R6b, 4)

    # ── Apply climate trajectory update ──
    if climate_update:
        updated["climate_trajectory"] = {
            "I1_trajectory": climate_update.get("I1_trajectory", 1.0),
            "I2_trajectory": climate_update.get("I2_trajectory", 1.0),
            "I3_trajectory": climate_update.get("I3_trajectory", 1.0),
        }

    # ── Apply socio-economic update ──
    if socio_update and "V_socio" in socio_update:
        se = updated.get("socio_economic", {})
        for key in ["V_socio", "EP_rate_region", "gdp_per_capita", "unemployment_rate",
                     "E2_local", "rd_pct_gdp", "elderly_pct", "migration_score"]:
            if key in socio_update:
                se[key] = socio_update[key]
        updated["socio_economic"] = se

    # ── Recompute scores ──
    components = updated.get("components", {})
    modifiers = updated.get("modifiers", {})

    # R_base (unchanged unless components updated)
    R_base = compute_r_base(components)
    updated["R_base_median"] = round(R_base, 4)

    # R_median with updated modifiers
    R_med = compute_r_median(R_base, modifiers)

    # Monte Carlo
    # PR-2 (F-L3-1): 10,000 iterations is the production default.
    # Numpy-vectorized engine completes 10k × 18 metrics in ~1-2 ms per
    # substation; the prior 1,000-iteration override (pure-Python) was a
    # browser-MC compatibility shim, retired with PR-4 JS engine retirement.
    mc = monte_carlo(components, modifiers, iterations=10_000)

    updated["R_median"] = mc["R_median"]
    updated["R_P5"] = mc["R_P5"]
    updated["R_P95"] = mc["R_P95"]
    updated["CI_width"] = mc["CI_width"]
    updated["skewness"] = mc["skewness"]
    updated["P_critical"] = mc["P_critical"]
    updated["R_unclipped"] = mc["R_median"]
    updated["modifier_impact"] = round(mc["R_median"] - R_base, 4)
    updated["modifier_pct"] = f"{abs(mc['R_median'] - R_base) / max(R_base, 0.001) * 100:.1f}%"
    updated["classification"] = classify_band(mc["R_median"])
    updated["confidence_tier"] = classify_confidence(mc["R_P5"], mc["R_P95"])

    # ── PR-3: Per-modifier provenance for audit trail + v4.2 W-axis ──
    # mult_product and add_sum are the two scalars that fully describe the
    # modifier chain's contribution; modifier_impacts dict gives the per-
    # modifier delta-from-identity (round(value − 1.0, 4)) so a reader can
    # see exactly which modifier shifted the score by how much. Renderers
    # consume these for tooltips + the "modifier breakdown" widget; the
    # v4.2 W1-W10 anti-maladaptation gate consumes them to verify that
    # adaptive capacity (R8, reverse-signed) is balanced against new risk
    # injections (R6c flood, R6d wildfire, R6e winter, R9 compound).
    mult_product, add_sum = compute_modifier_terms(modifiers)
    updated["mult_product"] = round(mult_product, 4)
    updated["add_sum"] = round(add_sum, 4)
    updated["modifier_impacts"] = per_modifier_impacts(modifiers)

    return updated


# ═══════════════════════════════════════════════════════════
#  FLEET-LEVEL ANALYTICS
# ═══════════════════════════════════════════════════════════

def compute_fleet_summary(substations):
    """Compute fleet-level statistics from scored substations.

    Classes B/C fix (16 July 2026, FAILURE_SOLVING_PROPOSAL_20260716.md §3):
    Substations with R_median=None are legitimate pre-L3 state (Convention #56
    per CONVENTION_78 §4bis.4). Filter them out of statistical aggregations and
    count them separately in bands as "Unclassified" — Convention #56 visibly-
    honest degradation.
    """
    n = len(substations)
    if n == 0:
        return {}

    # Phase 2B-1 (25 June 2026): 4-band → 5-band with Extreme
    # Classes B/C fix: Unclassified band absorbs pre-L3 None R_median subs
    bands = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0, "Extreme": 0, "Unclassified": 0}
    conf = {"high": 0, "medium": 0, "low": 0}

    for s in substations:
        bands[classify_band(s.get("R_median"))] += 1
        conf[classify_confidence(s.get("R_P5"), s.get("R_P95"))] += 1

    # Convention #56: statistics computed on subs with numeric R_median only
    scored_R_vals = sorted(
        s["R_median"] for s in substations if s.get("R_median") is not None
    )
    n_scored = len(scored_R_vals)

    summary = {
        "total": n,
        "n_scored": n_scored,
        "n_unclassified_pre_l3": n - n_scored,
        "bands": bands,
        "band_pct": {k: round(v / n * 100, 1) for k, v in bands.items()},
        "confidence_tiers": conf,
        "confidence_pct": {k: round(v / n * 100, 1) for k, v in conf.items()},
    }

    # Statistical aggregates only meaningful when scored subs exist
    if scored_R_vals:
        summary.update({
            "median_R": round(_percentile(scored_R_vals, 0.50), 4),
            "mean_R": round(sum(scored_R_vals) / n_scored, 4),
            "P5": round(_percentile(scored_R_vals, 0.05), 4),
            "P95": round(_percentile(scored_R_vals, 0.95), 4),
        })
    else:
        # Convention #56 visibly-honest: mark stats as pending L3 rescore
        summary.update({
            "median_R": None,
            "mean_R": None,
            "P5": None,
            "P95": None,
            "_stats_pending_l3_rescore": True,
        })

    return summary


def compute_regional_summary(substations):
    """Compute per-region aggregated statistics."""
    regions = {}
    for s in substations:
        r = s.get("region", "Unknown")
        if r not in regions:
            regions[r] = []
        regions[r].append(s)

    summaries = []
    for region, subs in regions.items():
        n = len(subs)
        # Classes B/C fix: filter pre-L3 None R_median subs per Convention #56
        scored_R_vals = sorted(
            s["R_median"] for s in subs if s.get("R_median") is not None
        )
        n_scored = len(scored_R_vals)
        # Phase 2B-1 (25 June 2026): 4-band → 5-band with Extreme
        # Classes B/C fix: Unclassified band absorbs pre-L3 None R_median subs
        bands = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0, "Extreme": 0, "Unclassified": 0}
        for s in subs:
            bands[classify_band(s.get("R_median"))] += 1

        # Phase 2B-1 (25 June 2026): pct_critical stays SINGLE-BAND
        # (its original semantic per pre-Phase-2B-1) to preserve API
        # back-compat. pct_high stays CUMULATIVE-FROM-HIGH (extended
        # to include Extreme so the "top-of-fleet share" semantic
        # holds). New pct_extreme is peer to pct_critical (single-band).
        entry = {
            "region": region,
            "count": n,
            "n_scored": n_scored,
            "bands": bands,
            "pct_critical": round(bands["Critical"] / n * 100, 1),
            "pct_extreme":  round(bands["Extreme"]  / n * 100, 1),
            "pct_high": round((bands["High"] + bands["Critical"] + bands["Extreme"]) / n * 100, 1),
        }
        if scored_R_vals:
            entry.update({
                "median_R": round(_percentile(scored_R_vals, 0.50), 4),
                "mean_R": round(sum(scored_R_vals) / n_scored, 4),
            })
        else:
            entry.update({
                "median_R": None,
                "mean_R": None,
                "_stats_pending_l3_rescore": True,
            })
        summaries.append(entry)

    # Sort: regions with numeric median_R descending, then unclassified regions last
    return sorted(
        summaries,
        key=lambda x: (x["median_R"] is None, -(x["median_R"] or 0.0)),
    )


# ═══════════════════════════════════════════════════════════
#  UTILITIES
# ═══════════════════════════════════════════════════════════

def _gaussian_random():
    """Box-Muller transform for Gaussian random variable."""
    u = random.random()
    v = random.random()
    while u == 0:
        u = random.random()
    while v == 0:
        v = random.random()
    return math.sqrt(-2.0 * math.log(u)) * math.cos(2.0 * math.pi * v)


def _percentile(sorted_vals, p):
    """Compute percentile from sorted array."""
    n = len(sorted_vals)
    if n == 0:
        return 0
    idx = p * (n - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return sorted_vals[lo]
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (idx - lo)
