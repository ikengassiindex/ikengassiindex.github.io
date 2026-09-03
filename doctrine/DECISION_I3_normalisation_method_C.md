# Decision — I3 is normalised by Method C

**Decided by** operator · **on** 31 August 2026
**Registered under** SSI Foundation Bible §8
**Element** `I3`
**Basis** `COMPARISON_I3_normalisation.md` · `MEMO_I3_normalisation_audit_view.md`

---

## 1. The decision

I3 (Heat-wave risk) moves from `B_percentile` to `C_bounded`, normalised
against a declared interval `[0, 0.30]` with a frozen anchor of
**51.93 degree Celsius days per year → 0.30**.

This is not a change of method against the controlling document. The
rank-4 v4.2 construct already assigned Method C to I1–I3; the deployed
derivation used Method B. **This amendment closes that deviation rather
than regularising it**, which is the posture Bible §1 requires.

## 2. Why, in one sentence

Under Method B a substation's published value depends on facts about
other substations. Under Method C it does not.

The supporting measurements are in the companion documents. The three
that carried the decision:

- Method B railed **10.3%** of the fleet at 0.000 or 1.000, and treated a
  substation with 82% more heat-wave excess than another as identical to
  it — against a doctrinal pin that I3 exists to capture extreme
  deviations.
- Stored anchors ranged from a **2.06 °C·day** span (Luxembourg) to
  **11.15** (Colombia), both mapped onto the same published [0, 1]. On I3
  as published, the index was not a cross-jurisdictional comparison.
- Section 05 of the v4.2 construct tests `IRI_current` against
  `IRI_THRESH = 0.02` **on the raw [0, 0.30] scale**. Method C produces
  that quantity; Method B does not, so a control the controlling document
  mandates could not be executed.

## 3. What §8 required, and where each part landed

§8 requires five things in the same change. Each is now in the source of
truth rather than in prose:

| § | Requirement | Where it landed |
|---|---|---|
| 1 | the new declared value | `judgement.yaml` → `metrics.I3` — `normalisation_method: C_bounded`, `bounded_interval: [0.0, 0.30]`, `anchor: {value: 51.93, maps_to: 0.30}` |
| 2 | a provenance pin | `metrics.I3.provenance` — operator, 2026-08-31, with the basis stated |
| 3 | an evidence tier with citation | `evidence.yaml` → `Perkins2013`, tier **E2**, DOI `10.1175/JCLI-D-12-00383.1`, `underpins: [I3]` |
| 4 | a change-log entry naming the element | `judgement.yaml` → `change_log.changes[0].element: I3` |
| 5 | a full re-render of every tier below | master construct + appendix and all **39** country pairs re-rendered — 160 files — and the conformance register rebuilt |

Two supporting amendments were required to make the above possible and
are part of the same change:

- `taxonomy.yaml` → `metric_inventory` gains `bounded_interval` and
  `anchor` (both class J, not MUST), and the section guard now reads: *a
  C_bounded metric whose bounded_interval is not [0, 1] must declare an
  anchor, and that anchor must state the basis on which it was pinned and
  the terms on which it is revised.*
- `SSI_FOUNDATION_render2.py` gains a `_change_log` writer. See §5.

## 4. The anchor is a pin, and is declared as one

51.93 °C·days is the 99.9th percentile of the **2018–2022** fleet,
measured across 620,129 derived records on 31 August 2026.

It is pinned once and frozen. Recomputing it each run would restore the
population dependence this decision exists to remove. The metric declares
its own revision terms: revised only by amendment, and only where the
fleet saturates against it — a condition that is **visible in the
published data**, because a hotter fleet saturates at 0.30 rather than
silently rescaling every other record.

The estate's existing doctrine on within-country anchoring is not
overturned by this. It is extended, and the construct now says so:
anchoring within a country was adopted so that a country's scores do not
move when an unrelated country is onboarded. `C_bounded` carries that
same reasoning to its conclusion — a within-country percentile still
makes a value depend on other substations, fewer of them and only
countrymen, but the same in kind.

## 5. A blocker found and closed on the way

**The change log could not be rendered.** The taxonomy declares
`change_log` a required section. The renderer's Section-conformance table
listed it in `rendered_here` and therefore reported it **✅ present in
this render** — while no writer for it existed anywhere in the renderer.

That is a conformance table asserting a section it does not produce: the
exact defect class this structure exists to prevent, committed by the
enforcement layer itself. It also meant **no amendment made under §8
could have been conformant**, because §8 item 4 had nowhere to land.

`_change_log` now writes the section, and executes the taxonomy's guard
rather than asserting it — an entry naming an element the registry does
not carry renders as a failure row.

## 6. What the re-render actually changed

Master construct, verified by diff against the pre-amendment render:

- new **§3 What changed against the previous version**, one entry, guard ✅
- I3 definition replaced with the measured heat-wave rule it implements
- I3 units `index` → `degree Celsius days per year`
- I3 normalisation `B_percentile` → `C_bounded`, plus bounded-interval and
  anchor rows, and anchor basis / revision blockquotes
- I3 evidence `E0 ERE2026` → `E0 ERE2026 · E2 Perkins2013`
- I3 source no longer blocked — blocked sources 36 → 35
- normalisation framework: the assignment table moves I3 between methods,
  and a new anchored-metric table and doctrine paragraph appear
- source registry gains the ERA5-Land line; bibliography gains Perkins2013
  with both what it establishes and what it does not
- `metric_inventory` declared fields 15 → 17

Blocking gaps unchanged at **22**. Gaps closed by the country file 38 → 37
(one fewer raised, because I3's source is now declared).

## 7. The register can now see this decision

§8 item 5 asks for sentinels passing. They passed — and that was the
problem. The register carried **no row on normalisation method at all**.
Its metric rows test population and status, and I3, I4 and I6 had dropped
out of it entirely once they carried data. The one divergence this
amendment deliberately creates produced no row, and the sentinel was
green because nothing tested it. Bible §9 requires the register to carry
every divergence between doctrine and deployment.

`SSI_FOUNDATION_conformance.py` now measures the deployed normalisation
from `meta.metric_derivations` in each published manifest — **the
deployment's own statement**, not the derivation script. A script edited
and not re-run therefore cannot turn the row green; only a re-derivation
can, which is the whole value of the row.

Two failure modes are kept apart, because reporting an absence in a
contradiction's wording is how a register loses its authority:

| Element | Aspect | Declared | Observed | Severity |
|---|---|---|---|---|
| `I3` | normalisation method | `C_bounded` | `B_percentile` in 39 of 39 | **BLOCKING** |
| `I3` | anchor value | 51.93 °C·days | no anchor recorded | **BLOCKING** |
| `I4` | normalisation coverage | all 39 countries | a record in 37 of 39 — iceland, luxembourg | MATERIAL |
| `I6` | normalisation coverage | all 39 countries | a record in 37 of 39 — iceland, luxembourg | MATERIAL |
| `I4`, `I5`, `I6` | normalisation method | `B_percentile` | `B_percentile` | conforming |

The two I3 rows are red **and are meant to be**: doctrine leads
deployment by design under Bible §1. They go green when the derivation is
amended and re-run, and not before.

Register: 45 → 52 rows, BLOCKING 8 → 10, MATERIAL 2 → 4.

A second inconsistency surfaced and was closed on the way. The register's
own entry point measures the deploy chain before building; the renderer
did not, so every document's Conformance section printed a row count
**four short of the register it claims to summarise** — 48 against 52. A
document that disagrees with the register about the size of the register
is worse than one that omits the section. The renderer now measures it
too, and the master reports 52/38/14 exactly as the register does.
Country documents report 49–50 by design, since R7 activation and the
cohort rows are measured for that jurisdiction rather than the cohort.

## 8. Open, and not closed by this decision

1. **Re-derivation of I3 itself.** This decision changes doctrine. The
   published values are still Method B until `ssi_derive_metric_I3.py` is
   amended and re-run, at which point the restatement in §6 of the
   comparison document lands — 22.9% of records moving more than 0.01 in
   R_base. Doctrine first, deployment second, per Bible §1.
2. **The provenance strings.** 620,696 records claim "fleet P5/P95".
   The master construct's doctrine was always correct; the derivation
   scripts' strings are not. Required under any method.
3. **M-006 scope.** `soft_clip_upper` is imported at two call sites the
   D4 `clip_continuity` invariant does not watch —
   `ssi_derive_metrics_I4_I6.py:150` (54,377 records, 16× the declared
   3,309 baseline) and `ssi_derive_component_T.py:141` (unquantified).
   The zeta-0.2 repair should be re-scoped before it is executed.
4. **The master appendix carries a contradictory legacy catalogue.** It
   embeds Australia's country-file metric table, which names I1 "Asset Age
   Index", I5 "Seismic PGA", I6 "Corrosion Class", I7 "Flood Risk Zone"
   and assigns I3 to "A (P5/P95)". None of that is the v4.2 catalogue, and
   it now sits alongside the registry-derived table that contradicts it.
   Pre-existing; surfaced by this work, not caused by it.
5. **I8 is `D_categorical` in the judgement layer** and "B (P5/P95)" in
   the v4.2 Italy construct. A divergence to resolve when I8 is pinned.
