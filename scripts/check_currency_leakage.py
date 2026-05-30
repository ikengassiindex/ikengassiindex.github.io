#!/usr/bin/env python3
"""
check_currency_leakage.py — Discipline #19 (BPG Part XXXVIII, KB §71.14 / A1f).

Prevents A1f (currency-symbol leakage) by greppimg € in
intelligence/country-configs/<slug>.json for non-eurozone countries.

KOREA INCIDENT (May 29, 2026):
  - Hotfix #5: korea.json voll_range used € for all 4 R3 tiers (should be ₩)
  - Hotfix #6: intelligence-sections.js had €13.1/kWh ACER hardcoded narrative
  - Hotfix #7-issue2: map.js currSymbol IIFE defaulted to €

Three layers of currency leakage. This gate catches layer 1 at pre-flight.
Layers 2+3 are now closed by hotfix #6 (b2_voll_note/b2_narrative override)
and hotfix #7 (map.js prefers SSIMetadata.currency_symbol).

Usage:
  python3 scripts/check_currency_leakage.py             # check all non-eurozone configs
  python3 scripts/check_currency_leakage.py <slug>      # one slug
  python3 scripts/check_currency_leakage.py --strict    # exit 1 on any €
  python3 scripts/check_currency_leakage.py --list-non-eurozone

Eurozone members (currency_symbol = € expected): AT, BE, CY, DE, EE, ES, FI, FR,
  GR, IE, IT, LV, LT, LU, MT, NL, PT, SI, SK, HR, plus accession candidates.

Non-eurozone OECD countries (€ should NOT appear as PRIMARY in voll_range):
  AU CA CH CL CZ DK GB HU IS IL JP KR MX NO NZ PL SE TR US CR CO (final-3)

Note: € MAY appear as PARENTHETICAL comparator (e.g., "₩25,000/kWh (≈ €18/kWh)").
This script flags configs where € appears as the FIRST currency symbol in
voll_range or b2_voll_note (i.e., primary not parenthetical).
"""
import json
import re
import sys
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = REPO_ROOT / "intelligence" / "country-configs"

# Eurozone-19 (+ accession candidates) — € is PRIMARY currency, leakage OK
EUROZONE = {
    "austria", "belgium", "cyprus", "germany", "estonia", "spain", "finland",
    "france", "greece", "ireland", "italy", "latvia", "lithuania", "luxembourg",
    "malta", "netherlands", "portugal", "slovenia", "slovakia", "croatia",
}

# Non-eurozone — € must be parenthetical only (comparator), NOT primary
NON_EUROZONE_CANDIDATES = {
    # OECD non-eurozone members
    "australia", "canada", "switzerland", "chile", "czechia", "denmark", "uk",
    "hungary", "iceland", "israel", "japan", "korea", "mexico", "norway",
    "new-zealand", "poland", "sweden", "turkey", "us",
    # Final-3 OECD pending
    "costa-rica", "colombia",
    # OECD-adjacent
    "greenland",
}


def get_nested(d, path):
    """Get nested value by dot-path."""
    keys = path.split(".")
    val = d
    for k in keys:
        if not isinstance(val, dict):
            return None
        val = val.get(k)
        if val is None:
            return None
    return val


def check_config(slug):
    """Scan one country-config for € leakage. Returns list of findings."""
    path = CONFIG_DIR / f"{slug}.json"
    if not path.exists():
        return [{"slug": slug, "status": "MISSING", "msg": f"country-config not found at {path}"}]

    try:
        with open(path) as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        return [{"slug": slug, "status": "INVALID", "msg": f"JSON parse failed: {e}"}]

    findings = []

    # 1. Check r3_buckets voll_range — must NOT START with € (parenthetical OK)
    # Detection: if the FIRST 2 characters are "€" + digit/space → primary-€ leakage.
    # Country-native prefixes accepted: Kč, Ft (postfix), ₩, kr. (postfix), NZ$, CHF,
    #   ₺, A$, C$, $, £, ¥, Mex$, Kr (Nordic), zł (Polish), Ft (Hungarian), Lei, etc.
    r3_buckets = get_nested(config, "thresholds.r3_buckets") or []
    for i, bucket in enumerate(r3_buckets):
        voll = bucket.get("voll_range", "")
        if not voll:
            continue
        stripped = voll.lstrip()
        if stripped.startswith("€"):
            findings.append({
                "slug": slug,
                "status": "LEAKAGE",
                "msg": f"r3_buckets[{i}].voll_range starts with €: '{voll[:80]}'",
                "field": f"thresholds.r3_buckets[{i}].voll_range",
            })

    # 2. Check b2_voll_note (if present) — same rule
    b2_note = config.get("b2_voll_note", "")
    if b2_note:
        first_curr = re.search(r"[€₩£¥$]|kr\.|Ft", b2_note)
        if first_curr and first_curr.group(0) == "€":
            findings.append({
                "slug": slug,
                "status": "LEAKAGE",
                "msg": f"b2_voll_note starts with €: '{b2_note[:80]}'",
                "field": "b2_voll_note",
            })

    # 3. Check b2_narrative — same rule
    b2_narr = config.get("b2_narrative", "")
    if b2_narr:
        # Narrative may have € mentioned in different contexts; flag only if
        # there's an € price quote with no preceding country-native currency
        if "€" in b2_narr and not any(c in b2_narr for c in "₩£¥$"):
            # check for kr. (Iceland), Ft (Hungary)
            if "kr." not in b2_narr and "Ft" not in b2_narr:
                findings.append({
                    "slug": slug,
                    "status": "LEAKAGE",
                    "msg": f"b2_narrative has € but no country-native currency: '{b2_narr[:80]}...'",
                    "field": "b2_narrative",
                })

    # 4. Check top-level currency_symbol if present (positive check)
    cs = config.get("currency_symbol")
    if cs == "€":
        findings.append({
            "slug": slug,
            "status": "LEAKAGE",
            "msg": f"currency_symbol='€' on non-eurozone country",
            "field": "currency_symbol",
        })

    if not findings:
        findings.append({"slug": slug, "status": "PASS", "msg": ""})

    return findings


def main():
    args = sys.argv[1:]
    strict = "--strict" in args
    args = [a for a in args if a != "--strict"]

    if args and args[0] == "--list-non-eurozone":
        print("Non-eurozone OECD countries (€ must be parenthetical only):")
        for slug in sorted(NON_EUROZONE_CANDIDATES):
            print(f"  {slug}")
        sys.exit(0)

    # Determine target slugs
    if args:
        slugs_to_check = [args[0]]
    else:
        # All non-eurozone candidates that have a config file
        slugs_to_check = sorted([
            s for s in NON_EUROZONE_CANDIDATES
            if (CONFIG_DIR / f"{s}.json").exists()
        ])

    print(f"check_currency_leakage.py — Discipline #19 — checking {len(slugs_to_check)} non-eurozone configs")
    print()

    total_leakages = 0
    countries_with_leakages = 0

    for slug in slugs_to_check:
        findings = check_config(slug)
        leakages = [f for f in findings if f["status"] == "LEAKAGE"]
        missing = [f for f in findings if f["status"] == "MISSING"]
        invalid = [f for f in findings if f["status"] == "INVALID"]

        if leakages or invalid:
            countries_with_leakages += 1
            print(f"  FAIL {slug}: {len(leakages)} € leakages")
            for f in leakages:
                print(f"    LEAKAGE: {f['field']}: {f['msg']}")
            for f in invalid:
                print(f"    INVALID: {f['msg']}")
            total_leakages += len(leakages)
        elif missing:
            print(f"  SKIP {slug}: {missing[0]['msg']}")
        else:
            print(f"  PASS {slug}")

    print()
    print(f"Summary: {len(slugs_to_check)} non-eurozone configs checked, "
          f"{countries_with_leakages} with leakages, {total_leakages} total findings")

    if total_leakages and strict:
        print("\nSTRICT MODE: exit 1 (deploy would be blocked)")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
