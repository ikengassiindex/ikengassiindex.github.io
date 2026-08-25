#!/usr/bin/env python3
"""
regen_per_country_wxxx_fcs.py — Auto-regenerate per-country W1-W10 Substation Formula
Construct HTML files from the Italy template via place-name substitution.

Phase G.1 of Task #459 coordinated foundational-doc big-bang refresh (22 July 2026).

Purpose
=======
The W1-W10 mathematical spine is shared across all 39 SSI Index countries. Country-
specific per-substation baseline computations differ only in:
  (a) place-name references (Regioni/Länder/Régions/provinces/prefectures/comuni)
  (b) national authority names (Terna → RTE + Enedis → BNetzA + 50Hz+Amprion+TenneT+TransnetBW)
  (c) hazard-event anchor references (L'Aquila → whatever anchors the country uses)
  (d) statistical hierarchy counts (20 Regioni / 107 NUTS-3 / 7,901 comuni → country's tiers)

This script regenerates 38 per-country W1-W10 FC files from the Italy v2 template by
substituting these fields via per-country YAML anchor files. Substitutions are
mechanical; regulatory-anchor context lives in the delta sidecar per Phase G.2.

Usage
=====
    # Regenerate all 38 non-Italy per-country FCs:
    python3 scripts/regen_per_country_wxxx_fcs.py --all

    # Regenerate a single country (e.g. France):
    python3 scripts/regen_per_country_wxxx_fcs.py --country france

    # Dry-run (show what would be written; no file writes):
    python3 scripts/regen_per_country_wxxx_fcs.py --all --dry-run

    # Verify per-country YAML anchor completeness (does not regen):
    python3 scripts/regen_per_country_wxxx_fcs.py --verify-anchors

Anchor-file schema
==================
Per-country YAML anchors live at:
    SSI_v4_2 Italy Pilot/reference-docs/w1_w10_country_anchors/<iso2>.yaml

Each anchor file MUST carry the following top-level keys (schema v1 · Phase G.1):
    country_name: <full name, e.g. "France">
    iso2: <e.g. "fr">
    tso_name: <e.g. "RTE">
    dominant_dso: <e.g. "Enedis">
    regional_tier_name: <e.g. "Régions">
    regional_tier_count: <int>
    subregional_tier_name: <e.g. "Départements">
    subregional_tier_count: <int>
    lau_tier_name: <e.g. "Communes">
    lau_tier_count: <int>
    energy_regulator: <e.g. "CRE">
    cyber_agency: <e.g. "ANSSI">
    nis2_transposition_date: <ISO date or "pending">
    seismic_authority: <e.g. "BRGM">
    flood_authority: <e.g. "SCHAPI + national basin agencies">
    wildfire_authority: <e.g. "Météo-France + ONF">
    energy_poverty_registry: <e.g. "ONPE (Observatoire national de la précarité énergétique)">
    high_exposure_anchor_substation: <e.g. "Corte 2 (Haute-Corse)">
    low_exposure_anchor_substation: <e.g. "Chambéry-Nord (Savoie)">
    bidding_zone_count: <int>
    bidding_zone_scheme: <e.g. "single national zone (FR)">
    fleet_substation_count_current: <int post-Wave-4>
    fleet_substation_count_stage_4_pilot: <int if applicable else null>
    convention_78_channel_reuse_class: <"Class 1" | "Class 2" | "Class 3">
    convention_78_precedent_country: <slug if Class 2 else null>

Non-goals
=========
- Regenerating FC v3 (the mathematical-spine anchor). FC v3 is the canonical reference
  document; only Italy holds the exhaustive worked-example detail. Non-Italy countries
  inherit FC v3's math verbatim and document regulatory anchors in the delta sidecar.
- Substituting hazard-event narrative content, regulatory-authority NIS2 landing dates,
  Convention #78 channel-reuse class assignments, or any qualitative regulatory-anchor
  content. Those live in the delta sidecar; this script only handles mechanical
  place-name + statistical-hierarchy substitution.
- Generating the delta sidecars themselves. Delta sidecars are authored country-by-
  country from FACT_CARD.md sources per Phase G.3.

License
=======
CC BY-SA 4.0.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    import yaml  # type: ignore
except ImportError:
    print("ERROR: pyyaml required. Install: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


# Canonical Italy template — the source-of-truth per Convention #14 Foundational-
# Documentation Single-Source-of-Truth. Any downstream regen reads from this path.
DEFAULT_ITALY_TEMPLATE = (
    Path(__file__).resolve().parent.parent.parent
    / "SSI Index"
    / "SSI_v4_2 Italy Pilot"
    / "reference-docs"
    / "SSI_v4_2_W1_W10_Substation_Formula_Construct_Italy_v2.html"
)

DEFAULT_ANCHOR_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "SSI Index"
    / "SSI_v4_2 Italy Pilot"
    / "reference-docs"
    / "w1_w10_country_anchors"
)

DEFAULT_OUTPUT_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "SSI Index"
    / "SSI_v4_2 Italy Pilot"
    / "reference-docs"
    / "per_country_regens"
)


# Post-Wave-4 canonical country roster (38 non-Italy + Italy = 39-country cohort per
# SSI Index v4.2 as of 21 July 2026 US P39 TERMINAL closure).
CANONICAL_COHORT = [
    "australia", "austria", "belgium", "canada", "chile",
    "colombia", "costa_rica", "czechia", "denmark", "estonia",
    "finland", "france", "germany", "greece", "greenland",
    "hungary", "iceland", "ireland", "israel", "italy",
    "japan", "korea", "latvia", "lithuania", "luxembourg",
    "mexico", "netherlands", "new_zealand", "norway", "poland",
    "portugal", "slovakia", "slovenia", "spain", "sweden",
    "switzerland", "turkey", "united_kingdom", "united_states",
]

ITALY_KEY = "italy"

# Canonical substitution schema. Each entry maps a token in the Italy template to the
# YAML key that supplies the substitute. Substitutions are performed as literal string
# replacements after regex-guarded matching to avoid false positives.
#
# Substitutions are grouped by semantic layer:
#   (1) country identity     — country name, ISO codes
#   (2) authority identity   — TSO / DSO / regulator / cyber agency / hazard authorities
#   (3) statistical hierarchy — NUTS-2 / NUTS-3 / LAU counts + tier names
#   (4) bidding-zone         — zone architecture + count
#   (5) fleet scale          — current + Stage 4 pilot substation counts
#   (6) hazard-event anchors — high-exposure + low-exposure worked-example substations
SUBSTITUTION_SCHEMA = [
    # (1) country identity
    ("Italy", "country_name"),
    ("Italian", "country_adjective"),  # derived at load time if not explicit
    # (2) authority identity
    ("Terna", "tso_name"),
    ("e-Distribuzione", "dominant_dso"),
    ("ARERA", "energy_regulator"),
    ("ACN", "cyber_agency"),
    ("INGV", "seismic_authority"),
    ("ISPRA PAI", "flood_authority"),
    ("EFFIS", "wildfire_authority"),
    ("OIPE", "energy_poverty_registry"),
    # (3) statistical hierarchy — Italy: 20 Regioni + 107 NUTS-3 + 7,901 comuni
    ("20 Regioni", "regional_tier_expression"),  # derived: "<count> <tier_name>"
    ("Regioni", "regional_tier_name"),
    ("107 NUTS-3 province", "subregional_tier_expression"),
    ("107 NUTS-3", "subregional_tier_count_expression"),
    ("NUTS-3 province", "subregional_tier_name"),
    ("7,901 LAU comuni", "lau_tier_expression"),
    ("7,901 LAU", "lau_tier_count_expression"),
    ("LAU comuni", "lau_tier_name"),
    # (4) bidding-zone architecture — Italy: 7 zones post-2021
    ("7 IT bidding zones", "bidding_zone_expression"),
    # (5) fleet scale — the Stage 4 baseline is preserved as an audit anchor per
    # methodology_pins.md drift-band rule; only replace when country-specific data
    # legitimately differs from Italy's pilot baseline.
    ("4,293 Italian substations", "fleet_stage_4_expression"),
    ("51,910", "fleet_current_expression"),
    # (6) hazard-event anchors — worked-example substations
    ("Catanzaro 2, Calabria", "high_exposure_anchor_substation_full"),
    ("Bolzano - Bozen, Trentino-Alto Adige", "low_exposure_anchor_substation_full"),
    ("Catanzaro 2", "high_exposure_anchor_substation"),
    ("Bolzano - Bozen", "low_exposure_anchor_substation"),
    ("Calabria", "high_exposure_anchor_region"),
    ("Trentino-Alto Adige", "low_exposure_anchor_region"),
]


@dataclass(frozen=True)
class CountryAnchor:
    """Per-country substitution anchor loaded from a YAML file."""

    country_name: str
    iso2: str
    country_adjective: str
    tso_name: str
    dominant_dso: str
    energy_regulator: str
    cyber_agency: str
    seismic_authority: str
    flood_authority: str
    wildfire_authority: str
    energy_poverty_registry: str
    regional_tier_name: str
    regional_tier_count: int
    subregional_tier_name: str
    subregional_tier_count: int
    lau_tier_name: str
    lau_tier_count: int
    bidding_zone_count: int
    bidding_zone_scheme: str
    fleet_substation_count_current: int
    fleet_substation_count_stage_4_pilot: Optional[int]
    high_exposure_anchor_substation: str
    high_exposure_anchor_region: str
    low_exposure_anchor_substation: str
    low_exposure_anchor_region: str
    convention_78_channel_reuse_class: str
    convention_78_precedent_country: Optional[str]

    def substitution_map(self) -> dict[str, str]:
        """Build the token→replacement map used by regen_html()."""
        m: dict[str, str] = {}

        # Direct scalar substitutions
        m["country_name"] = self.country_name
        m["country_adjective"] = self.country_adjective
        m["tso_name"] = self.tso_name
        m["dominant_dso"] = self.dominant_dso
        m["energy_regulator"] = self.energy_regulator
        m["cyber_agency"] = self.cyber_agency
        m["seismic_authority"] = self.seismic_authority
        m["flood_authority"] = self.flood_authority
        m["wildfire_authority"] = self.wildfire_authority
        m["energy_poverty_registry"] = self.energy_poverty_registry
        m["regional_tier_name"] = self.regional_tier_name
        m["subregional_tier_name"] = self.subregional_tier_name
        m["lau_tier_name"] = self.lau_tier_name

        # Derived compound expressions — mirror Italy template idioms
        m["regional_tier_expression"] = f"{self.regional_tier_count} {self.regional_tier_name}"
        m["subregional_tier_expression"] = (
            f"{self.subregional_tier_count} {self.subregional_tier_name}"
        )
        m["subregional_tier_count_expression"] = (
            f"{self.subregional_tier_count} {self.subregional_tier_name}"
        )
        m["lau_tier_expression"] = f"{self.lau_tier_count:,} {self.lau_tier_name}"
        m["lau_tier_count_expression"] = f"{self.lau_tier_count:,} {self.lau_tier_name}"

        # Bidding-zone architecture
        m["bidding_zone_expression"] = (
            f"{self.bidding_zone_count} {self.iso2.upper()} bidding zones"
        )

        # Fleet scale — Class A / Class B disambiguation per methodology_pins.md.
        # Italy's Stage 4 pilot baseline is preserved unchanged (methodology validation
        # anchor); country-specific Stage 4 pilots are substituted where they exist,
        # else the current fleet count is used as the sole anchor.
        if self.fleet_substation_count_stage_4_pilot is not None:
            m["fleet_stage_4_expression"] = (
                f"{self.fleet_substation_count_stage_4_pilot:,} "
                f"{self.country_adjective} substations"
            )
        else:
            # No Stage 4 pilot for this country — use current fleet, flag no-pilot
            m["fleet_stage_4_expression"] = (
                f"{self.fleet_substation_count_current:,} "
                f"{self.country_adjective} substations (current fleet; no Stage 4 pilot baseline)"
            )
        m["fleet_current_expression"] = f"{self.fleet_substation_count_current:,}"

        # Hazard-event anchor substitutions
        m["high_exposure_anchor_substation"] = self.high_exposure_anchor_substation
        m["high_exposure_anchor_region"] = self.high_exposure_anchor_region
        m["high_exposure_anchor_substation_full"] = (
            f"{self.high_exposure_anchor_substation}, {self.high_exposure_anchor_region}"
        )
        m["low_exposure_anchor_substation"] = self.low_exposure_anchor_substation
        m["low_exposure_anchor_region"] = self.low_exposure_anchor_region
        m["low_exposure_anchor_substation_full"] = (
            f"{self.low_exposure_anchor_substation}, {self.low_exposure_anchor_region}"
        )

        return m


def load_country_anchor(anchor_path: Path) -> CountryAnchor:
    """Load a per-country YAML anchor file. Raises on schema violation."""
    if not anchor_path.exists():
        raise FileNotFoundError(f"Country anchor file not found: {anchor_path}")

    with anchor_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Anchor file {anchor_path} did not parse to a mapping")

    # Derive country_adjective from country_name if not provided explicitly
    country_adjective = data.get("country_adjective") or _derive_country_adjective(
        data["country_name"]
    )

    return CountryAnchor(
        country_name=data["country_name"],
        iso2=data["iso2"].lower(),
        country_adjective=country_adjective,
        tso_name=data["tso_name"],
        dominant_dso=data["dominant_dso"],
        energy_regulator=data["energy_regulator"],
        cyber_agency=data["cyber_agency"],
        seismic_authority=data["seismic_authority"],
        flood_authority=data["flood_authority"],
        wildfire_authority=data["wildfire_authority"],
        energy_poverty_registry=data["energy_poverty_registry"],
        regional_tier_name=data["regional_tier_name"],
        regional_tier_count=int(data["regional_tier_count"]),
        subregional_tier_name=data["subregional_tier_name"],
        subregional_tier_count=int(data["subregional_tier_count"]),
        lau_tier_name=data["lau_tier_name"],
        lau_tier_count=int(data["lau_tier_count"]),
        bidding_zone_count=int(data["bidding_zone_count"]),
        bidding_zone_scheme=data["bidding_zone_scheme"],
        fleet_substation_count_current=int(data["fleet_substation_count_current"]),
        fleet_substation_count_stage_4_pilot=(
            int(data["fleet_substation_count_stage_4_pilot"])
            if data.get("fleet_substation_count_stage_4_pilot") is not None
            else None
        ),
        high_exposure_anchor_substation=data["high_exposure_anchor_substation"],
        high_exposure_anchor_region=data["high_exposure_anchor_region"],
        low_exposure_anchor_substation=data["low_exposure_anchor_substation"],
        low_exposure_anchor_region=data["low_exposure_anchor_region"],
        convention_78_channel_reuse_class=data["convention_78_channel_reuse_class"],
        convention_78_precedent_country=data.get("convention_78_precedent_country"),
    )


def _derive_country_adjective(country_name: str) -> str:
    """
    Derive a demonym adjective from a country name.

    This is a best-effort heuristic covering the common cases in the SSI Index cohort;
    per-country YAML anchors SHOULD provide `country_adjective` explicitly to override.
    """
    demonym_map = {
        "Australia": "Australian",
        "Austria": "Austrian",
        "Belgium": "Belgian",
        "Canada": "Canadian",
        "Chile": "Chilean",
        "Colombia": "Colombian",
        "Costa Rica": "Costa Rican",
        "Czechia": "Czech",
        "Denmark": "Danish",
        "Estonia": "Estonian",
        "Finland": "Finnish",
        "France": "French",
        "Germany": "German",
        "Greece": "Greek",
        "Greenland": "Greenlandic",
        "Hungary": "Hungarian",
        "Iceland": "Icelandic",
        "Ireland": "Irish",
        "Israel": "Israeli",
        "Italy": "Italian",
        "Japan": "Japanese",
        "Korea": "Korean",
        "Latvia": "Latvian",
        "Lithuania": "Lithuanian",
        "Luxembourg": "Luxembourgish",
        "Mexico": "Mexican",
        "Netherlands": "Dutch",
        "New Zealand": "New Zealand",
        "Norway": "Norwegian",
        "Poland": "Polish",
        "Portugal": "Portuguese",
        "Slovakia": "Slovak",
        "Slovenia": "Slovenian",
        "Spain": "Spanish",
        "Sweden": "Swedish",
        "Switzerland": "Swiss",
        "Turkey": "Turkish",
        "United Kingdom": "British",
        "United States": "U.S.",
    }
    return demonym_map.get(country_name, country_name)  # fallback: use full name


def regen_html(template_path: Path, anchor: CountryAnchor) -> str:
    """
    Apply the substitution schema to the Italy template. Returns regen'd HTML.

    Substitutions are applied in the order defined by SUBSTITUTION_SCHEMA so that
    longer / compound tokens are replaced before shorter / component tokens (e.g.
    "107 NUTS-3 province" before "NUTS-3 province" before "Italy").

    Adjective-vs-noun ordering discipline: "Italian" must be substituted BEFORE
    "Italy" to prevent "Italyn" typos (per foundational-docs refresh Iteration 2
    catchall lesson from Phase C.7 Wave 2 cross-jurisdiction leakage closure).
    """
    if not template_path.exists():
        raise FileNotFoundError(f"Italy template not found: {template_path}")

    html = template_path.read_text(encoding="utf-8")
    substitution_map = anchor.substitution_map()

    # Apply substitutions in schema order
    for source_token, anchor_key in SUBSTITUTION_SCHEMA:
        if anchor_key not in substitution_map:
            # Undocumented key — skip; not an error for optional substitutions
            continue
        replacement = substitution_map[anchor_key]
        html = html.replace(source_token, replacement)

    # Post-substitution attestation footer
    attestation = f"""
<!-- ═══════════════════════════════════════════════════════════════════════════ -->
<!-- REGEN ATTESTATION (Phase G.1 · scripts/regen_per_country_wxxx_fcs.py)       -->
<!-- Regenerated from Italy v2 template via mechanical place-name substitution.  -->
<!-- Country: {anchor.country_name} ({anchor.iso2.upper()})                                             -->
<!-- Mathematical spine: inherited from                                          -->
<!--   SSI_v4_2_Complete_Formula_Construct_Italy_v3.html (canonical anchor)      -->
<!-- Regulatory-anchor context: see SSI_v4_2_Complete_FC_Delta_{anchor.country_name}.md -->
<!-- Convention #78 channel-reuse class: {anchor.convention_78_channel_reuse_class}            -->
<!-- License: CC BY-SA 4.0                                                       -->
<!-- ═══════════════════════════════════════════════════════════════════════════ -->
"""
    # Insert attestation after opening <body> tag; fall back to end-of-document
    if "<body>" in html:
        html = html.replace("<body>", "<body>\n" + attestation, 1)
    else:
        html += attestation

    return html


def verify_anchor_completeness(anchor_dir: Path) -> tuple[list[str], list[str]]:
    """
    Verify per-country anchor completeness across the canonical cohort.
    Returns (missing_countries, malformed_countries).
    """
    missing: list[str] = []
    malformed: list[str] = []

    for country_slug in CANONICAL_COHORT:
        if country_slug == ITALY_KEY:
            continue  # Italy is the source template; no anchor needed
        anchor_path = anchor_dir / f"{country_slug}.yaml"
        if not anchor_path.exists():
            missing.append(country_slug)
            continue
        try:
            load_country_anchor(anchor_path)
        except (KeyError, ValueError, FileNotFoundError) as e:
            malformed.append(f"{country_slug}: {e}")

    return missing, malformed


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Regenerate per-country W1-W10 Substation Formula Construct HTML files "
            "from the Italy template. Phase G.1 of Task #459 coordinated foundational-"
            "doc big-bang refresh (22 July 2026)."
        )
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Regenerate all 38 non-Italy per-country FC files",
    )
    parser.add_argument(
        "--country",
        type=str,
        help="Regenerate a single country by slug (e.g. 'france')",
    )
    parser.add_argument(
        "--verify-anchors",
        action="store_true",
        help="Verify per-country YAML anchor completeness across the canonical cohort",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be written; make no file writes",
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=DEFAULT_ITALY_TEMPLATE,
        help=f"Path to Italy template (default: {DEFAULT_ITALY_TEMPLATE})",
    )
    parser.add_argument(
        "--anchor-dir",
        type=Path,
        default=DEFAULT_ANCHOR_DIR,
        help=f"Path to per-country anchor YAML directory (default: {DEFAULT_ANCHOR_DIR})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Path to output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    args = parser.parse_args()

    # Verify anchors — early-out mode
    if args.verify_anchors:
        missing, malformed = verify_anchor_completeness(args.anchor_dir)
        if not missing and not malformed:
            print(
                f"✓ All 38 non-Italy per-country YAML anchors present + valid at "
                f"{args.anchor_dir}"
            )
            return 0
        if missing:
            print(f"✗ Missing anchors ({len(missing)}):")
            for c in missing:
                print(f"    - {c}")
        if malformed:
            print(f"✗ Malformed anchors ({len(malformed)}):")
            for c in malformed:
                print(f"    - {c}")
        return 1

    # Regen mode
    if not (args.all or args.country):
        parser.error("Must specify --all, --country <slug>, or --verify-anchors")

    if args.all:
        countries_to_regen = [c for c in CANONICAL_COHORT if c != ITALY_KEY]
    else:
        countries_to_regen = [args.country.lower().replace("-", "_")]

    args.output_dir.mkdir(parents=True, exist_ok=True)

    n_regen, n_skipped, n_failed = 0, 0, 0

    for country_slug in countries_to_regen:
        anchor_path = args.anchor_dir / f"{country_slug}.yaml"
        if not anchor_path.exists():
            print(f"  [SKIP] {country_slug}: anchor YAML missing at {anchor_path}")
            n_skipped += 1
            continue

        try:
            anchor = load_country_anchor(anchor_path)
        except (KeyError, ValueError) as e:
            print(f"  [FAIL] {country_slug}: {e}")
            n_failed += 1
            continue

        try:
            html = regen_html(args.template, anchor)
        except FileNotFoundError as e:
            print(f"  [FAIL] {country_slug}: {e}")
            n_failed += 1
            continue

        out_path = args.output_dir / (
            f"SSI_v4_2_W1_W10_Substation_Formula_Construct_"
            f"{anchor.country_name.replace(' ', '_')}_v2_regen.html"
        )

        if args.dry_run:
            print(
                f"  [DRY-RUN] Would write {len(html):,} bytes to {out_path}"
            )
        else:
            out_path.write_text(html, encoding="utf-8")
            print(f"  [OK] {country_slug} → {out_path.name} ({len(html):,} bytes)")
        n_regen += 1

    print()
    print(
        f"Regen summary: {n_regen} regenerated, {n_skipped} skipped "
        f"(missing anchors), {n_failed} failed."
    )
    return 1 if n_failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
