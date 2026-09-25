# DESIGN — the public/private boundary, as a rule rather than a list

**Date** 24 September 2026
**Status** Measured and probed. This is the line B7 cuts along.

## The rule

> **What produces the scores is private. What checks them is public.**

A file list rots. A rule does not. Every question about where something belongs
is answered by asking which side of that sentence it falls on, and the answer
is checkable by anyone.

## Why this line and not "all of scripts/"

The original plan untracked `scripts/` wholesale and dropped `validate.yml`'s
provenance step, which it would have broken. Measuring first inverted it.

The two workflows that must stay public — `validate.yml` and
`validate-schemas.yml` — trigger on pushes to `*/ssi-data.json`, `doctrine/**`
and `*.html`. A workflow only fires on events in the repository that holds it,
so moving them private would not weaken them; it would stop them, silently.
Between them they invoke **eight** scripts under `scripts/`.

Seven are standalone — stdlib only, plus `jsonschema` for one. The eighth,
`check_cross_border.py`, imports `scripts.pipeline.utils.geo`, which imports
`..config` in four places and `scripts._ssi_data_shard_reader`.

So the cost of keeping every public gate working was measured rather than
assumed:

| | files |
|---|---:|
| Python under `scripts/` | 331 |
| kept public | **14** |
| untracked | **317** (95.8%) |

And the method is equally private either way:

| | goes private under BOTH options |
|---|---:|
| `scripts/pipeline/scoring/` | 6 files |
| `scripts/pipeline/enrichment/` | 6 files |
| `scripts/pipeline/ingestion/` | 164 files |

`geo.py` carries one scoring-related line in 583. `_ssi_data_shard_reader.py`
is pure I/O. `config.py` is 22 constants and a country list it reads from
`intelligence/countries.json`, which is already published.

The choice was therefore never "protect the method or keep a gate". It was
"keep a gate or remove eleven more files of plumbing". Eleven files of plumbing
do not buy the loss of a gate that catches substations placed outside their own
country's borders — the Austrian-class drift recorded in
`CROSS_BORDER_SUBSTATION_AUDIT_20260618.md`, where Canada's rejection log alone
runs to 52 MB. On every push that error is caught before it ships. On a weekly
schedule it is caught after a reader has already been served it.

## The fourteen that stay public

**Seven standalone validators**

    scripts/bump_cache_busters.py
    scripts/check_data_file_sizes.py
    scripts/check_inline_js_parse.py
    scripts/check_page_data_agreement.py
    scripts/check_provenance_citations_resolve.py
    scripts/generate_nav_data.py
    scripts/run_schema_validation.py

**The cross-border gate and its chain**

    scripts/check_cross_border.py
    scripts/pipeline/utils/geo.py
    scripts/pipeline/config.py
    scripts/_ssi_data_shard_reader.py

**Package markers, without which none of the above import**

    scripts/__init__.py
    scripts/pipeline/__init__.py
    scripts/pipeline/utils/__init__.py

## Probed, not asserted

A tree was built containing the public repo's data, schemas, intelligence and
doctrine, and **only these fourteen** under `scripts/`. Each validator was run
in it:

```
check_provenance_citations_resolve   exit 0   all 6 cited documents resolve
check_data_file_sizes                exit 0   all data files within threshold
generate_nav_data                    exit 0   regenerated nav.js (39 countries)
check_inline_js_parse                exit 0   failing pages: 0
check_page_data_agreement            exit 0
bump_cache_busters                   exit 0   585 cache-busters, 39 countries
run_schema_validation                exit 2   jsonschema absent in the PROBE VM
check_cross_border                   imports cross_border_audit from the kept
                                              geo.py; config.py resolves 39
```

The two that did not complete failed on packages missing from the probe VM, not
on the boundary. `validate.yml` installs both explicitly — `pip install
'shapely>=2.0'` at its line 106 — so CI has what the probe lacked.

## Why a public validator is an asset, not an exposure

The methodology is public and stays public, by operator instruction. A
validator that tests published data against declared rules is closer to
methodology than to working code: it is the show-your-work side of a foundation
instrument. Publishing it lets a third party verify the published data without
the pipeline that produced it. For an index whose purpose is supporting policy
decisions, that is worth more than the eleven files it costs.

## What this obliges at B7

1. `.gitignore` entries for everything untracked, so a careless `git add
   scripts/` cannot resurrect it. Removal alone is not enough — the same
   reasoning as `archive/` and `*/_v4.0.2.backup/` on 24 September.
2. `validate.yml` and `validate-schemas.yml` are **unchanged**. B6 as
   originally scoped — drop the provenance step — would have removed a working
   gate for no reason and is abandoned.
3. `automation/` is decided — see below. One file moves; the rest stays.

## Related

- `FINDING_the_pipeline_resolves_data_from_its_own_location.md`
- `DESIGN_the_public_private_split_measured.md`
- `CROSS_BORDER_SUBSTATION_AUDIT_20260618.md`

---

## `automation/` under the same rule

Five scripts, 1,751 lines, outside `scripts/` and therefore outside everything
above. The rule answers each of them, and it does not answer them all the same
way:

| file | what it writes | verdict |
|---|---|---|
| `runtime_audit.py` | its own report, to `audit/_logs` and `audit/_summary` | **public** — checker |
| `cross_validate_parity.py` | nothing at all | **public** — checker |
| `generate_parity_report.py` | `PARITY_REPORT.md`, checklists, `findings.json` | **public** — reporter |
| `send_audit_digest.py` | one temp file; emails a report | **public** — notifier, produces nothing, reads its secrets from the environment |
| `apply_parity_patches.py` | **`<clone>/<slug>/ssi-data.json`** | **private** — producer |

So **`automation/` stays public except `apply_parity_patches.py`**.

That one is unambiguous in its own docstring: *"Reads each of the 6 country
ssi-data.json files from the live site, applies the derivations spec'd in
automation/audit/patches/{slug}.md, and writes the patched JSON to
&lt;deploy_clone&gt;/&lt;slug&gt;/ssi-data.json."* It writes published score files.
Whatever else it is, it is on the producing side of the sentence.

The private `runtime-audit` workflow needs no change for this: `automation/` is
already in its sparse checkout of the public repo, and the one file that leaves
is not one it runs.

### A note the boundary does not resolve

The six countries that script patched — australia, chile, denmark, greece,
ireland, us — carry derivations applied once, by hand, documented in markdown,
with no pipeline that regenerates them. Its own docstring says so: *"a one-time
migration, NOT a recurring hotpatch … any future pipeline migration should
incorporate them at source."* That incorporation has not happened. Moving the
script private changes where it lives; it does not change that six countries'
published data contains values nothing re-derives. See
`FINDING_alert_components_is_derived_by_nothing.md`.
