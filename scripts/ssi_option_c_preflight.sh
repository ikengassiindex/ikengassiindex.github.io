#!/usr/bin/env bash
# ssi_option_c_preflight.sh — prepare and verify the Option C switch.
#
#   bash scripts/ssi_option_c_preflight.sh <archive-name>
#
# Authority: doctrine/AMENDMENT_DRAFT_the_engine_leaves_the_public_repository.md
#            SIGNED 25 September 2026.
#
# THIS SCRIPT CHANGES NOTHING ON GITHUB. It reads the live configuration,
# builds the candidate public repository on this machine, verifies it every
# way the amendment claims, and prints the switch runbook for the operator to
# run BY HAND, one command at a time.
#
# It does not run the switch itself, deliberately. Five scripting defects
# reached the operator on 25 September, every one in a step the gates could
# not exercise. A rename, a visibility flip and a repository creation are not
# steps to discover a sixth in.

set -euo pipefail
cd "$(dirname "$0")/.."
REPO_ROOT="$(pwd)"
ARCHIVE_NAME="${1:-}"
OUT="$HOME/ssi-public-new"
CAP="$HOME/ssi-option-c-capture"

if [[ -z "$ARCHIVE_NAME" ]]; then
  cat <<'USAGE'
✗ Give the name the CURRENT repository will be renamed to.

    bash scripts/ssi_option_c_preflight.sh ssi-estate

That repository keeps all 1,713 commits and becomes private. A new public
ikengassiindex.github.io is then created from the verified tree this script
builds. The name is permanent enough to be worth choosing deliberately, so
this script will not pick one for you.
USAGE
  exit 2
fi

echo "═══ Option C pre-flight ═══"
echo "  current repo  : ikengassiindex/ikengassiindex.github.io"
echo "  to be renamed : $ARCHIVE_NAME   (private, keeps all history)"
echo "  new public    : ikengassiindex.github.io   (from the tree built below)"
echo ""

# ── 1. capture the live configuration BEFORE anything changes ─────────────
mkdir -p "$CAP"
echo "── 1. capturing live configuration to $CAP ──"
if command -v gh >/dev/null 2>&1; then
  gh api repos/ikengassiindex/ikengassiindex.github.io           > "$CAP/repo.json"  2>/dev/null || echo "   ! repo.json not captured"
  gh api repos/ikengassiindex/ikengassiindex.github.io/pages     > "$CAP/pages.json" 2>/dev/null || echo "   ! pages.json not captured (Pages may be configured from the UI)"
  if [[ -s "$CAP/pages.json" ]]; then
    python3 - "$CAP/pages.json" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
s=d.get("source") or {}
print("   Pages: branch=%s path=%s  status=%s  https_enforced=%s" % (
    s.get("branch"), s.get("path"), d.get("status"), d.get("https_enforced")))
print("   url  : %s" % d.get("html_url"))
if d.get("cname"): print("   CNAME: %s" % d["cname"])
PY
  fi
  python3 - "$CAP/repo.json" <<'PY' 2>/dev/null || true
import json,sys
d=json.load(open(sys.argv[1]))
print("   repo : private=%s forks=%s network=%s default_branch=%s" % (
    d.get("private"), d.get("forks_count"), d.get("network_count"), d.get("default_branch")))
PY
else
  echo "   ✗ gh not found — install it or capture the Pages settings from the UI first"; exit 1
fi

# ── 2. the closure ────────────────────────────────────────────────────────
echo ""
echo "── 2. the public/private closure ──"
python3 scripts/ssi_public_private_closure.py --build || { echo "✗ closure not clean — stop"; exit 1; }

# ── 3. build the new public tree ──────────────────────────────────────────
echo ""
echo "── 3. building the candidate public repository at $OUT ──"
[[ -e "$OUT" ]] && { echo "   ✗ $OUT already exists. Move or remove it first."; exit 1; }
mkdir -p "$OUT"
python3 scripts/ssi_public_private_closure.py --list-private > "$CAP/private.txt"
git ls-files > "$CAP/tracked.txt"
python3 - "$REPO_ROOT" "$OUT" "$CAP/tracked.txt" "$CAP/private.txt" <<'PY'
import os, shutil, sys
src, dst, tracked, private = sys.argv[1:5]
priv = set(open(private).read().split())
pub  = [f for f in open(tracked).read().split() if f not in priv]
n = 0
for f in pub:
    d = os.path.join(dst, os.path.dirname(f))
    os.makedirs(d, exist_ok=True)
    shutil.copy2(os.path.join(src, f), os.path.join(dst, f))
    n += 1
print("   copied %d files" % n)
open(os.path.join(os.path.dirname(tracked), "public.txt"), "w").write("\n".join(pub))
PY

# ── 4. verify the tree ────────────────────────────────────────────────────
echo ""
echo "── 4. verifying the built tree ──"
[[ -f "$OUT/.nojekyll" ]] || { echo "   ✗ .nojekyll MISSING — Pages would run Jekyll and break underscore paths"; exit 1; }
echo "   ✓ .nojekyll present"
leak=0
while read -r f; do [[ -e "$OUT/$f" ]] && { echo "   ✗ PRIVATE file in the tree: $f"; leak=$((leak+1)); }; done < "$CAP/private.txt"
[[ $leak -eq 0 ]] || { echo "   ✗ $leak private file(s) present — stop"; exit 1; }
echo "   ✓ 0 private files in the tree"
miss=0
while read -r f; do [[ -e "$OUT/$f" ]] || { echo "   ✗ missing: $f"; miss=$((miss+1)); }; done < "$CAP/public.txt"
[[ $miss -eq 0 ]] || { echo "   ✗ $miss public file(s) missing — stop"; exit 1; }
echo "   ✓ every public file present ($(wc -l < "$CAP/public.txt" | tr -d ' '))"

# ── 5. every reference every page makes ───────────────────────────────────
echo ""
echo "── 5. resolving every asset reference in the built tree ──"
python3 - "$OUT" <<'PY'
import os, re, posixpath, collections, sys
root = sys.argv[1]
REF = re.compile(r'(?:href|src)\s*=\s*["\']([^"\'#?>]+)', re.I)
FET = re.compile(r'''fetch\(\s*[`"']([^`"'?]+)''')
have = set()
for dp, _, fs in os.walk(root):
    for f in fs:
        have.add(os.path.relpath(os.path.join(dp, f), root))
pages = sorted(f for f in have if f.endswith('.html'))
checked = 0; bad = collections.Counter()
for p in pages:
    d = posixpath.dirname(p)
    try: s = open(os.path.join(root, p), encoding='utf-8', errors='replace').read()
    except Exception: continue
    for r in set(REF.findall(s)) | set(FET.findall(s)):
        if r.startswith(('http://','https://','//','mailto:','data:','javascript:','tel:')): continue
        checked += 1
        t = r[1:] if r.startswith('/') else posixpath.normpath(posixpath.join(d, r))
        if t not in have and not os.path.isdir(os.path.join(root, t)):
            bad[t] += 1
print("   pages %d · references %d · unresolved %d" % (len(pages), checked, sum(bad.values())))
print("   (161 unresolved is the PRE-EXISTING figure — plan item E20. More than that means a file was misclassified.)")
PY

# ── 6. the validators, in the built tree ──────────────────────────────────
echo ""
echo "── 6. validators, run inside the built tree ──"
( cd "$OUT" && for v in check_required_files check_page_data_agreement check_inline_js_parse check_data_file_sizes check_provenance_citations_resolve; do
    if [[ -f "scripts/$v.py" ]]; then
      out=$(python3 "scripts/$v.py" 2>&1) && rc=0 || rc=$?
      printf "   %-36s exit %s\n" "$v" "$rc"
    fi
  done )

# ── 7. the runbook ────────────────────────────────────────────────────────
cat <<RUNBOOK

═══ PRE-FLIGHT COMPLETE — nothing has changed on GitHub ═══

  built tree : $OUT
  capture    : $CAP  (repo.json, pages.json — the settings to restore)

Run these FOUR commands by hand, one at a time, checking each before the next.
The site is unreachable between step 2 and step 4; prepare, then move quickly.

  1. Rename the current repository. It keeps every commit.
     gh repo rename $ARCHIVE_NAME --repo ikengassiindex/ikengassiindex.github.io

  2. Make it private. THIS is the step that removes the engine from the public.
     gh repo edit ikengassiindex/$ARCHIVE_NAME --visibility private --accept-visibility-change-consequences

  3. Create the new public repository from the verified tree.
     cd $OUT && git init -q -b main && git add -A && \\
       git commit -q -m "SSI Index — public site and validators" && \\
       gh repo create ikengassiindex/ikengassiindex.github.io --public --source=. --push

  4. Re-enable Pages with the captured settings (branch/path are in pages.json).
     gh api -X POST repos/ikengassiindex/ikengassiindex.github.io/pages \\
       -f 'source[branch]=main' -f 'source[path]=/'

  Then verify:
     curl -sI https://ikengassiindex.github.io/ | head -1        # expect 200
     gh api repos/ikengassiindex/$ARCHIVE_NAME --jq .private     # expect true

  And re-point the five local clones, whose origin breaks on the rename:
     for r in be ee lt lv nl; do
       git -C ~/ikengassiindex-deploy-\$r remote set-url origin \\
         https://github.com/ikengassiindex/$ARCHIVE_NAME.git
     done

  ROLLBACK, if step 3 or 4 fails: rename back and restore visibility.
     gh repo edit ikengassiindex/$ARCHIVE_NAME --visibility public --accept-visibility-change-consequences
     gh repo rename ikengassiindex.github.io --repo ikengassiindex/$ARCHIVE_NAME

RUNBOOK
