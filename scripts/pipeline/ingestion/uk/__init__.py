"""UK v4.23 substation + power-line ingestion package.

🎉 WAVE 4 P31 = FIRST v4.23 ENHANCEMENT EXTENSION COUNTRY 🎉
Post-Brexit non-ENTSO-E synchronous jurisdiction with:
- LOWEST cohort-wide baseline line count 807 (192× less than Norway 154,728)
- Dual-market architecture (GB National Grid ESO + NI I-SEM SONI)
- 7 subsea + 1 land + 1 pending Ireland interconnectors
- RICHEST cohort-wide island archipelago
- FIRST v4.23 enhancement to use Wave 4 CORRECTED architecture
  emitting canonical compact `{s, l, a}` schema (post-Turkey schema-bug lesson)

Architecture (dual-market + 14 DNO licence areas + Northern Ireland):

Great Britain Transmission:
- National Grid ESO (post-2019 unbundling; 2024 nationalized DESNZ)
  operates 400/275 kV backbone TSO
- National Grid Electricity Transmission (NGET) — England + Wales asset owner
- Scottish Power Transmission (SPT) — Central + Southern Scotland
- Scottish Hydro Electric Transmission (SHE-T / SSEN Transmission) —
  Northern Scotland incl. Shetland HVDC 2024

Great Britain Distribution — 6 DNO groups holding 14 licence areas:
1. UK Power Networks (UKPN) — London + South East + East England (3 areas)
   * LONDON POWER NETWORKS = Convention #78 §4bis.5 9TH ENFORCEMENT candidate
2. National Grid Electricity Distribution (NGED, ex-WPD) — Midlands +
   South West + South Wales (4 areas)
3. SP Energy Networks (SPEN, ScottishPower) — Central+Southern Scotland +
   Merseyside + North Wales (2 areas)
4. Scottish and Southern Electricity Networks (SSEN) — Northern Scotland +
   Southern England (2 areas)
5. Electricity North West (ENW) — North West England (1 area)
6. Northern Powergrid (NPG) — North East + Yorkshire (2 areas)

Northern Ireland (separate market I-SEM with ROI):
- SONI (System Operator for Northern Ireland) — TSO owned by EirGrid plc
- NIE Networks — combined DNO+TNO; owned by ROI state-owned ESB Group

Crown Dependencies (separate jurisdictions, not part of UK):
- Manx Utilities (Isle of Man)
- Jersey Electricity + Guernsey Electricity (Channel Islands)

Convention #78 BINDING 13th enforcement (5-language):
- English (majority) — Latin alphabet
- Welsh (Cymraeg) — Latin + ŵ ŷ â ê î ô û circumflex accents
- Scots Gaelic (Gàidhlig) — Latin + à è ì ò ù grave accents
- Irish (Gaeilge — NI recognized) — Latin + á é í ó ú fada accents
- Cornish (Kernewek) — Latin (revived 2003 recognized)

Convention #78 §4bis.5 Layer 3 9TH ENFORCEMENT candidate:
- London metropolitan UKPN London Power Networks geofence
- Bbox lat [51.28, 51.72] × lon [-0.51, 0.34] Greater London Authority
- 2.4M customers within LPN licence area

Interconnector portfolio (7 subsea + 1 land + 1 pending Ireland):
- IFA (1986 France 2000 MW) + IFA2 (2021 France 1000 MW)
- BritNed (2011 Netherlands 1000 MW)
- Nemo Link (2019 Belgium 1000 MW)
- North Sea Link (2021 Norway 1400 MW WORLD'S LONGEST subsea HVDC 720 km)
- ElecLink (2022 France via Channel Tunnel 1000 MW FIRST land-based)
- Viking Link (2023 Denmark 1400 MW)
- Greenlink (2024 PENDING Ireland 500 MW FIRST UK-Ireland HVDC)

Discipline #36: 3.0 km cross-border tolerance (post-Brexit precedent +
Northern Ireland land border + island archipelago).

Discipline #41 baseline pre-enhancement: 807 / 2,551 = 0.32 SEVERELY
BELOW healthy band [1.5-5.0] (LOWEST cohort-wide). Post-Wave-4
enhancement target: 2.0-4.5 healthy band.

Wave 4 architectural corrections (post-Turkey schema-bug lesson):
- OSM Overpass query hints: `out center` for way substations + `out geom`
  for lines (proper coord resolution)
- Merger emits canonical compact `{s, l, a}` schema from start
- Substation ID assignment (integer 10-digit 5000000000+ per UK convention)
- Line ID assignment (integer 30000000+ per UK convention)
- Polyline conversion to compact `p: [[lon, lat], ...]` format
- Line endpoint (ss/se) matching against substation dict (STRING IDs per UK convention)
- Adjacency graph construction (optional; UK baseline has empty a dict)

Author: ikenga-ssi-foundation
Date: 2026-07-18
"""
