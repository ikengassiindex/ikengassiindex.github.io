"""Spain v4.23 L1 ingestion connector — Wave 4 P36.

🇪🇸 SIXTH Wave 4 country. IBERIAN CLUSTER COMPLETION 2-of-2
milestone (Portugal P33 + Spain P36). Portugal P33 bi-directional
Option B pattern INHERITED as direct Iberian sibling.

Convention #78 BINDING 18TH ENFORCEMENT — 6-language (3rd highest
cohort-wide after Italy 8):
  Spanish (Castellano ~93%) + English (~5%) + Catalan (Català ~10M
  speakers Cataluña+Valencia+Balearic) + Galician (Galego ~2M Galicia)
  + Basque (Euskara ~750k País Vasco+Navarra) + Aranese (Occitan
  ~<5k Val d'Aran).

Convention #78 §4bis.5 Layer 3 13TH ENFORCEMENT candidate:
  Madrid 2-way DSO split (Naturgy inner-metropolitan + Iberdrola
  i-DE outer). Barcelona is single-DSO (Endesa) so no §4bis.5;
  Bilbao is mixed (Iberdrola + Viesgo) but small enough to defer.

Architecture: Portugal P33 bi-directional pattern.
  - Lines: minor_line → 20 kV; cable → 20 kV; line → 66 kV Spanish subT
  - Subs: substation=transmission → 220 kV; substation=distribution
    → 20 kV; substation=minor_distribution → 15 kV; substation=
    traction → 3 kV DC RENFE; power=substation → 20 kV MV default

Discipline #36: 5.0 km tolerance (matches Italy; less remote than
  Portugal's mid-Atlantic archipelagos).

Discipline #41: baseline 6.65 ABOVE_HEALTHY_BAND (sub-poor line-rich —
  MIRROR IMAGE of Portugal baseline 1.10). Wave 4 bi-directional
  Option B should MASSIVELY grow subs, bringing parity to 1.5-3.0.

Layer 4 baselines: R6d_wildfire 0.75 HIGH (2022 Zamora Sierra de la
  Culebra + 2023 Tenerife) + R6c_flood 0.55 (2024 DANA Valencia 220
  dead) + R8_adapt 0.60 MOD-HIGH (2021 COMPLETE coal phase-out FIRST
  major European economy + first-Europe offshore floating wind 2023).
"""

from ._base import (
    ALIAS_MAP,
    BALEARIC_BBOX,
    CANARY_BBOX,
    CEUTA_BBOX,
    MADRID_IBERDROLA_BBOX,
    MADRID_NATURGY_BBOX,
    MAINLAND_BBOX,
    MELILLA_BBOX,
    RESOLVER_LAYERS,
    SPAIN_MASTER_BBOX,
    resolve_operator,
)

__all__ = [
    "ALIAS_MAP",
    "BALEARIC_BBOX",
    "CANARY_BBOX",
    "CEUTA_BBOX",
    "MADRID_IBERDROLA_BBOX",
    "MADRID_NATURGY_BBOX",
    "MAINLAND_BBOX",
    "MELILLA_BBOX",
    "RESOLVER_LAYERS",
    "SPAIN_MASTER_BBOX",
    "resolve_operator",
]
