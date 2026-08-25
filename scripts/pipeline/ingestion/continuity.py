"""Continuity of supply — the fourth ingestion DOMAIN (M-063, 20 August 2026).

Scaffold. No fetcher is implemented yet; this module establishes the registry,
the tier contract and the per-country source record so that populating it is
data entry rather than archaeology.

WHY THIS DOMAIN
───────────────
`C` carries the largest component weight in the index (0.30) and `V` (0.10) is
computed from SAIDI, so continuity data unlocks **31% of R_base** from one
domain — 40% once C3 and C4 arrive. Nothing else in the metric registry comes
close per unit of acquisition effort.

THE GRANULARITY CONSTRAINT — read this before sourcing anything
───────────────────────────────────────────────────────────────
Components normalise on a **per-country fleet percentile** (`norm_percentile`,
construct Method A/B). A national SAIDI figure therefore gives every substation
in that country the same raw value, P5 == P95, and the metric carries no
within-country information whatsoever.

`components.norm_percentile` returns **None** in that case rather than the
construct reference implementation's 0.5, so an all-national feed produces an
absent metric, not an inert constant — and the component then refuses to roll
up. That is deliberate: a constant masquerading as a measurement is the
`EV_load_ratio` defect (20% of T is inert for exactly this reason), and we do
not want to add C to that list.

**So: sub-national (per-DSO, per-region, or finer) or it does not help.**

TIER CONTRACT — mirrors the seismic chain (P15-B-4)
───────────────────────────────────────────────────
  1a  national regulator fetcher      — per-DSO/region, machine-readable
  1b  committed national CSV          — operator-populated, under
                                        scripts/pipeline/data/<country>/
  1c  cache JSON                      — previous run
  1d  live agency API                 — where one exists
  2   international fallback          — see NOTE_ON_CEER below: there is
                                        currently NO usable one

NOTE_ON_CEER
────────────
The obvious international fallback — the CEER/ECRB Benchmarking Report on the
Quality of Electricity and Gas Supply — is **not usable as a scoring input**.
The 7th edition (Dec 2022) is the latest; its continuity series runs 2010–2018,
it is national-only, and it ships as a PDF with no machine-readable annex. It
remains useful as a cross-check on national means and nothing more. This domain
therefore has no Tier 2, which is itself a finding: unlike climate and seismic,
continuity cannot fall back to a universal international layer.
"""

from __future__ import annotations

#: Per-country continuity source record.
#:
#: `granularity` is the field that decides whether a source is usable:
#:   per_dso / per_region / per_nuts3  → usable
#:   national                          → NOT usable for within-country
#:                                       normalisation; recorded so nobody
#:                                       re-researches it
#:   none_found / not_published        → honest absence
#:   unconfirmed                       → needs a manual pass; do not assume
#:                                       either way
#:
#: Compiled 20 August 2026. Verify before ingesting — regulator publication
#: patterns change, and several entries below are explicitly unconfirmed.
CONTINUITY_SOURCES = {
    # ── Tier 1a candidates: sub-national, machine-readable ──
    "germany": {"publisher": "BNetzA", "dataset": "Einzelstörungsdaten Strom",
                "metrics": ["incident-level duration", "planned/unplanned", "voltage level",
                            "affected customers"],
                "granularity": "per_dso", "note": "782 pseudonymous operator IDs, ~165k incident "
                "rows for 2024; SAIDI/SAIFI computable per operator. Operator IDs are NOT "
                "geocoded — pair with the 16-Bundesland SAIDI table for geography.",
                "vintage": "2024", "format": "xlsx", "status": "candidate"},
    "uk": {"publisher": "Ofgem", "dataset": "RIIO-2 ED Annual Report supplementary datafile",
           "metrics": ["CI (interruptions/100 customers)", "CML (customer minutes lost)",
                       "planned/unplanned"],
           "granularity": "per_dso", "note": "14 DNO licence areas. CI/CML rather than "
           "SAIDI/SAIFI — a nomenclature bridge is required (playbook §5).",
           "vintage": "RY2024-25", "format": "xlsm", "status": "candidate"},
    "italy": {"publisher": "ARERA", "dataset": "Prestazioni delle imprese distributrici — continuità",
              "metrics": ["duration/LV user", "unplanned count/LV user", "MV voltage dips"],
              "granularity": "per_region", "note": "Per distributor and per density band "
              "(alta/media/bassa concentrazione), with regional disaggregation above 25k users. "
              "Latest year PDF-only; 2013–2023 available as XLSX. Declared LIVE in the v4.0 "
              "Italy data architecture and never built.",
              "vintage": "2024", "format": "pdf (xlsx for history)", "status": "candidate"},
    "norway": {"publisher": "RME / NVE", "dataset": "Avbrotsstatistikk",
               "metrics": ["interruptions", "planned disconnections", "ILE/KILE"],
               "granularity": "per_region", "note": "Per nettselskap AND per fylke AND per "
               "consumer group — the only source found giving operator × region together. "
               "Extraction is the obstacle (interactive tables).",
               "vintage": "2025", "format": "interactive", "status": "candidate"},
    "portugal": {"publisher": "ERSE", "dataset": "Relatório da Qualidade de Serviço Técnica",
                 "metrics": ["SAIDI", "SAIFI", "END", "TIEPI", "MAIFI", "planned/unplanned",
                             "voltage dips"],
                 "granularity": "per_nuts3", "note": "Per operator AND NUTS III for the "
                 "mainland, per island for Azores/Madeira. Exactly the target granularity.",
                 "vintage": "2024", "format": "pdf", "status": "candidate"},
    "sweden": {"publisher": "Energimarknadsinspektionen (Ei)", "dataset": "Leveranssäkerhet i Sveriges elnät",
               "metrics": ["SAIDI", "SAIFI"], "granularity": "per_dso",
               "note": "~148–168 elnätsbolag, 2010–2024. Excel indicated but NOT first-hand "
               "confirmed (ei.se blocks automated fetch) — verify manually.",
               "vintage": "2024", "format": "xlsx (unconfirmed)", "status": "candidate"},
    "slovenia": {"publisher": "AGEN-RS", "dataset": "Poročilo o kakovosti oskrbe",
                 "metrics": ["SAIDI", "SAIFI", "planned/unplanned", "MV voltage quality"],
                 "granularity": "per_dso", "note": "All 5 distribution companies, mapping 1:1 "
                 "onto regions. Small fleet but complete.",
                 "vintage": "2023", "format": "pdf", "status": "candidate"},
    "spain": {"publisher": "MITECO / CNMC", "dataset": "Índices de calidad zonal (CEL)",
              "metrics": ["TIEPI", "NIEPI"], "granularity": "per_region",
              "note": "Per province, per comunidad autónoma, and per zone type "
              "(urbana/semiurbana/rural concentrada/rural dispersa). Delivery via the CEL web "
              "app; vintage and export format UNCONFIRMED.",
              "vintage": "unconfirmed", "format": "web app", "status": "needs_verification"},
    "switzerland": {"publisher": "ElCom", "dataset": "Stromversorgungsqualität",
                    "metrics": ["SAIDI", "SAIFI", "planned/unplanned"], "granularity": "per_dso",
                    "note": "90 largest operators plus four settlement-density network classes. "
                    "PDF-only; whether operators are NAMED is unconfirmed — that decides "
                    "whether the data can be joined to territory.",
                    "vintage": "2024", "format": "pdf", "status": "needs_verification"},
    "austria": {"publisher": "E-Control", "dataset": "Ausfall- und Störungsstatistik Strom",
                "metrics": ["SAIDI", "SAIFI", "ASIDI", "ASIFI", "planned/unplanned"],
                "granularity": "per_dso", "note": "Charts are 'je Netzbetreiber' but operators "
                "are not named in captions and there is no Bundesland breakdown — "
                "identifiability UNCONFIRMED.",
                "vintage": "2024", "format": "pdf", "status": "needs_verification"},
    "netherlands": {"publisher": "ACM", "dataset": "Dashboard Kwaliteit netbeheerders",
                    "metrics": ["reliability indicators"], "granularity": "per_dso",
                    "note": "Dashboard exposes individual regional netbeheerders; whether "
                    "interruption duration/frequency specifically is included is UNCONFIRMED. "
                    "The Netbeheer Nederland report is national-only.",
                    "vintage": "annual", "format": "tableau", "status": "needs_verification"},
    "poland": {"publisher": "individual OSDs (URE methodology)", "dataset": "per-operator SAIDI/SAIFI/MAIFI",
               "metrics": ["SAIDI", "SAIFI", "MAIFI", "planned/unplanned", "rural/urban (some)"],
               "granularity": "per_dso", "note": "Five large operators publish individually; NO "
               "consolidated URE dataset found. Scattered across operator websites.",
               "vintage": "2024/2025", "format": "html/pdf", "status": "candidate"},

    # ── National-only: recorded so nobody re-researches them ──
    "france": {"publisher": "Enedis / CRE", "dataset": "Durée moyenne de coupure (critère B)",
               "metrics": ["critère B"], "granularity": "national",
               "note": "Enedis open data is a national annual series. CRE's TURPE 7 audit works "
               "at Direction Régionale level and explicitly does not disclose below it. ~160 "
               "ELDs publish individually with no central dataset. NOT usable as-is.",
               "vintage": "annual series", "format": "csv/api", "status": "national_only"},
    "czechia": {"publisher": "ERÚ", "dataset": "Roční zpráva o provozu ES ČR",
                "metrics": ["SAIDI", "SAIFI", "CAIDI"], "granularity": "national",
                "note": "XLSX parsed directly: continuity tables carry no per-distributor or "
                "per-kraj dimension.", "vintage": "2024", "format": "xlsx", "status": "national_only"},
    "denmark": {"publisher": "Green Power Denmark (ELFAS)", "dataset": "Leveringssikkerhed",
                "metrics": ["SAIDI", "SAIFI", "CAIDI", "ASAI"], "granularity": "national",
                "note": "Aggregated by voltage level and event type; the ~22 reporting "
                "netselskaber are listed but their individual indicators are not published.",
                "vintage": "2024", "format": "pdf", "status": "national_only"},
    "ireland": {"publisher": "ESB Networks / CRU", "dataset": "Distribution Annual Performance Report",
                "metrics": ["CI", "CML", "planned/unplanned", "storm/non-storm"],
                "granularity": "national", "note": "Report is explicit that there is no regional, "
                "county or network-area breakdown.", "vintage": "2024", "format": "pdf",
                "status": "national_only"},
    "estonia": {"publisher": "Konkurentsiamet", "dataset": "Aruanne elektri- ja gaasiturust",
                "metrics": ["SAIDI", "SAIFI"], "granularity": "national",
                "note": "Single dominant DSO (Elektrilevi); company-level ≈ national.",
                "vintage": "2024", "format": "pdf", "status": "national_only"},

    # ── Absent ──
    "luxembourg": {"publisher": "ILR", "dataset": "Benchmark Report", "metrics": [],
                   "granularity": "not_published",
                   "note": "The regulator publishes NO continuity indicators at all — not "
                   "per-DSO, not even national. Strongest negative finding of the sweep.",
                   "vintage": None, "format": None, "status": "absent"},
    "greece": {"publisher": "RAAEY / HEDNO (ΔΕΔΔΗΕ)", "dataset": None, "metrics": [],
               "granularity": "none_found", "note": "No sub-national continuity publication located.",
               "vintage": None, "format": None, "status": "absent"},
    "iceland": {"publisher": "Orkustofnun / Landsnet", "dataset": None, "metrics": [],
                "granularity": "none_found", "note": "No per-utility continuity dataset located.",
                "vintage": None, "format": None, "status": "absent"},
}

#: Countries with no entry above have not been researched. Listing them
#: explicitly beats an empty dict lookup returning "absent" — absence of
#: research is not absence of data (M-030: a guard that examined nothing
#: reports success).
UNRESEARCHED = [
    "australia", "belgium", "canada", "chile", "colombia", "costa-rica", "finland",
    "greenland", "hungary", "israel", "japan", "korea", "latvia", "lithuania",
    "mexico", "new-zealand", "slovakia", "turkey", "us",
]

USABLE_GRANULARITIES = {"per_dso", "per_region", "per_nuts3"}


def usable_sources():
    """Countries whose recorded source is sub-national enough to normalise."""
    return sorted(c for c, s in CONTINUITY_SOURCES.items()
                  if s["granularity"] in USABLE_GRANULARITIES)


def coverage_report():
    """Honest coverage summary — researched, usable, national-only, absent, unresearched."""
    by_status = {}
    for c, s in CONTINUITY_SOURCES.items():
        by_status.setdefault(s["status"], []).append(c)
    return {
        "researched": len(CONTINUITY_SOURCES),
        "unresearched": len(UNRESEARCHED),
        "total_countries": len(CONTINUITY_SOURCES) + len(UNRESEARCHED),
        "usable_granularity": usable_sources(),
        "by_status": {k: sorted(v) for k, v in sorted(by_status.items())},
        "has_international_fallback": False,
        "fallback_note": "CEER 7th edition is national-only and its series ends 2018 — "
                         "unusable as a scoring input. This domain has no Tier 2.",
    }


def fetch_continuity(country):
    """Not implemented — scaffold only.

    Deliberately raises rather than returning empty. A fetcher that returns
    nothing and lets the caller carry on is how M-030 happened: absence read
    as success.
    """
    raise NotImplementedError(
        f"continuity ingestion is not implemented for {country}. "
        f"CONTINUITY_SOURCES records the source, granularity and format; "
        f"Tier 1a fetchers are the next build step. See "
        f"SSI_DATA_SOURCE_RECORD.md and modification-log M-063."
    )
