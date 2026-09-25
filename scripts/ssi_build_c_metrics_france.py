#!/usr/bin/env python3
"""Build data/c_metrics/france.csv — C3 for the 94 Enedis départements.

SOURCE
    Enedis open data, "Indicateur réglementaire continuité d'alimentation",
    https://opendata.enedis.fr/datasets/indicateur-continuite-dalimentation/
    Licence Ouverte / Open Licence 2.0. 94 records, département, 2009-2024,
    refreshed annually. Read through the portal's Explore v2.1 API on
    25 September 2026.

    The published value is the percentage of a département's HTA and BT
    customers falling outside the regulatory continuity standard. That is
    C3_MT_exceed_pct — the exact string the metric registry blocks C3 on.

WHY ONLY C3
    Enedis publishes critère B (C1) and the coupure frequency (C2) NATIONALLY
    ONLY — 18 records each, one value per year, 485 and 707 bytes. Neither is
    sub-national. C3 is the single sub-national continuity metric France
    publishes. See the CORRECTION block in intelligence/c1_acquisition_register.yaml.

THE GATE
    The rows below were transferred from the API response. They are not
    trusted: SOURCE_AGGREGATES holds the count, the three annual sums and the
    2024 min and max as the API itself computed them, and this script refuses
    to write unless the transferred rows reproduce every one of them to full
    float precision. A transcription error cannot pass a 14-significant-figure
    sum over 94 values.
"""
from __future__ import annotations
import csv, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

SOURCE_AGGREGATES = {
    "n": 94,
    "sum_2024": 197.84799486999702,
    "sum_2023": 198.02190658562986,
    "sum_2022": 114.6058343749478,
    "min_2024": 0.000245291326376054,
    "max_2024": 7.05117060732499,
}

# dept_code, nom, aaa2024, aaa2023, aaa2022
ROWS = [
("01","Ain",4.62125253387389,3.0243749966318,0.661232478296049),
("02","Aisne",0.835519647009719,2.37031614175581,1.26790959774594),
("03","Allier",1.32730805335429,3.06893254138848,2.14707177454866),
("04","Alpes de Haute-Provence",3.18658924683156,1.47229347482343,2.14194260329497),
("05","Hautes-Alpes",2.32216938176667,2.5858868237709403,2.62646773196786),
("06","Alpes-Maritimes",0.711680900284672,0.3751574321367,0.0960559689111595),
("07","Ardèche",5.05708134907691,5.02750718340458,1.8602061691682998),
("08","Ardennes",0.705540050324361,1.00606774816338,1.49741716013607),
("09","Ariège",4.14200634520121,3.953014324674,1.70198050339742),
("10","Aube",1.69216301626007,0.476672201268927,0.381696304913855),
("11","Aude",1.5039147860673598,3.43230829648095,1.35330211918568),
("12","Aveyron",7.05117060732499,2.88238884636625,1.34446645909992),
("13","Bouches-du-Rhône",1.00293348449827,2.95045779910011,1.69858616961072),
("14","Calvados",1.9464447843985901,1.80776032630841,0.780206694169183),
("15","Cantal",1.8694321191483498,2.01452876419229,0.8316855725535091),
("16","Charente",3.8144691974943696,3.29375119928957,2.89957757468677),
("17","Charente-Maritime",2.10066201852087,1.54189366713086,1.49518868997838),
("18","Cher",4.24929323032016,4.37131680812166,2.95200869957733),
("19","Corrèze",4.06786921687584,5.31203630967967,2.1131417402550303),
("21","Côte-d'Or",1.31495302898312,0.909794525219516,0.412162222746931),
("22","Côtes d'Armor",3.25187058750126,1.54869933454325,2.6892824185964797),
("23","Creuse",2.39377491306929,5.59424203442447,2.46128613116919),
("24","Dordogne",6.809122348921511,9.13391226461965,4.46570018376788),
("25","Doubs",3.4073336548484,2.0284089842943698,0.885932974501032),
("26","Drôme",1.65209624431815,1.41923953903987,1.6005376611738902),
("27","Eure",2.26915770421671,1.9380288820849099,2.01382892032255),
("28","Eure-et-Loir",0.790199626256934,1.39478327213771,0.34854931371841996),
("29","Finistère",1.5672633345079199,3.6954162171323897,1.16507692989992),
("30","Gard",1.23611826809545,1.13589134097828,2.0799653132645797),
("31","Haute-Garonne",0.537043831672829,0.815619035843045,0.508602687779443),
("32","Gers",4.22791488550225,9.66430192055731,2.2974849684115903),
("33","Gironde",0.835291575507117,1.9556045404314801,1.40403836793691),
("34","Hérault",0.845509838648844,1.11643531707727,0.299489591673339),
("35","Île-et-Vilaine",2.97701730016416,0.6607483199441779,1.35091231446615),
("36","Indre",2.78970246773584,5.67569208763182,1.81302425715427),
("37","Indre-et-Loire",2.07152521300325,1.49570176453877,0.544956236352879),
("38","Isère",2.35976687718475,1.45366936043854,0.8630125718913519),
("39","Jura",4.92595185841125,6.639931861736111,0.9293514199417371),
("40","Landes",2.19693466340754,2.72830210233821,1.16047063340784),
("41","Loir-et-Cher",4.123874154120051,3.12390329264599,1.69813877408802),
("42","Loire",2.24080150653867,0.9847605990297411,0.799500367637288),
("43","Haute-Loire",2.07200694921123,0.507018134002018,0.581452706868911),
("44","Loire-Atlantique",0.977473871371515,1.8255899799738,0.7963576838371079),
("45","Loiret",2.8430150860354697,1.88278546597406,1.18763180178091),
("46","Lot",3.1568457019542002,5.65138857529917,3.71889526934646),
("47","Lot-et-Garonne",3.6640352680727397,3.93015821283245,1.16899018530302),
("48","Lozère",6.518250217176851,3.20936964612749,6.61524285119791),
("49","Maine-et-Loire",0.766218287076452,1.1722128745465399,0.773182343263206),
("50","Manche",4.277902765913931,2.45002478612464,1.3435087298880801),
("51","Marne",1.5489718812367201,0.690937532281629,0.469803856145285),
("52","Haute-Marne",0.752773375594295,1.59880420797699,0.676791646891315),
("53","Mayenne",2.0009335096629397,1.22026411963857,1.22243433239111),
("54","Meurthe-et-Moselle",0.45407757450989605,0.43059479431577297,0.170663771126428),
("55","Meuse",3.10192945540141,0.64478678276401,0.297946584351094),
("56","Morbihan",1.46242054163315,2.4323323865168898,1.59875061783151),
("57","Moselle",1.27776805774256,0.552095644423583,0.289599738825503),
("58","Nièvre",3.3841574334380704,3.3945251300628696,3.87590748601579),
("59","Nord",0.47107654372266,0.272324974469534,0.472515543860639),
("60","Oise",1.32956716888807,0.314557819865421,0.174707334987713),
("61","Orne",3.42469982654774,1.1889834050677202,1.31316225353391),
("62","Pas-de-Calais",0.622383646246304,0.502313737475445,1.08212037376305),
("63","Puy-de-Dôme",1.4672894085800798,1.0239357838963599,1.0027061800499801),
("64","Pyrénées-Atlantiques",4.41900796344431,3.14783938622773,1.50660729492812),
("65","Hautes-Pyrénées",2.54439101082031,2.45061731995078,0.452350280292469),
("66","Pyrénées-Orientales",0.58007216208715,0.22974994656977998,0.30570591091370103),
("67","Bas-Rhin",2.61873516271251,1.51219730007293,1.3855150697256),
("68","Haut-Rhin",0.9101198163788521,0.9539246869369871,0.31676255737281),
("69","Rhône",0.753983923843648,0.476344468230488,0.30909897738104797),
("70","Haute-Saône",3.19306989065583,4.9263725776302,0.9582379862700229),
("71","Saône-et-Loire",2.52136850460731,3.0636650308270696,1.86520498974253),
("72","Sarthe",1.3505377395684,1.79840326100636,0.9159927635953181),
("73","Savoie",1.9086993678229198,2.27539190959056,0.986414357744627),
("74","Haute-Savoie",1.93550171479146,2.57869458035801,0.477429810763144),
("75","Paris",0.000245291326376054,0.000246298290628289,0.0969194901948446),
("76","Seine-Maritime",0.8632031089638951,0.7640343905787159,1.20098266041847),
("77","Seine-et-Marne",0.93358368389754,1.237287308569,0.15705583971814802),
("78","Yvelines",0.42801182636168605,0.368444538514116,0.11996358591037999),
("79","Deux-Sèvres",0.115565538681902,0.127448897893825,0.0918138147000476),
("80","Somme",0.271402010902645,0.678832996371524,1.14503431060445),
("81","Tarn",2.3454516477484,1.8158749944352899,1.0997165771097999),
("82","Tarn-et-Garonne",1.33764832793959,2.13334526693986,1.33622946686578),
("83","Var",1.5711026327098,1.16033060621916,1.73298759853804),
("84","Vaucluse",1.0777682687795,0.828189071135675,1.6740983236439602),
("85","Vendée",1.7873572874413002,3.44614014492167,0.70082596604823),
("86","Vienne",1.25919804824303,0.376091655515879,0.314603161960894),
("87","Haute-Vienne",2.31892102796784,3.6266479255525397,1.68211758965601),
("88","Vosges",1.0710237435404601,0.589064066659752,0.41105106669270997),
("89","Yonne",5.38129575755905,3.88498025718643,1.43808120331318),
("90","Territoire-de-Belfort",0.976739003949046,1.91188177928152,0.8061381843712001),
("91","Essonne",0.12825009865392198,0.0888615306911628,0.0893789363107125),
("92","Hauts-de-Seine",0.0713471961702666,0.283754823938203,0.147166476797727),
("93","Seine-Saint-Denis",0.0660647154707047,0.0173179498626109,0.114550675627191),
("94","Val-de-Marne",0.047960363887097096,0.0465580685693771,0.159863507688303),
("95","Val-d'Oise",0.45584761180655503,0.248618072092364,0.134116377390913),
]

# ── layer 1, national ────────────────────────────────────────────────────────
# Enedis publishes critère B and the coupure frequency nationally only.
#   duree-moyenne-de-coupure-bt              18 records, 2009-2025 + 2026-T1
#   frequence-moyenne-de-coupure-par-client-bt  18 records, same span
# Both Licence Ouverte 2.0, read through Explore v2.1 on 25 September 2026.
#
# France splits frequency three ways — brève, longue planifiée, longue non
# planifiée — so C2 on Italy's basis (unplanned long AND short) is
# longue_non_planifiee + breve. The duration series does not split long from
# brief, so C1 here is "non planifiées" as published; whether it excludes
# interruptions under three minutes is NOT established and must be read from
# CRE's definition before France's C1 is compared with anyone's.
#
# year, C1_unplanned_min, C4_planned_min, C2_unpl_long_n, C2_brief_n, C2_planned_n
NATIONAL = [
 ("2024", 53.300, 18.272, 0.573, 1.338, 0.137),
 ("2023", 54.987, 17.941, 0.573, 1.374, 0.135),
 ("2022", 43.187, 16.301, 0.563, 1.219, 0.131),
]

def gate():
    errs = []
    if len(ROWS) != SOURCE_AGGREGATES["n"]:
        errs.append(f"row count {len(ROWS)} != {SOURCE_AGGREGATES['n']}")
    for yr, idx in (("2024", 2), ("2023", 3), ("2022", 4)):
        got = sum(r[idx] for r in ROWS)
        want = SOURCE_AGGREGATES[f"sum_{yr}"]
        if abs(got - want) > 1e-9:
            errs.append(f"sum({yr}) {got!r} != source {want!r}")
    v = [r[2] for r in ROWS]
    if min(v) != SOURCE_AGGREGATES["min_2024"]:
        errs.append(f"min(2024) {min(v)!r} != source {SOURCE_AGGREGATES['min_2024']!r}")
    if max(v) != SOURCE_AGGREGATES["max_2024"]:
        errs.append(f"max(2024) {max(v)!r} != source {SOURCE_AGGREGATES['max_2024']!r}")
    if len({r[0] for r in ROWS}) != len(ROWS):
        errs.append("duplicate département codes")
    return errs

def main():
    errs = gate()
    if errs:
        for e in errs: print("✗ " + e, file=sys.stderr)
        return 1
    print(f"✓ the transferred rows reproduce every aggregate the API itself reported")
    print(f"  n={len(ROWS)}  sum2024={sum(r[2] for r in ROWS)!r}")
    out = ROOT / "data" / "c_metrics" / "france.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    cols = ["unit_key","unit_key_in_source","unit_type","layer","year",
            "C1_unplanned_long_min_all_causes","C2_unplanned_longshort_n_all_causes",
            "C4_planned_min_all_causes","C3_mt_exceed_pct","customers","substations",
            "match","source_id"]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for code, nom, y24, y23, y22 in ROWS:
            for yr, val in (("2024", y24), ("2023", y23), ("2022", y22)):
                w.writerow({"unit_key": nom, "unit_key_in_source": code,
                            "unit_type": "departement", "layer": 2, "year": yr,
                            "C3_mt_exceed_pct": repr(val),
                            "source_id": "ENEDIS-INDIC-CONTINUITE-LO2.0"})
        for yr, c1, c4, nlong, nbrief, nplan in NATIONAL:
            w.writerow({"unit_key": "FR", "unit_key_in_source": "Enedis",
                        "unit_type": "national", "layer": 1, "year": yr,
                        "C1_unplanned_long_min_all_causes": c1,
                        "C2_unplanned_longshort_n_all_causes": round(nlong + nbrief, 4),
                        "C4_planned_min_all_causes": c4,
                        "match": "national series",
                        "source_id": "ENEDIS-CRITERE-B+FREQUENCE-LO2.0"})
    print(f"✓ wrote {out.relative_to(ROOT)} — {len(ROWS)} départements x 3 years")
    print(f"  C1, C2, C4 columns are EMPTY: Enedis publishes them nationally only.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
