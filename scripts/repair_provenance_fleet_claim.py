#!/usr/bin/env python3
"""
Repair two defects in stored per-record provenance strings.

    python3 scripts/repair_provenance_fleet_claim.py --all --dry-run
    python3 scripts/repair_provenance_fleet_claim.py --all

DEFECT 1 — A CLAIM THE MECHANISM NEVER DELIVERED
------------------------------------------------
`_metrics_source` on 620,696 records and `_component_T_source` on 17,502 say
the metric was normalised "Method B over fleet P5/P95". It was not. The
derivation computes P5/P95 inside derive(slug, ...), over that country's
records only.

The doctrine was never wrong about this. The master Complete Formula Construct
states that `B_percentile` is "anchored to fleet percentiles within the
country", and gives the reason: a percentile anchored across the cohort would
move a country's scores when an unrelated country is onboarded. Only the
scripts' own strings overclaimed, and a reader of the published record had no
way to know the two disagreed.

DEFECT 2 — A HEAP ADDRESS IN PUBLISHED PROVENANCE
-------------------------------------------------
136,731 records across us, uk, mexico and greenland carry

    kv >= <function make_floor.<locals>.floor_fn at 0x7f...>

because derive() interpolated the floor CLOSURE rather than the describe
string make_floor has returned since it was written. The string is unreadable
and its address differs on every run, so the same derivation produced
different provenance each time it was executed.

WHAT THIS SCRIPT DOES NOT DO
----------------------------
It does not touch a single metric value. No I4, I6, T or any other number is
read or written. Values are correct; only their description was wrong, and
re-deriving to fix a string would have been the more dangerous repair — I4 and
I6 still normalise through the defective engine soft_clip_upper (M-006), so a
re-derivation today would carry that defect forward under the guise of a
provenance fix.

CONVENTION #56
--------------
Anchored rewrite only. Every replacement matches an exact expected substring
or a tightly-shaped regex. A record whose string matches no known shape is
REFUSED, the country is left untouched, and the run exits non-zero. Nothing is
inferred and nothing is rebuilt from scratch.
"""
from __future__ import annotations
import argparse, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

OLD_FLEET = "Method B over fleet P5/P95"
NEW_FLEET = "Method B over this country's fleet P5/P95"
# NOT [^>]*? — a function repr contains its own angle brackets, as in
# "<function make_floor.<locals>.<lambda> at 0x7f...>". Excluding '>' made the
# pattern match nothing at all, and the dry run reported 0 addresses removed
# where 136,731 were expected. Non-greedy '.' is safe here because the repr
# carries exactly one " at 0x" and the match is anchored on it.
FN_REPR = re.compile(r"<function\s.*?\sat\s0x[0-9a-f]+>")


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


def floor_label(man):
    """The readable floor for this country, from its own derivation record.

    `kv_floor_label` is present where the floor is sub-national. Where the
    floor is a scalar the scalar IS the label. Returning None means the
    country cannot be repaired and must be refused rather than guessed at.
    """
    for e in reversed((man.get("meta") or {}).get("metric_derivations") or []):
        if "I4" not in (e.get("metrics") or []):
            continue
        if e.get("kv_floor_label") is not None:
            return str(e["kv_floor_label"])
        kv = e.get("kv_floor")
        if isinstance(kv, (int, float)):
            return str(kv)
    return None


def repair_string(v, label):
    """Return (new, changed, unresolved). Never invents; only substitutes."""
    out, changed = v, False
    if OLD_FLEET in out:
        out = out.replace(OLD_FLEET, NEW_FLEET)
        changed = True
    if FN_REPR.search(out):
        if label is None:
            return v, False, True
        out = FN_REPR.sub(label, out)
        changed = True
    return out, changed, False


def run(slug, dry):
    man, subs, paths = load(slug)
    label = floor_label(man)
    ms = ts = addr = 0
    unresolved = 0
    unknown = 0
    for s in subs:
        for key, counter in (("_metrics_source", "ms"),
                             ("_component_T_source", "ts")):
            v = s.get(key)
            if not isinstance(v, str):
                continue
            had_addr = bool(FN_REPR.search(v))
            new, changed, unres = repair_string(v, label)
            if unres:
                unresolved += 1
                continue
            if not changed:
                # A source string that carries neither defect is either already
                # repaired or a shape this script has never seen. Both are
                # reported; neither is edited.
                if OLD_FLEET not in v and NEW_FLEET not in v:
                    unknown += 1
                continue
            if had_addr:
                addr += 1
            if counter == "ms":
                ms += 1
            else:
                ts += 1
            if not dry:
                s[key] = new
    if unresolved:
        raise ValueError(f"{unresolved:,} records carry a function repr and "
                         f"this country declares no readable floor label")
    if unknown:
        raise ValueError(f"{unknown:,} source strings match no known shape")
    if not dry and (ms or ts):
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
    return ms, ts, addr, label


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    slugs = load_slugs() if a.all else a.slugs
    if not slugs:
        sys.exit("give country slugs or --all")

    print("\n  provenance repair — the fleet claim and the function repr\n")
    print(f"  {'country':<14}{'_metrics_source':>17}{'_component_T':>14}"
          f"{'addr removed':>14}  floor")
    tm = tt = ta = 0
    refused = []
    for slug in slugs:
        try:
            ms, ts, addr, label = run(slug, a.dry_run)
        except Exception as ex:
            refused.append(slug)
            print(f"  {slug:<14}REFUSED — {ex}")
            continue
        tm += ms
        tt += ts
        ta += addr
        print(f"  {slug:<14}{ms:>17,}{ts:>14,}{addr:>14,}  {label or '—'}")
    print(f"\n  {'TOTAL':<14}{tm:>17,}{tt:>14,}{ta:>14,}")
    if a.dry_run:
        print("\n  dry run — nothing written")
    if refused:
        print(f"\n  REFUSED {len(refused)}: {', '.join(refused)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
