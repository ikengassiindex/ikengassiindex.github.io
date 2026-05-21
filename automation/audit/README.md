# Stage 7e — Runtime audit harness

`automation/audit/` is the home for Stage 7e — the post-deploy
correctness gate that runs once a week (and on demand) against the
*live* `ikengassiindex.github.io` site, scanning every country page
for residue + schema drift.

KB §49.10 codifies the architecture. This file is the operational
guide for engineers who need to interpret findings, extend the
scanner, or change reporting channels.

---

## What it does

For every country slug in `intelligence/countries.json` (the canonical
SoT after the §49.8 consolidation), Stage 7e runs two passes:

**Pass 1 — Residue scan (Playwright + headless Chromium).** Loads each
of the 8 pages (`index`, `regional`, `map`, `intelligence`, `data`,
`esg-report`, `methodology`, `dno-dashboard`), waits for JS + canvas to
settle, cycles through every `.tab-btn` to expand lazy-rendered
sections, then scans the rendered HTML for known residue patterns:

| Pattern                          | Meaning                                                       | Severity |
|----------------------------------|---------------------------------------------------------------|----------|
| `Loading…`                       | IIFE didn't finish populating its target node                 | critical |
| <code>&#124;&#124;UPPER_TOKEN&#124;&#124;</code> | Placeholder token never substituted                          | critical |
| `>GAP<` (readiness pill)         | A field referenced by the template was missing from JSON      | warning  |
| `— kV`                            | em-dash voltage = untagged substation                         | warning  |
| `Edition 003+`                   | 3-digit edition regression (Estonia bug fingerprint)          | critical |
| `NOT ACTIVE`                     | Literal "NOT ACTIVE" placeholder                              | critical |
| `INACTIVE for <country>`         | INACTIVE label bled in from the CZ reference                  | warning  |
| `\d+(\.\d+)?%%`                  | Double-percent bug (status pill miscalculation)               | critical |

Patterns are matched with regex; matches inside `<!-- … -->` comments
or near a `KB §` reference are skipped to avoid false positives from
the methodology page where these strings appear in documentation.

**Pass 2 — Schema diff.** Loads each country's `ssi-data.json` (locally
when present, falling back to live fetch) and compares the key set
against the Latvia reference — the most complete schema in the fleet
post-§49.5. Missing keys in any of these dicts are flagged:

```
top_level     – country, edition, fleet_summary, regions, substations, …
fleet_summary – total_substations, R_median, low_band, …
meta          – mc_iterations, sobol_iterations, engine_version, …
substation    – substation_id, voltage_kv, R_median, modifiers, markov, …
modifiers     – R3, R3_C_mult, R4_F_topo, R6_seismic, R7_cyber, compound, …
markov        – risk_score, p_critical_20yr, ETTC_years, corrosion_class, …
regions[]     – region, substation_count, R_median, bands, pct_critical, …
```

Missing `modifiers` aliases are **critical** — they cause `TypeError`
on `.toFixed` in the dashboard JS. Everything else is **warning**.

---

## Reporting channels

A single run emits the same data via four channels:

1. **JSON artifact** `runtime-audit-report` — full per-country
   findings, 90-day retention. Useful for diffing across runs and
   for `jq` queries.

2. **Job step summary** — Markdown table written to
   `$GITHUB_STEP_SUMMARY` so the Actions UI shows the result inline,
   no clicking through to logs.

3. **Tracking issue** `Runtime audit — open findings` (label:
   `runtime-audit`) — created or updated on each run. **Closed
   automatically** when a clean run follows a non-clean one, so the
   project board doesn't accumulate stale issues. Body contains the
   same table as the step summary plus a link back to the run.

4. **Microsoft Graph email digest** to `ssi_index@ikenga.eu` —
   HTML table + JSON attachment, sent via the same Entra ID app
   already used by `scripts/archive-and-email.py` for the monthly
   bundle. Suppressed by default when there are zero findings (we
   don't want a heartbeat email — Actions run history is the
   heartbeat). Set `--always-send` to override.

The audit harness itself exits 1 on any critical finding, but the
workflow runs it with `continue-on-error: true` and only `::warning::`s
on critical findings. The workflow is **purely informational**; it
does not block deploys. If a country must be gated, that belongs in
`validate.yml`.

---

## File layout

```
automation/
  scripts/
    runtime_audit.py        ← main harness (Playwright + schema diff)
    send_audit_digest.py    ← Graph email sender (auth + render + post)
  audit/
    README.md               ← you are here
    _logs/                  ← runtime-audit-{ISO}.json   (gitignored)
    _summary/SUMMARY.md     ← latest Markdown summary    (gitignored)
.github/workflows/
  runtime-audit.yml         ← schedule + dispatch wrapper
```

Outputs under `audit/_logs/` and `audit/_summary/` are produced by the
harness at runtime and uploaded as artifacts — they are not committed
to the repo.

---

## Local invocation

Quick schema-only scan (no Playwright install needed):

```bash
python3 automation/scripts/runtime_audit.py \
  --skip-playwright \
  --countries latvia,lithuania,estonia
```

Full run including residue scan against the live site:

```bash
pip install playwright==1.45.0
python -m playwright install chromium
python3 automation/scripts/runtime_audit.py --countries latvia
```

Render + send a digest from the most recent JSON report:

```bash
export AZURE_TENANT_ID=...
export AZURE_CLIENT_ID=...
export AZURE_CLIENT_SECRET=...
python3 automation/scripts/send_audit_digest.py \
  --latest audit/_logs/ \
  --always-send
```

---

## Extending the scanner

**Add a residue pattern.** Append a `(label, regex, severity)` tuple
to `RESIDUE_PATTERNS` in `runtime_audit.py`. Keep the regex anchored
to HTML structure (e.g. `>GAP<` not bare `GAP`) to avoid false hits in
methodology copy. Add a row in this README's pattern table.

**Add a schema key.** Append to `LV_REFERENCE_KEYS[<dict>]` in the
same file. Choose `critical` only if the dashboard JS throws on the
missing key — otherwise `warning` is correct. Latvia is the canonical
reference because §49.5 left it the most complete; if Latvia's schema
itself changes, update the reference set in the same commit that
updates Latvia's `publish.py`.

**Add a country.** Nothing to do — the harness reads slugs from
`intelligence/countries.json`. Add the slug there (the §49.8 SoT) and
the next audit run picks it up. Pre-launch countries (with
`first_refresh` in the future) are skipped from the residue scan but
still get a schema diff if their `ssi-data.json` is present locally.

**Change reporting channels.** Step summary + artifacts are baked into
the workflow; the issue tracker uses `actions/github-script`; the
email uses `send_audit_digest.py`. To add Slack, add a step that
parses the same JSON report — keep `runtime_audit.py` as the single
source of truth for what's been found.

---

## KB references

- §49.10 — Stage 7e gate (architecture + production checklist)
- §49.7  — Workflow concurrency control (this workflow's group is
           `runtime-audit-main`)
- §49.8  — Single Source of Truth (slugs come from
           `intelligence/countries.json`, not the deleted root file)
- §47.13 — Two-pass substitution lesson (residue pattern §2 catches
           cases where the second pass failed)
- §47.14 — Edition 003 regression fingerprint (residue pattern §5)
- §49.5  — Latvia schema is the canonical reference (Pass 2 baseline)
