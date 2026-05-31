#!/usr/bin/env python3
"""
check_edition_offset.py — Discipline #20 (BPG Part XXXIX § XXXIX.10, KB §72.10).

Prevents D#15-sub-pattern (country-config field-value-range gap) by validating
that every country-config's `edition_anchor_month_offset` is in range [1, 12].

ICELAND + KOREA INCIDENT (May 29, 2026): both country-configs had
`edition_anchor_month_offset: 0` while SI/SK/HU used 5/7. Result: intelligence.html
Section G "Looking Ahead" rendered "Edition 07" instead of cohort-consistent
"Edition 02" for July 2026 publication. The Math.max(2,…) clamp in the renderer
masked the bug for SK (raw 0 → 02) and HU (raw 0 → 02) — meaning the same
displayed "02" comes from offsets 5/6/7 by coincidence for July publication.

D#15 (country-config mandatory) only checks file existence + r3_buckets.
This gate (D#20) extends to field-value-range validation:
  edition_anchor_month_offset ∈ [1, 12]
  recommended 5 for cohort Edition-02 (July) synchronization

Usage:
  python3 scripts/check_edition_offset.py               # check all country-configs
  python3 scripts/check_edition_offset.py <slug>        # check one country
  python3 scripts/check_edition_offset.py --strict      # exit 1 on any out-of-range
  python3 scripts/check_edition_offset.py --recommend   # print recommended values
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = REPO_ROOT / "intelligence" / "country-configs"

VALID_RANGE = (1, 12)  # inclusive
RECOMMENDED = 5         # produces Edition 02 for July 2026 publication (cohort-aligned)


def load_slugs():
    """Discover slugs from country-configs/*.json files present."""
    if not CONFIG_DIR.exists():
        return []
    return sorted(p.stem for p in CONFIG_DIR.glob("*.json"))


def check_config(slug):
    """Returns (status, offset, message)."""
    path = CONFIG_DIR / f"{slug}.json"
    if not path.exists():
        return ("MISSING", None, f"country-config not found at {path}")
    try:
        with open(path) as f:
            cfg = json.load(f)
    except json.JSONDecodeError as e:
        return ("INVALID", None, f"JSON parse failed: {e}")

    offset = cfg.get("edition_anchor_month_offset")
    if offset is None:
        # Field absent — renderer defaults to 5 (per intelligence-sections.js line 1397)
        return ("DEFAULT", None, "edition_anchor_month_offset absent (renderer uses default=5)")

    if not isinstance(offset, (int, float)):
        return ("INVALID", offset, f"edition_anchor_month_offset must be int, got {type(offset).__name__}")

    if offset < VALID_RANGE[0] or offset > VALID_RANGE[1]:
        return ("OUT_OF_RANGE", offset,
                f"edition_anchor_month_offset={offset} outside valid range {VALID_RANGE} "
                f"(D#15 sub-pattern: field-value-range violation)")

    if offset != RECOMMENDED:
        # In range but non-standard — warn-level
        return ("NON_STANDARD", offset,
                f"edition_anchor_month_offset={offset} (recommended {RECOMMENDED} for cohort sync)")

    return ("PASS", offset, "")


def main():
    args = sys.argv[1:]
    strict = "--strict" in args
    args = [a for a in args if a != "--strict"]

    if args and args[0] == "--recommend":
        print(f"Discipline #20 — edition_anchor_month_offset validation")
        print(f"  Valid range: {VALID_RANGE[0]} to {VALID_RANGE[1]} inclusive")
        print(f"  Recommended: {RECOMMENDED} (produces Edition 02 for July 2026 publication)")
        print(f"  Renderer formula: nextEditionNum = (year-2026)*12 + (nextMonth+1) - offset")
        print(f"  Clamped via Math.max(2, …) so minimum displayed edition = 02")
        sys.exit(0)

    if args:
        slugs = [args[0]]
    else:
        slugs = load_slugs()

    print(f"check_edition_offset.py — Discipline #20 — checking {len(slugs)} country-configs")
    print()

    fails = 0
    warns = 0
    passes = 0
    defaults = 0
    for slug in slugs:
        status, offset, msg = check_config(slug)
        if status == "PASS":
            passes += 1
            # silent on pass to reduce noise
        elif status == "DEFAULT":
            defaults += 1
            print(f"  INFO {slug:18} offset=<default 5>  {msg}")
        elif status == "NON_STANDARD":
            warns += 1
            print(f"  WARN {slug:18} offset={offset}  {msg}")
        elif status == "OUT_OF_RANGE":
            fails += 1
            print(f"  FAIL {slug:18} offset={offset}  {msg}")
        elif status == "INVALID":
            fails += 1
            print(f"  FAIL {slug:18}  {msg}")
        elif status == "MISSING":
            print(f"  SKIP {slug:18}  {msg}")

    print()
    print(f"Summary: {passes} pass / {defaults} default / {warns} warn / {fails} fail")

    if fails and strict:
        print("\nSTRICT MODE: exit 1 (deploy would be blocked)")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
