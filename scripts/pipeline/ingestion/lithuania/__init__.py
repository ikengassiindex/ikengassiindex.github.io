"""SSI Pipeline — Lithuania v4.23 ingestion package.

Wave 2 Priority 16 (task #235). Simplest 2-operator resolver yet — pure
vertically-integrated state monopoly via EPSO-G holding company:
  - Litgrid AB: state TSO (100% state-owned via EPSO-G), operates 400 + 330 + 110 kV
  - ESO (Elektros skirstymo operatorius): unified state DSO (100% state via EPSO-G),
    operates ≤110 kV distribution (35 + 30 + 10 + 0.4 kV)
  - Historical alias handling: Lietuvos energija (pre-2011 TSO name) →
    Litgrid-legacy; LESTO (pre-2016 DSO name) → ESO-legacy
  - Lithuanian Unicode NFC alias normalisation (diacritics: Šiaulių, Vilniaus)

Baltic Trio context: Lithuania (+ Latvia + Estonia) desynchronised from
Russian IPS grid February 2025, synchronised with Continental EU grid.
LitPol Link (400 kV to Poland) + NordBalt HVDC subsea (to Sweden) provide
cross-border interconnections.
"""
