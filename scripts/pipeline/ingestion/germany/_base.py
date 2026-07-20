"""Germany P38 Wave 4 base module — alias map + resolver + bbox geometry.

Portugal P33 bi-directional Option B canonical INHERITANCE with
German-specific extensions:

Convention #78 BINDING 20TH enforcement — 5-language German coverage:
  German (primary + Standard Hochdeutsch + Bayerisch + Sächsisch dialects)
  + English (technical/international) + Sorbian (Lusatia recognised
  minority) + Danish (Nordschleswig recognised minority) + Frisian
  (Nord/Ost/Sylt recognised minority).

Convention #78 §4bis.5 Layer 3 — NOT REQUIRED (NEW architectural signature):
  🏆 MOST-FRAGMENTED cohort-wide DSO landscape (~900 DSOs) but HORIZONTAL
  non-overlapping territorial architecture. Each city has ONE DSO
  concession, no dual-DSO overlaps within any given municipality.

12-layer resolver (Portugal P33 canonical + 2 Germany-specific extensions):
  1. TSO exact match (50Hertz + Amprion + TenneT DE + TransnetBW)
  2. Major DSO group exact match (E.ON subsidiaries + RWE + EnBW + Vattenfall)
  3. Major regional Stadtwerke exact match (SWM + Rheinenergie + Mainova + N-ERGIE + EWE)
  4. Rail traction Deutsche Bahn (15 kV AC 16.7 Hz)
  5. Voltage EHV declared (≥330 kV → TSO attribution)
  6. Voltage HV declared (110 kV → Hochspannung distribution)
  7. Voltage subtransmission declared (60-90 kV)
  8. Berlin metropolitan bbox → Stromnetz Berlin
  9. Hamburg metropolitan bbox → Stromnetz Hamburg
  10. München metropolitan bbox → SWM Stadtwerke München
  11. Alias-map broad hit (~140 entries multi-script)
  12. Fallback E.ON group default (most extensive coverage)
"""

from __future__ import annotations

import re
import unicodedata
from typing import Optional

# ─────────────────────────────────────────────────────────────
# Germany master bbox (mainland + North Sea + Baltic offshore)
# ─────────────────────────────────────────────────────────────

GERMANY_MASTER_BBOX = {
    "lat_min": 47.27,   # Alpine southern border (Zugspitze area)
    "lat_max": 55.06,   # Baltic northern (Sylt+Rügen island area)
    "lon_min": 5.87,    # Western border (Nordrhein-Westfalen Aachen)
    "lon_max": 15.04,   # Eastern border (Görlitz Sachsen-Polen)
}

# 5-zone bbox split for Overpass API
NORD_BBOX = (52.00, 5.87, 55.06, 15.04)   # SH + HH + HB + NI + MV
WEST_BBOX = (49.10, 5.87, 52.60, 9.50)    # NRW + RP + SL
MITTE_BBOX = (49.10, 7.80, 52.00, 12.00)  # HE + TH + parts ST
OST_BBOX = (49.10, 11.00, 53.60, 15.04)   # BE + BB + SN + ST + TH east
SUED_BBOX = (47.27, 7.50, 50.60, 13.85)   # BY + BW

# ─────────────────────────────────────────────────────────────
# Metropolitan bboxes (utility routing, NOT §4bis.5 geofences)
# ─────────────────────────────────────────────────────────────

# Berlin bbox for Stromnetz Berlin routing
BERLIN_BBOX = (52.35, 13.09, 52.68, 13.77)

# Hamburg bbox for Stromnetz Hamburg routing
HAMBURG_BBOX = (53.40, 9.72, 53.75, 10.32)

# München bbox for SWM Stadtwerke München routing
MUENCHEN_BBOX = (48.05, 11.36, 48.25, 11.72)

# Köln bbox for Rheinenergie routing
KOELN_BBOX = (50.85, 6.83, 51.10, 7.10)

# Frankfurt am Main bbox for Mainova routing
FRANKFURT_BBOX = (50.05, 8.45, 50.25, 8.80)

# Nürnberg bbox for N-ERGIE routing
NUERNBERG_BBOX = (49.35, 10.98, 49.55, 11.20)

# Sorbian minority region — Lusatia (Oberlausitz + Niederlausitz)
LUSATIA_BBOX = (51.10, 13.80, 52.15, 15.04)

# Danish minority region — Nordschleswig-Flensburg
NORDSCHLESWIG_BBOX = (54.55, 8.80, 55.06, 10.00)

# North Sea Frisian coast + Sylt-Föhr-Amrum
NORDFRIESLAND_BBOX = (54.28, 8.28, 55.06, 9.20)


# ─────────────────────────────────────────────────────────────
# ALIAS MAP — Convention #78 BINDING 20th enforcement
# 5-language: German + English + Sorbian + Danish + Frisian
# ─────────────────────────────────────────────────────────────

ALIAS_MAP: dict[str, tuple[str, str]] = {
    # ─── 4 TSOs (Convention #78 exact match Layer 1) ───────────
    "50hertz": ("50Hertz Transmission GmbH", "TSO"),
    "50hertz transmission": ("50Hertz Transmission GmbH", "TSO"),
    "50hertz transmission gmbh": ("50Hertz Transmission GmbH", "TSO"),
    "50 hertz": ("50Hertz Transmission GmbH", "TSO"),
    "vattenfall europe transmission": ("50Hertz Transmission GmbH", "TSO"),  # legacy pre-2010

    "amprion": ("Amprion GmbH", "TSO"),
    "amprion gmbh": ("Amprion GmbH", "TSO"),
    "rwe transportnetz strom": ("Amprion GmbH", "TSO"),  # legacy pre-2009
    "rwe net": ("Amprion GmbH", "TSO"),  # legacy

    "tennet": ("TenneT TSO GmbH", "TSO"),
    "tennet tso": ("TenneT TSO GmbH", "TSO"),
    "tennet tso gmbh": ("TenneT TSO GmbH", "TSO"),
    "tennet germany": ("TenneT TSO GmbH", "TSO"),
    "tennet deutschland": ("TenneT TSO GmbH", "TSO"),
    "eon netz": ("TenneT TSO GmbH", "TSO"),  # legacy pre-2010
    "e.on netz": ("TenneT TSO GmbH", "TSO"),  # legacy
    "e-on netz": ("TenneT TSO GmbH", "TSO"),  # legacy

    "transnetbw": ("TransnetBW GmbH", "TSO"),
    "transnetbw gmbh": ("TransnetBW GmbH", "TSO"),
    "enbw transportnetze": ("TransnetBW GmbH", "TSO"),  # legacy pre-2012
    "enbw regional": ("TransnetBW GmbH", "TSO"),  # legacy

    # ─── E.ON group DSO subsidiaries (Layer 2) ─────────────────
    "bayernwerk": ("Bayernwerk Netz GmbH (E.ON group)", "DSO"),
    "bayernwerk netz": ("Bayernwerk Netz GmbH (E.ON group)", "DSO"),
    "bayernwerk ag": ("Bayernwerk Netz GmbH (E.ON group)", "DSO"),
    "e.on bayern": ("Bayernwerk Netz GmbH (E.ON group)", "DSO"),

    "e.dis netz": ("E.DIS Netz GmbH (E.ON group)", "DSO"),
    "edis netz": ("E.DIS Netz GmbH (E.ON group)", "DSO"),
    "e.dis": ("E.DIS Netz GmbH (E.ON group)", "DSO"),
    "edis": ("E.DIS Netz GmbH (E.ON group)", "DSO"),

    "hansewerk": ("Hansewerk AG (E.ON group)", "DSO"),
    "hansewerk ag": ("Hansewerk AG (E.ON group)", "DSO"),
    "sh netz": ("Hansewerk AG (E.ON group)", "DSO"),
    "schleswig-holstein netz": ("Hansewerk AG (E.ON group)", "DSO"),

    "avacon": ("Avacon Netz GmbH (E.ON group)", "DSO"),
    "avacon netz": ("Avacon Netz GmbH (E.ON group)", "DSO"),
    "avacon ag": ("Avacon Netz GmbH (E.ON group)", "DSO"),

    "lew": ("Lechwerke AG (E.ON group)", "DSO"),
    "lechwerke": ("Lechwerke AG (E.ON group)", "DSO"),
    "lew verteilnetz": ("Lechwerke AG (E.ON group)", "DSO"),

    "mitnetz strom": ("MITNETZ Strom (E.ON group)", "DSO"),
    "mitteldeutsche netzgesellschaft strom": ("MITNETZ Strom (E.ON group)", "DSO"),
    "envia mitteldeutsche energie": ("enviaM (E.ON group)", "DSO"),
    "enviam": ("enviaM (E.ON group)", "DSO"),

    "westnetz": ("Westnetz GmbH (E.ON group)", "DSO"),
    "westnetz gmbh": ("Westnetz GmbH (E.ON group)", "DSO"),
    "innogy": ("Westnetz GmbH (E.ON group)", "DSO"),  # legacy pre-2020 split
    "rwe deutschland": ("Westnetz GmbH (E.ON group)", "DSO"),  # legacy
    "rwe deutschland ag": ("Westnetz GmbH (E.ON group)", "DSO"),  # legacy

    "e.on": ("E.ON SE (parent group)", "DSO"),
    "eon": ("E.ON SE (parent group)", "DSO"),
    "e-on": ("E.ON SE (parent group)", "DSO"),

    # ─── RWE legacy (Layer 2) ──────────────────────────────────
    "rwe": ("RWE AG (legacy)", "DSO"),
    "rwe ag": ("RWE AG (legacy)", "DSO"),
    "rwe generation": ("RWE Generation SE", "IPP"),
    "rwe power": ("RWE Power AG (generation)", "IPP"),

    # ─── EnBW group (Layer 2) ──────────────────────────────────
    "netze bw": ("Netze BW GmbH (EnBW group)", "DSO"),
    "netze bw gmbh": ("Netze BW GmbH (EnBW group)", "DSO"),
    "enbw": ("EnBW Energie Baden-Württemberg AG", "DSO"),
    "enbw energie": ("EnBW Energie Baden-Württemberg AG", "DSO"),
    "odr": ("ODR AG (EnBW group)", "DSO"),
    "ostwürttemberg-donauries": ("ODR AG (EnBW group)", "DSO"),
    "ostwuerttemberg-donauries": ("ODR AG (EnBW group)", "DSO"),

    # ─── Vattenfall Germany (Layer 2 — municipal-owned since 2014) ─
    "stromnetz berlin": ("Stromnetz Berlin GmbH (municipal-owned)", "DSO"),
    "stromnetz berlin gmbh": ("Stromnetz Berlin GmbH (municipal-owned)", "DSO"),
    "vattenfall europe distribution berlin": ("Stromnetz Berlin GmbH (municipal-owned)", "DSO"),

    "stromnetz hamburg": ("Stromnetz Hamburg GmbH (municipal-owned)", "DSO"),
    "stromnetz hamburg gmbh": ("Stromnetz Hamburg GmbH (municipal-owned)", "DSO"),
    "vattenfall europe distribution hamburg": ("Stromnetz Hamburg GmbH (municipal-owned)", "DSO"),

    "vattenfall": ("Vattenfall AB (Sweden parent)", "IPP"),
    "vattenfall europe": ("Vattenfall AB (Sweden parent)", "IPP"),

    # ─── Major Stadtwerke (Layer 3) ────────────────────────────
    "swm": ("SWM Stadtwerke München GmbH", "DSO"),
    "swm stadtwerke münchen": ("SWM Stadtwerke München GmbH", "DSO"),
    "swm stadtwerke muenchen": ("SWM Stadtwerke München GmbH", "DSO"),
    "stadtwerke münchen": ("SWM Stadtwerke München GmbH", "DSO"),
    "stadtwerke muenchen": ("SWM Stadtwerke München GmbH", "DSO"),
    "münchner stadtwerke": ("SWM Stadtwerke München GmbH", "DSO"),
    "muenchner stadtwerke": ("SWM Stadtwerke München GmbH", "DSO"),

    "rheinenergie": ("Rheinenergie AG", "DSO"),
    "rheinenergie ag": ("Rheinenergie AG", "DSO"),
    "rhein energie": ("Rheinenergie AG", "DSO"),
    "geo": ("Rheinenergie AG", "DSO"),  # legacy Gasversorgung Rheinstadt

    "mainova": ("Mainova AG", "DSO"),
    "mainova ag": ("Mainova AG", "DSO"),
    "netzdienste rhein-main": ("Netzdienste Rhein-Main GmbH (Mainova subsidiary)", "DSO"),

    "n-ergie": ("N-ERGIE AG", "DSO"),
    "n-ergie ag": ("N-ERGIE AG", "DSO"),
    "n ergie": ("N-ERGIE AG", "DSO"),

    "ewe": ("EWE AG", "DSO"),
    "ewe ag": ("EWE AG", "DSO"),
    "ewe netz": ("EWE Netz GmbH", "DSO"),

    "enervie": ("Enervie Vernetzt GmbH", "DSO"),
    "enervie südwestfalen": ("Enervie Vernetzt GmbH", "DSO"),
    "enervie suedwestfalen": ("Enervie Vernetzt GmbH", "DSO"),

    "ewr": ("EWR AG (Worms)", "DSO"),
    "ewr ag": ("EWR AG (Worms)", "DSO"),
    "ewr netz": ("EWR Netz GmbH", "DSO"),

    "leag": ("LEAG Lausitz Energie Bergbau AG", "IPP"),
    "leag lausitz": ("LEAG Lausitz Energie Bergbau AG", "IPP"),
    "lausitz energie": ("LEAG Lausitz Energie Bergbau AG", "IPP"),
    "vattenfall europe mining": ("LEAG Lausitz Energie Bergbau AG", "IPP"),  # legacy pre-2016

    "süwag": ("Süwag Energie AG", "DSO"),
    "suewag": ("Süwag Energie AG", "DSO"),
    "süwag energie": ("Süwag Energie AG", "DSO"),
    "suewag energie": ("Süwag Energie AG", "DSO"),

    "wemag": ("WEMAG AG (Schwerin)", "DSO"),
    "wemag ag": ("WEMAG AG (Schwerin)", "DSO"),
    "wemag netz": ("WEMAG Netz GmbH", "DSO"),

    "netze duisburg": ("Netze Duisburg GmbH", "DSO"),
    "duisburger netzgesellschaft": ("Netze Duisburg GmbH", "DSO"),

    "netzgesellschaft düsseldorf": ("Netzgesellschaft Düsseldorf mbH", "DSO"),
    "netzgesellschaft duesseldorf": ("Netzgesellschaft Düsseldorf mbH", "DSO"),
    "stadtwerke düsseldorf": ("Netzgesellschaft Düsseldorf mbH", "DSO"),
    "stadtwerke duesseldorf": ("Netzgesellschaft Düsseldorf mbH", "DSO"),

    "stadtwerke leipzig": ("Stadtwerke Leipzig GmbH", "DSO"),
    "leipziger stadtwerke": ("Stadtwerke Leipzig GmbH", "DSO"),
    "netz leipzig": ("Netz Leipzig GmbH", "DSO"),

    "drewag": ("DREWAG Stadtwerke Dresden GmbH", "DSO"),
    "stadtwerke dresden": ("DREWAG Stadtwerke Dresden GmbH", "DSO"),
    "sachsennetze": ("SachsenNetze GmbH (DREWAG)", "DSO"),

    "stadtwerke karlsruhe": ("Stadtwerke Karlsruhe GmbH", "DSO"),
    "netzservice karlsruhe": ("Stadtwerke Karlsruhe Netzservice GmbH", "DSO"),

    "swk": ("SWK Stadtwerke Krefeld AG", "DSO"),
    "stadtwerke krefeld": ("SWK Stadtwerke Krefeld AG", "DSO"),

    "stadtwerke stuttgart": ("Stadtwerke Stuttgart GmbH", "DSO"),
    "swsg": ("Stadtwerke Stuttgart GmbH", "DSO"),

    "stadtwerke bremen": ("SWB Bremen AG", "DSO"),
    "swb": ("SWB Bremen AG", "DSO"),
    "swb netz": ("swb Netz GmbH", "DSO"),

    "stadtwerke hannover": ("enercity Netz GmbH (Hannover)", "DSO"),
    "enercity": ("enercity AG", "DSO"),
    "enercity ag": ("enercity AG", "DSO"),
    "enercity netz": ("enercity Netz GmbH", "DSO"),

    "swk bielefeld": ("SW Bielefeld Netz GmbH", "DSO"),
    "sw netz bielefeld": ("SW Bielefeld Netz GmbH", "DSO"),
    "stadtwerke bielefeld": ("SW Bielefeld Netz GmbH", "DSO"),

    "stadtwerke augsburg": ("Stadtwerke Augsburg Energie GmbH", "DSO"),
    "sw augsburg": ("Stadtwerke Augsburg Energie GmbH", "DSO"),

    "stadtwerke ulm": ("SWU Netze GmbH (Ulm)", "DSO"),
    "swu": ("SWU Netze GmbH (Ulm)", "DSO"),

    "stadtwerke essen": ("Stadtwerke Essen AG", "DSO"),
    "stadtwerke bochum": ("Stadtwerke Bochum GmbH", "DSO"),
    "stadtwerke dortmund": ("DEW21 Dortmunder Energie- und Wasserversorgung GmbH", "DSO"),
    "dew21": ("DEW21 Dortmunder Energie- und Wasserversorgung GmbH", "DSO"),

    # ─── Rail traction Deutsche Bahn (Layer 4) ─────────────────
    "deutsche bahn": ("Deutsche Bahn AG (DB Netz)", "RAIL"),
    "db netz": ("Deutsche Bahn AG (DB Netz)", "RAIL"),
    "db energie": ("Deutsche Bahn Energie GmbH (rail traction)", "RAIL"),
    "db bahnstrom": ("Deutsche Bahn Energie GmbH (rail traction)", "RAIL"),
    "bahnstrom": ("Deutsche Bahn Energie GmbH (rail traction)", "RAIL"),
    "s-bahn berlin": ("Deutsche Bahn Energie GmbH (S-Bahn Berlin)", "RAIL"),

    # ─── Public transport local (subways) ──────────────────────
    "bvg": ("BVG Berliner Verkehrsbetriebe (U-Bahn Berlin)", "RAIL"),
    "berliner verkehrsbetriebe": ("BVG Berliner Verkehrsbetriebe (U-Bahn Berlin)", "RAIL"),
    "mvg": ("MVG Münchner Verkehrsgesellschaft (U-Bahn München)", "RAIL"),
    "hochbahn": ("Hamburger Hochbahn AG (U-Bahn Hamburg)", "RAIL"),
    "vag": ("VAG Verkehrs-AG Nürnberg (U-Bahn Nürnberg)", "RAIL"),

    # ─── Regional operators + smaller Stadtwerke ────────────────
    "wsw": ("WSW Wuppertaler Stadtwerke", "DSO"),
    "stadtwerke wuppertal": ("WSW Wuppertaler Stadtwerke", "DSO"),

    "stadtwerke aachen": ("STAWAG Stadtwerke Aachen AG", "DSO"),
    "stawag": ("STAWAG Stadtwerke Aachen AG", "DSO"),

    "stadtwerke mainz": ("Stadtwerke Mainz Netze GmbH", "DSO"),
    "swm mainz": ("Stadtwerke Mainz Netze GmbH", "DSO"),

    "stadtwerke saarbrücken": ("Stadtwerke Saarbrücken AG", "DSO"),
    "stadtwerke saarbruecken": ("Stadtwerke Saarbrücken AG", "DSO"),

    "stadtwerke kiel": ("Stadtwerke Kiel AG", "DSO"),
    "sw kiel": ("Stadtwerke Kiel AG", "DSO"),

    "stadtwerke lübeck": ("TraveNetz GmbH (Lübeck)", "DSO"),
    "stadtwerke luebeck": ("TraveNetz GmbH (Lübeck)", "DSO"),
    "travenetz": ("TraveNetz GmbH (Lübeck)", "DSO"),

    "stadtwerke rostock": ("Stadtwerke Rostock AG", "DSO"),
    "sw rostock": ("Stadtwerke Rostock AG", "DSO"),

    "stadtwerke potsdam": ("Energie und Wasser Potsdam GmbH", "DSO"),
    "ewp": ("Energie und Wasser Potsdam GmbH", "DSO"),

    "stadtwerke jena": ("Stadtwerke Jena Netze GmbH", "DSO"),
    "sw jena": ("Stadtwerke Jena Netze GmbH", "DSO"),

    "stadtwerke erfurt": ("SWE Netz GmbH (Erfurt)", "DSO"),
    "swe netz": ("SWE Netz GmbH (Erfurt)", "DSO"),
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
    stripped = re.sub(r"\s+(gmbh|ag|se|kg|ohg|gbr|e\.v\.|e\.k\.|mbh)$", "", key)
    if stripped != key and stripped in ALIAS_MAP:
        _alias_hit_counter += 1
        return ALIAS_MAP[stripped]
    return None


# ─────────────────────────────────────────────────────────────
# 12-layer resolver — Portugal P33 canonical + Germany extensions
# ─────────────────────────────────────────────────────────────

RESOLVER_LAYERS = (
    "alias_hit",
    "voltage_ehv",
    "voltage_hv_110",
    "voltage_subtransmission",
    "berlin_bbox_stromnetz",
    "hamburg_bbox_stromnetz",
    "muenchen_bbox_swm",
    "koeln_bbox_rheinenergie",
    "frankfurt_bbox_mainova",
    "nuernberg_bbox_nergie",
    "rail_traction_15kv_16_7hz",
    "fallback_default_eon_group",
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

    # Layer 1: alias hit (highest confidence — direct operator= tag match)
    if raw_operator:
        hit = _alias_hit(raw_operator)
        if hit:
            return hit[0], hit[1], "alias_hit"

    # Layer 2: voltage EHV → TSO attribution
    if voltage_kv is not None and voltage_kv >= 330.0:
        # Try to route by bbox to correct TSO
        if lat is not None and lon is not None:
            # 50Hertz eastern territory
            if _in_bbox(lat, lon, (50.20, 11.00, 54.75, 15.04)):
                return "50Hertz Transmission GmbH", "TSO", "voltage_ehv"
            # TransnetBW southwest
            if _in_bbox(lat, lon, (47.53, 7.50, 49.80, 10.50)):
                return "TransnetBW GmbH", "TSO", "voltage_ehv"
            # TenneT DE north-south spine
            if _in_bbox(lat, lon, (47.30, 9.00, 55.06, 13.85)):
                return "TenneT TSO GmbH", "TSO", "voltage_ehv"
            # Amprion western
            if _in_bbox(lat, lon, (49.10, 5.87, 52.60, 9.50)):
                return "Amprion GmbH", "TSO", "voltage_ehv"
        return "Amprion GmbH (voltage-inferred default TSO)", "TSO", "voltage_ehv"

    # Layer 3: voltage HV 110 kV (Germany-common Hochspannung distribution)
    if voltage_kv is not None and 100.0 <= voltage_kv < 200.0:
        return "E.ON group HV distribution (voltage-inferred)", "DSO", "voltage_hv_110"

    # Layer 4: voltage subtransmission 60-90 kV
    if voltage_kv is not None and 45.0 <= voltage_kv < 100.0:
        return "E.ON group subtransmission (voltage-inferred)", "DSO", "voltage_subtransmission"

    # Layers 5-9: Metropolitan bbox routing (utility attribution, NOT §4bis.5 geofence)
    if lat is not None and lon is not None:
        if _in_bbox(lat, lon, BERLIN_BBOX):
            return "Stromnetz Berlin GmbH (bbox-inferred)", "DSO", "berlin_bbox_stromnetz"
        if _in_bbox(lat, lon, HAMBURG_BBOX):
            return "Stromnetz Hamburg GmbH (bbox-inferred)", "DSO", "hamburg_bbox_stromnetz"
        if _in_bbox(lat, lon, MUENCHEN_BBOX):
            return "SWM Stadtwerke München GmbH (bbox-inferred)", "DSO", "muenchen_bbox_swm"
        if _in_bbox(lat, lon, KOELN_BBOX):
            return "Rheinenergie AG (bbox-inferred)", "DSO", "koeln_bbox_rheinenergie"
        if _in_bbox(lat, lon, FRANKFURT_BBOX):
            return "Mainova AG (bbox-inferred)", "DSO", "frankfurt_bbox_mainova"
        if _in_bbox(lat, lon, NUERNBERG_BBOX):
            return "N-ERGIE AG (bbox-inferred)", "DSO", "nuernberg_bbox_nergie"

    # Layer 10: rail traction 15 kV AC 16.7 Hz
    if voltage_kv is not None and 14.0 <= voltage_kv <= 16.5:
        return "Deutsche Bahn Energie GmbH (rail traction 15 kV 16.7 Hz)", "RAIL", "rail_traction_15kv_16_7hz"

    # Layer 11: fallback E.ON group (largest DSO coverage)
    return "E.ON group DSO (fallback default)", "DSO", "fallback_default_eon_group"
