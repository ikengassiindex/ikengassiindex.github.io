#!/usr/bin/env python3
"""
Do the numbers on the country pages still match the register?

    python3 scripts/check_published_counts_match_data.py --all
    python3 scripts/check_published_counts_match_data.py turkey --verbose

WHY
---
The counts on each country page are BAKED INTO THE HTML as data-canonical
literals — fleet.total, fleet.voltage.ehv/hv/distribution — filled by
country-renderer.js::fillCanonicalContentAttrs. They are not computed from
ssi-data.json at page load. So a data repair does not reach the page, and a
page can state a figure the register contradicts, indefinitely, silently.

refresh_country_counts.py cannot close this. It works by replacing strings it
finds in a `.pre-remediate-*.backup`, so it can only refresh a country that
has one. 26 of 39 do not.

Turkey is the worked example: repairing 1,110 volt-scale voltage_kv values
moved its EHV fleet from 1,120 to 136 and its HV fleet from 1 to 789, while
all seven turkey pages went on saying 1,120 and 1.

This gate reads. It changes nothing.

BUCKETS — the same ones refresh_country_counts.py uses
    EHV           voltage_kv >= 220
    HV            110 <= voltage_kv < 220
    distribution  voltage_kv < 110, or absent/non-numeric
"""
from __future__ import annotations
import argparse, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEYS = ("fleet.total", "fleet.voltage.ehv", "fleet.voltage.hv",
        "fleet.voltage.distribution")


def load_slugs():
    d = json.loads((ROOT / "intelligence" / "countries.json").read_text())
    return [c["slug"] for c in (d["countries"] if isinstance(d, dict) else d)]


def load_subs(slug):
    man = json.loads((ROOT / slug / "ssi-data.json").read_text())
    subs = man.get("substations")
    if subs is None and man.get("substations_shards"):
        subs = []
        for e in man["substations_shards"]:
            p = ROOT / slug / pathlib.Path(e["path"]).name
            raw = json.loads(p.read_text())
            subs.extend(raw if isinstance(raw, list) else raw.get("substations", []))
    if subs is None:
        raise ValueError("no substations and no readable shards")
    return subs


def from_data(subs):
    num = lambda s: isinstance(s.get("voltage_kv"), (int, float)) and not isinstance(s.get("voltage_kv"), bool)
    return {
        "fleet.total": len(subs),
        "fleet.voltage.ehv": sum(1 for s in subs if num(s) and s["voltage_kv"] >= 220),
        "fleet.voltage.hv": sum(1 for s in subs if num(s) and 110 <= s["voltage_kv"] < 220),
        "fleet.voltage.distribution": sum(1 for s in subs
                                          if not num(s) or s["voltage_kv"] < 110),
    }


def from_pages(slug):
    """Every data-canonical literal found, per key, per file."""
    out = {}
    for f in sorted((ROOT / slug).glob("*.html")):
        if ".backup" in f.name:
            continue
        text = f.read_text(errors="replace")
        for k in KEYS:
            for m in re.finditer(
                    r'data-canonical="' + re.escape(k) + r'"[^>]*>\s*([\d,]+)\s*<', text):
                out.setdefault(k, {}).setdefault(m.group(1).replace(",", ""), []).append(f.name)
            for m in re.finditer(
                    r'"' + re.escape(k) + r'"\s*:\s*"([\d,]+)"', text):
                out.setdefault(k, {}).setdefault(m.group(1).replace(",", ""), []).append(f.name)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    slugs = load_slugs() if a.all else a.slugs
    if not slugs:
        sys.exit("give country slugs or --all")

    print("\n  published counts vs the register\n")
    bad = disagree = nopage = 0
    rows = []
    for slug in sorted(slugs):
        try:
            truth = from_data(load_subs(slug))
        except Exception as ex:
            print(f"    {slug:14} UNREADABLE: {ex}")
            bad += 1
            continue
        pages = from_pages(slug)
        if not pages:
            nopage += 1
            continue
        mismatches = []
        for k in KEYS:
            found = pages.get(k)
            if not found:
                continue
            for value, files in found.items():
                if int(value) != truth[k]:
                    mismatches.append((k, int(value), truth[k], len(files)))
        if mismatches:
            disagree += 1
            rows.append((slug, mismatches))

    for slug, ms in rows:
        print(f"    {slug}")
        for k, published, actual, nfiles in ms:
            print(f"      {k:30} page says {published:>8,}   data says {actual:>8,}"
                  f"   ({nfiles} file{'s' if nfiles != 1 else ''})")
    if not rows:
        print("    every published count matches the register")
    print(f"\n    {disagree} countries disagree · {nopage} with no page literals"
          f" · {bad} unreadable\n")
    return 1 if disagree else 0


if __name__ == "__main__":
    sys.exit(main())
