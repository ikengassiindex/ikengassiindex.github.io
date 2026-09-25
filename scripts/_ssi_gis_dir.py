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
    raise SystemExit(0 if c else 1)
