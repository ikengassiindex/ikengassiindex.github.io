# Phase 1.5 — Operator Workflow

Closes the F-L4-2-extended cohort data gap. Three data classes:
- **Socio-economic** (P15-F-1 + P15-F-2): ✅ 38/39 SoT countries shipped (US gated on operator's free CENSUS_API_KEY)
- **Climate** (ERA5 via Copernicus CDS): 11/39 done, 28 to fetch (~12 min batch)
- **Seismic** (PGA via GEM 2018 global): 0/39 done, awaiting one-time operator CSV download

This doc gives the exact commands to close each remaining gap.

---

## Step 1 — Commit the P15-F-2 batch (5 sec)

15 non-EU agency fetchers + 246 sub-national regions emitted per session,
plus the chain reorder so per-agency data wins over Eurostat NUTS-2 for
EFTA countries that have both.

```bash
cd /Users/cedricberard/ikengassiindex.github.io

git add scripts/pipeline/ingestion/socioeconomic.py \
        scripts/pipeline/ingestion/climate.py \
        scripts/pipeline/ingestion/seismic.py \
        scripts/pipeline/fetch_data.py \
        scripts/pipeline/requirements.txt \
        scripts/pipeline/PHASE_1_5_OPERATOR_WORKFLOW.md \
        scripts/pipeline/data/{australia,canada,chile,colombia,costa-rica,greenland,iceland,israel,japan,korea,new-zealand,norway,switzerland,turkey,uk}/agency_regional_socioeconomic.csv

git commit -m "P15-F-2: 16 non-EU agency fetchers + 246 sub-national regions

Architecture: _NON_EU_AGENCY_FETCHERS registry dispatches per country slug
to dedicated state-of-record fetcher. Chain order: agency > Eurostat NUTS-3
> World Bank national. Each fetcher returns canonical region-keyed dict
shape; failures degrade visibly per Convention #56.

Per-country granularity (+ Mexico's 32 estados native = 17/17 non-EU):
  au(8)  ca(13)  cl(16)  co(33)  cr(7)   gl(5)   is(8)  il(7)
  jp(47) kr(17)  nz(16)  no(15)  ch(26)  tr(16)  uk(12) us(51 key-gated)

Coverage: F-L4-2 cohort socio gap closed 14/22 → 21/22.
US fetcher code-complete; live test gated on CENSUS_API_KEY registration.

Also: --only-class filter on fetch_data.py for surgical batch runs."
```

---

## Step 2 — US Census ACS live run (~10 sec)

Operator's CENSUS_API_KEY is activated. Export + run:

```bash
# Option A — one-shot for this session
export CENSUS_API_KEY=<paste-your-key-here>
python3 scripts/pipeline/fetch_data.py --country us --only-class socioeconomic

# Option B — persistent (preferred)
echo 'export CENSUS_API_KEY=<paste-your-key-here>' >> ~/.zshrc
source ~/.zshrc
python3 scripts/pipeline/fetch_data.py --country us --only-class socioeconomic
```

Expected output: `us: ✓ (51 records)` + writes
`scripts/pipeline/data/us/agency_regional_socioeconomic.csv` with 51
state-level rows (median HH income proxy for GDP/cap, unemp rate from
B23025_002/005, elderly % from 12 age-group columns).

Sanity check — California should be ~$91,905 median HH income, Mississippi
the floor ~$49k. Top: District of Columbia ($101k). The 2.5× spread
between top and bottom matches ACS 2022 5-year publication.

Commit:
```bash
git add scripts/pipeline/data/us/agency_regional_socioeconomic.csv
git commit -m "P15-F-2b: US Census ACS 5-year 2022 (51 states)"
```

---

## Step 3 — Climate batch via Copernicus CDS (~12 min)

Prerequisites (one-time, already done):
- `~/.cdsapirc` configured with operator's CDS key (proven via Korea pilot, 713 grid points)
- `pip install --user cdsapi netCDF4` (proven during P15-D-1)

Run the climate-only batch over the 28 missing countries:

```bash
python3 scripts/pipeline/fetch_data.py --all-missing --only-class climate
```

What this does:
1. Verifies which 28 countries still lack `data/cross-cutting/era5_baseline_<country>.csv`
2. For each: bbox-clips ERA5 monthly means 2000-2020 (2m temp + 10m wind + max/min temp) via CDS
3. Processes netCDF → CSV with columns `lat, lon, t_mean_c, heat_days, ice_days, wind_speed`
4. Writes to `data/cross-cutting/era5_baseline_<country>.csv`

Each country ~25 sec. Total wall-clock ~12 min. CDS queue can spike during
peak hours (CET afternoons) — overnight runs are smoother.

Per-country progress is logged; resumable if interrupted (already-present
CSVs short-circuit the fetcher at step 1).

Verify + commit:
```bash
python3 scripts/pipeline/fetch_data.py --all-missing --verify
git add scripts/pipeline/data/cross-cutting/era5_baseline_*.csv
git commit -m "P15-A: ERA5 climate baselines for 28 countries (CDS batch)"
```

---

## Step 4 — Seismic GEM 2023.1 GeoTIFF fallback (one-time, manual)

**Updated P15-B-2 (8 June 2026)**: format is GeoTIFF raster, not CSV.
GEM 2018 is only available as PDF/PNG; GEM 2023.1 publishes the raw
raster at 2.5× higher resolution. Switched to 2023.1.

**Prerequisites**:
```bash
pip install --user rasterio>=1.3
# Heavy dep (~50 MB with GDAL backend), only used by this fallback.
```

**Operator action**:

1. Go to https://www.globalquakemodel.org/product/global-seismic-hazard-map
2. Click "Open Version Download" (right panel) — opens https://cloud.openquake.org/s/6SnFk2f92JEr76H
3. Download the GeoTIFF (~50-200 MB depending on the package — Nextcloud share-link UI)
4. Rename to `gshm-2023-1.tif` and place at `scripts/pipeline/data/cross-cutting/gshm-2023-1.tif`
5. Run:
   ```bash
   python3 scripts/pipeline/fetch_data.py --all --only-class seismic
   ```

The fetcher's `fetch_gem_global_for_country()` opens the GeoTIFF via
rasterio, bbox-clips per country, and writes
`data/<country>/gem_pga475.csv` (lon, lat, pga_g columns) — same downstream
schema as the prior design.

Estimated batch time: <2 min for all 39 countries (rasterio bbox windowing
is fast; main cost is per-pixel iteration for the larger bboxes like US/CA).

### License caveat (CC BY-NC-SA 4.0)

GEM 2023.1 is licensed CC BY-NC-SA 4.0 — Attribution + **Non-Commercial** + ShareAlike.

| Use case | Compliant? |
|---|---|
| SSI Index methodology research, USCO deposits, academic papers | ✅ Yes |
| Internal Ikenga risk-assessment tooling, free-public dashboards | ✅ Yes (non-commercial use) |
| Paid client advisory using SSI Index outputs | ⚠️ Borderline — verify with GEM |
| Selling SSI Index as commercial product | ❌ Need commercial license (request via "License Request" button on product page; typically fast turnaround for legitimate use cases) |

### Fallback: pre-extract CSV if rasterio is a blocker

If you can't install rasterio (e.g. M-series Mac with GDAL build issues),
you can pre-extract the GeoTIFF to a CSV using QGIS or any GIS tool, then
place the result at `scripts/pipeline/data/cross-cutting/gem_global_pga475.csv`
with columns `lon, lat, pga_g`. The fetcher tries the GeoTIFF first, falls
through to CSV second.

---

## Final state — what closes the F-L4-2-extended cohort

After Steps 2 + 3 + 4 complete:

| Class | Before P15 | After Steps 1-4 |
|---|---|---|
| Socio-economic | 14/22 | **22/22** ✅ |
| Climate | 2/22 (au, us) | **22/22** ✅ |
| Seismic | 0/22 | **22/22** ✅ |
| **All three complete** | 0/22 | **22/22** ✅ |

The cohort acceptance gate closes when `--f-l4-2-cohort --verify` shows
`Complete: 22/22`.

Subsequent pipeline run (`run_pipeline.py --all`) will then re-score the
22 cohort countries through the full v4.0.2 chain (L1 → L5) and validate
strict-mode schema compliance per PR-7's acceptance harness.
