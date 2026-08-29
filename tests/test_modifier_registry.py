"""
SSI Pipeline — Modifier Registry Tests (Phase 1 PR-1)

12 tests covering the modifier registry foundation:
- Registry shape + integrity (tests 1-5)
- compute_modifier_terms behavior (tests 6-10)
- per_modifier_impacts behavior (test 11)
- Real-world Korea ssi-data.json modifier shape (test 12)

Cross-reference: PHASE_1_IMPLEMENTATION_PLAN.md PR-1 §"Test criteria (the 12 PR-1 tests)"
"""

import logging

import pytest

from scripts.pipeline.scoring.modifier_registry import (
    MODIFIER_REGISTRY,
    compute_modifier_terms,
    per_modifier_impacts,
)


# ═══════════════════════════════════════════════════════════
#  REGISTRY SHAPE + INTEGRITY (Tests 1-5)
# ═══════════════════════════════════════════════════════════

class TestRegistryShape:
    """Tests 1-5: registry shape and self-consistency invariants."""

    def test_1_registry_has_17_entries(self):
        """Registry has exactly 17 entries.

        v4.24 recount (18 August 2026, GATE-A-11-REVISED hard cutover):
        - 5 canonical v4.0.2 (R3_C_mult, R4_F_topo, R6_restoration, R6_seismic, R7_cyber-tombstoned)
        - 1 v4.24 R7_cyber_v2 primary emit path (CRA + NIS2 register-anchored)
        - 5 per-country adaptations (R6_volcanic, R6_drought, R6_armed_conflict, R6_typhoon, R6_chaebol)
        - 6 v4.2-ready (R6c_flood, R6d_wildfire, R6e_winter, R8_adapt, R9_compound, R10_just)
        = 17 total. R7_cyber v1 entry retained (with retired: True) for audit-trail readers.
        """
        assert len(MODIFIER_REGISTRY) == 17, (
            f"Expected 17 entries, got {len(MODIFIER_REGISTRY)}. "
            f"Keys: {sorted(MODIFIER_REGISTRY.keys())}"
        )

    def test_2_every_entry_has_required_keys(self):
        """Every entry has the 5 required metadata keys."""
        required = {"type", "default", "range", "introduced", "countries"}
        for name, spec in MODIFIER_REGISTRY.items():
            missing = required - set(spec.keys())
            assert not missing, f"Modifier '{name}' missing keys: {missing}"

    def test_3_every_default_is_within_range(self):
        """Every modifier's default value is within its declared range."""
        for name, spec in MODIFIER_REGISTRY.items():
            lo, hi = spec["range"]
            default = spec["default"]
            assert lo <= default <= hi, (
                f"Modifier '{name}' default {default} outside range ({lo}, {hi})"
            )

    def test_4_type_is_mult_or_add(self):
        """Every modifier's type is 'mult' or 'add'."""
        for name, spec in MODIFIER_REGISTRY.items():
            assert spec["type"] in ("mult", "add"), (
                f"Modifier '{name}' has invalid type '{spec['type']}'"
            )

    def test_5_range_lo_le_hi_for_every_entry(self):
        """Every modifier's range satisfies lo <= hi."""
        for name, spec in MODIFIER_REGISTRY.items():
            lo, hi = spec["range"]
            assert lo <= hi, (
                f"Modifier '{name}' has invalid range (lo > hi): ({lo}, {hi})"
            )


# ═══════════════════════════════════════════════════════════
#  compute_modifier_terms BEHAVIOR (Tests 6-10)
# ═══════════════════════════════════════════════════════════

class TestComputeModifierTerms:
    """Tests 6-10: compute_modifier_terms behavior."""

    def test_6_empty_modifiers_returns_identity(self, empty_modifiers):
        """compute_modifier_terms({}) returns (1.0, 0.0) — identity."""
        mult, add = compute_modifier_terms(empty_modifiers)
        assert mult == 1.0, f"Expected mult=1.0, got {mult}"
        assert add == 0.0, f"Expected add=0.0, got {add}"

    def test_7_single_multiplicative_modifier(self):
        """compute_modifier_terms({'R3_C_mult': 1.1}) returns (1.1, 0.0)."""
        mult, add = compute_modifier_terms({"R3_C_mult": 1.1})
        assert mult == pytest.approx(1.1)
        assert add == 0.0

    def test_8_single_additive_modifier(self):
        """compute_modifier_terms({'R6c_flood': 1.2}) returns (1.0, 0.2) — additive."""
        mult, add = compute_modifier_terms({"R6c_flood": 1.2})
        assert mult == 1.0, f"Expected mult=1.0 (no multiplicative mods), got {mult}"
        assert add == pytest.approx(0.2), f"Expected add=0.2, got {add}"

    def test_9_out_of_range_clipped_to_range_hi(self, out_of_range_modifiers):
        """Out-of-range values are clipped to range bounds before applying."""
        mult, add = compute_modifier_terms(out_of_range_modifiers)
        # R3_C_mult=2.0 should clip to 1.50, R8_adapt=0.90 should clip to 0.92.
        # (Was R7_cyber=0.90 -> 0.99 until the v4.24 cutover retired it.)
        expected_mult = 1.50 * 0.92
        assert mult == pytest.approx(expected_mult), (
            f"Expected clipped mult={expected_mult}, got {mult}"
        )
        assert add == 0.0

    def test_10_unknown_modifier_logged_warning_no_crash(self, unknown_modifiers, caplog):
        """Unknown modifier keys are skipped with a warning, no exception."""
        with caplog.at_level(logging.WARNING):
            mult, add = compute_modifier_terms(unknown_modifiers)
        # Should compute from only the known modifier (R3_C_mult=1.05)
        assert mult == pytest.approx(1.05), (
            f"Expected only R3_C_mult applied (mult=1.05), got {mult}"
        )
        assert add == 0.0
        # Warning should mention the unknown modifier names
        assert "Unknown modifier" in caplog.text
        assert "R99_unknown" in caplog.text or "totally_made_up" in caplog.text


# ═══════════════════════════════════════════════════════════
#  per_modifier_impacts BEHAVIOR (Test 11)
# ═══════════════════════════════════════════════════════════

class TestPerModifierImpacts:
    """Test 11: per_modifier_impacts provenance trail."""

    def test_11_per_modifier_impacts_returns_delta_dict(self):
        """per_modifier_impacts returns {name: round(value - 1.0, 4)} for known modifiers."""
        modifiers = {
            "R3_C_mult": 1.15,
            "R4_F_topo": 0.95,
            "R6c_flood": 1.20,
            "unknown_mod": 5.0,  # should be excluded from output
        }
        impacts = per_modifier_impacts(modifiers)
        assert impacts == {
            "R3_C_mult": 0.15,
            "R4_F_topo": -0.05,
            "R6c_flood": 0.20,
        }, f"Got: {impacts}"
        # Unknown modifier should be excluded
        assert "unknown_mod" not in impacts


# ═══════════════════════════════════════════════════════════
#  REAL-WORLD KOREA INTEGRATION (Test 12)
# ═══════════════════════════════════════════════════════════

class TestKoreaIntegration:
    """Test 12: Korea's actual ssi-data.json modifier shape is supported."""

    def test_12_korea_modifier_dict_processes_without_error(self, korea_modifiers):
        """Korea substations carry R6_typhoon + R6_chaebol — both in registry now."""
        # This is the F-L3-4 regression test: pre-PR-1, Korea's R6_typhoon and
        # R6_chaebol were stored but never multiplied. Post-PR-1 they're
        # registered; PR-3 will multiply them.
        mult, add = compute_modifier_terms(korea_modifiers)
        # All 7 Korea modifiers are multiplicative (no R6c flood in Korea)
        assert add == 0.0
        # Multiplicative product should include R6_typhoon=1.08 and R6_chaebol=1.06
        # Naive product (unclipped): 1.05 * 1.10 * 0.98 * 1.02 * 1.08 * 1.06 * 1.015
        expected = 1.05 * 1.10 * 0.98 * 1.02 * 1.08 * 1.06 * 1.015
        assert mult == pytest.approx(expected, rel=1e-9), (
            f"Expected Korea mult={expected:.6f}, got {mult:.6f}"
        )
        # R6_typhoon and R6_chaebol must appear in per-modifier impacts
        impacts = per_modifier_impacts(korea_modifiers)
        assert "R6_typhoon" in impacts, "R6_typhoon missing from per-modifier impacts"
        assert "R6_chaebol" in impacts, "R6_chaebol missing from per-modifier impacts"
        assert impacts["R6_typhoon"] == pytest.approx(0.08)
        assert impacts["R6_chaebol"] == pytest.approx(0.06)


# ═══════════════════════════════════════════════════════════
#  COHORT-LEVEL INTEGRATION (bonus tests)
# ═══════════════════════════════════════════════════════════

class TestCohortIntegration:
    """Bonus tests: verify the other per-country adaptation cohorts."""

    def test_colombia_volcanic_drought_armed_conflict(self, colombia_modifiers):
        """Colombia carries R6_volcanic + R6_drought + R6_armed_conflict — all in registry."""
        mult, add = compute_modifier_terms(colombia_modifiers)
        assert add == 0.0  # no additive in Colombia v4.0.2
        impacts = per_modifier_impacts(colombia_modifiers)
        assert "R6_volcanic" in impacts
        assert "R6_drought" in impacts
        assert "R6_armed_conflict" in impacts

    def test_v4_2_modifier_set_with_additive_r6c(self, v4_2_modifiers):
        """v4.2 modifier set with R6c additive flood + 5 multiplicative families."""
        mult, add = compute_modifier_terms(v4_2_modifiers)
        # R6c_flood=1.15 → contributes 0.15 to add_sum
        assert add == pytest.approx(0.15), (
            f"Expected add=0.15 from R6c_flood=1.15, got {add}"
        )
        # All other modifiers are multiplicative
        impacts = per_modifier_impacts(v4_2_modifiers)
        assert impacts["R6c_flood"] == pytest.approx(0.15)
        assert "R8_adapt" in impacts
        # R8_adapt=0.98 → impact=-0.02 (reverse-signed adaptive capacity)
        assert impacts["R8_adapt"] == pytest.approx(-0.02)
