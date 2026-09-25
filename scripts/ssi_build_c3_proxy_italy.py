#!/usr/bin/env python3
"""Build Italy's C3 as a declared proxy, per region.

    python3 scripts/ssi_build_c3_proxy_italy.py "<path to arera_tiqe_2024_dso_raw.csv>"

WHY A PROXY AND NOT AN IMPUTATION
    doctrine/FINDING_C3_is_not_published_where_C1_C2_C4_are.md establishes that
    C3 is withheld in every jurisdiction that publishes C1, C2 and C4, for a
    structural reason. The OECD/JRC Handbook on Constructing Composite
    Indicators names three methods for missing data — case deletion, single
    imputation, multiple imputation — and renormalising a component's weights
    over its surviving metrics is none of them. It is implicit single
    imputation: it silently sets the absent metric to the weighted mean of the
    others, and the Handbook warns that single imputation "is known to
    underestimate the variance".

    For data that is unavailable rather than missing, the Handbook says
    something different, at page 24: "Proxy measures can be used when the
    desired data are unavailable."

    This is that proxy.

THE CONSTRUCTION
    France's C3 is the share of a département's customers falling outside the
    regulated continuity standard — distance from the standard. Italy has no
    such share, but it has both halves of the same construct natively:

        numerator    N1L, the measured annual count of unplanned long plus
                     short interruptions per BT user, per ambito territoriale.
                     ARERA comparative publication 2024.
        denominator  the regulated maximum for that ambito's concentration
                     class, TIQE (del. 617/2023 all. A) article 32:
                         alta  6, media  9, bassa 10
                     "interruzioni senza preavviso lunghe più brevi all'anno"

    The numerator's definition and the standard's are the same quantity —
    unplanned, long plus short — which is why the ratio means anything.

    Dividing by the class standard also removes the settlement-density effect
    the raw count carries: raw N1L medians run 1.93 / 2.66 / 3.91 across the
    three classes, and the ratios 0.322 / 0.296 / 0.391.

WHAT IT IS NOT, DECLARED
    - It is not a breach rate. France publishes a share of customers; this is
      a ratio of an average to a threshold. Same construct, different
      quantity.
    - The numerator is the BT-user average; article 32's standard governs MT
      users. The same network events drive both, so the ratio is a monotone
      proxy for breach propensity, but the customer classes differ and that
      is an approximation, not an identity.
    - It uses a mean, so it cannot see the tail that an exceedance count is
      made of.
    - It therefore carries an evidence tier below the measured metrics beside
      it and must never be published as a measurement.

UNIT
    The proxy is computed per ambito and aggregated, BT-user weighted, to
    region — because region is the finest unit it can reach in this fleet.
    Italy's records carry no `owner` (0 of 41,662) so the DSO is unknown, and
    no comune population, so the concentration class is unknown. Region is
    derivable from the NUTS-3 code the records do carry. 20 units.
"""
from __future__ import annotations
import csv, sys, os, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

STANDARD = {"Alta": 6, "Media": 9, "Bassa": 10}   # TIQE art. 32, 2024-2025
TIQE = "TIQE del. 617/2023 all. A art. 32"

SOURCE_GATE = {"rows": 91, "users": 36995573, "weighted_N1L": 3.6789}

NUTS2_TO_REGION = {
    "ITC1": "Piemonte", "ITC2": "Valle d'Aosta", "ITC3": "Liguria",
    "ITC4": "Lombardia", "ITF1": "Abruzzo", "ITF2": "Molise",
    "ITF3": "Campania", "ITF4": "Puglia", "ITF5": "Basilicata",
    "ITF6": "Calabria", "ITG1": "Sicilia", "ITG2": "Sardegna",
    "ITH1": "Trentino-Alto Adige", "ITH2": "Trentino-Alto Adige",
    "ITH3": "Veneto", "ITH4": "Friuli-Venezia Giulia",
    "ITH5": "Emilia-Romagna", "ITI1": "Toscana", "ITI2": "Umbria",
    "ITI3": "Marche", "ITI4": "Lazio",
}

def main(src):
    rows = list(csv.DictReader(open(src, encoding="utf-8")))
    bad = [r for r in rows if r["concentrazione"] not in STANDARD]
    if bad:
        print(f"✗ unknown concentration class: {sorted({r['concentrazione'] for r in bad})}", file=sys.stderr)
        return 1
    U = sum(float(r["utenti_bt"]) for r in rows)
    wN = sum(float(r["utenti_bt"]) * float(r["N1L"]) for r in rows) / U
    errs = []
    if len(rows) != SOURCE_GATE["rows"]: errs.append(f"{len(rows)} rows, expected {SOURCE_GATE['rows']}")
    if round(U) != SOURCE_GATE["users"]: errs.append(f"{U:.0f} users, expected {SOURCE_GATE['users']}")
    if abs(wN - SOURCE_GATE["weighted_N1L"]) > 5e-4: errs.append(f"weighted N1L {wN:.4f}, expected {SOURCE_GATE['weighted_N1L']}")
    if errs:
        for e in errs: print("✗ " + e, file=sys.stderr)
        return 1
    print(f"✓ source gate: {len(rows)} ambiti, {U:,.0f} BT users, weighted N1L {wN:.4f}")

    by_region = collections.defaultdict(lambda: [0.0, 0.0])
    for r in rows:
        u = float(r["utenti_bt"]); ratio = float(r["N1L"]) / STANDARD[r["concentrazione"]]
        g = by_region[r["regione"]]
        g[0] += u; g[1] += u * ratio
    nat = sum(g[1] for g in by_region.values()) / sum(g[0] for g in by_region.values())
    print(f"✓ BT-user-weighted national proxy {nat:.4f}")

    missing = set(NUTS2_TO_REGION.values()) - set(by_region)
    if missing:
        print(f"✗ regions in the NUTS map with no ARERA rows: {sorted(missing)}", file=sys.stderr)
        return 1
    print(f"✓ all {len(set(NUTS2_TO_REGION.values()))} mapped regions have ARERA rows")

    out = ROOT / "data" / "c_metrics" / "italy_c3_proxy.csv"
    cols = ["unit_key","unit_type","layer","year","C3_proxy_n1l_over_standard",
            "bt_users","n_ambiti","evidence","numerator","denominator","source_id"]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for reg in sorted(by_region):
            u, wsum = by_region[reg]
            w.writerow({"unit_key": reg, "unit_type": "region", "layer": 3,
                        "year": 2024, "C3_proxy_n1l_over_standard": round(wsum/u, 6),
                        "bt_users": int(round(u)),
                        "n_ambiti": sum(1 for r in rows if r["regione"] == reg),
                        "evidence": "PROXY — not a measurement",
                        "numerator": "N1L, unplanned long+short per BT user, ARERA 2024",
                        "denominator": f"{TIQE} class maximum (alta 6, media 9, bassa 10)",
                        "source_id": "ARERA-TIQE-2024 / TIQE-617-2023-ART32"})
        w.writerow({"unit_key": "IT", "unit_type": "national", "layer": 3, "year": 2024,
                    "C3_proxy_n1l_over_standard": round(nat, 6),
                    "bt_users": int(round(U)), "n_ambiti": len(rows),
                    "evidence": "PROXY — not a measurement",
                    "numerator": "N1L, unplanned long+short per BT user, ARERA 2024",
                    "denominator": f"{TIQE} class maximum (alta 6, media 9, bassa 10)",
                    "source_id": "ARERA-TIQE-2024 / TIQE-617-2023-ART32"})
    vals = [by_region[r][1]/by_region[r][0] for r in by_region]
    print(f"✓ wrote {out.relative_to(ROOT)} — 20 regions + national")
    print(f"  proxy min={min(vals):.4f} max={max(vals):.4f} spread={max(vals)/min(vals):.1f}x")
    worst = sorted(((by_region[r][1]/by_region[r][0], r) for r in by_region), reverse=True)[:4]
    best  = sorted(((by_region[r][1]/by_region[r][0], r) for r in by_region))[:3]
    print("  worst:", ", ".join(f"{r} {v:.3f}" for v,r in worst))
    print("  best: ", ", ".join(f"{r} {v:.3f}" for v,r in best))
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2: print(__doc__); sys.exit(2)
    sys.exit(main(sys.argv[1]))
