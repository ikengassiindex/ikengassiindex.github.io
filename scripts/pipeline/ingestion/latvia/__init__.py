"""SSI Pipeline — Latvia v4.23 ingestion package.

Wave 2 Priority 18 (task #244). 2-operator vertically-integrated state
monopoly via Latvenergo Group holding — Baltic Trio 3rd instance,
empirical completion after Lithuania Priority 16 + Estonia Priority 17.
Queued for Convention #78 sub-convention BINDING promotion methodology-
version event at 3-country cumulative validation.

  - AS Augstsprieguma tīkls (AST): state TSO (100% state-owned via
    Latvenergo Group, 2011 spinoff from Latvenergo Transmission),
    operates 330 kV (Soviet-era EHV backbone) + 110 kV transmission
  - AS Sadales tīkls: unified state DSO (100% state via Latvenergo,
    2007 rename from Sadales tīkli), operates ≤110 kV distribution
    (20 + 10 + 6 + 3 kV Soviet-era voltage mix with dominant 20 kV MV tier)
  - Historical alias handling (DEEPER predecessor depth than
    Estonia/Lithuania — 3 predecessors):
    * Latvijas Elektrostacijas (pre-2005 TSO name) → AST-legacy
    * Latvenergo Transmission (2005-2011 predecessor) → AST-legacy
    * Sadales tīkli (pre-2007 DSO name) → Sadales tīkls-legacy
    * Latvenergo Sadale (earlier DSO predecessor) → Sadales tīkls-legacy
  - Latvian Unicode NFC alias normalisation (diacritics: ā ē ī ō ū č ģ ķ
    ļ ņ š ž — Augstsprieguma tīkls, Latvijas dzelzceļš, Liepājas
    Metalurgs)
  - Cyrillic alias handling (Latgale Russian-speaking OSM contributors)
    — DEEPER cohort than Estonia's Ida-Virumaa: 17.5% baseline share
    (213 subs), 25%+ Russian-speaking population per 2011 census.
    аст / садалес тиклс / латвэнерго / латвияс электростацияс
    preemptively mapped per Convention #78 sub-convention.

Baltic Trio context: Latvia (+ Estonia + Lithuania) desynchronised from
Russian IPS grid February 2025, synchronised with Continental EU grid.
NO direct HVDC to Nordic (unlike Estonia's Estlink 1+2 to Finland).
LatEst 330 kV AC cross-border to Estonia + LatLit 330 kV AC to Lithuania.
NordBalt HVDC subsea to Sweden routes via Lithuania (not directly through
Latvia).
"""
