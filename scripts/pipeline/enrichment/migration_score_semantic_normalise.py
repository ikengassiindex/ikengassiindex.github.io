#!/usr/bin/env python3
"""migration_score_semantic_normalise.py — Task #450 SYSTEMIC bridge

Task #450 SYSTEMIC (24 July 2026) — semantic-scale drift closure for
migration_score. Per-country min-max linear rescale to [0, 1] preserving
per-substation ranking for 5 countries surfaced empirically as
semantic-drift signature (out-of-[0,1] migration_score values):

  Denmark      — 4,821 subs, range [-0.02, +1.00] (tiny negative tail)
  Ireland      — 1,278 subs, range [-0.12, +1.00] (small negative tail)
  New Zealand  — 1,589 subs, range [-0.39, +1.00] (mixed sign)
  Greece       —   719 subs, range [-4.50, +2.50] (out-of-scale)
  Mexico       — 3,085 subs, range [-5.00, +8.00] (percent-scale)

Task #452 explicitly preserved these values (they are genuine
per-substation distributions, NOT fleet-uniform national-scalar fallback)
via `is_fleet_uniform_fallback()` detection helper. Task #450 SYSTEMIC
bridges the remaining gap: preserved-but-out-of-[0,1] values are
rescaled per-country via linear min-max transform.

Normalization contract
----------------------
For each country with `min < 0 OR max > 1` semantic-drift signature:

    new_score = (old_score - min_country) / (max_country - min_country)

This is a linear per-country rescale that:
  1. Preserves per-substation ranking (relative order unchanged)
  2. Maps [min, max] → [0, 1] exactly
  3. Loses absolute-scale semantic meaning (e.g. Mexico "percent change"
     becomes within-country normalized rank)
  4. Convention #56 visibly-honest: audit marker
     `_migration_score_semantic_normalise_source =
      "TASK_450_MIN_MAX_LINEAR_RESCALE_v4_2"` on every rescaled sub

Merge-not-replace BINDING contract (Task #451/#452/#453 discipline family)
-------------------------------------------------------------------------
Task #452 `_migration_score_source` marker MUST survive Task #450 pass.
Idempotency: if `_migration_score_semantic_normalise_source` already
present on a sub, skip (already normalised).

Convention preservation
-----------------------
- #7   Data-Layer Anchoring — per-country stat as documented-proxy
- #56  Visibly-honest degradation — audit marker + degenerate case
       (min==max) → skip country not fabricate
- #60  Ikenga IS the ESG provider — no commercial ESG source consumed
- #79  ssi-data sharding preserved (read_ssi_data + write_ssi_data)

Usage
-----
Diagnose (per-country stats, no write):
    python3 scripts/pipeline/enrichment/migration_score_semantic_normalise.py --diagnose-only

Single-country apply:
    python3 scripts/pipeline/enrichment/migration_score_semantic_normalise.py mexico

Cohort apply (5 target countries):
    python3 scripts/pipeline/enrichment/migration_score_semantic_normalise.py --cohort

Cross-refs
----------
- Task #450 SYSTEMIC   (this workstream)
- Task #452 Step 5d    Migration score utility Niva-based (sibling FLOW variant)
- Task #453 Step 3     Polygon spatial-join utility (sibling ADMIN variant)
- Task #454 SYSTEMIC   Polygon utility extension (cohort-wide 15 countries)
- REPORTS_FRAMING_KB.md §8bis Discipline #47 candidate SIBLING variant
- METHODOLOGY_DISCIPLINES.md §5septies (unchanged)
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# ── path setup ──────────────────────────────────────────────────────────
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
#  CONSTANTS — Task #450 SYSTEMIC audit markers + target cohort
# ═════════════════════════════════════════════════════════════════════

AUDIT_TRAIL_KEY = "_migration_score_semantic_normalise_source"
AUDIT_TRAIL_VALUE = "TASK_450_MIN_MAX_LINEAR_RESCALE_v4_2"

# Task #452 marker to preserve
TASK_452_MARKER = "_migration_score_source"
# Task #451 marker to preserve
TASK_451_MARKER = "_catchment_population_source"

# Empirical semantic-drift cohort (surfaced 24 Jul 2026 cohort audit).
# Countries where migration_score has out-of-[0,1] range signature.
# Utility computes per-country min/max at runtime (not hardcoded) so
# any future drift instance surfaces automatically without config change.
TARGET_COHORT = (
    "denmark", "ireland", "new-zealand", "greece", "mexico",
)

# Semantic-drift detection threshold (any populated sub with score outside
# this envelope triggers per-country rescale)
MIN_ENVELOPE = 0.0
MAX_ENVELOPE = 1.0


# ═════════════════════════════════════════════════════════════════════
#  Logging
# ═════════════════════════════════════════════════════════════════════

logging.basicConfig(
    format="%(asctime)s %(levelname)-7s %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════
#  Per-country semantic-drift audit
# ═════════════════════════════════════════════════════════════════════

def audit_country_semantic_drift(slug: str) -> Optional[Dict[str, Any]]:
    """Empirical per-country audit — returns stats dict or None if
    country has no ssi-data.json or no migration_score coverage.

    Semantic-drift detection: min < 0 OR max > 1 indicates rescale needed.
    """
    if not _HAS_SHARDING:
        raise RuntimeError("ssi_data_sharding utility not importable")

    ssi_path = REPO_ROOT / slug / "ssi-data.json"
    if not ssi_path.exists():
        return None

    data = read_ssi_data(ssi_path)
    subs = data.get("substations", [])

    scores = []
    for sub in subs:
        se = sub.get("socio_economic") or {}
        v = se.get("migration_score")
        if v is not None:
            scores.append(v)

    if not scores:
        return {
            "slug": slug,
            "n_total": len(subs),
            "n_populated": 0,
            "has_drift": False,
            "reason": "no migration_score coverage",
        }

    v_min = min(scores)
    v_max = max(scores)
    unique = len(set(scores))
    has_drift = (v_min < MIN_ENVELOPE) or (v_max > MAX_ENVELOPE)

    return {
        "slug": slug,
        "n_total": len(subs),
        "n_populated": len(scores),
        "unique_values": unique,
        "min": round(v_min, 6),
        "max": round(v_max, 6),
        "range_span": round(v_max - v_min, 6),
        "has_drift": has_drift,
    }


# ═════════════════════════════════════════════════════════════════════
#  Per-country normalization apply
# ═════════════════════════════════════════════════════════════════════

def normalise_country(
    slug: str,
    *,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Apply per-country min-max linear rescale to migration_score.

    Convention preservation:
      - Task #452 _migration_score_source marker preserved (merge-not-replace)
      - Task #451 _catchment_population_source marker preserved
      - Task #450 _migration_score_semantic_normalise_source added per sub
      - Idempotent: subs with existing Task #450 marker are skipped
      - Convention #56: degenerate case (min == max) → skip country
    """
    if not _HAS_SHARDING:
        raise RuntimeError("ssi_data_sharding utility not importable")

    t0 = time.time()
    ssi_path = REPO_ROOT / slug / "ssi-data.json"
    if not ssi_path.exists():
        raise FileNotFoundError(f"[{slug}] ssi-data.json not found")

    log.info(f"[{slug}] loading ssi-data.json...")
    data = read_ssi_data(ssi_path)
    subs = data.get("substations", [])
    n = len(subs)
    log.info(f"[{slug}] {n:,} subs loaded in {time.time()-t0:.1f}s")

    # ── Pre-compute per-country min/max (exclude already-normalised subs) ──
    raw_scores = []
    for sub in subs:
        se = sub.get("socio_economic") or {}
        # Skip subs already normalised (idempotency)
        if se.get(AUDIT_TRAIL_KEY) == AUDIT_TRAIL_VALUE:
            continue
        v = se.get("migration_score")
        if v is not None:
            raw_scores.append(v)

    if not raw_scores:
        return {
            "country": slug,
            "n_substations": n,
            "n_populated": 0,
            "n_written": 0,
            "reason": "no un-normalised migration_score to process",
            "dry_run": dry_run,
        }

    v_min = min(raw_scores)
    v_max = max(raw_scores)
    range_span = v_max - v_min

    # Convention #56 degenerate case
    if range_span == 0:
        log.warning(f"[{slug}] degenerate range (min == max = {v_min}) — Convention #56 skip")
        return {
            "country": slug,
            "n_populated": len(raw_scores),
            "n_written": 0,
            "min_pre": v_min,
            "max_pre": v_max,
            "reason": "degenerate range (min==max) — Convention #56 skip",
            "dry_run": dry_run,
        }

    # Semantic-drift check — if already in [0, 1], skip country
    if v_min >= MIN_ENVELOPE and v_max <= MAX_ENVELOPE:
        log.info(f"[{slug}] already in [0, 1] envelope — no rescale needed")
        return {
            "country": slug,
            "n_populated": len(raw_scores),
            "n_written": 0,
            "min_pre": v_min,
            "max_pre": v_max,
            "reason": "already in [0, 1] envelope",
            "dry_run": dry_run,
        }

    log.info(f"[{slug}] rescaling {len(raw_scores):,} subs — "
             f"[{v_min:.4f}, {v_max:.4f}] → [0, 1]")

    # ── Apply rescale ──────────────────────────────────────────────
    n_written = 0
    n_already_normalised = 0
    task_451_preserved = 0
    task_452_preserved = 0

    for sub in subs:
        se = sub.get("socio_economic") or {}

        # Skip already-normalised (idempotency)
        if se.get(AUDIT_TRAIL_KEY) == AUDIT_TRAIL_VALUE:
            n_already_normalised += 1
            continue

        v = se.get("migration_score")
        if v is None:
            continue

        # Linear rescale
        new_score = (v - v_min) / range_span
        # Clip to [0, 1] just in case of floating-point drift
        new_score = max(0.0, min(1.0, new_score))
        # Round to 6 sig figs (Task #452 precedent)
        new_score = round(new_score, 6)

        # Track pre-existing markers for audit
        if se.get(TASK_451_MARKER):
            task_451_preserved += 1
        if se.get(TASK_452_MARKER):
            task_452_preserved += 1

        # Rewrite score + add audit marker + preserve Task #451/#452 markers
        se["migration_score"] = new_score
        se[AUDIT_TRAIL_KEY] = AUDIT_TRAIL_VALUE
        sub["socio_economic"] = se

        n_written += 1

    if dry_run:
        log.info(f"[{slug}] DRY-RUN — no write")
    else:
        log.info(f"[{slug}] writing ssi-data.json...")
        write_ssi_data(data, ssi_path)
        log.info(f"[{slug}] saved.")

    elapsed = time.time() - t0
    return {
        "country": slug,
        "mode": "min_max_linear_rescale",
        "n_substations": n,
        "n_populated": len(raw_scores),
        "n_written": n_written,
        "n_already_normalised": n_already_normalised,
        "min_pre": v_min,
        "max_pre": v_max,
        "range_span_pre": range_span,
        "task_451_markers_preserved": task_451_preserved,
        "task_452_markers_preserved": task_452_preserved,
        "wall_clock_sec": round(elapsed, 2),
        "dry_run": dry_run,
    }


# ═════════════════════════════════════════════════════════════════════
#  CLI entry point
# ═════════════════════════════════════════════════════════════════════

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="migration_score_semantic_normalise.py",
        description="Task #450 SYSTEMIC bridge — per-country min-max "
                    "linear rescale for migration_score semantic-drift countries",
    )
    parser.add_argument("slug", nargs="?", default=None,
                        help="Country slug (single-country mode)")
    parser.add_argument("--cohort", action="store_true",
                        help="Apply to full 5-country target cohort")
    parser.add_argument("--dry-run", action="store_true",
                        help="Compute rescale but don't write to disk")
    parser.add_argument("--diagnose-only", action="store_true",
                        help="Empirical audit only — no rescale")
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if args.diagnose_only:
        # Cohort-wide diagnostic
        cohort_slugs = json.load(
            open(REPO_ROOT / "intelligence" / "countries.json")
        )["slugs"]
        log.info(f"Diagnosing {len(cohort_slugs)} countries for semantic-drift...")
        drift_reports = []
        for slug in cohort_slugs:
            r = audit_country_semantic_drift(slug)
            if r and r.get("has_drift"):
                drift_reports.append(r)
        print()
        print(f"Semantic-drift instances: {len(drift_reports)}")
        for r in drift_reports:
            print(f"  {r['slug']:14} n={r['n_populated']:>6} unique={r['unique_values']:>5} "
                  f"range=[{r['min']:>+8.4f}, {r['max']:>+8.4f}]")
        return 0

    # Determine target set
    if args.cohort:
        targets = list(TARGET_COHORT)
    elif args.slug:
        targets = [args.slug]
    else:
        parser.print_help()
        return 1

    # Execute
    reports = []
    total_written = 0
    for slug in targets:
        log.info(f"═══ {slug} ═══")
        try:
            r = normalise_country(slug, dry_run=args.dry_run)
            reports.append(r)
            if r.get("n_written"):
                total_written += r["n_written"]
                print()
                print(f"─── {slug} (min={r['min_pre']:.4f} → max={r['max_pre']:.4f}) ───")
                print(f"  n_written                        {r['n_written']:>7,}")
                print(f"  n_already_normalised             {r['n_already_normalised']:>7,}")
                print(f"  Task #451 markers preserved:     {r['task_451_markers_preserved']:>7,}")
                print(f"  Task #452 markers preserved:     {r['task_452_markers_preserved']:>7,}")
                print(f"  Wall-clock:                      {r['wall_clock_sec']:>7.2f}s")
        except Exception as e:
            log.error(f"[{slug}] FAILED: {e}")
            reports.append({"country": slug, "error": str(e)})

    # Write consolidated audit report
    audit_out = Path.home() / f"migration_score_semantic_normalise_audit_{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}.json"
    with open(audit_out, "w") as f:
        json.dump({
            "task_id": "#450-SYSTEMIC-bridge",
            "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "dry_run": args.dry_run,
            "targets": targets,
            "total_written": total_written,
            "reports": reports,
        }, f, indent=2, default=str)
    log.info(f"")
    log.info(f"✓ Consolidated audit report: {audit_out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
