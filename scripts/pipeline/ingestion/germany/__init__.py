"""Germany v4.23 L1 ingestion connector — Wave 4 P38.

🇩🇪 EIGHTH Wave 4 country (penultimate before US P39 TERMINAL closure).
Portugal P33 bi-directional Option B pattern INHERITED at Germany-wide +
16-Bundesländer + 4-TSO decentralised architecture scale.

Convention #78 BINDING 20TH ENFORCEMENT — 5-language German:
  German (~95%) + English (~4%) + Sorbian + Danish + Frisian (3 regional
  minorities). Mid-cohort ranking (below Italy 8 + France 8 + Spain 6;
  above Portugal/Sweden/Japan 4).

Convention #78 §4bis.5 Layer 3 — NOT REQUIRED for Germany:
  🏆 NEW ARCHITECTURAL SIGNATURE — MOST-FRAGMENTED cohort-wide DSO
  landscape (~900 DSOs) with HORIZONTAL non-overlapping territories.
  Different mechanism from Portugal single-DSO / Japan regional-monopoly /
  France Enedis-dominant simplifications. FOURTH cohort-wide NO §4bis.5
  country via NEW pattern.

Architecture: Portugal P33 bi-directional pattern.
  - Lines: minor_line → 20 kV; cable → 20 kV; line → 110 kV Hochspannung
    (UNIQUELY COMMON cohort-wide — Germany extensively uses 110 kV HV
    distribution more than most EU peers)
  - Subs: substation=transmission → 380 kV EHV German backbone;
    substation=distribution → 20 kV Mittelspannung; substation=minor →
    10 kV legacy MV; substation=traction → 15 kV AC 16.7 Hz Deutsche
    Bahn UNIQUE Central European standard (shared with AT+CH+NO+SE);
    power=substation → 20 kV MV default

Discipline #36: 5.0 km tolerance (matches Italy + Spain — continental
  European coastline+ridge complexity + 9-country land border HIGHEST
  cohort-wide).

Discipline #41: baseline parity TBD (rich baseline expected —
  Germany OSM density HIGHEST cohort-wide for infrastructure).

Layer 4 baselines: R8_adapt 0.70 🏆 HIGHEST-COHORT-WIDE (Energiewende +
  nuclear phase-out complete April 2023 + Kohleausstieg 2038 +
  Klimaschutzgesetz climate-neutral 2045 — 5 yr more ambitious than
  France 2050) + R10_just 0.65 (Kohleausstieg justice-transition +
  IG BCE/verdi labor + AfD populism + Sorbian + Danish + Frisian
  minorities + East-West income gap post-Wende + Bavarian sovereignty).

4-TSO decentralised architecture: 50Hertz east + Amprion west + TenneT
  DE north-south spine + TransnetBW Baden-Württemberg southwest.
"""

from ._base import (
    ALIAS_MAP,
    GERMANY_MASTER_BBOX,
    NORD_BBOX,
    WEST_BBOX,
    MITTE_BBOX,
    OST_BBOX,
    SUED_BBOX,
    RESOLVER_LAYERS,
    resolve_operator,
)

__all__ = [
    "ALIAS_MAP",
    "GERMANY_MASTER_BBOX",
    "NORD_BBOX",
    "WEST_BBOX",
    "MITTE_BBOX",
    "OST_BBOX",
    "SUED_BBOX",
    "RESOLVER_LAYERS",
    "resolve_operator",
]
