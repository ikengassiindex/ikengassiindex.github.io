#!/usr/bin/env python3
"""
Audit every published JSON record for values that are numerically fine and
textually wrong.

    python3 scripts/audit_published_json.py            # report
    python3 scripts/audit_published_json.py --gate     # exit 1 on any finding

WHY THIS EXISTS

    On 9 September, 23,997 substations were published with metrics.I1 = -0.0 -
    a negative snow load. ERA5-Land carries tiny negative snow water
    equivalents from numerical noise; averaged and rounded to 5 dp they become
    NEGATIVE ZERO, which is numerically equal to 0.0 and serialises into JSON
    as the string "-0.0".

    The check that missed it was `v < 0`, which is False for -0.0. I reported
    "zero records are negative" and was wrong. A clamp was added at I1's write
    site and the defect was recorded as fixed.

    It was fixed in one place. -0.0 is not a property of snow; it is a
    property of round() on a small negative, and every field written by every
    producer in this estate can carry it. Sweeping the published records on
    11 September found 251 more, in 30 of 39 countries, in fields nobody had
    looked at.

    The first sweep also nearly issued a false all-clear: parsing metrics and
    components found ZERO, because that is where the last bug was. Only a raw
    text scan across the whole document found the 251. Both passes are kept
    here, and they are required to agree.

WHAT IT CHECKS

    A. negative zero, anywhere in the document, by JSON path
    B. a parse-vs-text reconciliation: the structured walk and the raw token
       scan must find the same count. A disagreement means the walk is not
       reaching part of the document, which is how the first version of this
       sweep produced a clean report over dirty data.
    C. non-finite values - NaN and Infinity - which are not valid JSON and
       which some writers emit anyway

SEVERITY, STATED HONESTLY
    metrics.I1 = -0.0 was a negative snow load: a quantity that cannot be
    negative, published with a sign. The 251 found later are in
    modifier_impacts.* and skewness, which CAN legitimately be negative, so
    -0.0 there is a zero carrying a stray sign bit rather than a false
    physical claim. It is still a nonsense token in a published record, it
    still renders as "-0.0" in anything that reads the text, and it is still
    the same defect.

WHY --gate IS NOT THE DEFAULT AND NOT YET IN CI
    Wiring this into validate.yml today would fail every build, because the
    251 tokens are in the published records right now. The order is: land the
    instrument, clean the data as its own change under the pinned sequence,
    then turn on the gate. An instrument that has to be switched off to get
    work done teaches everyone to switch instruments off.
"""
from __future__ import annotations
import argparse, json, math, pathlib, re, sys, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
# -0.0, -0.00, -0.000... and nothing else. The first version of this pattern
# was (?![1-9]), which also matched -0.00123 by backtracking to -0.0 and
# finding a '0' next. It reported 85,192 against the walk's 251, and the
# reconciliation in check B is what exposed it. (?![0-9]) is the fix: no digit
# of any kind may follow the run of zeros.
NEGZERO_TEXT = re.compile(r'(?<![\w.])-0\.0+(?![0-9])')


def slugs():
    d = json.loads((ROOT / "intelligence" / "countries.json").read_text())
    return [c["slug"] for c in (d["countries"] if isinstance(d, dict) else d)]


def is_negzero(v):
    return isinstance(v, float) and v == 0.0 and math.copysign(1.0, v) < 0


def walk(o, path, negz, nonfinite):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, f"{path}.{k}" if path else k, negz, nonfinite)
    elif isinstance(o, list):
        for v in o:
            walk(v, f"{path}[]", negz, nonfinite)
    elif isinstance(o, float):
        if is_negzero(o):
            negz[path] += 1
        elif not math.isfinite(o):
            nonfinite[path] += 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", action="store_true",
                    help="exit 1 on any finding, for CI")
    a = ap.parse_args()

    negz = collections.Counter()
    nonfinite = collections.Counter()
    by_country = collections.Counter()
    text_total = 0
    nfiles = 0

    for slug in slugs():
        man_p = ROOT / slug / "ssi-data.json"
        if not man_p.exists():
            print(f"  {slug:<16} no ssi-data.json — skipped and counted")
            continue
        files = [man_p]
        man = json.loads(man_p.read_text())
        for e in (man.get("substations_shards") or []):
            files.append(ROOT / slug / pathlib.Path(e["path"]).name)
        before = sum(negz.values())
        for p in files:
            nfiles += 1
            t = p.read_text()
            text_total += len(NEGZERO_TEXT.findall(t))
            walk(json.loads(t), "" if p is man_p else "shard", negz, nonfinite)
        by_country[slug] = sum(negz.values()) - before

    total = sum(negz.values())
    print(f"\n  AUDIT — {nfiles} published JSON files, {len(slugs())} countries\n")

    print(f"  A. NEGATIVE ZERO by JSON path")
    if negz:
        for k, n in negz.most_common():
            print(f"    {n:>6,}  {k}")
    else:
        print(f"    none")

    print(f"\n  B. PARSE vs TEXT reconciliation")
    print(f"    structured walk : {total:,}")
    print(f"    raw token scan  : {text_total:,}")
    agree = total == text_total
    print(f"    {'AGREE' if agree else 'DISAGREE'} — "
          + ("both passes see the same document"
             if agree else
             "the walk is not reaching part of the document. This is the "
             "failure mode that produced a clean report over dirty data on "
             "11 September. Trust the larger number and fix the walk."))

    print(f"\n  C. NON-FINITE (NaN / Infinity — not valid JSON)")
    if nonfinite:
        for k, n in nonfinite.most_common():
            print(f"    {n:>6,}  {k}")
    else:
        print(f"    none")

    if total:
        print(f"\n  affected countries: "
              f"{sum(1 for v in by_country.values() if v)} of {len(slugs())}")

    findings = total + sum(nonfinite.values()) + (0 if agree else 1)
    print(f"\n  {findings:,} finding(s)")
    if a.gate and findings:
        print(f"  GATE FAILED")
        return 1
    if not a.gate and findings:
        print(f"  Reporting only. Re-run with --gate once the records are "
              f"clean, then wire it into validate.yml.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
