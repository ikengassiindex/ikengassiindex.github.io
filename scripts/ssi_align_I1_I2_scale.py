#!/usr/bin/env python3
"""
Put I1 and I2 on the same scale as I3, I4, I5 and I6.

    python3 scripts/ssi_align_I1_I2_scale.py --dry-run
    python3 scripts/ssi_align_I1_I2_scale.py

WHAT IS WRONG

    Construct section 03 defines both normalisation methods as producing a
    value in [0, 1]:

        Method B   N(x) = soft_clip((x - P5) / (P95 - P5))     I4, I6, (I5)
        Method C   N(x) = (x - x_min) / (x_max - x_min)        I1, I2, I3

    Published, I3/I4/I5/I6 carry N(x) in [0, 1]. I1 and I2 carry 0.30 x N(x)
    in [0, 0.30].

    The construct's line reads "Applies to: I1, I2, I3 [0, 0.30]", and that
    bracket is genuinely ambiguous: beside C3 it reads "[0%, 100%]" and beside
    E2 "(E2_local - 1.50) / (1.85 - 1.50)", which are INPUT bounds — but
    DECISION_I1_anchor.md reads it as the output interval ("raw 0.9029 -> IRI
    0.3000"), and I1's raw runs to 0.9029 m, which cannot be an input bound of
    0.30. I3 resolved the ambiguity one way and I1/I2 the other. Both readings
    are defensible; together they are incoherent.

WHY IT MATTERS

    ssi_derive_component_from_metrics.py computes

        _<C>_from_metrics = sum(INTRA_WEIGHTS[k] * metrics[k]) / coverage

    over both scales at once, so I1 and I2 enter the shadow component at
    roughly 30 per cent of the weight the definition gives them. No published
    R score is affected - the engine does not read that field - but it is the
    number the eventual component rebuild is meant to be validated against.

WHAT THIS DOES

    For every record carrying I1 or I2, recomputed from the PUBLISHED rounded
    raw so the result is reproducible from the record:

        I<n>        = round(min(1, raw / ANCHOR), 4)      [0, 1]   was 0.30 x this
        _I<n>_iri   = round(0.30 * min(1, raw / ANCHOR), 5)        new field

    Exactly the shape I3 already publishes, including its precisions: the
    metric at 4 dp and the IRI at 5 dp, each derived from the raw rather than
    from each other. (0.30 x I3's published 0.4073 is 0.12219, but _I3_iri is
    0.12218, because both hang off the raw independently. Copied deliberately.)

WHAT IT DOES NOT TOUCH

    No raw. No anchor. No coverage. No refusal. No record gains or loses a
    metric. The saturated records stay saturated - they simply saturate at 1.0
    instead of 0.30, with _I<n>_iri at 0.30.

    _<C>_from_metrics and _<C>_coverage are NOT recomputed here: they are a
    separate instrument's output and re-running it is the next step, not this
    one.
"""
from __future__ import annotations
import argparse, collections, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
IRI_TOP = 0.30
SPEC = {                       # metric -> (raw field, where, anchor)
    "I1": ("_I1_raw", "record",  0.9029),
    "I2": ("_I2_raw", "metrics", 45.3363),
}


def slugs():
    d = json.loads((ROOT / "intelligence" / "countries.json").read_text())
    return [c["slug"] for c in (d["countries"] if isinstance(d, dict) else d)]


def load(slug):
    man = json.loads((ROOT / slug / "ssi-data.json").read_text())
    sh = man.get("substations_shards")
    if not sh:
        return man, man.get("substations") or [], None
    subs, paths = [], []
    for e in sh:
        q = ROOT / slug / pathlib.Path(e["path"]).name
        raw = json.loads(q.read_text())
        blk = raw if isinstance(raw, list) else (raw.get("substations") or [])
        subs.extend(blk)
        paths.append((q, len(blk), isinstance(raw, list)))
    return man, subs, paths


def save(slug, man, subs, paths):
    if paths is None:
        man["substations"] = subs
        (ROOT / slug / "ssi-data.json").write_text(json.dumps(man))
        return
    off = 0
    for q, cnt, was_list in paths:
        q.write_text(json.dumps(subs[off:off + cnt] if was_list
                                else {"substations": subs[off:off + cnt]}))
        off += cnt
    (ROOT / slug / "ssi-data.json").write_text(json.dumps(man))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    done = collections.Counter(); already = collections.Counter()
    noraw = collections.Counter(); sat = collections.Counter()
    for slug in slugs():
        man, subs, paths = load(slug)
        touched = False
        for s in subs:
            m = s.get("metrics") or {}
            for k, (rf, where, anchor) in SPEC.items():
                if k not in m:
                    continue
                src = s if where == "record" else m
                raw = src.get(rf)
                if not isinstance(raw, (int, float)):
                    noraw[k] += 1
                    continue
                n = min(1.0, max(0.0, raw) / anchor)
                new = round(n, 4) + 0.0
                iri = round(IRI_TOP * n, 5) + 0.0
                if m.get(k) == new and m.get(f"_{k}_iri") == iri:
                    already[k] += 1
                    continue
                if not a.dry_run:
                    m[k] = new
                    m[f"_{k}_iri"] = iri
                done[k] += 1
                touched = True
                if n >= 1.0:
                    sat[k] += 1
        if touched and not a.dry_run:
            save(slug, man, subs, paths)
        del subs

    print(f"\n  ALIGNING I1 and I2 to [0, 1], with _I<n>_iri carrying the "
          f"0.30 contribution\n")
    print(f"  {'metric':<8}{'rescaled':>12}{'already':>10}{'no raw':>9}"
          f"{'saturated':>12}")
    for k in SPEC:
        print(f"  {k:<8}{done[k]:>12,}{already[k]:>10,}{noraw[k]:>9,}"
              f"{sat[k]:>12,}")
    print(f"\n  no raw, no anchor, no coverage and no refusal was changed")
    print(f"  {'DRY RUN — nothing written.' if a.dry_run else 'written.'}")
    if not a.dry_run:
        print(f"\n  next: re-run ssi_derive_component_from_metrics.py — "
              f"_<C>_from_metrics\n  was computed across two scales and is "
              f"stale until it is.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
