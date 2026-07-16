"""SSI Pipeline — Czechia v4.23 ingestion package.

Wave 2 Priority 19 (task #249). Region-jurisdiction x voltage-class monopoly
via SEPS TSO + 3 regional DSOs (ZSD + SSD + VSD) via clean NUTS-3
partition. 7th cohort-wide application of region-jurisdiction fallback
pattern (after Belgium + Netherlands + Chile + Hungary + Slovenia +
Colombia + Norway).

CONVENTION #78 BINDING ENFORCEMENT - FIRST EMPIRICAL TEST

First country onboarded post Convention #78 sub-convention BINDING
promotion methodology-version event (Latvia Priority 18 closure, 16
July 2026). Preemptive multi-script alias mapping REQUIRED at Step 3
connector authoring time:

  - SEPS (Slovenska elektrizacna prenosova sustava a.s.): state TSO
    (100% state-owned), operates 750 kV (Mir/Slavia Ukraine cross-border)
    + 400/420 kV Continental European EHV + 220 kV Soviet-era HV +
    110 kV transmission
  - ZSD (Zapadoslovenska distribucna a.s.): West Czechia DSO,
    NUTS-3: SK010 + SK021 + SK022 + SK023 (parent: ZSE 51 state / 49 E.ON)
  - SSD (Stredoslovenska distribucna a.s.): Centre Czechia DSO,
    NUTS-3: SK031 + SK032 (parent: SSE 51 state / 49 EPH)
  - VSD (Vychodoslovenska distribucna a.s.): East Czechia DSO,
    NUTS-3: SK041 + SK042 (parent: VSE 51 state / 49 RWE Innogy)
  - Historical predecessors:
    * Slovensky energeticky podnik s.p. (pre-2002) -> SEPS-legacy
    * *slovenske energeticke zavody (pre-2005) -> *SD-legacy
  - Czech Unicode NFC alias normalisation (c s z d l n t l r a i o u y)
  - Cyrillic alias handling (Rusyn + Ukrainian minority OSM in eastern
    Czechia - Presov + Kosice bordering Ukraine)
    SEPS/ZSD/SSD/VSD Cyrillic renderings preemptively mapped per
    Convention #78 BINDING
  - Czech typographic-quote variants (like Czech/German/Latvian)
    preemptively mapped per Convention #78 BINDING (Latvia precedent)

Czechia context: Visegrad Group member (V4 with Czech Republic + Poland
+ Hungary). EU-synchronised Continental zone pre-2025 (no Baltic Trio
EU synchronisation event). 5-country border zone: Czech Republic NW +
Poland N + Ukraine E (750 kV Mir/Slavia cross-border HVAC preserved
post-Ukraine grid disconnection Feb 2025) + Hungary S + Austria W.
"""
