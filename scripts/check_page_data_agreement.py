#!/usr/bin/env python3
"""
check_page_data_agreement.py — does the page say what the data says?

    python3 scripts/check_page_data_agreement.py --all
    python3 scripts/check_page_data_agreement.py --all --strict     # exit 1 on any mismatch
    python3 scripts/check_page_data_agreement.py japan france
    python3 scripts/check_page_data_agreement.py --all --json out.json

Read-only. Never writes to the repo.

WHY THIS EXISTS
---------------
Every published figure on a country page is marked up with a data-canonical
attribute naming what it claims to be:

    <span data-canonical="fleet.total">6,168</span>

That is a machine-checkable contract, and nothing was checking it. Measured
27 August 2026 across the live cohort:

    fleet.total                 10 of 39 countries wrong
    fleet.voltage.ehv / .hv      9 of 39 wrong
    fleet.voltage.distribution  10 of 39 wrong
    fleet.n_regions             38 of 39 wrong
    index.html data-subs        15 of 39 wrong  (corrected 27 Aug)

fleet.n_regions reads "20" on 38 countries. Twenty is Italy's region count —
the pages were generated from an Italy template and that figure was never
re-derived. France's page claims 20 regions against 102 in its data;
australia claims 20 against 8. This is the Italy-clone family the retired
sentinel suite was built to catch, reaching production unchallenged.

WHY THE EXISTING CHECKS MISS IT
--------------------------------
Stage 7e scans rendered pages for residue patterns — "Loading…", "||TOKEN||",
">GAP<" — which are the signatures of data that FAILED TO ARRIVE. A figure
that is present, well-formed, plausible and simply wrong passes every one of
them. So does a schema validator, which checks that a key exists and has the
right type. Wrongness of this kind is only visible by comparing the claim to
its source, which is what this does.

WHAT IT COMPARES
----------------
Per country, against <slug>/ssi-data.json and <slug>/grid-geo.json:

    fleet.total                 number of substations
    fleet.voltage.ehv           substations at >= 220 kV
    fleet.voltage.hv            substations at 110-220 kV
    fleet.voltage.distribution  the remainder (< 110 kV or untagged)
    fleet.n_regions             intelligence/country-configs/<slug>.json,
                                admin.l1.count — NOT len(regions). The regions
                                array is a by-product of the spatial join: it
                                carries a finer administrative tier on france,
                                japan, uk and portugal, and an "Unknown" bucket
                                on germany, italy, spain and sweden. The config
                                declares the tier the index reports at. Where
                                the two disagree it is reported separately as
                                a data finding, not as a page error.
    fleet.grid_lines            line records in grid-geo, shards resolved

Plus, once for the cohort, the root index.html data-subs attribute on each
country's map path — the figure shown in the landing-page tooltip.

Counts are read Convention #79 shard-aware throughout. Reading
data["substations"] directly returns nothing on the six sharded countries,
which is exactly how france's landing-page tooltip came to display 0.

WHY IT IS CHEAP
---------------
No browser, no network, no rendering. It reads files and compares numbers, so
it can run on every push rather than weekly, and it costs seconds.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

def _find_repo() -> Path:
    """The repo is the current directory when it looks like one, else the
    parent of this script's directory (the in-scripts/ case). Lets the check
    run either from scripts/ inside the repo or from anywhere else with the
    repo as the working directory."""
    cwd = Path.cwd()
    if (cwd / "intelligence" / "countries.json").exists():
        return cwd
    here = Path(__file__).resolve().parent.parent
    if (here / "intelligence" / "countries.json").exists():
        return here
    sys.exit("ABORT: run from the ikengassiindex.github.io repo root "
             "(or place this script in its scripts/ directory).")


REPO = _find_repo()
EHV_KV = 220
HV_KV = 110

# Pages that carry fleet.* figures. Others exist but restate these.
PAGES = ("index.html", "intelligence.html", "regional.html", "data.html",
         "esg-report.html", "methodology.html", "map.html")


def cohort_slugs() -> list[str]:
    cj = json.loads((REPO / "intelligence" / "countries.json").read_text())
    return sorted(c["slug"] for c in cj["countries"] if "slug" in c)


def load_country(slug: str):
    p = REPO / slug / "ssi-data.json"
    if not p.exists():
        return None, []
    d = json.loads(p.read_text())
    if isinstance(d, list):
        return {}, d
    if d.get("substations_shards"):
        subs = []
        for e in d["substations_shards"]:
            rel = e["path"] if isinstance(e, dict) else e
            sp = p.parent / Path(rel).name
            if sp.exists():
                q = json.loads(sp.read_text())
                subs += q if isinstance(q, list) else (q.get("substations") or [])
        return d, subs
    return d, (d.get("substations") or [])


def count_lines(slug: str):
    p = REPO / slug / "grid-geo.json"
    if not p.exists():
        return None
    g = json.loads(p.read_text())
    n = len(g.get("l") or [])
    for e in (g.get("l_shards") or []):
        rel = e["path"] if isinstance(e, dict) else e
        sp = p.parent / Path(rel).name
        if sp.exists():
            q = json.loads(sp.read_text())
            n += len(q if isinstance(q, list) else (q.get("l") or q.get("lines") or []))
    return n


def config_regions(slug: str):
    p = REPO / "intelligence" / "country-configs" / f"{slug}.json"
    if not p.exists():
        return None
    l1 = (json.loads(p.read_text()).get("admin") or {}).get("l1") or {}
    return l1.get("count")


def truth_for(slug: str) -> dict:
    root, subs = load_country(slug)
    if root is None:
        return {}
    kv = lambda s: s.get("voltage_kv") if isinstance(s.get("voltage_kv"), (int, float)) else 0
    ehv = sum(1 for s in subs if kv(s) >= EHV_KV)
    hv = sum(1 for s in subs if HV_KV <= kv(s) < EHV_KV)
    return {
        "fleet.total": len(subs),
        "fleet.voltage.ehv": ehv,
        "fleet.voltage.hv": hv,
        "fleet.voltage.distribution": len(subs) - ehv - hv,
        "fleet.n_regions": config_regions(slug),
        "fleet.grid_lines": count_lines(slug),
    }


def root_of(slug: str):
    root, _ = load_country(slug)
    return root if isinstance(root, dict) else None


def page_claims(slug: str) -> dict:
    """{key: {value: [pages that assert it]}} across the country's pages."""
    claims: dict[str, dict[int, list[str]]] = {}
    for page in PAGES:
        p = REPO / slug / page
        if not p.exists():
            continue
        for key, raw in re.findall(r'data-canonical="(fleet\.[^"]+)">([^<]*)<', p.read_text()):
            t = raw.replace(",", "").strip()
            if not t.isdigit():
                continue
            claims.setdefault(key, {}).setdefault(int(t), []).append(page)
    return claims


def landing_claims() -> dict:
    p = REPO / "index.html"
    if not p.exists():
        return {}
    html = p.read_text()
    out = {}
    for slug, raw in re.findall(
            r'data-href="([a-z-]+)/index\.html"[^>]*?data-subs="([^"]*)"', html, re.I):
        t = raw.replace(",", "").strip()
        out[slug] = int(t) if t.isdigit() else None
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("countries", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 on page errors. The declared config-vs-data "
                         "region questions are reported but do not fail: they "
                         "are an open data decision, not a page defect, and a "
                         "check that is permanently red teaches people to "
                         "ignore it.")
    ap.add_argument("--json", metavar="PATH")
    args = ap.parse_args()

    slugs = cohort_slugs() if (args.all or not args.countries) else args.countries
    landing = landing_claims()
    findings, checked = [], 0

    for slug in slugs:
        truth = truth_for(slug)
        if not truth:
            continue
        claims = page_claims(slug)

        for key, expected in truth.items():
            if expected is None:
                continue
            for claimed, pages in (claims.get(key) or {}).items():
                checked += 1
                if claimed != expected:
                    findings.append({
                        "slug": slug, "key": key, "claimed": claimed,
                        "expected": expected, "pages": sorted(set(pages)),
                        "scope": "country_page",
                    })

        # config vs data regions — a data finding, not a page error
        data_n = len(root_of(slug).get("regions") or []) if root_of(slug) else None
        cfg_n = config_regions(slug)
        if cfg_n is not None and data_n is not None and cfg_n != data_n:
            findings.append({
                "slug": slug, "key": "regions: config vs data",
                "claimed": cfg_n, "expected": data_n,
                "pages": ["intelligence/country-configs/%s.json" % slug],
                "scope": "data_tier",
            })

        if slug in landing:
            checked += 1
            if landing[slug] != truth["fleet.total"]:
                findings.append({
                    "slug": slug, "key": "index.html data-subs",
                    "claimed": landing[slug], "expected": truth["fleet.total"],
                    "pages": ["index.html (root)"], "scope": "landing_page",
                })

    by_country: dict[str, int] = {}
    for f in findings:
        by_country[f["slug"]] = by_country.get(f["slug"], 0) + 1

    print(f"Page/data agreement — {len(slugs)} countries, {checked:,} published figures\n")
    if findings:
        print(f"{'country':<14}{'figure':<28}{'page says':>12}{'data says':>12}")
        print("-" * 68)
        for f in sorted(findings, key=lambda x: (x["slug"], x["key"])):
            print(f"{f['slug']:<14}{f['key']:<28}"
                  f"{f['claimed'] if f['claimed'] is not None else '(blank)':>12}"
                  f"{f['expected']:>12,}")
        print("-" * 68)

    print(f"\n  {len(findings)} disagreements across {len(by_country)} countries")
    if not findings:
        print("  every published figure matches its source.")
    else:
        worst = sorted(by_country.items(), key=lambda kv: -kv[1])[:5]
        print("  most affected: " + ", ".join(f"{s} ({n})" for s, n in worst))

    if args.json:
        Path(args.json).write_text(json.dumps(
            {"checked": checked, "findings": findings}, indent=1))
        print(f"  report -> {args.json}")

    gating = [f for f in findings if f["scope"] != "data_tier"]
    declared = len(findings) - len(gating)
    if args.strict:
        if declared:
            print(f"\n  {declared} declared data-tier findings reported, not gating.")
        if gating:
            print(f"STRICT: {len(gating)} page figures disagree with their source "
                  f"-> exit 1")
            return 1
        print("STRICT: every published figure matches its source.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
