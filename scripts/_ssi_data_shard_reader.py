"""
_ssi_data_shard_reader.py — Convention #79 sharded ssi-data.json reader/writer.

Shared utility for scripts that need to load or save substations from a
country's ssi-data.json, transparently handling both the legacy single-file
format AND the Convention #79 sharded format.

USAGE
-----
    from scripts._ssi_data_shard_reader import (
        load_ssi_data, save_ssi_data, load_substations, count_substations,
    )

    # Load substations (transparent shard concatenation)
    subs = load_substations(country_slug)

    # Load full manifest + substations
    data, subs, is_sharded = load_ssi_data(country_slug)

    # Fast count without full load (for scripts that only need N)
    n = count_substations(country_slug)

CONTEXT
-------
Convention #79 (grid-geo sharding) was extended to ssi-data.json for
countries with >90MB single-file size. Manifest schema:

    {
        "sharded": true,
        "substations_shards": [
            {"path": "ssi-data-substations-01.json", "count": N, "size_mb": M},
            ...
        ],
        "meta": {...},
        "fleet_summary": {...},
        ... (all other top-level keys preserved) ...
    }

Each shard payload is `{"substations": [...]}` (or bare list for compact).

Countries currently sharded (empirically verified 24 Jul 2026):
  US (4 shards), France (7 shards), Germany (7 shards), UK (?), Italy (2)

Countries in single-file mode: everything else in the 39-cohort.

The reader auto-detects via `data.get("sharded") is True`; the writer
preserves the sharded state on save (uses grid_geo_sharding utility if
sharded, else single-file write).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent


def _country_dir(country_slug: str) -> Path:
    return REPO_ROOT / country_slug


def load_ssi_data(country_slug: str) -> Tuple[Dict[str, Any], List[dict], bool]:
    """Load a country's ssi-data.json, returning (manifest, substations, is_sharded).

    Handles both Convention #79 sharded format and legacy single-file.
    Substations are always returned as a flat list regardless of storage.
    """
    ssi_path = _country_dir(country_slug) / "ssi-data.json"
    with open(ssi_path) as f:
        data = json.load(f)

    is_sharded = bool(data.get("sharded"))

    if is_sharded:
        subs = []
        shard_list = data.get("substations_shards") or data.get("shards") or []
        for shard_ref in shard_list:
            if isinstance(shard_ref, dict):
                shard_filename = shard_ref.get("path") or shard_ref.get("file")
            else:
                shard_filename = shard_ref
            if not shard_filename:
                continue
            shard_path = _country_dir(country_slug) / shard_filename
            if not shard_path.exists():
                continue
            with open(shard_path) as f:
                shard = json.load(f)
            if isinstance(shard, list):
                subs.extend(shard)
            elif isinstance(shard, dict):
                subs.extend(shard.get("substations", []))
        return data, subs, True

    return data, data.get("substations") or [], False


def load_substations(country_slug: str) -> List[dict]:
    """Convenience — just the substations list."""
    _, subs, _ = load_ssi_data(country_slug)
    return subs


def count_substations(country_slug: str) -> int:
    """Fast count without materializing shards when sharded.

    For sharded manifests, sums the 'count' field on each shard reference
    (avoids loading multi-hundred-MB shard payloads just to count).
    For single-file, len(substations).
    """
    ssi_path = _country_dir(country_slug) / "ssi-data.json"
    with open(ssi_path) as f:
        data = json.load(f)

    if data.get("sharded"):
        total = 0
        shard_list = data.get("substations_shards") or data.get("shards") or []
        for shard_ref in shard_list:
            if isinstance(shard_ref, dict) and "count" in shard_ref:
                total += int(shard_ref["count"])
            else:
                # Fallback — actually load the shard
                shard_filename = shard_ref.get("path") if isinstance(shard_ref, dict) else shard_ref
                if not shard_filename:
                    continue
                shard_path = _country_dir(country_slug) / shard_filename
                if not shard_path.exists():
                    continue
                with open(shard_path) as f:
                    shard = json.load(f)
                if isinstance(shard, list):
                    total += len(shard)
                elif isinstance(shard, dict):
                    total += len(shard.get("substations", []))
        return total

    return len(data.get("substations") or [])


def save_ssi_data(
    country_slug: str,
    manifest: Dict[str, Any],
    substations: List[dict],
    force_sharded: bool = False,
    shard_size_mb_target: float = 60.0,
    shard_size_mb_hard_limit: float = 90.0,
) -> None:
    """Save country's ssi-data.json — sharded or single-file per Convention #79.

    - If `force_sharded=True` OR the serialized manifest exceeds the hard limit,
      writes sharded (delegating to Convention #79 canonical sharding utility
      if available; else falls back to inline sharding).
    - Else writes single-file.

    Preserves all top-level manifest keys other than 'substations' /
    'substations_shards' / 'sharded' (those are managed by this function).
    """
    ssi_path = _country_dir(country_slug) / "ssi-data.json"
    country_root = _country_dir(country_slug)

    # Strip out sharding metadata from manifest — we'll rewrite it
    clean_manifest = {
        k: v for k, v in manifest.items()
        if k not in ("substations", "substations_shards", "sharded", "shards")
    }

    # Attempt sharded write via canonical utility if present
    try:
        from scripts.pipeline.utils import grid_geo_sharding  # type: ignore
        # If canonical utility handles ssi-data sharding, delegate. If not, fall through.
        if hasattr(grid_geo_sharding, "save_ssi_data_sharded"):
            grid_geo_sharding.save_ssi_data_sharded(
                country_root=country_root,
                manifest=clean_manifest,
                substations=substations,
                target_mb=shard_size_mb_target,
                hard_limit_mb=shard_size_mb_hard_limit,
            )
            return
    except ImportError:
        pass

    # Fallback — inline single-file write
    clean_manifest["substations"] = substations
    with open(ssi_path, "w") as f:
        json.dump(clean_manifest, f, separators=(",", ":"))


if __name__ == "__main__":
    # Smoke test
    import sys
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <country_slug>")
        sys.exit(1)
    slug = sys.argv[1].lower()
    data, subs, sharded = load_ssi_data(slug)
    print(f"[{slug}] mode={'sharded' if sharded else 'single-file'}  "
          f"n_substations={len(subs):,}  top-keys={sorted(data.keys())[:8]}")
