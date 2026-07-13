"""
SSI Pipeline — Canada Option A: merge federation output into canada/ssi-data.json.

Purpose: execute the Option A closure of the v4.3 Canada Priority 1 workstream
per canada/v4_3-ingestion-audit-canada-delta.yaml.

What this does:
  (1) reads existing canada/ssi-data.json (6,399 scored substations)
  (2) reads scripts/pipeline/data/canada/substations_federated.json (4,557 raw)
  (3) identifies 1,227 net-new substations via 500m proximity dedupe
  (4) adds them to the array with 42-field schema, populating identity/geo/
      voltage/province from federation and setting computed fields to null
      for L2/L3 enrichment to fill downstream
  (5) does voltage_kv enrichment on matched pairs where federation carries
      known voltage but existing sub has voltage_kv=0
  (6) updates meta with growth stats + phase A merge audit record
  (7) writes back canada/ssi-data.json (compact JSON per Convention #56 §42
      to avoid the 100 MB GitHub file-size limit)

Usage (dry-run first — reports deltas without writing):
    python -m scripts.pipeline.ingestion.canada.merge_into_ssi_data --dry-run

Actual write (operator-confirmed):
    python -m scripts.pipeline.ingestion.canada.merge_into_ssi_data --write

After write, operator runs L2 enrichment + L3 scoring on new substations:
    python -m scripts.pipeline.fetch_data --country canada
    python -m scripts.pipeline.run canada

Cross-references:
  - canada/v4_3-ingestion-audit-canada-delta.yaml (parent state-transition anchor)
  - canada/v4_3-ingestion-audit-canada-preflight.yaml (grandparent)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import math
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Paths ────────────────────────────────────────────────────────────────
PIPELINE_DIR = Path(__file__).resolve().parent.parent.parent
REPO_ROOT = PIPELINE_DIR.parent.parent
EXISTING_SSI_DATA = REPO_ROOT / "canada" / "ssi-data.json"
FEDERATED_SUBS = PIPELINE_DIR / "data" / "canada" / "substations_federated.json"
MERGE_AUDIT_YAML = REPO_ROOT / "canada" / "v4_3-ingestion-audit-canada-merge.yaml"

# ── Constants ────────────────────────────────────────────────────────────
PROXIMITY_MATCH_M = 500.0    # matches Discipline #41 sentinel threshold

# Per-province TSO/RTO zone canonical mapping.  Provinces with a formal
# TSO/RTO are named; territories default to their utility.  This map is
# populated based on the existing state's `tso_zone` field distribution.
PROVINCE_TO_TSO_ZONE = {
    "Alberta": "AESO",
    "British Columbia": "BC Hydro",
    "Manitoba": "Manitoba Hydro",
    "New Brunswick": "NB Power",
    "Newfoundland and Labrador": "NL Hydro",
    "Northwest Territories": "NTPC",
    "Nova Scotia": "NS Power",
    "Nunavut": "Qulliq Energy",
    "Ontario": "IESO",
    "Prince Edward Island": "Maritime Electric",
    "Québec": "Hydro-Québec",
    "Saskatchewan": "SaskPower",
    "Yukon": "Yukon Energy",
}
# ISO-3166-2 code → dept_code short form used in existing schema
PROVINCE_TO_DEPT_CODE = {
    "CA-AB": "AB", "CA-BC": "BC", "CA-MB": "MB", "CA-NB": "NB",
    "CA-NL": "NL", "CA-NT": "NT", "CA-NS": "NS", "CA-NU": "NU",
    "CA-ON": "ON", "CA-PE": "PE", "CA-QC": "QC", "CA-SK": "SK",
    "CA-YT": "YT",
}


# ── Distance helper ─────────────────────────────────────────────────────
def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
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


# ── Grid index for fast proximity dedupe ────────────────────────────────
def _build_grid_index(subs: list[dict]) -> dict:
    """0.01° grid cell hash for fast approximate nearest-neighbour."""
    idx: dict = {}
    for i, s in enumerate(subs):
        key = (round(s["lat"] * 100), round(s["lon"] * 100))
        idx.setdefault(key, []).append(i)
    return idx


def _match_existing(
    lat: float,
    lon: float,
    existing_subs: list[dict],
    grid: dict,
    max_m: float = PROXIMITY_MATCH_M,
) -> int | None:
    """Return existing_subs index of the closest sub within max_m metres, else None."""
    key = (round(lat * 100), round(lon * 100))
    best_i, best_d = None, float("inf")
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            for i in grid.get((key[0] + dr, key[1] + dc), []):
                s = existing_subs[i]
                d = _haversine_m(lat, lon, s["lat"], s["lon"])
                if d < best_d and d <= max_m:
                    best_d = d
                    best_i = i
    return best_i


# ── Schema builder for a new substation record ───────────────────────────
def _new_substation_record(
    fed_sub: dict, sequence_id: int,
) -> dict:
    """Build a 42-field substation record from the federation entry.

    Populates identity + geo + voltage + province attribution + provenance
    from the federation output.  Sets computed fields to null placeholders
    for L2 enrichment (seismic, climate, socio) + L3 scoring (R_median,
    classification, band) to fill downstream via the standard pipeline.

    Convention #56 visibly-honest degradation: fields awaiting enrichment
    surface as null, not as spurious defaults.  The pipeline's own
    validate_schema.py will flag these until L2/L3 runs against them,
    which is the correct behaviour — new substations SHOULD be visibly
    non-scored until the pipeline enriches them.
    """
    province = fed_sub.get("province") or "Unknown"
    province_iso = fed_sub.get("province_iso") or ""
    region = fed_sub.get("region") or "Unknown"
    dept_code = PROVINCE_TO_DEPT_CODE.get(province_iso, "??")
    tso_zone = PROVINCE_TO_TSO_ZONE.get(province, "Unknown")

    voltage = fed_sub.get("voltage_kv")
    if voltage is None:
        voltage = 0    # matches existing schema convention (0 = unknown, not null)

    # Stable internal_id derived from federation substation_id + SHA-1 truncation
    # so identical federation inputs always produce identical merged records.
    substation_id_str = fed_sub.get("substation_id") or f"v43-{sequence_id:05d}"
    internal_id = hashlib.sha1(substation_id_str.encode("utf-8")).hexdigest()[:12]

    return {
        # Identity
        "internal_id": internal_id,
        "substation_id": f"CA_v43_{internal_id}",
        "name": fed_sub.get("name") or "",
        # Geography
        "lat": fed_sub["lat"],
        "lon": fed_sub["lon"],
        "province": province,
        "region": region,
        "region_code": dept_code,
        "departement": province,          # existing schema uses departement == province name
        "dept_code": dept_code,
        "tso_zone": tso_zone,
        # Physical
        "voltage_kv": voltage,
        # Provenance (v4.3-specific extension — captures which L1 sources contributed)
        "v43_sources": fed_sub.get("sources", []),
        "v43_provenance": fed_sub.get("provenance", {}),
        # Enrichment placeholders (L2 fills these — climate/seismic/socio).
        # Use empty dicts (not None) so downstream modules can do sub['x'].get()
        # and sub['x'][k]=v without AttributeError — the pipeline does partial
        # merges into these dicts, not wholesale replacement.  Convention #56
        # visibly-honest degradation is preserved via the ABSENCE of the
        # inner keys (pga_g, zone, R6_seismic, etc.) — those show up as
        # empty-dict lookups that L2 then populates.
        "climate_trajectory": {},
        "seismic": {},
        "socio_economic": {},
        "graph_topology": {},
        "markov": {},
        "transition": {},
        # Modifier placeholders (L3 fills these)
        "components": {},
        "modifiers": {},
        "modifier_impacts": {},
        "modifier_impact": None,
        "modifier_pct": None,
        # Scoring placeholders (L3 fills these). Numeric fields default to
        # 0.0 or 1.0 (multiplicative-neutral) rather than None so downstream
        # validate_schema.py + Phase 2b fleet-floor gate can format them
        # without hitting NoneType.__format__.  Convention #56 discipline
        # preserved: the values are OBVIOUSLY placeholder (0.0/1.0) which
        # any statistical audit will surface, but the format-string chain
        # is unbroken.
        "R_base_median": 0.0,
        "R_unclipped": 0.0,
        "R_median": 0.0,
        "R_P5": 0.0,
        "R_P95": 0.0,
        "Re_raw": 1.0,         # v4.2 master equation multiplicative neutral
        "Re_norm": 0.0,
        "add_sum": 0.0,
        "mult_product": 1.0,   # multiplicative neutral
        "P_critical": 0.0,
        "CI_width": 0.0,
        "component_alert": 0.0,
        "alert_components": [],
        "alert_flag": "",
        "classification": None,           # L3 scoring will populate + phase2c reclassify will bin
        "confidence_tier": None,
        "fleet_percentile": None,
        "skewness": None,
        "version": "4.2",                 # methodology version pin
    }


# ── Merge function ──────────────────────────────────────────────────────
def merge(*, dry_run: bool = True, write: bool = False) -> dict:
    """Execute the Option A merge.

    Args:
      dry_run:  Report deltas without writing.  If write=False, defaults to True.
      write:    Actually write the merged canada/ssi-data.json.  Requires
                explicit --write flag.

    Returns:
      dict summary of the merge operation.
    """
    if write:
        dry_run = False

    logger.info("Loading existing canada/ssi-data.json ...")
    with open(EXISTING_SSI_DATA) as f:
        existing = json.load(f)
    existing_subs = existing["substations"]
    n_existing = len(existing_subs)
    logger.info("  existing substations: %d", n_existing)

    logger.info("Loading federation output ...")
    with open(FEDERATED_SUBS) as f:
        fed = json.load(f)
    fed_subs = fed["substations"]
    logger.info("  federation substations: %d", len(fed_subs))

    # Build grid index for fast proximity dedupe
    grid = _build_grid_index(existing_subs)

    # Pass 1: classify federation subs as matched-vs-new
    new_records: list[dict] = []
    voltage_enrichments: list[tuple[int, dict]] = []
    matched_count = 0

    sequence_id = 0
    for fed_sub in fed_subs:
        match_i = _match_existing(fed_sub["lat"], fed_sub["lon"], existing_subs, grid)
        if match_i is None:
            sequence_id += 1
            new_records.append(_new_substation_record(fed_sub, sequence_id))
        else:
            matched_count += 1
            # Voltage enrichment opportunity: fed carries known voltage,
            # existing has voltage_kv=0 (or None)
            fed_voltage = fed_sub.get("voltage_kv")
            existing_voltage = existing_subs[match_i].get("voltage_kv")
            if fed_voltage and (existing_voltage in (0, 0.0, None, "")):
                voltage_enrichments.append((match_i, fed_sub))

    # Pass 2: apply voltage enrichments (if writing)
    if write:
        for match_i, fed_sub in voltage_enrichments:
            existing_subs[match_i]["voltage_kv"] = fed_sub["voltage_kv"]

    # Pass 3: append new records (if writing)
    if write:
        existing_subs.extend(new_records)

    # Meta update
    growth_pct = (len(new_records) / n_existing) * 100 if n_existing else 0
    merge_record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "phase": "Option A — v4.3 additive merge",
        "existing_subs_before": n_existing,
        "new_subs_added": len(new_records),
        "voltage_enrichments": len(voltage_enrichments),
        "total_subs_after": n_existing + len(new_records) if write else n_existing,
        "source_registry": [
            "CA-C1-canvec-resmgt",
            "CA-C2-nacei-arcgis",
            "CA-C3-yec-substations",
            "CA-C4-ns-nstdb-utilities-point",
        ],
        "parent_audit": "canada/v4_3-ingestion-audit-canada-delta.yaml",
        "dry_run": dry_run,
    }

    summary = {
        "n_existing": n_existing,
        "n_federation": len(fed_subs),
        "n_matched": matched_count,
        "n_new": len(new_records),
        "n_voltage_enrichments": len(voltage_enrichments),
        "n_after": n_existing + len(new_records) if write else n_existing,
        "growth_pct": round(growth_pct, 2),
    }

    # Province distribution of new subs
    from collections import Counter
    prov_counter = Counter(r["province"] for r in new_records)
    summary["new_by_province"] = dict(prov_counter.most_common())

    if write:
        # Append merge record to meta
        existing["meta"].setdefault("v43_merge_runs", []).append(merge_record)
        existing["meta"]["total_substations"] = len(existing_subs)
        existing["meta"]["n_substations"] = len(existing_subs)

        # Compact JSON write per Convention #56 §42 (100 MB limit)
        with open(EXISTING_SSI_DATA, "w") as f:
            json.dump(existing, f, ensure_ascii=False, separators=(",", ":"))
        logger.info(
            "Wrote %d substations to %s (%.1f MB)",
            len(existing_subs),
            EXISTING_SSI_DATA,
            EXISTING_SSI_DATA.stat().st_size / (1024 * 1024),
        )

    return summary


def main() -> None:
    p = argparse.ArgumentParser(description="Merge Canada v4.3 federation into ssi-data.json")
    p.add_argument("--dry-run", action="store_true", help="Report deltas without writing (default)")
    p.add_argument("--write", action="store_true", help="Actually write canada/ssi-data.json")
    args = p.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    summary = merge(dry_run=args.dry_run or not args.write, write=args.write)

    print("\n" + "=" * 70)
    print(f"Canada v4.3 Option A merge — {'DRY RUN' if not args.write else 'WRITE'}")
    print("=" * 70)
    print(f"  existing subs before:      {summary['n_existing']:>6,}")
    print(f"  federation subs available: {summary['n_federation']:>6,}")
    print(f"  federation matched exist:  {summary['n_matched']:>6,}")
    print(f"  new subs to be added:      {summary['n_new']:>6,}")
    print(f"  voltage_kv enrichments:    {summary['n_voltage_enrichments']:>6,}")
    print(f"  total after merge:         {summary['n_after']:>6,}")
    print(f"  growth:                    +{summary['growth_pct']}%")
    print(f"\n  New substations by province:")
    for prov, n in summary["new_by_province"].items():
        print(f"    {prov:30}: {n:>5,}")

    if not args.write:
        print("\n  Dry run — no changes written.")
        print("  Run with --write to apply the merge.")


if __name__ == "__main__":
    main()
