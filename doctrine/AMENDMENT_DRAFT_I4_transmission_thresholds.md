# Amendment draft — per-country transmission voltage thresholds for I4

**For flag-officer signature.** Definition A with a voltage filter is pinned;
this sets the filter, per country, as instructed ("voltage is not a clean
uniform thing").
**Date:** 30 August 2026. **Evidence tier:** Tier 0 — line-km by voltage level,
measured from each country's own `grid-geo.json`.
**Nothing written to the register.**

---

## 1. No re-fetch is required

Every line record in all 39 countries already carries a `kv` field:

    {'i': <osm id>, 'kv': <voltage>, 'p': [[lon,lat],…], 'se': …, 'ss': …}

2.9 million line records cohort-wide. The Overpass re-ingestion contemplated
when this definition was pinned is unnecessary.

## 2. Measured distribution, and the proposed pin

`line-km` by voltage. **Mode** is the level carrying the most km — usually the
distribution tier. **Proposed** is provisional and marked by its basis.

| country | TSO | total km | no-kv | mode | levels present (top, by km) | proposed |
|---|---|---:|---:|---:|---|---:|
| france | RTE | 295,763 | 0.0% | 20 | 63·90·225·400 | **63** |
| germany | 4 TSOs | 295,134 | 0.0% | 20 | 110·220·380·400 | **220** |
| italy | Terna | 143,509 | 0.0% | **132** | 132·150·220·380 | **132** |
| spain | REE | 179,267 | 0.0% | 20 | 66·132·220·400 | **220** |
| uk | NG ESO | 190,578 | **35.4%** | 11 | 33·132·275·400 | **275** ⚠ |
| poland | PSE | 119,497 | 7.3% | 15 | 110·220·400 | **220** |
| norway | Statnett | 121,939 | **28.4%** | 22 | 132·300·420 | **300** |
| portugal | REN | 93,812 | 0.0% | 30 | 60·150·220·400 | **150** |
| sweden | Svk | 66,451 | 0.0% | **130** | 130·220·400 | **220** |
| finland | Fingrid | 78,033 | **33.8%** | **110** | 110·220·330·400 | **110** |
| denmark | Energinet | 13,575 | 0.8% | 60 | 132·150·400 | **132** |
| netherlands | TenneT | 7,208 | 7.6% | **150** | 110·150·220·380 | **110** |
| belgium | Elia | 8,373 | 17.1% | 70 | 150·220·380 | **150** |
| austria | APG | 35,244 | 23.2% | **110** | 110·220·380·400 | **220** |
| czechia | ČEPS | 61,626 | 2.3% | 22 | 110·220·400 | **220** |
| slovakia | SEPS | 27,441 | 15.9% | 22 | 110·220·400 | **220** |
| hungary | MAVIR | 48,854 | 11.1% | 22 | 132·220·400 | **132** |
| slovenia | ELES | 6,883 | 25.4% | **110** | 110·220·400 | **110** |
| estonia | Elering | 10,973 | 13.4% | **110** | 110·330·400 | **110** |
| latvia | AST | 28,178 | 3.2% | 20 | 110·330 | **110** |
| lithuania | Litgrid | 11,389 | 11.9% | **110** | 110·330 | **110** |
| luxembourg | Creos | 1,512 | **57.5%** | 65 | 65·150·220 | **150** ⚠ |
| ireland | EirGrid | 42,337 | **34.6%** | 20 | 38·110·220·400 | **110** |
| iceland | Landsnet | 7,898 | **50.2%** | **132** | 66·132·220 | **132** ⚠ |
| greece | IPTO | 12,740 | 3.8% | **150** | 150·400 | **150** |
| turkey | TEİAŞ | 103,691 | 0.0% | **154 000** | see §4 — units defect | **154** ⚠ |
| switzerland | Swissgrid | 13,323 | **35.7%** | **220** | 110·132·220·380 | **220** |
| japan | 10 T&D | 95,907 | 0.0% | 66 | 154·187·275·500 | **154** |
| korea | KPX | 15,192 | 2.6% | **154** | 154·345·765 | **154** |
| israel | IEC | 8,818 | 28.7% | **161** | 161·400 | **161** |
| mexico | CENACE | 166,441 | **50.6%** | **115** | 115·230·400 | **230** |
| canada | provincial | 152,172 | 5.6% | **230** | 138·230·500·735 | **230** |
| chile | CEN | 28,403 | 12.6% | **220** | 110·220·500 | **220** |
| colombia | XM | 22,995 | 4.1% | **230** | 110·115·230·500 | **230** |
| costa-rica | ICE | 3,529 | 2.2% | **230** | 138·230 | **138** |
| greenland | Nukissiorfiit | 265 | 13.4% | **132** | 60·63·66·132 | **60** ⚠ |
| new-zealand | Transpower | 91,763 | 6.9% | 11 | 66·110·220·350·400 | **110** |
| australia | AEMO | 123,677 | 6.9% | **132** | 132·220·275·330 | **132** |
| us | ISO/RTO | 1,746,001 | 0.0% | 69 | 69·115·138·230·345·500 | **115** ⚠ |

**Basis.** Every figure left of "proposed" is measured. The proposed column is
NOT measured — it is my reading of where each TSO's transmission tier begins,
and it is exactly what the 37 unwritten delta sidecars are supposed to carry.
Treat it as a starting point for your pin, not as a finding.

## 3. The seven marked ⚠ need a decision rather than a default

- **uk** — 132 kV is transmission in Scotland and distribution in England/Wales.
  A single national threshold is wrong either way. 275 excludes Scottish
  transmission; 132 includes English distribution.
- **us** — no national definition. FERC/NERC bulk-electric-system is ≥100 kV;
  many utilities call 69 kV transmission. 69 vs 115 moves 360,666 km.
- **luxembourg** — 57.5% of line-km has no voltage at all. Any threshold
  operates on 42.5% of the network.
- **iceland** (50.2% no-kv), **mexico** (50.6% no-kv) — same problem, worse.
- **greenland** — 265 km total, and 132 kV is implausible for a 56,000-person
  system. Needs a look, not a threshold.
- **turkey** — see §4.

## 4. A defect found while measuring this

**Turkey's `kv` field is in volts, not kilovolts.** 2,204 of 8,061 line records
(27%) carry values above 1,000: `154000`, `380000`, `34500`, `31500`. The
correct readings are 154, 380, 34.5, 31.5 kV.

This is the same unit-confusion defect class as the Italy `voltage=15000;400`
case that the JIS paper is built on — found again, in the register's own line
geometry.

Sub-1 kV values also appear: uk 3,681 records, norway 1,426, estonia 611,
latvia 175, greenland 3. Seventeen countries show one anomaly or the other,
but only turkey is material at 27%.

**Recommendation:** fix turkey's units before pinning its threshold, and gate
the field. A `kv` above 1,000 is never a voltage in kilovolts on a power line.

## 5. What follows signature

I4 is computed as transmission line-km within a 3×3 block of 0.1° cells
(~33 km) around each substation, Method B normalised over fleet P5/P95, then
inverted per §03. It is written to a new `metrics` block with a provenance
marker naming this amendment and the pinned threshold.

I6 needs no threshold and can proceed regardless.

**Neither changes `components.I`.** I is nine metrics; two of nine does not
compose a component, and the `enrich_esg_gaps` fill for `components.I` cannot
be removed until all nine are real. This step builds the metric layer that has
never existed — a foundation, not a visible change to any published score.
