"""Resolve the GISCO shapefile directory, in whichever environment we are in.

WHY THIS EXISTS
---------------
`ssi_boundary_source.py` hardcoded

    GIS = ~/mnt/eurostat_gisco_nuts3_2024

which is the path the Cowork device VM mounts a connected folder at. On the
operator's own Mac the same folder is at ~/eurostat_gisco_nuts3_2024, so the
CNTR layer was not found, every non-NUTS country fell back to bounds.json, and
the cross-border gate — correctly — failed closed on a clean country.

The script was verified in one environment and shipped to another. That is the
mechanism of FINDING_the_pipeline_resolves_data_from_its_own_location.md, and
this module is the repair for the GIS case.

ORDER, and it is deliberate
---------------------------
1. $SSI_GIS_DIR            explicit override always wins
2. ~/eurostat_gisco_nuts3_2024        the operator's Mac
3. ~/mnt/eurostat_gisco_nuts3_2024    a Cowork device VM mount
4. <repo>/../eurostat_gisco_nuts3_2024

A directory counts as resolved only if it actually holds the NUTS layer, so a
stale empty folder earlier in the list cannot shadow a good one later.

NEVER SILENT
------------
If nothing resolves, `gis_dir()` raises and the message names every path tried.
A caller that wants to degrade does so explicitly, having been told. §7.5 — no
silent absence.
"""
from __future__ import annotations

import os
import pathlib

NUTS_NAME = "NUTS_RG_01M_2024_4326.shp"
CNTR_NAME = "CNTR_RG_01M_2024_4326.shp"
ITL1_NAME = "ITL1_2021_UK_BGC_4326.geojson"
ITL3_NAME = "ITL3_2025_UK_BGC_4326.geojson"
NE_A1_NAME = "NE_10m_admin1_seven_4326.geojson"

_REPO = pathlib.Path(__file__).resolve().parent.parent


def candidates() -> list[pathlib.Path]:
    out = []
    env = os.environ.get("SSI_GIS_DIR")
    if env:
        out.append(pathlib.Path(env).expanduser())
    out.append(pathlib.Path(os.path.expanduser("~/eurostat_gisco_nuts3_2024")))
    out.append(pathlib.Path(os.path.expanduser("~/mnt/eurostat_gisco_nuts3_2024")))
    out.append(_REPO.parent / "eurostat_gisco_nuts3_2024")
    seen, uniq = set(), []
    for p in out:
        if str(p) not in seen:
            seen.add(str(p))
            uniq.append(p)
    return uniq


def _holds_nuts(d: pathlib.Path) -> bool:
    return (d / NUTS_NAME).exists()


def gis_dir() -> pathlib.Path:
    """The GISCO directory, or a RuntimeError naming every path tried."""
    tried = candidates()
    for d in tried:
        if _holds_nuts(d):
            return d
    raise RuntimeError(
        "GISCO shapefile directory not found. Looked for %s in, in order:\n  %s\n"
        "Set SSI_GIS_DIR to the directory that holds it."
        % (NUTS_NAME, "\n  ".join(str(p) for p in tried))
    )


def nuts_path() -> pathlib.Path:
    return gis_dir() / NUTS_NAME


def cntr_path() -> pathlib.Path | None:
    """The CNTR layer, flat or in its own folder. None when genuinely absent."""
    d = gis_dir()
    for p in (d / CNTR_NAME, d / "CNTR_RG_01M_2024_4326" / CNTR_NAME):
        if p.exists():
            return p
    return None


def ne_admin1_path() -> pathlib.Path | None:
    """Natural Earth 10m admin-1, filtered to the seven non-NUTS jurisdictions.

    Acquired 2026-10-03. GISCO covers NUTS and ONS covers the United Kingdom;
    australia, canada, chile, colombia, mexico, new-zealand and the united
    states are in neither, and OECD publishes their economic accounts without
    publishing boundaries to join them on. Natural Earth's admin-1 layer is one
    file for all of them, carrying `name`, `name_alt` and `iso_3166_2`.

    Filtered to those seven at acquisition - 182 features of the world's
    several thousand - so the layer is 5.2 MB rather than 40.7.

    WHY NOT THE RECORDS' OWN `region` NAMES. Measured: a name join reaches
    82-98 per cent on five of these fleets and 0 per cent on new-zealand, and
    canada carries "Eastern Canada", "Western Canada" or "Northern Canada" on
    1,107 of 7,506 records - macro-groupings no crosswalk can ever place. By
    coordinate all thirteen provinces resolve. E85.
    """
    p = gis_dir() / NE_A1_NAME
    return p if p.exists() else None


def itl3_path() -> pathlib.Path | None:
    """The ONS ITL3 layer for the United Kingdom. None when genuinely absent.

    Acquired 2026-10-03 on the flag officer's direction — "we could make the
    effort to try ITL3" — because ITL1's twelve regions put 4,979 substations
    in each and E2 would barely rank inside the UK at all.

    ONS International Territorial Level 3 (JANUARY 2025) Boundaries UK BGC,
    V2, generalised and clipped, requested already reprojected to EPSG:4326:
    182 polygons carrying ITL325CD and ITL325NM.

    THE VINTAGE IS THE POINT. The January 2021 layer was fetched first — 179
    polygons — and it is the wrong one: ONS publishes GVA at ITL3 on the
    JANUARY 2025 geography, 182 codes, and only 122 of the 179 appear in it.
    57 polygons would have had no GVA and 60 GVA codes no polygon. Measured
    before anything was applied, and the 2021 file is kept beside this one
    rather than deleted so the mismatch stays checkable.

    Against the 2025 layer the match is exact: 182 polygons, 182 GVA codes,
    182 in common, none unmatched on either side.

    The CODE IS STORED AS PUBLISHED — TLC31, never a transformed UKC31 — the
    rule ssi_region_itl1.py set. With ONS's own GVA there is nothing to
    transform: the UK joins on ONS GVA at ONS codes, so it needs neither OECD
    nor the TL->UK substitution, and it carries VALUE ADDED like the Eurostat
    tier rather than GDP. The GVA/GDP seam does not touch the UK.
    """
    p = gis_dir() / ITL3_NAME
    return p if p.exists() else None


def itl1_path() -> pathlib.Path | None:
    """The ONS ITL1 layer for the United Kingdom. None when genuinely absent.

    GISCO's NUTS 2024 layer covers 39 countries and the United Kingdom is not
    among them, so the UK cannot be placed from the NUTS layer at all. This is
    the separate acquisition that replaces it: ONS International Territorial
    Level 1 (January 2021) Boundaries UK BGC, generalised 20m, clipped to Mean
    High Water, requested from the publisher already reprojected to EPSG:4326.

    Returned as None rather than raising, on the CNTR precedent: a caller that
    wants to degrade does so explicitly, having been told.
    """
    p = gis_dir() / ITL1_NAME
    return p if p.exists() else None


if __name__ == "__main__":
    print("candidates, in order:")
    for p in candidates():
        print("   %-64s %s" % (p, "HOLDS NUTS" if _holds_nuts(p) else "-"))
    try:
        d = gis_dir()
    except RuntimeError as e:
        print("\n%s" % e)
        raise SystemExit(1)
    print("\nresolved : %s" % d)
    print("NUTS     : %s" % nuts_path())
    c = cntr_path()
    print("CNTR     : %s" % (c if c else "NOT PRESENT — non-NUTS countries cannot resolve"))
    i = itl1_path()
    print("ITL1 (UK): %s" % (i if i else "NOT PRESENT — the United Kingdom cannot resolve"))
    raise SystemExit(0 if c else 1)
