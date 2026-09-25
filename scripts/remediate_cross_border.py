#!/usr/bin/env python3
"""
remediate_cross_border.py — Discipline #36 source-side remediation
(18 June 2026, KB §72.2).

Applies the per-country point-in-polygon filter to remove foreign substations
from a country's ssi-data.json. Each rejected substation is persisted to
{country}/ingestion_rejected_{date}.json as audit trail.

USE FOR FAILURE MODE 1 ONLY:
  This script removes substations. Use ONLY for countries whose outside-
  polygon substations are CONFIRMED to be foreign misattributions
  (failure mode 1 per CROSS_BORDER_SUBSTATION_AUDIT_20260618.md §
  Failure-mode classification). Do NOT use for failure mode 2 (coastline
  precision — Greenland 83%) or failure mode 3 (overseas-territory polygon
  gaps — Canada 74%, Norway 23%, France 6%, UK 19%, Denmark 5%). Those
  countries need bounds.json extension / refresh, not substation removal.

CONFIRMED FAILURE-MODE-1 COUNTRIES (as of 18 Jun 2026 audit):
  - Austria: 665 substations confirmed Bavarian / Slovenian / Italian /
             Swiss (8/8 sampled exact-duplicates in germany/ssi-data.json
             at byte-identical coordinates). Names: Hauptumspannwerk
             Föhring, Augsburg-Ost, Freising, Geisling, Hudi kot Trpotek,
             RTP Pekre, Fleres FS, Ova Spin, Filisur.
  - Mexico (22.42%): TBD — needs name-evidence audit before remediation
  - Possibly: parts of Norway / UK / Chile after mode classification

USAGE:
  python3 scripts/remediate_cross_border.py austria --dry-run    # preview
  python3 scripts/remediate_cross_border.py austria              # apply
  python3 scripts/remediate_cross_border.py austria --tolerance-km 0.5

WHAT IT DOES:
  1. Load {country}/bounds.json + heal topology
  2. Filter {country}/ssi-data.json substations through point-in-polygon
  3. Backup original ssi-data.json + bounds.json
  4. Persist rejected substations to {country}/ingestion_rejected_{ISO}.json
  5. Recompute fleet_summary, regions, meta totals from kept substations
  6. Write updated ssi-data.json
  7. Re-run check_cross_border to verify CLEAN

SAFETY:
  - --dry-run mode shows what would happen without writing
  - All original files backed up with .pre-remediate-{ISO}.backup suffix
  - Rejected substations preserved in ingestion_rejected_{ISO}.json with
    original schema + audit-trail fields (_reject_reason, _reject_dist_km)
  - Refuses to run if outside% < threshold (default 5%) — no-op for already-clean countries

EXIT CODES:
  0   Remediation completed successfully (or --dry-run preview emitted)
  1   Country already below threshold — no remediation needed
  2   Argument or environment error
  3   Country not in failure-mode-1 (per known classification)
"""
from __future__ import annotations
import argparse
import json
import shutil
import statistics
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Countries CONFIRMED as failure mode 1 (substations should be removed).
# All other violating countries need different remediation (bounds.json
# extension/refresh). See module docstring.
CONFIRMED_FAILURE_MODE_1 = {
    "austria",   # 47.30% — Bavarian / Slovenian / South-Tyrol misattribution
    "mexico",    # 22.42% — US substations crossed border (Sahuarita/AZ,
                 # Rough Canyon/TX, etc.). Confirmed via name-evidence sweep
                 # 18 Jun 2026.
    "canada",    # 74.39% — Reclassification 18 Jun 2026: top outliers at lat
                 # 68.7N lon -52.8W = Greenland (mislabelled NL); bulk at lat
                 # 41.7N lon -97 to -111W = US (mislabelled AB/MB/SK). After
                 # per-country tolerance for coastline (0.1km default).
    "norway",    # 22.54% → 10.05% post-tolerance. Remaining outliers at lat
                 # 64.6-65.0N lon 18.6-19.9E = northern Sweden. Sweden cross-
                 # border ingestion overshoot.
    "uk",        # 19.02% (Jun 2026) → 12.65% (Jul 2026). Top outliers France
                 # 4,132 (Channel + Kent coastline) + Ireland 896. Pure Mode 1.
    "france",    # 6.58% (Jun 2026) → 24.27% (Jul 2026 Wave 4 REGRESSION).
                 # Belgium 12,558 + Switzerland 3,051 + UK 2,711 + Italy 2,676
                 # + Germany 2,090 + Spain 411 — all Wave 4 OSM overshoot.
    "chile",     # 11.87% — Top outliers at lat -50.02 lon -68.54 = Argentinian
                 # Patagonia (Santa Cruz province). Argentinian substations
                 # crossed border.
    # ─── NEW Wave 4 additions (24 July 2026 empirical audit) ────────────
    "sweden",    # 94.79% — CATASTROPHIC. Denmark 6,076 (Copenhagen at
                 # 12.58E, 55.69N cluster) + Latvia 2,629 (Riga at 24.10E,
                 # 56.96N) + Finland 484 + Norway 447 + Estonia 104 +
                 # Lithuania 85 = ~9,825 pure Mode 1 cross-border. + Baltic
                 # offshore 354 + 626 unclassified (may be interior-gap OR
                 # legit). Only 594/11,399 = 5.2% actually inside Sweden.
                 # Wave 4 OSM Overpass bbox massively overshot into Nordic +
                 # Baltic neighbors. Empirical evidence: audit_out_of_polygon_
                 # audit_sweden_20260723T170921Z.json.
    "spain",     # 80.62% — CATASTROPHIC. France 13,623 (Pyrénées Atlantiques
                 # 0.14E, 43.08N cluster) + Portugal 4,707 (western border
                 # 8.43W, 41.50N) + smaller offshore/Med/Morocco = ~18,330
                 # pure Mode 1 cross-border. NOTE: 4,103 UNCLASSIFIED subs
                 # sampled at Barcelona (2.24E, 41.64N), Aragón (-2.50, 41.77),
                 # Castilla (-4.95, 42.36) — actually inside Spain, indicating
                 # ~13% bounds.json interior-gap (Class B, needs polygon
                 # refresh not substation removal). Recommend running with
                 # --tolerance-km 5 to preserve interior-gap subs while
                 # stripping true cross-border. Wave 4 OSM overshoot.
    "portugal",  # 13.53% — Spain 1,743 (border overshoot) + Azores/Madeira
                 # 148 (legit offshore). Real Mode 1 cross-border ~1,743.
                 # Mirror of Spain Portugal 4,707 overshoot — both Wave 4
                 # Iberian ingestions overshot into each other.
    "germany",   # 15.95% — Czechia 8,849 (border overshoot) + Austria 3,603
                 # + France 2,634 + Netherlands 2,195 + Poland 1,305 +
                 # Switzerland 908 + Belgium 874 + Denmark 756 + Luxembourg
                 # 5 = ~21,129 pure Mode 1 across 9 neighbors. + Baltic Sea
                 # 4,784 (mostly legit Nord Stream + wind farms; needs case
                 # audit) + North Sea 619 (legit offshore) + 3,401 UNCLASSIFIED.
                 # Wave 4 land-border overshoot into ALL neighbors.
    "us",        # 43.10% — Mexico 8,808 (border overshoot 89.8W, 30.3N =
                 # Louisiana/Texas coast) + Canada 8,165 (Toronto area 79.3W,
                 # 43.7N) = ~16,973 pure Mode 1 cross-border. + North
                 # Atlantic offshore 5,837 (legit East Coast wind farms +
                 # subsea cables) + Pacific 3,592 (Hawaii Alaska legit) +
                 # Gulf of Mexico 1,773 (legit offshore rigs) + 15,161
                 # UNCLASSIFIED at Appalachian region (VA/KY/TN) —
                 # BOUNDS.JSON QUALITY ISSUE (Class B), NOT pollution.
                 # Recommend --tolerance-km 5 to preserve Appalachian interior
                 # subs. Wave 4 OSM overshoot into Mexico + Canada.
    "italy",     # 35.11% — Switzerland 1,637 (Alpine border) + France 1,018
                 # (SE Riviera) + Austria 732 (South Tyrol) + Slovenia 337 +
                 # Malta 227 + Croatia 39 + Vatican 6 = ~3,996 pure Mode 1
                 # cross-border. BUT 10,292 Tyrrhenian Sea + 1,192 Adriatic
                 # + 996 Ligurian + 545 Ionian = 13,025 offshore subs which
                 # are Sardinia + Sicily coordinates being EXCLUDED from
                 # mainland-only bounds.json. This is BOUNDS.JSON QUALITY
                 # (Class B, ~63% of Italy's outside-polygon), NOT pollution.
                 # Recommend bounds.json refresh to include Sardinia + Sicily
                 # + minor islands BEFORE remediation, else strip legitimate
                 # island substations.
    "japan",     # 32.09% — Russia 261 (Sakhalin/Kuriles border overshoot) +
                 # Korea 14 = ~275 pure Mode 1. But 1,715 offshore subs (Sea
                 # of Japan 1,346 + Pacific 136 + East China Sea 118 +
                 # Philippine Sea 115) — mix of legitimate archipelago
                 # (Kii Peninsula 280 UNCLASSIFIED) and coastal subs whose
                 # coordinates fall in sea per 1:1M polygon. NEEDS CAREFUL
                 # REVIEW — Japan is mostly Class B (bounds quality) + Class
                 # C (legit offshore), only ~4% Class A. Run with high
                 # tolerance (--tolerance-km 10) OR skip remediation and
                 # only refresh bounds.json.
}

# Countries to NEVER auto-remediate via this script (handled by tolerance
# config or polygon refresh instead).
KNOWN_FAILURE_MODE_2_OR_3 = {
    # All handled via cross_border_tolerances.json per-country tolerance:
    "greenland",
    "new-zealand",
    "denmark",
}


# ─── Severity helpers (mirror check_cross_border.py) ────────────────────────
def severity(pct_out: float) -> str:
    if pct_out >= 30:
        return "🚨 SEVERE"
    if pct_out >= 10:
        return "⚠ MODERATE"
    if pct_out >= 1:
        return "⚪ MINOR"
    return "✅ CLEAN"


# ─── Statistics recomputation ──────────────────────────────────────────────
def percentile(values, p):
    """Compute the p-th percentile (0-100). Uses linear interpolation."""
    if not values:
        return None
    vs = sorted(values)
    k = (len(vs) - 1) * (p / 100)
    f = int(k)
    c = min(f + 1, len(vs) - 1)
    if f == c:
        return vs[f]
    return vs[f] + (vs[c] - vs[f]) * (k - f)


def recompute_fleet_summary(subs, original_summary):
    """Recompute fleet_summary statistics from the filtered substation list."""
    n = len(subs)
    r_bases = [s.get("R_base") for s in subs if isinstance(s.get("R_base"), (int, float))]
    classifications = Counter(s.get("classification") for s in subs)
    tiers = Counter(s.get("confidence_tier") for s in subs)

    bands = {
        "Low": classifications.get("Low", 0),
        "Medium": classifications.get("Medium", 0),
        "High": classifications.get("High", 0),
        "Critical": classifications.get("Critical", 0),
    }
    band_pct = {
        k: round(100 * v / n, 1) if n else 0.0
        for k, v in bands.items()
    }

    summary = dict(original_summary)  # Preserve any non-recomputed keys
    summary["total"] = n
    summary["median_R"] = round(statistics.median(r_bases), 4) if r_bases else None
    summary["mean_R"] = round(statistics.mean(r_bases), 4) if r_bases else None
    p5 = percentile(r_bases, 5)
    p95 = percentile(r_bases, 95)
    summary["P5"] = round(p5, 4) if p5 is not None else None
    summary["P95"] = round(p95, 4) if p95 is not None else None
    summary["bands"] = bands
    summary["band_pct"] = band_pct
    summary["confidence_tiers"] = {
        "high": tiers.get("high", 0),
        "medium": tiers.get("medium", 0),
        "low": tiers.get("low", 0),
    }
    return summary


def recompute_regions(subs, original_regions):
    """
    Recompute per-region rollup from filtered substations.
    Preserves the order of original_regions (which is a list of dicts).
    Drops any region that has zero kept substations.
    """
    # Bucket substations by region
    by_region = {}
    for s in subs:
        r = s.get("region")
        if r is None:
            continue
        by_region.setdefault(r, []).append(s)

    new_regions = []
    for orig in original_regions:
        rname = orig.get("region")
        bucket = by_region.get(rname, [])
        if not bucket:
            # Region has zero kept substations — drop, but log
            print(f"  ⚠ region '{rname}' has 0 kept substations — DROPPED from regions")
            continue
        r_bases = [s.get("R_base") for s in bucket
                   if isinstance(s.get("R_base"), (int, float))]
        classifications = Counter(s.get("classification") for s in bucket)
        bands = {
            "Low": classifications.get("Low", 0),
            "Medium": classifications.get("Medium", 0),
            "High": classifications.get("High", 0),
            "Critical": classifications.get("Critical", 0),
        }
        n = len(bucket)
        new_regions.append({
            "region": rname,
            "count": n,
            "median_R": round(statistics.median(r_bases), 4) if r_bases else None,
            "mean_R": round(statistics.mean(r_bases), 4) if r_bases else None,
            "bands": bands,
            "pct_critical": round(100 * bands["Critical"] / n, 1) if n else 0.0,
            "pct_high": round(100 * bands["High"] / n, 1) if n else 0.0,
        })
    return new_regions


def recompute_meta(meta, n_kept, n_hv, n_mv, n_regions):
    """Update meta totals + add remediation provenance."""
    meta = dict(meta)
    meta["n_substations"] = n_kept
    meta["total"] = n_kept
    meta["n_HV"] = n_hv
    meta["n_MV"] = n_mv
    meta["n_regions"] = n_regions
    # Add provenance record per existing pattern
    history = meta.get("normalisation_history", [])
    if not isinstance(history, list):
        history = []
    history.append({
        "action": "cross_border_polygon_remediation",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "discipline": "#36",
        "kb_section": "§72.2",
        "audit_memo": "CROSS_BORDER_SUBSTATION_AUDIT_20260618.md",
    })
    meta["normalisation_history"] = history
    meta["last_remediation_at"] = datetime.now(timezone.utc).isoformat()
    meta["last_remediation_discipline"] = "#36"
    return meta


# ─── Main remediation flow ─────────────────────────────────────────────────
def remediate(country, tolerance_km=0.1, threshold_pct=5.0, dry_run=False,
              force=False):
    if country in KNOWN_FAILURE_MODE_2_OR_3 and not force:
        print(f"REFUSE: '{country}' is failure mode 2 or 3 (coastline / "
              f"overseas-territory polygon gap). Remediation should fix "
              f"bounds.json, NOT remove substations. Pass --force to "
              f"override (NOT RECOMMENDED).", file=sys.stderr)
        sys.exit(3)

    if country not in CONFIRMED_FAILURE_MODE_1 and not force:
        print(f"WARN: '{country}' not in CONFIRMED_FAILURE_MODE_1 list. "
              f"Run name-evidence audit first to confirm misattribution is "
              f"the right diagnosis. Pass --force to proceed anyway.",
              file=sys.stderr)
        sys.exit(3)

    sys.path.insert(0, str(REPO_ROOT))
    from scripts.pipeline.utils.geo import (
        load_country_polygon, load_substations, filter_by_country_polygon,
        load_country_tolerance,
    )

    # Resolve tolerance: explicit arg > per-country config > default
    if tolerance_km is None:
        tolerance_km = load_country_tolerance(country, repo_root=REPO_ROOT)

    print(f"\n=== Remediating {country} ===")
    print(f"  tolerance: {tolerance_km} km")
    print(f"  mode:      {'DRY RUN' if dry_run else 'APPLY'}")
    print()

    # Load polygon (auto-heal topology)
    poly = load_country_polygon(country, repo_root=REPO_ROOT, heal_topology=True)
    if poly is None:
        print(f"FATAL: {country}/bounds.json missing or invalid.", file=sys.stderr)
        sys.exit(2)

    # Load substations
    data, subs = load_substations(country, repo_root=REPO_ROOT)
    n_total = len(subs)

    # Filter
    kept, rejected = filter_by_country_polygon(subs, poly, tolerance_km=tolerance_km)
    pct_rejected = (100 * len(rejected) / n_total) if n_total else 0.0

    print(f"  Total substations:   {n_total}")
    print(f"  Inside polygon:      {len(kept)}  ({100*len(kept)/n_total:.2f}%)")
    print(f"  Outside polygon:     {len(rejected)}  ({pct_rejected:.2f}%)")
    print(f"  Severity:            {severity(pct_rejected)}")
    print()

    if pct_rejected < threshold_pct and not force:
        print(f"NO-OP: outside% {pct_rejected:.2f}% < threshold {threshold_pct}%. "
              f"Country already clean; remediation not needed.")
        sys.exit(1)

    # Sample rejected for human review
    print(f"=== SAMPLE OF REJECTED SUBSTATIONS (top 10 by drift) ===")
    rejected_sorted = sorted(rejected, key=lambda r: -r.get("_reject_dist_km", 0))
    for r in rejected_sorted[:10]:
        print(f"  {(r.get('name') or '?')[:36]:36}  "
              f"region={(r.get('region') or '?')[:20]:20}  "
              f"lat={r.get('lat'):.4f} lon={r.get('lon'):.4f}  "
              f"~{r.get('_reject_dist_km')} km outside")
    if len(rejected_sorted) > 10:
        print(f"  ... and {len(rejected_sorted) - 10} more (see ingestion_rejected file)")
    print()

    if dry_run:
        print("=== DRY RUN — no files written ===")
        print(f"Would write {len(kept)} substations to {country}/ssi-data.json")
        print(f"Would write {len(rejected)} rejected to {country}/ingestion_rejected_*.json")
        print(f"Would back up original ssi-data.json")
        sys.exit(0)

    # ── APPLY ──
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    country_dir = REPO_ROOT / country

    # Backup original
    ssi_data_path = country_dir / "ssi-data.json"
    backup_path = country_dir / f"ssi-data.json.pre-remediate-{ts}.backup"
    shutil.copy2(ssi_data_path, backup_path)
    print(f"  ✓ Backed up original ssi-data.json to:")
    print(f"    {backup_path.name}")

    # Persist rejected list as audit trail
    rejected_path = country_dir / f"ingestion_rejected_{ts}.json"
    with open(rejected_path, "w") as f:
        json.dump({
            "country": country,
            "remediation_timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "tolerance_km": tolerance_km,
            "discipline": "#36",
            "kb_section": "§72.2",
            "audit_memo": "CROSS_BORDER_SUBSTATION_AUDIT_20260618.md",
            "rejected_count": len(rejected),
            "rejected_substations": rejected,
        }, f, indent=2)
    print(f"  ✓ Persisted {len(rejected)} rejected substations to:")
    print(f"    {rejected_path.name}")

    # Recompute meta + fleet_summary + regions
    n_hv = sum(1 for s in kept if isinstance(s.get("voltage_kv"), (int, float))
               and s["voltage_kv"] >= 60)
    n_mv = len(kept) - n_hv

    new_meta = recompute_meta(
        data.get("meta", {}),
        n_kept=len(kept),
        n_hv=n_hv,
        n_mv=n_mv,
        n_regions=len(set(s.get("region") for s in kept if s.get("region"))),
    )

    new_fleet = recompute_fleet_summary(kept, data.get("fleet_summary", {}))
    new_regions = recompute_regions(kept, data.get("regions", []))

    data["substations"] = kept
    data["meta"] = new_meta
    data["fleet_summary"] = new_fleet
    data["regions"] = new_regions

    # Task #520 fix (24 July 2026 night): Convention #79 sharded ssi-data
    # awareness. Wave 4 large countries (US, France, Germany, UK, Italy) store
    # substations across shard files. When we've just filtered ~10-100k subs,
    # the resulting single-file could easily exceed 90 MB → GitHub push refused.
    # Delegate to canonical write_ssi_data() which auto-shards above threshold
    # (default 90 MB hard limit / 60 MB target per shard).
    # Also strip the old shard-manifest keys from `data` before writing —
    # write_ssi_data will re-emit them if resharding is needed.
    for stale_key in ("sharded", "substations_shards", "shards"):
        data.pop(stale_key, None)
    try:
        from scripts.pipeline.utils.ssi_data_sharding import write_ssi_data as _write_ssi
        stats = _write_ssi(data, ssi_data_path)
        if stats.get("sharded"):
            print(f"  ✓ Wrote updated ssi-data.json manifest + "
                  f"{stats['shard_count']} shard files (Convention #79); "
                  f"{len(kept)} substations total")
        else:
            print(f"  ✓ Wrote updated ssi-data.json (single-file, "
                  f"{stats['size_mb']:.1f} MB) with {len(kept)} substations")
    except ImportError:
        # Fallback — single-file write (legacy behaviour)
        with open(ssi_data_path, "w") as f:
            json.dump(data, f, separators=(",", ":"))
        print(f"  ✓ Wrote updated ssi-data.json with {len(kept)} substations "
              f"(single-file legacy path; Convention #79 sharding utility unavailable)")
    print()

    # Verify gate now passes
    print("=== VERIFY: re-running check_cross_border on remediated country ===")
    from scripts.pipeline.utils.geo import cross_border_audit
    report = cross_border_audit(country, repo_root=REPO_ROOT,
                                tolerance_km=tolerance_km)
    new_pct = report["pct_outside"]
    new_sev = severity(new_pct)
    print(f"  After remediation: {report['inside']}/{report['total']} inside "
          f"({100 - new_pct:.2f}%), {report['outside']} outside ({new_pct:.2f}%) "
          f"{new_sev}")
    print()

    if new_pct >= threshold_pct:
        print(f"⚠ WARNING: country still above {threshold_pct}% threshold "
              f"after remediation. Manual investigation needed.", file=sys.stderr)
    else:
        print(f"✓ Country now CLEAN at {new_pct:.2f}% outside.")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Per-country cross-border remediation (Discipline #36).",
        epilog="Use --dry-run first. Use ONLY for failure-mode-1 countries.",
    )
    parser.add_argument("country", help="Country slug to remediate.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without writing files.")
    parser.add_argument("--tolerance-km", type=float, default=None,
                        help="Boundary tolerance in km. If omitted, per-country "
                             "override from cross_border_tolerances.json is used "
                             "(or 0.1 / 100m default).")
    parser.add_argument("--threshold", type=float, default=5.0,
                        help="Skip if outside%% < threshold. Default 5.0%%.")
    parser.add_argument("--force", action="store_true",
                        help="Bypass safety guards. Use only when confirmed.")
    args = parser.parse_args()

    sys.exit(remediate(
        args.country,
        tolerance_km=args.tolerance_km,
        threshold_pct=args.threshold,
        dry_run=args.dry_run,
        force=args.force,
    ))


if __name__ == "__main__":
    main()
