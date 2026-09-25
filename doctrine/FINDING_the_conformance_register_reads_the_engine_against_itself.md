# FINDING — the conformance register reads the engine against itself

**Date** 24 September 2026
**Occasion** Establishing which repository holds doctrine, before the
public/private split lands workflows.
**Status** Measured. Two findings, one about the register and one about B7.

## Why the read happened

`ssi-master-documents` describes itself as holding "doctrine … audit chain for
SSI_FOUNDATION_BIBLE §8". The public repo holds a `doctrine/` directory of 75
files. Pin 16 says master documents land before the site repo. Before writing
workflows that push to the public repo it had to be settled which of the two is
the constitutional record.

## It is not a conflict — the word carries two meanings

The Bible settles it directly, under *Doctrine promulgated versus doctrine
held*:

> The rendered `.md` and `.html` files are doctrine **issued**. They are never
> hand-edited; an edited rendering has lost its provenance and is void.

Doctrine **held** is exactly two files — `SSI_FOUNDATION_taxonomy.yaml` and
`SSI_FOUNDATION_judgement.yaml`. §8: doctrine is amended by changing those
"and by no other means."

The public `doctrine/` directory is neither held nor issued doctrine. It is the
working record — findings, designs, results, recommendations. Nothing in it
declares a value. No misfiling has occurred and none of it needs to move.

## First finding — the constitution cites the public repository

`judgement.yaml`, R3_C_mult entry:

```
document: doctrine/RECOMMENDATION_R3_C_mult_alpha_to_omega.md
```

That path resolves, in the **public** repo. A private constitutional instrument
depends on a public path. One citation today, so it is cheap; but it is a
constraint on the untrack step, which must not move or remove `doctrine/`
without re-pointing it. Recorded here because the constraint is invisible from
either repository alone.

## Second finding — the register's R3 row proves nothing

The register carries 86 elements: 45 conforming, 41 diverging, 8 BLOCKING,
6 MATERIAL, 27 DISCLOSED, 11 DEFERRED. Its only R3 row:

```
element: R3_C_mult   aspect: range
declared: [0.7, 1.3]   observed: [0.7, 1.3]   conforms: true
severity: DISCLOSED   owner: engine
```

`observed` is not a measurement of the published estate. `build()` in
`SSI_FOUNDATION_conformance.py` derives it from the modifier registry:

```python
for mid, meta in sorted(m["modifiers"].items()):
    jm  = (jud.get("modifiers") or {}).get(mid) or {}
    dec = jm.get("range")
    obs = meta.get("range")          # the registry, not the record
```

The row's own failure note says so: *"declared bound differs from the
registry"*. Doctrine's declared bound is compared with the engine's declared
bound. Both sides are the engine. No published record is opened, so the row
cannot go red however wrong the published data is.

### What the row would say if it read the artefact

Measured 23 September, `RESULT_the_39_country_r3_dry_run.md`:

| | countries | records | moved | bands vs published |
|---|---:|---:|---:|---:|
| attributable | 33 | 219,474 | 131,621 | 31,255 (14.2%) |
| stale-baseline | 5 | 398,599 | 349,155 | 96,226 (24.1%) |
| **total** | **38** | **618,073** | **480,776 (77.8%)** | **127,481 (20.6%)** |

77.8 per cent of published records do not carry the R3 the declared formula
produces. §9 requires the register to carry "every divergence between doctrine
and deployment". This is the largest known divergence in the estate and the
register reports the element as conforming.

It is not a defect of declaration. The 21 September amendment states on its
face: *"NOT YET APPLIED to published data — this settles the declaration; the
re-derivation across 622,104 records is a separate measured operation."*
Doctrine was amended first and the code followed, exactly as §8 requires. The
gap is that the interval between declaration and application — three days so
far, and the whole R3 write still ahead — is invisible in the instrument whose
purpose is to make it visible.

## The generator can already do this

Section 1 of `build()` is code-against-code for every modifier bound. Section 2
is not: the R7 rows read the published product and report *"reproduces on X% of
sampled assets"*. The register is not architecturally blind — R7 has an
artefact check and R3 has none.

This is a **fourth missing aspect**, not a verdict on the instrument.
`DESIGN_three_aspects_the_conformance_register_is_missing.md` §1.3 already
establishes that the register's two methods — reproduction and correlation —
are the correct two, and that it was using reproduction correctly on
18 September. It names three missing aspects: consumer reachability, variance
provenance, and marker against instrument range. None of the three is this one.
The register is the right instrument, applied to R3 in the one place where it
happens to read the engine rather than the record.

So the correction is not a row added by hand. The register is generated, and a
hand-edited rendering is void by the Bible's own words. The correction is a
check in `build()` that opens published records, in the shape section 2 already
uses.

A draft of that check is at
`SSI Index/DRAFT_conformance_r3_deployed_check.py`. It is a proposal, not an
amendment: adding it changes an operator-signed instrument and obliges a
re-render under §8.5.

## Third finding — the draft refused, and it was right to

The draft was run against the real `judgement.yaml` before being proposed. It
returned `None` and would have emitted a MATERIAL row rather than a measurement.

The reason is that R3's coefficients are not stored as values:

```
beta_pop  : "0.04, giving 2.4 percentage points of R3 per doubling of catchment..."
beta_vuln : "0.02"
s         : "sigmoid steepness, 4"
```

All three are strings. `s` does not even begin with its number. A check that
scraped a number out of that prose would work today and silently pick the wrong
one the first time a sentence was reworded, so the draft refuses instead.

This is not an R3 quirk. Across all 17 declared modifiers, of roughly 34
declared variables **exactly one is stored as a number**:

| declaration style | count |
|---|---|
| numeric | 1 |
| prose string | 33 |

The Bible says `judgement.yaml` holds "every value a human decided, under a
provenance pin". It holds the decisions; it does not hold most of them as
values. This is why section 1 of `build()` checks `range` and nothing else —
`range` is a list of numbers, and almost nothing else in the file is machine
-readable. The register is not narrow by choice. It is narrow because the
declaration it reads from is prose.

That makes the R3 conformance check dependent on a prior amendment: R3's
coefficients need machine-readable fields, with the present prose retained
beside them as commentary rather than replaced by them. That is a small
amendment and it unblocks a general capability, not one row.

Order, therefore: amend the declaration so coefficients are values; then the
check; then the render that closes the series. Three steps, in that order, none
of which can be skipped by editing a rendering.

## Fifth instance

This session has now found five checks that read code where they should read
the artefact: the R7 cutover test, the shard threshold test, `test.yml`'s
vanishing trigger, the systemic layer adapter contract, and this one. The first
four were in the test suite. This one is in the constitutional machinery — the
instrument the others are supposed to answer to.

See `DOCTRINE_a_check_must_read_the_artefact.md`.

## Answered — the debt is open, and the detector for it is uncommitted

`30a3cf7`, 24 September 09:18, amended `judgement.yaml` alone: one file,
+58/-11, no render. The last committed render is `7ad6bff`, 21 September 13:29,
whose message calls itself "the single re-render closing the 21 September
amendment series". An amendment has landed after the render that closed its
series, with nothing following. §8.5: a blocking gap.

`git status` shows why it was not caught. Eight files are modified and
uncommitted — the seven rendered masters, and `SSI_FOUNDATION_conformance.py`
itself. The uncommitted generator change, dated 18 September in its own
comments, adds two sections:

- **§13, amendment discipline** — asserts Constitution §8(2) and §8(3) against
  `change_log`: every amendment carries a provenance pin and declares an
  evidence tier. It found two unpinned, untiered entries on the day it was
  written. The register now reports all 23 pinned and tiered, so the check
  worked and someone acted on it.
- **§14, doctrine issued against doctrine held** — asserts §8(5) by comparing
  the mtime of `judgement.yaml`/`taxonomy.yaml` against the rendered masters.

**§14 is exactly the render-debt detector this finding needed.** It was written
six days ago, it works, and it has never been committed. The estate had the
instrument before the session that went looking for it — the fourth time that
has happened here; there is a doctrine file named for the pattern.

### Why it reports green

The on-disk register carries the row:

```
T1 masters · doctrine issued is current with doctrine held
observed: all 2 rendered at or after doctrine held    conforms: true
```

The register was generated 21 September 19:51. At that moment the masters
(13:29) were newer than doctrine held (13:02), so green was correct. The
22 September render at 05:14 and the `judgement.yaml` edit at 05:16 came after,
and nothing regenerated the register. A snapshot check reports the state of its
last run, not the present — so it passes at render time by construction and
decays silently thereafter.

### And mtime is the wrong signal in this repository

`master documents` is a git repository inside OneDrive. Both OneDrive sync and
`git checkout` rewrite mtimes without touching content, so §14 can pass on a
stale render and fail on a current one. The check is cheap and its comment says
it chose mtime to avoid a re-entrant render — but the cheaper correct form is a
content hash: record the SHA-256 of `judgement.yaml` and `taxonomy.yaml` in the
render's own header and compare digests. No re-render, no dependence on a
filesystem attribute two systems rewrite.

## Related

- `RESULT_the_39_country_r3_dry_run.md`
- `RECOMMENDATION_R3_C_mult_alpha_to_omega.md`
- `FINDING_the_pipeline_resolves_data_from_its_own_location.md`
- `DESIGN_three_aspects_the_conformance_register_is_missing.md`
- `DESIGN_the_public_private_split_measured.md`
- Bible §1, §8, §9; Pin 16
