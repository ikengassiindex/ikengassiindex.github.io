"""Korea v4.23 substation + power-line ingestion package.

Wave 3 Priority 26 (fifth Wave 3 country; smallest-first cadence
post-Ireland at 994 baseline subs; Korea at 1290 subs is next
smallest remaining).

Architecture (SIMPLEST cohort-wide via KEPCO monopoly):
- KEPCO (Korea Electric Power Corporation) — vertically-integrated
  state-owned utility owning ALL substations across ALL voltage
  tiers (765 / 345 / 154 / 55 / 22.9 kV). No unbundled TSO/DSO
  split (unlike Ireland EirGrid + ESB Networks or Greek IPTO +
  DEDDIE).
- KPX (Korea Power Exchange) — market operator handling dispatch
  only, NOT asset ownership. NO substations attributed to KPX.
- KHNP (Korea Hydro & Nuclear Power) — nuclear plant operator.
  6 nuclear-plant substation identities carved out at Layer 1
  by name pattern (Kori/Hanbit/Hanul/Wolseong/Saeul + Shin-*
  prefix variants).
- 5 GENCOs (post-2001 unbundling) — East-West / KOSPO / KOWEPO /
  KOMIPO / KOEN — own generation only, NOT distribution.
  Handled as generation-adjacent substations at Layer 2.
- Industrial captives — POSCO Energy + GS EPS + SK Gas + Hyundai
  Green Power + Samsung self-generation + KDHC district-heating
  CHP + KORAIL rail traction. Layer 2 identity via name pattern.
- Jeju HVDC interconnector — 3 submarine cables (300+300+400 MW)
  to Haenam mainland. DOMESTIC (Jeju is Korean territory), NOT
  cross-border. KEPCO owned.
- KR-ISOLATED grid — no cross-border interconnector (DMZ + no
  submarine link to Japan/China). 3rd cohort-wide non-cross-border
  grid (after Iceland + Greenland).

Convention #78 BINDING 8th enforcement — FIRST Asian Wave 3 event:
- Multi-script cohabitation: Hangul (한글) + Latin transliteration
  (Revised Romanization + McCune-Reischauer) + English acronyms
- 100-entry preemptive alias map:
  * KEPCO variants: 한국전력공사 / 한전 / Hanguk Jeollyeok Gongsa
    / Han'guk Chŏllyŏk Kongsa / KEPCO / Korea Electric Power
    Corporation + legal-form suffixes (주식회사 / 株式會社 / ㈜)
  * KHNP + 6 nuclear-plant identities (Kori/Hanbit/Hanul/
    Wolseong/Saeul + Shin-* prefix variants)
  * 5 GENCOs post-2001 unbundling (EWP/KOSPO/KOWEPO/KOMIPO/KOEN)
  * Chaebol industrial captives (POSCO/GS EPS/SK/Hyundai/Samsung)
  * KDHC district-heating + KORAIL rail traction
- Hangul NFC normalization for jamo composition
- Historical predecessor: KECO (pre-1982 Korea Electric Company)
  → 3 utilities merger → KEPCO 1982
- LARGEST projected cohort-wide alias hit count for Hangul script
  (~100-200 hits given multi-script cohabitation)

Convention #78 §4bis.5 Layer 3 geofence NOT NEEDED — KEPCO monopoly
covers all 17 do/si first-tier admin regions (Ireland/Greek/
Costa Rica single-DSO precedent applies).

Cumulative Layer 3 geofence enforcement stays at 4:
Prague CZ + Warsaw PL + EWZ Zurich + SIG Geneva
Korea DOES NOT increment this count.

Author: ikenga-ssi-foundation
Date: 17 July 2026
"""
