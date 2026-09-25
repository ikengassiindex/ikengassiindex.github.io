#!/usr/bin/env python3
"""
Restore substations the canonical lost, from the v4.0.2 backup beside it.

    python3 scripts/ssi_restore_from_v402_backup.py sweden
    python3 scripts/ssi_restore_from_v402_backup.py sweden --apply

Run from the repo root. Dry run by default.

WHAT THIS IS FOR
----------------
sweden publishes 1,192 substations and draws 4,014 on its map. It is the
largest Nordic country by area and population and scores 3.3x fewer
substations than finland.

The missing fleet was never lost. sweden/_v4.0.2.backup/ssi-data.json holds
3,872 substations, every one carrying a full component vector, real Monte
Carlo output (10,000 iterations), CI widths with a median of 0.1984 and not a
single zero-width interval. Five separate deploy repositories hold the same
3,872. Convention #56's backup discipline kept it all along.

Measured against sweden: 1,176 of the live 1,192 have a v4.0.2 twin within
50 m, so the live canonical is very nearly a subset of the backup. 2,707
backup substations have no live twin, and 2,678 of those are exactly the
records grid-geo is still drawing as unscored grey dots.

WHY RESTORE RATHER THAN MERGE FROM THE MAP
-------------------------------------------
grid-geo entries carry four fields: coordinates, a name and a voltage. Merging
those and running the pipeline produces R_median 0.0, classification "Low" and
confidence_tier "high" on every record — the pipeline consumes component
vectors, it does not create them.

The backup records carry components, modifiers, graph topology, markov,
transition, seismic and climate. Restoring them gives the v4.2 engine
something real to rescore, so the Monte Carlo runs, the confidence interval
has width, and the band means something.

WHAT THIS DOES NOT FIX
-----------------------
The v4.0.2 component vectors are det_var output: regionally anchored (S tracks
per-region seismic PGA, which is why sweden's S median sits at 0.169) with
per-substation variation drawn from md5(substation_id + name). That is the
same provenance every other country's components have. This brings sweden to
cohort parity. It does not make the components measured, and the separate
component-provenance workstream still stands.

THE DISCIPLINE #36 GATE
-----------------------
Only records inside the country's bounds.json polygon are restored. On sweden
that is 2,582 of 2,707; the excluded 125 are cross-border. Restoring blind
would be actively wrong on some countries — canada's backup holds 24,986
against a live 7,506, but that gap is the Discipline #36 remediation that
correctly removed a fleet which was 74.4% outside Canada. The polygon gate is
what makes this tool safe to point at a country other than sweden.

WHAT IS PORTED, AND WHAT IS DELIBERATELY NOT
---------------------------------------------
Ported: substation_id, name, lat, lon, voltage_kv, components, modifiers,
graph_topology, markov, transition, seismic, climate_trajectory.

region is ported through a name map built from the live canonical's own region
set, because the vintages disagree — v4.0.2 says "Stockholms län" where v4.2
says "Stockholm", and porting raw would fail the KB §56 regional-consistency
gate. The map is derived, verified to resolve every name onto a distinct live
region, and the run aborts if any name cannot be resolved.

province is NOT ported. v4.0.2 stores names ("Uppsala"); v4.2 stores NUTS-3
codes ("SE321"), which is the join key the socio-economic CSV needs. Set to
None per Convention #56, to be filled by the polygon backfill.

socio_economic is NOT ported. The v4.0.2 block holds population 400000 and
gdp_per_capita 490000 — regional aggregates in different units, not the
per-substation catchment values v4.2 expects. The audited enrichments fill it.

graph_topology IS ported but was computed against the v4.0.2 grid graph. It
should be recomputed from the current grid-geo adjacency map, which is a
tractable job nobody has done yet.

AFTER THIS RUNS
---------------
    python3 scripts/pipeline/enrichment/socio_economic_backfill.py --polygon-slug <slug>
    python3 -m scripts.pipeline.run <slug>
    python3 scripts/ssi_dedupe_country.py <slug> --apply

The first assigns NUTS-3 codes and socio-economic fields (needs the Eurostat
GISCO shapefile locally). The second rescores under v4.2 with real Monte
Carlo. The third refreshes every published figure. Nothing should be published
between the first step and the second.
"""
from __future__ import annotations

import argparse
import datetime
import json
import math
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

REPO = Path.cwd()

# seismic and climate_trajectory are deliberately NOT ported, and the reason is
# not obvious. merge.py decides whether to rescore a substation by comparing the
# freshly computed value against the stored one:
#
#     has_seismic = abs(new_pga - sub["seismic"]["pga_g"]) > 0.001
#
# Port the v4.0.2 blocks and the recomputed values match what is already there,
# so needs_rescore stays False and the Monte Carlo never runs — the records keep
# their components and get no R_median at all. Leaving both fields absent makes
# the comparison fall back to its defaults (0.03 pga, 1.0 trajectory), the delta
# clears the threshold, and the substation is scored properly. Verified: with
# them ported, 0 of 2,582 rescored; without, all of them.
PORT_FIELDS = ("name", "lat", "lon", "voltage_kv", "components", "modifiers",
               "graph_topology", "markov", "transition")


def load(path: Path):
    d = json.loads(path.read_text())
    if isinstance(d, list):
        return d, None, True
    if d.get("substations_shards"):
        subs = []
        for e in d["substations_shards"]:
            rel = e["path"] if isinstance(e, dict) else e
            sp = path.parent / Path(rel).name
            if sp.exists():
                q = json.loads(sp.read_text())
                subs += q if isinstance(q, list) else (q.get("substations") or [])
        return subs, d, False
    return (d.get("substations") or []), d, False


def haversine_km(a, b, c, d):
    R = 6371.0
    p = math.radians
    return 2 * R * math.asin(math.sqrt(
        math.sin(p(c - a) / 2) ** 2
        + math.cos(p(a)) * math.cos(p(c)) * math.sin(p(d - b) / 2) ** 2))


class Grid:
    """Coarse spatial bucket. Avoids an O(n*m) scan without a dependency."""

    CELL = 0.01

    def __init__(self, pts):
        self.pts = pts
        self.g = defaultdict(list)
        for i, (la, lo) in enumerate(pts):
            self.g[(int(la / self.CELL), int(lo / self.CELL))].append(i)

    def has_within(self, la, lo, tol_km):
        bi, bj = int(la / self.CELL), int(lo / self.CELL)
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                for i in self.g.get((bi + di, bj + dj), ()):
                    if haversine_km(la, lo, *self.pts[i]) <= tol_km:
                        return True
        return False



FLAT_LO, FLAT_HI = 0.245, 0.455


def is_flat(sub):
    """True when all six components sit inside the band enrich_esg_gaps.py
    produces — vary(0.35, name + '_' + K, 0.30) spans [0.245, 0.455] and gives
    every component the same distribution, so C, V, I, E, S and T carry no
    differentiating signal. Nine countries are filled this way cohort-wide."""
    c = sub.get("components") or {}
    vals = [c.get(k) for k in ("C", "V", "I", "E", "S", "T")]
    if any(not isinstance(v, (int, float)) for v in vals):
        return False
    return all(FLAT_LO - 1e-9 <= v <= FLAT_HI + 1e-9 for v in vals)


def nearest(grid, records, la, lo, tol_km):
    bi, bj = int(la / Grid.CELL), int(lo / Grid.CELL)
    best = None
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            for i in grid.g.get((bi + di, bj + dj), ()):
                d = haversine_km(la, lo, *grid.pts[i])
                if best is None or d < best[1]:
                    best = (i, d)
    return records[best[0]] if best and best[1] <= tol_km else None


def fold(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()


def region_map(old_regions, live_regions):
    """Resolve each v4.0.2 region name onto a live one. Tries exact, then the
    name minus its trailing administrative word, then minus a genitive s, then
    an ASCII fold. Returns (mapping, unresolved)."""
    out, bad = {}, []
    for name in sorted(old_regions):
        cands = [name]
        parts = name.split()
        if len(parts) > 1:
            cands.append(" ".join(parts[:-1]))
        cands += [c[:-1] for c in list(cands) if c.endswith("s")]
        hit = next((c for c in cands if c in live_regions), None)
        if hit is None:
            for c in cands:
                hit = next((t for t in live_regions
                            if fold(t).lower() == fold(c).lower()), None)
                if hit:
                    break
        if hit is None:
            bad.append(name)
        else:
            out[name] = hit
    return out, bad


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--no-refresh", action="store_true",
                    help="do not replace flat-0.35 component vectors on existing "
                         "records that have a backup twin")
    ap.add_argument("--tolerance-m", type=float, default=50.0,
                    help="a backup substation this close to a live one is the "
                         "same facility and is not restored (default 50)")
    args = ap.parse_args()
    slug = args.slug

    live_p = REPO / slug / "ssi-data.json"
    back_p = REPO / slug / "_v4.0.2.backup" / "ssi-data.json"
    for p in (live_p, back_p):
        if not p.exists():
            sys.exit(f"ABORT: {p} not found — run from the repo root.")

    live, root, was_flat = load(live_p)
    if root is not None and root.get("substations_shards"):
        sys.exit(f"ABORT: {slug} is Convention #79 sharded; this tool writes a "
                 f"single manifest and would break the shard contract.")
    backup, _, _ = load(back_p)

    bounds = REPO / slug / "bounds.json"
    if not bounds.exists():
        sys.exit(f"ABORT: {slug}/bounds.json not found — refusing to restore "
                 f"without the Discipline #36 polygon gate.")
    try:
        from shapely.geometry import shape, Point
        from shapely.ops import unary_union
        from shapely.prepared import prep
    except ImportError:
        sys.exit("ABORT: shapely is required — the polygon gate is not optional.")
    b = json.loads(bounds.read_text())
    poly = unary_union([shape(f["geometry"]) for f in (b.get("features") or [b])])
    if not poly.is_valid:
        poly = poly.buffer(0)
    inside = prep(poly)

    tol = args.tolerance_m / 1000.0
    live_grid = Grid([(x["lat"], x["lon"]) for x in live
                      if isinstance(x.get("lat"), (int, float))])
    missing = [x for x in backup
               if isinstance(x.get("lat"), (int, float))
               and not live_grid.has_within(x["lat"], x["lon"], tol)]

    keep = [x for x in missing if inside.contains(Point(x["lon"], x["lat"]))]
    drop = [x for x in missing if not inside.contains(Point(x["lon"], x["lat"]))]

    live_out = sum(1 for x in live
                   if isinstance(x.get("lat"), (int, float))
                   and not inside.contains(Point(x["lon"], x["lat"])))

    live_regions = {x.get("region") for x in live if x.get("region")}
    old_regions = {x.get("region") for x in keep if x.get("region")}
    rmap, unresolved = region_map(old_regions, live_regions)

    with_comp = sum(1 for x in keep if x.get("components"))
    after = len(live) + len(keep)

    print(f"restore from the v4.0.2 backup — {'APPLY' if args.apply else 'DRY RUN'}\n")
    print(f"  {slug} live canonical            {len(live):>8,}")
    print(f"  {slug} v4.0.2 backup             {len(backup):>8,}")
    print(f"  backup records with no live twin {len(missing):>8,}   (within {args.tolerance_m:g} m)")
    print(f"     inside bounds.json  -> restore{len(keep):>8,}")
    print(f"     outside             -> skip   {len(drop):>8,}   Discipline #36")
    print(f"  of those restored, with components{with_comp:>7,}")
    print(f"  canonical after restore          {after:>8,}")
    print(f"  outside-polygon share after      {live_out / max(after,1) * 100:>7.2f}%   (gate fails above 5%)")

    gg = REPO / slug / "grid-geo.json"
    if gg.exists():
        n_map = len(json.loads(gg.read_text()).get("s") or {})
        print(f"  the map draws                    {n_map:>8,}   residual gap {n_map - after:+,}")

    if unresolved:
        print(f"\n  ABORT: {len(unresolved)} v4.0.2 region name(s) do not resolve onto "
              f"a live region:")
        for n in unresolved:
            print(f"            {n!r}")
        print("  Porting these raw would fail the KB §56 regional-consistency gate.")
        sys.exit(2)

    print(f"\n  region names resolved            {len(rmap):>8} onto {len(set(rmap.values()))} distinct live regions")
    for k, v in list(sorted(rmap.items()))[:4]:
        print(f"            {k!r:<26} -> {v!r}")
    if len(rmap) > 4:
        print(f"            ... and {len(rmap) - 4} more")

    if not args.apply:
        print("\n  dry run — nothing written.\n")
        print("  On --apply, province is left None and socio_economic is not")
        print("  ported: the vintages disagree on both. Then, in order:")
        print(f"      python3 scripts/pipeline/enrichment/socio_economic_backfill.py --polygon-slug {slug}")
        print(f"      python3 -m scripts.pipeline.run {slug}")
        print(f"      python3 scripts/ssi_dedupe_country.py {slug} --apply")
        print("  Do not publish between the first and the second.")
        return 0

    stamp = datetime.datetime.now(datetime.timezone.utc)
    live_p.with_suffix(".json.pre-restore-v402-%s.backup"
                       % stamp.strftime("%Y%m%dT%H%M%SZ")).write_bytes(live_p.read_bytes())

    version = next((x.get("version") for x in live if x.get("version")), "4.2")
    for src in keep:
        rec = {k: src[k] for k in PORT_FIELDS if k in src}
        rec["substation_id"] = str(src.get("substation_id"))
        if src.get("region"):
            rec["region"] = rmap[src["region"]]
        rec["province"] = None
        # These records are about to be scored by the v4.2 engine. The backup is
        # a v4.0.2 vintage of DATA; what lands here is v4.2 output.
        rec["version"] = version
        rec["_restored_from_v402_backup"] = stamp.isoformat()
        live.append(rec)

    # Repair the flat-0.35 fill on records that have a backup twin.
    n_refresh = 0
    if not args.no_refresh:
        bgrid_pts = [(x["lat"], x["lon"]) for x in backup
                     if isinstance(x.get("lat"), (int, float))]
        bidx = Grid(bgrid_pts)
        blist = [x for x in backup if isinstance(x.get("lat"), (int, float))]
        for sub in live:
            if sub.get("_restored_from_v402_backup") or not is_flat(sub):
                continue
            twin = nearest(bidx, blist, sub["lat"], sub["lon"], tol)
            if twin is None or not twin.get("components"):
                continue
            sub["_components_flat035_replaced"] = stamp.isoformat()
            sub["_components_flat035_previous"] = sub.get("components")
            sub["components"] = twin["components"]
            n_refresh += 1

    payload = live if was_flat else dict(root or {}, substations=live)
    if not was_flat:
        payload.setdefault("meta", {}).setdefault("v402_restores", []).append({
            "utc": stamp.isoformat(),
            "restored": len(keep),
            "skipped_outside_polygon": len(drop),
            "canonical_before": len(live) - len(keep),
            "canonical_after": len(live),
            "note": "substations present in _v4.0.2.backup and absent from the "
                    "live canonical; polygon-gated per Discipline #36; province "
                    "and socio_economic deliberately not ported; unscored under "
                    "v4.2 until pipeline.run",
        })
    live_p.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))

    print(f"\n  written — {len(keep):,} restored, canonical now {len(live):,}")
    if n_refresh:
        print(f"            {n_refresh:,} existing records had their flat-0.35 component")
        print(f"            vector replaced from a backup twin (previous kept in")
        print(f"            _components_flat035_previous)")
    print(f"  backup beside it as .pre-restore-v402-*.backup (gitignored)")
    print(f"\n  REQUIRED NEXT, in order:")
    print(f"      python3 scripts/pipeline/enrichment/socio_economic_backfill.py --polygon-slug {slug}")
    print(f"      python3 -m scripts.pipeline.run {slug}")
    print(f"      python3 scripts/ssi_dedupe_country.py {slug} --apply")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
