#!/usr/bin/env python3
"""
Set every published fleet figure from its source — DRY RUN BY DEFAULT.

    python3 ssi_refresh_canonical_figures.py                 # cohort report
    python3 ssi_refresh_canonical_figures.py japan france    # named countries
    python3 ssi_refresh_canonical_figures.py --apply         # write

Nothing is written unless --apply is passed. Run from the repo root.

WHAT IT CORRECTS, AND FROM WHERE
--------------------------------
    fleet.total                 <slug>/ssi-data.json   substation count
    fleet.voltage.ehv           ssi-data              substations >= 220 kV
    fleet.voltage.hv            ssi-data              110-220 kV
    fleet.voltage.distribution  ssi-data              the remainder
    fleet.grid_lines            <slug>/grid-geo.json  line records
    fleet.n_regions             intelligence/country-configs/<slug>.json

Two forms carry these figures and both are rewritten:

    <span data-canonical="fleet.total">6,168</span>      the rendered text
    "fleet.total": "6,168"                               SSI_CANONICAL_LITERALS

WHY n_regions COMES FROM THE CONFIG, NOT THE DATA
--------------------------------------------------
len(ssi-data["regions"]) is a by-product of the spatial join. It carries a
different administrative tier on four countries — france holds 102
départements where the config declares 13 régions, japan 46 prefectures
against 10 regions, uk 244 against 12, portugal 21 against 7 — and on four
more it includes an "Unknown" bucket for substations the join could not
place (germany 17 = 16 Länder + Unknown; likewise italy, spain, sweden).

country-configs/<slug>.json::admin.l1.count declares the tier the index
intends to report at. It is country-specific and already agrees with the data
on 27 of 39. Publishing the join's by-product instead would put "France: 102"
beside "Australia: 8" — different administrative tiers presented as one
measure.

The 12 disagreements are reported, not silenced. They are a data workstream:
the Unknown buckets are a genuine gap, and the tier mismatches want a
deliberate decision.

WHY LABELS ARE NOT TOUCHED
--------------------------
admin.l1.label_plural reads "Regions" on all 39 countries — another artefact
of the Italy template. The correct labels are Prefectures, Länder, States,
Départements, Departamentos, Mehozot, Kraje. Pluralising those correctly is
per-language editorial work, and a tool that guesses would produce "Länders".
So this pass fixes numbers only and prints the label state for you to supply.

FORMATTING AND SAFETY
---------------------
Thousands separators follow the existing convention: comma-grouped at 1,000
and above, plain below. Only the VALUE inside a data-canonical span, or the
VALUE in a SSI_CANONICAL_LITERALS entry, is rewritten. No markup, styling or
layout is touched — the operating rule on this repo is that the rendering is
never modified, only what feeds it.

Verify after applying with:
    python3 check_page_data_agreement.py --all
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def _find_repo() -> Path:
    cwd = Path.cwd()
    if (cwd / "intelligence" / "countries.json").exists():
        return cwd
    here = Path(__file__).resolve().parent.parent
    if (here / "intelligence" / "countries.json").exists():
        return here
    sys.exit("ABORT: run from the ikengassiindex.github.io repo root.")


REPO = _find_repo()
EHV_KV, HV_KV = 220, 110
PAGES = ("index.html", "intelligence.html", "regional.html", "data.html",
         "esg-report.html", "methodology.html", "map.html")
DATA_KEYS = ("fleet.total", "fleet.voltage.ehv", "fleet.voltage.hv",
             "fleet.voltage.distribution", "fleet.grid_lines", "fleet.n_regions")


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
    """(declared count, declared label, needs_editorial) from the country config."""
    p = REPO / "intelligence" / "country-configs" / f"{slug}.json"
    if not p.exists():
        return None, None, False
    l1 = (json.loads(p.read_text()).get("admin") or {}).get("l1") or {}
    label = l1.get("label_en")
    messy = bool(label and ("(" in label))
    return l1.get("count"), label, messy


def truth_for(slug: str) -> dict:
    root, subs = load_country(slug)
    if root is None:
        return {}
    kv = lambda s: s.get("voltage_kv") if isinstance(s.get("voltage_kv"), (int, float)) else 0
    ehv = sum(1 for s in subs if kv(s) >= EHV_KV)
    hv = sum(1 for s in subs if HV_KV <= kv(s) < EHV_KV)
    n_cfg, _, _ = config_regions(slug)
    return {
        "fleet.total": len(subs),
        "fleet.voltage.ehv": ehv,
        "fleet.voltage.hv": hv,
        "fleet.voltage.distribution": len(subs) - ehv - hv,
        "fleet.grid_lines": count_lines(slug),
        "fleet.n_regions": n_cfg,
    }


# Digits immediately preceding the noun, inside a description. The noun
# is the anchor, so a description mentioning another number keeps it.
_META_DESC_RE = re.compile(r"([\d,]{1,})(\s+substations)")


def fmt(n: int) -> str:
    return f"{n:,}" if n >= 1000 else str(n)


def rewrite(html: str, key: str, value: int) -> tuple[str, int]:
    """Rewrite both carriers of `key`. Returns (html, replacements)."""
    v = fmt(value)
    n = 0

    def span_sub(m):
        nonlocal n
        if m.group(2) != v:
            n += 1
        return m.group(1) + v + m.group(3)

    html = re.sub(r'(data-canonical="' + re.escape(key) + r'">)([^<]*)(<)', span_sub, html)

    def lit_sub(m):
        nonlocal n
        if m.group(2) != v:
            n += 1
        return m.group(1) + v + m.group(3)

    html = re.sub(r'("' + re.escape(key) + r'":\s*")([^"]*)(")', lit_sub, html)

    # Third carrier: the meta description. Invisible on the page, visible in
    # view-source, to search engines and in every link preview. Nothing had
    # ever refreshed it, so on 29 August 2026 ten countries were still quoting
    # their first-written fleet — germany 187,714 against 108,016.
    #
    # Only fleet.total, and only the digits immediately before the word
    # "substations". The description is prose; a blanket numeric rewrite here
    # would be a licence to corrupt sentences.
    if key == "fleet.total":
        def desc_sub(m):
            nonlocal n
            inner = _META_DESC_RE.sub(
                lambda d: (v + d.group(2)) if d.group(1) != v else d.group(0),
                m.group(2))
            if inner != m.group(2):
                n += 1
            return m.group(1) + inner + m.group(3)

        html = re.sub(r'(name="description"\s+content=")([^"]*)(")', desc_sub, html)

    return html, n


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("countries", nargs="*")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    slugs = args.countries or cohort_slugs()
    total_edits = 0
    region_conflicts, label_gaps = [], []

    print(f"{'country':<13}{'pages':>6}{'edits':>7}   corrections")
    print("-" * 74)

    for slug in slugs:
        truth = truth_for(slug)
        if not truth:
            continue

        root, _ = load_country(slug)
        data_n = len(root.get("regions") or []) if isinstance(root, dict) else None
        cfg_n, label, messy = config_regions(slug)
        if cfg_n is not None and data_n is not None and cfg_n != data_n:
            region_conflicts.append((slug, cfg_n, data_n))
        if label in (None, "region") or messy:
            label_gaps.append((slug, label))

        edits, pages_touched, detail = 0, 0, []
        for page in PAGES:
            p = REPO / slug / page
            if not p.exists():
                continue
            html = original = p.read_text()
            for key in DATA_KEYS:
                v = truth.get(key)
                if v is None:
                    continue
                html, n = rewrite(html, key, v)
                if n:
                    edits += n
                    detail.append(f"{key.split('.')[-1]}")
            if html != original:
                pages_touched += 1
                if args.apply:
                    p.write_text(html)

        total_edits += edits
        if edits:
            uniq = sorted(set(detail))
            print(f"{slug:<13}{pages_touched:>6}{edits:>7}   {', '.join(uniq)}")

    print("-" * 74)
    print(f"  {total_edits} figures corrected across {len(slugs)} countries")

    if region_conflicts:
        print(f"\n  CONFIG vs DATA region counts disagree on {len(region_conflicts)} "
              f"countries — published from the config, logged here as data work:")
        for slug, c, d in region_conflicts:
            kind = "finer tier in data" if d > c * 1.5 else "likely Unknown bucket"
            print(f"     {slug:<13} config {c:>4}   data {d:>4}   ({kind})")

    if label_gaps:
        print(f"\n  admin.l1 label needs editorial input on {len(label_gaps)} countries")
        print(f"     generic 'region': "
              f"{', '.join(s for s, l in label_gaps if l == 'region')[:200]}")
        messy = [(s, l) for s, l in label_gaps if l and l != "region"]
        if messy:
            print("     parenthetical, needs a clean plural:")
            for s, l in messy[:8]:
                print(f"        {s:<13}{l[:60]}")

    if not args.apply:
        print("\n  dry run — nothing written. Add --apply to correct them.")
    else:
        print("\n  written. Verify: python3 check_page_data_agreement.py --all")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
