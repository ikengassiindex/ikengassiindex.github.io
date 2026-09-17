# FINDING — the Implementation pointer never pointed at an implementation

**Date** 17 September 2026
**Found while** propagating the I2 CERRA result into the foundational documents,
by rendering one country and reading it before looping the other thirty-eight.
**Scope** all 40 foundational documents — the master and 39 countries — for the
whole life of the field.

---

## What the field claims to do

`SSI_FOUNDATION_measure.implementation_pointers` carries this docstring, and the
Construct prints its result in a column headed **Implementation**:

> A pointer that does not resolve is reported as unresolved rather than omitted.
> An element the document calls implemented, with no coordinate to show for it,
> is exactly the claim this field exists to test.

The conformance register carries a check built on it, aspect
`implementation pointer`, severity MATERIAL, with the note *"an element the
document presents with no coordinate"*.

## What it actually did

Every pointer ever published was a false positive, of one of three kinds.

| Kind | Example, as published | What the line is |
|---|---|---|
| A dict KEY in a table ABOUT the element | `I1` → `engine.py`:57 | `"I1": 0.20,` in `SIGMA_TOTAL`, the Monte-Carlo sigma table |
| | `I6`, `I2`, `I4`, `I7`–`I9`, `C1`–`C4`, `V1`, `E1`, `E2`, `S1`–`S3`, `T1` | the same table |
| A line of module DOCSTRING prose | `I3` → `ssi_derive_metric_I3.py`:57 | `I3 = IRI_current / 0.30 = min(1, I3_raw / ANCHOR)` — a description of the formula inside a docstring |
| | `I5` → `ssi_derive_metric_I5.py`:45 | `I5 = Method B over THAT COUNTRY'S fleet P5/P95` — likewise |
| A local VARIABLE sharing an element's name | (would have been) `V1` → `session_k_r7_v2_dryrun.py`:93 | a local in a dry-run script |
| | (would have been) `S3` → `pipeline/ingestion/slovenia/_base.py`:111 | a local in one country's ingestion |

Not one of them computes a metric. `I3` and `I5` looked correct only because the
filename was plausible; the line was prose.

## The mechanism

Two independent faults, each sufficient on its own.

**1. The definition test was a text pattern anchored at line start:**

```python
re.search(r"^\s*(def\s+\w*I3|\"?I3\"?\s*[:=])", line)
```

It matches a dict key (`"I3": 0.22,`) and a docstring line (`I3 = ...`). It
cannot match the actual write, `m["I3"] = round(v, 4)`, because of the `m[`
prefix before the anchor. So the one line that *is* the implementation was the
one shape the test could not see.

**2. The pool was chosen before the rank was applied:**

```python
pool = defs or hits
pick = sorted(pool, key=lambda h: (rank(h), h[1]))[0]
```

`rank` demotes files with `validate` or `test` in the path to 9. But if any
"definition" existed anywhere, `defs` won outright and `rank` never got to
demote it. A file that merely *named* an element therefore outranked the engine.

## How it surfaced

It did not surface by inspection. It surfaced because
`scripts/verify_metrics_reproducible.py`, added on 12 September, contains

```python
GLOBAL = {"I1": ("_I1_raw", "record", 0.9029, 0.30, 4),
          "I2": ("_I2_raw", "metrics", 45.3363, 0.30, 4)}
```

at lines 48–56 — six lines that match the definition pattern and sit at lower
line numbers than the old accidents. All six I-metrics' pointers moved into a
file that verifies and writes nothing. The first reading of that was "my new
verifier has stolen the pointers." It had not. It had displaced one set of false
positives with another, and in doing so made the field's behaviour visible.

**A verifier that writes nothing was published as the implementation of six
metrics, and the only reason anyone looked was that it was the wrong wrong
answer rather than the familiar one.**

## Why it survived

The conformance register contains a check written to catch exactly this:

```python
for eid in elements:
    p = (ctx.get("pointers") or {}).get(eid) or {}
    if not p.get("resolved"):
        rows.append(_row(eid, "implementation pointer", ...))
```

It has never fired, for any element, in its entire life. It fires on
`not resolved`, and the old rule always resolved *something* — a sigma-table key
if nothing better. **The check was silenced by the measurement it depended on.**
A guard whose input can never take the failing value is not a guard.

## The rule now

Resolved by PARSING each file, not by matching text against it.

- A pointer resolves only to an **assignment into a subscript** — `m["I3"] = ...`
  — the act of putting the element on the record, which is what `implemented` is
  supposed to mean here. A dict key is not an assignment; a docstring is not
  code; a local variable is not a subscript. All three classes die structurally
  rather than by pattern.
- A key supplied through a **module-level string constant** is followed one step.
  `modifiers[REGISTRY_KEY] = r7_v2`, with `REGISTRY_KEY = "R7_cyber_v2"` in the
  same file, is a write and is counted as one. This was found by the rule's own
  first draft reporting `R7_cyber_v2` as declared-implemented-with-no-write, and
  running that down rather than waving it through.
- Files that **verify, validate, test, audit, probe, measure** or carry
  `conformance` in the name are excluded from the pool outright. Such a file
  names every element it checks and writes none.
- A **one-off** repair or migration ranks below a standing deriver. It is a
  truthful answer to "where is this written" and the wrong answer to the
  question the column asks. Without this, `I1` resolved to
  `ssi_repair_I1_reproducibility.py`:113 instead of `ssi_derive_metric_I1.py`:333.
- A file that **cannot be parsed** is reported on stderr, not swallowed: its
  writes are invisible to this measurement and that is worth knowing. None
  currently fail.
- No write site means **unresolved**, not a coordinate that misleads.

## What the documents now say

| | before | after |
|---|---|---|
| Elements with a printed coordinate | 37 of 37 | 17 of 37 |
| Elements declared `implemented` resolving to their write line | 0 of 5 | 5 of 5 |
| Conformance rows on aspect `implementation pointer` | 0 | 27, all MATERIAL |
| Other conformance rows changed | — | 0 changed, 0 removed |

Every one of the 27 is an element declared `blocked`, or a modifier with no
status declared. **No element declared `implemented` fails the check.**

The appendix column formerly headed `Sites` counted *mentions* — `C1` showed 111
of them while having no implementation at all, which is the same disease in
another column. It now counts write sites and is headed `Writes`.

## Two things this exposed and did not close

1. **`I4` and `I5` are declared `blocked` and both have live derivers** that
   write them onto records — `ssi_derive_metrics_I4_I6.py`:346 and
   `ssi_derive_metric_I5.py`:144. The register and the tree disagree. Visible
   now; not resolved here, because which one is wrong is the operator's call.
2. **Severity.** The check reports MATERIAL for all 27. For an element declared
   `blocked`, having no implementation is the declared state, not a defect. A
   severity that read the declared status — MATERIAL for `implemented` without a
   write, DISCLOSED for `blocked` without one — would carry more signal. Not
   changed unilaterally.

## The lesson, stated plainly

Three separate rules were tried here before this one, and each was checked
against the tree before being believed. The first two both produced confident,
plausible, wrong answers: `T1 = 0.50·N(DER_ratio) + ...` at
`ssi_derive_component_T.py`:15 is a docstring, and `V1` at
`session_k_r7_v2_dryrun.py`:93 is a local variable, and both were the output of
rules that looked reasonable when written.

**A measurement that is allowed to answer from text will answer from prose.**
Where the question is about code, parse the code. And a guard that has never
once fired is not evidence that the estate is clean; it is a thing to go and
test deliberately, because the most likely explanation is that it cannot fire.

---

*Registered under Constitution 8. The correction to the pointer rule is an edit
to the measurement tooling, not an amendment to any element, so it carries no
change-log entry: the change-log guard's own words are "An amendment that cannot
name one is not an amendment; it is an edit." The `I3` bounded-interval
correction found in the same pass does name an element and is registered there.*
