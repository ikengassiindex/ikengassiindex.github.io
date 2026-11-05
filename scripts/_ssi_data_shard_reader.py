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


def _country_dir(country_slug: str, repo_root=None) -> Path:
    """`repo_root` added 28 September 2026 so that a gate honouring its own
    --repo-root flag can use THIS reader instead of writing a ninth copy of the
    shard walk. Ten definitions of load_substations existed across the estate in
    eight distinct forms, of which two — this one and rebuild_grid_geo's —
    return an empty list where the other six raise. Default unchanged: every
    existing caller passes a slug alone and resolves against REPO_ROOT.
    See doctrine/RESULT_the_variance_gate_reads_the_shards.md"""
    return (Path(repo_root) if repo_root else REPO_ROOT) / country_slug


def load_ssi_data(country_slug: str, repo_root=None) -> Tuple[Dict[str, Any], List[dict], bool]:
    """Load a country's ssi-data.json, returning (manifest, substations, is_sharded).

    Handles both Convention #79 sharded format and legacy single-file.
    Substations are always returned as a flat list regardless of storage.
    """
    ssi_path = _country_dir(country_slug, repo_root) / "ssi-data.json"
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
            shard_path = _country_dir(country_slug, repo_root) / shard_filename
            if not shard_path.exists():
                # Left as a skip rather than a raise: this reader is imported by
                # pipeline ingestion and merge, and making it throw here changes
                # their behaviour, which is outside the scope that added
                # repo_root. A caller that must not fail open compares
                # len(subs) against the manifest's declared shard counts — the
                # manifest is returned for exactly that purpose. See
                # check_r3_variance.py::_read_fleet.
                continue
            with open(shard_path) as f:
                shard = json.load(f)
            if isinstance(shard, list):
                subs.extend(shard)
            elif isinstance(shard, dict):
                subs.extend(shard.get("substations", []))
        return data, subs, True

    return data, data.get("substations") or [], False


def load_substations(country_slug: str, repo_root=None, strict=True) -> List[dict]:
    """The one definition. Just the substations list.

    E25, closed 28 September 2026. There were TEN definitions of this function
    across the estate in EIGHT distinct forms — measured, not estimated: an AST
    walk finds one in each of eight scripts plus this one plus geo.py's, and
    nine distinct bodies. Six raised where a manifest declared shards that
    could not be read; two returned an empty list, and one of the two was THIS
    ONE — the shared utility whose own header says a second copy is exactly
    what failed.

    `strict=True` is now the default because six of the eight callers already
    expected it: a manifest with neither `substations` nor shards, or shards
    declared with no record read from any of them, RAISES. An empty country and
    an unreadable one are different facts and a bare [] cannot tell them apart.

    `strict=False` preserves the old behaviour and has exactly one caller:
    `scripts/pipeline/utils/geo.py`, which is imported by pipeline ingestion
    and merge and whose own fallback path also swallows a missing shard. Making
    the pipeline raise is a behaviour change with its own blast radius and it
    is NOT bundled into a consolidation — the flag is there so that change can
    be made in one line, deliberately, when it is ruled on.
    """
    data, subs, sharded = load_ssi_data(country_slug, repo_root)
    if strict:
        if not sharded and data.get("substations") is None:
            raise ValueError(
                f"{country_slug}: manifest has neither substations nor shards")
        if sharded and not subs:
            declared = len(data.get("substations_shards")
                           or data.get("shards") or [])
            raise ValueError(
                f"{country_slug}: {declared} shard(s) declared, no record read")
    return subs


def iter_substations(country_slug: str, repo_root=None):
    """Yield every record in manifest order, holding ONE SHARD at a time.

    WW, 18 October, E424. `load_substations` concatenates every shard into one
    list, and that list is what made france unwritable: 168,894 records at
    about 13 KiB resident each is past this window's 3.66 GiB once a writer
    needs a payload beside them. Every instrument that reads a fleet to WRITE
    it back needs the records in order and does not need them all at once.

    The order is the manifest's own, which is what makes a streaming digest
    over this iterator comparable with one taken over `load_substations`: the
    same records in the same sequence. A caller that needs a second pass calls
    this again rather than keeping the first - re-reading a shard from disk is
    cheap and holding the fleet is not.

    It refuses on the same conditions `load_substations(strict=True)` refuses
    on, so a missing shard cannot read as a short fleet.
    """
    cdir = _country_dir(country_slug, repo_root)
    with open(cdir / "ssi-data.json") as f:
        man = json.load(f)
    refs = man.get("substations_shards") or man.get("shards") or []
    if not refs:
        subs = man.get("substations")
        if subs is None:
            raise ValueError(
                f"{country_slug}: manifest has neither substations nor shards")
        for r in subs:
            yield r
        return
    seen = 0
    for ref in refs:
        path = cdir / Path(ref["path"]).name
        with open(path) as f:
            chunk = json.load(f)
        rows = chunk if isinstance(chunk, list) else chunk.get("substations", [])
        for r in rows:
            seen += 1
            yield r
        del chunk, rows
    if not seen:
        raise ValueError(
            f"{country_slug}: {len(refs)} shard(s) declared, no record read")


def count_substations(country_slug: str, repo_root=None) -> int:
    """Fast count without materializing shards when sharded.

    For sharded manifests, sums the 'count' field on each shard reference
    (avoids loading multi-hundred-MB shard payloads just to count).
    For single-file, len(substations).
    """
    ssi_path = _country_dir(country_slug, repo_root) / "ssi-data.json"
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
                shard_path = _country_dir(country_slug, repo_root) / shard_filename
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



# Convention #79's thresholds have one home: the canonical sharding module.
# This file used to keep its own copy — 60.0 target / 90.0 hard limit — which
# were the correct values when it was written on 24 July 2026 and stale from
# the 18 August v4.24 recalibration onward. Because they were passed down as
# explicit arguments they silently overrode the corrected defaults, and on
# 27 August they re-sharded six countries at the old sizes, leaving poland
# single-file at 62.40 MB against its own 60 MB threshold.
#
# Importing rather than re-copying: a second copy is exactly what failed.
def _shard_thresholds():
    try:
        from scripts.pipeline.utils.ssi_data_sharding import (
            SSI_DATA_SHARD_THRESHOLD_MB, SSI_DATA_SHARD_TARGET_MB)
        return SSI_DATA_SHARD_TARGET_MB, SSI_DATA_SHARD_THRESHOLD_MB
    except ImportError:
        # Visible fallback at the post-v4.24 values rather than a silent
        # reversion to the pre-v4.24 pair.
        return 45.0, 60.0


# ── Convention #79 has a TARGET and a REFUSAL, and GitHub warns between them ──
#
# 5 October 2026. A push of 12 commits drew three GitHub warnings:
#   "File italy/ssi-data-substations-01.json is 50.27 MB; this is larger than
#    GitHub's recommended maximum file size of 50.00 MB"
# Those blobs were historical -- the 4-shard italy layout at 52.7-53.2 MB -- and
# nothing was rewritten over a warning. But the gap they exposed is real:
#
#   Convention #79 TARGET      45 MiB   what the re-cutting writer aims at
#   GitHub's recommendation    50 MB    = 47.68 MiB      <-- inside the gap
#   Convention #79 REFUSAL     60 MiB   what this module refuses at
#
# save_ssi_data_in_place NEVER re-cuts: it slices by the manifest's own declared
# counts, so a fleet that gains fields grows its existing shards. Between 45 and
# 60 MiB it grows silently, and GitHub starts complaining at 47.68 MiB -- a full
# 12 MiB before anything here would object. The drift is therefore invisible to
# the estate and visible to GitHub, which is the wrong way round.
#
# So this WARNS at 47 MiB. It does not refuse: 60 MiB is the convention's number
# and a warning is not a veto. What it buys is that the drift is noticed on the
# write that causes it rather than on a push weeks later.
SHARD_WARN_MIB = 47.0


def _warn_if_drifting(country_slug, path_name, nbytes):
    import sys as _sys
    mib = nbytes / 1024 / 1024
    if mib < SHARD_WARN_MIB:
        return
    _sys.stderr.write(
        "  SHARD DRIFT  %s/%s is %.2f MiB (%.2f MB). Convention #79 targets 45 MiB "
        "and refuses at 60; GitHub warns above 50 MB = 47.68 MiB. This writer does "
        "not re-cut, so the file will keep growing until a re-cut is run.\n"
        % (country_slug, path_name, mib, nbytes / 1_000_000))


def _write_atomic(path, payload):
    """Write bytes so a killed process can never leave a half-written shard.

    WHY THIS EXISTS, DATED
      5 October 2026. A rescore of the uk was killed by a call timeout DURING
      `(cdir / ref["path"]).write_bytes(payload)`. Shards 01 and 02 were
      complete, 03 was truncated mid-record, and `json.load` on it raised
      "Expecting ',' delimiter: line 892 column 328". The fleet was recovered
      with `git checkout -- uk/` because the previous state happened to be
      committed. That is luck, not a design.

      A write to a temporary sibling followed by os.replace is atomic on a
      single filesystem: a reader sees either the whole old file or the whole
      new one, never a prefix of the new one. Every instrument that saves a
      fleet goes through this module, so fixing it here fixes all of them.
    """
    import os as _os
    tmp = path.with_name(path.name + ".writing.tmp")
    try:
        tmp.write_bytes(payload)
        _os.replace(str(tmp), str(path))
    except BaseException:
        # a failed write must not leave the .tmp behind to be mistaken for data
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass
        raise


def save_ssi_data_in_place(
    country_slug: str,
    manifest: Dict[str, Any],
    substations: List[dict],
    repo_root=None,
) -> Dict[str, Any]:
    """Write the records back to the files they came from. It NEVER re-cuts.

    `save_ssi_data` delegates to the Convention #79 writer, which recomputes the
    shard layout from the sizing rule and then calls `cleanup_stale_shards`. That
    is right when a fleet's size has changed and wrong when it has not: on
    10 September it re-cut italy into a fourth shard that stayed outside git for
    six hours (E33), and cleanup_stale_shards deletes, which is the flag officer's
    under Pin 8.

    So a script that only ADDS OR CHANGES A FIELD on records it already has
    should use this instead. The partition is exact rather than recomputed:
    `load_ssi_data` concatenates the shards in manifest order, so slicing the flat
    list back by the manifest's own counts restores the identical partition. Each
    shard keeps its path and its count; only `size_mb` is refreshed, which the
    write genuinely changes.

    IT REFUSES rather than guessing:
      * a record count that disagrees with the manifest's declared total — which
        is precisely the fail-open `load_ssi_data` warns about, where a missing
        shard is skipped and the flat list comes back short
      * any file that would reach the sharding threshold, because the NEXT writer
        would then re-cut it

    Returns {files: [(path, count, bytes)], sharded: bool}.
    """
    from scripts.pipeline.utils.ssi_data_sharding import (     # noqa: PLC0415
        dumps_canonical, SSI_DATA_SHARD_THRESHOLD_MB)
    limit = SSI_DATA_SHARD_THRESHOLD_MB * 1024 * 1024
    cdir = _country_dir(country_slug, repo_root)
    refs = manifest.get("substations_shards") or []

    if not refs:
        doc = {k: v for k, v in manifest.items() if k != "substations_shards"}
        doc["substations"] = substations
        payload = dumps_canonical(doc)
        if len(payload) >= limit:
            raise ValueError(
                "%s: the register would be %.2f MB, at or over the %.0f MB "
                "threshold — the next writer would shard it"
                % (country_slug, len(payload) / 1024 / 1024,
                   SSI_DATA_SHARD_THRESHOLD_MB))
        _warn_if_drifting(country_slug, "ssi-data.json", len(payload))
        _write_atomic(cdir / "ssi-data.json", payload)
        return {"files": [("ssi-data.json", len(substations), len(payload))],
                "sharded": False}

    declared = sum(int(r["count"]) for r in refs)
    if declared != len(substations):
        raise ValueError(
            "%s: the manifest declares %d records across %d shards and %d were "
            "handed back — refusing rather than re-partitioning"
            % (country_slug, declared, len(refs), len(substations)))

    # ── STAGE EVERY SHARD, THEN COMMIT. WW, 18 October, E424. ───────────
    #
    # This loop used to build EVERY shard's payload into `plans` and only then
    # write them, so that a fleet could never be left half-written when a late
    # shard turned out to be over the threshold. That property is right and is
    # kept. What it cost was memory: thirteen serialised shards sat beside the
    # records, and germany's 108,016 records peaked at 1,750 MiB with france's
    # 168,894 projected past the window's 3.66 GiB - which is why france's
    # re-cut was killed on 16 October with nothing written.
    #
    # THE SAME PROPERTY WITHOUT THE PEAK: serialise one shard, check it, and
    # stage it to the SAME `.writing.tmp` sibling `_write_atomic` already uses,
    # then drop the payload. If every shard passes, the only mutation left is
    # the os.replace of each staged file, which is what _write_atomic does
    # anyway. So the all-or-nothing guarantee is STRONGER than before - every
    # check now happens before ANY replace - and only one payload is ever in
    # memory. The cost is temporary disk, about the size of the fleet.
    import os as _os
    staged, start = [], 0
    try:
        for ref in refs:
            n = int(ref["count"])
            payload = dumps_canonical(substations[start:start + n])
            if len(payload) >= limit:
                raise ValueError(
                    "%s: %s would be %.2f MB, at or over the %.0f MB threshold — "
                    "the next writer would re-cut it"
                    % (country_slug, ref["path"], len(payload) / 1024 / 1024,
                       SSI_DATA_SHARD_THRESHOLD_MB))
            dest = cdir / ref["path"]
            tmp = dest.with_name(dest.name + ".writing.tmp")
            tmp.write_bytes(payload)
            staged.append((ref, dest, tmp, len(payload)))
            del payload
            start += n
    except BaseException:
        # A FAILED STAGE LEAVES NOTHING BEHIND. A .writing.tmp mistaken for
        # data is the defect _write_atomic exists to prevent.
        for _ref, _dest, _tmp, _n in staged:
            try:
                if _tmp.exists():
                    _tmp.unlink()
            except OSError:
                pass
        raise

    out = []
    for ref, dest, tmp, nbytes in staged:
        _warn_if_drifting(country_slug, ref["path"], nbytes)
        _os.replace(str(tmp), str(dest))
        ref["size_mb"] = round(nbytes / 1024 / 1024, 3)
        out.append((ref["path"], int(ref["count"]), nbytes))
    doc = {k: v for k, v in manifest.items() if k != "substations"}
    doc["sharded"] = True
    _write_atomic(cdir / "ssi-data.json", dumps_canonical(doc))
    return {"files": out, "sharded": True}


def save_ssi_data(
    country_slug: str,
    manifest: Dict[str, Any],
    substations: List[dict],
    force_sharded: bool = False,
    shard_size_mb_target: float = None,
    shard_size_mb_hard_limit: float = None,
) -> None:
    """Save country's ssi-data.json — sharded or single-file per Convention #79.

    - If `force_sharded=True` OR the serialized manifest exceeds the hard limit,
      writes sharded (delegating to Convention #79 canonical sharding utility
      if available; else falls back to inline sharding).
    - Else writes single-file.

    Preserves all top-level manifest keys other than 'substations' /
    'substations_shards' / 'sharded' (those are managed by this function).
    """
    _t, _h = _shard_thresholds()
    if shard_size_mb_target is None:
        shard_size_mb_target = _t
    if shard_size_mb_hard_limit is None:
        shard_size_mb_hard_limit = _h

    ssi_path = _country_dir(country_slug) / "ssi-data.json"
    country_root = _country_dir(country_slug)

    # Strip out sharding metadata from manifest — we'll rewrite it
    clean_manifest = {
        k: v for k, v in manifest.items()
        if k not in ("substations", "substations_shards", "sharded", "shards")
    }

    # Attempt sharded write via canonical utility if present
    try:
        from scripts.pipeline.utils.ssi_data_sharding import write_ssi_data as _canonical_write  # type: ignore
        clean_manifest["substations"] = substations
        _canonical_write(
            clean_manifest,
            ssi_path,
            threshold_mb=shard_size_mb_hard_limit,
            target_shard_mb=shard_size_mb_target,
        )
        return
    except ImportError:
        pass

    # Fallback — inline single-file write.
    #
    # IT MUST MATCH THE CANONICAL WRITER, and until 1 October it did not: this
    # call omitted ensure_ascii=False, so if the import above ever failed, a
    # register with a Polish or Turkish name in it would be written back with
    # every non-ascii character escaped — a different encoding of the same
    # document, and a diff touching every record that has an accent in it. It
    # also wrote the document on one line, which is the defect
    # doctrine/FINDING_a_write_reformats_32_of_39_registers_and_the_diff_cannot_show_it.md
    # records. Both are fixed here by using the one serialisation.
    clean_manifest["substations"] = substations
    try:
        from scripts.pipeline.utils.ssi_data_sharding import dumps_canonical
        payload = dumps_canonical(clean_manifest)
    except ImportError:
        payload = json.dumps(clean_manifest, separators=(",", ":"),
                             ensure_ascii=False).encode("utf-8")
    with open(ssi_path, "wb") as f:
        f.write(payload)


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
