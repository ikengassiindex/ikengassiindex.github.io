# DESIGN — the conformance register is the right instrument, and three aspects are missing

**Date** 21 September 2026
**On** `master documents/SSI_FOUNDATION_conformance.py` and
`SSI_CONFORMANCE_REGISTER.json` (86 rows, generated 21 Sep 05:20)
**Occasion** a day in which four code-reading hypotheses about one modifier
were all wrong, and the register had already recorded the answer

---

## 0 · Verdict

**It is on the right track, and it is the best-built instrument in the estate.**
Its posture is correct, its severity model is correct, and its methods are the
ones that actually worked today after code-reading failed four times.

The criticism below is therefore not "this is wrong". It is: **the register is
already a better detector than the people using it, and it is missing three
aspects that today's defects walked straight through.**

---

## 1 · Why it is the right instrument

### 1.1 The inversion

> *"Under the inversion, doctrine declares and the deployment is evidence …
> A red row is a defect against the implementation. It is never resolved by
> editing the declared column."*

That single rule is what makes this a conformance instrument rather than a
description. A descriptive document cannot say the implementation is wrong,
because it is generated from the implementation. The register can, and does.

### 1.2 The severity model prevents its own silencing

`BLOCKING / MATERIAL / DISCLOSED / DEFERRED`, with the explicit reasoning that
*"a permanently red check gets silenced, and silencing a correct refusal is a
failure this estate has already paid for once."* That is §7.8 made operational,
and it is why a register carrying 45 diverging rows is still alive rather than
switched off.

### 1.3 Its two methods are the correct two

**Reproduction.** `mult_product`: *"22.9% reproduce under no tested chain
shape."* `components · markov.risk_score`: *"reproduce exactly from the
substation name in 7 countries."* `R7_cyber`: *"reproduces as applied on 60.9%
of sampled assets."*

**Correlation.** Component `I`: *"r = +0.064 against its own metrics."* A
component that does not correlate with its own inputs is not derived from them,
whatever the doctrine says.

Today, four hypotheses about `R3_C_mult` formed by reading code were each
refuted within minutes of a measurement. What finally answered it was
reproduction against a candidate generator, and then the commit history. **The
register was using the right method on 18 September; the session using it was
not.**

---

## 2 · The row that was today's answer, three days early

> `published record` · *write paths* · declared: **written only by the declared
> pipeline** · observed: **22 scripts write published artefacts outside it** ·
> **BLOCKING**

If that row conformed, "what wrote this value" would be answerable by
construction and the whole `R3_C_mult` investigation would have been one
lookup. It is the highest-leverage row in the register.

---

## 3 · Missing aspect 1 — **consumer reachability**

### The gap

Two rows concern reachability — `validate.yml` *declared gates reachable* and
`I8` *input reachability*. Both look **upstream**. Nothing asks whether a
declared element is consumed by anything **downstream**.

### What it let through

`migration_score` is published on 622,104 records, now carries measured values
and honest provenance — and is consumed by nothing. `compute_r3`, the only
function containing the migration term, has **one call site in the repository**
and it passes no enrichments; `enrichments=` appears nowhere. The scoring
branch at `engine.py:296–303` is unreachable.

The estate's own pre-paper Q&A calls this *"the most consequential question in
this document"* for `graph_topology`. The register has the input half of it and
not the output half.

### Specification

| | |
|---|---|
| element | each declared element that doctrine states is scored, banded or ranked |
| aspect | `consumer reachability` |
| declared | the consumer doctrine names |
| observed | the call sites that reach it, counted, named |
| conforms | at least one reachable consumer exists in the deployed path |
| severity | **MATERIAL** — doctrine is not reachable in the deployment |

The test is a call-graph walk from the deployed entry points, not a grep for
the symbol. A function that *would* apply a term is not a term applied.

---

## 4 · Missing aspect 2 — **variance provenance**

### The gap

The register tests reproduction against a *declared transform*. The sharper
test is reproduction against a **hash of the record's own identifiers**, which
is a different and stronger statement: not "we cannot reproduce this" but
"this is not a measurement at all".

### What it let through, and why it matters more than anything else found today

`R3_C_mult` is the first multiplicative term in every published record's
modifier chain. Commit `dc761257` (4 June 2026) applied, in its own words,
*"hash-deterministic jitter: SHA-1(substation_id) first 4 bytes → uniform
[0,1) → [-1,+1) → *0.025"* to 19 countries, because health metric **D#29**
counted distinct values per country and failed them — the underlying
socio-economic input being regional, *"4-20 unique R3 values per country"*.

The same commit *"tightened D#29 precision (round(v,4) → round(v,6))"*, and
records the result: **US 13 unique → 30,886 unique, 68.6%.**

Nothing was concealed. The problem being solved was real. But the remedy was
presentation, not measurement, and **D#29 could not tell the difference.**

> **Any health check whose failure can be cured by adding entropy or precision
> is not a health check.**

### Specification

| | |
|---|---|
| element | each per-asset numeric field published |
| aspect | `variance provenance` |
| declared | measured per asset / regional with declared jitter / synthetic |
| observed | % of published values reproducing from a hash of the record's own identifiers, generator named |
| conforms | declared matches observed |
| severity | **BLOCKING** if declared measured and it reproduces from a hash; **DISCLOSED** if declared as jitter and it does |

Generators to test, all already present in the estate:
`md5(substation_id + name)`, `sha1(substation_id)[:4]`, and
`md5(f"{sid}|{name}|v42|{modifier}")`. Report the percentage per country, not
per cohort — **five countries reproduce at 100% and the cohort at 1.2%, and
the cohort figure hides the finding.**

---

## 5 · Missing aspect 3 — **marker against instrument range**

### The gap

Where a value carries a provenance marker naming an instrument, and that
instrument's reachable range is knowable, nothing compares the two.

### What it let through

90,476 records held `migration_score = 0.5` under
`_migration_score_source: NIVA_2023_20YR_SUM_v4_2_task_452`. The NIVA raster
contains no zero pixel; `0.5 + 0.5·tanh(raw/200)` returns 0.5 only at
`raw = 0`. All 1,922,207 finite pixels were tested and not one yields it.
**The instrument cannot emit the value the marker certifies.**

One comparison, and it would have failed on 90,476 records the day the marker
was written.

### Specification

| | |
|---|---|
| element | each field carrying a `_*_source` marker |
| aspect | `marker against instrument range` |
| declared | the instrument the marker names, and its reachable range |
| observed | count of values outside that range, or at values the instrument cannot produce |
| conforms | zero |
| severity | **BLOCKING** — a false provenance claim is a published value doctrine and deployment disagree about |

Only applicable where the range is computable. Where it is not, the aspect
should emit a **DEFERRED** row saying so rather than nothing — a silent absence
in a conformance register is the worst place for one.

---

## 6 · Two smaller items

**6.1 The summary does not reconcile with the rows.** `summary.by_severity`
reports BLOCKING 9 / MATERIAL 9 / DISCLOSED 27 / DEFERRED 11. The rows hold
11 / 11 / 53 / 11. The summary counts *diverging* rows for the first three and
*all* rows for DEFERRED. That is defensible and undeclared, and a reader
comparing the headline to the table sees a discrepancy with no explanation.
Either declare the semantic in the summary object, or report both counts. The
register would flag this in anything else.

**6.2 It is not wired into CI.** Nothing in `.github/workflows/` references
`SSI_FOUNDATION_conformance` or the register. It runs when someone remembers.
Its current register is stamped 21 Sep 05:20 — **before** the migration repair
(15:14), **before** ζ/η (14:08–15:45), and before the R7 v1 retirement actually
reached the published data. The three `R7_cyber` BLOCKING rows should read
differently now, and nothing will notice until it is re-run by hand.

An instrument whose whole purpose is to find divergence should not itself
depend on someone remembering to look.

---

## 7 · The process finding, which is not about the register

The register's BLOCKING list, generated before this session began, contains:
component `I` not deriving from its metrics; `R7_cyber` retired but applied;
values reproducing from the substation name; and 22 unsanctioned writers of
published records.

**That was this session's work, written down in advance.**

> **A conformance register that nobody reads before starting work is an
> expensive way to discover things twice.**

The cheapest change proposed in this document is not any of the three aspects.
It is reading the BLOCKING rows first.

---

## 8 · What not to do

**Do not turn it into a score.** The register's value is that each row is
binary and evidential — declared, observed, conforms. A composite "conformance
percentage" would be curable by adding easy rows, which is the D#29 failure
in a new costume.

**Test every proposed aspect against the entropy question before adopting it:**

> *Can this check's failure be cured by anything other than fixing the thing it
> measures?*

If yes, it is not a check. D#29 failed that test. The three aspects above are
proposed because they pass it: a consumer either exists or does not; a value
either reproduces from a hash or does not; an instrument either can emit a
value or cannot.
