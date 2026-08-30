"""I4 and I6 are INVERTED. Getting that backwards ranks the fleet exactly wrong
while producing entirely plausible numbers, so the direction is asserted
explicitly rather than inferred from a range check.

Construct section 03: "I4 (RTN density) and I6 (substation density) are
inverted because higher density = better resilience. N'(x) = N(P5 + P95 - x)."

Therefore: MORE transmission line-km near a substation must produce a LOWER I4.
More neighbouring substations must produce a LOWER I6.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from ssi_derive_metrics_I4_I6 import (
    derive, method_b, method_b_inverted, load_pins, cell, seg_km, CELL)


def line(kv, pts):
    return {"i": 1, "kv": kv, "p": pts}


def sub(lat, lon, sid="X"):
    return {"substation_id": sid, "name": sid, "lat": lat, "lon": lon}


def test_inversion_reverses_the_ranking():
    p5, p95 = 10.0, 90.0
    assert method_b(10.0, p5, p95) == 0.0
    assert method_b(90.0, p5, p95) == 1.0
    # inverted: the LOW raw value must map HIGH, the HIGH raw value LOW
    assert method_b_inverted(10.0, p5, p95) == 1.0
    assert method_b_inverted(90.0, p5, p95) == 0.0
    assert method_b_inverted(30.0, p5, p95) > method_b_inverted(70.0, p5, p95)


def test_a_denser_substation_gets_a_lower_I4_and_I6():
    """The whole point of the metric, asserted end to end on real geometry."""
    dense = [sub(50.0 + 0.001 * i, 5.0 + 0.001 * i, f"D{i}") for i in range(40)]
    sparse = [sub(52.0 + 0.3 * i, 9.0 + 0.3 * i, f"S{i}") for i in range(6)]
    subs = dense + sparse
    lines = []
    for i in range(60):                       # dense corridor of 400 kV line
        lines.append(line(400, [[5.0 + 0.001 * i, 50.0], [5.0 + 0.001 * (i + 1), 50.0]]))
    lines.append(line(400, [[9.0, 52.0], [9.001, 52.0]]))   # one line out in the sparse area
    derive("test", subs, lines, 132)
    d = [s["metrics"]["I4"] for s in dense if "metrics" in s]
    sp = [s["metrics"]["I4"] for s in sparse if "metrics" in s]
    assert d and sp
    assert max(d) < min(sp), (
        f"dense substations got I4 {max(d)} vs sparse {min(sp)} — the inversion "
        f"is backwards; denser must score LOWER")
    d6 = [s["metrics"]["I6"] for s in dense if "metrics" in s]
    s6 = [s["metrics"]["I6"] for s in sparse if "metrics" in s]
    assert max(d6) < min(s6), "I6 inversion is backwards"


def test_the_voltage_floor_excludes_distribution():
    """A 20 kV line must not count toward a 132 kV transmission metric.

    Needs a fleet with real spread: Method B normalises over fleet P5/P95, and
    a two-record fleet has none, so it correctly declines to produce a metric
    at all. The first version of this test asserted against that guard and
    failed — the guard was right.
    """
    subs = [sub(50.0 + 0.02 * i, 5.0, f"A{i}") for i in range(30)]
    lv = [line(20, [[5.0, 50.0 + 0.02 * i], [5.0, 50.0 + 0.02 * i + 0.01]])
          for i in range(30)]
    hv = [line(400, [[5.0, 50.0], [5.0, 50.05]])]
    derive("test", subs, lv + hv, 132)
    near = subs[0]["metrics"]["_I4_raw_km"]
    far = subs[-1]["metrics"]["_I4_raw_km"]
    assert far == 0.0, f"a 20 kV line counted at a 132 kV floor ({far} km)"
    assert near > 0, "the 400 kV line was not counted"


def test_volts_masquerading_as_kv_is_refused():
    """Turkey's defect: 27% of its kv values are volts. A 20 kV line read as
    20,000 kV would be counted as transmission everywhere."""
    subs = [sub(50.0, 5.0), sub(50.1, 5.1)]
    lines = [line(154000, [[5.0, 50.0], [5.01, 50.0]]) for _ in range(30)]
    lines += [line(400, [[5.0, 50.0], [5.01, 50.0]]) for _ in range(70)]
    try:
        derive("test", subs, lines, 132)
    except ValueError as e:
        assert "volts" in str(e)
        return
    raise AssertionError("30% of records with kv>1000 was not refused")


def test_held_countries_have_no_pin():
    pins, held = load_pins()
    for slug in ("uk", "us", "turkey", "luxembourg", "iceland", "mexico", "greenland"):
        assert slug not in pins, f"{slug} must stay unpinned until decided"
        assert slug in held
    assert len(pins) == 32


def test_a_substation_without_coordinates_is_skipped_not_defaulted():
    """Convention #56 — absent coordinates means no metric, not a default."""
    subs = [sub(50.0 + 0.02 * i, 5.0, f"A{i}") for i in range(30)]
    subs.append({"substation_id": "N", "name": "N"})
    lines = [line(400, [[5.0, 50.0], [5.0, 50.3]])]
    derive("test", subs, lines, 132)
    assert "metrics" in subs[0]
    assert "metrics" not in subs[-1], "a record with no coordinates got a metric"
