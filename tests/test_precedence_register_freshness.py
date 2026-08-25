"""
Sentinel — the document precedence register must exist, be current, and agree
with what the repository actually declares.

WHY THIS TEST EXISTS
────────────────────
78,505 substations published fabricated resilience scores because the scoring
engine followed one document's implicit behaviour while three other documents
said the opposite, and **no rule existed to say which won**. The engine had
been contradicting `classify_band`, `compute_fleet_summary` and Convention #56
— all three already correct — for weeks, and nothing in the estate could
adjudicate it.

`SSI_DOCUMENT_PRECEDENCE_REGISTER.md` is that rule. A precedence register that
goes stale is the exact failure it exists to prevent, so it is enforced here
rather than left to good intentions.

WHAT THIS PINS
──────────────
1.  The register is reachable from this repository.
2.  It declares a methodology version, and that version matches `versions.json`
    — the release source of truth. A register that disagrees with the running
    system is worse than none.
3.  It has been reviewed within 90 days, matching the cascade playbook's
    90-day partial-cascade retro-audit trigger (§6.4).
4.  Its structural sections are intact — someone editing it cannot silently
    delete the precedence ordering or the known-wrong register.

WHAT THIS DELIBERATELY DOES NOT DO
──────────────────────────────────
It does not parse the register's prose or grade its content. A sentinel that
tries to validate meaning becomes a second source of truth and drifts from the
first. This checks that the register exists, is current, and does not contradict
`versions.json`. Judgement stays with the reader.

Cross-reference: SSI_DOCUMENT_PRECEDENCE_REGISTER.md §7 (anchored maintenance);
CLAUDE.md Discipline #50; modification-log M-046 / M-049.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

#: The register lives in the Ikenga SL OneDrive tenant, not in this repo — it
#: governs four trees, of which this repository is one. Resolution order:
#:   1. SSI_PRECEDENCE_REGISTER env var (CI override)
#:   2. the operator's local OneDrive path
#:   3. a repo-root copy, if one is ever vendored
_ENV = os.environ.get("SSI_PRECEDENCE_REGISTER")
_ONEDRIVE = (
    Path.home() / "Library" / "CloudStorage" / "OneDrive-IkengaSL"
    / "Internal - IKENGA EU - Documents" / "0.22. IP agenda" / "SSI Index"
    / "SSI_DOCUMENT_PRECEDENCE_REGISTER.md"
)
_CANDIDATES = [Path(_ENV)] if _ENV else []
_CANDIDATES += [_ONEDRIVE, REPO_ROOT / "SSI_DOCUMENT_PRECEDENCE_REGISTER.md"]

MAX_AGE_DAYS = 90

REQUIRED_SECTIONS = (
    "## 1. Precedence",
    "## 2. Authoritative version",
    "## 3. Known-wrong statements",
    "## 4. Number-space collisions",
    "## 5. Settled questions",
    "## 6. Open items",
    "## 7. Maintenance",
)


def _register() -> Path | None:
    for c in _CANDIDATES:
        if c.exists():
            return c
    return None


@pytest.fixture(scope="module")
def register_text():
    p = _register()
    if p is None:
        pytest.skip(
            "precedence register not reachable from this checkout. It lives in "
            "the Ikenga SL OneDrive tenant; set SSI_PRECEDENCE_REGISTER to its "
            "path to enforce this sentinel in CI. Skipping rather than failing "
            "so a fresh clone is not blocked — but a run that skips this test "
            "is NOT evidence the register is healthy."
        )
    return p.read_text(encoding="utf-8", errors="replace")


class TestRegisterIntact:

    def test_all_sections_present(self, register_text):
        missing = [s for s in REQUIRED_SECTIONS if s not in register_text]
        assert not missing, (
            f"precedence register is missing sections: {missing}. These are "
            f"structural — the ordering (§1), the version table (§2) and the "
            f"known-wrong list (§3) are what stop bad statements propagating."
        )

    def test_declares_a_precedence_ordering(self, register_text):
        assert "principle beats formula" in register_text.lower(), (
            "the register no longer states its ordering principle "
            "('principle beats formula, formula beats code, code beats prose "
            "about code'). Without it §1 is a table with no rule."
        )


class TestRegisterAgreesWithTheRunningSystem:

    def test_methodology_version_matches_versions_json(self, register_text):
        """A register that disagrees with versions.json is worse than none."""
        vj = json.loads((REPO_ROOT / "versions.json").read_text(encoding="utf-8"))
        declared = str(vj.get("methodology") or "").strip()
        assert declared, "versions.json has no 'methodology' key"
        m = re.search(r"Live methodology version\s*—\s*\*\*v?([0-9.]+)\*\*", register_text)
        assert m, (
            "the register no longer declares a live methodology version in §5. "
            "That declaration is what resolves the v4.2 / v4.23 / v4.24 "
            "ambiguity; without it the question reopens."
        )
        assert m.group(1) == declared, (
            f"precedence register declares methodology v{m.group(1)} but "
            f"versions.json says v{declared}. One of them is wrong, and until "
            f"they agree nobody can cite either. Update both in the same commit "
            f"(register §7.1 rule 2)."
        )


class TestRegisterIsCurrent:

    def test_reviewed_within_max_age(self):
        p = _register()
        if p is None:
            pytest.skip("register not reachable — see fixture message")
        age = _dt.date.today() - _dt.date.fromtimestamp(p.stat().st_mtime)
        assert age.days <= MAX_AGE_DAYS, (
            f"precedence register last touched {age.days} days ago, beyond the "
            f"{MAX_AGE_DAYS}-day review cadence (§7.3, matching the cascade "
            f"playbook's 90-day partial-cascade retro-audit trigger). Re-read "
            f"§§1-5 and update §2, or the register becomes the stale authority "
            f"it was written to replace."
        )
