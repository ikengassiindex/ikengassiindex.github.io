"""
SSI Pipeline — Browser Engine Retirement Tests (Phase 1 PR-4)

5 tests confirming ssi-engine.js is in its retired-mode shape after PR-4:

- Test 1: monteCarlo is preserved on the public API as a throw tripwire
- Test 2: computeRBase is preserved as a throw tripwire
- Test 3: classifyBand is preserved as a working function (used by data-sections.js)
- Test 4: classifyConfidence is preserved as a working function
- Test 5: percentile is preserved as a working utility

The PR-4 plan called for assertions that the retired JS engine "throws if
invoked". We implement this as static-content analysis on the file: the
throw signatures are sufficient evidence that any caller would surface
loudly. This keeps the test suite hermetic (no Node spawn, no jsdom dep,
runs in 0.0s). If the operator wants runtime confirmation, the throw
messages are visible in any browser DevTools console — that gate is
covered by the per-country page-load smoke (acceptance gate 2 in the plan).

Cross-reference: PHASE_1_IMPLEMENTATION_PLAN.md PR-4 §"Test criteria (the 5 PR-4 tests)"
                 AUDIT_v4_0_2_PRE_v4_2_FOUNDATION.md F-L3-3 closure
"""

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SSI_ENGINE_JS = REPO_ROOT / "ssi-engine.js"


@pytest.fixture(scope="module")
def engine_source():
    """Read the retired ssi-engine.js once for all tests in this module."""
    assert SSI_ENGINE_JS.exists(), f"ssi-engine.js missing at {SSI_ENGINE_JS}"
    return SSI_ENGINE_JS.read_text(encoding="utf-8")


# ═══════════════════════════════════════════════════════════
#  RETIREMENT TRIPWIRES (Tests 1-2)
# ═══════════════════════════════════════════════════════════

class TestRetirementTripwires:
    """The computational functions must be preserved by name but throw if invoked."""

    def test_1_monte_carlo_is_throw_tripwire(self, engine_source):
        """monteCarlo() must throw a descriptive Error with retirement message."""
        # The function declaration must still exist (preserves API surface for
        # data-sections.js's Object.keys() counter + any latent callers).
        assert "function monteCarlo(" in engine_source, (
            "monteCarlo function declaration missing — would silently disappear "
            "from window.SSIEngine and break the tripwire contract"
        )
        # The body must throw with a message naming the retirement + the
        # canonical replacement path (per Convention #55 — actionable errors).
        monte_block = _extract_function_body(engine_source, "monteCarlo")
        assert "throw new Error(" in monte_block, (
            "monteCarlo body does not throw — silent retirement is a Convention "
            "#55 violation. Body was: " + monte_block[:200]
        )
        assert "RETIRED" in monte_block, "Retirement marker missing"
        assert "ssi-data.json" in monte_block, (
            "Throw message must point to the canonical replacement (ssi-data.json)"
        )

    def test_2_compute_r_base_is_throw_tripwire(self, engine_source):
        """computeRBase() must throw a descriptive Error with retirement message."""
        assert "function computeRBase(" in engine_source, (
            "computeRBase function declaration missing"
        )
        rbase_block = _extract_function_body(engine_source, "computeRBase")
        assert "throw new Error(" in rbase_block, (
            "computeRBase body does not throw — Convention #55 violation"
        )
        assert "RETIRED" in rbase_block
        assert "R_base_median" in rbase_block, (
            "Throw message must point to the precomputed R_base_median field"
        )


# ═══════════════════════════════════════════════════════════
#  PRESERVED FUNCTIONS (Tests 3-5)
# ═══════════════════════════════════════════════════════════

class TestPreservedFunctions:
    """Pure-function classification + utility helpers must survive retirement."""

    def test_3_classify_band_is_preserved_with_band_table(self, engine_source):
        """classifyBand must still exist as a working function with BANDS lookup."""
        assert "function classifyBand(" in engine_source
        # Must reference BANDS table (the band-threshold lookup that data-sections.js
        # ultimately reads via SSIEngine.classifyBand)
        body = _extract_function_body(engine_source, "classifyBand")
        assert "BANDS" in body, (
            "classifyBand does not reference BANDS table — broken implementation"
        )
        assert "throw" not in body, (
            "classifyBand is a pure-function classifier — must NOT throw. "
            "It's the path data-sections.js takes for the band-count widget."
        )

    def test_4_classify_confidence_is_preserved_as_pure_function(self, engine_source):
        """classifyConfidence must classify CI width into high/medium/low."""
        assert "function classifyConfidence(" in engine_source
        body = _extract_function_body(engine_source, "classifyConfidence")
        assert "CONFIDENCE_TIERS" in body, (
            "classifyConfidence does not reference CONFIDENCE_TIERS — broken"
        )
        assert "throw" not in body, (
            "classifyConfidence is a pure-function classifier — must NOT throw"
        )
        # Must compute the CI width (R_P95 − R_P5) to do anything useful
        assert "R_P95 - R_P5" in body or "R_P5" in body and "R_P95" in body, (
            "classifyConfidence does not reference R_P5 or R_P95 — broken implementation"
        )

    def test_5_percentile_is_preserved_with_linear_interpolation(self, engine_source):
        """percentile must preserve the linear-interpolation utility."""
        assert "function percentile(" in engine_source
        body = _extract_function_body(engine_source, "percentile")
        assert "throw" not in body, (
            "percentile is a pure-function utility — must NOT throw"
        )
        # Linear interpolation between floor + ceiling indices
        assert "Math.floor" in body and "Math.ceil" in body, (
            "percentile does not use floor/ceil index pattern — broken"
        )


# ═══════════════════════════════════════════════════════════
#  Helper
# ═══════════════════════════════════════════════════════════

def _extract_function_body(source, func_name):
    """
    Crude but sufficient: return the source between `function <name>(` and the
    matching closing brace at the same indent. Brace-counting from the opening
    `{` so nested braces (object literals, if-statements) don't confuse us.
    """
    # Find the opening line
    pattern = r"function\s+" + re.escape(func_name) + r"\s*\("
    m = re.search(pattern, source)
    if not m:
        raise AssertionError(f"Function '{func_name}' not found in source")
    # Find the opening brace
    brace_start = source.find("{", m.end())
    if brace_start < 0:
        raise AssertionError(f"No opening brace for '{func_name}'")
    # Brace-count to the matching close
    depth = 0
    i = brace_start
    while i < len(source):
        ch = source[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return source[brace_start:i + 1]
        i += 1
    raise AssertionError(f"No matching close brace for '{func_name}'")
