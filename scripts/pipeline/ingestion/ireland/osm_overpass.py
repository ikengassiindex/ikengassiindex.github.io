"""
SSI Pipeline — Ireland L1 connector: OSM Overpass API.

Source ID:   IE-C1-osm-overpass
Publisher:   OpenStreetMap contributors via Overpass API
Licence:     ODbL (Open Database License) — attribution required

Feature classes ingested:
  - power=substation      expected 700-1800 elements (way)
                          expected 300-800 elements (node)
                          expected 5-20 elements (relation)
  - power=line             expected 2500-6000 ways (Irish moderate density)
  - power=cable            urban underground (Dublin metro)
  - power=minor_line       MV distribution branches

DIFFERENCE FROM GREEK CONNECTOR (Wave 3 P22 single-DSO precedent):
  - MODERATE SCALE — Ireland is ~70k km² (~0.5× Greece at 131k km²)
    but 3× denser than Nordic/Arctic countries. Western European
    contributor density MODERATE. Single-query per element type
    expected reliable. 504 gateway timeouts less likely than
    Iceland/Greek Nordic-Arctic/Mediterranean sparsity — Convention
    #56 partial-fetch preservation ready.

  - SIMPLEST DSO ARCHITECTURE cohort-wide — SINGLE national DSO
    (ESB Networks) covering all 26 Republic of Ireland counties.
    Analogous to Greek DEDDIE simplification. NO Convention #78
    §4bis.5 Layer 3 lat/lon geofence needed. Attribution reduces to:
      * ≥110 kV → EirGrid — TSO (400/275/220/110 kV backbone)
      * <110 kV → ESB Networks — SINGLE national DSO
      * Voltage None → ESB Networks default (distribution-tier dominant)

  - ENGLISH-LANGUAGE DOMINANT + MINIMAL GAEILGE (IRISH) ALIAS
    NORMALISATION per Convention #78 BINDING 7th enforcement —
    Unicode NFC + case-insensitive lookup for:
      * English legal-form variants (Ltd / Limited / plc / DAC / PLC)
      * Gaeilge (Irish) legal-form variants (Teoranta / Teo /
        Cuideachta)
      * Minimal Gaeilge diacritics (á é í ó ú)
      * ESB Distribution → ESB Networks 2010 rebrand (15-year legacy —
        LARGEST predecessor class)
      * EirGrid Gaeilge alias (Éirid)
    ~80-entry alias map (SMALLEST Wave 3 cohort; Switzerland 150 +
    Poland 100 + Czechia 250+). Preserves original tag in
    raw_attributes.osm_original_operator for audit trail. Estimated
    10-50 alias-normalisation hits (LOWEST cohort-wide expected —
    cumulative 10-country post-Ireland: 20,647-20,687 — 2,065-2,069×
    above BINDING threshold).

  - TSO THRESHOLD 110 kV — EirGrid operates 400/275/220/110 kV
    backbone. Ireland 110 kV is MAIN transmission tier (unlike
    Central European where 110 kV is DSO subtransmission). Below
    110 kV → ESB Networks distribution jurisdiction.


Convention #56 visibly-honest degradation:
  - Missing OSM voltage tag → voltage_kv = None; owner defaults to
    ESB Networks (distribution-tier dominant per baseline empirical distribution)
  - Missing operator tag → owner via voltage-class × single-DSO default
  - Overpass 429/504 → exponential backoff; graceful degradation

Convention #60 non-commercial provenance:
  - OSM (ODbL) only. Public open-data cross-validation deferred.

Discipline #36 cross-border filter — 1.0 km default tolerance (per _base
— Atlantic coastline + 3 cross-border interconnector precedent applied
to Ireland's coastline complexity + Moyle HVDC + East-West HVDC +
Northern Ireland AC land border precision).

Discipline #41 line-substation pairing preserved.

Convention #78 §4bis.5 Layer 3 geofence — NOT REQUIRED (single
national DSO — Greek DEDDIE precedent).
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
SOURCE_ID = "IE-C1-osm-overpass"
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
_IE_AREA_HEADER = 'area["ISO3166-1"="IE"]->.ie'


def _query_substations(feature_type: str = "way") -> str:
    """Build Overpass query for one substation element type."""
    return (
        f'[out:json][timeout:{DEFAULT_QUERY_TIMEOUT_SECS}];'
        f'{_IE_AREA_HEADER};'
        f'{feature_type}["power"="substation"](area.ie);'
        f'out center tags;'
    )


def _query_lines() -> str:
    """Build Overpass query for all lines within Ireland.

    Single-query safe for moderate-scale country — Ireland ~70k km²
    with western European moderate OSM contributor density. Expected
    2500-6000 lines within timeout budget."""
    return (
        f'[out:json][timeout:{DEFAULT_QUERY_TIMEOUT_SECS}];'
        f'{_IE_AREA_HEADER};'
        f'(way["power"="line"](area.ie);'
        f'way["power"="cable"](area.ie);'
        f'way["power"="minor_line"](area.ie););'
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
    """Parse OSM voltage= tag (in volts, may be semicolon-separated)."""
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

    Ireland-specific: direct OSM operator= tag propagation with English
    (dominant) + Gaeilge (Irish) legal-form variants (Ltd/Limited/plc/
    DAC/Teoranta/Teo/Cuideachta) + minimal Gaeilge diacritics + ESB
    Distribution predecessor Unicode alias normalisation per Convention
    #78 BINDING 7th enforcement; if untagged, voltage-class × single-DSO
    resolver (EirGrid ≥110 kV OR ESB Networks <110 kV OR ESB Networks
    default). NO Layer 3 geofence — single national DSO (Greek DEDDIE
    precedent)."""
    coords = _center_lat_lon(el)
    if coords is None:
        return None
    lat, lon = coords
    tags = el.get("tags", {}) or {}

    osm_id = f"osm_{el.get('type', '?')}_{el.get('id', 0)}"
    voltage_kv = _parse_voltage_kv(tags.get("voltage"))

    op_tag = (tags.get("operator") or "").strip()

    if op_tag:
        owner = normalise_owner_alias(op_tag)
        owner_provenance = (
            "osm_operator_tag_direct_alias_normalised" if owner != op_tag
            else "osm_operator_tag_direct"
        )
    else:
        # Voltage-class × single-DSO resolver
        nuts3 = tags.get('ref:nuts:3') or tags.get('nuts:3') or tags.get('nuts_3')
        owner, owner_provenance = resolve_owner_from_region_jurisdiction(
            voltage_kv, lat, lon, nuts3=nuts3
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
    owner = normalise_owner_alias(op_tag) if op_tag else None

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
    """Fetch OSM Ireland substations + lines (single-query per element type).

    Moderate-scale country — no partitioning needed. Uses OSM operator=
    tag with English + Gaeilge legal-form variants + Gaeilge diacritics
    + ESB Distribution predecessor Unicode alias normalisation per
    Convention #78 BINDING 7th enforcement, then voltage-class ×
    single-DSO fallback (EirGrid ≥110 kV OR ESB Networks <110 kV OR
    ESB Networks default) for untagged. Convention #56 preserved."""
    result = IngestionResult(
        source_id=SOURCE_ID,
        fetched_at_utc=now_utc_iso(),
        source_url=OVERPASS_ENDPOINTS[0],
        provincial_scope="IE",
    )

    # ── Substations (split by element type) ──
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

    # ── Lines (single-query, no partitioning) ──
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
                result.warnings.append(
                    f"Convention #56 — OSM lines JSON parse error: {exc}"
                )
        except Exception as exc:
            result.warnings.append(
                f"Convention #56 partial — OSM lines fetch failed: {exc}"
            )
        logger.info("Parsed %d lines from OSM Overpass", len(result.transmission_lines))

    # ── Discipline #36 bounds filter (1.0 km Atlantic coastline tolerance) ──
    if apply_bounds:
        subs_kept, subs_dropped = apply_bounds_filter(result.substations)
        lines_kept, lines_dropped = apply_bounds_filter(result.transmission_lines)
        result.substations = subs_kept
        result.transmission_lines = lines_kept
        if subs_dropped or lines_dropped:
            result.warnings.append(
                f"Discipline #36 — dropped {len(subs_dropped)} substations + "
                f"{len(lines_dropped)} lines outside Ireland polygon "
                "(1.0 km Atlantic coastline tolerance)."
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
        eirgrid_tso = sum(
            v for k, v in prov_counter.items()
            if k.startswith("region_jurisdiction_fallback_EirGrid")
        )
        esb_networks = sum(
            v for k, v in prov_counter.items()
            if k.startswith("region_jurisdiction_fallback_ESB Networks")
            or k.startswith("region_jurisdiction_fallback_ESB_Networks")
        )
        alias_normalised = prov_counter.get("osm_operator_tag_direct_alias_normalised", 0)
        logger.info(
            "Owner enrichment: %d direct OSM (%d alias-normalised) + %d EirGrid_TSO + %d ESB_Networks",
            direct, alias_normalised, eirgrid_tso, esb_networks,
        )
        result.warnings.append(
            f"Owner enrichment: {direct}/{len(result.substations)} direct "
            f"OSM operator= tag ({100 * direct / len(result.substations):.1f}%; "
            f"of these {alias_normalised} alias-normalised incl. English (Ltd/Limited/plc/DAC) + Gaeilge (Teoranta/Teo/Cuideachta) + Gaeilge diacritics (á é í ó ú + Éirid) + ESB Distribution predecessor per Convention #78 BINDING 7th enforcement); "
            f"{eirgrid_tso} EirGrid_TSO + {esb_networks} ESB_Networks_DSO "
            f"({100 * (eirgrid_tso + esb_networks) / len(result.substations):.1f}%)."
        )

    # ── Discipline #41 parity ──
    parity_ok, findings = assert_line_parity(result, outbound_border_ok=False)
    for f in findings:
        logger.info("Discipline #41: %s", f)

    return result


# ── CLI harness ──────────────────────────────────────────────────────────
def _cli_main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="OSM Overpass IE L1 connector — Ireland voltage-class × single-DSO via EirGrid ≥110kV + ESB Networks <110kV + Convention #78 BINDING 7th-enforcement test (English + Gaeilge Ltd/Limited/plc/DAC/Teoranta/Teo/Cuideachta legal-form + minimal Gaeilge diacritics + ESB Distribution pre-2010 predecessor)")
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

    parity_ok, findings = assert_line_parity(result, outbound_border_ok=False)
    audit_path = emit_audit_sidecar(result, parity_findings=findings)

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
    print("  Top 15 operators:")
    for k, v in ops.most_common(15):
        print(f"    {v:>5}  {k}")

    for w in result.warnings:
        print(f"  ⚠ {w}")


if __name__ == "__main__":
    _cli_main()
