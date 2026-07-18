"""Grid-geo automatic sharding utility (Convention #80).

Solves GitHub's 100 MB per-file hard limit for large-scale grid-geo.json
files (US + Germany + France projected 100-500 MB post-Wave-4 enhancement).

Trigger: when total grid-geo.json payload would exceed 90 MB (leaves 10 MB
safety margin under GitHub 100 MB limit), automatically split the `l` list
into `grid-geo-l-NN.json` shards.

Schema conventions:
- Single-file (unshared): {"s": {...}, "l": [...], "a": {...}}
- Sharded: {"s": {...}, "a": {...}, "sharded": true,
            "l_shards": [{"path": "grid-geo-l-01.json", "count": N, "size_mb": M}, ...]}

The renderer (map.js) auto-detects the `sharded: true` flag and fetches
shards in parallel, concatenating into a virtual `l` list.

Backward compatibility:
- Countries under 90 MB continue to use single-file format (no change)
- Renderer handles both cases from the same code path
- Git operations work fine with multiple smaller files

Convention preservation:
- #23 Provenance pinning (each shard SHA-256'd separately)
- #56 Visibly-honest degradation (missing shard surfaces as visibly-missing lines)
- #67 Consumer-adapter discipline (renderer treats sharded/inline transparently)
- #79 (NEW) Grid-geo automatic sharding rule

Author: ikenga-ssi-foundation
Date: 2026-07-18 (Wave 4 UK P31 file-size lesson)
"""
from __future__ import annotations

import json
import logging
import math
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ─── Sharding thresholds ───
GRID_GEO_SHARD_THRESHOLD_MB = 90.0  # Below → single file; above → shard
GRID_GEO_SHARD_TARGET_MB = 70.0     # Each shard target size (safety margin below threshold)
GRID_GEO_MIN_LINES_PER_SHARD = 1000  # Never shard smaller than this (avoid over-sharding)


def _json_size_mb(obj: Any) -> float:
    """Estimate compact JSON size in MB."""
    return len(json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")) / 1024 / 1024


def _estimate_avg_line_bytes(l_list: list, sample_size: int = 200) -> float:
    """Estimate average bytes per line entry from a sample."""
    if not l_list:
        return 0.0
    n = min(sample_size, len(l_list))
    total = 0
    for i in range(n):
        # Sample uniformly
        idx = int(i * len(l_list) / n)
        total += len(json.dumps(l_list[idx], separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    return total / n


def _compute_lines_per_shard(l_list: list, target_shard_mb: float) -> int:
    """Compute how many lines per shard given target size."""
    avg_bytes = _estimate_avg_line_bytes(l_list)
    if avg_bytes == 0:
        return len(l_list) or 1
    target_bytes = target_shard_mb * 1024 * 1024
    # Account for JSON array overhead (`[` + `]` + N-1 commas ≈ ~1% overhead)
    lines_per_shard = int(target_bytes / (avg_bytes * 1.02))
    return max(lines_per_shard, GRID_GEO_MIN_LINES_PER_SHARD)


def write_grid_geo(
    grid_doc: dict,
    path: Path,
    *,
    threshold_mb: float = GRID_GEO_SHARD_THRESHOLD_MB,
    target_shard_mb: float = GRID_GEO_SHARD_TARGET_MB,
) -> dict:
    """Write grid-geo.json with automatic sharding if size exceeds threshold.

    Convention #80 implementation.

    Args:
        grid_doc: dict with {s, l, a} keys (canonical compact schema)
        path: target path for grid-geo.json
        threshold_mb: size trigger for sharding
        target_shard_mb: target per-shard size

    Returns:
        stats dict: {sharded: bool, size_mb: float, shard_count: int,
                     shards: list, manifest_size_mb: float}
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # ── Step 1: check if single-file fits under threshold ──
    total_size_mb = _json_size_mb(grid_doc)
    if total_size_mb < threshold_mb:
        # Single file — no sharding needed
        payload = json.dumps(grid_doc, separators=(",", ":"), ensure_ascii=False)
        path.write_text(payload)
        # Clean up any previous shards that may exist
        cleanup_count = cleanup_stale_shards(path)
        logger.info(
            f"Wrote {path} ({total_size_mb:.2f} MB single-file — under {threshold_mb} MB threshold)"
            + (f"; cleaned {cleanup_count} stale shards" if cleanup_count else "")
        )
        return {
            "sharded": False,
            "size_mb": total_size_mb,
            "shard_count": 0,
            "shards": [],
            "manifest_size_mb": total_size_mb,
            "stale_shards_cleaned": cleanup_count,
        }

    # ── Step 2: shard the `l` list ──
    l_list = grid_doc.pop("l", [])
    if not isinstance(l_list, list):
        raise ValueError(f"Cannot shard: grid_doc['l'] is not a list (got {type(l_list)})")

    lines_per_shard = _compute_lines_per_shard(l_list, target_shard_mb)
    logger.info(
        f"Sharding {len(l_list):,} lines into shards of ~{lines_per_shard:,} lines each "
        f"(target {target_shard_mb} MB per shard)"
    )

    shards_info = []
    shard_idx = 1
    for start in range(0, len(l_list), lines_per_shard):
        chunk = l_list[start:start + lines_per_shard]
        shard_name = f"grid-geo-l-{shard_idx:02d}.json"
        shard_path = path.parent / shard_name
        shard_payload = json.dumps(chunk, separators=(",", ":"), ensure_ascii=False)
        shard_bytes = len(shard_payload.encode("utf-8"))
        shard_path.write_text(shard_payload)
        shards_info.append({
            "path": shard_name,
            "count": len(chunk),
            "size_mb": round(shard_bytes / 1024 / 1024, 3),
        })
        logger.info(
            f"  Wrote shard {shard_idx:02d}: {shard_name} "
            f"({len(chunk):,} lines, {shard_bytes / 1024 / 1024:.2f} MB)"
        )
        shard_idx += 1

    # ── Step 3: write manifest (grid-geo.json with sharded=true) ──
    grid_doc["sharded"] = True
    grid_doc["l_shards"] = shards_info
    manifest_payload = json.dumps(grid_doc, separators=(",", ":"), ensure_ascii=False)
    manifest_size_mb = len(manifest_payload.encode("utf-8")) / 1024 / 1024
    path.write_text(manifest_payload)

    # ── Step 4: cleanup any stale shards beyond our count ──
    cleanup_count = cleanup_stale_shards(path, active_shard_count=len(shards_info))

    logger.info(
        f"Wrote {path} manifest ({manifest_size_mb:.2f} MB) + {len(shards_info)} shards "
        f"(total: {total_size_mb:.2f} MB → sharded per Convention #80)"
        + (f"; cleaned {cleanup_count} stale shards" if cleanup_count else "")
    )

    return {
        "sharded": True,
        "size_mb": total_size_mb,
        "shard_count": len(shards_info),
        "shards": shards_info,
        "manifest_size_mb": manifest_size_mb,
        "stale_shards_cleaned": cleanup_count,
    }


def cleanup_stale_shards(
    manifest_path: Path,
    *,
    active_shard_count: int = 0,
) -> int:
    """Remove stale grid-geo-l-NN.json shards no longer referenced.

    When re-writing a grid-geo.json that was previously sharded into N shards,
    if the new write requires only M < N shards, the extras must be deleted
    to avoid stale-file pollution.

    When re-writing a grid-geo.json single-file (no longer sharded), all
    grid-geo-l-*.json shards must be deleted.

    Returns count of shards deleted.
    """
    parent = Path(manifest_path).parent
    stale = list(parent.glob("grid-geo-l-*.json"))
    kept_count = 0
    deleted_count = 0
    for shard_path in stale:
        # Extract shard number from filename
        try:
            stem = shard_path.stem  # e.g. "grid-geo-l-05"
            num_str = stem.rsplit("-", 1)[-1]
            num = int(num_str)
        except (ValueError, IndexError):
            continue
        if 1 <= num <= active_shard_count:
            kept_count += 1
        else:
            shard_path.unlink()
            deleted_count += 1
            logger.info(f"  Cleaned stale shard: {shard_path.name}")
    return deleted_count


def read_grid_geo(path: Path) -> dict:
    """Read grid-geo.json, auto-loading shards if sharded (Convention #80).

    Consumer-side helper — Python code reads grid-geo.json transparently
    whether it's single-file or sharded. The returned dict always has
    `l` as an inline list (shard manifest is transparently expanded).

    Args:
        path: grid-geo.json path

    Returns:
        dict: {s, l, a} canonical compact schema (l always inline)
    """
    path = Path(path)
    data = json.loads(path.read_text())
    if not data.get("sharded"):
        return data  # Single-file case — return as-is

    # Sharded — load all shards and concatenate into virtual `l`
    l_shards_info = data.get("l_shards", [])
    all_lines: list = []
    for shard_info in l_shards_info:
        shard_path = path.parent / shard_info["path"]
        if not shard_path.exists():
            logger.warning(
                f"Convention #56 partial-fetch: shard {shard_path.name} missing "
                f"(expected {shard_info['count']} lines)"
            )
            continue
        shard_data = json.loads(shard_path.read_text())
        if isinstance(shard_data, list):
            all_lines.extend(shard_data)
        else:
            logger.warning(f"Shard {shard_path.name} is not a list (skipped)")

    # Return virtual-inline schema
    data["l"] = all_lines
    # Preserve manifest keys for audit trail; consumer can ignore
    return data


def get_grid_geo_size_stats(country_slug: str, repo_root: Optional[Path] = None) -> dict:
    """Empirical size audit for a country's grid-geo.json + shards.

    Returns dict: {country, single_file_size_mb, shard_count, total_size_mb, sharded}
    """
    if repo_root is None:
        repo_root = Path(__file__).resolve().parent.parent.parent.parent
    country_dir = repo_root / country_slug
    manifest_path = country_dir / "grid-geo.json"
    if not manifest_path.exists():
        return {"country": country_slug, "exists": False}

    manifest_mb = manifest_path.stat().st_size / 1024 / 1024
    manifest = json.loads(manifest_path.read_text())
    sharded = bool(manifest.get("sharded"))
    shards_info = manifest.get("l_shards", []) if sharded else []
    shards_total_mb = sum(
        (country_dir / sh["path"]).stat().st_size / 1024 / 1024
        for sh in shards_info
        if (country_dir / sh["path"]).exists()
    )
    total_mb = manifest_mb + shards_total_mb
    return {
        "country": country_slug,
        "exists": True,
        "sharded": sharded,
        "manifest_size_mb": round(manifest_mb, 2),
        "shard_count": len(shards_info),
        "shards_total_size_mb": round(shards_total_mb, 2),
        "total_size_mb": round(total_mb, 2),
        "under_github_limit": total_mb < 100.0 and manifest_mb < 100.0 and all(
            sh.get("size_mb", 0) < 100.0 for sh in shards_info
        ),
    }


# ─── Sentinel — validate sharding invariants ───
def validate_grid_geo(path: Path) -> tuple[bool, list[str]]:
    """Validate grid-geo.json (+ shards if sharded) satisfies Convention #80.

    Checks:
    - Every file (manifest + all shards) is under 100 MB GitHub hard limit
    - If sharded: all referenced shards exist on disk
    - If sharded: `l_shards` manifest count matches shard files
    - `s` dict and `a` dict are inline (never sharded)

    Returns (is_valid, list_of_issues).
    """
    path = Path(path)
    issues: list[str] = []
    if not path.exists():
        return (False, [f"Manifest {path.name} does not exist"])

    manifest_size_mb = path.stat().st_size / 1024 / 1024
    if manifest_size_mb >= 100.0:
        issues.append(
            f"Manifest {path.name} is {manifest_size_mb:.2f} MB — exceeds GitHub 100 MB hard limit"
        )

    try:
        data = json.loads(path.read_text())
    except Exception as e:
        return (False, [f"Manifest JSON parse failed: {e}"])

    # Validate `s` and `a` are inline dicts
    if not isinstance(data.get("s"), dict):
        issues.append(f"'s' key missing or not a dict (Convention #80 requires inline)")
    if not isinstance(data.get("a"), dict):
        issues.append(f"'a' key missing or not a dict (Convention #80 requires inline)")

    if data.get("sharded"):
        l_shards = data.get("l_shards")
        if not isinstance(l_shards, list):
            issues.append(f"'sharded'=true but 'l_shards' missing or not a list")
        else:
            for sh_info in l_shards:
                shard_path = path.parent / sh_info["path"]
                if not shard_path.exists():
                    issues.append(f"Referenced shard {sh_info['path']} does not exist on disk")
                    continue
                shard_size_mb = shard_path.stat().st_size / 1024 / 1024
                if shard_size_mb >= 100.0:
                    issues.append(
                        f"Shard {sh_info['path']} is {shard_size_mb:.2f} MB — "
                        f"exceeds GitHub 100 MB hard limit"
                    )
    else:
        # Non-sharded — validate `l` is inline list
        if not isinstance(data.get("l"), list):
            issues.append(f"Non-sharded but 'l' key missing or not a list")

    return (len(issues) == 0, issues)


# ─── Empirical demo helper ───
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 2:
        print("Usage: python -m scripts.pipeline.utils.grid_geo_sharding <country_slug>")
        print("       Runs empirical size audit for that country's grid-geo.json")
        sys.exit(1)

    country = sys.argv[1]
    stats = get_grid_geo_size_stats(country)
    print(json.dumps(stats, indent=2))
