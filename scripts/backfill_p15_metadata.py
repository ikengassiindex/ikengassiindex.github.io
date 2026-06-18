#!/usr/bin/env python3
"""
P15-B3 — Backfill Phase 1.5 data sources into per-country ssi-metadata.js files.

Updates each of the 40 country-level ssi-metadata.js files to reflect:
  1. CDS entry: 0.25° (~25 km) → 0.1° (~11 km, ERA5-Land + daily stats),
                vars 4 → 6 (added heat_days, ice_days from daily-stats),
                freq Static → Annual
  2. New GEM entry (P15-B-2): GEM 2023.1 Global Seismic Hazard Map,
                              0.05° (~5.5 km) raster, CC BY-NC-SA 4.0
  3. New Eurostat-NUTS3 entry (P15-F-1) for 20 EU countries
  4. New per-country agency entry (P15-F-2) for 16 non-EU SoT countries
  5. Header comment "N sources" count updated to reflect additions

Pure-Python regex patcher; no JS parser dependency. Run from repo root:
    python3 scripts/backfill_p15_metadata.py

Use --dry-run to see what would change without modifying files.
Use --verbose to show per-country diff summary.
"""
import argparse
import re
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOT_PATH = REPO_ROOT / "intelligence" / "countries.json"


# ═══════════════════════════════════════════════════════════
#  New + updated DATA_SOURCES entries
# ═══════════════════════════════════════════════════════════

# Updated CDS entry (P15-A-2 + P15-A-3)
CDS_UPDATED = {
    "id": "CDS",
    "name": "Copernicus CDS / ERA5-Land",
    "url": "cds.climate.copernicus.eu",
    "freq": "Annual",
    "res": "0.1° (~11 km, ERA5-Land + daily-stats)",
    "vars": 5,
    "category": "Climate",
    "feeds": "R2 Δ_climate (t_mean_c, heat_days, ice_days at 0.1° land grid)",
    "registration": True,
}

# New GEM entry (P15-B-2)
GEM_NEW = {
    "id": "GEM",
    "name": "GEM Global Seismic Hazard Map 2023.1",
    "url": "globalquakemodel.org",
    "freq": "Static",
    "res": "0.05° (~5.5 km, rock-site PGA 475-yr)",
    "vars": 1,
    "category": "Hazard",
    "feeds": "R6a seismic PGA, substation-level overlay (CC BY-NC-SA 4.0)",
    "registration": False,
}

# Eurostat NUTS-3 entry (P15-F-1) — for the 20 EU SoT countries
EUROSTAT_NUTS3 = {
    "id": "Eurostat-NUTS3",
    "name": "Eurostat NUTS-3 Regional Statistics",
    "url": "ec.europa.eu/eurostat",
    "freq": "Annual",
    "res": "NUTS-3 (province / NUTS-2 unemployment)",
    "vars": 5,
    "category": "Socio-Econ",
    "feeds": "R2 GDP/cap, unemp, elderly%, ep_rate, migration (CC BY 4.0)",
    "registration": False,
}

# Per-country non-EU agency entries (P15-F-2)
# Maps SoT slug → DATA_SOURCES entry
NON_EU_AGENCY_ENTRIES = {
    "us": {
        "id": "Census-ACS",
        "name": "US Census Bureau ACS 5-year",
        "url": "api.census.gov",
        "freq": "Annual",
        "res": "State / tract",
        "vars": 5,
        "category": "Socio-Econ",
        "feeds": "R2 per-state GDP-proxy, unemp, elderly% (US Govt public domain)",
        "registration": True,
    },
    "uk": {
        "id": "ONS-Regional",
        "name": "ONS Regional Accounts + Nomis",
        "url": "ons.gov.uk + nomisweb.co.uk",
        "freq": "Annual",
        "res": "12 NUTS-1 regions",
        "vars": 5,
        "category": "Socio-Econ",
        "feeds": "R2 per-region GVA/cap, unemp, elderly% (Open Govt Licence v3.0)",
        "registration": False,
    },
    "norway": {
        "id": "SSB",
        "name": "SSB Regional Accounts",
        "url": "ssb.no",
        "freq": "Annual",
        "res": "15 fylker",
        "vars": 5,
        "category": "Socio-Econ",
        "feeds": "R2 per-fylke GRP/cap, unemp, elderly% (CC BY 4.0)",
        "registration": False,
    },
    "new-zealand": {
        "id": "StatsNZ",
        "name": "Stats NZ Regional GDP + HLFS + SPE",
        "url": "stats.govt.nz",
        "freq": "Annual",
        "res": "16 Regional Councils",
        "vars": 5,
        "category": "Socio-Econ",
        "feeds": "R2 per-region GDP/cap, unemp, elderly% (CC BY 4.0)",
        "registration": False,
    },
    "australia": {
        "id": "ABS",
        "name": "ABS National + Labour Force + Pop Estimates",
        "url": "abs.gov.au",
        "freq": "Annual",
        "res": "8 states / territories",
        "vars": 5,
        "category": "Socio-Econ",
        "feeds": "R2 GSP/cap, unemp, elderly% (CC BY 4.0)",
        "registration": False,
    },
    "japan": {
        "id": "eStat-CabinetOffice",
        "name": "Cabinet Office Prefectural Accounts + MIC LFS",
        "url": "esri.cao.go.jp + stat.go.jp",
        "freq": "Annual",
        "res": "47 prefectures",
        "vars": 5,
        "category": "Socio-Econ",
        "feeds": "R2 per-prefecture GDP/cap, unemp, elderly% (Open Data)",
        "registration": True,
    },
    "canada": {
        "id": "StatCan",
        "name": "StatCan Provincial Accounts + LFS",
        "url": "statcan.gc.ca",
        "freq": "Annual",
        "res": "13 provinces / territories",
        "vars": 5,
        "category": "Socio-Econ",
        "feeds": "R2 per-province GDP/cap, unemp, elderly% (Open Govt Licence — Canada)",
        "registration": False,
    },
    "korea": {
        "id": "KOSIS",
        "name": "KOSIS Regional Income GRDP",
        "url": "kosis.kr",
        "freq": "Annual",
        "res": "17 sido",
        "vars": 5,
        "category": "Socio-Econ",
        "feeds": "R2 per-sido GRDP/cap, unemp, elderly% (Open Data)",
        "registration": False,
    },
    "switzerland": {
        "id": "BFS",
        "name": "BFS Kantonale Volkswirtschaftliche Gesamtrechnung",
        "url": "bfs.admin.ch",
        "freq": "Annual",
        "res": "26 cantons",
        "vars": 5,
        "category": "Socio-Econ",
        "feeds": "R2 per-canton GDP/cap, unemp, elderly% (Open Data)",
        "registration": False,
    },
    "turkey": {
        "id": "TUIK",
        "name": "TÜİK Provincial GDP + HLFS",
        "url": "tuik.gov.tr",
        "freq": "Annual",
        "res": "15 detailed provinces + national-mean",
        "vars": 5,
        "category": "Socio-Econ",
        "feeds": "R2 per-province GDP/cap, unemp, elderly% (Open Data)",
        "registration": False,
    },
    "chile": {
        "id": "BCCh-INE",
        "name": "Banco Central CCNR + INE ENE",
        "url": "bcentral.cl + ine.cl",
        "freq": "Annual",
        "res": "16 regiones",
        "vars": 5,
        "category": "Socio-Econ",
        "feeds": "R2 per-región GDP/cap, unemp, elderly% (Open Data)",
        "registration": False,
    },
    "iceland": {
        "id": "Hagstofa",
        "name": "Hagstofa Þjóðhagsreikningar + VMS",
        "url": "hagstofa.is",
        "freq": "Annual",
        "res": "8 regions",
        "vars": 5,
        "category": "Socio-Econ",
        "feeds": "R2 per-region GDP/cap, unemp, elderly%",
        "registration": False,
    },
    "colombia": {
        "id": "DANE",
        "name": "DANE Cuentas Nacionales Departamentales",
        "url": "dane.gov.co",
        "freq": "Annual",
        "res": "33 departamentos",
        "vars": 5,
        "category": "Socio-Econ",
        "feeds": "R2 per-departamento GDP/cap, unemp, elderly% (Open Data)",
        "registration": False,
    },
    "israel": {
        "id": "CBS-IL",
        "name": "CBS Statistical Abstract + LFS",
        "url": "cbs.gov.il",
        "freq": "Annual",
        "res": "7 districts",
        "vars": 5,
        "category": "Socio-Econ",
        "feeds": "R2 per-district GDP/cap, unemp, elderly%",
        "registration": False,
    },
    "costa-rica": {
        "id": "BCCR-INEC",
        "name": "BCCR Cuentas Nacionales + INEC ECE",
        "url": "bccr.fi.cr + inec.cr",
        "freq": "Annual",
        "res": "7 provincias",
        "vars": 5,
        "category": "Socio-Econ",
        "feeds": "R2 per-provincia GDP/cap, unemp, elderly% (Open Data)",
        "registration": False,
    },
    "greenland": {
        "id": "StatGreenland",
        "name": "Statistics Greenland National Accounts + LFS",
        "url": "stat.gl",
        "freq": "Annual",
        "res": "5 kommuner",
        "vars": 5,
        "category": "Socio-Econ",
        "feeds": "R2 per-kommune GDP/cap, unemp, elderly%",
        "registration": False,
    },
}

# Eurostat NUTS-3 countries (20 EU SoT)
EUROSTAT_COUNTRIES = {
    "belgium", "czechia", "denmark", "estonia", "finland", "france",
    "germany", "hungary", "ireland", "latvia", "lithuania", "luxembourg",
    "netherlands", "poland", "portugal", "slovakia", "slovenia", "spain",
    "sweden", "austria",
}

# Italy + Greece + Mexico already have native CSVs (no Eurostat/agency overlay needed for socio)
NATIVE_SOCIO_COUNTRIES = {"italy", "greece", "mexico"}


# ═══════════════════════════════════════════════════════════
#  JS-line formatter — match the existing column alignment
# ═══════════════════════════════════════════════════════════

def format_entry_js(entry, base_indent="    "):
    """Format a Python dict as a one-line JS object literal,
    aligning with the existing file's columnar style.
    """
    # Build key:value pairs with consistent quoting
    parts = []
    # ensure_ascii=False preserves degree symbols, delta, accented chars,
    # CJK etc. as literal UTF-8 (much more readable in JS source than
    # \uXXXX escapes). All target files are UTF-8 by default.
    def jq(s):
        return json.dumps(s, ensure_ascii=False)
    parts.append(f"id: {jq(entry['id'])}")
    parts.append(f"name: {jq(entry['name'])}")
    parts.append(f"url: {jq(entry['url'])}")
    parts.append(f"freq: {jq(entry['freq'])}")
    parts.append(f"res: {jq(entry['res'])}")
    parts.append(f"vars: {entry['vars']}")
    parts.append(f"category: {jq(entry['category'])}")
    parts.append(f"feeds: {jq(entry['feeds'])}")
    if entry.get("registration"):
        parts.append(f"registration: true")
    body = ", ".join(parts)
    return f"{base_indent}{{ {body} }}"


# ═══════════════════════════════════════════════════════════
#  Per-file patcher
# ═══════════════════════════════════════════════════════════

def patch_metadata_file(path, country_slug, dry_run=False, verbose=False):
    """Apply P15 updates to a single ssi-metadata.js file.

    Returns: dict with diff summary {country, cds_updated, gem_added, eurostat_added, agency_added}
    """
    text = path.read_text()
    original = text
    diff = {
        "country": country_slug,
        "cds_updated": False,
        "gem_added": False,
        "eurostat_added": False,
        "agency_added": False,
    }

    # ── 1. Update Copernicus/CDS entry ──
    # Match the whole single-line entry containing the universal CDS URL.
    # Works for both structures: `id: 'CDS'` (US/Belgium-style) and
    # `id:"COPERNICUS"` / `id:"COPER"` (Norway/Australia-style).
    cds_line_pattern = re.compile(
        r"^(\s*)\{[^}\n]*cds\.climate\.copernicus\.eu[^}\n]*\}[,]?\s*$",
        re.MULTILINE,
    )
    cds_match = cds_line_pattern.search(text)
    if cds_match:
        indent = cds_match.group(1)
        new_line = format_entry_js(CDS_UPDATED, base_indent=indent) + ","
        text = text[:cds_match.start()] + new_line + text[cds_match.end():]
        diff["cds_updated"] = True

    # ── Helper: find the closing of DATA_SOURCES array ──
    # In Structure A: `];` (const declaration), in Structure B: `],` (object property)
    def find_data_sources_closing(s):
        # Look for the closing of the DATA_SOURCES array specifically.
        # Strategy: find "DATA_SOURCES" keyword, then find the next ]; or ],
        # at the start of a line (column aligned).
        ds_start = re.search(r"DATA_SOURCES\s*[:=]\s*\[", s)
        if not ds_start:
            return None
        # Now scan from there for a matching ] at start of line
        closing = re.search(r"^(\s*)\][,;]", s[ds_start.end():], re.MULTILINE)
        if closing:
            absolute_start = ds_start.end() + closing.start()
            return absolute_start
        return None

    # ── Helper: ensure the entry immediately before `pos` has a trailing comma ──
    # JS requires commas between array elements. Many hand-curated ssi-metadata.js
    # files omit the trailing comma on the LAST entry (which is fine when nothing
    # follows). When we insert a new entry, we need to add a comma to the
    # previous entry's closing `}` if it doesn't already have one.
    def ensure_trailing_comma_before(s, pos):
        # Walk backwards from pos to find the last non-whitespace char
        i = pos - 1
        while i >= 0 and s[i] in " \t\n\r":
            i -= 1
        if i >= 0 and s[i] == '}':
            # Last char is `}` with no trailing comma — insert one
            return s[:i + 1] + ',' + s[i + 1:]
        return s

    # ── 2. Add GEM entry if missing ──
    if not re.search(r"id\s*:\s*['\"]GEM['\"]", text):
        closing_pos = find_data_sources_closing(text)
        if closing_pos is not None:
            text = ensure_trailing_comma_before(text, closing_pos)
            # After ensure, length may have grown by 1; re-find closing
            closing_pos = find_data_sources_closing(text)
            indent = "    "
            gem_line = format_entry_js(GEM_NEW, base_indent=indent) + ","
            text = text[:closing_pos] + gem_line + "\n" + text[closing_pos:]
            diff["gem_added"] = True

    # ── 3. Add Eurostat-NUTS3 entry for EU countries ──
    if country_slug in EUROSTAT_COUNTRIES and not re.search(r"id\s*:\s*['\"]Eurostat-NUTS3['\"]", text):
        closing_pos = find_data_sources_closing(text)
        if closing_pos is not None:
            text = ensure_trailing_comma_before(text, closing_pos)
            closing_pos = find_data_sources_closing(text)
            indent = "    "
            es_line = format_entry_js(EUROSTAT_NUTS3, base_indent=indent) + ","
            text = text[:closing_pos] + es_line + "\n" + text[closing_pos:]
            diff["eurostat_added"] = True

    # ── 4. Add non-EU per-agency entry ──
    agency = NON_EU_AGENCY_ENTRIES.get(country_slug)
    if agency and not re.search(rf"id\s*:\s*['\"]{re.escape(agency['id'])}['\"]", text):
        closing_pos = find_data_sources_closing(text)
        if closing_pos is not None:
            text = ensure_trailing_comma_before(text, closing_pos)
            closing_pos = find_data_sources_closing(text)
            indent = "    "
            ag_line = format_entry_js(agency, base_indent=indent) + ","
            text = text[:closing_pos] + ag_line + "\n" + text[closing_pos:]
            diff["agency_added"] = True

    # ── 5. Update header source count ──
    # Count current entries (rough estimate: count `id:` occurrences in DATA_SOURCES block)
    sources_block_match = re.search(
        r"const\s+DATA_SOURCES\s*=\s*\[(.*?)\];",
        text,
        re.DOTALL,
    )
    if sources_block_match:
        block = sources_block_match.group(1)
        new_count = len(re.findall(r"id:\s*'[^']+'", block))
        # Update header count
        header_pattern = re.compile(r"(\d+)\s+variables\s*·\s*(\d+)\s+sources")
        text = header_pattern.sub(
            lambda m: f"{m.group(1)} variables · {new_count} sources",
            text,
        )

    if text != original:
        if not dry_run:
            path.write_text(text)
        if verbose:
            flags = []
            if diff["cds_updated"]: flags.append("CDS↑")
            if diff["gem_added"]: flags.append("+GEM")
            if diff["eurostat_added"]: flags.append("+Eurostat")
            if diff["agency_added"]: flags.append(f"+{agency['id']}")
            print(f"  ✓ {country_slug:14s} — {', '.join(flags) if flags else 'noop'}")
    elif verbose:
        print(f"  ☐ {country_slug:14s} — no changes")

    return diff


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="Show changes without writing")
    ap.add_argument("--verbose", action="store_true", help="Per-country diff line")
    args = ap.parse_args()

    sot_slugs = sorted(json.loads(SOT_PATH.read_text())["slugs"])
    print(f"═══ P15-B3 metadata backfill ({len(sot_slugs)} SoT countries) ═══\n")

    summary = {"cds_updated": 0, "gem_added": 0, "eurostat_added": 0, "agency_added": 0}
    missing_files = []

    for slug in sot_slugs:
        path = REPO_ROOT / slug / "ssi-metadata.js"
        if not path.exists():
            missing_files.append(slug)
            continue
        diff = patch_metadata_file(path, slug, dry_run=args.dry_run, verbose=args.verbose)
        for k in summary:
            if diff[k]:
                summary[k] += 1

    print()
    print(f"═══ Summary ═══")
    print(f"  CDS updated:          {summary['cds_updated']:>3} / {len(sot_slugs) - len(missing_files)}")
    print(f"  GEM added:            {summary['gem_added']:>3} / {len(sot_slugs) - len(missing_files)}")
    print(f"  Eurostat-NUTS3 added: {summary['eurostat_added']:>3} / {len(EUROSTAT_COUNTRIES)}")
    print(f"  Non-EU agency added:  {summary['agency_added']:>3} / {len(NON_EU_AGENCY_ENTRIES)}")
    if missing_files:
        print(f"  ⚠ Missing files for: {missing_files}")
    if args.dry_run:
        print(f"\n  (dry-run — no files modified)")


if __name__ == "__main__":
    main()
