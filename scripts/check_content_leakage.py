#!/usr/bin/env python3
"""
check_content_leakage.py — Discipline #21 (post-CR S33 audit finding).

Detects cross-country content contamination in country-specific files:
  <slug>/ssi-metadata.js
  <slug>/{index,intelligence,regional,map,data,methodology,esg-report,dno-dashboard}.html

ROOT CAUSE: clone-from-template (Discipline #16) catches HTML structure but
NOT prose narrative. When iceland/ was cloned to costa-rica/ via regex
substitution, the upstream Iceland-specific narrative passed through —
PLUS the Hungary content that was already contaminating Iceland's own pages.

DETECTION: each country has a fingerprint vocabulary of proper nouns that
should only appear in that country's own files (place names, TSO names,
language-specific terms). If country X's files contain ≥THRESHOLD hits from
country Y's vocabulary, that's a content-leakage regression.

Pattern: A1c-at-content-layer sub-pattern (distinct from A1c-at-DOM-hooks).

Usage:
  python3 scripts/check_content_leakage.py             # sweep all countries
  python3 scripts/check_content_leakage.py <slug>      # one country
  python3 scripts/check_content_leakage.py --strict    # exit 1 on any leakage
  python3 scripts/check_content_leakage.py --vocab     # print vocab dict
"""
import re
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

REPO_ROOT = Path(__file__).resolve().parent.parent
THRESHOLD = 5  # hits from other-country vocab = FAIL

# ─── Country-specific fingerprint vocabularies (D#21 v2 — major tune 2026-05-29) ─
#
# DESIGN PRINCIPLE: HIGH PRECISION over recall. Each term must be a PROPER NOUN
# (TSO name, regulator acronym, unique place name, anchor-event name, industrial
# brand) that has near-zero probability of legitimately appearing in another
# country's narrative. Common geographic / administrative words (kraj, kommune,
# Bundesland, regione, département, etc.) are DROPPED because they appear in
# generic template legends and cause false positives.
#
# Calibration target: a clean country's pages should produce 0 hits from any
# other country's vocab. A contaminated country (CR pre-rollback) should produce
# ≥THRESHOLD hits.
VOCAB = {
    "iceland": [
        # TSO/DSO/regulator: 4
        "Landsnet", "Landsvirkjun", "Orkustofnun", "Veðurstofa Íslands",
        # Place names (unique to Iceland): 7
        "Reykjavík", "Reykjanes", "Suðurnes", "Vestfirðir", "Höfuðborgarsvæðið",
        "Selfoss", "Hveragerði",
        # Anchor events / hydro / volcanic (unique): 6
        "Eyjafjallajökull", "Sundhnúkur", "Svartsengi", "Þjórsá",
        "Markarfljót", "jökulhlaup",
        # Cyber/orgs (unique): 2
        "CERT-IS", "GovCERT-IS",
        # DSOs (unique): 3
        "RARIK", "HS Veitur", "HS Orka",
        # Currency/identifier: 2
        "Ísland", "ISK",
    ],
    "hungary": [
        # TSO/DSO/regulator: 4
        "MAVIR", "MVM", "MEKH", "Démász",
        # Unique DSO names (heritage portfolio): 3
        "Émász", "Elmű", "E.ON Tiszántúli",
        # Place names (unique to HU): 8
        "Mátra", "Tolna megye", "Komárom-Esztergom", "Győr-Moson-Sopron",
        "Bács-Kiskun", "Szabolcs-Szatmár-Bereg", "Hajdú-Bihar", "Borsod-Abaúj-Zemplén",
        # Industrial anchors (unique): 4
        "Audi Győr", "Mercedes Kecskemét", "Suzuki Esztergom", "BMW Debrecen",
        # Nuclear: 1
        "Paks Atomerőmű",
        # Stat orgs (unique): 3
        "OMSZ", "MBFSZ", "KSH",
        # Currency: 1
        "forint",
    ],
    "korea": [
        # TSO/DSO/regulator: 3
        "KEPCO", "KPX", "KHNP",
        # Place names (unique to KR): 9
        "Pyeongtaek", "Icheon", "Hwaseong", "Gyeonggi", "Gyeongbuk",
        "Gyeongnam", "Jeonnam", "Chungnam", "Chungbuk",
        # Anchor events / NPPs (unique): 7
        "Hanul", "Hanbit", "Wolseong", "Saeul", "Shin-Kori", "Shin-Hanul",
        # Chaebol fab corridor (unique): 3
        "Samsung Pyeongtaek", "SK Hynix Icheon", "POSCO Gwangyang",
        # Typhoon anchors: 3
        "Hinnamnor", "Khanun", "Bolaven",
        # Cyber: 2
        "KISA", "KrCERT",
        # Currency/identifier: 2
        "KRW", "한국",
    ],
    "slovenia": [
        # TSO/regulator/utility: 4
        "ELES", "AGEN-RS", "GEN energija", "Borzen",
        # Place names (unique): 7
        "Krško", "Osrednjeslovenska", "Obalno-kraška", "Podravska",
        "Savinjska", "Gorenjska", "Pomurska",
        # Anchor events / NPPs: 1
        "NEK Krško",
        # Currency/identifier removed (EUR shared with cohort)
        "Slovenija",
    ],
    "slovakia": [
        # TSO/regulator: 3
        "SEPS", "ÚRSO", "Slovenské elektrárne",
        # Place names (unique kraje): 6
        "Bratislavský kraj", "Nitriansky kraj", "Trnavský kraj",
        "Trenčiansky kraj", "Žilinský kraj", "Banskobystrický kraj",
        # NPPs (unique): 2
        "Bohunice", "Mochovce",
        # Currency removed (EUR)
        "Slovenská",
    ],
    "czechia": [
        # TSO/regulator/utility: 4
        "ČEPS", "ERÚ", "ČSÚ", "ČEZ",
        # NPPs (unique): 2
        "Temelín", "Dukovany",
        # Place names (unique): 5
        "Středočeský kraj", "Jihomoravský kraj", "Moravskoslezský kraj",
        "Ústecký kraj", "Praha kraj",
        # Currency: 1
        "Kč",
    ],
    "luxembourg": [
        # Utility/regulator: 3
        "Creos", "ENOVOS", "ILR Luxembourg",
        # Place names (unique cantons): 6
        "Esch-sur-Alzette", "Belval Luxembourg", "Diekirch",
        "Echternach", "Grevenmacher", "Wiltz",
        # Stat: 2
        "STATEC", "BCL Luxembourg",
        # Hydro: 1
        "Vianden Pumped",
    ],
    "estonia": [
        "Elering", "Konkurentsiamet", "Eesti Energia",
        "Narva", "Harju", "Pärnumaa", "Tartumaa", "Saaremaa",
        "Eesti", "maakond",
    ],
    "latvia": [
        "AS Augstsprieguma tīkls", "AST Latvia", "SPRK", "Latvenergo",
        "Rīga", "Daugava", "Kurzeme", "Vidzeme", "Latgale", "Zemgale",
        "Latvijas",
    ],
    "lithuania": [
        "Litgrid", "VERT", "Ignitis", "Visaginas", "Ignalina",
        "Vilnius apskritis", "Kauno apskritis", "Klaipėdos apskritis",
        "Lietuva",
    ],
    "germany": [
        # TSOs (unique): 4
        "TenneT TSO", "50Hertz", "Amprion", "TransnetBW",
        # Regulator/stat: 2
        "Bundesnetzagentur", "BNetzA",
        # Place names (Länder, unique): 6
        "Schleswig-Holstein", "Nordrhein-Westfalen", "Niedersachsen",
        "Bayern", "Baden-Württemberg", "Mecklenburg-Vorpommern",
        # Utilities (unique): 2
        "RWE", "EnBW",
    ],
    "france": [
        # TSO/regulator/stat: 3
        "RTE France", "CRE France", "INSEE",
        # Utility: 1
        "Enedis",
        # Place names (regions, unique): 6
        "Île-de-France", "Auvergne-Rhône-Alpes", "Nouvelle-Aquitaine",
        "Occitanie", "Pays de la Loire", "Provence-Alpes-Côte d'Azur",
    ],
    "italy": [
        "Terna SpA", "ARERA", "ISTAT", "Enel Distribuzione", "GME Italia",
        "Lombardia", "Lazio", "Campania", "Veneto", "Emilia-Romagna",
        "Sicilia", "Sardegna", "Piemonte", "Toscana",
    ],
    "spain": [
        "Red Eléctrica de España", "REE Spain", "CNMC España", "INE España",
        "Iberdrola Distribución",
        "Cataluña", "Andalucía", "Galicia", "Castilla y León",
        "Comunidad Valenciana", "País Vasco",
    ],
    "japan": [
        "TEPCO", "Chubu Electric", "Kansai Electric", "Tohoku Electric",
        "Kyushu Electric", "Hokkaido EPCO", "Shikoku Electric", "OCCTO",
        "METI Japan",
        "Fukushima", "Kashiwazaki-Kariwa", "Kanto Japan",
    ],
    "us": [
        "ERCOT", "PJM Interconnection", "MISO", "CAISO", "NYISO", "ISO-NE",
        "WECC", "SERC", "NERC", "FERC",
    ],
    "uk": [
        "National Grid ESO", "NGESO", "Ofgem", "DUKES UK",
        "UK Power Networks", "UKPN",
    ],
    "ireland": [
        "EirGrid", "ESB Networks", "CRU Ireland", "CSO Ireland",
        "Éire",
    ],
    "portugal": [
        "REN Portugal", "ERSE Portugal", "EDP Distribuição", "INE Portugal",
        "Açores Portugal", "Madeira Portugal", "Alentejo", "Algarve",
    ],
    "netherlands": [
        "TenneT NL", "ACM Nederland", "CBS Nederland", "Stedin",
        "Liander", "Enexis",
        "Randstad", "Eemshaven",
    ],
    "belgium": [
        "Elia België", "Elia Belgique", "CREG Belgium", "Statbel",
        "Fluvius", "ORES Belgium", "Sibelga",
        "Vlaanderen", "Wallonie Belgium",
    ],
    "austria": [
        "APG Austria", "E-Control Austria", "Statistik Austria",
        "Tirol", "Vorarlberg", "Steiermark", "Burgenland", "Oberösterreich",
        "Niederösterreich", "Kärnten",
    ],
    "switzerland": [
        "Swissgrid", "ElCom Switzerland", "Bundesamt für Statistik",
        "Genève", "Vaud", "Wallis Switzerland", "Graubünden", "Aargau",
    ],
    "denmark": [
        "Energinet", "DERA Denmark", "Sjælland", "Jutland", "Fyn",
        "Hovedstaden",
    ],
    "sweden": [
        "Svenska kraftnät", "Energimarknadsinspektionen", "SCB Sweden",
        "Norrbotten", "Västra Götaland", "Skåne",
    ],
    "norway": [
        "Statnett", "NVE Norway", "SSB Norway",
        "Nordland", "Trøndelag", "Vestland", "Innlandet",
    ],
    "finland": [
        "Fingrid", "Energiavirasto", "Tilastokeskus",
        "Uusimaa", "Pirkanmaa", "Pohjois-Pohjanmaa",
    ],
    "poland": [
        "PSE Polska", "URE Poland", "GUS Poland",
        "Mazowieckie", "Śląskie", "Małopolskie", "Wielkopolskie",
    ],
    "greece": [
        "ADMIE", "RAE Greece", "ELSTAT",
        "Attiki", "Kentriki Makedonia", "Sterea Ellada",
    ],
    "turkey": [
        "TEİAŞ", "EPDK", "TÜİK Turkey",
        "İç Anadolu", "Marmara Turkey", "Doğu Anadolu",
    ],
    "mexico": [
        "CFE Mexico", "CRE Mexico", "CENACE", "INEGI",
        "CDMX", "Nuevo León México", "Querétaro México", "Jalisco México",
    ],
    "chile": [
        "Coordinador Eléctrico", "CNE Chile", "INE Chile",
        "Biobío Chile", "Atacama Chile",
    ],
    "australia": [
        "AEMO", "AER Australia", "ABS Australia",
        "NSW Australia", "Victoria Australia", "Queensland",
        "South Australia Wind",
    ],
    "new-zealand": [
        "Transpower", "Electricity Authority NZ", "Stats NZ",
        "Auckland NZ", "Wellington NZ", "Canterbury NZ", "Otago",
    ],
    "canada": [
        "Hydro-Québec", "AESO", "IESO Ontario", "Statistics Canada",
        "Alberta Canada", "Quebec Canada",
    ],
    "colombia": [
        # TSO + Transmission + Regulator (CO-specific)
        "XM Colombia", "Compañía de Expertos en Mercados",
        "ISA INTERCOLOMBIA", "ISA Colombia",
        "CREG Colombia", "UPME Colombia", "MME Colombia",
        # Stat + central bank + agencies
        "DANE Colombia", "Banco de la República", "IDEAM Colombia",
        "SGC Colombia", "Servicio Geológico Colombiano",
        "ColCERT", "CSIRT-XM", "CCOCI",
        "Unidad de Víctimas", "Migración Colombia",
        # DSO/generator brands
        "Codensa", "EPM Medellín", "Emgesa", "Isagen Colombia",
        "Celsia", "EPSA", "Tebsa", "Termocandelaria",
        "Drummond Colombia", "Cerrejón",
        # Major cities + departamentos
        "Bogotá D.C.", "Medellín", "Cali Colombia", "Barranquilla",
        "Cartagena Colombia", "Bucaramanga", "Cúcuta",
        "Antioquia", "Cundinamarca", "Casanare",
        "Chocó", "La Guajira", "Boyacá", "Nariño Colombia",
        "Catatumbo", "Llanos Orientales",
        # Volcanoes (CO-specific anchors)
        "Nevado del Ruiz", "Armero", "Galeras Colombia",
        "Nevado del Tolima", "Puracé", "Nevado del Huila",
        # Anchor events
        "Apagón 1992", "Apagón 1993",
        "Armenia 1999", "Tumaco 1979", "Mocoa 2017",
        # Hydro + grid
        "Ituango", "Guavio", "Sogamoso hydro", "El Quimbo",
        "Chivor Colombia", "Hagit",
        # Conflict
        "FARC-EP", "ELN Colombia", "Clan del Golfo",
        # System
        "SIN Colombia", "MEM Colombia", "CND XM",
        # Currency + cohort
        "COP Colombia", "peso colombiano",
        # Geology
        "Nazca plate", "Bucaramanga seismic nest",
        # Policy framework
        "CONPES 3854", "CONPES 3995",
    ],
    "costa-rica": [
        # TSO/DSO (single-DSO monopoly)
        "ICE Costa Rica", "Instituto Costarricense de Electricidad",
        "CNFL", "JASEC", "ESPH", "Coopelesca", "Coopeguanacaste",
        # Regulator
        "ARESEP", "MINAE", "SEPSE",
        # Place names (provincias)
        "San José Costa Rica", "Alajuela Costa Rica", "Cartago Costa Rica",
        "Heredia Costa Rica", "Guanacaste", "Puntarenas", "Limón Costa Rica",
        # Anchor events
        "Nicoya 2012", "Cinchona 2009", "Cariblanco",
        # Volcanoes
        "Arenal volcano", "Poás", "Turrialba", "Rincón de la Vieja",
        # Hydro
        "Reventazón", "Miravalles",
        # SIEPAC
        "SIEPAC",
        # Stat/cyber
        "CSIRT-CR", "MICITT",
        # Currency
        "CRC", "Colón",
    ],
}

# Pages to scan
PAGES = [
    "index.html", "intelligence.html", "regional.html", "map.html",
    "data.html", "methodology.html", "esg-report.html", "dno-dashboard.html",
    "ssi-metadata.js",
]


def load_slugs():
    """Load slugs from countries.json (SoT)."""
    path = REPO_ROOT / "intelligence" / "countries.json"
    try:
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, dict) and "countries" in data:
            return [c["slug"] for c in data["countries"] if c.get("slug")]
        return list(data.keys())
    except Exception:
        return sorted([d.name for d in REPO_ROOT.iterdir() if d.is_dir() and (d / "index.html").exists()])


def scan_country(slug):
    """For one country, count hits from EVERY other country's vocab. Returns dict."""
    country_dir = REPO_ROOT / slug
    if not country_dir.is_dir():
        return None

    # Concatenate all pages text
    pages_text = ""
    for page in PAGES:
        path = country_dir / page
        if path.exists():
            try:
                pages_text += "\n" + path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                pass
    if not pages_text:
        return None

    # Count hits from every other country's vocab
    leakage = {}
    for other_slug, vocab in VOCAB.items():
        if other_slug == slug:
            continue
        hits = []
        for term in vocab:
            # Word-boundary match, case-sensitive (proper nouns)
            count = len(re.findall(r"(?<!\w)" + re.escape(term) + r"(?!\w)", pages_text))
            if count > 0:
                hits.append((term, count))
        if hits:
            total = sum(c for _, c in hits)
            leakage[other_slug] = {"total": total, "hits": hits[:5]}  # top 5 terms
    return leakage


def main():
    args = sys.argv[1:]
    strict = "--strict" in args
    args = [a for a in args if a != "--strict"]

    if args and args[0] == "--vocab":
        for slug, terms in VOCAB.items():
            print(f"{slug:14}  {len(terms):>3} terms")
        sys.exit(0)

    if args:
        slugs = [args[0]]
    else:
        slugs = load_slugs()

    print(f"check_content_leakage.py — Discipline #21 — scanning {len(slugs)} countries × {len(VOCAB)} vocabularies")
    print(f"  Threshold: ≥{THRESHOLD} hits from another country's vocab = FAIL")
    print()

    total_fails = 0
    countries_with_issues = 0

    for slug in slugs:
        leakage = scan_country(slug)
        if leakage is None:
            continue

        fails = {k: v for k, v in leakage.items() if v["total"] >= THRESHOLD}
        warns = {k: v for k, v in leakage.items() if 0 < v["total"] < THRESHOLD}

        if not fails and not warns:
            print(f"  PASS {slug}")
        elif fails:
            countries_with_issues += 1
            total_fails += len(fails)
            print(f"  FAIL {slug:18} contaminated by: " +
                  ", ".join(f"{k}({v['total']})" for k, v in sorted(fails.items(), key=lambda x: -x[1]['total'])))
            for source, info in sorted(fails.items(), key=lambda x: -x[1]["total"])[:3]:
                top = ", ".join(f"{t}×{c}" for t, c in info["hits"][:3])
                print(f"      ← {source}: {top}")
        elif warns:
            countries_with_issues += 1
            print(f"  WARN {slug:18} minor leakage: " +
                  ", ".join(f"{k}({v['total']})" for k, v in sorted(warns.items(), key=lambda x: -x[1]['total'])))

    print()
    print(f"Summary: {len(slugs)} countries scanned, {countries_with_issues} with issues, {total_fails} fails")

    if total_fails and strict:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
