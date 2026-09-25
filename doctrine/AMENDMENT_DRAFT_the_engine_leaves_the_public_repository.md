# AMENDMENT — the engine leaves the public repository

**Amends** `DESIGN_the_public_private_boundary.md` (landed in EB, `71a1bd98`)
**Decided by** operator
**Decided on** 2026-09-25
**Tier** E1 — every figure measured against the repository itself
**Status** SIGNED and in force. Operator, 25 September 2026: *"yes we sign and
proceed with option C."* §4 (the engine is private) and §2's Option C are
pinned. Execution is `land_20260925_EE.sh`; this document is the authority it
cites.

---

## 0. The requirement, stated plainly

**The scoring engine must not be available to the public.**

That is the requirement. It is not "the working tree should be tidy" and it is
not "future additions should be private". An earlier draft of this amendment
proposed a forward-looking boundary — private from a date, history
acknowledged. **That draft is withdrawn: it does not meet the requirement it
was written to serve.**

## 1. Why B2, as designed, cannot meet it

`DESIGN_the_public_private_boundary.md` specifies untracking. Untracking
removes a file from `HEAD` and leaves it in history. Tested against this
repository's own precedent, `0946cdbe` — *"untrack 1.75 GB the site publishes
and references nowhere"*:

    git cat-file -e "0946cdbe^:<path>"    →    the object still exists

Measured on the engine specifically:

| | |
|---|---|
| first public commit | `47478e16`, **17 March 2026** |
| commits since | **1,088** of 1,713 — 63% of this repository's history |
| public commits touching `engine.py` | 16 |
| also carrying engine files | `deploy-be`, `-ee`, `-lt`, `-lv`, `-nl` — 2 files each |
| already private | `ssi-pipeline` holds all six engine files |

The engine has been publicly readable for six months. `git rm --cached`
changes nothing about that.

## 2. The three options, and what each actually costs

### A — rewrite history

`git filter-repo --path scripts/pipeline/scoring --invert-paths`, force-push,
then a GitHub Support request to purge unreachable objects, across six
repositories.

It rewrites **1,088 of 1,713 commits**, so every commit SHA after 17 March
changes — which is every SHA this estate's doctrine cites, `cced85da`,
`7e5a688`, `8cf51464`, `124b1624`, and every commit of the present series.
§7.6 asks that no citation go unread; a rewrite leaves citations whose target
no longer exists.

**The history is the audit trail. It is the evidence, not a liability to be
cleaned.** Rejected.

### B — delete and recreate the public repository

Total loss of public history plus downtime. Strictly worse than C. Rejected.

### C — make the current repository private; publish a fresh public one

Rename the existing repository, set it private — one settings change, and
1,713 commits become invisible to the public immediately — then create a new
`ikengassiindex.github.io` containing only the public tree, with a clean
initial history.

    forks 0    network 0    subscribers 0    private false

Measured 25 September 2026 via `gh api`. **There is no fork network**, so
nothing survives elsewhere on GitHub once the origin is private. No Support
ticket, no rewrite, no broken SHA — the old repository keeps its full history
and remains readable inside Ikenga.

**C is the recommendation.**

## 3. What C does NOT achieve, said rather than implied

Anything already cloned by a third party cannot be retracted. Two external
archives were the open question, and one is now measured.

**Software Heritage — checked, 25 September 2026, and this estate is not in
it.**

    GET /api/1/origin/search/ikengassiindex/?limit=20   →   []

Software Heritage systematically ingests public GitHub repositories, so this
was the single largest residual. The search is a case-insensitive substring
match over origin URLs and returns an empty array: **no `ikengassiindex`
origin has ever been archived there**, main repository or deploy mirror.

The Wayback Machine may separately hold the *rendered site*, which is intended
to be public and carries no source. Not checked, and not material.

Combined with `forks 0 · network 0 · subscribers 0`, the exposure surface after
C is: private clones taken by someone who found the repository, of which there
is no evidence and no way to obtain any.

The honest claim after C is therefore **"our copy is removed, no copy survives
on GitHub, and the public archives do not hold it"** — not "the engine was
never public", which would be false. §7.9.

## 4. The engine is private

`scripts/pipeline/scoring/engine.py` is **1,144 lines and 26 functions**:
`_nearest_pd_correlation` with an eigenvalue floor of `1e-3`, `derive_mc_seed`,
a Gaussian-copula `monte_carlo`, `_soft_clip_upper_vectorized`,
`scoring_fingerprint_describe`. Not a constants file.

An earlier draft argued it holds only constants already published and should
therefore stay public. **That was false**, and the artefact refutes it twice
over:

1. `france/methodology.html` mentions `Monte Carlo` four times, `soft_clip`
   five, `copula` twice. It **names** them. Naming is not specifying.
2. `AMENDMENT_DRAFT_coefficients_declared_as_values.md` §1 records that the
   conformance register *"reports `conforms: true` while **77.8 per cent of
   published records do not reproduce under the declared formula**."* If the
   published method were a complete specification that figure would be zero.

And it inverts the auditability argument the earlier draft rested on:
publishing the engine lets the index be *reproduced* while its specification
stays 77.8 per cent short. That is re-execution, not audit.

> **Keeping the engine private forces the published specification to become
> complete enough to reproduce the numbers. Publishing it removes the pressure
> to ever finish it.**

The rule also survives intact. The design's own words: *"A file list rots. A
rule does not."* The rule is **what produces the scores is private**. The
engine produces the scores; an exception for it would have left the rule
reading "except the thing that produces the scores".

### 4.5 What it costs, measured by AST rather than grep

**17 of 46** test files import `pipeline.scoring`; **26 of 46** import something
under `pipeline`. Four checkers import it: `check_master_equation_closure.py`,
`check_r7_cutover_complete.py`, `check_band_rule_per_country.py`,
`check_r_base_derives_from_components.py`.

**`tests/conftest.py` is NOT among them.** An earlier count said it was, and
that it would take the suite's fixtures private with the engine. It imports
`pathlib`, `pytest` and `sys`, and nothing else — the match was on a *comment*
at line 15 describing what tests do. The fixtures stay public, so the public
repository keeps a working pytest harness for every test that does not touch
the engine.

That is a relocation, not a loss. A test that verifies the engine is Ikenga's
internal quality control. What an external auditor uses is the set that reads
*published data against declared rules* — `check_data_file_sizes`,
`check_page_data_agreement`, `check_provenance_citations_resolve`,
`check_cross_border`, `run_schema_validation` — and every one stays public and
stays working, as §6 probes.

## 5. The private set is a CLOSURE, not a list of directories

This is the probe's most useful finding, and it was a defect in the first
attempt at this amendment.

Defining private as three directories plus the deprecated files left **33
public files importing private modules**. The first check reported zero,
because `grep -r` does not follow symlinks and the candidate tree was a symlink
farm — a clean result from a check that never read the files, the same defect
class as `FINDING_the_gate_that_passed_by_not_running.md`. Rerun with `-R` it
returned 33.

Recomputed as a closure — the seed, plus anything importing it, iterated to a
fixed point — it converges in three passes:

    pass 1  +51      pass 2  +3      pass 3  +1
    private 270      public 1,802     of 2,072 tracked

The 55 additions beyond the seed are almost all producers that belong private
by the rule — `normalise_bands_per_country.py`, `ssi_dedupe_substations.py`,
`refresh_fleet_summary.py`, `pipeline/run.py`, `pipeline/fetch_data.py`, the
derivation scripts — plus the four checkers that verify the engine and travel
with it.

**A boundary defined by file list is wrong by construction. It must be defined
by closure and recomputed whenever an import changes.**

### 5.1 It is now an instrument, not a measurement

`scripts/ssi_public_private_closure.py` computes the closure and verifies a
tree against it. It reads imports with `ast.parse`, not `grep`, because grep
misled this work three separate times on one afternoon:

| what happened | the true answer |
|---|---|
| `grep -r` does not follow symlinks; the candidate tree was a symlink farm | 0 reported, **33** actual |
| an unanchored pattern matched a **comment** in `tests/conftest.py` | conftest imports `pathlib`, `pytest`, `sys` — **not** the engine |
| `from scripts.pipeline` missed the `from pipeline.x` spelling | 21 reported, **26** actual |

`ast.parse` reads the imports the interpreter would. It cannot match a comment,
a docstring or a string literal, and it does not care about symlinks. The AST
closure returns **the same 270 / 1,802** as the regex closure did — so the
boundary was right and only the checks of it were wrong, which is the more
dangerous of the two.

    python3 scripts/ssi_public_private_closure.py --build
    →  built a candidate tree · public N of N present · PRIVATE present 0
       ✓ matches the closure · (tree removed)

`--build` constructs the candidate tree itself, verifies it and removes it, so
the strong check runs on any machine. It replaced `--verify ~/cand`, which
depended on a tree that existed only on the machine that built it — everywhere
else the gate silently fell back to the weaker internal-consistency check. **A
check that is strong in one environment and weak in another is two checks
wearing one name.** Fourth instance today of a path resolved from the author's
own environment; see `scripts/_ssi_gis_dir.py`.

The counts in this document are those of the commit that landed it. They move
as the repository moves — that is the point of an instrument over a list.

## 6. The probe: built and run, not asserted

A candidate public tree of 1,802 files was built and every read-only validator
run inside it.

    public files importing the private tranche       0   (verified with -R)
    check_required_files                        exit 0
    check_page_data_agreement                   exit 0
    check_inline_js_parse                       exit 0   failing pages: 0
    check_data_file_sizes                       exit 0   all within threshold
    check_provenance_citations_resolve          exit 0   all 6 resolve
    check_cross_border.py --all --strict        exit 0
    check_cross_border_v2.py czechia --strict   exit 0
    check_cross_border_v2.py italy   --strict   exit 1   ← still blocks, correctly
    preflight.sh                                parses; 0 of its 13 checkers went private

`run_schema_validation` exits 2 on `jsonschema` absent **in the probe VM**, not
on the boundary — `validate-schemas.yml:50` installs it. The same exception the
design's own probe recorded.

### 6.1 The published site is unaffected

Every reference in all 520 HTML pages was resolved against the candidate tree:
**4,290 references checked, 0 landing in the private tranche.**

161 do not resolve — and resolve identically badly today, before any split, so
the split adds none of them. Three classes, recorded as a plan item and not
addressed here: 39 links to `reference-docs/` formula constructs that live in
the OneDrive estate rather than the repository; 39 directory-style
`../methodology/` links; 83 relative paths inside the shared
`esg-report-shared.html` template.

**Pin 1 is not engaged.** 1,802 files move verbatim; not a line of layout is
edited. The design of the site is a property of its files, and the files do not
change.

## 7. Executing C — the operational risks, each with its mitigation

| risk | why it bites | mitigation |
|---|---|---|
| `.nojekyll` omitted | present, 0 bytes. Without it Pages runs Jekyll and silently breaks every path with a leading underscore | carried in the public tree; asserted by the switch gate |
| Pages source not re-set | not inherited by a new repository | set branch and folder before the first push is announced |
| a file misclassified | one missing asset breaks a page | §6.1's 4,290-reference resolution, re-run against the final tree |
| downtime | **no CNAME** — the site is served at `ikengassiindex.github.io`, so the repository *name* is load-bearing, and there is a window between rename and first successful Pages build | prepare the full tree first; rename, create and push in immediate succession |

### 7.1 The downtime can be removed entirely

Put the site on a custom domain **first** — a `CNAME` file plus a DNS record,
`index.ikenga.eu` or similar. Once served by domain rather than repository
name, the name stops mattering and the swap is invisible to every reader. It
changes the public URL, which is a separate decision, and it converts C from
"a window of 404s" into "no observable change".

## 8. There is exactly ONE public repository

An earlier draft of this section recorded five deploy repositories as unmeasured
exposure. Measured, they are not repositories at all.

    deploy-be   remote = github.com/ikengassiindex/ikengassiindex.github.io.git
    deploy-ee   remote = same
    deploy-lt   remote = same
    deploy-lv   remote = same
    deploy-nl   remote = same

`gh api repos/ikengassiindex/ikengassiindex-deploy-*` returns **404 on all
five** — correctly, because they do not exist. They are **local working clones
of this same repository**, taken at different times: 2,005 / 2,141 / 2,150 /
2,141 / 2,018 files tracked against this clone's 2,072, and 2 engine files each
rather than 6 because they predate the other four.

**C's scope is one repository.** Nothing else on GitHub carries the engine.

### 8.1 What that means operationally

Those five clones hold their own copies of the history on the operator's own
machine, which is not exposure. But a rename breaks their `origin` URL. After
the switch each needs `git remote set-url origin <new url>`, or removing if
they are disposable — they appear to be leftovers of per-country deployment
work. Recorded so the rename does not silently strand five checkouts.

## 9. What is NOT in this amendment

The GISCO download step that would let the public workflow run
`check_cross_border_v2.py` instead of v1. Operator decision, 25 September: the
download cannot be added until an authorisation request to
`ssi_index@ikenga.eu` is approved by reply. Plan item E19.

## Re-derive

    gh api repos/ikengassiindex/ikengassiindex.github.io --jq '{forks:.forks_count,network:.network_count}'
    git log --reverse --format="%h %ad" --date=short -- scripts/pipeline/scoring/engine.py | head -1
    git rev-list --count 47478e16..HEAD
    grep -RlE "(from|import)[[:space:]]+(scripts\.)?pipeline\.(scoring|enrichment|ingestion)" --include=*.py ~/cand
