# Result — mosaic test 1, FAILED. Recorded before any retry.

Run 2026-09-10, against criteria committed in 87f43946 BEFORE the second CERRA
month was opened. This file records the failure. A pre-registered test that
fails and is then quietly retried is worse than no pre-registration, so the
failure is written down first and the retry, if any, is numbered.

---

## 1. The result

    country           n     T1 r     CV era5   CV mos   CV cerra   gap closed   T3 r
    france      168,478    0.587       0.120    0.139      0.133         144%   0.679
    germany     108,016    0.339       0.135    0.140      0.146          41%   0.283
    norway        6,113    0.436       0.160    0.180      0.190          68%   0.449
    uk           59,744    0.384       0.064    0.123      0.092         210%   0.492
    italy        41,662    0.427       0.206    0.230      0.234          87%   0.330
    spain        12,438    0.467       0.154    0.254      0.182         355%   0.619

    TEST 1  persistence      min 0.339  median 0.431   FAIL   (needed all >=0.60, median >=0.80)
    TEST 2  worth it         median gap closed 116%    pass   (needed >=50%)
    TEST 3  scale invariance median 0.471              FAIL   (needed >=0.80)

    VERDICT: the mosaic as constructed is NOT supported.

## 2. What failed and why it matters

Texture derived from January 2018 and from January 2019 agrees at the same
substation at r ~ 0.43. Terrain — exposure, roughness, orography — does not
change between years. This does. So the quantity proposed as a multiplier on
roughly 500,000 published values is substantially weather.

Had it been applied, the estate would have carried spatial structure that is
the footprint of two particular Januaries, presented as a property of the
sites.

## 3. TEST 2 PASSED AND THAT IS EVIDENCE AGAINST, NOT FOR

Spain closes 355 per cent of the gap and the UK 210 per cent. The mosaic CV
EXCEEDS the CV of CERRA itself.

Real terrain texture cannot do that. It would move the coarse field toward the
fine field, not past it. Overshooting means variance is being added that is not
present in CERRA either — the signature of injected noise.

**A spread statistic rewards noise.** T2 measures whether the field varies
more, and noise makes anything vary more. That is precisely why persistence was
made the gate and spread merely a secondary check. On T2 alone this would have
been endorsed at 116 per cent of target.

Recorded because the same trap is available in any future "does the finer
source help" question, and the answer is never a spread statistic alone.

## 4. TEST 3 diagnoses the mechanism

Texture computed on the period maximum against texture computed on the period
median correlates at only 0.471 — within the SAME month, on the SAME data.

So the max-based texture is not even self-consistent across the distribution.
A monthly maximum gust field is one or two storms; it is a sample of size
roughly one from the weather, and the ratio it produces is not a stable
property of anything.

## 5. What this does and does not reject

REJECTS: texture derived from a MONTHLY MAXIMUM, applied as a multiplier.
That specific construction, which is what was pre-registered and tested.

DOES NOT REJECT, and is not thereby supported either: texture derived from a
different statistic over a longer period. There is a physical argument that it
would behave differently — terrain speed-up over ridges and shelter in valleys
are MEAN effects, estimated by averaging many events, and T3 says directly that
the maximum is the unstable end of the distribution.

That argument was available before the test and was not made. It is being made
after a failure, which is the weakest possible position to argue from, and it
is recorded as such.

## 6. Standing decision if nothing further is attempted

Option D stands: I2 derived from CERRA at 5.5 km for the 513,554 substations
inside its domain, and declared ABSENT for the 108,550 outside. One field, one
instrument, every published value meaning the same thing. Component I coverage
reaches 0.719 for 82.6 per cent of the estate and stays at 0.629 for the rest.
