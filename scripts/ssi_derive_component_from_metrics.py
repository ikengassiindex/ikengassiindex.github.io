#!/usr/bin/env python3
"""
Write, alongside each published component, the value its OWN metrics give.

    python3 scripts/ssi_derive_component_from_metrics.py --all --dry-run
    python3 scripts/ssi_derive_component_from_metrics.py --all

WHY THIS EXISTS AND WHY IT DOES NOT OVERWRITE
---------------------------------------------
Doctrine says component_c = SIGMA intra_{c,m} x metric_m. The deployment does
not do that. `enrich_esg_gaps.py:317` fills any empty component with
vary(0.35, name + '_' + K, 0.30) — a hash of the substation's own name — and
456,184 records carry all six components from that hash.

Measured across 543,546 substations, the correlation between the published
component I and a weight-renormalised mean of its own measured metrics is

    r = +0.004

which is the absence of a relationship, not a weak one.

Four I-metrics are now genuinely measured across ~620,000 substations — I3,
I4, I5, I6 — and they reach no published score. But rebuilding component I
from them today would re-band 68.2 per cent of the estate on 0.509 of the
component's intra-weight, and would do it again when I1, I2, I7, I8 and I9
arrive. Operator decision, 31 August 2026: publish the measured quantity
ALONGSIDE, swap once coverage is complete.

So this script writes two diagnostic fields and changes no score:

    _<C>_from_metrics    the renormalised value the present metrics give
    _<C>_coverage        the share of that component's intra-weight behind it

Neither is consumed by the engine. Their entire purpose is that a reader of
the published record can see the divergence without re-deriving anything, and
that the conformance register can measure it. The day components are rebuilt
from metrics, these become the check on that rebuild rather than a substitute
for it.

CONVENTION #56
--------------
A record with no measured metric for a component gets NO field, not a zero
and not a default. Coverage is stated on every record that does get one, so a
value derived from half a definition can never be read as a value derived
from all of it.
"""
from __future__ import annotations
import argparse, json, os, pathlib, sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from pipeline.scoring.engine import INTRA_WEIGHTS          # noqa: E402

DECISION = "FINDING_component_I_cannot_be_rebuilt_yet.md"


def load_slugs():
    d = json.loads((ROOT / "intelligence" / "countries.json").read_text())
    return [c["slug"] for c in (d["countries"] if isinstance(d, dict) else d)]


def load(slug):
    man = json.loads((ROOT / slug / "ssi-data.json").read_text())
    shards = man.get("substations_shards")
    if not shards:
        return man, man.get("substations") or [], None
    subs, paths = [], []
    for e in shards:
        p = ROOT / slug / pathlib.Path(e["path"]).name
        raw = json.loads(p.read_text())
        block = raw if isinstance(raw, list) else (raw.get("substations") or [])
        subs.extend(block)
        paths.append((p, len(block), isinstance(raw, list)))
    return man, subs, paths


def derive(subs, dry):
    """Returns (written, per-component stats). Never touches components.<C>."""
    stats = {c: {"n": 0, "cov": 0.0} for c in INTRA_WEIGHTS}
    written = 0
    for s in subs:
        m = s.get("metrics") or {}
        touched = False
        for comp, weights in INTRA_WEIGHTS.items():
            have = {k: m[k] for k, w in weights.items()
                    if isinstance(m.get(k), (int, float))}
            if not have:
                # Convention #56: no metric, no field. Not a zero.
                continue
            cov = sum(weights[k] for k in have)
            if cov <= 0:
                continue
            val = sum(weights[k] * v for k, v in have.items()) / cov
            if not dry:
                s[f"_{comp}_from_metrics"] = round(val, 4)
                s[f"_{comp}_coverage"] = round(cov, 4)
            stats[comp]["n"] += 1
            stats[comp]["cov"] += cov
            touched = True
        if touched:
            written += 1
    return written, stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    slugs = load_slugs() if a.all else a.slugs
    if not slugs:
        sys.exit("give country slugs or --all")

    print(f"\n  component-from-metrics diagnostic — {DECISION}\n")
    print(f"  {'country':<14}{'records':>9}" +
          "".join(f"{c + ' cov':>10}" for c in INTRA_WEIGHTS))
    agg = {c: {"n": 0, "cov": 0.0} for c in INTRA_WEIGHTS}
    total = 0
    for slug in sorted(slugs):
        try:
            man, subs, paths = load(slug)
            n, st = derive(subs, a.dry_run)
        except Exception as ex:
            print(f"  {slug:<14}REFUSED — {ex}")
            continue
        total += n
        row = ""
        for c in INTRA_WEIGHTS:
            agg[c]["n"] += st[c]["n"]
            agg[c]["cov"] += st[c]["cov"]
            row += f"{(st[c]['cov'] / st[c]['n'] if st[c]['n'] else 0):>10.3f}"
        print(f"  {slug:<14}{n:>9,}{row}")
        if a.dry_run or not n:
            continue
        man.setdefault("meta", {}).setdefault("component_derivations", []).append({
            "fields": [f"_{c}_from_metrics" for c in INTRA_WEIGHTS],
            "at_utc": datetime.now(timezone.utc).isoformat(),
            "decision": DECISION,
            "note": ("diagnostic only; components.<C> is NOT modified. Written "
                     "so the divergence between doctrine (component = SIGMA "
                     "intra x metric) and deployment is visible in the "
                     "published record rather than only on re-derivation."),
            "coverage": {c: (round(st[c]["cov"] / st[c]["n"], 4)
                             if st[c]["n"] else None) for c in INTRA_WEIGHTS},
            "n_records": n})
        if paths is None:
            man["substations"] = subs
            (ROOT / slug / "ssi-data.json").write_text(json.dumps(man))
        else:
            off = 0
            for p, cnt, was_list in paths:
                blk = subs[off:off + cnt]
                off += cnt
                p.write_text(json.dumps(blk if was_list else
                                        {"substations": blk}))
            (ROOT / slug / "ssi-data.json").write_text(json.dumps(man))
    print(f"\n  {'TOTAL':<14}{total:>9,}" +
          "".join(f"{(agg[c]['cov'] / agg[c]['n'] if agg[c]['n'] else 0):>10.3f}"
                  for c in INTRA_WEIGHTS))
    print("\n  Coverage is the share of each component's intra-weight that has a")
    print("  measured metric behind it. It is not a quality score and must not")
    print("  be read as one: 1.000 would mean every metric is present, not that")
    print("  any of them is right.")
    if a.dry_run:
        print("\n  DRY RUN — nothing written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
