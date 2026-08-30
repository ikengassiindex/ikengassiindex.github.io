"""Anchored count rewriting. The Task #520 collision must be impossible."""
import importlib.util, pathlib

_spec = importlib.util.spec_from_file_location(
    "rcc", pathlib.Path(__file__).resolve().parent.parent / "scripts" / "refresh_country_counts.py")
rcc = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(rcc)

TRUTH = {"fleet.total": 4031, "fleet.voltage.ehv": 136,
         "fleet.voltage.hv": 789, "fleet.voltage.distribution": 3106}


def test_it_rewrites_the_literal_table():
    src = '''window.SSI_CANONICAL_LITERALS = {
 "fleet.total": "4,031",
 "fleet.voltage.ehv": "1,120",
 "fleet.voltage.hv": "1",
 "fleet.voltage.distribution": "2,910"};'''
    out, n = rcc._rewrite(src, TRUTH)
    assert '"fleet.voltage.ehv": "136"' in out
    assert '"fleet.voltage.hv": "789"' in out
    assert '"fleet.voltage.distribution": "3,106"' in out
    assert '"fleet.total": "4,031"' in out          # unchanged, still correct
    assert "1,120" not in out and "2,910" not in out


def test_it_rewrites_the_spans():
    src = ('<span data-canonical="fleet.voltage.ehv">1,120</span> EHV · '
           '<span data-canonical="fleet.voltage.hv">1</span> HV')
    out, _ = rcc._rewrite(src, TRUTH)
    assert '>136<' in out and '>789<' in out
    assert '>1,120<' not in out


def test_the_task_520_collision_cannot_happen():
    """Austria: a bare replace of "262" -> "14,070" hit "262,807" and produced
    "14070,807". Anchoring locates the number by its KEY, so an unrelated
    number that merely contains the digits is untouchable."""
    src = ('<span data-canonical="fleet.voltage.ehv">1,120</span>'
           '<p>unrelated: 1,120,807 and 11,120 and 1120 and revenue 1,120</p>')
    out, _ = rcc._rewrite(src, TRUTH)
    assert '>136<' in out
    assert '1,120,807' in out, "an unrelated longer number was mangled"
    assert '11,120' in out, "an unrelated number containing the digits was mangled"
    assert '1120' in out
    assert 'revenue 1,120' in out, "prose carrying the same digits was rewritten"


def test_a_value_already_correct_is_left_byte_identical():
    src = '"fleet.voltage.ehv": "136"'
    out, _ = rcc._rewrite(src, TRUTH)
    assert out == src


def test_reader_finds_both_forms():
    src = ('"fleet.voltage.hv": "1"\n'
           '<span data-canonical="fleet.voltage.hv">1</span>')
    found = rcc._canon_in_text(src)
    assert found["fleet.voltage.hv"] == {1}


def test_reader_ignores_a_key_that_is_not_canonical():
    src = '"fleet.grid_lines": "8,061"'
    assert rcc._canon_in_text(src) == {}


def test_buckets_partition_the_fleet():
    """Every substation lands in exactly one tier — the three must sum to the
    total, or a record is being counted twice or not at all."""
    for slug in ("turkey", "israel", "costa-rica"):
        c = rcc.counts_from_data(slug)
        assert (c["fleet.voltage.ehv"] + c["fleet.voltage.hv"]
                + c["fleet.voltage.distribution"]) == c["fleet.total"], slug
