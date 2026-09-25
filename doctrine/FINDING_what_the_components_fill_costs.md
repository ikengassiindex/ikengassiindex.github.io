# FINDING — what the `components.I` fill costs

**Date** 17 September 2026
**Measured on** the deployed tree, all 39 countries, 622,104 substations.
**Status** measurement only. Nothing published was changed.

---

## The question

`components.I` is not built from the I metrics. It is filled by
`enrich_esg_gaps` from `vary(0.35, name + '_' + K, 0.30)` — a hash of the
substation's name. The real metric-derived value is published alongside as
`_I_from_metrics`, per the operator decision of 31 August 2026 to publish both
and swap when coverage is complete.

Everything done to the metric layer this session — I2's CERRA anchor, the I1/I2
scale alignment, I3's interval, the I4 thresholds — improves `_I_from_metrics`
and touches no published score. The question nobody had answered is what that
separation is worth: **if component I were rebuilt from the metrics, what would
move?**

## What was measured, and where the measurement stops

`compute_r_base` is a weighted sum, so replacing `components.I` with
`_I_from_metrics` moves `R_base` by exactly `0.25 × dI`. `R_median =
soft_clip_upper(R_base × mult_product) + add_sum`, and `soft_clip_upper` is the
identity at or below 1.0, so the shift propagates exactly as
`0.25 × dI × mult_product` wherever `R_base × mult_product ≤ 1.0`.

    delta propagates EXACTLY          540,074 records   99.4%
    compressed region, first-order      3,472 records    0.6%

**The limit.** `R_median` does not itself reproduce from published components —
703 of 2,247 sampled, the registered `mult_product` chain-provenance finding. So
this measures the SHIFT the swap would cause, applied to the published `R`. It is
not a recomputation of `R`, and it cannot be one until that finding is closed.

**The second limit.** Component I is nine metrics and six are real, so
`_I_coverage` is 0.72. This is what a rebuild would do TODAY, not what a complete
component I would do.

**The third limit.** Only component I has a metrics-derived counterpart at all.
C, V, E, S and T have `_from_metrics` on ZERO records, because every metric
beneath them sits on zero records. There is no equivalent measurement to make for
them, and that absence is the more important fact about the estate.

## The answer

`components.I` is carried on **543,546 records, 87.4 per cent of the estate** —
not a niche. It equals `_I_from_metrics` on **149 of them, 0.027 per cent**. The
two differ by more than 0.10 on 51.9 per cent, mean +0.0610, range −0.974 to
+0.994.

**Rebuilding component I from the metric layer would move 89,056 substations
across a classification band — 16.4 per cent of the scored estate.**

| | published | rebuilt | change |
|---|---:|---:|---:|
| Low | 2,384 | 888 | −1,496 |
| Medium | 86,817 | 69,903 | −16,914 |
| High | 384,996 | 378,467 | −6,529 |
| **Critical** | **67,854** | **92,713** | **+24,859** |
| Extreme | 1,495 | 1,575 | +80 |

67,097 substations move to a worse band and 21,959 to a better one.

**The fill is systematically optimistic.** The Critical band grows by 37 per
cent. Every one of the five largest fleets shifts the same way — France +0.069,
Germany +0.078, United States +0.109, United Kingdom +0.074, Spain +0.085 mean
`dI` — so the fill is not noise around the truth. A hash of a substation's name
has no reason to be biased, and yet across 543,546 records it reads the estate as
safer than its own metrics do.

## Where it bites hardest

| country | scored | mean dI | band change | worse | better |
|---|---:|---:|---:|---:|---:|
| estonia | 614 | −0.294 | **61.2%** | 48 | 328 |
| netherlands | 1,639 | −0.113 | **56.8%** | 284 | 647 |
| turkey | 4,001 | −0.221 | **56.7%** | 446 | 1,824 |
| colombia | 378 | −0.132 | 47.1% | 60 | 118 |
| greenland | 37 | −0.177 | 45.9% | 5 | 12 |
| mexico | 2,436 | +0.021 | 44.5% | 551 | 533 |
| united states | 73,859 | +0.109 | 20.3% | 13,419 | 1,538 |
| united kingdom | 59,744 | +0.074 | 17.7% | 9,231 | 1,348 |
| france | 168,894 | +0.069 | 13.0% | 18,190 | 3,780 |
| germany | 108,016 | +0.078 | 12.2% | 11,745 | 1,398 |

The direction is not uniform. Turkey, Estonia and the Netherlands would get
substantially BETTER under a rebuild; France, Germany, the US and the UK
substantially worse. So the fill does not merely add noise — it reorders
countries against each other, which is precisely what a cross-jurisdiction index
exists to do correctly.

## What follows

This finding decides nothing. It replaces an intention with a number, so the
decision can be made:

1. **Whether to rebuild component I now, at 0.72 coverage**, accepting that
   89,056 substations change band and 24,859 enter Critical — or to hold until
   I7, I8 and I9 exist and rebuild once.
2. **Whether the twenty-six unsourced I4 thresholds are worth sourcing.** If the
   rebuild happens they become load-bearing on published scores. If it does not,
   they never reach a published number.
3. **The `mult_product` chain-provenance finding is now upstream of this.** No
   rebuild can be verified while `R_median` fails to reproduce from published
   components on 69 per cent of records. That finding was already BLOCKING; it is
   now also the gate on this one.

## A correction this measurement forced

Earlier today I reported, repeatedly and in two committed doctrine documents,
that `components.I` sits on **8.1 per cent** of records. That is **Poland's**
figure. I measured one country and stated it as the estate. Estate-wide it is
**87.4 per cent**, and coverage is extremely uneven — France, Germany, Italy,
Israel and Costa Rica at 100 per cent; Austria at 5.0, Poland at 8.1.

The error ran in the safe direction rhetorically — it made the fill sound like a
small problem — and it is the seventh instance in one session of reporting a
measurement from one place as though it held everywhere. Both documents are
corrected.
