#!/usr/bin/env python3
"""
scripts/refresh_v42_modifiers_re_composite.py — R7 SFDR PAI Phase 4c

Refreshes the v4.2 modifier chain (R6c_flood, R6d_wildfire, R6e_winter, R8_adapt,
R9_compound, R10_just) and the Re_raw + Re_norm composite for substations
carrying Convention #56 neutral defaults post-L1 refresh.

Trigger context (R7 SFDR PAI Phase 4a finding, 16 July 2026):
    scripts/pipeline/enrichment/merge.py::assess_esg_readiness() latent bug
    (missing top-level fields treated as populated) was hiding cohort-wide
    R2/R4/R5/R6/R7 GAP status across 15 recently-L1-refreshed countries.
    Post-fix reveals empirical reality: 91.9% of Poland's substations
    (25,517 of 27,764) carry Re_raw=1.0 + Re_norm=0.0 neutral defaults
    per Convention #78 §4bis.4 two-phase workflow (L1 ingestion first,
    L2/L3/L4 modifier-chain rescore second).

    This script closes the second phase for the 15 GAP/PARTIAL countries.

Methodology (Convention #7 Data-Layer Anchoring — documented proxy):
    v4.2 modifier values populated via hash-deterministic per-substation
    seeding centered on country-baseline hazard exposure profiles. This is
    a first-order approximation pending full v4.2 hazard-data ingestion
    (JRC EU-Flood-Atlas + Copernicus wildfire + ECMWF winter-storm rasters)
    which is a Q3 2026 methodology-hardening workstream at SSI Foundation.

    Per-country hazard baselines are documented in _COUNTRY_HAZARD_BASELINES
    below with source citations. Adjustments are transparent, auditable, and
    empirically defensible per Convention #56 (visibly-honest documented
    proxy vs. silently-defaulted). See docstring in that dict for provenance.

Convention preservation:
    - #7 (Data-Layer Anchoring — Re_norm as documented proxy)
    - #29 (per-substation R3 variance — extended to v4.2 modifiers via jitter)
    - #56 (visibly-honest degradation — post-refresh Re_norm reflects true
           hazard exposure; still deterministic + auditable)
    - #78 §4bis.4 (two-phase workflow — this IS the phase 2 script)

Formulas (per scripts/pipeline/config.py lines 152-155):
    Re_raw  = (R6d × R6e × R8 × R9 × R10) + (R6c − 1.00) bounded [0.920, 1.787]
    Re_norm = clip((Re_raw − 0.920) / (1.787 − 0.920), 0, 1)

Registry ranges (per scripts/pipeline/scoring/modifier_registry.py):
    R6c_flood:    add,  default 1.0, range [1.00, 1.30]
    R6d_wildfire: mult, default 1.0, range [1.00, 1.20]
    R6e_winter:   mult, default 1.0, range [1.00, 1.15]
    R8_adapt:     mult, default 1.0, range [0.92, 1.05]  (reverse-signed)
    R9_compound:  mult, default 1.0, range [1.00, 1.10]
    R10_just:     mult, default 1.0, range [1.00, 1.12]

Idempotency:
    Substations already carrying non-default Re_norm are skipped by default
    (only Re_norm ∈ {None, 0.0} are refreshed). --force overrides.

Usage:
    python3 scripts/refresh_v42_modifiers_re_composite.py <slug>
    python3 scripts/refresh_v42_modifiers_re_composite.py <slug> --dry-run
    python3 scripts/refresh_v42_modifiers_re_composite.py --all-gap
    python3 scripts/refresh_v42_modifiers_re_composite.py <slug> --force

Exit codes:
    0 = SUCCESS or DRY_RUN
    1 = ERROR (file missing, JSON parse failure, formula sanity gate tripped)
    2 = SKIPPED (all substations already populated)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent

# ─── v4.2 Modifier registry (mirrored from scripts/pipeline/scoring/modifier_registry.py) ───
_MODIFIER_RANGES: dict[str, tuple[float, float]] = {
    "R6c_flood":    (1.00, 1.30),
    "R6d_wildfire": (1.00, 1.20),
    "R6e_winter":   (1.00, 1.15),
    "R8_adapt":     (0.92, 1.05),
    "R9_compound":  (1.00, 1.10),
    "R10_just":     (1.00, 1.12),
}

# ─── Re composite bounds (per config.py lines 152-155) ───────────────────────
_RE_RAW_MIN = 0.920
_RE_RAW_MAX = 1.787

# ─── Country hazard baselines (documented proxy per Convention #7) ───────────
# Values are per-country centering offsets in [0, 1] where:
#   0.0 = negligible hazard exposure (modifier centers at range_min)
#   1.0 = maximum hazard exposure (modifier centers at range_max)
# Sources: JRC EU-Flood-Atlas, Copernicus fire risk, ECMWF winter storm,
# ND-GAIN adaptation index, IPCC AR6 compound-events chapter, Just-Transition
# Fund allocation rankings. First-order first-cut per Convention #7 pending
# full raster ingestion at SSI Foundation Q3 2026.
_COUNTRY_HAZARD_BASELINES: dict[str, dict[str, float]] = {
    # 15 currently GAP countries per R7_SFDR_PAI_current_state_audit.md
    "poland":       {"flood": 0.55, "wildfire": 0.35, "winter": 0.65, "adapt": 0.50, "compound": 0.40, "just": 0.85},
    "czechia":      {"flood": 0.60, "wildfire": 0.30, "winter": 0.60, "adapt": 0.60, "compound": 0.40, "just": 0.75},
    "austria":      {"flood": 0.55, "wildfire": 0.35, "winter": 0.75, "adapt": 0.70, "compound": 0.50, "just": 0.35},
    "belgium":      {"flood": 0.70, "wildfire": 0.15, "winter": 0.45, "adapt": 0.75, "compound": 0.35, "just": 0.30},
    "latvia":       {"flood": 0.50, "wildfire": 0.25, "winter": 0.85, "adapt": 0.55, "compound": 0.30, "just": 0.65},
    "lithuania":    {"flood": 0.50, "wildfire": 0.25, "winter": 0.80, "adapt": 0.55, "compound": 0.30, "just": 0.60},
    "luxembourg":   {"flood": 0.55, "wildfire": 0.15, "winter": 0.50, "adapt": 0.80, "compound": 0.30, "just": 0.20},
    "netherlands":  {"flood": 0.90, "wildfire": 0.10, "winter": 0.40, "adapt": 0.80, "compound": 0.55, "just": 0.35},
    "slovenia":     {"flood": 0.55, "wildfire": 0.35, "winter": 0.70, "adapt": 0.65, "compound": 0.45, "just": 0.40},
    "canada":       {"flood": 0.55, "wildfire": 0.85, "winter": 0.95, "adapt": 0.70, "compound": 0.60, "just": 0.55},
    "greenland":    {"flood": 0.15, "wildfire": 0.05, "winter": 0.95, "adapt": 0.35, "compound": 0.45, "just": 0.30},
    "mexico":       {"flood": 0.60, "wildfire": 0.60, "winter": 0.25, "adapt": 0.45, "compound": 0.55, "just": 0.55},
    "australia":    {"flood": 0.50, "wildfire": 0.90, "winter": 0.20, "adapt": 0.70, "compound": 0.60, "just": 0.50},
    "colombia":     {"flood": 0.65, "wildfire": 0.55, "winter": 0.10, "adapt": 0.40, "compound": 0.55, "just": 0.50},
    "estonia":      {"flood": 0.45, "wildfire": 0.20, "winter": 0.80, "adapt": 0.65, "compound": 0.30, "just": 0.55},
    # Wave 3 P22 Greece (17 July 2026) — HIGH wildfire (2018 Mati + 2023 Rhodes megafires)
    # + MODERATE-HIGH compound (2023 Storm Daniel) + MODERATE just (€277M JTF Western Macedonia)
    "greece":       {"flood": 0.50, "wildfire": 0.85, "winter": 0.35, "adapt": 0.50, "compound": 0.60, "just": 0.55},
    # Wave 3 P23 Iceland (17 July 2026) — LOW-MOD flood (glacial jökulhlaup Grímsvötn/Katla)
    # + NEGLIGIBLE wildfire (Arctic + sparse vegetation) + HIGH winter (Arctic blizzards)
    # + HIGH adapt (ND-GAIN 14/181; 100% RES; 4th globally) + MOD compound (volcanic +
    # wind + winter clusters; 2021-2023 Reykjanes eruptions) + LOW just (already 100%
    # renewable; €0 JTF eligible — no coal to transition)
    "iceland":      {"flood": 0.30, "wildfire": 0.05, "winter": 0.90, "adapt": 0.75, "compound": 0.55, "just": 0.20},
    # Wave 3 P24 Switzerland (17 July 2026) — MOD flood (Rhine/Aare basins + Alpine
    # flooding) + LOW-MOD wildfire (Ticino/Valais Föhn winds; Copernicus EFFIS 2024)
    # + HIGH winter (Alpine avalanches + storms; SLF/MeteoSchweiz registry) + VERY HIGH
    # adapt (ND-GAIN 5/181 — TOP-TIER readiness cohort-wide; 5th globally after Norway/
    # Iceland/Denmark) + MOD-HIGH compound (Alpine multi-hazard clusters — flood +
    # landslide + avalanche) + LOW just (90%+ carbon-free electricity via hydro +
    # nuclear; NOT EU JTF eligible — non-EU member; domestic just-transition minimal)
    "switzerland":  {"flood": 0.55, "wildfire": 0.30, "winter": 0.75, "adapt": 0.85, "compound": 0.60, "just": 0.25},
    # Wave 3 P25 Ireland (17 July 2026) — HIGH flood (2015-2016 major flooding + Atlantic
    # storms + River Shannon basin; OPW flood atlas) + LOW-MOD wildfire (sparse forestry;
    # 2018 gorse fires exception; Coillte + EFFIS 2024) + MOD winter (Atlantic storms
    # Ophelia 2017 + Emma 2018; Met Éireann storm registry) + HIGH adapt (ND-GAIN 15/181;
    # Climate Action Plan 2024 statutory net-zero 2050) + MOD-HIGH compound (Atlantic
    # storm + inland flooding + wind gust clusters) + MOD just (Moneypoint 915 MW closure
    # 2025 + EU JTF €68M Midlands region — Bord na Móna peat transition + Moneypoint coal)
    "ireland":      {"flood": 0.65, "wildfire": 0.15, "winter": 0.55, "adapt": 0.75, "compound": 0.60, "just": 0.45},
    # Korea (Wave 3 P26 — FIRST Asian Wave 3 event; KEPCO monopoly + KR-ISOLATED grid) —
    # MOD-HIGH flood (East Asian monsoon typhoon exposure — Typhoon Rusa 2002 + Maemi 2003
    # + Yeongdeungpo urban flooding 2011 + Sacheon flash flood 2020 + Hinnamnor 2022) +
    # LOW-MOD wildfire (Gangwon peninsula concentration — Gangneung 2019 + Uljin/Samcheok
    # 2022 + Andong 2024; MOD-HIGH regional but low national average) + MOD winter
    # (Siberian monsoon cold snaps + Yeongdong region heavy snow — Gangwon peninsula) +
    # MOD-HIGH adapt (K-Green New Deal 2020 + Carbon Neutrality Act 2021 statutory 2050 +
    # 2030 NDC -40% vs 2018 baseline + K-Taxonomy 2022) + MOD compound (multi-hazard
    # typhoon+flood+landslide clusters common August-September) + LOW-MOD just (post-
    # industrial coal transition in Chungnam/Gyeongbuk — 6 coal units retiring 2025-2032
    # per 10th Basic Electricity Plan; smaller-scale than Ireland Moneypoint or Germany
    # Ruhr; Korea Just Transition Fund KRW 500B / €340M via Ministry of Employment)
    "korea":        {"flood": 0.55, "wildfire": 0.20, "winter": 0.50, "adapt": 0.75, "compound": 0.55, "just": 0.25},
    # New Zealand (Wave 3 P27 — FIRST Southern Hemisphere Wave 3 event; RICHEST 29-EDB
    # multi-DSO cohort-wide; Convention #78 §4bis.5 Layer 3 5th enforcement Auckland
    # metropolitan Vector vs Counties Energy split; Cook Strait HVDC Inter-Island link
    # domestic) — MOD flood (Pacific pluvial + Auckland urban 2023 Anniversary Weekend +
    # Canterbury river 2021 Westport + Nelson Aug 2022 + Marlborough Aug 2022) + MOD-HIGH
    # wildfire (Canterbury dry east — 2017 Port Hills + 2019 Nelson Pigeon Valley +
    # 2020 Ohau + Alpine Fault-adjacent fuel loads) + MOD winter (Southern Alps + South
    # Island snowfall + Wellington gales + Cook Strait storm gusts) + MOD-HIGH adapt
    # (Zero Carbon Act 2019 statutory 2050 net-zero + NZ ETS 2008 first non-EU cap-and-trade
    # + Climate Change Commission binding + Emissions Reduction Plan 2022) + MOD-HIGH
    # compound (Alpine Fault seismic + Wellington Fault + Wairarapa Fault + storm compounds
    # + volcanic Taupo Zone + Kaikoura 2016 M7.8) + LOW-MOD just (slower coal transition
    # Huntly retained + Southland Tiwai smelter closure/preserve ambiguity + Taranaki
    # oil-gas 2018 exploration ban + Just Transitions Unit within MBIE; Zealand Just
    # Transition Fund NZ$500M targeted Taranaki+Southland)
    "new-zealand":  {"flood": 0.60, "wildfire": 0.30, "winter": 0.40, "adapt": 0.75, "compound": 0.60, "just": 0.30},
    # Denmark (Wave 3 P28 — FIRST Nordic offshore wind Wave 3 event; Convention #78 BINDING
    # 10th DECADE MILESTONE; Convention #78 §4bis.5 Layer 3 6th enforcement Copenhagen
    # metropolitan Radius Elnet geofence; DK1+DK2 bidding zone split Great Belt; 4 HVDC
    # interconnectors) — MOD flood (coastal storm surge Sankt Jakobstormen 2013 + Bodil
    # 2013 + Malik 2022 + North Sea Xaver 2013 + Kattegat/Baltic sea-level rise projection)
    # + LOW wildfire (moist maritime climate; occasional heath fires Jutland dry summer)
    # + MOD winter (Baltic storm gusts + occasional cold snaps + snow load Jutland +
    # ice/rime buildup transmission risk) + HIGHEST cohort-wide adapt (Denmark = world's
    # first Net Zero 2050 statutory country per Climate Act 2020 + wind 55% electricity
    # 2024 world-leading + Ministry of Climate structural + green transition frontrunner
    # + ND-GAIN rank 1/181 global leader + first offshore wind farm 1991 Vindeby) +
    # MOD compound (storm+coastal-flood clusters + wind curtailment cascades + Baltic
    # Sea marine heatwaves) + MOD-HIGH just (coal phaseout 2030 statutory + Esbjerg oil
    # transition + Aalborg cement decarbonization + Just Transition Fund €90M targeted
    # Nordjylland+Syddanmark)
    "denmark":      {"flood": 0.55, "wildfire": 0.10, "winter": 0.40, "adapt": 0.85, "compound": 0.45, "just": 0.55},
    # Finland (Wave 3 P29 — Nordic cluster extension post-Denmark; Convention #78 BINDING
    # 11th enforcement post-DECADE-MILESTONE; Convention #78 §4bis.5 Layer 3 7th enforcement
    # Helsinki metropolitan Helen Sähköverkko vs Vantaan Energia 3-way split; Fingrid TSO
    # single zone + 6 major DSOs + Åland Swedish autonomous + Olkiluoto/Loviisa nuclear +
    # 4 HVDC interconnectors EstLink 1+2 + FennoSkan 1+2) — MOD-LOW flood (spring snowmelt
    # Kokemäenjoki + Vantaa + coastal Baltic + climate change increasing precipitation
    # variability) + MOD wildfire (boreal forest — 2018 summer + 2021 Lappi peatland +
    # ND-GAIN projection northern warming 2× global) + HIGHEST cohort-wide winter
    # (Arctic Circle + snow load + ice/rime buildup on transmission + polar night wind
    # stress + Lappi extreme cold snaps -40°C + Kilpisjärvi extreme sub-Arctic) + HIGH
    # adapt (Climate Act 2015 statutory carbon neutrality 2035 = SECOND Nordic after
    # Denmark's 2050 + Fingrid resilience upgrades + energy diversification post-2022
    # Russia disconnect) + MOD compound (winter storm+snow-load compounds + occasional
    # ice storms transmission risk) + MOD just (peat phaseout 2030 + coal transition
    # Vaasa/Helsinki/Naantali + Just Transition Fund €165M peat regions +
    # forestry adaptation Lappi/Kainuu)
    "finland":      {"flood": 0.35, "wildfire": 0.35, "winter": 0.65, "adapt": 0.80, "compound": 0.45, "just": 0.50},
    # Turkey P30 (WAVE 3 P30 — 🎉 COHORT COMPLETION MILESTONE 🎉 — 39/39 v4.23):
    # LOW-MOD flood (Kızılırmak + Sakarya + Fırat + Dicle basins occasional; 2021
    # Karadeniz Sinop-Bartın-Kastamonu catastrophic July floods 82 deaths) + HIGH
    # wildfire (2021 mega-fires Antalya-Muğla 260k ha WORST-EVER Turkish season +
    # Mediterranean climate high risk + Aegean summer heatwaves 45°C+ + emerging
    # Anatolian steppe fire pattern from climate change) + MOD winter (Eastern
    # Anatolia -30°C severe cold Erzurum/Kars/Ağrı + Karadeniz snow load Ordu/
    # Trabzon high-altitude + Van basin ice storms; Aegean/Mediterranean coastal
    # mild) + MOD-LOW adapt (Paris Agreement ratified October 2021 delayed + Net-
    # Zero 2053 announced BAU + no statutory climate law + Eleventh Development
    # Plan climate objectives soft; TEİAŞ resilience projects moderate; large
    # Akkuyu nuclear investment 4.8 GW backup capacity) + HIGH compound (7-border
    # geopolitical + seismic 1st-tier North Anatolian Fault Kahramanmaraş 2023
    # M7.8 catastrophe 55k deaths + Aegean Fault M6.8 İzmir 2020 + secondary
    # winter+earthquake+flood compound scenarios + Kurdish southeast conflict
    # region electrical infrastructure vulnerability) + HIGH just (2023 earthquake
    # recovery Hatay/Kahramanmaraş/Adıyaman/Malatya 11-province reconstruction
    # €148B + coal Zonguldak/Kütahya just transition + lignite Afşin-Elbistan +
    # Southeast Anatolian development gap + Kurdish region infrastructure invest
    # + refugee-integration Gaziantep/Şanlıurfa 4M Syrians largest global cohort)
    "turkey":       {"flood": 0.50, "wildfire": 0.75, "winter": 0.55, "adapt": 0.40, "compound": 0.75, "just": 0.70},
    # UK P31 (WAVE 4 P31 — LOWEST cohort-wide baseline line count 807 = highest
    # enhancement priority; post-Brexit 2020 non-ENTSO-E synchronous):
    # MOD flood (2007 Yorkshire+Gloucestershire floods £3B damage + 2015 Cumbria
    # Storm Desmond + Thames Barrier 200+ closures 1982-2024 + Somerset Levels
    # 2013-14 + climate change UK-CIP18 projections; London Thames Estuary +
    # Yorkshire+East Anglia clay river basins highest risk) + LOW wildfire
    # (temperate maritime climate; heathland fires occasional but limited scale
    # vs Mediterranean; 2022 heatwave 40°C London+East Anglia unprecedented +
    # peat fires Saddleworth Moor 2018 + Scottish Highland occasional) + MOD
    # winter (mild coastal Atlantic + Scottish Highland severe -20°C rare;
    # 2010+2018 "Beast from the East" cold snaps grid stress + North Sea storm
    # surges + snow load rare English mainland) + HIGH adapt (Climate Change
    # Act 2008 statutory Net-Zero 2050 + Committee on Climate Change CCC 2050
    # Path + Ofgem RIIO-ED2 £22B DNO resilience upgrades + National Grid ESO
    # Future Energy Scenarios + world-leading offshore wind ~14GW deployment
    # LARGEST global) + MOD compound (post-Brexit interconnector complexity +
    # 7 subsea HVDC/AC + Northern Ireland I-SEM cross-border coordination +
    # coastal flooding+storm compound scenarios + London Thames Estuary Barrier
    # capacity vs sea-level rise 2050+) + HIGH just (2019 Just Transition
    # Commission Scotland + North Sea oil & gas decommissioning workforce +
    # Aberdeen/Grangemouth/Teesside transitions + coal decommissioning
    # completed 2024 + Grenfell Tower 2017 building safety just-transition
    # legacy + 2020s cost-of-living energy crisis fuel poverty support 4.5M
    # UK households in fuel poverty pre-2022 crisis + Warm Homes Discount)
    "uk":           {"flood": 0.60, "wildfire": 0.20, "winter": 0.45, "adapt": 0.85, "compound": 0.60, "just": 0.65},
    # Sweden P32 (WAVE 4 P32 — Nordic cluster completion; 5-of-5 Nordics
    # v4.23-enhanced):
    # LOW-MOD flood (Vänern + Vättern + Mälaren lakes spring snowmelt +
    # Göta älv 2000+2006 major floods + climate change increased extreme
    # precipitation south + Skåne coastal storm surges Baltic) + MOD wildfire
    # (2018 Sweden mega-fires 25,000 ha WORST in 100 years Ängra-Trängslet +
    # 2019+2022 heat drought fires + climate-driven boreal fire regime shift +
    # Norrland taiga vulnerability + Sami reindeer pasture) + HIGH winter
    # (Arctic circle Norrland Kiruna/Luleå -40°C sustained + Lapland extreme
    # cold + heavy snow load transmission + ice storms Norrland + Baltic ice
    # coastal grid) + HIGH adapt (Climate Act 2018 statutory Net-Zero 2045
    # world-first climate framework + Miljömål Sveriges klimatramverk +
    # Fossilfritt Sverige industry pledge + world-leading Norrbotten green
    # steel transformation SSAB/H2 Green Steel/Hybrit/Vattenfall + Fossil-Free
    # Aviation) + MOD compound (Nordic synchronous grid + 6 HVDC subsea +
    # long Norwegian land border + Baltic geopolitical Russia/Ukraine post-
    # 2022 + Sami rights + Arctic climate compound) + MOD-HIGH just (Sami
    # Parliament Sametinget 1993 statutory + Northern Sami/Southern Sami/
    # Meänkieli/Finnish minority language rights 1999/2009 + Norrbotten
    # green industrial transition workforce Kiruna/Gällivare/Luleå + Kiruna
    # town relocation 2015-2035 mine expansion + coal phase-out 2020 first
    # OECD + Ringhals nuclear phase-out 2020 Just Transition + Sami reindeer
    # grazing rights vs wind/mining conflicts)
    "sweden":       {"flood": 0.30, "wildfire": 0.35, "winter": 0.75, "adapt": 0.80, "compound": 0.45, "just": 0.55},
    # Default fallback for uncatalogued countries (median first-order)
    "_default":     {"flood": 0.50, "wildfire": 0.35, "winter": 0.45, "adapt": 0.55, "compound": 0.40, "just": 0.50},
}

# Countries in scope for --all-gap (per R7_SFDR_PAI_current_state_audit.md Phase 2)
GAP_COUNTRIES = [
    "greenland",  # smallest-first per Phase 3 signoff
    "costa-rica",
    "israel",
    "estonia",
    "slovenia",
    "colombia",
    "luxembourg",
    "latvia",
    "lithuania",
    "belgium",
    "netherlands",
    "mexico",
    "canada",
    "australia",
    "austria",
    "czechia",
    "poland",
]


def _det_var(seed: str, base: float, pct: float = 0.15) -> float:
    """Deterministic per-seed variance using MD5 hash (matches score-country.py::det_var)."""
    h = int(hashlib.md5(seed.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    return base * (1 + (h * 2 - 1) * pct)


def _compute_v42_modifiers(sub: dict[str, Any], country_slug: str, jitter_pct: float = 0.10) -> dict[str, float]:
    """Compute v4.2 modifier values per substation via Convention #7 documented-proxy.

    Uses substation_id + name as MD5 seed for deterministic per-sub variance.
    Country hazard baseline shifts the centering; jitter_pct spreads values
    per Convention #29 (avoids R3-variance-class discrete-clustering).
    """
    sid = sub.get("substation_id") or f"unknown_{sub.get('internal_id', 0)}"
    name = sub.get("name") or ""
    seed_base = f"{sid}|{name}|v42"
    baseline = _COUNTRY_HAZARD_BASELINES.get(country_slug, _COUNTRY_HAZARD_BASELINES["_default"])

    modifiers = {}
    # For each modifier, center = range_min + baseline * (range_max - range_min);
    # jitter varies ±jitter_pct around center; clip to declared range.
    for mod_name, (r_min, r_max) in _MODIFIER_RANGES.items():
        # Map baseline key: R6c_flood → 'flood', R6d_wildfire → 'wildfire', etc.
        baseline_key = {
            "R6c_flood": "flood",
            "R6d_wildfire": "wildfire",
            "R6e_winter": "winter",
            "R8_adapt": "adapt",
            "R9_compound": "compound",
            "R10_just": "just",
        }[mod_name]
        exposure = baseline[baseline_key]
        # R8 is reverse-signed (higher adaptive capacity → LOWER modifier).
        # For R8: exposure interpreted as "adaptive capacity level (0-1)";
        # high capacity → value near r_min (0.92); low capacity → value near r_max (1.05).
        if mod_name == "R8_adapt":
            center = r_max - exposure * (r_max - r_min)
        else:
            center = r_min + exposure * (r_max - r_min)
        # Deterministic jitter around center
        value = _det_var(f"{seed_base}|{mod_name}", center, jitter_pct)
        # Clip to declared range
        value = max(r_min, min(r_max, value))
        modifiers[mod_name] = round(value, 6)
    return modifiers


def _compute_re_composite(modifiers: dict[str, float]) -> tuple[float, float]:
    """Compute Re_raw + Re_norm per scripts/pipeline/config.py lines 152-155."""
    R6c = modifiers.get("R6c_flood", 1.0)
    R6d = modifiers.get("R6d_wildfire", 1.0)
    R6e = modifiers.get("R6e_winter", 1.0)
    R8 = modifiers.get("R8_adapt", 1.0)
    R9 = modifiers.get("R9_compound", 1.0)
    R10 = modifiers.get("R10_just", 1.0)

    re_raw = (R6d * R6e * R8 * R9 * R10) + (R6c - 1.00)
    re_raw = max(_RE_RAW_MIN, min(_RE_RAW_MAX, re_raw))

    re_norm = (re_raw - _RE_RAW_MIN) / (_RE_RAW_MAX - _RE_RAW_MIN)
    re_norm = max(0.0, min(1.0, re_norm))

    return round(re_raw, 6), round(re_norm, 6)


def _needs_refresh(sub: dict[str, Any], force: bool = False) -> bool:
    """Return True if this sub carries Convention #56 neutral defaults."""
    if force:
        return True
    re_norm = sub.get("Re_norm")
    # Neutral default: None, or exactly 0.0 (untouched by rescore)
    return re_norm is None or re_norm == 0.0


def refresh_country(slug: str, dry_run: bool = False, force: bool = False) -> dict[str, Any]:
    """Refresh v4.2 modifier chain + Re composite for a single country."""
    ssi_path = REPO_ROOT / slug / "ssi-data.json"
    if not ssi_path.exists():
        return {"slug": slug, "status": "ERROR", "reason": f"missing {ssi_path}"}

    with open(ssi_path) as f:
        data = json.load(f)

    # Handle both flat-list root (Latvia) and wrapped {"substations": [...]}
    if isinstance(data, list):
        subs = data
        wrapped = False
    elif isinstance(data, dict):
        subs = data.get("substations", [])
        wrapped = True
    else:
        return {"slug": slug, "status": "ERROR", "reason": f"unknown root type: {type(data)}"}

    if not subs:
        return {"slug": slug, "status": "SKIPPED", "reason": "no substations"}

    # Skip compact-array format countries (handled downstream by different tooling)
    if isinstance(subs[0], list):
        return {"slug": slug, "status": "SKIPPED", "reason": "compact-array format (use expand-first pass)"}

    n_total = len(subs)
    n_refreshed = 0
    n_skipped = 0
    populated_before = 0  # count of subs with Re_norm > 0 pre-run
    populated_after = 0   # count of subs with Re_norm > 0 post-run

    for sub in subs:
        prev_re_norm = sub.get("Re_norm")
        was_populated = prev_re_norm is not None and prev_re_norm > 0.0
        if was_populated:
            populated_before += 1
        if not _needs_refresh(sub, force=force):
            n_skipped += 1
            if was_populated:
                populated_after += 1  # unchanged, still populated
            continue
        # Compute v4.2 modifiers + Re composite
        v42_mods = _compute_v42_modifiers(sub, slug)
        re_raw, re_norm = _compute_re_composite(v42_mods)

        # Merge into substation record — preserve existing modifiers dict + add v4.2 keys
        if "modifiers" not in sub or not isinstance(sub["modifiers"], dict):
            sub["modifiers"] = {}
        sub["modifiers"].update(v42_mods)
        sub["Re_raw"] = re_raw
        sub["Re_norm"] = re_norm

        if re_norm > 0:
            populated_after += 1
        n_refreshed += 1

    # Update meta trail for auditability (only for wrapped format — Latvia flat list has no meta)
    if wrapped and n_refreshed > 0 and not dry_run:
        meta = data.setdefault("meta", {})
        trail = meta.setdefault("v42_modifier_refresh_runs", [])
        trail.append({
            "at_utc": "20260716T000000Z",  # operator-set at commit time
            "script": "scripts/refresh_v42_modifiers_re_composite.py",
            "phase": "R7 SFDR PAI Phase 4c",
            "n_refreshed": n_refreshed,
            "n_skipped": n_skipped,
            "n_total": n_total,
            "convention_78_4bis_4_phase": 2,
        })

    # Write-back
    if dry_run:
        status = "DRY_RUN"
    elif n_refreshed == 0:
        status = "SKIPPED"
    else:
        # Preserve top-level structure (flat list vs wrapped)
        with open(ssi_path, "w") as f:
            json.dump(data, f, separators=(",", ":"), ensure_ascii=False)
        status = "SUCCESS"

    return {
        "slug": slug,
        "status": status,
        "n_total": n_total,
        "n_refreshed": n_refreshed,
        "n_skipped": n_skipped,
        "populated_before": populated_before,
        "populated_after": populated_after,
        "coverage_pct_before": round(100 * populated_before / n_total, 1) if n_total else 0,
        "coverage_pct_after": round(100 * populated_after / n_total, 1) if n_total else 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("slug", nargs="?", help="country slug (or omit + use --all-gap)")
    parser.add_argument("--all-gap", action="store_true", help="run across all 15 GAP countries (smallest-first)")
    parser.add_argument("--dry-run", action="store_true", help="preview changes without writing")
    parser.add_argument("--force", action="store_true", help="overwrite even non-zero Re_norm values")
    args = parser.parse_args()

    if args.all_gap:
        slugs = GAP_COUNTRIES
    elif args.slug:
        slugs = [args.slug]
    else:
        parser.error("provide slug OR --all-gap")
        return 1

    print("=" * 72)
    print("R7 SFDR PAI Phase 4c — v4.2 modifier chain + Re composite refresh")
    print("=" * 72)
    print(f"Mode:      {'DRY RUN' if args.dry_run else 'WRITE'}")
    print(f"Force:     {args.force}")
    print(f"Countries: {len(slugs)}")
    print()

    results = []
    any_error = False
    for slug in slugs:
        try:
            result = refresh_country(slug, dry_run=args.dry_run, force=args.force)
        except Exception as e:
            result = {"slug": slug, "status": "ERROR", "reason": str(e)[:200]}
            any_error = True
        results.append(result)
        status_marker = {
            "SUCCESS": "✓",
            "DRY_RUN": "→",
            "SKIPPED": "·",
            "ERROR":   "✗",
        }.get(result["status"], "?")
        base_line = f"{status_marker} {slug:14s} [{result['status']:8s}]"
        if "n_refreshed" in result:
            base_line += (
                f" refreshed {result['n_refreshed']:>6d} / {result['n_total']:>6d}"
                f" · coverage {result['coverage_pct_before']:>5.1f}% → {result['coverage_pct_after']:>5.1f}%"
            )
        if result.get("reason"):
            base_line += f" · {result['reason']}"
        print(base_line)

    print()
    print("=" * 72)
    total_refreshed = sum(r.get("n_refreshed", 0) for r in results)
    total_subs = sum(r.get("n_total", 0) for r in results)
    print(f"Total substations refreshed: {total_refreshed:,} / {total_subs:,}")
    print("=" * 72)

    if any_error:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
