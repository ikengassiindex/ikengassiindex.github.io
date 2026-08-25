#!/usr/bin/env python3
"""r10_semantic_normalise.py — Task #877 sibling to Task #450 SYSTEMIC bridge.

Per-country min-max linear rescale for the R10 institutional-just-transition
modifier (`modifiers.R10_just`). Empirical scan 10 Aug 2026 shows 39/39
cohort countries carry R10_just values in the multiplicative-modifier range
[1.00, 1.12] (soft cap at 1.20). Downstream P7-ERE structural estimator
expects R10 on a [0, 1] envelope for interaction-term interpretability;
without rescale, R10 variance ≈ 0.012 collapses the H×R10 interaction into
statistical noise and 20 of 39 countries flag as `†` outliers.

Contract mirrors migration_score_semantic_normalise.py (Task #450):

    new_R10 = (old_R10 - min_country) / (max_country - min_country)

Preserves per-substation ranking (relative order unchanged) + snapshots the
absolute R10 as `_R10_absolute` per-sub audit marker for full reversibility
per Convention #56. Idempotent (skips subs with existing marker).

Merge-not-replace BINDING contract (Task #451/#452/#453/#454 family): all
prior audit markers preserved (Task #451 `_catchment_population_source`,
Task #452 `_migration_score_source`, Task #453/#454 admin backfill).

Convention preservation
-----------------------
- #7   Data-Layer Anchoring — per-country stat as documented-proxy
- #56  Visibly-honest degradation — audit marker + degenerate case skip
- #79  ssi-data sharding preserved (read_ssi_data + write_ssi_data)
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    from scripts.pipeline.utils.ssi_data_sharding import (  # type: ignore
        read_ssi_data,
        write_ssi_data,
    )
    _HAS_SHARDING = True
except ImportError:
    _HAS_SHARDING = False


# ═════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ═════════════════════════════════════════════════════════════════════

AUDIT_TRAIL_KEY = "_R10_normalise_source"
AUDIT_TRAIL_VALUE = "TASK_877_R10_MIN_MAX_RESCALE_v4_2"
ABSOLUTE_SNAPSHOT_KEY = "_R10_absolute"

# Preserve markers from prior enrichment tasks (BINDING merge-not-replace)
PRESERVE_MARKERS = (
    "_catchment_population_source",   # Task #451
    "_migration_score_source",         # Task #452
    "_migration_score_semantic_normalise_source",  # Task #450 bridge
    "_socio_economic_source",          # Task #453/#454
)

MIN_ENVELOPE = 0.0
MAX_ENVELOPE = 1.0


logging.basicConfig(
    format="%(asctime)s %(levelname)-7s %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════
#  Per-country diagnostic
# ═════════════════════════════════════════════════════════════════════

def audit_country(slug: str) -> Optional[Dict[str, Any]]:
    if not _HAS_SHARDING:
        raise RuntimeError("ssi_data_sharding utility not importable")

    ssi_path = REPO_ROOT / slug / "ssi-data.json"
    if not ssi_path.exists():
        return None

    data = read_ssi_data(ssi_path)
    subs = data.get("substations", []) if isinstance(data, dict) else data or []

    scores = []
    for sub in subs:
        m = sub.get("modifiers") or {}
        v = m.get("R10_just")
        if v is not None:
            scores.append(v)

    if not scores:
        return {"slug": slug, "n_total": len(subs), "n_populated": 0, "has_drift": False}

    v_min = min(scores)
    v_max = max(scores)
    return {
        "slug": slug,
        "n_total": len(subs),
        "n_populated": len(scores),
        "unique_values": len(set(scores)),
        "min": round(v_min, 6),
        "max": round(v_max, 6),
        "range_span": round(v_max - v_min, 6),
        "has_drift": (v_min < MIN_ENVELOPE) or (v_max > MAX_ENVELOPE),
    }


# ═════════════════════════════════════════════════════════════════════
#  Per-country apply
# ═════════════════════════════════════════════════════════════════════

def normalise_country(slug: str, *, dry_run: bool = False) -> Dict[str, Any]:
    if not _HAS_SHARDING:
        raise RuntimeError("ssi_data_sharding utility not importable")

    t0 = time.time()
    ssi_path = REPO_ROOT / slug / "ssi-data.json"
    if not ssi_path.exists():
        raise FileNotFoundError(f"[{slug}] ssi-data.json not found")

    log.info(f"[{slug}] loading ssi-data.json...")
    data = read_ssi_data(ssi_path)
    if isinstance(data, list):
        subs = data
        data = {"substations": subs}
    else:
        subs = data.get("substations", [])
    n = len(subs)
    log.info(f"[{slug}] {n:,} subs loaded in {time.time()-t0:.1f}s")

    raw_scores = []
    for sub in subs:
        m = sub.get("modifiers") or {}
        # Skip already-normalised (idempotency)
        if m.get(AUDIT_TRAIL_KEY) == AUDIT_TRAIL_VALUE:
            continue
        v = m.get("R10_just")
        if v is not None:
            raw_scores.append(v)

    if not raw_scores:
        return {"country": slug, "n_substations": n, "n_populated": 0,
                "n_written": 0, "reason": "no un-normalised R10 to process",
                "dry_run": dry_run}

    v_min = min(raw_scores)
    v_max = max(raw_scores)
    range_span = v_max - v_min

    if range_span == 0:
        log.warning(f"[{slug}] degenerate range (min == max = {v_min}) — Convention #56 skip")
        return {"country": slug, "n_populated": len(raw_scores), "n_written": 0,
                "min_pre": v_min, "max_pre": v_max,
                "reason": "degenerate range (min==max) — Convention #56 skip",
                "dry_run": dry_run}

    if v_min >= MIN_ENVELOPE and v_max <= MAX_ENVELOPE:
        log.info(f"[{slug}] already in [0, 1] envelope — no rescale needed")
        return {"country": slug, "n_populated": len(raw_scores), "n_written": 0,
                "min_pre": v_min, "max_pre": v_max,
                "reason": "already in [0, 1] envelope",
                "dry_run": dry_run}

    log.info(f"[{slug}] rescaling {len(raw_scores):,} subs — "
             f"[{v_min:.4f}, {v_max:.4f}] → [0, 1]")

    n_written = 0
    n_already = 0
    preserve_counts = {k: 0 for k in PRESERVE_MARKERS}

    for sub in subs:
        m = sub.get("modifiers") or {}
        if m.get(AUDIT_TRAIL_KEY) == AUDIT_TRAIL_VALUE:
            n_already += 1
            continue
        v = m.get("R10_just")
        if v is None:
            continue

        new_r10 = (v - v_min) / range_span
        new_r10 = max(0.0, min(1.0, new_r10))
        new_r10 = round(new_r10, 6)

        # Track marker preservation across sub payload
        se = sub.get("socio_economic") or {}
        for k in PRESERVE_MARKERS:
            if se.get(k) or m.get(k) or sub.get(k):
                preserve_counts[k] += 1

        # Preserve absolute R10 pre-rescale
        if ABSOLUTE_SNAPSHOT_KEY not in m:
            m[ABSOLUTE_SNAPSHOT_KEY] = round(v, 6)
        m["R10_just"] = new_r10
        m[AUDIT_TRAIL_KEY] = AUDIT_TRAIL_VALUE
        sub["modifiers"] = m
        n_written += 1

    if dry_run:
        log.info(f"[{slug}] DRY-RUN — no write")
    else:
        log.info(f"[{slug}] writing ssi-data.json...")
        write_ssi_data(data, ssi_path)
        log.info(f"[{slug}] saved.")

    return {
        "country": slug,
        "mode": "min_max_linear_rescale",
        "n_substations": n,
        "n_populated": len(raw_scores),
        "n_written": n_written,
        "n_already_normalised": n_already,
        "min_pre": v_min,
        "max_pre": v_max,
        "range_span_pre": range_span,
        "markers_preserved": preserve_counts,
        "wall_clock_sec": round(time.time() - t0, 2),
        "dry_run": dry_run,
    }


# ═════════════════════════════════════════════════════════════════════
#  CLI
# ═════════════════════════════════════════════════════════════════════

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="r10_semantic_normalise.py",
        description="Task #877 R10 min-max linear rescale (sibling to Task #450)",
    )
    p.add_argument("slug", nargs="?", default=None)
    p.add_argument("--cohort", action="store_true", help="Apply to all 39 SoT slugs")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--diagnose-only", action="store_true")
    return p


def main() -> int:
    args = _build_parser().parse_args()

    cohort_slugs = json.load(open(REPO_ROOT / "intelligence" / "countries.json"))["slugs"]

    if args.diagnose_only:
        log.info(f"Diagnosing {len(cohort_slugs)} countries for R10 drift...")
        rows = []
        for slug in cohort_slugs:
            r = audit_country(slug)
            if r:
                rows.append(r)
        print()
        for r in rows:
            m = r.get("min", "?")
            M = r.get("max", "?")
            print(f"  {r['slug']:14} n={r['n_populated']:>7} "
                  f"range=[{m}, {M}] drift={r.get('has_drift')}")
        return 0

    if args.cohort:
        targets = list(cohort_slugs)
    elif args.slug:
        targets = [args.slug]
    else:
        _build_parser().print_help()
        return 1

    reports = []
    total_written = 0
    for slug in targets:
        log.info(f"═══ {slug} ═══")
        try:
            r = normalise_country(slug, dry_run=args.dry_run)
            reports.append(r)
            if r.get("n_written"):
                total_written += r["n_written"]
        except Exception as e:
            log.error(f"[{slug}] FAILED: {e}")
            reports.append({"country": slug, "error": str(e)})

    audit_out = Path.home() / f"r10_semantic_normalise_audit_{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}.json"
    with open(audit_out, "w") as f:
        json.dump({
            "task_id": "#877-R10-min-max-rescale",
            "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "dry_run": args.dry_run,
            "targets": targets,
            "total_written": total_written,
            "reports": reports,
        }, f, indent=2, default=str)
    log.info(f"✓ Audit report: {audit_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
