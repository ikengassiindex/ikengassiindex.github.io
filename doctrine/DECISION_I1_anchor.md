# Decision (DRAFT) — I1's anchor, for the operator's pin

Status: PINNED by the operator, 2026-09-09. ANCHOR = 0.9029 m SWE, frozen.
Registered under Bible §8. `_I1_raw` was written on 622,079 records on
2026-09-09; `metrics.I1` is derived against this anchor.

Operator's words on the skew of §4: "nothing to bury and we adopt geography
dictates snow." The concentration of the fleet near zero is accepted as the
correct behaviour of a load metric across a fleet spanning Costa Rica to
Norway, and is declared rather than corrected.

---

## 1. The fleet, measured

622,079 substations with at least 4 of 5 years. 25 records were unresolvable
and skipped; a further 25 across Portugal, the UK, the US and Canada had too
few finite years and were refused. None was defaulted.

    P50      0.0096 m SWE
    P90      0.0499
    P99      0.4300
    P99.5    0.6015
    P99.9    0.9029
    P100     7.2330
    at or below 1 mm: 67,842 records (10.9%)

## 2. A concern raised, investigated, and mostly retired

P100 of 7.23 m of snow water equivalent is not a snow load on a substation.
Seven metres of water equivalent is a glacier. The question was whether the top
of the distribution — and therefore the anchor — is set by permanently
glaciated grid cells rather than by seasonal snow.

Measured: **40 records of 622,079 sit above 2.0 m SWE**, spread across France
(26), Switzerland (4), Norway (4), Italy (2), the US (2), Canada (1) and
Iceland (1). The country maxima behave exactly as physical geography predicts —
Norway 7.23, Italy 6.17, the US 5.41, Switzerland 5.31, Iceland 5.08, Canada
4.08 — and the bottom of the table is Costa Rica, Colombia, Mexico and the
Netherlands at effectively zero.

**628 records sit above the P99.9 of 0.9029.** So the anchor is set by the
628th-largest value, not by the 40 extremes. The glacier tail is inside the
saturating band and does not move the pin.

A second concern, also retired: Costa Rica's maximum printed as `-0.0000`,
which looked like a negative snow depth. Checked across the whole estate:
**zero records are negative.** It is negative zero from rounding a value
smaller than 1e-5, not a sign error.

## 3. What the tail actually is

A 9 km ERA5-Land cell containing an alpine glacier reports that glacier's mass.
A substation whose nearest land cell is such a cell inherits it. That is a
real property of the source, not a defect in the derivation, and Method C
handles it the way it was designed to: everything at or above the anchor maps
to the top of the interval and stops. Forty units read "maximum snow loading"
rather than "seven times the maximum", which is the correct published claim.

It should still be declared, because a reader comparing I1 across the estate
deserves to know the top band contains cells whose value is glaciological
rather than meteorological.

## 4. The pin, and what it does to the fleet — ADOPTED

Anchor **PINNED at P99.9 = 0.9029 m SWE, frozen** — the rule I3 used, so the two
C_bounded metrics are pinned by one method rather than two.

    P50     raw 0.0096  ->  IRI 0.0032
    P75     raw 0.0214  ->  IRI 0.0071
    P90     raw 0.0499  ->  IRI 0.0166
    P95     raw 0.0972  ->  IRI 0.0323
    P99     raw 0.4300  ->  IRI 0.1429
    P99.9   raw 0.9029  ->  IRI 0.3000
    saturated: 628 records (0.101%)

**The distribution is extremely skewed and this must be said plainly.** Half
the fleet lands at 1% of the interval, and 10.9% at zero. I1 will contribute
almost nothing to component I for most substations.

That is not a fault. Snow load genuinely is zero in Costa Rica and genuinely is
extreme in Norway, and a metric that reported otherwise would be wrong. But it
means I1 buys less discrimination across the estate than its 0.12 intra-weight
implies, and the register should be able to say so.

## 5. The alternative considered and NOT taken

A lower anchor — P99 at 0.4300 — would give more resolution in the middle
(P95 would map to 0.068 rather than 0.032) at the cost of saturating 1% of the
fleet rather than 0.1%.

I do not recommend it. It compresses the genuine Nordic and alpine extremes
that I1 exists to capture, and it breaks the consistency with I3. But it is a
real option and the operator may prefer more spread across the middle of the
estate.

## 6. Declared with the metric, on every published value

- **Convention #7.** Five years, 2018-2022. For a LOAD metric this bites
  harder than for a within-period anomaly: an annual maximum over five years is
  a weak estimator of a design load that engineering practice takes at a
  50-year return period. I1 is five-year observed loading, not a design load.
- **The ice gap.** Glaze and freezing rain need precipitation phase, which this
  source does not carry. I1 is a snow-load metric with an ice-load gap.
- **The glacier band.** Section 3.
- **The skew.** Section 4.

## 7. If pinned

Component I coverage moves 0.509 -> 0.629 on I1 alone. `components.I` is NOT
rebuilt — that waits for full coverage per the 31 August decision. What moves
is `_I_from_metrics` and the conformance row that measures it.

No published score changes.
