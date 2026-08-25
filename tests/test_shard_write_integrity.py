"""Sentinel — a shard set must never be internally inconsistent, and the writer
that produces it must never be able to leave it that way.

WHY THIS TEST EXISTS
────────────────────
On 20 August 2026 an M-054 recovery pass over Italy was killed by a timeout
mid-write. `write_ssi_data` used `Path.write_text`, which truncates the target
and then streams, so the interrupted run left:

  shard 01 — complete, but written under a NEW record-per-shard boundary
  shard 02 — truncated mid-string, invalid JSON
  shard 03 — stale, still holding the PREVIOUS boundary's records
  manifest — never updated, still declaring the previous layout

Shard 01 was the dangerous one. It was *valid JSON* holding 16,791 records
where the manifest declared 16,805. Every reader that concatenates shards
without checking counts would have accepted a fleet 14 substations short and
reported success. That is M-046's signature in file form: absence read as
success.

Recovery required reverting Italy to the last commit and re-running both
remediation stages, because no coherent reconstruction existed on disk.

WHAT THIS PINS
──────────────
1.  Every sharded country's shards parse, and each shard's length equals the
    count its manifest declares. A stale manifest and a short shard are the
    same failure and both fail here.
2.  The shard totals reconcile with `meta.total` / `meta.n_substations`.
3.  No `.tmp-write` files are left lying around — one means a write died and
    was never cleaned up, and the next reader may be about to trust whatever
    the real file currently holds.
4.  The writers actually go through the atomic helper. This is the structural
    half: a future refactor that reintroduces `path.write_text` for a payload
    fails here rather than at 3 a.m. during a cohort run.

Cross-reference: Convention #79 (ssi-data sharding), Convention #80 (grid-geo
sharding), Convention #56 (never silently default; never hide degradation),
CLAUDE.md Discipline #50, modification-log M-055.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

SHARDING_MODULES = (
    REPO_ROOT / "scripts" / "pipeline" / "utils" / "ssi_data_sharding.py",
    REPO_ROOT / "scripts" / "pipeline" / "utils" / "grid_geo_sharding.py",
)


def _sharded_countries():
    out = []
    for manifest in sorted(REPO_ROOT.glob("*/ssi-data.json")):
        try:
            doc = json.loads(manifest.read_text(encoding="utf-8"))
        except Exception:
            continue
        if doc.get("sharded"):
            out.append((manifest.parent.name, manifest, doc))
    return out


SHARDED = _sharded_countries()
IDS = [c for c, _, _ in SHARDED] or ["<none>"]


class TestShardSetsAreCoherent:

    @pytest.mark.parametrize("country,manifest,doc", SHARDED or [pytest.param(None, None, None, marks=pytest.mark.skip(reason="no sharded countries in this checkout"))], ids=IDS)
    def test_each_shard_matches_its_declared_count(self, country, manifest, doc):
        shards = doc.get("substations_shards") or []
        assert shards, f"{country}: manifest says sharded=true but declares no shards"
        problems = []
        total = 0
        for entry in shards:
            path = manifest.parent / entry["path"]
            if not path.exists():
                problems.append(f"{entry['path']}: MISSING")
                continue
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                problems.append(f"{entry['path']}: unparseable — {exc}")
                continue
            if not isinstance(payload, list):
                problems.append(f"{entry['path']}: payload is {type(payload).__name__}, expected list")
                continue
            total += len(payload)
            if len(payload) != entry["count"]:
                problems.append(
                    f"{entry['path']}: holds {len(payload):,} but the manifest declares "
                    f"{entry['count']:,} — shard truncated or manifest stale"
                )
        assert not problems, (
            f"{country} shard set is incoherent:\n  " + "\n  ".join(problems) +
            "\n\nA short-but-valid shard is accepted silently by every "
            "concatenating reader. Restore from git and re-run the producing "
            "pass; do not patch the manifest to agree with the damage."
        )
        declared_total = (doc.get("meta") or {}).get("total") or (doc.get("meta") or {}).get("n_substations")
        if declared_total is not None:
            assert total == declared_total, (
                f"{country}: shards sum to {total:,} but meta declares {declared_total:,}"
            )


class TestNoInterruptedWritesLeftBehind:

    def test_no_orphan_tmp_write_files(self):
        orphans = sorted(str(p.relative_to(REPO_ROOT)) for p in REPO_ROOT.glob("*/*.tmp-write"))
        assert not orphans, (
            "orphaned atomic-write temp files found — a write died and left "
            f"these behind: {orphans}. The real file may be the previous "
            "version; confirm before trusting it."
        )


class TestWritersAreAtomic:
    """The structural guard. Point 1 catches damage; this catches its cause."""

    @pytest.mark.parametrize("module", SHARDING_MODULES, ids=lambda p: p.name)
    def test_no_raw_write_text_for_payloads(self, module):
        if not module.exists():
            pytest.skip(f"{module.name} not present in this checkout")
        source = module.read_text(encoding="utf-8")
        tree = ast.parse(source)
        offenders = []
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "write_text"
            ):
                offenders.append(node.lineno)
        assert not offenders, (
            f"{module.name} calls .write_text() at line(s) {offenders}. "
            "`write_text` truncates the target and then streams: an interrupted "
            "run leaves a half-written file, and for a shard that means a "
            "shorter-but-parseable array every reader accepts. Use "
            "`_atomic_write_text` (temp file + fsync + os.replace) so the "
            "target is always either the whole old version or the whole new one."
        )

    def test_atomic_helper_replaces_rather_than_rewrites(self):
        source = SHARDING_MODULES[0].read_text(encoding="utf-8")
        assert "_atomic_write_text" in source, "the atomic write helper is gone"
        assert "os.replace" in source, (
            "_atomic_write_text no longer uses os.replace. A copy-then-delete "
            "or a shutil.move across filesystems is not atomic and reopens the "
            "exact window this helper exists to close."
        )
        assert "os.fsync" in source, (
            "_atomic_write_text no longer fsyncs before replacing. Without it "
            "the rename can land before the bytes do, and a crash leaves an "
            "atomically-renamed empty file — a worse failure than the one fixed."
        )
