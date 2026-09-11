#!/usr/bin/env python3
"""
Measure what a published substation record costs, field by field, and who
actually reads each field.

    python3 scripts/measure_record_field_weight.py
    python3 scripts/measure_record_field_weight.py --shard uk/ssi-data-substations-01.json

WHY

    A visit to the France country page fetches eleven files, 524 MB raw, about
    57 MB over the wire after gzip. Before anyone proposes shrinking that, the
    question is which bytes are there for the browser and which are there for
    the estate.

    This answers it three ways, because the first two are not sufficient on
    their own and the third is the one that matters.

WHAT IT MEASURES

    A. WEIGHT. Serialised bytes per top-level key, per record, as a share of
       the whole. This says where the mass is.

    B. DISPLAY REFERENCES. Whether each key's name appears anywhere in the
       served JS and HTML. A key no served code names cannot be on the page.

    C. PIPELINE REFERENCES. Whether each key is read by the estate's own
       Python and workflows. THIS IS THE ONE THAT PREVENTS THE ACCIDENT.
       A field unused by the renderer is not a dead field: it may be an input
       to a validator, a derivation or an ingestion merge. Measured on
       11 September 2026, 21 of the 28 display-unused keys were read by
       non-served code - `operator` by 42 consumers, `osm_type` by 68,
       `P_critical` by 34.

    D. DYNAMIC ACCESS. Whether any served code enumerates a record's keys -
       Object.keys, for..in, spread, JSON.stringify of a whole record. If it
       does, B is worthless: a field could reach the page without ever being
       named, and any split would break the page silently. Measured: none.

WHAT IT DOES NOT DO

    It does not propose removing anything, and no conclusion of the form
    "this field is safe to delete" follows from B alone. The only safe shape
    is additive: the full record stays canonical and a DERIVED slim view is
    what the browser fetches. See doctrine/FINDING_delivery_and_payload.md.

    Section B's matching is deliberately loose - a bare name search - because
    a false "referenced" is harmless and a false "unreferenced" is not. Read
    its output as a lower bound on what display needs.
"""
from __future__ import annotations
import argparse, collections, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

DYNAMIC = {
    r"Object\.keys\s*\(\s*(sub|s|d|rec|substation)\b": "Object.keys over a record",
    r"for\s*\(\s*(var|let|const)\s+\w+\s+in\s+(sub|s|rec|substation)\b": "for..in over a record",
    r"JSON\.stringify\s*\(\s*(sub|s|rec|substation)\b": "stringify a whole record",
    r"\.\.\.(sub|s|rec|substation)\b": "spread a whole record",
    r"Object\.entries\s*\(\s*(sub|s|rec|substation)\b": "Object.entries over a record",
}


def served_blob():
    files = list(ROOT.glob("*.js")) + list(ROOT.glob("*.html"))
    for d in ("assets", "js"):
        if (ROOT / d).exists():
            files += list((ROOT / d).glob("*.js"))
    for extra in ("uk/esg-report.html", "uk/intelligence.html", "uk/index.html"):
        if (ROOT / extra).exists():
            files.append(ROOT / extra)
    return files, "\n".join(p.read_text(errors="replace") for p in files)


def pipeline_files():
    out = []
    for pat in ("scripts/**/*.py", "*.py", ".github/workflows/*.yml"):
        out += list(ROOT.glob(pat))
    return [p for p in out if ".cache" not in str(p)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", default="uk/ssi-data-substations-01.json")
    ap.add_argument("--records", type=int, default=4000)
    a = ap.parse_args()

    p = ROOT / a.shard
    if not p.exists():
        sys.exit(f"no {a.shard}")
    raw = json.loads(p.read_text())
    subs = raw if isinstance(raw, list) else raw.get("substations", [])
    n = min(a.records, len(subs))

    w = collections.Counter()
    total = 0
    for s in subs[:n]:
        for k, v in s.items():
            b = len(json.dumps(v, separators=(",", ":"))) + len(k) + 3
            w[k] += b
            total += b

    sfiles, blob = served_blob()
    pfiles = pipeline_files()
    ptexts = []
    for q in pfiles:
        try:
            ptexts.append((q.name, q.read_text(errors="replace")))
        except Exception:
            pass

    print(f"\n  {p.name}  {len(subs):,} records, {p.stat().st_size/1048576:.1f} MB")
    print(f"  sampled {n:,} records · {len(sfiles)} served files · "
          f"{len(ptexts)} pipeline consumers")
    print(f"  {total/n:.0f} bytes per record\n")
    print(f"  {'key':<30}{'B/rec':>7}{'share':>8}{'display':>9}{'pipeline':>10}")

    disp_only = pipe_only = neither = 0.0
    for k, b in w.most_common():
        pc = 100 * b / total
        d = re.search(r"[\"'\.\[]" + re.escape(k) + r"[\"'\]\b]?", blob) is not None
        np_ = sum(1 for _, t in ptexts if re.search(r"[\"']" + re.escape(k) + r"[\"']", t))
        if not d and np_ == 0:
            neither += pc
        elif not d:
            pipe_only += pc
        print(f"  {k:<30}{b/n:>7.0f}{pc:>7.1f}%{('yes' if d else '—'):>9}{np_:>10}")

    print(f"\n  share used by the page            {100-pipe_only-neither:>6.1f}%")
    print(f"  share NOT on the page but read")
    print(f"    by the estate's own pipeline    {pipe_only:>6.1f}%   <- NOT removable")
    print(f"  share read by neither             {neither:>6.1f}%   <- still published "
          f"data; removal is an editorial decision, not a cleanup")

    print(f"\n  DYNAMIC ACCESS IN SERVED CODE")
    found = False
    for rx, label in DYNAMIC.items():
        for m in re.finditer(rx, blob):
            found = True
            print(f"    HIT  {label}: {blob[m.start():m.start()+70]!r}")
    if not found:
        print(f"    none — no served code enumerates a record's keys, so the")
        print(f"    display column above is meaningful. If this ever reports a")
        print(f"    hit, the display column becomes worthless and no split is")
        print(f"    safe without reading that code first.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
