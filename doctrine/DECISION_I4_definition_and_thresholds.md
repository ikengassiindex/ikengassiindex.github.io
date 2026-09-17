# Decision paper — I4: definition, thresholds, and what the filter actually buys

**For operator signature.** Closes the two drafts of 30 August 2026,
`AMENDMENT_DRAFT_I4_I6_definition.md` and
`AMENDMENT_DRAFT_I4_transmission_thresholds.md`, both of which state in their own
headers that nothing has been written to the register.

**Date:** 17 September 2026.
**Status of the code:** I4 is DERIVED AND ON RECORDS ALREADY, at 100 per cent of
622,104 substations, under those two unsigned drafts. This paper exists because
that is the wrong order and the order cannot now be reversed, only regularised.

---

## 0. First, what is and is not at stake

Measured on Poland, 17 September 2026:

| layer | present on |
|---|---:|
| `metrics.I1`–`I6`, `_I_from_metrics` | **100%** (27,764 of 27,764) |
| `components.I`, `R_base` | **8.1%** (2,247) |

`components.I` is **never** equal to `_I_from_metrics` — 0 of 2,247 records, with
the two differing by more than 0.10 on 76 per cent and ranging −0.58 to +0.75.
`components.I` is still the `enrich_esg_gaps` fill.

**So the drafts' §5 condition held.** I4 reaches no published R score. Whatever is
decided here changes the metric layer and nothing a reader of the index sees
today. That lowers the urgency and it does not lower the obligation: the metric
layer is published, and it is published citing documents that say they are
unsigned.

---

## 1. DECISION ONE — definition A or definition B

The drafts set out two ways to compute density at a substation:

- **A — local.** Line-km within a 3×3 block of 0.1° cells, about 33 km across.
  Varies per substation.
- **B — regional.** A NUTS-3 statistic per 1,000 km², joined to every substation
  in the region. Constant within a region.

The 30 August draft measured these on France and found Spearman rank correlation
0.7038 for I4 and 0.6743 for I6 — about a third of the fleet ordering differs.

**New measurement, 17 September 2026, three countries.** Decomposing the variance
of definition A into between-region and within-region components. B keeps only
the between-region part by construction; the within-region part is what B throws
away.

| country | substations | regions | variance B KEEPS | variance B DESTROYS |
|---|---:|---:|---:|---:|
| Poland | 27,764 | 74 | 58.8% | **41.2%** |
| France | 168,894 | 102 | 59.2% | **40.8%** |
| Spain | 12,438 | 66 | 45.2% | **54.8%** |

**Recommendation: A.** B discards between two-fifths and more than half of the
discriminating signal, consistently across three different grid geometries. The
construct's own rationale for inverting this metric — "higher density = better
resilience" — describes local network redundancy, which is what A measures and
what B averages away. A also uses geometry already held rather than discarding it.

This is the same recommendation the 30 August draft made. It is now measured on
three countries rather than argued from one.

---

## 2. DECISION TWO — the per-country voltage threshold

The 30 August draft was explicit that its proposed column was **not measured**:
*"it is my reading of where each TSO's transmission tier begins… Treat it as a
starting point for your pin, not as a finding."*

That warning was warranted. Thirteen of the 39 have now been checked against
named primary sources. **Five of the thirteen need to change, and one country
cannot take a threshold at all.**

| country | draft | **pinned** | verdict and authority |
|---|---:|---:|---|
| france | 63 | **63** | CONFIRMED — RTE *Bilan électrique*, "63 kV à 400 kV", 105,817 km |
| germany | 220 | **220** | CONFIRMED — Bundesnetzagentur/SMARD, transmission "at least 220 kilovolts" |
| spain | 220 | **220** | CONFIRMED peninsula — Ley 24/2013 Art. 34, transporte secundario ≥220 kV |
| poland | 220 | **220** | CONFIRMED — PSE, 400 kV 9,624 km + 220 kV 6,896 km |
| ireland | 110 | **110** | CONFIRMED — EirGrid, "operated at 400 kV, 220 kV and 110 kV" |
| turkey | 154 | **154** | CONFIRMED operationally — TEİAŞ *Stratejik Planı*, "154 kV ve 400 kV" |
| iceland | 132 | **132** | CONFIRMED as backbone — Landsnet *meginflutningskerfi* |
| italy | 132 | **120** | ⚠ CHANGE — Terna's own tier is "150-132-120 kV" |
| mexico | 230 | **69** | ⚠ CHANGE — CENACE, "tensiones iguales o mayores a 69 kV" |
| luxembourg | 150 | **220** | ⚠ CHANGE — ILR: 65 kV is *distribution*, not transport |
| us | 115 | **100** | ⚠ CHANGE — NERC BES, FERC Order No. 773 |
| uk | 275 | **split** | ⚠ CHANGE — statutory and territorial; see §2.2 |
| greenland | 60 | **none** | ⚠ NOT APPLICABLE; see §2.3 |

### 2.1 The four straightforward corrections

**Italy → 120.** Terna's reporting category is literally "150-120 kV appartenenti
alla RTN", 45,343 km, plus a further 3,550 km of RTN lines *below* 120 kV. A
132 kV cut excludes the 120 kV RTN tier. Terna's RTN perimeter is in any case
fixed by ministerial asset list (DM 25 giugno 1999), not by voltage, so any kV
threshold for Italy is an approximation — 120 is the tightest one available.

**Mexico → 69.** This is the largest single error in the draft. "Subtransmisión"
is not a legal category in Mexico: CENACE places the 69–138 kV tier *inside* the
Red Nacional de Transmisión, as "Transmisión 69 a 138 kV", 54,437 km against
56,409 km for the 161–400 kV tier. **A 230 kV threshold discards about 49 per
cent of Mexico's legally defined transmission network by length.** Note the
boundary is administrative, not statutory: the Ley de la Industria Eléctrica
states no voltage at all.

**Luxembourg → 220.** The trap is that 65 kV is high voltage but is regulated as
distribution. ILR's tariff classes are THT 220 kV (transport); HT 65 kV, MT
20 kV, BT 400 V (distribution). The draft's 150 kV admits almost nothing —
measured, 195 km survives a 220 kV cut against ILR's published 590 km of
transport, and Creos is simultaneously the sole TSO and dominant DSO, so
ownership does not disambiguate. Note also that 380 kV enters service around
2027 and this pin will need revisiting.

**United States → 100.** The draft's 115 kV has no federal basis. The defensible
figure is the NERC Bulk Electric System bright line, *"all Transmission Elements
operated at 100 kV or higher"*, approved by FERC Order No. 773 (20 December
2012) and mandatory. Two caveats must travel with it: exclusion E1 removes
radial groups above 100 kV, so ≥100 kV overstates the BES; and FERC's own
jurisdictional test is the seven-factor functional test from Order No. 888, which
contains no voltage number at all. The widely repeated "69 kV is transmission"
convention appears only in trade sources and **must not be used as a coefficient.**

### 2.2 The United Kingdom cannot take one threshold

This is statutory, not conventional. **Energy Act 2004, section 180** defines a
high voltage line as, for Scotland and relevant offshore lines, *"a nominal
voltage of 132 kilovolts or more"*, and for England and Wales, *"more than 132
kilovolts"*. The distinction is carried by the words "or more" against "more
than".

| area | threshold | operator's stated levels |
|---|---|---|
| Scotland (SPT, SHET) | **≥132 kV** | SPT 400/275/132; SHET 132/220/275/400 |
| England & Wales | **>132 kV** | NGET 400 and 275 kV |
| GB offshore | **≥132 kV** | per s.180 |
| Northern Ireland | **≥110 kV** | NIE 275 and 110 kV; no 400, no 220 |

The draft's single 275 kV excludes Scottish transmission entirely. Measured, the
difference is large: 14,619 km survives a 275 kV cut against 36,724 km at 132 kV.

**Recommendation:** pin 132 kV for the UK as a whole and declare the England and
Wales over-capture, OR split the country. The estate keys on country, so a split
is a schema change; 132 with a declared over-capture is the lighter path and I
recommend it, but it is an over-capture and must be named as one.

### 2.3 Greenland has no transmission network

There is no national or regional interconnected grid — approximately 69 to 70
independent stand-alone settlement systems, ranging from 30 kW to 45 MW. There is
no TSO, no grid code, and no transmission/distribution regulatory boundary,
because there is nothing to distinguish. The only interconnection of any kind is
Qaqortoq and Narsaq sharing one hydro plant.

Danish-language government documents do call the 56.7 km 132 kV Buksefjord line a
*transmissionsledning*, so the word is findable — but it denotes a single radial
generator lead-in to Nuuk, not a network.

**Recommendation: I4 is NOT APPLICABLE for Greenland and must be declared ABSENT,
not zero.** The draft's proposed 60 kV would be a fabricated coefficient. This is
the same discipline already applied to the 108,550 substations outside the CERRA
domain, which carry no I2 rather than an estimate.

### 2.4 Twenty-six countries remain unsourced

Checked against named authorities: france, germany, spain, italy, poland, turkey,
uk, us, ireland, luxembourg, iceland, mexico, greenland — **13 of 39**.

Not yet checked: australia, austria, belgium, canada, chile, colombia,
costa-rica, czechia, denmark, estonia, finland, greece, hungary, israel, japan,
korea, latvia, lithuania, netherlands, new-zealand, norway, portugal, slovakia,
slovenia, sweden, switzerland — **26 of 39**, carrying the draft's unverified
reading.

Given that checking 13 found 5 errors and 1 non-applicable case, **the expected
error count in the remaining 26 is not small.** Pin 14 says a coefficient must be
verified against a primary or secondary source. Signing all 39 today would sign
26 unverified numbers.

**Recommendation: sign 13 now, and hold the 26 pending the same check.** I4 can
be derived for the signed 13 and declared ABSENT for the rest, exactly as I2 is
ABSENT outside the CERRA domain. A partial metric honestly bounded is worth more
than a complete one with 26 unexamined coefficients in it.

---

## 3. What the voltage filter actually buys

The drafts promised that a voltage filter "would make it RTN density in fact and
not by proxy." **It does not.** Measured 17 September 2026 against each TSO's own
published transmission length:

| country | OSM total km | ÷ TSO published | after threshold | ÷ TSO published |
|---|---:|---:|---:|---:|
| poland | 119,363 | 7.23× | 16,338 | **0.99×** |
| france | 295,431 | 2.79× | 130,212 | **1.23×** |
| italy | 143,348 | 2.02× | 94,345 | **1.33×** |
| turkey | 103,569 | 1.39× | 54,942 | **0.74×** |
| mexico | 166,254 | 1.50× | 163,604 | **1.48×** |
| luxembourg | 1,510 | 2.56× | 195 | **0.33×** |

Published figures: RTE *Bilan électrique* 105,817 km; Terna statistical annex
70,974 km; PSE 16,520 km; TEİAŞ *Stratejik Planı* 74,442 km; CENACE PRODESEN
110,846 km; ILR 590 km.

**Reading.** The filter is a large improvement — Poland moves from 7.2× the
national transmission length to within one per cent of it, France from 2.8× to
1.2×. But the residual spread runs from 0.33× to 1.48×, a factor of 4.5 between
best and worst, and Mexico barely improves at all because a 69 kV threshold
admits nearly everything OSM holds.

**Therefore the Convention #7 proxy declaration in the 30 August draft must
survive signature, not be retired by it.** I4 is *transmission-voltage OSM
power-line density*, and it must not be published as "RTN density" without that
declaration. The draft anticipated exactly this and warned it "would be a poor
outcome to reintroduce it at the first honest metric."

---

## 4. Residual data-quality items found while measuring

**4.1 `kv = 0` is a sentinel for unknown, not a voltage.** Countries encode
missing voltage two different ways — the UK omits the field on 35.4 per cent of
line-km, while Finland supplies `kv = 0` on 33.8 per cent. Any threshold code
must treat both as unknown. A first pass of this measurement did not, and
silently scored 26,381 km of Finnish line as 0 kV.

Materially affected: iceland 50.2%, luxembourg 57.5%, ireland 34.6%, switzerland
35.7%, uk 35.4%, finland 33.8%, norway 28.4%, israel 28.7%, slovenia 25.4%,
austria 23.2%. **For these, any threshold operates on the remaining fraction
only, and that fraction must be published with the metric.** Luxembourg's
threshold governs 42.5 per cent of its network.

**4.2 Turkey's 66 kV mass is not transmission.** Measured: 35,941 km at 66 kV,
second only to 154 kV's 36,833 km. TEİAŞ's own figure for 66 kV is **119.5 km**
— a factor of 300. The 66 kV tier in Turkish OSM is distribution, and although
the grid code does name 66 kV as a nominal transmission voltage, pinning 154 kV
is what keeps this out.

**4.3 Turkey's volts-vs-kilovolts defect is fixed, with one survivor.** The draft
found 2,204 of 8,061 line records (27 per cent) carrying volts. Now: **1**. It
reads `15400.0` kV, which is physically impossible — the world's highest
transmission voltage is about 1,100 kV. One record, findable, worth sweeping.

**4.4 Zero-density substations.** Under definition A at the pinned threshold,
substations whose 3×3 block contains no transmission line score a raw of zero,
which after inversion becomes the *worst* density band. Measured: France 0.1 per
cent, Poland 6.2 per cent, **Spain 13.2 per cent**. Whether that is a genuine
finding about remoteness or an artefact of a distribution-only substation needs a
decision before the inversion is applied. It is not addressed in either draft.

---

## 5. What is requested

1. **Definition A**, 0.1° cells, 3×3 block — confirm or substitute a stated radius.
2. **The 13 sourced thresholds** as pinned in §2, including the four corrections,
   the UK treatment chosen in §2.2, and Greenland declared NOT APPLICABLE.
3. **Whether to hold the 26 unsourced countries** (recommended) or sign the
   draft's unverified reading for them.
4. **The zero-density treatment** in §4.4.
5. Acknowledgement that the **Convention #7 proxy declaration survives** — I4 is
   an OSM power-line proxy for RTN density, not RTN density.

On signature: the derivation is re-run for the signed set, `_metrics_source` is
corrected (it currently cites `AMENDMENT_DRAFT_I4_definition.md`, which exists
nowhere — the real document is `AMENDMENT_DRAFT_I4_I6_definition.md`, and the
manifest's `metric_derivations` cites it correctly), I4's status moves from
`blocked` to `implemented` for the signed countries only, and a change-log entry
naming element I4 is registered.

**If this is not signed**, the honest alternative is to withdraw the derivation:
remove I4 from the metric layer until a definition is pinned. What is not
available is leaving it where it is — published on 622,104 records, citing two
documents that state on their face that nothing has been written to the register.

---

*Measurements in §1, §3 and §4 taken 17 September 2026 against the deployed tree.
Voltage authorities in §2 are cited to the operator's, regulator's or
legislature's own publication in every case; where only a secondary source could
be found it is labelled as such in the research record. Line-km are computed by
haversine over each polyline's own vertices.*
