#!/usr/bin/env python3
"""hazard_accumulate.py — stream a hazard raster past 25,165 cells and keep
only what survives.

The winter leg is on the order of 1-2 TB and the fire leg ~260 GB. Neither is
stored. A window is fetched, evaluated, reduced to per-cell annual statistics,
and discarded; what is kept per cell per year is a few dozen bytes.

    25 165 cells x 86 years x a handful of statistics  ~= tens of MB

THREE CONSTRAINTS, from RESULT_a_raster_can_give_25165_values_not_622104.md.
They are enforced by the shape of this API, not by a comment asking nicely.

1. EVALUATE BEFORE AGGREGATING. For a conditional diagnostic such as FMICLIM,
   applying the threshold to interpolated or pre-averaged inputs is NOT the
   same operation as applying it per timestep and aggregating the outcome.
   That is the nonlinearity rule that broke I2 and blocks I8.

   So `Accumulator.observe()` takes ONE already-evaluated scalar per cell. It
   cannot be handed a stack of input fields, because a caller holding input
   fields has not yet done the step that must come first. The diagnostic lives
   in the caller; the accumulator never sees an input variable.

2. NEAREST CELL, NEVER BILINEAR. Cell assignment is the cell index's business
   (`build_hazard_cell_index.py`), fixed at floor(x/res + 0.5). Nothing here
   interpolates, and nothing here accepts a coordinate — only cell ordinals.

3. NATIVE RESOLUTION ONLY. Refining the grid manufactures per-asset variation.
   The accumulator carries the index's resolution into its output so a
   downstream reader cannot lose track of what resolution a number came from.

NUMERICAL NOTE. Mean and variance use Welford, not sum and sum-of-squares.
Over 31,412 daily values — 125,648 six-hourly ones — the naive form loses
significant digits to cancellation exactly where the estate cares, in the
variance of a near-constant series. Welford costs one extra multiply.

OBSERVING-SYSTEM REGIME. Every year is tagged, per
FINDING_the_pre1979_boundary_is_not_1979.md, because a statistic that averages
across a change in the observing system measures the observing system. The tag
travels with the data; it is not left for a reader to reconstruct.
"""
from __future__ import annotations

import json
import math
import os
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CELL_INDEX = os.path.join(ROOT, "data", "hazard_cell_index.json")

# ECMWF, read 21 September 2026: "no satellite data were used before 1970 ...
# before the mid-1940s no upper-air observations were available."
REGIMES: Tuple[Tuple[int, int, str], ...] = (
    (1940, 1945, "no_upper_air"),
    (1946, 1969, "pre_satellite"),
    (1970, 1978, "early_satellite"),
    (1979, 9999, "modern"),
)
# The WMO standard normal in force. Lies wholly inside "modern" — deliberately
# so, and the assertion below keeps it that way if either is ever edited.
NORMAL_FROM, NORMAL_TO = 1991, 2020


def regime_for(year: int) -> str:
    for lo, hi, name in REGIMES:
        if lo <= year <= hi:
            return name
    raise ValueError("year %r precedes the record (ERA5 begins 1940)" % year)


def _normal_is_inside_one_regime() -> bool:
    return len({regime_for(y) for y in range(NORMAL_FROM, NORMAL_TO + 1)}) == 1


assert _normal_is_inside_one_regime(), (
    "the standard normal now spans an observing-system change; a statistic "
    "computed on it would mix kinds of data. Re-read "
    "FINDING_the_pre1979_boundary_is_not_1979.md before changing either.")


class CellYear:
    """Welford state plus extremes and threshold counts, for one cell-year."""

    __slots__ = ("n", "mean", "_m2", "min", "max", "exceed")

    def __init__(self, n_thresholds: int = 0):
        self.n = 0
        self.mean = 0.0
        self._m2 = 0.0
        self.min = math.inf
        self.max = -math.inf
        self.exceed = [0] * n_thresholds

    def push(self, x: float, thresholds: Sequence[float]) -> None:
        self.n += 1
        d = x - self.mean
        self.mean += d / self.n
        self._m2 += d * (x - self.mean)
        if x < self.min:
            self.min = x
        if x > self.max:
            self.max = x
        for i, t in enumerate(thresholds):
            if x >= t:
                self.exceed[i] += 1

    @property
    def variance(self) -> Optional[float]:
        # Sample variance is undefined for one observation. Returning 0.0 there
        # would assert certainty from a single reading — section 7.5, a silent
        # absence dressed as a measurement.
        return self._m2 / (self.n - 1) if self.n > 1 else None

    def as_dict(self) -> dict:
        v = self.variance
        return {
            "n": self.n,
            "mean": self.mean,
            "sd": math.sqrt(v) if v is not None else None,
            "min": None if self.min == math.inf else self.min,
            "max": None if self.max == -math.inf else self.max,
            "exceed": list(self.exceed),
        }


class Accumulator:
    """Per-cell, per-year statistics of ONE already-evaluated quantity.

    The quantity is whatever the caller's diagnostic returns for a cell at a
    timestep — a DSR value, an FWI value, a 0/1 FMICLIM outcome. The
    accumulator does not know which, and deliberately cannot compute one.
    """

    def __init__(self, variable: str, n_cells: int, resolution_deg: float,
                 thresholds: Sequence[float] = ()):
        self.variable = variable
        self.n_cells = n_cells
        self.resolution_deg = resolution_deg
        self.thresholds = tuple(thresholds)
        self._years: Dict[int, List[Optional[CellYear]]] = {}
        self._observations = 0

    def observe(self, year: int, values: Sequence[Optional[float]]) -> None:
        """One timestep. `values[o]` is the evaluated quantity at cell ordinal o.

        None means the raster had no value there (sea mask, missing field). It
        is skipped and NOT counted, so `n` reports how many real observations a
        cell-year actually had rather than how many timesteps went past.
        """
        if len(values) != self.n_cells:
            raise ValueError(
                "expected one value per cell (%d), got %d — a partial timestep "
                "would silently bias every statistic it touches"
                % (self.n_cells, len(values)))
        row = self._years.get(year)
        if row is None:
            row = self._years[year] = [None] * self.n_cells
        nt = len(self.thresholds)
        for o, x in enumerate(values):
            if x is None:
                continue
            cy = row[o]
            if cy is None:
                cy = row[o] = CellYear(nt)
            cy.push(float(x), self.thresholds)
        self._observations += 1

    @property
    def years(self) -> List[int]:
        return sorted(self._years)

    def cell_year(self, cell: int, year: int) -> Optional[CellYear]:
        row = self._years.get(year)
        return row[cell] if row else None

    def normal(self, cell: int, frm: int = NORMAL_FROM, to: int = NORMAL_TO):
        """Mean over the standard normal, weighted by each year's count.

        Returns (value, years_present, years_expected). A caller that ignores
        the second and third numbers can publish a "1991-2020 normal" computed
        from four years; returning them together makes that a choice.
        """
        num = den = 0.0
        present = 0
        for y in range(frm, to + 1):
            cy = self.cell_year(cell, y)
            if cy is None or cy.n == 0:
                continue
            num += cy.mean * cy.n
            den += cy.n
            present += 1
        return (num / den if den else None), present, (to - frm + 1)

    def series(self, cell: int) -> List[dict]:
        """The full annual series for one cell, each year carrying its regime."""
        out = []
        for y in self.years:
            cy = self.cell_year(cell, y)
            if cy is None:
                continue
            rec = cy.as_dict()
            rec["year"] = y
            rec["regime"] = regime_for(y)
            out.append(rec)
        return out

    def summary(self) -> dict:
        return {
            "variable": self.variable,
            "resolution_deg": self.resolution_deg,
            "n_cells": self.n_cells,
            "thresholds": list(self.thresholds),
            "years": self.years,
            "timesteps_observed": self._observations,
            "regimes_present": sorted({regime_for(y) for y in self.years}),
        }


def load_cell_index(path: str = CELL_INDEX) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def fan_out(per_cell: Sequence[Optional[float]], cell_index: dict,
            lat: float, lon: float) -> Tuple[Optional[float], int]:
    """The value for an asset, and the cell it came from.

    Returns the cell ordinal alongside the value so that the collapse is
    auditable: 147 French substations share a number BECAUSE they share a cell,
    and a reader can see it without re-deriving the grid.
    """
    res = cell_index["resolution_deg"]
    key = (math.floor(lat / res + 0.5), math.floor(lon / res + 0.5))
    lookup = getattr(cell_index, "_lookup", None)
    if lookup is None:
        lookup = {(int(round(c["lat"] / res)), int(round(c["lon_signed"] / res))): c["o"]
                  for c in cell_index["cells"]}
        try:
            cell_index["_lookup"] = lookup
        except Exception:
            pass
    o = lookup.get(key)
    if o is None:
        raise KeyError("no cell for (%.4f, %.4f) — the asset is outside the "
                       "index, which means the index is stale" % (lat, lon))
    return per_cell[o], o
