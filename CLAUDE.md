# CLAUDE.md — SSI Index public dashboard briefing

> Auto-loaded briefing for Claude sessions on the `ikengassiindex.github.io` repo. Read this first before touching the codebase.
> Maintained by Ikenga / Cowork · Last updated: **25 June 2026 (Discipline #36 closure — cross-border substation enforcement gate live + pytest sentinel + 39-country cohort canonical at 174,046 substations cleaned of cross-border leakage)**

## What this repo is

This is the **public dashboard** for the SSI Index methodology, served via GitHub Pages at `https://ikengassiindex.github.io`. It is NOT the methodology development repository — that lives in `~/Library/CloudStorage/OneDrive-…/SSI Index/Report Production/` and is published as foundational documents (REPORTS_FRAMING_KB.md, About_SSI_Index.md, METHODOLOGY_DISCIPLINES.md, etc.).

This repo holds **39 country folders** (austria, canada, chile, …, uk) each carrying:

- `bounds.json` — national polygon (Natural Earth derived) for the cross-border filter
- `ssi-data.json` — per-substation canonical (the methodology output)
- `grid-geo.json` — substations + transmission/distribution lines + areas for the map
- 7 HTML pages: `index.html`, `map.html`, `methodology.html`, `regional.html`, `data.html`, `intelligence.html`, `esg-report.html`
- 1 metadata + override JS pair: `ssi-metadata.js`, `{slug}-section-overrides.js`

Plus:
- `intelligence/countries.json` — **single source of truth for the 39-country slug list** (KB §57; never hardcode the slug list anywhere else)
- `intelligence/edition-config.json` — monthly edition counter
- `versions.json` — methodology version pin
- `cross_border_tolerances.json` — per-country tolerance config for the cross-border gate (Discipline #36)
- `scripts/` — ingestion + remediation + audit tooling
- `scripts/pipeline/` — Monte Carlo scoring engine (Phase 1 PR-1+, Phase 1.5 P15-A+)
- `tests/` — pytest sentinel suite (10+ tests)
- `.github/workflows/` — 7 CI workflows (validate, pipeline-enrichment, monthly-refresh, etc.)

## Methodology version

**v4.2** (current). Peer-reviewed anchor: *Journal of Infrastructure Preservation and Resilience* v16 (doi:10.1186/s43065-026-00193-z); *Environmental Research: Energy* companion bound. Per-country canonicals at the v4.2 + v4.0.2 (legacy) versions are committed; v4.0.2 backups live at `{slug}/_v4.0.2.backup/` per Convention #56 (visibly-honest degradation — old versions preserved for audit, not silently overwritten).

## Live deployment

GitHub Pages auto-deploys `main` HEAD within ~30-90 seconds of any push. There is no staging environment — `main` IS production. The validate.yml CI workflow gates every PR + push touching `*/ssi-data.json` or `*/grid-geo.json` to prevent broken data from landing.

## Binding disciplines (the codebase-level conventions that prevent regressions)

### Discipline #36 — Cross-border substation enforcement gate (NEW · 18 June 2026)

**Problem this prevents.** Per-country `ssi-data.json` was ingesting substations via bounding-box queries against upstream OSM / regulator sources. Bounding boxes overshoot national polygons (especially for concave borders, enclaves, coastline complexity), so substations from neighbouring countries leak into each country's canonical. Pre-fix audit (18 June 2026) found ~17% of cohort substations (≈24,650 of 174,046) were misattributed cross-border. Worst cases: Austria 47.5% outside, Canada 74.4%, Greenland 86.5%, Norway 23.4%, Mexico 22.5%, UK 19.2%, Chile 12.1%, France/DOM-TOM polygon gaps.

**Five-layer defense in depth.**

1. **`{country}/bounds.json`** — Natural Earth derived national polygon, topology-healed (Italy 12 of 20 region polygons fixed). Source of truth for the polygon test.
2. **`cross_border_tolerances.json`** — per-country tolerance config. Default 100m (cadastral standard). Greenland / New Zealand / Norway / Denmark get 5km for fjord/coastline simplification (Mode 2). UK gets Northern Ireland territorial extension; France gets DOM-TOM; Chile gets partial; Canada gets Arctic territories (Mode 3).
3. **`scripts/pipeline/utils/geo.py`** — shapely-backed helpers: `load_country_polygon`, `load_country_tolerance`, `is_inside_country`, `filter_by_country_polygon`, `cross_border_audit`.
4. **`scripts/remediate_cross_border.py`** — per-country one-shot fixer. Loads bounds + tolerance, filters substations, recomputes `meta` + `fleet_summary` + `regions`. Idempotent: re-running on clean data is a no-op. **Lines connecting filtered-in substations to filtered-out substations are KEPT** per `scripts/clean_grid_geo.py` — the user requirement was "keep relevant power lines."
5. **`scripts/check_cross_border.py`** — CI-friendly deploy-gate. `--all --strict` fails the build if any country exceeds 5% outside-polygon threshold. JSON output via `--json out.json` for diffing across runs.

**Three enforcement points.**

- **PR-time gate**: `.github/workflows/validate.yml` runs `check_cross_border.py --all --strict` on every PR/push touching `*/ssi-data.json` or `*/grid-geo.json`. Cross-border drift is structurally impossible to merge.
- **Monthly pipeline auto-remediation**: `.github/workflows/pipeline-enrichment.yml` 1st-Thursday cron runs `remediate_cross_border.py` per country after ingestion, then `clean_grid_geo.py --all-remediated`, then `refresh_country_counts.py --all-remediated`, then the final `check_cross_border.py --all --strict` audit. If the upstream ingestion bounding-box overshoots again (it will), the filter strips cross-border substations before the commit.
- **Pytest sentinel**: `tests/test_no_cross_border_leakage.py` runs the same audit at `pytest tests/` time. Mirrors the CI gate at the local layer so contributors catch regressions before pushing. Marked `@pytest.mark.integration + @pytest.mark.slow` (~30s wall-clock for full cohort sweep through shapely).

**Authoritative documentation.**

- `CROSS_BORDER_SUBSTATION_AUDIT_20260618.md` — original audit memo (discovery + 4 failure-mode classification + per-country results + remediation queue)
- `MODE_2_3_FOLLOWON_PLAN.md` — second-wave remediation plan (tolerance config + territorial polygon extensions)
- `PR_CROSS_BORDER_GUARD.md` — PR-ready integration notes (the description used for PR #1)

**Closure status.** Discipline #36 codified 18 June 2026; PR #1 merged 24 June 2026 (commit `86d7c9df`). Austria 1,406 → 741 substations on the live site. All 10 originally-leaking countries remediated and pinned by sentinel.

### KB §57 — Single source of truth for the 39-country slug list

The 39-country slug list lives in `intelligence/countries.json::slugs` and ONLY there. Never hardcode the list in shell scripts, workflows, Python modules, HTML pages, JS files, or anywhere else. Read from the SoT at runtime via `json.load(open('intelligence/countries.json'))['slugs']`. Pre-KB-§57 the `pipeline-enrichment.yml` cache-bust loop hardcoded 24 countries and silently excluded BE/NL/LU/CZ/LV/LT/EE from the monthly enrichment loop. This is the failure-mode that motivated the rule.

### KB §91.A / §91.B — Cron-gate discipline

GitHub Actions cron uses OR semantics when both day-of-month AND day-of-week are restricted. `'0 6 1-7 * 4'` looks like "1st Thursday at 06:00 UTC" but actually fires ~10×/month. Workflows that need "1st Thursday" / "2nd Thursday" must use a narrow cron (`'0 6 * * 4'` = every Thursday) plus a runtime DOM gate inside the workflow (DOM ≤ 7 for 1st Thursday; 8 ≤ DOM ≤ 14 for 2nd Thursday). Manual `workflow_dispatch` invocations always proceed regardless of the gate.

### KB §91.A pull-rebase race defuse

Multiple workflows can push to `main` concurrently (intelligence + ESG monthly refresh + manual dispatches). Each push step does `git pull --rebase --autostash origin main` with 3 attempts, falling back to `merge -X ours` if the rebase conflicts (the cron's enrichment + edition bump always wins over a competing external push). The `concurrency: monthly-refresh-main` block at workflow level prevents same-workflow race.

### Convention #56 — Visibly-honest degradation (inherited from the SSI Index methodology framework)

When a value cannot be sourced from a public regulatory canonical, the methodology surfaces `[N/A]` markers + degradation reasons rather than silent defaults. The v4.0.2 → v4.2 promotion preserves `_v4.0.2.backup/` per country so older deliverables remain auditable. Applies cohort-wide: ingestion failures surface as visible gaps, not silent zeros.

## Quick reference — running the tooling

```bash
# Run the full pytest suite (locally; CI runs validate.yml on push)
pytest tests/                                                  # all tests
pytest tests/test_no_cross_border_leakage.py -v                # Discipline #36 sentinel only
pytest tests/ -m "not slow"                                    # skip slow integration tests

# Cross-border audit (manual diagnostic)
python3 scripts/check_cross_border.py --all                    # full cohort report
python3 scripts/check_cross_border.py --all --strict           # fail on any violation
python3 scripts/check_cross_border.py austria                  # single country
python3 scripts/check_cross_border.py --all --json out.json    # machine-readable

# Per-country remediation (one-shot)
python3 scripts/remediate_cross_border.py austria              # fix Austria
python3 scripts/remediate_cross_border.py austria --dry-run    # preview only
python3 scripts/clean_grid_geo.py --all-remediated             # propagate to grid-geo
python3 scripts/refresh_country_counts.py --all-remediated     # propagate to HTML pages

# Pipeline run (manual; cron is monthly 1st Thursday 06:00 UTC)
python -m scripts.pipeline.run --all                           # full pipeline
python -m scripts.pipeline.run austria germany italy           # specific countries
python -m scripts.pipeline.run --all --skip-rescore --dry-run  # fast preview
```

## When you need to modify something

| Change type | Where to edit | How to verify |
|---|---|---|
| Fix a country's substation data | `{slug}/ssi-data.json` (rarely manually; usually via pipeline + remediation) | `pytest tests/test_no_cross_border_leakage.py -v` + `scripts/check_cross_border.py {slug}` |
| Extend a country's bounds (add territorial polygon) | `{slug}/bounds.json` (Natural Earth + manual additions documented in `MODE_2_3_FOLLOWON_PLAN.md`) | Re-run remediation + verify pytest green |
| Add a tolerance for a new Mode 2 country | `cross_border_tolerances.json::per_country` | Verify pytest `TestToleranceConfig` passes |
| Add a new country to the cohort | `intelligence/countries.json::slugs` + create `{slug}/` folder + drop `bounds.json` + run pipeline | Verify all 39+1 tests pass; CI gate runs on PR |
| Change the cross-border threshold | `scripts/check_cross_border.py` default + `tests/test_no_cross_border_leakage.py::THRESHOLD_PCT` + workflow files (find via grep `THRESHOLD_PCT`) | The threshold lives in three places — keep in sync |
| Add a new pipeline modifier | `scripts/pipeline/scoring/modifier_registry.py` + write tests | `pytest tests/test_modifier_registry.py -v` |

## Pre-commit checklist

Before pushing to `main` or merging a PR:

- [ ] `pytest tests/` → all tests green (10+ existing + the 4 cross-border classes)
- [ ] `scripts/check_cross_border.py --all --strict` → green (or PR's validate.yml will fail)
- [ ] If you touched `*/ssi-data.json` or `*/grid-geo.json`: confirm `validate.yml` is green on the PR
- [ ] If you added a new country: confirm pytest discovers the new slug via `intelligence/countries.json`
- [ ] If you changed methodology version: bump `versions.json` + the v4.0.2-style backup pattern per Convention #56

## Companion documents

| Doc | Role | Where it lives |
|---|---|---|
| `CLAUDE.md` (this file) | Session briefing + binding disciplines | repo root |
| `CROSS_BORDER_SUBSTATION_AUDIT_20260618.md` | Discipline #36 origin audit | repo root |
| `MODE_2_3_FOLLOWON_PLAN.md` | Discipline #36 second-wave plan | repo root |
| `PR_CROSS_BORDER_GUARD.md` | Discipline #36 PR-ready notes | repo root |
| `REPORTS_FRAMING_KB.md` §72 | Discipline #36 cross-reference from the SSI Index methodology framework | `~/Library/CloudStorage/OneDrive-…/SSI Index/Report Production/00-Framing/REPORTS_FRAMING_KB.md` (separate repo) |
| `PHASE_1_IMPLEMENTATION_PLAN.md` | Phase 1 PR-1+ scoring engine | repo root (canonical Phase 1 narrative) |
| `AUDIT_v4_0_2_PRE_v4_2_FOUNDATION.md` | v4.0.2 → v4.2 audit (F-Lx-y findings) | repo root |
| `intelligence/countries.json` | 39-country slug + first-refresh SoT (KB §57) | repo |

## Contact

- **Cedric Berard** — c.berard@ikenga.eu — Ikenga Capital
- **SSI Index project** — ssi_index@ikenga.eu

---

*If you find this briefing outdated, update it in the same commit as your fix.*
