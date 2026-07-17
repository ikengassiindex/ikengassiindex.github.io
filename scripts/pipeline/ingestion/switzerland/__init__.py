"""Switzerland v4.23 substation + power-line ingestion package.

Wave 3 Priority 24 (third Wave 3 country; smallest-first cadence
post-Iceland at 947 baseline subs).

Architecture (architecturally richest Wave 3 cohort country):
- Swissgrid AG federal TSO ≥220 kV (established 2006 via BFE
  unbundling per EU 3rd Package bilateral)
- 5 major cantonal DSOs: Axpo Grid + BKW Netzservice + CKW +
  Groupe E + Romande Energie
- 3 major metro DSO carve-outs: EWZ (Zürich Stadt) + SIG (Genève) +
  SIL (Lausanne) — analogous to Warsaw Innogy Stoen pattern
- ~600 municipal DSOs (LARGEST DSO fragmentation cohort-wide)
- 41 cross-border interconnectors (HIGHEST cohort-wide) — UCTE
  Continental Europe synchronous grid
- 26 cantons with independent energy policies
- Non-EU member (EFTA yes, EEA NO — bilateral EU relationship)

Convention #78 BINDING 6th enforcement:
- 4-language script cohabitation (German + French + Italian + Romansh)
  — FIRST Wave 3 4-language country cohort-wide
- Trilingual legal forms: AG (Aktiengesellschaft) / SA (Société
  anonyme) / SpA (Società per azioni)
- Predecessor rebrand cascades:
  * NOK → Axpo Grid (2001 — 25-year legacy LARGEST)
  * Bernische Kraftwerke → BKW (2013)
  * EEF → Groupe E (2006)
  * EOS → Romande Energie (2007)
  * Rätia Energie → Repower (2007)

Convention #78 §4bis.5 Layer 3 geofence × 3 metro carve-outs:
- Zürich Stadt (EWZ metropolitan carve-out from Axpo Grid canton)
- Genève (SIG carve-out from Romande Energie canton)
- Lausanne (SIL carve-out from Romande Energie canton)
- Cumulative enforcement count could jump 2 → 4-5 (Prague +
  Warsaw + Swiss trio)

Author: ikenga-ssi-foundation
Date: 17 July 2026
"""
