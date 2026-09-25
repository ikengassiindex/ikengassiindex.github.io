# AMENDMENT — coefficients are declared as values, not as prose

**Element** `R3_C_mult.variables`, and the `variables` field in the taxonomy
**Decided by** operator
**Decided on** 2026-09-24
**Tier** E3
**Status** SIGNED and in force. Applied to `taxonomy.yaml` and
`judgement.yaml`, promulgated by the render that closes the series, at
`ssi-master-documents` `7e5a688`.

---

## 1. What is wrong

`judgement.yaml` is declared by the Bible to hold "every value a human decided,
under a provenance pin". It holds the decisions. It does not hold most of them
as values.

Measured 24 September 2026, across all 17 declared modifiers:

| how a variable is declared | count |
|---|---:|
| as a number | **1** |
| as a prose string | 33 |

R3's own coefficients:

```yaml
beta_pop:  "0.04, giving 2.4 percentage points of R3 per doubling of catchment..."
beta_vuln: "0.02"
s:         "sigmoid steepness, 4"
```

`s` does not begin with its number. Any check that scraped a value out of that
would work today and take the wrong number the first time a sentence was
reworded.

The consequence is visible in the register. Section 1 of `build()` checks
`range` and nothing else, because `range` is the only machine-readable
declaration in the file. R3's only row therefore compares doctrine's declared
bound with the engine's registry — both sides are the engine — and reports
`conforms: true` while 77.8 per cent of published records do not reproduce
under the declared formula.

`taxonomy.yaml` already asks for the remedy and has never had it. Its `variables`
field carries the note: *"every symbol defined, with units and domain."* No
symbol in the estate declares either.

## 2. What is amended

**No declared value moves.** `range` stays `[0.70, 1.30]`; `beta_pop` stays
0.04, `beta_vuln` 0.02, `s` 4. This is a re-expression of decisions already
taken on 21 September, not a re-decision. It is tiered E3 because the values it
re-expresses are E3 operator judgement; it introduces no new evidence and cites
none.

### 2.1 Taxonomy — the `variables` field admits two forms

```
- {name: variables, class: J, must: true,
   note: every symbol defined, with units and domain. A symbol may be declared
         as a string, or as a mapping carrying value, units, domain and note.
         Where the symbol IS a constant, the mapping form is required and
         `value` must be a number.}
```

### 2.2 Judgement — R3's variables take the mapping form

```yaml
      variables:
        catchment_population:
          units: persons
          domain: '[0, inf)'
          note: GHSL catchment population for the substation, measured per asset
        pop_med:
          units: persons
          domain: '(0, inf)'
          note: cohort median catchment population, re-derived each run by
            engine.derive_pop_med; NOT a frozen literal, so it carries no value here
        V_socio:
          units: dimensionless
          domain: '[0, 1]'
          note: socio-economic vulnerability; REGIONAL, 6-57 distinct values per
            country against 80-95 per cent distinct populations
        beta_pop:
          value: 0.04
          units: dimensionless, per log2 doubling of catchment population
          domain: '(0, 1)'
          note: giving 2.4 percentage points of R3 per doubling at the centre of
            the curve. Stated per doubling because 0.04 is not a quantity a
            reader can dispute
        beta_vuln:
          value: 0.02
          units: dimensionless
          domain: '(0, 1)'
          note: weight on the regional vulnerability term
        s:
          value: 4
          units: dimensionless
          domain: '(0, inf)'
          note: sigmoid steepness
```

Three symbols carry a value; three carry none, because they are measured or
derived per record rather than decided. A check reads `value` where it exists
and does not infer one where it does not.

### 2.3 The renderer promulgates it

`SSI_FOUNDATION_render2.py` currently writes each variable straight into a
markdown cell at two sites (≈1049 and ≈1386):

```python
w(f"| `{k}` | {v} | J |")
```

A mapping would render as a Python dict. Both sites gain a Value column and
handle either form; a symbol with no value renders "—". This is the whole
renderer change. Note that the field tuple at ≈1067 is fixed, which is why a
new sibling key was rejected: an undeclared field would sit in doctrine held and
never be promulgated.

## 3. Change-log entry

> **element** `R3_C_mult`
> **change** Coefficients re-expressed as declared values rather than prose.
> `variables` now admits a mapping carrying value, units, domain and note, and
> requires it where the symbol is a constant — which is what the taxonomy has
> asked for since it was written and has never had. No declared value moves:
> range stays [0.70, 1.30], beta_pop 0.04, beta_vuln 0.02, s 4. Measured cause:
> of roughly 34 declared variables across 17 modifiers, exactly one was stored
> as a number, so the register could check `range` and nothing else, and R3's
> only row compared doctrine's bound with the engine's registry — both sides the
> engine — reporting conformance while 77.8 per cent of published records did
> not reproduce under the declared formula. This amendment does not close that
> divergence; it makes it measurable.
> **decided_on** `'2026-09-24'`
> **tier** E3

## 4. What this does not do

It does not correct the published data. The R3 re-derivation across 622,104
records remains the separate measured operation the 21 September amendment
named, still pending.

It does not migrate the other 16 modifiers. After this amendment 1 of 17
declares values. The conformance check should report that coverage as a row, so
the remaining migration is visible in the register rather than remembered.

## 5. Obligations on signature

§8(5): a full re-render of every tier below, sentinels passing, rendered **once
per amendment series** and closed by a single commit naming every amendment it
promulgates. This amendment joins the series already open — `30a3cf7`, the
21 September R3 correction committed on 24 September with no render. Both are
discharged by one render and one commit.

§13 of the conformance generator, landed at `861cfd7`, will now check that this
entry carries a provenance pin and an evidence tier. It will fail until this
document is signed and `decided_on` is filled.

## 6. Related

- `FINDING_the_conformance_register_reads_the_engine_against_itself.md`
- `RECOMMENDATION_R3_C_mult_alpha_to_omega.md`
- `RESULT_the_39_country_r3_dry_run.md`
- `DESIGN_three_aspects_the_conformance_register_is_missing.md`
- Bible §8, §9; `SSI Index/DRAFT_conformance_r3_deployed_check.py`

---

## 7. Applied — what the register said afterwards

Landed at `ssi-master-documents` `7e5a688`, one commit, promulgating this
amendment and `30a3cf7` together and discharging the §8(5) debt the latter had
been carrying since 24 September 09:18.

Verified after the edit and before the render: no R3 field other than
`variables` changed, 17 modifiers before and after, the file's top-level keys
identical, `range` still `[0.70, 1.30]`, `beta_pop` 0.04, `beta_vuln` 0.02,
`s` 4. All 24 change-log entries carry a pin and a tier, so §13 passes.

The register went from 86 rows to 89, and now carries the chain that was
missing — published ⟷ engine ⟷ doctrine:

| row | observed | |
|---|---|---|
| R3 published reproduces under the engine | 0.0% of 14,287 sampled | BLOCKING |
| the engine's coefficients are the declared ones | carries every declared value | **green** |
| coefficients declared as values | 1 of 17 | DISCLOSED |
| T1 masters current with doctrine held | all 2 carry the digest | **green** |

The first row is red because the R3 write has not happened: every sampled
record lacks a `_r3_pop_med` anchor. It turns green when the 34 attributable
countries are written, which is what makes that write verifiable by the
instrument rather than by a session document. It required no signature and
could have existed three days ago.

The second is green, and is the answer this amendment made askable: the engine
does implement the coefficients doctrine declares.

The fourth is green on content rather than on mtime. §14 formerly compared
modification times, in a git working tree inside OneDrive, where both OneDrive
sync and `git checkout` rewrite mtimes without touching content — and it was a
snapshot that passed at render time by construction, which is precisely how
`30a3cf7` came to sit unrendered beneath a green row. The renderer now writes a
SHA-256 over `taxonomy.yaml` and `judgement.yaml` into each master's banner and
the check compares digests.

## 8. What is still owed

The sixteen remaining modifiers. Row three counts them, so this is a tracked
number and not a memory. Each is its own amendment, because `units` and
`domain` are declarations nobody has yet made for most symbols — migrating
them in a sweep would mean inventing thirty-three decisions in an afternoon.
