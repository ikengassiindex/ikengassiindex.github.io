#!/usr/bin/env python3
"""
voltage_kv and grid-geo kv are in VOLTS on some records. Divide by 1000.

    python3 scripts/repair_voltage_units.py --all --dry-run
    python3 scripts/repair_voltage_units.py turkey

THE DEFECT
----------
A voltage above 1000 is never kilovolts on a power line. Turkey carries 1,116
substations (27.7%) and 2,204 line records (27.3%) at 154000, 380000, 34500,
31500 — raw OSM volt strings that never went through the `// 1000` in
score-country.py:104. Nine other countries carry between 1 and 24 such records
each; those are isolated bad tags, not a systematic failure.

This is the same unit-confusion class as the Italy `voltage=15000;400` case.

WHAT IT COSTS TODAY
-------------------
refresh_country_counts.py buckets substations as EHV >= 220 kV and
HV 110-220 kV. With turkey's 154000 reading as ">= 220", the published turkey
figures are:

    published        1,120 at >= 220 kV       1 at 110-220 kV
    correct            130 at >= 220 kV     790 at 110-220 kV

An 8.6x overstatement of turkey's EHV fleet, live on the site.

WHAT THIS DOES NOT TOUCH
------------------------
The 2,880 turkey substations (71.4%) whose voltage_kv is exactly 66 — the
hardcoded fallback at score-country.py:104 and :106, reached both when the OSM
voltage tag is empty and when parsing it raises. They are not a unit error and
dividing them by anything makes them no truer. They are held for a separate
decision; see FINDING_turkey_voltage_units.md.

That 66 is a default and not a measurement is established by absence of a
ladder: a country with a real 66 kV population shows its neighbouring levels on
the same scale. Japan does (6.6, 66, 154, 77, 275, 500) and australia does
(33, 66, 132, 110, 220) — both are genuine and are NOT touched by this script.
Turkey shows 66 alone, with every real Turkish level (154, 380, 34.5, 31.5)
sitting in the volts bucket instead.

SAFETY
------
Every converted value must land on a plausible transmission or distribution
level, or the record is refused and the country aborts. Convention #56: a
record that cannot be repaired confidently is left alone and counted out loud,
never quietly coerced.
"""
from __future__ import annotations
import argparse, json, pathlib, sys, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
VOLT_FLOOR = 1000.0            # above this, the value is volts
# Levels a converted value may legitimately land on (kV), IEC/ANSI plus the
# national levels present in this cohort. A conversion landing elsewhere is a
# refusal, not a rounding opportunity.
PLAUSIBLE = {0.4, 1, 1.5, 3, 3.3, 6, 6.6, 10, 11, 12, 15, 16, 20, 22, 24, 25,
             30, 31.5, 33, 34.5, 35, 38, 45, 50, 55, 60, 63, 66, 70, 72.5, 77,
             90, 100, 110, 115, 120, 130, 132, 138, 145, 150, 154, 161, 170,
             220, 225, 230, 236, 245, 275, 285, 300, 330, 345, 380, 400, 412,
             420, 450, 500, 525, 550, 735, 750, 765}
TOL = 0.001


def snap(v):
    """The ladder level this quotient matches, or None. Returns the LEVEL, not
    the quotient: 20000.75 V / 1000 = 20.00075, which is 20 kV with float noise
    on the source tag, not a 20.001 kV line. Storing the quotient would invent
    a precision the source never had."""
    for p in PLAUSIBLE:
        if abs(v - p) <= TOL:
            return float(p)
    return None


def load_slugs():
    d = json.loads((ROOT / "intelligence" / "countries.json").read_text())
    return [c["slug"] for c in (d["countries"] if isinstance(d, dict) else d)]


def repair_value(v, refused):
    """Return (new_value, changed). Refuses rather than guesses."""
    if not isinstance(v, (int, float)) or isinstance(v, bool) or v <= VOLT_FLOOR:
        return v, False
    q = v / 1000.0
    level = snap(q)
    if level is None:
        refused.append((v, q))
        return v, False
    return level, True


def do_country(slug, apply):
    report = {"slug": slug, "subs_fixed": 0, "lines_fixed": 0,
              "subs_refused": [], "lines_refused": [], "changes": collections.Counter()}

    # ── substations (manifest or shards) ────────────────────────────────────
    manp = ROOT / slug / "ssi-data.json"
    man = json.loads(manp.read_text())
    shards = man.get("substations_shards")
    blocks = []                     # (path, records, was_list) ; path None = inline
    if shards:
        for e in shards:
            p = ROOT / slug / pathlib.Path(e["path"]).name
            raw = json.loads(p.read_text())
            blocks.append((p, raw if isinstance(raw, list) else raw.get("substations", []),
                           isinstance(raw, list)))
    else:
        blocks.append((None, man.get("substations") or [], False))

    refused = []
    for _p, recs, _l in blocks:
        for r in recs:
            nv, ch = repair_value(r.get("voltage_kv"), refused)
            if ch:
                report["changes"][f"{r['voltage_kv']} -> {nv}"] += 1
                r["voltage_kv"] = nv
                report["subs_fixed"] += 1
    report["subs_refused"] = refused

    # ── grid-geo lines ──────────────────────────────────────────────────────
    gp = ROOT / slug / "grid-geo.json"
    g = json.loads(gp.read_text()) if gp.exists() else None
    lrefused = []
    lblocks = []
    if g is not None:
        lblocks.append((None, g.get("l") or []))
        for sh in (g.get("l_shards") or []):
            p = ROOT / slug / pathlib.Path(sh["path"] if isinstance(sh, dict) else sh).name
            if p.exists():
                raw = json.loads(p.read_text())
                lblocks.append((p, raw if isinstance(raw, list) else (raw.get("l") or [])))
        for _p, lines in lblocks:
            for ln in lines:
                nv, ch = repair_value(ln.get("kv"), lrefused)
                if ch:
                    ln["kv"] = nv
                    report["lines_fixed"] += 1
    report["lines_refused"] = lrefused

    # Convention #56: a refused record is left EXACTLY as it was and reported.
    # It does not block the records that can be converted confidently, and it
    # does not get quietly rounded to the nearest level that happens to be in
    # the table. The run exits non-zero so refusals cannot pass unnoticed.

    if apply and (report["subs_fixed"] or report["lines_fixed"]):
        for p, recs, was_list in blocks:
            if p is None:
                man["substations"] = recs
            else:
                p.write_text(json.dumps(recs if was_list else {"substations": recs}))
        manp.write_text(json.dumps(man))
        if g is not None and report["lines_fixed"]:
            for p, lines in lblocks:
                if p is None:
                    g["l"] = lines
                else:
                    p.write_text(json.dumps(lines))
            gp.write_text(json.dumps(g))
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    slugs = load_slugs() if a.all else a.slugs
    if not slugs:
        sys.exit("give country slugs or --all")

    tot_s = tot_l = 0
    refusals = []
    print(f"\n  voltage unit repair{' (DRY RUN)' if a.dry_run else ''}\n")
    for slug in sorted(slugs):
        try:
            r = do_country(slug, apply=not a.dry_run)
        except FileNotFoundError:
            continue
        if r["subs_fixed"] or r["lines_fixed"]:
            tot_s += r["subs_fixed"]; tot_l += r["lines_fixed"]
            print(f"    {slug:14} {r['subs_fixed']:>6,} substations  "
                  f"{r['lines_fixed']:>6,} lines")
            for k, n in r["changes"].most_common(6):
                print(f"        {k}  x{n:,}")
        for v, q in r["subs_refused"]:
            refusals.append((slug, "substation", v, q))
        for v, q in r["lines_refused"]:
            refusals.append((slug, "line", v, q))
    print(f"\n    total {tot_s:,} substations, {tot_l:,} line records")
    if refusals:
        print(f"\n    REFUSED — left untouched, {len(refusals)} record(s) whose "
              f"value / 1000 is not a real voltage level:")
        for slug, kind, v, q in refusals:
            print(f"        {slug:14} {kind:11} {v:>12,.0f} V -> {q:,.3f} kV")
        print("\n    These need a source decision, not a unit conversion.\n")
        return 1
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
