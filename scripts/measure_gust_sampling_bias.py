#!/usr/bin/env python3
"""
Measure how much a gust MAXIMUM loses when the day is sampled less often.

    python3 scripts/measure_gust_sampling_bias.py --file <cerra .nc>   # one file
    python3 scripts/measure_gust_sampling_bias.py --report             # combine

WHY
    The CERRA probes on disk carry 8 gust fields per day (one per 3-hourly
    analysis, leadtime 1). If each is a one-hour window, they see 8 hours of 24
    and every maximum taken from them is biased low. The size of that bias
    decides whether the five-year fetch must be tripled to leadtimes 1,2,3 -
    from about 33 GB to about 100 GB.

    The leadtime-semantics probe answers WHETHER the gap exists. This answers
    HOW BIG a gap of that shape is, from data already on disk, for free, before
    the decision is taken.

HOW
    Within a January file, thin the 8-per-day sampling to 4, 2 and 1 per day
    and recompute the monthly maximum at every cell. The ratio at each step is
    what one halving of sampling density costs a maximum. If halving from 8 to
    4 costs r, the unmeasurable step from 24 to 8 - a factor of three, between
    one and two halvings - is bounded by r^2 .. r, PROVIDED the cost per
    halving does not grow as sampling thins. That proviso is itself tested
    here: the 8->4, 4->2 and 2->1 costs are printed side by side.

    THAT PROVISO DID NOT HOLD. The leadtime probe later measured 24 -> 8
    directly at 19.6 per cent of cells more than 5 per cent low, against the
    20.3 and 22.5 that one halving costs. Same magnitude, not smaller. Read
    the output as an ANALOGUE, not as a bound; the script says so where it
    prints the number, and doctrine/FINDING_cerra_leadtime_and_temporal_
    sampling.md records why the reasoning failed.

    Thinning takes every 2nd, 4th and 8th analysis, so 4/day is 00-06-12-18,
    2/day is 00-12, 1/day is 00 - each an evenly spaced subset of the day, the
    same shape of gap as 8-of-24, not a contiguous block.

READING SPEED
    The field is chunked [50, 214, 214]. Cells scattered at random would force
    the whole file through the decompressor, so this reads chunk-aligned tiles
    instead and samples inside them. Fewer bytes, same statistic.

WHAT IT IS NOT
    Not a substitute for fetching the missing hours - a bound computed before
    spending 70 GB, so the spend is a decision and not a reflex. Both answers
    are useful: a small bias means the lt=["1"] fetch is defensible and the
    11 per cent ERA5 gap is mostly physical; a large one means neither.

    January only. Winter gusts in this domain are synoptic and less diurnal
    than summer convection, so January is the FAVOURABLE case and a summer
    month would show a larger bias. Stated, not hidden.
"""
from __future__ import annotations
import argparse, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "scripts" / "pipeline" / ".cache"
OUTDIR = CACHE / "sampling_bias"
PER_DAY = 8
TILE = 214                      # the file's own spatial chunk size
TILE_ORIGINS = (0, 214, 428, 642, 856)


def run_one(path: pathlib.Path, n_tiles: int, cells_per_tile: int) -> dict:
    import netCDF4, numpy as np
    d = netCDF4.Dataset(str(path))
    v = d.variables["fg10"]
    nt, ny, nx = v.shape
    if nt % PER_DAY:
        d.close()
        sys.exit(f"{path.name}: {nt} timesteps is not a multiple of {PER_DAY}")

    rng = np.random.default_rng(20260910)
    grid = [(y, x) for y in TILE_ORIGINS for x in TILE_ORIGINS
            if y + TILE <= ny and x + TILE <= nx]
    pick = rng.permutation(len(grid))[:n_tiles]

    keep = {"8/day": [], "4/day": [], "2/day": [], "1/day": []}
    n_cells = 0
    for i in pick:
        y0, x0 = grid[i]
        blk = np.asarray(v[:, y0:y0 + TILE, x0:x0 + TILE], dtype="float32")
        blk = blk.reshape(nt, -1)
        good = np.all(np.isfinite(blk), axis=0)
        blk = blk[:, good]
        if blk.shape[1] > cells_per_tile:
            sel = rng.permutation(blk.shape[1])[:cells_per_tile]
            blk = blk[:, sel]
        if not blk.shape[1]:
            continue
        n_cells += blk.shape[1]
        for stride, label in ((1, "8/day"), (2, "4/day"), (4, "2/day"), (8, "1/day")):
            keep[label].append(blk[::stride].max(axis=0))
    d.close()

    if not n_cells:
        sys.exit(f"{path.name}: no fully finite cells in the tiles read")
    m = {k: np.concatenate(vv) for k, vv in keep.items()}
    base = m["8/day"]
    res = {"file": path.name, "n_cells": int(n_cells),
           "n_tiles": int(len(pick)), "n_timesteps": int(nt), "levels": {}}
    for label in ("8/day", "4/day", "2/day", "1/day"):
        a = m[label]
        r = a / base
        res["levels"][label] = {
            "mean_max": float(a.mean()),
            "fleet_ratio": float(a.mean() / base.mean()),
            "median_ratio": float(np.median(r)),
            "p05_ratio": float(np.percentile(r, 5)),
            "p01_ratio": float(np.percentile(r, 1)),
            "frac_below_0.95": float((r < 0.95).mean()),
            "frac_below_0.90": float((r < 0.90).mean()),
        }
    res["halving_cost"] = {
        "8->4": float(np.median(m["4/day"] / m["8/day"])),
        "4->2": float(np.median(m["2/day"] / m["4/day"])),
        "2->1": float(np.median(m["1/day"] / m["2/day"])),
    }
    return res


def show(res: dict) -> None:
    print(f"\n  {res['file']}   {res['n_cells']:,} cells "
          f"from {res['n_tiles']} tiles, {res['n_timesteps']} timesteps")
    print(f"    {'sampling':<8} {'mean':>7} {'fleet':>7} {'median':>7} "
          f"{'p05':>7} {'p01':>7} {'<0.95':>7} {'<0.90':>7}")
    for label in ("8/day", "4/day", "2/day", "1/day"):
        L = res["levels"][label]
        print(f"    {label:<8} {L['mean_max']:>7.2f} {L['fleet_ratio']:>7.4f} "
              f"{L['median_ratio']:>7.4f} {L['p05_ratio']:>7.4f} "
              f"{L['p01_ratio']:>7.4f} {L['frac_below_0.95']:>6.1%} "
              f"{L['frac_below_0.90']:>7.1%}")
    print(f"    fleet = mean of maxima, ratio of means. median/p05/p01 and the")
    print(f"    two fractions are the PER-CELL ratio: a metric published per")
    print(f"    substation is answerable to the tail, not to the fleet mean.")
    L4 = res["levels"]["4/day"]
    print(f"\n    ONE HALVING, 8/day -> 4/day, is the closest measurable analogue")
    print(f"    to the unmeasured 24/day -> 8/day. It costs:")
    print(f"      fleet mean            {100*(1-L4['fleet_ratio']):.1f}% low")
    print(f"      median substation     {100*(1-L4['median_ratio']):.1f}% low")
    print(f"      1 cell in 20 (p05)    {100*(1-L4['p05_ratio']):.1f}% low")
    print(f"      1 cell in 100 (p01)   {100*(1-L4['p01_ratio']):.1f}% low")
    print(f"      cells >5% low         {L4['frac_below_0.95']:.1%}")
    print(f"      cells >10% low        {L4['frac_below_0.90']:.1%}")
    print(f"\n    HOW THIS ANALOGUE HELD UP, once the real thing was measured.")
    print(f"    Before the leadtime probe returned, this script argued that")
    print(f"    24 -> 8 would cost LESS than one halving, because it happens at")
    print(f"    the dense end where neighbouring hours are strongly correlated,")
    print(f"    and reported the table above as an UPPER BOUND.")
    print(f"    Direct measurement on one real day, 8-of-24 against all 24 over")
    print(f"    1,142,761 cells: 19.6% of cells more than 5% low, against the")
    print(f"    20.3% and 22.5% one halving costs. The SAME MAGNITUDE, not")
    print(f"    smaller. The argument was plausible and it was wrong, and it was")
    print(f"    wrong in the direction that favoured the cheaper fetch.")
    print(f"    Mechanism, in hindsight: a gust maximum is a single short-lived")
    print(f"    peak, not a quantity smeared across hours, and a peak does not")
    print(f"    care how correlated its neighbours are. The same mechanism shows")
    print(f"    up in this very table - a MONTHLY maximum over 248 samples loses")
    print(f"    as much to one halving as a DAILY maximum over 24 does - so the")
    print(f"    hope that an ANNUAL maximum over 2,920 samples would be robust")
    print(f"    does not survive either.")
    print(f"    Read this table as an ANALOGUE of the same magnitude, not as a")
    print(f"    bound. And read the tail, not the fleet mean: a published")
    print(f"    per-substation value is wrong for the substation it names.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--tiles", type=int, default=6)
    ap.add_argument("--cells-per-tile", type=int, default=3000)
    a = ap.parse_args()
    OUTDIR.mkdir(parents=True, exist_ok=True)

    if a.file:
        p = pathlib.Path(a.file)
        if not p.is_absolute():
            p = CACHE / a.file
        res = run_one(p, a.tiles, a.cells_per_tile)
        (OUTDIR / (p.stem + ".json")).write_text(json.dumps(res, indent=2))
        show(res)
        return 0

    if a.report:
        got = sorted(OUTDIR.glob("*.json"))
        if not got:
            sys.exit("nothing measured yet — run with --file first")
        print(f"\n  SAMPLING-DENSITY COST OF A GUST MAXIMUM — {len(got)} file(s)")
        first = []
        for g in got:
            res = json.loads(g.read_text())
            show(res)
            first.append(res["levels"]["4/day"]["frac_below_0.95"])
        if len(first) > 1:
            print(f"\n  ACROSS FILES — one halving leaves {min(first):.1%} to "
                  f"{max(first):.1%} of cells more than 5 per cent low.")
            print(f"  Reproducing across years makes it a property of the field,")
            print(f"  not of one January.")
        print(f"\n  CAVEAT: January only, and January is the favourable case.")
        return 0

    ap.error("give --file or --report")


if __name__ == "__main__":
    sys.exit(main())
