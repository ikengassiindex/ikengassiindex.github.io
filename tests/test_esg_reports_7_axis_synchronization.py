"""
Sentinel — R7 SFDR PAI 7-axis synchronization between pipeline registry and frontend rendering.

Landed 16 July 2026 as part of R7 Phase 4e per FC v3 §14 subsection 13.7.

Guards against future drift between:
- scripts/pipeline/config.py::ESG_REPORTS (backend registry)
- esg-sections.js::ESG_REPORTS (frontend rendering)
- esg-sections.js::computeESGScores() (readiness scoring)
- esg-sections.js::labels[] (radar axis labels)

Any structural mismatch (R7 missing, R3/R4/R5 title drift, radar array length ≠ 7)
fails CI before the next commit lands.

Convention cross-refs:
- Convention #7 (Data-Layer Anchoring — Re_norm proxy path)
- Convention #56 (visibly-honest degradation — GAP status for Convention #56 neutral defaults)
- Convention #78 §4bis.4 (two-phase workflow — Phase 1 L1 ingestion then Phase 2 L2/L3/L4 rescore)
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PY = REPO_ROOT / "scripts" / "pipeline" / "config.py"
ESG_SECTIONS_JS = REPO_ROOT / "esg-sections.js"

FC_V3_S14_CANONICAL_ORDER = [
    ("R1", "Climate Physical Risk Assessment"),
    ("R2", "Grid Equity & Social Vulnerability"),
    ("R3", "Infrastructure Resilience [Re composite home]"),
    ("R4", "Pollution & Corrosion"),
    ("R5", "Energy Transition & DER Stress"),
    ("R6", "Cybersecurity Exposure"),
    ("R7", "SFDR PAI Infrastructure Disclosure"),
]


# ── Backend (scripts/pipeline/config.py::ESG_REPORTS) ──────────────────────

@pytest.fixture(scope="module")
def config_py_source() -> str:
    return CONFIG_PY.read_text(encoding="utf-8")


def test_config_py_has_r7_sfdr_pai_entry(config_py_source: str) -> None:
    """R7 SFDR PAI Infrastructure Disclosure must be registered in config.py::ESG_REPORTS."""
    assert '"R7":' in config_py_source, (
        "R7 SFDR PAI Infrastructure Disclosure missing from config.py::ESG_REPORTS. "
        "Expected registration per FC v3 §14 subsection 13.7."
    )
    assert "SFDR PAI Infrastructure Disclosure" in config_py_source


def test_config_py_r3_relabelled_infrastructure_resilience(config_py_source: str) -> None:
    """R3 must be relabelled to 'Infrastructure Resilience [Re composite home]' per FC v3 §14."""
    assert "Infrastructure Resilience [Re composite home]" in config_py_source, (
        "R3 must be relabelled to 'Infrastructure Resilience [Re composite home]'. "
        "The legacy 'EU Taxonomy Alignment' label was retired 16 July 2026."
    )


def test_config_py_r4_r5_swap_pollution_before_transition(config_py_source: str) -> None:
    """R4 = Pollution & Corrosion (before) R5 = Energy Transition per FC v3 §14 canonical order."""
    r4_match = re.search(r'"R4":\s*\{[^}]*"name":\s*"([^"]+)"', config_py_source, re.DOTALL)
    r5_match = re.search(r'"R5":\s*\{[^}]*"name":\s*"([^"]+)"', config_py_source, re.DOTALL)
    assert r4_match is not None, "R4 entry missing from config.py::ESG_REPORTS"
    assert r5_match is not None, "R5 entry missing from config.py::ESG_REPORTS"
    assert "Pollution" in r4_match.group(1), (
        f"R4 must be 'Pollution & Corrosion' post-swap; got {r4_match.group(1)!r}"
    )
    assert "Transition" in r5_match.group(1) or "DER" in r5_match.group(1), (
        f"R5 must be 'Energy Transition & DER Stress' post-swap; got {r5_match.group(1)!r}"
    )


def test_config_py_r7_required_fields_re_norm(config_py_source: str) -> None:
    """R7 SFDR PAI must use Re_norm as its canonical required field (Convention #7 Data-Layer Anchoring)."""
    r7_block = re.search(
        r'"R7":\s*\{[^}]*"required_fields":\s*\[([^\]]+)\]',
        config_py_source,
        re.DOTALL,
    )
    assert r7_block is not None, "R7 required_fields block missing from config.py"
    assert "Re_norm" in r7_block.group(1), (
        "R7 SFDR PAI must anchor on Re_norm (public-dashboard field name). "
        "The compliance-clone 'Re_normalised' naming is a cross-repo inconsistency "
        "deferred to Q3 2026 methodology-hardening per Convention #66."
    )


# ── Frontend (esg-sections.js::ESG_REPORTS) ────────────────────────────────

@pytest.fixture(scope="module")
def esg_sections_js_source() -> str:
    return ESG_SECTIONS_JS.read_text(encoding="utf-8")


def test_esg_sections_js_has_7_report_entries(esg_sections_js_source: str) -> None:
    """esg-sections.js::ESG_REPORTS must have exactly 7 id: 'report-N' entries."""
    ids = re.findall(r"id:\s*'report-(\d+)'", esg_sections_js_source)
    assert ids == ["1", "2", "3", "4", "5", "6", "7"], (
        f"Expected report ids in canonical order [1..7], got {ids}. "
        f"R7 SFDR PAI landed 16 July 2026 as 7th entry."
    )


def test_esg_sections_js_titles_match_fc_v3_s14_canonical(esg_sections_js_source: str) -> None:
    """Each report title must match FC v3 §14 canonical order + terminology."""
    title_pattern = re.compile(
        r"id:\s*'report-(\d+)',\s*num:\s*'\d+',\s*title:\s*'([^']+)'"
    )
    found = dict(title_pattern.findall(esg_sections_js_source))
    for expected_num, expected_title in FC_V3_S14_CANONICAL_ORDER:
        actual_title = found.get(expected_num[1:])
        assert actual_title == expected_title, (
            f"{expected_num} title drift: expected {expected_title!r}, got {actual_title!r}. "
            f"See FC v3 §14 subsection 13.7 for canonical titles."
        )


def test_esg_sections_js_r7_uses_re_norm_field(esg_sections_js_source: str) -> None:
    """R7 SFDR PAI block must reference d.Re_norm (public-dashboard field name)."""
    r7_start = esg_sections_js_source.find("id: 'report-7'")
    assert r7_start >= 0, "R7 report-7 block missing from esg-sections.js"
    # Look at next 4000 chars for Re_norm reference
    r7_body = esg_sections_js_source[r7_start:r7_start + 4000]
    assert "d.Re_norm" in r7_body or "Re_norm" in r7_body, (
        "R7 SFDR PAI block must anchor on d.Re_norm per Convention #7 (Data-Layer Anchoring). "
        "Public dashboard uses Re_norm; compliance clone uses Re_normalised (Convention #66 gap)."
    )


def test_esg_sections_js_computeESGScores_returns_7_elements(esg_sections_js_source: str) -> None:
    """computeESGScores() return statement must list exactly 7 elements (R1..R7)."""
    # Match the return array in computeESGScores
    match = re.search(
        r"function computeESGScores\(d\)[\s\S]*?return\s*\[([\s\S]*?)\];",
        esg_sections_js_source,
    )
    assert match is not None, "computeESGScores return block not found"
    body = match.group(1)
    # Count Math.round entries (one per axis)
    entries = re.findall(r"Math\.round\(r\d+\s*\*\s*100\)\s*/\s*100", body)
    assert len(entries) == 7, (
        f"computeESGScores must return 7-element array (R1..R7). "
        f"Found {len(entries)} Math.round entries. R7 landed 16 July 2026."
    )
    # Verify r1..r7 present
    for i in range(1, 8):
        assert f"Math.round(r{i} * 100) / 100" in body, (
            f"computeESGScores return array missing r{i} entry."
        )


def _extract_radar_labels_body(source: str) -> str:
    """Extract the 'var labels = [ ... ];' body handling nested brackets like '[Re]' in R3."""
    match = re.search(r"var labels\s*=\s*\[", source)
    assert match is not None, "var labels = [ ... assignment not found"
    start = match.end()  # position AFTER opening [
    depth = 1
    i = start
    while i < len(source) and depth > 0:
        ch = source[i]
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        i += 1
    assert depth == 0, "var labels array bracket balance failed"
    return source[start:i - 1]  # body without the closing ]


def test_esg_sections_js_radar_labels_have_7_axes(esg_sections_js_source: str) -> None:
    """Radar chart labels array must have exactly 7 axis entries (R1..R7)."""
    labels_body = _extract_radar_labels_body(esg_sections_js_source)
    r_axes = re.findall(r"\['R(\d)", labels_body)
    assert r_axes == ["1", "2", "3", "4", "5", "6", "7"], (
        f"Radar labels array must list R1..R7 in canonical order; got R{r_axes}. "
        f"R7 SFDR PAI landed 16 July 2026 per FC v3 §14."
    )


def test_esg_sections_js_r3_radar_label_infrastructure_resilience(esg_sections_js_source: str) -> None:
    """R3 radar axis label must reference 'Infrastructure' and 'Resilience' (post FC v3 §14 relabel)."""
    labels_body = _extract_radar_labels_body(esg_sections_js_source)
    # R3 label pair — allow internal [Re] brackets via balanced-bracket manual walk
    r3_start = labels_body.find("['R3")
    assert r3_start >= 0, "R3 label pair missing from radar labels array"
    # Walk forward with bracket-depth tracking to find the matching closing ]
    depth = 0
    i = r3_start
    while i < len(labels_body):
        if labels_body[i] == "[":
            depth += 1
        elif labels_body[i] == "]":
            depth -= 1
            if depth == 0:
                break
        i += 1
    r3_str = labels_body[r3_start:i + 1]
    assert "Infrastructure" in r3_str and "Resilience" in r3_str, (
        f"R3 radar label must reference 'Infrastructure' + 'Resilience' post FC v3 §14 relabel; "
        f"got {r3_str!r}. Legacy 'EU Taxonomy Alignment' label retired 16 July 2026."
    )


def test_esg_sections_js_r4_r5_swap_pollution_before_transition(esg_sections_js_source: str) -> None:
    """R4 = Pollution + R5 = Transition per FC v3 §14 canonical order (post 16 Jul 2026 swap)."""
    labels_body = _extract_radar_labels_body(esg_sections_js_source)
    # R4 + R5 labels don't contain nested [] so simpler regex works
    r4_pair = re.search(r"\['R4[^\[\]]*',\s*'[^']*'\]", labels_body)
    r5_pair = re.search(r"\['R5[^\[\]]*',\s*'[^']*'\]", labels_body)
    assert r4_pair is not None, "R4 label pair missing from radar labels array"
    assert r5_pair is not None, "R5 label pair missing from radar labels array"
    assert "Pollution" in r4_pair.group(0), (
        f"R4 radar label must be 'Pollution' post-swap; got {r4_pair.group(0)!r}"
    )
    assert "Transition" in r5_pair.group(0) or "Energy" in r5_pair.group(0), (
        f"R5 radar label must be 'Energy Transition' post-swap; got {r5_pair.group(0)!r}"
    )


# ── Cross-file synchronization ──────────────────────────────────────────────

def test_backend_frontend_ordering_consistent(config_py_source: str, esg_sections_js_source: str) -> None:
    """Backend R1..R7 order must match frontend R1..R7 order (no swap drift between the two layers)."""
    # Extract backend order
    backend_keys = re.findall(r'"(R[1-7])":', config_py_source)
    # Frontend order via report ids
    frontend_ids = re.findall(r"id:\s*'report-([1-7])'", esg_sections_js_source)
    frontend_keys = [f"R{i}" for i in frontend_ids]
    assert backend_keys == frontend_keys, (
        f"Backend/frontend ordering drift. Backend: {backend_keys}, Frontend: {frontend_keys}. "
        f"Both must follow FC v3 §14 canonical order R1..R7."
    )
