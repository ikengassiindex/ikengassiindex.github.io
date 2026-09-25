"""Audit-trail destinations are decided in one place.

Before scripts/pipeline/utils/audit_dir.py, seven scripts each hard-coded
`Path.home() / "<something>_audit_<ts>.json"`. The locations were declared in
CLAUDE.md, so nothing was hidden — but they were seven independent decisions,
none of them overridable except one, and the files landed loose in the
operator's home directory where nothing but that machine could see them.

These assertions pin the shape, not the prose. The AST is walked and
identifiers are inspected; the module docstrings talk about `Path.home()`
and a grep would fail on its own explanation.
"""

from __future__ import annotations

import ast
import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.pipeline.utils.audit_dir import (  # noqa: E402
    DEFAULT_AUDIT_DIRNAME,
    ENV_VAR,
    audit_path,
    resolve_audit_dir,
)

RESOLVER = REPO / "scripts" / "pipeline" / "utils" / "audit_dir.py"


def _python_files():
    for p in (REPO / "scripts").rglob("*.py"):
        if p == RESOLVER:
            continue
        yield p


def _home_joined_with(tree):
    """Yield the string literals that get `/`-joined onto Path.home()."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Div):
            continue
        left = node.left
        is_home = (
            isinstance(left, ast.Call)
            and isinstance(left.func, ast.Attribute)
            and left.func.attr == "home"
        )
        if not is_home:
            continue
        right = node.right
        if isinstance(right, ast.Constant) and isinstance(right.value, str):
            yield right.value
        elif isinstance(right, ast.JoinedStr):
            yield "".join(
                v.value for v in right.values
                if isinstance(v, ast.Constant) and isinstance(v.value, str)
            )
        else:
            yield ""


def test_no_script_writes_an_audit_path_from_Path_home():
    """The ninth copy of the decision does not get made."""
    offenders = []
    for path in _python_files():
        try:
            tree = ast.parse(path.read_text())
        except SyntaxError:                      # not ours to police here
            continue
        for joined in _home_joined_with(tree):
            if "audit" in joined.lower():
                offenders.append(f"{path.relative_to(REPO)} -> Path.home() / {joined!r}")
    assert not offenders, (
        "audit destinations must come from audit_dir.audit_path():\n  "
        + "\n  ".join(offenders)
    )


def test_credential_paths_are_left_alone():
    """The rule is about audit output, not about ~/.cdsapirc. Pin 9."""
    climate = REPO / "scripts" / "pipeline" / "ingestion" / "climate.py"
    if not climate.exists():
        pytest.skip("climate.py not present")
    joined = list(_home_joined_with(ast.parse(climate.read_text())))
    assert ".cdsapirc" in joined, (
        "the credential path should still resolve from Path.home() — "
        "this test exists so a future sweep does not 'fix' it"
    )


def test_precedence_is_explicit_then_env_then_default(monkeypatch, tmp_path):
    monkeypatch.setenv(ENV_VAR, str(tmp_path / "from_env"))
    assert resolve_audit_dir(tmp_path / "explicit") == tmp_path / "explicit"
    assert resolve_audit_dir() == tmp_path / "from_env"
    monkeypatch.delenv(ENV_VAR)
    assert resolve_audit_dir() == Path.home() / DEFAULT_AUDIT_DIRNAME


def test_default_is_a_named_directory_not_loose_in_home(monkeypatch):
    """The old behaviour dropped files directly into $HOME. It does not now."""
    monkeypatch.delenv(ENV_VAR, raising=False)
    assert resolve_audit_dir() != Path.home()
    assert resolve_audit_dir().parent == Path.home()


def test_audit_path_creates_the_directory_and_stamps_the_name(tmp_path):
    p = audit_path("demo_audit", explicit=tmp_path / "nested" / "deeper")
    assert p.parent.is_dir(), "the directory must exist before a caller writes"
    assert p.name.startswith("demo_audit_") and p.suffix == ".json"


def test_every_audit_emitting_script_imports_the_resolver():
    """Named so a reader can see which scripts are in scope."""
    expected = [
        "scripts/pipeline/enrichment/migration_score.py",
        "scripts/pipeline/enrichment/migration_score_semantic_normalise.py",
        "scripts/pipeline/enrichment/catchment_population.py",
        "scripts/pipeline/enrichment/socio_economic_backfill.py",
        "scripts/normalise_bands_per_country.py",
        "scripts/audit_out_of_polygon_clusters.py",
        "scripts/ssi_dedupe_substations.py",
    ]
    missing = [
        rel for rel in expected
        if "utils.audit_dir import" not in (REPO / rel).read_text()
    ]
    assert not missing, f"no longer routed through the resolver: {missing}"
