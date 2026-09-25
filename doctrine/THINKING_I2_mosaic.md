# Thinking — the mosaic, and the one move that makes it sound

> ## CORRECTION, 21 September 2026 — the definition in §3 was wrong
>
> §3 defined mosaic theory as *"individually non-material public pieces,
> assembled, can yield a material picture."* The operator challenged it:
> **is it not "individually material and non-material"?** It is. §3 is
> corrected below and the original sentence is kept there, struck, so the
> error is visible rather than edited away.
>
> Two doctrines carry this name and they are not the same:
>
> **Securities law** (the *Dirks v. SEC* lineage) is the precise one, and it
> has two axes — materiality AND publicness. An analyst may lawfully combine
> **"non-material non-public information and material public information"**
> into a mosaic that is itself material. *Material public* information is
> expressly part of it.
>
> **National security and FOIA** (*CIA v. Sims*, 1985) is where the original
> sentence came from. It permits withholding **"seemingly innocuous details"**
> because **"aggregated disclosures could expose intelligence sources"**, and
> the open-data literature follows: **"seemingly harmless fragments of
> information can, when aggregated, enable sensitive inferences."** There the
> pieces genuinely are individually non-material — that is the whole
> justification for withholding them.
>
> The original sentence collapsed the two and kept the weaker one.
>
> **What the correction exposes matters more than the wording.** NEITHER form
> fits this estate's construct. The securities mosaic needs a NON-PUBLIC leg
> and the SSI Index has none — it is published. *Sims* needs pieces an agency
> withholds as innocuous, and this estate withholds nothing. What the estate
> actually has is open data plus a second open source, some of it individually
> material: a 400 kV substation's location and voltage are not innocuous.
>
> The framing that does fit is the **mosaic EFFECT** of the open-data and
> re-identification literature — harm arising from aggregation and linkage of
> public sources — and it is stronger than what it replaces:
>
> **An index is not a tile in the mosaic. It is the assembled mosaic.** Its
> whole value proposition is the assembly: scattered public sources made
> comparable on one scale, normalised, ranked, published. Its marginal
> disclosure is not a new fragment. It is that the estate performed the
> aggregation FOR the adversary and saved them the linkage step, which in that
> literature is the expensive one.
>
> This does not disturb the measurement in
> `RESULT_the_circularity_test.md` — 0.151 → 0.538 remains the right quantity.
> It changes what the number MEANS: not "the index adds material information"
> but "the index supplies the assembly."
>
> Sources, read 21 September 2026: *Mosaic theory (investments)* and *Mosaic
> effect*, Wikipedia, for the two doctrinal formulations and the *Sims*
> quotations. Both are encyclopaedia articles, not primary law. **The primary
> sources — *Dirks v. SEC* 463 U.S. 646 (1983) and *CIA v. Sims* 471 U.S. 159
> (1985) — have NOT been read**, and under §7.6 must be before either is cited
> in a paper. Nothing above should be treated as a legal opinion; it is a
> reading of how the term is used.

Raised 2026-09-10 on the operator's direction: proceed with D, but populate
what D leaves absent; auditable, nothing invented; consider the mosaic theory.

Not a proposal for pin. A line of reasoning, with the experiment that would
falsify it named at the end.

---

## 1. Why the two-tier design failed, stated precisely

Measured at the same 396,000 substations, same month:

    CERRA / ERA5 level ratio     0.891   (0.845 Germany to 0.936 UK)
    correlation between fields   0.26 UK · 0.49 France · 0.71 Norway

Two distinct problems, and only one of them is a calibration problem.

**Level.** CERRA runs 11 per cent below ERA5. Fixable by bias correction.
Because I2 is a threshold-EXCESS sum, an 11 per cent level shift near the
threshold produces a far larger shift in the metric — but it is still just an
offset, and offsets can be corrected.

**Rank.** A correlation of 0.26 in the UK means the two fields disagree about
WHICH substations are windy. No bias correction touches that. Two substations
would be ranked differently depending only on which instrument measured them.

Option B fails on the second problem, not the first. That is why no amount of
calibration rescues it.

## 2. The move

We have been asking two instruments to agree on an absolute value. They do not
and will not. But we are not short of absolute level: **ERA5 covers the whole
globe on one ruler.** What ERA5 lacks is what happens INSIDE its 31 km cell —
and that is precisely what the fine sources have and what no global product can
give.

So stop asking the fine source for a level. Ask it only for the deviation.

    LEVEL    from the globally uniform source. One ruler, every substation.
    TEXTURE  from the finest source covering that substation: how this site
             differs from the neighbourhood ERA5 already measured.

Concretely, for substation s inside ERA5 cell C:

    texture(s) = FINE_stat(s) / mean over C of FINE_stat
                 = 1 exactly, where no finer source covers s

    gust'(s, d) = ERA5_gust(C, d) x texture(s)
    I2_raw(s)   = mean annual sum of max(0, gust'(s, d) - GUST_THRESHOLD)

By construction, the mean of texture over any ERA5 cell is 1. So the fine
source cannot move a region's level — only redistribute within it. The 11 per
cent offset disappears because CERRA's absolute level is never used. The rank
disagreement is not papered over; it is REFRAMED. We stop asking CERRA whether
France is windier than Spain — ERA5 answers that, consistently, everywhere —
and ask it only how this substation differs from its immediate neighbours,
which ERA5 cannot answer at all.

The absolute threshold survives, which matters: it was pinned deliberately to
contrast with I3's local-percentile logic. Every value is still on one scale.

## 3. What the mosaic theory actually licenses

~~Its proper form: individually non-material public pieces, assembled, can
yield a material picture.~~ **Superseded 21 September 2026 — see the correction
at the head of this file.** Its proper form depends on which doctrine is meant:
in securities law, *material public* information combined with *non-material
non-public* information; in the FOIA and national-security line, individually
innocuous details whose aggregation is disclosive. This estate's own construct
fits neither, because nothing here is non-public — it is the open-data **mosaic
effect**, in which an index is not a tile but the assembled mosaic.

The part of §3 that survives unchanged is the failure mode, which is what this
section was actually written to guard against. Its failure mode is the seam —
assembling pieces that do not belong together and getting a confident wrong
answer. The discipline that separates the two here:

    - one LEVEL source for the whole estate. The mosaic contributes texture
      only. Levels are never mixed.
    - the combination rule is IDENTICAL everywhere, including where texture
      is 1. There is no special case for the covered regions.
    - texture = 1 is not a missing value. It is a declared statement that no
      finer information exists for this site, and it is the correct value
      under that state of knowledge.
    - every record names its texture source and resolution.

And the property that makes it safe to build incrementally:

    ADDING A SOURCE CHANGES ONLY THE SUBSTATIONS IT COVERS.

Because texture normalises to 1 within each ERA5 cell, adding BARRA2 moves
Australian records and touches nothing else. No anchor moves, no re-scoring of
the estate, no restatement. Compare options B and C, where introducing a tier
changes a shared anchor and re-scores every substation in the index.

That is the difference between a mosaic and a patchwork.

## 4. The candidate mosaic

Verified to exist, with a citable description:

    Europe             CERRA            5.5 km   in hand, one month fetched
    Australia          BARRA2           12 km (BARRA-R2) / 4.4 km (BARRA-C2)
                                        BOM, GMD 17, 731-757, 2024; NCI ob53
    North America      RDRS             10 km    GEM-based, HESS 25, 4917, 2021
                       (Canada, US, and northern Mexico)
    Japan              DSJRA-55         5 km     JMA downscaling of JRA-55,
                                        SOLA 12, 2016

Not identified, and therefore texture = 1 until they are:

    korea · chile · colombia · costa-rica · new-zealand
    (BARRA2's domain may reach New Zealand — unverified, and it must be
     checked against the file rather than assumed, as CERRA's was.)

Coverage if all four land: roughly 96 per cent of the estate carries texture
from a source finer than 31 km. The remainder is honestly plain ERA5.

## 5. The experiment that must pass first, and could kill this

**Texture must be a persistent property of the site, not noise.**

Terrain, exposure and roughness do not change between years. If texture is
real, texture computed from one period and texture computed from another must
agree at the same substation. If they do not, texture is weather noise dressed
as terrain, and applying it would inject spurious structure into 500,000
published values — worse than the coarse field it replaces.

    TEST 1 — persistence
      compute texture from CERRA January 2018 and from CERRA January 2019
      correlate, per country, across substations
      PASS: r high and stable. FAIL: r low -> abandon; texture is noise.

    TEST 2 — does it buy anything
      compute the within-country CV of (ERA5 level x texture)
      it should move from the ERA5 baseline toward the CERRA baseline
      france 0.120 -> ? against CERRA's 0.133
      uk     0.064 -> ? against CERRA's 0.092
      PASS: materially closes the gap. FAIL: the texture is real but too
      weak to matter, and the mosaic is not worth its cost.

    TEST 3 — scale invariance
      texture is derived from a maximum statistic and applied to a daily
      series. That assumes the ratio holds across the distribution. Check
      the texture ratio computed on the median day against the one computed
      on the annual maximum. If they diverge, texture must be applied as a
      distribution mapping rather than a multiplier.

Test 1 costs one more CERRA month: 1,488 against a 90,000 limit, and the
January probe returned in about two hours.

## 6. What I am not claiming

That this is standard practice. It is a defensible construction — separating
a globally consistent level from locally resolved texture is what statistical
downscaling does — but the specific form here is ours, and it should be
declared as a documented method rather than cited to a standard.

That texture is truth. It is one reanalysis's opinion about within-cell
variation, and it inherits that model's biases.

That the seams vanish. A substation with 5.5 km texture and one with none are
not equally resolved, and the record must say which is which. What the
construction buys is that they remain COMPARABLE — measured with one ruler,
differing only in how much detail was available.

## 7. If all three tests pass

I2 is derived once, globally, on ERA5 level with mosaic texture. One
definition, one threshold, one anchor, one scale, and a declared per-record
resolution. Component I coverage reaches 0.719 for the whole estate rather
than for 82.6 per cent of it.

If test 1 fails, D stands as written and the 108,550 keep an absent I2.
