#!/usr/bin/env bash
# Regenerate the pipeline matrix. Run in the same commit as any pipeline change.
# Per-country subprocesses: one process holding all 39 countries is an OOM.
set -euo pipefail
cd "$(dirname "$0")/.."
OUT="${1:-/tmp/matrix}"
mkdir -p "$OUT"
for c in $(ls -d */ssi-data.json | cut -d/ -f1); do
  python3 scripts/pipeline_matrix_probe.py "$c" > "$OUT/$c.json"
done
python3 scripts/gen_pipeline_matrix.py "$OUT"
