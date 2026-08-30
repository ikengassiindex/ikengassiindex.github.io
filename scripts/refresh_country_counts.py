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


# ═══════════════════════════════════════════════════════════════════════════
#  RECOMPUTE MODE (30 August 2026)
# ───────────────────────────────────────────────────────────────────────────
#  The mode above propagates a count change by replacing the OLD string with
#  the NEW one, reading the old value from a `.pre-remediate-*.backup`. That
#  makes it unusable for 26 of 39 countries, which have no such backup — their
#  published counts cannot be refreshed at all, and so can diverge from the
#  register silently and indefinitely.
#
#  Turkey was the worked example: repairing 1,110 volt-scale voltage_kv values
#  moved its EHV fleet from 1,120 to 136 and its HV fleet from 1 to 789 while
#  all seven of its pages went on publishing 1,120 and 1.
#
#  This mode needs no backup. It recomputes the four canonical fleet counts
#  from {country}/ssi-data.json and writes them BY ANCHOR — inside the
#  SSI_CANONICAL_LITERALS table and inside elements carrying the matching
#  data-canonical attribute. It never does a bare string replacement, so the
#  Task #520 substring collision (Austria: "262" inside "262,807" mangled to
#  "14070,807") cannot occur here by construction: the number being replaced
#  is located by its key, not by its digits.
#
#  It refuses to leave a file it cannot verify: after writing, each file is
#  re-parsed and every canonical value must equal the register, or the backup
#  is restored and the country aborts.
# ═══════════════════════════════════════════════════════════════════════════

CANON_KEYS = ("fleet.total", "fleet.voltage.ehv", "fleet.voltage.hv",
              "fleet.voltage.distribution")


def _load_subs(slug):
    man = json.loads((REPO_ROOT / slug / "ssi-data.json").read_text())
    subs = man.get("substations")
    if subs is None and man.get("substations_shards"):
        subs = []
        for e in man["substations_shards"]:
            fp = REPO_ROOT / slug / Path(e["path"]).name
            raw = json.loads(fp.read_text())
            subs.extend(raw if isinstance(raw, list) else raw.get("substations", []))
    if subs is None:
        raise ValueError(f"{slug}: no substations and no readable shards")
    return subs


def counts_from_data(slug):
    """The four canonical fleet counts, from the register.

    Buckets are the ones this file has always used:
      EHV >= 220 kV · HV 110-220 kV · distribution < 110 kV or untagged.
    """
    subs = _load_subs(slug)
    num = lambda s: (isinstance(s.get("voltage_kv"), (int, float))
                     and not isinstance(s.get("voltage_kv"), bool))
    return {
        "fleet.total": len(subs),
        "fleet.voltage.ehv": sum(1 for s in subs if num(s) and s["voltage_kv"] >= 220),
        "fleet.voltage.hv": sum(1 for s in subs
                                if num(s) and 110 <= s["voltage_kv"] < 220),
        "fleet.voltage.distribution": sum(1 for s in subs
                                          if not num(s) or s["voltage_kv"] < 110),
    }


def _canon_in_text(text):
    """Every canonical value the file states, as {key: {value, ...}}."""
    found = {}
    for k in CANON_KEYS:
        for pat in (r'"' + re.escape(k) + r'"\s*:\s*"([\d,]+)"',
                    r'data-canonical="' + re.escape(k) + r'"[^>]*>\s*([\d,]+)\s*<'):
            for m in re.finditer(pat, text):
                found.setdefault(k, set()).add(int(m.group(1).replace(",", "")))
    return found


def _rewrite(text, truth):
    """Replace canonical values by anchor. Returns (new_text, n_changes)."""
    n = 0
    for k, v in truth.items():
        new = fmt(v)

        def _tbl(m, new=new):
            nonlocal n
            if m.group(1) != new:
                n += 1
            return f'"{m.group(0).split(chr(34))[1]}": "{new}"'

        text, c1 = re.subn(
            r'"(' + re.escape(k) + r')"(\s*:\s*)"([\d,]+)"',
            lambda m, new=new: f'"{m.group(1)}"{m.group(2)}"{new}"', text)
        text, c2 = re.subn(
            r'(data-canonical="' + re.escape(k) + r'"[^>]*>)\s*[\d,]+\s*(<)',
            lambda m, new=new: f'{m.group(1)}{new}{m.group(2)}', text)
        n += c1 + c2
    return text, n


def refresh_from_data(slug, dry_run=False):
    """Recompute the canonical counts and write them by anchor. No backup file
    of the previous data is needed, and none is consulted."""
    cdir = REPO_ROOT / slug
    if not (cdir / "ssi-data.json").exists():
        print(f"  {slug:14} no ssi-data.json — skipped")
        return 0
    truth = counts_from_data(slug)
    files = [f for f in sorted(cdir.glob("*.html")) if ".backup" not in f.name]
    files += [f for f in sorted(cdir.glob("*.js")) if ".backup" not in f.name]

    stale = []
    for f in files:
        text = f.read_text(errors="replace")
        for k, vals in _canon_in_text(text).items():
            if any(v != truth[k] for v in vals):
                stale.append(f)
                break
    if not stale:
        return 0

    print(f"  {slug:14} {len(stale)} file(s) stale")
    for k in CANON_KEYS:
        published = set()
        for f in stale:
            published |= _canon_in_text(f.read_text(errors="replace")).get(k, set())
        if published and published != {truth[k]}:
            print(f"      {k:30} {sorted(published)} -> {truth[k]:,}")
    if dry_run:
        return 0

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for f in stale:
        original = f.read_text(errors="replace")
        updated, n = _rewrite(original, truth)
        if updated == original:
            continue
        backup = f.with_name(f"{f.name}.pre-count-refresh-{ts}.backup")
        shutil.copy2(f, backup)
        f.write_text(updated)
        # Verify, or put it back. A page left half-corrected is worse than one
        # left alone, because the disagreement is then internal to the file.
        check = _canon_in_text(f.read_text(errors="replace"))
        wrong = {k: sorted(v) for k, v in check.items()
                 if any(x != truth[k] for x in v)}
        if wrong:
            shutil.copy2(backup, f)
            raise SystemExit(
                f"{slug}/{f.name}: after rewrite the file still states {wrong} "
                f"against {truth}. Restored from backup and aborting.")
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
    parser.add_argument("--from-data", action="store_true",
                        help="Recompute counts from ssi-data.json and write "
                             "them by anchor. Needs no pre-remediate backup, "
                             "so it works for all 39 countries.")
    parser.add_argument("--all", action="store_true",
                        help="With --from-data: every country in the cohort.")
    args = parser.parse_args()

    if args.from_data:
        if args.all:
            slugs = [c["slug"] for c in json.loads(
                (REPO_ROOT / "intelligence" / "countries.json").read_text())["countries"]]
        elif args.country:
            slugs = [args.country]
        else:
            print("ERROR: --from-data needs a country slug or --all.", file=sys.stderr)
            sys.exit(2)
        print(f"\n  recomputing published counts from the register"
              f"{' (DRY RUN)' if args.dry_run else ''}\n")
        for c in sorted(slugs):
            refresh_from_data(c, dry_run=args.dry_run)
        print()
        sys.exit(0)

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
