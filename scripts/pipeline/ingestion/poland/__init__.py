"""SSI Pipeline — Poland v4.23 ingestion package.

Wave 2 Priority 21 (task #277). Region-jurisdiction × voltage-class monopoly
via PSE TSO + 4 regional DSOs (PGE Dystrybucja + Tauron Dystrybucja + Enea
Operator + Energa Operator) + Innogy Stoen Warsaw metro Layer 3 geofence.
9th cohort-wide application of region-jurisdiction fallback pattern
(after Belgium + Netherlands + Chile + Hungary + Slovenia + Colombia +
Norway + Slovakia + Czechia).

CONVENTION #78 BINDING ENFORCEMENT — 3RD EMPIRICAL TEST + LAYER 3 GEOFENCE
3RD ENFORCEMENT POST-BINDING + VISEGRÁD TRIO COMPLETION MILESTONE

Third country onboarded post Convention #78 sub-convention BINDING
promotion methodology-version event (Latvia P17 closure 16 July 2026),
following Slovakia P19 1st enforcement + Czechia P20 2nd enforcement.
Poland completes Visegrád Trio at v4.23 (3 of 3, joining Slovakia +
Czechia; Hungary shipped Wave 2 P7 under NUTS-3 sub-convention path).

Preemptive multi-script alias mapping REQUIRED at Step 3 connector
authoring time per Convention #78 BINDING — Poland is the LARGEST
alias-normalisation cohort expected cohort-wide with 5-7 rebrand-
predecessor alias classes:

  - PSE (Polskie Sieci Elektroenergetyczne S.A.): state TSO
    (100% state-owned), operates 750 kV (Rzeszów-Kaliningrad Direct HVAC
    plus interconnectors) + 400 kV Continental European EHV (since 1993
    sync + LitPol Link 2015 to Baltics) + 220 kV backbone
    UNIQUE cohort-wide: PSE operates the only 750 kV cross-border to
    Belarus/Ukraine still active despite Feb 2025 sync events

  - PGE Dystrybucja S.A.: East/NE Poland DSO (LARGEST DSO territorially,
    ~35% market share). Territories: Mazowieckie non-Warsaw +
    Łódzkie + Świętokrzyskie + Lubelskie + Podkarpackie +
    Warmińsko-Mazurskie. Predecessors: PGE Rzeszów + PGE Zamość + PGE
    Lublin + PGE Skarżysko (4 regional predecessors consolidated 2019)
    → CONVENTION #78 BINDING 4-VARIANT PREDECESSOR CASCADE

  - Tauron Dystrybucja S.A.: South Poland DSO (~24% market share).
    Territories: Małopolskie + Śląskie + Opolskie + Dolnośląskie +
    Podkarpackie (Bieszczady portion). Predecessors: EnergiaPro + Enion
    (both consolidated 2008) → CONVENTION #78 BINDING 2-VARIANT PREDECESSOR
    CASCADE

  - Enea Operator sp. z o.o.: West/NW Poland DSO (~19% market share).
    Territories: Wielkopolskie + Zachodniopomorskie + Lubuskie +
    Kujawsko-Pomorskie (Bydgoszcz portion). Predecessors: Zachodniopomorska
    Grupa Energetyczna (ZGE, pre-2007 consolidation) → CONVENTION #78
    BINDING 1-VARIANT PREDECESSOR CASCADE

  - Energa Operator SA: North Poland DSO (~14% market share). Territories:
    Pomorskie + Warmińsko-Mazurskie (Elbląg portion) + Kujawsko-Pomorskie
    (Toruń portion). Predecessors: Grupa Energetyczna Zachód (GEZ,
    pre-2006) + Koncern Energetyczny Energa (2006 consolidation) →
    CONVENTION #78 BINDING 2-VARIANT PREDECESSOR CASCADE

  - Innogy Stoen Operator sp. z o.o.: Warsaw metro DSO (~8% market share).
    Territories: Warszawa admin bounds only. LAYER 3 GEOFENCE 3RD
    ENFORCEMENT POST-BINDING. Predecessors:
    * RWE Stoen Operator (pre-2020 rebrand — RWE Group sold to
      Innogy 2020)
    * Stoen Operator (pre-2016 rebrand — Stoen SA restructured to Stoen
      Operator sp. z o.o. 2016)
    * ZE Warszawa (pre-2003 rebrand — Zakład Energetyczny Warszawa was
      state utility until 2003 privatisation)
    → CONVENTION #78 BINDING 3-GENERATION PREDECESSOR CASCADE (unique
    cohort-wide multi-generational rebrand tracking; NEW sub-convention
    candidate for multi-generation rebrand-predecessor tracking)

  - Historical predecessors (pre-1990 state utility system):
    * Zjednoczone Zakłady Energetyczne (ZZE) → pre-consolidation regional
    * Zjednoczenie Energetyczne (ZE) prefix → regional predecessors
    preserved honestly per Convention #56

  - Polish NFC alias normalisation (ą ć ę ł ń ó ś ź ż)
  - Cyrillic alias handling (Belarusian minority OSM in Podlaskie +
    Ukrainian minority OSM in eastern Silesia + Kaliningrad-adjacent
    Overpass contribution)
  - Polish typographic-quote variants („…" like German/Czech/Latvian)

Poland context: Visegrád Group member (V4 with Czech Republic + Slovakia
+ Hungary). EU-synchronised Continental European zone since 1993, plus
LitPol Link HVAC 2015 to Baltic Trio (which desynchronised from BRELL
Feb 2025). Bordering 7 countries: Germany W + Czech Republic S + Slovakia
S + Ukraine E + Belarus E + Lithuania NE + Russia (Kaliningrad enclave)
NE. Cross-border transmission preserved cleanly via Discipline #36
100m tolerance.

Private industrial captives + non-DSO operators:
  - KGHM Polska Miedź (Zagłębie Miedziowe copper mining — Lubuskie/
    Dolnośląskie)
  - JSW Jastrzębska Spółka Węglowa (Silesian coal mining)
  - PKN Orlen (Płock petrochemical + Trzebinia refinery)
  - PKP Energetyka (Polish State Railways electric traction — 3 kV DC)
  - Tram/metro traction operators (Warszawski Metro + PKM Warszawa +
    MPK Kraków + MPK Wrocław + MZKZG Gdańsk)
  - Direct OSM operator= tag preserved for these entities (not resolved
    via Layer 3 geofence)
"""
