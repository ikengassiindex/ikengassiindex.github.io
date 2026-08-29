"""Each closure check must fire on the defect it names, and on nothing else.

The register publishes four fields per substation and a page-level assertion
that they satisfy

    R_median = soft_clip_upper(R_base_median x mult_product) + add_sum

On 29 August 2026 that held on 28.1% of 622,039 records while all 39 country
pages reported the check verified. These tests pin the detector, so a later
edit that quietly weakens it fails here rather than reporting a clean cohort.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from check_master_equation_closure import (
    audit, declared_status, _DECLARED, CHECKS, TOL, RE_CORE_KEYS)
from pipeline.scoring.engine import soft_clip_upper

# Modifier values whose product is deliberately NOT the stored mult_product,
# so RE_CORE stays silent unless a test asks for it.
MODS = {"R6d_wildfire": 1.06, "R6e_winter": 1.11, "R8_adapt": 0.92,
        "R9_compound": 1.10, "R10_just": 1.00}
RE_CORE = 1.06 * 1.11 * 0.92 * 1.10 * 1.00


def rec(rb=0.375, mp=1.25, ad=0.14, med=None, mods=None, **over):
    """A record that closes exactly, built through the engine's own soft_clip."""
    if med is None:
        med = round(soft_clip_upper(rb * mp) + ad, 4)
    s = {"substation_id": "X1", "R_base_median": rb, "mult_product": mp,
         "add_sum": ad, "R_median": med, "modifiers": dict(mods or MODS)}
    s.update(over)
    return s


def only(counts, *expected):
    fired = {k for k in CHECKS if counts[k]}
    assert fired == set(expected), f"fired {sorted(fired)}, expected {sorted(expected)}"


def test_a_closing_record_trips_nothing():
    c, share, _ = audit([rec()])
    only(c)
    assert share == 1.0


def test_closure_fires_when_the_equation_does_not_hold():
    # france's live shape: published R_median above what the terms produce.
    c, share, worst = audit([rec(med=0.612)])
    only(c, "CLOSURE")
    assert share == 0.0
    assert worst[1] == "X1"


def test_tolerance_is_the_rounding_floor_not_a_loophole():
    base = soft_clip_upper(0.375 * 1.25) + 0.14
    inside, _, _ = audit([rec(med=round(base + TOL * 0.8, 6))])
    only(inside)
    outside, _, _ = audit([rec(med=round(base + TOL * 1.2, 6))])
    only(outside, "CLOSURE")


def test_re_core_fires_when_mult_product_is_the_esg_composite_core():
    # The france/germany shape: mult_product holds R6d x R6e x R8 x R9 x R10.
    c, _, _ = audit([rec(mp=RE_CORE)])
    only(c, "RE_CORE")


def test_re_core_is_silent_when_the_modifiers_are_absent():
    c, _, _ = audit([rec(mp=RE_CORE, mods={"R3_C_mult": 1.05})])
    only(c)


def test_incomplete_fires_and_closure_does_not_guess():
    # Convention #56: a term absent means closure cannot be evaluated. It must
    # not be counted as closing, and it must not be counted as failing.
    c, share, _ = audit([rec(mult_product=None)])
    only(c, "INCOMPLETE")
    assert share is None, "share must be undefined when nothing is evaluable"


def test_soft_clip_is_the_engines_own():
    # Built in the compression regime. If the checker re-implemented soft_clip
    # even slightly differently, this record would not close.
    rb, mp = 0.95, 1.30
    assert abs(soft_clip_upper(rb * mp) - rb * mp) > 1e-6, (
        "pick operands inside the compression regime or this proves nothing")
    c, _, _ = audit([rec(rb=rb, mp=mp)])
    only(c)


def test_declared_status_is_read_from_the_metadata():
    line = ("{ check: 'v4.2 master equation closure', "
            "criterion: 'R_final = soft_clip_upper(R_base)', "
            "status: 'verified', tier: 'v4.2' }")
    assert _DECLARED.search(line).group(1) == "verified"
    assert _DECLARED.search("{ check: 'something else', status: 'verified' }") is None


def test_declared_status_reads_a_real_country():
    # The claim under audit: every page asserted this while failing it.
    assert declared_status("france") == "verified"
