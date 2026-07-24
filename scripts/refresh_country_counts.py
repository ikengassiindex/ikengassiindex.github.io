#!/usr/bin/env python3
"""
refresh_country_counts.py — Discipline #36 page-text refresh
(18 June 2026 deep night).

After ssi-data.json + grid-geo.json remediation, the country's HTML/JS pages
still display the pre-remediation hardcoded substation counts. This script
reads the post-remediation counts from {country}/ssi-data.json and
propagates them to:

  - {country}/index.html        (landing page)
  - {country}/map.html          (map explorer page)
  - {country}/data.html         (data download page)
  - {country}/esg-report.html
  - {country}/methodology.html
  - {country}/regional.html
  - {country}/intelligence.html
  - {country}/ssi-metadata.js   (metadata registry)
  - index.html                  (root landing — data-subs attribute on country path)

Replacements (string-form, with thousands separator):
  - Pre-remediation total → Post-remediation total
  - Pre-remediation total without separator → Post-remediation total without separator
  - Pre-remediation n_HV count → Post-remediation n_HV count
  - Pre-remediation n_MV count → Post-remediation n_MV count

The script reads the pre-remediation count from the per-country
ssi-data.json.pre-remediate-*.backup file (which we preserved during
remediation), so the substitution is precise and reversible.

USAGE:
  python3 scripts/refresh_country_counts.py austria --dry-run
  python3 scripts/refresh_country_counts.py austria
  python3 scripts/refresh_country_counts.py --all-remediated

EXIT CODES:
  0   Refresh completed (or --dry-run preview)
  1   Country has no backup (not yet remediated)
  2   Argument or environment error
"""
from __future__ import annotations
import argparse
import glob
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

REMEDIATED_COUNTRIES = [
    "austria", "mexico", "norway", "uk", "france", "chile", "canada",
]


def fmt(n):
    """Format integer with comma thousands-separator."""
    return f"{n:,}"


def get_counts(country):
    """
    Return ({pre_total, pre_hv, pre_mv}, {post_total, post_hv, post_mv}).

    Pre comes from the backup ssi-data.json.pre-remediate-*.backup.
    Post comes from current ssi-data.json.
    """
    country_dir = REPO_ROOT / country
    current_path = country_dir / "ssi-data.json"
    backups = sorted(country_dir.glob("ssi-data.json.pre-remediate-*.backup"))
    if not backups:
        return None, None

    with open(backups[-1]) as f:
        pre = json.load(f)
    with open(current_path) as f:
        post = json.load(f)

    # Task #520 fix (24 July 2026 night): Convention #79 sharded ssi-data
    # awareness. Wave 4 large countries (US, France, Germany, UK, Italy) store
    # substations across N shard files referenced by `substations_shards` at
    # the top level. Legacy `data.get("substations", [])` returns [] on these
    # manifests → voltage-tier recount collapses to 0 → replacement builder
    # emits garbage substitutions on HTML pages. Load shards inline.
    def _load_subs_from_manifest(data, base_dir):
        if not data.get("sharded"):
            return data.get("substations") or []
        subs = []
        shard_list = data.get("substations_shards") or data.get("shards") or []
        for shard_ref in shard_list:
            if isinstance(shard_ref, dict):
                shard_filename = shard_ref.get("path") or shard_ref.get("file")
            else:
                shard_filename = shard_ref
            if not shard_filename:
                continue
            shard_path = base_dir / shard_filename
            if not shard_path.exists():
                continue
            with open(shard_path) as _f:
                shard = json.load(_f)
            if isinstance(shard, list):
                subs.extend(shard)
            elif isinstance(shard, dict):
                subs.extend(shard.get("substations", []))
        return subs

    _pre_subs = _load_subs_from_manifest(pre, country_dir)
    _post_subs = _load_subs_from_manifest(post, country_dir)
    pre["substations"] = _pre_subs
    post["substations"] = _post_subs

    def counts_of(data):
        meta = data.get("meta", {})
        n_hv_meta = meta.get("n_HV")
        n_mv_meta = meta.get("n_MV")
        total = meta.get("n_substations") or meta.get("total") or len(data.get("substations", []))
        subs = data.get("substations", [])
        # Recount voltage tiers from substations (most reliable)
        # EHV ≥ 220 kV  ·  HV 110-220 kV  ·  Distribution < 110 kV or untagged
        n_ehv = sum(1 for s in subs
                    if isinstance(s.get("voltage_kv"), (int, float))
                    and s["voltage_kv"] >= 220)
        n_hv_110_220 = sum(1 for s in subs
                           if isinstance(s.get("voltage_kv"), (int, float))
                           and 110 <= s["voltage_kv"] < 220)
        n_distribution = sum(1 for s in subs
                             if (not isinstance(s.get("voltage_kv"), (int, float)))
                             or s.get("voltage_kv", 0) < 110)
        # Aggregate HV ≥ 60 kV (matches existing n_HV semantics)
        n_hv_agg = sum(1 for s in subs
                       if isinstance(s.get("voltage_kv"), (int, float))
                       and s["voltage_kv"] >= 60)
        n_mv_agg = len(subs) - n_hv_agg
        return {
            "total": total,
            "hv": n_hv_meta if n_hv_meta is not None else n_hv_agg,
            "mv": n_mv_meta if n_mv_meta is not None else n_mv_agg,
            "ehv": n_ehv,
            "hv_110_220": n_hv_110_220,
            "distribution": n_distribution,
        }

    return counts_of(pre), counts_of(post)


def build_replacements(pre, post):
    """
    Return list of (search, replace) tuples ordered most-specific-first.

    Each count is given in both comma-formatted ("1,406") and bare ("1406")
    forms because both occur in the HTML/JS.
    """
    repls = []
    # Total (both forms)
    repls.append((fmt(pre["total"]), fmt(post["total"])))
    repls.append((str(pre["total"]), str(post["total"])))
    # HV-aggregate (only if changed)
    if pre["hv"] != post["hv"]:
        repls.append((fmt(pre["hv"]), fmt(post["hv"])))
        repls.append((str(pre["hv"]), str(post["hv"])))
    # MV-aggregate
    if pre["mv"] != post["mv"]:
        repls.append((fmt(pre["mv"]), fmt(post["mv"])))
        repls.append((str(pre["mv"]), str(post["mv"])))
    # EHV (≥220 kV)
    if pre["ehv"] != post["ehv"]:
        repls.append((fmt(pre["ehv"]), fmt(post["ehv"])))
        repls.append((str(pre["ehv"]), str(post["ehv"])))
    # HV 110-220 kV
    if pre["hv_110_220"] != post["hv_110_220"]:
        repls.append((fmt(pre["hv_110_220"]), fmt(post["hv_110_220"])))
        repls.append((str(pre["hv_110_220"]), str(post["hv_110_220"])))
    # Distribution (typically same as MV but the page text uses this label)
    if pre["distribution"] != post["distribution"]:
        repls.append((fmt(pre["distribution"]), fmt(post["distribution"])))
        repls.append((str(pre["distribution"]), str(post["distribution"])))
    # Dedup preserving order
    seen, out = set(), []
    for k in repls:
        if k in seen:
            continue
        seen.add(k)
        out.append(k)
    return out


PAGE_FILES = [
    "index.html", "map.html", "data.html", "esg-report.html",
    "methodology.html", "regional.html", "intelligence.html",
    "ssi-metadata.js",
    # Per-country section overrides file (named {country}-section-overrides.js)
    # — added as a dynamic glob below in refresh_country()
]


def refresh_country(country, dry_run=False):
    print(f"\n=== Refreshing page counts for {country} ===")
    pre, post = get_counts(country)
    if pre is None:
        print(f"  ⚠ no ssi-data.json.pre-remediate-*.backup found — skipped "
              f"(country not remediated?)")
        return 1

    print(f"  pre-remediation:  total={pre['total']}  HV={pre['hv']}  MV={pre['mv']}")
    print(f"  post-remediation: total={post['total']}  HV={post['hv']}  MV={post['mv']}")
    if pre == post:
        print(f"  no count changes — no-op.")
        return 1

    repls = build_replacements(pre, post)
    print(f"  string replacements ({len(repls)} pairs):")
    for s, r in repls:
        print(f"    '{s}' → '{r}'")
    print()

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    country_dir = REPO_ROOT / country

    # Dynamic file list = static PAGE_FILES + per-country section-overrides
    file_list = list(PAGE_FILES)
    per_country_overrides = country_dir / f"{country}-section-overrides.js"
    if per_country_overrides.exists():
        file_list.append(f"{country}-section-overrides.js")

    total_changes = 0
    for fname in file_list:
        fpath = country_dir / fname
        if not fpath.exists():
            continue
        original = fpath.read_text()
        updated = original
        # Task #520 fix (24 July 2026 night): substring-collision guard.
        # Bare str.replace of "262" → "14,070" caused catastrophic damage on
        # Austria (operator paste-back evidence: 262 appeared as "262,807" in
        # unrelated field, was mangled to "14070,807"). Anchor each match with
        # lookaround so digits + commas either side prevent partial-number
        # matches — comma protects against comma-separator context, digit
        # protects against integer-substring context.
        for s, r in repls:
            pat = re.compile(r'(?<![\d,])' + re.escape(s) + r'(?![\d,])')
            updated = pat.sub(r, updated)
        # Sentinel — pattern-based counts (same lookaround guard) for report
        _count = lambda text, needle: len(re.findall(
            r'(?<![\d,])' + re.escape(needle) + r'(?![\d,])', text))
        n_changes = sum(_count(original, s) for s, _ in repls)
        if updated == original:
            print(f"  {fname:<22}  unchanged")
            continue

        # Count number of replacements made (approximate — counts old strings)
        actual_changes = sum(
            _count(original, s) - _count(updated, s) for s, _ in repls)
        print(f"  {fname:<22}  ~{actual_changes} replacement(s)")
        total_changes += actual_changes

        if not dry_run:
            # Backup + write
            backup_path = country_dir / f"{fname}.pre-refresh-{ts}.backup"
            shutil.copy2(fpath, backup_path)
            fpath.write_text(updated)

    # Root index.html — update data-subs attribute for this country
    root_index = REPO_ROOT / "index.html"
    if root_index.exists():
        original = root_index.read_text()
        # Match data-subs="X,XXX" within a path that contains the country
        # Pattern: data-href="{country}/index.html" ... data-subs="..."
        pattern = re.compile(
            r'(data-href="' + re.escape(country) + r'/index\.html"[^>]*?data-subs=")'
            r'([^"]+)(")',
            re.IGNORECASE
        )
        new_root, n_root = pattern.subn(
            lambda m: m.group(1) + fmt(post["total"]) + m.group(3),
            original
        )
        if n_root > 0:
            print(f"  index.html (root)       ~{n_root} replacement(s) (data-subs)")
            total_changes += n_root
            if not dry_run:
                backup_path = REPO_ROOT / f"index.html.pre-refresh-{country}-{ts}.backup"
                shutil.copy2(root_index, backup_path)
                root_index.write_text(new_root)

    print(f"\n  total changes: {total_changes}")
    if dry_run:
        print(f"  DRY RUN — no files written.")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Refresh hardcoded substation counts in country page assets.",
    )
    parser.add_argument("country", nargs="?", help="Country slug.")
    parser.add_argument("--all-remediated", action="store_true",
                        help="Process all 7 remediated countries.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without writing.")
    args = parser.parse_args()

    if args.all_remediated and args.country:
        print("ERROR: pass either a country slug OR --all-remediated.", file=sys.stderr)
        sys.exit(2)

    if args.all_remediated:
        for c in REMEDIATED_COUNTRIES:
            refresh_country(c, dry_run=args.dry_run)
        return

    if not args.country:
        print("ERROR: must pass a country slug or --all-remediated.", file=sys.stderr)
        sys.exit(2)

    sys.exit(refresh_country(args.country, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
