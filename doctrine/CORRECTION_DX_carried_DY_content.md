# CORRECTION — commit DX carries DY's content, and the landing script caused it

**Date** 25 September 2026
**Status** Recorded, not repaired by rewriting history. Both commits are pushed
to `main` and are public.
**Applies to** `4540569c` (DX) and `7874e0c1` (DY).

---

## What the git history says, and what is true

| commit | message says | actually contains |
|---|---|---|
| `4540569c` DX | *"the R7 cutover is arithmetically done and editorially not"* | **5 files, 943 lines**: the R7 result (186) and the sentinel addendum (33) — **and** `PLAN_OF_WORK.md` (333), `AUDIT_what_the_estate_already_holds_for_the_sixteen_metrics.md` (209) and `DECIDE_S1_needs_two_series_not_one.md` (182) |
| `7874e0c1` DY | *"the plan of work, audited before it was written down"* | **1 file, 1 line** — the E15 row added to the plan after DX had already taken it |

**724 of DX's 943 lines belong to DY.** DY's commit message describes work that
landed in DX. Neither message is a true description of its commit.

## The mechanism, and it was mine

`land_20260925_DX.sh` and `land_20260925_DY.sh` both ended with

    git add <explicit paths>       # Pin 7, correctly
    git commit -m "..."            # NO PATHSPEC

`git commit -m` with no pathspec commits **the whole index**, not the paths the
script staged. Pin 7 — *no `git add -u` sweeps, explicit paths* — was honoured
at the `add` and then discarded at the `commit`.

It only became visible because of a second defect. Both scripts contained

    git status --short --cached

which is not a valid invocation — `git status` has no `--cached` option, in any
version. On the operator's first run that line aborted each script **after**
`git add` had run. So when DX was re-run, the index already held DY's three
files, and DX's pathspec-less commit took them.

Two of my errors composing: an invented git option, and a commit that trusted
the index instead of naming its own paths.

## What is NOT being done

`main` is not rewritten. Both commits are pushed and public; a foundation
instrument does not quietly re-issue its own history to make a commit message
true. The record is corrected here instead, which is what §7.9 requires of a
marker that asserts something the artefact does not bear out.

The content itself is correct, complete and in the repository. Nothing is
missing and nothing is duplicated. What is wrong is the attribution of 724
lines to the wrong commit message.

## What is being done

Three repairs, all in DW:

1. **Pathspec commit.** Every landing script now ends `git commit -- "${PATHS[@]}"
   -m "..."`, so the commit can only ever contain the paths the script named,
   whatever the index holds.
2. **An index-cleanliness gate.** A landing script refuses to run if the index
   is already non-empty, prints what is staged, and says how to clear it.
3. **The invalid option is gone** — `git diff --cached --name-status` in its
   place.

4. **Options before the separator.** The first attempt at repair 1 was written
   `git commit -- "${PATHS[@]}" -F -`, which fails: everything after `--` is a
   pathspec, so git looked for files named `-F` and `-`. The correct form is
   `git commit -F - -- "${PATHS[@]}"`.

These four become the landing-script template. A landing script that does not
carry all four is not to be run.

## How the template was finally verified

Not by reasoning about it. Four separate defects reached the operator's
terminal in one session — an invented `git status --cached`, a pathspec-less
commit, a `$VARIABLE` expanded inside a `-m "..."` string under `set -u`, and
options placed after `--`. Every one is in the *commit step*, which is the one
step a landing script's gates never exercise, because Pin 6 reserves every git
write to the operator.

The repair is not more care. It is a throwaway repository, in an environment
that touches nothing, where the exact command shape is run before it ships:

    rm -rf /tmp/shapetest && mkdir -p /tmp/shapetest && cd /tmp/shapetest
    git init -q . && git config user.email t@t && git config user.name t
    mkdir -p doctrine scripts
    echo a > doctrine/one.md; echo b > scripts/two.py; echo c > foreign.txt
    git add doctrine/one.md scripts/two.py foreign.txt
    PATHS=(doctrine/one.md scripts/two.py)
    git commit -F - -- "${PATHS[@]}" <<'MSG'
    title

    body mentioning $SSI_GIS_DIR and `backticks` and $(date) literally
    MSG
    git show --stat --oneline HEAD     # only the two named paths
    git diff --cached --name-only      # foreign.txt, still staged, not committed
    git log -1 --format=%B             # the $ and backticks stored verbatim

All three assertions hold. **A landing script's commit line is tested in a
scratch repository before the script is handed over.** That is the rule this
episode produces, and it costs one minute.

## The rule this produces

> **A commit names its own paths. It does not inherit the index.**

Pin 7 is about what a commit contains. Staging explicitly and then committing
the index satisfies the letter of it and none of the intent — a crashed earlier
run is enough to defeat it, and that is exactly what happened.
