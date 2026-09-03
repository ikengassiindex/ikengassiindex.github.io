#!/usr/bin/env python3
"""
Rebuild the ERA5 fetch plan on the axis that is actually free: AREA.

    python3 scripts/build_era5_merged_plan.py --plan <old.json> --boxes 4 \
        --variables snow_depth_water_equivalent --statistic daily_maximum \
        --out <new.json>

WHAT WAS MEASURED, AND WHERE
    probe_era5_cost_frontier.py     cost = 365.0 for every box from New Zealand
                                    to Canada, limit 400.0
    probe_era5_area_sensitivity.py  cost = 365.0 for a GLOBAL box, 2469x the
                                    area of Denmark. Still 365.0.

    So the CDS prices FIELDS, not bytes: cost = variables x days. Both terms
    are fixed by the metric definitions — I1 needs a whole year to take an
    annual maximum, and a variable is a variable. Variables and years are
    precisely the two axes that cannot move, and they are the only two axes
    the three previous fetch redesigns ever touched.

    Area never enters the cost. It does enter the BYTES, at a near-constant
    0.0659 MB/deg^2 measured across the twelve boxes the stalled run produced
    (2 to 2370 deg^2, a factor of 1000, rates 0.054 to 0.084).

    Merging boxes therefore trades disk against queue, and the queue is what
    is scarce at 5.74 requests/day.

HOW THE MERGE IS CHOSEN
    Greedy agglomerative: repeatedly merge the pair of groups whose bounding
    box adds the least area. Bounding boxes only — no reprojection, no
    clustering heuristic with a tuning parameter. Boxes crossing the
    antimeridian are NOT merged across it; that trap cost the estate a
    rebuild once already.

CONVENTION #56
    The plan records the measurement it was built from, so a reader can see
    the byte estimate is an extrapolation from twelve files and not a fact.
"""
from __future__ import annotations
import argparse, itertools, json, pathlib, sys
from datetime import datetime, timezone

MB_PER_DEG2 = 0.0659          # measured; see docstring
MEASURED_N = 12


def area(bb):
    return (bb[0] - bb[2]) * (bb[3] - bb[1])


def bbox(group):
    return (max(b["north"] for b in group), min(b["west"] for b in group),
            min(b["south"] for b in group), max(b["east"] for b in group))


def crosses_antimeridian(group):
    return any(b["west"] > b["east"] for b in group)


def merge_to(boxes, k):
    groups = [[b] for b in boxes]
    while len(groups) > k:
        best = None
        for i, j in itertools.combinations(range(len(groups)), 2):
            cand = groups[i] + groups[j]
            if crosses_antimeridian(cand):
                continue           # never merge across the antimeridian
            d = area(bbox(cand)) - area(bbox(groups[i])) - area(bbox(groups[j]))
            if best is None or d < best[0]:
                best = (d, i, j)
        if best is None:
            print(f"  cannot merge below {len(groups)} without crossing the "
                  f"antimeridian; stopping there")
            break
        _, i, j = best
        merged = groups[i] + groups[j]
        groups = [g for n, g in enumerate(groups) if n not in (i, j)] + [merged]
    return groups


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--boxes", type=int, required=True)
    ap.add_argument("--variables", nargs="+", required=True)
    ap.add_argument("--statistic", required=True)
    ap.add_argument("--tag", required=True)
    a = ap.parse_args()

    old = json.loads(pathlib.Path(a.plan).read_text())
    flat, members = [], []
    for slug, bs in old["boxes"].items():
        for b in bs:
            flat.append(b)
            members.append(slug)
    # label by slug:box_index, never by slug alone. A country can have several
    # boxes (overseas territories), and naming only the country would tell a
    # reader that France comes from an Indian Ocean box.
    seen = {}
    labels = []
    for m in members:
        seen[m] = seen.get(m, -1) + 1
        labels.append(f"{m}:b{seen[m]}")
    idx = {id(b): l for b, l in zip(flat, labels)}

    groups = merge_to(flat, a.boxes)
    years = [str(y) for y in old["years"]]

    regions, tot = [], 0.0
    for n, g in enumerate(sorted(groups, key=lambda g: -area(bbox(g)))):
        bb = bbox(g)
        tot += area(bb)
        regions.append({
            "id": f"r{n}",
            "north": round(bb[0], 2), "west": round(bb[1], 2),
            "south": round(bb[2], 2), "east": round(bb[3], 2),
            "deg2": round(area(bb), 1),
            "est_mb_per_variable_year": round(area(bb) * MB_PER_DEG2, 1),
            "covers_boxes": sorted(idx[id(b)] for b in g),
            "covers_countries": sorted({idx[id(b)].split(":")[0] for b in g})})

    nreq = len(regions) * len(years) * len(a.variables)
    gb = tot * MB_PER_DEG2 * len(years) * len(a.variables) / 1000

    plan = {
        "dataset": old["dataset"],
        "years": old["years"],
        "tag": a.tag,
        "statistic": a.statistic,
        "variables": a.variables,
        "regions": regions,
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "built_from": pathlib.Path(a.plan).name,
        "n_requests": nreq,
        "est_total_gb": round(gb, 1),
        "basis": {
            "cost_rule": "cost = variables x days; area does not enter. "
                         "Measured by probe_era5_cost_frontier.py and "
                         "probe_era5_area_sensitivity.py — a global box prices "
                         "365.0 against a limit of 400.0, identical to Denmark.",
            "mb_per_deg2": MB_PER_DEG2,
            "mb_per_deg2_basis": f"extrapolated from {MEASURED_N} files of the "
                                 f"stalled run, 2 to 2370 deg^2, observed rates "
                                 f"0.054 to 0.084 MB/deg^2. AN EXTRAPOLATION, "
                                 f"NOT A MEASUREMENT OF THE MERGED BOXES.",
            "measured_throughput_per_day": 5.74},
    }
    pathlib.Path(a.out).write_text(json.dumps(plan, indent=2))

    print(f"\n  merged plan — {a.tag}: {a.statistic}, {a.variables}")
    print(f"  {len(flat)} boxes -> {len(regions)} regions\n")
    print(f"  {'region':<8}{'deg^2':>10}{'MB/var-yr':>12}  covers")
    for r in regions:
        c = ", ".join(r["covers_boxes"][:4]) + (f" +{len(r['covers_boxes'])-4} more"
                                               if len(r["covers_boxes"]) > 4 else "")
        print(f"  {r['id']:<8}{r['deg2']:>10.0f}{r['est_mb_per_variable_year']:>12.0f}  {c}")
    print(f"\n  requests {nreq}   est {gb:.1f} GB   "
          f"~{nreq/5.74:.1f} days at the measured 5.74/day")
    print(f"  (was {len(flat)*len(old['years'])*sum(len(s['variables']) for s in old['request_sets'])} requests / 360 days)")
    print(f"\n  written: {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
