"""Finland v4.23 substation + power-line ingestion package.

Wave 3 Priority 29 (eighth Wave 3 country; smallest-first cadence
post-Denmark at 2433 baseline subs; Finland at 3885 subs is next
smallest remaining Wave 3 candidate — extends Nordic cluster).

Architecture (multi-DSO Nordic cohort + Finnish/Swedish/Sami trilingual):
- Fingrid Oyj — state-owned single national TSO (53.1% State + 27.2%
  Ilmarinen + 19.7% other institutional). Operates 400/220/110 kV
  backbone. Fenno-Scandia ENTSO-E synchronous grid via Sweden/Norway
  + Estonia EstLink 1+2 HVDC. Owns 4 HVDC interconnectors:
  * EstLink 1 (350 MW) — Anttila FI ↔ Harku EE (2007)
  * EstLink 2 (650 MW) — Anttila FI ↔ Püssi EE (2014)
  * FennoSkan 1 (400 MW) — Rauma FI ↔ Dannebo SE (1989)
  * FennoSkan 2 (800 MW) — Rauma FI ↔ Finnböle SE (2011)
  Established 1996 unbundling from IVO (Imatran Voima).
- Nuclear generation (owns generation NOT grid):
  * Teollisuuden Voima (TVO) — Olkiluoto 1+2 (BWR) + Olkiluoto 3
    (world's largest EPR, commissioned 2023)
  * Fortum — Loviisa 1+2 (VVER-440)
- 6 major DSOs operating <110 kV distribution + some 110 kV:
  * Caruna Oy (LARGEST — First Sentier Investors + Elo + KEVA
    consortium since 2014 Fortum sale) — Uusimaa (excl Helsinki) +
    Varsinais-Suomi + Satakunta + Etelä-Pohjanmaa + Pohjanmaa +
    Keski-Pohjanmaa (~1M customers)
  * Elenia Oy (Vattenfall Finland Distribution → Elenia 2012
    rebrand) — Pirkanmaa (Tampere) + Kanta-Häme + Päijät-Häme +
    Keski-Suomi + Pohjois-Pohjanmaa (~430k customers)
  * Helen Sähköverkko Oy (Helsinki Municipal / Helen Oy
    subsidiary) — Helsinki city (~400k customers)
    → Convention #78 §4bis.5 7TH ENFORCEMENT geofence subject
  * Vantaan Energia Sähköverkot Oy (Vantaa + Kerava + Helsinki +
    Espoo Municipal) — Vantaa northern suburb (~110k customers)
  * Turku Energia Sähköverkot / Åbo Energi (Turku Municipal) —
    Turku city (~135k customers)
  * Tampereen Sähkölaitos (Tampere Municipal) — Tampere city core
    (co-exists with Elenia in surrounding Pirkanmaa)
- Minor regional DSOs: Savon Voima Verkko (Savonia) + KSS-verkko
  (Kymenlaakso) + Lappeenrannan Energia (South Karelia) +
  Rovaniemen Energia (Lappi) + Tornion Energia (Tornio border)
- ~80 municipal DSOs (Nordic municipal cooperative tradition)
- Åland autonomous jurisdiction — Kraftnät Åland (TSO) +
  Mariehamns Elnät (DSO). Åland has separate energy law
  (Elmarknadslag) + separate HVDC connection to Sweden
- VR Group — rail traction 25 kV AC electrified main lines
  (Helsinki-Turku + Helsinki-Tampere-Oulu + Karelia line)

Convention #78 BINDING 11th enforcement (post DECADE MILESTONE):
- Finnish native (majority) + Swedish constitutional bilingual
  (Åland 100% + Bothnian coast Vaasa/Kokkola) + Sami minority
  (Lappi region: Northern/Skolt/Inari — ŋ ǯ â diacritics)
- Finnish diacritics (ä ö å) + Swedish diacritics (å ä ö) +
  Sami extended diacritics (ŋ ǯ â) via NFC normalization
- ~130-entry preemptive alias map with Nordic predecessor rebrands
  (Fortum→Caruna 2014 + Vattenfall→Elenia 2012 + IVO→Fortum 1998)

Convention #78 §4bis.5 Layer 3 geofence 7TH ENFORCEMENT:
- Helsinki metropolitan Helen Sähköverkko vs Vantaan Energia
  vs Caruna (Uusimaa outside metros) 3-way split
- Cumulative enforcement grows to 7:
  * Prague CZ (Czechia P20)
  * Warsaw PL (Poland P21)
  * EWZ Zurich CH (Switzerland P24)
  * SIG Geneva CH (Switzerland P24)
  * Auckland NZ (New Zealand P27)
  * Copenhagen DK (Denmark P28 — 6TH; HIGHEST hits 615)
  * NEW: Helsinki FI (Finland P29 — 7TH)

Author: ikenga-ssi-foundation
Date: 18 July 2026
"""
