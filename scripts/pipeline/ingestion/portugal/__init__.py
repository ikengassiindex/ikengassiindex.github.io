"""Portugal v4.23 L1 ingestion connector — Wave 4 P33.

🇵🇹 THIRD Wave 4 country. Iberian synchronous grid + MIBEL market
coupling with Spain since 2007. Sweden P32 Option B inheritance
(power=minor_line + no-voltage inference).

Architecture: Wave 4 CORRECTED + Sweden P32 Option B pattern.
  - out center query hint on way subs (100% coord capture)
  - out geom query hint on lines (proper polyline coords)
  - power=minor_line INCLUDED per Sweden P32 Nordic MV pattern
  - No-voltage lines accepted with power-class-based inference:
    * minor_line → 20 kV MV rural distribution
    * cable no-voltage → 20 kV MV underground urban
    * line no-voltage → 60 kV Portugal subtransmission (NOT Nordic 130)
  - Compact {s, l, a} grid-geo schema (canonical)
  - Grid-based spatial index (0.1° cells, ~11 km, ~600× speedup)
  - Continental single-bbox + Açores + Madeira additional zones

Convention #78 BINDING 15TH ENFORCEMENT:
  Portuguese (~90%) + English (~7%) + Spanish (~2% cross-border) +
  Mirandese (~<1% Miranda do Douro concelho statutory since 1999).

Convention #78 §4bis.5 Layer 3 — NOT REQUIRED for Portugal:
  Single-DSO architectural simplification. E-REDES (former EDP
  Distribuição) holds ~99% mainland market share. Açores + Madeira
  are ISLANDED grids (EDA + EEM) resolved via bbox layer, not
  metropolitan geofence. No Lisboa/Porto DSO split exists.

Discipline #36: 6.0 km cross-border tolerance (HIGHEST Wave 4):
  Atlantic coastline complexity (900 km continental) + Açores
  mid-Atlantic offshore extension + Madeira archipelago + 5 400 kV
  AC cross-border interconnectors with Spain.

Discipline #41: baseline parity 1.10 BELOW_HEALTHY_BAND;
  post-Sweden-Option-B-inheritance projected 2-4 HEALTHY_BAND.

Layer 4 baseline HIGHLIGHT: R6d_wildfire = 0.90 HIGHEST cohort-wide
  (2017 Pedrógão Grande 66 dead + annual wildfire crisis + Portugal
  has HIGHEST wildfire mortality per capita in OECD 2000-2020).
"""

from ._base import (
    ALIAS_MAP,
    AZORES_BBOX,
    CONTINENTAL_BBOX,
    MADEIRA_BBOX,
    RESOLVER_LAYERS,
    resolve_operator,
)

__all__ = [
    "ALIAS_MAP",
    "AZORES_BBOX",
    "CONTINENTAL_BBOX",
    "MADEIRA_BBOX",
    "RESOLVER_LAYERS",
    "resolve_operator",
]
