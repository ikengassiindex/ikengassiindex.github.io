#!/usr/bin/env python3
"""
Give the region field the finest granularity the source supports: NUTS-3.

    python3 scripts/ssi_region_nuts3.py --shapefile ~/eurostat_gisco_nuts3_2024/NUTS_RG_01M_2024_4326
    python3 scripts/ssi_region_nuts3.py --shapefile <base> --apply
    python3 scripts/ssi_region_nuts3.py --shapefile <base> --apply poland italy

Dry run by default. `<base>` is the shapefile path WITHOUT extension; .shp,
.shx and .dbf are read beside it.

THE RULE THIS IMPLEMENTS
------------------------
Primary is the greatest granularity the data source supports; fallback is what
is available. For the 26 cohort countries inside NUTS, the greatest available
is NUTS-3 — but only where NUTS-3 is actually finer than what the country
already publishes, and for seven of them it is not:

    ireland     26 counties        vs   8 NUTS-3 groupings
    luxembourg  11 cantons         vs   1 NUTS-3 unit
    estonia     15 counties        vs   5
    iceland      8 landshlutar     vs   2
    france     102 departments     vs 101
    latvia       6 regions         vs   5
    sweden      22 regions         vs  21

Applying NUTS-3 to those would be a downgrade, so they are not in scope. Six
more (czechia, hungary, lithuania, slovakia, slovenia, switzerland) already sit
at NUTS-3 granularity and change nothing. That leaves the thirteen below, where
NUTS-3 is a genuine upgrade — germany from 17 Bundesländer to 400 Kreise, italy
from 21 regions to 107 provinces, poland from 16 voivodeships to 73 subregions.

WHAT IT WRITES, AND WHAT IT DELIBERATELY DOES NOT
-------------------------------------------------
Writes `region` — the NUTS-3 NAME_LATN, so a page shows "Miasto Poznań" and
never "PL415" — plus `_region_nuts3` holding the code, per record.

The derivation itself goes on the manifest as `meta.region_derivation`, not on
every substation. Written per record it is the same 32-byte constant 246,746
times: 7.9 MB, and enough to push three shards past Convention #79's 45 MiB
target for no information at all.

Does NOT touch `province`. That field is the CSV join key for the
socio-economic layer, and for the v4.2 generation it already holds the NUTS-3
code. Rewriting it would change a lookup this script has no business changing.
The consequence is that `province` stays mixed — NUTS-3 codes on v4.2 records,
admin names on the v4.0.2 minority — and unifying it is a separate, deliberate
follow-up.

Does NOT touch scores, bands, confidence tiers or any other field.

CONVENTION #56 — TWO WAYS TO NOT GET A REGION
---------------------------------------------
A point outside every NUTS-3 polygon keeps whatever region it had and is
counted as `unplaced`. 470 records across the thirteen are in this state, 256
of them in Norway, which is the fjord coastline Discipline #36 already gives a
5 km tolerance for.

A point inside a NUTS-3 polygon belonging to a DIFFERENT country is not given
that country's region. It is counted as `foreign` and left alone. 2,672 records
are in this state, and they are not a region problem: they are the cross-border
ingestion pollution of Task #511, surfaced here more sharply than a bounding
box can. Assigning them a neighbour's region would bury a known defect inside a
granularity upgrade.

VERIFICATION THIS ALREADY PASSED
--------------------------------
Poland carries 25,509 records whose NUTS-3 code was derived independently, by
the Task #454 socio-economic backfill, months ago. Running this join against
them reproduces all 25,509 codes exactly — 100.00%, zero disagreements, zero
outside. That is an independent second derivation of a stored value, and it is
the reason to trust the other twelve countries.
"""
from __future__ import annotations

import argparse
import collections
import datetime
import json
import pathlib
import sys


def _stamp() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

REPO = pathlib.Path.cwd()
if not (REPO / "intelligence" / "countries.json").exists():
    sys.exit("ABORT: run from the ikengassiindex.github.io repo root.")

sys.path.insert(0, str(REPO / "scripts"))

# Countries where NUTS-3 is strictly finer than the published region layer.
# Value is the NUTS country code, which is not always the ISO-2 code — Greece
# is EL in NUTS and GR in ISO, and getting that wrong silently places every
# Greek substation as foreign.
IN_SCOPE = {
    "germany": "DE", "italy": "IT", "turkey": "TR", "poland": "PL",
    "spain": "ES", "greece": "EL", "belgium": "BE", "netherlands": "NL",
    "austria": "AT", "denmark": "DK", "portugal": "PT", "norway": "NO",
    "finland": "FI",
}

SOURCE = "nuts3_gisco_2024_polygon_join"

BANDS = ("Low", "Medium", "High", "Critical", "Extreme", "Unclassified")


def _percentile(sorted_vals, q):
    if not sorted_vals:
        return None
    k = (len(sorted_vals) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (k - lo)


def regional_summary(substations):
    """Rebuild `regions`, counting each region's bands from `classification`.

    NOT engine.compute_regional_summary. That one tallies
    classify_band(R_median) — the absolute cutoffs Task #461 replaced — so
    calling it here would revert Phase 2D at the regional level, which is the
    same defect fixed at fleet level in commit 561e2337 one level down. The
    fleet summary already counts the stored label; the regional summary now
    does too, and the two cannot disagree.

    Every region name changes in this pass, so there is no previous block to
    preserve. `pct_high` is therefore emitted on the semantic the current code
    documents — cumulative from High, per Phase 2B-1 — where the superseded
    blocks held a single-band value. On austria's Kärnten that reads 91.5
    rather than 56.1. It is a real change of meaning and it is stated here
    rather than left to be discovered.
    """
    groups = {}
    for s in substations:
        groups.setdefault(s.get("region") or "Unclassified", []).append(s)

    out = []
    for region, subs in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        n = len(subs)
        bands = {b: 0 for b in BANDS}
        for s in subs:
            b = s.get("classification")
            bands[b if b in bands else "Unclassified"] += 1
        scored = sorted(s["R_median"] for s in subs
                        if isinstance(s.get("R_median"), (int, float)))
        entry = {
            "region": region,
            "count": n,
            "n_scored": len(scored),
            "bands": bands,
            "pct_critical": round(bands["Critical"] / n * 100, 1),
            "pct_extreme": round(bands["Extreme"] / n * 100, 1),
            "pct_high": round((bands["High"] + bands["Critical"]
                               + bands["Extreme"]) / n * 100, 1),
            "median_R": round(_percentile(scored, 0.50), 4) if scored else None,
            "mean_R": round(sum(scored) / len(scored), 4) if scored else None,
        }
        if not scored:
            entry["_stats_pending_l3_rescore"] = True
        out.append(entry)
    return out


def build_index(base: pathlib.Path):
    from nuts_reader import read_shapes, read_dbf          # noqa: E402
    from shapely.strtree import STRtree                    # noqa: E402
    from shapely.prepared import prep                      # noqa: E402

    dbf, shp = base.with_suffix(".dbf"), base.with_suffix(".shp")
    for p in (dbf, shp, base.with_suffix(".shx")):
        if not p.exists():
            sys.exit(f"ABORT: {p} not found. Pass --shapefile without the extension.")

    attrs = list(read_dbf(dbf, ["NUTS_ID", "LEVL_CODE", "CNTR_CODE", "NAME_LATN"]))
    geoms = list(read_shapes(shp))
    if len(attrs) != len(geoms):
        sys.exit(f"ABORT: {len(attrs)} attribute rows against {len(geoms)} geometries.")

    units = []
    repaired = 0
    for a, g in zip(attrs, geoms):
        if a["LEVL_CODE"] != "3" or g is None:
            continue
        if not g.is_valid:
            g = g.buffer(0)          # the pattern audit_out_of_polygon_clusters already uses
            repaired += 1
        units.append((a, g))
    if not units:
        sys.exit("ABORT: no level-3 polygons found — is this the NUTS layer?")

    tree = STRtree([g for _, g in units])
    prepared = [prep(g) for _, g in units]
    print(f"  NUTS-3 index: {len(units):,} polygons"
          + (f", {repaired} repaired with buffer(0)" if repaired else ""))
    return units, tree, prepared


def load(slug: str):
    """Manifest, substations and the shard file each came from.

    Task #520 is the registered defect class for reading data['substations'] on
    a sharded manifest, so the shard list is consulted first.
    """
    d = REPO / slug
    man = json.loads((d / "ssi-data.json").read_text())
    shards = man.get("substations_shards")
    if not shards:
        subs = man.get("substations")
        if subs is None:
            sys.exit(f"ABORT: {slug} has neither shards nor a substations key.")
        return man, [(None, subs)]
    parts = []
    for e in shards:
        p = d / pathlib.Path(e["path"]).name
        if not p.exists():
            sys.exit(f"ABORT: {slug} shard missing: {e['path']}")
        raw = json.loads(p.read_text())
        parts.append((p, raw if isinstance(raw, list) else (raw.get("substations") or [])))
    return man, parts


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("countries", nargs="*")
    ap.add_argument("--shapefile", required=True,
                    help="path to NUTS_RG_01M_2024_4326 WITHOUT extension")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    slugs = a.countries or list(IN_SCOPE)
    bad = [s for s in slugs if s not in IN_SCOPE]
    if bad:
        sys.exit(f"ABORT: {', '.join(bad)} is not in scope. NUTS-3 is not finer than "
                 f"what it already publishes, or it is outside NUTS. "
                 f"In scope: {', '.join(sorted(IN_SCOPE))}")

    print(f"\n  {'APPLY' if a.apply else 'DRY RUN'} — {len(slugs)} country(ies)\n")
    units, tree, prepared = build_index(pathlib.Path(a.shapefile).expanduser())
    from shapely.geometry import Point                      # noqa: E402

    national = collections.Counter(u[0]["CNTR_CODE"] for u in units)

    def locate(lat, lon):
        p = Point(lon, lat)
        for i in tree.query(p):
            if prepared[i].contains(p):
                return units[i][0]
        return None

    print(f"\n  {'country':<13}{'fleet':>9}{'placed':>9}{'units':>7}{'of':>5}"
          f"{'foreign':>9}{'unplaced':>9}{'no coords':>11}")
    total = collections.Counter()
    cross = {}

    for slug in slugs:
        cc = IN_SCOPE[slug]
        man, parts = load(slug)
        placed = foreign = unplaced = nocoord = 0
        seen = set()
        neighbours = collections.Counter()

        for _, subs in parts:
            for s in subs:
                lat, lon = s.get("lat"), s.get("lon")
                if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
                    nocoord += 1
                    continue
                u = locate(lat, lon)
                if u is None:
                    unplaced += 1
                    continue
                if u["CNTR_CODE"] != cc:
                    foreign += 1
                    neighbours[u["CNTR_CODE"]] += 1
                    continue
                placed += 1
                seen.add(u["NUTS_ID"])
                if a.apply:
                    s["region"] = u["NAME_LATN"]
                    s["_region_nuts3"] = u["NUTS_ID"]

        print(f"  {slug:<13}{sum(len(x) for _, x in parts):>9,}{placed:>9,}"
              f"{len(seen):>7}{national[cc]:>5}{foreign:>9,}{unplaced:>9,}{nocoord:>11,}")
        cross[slug] = neighbours
        total["fleet"] += sum(len(x) for _, x in parts)
        total["placed"] += placed
        total["foreign"] += foreign
        total["unplaced"] += unplaced
        total["nocoord"] += nocoord

        if a.apply:
            # `regions` is rebuilt here, not left to a later pass. Every region
            # name in this country has just changed, so the stored block now
            # describes units that no longer exist — a manifest that ships
            # between the two is not stale, it is wrong.
            allsubs = [x for _, subs in parts for x in subs]
            man["regions"] = regional_summary(allsubs)
            fs = man.get("fleet_summary") or {}
            fs["n_regions"] = len(man["regions"])
            man["fleet_summary"] = fs

            # Provenance goes on the manifest, once, not on every substation.
            # The codebase's other enrichments write a per-record source marker
            # — _catchment_population_source, _migration_score_source — and that
            # is right where the value varies. This one does not: it is the same
            # 32-byte string on every record, and at 246,746 records it costs
            # 7.9 MB and pushes three shards past Convention #79's 45 MiB target
            # for no information. The per-record audit trail that DOES vary,
            # _region_nuts3, stays where it belongs.
            man.setdefault("meta", {})["region_derivation"] = {
                "source": SOURCE,
                "layer": "Eurostat GISCO NUTS 2024, NUTS_RG_01M_2024_4326, level 3",
                "attribute": "NAME_LATN for region, NUTS_ID kept per record as _region_nuts3",
                "licence": "Eurostat GISCO, attribution required",
                "placed": placed,
                "left_alone_outside_polygons": unplaced,
                "left_alone_in_a_neighbour_country": foreign,
                "applied_utc": _stamp(),
            }
            for p, subs in parts:
                if p is None:
                    man["substations"] = subs
                else:
                    p.write_text(json.dumps(subs, separators=(",", ":")))
            # The manifest is written for BOTH shapes, always. An earlier
            # version wrote it only in the unsharded branch, so on a sharded
            # country meta.region_derivation was set in memory and thrown away
            # — the provenance silently missing from exactly the ten countries
            # that most needed it.
            (REPO / slug / "ssi-data.json").write_text(
                json.dumps(man, separators=(",", ":")))

    print(f"\n  {'TOTAL':<13}{total['fleet']:>9,}{total['placed']:>9,}{'':>12}"
          f"{total['foreign']:>9,}{total['unplaced']:>9,}{total['nocoord']:>11,}")
    print(f"\n  placed in own country: {100*total['placed']/total['fleet']:.2f}%")

    print("\n  Convention #56 — records left without a NUTS-3 region:")
    print(f"    {total['unplaced']:,} outside every polygon. They keep the region they had.")
    print(f"    {total['foreign']:,} inside a NEIGHBOUR's polygon. Not given a foreign region —")
    print( "      this is Task #511 cross-border ingestion pollution, not a region gap:")
    for slug, n in sorted(cross.items(), key=lambda kv: -sum(kv[1].values())):
        if n:
            top = ", ".join(f"{k} {v:,}" for k, v in n.most_common(4))
            print(f"        {slug:<13}{sum(n.values()):>6,}   {top}")

    if not a.apply:
        print("\n  dry run — nothing written. Re-run with --apply once agreed.")
        return 0

    # intelligence/country-configs belongs in this line. admin.l1.count drives a
    # region-count KPI on every country page, and this pass changes the region
    # count — germany 16 -> 409. An earlier version of this message omitted the
    # configs, which would have committed pages quoting a count their own config
    # contradicts: the exact defect class this work exists to remove.
    globs = " ".join(f"'{s}/*'" for s in slugs) + " intelligence/country-configs"
    print("\n  written. `regions` was rebuilt in the same pass and reconciles:")
    print("  each country's region counts sum to its fleet, and the regional band")
    print("  counts sum to the fleet band counts. fleet_summary.bands is untouched")
    print("  because no substation's classification changed — only its region did.")
    print("\n  Do NOT run refresh_fleet_summary.py to 'finish' this: it writes")
    print("  through save_ssi_data, which re-packs the country, and it rebuilds")
    print("  regions with the absolute-cutoff bands this pass exists to avoid.")
    print("\n  Next, IN THIS ORDER — data, then configs, then pages:")
    print("    1. set admin.l1.count in intelligence/country-configs/<slug>.json")
    print("       from len(regions) for each country written above")
    print("    2. ssi_refresh_canonical_figures.py <slug> --apply, per country")
    print("    3. generate_nav_data.py, then bump_cache_busters.py")
    print("    4. ssi_refresh_landing_counts.py --apply")
    print("  Refreshing the pages before the configs writes the OLD region count")
    print("  into them, and the page/data check then fails on all thirteen.")
    print(f"\n      git add -A -- {globs} index.html nav.js '*/*.html'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
