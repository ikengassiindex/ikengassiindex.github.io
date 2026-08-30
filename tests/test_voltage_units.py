"""A voltage above 1000 is volts. Converting it must never invent a level."""
import importlib.util, pathlib

_spec = importlib.util.spec_from_file_location(
    "rvu", pathlib.Path(__file__).resolve().parent.parent / "scripts" / "repair_voltage_units.py")
rvu = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(rvu)


def test_turkeys_real_levels_convert_exactly():
    for volts, kv in [(154000, 154.0), (380000, 380.0), (34500, 34.5),
                      (31500, 31.5), (66000, 66.0)]:
        out, changed = rvu.repair_value(volts, [])
        assert changed and out == kv, f"{volts} -> {out}, expected {kv}"


def test_a_value_already_in_kv_is_left_alone():
    for kv in [66, 154.0, 400, 0.4, 1000]:
        out, changed = rvu.repair_value(kv, [])
        assert not changed and out == kv


def test_float_noise_on_the_source_tag_snaps_to_the_level():
    # 20000.75 / 1000 = 20.00075. That is a 20 kV line with a dirty tag, not a
    # 20.001 kV line. Storing the quotient would invent precision.
    out, changed = rvu.repair_value(20000.75, [])
    assert changed and out == 20.0, out
    assert rvu.repair_value(20000.4, [])[0] == 20.0


def test_an_implausible_quotient_is_refused_not_rounded():
    refused = []
    out, changed = rvu.repair_value(6600011.0, refused)
    assert not changed, "6,600,011 V must not be coerced to a level"
    assert out == 6600011.0, "the refused record must be left exactly as it was"
    assert refused and refused[0][0] == 6600011.0


def test_refusal_does_not_block_the_rest():
    refused = []
    vals = [154000, 6600011.0, 380000]
    out = [rvu.repair_value(v, refused)[0] for v in vals]
    assert out == [154.0, 6600011.0, 380.0]
    assert len(refused) == 1


def test_non_numeric_and_none_survive():
    for v in [None, "154000", True, False]:
        out, changed = rvu.repair_value(v, [])
        assert not changed and out == v


def test_the_66_default_is_not_touched():
    # 2,880 turkey substations carry the hardcoded fallback 66. It is not a
    # unit error and this script must leave it entirely alone.
    out, changed = rvu.repair_value(66, [])
    assert not changed and out == 66
