#!/usr/bin/env python3
"""
I5 — Thermal stress proxy, IEEE C57.91 insulation ageing.

    python3 scripts/ssi_derive_metric_I5.py greece --dry-run
    python3 scripts/ssi_derive_metric_I5.py --all

WHY THIS IS ABSOLUTE WHERE I3 IS RELATIVE
-----------------------------------------
I3 captures extreme DEVIATION from the local norm — irregular excursions. It
deliberately scores a perfectly regular annual event at zero, because that is
the local climate. Chronic heat therefore registers nowhere in I3.

I5 is the complement, and it is absolute. Insulation ageing is physics, not
convention: 40 degC ambient ages a transformer at the same rate in Tromso as in
Athens. So a hot country SHOULD score higher here, and the two metrics measure
different things rather than the same thing twice.

  I3 ordering (deviation):  greece > finland > turkey > norway > japan
  I5 ordering (absolute):   costa-rica > turkey > greece > japan > norway

THE STANDARD
------------
IEEE C57.91, Guide for Loading Mineral-Oil-Immersed Transformers, cited by the
construct as I5's source ("Thermal stress proxy (ILVE C57.91)"; ITALY_FACT_CARD
source #30 "IEEE C57.91 / IEC 60076"). The corpus cites the standard and never
gives a computation, so this is a definition amendment, as I3 was.

Ageing acceleration factor, C57.91 Annex A:

    F_AA = exp( 15000/383 - 15000/(theta_H + 273) )

theta_H is the winding hot-spot temperature in degC. F_AA = 1.0 at the
110 degC reference hot spot, above which insulation ages faster than nominal.

    theta_H = ambient + HOTSPOT_RISE

HOTSPOT_RISE = 80 K is the C57.91 rise for a 65 degC-average-winding-rise
transformer at RATED LOAD (top-oil rise ~55 K plus hot-spot rise over top oil
~25 K). Verified: at 30 degC ambient this gives exactly F_AA = 1.0000, the
reference point — so the constant is not a guess, it reproduces the standard's
own anchor.

    I5_raw = mean daily F_AA over all cached years
    I5     = Method B over THAT COUNTRY'S fleet P5/P95, NOT inverted
             (faster ageing = more
             risk, the same direction as R)

CONVENTION #7 DECLARATIONS — READ BEFORE CITING THIS
----------------------------------------------------
1. LOADING IS HELD CONSTANT AT RATED. Real hot-spot rise scales with load
   squared, and load data is I7's subject, not available here. So I5 is a
   CLIMATE-driven thermal stress proxy with loading held fixed — which is what
   the construct calls it, a proxy. A substation running at half load ages far
   more slowly than this says; one running overloaded, far faster.

2. DAILY MAXIMUM, NOT DAILY MEAN. The cache holds daily-max 2 m temperature, so
   F_AA is evaluated at each day's peak. This overstates absolute ageing rate
   against a full diurnal integration, consistently, in every country. It is
   the standard worst-case convention and it preserves ranking, which is what
   Method B consumes.

3. WITHIN A COUNTRY, I5 RANKS SUBSTATIONS EXACTLY AS MEAN AMBIENT TEMPERATURE
   WOULD. F_AA is a fixed monotone function of temperature, so the ordering
   carries no information beyond ambient temperature. What C57.91 adds is a
   physically grounded, interpretable SCALE — relative insulation ageing rate —
   and a non-linearity that changes the spacing, not the order. Said plainly
   because the opposite impression would be easy to give.

SEA CELLS AND LARGE GRIDS
-------------------------
The cell resolution, land mask and contiguous-band reader are imported from the
I3 module rather than reimplemented. Those guards were not free: ERA5-Land is
empty over sea, and without the land mask a coastal substation would have taken
an all-NaN cell whose mean is NaN — or worse, a sum of 0.0 that looks measured.
"""
from __future__ import annotations
import argparse, importlib.util, json, pathlib, sys
from datetime import datetime, timezone

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "i3", ROOT / "scripts" / "ssi_derive_metric_I3.py")
i3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(i3)

HOTSPOT_RISE = 80.0      # K, C57.91 65degC-rise transformer at rated load
REF_A = 15000.0 / 383.0  # C57.91 Annex A constants
REF_B = 15000.0
AMENDMENT = "AMENDMENT_I5_thermal_stress_C57_91.md"


def f_aa(ambient_c):
    """IEEE C57.91 ageing acceleration factor from ambient temperature."""
    return np.exp(REF_A - REF_B / (ambient_c + HOTSPOT_RISE + 273.0))


def derive(slug, subs, dry):
    lat, lon, valid = i3.axes_and_validity(slug)
    cellmap, snapped, skipped = i3.resolve_cells(subs, lat, lon, valid)
    if not cellmap:
        raise ValueError("no substation fell on a land cell")
    t, doy, offset, used = i3.series_for_cells(slug, set(cellmap.values()))
    mean_faa = np.nanmean(f_aa(t - 273.15), axis=0)
    del t

    raw, idx = [], []
    for k, (i, j) in cellmap.items():
        v = mean_faa[offset[(i, j)]]
        if not np.isfinite(v):
            skipped += 1
            continue
        raw.append(float(v))
        idx.append(k)
    if not raw:
        raise ValueError("no finite value")

    sv = sorted(raw)
    p5, p95 = i3.percentile(sv, 0.05), i3.percentile(sv, 0.95)
    n = 0
    for k, i in enumerate(idx):
        v = i3.method_b(raw[k], p5, p95)
        if v is None:
            continue
        if not dry:
            m = subs[i].setdefault("metrics", {})
            m["I5"] = round(v, 4)
            m["_I5_raw_F_AA"] = round(raw[k], 5)
        n += 1
    return n, skipped, snapped, (p5, p95), used, float(np.median(raw))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    slugs = i3.load_slugs() if a.all else a.slugs
    if not slugs:
        sys.exit("give country slugs or --all")

    print(f"\n  I5 thermal stress (IEEE C57.91) — {AMENDMENT}\n")
    print(f"  {'country':<14}{'yrs':>5}{'derived':>9}{'skipped':>9}{'snapped':>9}"
          f"{'med F_AA':>10}{'P5':>9}{'P95':>9}")
    for slug in slugs:
        try:
            man, subs, paths = i3.load_subs(slug)
            n, sk, snp, anch, used, med = derive(slug, subs, a.dry_run)
        except Exception as ex:
            print(f"  {slug:<14}REFUSED — {ex}")
            continue
        print(f"  {slug:<14}{len(used):>5}{n:>9,}{sk:>9,}{snp:>9,}"
              f"{med:>10.4f}{anch[0]:>9.4f}{anch[1]:>9.4f}")
        if a.dry_run or not n:
            continue
        man.setdefault("meta", {}).setdefault("metric_derivations", []).append({
            "metrics": ["I5"], "at_utc": datetime.now(timezone.utc).isoformat(),
            "amendment": AMENDMENT,
            "source": "ERA5-Land daily max 2m temperature + IEEE C57.91 Annex A",
            "years": used, "hotspot_rise_K": HOTSPOT_RISE,
            "n_derived": n, "n_skipped": sk, "n_snapped_to_land": snp,
            "anchors": {"I5": list(anch)},
            "caveat": "loading held constant at rated; daily maximum not daily "
                      "mean; ranks as mean ambient temperature does"})
        if paths is None:
            man["substations"] = subs
            (ROOT / slug / "ssi-data.json").write_text(json.dumps(man))
        else:
            off = 0
            for p, cnt, was_list in paths:
                blk = subs[off:off + cnt]; off += cnt
                p.write_text(json.dumps(blk if was_list else {"substations": blk}))
            (ROOT / slug / "ssi-data.json").write_text(json.dumps(man))
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
