#!/usr/bin/env python3
"""
SSI Index v4.0.2 — Pipeline Orchestrator
Runs the full ingestion → scoring → enrichment pipeline for one or more countries.

Usage:
  python -m scripts.pipeline.run italy                    # Single country
  python -m scripts.pipeline.run italy spain germany      # Multiple countries
  python -m scripts.pipeline.run --all                    # All 10 countries
  python -m scripts.pipeline.run italy --dry-run          # Preview without writing
  python -m scripts.pipeline.run italy --skip-rescore     # Fast mode (no Monte Carlo)
  python -m scripts.pipeline.run italy --seismic-only     # Only seismic ingestion
"""

import argparse
import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Add parent to path for module imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from scripts.pipeline.config import COUNTRIES, REPO_ROOT
from scripts.pipeline.ingestion.seismic import overlay_seismic_pga
from scripts.pipeline.ingestion.climate import compute_iri_forward
from scripts.pipeline.ingestion.socioeconomic import overlay_socioeconomic
from scripts.pipeline.enrichment.merge import merge_and_rescore, generate_diff_report

logger = logging.getLogger("ssi.pipeline")


def run_pipeline(country, skip_seismic=False, skip_climate=False, skip_socio=False,
                 rescore=True, dry_run=False):
    """
    Run the full pipeline for a single country.

    Returns:
        dict — merge statistics and ESG readiness
    """
    logger.info(f"{'=' * 60}")
    logger.info(f"SSI Pipeline — {country.upper()}")
    logger.info(f"{'=' * 60}")

    t0 = time.time()

    # ── Phase 1: Ingestion ──
    logger.info("Phase 1: Data Ingestion")

    seismic_results = None
    climate_results = None
    socio_results = None

    if not skip_seismic:
        logger.info(f"  [1/3] Seismic PGA overlay...")
        try:
            seismic_results = overlay_seismic_pga(country)
            if seismic_results:
                changed = sum(1 for r in seismic_results
                              if abs(r.get("pga_g", 0) - r.get("previous_pga", 0)) > 0.001)
                logger.info(f"        → {len(seismic_results)} substations, {changed} changed from default")
        except Exception as e:
            logger.error(f"        Seismic ingestion failed: {e}")

    if not skip_climate:
        logger.info(f"  [2/3] Climate trajectory (CMIP6 SSP2-4.5)...")
        try:
            climate_results = compute_iri_forward(country)
            if climate_results:
                logger.info(f"        → {len(climate_results)} substations with trajectory updates")
        except Exception as e:
            logger.error(f"        Climate ingestion failed: {e}")

    if not skip_socio:
        logger.info(f"  [3/3] Socio-economic overlay...")
        try:
            socio_results = overlay_socioeconomic(country)
            if socio_results:
                matched = sum(1 for r in socio_results
                              if "V_socio" in r.get("socio_economic", {}))
                logger.info(f"        → {len(socio_results)} substations, {matched} matched")
        except Exception as e:
            logger.error(f"        Socio-economic ingestion failed: {e}")

    # ── Phase 2: Merge & Rescore ──
    logger.info("Phase 2: Merge & Rescore")

    stats = merge_and_rescore(
        country,
        seismic_results=seismic_results,
        climate_results=climate_results,
        socio_results=socio_results,
        rescore=rescore,
        dry_run=dry_run,
    )

    # ── Phase 2b: KB §56 Fleet-Floor Gate ──
    # Per KB §56 (Stub Deploy Regression, May 2026 incident): the cron-driven
    # path previously committed rescored data without running validate-schema.py.
    # Call it now and abort the country if MIN_FLEET is breached. Other
    # countries in the batch must continue uninterrupted.
    if not dry_run:
        scripts_dir = Path(__file__).resolve().parent.parent  # → scripts/
        validator = scripts_dir / "validate-schema.py"
        output_json = REPO_ROOT / country / "ssi-data.json"
        if validator.exists() and output_json.exists():
            logger.info("Phase 2b: Fleet-floor validation (KB §56)")
            result = subprocess.run(
                ["python3", str(validator), str(output_json)],
                capture_output=True, text=True,
            )
            if result.returncode != 0:
                logger.error(f"  ✗ KB §56 FLEET-FLOOR FAILED for {country} — skipping commit, page not updated")
                if result.stdout:
                    logger.error(result.stdout.rstrip())
                if result.stderr:
                    logger.error(result.stderr.rstrip())
                stats["validation_failed"] = True
                stats["validation_output"] = (result.stdout or "") + (result.stderr or "")
                stats["elapsed_seconds"] = round(time.time() - t0, 1)
                # Raise so the outer per-country try/except marks this country as failed
                # while continuing the loop for the rest.
                raise RuntimeError(
                    f"KB §56 fleet-floor validation failed for {country}; refusing to commit."
                )
        else:
            logger.warning(
                f"  ⚠ KB §56 validator or output missing (validator={validator.exists()}, "
                f"output={output_json.exists()}) — fleet-floor check skipped for {country}"
            )

    elapsed = time.time() - t0
    stats["elapsed_seconds"] = round(elapsed, 1)

    # ── Phase 3: Report ──
    report = generate_diff_report(stats)
    logger.info(f"\n{report}")
    logger.info(f"\nPipeline completed in {elapsed:.1f}s")

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="SSI Index v4.0.2 — Pipeline Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m scripts.pipeline.run italy              # Run for Italy
  python -m scripts.pipeline.run --all              # Run for all countries
  python -m scripts.pipeline.run italy --dry-run    # Preview without writing
  python -m scripts.pipeline.run italy --seismic-only  # Seismic only
        """
    )

    parser.add_argument("countries", nargs="*", help="Countries to process")
    parser.add_argument("--all", action="store_true", help="Process all 10 countries")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing to disk")
    parser.add_argument("--skip-rescore", action="store_true", help="Skip Monte Carlo rescoring")
    parser.add_argument("--seismic-only", action="store_true", help="Only run seismic ingestion")
    parser.add_argument("--climate-only", action="store_true", help="Only run climate ingestion")
    parser.add_argument("--socio-only", action="store_true", help="Only run socio-economic ingestion")
    parser.add_argument("--output-report", type=str, help="Write JSON report to file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Determine countries
    if args.all:
        countries = COUNTRIES
    elif args.countries:
        countries = args.countries
    else:
        parser.error("Specify country names or --all")

    # Validate
    for c in countries:
        if c not in COUNTRIES:
            parser.error(f"Unknown country: {c}. Valid: {', '.join(COUNTRIES)}")

    # Determine what to skip
    skip_seismic = args.climate_only or args.socio_only
    skip_climate = args.seismic_only or args.socio_only
    skip_socio = args.seismic_only or args.climate_only

    # Run
    all_stats = {}
    t_total = time.time()

    for country in countries:
        try:
            stats = run_pipeline(
                country,
                skip_seismic=skip_seismic,
                skip_climate=skip_climate,
                skip_socio=skip_socio,
                rescore=not args.skip_rescore,
                dry_run=args.dry_run,
            )
            all_stats[country] = stats
        except Exception as e:
            logger.error(f"Pipeline failed for {country}: {e}")
            all_stats[country] = {"error": str(e)}

    total_elapsed = time.time() - t_total

    # Summary
    logger.info(f"\n{'═' * 60}")
    logger.info(f"PIPELINE COMPLETE — {len(countries)} countries in {total_elapsed:.1f}s")
    logger.info(f"{'═' * 60}")

    for c, s in all_stats.items():
        if "error" in s:
            logger.error(f"  ✗ {c}: FAILED — {s['error']}")
        else:
            esg = s.get("esg_readiness", {})
            ready = sum(1 for r in esg.values() if r.get("status") == "READY")
            partial = sum(1 for r in esg.values() if r.get("status") == "PARTIAL")
            gap = sum(1 for r in esg.values() if r.get("status") == "GAP")
            logger.info(f"  ✓ {c}: {s.get('rescored', 0)} rescored | "
                        f"ESG: {ready} READY, {partial} PARTIAL, {gap} GAP | "
                        f"{s.get('elapsed_seconds', 0)}s")

    # Write report
    if args.output_report:
        report_path = Path(args.output_report)
        with open(report_path, "w") as f:
            json.dump(all_stats, f, indent=2, default=str)
        logger.info(f"Report written to {report_path}")


if __name__ == "__main__":
    main()
