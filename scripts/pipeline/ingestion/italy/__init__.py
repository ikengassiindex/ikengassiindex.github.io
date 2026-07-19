"""Italy v4.23 L1 ingestion connector — Wave 4 P34.

🇮🇹 FOURTH Wave 4 country. Post-2021 Terna 7-zone bidding
architecture. Portugal P33 bi-directional Option B pattern
INHERITED end-to-end (both lines AND subs).

Convention #78 BINDING 16TH ENFORCEMENT — HIGHEST cohort-wide
8-language alias map:
  Italian (~92%) + English (~5%) + German South Tyrol/Alto Adige
  (~2%) + French Aosta Valley (~0.5%) + Slovenian Trieste/Gorizia
  (~0.3%) + Ladin Dolomites (~<0.1%) + Friulian (~<0.1%) +
  Sardinian (~<0.1%).

Convention #78 §4bis.5 Layer 3 DUAL ENFORCEMENT:
  11TH: Milan 2-way A2A/Unareti + E-Distribuzione
  12TH: Rome 2-way ACEA + E-Distribuzione

Architecture: Wave 4 CORRECTED + Portugal P33 bi-directional pattern.
  - out center + out geom query hints
  - power=minor_line INCLUDED (Sweden P32 lines-side)
  - No-voltage lines + subs accepted with power-class inference
    (Portugal P33 bi-directional):
    * Lines: minor_line/cable → 20 kV MV; line → 132 kV Italian subT
    * Subs: substation=transmission → 220 kV Terna; substation=
      distribution → 20 kV E-Distribuzione MV (Italian standard);
      substation=minor_distribution → 15 kV rural MV; substation=
      traction → 25 kV RFI rail; power=substation generic → 20 kV
  - 7-zone bbox-split aligned with Terna post-2021 bidding zones
  - Compact {s, l, a} grid-geo schema + Convention #80 sharding

Discipline #36: 5.0 km cross-border tolerance (Mediterranean coastline
  + Alpine ridge complexity + island archipelago precision).

Discipline #41: baseline parity 3.31 HEALTHY_BAND; post-Option-B-
  bi-directional projected 3-4 HEALTHY_BAND (proportional growth).

Layer 4 baselines: R6d_wildfire 0.65 MOD-HIGH + R9_compound 0.60
  MOD-HIGH (6th most seismic OECD + Etna/Vesuvio/Stromboli active
  volcanism) + R8_adapt 0.60 (PNIEC + PNRR €200bn EU recovery fund).
"""

from ._base import (
    ALIAS_MAP,
    ITALY_BBOX,
    MILAN_A2A_UNARETI_BBOX,
    MILAN_E_DISTRIBUZIONE_BBOX,
    RESOLVER_LAYERS,
    ROME_ACEA_BBOX,
    ROME_E_DISTRIBUZIONE_BBOX,
    resolve_operator,
)

__all__ = [
    "ALIAS_MAP",
    "ITALY_BBOX",
    "MILAN_A2A_UNARETI_BBOX",
    "MILAN_E_DISTRIBUZIONE_BBOX",
    "RESOLVER_LAYERS",
    "ROME_ACEA_BBOX",
    "ROME_E_DISTRIBUZIONE_BBOX",
    "resolve_operator",
]
