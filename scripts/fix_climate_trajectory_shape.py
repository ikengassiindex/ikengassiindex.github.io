#!/usr/bin/env python3
"""
Path A execution — fix climate_trajectory shape for 7 gap countries.

Root cause (22 July 2026 audit): frontend esg-sections.js:74-76 expects
substation.climate_trajectory as {I1_trajectory, I2_trajectory, I3_trajectory}
dict (v4.2 CMIP6 shape). 7 countries fail this contract:

  Str-shape (legacy v4.0.2 categorical): AU · CL · IE
    → carries climate_trajectory: "deteriorating" (or similar label)
    → overwrite with dict from CMIP6 SSP2-4.5 cross-cutting CSV

  None-shape (field absent): CO · CR · IS · IL
    → climate_trajectory field missing entirely
    → insert dict from CMIP6 SSP2-4.5 cross-cutting CSV

Data source: scripts/pipeline/data/cross-cutting/cmip6_ssp245_deltas.csv
             (global 0.5° grid; filtered per-country by bbox)

No MC rescore triggered. climate_trajectory is not read by scoring engine
(scripts/pipeline/scoring/engine.py) — only written. R_median unchanged.

Usage:
  # Dry-run (analyse only, no writes)
  python3 scripts/fix_climate_trajectory_shape.py --dry-run

  # Fix ONE country
  python3 scripts/fix_climate_trajectory_shape.py --country australia

  # Fix ALL 7 targets
  python3 scripts/fix_climate_trajectory_shape.py --all

Related tasks: #448 (this) · #443 (parent audit) · #450 (Wave 4 uniformity sister)
Related audit: docs/audits/esg_report_climate_trajectory_shape_audit_20260722.md
"""
import argparse
import json
import logging
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("fix_climate_trajectory")

# ── 7 target countries ──
STR_SHAPE_COUNTRIES = ["australia", "chile", "ireland"]
NONE_SHAPE_COUNTRIES = ["colombia", "costa-rica", "iceland", "israel"]
ALL_TARGETS = STR_SHAPE_COUNTRIES + NONE_SHAPE_COUNTRIES


def load_country_data(country):
    """Load ssi-data.json — supports sharded (Wave 4) and non-sharded shapes.

    Returns (index_data, list_of_all_substations, is_sharded_flag).
    For sharded countries, index_data references shards; caller must write shards.
    None of our 7 targets are Wave 4 → all non-sharded → single-file path expected.
    """
    p = REPO_ROOT / country / "ssi-data.json"
    if not p.exists():
        raise FileNotFoundError(f"{p} not found")
    with open(p) as f:
        data = json.load(f)

    if data.get("sharded"):
        # Support 2 sharding schemas: {"shards": [...]} and {"substations_shards": [...]}
        shard_refs = data.get("shards") or data.get("substations_shards") or []
        subs = []
        for sref in shard_refs:
            shard_path = sref["path"] if isinstance(sref, dict) else sref
            with open(REPO_ROOT / country / shard_path) as f:
                shard = json.load(f)
            shard_subs = shard.get("substations", []) if isinstance(shard, dict) else shard
            subs.extend(shard_subs)
        return data, subs, True

    return data, data.get("substations", []), False


def write_country_data(country, index_data, updated_subs, is_sharded):
    """Write ssi-data.json — non-sharded case only (our 7 targets)."""
    if is_sharded:
        raise NotImplementedError(f"{country} is sharded — this script's write path handles non-sharded only")
    p = REPO_ROOT / country / "ssi-data.json"
    index_data["substations"] = updated_subs
    with open(p, "w") as f:
        # Compact JSON per Convention #56 sizing discipline (indent=None)
        json.dump(index_data, f, separators=(",", ":"))
    size_mb = p.stat().st_size / (1024 * 1024)
    logger.info(f"  Wrote {p.name} — {size_mb:.1f} MB")


def compute_trajectories_for_country(country):
    """Call the pipeline's compute_iri_forward with an era5_baseline stub to
    skip the ERA5 fetch (not used by the compute body — only cmip6_deltas is).

    Empirical finding (22 July 2026): the cross-cutting CMIP6 CSV at
    scripts/pipeline/data/cross-cutting/cmip6_ssp245_deltas.csv covers only
    lat range 24-62 / lon -141 to 153, i.e. Europe + N. America + Japan/Korea.
    Our 7 gap countries mostly fall OUTSIDE this bbox:
      - Australia (S. Hemisphere)   — 0 grid points
      - Chile (S. Hemisphere)       — 0 grid points
      - Colombia (tropics, ~5°N)    — 0 grid points
      - Costa-Rica (tropics, ~10°N) — 0 grid points
      - Iceland (>63°N)             — 0 grid points
      - Israel (Middle East)        — 0 grid points
      - Ireland                     — 54 grid points ✓

    Fallback strategy: use compute_iri_forward's built-in country-mean fallback
    path (lines 1180-1184 of climate.py) which activates for substations that
    miss the grid. The fallback emits deterministic {I1=0.9, I2=1.05, I3=1.15}
    matching the SSP2-4.5 global-mean deltas already used by 6 other countries
    in the cohort (Greece, Greenland, Mexico, Poland, Slovakia, Sweden). This
    produces uniform per-substation values, joining the Task #450 systemic
    Wave 4 interpolation regression queue rather than adding a new class.

    To trigger the fallback for the 6 out-of-bbox countries, we pass a dummy
    single grid point at (0, 0) far from every substation → best_pt=None →
    fallback engaged → uniform 0.9/1.05/1.15 values written.

    Ireland gets the real per-substation CSV values (54 grid points covers the
    whole country at 0.5°).

    Returns list of {substation_id, index, I1_trajectory, I2_trajectory, I3_trajectory, delta_t_c}
    """
    from scripts.pipeline.ingestion.climate import (
        compute_iri_forward,
        fetch_cmip6_projections,
    )

    logger.info(f"  [{country}] Loading CMIP6 deltas from cross-cutting CSV…")
    cmip6_deltas = fetch_cmip6_projections(country)
    if not cmip6_deltas:
        # Country's bbox doesn't intersect the CSV coverage. Feed a dummy grid
        # point far from every substation to engage the country-mean fallback
        # path in compute_iri_forward (climate.py:1180). Every substation will
        # miss the lookup and get the deterministic global-mean IPCC AR6
        # SSP2-4.5 deltas (delta_heat=0.15, delta_ice=-0.10, delta_wind=0.05,
        # delta_t=1.0°C), producing I1=0.9, I2=1.05, I3=1.15 uniformly.
        # Same fallback path used by Greece/Greenland/Mexico/Poland/Slovakia/Sweden.
        logger.info(f"  [{country}] CSV coverage misses country bbox — engaging IPCC AR6 "
                    f"SSP2-4.5 global-mean fallback (I1=0.9, I2=1.05, I3=1.15)")
        cmip6_deltas = [{
            "lat": 0.0, "lon": 0.0,
            "delta_t_c": 0.0,
            "delta_heat_pct": 0.0,
            "delta_ice_pct": 0.0,
            "delta_wind_pct": 0.0,
        }]
    else:
        logger.info(f"  [{country}] Got {len(cmip6_deltas)} CMIP6 grid points; computing IRI trajectories…")

    # era5_baseline=[] skips the internal fetch (which requires CDS_API_KEY);
    # compute_iri_forward's body doesn't actually use era5_baseline — only cmip6_deltas
    results = compute_iri_forward(country, era5_baseline=[], cmip6_deltas=cmip6_deltas)
    logger.info(f"  [{country}] Emitted {len(results)} per-substation trajectory rows")
    return results


def apply_fix(country, dry_run=False):
    """Load country data → compute CMIP6 trajectories → overlay dict shape → write."""
    logger.info(f"═══ {country.upper()} ═══")

    # Load current state
    try:
        index_data, subs, is_sharded = load_country_data(country)
    except FileNotFoundError as e:
        logger.error(f"  {e}")
        return None
    logger.info(f"  Loaded {len(subs)} substations (sharded={is_sharded})")

    # Analyse current shape
    n_dict = sum(1 for s in subs if isinstance(s.get("climate_trajectory"), dict))
    n_str = sum(1 for s in subs if isinstance(s.get("climate_trajectory"), str))
    n_none = sum(1 for s in subs if s.get("climate_trajectory") is None)
    logger.info(f"  Pre-fix shape breakdown: dict={n_dict}  str={n_str}  none={n_none}")

    if is_sharded:
        logger.warning(f"  {country} is sharded — write path not supported for this script; skipping.")
        return {"country": country, "status": "sharded-not-supported"}

    # Compute CMIP6-derived trajectories
    results = compute_trajectories_for_country(country)
    if not results:
        return {"country": country, "status": "cmip6-unavailable"}

    # Overlay dict shape on every substation
    # Build lookup by index (compute_iri_forward emits index alongside substation_id)
    by_index = {r["index"]: r for r in results}
    n_updated = 0
    n_str_overwritten = 0
    n_none_filled = 0
    for i, sub in enumerate(subs):
        r = by_index.get(i)
        if r is None:
            continue
        old = sub.get("climate_trajectory")
        new_ct = {
            "I1_trajectory": r["I1_trajectory"],
            "I2_trajectory": r["I2_trajectory"],
            "I3_trajectory": r["I3_trajectory"],
        }
        if isinstance(old, dict) and old == new_ct:
            continue  # no change
        if isinstance(old, str):
            n_str_overwritten += 1
        elif old is None:
            n_none_filled += 1
        sub["climate_trajectory"] = new_ct
        n_updated += 1

    logger.info(f"  Post-fix updates: {n_updated} substations")
    logger.info(f"    str → dict overwrites: {n_str_overwritten}")
    logger.info(f"    None → dict inserts:  {n_none_filled}")

    # Sample verification — show first 3 updated substations
    sample = [r for r in results[:3]]
    for r in sample:
        logger.info(f"    sample: idx={r['index']:>4}  I1={r['I1_trajectory']:.4f}  "
                    f"I2={r['I2_trajectory']:.4f}  I3={r['I3_trajectory']:.4f}")

    # Write
    if dry_run:
        logger.info(f"  DRY-RUN — no file written")
        return {"country": country, "status": "dry-run-ok", "n_updated": n_updated}

    write_country_data(country, index_data, subs, is_sharded)
    logger.info(f"  ✓ {country}/ssi-data.json updated")
    return {"country": country, "status": "success", "n_updated": n_updated}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\nUsage:")[0])
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--country", help="Single country slug to fix")
    grp.add_argument("--all", action="store_true", help=f"Fix all 7 targets: {' '.join(ALL_TARGETS)}")
    grp.add_argument("--diagnose-only", action="store_true", help="Report current shape distribution; no writes")
    parser.add_argument("--dry-run", action="store_true", help="Compute + report, but do not write ssi-data.json")
    args = parser.parse_args()

    if args.diagnose_only:
        for c in ALL_TARGETS:
            try:
                _, subs, _ = load_country_data(c)
                n_dict = sum(1 for s in subs if isinstance(s.get("climate_trajectory"), dict))
                n_str = sum(1 for s in subs if isinstance(s.get("climate_trajectory"), str))
                n_none = sum(1 for s in subs if s.get("climate_trajectory") is None)
                sample = subs[0].get("climate_trajectory") if subs else None
                sample_type = type(sample).__name__
                print(f"  {c:<14} {len(subs):>7} subs  dict={n_dict:>7}  str={n_str:>7}  none={n_none:>7}  sample_type={sample_type}")
            except Exception as e:
                print(f"  {c:<14} ERROR: {e}")
        return

    targets = ALL_TARGETS if args.all else [args.country]
    if not args.all and args.country not in ALL_TARGETS:
        logger.warning(f"{args.country} not in the 7-target list; proceeding anyway")

    summary = []
    for country in targets:
        try:
            result = apply_fix(country, dry_run=args.dry_run)
            summary.append(result)
        except Exception as e:
            logger.error(f"[{country}] EXCEPTION: {type(e).__name__}: {e}")
            summary.append({"country": country, "status": "exception", "error": str(e)})

    print("\n" + "═" * 78)
    print("SUMMARY")
    print("═" * 78)
    for r in summary:
        if r is None:
            continue
        status = r.get("status", "?")
        n = r.get("n_updated", 0)
        print(f"  {r['country']:<14} {status:<28} n_updated={n}")
    total = sum((r or {}).get("n_updated", 0) for r in summary)
    ok = sum(1 for r in summary if r and r.get("status") in ("success", "dry-run-ok"))
    print(f"\n  Countries processed OK: {ok}/{len(targets)}")
    print(f"  Total substations updated: {total}")


if __name__ == "__main__":
    main()
