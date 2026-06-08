"""SSI Pipeline — Scoring Engine

Phase 1 PR-1 (8 June 2026) introduces the modifier registry as the
canonical extension point for the modifier chain. See PHASE_1_IMPLEMENTATION_PLAN.md.
"""

# Phase 1 PR-1: modifier registry — canonical source of truth
from .modifier_registry import (
    MODIFIER_REGISTRY,
    compute_modifier_terms,
    per_modifier_impacts,
)

# Note: engine module is imported on demand by the L2 merge layer
# (scripts/pipeline/enrichment/merge.py) — keeping it out of the package
# __init__ avoids a circular import risk during the PR-2 rewrite when
# engine.py begins importing the registry above.

__all__ = [
    "MODIFIER_REGISTRY",
    "compute_modifier_terms",
    "per_modifier_impacts",
]
