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
' + ' and stripped of trailing prose after a comma, AND every document named in
the per-record `_metrics_source` string, must name a file that exists in the SSI
Index estate folder.

THE RECORD-LEVEL SURFACE WAS ADDED 17 SEPTEMBER 2026, AND IT MATTERED.
Until then this gate read the manifest only. The I4/I6 citation named in the
paragraph above was repaired in meta.metric_derivations and NOT in the records:
`_metrics_source` on 37 countries' substations still named
AMENDMENT_DRAFT_I4_definition.md, a file that exists nowhere. So this gate —
written for exactly that defect, and naming it in its own docstring — reported
"all 5 cited documents resolve" and exited 0 while the defect it was built for
sat live on the published records of 37 countries.

A gate that reads half the surface where a defect occurs will certify the half
it reads. The lesson is registered in
doctrine/DOCTRINE_a_check_must_read_the_artefact.md.

Exit 1 if any citation dangles.
"""
from __future__ import annotations
import json, os, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
# Cited documents live in the repository that holds the citing records, so a
# citation resolves inside one versioned unit and cannot change without a
# commit. Before 2026-09-03 this pointed at a OneDrive folder with no git: the
# gate proved a file EXISTED and could not prove it had not been edited since
# the record cited it. SSI_ESTATE still overrides, for checking a working copy
# elsewhere.
DOCTRINE = ROOT / "doctrine"
ESTATE = pathlib.Path(os.environ["SSI_ESTATE"]) if os.environ.get("SSI_ESTATE") \
    else DOCTRINE


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
        print("  expected doctrine/ in this repository; set SSI_ESTATE to override\n")
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

        # The RECORD-level citation. The manifest and the records can disagree,
        # and have: repairing one is not repairing the other. Sampled from the
        # head of the first shard rather than by parsing every record, because
        # the string is constant within a country and a full parse of 39 shards
        # is minutes of I/O for one value. Stated here so the sampling is not
        # mistaken for a census.
        # A country is sharded or it is not, and only 6 of 39 are. A first
        # version of this read `substations_shards` alone and so never looked
        # at 33 countries' records at all, reporting 6 dangling where 37 dangle
        # — the same unsharded-fallback blind spot that silenced a conformance
        # check earlier the same day.
        shards = d.get("substations_shards") or []
        targets = [man.parent / sh.get("path", "") for sh in shards[:1]] or [man]
        for shard in targets:
            if not shard.exists():
                continue
            with shard.open(encoding="utf-8", errors="replace") as fh:
                head = fh.read(262144)
            m = re.search(r'"_metrics_source"\s*:\s*"([^"]*)"', head)
            # D-14 OPTION B, 3 OCTOBER 2026 — FOLLOW THE POINTER.
            # The record's _metrics_source is being normalised to a provenance
            # code plus the ids of the metrics that record carries, with the
            # fleet statement moved VERBATIM to the manifest's
            # meta._metrics_source. The code form names NO FILE, so the findall
            # below would return nothing and this gate would not fail -- it would
            # SILENTLY STOP CHECKING THAT JURISDICTION. A gate quietly covering
            # one fewer fleet is worse than a gate that fails, so the manifest's
            # statement is scanned alongside the record's.
            texts = [m.group(1)] if m else []
            meta_stmt = (d.get("meta") or {}).get("_metrics_source")
            if isinstance(meta_stmt, str) and meta_stmt:
                texts.append(meta_stmt)
            if not texts:
                continue
            for doc in re.findall(r"[A-Za-z0-9_.\-]+\.(?:md|html|yaml|json)",
                                  " ".join(texts)):
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
