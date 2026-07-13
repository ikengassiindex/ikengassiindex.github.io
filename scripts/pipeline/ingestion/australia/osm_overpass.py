"""
SSI Pipeline — Australia L1 connector: OSM Overpass API.

Source ID:   AU-C1-osm-overpass (primary — federal-canonical unavailable per Step 1)
Publisher:   OpenStreetMap contributors via Overpass API
Licence:     ODbL (Open Database License) — attribution required
Vintage:     Real-time (OSM Planet mirror)

Feature classes ingested:
  - power=substation      expected 8k-12k elements
  - power=line             expected 30k-70k ways
  - power=cable            few (underground urban)
  - power=minor_line       moderate (MV distribution)

DIFFERENCE FROM AUSTRIA CONNECTOR:
  - CONTINENTAL SCALE — Australia is 7.7M km² (94× Austria). Substation
    queries split by state/territory (not by element type) because Overpass
    504 gateway on continent-wide queries. Line queries split into 8
    partitions (one per state/territory) with generous inter-request delay.

  - STATE-JURISDICTION OWNER FALLBACK — Australia has a federal-fragmented
    grid (AEMO NEM + WEM + 5 state DNSPs). For substations without a direct
    OSM operator= tag, we derive owner from (state, voltage class) per the
    mapping in _base.py::resolve_owner_from_state_jurisdiction. This is
    distinct from Austria (no fallback rule) + Greenland (pure monopoly
    Nukissiorfiit) — a 3rd class of fallback pattern.

  - Same architecture otherwise: rate-limit backoff, 3-endpoint fallback
    (overpass-api.de → overpass.kumi.systems → overpass.private.coffee).

Convention #56 visibly-honest degradation:
  - Missing OSM voltage tag → voltage_kv = None (not 0.0)
  - Missing operator tag → owner via state fallback (never fabricated)
  - VIC multi-DNSP unresolved → "Victoria DNSP (unresolved multi-provider)"
    (explicit — see Convention #56 provenance tag)
  - Overpass 429/504 → exponential backoff; graceful degradation to empty result

Convention #60 non-commercial provenance:
  - OSM (ODbL) only. AEMO/AER wholesale-market data queued as informational
    cross-validation, not asset-level canonical.

Discipline #36 cross-border filter — 100m default tolerance (per _base).
Discipline #41 line-substation pairing preserved (assert at end of fetch).
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
    resolve_owner_from_state_jurisdiction,
)

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────
SOURCE_ID = "AU-C1-osm-overpass"
OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]

DEFAULT_TIMEOUT_SECS = 180  # continental scale — longer than AT/GL
DEFAULT_QUERY_TIMEOUT_SECS = 120
USER_AGENT = "SSI-Index-Foundation/1.0 (+https://ikengassiindex.github.io)"

# Rate-limit backoff
INITIAL_BACKOFF_SECS = 30
MAX_BACKOFF_SECS = 300
MAX_RETRY_ATTEMPTS = 4

# Continental-scale considerate delay (avoid hammering public Overpass)
INTER_STATE_DELAY_SECS = 15

# Per-state bboxes (south, west, north, east, state_code)
# Precomputed to cover mainland + Tasmania + coastal islands. Cross-border
# filter (Discipline #36) trims any overshoot at the polygon boundary.
_AU_STATE_BBOXES = [
    # (south, west, north, east, state, note)
    (-37.5, 140.9, -28.2, 153.7, "NSW", "New South Wales + ACT bubble"),
    (-29.3, 137.8, -10.0, 153.8, "QLD", "Queensland — north-east coast + Cape York"),
    (-39.2, 140.9, -33.9, 150.1, "VIC", "Victoria — south-east mainland"),
    (-35.2, 112.7, -13.5, 129.1, "WA",  "Western Australia — full west + Kimberley"),
    (-38.1, 128.9, -25.9, 141.1, "SA",  "South Australia + islands"),
    (-43.7, 143.7, -39.5, 148.5, "TAS", "Tasmania + islands"),
    (-25.9, 129.0, -10.9, 138.1, "NT",  "Northern Territory"),
    (-35.94, 148.75, -35.12, 149.42, "ACT", "Australian Capital Territory bubble"),
]


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
                        "Overpass %d gateway; trying next endpoint after 10s",
                        exc.code,
                    )
                    time.sleep(10)
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
                logger.warning("Overpass network error: %s; trying next endpoint after 10s", exc)
                time.sleep(10)
                break

    if last_err is not None:
        raise last_err
    raise RuntimeError("Overpass fetch failed on all endpoints without a specific error")


# ── Query builders ──────────────────────────────────────────────────────
def _query_substations_bbox(south: float, west: float, north: float, east: float) -> str:
    """Substations query for one state bbox.

    Fetches all 3 element types (way/node/relation) in a single query per
    state — continental partitioning replaces Austria's per-element split.
    """
    return (
        f'[out:json][timeout:{DEFAULT_QUERY_TIMEOUT_SECS}];'
        f'(way["power"="substation"]({south},{west},{north},{east});'
        f'node["power"="substation"]({south},{west},{north},{east});'
        f'relation["power"="substation"]({south},{west},{north},{east}););'
        f'out center tags;'
    )


def _query_lines_bbox(south: float, west: float, north: float, east: float) -> str:
    """Lines query for one state bbox."""
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

    Australia-specific: direct OSM operator= tag propagation; if untagged,
    apply state-jurisdiction fallback per _base.py::resolve_owner_from_state_jurisdiction.
    """
    coords = _center_lat_lon(el)
    if coords is None:
        return None
    lat, lon = coords
    tags = el.get("tags", {}) or {}

    osm_id = f"osm_{el.get('type', '?')}_{el.get('id', 0)}"
    voltage_kv = _parse_voltage_kv(tags.get("voltage"))

    # Owner: direct OSM operator= tag, then state fallback
    op_tag = (tags.get("operator") or "").strip()
    osm_state = tags.get("addr:state")
    if op_tag:
        owner = op_tag
        owner_provenance = "osm_operator_tag_direct"
    else:
        owner, owner_provenance = resolve_owner_from_state_jurisdiction(
            lat, lon, voltage_kv, osm_state=osm_state
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
    max_states: int | None = None,
    inter_state_delay: float = INTER_STATE_DELAY_SECS,
) -> IngestionResult:
    """Fetch OSM Australia substations + lines with 8-state bbox partitioning.

    Uses OSM operator= tag when present; falls back to state-jurisdiction
    mapping for untagged substations per Convention #56 discipline
    (visibly-honest — never fabricates owner beyond documented state fallback).
    """
    result = IngestionResult(
        source_id=SOURCE_ID,
        fetched_at_utc=now_utc_iso(),
        source_url=OVERPASS_ENDPOINTS[0],
        provincial_scope="AU",
    )

    states = _AU_STATE_BBOXES if max_states is None else _AU_STATE_BBOXES[:max_states]

    all_sub_bytes = bytearray()

    # ── Substations (per-state bbox partition) ──
    for i, (south, west, north, east, state, note) in enumerate(states):
        try:
            body = _fetch_overpass(_query_substations_bbox(south, west, north, east))
        except Exception as exc:
            result.warnings.append(
                f"Convention #56 partial — OSM substations {state} fetch failed: {exc}"
            )
            if i < len(states) - 1:
                time.sleep(inter_state_delay)
            continue
        all_sub_bytes.extend(body)
        try:
            data = json.loads(body)
        except json.JSONDecodeError as exc:
            result.warnings.append(
                f"Convention #56 — OSM substations {state} JSON parse error: {exc}"
            )
            continue
        state_count = 0
        for el in data.get("elements", []):
            rec = _substation_from_osm(el)
            if rec is not None:
                result.substations.append(rec)
                state_count += 1
        logger.info("Parsed %d substations from %s (%s)", state_count, state, note)
        if i < len(states) - 1:
            time.sleep(inter_state_delay)

    result.raw_bytes_fetched = len(all_sub_bytes)
    result.raw_sha256 = hashlib.sha256(bytes(all_sub_bytes)).hexdigest()
    logger.info("Parsed %d substations total from OSM Overpass", len(result.substations))

    # ── Lines (per-state bbox partition) ──
    if ingest_lines:
        for i, (south, west, north, east, state, note) in enumerate(states):
            try:
                body = _fetch_overpass(_query_lines_bbox(south, west, north, east))
            except Exception as exc:
                result.warnings.append(
                    f"Convention #56 partial — OSM lines {state} fetch failed: {exc}"
                )
                if i < len(states) - 1:
                    time.sleep(inter_state_delay)
                continue
            try:
                data = json.loads(body)
            except json.JSONDecodeError as exc:
                result.warnings.append(
                    f"Convention #56 — OSM lines {state} JSON parse error: {exc}"
                )
                continue
            state_count = 0
            for el in data.get("elements", []):
                rec = _line_from_osm(el)
                if rec is not None:
                    result.transmission_lines.append(rec)
                    state_count += 1
            logger.info(
                "Parsed %d lines from %s (%d cumulative)",
                state_count, state, len(result.transmission_lines),
            )
            if i < len(states) - 1:
                time.sleep(inter_state_delay)

    # ── Discipline #36 bounds filter ──
    if apply_bounds:
        subs_kept, subs_dropped = apply_bounds_filter(result.substations)
        lines_kept, lines_dropped = apply_bounds_filter(result.transmission_lines)
        result.substations = subs_kept
        result.transmission_lines = lines_kept
        if subs_dropped or lines_dropped:
            result.warnings.append(
                f"Discipline #36 — dropped {len(subs_dropped)} substations + "
                f"{len(lines_dropped)} lines outside Australia polygon "
                "(100m default tolerance)."
            )

    # ── Owner enrichment summary ──
    if result.substations:
        from collections import Counter
        prov_counter = Counter(
            s.raw_attributes.get("owner_provenance", "none")
            for s in result.substations
        )
        direct = prov_counter.get("osm_operator_tag_direct", 0)
        state_fallback = sum(
            v for k, v in prov_counter.items() if k.startswith("state_fallback")
        )
        unresolved = sum(
            v for k, v in prov_counter.items() if k.startswith("state_unresolved")
        )
        logger.info(
            "Owner enrichment: %d direct OSM + %d state_fallback + %d unresolved",
            direct, state_fallback, unresolved,
        )
        result.warnings.append(
            f"Owner enrichment: {direct}/{len(result.substations)} direct "
            f"OSM operator= tag ({100 * direct / len(result.substations):.1f}%); "
            f"{state_fallback} state_jurisdiction_fallback "
            f"({100 * state_fallback / len(result.substations):.1f}%); "
            f"{unresolved} unresolved (Convention #56 preserved as None)."
        )

    # ── Discipline #41 parity ──
    parity_ok, findings = assert_line_parity(result, outbound_border_ok=False)
    for f in findings:
        logger.info("Discipline #41: %s", f)

    return result


# ── CLI harness ──────────────────────────────────────────────────────────
def _cli_main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="OSM Overpass AU L1 connector")
    parser.add_argument("--skip-lines", action="store_true",
                        help="Skip line ingestion (subs only)")
    parser.add_argument("--max-states", type=int, default=None,
                        help="Cap number of state partitions (for smoke testing)")
    parser.add_argument("--no-bounds", action="store_true",
                        help="Skip Discipline #36 filter")
    parser.add_argument("--inter-state-delay", type=float, default=INTER_STATE_DELAY_SECS,
                        help="Delay (secs) between per-state Overpass fetches")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    result = fetch(
        apply_bounds=not args.no_bounds,
        ingest_lines=not args.skip_lines,
        max_states=args.max_states,
        inter_state_delay=args.inter_state_delay,
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
        print(f"    {v:>6}  {k}")

    ops = Counter(s.owner for s in result.substations if s.owner)
    print(f"  Distinct operators: {len(ops)}")
    print("  Top 15 operators:")
    for k, v in ops.most_common(15):
        print(f"    {v:>6}  {k}")

    for w in result.warnings:
        print(f"  ⚠ {w}")


if __name__ == "__main__":
    _cli_main()
