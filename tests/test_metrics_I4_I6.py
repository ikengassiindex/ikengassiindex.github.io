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
    for slug in ("luxembourg", "iceland", "mexico", "greenland"):
        assert slug not in pins, f"{slug} must stay unpinned until decided"
        assert slug in held
    assert len(pins) == 35


def test_the_uk_carries_three_floors_not_one():
    """A single UK floor is wrong in BOTH directions, which is why it is a
    schema case and not a judgement call: 132 counts English and Welsh
    distribution as transmission, 275 drops Scottish and NI transmission."""
    pins, _ = load_pins()
    spec = pins["uk"]
    assert isinstance(spec, dict), "uk must not collapse to a scalar floor"
    floors = {j["id"]: j["floor"] for j in spec["jurisdictions"]}
    assert floors == {"EW": 275, "SCO": 132, "NI": 110}


def test_a_scalar_floor_still_behaves_exactly_as_before():
    """35 countries carry a scalar. make_floor must not change them."""
    import importlib.util, pathlib as _p
    root = _p.Path(__file__).resolve().parent.parent
    sp = importlib.util.spec_from_file_location(
        "drv", root / "scripts" / "ssi_derive_metrics_I4_I6.py")
    drv = importlib.util.module_from_spec(sp); sp.loader.exec_module(drv)
    fn, label = drv.make_floor(132, [])
    assert label == "132"
    assert fn({"kv": 400}) == 132 and fn({}) == 132


def test_uk_classifier_places_the_three_jurisdictions():
    import importlib.util, pathlib as _p
    root = _p.Path(__file__).resolve().parent.parent
    sp = importlib.util.spec_from_file_location(
        "drv", root / "scripts" / "ssi_derive_metrics_I4_I6.py")
    drv = importlib.util.module_from_spec(sp); sp.loader.exec_module(drv)
    subs = [
        {"substation_id": "a", "region": "Highland", "lat": 57.5, "lon": -4.2},
        {"substation_id": "b", "region": "Devon", "lat": 50.7, "lon": -3.5},
        {"substation_id": "c", "region": "Belfast", "lat": 54.6, "lon": -5.9},
        # no usable region — must fall through to geometry, not to a default
        {"substation_id": "d", "region": None, "lat": 56.9, "lon": -4.0},
    ]
    cls = drv.uk_jurisdiction(subs)
    assert cls == {"a": "SCO", "b": "EW", "c": "NI", "d": "SCO"}
    spec = {"classifier": "uk_jurisdiction", "jurisdictions": [
        {"id": "EW", "floor": 275}, {"id": "SCO", "floor": 132},
        {"id": "NI", "floor": 110}]}
    fn, label = drv.make_floor(spec, subs)
    assert fn({"ss": "a"}) == 132 and fn({"ss": "b"}) == 275 and fn({"ss": "c"}) == 110
    # a line with no known endpoint is placed by its own geometry
    assert fn({"ss": "zz", "p": [[-4.0, 57.0], [-4.1, 57.1]]}) == 132
    assert fn({"ss": "zz", "p": [[-1.0, 51.0], [-1.1, 51.1]]}) == 275


def test_a_line_that_cannot_be_placed_is_skipped_not_defaulted():
    """Convention #56 — an unplaceable line gets no floor, so it is excluded,
    rather than silently inheriting whichever floor happens to be first."""
    import importlib.util, pathlib as _p
    root = _p.Path(__file__).resolve().parent.parent
    sp = importlib.util.spec_from_file_location(
        "drv", root / "scripts" / "ssi_derive_metrics_I4_I6.py")
    drv = importlib.util.module_from_spec(sp); sp.loader.exec_module(drv)
    spec = {"classifier": "uk_jurisdiction", "jurisdictions": [
        {"id": "EW", "floor": 275}, {"id": "SCO", "floor": 132},
        {"id": "NI", "floor": 110}]}
    fn, _ = drv.make_floor(spec, [])
    assert fn({"ss": "unknown"}) is None, "a line with no endpoint and no geometry must be skipped"


def test_turkey_is_pinned_only_because_its_units_were_repaired():
    """Turkey was held at 27.3% of line records in volts. It is pinned at
    154 kV (TEIAS transmission) now that repair_voltage_units.py has run.
    If the units regress, the pin must not stand — this asserts the condition
    the pin rests on, not just the pin."""
    import importlib.util, pathlib as _p
    root = _p.Path(__file__).resolve().parent.parent
    spec = importlib.util.spec_from_file_location(
        "drv", root / "scripts" / "ssi_derive_metrics_I4_I6.py")
    drv = importlib.util.module_from_spec(spec); spec.loader.exec_module(drv)
    pins, held = load_pins()
    assert pins.get("turkey") == 154
    assert "turkey" not in held
    lines = drv.load_lines("turkey")
    breach = sum(1 for ln in lines
                 if isinstance(ln.get("kv"), (int, float)) and ln["kv"] > 1000)
    assert breach / len(lines) <= drv.UNIT_BREACH_MAX, (
        f"turkey is pinned but {breach:,} of {len(lines):,} line records are "
        f"back in volts — the pin's precondition has regressed")


def test_one_bad_record_cannot_add_phantom_transmission_km():
    """The country guard catches a SYSTEMATIC unit failure. It cannot catch a
    single record, and a single record tagged 15400 passes any floor. Turkey
    carried exactly that: one line worth 1,005 phantom km."""
    subs = [sub(50.0 + 0.02 * i, 5.0, f"A{i}") for i in range(30)]
    # 200 clean lines so that ONE bad record is 0.5% — under UNIT_BREACH_MAX.
    # The country guard must not fire here; the per-record exclusion is what is
    # under test, and a smaller fleet would test the wrong guard.
    clean = [line(400, [[5.0, 50.0 + 0.002 * i], [5.05, 50.0 + 0.002 * i]])
             for i in range(200)]
    poisoned = clean + [line(15400, [[5.0, 50.0], [9.0, 50.0]])]
    a = derive("t", subs, clean, 132)
    b = derive("t", subs, poisoned, 132)
    assert a[0] == b[0], "a kv>1000 record changed I4 — it must be excluded"


def test_a_substation_without_coordinates_is_skipped_not_defaulted():
    """Convention #56 — absent coordinates means no metric, not a default."""
    subs = [sub(50.0 + 0.02 * i, 5.0, f"A{i}") for i in range(30)]
    subs.append({"substation_id": "N", "name": "N"})
    lines = [line(400, [[5.0, 50.0], [5.0, 50.3]])]
    derive("test", subs, lines, 132)
    assert "metrics" in subs[0]
    assert "metrics" not in subs[-1], "a record with no coordinates got a metric"
