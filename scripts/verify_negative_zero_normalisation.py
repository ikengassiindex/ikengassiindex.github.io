#!/usr/bin/env python3
"""
Verify the working tree against HEAD: every change must be -0.0 becoming 0.0.

    python3 scripts/verify_negative_zero_normalisation.py

WHY THIS IS SEPARATE FROM THE SCRIPT THAT MADE THE CHANGE

    normalise_published_negative_zero.py verifies each file structurally
    before writing it. That is the right guard, and it is not independent
    evidence: the same process decided what to write and then confirmed its
    own output. If its pattern were wrong in a way its own check shared, both
    would agree.

    This reads the committed version out of git and compares it to what is on
    disk now. Different source, different code path, same question.

    It shells out to `git show`, which is why it exists as a script the
    OPERATOR runs rather than something done from the assistant's side.

WHAT MUST HOLD

    - every file that differs from HEAD differs ONLY by -0.0 -> 0.0
    - the total number of such differences is exactly the number reported by
      the normalisation run
    - no file gained or lost a key, changed a type, or moved a value
    - every file still parses

    Any other difference names its JSON path and fails.
"""
from __future__ import annotations
import json, math, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXPECTED = 251


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


def changed_files():
    out = subprocess.run(["git", "diff", "--name-only", "HEAD", "--", "*.json"],
                         cwd=ROOT, capture_output=True, text=True, check=True)
    return [ln for ln in out.stdout.splitlines() if ln.strip()]


def main() -> int:
    files = changed_files()
    print(f"\n  {len(files)} JSON file(s) differ from HEAD\n")
    fixed, bad, unparsed = 0, [], []
    for rel in files:
        head = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT,
                              capture_output=True, text=True)
        if head.returncode != 0:
            print(f"    {rel}  NEW FILE (not in HEAD) — not part of this change")
            bad.append((rel, "", "new file", ""))
            continue
        try:
            before = json.loads(head.stdout)
            after = json.loads((ROOT / rel).read_text())
        except Exception as ex:
            unparsed.append((rel, f"{type(ex).__name__}: {ex}"))
            continue
        d = []
        structural_diff(before, after, "", d)
        for path, was, now in d:
            if was == "-0.0" and now == "0.0":
                fixed += 1
            else:
                bad.append((rel, path, was, now))

    print(f"  -0.0 -> 0.0 differences      {fixed}")
    print(f"  expected                     {EXPECTED}")
    print(f"  differences of any other kind {len(bad)}")
    print(f"  files that failed to parse    {len(unparsed)}")

    ok = True
    if unparsed:
        ok = False
        for rel, why in unparsed[:10]:
            print(f"    UNPARSED {rel}  {why}")
    if bad:
        ok = False
        print(f"\n  FAIL — differences that are not the intended one:")
        for rel, path, was, now in bad[:10]:
            print(f"    {rel}{path}\n       HEAD {was}\n       now  {now}")
    if fixed != EXPECTED:
        ok = False
        print(f"\n  FAIL — expected {EXPECTED} normalisations, found {fixed}. "
              f"A count that does not match is not a rounding difference; "
              f"something else changed or something was missed.")
    print()
    if not ok:
        print(f"  DO NOT COMMIT.")
        return 1
    print(f"  PASS — the working tree differs from HEAD by exactly {fixed} "
          f"negative zeros\n  becoming positive zeros, and by nothing else.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
