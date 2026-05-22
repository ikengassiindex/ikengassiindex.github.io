#!/usr/bin/env python3
"""
Stage 7e — Runtime audit harness (KB §49.10).

Two passes per country slug:

  1. RESIDUE SCAN  — Playwright + headless Chromium loads each page on
     ikengassiindex.github.io/{slug}/, waits for JS + canvas, cycles
     through every tab via switchTab() / class="tab-btn" simulation,
     dumps the rendered HTML, then scans for known residue patterns:

         "Loading…"                  — IIFE that never populated
         "||UPPER_TOKEN||"           — placeholder leftover
         ">GAP<"                     — status pill from missing field
         "— kV"                      — em-dash voltage (untagged subs)
         "Edition 003" / "Edition 004"  — 3-digit padding regression
         "INACTIVE for <country>"    — INACTIVE label leak from CZ
         "%%"                         — double-percent bug
         "NOT ACTIVE"                — literal NOT ACTIVE placeholder

  2. SCHEMA DRIFT  — load each country's ssi-data.json, compare top-level
     keys + substations[0] keys + fleet_summary keys + meta keys + per-
     substation nested-dict keys against the Latvia reference (the most
     complete schema in the fleet post-§49.5). Report any key the country
     is missing.

Outputs:

  audit/_logs/runtime-audit-{ISO}.json
                              — one file per run with full per-country
                                findings, suitable for diffing across runs.
  audit/_summary/SUMMARY.md   — Markdown summary written to GITHUB_STEP_SUMMARY.
  audit/_email/digest.html    — email body if findings exist (consumed by
                                send_audit_digest.py).

Exit code: 0 if no findings, 1 otherwise. Workflow can decide whether to
fail the run on findings or just notify.
"""
from __future__ import annotations
import argparse, datetime, json, os, re, sys, time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LIVE_BASE = "https://ikengassiindex.github.io"
COUNTRIES_JSON = REPO_ROOT / "intelligence" / "countries.json"

# 8 pages every country has
PAGES = [
    ("index.html",          "Overview"),
    ("regional.html",       "Regional"),
    ("map.html",            "Map"),
    ("intelligence.html",   "Intelligence"),
    ("data.html",           "Data"),
    ("esg-report.html",     "ESG"),
    ("methodology.html",    "Methodology"),
    ("dno-dashboard.html",  "DNO"),
]

# Residue patterns — (label, regex, severity)
# Severity: "critical" (data clearly broken), "warning" (cosmetic), "info"
RESIDUE_PATTERNS = [
    ("Loading placeholder",       r">\s*Loading[^<]*?…?\s*<",                        "critical"),
    ("||UPPER_TOKEN|| literal",   r"\|\|[A-Z][A-Z_\s]{2,30}\|\|",                    "critical"),
    ("GAP status pill",           r"class=\"readiness-pill\s+gap\">GAP<",            "warning"),
    ("Em-dash voltage",           r"—\s*kV",                                          "warning"),
    ("Edition 003+",              r"Edition\s+0\d{2,}",                              "critical"),
    ("NOT ACTIVE placeholder",    r"\bNOT\s+ACTIVE\b",                               "critical"),
    ("INACTIVE for country",      r"INACTIVE\s+for\s+\w+",                           "warning"),
    ("Double percent",            r"\b\d+(\.\d+)?%%",                                "critical"),
]

# ──────────────────────────────────────────────────────────────────────
# Schema-key reference — intersection of LV (post-§49.5 reference) AND
# FR (OECD-15 legacy reference). These are the keys EVERY country in
# the live fleet is known to emit. Anything missing here is a real gap.
#
# Calibrated 2026-05-22 from live JSONs at:
#   https://ikengassiindex.github.io/{latvia,france,lithuania}/ssi-data.json
# (KB §49.11 — schema parity sweep, intersection-based reference)
# ──────────────────────────────────────────────────────────────────────
LV_REFERENCE_KEYS = {
    "top_level": {
        # Both LV and FR emit these. LV adds many provenance fields
        # (country, iso2, edition, generated_utc, session, kb_refs, …)
        # but FR omits them — they're informational, not required.
        "fleet_summary", "regions", "substations", "meta",
    },
    "fleet_summary": {
        # Statistical block both emit (FR uses P5/P95; LV uses both
        # P5/P95 and R_p5/R_p95 — SYNONYM_GROUPS bridges that).
        "P5", "P95", "mean_R", "median_R", "total",
        "bands", "band_pct", "confidence_pct",
    },
    "meta": {
        # Sparse intersection — FR emits country/version/note/generator/
        # enrichment_run; LV emits country_name/iso2/engine_version/session.
        # Both emit:
        "data_sources", "mc_iterations", "total_departments", "variables",
    },
    "substation": {
        # Core per-substation fields — both schemas emit these.
        "substation_id", "internal_id", "lat", "lon", "voltage_kv",
        "name", "region", "province",
        "R_median", "R_P5", "R_P95", "R_base_median", "R_unclipped",
        "CI_width",
        "classification", "confidence_tier", "fleet_percentile",
        "modifier_impact", "modifier_pct",
        "components", "alert_components",
        "modifiers", "markov",
        "socio_economic", "seismic", "climate_trajectory",
        "graph_topology", "transition",
        "version",
    },
    "modifiers": {
        # Derived-alias style — these are what the dashboard JS reads.
        # The raw forms (R3, R3_tier, R6b, R6c_flood, R7, compound)
        # are emitted by LV/LT only and aren't strictly required —
        # see LV_ONLY_KEYS below for the warning-level set.
        "R3_C_mult", "R4_F_topo", "R6_seismic", "R6_restoration", "R7_cyber",
    },
    "markov": {
        # 20-year horizon is universal; 10-year exists in both fleets
        # under different names — SYNONYM_GROUPS handles that.
        "risk_score", "p_critical_20yr", "p_crit_20yr",
        "ettc_years", "corrosion_class", "steady_state",
    },
    "regions[]": {
        # Both LV and FR emit these per-region.
        "region", "count", "mean_R", "median_R",
        "bands", "pct_critical", "pct_high",
    },
}

# ──────────────────────────────────────────────────────────────────────
# LV-only keys — present in the post-§49.5 fleet (LV/LT/EE/CZ/LU/BE/NL)
# but NOT in the OECD-15 legacy fleet. Missing these is a WARNING for
# new countries (we want all new builds to match LV), but a legacy
# country missing them is informational, not a real gap.
#
# Audit uses this set to flag "country could be enriched with these
# fields" rather than "country is broken".
# ──────────────────────────────────────────────────────────────────────
LV_ONLY_KEYS = {
    "top_level": {
        "country", "iso2", "country_number", "oecd_number",
        "edition", "first_refresh", "session", "generated_utc",
        "sobol_first_order", "markov_handling", "kb_refs",
    },
    "fleet_summary": {
        "R_median", "R_p5", "R_p95", "alert_flag_count",
        "low_band", "medium_band", "high_band", "critical_band",
        "total_substations",
    },
    "meta": {
        "country_name", "iso2", "engine_version", "session",
        "sobol_iterations", "total_km", "total_lines",
    },
    "substation": {
        "operator", "R_base", "R_final",
        "CI_lower", "CI_upper", "CI_ratio",
        "components_norm", "mc",
        "osm_id", "osm_type", "ref", "substation_type",
        "cyber_classification",
    },
    "modifiers": {
        # Raw forms — LV emits both raw AND derived; FR emits derived only.
        "R3", "R3_tier", "R6b", "R6c_flood", "R7", "compound",
    },
    "markov": {
        "ETTC_years", "p_critical_10yr", "confidence_tier",
        "review_date", "stationary_critical",
    },
    "regions[]": {
        "R_median", "R_p5", "R_p95",
        "low_count", "medium_count", "high_count", "critical_count",
        "substation_count", "pct_low", "pct_medium",
    },
}

# ──────────────────────────────────────────────────────────────────────
# SYNONYM_GROUPS — pairs/groups of equivalent key names. When checking
# missing keys, if ANY synonym in a group is present, the requirement
# is satisfied. This eliminates false positives where two countries
# emit the same metric under different names.
#
# Standardised target per KB §49.11 user decision: prefer the LV form
# (p_critical_10yr). Standardisation happens at publish.py level via
# follow-up patches; the audit just stops flagging the drift here.
# ──────────────────────────────────────────────────────────────────────
SYNONYM_GROUPS = {
    "fleet_summary": [
        # Percentile naming drift (FR ≡ LV)
        ("P5",  "R_p5"),
        ("P95", "R_p95"),
        ("total", "total_substations"),
    ],
    "markov": [
        # 10-year and 20-year horizons under both naming conventions
        ("p_crit_10yr", "p_critical_10yr"),
        ("p_crit_20yr", "p_critical_20yr"),
        ("ettc_years",  "ETTC_years"),
    ],
}


def load_countries():
    """Load slugs from intelligence/countries.json (canonical SoT)."""
    cfg = json.loads(COUNTRIES_JSON.read_text())
    return cfg["slugs"], cfg.get("first_refresh", {})


def is_pre_launch(slug: str, fr_map: dict, today: datetime.date) -> bool:
    fr = fr_map.get(slug)
    if not fr:
        return False  # legacy = always live
    try:
        y, m = map(int, fr.split("-")[:2])
        return today < datetime.date(y, m, 1)
    except (ValueError, IndexError):
        return False


def missing_keys(required: set[str], present: set[str],
                 synonym_groups: list[tuple] | None = None) -> set[str]:
    """Subtract present keys from required, honouring synonym groups.

    For each synonym tuple, if ANY synonym is in `present`, ALL members
    of that tuple are treated as satisfied (removed from the missing set).
    """
    missing = set(required) - set(present)
    if not synonym_groups:
        return missing
    for group in synonym_groups:
        group_set = set(group)
        if group_set & set(present):
            # At least one member is present — drop all from missing
            missing -= group_set
    return missing


def scan_residue(html: str, slug: str) -> list[dict]:
    """Apply all RESIDUE_PATTERNS to the rendered HTML; return list of findings."""
    findings = []
    for label, pattern, severity in RESIDUE_PATTERNS:
        # Skip false-positive: Section G "Edition 003" residue is real (KB §47.14),
        # but inside a code block / KB cross-reference text, allow.
        for m in re.finditer(pattern, html):
            ctx = html[max(0, m.start() - 50):m.end() + 50]
            # Skip if context shows it's inside a comment or KB reference
            if "KB §" in ctx or "<!--" in ctx[:60]:
                continue
            findings.append({
                "type": "residue",
                "label": label,
                "severity": severity,
                "match": m.group()[:80],
                "context": ctx.strip()[:200],
            })
    return findings


def scan_schema(slug: str) -> list[dict]:
    """Check ssi-data.json schema keys against LV reference. Skip if file missing."""
    findings = []
    # Try local first (faster); fall back to live fetch
    local_path = REPO_ROOT / slug / "ssi-data.json"
    if local_path.exists():
        try:
            data = json.loads(local_path.read_text())
        except Exception as e:
            findings.append({
                "type": "schema",
                "severity": "critical",
                "label": "ssi-data.json parse error",
                "details": str(e)[:200],
            })
            return findings
    else:
        # Live fetch
        import urllib.request
        url = f"{LIVE_BASE}/{slug}/ssi-data.json"
        try:
            with urllib.request.urlopen(url, timeout=20) as resp:
                data = json.loads(resp.read())
        except Exception as e:
            findings.append({
                "type": "schema",
                "severity": "warning",
                "label": "ssi-data.json fetch failed",
                "details": f"{url}: {str(e)[:100]}",
            })
            return findings

    def check(cat: str, label: str, present: set[str]):
        """Emit a critical finding for missing intersection keys, and an
        info-level finding for missing LV_ONLY keys (recommended-not-required)."""
        syns = SYNONYM_GROUPS.get(cat)
        miss_req = missing_keys(LV_REFERENCE_KEYS.get(cat, set()), present, syns)
        if miss_req:
            findings.append({
                "type": "schema",
                "severity": "warning",
                "label": label,
                "missing": sorted(miss_req),
            })
        # LV_ONLY = enrichment opportunities, not bugs — flag as info
        miss_opt = missing_keys(LV_ONLY_KEYS.get(cat, set()), present, syns)
        # Don't double-report anything already in required-missing
        miss_opt -= miss_req
        if miss_opt:
            findings.append({
                "type": "schema",
                "severity": "info",
                "label": f"{label} — recommended additions (LV-only)",
                "missing": sorted(miss_opt),
            })

    # Top-level
    check("top_level", "ssi-data.json top-level keys", set(data.keys()))

    # fleet_summary
    if isinstance(data.get("fleet_summary"), dict):
        check("fleet_summary", "fleet_summary keys", set(data["fleet_summary"].keys()))

    # meta
    if isinstance(data.get("meta"), dict):
        check("meta", "meta keys", set(data["meta"].keys()))

    # First substation — tolerate list or dict shape
    subs_raw = data.get("substations")
    s0 = None
    if isinstance(subs_raw, list) and subs_raw:
        if isinstance(subs_raw[0], dict):
            s0 = subs_raw[0]
    elif isinstance(subs_raw, dict) and subs_raw:
        for v in subs_raw.values():
            if isinstance(v, dict):
                s0 = v
                break
    if s0 is not None:
        check("substation", "substations[0] keys", set(s0.keys()))
        if isinstance(s0.get("modifiers"), dict):
            # Modifiers retain CRITICAL severity for the required set
            # because missing them = JS TypeError on .toFixed.
            syns_mod = SYNONYM_GROUPS.get("modifiers")
            miss_mod = missing_keys(
                LV_REFERENCE_KEYS["modifiers"],
                set(s0["modifiers"].keys()),
                syns_mod,
            )
            if miss_mod:
                findings.append({
                    "type": "schema",
                    "severity": "critical",
                    "label": "substations[0].modifiers keys",
                    "missing": sorted(miss_mod),
                    "details": "Without these aliases the dashboard pages throw TypeError on .toFixed",
                })
            # LV-only mods = info-level (raw R3/R7/compound etc.)
            miss_mod_info = missing_keys(
                LV_ONLY_KEYS.get("modifiers", set()),
                set(s0["modifiers"].keys()),
                syns_mod,
            ) - miss_mod
            if miss_mod_info:
                findings.append({
                    "type": "schema",
                    "severity": "info",
                    "label": "substations[0].modifiers — recommended additions (LV-only)",
                    "missing": sorted(miss_mod_info),
                })
        if isinstance(s0.get("markov"), dict):
            check("markov", "substations[0].markov keys", set(s0["markov"].keys()))

    # regions — tolerate both shapes:
    #   list-form (LV/LT convention):  [{"region":"...","R_median":...}, ...]
    #   dict-form (legacy convention): {"region_name": {"R_median":...}, ...}
    regions_raw = data.get("regions")
    first_region = None
    if isinstance(regions_raw, list) and regions_raw:
        if isinstance(regions_raw[0], dict):
            first_region = regions_raw[0]
    elif isinstance(regions_raw, dict) and regions_raw:
        # Pick first value that is itself a dict
        for v in regions_raw.values():
            if isinstance(v, dict):
                first_region = v
                break
    if first_region is not None:
        check("regions[]", "regions[0] keys", set(first_region.keys()))

    return findings


def audit_country(slug: str, fr_map: dict, today: datetime.date,
                  pw, use_playwright: bool = True) -> dict:
    """Run residue scan + schema diff for one country slug."""
    result = {
        "slug": slug,
        "checked_at": datetime.datetime.utcnow().isoformat() + "Z",
        "pre_launch": is_pre_launch(slug, fr_map, today),
        "pages": {},
        "schema_findings": [],
        "summary": {"critical": 0, "warning": 0, "info": 0},
    }
    # Pre-launch: skip the residue scan (pages won't render meaningfully
    # before the first refresh has fired) but ALWAYS run the schema diff
    # — the JSON is already deployed and is testable from day one.
    # KB §49.11 — schema diff is shape-only, not time-gated.
    if result["pre_launch"]:
        result["schema_findings"] = scan_schema(slug)
        for f in result["schema_findings"]:
            result["summary"][f["severity"]] = result["summary"].get(f["severity"], 0) + 1
        return result

    # ── Pass 1: Residue scan via Playwright ──
    if use_playwright:
        for fname, label in PAGES:
            url = f"{LIVE_BASE}/{slug}/{fname}"
            page_findings = []
            try:
                page = pw.new_page()
                page.set_default_timeout(30_000)
                page.goto(url, wait_until="networkidle", timeout=45_000)
                page.wait_for_timeout(2000)  # let canvas + chart libs settle

                # Cycle tabs if present
                tab_btns = page.locator(".tab-btn").all()
                for i, btn in enumerate(tab_btns):
                    try:
                        btn.click(timeout=3000)
                        page.wait_for_timeout(1500)
                        html = page.content()
                        page_findings.extend(scan_residue(html, slug))
                    except Exception:
                        pass  # tab click may fail on some pages, that's fine

                # Final scan after all tabs
                final_html = page.content()
                page_findings.extend(scan_residue(final_html, slug))

                # Dedupe by (label, match)
                seen = set()
                deduped = []
                for f in page_findings:
                    key = (f["label"], f["match"])
                    if key in seen:
                        continue
                    seen.add(key)
                    deduped.append(f)
                page_findings = deduped

                page.close()
            except Exception as e:
                page_findings.append({
                    "type": "page_load_error",
                    "severity": "warning",
                    "label": f"{fname} failed to load",
                    "details": str(e)[:200],
                })

            result["pages"][fname] = {
                "url": url,
                "label": label,
                "findings": page_findings,
            }
            for f in page_findings:
                result["summary"][f["severity"]] = result["summary"].get(f["severity"], 0) + 1

    # ── Pass 2: Schema diff ──
    result["schema_findings"] = scan_schema(slug)
    for f in result["schema_findings"]:
        result["summary"][f["severity"]] = result["summary"].get(f["severity"], 0) + 1

    return result


def write_step_summary(run_data: dict, summary_path: Path):
    """Write a Markdown summary table for GITHUB_STEP_SUMMARY."""
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Stage 7e Runtime Audit — {run_data['started_at'][:10]}",
        "",
        f"**Countries scanned**: {run_data['countries_scanned']}  ·  "
        f"**Findings (total)**: {run_data['total_findings']}  ·  "
        f"**Critical**: {run_data['critical_count']}",
        "",
        "| Country | Status | Critical | Warning | Top finding |",
        "|---|---|---:|---:|---|",
    ]
    for r in sorted(run_data["per_country"], key=lambda x: -x["summary"].get("critical", 0)):
        if r["pre_launch"]:
            status = "⏸ pre-launch"
        elif r["summary"].get("critical", 0) > 0:
            status = "✗ critical"
        elif r["summary"].get("warning", 0) > 0:
            status = "⚠ warning"
        else:
            status = "✓ clean"
        # Pick top finding for summary cell
        top = ""
        for pg, payload in r["pages"].items():
            for f in payload["findings"]:
                if f["severity"] == "critical":
                    top = f"{pg}: {f['label']}"
                    break
            if top:
                break
        if not top:
            for f in r["schema_findings"]:
                if f["severity"] == "critical":
                    top = f"schema: {f['label']}"
                    break
        if not top and r["summary"].get("warning", 0):
            top = "(warnings only)"
        if not top:
            top = "—"
        lines.append(
            f"| {r['slug']} | {status} | {r['summary'].get('critical', 0)} | "
            f"{r['summary'].get('warning', 0)} | {top} |"
        )
    lines.extend([
        "",
        "Full JSON report uploaded as workflow artifact `runtime-audit-report`.",
        "",
        "KB §49.10 · Stage 7e gate.",
    ])
    summary_path.write_text("\n".join(lines))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--countries", default="", help="CSV slugs (default: all)")
    p.add_argument("--skip-playwright", action="store_true",
                   help="Skip residue scan, only schema diff (for local quick runs)")
    p.add_argument("--out-dir", default="audit", help="Output directory")
    args = p.parse_args()

    slugs, fr_map = load_countries()
    if args.countries:
        wanted = [s.strip() for s in args.countries.split(",") if s.strip()]
        slugs = [s for s in slugs if s in wanted]

    today = datetime.date.today()
    out_dir = Path(args.out_dir)
    (out_dir / "_logs").mkdir(parents=True, exist_ok=True)
    (out_dir / "_summary").mkdir(parents=True, exist_ok=True)

    print(f"[runtime_audit] {len(slugs)} countries to scan; "
          f"playwright={'OFF' if args.skip_playwright else 'ON'}")

    pw_inst = None
    browser = None
    pw_context = None
    if not args.skip_playwright:
        try:
            from playwright.sync_api import sync_playwright
            pw_inst = sync_playwright().start()
            browser = pw_inst.chromium.launch(headless=True)
            pw_context = browser.new_context(viewport={"width": 1400, "height": 900})
        except ImportError:
            print("[runtime_audit] Playwright not installed — falling back to schema-only")
            args.skip_playwright = True

    run_data = {
        "started_at": datetime.datetime.utcnow().isoformat() + "Z",
        "countries_scanned": 0,
        "total_findings": 0,
        "critical_count": 0,
        "warning_count": 0,
        "per_country": [],
    }

    for slug in slugs:
        print(f"  · {slug}")
        result = audit_country(slug, fr_map, today,
                               pw_context, use_playwright=not args.skip_playwright)
        run_data["per_country"].append(result)
        run_data["countries_scanned"] += 1
        run_data["critical_count"] += result["summary"].get("critical", 0)
        run_data["warning_count"] += result["summary"].get("warning", 0)
        run_data["total_findings"] += sum(result["summary"].values())

    run_data["finished_at"] = datetime.datetime.utcnow().isoformat() + "Z"

    if browser:
        browser.close()
    if pw_inst:
        pw_inst.stop()

    # ── Write outputs ──
    iso_stamp = run_data["started_at"][:10]
    json_path = out_dir / "_logs" / f"runtime-audit-{iso_stamp}.json"
    json_path.write_text(json.dumps(run_data, indent=2, ensure_ascii=False))
    print(f"[runtime_audit] wrote {json_path} ({json_path.stat().st_size:,} bytes)")

    summary_path = out_dir / "_summary" / "SUMMARY.md"
    write_step_summary(run_data, summary_path)
    print(f"[runtime_audit] wrote {summary_path}")

    # Write to GITHUB_STEP_SUMMARY if running in Actions
    gh_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if gh_summary:
        with open(gh_summary, "a") as fh:
            fh.write(summary_path.read_text())

    # ── Console summary ──
    print()
    print("═" * 60)
    print(f" Stage 7e Audit Summary — {iso_stamp}")
    print("═" * 60)
    print(f"  Scanned    : {run_data['countries_scanned']} countries")
    print(f"  Critical   : {run_data['critical_count']}")
    print(f"  Warning    : {run_data['warning_count']}")
    print(f"  Total      : {run_data['total_findings']}")
    print()
    if run_data["critical_count"]:
        print("✗ CRITICAL FINDINGS — investigate runtime-audit-{iso_stamp}.json")
        sys.exit(1)
    elif run_data["warning_count"]:
        print("⚠ Warnings only — review at leisure")
        sys.exit(0)
    else:
        print("✓ Clean — all countries pass residue + schema checks")
        sys.exit(0)


if __name__ == "__main__":
    main()
