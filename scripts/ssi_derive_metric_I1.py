#!/usr/bin/env python3
"""
Derive I1 — snow load — from the merged-region ERA5-Land fetch.

    python3 scripts/ssi_derive_metric_I1.py --plan <merged.json> --raw-only --all
    python3 scripts/ssi_derive_metric_I1.py --plan <merged.json> --all      (needs ANCHOR)

DEFINITION, pinned under Bible s8 on 31 August 2026
    I1_raw(s) = mean over years of the ANNUAL MAXIMUM snow water equivalent at
                the substation's grid cell, in metres SWE.

    A load, not a frequency. R6e_winter already carries winter frequency
    (0.55 x ERA5_tmin_p1_freq + 0.25 x snow_days + 0.20 x ice_storm_proxy); an
    I1 built on cold-day counts would put one signal into the index twice.
    ISO 12494 and IEC 60826 treat ice and snow as design LOADS with return
    periods, which is the basis for taking the load and leaving frequency to R6e.

DECLARED GAP
    Glaze and freezing rain need precipitation phase, which this fetch does not
    carry. I1 is a snow-load metric with an ice-load gap, and its limitation
    says so on every published value.

WHY THE INPUT LOOKS DIFFERENT FROM I3's
    I3 and I5 read era5land_daily_max_<slug>_<year>.nc — one file per country.
    That decomposition was abandoned for I1 because the CDS prices FIELDS, not
    bytes: a global box costs the same as Denmark (365.0 against a limit of
    400.0, measured). Latency is per-request, so 59 country boxes cost 59x the
    queue for nothing. I1 reads 4 merged regional files per year instead, and
    the substations of many countries are sampled out of each one.

    Regions were verified to contain all 59 original boxes with no overlap
    before any request was submitted.

CONVENTION #56
    A substation without coordinates is skipped and counted. A substation on a
    sea cell is snapped to the nearest land cell within MAX_SNAP and counted; if
    none is found it is skipped, never defaulted. ERA5-Land is empty over sea,
    so an unsnapped coastal cell would return a finite, plausible and false
    zero — measured at 900 of Norway's 6,113 substations before the guard
    existed. A country with fewer than MIN_YEARS is refused whole.

THE ANCHOR
    C_bounded on [0, 0.30] needs a frozen raw value mapping to the top of the
    interval. It cannot be chosen before the fleet exists. Run --raw-only
    first: it writes _I1_raw and reports the fleet distribution including the
    99.9th percentile. The anchor is then pinned by amendment, set in ANCHOR
    below, and the script re-run without --raw-only. This is the sequence I3
    followed and it is not shortcut here.
"""
from __future__ import annotations
import argparse, json, pathlib, sys
from datetime import datetime, timezone

import numpy as np
import netCDF4

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "scripts" / "pipeline" / ".cache"

MIN_YEARS = 4
MAX_SNAP = 6
IRI_TOP = 0.30
ANCHOR = None          # metres SWE. Pin by amendment after --raw-only.
TIME_CHUNK = 40        # days read at once; bounds peak memory on a 2 GB file


def slugs():
    d = json.loads((ROOT / "intelligence" / "countries.json").read_text())
    return [c["slug"] for c in (d["countries"] if isinstance(d, dict) else d)]


def load(slug):
    man = json.loads((ROOT / slug / "ssi-data.json").read_text())
    sh = man.get("substations_shards")
    if not sh:
        return man, man.get("substations") or [], None
    subs, paths = [], []
    for e in sh:
        p = ROOT / slug / pathlib.Path(e["path"]).name
        raw = json.loads(p.read_text())
        blk = raw if isinstance(raw, list) else (raw.get("substations") or [])
        subs.extend(blk)
        paths.append((p, len(blk), isinstance(raw, list)))
    return man, subs, paths


def save(slug, man, subs, paths):
    if paths is None:
        man["substations"] = subs
        (ROOT / slug / "ssi-data.json").write_text(json.dumps(man))
        return
    off = 0
    for p, cnt, was_list in paths:
        blk = subs[off:off + cnt]
        off += cnt
        p.write_text(json.dumps(blk if was_list else {"substations": blk}))
    (ROOT / slug / "ssi-data.json").write_text(json.dumps(man))


def region_file(plan, rid, year):
    v = plan["variables"][0]
    ab = "".join(w[0] for w in v.split("_"))[:6]
    return CACHE / f"era5land_{plan['tag']}_{rid}_{ab}_{year}.nc"


def field_name(ds):
    """The data variable, discovered rather than hardcoded.

    ERA5-Land short names are not always what the CDS request asked for
    (snow_depth_water_equivalent arrives as 'sd'). Guessing that mapping is how
    a derivation silently reads the wrong array."""
    skip = {"latitude", "longitude", "valid_time", "time", "number",
            "expver", "lat", "lon"}
    cand = [k for k, v in ds.variables.items()
            if k not in skip and len(v.dimensions) >= 3]
    if len(cand) != 1:
        raise ValueError(f"expected exactly one 3-D field, found {cand}")
    return cand[0]


def axes_and_validity(path):
    ds = netCDF4.Dataset(str(path))
    lat = np.asarray(ds.variables["latitude"][:])
    lon = np.asarray(ds.variables["longitude"][:])
    f = field_name(ds)
    nt = ds.variables[f].shape[0]
    probe = np.asarray(ds.variables[f][::max(1, nt // 8)], dtype="float32")
    ds.close()
    return lat, lon, np.isfinite(probe).any(axis=0), f


def resolve(points, lat, lon, valid):
    """(index -> (i,j) on land), snapped count, skipped count."""
    out, snapped, skipped = {}, 0, 0
    for k, (la, lo) in points:
        i = int(np.abs(lat - la).argmin())
        j = int(np.abs(lon - lo).argmin())
        if not valid[i, j]:
            found = None
            for r in range(1, MAX_SNAP + 1):
                a0, a1 = max(0, i - r), min(valid.shape[0], i + r + 1)
                b0, b1 = max(0, j - r), min(valid.shape[1], j + r + 1)
                blk = valid[a0:a1, b0:b1]
                if blk.any():
                    c = np.argwhere(blk)
                    d2 = (c[:, 0] + a0 - i) ** 2 + (c[:, 1] + b0 - j) ** 2
                    ii, jj = c[int(np.argmin(d2))]
                    found = (int(ii + a0), int(jj + b0))
                    break
            if found is None:
                skipped += 1
                continue
            i, j = found
            snapped += 1
        out[k] = (i, j)
    return out, snapped, skipped


def annual_max(path, cells, field):
    """Max over the year at each cell. Streamed in time chunks.

    A merged region is ~2 GB as float32; reading it whole is an OOM. The
    maximum is associative, so a running max over time chunks is exact."""
    cl = sorted(set(cells.values()))
    rmin, rmax = min(i for i, _ in cl), max(i for i, _ in cl)
    ii = np.array([i - rmin for i, _ in cl])
    jj = np.array([j for _, j in cl])
    pos = {c: k for k, c in enumerate(cl)}

    ds = netCDF4.Dataset(str(path))
    var = ds.variables[field]
    nt = var.shape[0]
    acc = np.full(len(cl), -np.inf, dtype="float32")
    for t0 in range(0, nt, TIME_CHUNK):
        blk = np.asarray(var[t0:t0 + TIME_CHUNK, rmin:rmax + 1, :],
                         dtype="float32")[:, ii, jj]
        acc = np.maximum(acc, np.nanmax(np.where(np.isfinite(blk), blk, -np.inf),
                                        axis=0))
    ds.close()
    acc[~np.isfinite(acc)] = np.nan
    return {k: float(acc[pos[c]]) for k, c in cells.items()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--raw-only", action="store_true",
                    help="write _I1_raw and report the fleet; no normalisation")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    plan = json.loads(pathlib.Path(a.plan).read_text())
    years = [str(y) for y in plan["years"]]
    regions = plan["regions"]
    if not a.raw_only and ANCHOR is None:
        sys.exit("ANCHOR is not pinned. Run --raw-only, take the reported "
                 "P99.9 to amendment, set ANCHOR, then re-run.")

    want = slugs() if a.all else a.slugs
    if not want:
        sys.exit("give country slugs or --all")

    # ---- 1. coordinates only, one country at a time ----
    # Holding every substation RECORD at once is ~620,000 dicts and is
    # OOM-killed. Only lat/lon is needed to place a point in a region, so pass
    # one keeps four numbers per substation and drops the rest. The records are
    # reopened in pass three, one country at a time, to be written.
    placed = {r["id"]: [] for r in regions}
    counts, nocoord, outside = {}, 0, 0
    for slug in sorted(want):
        try:
            _, subs, _ = load(slug)
        except Exception as ex:
            print(f"  {slug:<14}REFUSED — {ex}")
            continue
        counts[slug] = len(subs)
        for k, s in enumerate(subs):
            la, lo = s.get("lat"), s.get("lon")
            if not isinstance(la, (int, float)) or not isinstance(lo, (int, float)):
                nocoord += 1
                continue
            hit = [r for r in regions
                   if r["south"] <= la <= r["north"] and r["west"] <= lo <= r["east"]]
            if not hit:
                outside += 1
                continue
            placed[hit[0]["id"]].append((slug, k, float(la), float(lo)))
        del subs

    print(f"\n  I1 — snow load, mean of annual maximum SWE (metres)")
    print(f"  {len(counts)} countries · {sum(len(v) for v in placed.values()):,} "
          f"substations placed · {nocoord:,} without coordinates · "
          f"{outside:,} outside every region\n")
    if outside:
        print(f"  {outside:,} substations fall outside every merged region. That is a")
        print(f"  COVERAGE GAP, not a rounding detail — the regions were built from")
        print(f"  the old plan's boxes, so anything outside was never in the plan.\n")

    # ---- 2. per region, per year, annual max at each placed cell ----
    peryear = {}
    for r in regions:
        pts = placed[r["id"]]
        if not pts:
            print(f"  {r['id']}  no substations")
            continue
        have = [y for y in years if region_file(plan, r["id"], y).exists()]
        print(f"  {r['id']}  {len(pts):,} substations · {len(have)}/{len(years)} "
              f"years on disk" + ("" if len(have) == len(years) else "  PARTIAL"))
        if not have:
            continue
        lat, lon, valid, field = axes_and_validity(region_file(plan, r["id"], have[0]))
        cells, snapped, skipped = resolve([((s, k), (la, lo))
                                           for s, k, la, lo in pts], lat, lon, valid)
        print(f"        field '{field}' · grid {valid.shape} · "
              f"{snapped:,} snapped to land · {skipped:,} unresolvable")
        if a.dry_run:
            continue
        for y in have:
            am = annual_max(region_file(plan, r["id"], y), cells, field)
            for key, v in am.items():
                peryear.setdefault(key, {})[y] = v
            print(f"        {y}  max at {len(am):,} cells")

    if a.dry_run:
        print("\n  DRY RUN — nothing written")
        return 0

    # ---- 3. mean over years, refusing short records ----
    vals, written = [], {}
    for (slug, k), by in peryear.items():
        good = [v for v in by.values() if v is not None and np.isfinite(v)]
        if len(good) < MIN_YEARS:
            continue
        raw = float(np.mean(good))
        written.setdefault(slug, {})[k] = (raw, len(good))
        vals.append(raw)

    if not vals:
        print("\n  nothing derived — no substation had "
              f"{MIN_YEARS} finite years. Nothing written.")
        return 1

    v = np.array(vals)
    qs = [50, 90, 99, 99.5, 99.9, 100]
    print(f"\n  FLEET — {len(v):,} substations with >= {MIN_YEARS} years")
    for q in qs:
        print(f"    P{q:<6} {np.percentile(v, q):.4f} m SWE")
    print(f"    zero or near-zero (<1 mm): "
          f"{int((v < 0.001).sum()):,} ({100*(v<0.001).mean():.1f}%)")

    for slug, rows in sorted(written.items()):
        man, subs, paths = load(slug)          # reopened here, not held in pass one
        for k, (raw, ny) in rows.items():
            subs[k]["_I1_raw"] = round(raw, 5)
            subs[k]["_I1_years"] = ny
            if ANCHOR:
                m = subs[k].setdefault("metrics", {})
                m["I1"] = round(IRI_TOP * min(1.0, raw / ANCHOR), 5)
        man.setdefault("meta", {}).setdefault("metric_derivations", []).append({
            "metric": "I1",
            "at_utc": datetime.now(timezone.utc).isoformat(),
            "definition": "mean over years of annual maximum snow water "
                          "equivalent at the substation's grid cell, metres SWE",
            "source": f"{plan['dataset']} · {plan['tag']} · merged regions "
                      f"{[r['id'] for r in regions]} · {years[0]}-{years[-1]}",
            "normalisation": "C_bounded" if ANCHOR else "RAW ONLY - anchor not pinned",
            "anchor": ANCHOR, "bounded_interval": [0.0, IRI_TOP],
            "min_years": MIN_YEARS, "n_records": len(rows),
            "coverage_note": f"{len(rows)} of {counts.get(slug, 0)} substations "
                             f"in this country carry I1",
            "gap": "glaze and freezing rain need precipitation phase, which "
                   "this source does not carry. Snow-load metric, ice-load gap."})
        save(slug, man, subs, paths)
        print(f"  {slug:<14}{len(rows):>9,} of {counts.get(slug,0):>9,} written")
        del subs, man

    if ANCHOR is None:
        print("\n  _I1_raw written. metrics.I1 NOT written — the anchor is not")
        print("  pinned. Take the P99.9 above to amendment under Bible s8, set")
        print("  ANCHOR, and re-run without --raw-only.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
