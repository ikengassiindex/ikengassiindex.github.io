# FINDING — a second name-hash generator, which the Pin 14 sweep did not reach

**Date** 21 September 2026
**Measured on** the deployed tree, all 39 countries, 622,104 records.
**Status** measurement only. Nothing written.
**Found while** trying to settle additive versus multiplicative composition.

---

## The generator

`scripts/refresh_v42_modifiers_re_composite.py::_compute_v42_modifiers` builds
six modifiers — `R6c_flood`, `R6d_wildfire`, `R6e_winter`, `R8_adapt`,
`R9_compound`, `R10_just` — as follows, read from the source:

    exposure = _COUNTRY_HAZARD_BASELINES[country][key]      # hand-set constant
    center   = r_min + exposure * (r_max - r_min)
    value    = _det_var(f"{substation_id}|{name}|v42|{mod}", center, 0.10)

    def _det_var(seed, base, pct):
        h = int(hashlib.md5(seed.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
        return base * (1 + (h * 2 - 1) * pct)

The per-country exposure is a constant typed into a dictionary — every value a
multiple of 0.05, e.g. `poland: {flood 0.55, wildfire 0.35, winter 0.65}`. The
per-asset variation is an **MD5 of the substation's id and name**.

## Why the Pin 14 sweep missed it

`FINDING_pin14_sweep_complete.md` enumerated the writes of
`enrich_esg_gaps.py` by AST and tested every one. It was complete **for that
generator**. This is a different one, in a different file, with a different seed
string — `"<id>|<name>|v42|<modifier>"` against `"<name>:42"` — so no test in
that sweep could have matched it.

**The lesson is about the method, not the miss.** Enumerating one generator's
writes exhaustively proves nothing about a second generator. The sweep should
have started from the FIELD and asked what writes it, not from the generator and
asked what it writes. That is the same shape as
`DOCTRINE_a_check_must_read_the_artefact.md`: the question has to start at the
artefact.

## Reproduction

Under the parameterisation currently in the source, exact bit-for-bit:

    modifier          present   reproduced    rate
    R9_compound       619,171      153,829   24.8%
    R10_just          619,171      128,969   20.8%
    R6e_winter        619,171      121,054   19.6%
    R8_adapt          619,171      116,727   18.9%
    R6d_wildfire      619,171       99,407   16.1%
    R6c_flood         619,171       82,067   13.3%
    TOTAL           3,715,026      702,053   18.9%

Per country it ranges from 50.4 per cent (switzerland) to 2.6 per cent (turkey),
and the six countries absent from the baseline table reproduce at 0.2 per cent.

**18.9 per cent is a FLOOR, not a measurement of how much is synthetic.** The
remainder does not reproduce under *this* parameterisation — a different
`jitter_pct`, an edited baseline, or a later overwrite would all break an exact
match while leaving the value just as synthetic. What is established is the
mechanism, which is read from the source and needs no reproduction rate; the
rate only bounds how much of the deployed data came from this exact call.

## What the doctrine already says

All three hazard modifiers carry, from the 21 August pin:

    provenance.basis: engine semantics at the pinned commit;
                      no prior document used as evidence
    blocked_on:       no verifiable provenance in the deployed pipeline
                      at the pinned commit

So the estate already declared these unsourced. This finding says what they are
instead, and the script's own docstring names the remedy: the values are a
"first-order first-cut per Convention #7 **pending full raster ingestion at SSI
Foundation Q3 2026**."

## Why it settled a question rather than only adding to the pile

The additive-versus-multiplicative review concluded, on three independent tests,
that `R6d_wildfire`, `R6e_winter`, `R6_typhoon`, `R6_volcanic` and
`R6_armed_conflict` sit beside `R6c_flood` and should be additive. Measured, that
reclassification moves **115,578 bands — 51.6 per cent of the attributable set**,
taking Extreme from 17,067 to 44,092.

Every unit of that movement would be the arithmetic of a hand-set constant times
a hash. The methodological argument is sound and the change is still wrong to
make now: it would present as a methodology correction while being a rescaling
of an arbitrary number. **Acquire the rasters, then reclassify.** The move is
then one registry field per modifier, because all seventeen already share the
form `clip(1 + k·index, range)` and the add/mult split is a consumption tag with
no modelling content behind it.

## Re-derive

    recompute _det_var("<substation_id>|<name>|v42|<modifier>", center, 0.10)
    with center = r_min + baseline * (r_max - r_min), and compare to the
    published modifier. Baselines and ranges are in
    scripts/refresh_v42_modifiers_re_composite.py.
