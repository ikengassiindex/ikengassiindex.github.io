#!/usr/bin/env python3
"""
Every document the register cites must exist.

    python3 scripts/check_provenance_citations_resolve.py

WHY THIS EXISTS
---------------
On 30 August 2026 the I5 derivation stamped

    "amendment": "AMENDMENT_I5_thermal_stress_C57_91.md"

into 620,129 substations' metric_derivations. The filename was a constant in
the derivation script. The document did not exist and was not written for
another day. Separately, the I4/I6 derivation cited
AMENDMENT_DRAFT_I4_definition.md while the file on disk was named
AMENDMENT_DRAFT_I4_I6_definition.md — 45 entries across 37 countries pointing
one character wrong.

Both are the same defect: a provenance pointer to nothing. A record that cites
a document nobody can open is not better evidenced than a record that cites
none — it is worse, because it reads as evidenced.

Nothing else checks this. The gates verify that values derive, that intervals
cohere, that published counts match the register. None of them asks whether the
paper trail resolves.

WHAT IT CHECKS
--------------
Every `amendment` and `decision` string in every country's
meta.metric_derivations, split on
' + ' and stripped of trailing prose after a comma, must name a file that
exists in the SSI Index estate folder.

Exit 1 if any citation dangles.
"""
from __future__ import annotations
import json, os, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ESTATE = pathlib.Path(os.environ.get(
    "SSI_ESTATE",
    pathlib.Path.home() / "Library/CloudStorage/OneDrive-IkengaSL"
    / "Internal - IKENGA EU - Documents/0.22. IP agenda/SSI Index"))


def cited_documents(text):
    """Filenames named in an amendment string."""
    out = []
    for part in str(text).split(" + "):
        part = part.split(",")[0].strip()
        for m in re.finditer(r"[A-Za-z0-9_.\-]+\.(?:md|html|yaml|json)", part):
            out.append(m.group(0))
    return out


def main():
    if not ESTATE.exists():
        print(f"\n  estate folder not found: {ESTATE}")
        print("  set SSI_ESTATE to the SSI Index folder path\n")
        return 2

    present = {p.name for p in ESTATE.rglob("*") if p.is_file()}
    seen, dangling = {}, {}
    for man in sorted(ROOT.glob("*/ssi-data.json")):
        try:
            d = json.loads(man.read_text())
        except Exception:
            continue
        country = man.parent.name
        for e in (d.get("meta") or {}).get("metric_derivations") or []:
            # `decision` joined `amendment` as a citation key on 31 August
            # 2026 with the I3 Method C registration. A new citation key that
            # this gate does not read is an ungated citation, which is the
            # condition this gate exists to prevent.
            for key in ("amendment", "decision"):
                for doc in cited_documents(e.get(key, "")):
                    seen.setdefault(doc, set()).add(country)
                    if doc not in present:
                        dangling.setdefault(doc, set()).add(country)

    print("\n  provenance citations — does every cited document exist?\n")
    for doc in sorted(seen):
        mark = "MISSING" if doc in dangling else "ok"
        print(f"    {mark:>8}  {doc}  ({len(seen[doc])} countries)")
    if dangling:
        print(f"\n    {len(dangling)} DANGLING CITATION(S). A record citing a "
              f"document nobody can open reads as evidenced and is not.\n")
        return 1
    print(f"\n    all {len(seen)} cited documents resolve\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
