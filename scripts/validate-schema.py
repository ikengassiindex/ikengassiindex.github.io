#!/usr/bin/env python3
"""
SSI v4.0.2 — JSON Schema Validator (BACKWARD-COMPAT SHIM)

PR-5 (audit memo 2026-06-08): the canonical module is now
`scripts/validate_schema.py` (underscore-named, importable as Python module).
This shim is preserved so any cron job or operator command-line invocation
that uses the hyphen-named path continues to work without code changes.

Both paths produce identical exit codes + output:
  python3 scripts/validate-schema.py <file>   # hyphen path (this shim)
  python3 scripts/validate_schema.py <file>   # canonical path

The shim emits a DeprecationWarning (visible with `python3 -W default`) so
operators see the migration message. PR-7 will retire the shim entirely
after the cron jobs migrate.
"""
import importlib.util
import sys
import warnings
from pathlib import Path

_THIS = Path(__file__).resolve()
_CANONICAL = _THIS.parent / "validate_schema.py"

if not _CANONICAL.exists():
    print(f"FATAL: canonical module {_CANONICAL} missing", file=sys.stderr)
    sys.exit(2)

# Soft-deprecation banner — visible under `python3 -W default::DeprecationWarning`
warnings.warn(
    "scripts/validate-schema.py is a backward-compat shim (PR-5). "
    "Migrate to: python3 scripts/validate_schema.py (or import as Python module).",
    DeprecationWarning, stacklevel=2,
)

# Delegate to canonical module
_spec = importlib.util.spec_from_file_location("validate_schema_canonical", _CANONICAL)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

if __name__ == "__main__":
    _mod.main()
