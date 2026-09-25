#!/usr/bin/env bash
#
# SSI Index — pre-commit hook (task #125)
#
# Install once (from repo root):
#   ln -sf ../../scripts/hooks/pre-commit.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#
# Purpose: catch the indent=2 pretty-printing bloat class on ssi-data.json /
# grid-geo.json BEFORE it hits GitHub's hard 100 MB per-file limit + force-push
# cleanup pain.  Delegates to scripts/check_data_file_sizes.py which supports
# --only-staged mode (checks only files git has staged, so unrelated commits
# aren't slowed down).
#
# To bypass in emergencies: git commit --no-verify

set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"

python3 "${repo_root}/scripts/check_data_file_sizes.py" --only-staged --threshold 90
