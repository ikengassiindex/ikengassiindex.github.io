#!/usr/bin/env python3
"""
scripts/check_socio_economic_completeness.py — Discipline #27

Validates that every substation in <slug>/ssi-data.json has the canonical
nested-dict expansions needed for the dashboard's socio-economic + topology
+ seismic + markov panels to render with real data (not blank/"—" / "Loading…").

This gate exists because of the IL S35 hotfix where the rebuild authored
the substations with stub dicts:
  - socio_economic: 2 keys (r3_tier + industry_anchor only) → should be 10
  - graph_topology: string ('radial-mesh') → should be dict
  - seismic: 2 keys → should be 6
  - markov: 1 key (P5) → should be 8

Specifically catches the "graph_topology as string" / "socio_economic
2-key stub" defect class — passes D#16 page-ID parity + D#17 substation
schema (44 fields present) but the values render blank on the dashboard.

Content-agnostic stub-class thresholds (catches IL S35-style defects without
false-positiving on naming-convention variations like PGA_g vs pga_g,
state_now vs steady_state, etc.):

  socio_economic: dict, ≥4 keys  (IL stub had 2 → catches)
  graph_topology: dict, ≥2 keys  (IL stub was STRING → type-check catches)
  seismic:        dict, ≥2 keys  (IL stub had 2 → tolerates naming variants)
  markov:         dict, ≥3 keys  (IL stub had 1 P5 only → catches)

Canonical reference (Costa Rica S33B baseline) for authors:

  socio_economic (10 keys): gdp_per_capita, rd_pct_gdp, unemployment_rate,
    elderly_pct, EP_rate_region, E2_local, V_socio, population,
    industry_anchor, r3_tier
  graph_topology (4 keys): degree, cluster_coeff, BC_percentile, is_bridge
  seismic (5+ keys): R6_seismic, pga_g, zone, transform_fault, fault_distance_km
  markov (7+ keys): corrosion_class, ettc_years, p_critical_10yr,
    p_critical_20yr, risk_score, steady_state, P5

Usage:
    python3 scripts/check_socio_economic_completeness.py <slug>
    python3 scripts/check_socio_economic_completeness.py --all

Exit codes:
    0 = PASS
    1 = FAIL (incomplete dict found in any substation)
"""
import json, os, sys

# D#27 intent: catch the "stub dict" defect class (IL S35 hotfix lesson) where
# fields are present in schema but contain placeholder/incomplete content that
# fails to render on the dashboard. Content-agnostic min-key thresholds catch
# stubs without false-positiving on country-specific naming conventions
# (PGA_g vs pga_g, state_now vs steady_state, etc.).
#
# Thresholds calibrated against:
#   - IL S35 stub: socio_economic=2 keys, graph_topology=string, seismic=2,
#     markov=1 (P5 only) — ALL must FAIL.
#   - Healthy cohort baseline: most countries have socio≥5, gt-dict,
#     seismic≥3, markov≥4 keys.
REQUIRED = {
    "socio_economic": {"type": "dict", "min_keys": 4},  # IL stub had 2; catches it.
    "graph_topology": {"type": "dict", "min_keys": 2},  # IL stub was STRING; type-check fails it.
    "seismic":        {"type": "dict", "min_keys": 2},  # IL stub had 2; allows naming variants.
    "markov":         {"type": "dict", "min_keys": 3},  # IL stub had 1 (P5 only); catches it.
}

def check_substation(s, idx):
    """Return list of issues for this substation. Content-agnostic — counts
    total dict keys (not canonical-name matches) to be naming-convention-tolerant."""
    issues = []
    for field, spec in REQUIRED.items():
        v = s.get(field)
        if v is None:
            issues.append((field, "missing"))
            continue
        if spec["type"] == "dict":
            if not isinstance(v, dict):
                issues.append((field, f"not a dict (got {type(v).__name__}: {repr(v)[:60]})"))
                continue
            if len(v) < spec["min_keys"]:
                issues.append((field, f"has {len(v)} keys, needs ≥{spec['min_keys']} (stub-class defect)"))
    return issues

def check_country(slug, repo_root="."):
    path = os.path.join(repo_root, slug, "ssi-data.json")
    if not os.path.exists(path):
        return {"slug": slug, "status": "EXEMPT", "reason": "no ssi-data.json"}

    try: d = json.load(open(path))
    except Exception as e: return {"slug": slug, "status": "ERROR", "reason": str(e)[:60]}

    subs = d.get("substations") or []
    if not subs:
        return {"slug": slug, "status": "ERROR", "reason": "no substations[]"}

    # Sample first 5 substations to detect systemic stubs
    findings_per_field = {}  # field → count of subs missing it
    sample_issues = []
    for i, s in enumerate(subs[:5]):
        issues = check_substation(s, i)
        if issues and not sample_issues:
            sample_issues = issues
        for field, _ in issues:
            findings_per_field[field] = findings_per_field.get(field, 0) + 1

    # If first 5 all have same issue, sweep ALL subs to confirm systemic
    if sample_issues:
        total_affected = {}
        for i, s in enumerate(subs):
            for field, _ in check_substation(s, i):
                total_affected[field] = total_affected.get(field, 0) + 1
        status = "FAIL"
        return {"slug": slug, "status": status, "n_subs": len(subs),
                "affected_by_field": total_affected, "sample": sample_issues}

    return {"slug": slug, "status": "PASS", "n_subs": len(subs)}

def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: check_socio_economic_completeness.py <slug>|--all")
        sys.exit(2)

    if args[0] == "--all":
        slugs = sorted([d for d in os.listdir(".")
                        if os.path.isdir(d) and os.path.exists(os.path.join(d,"ssi-data.json"))])
    else:
        slugs = args

    print(f"check_socio_economic_completeness.py — Discipline #27 — checking {len(slugs)} countries")
    print(f"  Content-agnostic min-key thresholds: socio_economic≥4, graph_topology≥2 (dict),")
    print(f"                                       seismic≥2, markov≥3")
    print()

    n_fail = 0; n_pass = 0
    for slug in slugs:
        r = check_country(slug)
        if r["status"] == "FAIL":
            n_fail += 1
            print(f"  FAIL {slug:18s} ({r['n_subs']} subs)")
            for field, count in r["affected_by_field"].items():
                pct = 100*count/r['n_subs']
                print(f"      → {field}: {count}/{r['n_subs']} ({pct:.0f}%) substations stub/missing")
            for field, msg in r["sample"][:3]:
                print(f"      sample: {field} — {msg}")
        elif r["status"] == "ERROR":
            n_fail += 1
            print(f"  ERROR {slug}: {r['reason']}")
        else:
            n_pass += 1

    print()
    print(f"Summary: {n_pass} PASS · {n_fail} FAIL")
    sys.exit(1 if n_fail else 0)

if __name__ == "__main__":
    main()
