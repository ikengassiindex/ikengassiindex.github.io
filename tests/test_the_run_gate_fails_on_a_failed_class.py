"""The fetch run gate must fail when a data class fails.

`scripts/pipeline/fetch_data.py::cmd_fetch` ended `return 0` unconditionally,
two screens below the lines that print "✗ FAILED" and "✗ ERROR". Every data
class could fail for all 39 countries and the run exited green — recorded in
doctrine/FINDING_the_climate_chain_declares_what_it_never_derives.md, item 6.

This is the sentinel for the repair. Per DOCTRINE_a_check_must_read_the_artefact
it exercises the function rather than asserting on its source, and per §7.8 it
must be able to FAIL: `test_a_failure_fails_the_run` is red against the old
`return 0` and green against the new one.
"""
from __future__ import annotations

import importlib.util
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
FD = REPO / "scripts" / "pipeline" / "fetch_data.py"


def _module():
    spec = importlib.util.spec_from_file_location("fetch_data_under_test", FD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def fd(monkeypatch):
    """cmd_fetch with its three fetchers replaced by a scripted outcome."""
    mod = _module()

    def scripted(outcomes):
        def make(status):
            def fn(country, dry_run=False):
                return (outcomes.get(country, status), 0)
            return fn
        monkeypatch.setattr(mod, "_fetch_climate", make("ok"))
        monkeypatch.setattr(mod, "_fetch_seismic", make("ok"))
        monkeypatch.setattr(mod, "_fetch_socio", make("ok"))
    mod.scripted = scripted
    return mod


def test_all_ok_is_green(fd):
    fd.scripted({})
    assert fd.cmd_fetch(["france", "italy"]) == 0


def test_a_failure_fails_the_run(fd, capsys):
    """THE defect. One class, one country, and the run must not be green."""
    fd.scripted({"italy": "failed"})
    rc = fd.cmd_fetch(["france", "italy"])
    out = capsys.readouterr().out
    assert rc == 1, "a failed data class must fail the run"
    assert "italy" in out and "FAILED" in out, "the failing country must be named"


def test_every_class_failing_everywhere_fails(fd):
    fd.scripted({c: "failed" for c in ("france", "italy", "us")})
    assert fd.cmd_fetch(["france", "italy", "us"]) == 1


def test_an_exception_fails_the_run(fd):
    """The except branch writes 'error: ...'; that is a failure too."""
    def boom(country, dry_run=False):
        raise RuntimeError("CDS refused")
    fd.scripted({})
    import types
    setattr(fd, "_fetch_climate", boom)
    assert fd.cmd_fetch(["france"]) == 1


def test_skip_is_not_a_failure(fd):
    fd.scripted({})
    assert fd.cmd_fetch(["france"], skip={"climate", "seismic"}) == 0


def test_dry_run_is_not_a_failure(fd):
    def dry(country, dry_run=False):
        return ("dry-run", 0)
    fd.scripted({})
    for name in ("_fetch_climate", "_fetch_seismic", "_fetch_socio"):
        setattr(fd, name, dry)
    assert fd.cmd_fetch(["france"], dry_run=True) == 0
