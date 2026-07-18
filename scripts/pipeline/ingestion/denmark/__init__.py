"""Denmark v4.23 substation + power-line ingestion package.

Wave 3 Priority 28 (seventh Wave 3 country; smallest-first cadence
post-New Zealand at 1558 baseline subs; Denmark at 2433 subs is next
smallest remaining Wave 3 candidate — NORDIC BASELINE-CAPTURED MV/LV
pattern like NZ).

Architecture (multi-DSO Nordic offshore-wind cohort):
- Energinet Danmark A/S — state-owned single national TSO
  (Ministry of Climate, Energy and Utilities). Operates 400/150/
  132 kV backbone across DK1 + DK2 bidding zones. Owns 4 HVDC
  interconnectors (Skagerrak Norway 4 × 240 kV DC + Kontek Germany
  + Kriegers Flak Germany 400 MW + Öresund Sweden AC/HVDC).
  Established 2005 via merger of Eltra (DK1 Jutland) + Elkraft
  System (DK2 Zealand) + Gastra.
- 4 major regional DSOs operating <132 kV distribution:
  * Radius Elnet A/S (Ørsted subsidiary since 2015) — Copenhagen +
    Frederiksberg + North Zealand + Bornholm
    (25% DK customer share)
  * Cerius A/S (Andel/SEAS-NVE since 2020 rebrand) — Zealand
    central + south (Roskilde + Sorø + Vordingborg)
    (9% DK share)
  * N1 A/S (Norlys Holding since 2019 merger) — North + Central
    Jutland (Aarhus + Aalborg + Herning + Randers)
    (15% DK share)
  * Trefor Elnet A/S (EWII since 2016 rebrand) — East Jutland
    (Vejle + Kolding + Fredericia + Middelfart) + Fyn/Funen (Odense)
    (8% DK share)
- 3 minor DSOs (regional coverage): AURA (Aarhus surroundings) +
  Konstant (Silkeborg + Skanderborg) + Dinel (Aarhus metropolitan)
- ~50 municipal DSOs (Aal Elnet + Sunds Elforsyning + etc.)
- Banedanmark — rail traction infrastructure (25 kV AC electrified
  main lines Copenhagen + Fredericia + Padborg to Germany)
- Offshore wind farms (industrial-scale generation, NOT DSO):
  * Ørsted (formerly DONG Energy) — Horns Rev I+II+III + Anholt
    Havmøllepark + Kriegers Flak DK-side
  * Vattenfall Wind Denmark — Horns Rev III partial + Kriegers Flak
    partial
  * European Energy — onshore + offshore renewable developer

FIRST Nordic offshore wind Wave 3 event — establishes offshore
wind terminal precedent for future Sweden/Finland Wave 3
continuations.

Convention #78 BINDING 10th enforcement — DECADE MILESTONE:
- Danish native + English + minimal German Schleswig cohabitation
- Danish diacritics (æ ø å) via NFC normalization
- Legal-form variants (A/S / ApS / AmbA / IvS / FmbA)
- Predecessor rebrands: DONG Energy → Ørsted 2017 + SEAS-NVE →
  Cerius/Andel 2020 + Eltra + Elkraft System → Energinet 2005
- ~100-entry preemptive alias map with Ørsted rebrand + N1 merger
  history + Trefor EWII rebrand

Convention #78 §4bis.5 Layer 3 geofence 6TH ENFORCEMENT:
- Copenhagen (København) metropolitan Radius Elnet geofence
- Cumulative enforcement grows to 6:
  * Prague CZ (Czechia P20)
  * Warsaw PL (Poland P21)
  * EWZ Zurich CH (Switzerland P24)
  * SIG Geneva CH (Switzerland P24)
  * Auckland NZ (New Zealand P27)
  * NEW: Copenhagen DK (Denmark P28)

Author: ikenga-ssi-foundation
Date: 17 July 2026
"""
