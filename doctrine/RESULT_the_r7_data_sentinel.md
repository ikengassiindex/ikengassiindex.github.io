# RESULT — the R7 data sentinel, and what it found on its first run

**Date** 17 September 2026
**Instrument** `scripts/check_r7_cutover_complete.py` (new; read-only).
**Measured on** the deployed tree, all 39 countries, **622,104 records, every
shard**. Full census.
**Status** measurement only. Nothing published was changed.
**Plan step** 2 of `PLAN_r7_cutover.md`.

---

## Why it exists

`tests/test_r7_cyber_v2_construct.py::TestPostCutoverInvariants` asserts
`versions.json`, `intelligence/edition-config.json`, the registry's `retired`
flags and the Convention #79 shard thresholds. Every assertion reads code or
config; none reads a substation record. Run in the cloud container on the current
tree: **95 passed in 0.28 s**, with the cutover not done. The suite cannot see the
defect. This is the missing half, per
`DOCTRINE_a_check_must_read_the_artefact.md`.

Acceptance criterion for the sentinel itself: **it must be RED now.** A check that
passes on both sides of a change has not tested the change.

## It is red, as required

    A  _r7_cyber_v1_retired True         0     False  619,522     absent  2,582
    B  modifiers.R7_cyber present  543,546     (must be 0 post-cutover)
       modifiers.R7_cyber_v2       619,522
       v2 with no v1 beneath it     78,558

The 2,582 records with the marker absent are, exactly, Sweden's 2,582 records
that carry no v2.

## C — the test that was worth building

Rather than asking "does `mult_product` reproduce", the check tests **four**
hypotheses per record and reports degenerate matches honestly instead of
crediting the first hit:

    published mult_product fits            records      share
    none                                   397,909      64.0%
    ambiguous(neither | v1_only)            83,556      13.4%
    v2_only                                 81,327      13.1%
    v1_only                                 56,302       9.1%
    ambiguous(neither | v2_only)             2,582       0.4%
    neither                                    199       0.0%
    ambiguous(v1_only | v2_only)                93       0.0%
    both                                        84       0.0%
    ambiguous(both | v2_only)                   22       0.0%

`v1_only` and `neither` coincide wherever v1 is exactly 1.0, which is why the
ambiguous buckets are large; they are reported rather than collapsed.

### Finding 1 — on 64% of the estate the published product reproduces from nothing

**397,852** of the 397,909 sit in five countries — france 168,530, germany
107,832, us 73,673, italy 41,655, japan 6,162. The remaining **57** are scattered
across ten others (new-zealand 31, poland 8, belgium 4, netherlands 3,
slovenia 3, estonia 2, ireland 2, latvia 2, finland 1, iceland 1) and are a
separate, small question.

Those five countries hold 398,599 records in total, so 747 of their records DO
fit a hypothesis. Ratio of published `mult_product` to the chain recomputed from
the record's own modifiers, over each country's full population:

    country     n          published / chain(v1)        published / chain(v2)
    france      168,894    med 1.008761  sd 0.047681    med 0.994650  sd 0.038492
    germany     108,016    med 1.009551  sd 0.051896    med 0.995488  sd 0.042669
    us           73,859    med 1.008466  sd 0.046803    med 0.989561  sd 0.037471
    italy        41,662    med 1.100368  sd 0.047737    med 1.087193  sd 0.037717
    japan         6,168    med 1.078997  sd 0.050051    med 1.067268  sd 0.040391
    sweden        3,774    med 0.986893  sd 0.012048    med 1.000001  sd 0.000023
    uk           59,744    med 1.017990  sd 0.009295    med 1.000000  sd 0.000026

Italy's 1.1004 reproduces the figure already recorded in
`RESULT_the_three_R7_cutover_residuals.md` from an independent measurement.

The standard deviation is the point: ~0.047 is a DISTRIBUTION, not a scalar
offset. These five countries' published `mult_product` predates their current
modifier values, per record and by differing amounts. This is not an R7 question
at all — no cyber hypothesis fits because the mismatch is elsewhere in the chain.

**This changes plan steps 4 and 5.** On 398,599 records — 64.1% of the estate —
the cutover's effect **cannot be computed as a delta**, because there is no
reproducible baseline to apply a delta to. Those countries need the Phase ζ
rescore, not an arithmetic adjustment. Any band-change figure quoted for them
without a rescore is measuring against a baseline that does not reproduce.

UK and Sweden, by contrast, fit v2 at 1.000000 with sd ~2.5e-5 — clean, and proof
the reproduction method itself is sound.

### Finding 2 — a claim written into production code that the artefact refutes

`scripts/pipeline/scoring/modifier_registry.py::compute_modifier_terms` carries,
as a comment explaining the retired-skip guard:

> "…a record carrying both R7_cyber and R7_cyber_v2 had the cyber modifier
> applied twice. **Sweden's published scores carry that double-count today**;
> every other v4.2-cohort country would have acquired it on its next re-score."

Measured against the published records:

- **Zero** Sweden records fit the `both` hypothesis.
- Sweden's published `mult_product` ÷ chain(v2) = **1.000001, sd 0.000023** — a
  clean single-count v2 fit.
- Estate-wide, `both` fits **84 records** (italy 7, japan 3, and the remainder
  inside ambiguous buckets in canada, norway and uk) — 0.0%.

Either the double-count was corrected and Sweden re-scored after the comment was
written, or the claim was never true of the artefact. The measurement cannot
distinguish those, and does not need to: **the comment asserts a present-tense
fact about published data that the published data contradicts.** It is corrected
in the same change that reconciles the module, not left as a trap for the next
reader.

The guard itself is correct and stays. Only the claim about what the artefact
currently contains is wrong.

## What the sentinel does not yet do

- It does not check the front end. `map.js` and `country-renderer.js` read
  `modifiers.R7_cyber` by name (plan step 4b); no automated check covers that.
- Its condition C will stay red for the five stale countries even after a correct
  cutover, until Phase ζ runs. That is honest, not a defect — but it means C is
  two conditions wearing one name, and it should be split before it is used as a
  release gate.

## Re-derive

    python3 scripts/check_r7_cutover_complete.py            # all 39
    python3 scripts/check_r7_cutover_complete.py --country sweden

Exit 0 only when all three conditions hold cohort-wide. It exits 1 today.

---

## ADDENDUM — 25 September 2026: condition C no longer holds as written

The same script, unmodified, re-run over the same 39 countries and the same
622,104 records, now returns `none` **23** where this document records **397,909
(64.0%)**. 621,967 records — 99.978% — reproduce from **v2 applied, v1 not**.

The cause is on the record: commit `866f3fc0` (21 September), the Phase ζ
39-country rescore plus Phase η band renormalisation. The five stale
jurisdictions named in Finding 1 — france, germany, us, italy, japan — now
reproduce.

Therefore, **of this document, as of today:**

- **Finding 1 is historical.** "On 64% of the estate the published product
  reproduces from nothing" was true on 17 September and is false now. Its
  consequence — "this changes plan steps 4 and 5 … those countries need the
  Phase ζ rescore, not an arithmetic adjustment" — was acted on, and the rescore
  ran.
- **Conditions A and B are unchanged, byte for byte.** 0 retired-True, 543,546
  v1 still emitted, 2,582 Sweden records with no v2. Eight days after the
  cutover was applied to the arithmetic, nothing has been applied to the record.
- **Finding 2 stands and is sharpened.** Sweden's 2,582 exceptional records
  carry *neither* cyber modifier, not both.
- **"What the sentinel does not yet do" has been measured.** The front end reads
  `modifiers.R7_cyber` in `regional-sections.js`, `data-sections.js` and
  `esg-report-shared.html`; `R7_cyber_v2` appears in no `.js` file in the
  repository.

Nothing above is edited. See
`RESULT_the_R7_cutover_is_arithmetically_done_and_editorially_not.md`.
