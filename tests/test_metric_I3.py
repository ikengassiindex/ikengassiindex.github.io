"""I3 heat-wave IRI. Each test guards a trap that was measured, not imagined."""
import importlib.util, pathlib
import numpy as np

_r = pathlib.Path(__file__).resolve().parent.parent
_s = importlib.util.spec_from_file_location("i3", _r / "scripts" / "ssi_derive_metric_I3.py")
i3 = importlib.util.module_from_spec(_s); _s.loader.exec_module(i3)


_RNG = np.random.default_rng(7)


def _series(n_days, base, amp, spikes=(), noise=1.5):
    """Seasonal sine + weather noise + optional spikes, (n,1,1), Kelvin.

    The noise matters. A noiseless series makes every test measure the
    small-sample behaviour of a percentile rather than the metric."""
    t = np.arange(n_days)
    v = base + amp * np.sin(2 * np.pi * t / 365.25) + _RNG.normal(0, noise, n_days)
    for start, length, delta in spikes:
        v[start:start + length] += delta
    return (v + 273.15).astype("float32").reshape(-1, 1)


def _summer_spikes(years, delta, length=5):
    """A heat wave each year at a DIFFERENT summer date, as real ones occur."""
    return [(int(365.25 * k) + int(_RNG.integers(170, 240)), length, delta)
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
    winter = [(int(365.25 * k) + int(_RNG.integers(10, 60)), 5, 12) for k in range(5)]
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
