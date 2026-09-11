"""
One place to strip negative zero from anything about to be published.

WHY THIS MODULE EXISTS

    round() on a small negative returns -0.0. It is numerically equal to 0.0
    and compares equal to it, so `v < 0` is False and `v == 0` is True — but
    it serialises into JSON as the token "-0.0", and anything that reads the
    text rather than parsing it shows a negative.

    On 9 September this reached production as metrics.I1 = -0.0 on 23,997
    substations: a negative snow load. It was clamped at I1's write site and
    recorded as fixed.

    On 11 September a sweep of all 73 published JSON files found 251 more, in
    30 of 39 countries, in modifier_impacts.* and skewness — fields nobody had
    looked at, because the first fix went where the first bug was.

    engine.py has 27 round() call sites. Two of them are known to have emitted
    -0.0. The other 25 are clean only because no value has yet landed in that
    band. Patching the two known sites would leave 25 latent and would be the
    third repair in two days to fix one place of several.

    So: one helper, applied at the boundaries where records leave the scoring
    engine, covering every field those records carry — including fields added
    later, which is the part a point fix cannot do.

WHAT IT DOES NOT DO

    It does not clamp negatives. A modifier impact and a skewness can
    legitimately be negative and must stay negative. Only the zero with a sign
    bit is normalised, and only because -0.0 and 0.0 are the same number.

    It does not touch NaN or Infinity. Those are not valid JSON and are a
    different defect; scripts/audit_published_json.py reports them separately
    so that one problem is not quietly absorbed into the fix for another.
"""
from __future__ import annotations
import math

__all__ = ["nz", "clean"]


def nz(x):
    """Negative zero -> positive zero. Everything else returned unchanged.

    >>> nz(-0.0), nz(0.0), nz(-0.5), nz(3), nz(None)
    (0.0, 0.0, -0.5, 3, None)
    """
    if isinstance(x, float) and x == 0.0 and math.copysign(1.0, x) < 0:
        return 0.0
    return x


def clean(obj):
    """Recursively normalise negative zero in a JSON-shaped structure.

    Returns a new container; scalars are returned as-is unless they are
    negative zero. bool is left alone deliberately — it is a subclass of int
    and must not be coerced to a number.

    >>> clean({"a": -0.0, "b": [-0.0, -0.5], "c": "x", "d": True})
    {'a': 0.0, 'b': [0.0, -0.5], 'c': 'x', 'd': True}
    """
    if isinstance(obj, dict):
        return {k: clean(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean(v) for v in obj]
    if isinstance(obj, tuple):
        return tuple(clean(v) for v in obj)
    if isinstance(obj, bool):
        return obj
    return nz(obj)
