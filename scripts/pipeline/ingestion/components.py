"""Component builder — the fourth ingestion stage (M-061, 20 August 2026).

WHY THIS MODULE EXISTS
──────────────────────
Until today the pipeline had three ingestion stages — seismic, climate
trajectory, socio-economic — and every one of them wrote into the **modifier**
chain. Meanwhile every per-country `merge_into_ssi_data.py` initialises

    "components": {}

and nothing in the estate ever filled it. `compute_r_base` consumes
`components`; no producer existed. That is the structural reason 637,832
substations (88.4% of the cohort) are Unclassified — not a missing data feed,
a missing stage — and it is also where M-046 came from: `compute_r_base` read
`components.get(comp, 0)` from a dict the pipeline hardcodes empty, so every
ingested-but-unenriched substation scored R_base = 0.0.

This module is that missing stage.

THE RULE IT IS BUILT AROUND
───────────────────────────
**A component letter is emitted only when every metric feeding it is present.**

The temptation here is large and wrong: we can derive I1 and I3 today, so we
could write `components["I"]` from two of nine metrics and let 637,832 records
become scoreable. That reproduces M-046 exactly — the seven absent metrics
would contribute zero, `I` would be systematically understated, and because R
is a *risk* score the error would again be biased toward reassurance, cohort
wide. Partial evidence is not evidence of a low score.

So `rollup_components` refuses to emit a letter whose metric set is incomplete,
and records the reason. This stage makes the gap **visible and precise**; it
does not paper over it.

WHAT IS IMPLEMENTED TODAY
─────────────────────────
I1 and I3, from the ERA5-Land baseline already cached on disk for all 39
countries (`scripts/pipeline/.cache/era5_baseline_<country>.json`), acquired
through the documented three-tier climate chain (P15-A-4). No new acquisition,
no new licence question, full provenance.

Everything else is declared in METRIC_REGISTRY with an explicit `status` and,
where blocked, the source that would unblock it. That registry is the point of
this module as much as the two builders are: it is the first place in the
estate that states, per metric, what is computed and what is missing.

A NOTE ON THE ERA5 BASELINE
───────────────────────────
`climate.compute_iri_forward()` fetches this same baseline and then never
references it — trajectories are computed purely from CMIP6 deltas. The data
was already being paid for and discarded. This module consumes it.

Cross-reference: Convention #56, CLAUDE.md Discipline #50,
SSI_INGESTION_ARCHITECTURE_AUDIT_20260820.md, SSI_METRIC_IMPLEMENTATION_DISCLOSURE_v1.md.
"""

from __future__ import annotations

import json
import logging
import math
from pathlib import Path

from ..config import CACHE_DIR
from ..scoring.engine import INTRA_WEIGHTS, soft_clip

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[3]

#: Provenance recorded on every metric this module writes. Mirrors the
#: `source_agency` convention used by climate.py and seismic.py.
ERA5_PROVENANCE = {
    "source": "ERA5-Land 0.1° reanalysis (Copernicus Climate Data Store)",
    "source_agency": "ECMWF / Copernicus C3S",
    "licence": "EU Copernicus open licence",
    "attribution": "Contains modified Copernicus Climate Change Service information",
    "doi": "10.24381/cds.e9c9c792",
    "tier": "2 — international fallback (P15-A-4)",
}


METRIC_REGISTRY = {
    # ── C — Continuity (component weight 0.30) ──
    "C1": {"component": "C", "intra": 0.40, "name": "Outage duration (SAIDI)",
           "status": "blocked", "blocked_on": "regulator continuity return — SAIDI, sub-national"},
    "C2": {"component": "C", "intra": 0.30, "name": "Outage count (SAIFI)",
           "status": "blocked", "blocked_on": "regulator continuity return — SAIFI, sub-national"},
    "C3": {"component": "C", "intra": 0.15, "name": "MV exceedance rate",
           "status": "blocked", "blocked_on": "regulator continuity return — C3_MT_exceed_pct"},
    "C4": {"component": "C", "intra": 0.15, "name": "Planned outages",
           "status": "blocked", "blocked_on": "regulator continuity return — planned/unplanned split"},

    # ── V — Voltage (0.10) ──
    "V1": {"component": "V", "intra": 1.00, "name": "Severity-weighted voltage (SAIDI × V_socio proxy)",
           "status": "blocked", "blocked_on": "SAIDI; V_socio is already present at 100% coverage"},

    # ── I — Infrastructure (0.25) ──
    "I1": {"component": "I", "intra": 0.12, "name": "Ice / snow risk",
           "status": "implemented", "inputs": ["ice_days"], "direction": "higher = higher risk",
           "proxy_note": "ice_days (T_max < 0 °C day count) substituted for the construct's "
                         "HDD_annual/10000. A frost-day count is a more direct ice-loading "
                         "proxy than heating degree-days, but it is still a proxy — see the "
                         "metric implementation disclosure."},
    "I2": {"component": "I", "intra": 0.09, "name": "Tree-fall / wind risk",
           "status": "blocked", "blocked_on": "wind speed — NOT in the cached ERA5 baseline "
                                              "(fields are lat/lon/t_mean_c/heat_days/ice_days "
                                              "across all 39 countries)"},
    "I3": {"component": "I", "intra": 0.15, "name": "Heat-wave risk",
           "status": "implemented", "inputs": ["heat_days"], "direction": "higher = higher risk",
           "proxy_note": "heat_days (T_max > 25 °C day count) substituted for the construct's "
                         "CDD_annual/2000."},
    "I4": {"component": "I", "intra": 0.12, "name": "Line density, inverted", "inverted": True,
           "status": "blocked",
           "blocked_on": "grid-geo lines exist (sharded as grid-geo-l-NN.json for germany, france, "
                         "us) but grid-geo's substation ID space diverges from the fleet, and "
                         "differently per country: italy matches exactly, poland is prefix-only "
                         "(225674207 vs PL_225674207), greece is positional (0,1,2 vs "
                         "GR-ADMIE-0000), uk does not match at all. A line-to-unit join needs "
                         "per-country ID reconciliation first — Convention #80 grid-geo is not "
                         "uniformly joinable to ssi-data."},
    "I5": {"component": "I", "intra": 0.12, "name": "Thermal stress (IEEE C57.91)",
           "status": "blocked", "blocked_on": "peak_load_MW / avg_load_MW"},
    "I6": {"component": "I", "intra": 0.12, "name": "Substation density, inverted",
           "status": "implemented", "inputs": ["region substation count"], "inverted": True,
           "proxy_note": "Counted from the ssi-data fleet itself, NOT from grid-geo — the "
                         "authoritative substation set, and it sidesteps the ID-space divergence "
                         "that blocks I4. The unit is `region`, matching the construct's 'count "
                         "in the unit'. Records carrying no region get no I6 rather than a "
                         "default, so the component refuses to roll up for them."},
    "I7": {"component": "I", "intra": 0.10, "name": "Load stress",
           "status": "blocked", "blocked_on": "avg_load_MW"},
    "I8": {"component": "I", "intra": 0.08, "name": "Air-quality corrosion (ISO 9223)",
           "status": "blocked", "blocked_on": "air quality / coastal exposure dataset"},
    "I9": {"component": "I", "intra": 0.10, "name": "Hydrogeological risk",
           "status": "blocked", "blocked_on": "flood hazard layer (shares its input with S2)"},

    # ── E — Economic (0.10) ──
    "E1": {"component": "E", "intra": 0.55, "name": "Continuity penalties per LV user",
           "status": "blocked", "blocked_on": "C1_raw and avg_load_MW"},
    "E2": {"component": "E", "intra": 0.45, "name": "Capital-intensity mix",
           "status": "blocked",
           "blocked_on": "`E2_local` is present on every record but its producer is not in the "
                         "estate — it appears in no ingestion module. Provenance must be "
                         "established before it can feed a published score (M-052 precedent)."},

    # ── S — Saturation (0.20) ──
    "S1": {"component": "S", "intra": 0.75, "name": "Generation / consumption KPI",
           "status": "blocked", "blocked_on": "res_capacity_MW and avg_load_MW"},
    "S2": {"component": "S", "intra": 0.125, "name": "Reverse power flow",
           "status": "blocked", "blocked_on": "flood hazard layer (as implemented) or true RPF data"},
    "S3": {"component": "S", "intra": 0.125, "name": "Criticality of served load",
           "status": "blocked", "blocked_on": "critical-infrastructure register"},

    # ── T — Transition (0.05) ──
    "T1": {"component": "T", "intra": 1.00, "name": "DER / EV transition pressure",
           "status": "blocked", "blocked_on": "S1_raw, DER variability, EV load ratio"},
}


def _registry_selfcheck():
    """The registry must agree with the engine's own intra-weights.

    A registry that drifts from INTRA_WEIGHTS would let a component roll up from
    the wrong metric set — silently, and in the direction nobody checks.
    """
    problems = []
    for comp, weights in INTRA_WEIGHTS.items():
        declared = {m for m, spec in METRIC_REGISTRY.items() if spec["component"] == comp}
        expected = set(weights)
        if declared != expected:
            problems.append(f"{comp}: registry has {sorted(declared)}, engine has {sorted(expected)}")
            continue
        for m, w in weights.items():
            if abs(METRIC_REGISTRY[m]["intra"] - w) > 1e-9:
                problems.append(f"{m}: registry intra {METRIC_REGISTRY[m]['intra']} != engine {w}")
    if problems:
        raise ValueError("METRIC_REGISTRY disagrees with engine INTRA_WEIGHTS: " + "; ".join(problems))


_registry_selfcheck()


def implemented_metrics():
    return sorted(m for m, s in METRIC_REGISTRY.items() if s["status"] == "implemented")


def blocked_metrics():
    return sorted(m for m, s in METRIC_REGISTRY.items() if s["status"] != "implemented")


# ═══════════════════════════════════════════════════════════
#  Normalisation — Method A/B, fleet percentile, per country
# ═══════════════════════════════════════════════════════════

def _percentile(sorted_vals, q):
    if not sorted_vals:
        return None
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    pos = q * (len(sorted_vals) - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = pos - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def norm_percentile(x, p5, p95, inverted=False):
    """Construct Method A/B. Returns None when the fleet has no spread.

    P5 == P95 means every substation in the country shares one value, so the
    metric carries no within-country information. The construct's own
    reference implementation returns 0.5 here; that is a silent default —
    a constant masquerading as a measurement, which is the `EV_load_ratio`
    defect. Return None instead so the metric is absent rather than inert,
    and the component refuses to roll up.
    """
    if x is None or p5 is None or p95 is None or p95 == p5:
        return None
    n = (x - p5) / (p95 - p5)
    if inverted:
        n = 1.0 - n
    return round(soft_clip(n), 4)


# ═══════════════════════════════════════════════════════════
#  Climate baseline lookup
# ═══════════════════════════════════════════════════════════

def load_era5_baseline(country):
    fp = Path(CACHE_DIR) / f"era5_baseline_{country}.json"
    if not fp.exists():
        logger.warning(f"{country}: no cached ERA5 baseline at {fp}")
        return None
    grid = json.loads(fp.read_text(encoding="utf-8"))
    if not isinstance(grid, list) or not grid:
        logger.warning(f"{country}: ERA5 baseline is empty or not a list")
        return None
    return grid


def _index_grid(grid, cell=0.5):
    idx = {}
    for pt in grid:
        key = (round(pt["lat"] / cell), round(pt["lon"] / cell))
        idx.setdefault(key, []).append(pt)
    return idx


def _nearest(idx, lat, lon, cell=0.5, max_rings=3):
    key = (round(lat / cell), round(lon / cell))
    best, best_d = None, None
    for ring in range(max_rings + 1):
        for dr in range(-ring, ring + 1):
            for dc in range(-ring, ring + 1):
                if ring and max(abs(dr), abs(dc)) != ring:
                    continue
                for pt in idx.get((key[0] + dr, key[1] + dc), ()):
                    d = (pt["lat"] - lat) ** 2 + (pt["lon"] - lon) ** 2
                    if best_d is None or d < best_d:
                        best, best_d = pt, d
        if best is not None:
            return best, math.sqrt(best_d) * 111.32
    return None, None


# ═══════════════════════════════════════════════════════════
#  Stage 1 — raw metric extraction
# ═══════════════════════════════════════════════════════════

def build_metrics(country, subs):
    """Attach raw metric values (pre-normalisation) to each substation.

    Returns (n_written, stats). Mutates `subs` in place: each record gains a
    `metrics` block keyed by metric id, each carrying `raw`, provenance and
    the match distance.
    """
    grid = load_era5_baseline(country)
    if grid is None:
        return 0, {"reason": "no cached ERA5 baseline"}

    idx = _index_grid(grid)
    n = 0
    dists = []
    for s in subs:
        lat, lon = s.get("lat"), s.get("lon")
        if lat is None or lon is None:
            continue
        pt, dist_km = _nearest(idx, lat, lon)
        if pt is None:
            continue
        # Provenance is written ONCE at document level (see metric_provenance()),
        # not repeated per substation. At 721,275 records a full provenance
        # block per metric would add ~290 MB to the cohort for information that
        # is identical on every row; the per-record payload keeps only what
        # actually varies — the value, its normalisation, and the spatial-join
        # distance that makes the match auditable.
        metrics = s.get("metrics") or {}
        if pt.get("ice_days") is not None:
            metrics["I1"] = {"raw": pt["ice_days"], "match_km": round(dist_km, 2)}
        if pt.get("heat_days") is not None:
            metrics["I3"] = {"raw": pt["heat_days"], "match_km": round(dist_km, 2)}
        if metrics:
            s["metrics"] = metrics
            n += 1
            dists.append(dist_km)

    # I6: substation density per region, from the authoritative fleet.
    # Deliberately not grid-geo: its substation ID space diverges from the
    # fleet, differently per country (see I4's blocked_on).
    region_counts = {}
    for s in subs:
        r = s.get("region")
        if r:
            region_counts[r] = region_counts.get(r, 0) + 1
    n_i6 = 0
    for s in subs:
        r = s.get("region")
        if not r:
            continue          # no region -> no I6. Absent, never defaulted.
        m = s.get("metrics") or {}
        m["I6"] = {"raw": region_counts[r], "unit": "region", "unit_value": r}
        s["metrics"] = m
        n_i6 += 1

    dists.sort()
    return n, {
        "grid_points": len(grid),
        "matched": n,
        "i6_regions": len(region_counts),
        "i6_attached": n_i6,
        "i6_no_region": len(subs) - n_i6,
        "median_match_km": round(_percentile(dists, 0.5), 2) if dists else None,
        "p95_match_km": round(_percentile(dists, 0.95), 2) if dists else None,
    }


# ═══════════════════════════════════════════════════════════
#  Stage 2 — per-country normalisation
# ═══════════════════════════════════════════════════════════

def normalise_metrics(country, subs):
    """Normalise each implemented metric to [0,1] on the country's own P5/P95."""
    anchors = {}
    for mid in implemented_metrics():
        vals = sorted(s["metrics"][mid]["raw"] for s in subs
                      if (s.get("metrics") or {}).get(mid, {}).get("raw") is not None)
        if not vals:
            continue
        p5, p95 = _percentile(vals, 0.05), _percentile(vals, 0.95)
        anchors[mid] = {"P5": round(p5, 4), "P95": round(p95, 4), "n": len(vals)}
        inverted = bool(METRIC_REGISTRY[mid].get("inverted"))
        for s in subs:
            m = (s.get("metrics") or {}).get(mid)
            if not m or m.get("raw") is None:
                continue
            m["normalised"] = norm_percentile(m["raw"], p5, p95, inverted)
    return anchors


def metric_provenance(country, anchors, stats):
    """Document-level provenance block — written to meta, not to every record."""
    return {
        "built_utc_note": "stamp at call site; this module must stay deterministic",
        "stage": "ingestion/components.py (M-061)",
        "implemented": implemented_metrics(),
        "blocked": {m: METRIC_REGISTRY[m]["blocked_on"] for m in blocked_metrics()},
        "metric_inputs": {m: METRIC_REGISTRY[m].get("inputs") for m in implemented_metrics()},
        "proxy_notes": {m: METRIC_REGISTRY[m].get("proxy_note")
                        for m in implemented_metrics() if METRIC_REGISTRY[m].get("proxy_note")},
        "normalisation": {"method": "per_country_P5_P95_linear (construct Method A/B)",
                          "anchors": anchors},
        "spatial_join": stats,
        "source": ERA5_PROVENANCE,
    }


# ═══════════════════════════════════════════════════════════
#  Stage 3 — roll-up, refusing incomplete components
# ═══════════════════════════════════════════════════════════

def rollup_components(subs):
    """Emit a component letter only when every metric feeding it is present.

    This is the whole safety property of the module. See the module docstring:
    emitting `I` from 2 of 9 metrics would understate it by construction and
    bias the score toward reassurance — M-046's exact failure mode.
    """
    emitted = {c: 0 for c in INTRA_WEIGHTS}
    refused = {c: 0 for c in INTRA_WEIGHTS}
    for s in subs:
        metrics = s.get("metrics") or {}
        comps = s.get("components") or {}
        missing_by_comp = {}
        for comp, weights in INTRA_WEIGHTS.items():
            missing = [m for m in weights
                       if metrics.get(m, {}).get("normalised") is None]
            if missing:
                missing_by_comp[comp] = missing
                refused[comp] += 1
                continue
            comps[comp] = round(
                sum(w * metrics[m]["normalised"] for m, w in weights.items()), 4)
            emitted[comp] += 1
        if comps:
            s["components"] = comps
        if missing_by_comp:
            s["_components_incomplete"] = {
                c: sorted(ms) for c, ms in missing_by_comp.items()}
    return emitted, refused


# ═══════════════════════════════════════════════════════════
#  Orchestrator entry point — called by scripts/pipeline/run.py
# ═══════════════════════════════════════════════════════════

def build_component_metrics(country, dry_run=False, repo_root=None):
    """Run the full component-builder stage for one country.

    Returns a stats dict, or None if the country has no cached climate
    baseline. Writes through `write_ssi_data` so Convention #79 sharding and
    the M-055 atomic-write guarantee both apply.
    """
    from ..utils.ssi_data_sharding import read_ssi_data, write_ssi_data

    root = Path(repo_root) if repo_root else REPO_ROOT
    path = root / country / "ssi-data.json"
    if not path.exists():
        logger.warning(f"{country}: no ssi-data.json at {path}")
        return None

    doc = read_ssi_data(path)
    subs = doc.get("substations") or []
    if not subs:
        logger.warning(f"{country}: no substations")
        return None

    attached, stats = build_metrics(country, subs)
    if not attached:
        logger.warning(f"{country}: no metrics attached — {stats.get('reason', 'unknown')}")
        return None

    anchors = normalise_metrics(country, subs)
    emitted, refused = rollup_components(subs)

    result = {
        "country": country,
        "fleet": len(subs),
        "metrics_attached": attached,
        "anchors": anchors,
        "emitted": emitted,
        "refused": refused,
        "implemented": implemented_metrics(),
        "blocked": blocked_metrics(),
    }

    if dry_run:
        logger.info(f"{country}: DRY RUN — not written")
        return result

    meta = doc.get("meta") or {}
    prov = metric_provenance(country, anchors, stats)
    prov.pop("built_utc_note", None)
    meta["metric_build"] = prov
    meta["n_metrics_built_m061"] = attached
    doc["meta"] = meta
    write_ssi_data(doc, path)
    logger.info(f"{country}: component metrics written ({attached:,} substations)")
    return result
