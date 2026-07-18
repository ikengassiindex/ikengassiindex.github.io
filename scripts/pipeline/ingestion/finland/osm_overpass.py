"""
SSI Pipeline — Finland L1 connector: OSM Overpass API.

Source ID:   FI-C1-osm-overpass
Publisher:   OpenStreetMap contributors via Overpass API
Licence:     ODbL (Open Database License) — attribution required

Feature classes ingested:
  - power=substation      expected 4000-6000 elements (way)
                          expected 800-1500 elements (node)
                          expected 10-30 elements (relation)
  - power=line             expected 4000-10000 ways (Nordic density)

DIFFERENCE FROM DENMARK CONNECTOR (Wave 3 P28 Nordic offshore-wind
precedent):
  - LARGER SCALE MULTI-DSO NORDIC CLUSTER EXTENSION — Finland is
    ~338k km² (~7.8× Denmark at 43k km²) with sparser Nordic OSM
    contributor density. Single-query per element type expected
    reliable given Nordic OSM community maturity (like DK P28 single-
    pass). Convention #56 partial-fetch preservation ready if needed.

  - 8-LAYER MULTI-DSO RESOLVER + HELSINKI §4bis.5 7TH ENFORCEMENT —
    Fingrid TSO + 6 major DSOs (Caruna LARGEST + Elenia + Helen +
    Vantaan Energia + Turku + Tampereen) + Åland autonomous +
    nuclear (Olkiluoto + Loviisa) + VR Group rail traction + industrial
    captives (Stora Enso + UPM + Metsä + Outokumpu + SSAB + Nokia +
    Neste). Attribution reduces to 8-layer cascade:
      * Layer 1: Fingrid TSO threshold (≥110 kV)
      * Layer 2: VR Group rail traction (25 kV AC)
      * Layer 3a: Nuclear plant name-match (Olkiluoto + Loviisa)
      * Layer 3b: §4bis.5 Helsinki metropolitan 3-way geofence
                  (Helen city + Vantaan suburb + Caruna region)
                  (7TH COHORT-WIDE ENFORCEMENT)
      * Layer 4a: Åland autonomous Swedish-only carve-out
      * Layer 4b: Industrial captive
      * Layer 5: Region → dominant DSO map (18 maakunta)
      * Layer 6: Fingrid catch-all (safety net)

  - FINNISH + SWEDISH + SAMI + ENGLISH TRILINGUAL per Convention #78
    BINDING 11TH ENFORCEMENT (post-DECADE-MILESTONE) — Unicode NFC +
    case-insensitive lookup for:
      * Finnish diacritics (ä ö å) via NFC normalization
      * Swedish diacritics (ä ö å — same set; Åland 100% + Bothnian
        bilingual)
      * Sami minority diacritics (ŋ ǯ â — Lappi region)
      * Finnish legal-form (Oyj / Oy / Ky / ry)
      * Swedish/Åland legal-form (Ab / Abp / AB)
      * Predecessor rebrand cascades (Fortum→Caruna 2014 + Vattenfall
        →Elenia 2012 + IVO→Fortum 1998 + Helsingin Energia→Helen
        2015)
      * Nuclear generation-vs-distribution separation (TVO/Fortum
        own nuclear BUT grid=Fingrid TSO)
    ~130-entry alias map. Estimated 30-100 alias-normalisation hits.

  - TSO THRESHOLD 110 kV — Fingrid operates 110/220/400 kV backbone.
    Finland 110 kV is MAIN transmission tier (like Ireland/NZ). Note:
    baseline is 96.8% at 110 kV so Layer 1 will dominate for that
    tier; direct OSM tags catch the DSO cases (Helen 110 kV Helsinki
    urban + Caruna 110 kV backbone in some regions).

Convention #56 visibly-honest degradation:
  - Missing OSM voltage tag → voltage_kv = None; owner defaults to
    Fingrid catch-all (Layer 6 safety net)
  - Missing operator tag → owner via 8-layer cascade
  - Overpass 429/504 → exponential backoff; graceful degradation

Convention #60 non-commercial provenance:
  - OSM (ODbL) only. Public open-data cross-validation deferred to
    Fingrid Annual Report + Suomen Energia + Energiavirasto public.

Discipline #36 cross-border filter — 5.0 km default tolerance (per
_base — Baltic archipelago + Bothnian coastline precedent + 4 HVDC
interconnector terminals). No Russian cross-border (post-2022
disconnect). Åland Swedish autonomous carve-out preserved.

Discipline #41 line-substation pairing preserved.

Convention #78 §4bis.5 Layer 3 geofence — REQUIRED (7TH COHORT-WIDE
ENFORCEMENT at Helsinki metropolitan 3-way DSO split).
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
SOURCE_ID = "FI-C1-osm-overpass"
OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]

DEFAULT_TIMEOUT_SECS = 120
DEFAULT_QUERY_TIMEOUT_SECS = 90
USER_AGENT = "SSI-Index-Foundation/1.0 (+https://ikengassiindex.github.io)"

INITIAL_BACKOFF_SECS = 30
MAX_BACKOFF_SECS = 300
MAX_RETRY_ATTEMPTS = 4


def _fetch_overpass(query: str, timeout: int = DEFAULT_TIMEOUT_SECS) -> bytes:
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
                    logger.warning("Overpass 429 rate-limited; backing off %.0fs (attempt %d)", backoff, attempt + 1)
                    time.sleep(backoff)
                    backoff = min(backoff * 2, MAX_BACKOFF_SECS)
                    continue
                elif exc.code in (502, 503, 504):
                    logger.warning("Overpass %d gateway; trying next endpoint after 5s", exc.code)
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


_FI_AREA_HEADER = 'area["ISO3166-1"="FI"]->.fi'


def _query_substations(feature_type: str = "way") -> str:
    return (
        f'[out:json][timeout:{DEFAULT_QUERY_TIMEOUT_SECS}];'
        f'{_FI_AREA_HEADER};'
        f'{feature_type}["power"="substation"](area.fi);'
        f'out center tags;'
    )


def _query_lines() -> str:
    return (
        f'[out:json][timeout:{DEFAULT_QUERY_TIMEOUT_SECS}];'
        f'{_FI_AREA_HEADER};'
        f'(way["power"="line"](area.fi);'
        f'way["power"="cable"](area.fi);'
        f'way["power"="minor_line"](area.fi););'
        f'out geom tags;'
    )


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
    """Parse OSM substation element — Finland 8-layer cascade."""
    coords = _center_lat_lon(el)
    if coords is None:
        return None
    lat, lon = coords
    tags = el.get("tags", {}) or {}

    osm_id = f"osm_{el.get('type', '?')}_{el.get('id', 0)}"
    voltage_kv = _parse_voltage_kv(tags.get("voltage"))
    name = tags.get("name") or tags.get("name:fi") or tags.get("name:sv") or tags.get("name:en") or tags.get("name:se")

    op_tag = (tags.get("operator") or "").strip()

    if op_tag:
        owner = normalise_owner_alias(op_tag)
        owner_provenance = (
            "osm_operator_tag_direct_alias_normalised" if owner != op_tag
            else "osm_operator_tag_direct"
        )
    else:
        admin_code = (
            tags.get("addr:state")
            or tags.get("addr:region")
            or tags.get("is_in:region")
            or tags.get("region")
        )
        owner, owner_provenance = resolve_owner_from_region_jurisdiction(
            voltage_kv, lat, lon, admin_code=admin_code, name=name
        )

    return SubstationRecord(
        source_id=SOURCE_ID,
        feature_id=osm_id,
        latitude=lat,
        longitude=lon,
        voltage_kv=voltage_kv,
        owner=owner,
        operator_station_name=name,
        raw_attributes={
            "osm_type": el.get("type"),
            "osm_id": el.get("id"),
            "osm_tags": tags,
            "owner_provenance": owner_provenance,
            "osm_substation_subtype": tags.get("substation"),
            "osm_location": tags.get("location"),
            "osm_ref": tags.get("ref"),
            "osm_name_fi": tags.get("name:fi"),
            "osm_name_sv": tags.get("name:sv"),
            "osm_name_se": tags.get("name:se"),  # Sami
            "osm_name_en": tags.get("name:en"),
            "osm_original_operator": op_tag if op_tag and op_tag != owner else None,
        },
    )


def _line_from_osm(el: dict) -> TransmissionLineRecord | None:
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
    owner = normalise_owner_alias(op_tag) if op_tag else None
    name = tags.get("name") or tags.get("name:fi") or tags.get("name:sv") or tags.get("name:en")

    return TransmissionLineRecord(
        source_id=SOURCE_ID,
        feature_id=f"osm_way_{el.get('id', 0)}",
        coordinates_multilinestring=[coords],
        voltage_kv=voltage_kv,
        owner=owner,
        line_name=name,
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


def fetch(
    *,
    apply_bounds: bool = True,
    ingest_lines: bool = True,
) -> IngestionResult:
    result = IngestionResult(
        source_id=SOURCE_ID,
        fetched_at_utc=now_utc_iso(),
        source_url=OVERPASS_ENDPOINTS[0],
        provincial_scope="FI",
    )

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
            result.warnings.append(f"Convention #56 — OSM {feat_type} JSON parse error: {exc}")
            continue
        for el in data.get("elements", []):
            rec = _substation_from_osm(el)
            if rec is not None:
                result.substations.append(rec)

    result.raw_bytes_fetched = len(all_sub_bytes)
    result.raw_sha256 = hashlib.sha256(bytes(all_sub_bytes)).hexdigest()
    logger.info("Parsed %d substations from OSM Overpass", len(result.substations))

    if ingest_lines:
        try:
            body = _fetch_overpass(_query_lines())
            try:
                data = json.loads(body)
                for el in data.get("elements", []):
                    rec = _line_from_osm(el)
                    if rec is not None:
                        result.transmission_lines.append(rec)
            except json.JSONDecodeError as exc:
                result.warnings.append(f"Convention #56 — OSM lines JSON parse error: {exc}")
        except Exception as exc:
            result.warnings.append(f"Convention #56 partial — OSM lines fetch failed: {exc}")
        logger.info("Parsed %d lines from OSM Overpass", len(result.transmission_lines))

    if apply_bounds:
        subs_kept, subs_dropped = apply_bounds_filter(result.substations)
        lines_kept, lines_dropped = apply_bounds_filter(result.transmission_lines)
        result.substations = subs_kept
        result.transmission_lines = lines_kept
        if subs_dropped or lines_dropped:
            result.warnings.append(
                f"Discipline #36 — dropped {len(subs_dropped)} substations + "
                f"{len(lines_dropped)} lines outside Finland polygon "
                "(5.0 km Baltic archipelago + Bothnian coastline + 4 HVDC "
                "interconnector precision tolerance; NO Russian cross-border)."
            )

    if result.substations:
        from collections import Counter
        prov_counter = Counter(
            s.raw_attributes.get("owner_provenance", "none")
            for s in result.substations
        )
        direct = sum(v for k, v in prov_counter.items() if k.startswith("osm_operator_tag_direct"))
        fingrid_tso = sum(
            v for k, v in prov_counter.items()
            if k.startswith("region_jurisdiction_layer_1_Fingrid_TSO")
            or k.startswith("region_jurisdiction_layer_6_Fingrid_catch_all")
        )
        vr = prov_counter.get("region_jurisdiction_layer_2_VR_25kv_AC_traction", 0)
        nuclear = prov_counter.get("region_jurisdiction_layer_3a_nuclear_name_match", 0)
        helsinki_geofence = sum(
            v for k, v in prov_counter.items()
            if k.startswith("region_jurisdiction_layer_3_4bis5_7th_enforcement")
        )
        aland = sum(
            v for k, v in prov_counter.items()
            if k.startswith("region_jurisdiction_layer_4_Aland")
        )
        captive = prov_counter.get("region_jurisdiction_layer_4b_industrial_captive_name_match", 0)
        region_dso = sum(
            v for k, v in prov_counter.items()
            if k.startswith("region_jurisdiction_layer_5_")
        )
        alias_normalised = prov_counter.get("osm_operator_tag_direct_alias_normalised", 0)
        logger.info(
            "Owner enrichment: %d direct OSM (%d alias-normalised) + "
            "%d Fingrid_TSO + %d VR + %d nuclear + "
            "%d §4bis5_Helsinki (7th enforcement) + %d Åland + %d captive + "
            "%d region_DSO",
            direct, alias_normalised, fingrid_tso, vr, nuclear,
            helsinki_geofence, aland, captive, region_dso,
        )
        result.warnings.append(
            f"Owner enrichment: {direct}/{len(result.substations)} direct "
            f"OSM operator= tag ({100 * direct / len(result.substations):.1f}%; "
            f"of these {alias_normalised} alias-normalised incl. Finnish "
            f"(Fingrid / Caruna / Elenia / Helen / Vantaan Energia / Turku / Tampereen + ä ö å) "
            f"+ Swedish (Åland 100% + Bothnian bilingual + Kraftnät Åland) "
            f"+ Sami minority (Lappi ŋ ǯ â) + nuclear generation-vs-distribution "
            f"separation (TVO Olkiluoto + Fortum Loviisa NOT DSO — routed to Fingrid) "
            f"+ predecessor rebrands (IVO→Fortum 1998 + Fortum→Caruna 2014 + "
            f"Vattenfall→Elenia 2012 + Helsingin Energia→Helen 2015) per Convention "
            f"#78 BINDING 11th enforcement post-DECADE-MILESTONE); "
            f"{fingrid_tso} Fingrid_TSO + {vr} VR + {nuclear} nuclear + "
            f"{helsinki_geofence} §4bis5_Helsinki_7TH_ENFORCEMENT + {aland} Åland + "
            f"{captive} industrial_captive + {region_dso} region_DSO "
            f"({100 * (fingrid_tso + vr + nuclear + helsinki_geofence + aland + captive + region_dso) / len(result.substations):.1f}%)."
        )

    parity_ok, findings = assert_line_parity(result, outbound_border_ok=False)
    for f in findings:
        logger.info("Discipline #41: %s", f)

    return result


def _cli_main() -> None:
    import argparse
    parser = argparse.ArgumentParser(
        description="OSM Overpass FI L1 connector — 8-layer multi-DSO cascade "
                    "(Fingrid TSO OR VR rail OR nuclear name-match OR §4bis.5 "
                    "Helsinki 3-way geofence 7TH COHORT-WIDE ENFORCEMENT OR Åland "
                    "autonomous OR industrial captive OR region → dominant DSO OR "
                    "Fingrid catch-all) + Convention #78 BINDING 11th ENFORCEMENT "
                    "(Finnish + Swedish + Sami trilingual + predecessor rebrands "
                    "IVO→Fortum 1998 + Fortum→Caruna 2014 + Vattenfall→Elenia 2012 "
                    "+ Helsingin Energia→Helen 2015 + nuclear TVO/Fortum "
                    "generation-vs-distribution separation) — post-DECADE MILESTONE"
    )
    parser.add_argument("--skip-lines", action="store_true", help="Skip line ingestion (subs only)")
    parser.add_argument("--no-bounds", action="store_true", help="Skip Discipline #36 filter")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    result = fetch(apply_bounds=not args.no_bounds, ingest_lines=not args.skip_lines)

    parity_ok, findings = assert_line_parity(result, outbound_border_ok=False)
    audit_path = emit_audit_sidecar(result, parity_findings=findings)

    print(f"\n{SOURCE_ID} fetch complete")
    print(f"  substations:        {len(result.substations):,}")
    print(f"  transmission_lines: {len(result.transmission_lines):,}")
    print(f"  raw_bytes_fetched:  {result.raw_bytes_fetched:,}")
    print(f"  raw_sha256:         {result.raw_sha256}")
    print(f"  audit_sidecar:      {audit_path}")

    from collections import Counter
    prov = Counter(s.raw_attributes.get("owner_provenance", "none") for s in result.substations)
    print("  Owner-provenance distribution:")
    for k, v in prov.most_common():
        print(f"    {v:>5}  {k}")

    ops = Counter(s.owner for s in result.substations if s.owner)
    print(f"  Distinct operators: {len(ops)}")
    print("  Top 15 operators:")
    for k, v in ops.most_common(15):
        print(f"    {v:>5}  {k}")

    for w in result.warnings:
        print(f"  ⚠ {w}")


if __name__ == "__main__":
    _cli_main()
