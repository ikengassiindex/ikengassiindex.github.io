#!/usr/bin/env python3
"""
SSI Pipeline — Provenance Backfill Tool (Phase 1 PR-7)

Reads each country's ssi-data.json, computes PR-3 provenance fields
(mult_product, add_sum, modifier_impacts) for every substation via the
canonical modifier_registry chain, writes back atomically.

Convention #56 — SAFE ADDITIVE CHANGE:
  • Existing fields preserved (R_median, R_P5, R_P95, classification,
    components, modifiers, etc.)
  • Three new top-level keys added per substation
  • Backup snapshot created at <country>/ssi-data.json.pre-pr7-backup
    before write-back so the PR-7 score-shift acceptance harness has a
    baseline to diff against
  • Idempotent: re-running on a file that already carries the provenance
    fields produces byte-identical output

Architectural pin: this tool is NOT a substitute for the operator's
full --all pipeline refresh. It backfills the PR-3 provenance schema
extension onto the EXISTING modifier values; it does NOT re-clip
out-of-range modifiers or re-compute R_median. The F-L4-2 cohort
mitigations (Class A pipeline drift in CO/CR; Class B R7_cyber drift
in IL/IS/HU/SK) are resolved on the next --all refresh per
PHASE_1_ACCEPTANCE_REPORT.md §F-L4-2.

Usage:
  python3 scripts/backfill_provenance.py <country>      # one country
  python3 scripts/backfill_provenance.py --all          # every SoT country
  python3 scripts/backfill_provenance.py --dry-run --all  # show what would change
  python3 scripts/backfill_provenance.py --verify italy   # check provenance present
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def _load_modifier_registry():
    """Import compute_modifier_terms + per_modifier_impacts from the canonical
    pipeline module. We attempt the proper package import first; fall back to
    direct file-load so this tool works in environments where
    scripts/pipeline is not on PYTHONPATH."""
    try:
        from scripts.pipeline.scoring.modifier_registry import (
            compute_modifier_terms, per_modifier_impacts,
        )
    except ImportError:
        # Direct file-load fallback
        import importlib.util
        mr_path = (REPO_ROOT / "scripts" / "pipeline" / "scoring"
                              / "modifier_registry.py")
        spec = importlib.util.spec_from_file_location(
            "_mr_canonical", mr_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        compute_modifier_terms = mod.compute_modifier_terms
        per_modifier_impacts = mod.per_modifier_impacts
    return compute_modifier_terms, per_modifier_impacts


def _backfill_substation(sub, compute_terms, per_impacts):
    """In-place: add mult_product, add_sum, modifier_impacts. Idempotent."""
    mods = sub.get("modifiers", {})
    if not isinstance(mods, dict):
        # Defensive: skip substations with malformed modifier blocks
        return False
    mult_product, add_sum = compute_terms(mods)
    sub["mult_product"] = round(float(mult_product), 4)
    sub["add_sum"] = round(float(add_sum), 4)
    sub["modifier_impacts"] = per_impacts(mods)
    return True


def backfill_country(country, dry_run=False, verbose=True):
    """Backfill provenance fields across one country's substations.

    Returns dict with counts: total / updated / skipped / preexisting.
    """
    fp = REPO_ROOT / country / "ssi-data.json"
    if not fp.exists():
        return {"country": country, "status": "missing"}

    compute_terms, per_impacts = _load_modifier_registry()
    data = json.loads(fp.read_text(encoding="utf-8"))
    subs = data.get("substations", [])
    if isinstance(subs, dict):
        subs_list = list(subs.values())
    elif isinstance(subs, list):
        subs_list = subs
    else:
        return {"country": country, "status": "no_substations"}

    total = len(subs_list)
    updated = 0
    skipped = 0
    preexisting = 0
    for s in subs_list:
        # Idempotency check: skip if all 3 fields already present + valid
        if ("mult_product" in s and "add_sum" in s
                and "modifier_impacts" in s
                and isinstance(s["modifier_impacts"], dict)):
            preexisting += 1
            continue
        ok = _backfill_substation(s, compute_terms, per_impacts)
        if ok:
            updated += 1
        else:
            skipped += 1

    # Atomic write-back: backup first, then overwrite. Skip write entirely
    # on dry-run.
    if not dry_run and updated > 0:
        backup_fp = fp.with_suffix(".json.pre-pr7-backup")
        if not backup_fp.exists():
            shutil.copy2(fp, backup_fp)
        # Write back. We've mutated `subs_list` in place; for the dict-shape
        # case the original ref is preserved.
        tmp_fp = fp.with_suffix(".json.tmp")
        tmp_fp.write_text(
            json.dumps(data, ensure_ascii=False, indent=None),
            encoding="utf-8",
        )
        tmp_fp.replace(fp)

    if verbose:
        action = "WOULD update" if dry_run else "updated"
        print(
            f"  {country}: {action} {updated}/{total} substations "
            f"(skipped {skipped}, preexisting {preexisting})"
        )

    return {
        "country": country,
        "status": "ok",
        "total": total,
        "updated": updated,
        "preexisting": preexisting,
        "skipped": skipped,
    }


def verify_country(country):
    """Verify all substations in one country carry the 3 PR-3 fields."""
    fp = REPO_ROOT / country / "ssi-data.json"
    if not fp.exists():
        return {"country": country, "status": "missing"}
    data = json.loads(fp.read_text(encoding="utf-8"))
    subs = data.get("substations", [])
    if isinstance(subs, dict):
        subs = list(subs.values())
    total = len(subs)
    missing_counts = {"mult_product": 0, "add_sum": 0, "modifier_impacts": 0}
    for s in subs:
        for f in missing_counts:
            if f not in s:
                missing_counts[f] += 1
    all_present = all(c == 0 for c in missing_counts.values())
    print(
        f"  {country}: {total} substations, "
        f"missing fields: {missing_counts} "
        f"→ {'✓ COMPLETE' if all_present else '✗ INCOMPLETE'}"
    )
    return {
        "country": country, "total": total,
        "missing": missing_counts, "complete": all_present,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    parser.add_argument("target", nargs="?",
                        help="Country slug (e.g. 'italy') or omit with --all")
    parser.add_argument("--all", action="store_true",
                        help="Backfill every SoT country")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change; don't write")
    parser.add_argument("--verify", action="store_true",
                        help="Verify provenance present; no backfill")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress per-country lines; just final summary")
    args = parser.parse_args()

    sot = json.loads(
        (REPO_ROOT / "intelligence" / "countries.json").read_text())
    countries = sorted(sot["slugs"])

    if args.target and args.all:
        parser.error("Specify either a target country OR --all, not both")
    if not args.target and not args.all and not args.verify:
        parser.error("Need a target country, --all, or --verify <slug>")

    targets = countries if args.all else [args.target]
    if args.verify and args.target:
        targets = [args.target]
    elif args.verify and args.all:
        targets = countries

    mode = "VERIFY" if args.verify else ("DRY-RUN" if args.dry_run else "BACKFILL")
    print(f"\n═══ Provenance {mode} ({len(targets)} countries) ═══")

    results = []
    for c in targets:
        try:
            if args.verify:
                results.append(verify_country(c))
            else:
                results.append(backfill_country(
                    c, dry_run=args.dry_run, verbose=not args.quiet))
        except Exception as e:
            print(f"  {c}: ERROR — {e}")
            results.append({"country": c, "status": "error", "error": str(e)})

    # Final summary
    print(f"\n═══ Summary ═══")
    ok = [r for r in results if r.get("status") == "ok"]
    err = [r for r in results if r.get("status") == "error"]
    missing = [r for r in results if r.get("status") == "missing"]
    if not args.verify:
        total_updated = sum(r.get("updated", 0) for r in ok)
        total_pre = sum(r.get("preexisting", 0) for r in ok)
        total_sub = sum(r.get("total", 0) for r in ok)
        print(f"  Countries processed OK: {len(ok)}")
        print(f"  Countries missing ssi-data.json: {len(missing)}")
        print(f"  Countries with errors: {len(err)}")
        print(f"  Substations updated: {total_updated}")
        print(f"  Substations preexisting (idempotent): {total_pre}")
        print(f"  Total substations seen: {total_sub}")
    else:
        complete = sum(1 for r in results if r.get("complete"))
        print(f"  Countries complete: {complete}/{len(results)}")

    if err:
        sys.exit(1)


if __name__ == "__main__":
    main()
