#!/usr/bin/env python3
"""
Option 3 — Cross-country schema parity sweep (KB §49.11).

Consumes a runtime-audit-{ISO}.json report produced by runtime_audit.py
and emits a human-readable parity report that an engineer uses as a
checklist when hand-patching each country's scoring-XX/publish.py.

This script does NOT generate git-applyable diffs. The user explicitly
asked for "clean and auditable, no quick fix" — auto-generated diffs
risk mis-casting derived aliases (e.g. R3_C_mult is a multiplier,
R3 is an integer tier; the relationship is country-specific). The
report tells the engineer WHAT is missing per country; the engineer
decides HOW each field should be derived from that country's scoring
logic, then writes the patch by hand and re-runs the pipeline.

Output layout:

    {out_dir}/
      PARITY_REPORT.md          — one big markdown table + per-country
                                  detail sections
      findings.json             — machine-readable index, one record
                                  per (country, missing_key) for later
                                  diffing against Monday's cron run
      checklist/{slug}.md       — per-country patch checklist suitable
                                  for pasting into a PR description

Invocation:

    python3 generate_parity_report.py \
        --audit ~/ssi-audit/_logs/runtime-audit-2026-05-21.json \
        --out  ~/ssi-parity-sweep/2026-05-21/

KB §49.11 (NEW) — Schema parity sweep. After Stage 7e identifies which
countries have stale or missing keys against the LV reference, every
gap MUST be closed at the scoring engine level (publish.py), not at
the JSON file (which next refresh would overwrite). The parity report
is the bridge between Stage 7e findings and per-country PRs.
"""
from __future__ import annotations
import argparse, datetime, json, os, sys
from pathlib import Path
from collections import defaultdict

# Categories from runtime_audit.py LV_REFERENCE_KEYS — keep in sync.
# The order here drives section ordering in the report.
SCHEMA_CATEGORIES = [
    ("top_level",      "Top-level ssi-data.json keys"),
    ("fleet_summary",  "fleet_summary{} keys"),
    ("meta",           "meta{} keys"),
    ("substation",     "substations[0] keys"),
    ("modifiers",      "substations[0].modifiers{} (CRITICAL — TypeError risk)"),
    ("markov",         "substations[0].markov{} keys"),
    ("regions[]",      "regions[0] keys"),
]

# Severity weights (for ranking countries by patch urgency)
SEVERITY_WEIGHT = {"critical": 10, "warning": 1, "info": 0}


def categorize_finding(f: dict) -> str | None:
    """Map a schema finding's label back to a category name."""
    label = f.get("label", "").lower()
    if "top-level" in label:
        return "top_level"
    if "fleet_summary" in label:
        return "fleet_summary"
    if label.startswith("meta keys") or " meta " in label:
        return "meta"
    if "modifiers keys" in label:
        return "modifiers"
    if "markov keys" in label:
        return "markov"
    if "regions[0]" in label or label.startswith("regions"):
        return "regions[]"
    if "substations[0]" in label:
        return "substation"
    return None


def build_country_summary(per_country: list[dict]) -> list[dict]:
    """For each country produce a compact summary: missing-key inventory."""
    summaries = []
    for c in per_country:
        if c.get("pre_launch"):
            summaries.append({
                "slug": c["slug"],
                "status": "pre_launch",
                "critical_keys": 0,
                "warning_keys": 0,
                "by_category": {},
                "patch_priority": 0,
            })
            continue

        by_cat: dict[str, dict[str, list]] = defaultdict(
            lambda: {"missing": [], "severity": "warning"}
        )
        for f in c.get("schema_findings", []):
            cat = categorize_finding(f)
            if not cat:
                continue
            missing = f.get("missing", [])
            by_cat[cat]["missing"].extend(missing)
            # critical wins over warning
            if f.get("severity") == "critical":
                by_cat[cat]["severity"] = "critical"

        # Also collect residue-page hits (informational — not a publish.py
        # patch but worth flagging in the per-country checklist)
        residue_by_page = {}
        for pg, payload in c.get("pages", {}).items():
            crit = [f for f in payload.get("findings", []) if f.get("severity") == "critical"]
            warn = [f for f in payload.get("findings", []) if f.get("severity") == "warning"]
            if crit or warn:
                residue_by_page[pg] = {
                    "critical": [f["label"] for f in crit],
                    "warning":  [f["label"] for f in warn],
                }

        crit_keys = sum(
            len(d["missing"]) for d in by_cat.values()
            if d["severity"] == "critical"
        )
        warn_keys = sum(
            len(d["missing"]) for d in by_cat.values()
            if d["severity"] == "warning"
        )
        priority = (
            crit_keys * SEVERITY_WEIGHT["critical"]
            + warn_keys * SEVERITY_WEIGHT["warning"]
        )

        summaries.append({
            "slug": c["slug"],
            "status": "ok" if (crit_keys + warn_keys == 0) else "needs_patch",
            "critical_keys": crit_keys,
            "warning_keys": warn_keys,
            "by_category": {k: dict(v) for k, v in by_cat.items()},
            "residue": residue_by_page,
            "patch_priority": priority,
        })

    summaries.sort(key=lambda s: (-s["patch_priority"], s["slug"]))
    return summaries


def render_md_report(audit_data: dict, summaries: list[dict]) -> str:
    started = audit_data.get("started_at", "")[:19].replace("T", " ")
    n = audit_data.get("countries_scanned", 0)
    crit = audit_data.get("critical_count", 0)
    warn = audit_data.get("warning_count", 0)

    needs = [s for s in summaries if s["status"] == "needs_patch"]
    clean = [s for s in summaries if s["status"] == "ok"]
    pre   = [s for s in summaries if s["status"] == "pre_launch"]

    lines = [
        "# SSI Index — Cross-Country Schema Parity Report",
        "",
        f"**Source audit**: {started} UTC · {n} countries scanned",
        f"**Findings**: {crit} critical · {warn} warning",
        "**Reference schema**: Latvia (post-§49.5, most-complete fleet)",
        "**Patch scope**: per-country `scoring-XX/publish.py` — hand-written, "
        "reviewable, single PR per country",
        "",
        "## Country status overview",
        "",
        "| Slug | Status | Critical keys | Warning keys | Priority |",
        "|---|---|---:|---:|---:|",
    ]
    for s in summaries:
        if s["status"] == "pre_launch":
            status_md = "⏸ pre-launch"
        elif s["status"] == "ok":
            status_md = "✓ schema OK"
        else:
            badge = "✗ critical" if s["critical_keys"] else "⚠ warning"
            status_md = badge
        lines.append(
            f"| {s['slug']} | {status_md} | {s['critical_keys']} | "
            f"{s['warning_keys']} | {s['patch_priority']} |"
        )

    lines += [
        "",
        f"**Summary**: {len(needs)} countries need patches · "
        f"{len(clean)} already match LV reference · {len(pre)} pre-launch (skipped).",
        "",
    ]

    if needs:
        lines += [
            "## Per-country patch checklist",
            "",
            "Each section below lists exactly what's missing from a country's "
            "`ssi-data.json` against the Latvia reference. Use as a checklist when "
            "patching that country's `scoring-XX/publish.py`. Once patched, "
            "re-run the pipeline, redeploy, and Stage 7e on the next cron run "
            "should show ✓ clean for that country.",
            "",
        ]
        for s in needs:
            lines.append(f"### `{s['slug']}` — priority {s['patch_priority']}")
            lines.append("")
            for cat_key, cat_title in SCHEMA_CATEGORIES:
                if cat_key not in s["by_category"]:
                    continue
                d = s["by_category"][cat_key]
                if not d["missing"]:
                    continue
                badge = "**CRITICAL**" if d["severity"] == "critical" else "_warning_"
                missing_list = ", ".join(f"`{k}`" for k in sorted(set(d["missing"])))
                lines.append(f"- {badge} · _{cat_title}_ → missing: {missing_list}")
            if s.get("residue"):
                lines.append("")
                lines.append("  **Runtime residue (separate from schema — fix in HTML/JS, not publish.py):**")
                for pg, hits in sorted(s["residue"].items()):
                    parts = []
                    if hits["critical"]:
                        parts.append("crit: " + ", ".join(hits["critical"]))
                    if hits["warning"]:
                        parts.append("warn: " + ", ".join(hits["warning"]))
                    lines.append(f"  - `{pg}` — {'; '.join(parts)}")
            lines.append("")
    else:
        lines += [
            "## All countries already match LV reference",
            "",
            "No `publish.py` patches needed. The Stage 7e harness will keep "
            "watching weekly; any drift introduced by a future refresh will "
            "surface on the next Monday cron.",
            "",
        ]

    lines += [
        "---",
        "",
        "## Cross-validation gate (KB §49.11)",
        "",
        "This report was generated from a **local** audit run, so the engineer "
        "could start working immediately. Once Monday's scheduled cron also "
        "produces a `runtime-audit-*.json` artifact, run:",
        "",
        "```",
        "python3 automation/scripts/cross_validate_parity.py \\",
        "    --local  ~/ssi-parity-sweep/{ISO}/findings.json \\",
        "    --cron   <path-to-Monday's-artifact>/runtime-audit-*.json",
        "```",
        "",
        "Any country where the two reports disagree is a sign of either:",
        "  (a) a race between this report and a refresh that happened between "
        "the two runs (likely benign — investigate the commit log);",
        "  (b) live-vs-local schema drift (unlikely — runtime_audit.py uses "
        "live URLs in both modes);",
        "  (c) a bug in `generate_parity_report.py` or the cron pipeline.",
        "",
        "KB §49.11 — Schema parity sweep gates a country as 'patched' only "
        "after BOTH the local report and the next cron report show ✓ clean.",
        "",
    ]
    return "\n".join(lines)


def render_checklist_md(s: dict, audit_started: str) -> str:
    """Per-country checklist for pasting into a PR description."""
    if s["status"] != "needs_patch":
        return ""  # nothing to do

    lines = [
        f"# Schema parity patch — `{s['slug']}`",
        "",
        f"_Source: Stage 7e audit {audit_started[:10]} UTC · KB §49.11_",
        "",
        f"**Priority**: {s['patch_priority']} · "
        f"**{s['critical_keys']}** critical key(s) · "
        f"**{s['warning_keys']}** warning key(s)",
        "",
        "## What's missing",
        "",
    ]
    for cat_key, cat_title in SCHEMA_CATEGORIES:
        if cat_key not in s["by_category"]:
            continue
        d = s["by_category"][cat_key]
        if not d["missing"]:
            continue
        lines.append(f"### {cat_title}")
        lines.append("")
        sev = "**CRITICAL**" if d["severity"] == "critical" else "warning"
        lines.append(f"_{sev}_")
        lines.append("")
        for k in sorted(set(d["missing"])):
            lines.append(f"- [ ] `{k}`")
        lines.append("")

    lines += [
        "## How to patch",
        "",
        "1. Open `scoring-{}/publish.py` for this country.".format(s["slug"][:2]),
        "2. Locate the dict that builds the relevant section "
        "(`fleet_summary`, `meta`, the substation loop, `regions[]`, etc.).",
        "3. Add each missing key with a value derived from this country's "
        "scoring logic. Do NOT copy literal values from Latvia — derive them.",
        "4. Re-run the pipeline locally:",
        "   ```",
        "   python3 scoring-XX/score-country.py",
        "   ```",
        "5. Diff the new `ssi-data.json` vs the old — confirm only the "
        "expected keys changed, nothing else.",
        "6. Deploy via this country's existing deploy script.",
        "7. After Monday's Stage 7e cron, confirm this country shows ✓ clean.",
        "",
    ]

    if s.get("residue"):
        lines += [
            "## Runtime residue (separate work — patch HTML/JS, not publish.py)",
            "",
        ]
        for pg, hits in sorted(s["residue"].items()):
            lines.append(f"- `{pg}`")
            for label in hits.get("critical", []):
                lines.append(f"  - [ ] crit: {label}")
            for label in hits.get("warning", []):
                lines.append(f"  - [ ] warn: {label}")
        lines.append("")

    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--audit", required=True,
                   help="Path to runtime-audit-{ISO}.json (input)")
    p.add_argument("--out", required=True,
                   help="Output directory for PARITY_REPORT.md + checklists")
    args = p.parse_args()

    audit_path = Path(args.audit)
    audit_data = json.loads(audit_path.read_text())
    out_dir = Path(args.out)
    (out_dir / "checklist").mkdir(parents=True, exist_ok=True)

    summaries = build_country_summary(audit_data.get("per_country", []))

    # Master report
    report_md = render_md_report(audit_data, summaries)
    (out_dir / "PARITY_REPORT.md").write_text(report_md)

    # Per-country checklists
    written = 0
    started = audit_data.get("started_at", "")
    for s in summaries:
        if s["status"] != "needs_patch":
            continue
        cl = render_checklist_md(s, started)
        if cl:
            (out_dir / "checklist" / f"{s['slug']}.md").write_text(cl)
            written += 1

    # Machine-readable findings index
    findings = {
        "source_audit":   str(audit_path),
        "audit_started":  started,
        "generated_utc":  datetime.datetime.utcnow().isoformat() + "Z",
        "summary_by_country": summaries,
    }
    (out_dir / "findings.json").write_text(
        json.dumps(findings, indent=2, ensure_ascii=False)
    )

    print(f"[parity] wrote {out_dir / 'PARITY_REPORT.md'}")
    print(f"[parity] wrote {written} per-country checklist(s) under {out_dir / 'checklist'}")
    print(f"[parity] wrote {out_dir / 'findings.json'}")
    needs = sum(1 for s in summaries if s["status"] == "needs_patch")
    if needs:
        print(f"[parity] → {needs} countries need publish.py patches")
        sys.exit(0)  # Not a CI failure — it's a planning report
    else:
        print("[parity] ✓ all countries match LV reference — no patches needed")


if __name__ == "__main__":
    main()
