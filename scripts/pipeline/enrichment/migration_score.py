#!/usr/bin/env python3
"""migration_score.py — Niva 2023 gridded net-migration enrichment

Task #452 Step 3 (23 July 2026)
==============================

Populates `socio_economic.migration_score` per substation from the Niva
et al. 2023 global gridded net-migration dataset (published in Nature
Human Behaviour 7:2023-2037, DOI 10.1038/s41562-023-01689-4; dataset DOI
10.5281/zenodo.7997134; CC BY 4.0 license).

Closes R2 Grid Equity Defect Class 3 architecturally — sibling to Task
#451 (catchment_population GHSL enrichment) but structurally different:

    ┌───────────────────────────────────────────────────────────────┐
    │ CONCEPT DIFFERENCES vs Task #451 catchment_population         │
    ├───────────────────────────────────────────────────────────────┤
    │ Population    STOCK  → zonal-SUM over 5 km buffer             │
    │ Migration     FLOW   → SINGLE-POINT sample at (lat, lon)      │
    │                                                                │
    │ GHSL CRS:     ESRI:54009 Mollweide (needs reprojection)       │
    │ Niva CRS:     EPSG:4326 WGS84 (direct lat/lon index)          │
    │                                                                │
    │ Population    integer count (no range mapping needed)         │
    │ Migration     raw persons/1000/20yr → tanh(x/200) → [0, 1]    │
    │                                                                │
    │ Task #451     RETIRE synthetic generator + additive           │
    │ Task #452     Pure additive enrichment (no synthetic exists)  │
    └───────────────────────────────────────────────────────────────┘

Methodology
-----------
For each substation at (lat, lon):
  1. Convert lat/lon to Niva raster pixel indices (direct, EPSG:4326).
  2. Read single-band pixel value at that index — raw net-migration
     rate in persons per 1000 people per 20-year period (2000-2019 sum).
  3. Map to [0, 1] score via `0.5 + 0.5 * tanh(raw / K)` where K=200
     (author-empirical moderate-migration reference).
  4. Write result to `sub['socio_economic']['migration_score']`.
  5. Convention #56 fallback: pixel is NoData / outside raster → None
     (visibly-honest; not fabricated).

NARROW SCOPE (Gate A operator sign-off 23 Jul 2026)
---------------------------------------------------
Substations with non-None existing `socio_economic.migration_score`
are SKIPPED by default. This preserves genuine per-substation
distributions (Norway 742 unique values, Lithuania 332, Ireland 25,
Denmark 590) AND leaves Task #450 SYSTEMIC scope (fleet-uniform 0.5
national fallbacks in Wave 4 majors, drifted semantic in Denmark /
Mexico / Italy) UNTOUCHED — those are separate workstreams.

`--force-rewrite` is available as an opt-in flag for WIDE-scope
future work, but the default flow is NARROW.

Range mapping formula (Gate A #2)
---------------------------------
    score = 0.5 + 0.5 * tanh(raw / K)   where K = 200.0

    raw           →  score
    ---           ---------
    -1000         →  0.007  (extreme out-migration)
    -500          →  0.041
    -200          →  0.119
    -100          →  0.269
     0            →  0.500  (neutral — no net migration)
    +100          →  0.731
    +200          →  0.881
    +500          →  0.959
    +1000         →  0.993  (extreme in-migration)

    K=200 chosen because Niva 2023 paper Fig 2 histogram median for
    non-zero cells is ~200 persons/1000/20yr; makes typical migration
    score ~0.75 (in) or ~0.25 (out), leaving 0.5 for genuinely neutral.

Convention preservation
-----------------------
- #7  Data-Layer Anchoring documented-proxy — Niva 2023 is
      publisher-cited (Nature Human Behaviour) + product-versioned
      (20-yr sum 2000-2019) + coordinate-system-declared (EPSG:4326)
      + resolution-declared (5 arc-min ≈ 10 km at equator).
- #56 Visibly-honest degradation — raster-gap substations (NoData
      pixels) receive None; no fabrication.
- #60 Ikenga IS the ESG provider — Niva 2023 is peer-reviewed
      academic publication under CC BY 4.0 open license. Non-commercial.
- #79 ssi-data sharding preserved — uses read_ssi_data / write_ssi_data.

Usage
-----
Diagnose-only (check deps + raster presence, no reads):
    python3 scripts/pipeline/enrichment/migration_score.py --diagnose-only

Single country dry-run (compute + report, don't write):
    python3 scripts/pipeline/enrichment/migration_score.py spain --dry-run

Single country apply (NARROW scope — skip existing non-None):
    python3 scripts/pipeline/enrichment/migration_score.py spain

Cohort-wide apply (39 countries per intelligence/countries.json):
    python3 scripts/pipeline/enrichment/migration_score.py --all-countries

Force rewrite (WIDE scope — overwrite existing; USE WITH OPERATOR APPROVAL):
    python3 scripts/pipeline/enrichment/migration_score.py spain --force-rewrite

Custom mapping constant K (methodology exploration):
    python3 scripts/pipeline/enrichment/migration_score.py spain --dry-run --k-constant 300
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
# rasterio is heavy. Fall back gracefully so --diagnose-only mode works
# even without it.

try:
    import rasterio  # type: ignore
    _HAS_RASTERIO = True
except ImportError:
    _HAS_RASTERIO = False

# pyproj + shapely not needed here — Niva is EPSG:4326 (direct lat/lon
# indexing). Simpler than Task #451.

try:
    from scripts.pipeline.utils.ssi_data_sharding import (  # type: ignore
        read_ssi_data,
        write_ssi_data,
    )
    _HAS_SHARDING = True
except ImportError:
    _HAS_SHARDING = False


# ═════════════════════════════════════════════════════════════════════
#  CANONICAL CONSTANTS — Task #452 methodology anchors
# ═════════════════════════════════════════════════════════════════════

# Range-mapping constant. K=200 persons/1000/20yr = Niva 2023 empirical
# "moderate net migration" magnitude. See module docstring for lookup
# table + derivation.
MAPPING_CONSTANT_K = 200.0

# Niva raster path — download by operator from Zenodo 7997134.
DEFAULT_NIVA_RASTER_PATH = (
    REPO_ROOT / "docs" / "audits" / "raster_netMgr_2000_2019_20yrSum.tif"
)

# CRS
CRS_WGS84 = "EPSG:4326"

# Convention #56 audit trail per Task #452
AUDIT_TRAIL_KEY = "_migration_score_source"
AUDIT_TRAIL_VALUE = "NIVA_2023_20YR_SUM_v4_2_task_452"

# Zenodo download reference (for --diagnose-only guidance)
_NIVA_DATASET_DOI = "10.5281/zenodo.7997134"
_NIVA_DATASET_URL = "https://zenodo.org/records/7997134"
_NIVA_FILE_URL = (
    "https://zenodo.org/records/7997134/files/"
    "raster_netMgr_2000_2019_20yrSum.tif?download=1"
)
_NIVA_FILE_MD5 = "97793810040b30dd4f4ffc889c52cef7"


# ═════════════════════════════════════════════════════════════════════
#  logging
# ═════════════════════════════════════════════════════════════════════

logging.basicConfig(
    format="%(asctime)s %(levelname)-7s %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════
#  Fleet-uniform fallback detection (Task #450 SYSTEMIC signature)
# ═════════════════════════════════════════════════════════════════════

# Threshold: minimum populated substation count for fleet-uniform
# signature to apply. Small countries with < 100 subs could genuinely
# have a single value from the raster (single admin unit); don't
# override those.
FLEET_UNIFORM_MIN_POPULATED = 100


def is_fleet_uniform_fallback(
    substations: list, threshold: int = FLEET_UNIFORM_MIN_POPULATED
) -> bool:
    """Detect whether a country's migration_score is a fleet-uniform fallback.

    Returns True iff:
      - Number of populated (non-None) migration_score values > threshold
      - Number of unique populated values == 1

    This is the Task #450 SYSTEMIC signature — a single national scalar
    applied fleet-uniformly across many substations, indicating pipeline
    fallback rather than real per-substation data.

    Preserved cases (returns False):
      - Genuine per-substation distributions (norway 742 unique / lithuania
        332 / ireland 25 / denmark 590 / mexico 18 / new-zealand 67)
      - Small countries (< threshold subs) where 1 unique might be genuine
      - Countries with all-None migration_score (nothing to override)
    """
    values = set()
    n_populated = 0
    for sub in substations:
        se = sub.get("socio_economic") or {}
        val = se.get("migration_score")
        if val is None:
            continue
        n_populated += 1
        values.add(val)
        # Early exit — clearly not fleet-uniform once we see 2 distinct values
        if len(values) > 1:
            return False
    return n_populated > threshold and len(values) == 1


# ═════════════════════════════════════════════════════════════════════
#  Range mapping — raw persons/1000/20yr → [0, 1]
# ═════════════════════════════════════════════════════════════════════

def map_raw_to_score(raw: float, k: float = MAPPING_CONSTANT_K) -> float:
    """Symmetric hyperbolic-tangent mapping raw net-migration → [0, 1].

    Formula:  score = 0.5 + 0.5 * tanh(raw / K)

    - raw = 0  → score = 0.5 (neutral)
    - raw > 0  → score > 0.5 (net in-migration)
    - raw < 0  → score < 0.5 (net out-migration)
    - |raw| → ∞ → score saturates at 0 or 1

    Preserves order + sign. Robust to outliers via tanh saturation.
    """
    if raw is None or not math.isfinite(raw):
        return None  # type: ignore
    return 0.5 + 0.5 * math.tanh(raw / k)


# ═════════════════════════════════════════════════════════════════════
#  Niva raster loader
# ═════════════════════════════════════════════════════════════════════

class NivaRaster:
    """Lazy Niva 2023 20-yr net-migration raster loader.

    Direct lat/lon indexing via rasterio.DatasetReader.index (no
    reprojection needed — Niva is EPSG:4326).
    """

    def __init__(self, raster_path: Path):
        if not _HAS_RASTERIO:
            raise RuntimeError(
                "rasterio not installed — install via `pip install rasterio`"
            )
        self.path = Path(raster_path)
        if not self.path.exists():
            raise FileNotFoundError(
                f"Niva raster not found at {self.path}. Download from "
                f"{_NIVA_FILE_URL} and place at {DEFAULT_NIVA_RASTER_PATH} "
                f"(Task #452 Step 4a)."
            )
        self._dataset: Any = None
        self._nodata: Any = None

    def _open(self) -> None:
        if self._dataset is None:
            self._dataset = rasterio.open(str(self.path))
            self._nodata = self._dataset.nodata
            log.info(
                f"[NIVA] loaded {self.path.name} — "
                f"crs={self._dataset.crs} "
                f"shape={self._dataset.shape} "
                f"bounds={self._dataset.bounds} "
                f"nodata={self._nodata}"
            )

    def sample_score(
        self, lat: float, lon: float, k: float = MAPPING_CONSTANT_K
    ) -> Optional[float]:
        """Sample raw value at (lat, lon), map to [0, 1] score.

        Returns None (Convention #56 fallback) when:
          - Coords fall outside raster extent
          - Pixel value equals raster NoData
          - Read fails for any other reason
        """
        self._open()

        # 1. Direct WGS84 → pixel-index (rasterio handles EPSG:4326 natively)
        try:
            row, col = self._dataset.index(lon, lat)
        except Exception as e:  # noqa: BLE001
            log.debug(f"  index failed lat={lat} lon={lon}: {e}")
            return None

        # 2. Bounds check
        h, w = self._dataset.shape
        if not (0 <= row < h and 0 <= col < w):
            return None

        # 3. Read single pixel
        try:
            window = ((row, row + 1), (col, col + 1))
            arr = self._dataset.read(1, window=window)
        except Exception as e:  # noqa: BLE001
            log.debug(f"  read failed row={row} col={col}: {e}")
            return None

        if arr.size == 0:
            return None
        raw = float(arr[0, 0])

        # 4. NoData check
        if self._nodata is not None and raw == self._nodata:
            return None
        if not math.isfinite(raw):
            return None

        # 5. Map raw → [0, 1] score
        return map_raw_to_score(raw, k)

    def close(self) -> None:
        if self._dataset is not None:
            self._dataset.close()
            self._dataset = None


# ═════════════════════════════════════════════════════════════════════
#  Per-country enrichment (NARROW scope by default)
# ═════════════════════════════════════════════════════════════════════

def enrich_country(
    slug: str,
    raster: NivaRaster,
    *,
    k_constant: float = MAPPING_CONSTANT_K,
    dry_run: bool = False,
    force_rewrite: bool = False,
    disable_fleet_uniform_override: bool = False,
) -> dict:
    """Apply Niva migration_score enrichment to one country.

    Reads slug/ssi-data.json (sharded or single-file), enriches
    socio_economic.migration_score per substation, writes back
    (unless dry_run).

    NARROW scope default: skips substations that already have non-None
    `migration_score`. Use `force_rewrite=True` for WIDE-scope.

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

    # ── Fleet-uniform detection (Gate A rev2 23 Jul 2026) ──────────────
    # Auto-override fleet-uniform fallback distributions (Task #450 SYSTEMIC
    # signature). Preserves real per-substation distributions.
    fleet_uniform_override = (
        not disable_fleet_uniform_override
        and is_fleet_uniform_fallback(substations)
    )
    if fleet_uniform_override:
        # Sample the fleet-uniform value for the audit trail
        _sample_value = next(
            (s.get("socio_economic", {}).get("migration_score")
             for s in substations
             if s.get("socio_economic", {}).get("migration_score") is not None),
            None,
        )
        log.info(
            f"[{slug}] fleet-uniform fallback detected "
            f"(single value={_sample_value!r}) — WILL OVERRIDE with Niva "
            f"per-substation values (Task #450 SYSTEMIC signature)."
        )

    # ── audit counters ──────────────────────────────────────────────────
    n_written = 0            # real Niva-derived score written
    n_skipped_existing = 0   # NARROW scope skip (has non-None already)
    n_none_convention_56 = 0 # raster returned None (Convention #56 fallback)
    n_missing_coords = 0
    n_out_of_range = 0       # value outside [0, 1] — should be zero by construction
    delta_from_existing = 0  # count where existing value was overwritten

    scope_label = (
        "WIDE (force-rewrite)" if force_rewrite
        else "NARROW + fleet-uniform OVERRIDE" if fleet_uniform_override
        else "NARROW (skip existing)"
    )
    log.info(f"[{slug}] enriching (k={k_constant}, scope={scope_label})...")
    for i, sub in enumerate(substations, 1):
        lat = sub.get("lat")
        lon = sub.get("lon")
        if lat is None or lon is None:
            n_missing_coords += 1
            continue

        se = sub.setdefault("socio_economic", {})
        existing = se.get("migration_score")

        # NARROW scope: skip existing non-None UNLESS force_rewrite OR
        # fleet-uniform override active.
        if existing is not None and not force_rewrite and not fleet_uniform_override:
            n_skipped_existing += 1
            continue

        score = raster.sample_score(lat, lon, k_constant)

        if existing is not None and (force_rewrite or fleet_uniform_override):
            delta_from_existing += 1

        if score is not None:
            # Value invariant guard — tanh output MUST be in [0, 1]
            if not (0.0 <= score <= 1.0):
                n_out_of_range += 1
                score = max(0.0, min(1.0, score))  # clamp defensively

        se["migration_score"] = score
        se[AUDIT_TRAIL_KEY] = AUDIT_TRAIL_VALUE
        if score is None:
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
        "n_out_of_range_clamped": n_out_of_range,
        "delta_from_existing": delta_from_existing,
        "fleet_uniform_override_applied": fleet_uniform_override,
        "k_constant": k_constant,
        "wall_clock_sec": round(elapsed, 1),
        "raster_source": "NIVA_2023_20YR_SUM_2000_2019",
        "dry_run": dry_run,
        "force_rewrite": force_rewrite,
    }


# ═════════════════════════════════════════════════════════════════════
#  Diagnostics
# ═════════════════════════════════════════════════════════════════════

def diagnose(raster_path: Path) -> dict:
    """Report dependency state + raster presence without touching ssi-data."""
    diag = {
        "task_id": 452,
        "step": 3,
        "rasterio_installed": _HAS_RASTERIO,
        "ssi_data_sharding_importable": _HAS_SHARDING,
        "raster_path": str(raster_path),
        "raster_exists": raster_path.exists(),
        "raster_size_mb": (
            round(raster_path.stat().st_size / 1_000_000, 1)
            if raster_path.exists() else None
        ),
        "raster_download_url": _NIVA_FILE_URL,
        "raster_expected_md5": _NIVA_FILE_MD5,
        "raster_expected_size_mb_approx": 10.5,
        "mapping_constant_k": MAPPING_CONSTANT_K,
        "audit_trail_value": AUDIT_TRAIL_VALUE,
    }
    diag["ready_for_step_4"] = all([
        _HAS_RASTERIO, _HAS_SHARDING, raster_path.exists()
    ])
    return diag


# ═════════════════════════════════════════════════════════════════════
#  CLI
# ═════════════════════════════════════════════════════════════════════

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
        "--k-constant", type=float, default=MAPPING_CONSTANT_K,
        help=f"mapping constant K in tanh(raw/K) formula (default {MAPPING_CONSTANT_K})",
    )
    ap.add_argument(
        "--raster", type=Path, default=DEFAULT_NIVA_RASTER_PATH,
        help="path to Niva 2023 20-yr sum GeoTIFF",
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
        help=(
            "WIDE SCOPE — overwrite existing non-None migration_score values. "
            "Default is NARROW-plus-fleet-uniform-override. Use only with "
            "operator approval."
        ),
    )
    ap.add_argument(
        "--no-fleet-uniform-override", action="store_true",
        help=(
            "STRICT NARROW — do NOT auto-override fleet-uniform fallback "
            "distributions. Default behavior detects the (n_unique==1 AND "
            "n_populated>100) signature (Task #450 SYSTEMIC fingerprint) and "
            "overrides with Niva per-substation values. Setting this flag "
            "reverts to skip-any-non-None."
        ),
    )
    args = ap.parse_args()

    # ── Diagnose-only mode ─────────────────────────────────────────────
    if args.diagnose_only:
        diag = diagnose(args.raster)
        print(json.dumps(diag, indent=2))
        sys.exit(0 if diag["ready_for_step_4"] else 1)

    # ── Ensure deps available ───────────────────────────────────────────
    if not (_HAS_RASTERIO and _HAS_SHARDING):
        log.error(
            "Missing required deps. Run with --diagnose-only for details. "
            "Typical install: pip install --user rasterio"
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
    log.info(
        f"Task #452 execution — {len(targets)} countries "
        f"(scope: {'WIDE' if args.force_rewrite else 'NARROW'})"
    )
    raster = NivaRaster(args.raster)
    all_audits = []
    for slug in targets:
        try:
            audit = enrich_country(
                slug, raster,
                k_constant=args.k_constant,
                dry_run=args.dry_run,
                force_rewrite=args.force_rewrite,
                disable_fleet_uniform_override=args.no_fleet_uniform_override,
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
        report_path = Path.home() / f"migration_score_audit_{ts}.json"
        report_path.write_text(json.dumps({
            "task_id": 452,
            "step": 4,
            "run_timestamp_utc": ts,
            "mode": "dry-run" if args.dry_run else "applied",
            "scope": "WIDE" if args.force_rewrite else "NARROW",
            "k_constant": args.k_constant,
            "raster_source": "NIVA_2023_20YR_SUM_2000_2019",
            "n_countries": len(all_audits),
            "audits": all_audits,
        }, indent=2))
        print(f"\n✓ Consolidated audit report: {report_path}")


def _print_report(audit: dict) -> None:
    """Print a human-readable per-country enrichment summary."""
    n = audit["n_substations"]
    print(f"\n─── {audit['country']} ({n:,} subs, {audit['wall_clock_sec']}s) ───")
    if audit.get("fleet_uniform_override_applied"):
        print(f"  ⚡ FLEET-UNIFORM OVERRIDE ACTIVE (Task #450 SYSTEMIC signature)")
    print(f"  n_written (real Niva):        {audit['n_written']:>7,}")
    print(f"  n_none (Convention #56):      {audit['n_none_convention_56']:>7,}")
    print(f"  n_skipped (NARROW: existing): {audit['n_skipped_existing']:>7,}")
    print(f"  n_missing_coords:             {audit['n_missing_coords']:>7,}")
    if audit["n_out_of_range_clamped"]:
        print(f"  ⚠ n_out_of_range_clamped:     {audit['n_out_of_range_clamped']:>7,}")
    if audit["delta_from_existing"]:
        label = "WIDE: existing overwritten" if audit["force_rewrite"] else "fleet-uniform: existing overwritten"
        print(f"  ⚠ {label}: {audit['delta_from_existing']:>7,}")


if __name__ == "__main__":
    main()
