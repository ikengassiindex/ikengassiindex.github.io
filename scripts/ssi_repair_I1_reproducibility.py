#!/usr/bin/env python3
"""
Renormalise published I1 from the published _I1_raw, so the pair agrees.

    python3 scripts/ssi_repair_I1_reproducibility.py --dry-run
    python3 scripts/ssi_repair_I1_reproducibility.py

WHAT IS WRONG

    ssi_derive_metric_I1.py computed I1 from the UNROUNDED raw and published
    _I1_raw rounded to 5 dp, so the two need not agree in the last digit:

        true raw 0.0017612 -> I1 published 0.00059
        _I1_raw  0.00176   -> recomputes to  0.00058

    46,391 of 622,079 records (7.457%) carry an I1 that cannot be recomputed
    from their own published raw. The purpose of publishing the raw is that a
    reader can verify the metric without trusting the producer; for those
    records that verification fails, and it fails in a way that looks like the
    reader's error.

WHY THIS DOES NOT RE-READ THE ERA5 ARCHIVE

    The same argument as derive_from_raw() in ssi_derive_metrics_I4_I6.py.
    The annual snow maxima are already carried per record as _I1_raw. The
    defect is in how the NORMALISER consumed them, not in the values. Re-running
    the full derivation would re-read 3.1 GB of ERA5-Land to arrive at numbers
    the records already hold, and would silently absorb any drift in the
    reanalysis into a change advertised as a rounding repair.

    ANCHOR is frozen at 0.9029 and is NOT recomputed. This changes no anchor,
    no coverage, no refusal, and no record's raw. It changes one digit of I1 on
    the records where the published pair disagreed.

WHAT IT REFUSES TO DO

    A record without _I1_raw is left alone and counted - the repair cannot
    invent an input it does not have. A record whose recomputed value differs
    from the published one by more than one unit in the 5th decimal is REFUSED
    and named: that would not be a rounding artefact, it would mean the anchor
    or the raw had changed, and this instrument has no business papering over
    that.
"""
from __future__ import annotations
import argparse, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ANCHOR = 0.9029          # FROZEN, DECISION_I1_anchor.md, 9 September 2026
IRI_TOP = 0.30
TOL = 1.5e-5             # one unit in the 5th decimal, with room for float noise


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

    seen = changed = no_raw = 0
    refused = []
    per_country = {}
    for slug in slugs():
        man, subs, paths = load(slug)
        n = 0
        for k, s in enumerate(subs):
            m = s.get("metrics") or {}
            if "I1" not in m:
                continue
            raw = s.get("_I1_raw")
            if not isinstance(raw, (int, float)):
                no_raw += 1
                continue
            seen += 1
            want = round(IRI_TOP * min(1.0, max(0.0, raw) / ANCHOR), 5) + 0.0
            cur = m["I1"]
            if abs(want - cur) > TOL:
                refused.append((slug, k, cur, want, raw))
                continue
            if want != cur:
                if not a.dry_run:
                    m["I1"] = want
                n += 1
        if refused:
            break
        if n and not a.dry_run:
            save(slug, man, subs, paths)
        per_country[slug] = n
        changed += n
        del subs

    if refused:
        print(f"\n  REFUSED — {len(refused)} record(s) differ by more than one "
              f"unit in the 5th decimal.")
        print(f"  That is not a rounding artefact. Nothing written.")
        for r in refused[:5]:
            print(f"    {r[0]} #{r[1]}: published {r[2]}, from raw {r[4]} -> {r[3]}")
        return 1

    print(f"\n  {seen:,} records carry both I1 and _I1_raw")
    print(f"  {no_raw:,} carry I1 without _I1_raw and were left alone")
    print(f"  {changed:,} ({100*changed/max(1,seen):.3f}%) need their last digit "
          f"corrected\n")
    for slug in sorted(per_country):
        if per_country[slug]:
            print(f"    {slug:<16}{per_country[slug]:>9,}")
    print(f"\n  anchor {ANCHOR} unchanged · no raw changed · no coverage changed")
    print(f"  {'DRY RUN — nothing written.' if a.dry_run else 'written.'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
