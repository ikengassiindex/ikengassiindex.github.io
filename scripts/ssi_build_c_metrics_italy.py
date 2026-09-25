#!/usr/bin/env python3
"""Build data/c_metrics/italy.csv — layer 4 of the C mosaic for Italy.

    python3 scripts/ssi_build_c_metrics_italy.py "<path to Rapporto annuale degli output 2025.pdf>"

SOURCE
    E-Distribuzione, "Rapporto Annuale degli Output – 30/06/2025", data year
    2024, published by the company from its own operational records under
    article 58 of ARERA deliberation 617/2023/R/eel. Three per-province
    tables, 104 provinces each, plus the company's own national total.

        b)  Durata media per utente delle interruzioni (lunghe) senza preavviso
        c)  Numero medio per utente delle interruzioni (lunghe e brevi) senza preavviso
        d)  Durata media per utente delle interruzioni con preavviso

    Each is given twice: "tutte le cause" and "altre cause". The difference is
    the exceptional-event contribution, which is the CEER definitional axis.

WHAT IT DOES NOT DO
    It does not type a value. Every number is parsed from the PDF and the
    parse is re-checked against the document's own three national totals
    before anything is written. It does not interpolate below the province.
    It does not invent a value for a province the company does not serve;
    those substations get no C from this layer.

ALIASES
    Four fleet province names differ in spelling from the company's table.
    Each is declared here explicitly and none is fuzzy-matched.
"""
from __future__ import annotations
import csv, json, re, sys, unicodedata, collections, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

ROW = re.compile(r"^([A-ZÀ-ÜÈÉÌÒÙ'’\.\- ]{3,40}?)\s+(\d{1,3}(?:\.\d{3})*,\d+)\s+(\d{1,3}(?:\.\d{3})*,\d+)\s*$")
HDR = re.compile(r"^([a-z])\)\s+")
NUM = re.compile(r"\d{1,3}(?:\.\d{3})*,\d+")

SECTIONS = {"b": "C1_unplanned_long_min", "c": "C2_unplanned_longshort_n", "d": "C4_planned_min"}
EXPECTED_TOTALS = {"b": (73.11, 44.84), "c": (5.502, 3.985), "d": (95.53, 90.71)}
EXPECTED_ROWS = 104

ALIAS = {
    "Forlì-Cesena":         "FORLI'",
    "Reggio nell’Emilia":   "REGGIO EMILIA",
    "Pesaro e Urbino":      "PESARO",
    "Verbano-Cusio-Ossola": "VERBANIA",
}

def it_num(s: str) -> float:
    return float(s.replace(".", "").replace(",", "."))

def norm(s: str) -> str:
    s = (s or "").replace("’", "'").replace("`", "'")
    s = s.replace("'", " ").replace("-", " ").replace("/", " ")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().upper()
    return re.sub(r"\s+", " ", s).strip()

class ParserUnavailable(RuntimeError):
    pass


def parse(pdf_path: str):
    try:
        import pdfplumber
    except ImportError as e:
        raise ParserUnavailable(
            "pdfplumber is not installed in this interpreter.\n"
            "  Install it with:   python3 -m pip install --user pdfplumber\n"
            "  Until then the committed data/c_metrics/italy.csv stands on its own\n"
            "  integrity check, which does not need the PDF: the national row must\n"
            "  carry the document's own totals 73.11/44.84, 5.502/3.985, 95.53/90.71."
        ) from e
    tables: dict[str, dict[str, tuple[float, float]]] = collections.defaultdict(dict)
    totals: dict[str, tuple[float, float]] = {}
    cur = None
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages[:10]:
            for ln in (page.extract_text() or "").split("\n"):
                ln = ln.strip()
                h = HDR.match(ln)
                if h:
                    cur = h.group(1)
                if ln.startswith("Totale e-distribuzione") and cur:
                    a, b = NUM.findall(ln)[:2]
                    totals[cur] = (it_num(a), it_num(b))
                    continue
                m = ROW.match(ln)
                if m and cur in SECTIONS:
                    tables[cur][m.group(1).strip()] = (it_num(m.group(2)), it_num(m.group(3)))
    return tables, totals

def check(tables, totals):
    """The parse must reproduce the document's own totals and row counts."""
    errs = []
    for k in SECTIONS:
        if len(tables.get(k, {})) != EXPECTED_ROWS:
            errs.append(f"section {k}: {len(tables.get(k, {}))} rows, expected {EXPECTED_ROWS}")
        if totals.get(k) != EXPECTED_TOTALS[k]:
            errs.append(f"section {k}: total {totals.get(k)}, expected {EXPECTED_TOTALS[k]}")
    sets = [set(tables[k]) for k in SECTIONS if k in tables]
    if len(sets) == 3 and not (sets[0] == sets[1] == sets[2]):
        errs.append("the three tables do not cover the same province set")
    return errs

def main(pdf_path):
    from scripts._ssi_data_shard_reader import load_ssi_data
    try:
        tables, totals = parse(pdf_path)
    except ParserUnavailable as e:
        print(f"⚠ re-parse skipped — {e}", file=sys.stderr)
        return 3
    errs = check(tables, totals)
    if errs:
        for e in errs:
            print("✗ " + e, file=sys.stderr)
        return 1
    print(f"✓ parse reproduces the document's own three national totals and {EXPECTED_ROWS} rows in each table")

    _, subs, _ = load_ssi_data("italy")
    by_prov = collections.defaultdict(lambda: {"n": 0, "nuts": collections.Counter()})
    for s in subs:
        p = s.get("region")
        by_prov[p]["n"] += 1
        by_prov[p]["nuts"][s.get("province")] += 1

    pdfmap = {norm(p): p for p in tables["b"]}
    rows, unmatched = [], []
    for fleet_name, info in sorted(by_prov.items(), key=lambda kv: -kv[1]["n"]):
        key = ALIAS.get(fleet_name) or pdfmap.get(norm(fleet_name))
        if key is None:
            unmatched.append((fleet_name, info["n"]))
            continue
        rows.append({
            "unit_key": fleet_name,
            "unit_key_in_source": key,
            "unit_type": "province",
            "nuts3": info["nuts"].most_common(1)[0][0],
            "layer": 4,
            "year": 2024,
            "C1_unplanned_long_min_all_causes":   f"{tables['b'][key][0]:.2f}",
            "C1_unplanned_long_min_other_causes": f"{tables['b'][key][1]:.2f}",
            "C2_unplanned_longshort_n_all_causes":   f"{tables['c'][key][0]:.3f}",
            "C2_unplanned_longshort_n_other_causes": f"{tables['c'][key][1]:.3f}",
            "C4_planned_min_all_causes":   f"{tables['d'][key][0]:.2f}",
            "C4_planned_min_other_causes": f"{tables['d'][key][1]:.2f}",
            "C3_mt_exceed_pct": "",
            "customers": "",
            "substations": info["n"],
            "match": "alias" if fleet_name in ALIAS else "exact",
            "source_id": "EDIST-RAO-2025-DY2024",
        })
    cols = list(rows[0].keys())
    out = ROOT / "data" / "c_metrics" / "italy.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)
        w.writerow({**{c: "" for c in cols},
                    "unit_key": "IT", "unit_key_in_source": "Totale e-distribuzione",
                    "unit_type": "national", "layer": 4, "year": 2024,
                    "C1_unplanned_long_min_all_causes": f"{totals['b'][0]:.2f}",
                    "C1_unplanned_long_min_other_causes": f"{totals['b'][1]:.2f}",
                    "C2_unplanned_longshort_n_all_causes": f"{totals['c'][0]:.3f}",
                    "C2_unplanned_longshort_n_other_causes": f"{totals['c'][1]:.3f}",
                    "C4_planned_min_all_causes": f"{totals['d'][0]:.2f}",
                    "C4_planned_min_other_causes": f"{totals['d'][1]:.2f}",
                    "substations": sum(r["substations"] for r in rows),
                    "match": "document total", "source_id": "EDIST-RAO-2025-DY2024"})
    covered = sum(r["substations"] for r in rows)
    total = len(subs)
    print(f"✓ wrote {out.relative_to(ROOT)} — {len(rows)} provinces + 1 national row")
    print(f"  fleet covered   {covered:,} of {total:,}  ({100*covered/total:.2f}%)")
    print(f"  no C from L4    {total-covered:,}  ({100*(total-covered)/total:.2f}%)")
    for name, n in sorted(unmatched, key=lambda x: -x[1]):
        print(f"      {str(name):<30}{n:>6,}")
    print(f"  source provinces unused: {len(set(tables['b']) - {r['unit_key_in_source'] for r in rows})}")
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    sys.exit(main(sys.argv[1]))
