"""
SSI v4.0.2 — Modifier Registry
Single source of truth for all deployed + v4.2-ready modifiers.

Introduced in Phase 1 PR-1 per AUDIT_v4_0_2_PRE_v4_2_FOUNDATION.md §7.7
Decision 3 (F-L3-4): declarative modifier registry + numpy-vectorized chain
product computed once outside the Monte Carlo loop.

Each registry entry declares:
    type        "mult" (multiplicative inside soft_clip_upper) or
                "add"  (additive outside, per v4.2 R6c flood pattern)
    default     Identity value when modifier is absent
    range       (lo, hi) clipping bounds, enforced before applying
    introduced  Which session/version this modifier first deployed
    countries   Comma-separated cohort that emits this modifier (informational)

Pre-PR-3 history:
- compute_r_median in engine.py hardcoded 5 modifiers (R3, R4, R6_restoration,
  R6_seismic, R7) — see F-L3-4 finding. Per-country modifiers (R6_typhoon for
  Korea, R6_volcanic for Iceland/Colombia/Costa Rica, etc.) were stored on each
  substation but never multiplied into R_median.

Post-PR-3 behavior:
- compute_r_median iterates this registry; every modifier present in the
  substation's `modifiers` dict participates in the score (within its
  declared range). Unknown modifiers are skipped with a warning. v4.2's
  six new modifier families (R6c, R6d, R6e, R8, R9, R10) land here as
  data-only entries — no engine code changes needed.

This module is the canonical extension point for the modifier chain.
"""

import logging

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
#  REGISTRY
# ═══════════════════════════════════════════════════════════

MODIFIER_REGISTRY = {
    # ── v4.0.2 canonical (5 modifiers — historically the only multiplied set) ──
    "R3_C_mult":         {"type": "mult", "default": 1.0, "range": (0.70, 1.50),
                          "introduced": "v4.0.0",
                          "countries": "all"},
    "R4_F_topo":         {"type": "mult", "default": 1.0, "range": (0.80, 1.35),
                          "introduced": "v4.0.0",
                          "countries": "all"},
    "R6_restoration":    {"type": "mult", "default": 1.0, "range": (0.90, 1.10),
                          "introduced": "v4.0.0",
                          "countries": "all"},
    "R6_seismic":        {"type": "mult", "default": 1.0, "range": (1.00, 1.25),
                          "introduced": "v4.0.0",
                          "countries": "all"},
    "R7_cyber":          {"type": "mult", "default": 1.0, "range": (0.99, 1.05),
                          "introduced": "v4.0.0",
                          "countries": "all"},

    # ── Per-country adaptations (deployed in ssi-data.json pre-PR-3
    # ── but not yet engine-applied; PR-3 makes them live) ────────────────
    "R6_volcanic":       {"type": "mult", "default": 1.0, "range": (1.00, 1.20),
                          "introduced": "Session 30 (Iceland)",
                          "countries": "iceland, colombia, costa-rica"},
    "R6_drought":        {"type": "mult", "default": 1.0, "range": (1.00, 1.18),
                          "introduced": "Session 34 (Israel desal) + Session 39 (Colombia hydro)",
                          "countries": "israel, colombia"},
    "R6_armed_conflict": {"type": "mult", "default": 1.0, "range": (1.00, 1.12),
                          "introduced": "Session 39 (Colombia)",
                          "countries": "colombia"},
    "R6_typhoon":        {"type": "mult", "default": 1.0, "range": (1.00, 1.15),
                          "introduced": "Session 31 (Korea)",
                          "countries": "korea"},
    "R6_chaebol":        {"type": "mult", "default": 1.0, "range": (1.00, 1.10),
                          "introduced": "Session 31 (Korea)",
                          "countries": "korea"},

    # ── v4.2-ready entries (registered now; applied when v4.2 lands) ───────
    # Adding these here means v4.2 modifier emission can begin immediately
    # post-Phase-1 without requiring an engine code change.
    "R6c_flood":         {"type": "add",  "default": 1.0, "range": (1.00, 1.30),
                          "introduced": "v4.2 spec (architecture: additive cliff outside soft_clip)",
                          "countries": "v4.2 cohort (NL, BE, DE, UK, IT, FR, ...)"},
    "R6d_wildfire":      {"type": "mult", "default": 1.0, "range": (1.00, 1.20),
                          "introduced": "v4.2 spec",
                          "countries": "v4.2 cohort"},
    "R6e_winter":        {"type": "mult", "default": 1.0, "range": (1.00, 1.15),
                          "introduced": "v4.2 spec",
                          "countries": "v4.2 cohort"},
    "R8_adapt":          {"type": "mult", "default": 1.0, "range": (0.92, 1.05),
                          "introduced": "v4.2 spec (reverse-signed adaptive capacity)",
                          "countries": "v4.2 cohort"},
    "R9_compound":       {"type": "mult", "default": 1.0, "range": (1.00, 1.10),
                          "introduced": "v4.2 spec (pairwise compound coupling)",
                          "countries": "v4.2 cohort"},
    "R10_just":          {"type": "mult", "default": 1.0, "range": (1.00, 1.12),
                          "introduced": "v4.2 spec (distributive justice / Gini-of-outage)",
                          "countries": "v4.2 cohort"},
}


# ═══════════════════════════════════════════════════════════
#  REGISTRY HELPERS
# ═══════════════════════════════════════════════════════════

def compute_modifier_terms(modifiers):
    """
    Compute the multiplicative product and additive sum for a substation's
    modifier dict. Computed ONCE per substation, outside the Monte Carlo loop.

    This is the canonical entry point used by `engine.compute_r_median` (PR-3)
    and `engine.monte_carlo` (PR-2). The MC loop multiplies the precomputed
    mult_product into R_base_samples (vectorized via numpy) and adds the
    precomputed add_sum after the soft_clip_upper. Pulling these out of the
    inner loop is the key efficiency win — Python's dynamic dispatch
    prevented compiler constant-folding when this was inline.

    Args:
        modifiers: Dict of {modifier_name: float} from the substation record.
                   Typical shape: {"R3_C_mult": 1.05, "R4_F_topo": 1.10, ...}

    Returns:
        (mult_product, add_sum) tuple of floats.
        - mult_product: product of all multiplicative modifiers (>=0)
        - add_sum: sum of (value - 1.0) for additive modifiers (R6c flood, etc.)

    Unknown modifier names (keys not in MODIFIER_REGISTRY) are silently
    skipped after logging a warning. This preserves Convention #56 forward
    compatibility while flagging schema drift.

    Out-of-range values are clipped to the modifier's declared range before
    being applied. This is a safety net against upstream emission errors.

    Examples:
        >>> compute_modifier_terms({})
        (1.0, 0.0)

        >>> compute_modifier_terms({"R3_C_mult": 1.10})
        (1.1, 0.0)

        >>> compute_modifier_terms({"R6c_flood": 1.15})
        (1.0, 0.15)

        >>> # Out-of-range value is clipped to range[1]:
        >>> compute_modifier_terms({"R3_C_mult": 2.0})
        (1.5, 0.0)
    """
    mult_product = 1.0
    add_sum = 0.0

    for name, value in modifiers.items():
        spec = MODIFIER_REGISTRY.get(name)
        if spec is None:
            logger.warning("Unknown modifier '%s' in substation; skipping", name)
            continue

        lo, hi = spec["range"]
        # Clip to declared range as a safety net against upstream emission errors.
        # See F-L1-10 + F-L4-1 findings; range enforcement is now centralized here.
        clipped = max(lo, min(hi, value))

        if spec["type"] == "mult":
            mult_product *= clipped
        elif spec["type"] == "add":
            # Additive modifiers (v4.2 R6c flood pattern): accumulate
            # (value - 1.0) so that the identity value of 1.0 contributes 0.
            add_sum += (clipped - 1.0)
        else:
            # Should be unreachable — type is validated at registry-build time.
            logger.error("Modifier '%s' has unknown type '%s'; skipping", name, spec["type"])
            continue

    return mult_product, add_sum


def per_modifier_impacts(modifiers):
    """
    Compute per-modifier contribution (value - 1.0) for the audit trail.

    Used by `engine.score_substation` (PR-3) to populate the
    substation["modifier_impacts"] field in ssi-data.json. This per-modifier
    provenance trail is what v4.2's W1-W10 audit-state classification
    requires.

    Unknown modifiers are excluded from the output (vs `compute_modifier_terms`
    which only logs a warning) — the audit trail is for declared modifiers only.

    Args:
        modifiers: Dict of {modifier_name: float} from the substation record.

    Returns:
        Dict of {modifier_name: round(value - 1.0, 4)} for every modifier
        present in the substation AND declared in MODIFIER_REGISTRY.

    Examples:
        >>> per_modifier_impacts({"R3_C_mult": 1.10, "R4_F_topo": 0.95})
        {'R3_C_mult': 0.1, 'R4_F_topo': -0.05}

        >>> per_modifier_impacts({"R6c_flood": 1.15})
        {'R6c_flood': 0.15}

        >>> per_modifier_impacts({"unknown_mod": 5.0})
        {}
    """
    return {
        name: round(value - 1.0, 4)
        for name, value in modifiers.items()
        if name in MODIFIER_REGISTRY
    }


# ═══════════════════════════════════════════════════════════
#  REGISTRY VALIDATION (run at import time)
# ═══════════════════════════════════════════════════════════

def _validate_registry():
    """
    Sanity-check the registry at import time. Catches editing errors before
    they reach production.

    Invariants:
    - Every entry has the 5 required keys (type, default, range, introduced, countries)
    - type is "mult" or "add"
    - default is within range
    - range[0] <= range[1]
    """
    required_keys = {"type", "default", "range", "introduced", "countries"}
    for name, spec in MODIFIER_REGISTRY.items():
        missing = required_keys - set(spec.keys())
        if missing:
            raise ValueError(f"Modifier '{name}' missing required keys: {missing}")
        if spec["type"] not in ("mult", "add"):
            raise ValueError(f"Modifier '{name}' has invalid type '{spec['type']}'")
        lo, hi = spec["range"]
        if lo > hi:
            raise ValueError(f"Modifier '{name}' has invalid range (lo > hi): ({lo}, {hi})")
        if not (lo <= spec["default"] <= hi):
            raise ValueError(
                f"Modifier '{name}' default {spec['default']} is outside range ({lo}, {hi})"
            )


_validate_registry()


# Public API
__all__ = ["MODIFIER_REGISTRY", "compute_modifier_terms", "per_modifier_impacts"]
