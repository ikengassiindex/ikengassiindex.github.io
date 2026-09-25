# FINDING — the pipeline resolves data from its own location

**Date** 24 September 2026
**Occasion** Design B, before the `PUBLIC_REPO_TOKEN` is minted.
**Status** Measured. Changes the shape of the public/private split.

## The question

Design B moves the working code to a private repo (`ssi-pipeline`) and leaves
the data in the public one (`ikengassiindex.github.io`). Does the pipeline
survive that separation?

## The one line that answers it

`scripts/pipeline/config.py:12`

```python
DATA_DIR = REPO_ROOT  # country folders are at repo root
```

Code and data share a single root **by construction**. Separate the two repos
and every data path in the estate points at the private repo, where no country
folder exists.

## How widely

| measure | count |
|---|---|
| `REPO_ROOT` occurrences under `scripts/` | 429 |
| files carrying one | 120 |
| **independent definition sites** (each computed from `__file__`) | **110** |
| files that import it from `pipeline/config.py` | 6 |
| files referencing `ssi-data` | 168 |
| — of those, via `_ssi_data_shard_reader` / `ssi_data_sharding` | 21 |
| — of those, constructing the path themselves | **147** |

There is no single point. The 110 sites use eight different spellings of the
parent-walk (`parent.parent`, `parent.parent.parent`,
`parent.parent.parent.parent`, `parents[1]`, `PIPELINE_DIR.parent.parent`,
`_HERE.parent.parent.parent.parent.parent`, and two `os.path.dirname` chains).
A single-point override does not exist to be edited.

Only two environment overrides exist anywhere in the estate — `SSI_AUDIT_DIR`
(`pipeline/utils/audit_dir.py`) and `SSI_ESTATE`
(`check_provenance_citations_resolve.py`). Neither governs the data root.

## The artefact, read

Not inferred. `_ssi_data_shard_reader.py` was copied to a directory outside the
data repo and `load_ssi_data("france")` called three ways:

```
A. in place (today)
   REPO_ROOT -> .../ikengassiindex.github.io
   load_ssi_data(france) OK, substations = 168894

B. code relocated to a private repo (the split as designed)
   REPO_ROOT -> .../relocation_probe
   load_ssi_data(france) FAILED: FileNotFoundError
     .../relocation_probe/france/ssi-data.json

C. same relocated code, data tree present beneath it
   load_ssi_data(france) OK, substations = 168894 | sharded = True
```

B is the migration as written. C is the migration that works.

## What this rules out

**An `SSI_DATA_ROOT` indirection.** It would touch 110 definition sites across
every ingestion module, each needing its own spelling read and rewritten, with
the data estate as the blast radius and no test that distinguishes "resolved to
the right root" from "resolved to a root that happens to exist". Against Pin 3
(most efficient *and* most auditable) and against Pin 5 (a change lands before
the next one starts) — this is one change that cannot land incrementally.

## What run C says to do instead

Do not separate the trees at run time. Separate them at rest and reassemble
them in the private workflow:

1. `actions/checkout` the **public** repo at the workspace root — the data,
   `intelligence/`, `templates/`, `cross_border_tolerances.json`.
2. `actions/checkout` the **private** `ssi-pipeline` to a side path.
3. Place its `scripts/` at `$GITHUB_WORKSPACE/scripts/`.
4. Run. Every `REPO_ROOT` resolves exactly as it does today, because the tree
   is the tree it has always been.
5. Push the changed data paths back to the public repo with
   `PUBLIC_REPO_TOKEN` (Contents: read and write, that repo only).

Zero pipeline code changes. The check that it works is that the tree is
byte-identical to today's and the existing suite passes unchanged — which is a
check that reads the artefact rather than the intention.

## Consequence for the token

None. `PUBLIC_REPO_TOKEN` is still needed and still needs exactly
`Contents: read and write` on `ikengassiindex.github.io` alone. The finding
changes the workflow YAML, not the credential.

## Open, to confirm before step 3

Whether the extracted `ssi-pipeline` carries `scripts/` at its own root. The
extraction preserved paths, so it should; it has not been read, and it is not
connected as a folder yet. One `ls` settles it.

## Related

- `DESIGN_the_public_private_split_measured.md`
- `DOCTRINE_a_check_must_read_the_artefact.md`
- Pin 3, Pin 5, Pin 9
