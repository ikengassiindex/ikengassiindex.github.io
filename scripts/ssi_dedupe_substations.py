#!/usr/bin/env python3
"""
SSI substation deduplication — DRY RUN BY DEFAULT.

Run from the repo root of ikengassiindex.github.io:

    python3 ssi_dedupe_substations.py japan              # dry run, reports only
    python3 ssi_dedupe_substations.py japan --apply      # writes
    python3 ssi_dedupe_substations.py --all              # dry run, whole cohort

Nothing is written unless --apply is passed.

ONE RULE, ONE IMPLEMENTATION
----------------------------
The classification is imported from ssi_duplicate_census.py, which must sit
beside this file. The census decides what a duplicate is and which record
survives; this utility only carries that decision out. Two copies of the rule
would be free to drift, and the census is the audited one.

WHAT IT DOES
------------
For every A / B / C / D1 group in a country:

  1. MERGE ADJACENCY FIRST. grid-geo.json holds no substation reference on its
     line records — `l` is geometry, and connectivity lives in `a`, a map of
     substation_id -> [line indices]. So a removed substation strands its
     edges unless they are unioned onto the keeper first. This is the additive
     counterpart to Discipline #36's rule that lines to filtered-out
     substations are kept. Cohort-wide only 77 line-links are affected, but
     losing one silently would be a topology error nothing downstream reports.

  2. Drop the redundant substations from ssi-data.json and from grid-geo's `s`.

  3. Recompute fleet_summary and regions from what remains.

  D2 groups are never touched — 207 coordinates cohort-wide carry two or more
  genuinely different voltages (france 20 kV with 400 kV, 175 sites in the
  US). Transmission and distribution at one point is real infrastructure.

INDEPENDENT VERIFICATION, BUILT IN
-----------------------------------
grid-geo.json already holds the deduplicated fleet — it was built by a
different code path that did not carry the duplicates through. Its substation
count matches the census's post-dedupe figure exactly on japan (6,168),
australia (12,059) and spain (12,438), within 11 on germany and 2 on france.

So this utility has an oracle. After computing the survivors it compares the
count against grid-geo and prints the delta. A large disagreement means the
rule misfired on that country and the run should not be applied.

WHAT IT DELIBERATELY DOES NOT DO
---------------------------------
Duplicate LINE geometries — 298,660 cohort-wide, 11.2% — are left alone.
Adjacency references lines by INDEX into `l`, so removing line records
renumbers every entry in `a`. That is a separate, riskier operation and
belongs in its own step with its own verification.

Scores are not recomputed. Removing a duplicate does not change any surviving
substation's R_median; it changes the fleet aggregates, which are recomputed,
and the per-country P5/P95 band anchors, which are NOT — those are Phase 2D
territory and interact with the classification split. Run
normalise_bands_per_country.py afterwards, deliberately, as its own decision.

PRESERVING PROVENANCE THROUGH THE REBUILD
-----------------------------------------
fleet_summary and regions are recomputed from the survivors, but production's
compute_fleet_summary(substations) takes no `previous=` argument — M-065 added
one, and M-065 lives in v4.24, which is parked. Rebuilding naively therefore
DESTROYS every underscore-prefixed provenance key, `_band_normalisation` above
all. Japan is one of only three countries that still carries it.

So this utility captures the underscore-prefixed keys before the rebuild and
restores them afterwards. It does not depend on M-065 landing.

AUDIT TRAIL
-----------
--apply writes ~/ssi-audit-trail/ssi_dedupe_audit_<slug>_<UTC>.json
(override with SSI_AUDIT_DIR or --audit-dir; kept out of the repo because
git already versions ssi-data.json, which is the authoritative record)
recording every group: the
keeper, the removed ids, the adjacency merged onto the keeper, and the
R_median values discarded. Convention #56 — the removal is reversible from
the audit file plus git history, and visible rather than silent.
"""
from __future__ import annotations

import argparse
import datetime
import importlib.util
import math
import json
import os
import sys
from pathlib import Path

REPO = Path.cwd()
HERE = Path(__file__).resolve().parent


def _load_census():
    """Import the census module that sits beside this file — one rule, one copy."""
    p = HERE / "ssi_duplicate_census.py"
    if not p.exists():
        sys.exit(f"ABORT: {p} not found. The classification rule lives in the "
                 f"census; this utility only carries out its decision.")
    spec = importlib.util.spec_from_file_location("ssi_duplicate_census", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.REPO = REPO                      # census resolves paths from cwd
    return mod


def load_ssi(slug: str):
    """Return (root, [(path, substations, kind)]) — kind in flat|wrapped|shard.

    The `wrapped` case must write the ROOT back, not the substation list.
    Getting this wrong destroys meta, fleet_summary and regions.
    """
    p = REPO / slug / "ssi-data.json"
    d = json.loads(p.read_text())
    if isinstance(d, list):
        return {"substations": d}, [(p, d, "flat")]
    if d.get("substations_shards"):
        parts = []
        for e in d["substations_shards"]:
            rel = e["path"] if isinstance(e, dict) else e
            sp = p.parent / Path(rel).name
            if not sp.exists():
                continue
            q = json.loads(sp.read_text())
            subs = q if isinstance(q, list) else (q.get("substations") or [])
            parts.append((sp, subs, "shard"))
        return d, parts
    return d, [(p, d.get("substations") or [], "wrapped")]


def _same_facility(a, b, metres=50.0):
    """Do two records under one substation_id describe one facility?

    Same name, same voltage, and close enough that the difference is
    coordinate jitter from separate ingestion runs rather than two sites.

    Wodonga Terminal Station appears twice in australia 8 m apart with an
    identical name, voltage and R_median — a real duplicate that fails a byte
    comparison only in the fifth decimal of its coordinates. It must collapse.
    Buronga substation (330 kV) and Buronga Switching Station (220 kV) share
    an id 218 m apart. It must not.
    """
    if (a.get("name") or "") != (b.get("name") or ""):
        return False
    if a.get("voltage_kv") != b.get("voltage_kv"):
        return False
    try:
        lat1, lon1 = float(a["lat"]), float(a["lon"])
        lat2, lon2 = float(b["lat"]), float(b["lon"])
    except (KeyError, TypeError, ValueError):
        return False           # no coordinates to compare: do not assume
    dy = (lat1 - lat2) * 111_320.0
    dx = (lon1 - lon2) * 111_320.0 * math.cos(math.radians(lat1))
    return math.hypot(dx, dy) <= metres


def _assert_ids_are_not_collisions(slug, substations):
    """Refuse to collapse a repeated id that covers two different facilities.

    write_country discards any id it has already seen, keeping whichever
    record came first in file order. That is correct for a substation stored
    twice and catastrophic for an id collision: it deletes a real asset and
    reports it as a duplicate removed. The grid-geo delta moves by one, well
    inside tolerance, so nothing downstream notices.

    Aborting is the right response rather than skipping the group. Every join
    in the pipeline keys on substation_id; a country whose ids are not unique
    is not ready to be deduplicated.
    """
    # An absent id is its own case. turkey carries 30 unscored ingestion stubs
    # with no substation_id — an osm_id, coordinates, no R_median, published
    # as "Unclassified" per Convention #56. They share the key None, so the
    # collapse would keep one and delete 29 real records. They are not
    # duplicates of each other and the remedy is ids, not deduplication.
    missing = [x for x in substations
               if x.get("substation_id") in (None, "", "null")]
    if missing:
        print(f"\n  ABORT: {slug} has {len(missing)} substation(s) with no "
              f"substation_id.\n")
        for x in missing[:8]:
            print(f"       {str(x.get('name')):<32} {x.get('voltage_kv')} kV"
                  f"   ({x.get('lat')}, {x.get('lon')})"
                  f"   osm={x.get('osm_id')}   R={x.get('R_median')}")
        if len(missing) > 8:
            print(f"       ... and {len(missing) - 8} more")
        print()
        print("  These share the key None, so the collapse would keep one and")
        print(f"  delete the other {len(missing) - 1}. They are not duplicates")
        print("  of each other — they are separate places that never received")
        print("  an id. Give them ids, then re-run. Nothing has been written.")
        sys.exit(3)

    groups = {}
    for sub in substations:
        groups.setdefault(str(sub.get("substation_id")), []).append(sub)

    collisions = []
    for sid, g in groups.items():
        if len(g) < 2:
            continue
        if not all(_same_facility(g[0], other) for other in g[1:]):
            collisions.append((sid, g))

    if not collisions:
        return

    print(f"\n  ABORT: {slug} has {len(collisions)} substation_id "
          f"collision(s) — one id, more than one facility.\n")
    for sid, g in collisions:
        print(f"    {sid}")
        for x in g:
            print(f"       {str(x.get('name')):<38} {x.get('voltage_kv')} kV"
                  f"   ({x.get('lat')}, {x.get('lon')})   R={x.get('R_median')}")
        print()
    print("  These are not duplicates. The collapse keeps whichever record")
    print("  comes first in file order and deletes the rest, so running this")
    print("  would remove a real substation and count it as a duplicate.")
    print()
    print("  Give the second facility an id of its own, then re-run. Nothing")
    print("  has been written.")
    sys.exit(3)


def write_country(slug, root, parts, survivors, drop, merges):
    """Write survivors back, rebuild aggregates, update grid-geo adjacency.

    Storage shape is preserved exactly. The `wrapped` case must write the
    ROOT — writing the substation list over ssi-data.json destroys meta,
    fleet_summary and regions, which is a mistake this codebase has made
    before.
    """
    _assert_ids_are_not_collisions(
        slug, [x for _, subs_, _ in parts for x in subs_])

    sys.path.insert(0, str(REPO / "scripts"))
    sys.path.insert(0, str(REPO))
    from pipeline.scoring.engine import compute_regional_summary
    # NOT engine.compute_fleet_summary. That one recounts bands with
    # classify_band(R_median) — the absolute cutoffs Task #461 replaced — so
    # calling it here reverts Phase 2D for the published figure while every
    # substation keeps its normalised `classification`. The map then colours
    # from one and the page header quotes the other. It did exactly that to
    # us, germany, sweden and japan. refresh_fleet_summary already holds the
    # correct routine; import it rather than restate it, so the two cannot
    # drift apart.
    from scripts.refresh_fleet_summary import (
        _recompute_fleet_summary_task_461_aware as compute_fleet_summary)

    # Pre-remediation snapshot, in the name scripts/refresh_country_counts.py
    # already looks for. That script derives the page-text "before" figure by
    # recounting voltage tiers from the pre file, so a stub will not do — it
    # needs the real thing. *.pre-*.backup is gitignored, so this is local
    # working state and never reaches a commit.
    #
    # Without it the dedupe leaves every country page displaying its old count:
    # japan's index.html carried the hardcoded "7,073" three times while the
    # data said 6,168.
    stamp_b = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    src = REPO / slug / "ssi-data.json"
    (REPO / slug / f"ssi-data.json.pre-remediate-dedupe-{stamp_b}.backup").write_bytes(
        src.read_bytes())

    # ── aggregates, with provenance carried across the rebuild ──
    old_fs = root.get("fleet_summary") or {}
    preserved = {k: v for k, v in old_fs.items() if k.startswith("_")}
    fs = compute_fleet_summary(survivors)
    # Preserved keys FILL GAPS; they never overwrite what the rebuild computed.
    # The old order let a stale `_bands_source` survive on top of freshly
    # rebuilt counts, which is how germany's manifest came to stamp
    # "task_461_per_country_normalised" over bands that were not normalised.
    # An untrue provenance claim is worse than an absent one.
    fs = {**preserved, **fs}
    root["fleet_summary"] = fs

    regions = compute_regional_summary(survivors)
    root["regions"] = list(regions.values()) if isinstance(regions, dict) else regions

    root.setdefault("meta", {}).setdefault("dedupe_runs", []).append({
        "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "removed": len(drop),
        "rule": "ssi_duplicate_census A/B/C/D1, D2 preserved",
    })

    # ── substations, in whatever shape they were stored ──
    kinds = {k for _, _, k in parts}
    if kinds == {"flat"}:
        parts[0][0].write_text(json.dumps(survivors, separators=(",", ":")))
    elif kinds == {"wrapped"}:
        root["substations"] = survivors
        parts[0][0].write_text(json.dumps(root, separators=(",", ":")))
    else:
        by_id = {str(s.get("substation_id")): s for s in survivors}
        used, manifest = set(), []
        for path, subs, _ in parts:
            keep = []
            for sub in subs:
                sid = str(sub.get("substation_id"))
                if sid in by_id and sid not in used:
                    used.add(sid); keep.append(sub)
            path.write_text(json.dumps(keep, separators=(",", ":")))
            manifest.append({"path": path.name, "count": len(keep)})
        root["substations_shards"] = manifest
        root.pop("substations", None)
        (REPO / slug / "ssi-data.json").write_text(json.dumps(root, separators=(",", ":")))

    # ── grid-geo: merge adjacency BEFORE dropping, never after ──
    gp = REPO / slug / "grid-geo.json"
    if gp.exists():
        g = json.loads(gp.read_text())
        for keeper_id, edges in merges.items():
            if keeper_id in (g.get("a") or {}) or edges:
                g.setdefault("a", {})[keeper_id] = edges
        # Re-key, do not delete. grid-geo sometimes kept a DIFFERENT member of
        # a group than the census keeper — the "keeper choice" residual in
        # --reconcile. Popping the dropped id then leaves the site with no
        # grid-geo entry at all, because the survivor was never in there.
        # Japan's pilot lost 2 substations from the map exactly this way.
        for sid, keeper_id in drop.items():
            for key in ("s", "a"):
                node = g.get(key) or {}
                if sid not in node:
                    continue
                if keeper_id in node:
                    node.pop(sid)                    # survivor already present
                else:
                    node[keeper_id] = node.pop(sid)  # carry the site across
        gp.write_text(json.dumps(g, separators=(",", ":")))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("countries", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--apply", action="store_true", help="write (default: dry run)")
    ap.add_argument("--audit-dir", metavar="PATH",
                    help="where the audit sidecar goes (default: $SSI_AUDIT_DIR, else ~/ssi-audit-trail)")
    args = ap.parse_args()

    if not (REPO / "intelligence" / "countries.json").exists():
        sys.exit("ABORT: run from the ikengassiindex.github.io repo root.")

    census = _load_census()
    slugs = census.cohort_slugs() if args.all else args.countries
    if not slugs:
        sys.exit("ABORT: name a country, or pass --all.")

    mode = "APPLY" if args.apply else "DRY RUN"
    print(f"SSI substation deduplication — {mode}\n")
    print(f"{'country':<13}{'before':>9}{'remove':>8}{'after':>9}"
          f"{'grid-geo':>10}{'delta':>7}{'edges':>7}")
    print("-" * 63)

    for slug in slugs:
        r = census.classify(slug)
        if not r["substations"]:
            continue

        adj, _ = census.load_grid_geo(slug)
        drop, merges = {}, {}

        for cls in ("A", "B", "C", "D1"):
            for g in r[cls]:
                keep = g["keeper"]
                others = [i for i in set(g["ids"]) if i != keep]
                if not others:
                    continue          # class A: one id stored twice
                for i in others:
                    drop[i] = keep
                edges = sorted({e for i in others for e in adj.get(i, [])}
                               | set(adj.get(keep, [])),
                               key=lambda v: (isinstance(v, str), v))
                if edges != sorted(adj.get(keep, []),
                                   key=lambda v: (isinstance(v, str), v)):
                    merges[keep] = edges

        root, parts = load_ssi(slug)
        before = sum(len(s) for _, s, _ in parts)

        # Before the row is printed, not after it is agreed. This used to be
        # reached only from write_country, which runs under --apply, so a dry
        # run would print `turkey 30` and the refusal came later. A dry run is
        # the step where numbers are agreed; it has to be the step that
        # refuses.
        _assert_ids_are_not_collisions(slug, [x for _, s_, _ in parts for x in s_])

        # Class A repeats one id, so removing "the other" ids is not enough —
        # collapse any id appearing more than once down to a single record.
        kept_ids, survivors = set(), []
        for _, subs, _ in parts:
            for s in subs:
                sid = str(s.get("substation_id"))
                if sid in drop or sid in kept_ids:
                    continue
                kept_ids.add(sid)
                survivors.append(s)

        after = len(survivors)
        gg = len(json.loads((REPO / slug / "grid-geo.json").read_text()).get("s") or {}) \
            if (REPO / slug / "grid-geo.json").exists() else 0
        delta = gg - after if gg else 0

        flag = "" if abs(delta) <= max(15, after * 0.005) else "   <-- CHECK"
        print(f"{slug:<13}{before:>9,}{before - after:>8,}{after:>9,}"
              f"{gg:>10,}{delta:>7,}{len(merges):>7,}{flag}")

        if args.apply:
            stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            discarded = {}
            for _, subs, _ in parts:
                for sub in subs:
                    sid = str(sub.get("substation_id"))
                    if sid in drop:
                        discarded[sid] = sub.get("R_median")

            write_country(slug, root, parts, survivors, drop, merges)

            audit = {
                "slug": slug, "generated_utc": stamp,
                "rule": "ssi_duplicate_census.classify A/B/C/D1; D2 preserved",
                "before": before, "after": after, "removed": before - after,
                "grid_geo_count": gg, "grid_geo_delta": delta,
                "adjacency_merges": merges,
                "removed_id_to_keeper": drop,
                "discarded_R_median": discarded,
            }
            # Outside the repo. git already holds the authoritative record —
            # ssi-data.json is versioned, so the removed set is recoverable by
            # diffing the commit whatever this file says. The sidecar is the
            # convenience copy, and the wrong thing to commit at scale: the
            # per-id mappings for germany and us run to megabytes against a
            # repo already sharding data files at 60 MB.
            adir = (Path(args.audit_dir) if args.audit_dir
                    else Path(os.environ.get("SSI_AUDIT_DIR")
                              or (Path.home() / "ssi-audit-trail")))
            adir.mkdir(parents=True, exist_ok=True)
            out = adir / f"ssi_dedupe_audit_{slug}_{stamp}.json"
            out.write_text(json.dumps(audit, indent=1))
            print(f"              written; audit -> {out}")

    if not args.apply:
        print("\n  dry run — nothing written. Add --apply once the numbers are agreed.")
    print("  D2 co-locations preserved. Duplicate line geometries untouched (separate step).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
