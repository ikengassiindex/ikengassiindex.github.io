# FINDING — the impact table credits a modifier the score does not contain

**Measured** 21 September 2026, over all 622,000 published records carrying
`modifier_impacts`.

Found while repairing a red sentinel, and not by the part that was red. The
failing assertion was an arithmetic expectation written before the R7 cutover.
Correcting it was routine. The defect surfaced only because I added a *second*
assertion — that a retired modifier must not reach the impact table — to
check that the drop was deliberate rather than accidental. **The product was
right. The table was wrong. Only the product was being checked.**

## The defect

`compute_modifier_terms()` honours `retired` and drops the modifier from the
**score**. `per_modifier_impacts()` did not, and kept it in the
**attribution**. So the published audit trail credited a term the score does
not contain.

An audit trail that does not reconcile with the number it explains is worse
than no audit trail, because it looks like provenance.

## How far it reached

    records carrying modifier_impacts                           622,000

    impacts naming R7_cyber — RETIRED, absent from the score     144,947   23.3%
    impacts naming R7_cyber_v2 — the term actually applied        81,063   13.0%
    naming BOTH                                                   81,063
    naming NEITHER                                               477,053   76.7%

Three observations, in ascending order of seriousness.

**The tables are heterogeneous.** Three different shapes across one cohort
means they were written at different times and never re-derived. A field that
differs by when a record was last touched is not a specification.

**Where both appear — all 81,063 of them — the attribution double-counts.**
The score applies the cyber term once, through v2. The table names v1 and v2
side by side, so a reader summing the impacts gets a cyber contribution the
score never had.

**The common case names the wrong one.** 144,947 records name v1 and only
81,063 name v2, so on the majority of records that mention cyber at all, the
table credits the retired modifier and omits the live one.

## Fixed in code, not in the data

`per_modifier_impacts()` now excludes any modifier the registry marks
`retired`, and `tests/test_modifier_registry.py` asserts it.

**The published records are not repaired by this.** They carry the old tables
until they are re-scored, and re-scoring is a data operation, not a code fix.
Recorded here so the gap between the corrected code and the uncorrected
payload is visible rather than assumed away.

## What it says about the sentinel suite

This is the second time today that fixing a red test found something the red
test was not about. The first was `test_retired_modifier_excluded`, where the
failure was a test-order bug but the throttle it exposed was correct and worth
keeping. This one is sharper: **the assertion that found the defect did not
exist until I wrote it**, and nothing in 1,207 existing assertions covered the
reconciliation between `mult_product` and `modifier_impacts`.

There is a test asserting that the ADDITIVE impacts sum to `add_sum`. There is
none asserting the multiplicative impacts reconstruct `mult_product`. That
asymmetry is why this survived, and it is the obvious next sentinel to write.
