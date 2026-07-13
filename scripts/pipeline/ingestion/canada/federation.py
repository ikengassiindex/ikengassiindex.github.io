"""
SSI Pipeline — Canada L1 federation layer.

Consumes IngestionResult payloads from the four Canada connectors (CA-C1
CanVec Res_MGT + CA-C2 NACEI + CA-C3 YEC + CA-C4 NS-NSTDB) and emits a
unified substation registry ready for L2 enrichment (climate + seismic +
socio-economic) and L3 scoring (SSI v4.2 modifier chain).

Scope of THIS layer (L1 federation):
  1. Dedupe substations across sources by lat/lon proximity (500 m match).
  2. Enrich matched substations: federal CanVec provides base topology
     (location + accuracy + temporal_extent); provincial supplements
     (YEC voltage / operator_station_name; NACEI voltage_kV / owner;
     NS-NSTDB feat_desc) merge in when they match by proximity.
  3. Attribute province + region via canada/bounds.json point-in-polygon.
  4. Attach provenance (sources list per substation) for Discipline #55.
  5. Emit intermediate JSON at scripts/pipeline/data/canada/substations_federated.json
     ready for L2 pipeline consumption.

OUT OF SCOPE (downstream):
  - Climate / seismic / socio-economic enrichment (that's L2, handled by
    the existing scripts/pipeline/ingestion/{climate,seismic,socioeconomic}.py).
  - R_median / classification / band scoring (that's L3, handled by
    scripts/pipeline/scoring/engine.py).
  - Final canada/ssi-data.json write (that happens after L3, orchestrated
    by scripts/pipeline/run.py canada).

Discipline #41 line-coupling: transmission lines are federated in a parallel
list and emitted alongside substations.  The Discipline #41 orphan-ratio
sentinel (tests/test_substation_line_parity.py) enforces the invariant on
the final federated output.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from . import canvec_resmgt, nacei_transmission, yec_substations, ns_nstdb_utilities
from ._base import (
    SubstationRecord,
    TransmissionLineRecord,
    IngestionResult,
    now_utc_iso,
    CANADA_DATA_DIR,
)

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────
PROXIMITY_MATCH_M = 500.0    # 500 m — matches Discipline #41 sentinel threshold
FEDERATED_OUTPUT_PATH = CANADA_DATA_DIR / "substations_federated.json"
LINES_OUTPUT_PATH = CANADA_DATA_DIR / "transmission_lines_federated.json"


# ── Distance helpers ─────────────────────────────────────────────────────
def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine distance in metres."""
    R = 6_371_000.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return 2 * R * math.asin(math.sqrt(a))


# ── Province attribution ────────────────────────────────────────────────
@dataclass
class _ProvinceIndex:
    """Point-in-polygon index for the 13 Canadian province/territory polygons."""
    polygons: list[Any] = field(default_factory=list)
    props: list[dict] = field(default_factory=list)

    def lookup(self, lat: float, lon: float) -> dict | None:
        try:
            from shapely.geometry import Point
        except ImportError:
            return None
        pt = Point(lon, lat)
        for poly, props in zip(self.polygons, self.props):
            if poly.contains(pt) or poly.touches(pt):
                return props
        # Fall back — nearest polygon (some substations sit just outside due to
        # bounds-precision rounding at 500 m tolerance)
        min_dist = float("inf")
        min_props = None
        for poly, props in zip(self.polygons, self.props):
            d = pt.distance(poly)
            if d < min_dist:
                min_dist = d
                min_props = props
        if min_dist < 0.05:    # ~5 km at Canada latitudes
            return min_props
        return None


def _load_province_index() -> _ProvinceIndex:
    """Load canada/bounds.json as an indexable point-in-polygon lookup."""
    try:
        from shapely.geometry import shape
    except ImportError:
        logger.warning(
            "shapely not available; province attribution NO-OP. "
            "Convention #56 visibly-honest degradation."
        )
        return _ProvinceIndex()

    from ._base import CANADA_BOUNDS_JSON
    with open(CANADA_BOUNDS_JSON) as f:
        bounds = json.load(f)

    idx = _ProvinceIndex()
    for feat in bounds.get("features", []):
        geom = feat.get("geometry")
        if not geom:
            continue
        try:
            poly = shape(geom)
            if not poly.is_valid:
                poly = poly.buffer(0)
        except Exception as exc:
            logger.warning("Skipping invalid province polygon: %s", exc)
            continue
        idx.polygons.append(poly)
        idx.props.append(feat.get("properties") or {})
    return idx


# ── Federation ──────────────────────────────────────────────────────────
@dataclass
class FederatedSubstation:
    """Merged substation across sources.  Written to substations_federated.json.

    Ready for L2 enrichment: has identity, geometry, voltage, province/region
    attribution, and provenance.  L2 will inject climate/seismic/socio_economic
    dicts; L3 will compute R_median + classification + band.
    """
    substation_id: str
    name: str | None
    lat: float
    lon: float
    voltage_kv: float | None
    province: str | None
    province_iso: str | None
    region: str | None
    tso_zone: str | None       # Canada uses provincial RTOs (IESO, AESO, etc.); populated post-federation
    sources: list[str] = field(default_factory=list)
    provenance: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        return {k: v for k, v in d.items() if v is not None or k in ("sources", "provenance")}


def _seed_from_canvec(rec: SubstationRecord, idx_counter: list[int]) -> FederatedSubstation:
    """Federal CanVec base record (location-only schema)."""
    idx_counter[0] += 1
    return FederatedSubstation(
        substation_id=f"CA-canvec-{idx_counter[0]:05d}",
        name=None,
        lat=rec.latitude,
        lon=rec.longitude,
        voltage_kv=None,
        province=None,
        province_iso=None,
        region=None,
        tso_zone=None,
        sources=[rec.source_id],
        provenance={
            "canvec_feature_id": rec.feature_id,
            "canvec_horiz_accuracy_m": rec.horiz_accuracy_min_m,
            "canvec_temporal_extent": rec.temporal_extent_min,
        },
    )


def _seed_from_provincial(rec: SubstationRecord, idx_counter: list[int]) -> FederatedSubstation:
    """Provincial-utility base record (fuller schema — voltage + name + community)."""
    idx_counter[0] += 1
    prefix = "yec" if "yec" in rec.source_id else ("ns" if "ns-nstdb" in rec.source_id else "prov")
    return FederatedSubstation(
        substation_id=f"CA-{prefix}-{idx_counter[0]:05d}",
        name=rec.operator_station_name,
        lat=rec.latitude,
        lon=rec.longitude,
        voltage_kv=rec.voltage_kv,
        province=None,
        province_iso=None,
        region=None,
        tso_zone=None,
        sources=[rec.source_id],
        provenance={
            f"{prefix}_feature_id": rec.feature_id,
            f"{prefix}_community": rec.community,
            f"{prefix}_operator_station_name": rec.operator_station_name,
            f"{prefix}_voltage_out_kv": rec.voltage_out_kv,
            f"{prefix}_is_transmission": rec.is_transmission_station,
            f"{prefix}_is_switching": rec.is_switching_station,
            f"{prefix}_is_converter": rec.is_converter_station,
        },
    )


def _enrich_with_provincial(base: FederatedSubstation, incoming: SubstationRecord) -> None:
    """Merge provincial supplement into a base CanVec substation."""
    if incoming.source_id not in base.sources:
        base.sources.append(incoming.source_id)
    if base.name is None and incoming.operator_station_name:
        base.name = incoming.operator_station_name
    if base.voltage_kv is None and incoming.voltage_kv is not None:
        base.voltage_kv = incoming.voltage_kv
    # Provenance keyed by source_id
    key_prefix = incoming.source_id.split("-")[-1] if "-" in incoming.source_id else incoming.source_id
    base.provenance[f"{key_prefix}_feature_id"] = incoming.feature_id
    base.provenance[f"{key_prefix}_community"] = incoming.community
    base.provenance[f"{key_prefix}_operator_station_name"] = incoming.operator_station_name
    base.provenance[f"{key_prefix}_voltage_kv"] = incoming.voltage_kv
    base.provenance[f"{key_prefix}_voltage_out_kv"] = incoming.voltage_out_kv


def _match_index(
    federated: list[FederatedSubstation],
    lat: float,
    lon: float,
) -> int | None:
    """Return index of the closest FederatedSubstation within PROXIMITY_MATCH_M,
    or None if no match."""
    best_i, best_d = None, float("inf")
    for i, s in enumerate(federated):
        d = _haversine_m(s.lat, s.lon, lat, lon)
        if d < best_d and d <= PROXIMITY_MATCH_M:
            best_d = d
            best_i = i
    return best_i


# ── Public federate() entry ─────────────────────────────────────────────
def federate(
    *,
    apply_bounds: bool = True,
    write_output: bool = True,
) -> tuple[list[FederatedSubstation], list[dict]]:
    """Fetch all four L1 connectors and produce the federated substation +
    transmission-line registries.

    Args:
      apply_bounds:  Apply Discipline #36 bounds filter to each connector
                     during fetch (default True).
      write_output:  Write the federated JSON files to disk (default True).

    Returns:
      (federated_substations, federated_lines) — lists of dicts ready for L2 pipeline.
    """
    logger.info("Running Canada L1 federation across 4 connectors ...")

    results: list[IngestionResult] = [
        canvec_resmgt.fetch(provincial_scope="CA", apply_bounds=apply_bounds),
        nacei_transmission.fetch(apply_bounds=apply_bounds),
        yec_substations.fetch(apply_bounds=apply_bounds),
        ns_nstdb_utilities.fetch(apply_bounds=apply_bounds),
    ]

    # ── Substation federation ──
    idx_counter = [0]
    federated: list[FederatedSubstation] = []

    # Pass 1: seed with federal CanVec (base topology).
    canvec_result = results[0]
    for rec in canvec_result.substations:
        federated.append(_seed_from_canvec(rec, idx_counter))
    logger.info("Federation seed (CanVec): %d substations", len(federated))

    # Pass 2: enrich with provincial-utility sources (YEC, NS-NSTDB), matching
    # by lat/lon proximity.  Unmatched provincial substations become new base
    # records (they represent operational-utility infrastructure not captured
    # by CanVec at 1:50k scale — expected given the ~14% CanVec completeness
    # ratio surfaced in the Yukon proxy).
    for provincial_result in results[2:]:    # YEC + NS-NSTDB
        matched, new_seeded = 0, 0
        for rec in provincial_result.substations:
            match_i = _match_index(federated, rec.latitude, rec.longitude)
            if match_i is not None:
                _enrich_with_provincial(federated[match_i], rec)
                matched += 1
            else:
                federated.append(_seed_from_provincial(rec, idx_counter))
                new_seeded += 1
        logger.info(
            "Federation merge (%s): %d matched + %d seeded (new)",
            provincial_result.source_id, matched, new_seeded,
        )

    # Pass 3: NACEI has 0 substation records (Layer 1 is lines) — nothing to merge.

    # ── Province + region attribution via point-in-polygon ──
    prov_idx = _load_province_index()
    if prov_idx.polygons:
        attributed, unattributed = 0, 0
        for fed in federated:
            props = prov_idx.lookup(fed.lat, fed.lon)
            if props:
                fed.province = props.get("name")
                fed.province_iso = props.get("iso_3166_2")
                fed.region = props.get("region")
                attributed += 1
            else:
                unattributed += 1
        logger.info(
            "Province attribution: %d assigned, %d unassigned",
            attributed, unattributed,
        )

    # ── Transmission line federation (flat list, not merged) ──
    federated_lines: list[dict] = []
    for r in results:
        for line in r.transmission_lines:
            federated_lines.append({
                "source_id": line.source_id,
                "feature_id": line.feature_id,
                "voltage_kv": line.voltage_kv,
                "owner": line.owner,
                "line_name": line.line_name,
                "number_of_lines": line.number_of_lines,
                "coordinates_multilinestring": line.coordinates_multilinestring,
            })

    # ── Write output ──
    subs_output = [f.to_dict() for f in federated]
    lines_output = federated_lines

    if write_output:
        FEDERATED_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(FEDERATED_OUTPUT_PATH, "w") as f:
            json.dump({
                "meta": {
                    "generated_at_utc": now_utc_iso(),
                    "source_ids": [r.source_id for r in results],
                    "n_substations": len(subs_output),
                    "n_transmission_lines": len(lines_output),
                    "proximity_match_m": PROXIMITY_MATCH_M,
                },
                "substations": subs_output,
            }, f, ensure_ascii=False, separators=(",", ":"))
        with open(LINES_OUTPUT_PATH, "w") as f:
            json.dump({
                "meta": {
                    "generated_at_utc": now_utc_iso(),
                    "source_ids": [r.source_id for r in results],
                    "n_transmission_lines": len(lines_output),
                },
                "transmission_lines": lines_output,
            }, f, ensure_ascii=False, separators=(",", ":"))
        logger.info(
            "Wrote %d substations to %s (%d bytes)",
            len(subs_output), FEDERATED_OUTPUT_PATH,
            FEDERATED_OUTPUT_PATH.stat().st_size,
        )
        logger.info(
            "Wrote %d lines to %s (%d bytes)",
            len(lines_output), LINES_OUTPUT_PATH,
            LINES_OUTPUT_PATH.stat().st_size,
        )

    return subs_output, lines_output


def main() -> None:
    """CLI wrapper: python -m scripts.pipeline.ingestion.canada.federation"""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    subs, lines = federate()
    print(f"\n=== Canada federation complete ===")
    print(f"  substations: {len(subs):,}")
    print(f"  transmission_lines: {len(lines):,}")
    if subs:
        # Report source coverage
        from collections import Counter
        multi_source = sum(1 for s in subs if len(s.get("sources", [])) > 1)
        prov_covered = sum(1 for s in subs if s.get("province"))
        volt_covered = sum(1 for s in subs if s.get("voltage_kv") is not None)
        print(f"  multi-source enriched: {multi_source} ({multi_source/len(subs):.1%})")
        print(f"  province-attributed:    {prov_covered} ({prov_covered/len(subs):.1%})")
        print(f"  voltage-populated:      {volt_covered} ({volt_covered/len(subs):.1%})")


if __name__ == "__main__":
    main()
