"""SSI Pipeline — Estonia v4.23 ingestion package.

Wave 2 Priority 17 (task #238). 2-operator vertically-integrated state
monopoly via Eesti Energia Grupp holding — Baltic Trio 2nd instance
after Lithuania Priority 16:

  - Elering AS: state TSO (100% state-owned via Eesti Energia Grupp,
    2010 spinoff), operates 450 kV DC (Estlink 1+2 HVDC to Finland) +
    330 kV (Soviet-era EHV backbone) + 110 kV transmission
  - Elektrilevi OÜ: unified state DSO (100% state via Eesti Energia,
    2013 spinoff), operates ≤110 kV distribution (35 + 10 + 0.4 kV)
  - Historical alias handling: Põhivõrk (pre-2010 TSO name) →
    Elering-legacy; Eesti Energia Jaotusvõrk (pre-2013 DSO name) →
    Elektrilevi-legacy
  - Estonian Unicode NFC alias normalisation (diacritics: Ä Ö Õ Ü Š Ž;
    Põhivõrk, Jaotusvõrk, Šiaulių-analogue Estonian toponyms)
  - Cyrillic alias handling (Ida-Virumaa / Narva Russian-speaking OSM
    contributors) — Элеринг / Электрилеви preemptively mapped per
    Convention #78 sub-convention on multi-script OSM handling

Baltic Trio context: Estonia (+ Latvia + Lithuania) desynchronised from
Russian IPS grid February 2025, synchronised with Continental EU grid.
Estlink 1 (450 kV DC, 2006, 350 MW) + Estlink 2 (450 kV DC, 2014, 650 MW)
HVDC subsea to Finland provide cross-border interconnection.
LatEst cross-border tie at Latvia border to south.
"""
