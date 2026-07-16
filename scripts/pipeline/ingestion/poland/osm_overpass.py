"""
SSI Pipeline — Poland L1 connector: OSM Overpass API.

Source ID:   PL-C1-osm-overpass
Publisher:   OpenStreetMap contributors via Overpass API
Licence:     ODbL (Open Database License) — attribution required

Feature classes ingested:
  - power=substation      expected 25,000-45,000 elements (5.8× Czechia scale)
  - power=line             expected 130,000-250,000 ways (5-DSO territorial + PSE
                            EHV backbone + tram/metro traction) — LARGEST cohort-wide
  - power=cable            urban underground (5 major cities)
  - power=minor_line       MV distribution branches

⚡ CONVENTION #78 BINDING ENFORCEMENT — 3RD EMPIRICAL TEST ⚡
⚡ LAYER 3 GEOFENCE SUB-CONVENTION 3RD ENFORCEMENT POST-BINDING ⚡
🏛 VISEGRÁD TRIO COMPLETION MILESTONE (3 of 3) 🏛

DIFFERENCE FROM CZECHIA CONNECTOR (post-Convention #78 BINDING 2nd-enforcement
SUCCESS + Layer 3 geofence 2nd application):

  - LARGER SCALE — Poland is ~313k km² (~6.4× Czechia). Bounding-box
    partitioning REQUIRED for line queries (Overpass 512 MB memory ceiling
    + rate-limit prudence). Partitioning by 6 macroregions covering PGE
    (Central+East+SE) + Tauron (South) + Enea (West) + Energa (North) +
    Warsaw metro (Innogy Stoen bbox) + 380/220 kV PSE backbone.

  - REGION-JURISDICTION × VOLTAGE-CLASS OWNER FALLBACK — 9th cohort-wide
    application (after Belgium + Netherlands + Chile + Hungary + Slovenia
    + Colombia + Norway + Slovakia + Czechia). PSE TSO ≥220 kV (400/220 kV
    EHV backbone + UNIQUE 750 kV Rzeszów-Kaliningrad Direct HVAC still active) +
    4 regional DSOs (PGE dominant + Tauron + Enea + Energa) via
    NUTS-3 województwo lookup PLUS Innogy Stoen Warsaw metro Layer 3
    geofence.

    RICHER NUTS-3 COVERAGE THAN SLOVAKIA/CZECHIA — Polish OSM operators
    empirically populate ref:nuts:3 tags per baseline metadata (Poland
    baseline shows 16 województwa fully populated + 44.5% voltage coverage
    at 2247 subs). Layer 2 NUTS-3 → DSO map covers 74 NUTS-3 codes across
    4 DSOs. Only Warsaw metro requires Layer 3 lat/lon geofence.

  - 110 kV MIXED TIER — Poland has explicit 110 kV DSO/TSO split per
    ARERA-equivalent (URE) tariff regulation. PSE operates ONLY EHV
    (220 kV + 400 kV + 750 kV); DSO operates 110 kV + MV + LV. Below 220 kV
    → DSO jurisdiction resolved via NUTS-3 or Layer 3 geofence. Cleaner
    split than Czechia (where ČEPS operates some 110 kV).

  - POLISH NFC + CYRILLIC + TYPOGRAPHIC-QUOTE + COMMA-SEPARATED LEGAL-FORM +
    5-DSO REBRAND-PREDECESSOR UNICODE ALIAS NORMALISATION per Convention #78
    BINDING 3rd enforcement — Unicode NFC + case-insensitive lookup for:
    (a) Polish diacritics (ą ć ę ł ń ó ś ź ż);
    (b) Cyrillic (пге дистрибуция / таурон дистрибуция / энеа оператор /
        энерга оператор / инноджи стоен — Belarusian minority OSM in
        Podlaskie + Ukrainian minority OSM in eastern Silesia + Kaliningrad-
        adjacent OSM contributors);
    (c) Polish typographic quotes („..." like Czech/German/Latvian);
    (d) Slovak/Czech-precedent comma-separated legal-form (s.a. with space
        + s. a. wider space + sp. z o.o. limited-liability variant);
    (e) 5-DSO REBRAND-PREDECESSOR CASCADES:
        - PGE Dystrybucja 4-regional (Rzeszów + Zamość + Lublin + Skarżysko)
        - Tauron 2-variant (EnergiaPro + Enion pre-2008)
        - Enea 1-variant (ZGE pre-2007)
        - Energa 2-variant (GEZ + KEE pre-2006)
        - Innogy Stoen 3-GENERATION (RWE Stoen 2003-2020 + Stoen SA
          2003-2016 + ZE Warszawa pre-2003 state utility) — UNIQUE
          cohort-wide multi-generation tracking
    THIRD empirical test post-BINDING promotion (Latvia P17 closure, 16 July
    2026) + Slovakia P19 1st-enforcement SUCCESS + Czechia P20 2nd-enforcement
    SUCCESS validation. Poland is LARGEST alias-normalisation cohort with
    5-7 rebrand-predecessor cascades + private tram/metro traction preserved
    honestly per Convention #56.
    Preserves original tag in raw_attributes.osm_original_operator for
    audit trail.

  - TSO THRESHOLD 220 kV — Poland's PSE operates 400/220 kV EHV backbone
    (Continental European sync since 1993, LitPol Link HVAC 2015 to Baltic
    Trio which desynchronised from BRELL Feb 2025) + UNIQUE 750 kV Rzeszów-
    Kaliningrad Direct HVAC interconnector still active despite geopolitical
    tension. Below 220 kV → 4-DSO jurisdiction via NUTS-3 OR Warsaw metro
    Layer 3 geofence.

Convention #56 visibly-honest degradation:
  - Missing OSM voltage tag → voltage_kv = None (not 0.0)
  - Missing operator tag → owner via NUTS-3 or Layer 3 geofence fallback
  - Overpass 429/504 → exponential backoff; graceful degradation

Convention #60 non-commercial provenance:
  - OSM (ODbL) only. Public open-data cross-validation deferred.

Discipline #36 cross-border filter — 100m default tolerance (per _base).
Poland's national territory defined by poland/bounds.json polygon —
7-country border cohort (Germany W + Czech Republic S + Slovakia S +
Ukraine E + Belarus E + Lithuania NE + Russia/Kaliningrad NE) + maritime
borders (Sweden + Denmark). LARGEST border cohort cohort-wide.
Discipline #41 line-substation pairing preserved.
"""

from __future__ import annotations

import hashlib
import logging
import time
import urllib.request
import urllib.error
import urllib.parse
import json

from ._base import (
    SubstationRecord,
    TransmissionLineRecord,
    IngestionResult,
    apply_bounds_filter,
    assert_line_parity,
    emit_audit_sidecar,
    cache_path_for,
    now_utc_iso,
    resolve_owner_from_region_jurisdiction,
    normalise_owner_alias,
)

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────
SOURCE_ID = "PL-C1-osm-overpass"
OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]

DEFAULT_TIMEOUT_SECS = 180        # Extended for larger country
DEFAULT_QUERY_TIMEOUT_SECS = 150  # Extended
USER_AGENT = "SSI-Index-Foundation/1.0 (+https://ikengassiindex.github.io)"

INITIAL_BACKOFF_SECS = 30
MAX_BACKOFF_SECS = 300
MAX_RETRY_ATTEMPTS = 4


# ── HTTP fetch with rate-limit backoff ──────────────────────────────────
def _fetch_overpass(query: str, timeout: int = DEFAULT_TIMEOUT_SECS) -> bytes:
    """Fetch Overpass query with retry + endpoint fallback."""
    cache = cache_path_for(query)
    if cache.exists():
        body = cache.read_bytes()
        logger.info("Cache hit: %s (%d bytes)", cache.name, len(body))
        return body

    data = urllib.parse.urlencode({"data": query}).encode("ascii")
    last_err: Exception | None = None

    for endpoint_idx, endpoint in enumerate(OVERPASS_ENDPOINTS):
        backoff = INITIAL_BACKOFF_SECS
        for attempt in range(MAX_RETRY_ATTEMPTS):
            try:
                req = urllib.request.Request(
                    endpoint,
                    data=data,
                    headers={
                        "User-Agent": USER_AGENT,
                        "Accept": "application/json",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                )
                logger.info(
                    "Overpass POST %s (attempt %d/%d)",
                    endpoint, attempt + 1, MAX_RETRY_ATTEMPTS,
                )
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    body = r.read()
                cache.write_bytes(body)
                return body
            except urllib.error.HTTPError as exc:
                last_err = exc
                if exc.code == 429:
                    logger.warning(
                        "Overpass 429 rate-limited; backing off %.0fs (attempt %d)",
                        backoff, attempt + 1,
                    )
                    time.sleep(backoff)
                    backoff = min(backoff * 2, MAX_BACKOFF_SECS)
                    continue
                elif exc.code in (502, 503, 504):
                    logger.warning(
                        "Overpass %d gateway; trying next endpoint after 5s",
                        exc.code,
                    )
                    time.sleep(5)
                    break
                elif exc.code == 406:
                    logger.warning("Overpass 406; retry in 5s")
                    time.sleep(5)
                    continue
                else:
                    logger.error("Overpass HTTP %d: %s", exc.code, exc.reason)
                    time.sleep(5)
                    continue
            except (urllib.error.URLError, TimeoutError) as exc:
                last_err = exc
                logger.warning("Overpass network error: %s; trying next endpoint after 5s", exc)
                time.sleep(5)
                break

    if last_err is not None:
        raise last_err
    raise RuntimeError("Overpass fetch failed on all endpoints without a specific error")


# ── Query builders ──────────────────────────────────────────────────────
_PL_AREA_HEADER = 'area["ISO3166-1"="PL"]->.pl'

# 6-macroregion bbox partitioning for line queries (Overpass 512 MB
# memory ceiling protection at Poland's scale)
_MACROREGION_BBOXES = {
    "NORTH_ENERGA": (53.0, 55.5, 14.0, 20.0),          # Pomorskie + coast
    "NORTH_EAST_ENEA": (52.0, 55.0, 14.0, 18.0),       # Wielkopolskie + Zachodniopomorskie
    "CENTRAL_PGE": (51.0, 53.5, 17.0, 24.0),           # Mazowieckie + Łódzkie + Warsaw
    "SOUTH_TAURON": (49.0, 51.5, 15.0, 21.0),          # Małopolskie + Śląskie + Dolnośląskie
    "SOUTH_EAST_PGE": (49.0, 52.0, 21.0, 24.5),        # Lubelskie + Podkarpackie
    "PSE_BACKBONE": (49.0, 55.5, 14.0, 24.5),          # National for ≥220 kV
}


def _query_substations(feature_type: str = "way") -> str:
    """Build Overpass query for one substation element type (single-shot)."""
    return (
        f'[out:json][timeout:{DEFAULT_QUERY_TIMEOUT_SECS}];'
        f'{_PL_AREA_HEADER};'
        f'{feature_type}["power"="substation"](area.pl);'
        f'out center tags;'
    )


def _query_lines_macroregion(bbox: tuple[float, float, float, float]) -> str:
    """Build Overpass query for lines within a bbox macroregion.

    bbox: (south_lat, north_lat, west_lon, east_lon)
    """
    s, n, w, e = bbox
    return (
        f'[out:json][timeout:{DEFAULT_QUERY_TIMEOUT_SECS}];'
        f'(way["power"="line"]({s},{w},{n},{e});'
        f'way["power"="cable"]({s},{w},{n},{e});'
        f'way["power"="minor_line"]({s},{w},{n},{e}););'
        f'out geom tags;'
    )


# ── OSM element parsers ─────────────────────────────────────────────────
def _center_lat_lon(el: dict) -> tuple[float, float] | None:
    if el.get("type") == "node":
        lat, lon = el.get("lat"), el.get("lon")
    else:
        center = el.get("center") or {}
        lat, lon = center.get("lat"), center.get("lon")
    if lat is None or lon is None:
        return None
    return float(lat), float(lon)


def _parse_voltage_kv(tag_value: str | None) -> float | None:
    """Parse OSM voltage= tag (in volts, may be semicolon-separated).

    Poland-specific: also handles 750000 (750 kV) for Rzeszów-Kaliningrad
    Direct HVAC unique cohort-wide.
    """
    if not tag_value:
        return None
    values = []
    for token in tag_value.replace(",", "").split(";"):
        token = token.strip().rstrip("V").strip()
        try:
            v = float(token)
            if v > 0:
                values.append(v)
        except ValueError:
            continue
    if not values:
        return None
    max_v = max(values)
    return max_v / 1000.0 if max_v > 2000 else max_v


def _substation_from_osm(el: dict) -> SubstationRecord | None:
    """Parse OSM substation element.

    Poland-specific: direct OSM operator= tag propagation with Polish NFC +
    Cyrillic + typographic-quote + comma-separated legal-form + 5-DSO
    rebrand-predecessor Unicode alias normalisation per Convention #78 BINDING
    3rd enforcement; if untagged, region-jurisdiction × voltage-class resolver
    (PSE ≥220 kV OR NUTS-3 → 4-DSO OR Layer 3 geofence (Innogy Stoen Warsaw
    metro) OR PGE catch-all default LARGEST DSO).
    """
    coords = _center_lat_lon(el)
    if coords is None:
        return None
    lat, lon = coords
    tags = el.get("tags", {}) or {}

    osm_id = f"osm_{el.get('type', '?')}_{el.get('id', 0)}"
    voltage_kv = _parse_voltage_kv(tags.get("voltage"))

    op_tag = (tags.get("operator") or "").strip()

    if op_tag:
        owner, was_normalised = normalise_owner_alias(op_tag)
        owner_provenance = (
            "osm_operator_tag_direct_alias_normalised" if was_normalised
            else "osm_operator_tag_direct"
        )
    else:
        # Extract NUTS-3 from OSM tags if present (Polish OSM populates
        # richer NUTS-3 than Slovakia/Czechia per baseline metadata)
        nuts3 = tags.get('ref:nuts:3') or tags.get('nuts:3') or tags.get('nuts_3')
        owner, owner_provenance = resolve_owner_from_region_jurisdiction(
            voltage_kv=voltage_kv,
            nuts_3=nuts3,
            lat=lat,
            lon=lon,
        )

    return SubstationRecord(
        source_id=SOURCE_ID,
        feature_id=osm_id,
        latitude=lat,
        longitude=lon,
        voltage_kv=voltage_kv,
        owner=owner,
        operator_station_name=tags.get("name"),
        raw_attributes={
            "osm_type": el.get("type"),
            "osm_id": el.get("id"),
            "osm_tags": tags,
            "owner_provenance": owner_provenance,
            "osm_substation_subtype": tags.get("substation"),
            "osm_location": tags.get("location"),
            "osm_ref": tags.get("ref"),
            "osm_original_operator": op_tag if op_tag and op_tag != owner else None,
        },
    )


def _line_from_osm(el: dict) -> TransmissionLineRecord | None:
    """Parse OSM power=line element."""
    geom = el.get("geometry") or []
    if not geom or len(geom) < 2:
        return None
    coords: list[list[float]] = []
    for pt in geom:
        lat = pt.get("lat")
        lon = pt.get("lon")
        if lat is None or lon is None:
            continue
        coords.append([float(lon), float(lat)])
    if len(coords) < 2:
        return None

    tags = el.get("tags", {}) or {}
    voltage_kv = _parse_voltage_kv(tags.get("voltage"))
    op_tag = (tags.get("operator") or "").strip()
    if op_tag:
        owner, _ = normalise_owner_alias(op_tag)
    else:
        owner = None

    return TransmissionLineRecord(
        source_id=SOURCE_ID,
        feature_id=f"osm_way_{el.get('id', 0)}",
        coordinates_multilinestring=[coords],
        voltage_kv=voltage_kv,
        owner=owner,
        line_name=tags.get("name"),
        raw_attributes={
            "osm_type": el.get("type"),
            "osm_id": el.get("id"),
            "osm_tags": tags,
            "osm_power_class": tags.get("power"),
            "osm_cables": tags.get("cables"),
            "osm_wires": tags.get("wires"),
            "osm_circuits": tags.get("circuits"),
        },
    )


# ── Public entry ─────────────────────────────────────────────────────────
def fetch(
    *,
    apply_bounds: bool = True,
    ingest_lines: bool = True,
) -> IngestionResult:
    """Fetch OSM Poland substations + lines with 6-macroregion partitioning.

    Larger country than Czechia (~6.4× area) — line queries partition by
    6-macroregion bbox to respect Overpass 512 MB memory ceiling. Uses
    OSM operator= tag with Polish NFC + Cyrillic + typographic-quote +
    comma-separated legal-form + 5-DSO rebrand-predecessor Unicode alias
    normalisation per Convention #78 BINDING 3rd enforcement, then
    region-jurisdiction × voltage-class fallback (PSE ≥220 kV OR NUTS-3 →
    4-DSO OR Layer 3 geofence (Innogy Stoen Warsaw metro) OR PGE catch-all).
    Convention #56 preserved.
    """
    result = IngestionResult(
        source_id=SOURCE_ID,
        fetched_at_utc=now_utc_iso(),
        source_url=OVERPASS_ENDPOINTS[0],
        provincial_scope="PL",
    )

    # ── Substations (split by element type; single-shot per type) ──
    all_sub_bytes = bytearray()
    for feat_type in ("way", "node", "relation"):
        try:
            body = _fetch_overpass(_query_substations(feat_type))
        except Exception as exc:
            result.warnings.append(
                f"Convention #56 partial — OSM substation {feat_type} fetch failed: {exc}"
            )
            continue
        all_sub_bytes.extend(body)
        try:
            data = json.loads(body)
        except json.JSONDecodeError as exc:
            result.warnings.append(
                f"Convention #56 — OSM {feat_type} JSON parse error: {exc}"
            )
            continue
        for el in data.get("elements", []):
            rec = _substation_from_osm(el)
            if rec is not None:
                result.substations.append(rec)

    result.raw_bytes_fetched = len(all_sub_bytes)
    result.raw_sha256 = hashlib.sha256(bytes(all_sub_bytes)).hexdigest()
    logger.info("Parsed %d substations from OSM Overpass", len(result.substations))

    # ── Lines (6-macroregion partitioned) ──
    if ingest_lines:
        seen_way_ids: set[int] = set()  # Dedup across bboxes
        for region_name, bbox in _MACROREGION_BBOXES.items():
            try:
                body = _fetch_overpass(_query_lines_macroregion(bbox))
                try:
                    data = json.loads(body)
                    region_count = 0
                    for el in data.get("elements", []):
                        way_id = el.get("id")
                        if way_id in seen_way_ids:
                            continue
                        seen_way_ids.add(way_id)
                        rec = _line_from_osm(el)
                        if rec is not None:
                            result.transmission_lines.append(rec)
                            region_count += 1
                    logger.info(
                        "Parsed %d lines from %s macroregion (dedupe applied)",
                        region_count, region_name,
                    )
                except json.JSONDecodeError as exc:
                    result.warnings.append(
                        f"Convention #56 — OSM lines JSON parse error for {region_name}: {exc}"
                    )
            except Exception as exc:
                result.warnings.append(
                    f"Convention #56 partial — OSM lines fetch failed for {region_name}: {exc}"
                )
        logger.info(
            "Parsed %d total lines from OSM Overpass across 6 macroregions",
            len(result.transmission_lines),
        )

    # ── Discipline #36 bounds filter ──
    if apply_bounds:
        subs_kept, subs_dropped = apply_bounds_filter(result.substations)
        lines_kept, lines_dropped = apply_bounds_filter(result.transmission_lines)
        result.substations = subs_kept
        result.transmission_lines = lines_kept
        if subs_dropped or lines_dropped:
            result.warnings.append(
                f"Discipline #36 — dropped {len(subs_dropped)} substations + "
                f"{len(lines_dropped)} lines outside Poland polygon "
                "(100m default tolerance; 7-country border cohort — LARGEST cohort-wide)."
            )

    # ── Owner enrichment summary ──
    if result.substations:
        from collections import Counter
        prov_counter = Counter(
            s.raw_attributes.get("owner_provenance", "none")
            for s in result.substations
        )
        direct = sum(
            v for k, v in prov_counter.items()
            if k.startswith("osm_operator_tag_direct")
        )
        pse_tso = sum(
            v for k, v in prov_counter.items()
            if k.startswith("region_jurisdiction_fallback_PSE")
        )
        dso_via_nuts3 = sum(
            v for k, v in prov_counter.items()
            if "_via_nuts3" in k
        )
        innogy_via_geofence = prov_counter.get(
            "region_jurisdiction_fallback_Innogy_Stoen_via_lat_lon_geofence", 0
        )
        pge_default = prov_counter.get(
            "region_jurisdiction_fallback_PGE_via_LARGEST_DSO_default", 0
        )
        alias_normalised = prov_counter.get("osm_operator_tag_direct_alias_normalised", 0)
        logger.info(
            "Owner enrichment: %d direct OSM (%d alias-normalised) + %d PSE_TSO + "
            "%d DSO_via_NUTS3 + %d Innogy_Stoen_via_geofence + %d PGE_default",
            direct, alias_normalised, pse_tso, dso_via_nuts3,
            innogy_via_geofence, pge_default,
        )
        result.warnings.append(
            f"Owner enrichment: {direct}/{len(result.substations)} direct OSM "
            f"operator= tag ({100 * direct / len(result.substations):.1f}%; of these "
            f"{alias_normalised} alias-normalised incl. Polish NFC + Cyrillic + "
            f"typographic quotes + 5-DSO rebrand-predecessor cascades "
            f"(PGE 4-regional + Tauron 2-variant + Enea 1-variant + Energa 2-variant "
            f"+ Innogy Stoen 3-GENERATION UNIQUE cohort-wide) per Convention #78 "
            f"BINDING 3rd enforcement); {pse_tso} PSE_TSO + {dso_via_nuts3} DSO_via_NUTS3 "
            f"(RICHER than Slovakia/Czechia — Polish OSM populates NUTS-3 tags) "
            f"+ {innogy_via_geofence} Innogy_Stoen_via_Warsaw_metro_Layer_3_geofence "
            f"(post-BINDING 3rd enforcement) + {pge_default} PGE_LARGEST_DSO_default "
            f"catch-all ({100 * (pse_tso + dso_via_nuts3 + innogy_via_geofence + pge_default) / len(result.substations):.1f}%)."
        )

    # ── Discipline #41 parity ──
    parity_ok, findings = assert_line_parity(result, outbound_border_ok=True)
    for f in findings:
        logger.info("Discipline #41: %s", f)

    return result


# ── CLI harness ──────────────────────────────────────────────────────────
def _cli_main() -> None:
    import argparse
    parser = argparse.ArgumentParser(
        description=(
            "OSM Overpass PL L1 connector — Poland region-jurisdiction × "
            "voltage-class via PSE + 4 DSO NUTS-3 + Innogy Stoen Warsaw "
            "metro Layer 3 geofence + Convention #78 BINDING 3rd-enforcement "
            "test + Visegrád Trio completion milestone"
        )
    )
    parser.add_argument("--skip-lines", action="store_true",
                        help="Skip line ingestion (subs only)")
    parser.add_argument("--no-bounds", action="store_true",
                        help="Skip Discipline #36 filter")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    result = fetch(
        apply_bounds=not args.no_bounds,
        ingest_lines=not args.skip_lines,
    )

    from pathlib import Path
    audit_path = Path(__file__).resolve().parent.parent.parent.parent / "poland" / "v4_23-ingestion-audit-poland-overpass.yaml"
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    emit_audit_sidecar(result, audit_path)

    print(f"\n{SOURCE_ID} fetch complete")
    print(f"  substations:        {len(result.substations):,}")
    print(f"  transmission_lines: {len(result.transmission_lines):,}")
    print(f"  raw_bytes_fetched:  {result.raw_bytes_fetched:,}")
    print(f"  raw_sha256:         {result.raw_sha256}")
    print(f"  audit_sidecar:      {audit_path}")

    from collections import Counter
    prov = Counter(
        s.raw_attributes.get("owner_provenance", "none")
        for s in result.substations
    )
    print("  Owner-provenance distribution:")
    for k, v in prov.most_common():
        print(f"    {v:>5}  {k}")

    ops = Counter(s.owner for s in result.substations if s.owner)
    print(f"  Distinct operators: {len(ops)}")
    print("  Top 20 operators:")
    for k, v in ops.most_common(20):
        print(f"    {v:>5}  {k}")

    for w in result.warnings:
        print(f"  ⚠ {w}")


if __name__ == "__main__":
    _cli_main()
