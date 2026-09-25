# RESULT — a 0.25° raster can give the estate 25,165 values, not 622,104

**Measured** 21 September 2026 · `scripts/measure_grid_cell_collapse.py` ·
read from the published per-asset data of all 39 jurisdictions, 622,104 assets,
none missing coordinates.

Asked *before* the fetch-and-sample layer was written, because the answer
decides its shape — and decides something the index will have to declare.

## The measurement

    resolution   occupied cells   collapse   as % of assets
      0.50°           9 256        67.2x          1.49 %
      0.25°          25 165        24.7x          4.05 %
      0.10°          73 761         8.4x         11.86 %

Occupancy at 0.25°, the grid both ERA5 and CEMS publish on:

    cells holding exactly one asset     5 425
    cells holding more than one        19 740
    assets sharing a cell             616 679   — 99.1 % of the estate
    largest single cell                 2 855 assets

**99.1 % of the estate shares its hazard value with at least one other
substation, and in one cell with 2,854 others.** That is not an approximation
to be reduced by care. Every asset in a cell receives the identical number,
because the raster contains one number for that cell.

## What this says about the published modifiers today

Inside the 19,740 shared cells, where a raster can supply at most 19,740
distinct values:

    R6d_wildfire      500 434 distinct values
    R6e_winter        424 361 distinct values
    R6c_flood         575 006 distinct values

Roughly **96 % of the apparent per-asset variation in the published hazard
modifiers is variation no gridded hazard dataset could produce.** It is the
name hash. This is not a new finding — the name-hash sweep established the
mechanism — but it is the first time its magnitude has been stated in the units
that matter: not "the field is hash-derived" but "the field claims twenty-five
times more spatial resolution than any hazard raster on earth could give it".

## The consequence nobody will like

When the real rasters land, **the hazard modifiers will become far less varied
than they are today.** Five hundred thousand distinct wildfire values will
become at most twenty-five thousand. Assets that today carry visibly different
wildfire exposure will carry identical values, correctly, because they sit
2 km apart inside one 28 km cell.

That will look like a loss of resolution and a regression. It is the opposite:
it is the removal of resolution that was never there. **It must be stated
before the fetch, not explained afterwards** — a published index that becomes
flatter without warning invites exactly the wrong inference.

## Three design consequences, which the sampler must honour

**1. Sample 25,165 cells, not 622,104 points.** A 24.7× reduction in per-
timestep work, exactly equal in result, because the extra 597,000 lookups
return numbers already computed. This is not an approximation for speed.

**2. Do not request a finer grid than the product's native resolution.**
0.10° would give 73,761 cells and would be *manufacturing* per-asset variation
by interpolation — the identical error this result is about, committed
deliberately. ERA5 and CEMS publish at 0.25°; the estate requests 0.25°.

**3. Nearest cell, never bilinear — and evaluate before aggregating.** For a
conditional diagnostic such as FMICLIM, interpolating the inputs and then
applying the threshold is not the same operation as applying the threshold and
then combining. That is the nonlinearity rule that broke I2, and bilinear
interpolation is the respectable-looking way to commit it. The order is fixed:
evaluate the diagnostic per cell per timestep on native values → aggregate over
time → fan the per-cell result out to the assets in that cell.

## What the per-asset record must carry

So that the collapse is auditable rather than hidden, each asset's hazard entry
carries the cell it was drawn from and the resolution it was drawn at. An
auditor must be able to see that 147 French substations share one number
*because they share one cell*, without re-deriving the grid.

## Note on method

Occupancy is computed globally. Computed per country it came to 25,694 cells,
529 too many, because a border cell holds assets from two countries and is one
cell to the raster. The first version of the instrument made that error; the
figures above are from the corrected one, and 5,425 + 19,740 = 25,165 now
reconciles with the global count.
