"""One place that decides where a run's audit trail is written.

Before this module, seven scripts each hard-coded `Path.home() / "<name>.json"`.
The locations were declared in CLAUDE.md, so they were not secret — but they
were seven independent decisions, they scattered loose files across the
operator's home directory, and only one of them (`ssi_dedupe_substations.py`)
offered a way to point them somewhere else. That one carried the reasoning:

    the sidecar is the convenience copy, and the wrong thing to commit at
    scale: the per-id mappings for germany and us run to megabytes against a
    repo already sharding data files at 60 MB.

That reasoning is right and is preserved here — audit trails are NOT committed.
What changes is that the decision now lives once. The practical consequence is
that `SSI_AUDIT_DIR` can point every script at a single directory, including
one visible to a reviewer who is not sitting at the machine that ran the job.

Precedence, highest first:
    1. an explicit path (a script's --audit-dir)
    2. $SSI_AUDIT_DIR
    3. ~/ssi-audit-trail        (the default the dedupe utility established)

The git history is the audit trail of record for anything that changes a
published file. These reports are the working notes beside it.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

DEFAULT_AUDIT_DIRNAME = "ssi-audit-trail"
ENV_VAR = "SSI_AUDIT_DIR"


def resolve_audit_dir(explicit: str | Path | None = None) -> Path:
    """Return the directory this run's audit report belongs in (not created)."""
    if explicit:
        return Path(explicit).expanduser()
    env = os.environ.get(ENV_VAR)
    if env:
        return Path(env).expanduser()
    return Path.home() / DEFAULT_AUDIT_DIRNAME


def audit_path(stem: str,
               explicit: str | Path | None = None,
               timestamp: str | None = None,
               suffix: str = ".json") -> Path:
    """Full path for an audit report, with the directory created.

    `stem` is the report family, e.g. "migration_score_audit". The UTC
    timestamp is appended unless one is supplied.
    """
    ts = timestamp or time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    d = resolve_audit_dir(explicit)
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{stem}_{ts}{suffix}"


def add_audit_dir_argument(parser) -> None:
    """Attach the standard --audit-dir flag to an argparse parser."""
    parser.add_argument(
        "--audit-dir", metavar="PATH", default=None,
        help=(f"directory for this run's audit report "
              f"(default ${ENV_VAR}, else ~/{DEFAULT_AUDIT_DIRNAME}). "
              f"Audit reports are deliberately not committed."),
    )
