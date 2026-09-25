# PROPOSAL — five amendments to the Constitution

**Date** 21 September 2026 · **Status** FOR THE FLAG OFFICER. Nothing in
`SSI_FOUNDATION_BIBLE.md` has been touched.

The operator asked for a "full refresh" of the BIBLE. Having read it, **a full
refresh is the wrong instrument and I recommend against it.**

`SSI_FOUNDATION_BIBLE.md` is a document of principles, not measurements. It
carries almost no figures, and the ones it carries are illustrative. A
projection goes stale because the data moved; a constitution does not go stale
that way. Its 21 August date made it look a month behind alongside the
rendered packages, and that framing — mine, in
`FINDING_the_render_debt.md` — was misleading. **The BIBLE is not behind. It
is incomplete in five specific places, each of which the estate learned about
after it was written.**

Rewriting it wholesale would also be the wrong act constitutionally: it is
hand-authored, it is the one document no tool can regenerate, and the operator
holds the flag-officer role over doctrine. So this is five amendments with
draft language, to accept, reject or rewrite — not a replacement text.

---

## 1. §5 — the constitution recognises three evidence tiers. Four are in use.

**The gap.** §5 is headed "The three tiers" and defines E1, E2, E3.
`render2.py:1835` prints four, and **E0 is live**: `evidence.yaml` carries an
`own_publications:` block with `JIPR2026` and `ERE2026` at tier E0, and
`judgement.yaml` pins I1's 9 September amendment at E0. Tier usage across
`evidence.yaml` today is E0×2, E1×1, E2×14, E3×6.

**Why it matters more than a missing row.** E0 is *self-citation* — the estate
citing its own published papers as authority for its own doctrine. That is the
most delicate tier there is, and it is the one the anti-theatre rule does not
reach, because the rule is written about citations nobody read rather than
citations of oneself. The paper programme's own reference sweep found the
estate's two published papers cited under **nine different non-published
titles across five manuscripts**. E0 is exactly where that failure lands.

**And the constraint that matters most is not self-citation.** The operator,
21 September 2026: *"there is and always will be a difference between the live
of the index and any paper (published or to be published)."*

That is the governing fact and it is structural, not a risk to be managed. The
index is **live** — its data, its methods and its scores move, and are meant
to. A paper is a **snapshot**, fixed at submission and never updated again. An
E0 citation therefore supports a moving value with a frozen one, and the gap
between them only ever widens.

The estate already has the worked example. The Climate Risk Management paper's
own title states a **"796,121-substation × 39-OECD-country scale"**. The
canonical count is **622,104** — five deduplications on 29 August removed some
97,800 duplicate records. The paper is not wrong; it is *as of*. The register
moved and the paper cannot. That is why the estate's standing rule is that
796,121 stays inside citations of that paper and never cascades outward.

**Draft language, to sit after the E3 paragraph:**

> **E0 — the index's own publication.** A value supported by a peer-reviewed
> paper this estate authored.
>
> **The live index and a paper are different objects, permanently.** The index
> moves; a paper is fixed at submission. An E0 citation supports a value that
> can change with one that cannot, so every E0 is read *as of* its publication
> and never as a current statement of the index. A figure inside a paper's
> own text — its title, its abstract, its tables — stays inside that citation
> and is never cascaded into the live estate, however wrong it has become.
> Conversely a figure that has moved in the live estate does not retroactively
> falsify the paper.
>
> E0 is also *self-citation*, and is declared as such. It is admissible,
> because the estate's papers are peer-reviewed and public, and it is
> constrained:
>
> - E0 may not be used where an E1 or E2 source exists for the same value. Our
>   own paper is not preferred to the standard or the literature it cites.
> - E0 may not be the sole support for a value that a reader would take as
>   externally established.
> - An E0 citation names the paper as published — venue, year, DOI — and never
>   a manuscript in preparation or a preprint of our own.
>
> The anti-theatre rule applies to E0 with particular force. A citation of
> ourselves that a reader mistakes for external authority is the failure the
> rule exists to prevent, wearing the estate's own name.

---

## 2. §7 — a new prohibition. No marker that asserts work not done.

**What was learned.** Today, twice:

- The Task #450 bridge's audit marker sat on 100 % of Greek and Mexican
  records asserting a rescale that had been reverted seven weeks earlier. The
  utility skipped on the marker, so **the repair was blocked by its own audit
  trail**.
- `socio_economic_backfill.py:142` defines `DO_NOT_TOUCH_FIELDS`, a frozenset
  naming the fields that must survive a merge, and **references it nowhere**.
  The behaviour is correct by other means; the guard is decorative. I read the
  constant and drew the wrong conclusion about why the file was safe.

Prohibition 5 covers absence that reads as completeness. Neither of these is
an absence. Both are **a positive claim that the work was done**, which is the
same failure with the sign reversed and is not currently prohibited.

**Draft language, as Prohibition 9:**

> **9. No marker that asserts work not done.** A provenance marker, an audit
> trail, a named guard or a declared constraint is itself a claim, and it is
> subject to the same discipline as a measured value. A marker is written by
> the step that does the work, in the same operation, and never separately. A
> guard that is declared and never consulted is removed or wired in; there is
> no third state. Where a process decides whether to repeat work, it verifies
> the WORK, never the marker — a marker contradicted by the data is the reason
> to act, not the reason to skip.

---

## 3. §7.8 — a sentinel that cannot be run is not a sentinel.

**What was learned.** `pytest tests/` is killed by the OOM reaper at about
16 % in a 3.9 GB environment. Run file by file, all 33 complete and **46 real
assertions were red** — including one reporting 72 % of the canonical
reference country as misclassified. None of it was visible, because the wall
was not a red check but an unfinishable run. Behind it, a monthly job had been
silently reverting a manual repair for seven weeks.

Prohibition 8 forbids a permanently red sentinel. It does not reach a sentinel
nobody can execute, which is strictly worse: a red check is at least a claim.

**Draft language, appended to Prohibition 8:**

> A check that cannot be RUN is not a check. A suite that cannot complete in
> the environment it is meant to run in is a defect of the same class as a
> permanently red sentinel, and it conceals every check behind it. Where a
> suite cannot run whole, the inability is itself recorded as a blocking gap
> with an owner, and the checks are run in whatever partition does complete
> until it is fixed.

---

## 4. §8.5 — the re-render requirement contradicts Pin 16.

**The conflict.** §8 requires, *in the same change* as an amendment, "a full
re-render of every tier below". Pin 16 requires "render ONCE and LAST". With
amendments arriving in a series — three in September, six on 21 September
alone — both cannot be honoured. Today §8.5 was unmet for most of the day and
the render came at the end, which was the right call and was outside the
letter of the constitution.

**Draft language, replacing §8 item 5:**

> 5. a full re-render of every tier below, with sentinels passing — rendered
>    ONCE per amendment SERIES and not once per amendment, and closed by a
>    single commit that names every amendment it promulgates. An amendment
>    that is landed without its render is not thereby exempt: it is in debt,
>    and the debt is discharged only by that closing render. A series left
>    unrendered at the end of a working session is a blocking gap.

---

## 5. Prohibition 4 — the one document it cannot govern is this one.

**The gap.** Prohibition 4 states: "No document derived from another document.
Documents derive from the registry. Always." The BIBLE derives from neither.
It is authored, and measured today: **no `.py` file in either tree contains
the string "BIBLE"**. Nothing can regenerate it.

That is correct and should stay correct — a constitution generated from the
thing it governs would be circular. But it is unstated, and its consequence is
unowned: because no renderer touches it, its currency is nobody's tooling's
problem and it can drift indefinitely without any gate noticing. Which is what
happened.

**Draft language, as a note under Prohibition 4:**

> This document is the single exception, and necessarily so: a constitution
> generated from the registry it governs would be circular. It is authored,
> nothing renders it, and no gate can detect that it has fallen behind. Its
> currency is therefore the flag officer's personal charge and cannot be
> delegated to a sentinel. Every amendment to `judgement.yaml` or
> `taxonomy.yaml` carries an explicit question: does this change what the
> constitution says? The answer is recorded in the change-log entry, including
> when it is no.

---

---

## 6. §5 — and the same rule in the other direction

The live/snapshot distinction has a second edge, and the constitution governs
neither.

A paper cites the **register** as a data source: *"SSI Index (Systemic System
Infrastructure Index). 2026. Italy substation register. V4.2."* By the time a
reviewer follows that citation, the register will have moved — it is refreshed
monthly by design. A citation of a live resource that does not pin what it
saw is not reproducible, and the estate's own constitution demands
reproducibility of everything else.

This is not hypothetical either: the register is a manifest over shards whose
counts changed on 29 August, and today's work changed 358 province labels and
four shard manifests. A reader checking a June citation against today's
register finds different numbers and no way to tell whether the paper was
wrong or the data moved.

**Draft language, as a further requirement on a citation:**

> **A citation of the live estate pins what it saw.** Where a paper, a report
> or a document cites the index's own register or published data, it names the
> version and the date, and where the artefact is addressable it names the
> commit. The index is refreshed by design, so an unpinned citation of it is
> not reproducible and is defective on the same grounds as an unread source.
> This binds the estate's own publications first.

---

## What is NOT proposed

No change to §1, §2, §3, §3b, §4, §6 or §9. They were read and they hold. The
founding principle, the order of battle, the three classes, the cascade,
country articulation and the conformance register all describe an estate that
still works the way they say it does.

## If these are accepted

They are five amendments to `judgement.yaml`'s governing document, not to
`judgement.yaml`, so §8's machinery does not directly apply — but its spirit
does. Each should land with a date, the operator as decider, and a one-line
basis. I can prepare the edited BIBLE for signature; I have deliberately not
prepared it in advance, because a constitution offered as a fait accompli is
a different thing from a constitution amended.
