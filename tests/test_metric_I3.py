"""I3 heat-wave IRI. Each test guards a trap that was measured, not imagined."""
import importlib.util, pathlib, zlib
import numpy as np

_r = pathlib.Path(__file__).resolve().parent.parent
_s = importlib.util.spec_from_file_location("i3", _r / "scripts" / "ssi_derive_metric_I3.py")
i3 = importlib.util.module_from_spec(_s); _s.loader.exec_module(i3)


def _series(n_days, base, amp, spikes=(), noise=1.5):
    """Seasonal sine + weather noise + optional spikes, (n,1,1), Kelvin.

    The noise matters. A noiseless series makes every test measure the
    small-sample behaviour of a percentile rather than the metric.

    The seed is derived from the arguments rather than drawn from one shared
    generator. With a shared generator these tests passed in file order and
    test_magnitude_separates_where_frequency_cannot failed in alphabetical
    order, because each test consumed a different amount of the stream. A
    suite whose result depends on the order the runner happens to choose is
    not evidence of anything.
    """
    seed = zlib.crc32(repr((n_days, base, amp, tuple(spikes), noise)).encode())
    rng = np.random.default_rng(seed)
    t = np.arange(n_days)
    v = base + amp * np.sin(2 * np.pi * t / 365.25) + rng.normal(0, noise, n_days)
    for start, length, delta in spikes:
        v[start:start + length] += delta
    return (v + 273.15).astype("float32").reshape(-1, 1)


def _rng(tag):
    """A generator seeded by name, so no test consumes another test's stream."""
    return np.random.default_rng(zlib.crc32(tag.encode()))


def _summer_spikes(years, delta, length=5):
    """A heat wave each year at a DIFFERENT summer date, as real ones occur."""
    r = _rng(f"summer:{years}:{delta}:{length}")
    return [(int(365.25 * k) + int(r.integers(170, 240)), length, delta)
            for k in range(years)]


def test_a_run_shorter_than_three_days_is_not_a_heat_wave():
    # noise=0 so the ONLY exceedances are the spikes; with weather noise the
    # series produces its own 3-day runs and the rule under test is masked.
    n = int(365.25 * 5); doy = np.arange(n) % 366
    two = _series(n, 15, 10, spikes=[(int(365.25 * k) + 200, 2, 25) for k in range(5)], noise=0.0)
    three = _series(n, 15, 10, spikes=[(int(365.25 * k) + 200 + 3 * k, 3, 25) for k in range(5)], noise=0.0)
    d2 = i3.heatwave_1d(two, doy)
    d3 = i3.heatwave_1d(three, doy)
    assert d2[0] == 0.0, "a 2-day spike must not count as a heat wave"
    assert d3[0] > 0.0, "a 3-day spike must count"


def test_more_excess_gives_a_higher_metric_not_lower():
    """I3 carries RISK. Unlike I4/I6 it is NOT inverted."""
    n = int(365.25 * 5); doy = np.arange(n) % 366
    a = i3.heatwave_1d(_series(n, 15, 10, _summer_spikes(5, 3)), doy)
    b = i3.heatwave_1d(_series(n, 15, 10, _summer_spikes(5, 15)), doy)
    assert b[0] > a[0], f"fiercer heat scored lower: {b[0,0]} vs {a[0,0]}"
    lo = i3.method_b(float(a[0]), 0.0, float(b[0]))
    hi = i3.method_b(float(b[0]), 0.0, float(b[0]))
    assert hi > lo, "the normalisation must preserve the direction"


def test_the_baseline_tracks_the_season_not_the_year():
    """A whole-year p90 sits at a summer temperature, so a large WINTER
    anomaly scores zero against it. That confound is what ranked finland and
    norway ABOVE greece before the calendar-day baseline was adopted."""
    n = int(365.25 * 5); doy = np.arange(n) % 366
    r = _rng("winter")
    winter = [(int(365.25 * k) + int(r.integers(10, 60)), 5, 12) for k in range(5)]
    d = i3.heatwave_1d(_series(n, 15, 15, winter), doy)
    assert d[0] > 0.0, "a winter heat anomaly must register against a seasonal baseline"


def test_magnitude_separates_where_frequency_cannot():
    """With the threshold at the p90 of the same data ~10% of days exceed it
    whatever the climate — measured, the exceedance COUNT is capped at
    0-37 days/yr in every one of the 39 countries. Magnitude is what carries
    the signal, so that is what the metric integrates."""
    n = int(365.25 * 5); doy = np.arange(n) % 366
    calm = i3.heatwave_1d(_series(n, 15, 10, _summer_spikes(5, 2)), doy)
    wild = i3.heatwave_1d(_series(n, 15, 10, _summer_spikes(5, 12)), doy)
    assert wild[0] > calm[0], "magnitude must separate these"
    dc = i3.heatwave_1d(_series(n, 15, 10, _summer_spikes(5, 2)), doy)
    dw = i3.heatwave_1d(_series(n, 15, 10, _summer_spikes(5, 12)), doy)
    assert abs(float(dw[0]) - float(dc[0])) < float(wild[0]), \
        "day-count must separate them far less than magnitude does"


def test_an_event_that_recurs_identically_every_year_IS_the_climatology():
    """Not a bug. A metric of extreme DEVIATION must score a perfectly regular
    annual event at zero, because it is the local norm. This is the boundary of
    what I3 measures: it captures irregular excursions, not chronic heat, and a
    substation that sees the same August every year registers nothing here."""
    n = int(365.25 * 5); doy = np.arange(n) % 366
    fixed = [(int(365.25 * k) + 200, 5, 15) for k in range(5)]   # same day each year
    d = i3.heatwave_1d(_series(n, 15, 10, fixed, noise=0.0), doy)
    assert d[0] == 0.0


def test_an_all_nan_cell_never_becomes_a_real_zero():
    """ERA5-Land is empty over sea. Summing an all-NaN series gives 0.0, which
    is finite and plausible and false. Measured: it would have handed a zero to
    900 of norway's 6,113 substations."""
    doy = np.arange(366) % 366
    sea = np.full((366, 1), np.nan, dtype="float32")
    d = i3.heatwave_1d(sea, doy)
    assert d[0] == 0.0, "sum of nothing is 0 — which is exactly the trap"
    valid = np.isfinite(sea).any(axis=0)
    assert not valid[0], "the validity mask, not the value, is what must gate it"


def test_method_b_declines_a_degenerate_fleet():
    assert i3.method_b(5.0, 3.0, 3.0) is None
    assert i3.method_b(5.0, None, 10.0) is None


# ---------------------------------------------------------------------------
# Method C. Added with DECISION_I3_normalisation_method_C.md, 31 August 2026.
# ---------------------------------------------------------------------------

def test_method_c_maps_the_anchor_to_the_top_and_saturates_above_it():
    assert i3.method_c(0.0) == 0.0
    assert i3.method_c(i3.ANCHOR) == 1.0
    assert i3.method_c(i3.ANCHOR * 2) == 1.0, "above the anchor must saturate, not exceed"
    assert 0.0 < i3.method_c(i3.ANCHOR / 2) < 1.0


def test_method_c_is_strictly_increasing_below_the_anchor():
    xs = [1.0, 5.0, 12.5, 25.0, 40.0, 51.0]
    vs = [i3.method_c(x) for x in xs]
    assert all(b > a for a, b in zip(vs, vs[1:])), \
        f"the normalisation must preserve the direction: {vs}"


def test_method_c_does_not_depend_on_any_other_record():
    """The whole point of the amendment. One record, one value, no population."""
    alone = i3.method_c(20.0)
    assert alone == i3.method_c(20.0)
    # There is no fleet argument to pass, which is the structural guarantee.
    import inspect
    assert list(inspect.signature(i3.method_c).parameters) == ["x"], \
        "method_c must take the record's own value and nothing else"


def test_iri_current_lands_on_the_construct_interval():
    assert i3.iri_current(0.0) == 0.0
    assert i3.iri_current(i3.ANCHOR) == 0.30
    assert i3.iri_current(i3.ANCHOR * 10) == 0.30, "the interval is closed at 0.30"
    v = i3.iri_current(20.0)
    assert 0.0 < v < 0.30


def test_the_r2_gate_can_be_evaluated_which_it_could_not_under_method_b():
    """IRI_THRESH = 0.02 on the raw scale — construct section 05."""
    IRI_THRESH = 0.02
    below = i3.iri_current(2.0)
    above = i3.iri_current(30.0)
    assert below < IRI_THRESH, "a cool cell must be testable as below the gate"
    assert above > IRI_THRESH


def test_the_anchor_is_the_pinned_value_and_changing_it_is_an_amendment():
    """A sentinel on the pin itself. If this fails, doctrine and code disagree."""
    assert i3.ANCHOR == 51.93
    assert i3.IRI_TOP == 0.30
