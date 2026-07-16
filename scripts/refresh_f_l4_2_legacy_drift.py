#!/usr/bin/env python3
"""
SSI v4.0.2 — F-L4-2-extended legacy-drift SURGICAL refresher

Closes the 6 Filing 4 F-L4-2-extended xfails (colombia, costa-rica, hungary,
iceland, israel, slovakia) via MINIMAL-IMPACT patches to the two validator
gates that trip:

  Gate 1 — MODIFIER-RANGE  (R7_cyber, R6_restoration, R6_volcanic, etc.):
    Fix: clip stored modifier values to validate_schema._MODIFIER_RANGES.
    Does NOT touch R_median (compute_modifier_terms already re-clips at
    runtime, so this only aligns the stored snapshot with the validator).

  Gate 2 — CLASSIFICATION-BAND  (classification string vs band-of-R_median):
    Fix: re-classify each substation per classify_band(stored_R_median).
    Does NOT recompute R_median itself.

Why surgical rather than full re-emit:
  The score-shift acceptance harness (tests/test_score_shift_acceptance.py)
  pins post-PR-3 mean R_median to drift no worse than -2% vs the PR-7
  baseline. A full re-emit via score_substation() recomputes R_base from
  components — and colombia's stored R_base_median is 0.42 vs the
  canonical-engine recomputed 0.30 (-30%), which would fail the gate.
  That deeper R_base drift is a separate issue (logged as the v4.5 R_base
  recomputation followup).  THIS script does not address it.

What this script does NOT do:
  - Recompute R_base, R_median, P5/P95, CI_width, P_critical, skewness
  - Touch the PR-3 provenance fields (mult_product, add_sum, modifier_impacts)
  - Modify ingestion data on disk
  - Change the modifier registry or validator ranges

Idempotent: re-running once the file is clean produces byte-identical output.
Atomic: backup `.pre-f-l4-2-refresh-backup` is created before write-back.

Usage:
  python3 scripts/refresh_f_l4_2_legacy_drift.py colombia
  python3 scripts/refresh_f_l4_2_legacy_drift.py --all-filing-4
  python3 scripts/refresh_f_l4_2_legacy_drift.py --dry-run --all-filing-4
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from scripts.pipeline.scoring.engine import classify_band
from validate_schema import _MODIFIER_RANGES, _MODIFIER_RANGE_TOLERANCE, validate_file


FILING_4_F_L4_2 = ["colombia", "costa-rica", "hungary", "iceland", "israel", "slovakia"]


def clip_modifiers_to_validator_ranges(sub: dict) -> int:
    """Clip stored modifiers to validator declared range. Returns count clipped.

    Uses the validator's 2% tolerance band: if a value is within the tolerance
    of the boundary, leave it alone (the validator will pass it).  Outside the
    tolerance band, clip to the strict range boundary.  This preserves
    legitimate near-boundary values while fixing the systemic drift cases."""
    mods = sub.get("modifiers", {})
    if not isinstance(mods, dict):
        return 0
    n_clipped = 0
    tol = _MODIFIER_RANGE_TOLERANCE
    for name, value in list(mods.items()):
        rng = _MODIFIER_RANGES.get(name)
        if rng is None or not isinstance(value, (int, float)):
            continue
        lo, hi = rng
        v = float(value)
        # Validator tolerance window: lo*(1-tol) .. hi*(1+tol)
        lo_tol = lo * (1 - tol)
        hi_tol = hi * (1 + tol)
        if v < lo_tol or v > hi_tol:
            # Out-of-tolerance: clip to strict boundary
            clipped = max(lo, min(hi, v))
            mods[name] = round(clipped, 4)
            n_clipped += 1
    return n_clipped


def reclassify_from_stored_r_median(sub: dict) -> bool:
    """Re-derive classification from stored R_median via canonical classify_band.
    Returns True if the classification string changed."""
    r_med = sub.get("R_median")
    if not isinstance(r_med, (int, float)):
        return False
    old_class = sub.get("classification", "Medium")
    new_class = classify_band(r_med)
    if new_class != old_class:
        sub["classification"] = new_class
        return True
    return False


def refresh_country(country: str, dry_run: bool = False):
    fp = REPO_ROOT / country / "ssi-data.json"
    if not fp.exists():
        return {"country": country, "status": "missing"}

    data = json.loads(fp.read_text(encoding="utf-8"))
    raw_subs = data.get("substations", [])

    # Handle compact-array format
    compact_format = False
    sub_fields = []
    if raw_subs and isinstance(raw_subs[0], list):
        compact_format = True
        sub_fields = data.get("sub_fields", [])
        if not sub_fields:
            return {"country": country, "status": "compact_no_fields"}
        subs = []
        for arr in raw_subs:
            d = {}
            for i, field in enumerate(sub_fields):
                if i < len(arr):
                    d[field] = arr[i]
            subs.append(d)
    else:
        subs = raw_subs

    total = len(subs)
    n_clipped_subs = 0
    n_total_clips = 0
    n_reclassified = 0
    class_shifts = {}

    for sub in subs:
        n_clips = clip_modifiers_to_validator_ranges(sub)
        if n_clips > 0:
            n_clipped_subs += 1
            n_total_clips += n_clips
        old_class = sub.get("classification", "Medium")
        if reclassify_from_stored_r_median(sub):
            new_class = sub.get("classification", "Medium")
            n_reclassified += 1
            key = f"{old_class}→{new_class}"
            class_shifts[key] = class_shifts.get(key, 0) + 1

    # Repack into compact format if needed
    if compact_format:
        out_subs = []
        for sub in subs:
            arr = [sub.get(f, None) for f in sub_fields]
            out_subs.append(arr)
        data["substations"] = out_subs
    else:
        data["substations"] = subs

    # Update fleet_summary classification distribution if present
    if "fleet_summary" in data:
        bands = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
        for sub in subs:
            c = sub.get("classification", "Medium")
            bands[c] = bands.get(c, 0) + 1
        if "classification_distribution" in data["fleet_summary"]:
            data["fleet_summary"]["classification_distribution"] = bands

    result = {
        "country": country,
        "status": "ok",
        "total": total,
        "modifier_subs_clipped": n_clipped_subs,
        "modifier_total_clips": n_total_clips,
        "reclassified": n_reclassified,
        "class_shifts": class_shifts,
    }

    if dry_run:
        result["status"] = "dry_run"
        return result

    # Backup + atomic write
    backup_fp = fp.with_suffix(".json.pre-f-l4-2-refresh-backup")
    if not backup_fp.exists():
        shutil.copy2(fp, backup_fp)
        result["backup_created"] = str(backup_fp.name)

    tmp_fp = fp.with_suffix(".json.tmp")
    # Compact serialisation (no indent) — aligns with cohort-wide ssi-data.json
    # discipline + prevents Task #125 90-MB sentinel trigger on large canonicals
    # (norway 13.6→19.1 MB indent=2, australia 21.5→29.7 MB indent=2; both stay
    # under threshold but format-drift misaligns with 39-country cohort norm).
    tmp_fp.write_text(
        json.dumps(data, default=str, ensure_ascii=False),
        encoding="utf-8",
    )
    tmp_fp.replace(fp)

    # Re-run the validator to confirm xfail-closing
    errors, warnings = validate_file(str(fp))
    result["validator_errors"] = errors
    result["validator_warnings_count"] = len(warnings)
    result["validation_status"] = "PASS" if not errors else "FAIL"

    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("countries", nargs="*",
                        help="Countries to refresh (canonical_id)")
    parser.add_argument("--all-filing-4", action="store_true",
                        help="Refresh all 6 Filing 4 F-L4-2-extended countries")
    parser.add_argument("--dry-run", action="store_true",
                        help="Compute changes but do NOT write to disk")
    args = parser.parse_args()

    if args.all_filing_4:
        countries = FILING_4_F_L4_2
    elif args.countries:
        countries = args.countries
    else:
        parser.error("Specify country names or --all-filing-4")

    print(f"\n{'═' * 72}")
    print(f"F-L4-2-extended SURGICAL REFRESH ({'DRY-RUN' if args.dry_run else 'LIVE'})")
    print(f"{'═' * 72}")
    print(f"Countries: {', '.join(countries)}\n")

    all_ok = True
    for c in countries:
        print(f"┌─ {c} ─")
        try:
            r = refresh_country(c, dry_run=args.dry_run)
            if r.get("status") == "missing":
                print(f"│  ⚠ MISSING — no ssi-data.json")
                all_ok = False
                continue
            print(f"│  Substations: {r['total']}")
            print(f"│  Modifiers re-clipped: {r['modifier_total_clips']} "
                  f"across {r['modifier_subs_clipped']} subs")
            print(f"│  Classifications re-derived: {r['reclassified']}")
            if r['class_shifts']:
                for shift, n in sorted(r['class_shifts'].items()):
                    print(f"│    {shift}: {n}")
            if r.get("backup_created"):
                print(f"│  Backup: {r['backup_created']}")
            if "validation_status" in r:
                status_glyph = "✅" if r["validation_status"] == "PASS" else "❌"
                print(f"│  Validator: {status_glyph} {r['validation_status']} "
                      f"({len(r.get('validator_errors', []))} errors, "
                      f"{r.get('validator_warnings_count', 0)} warnings)")
                if r["validation_status"] != "PASS":
                    for e in r["validator_errors"][:5]:
                        print(f"│    ERROR: {e[:120]}")
                    all_ok = False
        except Exception as e:
            print(f"│  ✗ EXCEPTION: {e}")
            all_ok = False
        print(f"└─")
        print()

    print(f"{'═' * 72}")
    if args.dry_run:
        print("DRY-RUN complete (no files written)")
    else:
        print(f"REFRESH {'COMPLETE — all GREEN' if all_ok else 'COMPLETE WITH FAILURES'}")
    print(f"{'═' * 72}\n")

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
