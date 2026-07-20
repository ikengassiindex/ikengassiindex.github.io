"""Japan v4.23 L1 ingestion connector — Wave 4 P35.

🇯🇵 FIFTH Wave 4 country. UNIQUE cohort-wide architectural
signatures:
  - 🌍 FIRST fully islanded grid (no cross-border interconnectors)
  - 🌍 FIRST 50/60 Hz frequency split (Fossa Magna line)
  - 🌍 FIRST 9-regional-utility post-2020 unbundling architecture
  - 🌍 FIRST 6.6 kV MV distribution voltage standard cohort-wide
  - 🚨 HIGHEST cohort-wide R9_compound (0.85 — Fukushima 2011
     canonical earthquake+tsunami+nuclear+typhoon compound event)

Portugal P33 bi-directional Option B pattern INHERITED end-to-end
with Japan-specific voltage defaults:
  - Lines: minor_line/cable → 6.6 kV (Japanese MV standard);
    line → 66 kV Japanese subT (vs Italy 132 kV, Portugal 60 kV)
  - Subs: substation=transmission → 275 kV Japanese HV; substation=
    distribution → 6.6 kV Japanese MV; substation=traction → 1.5 kV
    DC JR classic; power=substation generic → 6.6 kV MV default

Convention #78 BINDING 17TH ENFORCEMENT — 4-language:
  Japanese (~93% — Kanji + Hiragana + Katakana + Rōmaji) + English
  (~5%) + Ainu (~<1% — Hokkaido indigenous statutory 2019 Ainu
  People Promotion Act) + Ryukyuan (~<1% — Okinawa recognized).

Convention #78 §4bis.5 Layer 3 — NOT REQUIRED for Japan:
  Regional-monopoly architectural simplification. Each of 9 regional
  utilities is single-DSO in its non-overlapping territory. Tokyo
  → TEPCO PG only; Osaka → Kansai T&D only; no metro multi-DSO
  splits like Milan/Rome. Sibling pattern to Portugal single-DSO
  simplification.

Discipline #36: 6.0 km cross-border tolerance (matches Portugal —
  archipelago complexity + Ogasawara/Bonin 1,000 km south of Tokyo +
  Sakishima 2,500 km southwest + Rebun/Rishiri + Seto Inland Sea).

Discipline #41: baseline parity 1.97 HEALTHY_BAND; post-Option-B-
  bi-directional projected 2-3 HEALTHY_BAND (proportional growth).

Layer 4 baselines: R6c_flood 0.75 HIGH + R6d_wildfire 0.20 LOW-MOD
  (humid climate) + R6e_winter 0.65 HIGH (Hokkaido -30°C + Niigata
  world's worst snow load) + R9_compound 0.85 🚨 HIGHEST cohort-wide.
"""

from ._base import (
    ALIAS_MAP,
    JAPAN_BBOX,
    RESOLVER_LAYERS,
    resolve_operator,
)

__all__ = [
    "ALIAS_MAP",
    "JAPAN_BBOX",
    "RESOLVER_LAYERS",
    "resolve_operator",
]
