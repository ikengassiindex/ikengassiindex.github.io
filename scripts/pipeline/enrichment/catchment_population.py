#!/usr/bin/env python3
"""catchment_population.py — GHSL Population Grid spatial-join enrichment

Task #451 Step 3 (23 July 2026)
==============================

Populates `socio_economic.population` per substation from the GHSL Population
Grid (EC JRC / Copernicus Emergency Management Service, GHS-POP R2023A).
Retires the pre-existing synthetic-generator in scripts/score-country.py line
195 (`int(det_var(seed+'pop', ref.get('pop_density',50)*25, 0.40))`) that
fabricated population values from deterministic-variance rather than sourcing
from real population data (Task #450 / #117 / #159 D2 modifier drift class
manifesting at R2 Grid Equity axis).

Methodology
-----------
For each substation at (lat, lon):
  1. Reproject WGS84 (EPSG:4326) → Mollweide equal-area (EPSG:54009).
  2. Buffer the point with a circle of `radius_km` (default 5 km per v4.2
     methodology).
  3. Sum GHSL pixel values intersecting the buffer (each pixel = population
     count for that pixel's ground area at 30 arc-sec ≈ 1 km).
  4. Write result as integer to `sub['socio_economic']['population']`.
  5. Convention #56 fallback: if buffer falls outside raster coverage or all
     pixels are NoData, write None (visibly-honest degradation).

Pre-flight source verification (docs/audits/task_451_catchment_population_
preflight_20260723.yaml Step 2):
  - Publisher: EC JRC / Copernicus Emergency Management Service
  - License: attribution-required open license (Convention #7 + #60 compat)
  - Product: GHS-POP R2023A, epoch E2025
  - Coordinate system: Mollweide (EPSG:54009) equal-area, 30 arc-sec ~1 km
  - File format: GeoTIFF (single-file global or tile-based)

Convention preservation
-----------------------
- Convention #56 visibly-honest degradation: any substation for which the
  raster lookup fails writes None (not a fabricated fallback value).
- Convention #7 documented-proxy: uses public regulatory canonical (GHSL).
- Convention #60 (Ikenga IS the ESG provider): non-commercial open-license
  raster from public institutional publisher.
- Convention #79 candidate sharding: uses same read_ssi_data / write_ssi_data
  as siblings (scripts/pipeline/utils/ssi_data_sharding.py).

Usage
-----
Diagnose-only (check dependencies + raster presence, no reads):
    python3 scripts/pipeline/enrichment/catchment_population.py --diagnose-only

Single country dry-run (compute + report, don't write):
    python3 scripts/pipeline/enrichment/catchment_population.py spain --dry-run

Single country apply:
    python3 scripts/pipeline/enrichment/catchment_population.py spain

Cohort-wide apply (39 countries per intelligence/countries.json SoT):
    python3 scripts/pipeline/enrichment/catchment_population.py --all-countries

Force rewrite (overwrite existing synthetic values with real):
    python3 scripts/pipeline/enrichment/catchment_population.py spain --force-rewrite

Custom radius (methodology exploration):
    python3 scripts/pipeline/enrichment/catchment_population.py spain --radius-km 3
"""
from __future__ import annotations

import argparse
import json
import logging
import math
import sys
import time
from pathlib import Path
from typing import Any, Optional

# ── path setup for repo-relative imports ────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# ── graceful geospatial-dependency imports ──────────────────────────────
# rasterio + pyproj + shapely are heavy dependencies. Fall back gracefully
# so the file can be imported for --diagnose-only mode even without them.

try:
    import rasterio  # type: ignore
    from rasterio.mask import mask as raster_mask  # type: ignore
    _HAS_RASTERIO = True
except ImportError:
    _HAS_RASTERIO = False

try:
    from pyproj import Transformer  # type: ignore
    _HAS_PYPROJ = True
except ImportError:
    _HAS_PYPROJ = False

try:
    from shapely.geometry import Point, mapping  # type: ignore
    _HAS_SHAPELY = True
except ImportError:
    _HAS_SHAPELY = False

# ── conditional imports of pipeline utilities ───────────────────────────

try:
    from scripts.pipeline.utils.ssi_data_sharding import (  # type: ignore
        read_ssi_data,
        write_ssi_data,
    )
    _HAS_SHARDING = True
except ImportError:
    _HAS_SHARDING = False


# ── constants ───────────────────────────────────────────────────────────

DEFAULT_RADIUS_KM = 5.0

# GHSL raster path — download by operator into docs/audits/ or equivalent
# during Task #451 Step 4. Convention #56 fallback if absent.
DEFAULT_GHSL_RASTER_PATH = REPO_ROOT / "docs" / "audits" / "GHS_POP_E2025_GLOBE_R2023A_54009_1000_V1_0.tif"

# Coordinate systems
CRS_WGS84 = "EPSG:4326"        # substation lat/lon
CRS_MOLLWEIDE = "EPSG:54009"   # GHSL native (equal-area, ideal for buffers)

# Convention #56 marker — audit-trail field per substation
AUDIT_TRAIL_KEY = "_catchment_population_source"
AUDIT_TRAIL_VALUE = "GHSL_POP_R2023A_E2025_v4_2_task_451"


# ── logging ─────────────────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s %(levelname)-7s %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════
#  GHSL raster loader
# ══════════════════════════════════════════════════════════════════════

class GHSLRaster:
    """Lazy GHSL Population Grid loader with windowed reads.

    Opens the GHSL GeoTIFF on demand and computes population totals for
    per-substation buffers via rasterio's `mask` operation. Assumes the
    raster is Mollweide (EPSG:54009); each pixel value = population count
    for that pixel's ~1km² ground area at 30 arc-sec resolution.
    """

    def __init__(self, raster_path: Path):
        if not _HAS_RASTERIO:
            raise RuntimeError(
                "rasterio not installed — install via `pip install rasterio`"
            )
        if not _HAS_SHAPELY:
            raise RuntimeError(
                "shapely not installed — install via `pip install shapely`"
            )
        if not _HAS_PYPROJ:
            raise RuntimeError(
                "pyproj not installed — install via `pip install pyproj`"
            )
        self.path = Path(raster_path)
        if not self.path.exists():
            raise FileNotFoundError(
                f"GHSL raster not found at {self.path}. "
                f"Download E2025 30-arc-sec Mollweide GeoTIFF from "
                f"https://human-settlement.emergency.copernicus.eu/download.php?ds=pop "
                f"and place at {DEFAULT_GHSL_RASTER_PATH} (Task #451 Step 4)."
            )
        self._dataset: Any = None
        self._transformer: Any = None

    def _open(self) -> None:
        if self._dataset is None:
            self._dataset = rasterio.open(str(self.path))
            log.info(
                f"[GHSL] loaded {self.path.name} — "
                f"crs={self._dataset.crs} "
                f"shape={self._dataset.shape} "
                f"bounds={self._dataset.bounds}"
            )
            # Read the raster's own CRS instead of hardcoding — the GHSL
            # E2025 raster carries ESRI:54009 (Mollweide, ESRI authority),
            # which older pyproj builds recognise while EPSG:54009 may not
            # be in their proj.db. Whatever authority the raster carries,
            # pyproj handles via the WKT round-trip through rasterio.CRS.
            raster_crs_wkt = self._dataset.crs.to_wkt()
            self._transformer = Transformer.from_crs(
                CRS_WGS84, raster_crs_wkt, always_xy=True
            )

    def catchment_population(
        self, lat: float, lon: float, radius_km: float = DEFAULT_RADIUS_KM
    ) -> Optional[int]:
        """Sum GHSL pixel values within radius_km of (lat, lon).

        Returns integer population count, or None if buffer falls outside
        raster coverage / all pixels are NoData (Convention #56 fallback).
        """
        self._open()

        # 1. Reproject substation coords WGS84 → Mollweide (equal-area).
        try:
            x_m, y_m = self._transformer.transform(lon, lat)
        except Exception as e:  # noqa: BLE001
            log.warning(f"  reproject failed lat={lat} lon={lon}: {e}")
            return None

        if not (math.isfinite(x_m) and math.isfinite(y_m)):
            return None

        # 2. Build a circular buffer at radius_km (meters in Mollweide).
        buffer_geom = Point(x_m, y_m).buffer(radius_km * 1000.0)

        # 3. Zonal sum via rasterio.mask (crops raster to buffer + returns
        #    pixel values).
        try:
            out_image, _out_transform = raster_mask(
                self._dataset,
                [mapping(buffer_geom)],
                crop=True,
                filled=False,  # NoData → masked (excluded from sum)
                all_touched=True,  # include pixels partially in buffer
            )
        except ValueError:
            # ValueError typically = buffer entirely outside raster extent
            return None

        # 4. Sum finite values (masked pixels excluded).
        try:
            pixel_sum = float(out_image.sum())
        except Exception:  # noqa: BLE001
            return None

        if not math.isfinite(pixel_sum) or pixel_sum <= 0:
            return None

        return int(round(pixel_sum))

    def close(self) -> None:
        if self._dataset is not None:
            self._dataset.close()
            self._dataset = None


# ══════════════════════════════════════════════════════════════════════
#  Per-country enrichment
# ══════════════════════════════════════════════════════════════════════

def enrich_country(
    slug: str,
    raster: GHSLRaster,
    *,
    radius_km: float = DEFAULT_RADIUS_KM,
    dry_run: bool = False,
    force_rewrite: bool = False,
) -> dict:
    """Apply GHSL catchment_population enrichment to one country.

    Reads slug/ssi-data.json (sharded or single-file), enriches
    socio_economic.population per substation, writes back (unless dry_run).

    Returns audit dict with counts + timing + delta stats.
    """
    if not _HAS_SHARDING:
        raise RuntimeError(
            "ssi_data_sharding utility not importable — check REPO_ROOT resolution"
        )

    t0 = time.time()
    ssi_path = REPO_ROOT / slug / "ssi-data.json"
    if not ssi_path.exists():
        raise FileNotFoundError(f"[{slug}] ssi-data.json not found at {ssi_path}")

    log.info(f"[{slug}] loading ssi-data...")
    data = read_ssi_data(ssi_path)
    substations = data.get("substations", [])
    n = len(substations)
    if n == 0:
        raise RuntimeError(f"[{slug}] ssi-data has zero substations")
    log.info(f"[{slug}] {n:,} subs loaded in {time.time()-t0:.1f}s")

    # ── audit counters ──────────────────────────────────────────────────
    n_written = 0
    n_skipped_existing = 0    # subs that already had non-None population
    n_none_convention_56 = 0  # subs where raster fallback fired
    n_missing_coords = 0
    delta_from_synthetic = 0  # count of subs whose pre-value was synthetic

    log.info(f"[{slug}] enriching (radius_km={radius_km})...")
    for i, sub in enumerate(substations, 1):
        lat = sub.get("lat")
        lon = sub.get("lon")
        if lat is None or lon is None:
            n_missing_coords += 1
            continue

        se = sub.setdefault("socio_economic", {})
        existing = se.get("population")

        if existing is not None and not force_rewrite:
            n_skipped_existing += 1
            continue

        pop = raster.catchment_population(lat, lon, radius_km)

        if existing is not None and force_rewrite:
            delta_from_synthetic += 1

        se["population"] = pop
        se[AUDIT_TRAIL_KEY] = AUDIT_TRAIL_VALUE
        if pop is None:
            n_none_convention_56 += 1
        else:
            n_written += 1

        if i % 10_000 == 0:
            elapsed = time.time() - t0
            rate = i / max(elapsed, 0.01)
            eta = (n - i) / max(rate, 0.01)
            log.info(
                f"[{slug}]   {i:,}/{n:,} ({100*i/n:.1f}%) - "
                f"{rate:.0f} subs/s - ETA {eta:.0f}s"
            )

    if dry_run:
        log.info(f"[{slug}] DRY-RUN — no write")
    else:
        log.info(f"[{slug}] writing ssi-data.json (may re-shard if > 90.0 MB)...")
        write_ssi_data(data, ssi_path)
        log.info(f"[{slug}] saved.")

    elapsed = time.time() - t0
    return {
        "country": slug,
        "n_substations": n,
        "n_written": n_written,
        "n_none_convention_56": n_none_convention_56,
        "n_skipped_existing": n_skipped_existing,
        "n_missing_coords": n_missing_coords,
        "delta_from_synthetic": delta_from_synthetic,
        "radius_km": radius_km,
        "wall_clock_sec": round(elapsed, 1),
        "raster_source": "GHSL_POP_R2023A_E2025",
        "dry_run": dry_run,
        "force_rewrite": force_rewrite,
    }


# ══════════════════════════════════════════════════════════════════════
#  Diagnostics
# ══════════════════════════════════════════════════════════════════════

def diagnose(raster_path: Path) -> dict:
    """Report dependency state + raster presence without touching ssi-data."""
    diag = {
        "rasterio_installed": _HAS_RASTERIO,
        "pyproj_installed": _HAS_PYPROJ,
        "shapely_installed": _HAS_SHAPELY,
        "ssi_data_sharding_importable": _HAS_SHARDING,
        "raster_path": str(raster_path),
        "raster_exists": raster_path.exists(),
        "raster_size_mb": (
            round(raster_path.stat().st_size / 1_000_000, 1)
            if raster_path.exists() else None
        ),
    }
    diag["ready_for_step_4"] = all([
        _HAS_RASTERIO, _HAS_PYPROJ, _HAS_SHAPELY,
        _HAS_SHARDING, raster_path.exists()
    ])
    return diag


# ══════════════════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════════════════

def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("slug", nargs="?", help="country slug (e.g. spain)")
    ap.add_argument(
        "--all-countries", action="store_true",
        help="run against all 39 cohort countries per intelligence/countries.json",
    )
    ap.add_argument(
        "--radius-km", type=float, default=DEFAULT_RADIUS_KM,
        help=f"catchment radius in km (default {DEFAULT_RADIUS_KM})",
    )
    ap.add_argument(
        "--raster", type=Path, default=DEFAULT_GHSL_RASTER_PATH,
        help="path to GHSL raster GeoTIFF",
    )
    ap.add_argument(
        "--dry-run", action="store_true",
        help="compute + report, don't write ssi-data.json",
    )
    ap.add_argument(
        "--diagnose-only", action="store_true",
        help="report dependency + raster state, exit without touching ssi-data",
    )
    ap.add_argument(
        "--force-rewrite", action="store_true",
        help="overwrite existing socio_economic.population values "
             "(retires synthetic values from score-country.py)",
    )
    args = ap.parse_args()

    # ── Diagnose-only mode ─────────────────────────────────────────────
    if args.diagnose_only:
        diag = diagnose(args.raster)
        print(json.dumps(diag, indent=2))
        sys.exit(0 if diag["ready_for_step_4"] else 1)

    # ── Ensure geospatial deps available ────────────────────────────────
    if not (_HAS_RASTERIO and _HAS_PYPROJ and _HAS_SHAPELY and _HAS_SHARDING):
        log.error(
            "Missing required deps. Run with --diagnose-only for details. "
            "Typical install: pip install rasterio pyproj shapely"
        )
        sys.exit(2)

    # ── Resolve target list ────────────────────────────────────────────
    if args.all_countries:
        countries_path = REPO_ROOT / "intelligence" / "countries.json"
        cohort = json.loads(countries_path.read_text())
        targets = cohort.get("slugs", [])
        if not targets:
            log.error("intelligence/countries.json has no 'slugs' key")
            sys.exit(2)
    elif args.slug:
        targets = [args.slug]
    else:
        ap.error("must pass a slug OR --all-countries")

    # ── Load raster once + run enrichment ──────────────────────────────
    log.info(f"Task #451 Step 4 execution — {len(targets)} countries")
    raster = GHSLRaster(args.raster)
    all_audits = []
    for slug in targets:
        try:
            audit = enrich_country(
                slug, raster,
                radius_km=args.radius_km,
                dry_run=args.dry_run,
                force_rewrite=args.force_rewrite,
            )
            all_audits.append(audit)
            _print_report(audit)
        except Exception as e:  # noqa: BLE001
            log.error(f"[{slug}] FAILED: {e}")
            import traceback
            traceback.print_exc()
    raster.close()

    # ── Emit consolidated audit report ─────────────────────────────────
    if all_audits:
        ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        report_path = Path.home() / f"catchment_population_audit_{ts}.json"
        report_path.write_text(json.dumps({
            "task_id": 451,
            "step": 4,
            "run_timestamp_utc": ts,
            "mode": "dry-run" if args.dry_run else "applied",
            "force_rewrite": args.force_rewrite,
            "radius_km": args.radius_km,
            "raster_source": "GHSL_POP_R2023A_E2025",
            "n_countries": len(all_audits),
            "audits": all_audits,
        }, indent=2))
        print(f"\n✓ Consolidated audit report: {report_path}")


def _print_report(audit: dict) -> None:
    """Print a human-readable per-country enrichment summary."""
    n = audit["n_substations"]
    print(f"\n─── {audit['country']} ({n:,} subs, {audit['wall_clock_sec']}s) ───")
    print(f"  n_written (real GHSL):       {audit['n_written']:>7,}")
    print(f"  n_none (Convention #56):     {audit['n_none_convention_56']:>7,}")
    print(f"  n_skipped (already had val): {audit['n_skipped_existing']:>7,}")
    print(f"  n_missing_coords:            {audit['n_missing_coords']:>7,}")
    if audit["force_rewrite"]:
        print(f"  synthetic retired:           {audit['delta_from_synthetic']:>7,}")


if __name__ == "__main__":
    main()
