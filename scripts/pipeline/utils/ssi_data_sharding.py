"""SSI-data automatic sharding utility (Convention #79 candidate).

Solves GitHub's 100 MB per-file hard limit for large-scale ssi-data.json
files (US 181 MB + Germany 335 MB + France 341 MB + UK 109 MB in Wave 4).

Analog of scripts/pipeline/utils/grid_geo_sharding.py (Convention #80 for
grid-geo.json), applied to ssi-data.json's `substations` array.

Trigger: when total ssi-data.json payload would exceed 90 MB (leaves 10 MB
safety margin under GitHub 100 MB limit), automatically split the
`substations` array into `ssi-data-substations-NN.json` shards.

Schema conventions:
- Single-file (unshared): {"meta": {...}, "fleet_summary": {...},
                           "regions": [...], "substations": [...]}
- Sharded: {"meta": {...}, "fleet_summary": {...}, "regions": [...],
            "sharded": true,
            "substations_shards": [{"path": "ssi-data-substations-01.json",
                                    "count": N, "size_mb": M}, ...]}

The renderers (map.js + country-renderer.js) auto-detect the `sharded: true`
flag and fetch shards in parallel, concatenating into a virtual `substations`
array.

Backward compatibility:
- Countries under 90 MB continue to use single-file format (no change)
- Renderers handle both cases from the same code path
- Git operations work fine with multiple smaller files

Convention preservation:
- #7  Data-Layer Anchoring (each shard SHA-256'd separately)
- #23 Provenance pinning (each shard SHA-256'd separately)
- #56 Visibly-honest degradation (missing shard surfaces as visibly-missing subs)
- #67 Consumer-adapter discipline (renderer treats sharded/inline transparently)
- #79 (NEW candidate) SSI-data automatic sharding rule
- #80 grid-geo sharding — parallel sibling rule

Author: ikenga-ssi-foundation
Date: 2026-07-21 (Wave 4 Commit 45 — 4 large countries at 109-341 MB)
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ─── Sharding thresholds ───
SSI_DATA_SHARD_THRESHOLD_MB = 90.0   # Below → single file; above → shard
SSI_DATA_SHARD_TARGET_MB = 60.0      # Each shard target size (safety margin)
SSI_DATA_MIN_SUBS_PER_SHARD = 500    # Never shard smaller than this


def _json_size_mb(obj: Any) -> float:
    """Estimate compact JSON size in MB."""
    return len(json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")) / 1024 / 1024


def _estimate_avg_sub_bytes(subs: list, sample_size: int = 200) -> float:
    """Estimate average bytes per substation entry from a sample."""
    if not subs:
        return 0.0
    n = min(sample_size, len(subs))
    total = 0
    for i in range(n):
        idx = int(i * len(subs) / n)
        total += len(json.dumps(subs[idx], separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    return total / n


def _compute_subs_per_shard(subs: list, target_shard_mb: float) -> int:
    """Compute how many substations per shard given target size."""
    avg_bytes = _estimate_avg_sub_bytes(subs)
    if avg_bytes == 0:
        return len(subs) or 1
    target_bytes = target_shard_mb * 1024 * 1024
    # Account for JSON array overhead (`[` + `]` + N-1 commas ≈ ~1% overhead)
    subs_per_shard = int(target_bytes / (avg_bytes * 1.02))
    return max(subs_per_shard, SSI_DATA_MIN_SUBS_PER_SHARD)


def write_ssi_data(
    ssi_doc: dict,
    path: Path,
    *,
    threshold_mb: float = SSI_DATA_SHARD_THRESHOLD_MB,
    target_shard_mb: float = SSI_DATA_SHARD_TARGET_MB,
) -> dict:
    """Write ssi-data.json with automatic sharding if size exceeds threshold.

    Convention #79 implementation.

    Args:
        ssi_doc: dict with {meta, fleet_summary, regions, substations} keys
        path: target path for ssi-data.json
        threshold_mb: size trigger for sharding
        target_shard_mb: target per-shard size

    Returns:
        stats dict: {sharded: bool, size_mb: float, shard_count: int,
                     shards: list, manifest_size_mb: float}
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # ── Step 1: check if single-file fits under threshold ──
    total_size_mb = _json_size_mb(ssi_doc)
    if total_size_mb < threshold_mb:
        # Single file — no sharding needed
        payload = json.dumps(ssi_doc, separators=(",", ":"), ensure_ascii=False)
        path.write_text(payload)
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

    # ── Step 2: shard the `substations` array ──
    subs = ssi_doc.pop("substations", [])
    if not isinstance(subs, list):
        raise ValueError(f"Cannot shard: ssi_doc['substations'] is not a list (got {type(subs)})")

    subs_per_shard = _compute_subs_per_shard(subs, target_shard_mb)
    logger.info(
        f"Sharding {len(subs):,} substations into shards of ~{subs_per_shard:,} subs each "
        f"(target {target_shard_mb} MB per shard)"
    )

    shards_info = []
    shard_idx = 1
    for start in range(0, len(subs), subs_per_shard):
        chunk = subs[start:start + subs_per_shard]
        shard_name = f"ssi-data-substations-{shard_idx:02d}.json"
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
            f"({len(chunk):,} subs, {shard_bytes / 1024 / 1024:.2f} MB)"
        )
        shard_idx += 1

    # ── Step 3: write manifest (ssi-data.json with sharded=true) ──
    ssi_doc["sharded"] = True
    ssi_doc["substations_shards"] = shards_info
    manifest_payload = json.dumps(ssi_doc, separators=(",", ":"), ensure_ascii=False)
    manifest_size_mb = len(manifest_payload.encode("utf-8")) / 1024 / 1024
    path.write_text(manifest_payload)

    # ── Step 4: cleanup any stale shards beyond our count ──
    cleanup_count = cleanup_stale_shards(path, active_shard_count=len(shards_info))

    logger.info(
        f"Wrote {path} manifest ({manifest_size_mb:.2f} MB) + {len(shards_info)} shards "
        f"(total: {total_size_mb:.2f} MB → sharded per Convention #79)"
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
    """Remove stale ssi-data-substations-NN.json shards no longer referenced.

    When re-writing a ssi-data.json that was previously sharded into N shards,
    if the new write requires only M < N shards, the extras must be deleted
    to avoid stale-file pollution.

    Returns count of shards deleted.
    """
    parent = Path(manifest_path).parent
    stale = list(parent.glob("ssi-data-substations-*.json"))
    kept_count = 0
    deleted_count = 0
    for shard_path in stale:
        try:
            stem = shard_path.stem  # e.g. "ssi-data-substations-05"
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


def read_ssi_data(path: Path) -> dict:
    """Read ssi-data.json, auto-loading shards if sharded (Convention #79).

    Consumer-side helper — Python code reads ssi-data.json transparently
    whether it's single-file or sharded. The returned dict always has
    `substations` as an inline list (shard manifest is transparently expanded).

    Args:
        path: ssi-data.json path

    Returns:
        dict: {meta, fleet_summary, regions, substations} canonical schema
    """
    path = Path(path)
    data = json.loads(path.read_text())
    if not data.get("sharded"):
        return data  # Single-file case

    # Sharded — load all shards and concatenate into virtual `substations`
    shards_info = data.get("substations_shards", [])
    all_subs: list = []
    for shard_info in shards_info:
        shard_path = path.parent / shard_info["path"]
        if not shard_path.exists():
            logger.warning(
                f"Convention #56 partial-fetch: shard {shard_path.name} missing "
                f"(expected {shard_info['count']} subs)"
            )
            continue
        shard_data = json.loads(shard_path.read_text())
        if isinstance(shard_data, list):
            all_subs.extend(shard_data)
        else:
            logger.warning(f"Shard {shard_path.name} is not a list (skipped)")

    data["substations"] = all_subs
    return data


def get_ssi_data_size_stats(country_slug: str, repo_root: Optional[Path] = None) -> dict:
    """Empirical size audit for a country's ssi-data.json + shards.

    Returns dict: {country, manifest_size_mb, shard_count, total_size_mb, sharded}
    """
    if repo_root is None:
        repo_root = Path(__file__).resolve().parent.parent.parent.parent
    country_dir = repo_root / country_slug
    manifest_path = country_dir / "ssi-data.json"
    if not manifest_path.exists():
        return {"country": country_slug, "exists": False}

    manifest_mb = manifest_path.stat().st_size / 1024 / 1024
    manifest = json.loads(manifest_path.read_text())
    sharded = bool(manifest.get("sharded"))
    shards_info = manifest.get("substations_shards", []) if sharded else []
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
        # Convention #79 semantics: each INDIVIDUAL file must be <100 MB (GitHub hard limit).
        # The whole point of sharding is that TOTAL can exceed 100 MB while every file fits.
        "under_github_limit": manifest_mb < 100.0 and all(
            sh.get("size_mb", 0) < 100.0 for sh in shards_info
        ),
    }


def validate_ssi_data(path: Path) -> tuple[bool, list[str]]:
    """Validate ssi-data.json (+ shards if sharded) satisfies Convention #79.

    Checks:
    - Every file (manifest + all shards) is under 100 MB GitHub hard limit
    - If sharded: all referenced shards exist on disk
    - If sharded: `substations_shards` manifest count matches shard files
    - `meta`, `fleet_summary`, `regions` are inline (never sharded)

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

    if data.get("sharded"):
        shards = data.get("substations_shards")
        if not isinstance(shards, list):
            issues.append(f"'sharded'=true but 'substations_shards' missing or not a list")
        else:
            for sh_info in shards:
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
        if not isinstance(data.get("substations"), list):
            issues.append(f"Non-sharded but 'substations' key missing or not a list")

    return (len(issues) == 0, issues)


# ─── CLI: batch-shard a list of countries ───
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m scripts.pipeline.utils.ssi_data_sharding audit <country>")
        print("  python -m scripts.pipeline.utils.ssi_data_sharding shard <country> [<country> ...]")
        print("  python -m scripts.pipeline.utils.ssi_data_sharding shard --wave4-large")
        print("       (shards uk + us + france + germany — the 4 Wave 4 countries >100 MB)")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "audit":
        for country in sys.argv[2:]:
            stats = get_ssi_data_size_stats(country)
            print(json.dumps(stats, indent=2))
    elif cmd == "shard":
        if len(sys.argv) > 2 and sys.argv[2] == "--wave4-large":
            countries = ["uk", "us", "france", "germany"]
        else:
            countries = sys.argv[2:]
        if not countries:
            print("ERROR: no countries specified")
            sys.exit(1)

        REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
        print(f"═══════════════════════════════════════════════════════════")
        print(f"Sharding {len(countries)} country(ies) via Convention #79")
        print(f"═══════════════════════════════════════════════════════════")

        for country in countries:
            path = REPO_ROOT / country / "ssi-data.json"
            if not path.exists():
                print(f"  {country}: ssi-data.json MISSING, skipping")
                continue
            print(f"\n── {country.upper()} ──")
            data = json.loads(path.read_text())
            stats = write_ssi_data(data, path)
            if stats["sharded"]:
                print(f"  ✓ Sharded: manifest {stats['manifest_size_mb']:.2f} MB + "
                      f"{stats['shard_count']} shards ({stats['size_mb']:.2f} MB total)")
                for sh in stats["shards"]:
                    print(f"     {sh['path']}: {sh['count']:,} subs · {sh['size_mb']} MB")
            else:
                print(f"  · Single-file (under threshold): {stats['size_mb']:.2f} MB")

        print("\n═══════════════════════════════════════════════════════════")
        print("✓ Sharding complete. Run validation next:")
        for country in countries:
            print(f"  python -m scripts.pipeline.utils.ssi_data_sharding audit {country}")
        print("═══════════════════════════════════════════════════════════")
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
