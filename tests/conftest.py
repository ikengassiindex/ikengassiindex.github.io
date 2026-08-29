"""
SSI Pipeline — pytest fixtures
Shared fixtures across all test modules.

Introduced in Phase 1 PR-1 per PHASE_1_IMPLEMENTATION_PLAN.md.
"""

import sys
from pathlib import Path

import pytest

# Make the repo root importable. The tests directory is at the repo root,
# alongside the scripts/ package. This allows tests to do
# `from scripts.pipeline.scoring.modifier_registry import ...` without
# requiring the test runner to be invoked from a specific working directory.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# ═══════════════════════════════════════════════════════════
#  SAMPLE SUBSTATION FIXTURES
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def canonical_modifiers():
    """Canonical 5-modifier dict (v4.0.2 baseline)."""
    return {
        "R3_C_mult": 1.05,
        "R4_F_topo": 1.10,
        "R6_restoration": 0.98,
        "R6_seismic": 1.08,
        "R7_cyber": 1.01,
    }


@pytest.fixture
def korea_modifiers():
    """Korea substation modifiers: canonical 5 + R6_typhoon + R6_chaebol."""
    return {
        "R3_C_mult": 1.05,
        "R4_F_topo": 1.10,
        "R6_restoration": 0.98,
        "R6_seismic": 1.02,
        "R6_typhoon": 1.08,
        "R6_chaebol": 1.06,
        "R7_cyber": 1.015,
    }


@pytest.fixture
def colombia_modifiers():
    """Colombia substation modifiers: canonical 5 + R6_volcanic + R6_drought + R6_armed_conflict."""
    return {
        "R3_C_mult": 1.15,
        "R4_F_topo": 1.10,
        "R6_restoration": 0.96,
        "R6_seismic": 1.10,
        "R6_volcanic": 1.12,
        "R6_drought": 1.08,
        "R6_armed_conflict": 1.04,
        "R7_cyber": 1.005,
    }


@pytest.fixture
def v4_2_modifiers():
    """v4.2 modifier set with R6c flood (additive) + the 5 multiplicative families."""
    return {
        "R3_C_mult": 1.00,
        "R4_F_topo": 1.05,
        "R6_seismic": 1.05,
        "R7_cyber": 1.00,
        "R6c_flood": 1.15,  # additive: contributes +0.15 outside soft_clip
        "R6d_wildfire": 1.10,
        "R6e_winter": 1.05,
        "R8_adapt": 0.98,  # reverse-signed
        "R9_compound": 1.03,
        "R10_just": 1.07,
    }


@pytest.fixture
def empty_modifiers():
    """Empty modifier dict — used to verify identity behavior."""
    return {}


@pytest.fixture
def out_of_range_modifiers():
    """Modifier values outside their declared range — clipped at apply time."""
    return {
        "R3_C_mult": 2.0,  # above 1.50 — should clip to 1.50
        # Was R7_cyber=0.90 (clipping up to 0.99). R7_cyber was retired at the
        # v4.24 hard cutover and is no longer applied, so it can no longer
        # demonstrate clipping. R8_adapt has a live range of 0.92–1.05 and
        # serves the same purpose: a value below range, clipped up at apply.
        "R8_adapt": 0.90,  # below 0.92 — should clip to 0.92
    }


@pytest.fixture
def unknown_modifiers():
    """Modifier dict containing keys not in the registry."""
    return {
        "R3_C_mult": 1.05,
        "R99_unknown": 1.20,  # not in registry — skipped with warning
        "totally_made_up": 5.0,
    }
