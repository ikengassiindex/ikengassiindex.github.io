#!/usr/bin/env python3
"""
The six components must be measurements. For 456,200 they are a hash of the name.

    python3 scripts/check_components_are_measured.py --all
    python3 scripts/check_components_are_measured.py --all --strict
    python3 scripts/check_components_are_measured.py france --verbose
    python3 scripts/check_components_are_measured.py --all --update-baseline

WHAT THIS GATES
---------------
scripts/enrich_esg_gaps.py:317

    for key in ['C', 'V', 'I', 'E', 'S', 'T']:
        if not comp.get(key):
            comp[key] = round(vary(0.35, name + f'_{key}', 0.30), 4)

vary() is a deterministic hash of its string argument. Re-deriving it and
comparing against the published register on 29 August 2026:

    france 168,894/168,894  germany 108,016/108,016  us 73,859/73,859
    italy   41,662/41,662   portugal + spain + japan all 100.0%
    uk      31,583/34,120 (92.6%)      sweden 16/3,774 (0.4%)

456,200 of 622,104 cohort substations -- 73.3% -- carry six component scores
generated from the substation's name. The name is itself a placeholder built
from the identifier.

WHY THIS ONE MATTERS MOST
-------------------------
The other four gates cover DERIVED fields carrying the wrong quantity:
R_P5/R_P95 holding add_sum, CI_width holding a name hash, mult_product holding
the ESG composite core, R_base zeroed. Each was repairable because the inputs
survived -- re-deriving R_base from components is exactly what fixed uk.

C, V, I, E, S and T ARE the inputs. They are the whole basis of R_base, hence
R_median, hence every band, regional summary and league table the site
publishes. There is nothing upstream of them to re-derive from.

WHAT IT IS NOT
--------------
Not an overwrite. The fill is guarded by `if not comp.get(key)` -- it only ever
wrote where the value was missing or zero, so no measured component was
replaced. The defect is that a vacuum was filled with a placeholder and
published as a measurement rather than left absent.

That makes it a Convention #56 failure at the largest scale in the register.
classify_band has "Unclassified", classify_confidence returns None, the
connectors write "R_P5": None -- the machinery for saying "we do not know"
exists throughout this codebase, and here it was bypassed with a number.

FOUR CHECKS
-----------
  HASHED     all six components reproduce vary(0.35, name + '_' + K, 0.30)
  PARTIAL    some but not all six reproduce -- a mixture of measured and
             manufactured within one record, which is worse to reason about
             than either
  NO_COMPS   components absent or empty (the 78,558 of 5fefb9ac)
  UNCHECKED  components present but no name, so the derivation cannot be run.
             Convention #56: reported, never counted as clean

THIS BASELINE IS NOT A DEBT TO PAY DOWN
---------------------------------------
The R_base baseline was, and it was paid: DRIFT went 57,652 -> 0 in 3a14a7f6.
This one cannot be repaired by any script, because there is no measurement to
recover. Lowering it means either ingesting real component data or setting the
fabricated ones to None and letting the records read Unclassified -- a decision
about what the index can claim, not a code change. The baseline records the
scale so it cannot grow unnoticed while that decision is pending.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASELINE = ROOT / "scripts" / "components_baseline.json"
CHECKS = ("HASHED", "PARTIAL", "NO_COMPS", "UNCHECKED")
KEYS = ("C", "V", "I", "E", "S", "T")
EPS = 1e-9

sys.path.insert(0, str(ROOT / "scripts"))
try:
    from enrich_esg_gaps import vary
except Exception as ex:                                    # pragma: no cover
    sys.exit(f"ABORT: cannot import enrich_esg_gaps.vary — {ex}. This check "
             f"must use the same function that wrote the values, or it proves "
             f"nothing.")


def load_slugs():
    d = json.loads((ROOT / "intelligence" / "countries.json").read_text())
    return [c["slug"] for c in (d["countries"] if isinstance(d, dict) else d)]


def load_substations(slug):
    m = json.loads((ROOT / slug / "ssi-data.json").read_text())
    shards = m.get("substations_shards")
    if not shards:
        subs = m.get("substations")
        if subs is None:
            raise ValueError("manifest has neither substations nor shards")
        return subs
    out = []
    for e in shards:
        p = ROOT / slug / pathlib.Path(e["path"]).name
        r = json.loads(p.read_text())
        out.extend(r if isinstance(r, list) else (r.get("substations") or []))
    if not out:
        raise ValueError(f"{len(shards)} shards declared but no records read")
    return out


def hashed_keys(name, comps):
    """Which of the six reproduce the fill exactly."""
    return [k for k in KEYS
            if isinstance(comps.get(k), (int, float))
            and abs(round(vary(0.35, f"{name}_{k}", 0.30), 4) - comps[k]) <= EPS]


def audit(subs):
    c = {k: 0 for k in CHECKS}
    example = None
    for s in subs:
        comps = s.get("components") or {}
        if not any(isinstance(v, (int, float)) for v in comps.values()):
            c["NO_COMPS"] += 1
            continue
        name = s.get("name")
        if name is None:
            c["UNCHECKED"] += 1
            continue
        hits = hashed_keys(name, comps)
        if len(hits) == len(KEYS):
            c["HASHED"] += 1
            if example is None:
                example = s
        elif hits:
            c["PARTIAL"] += 1
    return c, example


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--update-baseline", action="store_true")
    args = ap.parse_args()

    slugs = load_slugs() if args.all else args.slugs
    if not slugs:
        sys.exit("give country slugs or --all")

    base = json.loads(BASELINE.read_text()) if BASELINE.exists() else {}
    live, unreadable, total = {}, [], 0

    for slug in sorted(slugs):
        try:
            subs = load_substations(slug)
        except Exception as ex:
            unreadable.append((slug, str(ex)))
            continue
        total += len(subs)
        c, ex = audit(subs)
        live[slug] = c
        if args.verbose and c["HASHED"]:
            n = len(subs)
            print(f"\n  {slug} ({n:,}) — {c['HASHED']:,} hashed "
                  f"({100 * c['HASHED'] / n:.1f}%)")
            if ex is not None:
                nm = ex.get("name")
                print(f"    e.g. {ex.get('substation_id')} · name {nm!r}")
                for k in KEYS:
                    print(f"      {k}  published {ex['components'][k]:<10} "
                          f"vary → {round(vary(0.35, f'{nm}_{k}', 0.30), 4)}")

    if args.update_baseline:
        BASELINE.write_text(json.dumps(live, indent=1, sort_keys=True) + "\n")
        print(f"\n  baseline written: {BASELINE.relative_to(ROOT)} "
              f"({len(live)} countries)")
        print("  This one is not a debt to pay down — see the module docstring.")
        return 0

    print(f"\n  Component provenance — {len(live)} countries, "
          f"{total:,} substations\n")
    print(f"    {'check':<12}{'live':>12}{'baseline':>12}{'delta':>10}")
    regressions = []
    for k in CHECKS:
        lv = sum(c[k] for c in live.values())
        bl = sum(base.get(s, {}).get(k, 0) for s in live)
        d = lv - bl
        if d > 0:
            regressions.append(k)
        print(f"    {k:<12}{lv:>12,}{bl:>12,}{d:>+10,}"
              f"{'  <-- REGRESSION' if d > 0 else ''}")

    hashed = sum(c["HASHED"] for c in live.values())
    if total:
        print(f"\n    {hashed:,} of {total:,} substations ({100 * hashed / total:.1f}%) "
              f"have all six components generated from their own name")

    worst = sorted(((c["HASHED"], s) for s, c in live.items() if c["HASHED"]),
                   reverse=True)
    if worst:
        print("\n    worst affected:")
        for h, s in worst[:12]:
            print(f"      {s:<16}{h:>9,}")

    if unreadable:
        print("\n    UNREADABLE (Convention #56 — not counted as clean):")
        for s, why in unreadable:
            print(f"      {s:<16}{why}")

    if not base:
        print("\n  No baseline recorded yet. Run --update-baseline to record the\n"
              "  known population; --strict then fails on any increase.")

    if args.strict:
        if unreadable:
            print("\nSTRICT: countries unreadable.")
            return 1
        if regressions:
            print(f"\nSTRICT: component provenance regressed "
                  f"({', '.join(regressions)}).")
            return 1
        print("\nSTRICT: no regression against baseline.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
