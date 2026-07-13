"""
SSI Pipeline — Canada v4.23 ingestion package.

Public entry points:
  - canvec_resmgt          — federal canonical (substations + transmission lines)
  - nacei_transmission     — federal strategic cross-check (transmission-line backbone)
  - yec_substations        — Yukon Territory operational-utility supplementary
  - ns_nstdb_utilities     — Nova Scotia provincial supplementary

Architectural anchor: canada/v4_23-ingestion-audit-canada-preflight.yaml
(schema v2, 2026-07-12) — see METHODOLOGY_DISCIPLINES.md §5ter state-transition
auditability contract.

Every connector emits (a) a normalised list of SubstationRecord + TransmissionLineRecord
dataclasses; (b) a companion v4_23-ingestion-audit-canada-<source>.yaml sidecar
per §5ter; (c) a Discipline #36 point-in-polygon filter over the Canada bounds
polygon; (d) a Discipline #41 substation ↔ line parity assertion.
"""

from ._base import (
    SubstationRecord,
    TransmissionLineRecord,
    IngestionResult,
    apply_bounds_filter,
    assert_line_parity,
    emit_audit_sidecar,
)

__all__ = [
    "SubstationRecord",
    "TransmissionLineRecord",
    "IngestionResult",
    "apply_bounds_filter",
    "assert_line_parity",
    "emit_audit_sidecar",
    # Federation entry point
    "federate",
]


def federate(**kwargs):
    """Convenience re-export of federation.federate() for the top-level API."""
    from . import federation
    return federation.federate(**kwargs)
