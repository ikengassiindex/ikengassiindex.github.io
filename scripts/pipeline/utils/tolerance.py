"""Boundary-tolerance resolver — single source of truth (Discipline #36).

Every ingestion module obtains its polygon-filter tolerance from
:func:`resolve_boundary_tolerance_km`. Nothing else may read
``cross_border_tolerances.json`` directly.

WHY THIS MODULE EXISTS
──────────────────────
Until 19 August 2026 each of the 30 ingestion modules carried its own
inline lookup against ``cross_border_tolerances.json``. The lookups drifted
into two mutually incompatible dialects:

    tol_cfg["per_country"][slug]["tolerance_km"]           # 22 modules
    tol_cfg["countries"][slug]["boundary_tolerance_km"]    #  8 modules

The file only ever had the second shape. All 22 modules on the first dialect
therefore resolved to ``{}`` and fell through to a hardcoded literal, with no
warning of any kind. For 21 of them the literal happened to match the
configured value (or no value was configured), so the fault was invisible.

For **Greece** it was not. Greece is configured at 5.0 km — a figure chosen
deliberately for the Aegean archipelago and the indented Peloponnese
coastline — and ran at the 0.1 km literal instead, 50x too tight. The Greek
ingestion dropped 18 substations at 0.1 km where 5.0 km would have dropped 1;
17 real island and gulf substations were discarded, and the audit sidecar
recorded ``tolerance_km_applied: 5.0`` while the run had demonstrably used
0.1. The standalone cross-border audit tool read the config correctly and
reported Greece CLEAN, so audit and ingestion disagreed about the same file.

The defect class here is duplication, not arithmetic. One resolver, one
schema, one logged decision, one place to audit.

CONFIG SCHEMA (authoritative)
─────────────────────────────
``cross_border_tolerances.json`` at repo root::

    {
      "_schema": "...",
      "_default_tolerance_km": 0.1,
      "countries": {
        "<slug>": {"boundary_tolerance_km": <float>, "rationale": "<str>"}
      }
    }

Keys prefixed with ``_`` are metadata by convention. ``countries`` is keyed by
the public country slug (``new-zealand``, ``costa-rica``), not by the Python
package name (``new_zealand``, ``costa_rica``).

RESOLUTION ORDER
────────────────
1. ``countries[slug].boundary_tolerance_km``  → source ``config:countries``
2. ``module_fallback`` argument               → source ``module_fallback``
3. ``_default_tolerance_km``                  → source ``config:default``
4. ``_HARD_FLOOR_KM`` (0.1)                   → source ``hard_floor``

``module_fallback`` deliberately outranks ``_default_tolerance_km``. A module
that hardcodes a non-default literal is expressing a per-country judgement;
the cohort default is for countries with no opinion. Ordering it the other way
round silently demotes any such country to 0.1 km — Finland (literal 5.0 km,
no config entry, Turku/Åland archipelago) was measured regressing exactly that
way during this refactor, which is why the order reads as it does.

When ``module_fallback`` wins **and** differs from ``_default_tolerance_km``,
the country holds an undeclared opinion: the config should carry an explicit
entry for it. That case is logged at WARNING so the gap stays visible.

Every resolution is logged with its source, so a run's tolerance provenance is
recoverable from the log alone.

Cross-reference: Discipline #36 (cross-border), modification-log M-026.
"""

from __future__ import annotations

import json
import logging
import threading
from pathlib import Path
from typing import NamedTuple

logger = logging.getLogger(__name__)

# scripts/pipeline/ingestion/_tolerance.py → repo root is four levels up
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
TOLERANCE_CONFIG_PATH = REPO_ROOT / "cross_border_tolerances.json"

#: Last-resort value if the config is missing entirely and the caller gave no
#: fallback. Matches the historical cadastral default.
_HARD_FLOOR_KM = 0.1

#: Package-name → public-slug corrections. The config is keyed by public slug.
_PACKAGE_TO_SLUG = {
    "new_zealand": "new-zealand",
    "costa_rica": "costa-rica",
}

_cache: dict | None = None
_cache_lock = threading.Lock()


class ToleranceResolution(NamedTuple):
    """The resolved tolerance and where it came from."""

    slug: str
    value_km: float
    source: str

    def __float__(self) -> float:  # pragma: no cover - convenience only
        return self.value_km


def normalise_slug(slug: str) -> str:
    """Map a Python package name to the public slug used in the config."""
    return _PACKAGE_TO_SLUG.get(slug, slug.replace("_", "-"))


def load_config(*, config_path: Path | None = None, refresh: bool = False) -> dict:
    """Read and cache ``cross_border_tolerances.json``.

    A missing or malformed file is not fatal — it degrades to an empty dict
    and every caller falls through to its own fallback. That degradation is
    logged loudly (Convention #56: visibly-honest degradation).
    """
    global _cache
    path = config_path or TOLERANCE_CONFIG_PATH
    if config_path is not None or refresh:
        return _read_config(path)
    with _cache_lock:
        if _cache is None:
            _cache = _read_config(path)
    return _cache


def _read_config(path: Path) -> dict:
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        logger.error(
            "cross_border_tolerances.json not found at %s — every country "
            "will fall back to its module default. Cross-border filtering is "
            "running unconfigured.",
            path,
        )
        return {}
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        logger.error(
            "cross_border_tolerances.json at %s is malformed (%s) — every "
            "country will fall back to its module default.",
            path,
            exc,
        )
        return {}

    if not isinstance(cfg, dict):
        logger.error(
            "cross_border_tolerances.json at %s is not a JSON object.", path
        )
        return {}

    # Guard against a silent return of the pre-19-August dialect. If someone
    # reintroduces `per_country`, say so rather than ignoring it.
    if "per_country" in cfg:
        logger.error(
            "cross_border_tolerances.json carries a legacy 'per_country' key. "
            "The authoritative schema is 'countries' with "
            "'boundary_tolerance_km'. The legacy key is IGNORED — see M-026.",
        )
    if "countries" not in cfg:
        logger.warning(
            "cross_border_tolerances.json has no 'countries' key; only the "
            "default tolerance will be available.",
        )
    return cfg


def resolve(
    slug: str,
    *,
    module_fallback: float | None = None,
    config_path: Path | None = None,
) -> ToleranceResolution:
    """Resolve the boundary tolerance for ``slug``, with provenance.

    Args:
        slug: country slug or Python package name; normalised either way.
        module_fallback: the module's historical literal, used only if the
            config supplies neither a per-country value nor a default. Passing
            it preserves each module's prior behaviour when the config is
            unavailable.
        config_path: override for tests.

    Returns:
        ToleranceResolution(slug, value_km, source)
    """
    key = normalise_slug(slug)
    cfg = load_config(config_path=config_path)

    entry = (cfg.get("countries") or {}).get(key) or {}
    value = entry.get("boundary_tolerance_km")
    if _is_number(value):
        return ToleranceResolution(key, float(value), "config:countries")

    default = cfg.get("_default_tolerance_km")

    # module_fallback outranks the cohort default — see RESOLUTION ORDER.
    if module_fallback is not None:
        return ToleranceResolution(key, float(module_fallback), "module_fallback")

    if _is_number(default):
        return ToleranceResolution(key, float(default), "config:default")

    return ToleranceResolution(key, _HARD_FLOOR_KM, "hard_floor")


def _is_number(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def resolve_boundary_tolerance_km(
    slug: str,
    *,
    module_fallback: float | None = None,
    config_path: Path | None = None,
) -> float:
    """Resolve the boundary tolerance for ``slug`` and log the decision.

    This is the function ingestion modules call.
    """
    res = resolve(slug, module_fallback=module_fallback, config_path=config_path)
    if res.source == "config:countries":
        logger.info(
            "Boundary tolerance for %s: %.3f km (source: %s)",
            res.slug, res.value_km, res.source,
        )
        return res.value_km

    if res.source == "module_fallback":
        cfg_default = load_config(config_path=config_path).get("_default_tolerance_km")
        if _is_number(cfg_default) and abs(float(cfg_default) - res.value_km) > 1e-9:
            logger.warning(
                "Boundary tolerance for %s: %.3f km from the module literal, "
                "not from config. It differs from _default_tolerance_km "
                "(%.3f km), so %s holds an UNDECLARED per-country opinion — "
                "add an explicit 'countries.%s.boundary_tolerance_km' entry to "
                "cross_border_tolerances.json.",
                res.slug, res.value_km, float(cfg_default), res.slug, res.slug,
            )
            return res.value_km

    logger.warning(
        "Boundary tolerance for %s: %.3f km (source: %s) — not configured.",
        res.slug, res.value_km, res.source,
    )
    return res.value_km


def audit_all(*, config_path: Path | None = None) -> dict[str, ToleranceResolution]:
    """Return the effective tolerance for every configured country.

    Auditability hook: lets a sentinel or an operator dump exactly what each
    country resolves to, without importing 30 ingestion modules.
    """
    cfg = load_config(config_path=config_path)
    slugs = sorted((cfg.get("countries") or {}).keys())
    return {s: resolve(s, config_path=config_path) for s in slugs}


__all__ = [
    "REPO_ROOT",
    "TOLERANCE_CONFIG_PATH",
    "ToleranceResolution",
    "audit_all",
    "load_config",
    "normalise_slug",
    "resolve",
    "resolve_boundary_tolerance_km",
]
