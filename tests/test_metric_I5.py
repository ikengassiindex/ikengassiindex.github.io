"""I5 thermal stress, IEEE C57.91."""
import importlib.util, pathlib
import numpy as np

_r = pathlib.Path(__file__).resolve().parent.parent
_s = importlib.util.spec_from_file_location("i5", _r / "scripts" / "ssi_derive_metric_I5.py")
i5 = importlib.util.module_from_spec(_s); _s.loader.exec_module(i5)
i3 = i5.i3


def test_it_reproduces_the_standards_own_reference_point():
    """C57.91 defines F_AA = 1.0 at a 110 degC hot spot. With the 80 K rise for
    a 65 degC-rise transformer at rated load, that is 30 degC ambient. If this
    fails the constants are wrong, not the data."""
    assert abs(float(i5.f_aa(np.array([30.0]))[0]) - 1.0) < 1e-4


def test_ageing_roughly_doubles_every_six_kelvin():
    """The Arrhenius behaviour C57.91 encodes. A transformer at 116 degC hot
    spot ages about twice as fast as one at 110 degC."""
    a = float(i5.f_aa(np.array([30.0]))[0])
    b = float(i5.f_aa(np.array([36.0]))[0])
    assert 1.7 < b / a < 2.1, f"ratio {b/a:.2f} is not the C57.91 doubling"


def test_hotter_is_higher_not_lower():
    """I5 carries RISK and is NOT inverted."""
    v = i5.f_aa(np.array([-10.0, 0.0, 15.0, 30.0, 45.0]))
    assert np.all(np.diff(v) > 0), "F_AA must increase monotonically with ambient"
    lo = i3.method_b(float(v[0]), float(v[0]), float(v[-1]))
    hi = i3.method_b(float(v[-1]), float(v[0]), float(v[-1]))
    assert hi > lo


def test_I5_and_I3_measure_different_things():
    """The pair's whole justification. A site with a large but PERFECTLY
    REGULAR annual heat cycle has no irregular excursions, so I3 scores it at
    zero — while its chronic heat gives it a high I5. If both moved together
    one of them would be redundant."""
    n = int(365.25 * 5)
    doy = np.arange(n) % 366
    t = np.arange(n)
    regular = (25.0 + 12.0 * np.sin(2 * np.pi * t / 365.25) + 273.15)
    regular = regular.astype("float32").reshape(-1, 1)
    hw = i3.heatwave_1d(regular, doy)
    assert float(hw[0]) == 0.0, "a perfectly regular cycle has no deviation"
    warm = float(np.nanmean(i5.f_aa(regular[:, 0] - 273.15)))
    cold = float(np.nanmean(i5.f_aa(regular[:, 0] - 273.15 - 20.0)))
    assert warm > cold * 3, "I5 must separate chronic heat that I3 cannot see"


def test_a_sea_cell_is_never_given_a_value():
    """Delegated to the I3 module's land mask. Without it a coastal substation
    takes an all-NaN cell — which cost 900 of norway's records a manufactured
    zero when I3 was first written."""
    lat = np.array([10.0, 10.1, 10.2])
    lon = np.array([20.0, 20.1, 20.2])
    valid = np.zeros((3, 3), dtype=bool)
    valid[2, 2] = True
    subs = [{"lat": 10.0, "lon": 20.0}]
    cells, snapped, skipped = i3.resolve_cells(subs, lat, lon, valid)
    assert cells[0] == (2, 2) and snapped == 1 and skipped == 0
    far = [{"lat": 10.0, "lon": 20.0}]
    cells2, _, skipped2 = i3.resolve_cells(far, lat, lon, np.zeros((3, 3), dtype=bool))
    assert cells2 == {} and skipped2 == 1, "no land anywhere means skip, not default"


def test_freezing_ambient_still_ages_slowly_not_negatively():
    v = float(i5.f_aa(np.array([-30.0]))[0])
    assert 0.0 < v < 0.05, f"F_AA at -30C should be small and positive, got {v}"
