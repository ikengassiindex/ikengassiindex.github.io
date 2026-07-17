"""New Zealand v4.23 substation + power-line ingestion package.

Wave 3 Priority 27 (sixth Wave 3 country; smallest-first cadence
post-Korea at 1290 baseline subs; NZ at 1558 subs is next smallest
remaining Wave 3 candidate).

Architecture (RICHEST cohort-wide multi-DSO — 29 EDBs):
- Transpower New Zealand Ltd — state-owned single national TSO
  operating 220/110/66 kV backbone including 1200 MW Cook Strait
  HVDC Inter-Island link (Kikiwa South Island + Haywards North
  Island; 2 x 350 kV DC bipole + 1 x 500 kV DC pole 3).
  ~11,000 km transmission network.
- 29 EDBs (Electricity Distribution Businesses) operating MV/LV
  distribution (33/22/11/0.4 kV) across all 16 NZ regions.
  RICHEST multi-DSO cohort-wide (Swiss 8-way was previous max):
  * NORTH ISLAND (16 EDBs):
    - Northland: Top Energy (northern) + Northpower (southern)
    - Auckland: Vector (metropolitan) + Counties Energy (southern)
      — Convention #78 §4bis.5 Layer 3 5th enforcement carve-out
    - Waikato: WEL Networks + Waipa Networks + The Lines Company
      + Powerco (Coromandel + eastern)
    - Bay of Plenty: Horizon Networks + Unison Networks (Rotorua)
    - Gisborne: Eastland Network
    - Hawke's Bay: Unison Networks
    - Taranaki: Powerco
    - Manawatu-Whanganui: Powerco + Electra (Kapiti + Horowhenua)
    - Wellington: Wellington Electricity + Powerco (Wairarapa)
  * SOUTH ISLAND (13 EDBs):
    - Marlborough: Marlborough Lines
    - Nelson: Nelson Electricity
    - Tasman: Network Tasman + Powerco (western)
    - West Coast: Westpower + Buller Electricity
    - Canterbury: Orion NZ (Christchurch) + MainPower NZ (North
      Canterbury) + Alpine Energy (South Canterbury) + Network
      Waitaki (Waimate)
    - Otago: Aurora Energy (Dunedin + Central) + OtagoNet (coastal)
    - Southland: PowerNet (Invercargill + Stewart Island) +
      The Power Company (Fiordland + Te Anau)
- KiwiRail rail traction (25 kV AC — main trunk line electrified
  Palmerston North to Hamilton + Auckland metro rail 25 kV AC)
- NZAS Tiwai Point aluminium smelter (Southland — Meridian Energy
  hydro contract, largest single industrial captive)
- Methanex methanol production (Taranaki — Motunui + Waitara)
- Cook Strait HVDC Inter-Island link (DOMESTIC — Jeju-analog:
  intra-NZ, NOT cross-border)
- KR-ISOLATED grid — no submarine link to Australia or Pacific
  islands (Chatham Islands + Kermadec + Tokelau are territorial
  extensions of NZ, Mode 3 pattern from Discipline #36 remediation)

Convention #78 BINDING 9th enforcement — FIRST Southern Hemisphere
Wave 3 event + FIRST English multi-DSO Wave 3 (Ireland was single-DSO):
- English-dominant (~95% expected) + Māori Te Reo cohabitation (~5%)
- ~120-entry preemptive alias map:
  * Transpower variants (Ltd/Limited/New Zealand/NZ)
  * 29 EDB variants + subsidiary aliases
  * Māori diacritics (macrons ā ē ī ō ū) via NFC normalization
  * Māori Te Reo names (Aotearoa cohabit + Ara Whanui KiwiRail Māori)
  * Industrial captives (NZAS Tiwai + Methanex + Fonterra)
  * Generation-retail separation (Meridian/Mercury/Genesis/Contact
    Energy OWN generation but grid is Transpower — must be routed
    to Transpower for substations, NOT to the generation-retail
    entity)
- 30-80 alias-normalisation hits projected (LOWER than Korean 198
  hits given English dominance)

Convention #78 §4bis.5 Layer 3 geofence 5th enforcement:
- Auckland metropolitan carve-out (Vector CBD + Counties Energy south)
- Cumulative enforcement grows to 5:
  * Prague CZ (Czechia P20)
  * Warsaw PL (Poland P21)
  * EWZ Zurich CH (Switzerland P24)
  * SIG Geneva CH (Switzerland P24)
  * NEW: Auckland NZ (Vector vs Counties Energy — 5th)

Author: ikenga-ssi-foundation
Date: 17 July 2026
"""
