# DESIGN — the public/private split, measured rather than assumed

Decided 24 September 2026. Supersedes the approach sketched in
`NOTE_the_workflows_must_move_before_the_untrack.md` §4, which assumed the
data validators had to move private and cost two credentials to do it.

They do not. Measuring what they actually import changed the design.

---

## 1. What the measurement found

The two push-triggered validation workflows invoke eight scripts. **None of
them references `compute_r3`, `compute_r_median`, `monte_carlo`,
`MODIFIER_REGISTRY` or `score_substation`.** One imports from the pipeline at
all — `check_cross_border.py` needs `pipeline/utils/geo.py`, a geometry
helper.

The full import closure of the seven that stay is **10 Python files**, and it
touches nothing in `scoring/`, `ingestion/` or `enrichment/`. All three
`__init__.py` on the path are empty, so nothing leaks through the package.

The eighth, `check_provenance_citations_resolve.py`, reads `doctrine/` and
follows it private.

## 2. The split

**Stays public — 13 files, from 396.**

    scripts/check_cross_border.py
    scripts/check_data_file_sizes.py
    scripts/bump_cache_busters.py
    scripts/check_inline_js_parse.py
    scripts/check_page_data_agreement.py
    scripts/generate_nav_data.py
    scripts/run_schema_validation.py
    scripts/_ssi_data_shard_reader.py
    scripts/pipeline/utils/geo.py
    scripts/pipeline/utils/ssi_data_sharding.py
    scripts/__init__.py  scripts/pipeline/__init__.py
    scripts/pipeline/utils/__init__.py

plus `schemas/` (4 files) and `intelligence/`, which the site needs anyway.

**Goes private** — the other 633 tracked files under `scripts/`, plus
`tests/` (44), `doctrine/` (68), `data/` (17), `audit/` (2), `CLAUDE.md`,
`FIX_SLUG_LEAKAGE.py` and 18 root `.md` audit reports. Already pushed to
`ikengassiindex/ssi-pipeline` with history — 415 commits, 797 files, 204 MB.

## 3. Why this is better than moving the validators too

The rejected design had a thin public workflow `repository_dispatch` to the
private repo, which would post a commit status back. It needed two
fine-grained tokens, one of them a secret stored in a PUBLIC repository, and
its failure mode was a dispatch that quietly does not arrive — the same
silent-failure class that bit four times on 24 September alone (the R7
cutover test, the shard threshold test, `test.yml`'s vanishing trigger, and
the systemic layer's adapter contract).

This design has no token for the validation half, no secret in a public repo,
and nothing new to fail. Inline validation on push continues to work exactly
as it does today, because the code it runs never moves.

## 4. What stays public, stated honestly

Roughly 2,700 lines that reveal **what is checked** — cross-border
containment, file-size limits, page/data agreement, schema shape, cache-bust
consistency. They reveal the INVARIANTS, not the method: no formula, no
weight, no modifier, no Monte Carlo, no ingestion source.

That is a deliberate asset rather than a residue. Publishing what you check
is a credibility claim, and it is the half of the work that supports the
reproducibility argument the journal programme rests on. The operator's
stated aim was to protect the method and the inputs; both go private.

## 5. Workflows

| workflow | after |
|---|---|
| `validate-schemas.yml` | **stays public, unchanged** — all 5 scripts are in the keep-list |
| `validate.yml` | **stays public**, minus its provenance step, which follows `doctrine/` private |
| `test.yml` | private, triggers on private pushes |
| `runtime-audit.yml` | private |
| `pipeline-enrichment.yml` | private, pushes results to public |
| `monthly-refresh.yml` | private, pushes results to public |
| `esg-refresh.yml` | private, pushes results to public |

Only the last three need a credential, and only because they write results
back. Pin 9: the operator creates it.

## 6. Order, and why the untrack is still last

  1. Connect the private repo as a working folder; move the extract from
     `~/_ssi_pipeline_extract_20260924` to a permanent home.
  2. Create the write token (Pin 9) and set it as a secret on `ssi-pipeline`.
  3. Land the four private workflows; **verify one scheduled run and one
     push-triggered run actually succeed**, reading the run, not the config.
  4. Amend `validate.yml` to drop the provenance step.
  5. Only then untrack, with a run-time guard that refuses unless the private
     repo demonstrably holds every path being removed — the pattern
     `land_20260924_BR.sh` used for the archives.

Step 3 is the gate. A workflow that is configured is not a workflow that
runs, and this estate has four instances this month of a green check that
never read the artefact it claimed to check.

## 7. Not yet decided

Whether the private repo should drop its copies of the 13 public files, or
carry them and risk divergence. Carrying them is the safer default until the
migration is verified; a test that the two copies are byte-identical would
settle it cheaply.
