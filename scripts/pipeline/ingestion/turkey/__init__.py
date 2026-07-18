"""Turkey v4.23 substation + power-line ingestion package.

🎉 COHORT COMPLETION MILESTONE 🎉
Wave 3 Priority 30 = LAST v4.23 refresh candidate.
Post-Turkey closure: 39/39 canonical cohort empirical completion.

Architecture (bi-continental jurisdiction + RICHEST cohort-wide 7-border
+ RICHEST cohort-wide DSO count 21 + FIRST post-2015 ENTSO-E accession):

TSO:
- TEİAŞ (Türkiye Elektrik İletim Anonim Şirketi) — state-owned 100%
  Ministry of Energy. Operates 380/154/66 kV backbone. ENTSO-E
  synchronous grid since September 2015 (Kapıkule/Nea Santa Thrace
  synchronization point). 7 cross-border interconnectors:
  * Bulgaria — Kapıkule 380 kV AC (ENTSO-E synchronous)
  * Greece — Nea Santa 400 kV AC (ENTSO-E synchronous)
  * Georgia — Meltem 400 kV AC + Kars 154 kV AC
  * Armenia — Iğdır sealed since 1993 (Nagorno-Karabakh conflict)
  * Iran — Doğubayazıt 500 kV HVDC (asynchronous DC block)
  * Iraq — Cizre 400 kV AC (post-2003 synchronous with Iraqi grid)
  * Syria — Kilis/Reyhanlı DC blocks curtailed post-2011 civil war
  Established 2001 unbundling from TEK (Türkiye Elektrik Kurumu):
  TEK → TEİAŞ (transmission) + TEDAŞ (dist wholesale) + EÜAŞ
  (generation) + TETAŞ (trading, merged into EÜAŞ 2019).

Nuclear generation (owns generation NOT grid):
- Akkuyu NPP (Rosatom VVER-1200 × 4 = 4.8 GW) — Mersin province,
  construction 2018-2028; first reactor grid-sync 2025 pending.
  Layer 4b generation carve-out.
- Sinop 2nd nuclear plant cancelled 2018+2020 (KEPCO withdrew)

21 privatized DSOs post-2013 (RICHEST cohort-wide DSO count):
- Istanbul 3-way (Convention #78 §4bis.5 8TH ENFORCEMENT):
  * BEDAŞ (Boğaziçi Elektrik Dağıtım A.Ş.) — European Istanbul
    ~4.5M customers (Cengiz-Kolin-Limak Consortium)
  * AYEDAŞ (Anadolu Yakası Elektrik Dağıtım A.Ş.) — Asian Istanbul
    ~3M customers (Enerjisa E.ON + Sabancı)
  * BOĞAZİÇİ (Bosphorus strait carve-out) — 3 HV crossings +
    legacy pre-2013 operator name capture
- Marmara/Aegean/Mediterranean coastal:
  * TREDAŞ (Thrace European) + UEDAŞ (Bursa) + OEDAŞ (Eskişehir)
  * Gediz (İzmir) + Aydem (Aydın-Denizli-Muğla) + Akdeniz (Antalya)
  * Toroslar (Adana-Mersin-Hatay-Osmaniye-Gaziantep-Kilis —
    2023 earthquake RECONSTRUCTION zone)
- Central Anatolia:
  * Başkent (Ankara + 6 provinces) + Meram (Konya) + KCETAŞ
    (Kayseri — ONLY non-privatized municipal DSO)
- Black Sea:
  * YEDAŞ (Samsun — 2021 Karadeniz FLOOD RECOVERY zone)
  * ÇEDAŞ (Sivas central) + Çoruh (Rize-Trabzon-Artvin high-seismic)
- Eastern Anatolia:
  * Fırat (Elazığ RECONSTRUCTION partial) + Aras (Erzurum-Kars-
    Iğdır Armenian border-CLOSED + Georgian border)
- Southeast Anatolia (Kurdish region + refugee integration):
  * Dicle (Diyarbakır-Şırnak-Batman-Mardin-Şanlıurfa — 4M Syrian
    refugee LARGEST global cohort)
  * Van Gölü (Van-Bitlis-Muş-Hakkari — Iranian/Iraqi border +
    2011 earthquake legacy)
- SEDAŞ (Sakarya-Kocaeli-Bolu-Düzce)

Cross-sector operators (Layer 2 catchment):
- BOTAŞ (natural gas TSO — gas pipeline compressor stations)
- TCDD (state railways — 25 kV AC electrified YHT high-speed +
  Ankara-İstanbul + Konya-Karaman lines)

Convention #78 BINDING 12th enforcement (post-DECADE-MILESTONE):
- Turkish (majority) — Latin alphabet 1928 reform + 6 diacritics
  ç ğ ı ö ş ü (unique cohort-wide diacritic set)
- Kurdish (SE region ~20% pop; recognized 2013) — Latin alphabet
  with additional diacritics ê î û
- Arabic (SE Syrian refugee cohort 4M LARGEST global) — Arabic
  script for border-region OSM tags
- Greek (Aegean legacy + Rum minority ~2500 in Istanbul)
- English (~5% — international OSM tagging + operator brands)
- Ottoman Turkish (pre-1928 alphabet reform — legacy historical
  site names in Osmanlıca Arabic script)
- ~150-entry preemptive alias map with:
  * Turkish-diacritic canonical forms + ASCII fallbacks
  * BEDAŞ/AYEDAŞ/BOĞAZİÇİ 3-way Istanbul enforcement
  * TEK → TEİAŞ/TEDAŞ/EÜAŞ/TETAŞ 2001 predecessor cascade
  * TEDAŞ → 21 privatized DSOs 2013 predecessor cascade
  * BOTAŞ + TCDD cross-sector Layer 2 catchment
  * Akkuyu nuclear Layer 4b generation carve-out
  * 21 privatized DSO Turkish diacritic + English + Ottoman variants

Convention #78 §4bis.5 Layer 3 8TH ENFORCEMENT:
- Istanbul metropolitan 3-way BEDAŞ + AYEDAŞ + BOĞAZİÇİ + Bosphorus
  strait carve-out. Anticipated LARGEST cohort-wide hit count
  (7.5M customer base vs Denmark 615 HIGHEST).
- Cumulative enforcement grows to 8:
  1. Prague CZ (Czechia P20)
  2. Warsaw PL (Poland P21)
  3. EWZ Zurich CH (Switzerland P24)
  4. SIG Geneva CH (Switzerland P24)
  5. Auckland NZ (New Zealand P27)
  6. Copenhagen DK (Denmark P28 — 615 HIGHEST hits)
  7. Helsinki FI (Finland P29 — 446 2nd cohort-wide)
  8. NEW: Istanbul TR (Turkey P30 — anticipated LARGEST)

Discipline #36 cross-border filter:
- 5.0 km tolerance (NEW turkey entry) per Aegean archipelago +
  Alpine ridge complexity + Bosphorus HV crossing precedent.
- 7 cross-border interconnectors preserved (2 ENTSO-E synchronous
  + 3 asynchronous DC block + 1 sealed + 1 curtailed).

Author: ikenga-ssi-foundation
Date: 18 July 2026
"""
