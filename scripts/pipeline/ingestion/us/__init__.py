"""US v4.23 L1 ingestion connector — Wave 4 P39.

🇺🇸 NINTH Wave 4 country + 🏆 FINAL TERMINAL CLOSURE at 39/39 = 100%
cohort-wide. Portugal P33 bi-directional Option B pattern INHERITED at
50-state + 3-Interconnection + 5-territory-globally-distributed scale.

Convention #78 BINDING 21ST ENFORCEMENT — 3-language coverage:
  English (~79%) + Spanish (~13%) + Native American languages
  (representative — 574 federally-recognised tribes + Navajo dominant).
  Lower-cohort ranking (below Portugal/Sweden/Japan 4).

Convention #78 §4bis.5 Layer 3 — NOT REQUIRED for US (5th cohort-wide):
  HORIZONTAL FRAGMENTATION extends Germany P38 pattern at 3.5× utility
  scale (~3,200+ utilities: 180 IOUs + 2,000 munis + 900 coops + 5
  federal PMAs + 30+ tribal + 5 territorial). State-franchise
  territorial boundaries cleanly delineate all major metropolitan
  areas — no dual-DSO overlaps within any municipality.

Architecture: Portugal P33 bi-directional pattern.
  - Lines: minor_line → 12.47 kV MV standard; cable → 12.47 kV;
    line → 69 kV US subT (UNIQUE cohort-wide — France 63, Portugal 60,
    Spain/Japan 66, Italy 132, Germany 110)
  - Subs: substation=transmission → 345 kV EHV US standard (distinct
    from EU 380 kV, Japan 275 kV, France 225 kV UNIQUE);
    substation=distribution → 12.47 kV MV standard (much lower than
    EU 20 kV, higher than Japan 6.6 kV); substation=minor →
    4.16 kV legacy US MV; substation=traction → 0.75 kV DC third rail
    (NYC MTA + BART + WMATA + MBTA + CTA + PATH); power=substation →
    12.47 kV MV default

Discipline #36: 6.0 km tolerance (matches France + Portugal + Japan + UK
  — US 4-continent territorial reach: mainland + Caribbean + Pacific +
  Alaska Arctic + Hawaii).

Discipline #41: baseline TBD. US OSM historically less MV-complete than
  Central European (France/Germany) — may NOT exhibit over-recovery
  signature; possible moderate HEALTHY_BAND landing instead.

Layer 4 baselines: R6d_wildfire 0.80 (2nd cohort-wide after Portugal
  0.90 — Camp Fire + Maui) + R9_compound 0.75 (HIGHEST alongside
  Japan — Katrina archetypal cascade + Uri triple-cascade) +
  R6e_winter 0.75 (2nd cohort-wide — Texas Uri + polar vortex).

🏆 UNIQUE 3-INTERCONNECTION architecture (Eastern + Western + ERCOT
  Texas triple-frequency-island system).
"""

from ._base import (
    ALIAS_MAP,
    US_MASTER_BBOX,
    NORTHEAST_BBOX,
    SOUTHEAST_BBOX,
    GREAT_LAKES_BBOX,
    PLAINS_BBOX,
    TEXAS_BBOX,
    SOUTHWEST_BBOX,
    MOUNTAIN_BBOX,
    CALIFORNIA_BBOX,
    PACIFIC_NW_BBOX,
    ALASKA_BBOX,
    HAWAII_BBOX,
    PUERTO_RICO_USVI_BBOX,
    GUAM_MARIANA_BBOX,
    AMERICAN_SAMOA_BBOX,
    RESOLVER_LAYERS,
    resolve_operator,
)

__all__ = [
    "ALIAS_MAP",
    "US_MASTER_BBOX",
    "NORTHEAST_BBOX",
    "SOUTHEAST_BBOX",
    "GREAT_LAKES_BBOX",
    "PLAINS_BBOX",
    "TEXAS_BBOX",
    "SOUTHWEST_BBOX",
    "MOUNTAIN_BBOX",
    "CALIFORNIA_BBOX",
    "PACIFIC_NW_BBOX",
    "ALASKA_BBOX",
    "HAWAII_BBOX",
    "PUERTO_RICO_USVI_BBOX",
    "GUAM_MARIANA_BBOX",
    "AMERICAN_SAMOA_BBOX",
    "RESOLVER_LAYERS",
    "resolve_operator",
]
