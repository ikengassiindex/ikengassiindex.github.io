#!/usr/bin/env python3
"""check_pin14_field_first.py — Pin 14, asked the right way round.

FINDING_pin14_sweep_complete.md enumerated ONE generator's writes and tested
them. That was necessary and not sufficient: a second generator
(refresh_v42_modifiers_re_composite.py::_det_var) was found later, and the
enumeration itself was then truncated, so 8 of 22 writes were tested. Twice the
same mistake — starting from the generator.

This starts from the FIELD. It scans EVERY python file in the repository by AST
for any assignment whose value expression reaches a randomness-from-identity
call — vary, _det_var, det_var, stable_hash, or hashlib.md5 — and reports the
target field, so the question becomes "what writes this field?" rather than
"what does this generator write?".

Discovery only. It does not test reproduction; it tells you what to test.
Read-only.
"""
from __future__ import annotations
import ast, os, sys
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HASHY = {"vary", "_det_var", "det_var", "stable_hash", "md5", "_hash_unit",
         "_stable_hash", "deterministic_jitter"}
SKIP_DIRS = {"__pycache__", "_audit-snapshot", "archive", ".git", "node_modules"}

def calls_hash(node):
    """Does this expression SYNTACTICALLY reach a randomness call?"""
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            f = n.func
            nm = (f.id if isinstance(f, ast.Name)
                  else f.attr if isinstance(f, ast.Attribute) else None)
            if nm in HASHY:
                return nm
    return None


def names_in(node):
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def tainted_locals(fn):
    """Local names carrying a hash-derived value, to a fixed point.

    Needed because the second generator found in this estate does NOT call the
    hash in the field assignment:

        value = _det_var(seed, center, pct)      # hash here
        value = max(r_min, min(r_max, value))
        modifiers[mod_name] = round(value, 6)    # field written here

    A syntactic check on the assignment expression sees `round(value, 6)` and
    reports nothing. That is how the first version of this scan missed
    refresh_v42_modifiers_re_composite.py entirely — the third time in this
    estate that a check looked thorough and was not.
    """
    tainted, origin = set(), {}
    for _ in range(12):                      # fixed point; depth is small
        grew = False
        for node in ast.walk(fn):
            if not isinstance(node, (ast.Assign, ast.AugAssign)): continue
            g = calls_hash(node.value)
            via = g or next((origin.get(n) for n in names_in(node.value)
                             if n in tainted), None)
            if not via: continue
            tgts = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in tgts:
                if isinstance(t, ast.Name) and t.id not in tainted:
                    tainted.add(t.id); origin[t.id] = via; grew = True
        if not grew: break
    return tainted, origin


def target_path(t):
    """Render an assignment target as a dotted field path where possible."""
    parts = []
    cur = t
    while isinstance(cur, ast.Subscript):
        k = cur.slice
        if isinstance(k, ast.Constant): parts.append(str(k.value))
        else: parts.append("<expr>")
        cur = cur.value
    if isinstance(cur, ast.Name): parts.append(cur.id)
    elif isinstance(cur, ast.Attribute): parts.append(cur.attr)
    return ".".join(reversed(parts))

def main():
    found = defaultdict(list)
    files = 0
    unparsed = []
    for root, dirs, names in os.walk(os.path.join(REPO, "scripts")):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for n in names:
            if not n.endswith(".py"): continue
            p = os.path.join(root, n)
            files += 1
            try:
                tree = ast.parse(open(p, encoding="utf-8", errors="replace").read())
            except SyntaxError as e:
                unparsed.append((os.path.relpath(p, REPO), str(e))); continue
            scopes = [n for n in ast.walk(tree)
                      if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))] + [tree]
            for fn in scopes:
                tainted, origin = tainted_locals(fn)
                for node in ast.walk(fn):
                    if not isinstance(node, (ast.Assign, ast.AugAssign)): continue
                    gen = calls_hash(node.value)
                    if not gen:
                        gen = next((origin[n] for n in names_in(node.value)
                                    if n in tainted), None)
                        if gen: gen += " (via local)"
                    if not gen: continue
                    tgts = node.targets if isinstance(node, ast.Assign) else [node.target]
                    for t in tgts:
                        if isinstance(t, (ast.Subscript, ast.Attribute)):
                            found[target_path(t)].append(
                                (os.path.relpath(p, REPO), node.lineno, gen))

    # A hash used to DETECT fabrication is the opposite of one used to CREATE
    # it, and the first version of this scan reported both in one list — which
    # is how ssi_derive_component_T.py, a guard, appeared among the fabricators.
    DETECTORS = {"scripts/ssi_derive_component_T.py", "scripts/ssi_provenance_sweep.py"}
    fab = {f: [] for f in sorted({x[0] for v in found.values() for x in v}) if f not in DETECTORS}
    det = {f: [] for f in sorted({x[0] for v in found.values() for x in v}) if f in DETECTORS}
    for fld, v in found.items():
        for f, ln, gen in v:
            (det if f in DETECTORS else fab)[f].append((fld, ln, gen))

    print("FIELD-FIRST PIN 14 SCAN — %d python files under scripts/" % files)
    print("randomness-from-identity calls searched: %s\n" % ", ".join(sorted(HASHY)))
    print("%-38s %-52s %s" % ("field written", "writer", "via"))
    print("-" * 104)
    for fld in sorted(found):
        for f, ln, gen in sorted(set(found[fld])):
            print("%-38s %-52s %s" % (fld, "%s:%d" % (f, ln), gen))
    print("\n" + "=" * 104)
    print("FABRICATORS — a hash BECOMES a published value (%d files)" % len(fab))
    for f in sorted(fab):
        flds = sorted({x[0] for x in fab[f]})
        print("   %-52s %d fields: %s" % (f, len(flds), ", ".join(flds)[:60]))
    print("\nDETECTORS — a hash is used to CATCH fabrication (%d files)" % len(det))
    for f in sorted(det):
        print("   %-52s (guard, not a writer)" % f)
    print("\nThe distinction is not cosmetic. ssi_derive_component_T.py correlates")
    print("stable_hash(name) against its inputs and REFUSES the country above")
    print("HASH_R=0.99. It is the model the other derivations should follow.")
    print("\ndistinct field targets reached by a hash: %d" % len(found))
    gens = sorted({g for v in found.values() for _, _, g in v})
    files_ = sorted({f for v in found.values() for f, _, _ in v})
    print("generators in use: %s" % ", ".join(gens))
    print("files that write a field from a hash: %d" % len(files_))
    for f in files_: print("   %s" % f)
    if unparsed:
        print("\nUNPARSED (reported, not swallowed): %d" % len(unparsed))
        for f, e in unparsed[:10]: print("   %s — %s" % (f, e[:70]))
    return 0

if __name__ == "__main__":
    sys.exit(main())
