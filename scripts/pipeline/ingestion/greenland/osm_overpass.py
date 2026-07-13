"""
SSI Pipeline — Greenland L1 connector: OSM Overpass API.

Source ID:   GL-C1-osm-overpass (primary — federal-canonical unavailable per Step 1)
Publisher:   OpenStreetMap contributors via Overpass API
Licence:     ODbL (Open Database License) — attribution required
Vintage:     Real-time (OSM Planet mirror)

Feature classes ingested (empirically anchored at Step 2 fetch probe):
  - power=substation      44 elements (14 nodes + 30 ways + 0 relations)
  - power=line             21 ways
  - power=minor_line       82 ways
  - power=cable            ~9 ways (retrying on 504 via endpoint rotation)

DIFFERENCE FROM AUSTRIA CONNECTOR:
  - NO bbox partitioning — Greenland small enough for single-query per class
    (44 subs + ~112 lines fit under Overpass soft payload cap).  Austria
    needed 4 bbox quadrants for 70,964 lines.
  - PURE MONOPOLY fallback rule: Nukissiorfiit for ALL untagged.  Unlike
    Austria (fragmented — untagged → None) and unlike Mexico (CFE with
    industrial self-gen exceptions).  Empirically confirmed: 100% of tagged
    operators = Nukissiorfiit (28/28 subs + 2/2 lines).
  - Lines are split by class in separate queries to avoid the 504 gateway
    error that combined out-geom queries trigger for medium-sized country
    scopes.

Convention #56 visibly-honest degradation:
  - Missing OSM voltage tag → voltage_kv = None (not 0.0)
  - PURE MONOPOLY fallback for owner is architecturally sound at 100%
    confidence (Nukissiorfiit is the SOLE utility) — but the fallback
    class is EXPLICITLY tagged in provenance so downstream audit sees the
    inference chain.

Convention #60 non-commercial provenance:
  - OSM (ODbL) only.  Nukissiorfiit public tariff schedules queued as
    Phase 2 supplement (PDF extraction, small delta expected).

Discipline #36 cross-border filter — 5 km Mode 2 fjord tolerance.
Discipline #41 line-substation pairing preserved.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
import urllib.request
import urllib.error
import urllib.parse
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
SOURCE_ID = "GL-C1-osm-overpass"
OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]

DEFAULT_TIMEOUT_SECS = 60
DEFAULT_QUERY_TIMEOUT_SECS = 50
USER_AGENT = "SSI-Index-Foundation/1.0 (+https://ikengassiindex.github.io)"

INITIAL_BACKOFF_SECS = 15
MAX_BACKOFF_SECS = 120
MAX_RETRY_ATTEMPTS = 3

# PURE MONOPOLY canonical name — used for owner fallback + operator_station_name prefix
NUKISSIORFIIT_CANONICAL_NAME = "Nukissiorfiit"


# ── Overpass HTTP ────────────────────────────────────────────────────────
def _fetch_overpass(query: str, timeout: int = DEFAULT_TIMEOUT_SECS) -> bytes:
    """POST query to Overpass with endpoint fallback + exponential backoff."""
    body = urllib.parse.urlencode({"data": query}).encode("utf-8")
    last_err: Exception | None = None
    for ep_idx, endpoint in enumerate(OVERPASS_ENDPOINTS):
        for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
            logger.info("Overpass POST %s (attempt %d/%d)", endpoint, attempt, MAX_RETRY_ATTEMPTS)
            req = urllib.request.Request(
                endpoint,
                data=body,
                headers={
                    "User-Agent": USER_AGENT,
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    return resp.read()
            except urllib.error.HTTPError as e:
                if e.code in (429, 504, 502, 503):
                    backoff = min(INITIAL_BACKOFF_SECS * (2 ** (attempt - 1)), MAX_BACKOFF_SECS)
                    logger.warning(
                        "Overpass %d %s; backoff %ds before retry",
                        e.code, endpoint, backoff,
                    )
                    time.sleep(backoff)
                    last_err = e
                    continue
                logger.warning("Overpass HTTP %d on %s; trying next endpoint after 5s", e.code, endpoint)
                last_err = e
                time.sleep(5)
                break
            except (urllib.error.URLError, TimeoutError) as e:
                logger.warning("Overpass timeout/URLError on %s: %s; trying next endpoint after 5s", endpoint, e)
                last_err = e
                time.sleep(5)
                break
    if last_err:
        raise last_err
    raise RuntimeError("All Overpass endpoints exhausted without response")


# ── Cached fetch ─────────────────────────────────────────────────────────
def _fetch_cached_or_live(query: str, cache_key: str) -> bytes:
    """Cache-first Overpass fetch — writes JSON to cache_path_for(cache_key) on live hit."""
    cache_path = cache_path_for(cache_key, ext=".json")
    if cache_path.exists():
        logger.info("Cache hit: %s (%d bytes)", cache_path.name, cache_path.stat().st_size)
        return cache_path.read_bytes()
    body = _fetch_overpass(query)
    cache_path.write_bytes(body)
    logger.info("Cache write: %s (%d bytes)", cache_path.name, len(body))
    return body


# ── Query builders ───────────────────────────────────────────────────────
def _query_substations() -> str:
    """All Greenland substations in one query (44 elements fits easily)."""
    return (
        f'[out:json][timeout:{DEFAULT_QUERY_TIMEOUT_SECS}];'
        'area["ISO3166-1"="GL"]->.gl;'
        '(node["power"="substation"](area.gl);'
        ' way["power"="substation"](area.gl);'
        ' relation["power"="substation"](area.gl);'
        ');'
        'out center tags;'
    )


def _query_lines(power_class: str) -> str:
    """Single-class line query (split to avoid 504 on combined out geom)."""
    return (
        f'[out:json][timeout:{DEFAULT_QUERY_TIMEOUT_SECS}];'
        'area["ISO3166-1"="GL"]->.gl;'
        f'way["power"="{power_class}"](area.gl);'
        'out geom tags;'
    )


# ── Record parsers ───────────────────────────────────────────────────────
def _parse_voltage_kv(raw: str | None) -> float | None:
    """Parse OSM voltage= tag (V or kV, semicolons for stacked step-downs)."""
    if not raw:
        return None
    # Take highest voltage in stacked "63000;10500" pattern (transmission side)
    parts = [p.strip() for p in raw.split(";") if p.strip()]
    if not parts:
        return None
    try:
        vals = [float(p) for p in parts]
    except ValueError:
        return None
    v = max(vals)
    # OSM stores in volts by convention; some outliers use kV.  Detect by magnitude:
    # any value <1000 assumed already-kV; >=1000 assumed volts.
    if v < 1000:
        return v
    return v / 1000.0


def _substation_from_osm(el: dict) -> SubstationRecord | None:
    """Normalise OSM substation element to SubstationRecord."""
    osm_type = el.get("type")
    osm_id = el.get("id")
    if not osm_id or osm_type not in ("node", "way", "relation"):
        return None

    # Coordinates: node has lat/lon; way/relation has center lat/lon via 'out center'
    if osm_type == "node":
        lat = el.get("lat")
        lon = el.get("lon")
    else:
        center = el.get("center") or {}
        lat = center.get("lat")
        lon = center.get("lon")
    if lat is None or lon is None:
        return None

    tags = el.get("tags", {}) or {}
    operator_raw = tags.get("operator")
    name = tags.get("name")
    voltage_kv = _parse_voltage_kv(tags.get("voltage"))
    substation_subtype = tags.get("substation")

    # ── PURE MONOPOLY fallback ──
    if operator_raw:
        owner = operator_raw
        owner_prov = "osm_operator_tag_direct"
    else:
        owner = NUKISSIORFIIT_CANONICAL_NAME
        owner_prov = "nukissiorfiit_monopoly_fallback"

    feature_id = f"osm_{osm_type}_{osm_id}"
    return SubstationRecord(
        source_id=SOURCE_ID,
        feature_id=feature_id,
        latitude=float(lat),
        longitude=float(lon),
        voltage_kv=voltage_kv,
        owner=owner,
        operator_station_name=name,
        raw_attributes={
            "osm_id": osm_id,
            "osm_type": osm_type,
            "osm_substation_subtype": substation_subtype,
            "osm_operator_raw": operator_raw,
            "owner_provenance": owner_prov,
            "osm_voltage_raw": tags.get("voltage"),
            "osm_name": name,
        },
    )


def _line_from_osm(el: dict) -> TransmissionLineRecord | None:
    """Normalise OSM power line element to TransmissionLineRecord."""
    osm_type = el.get("type")
    osm_id = el.get("id")
    if not osm_id or osm_type != "way":
        return None
    geom = el.get("geometry") or []
    if len(geom) < 2:
        return None
    # geom is list of {lat, lon} points; convert to [[lon,lat], ...]
    polyline = [[float(p["lon"]), float(p["lat"])] for p in geom if "lon" in p and "lat" in p]
    if len(polyline) < 2:
        return None
    # Wrap as MultiLineString per TransmissionLineRecord canonical shape
    coords_multi = [polyline]

    tags = el.get("tags", {}) or {}
    operator_raw = tags.get("operator")
    voltage_kv = _parse_voltage_kv(tags.get("voltage"))
    power_class = tags.get("power")
    name = tags.get("name")

    # ── PURE MONOPOLY fallback ──
    if operator_raw:
        owner = operator_raw
        owner_prov = "osm_operator_tag_direct"
    else:
        owner = NUKISSIORFIIT_CANONICAL_NAME
        owner_prov = "nukissiorfiit_monopoly_fallback"

    feature_id = f"osm_way_{osm_id}"
    return TransmissionLineRecord(
        source_id=SOURCE_ID,
        feature_id=feature_id,
        coordinates_multilinestring=coords_multi,
        voltage_kv=voltage_kv,
        owner=owner,
        line_name=name,
        raw_attributes={
            "osm_id": osm_id,
            "osm_type": "way",
            "osm_power_class": power_class,
            "osm_operator_raw": operator_raw,
            "owner_provenance": owner_prov,
            "osm_voltage_raw": tags.get("voltage"),
            "osm_cables": tags.get("cables"),
        },
    )


# ── Public entry ─────────────────────────────────────────────────────────
def fetch(
    *,
    apply_bounds: bool = True,
    ingest_lines: bool = True,
) -> IngestionResult:
    """Fetch OSM Greenland substations + lines.

    PURE MONOPOLY fallback rule applied to ALL untagged operator=
    substations + lines (Nukissiorfiit is 100% of the tagged population).
    Convention #56 provenance-class label makes the inference chain
    visible in downstream audit.
    """
    result = IngestionResult(
        source_id=SOURCE_ID,
        fetched_at_utc=now_utc_iso(),
        source_url=OVERPASS_ENDPOINTS[0],
        provincial_scope="GL",
    )

    # ── Substations (single query — small enough) ──
    all_sub_bytes = bytearray()
    try:
        body = _fetch_cached_or_live(
            _query_substations(),
            "https://overpass-api.de/api/interpreter::greenland_substations_v1",
        )
        all_sub_bytes.extend(body)
        data = json.loads(body)
        for el in data.get("elements", []):
            rec = _substation_from_osm(el)
            if rec is not None:
                result.substations.append(rec)
    except Exception as exc:
        result.warnings.append(
            f"Convention #56 partial — OSM substation fetch failed: {exc}"
        )

    result.raw_bytes_fetched = len(all_sub_bytes)
    result.raw_sha256 = hashlib.sha256(bytes(all_sub_bytes)).hexdigest()
    logger.info("Parsed %d substations from OSM Overpass", len(result.substations))

    # ── Lines (split by power class to avoid 504) ──
    if ingest_lines:
        for power_class in ("line", "minor_line", "cable"):
            cache_key = f"https://overpass-api.de/api/interpreter::greenland_lines_{power_class}_v1"
            try:
                body = _fetch_cached_or_live(_query_lines(power_class), cache_key)
            except Exception as exc:
                result.warnings.append(
                    f"Convention #56 partial — OSM lines power={power_class} fetch failed: {exc}"
                )
                continue
            try:
                data = json.loads(body)
            except json.JSONDecodeError as exc:
                result.warnings.append(
                    f"Convention #56 — OSM lines power={power_class} JSON parse error: {exc}"
                )
                continue
            for el in data.get("elements", []):
                rec = _line_from_osm(el)
                if rec is not None:
                    result.transmission_lines.append(rec)
            logger.info(
                "Parsed lines power=%s: %d cumulative",
                power_class, len(result.transmission_lines),
            )

    # ── Discipline #36 bounds filter (5 km Mode 2 fjord) ──
    if apply_bounds:
        subs_kept, subs_dropped = apply_bounds_filter(result.substations)
        lines_kept, lines_dropped = apply_bounds_filter(result.transmission_lines)
        result.substations = subs_kept
        result.transmission_lines = lines_kept
        if subs_dropped or lines_dropped:
            result.warnings.append(
                f"Discipline #36 — dropped {len(subs_dropped)} substations + "
                f"{len(lines_dropped)} lines outside Greenland polygon "
                "(5 km Mode 2 fjord tolerance)."
            )

    # ── Owner enrichment summary ──
    if result.substations:
        direct_tagged = sum(
            1 for s in result.substations
            if s.raw_attributes.get("owner_provenance") == "osm_operator_tag_direct"
        )
        monopoly_fallback = sum(
            1 for s in result.substations
            if s.raw_attributes.get("owner_provenance") == "nukissiorfiit_monopoly_fallback"
        )
        logger.info(
            "Owner enrichment: %d direct OSM tags + %d PURE MONOPOLY fallback (Nukissiorfiit)",
            direct_tagged, monopoly_fallback,
        )
        result.warnings.append(
            f"Owner enrichment: {direct_tagged}/{len(result.substations)} "
            f"substations attributed via direct OSM operator= tag "
            f"({100 * direct_tagged / len(result.substations):.1f}%); "
            f"{monopoly_fallback} untagged filled via PURE MONOPOLY fallback rule "
            "(Nukissiorfiit — 100% concentration confirmed empirically at Step 2)."
        )

    # ── Discipline #41 parity ──
    # Greenland is a validation workstream — line count may be LOWER than
    # substation count because baseline has richer coverage than OSM.
    # min_line_ratio=0.3 accommodates the ~112 lines / 44 subs = 2.5 empirical
    # ratio observed at Step 2 fetch probe.
    parity_ok, findings = assert_line_parity(
        result,
        outbound_border_ok=False,
        min_line_ratio=0.3,
    )
    for f in findings:
        logger.info("Discipline #41: %s", f)
        result.warnings.append(f"Discipline #41: {f}")

    return result


if __name__ == "__main__":
    import argparse
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser(description="Greenland L1 OSM Overpass connector")
    parser.add_argument("--skip-lines", action="store_true")
    parser.add_argument("--no-bounds", action="store_true")
    args = parser.parse_args()

    result = fetch(
        apply_bounds=not args.no_bounds,
        ingest_lines=not args.skip_lines,
    )
    print()
    print(f"Substations: {len(result.substations)}")
    print(f"Lines:       {len(result.transmission_lines)}")
    print(f"SHA-256:     {result.raw_sha256}")
    print(f"Warnings ({len(result.warnings)}):")
    for w in result.warnings:
        print(f"  - {w}")
