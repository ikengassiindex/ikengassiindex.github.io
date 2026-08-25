"""
SSI Pipeline — compute_r_median Tests (Phase 1 PR-3)

8 tests pinning the registry-driven multiplicative + additive modifier chain:

- Tests 1-2: identity and no-op semantics
- Tests 3-5: pure-multiplicative, pure-additive, and mixed regimes
- Test 6: soft_clip_upper trigger when R_raw exceeds 1.0
- Test 7: unknown modifier graceful degradation
- Test 8: master-equation invariant (R = soft_clip(R_base × Π mult) + Σ add)

Cross-reference: PHASE_1_IMPLEMENTATION_PLAN.md PR-3 §"Test criteria (the 15 PR-3 tests)"
                 AUDIT_v4_0_2_PRE_v4_2_FOUNDATION.md F-L3-4 closure
"""

import logging

import pytest

from scripts.pipeline.scoring.engine import (
    compute_r_median,
    soft_clip_upper,
)
from scripts.pipeline.scoring.modifier_registry import compute_modifier_terms


# ═══════════════════════════════════════════════════════════
#  IDENTITY / NO-OP SEMANTICS (Tests 1-2)
# ═══════════════════════════════════════════════════════════

class TestIdentity:
    """The empty/identity cases — preserve R_base under no-op."""

    def test_1_empty_modifiers_returns_r_base(self):
        """compute_r_median(0.5, {}) → 0.5 (no modifiers)."""
        assert compute_r_median(0.5, {}) == pytest.approx(0.5)

    def test_2_identity_multiplicative_returns_r_base(self):
        """compute_r_median(0.5, {'R3_C_mult': 1.0}) → 0.5 (identity mult)."""
        assert compute_r_median(0.5, {"R3_C_mult": 1.0}) == pytest.approx(0.5)


# ═══════════════════════════════════════════════════════════
#  MULTIPLICATIVE / ADDITIVE / MIXED (Tests 3-5)
# ═══════════════════════════════════════════════════════════

class TestModifierTypes:
    """The three modifier-application regimes."""

    def test_3_single_multiplicative_modifier_amplifies(self):
        """compute_r_median(0.5, {'R3_C_mult': 1.2}) → 0.5 × 1.2 = 0.6."""
        result = compute_r_median(0.5, {"R3_C_mult": 1.2})
        assert result == pytest.approx(0.6)

    def test_4_single_additive_modifier_shifts_outside_soft_clip(self):
        """compute_r_median(0.5, {'R6c_flood': 1.1}) → 0.5 + 0.1 = 0.6."""
        # R6c_flood is type 'add' with default 1.0 → contributes (val − 1.0)
        result = compute_r_median(0.5, {"R6c_flood": 1.1})
        assert result == pytest.approx(0.6)

    def test_5_mixed_mult_and_add_compose_correctly(self):
        """0.5 × 1.2 = 0.6 (mult), then + 0.1 (add) = 0.7."""
        result = compute_r_median(0.5, {"R3_C_mult": 1.2, "R6c_flood": 1.1})
        assert result == pytest.approx(0.7)


# ═══════════════════════════════════════════════════════════
#  SOFT_CLIP_UPPER TRIGGER (Test 6)
# ═══════════════════════════════════════════════════════════

class TestSoftClipUpper:
    """soft_clip_upper saturates R > 1.0 at 1.0; PR-3 chain must invoke it.

    M-006 (19 Aug 2026): the logistic form was replaced by min(R, 1.0) —
    the logistic was discontinuous at the threshold and inverted the
    ranking above it. These tests compare against soft_clip_upper itself,
    so they hold across the change.
    """

    def test_6_high_modifier_triggers_soft_clip(self):
        """R_base=0.95, R3_C_mult=1.40 → R_raw = 1.33 → must be compressed below R_raw."""
        R_base = 0.95
        # R_raw = 0.95 × 1.40 = 1.33 — well into soft_clip territory
        result = compute_r_median(R_base, {"R3_C_mult": 1.40})
        # Without compression result would be 1.33 — but soft_clip pulls toward 1.0
        assert result < 1.33, (
            f"soft_clip_upper not invoked: got {result}, expected < 1.33"
        )
        # Must match the scalar soft_clip_upper for the same input
        expected = soft_clip_upper(R_base * 1.40)
        assert result == pytest.approx(expected), (
            f"compute_r_median diverged from soft_clip_upper: {result} vs {expected}"
        )


# ═══════════════════════════════════════════════════════════
#  UNKNOWN MODIFIER GRACEFUL DEGRADATION (Test 7)
# ═══════════════════════════════════════════════════════════

class TestUnknownModifier:
    """Unknown modifier keys must be skipped with a warning, not crash."""

    def test_7_unknown_modifier_logs_warning_no_crash(self, caplog):
        """compute_r_median ignores unknown keys + logs warning."""
        with caplog.at_level(logging.WARNING):
            result = compute_r_median(0.5, {"R99_unknown": 1.50, "R3_C_mult": 1.1})
        # Only the known modifier should be applied: 0.5 × 1.1 = 0.55
        assert result == pytest.approx(0.55), (
            f"Unknown modifier leaked into calculation: result={result}"
        )
        # The warning must explicitly call out the unknown name
        assert "Unknown modifier" in caplog.text
        assert "R99_unknown" in caplog.text


# ═══════════════════════════════════════════════════════════
#  MASTER-EQUATION INVARIANT (Test 8)
# ═══════════════════════════════════════════════════════════

class TestMasterEquationInvariant:
    """The function MUST satisfy R = soft_clip(R_base × mult) + add for all inputs."""

    @pytest.mark.parametrize("R_base,modifiers", [
        (0.30, {"R3_C_mult": 1.05}),
        (0.50, {"R3_C_mult": 1.05, "R4_F_topo": 1.10, "R6_seismic": 1.08}),
        (0.75, {"R3_C_mult": 1.20, "R6c_flood": 1.15}),
        (0.90, {"R3_C_mult": 1.30, "R6_seismic": 1.10, "R6c_flood": 1.05}),
        (0.05, {"R3_C_mult": 0.95, "R7_cyber": 1.005}),
    ])
    def test_8_invariant_matches_decomposed_chain(self, R_base, modifiers):
        """compute_r_median(R, m) ≡ soft_clip_upper(R × mult_product) + add_sum."""
        result = compute_r_median(R_base, modifiers)
        mult_product, add_sum = compute_modifier_terms(modifiers)
        expected = soft_clip_upper(R_base * mult_product) + add_sum
        assert result == pytest.approx(expected, abs=1e-12), (
            f"Invariant breached for R_base={R_base}, modifiers={modifiers}: "
            f"got {result}, expected {expected}"
        )
