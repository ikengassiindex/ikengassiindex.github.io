#!/usr/bin/env python3
"""
apply_parity_patches.py — one-shot JSON migration for Option 3 closure
(KB §49.11, Session 18).

Reads each of the 6 country ssi-data.json files from the live site,
applies the derivations spec'd in automation/audit/patches/{slug}.md,
and writes the patched JSON to <deploy_clone>/<slug>/ssi-data.json.

This is a one-time migration, NOT a recurring hotpatch. These 6
countries are OECD-15 legacy with no per-country scoring-XX pipeline
to regenerate the JSON on refresh. The derivations are documented;
any future pipeline migration should incorporate them at source.

Run with --dry-run first to see what changes; then re-run without it
to actually write the files. A separate deploy script commits and
pushes the result.
"""
from __future__ import annotations
import argparse, json, statistics, sys, urllib.request
from collections import defaultdict
from pathlib import Path

LIVE_BASE = "https://ikengassiindex.github.io"

# Default deploy clone path; override with --clone
DEFAULT_CLONE = Path.home() / "ikengassiindex-deploy-lt"

PATCH_REGISTRY = {
    "chile":     ["substation_climate_trajectory",
                  "substation_confidence_tier",
                  "regions_rebuild"],
    "denmark":   ["markov_20yr_horizon"],
    "australia": ["substation_climate_trajectory",
                  "substation_confidence_tier"],
    "ireland":   ["substation_climate_trajectory"],
    "greece":    ["substation_alert_components",
                  "substation_version_stamp"],
    "us":        ["substation_internal_id_identity"],
}


# ── derivations ──────────────────────────────────────────────────────

def climate_trajectory(sub: dict) -> str:
    """Per patch specs: derive from flood + seismic modifiers."""
    mods = sub.get("modifiers", {}) or {}
    flood   = mods.get("R6c_flood", 0) or 0
    seismic = mods.get("R6_seismic", 0) or 0
    if flood >= 0.04 or seismic >= 0.05:
        return "deteriorating"
    if flood >= 0.02 or seismic >= 0.03:
        return "stable-watchful"
    return "stable"


def confidence_tier(sub: dict) -> str:
    """Per patch specs: derive from CI_width."""
    w = sub.get("CI_width")
    if w is None:
        return "medium"  # safe default when CI_width missing
    if w < 0.10: return "high"
    if w < 0.20: return "medium"
    return "low"


def alert_components(sub: dict) -> list[str]:
    """Per patch specs: components with normalised score > 0.75."""
    out = []
    comps = sub.get("components", {}) or {}
    # If values look raw (>1), use a higher threshold
    threshold = 0.75
    if comps and max(v for v in comps.values() if isinstance(v, (int, float))) > 1.5:
        threshold = 4.0  # raw-scale fallback (R3 is 1-5ish)
    for code, val in comps.items():
        if isinstance(val, (int, float)) and val > threshold:
            out.append(code)
    return sorted(out)


def patch_markov_20yr(mk: dict) -> dict:
    """Denmark: add p_crit_20yr, p_critical_20yr, steady_state.

    The published JSON doesn't include the Markov transition matrix,
    so we use a geometric extrapolation from the 10yr horizon and
    an industry-default steady-state vector. These are approximations,
    documented in KB §49.11 / Session 18.
    """
    if mk is None:
        mk = {}
    p10 = mk.get("p_crit_10yr") or mk.get("p_critical_10yr") or 0.05
    p20 = 1.0 - (1.0 - p10) ** 2          # geometric extrapolation
    mk.setdefault("p_crit_20yr",     round(p20, 4))
    mk.setdefault("p_critical_20yr", round(p20, 4))
    # Industry-default steady-state if absent. Real Markov pipelines
    # would emit this from the eigenvector of the transition matrix.
    mk.setdefault("steady_state", [0.45, 0.30, 0.18, 0.07])
    return mk


def rebuild_regions_chile(data: dict) -> list[dict]:
    """Chile: group substations by `region` field, compute aggregates.

    Falls back to a single national-aggregate region if substations
    lack a region attribution.
    """
    subs_raw = data.get("substations")
    if isinstance(subs_raw, dict):
        subs = list(subs_raw.values())
    elif isinstance(subs_raw, list):
        subs = subs_raw
    else:
        return []

    by_region = defaultdict(list)
    for s in subs:
        if not isinstance(s, dict):
            continue
        r = s.get("region") or s.get("province") or "Chile (national aggregate)"
        by_region[r].append(s)

    regions = []
    for region_name, region_subs in by_region.items():
        Rs = [s.get("R_median") for s in region_subs if isinstance(s.get("R_median"), (int, float))]
        if not Rs:
            Rs = [0.0]
        bands = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for s in region_subs:
            band = (s.get("classification") or "low").lower()
            if band in bands:
                bands[band] += 1
            else:
                # Sometimes classification carries an "elevated" or similar tag — bucket up
                bands["medium"] += 1
        total = len(region_subs)
        regions.append({
            "region":       region_name,
            "count":        total,
            "mean_R":       round(statistics.mean(Rs), 4),
            "median_R":     round(statistics.median(Rs), 4),
            "bands":        bands,
            "pct_critical": round(100.0 * bands["critical"] / total, 2) if total else 0.0,
            "pct_high":     round(100.0 * bands["high"]     / total, 2) if total else 0.0,
        })
    # Sort by count desc, regions with most substations first
    regions.sort(key=lambda r: -r["count"])
    return regions


# ── per-country application ─────────────────────────────────────────

def iter_subs(data: dict):
    """Yield (key, sub) for each substation; key is index or dict-key."""
    subs = data.get("substations")
    if isinstance(subs, list):
        for i, s in enumerate(subs):
            if isinstance(s, dict):
                yield i, s
    elif isinstance(subs, dict):
        for k, s in subs.items():
            if isinstance(s, dict):
                yield k, s


def apply_patches(slug: str, data: dict, engine_version: str = "v4.0.2-parity") -> dict:
    """Apply the per-slug patches in-place; return a summary of changes."""
    patches = PATCH_REGISTRY.get(slug, [])
    summary = {"slug": slug, "patches_applied": [], "subs_touched": 0,
               "regions_rebuilt": False}

    for sub_key, sub in iter_subs(data):
        touched = False
        if "substation_climate_trajectory" in patches and "climate_trajectory" not in sub:
            sub["climate_trajectory"] = climate_trajectory(sub)
            touched = True
        if "substation_confidence_tier" in patches and "confidence_tier" not in sub:
            sub["confidence_tier"] = confidence_tier(sub)
            touched = True
        if "substation_alert_components" in patches and "alert_components" not in sub:
            sub["alert_components"] = alert_components(sub)
            touched = True
        if "substation_version_stamp" in patches and "version" not in sub:
            sub["version"] = engine_version
            touched = True
        if "substation_internal_id_identity" in patches and "internal_id" not in sub:
            sub["internal_id"] = sub.get("substation_id") or f"{slug.upper()}_{sub_key}"
            touched = True
        if "markov_20yr_horizon" in patches:
            mk = sub.get("markov")
            if isinstance(mk, dict):
                before = dict(mk)
                sub["markov"] = patch_markov_20yr(mk)
                if sub["markov"] != before:
                    touched = True
        if touched:
            summary["subs_touched"] += 1

    if "regions_rebuild" in patches:
        new_regions = rebuild_regions_chile(data)
        data["regions"] = new_regions
        summary["regions_rebuilt"] = True
        summary["new_region_count"] = len(new_regions)

    summary["patches_applied"] = patches
    return summary


# ── fetch + write ────────────────────────────────────────────────────

def fetch_live(slug: str) -> dict:
    url = f"{LIVE_BASE}/{slug}/ssi-data.json"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read())


def describe_current(slug: str, data: dict) -> dict:
    """Show what's there now (for review before patching)."""
    subs_raw = data.get("substations")
    n_subs = len(subs_raw) if isinstance(subs_raw, (list, dict)) else 0
    regions_raw = data.get("regions")
    n_regions = len(regions_raw) if isinstance(regions_raw, (list, dict)) else 0
    first_sub = None
    if isinstance(subs_raw, list) and subs_raw:
        first_sub = subs_raw[0] if isinstance(subs_raw[0], dict) else None
    elif isinstance(subs_raw, dict) and subs_raw:
        first_sub = next(iter(subs_raw.values())) if subs_raw else None
    return {
        "slug": slug,
        "n_substations": n_subs,
        "n_regions": n_regions,
        "sub_has_region_field":  bool(first_sub and "region" in first_sub),
        "sub_has_CI_width":      bool(first_sub and "CI_width" in first_sub),
        "sub_has_modifiers":     bool(first_sub and "modifiers" in first_sub),
        "sub_has_components":    bool(first_sub and "components" in first_sub),
        "sub_has_classification": bool(first_sub and "classification" in first_sub),
        "markov_has_p_crit_10yr": bool(
            first_sub and isinstance(first_sub.get("markov"), dict) and
            (first_sub["markov"].get("p_crit_10yr") is not None or
             first_sub["markov"].get("p_critical_10yr") is not None)
        ),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--clone", default=str(DEFAULT_CLONE),
                   help="Path to the deploy clone (default: ~/ikengassiindex-deploy-lt)")
    p.add_argument("--dry-run", action="store_true",
                   help="Print what would change; do not write files")
    p.add_argument("--countries", default="",
                   help="CSV slugs (default: all 6)")
    args = p.parse_args()

    clone = Path(args.clone)
    if not clone.exists():
        print(f"✗ Deploy clone not found: {clone}", file=sys.stderr)
        sys.exit(1)

    slugs = list(PATCH_REGISTRY)
    if args.countries:
        wanted = {s.strip() for s in args.countries.split(",")}
        slugs = [s for s in slugs if s in wanted]

    print("═" * 70)
    print(f" PARITY PATCHES — {len(slugs)} country/countries · "
          f"{'DRY RUN' if args.dry_run else 'WRITE'} mode")
    print("═" * 70)

    all_summaries = []
    for slug in slugs:
        print(f"\n── {slug} ──")
        try:
            data = fetch_live(slug)
        except Exception as e:
            print(f"  ✗ fetch failed: {e}")
            continue

        desc = describe_current(slug, data)
        print(f"  current: {desc['n_substations']} subs · {desc['n_regions']} regions")
        print(f"           region={desc['sub_has_region_field']} · "
              f"CI_width={desc['sub_has_CI_width']} · "
              f"modifiers={desc['sub_has_modifiers']} · "
              f"components={desc['sub_has_components']} · "
              f"classification={desc['sub_has_classification']} · "
              f"markov_p10={desc['markov_has_p_crit_10yr']}")

        summary = apply_patches(slug, data)
        print(f"  patches: {', '.join(summary['patches_applied'])}")
        print(f"  ✓ {summary['subs_touched']} substation(s) modified" +
              (f", regions rebuilt → {summary.get('new_region_count', 0)} entries"
               if summary["regions_rebuilt"] else ""))

        if not args.dry_run:
            country_dir = clone / slug
            country_dir.mkdir(parents=True, exist_ok=True)
            out_path = country_dir / "ssi-data.json"
            out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
            print(f"  → wrote {out_path} ({out_path.stat().st_size:,} bytes)")

        all_summaries.append(summary)

    print()
    print("═" * 70)
    if args.dry_run:
        print(" DRY RUN — no files written. Re-run without --dry-run to apply.")
    else:
        print(f" ✓ Wrote {len(all_summaries)} patched JSON file(s) to {clone}/")
        print(f"   Review with: cd {clone} && git status")
        print(f"   Commit + push via: deploy_parity_patches.sh")
    print("═" * 70)


if __name__ == "__main__":
    main()
