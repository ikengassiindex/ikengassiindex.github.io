#!/usr/bin/env python3
"""
Record WHERE each voltage_kv came from, so a default stops passing as a reading.

    python3 scripts/mark_voltage_provenance.py turkey --dry-run
    python3 scripts/mark_voltage_provenance.py turkey

THE PROBLEM THIS MAKES VISIBLE
------------------------------
score-country.py:104 and :106 fall back to 66 when the OSM voltage tag is
empty AND when parsing it raises. The stored 66 is then indistinguishable from
a measured 66. Turkey carries 2,895 of them — 71.4% of its fleet.

Nothing here changes a published value. It adds `_voltage_kv_source`, the same
class of additive audit field as `metrics`. Convention #7: a proxy that is
documented is a different object from a proxy that is silent.

THE VERDICTS, AND THE EVIDENCE FOR EACH
---------------------------------------
  default_no_identity  voltage_kv == 66, the name is the placeholder
                       "Substation <substation_id>", and there is no osm_id.
                       The record carries NO source identity of any kind, so
                       its 66 cannot be a reading of anything. Provably the
                       fallback.  turkey: 2,162

  unverified_66        voltage_kv == 66 on a genuinely named record
                       ("Maltepe GIS TM", "Kepsut RES"). Turkey does operate a
                       66 kV network, so this MAY be real — but it is not
                       separable from the fallback without the OSM tag.
                       Not a claim that it is wrong; a claim that it is
                       unverified.  turkey: 733

  tagged               any other numeric value. turkey: 1,112
  absent               no numeric voltage. turkey: 24

WHY TURKEY ONLY
---------------
The evidence that 66 is a default rather than a reading is the ABSENCE OF A
LADDER: a country with a real 66 kV population shows its neighbouring levels
on the same scale. Japan (6.6, 66, 154, 77, 275, 500) and australia
(33, 66, 132, 110, 220) both do, so their 66 kV records are genuine and are
not marked. Turkey shows 66 alone, with every real Turkish level having sat in
the volts bucket until 0ef6b3ee.

Running this on a country without that evidence would manufacture a doubt
rather than record one, so the script refuses any slug not listed in EVIDENCED.
"""
from __future__ import annotations
import argparse, collections, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_KV = 66.0
EVIDENCED = {"turkey": "FINDING_turkey_voltage_units.md section 5 — 66 stands "
                       "alone on turkey's ladder while every real Turkish "
                       "level sat in the volts bucket"}


def verdict(s):
    v = s.get("voltage_kv")
    if not isinstance(v, (int, float)) or isinstance(v, bool):
        return "absent"
    if float(v) != DEFAULT_KV:
        return "tagged"
    sid = s.get("substation_id")
    name = (s.get("name") or "").strip()
    if sid is not None and name == f"Substation {sid}" and not s.get("osm_id"):
        return "default_no_identity"
    return "unverified_66"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if not a.slugs:
        sys.exit("give a country slug")

    for slug in a.slugs:
        if slug not in EVIDENCED:
            print(f"  {slug}: REFUSED — no evidence on file that this country's "
                  f"66 kV records are defaults. Marking it would manufacture a "
                  f"doubt rather than record one.")
            continue
        manp = ROOT / slug / "ssi-data.json"
        man = json.loads(manp.read_text())
        subs = man.get("substations")
        if subs is None:
            print(f"  {slug}: sharded manifests not handled here")
            continue
        counts = collections.Counter()
        for s in subs:
            v = verdict(s)
            counts[v] += 1
            if not a.dry_run:
                s["_voltage_kv_source"] = v
        print(f"\n  {slug} — {len(subs):,} substations")
        for k, n in counts.most_common():
            print(f"      {k:22}{n:>7,}")
        assert sum(counts.values()) == len(subs)
        if not a.dry_run:
            man.setdefault("meta", {})["voltage_provenance"] = {
                "marked_utc": __import__("datetime").datetime.now(
                    __import__("datetime").timezone.utc).isoformat(),
                "evidence": EVIDENCED[slug],
                "counts": dict(counts),
                "note": "additive audit field; no published value changed",
            }
            manp.write_text(json.dumps(man))
            print(f"      written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
