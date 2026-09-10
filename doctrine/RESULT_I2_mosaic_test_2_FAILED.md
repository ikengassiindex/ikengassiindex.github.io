# Result — mosaic attempt 2. Headline PASS, and it does not survive audit.

Run 2026-09-10, after attempt 1 failed. Criteria committed in ac1bed5e before
the run. Attempt 2 met all three bars. It is being recorded as a FAILURE
because scrutinising the pass showed that one of the three bars did not test
the construction it was supposed to test.

---

## 1. What attempt 2 reported

    TEST 1  persistence      min r 0.842  median 0.873   PASS
    TEST 2  worth it         median gap closed 265%      PASS
    TEST 3  scale invariance median r 0.937              PASS
    VERDICT printed: mosaic is supported

## 2. Why that verdict is withdrawn

**TEST 3 did not test the construction.** As implemented it compares
texture(chosen statistic) against texture(MEDIAN). With the mean chosen it
compared the MEAN against the MEDIAN — two central statistics, which agree
almost by definition. r = 0.937 measures nothing the construction depends on.

What the construction depends on: texture is estimated from the MEAN and
multiplied onto a field of MAXIMA, because I2 is a threshold-excess metric
driven by extremes. Measured directly, at the same 0.80 bar:

    france   168,478   r 0.716
    germany  108,016   r 0.415
    uk        59,744   r 0.564
    italy     41,662   r 0.497
    median             r 0.530   FAIL

Mean-derived texture does not transfer to maxima. The construction multiplies
a maximum field by a ratio that describes mean conditions, and the two are
only weakly related.

**TEST 2's overshoot is not explained by the baseline mismatch I suspected.**
CERRA's mean-field CV against its max-field CV is 0.85x to 1.39x — comparable.
France's mosaic CV of 0.192 exceeds even the mean-field baseline of 0.168. The
mosaic is a third field, combining ERA5's between-cell pattern with CERRA's
within-cell pattern; since the two sources correlate at only 0.26 to 0.71,
their combination carries more variance than either. Not obviously wrong, but
not "closing the gap toward CERRA" either. The statistic does not mean what
the test claimed.

## 3. What survives, and it is worth keeping

TEST 1 stands. Texture derived from the period MEAN is a genuinely stable
property of the site: r 0.842 to 0.963 across six countries and two
independent years. Terrain does leave a persistent, measurable signature in
CERRA's mean wind field.

It is simply not the quantity a threshold-excess metric on maxima can use.

## 4. Decision

The mosaic is not adopted. Attempt 1 failed on persistence, attempt 2 on
transfer, and the rule set before attempt 2 was that two attempts is the limit.

**Option D proceeds:** I2 from CERRA at 5.5 km for the 513,554 substations
inside its domain; I2 declared ABSENT for the 108,550 outside. One instrument,
one meaning for every published value.

## 5. One question deferred, not abandoned

Attempt 1 failed because a single month's maximum is a sample of about one
storm. Texture from maxima over FIVE YEARS would keep the quantity in the max
domain while removing that sampling problem. It is the only remaining variant
with a physical argument behind it.

It is not attempt 3. Testing it requires five years of CERRA — which option D
is about to fetch for its own reasons. So the question is deferred until its
evidence exists as a by-product, and is answered from data in hand rather than
used to justify acquiring it. That ordering is the point.

## 6. The generalisable lesson

Attempt 1's failure was caught by a pre-registered gate. Attempt 2's failure
was caught only by auditing a PASS.

A pre-registered criterion protects against moving the bar. It does not
protect against a bar that measures the wrong thing — and a passing test
invites far less scrutiny than a failing one. Both of the weak tests here
were written by the same hand that wanted the result.
