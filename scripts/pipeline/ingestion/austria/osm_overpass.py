"""
SSI Pipeline — Austria L1 connector: OSM Overpass API.

Source ID:   AT-C1-osm-overpass (primary — federal-canonical unavailable per Step 1)
Publisher:   OpenStreetMap contributors via Overpass API
Licence:     ODbL (Open Database License) — attribution required
Vintage:     Real-time (OSM Planet mirror)

Feature classes ingested (empirically anchored at Step 1 preflight):
  - power=substation      15,213 elements (1,676 nodes + 13,528 ways + 9 relations)
  - power=line             5,651 ways
  - power=cable            few (mostly underground urban)
  - power=minor_line       moderate (small distribution branches)

DIFFERENCE FROM MEXICO CONNECTOR:
  - NO CFE-monopoly fallback rule.  Austrian market structure is FRAGMENTED
    across 9+ distinct utility owners (APG TSO + 8 Bundesland DSOs + ÖBB
    railway traction).  Direct OSM operator= tag propagation covers 77.2% by
    construction (empirical from 500-sample).  Convention #56 visibly-honest
    degradation applies to the ~23% untagged tail — owner stays None.

  - Same architecture otherwise: rate-limit backoff (exponential to 5min cap),
    3-endpoint fallback (overpass-api.de → overpass.kumi.systems →
    overpass.private.coffee), bbox-partitioned line queries, split-by-element-
    type substation queries to avoid single-query 504.

Convention #56 visibly-honest degradation:
  - Missing OSM voltage tag → voltage_kv = None (not 0.0)
  - Missing operator tag → owner = None (do NOT fabricate default)
  - Overpass 429/504 → exponential backoff; graceful degradation to empty result

Convention #60 non-commercial provenance:
  - OSM (ODbL) only.  ENTSO-E Transparency Platform (open, needs token) queued
    as Phase 2 supplement.

Discipline #36 cross-border filter — 100m default tolerance.
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
from pathlib import Path

from ._base import (
    SubstationRecord,
    TransmissionLineRecord,
    IngestionResult,
    apply_bounds_filter,
    assert_line_parity,
    emit_audit_sidecar,
    cache_path_for,
    now_utc_iso,
)

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────
SOURCE_ID = "AT-C1-osm-overpass"
OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]

DEFAULT_TIMEOUT_SECS = 120
DEFAULT_QUERY_TIMEOUT_SECS = 90
USER_AGENT = "SSI-Index-Foundation/1.0 (+https://ikengassiindex.github.io)"

# Rate-limit backoff
INITIAL_BACKOFF_SECS = 30
MAX_BACKOFF_SECS = 300
MAX_RETRY_ATTEMPTS = 4

# Austria bbox: approximately (46.4, 9.5) to (49.0, 17.2)
# 4-quadrant partition (center 47.7, 13.35)
_AT_LINE_QUADRANTS = [
    (46.4, 9.5, 47.7, 13.35, "SW"),
    (47.7, 9.5, 49.0, 13.35, "NW"),
    (46.4, 13.35, 47.7, 17.2, "SE"),
    (47.7, 13.35, 49.0, 17.2, "NE"),
]


# ── HTTP fetch with rate-limit backoff ──────────────────────────────────
def _fetch_overpass(query: str, timeout: int = DEFAULT_TIMEOUT_SECS) -> bytes:
    """Fetch Overpass query with retry + endpoint fallback.

    Same pattern as Mexico's connector.  Handles 429 with exponential backoff,
    504 with fallback endpoint, 406 with retry.
    """
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
                    logger.warning("Overpass 406; retry with plain Accept in 5s")
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
_AT_AREA_HEADER = 'area["ISO3166-1"="AT"]->.at'


def _query_substations(feature_type: str = "way") -> str:
    """Build Overpass query for one substation element type.

    Split by type (way / node / relation) because single-query full-country
    fetch triggers 504 gateway timeouts on public Overpass endpoints.
    """
    return (
        f'[out:json][timeout:{DEFAULT_QUERY_TIMEOUT_SECS}];'
        f'{_AT_AREA_HEADER};'
        f'{feature_type}["power"="substation"](area.at);'
        f'out center tags;'
    )


def _query_lines_bbox(south: float, west: float, north: float, east: float) -> str:
    """Build Overpass query for lines in a bbox."""
    return (
        f'[out:json][timeout:{DEFAULT_QUERY_TIMEOUT_SECS}];'
        f'(way["power"="line"]({south},{west},{north},{east});'
        f'way["power"="cable"]({south},{west},{north},{east});'
        f'way["power"="minor_line"]({south},{west},{north},{east}););'
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

    Returns MAX kV if multi-valued.
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
    """Parse OSM substation element to SubstationRecord.

    NO monopoly-fallback rule — direct OSM operator= tag propagation only.
    Convention #56 visibly-honest degradation: missing operator → owner=None.
    """
    coords = _center_lat_lon(el)
    if coords is None:
        return None
    lat, lon = coords
    tags = el.get("tags", {}) or {}

    osm_id = f"osm_{el.get('type', '?')}_{el.get('id', 0)}"
    voltage_kv = _parse_voltage_kv(tags.get("voltage"))

    # Owner: direct OSM operator= tag propagation, no fallback rule
    op_tag = (tags.get("operator") or "").strip()
    owner = op_tag if op_tag else None
    owner_provenance = (
        "osm_operator_tag_direct" if op_tag else "convention_56_no_operator_tagged"
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
        },
    )


def _line_from_osm(el: dict) -> TransmissionLineRecord | None:
    """Parse OSM power=line element to TransmissionLineRecord."""
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
    owner = op_tag if op_tag else None

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
    max_line_quadrants: int | None = None,
) -> IngestionResult:
    """Fetch OSM Austria substations + lines.

    Direct OSM operator= tag propagation (no monopoly fallback rule since
    Austrian market is FRAGMENTED across 9+ distinct utilities).  Convention
    #56 visibly-honest degradation for ~23% untagged tail.
    """
    result = IngestionResult(
        source_id=SOURCE_ID,
        fetched_at_utc=now_utc_iso(),
        source_url=OVERPASS_ENDPOINTS[0],
        provincial_scope="AT",
    )

    # ── Substations (split by element type to avoid 504) ──
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

    # ── Lines (bbox-partitioned quadrants) ──
    if ingest_lines:
        quadrants = _AT_LINE_QUADRANTS
        if max_line_quadrants is not None:
            quadrants = quadrants[:max_line_quadrants]
        for (south, west, north, east, label) in quadrants:
            try:
                body = _fetch_overpass(_query_lines_bbox(south, west, north, east))
            except Exception as exc:
                result.warnings.append(
                    f"Convention #56 partial — OSM lines quadrant {label} fetch failed: {exc}"
                )
                continue
            try:
                data = json.loads(body)
            except json.JSONDecodeError as exc:
                result.warnings.append(
                    f"Convention #56 — OSM lines {label} JSON parse error: {exc}"
                )
                continue
            for el in data.get("elements", []):
                rec = _line_from_osm(el)
                if rec is not None:
                    result.transmission_lines.append(rec)
            logger.info(
                "Parsed lines from quadrant %s: %d cumulative",
                label, len(result.transmission_lines),
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
                f"{len(lines_dropped)} lines outside Austria polygon "
                "(100m default tolerance)."
            )

    # ── Owner enrichment summary ──
    if result.substations:
        direct_tagged = sum(
            1 for s in result.substations
            if s.raw_attributes.get("owner_provenance") == "osm_operator_tag_direct"
        )
        untagged = sum(
            1 for s in result.substations
            if s.raw_attributes.get("owner_provenance") == "convention_56_no_operator_tagged"
        )
        logger.info(
            "Owner enrichment: %d direct OSM tags + %d Convention #56 untagged tail",
            direct_tagged, untagged,
        )
        result.warnings.append(
            f"Owner enrichment: {direct_tagged}/{len(result.substations)} "
            f"substations attributed via direct OSM operator= tag "
            f"({100 * direct_tagged / len(result.substations):.1f}%); "
            f"{untagged} untagged preserved as owner=None per Convention #56 "
            "(NO monopoly fallback — Austrian market is fragmented)."
        )

    # ── Discipline #41 parity ──
    parity_ok, findings = assert_line_parity(result, outbound_border_ok=False)
    for f in findings:
        logger.info("Discipline #41: %s", f)

    return result


# ── CLI harness ──────────────────────────────────────────────────────────
def _cli_main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="OSM Overpass AT L1 connector")
    parser.add_argument("--skip-lines", action="store_true",
                        help="Skip line ingestion (subs only)")
    parser.add_argument("--max-quadrants", type=int, default=None,
                        help="Cap number of line quadrants")
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
        max_line_quadrants=args.max_quadrants,
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

    # Top operators
    ops = Counter(s.owner for s in result.substations if s.owner)
    print(f"  Distinct operators: {len(ops)}")
    print("  Top 10 operators:")
    for k, v in ops.most_common(10):
        print(f"    {v:>5}  {k}")

    for w in result.warnings:
        print(f"  ⚠ {w}")


if __name__ == "__main__":
    _cli_main()
