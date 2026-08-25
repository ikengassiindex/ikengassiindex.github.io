"""
Shared test support — one shard-resolution implementation for the suite.

Convention #79 shards six countries (france, germany, italy, poland, uk, us)
whose ssi-data.json exceeds the 60 MB threshold. For those, ssi-data.json is a
MANIFEST: it carries ``sharded: true`` and a ``substations_shards`` list, and
has no inline ``substations`` key.

Any reader that does a plain ``json.load`` and reaches for ``substations`` gets
nothing — and, in this repo's experience, then reports success on the empty
result. That produced two separate false signals in the 19 August run: six
G2 failures, and a score-shift gate that saw an empty post-refresh fleet and
declared the baseline incomparable.

This module exists so there is exactly ONE resolution implementation in the
test suite, matching the single-reader principle applied to the tolerance
config. It is deliberately STRICTER than the production reader
(``scripts/_ssi_data_shard_reader.py``), which skips missing shards silently:
here a missing shard, a non-list payload, or a length that disagrees with the
manifest's declared ``count`` raises. A harness that quietly loses a shard is
the failure mode being guarded against.

Cross-reference: Convention #79; modification-log M-030.
"""

from __future__ import annotations

import json
from pathlib import Path


class ShardResolutionError(AssertionError):
    """A sharded manifest and its shard files disagree."""


def load_ssi_data(country: str, repo_root: Path) -> dict:
    """Load ``<country>/ssi-data.json``, materialising shards if sharded.

    Returns a dict that always has a ``substations`` list, so callers need no
    shard awareness of their own.
    """
    fp = repo_root / country / "ssi-data.json"
    doc = json.loads(fp.read_text(encoding="utf-8"))
    if not doc.get("sharded"):
        return doc
    return _resolve(country, doc, repo_root)


def _resolve(country: str, doc: dict, repo_root: Path) -> dict:
    shards = doc.get("substations_shards")
    if not isinstance(shards, list) or not shards:
        raise ShardResolutionError(
            f"{country}/ssi-data.json declares sharded=true but carries no "
            f"'substations_shards' list — Convention #79 manifest contract "
            f"broken"
        )
    subs: list = []
    for idx, shard in enumerate(shards, start=1):
        rel = shard.get("path") if isinstance(shard, dict) else shard
        if not rel:
            raise ShardResolutionError(
                f"{country} shard #{idx} has no 'path' — entry: {shard!r}"
            )
        shard_fp = repo_root / country / rel
        if not shard_fp.exists():
            raise ShardResolutionError(
                f"{country} manifest points at {rel}, which is not on disk. "
                f"The manifest and the shard files have diverged."
            )
        payload = json.loads(shard_fp.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            payload = payload.get("substations", [])
        if not isinstance(payload, list):
            raise ShardResolutionError(
                f"{country}/{rel} did not parse to a list of substations "
                f"(got {type(payload).__name__}). The JS loaders concatenate "
                f"shards as arrays and would silently yield one bogus record."
            )
        declared = shard.get("count") if isinstance(shard, dict) else None
        if declared is not None and len(payload) != declared:
            raise ShardResolutionError(
                f"{country}/{rel} holds {len(payload)} substations but the "
                f"manifest declares {declared} — shard truncated or manifest "
                f"stale"
            )
        subs.extend(payload)
    out = dict(doc)
    out["substations"] = subs
    return out


def substation_list(doc: dict) -> list:
    """Normalise the substations container to a list."""
    subs = doc.get("substations", [])
    if isinstance(subs, dict):
        subs = list(subs.values())
    return subs


__all__ = ["ShardResolutionError", "load_ssi_data", "substation_list"]
