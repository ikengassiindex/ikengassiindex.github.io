#!/usr/bin/env python3
"""
Remove the 251 negative-zero tokens from the published records, and change
nothing else.

    python3 scripts/normalise_published_negative_zero.py            # dry run
    python3 scripts/normalise_published_negative_zero.py --apply

WHY A TEXT SUBSTITUTION AND NOT PARSE-AND-REWRITE

    The obvious implementation is json.load, walk, json.dump. It is the wrong
    one. Re-serialising rewrites the ENTIRE file: separators, float repr, key
    order, ensure_ascii. Every byte becomes suspect, the diff is 73 files
    changed beyond recognition, and no reviewer can confirm that only the
    defect moved.

    A text substitution of the exact token changes those bytes and no others.
    The diff is then literally readable: 251 characters removed across 30
    countries. That is the difference between a change that can be reviewed
    and one that must be trusted.

    The pattern is the one validated in audit_published_json.py:
    -0.0, -0.00, -0.000... and nothing else. Its first version, (?![1-9]),
    also matched -0.00123 by backtracking to -0.0 and finding a 0 next; it
    reported 85,192 against the structured walk's 251, and the reconciliation
    between the two passes is what exposed it.

WHAT IS VERIFIED BEFORE ANYTHING IS WRITTEN

    For every file, both texts are parsed and compared STRUCTURALLY, key by
    key, and every difference must be a -0.0 becoming 0.0. This is what
    catches the one thing a text substitution can get wrong that a parse
    cannot: a "-0.0" occurring inside a STRING value would be silently
    rewritten, and the structural walk would name it immediately.

    A file that fails is not written and is named. Nothing is written at all
    unless every file passes.

ORDERING

    This must run AFTER the engine fix (5bcaf8e8), not before. Cleaning the
    data while the producer still emits -0.0 would last until the first
    Thursday, when pipeline-enrichment re-scores and puts them back.

    After this lands, audit_published_json.py --gate can go into validate.yml.

SAFETY

    Every file it touches is tracked and committed, so git is the backup. It
    writes in place and prints a per-country count so the diff can be checked
    against it.
"""
from __future__ import annotations
import argparse, json, math, pathlib, re, sys, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
NEGZERO = re.compile(r'(?<![\w.])-0\.0+(?![0-9])')


def slugs():
    d = json.loads((ROOT / "intelligence" / "countries.json").read_text())
    return [c["slug"] for c in (d["countries"] if isinstance(d, dict) else d)]


def is_negzero(v):
    return isinstance(v, float) and v == 0.0 and math.copysign(1.0, v) < 0


def structural_diff(b, a, path, out):
    if isinstance(b, dict) and isinstance(a, dict):
        for k in set(b) | set(a):
            if k not in b or k not in a:
                out.append((f"{path}.{k}", "key present in one only", ""))
            else:
                structural_diff(b[k], a[k], f"{path}.{k}", out)
    elif isinstance(b, list) and isinstance(a, list):
        if len(b) != len(a):
            out.append((path, f"length {len(b)}", f"length {len(a)}"))
        else:
            for i, (x, y) in enumerate(zip(b, a)):
                structural_diff(x, y, f"{path}[{i}]", out)
    elif is_negzero(b) and a == 0.0 and not is_negzero(a):
        out.append((path, "-0.0", "0.0"))
    elif repr(b) != repr(a):
        out.append((path, repr(b), repr(a)))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="write the files. Without it, nothing is touched.")
    a = ap.parse_args()

    files = []
    for slug in slugs():
        man_p = ROOT / slug / "ssi-data.json"
        if not man_p.exists():
            continue
        files.append((slug, man_p))
        for e in (json.loads(man_p.read_text()).get("substations_shards") or []):
            files.append((slug, ROOT / slug / pathlib.Path(e["path"]).name))

    planned, by_country, failures = [], collections.Counter(), []
    for slug, p in files:
        text = p.read_text()
        n = len(NEGZERO.findall(text))
        if not n:
            continue
        new = NEGZERO.sub("0.0", text)
        try:
            before, after = json.loads(text), json.loads(new)
        except Exception as ex:
            failures.append((p, f"result does not parse: {type(ex).__name__}: {ex}"))
            continue
        d = []
        structural_diff(before, after, "", d)
        other = [x for x in d if not (x[1] == "-0.0" and x[2] == "0.0")]
        if other:
            failures.append((p, f"{len(other)} change(s) beyond -0.0, first: {other[0]}"))
            continue
        if len(d) != n:
            failures.append((p, f"text found {n} tokens, structure found {len(d)}"))
            continue
        planned.append((p, new, n))
        by_country[slug] += n

    total = sum(n for _, _, n in planned)
    print(f"\n  {len(files)} published files · {len(planned)} need changing · "
          f"{total} token(s)\n")
    for s in sorted(by_country):
        print(f"    {s:<16}{by_country[s]:>6}")

    if failures:
        print(f"\n  REFUSING — {len(failures)} file(s) failed verification. "
              f"Nothing written.")
        for p, why in failures[:10]:
            print(f"    {p.relative_to(ROOT)}  {why}")
        return 1

    if not a.apply:
        print(f"\n  Dry run. Every file verified structurally: each difference "
              f"is a -0.0\n  becoming 0.0 and there are no others. "
              f"Re-run with --apply to write.")
        return 0

    for p, new, n in planned:
        p.write_text(new)
    print(f"\n  written — {len(planned)} file(s), {total} token(s) removed")
    print(f"  Now: python3 scripts/audit_published_json.py --gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
