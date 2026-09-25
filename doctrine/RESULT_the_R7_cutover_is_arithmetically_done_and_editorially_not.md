# RESULT — the R7 cutover is arithmetically done and editorially not

**Date** 25 September 2026
**Instrument** `scripts/check_r7_cutover_complete.py`, unmodified, re-run.
**Measured on** the deployed tree, all 39 countries, **622,104 records, every
shard**. Full census.
**Status** measurement only. Nothing published was changed.
**Supersedes, on condition C only**, `RESULT_the_r7_data_sentinel.md`
(17 September). Conditions A and B are unchanged to the record.

---

## 0. A claim of mine, withdrawn

Earlier in this session I wrote that the Ireland `R7_cyber` defect was

> the most serious of the five, since it is a live scoring error on a third of a
> published fleet.

**That is wrong and is withdrawn.** Ireland's 585 out-of-range v1 values do not
reach any published score. They do not reach a score anywhere in the cohort.

What I had missed is one line of the estate's own reproduction logic:

    p *= max(lo, min(hi, value))          # check_r7_cutover_complete.py

The chain **clamps** every multiplicative modifier into its registry range before
multiplying. I had reproduced the chain four times without the clamp, watched
"neither" dominate, and concluded the chain was unknown. It was not unknown; my
reproduction was wrong. The lesson is the cheaper one: the estate had already
built the instrument, and I re-derived instead of reading it.

## 1. Condition C, re-measured

    published mult_product fits            records      share
    v2_only                                534,887      85.98%
    ambiguous(both | v2_only)               83,529      13.43%
    ambiguous(neither | v2_only)             2,582       0.42%
    ambiguous(v1_only | v2_only)               969       0.16%
    ambiguous(neither | v1_only)                84       0.01%
    none                                        23       0.00%

Collapsing the degenerate buckets by what they actually decide:

    published product CONSISTENT with v2 applied      621,967   99.978%
    published product consistent with v2 NOT applied       84    0.014%
    published product reproduces from NO hypothesis        23    0.004%
    no published mult_product at all (turkey)              30    0.005%

On 17 September the same script on the same countries returned `none` **397,909
(64.0%)**. The cause of the change is on the record and is not a mystery:
commit `866f3fc0`, 21 September, *"zeta + eta: the estate rescored, and what
actually moved was the R7 cutover"* — a 39-country rescore plus band
renormalisation. The five stale jurisdictions the sentinel identified
(france, germany, us, italy, japan) now reproduce: france 168,489 of 168,894,
germany 107,646 of 108,016, italy 41,571 of 41,662, us 73,859 of 73,859.

**The sentinel's paragraph "on 64% of the estate the published product reproduces
from nothing", and its consequence "this changes plan steps 4 and 5", are true of
17 September and false of today.** They are left standing there, dated, and
pointed here.

## 2. Conditions A and B have not moved at all

    A  _r7_cyber_v1_retired True             0    False 619,522    absent 2,582
    B  modifiers.R7_cyber present      543,546    (must be 0 post-cutover)
       modifiers.R7_cyber_v2           619,522
       v2 with no v1 beneath it         78,558

Byte-identical to 17 September. The rescore changed what the arithmetic uses; it
changed nothing about what the record *says*. So:

- the flag that asserts the cutover happened is **True on zero of 622,104
  records**, eight days after the cutover happened;
- the retired key is still **emitted on 543,546 records**, inert but published.

`866f3fc0`'s own commit message says it plainly — *"the 543,546 records that
still carried the v1 key"* — in the present tense, and still correct.

## 3. Where the residue is not inert: the front end

`RESULT_the_r7_data_sentinel.md` closed by noting the sentinel "does not check
the front end … no automated check covers that." Measured now:

| file | line | what it does |
|---|---|---|
| `regional-sections.js` | 156 | `mods.R7 += Number(m.R7_cyber \|\| 0)` — regional R7 aggregate |
| `data-sections.js` | 307, 545 | prints `mods.R7_cyber` in the data table and the JSON view |
| `esg-report-shared.html` | 360, 365, 375, 380, 598 | SDG 9.1 narrative, the R7 row, the **NIS2 compliance cell**, the validity note, an R6 score term |

**`R7_cyber_v2` appears in no `.js` file in the repository.** The front end reads
the retired modifier, exclusively.

Three consequences, all live on the published site:

1. **On 543,546 records the figure displayed as R7 is not the figure scored.**
   Display shows v1; `mult_product` uses v2. The two differ per record.
2. **On 78,558 records the R7 cell renders `—` and the NIS2 row renders `gap`**
   (`d.modifiers?.R7_cyber ? 'ready' : 'gap'`), although the record carries a v2
   cyber term. That is a compliance statement, published, and false.
3. Every regional R7 aggregate is a sum of v1 over 87% of its members and of zero
   over the rest.

## 4. Two smaller things the census turned up

**38 of 39 `ssi-metadata.js` declare `R7_cyber` bounds `[1.00, 1.10]`.** The
registry says `(0.99, 1.05)`, and the archived v4.0.2 formula card says
`clip(..., 0.99, 1.05)`. The published bound contradicts both. Section 7.6.

**All 39 `intelligence.html` carry the dual-write paragraph:** *"the legacy
R7_cyber … co-exists with R7_cyber_v2 … Consumers may select either."* Consumers
cannot select either. The score uses v2 only and the page displays v1 only.

## 5. The 23 + 84 + 30

Three small populations where the arithmetic itself does not close.

**23 records reproduce from no hypothesis** (poland 8, belgium 4, slovenia 3,
estonia 2, ireland 2, latvia 2, netherlands 1, new-zealand 1). Every one is
under-modified in the same direction — the published product sits at 1.00–1.10
against a chain of 1.16–1.61:

    country        id                        published    v2 chain
    ireland        IE_v43_2748b644f421          1.0000      1.1620
    ireland        IE_v43_297b6bbe67f3          1.0000      1.3893
    poland         PL_v43_560836014522          1.0000      1.5252
    slovenia       SI_v43_f13478e2ae22          1.0552      1.6082
    belgium        BE_v43_293f4775b12a          1.0086      1.4936

Ten of the 23 publish exactly `1.0000`. This is the same class as residual 3 of
`RESULT_the_three_R7_cutover_residuals.md` (86 records, 17 September) — the
rescore cleared most of it and left 23. Section 7.5: a value that looks like a
result and is an absence.

**84 records carry v2 and their published product excludes it** — chile 70,
hungary 5, slovakia 5, denmark 3, korea 1.

**Turkey publishes 30 records with no `mult_product` key at all.**

## 6. Sweden, and the comment the artefact still refutes

Sweden is the only country where `R7_cyber_v2` is not on every record: **1,192 of
3,774**. Its other **2,582 carry v1 and no v2**, and their published product fits
the chain with *neither* — so those records carry **no cyber term at any version**
in their score. They are also, exactly, the 2,582 with no `_r7_cyber_v1_retired`
key.

`modifier_registry.compute_modifier_terms` still comments that *"Sweden's
published scores carry that double-count today."* The sentinel refuted it on
17 September; it is refuted again today, and more sharply. Sweden's exceptional
records carry neither cyber modifier, not both.

## 7. The instrument passes by not running

`scripts/check_r7_cutover_complete.py` exists in two places:
`ikengassiindex.github.io/scripts/` and `ssi-pipeline/scripts/`, byte-identical.
It resolves its data root as `REPO = dirname(dirname(__file__))`. Run from the
pipeline mirror, which holds no country directories, it enumerates zero
countries and prints:

    ESTATE  n = 0
    CUTOVER COMPLETE — all three conditions hold cohort-wide        # exit 0

Green, on an empty set, for a cutover that is not complete. Same mechanism as
`FINDING_the_gate_that_passed_by_not_running.md`; a fifth instance.

It is also **not wired into `scripts/preflight.sh`**, so nothing runs it on a
refresh.

## 8. What this leaves

The cutover is **arithmetically complete** — 99.978% of published scores use v2
and not v1 — and **editorially not started**: the flag is false everywhere, the
retired key is published on 543,546 records, and the site renders the retired
value as the live one.

Nothing here blocks the C-mosaic refresh, and nothing here is a scoring error of
the size I claimed. What it is, is a published statement that does not match the
published number, on 87% of the estate, plus a false NIS2 compliance cell on
78,558 records.

## Re-derive

    cd <site repo>                                     # NOT the pipeline mirror
    python3 scripts/check_r7_cutover_complete.py --country ireland
    python3 scripts/check_r7_cutover_complete.py       # all 39, ~7 min
