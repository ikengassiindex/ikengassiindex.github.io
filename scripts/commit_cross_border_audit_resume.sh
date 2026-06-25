#!/bin/bash
# commit_cross_border_audit_resume.sh — resume after the line-157 typo.
#
# Commits 1-4 already landed (gitignore + infrastructure + italy heal + 7-country
# data fix). This script picks up where the original left off:
#   - Commit 5/6: per-country HTML/JS page count refresh
#   - Commit 6/6: docs (audit memo + follow-on plan + PR description)
#   - Push feature branch to origin
#
# Usage:
#   cd ~/ikengassiindex.github.io
#   bash scripts/commit_cross_border_audit_resume.sh

set -e
set -o pipefail

GREEN='\033[0;32m'; BLUE='\033[0;34m'; YELLOW='\033[0;33m'; RED='\033[0;31m'; NC='\033[0m'
say() { echo -e "${BLUE}▸${NC} $*"; }
ok()  { echo -e "${GREEN}✓${NC} $*"; }
err() { echo -e "${RED}✗${NC} $*"; }

# Confirm we're on the right branch
BRANCH="feature/cross-border-audit-2026-06-18"
CURRENT=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT" != "$BRANCH" ]; then
  err "Expected branch $BRANCH but on $CURRENT — aborting"
  exit 1
fi
ok "on branch $BRANCH"

# Show what's already committed
say "Already committed on this branch:"
git log --oneline main..HEAD

# ─── COMMIT 5/6: Per-country page assets ────────────────────────────────────
say "Commit 5/6: per-country HTML/JS page count refresh"
for country in austria mexico norway uk france chile canada; do
  for fname in index.html map.html data.html esg-report.html methodology.html regional.html intelligence.html ssi-metadata.js "${country}-section-overrides.js"; do
    fpath="$country/$fname"
    [ -f "$fpath" ] && git add "$fpath"
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

# ─── COMMIT 6/6: Docs ───────────────────────────────────────────────────────
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
