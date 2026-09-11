#!/usr/bin/env python3
"""
Prove the -0.0 hygiene changes nothing in a published record except -0.0.

    python3 scripts/test_numeric_hygiene_is_value_preserving.py

WHY A TEST AND NOT AN ARGUMENT

    The argument is short and sounds complete: `clean()` is the identity on
    everything except negative zero, it is applied only at return boundaries,
    therefore nothing else can change. Fifteen unit tests pin the first claim.

    "Safe by construction" is exactly the reasoning that failed twice this
    week — a CI repair that covered one workflow of three, and a -0.0 clamp
    that covered one write site of five. So this measures it instead.

HOW

    Score REAL substations twice under an identical RNG seed: once with the
    hygiene neutralised to the identity function, once with it live. Serialise
    both records and compare the text.

    The two texts must differ ONLY by "-0.0" tokens becoming "0.0". Any other
    difference — a value moved, a key gained or lost, a type changed — is a
    failure, and the diff is printed.

    Seeding matters because score_substation runs a 10,000-iteration Monte
    Carlo. Both `random` and `numpy.random` are reseeded identically before
    each call, so the two runs see the same draws and any difference is the
    hygiene and nothing else.
"""
from __future__ import annotations
import json, pathlib, random, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "pipeline"))

SEED = 20260911
N_SUBS = 40


def score_all(subs, neutralise):
    from scoring import engine, numeric_hygiene
    real_clean, real_nz = engine._nz_clean, engine._nz
    if neutralise:
        engine._nz_clean = lambda o: o
        engine._nz = lambda x: x
    out = []
    try:
        for s in subs:
            random.seed(SEED)
            np.random.seed(SEED)
            out.append(engine.score_substation(json.loads(json.dumps(s))))
    finally:
        engine._nz_clean, engine._nz = real_clean, real_nz
    return out


def main() -> int:
    slugs = [c["slug"] for c in json.loads(
        (ROOT / "intelligence" / "countries.json").read_text())["countries"]]

    # SELECTING A POOL THAT ACTUALLY EXERCISES THE DEFECT
    #
    # The first version of this test scored the first 40 substations of the
    # first country and removed zero -0.0 tokens, so it reported INCONCLUSIVE
    # rather than PASS. That was the test working: a run that does not reach
    # the thing under test is not evidence about it.
    #
    # The reason it found nothing is worth keeping. There are two producers of
    # -0.0 in a scored record and only one of them is reproducible:
    #
    #   skewness         comes out of a 10,000-iteration Monte Carlo. Re-scoring
    #                    the same substation draws different samples, so a
    #                    published -0.0 skewness will not reappear on demand.
    #   modifier_impacts is round(value - 1.0, 4) — pure arithmetic on stored
    #                    inputs. Any modifier in (0.99995, 1.0) yields -0.0,
    #                    every time.
    #
    # So the pool is chosen deterministically: substations carrying a modifier
    # in that band. If none exist the test says so rather than passing.
    def yields_negzero(sub):
        for v in (sub.get("modifiers") or {}).values():
            if isinstance(v, (int, float)) and 0.99995 < v < 1.0:
                return True
        return False

    pool, scanned = [], 0
    for slug in slugs:
        man = json.loads((ROOT / slug / "ssi-data.json").read_text())
        blocks = [man.get("substations") or []]
        for e in (man.get("substations_shards") or []):
            raw = json.loads((ROOT / slug / pathlib.Path(e["path"]).name).read_text())
            blocks.append(raw if isinstance(raw, list) else (raw.get("substations") or []))
        for blk in blocks:
            for sub in blk:
                scanned += 1
                if yields_negzero(sub):
                    pool.append(sub)
                    if len(pool) >= N_SUBS:
                        break
            if len(pool) >= N_SUBS:
                break
        if len(pool) >= N_SUBS:
            break
    print(f"\n  scanned {scanned:,} published substations to find "
          f"{len(pool)} carrying a modifier in (0.99995, 1.0)")

    if not pool:
        sys.exit("no substations found to score")

    print(f"\n  scoring {len(pool)} real substations twice, seed {SEED}")
    before = score_all(pool, neutralise=True)
    after = score_all(pool, neutralise=False)

    # Compare key by key, not by string surgery. The first version of this
    # comparison built an "expected" text with str.replace and declared any
    # mismatch a failure; it flagged a record whose only difference WAS a
    # -0.0, because the replace chain does not model JSON. A structural walk
    # cannot make that mistake: it names the path of every difference and
    # decides each one on the pair of values, not on the surrounding text.
    import math

    def is_negzero(v):
        return isinstance(v, float) and v == 0.0 and math.copysign(1.0, v) < 0

    def diff(b, a, path, out):
        if isinstance(b, dict) and isinstance(a, dict):
            for k in set(b) | set(a):
                if k not in b or k not in a:
                    out.append((f"{path}.{k}", "key present in one only", ""))
                else:
                    diff(b[k], a[k], f"{path}.{k}", out)
        elif isinstance(b, list) and isinstance(a, list):
            if len(b) != len(a):
                out.append((path, f"length {len(b)}", f"length {len(a)}"))
            else:
                for i, (x, y) in enumerate(zip(b, a)):
                    diff(x, y, f"{path}[{i}]", out)
        elif is_negzero(b) and a == 0.0 and not is_negzero(a):
            out.append((path, "-0.0", "0.0"))          # the intended change
        elif repr(b) != repr(a):
            out.append((path, repr(b), repr(a)))       # anything else

    bad, nfixed = [], 0
    for i, (b, a) in enumerate(zip(before, after)):
        d = []
        diff(b, a, "", d)
        for path, was, now in d:
            if was == "-0.0" and now == "0.0":
                nfixed += 1
            else:
                bad.append((i, path, was, now))

    print(f"\n  records scored          {len(pool)}")
    print(f"  -0.0 tokens removed     {nfixed}")
    print(f"  records changed in any\n  other way              {len(bad)}")

    if bad:
        print(f"\n  FAIL — {len(bad)} difference(s) that are not -0.0 -> 0.0")
        for i, path, was, now in bad[:10]:
            print(f"    record {i}  {path}")
            print(f"       before {was}")
            print(f"       after  {now}")
        return 1

    if nfixed == 0:
        print(f"\n  INCONCLUSIVE — the hygiene removed nothing, so this run")
        print(f"  did not exercise it. That is not a pass: pick substations")
        print(f"  whose scores actually produce -0.0, or widen N_SUBS.")
        return 2

    print(f"\n  PASS — every difference is a -0.0 becoming 0.0, and there are")
    print(f"  {nfixed} of them. No value moved, no key gained or lost.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
