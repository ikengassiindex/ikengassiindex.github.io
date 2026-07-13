"""
SSI Pipeline — Norway L1 connector: NVE Nettanlegg WFS.

Source ID:   NO-C1-nve-nettanlegg (federal-canonical, primary)
Publisher:   NVE (Norges vassdrags- og energidirektorat)
Endpoint:    http://wfs.geonorge.no/skwms1/wfs.nettanlegg
Licence:     Norwegian Licence for Open Government Data (NLOD 2.0)
Vintage:     Continuously updated; per-feature kildeEndretDato timestamps.

Feature classes ingested (from norway/v4_3-ingestion-audit-norway-fetch.yaml):
  - app:EL_Transformatorstasjon    1,558 substations
  - app:EL_Luftlinje             145,460 overhead lines w/ spenning
  - app:EL_Sjøkabel                8,747 submarine cables

Field schema per norway/v4_3-ingestion-audit-norway-line-schema.yaml:
  Substation: gml_id, driftsattår, eier, eierOrgnr, lokalId, navn, posisjon
  Line:       gml_id, driftsattår, eier, eierOrgnr, lokalId, navn, nettnivå,
              spenning (VOLTAGE IN kV — 99.78% completeness), linje (geometry)

REVERSE DISCIPLINE #41 VOLTAGE INHERITANCE:
  Substation voltage_kv is derived by joining line endpoints to substation
  centers within 500m proximity.  When a substation is within 500m of one or
  more line endpoints, it inherits the MAX voltage of those endpoints.  This
  closes the substation-voltage gap that Refutation #3 (Step 2) surfaced,
  since NVE's Transformatorstasjon schema itself lacks a voltage field.

Convention #56 visibly-honest degradation:
  - Missing spenning on a line → voltage_kv = None (not 0.0 default)
  - Substation with no line endpoints within 500m → voltage_kv remains None
  - WFS timeout / 5xx → returns empty IngestionResult with warning listing
    the Discipline reference; federation layer proceeds with remaining sources.

Convention #60 non-commercial provenance:
  - Only NVE + Statnett + OSM used (see federation layer).  No commercial ESG
    or utility-inventory paid feeds.
"""

from __future__ import annotations

import hashlib
import logging
import math
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
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
SOURCE_ID = "NO-C1-nve-nettanlegg"
WFS_ENDPOINT = "http://wfs.geonorge.no/skwms1/wfs.nettanlegg"
WFS_VERSION = "2.0.0"

FEATURE_TYPE_SUBSTATION = "app:EL_Transformatorstasjon"
FEATURE_TYPE_LUFTLINJE = "app:EL_Luftlinje"
FEATURE_TYPE_SJOKABEL = "app:EL_Sjøkabel"

# WFS pagination: NVE server tolerates count=1000 batches comfortably.
# Substations at 1,558 fit in 2 pages; lines at 145,460 need ~146 pages.
DEFAULT_PAGE_SIZE = 1000
DEFAULT_TIMEOUT_SECS = 120
USER_AGENT = "SSI-Index-Foundation/1.0 (+https://ikengassiindex.github.io)"

# XML namespaces (empirically extracted from GML samples)
_NS = {
    "wfs": "http://www.opengis.net/wfs/2.0",
    "gml": "http://www.opengis.net/gml/3.2",
    "app": "http://skjema.geonorge.no/SOSI/produktspesifikasjon/Nettanlegg/1.0",
    "ows": "http://www.opengis.net/ows/1.1",
}

# Discipline #41 reverse-inheritance proximity threshold
LINE_ENDPOINT_JOIN_METERS = 500.0

# ── HTTP fetch (paged WFS) ───────────────────────────────────────────────
def _build_wfs_url(feature_type: str, *, count: int, start_index: int) -> str:
    from urllib.parse import quote
    return (
        f"{WFS_ENDPOINT}?service=WFS&version={WFS_VERSION}&request=GetFeature"
        f"&typeName={quote(feature_type)}&count={count}&startIndex={start_index}"
    )


def _fetch_wfs_page(
    feature_type: str,
    *,
    start_index: int,
    count: int = DEFAULT_PAGE_SIZE,
    timeout: int = DEFAULT_TIMEOUT_SECS,
) -> bytes:
    """Fetch one WFS GetFeature page.  Uses SHA-256-keyed cache."""
    url = _build_wfs_url(feature_type, count=count, start_index=start_index)
    cache = cache_path_for(url)
    if cache.exists():
        body = cache.read_bytes()
        logger.info("Cache hit: %s (%d bytes)", cache.name, len(body))
        return body
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    logger.info("Fetching %s startIndex=%d count=%d ...", feature_type, start_index, count)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
    cache.write_bytes(body)
    return body


# ── XML parsing helpers ──────────────────────────────────────────────────
def _text(el: ET.Element | None) -> str | None:
    if el is None or el.text is None:
        return None
    t = el.text.strip()
    return t or None


def _float(el: ET.Element | None) -> float | None:
    t = _text(el)
    if t is None:
        return None
    try:
        return float(t)
    except ValueError:
        return None


def _int(el: ET.Element | None) -> int | None:
    t = _text(el)
    if t is None:
        return None
    try:
        return int(t)
    except ValueError:
        return None


def _find_ns(el: ET.Element, path: str) -> ET.Element | None:
    """Find first element by ns-prefixed path (e.g. 'app:eier' or 'app:identifikasjon/app:Identifikasjon/app:lokalId')."""
    return el.find(path, _NS)


def _parse_pos_list(text: str) -> list[list[float]]:
    """Parse GML posList (space-separated 'lat lon lat lon ...') to [[lon, lat], ...] WGS84."""
    tokens = text.strip().split()
    coords: list[list[float]] = []
    for i in range(0, len(tokens) - 1, 2):
        try:
            lat = float(tokens[i])
            lon = float(tokens[i + 1])
            coords.append([lon, lat])  # canonical GeoJSON order
        except ValueError:
            continue
    return coords


def _parse_linje_geometry(linje_el: ET.Element) -> list[list[list[float]]]:
    """Parse app:linje sub-element into MultiLineString-shaped coordinates.

    Handles both single LineString and MultiCurve/curveMember/LineString.
    """
    multiline: list[list[list[float]]] = []
    for ls in linje_el.iter(f"{{{_NS['gml']}}}LineString"):
        pos_el = ls.find(f"{{{_NS['gml']}}}posList")
        if pos_el is None or not pos_el.text:
            continue
        coords = _parse_pos_list(pos_el.text)
        if len(coords) >= 2:
            multiline.append(coords)
    return multiline


# ── Substation parsing ───────────────────────────────────────────────────
def _substation_from_gml(feature_el: ET.Element) -> SubstationRecord | None:
    """Parse EL_Transformatorstasjon feature into SubstationRecord."""
    gml_id = feature_el.get(f"{{{_NS['gml']}}}id") or ""
    eier = _text(_find_ns(feature_el, "app:eier"))
    eier_orgnr = _text(_find_ns(feature_el, "app:eierOrgnr"))
    lokal_id = _text(_find_ns(feature_el, "app:identifikasjon/app:Identifikasjon/app:lokalId"))
    navn = _text(_find_ns(feature_el, "app:navn"))
    kilde_dato = _text(_find_ns(feature_el, "app:kildeEndretDato"))
    driftsatt = _int(_find_ns(feature_el, "app:driftsattår"))

    # Position: <app:posisjon><gml:Point srsName="urn:ogc:def:crs:EPSG::4258"><gml:pos>lat lon</gml:pos></gml:Point></app:posisjon>
    posisjon = _find_ns(feature_el, "app:posisjon")
    if posisjon is None:
        return None
    pos_el = posisjon.find(f"{{{_NS['gml']}}}Point/{{{_NS['gml']}}}pos")
    if pos_el is None or not pos_el.text:
        return None
    try:
        lat_str, lon_str = pos_el.text.strip().split()[:2]
        lat = float(lat_str)
        lon = float(lon_str)
    except (ValueError, IndexError):
        return None

    return SubstationRecord(
        source_id=SOURCE_ID,
        feature_id=lokal_id or gml_id,
        latitude=lat,
        longitude=lon,
        voltage_kv=None,  # not on substation schema — reverse-inherited from lines
        owner=eier,
        operator_station_name=navn,
        temporal_extent_min=str(driftsatt) if driftsatt else None,
        temporal_extent_max=kilde_dato,
        raw_attributes={
            "gml_id": gml_id,
            "eier": eier,
            "eierOrgnr": eier_orgnr,
            "lokalId": lokal_id,
            "navn": navn,
            "driftsattår": driftsatt,
            "kildeEndretDato": kilde_dato,
        },
    )


# ── Line parsing (Luftlinje + Sjøkabel share schema) ─────────────────────
def _line_from_gml(feature_el: ET.Element, source_tag: str) -> TransmissionLineRecord | None:
    """Parse EL_Luftlinje or EL_Sjøkabel feature into TransmissionLineRecord."""
    gml_id = feature_el.get(f"{{{_NS['gml']}}}id") or ""
    eier = _text(_find_ns(feature_el, "app:eier"))
    eier_orgnr = _text(_find_ns(feature_el, "app:eierOrgnr"))
    lokal_id = _text(_find_ns(feature_el, "app:identifikasjon/app:Identifikasjon/app:lokalId"))
    navn = _text(_find_ns(feature_el, "app:navn"))
    nettniva = _text(_find_ns(feature_el, "app:nettnivå"))
    spenning = _float(_find_ns(feature_el, "app:spenning"))
    driftsatt = _int(_find_ns(feature_el, "app:driftsattår"))
    kilde_dato = _text(_find_ns(feature_el, "app:kildeEndretDato"))

    linje = _find_ns(feature_el, "app:linje")
    if linje is None:
        return None
    multiline = _parse_linje_geometry(linje)
    if not multiline:
        return None

    return TransmissionLineRecord(
        source_id=SOURCE_ID,
        feature_id=lokal_id or gml_id,
        coordinates_multilinestring=multiline,
        voltage_kv=spenning,           # 99.78% completeness on Luftlinje per Step 2b
        owner=eier,
        line_name=navn,
        raw_attributes={
            "gml_id": gml_id,
            "source_tag": source_tag,   # "luftlinje" | "sjokabel"
            "eier": eier,
            "eierOrgnr": eier_orgnr,
            "lokalId": lokal_id,
            "navn": navn,
            "nettnivå": nettniva,
            "spenning_kv": spenning,
            "driftsattår": driftsatt,
            "kildeEndretDato": kilde_dato,
        },
    )


# ── Reverse Discipline #41 — line-endpoint → substation voltage inheritance ──
def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in metres."""
    R = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def _propagate_voltage_to_substations(
    substations: list[SubstationRecord],
    lines: list[TransmissionLineRecord],
    *,
    join_meters: float = LINE_ENDPOINT_JOIN_METERS,
) -> int:
    """Reverse Discipline #41: propagate line spenning to endpoint substations.

    For each line with voltage_kv populated, extract start and end endpoints
    from the MultiLineString.  For each substation within join_meters of any
    endpoint, record the line voltage.  Substation.voltage_kv is set to the
    MAX of collected line voltages (a station's operating voltage class is
    the highest incident line voltage).

    Provenance is recorded in substation.raw_attributes['v43_voltage_inheritance']:
        {
          "sources": [{"line_lokal_id": ..., "spenning_kv": ..., "distance_m": ...}, ...],
          "chosen_voltage_kv": ...,
        }

    Returns:
        Count of substations enriched with voltage_kv.
    """
    # Extract line endpoints with voltage
    endpoints: list[tuple[float, float, float, str]] = []  # (lat, lon, voltage_kv, line_id)
    for ln in lines:
        if ln.voltage_kv is None:
            continue
        for seg in ln.coordinates_multilinestring:
            if len(seg) < 2:
                continue
            # start endpoint
            lon0, lat0 = seg[0][0], seg[0][1]
            endpoints.append((lat0, lon0, ln.voltage_kv, ln.feature_id))
            # end endpoint
            lon1, lat1 = seg[-1][0], seg[-1][1]
            endpoints.append((lat1, lon1, ln.voltage_kv, ln.feature_id))

    if not endpoints:
        logger.warning(
            "Reverse Discipline #41 — no line endpoints with voltage available; "
            "no substation voltage enrichment performed. Convention #56 visibly-honest."
        )
        return 0

    # Grid-index endpoints for O(N+M) instead of O(N*M) proximity join.
    # Grid cell size ~= join_meters converted to degrees; at Norway latitudes
    # 1° lat ≈ 111 km, 1° lon ≈ 55 km (at 60°N).  Use 0.01° cells (~1.1 km) so
    # a 500m proximity fits inside a 3x3 cell window.
    cell_size_deg = 0.01
    grid: dict[tuple[int, int], list[tuple[float, float, float, str]]] = {}
    for ep in endpoints:
        cx = int(ep[1] / cell_size_deg)
        cy = int(ep[0] / cell_size_deg)
        grid.setdefault((cx, cy), []).append(ep)

    enriched_count = 0
    for sub in substations:
        cx = int(sub.longitude / cell_size_deg)
        cy = int(sub.latitude / cell_size_deg)
        candidate_lines: list[dict] = []
        for dcx in (-1, 0, 1):
            for dcy in (-1, 0, 1):
                for ep in grid.get((cx + dcx, cy + dcy), []):
                    d = _haversine_m(sub.latitude, sub.longitude, ep[0], ep[1])
                    if d <= join_meters:
                        candidate_lines.append({
                            "line_lokal_id": ep[3],
                            "spenning_kv": ep[2],
                            "distance_m": round(d, 1),
                        })
        if not candidate_lines:
            continue
        # deduplicate by (line_id, voltage) — a line's two endpoints may both hit
        seen: set[tuple[str, float]] = set()
        unique_lines: list[dict] = []
        for cl in candidate_lines:
            k = (cl["line_lokal_id"], cl["spenning_kv"])
            if k not in seen:
                seen.add(k)
                unique_lines.append(cl)
        chosen = max(cl["spenning_kv"] for cl in unique_lines)
        sub.voltage_kv = chosen
        sub.raw_attributes["v43_voltage_inheritance"] = {
            "sources": unique_lines,
            "chosen_voltage_kv": chosen,
        }
        enriched_count += 1

    logger.info(
        "Reverse Discipline #41 — enriched %d/%d substations with voltage_kv via line-endpoint proximity join (%.0fm)",
        enriched_count,
        len(substations),
        join_meters,
    )
    return enriched_count


# ── Paged fetch driver ───────────────────────────────────────────────────
def _fetch_all_features(
    feature_type: str,
    *,
    expected_count: int,
    page_size: int = DEFAULT_PAGE_SIZE,
    max_pages: int | None = None,
) -> tuple[list[ET.Element], int, str]:
    """Fetch all features of a given type via paged WFS GetFeature.

    Returns:
        (list_of_feature_elements, total_raw_bytes, aggregate_sha256)
    """
    all_features: list[ET.Element] = []
    all_bytes = bytearray()
    start_index = 0
    page_num = 0
    max_pages = max_pages or (expected_count // page_size + 3)

    while page_num < max_pages:
        try:
            body = _fetch_wfs_page(feature_type, start_index=start_index, count=page_size)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            logger.warning(
                "WFS fetch %s page %d failed (%s); Convention #56 partial-degradation.",
                feature_type, page_num, exc,
            )
            break
        all_bytes.extend(body)

        try:
            root = ET.fromstring(body)
        except ET.ParseError as exc:
            logger.warning("XML parse error on %s page %d: %s", feature_type, page_num, exc)
            break

        members = root.findall(f"{{{_NS['wfs']}}}member")
        if not members:
            break
        for m in members:
            for child in m:
                if child.tag.startswith(f"{{{_NS['app']}}}"):
                    all_features.append(child)
                    break

        if len(members) < page_size:
            break  # last page
        start_index += page_size
        page_num += 1

    agg_sha = hashlib.sha256(bytes(all_bytes)).hexdigest()
    return all_features, len(all_bytes), agg_sha


# ── Public entry ─────────────────────────────────────────────────────────
def fetch(
    *,
    apply_bounds: bool = True,
    ingest_luftlinje: bool = True,
    ingest_sjokabel: bool = True,
    propagate_voltage: bool = True,
    max_pages_substation: int | None = None,
    max_pages_luftlinje: int | None = None,
    max_pages_sjokabel: int | None = None,
) -> IngestionResult:
    """Fetch NVE Nettanlegg substations + lines + submarine cables.

    Discipline #41 line-coupling: substations + lines ingested in same pass.
    Reverse Discipline #41 voltage inheritance: line spenning propagated to
    endpoint substations via 500m proximity join (see line-schema audit YAML).
    """
    result = IngestionResult(
        source_id=SOURCE_ID,
        fetched_at_utc=now_utc_iso(),
        source_url=WFS_ENDPOINT,
        provincial_scope="NO",
    )

    # ── Substations (EL_Transformatorstasjon) ──
    try:
        sub_features, sub_bytes, sub_sha = _fetch_all_features(
            FEATURE_TYPE_SUBSTATION,
            expected_count=1558,
            max_pages=max_pages_substation,
        )
    except Exception as exc:
        result.warnings.append(
            f"Convention #56 degradation — EL_Transformatorstasjon fetch failed: {exc}"
        )
        return result

    for feat_el in sub_features:
        rec = _substation_from_gml(feat_el)
        if rec is not None:
            result.substations.append(rec)
    logger.info("Parsed %d substations from %d GML features", len(result.substations), len(sub_features))

    # ── Lines (EL_Luftlinje) ──
    line_bytes_total = 0
    line_sha_material = bytearray()
    if ingest_luftlinje:
        try:
            luft_features, luft_bytes, luft_sha = _fetch_all_features(
                FEATURE_TYPE_LUFTLINJE,
                expected_count=145460,
                max_pages=max_pages_luftlinje,
            )
        except Exception as exc:
            result.warnings.append(
                f"Convention #56 partial — EL_Luftlinje fetch failed: {exc}"
            )
            luft_features, luft_bytes, luft_sha = [], 0, ""
        for feat_el in luft_features:
            rec = _line_from_gml(feat_el, "luftlinje")
            if rec is not None:
                result.transmission_lines.append(rec)
        line_bytes_total += luft_bytes
        line_sha_material.extend(luft_sha.encode())
        logger.info(
            "Parsed %d Luftlinje features from %d GML features",
            sum(1 for ln in result.transmission_lines if ln.raw_attributes.get("source_tag") == "luftlinje"),
            len(luft_features),
        )

    # ── Submarine cables (EL_Sjøkabel) ──
    if ingest_sjokabel:
        try:
            sjo_features, sjo_bytes, sjo_sha = _fetch_all_features(
                FEATURE_TYPE_SJOKABEL,
                expected_count=8747,
                max_pages=max_pages_sjokabel,
            )
        except Exception as exc:
            result.warnings.append(
                f"Convention #56 partial — EL_Sjøkabel fetch failed: {exc}"
            )
            sjo_features, sjo_bytes, sjo_sha = [], 0, ""
        for feat_el in sjo_features:
            rec = _line_from_gml(feat_el, "sjokabel")
            if rec is not None:
                result.transmission_lines.append(rec)
        line_bytes_total += sjo_bytes
        line_sha_material.extend(sjo_sha.encode())

    # Aggregate bytes + sha across substation + line fetches
    result.raw_bytes_fetched = sub_bytes + line_bytes_total
    agg_sha_material = bytes(sub_sha, "utf-8") + bytes(line_sha_material)
    result.raw_sha256 = hashlib.sha256(agg_sha_material).hexdigest()

    # ── Discipline #36 bounds filter ──
    if apply_bounds:
        subs_kept, subs_dropped = apply_bounds_filter(result.substations)
        lines_kept, lines_dropped = apply_bounds_filter(result.transmission_lines)
        n_sub_dropped = len(subs_dropped)
        n_line_dropped = len(lines_dropped)
        result.substations = subs_kept
        result.transmission_lines = lines_kept
        if n_sub_dropped or n_line_dropped:
            result.warnings.append(
                f"Discipline #36 — dropped {n_sub_dropped} substations + "
                f"{n_line_dropped} lines outside Norway polygon "
                "(fjord tolerance 5 km per norway/cross_border_tolerances.json Mode 2)."
            )

    # ── REVERSE DISCIPLINE #41 — voltage inheritance ──
    if propagate_voltage and result.substations and result.transmission_lines:
        n_enriched = _propagate_voltage_to_substations(
            result.substations,
            result.transmission_lines,
            join_meters=LINE_ENDPOINT_JOIN_METERS,
        )
        result.warnings.append(
            f"Reverse Discipline #41 — voltage_kv inherited on {n_enriched}/"
            f"{len(result.substations)} substations via {LINE_ENDPOINT_JOIN_METERS:.0f}m "
            "line-endpoint proximity join."
        )

    # ── Discipline #41 parity assertion ──
    parity_ok, findings = assert_line_parity(result, outbound_border_ok=False)
    for f in findings:
        logger.info("Discipline #41: %s", f)

    return result


# ── CLI harness ──────────────────────────────────────────────────────────
def _cli_main() -> None:
    """Manual invocation harness for empirical validation runs."""
    import argparse
    parser = argparse.ArgumentParser(description="NVE Nettanlegg WFS L1 connector")
    parser.add_argument("--max-pages-sub", type=int, default=None,
                        help="Cap substation pages (for smoke testing)")
    parser.add_argument("--max-pages-lines", type=int, default=None,
                        help="Cap Luftlinje pages (for smoke testing)")
    parser.add_argument("--max-pages-sjokabel", type=int, default=None,
                        help="Cap Sjøkabel pages (for smoke testing)")
    parser.add_argument("--skip-lines", action="store_true", help="Skip line ingestion")
    parser.add_argument("--skip-sjokabel", action="store_true", help="Skip submarine cables")
    parser.add_argument("--no-bounds", action="store_true", help="Skip Discipline #36 filter")
    parser.add_argument("--no-voltage-inheritance", action="store_true",
                        help="Skip reverse Discipline #41 voltage propagation")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    result = fetch(
        apply_bounds=not args.no_bounds,
        ingest_luftlinje=not args.skip_lines,
        ingest_sjokabel=not args.skip_sjokabel,
        propagate_voltage=not args.no_voltage_inheritance,
        max_pages_substation=args.max_pages_sub,
        max_pages_luftlinje=args.max_pages_lines,
        max_pages_sjokabel=args.max_pages_sjokabel,
    )

    parity_ok, findings = assert_line_parity(result, outbound_border_ok=False)
    audit_path = emit_audit_sidecar(result, parity_findings=findings)

    print(f"\n{SOURCE_ID} fetch complete")
    print(f"  substations:        {len(result.substations)}")
    print(f"  transmission_lines: {len(result.transmission_lines)}")
    print(f"  raw_bytes_fetched:  {result.raw_bytes_fetched:,}")
    print(f"  raw_sha256:         {result.raw_sha256}")
    print(f"  audit_sidecar:      {audit_path}")

    enriched = sum(1 for s in result.substations if s.voltage_kv is not None)
    if enriched:
        print(f"  voltage_enriched:   {enriched}/{len(result.substations)} substations")
        # sample distribution
        from collections import Counter
        vdist = Counter(s.voltage_kv for s in result.substations if s.voltage_kv is not None)
        top = sorted(vdist.items(), key=lambda kv: -kv[1])[:8]
        print(f"  top voltage tiers:  {top}")

    for w in result.warnings:
        print(f"  ⚠ {w}")


if __name__ == "__main__":
    _cli_main()
