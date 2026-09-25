#!/usr/bin/env python3
"""Repair the dangling I4 provenance citation on the published records.

    python3 scripts/repair_i4_citation.py            # dry run
    python3 scripts/repair_i4_citation.py --apply

WHAT AND WHY
------------
`_metrics_source` on 37 countries' records names

    AMENDMENT_DRAFT_I4_definition.md

which exists in no directory of this repository. The document actually consulted
is AMENDMENT_DRAFT_I4_I6_definition.md, and the manifest's metric_derivations
already cites it correctly — the manifest was repaired and the records were not.

This changes NO VALUE and pins NOTHING. It corrects a filename to one that
exists. The records then cite an unsigned draft, which is what they were in fact
derived under, and which the conformance register reports in its own row.

DISCIPLINE, ALL OF IT LEARNED THE HARD WAY TODAY
------------------------------------------------
* TEXT SUBSTITUTION, not parse-and-rewrite. Re-serialising 620,696 records to
  change one string would rewrite every float in the estate and bury the change
  in noise.
* The replacement is checked to be SAFE FIRST: the correct name must not contain
  the dangling name as a substring, or a second pass would corrupt it.
* Every file is PARSED BEFORE AND AFTER and compared structurally, so the only
  thing that may differ is the intended string. A file that fails is not written.
* BOTH SURFACES: manifests and shards, sharded countries and unsharded. Reading
  `substations_shards` alone missed 33 of 39 countries earlier today.
"""
from __future__ import annotations
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BAD = "AMENDMENT_DRAFT_I4_definition.md"
GOOD = "AMENDMENT_DRAFT_I4_I6_definition.md"

# If the replacement contained the target, applying it twice would corrupt the
# name. Asserted rather than assumed: this is cheap and the failure is silent.
assert BAD not in GOOD, "replacement contains the target — substitution is unsafe"


def walk(a, b, path="$"):
    """Yield every leaf position where two parsed structures differ."""
    if type(a) is not type(b):
        yield path, a, b
        return
    if isinstance(a, dict):
        if a.keys() != b.keys():
            yield path + " {keys}", sorted(a), sorted(b)
            return
        for k in a:
            yield from walk(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, list):
        if len(a) != len(b):
            yield path + " {len}", len(a), len(b)
            return
        for i, (x, y) in enumerate(zip(a, b)):
            yield from walk(x, y, f"{path}[{i}]")
    elif a != b:
        yield path, a, b


def main():
    apply = "--apply" in sys.argv
    targets = sorted(ROOT.glob("*/ssi-data.json")) + \
        sorted(ROOT.glob("*/ssi-data-substations-*.json"))
    files = hits = 0
    bad_files = []
    for p in targets:
        text = p.read_text(encoding="utf-8")
        n = text.count(BAD)
        if not n:
            continue
        files += 1
        hits += n
        new_text = text.replace(BAD, GOOD)
        # Structural check: parse both, and accept only differences that are
        # exactly this substitution on a string leaf.
        before, after = json.loads(text), json.loads(new_text)
        bad = [(path, x, y) for path, x, y in walk(before, after)
               if not (isinstance(x, str) and isinstance(y, str)
                       and x.replace(BAD, GOOD) == y)]
        if bad:
            bad_files.append((p, bad[:3]))
            print(f"  REFUSED {p.relative_to(ROOT)} — {len(bad)} unexpected diff(s)")
            continue
        if new_text.count(BAD):
            bad_files.append((p, [("residual", new_text.count(BAD), 0)]))
            print(f"  REFUSED {p.relative_to(ROOT)} — {new_text.count(BAD)} residual")
            continue
        print(f"  {'wrote  ' if apply else 'would  '} {p.relative_to(ROOT)}  "
              f"{n:,} occurrence(s)")
        if apply:
            p.write_text(new_text, encoding="utf-8")
    print(f"\n  {files} file(s), {hits:,} occurrence(s)")
    print(f"  {'APPLIED' if apply else 'DRY RUN — nothing written'}")
    if bad_files:
        print(f"  {len(bad_files)} FILE(S) REFUSED — nothing written for those")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
