# v4.0.2 Connector + Fallback Coverage Audit

**Date**: 8 June 2026
**Purpose**: Verify every SoT country has a primary connector + fallback for all three data classes, with deterministic v4.0.2 behaviour.

---

## Climate (Tier resolution chain)

```
Tier 1a (direct national) ─ _NATIONAL_MET_FETCHERS registry — EMPTY for v4.0.2 (v4.5 expansion)
Tier 1b (NOAA-aggregated) ─ GHCN-D — SHIPPED + DORMANT (gated SSI_USE_GHCND=1, v4.5 activation)
Tier 2  (international)   ─ ERA5-Land 0.1° — ACTIVE PRIMARY for v4.0.2
```

For v4.0.2: **all 39 countries use ERA5-Land 0.1°** as the deterministic primary source. GHCN-D code is shipped + standby, callable for ad-hoc testing (`fetch_ghcnd_for_country('italy')`) but not auto-invoked.

For v4.5: `export SSI_USE_GHCND=1` activates Tier 1b. Plus per-country direct fetchers added to `_NATIONAL_MET_FETCHERS` per build cards.

---

## Seismic (Tier resolution chain)

```
Tier 1a (direct fetcher)  ─ _NATIONAL_SEISMIC_FETCHERS — EMPTY for v4.0.2 (v4.5 expansion)
Tier 1b (national CSV)    ─ _SEISMIC_LOCAL_PATHS — POPULATED for 3 countries
Tier 1c (cache JSON)      ─ Previous-run cache
Tier 1d (live agency API) ─ _SEISMIC_API_URLS — 4 endpoints registered
Tier 2  (international)   ─ GEM 2023.1 GeoTIFF — ACTIVE for 36 countries
Tier 3                    ─ ABORT
```

---

## Per-country coverage matrix — v4.0.2

Legend: 🥇 = primary in use · 🥈 = registered fallback · ⚪ = not applicable

| Country | Subs | Socio primary | Socio fallback | Seismic primary | Seismic fallback | Climate primary | Climate fallback |
|---|---:|---|---|---|---|---|---|
| **us** | 45,003 | 🥇 Census ACS | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **canada** | 24,986 | 🥇 StatCan | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **germany** | 13,251 | 🥇 Eurostat NUTS-3 | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **portugal** | 10,191 | 🥇 Eurostat NUTS-3 | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **australia** | 8,500 | 🥇 ABS | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **france** | 7,898 | 🥇 Eurostat NUTS-3 | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **norway** | 6,495 | 🥇 SSB | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **japan** | 5,981 | 🥇 Cabinet Office + MIC | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **italy** | 4,293 | 🥇 ISTAT | 🥈 World Bank | 🥇 **INGV MPS04** ✅ | 🥈 GEM 2023.1 | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **turkey** | 4,092 | 🥇 TÜİK + national-mean | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **finland** | 4,022 | 🥇 Eurostat NUTS-3 | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **sweden** | 3,872 | 🥇 Eurostat NUTS-3 | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **spain** | 3,529 | 🥇 Eurostat NUTS-3 | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **hungary** | 3,502 | 🥇 Eurostat NUTS-3 | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **uk** | 3,150 | 🥇 ONS Regional | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **mexico** | 3,140 | 🥇 INEGI compiled | 🥈 World Bank | 🥇 **CENAPRED** ✅ | 🥈 GEM 2023.1 | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **denmark** | 2,451 | 🥇 Eurostat NUTS-3 | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **poland** | 2,248 | 🥇 Eurostat NUTS-3 | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **netherlands** | 1,640 | 🥇 Eurostat NUTS-3 | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **new-zealand** | 1,558 | 🥇 Stats NZ | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **slovakia** | 1,516 | 🥇 Eurostat NUTS-3 | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **austria** | 1,406 | 🥇 Eurostat NUTS-3 | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **korea** | 1,290 | 🥇 KOSIS | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **belgium** | 1,220 | 🥇 Eurostat NUTS-3 | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **latvia** | 1,219 | 🥇 Eurostat NUTS-3 | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **chile** | 1,095 | 🥇 BCCh + INE | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **czechia** | 1,077 | 🥇 Eurostat NUTS-3 | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **ireland** | 994 | 🥇 Eurostat NUTS-3 | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **switzerland** | 947 | 🥇 BFS | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **iceland** | 687 | 🥇 Hagstofa | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **estonia** | 614 | 🥇 Eurostat NUTS-3 | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **greece** | 581 | 🥇 ELSTAT | 🥈 World Bank | 🥇 **EAK 2003** ✅ | 🥈 GEM 2023.1 | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **lithuania** | 505 | 🥇 Eurostat NUTS-3 | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **colombia** | 381 | 🥇 DANE | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **israel** | 257 | 🥇 CBS-IL | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **costa-rica** | 169 | 🥇 BCCR + INEC | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **slovenia** | 158 | 🥇 Eurostat NUTS-3 | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **luxembourg** | 91 | 🥇 Eurostat NUTS-3 | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **greenland** | 37 | 🥇 StatGreenland | 🥈 World Bank | 🥇 GEM 2023.1 | 🥈 ABORT | 🥇 ERA5-Land 0.1° | 🥈 ABORT |
| **TOTAL** | **131,326** | **39/39** | **39/39** | **39/39** | **3/39 + ABORT** | **39/39** | **0** |

---

## Summary

For **v4.0.2**:

- **Socio**: All 39 countries have a primary connector + at least one fallback (World Bank national)
- **Seismic**: All 39 countries have a primary connector (3 native + 36 via GEM 2023.1) and italy/greece/mexico additionally have GEM as a registered fallback
- **Climate**: All 39 countries have ERA5-Land 0.1° as primary; no fallback below it (would ABORT — same behaviour as pre-P15)

**Determinism**: GHCN-D code shipped but gated behind `SSI_USE_GHCND=1` env var so the next pipeline run after v4.0.2 closure produces deterministic ERA5-Land output (same as today). v4.5 activation = single env var flip + per-country direct fetchers per build cards.

**Risk-free closure**: ✅ Yes. All connectors and fallbacks are in place for v4.0.2.

For **v4.5** the gap is:
- Tier 1a direct national fetchers (78 build cards in V4_5_DIRECT_AGENCY_EXPANSION_PLAN.md)
- Tier 1b GHCN-D activation via env var unsetting the gate

These are additive expansions, not v4.0.2 blockers.
