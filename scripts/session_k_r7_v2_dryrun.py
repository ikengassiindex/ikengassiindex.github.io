#!/usr/bin/env python3
"""session_k_r7_v2_dryrun.py — Task #1141 (18 August 2026)

R7 v2 dry-run compute across the 39-country cohort. Does NOT write to any
ssi-data.json (Session K is compute + audit only per hard boundary #2).

Reads r7_cyber_v2_inputs.json (Session J output) for each country. Calls
r7_cyber_v2 module compute functions with a synthetic per-country
representative substation (per-country f_product bakes in country-level
defaults per r7_cyber_v2 §compute_r7_cyber_v2_for_sub contract).

Optionally reads R7 v1 baseline from country ssi-data.json (Convention #79
sharded reader) for dual-write divergence analysis. Read-only.

Weight sensitivity: compute R7 v2 with 4 weight configurations:
- (0.55, 0.45)  Gate A GATE-A-2 default
- (0.50, 0.50)  neutral
- (0.60, 0.40)  entity-heavier
- (0.65, 0.35)  entity-dominant

Emits:
- /Users/cedricberard/Library/CloudStorage/OneDrive-IkengaSL/.../r7_v2_dryrun_20260818.json
  (full per-country dry-run result + weight-sensitivity matrix)
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.pipeline.scoring import r7_cyber_v2 as m  # noqa: E402

DATA_ROOT = REPO_ROOT / "scripts" / "pipeline" / "data"
SLUGS = json.loads((REPO_ROOT / "intelligence" / "countries.json").read_text())["slugs"]

_CANDIDATE_PATHS = [
    Path("/Users/cedricberard/Library/CloudStorage/OneDrive-IkengaSL/"
         "Internal - IKENGA EU - Documents/0.22. IP agenda/SSI Index/"
         "Upgrade Methodology Rulebook/01-R7-Cyber-v2-CRA-Integration/"
         "r7_v2_dryrun_20260818.json"),
    Path("/sessions/wonderful-exciting-fermi/mnt/OneDrive-IkengaSL/"
         "Internal - IKENGA EU - Documents/0.22. IP agenda/SSI Index/"
         "Upgrade Methodology Rulebook/01-R7-Cyber-v2-CRA-Integration/"
         "r7_v2_dryrun_20260818.json"),
]
OUT_PATH = next((p for p in _CANDIDATE_PATHS if p.parent.exists()),
                _CANDIDATE_PATHS[0])

# Weight sensitivity configurations.
WEIGHT_CONFIGS = [
    ("gate_a_default", 0.55, 0.45),
    ("neutral_50_50", 0.50, 0.50),
    ("entity_60_40", 0.60, 0.40),
    ("entity_65_35", 0.65, 0.35),
]


def compute_with_weights(country_inputs, w_entity, w_product):
    """Recompute R7 v2 for a country's inputs with custom w_entity/w_product.

    Uses the module's compute_f_entity + compute_f_product + a manual
    delta_cyber composition (avoiding mutation of module constants).
    """
    if country_inputs is None:
        return None, "no_country_inputs"

    f_entity, entity_missing = m.compute_f_entity(
        nis2_status_norm=country_inputs.get("nis2_status_norm"),
        nis2_incident_history_norm=country_inputs.get("nis2_incident_history_norm"),
        regulatory_regime_maturity_norm=country_inputs.get("regulatory_regime_maturity_norm"),
    )
    f_product, product_missing = m.compute_f_product(
        vendor_mix_cra_vintage=country_inputs.get("default_vendor_mix_cra_vintage"),
        sbom_coverage=country_inputs.get("default_sbom_coverage"),
        srp_exploited_vuln_signal=country_inputs.get("srp_exploited_vuln_signal"),
    )
    # Compose with custom weights.
    if f_entity is None and f_product is None:
        return None, "no_entity_no_product_data"
    if f_entity is None:
        return m.scale_delta_to_envelope(f_product), "entity_layer_none_full_weight_on_product"
    if f_product is None:
        return m.scale_delta_to_envelope(f_entity), "product_layer_none_full_weight_on_entity"
    delta = w_entity * f_entity + w_product * f_product
    delta = max(0.0, min(1.0, delta))
    return m.scale_delta_to_envelope(delta), ""


def try_load_r7_v1_baseline(slug):
    """Best-effort read of R7 v1 from country ssi-data.json.

    Uses _ssi_data_shard_reader if available. Returns (mean_r7_v1, n_subs)
    or (None, 0) if inaccessible.
    """
    try:
        from scripts._ssi_data_shard_reader import load_ssi_data  # noqa
    except ImportError:
        return None, 0
    try:
        data = load_ssi_data(slug)
        subs = data.get("substations") or []
        if isinstance(subs, dict):
            subs = subs.get("items", []) or []
        v1_vals = []
        for s in subs:
            v = s.get("modifiers", {}).get("R7_cyber")
            if v is not None:
                try:
                    v1_vals.append(float(v))
                except (TypeError, ValueError):
                    pass
        if v1_vals:
            return statistics.mean(v1_vals), len(v1_vals)
        return None, len(subs)
    except Exception:
        return None, 0


def main():
    per_country = []
    for slug in SLUGS:
        inputs = m.load_country_inputs(slug)
        path_variant = m.resolve_path_variant(slug)

        # Gate A default compute (via module).
        synthetic_sub = {"modifiers": {}}  # per-country f_product uses defaults
        r7_v2_default, audit = m.compute_r7_cyber_v2_for_sub(synthetic_sub, inputs)

        # Weight-sensitivity sweep.
        weight_sweep = {}
        for name, we, wp in WEIGHT_CONFIGS:
            val, reason = compute_with_weights(inputs, we, wp)
            weight_sweep[name] = {"w_entity": we, "w_product": wp,
                                  "r7_v2": val, "fallback_reason": reason or None}

        # R7 v1 baseline (best-effort read for divergence).
        v1_mean, n_v1 = try_load_r7_v1_baseline(slug)
        divergence = None
        if v1_mean is not None and r7_v2_default is not None:
            divergence = r7_v2_default - v1_mean

        per_country.append({
            "slug": slug,
            "path_variant": path_variant,
            "inputs_present": inputs is not None,
            "f_entity": audit.get("f_entity"),
            "f_product": audit.get("f_product"),
            "delta_cyber": audit.get("delta_cyber"),
            "r7_v2_default": r7_v2_default,
            "fallback_reason": audit.get("fallback_reason") or None,
            "missing_components": audit.get("missing_components", []),
            "weight_sweep": weight_sweep,
            "r7_v1_mean_baseline": v1_mean,
            "r7_v1_n_subs_read": n_v1,
            "r7_v2_minus_v1_default": divergence,
        })

    # Cohort roll-up.
    r7_v2_populated = [r["r7_v2_default"] for r in per_country
                       if r["fallback_reason"] not in ("no_country_inputs",
                                                       "no_entity_no_product_data")
                       and r["r7_v2_default"] is not None]
    fallback_countries = [r for r in per_country
                          if r["fallback_reason"] in ("no_country_inputs",
                                                       "no_entity_no_product_data")]
    envelope_violations = [r["slug"] for r in per_country
                           if r["r7_v2_default"] is not None
                           and (r["r7_v2_default"] < m.ENVELOPE_LOW
                                or r["r7_v2_default"] > m.ENVELOPE_HIGH)]

    def _summ(vals):
        if not vals:
            return {"n": 0}
        return {
            "n": len(vals),
            "mean": round(statistics.mean(vals), 6),
            "median": round(statistics.median(vals), 6),
            "min": round(min(vals), 6),
            "max": round(max(vals), 6),
            "stdev": round(statistics.pstdev(vals), 6) if len(vals) > 1 else 0.0,
            "p5": round(sorted(vals)[max(0, int(len(vals) * 0.05))], 6),
            "p95": round(sorted(vals)[min(len(vals) - 1, int(len(vals) * 0.95))], 6),
        }

    # Path C vs D split.
    path_c_vals = [r["r7_v2_default"] for r in per_country
                   if r["path_variant"] == "C" and r["r7_v2_default"] is not None
                   and r["fallback_reason"] not in ("no_country_inputs",
                                                    "no_entity_no_product_data")]
    path_d_vals = [r["r7_v2_default"] for r in per_country
                   if r["path_variant"] == "D" and r["r7_v2_default"] is not None
                   and r["fallback_reason"] not in ("no_country_inputs",
                                                    "no_entity_no_product_data")]

    # Weight-sensitivity cohort mean per config.
    weight_sensitivity_summary = {}
    for name, we, wp in WEIGHT_CONFIGS:
        vals = [r["weight_sweep"][name]["r7_v2"] for r in per_country
                if r["weight_sweep"][name]["r7_v2"] is not None
                and r["weight_sweep"][name]["fallback_reason"] not in
                ("no_country_inputs", "no_entity_no_product_data")]
        weight_sensitivity_summary[name] = {
            "w_entity": we, "w_product": wp,
            "cohort_summary": _summ(vals),
        }

    # Divergence stats.
    divergences = [r["r7_v2_minus_v1_default"] for r in per_country
                   if r["r7_v2_minus_v1_default"] is not None]

    payload = {
        "session": "Session K (Task #1141) — R7 v2 dry-run compute",
        "session_date": "2026-08-18",
        "cohort_size": len(SLUGS),
        "path_c_count": sum(1 for r in per_country if r["path_variant"] == "C"),
        "path_d_count": sum(1 for r in per_country if r["path_variant"] == "D"),
        "envelope_invariant": {
            "envelope_low": m.ENVELOPE_LOW,
            "envelope_high": m.ENVELOPE_HIGH,
            "n_violations": len(envelope_violations),
            "violation_countries": envelope_violations,
        },
        "cohort_summary_r7_v2_default": _summ(r7_v2_populated),
        "path_c_summary_r7_v2_default": _summ(path_c_vals),
        "path_d_summary_r7_v2_default": _summ(path_d_vals),
        "fallback_identity_countries": [r["slug"] for r in fallback_countries],
        "n_fallback_identity_countries": len(fallback_countries),
        "weight_sensitivity_cohort_summary": weight_sensitivity_summary,
        "dual_write_divergence_r7_v2_minus_v1": _summ(divergences),
        "per_country": per_country,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n")
    print(f"Session K dry-run compute complete. Output → {OUT_PATH}")
    print()
    print(f"Cohort R7 v2 default (Path C+D): {payload['cohort_summary_r7_v2_default']}")
    print(f"Path C mean: {payload['path_c_summary_r7_v2_default'].get('mean')}")
    print(f"Path D mean: {payload['path_d_summary_r7_v2_default'].get('mean')}")
    print(f"Envelope violations: {payload['envelope_invariant']['n_violations']}")
    print(f"Fallback-identity countries: {payload['n_fallback_identity_countries']}")
    ws_means = ", ".join(
        "{}={}".format(k, v["cohort_summary"].get("mean"))
        for k, v in weight_sensitivity_summary.items()
    )
    print("Weight sensitivity (means): " + ws_means)
    if divergences:
        print(f"Dual-write divergence R7 v2 − v1: {payload['dual_write_divergence_r7_v2_minus_v1']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
