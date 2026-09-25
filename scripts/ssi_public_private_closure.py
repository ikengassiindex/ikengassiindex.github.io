#!/usr/bin/env python3
"""Compute the public/private boundary as a CLOSURE, and verify a tree against it.

    python3 scripts/ssi_public_private_closure.py                 # report
    python3 scripts/ssi_public_private_closure.py --verify <dir>  # gate a tree
    python3 scripts/ssi_public_private_closure.py --list-private

WHY THIS EXISTS
---------------
`DESIGN_the_public_private_boundary.md` names fourteen files that stay public.
A file list rots -- the design says so itself -- and this one rotted inside a
day: DW added five scripts and the count moved 331 -> 344 before anyone
executed anything.

Worse, a boundary stated as a list of directories is wrong by construction.
Defining private as `pipeline/{ingestion,enrichment,scoring}` plus the
deprecated files leaves 33 public files importing private modules. The private
set is the TRANSITIVE CLOSURE of the seed under "is imported by", and it has to
be recomputed whenever an import changes.

WHY AST AND NOT GREP
--------------------
Three separate greps lied during this work, all on 25 September 2026:

  * `grep -r` does not follow symlinks, so a check over a symlinked candidate
    tree reported ZERO files importing the private tranche when the answer was
    33. Green by not reading the files -- the mechanism of
    FINDING_the_gate_that_passed_by_not_running.md.
  * an unanchored pattern matched a COMMENT in tests/conftest.py and reported
    it as an importer of the engine. It imports pathlib, pytest and sys.
  * `from scripts.pipeline` missed the `from pipeline.x` spelling, undercounting
    tests that import the engine 26 -> 21.

`ast.parse` reads the imports the interpreter would. It cannot match a comment,
a docstring or a string literal, and it does not care about symlinks.

Read-only. Writes nothing. Exit 0 when the tree is clean, 1 when it is not.
"""
from __future__ import annotations

import argparse
import ast
import os
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent

SEED_DIRS = ("scripts/pipeline/ingestion",
             "scripts/pipeline/enrichment",
             "scripts/pipeline/scoring")
SEED_SUFFIX = ".deprecated_by_session_j_task_1140"

# Spellings the seed packages are imported by, in either layout.
SEED_MODULES = {
    "scripts.pipeline.scoring", "scripts.pipeline.enrichment", "scripts.pipeline.ingestion",
    "pipeline.scoring", "pipeline.enrichment", "pipeline.ingestion",
}


def tracked():
    out = subprocess.run(["git", "ls-files"], cwd=REPO,
                         capture_output=True, text=True).stdout.split()
    return [f for f in out if f]


def imports_of(path):
    try:
        tree = ast.parse((REPO / path).read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return set()
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                out.add(a.name)
        elif isinstance(n, ast.ImportFrom) and n.module:
            out.add(n.module)
    return out


def module_spellings(paths):
    """Every dotted name a file could plausibly be imported by."""
    out = set(SEED_MODULES)
    for p in paths:
        if not p.endswith(".py"):
            continue
        m = p[:-3].replace("/", ".")
        parts = m.split(".")
        for i in range(len(parts)):
            out.add(".".join(parts[i:]))
    return out


def hits(mods, names):
    return any(m in names or any(m.startswith(x + ".") for x in names) for m in mods)


def closure(files=None, verbose=False):
    files = files or tracked()
    py = [f for f in files if f.endswith(".py")]
    imp = {f: imports_of(f) for f in py}

    private = {f for f in files
               if f.startswith(SEED_DIRS) or f.endswith(SEED_SUFFIX)}
    for i in range(1, 12):
        names = module_spellings(private)
        added = {f for f in py if f not in private and hits(imp[f], names)}
        if not added:
            break
        private |= added
        if verbose:
            print("  pass %d: +%-4d (total private %d)" % (i, len(added), len(private)))
    public = [f for f in files if f not in private]
    return private, public, imp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", metavar="DIR",
                    help="a candidate public tree; fails if any file in it imports the private set")
    ap.add_argument("--build", action="store_true",
                    help="build the candidate tree here, verify it, remove it. Works on any machine.")
    ap.add_argument("--list-private", action="store_true")
    a = ap.parse_args()

    private, public, imp = closure(verbose=not a.verify)
    names = module_spellings(private)

    if a.list_private:
        for f in sorted(private):
            print(f)
        return 0

    print("\n  seed      %s + *%s" % (", ".join(SEED_DIRS), SEED_SUFFIX))
    print("  CLOSURE   private %d   public %d   of %d tracked"
          % (len(private), len(public), len(private) + len(public)))

    leak = sorted(f for f in public if f.endswith(".py") and hits(imp.get(f, set()), names))
    print("  public files importing the private set: %d" % len(leak))
    for f in leak[:20]:
        print("     %s" % f)

    if a.build:
        # Build the tree rather than depend on one someone else made earlier.
        # The --verify path needed a tree at ~/cand, which existed on the
        # machine that built it and nowhere else, so the gate silently fell
        # back to the weaker check on every other machine. A check that is
        # strong in one environment and weak in another is two checks wearing
        # one name.
        import shutil, tempfile
        root = pathlib.Path(tempfile.mkdtemp(prefix="ssi_candidate_"))
        try:
            for f in public:
                d = root / os.path.dirname(f)
                d.mkdir(parents=True, exist_ok=True)
                try:
                    os.symlink(REPO / f, root / f)
                except FileExistsError:
                    pass
            a.verify = str(root)
            print("\n  built a candidate public tree at %s" % root)
            rc = _verify(root, public, private, imp, names)
        finally:
            shutil.rmtree(root, ignore_errors=True)
            print("  (tree removed)")
        return rc

    if a.verify:
        root = pathlib.Path(a.verify)
        if not root.is_dir():
            print("  ✗ %s is not a directory" % root)
            return 1
        present = sum(1 for f in public if (root / f).exists())
        offenders = [f for f in sorted(private) if (root / f).exists()]
        return _report(root, present, public, offenders, leak)

    return 0 if not leak else 1


def _verify(root, public, private, imp, names):
    present = sum(1 for f in public if (root / f).exists())
    offenders = [f for f in sorted(private) if (root / f).exists()]
    leak = sorted(f for f in public if f.endswith(".py") and hits(imp.get(f, set()), names))
    return _report(root, present, public, offenders, leak)


def _report(root, present, public, offenders, leak):
    print("\n  tree %s" % root)
    print("     public files present : %d of %d" % (present, len(public)))
    print("     PRIVATE files present: %d (must be 0)" % len(offenders))
    for f in offenders[:15]:
        print("        %s" % f)
    ok = (not leak) and (not offenders) and present == len(public)
    print("\n  %s" % ("✓ the tree matches the closure" if ok
                      else "✗ the tree does NOT match the closure"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
