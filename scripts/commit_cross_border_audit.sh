#!/bin/bash
# commit_cross_border_audit.sh — Run from the repo root on your Mac terminal.
# Authored 18 June 2026 deep night. Executes the full commit + push for the
# Discipline #36 cross-border audit work in structured, reviewable commits.
#
# What it does:
#   1. Clears the stale .git/index.lock (left from earlier process)
#   2. Creates feature branch feature/cross-border-audit-2026-06-18 (if not exists)
#   3. Commits in 6 logical groups with ConventionalCommits formatting
#   4. Pushes the feature branch to origin
#
# After this runs, open a PR on github.com/ikengassiindex/ikengassiindex.github.io
# from feature/cross-border-audit-2026-06-18 → main.
#
# Usage:
#   cd ~/ikengassiindex.github.io
#   bash scripts/commit_cross_border_audit.sh
#
# Exits 0 on success; non-zero on first failure.

set -e
set -o pipefail

# Color helpers
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

say() { echo -e "${BLUE}▸${NC} $*"; }
ok()  { echo -e "${GREEN}✓${NC} $*"; }
warn(){ echo -e "${YELLOW}⚠${NC} $*"; }
err() { echo -e "${RED}✗${NC} $*"; }

say "Step 0: clear stale .git/index.lock if present"
if [ -f .git/index.lock ]; then
  rm -f .git/index.lock && ok "stale lock removed" || { err "could not remove .git/index.lock"; exit 1; }
fi

say "Step 1: create + switch to feature branch"
BRANCH="feature/cross-border-audit-2026-06-18"
if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
  git checkout "$BRANCH"
  ok "switched to existing branch $BRANCH"
else
  git checkout -b "$BRANCH"
  ok "created + switched to $BRANCH"
fi

# ─── COMMIT 1: .gitignore housekeeping ───────────────────────────────────────
say "Commit 1/6: .gitignore — exclude backup files + ingestion rejection logs"
git add .gitignore
git commit -m "chore(gitignore): exclude .backup files + ingestion_rejected_*.json (Discipline #36)

Two new patterns added:
- *.pre-*.backup   - backups produced by remediate_cross_border.py,
                     clean_grid_geo.py, refresh_country_counts.py
- */ingestion_rejected_*.json - forensic audit-trail artifacts; too
                                large for the repo (Canada: 52 MB)

Audit memo CROSS_BORDER_SUBSTATION_AUDIT_20260618.md preserves the
per-country summary; full rejection lists stay on operator's machine."

# ─── COMMIT 2: Infrastructure ────────────────────────────────────────────────
say "Commit 2/6: infrastructure — helpers, deploy gate, remediation tools"
git add \
  scripts/pipeline/utils/geo.py \
  scripts/pipeline/requirements.txt \
  scripts/check_cross_border.py \
  scripts/remediate_cross_border.py \
  scripts/clean_grid_geo.py \
  scripts/refresh_country_counts.py \
  cross_border_tolerances.json

git commit -m "feat(audit): add cross-border substation enforcement gate (Discipline #36, KB §72)

Closes the failure-mode-1 class surfaced by the 18 Jun 2026 audit: per-country
ssi-data.json was inheriting substations from neighbouring countries via
ingestion bounding-box overshoot (Austria 47.5% Bavarian/Slovenian/South-
Tyrolean, Canada 74.4% US/Greenland-coords, etc.).

New helpers in scripts/pipeline/utils/geo.py (shapely-backed, lazy-imported):
  - load_country_polygon(country)  - loads + auto-heals bounds.json
  - load_country_tolerance(country) - reads cross_border_tolerances.json
  - is_inside_country(lat, lon, polygon, tolerance_km)
  - filter_by_country_polygon(subs, polygon, tolerance_km)
  - cross_border_audit(country, tolerance_km=None)

New tools at scripts/ root:
  - check_cross_border.py    - deploy-gate, CI-friendly --strict/--json flags
  - remediate_cross_border.py - per-country substation filter + recomputes
                                meta + fleet_summary + regions
  - clean_grid_geo.py        - propagates filter to grid-geo.json s/l/a
  - refresh_country_counts.py - propagates post-remediation counts to all
                                country HTML/JS pages + root index data-subs

Methodology-transparent per-country tolerance config at
cross_border_tolerances.json (default 100m; Greenland/NZ/Denmark/Norway 5km
for fjord/coastline simplification).

shapely>=2.0 added to scripts/pipeline/requirements.txt.

See CROSS_BORDER_SUBSTATION_AUDIT_20260618.md + PR_CROSS_BORDER_GUARD.md."

# ─── COMMIT 3: Italy bounds.json topology heal ───────────────────────────────
say "Commit 3/6: italy/bounds.json topology heal"
git add italy/bounds.json
git commit -m "fix(italy): heal bounds.json topology — 12 of 20 region polygons (Discipline #36)

12 Italian region polygons had self-intersections (Lombardia, Veneto,
Friuli-Venezia Giulia, Liguria, Emilia-Romagna, Toscana, Campania, Puglia,
Basilicata, Calabria, Sicilia, Sardegna). Healed via shapely buffer(0)
which fixes ring topology without changing substantive shape.

Post-heal cross-border audit: 4,289 of 4,293 Stage-4 substations
verifiably inside Italian polygon (99.91%); 4 outliers within 20m
boundary-precision tolerance (SE Cala Telegrafo, Malalbergo, Preci,
Fincantieri - all geographically Italian).

Strategic Brief No. 01 Stage-4 validation claim verified empirically."

# ─── COMMIT 4: Per-country remediations (data) ───────────────────────────────
say "Commit 4/6: per-country ssi-data.json + grid-geo.json remediations"
for country in austria mexico norway uk france chile canada; do
  git add "$country/ssi-data.json" "$country/grid-geo.json"
done
git commit -m "fix(cohort): remediate 7 countries' cross-border substation leakage (Discipline #36)

Applied scripts/remediate_cross_border.py + scripts/clean_grid_geo.py to
seven countries that exceeded the 5% --strict threshold:

  Country  | Pre-remediation | Post-remediation | Removed
  ---------|-----------------|------------------|--------
  austria  |        1,406    |           741    |    665   (Bavaria + Slovenia + South Tyrol + Engadin)
  mexico   |        3,140    |         2,436    |    704   (US: Sahuarita/AZ, Rough Canyon/TX)
  norway   |        6,495    |         5,842    |    653   (Sweden: Vargfors, Bålforsens kraftstation, Gallejaur)
  uk       |        3,150    |         2,551    |    599   (North Sea / European coast mis-coords)
  france   |        7,898    |         7,378    |    520   (Northern Spain: Cantabrian coast)
  chile    |        1,095    |           965    |    130   (Argentina: Santa Cruz / Patagonia)
  canada   |       24,986    |         6,399    | 18,587   (US: Wyoming/Nebraska/Colorado + Greenland coords)

  Total substations removed cohort-wide: 21,858
  Aggregate cohort total: 174,046 to 152,188 (verifiable to polygon)

grid-geo.json cleaned in parallel (same point-in-polygon filter applied to
s dict + l list). Cross-border power lines preserved (real ENTSO-E
interconnections); only fully-outside lines dropped.

Cohort gate now passes scripts/check_cross_border.py --all --strict at 5%
threshold: exit code 0; zero violators."

# ─── COMMIT 5: Per-country page assets ───────────────────────────────────────
say "Commit 5/6: per-country HTML/JS page count refresh"
for country in austria mexico norway uk france chile canada; do
  for f in \"\$country/index.html\" \"\$country/map.html\" \"\$country/data.html\" \\
           \"\$country/esg-report.html\" \"\$country/methodology.html\" \\
           \"\$country/regional.html\" \"\$country/intelligence.html\" \\
           \"\$country/ssi-metadata.js\" \"\$country/\${country}-section-overrides.js\"; do
    [ -f "$f" ] && git add "$f"
  done
done
git add index.html

git commit -m "fix(pages): refresh hardcoded substation counts for 7 remediated countries (Discipline #36)

The data-canonical=fleet.total spans (and the embedded JSON canonical-
store blocks) contained pre-remediation counts hardcoded as fallback text.
Applied scripts/refresh_country_counts.py which reads post-remediation
counts from ssi-data.json and propagates them to:

  - {country}/index.html, map.html, data.html, esg-report.html,
    methodology.html, regional.html, intelligence.html
  - {country}/ssi-metadata.js
  - {country}/{country}-section-overrides.js
  - index.html (root - data-subs attribute on country path)

Updated headlines (example):
  - austria map.html: 'Explore 1,406 substations' to 'Explore 741 substations'
  - canada map.html: 'Explore 24,986 substations' to 'Explore 6,399 substations'

Updated breakdown (example, Austria):
  - 131 EHV (>=220 kV) to 86 EHV
  - 1,013 HV (110-220 kV) to 553 HV
  - 262 distribution-tier to 102 distribution-tier
  - 1,144 HV-aggregate to 639 HV-aggregate

Root index.html data-subs attribute updated for all 7 country paths."

# ─── COMMIT 6: Docs ──────────────────────────────────────────────────────────
say "Commit 6/6: audit memo + follow-on plan + PR description"
git add \
  CROSS_BORDER_SUBSTATION_AUDIT_20260618.md \
  MODE_2_3_FOLLOWON_PLAN.md \
  PR_CROSS_BORDER_GUARD.md

git commit -m "docs(audit): cross-border substation audit memo + follow-on plan + PR description (Discipline #36)

CROSS_BORDER_SUBSTATION_AUDIT_20260618.md - full audit memo:
  - Discovery + 4 failure-mode classification (1: ingestion overshoot;
    2: coastline precision; 3: polygon gap; 4: topology self-intersection)
  - Per-country audit results (39 countries; pre + post remediation)
  - Italy Stage-4 verification (99.91% in-polygon, brief claim stands)
  - Remediation queue + completion status

MODE_2_3_FOLLOWON_PLAN.md - second-wave plan (mostly executed in-session):
  - Per-country tolerance config rationale (Greenland 5km, NZ 5km, etc.)
  - Mode 1 reclassification of UK/France/Chile/Canada/Norway after
    detailed name + coordinate evidence
  - Sequencing + data-source provenance

PR_CROSS_BORDER_GUARD.md - PR-ready description:
  - What changed; why; how to test; CI integration; future-state notes;
    backward compatibility guarantees."

ok "All 6 commits landed on feature branch $BRANCH"

# ─── Push ────────────────────────────────────────────────────────────────────
say "Pushing feature branch to origin..."
git push -u origin "$BRANCH"
ok "branch pushed"

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "  Open the PR at:"
echo "    https://github.com/ikengassiindex/ikengassiindex.github.io/compare/main...$BRANCH"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo "Summary log of commits on this branch:"
git log --oneline main..HEAD
