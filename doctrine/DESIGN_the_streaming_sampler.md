# DESIGN — the streaming sampler

**Landed** 21 September 2026: `scripts/hazard_accumulate.py`,
`tests/test_hazard_accumulate.py` (23 assertions).

The winter leg is on the order of 1–2 TB and the fire leg ~260 GB. Neither is
stored. A window is fetched, evaluated, reduced to per-cell annual statistics,
and discarded. What survives is a few dozen bytes per cell-year:

    25,165 cells × 86 years × a handful of statistics  ≈ tens of MB

## The three constraints, enforced by shape rather than by comment

From `RESULT_a_raster_can_give_25165_values_not_622104.md`.

**1. Evaluate before aggregating.** `Accumulator.observe()` takes **one
already-evaluated scalar per cell**. It cannot be handed a stack of input
fields, because a caller still holding input fields has not yet done the step
that must come first. The diagnostic lives in the caller; the accumulator never
learns what an input variable is. A sentinel walks the module's AST and fails
if any identifier in the code names a field or an interpolation.

That is the I2 defect pre-empted: for a conditional test like FMICLIM,
thresholding interpolated or pre-averaged inputs is a different operation from
thresholding per timestep and aggregating the outcome.

**2. Nearest cell, never bilinear.** Assignment belongs to the cell index and
is fixed at `floor(x/res + 0.5)`. Nothing here interpolates and nothing here
accepts a coordinate except `fan_out`, which returns the **cell ordinal beside
the value** so the collapse stays auditable — 147 French substations share a
number *because they share a cell*, visibly.

**3. Native resolution only.** The resolution travels with the output, so a
downstream reader cannot lose track of what a number's resolution was.

## What it refuses to do

- **A partial timestep raises.** A short row would bias every statistic it
  touched, silently.
- **A missing value is skipped, not zeroed.** `n` counts real observations, not
  timesteps that went past, so a sea-masked cell does not acquire a mean of
  zero.
- **One observation has no variance.** `variance` returns `None`, not `0.0`.
  Zero would assert certainty from a single reading — the same §7.5 failure as
  the degenerate confidence intervals already in the estate.
- **A point outside the index raises** rather than snapping to a nearest guess.
  An asset off the index means the index is stale, and that should stop the
  run.
- **The normal reports its own coverage.** `normal()` returns
  `(value, years_present, years_expected)`. A caller can still publish a
  "1991–2020 normal" built from four years, but not without being told it was
  four.

## Numerics

Mean and variance use **Welford**, not sum and sum-of-squares. Over 31,412
daily values — 125,648 six-hourly — the naive form loses significant digits to
cancellation exactly where it matters, in the variance of a near-constant
series. The sentinel demonstrates it: on five values near 10⁹ the naive form is
off by more than 10⁻³ while Welford returns 2.5.

## Observing-system regime

Every year carries its regime, per
`FINDING_the_pre1979_boundary_is_not_1979.md`:

    1940–1945  no_upper_air        1970–1978  early_satellite
    1946–1969  pre_satellite       1979–      modern

A module-level assertion fails at import if the standard normal ever stops
lying inside exactly one regime. It lies inside `modern` today, which was
decided for the WMO convention and protects against this by accident.

## Throughput — measured, because compute was the remaining unknown

At full width, 25,165 cells per timestep, on the device VM:

    no thresholds   7.50 ms/timestep   3.36 M pushes/s
    3 thresholds    8.32 ms/timestep   3.02 M pushes/s

    fire    31,412 daily timesteps   →  ~4 minutes
    winter 125,648 6-hourly          →  ~17 minutes

**Pure Python is fast enough, so the accumulator takes no numpy.** Seventeen
minutes of arithmetic against a fetch measured in hours of queue latency and
terabytes of transfer is not the constraint, and this confirms from the compute
side what `RESULT_the_winter_fetch_is_priced.md` concluded from the data side:
**transfer is the binding constraint, not compute.** A dependency-free
accumulator is also one an auditor can read end to end.

## Not built yet

- The **GRIB reader** that turns a downloaded window into per-timestep rows at
  the 25,165 cells. It is the only part that needs a binary format library, and
  it should stay the only part.
- The **FMICLIM diagnostic** itself, which belongs in the caller.
- The **per-country percentile** step (Method B) that turns per-cell normals
  into the operative exposure statistic. Note that this now sits downstream of
  an unresolved question — see
  `FINDING_the_cohort_is_banded_by_two_different_rules.md` — and should not be
  built until the estate has one banding rule.
