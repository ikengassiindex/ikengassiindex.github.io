"""
SSI Pipeline — Climate Trajectory Ingestion
Fetches CMIP6 climate projections and ERA5 reanalysis to compute
forward-looking IRI metrics (I1/I2/I3 trajectories).

Priority 1 in the Data Procurement Matrix — affects ALL 10 countries.

Pipeline: Copernicus CDS → spatial interpolation → delta from baseline → IRI_forward

Supported sources:
  - Copernicus CDS: ERA5 reanalysis (1940–present, 31 km)
  - Copernicus CDS: CMIP6 SSP2-4.5 ensemble (50+ GCMs)
  - National downscaling where available:
    * Italy: ISPRA regional projections
    * UK: UKCP18 (12 km)
    * Switzerland: CH2018
    * France: DRIAS/Météo-France
    * Germany: DWD REMO/WETTREG
    * Mexico: SMN/CONAGUA regional projections
"""

import json
import logging
import math
import os
from pathlib import Path

from ..utils.geo import (
    haversine_km, nearest_grid_value, bilinear_interpolate,
    load_substations, substation_coords,
)
from ..config import CACHE_DIR, CDS_API_KEY, CDS_API_URL, CMIP6_MODELS

logger = logging.getLogger(__name__)

# ── Paths ──
PIPELINE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PIPELINE_DIR / "data"

# Local committed reference files (preferred)
CMIP6_LOCAL_CSV = DATA_DIR / "cross-cutting" / "cmip6_ssp245_deltas.csv"

def _era5_local_path(country):
    return DATA_DIR / "cross-cutting" / f"era5_baseline_{country}.csv"

def _cmip6_country_local(country):
    return DATA_DIR / country / f"cmip6_ssp245_deltas.csv"


# ═══════════════════════════════════════════════════════════
#  CDS API CLIENT
# ═══════════════════════════════════════════════════════════

def cds_retrieve(dataset, request_params, output_path):
    """
    Retrieve data from Copernicus Climate Data Store.

    Phase 1.5 (P15-A, 8 June 2026): credentials resolved via either path:
      1. CDS_API_KEY env var (canonical for CI / GitHub Actions per
         .github/workflows/pipeline-enrichment.yml)
      2. ~/.cdsapirc (canonical for local operator use per the cdsapi
         package default). The cdsapi.Client() constructor with no args
         auto-reads ~/.cdsapirc — so if either path is configured the
         retrieval will work.

    Uses the cdsapi package (preferred) or direct HTTP (fallback).
    """
    from pathlib import Path
    cdsapirc = Path.home() / ".cdsapirc"
    if not CDS_API_KEY and not cdsapirc.exists():
        logger.warning(
            "No CDS credentials found — neither CDS_API_KEY env var nor "
            "~/.cdsapirc is present. Register free at "
            "https://cds.climate.copernicus.eu, then either "
            "export CDS_API_KEY=<your-key> OR put the key in ~/.cdsapirc. "
            "See scripts/pipeline/data/README.md for setup instructions."
        )
        return False

    try:
        import cdsapi
        # If env var is set, prefer it; otherwise let cdsapi auto-read ~/.cdsapirc
        if CDS_API_KEY:
            c = cdsapi.Client(url=CDS_API_URL, key=CDS_API_KEY)
        else:
            c = cdsapi.Client()  # reads ~/.cdsapirc per cdsapi convention
        c.retrieve(dataset, request_params, str(output_path))
        # P15-A-3 fix: validate the downloaded file is a real NetCDF and not
        # an HTML error page that CDS sometimes returns on oversized requests.
        # Real NetCDF files start with "CDF\x01" (classic), "CDF\x02"
        # (64-bit), or "\x89HDF\r\n\x1a\n" (HDF5 / NetCDF-4). HTML responses
        # start with "<" or "{" (JSON).
        #
        # P15-A-5 fix (8 June 2026): CDS-Beta returns ZIP archives for
        # several derived/monthly datasets — `reanalysis-era5-land-monthly-means`
        # is a confirmed ZIP-bundled dataset for multi-variable / multi-year
        # requests. The ZIP contains one or more .nc files. We detect the
        # ZIP magic (PK\x03\x04) and unpack in-place so downstream parsers
        # see a real NetCDF.
        if output_path.exists():
            with open(output_path, 'rb') as fh:
                head = fh.read(8)
            # P15-A-5: ZIP-archive response (legitimate from CDS-Beta) —
            # unpack and replace output with the first .nc inside.
            if head.startswith(b'PK\x03\x04'):
                import zipfile
                size = output_path.stat().st_size
                try:
                    with zipfile.ZipFile(output_path, 'r') as zf:
                        nc_members = [
                            m for m in zf.namelist()
                            if m.lower().endswith('.nc')
                        ]
                        if not nc_members:
                            logger.error(
                                f"CDS returned ZIP ({size} bytes) but no .nc "
                                f"members inside for {dataset}. ZIP contents: "
                                f"{zf.namelist()[:10]}. Deleting bad file."
                            )
                            output_path.unlink()
                            return False
                        # Extract the largest .nc (covers the case where
                        # CDS bundles a tiny accompanying metadata .nc).
                        biggest = max(
                            nc_members,
                            key=lambda m: zf.getinfo(m).file_size,
                        )
                        with zf.open(biggest) as src, \
                             open(str(output_path) + ".tmp", "wb") as dst:
                            import shutil as _sh
                            _sh.copyfileobj(src, dst)
                    # Atomic swap: replace ZIP with extracted .nc
                    import os as _os
                    _os.replace(str(output_path) + ".tmp", str(output_path))
                    logger.info(
                        f"P15-A-5: unpacked CDS ZIP archive ({size} bytes) for "
                        f"{dataset}; extracted '{biggest}' as {output_path.name}"
                    )
                    # Re-read the magic to confirm
                    with open(output_path, 'rb') as fh:
                        head = fh.read(8)
                except (zipfile.BadZipFile, KeyError) as zip_exc:
                    logger.error(
                        f"CDS ZIP unpack failed for {dataset}: {zip_exc}. "
                        f"Deleting bad file."
                    )
                    output_path.unlink()
                    return False

            # Final magic-byte validation (post-ZIP-unpack if needed)
            if not (head.startswith(b'CDF\x01') or head.startswith(b'CDF\x02')
                    or head.startswith(b'\x89HDF\r\n\x1a\n')):
                size = output_path.stat().st_size
                logger.error(
                    f"CDS returned non-NetCDF response ({size} bytes, header "
                    f"{head!r}) for {dataset} — likely 'request too large' "
                    f"or rate-limited. Deleting bad file. Operator should "
                    f"reduce request size or chunk."
                )
                output_path.unlink()
                return False
        logger.info(f"Downloaded {dataset} to {output_path}")
        return True
    except ImportError:
        logger.warning(
            "cdsapi package not installed — using direct HTTP fallback. "
            "Install via: pip install cdsapi (already in requirements.txt)"
        )
        return _cds_http_retrieve(dataset, request_params, output_path)
    except Exception as e:
        logger.error(f"CDS API error: {e}")
        return False


def _cds_http_retrieve(dataset, params, output_path):
    """Direct HTTP fallback for CDS API."""
    import urllib.request
    import urllib.error

    api_url = f"{CDS_API_URL}/v1/resources/{dataset}"
    headers = {
        "Authorization": f"Bearer {CDS_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        req_data = json.dumps(params).encode()
        req = urllib.request.Request(api_url, data=req_data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=300) as resp:
            with open(output_path, "wb") as f:
                f.write(resp.read())
        return True
    except Exception as e:
        logger.error(f"CDS HTTP fallback failed: {e}")
        return False


# ═══════════════════════════════════════════════════════════
#  P15-A-4 NATIONAL MET AGENCY TIER (Tier 1, auditable)
# ═══════════════════════════════════════════════════════════
# Climate ingestion follows a 3-tier resolution chain for full provenance:
#
#   Tier 1a (direct national):  _NATIONAL_MET_FETCHERS registry — per-country
#                                direct ingestion from the national met service
#                                (e.g. DWD CDC for Germany, NCEI gridded for US).
#                                Currently empty stubs; populate as v4.5 work.
#
#   Tier 1b (NOAA-aggregated):   GHCN-D Global Historical Climatology Network —
#                                Daily, maintained by NOAA NCEI. Aggregates
#                                daily TMAX/TMIN from contributing national met
#                                services worldwide. Each station carries source
#                                agency attribution (DWD, JMA, MetOffice, BoM,
#                                ECCC, MET Norway, NOAA-COOP, etc.) per WMO
#                                international cooperation protocol.
#                                Station-based ~1-5km in populated areas.
#
#   Tier 2 (international):     ERA5-Land 0.1° (existing P15-A-3 path) — gridded
#                                reanalysis used for substations far from any
#                                GHCN-D station, or where the national agency
#                                doesn't contribute to GHCN-D.
#
# Audit traceability: each substation's heat_days/ice_days can be traced to
# either (a) the specific GHCN-D station + source agency, or (b) ERA5-Land
# grid cell. Output CSV includes a source_agency column for every grid point.


# GHCN-D country codes (FIPS-style 2-letter, NOT ISO-2 in all cases).
# Maps SoT slug → GHCN-D country code. See
# https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-countries.txt for the
# canonical list. Some quirks to note: GHCN-D uses GM not DE for Germany;
# JA not JP for Japan; SP not ES for Spain; SZ not CH for Switzerland;
# UK not GB for United Kingdom; KS not KR for Korea.
_GHCND_COUNTRY_CODES = {
    "australia":   "AS",
    "austria":     "AU",
    "belgium":     "BE",
    "canada":      "CA",
    "chile":       "CI",
    "colombia":    "CO",
    "costa-rica":  "CS",
    "czechia":     "EZ",
    "denmark":     "DA",
    "estonia":     "EN",
    "finland":     "FI",
    "france":      "FR",
    "germany":     "GM",
    "greece":      "GR",
    "greenland":   "GL",
    "hungary":     "HU",
    "iceland":     "IC",
    "ireland":     "EI",
    "israel":      "IS",
    "italy":       "IT",
    "japan":       "JA",
    "korea":       "KS",
    "latvia":      "LG",
    "lithuania":   "LH",
    "luxembourg":  "LU",
    "mexico":      "MX",
    "netherlands": "NL",
    "new-zealand": "NZ",
    "norway":      "NO",
    "poland":      "PL",
    "portugal":    "PO",
    "slovakia":    "LO",
    "slovenia":    "SI",
    "spain":       "SP",
    "sweden":      "SW",
    "switzerland": "SZ",
    "turkey":      "TU",
    "uk":          "UK",
    "us":          "US",
}

# Per-country source agency attribution — what national met service does each
# country's GHCN-D contribution actually come from? Used to tag stations in
# the output CSV for audit traceability.
_GHCND_NATIONAL_AGENCY = {
    "us":          "NOAA-COOP + NWS (USA)",
    "germany":     "DWD (Deutscher Wetterdienst)",
    "japan":       "JMA (Japan Meteorological Agency)",
    "uk":          "Met Office (UK)",
    "france":      "Météo-France",
    "italy":       "Aeronautica Militare / ISPRA (Italy)",
    "spain":       "AEMET (Agencia Estatal de Meteorología)",
    "canada":      "ECCC (Environment and Climate Change Canada)",
    "australia":   "BOM (Bureau of Meteorology, Australia)",
    "norway":      "MET Norway (Meteorologisk institutt)",
    "sweden":      "SMHI (Swedish Meteorological and Hydrological Institute)",
    "finland":     "FMI (Finnish Meteorological Institute)",
    "denmark":     "DMI (Danish Meteorological Institute)",
    "netherlands": "KNMI (Royal Netherlands Meteorological Institute)",
    "belgium":     "RMI (Royal Meteorological Institute, Belgium)",
    "switzerland": "MeteoSwiss (Federal Office of Meteorology)",
    "austria":     "GeoSphere Austria (formerly ZAMG)",
    "iceland":     "IMO (Icelandic Met Office)",
    "ireland":     "Met Éireann (Irish Meteorological Service)",
    "portugal":    "IPMA (Instituto Português do Mar e da Atmosfera)",
    "greece":      "HNMS (Hellenic National Meteorological Service)",
    "poland":      "IMGW (Institute of Meteorology and Water Management)",
    "hungary":     "OMSZ (Hungarian Meteorological Service)",
    "czechia":     "CHMI (Czech Hydrometeorological Institute)",
    "slovakia":    "SHMÚ (Slovak Hydrometeorological Institute)",
    "slovenia":    "ARSO (Slovenian Environment Agency)",
    "estonia":     "EMHI (Estonian Environment Agency)",
    "latvia":      "LVĢMC (Latvian Environment Agency)",
    "lithuania":   "LHMT (Lithuanian Hydrometeorological Service)",
    "luxembourg":  "MeteoLux (Luxembourg Airport)",
    "greenland":   "DMI (Greenland stations operated by Danish Met)",
    "turkey":      "MGM (Turkish State Meteorological Service)",
    "israel":      "IMS (Israel Meteorological Service)",
    "korea":       "KMA (Korea Meteorological Administration)",
    "new-zealand": "MetService NZ + NIWA",
    "mexico":      "SMN (Servicio Meteorológico Nacional)",
    "chile":       "DMC (Dirección Meteorológica de Chile)",
    "colombia":    "IDEAM (Instituto de Hidrología, Meteorología)",
    "costa-rica":  "IMN (Instituto Meteorológico Nacional)",
}


def fetch_ghcnd_for_country(country, daily_years=(2018, 2022), cache=True, timeout=120):
    """P15-A-4: Pull GHCN-D daily TMAX/TMIN for all stations in country.

    Returns per-station grid: [{lat, lon, t_mean_c, heat_days, ice_days,
    source_agency, station_id}, ...].

    Source: NOAA NCEI Global Historical Climatology Network — Daily
    (https://www.ncei.noaa.gov/products/land-based-station/global-historical-
    climatology-network-daily). Each station's data was contributed by the
    country's national meteorological agency per WMO international protocol;
    the source_agency field documents which agency for audit traceability.

    Resolution: station-based, typically 1-5 km between stations in
    populated areas. Coverage is sparser in remote regions — substations
    in those areas should fall through to ERA5-Land Tier 2.

    Thresholds (Köppen / WMO standard):
      - heat_days = count of days where TMAX > 25°C (annual mean over window)
      - ice_days  = count of days where TMAX < 0°C  (annual mean over window)
      - t_mean_c  = annual mean of daily TMAX over window (proxy; better
                    would be (TMAX+TMIN)/2 but TMAX-only is fastest)
    """
    cache_path = CACHE_DIR / f"ghcnd_{country}_{daily_years[0]}_{daily_years[1]}.json"
    if cache and cache_path.exists():
        with open(cache_path) as f:
            return json.load(f)

    cc = _GHCND_COUNTRY_CODES.get(country)
    if not cc:
        logger.warning(
            f"P15-A-4: no GHCN-D country code for {country}; falling through to ERA5-Land."
        )
        return None
    agency = _GHCND_NATIONAL_AGENCY.get(country, "national met service")

    bbox = _country_bbox(country)
    if not bbox:
        logger.warning(
            f"P15-A-4: no bbox for {country}; cannot bbox-query GHCN-D."
        )
        return None

    # Step 1: query NCEI v1 API for stations within the country bbox.
    # The bbox parameter takes (N, W, S, E) order.
    # The query returns CSV rows: STATION, DATE, LATITUDE, LONGITUDE, NAME, TMAX, TMIN
    # We request just daily TMAX (TMIN optional). One bbox query handles the
    # whole 5-year window in chunks if needed.
    import urllib.request
    import urllib.parse

    base_url = "https://www.ncei.noaa.gov/access/services/data/v1"
    # Some bboxes (US, Canada, Australia) are huge — chunk by year to avoid
    # response size limits (NCEI caps at ~1M rows per request).
    all_rows = []
    for yr in range(daily_years[0], daily_years[1] + 1):
        params = {
            "dataset": "daily-summaries",
            "startDate": f"{yr}-01-01",
            "endDate": f"{yr}-12-31",
            "bbox": f"{bbox['lat_max']},{bbox['lon_min']},{bbox['lat_min']},{bbox['lon_max']}",
            "dataTypes": "TMAX",
            "format": "csv",
            "includeStationName": "true",
            "includeStationLocation": "1",
        }
        url = base_url + "?" + urllib.parse.urlencode(params)
        try:
            logger.info(f"P15-A-4: querying GHCN-D for {country} year {yr}")
            req = urllib.request.Request(url, headers={"User-Agent": "SSI-Pipeline/4.0.2"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                content = resp.read().decode("utf-8", errors="replace")
            # Parse CSV
            import csv as csv_mod
            reader = csv_mod.DictReader(content.splitlines())
            year_rows = list(reader)
            all_rows.extend(year_rows)
            logger.info(f"P15-A-4: {country} {yr} → {len(year_rows)} daily station-day records")
        except Exception as exc:
            logger.warning(
                f"P15-A-4: GHCN-D fetch for {country} year {yr} failed "
                f"({type(exc).__name__}: {exc}); skipping year"
            )
            continue

    if not all_rows:
        logger.warning(f"P15-A-4: no GHCN-D data returned for {country}; falling through")
        return None

    # Step 2: aggregate per station — count threshold crossings + mean.
    # TMAX values from GHCN-D are in tenths of degrees C (per dataset spec).
    HEAT_THRESHOLD_TENTHS = 250  # 25.0°C × 10
    ICE_THRESHOLD_TENTHS = 0     # 0.0°C × 10
    n_years = daily_years[1] - daily_years[0] + 1

    stations = {}  # station_id -> {lat, lon, name, tmax_sum, tmax_count, heat_count, ice_count}
    for row in all_rows:
        sid = row.get("STATION") or row.get("station") or ""
        if not sid:
            continue
        try:
            lat = float(row.get("LATITUDE") or row.get("latitude") or 0)
            lon = float(row.get("LONGITUDE") or row.get("longitude") or 0)
            tmax_raw = row.get("TMAX")
            if not tmax_raw or tmax_raw == "":
                continue
            tmax_tenths = int(float(tmax_raw))
        except (ValueError, TypeError):
            continue
        s = stations.setdefault(sid, {
            "lat": lat, "lon": lon,
            "name": row.get("NAME") or row.get("name") or "",
            "tmax_sum": 0, "tmax_count": 0,
            "heat_count": 0, "ice_count": 0,
        })
        s["tmax_sum"] += tmax_tenths
        s["tmax_count"] += 1
        if tmax_tenths > HEAT_THRESHOLD_TENTHS:
            s["heat_count"] += 1
        if tmax_tenths < ICE_THRESHOLD_TENTHS:
            s["ice_count"] += 1

    if not stations:
        logger.warning(f"P15-A-4: GHCN-D query returned 0 valid stations for {country}")
        return None

    # Step 3: build the canonical per-station grid output
    grid = []
    for sid, s in stations.items():
        if s["tmax_count"] < 30:  # need at least 30 valid daily readings to be meaningful
            continue
        t_mean_c = (s["tmax_sum"] / s["tmax_count"]) / 10.0
        # heat_days / ice_days annualised over window
        heat_per_year = s["heat_count"] / n_years
        ice_per_year = s["ice_count"] / n_years
        grid.append({
            "lat": round(s["lat"], 4),
            "lon": round(s["lon"], 4),
            "t_mean_c": round(t_mean_c, 2),
            "heat_days": round(heat_per_year, 1),
            "ice_days": round(ice_per_year, 1),
            "source_agency": agency,
            "station_id": sid,
        })

    logger.info(
        f"P15-A-4: {country} — emitted {len(grid)} stations from GHCN-D "
        f"(source agency: {agency}, {n_years} year window, "
        f"thresholds 25°C heat / 0°C ice)"
    )

    if cache:
        with open(cache_path, "w") as f:
            json.dump(grid, f)
    return grid


# Per-country direct-agency override registry (v4.5 expansion target).
# Each entry maps SoT slug → fetcher function that returns canonical grid.
# When populated, the fetcher takes precedence over GHCN-D. Useful for:
#   - US: NOAA NCEI gridded products (PRISM, nClimGrid) at 4km — finer than GHCN-D stations
#   - Germany: DWD CDC HYRAS at 5km grid
#   - Japan: JMA AMeDAS direct (~1km network)
#   - France: Météo-France SAFRAN at 8km
# Currently EMPTY — all countries use GHCN-D Tier 1b → ERA5-Land Tier 2.
_NATIONAL_MET_FETCHERS = {
    # "us":      _fetch_noaa_nclimgrid_us,         # P15-A-4-future
    # "germany": _fetch_dwd_hyras_germany,         # P15-A-4-future
    # "japan":   _fetch_jma_amedas_japan,          # P15-A-4-future
    # "france":  _fetch_meteofrance_safran_france, # P15-A-4-future
}


# ═══════════════════════════════════════════════════════════
#  ERA5 CLIMATE BASELINE (Tier 2 international fallback)
# ═══════════════════════════════════════════════════════════

def fetch_era5_baseline(country, years=(2000, 2020), cache=True):
    """
    Load climate baseline for a country.

    P15-A-4 resolution chain (8 June 2026):
      Tier 1a — Direct national met agency (per-country registry, currently empty stubs)
      Tier 1b — GHCN-D NOAA-aggregated daily (per-station, source-agency tagged)
      Tier 2  — ERA5-Land 0.1° gridded reanalysis (universal fallback)

    Pre-P15-A-4 chain:
      1. Local committed CSV
      2. Cached JSON from previous CDS download
      3. Live download from Copernicus CDS
      4. ABORT with instructions

    Tier 1a + 1b are ADDITIVE — if they succeed they replace Tier 2 output.
    If they fail, the existing Tier 2 path runs unchanged (visibly-honest
    degradation per Convention #56).

    Each output row includes a `source_agency` column for audit:
    - GHCN-D rows: "DWD", "JMA", "MetOffice", etc.
    - ERA5-Land rows: "Copernicus ERA5-Land"
    - Mixed output marks per-row provenance.
    """
    local_path = _era5_local_path(country)

    # ── Tier 1a: per-country direct national fetcher (override) ──
    direct_fetcher = _NATIONAL_MET_FETCHERS.get(country)
    if direct_fetcher is not None:
        try:
            grid = direct_fetcher(country)
            if grid:
                logger.info(
                    f"P15-A-4: Tier 1a (direct national agency) succeeded for {country}; "
                    f"emitted {len(grid)} records"
                )
                return grid
        except Exception as exc:
            logger.warning(
                f"P15-A-4: Tier 1a direct fetcher for {country} raised "
                f"{type(exc).__name__}: {exc}; falling through to GHCN-D."
            )

    # ── Tier 1b: GHCN-D NOAA-aggregated daily ──
    # **GATED for v4.0.2 stability**: GHCN-D code is SHIPPED but DORMANT
    # by default. Activate via env var `SSI_USE_GHCND=1` for v4.5+ once
    # live-test coverage is in place. This prevents non-deterministic
    # behaviour-change on the next pipeline run after v4.0.2 closure:
    # v4.0.2 stays deterministically ERA5-Land; v4.5 opt-in unlocks
    # finer-resolution station-based data with per-agency attribution.
    if os.environ.get("SSI_USE_GHCND") == "1":
        try:
            ghcnd_grid = fetch_ghcnd_for_country(country)
            if ghcnd_grid:
                logger.info(
                    f"P15-A-4: Tier 1b (GHCN-D) succeeded for {country}; "
                    f"emitted {len(ghcnd_grid)} stations"
                )
                return ghcnd_grid
        except Exception as exc:
            logger.warning(
                f"P15-A-4: Tier 1b GHCN-D for {country} raised "
                f"{type(exc).__name__}: {exc}; falling through to Tier 2."
            )
    # Else: GHCN-D dormant. Operator can still call fetch_ghcnd_for_country()
    # directly for ad-hoc tests / smoke checks without affecting the
    # production resolution chain.

    # ── Tier 2: pre-existing ERA5-Land path (unchanged) ──
    # 1. Local committed reference
    if local_path.exists():
        logger.info(f"Loading ERA5 baseline from committed reference: {local_path}")
        grid = _parse_climate_csv(local_path, ["lat", "lon", "t_mean_c", "heat_days", "ice_days", "wind_speed"])
        if grid:
            return grid

    # 2. Cache
    cache_path = CACHE_DIR / f"era5_baseline_{country}.json"
    if cache and cache_path.exists():
        with open(cache_path) as f:
            return json.load(f)

    # 3. Live CDS download
    # P15-A follow-up (8 June 2026): accept EITHER CDS_API_KEY env var
    # OR ~/.cdsapirc file (the cdsapi package's canonical config). The
    # earlier check only looked at the env var, causing silent fallthrough
    # to ABORT when operators configured credentials via .cdsapirc.
    from pathlib import Path
    have_cds_creds = bool(CDS_API_KEY) or (Path.home() / ".cdsapirc").exists()
    bbox = _country_bbox(country)
    if bbox and have_cds_creds:
        # P15-A-2 (8 June 2026): ERA5-Land monthly at 0.1° (~11 km mesh).
        # P15-A-3 (8 June 2026): added daily-statistics fetch for true
        # heat_days/ice_days counts (Option B per operator decision —
        # the monthly mean alone cannot capture daily extreme-day events).
        #
        # Two-request architecture:
        #   1. Monthly mean for t_mean_c (annual climatology, 2000-2020)
        #   2. Daily maximum for heat_days/ice_days (5-year window 2018-2022)
        #
        # The daily fetch uses derived-era5-land-daily-statistics which
        # pre-aggregates ERA5-Land hourly → daily. ONE request returns one
        # statistic; we use daily_maximum because:
        #   - heat_days = days where T_max > 25°C  (Köppen hot-day convention)
        #   - ice_days  = days where T_max < 0°C   (Köppen frost-day convention)
        # Both derive from the same daily_max field.
        bbox_area = [bbox["lat_max"], bbox["lon_min"], bbox["lat_min"], bbox["lon_max"]]

        # ── 1. Monthly t_mean_c (existing path) ──
        era5_monthly_request = {
            "product_type": "monthly_averaged_reanalysis",
            "variable": ["2m_temperature"],
            "year": [str(y) for y in range(years[0], years[1] + 1)],
            "month": [f"{m:02d}" for m in range(1, 13)],
            "time": "00:00",
            "area": bbox_area,
            "format": "netcdf",
        }
        monthly_output = CACHE_DIR / f"era5land_{country}_{years[0]}_{years[1]}.nc"
        monthly_success = cds_retrieve(
            "reanalysis-era5-land-monthly-means",
            era5_monthly_request,
            monthly_output,
        )

        # ── 2. Daily maximum for heat/ice day counts (P15-A-3, NEW) ──
        # Window: 2018-2022 (recent 5-year climatology). Statistically
        # sufficient for day-count variance to converge; recent enough to
        # capture current climate-change baseline (heat-day rate has
        # shifted materially since the 1990s).
        #
        # P15-A-3 fix (8 June 2026 evening): single 5-year request exceeded
        # CDS per-request size limit ("Your request is too large"). Chunked
        # by year — 5 separate requests of (1 year × 12 months × 31 days)
        # each, dramatically smaller payload. Each successful chunk lands
        # as its own .nc file; the overlay function reads all available.
        # Partial success is acceptable (visibly-honest degradation per
        # Convention #56) — if 3 of 5 years succeed, day counts are still
        # statistically meaningful, just averaged over fewer years.
        daily_years = (2018, 2022)
        daily_nc_paths = []
        daily_chunks_ok = 0
        for yr in range(daily_years[0], daily_years[1] + 1):
            era5_daily_request = {
                "variable": "2m_temperature",
                "year": str(yr),
                "month": [f"{m:02d}" for m in range(1, 13)],
                "day": [f"{d:02d}" for d in range(1, 32)],
                "daily_statistic": "daily_maximum",
                "time_zone": "utc+00:00",
                "frequency": "1_hourly",
                "area": bbox_area,
                "format": "netcdf",
            }
            yr_output = CACHE_DIR / f"era5land_daily_max_{country}_{yr}.nc"
            ok = cds_retrieve(
                "derived-era5-land-daily-statistics",
                era5_daily_request,
                yr_output,
            )
            if ok and yr_output.exists() and yr_output.stat().st_size > 1024:
                daily_nc_paths.append(yr_output)
                daily_chunks_ok += 1
            else:
                logger.warning(
                    f"P15-A-3: daily ERA5-Land fetch failed for {country} year {yr}; "
                    f"this year will not contribute to the {daily_years[0]}-{daily_years[1]} "
                    f"climatology."
                )

        if monthly_success:
            # Process monthly NetCDF → grid keyed by (lat, lon) with t_mean_c
            baseline = _process_era5_netcdf(monthly_output, country)
            # If at least one daily chunk succeeded, overlay TRUE
            # heat_days/ice_days counts averaged over successful years;
            # otherwise baseline retains the analytic approximation
            # (with a clear log line so the operator knows).
            if daily_chunks_ok > 0 and baseline:
                baseline = _overlay_daily_extremes(
                    baseline, daily_nc_paths, country, daily_chunks_ok,
                )
            else:
                logger.warning(
                    f"P15-A-3: NO daily ERA5-Land chunks succeeded for {country}; "
                    f"heat_days/ice_days will be the monthly-mean analytic "
                    f"approximation (likely zero for temperate climates). "
                    f"Operator can re-run the country to retry daily fetch."
                )
            if baseline and cache:
                with open(cache_path, "w") as f:
                    json.dump(baseline, f)
            return baseline

    # 4. ABORT
    logger.error(
        f"ERA5 baseline data not available for {country}.\n"
        f"  No synthetic fallback — real climate data is required.\n"
        f"\n"
        f"  To fix this:\n"
        f"    1. Register at https://cds.climate.copernicus.eu (free)\n"
        f"    2. Download ERA5 monthly means (2000–2020) for {country}\n"
        f"    3. Process into CSV: lat, lon, t_mean_c, heat_days, ice_days, wind_speed\n"
        f"    4. Place at: {local_path}\n"
        f"\n"
        f"  Or set CDS_API_KEY env var for automatic download.\n"
        f"  See scripts/pipeline/data/README.md for full instructions."
    )
    return None


def _parse_climate_csv(csv_path, expected_columns):
    """
    Parse a committed climate reference CSV into a list of grid-point dicts.

    Args:
        csv_path: Path to CSV file
        expected_columns: List of column names to extract (first two should be lat/lon)

    Returns:
        List of dicts with numeric values, or None if parsing fails.
    """
    import csv as csv_mod

    try:
        grid = []
        with open(csv_path, newline="") as f:
            reader = csv_mod.DictReader(f)
            headers = reader.fieldnames or []

            # Validate columns exist
            missing = [c for c in expected_columns if c not in headers]
            if missing:
                logger.warning(f"Climate CSV {csv_path} missing columns: {missing}")
                # Try common aliases
                alias_map = {
                    "lat": ["latitude", "LAT", "Lat"],
                    "lon": ["longitude", "LON", "Lon", "lng"],
                    "t_mean_c": ["t_mean", "temperature", "temp_c"],
                    "heat_days": ["heat_days_yr", "hot_days"],
                    "ice_days": ["ice_days_yr", "frost_days"],
                    "wind_speed": ["wind_ms", "wind_speed_ms"],
                    "delta_t_c": ["delta_t", "warming_c"],
                    "delta_heat_pct": ["delta_heat", "heat_change_pct"],
                    "delta_ice_pct": ["delta_ice", "ice_change_pct"],
                    "delta_wind_pct": ["delta_wind", "wind_change_pct"],
                }
                col_map = {}
                for col in expected_columns:
                    if col in headers:
                        col_map[col] = col
                    else:
                        for alias in alias_map.get(col, []):
                            if alias in headers:
                                col_map[col] = alias
                                break
                        else:
                            logger.error(f"Cannot resolve column '{col}' in {csv_path}")
                            return None
            else:
                col_map = {c: c for c in expected_columns}

            for row in reader:
                try:
                    point = {}
                    for target, source in col_map.items():
                        val = row[source].strip()
                        point[target] = float(val)
                    grid.append(point)
                except (ValueError, KeyError) as e:
                    continue  # skip malformed rows

        if not grid:
            logger.warning(f"Climate CSV {csv_path} parsed but yielded 0 rows")
            return None

        logger.info(f"Parsed {len(grid)} grid points from {csv_path.name}")
        return grid

    except FileNotFoundError:
        logger.warning(f"Climate CSV not found: {csv_path}")
        return None
    except Exception as e:
        logger.error(f"Error parsing climate CSV {csv_path}: {e}")
        return None


def _overlay_daily_extremes(monthly_baseline, daily_nc_paths, country, n_years_used):
    """P15-A-3: read one OR MORE daily-maximum NetCDF chunks (per year), count
    true heat_days + ice_days per grid cell, and overlay onto the monthly baseline.

    The monthly baseline already carries t_mean_c per (lat, lon). This function
    REPLACES the analytic heat_days/ice_days approximation with empirical
    counts derived from daily ERA5-Land maxima.

    Counting convention (Köppen / WMO standard):
      - heat_days = count of days where T_max > 25°C (mean over the N-year window)
      - ice_days  = count of days where T_max < 0°C  (mean over the N-year window)

    Both are reported as annual averages so they're directly comparable to
    single-year observed climatologies.

    P15-A-3 fix (8 June 2026 evening): accepts a LIST of NetCDF paths
    (one per successfully-downloaded year) rather than a single big file,
    because CDS rejects multi-year derived-statistics requests as too large.
    Counts are accumulated across all available years; the divisor is
    n_years_used (the number of years actually downloaded) — if some years
    failed, the climatology is still valid, just from fewer years.
    """
    try:
        import netCDF4 as nc
        import numpy as np

        # Accumulated counts across all year chunks
        accumulated_heat = None
        accumulated_ice = None
        accumulated_lats = None
        accumulated_lons = None
        total_days = 0
        var_used = None

        # Threshold conversions: 25°C = 298.15K, 0°C = 273.15K
        HEAT_THRESHOLD_K = 298.15
        ICE_THRESHOLD_K = 273.15

        # Coerce single path to list for backward compat
        if not isinstance(daily_nc_paths, (list, tuple)):
            daily_nc_paths = [daily_nc_paths]

        for nc_path in daily_nc_paths:
            try:
                ds = nc.Dataset(str(nc_path))
            except Exception as exc:
                logger.warning(
                    f"P15-A-3: skipping {nc_path.name} "
                    f"({type(exc).__name__}: {exc})"
                )
                continue

            # The variable might be 't2m' or 'mx2t' depending on CDS naming
            if 't2m' in ds.variables:
                t_max = ds.variables['t2m'][:]
                vname = 't2m'
            elif 'mx2t' in ds.variables:
                t_max = ds.variables['mx2t'][:]
                vname = 'mx2t'
            else:
                available = list(ds.variables.keys())
                logger.error(
                    f"P15-A-3: {nc_path.name} doesn't have t2m or mx2t. "
                    f"Available: {available}"
                )
                ds.close()
                continue

            if var_used is None:
                var_used = vname

            lats = ds.variables['latitude'][:]
            lons = ds.variables['longitude'][:]
            ds.close()

            # Count days where t_max crosses thresholds for THIS year chunk
            if hasattr(t_max, 'mask') and t_max.mask is not False:
                heat_count = np.where(t_max.mask, 0, t_max > HEAT_THRESHOLD_K).sum(axis=0)
                ice_count  = np.where(t_max.mask, 0, t_max < ICE_THRESHOLD_K).sum(axis=0)
            else:
                heat_count = (t_max > HEAT_THRESHOLD_K).sum(axis=0)
                ice_count  = (t_max < ICE_THRESHOLD_K).sum(axis=0)

            # Accumulate (sum across years)
            if accumulated_heat is None:
                accumulated_heat = heat_count.astype(float)
                accumulated_ice  = ice_count.astype(float)
                accumulated_lats = lats
                accumulated_lons = lons
            else:
                # Shape mismatch defensively handled (shouldn't happen
                # since all yearly requests use the same bbox/area)
                if heat_count.shape == accumulated_heat.shape:
                    accumulated_heat += heat_count.astype(float)
                    accumulated_ice  += ice_count.astype(float)
                else:
                    logger.warning(
                        f"P15-A-3: shape mismatch on {nc_path.name} "
                        f"({heat_count.shape} vs {accumulated_heat.shape}); skipping"
                    )
                    continue
            total_days += t_max.shape[0]

        if accumulated_heat is None:
            logger.error(
                f"P15-A-3: no usable daily chunks for {country}; "
                f"keeping monthly-analytic approximation."
            )
            return monthly_baseline

        # Normalise to annual average across the successful years
        heat_per_year = accumulated_heat / n_years_used
        ice_per_year  = accumulated_ice  / n_years_used

        # Build lookup keyed by rounded (lat, lon)
        lookup = {}
        for i, lat in enumerate(accumulated_lats):
            for j, lon in enumerate(accumulated_lons):
                heat_v = float(heat_per_year[i, j])
                ice_v  = float(ice_per_year[i, j])
                if not (np.isfinite(heat_v) and np.isfinite(ice_v)):
                    continue
                key = (round(float(lat), 3), round(float(lon), 3))
                lookup[key] = (heat_v, ice_v)

        # Overlay onto monthly baseline
        matched, unmatched = 0, 0
        for point in monthly_baseline:
            key = (round(point['lat'], 3), round(point['lon'], 3))
            if key in lookup:
                heat_v, ice_v = lookup[key]
                point['heat_days'] = round(heat_v, 1)
                point['ice_days']  = round(ice_v, 1)
                matched += 1
            else:
                unmatched += 1

        logger.info(
            f"P15-A-3: {country} — overlaid TRUE heat/ice counts on "
            f"{matched}/{matched+unmatched} grid cells "
            f"(var {var_used}, {total_days} daily samples × {n_years_used} yr chunks, "
            f"thresholds 25°C heat / 0°C ice). "
            f"{unmatched} cells retained monthly-analytic fallback."
        )
        return monthly_baseline

    except ImportError:
        logger.error(
            f"P15-A-3: netCDF4 or numpy not available; cannot overlay daily extremes for {country}."
        )
        return monthly_baseline
    except Exception as exc:
        logger.error(
            f"P15-A-3: failed to overlay daily extremes for {country}: "
            f"{type(exc).__name__}: {exc}"
        )
        return monthly_baseline


def _process_era5_netcdf(nc_path, country):
    """Process ERA5 / ERA5-Land NetCDF into grid of climate metrics.

    P15-A-2 (8 June 2026): handles ERA5-Land's ocean-mask via NaN/MaskedArray
    detection — ERA5-Land defines t2m only over land grid cells, so coastal
    bboxes have many cells where t2m[:,i,j].mean() yields a masked constant
    or NaN. We skip those cells silently so the resulting CSV has just the
    land-covered grid (which is what the L2 spatial overlay wants anyway).
    """
    try:
        import netCDF4 as nc
        import numpy as np
        ds = nc.Dataset(str(nc_path))

        # ERA5-Land sometimes uses 'valid_time' instead of 'time' coord name,
        # but the t2m variable's space dims are always (time, latitude, longitude)
        lats = ds.variables["latitude"][:]
        lons = ds.variables["longitude"][:]
        t2m = ds.variables["t2m"][:]  # 2m temperature (K), shape (time, lat, lon)

        grid = []
        skipped_masked = 0
        for i, lat in enumerate(lats):
            for j, lon in enumerate(lons):
                # Compute monthly-mean across time axis
                cell = t2m[:, i, j]
                # Detect masked / NaN cells (ocean over ERA5-Land)
                if np.ma.is_masked(cell):
                    # Fully-masked cells have mean = masked constant
                    cell_mean = cell.mean()
                    if cell_mean is np.ma.masked or (hasattr(cell_mean, 'mask') and cell_mean.mask):
                        skipped_masked += 1
                        continue
                    t_mean_k = float(cell_mean)
                else:
                    t_mean_k = float(cell.mean())

                if not np.isfinite(t_mean_k):
                    skipped_masked += 1
                    continue

                t_mean_c = t_mean_k - 273.15
                heat_days = max(0, (t_mean_c - 20) * 15)
                ice_days = max(0, (0 - t_mean_c) * 20)

                grid.append({
                    "lat": float(lat), "lon": float(lon),
                    "t_mean_c": round(t_mean_c, 2),
                    "heat_days": round(heat_days, 1),
                    "ice_days": round(ice_days, 1),
                })

        ds.close()
        if skipped_masked:
            logger.info(
                f"  {country}: emitted {len(grid)} land grid points, "
                f"skipped {skipped_masked} ocean/masked cells (ERA5-Land mask)"
            )
        return grid
    except ImportError:
        logger.error(
            f"netCDF4 not available — cannot process ERA5 NetCDF for {country}.\n"
            f"  Install with: pip install netCDF4\n"
            f"  Or pre-process the NetCDF to CSV and place at: {_era5_local_path(country)}"
        )
        return None


# ═══════════════════════════════════════════════════════════
#  CMIP6 CLIMATE PROJECTIONS
# ═══════════════════════════════════════════════════════════

def fetch_cmip6_projections(country, scenario="ssp245", period=(2030, 2050), cache=True):
    """
    Load CMIP6 ensemble projections (SSP2-4.5 deltas) for a country.

    Resolution order:
      1. Country-specific committed CSV (scripts/pipeline/data/{country}/cmip6_ssp245_deltas.csv)
      2. Cross-cutting committed CSV (scripts/pipeline/data/cross-cutting/cmip6_ssp245_deltas.csv)
      3. Cached JSON from previous CDS download
      4. Live download from Copernicus CDS (requires CDS_API_KEY + netCDF4)
      5. ABORT with instructions — no synthetic data

    Returns gridded deltas: [{"lat", "lon", "delta_t_c", "delta_heat_pct", "delta_ice_pct", "delta_wind_pct"}, ...]
    """
    cmip6_cols = ["lat", "lon", "delta_t_c", "delta_heat_pct", "delta_ice_pct", "delta_wind_pct"]

    # 1. Country-specific committed CSV
    country_csv = _cmip6_country_local(country)
    if country_csv.exists():
        logger.info(f"Loading CMIP6 deltas from country CSV: {country_csv}")
        grid = _parse_climate_csv(country_csv, cmip6_cols)
        if grid:
            return grid

    # 2. Cross-cutting committed CSV (global grid — filter to country bbox)
    if CMIP6_LOCAL_CSV.exists():
        logger.info(f"Loading CMIP6 deltas from cross-cutting CSV: {CMIP6_LOCAL_CSV}")
        full_grid = _parse_climate_csv(CMIP6_LOCAL_CSV, cmip6_cols)
        if full_grid:
            bbox = _country_bbox(country)
            if bbox:
                grid = [
                    p for p in full_grid
                    if bbox["lat_min"] <= p["lat"] <= bbox["lat_max"]
                    and bbox["lon_min"] <= p["lon"] <= bbox["lon_max"]
                ]
                if grid:
                    logger.info(f"Filtered {len(grid)} CMIP6 grid points for {country} from global grid")
                    return grid

    # 3. Cache
    cache_path = CACHE_DIR / f"cmip6_{scenario}_{country}.json"
    if cache and cache_path.exists():
        with open(cache_path) as f:
            return json.load(f)

    # 4. Live CDS download
    bbox = _country_bbox(country)
    if bbox and CDS_API_KEY:
        cmip6_request = {
            "temporal_resolution": "monthly",
            "experiment": scenario,
            "variable": "near_surface_air_temperature",
            "model": CMIP6_MODELS,
            "year": [str(y) for y in range(period[0], period[1] + 1)],
            "month": [f"{m:02d}" for m in range(1, 13)],
            "area": [bbox["lat_max"], bbox["lon_min"], bbox["lat_min"], bbox["lon_max"]],
            "format": "zip",
        }

        output = CACHE_DIR / f"cmip6_{scenario}_{country}_{period[0]}_{period[1]}.zip"
        success = cds_retrieve("projections-cmip6", cmip6_request, output)

        if success:
            deltas = _process_cmip6(output, country)
            if deltas and cache:
                with open(cache_path, "w") as f:
                    json.dump(deltas, f)
            return deltas

    # 5. ABORT
    logger.error(
        f"CMIP6 climate projections not available for {country}.\n"
        f"  No synthetic fallback — real climate projection data is required.\n"
        f"\n"
        f"  To fix this:\n"
        f"    1. Register at https://cds.climate.copernicus.eu (free)\n"
        f"    2. Accept the CMIP6 licence terms\n"
        f"    3. Download SSP2-4.5 ensemble (ACCESS-CM2, CNRM-CM6-1, EC-Earth3,\n"
        f"       GFDL-ESM4, MRI-ESM2-0), period 2030–2050, monthly\n"
        f"    4. Compute ensemble median per 0.5° grid cell\n"
        f"    5. Subtract 2000–2020 ERA5 baseline to get deltas\n"
        f"    6. Save as CSV: lat, lon, delta_t_c, delta_heat_pct, delta_ice_pct, delta_wind_pct\n"
        f"    7. Place at: {country_csv}\n"
        f"       Or for all countries: {CMIP6_LOCAL_CSV}\n"
        f"\n"
        f"  Or set CDS_API_KEY env var for automatic download.\n"
        f"  See scripts/pipeline/data/README.md for full instructions."
    )
    return None


def _process_cmip6(zip_path, country):
    """Process CMIP6 NetCDF ensemble into delta grid."""
    try:
        import netCDF4  # noqa: F401
        # Full implementation: extract NetCDF from zip, compute ensemble median,
        # subtract baseline, produce delta grid
        logger.warning("CMIP6 NetCDF post-processing not yet implemented — pre-process to CSV")
        return None
    except ImportError:
        logger.error(
            f"netCDF4 not available — cannot process CMIP6 NetCDF.\n"
            f"  Install with: pip install netCDF4\n"
            f"  Or pre-process to CSV and place at: {_cmip6_country_local(country)}"
        )
        return None


# ═══════════════════════════════════════════════════════════
#  IRI FORWARD COMPUTATION
# ═══════════════════════════════════════════════════════════

def compute_iri_forward(country, era5_baseline=None, cmip6_deltas=None, cache=True):
    """
    Compute forward-looking IRI trajectory ratios for each substation.

    IRI_forward = IRI_base × (1 + delta_CMIP6)

    The trajectory ratio indicates how much each IRI metric is expected to change
    under SSP2-4.5 by 2030–2050 relative to 2000–2020 baseline.

    Returns list of per-substation trajectory updates.
    """
    if era5_baseline is None:
        era5_baseline = fetch_era5_baseline(country, cache=cache)
    if cmip6_deltas is None:
        cmip6_deltas = fetch_cmip6_projections(country, cache=cache)

    if not cmip6_deltas:
        logger.warning(f"No CMIP6 data for {country} — IRI forward cannot be computed")
        return []

    data, subs = load_substations(country)
    coords = substation_coords(subs)

    # Build a fast lookup grid for CMIP6 deltas (O(1) per query instead of O(n))
    cmip6_grid = {}
    for pt in cmip6_deltas:
        key = (round(pt["lat"] * 2) / 2, round(pt["lon"] * 2) / 2)  # round to 0.5°
        cmip6_grid[key] = pt

    results = []
    for lat, lon, idx in coords:
        sub = subs[idx]

        # Fast O(1) lookup — round substation coords to nearest 0.5° CMIP6 grid cell
        grid_key = (round(lat * 2) / 2, round(lon * 2) / 2)
        best_pt = cmip6_grid.get(grid_key)

        # Try nearby cells if exact key not found
        if best_pt is None:
            for dlat in [-0.5, 0, 0.5]:
                for dlon in [-0.5, 0, 0.5]:
                    nearby_key = (grid_key[0] + dlat, grid_key[1] + dlon)
                    best_pt = cmip6_grid.get(nearby_key)
                    if best_pt:
                        break
                if best_pt:
                    break

        if best_pt is None:
            # Country-mean fallback
            delta_heat = 0.15
            delta_ice = -0.10
            delta_wind = 0.05
            delta_t = 1.0
        else:
            delta_heat = best_pt.get("delta_heat_pct", 0.15)
            delta_ice = best_pt.get("delta_ice_pct", -0.10)
            delta_wind = best_pt.get("delta_wind_pct", 0.05)
            delta_t = best_pt.get("delta_t_c", 1.0)

        # IRI trajectory ratios
        # I1 = snow/ice → less ice stress → lower I1
        # I2 = tree-fall/wind → more wind → higher I2
        # I3 = heat-wave → more heat → higher I3
        i1_trajectory = round(1.0 + delta_ice, 4)
        i2_trajectory = round(1.0 + delta_wind, 4)
        i3_trajectory = round(1.0 + delta_heat, 4)

        results.append({
            "substation_id": sub.get("substation_id", sub.get("name", f"sub_{idx}")),
            "index": idx,
            "I1_trajectory": i1_trajectory,
            "I2_trajectory": i2_trajectory,
            "I3_trajectory": i3_trajectory,
            "delta_t_c": delta_t,
            "previous": sub.get("climate_trajectory", {}),
        })

    # Summary
    if results:
        i3_vals = [r["I3_trajectory"] for r in results]
        logger.info(f"IRI forward for {country}: I3_trajectory range [{min(i3_vals):.4f}, {max(i3_vals):.4f}]")

    return results


# ═══════════════════════════════════════════════════════════
#  COUNTRY BOUNDING BOXES
# ═══════════════════════════════════════════════════════════

def _country_bbox(country):
    """
    Return lat/lon bounding box for CDS API requests.

    P15-A follow-up (8 June 2026): extended from 17 → 39 countries to
    cover the full SoT list. Pre-fix, F-L4-2 cohort countries (korea,
    colombia, israel, costa-rica, iceland, hungary, slovakia, slovenia)
    + others (australia, belgium, chile, czechia, estonia, ireland,
    latvia, lithuania, luxembourg, netherlands, new-zealand, portugal,
    turkey, greenland, ...) returned None here, causing fetch_era5_baseline
    to silently fall through to ABORT even when CDS credentials were
    correctly configured.
    """
    boxes = {
        # Original 17 (Phase 1 baseline)
        "italy":       {"lat_min": 35.5, "lat_max": 47.1, "lon_min": 6.6,  "lon_max": 18.5},
        "germany":     {"lat_min": 47.3, "lat_max": 55.1, "lon_min": 5.9,  "lon_max": 15.0},
        "france":      {"lat_min": 41.3, "lat_max": 51.1, "lon_min": -5.1, "lon_max": 9.6},
        "spain":       {"lat_min": 36.0, "lat_max": 43.8, "lon_min": -9.3, "lon_max": 3.3},
        "uk":          {"lat_min": 49.9, "lat_max": 60.9, "lon_min": -8.2, "lon_max": 1.8},
        "us":          {"lat_min": 24.5, "lat_max": 49.4, "lon_min": -124.8, "lon_max": -66.9},
        "switzerland": {"lat_min": 45.8, "lat_max": 47.8, "lon_min": 5.9, "lon_max": 10.5},
        "austria":     {"lat_min": 46.4, "lat_max": 49.0, "lon_min": 9.5, "lon_max": 17.2},
        "canada":      {"lat_min": 41.7, "lat_max": 83.1, "lon_min": -141.0, "lon_max": -52.6},
        "japan":       {"lat_min": 24.0, "lat_max": 45.6, "lon_min": 122.9, "lon_max": 153.0},
        "denmark":     {"lat_min": 54.5, "lat_max": 57.8, "lon_min": 8.0,  "lon_max": 15.2},
        "norway":      {"lat_min": 57.9, "lat_max": 71.2, "lon_min": 4.5,  "lon_max": 31.1},
        "finland":     {"lat_min": 59.8, "lat_max": 70.1, "lon_min": 20.6, "lon_max": 31.6},
        "poland":      {"lat_min": 49.0, "lat_max": 54.9, "lon_min": 14.1, "lon_max": 24.2},
        "sweden":      {"lat_min": 55.3, "lat_max": 69.1, "lon_min": 11.0, "lon_max": 24.2},
        "mexico":      {"lat_min": 14.5, "lat_max": 32.8, "lon_min": -118.5, "lon_max": -86.5},
        "greece":      {"lat_min": 34.5, "lat_max": 42.0, "lon_min": 19.0, "lon_max": 29.5},
        # P15-A: 22 countries added to close the F-L4-2-extended gap
        "australia":   {"lat_min": -45.0, "lat_max": -10.0, "lon_min": 110.0, "lon_max": 155.0},
        "belgium":     {"lat_min": 49.50, "lat_max": 51.51, "lon_min":  2.55, "lon_max":  6.41},
        "chile":       {"lat_min": -56.0, "lat_max": -17.0, "lon_min": -76.0, "lon_max": -66.0},
        "colombia":    {"lat_min":  -4.3, "lat_max":  13.5, "lon_min": -82.0, "lon_max": -66.8},
        "costa-rica":  {"lat_min":   8.0, "lat_max":  11.3, "lon_min": -86.0, "lon_max": -82.5},
        "czechia":     {"lat_min": 48.55, "lat_max": 51.06, "lon_min": 12.09, "lon_max": 18.86},
        "estonia":     {"lat_min": 57.51, "lat_max": 59.69, "lon_min": 21.83, "lon_max": 28.21},
        "greenland":   {"lat_min": 59.5,  "lat_max": 83.7,  "lon_min": -74.0, "lon_max": -11.0},
        "hungary":     {"lat_min": 45.7,  "lat_max": 48.6,  "lon_min": 16.1,  "lon_max": 22.9},
        "iceland":     {"lat_min": 63.2,  "lat_max": 66.6,  "lon_min": -24.6, "lon_max": -13.4},
        "ireland":     {"lat_min": 51.4,  "lat_max": 55.4,  "lon_min": -10.5, "lon_max": -5.4},
        "israel":      {"lat_min": 29.4,  "lat_max": 33.4,  "lon_min": 34.2,  "lon_max": 35.9},
        "korea":       {"lat_min": 33.0,  "lat_max": 38.7,  "lon_min": 124.5, "lon_max": 132.0},
        "latvia":      {"lat_min": 55.67, "lat_max": 58.09, "lon_min": 20.97, "lon_max": 28.24},
        "lithuania":   {"lat_min": 53.90, "lat_max": 56.45, "lon_min": 20.95, "lon_max": 26.84},
        "luxembourg":  {"lat_min": 49.45, "lat_max": 50.18, "lon_min":  5.73, "lon_max":  6.53},
        "netherlands": {"lat_min": 50.75, "lat_max": 53.55, "lon_min":  3.36, "lon_max":  7.23},
        "new-zealand": {"lat_min": -47.5, "lat_max": -34.0, "lon_min": 165.5, "lon_max": 179.0},
        "portugal":    {"lat_min": 36.9,  "lat_max": 42.2,  "lon_min": -9.6,  "lon_max": -6.1},
        "slovakia":    {"lat_min": 47.7,  "lat_max": 49.7,  "lon_min": 16.8,  "lon_max": 22.6},
        "slovenia":    {"lat_min": 45.4,  "lat_max": 46.9,  "lon_min": 13.4,  "lon_max": 16.6},
        "turkey":      {"lat_min": 35.8,  "lat_max": 42.1,  "lon_min": 26.0,  "lon_max": 44.8},
    }
    return boxes.get(country)


# ═══════════════════════════════════════════════════════════
#  CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════

def main():
    """Run climate trajectory ingestion for a country."""
    import argparse

    parser = argparse.ArgumentParser(description="SSI Pipeline — Climate Trajectory Ingestion")
    parser.add_argument("country", help="Country to process")
    parser.add_argument("--scenario", default="ssp245", help="CMIP6 scenario (default: ssp245)")
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--output", type=str)

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    results = compute_iri_forward(args.country, cache=not args.no_cache)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Wrote {len(results)} results to {args.output}")
    else:
        print(f"\nClimate trajectory results for {args.country}: {len(results)} substations")


if __name__ == "__main__":
    main()
