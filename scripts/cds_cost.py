#!/usr/bin/env python3
"""cds_cost.py — the shared pieces of every CDS/EWDS cost probe.

Extracted 21 September 2026, immediately after `estimate_fire_fetch_cost.py`
landed, and BEFORE a second probe was written, so the estate does not acquire a
second copy of the defect that probe found in itself.

That defect, for the record: `estimate_costs()` returns a MAPPING,
`{'id': 'size', 'cost': 366.0, 'limit': 3720.0}`. Read with
`getattr(costs, "cost", 0)` it yields 0.0 silently — a cost probe whose failure
mode is printing "free". `field()` below reads it as a mapping and RAISES
rather than defaulting, so a shape change is loud.

CREDENTIALS ARE NEVER PASSED TO A PROBE and are never printed. They are read
from the estate's single `.env` named in Pin 9. Two endpoints live in it:

    CDS_API_URL  / CDS_API_KEY    Climate Data Store        (ERA5, CERRA, ...)
    EWDS_API_URL / EWDS_API_KEY   Early Warning Data Store  (CEMS fire, GloFAS)
"""
from __future__ import annotations
import glob as _glob
import os
import re

ENV_TAIL = os.path.join("SSI Index", "SSI_v4_2 Italy Pilot", "pipeline-v4.2", ".env")


def find_env(explicit=None):
    """Locate the estate credential store, or None.

    `scripts/fetch_era5_I1_I2.py:118` resolves ROOT.parent / "SSI Index" / ...,
    which is /Users/<user>/SSI Index/... and has never existed — a default
    masked because that script is always given --env. Resolved here by
    searching the places the one file is actually seen from, and the path found
    is printed by the caller so the run is auditable.
    """
    if explicit:
        return explicit if os.path.exists(explicit) else None
    home = os.path.expanduser("~")
    candidates = [
        # the Mac, where the operator runs it
        os.path.join(home, "Library", "CloudStorage", "OneDrive-IkengaSL",
                     "Internal - IKENGA EU - Documents", "0.22. IP agenda", ENV_TAIL),
        # the Cowork device VM, where the same folder is mounted elsewhere
        os.path.join(home, "mnt", ENV_TAIL),
        os.path.join(home, ENV_TAIL),
    ]
    candidates += sorted(_glob.glob(os.path.join(
        home, "Library", "CloudStorage", "OneDrive-*", "**", ENV_TAIL), recursive=True))
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def load_env(env_path):
    """Read the credential store. Values are returned, never printed.

    Same shape as scripts/fetch_era5_I1_I2.py::load_env — deliberately, so the
    estate has one convention rather than four.
    """
    env = {}
    with open(env_path, encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            m = re.match(r"\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$", ln)
            if m:
                env[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return env


def field(costs, name):
    """Read one field of an estimate_costs() result. Raises rather than defaults."""
    if isinstance(costs, dict):
        return float(costs[name])
    return float(getattr(costs, name))


def open_client(env, prefix):
    """Authenticated ecmwf-datastores client for 'CDS' or 'EWDS'. Never prints the key."""
    from ecmwf.datastores import Client
    key = env.get("%s_API_KEY" % prefix)
    if not key:
        raise SystemExit(
            "%s_API_KEY not found in the credential store. %s is a separate "
            "registration; add %s_API_URL and %s_API_KEY to that same file."
            % (prefix, prefix, prefix, prefix))
    return Client(url=env.get("%s_API_URL" % prefix), key=key)


def fields_per_combination(product_type):
    """How many fields ONE selector combination delivers for this product_type.

    Measured 21 September 2026: estimate_costs() counts SELECTOR COMBINATIONS,
    not delivered fields. It answers "will the CDS accept this request?" and
    NOT "how much data will arrive?". For reanalysis / ensemble_mean /
    ensemble_spread the two coincide. For ensemble_members they do not: the
    ERA5 ensemble is 10-member, so the identical request delivers ten times the
    volume at one times the price, and the cost limit gives no warning.
    """
    return 10 if product_type == "ensemble_members" else 1


def price(client, dataset, request):
    """(cost, limit) for one request, priced server-side. Nothing is queued.

    NOTE: cost is a count of selector combinations. To reason about VOLUME,
    multiply by fields_per_combination() of the request's product_type.
    """
    c = client.get_process(dataset).estimate_costs(request)
    return field(c, "cost"), field(c, "limit")


def sweep(client, dataset, build_request, counts, label="years"):
    """Price the same request at several sizes and print how cost scales.

    Returns the largest count that priced within the limit, or None. The point
    is the BOUNDARY: cost per unit is arithmetic, and arithmetic is what put a
    limit of 400 into the fire plan when the real one was 3720.
    """
    base = None
    largest_ok = None
    for n in counts:
        try:
            cost, limit = price(client, dataset, build_request(n))
        except Exception as exc:
            print("  %3d %-7s estimate FAILED: %s" % (n, label, exc))
            continue
        ok = cost <= limit
        if ok:
            largest_ok = n if largest_ok is None else max(largest_ok, n)
        if base is None:
            base = cost
        print("  %3d %-7s cost %10.1f  limit %10.1f  %-4s  x%.2f vs %d"
              % (n, label, cost, limit, "OK" if ok else "OVER",
                 (cost / base) if base else float("nan"), counts[0]))
    return largest_ok


def find_boundary(client, dataset, build_request, lo=1, hi=90, label="years"):
    """Bisect for the largest window that prices within the limit, and MEASURE
    the first one that does not.

    A ladder (1, 2, 5, 10) brackets the boundary; it does not locate it. The
    estate's rule after the fire probe is that the boundary is measured, not
    inferred, because inference is what put a limit of 400 into the fire plan
    when the real one was 3720. Four extra priced calls settle it.

    Returns (largest_ok, its cost, first_over, its cost, limit).
    """
    def ok(n):
        cost, limit = price(client, dataset, build_request(n))
        return cost <= limit, cost, limit

    good, cost_good, limit = ok(lo)
    if not good:
        return None, cost_good, lo, cost_good, limit
    best, best_cost = lo, cost_good
    worst, worst_cost = None, None
    top_ok, _, _ = ok(hi)
    if top_ok:
        return hi, None, None, None, limit
    worst = hi
    while worst - best > 1:
        mid = (best + worst) // 2
        good, cost, limit = ok(mid)
        if good:
            best, best_cost = mid, cost
        else:
            worst, worst_cost = mid, cost
    if worst_cost is None:
        _, worst_cost, limit = ok(worst)
    print("  boundary: %d %s price at %.1f (OK) — %d %s price at %.1f (OVER of %.1f)"
          % (best, label, best_cost, worst, label, worst_cost, limit))
    return best, best_cost, worst, worst_cost, limit
