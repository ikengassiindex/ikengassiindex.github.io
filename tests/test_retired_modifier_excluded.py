"""A retired modifier is not applied, and its absence is not silent.

modifier_registry.py has declared R7_cyber retired since the v4.24 hard cutover
of 18 August 2026, in a comment that names this exact requirement:

    Any pipeline reader referencing "R7_cyber" post v4.24 MUST migrate to
    "R7_cyber_v2".

compute_modifier_terms is that reader and did not honour it, so every record
carrying both modifiers had the cyber term applied twice. Sweden's published
scores carry that double-count today. These tests exist so it cannot come back
by omission.
"""
import logging
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from pipeline.scoring.modifier_registry import (
    MODIFIER_REGISTRY, compute_modifier_terms, retired_modifiers_present)


def test_retired_modifier_declares_its_successor():
    """The prose said 'superseded by R7_cyber_v2'; the code can now read it."""
    spec = MODIFIER_REGISTRY["R7_cyber"]
    assert spec.get("retired")
    assert spec.get("superseded_by") == "R7_cyber_v2"


def test_cyber_is_applied_once_when_both_are_present():
    """The live shape: every v4.2-cohort record carries both."""
    mult, _ = compute_modifier_terms(
        {"R7_cyber": 1.0259, "R7_cyber_v2": 1.0345, "R3_C_mult": 0.972})
    assert abs(mult - (1.0345 * 0.972)) < 1e-12, (
        "R7_cyber is still in the chain — the double-count is back")


def test_retired_modifier_alone_is_not_applied():
    mult, _ = compute_modifier_terms({"R7_cyber": 1.0259})
    assert abs(mult - 1.0) < 1e-12


def test_dropping_it_without_a_successor_is_logged_as_an_error(caplog):
    """Convention #56: a lost signal is announced, not absorbed quietly."""
    with caplog.at_level(logging.ERROR):
        compute_modifier_terms({"R7_cyber": 1.0259})
    assert "retired" in caplog.text
    assert "R7_cyber_v2" in caplog.text


def test_helper_separates_clean_migration_from_lost_signal():
    both = retired_modifiers_present({"R7_cyber": 1.02, "R7_cyber_v2": 1.03})
    assert both["R7_cyber"]["successor_present"] is True
    alone = retired_modifiers_present({"R7_cyber": 1.02})
    assert alone["R7_cyber"]["successor_present"] is False
    assert retired_modifiers_present({"R3_C_mult": 1.05}) == {}


def test_live_modifiers_are_untouched():
    """The fix must not quietly drop anything else."""
    mult, add = compute_modifier_terms(
        {"R3_C_mult": 0.972, "R4_F_topo": 0.9913, "R6c_flood": 1.143174})
    assert abs(mult - (0.972 * 0.9913)) < 1e-12
    assert abs(add - 0.143174) < 1e-9
