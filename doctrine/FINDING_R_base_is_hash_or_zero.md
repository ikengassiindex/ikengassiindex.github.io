# FINDING — `R_base` is a name hash on 77.5% of the estate and zero on 12.6%

**Date** 17 September 2026
**Measured on** the deployed tree, all 39 countries, 622,104 records, every
shard. Full census, exact reproduction rather than correlation.
**Status** measurement only. Nothing written.
**Found by** following the R7 cutover cost down to why `R_median` moved on only
43.9 per cent of the records the substitution acts on.

---

## The chain this concerns

    R_base  = 0.30·C + 0.10·V + 0.25·I + 0.10·E + 0.20·S + 0.05·T
    R_median = soft_clip_upper(R_base × Π mult_i) + Σ (add_i − 1)

`R_base` is the foundation. Every modifier — consequence, topology, restoration,
seismic, cyber, adaptation, compound, just-transition — multiplies it.

## What `R_base` is made of

    481,952 records   77.5%   all six components reproduce from md5(name)
     78,493 records   12.6%   components {} — R_base is exactly 0
     61,594 records    9.9%   components present, NOT from this generator

For the first group: 2,891,698 of 3,261,276 component cells reproduce
**bit-for-bit** from

    vary(0.35, name + '_' + K, 0.30)

at `scripts/enrich_esg_gaps.py`, where `vary` is a deterministic MD5 of the
substation's own name. The rate is 88.7 per cent on each of C, V, I, E, S and T
independently — the uniformity is itself the signature.

**There is no population on this estate where `R_base` is known to be real.** The
third group is only "not from this generator"; where it came from is not
established here and should not be assumed.

## The zero-base population, and the direction of its error

78,493 records carry `components: {}`. `compute_r_base` sums weight × 0, so
`R_base` is exactly zero, `R_median` collapses to the additive residue, and every
multiplicative modifier — R3, R4, R6, R7, R8, R9, R10 — is inert. Nothing
multiplicative can move them, which is why the R7 substitution cannot reach them.

What they are published as:

    Low      65,738   83.6%
    Medium   12,893   16.4%
    High / Critical / Extreme        0    0.0%

**A record with no component data cannot be classified above Medium.** Not by
policy — by arithmetic. And the effect on the published index is large:

    published band   total     of which zero-base    share
    Low            189,211           65,600          34.7%
    Medium         159,928           12,893           8.1%
    High           164,836                0           0.0%
    Critical        83,340                0           0.0%
    Extreme         24,724                0           0.0%

**More than a third of every "Low" classification the index publishes is a
substation with no component data.** The index presents its least-scored assets
as its safest, and that is the single worst direction for the error to run in a
tool whose stated purpose is anti-maladaptation in policy decision-making. It
steers attention away from exactly the infrastructure nobody has scored.

It is also the opposite of Convention #56. Visibly-honest degradation would show
these as Unclassified — as Switzerland's records were once described. They are
shown as Low.

Where they are:

    austria    95.0%   poland     91.9%   slovenia   90.9%   lithuania  89.7%
    czechia    87.9%   luxembourg 87.7%   belgium    81.7%   latvia     73.8%
    netherlands 69.9%  estonia    65.8%   denmark    49.5%   colombia   49.2%

For ten countries the published index is majority zero-base.

## The irony, and it is the actionable part

These records are **not** unmeasured. Every one of the 78,493 carries a metrics
block:

    _I_from_metrics   78,493   100.0%
    I6                78,493   100.0%
    I1                78,491   100.0%
    I3                78,489   100.0%
    I5                78,489   100.0%
    I4                77,859    99.2%
    I2                71,807    91.5%

They carry the six I-metrics derived from primary sources — CERRA, ERA5-Land,
IEEE C57.91, the estate's own OSM line geometry — and a real, derived
`_I_from_metrics` on every single record.

**So the records holding real derived data are the ones published as "Low",
because that data is not wired into the score; and the records holding a hash of
their own name get a full classification.** The fabricated population outranks
the measured one.

## Why `fix_wave4_r_base_regression.py` does not solve this

That script exists, diagnoses this exact arithmetic, and works. Measured today:
**all eight of its `BROKEN_COUNTRIES` — spain, italy, france, portugal, germany,
sweden, japan, us — now carry zero zero-base records.** The fix succeeded
completely on its targets.

Its target list is a hardcoded constant, not a measurement. The 25 countries
carrying the defect today are a different set, none of them on the list — they
are the Phase 4c cohort refreshed later by
`refresh_v42_modifiers_re_composite.py`, which the script's own docstring names
as the cause: it "populates per-substation modifier values … but does NOT
re-invoke compute_r_base(components)".

But the deeper reason it does not solve this is that its remedy assumes
components exist to recompute from. Here they do not. Recomputing `R_base` from
`components: {}` returns zero again.

## What would actually close it, and what that costs

`components.I` has a real counterpart already on the record — `_I_from_metrics`,
present on 100 per cent of this population, per the operator decision of
31 August 2026 to publish both and swap when coverage is complete. Wiring it in
gives `R_base = 0.25 × I` for these records.

That is a quarter of the equation. **C, V, E, S and T have `_from_metrics` on
zero records estate-wide**, because every metric beneath them sits on zero
records (`FINDING_what_the_components_fill_costs.md`). So even the best available
move leaves three quarters of `R_base` unsourced — and on the other 481,952
records, that three quarters is currently a hash.

This is not a defect with a cheap fix. It is the acquisition programme the
operator directed on 29 August — every substation classified with real data —
stated in its true size for the first time.

## What is NOT claimed

- Not that the 61,594 third-group records are real. Only that this generator did
  not produce them.
- Not that `fix_wave4_r_base_regression.py` is faulty. It worked on its targets.
- Not that wiring `_I_from_metrics` into `components.I` is correct without a
  pin. It changes published scores and is a Bible §8 act.
- Not a cause for the 398,073 records whose `mult_product` does not reproduce.
  Those are almost entirely disjoint — 22 records overlap.

## Re-derive

    python3 scripts/measure_r7_cutover_cost.py      # zero-base surfaces as the 43.9%
    # components reproduction: vary(0.35, name + '_' + K, 0.30) vs components[K]
