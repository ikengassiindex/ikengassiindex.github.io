"""
SSI Pipeline — Korea L1 connector: OSM Overpass API.

Source ID:   KR-C1-osm-overpass
Publisher:   OpenStreetMap contributors via Overpass API
Licence:     ODbL (Open Database License) — attribution required

Feature classes ingested:
  - power=substation      expected 1200-2000 elements (way)
                          expected 400-800 elements (node)
                          expected 5-15 elements (relation)
  - power=line             expected 3000-8000 ways (moderate density)
  - power=cable            urban underground (Seoul metro + Busan)
  - power=minor_line       MV distribution branches

DIFFERENCE FROM IRELAND CONNECTOR (Wave 3 P25 single-DSO precedent):
  - LARGEST SINGLE-DSO EMPIRICAL WAVE 3 EVENT — Korea is ~100k km²
    (~1.4× Ireland at 70k km²) with mature Asian OSM contributor
    density (Korean OSM community established since 2007). Single-
    query per element type expected reliable. 504 gateway timeouts
    less likely than Nordic-isolated Iceland — Convention #56
    partial-fetch preservation ready.

  - SIMPLEST DSO ARCHITECTURE cohort-wide — SINGLE vertically-
    integrated monopoly (KEPCO) owning ALL voltage tiers
    (765/345/154/55/22.9 kV) across all 17 do/si first-tier admin
    regions. Analogous to Greek DEDDIE / Costa Rica ICE / Ireland
    ESB Networks simplifications, but at LARGER scale (~2.5M km
    distribution + ~30,000 km transmission network). NO Convention
    #78 §4bis.5 Layer 3 lat/lon geofence needed. Attribution
    reduces to 4-layer name-based cascade:
      * Layer 1: KHNP nuclear identity (6 nuclear plants)
      * Layer 2: Industrial captive (POSCO/Samsung/SK/Hyundai/LG/KDHC/KORAIL)
      * Layer 3: Admin → DSO (empirically ~0 hits — all route to KEPCO)
      * Layer 4: KEPCO catch-all (monopoly default)

  - MULTI-SCRIPT ALIAS NORMALISATION per Convention #78 BINDING 8th
    enforcement (FIRST Asian Wave 3 event) — Unicode NFC + case-
    insensitive lookup for:
      * Hangul native forms (한국전력공사 / 한전 / 한국수력원자력)
      * Revised Romanization (RRK, 2000): Hanguk Jeollyeok Gongsa
      * McCune-Reischauer (M-R, pre-2000): Han'guk Chŏllyŏk Kongsa
      * English acronyms (KEPCO / KHNP / KPX / KDN)
      * Legal-form suffixes (주식회사 / 株式會社 / ㈜ / Co., Ltd.)
      * Predecessor: KECO pre-1982 Korea Electric Company merger
    ~100-entry alias map (LARGER than Ireland 80; between Slovakia
    100 and Switzerland 150). Preserves original tag in
    raw_attributes.osm_original_operator for audit trail. Estimated
    50-200 alias-normalisation hits (SIGNIFICANT cohort-wide event —
    cumulative 11-country post-Korea: ~20,700-20,850 — 2,070-2,085×
    above BINDING threshold).

  - NO TSO THRESHOLD — KEPCO owns ALL voltages including 765 kV
    ultra-EHV backbone. Layer 1 KHNP nuclear identity handled by
    name pattern match (Kori/Hanbit/Hanul/Wolseong/Saeul + Shin-*
    prefix variants). Layer 2 industrial captives handled by name
    pattern match (POSCO/Samsung/SK Hynix/Hyundai/LG Chem/KDHC/
    KORAIL). Layer 3 empirically dormant (all admin → KEPCO).
    Layer 4 KEPCO catch-all covers the remaining ~87% direct +
    Layer 3 default fallback for untagged.

Convention #56 visibly-honest degradation:
  - Missing OSM voltage tag → voltage_kv = None; owner defaults to
    KEPCO (monopoly per baseline empirical distribution)
  - Missing operator tag → owner via KEPCO monopoly Layer 4 default
  - Overpass 429/504 → exponential backoff; graceful degradation

Convention #60 non-commercial provenance:
  - OSM (ODbL) only. Public open-data cross-validation deferred.

Discipline #36 cross-border filter — 5.0 km default tolerance (per
_base — Iceland-analog for ~4,400 islands + Ulleungdo + Dokdo +
Marado + Jeju + Baengnyeongdo offshore offsets). DMZ northern
boundary pre-excluded via bounds.json 17-region South-Korea-only
polygon (DPRK entirely excluded).

Discipline #41 line-substation pairing preserved.

Convention #78 §4bis.5 Layer 3 geofence — NOT REQUIRED (KEPCO
monopoly — Ireland/Greek/Costa Rica single-DSO precedent).
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
SOURCE_ID = "KR-C1-osm-overpass"
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
_KR_AREA_HEADER = 'area["ISO3166-1"="KR"]->.kr'


def _query_substations(feature_type: str = "way") -> str:
    """Build Overpass query for one substation element type."""
    return (
        f'[out:json][timeout:{DEFAULT_QUERY_TIMEOUT_SECS}];'
        f'{_KR_AREA_HEADER};'
        f'{feature_type}["power"="substation"](area.kr);'
        f'out center tags;'
    )


def _query_lines() -> str:
    """Build Overpass query for all lines within South Korea.

    Single-query safe for moderate-scale country — Korea ~100k km²
    with mature Asian OSM contributor density (Korean OSM community
    established since 2007). Expected 3000-8000 lines within timeout
    budget."""
    return (
        f'[out:json][timeout:{DEFAULT_QUERY_TIMEOUT_SECS}];'
        f'{_KR_AREA_HEADER};'
        f'(way["power"="line"](area.kr);'
        f'way["power"="cable"](area.kr);'
        f'way["power"="minor_line"](area.kr););'
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

    Korea-specific: direct OSM operator= tag propagation with Hangul
    + Latin RRK/M-R + English acronym cohabitation via Convention #78
    BINDING 8th enforcement alias map (100-entry KEPCO/KHNP/KPX/
    GENCOs/Chaebol captives normalization); if untagged, 4-layer
    KEPCO monopoly resolver (Layer 1 KHNP nuclear name-match OR
    Layer 2 industrial captive name-match OR Layer 3 admin → DSO
    (empirically ~0 hits) OR Layer 4 KEPCO catch-all default).
    NO Layer 3 geofence — KEPCO monopoly (Ireland/Greek/Costa Rica
    single-DSO precedent)."""
    coords = _center_lat_lon(el)
    if coords is None:
        return None
    lat, lon = coords
    tags = el.get("tags", {}) or {}

    osm_id = f"osm_{el.get('type', '?')}_{el.get('id', 0)}"
    voltage_kv = _parse_voltage_kv(tags.get("voltage"))
    name = tags.get("name") or tags.get("name:ko") or tags.get("name:en")

    op_tag = (tags.get("operator") or "").strip()

    if op_tag:
        owner = normalise_owner_alias(op_tag)
        owner_provenance = (
            "osm_operator_tag_direct_alias_normalised" if owner != op_tag
            else "osm_operator_tag_direct"
        )
    else:
        # 4-layer KEPCO monopoly resolver (Layer 1 nuclear → Layer 2
        # captive → Layer 3 admin → Layer 4 KEPCO catch-all)
        admin_code = (
            tags.get("addr:province")
            or tags.get("addr:state")
            or tags.get("is_in:province")
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
            "osm_name_ko": tags.get("name:ko"),
            "osm_name_en": tags.get("name:en"),
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
    name = tags.get("name") or tags.get("name:ko") or tags.get("name:en")

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


# ── Public entry ─────────────────────────────────────────────────────────
def fetch(
    *,
    apply_bounds: bool = True,
    ingest_lines: bool = True,
) -> IngestionResult:
    """Fetch OSM Korea substations + lines (single-query per element type).

    Moderate-scale country — no partitioning needed. Uses OSM operator=
    tag with Hangul + Latin RRK/M-R + English acronym cohabitation
    alias normalisation per Convention #78 BINDING 8th enforcement,
    then 4-layer KEPCO monopoly resolver (KHNP nuclear OR industrial
    captive OR admin default OR KEPCO catch-all) for untagged.
    Convention #56 preserved."""
    result = IngestionResult(
        source_id=SOURCE_ID,
        fetched_at_utc=now_utc_iso(),
        source_url=OVERPASS_ENDPOINTS[0],
        provincial_scope="KR",
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

    # ── Discipline #36 bounds filter (5.0 km coastline tolerance) ──
    if apply_bounds:
        subs_kept, subs_dropped = apply_bounds_filter(result.substations)
        lines_kept, lines_dropped = apply_bounds_filter(result.transmission_lines)
        result.substations = subs_kept
        result.transmission_lines = lines_kept
        if subs_dropped or lines_dropped:
            result.warnings.append(
                f"Discipline #36 — dropped {len(subs_dropped)} substations + "
                f"{len(lines_dropped)} lines outside Korea polygon "
                "(5.0 km coastline + island offset tolerance)."
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
        khnp_nuclear = prov_counter.get(
            "region_jurisdiction_layer_1_KHNP_nuclear_name_match", 0
        )
        captive = prov_counter.get(
            "region_jurisdiction_layer_2_industrial_captive_name_match", 0
        )
        kepco_default = sum(
            v for k, v in prov_counter.items()
            if k.startswith("region_jurisdiction_layer_4_KEPCO_monopoly_default")
            or k.startswith("region_jurisdiction_layer_3_KEPCO")
        )
        alias_normalised = prov_counter.get(
            "osm_operator_tag_direct_alias_normalised", 0
        )
        logger.info(
            "Owner enrichment: %d direct OSM (%d alias-normalised) + %d KHNP_nuclear + %d industrial_captive + %d KEPCO_monopoly_default",
            direct, alias_normalised, khnp_nuclear, captive, kepco_default,
        )
        result.warnings.append(
            f"Owner enrichment: {direct}/{len(result.substations)} direct "
            f"OSM operator= tag ({100 * direct / len(result.substations):.1f}%; "
            f"of these {alias_normalised} alias-normalised incl. Hangul (한국전력공사/한전/한국수력원자력) + Latin RRK (Hanguk Jeollyeok Gongsa) + Latin M-R (Han'guk Chŏllyŏk Kongsa) + English acronyms (KEPCO/KHNP/KPX/KDN) + Chaebol captives (POSCO/Samsung/SK Hynix/Hyundai/LG Chem) + Hangul legal-form (주식회사/㈜) + KECO pre-1982 predecessor per Convention #78 BINDING 8th enforcement); "
            f"{khnp_nuclear} KHNP_nuclear + {captive} industrial_captive + {kepco_default} KEPCO_monopoly_default "
            f"({100 * (khnp_nuclear + captive + kepco_default) / len(result.substations):.1f}%)."
        )

    # ── Discipline #41 parity ──
    parity_ok, findings = assert_line_parity(result, outbound_border_ok=False)
    for f in findings:
        logger.info("Discipline #41: %s", f)

    return result


# ── CLI harness ──────────────────────────────────────────────────────────
def _cli_main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="OSM Overpass KR L1 connector — Korea KEPCO monopoly 4-layer cascade (KHNP nuclear OR industrial captive OR admin default OR KEPCO catch-all) + Convention #78 BINDING 8th-enforcement test (Hangul + Latin RRK/M-R + English acronyms + Chaebol captives + KEPCO GENCOs + Hangul legal-form 주식회사/㈜ + KECO pre-1982 predecessor) — FIRST Asian Wave 3 event")
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
