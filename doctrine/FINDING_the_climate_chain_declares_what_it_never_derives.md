# FINDING — the climate chain declares what it never derives

**Date** 24 September 2026
**Occasion** A failed ERA5 fetch in the first private pipeline run. Asked whether ERA5 is meant to feed R2 Δ_climate, and directed to read the foundational documents first. They answer it, and the answer overturns the question.
**Status** Measured across all 39 countries and 622,104 published records, and read against doctrine held and doctrine issued.
**Reach** Public. Two of the six measurements below are on every published record.

## The question

`pipeline-enrichment` run #2 (france, dry run) failed its climate step:

```
cdsapi package not installed — using direct HTTP fallback
CDS HTTP fallback failed: HTTP Error 404: Not Found
ERA5 baseline data not available for france.
```

The operator's instruction was that everything must work perfectly. The
obvious reading is that the ERA5 fetch must be repaired. The foundational
documents say otherwise, and the measurements say otherwise with more force.

## What doctrine says

### R2 is declared — in doctrine issued

`SSI_FORMULA_CONSTRUCT_MASTER.md`, "Modifier sources — declared", Class J:

```
| R2 | BOM, Copernicus ERA5 | — | australia v4.0.2 MODIFIERS registry | J |
```

and, in the same master:

> **R2 — "Adaptive IRI + Climate Trajectory"**. Type: *Weight modifier*.
> Range: *Weight redistribution*.
> "Uses CMIP6 SSP2-4.5 projections to adjust IRI metrics for bushfire corridor
> and cyclone exposure. When local hazard risk is low, weight shifts from IRI
> metrics (I3, I9) to structural metrics (I1, I4)."
>
> `IRI_forward(m,s) = IRI_current(m,s) × (1 + 0.15 × clip(Δ_climate, −0.50, +1.00))`

### Δ_climate is CMIP6, not ERA5

The construct's own description names the input: CMIP6 SSP2-4.5 projections.
ERA5 appears in the `sources:` list beside BOM; the quantity the formula
consumes is the projection. So the answer to the occasioning question is **no**
— ERA5 is not the source of Δ_climate by any declaration in the estate.

### ERA5's doctrinal job is I1, I3 and I5, and it is already done

`SSI_FOUNDATION_judgement.yaml` names ERA5-Land as the source of three metrics,
and names the acquisition each time:

| Element | Declared source |
|---|---|
| `I1` | "Derived on 622,079 substations from **four merged ERA5-Land regional boxes**, 2018-2022" |
| `I3` | "ERA5-Land daily maximum 2 m temperature, 2018-2022, resolved per grid cell" |
| `I5` | "ERA5-Land daily maximum 2 m temperature, **already cached in the repository; nothing was fetched for this metric**" |

and the change-log for the I3 re-derivation states it directly:

> "no re-ingestion of ERA5-Land is required, because the raw quantity is
> already carried per record as `_I3_raw_degC_days`."

Four merged regional boxes, cached, pinned, spent. That acquisition is closed.

**`climate.py`'s per-country `fetch_era5_baseline` is a second, unrelated ERA5
path** — monthly means plus daily statistics, per country, via the CDS API —
and it is the one that fails. Repairing it would not touch I1, I3 or I5, which
are the only things doctrine asks ERA5 for.

## Six measurements

### 1. R2 is absent from doctrine held

`SSI_FOUNDATION_judgement.yaml` declares seventeen modifiers:

```
R3_C_mult  R4_F_topo  R6_restoration  R6_seismic  R6c_flood  R6d_wildfire
R6e_winter  R8_adapt  R9_compound  R10_just  R7_cyber_v2  R7_cyber
R6_volcanic  R6_drought  R6_armed_conflict  R6_typhoon  R6_chaebol
```

**R2 is not among them.** Constitution §2 names doctrine *held* as the two YAML
files — the form an officer signs — and the rendered masters as doctrine
*issued*. R2 exists only in the issued form, and there it is marked "declared
from australia v4.0.2 MODIFIERS registry": one jurisdiction's client-side
JavaScript. §2 says country articulations may not alter doctrine. §7.4 forbids
a document derived from another document. This is a Class J declaration that
entered the master from below, and it is the only modifier in the table with
that provenance.

### 2. No published record carries an R2 modifier

France, every shard, 14,567 of 14,567 records in the first alone:

```
R10_just   R3_C_mult   R4_F_topo   R6_restoration   R6_seismic   R6c_flood
R6d_wildfire   R6e_winter   R7_cyber   R7_cyber_v2   R8_adapt   R9_compound
```

Twelve modifiers. No R2. And no weight redistribution occurs anywhere:
`engine.COMPONENT_WEIGHTS` and the intra-component weights are fixed constants,
read identically for every substation in the estate. The declared behaviour of
R2 — weight shifting from I3 and I9 to I1 and I4 when local hazard is low —
does not exist in the deployed engine in any form.

### 3. `climate_trajectory` is published and never scored

`compute_iri_forward` produces `I1_trajectory`, `I2_trajectory`,
`I3_trajectory`. `score_substation` stores them:

```python
if climate_update:
    updated["climate_trajectory"] = {
        "I1_trajectory": climate_update.get("I1_trajectory", 1.0),
        ...
```

and nothing reads them back. No component, no modifier, no normalisation step
consumes the field. Every ingestion module initialises it as `"climate_trajectory": {}`
— the same shape, written by the same hand, as `alert_components`.

The deployed derivation also departs from the declared formula in two ways
beyond its input: there is no `0.15` factor and no `clip(−0.50, +1.00)`, and it
emits three separate per-metric ratios rather than the single weight
redistribution the construct declares.

### 4. `delta_wind_pct` is a constant

The committed file that is the actual input to the only surviving climate
computation:

```
scripts/pipeline/data/cross-cutting/cmip6_ssp245_deltas.csv — 18,990 rows

  lat                153 distinct
  lon                473 distinct
  delta_t_c           31 distinct
  delta_heat_pct      31 distinct
  delta_ice_pct       31 distinct
  delta_wind_pct       1 distinct      ← 0.05, on every row
```

And the code reads it as

```python
delta_wind = best_pt.get("delta_wind_pct", 0.05)
```

so the hardcoded fallback and the file's only value are **the same number**. A
lookup that hits and a lookup that misses are indistinguishable in the output.
There is no observable difference between having the data and not having it.

Measured on the published record, all 39 countries:

| | |
|---|---:|
| substation records | 622,104 |
| carrying `climate_trajectory` | 612,715 |
| **`I2_trajectory` at exactly 1.05** | **595,079 — 97.1% of those carrying it** |
| carrying anything else | 17,636 |

`I2_trajectory` is the published forward-looking wind exposure of a substation.
On 595,079 of them it is a typed constant wearing a CMIP6 filename. This is the
one finding of the six that a reader of the site can see.

### 5. 17,636 records carry a value nothing in the repository can produce

The 17,636 exceptions are not scattered. They are eight countries:

```
norway       5,832 of 6,113        turkey       4,001 of 4,031
finland      3,885 of 3,939        new-zealand  1,558 of 1,589
latvia       1,219 of 4,646        estonia        614 of 1,794
lithuania      505 of 4,901        poland          22 of 27,764
```

The repository holds exactly one CMIP6 file and no CMIP6 cache. That file's
`delta_wind_pct` is constant, so it cannot produce a varying `I2_trajectory`
for any record. Whatever derived these 17,636 values is not in the repository
and cannot be re-run. Poland's 22 are the sharpest case: twenty-two records,
twenty-two distinct values, one occurrence each, inside a country of 27,764
that is otherwise uniformly 1.05.

Constitution §1: every divergence between doctrine and deployment is an open
defect with an owner. A published value that cannot be reproduced from the
estate is that, in its plainest form.

### 6. The failing ERA5 path has no consumer, and cannot go red

`compute_iri_forward` — the only caller of `fetch_era5_baseline` in the
scoring path — takes the baseline, fetches it when absent, and never reads it:

```python
def compute_iri_forward(country, era5_baseline=None, cmip6_deltas=None, cache=True):
    if era5_baseline is None:
        era5_baseline = fetch_era5_baseline(country, cache=cache)   # line 1138
    ...                                                             # never referenced again
```

Constitution §7.9 governs exactly this: *"A guard that is declared and never
consulted is removed or wired in; there is no third state."*

And the failure cannot be seen from outside. Run #2 is green — every step,
including `Run pipeline`, including the job — because:

```python
def cmd_fetch(countries, skip=None, dry_run=False):
    ...
                else:
                    print(f"    {label:<18} ✗ FAILED")
    ...
    return 0                                     # fetch_data.py:220
```

`cmd_fetch` returns 0 unconditionally. Only `cmd_verify` returns non-zero on
incompleteness. **Every data class could fail for all 39 countries and the run
would still exit 0.** §7.5 forbids silent absence; here the absence is not even
silent, it is printed — and then discarded by the return statement two screens
below it. §7.8 asks that no sentinel be permanently red. There is no sentinel
to be red.

Two contributing facts, both measured on run #2: the install step completed in
seven seconds, which is not enough time to install `netCDF4`, `rasterio` or
`cdsapi` — all three declared in `requirements.txt` since 8 June and none
installed by the workflow. `rasterio` absent also disables the seismic GEM
raster fallback at `seismic.py:411`. And `numpy`, which `engine.py:33` imports
unguarded for the canonical Monte Carlo, was present only as a transitive
dependency of `shapely`, which the old step installed by name.

## What the 27 metadata files claim

Twenty-seven live per-country `ssi-metadata.js` files publish:

```js
{ id: "CDS", name: "Copernicus CDS / ERA5-Land", res: "0.1° (~11 km, ERA5-Land + daily-stats)",
  vars: 5, category: "Climate",
  feeds: "R2 Δ_climate (t_mean_c, heat_days, ice_days at 0.1° land grid)" }
```

Three things in that one string are not true of the deployment. The per-country
CDS fetch does not feed R2. Δ_climate does not come from ERA5 in any
declaration. And `t_mean_c`, `heat_days` and `ice_days` from that fetch reach no
published number at all.

§7.9: *"No marker that asserts work not done. A provenance marker, an audit
trail, a named guard or a declared constraint is itself a claim, and is subject
to the same discipline as a measured value."* This is such a marker, twenty-seven
times.

## The `wind_speed` column, in passing

The blocker that opened this investigation deserves recording because it is the
mechanism in miniature. `_parse_climate_csv` is called with six required
columns, the sixth being `wind_speed`, and an unresolvable column returns `None`
for the whole file. No code anywhere in the 331-file pipeline reads
`wind_speed`. And none of the three paths that *produce* a baseline emits it:

```
_process_era5_netcdf     -> lat, lon, t_mean_c, heat_days, ice_days
fetch_ghcnd_for_country  -> lat, lon, t_mean_c, heat_days, ice_days (+ agency, station_id)
the 39 cached JSON grids -> lat, lon, t_mean_c, heat_days, ice_days     [39 of 39]
```

The pipeline cannot produce a file its own reader would accept. The only files
that pass the gate are twelve hand-made CSVs in a sibling clone, and their
`wind_speed` is near-constant per country — switzerland one distinct value
across 55 rows, france two across 651, spain two across 459. A column filled to
open a door, on a door that guards nothing.

They are not committed here and should not be. The committed-CSV branch precedes
the cache branch, so committing france's 651 hand-made rows would *displace* the
pipeline's own 10,454-point cache while adding a fabricated column to the public
record.

## The shape of this

The climate chain is declared at four points and derived at none of them.

| Declared | Derived |
|---|---|
| R2 in the issued master, sourced from one country's client JS | absent from doctrine held; absent from every published record |
| the weight redistribution R2 describes | fixed weights, read identically for every substation |
| `Δ_climate` from CMIP6 | `delta_wind_pct` constant; 595,079 records at the fallback |
| CDS/ERA5 feeding R2, in 27 metadata files | that fetch reaches no published number |

It is the fifth and sixth thing found this session preserved by everything and
produced by nothing — after the record-level `version` field, `W1`–`W10`,
`meta.n_substations`, and `alert_components`. It is the first that reaches a
number on the public record at scale.

The pattern is consistent enough now to name: **this estate's characteristic
defect is not a wrong value. It is a declared relationship that nothing
executes, preserved indefinitely because every downstream operation carries it
forward faithfully.** A rescore preserves `alert_components` perfectly. A merge
preserves `climate_trajectory` perfectly. Fidelity in propagation is exactly
what makes a dead derivation invisible.

## What would close it

Nothing here is proposed, and nothing has been changed. The decisions belong to
the operator, and three of them are amendments under §8, not patches.

1. **R2.** Either declare it in `judgement.yaml` under a provenance pin — with
   the weight redistribution actually implemented — or strike it from the issued
   master and record in the register that it was a single jurisdiction's client
   registry elevated to doctrine. It cannot stay as it is: declared in the
   document, absent from the signature, absent from the data.
2. **`delta_wind_pct`.** A constant reaching 595,079 published records needs
   either a real source or an honest declaration as a placeholder. Under the
   anti-theatre rule, E3 openly declared outranks a fabricated E2, and a CMIP6
   filename containing one repeated number is the fabricated case.
3. **The 17,636.** Establish what produced them, or restate them. A published
   figure that cannot be reproduced from the estate is not defensible under §1
   whichever way it was derived.
4. **The 27 metadata claims.** Correct the claim. Do not build the feed to make
   the claim true.
5. **`fetch_era5_baseline`.** §7.9 admits two states. On the evidence there is
   nothing to wire it into, so the honest state is removal — with the four
   merged regional boxes, which are the ERA5 doctrine actually names, left
   untouched and pinned where they are.
6. **`cmd_fetch` returning 0.** A failed data class should fail the run. This
   one is a pin, and it is the cheapest of the six.

The install step should be corrected regardless — `netCDF4`, `rasterio` and
`cdsapi` are declared and absent, and `numpy` arriving through `shapely` is a
defect on its own terms. But it is housekeeping, not the fix, and it should not
be presented as having addressed anything above.

## Related

- `FINDING_alert_components_is_derived_by_nothing.md`
- `FINDING_era5land_wind_is_interpolated.md`
- `AMENDMENT_DRAFT_I2_two_tier_resolution.md`
- `DECISION_I3_normalisation_method_C.md`
- `DESIGN_the_public_private_boundary.md`
- `FINDING_the_conformance_register_reads_the_engine_against_itself.md`
