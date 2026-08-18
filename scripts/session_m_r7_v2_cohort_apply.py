#!/usr/bin/env python3
"""session_m_r7_v2_cohort_apply.py — Task #1145 (18 August 2026)

Session M — cohort-wide APPLY of R7_cyber v2 (v0 first apply) to the
39-country cohort per operator Gate B sign-off 18 Aug 2026 (accelerated
cadence per Session L brief operator decision).

Operator Gate B sign-offs (18 August 2026)
------------------------------------------
- **B-1a** — Accept Gate A default weights w_entity=0.55, w_product=0.45
  (dormant at v0 since product-layer is Convention #56 fallback cohort-wide
  until 11 Dec 2027 CRA full applicability).
- **B-2a** — Accept 66.7% Convention #56 input-cell fallback rate.
- **B-3a** — Proceed with all 39 countries — no anomalies to reject.
- **B-5a** — Single atomic commit for the full apply (Session M) + tooltip
  cascade extension (36 net-new intelligence.html files).

Contract (BINDING at write layer)
---------------------------------
For every substation in every country ssi-data.json:

- ``sub["modifiers"]["R7_cyber_v2"]`` = R7 v2 value (float in [0.99, 1.05])
  when the country register produces a computable value, else Convention
  #56 identity fallback 1.0 (still float, per module contract).
- ``sub["_r7_cyber_v2_source"]`` = ``AUDIT_TRAIL_VALUE`` marker.
- ``sub["_r7_cyber_v2_fallback_reason"]`` = machine-parseable reason string
  when a Convention #56 fallback path was taken (else absent).
- ``sub["_r7_cyber_v1_retired"]`` = False (dual-write per GATE-A-11
  ~6-month transition; v1 remains live + emitted).
- ``sub["_r7_cyber_v1_value"]`` = snapshot of ``sub["modifiers"]["R7_cyber"]``
  taken at first-apply time (Convention #56 audit trail).
- ``sub["modifiers"]["R7_cyber"]`` — NEVER MODIFIED (BINDING per GATE-A-11).

Cache-bust markers on each country manifest (top-level ``meta`` key):

- ``meta["r7_cyber_v2_first_apply_timestamp"]`` — ISO UTC apply time.
- ``meta["r7_cyber_v2_first_apply_gate_b_signoffs"]`` — dict of B-1a..B-5a.

Convention preservation
-----------------------
- **#7** — CRA + NIS2 documented-proxy anchors delegated to
  r7_cyber_v2.py + cra_nis2_register.json + r7_cyber_v2_inputs.json.
- **#55** — Verify-don't-trust: sentinel re-run REQUIRED post-apply.
- **#56** — Visibly-honest fallback markers on every substation.
- **#78** §5septies BINDING — L1 ingestion untouched.
- **#79** — Sharded countries (france/germany/uk/us/italy) preserved via
  ``_ssi_data_shard_reader.load_ssi_data`` + ``save_ssi_data``.

Usage
-----
  python3 scripts/session_m_r7_v2_cohort_apply.py               # full cohort
  python3 scripts/session_m_r7_v2_cohort_apply.py --dry-run     # no writes
  python3 scripts/session_m_r7_v2_cohort_apply.py --slug spain  # single country
  python3 scripts/session_m_r7_v2_cohort_apply.py --json-out audit.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

# Load modules AFTER sys.path insertion.
from scripts._ssi_data_shard_reader import load_ssi_data, save_ssi_data  # noqa: E402
from scripts.pipeline.scoring import r7_cyber_v2 as m  # noqa: E402

SOT = REPO_ROOT / "intelligence" / "countries.json"

GATE_B_SIGNOFFS = {
    "B-1a": "weights_gate_a_default_w_entity_0.55_w_product_0.45",
    "B-2a": "convention_56_fallback_rate_66.7_accepted",
    "B-3a": "proceed_all_39_countries_no_anomalies",
    "B-4a": "tooltip_cascade_extended_pilot_to_full_cohort",
    "B-5a": "single_atomic_commit_tree_1",
    "operator": "Cédric Bérard",
    "signoff_date": "2026-08-18",
    "session_L_brief_ref": (
        "SSI Index/Upgrade Methodology Rulebook/01-R7-Cyber-v2-CRA-Integration/"
        "R7_V2_GATE_B_DECISION_BRIEF_20260818.md"
    ),
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def apply_to_country(
    slug: str,
    dry_run: bool,
    apply_timestamp: str,
) -> Dict[str, Any]:
    """Apply R7 v2 to one country. Returns a per-country audit dict."""
    t_start = time.perf_counter()
    country_inputs = m.load_country_inputs(slug)
    data, substations, is_sharded = load_ssi_data(slug)

    summary: Dict[str, Any] = {
        "slug": slug,
        "path_variant": m.resolve_path_variant(slug),
        "inputs_present": country_inputs is not None,
        "is_sharded_convention_79": is_sharded,
        "n_substations": len(substations),
        "n_populated_v2": 0,
        "n_fallback_identity": 0,
        "fallback_reason_distribution": {},
        "r7_v2_values": [],
        "r7_v1_values_snapshot": [],
        "v1_retired_all_false": True,  # BINDING per GATE-A-11
        "v1_marker_missing_count": 0,
        "wall_clock_sec": 0.0,
        "wrote_ssi_data": False,
    }

    audit_key = m.AUDIT_TRAIL_KEY
    audit_val = m.AUDIT_TRAIL_VALUE
    fallback_key = m.FALLBACK_KEY
    v1_retired_key = m.V1_RETIRED_KEY
    v1_value_key = m.V1_VALUE_KEY
    registry_key = m.REGISTRY_KEY

    for sub in substations:
        modifiers = sub.setdefault("modifiers", {})
        v1_val = modifiers.get("R7_cyber")

        r7_v2, audit_meta = m.compute_r7_cyber_v2_for_sub(sub, country_inputs)

        # Write R7 v2 modifier sibling (dual-write per GATE-A-11).
        modifiers[registry_key] = r7_v2

        # Audit trail marker (present on every substation post-apply).
        sub[audit_key] = audit_val

        # Fallback reason marker — populated only when a fallback path fires.
        reason = audit_meta.get("fallback_reason") or ""
        if reason:
            sub[fallback_key] = reason
            summary["fallback_reason_distribution"][reason] = (
                summary["fallback_reason_distribution"].get(reason, 0) + 1
            )
        elif fallback_key in sub:
            # Clean up any stale marker if a prior run wrote one.
            del sub[fallback_key]

        # Dual-write transition markers (v1 remains live per GATE-A-11).
        sub[v1_retired_key] = False  # BINDING at v0 first apply.
        if v1_val is None:
            summary["v1_marker_missing_count"] += 1
        else:
            sub[v1_value_key] = v1_val
            try:
                summary["r7_v1_values_snapshot"].append(float(v1_val))
            except (TypeError, ValueError):
                pass

        # Classification for cohort roll-up.
        if reason in ("no_country_inputs", "no_entity_no_product_data"):
            summary["n_fallback_identity"] += 1
        else:
            summary["n_populated_v2"] += 1
        # Always record the value for envelope + distribution analysis.
        if r7_v2 is not None:
            try:
                summary["r7_v2_values"].append(float(r7_v2))
            except (TypeError, ValueError):
                pass

    # Manifest cache-bust markers (top-level ``meta``).
    manifest_meta = data.setdefault("meta", {})
    if not isinstance(manifest_meta, dict):
        # Convention #56 preservation — surface but do not overwrite non-dict.
        manifest_meta = {"_pre_r7_v2_meta_non_dict": True}
        data["meta"] = manifest_meta
    manifest_meta["r7_cyber_v2_first_apply_timestamp"] = apply_timestamp
    manifest_meta["r7_cyber_v2_first_apply_gate_b_signoffs"] = dict(GATE_B_SIGNOFFS)
    manifest_meta["r7_cyber_v2_first_apply_task_ids"] = [
        "1102", "1107", "1118", "1134", "1140", "1141", "1142", "1145",
    ]
    manifest_meta["r7_cyber_v2_first_apply_module_version"] = audit_val

    if not dry_run:
        # Convention #79 sharding preserved by shard-reader utility.
        save_ssi_data(slug, data, substations)
        summary["wrote_ssi_data"] = True

    summary["wall_clock_sec"] = round(time.perf_counter() - t_start, 3)
    return summary


def _stats(vals: List[float]) -> Dict[str, Any]:
    if not vals:
        return {"n": 0}
    sv = sorted(vals)
    return {
        "n": len(vals),
        "mean": round(statistics.mean(vals), 6),
        "median": round(statistics.median(vals), 6),
        "min": round(sv[0], 6),
        "max": round(sv[-1], 6),
        "p5": round(sv[max(0, int(len(sv) * 0.05))], 6),
        "p95": round(sv[min(len(sv) - 1, int(len(sv) * 0.95))], 6),
        "stdev": round(statistics.pstdev(vals), 6) if len(vals) > 1 else 0.0,
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Session M — cohort-wide R7 v2 first apply (Task #1145)"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Compute + audit only; do NOT write ssi-data.json.")
    parser.add_argument("--slug", type=str, default=None,
                        help="Apply to a single country (else full 39-cohort).")
    parser.add_argument("--json-out", type=str, default=None,
                        help="Path to write consolidated audit JSON.")
    args = parser.parse_args(argv)

    slugs = json.loads(SOT.read_text())["slugs"]
    if args.slug:
        assert args.slug in slugs, f"unknown slug: {args.slug}"
        slugs = [args.slug]

    apply_timestamp = _now_iso()
    print(f"Session M · R7 v2 cohort apply · timestamp {apply_timestamp}")
    print(f"  dry_run={args.dry_run}  cohort={len(slugs)}")
    print("-" * 78)

    per_country = []
    total_subs = 0
    total_populated = 0
    total_fallback = 0
    total_wall_clock = 0.0
    sharded_slugs = []
    all_r7_v2 = []
    all_v1_snapshots = []
    all_v2_minus_v1 = []

    for slug in slugs:
        try:
            s = apply_to_country(slug, dry_run=args.dry_run,
                                 apply_timestamp=apply_timestamp)
        except Exception as exc:  # noqa: BLE001 — surface per Convention #56
            print(f"  [{slug:16s}] FAILED: {exc}")
            per_country.append({"slug": slug, "error": str(exc)})
            continue

        per_country.append({
            k: v for k, v in s.items()
            # Trim the per-country per-substation lists from the roll-up dict
            # (keep only distribution stats). Full lists roll up cohort-wide.
            if k not in ("r7_v2_values", "r7_v1_values_snapshot")
        })
        # Cohort roll-up.
        all_r7_v2.extend(s["r7_v2_values"])
        all_v1_snapshots.extend(s["r7_v1_values_snapshot"])
        # Compute per-sub v2−v1 divergence (aligned lists).
        n_pairs = min(len(s["r7_v2_values"]), len(s["r7_v1_values_snapshot"]))
        for i in range(n_pairs):
            try:
                all_v2_minus_v1.append(
                    float(s["r7_v2_values"][i]) - float(s["r7_v1_values_snapshot"][i])
                )
            except (TypeError, ValueError):
                pass
        total_subs += s["n_substations"]
        total_populated += s["n_populated_v2"]
        total_fallback += s["n_fallback_identity"]
        total_wall_clock += s["wall_clock_sec"]
        if s["is_sharded_convention_79"]:
            sharded_slugs.append(slug)

        marker = "SHARDED" if s["is_sharded_convention_79"] else "single"
        wrote = "WROTE" if s["wrote_ssi_data"] else ("DRY-RUN" if args.dry_run else "SKIP")
        print(
            f"  [{slug:16s}] {marker:7s} n={s['n_substations']:>7d}  "
            f"pop={s['n_populated_v2']:>7d} fb={s['n_fallback_identity']:>6d}  "
            f"v1_snap={len(s['r7_v1_values_snapshot']):>7d}  "
            f"{wrote}  ({s['wall_clock_sec']}s)"
        )

    print("-" * 78)
    print(f"Cohort roll-up: n_subs={total_subs}  "
          f"populated={total_populated} ({total_populated/total_subs*100:.2f}%)  "
          f"fallback_identity={total_fallback} ({total_fallback/total_subs*100:.2f}%)")
    print(f"  Convention #79 sharded countries: {sharded_slugs}")
    print(f"  R7 v2 distribution: {_stats(all_r7_v2)}")
    print(f"  R7 v1 distribution (dual-write snapshot): {_stats(all_v1_snapshots)}")
    print(f"  Divergence (v2 − v1) distribution: {_stats(all_v2_minus_v1)}")
    print(f"  Wall-clock total: {round(total_wall_clock, 2)}s")

    payload = {
        "session": "Session M · R7 v2 cohort apply · Task #1145",
        "session_date": "2026-08-18",
        "apply_timestamp": apply_timestamp,
        "dry_run": args.dry_run,
        "gate_b_signoffs": GATE_B_SIGNOFFS,
        "cohort_size": len(slugs),
        "total_substations": total_subs,
        "total_populated_v2": total_populated,
        "total_fallback_identity": total_fallback,
        "populate_rate_pct": round(total_populated / total_subs * 100, 4) if total_subs else 0.0,
        "fallback_rate_pct": round(total_fallback / total_subs * 100, 4) if total_subs else 0.0,
        "sharded_convention_79_slugs": sharded_slugs,
        "cohort_r7_v2_distribution": _stats(all_r7_v2),
        "cohort_r7_v1_snapshot_distribution": _stats(all_v1_snapshots),
        "cohort_v2_minus_v1_divergence": _stats(all_v2_minus_v1),
        "per_country": per_country,
    }

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n"
        )
        print(f"Audit JSON: {args.json_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
