#!/usr/bin/env python3
"""
Recover Turkey's real substation names and voltages from OSM.

    python3 scripts/recover_turkey_from_osm.py --osm <file> --dry-run
    python3 scripts/recover_turkey_from_osm.py --osm <file>

WHAT IS BROKEN
--------------
2,445 of turkey's 4,031 records (60.7%) store the name
`"Substation " + substation_id` — a string deterministic from the id, carrying
no information, shaped exactly like data. The same ingestion gap left 2,162
voltages at score-country.py's hardcoded fallback of 66 kV.

Every other clean country is at 0.0% placeholder names. This closes that gap
from the source rather than by deletion.

MATCHING, AND WHY IT IS TRUSTWORTHY
-----------------------------------
Only 30 of 4,031 records carry an osm_id, so matching is by coordinate.
That is an inference, so it was validated against ground truth BEFORE being
used to write anything.

1,556 register records already hold a real name. Of those, 1,545 have a
name-identical OSM object, and the coordinates agree to
    median 8 m · p90 20 m · p95 34 m · p99 71 m.

Matching those records by NEAREST COORDINATE ALONE, ignoring names, and then
asking whether the recovered name is the right one:

    threshold  50 m   96.4% correct
    threshold 150 m   98.8% correct   <- chosen, plateaus here
    threshold 500 m   98.8% correct

All 17 apparent mismatches were inspected by hand and 16 are the same
substation under a different string — "Havsa TM" against "Havsa Trafo
Merkezi", "Kazan TM" against "TEİAŞ Kazan Trafo Merkezi". In one case OSM is
more correct than the register, which holds the typo
"Edirne 154 jV (GIS)" for "154 kV". One case, "Denizli OSB TM" against
"Denizli4 TM" at 76 m, is genuinely uncertain. True accuracy is ~99.9%.

VOLTAGE
-------
OSM voltage tags are multi-valued: "154000;34500" is a 154/34.5 kV substation.
The value taken is the MAXIMUM, because a substation's class is its highest
level and max is order-independent — a differently ordered tag cannot flip it.
On the 714 records where a matched OSM tag agrees with the register, first and
max are identical, so this choice is not contradicted by the existing data.

WHAT IT WILL NOT DO
-------------------
- Never overwrites a genuinely sourced value. A real name stays; a voltage not
  marked as a fallback stays.
- Refuses an ambiguous match: two candidates whose distances differ by less
  than AMBIGUITY_M and which disagree on what they would write.
- A record OSM has no name for gets `name: null`, not a placeholder. 25,624
  records cohort-wide already carry a null name; that is the convention, and a
  null is honest where a deterministic string is not.
"""
from __future__ import annotations
import argparse, collections, json, math, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MATCH_M = 150.0          # validated above; accuracy plateaus here
AMBIGUITY_M = 20.0       # two candidates closer than this apart = ambiguous
GRID = 0.02              # ~2 km spatial buckets


def km(a, b, c, d):
    dy = (c - a) * 111.32
    dx = (d - b) * 111.32 * math.cos(math.radians((a + c) / 2))
    return math.hypot(dx, dy)


def parse_voltage(raw):
    """Highest level in a possibly multi-valued OSM voltage tag, in kV."""
    if raw is None:
        return None
    vals = []
    for part in str(raw).replace(",", ";").split(";"):
        part = part.strip()
        if part.isdigit():
            vals.append(int(part))
    if not vals:
        return None
    v = max(vals) / 1000.0
    if v <= 0 or v > 1200:          # 1200 kV is above any real line
        return None
    return round(v, 3)


def load_osm(path):
    pts = []
    for x in json.loads(pathlib.Path(path).read_text())["elements"]:
        t = x.get("tags") or {}
        lat = x.get("lat") if x.get("lat") is not None else (x.get("center") or {}).get("lat")
        lon = x.get("lon") if x.get("lon") is not None else (x.get("center") or {}).get("lon")
        if lat is None or lon is None:
            continue
        pts.append({"osm_id": x["id"], "osm_type": x["type"], "lat": lat, "lon": lon,
                    "name": (t.get("name") or "").strip() or None,
                    "kv": parse_voltage(t.get("voltage"))})
    return pts


def index(pts):
    idx = collections.defaultdict(list)
    for p in pts:
        idx[(int(p["lat"] / GRID), int(p["lon"] / GRID))].append(p)
    return idx


def candidates(idx, lat, lon, radius_m):
    c = (int(lat / GRID), int(lon / GRID))
    out = []
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            for p in idx.get((c[0] + i, c[1] + j), ()):
                d = km(lat, lon, p["lat"], p["lon"]) * 1000.0
                if d <= radius_m:
                    out.append((d, p))
    return sorted(out, key=lambda t: t[0])


def is_placeholder(s):
    sid = s.get("substation_id")
    return sid is not None and (s.get("name") or "").strip() == f"Substation {sid}"


def recover(subs, idx):
    """Returns (report, changes). Mutates nothing until caller applies."""
    rep = collections.Counter()
    plan = []
    for i, s in enumerate(subs):
        lat, lon = s.get("lat"), s.get("lon")
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            rep["no_coordinates"] += 1
            continue
        cands = candidates(idx, lat, lon, MATCH_M)
        if not cands:
            rep["no_osm_within_150m"] += 1
            continue

        want_name = is_placeholder(s)
        src = s.get("_voltage_kv_source")
        want_kv = src in ("default_no_identity", "unverified_66", "absent")

        # Ambiguity is only a problem when rival candidates DISAGREE about what
        # they would write. Two identical neighbours are not ambiguous.
        rivals = [p for d, p in cands if d - cands[0][0] < AMBIGUITY_M]
        if len(rivals) > 1:
            names = {p["name"] for p in rivals if p["name"]}
            kvs = {p["kv"] for p in rivals if p["kv"] is not None}
            if (want_name and len(names) > 1) or (want_kv and len(kvs) > 1):
                rep["ambiguous_refused"] += 1
                continue

        best = cands[0][1]
        ch = {"i": i, "dist_m": round(cands[0][0], 1),
              "osm_id": best["osm_id"], "osm_type": best["osm_type"]}
        if want_name:
            ch["name"] = best["name"]            # may be None — that is the point
            rep["name_recovered" if best["name"] else "name_nulled_no_osm_name"] += 1
        if want_kv and best["kv"] is not None:
            ch["voltage_kv"] = best["kv"]
            rep["voltage_recovered"] += 1
        elif want_kv:
            rep["voltage_no_osm_tag"] += 1
        if len(ch) > 4:
            plan.append(ch)
        else:
            rep["matched_nothing_to_write"] += 1
    return rep, plan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--osm", required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    manp = ROOT / "turkey" / "ssi-data.json"
    man = json.loads(manp.read_text())
    subs = man["substations"]
    pts = load_osm(a.osm)
    print(f"\n  OSM objects: {len(pts):,}   register records: {len(subs):,}")
    rep, plan = recover(subs, index(pts))
    print(f"\n  {'outcome':32}{'records':>9}")
    for k, v in rep.most_common():
        print(f"    {k:32}{v:>9,}")
    print(f"    {'writes planned':32}{len(plan):>9,}")

    if a.dry_run:
        print("\n  DRY RUN — nothing written\n")
        return 0

    for ch in plan:
        s = subs[ch["i"]]
        if "name" in ch:
            s["name"] = ch["name"]
            s["_name_source"] = "osm" if ch["name"] else "osm_untagged"
        if "voltage_kv" in ch:
            s["voltage_kv"] = ch["voltage_kv"]
            s["_voltage_kv_source"] = "osm_tag"
        s["_osm_match"] = {"osm_id": ch["osm_id"], "osm_type": ch["osm_type"],
                           "distance_m": ch["dist_m"]}
    man.setdefault("meta", {})["osm_recovery"] = {
        "at_utc": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc).isoformat(),
        "match_radius_m": MATCH_M, "ambiguity_m": AMBIGUITY_M,
        "validated": "98.8% correct on 1,556 already-named records matched by "
                     "coordinate alone; 16 of 17 apparent misses are naming "
                     "variants of the same substation",
        "counts": dict(rep)}
    manp.write_text(json.dumps(man))
    print(f"\n  written — {len(plan):,} records updated\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
