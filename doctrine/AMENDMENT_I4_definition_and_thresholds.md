# AMENDMENT — I4 and I6 density: definitions, floors, and declared limits

**SIGNED BY THE OPERATOR, 17 SEPTEMBER 2026.** It SUPERSEDES
`AMENDMENT_DRAFT_I4_I6_definition.md` and
`AMENDMENT_DRAFT_I4_transmission_thresholds.md`, both of which were unsigned and
stated so on their face, and it is now the sole authority for **I4 and I6**.

**The three elections, as made:**

| election | decided |
|---|---|
| Floor scope | **Sign the 13 sourced floors as verified; carry the other 26 as DECLARED UNVERIFIED.** Not held as ABSENT: holding would mean a derivation run writing ABSENT across most of the estate, in a layer that reaches no published score, and the honest alternative is to name them unverified and require sourcing before any rebuild. |
| Mexico | **69**, per CENACE's own PRODESEN. The 115 pinned in August read CFE's ladder without a citation; the sourced figure wins. |
| I6 population | **Derive for Luxembourg and Iceland.** I6 needs no voltage floor and could always have covered them. |

> **I6 WAS ADDED TO THIS DOCUMENT ON THE SAME DAY IT WAS DRAFTED, AFTER A GAP
> WAS FOUND IN IT.** The first issue superseded
> `AMENDMENT_DRAFT_I4_I6_definition.md` — which defines I4 *and* I6 — and
> replaced the authority for I4 only. Signing it would have left I6, a metric
> already declared `implemented` on 37 countries, with its defining document
> superseded and nothing in its place: no authority at all, which is worse than
> the unsigned draft it has now. Found by asking what else the superseded
> document contained, which is a question the first issue never asked.

**Date drafted:** 17 September 2026. **Evidence:** every figure below is either
measured against the deployed tree on that date, or cited to a named primary
source. Where neither is true the row says so.

**Why this document exists.** I4 is derived and published on 100 per cent of
622,104 substations. Its definition cites two documents that state on their face
that nothing was written to the register, and its 37 country floors live in
`scripts/i4_transmission_thresholds.json`, a file no doctrine document
references. Asked on 17 September whether the 30 August pin was ever made, the
operator did not recall. The estate therefore cannot establish its own authority
for a published metric, and this amendment is the instrument that settles it.

---

## 1. The definition

    I4_raw   transmission line-km within a 3x3 block of 0.1 degree cells
             (~33 km across) centred on the substation's cell, counting a line
             when kv >= that country's floor in section 2.
    I4       Method B over THAT COUNTRY'S fleet P5/P95, then INVERTED per
             construct section 03: N'(x) = N(P5 + P95 - x), because higher
             density is better resilience.

**Definition A (local), not B (regional).** Measured 17 September 2026 by
decomposing the variance of A into between- and within-region parts. Definition
B keeps only the between-region part:

| country | substations | regions | B keeps | B destroys |
|---|---:|---:|---:|---:|
| Poland | 27,764 | 74 | 58.8% | **41.2%** |
| France | 168,894 | 102 | 59.2% | **40.8%** |
| Spain | 12,438 | 66 | 45.2% | **54.8%** |

B discards between two-fifths and more than half of the discriminating signal.
The construct's own rationale for inverting this metric describes local network
redundancy, which is what A measures and what B averages away.

## 1a. I6 — substation density

    I6_raw   substations within the SAME 3x3 block of 0.1 degree cells used by
             I4, centred on the substation's own cell.
    I6       Method B over THAT COUNTRY'S fleet P5/P95, then INVERTED, exactly
             as I4: denser surroundings mean better resilience and a lower
             metric.

**I6 needs no voltage floor.** It counts substations, not lines, so section 2
does not apply to it and none of the threshold questions in this amendment touch
it. Measured on the deployed records, 17 September 2026: `_I6_raw_count` runs
from 1 to 4,183 with a median of 144, across 37 countries.

### The one election I6 requires

I6 is ABSENT in Luxembourg and Iceland — **not because it cannot be computed
there.** It can: it needs no voltage, and the voltage gaps that hold I4 in those
two countries are irrelevant to counting substations. It is withheld because the
deriver holds it to I4's country gate, in its own words, *"so the two metrics
always describe the same population"*.

That is a stated design choice and not an oversight, and it has a real argument
behind it: I4 and I6 both feed component I, and letting them cover different
countries makes `_I_coverage` mean different things in different places.

**But it is inconsistent with how I2 was handled.** I2 is ABSENT for 108,550
substations outside the CERRA domain while every other I metric is present for
them, and component I's coverage is declared as geographically uneven rather than
levelled down. The estate already tolerates and declares uneven coverage within
component I. Holding a computable metric hostage to an uncomputable one is the
opposite convention, applied to the same component.

At stake: 1,408 substations — Luxembourg 723, Iceland 685.

*I6 population elected (delete one): hold to I4's gate as now · derive I6
independently for Luxembourg and Iceland*

## 2. The floors (I4 only)

Generated from `scripts/i4_transmission_thresholds.json` rather than retyped, so
the values in this table and the values the deriver reads are the same values.
**On signature this table, not that file, is the authority; the file becomes its
serialisation.**

| country | floor (kV) | status | basis |
|---|---|---|---|
| `australia` | 132 | — not sourced — | carries the 30 August reading; no primary source checked |
| `austria` | 220 | — not sourced — | carries the 30 August reading; no primary source checked |
| `belgium` | 150 | — not sourced — | carries the 30 August reading; no primary source checked |
| `canada` | 230 | — not sourced — | carries the 30 August reading; no primary source checked |
| `chile` | 220 | — not sourced — | carries the 30 August reading; no primary source checked |
| `colombia` | 230 | — not sourced — | carries the 30 August reading; no primary source checked |
| `costa-rica` | 138 | — not sourced — | carries the 30 August reading; no primary source checked |
| `czechia` | 220 | — not sourced — | carries the 30 August reading; no primary source checked |
| `denmark` | 132 | — not sourced — | carries the 30 August reading; no primary source checked |
| `estonia` | 110 | — not sourced — | carries the 30 August reading; no primary source checked |
| `finland` | 110 | — not sourced — | carries the 30 August reading; no primary source checked |
| `france` | 63 | CONFIRMED | RTE, *Bilan électrique* — "63 kV à 400 kV", 105,817 km |
| `germany` | 220 | CONFIRMED | Bundesnetzagentur/SMARD — transmission "at least 220 kilovolts" |
| `greece` | 150 | — not sourced — | carries the 30 August reading; no primary source checked |
| `greenland` | 60 | CONFIRMED as pinned | pin file `_greenland_basis`, verified: 228.0 km on 28 records ≥60 kV; 132 kV is 80.1 km on 12 |
| `hungary` | 132 | — not sourced — | carries the 30 August reading; no primary source checked |
| `ireland` | 110 | CONFIRMED (operational, not statutory) | EirGrid — "operated at 400 kV, 220 kV and 110 kV" |
| `israel` | 161 | — not sourced — | carries the 30 August reading; no primary source checked |
| `italy` | 132 | **CHANGE TO 120** | Terna *Codice di Rete* — RTN tiers "150-132-120 kV"; annex: 45,343 km at 150-120 plus 3,550 km RTN below 120 |
| `japan` | 154 | — not sourced — | carries the 30 August reading; no primary source checked |
| `korea` | 154 | — not sourced — | carries the 30 August reading; no primary source checked |
| `latvia` | 110 | — not sourced — | carries the 30 August reading; no primary source checked |
| `lithuania` | 110 | — not sourced — | carries the 30 August reading; no primary source checked |
| `mexico` | 115 | CONTESTED — 69 vs 115, 4,092 km, 3.7% | CENACE PRODESEN — "tensiones iguales o mayores a 69 kV"; pin file reads CFE's ladder as 400/230/161/138/115 |
| `netherlands` | 110 | — not sourced — | carries the 30 August reading; no primary source checked |
| `new-zealand` | 110 | — not sourced — | carries the 30 August reading; no primary source checked |
| `norway` | 300 | — not sourced — | carries the 30 August reading; no primary source checked |
| `poland` | 220 | CONFIRMED | PSE — 400 kV 9,624 km + 220 kV 6,896 km |
| `portugal` | 150 | — not sourced — | carries the 30 August reading; no primary source checked |
| `slovakia` | 220 | — not sourced — | carries the 30 August reading; no primary source checked |
| `slovenia` | 110 | — not sourced — | carries the 30 August reading; no primary source checked |
| `spain` | 220 | CONFIRMED (peninsula; islands run to 66 kV) | Ley 24/2013 Art. 34 — transporte secundario ≥220 kV |
| `sweden` | 220 | — not sourced — | carries the 30 August reading; no primary source checked |
| `switzerland` | 220 | — not sourced — | carries the 30 August reading; no primary source checked |
| `turkey` | 154 | CONFIRMED as operating level, not the legal >36 kV boundary | TEİAŞ *Stratejik Planı* — "154 kV ve 400 kV" |
| `uk` | EW 275 / SCO 132 / NI 110 | CONFIRMED | Energy Act 2004 s.180 — ≥132 kV Scotland, >132 kV England & Wales |
| `us` | 100 | CONFIRMED (radial exclusion E1 applies) | NERC Bulk Electric System; FERC Order No. 773 |

### Held — I4 is ABSENT, and that is a decision, not a gap

| country | state | rule | tested basis |
|---|---|---|---|
| `iceland` | I4 ABSENT | declared | 50.2% of line-km carries no voltage. TESTED against OSM 31 Aug 2026: grid-geo line ids are 1..1,427, sequential synthetic integers rather than OSM way ids, so no id join exists; OSM holds only 153 voltage-bearing lines for the whole country against 1,230 untagged register lines. Not recoverable from OSM. |
| `luxembourg` | I4 ABSENT | declared | 57.5% of line-km carries no voltage. TESTED against OSM 31 Aug 2026: only 116 of 797 untagged lines exist in OSM even including minor_line and cable, and NONE carries a voltage tag. Not recoverable from OSM. |

### The one change requested

**`italy` 132 → 120.** Terna's own reporting tier is "150-132-120 kV", and its
statistical annex books 45,343 km at 150-120 kV plus a further 3,550 km of RTN
*below* 120 kV. A 132 kV floor excludes the 120 kV RTN tier. 41,662 substations.
Terna's RTN perimeter is fixed by ministerial asset list (DM 25 giugno 1999) and
not by voltage, so any kV floor for Italy is an approximation; 120 is the
tightest available.

### The one contested reading, not a change

**`mexico` 115.** CENACE's PRODESEN states the Red Nacional de Transmisión
"incluye las tensiones iguales o mayores a 69 kV" and books a "Transmisión 69 a
138 kV" tier of 54,437 km. The pin file reads CFE's ladder as beginning at 115.
The difference is the 69 and 85 kV tiers, 4,092 km, 3.7 per cent of the RNT.
**Recorded as a divergence rather than resolved.** Signing this amendment at 115
is defensible; so is 69. What is not defensible is leaving the disagreement
unrecorded.

## 3. What the floors do NOT buy — the proxy declaration

The 30 August draft hoped a voltage filter would make this "RTN density in fact
and not by proxy". **It does not.** Measured 17 September 2026 against each
TSO's own published transmission length:

| country | filtered ÷ published |
|---|---|
| `poland` | 0.99× |
| `france` | 1.23× |
| `italy` | 1.33× |
| `turkey` | 0.74× |
| `mexico` | 1.48× |
| `luxembourg` | 0.33× (held) |

Poland moves from 7.23x the national transmission length unfiltered to 0.99x
filtered; France from 2.79x to 1.23x. The residual spread is 4.5x between best
and worst.

> **CONVENTION #7 DECLARATION, which survives signature.** I4 is
> **transmission-voltage OSM power-line density**, a documented proxy for RTN
> density. It must not be published as "RTN density". OSM mixes transmission and
> distribution unevenly between countries, and the ratios above are the measure
> of that unevenness. This declaration travels with every published value.

## 4. Declared limits

**4.1 Twenty-six of thirty-nine floors are unsourced.** Eleven were checked
against named primary sources for this amendment, plus the two held countries.
The remaining twenty-six carry the 30 August reading, which that draft itself
labelled "NOT measured — my reading ... a starting point for your pin, not as a
finding". Checking eleven produced one change and one contested reading.
**Signing this amendment signs twenty-six unverified coefficients unless they are
held.** The operator may (a) sign all 39 and accept that, (b) sign the 13 and
hold the rest as ABSENT, or (c) hold signature until the 26 are checked.

**4.2 `kv = 0` is a sentinel for unknown, not a voltage**, and countries use two
encodings — the UK omits the field on 35.4 per cent of line-km, Finland supplies
0 on 33.8 per cent. Any code touching these floors must treat both as unknown.

**4.3 Zero-density substations.** A substation whose 3x3 block contains no
qualifying line scores a raw of zero, which after inversion becomes the WORST
band. Measured: France 0.1 per cent, Poland 6.2 per cent, **Spain 13.2 per
cent**. Whether that is genuine remoteness or an artefact of a distribution-only
substation is NOT decided by this amendment and remains open.

**4.4 I4 does not reach any published score, and the layer it does reach is
not small.** `components.I` is the `enrich_esg_gaps` fill, not a sum of the
metrics, so nothing in this amendment changes a published R. Measured across the
whole estate on 17 September 2026, not on one country: **543,546 records (87.4
per cent) carry `components.I`**, and it equals `_I_from_metrics` on **149 of
them — 0.027 per cent**. The two differ by more than 0.10 on 51.9 per cent of
records, mean +0.0610, range −0.974 to +0.994.

Rebuilding component I from the metric layer would move **89,056 substations
(16.4 per cent) across a classification band** — 67,097 to a worse band, 21,959
to a better. That is not a consequence of this amendment and is recorded here so
that signature is not read as endorsing the fill. Country coverage is very
uneven: France, Germany, Italy, Israel and Costa Rica at 100 per cent, Austria at
5.0 per cent, Poland at 8.1 per cent.

## 5. What signature does

1. This document supersedes both drafts and becomes I4's sole authority.
2. `scripts/i4_transmission_thresholds.json` becomes the serialisation of §2,
   and gains a header naming this amendment — closing the finding that 37
   coefficients determining a published metric are referenced by no doctrine
   document.
3. The deriver's `AMENDMENT` constant changes to name this document, which
   repairs the citation of `AMENDMENT_DRAFT_I4_definition.md` — a file that
   exists nowhere and is currently cited by the published records.
4. Italy re-derives at 120 kV. No other country's values change.
5. I4's status moves from `blocked` to `implemented` for the signed set, with a
   change-log entry naming element I4.
5a. **I6's judgement entry is rewritten to describe what it derives.** It
   currently reads "Density of the surrounding transmission and distribution
   network" with units "index" — generic where the quantity is a count of
   substations in a 3x3 block, normalised Method B per country and inverted.
   I6 is already declared `implemented`, so this corrects a description rather
   than adding a claim, and it is the same staleness found in I5 on 17
   September. A change-log entry names element I6.
6. The conformance rows for provenance citation, declared-blocked-found-on-
   records and coefficients-outside-doctrine close for I4.

**If this is not signed**, the alternative is to withdraw I4 from the metric
layer until it is. What is not available is the present state: published on
622,104 records, citing documents that say nothing was written to the register,
against floors no doctrine document can see.

---

**Signed:** operator  **Date:** 17 September 2026

Recorded as the estate records every other decision of this kind — `decided_by:
operator` with a date, in the judgement layer and in the change log — rather than
by a signature this repository has no means of verifying.

**Applied the same day:**

| | |
|---|---|
| `italy` 132 → 120 | 413 of 41,662 units changed, 1.0%, mean −0.0006 |
| `mexico` 115 → 69 | 2,789 of 3,085 units changed, 90.4%, mean −0.0213 |
| `I6` for luxembourg + iceland | 1,408 units added; no existing value changed |
| I4 status | blocked → implemented |
| I6 coverage | **622,104 of 622,104 — the only metric in the register at complete coverage** |

Italy moving only 1.0 per cent is worth stating plainly: Method B normalises
within a country, so adding the 120 kV tier lifts the whole distribution and
changes the ORDERING very little. The correction was still worth making — the
floor now matches what Terna calls its own network — but it is a correction to
the declaration more than to the numbers, and anyone expecting a visible shift in
Italy's I4 should not.
