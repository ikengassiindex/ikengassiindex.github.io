#!/usr/bin/env python3
"""
Every substation, every published field: measured, manufactured, or absent.

    python3 scripts/ssi_provenance_census.py --all
    python3 scripts/ssi_provenance_census.py --all --out SSI_PROVENANCE_CENSUS.json
    python3 scripts/ssi_provenance_census.py --all --csv census.csv     # 622k rows
    python3 scripts/ssi_provenance_census.py france --verbose

WHY
---
Five separate defects were identified across 29 August 2026, each with its own
gate. Each gate answers one question over the whole cohort. None of them
answers the question an operator actually has to answer before publishing,
citing or depositing anything:

    for THIS substation, which of its published numbers mean anything?

This walks the register once and decides that per record, per field, using the
same derivations the five gates use — so the census and the gates cannot drift
apart in what they call manufactured.

THE VERDICTS
------------
components   MEASURED    present, and not reproducible from the name hash
             HASHED      all six reproduce round(vary(0.35, name+'_'+K, .30), 4)
             PARTIAL     some do, some do not — a mixture inside one record
             ABSENT      components {} — nothing was ever there
             UNNAMED     present but no name, so the test cannot be run

R_base       DERIVED     equals compute_r_base(components)
             ZEROED      exactly 0.0 while components are populated
             DRIFTED     present but does not equal the derivation
             ABSENT

R_median     CLOSES      within 5e-4 of soft_clip(R_base x mult) + add_sum
             ONLY_FLOOD  equals add_sum — the flood modifier alone
             OPEN        neither
             ABSENT

interval     REAL        R_P5 < R_P95 and CI_width agrees with the endpoints
             ADD_SUM     R_P5 == R_P95 == add_sum
             DEGENERATE  R_P5 == R_P95 for some other reason
             HASHED_W    CI_width reproduces vary(0.22, name, 0.15), orphaned
             ABSENT

band         GROUNDED    a band, with components behind it
             BLIND       a band, with no components behind it
             UNCLASSIFIED

RECORD VERDICT
--------------
  MANUFACTURED   components are HASHED — everything downstream inherits it,
                 because C V I E S T are the whole basis of R_base
  NO_BASIS       components ABSENT — nothing to compute from
  MIXED          components measured but some downstream field manufactured
  MEASURED       components measured and nothing downstream manufactured

MANUFACTURED is deliberately decided by the components alone. A record whose
inputs are a hash of its own name cannot be rescued by any downstream field
being correct — and today's uk repair is the worked example: it made the
pipeline internally consistent over inputs that were, for 31,583 of uk's 34,120
named records, name hashes. Internal consistency over manufactured inputs is a
smaller claim than it looks, and this census exists so that the difference is
never again invisible.

Convention #56 throughout: ABSENT is a verdict, not a gap in the count. Every
substation in the register receives one verdict in every dimension, and the
per-country totals must equal the fleet size — the script asserts that.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEYS = ("C", "V", "I", "E", "S", "T")
EPS = 1e-9
TOL = 5e-4

sys.path.insert(0, str(ROOT / "scripts"))
from enrich_esg_gaps import vary                                    # noqa: E402
from pipeline.scoring.engine import compute_r_base, soft_clip_upper  # noqa: E402

DIMS = ("components", "R_base", "R_median", "interval", "band", "record")


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


def verdicts(s, sweep_hashed=frozenset()):
    """sweep_hashed: component letters the provenance sweep found reproducible
    from a named seed for THIS country. See HASHED_FIELD below."""
    comps = s.get("components") or {}
    name = s.get("name")
    populated = any(isinstance(v, (int, float)) for v in comps.values())

    if not populated:
        v_comp = "ABSENT"
    elif name is None:
        v_comp = "UNNAMED"
    else:
        hits = sum(1 for k in KEYS
                   if isinstance(comps.get(k), (int, float))
                   and abs(round(vary(0.35, f"{name}_{k}", 0.30), 4) - comps[k]) <= EPS)
        v_comp = "HASHED" if hits == len(KEYS) else ("PARTIAL" if hits else "MEASURED")
        # HASHED above is EXACT REPRODUCTION of vary(0.35, name+'_'+K, 0.30) —
        # one generator, one constant set. It cannot catch a generator whose
        # constants we do not have. Israel's components are md5(sid+name+K)
        # through base ~0.4992 / spread ~1.099 clipped to [0,1]; chile's vary by
        # region. Both reproduce at r >= 0.999 in the sweep and both were
        # called MEASURED here.
        #
        # A per-record affine-on-hash test was built and REJECTED: chile's
        # records sit on no single line (median residual 4.7e-3, 49 of 965
        # within tolerance) because the generator is parameterised per region,
        # so the test missed a known positive AND flagged 182 chile T records
        # the sweep clears. Per-record exactness is the wrong instrument for a
        # per-region generator.
        #
        # So the field-level verdict is taken from the sweep, which measures
        # correlation against named seeds, and is labelled apart from HASHED so
        # the two claims are never confused:
        #   HASHED        this record reproduces exactly, here, now
        #   HASHED_FIELD  this record's country+component was found
        #                 reproducible by the sweep; the record inherits it
        if v_comp in ("MEASURED", "PARTIAL") and sweep_hashed:
            present = {k for k in KEYS if isinstance(comps.get(k), (int, float))}
            if present and present <= set(sweep_hashed):
                v_comp = "HASHED_FIELD"
            elif present & set(sweep_hashed):
                v_comp = "PARTIAL"

    rb = s.get("R_base_median")
    if rb is None:
        v_rb = "ABSENT"
    elif not populated:
        v_rb = "ZEROED" if rb == 0.0 else "DRIFTED"
    elif abs(compute_r_base(comps) - rb) <= TOL:
        v_rb = "DERIVED"
    elif rb == 0.0:
        v_rb = "ZEROED"
    else:
        v_rb = "DRIFTED"

    mp, ad, med = s.get("mult_product"), s.get("add_sum"), s.get("R_median")
    if med is None:
        v_med = "ABSENT"
    elif ad is not None and abs(med - ad) <= TOL:
        v_med = "ONLY_FLOOD"
    elif None not in (rb, mp, ad) and abs(soft_clip_upper(rb * mp) + ad - med) <= TOL:
        v_med = "CLOSES"
    else:
        v_med = "OPEN"

    p5, p95, w = s.get("R_P5"), s.get("R_P95"), s.get("CI_width")
    if p5 is None or p95 is None:
        v_int = "ABSENT"
    elif abs(p95 - p5) <= EPS:
        if ad is not None and abs(p5 - ad) <= EPS:
            v_int = "ADD_SUM"
        else:
            v_int = "DEGENERATE"
    elif (w is not None and name is not None
          and abs(round(vary(0.22, name, 0.15), 4) - w) <= EPS
          and abs(w - (p95 - p5)) > TOL):
        v_int = "HASHED_W"
    elif w is not None and abs(w - (p95 - p5)) > TOL:
        v_int = "HASHED_W"
    else:
        v_int = "REAL"

    cls = s.get("classification")
    if cls in (None, "Unclassified"):
        v_band = "UNCLASSIFIED"
    elif populated:
        v_band = "GROUNDED"
    else:
        v_band = "BLIND"

    if v_comp in ("HASHED", "HASHED_FIELD"):
        v_rec = "MANUFACTURED"
    elif v_comp == "ABSENT":
        v_rec = "NO_BASIS"
    elif v_comp == "PARTIAL" or v_int in ("ADD_SUM", "HASHED_W") \
            or v_rb in ("ZEROED", "DRIFTED"):
        v_rec = "MIXED"
    elif v_comp == "UNNAMED":
        v_rec = "MIXED"
    else:
        v_rec = "MEASURED"

    return {"components": v_comp, "R_base": v_rb, "R_median": v_med,
            "interval": v_int, "band": v_band, "record": v_rec}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", default="")
    ap.add_argument("--csv", default="")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--sweep", default="",
                    help="SSI_PROVENANCE_SWEEP_v2.json — supplies field-level "
                         "FABRICATED verdicts the exact test cannot reach. "
                         "Without it the census reports only what one "
                         "generator's constants can prove, and says so.")
    args = ap.parse_args()

    sweep = {}
    if args.sweep:
        raw = json.loads(pathlib.Path(args.sweep).read_text())
        for slug, blk in raw.items():
            letters = set()
            for path, res in (blk.get("fields") or {}).items():
                if (path.startswith("components.")
                        and res.get("verdict") == "FABRICATED"):
                    letters.add(path.split(".", 1)[1])
            if letters:
                sweep[slug] = letters
        print(f"  sweep loaded: {len(sweep)} countries carry a FABRICATED "
              f"component field")
    else:
        print("  NO SWEEP SUPPLIED — components are tested against "
              "vary(0.35, name+'_'+K, 0.30) only. A record fabricated by any "
              "other generator will read MEASURED. Pass --sweep.")

    slugs = load_slugs() if args.all else args.slugs
    if not slugs:
        sys.exit("give country slugs or --all")

    per_country, unreadable, total = {}, [], 0
    writer = fh = None
    if args.csv:
        fh = open(args.csv, "w", newline="", encoding="utf-8")
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["country", "substation_id"] + list(DIMS))

    for slug in sorted(slugs):
        try:
            subs = load_substations(slug)
        except Exception as ex:
            unreadable.append((slug, str(ex)))
            continue
        counts = {d: collections.Counter() for d in DIMS}
        sweep_hashed = sweep.get(slug, frozenset())
        for s in subs:
            v = verdicts(s, sweep_hashed)
            for d in DIMS:
                counts[d][v[d]] += 1
            if writer:
                writer.writerow([slug, s.get("substation_id")]
                                + [v[d] for d in DIMS])
        # Convention #56: every record gets a verdict in every dimension.
        for d in DIMS:
            assert sum(counts[d].values()) == len(subs), (
                f"{slug}/{d}: {sum(counts[d].values())} verdicts for "
                f"{len(subs)} substations — a record was skipped")
        per_country[slug] = {d: dict(counts[d]) for d in DIMS}
        total += len(subs)
    if fh:
        fh.close()

    agg = {d: collections.Counter() for d in DIMS}
    for c in per_country.values():
        for d in DIMS:
            agg[d].update(c[d])

    print(f"\n  SSI provenance census — {len(per_country)} countries, "
          f"{total:,} substations\n")
    for d in DIMS:
        print(f"    {d}")
        for k, n in agg[d].most_common():
            print(f"      {k:<14}{n:>9,}  {100 * n / max(total, 1):>5.1f}%")
        print()

    print("    by country — share of records whose verdict is MANUFACTURED "
          "or NO_BASIS")
    rows = []
    for slug, c in per_country.items():
        n = sum(c["record"].values())
        bad = c["record"].get("MANUFACTURED", 0) + c["record"].get("NO_BASIS", 0)
        rows.append((bad / max(n, 1), slug, bad, n))
    for share, slug, bad, n in sorted(rows, reverse=True):
        bar = "█" * int(round(share * 28))
        print(f"      {slug:<14}{bad:>8,} / {n:<8,} {100*share:>5.1f}%  {bar}")

    if unreadable:
        print("\n    UNREADABLE (Convention #56 — not counted as clean):")
        for s, why in unreadable:
            print(f"      {s:<16}{why}")

    if args.out:
        pathlib.Path(args.out).write_text(json.dumps(
            {"generated_at_commit_note": "run against the working tree",
             "n_substations": total,
             "cohort": {d: dict(agg[d]) for d in DIMS},
             "per_country": per_country}, indent=1, sort_keys=True) + "\n")
        print(f"\n  written {args.out}")
    if args.csv:
        print(f"  written {args.csv} ({total:,} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
