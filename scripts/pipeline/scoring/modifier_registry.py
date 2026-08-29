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
  declared range) EXCEPT those carrying `retired`, which are skipped —
  see compute_modifier_terms. Before 29 August 2026 the flag was
  declared but never read, and R7_cyber was applied alongside its own
  successor. Unknown modifiers are skipped with a warning. v4.2's
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
    # ─── R7_cyber v1 → v2 HARD CUTOVER · v4.24 methodology-version event ───
    # GATE-A-11 REVISED 18 August 2026 from dual-write (~6 months) → hard cutover at
    # Session M+1. Rationale per operator directive: thought-leadership framing
    # ("done before the market"), R7 v2 empirically better than v1 (CRA/NIS2 register-
    # anchored composite > DESI/ACN scalar proxy), NIS2 already binding since Oct 2024,
    # CRA in force since Dec 2024 — Article 14 reporting activation Sept 2026 does not
    # gate methodology adoption. See task_1108_r7_cyber_v2_preflight_20260825.yaml
    # operator_signoff_log row GATE-A-11-REVISED.
    #
    # R7_cyber (v1) — TOMBSTONED · Convention #56 retire-with-comment discipline
    # Historical v4.0.0 → v4.23 emit path (DESI/ACN documented-proxy fleet-defensible
    # fallback per §5quater dual-axis SFDR PAI discipline). NOT emitted in v4.24+
    # pipeline runs. Audit trail preserved cohort-wide via:
    #   - `_r7_cyber_v1_retired: True` marker (boolean)
    #   - `_r7_cyber_v1_value: <last-computed float>` snapshot (per-substation)
    # Any pipeline reader referencing "R7_cyber" post v4.24 MUST migrate to
    # "R7_cyber_v2". Registry entry retained (with retired: True) to enable audit-
    # trail readers and reject-with-clear-message consumer errors.
    "R7_cyber":          {"type": "mult", "default": 1.0, "range": (0.99, 1.05),
                          "introduced": "v4.0.0",
                          "retired": "v4.24 (18 August 2026, GATE-A-11-REVISED hard cutover; superseded by R7_cyber_v2)",
                          "superseded_by": "R7_cyber_v2",
                          "countries": "all"},
    #
    # R7_cyber v2 — CRA + NIS2 regulatory-vintage composite (Task #1102 workstream)
    # Envelope at v0 preserved [0.99, 1.05] for continuity with v1 (matches R7 v1 default);
    # envelope re-calibration deferred to v1 (post ENISA SRP feed availability) → v2 (post
    # 11 December 2027 CRA full applicability + SBOM per-vendor granularity).
    # Path variant = Path C+D composite (entity + product, 26 EU Path C via CRA+NIS2
    # register-read + 13-country non-EU Path D parallel constructs per D1 memo §4).
    # Weights: w_entity = 0.55 · w_product = 0.45 (BINDING sum-to-unity invariant
    # w_entity + w_product = 1.0 per V_socio precedent + Discipline #47 REGULATORY-VINTAGE
    # variant sub-discipline). Anchored Ciso-Nasser 2024 + NERC E-ISAC 2022 empirical
    # grounding — operator-response discipline dominates over vendor-vulnerability tail
    # for grid-critical infrastructure. Resolved per Gate A GATE-A-1 + GATE-A-2 operator
    # sign-off 18 August 2026 (Session B merge; see task_1108_r7_cyber_v2_preflight_20260825.yaml
    # operator_signoff_log block). See:
    #   - Report Production framing: METHODOLOGY_DISCIPLINES.md §5novies + §5decies
    #   - Rulebook subfolder: 01-R7-Cyber-v2-CRA-Integration/CRA_P1_GATE_A_DECISION_SURFACING.md
    #   - Formula construct draft: R7_CYBER_V2_FORMULA_CONSTRUCT_DRAFT.md (D2)
    # First-apply implementation module `scripts/pipeline/scoring/r7_cyber_v2.py` queued P4
    # per CRA_R7_CASCADE_PLAN_EXTENDED.md; sentinel `tests/test_r7_cyber_v2_construct.py`
    # queued alongside. Registering the entry NOW enables downstream code paths to reference
    # the modifier name without waiting for module authoring (Convention #56 discipline:
    # registry entry surfaces the intent-to-emit even before emission code lands).
    "R7_cyber_v2":       {"type": "mult", "default": 1.0, "range": (0.99, 1.05),
                          "introduced": "v4.2 (Task #1102 CRA integration · 18 August 2026 · Path C+D composite recommended · Gate A pending)",
                          "countries": "v4.2 cohort (26 EU via CRA + NIS2 + 13 non-EU parallel constructs per D1 memo §4)"},

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

        # A retired modifier is not part of the chain. The registry has said so
        # since the v4.24 hard cutover — "Any pipeline reader referencing
        # R7_cyber post v4.24 MUST migrate to R7_cyber_v2" — but this function,
        # which is that reader, never looked at the flag. It multiplied every
        # modifier present, so a record carrying both R7_cyber and R7_cyber_v2
        # had the cyber modifier applied twice. Sweden's published scores carry
        # that double-count today; every other v4.2-cohort country would have
        # acquired it on its next re-score.
        if spec.get("retired"):
            successor = spec.get("superseded_by")
            if successor and successor not in modifiers:
                # Convention #56: dropping a retired modifier with nothing in
                # its place is a loss of signal, not a tidy-up. Say so rather
                # than letting the score quietly fall. Nothing is substituted —
                # there is no honest substitute.
                logger.error(
                    "Modifier '%s' is retired (%s) and its successor '%s' is "
                    "absent from this substation; it is not applied and nothing "
                    "replaces it.", name, spec["retired"], successor)
            else:
                logger.warning("Modifier '%s' is retired; not applied.", name)
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


def retired_modifiers_present(modifiers):
    """Retired modifiers a record still carries, and whether the successor is there.

    compute_modifier_terms now skips these, so this is how a gate or an audit
    asks which records are affected without re-deriving the rule. The
    successor_present flag separates the two cases that matter: a clean
    migration (both present, the retired one simply ignored) from a record that
    loses the signal entirely because nothing replaced it.

    Returns:
        {name: {"retired": str, "superseded_by": str|None,
                "successor_present": bool}}

    Examples:
        >>> r = retired_modifiers_present({"R7_cyber": 1.02, "R7_cyber_v2": 1.03})
        >>> r["R7_cyber"]["successor_present"]
        True
        >>> retired_modifiers_present({"R3_C_mult": 1.05})
        {}
    """
    out = {}
    for name in modifiers:
        spec = MODIFIER_REGISTRY.get(name)
        if not spec or not spec.get("retired"):
            continue
        succ = spec.get("superseded_by")
        out[name] = {"retired": spec["retired"], "superseded_by": succ,
                     "successor_present": bool(succ and succ in modifiers)}
    return out


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
