"""UK v4.23 substation ingestion base module — Wave 4 P31.

Shared infrastructure for OSM Overpass fetch + provenance + resolver +
alias normalisation across UK 5-language scripts (English + Welsh +
Scots Gaelic + Irish + Cornish) + Wave 4 CORRECTED compact schema
emission helpers.

Convention preservation:
- #7 Data-Layer Anchoring (documented proxy per country hazard baselines)
- #23 Provenance pinning (SHA-256 raw payload + audit sidecar)
- #36 Cross-border filter (3.0 km tolerance uk entry)
- #41 Line-substation parity (target [1.5-5.0] healthy band)
- #56 Visibly-honest degradation (partial-fetch preserved end-to-end)
- #60 Non-commercial provenance (OSM ODbL + Ofgem RIIO-ED2 + NIE public)
- #78 BINDING 13th enforcement — English + Welsh + Scots Gaelic + Irish + Cornish
- #78 §4bis.5 Layer 3 9TH ENFORCEMENT candidate — London UKPN LPN
"""
from __future__ import annotations

import hashlib
import json
import logging
import math
import re
import time
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from ...utils.tolerance import resolve_boundary_tolerance_km
from typing import Any, Iterable, Optional

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
COUNTRY_SLUG = "uk"
COUNTRY_CODE = "gb"  # ISO 3166-1 alpha-2

# ─── Convention #78 §4bis.5 Layer 3 9TH ENFORCEMENT candidate — London geofence ───
LONDON_UKPN_LPN_BBOX = {
    "lat_min": 51.28, "lat_max": 51.72,
    "lon_min": -0.51, "lon_max": 0.34,
    "operator_canonical": "UKPN LPN",
    "operator_english": "UK Power Networks London Power Networks",
    "role": "LONDON_METROPOLITAN_DSO_UKPN_LPN",
    "customers_millions": 2.4,
}

# ─── Isle of Man Crown Dependency carve-out (Layer 4d) ───
ISLE_OF_MAN_BBOX = {
    "lat_min": 54.03, "lat_max": 54.42,
    "lon_min": -4.85, "lon_max": -4.30,
    "operator_canonical": "Manx Utilities",
    "role": "CROWN_DEPENDENCY_ISLE_OF_MAN_MANX_UTILITIES",
}

# ─── Channel Islands Crown Dependencies carve-out (Layer 4d) ───
CHANNEL_ISLANDS_BBOX = {
    "lat_min": 49.15, "lat_max": 49.75,
    "lon_min": -2.70, "lon_max": -1.90,
    "operator_canonical": "Channel Islands Utilities",
    "role": "CROWN_DEPENDENCY_CHANNEL_ISLANDS_JEC_GEL",
}

# ─── Northern Ireland carve-out (Layer 4e — separate market I-SEM) ───
NORTHERN_IRELAND_BBOX = {
    "lat_min": 54.02, "lat_max": 55.31,
    "lon_min": -8.18, "lon_max": -5.42,
    "operator_canonical": "NIE Networks",
    "operator_tso": "SONI",
    "role": "NORTHERN_IRELAND_I_SEM_NIE_SONI",
    "note": "Separate market I-SEM with ROI; NIE Networks (DNO+TNO) owned by ROI ESB Group",
}

# ─── Voltage thresholds ───
TSO_MIN_KV = 275.0  # UK TSO threshold — 400 kV (England/Wales) + 275 kV (Scotland) backbone
EHV_KV = 400.0      # English/Welsh EHV backbone
LEGACY_SUBTRANSMISSION_KV = 132.0  # UK-specific pre-1990 subtransmission tier

# ─── 14-DNO licence area → DNO group map (Layer 3b admin resolver) ───
# Not directly indexed by province — UK OSM tags often use region names
DNO_REGION_MAP: dict[str, str] = {
    # ── UKPN — London + South East + East England (3 areas) ──
    "London": "UKPN",
    "Greater London": "UKPN",
    "South East": "UKPN",
    "Kent": "UKPN",
    "East Sussex": "UKPN",
    "West Sussex": "UKPN",
    "Surrey": "UKPN",
    "Essex": "UKPN",
    "Cambridgeshire": "UKPN",
    "Norfolk": "UKPN",
    "Suffolk": "UKPN",
    "Bedfordshire": "UKPN",
    "Hertfordshire": "UKPN",
    # ── NGED — Midlands + South West + South Wales (4 areas) ──
    "West Midlands": "NGED",
    "East Midlands": "NGED",
    "Warwickshire": "NGED",
    "Worcestershire": "NGED",
    "Herefordshire": "NGED",
    "Staffordshire": "NGED",
    "Nottinghamshire": "NGED",
    "Leicestershire": "NGED",
    "Northamptonshire": "NGED",
    "Rutland": "NGED",
    "Derbyshire": "NGED",
    "Lincolnshire": "NGED",
    "South West": "NGED",
    "Devon": "NGED",
    "Cornwall": "NGED",  # UK-Cornish 5-language enforcement region
    "Somerset": "NGED",
    "Dorset": "NGED",
    "Wiltshire": "NGED",
    "Gloucestershire": "NGED",
    "Bristol": "NGED",
    "Carmarthenshire": "NGED",
    "Ceredigion": "NGED",
    "Pembrokeshire": "NGED",
    "Powys": "NGED",  # partial (South Powys)
    "Monmouthshire": "NGED",
    "South Wales": "NGED",
    # ── SPEN — Central+Southern Scotland + Merseyside + North Wales (2 areas) ──
    "Scotland Central": "SPEN",
    "Scotland Southern": "SPEN",
    "Glasgow": "SPEN",
    "Edinburgh": "SPEN",
    "Dumfries and Galloway": "SPEN",
    "Scottish Borders": "SPEN",
    "Merseyside": "SPEN",
    "Cheshire": "SPEN",
    "North Wales": "SPEN",
    "Gwynedd": "SPEN",
    "Anglesey": "SPEN",  # Ynys Môn
    "Conwy": "SPEN",
    "Denbighshire": "SPEN",
    "Flintshire": "SPEN",
    "Wrexham": "SPEN",
    # ── SSEN — Northern Scotland + Southern England (2 areas) ──
    "Highland": "SSEN",
    "Aberdeenshire": "SSEN",
    "Moray": "SSEN",
    "Perth and Kinross": "SSEN",
    "Angus": "SSEN",
    "Fife": "SSEN",
    "Argyll and Bute": "SSEN",
    "Stirling": "SSEN",
    "Shetland": "SSEN",
    "Orkney": "SSEN",
    "Outer Hebrides": "SSEN",
    "Western Isles": "SSEN",
    "Southern England": "SSEN",
    "Hampshire": "SSEN",
    "Berkshire": "SSEN",
    "Oxfordshire": "SSEN",
    "Isle of Wight": "SSEN",
    # ── ENW — North West England ──
    "North West": "ENW",
    "Cumbria": "ENW",
    "Lancashire": "ENW",
    "Greater Manchester": "ENW",
    # ── NPG — North East + Yorkshire (2 areas) ──
    "North East": "NPG",
    "Northumberland": "NPG",
    "County Durham": "NPG",
    "Tyne and Wear": "NPG",
    "Yorkshire": "NPG",
    "West Yorkshire": "NPG",
    "South Yorkshire": "NPG",
    "East Yorkshire": "NPG",
    "North Yorkshire": "NPG",
    "Humberside": "NPG",
    # ── Northern Ireland (I-SEM cross-border ROI) ──
    "Northern Ireland": "NIE Networks",
    "Antrim": "NIE Networks",
    "Armagh": "NIE Networks",
    "Down": "NIE Networks",
    "Fermanagh": "NIE Networks",
    "Londonderry": "NIE Networks",
    "Derry": "NIE Networks",
    "Tyrone": "NIE Networks",
    "Belfast": "NIE Networks",
    # ── Crown Dependencies ──
    "Isle of Man": "Manx Utilities",
    "Jersey": "Jersey Electricity",
    "Guernsey": "Guernsey Electricity",
}


def _normalize_operator(name: str) -> str:
    """NFC normalization + strip + lowercase for alias matching.

    Preserves Welsh (ŵ ŷ â ê î ô û) + Scots Gaelic (à è ì ò ù) +
    Irish (á é í ó ú) + Cornish diacritics per Convention #78 BINDING
    13th enforcement.
    """
    if not name:
        return ""
    normalized = unicodedata.normalize("NFC", name)
    return normalized.strip().lower()


# ─── Convention #78 BINDING 13th enforcement — UK alias map (~110 entries) ───
_ALIAS_MAP: dict[str, str] = {
    # ═══ National Grid ESO (post-2019 unbundled TSO, 2024 nationalized) ═══
    _normalize_operator("National Grid ESO"): "National Grid ESO",
    _normalize_operator("NGESO"): "National Grid ESO",
    _normalize_operator("ESO"): "National Grid ESO",
    _normalize_operator("National Grid Electricity System Operator"): "National Grid ESO",
    _normalize_operator("Great Britain ESO"): "National Grid ESO",
    _normalize_operator("GB Electricity System Operator"): "National Grid ESO",

    # ═══ National Grid Electricity Transmission (NGET) ═══
    _normalize_operator("National Grid Electricity Transmission"): "NGET",
    _normalize_operator("NGET"): "NGET",
    _normalize_operator("National Grid ET"): "NGET",
    _normalize_operator("National Grid plc"): "NGET",
    _normalize_operator("National Grid"): "NGET",  # ambiguous — historical default → NGET

    # ═══ Scottish Transmission (SPT + SHE-T) ═══
    _normalize_operator("Scottish Power Transmission"): "SPT",
    _normalize_operator("SPT"): "SPT",
    _normalize_operator("ScottishPower Transmission"): "SPT",
    _normalize_operator("Scottish Hydro Electric Transmission"): "SHE-T",
    _normalize_operator("SHE-T"): "SHE-T",
    _normalize_operator("SHET"): "SHE-T",
    _normalize_operator("SSEN Transmission"): "SHE-T",
    _normalize_operator("Scottish and Southern Electricity Networks Transmission"): "SHE-T",
    # Scots Gaelic variant
    _normalize_operator("Còmhdhail Dealanach Uisge Alba"): "SHE-T",

    # ═══ UK Power Networks (UKPN) — London + SE + East ═══
    _normalize_operator("UK Power Networks"): "UKPN",
    _normalize_operator("UKPN"): "UKPN",
    _normalize_operator("UK Power Networks Ltd"): "UKPN",
    _normalize_operator("UK Power Networks Limited"): "UKPN",
    _normalize_operator("EDF Energy Networks"): "UKPN",  # pre-2010 predecessor
    _normalize_operator("EDF Energy"): "UKPN",  # ambiguous but historically → distribution → UKPN
    _normalize_operator("London Power Networks"): "UKPN LPN",  # sub-tag for §4bis.5 candidate
    _normalize_operator("LPN"): "UKPN LPN",
    _normalize_operator("UKPN LPN"): "UKPN LPN",
    _normalize_operator("Eastern Power Networks"): "UKPN EPN",
    _normalize_operator("EPN"): "UKPN EPN",
    _normalize_operator("UKPN EPN"): "UKPN EPN",
    _normalize_operator("South Eastern Power Networks"): "UKPN SPN",
    _normalize_operator("SPN"): "UKPN SPN",
    _normalize_operator("UKPN SPN"): "UKPN SPN",

    # ═══ National Grid Electricity Distribution (NGED, ex-WPD) ═══
    _normalize_operator("National Grid Electricity Distribution"): "NGED",
    _normalize_operator("NGED"): "NGED",
    _normalize_operator("National Grid ED"): "NGED",
    _normalize_operator("Western Power Distribution"): "NGED",  # pre-June-2022 rebrand
    _normalize_operator("WPD"): "NGED",
    _normalize_operator("WPD Midlands"): "NGED",
    _normalize_operator("WPD South Wales"): "NGED",
    _normalize_operator("WPD South West"): "NGED",
    _normalize_operator("PPL Global"): "NGED",  # pre-2021 US parent
    # Welsh variant
    _normalize_operator("Dosbarthu Trydan Grid Cenedlaethol"): "NGED",

    # ═══ SP Energy Networks (SPEN, ScottishPower Iberdrola) ═══
    _normalize_operator("SP Energy Networks"): "SPEN",
    _normalize_operator("SPEN"): "SPEN",
    _normalize_operator("ScottishPower Energy Networks"): "SPEN",
    _normalize_operator("Scottish Power Networks"): "SPEN",
    _normalize_operator("SP Distribution"): "SPEN",  # Scotland licence area
    _normalize_operator("SP Manweb"): "SPEN",  # Merseyside+Cheshire+N Wales licence area
    _normalize_operator("Manweb"): "SPEN",  # historical name
    _normalize_operator("Iberdrola"): "SPEN",  # Spanish parent
    _normalize_operator("ScottishPower"): "SPEN",
    # Scots Gaelic variant
    _normalize_operator("Lìonraidhean Cumhachd Alba"): "SPEN",

    # ═══ Scottish and Southern Electricity Networks (SSEN) ═══
    _normalize_operator("Scottish and Southern Electricity Networks"): "SSEN",
    _normalize_operator("SSEN"): "SSEN",
    _normalize_operator("SSEN Distribution"): "SSEN",
    _normalize_operator("SSEN Northern"): "SSEN",
    _normalize_operator("SSEN Southern"): "SSEN",
    _normalize_operator("SSE Networks"): "SSEN",
    _normalize_operator("Scottish Hydro Electric"): "SSEN",  # historical N Scotland
    _normalize_operator("Southern Electric"): "SSEN",  # historical Southern England
    _normalize_operator("SSE plc"): "SSEN",
    _normalize_operator("SSE"): "SSEN",  # ambiguous but → distribution
    # Scots Gaelic variant
    _normalize_operator("Lìonraidhean Dealanach Alba is a Deas"): "SSEN",

    # ═══ Electricity North West (ENW) ═══
    _normalize_operator("Electricity North West"): "ENW",
    _normalize_operator("ENW"): "ENW",
    _normalize_operator("Electricity North West Limited"): "ENW",
    _normalize_operator("NORWEB"): "ENW",  # historical pre-1990

    # ═══ Northern Powergrid (NPG) ═══
    _normalize_operator("Northern Powergrid"): "NPG",
    _normalize_operator("NPG"): "NPG",
    _normalize_operator("Northern Electric"): "NPG",  # historical pre-1990
    _normalize_operator("YEB"): "NPG",  # Yorkshire Electricity Board historical
    _normalize_operator("Yorkshire Electricity"): "NPG",  # historical

    # ═══ Northern Ireland (SONI + NIE Networks) ═══
    _normalize_operator("SONI"): "SONI",
    _normalize_operator("System Operator for Northern Ireland"): "SONI",
    _normalize_operator("SONI Ltd"): "SONI",
    # Irish variant
    _normalize_operator("Feidhmeoir Chóras do Thuaisceart Éireann"): "SONI",
    _normalize_operator("NIE Networks"): "NIE Networks",
    _normalize_operator("Northern Ireland Electricity Networks"): "NIE Networks",
    _normalize_operator("NIE"): "NIE Networks",
    _normalize_operator("Northern Ireland Electricity"): "NIE Networks",
    _normalize_operator("ESB Networks NI"): "NIE Networks",  # ROI parent brand
    # Irish variant
    _normalize_operator("Líonraí Leictreachais Thuaisceart Éireann"): "NIE Networks",

    # ═══ Crown Dependencies ═══
    _normalize_operator("Manx Utilities"): "Manx Utilities",
    _normalize_operator("Manx Electricity Authority"): "Manx Utilities",
    _normalize_operator("MEA"): "Manx Utilities",
    _normalize_operator("Jersey Electricity"): "Jersey Electricity",
    _normalize_operator("Jersey Electricity Company"): "Jersey Electricity",
    _normalize_operator("JEC"): "Jersey Electricity",
    _normalize_operator("Compagnie de l'Électricité de Jersey"): "Jersey Electricity",  # Jèrriais French
    _normalize_operator("Guernsey Electricity"): "Guernsey Electricity",
    _normalize_operator("Guernsey Electricity Limited"): "Guernsey Electricity",
    _normalize_operator("GEL"): "Guernsey Electricity",

    # ═══ Rail traction (Layer 4c) ═══
    _normalize_operator("Network Rail"): "Network Rail",
    _normalize_operator("Network Rail Infrastructure Limited"): "Network Rail",
    _normalize_operator("Network Rail Traction Power"): "Network Rail",
    _normalize_operator("Railtrack"): "Network Rail",  # pre-2002 predecessor
    _normalize_operator("British Rail"): "Network Rail",  # historical
    _normalize_operator("BR"): "Network Rail",
    _normalize_operator("Transport for London"): "TfL",
    _normalize_operator("TfL"): "TfL",
    _normalize_operator("London Underground"): "TfL",
    _normalize_operator("Elizabeth Line"): "TfL",
    _normalize_operator("Crossrail"): "TfL",  # pre-Elizabeth Line name

    # ═══ Nuclear (Layer 4b generation carve-out) ═══
    _normalize_operator("EDF Energy Generation"): "EDF Energy Generation",
    _normalize_operator("EDF Energy UK"): "EDF Energy Generation",
    _normalize_operator("Électricité de France UK"): "EDF Energy Generation",
    _normalize_operator("Sizewell B"): "EDF Energy Generation",
    _normalize_operator("Sizewell C"): "EDF Energy Generation",
    _normalize_operator("Hinkley Point"): "EDF Energy Generation",
    _normalize_operator("Hinkley Point B"): "EDF Energy Generation",
    _normalize_operator("Hinkley Point C"): "EDF Energy Generation",
    _normalize_operator("Heysham"): "EDF Energy Generation",
    _normalize_operator("Hartlepool"): "EDF Energy Generation",
    _normalize_operator("Torness"): "EDF Energy Generation",
    _normalize_operator("Dungeness B"): "EDF Energy Generation",
    _normalize_operator("Urenco"): "Urenco",
    _normalize_operator("Urenco UK"): "Urenco",
    _normalize_operator("Urenco Capenhurst"): "Urenco",

    # ═══ Cross-border interconnector consortiums (informational routing) ═══
    _normalize_operator("IFA"): "NGET",  # IFA → default to NGET UK side
    _normalize_operator("Interconnexion France-Angleterre"): "NGET",
    _normalize_operator("IFA1"): "NGET",
    _normalize_operator("IFA2"): "NGET",
    _normalize_operator("BritNed"): "NGET",
    _normalize_operator("Nemo Link"): "NGET",
    _normalize_operator("North Sea Link"): "NGET",
    _normalize_operator("NSL"): "NGET",
    _normalize_operator("Viking Link"): "NGET",
    _normalize_operator("Greenlink"): "NGET",
    _normalize_operator("Greenlink Interconnector"): "NGET",
    _normalize_operator("Getlink"): "Getlink ElecLink",
    _normalize_operator("Eurotunnel"): "Getlink ElecLink",
    _normalize_operator("ElecLink"): "Getlink ElecLink",
    _normalize_operator("Getlink SE"): "Getlink ElecLink",

    # ═══ Cross-border partner operators (route to UK TSO) ═══
    _normalize_operator("RTE"): "NGET",  # French TSO → route to UK NGET
    _normalize_operator("Réseau de transport d'électricité"): "NGET",
    _normalize_operator("TenneT"): "NGET",  # Dutch TSO → UK NGET
    _normalize_operator("Elia"): "NGET",  # Belgian TSO → UK NGET
    _normalize_operator("Statnett"): "NGET",  # Norwegian TSO → UK NGET
    _normalize_operator("Energinet"): "NGET",  # Danish TSO → UK NGET
    _normalize_operator("EirGrid"): "SONI",  # Irish TSO → route to SONI (I-SEM cross-border partner)
}


def normalize_operator_name(raw: Optional[str]) -> tuple[Optional[str], bool]:
    """Return (canonical_name, was_alias_normalised).

    Per Convention #78 BINDING 13th enforcement — NFC normalization
    for English + Welsh + Scots Gaelic + Irish + Cornish scripts.
    """
    if not raw:
        return (None, False)
    norm_key = _normalize_operator(raw)
    if norm_key in _ALIAS_MAP:
        canonical = _ALIAS_MAP[norm_key]
        was_normalised = _normalize_operator(canonical) != norm_key
        return (canonical, was_normalised)
    return (raw, False)


def is_in_bbox(lat: float, lon: float, bbox: dict) -> bool:
    """Convention #78 §4bis.5 Layer 3 geofence check."""
    return (
        bbox["lat_min"] <= lat <= bbox["lat_max"]
        and bbox["lon_min"] <= lon <= bbox["lon_max"]
    )


def resolve_owner_via_admin(region: Optional[str]) -> Optional[str]:
    """Layer 3b admin-based resolver (14-DNO licence area → DNO group).

    Returns None if region unknown (Layer 5 fallback to NGET catch-all).
    """
    if not region:
        return None
    return DNO_REGION_MAP.get(region)


@dataclass
class OwnerResolverResult:
    """Per-substation owner attribution decision + provenance.

    Layer routing (8-layer resolver + admin fallback):
    - Layer 0: Direct OSM operator= tag (Convention #78 alias-normalise)
    - Layer 1: TSO threshold (voltage ≥ 275 kV) → NGET/SPT/SHE-T
    - Layer 3a: Convention #78 §4bis.5 London UKPN LPN geofence
    - Layer 3b: 14-DNO admin-based resolver
    - Layer 4a: Nuclear name-match (Sizewell/Hinkley/Heysham/etc.)
    - Layer 4b: Rail traction (Network Rail/TfL)
    - Layer 4c: Isle of Man Crown Dependency (Manx Utilities)
    - Layer 4d: Channel Islands Crown Dependencies (JEC/GEL)
    - Layer 4e: Northern Ireland I-SEM (NIE Networks/SONI)
    - Layer 5: NGET Layer 6 catch-all default
    """
    canonical_name: str
    provenance: str
    was_alias_normalised: bool = False
    convention_78_4bis_5_geofence_hit: Optional[str] = None


def resolve_owner(
    *,
    osm_operator: Optional[str],
    voltage_kv: Optional[float],
    lat: Optional[float],
    lon: Optional[float],
    region: Optional[str],
    name: Optional[str] = None,
) -> OwnerResolverResult:
    """Full 9-layer resolver dispatch for UK.

    Order matters — first-match wins per Nordic + Turkey precedent.
    """
    # ── Layer 0: Direct OSM operator= tag ──
    if osm_operator:
        canonical, was_normalised = normalize_operator_name(osm_operator)
        if canonical:
            provenance = (
                "osm_operator_tag_direct_alias_normalised"
                if was_normalised
                else "osm_operator_tag_direct"
            )
            return OwnerResolverResult(
                canonical_name=canonical,
                provenance=provenance,
                was_alias_normalised=was_normalised,
            )

    # ── Layer 4a: Nuclear name-match ──
    if name:
        name_norm = _normalize_operator(name)
        nuclear_markers = ["sizewell", "hinkley", "heysham", "hartlepool", "torness", "dungeness", "urenco", "capenhurst"]
        if any(m in name_norm for m in nuclear_markers):
            return OwnerResolverResult(
                canonical_name="EDF Energy Generation",
                provenance="region_jurisdiction_layer_4a_nuclear_name_match",
            )

    # ── Layer 4b: Rail traction name-match ──
    if name:
        name_norm = _normalize_operator(name)
        if any(m in name_norm for m in ["network rail", "railway", "elizabeth line", "underground"]):
            return OwnerResolverResult(
                canonical_name="Network Rail",
                provenance="region_jurisdiction_layer_4b_rail_traction_name_match",
            )

    if lat is not None and lon is not None:
        # ── Layer 4c: Isle of Man Crown Dependency ──
        if is_in_bbox(lat, lon, ISLE_OF_MAN_BBOX):
            return OwnerResolverResult(
                canonical_name="Manx Utilities",
                provenance="region_jurisdiction_layer_4c_isle_of_man_crown_dependency_bbox",
            )

        # ── Layer 4d: Channel Islands Crown Dependencies ──
        if is_in_bbox(lat, lon, CHANNEL_ISLANDS_BBOX):
            return OwnerResolverResult(
                canonical_name="Channel Islands Utilities",
                provenance="region_jurisdiction_layer_4d_channel_islands_crown_dependency_bbox",
            )

        # ── Layer 4e: Northern Ireland (I-SEM separate market) ──
        if is_in_bbox(lat, lon, NORTHERN_IRELAND_BBOX):
            # Distinguish TSO ≥ 110 kV vs DNO
            if voltage_kv is not None and voltage_kv >= 110.0:
                return OwnerResolverResult(
                    canonical_name="SONI",
                    provenance="region_jurisdiction_layer_4e_northern_ireland_SONI_tso_via_bbox",
                )
            return OwnerResolverResult(
                canonical_name="NIE Networks",
                provenance="region_jurisdiction_layer_4e_northern_ireland_NIE_networks_via_bbox",
            )

        # ── Layer 3a: Convention #78 §4bis.5 9TH ENFORCEMENT — London UKPN LPN ──
        if is_in_bbox(lat, lon, LONDON_UKPN_LPN_BBOX):
            return OwnerResolverResult(
                canonical_name="UKPN LPN",
                provenance="region_jurisdiction_layer_3_4bis5_9th_enforcement_UKPN_LPN_via_London_geofence",
                convention_78_4bis_5_geofence_hit="UKPN LPN",
            )

    # ── Layer 1: TSO threshold (voltage ≥ 275 kV) ──
    if voltage_kv is not None and voltage_kv >= TSO_MIN_KV:
        # Distinguish English/Welsh NGET vs Scottish SPT/SHE-T by lat
        if lat is not None and lat >= 55.0:  # Scotland lat threshold
            # Northern Scotland >= 57°N → SHE-T; South of that → SPT
            if lat >= 57.0:
                return OwnerResolverResult(
                    canonical_name="SHE-T",
                    provenance="region_jurisdiction_layer_1_SHE_T_scottish_northern_tso_ge_275kv",
                )
            return OwnerResolverResult(
                canonical_name="SPT",
                provenance="region_jurisdiction_layer_1_SPT_scottish_southern_tso_ge_275kv",
            )
        return OwnerResolverResult(
            canonical_name="NGET",
            provenance="region_jurisdiction_layer_1_NGET_english_welsh_tso_ge_275kv",
        )

    # ── Layer 3b: 14-DNO admin-based resolver ──
    dno = resolve_owner_via_admin(region)
    if dno:
        return OwnerResolverResult(
            canonical_name=dno,
            provenance=f"region_jurisdiction_layer_3b_{dno.replace(' ', '_')}_via_admin_map",
        )

    # ── Layer 5: NGET Layer 6 catch-all default ──
    return OwnerResolverResult(
        canonical_name="NGET",
        provenance="region_jurisdiction_layer_6_NGET_catch_all_default",
    )


# ═══════════════════════════════════════════════════════════════
# WAVE 4 CORRECTED ARCHITECTURE — Compact schema emission helpers
# ═══════════════════════════════════════════════════════════════
# Post-Turkey schema-bug lesson: emit canonical `{s, l, a}` schema
# from the start with proper OSM way coord resolution.


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in meters."""
    R = 6_371_000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlmb / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def build_sub_spatial_index(s_dict: dict[str, dict]) -> list[tuple[str, float, float]]:
    """Convert compact `s` dict to spatial-index list for matching.

    Returns list of (sub_id_str, lon, lat) tuples.
    """
    return [(sid, entry.get('x', 0.0), entry.get('y', 0.0)) for sid, entry in s_dict.items()]


def find_nearest_sub(
    lon: float,
    lat: float,
    spatial_index: list[tuple[str, float, float]],
    *,
    radius_m: float = 500,
) -> Optional[str]:
    """Find nearest substation within radius_m. Returns sub_id_str or None.

    LEGACY O(N) linear scan — use build_grid_index + find_nearest_sub_gridded
    for large N (>1000) instead.
    """
    best_id = None
    best_d = float("inf")
    for sid, sx, sy in spatial_index:
        d = haversine_m(lat, lon, sy, sx)
        if d < radius_m and d < best_d:
            best_d = d
            best_id = sid
    return best_id


# ═══════════════════════════════════════════════════════════════
# GRID-BASED SPATIAL INDEX — O(1) per-query nearest-neighbor
# for UK P31 60,128 subs × 201,976 lines merge
# ═══════════════════════════════════════════════════════════════
# Bucket subs by 0.1° cells (~11 km) — check same cell + 8 neighbors
# for nearest-neighbor query. Reduces 60,128 sub scan → ~100-200 subs per query.
# Speedup: 300-600× for line endpoint matching.

GRID_CELL_DEG = 0.1  # ~11 km cell size


def build_grid_index(spatial_index: list[tuple[str, float, float]]) -> dict:
    """Build grid-based spatial index for O(1) nearest-neighbor queries.

    Input: list of (sub_id_str, lon, lat) tuples (compact schema convention).
    Returns: dict {(cell_lat_int, cell_lon_int): [(sub_id, lon, lat), ...]}
    """
    grid: dict = {}
    for sid, lon, lat in spatial_index:
        cell_lat = int(lat / GRID_CELL_DEG)
        cell_lon = int(lon / GRID_CELL_DEG)
        grid.setdefault((cell_lat, cell_lon), []).append((sid, lon, lat))
    return grid


def find_nearest_sub_gridded(
    lon: float,
    lat: float,
    grid: dict,
    *,
    radius_m: float = 500,
) -> Optional[str]:
    """Find nearest substation within radius_m using grid-based index.

    Checks same cell + 8 neighbors (9 cells total).
    """
    cell_lat = int(lat / GRID_CELL_DEG)
    cell_lon = int(lon / GRID_CELL_DEG)
    best_id = None
    best_d = float("inf")
    for dlat in (-1, 0, 1):
        for dlon in (-1, 0, 1):
            cell = grid.get((cell_lat + dlat, cell_lon + dlon))
            if not cell:
                continue
            for sid, sx, sy in cell:
                d = haversine_m(lat, lon, sy, sx)
                if d < radius_m and d < best_d:
                    best_d = d
                    best_id = sid
    return best_id


def add_to_grid_index(
    grid: dict,
    sub_id: str,
    lon: float,
    lat: float,
) -> None:
    """Insert a substation into an existing grid-based spatial index."""
    cell_lat = int(lat / GRID_CELL_DEG)
    cell_lon = int(lon / GRID_CELL_DEG)
    grid.setdefault((cell_lat, cell_lon), []).append((sub_id, lon, lat))


def compact_substation_entry(
    *,
    lon: float,
    lat: float,
    name: str,
    voltage_kv: Optional[float] = None,
) -> dict:
    """Emit canonical compact `s` dict entry: {x, y, n, v}."""
    v_int = int(voltage_kv * 1000) if voltage_kv else None  # store as volts (matching UK format 132000)
    entry = {"x": lon, "y": lat, "n": name}
    if v_int is not None:
        entry["v"] = v_int / 1000  # UK uses kV in v field (132, not 132000)
    return entry


def compact_line_entry(
    *,
    line_id: int,
    polyline: list[list[float]],
    voltage_kv: Optional[float] = None,
    ss: Optional[str] = None,
    se: Optional[str] = None,
) -> dict:
    """Emit canonical compact `l` list entry: {i, p, kv, ss, se}."""
    return {
        "i": line_id,
        "p": polyline,  # [[lon, lat], ...]
        "kv": voltage_kv,
        "ss": ss if ss else "",
        "se": se if se else "",
    }


def next_available_sub_id(s_dict: dict[str, Any]) -> int:
    """Get next available integer sub ID (starts at max existing + 1)."""
    if not s_dict:
        return 5000000000
    try:
        max_id = max(int(k) for k in s_dict.keys() if str(k).isdigit())
        return max_id + 1
    except (ValueError, TypeError):
        return 5000000000  # UK convention 10-digit starting


def next_available_line_id(l_list: list) -> int:
    """Get next available integer line ID (starts at max existing + 1)."""
    if not l_list:
        return 30000001
    try:
        max_id = max(int(entry.get('i', 0)) for entry in l_list if isinstance(entry, dict))
        return max_id + 1
    except (ValueError, TypeError):
        return 30000001  # UK convention 8-digit starting


# ─── Discipline #36 cross-border filter ───
def load_bounds_polygon() -> Optional[Any]:
    """Load uk bounds.json 232-polygon per-county file."""
    bounds_path = REPO_ROOT / COUNTRY_SLUG / "bounds.json"
    if not bounds_path.exists():
        logger.warning(f"bounds.json not found at {bounds_path}")
        return None
    try:
        return json.loads(bounds_path.read_text())
    except Exception as exc:
        logger.error(f"Failed to load bounds.json: {exc}")
        return None


def load_tolerance_km() -> float:
    """Load uk tolerance via the single resolver (configured 3.0 km)."""
    return resolve_boundary_tolerance_km(COUNTRY_SLUG, module_fallback=3.0)


def apply_bounds_filter(
    features: list[dict[str, Any]],
    *,
    tolerance_km: Optional[float] = None,
) -> tuple[list[dict[str, Any]], int]:
    """Discipline #36 cross-border filter with uk 3.0 km tolerance."""
    if tolerance_km is None:
        tolerance_km = load_tolerance_km()
    try:
        from scripts.pipeline.utils.cross_border import filter_by_country_polygon
        return filter_by_country_polygon(features, country_slug=COUNTRY_SLUG, tolerance_km=tolerance_km)
    except ImportError:
        logger.warning(f"cross_border filter unavailable; passing through {len(features)} features")
        return (features, 0)


# ─── Convention #23 provenance ───
def sha256_hexdigest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ─── Discipline #41 line-substation parity ───
def check_discipline_41(subs_count: int, lines_count: int) -> tuple[str, float]:
    """Discipline #41 — line/substation ratio target [1.5-5.0]."""
    if subs_count == 0:
        return ("Discipline #41 DEGENERATE — 0 substations.", 0.0)
    ratio = lines_count / subs_count
    if ratio < 1.5:
        return (
            f"Discipline #41 BELOW_HEALTHY_BAND — {subs_count} substations + "
            f"{lines_count} lines (ratio {ratio:.2f}). May indicate line under-capture.",
            ratio,
        )
    elif ratio > 5.0:
        return (
            f"Discipline #41 ABOVE_HEALTHY_BAND — {subs_count} substations + "
            f"{lines_count} lines (ratio {ratio:.2f}). May indicate MV/LV over-capture.",
            ratio,
        )
    return (
        f"Discipline #41 OK — {subs_count} substations + {lines_count} lines (ratio {ratio:.2f}).",
        ratio,
    )


# ─── Audit sidecar emission ───
def emit_audit_sidecar(
    subcommand: str,
    *,
    substations_count: int,
    lines_count: int,
    raw_sha256: str,
    raw_bytes: int,
    owner_provenance_hist: dict[str, int],
    convention_78_binding_hits: int = 0,
    convention_78_4bis_5_hits: dict[str, int] = None,
    partial_fetch_notes: list[str] = None,
    discipline_41_msg: str = "",
    discipline_36_drops_subs: int = 0,
    discipline_36_drops_lines: int = 0,
) -> Path:
    """Emit YAML audit sidecar per Convention #23 provenance pinning."""
    data_dir = REPO_ROOT / "scripts" / "pipeline" / "data" / COUNTRY_SLUG
    data_dir.mkdir(parents=True, exist_ok=True)
    sidecar_path = data_dir / f"v4_23-ingestion-audit-{COUNTRY_SLUG}-{subcommand}.yaml"

    lines = [
        "# SSI Index v4.23 — UK P31 Wave 4 Ingestion Audit Sidecar",
        f"# Subcommand: {subcommand}",
        f"# Convention #23 provenance pin — auto-generated",
        "",
        "schema_version: v4_23-ingestion-audit-1",
        "country_slug: uk",
        f"subcommand: {subcommand}",
        f"substations_count: {substations_count}",
        f"lines_count: {lines_count}",
        f"raw_sha256: {raw_sha256}",
        f"raw_bytes_fetched: {raw_bytes}",
        "",
        f"discipline_41: '{discipline_41_msg}'",
        f"discipline_36_drops_subs: {discipline_36_drops_subs}",
        f"discipline_36_drops_lines: {discipline_36_drops_lines}",
        "",
        "owner_provenance_histogram:",
    ]
    for prov, count in sorted(owner_provenance_hist.items(), key=lambda x: -x[1]):
        lines.append(f"  {prov}: {count}")
    lines.extend(
        [
            "",
            f"convention_78_alias_normalisation_hits: {convention_78_binding_hits}",
            "",
            "convention_78_4bis_5_hits:",
        ]
    )
    if convention_78_4bis_5_hits:
        for k, v in sorted(convention_78_4bis_5_hits.items()):
            lines.append(f"  {k}: {v}")
    else:
        lines.append("  {}")

    if partial_fetch_notes:
        lines.append("")
        lines.append("partial_fetch_notes:")
        for note in partial_fetch_notes:
            lines.append(f"  - {note}")

    sidecar_path.write_text("\n".join(lines) + "\n")
    logger.info(f"Wrote audit sidecar {sidecar_path} ({sidecar_path.stat().st_size} bytes)")
    return sidecar_path
