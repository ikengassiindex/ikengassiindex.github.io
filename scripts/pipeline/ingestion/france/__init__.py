"""France v4.23 L1 ingestion connector — Wave 4 P37.

🇫🇷 SEVENTH Wave 4 country. Portugal P33 bi-directional Option B
pattern INHERITED at Franco-metropolitan + DOM/COM overseas scale.

Convention #78 BINDING 19TH ENFORCEMENT — 8-language TIES ITALY
HIGHEST cohort-wide:
  French (~94%) + English (~5%) + Corsican + Breton + Basque +
  Alsatian + Catalan + Occitan (6 regional minorities).

Convention #78 §4bis.5 Layer 3 — NOT REQUIRED for France:
  Regional-dominant-DSO simplification (Enedis ~95% mainland + ~150
  small regional ELDs ~5%). Third cohort-wide simplification after
  Portugal P33 single-DSO + Japan P35 regional-monopoly.

Architecture: Portugal P33 bi-directional pattern.
  - Lines: minor_line → 20 kV; cable → 20 kV; line → 63 kV French subT
  - Subs: substation=transmission → 225 kV French HV (UNIQUE cohort-wide);
    substation=distribution → 20 kV Enedis MV; substation=minor →
    15 kV MV rural; substation=traction → 1.5 kV DC SNCF classic +
    25 kV AC 50 Hz TGV; power=substation → 20 kV MV default

Discipline #36: 6.0 km tolerance (matches Portugal + Japan + UK —
  DOM/COM globally distributed archipelago complexity).

Discipline #41: baseline parity 5.43 slightly ABOVE_HEALTHY_BAND
  (sub-poor line-rich like Spain baseline 6.65). Wave 4 bi-directional
  Option B should grow subs to bring parity to 1.5-3.0 HEALTHY_BAND.

Layer 4 baselines: R8_adapt 0.65 MOD-HIGH (nuclear leadership 70%
  electricity + SNBC + Loi Climat + first-Europe offshore Saint-Nazaire
  2022) + R10_just 0.60 (Fessenheim + coal 2022 + Gilets Jaunes +
  6-language regional minorities + DOM/COM autonomies).

LARGEST cohort-wide bounds.json: 101 features (96 métro dépts +
  Corsica + 5 DOM territories).
"""

from ._base import (
    ALIAS_MAP,
    FRANCE_MASTER_BBOX,
    MAINLAND_BBOX,
    CORSICA_BBOX,
    GUADELOUPE_BBOX,
    MARTINIQUE_BBOX,
    GUYANE_BBOX,
    REUNION_BBOX,
    MAYOTTE_BBOX,
    SAINT_PIERRE_MIQUELON_BBOX,
    RESOLVER_LAYERS,
    resolve_operator,
)

__all__ = [
    "ALIAS_MAP",
    "FRANCE_MASTER_BBOX",
    "MAINLAND_BBOX",
    "CORSICA_BBOX",
    "GUADELOUPE_BBOX",
    "MARTINIQUE_BBOX",
    "GUYANE_BBOX",
    "REUNION_BBOX",
    "MAYOTTE_BBOX",
    "SAINT_PIERRE_MIQUELON_BBOX",
    "RESOLVER_LAYERS",
    "resolve_operator",
]
