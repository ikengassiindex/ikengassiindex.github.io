"""Iceland v4.23 substation + power-line ingestion package.

Wave 3 Priority 23 (second Wave 3 country; smallest-first cadence
post-Greece at 684 baseline subs).

Architecture:
- Landsnet single TSO (established 2005, unbundled from Landsvirkjun per
  EU 3rd Package)
- 5 regional DSOs: Veitur (OR — Capital Region) + RARIK (rural + N/S/E) +
  HS Veitur (Reykjanes + Vestmannaeyjar) + Norðurorka (Akureyri) +
  Orkubú Vestfjarða (Westfjords)
- Isolated grid (no cross-border interconnector — unique Wave 3 feature)
- 100% renewable (70% hydro + 30% geothermal + wind pilot)

Convention #78 BINDING 5th enforcement:
- Icelandic script (Þ ð æ ö) — NEW class cohort-wide
- Latin transliteration (d/oe/ae/th)
- English acronyms (none — Icelandic-first)
- Legal form: hf. / ohf. (hlutafélag / opinbert hlutafélag)
- Predecessor rebrand: Landsvirkjun pre-2005 + Hitaveita Suðurnesja
  pre-2008 + Rafmagnsveitur ríkisins pre-2006 + Rafveita Akureyrar pre-2000

Convention #78 §4bis.5 Layer 3 geofence:
- Reykjavík Capital Region (Höfuðborgarsvæðið) — Veitur vs Landsnet HV
  coexistence LIKELY REQUIRED (empirical validation at Step 4)

Author: ikenga-ssi-foundation
Date: 17 July 2026
"""
