# FINDING — the cohort is banded by two different rules, and "Low" means two different things

**Measured** 21 September 2026, over all 39 jurisdictions and all 622,104
published records.

Set out to test one hypothesis from `FINDING_the_red_sentinel_census.md`: that
`validate_schema`'s alarm of *"30,015 Italian substations (72.04 %) have
classification mismatched to R_median band"* was the validator applying the
wrong band rule, not three quarters of Italy being misclassified.

**The hypothesis is confirmed. Testing it uncovered something larger.**

## 1. The hypothesis, confirmed

`validate_schema.py::_expected_band_v42` applies **absolute** cutoffs —
`<0.25 Low, <0.50 Medium, <0.75 High, <1.00 Critical, else Extreme` — and never
reads `_band_norm_R_P5` / `_band_norm_R_P95`.

Italy's published classification is reproduced by the **per-country normalised**
rule for **41,662 of 41,662 records — 100.00 %**, and by the absolute rule for
0. The validator's own example, `7000000001`: `R_median = 0.4713`, anchors
`0.4531 / 0.7530`; *Medium* absolute, *Low* normalised, **published Low**.

The alarm on Italy is a false alarm.

## 2. What the sweep found instead

Every country is **purely one rule**. None mixes them.

    PER-COUNTRY NORMALISED   11 countries   483,706 assets   77.8 %
        canada finland france germany italy japan norway sweden turkey uk us

    ABSOLUTE                 28 countries   138,398 assets   22.2 %
        australia austria belgium chile colombia costa-rica czechia denmark
        estonia greece greenland hungary iceland ireland israel korea latvia
        lithuania luxembourg mexico netherlands new-zealand poland portugal
        slovakia slovenia spain switzerland

Agreement is exact, not approximate: Spain, Poland and Austria each match the
absolute rule on **100.00 %** of records, chance-corrected **κ = 1.000**.
Italy matches the absolute rule on 28 % with **κ = 0.011** — that is chance.

## 3. Why this matters more than the validator

**The word "Low" on the site denotes two different quantities.**

In Italy it means *bottom ~15 % of Italian substations* — a within-country
rank. In Austria it means *R_median below 0.25* — a position on the absolute
scale. They are printed in the same column, in the same colour, under the same
heading.

The clearest demonstration is Spain against Italy:

    Spain,  published (absolute)      Medium 11 %  High 81 %  Critical 7 %
    Spain,  under the normalised rule Low 22 %  Medium 28 %  High 28 %  Critical 16 %  Extreme 5 %
    Italy,  published (normalised)    Low 23 %  Medium 29 %  High 28 %  Critical 15 %  Extreme 5 %

Spain's underlying distribution is **almost identical to Italy's**. Spain is
published as 81 % High and Italy as 28 % High. The entire apparent difference
between the two countries is which rule was applied to them.

Any cross-country comparison of bands in this index — a league table, a map
colour, a "share of Critical assets" — currently compares two different
measurements. That is not a presentation problem to be fixed in the front end;
the numbers themselves are not comparable.

## 4. The cost of harmonising, measured before deciding

Moving the 28 absolute countries onto the normalised rule:

    assets in those countries          138,398
    published bands that would move     81,598   59.0 % of them, 13.1 % of the estate

    Low      -> Medium   28,141        High -> Medium   10,199
    High     -> Critical  7,429        Medium -> High    6,320
    Medium   -> Low       5,524        Critical -> Extreme 3,939

    austria 99.9 %   czechia 77.7 %   australia 71.9 %   spain 69.5 %   portugal 68.7 %

Austria restates essentially in full. This is a large restatement and it is not
proposed here.

## 5. What must NOT be done

**Do not "fix" the validator to use the normalised rule.** That silences a true
alarm for the 28 countries whose bands genuinely are absolute, and converts a
visible inconsistency into an invisible one.

**Do not flip the 28 countries without deciding what a band means.** The
normalised rule is not obviously the right one: it was introduced (Task #461,
22 July 2026) because absolute cutoffs collapsed ~80 % of Wave-4 countries into
*High*, which is a presentation complaint, and it changes the band's semantics
from *absolute physical risk threshold* to *within-country ranking*. The
docstring says so plainly. A within-country ranking cannot, by construction,
say that one country is more exposed than another — every country has a bottom
15 %.

## 6. Recommendation

One rule, cohort-wide, **declared in `judgement.yaml`** as a pinned
methodological choice with its reasoning, and the validator then checks against
the declared rule rather than a rule hard-coded in its own source. Until that
is pinned, the honest interim is that every country declares which rule it was
banded under, and the validator reads that declaration — so the inconsistency
is visible in the data rather than in a test nobody can run.

Which rule it should be is a methodology decision, and it is the operator's. It
should be taken knowing that the absolute rule makes countries comparable and
compresses within-country detail, and the normalised rule does the exact
reverse, and that no single band label can do both.

## 7. A measurement error of mine, recorded

The first version of this sweep reported **27 "mixed" countries**, with
proportions like *Spain 30.5 % normalised / 69.5 % absolute*. That was wrong,
and wrong in a way worth naming: I counted `published == normalised` **first**,
so every record where the two rules happen to agree was credited to the
normalised rule. The residue looked like a mixture and was not one.

It was caught by asking whether the agreement survived a correction for chance.
It did not: Spain's apparent 30.5 % normalised agreement has κ = 0.011 against
the absolute rule's κ = 1.000. **Every country is pure.** A raw agreement rate
between two classifiers with skewed label distributions is not evidence, and
the estate should not accept one again without κ beside it.

## 8. The 92 records that match neither rule

France 70, US 21, Norway 1. All 92 sit within **4.06 × 10⁻⁵** of a band cutoff
after normalisation, and most sit exactly on 0.5000000000 to within 1.1 × 10⁻¹⁶.
They are floating-point boundary ties between the full-precision anchors used at
scoring time and the 4-decimal anchors stored on the record. Benign, fully
explained, and an argument for an explicit tolerance at the cutoffs rather than
for a re-score.
