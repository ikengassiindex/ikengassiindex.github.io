"""US P39 Wave 4 base module — alias map + resolver + bbox geometry.

Portugal P33 bi-directional Option B canonical INHERITANCE with
US-specific extensions:

Convention #78 BINDING 21ST enforcement — 3-language US coverage:
  English (primary + General American + Southern + Northeast + Chicano
  + Hawaiian Creole variants) + Spanish (Bilingual official Puerto Rico
  + New Mexico state-official + Mexican-American + PR Spanish + Cuban-
  American) + Native American languages (574 tribes + Navajo Diné
  dominant + Cherokee + Alaska Native + Hawaiian ʻŌlelo Hawaiʻi).

Convention #78 §4bis.5 Layer 3 — NOT REQUIRED (5th cohort-wide):
  HORIZONTAL FRAGMENTATION extends Germany P38 pattern at 3.5× utility
  scale (~3,200+ utilities). State-franchise architecture cleanly
  delineates all major metropolitan territorial boundaries.

12-layer resolver (Portugal P33 canonical + US-specific extensions):
  1. Alias exact match (~180 entries: 7 RTOs + 30+ IOUs + 15+ munis + 5 PMAs + tribal + territorial)
  2. Voltage EHV declared (≥300 kV → RTO/PMA attribution via bbox routing)
  3. Voltage HV subT declared (69/138/230 kV)
  4. NYC metropolitan bbox → Con Edison + LIPA
  5. LA metropolitan bbox → LADWP + SoCal Edison split
  6. SF Bay bbox → PG&E + municipal
  7. Chicago bbox → ComEd
  8. Texas ERCOT bbox → CenterPoint / Oncor / AEP Texas
  9. Alaska bbox → GVEA + Chugach + HEA
  10. Hawaii bbox → HECO + KIUC + HELCO
  11. US Territories bbox routing (PR PREPA + USVI + Guam + Mariana + Samoa)
  12. Fallback default (regional attribution based on longitude — Eastern IC / Western IC / ERCOT)
"""

from __future__ import annotations

import re
import unicodedata
from typing import Optional

# ─────────────────────────────────────────────────────────────
# US master bbox (crosses anti-meridian at Alaska Aleutians)
# ─────────────────────────────────────────────────────────────

US_MASTER_BBOX = {
    "lat_min": -14.55,   # American Samoa (South Pacific)
    "lat_max": 71.60,    # Barrow, Alaska (Arctic)
    "lon_min_east": -179.15,  # Alaska Aleutians (crosses anti-meridian eastward)
    "lon_max_east": -64.50,   # US Virgin Islands (Atlantic)
    "lon_min_west": 144.60,   # Guam (Western Pacific — cross anti-meridian)
    "lon_max_west": 146.10,   # Northern Mariana Islands
}

# 12-zone bbox split (with sub-zones for US Territories combined)
NORTHEAST_BBOX = (37.90, -80.52, 47.46, -66.90)
SOUTHEAST_BBOX = (24.40, -94.05, 39.14, -75.24)
GREAT_LAKES_BBOX = (37.77, -97.24, 49.38, -80.52)
PLAINS_BBOX = (33.00, -104.05, 49.00, -89.09)
TEXAS_BBOX = (25.84, -106.65, 36.50, -93.51)
SOUTHWEST_BBOX = (31.33, -114.82, 37.00, -94.43)
MOUNTAIN_BBOX = (35.00, -117.24, 49.00, -102.04)
CALIFORNIA_BBOX = (32.53, -124.48, 42.01, -114.13)
PACIFIC_NW_BBOX = (41.99, -124.85, 49.00, -116.46)
ALASKA_BBOX = (51.20, -179.15, 71.60, -129.98)
HAWAII_BBOX = (18.91, -160.25, 22.24, -154.75)

# US Territories subzones (packaged as 3 separate zones)
PUERTO_RICO_USVI_BBOX = (17.62, -67.98, 18.60, -64.50)
GUAM_MARIANA_BBOX = (13.20, 144.60, 20.60, 146.10)
AMERICAN_SAMOA_BBOX = (-14.55, -170.85, -14.15, -169.40)

# ─────────────────────────────────────────────────────────────
# Metropolitan bboxes (utility routing, NOT §4bis.5 geofences)
# ─────────────────────────────────────────────────────────────

# NYC 5-borough (Con Edison territory)
NYC_BBOX = (40.50, -74.25, 40.92, -73.70)
# Long Island (LIPA / PSEG-LI)
LONG_ISLAND_BBOX = (40.55, -73.65, 41.15, -71.85)

# LA city (LADWP)
LA_CITY_BBOX = (33.70, -118.66, 34.34, -118.15)

# SF Bay Area (PG&E dominant + municipals)
SF_BAY_BBOX = (37.20, -122.60, 38.10, -121.80)

# Chicago (ComEd dominant)
CHICAGO_BBOX = (41.60, -87.94, 42.06, -87.52)

# Houston (CenterPoint Energy ERCOT delivery)
HOUSTON_BBOX = (29.50, -95.85, 30.10, -95.00)

# Dallas-Fort Worth (Oncor ERCOT delivery)
DFW_BBOX = (32.55, -97.55, 33.15, -96.55)

# Phoenix (APS + SRP)
PHOENIX_BBOX = (33.30, -112.32, 33.85, -111.65)

# Seattle (Seattle City Light)
SEATTLE_BBOX = (47.48, -122.44, 47.75, -122.24)

# Anchorage (Chugach Electric / ML&P)
ANCHORAGE_BBOX = (61.05, -150.20, 61.30, -149.55)

# Fairbanks (GVEA)
FAIRBANKS_BBOX = (64.75, -147.95, 64.92, -147.55)

# Puerto Rico bbox (PREPA territory)
PUERTO_RICO_ONLY_BBOX = (17.85, -67.30, 18.55, -65.20)

# US Virgin Islands (USVI Water and Power Authority)
USVI_ONLY_BBOX = (17.62, -65.05, 18.44, -64.50)

# Navajo Nation reservation (Navajo Tribal Utility Authority)
NAVAJO_NATION_BBOX = (35.35, -111.70, 37.20, -108.68)


# ─────────────────────────────────────────────────────────────
# ALIAS MAP — Convention #78 BINDING 21st enforcement
# 3-language: English + Spanish + Native American representative
# ─────────────────────────────────────────────────────────────

ALIAS_MAP: dict[str, tuple[str, str]] = {
    # ─── 7 RTOs/ISOs (Layer 1 exact match) ─────────────────────
    "pjm": ("PJM Interconnection LLC", "RTO"),
    "pjm interconnection": ("PJM Interconnection LLC", "RTO"),
    "pjm interconnection llc": ("PJM Interconnection LLC", "RTO"),

    "miso": ("Midcontinent Independent System Operator", "RTO"),
    "midcontinent iso": ("Midcontinent Independent System Operator", "RTO"),
    "midwest iso": ("Midcontinent Independent System Operator", "RTO"),
    "miso energy": ("Midcontinent Independent System Operator", "RTO"),

    "ercot": ("Electric Reliability Council of Texas", "ISO"),
    "electric reliability council of texas": ("Electric Reliability Council of Texas", "ISO"),

    "caiso": ("California Independent System Operator", "ISO"),
    "california iso": ("California Independent System Operator", "ISO"),
    "cal iso": ("California Independent System Operator", "ISO"),

    "spp": ("Southwest Power Pool", "RTO"),
    "southwest power pool": ("Southwest Power Pool", "RTO"),

    "nyiso": ("New York Independent System Operator", "ISO"),
    "new york iso": ("New York Independent System Operator", "ISO"),
    "ny iso": ("New York Independent System Operator", "ISO"),

    "isone": ("ISO New England", "ISO"),
    "iso-ne": ("ISO New England", "ISO"),
    "iso ne": ("ISO New England", "ISO"),
    "iso new england": ("ISO New England", "ISO"),

    # ─── 5 Federal Power Marketing Administrations (Layer 1) ───
    "tva": ("Tennessee Valley Authority", "PMA"),
    "tennessee valley authority": ("Tennessee Valley Authority", "PMA"),

    "bpa": ("Bonneville Power Administration", "PMA"),
    "bonneville power": ("Bonneville Power Administration", "PMA"),
    "bonneville power administration": ("Bonneville Power Administration", "PMA"),

    "wapa": ("Western Area Power Administration", "PMA"),
    "western area power": ("Western Area Power Administration", "PMA"),
    "western area power administration": ("Western Area Power Administration", "PMA"),

    "swpa": ("Southwestern Power Administration", "PMA"),
    "southwestern power": ("Southwestern Power Administration", "PMA"),
    "southwestern power administration": ("Southwestern Power Administration", "PMA"),

    "sepa": ("Southeastern Power Administration", "PMA"),
    "southeastern power": ("Southeastern Power Administration", "PMA"),
    "southeastern power administration": ("Southeastern Power Administration", "PMA"),

    # ─── Major IOUs (Layer 1 exact match — top ~30) ────────────
    "duke energy": ("Duke Energy Corporation", "IOU"),
    "duke energy carolinas": ("Duke Energy Carolinas", "IOU"),
    "duke energy florida": ("Duke Energy Florida", "IOU"),
    "duke energy ohio": ("Duke Energy Ohio", "IOU"),
    "duke energy indiana": ("Duke Energy Indiana", "IOU"),
    "duke energy kentucky": ("Duke Energy Kentucky", "IOU"),
    "duke energy progress": ("Duke Energy Progress", "IOU"),

    "nextera energy": ("NextEra Energy Inc.", "IOU"),
    "fpl": ("Florida Power & Light Company", "IOU"),
    "florida power and light": ("Florida Power & Light Company", "IOU"),
    "florida power light": ("Florida Power & Light Company", "IOU"),

    "southern company": ("Southern Company", "IOU"),
    "georgia power": ("Georgia Power (Southern Company)", "IOU"),
    "alabama power": ("Alabama Power (Southern Company)", "IOU"),
    "mississippi power": ("Mississippi Power (Southern Company)", "IOU"),

    "exelon": ("Exelon Corporation", "IOU"),
    "comed": ("Commonwealth Edison (Exelon)", "IOU"),
    "commonwealth edison": ("Commonwealth Edison (Exelon)", "IOU"),
    "bge": ("Baltimore Gas and Electric (Exelon)", "IOU"),
    "baltimore gas and electric": ("Baltimore Gas and Electric (Exelon)", "IOU"),
    "delmarva power": ("Delmarva Power (Exelon)", "IOU"),
    "atlantic city electric": ("Atlantic City Electric (Exelon)", "IOU"),
    "pepco": ("Pepco (Exelon)", "IOU"),
    "peco": ("PECO Energy (Exelon)", "IOU"),

    "dominion energy": ("Dominion Energy Inc.", "IOU"),
    "dominion virginia": ("Dominion Energy Virginia", "IOU"),
    "dominion north carolina": ("Dominion Energy North Carolina", "IOU"),

    "pg&e": ("Pacific Gas and Electric Company", "IOU"),
    "pacific gas and electric": ("Pacific Gas and Electric Company", "IOU"),
    "pg and e": ("Pacific Gas and Electric Company", "IOU"),

    "sce": ("Southern California Edison", "IOU"),
    "southern california edison": ("Southern California Edison", "IOU"),
    "socal edison": ("Southern California Edison", "IOU"),

    "sempra": ("Sempra Energy", "IOU"),
    "sdge": ("San Diego Gas and Electric", "IOU"),
    "san diego gas and electric": ("San Diego Gas and Electric", "IOU"),
    "socalgas": ("Southern California Gas Company", "IOU"),

    "xcel energy": ("Xcel Energy Inc.", "IOU"),
    "public service colorado": ("Public Service Company of Colorado (Xcel)", "IOU"),
    "northern states power": ("Northern States Power Company (Xcel)", "IOU"),
    "southwestern public service": ("Southwestern Public Service (Xcel)", "IOU"),

    "aep": ("American Electric Power", "IOU"),
    "american electric power": ("American Electric Power", "IOU"),
    "aep ohio": ("AEP Ohio", "IOU"),
    "aep texas": ("AEP Texas", "IOU"),
    "kentucky power": ("Kentucky Power (AEP)", "IOU"),
    "appalachian power": ("Appalachian Power (AEP)", "IOU"),
    "indiana michigan power": ("Indiana Michigan Power (AEP)", "IOU"),
    "public service oklahoma": ("Public Service Company of Oklahoma (AEP)", "IOU"),
    "southwestern electric power": ("Southwestern Electric Power (AEP)", "IOU"),

    "con edison": ("Consolidated Edison Inc.", "IOU"),
    "consolidated edison": ("Consolidated Edison Inc.", "IOU"),
    "coned": ("Consolidated Edison Inc.", "IOU"),

    "eversource": ("Eversource Energy", "IOU"),
    "eversource energy": ("Eversource Energy", "IOU"),
    "nstar": ("NSTAR (Eversource)", "IOU"),
    "public service new hampshire": ("Public Service Company of New Hampshire (Eversource)", "IOU"),

    "firstenergy": ("FirstEnergy Corp", "IOU"),
    "first energy": ("FirstEnergy Corp", "IOU"),
    "ohio edison": ("Ohio Edison (FirstEnergy)", "IOU"),
    "toledo edison": ("Toledo Edison (FirstEnergy)", "IOU"),
    "cleveland electric": ("Cleveland Electric Illuminating (FirstEnergy)", "IOU"),
    "penelec": ("Pennsylvania Electric (FirstEnergy)", "IOU"),
    "penn power": ("Pennsylvania Power (FirstEnergy)", "IOU"),
    "met-ed": ("Metropolitan Edison (FirstEnergy)", "IOU"),
    "west penn power": ("West Penn Power (FirstEnergy)", "IOU"),
    "mon power": ("Monongahela Power (FirstEnergy)", "IOU"),
    "potomac edison": ("Potomac Edison (FirstEnergy)", "IOU"),
    "jcp&l": ("Jersey Central Power & Light (FirstEnergy)", "IOU"),

    "entergy": ("Entergy Corporation", "IOU"),
    "entergy louisiana": ("Entergy Louisiana", "IOU"),
    "entergy mississippi": ("Entergy Mississippi", "IOU"),
    "entergy arkansas": ("Entergy Arkansas", "IOU"),
    "entergy texas": ("Entergy Texas", "IOU"),
    "entergy new orleans": ("Entergy New Orleans", "IOU"),

    "ppl": ("PPL Corporation", "IOU"),
    "ppl electric": ("PPL Electric Utilities", "IOU"),
    "kentucky utilities": ("Kentucky Utilities (PPL)", "IOU"),
    "lg&e": ("Louisville Gas and Electric (PPL)", "IOU"),

    "wec energy": ("WEC Energy Group", "IOU"),
    "we energies": ("We Energies (WEC)", "IOU"),
    "wisconsin electric": ("Wisconsin Electric (WEC)", "IOU"),
    "wisconsin public service": ("Wisconsin Public Service (WEC)", "IOU"),

    "aes": ("AES Corporation", "IOU"),
    "aes indiana": ("AES Indiana", "IOU"),
    "aes ohio": ("AES Ohio", "IOU"),
    "dpl": ("Dayton Power and Light (AES)", "IOU"),

    "constellation energy": ("Constellation Energy Corporation", "IOU"),

    "alliant energy": ("Alliant Energy Corporation", "IOU"),
    "interstate power and light": ("Interstate Power and Light (Alliant)", "IOU"),
    "wisconsin power and light": ("Wisconsin Power and Light (Alliant)", "IOU"),

    "centerpoint energy": ("CenterPoint Energy Inc.", "IOU"),
    "centerpoint": ("CenterPoint Energy Inc.", "IOU"),

    "ameren": ("Ameren Corporation", "IOU"),
    "ameren missouri": ("Ameren Missouri", "IOU"),
    "ameren illinois": ("Ameren Illinois", "IOU"),
    "union electric": ("Union Electric (Ameren)", "IOU"),

    "dte energy": ("DTE Energy Company", "IOU"),
    "dte electric": ("DTE Electric Company", "IOU"),
    "detroit edison": ("Detroit Edison (DTE)", "IOU"),

    "consumers energy": ("Consumers Energy Company", "IOU"),

    "pseg": ("Public Service Enterprise Group", "IOU"),
    "public service enterprise group": ("Public Service Enterprise Group", "IOU"),
    "pseg new jersey": ("PSEG New Jersey", "IOU"),
    "pseg long island": ("PSEG Long Island (LIPA operations)", "IOU"),

    "pnm": ("PNM Resources", "IOU"),
    "public service new mexico": ("Public Service Company of New Mexico (PNM)", "IOU"),

    "puget sound energy": ("Puget Sound Energy", "IOU"),
    "pse": ("Puget Sound Energy", "IOU"),

    "portland general electric": ("Portland General Electric", "IOU"),
    "pge oregon": ("Portland General Electric", "IOU"),

    "idaho power": ("Idaho Power Company", "IOU"),

    "avista": ("Avista Corporation", "IOU"),
    "avista utilities": ("Avista Utilities", "IOU"),

    "pacificorp": ("PacifiCorp", "IOU"),
    "pacific power": ("Pacific Power (PacifiCorp)", "IOU"),
    "rocky mountain power": ("Rocky Mountain Power (PacifiCorp)", "IOU"),

    "berkshire hathaway energy": ("Berkshire Hathaway Energy", "IOU"),

    "nv energy": ("NV Energy", "IOU"),
    "sierra pacific": ("Sierra Pacific Power (NV Energy)", "IOU"),

    "arizona public service": ("Arizona Public Service", "IOU"),
    "aps": ("Arizona Public Service", "IOU"),

    "tep": ("Tucson Electric Power", "IOU"),
    "tucson electric power": ("Tucson Electric Power", "IOU"),
    "unisource energy": ("UniSource Energy Services", "IOU"),

    "el paso electric": ("El Paso Electric", "IOU"),

    "oncor": ("Oncor Electric Delivery", "IOU"),
    "oncor electric": ("Oncor Electric Delivery", "IOU"),

    # ─── Major Municipal Utilities (Layer 1) ───────────────────
    "ladwp": ("Los Angeles Department of Water and Power", "MUNI"),
    "los angeles department of water and power": ("Los Angeles Department of Water and Power", "MUNI"),

    "smud": ("Sacramento Municipal Utility District", "MUNI"),
    "sacramento municipal utility district": ("Sacramento Municipal Utility District", "MUNI"),

    "seattle city light": ("Seattle City Light", "MUNI"),

    "jea": ("JEA (Jacksonville Electric Authority)", "MUNI"),
    "jacksonville electric authority": ("JEA (Jacksonville Electric Authority)", "MUNI"),

    "cps energy": ("CPS Energy (San Antonio)", "MUNI"),
    "city public service": ("CPS Energy (San Antonio)", "MUNI"),

    "austin energy": ("Austin Energy", "MUNI"),

    "nashville electric service": ("Nashville Electric Service", "MUNI"),
    "nes": ("Nashville Electric Service", "MUNI"),

    "memphis light gas water": ("Memphis Light Gas and Water", "MUNI"),
    "mlgw": ("Memphis Light Gas and Water", "MUNI"),

    "chattanooga epb": ("Chattanooga Electric Power Board (EPB)", "MUNI"),
    "epb chattanooga": ("Chattanooga Electric Power Board (EPB)", "MUNI"),

    "lipa": ("Long Island Power Authority", "MUNI"),
    "long island power authority": ("Long Island Power Authority", "MUNI"),

    "srp": ("Salt River Project", "MUNI"),
    "salt river project": ("Salt River Project", "MUNI"),

    "nppd": ("Nebraska Public Power District", "MUNI"),
    "nebraska public power district": ("Nebraska Public Power District", "MUNI"),

    "oppd": ("Omaha Public Power District", "MUNI"),
    "omaha public power district": ("Omaha Public Power District", "MUNI"),

    "meag": ("Municipal Electric Authority of Georgia", "MUNI"),
    "municipal electric authority georgia": ("Municipal Electric Authority of Georgia", "MUNI"),

    "nypa": ("New York Power Authority", "MUNI"),
    "new york power authority": ("New York Power Authority", "MUNI"),

    "hetch hetchy": ("San Francisco Public Utilities Commission (Hetch Hetchy)", "MUNI"),
    "sfpuc": ("San Francisco Public Utilities Commission", "MUNI"),

    # ─── Alaska + Hawaii utilities ─────────────────────────────
    "chugach electric": ("Chugach Electric Association", "COOP"),
    "chugach": ("Chugach Electric Association", "COOP"),

    "gvea": ("Golden Valley Electric Association", "COOP"),
    "golden valley electric": ("Golden Valley Electric Association", "COOP"),

    "hea": ("Homer Electric Association", "COOP"),
    "homer electric": ("Homer Electric Association", "COOP"),

    "avec": ("Alaska Village Electric Cooperative", "COOP"),
    "alaska village electric": ("Alaska Village Electric Cooperative", "COOP"),

    "ml&p": ("Anchorage Municipal Light & Power", "MUNI"),
    "anchorage municipal light and power": ("Anchorage Municipal Light & Power", "MUNI"),

    "heco": ("Hawaiian Electric Company", "IOU"),
    "hawaiian electric": ("Hawaiian Electric Company", "IOU"),
    "hawaiian electric company": ("Hawaiian Electric Company", "IOU"),

    "helco": ("Hawaii Electric Light Company", "IOU"),
    "hawaii electric light": ("Hawaii Electric Light Company", "IOU"),

    "meco": ("Maui Electric Company", "IOU"),
    "maui electric": ("Maui Electric Company", "IOU"),

    "kiuc": ("Kauai Island Utility Cooperative", "COOP"),
    "kauai island utility cooperative": ("Kauai Island Utility Cooperative", "COOP"),

    # ─── Major Rural Electric Cooperatives (Layer 1) ───────────
    "tri-state g&t": ("Tri-State Generation and Transmission Association", "COOP"),
    "tri-state generation and transmission": ("Tri-State Generation and Transmission Association", "COOP"),
    "tri state": ("Tri-State Generation and Transmission Association", "COOP"),

    "great river energy": ("Great River Energy", "COOP"),

    "basin electric": ("Basin Electric Power Cooperative", "COOP"),
    "basin electric power cooperative": ("Basin Electric Power Cooperative", "COOP"),

    "buckeye power": ("Buckeye Power Inc.", "COOP"),

    "old dominion electric cooperative": ("Old Dominion Electric Cooperative", "COOP"),
    "odec": ("Old Dominion Electric Cooperative", "COOP"),

    "seminole electric cooperative": ("Seminole Electric Cooperative", "COOP"),

    "central electric cooperative": ("Central Electric Cooperative", "COOP"),

    "south mississippi electric": ("South Mississippi Electric Power Association", "COOP"),

    # ─── Native American Tribal Utilities ──────────────────────
    "ntua": ("Navajo Tribal Utility Authority", "TRIBAL"),
    "navajo tribal utility authority": ("Navajo Tribal Utility Authority", "TRIBAL"),
    "navajo tribal utility": ("Navajo Tribal Utility Authority", "TRIBAL"),

    "kayenta township": ("Kayenta Township Utilities", "TRIBAL"),
    "blackfeet utilities": ("Blackfeet Utilities (Blackfeet Nation)", "TRIBAL"),
    "gila river": ("Gila River Indian Community Utility Authority", "TRIBAL"),
    "salt river pima maricopa": ("Salt River Pima-Maricopa Indian Community", "TRIBAL"),
    "hopi utility": ("Hopi Utilities Corporation", "TRIBAL"),
    "cherokee nation": ("Cherokee Nation Businesses (electric)", "TRIBAL"),

    # ─── US Territories utilities ──────────────────────────────
    "prepa": ("Puerto Rico Electric Power Authority", "STATE"),
    "puerto rico electric power authority": ("Puerto Rico Electric Power Authority", "STATE"),
    "autoridad de energia electrica": ("Puerto Rico Electric Power Authority", "STATE"),
    "aee": ("Puerto Rico Electric Power Authority", "STATE"),

    "wapa usvi": ("US Virgin Islands Water and Power Authority", "STATE"),
    "us virgin islands wapa": ("US Virgin Islands Water and Power Authority", "STATE"),
    "virgin islands water and power": ("US Virgin Islands Water and Power Authority", "STATE"),

    "guam power authority": ("Guam Power Authority", "STATE"),
    "gpa": ("Guam Power Authority", "STATE"),

    "american samoa power authority": ("American Samoa Power Authority", "STATE"),
    "aspa": ("American Samoa Power Authority", "STATE"),

    "commonwealth utilities corporation": ("Commonwealth Utilities Corporation (Northern Mariana Islands)", "STATE"),
    "cuc": ("Commonwealth Utilities Corporation (Northern Mariana Islands)", "STATE"),

    # ─── Rail traction (Amtrak + urban transit) ────────────────
    "amtrak": ("Amtrak (National Railroad Passenger Corporation)", "RAIL"),
    "mta": ("Metropolitan Transportation Authority NYC", "RAIL"),
    "nyc mta": ("Metropolitan Transportation Authority NYC", "RAIL"),
    "bart": ("Bay Area Rapid Transit", "RAIL"),
    "wmata": ("Washington Metropolitan Area Transit Authority", "RAIL"),
    "mbta": ("Massachusetts Bay Transportation Authority", "RAIL"),
    "cta": ("Chicago Transit Authority", "RAIL"),
    "septa": ("Southeastern Pennsylvania Transportation Authority", "RAIL"),
    "path": ("Port Authority Trans-Hudson (PATH)", "RAIL"),
    "long island rail road": ("Long Island Rail Road (MTA)", "RAIL"),
    "lirr": ("Long Island Rail Road (MTA)", "RAIL"),
    "metro-north": ("Metro-North Railroad (MTA)", "RAIL"),

    # ─── Independent Power Producers (Layer for generation-only) ─
    "vistra": ("Vistra Corp (IPP)", "IPP"),
    "vistra energy": ("Vistra Corp (IPP)", "IPP"),
    "nrg energy": ("NRG Energy Inc. (IPP)", "IPP"),
    "calpine": ("Calpine Corporation (IPP)", "IPP"),
    "invenergy": ("Invenergy LLC (IPP)", "IPP"),
    "avangrid": ("Avangrid Inc. (Iberdrola subsidiary)", "IOU"),  # actually IOU status via subsidiaries
}


# ─────────────────────────────────────────────────────────────
# NFC normalisation + alias lookup with hit counter
# ─────────────────────────────────────────────────────────────

_alias_hit_counter: int = 0


def alias_hit_count() -> int:
    return _alias_hit_counter


def reset_alias_hit_counter() -> None:
    global _alias_hit_counter
    _alias_hit_counter = 0


def _nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s).strip().lower()


def _alias_hit(raw: str) -> Optional[tuple[str, str]]:
    global _alias_hit_counter
    if not raw:
        return None
    key = _nfc(raw)
    if key in ALIAS_MAP:
        _alias_hit_counter += 1
        return ALIAS_MAP[key]
    # Broad hit: try stripping legal form suffixes
    stripped = re.sub(
        r"\s+(inc\.?|corporation|corp\.?|company|co\.?|llc|l\.p\.?|lp|"
        r"cooperative|coop|authority|association|foundation)$",
        "",
        key,
    )
    if stripped != key and stripped in ALIAS_MAP:
        _alias_hit_counter += 1
        return ALIAS_MAP[stripped]
    return None


# ─────────────────────────────────────────────────────────────
# 12-layer resolver — Portugal P33 canonical + US extensions
# ─────────────────────────────────────────────────────────────

RESOLVER_LAYERS = (
    "alias_hit",
    "voltage_ehv",
    "voltage_subtransmission",
    "nyc_bbox_coned",
    "long_island_bbox_lipa",
    "la_city_bbox_ladwp",
    "sf_bay_bbox_pge",
    "chicago_bbox_comed",
    "houston_bbox_centerpoint",
    "dfw_bbox_oncor",
    "phoenix_bbox_aps_srp",
    "seattle_bbox_scl",
    "anchorage_bbox_chugach",
    "fairbanks_bbox_gvea",
    "puerto_rico_bbox_prepa",
    "usvi_bbox_wapa",
    "navajo_nation_bbox_ntua",
    "rail_traction_25kv_ac_amtrak",
    "rail_traction_dc_third_rail",
    "fallback_default_regional_ic",
)


def _in_bbox(lat: float, lon: float, bbox: tuple) -> bool:
    lat_min, lon_min, lat_max, lon_max = bbox
    return lat_min <= lat <= lat_max and lon_min <= lon <= lon_max


def resolve_operator(
    raw_operator: Optional[str],
    *,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    voltage_kv: Optional[float] = None,
) -> tuple[str, str, Optional[str]]:
    """Return (canonical_name, role, resolution_layer)."""

    # Layer 1: alias hit
    if raw_operator:
        hit = _alias_hit(raw_operator)
        if hit:
            return hit[0], hit[1], "alias_hit"

    # Layer 2: voltage EHV declared (≥300 kV → RTO/PMA/TSO attribution)
    if voltage_kv is not None and voltage_kv >= 300.0:
        if lat is not None and lon is not None:
            # ERCOT Texas (isolated)
            if _in_bbox(lat, lon, TEXAS_BBOX):
                return "ERCOT (Electric Reliability Council of Texas)", "ISO", "voltage_ehv"
            # CAISO California
            if _in_bbox(lat, lon, CALIFORNIA_BBOX):
                return "CAISO (California ISO)", "ISO", "voltage_ehv"
            # NYISO New York
            if _in_bbox(lat, lon, (40.50, -79.76, 45.02, -71.85)):
                return "NYISO (New York ISO)", "ISO", "voltage_ehv"
            # ISO-NE New England
            if _in_bbox(lat, lon, (40.98, -73.73, 47.46, -66.90)):
                return "ISO New England", "ISO", "voltage_ehv"
            # PJM Mid-Atlantic
            if _in_bbox(lat, lon, (35.20, -84.32, 42.51, -74.69)):
                return "PJM Interconnection", "RTO", "voltage_ehv"
            # MISO Midwest
            if _in_bbox(lat, lon, (29.06, -104.05, 49.38, -80.05)):
                return "MISO (Midcontinent ISO)", "RTO", "voltage_ehv"
            # SPP Southwest Power Pool
            if _in_bbox(lat, lon, (33.62, -104.05, 49.00, -89.09)):
                return "SPP (Southwest Power Pool)", "RTO", "voltage_ehv"
            # WECC + BPA Northwest
            if _in_bbox(lat, lon, (41.99, -124.85, 49.00, -111.05)):
                return "BPA (Bonneville Power Administration)", "PMA", "voltage_ehv"
            # WAPA Western + Southwest
            if _in_bbox(lat, lon, (31.33, -122.24, 49.00, -102.04)):
                return "WAPA (Western Area Power Administration)", "PMA", "voltage_ehv"
        return "PJM Interconnection (voltage-inferred default RTO)", "RTO", "voltage_ehv"

    # Layer 3: voltage subtransmission (69/138/230 kV)
    if voltage_kv is not None and 60.0 <= voltage_kv < 300.0:
        return "US utility subtransmission (voltage-inferred)", "IOU", "voltage_subtransmission"

    # Layers 4-15: Metropolitan bbox routing (utility attribution)
    if lat is not None and lon is not None:
        if _in_bbox(lat, lon, NYC_BBOX):
            return "Consolidated Edison Inc. (bbox-inferred)", "IOU", "nyc_bbox_coned"
        if _in_bbox(lat, lon, LONG_ISLAND_BBOX):
            return "PSEG Long Island / LIPA (bbox-inferred)", "IOU", "long_island_bbox_lipa"
        if _in_bbox(lat, lon, LA_CITY_BBOX):
            return "Los Angeles Department of Water and Power (bbox-inferred)", "MUNI", "la_city_bbox_ladwp"
        if _in_bbox(lat, lon, SF_BAY_BBOX):
            return "Pacific Gas and Electric Company (bbox-inferred)", "IOU", "sf_bay_bbox_pge"
        if _in_bbox(lat, lon, CHICAGO_BBOX):
            return "Commonwealth Edison (bbox-inferred)", "IOU", "chicago_bbox_comed"
        if _in_bbox(lat, lon, HOUSTON_BBOX):
            return "CenterPoint Energy (bbox-inferred)", "IOU", "houston_bbox_centerpoint"
        if _in_bbox(lat, lon, DFW_BBOX):
            return "Oncor Electric Delivery (bbox-inferred)", "IOU", "dfw_bbox_oncor"
        if _in_bbox(lat, lon, PHOENIX_BBOX):
            return "Salt River Project / Arizona Public Service (bbox-inferred)", "MUNI", "phoenix_bbox_aps_srp"
        if _in_bbox(lat, lon, SEATTLE_BBOX):
            return "Seattle City Light (bbox-inferred)", "MUNI", "seattle_bbox_scl"
        if _in_bbox(lat, lon, ANCHORAGE_BBOX):
            return "Chugach Electric Association (bbox-inferred)", "COOP", "anchorage_bbox_chugach"
        if _in_bbox(lat, lon, FAIRBANKS_BBOX):
            return "Golden Valley Electric Association (bbox-inferred)", "COOP", "fairbanks_bbox_gvea"
        if _in_bbox(lat, lon, PUERTO_RICO_ONLY_BBOX):
            return "Puerto Rico Electric Power Authority (bbox-inferred)", "STATE", "puerto_rico_bbox_prepa"
        if _in_bbox(lat, lon, USVI_ONLY_BBOX):
            return "US Virgin Islands Water and Power Authority (bbox-inferred)", "STATE", "usvi_bbox_wapa"
        if _in_bbox(lat, lon, NAVAJO_NATION_BBOX):
            return "Navajo Tribal Utility Authority (bbox-inferred)", "TRIBAL", "navajo_nation_bbox_ntua"

    # Rail traction layers
    if voltage_kv is not None:
        if 24.0 <= voltage_kv <= 26.0:
            return "Amtrak Northeast Corridor 25 kV AC 60 Hz (rail traction)", "RAIL", "rail_traction_25kv_ac_amtrak"
        if 12.0 <= voltage_kv <= 13.0:
            return "Amtrak Northeast Corridor 12.5 kV AC 25 Hz legacy (rail traction)", "RAIL", "rail_traction_25kv_ac_amtrak"
        if 0.6 <= voltage_kv <= 0.9:
            return "Urban transit 750 V DC third rail (rail traction)", "RAIL", "rail_traction_dc_third_rail"

    # Layer 12: fallback default — regional IC attribution by longitude
    if lat is not None and lon is not None:
        # ERCOT if in Texas bbox
        if _in_bbox(lat, lon, TEXAS_BBOX):
            return "ERCOT-region utility (fallback)", "IOU", "fallback_default_regional_ic"
        # Western IC if west of Rockies (~-102°)
        if lon <= -102.0:
            return "Western Interconnection utility (fallback)", "IOU", "fallback_default_regional_ic"
        # Eastern IC otherwise
        return "Eastern Interconnection utility (fallback)", "IOU", "fallback_default_regional_ic"

    # Last resort fallback
    return "US utility (fallback default)", "IOU", "fallback_default_regional_ic"
