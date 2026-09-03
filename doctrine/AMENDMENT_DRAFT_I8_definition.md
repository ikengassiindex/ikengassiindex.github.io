# Amendment (DRAFT) — I8, atmospheric corrosion, defined before its fetch

Status: DRAFT for the operator's pin. Not registered, nothing derived.
Raised: 2026-09-03, before the 590 dmean requests are spent.
I8 is `blocked` and exists on zero records.

---

## 1. Why this is written now

`ERA5_FETCH_PLAN_I1_I2.json` reserves 590 of its 2,065 requests for
`2m_temperature` and `2m_dewpoint_temperature` daily means, labelled "I8". No
definition of I8 exists. That is the same position I1, I2 and I3 were in, and
it is closed the same way — write the computation first, then fetch to it.

Doing so has already changed the answer. See §4.

## 2. What ISO 9223 actually computes

ISO 9223:2012 §8.2 gives a dose-response function for the first-year
corrosion rate of carbon steel:

    rcorr = 1.77 · Pd^0.52 · exp(0.020·RH + f_St)
          + 0.102 · Sd^0.62 · exp(0.033·RH + 0.040·T)          µm/a

    f_St = 0.150·(T − 10)   for T ≤ 10 °C
         = −0.054·(T − 10)  for T > 10 °C

    Pd   annual mean SO2 deposition       mg/(m²·d)
    Sd   annual mean Cl⁻ deposition       mg/(m²·d)
    RH   annual mean relative humidity    %
    T    annual mean temperature          °C

**COEFFICIENTS ARE NOT YET VERIFIED AGAINST THE STANDARD ITSELF.** They were
assembled from secondary sources because ISO 9223 is a paid standard the estate
does not hold. One retrieval returned an internally inconsistent form — f_St as
a multiplier rather than inside the exponential, and the temperature branches
inverted — and was rejected. The structure above was confirmed against the
published zinc equation, which places its own f term inside the exponential.

That is enough to reason about the fetch. **It is not enough to pin.** A copy
of ISO 9223:2012 must be obtained and the coefficients checked before this
amendment is registered. Recorded here rather than discovered after 620,000
records carry the result.

## 3. What the planned fetch supplies

    2m_temperature       daily mean  ->  T
    2m_dewpoint_temperature daily mean -> with T, gives RH

And nothing else.

## 4. The finding: the fetch buys the modifiers, not the drivers

Look at where each variable sits in the function.

**Pd and Sd are the multiplicands.** The corrosion rate is the sum of two
terms, each proportional to a deposition quantity raised to a power. T and RH
appear only inside exponentials that scale those terms.

    Pd = Sd = 0   ->   rcorr = 0, whatever T and RH are.

Neither SO2 deposition nor chloride deposition exists in ERA5-Land. **So the
590 requests reserved for I8 buy the two terms that modulate the answer and
neither of the two that produce it.** I8 cannot be computed at all from this
fetch — not approximately, not as a declared proxy. There is no corrosion
without a corrodent.

This is a different and larger defect than the one recorded against these same
requests in FINDING_era5_fetch_not_viable.md §4, which said only that RH from
daily means is a degraded estimate of daily-mean RH. That remains true (§5) and
is now the smaller of the two problems.

## 5. The nonlinearity, which also survives

RH is a nonlinear function of T and dewpoint. Computing RH per day from the
daily MEAN temperature and the daily MEAN dewpoint, then averaging over days,
is not the annual mean of hourly RH. The error is not signed in general and its
magnitude is unmeasured.

The same rule that broke I2 applies: a nonlinear function of two variables
cannot be computed from their independently pre-aggregated marginals. I1 is
exempt because it is a maximum of one variable. I8 is not.

If I8 is built at all, its RH term should come from hourly T and dewpoint with
RH formed first and averaged second — the same conclusion I2 reached, from the
same rule.

## 6. Time of wetness

ISO 9223 defines τ as the hours per year with RH > 80 % and T > 0 °C. It feeds
the corrosivity CLASSIFICATION tables, not the dose-response function above, so
it is not required for I8 as defined here. It is worth stating that it could
never be computed from daily means either: it is an hourly threshold count, the
same shape as I2's gale threshold.

## 7. What I8 needs that the estate does not have

    Pd   SO2 deposition       EMEP provides modelled deposition for Europe.
                              No equivalent is identified for Canada, the US,
                              Chile, Japan, Korea, Australia, New Zealand,
                              Colombia, Costa Rica, Mexico, Israel, Turkey or
                              Greenland. Under the national-primary discipline
                              each needs its own source before a fallback.
    Sd   Cl⁻ deposition       No global observational product is identified.
                              Distance-to-coast with a decay function is the
                              conventional proxy and would be a Convention #7
                              declaration of real weight, since Sd^0.62 carries
                              the marine half of the metric outright.

Both are dataset decisions, not definitional ones, and neither is closed here.

## 8. Recommendation

**Do not spend the 590 dmean requests.** They cannot produce I8, and the two
variables they carry would need re-fetching hourly if I8 is ever built.

**Do not define I8's normalisation or anchor yet.** Both are meaningless until
Pd and Sd have sources.

**Do obtain ISO 9223:2012** before this is pinned, and verify §2.

I8 stays `blocked`, with `blocked_on` naming the deposition datasets rather
than the ERA5 fetch — which is what it has been blocked on all along, wrongly
recorded.
