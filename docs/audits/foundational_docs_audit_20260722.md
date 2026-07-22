# Foundational documentation audit — 22 July 2026

> **Operator directive**: thorough read of ALL foundational documentation across
> Tier 1 (framing) + Tier 1a (formula construct + technical appendix) +
> Tier 2 (methodology hub) + Tier 3 (repo-side), with focus on cross-doc
> **consistency + coherence**, then refresh what needs refreshing.
>
> **Anchor**: CLAUDE.md (last updated 21 Jul 2026 evening) is the fresh
> "current state" reference. All other foundational docs are audited against
> this + against each other.
>
> **Findings severity**: `CRITICAL` (empirically wrong / actively misleading)
> · `MAJOR` (materially stale — post-June-2026 landings not reflected)
> · `MINOR` (small refresh — dates, cross-refs, wording)
> · `OK` (current)
>
> **Author**: Sandbox audit — writes findings, no doc-side edits yet
>
> **Related tasks**: #459 (this parent) · #268 (prior audit-first discipline anchor) · #431 (workstream 2 foundational-doc audit prior pass, closed)

---

## Global evaluation rules

Applied to every doc in the read pass. Findings register + refresh recommendations honour these.

### G1 — Jesuit-terminology scrub (external-facing docs) — LOCKED

**Operator directive, 22 Jul 2026**: *"the Jesuit item is purely internal so we never forget the way in which we communicate, it is not to be mentioned in any external facing deliverables"*.

**Rule**:
- **External-facing** docs (published as PDF/HTML/print, or living in `Report Production/00-Framing/` which is the external-narrative hub, or repo-side README/dashboard) — **any mention of "Jesuit" / "Jesuit style" / "Rule N (Jesuit Style)" is drift and MUST be scrubbed**. Canonical external-voice replacement: `structured analytical writing discipline` (per About §9 usage).
- **Internal** docs (SSI Index root: HOUSEKEEPING.md, CONVENTIONS.md, CLAUDE.md, KB, internal audit memos) — Jesuit label preserved as internal shorthand so the writing discipline is not forgotten.

**Docs affected (scrub required)**: METHODOLOGY_DISCIPLINES.md (26 Jesuit refs, MD.1 escalated to CRITICAL - SCRUB REQUIRED), REPORTS_FRAMING_KB.md (Phase 3 read pending, likely many refs), any external-facing content that references Rule N by name.

**Docs unaffected (Jesuit label OK)**: HOUSEKEEPING.md, CONVENTIONS.md, CLAUDE.md, internal audit memos.

Rule enforced across all subsequent Phase 2-9 doc reads.

---

## Scope inventory

### Tier 1 — Framing docs (`SSI Index/Report Production/00-Framing/`)

| # | Doc | Size | Last edit | Phase |
|---|---|---:|---|---|
| T1.1 | About_SSI_Index.md | 19 KB | 21 Jun 2026 | P1 |
| T1.2 | METHODOLOGY_DISCIPLINES.md | 29 KB | 12 Jul 2026 | P2 |
| T1.3 | REPORTS_FRAMING_KB.md | 102 KB | 21 Jul 2026 | P3 |
| T1.4 | EDITORIAL_CALENDAR.md | 45 KB | 20 Jul 2026 | P5 |
| T1.5 | SSI_INDEX_X_SSI_ENN_DATA_BRIDGE.md | 38 KB | 20 Jul 2026 | P5 |
| T1.6 | SSI_INDEX_DIFFERENTIATION_ANGLES.md | 32 KB | 18 Jun 2026 | P6 |
| T1.7 | COMPETITIVE_SCORING_MATRIX.md | 28 KB | 18 Jun 2026 | P6 |
| T1.8 | COMPETITIVE_SCRAPE_KB.md | 50 KB | 18 Jun 2026 | P6 |

### Tier 1a — Formula Construct + Technical Appendix

| # | Doc | Size | Last edit | Phase |
|---|---|---:|---|---|
| T1a.1 | SSI_v4_2_Complete_Formula_Construct_Italy_v3.html | **228 KB** | 18 Jun 2026 | P4 |
| T1a.2 | SSI_v4_2_W1_W10_Substation_Formula_Construct_Italy_v2.html | 62 KB | 11 Jun 2026 | P4 |
| T1a.3 | SSI Index v4.2 Methodological Foundations PDF | (tbd) | mid Jun 2026 | P4 |
| T1a.4 | 10+ per-country W1-W10 FCs | varies | Q3 2026 | P7 (sample) |

### Tier 2 — Methodology hub (`SSI Index/` root)

| # | Doc | Size | Last edit | Phase |
|---|---|---:|---|---|
| T2.1 | CONVENTIONS.md | 65 KB | 18 Jun 2026 | P2 |
| T2.2 | HOUSEKEEPING.md | 43 KB | 18 Jun 2026 | P2 |
| T2.3 | LITERATURE_EVIDENCE_REPORT_v4_2.md | 108 KB | 11 Jun 2026 | P3 |
| T2.4 | AUDIT_BASELINE.md | 12 KB | 13 Jun 2026 | P1 |
| T2.5 | SSI_Dashboard_Knowledge_Base_v19.md | 344 KB | 18 Jun 2026 | P8 |
| T2.6 | AUDIT_v4_0_2_PRE_v4_2_FOUNDATION.md | 70 KB | 8 Jun 2026 | P9 |

### Tier 3 — Repo-side (`ikengassiindex.github.io/`)

| # | Doc | Size | Last edit | Phase |
|---|---|---:|---|---|
| T3.1 | CLAUDE.md | ~500 KB | 21 Jul 2026 | (anchor — no audit needed) |
| T3.2 | README.md | (small) | (?) | P1 |
| T3.3 | Recent audit memos (R7/Convention #78/v4.23/etc.) | varies | recent | reference-only |

---

## Per-doc findings (populated incrementally as read pass proceeds)

### T3.2 — README.md (Phase 1) — **overall severity: CRITICAL**

Doc is a **v4.0.2-era snapshot**, materially misleading. Not updated since v4.2 shipped.

| # | Finding | Severity |
|---|---|---|
| R.1 | Header stamps `v4.0.2` — should be v4.2 methodology + v4.23 ingestion cohort | CRITICAL |
| R.2 | Substation count "> 130k across ... 39" — actual **796,121** post-Wave-4 (6× undercount) | CRITICAL |
| R.3 | Italy reference baseline `4,293 substations` — actual **51,910** post-Wave-4 (12× undercount) | CRITICAL |
| R.4 | Formula lists v4.0.2 modifier chain (R4/R3/R6a/R6b/R7cyber only) — missing entire v4.2 family (R6c flood + R6d wildfire + R6e winter + R8 adapt + R9 compound + R10 just + Re composite) | CRITICAL |
| R.5 | Component structure lists 6-axis (CVIEST) — v4.2 heptagonal CVIESTR (adds Re axis) missing | CRITICAL |
| R.6 | Classification bands: 4-band Low/Med/High/Critical — post-25-Jun-2026 5-band system with Extreme [1.00, 1.30] missing | MAJOR |
| R.7 | Counts stale: `95 variables · 30+ sources · 8 modifiers` — actual **101 vars · 34 sources · 11 modifiers** | MAJOR |
| R.8 | Architecture tree missing `esg-report.html` + `intelligence.html` + `regional-sections.js` + `esg-sections.js` (6-page structure vs 5-page shown) | MAJOR |
| R.9 | Task #123 reference is a repo-internal task-number — shouldn't be in public README | MINOR |
| R.10 | "Phase 1.5 ingestion (June 2026)" wording positions June 2026 as current — 7 months out of date | MINOR |
| R.11 | Missing all Wave 2/3/4 progress narrative (Wave 4 TERMINAL closure 21 Jul 2026 nowhere) | MAJOR |
| R.12 | Design system: `Playfair Display + DM Sans` — actual `Playfair Display + Cormorant Garamond` | MINOR |

**Refresh recommendation**: full README rewrite — not a patch job.

### T1.1 — About_SSI_Index.md (Phase 1) — **overall severity: MAJOR**

Well-structured 9-commitment narrative with strong v4.2 anchoring, but count-drift + missing post-June-18 landings.

| # | Finding | Severity |
|---|---|---|
| A.1 | Substation count `174,046` — actual **796,121** (4.6× undercount from post-Wave-2/3/4) | MAJOR |
| A.2 | Italy Stage 4 pilot `4,293 substations` — likely defensible as historical reference-set validation cohort BUT reader will read this as current fleet size (which is now 51,910). Needs disambiguating footnote | MAJOR |
| A.3 | "7 of 7 historical-event PASS battery" — prior session (task #37 HIT-A3) swapped Mezzogiorno 2024 out of the battery. Needs verification: is it now still 7/7 or is the composition/status different? | MAJOR |
| A.4 | Line 13 cites `Convention #62` + `Convention #63` — these are **SSI-ENN** conventions, not **SSI Index** conventions. SSI Index has its own Discipline register (Discipline #36 = cross-border, etc.). A reader could reasonably conflate the two registers. **Cross-repo terminology coherence issue** | MAJOR |
| A.5 | Line 9 says "39 OECD jurisdictions" — cohort is `38 OECD member + Greenland (autonomous territory within Kingdom of Denmark, not an OECD member)`. Landing page has this right. Should sync | MAJOR |
| A.6 | Foundation timeline `"target establishment in 2027-2028"` — verify against EDITORIAL_CALENDAR + operator commitments | MINOR |
| A.7 | Line 27 `"Q3 2026 open-source release of the core scoring repository"` — we're now in Q3 2026 (July). Track record + revised commitment need updating | MAJOR |
| A.8 | No mention of: Convention #78 BINDING promotion, Convention #79 candidate ssi-data sharding, 5-band Extreme, R7 SFDR PAI Phase 4a-4e rollout, Wave 2/3/4 completion (all landed post-18 Jun 2026) | MAJOR |
| A.9 | Version stamp `v1 · authored 18 June 2026 deep night` — needs v2 bump at refresh | MINOR |

**Refresh recommendation**: v2 refresh preserving the 9-commitment structure + narrative voice. Update: cohort count · Convention # discipline separation SSI Index vs SSI-ENN · Foundation timeline reality-check · post-June-2026 landings inclusion.

### T2.4 — AUDIT_BASELINE.md (Phase 1) — **overall severity: CRITICAL**

Doc labelled `"Binding canonical baseline for the SSI Index v4.2 methodology"` — but hasn't been maintained since 13 June 2026 (only 1 addendum). Now stale on every headline KPI.

**Cross-doc coherence issue**: This doc self-describes as "the source of truth" (line 12: "Other docs MUST cite values here. If a discrepancy surfaces, the inconsistent doc gets refreshed against this baseline"). But CLAUDE.md is the actual fresh source of truth. **Truth-source ambiguity across the doc set** — reader is left uncertain which is canonical.

| # | Finding | Severity |
|---|---|---|
| AB.1 | `Italy fleet | 4,293 substations` (line 32) — actual **51,910** post-Wave-4 (12× stale) | CRITICAL |
| AB.2 | Line 98 `CONVENTIONS.md — 12 conventions (#1 … #12)` — repo state is now at Convention #78 BINDING + Convention #79 candidate (see CLAUDE.md). Massive convention-register drift | CRITICAL |
| AB.3 | No mention of 5-band Extreme classification (Phase 2A/B/C, 25 Jun 2026); classification-band structure implicitly 4-band | CRITICAL |
| AB.4 | No mention of R7 SFDR PAI dual-axis architecture (Phase 4a-4e, 16 Jul 2026) — line 65 shows R7 as "Cyber-Exposure" only. Should reflect both R7 cyber modifier AND R7 SFDR PAI ESG-disclosure axis (per FC v3 §14 subsection 13.7 + V4_2_IMPLEMENTATION_ARCHITECTURE.md §4.5) | CRITICAL |
| AB.5 | No mention of Discipline #36 (cross-border enforcement, 25 Jun 2026) — the parent CLAUDE.md flags it heavily; AUDIT_BASELINE has nothing | MAJOR |
| AB.6 | USCO filing history (line 129-136) stops at USCO-005 "IN PREPARATION". Full Wave 2 (Jul 12-13) + Wave 3 (17 Jul) + Wave 4 (17-21 Jul TERMINAL) all missing from history | MAJOR |
| AB.7 | Voltage class counts `475 EHV / 3,035 HV / 783 dist` are v4.0.2-era Italy pre-Wave-4 refresh. Wave 4 Italy is 51,910 subs — the tier breakdown will differ substantially | MAJOR |
| AB.8 | Line 118 `Current Edition (June 2026): Edition 02 / 2026-06 / Italy corridor: Puglia` — Edition rotation should have advanced 7 months. Verify against intelligence/edition-config.json | MAJOR |
| AB.9 | Line 183 cohort-parity `16 countries (Italy + 15 cohort = 47,673 substations)` — Wave 4 TERMINAL closed at 39 countries × 662k Wave-4-side subs alone. Number is ~17× stale | MAJOR |
| AB.10 | No addenda since 13 June 2026 — over 5 weeks of major landings unrecorded | CRITICAL |

**Refresh recommendation**: **complete v2 rewrite** — this doc's whole model is "append addenda at top, never delete". Right approach is to add a v2 addendum with current state + then decide whether to auto-collapse the June baseline into a "historical footnote" or preserve it as-is with a big banner "SUPERSEDED — see v2 addendum".

### T1.2 — METHODOLOGY_DISCIPLINES.md (Phase 2) — **overall severity: MAJOR**

Actually in **better shape** than the anchor docs — was updated 12 Jul 2026, contains the §5bis reclassify-vs-rescore + §5ter state-transition auditability (both 25 Jun 2026 additions). But still has systemic coherence issues.

| # | Finding | Severity |
|---|---|---|
| MD.1 | **🚨 SCRUB REQUIRED per operator directive 22 Jul 2026 (see Global Rule G1)** — doc refers to `Rule N (Jesuit Style)` and `Jesuit style` **26 times**. Doc lives in `Report Production/00-Framing/` (external-narrative hub) and is exported to HTML/PDF. Operator locked directive: *"the Jesuit item is purely internal so we never forget the way in which we communicate, it is not to be mentioned in any external facing deliverables"*. Canonical external-voice replacement: `structured analytical writing discipline` (per About §9). Refresh action: rewrite §2 (Rule N section) as `Discipline N — Structured Analytical Writing`; sweep all 25 other refs to Jesuit terminology across the doc, preserving the SUBSTANCE (short declarative sentences, front-loaded conclusions, hierarchical enumeration, no rhetorical flourish) but retiring the LABEL. | CRITICAL |
| MD.2 | Line 137-146 refers to SSI-ENN conventions #56/#60/#62/#63/#67/#75 (correctly attributing to SSI-ENN via line 234). But cross-doc coherence still poor: reader must understand there are TWO discipline registers (SSI Index Discipline #36-#38+ + SSI-ENN Convention #56+). Only §3 header "Convention chain" hints at this | MAJOR |
| MD.3 | Missing all post-25-Jun-2026 landings: Convention #78 BINDING promotion (16 Jul), Convention #79 candidate ssi-data sharding (18 Jul), R7 SFDR PAI Phase 4a-4e (16 Jul), Wave 3 completion (17 Jul), Wave 4 TERMINAL (21 Jul), Disciplines #37/#38/#39 candidate | MAJOR |
| MD.4 | Line 156 `Italian Stage 4 (validated) | Direct at 4,293 substations` — actual 51,910 post-Wave-4. Same as A.2 above — needs disambiguating footnote (historical validation cohort vs current cohort) | MAJOR |
| MD.5 | Line 157 `Spanish + German Stage 4 (September 2026)` — 2 months away. On-track verification needed | MINOR |
| MD.6 | Doc version stamps `v1 · 19 June 2026` (line 5, line 240). File was updated 12 Jul 2026 with §5bis + §5ter additions — should be v1.1 or v2 | MINOR |
| MD.7 | Cross-doc coherence with About_SSI_Index.md: both refer to Rules M + N; commitments #8 + #9 in About ↔ §1 + §2 here. Explicit cross-ref preserved (line 231). **Coherent within the "Jesuit terminology stays" reading, coherent within "Jesuit terminology scrubbed" reading — but currently BOTH docs have it heavily, so if the scrub was intended, drift is bilateral** | MAJOR (coherence) |

**Refresh recommendation**: v1.1 refresh — resolve terminology question first (MD.1), then patch (a) Italy count with historical footnote, (b) add addendum §5quater covering post-25-Jun landings (Convention #78/#79, R7 SFDR PAI, Wave 3/4).

### T2.2 — HOUSEKEEPING.md (Phase 2) — **overall severity: MAJOR**

Internal working-memory doc (SSI Index root — Jesuit label preserved OK per G1). Structurally sound trigger-driven procedure register. Last touched 18 Jun 2026. Gaps are additive: no post-June-2026 landings, no post-Wave-2/3/4 triggers, no v4.23 refresh cadence, but structure + existing triggers stay valid.

| # | Finding | Severity |
|---|---|---|
| HK.1 | Header stamps `Established: 11 June 2026 during the V4.2-4c discipline-layer remediation`, footer says `Last updated 18 June 2026`. Doc has not been touched in 5+ weeks despite: Discipline #36 (25 Jun 2026), Phase 2A/B/C 5-band Extreme (25 Jun 2026), Discipline #37 defensive-coding (16 Jul 2026), Discipline #38 nested-field navigation (16 Jul 2026), R7 SFDR PAI Phase 4a-4e (16 Jul 2026), Convention #78 BINDING promotion (16 Jul 2026), Convention #79 candidate ssi-data sharding (18 Jul 2026), Wave 4 TERMINAL (21 Jul 2026). All Triggers #4-#14 have no post-June entries | MAJOR |
| HK.2 | Trigger #14 (public production deployment closure) fired ONCE for the v4.2 ship (18 Jun 2026, LP-1..LP-12) but has NOT been re-fired for subsequent major landings — Wave 2 EU-OECD batch (12 Jul), Wave 3 Greece + others (17 Jul), Wave 4 TERMINAL 9 countries + sharding (21 Jul). By Trigger #14's own text these are "substantial methodology + product + automation deployment" — closure memos should exist. Verify whether the operator has fired Trigger #14 for these via alternative memos (e.g. commit closure notes) or whether this is unrecorded procedural drift | MAJOR |
| HK.3 | Trigger #8 conflict-resolution table (lines 265-268) shows 4 conflicts all resolved. No new open conflicts logged. But: R7 SFDR PAI Phase 4a discovery surfaced a "cohort-wide false-positive latent bug" (per CLAUDE.md ⭐ block) in `assess_esg_readiness()` — this is exactly the Convention-#6-class pattern. Should have prompted a Trigger #8 lit-review section in `LITERATURE_EVIDENCE_REPORT_v4_2.md` (verify against Phase 3 read) | MAJOR |
| HK.4 | Trigger #10 (voltage-tier trichotomy) still cites `475 EHV / 3,035 HV / 783 distribution-tier` as Italy canonical (line 346). This is pre-Wave-4-refresh Italy at 4,293 subs. Post-Wave-4 Italy = 51,910 subs → the tier counts are ~12× stale. If any dashboard surface still displays these three numbers, they're wrong | CRITICAL |
| HK.5 | Trigger #13 (Convention #14.1 bootstrap-source largest-canonical) covers 15 countries. Wave 4 TERMINAL onboarded 9 countries (Sweden, Portugal, Italy, Japan, Spain, France, Germany, US, UK). Cohort now at 39 (per CLAUDE.md), sharded countries (UK/US/Germany/France via Convention #79 candidate) impose a NEW class of bootstrap consideration — trigger's baseline audit one-liner doesn't yet handle sharded countries. Bootstrap sentinel `test_v42_bootstrap_source_canonical.py` may need extension | MAJOR |
| HK.6 | Sentinel summary table (lines 306-319) shows 5 codified + 4 queued + 2 special. Missing: Convention #14.1 bootstrap-source sentinel (which IS codified per Trigger #13 line 489); missing: v4.23 owner-attribution + alias-map sentinels (from CLAUDE.md ⭐ Denmark P28 closure); missing: Convention #56 sentinel via `test_ssi_data_sharding_invariants.py` (queued per CLAUDE.md next-item). Sentinel inventory drifted | MAJOR |
| HK.7 | No Trigger has been established for: 5-band Extreme classification changes (Phase 2A/B/C precedent), reclassify-vs-rescore workflow (§5bis in METHODOLOGY_DISCIPLINES), R7 dual-axis synchronisation (backend engine ↔ frontend renderer), cross-border enforcement gate (Discipline #36), ssi-data sharding onboarding (Convention #79 candidate). These are all landed disciplines with recurring drift risk | MAJOR |
| HK.8 | Convention #78 BINDING promotion (16 Jul 2026, 7/5-10 saturation) should have triggered an update to Trigger #4 (adding a locked decision to architecture memo). No entry logged. Verify against `V4_2_IMPLEMENTATION_ARCHITECTURE.md` (Phase 3 read) | MAJOR |
| HK.9 | Meta-rule (line 28-32) references `Convention #1 read-attestation` — but attests to canonical sources that themselves have drifted. For example, `V4_2_IMPLEMENTATION_ARCHITECTURE.md §7.X Per-page enhancement plan` is cited as authoritative — verify this file exists + has been kept current. Meta-rule integrity depends on it | MAJOR |
| HK.10 | Convention numbering internal reference: HK cites Convention #56 (SSI-ENN side, footer line 311). The convention register comprises SSI Index Disciplines #1..#39 candidate (rolling) + SSI-ENN Conventions #1..#78 BINDING (rolling). Reader without CLAUDE.md context can't disambiguate. Header should carry a "which convention register does this file follow" one-liner | MINOR |

**Refresh recommendation**: v2 refresh — mechanical additive updates (no rewrites needed). Additions: (i) update footer with 22 Jul 2026 timestamp; (ii) Trigger #14 addendum for Wave 2/3/4 closures (if operator confirms they were closure-memo-worthy); (iii) new Trigger #15 for 5-band classification changes; (iv) new Trigger #16 for reclassify-vs-rescore workflow; (v) new Trigger #17 for ssi-data sharding onboarding; (vi) sentinel summary table refresh with new codified sentinels; (vii) fix HK.4 voltage-tier count (mandatory data-correctness fix); (viii) explicit convention-register disambiguation banner in header.

### T2.1 — CONVENTIONS.md (Phase 2) — **overall severity: MAJOR**

Internal working-memory doc (SSI Index root — Jesuit label preserved OK per G1; verified 0 Jesuit refs in this file). Structurally rigorous convention register — 14 conventions + 1 sub-rule (14.1), sequential numbering enforced, each convention has stated sentinel, cross-references intact. Same problem as HOUSEKEEPING.md: no updates since 13 June 2026 despite five weeks of major landings.

| # | Finding | Severity |
|---|---|---|
| CV.1 | Header stamps `Established: 11 June 2026`; footer stamps `Last updated 13 June 2026`. Doc has been static since 13 Jun 2026 despite: Discipline #36 cross-border enforcement (25 Jun 2026), Phase 2A/B/C 5-band Extreme (25 Jun 2026), Discipline #37 defensive-coding (16 Jul 2026), Discipline #38 nested-field navigation (16 Jul 2026), R7 SFDR PAI Phase 4a-4e (16 Jul 2026), Convention #78 BINDING promotion (16 Jul 2026), Convention #79 candidate ssi-data sharding (18 Jul 2026), Wave 4 TERMINAL (21 Jul 2026). Register is 5 weeks stale | MAJOR |
| CV.2 | Register terminates at **Convention #14.1** with tagline "Next available convention number: **#15**". CLAUDE.md ⭐ block reveals conventions coined post-14.1: Convention #78 BINDING (channel-reuse taxonomy), Convention #79 candidate (grid-geo sharding, referenced in HOUSEKEEPING.md HK.6). **BUT** the #56-through-#79 gap likely reflects SSI-ENN's convention register, NOT SSI Index's. Line 5 header explicitly says "Conventions in this file are binding for the SSI Index repository...they do not replace SSI-ENN conventions". So the SSI Index convention chain is: **#1..#14 + #14.1** with next slot #15 — while SSI-ENN chain is: #56..#79+. Two independent registers. **Coherence problem**: Convention #4 in this doc IS Convention #56 (SSI-ENN) — this is stated as a cross-register import. Then convention refs like "Convention #78 BINDING" in CLAUDE.md — do these refer to SSI-ENN Convention #78 or an unpublished SSI Index Convention #78? Grep of Wave 4 closure YAMLs may clarify | MAJOR (coherence) |
| CV.3 | Missing all post-13-Jun-2026 methodology landings: (i) Convention #15 candidate: 5-band classification-band schema change (bumped from 4-band to 5-band 25 Jun 2026); (ii) Convention #16 candidate: reclassify-vs-rescore discipline (Phase 2C — targeted binning, no R_median recompute); (iii) Convention #17 candidate: connecting-power-lines invariant (per v4.23 gap audit); (iv) Convention #18 candidate: R7 dual-axis synchronisation (backend ↔ frontend); (v) Convention #19 candidate: cross-border enforcement discipline (formalizes SSI Index Discipline #36); (vi) Convention #79 candidate: ssi-data automatic sharding (per CLAUDE.md ⭐ block; also referenced in HK.6 as missing) | MAJOR |
| CV.4 | Convention #2 cross-doc consistency table (lines 92-102) is materially stale. Key values pinned in table: `101 variables`, `4,293 substations` (Italy), `35 Italy DATA_SOURCES`. Post-Wave-4 Italy is **51,910 substations**; cohort is 796,121; variable count needs re-audit against 11-modifier register + W1-W10. **This is the convention that's SUPPOSED to prevent drift** — but the table itself has drifted. Meta-drift | CRITICAL |
| CV.5 | Convention #14.1 (bootstrap-source largest-canonical) currently pinned to 15 countries baseline (line 555). Wave 2/3/4 added 24 more; the sentinel `test_v42_bootstrap_source_canonical.py` needs pins for all 39. Bootstrap sentinel is only guarding half the fleet | MAJOR |
| CV.6 | Convention #7 (data-layer anchoring for per-substation values) was locked to prevent hardcoded numbers in SVGs. But R7 SFDR PAI phase-4a discovery surfaced a related class of bug: `assess_esg_readiness()` treating missing fields as populated (per CLAUDE.md ⭐ block, Discipline #38). This may warrant a new Convention #20 candidate — extending Convention #7 to backend readiness assessors | MAJOR |
| CV.7 | Convention #12 (voltage-tier trichotomy) is same drift class as HK.4. Line 428: `Italy: 475 EHV / 3,035 HV / 783 distribution-tier`. Post-Wave-4 Italy tier counts will differ. Coherent-with-HOUSEKEEPING but coherent-in-being-wrong | MAJOR (matches HK.4) |
| CV.8 | Convention #1 attestation table (lines 24-40) references canonical sources. Verify each still exists at declared path + last-touched dates aren't grossly stale. Specifically: `V4_2_IMPLEMENTATION_ARCHITECTURE.md` (Italy Pilot), 7 methodology briefs, LITERATURE_EVIDENCE_REPORT_v4_2.md, SSI_v4_2_Supporting_Paper.html, PUBLICATION_STRATEGY_v4_2.md. These are the Convention #1 read-attestation targets; if any is stale, the whole attestation chain is broken | MAJOR (traceability) |
| CV.9 | No explicit Convention numbering for the SSI Index vs SSI-ENN register split. Header line 5 gestures at it ("Conventions in this file are binding for the SSI Index repository...they do not replace SSI-ENN conventions"). But readers of CLAUDE.md see numbers like #56/#60/#63/#67/#75/#78 — should be explicit which register each convention comes from at reference time. **Cross-register reference format** should be codified (e.g. "SSI Index Convention #4" or "SSI-ENN Convention #56") | MINOR (convention-of-conventions) |
| CV.10 | Sentinel-codified matrix (bottom of doc lines 556-559): 9 sentinels codified, 3 queued (#6, #11, #12). Need to verify: (i) each codified sentinel still passes on the CURRENT cohort (not just June 2026 state); (ii) queued sentinels haven't inadvertently been promoted; (iii) Convention #79 candidate sentinel `test_ssi_data_sharding_invariants.py` (per CLAUDE.md next-item) should be added to this table when codified | MAJOR |

**Refresh recommendation**: v2 refresh — additive, mechanical. (i) update footer with 22 Jul 2026 timestamp; (ii) add Convention #15-#20 candidates for post-13-Jun-2026 landings (5-band, reclassify-vs-rescore, connecting-power-lines, R7 dual-axis, cross-border enforcement, extended data-anchoring); (iii) update Convention #2 cross-doc table with post-Wave-4 numbers (51,910 Italy, 796,121 cohort, 11 modifiers, actual DATA_SOURCES range); (iv) update Convention #12 voltage-tier example with post-Wave-4 Italy counts (mandatory data-correctness); (v) update Convention #14.1 country baseline pin to 39 countries; (vi) explicit convention-register disambiguation banner in header (per CV.9); (vii) verify Convention #1 attestation-chain source docs still exist and are current.

### T1.3 — REPORTS_FRAMING_KB.md (Phase 3) — **overall severity: MAJOR** (mixed — §8bis excellent, §4 requires scrub)

External-facing framing register (`Report Production/00-Framing/`; published as PDF; canonical companion to the 9-report editorial spine). G1 Jesuit-scrub rule applies. Actually **materially fresher than the anchor docs** — §8bis was updated 21 Jul 2026 (yesterday) with Discipline #42+#43 candidate + #44 candidate landing Wave 4 TERMINAL closure state. **Split severity**: §8bis is EXCELLENT (freshest doc in the whole audit set); §4 Rules N/M and §7 editorial spine have the drift + scrub issues.

**Interesting nuance re G1 Jesuit-scrub**: §4 Rule N (line 301) *itself* codifies the internal/external naming convention — "In every external-audience publication...the discipline is referenced as *a structured analytical writing discipline*". So this doc DOCUMENTS the rule but doesn't apply the rule to itself. Same class of "REPORTS_FRAMING_KB is a *framing register* not a *publication*" argument that plausibly justifies keeping the tradition-lineage citations for drafters — BUT the doc is exported to HTML/PDF and lives in `Report Production/00-Framing/` (the external-narrative hub, mirror of published deliverables). **Operator directive scope 22 Jul 2026** is unambiguous: *"not to be mentioned in any external facing deliverables"* — the framing register is a deliverable that external evaluators, peer institutions, and EU-funding reviewers CAN see. Scrub required.

| # | Finding | Severity |
|---|---|---|
| RFK.1 | **🚨 SCRUB REQUIRED per Global Rule G1** — 7 Jesuit references across §4 Rule N. Rule N block (lines 276-301) is the CANONICAL codification of the discipline — carries full tradition-lineage citation (Ignatius of Loyola, Spiritual Exercises 1548, Ratio Studiorum 1599, Suárez / Vázquez / Toledo / Sánchez casuistry, Pedro Arrupe, magis / examen / contemplation-in-action, Pascal Provincial Letters, Bayesian probabilism). **Refresh action**: rewrite §4 Rule N as "Discipline N — Structured Analytical Writing" with the same six operational features preserved unchanged. Retire the tradition-lineage authority anchor from this external-facing register. Preserve the internal/external naming convention paragraph (line 301) but reframe it: the drafter-facing lineage lives ONLY in METHODOLOGY_DISCIPLINES.md + CONVENTIONS.md (which per G1 keep Jesuit terminology) + CLAUDE.md — never in a doc that ships as PDF. | CRITICAL |
| RFK.2 | Rule N's own internal/external convention paragraph (line 301) declares that pre-21-June-2026 external artefacts "are scrubbed on first available refresh cycle". The Rule N declaration was made 21 Jun 2026; 31 days have passed; this doc is one of those external artefacts and hasn't been refreshed. **Meta-drift**: the doc contains a self-declared scrub obligation that it hasn't fulfilled on itself. | CRITICAL |
| RFK.3 | §4 Rules A-O now spans A-O (15 rules) — Rules M (Mosaic Theory, 19 Jun 2026) + N (Jesuit Style, 19 Jun 2026) + O (RESILINK subject-matter-relevance, per Task #104) all landed post-v2 refresh. Doc header still says "Rules A-L" (line 191). Header vs content drift | MINOR |
| RFK.4 | §7 editorial spine schedule (line 476): July 2026 A1/SB-01 is present-tense "lands well before LIFE-RESILINK 22 September 2026". SB-01 shipped 4 Jul 2026 (per repo commit history + tasks #47+); we are now in Jul 22 2026; A2 Nov 2026 is next scheduled ~4 months out. **Two problems**: (i) LIFE-RESILINK references remain in §7 timing notes (line 493) — but Task #105 (Option C) scrubbed all LIFE-CCA + HORIZON CL5 references from external-audience docs. This is external-facing (in `00-Framing/`); scrub incomplete; (ii) §7 doesn't record SB-01 as shipped, doesn't schedule the D2 Aug 2026 or B1 Sep 2026 slots as imminent | MAJOR (both scrub-incomplete + schedule-stale) |
| RFK.5 | §7 title-tag rows show "LIFE-RESILINK" + "LIFE-CCA / HORIZON CL5" verbatim in timing notes despite Task #105 scrub completion. `grep -c "LIFE-\|RESILINK\|HORIZON CL5"` on this file returns non-zero — confirm sweep incompleteness on next diff | MAJOR (Rule O scope) |
| RFK.6 | §0 "instrumentation rule" (line 11) frames every report as "instrument to *increase the probability of winning at least one EU funding call*". This is the doc's foundational orientation. Post-Task #104+#105 scrub, `RESILINK` + `LIFE-CCA` + `HORIZON CL5` references removed from external-audience deliverables — but §0 keeps the EU-funding-instrument frame intact (which is fine per Rule O — the STRATEGY stays internal to the KB). Verify Rule O's scope doesn't require §0 rewrite | MINOR (Rule O clarification) |
| RFK.7 | §8bis is **the freshest section in this doc** — updated 21 Jul 2026 with Discipline #42 (compact-JSON writes) + #43 candidate (sharding) + #44 candidate (retroactive alias-map). Well-anchored to codebase state; cross-references Convention #79 candidate + Convention #78 §4bis.4. **This is the section that CLAUDE.md's ⭐ block sync-refreshes with**. Very well done here — the coherence pattern shows the framing register CAN be kept current. **The rest of the doc should follow §8bis's cadence** | OK |
| RFK.8 | §8bis Disciplines #36 + #40 + #41 + #42 + #43 + #44 codified. Missing (candidates that could graduate): Discipline #45 (Wave 4 R4/R5/R6 institutional-data-proxy enrichment) is queued in "Future discipline-track entries" (line 656) but not codified — should be promoted given empirical anchor (SGU + SCB + LNEC + APA + INE + DGEG + INGV MPS04 + ISTAT + ISPRA + GSE + NIED J-SHIS + BRGM + INSEE + ONPE + ADEME + AEA Barómetro + MITECO across 6 countries per CLAUDE.md ⭐ block); also missing: R7 SFDR PAI Phase 4a-4e discipline (16 Jul 2026 landing per CLAUDE.md — should have its own discipline entry for the 7-axis backend↔frontend synchronization discipline). Discipline-track cadence should catch up | MAJOR |
| RFK.9 | §5.6 W1-W10 5/1/1/3 mesh referenced heavily. Verify against W1-W10 FC v2 (Phase 4 upcoming read) — coherence at mesh-rule layer | (verify Phase 4) |
| RFK.10 | §10 "Open items" (line 675) still lists "Backfill HORIZON CL5-2027-07 D3-26 + D3-28 content" as a TODO. Task #105 scrub says these should be removed from external-audience deliverables. Two possible resolutions: (a) HORIZON CL5 references retire from §10 too (Rule O-strict reading — this file IS external-facing); (b) §10 as internal-drafter-only task list stays (Rule O-lax reading — TODO markers are for drafters, not readers). Operator to disambiguate on doc-refresh | MAJOR (Rule O clarification, sister to RFK.6) |
| RFK.11 | Version stamp "v2 — refreshed 18 Jun 2026 deep night" (header line 4) + footer stamp "§8bis refreshed 21 July 2026" (line 687). Doc is bi-versioned — §8bis is fresh, rest is 5 weeks stale. Version-stamp discipline should acknowledge partial-refresh state ("v2.1 — §8bis at 21 Jul 2026, rest at 18 Jun 2026, next full refresh planned for X"). Also `v2` bump to `v3` warranted on next full refresh given the scope of pending changes (RFK.1 scrub + RFK.3 A-O rules extension + RFK.4 schedule refresh + RFK.5+6+10 Rule O scope + RFK.7 candidate-#45 graduation) | MINOR |
| RFK.12 | Cross-refs to CLAUDE.md are one-way. CLAUDE.md ⭐ blocks land daily and cascade downstream; this doc's §8bis follows CLAUDE.md's convention register (see line 660: "cross-reference: ikengassiindex.github.io CLAUDE.md Convention #79 candidate"). Good pattern — same pattern should extend to Discipline #45 candidate + R7 SFDR PAI discipline. **The cross-ref discipline is working**; it just needs to run more often | OK |

**Refresh recommendation**: v2 → v3 refresh — this is a bigger job than the anchor docs. (i) rewrite §4 Rule N as "Discipline N — Structured Analytical Writing" retiring Jesuit lineage from THIS external-facing register (Global Rule G1 CRITICAL); (ii) extend §4 header from "Rules A-L" to "Rules A-O"; (iii) sweep §7 + §10 + §0 for LIFE-CCA + HORIZON CL5 + RESILINK references per Task #104+#105 scope (Rule O completeness); (iv) refresh §7 editorial spine: SB-01 shipped, D2 Aug next, add Wave 2/3/4 completion narrative context, dedupe LIFE-RESILINK timing note; (v) codify Discipline #45 (Wave 4 R4/R5/R6 enrichment) + R7 SFDR PAI discipline in §8bis (currently only queued in "future entries"); (vi) header version bump to v3 + partial-refresh disclosure. **This is a substantial rewrite job** — larger than any of Phase 1-2 docs.

### T2.3 — LITERATURE_EVIDENCE_REPORT_v4_2.md (Phase 3) — **overall severity: MINOR** (best-shape doc yet)

Internal-facing academic-evidence audit doc (SSI Index root — G1 Jesuit-scrub not applicable; verified 0 Jesuit refs). **Best-shape doc in the audit set so far** — carries the four Convention #6 conflict-resolution literature reviews as explicit `[CONFLICT_RESOLVED_VIA_§X.Y]` sections (Trigger #8 discipline empirically honoured), Sansavini et al. 2025 iScience headline finding, Reckien et al. 2023 Nature Climate Change framework anchor, 108 KB / 1073 lines of substantive literature review across 6 modifier families + 12 sections. Structurally sound.

| # | Finding | Severity |
|---|---|---|
| LER.1 | Header: `Status: Working draft v1` + `Authored: June 2026`. Consistent — this is the peer-review-preparation self-audit for the v4.2 additions. Doc is not a rolling register (like AUDIT_BASELINE.md); it's a point-in-time literature snapshot. That's fine — but should be marked as such rather than as "working draft" (which implies imminent refresh) | MINOR |
| LER.2 | Four Convention #6 conflict resolutions landed here as promised in HOUSEKEEPING.md Trigger #8 (§5.6 W9 mesh + §2.1.1 d15 PGRA + §2.2.1 d10 wildfire + §2.3.1 d11 freezing-rain). Sections carry `[CONFLICT_RESOLVED_VIA_§X.Y]` markers per Convention #6 §5-6 procedure. Empirical trail intact | OK |
| LER.3 | §1 headline finding pins Sansavini et al. (2025) iScience — direct peer-reviewed validation of energy-justice framing at Italian per-substation level. §5 pins Reckien et al. (2023) Nature Climate Change — framework the W1-W10 governance gate operationalises. Both are strong publication-strategy anchors. Should remain intact | OK |
| LER.4 | No post-June-2026 landings reflected: R7 SFDR PAI Phase 4a-4e (16 Jul 2026 landing) is not in Family F ESG framework consolidation. R7 was previously the cyber modifier only; post-Phase-4a it's dual-axis (cyber modifier + SFDR PAI ESG-disclosure axis per FC v3 §14 subsection 13.7). Family F literature currently doesn't reflect this. If a v2 refresh happens, the SFDR PAI axis needs peer-reviewed / regulatory anchors — SFDR RTS Annex I, EFRAG ESRS S1-S4 alignment, EBA GL on ESG risks, ECB guide on climate-related and environmental risks | MAJOR (post-doc-authoring landing) |
| LER.5 | Zero mentions of Wave 2 / Wave 3 / Wave 4 / Convention #78 / Convention #79 (0 grep hits). Cohort scale evolution (18k → 174k → 796k substations) doesn't affect the literature evidence per se (this doc validates the METHODOLOGY not the DATA), so this is fine. But a v2 refresh should note the post-June cohort expansion in §0 scope to keep the doc temporally anchored | MINOR |
| LER.6 | §12 net positioning verdict (line 1010+) claims v4.2 is "ahead of the curve" per 5 identified gaps G1-G5. Verify none of these gaps have been closed by June 2026-July 2026 literature (rapid-moving space — Duvat et al. 2026 WIREs Climate Change compound events; Nature Reviews Electrical Engineering 2026 wildfire/grid nexus already recent). Recommend rolling per-quarter literature scan to keep the "ahead of the curve" claim honest | MAJOR (positioning-freshness) |
| LER.7 | §11 "Sources cited in this report" (starts line 972) — verify each cited source URL is still live at retrieval; verify no primary sources have been retracted or superseded. Snapshot-time sources age over publication cycle | MINOR |
| LER.8 | §12.5 "Where v4.2 stays measured" (line 1032+) — the anti-overclaim discipline paragraphs. Explicitly names v4.2 as "Italy-pilot scoped" (line 1039) — but 5 weeks post-doc-authoring, cohort is now 39 countries × 796k substations. The Italy-pilot-scoped humility is no longer accurate as a factual claim; needs update to "cohort-wide-deployed with Italian-pilot-validated methodology" | MAJOR |
| LER.9 | Doc doesn't cross-reference the FC v3 (Complete Formula Construct Italy v3, upcoming Phase 4 read) or W1-W10 FC v2. Should — literature evidence report is downstream of FC (which codifies the math) and should cite the FC as the target of validation. Verify cross-refs on next refresh | MINOR (coherence) |
| LER.10 | Doc is a peer-review-preparation output. **Coherence question**: does this doc represent our commitment to publish? Task list shows PUBLICATION_STRATEGY_v4_2.md exists but isn't in current-session read set. If publication strategy has slipped (which is common in early-Foundation-stage work), this doc may position claims further ahead than the publication timeline supports. Verify against PUBLICATION_STRATEGY_v4_2.md on next full audit | MAJOR (publication-strategy coherence — verification needed) |

**Refresh recommendation**: v1.1 tail refresh + v2 target for Q4 2026. (i) mark header status as "point-in-time v1, snapshot 5-11 Jun 2026, next-scan Q4 2026" instead of "working draft v1"; (ii) add Family F R7 SFDR PAI dual-axis literature (SFDR RTS, EFRAG, EBA GL); (iii) §0 scope note post-June cohort expansion; (iv) quarterly rolling literature scan for §12 "ahead of curve" gaps G1-G5; (v) §12.5 anti-overclaim update ("Italy-pilot-scoped" → "cohort-wide-deployed with Italian-pilot-validated methodology"); (vi) URL freshness check on §11 sources; (vii) FC v3 cross-refs. Overall this doc is the freshest-in-shape of the audit set — most findings are MINOR or ADDITIVE rather than CRITICAL.

_(Phase 3 read pass complete; Phase 4 — FC v3 mathematical spine + W1-W10 FC v2 + Methodological Foundations PDF — next)_

---

## Cross-doc consistency findings

_(populated as pairs of docs are read together — checks for stale numbers,
convention-number drift, cohort-count mismatches, methodology version drift)_

---

## Refresh plan (populated after read pass complete)

_(deferred until findings register is populated + operator approves)_

---

## Reading progress log

| Phase | Docs | Status | Started | Completed | Findings count |
|---|---|---|---|---|---|
| P1 | Anchor (README + About + AUDIT_BASELINE) | ✅ complete | 22 Jul 2026 | 22 Jul 2026 | 31 (R×12 + A×9 + AB×10) |
| P2 | Discipline registers (METHODOLOGY_DISCIPLINES + HOUSEKEEPING + CONVENTIONS) | ✅ complete | 22 Jul 2026 | 22 Jul 2026 | 27 (MD×7 + HK×10 + CV×10) |
| P3 | Main methodology hub (REPORTS_FRAMING_KB + LITERATURE_EVIDENCE_REPORT) | ✅ complete | 22 Jul 2026 | 22 Jul 2026 | 22 (RFK×12 + LER×10) |
| P4 | FC v3 mathematical spine (228 KB HTML + W1-W10 FC v2 + Methodological Foundations PDF) | ⏸ paused for operator | — | — | — |
| P5 | Editorial + Data Bridge (EDITORIAL_CALENDAR + SSI_INDEX_X_SSI_ENN_DATA_BRIDGE) | pending | — | — | — |
| P6 | Competitive positioning trio (DIFFERENTIATION_ANGLES + SCORING_MATRIX + SCRAPE_KB) | pending | — | — | — |
| P7 | Per-country FC sample (Germany + France + Spain + UK to check cohort-scope FC coherence) | pending | — | — | — |
| P8 | SSI_Dashboard_Knowledge_Base_v19 (344 KB — largest doc in set) | pending | — | — | — |
| P9 | AUDIT_v4_0_2_PRE_v4_2_FOUNDATION.md (baseline for what v4.2 replaces) | pending | — | — | — |
| P10 | Coherence matrix + refresh plan (synthesise across all read docs; author refresh queue) | pending | — | — | — |

---

## Interim consolidation — Phase 1-3 complete (6 docs read, 80 findings logged)

### The pattern that emerges

Across the 6 docs read so far, **three distinct maintenance-tier states** are visible:

**Tier 1 — Fresh, well-anchored (2 docs)**
- **REPORTS_FRAMING_KB.md §8bis** (last refresh 21 Jul 2026): follows CLAUDE.md ⭐-block cadence for codebase disciplines; Discipline #36-#44 all codified with empirical anchors
- **LITERATURE_EVIDENCE_REPORT_v4_2.md** (point-in-time June 2026): peer-review self-audit; Convention #6 conflict-resolution sections empirically landed; Sansavini + Reckien headline anchors intact

**Tier 2 — Structurally sound but content-stale (3 docs)**
- **About_SSI_Index.md** (last refresh 21 Jun 2026): 9-commitment structure sound; counts stale (174k → 796k substation drift); Convention # register confusion (SSI-ENN #62 cited without SSI Index disambiguation)
- **METHODOLOGY_DISCIPLINES.md** (last refresh 12 Jul 2026): §5bis + §5ter fresh; Jesuit-scrub REQUIRED per G1 (26 refs, external-facing); post-25-Jun landings missing
- **HOUSEKEEPING.md** (last refresh 18 Jun 2026) + **CONVENTIONS.md** (last refresh 13 Jun 2026): internal working docs; no Jesuit issue; Convention #14 register 5 weeks behind CLAUDE.md; voltage-tier + cohort count references pre-Wave-4

**Tier 3 — Critical drift (2 docs)**
- **AUDIT_BASELINE.md** (last refresh 13 Jun 2026, self-declared "binding canonical baseline"): now materially wrong on every headline KPI; **truth-source ambiguity** with CLAUDE.md
- **README.md** (undated, v4.0.2-era snapshot): repo-side public README; 5-band + v4.2 formula + Wave 4 cohort scale all missing; **highest-visibility external drift**

### The four themes that cross every doc

**Theme 1: Truth-source ambiguity.** AUDIT_BASELINE.md self-declares as canonical baseline but hasn't been maintained; CLAUDE.md ⭐ block is the actual fresh source of truth. Docs contradict which is authoritative. **Resolution needed**: designate CLAUDE.md ⭐ block as canonical rolling anchor; retire AUDIT_BASELINE.md self-declaration or refresh it to match.

**Theme 2: Convention register split.** SSI Index Convention #1-#14.1 (CONVENTIONS.md) vs SSI-ENN Convention #56-#79 (CLAUDE.md). Neither disambiguates at reference time. About_SSI_Index.md and METHODOLOGY_DISCIPLINES.md cite "Convention #62" without prefix — external readers can't disambiguate. **Resolution needed**: codify reference format `SSI Index Convention #X` vs `SSI-ENN Convention #Y` in Convention #9 (or new Convention #15).

**Theme 3: Jesuit terminology scrub incomplete.** Operator directive 22 Jul 2026 locks external-facing scrub. METHODOLOGY_DISCIPLINES.md (26 refs) + REPORTS_FRAMING_KB.md (7 refs) both external-facing and both violate. **Resolution needed**: single-commit scrub sweep across `Report Production/00-Framing/` retiring Jesuit lineage from Rule N + rewriting as "Discipline N — Structured Analytical Writing"; internal docs (CLAUDE.md, HOUSEKEEPING.md, CONVENTIONS.md, KB) keep the lineage.

**Theme 4: Post-June-2026 landings not reflected.** Wave 2 (12 Jul) + Wave 3 (17 Jul) + Wave 4 TERMINAL (21 Jul) + Convention #78 BINDING + Convention #79 candidate + R7 SFDR PAI Phase 4a-4e + Discipline #37/#38/#39 candidate + 5-band Extreme are missing from 4 of 6 docs. **Resolution needed**: single-commit multi-doc refresh once operator confirms scope + Convention register format.

### Recommended proceed-order

Given the depth of context now built, three routes for the operator:

**Route A — Continue read pass (Phase 4-9)** before any refresh. Complete diligent audit-first-then-fix discipline (Task #268 anchor). Estimated 3-4 more sessions (FC v3 mathematical spine is largest reading commitment). Refresh queue starts full but risk of finding surprises in FC/KB that change refresh plan is preserved.

**Route B — Land Phase 1-3 refresh** while continuing Phase 4-9 read pass in parallel. Highest-impact fixes land immediately (AUDIT_BASELINE.md v2 rewrite, README.md full rewrite, Jesuit scrub, count corrections) while heavier docs read. Trades some coherence risk for velocity.

**Route C — Author single refresh plan** based on Phase 1-3 findings alone, defer FC + KB reads. Assumes the mathematical spine + KB are internally consistent since they haven't drifted (both are internal working docs, not exported). Fastest to close — but leaves Phase 4-9 gaps if surprises exist.

**Recommendation**: Route A conservative continuation given Task #268 audit-first discipline anchor. Operator to select.

---

### T1a.1 — SSI_v4_2_Complete_Formula_Construct_Italy_v3.html (Phase 4) — **overall severity: MAJOR** (structurally good, mathematical drift)

The mathematical spine — 228 KB / 2260 lines. Internal reference-docs (in `SSI_v4_2 Italy Pilot/reference-docs/`), G1 Jesuit-scrub not applicable (0 Jesuit refs verified). Has strong bones: §14 ESG Reporting Framework R1-R7 CONSOLIDATED v3 is codified (line 276 TOC + line 1920 section marker), §13.7 R7 SFDR PAI section exists with "NEW in v3" tag (line 2082, coherent with CLAUDE.md ⭐ block anchor), ship-narrative LP-1..LP-12 tail-anchored with commit hashes + Trigger #14 cross-reference. **But** carries a critical mathematical-spine drift: master equation still displays v4.0.2 multiplicative-only shape.

| # | Finding | Severity |
|---|---|---|
| FC.1 | **Master equation at line 396** displays: `R_final = soft_clip_upper( R_base × F_topo × C_mult × R6_rest × R6_seis × Cyber_factor )` — this is the v4.0.2 multiplicative form. Per CLAUDE.md's own cited form + Phase 2A/B/C 5-band closure, the v4.2 form is: `R_final = soft_clip_upper(R_base × Π mult_i) + Σ (add_i − 1.0)` with additive R6c_flood producing R_median ∈ [0, 1.30]. **Mathematical spine drift on the master equation** — reader coming from CLAUDE.md sees a formula shape that doesn't match. FC v3 shows the multiplicative baseline WITH R6_rest + R6_seis but not the ADDITIVE R6c_flood layer that enables Extreme band. Need to reconcile | CRITICAL |
| FC.2 | **§13.9 pins Italy fleet at 4,293 substations, 59 fields** — same drift pattern as every June-2026 doc. Post-Wave-4 Italy is 51,910 substations. Header claims "Complete Formula Construct" — completeness needs updating | MAJOR |
| FC.3 | §14 R1-R7 register is comprehensive but R7 heading at §13.6 says "R7 — Cybersecurity Exposure Assessment" AND §13.7 says "R7 — SFDR Principal Adverse Impact Statement (Infrastructure Module) NEW in v3". **Two §13.X sections both claim R7**. This is the DUAL-AXIS R7 architecture (cyber modifier + SFDR PAI ESG-disclosure axis) — but the doc doesn't lead with that framing. Reader sees §13.6 R7=Cyber, §13.7 R7=SFDR PAI, and may not realize both are simultaneously true. Needs explicit R7-dual-axis framing at §13.0 header + §14 opener | MAJOR |
| FC.4 | Master equation modifier chain (line 396) lists `R6_rest × R6_seis × Cyber_factor` but master-equation-section body (line 871) lists `R6_rest × R6_seis × Cyber_factor` **without R6c_flood + R6d_wildfire + R6e_winter**. Line 1232 modifier table also displays 4-modifier v4.0.2 shape (R3 Consequence + R4 F_topo + R6 + R7 Cyber). **The v4.2 modifier registry (11 modifiers per CLAUDE.md) is not integrated into the master equation display anywhere** — Line 1044 R6e_winter is described in isolation, R6c/R6d elsewhere, but no unified master-equation-with-all-11-modifiers block exists. Structural documentation gap | CRITICAL |
| FC.5 | 5 mentions of "Extreme" but all in "extreme cold/extreme projections" context (R6e_winter narrative, cold extremes, projection clipping). **Zero mentions of 5-band Extreme classification band** (Phase 2A/B/C 25 Jun 2026 landing). Doc classification section (H2 "Classification & Output Schema") predates Phase 2 5-band cascade. Need to add Extreme band [1.00, 1.30] card | CRITICAL |
| FC.6 | 4 mentions of "cross-border" / "bounds.json" / "Discipline #36" / "point-in-polygon" — Discipline #36 (18 Jun origin, 25 Jun anchored) is **not codified in FC v3 §12 or §13**. FC v3 doesn't reference the cross-border discipline as a preprocessing invariant on the ingestion side. HOUSEKEEPING.md Trigger #10 codifies voltage-tier trichotomy; FC v3 §12 could add cross-border invariant | MAJOR |
| FC.7 | 8 mentions of "5/2/3" mesh in various W1-W10 contexts (Convention #6 §5.6 pre-resolution). LITERATURE_EVIDENCE_REPORT §5.6 resolved to 5/1/1/3 (5 Published + 1 Published-baseline + 1 Baseline-only + 3 Commercial). FC v3 doesn't reflect the mesh resolution — coherence broken with LITERATURE_EVIDENCE_REPORT + HOUSEKEEPING.md Trigger #8 table | MAJOR (coherence — §5.6 conflict resolution not cascaded) |
| FC.8 | Ship-narrative tail (LP-1..LP-12) cites `V4_2_LIVE_SHIP_CLOSURE_2026-06-18.md` as canonical SoT + `HOUSEKEEPING.md Trigger #14` as procedural pattern + `Knowledge Base v19 §52` as operating-memory entry. This is EXCELLENT cross-doc anchoring — enables backwards-tracing from any doc to the ship state that produced it. But the tail also self-declares: **"This FC v3 has not been modified by the ship; the closure marker …"** — meaning FC v3 as a document is treated as pre-ship canonical and DOES NOT roll with subsequent Wave 2/3/4 landings. **This is important**: FC v3 is a POINT-IN-TIME reference-doc, not a rolling register. The right refresh cadence is v3 → v3.1 (add 5-band + R7 dual-axis + Convention #78 + Wave 2/3/4 count updates) → v4 (major refresh alongside v5.0 methodology bump). Not daily-rolling | MAJOR (understanding refresh cadence — sets expectations for refresh plan) |
| FC.9 | 6 refs to Wave 2/3/4 + Convention #78 + Convention #79 + SFDR PAI + 39-country context. Sparse coverage of post-June-2026 landings — matches expected point-in-time-doc shape from FC.8 | MAJOR (part of FC.8 refresh event) |
| FC.10 | Data Sources — Complete Registry claims "46 Verified — 35 v4.0.2 + 11 v4.2" (H2 header). Verify against actual current source count post-Wave-4 (v4.23 added multi-country sources + R7 SFDR PAI adds Re_normalised gate data source). Registry needs count refresh + potential source additions | MAJOR |
| FC.11 | Registry check surfaced mixed notation: R6a + R6b + R6_seis + R6_rest + R6c + R6d + R6e + R6_total all appearing. Inconsistent modifier naming — some places "R6_seis" some "R6_seismic" some "R6b". Should canonicalize per Convention #2 cross-doc consistency table (target: R6a_rest / R6b_seis / R6c_flood / R6d_wildfire / R6e_winter per FC v3 §13 subsections) | MINOR (nomenclature hygiene) |

**Refresh recommendation**: v3 → v3.1 refresh. (i) master equation display at line 396 + 871 + 1232 modifier table extended to full 11-modifier v4.2 shape with additive R6c_flood term (CRITICAL); (ii) §13.0 opener + §14 header add R7 dual-axis explicit framing (cyber modifier + SFDR PAI axis simultaneously); (iii) new §5b-Extreme card for 5-band classification (Extreme [1.00, 1.30]); (iv) §12 add cross-border discipline reference (Discipline #36 anchor); (v) §5.6 mesh update 5/2/3 → 5/1/1/3 per Convention #6 resolution; (vi) §11 registry count refresh + source additions post-Wave-4; (vii) Italy fleet 4,293 → 51,910 with backward-compat note (4,293 was Stage 4 validation baseline; 51,910 is current fleet); (viii) v3.1 header stamp + ship narrative addendum LP-13..LP-N for Wave 2/3/4 closures. **This is substantial mathematical documentation work** — larger than any Phase 1-3 refresh.

---

### T1a.2 — SSI_v4_2_W1_W10_Substation_Formula_Construct_Italy_v2.html (Phase 4) — **overall severity: MAJOR**

W1-W10 substation formula construct — 62 KB / 602 lines. Internal reference-docs (0 Jesuit refs). Simpler doc than FC v3; carries H2 "Audit-state classification — 5 / 1 / 1 / 3 split (4-tier, mesh resolution)" — **header is correct** per Convention #6 §5.6 resolution. But body has 1 mention each of the historical 5/2/3 + 6/1/3 splits preserved as narrative. Zero mentions of the current 5/1/1/3 in body.

| # | Finding | Severity |
|---|---|---|
| W10.1 | Header correctly states "5/1/1/3 split (4-tier, mesh resolution)" per Convention #6 §5.6 resolution. Cross-doc coherent with LITERATURE_EVIDENCE_REPORT §5.6. ✅ | OK |
| W10.2 | Body still carries 1 mention of `5/2/3` + 1 mention of `6/1/3` — these are the pre-resolution split variants. Should either: (a) retire completely from body; or (b) preserve as `[HISTORICAL — superseded by §5.6 mesh resolution — CONFLICT_RESOLVED_VIA_LITERATURE_EVIDENCE_REPORT_§5.6]` markers with cross-ref | MAJOR (coherence) |
| W10.3 | Grep for "5/1/1/3" in doc body returns 0 — the current mesh is only in the header, not woven into worked examples or validation hooks. **Header-body coherence gap** — reader sees correct header, then body prose that still describes 5/2/3 or 6/1/3 | MAJOR |
| W10.4 | Doc scope pinned to Italy pilot (title: "Substation Formula Construct (Italy)"). Zero Wave 2/3/4 / Convention #78/#79 refs — consistent with point-in-time reference-doc shape per FC.8. Need cohort-generalization note in scope block: "W1-W10 methodology validated on Italian pilot fleet; extends to 39 OECD cohort per V4_2 IMPLEMENTATION ARCHITECTURE trigger #6 cohort-replication" | MAJOR |
| W10.5 | Validation hooks at doc tail (W-T1..W-T5) show 4 "To install" + 1 "Stage 4 E4 PASS (radius-based test, 95.5%) — aligned". **4 of 5 validation hooks still uninstalled** as of doc last touch (June 2026). Verify against current codebase state; some may have landed via Stage 4 completion + Wave 2/3/4 batch reruns | MAJOR (verify against codebase) |
| W10.6 | External event battery reference at tail (E2 L'Aquila 2009, E3 Amatrice 2016, E4 Sardegna 2021, E5 Sicilia 2023, E6 Emilia-Romagna 2023, E7 Mezzogiorno 2024 ARERA + ISTAT) — **BUT** Task #37 was "HIT-A3 — Swap Mezzogiorno 2024 out of 7/7 PASS battery". Task completed. Verify battery composition current; Mezzogiorno 2024 may have been swapped out but this doc still references it | MAJOR (Task #37 sync gap) |
| W10.7 | H2 "Worked examples — two substations (real values)" — verify these worked examples are still valid with current L1-L4 data. Wave 4 spatial-join enrichment + per-substation interpolation regression (Tasks #423-#450) may have shifted per-substation values | MAJOR (verify data freshness) |
| W10.8 | No cross-ref to CLAUDE.md Convention #78 BINDING taxonomy or Convention #79 candidate sharding (naturally, both post-doc-touch). Point-in-time doc shape — refresh cadence sister to FC v3 | MAJOR (part of point-in-time refresh event) |

**Refresh recommendation**: v2 → v2.1 refresh. (i) reconcile body 5/2/3 + 6/1/3 mentions with 5/1/1/3 canonical per header (mark historical or retire); (ii) add scope-block cohort-generalization note; (iii) validation hooks W-T1..W-T5 status refresh against current codebase; (iv) Mezzogiorno 2024 event battery composition update per Task #37 close; (v) worked-example real-values refresh vs current L4 data; (vi) v2.1 header stamp + refresh note. Same point-in-time refresh cadence as FC v3 v3.1.

---

### T1a.3 — SSI Index v4.2 Methodological Foundations PDF (Phase 4) — **overall severity: MAJOR** (external — needs pre-submission refresh)

*"SSI Index v4.2 — Methodological Foundations and Anti-Maladaptation Discipline for Italian Distribution Substation Resilience"* — 283 KB PDF (`file:///` path shows source is `SSI_v4_2_Supporting_Paper.html` on operator's Mac). External-facing — labelled `WORKING PAPER — PRE-PRINT DRAFT V1 · JUNE 2026`; drafted for arXiv / SSRN submission + LIFE-RESILINK Annex C + Foundation Charter D7.6 governance. G1 Jesuit-scrub applies (0 refs verified — paper pre-dates Rule N codification 19 Jun 2026, so no scrub needed by chronology).

| # | Finding | Severity |
|---|---|---|
| MF.1 | **6/1/3 audit-state split** codified at page 2 abstract: "published with a 6/1/3 audit-state split: six axes computable from public data (W1, W2, W3, W4, W8, W9); one baseline-only (W5); three commercial-extended (W6, W7, W10)". Convention #6 §5.6 resolution (25 Jun 2026 post-doc) locked 5/1/1/3. **Paper carries pre-resolution mesh — CRITICAL for submission**: if paper is submitted to arXiv/SSRN with 6/1/3, and dashboard runs 5/1/1/3, peer reviewer + LP-DD reviewer both see cross-doc inconsistency. **Must refresh before submission** | CRITICAL |
| MF.2 | Italy fleet: 4,293 substations — same drift class, 8 mentions across paper. Post-Wave-4 = 51,910. Paper is Italian-pilot calibration doc; the 4,293 is the STAGE 4 validation cohort — could be preserved as "Stage 4 validation baseline (n=4,293)" with footnote "post-v4.23 refresh cohort n=51,910 as of 21 Jul 2026" — same disambiguation pattern as About_SSI_Index.md A.2 | MAJOR (disambiguation needed) |
| MF.3 | 4 mentions of RESILINK / LIFE-CCA / HORIZON CL5 / LIFE-RESILINK — Task #104 (RESILINK scrub) + Task #105 (LIFE-CCA + HORIZON CL5 scrub) targeted "external-audience docs". Paper is external-facing (arXiv / SSRN target). **BUT** paper's front matter cites "Fondazione SSI Index (Naples, in formation) · LIFE-RESILINK consortium" as institutional attribution + "LIFE-RESILINK Annex C" as target of the paper's evidentiary use. **This is different from marketing-copy RESILINK refs**: it's authorship consortium attribution + specific-target attribution for the paper's citational scope. Analogous to REPORTS_FRAMING_KB §0 keeping EU-funding-instrument frame internal while scrubbing per-report copy. **Rule O scope needs operator disambiguation for research paper drafts vs dashboard/report ships**. Suggest: keep in front-matter as authorship attribution + specific-target Annex C reference; scrub from body prose if any | MAJOR (Rule O scope clarification pending) |
| MF.4 | 5 SFDR PAI mentions in paper — the R7 SFDR PAI framework is contemplated in the paper (June 2026, pre-Phase-4a-e which was 16 Jul 2026). Concept-to-implementation sequence coherent. But paper doesn't yet reflect the R7 dual-axis (cyber modifier + SFDR PAI ESG-disclosure axis) that FC v3 §13.6 + §13.7 codify. Refresh should extend R7 section to note dual-axis + reference FC v3 §14 subsection 13.7 as the canonical anchor | MAJOR |
| MF.5 | 0 mentions of 5-band Extreme classification — expected (paper is 8 Jun 2026, pre-Phase-2A/B/C 25 Jun 2026). Refresh must add 5-band card + rewrite classification section to reflect Extreme [1.00, 1.30] + note the additive R6c_flood modifier as the source of R_median > 1.0 values | CRITICAL (pre-submission) |
| MF.6 | 0 mentions of Wave 2/3/4/Convention #78/79/v4.23 — expected (paper is 8 Jun 2026 snapshot). Refresh must add: (a) v4.23 cohort expansion narrative in §1 Introduction ("v4.2 as instantiated at 39 OECD cohort × 796,121 substations as of Jul 2026 following Wave 2/3/4 ingestion cycles"); (b) Convention #78 BINDING channel-reuse taxonomy note in methodology section; (c) Convention #79 candidate sharding note as data-artifact-scale ceteris paribus | MAJOR (pre-submission) |
| MF.7 | 0 mentions of Discipline #36 cross-border enforcement — the paper predates the discipline codification. Given the paper cites per-substation-scale calibration as the analytical advantage, Discipline #36 (which validates cross-border integrity of per-country canonicals) is essential methodology-integrity infrastructure. Refresh should add data-integrity infrastructure paragraph in §2 Methodology or §3 Data | MAJOR (pre-submission — makes per-substation claims defensible) |
| MF.8 | Contribution structure C1-C8 (5 primary + 3 secondary) is well-anchored. C5 mentions "6/1/3 audit-state split" — same MF.1 mesh drift, needs to become "5/1/1/3 4-tier mesh". C7 mentions "Radar 2, 10-axis W1–W10" — good. C6 mentions Re composite with Convention #56 — good but Convention # register needs disambiguation ("Convention #56" ambiguously refers to SSI-ENN #56 frozen_legacy_v1) | MAJOR |
| MF.9 | Paper metadata: `Draft prepared in support of LIFE-RESILINK Annex C · Foundation Charter D7.6 governance documentation · candidate pre-print upload (arXiv / SSRN)`. **Submission status verify**: is this paper still pre-submission, or has it been uploaded to arXiv/SSRN? If pre-submission, refresh MUST land before upload. If uploaded, paper is now historical snapshot + a v2 needs preparation. Operator to confirm status | CRITICAL (verify) |
| MF.10 | Front-matter authorship: `[Authors — to be confirmed before submission]` — author attribution TBD. Ship-critical — refresh must land author attribution before submission | MAJOR (submission-blocking) |
| MF.11 | Reader-flow anchor at pages 1-3: Abstract → §1 Introduction → §1.1 Contribution structure → §1.2 Positioning relative to the literature (cites LITERATURE_EVIDENCE_REPORT_v4_2.md [23] §12) → §1.3 Scope and limitations. Structure is peer-review-ready. Cross-refs to LITERATURE_EVIDENCE_REPORT are correct. Coherence with literature-evidence-report intact | OK (coherence) |

**Refresh recommendation**: **v1 → v2 major refresh required BEFORE arXiv/SSRN submission**. (i) 6/1/3 → 5/1/1/3 mesh update per Convention #6 §5.6 (MF.1 CRITICAL); (ii) Italy 4,293 → 51,910 with Stage 4 validation baseline footnote (MF.2 same as About A.2 pattern); (iii) Rule O scope clarification for research-paper front-matter attribution (MF.3, awaiting operator); (iv) R7 dual-axis extension (MF.4); (v) 5-band Extreme classification card (MF.5 CRITICAL); (vi) Wave 2/3/4 cohort narrative + Convention #78/#79 methodology notes (MF.6); (vii) Discipline #36 cross-border data-integrity paragraph (MF.7); (viii) C5 update to 5/1/1/3 (MF.8); (ix) verify submission status (MF.9 CRITICAL); (x) author attribution landing (MF.10). **This is the single most refresh-critical doc in the audit** — it goes to arXiv, LIFE-RESILINK evaluator eyes, and peer reviewers. Cannot ship pre-submission unfreshened.

### T1.4 — EDITORIAL_CALENDAR.md (Phase 5) — **overall severity: MINOR** (freshest external-facing doc after RFK §8bis)

External-facing editorial calendar in `Report Production/00-Framing/`. G1 Jesuit-scrub applies. **Freshest external-facing doc in audit set** — v1.2 refreshed 13 Jul 2026 (Flash Brief F-01 addendum for July 2026 European heat episode). Verified 0 Jesuit refs, 0 RESILINK/LIFE-CCA/HORIZON CL5 refs (fully scrubbed per Task #104+#105 completion). Well-organized: default monthly schedule (Jul 2026 → Jan 2028), per-piece detail, collaboration windows, non-engagement principles, per-piece state-of-readiness flags, addendum for v4.23 engineering workstream (25 Jun 2026).

| # | Finding | Severity |
|---|---|---|
| EC.1 | Header stamps `v1.2 · updated 13 Jul 2026 · v1.1 baseline locked 19 Jun 2026`. Version-and-date discipline explicit. ✅ | OK |
| EC.2 | 0 Jesuit refs ✅ + 0 RESILINK/LIFE-CCA/HORIZON CL5 refs ✅ — G1 + Task #104/#105 scrub complete on this doc | OK |
| EC.3 | Cadence discipline: monthly, one report per calendar month from July 2026; responsive re-ordering explicit; flash briefs as off-cadence class. Mirrors REPORTS_FRAMING_KB.md §7 + SSI_INDEX_DIFFERENTIATION_ANGLES.md §3. Cross-doc coherence intact | OK |
| EC.4 | Addendum (25 Jun 2026) covers v4.23 gap-closure engineering workstream Q3 2026 → Q2 2027 in detail. Priority 1-5 country queue + effort estimates + coordination with report-writing spine. **But we're now in Jul 22 2026 — Q3 2026 already started; Priority 1 Canada should be actively in progress**. Per CLAUDE.md ⭐ block, Canada P1 completed as part of Wave 1 (see task history #147-#148). Addendum needs status-update note reflecting Wave 1-4 execution actually happened + methodology-brief follow-on annex status | MAJOR (execution vs plan gap) |
| EC.5 | Addendum cites cohort scale evolution: "174 k → 184-191 k substations after v4.3; 350-500 k after v5.0 DSO expansion". Post-Wave-4 actual is **796,121** substations across 39 countries. **The addendum's v5.0 projection has already been eclipsed by the v4.23 landing** — 350-500k was the v5.0 estimate; 796k is the actual Jul 21 2026 state. Refresh needed | MAJOR (empirical scale drift) |
| EC.6 | Per-piece row for **A1/SB-01 Jul 2026** — the Strategic Brief No. 01. Task list shows SB-01 shipped 4 Jul 2026 (via commit history + Task #47 "Ship-readiness sweep — version bump + PIN_AT_SHIP consistency + ship-date confirmation"). Verify calendar's status flag for SB-01 reflects shipped state, not pending | MAJOR (verify) |
| EC.7 | Per-piece row for **D2 Aug 2026** — Foundation Steward Model. Should be actively in draft or scope-locked given the ship date is next month. Verify against per-piece state-of-readiness flags | MAJOR (verify readiness) |
| EC.8 | Addendum §Auditability chain cites `Report Production/02-v4_3-gap-audit-2026-07/v4_3-gap-audit.md` as source. Verify this file still exists post-v4.23-rename cascade (Task #172 renamed v4.3 → v4.23 across documents + filesystem paths). Cross-ref may point to legacy path | MAJOR (post-rename verify) |
| EC.9 | Flash Brief F-01 addendum (v1.2, 13 Jul 2026) for July 2026 European heat episode. New class of publication. But no back-reference to how flash briefs feed into monthly cadence (e.g. do they cite specific modifier surface elements? do they trigger monthly re-ordering per Rule J?). Missing operational-mechanics section for the new class | MINOR |
| EC.10 | Cross-references §10 in DATA_BRIDGE + cross-references block at end of EDITORIAL_CALENDAR mirror well. Both cite REPORTS_FRAMING_KB.md §7 (editorial spine parent) + Rule J (cadence) + SSI_INDEX_DIFFERENTIATION_ANGLES §3 + DATA_BRIDGE §5. Cross-doc anchoring solid | OK |

**Refresh recommendation**: v1.3 tail refresh, mostly mechanical. (i) update Addendum cohort scale projections to actuals (350-500k → 796k); (ii) status-update note in Addendum reflecting Wave 1-4 executed + methodology-brief follow-on annex status; (iii) verify + refresh per-piece state-of-readiness flags for SB-01 (shipped) + D2 (next up); (iv) verify v4.3 → v4.23 rename cascade completeness in cross-refs; (v) flash-brief operational-mechanics section; (vi) v1.3 header stamp. **This is the fastest refresh in the audit set** — half a session's work.

---

### T1.5 — SSI_INDEX_X_SSI_ENN_DATA_BRIDGE.md (Phase 5) — **overall severity: MAJOR** (architecture spec — point-in-time doc)

External-facing architecture spec (`Report Production/00-Framing/`), G1 Jesuit-scrub applies. Verified 0 Jesuit refs ✅. 2 LIFE-RESILINK refs surfaced — need Rule O-scope disambiguation. Doc is v1 authored 18 Jun 2026 evening — POINT-IN-TIME spec, not rolling register. Structure sound: 3-tier bridge (T1 public canonicals / T2 SSI-ENN methodology refs / T3 no-flow proprietary), manifest.json schema, methodology_pins.md template, validate_report_manifest.py sentinel spec, worked example, risk register, implementation roadmap.

| # | Finding | Severity |
|---|---|---|
| DB.1 | Header stamps `Status: v1 — authored 18 Jun 2026 evening. This is the architecture spec doc for the cross-leverage pattern.` — point-in-time architecture spec. Doc self-declares as spec, not rolling register. That's fine per doc class | OK |
| DB.2 | **2 LIFE-RESILINK refs surfaced** — line 25 (Rule L example about "consortium HPC innovation lineage documented in LIFE-RESILINK Teaser — EIC SoE, ETP4HPC Disruptive Innovation Award Feb 2026" — used as EXAMPLE of Rule L reader-inference discipline) + line 611 ("Hypothetical LIFE-RESILINK Section 1 evaluator reads SB-01 and follows footnote..." — used as WORKED EXAMPLE of the manifest.json sentinel-verification chain). **Both are legitimate methodological usage** (Rule L example + worked-example evaluator persona), not marketing copy or specific-project-attribution. **BUT** doc is external-facing per its `00-Framing/` location, and Task #104/#105 scrub applied "external-audience docs". Rule O-scope needs operator disambiguation: are worked-example evaluator personas within scope or outside? Consistent decision needed against MF.3 finding on Methodological Foundations PDF (same class) | MAJOR (Rule O clarification pending — sister to MF.3) |
| DB.3 | Convention reference block cites SSI-ENN Conventions (#56/#60/#62/#63/#67/#71) + SSI Index Convention (#14.1). **Register-split discipline is applied correctly** at doc load — cites both registers explicitly + prefixes with "SSI-ENN Convention" vs "SSI Index Convention". This is exactly the pattern that CV.9 recommends for cross-doc consistency. **DATA_BRIDGE is the model for register-disambiguation discipline** across the doc set | OK (leading example) |
| DB.4 | §1 architectural problem cites "39 OECD countries" — post-Wave-4 is actually 39 (38 OECD + Greenland). Coherent. But wraps in "39 OECD" without noting Greenland's non-OECD status. Micro-drift, same class as A.5 | MINOR |
| DB.5 | §11 open items shows all specification items ✅ complete + 2 pending items: (a) actual implementation (validator + template + cron in Q3 2026 per roadmap); (b) operator decision — confirm scope of SSI-ENN methodology approved for public citation. **Both are TODOs from 18 Jun 2026 — verify current status**: has the validator been implemented per SB-01 ship in Jul 2026? Task list shows Task #4 "SB-01 scaffold B — manifest.json + methodology_pins.md per Doc 4 schema" completed. So the SCHEMA landed; verify whether the sentinel + cron implementation landed too | MAJOR (verify implementation status) |
| DB.6 | Roadmap (§9) targets "early July → ship 15 August → ongoing". Currently 22 Jul 2026. Roadmap partly executed (SB-01 shipped 4 Jul 2026, per task history). Refresh should update roadmap with actuals + next Foundation-establishment milestones | MAJOR (roadmap refresh) |
| DB.7 | 1 mention of Wave 2 / Convention #78 / Convention #79 (verified in earlier grep). Doc is a POINT-IN-TIME architecture spec (per DB.1 doc-class self-declaration), so it wouldn't be expected to roll with Wave 2/3/4 cadence. But cohort-scale references may need footnote noting current cohort state | MINOR (per doc class) |
| DB.8 | Cross-refs (§10) very well-anchored: sibling docs (RFK / COMPETITIVE_SCRAPE_KB / COMPETITIVE_SCORING_MATRIX / SSI_INDEX_DIFFERENTIATION_ANGLES / SSI-ENN CLAUDE.md) all cited by exact filename. Convention refs prefixed with register. **Cross-doc anchoring discipline is exemplary in this doc** — Should be pattern for other docs | OK (leading example) |
| DB.9 | Doc doesn't yet reflect Wave 4 sharding architecture (Convention #79 candidate). If the manifest.json schema needs extension to handle sharded canonicals (per CLAUDE.md's Convention #79 candidate — 4 large countries UK/US/Germany/France split into 18 shard files), that's a v1.1 refresh trigger | MAJOR (architecture refresh trigger — sharding schema extension) |
| DB.10 | §6 operational mechanics + §7 worked example (SB-01 traced end-to-end) both reference the SB-01 ship as illustration. SB-01 has now shipped (4 Jul 2026). Refresh could promote the "hypothetical worked example" to "actual worked example" — reader benefits from real-vs-hypothetical example | MINOR (upgrade opportunity) |

**Refresh recommendation**: v1 → v1.1 refresh. (i) Rule O-scope disambiguation on 2 LIFE-RESILINK refs (worked-example evaluator personas — pending operator; sister decision to MF.3); (ii) roadmap actuals update (SB-01 shipped, validator implementation status verify, Aug 15 ship-window followed); (iii) manifest.json schema extension for Convention #79 candidate sharded canonicals; (iv) SB-01 worked example from "hypothetical" to "actual"; (v) implementation-status update on §11 open items; (vi) v1.1 header stamp. **Register-disambiguation discipline is exemplary — should be back-ported to other docs** (theme 2 resolution model).

### T1.6 — SSI_INDEX_DIFFERENTIATION_ANGLES.md (Phase 6) — **overall severity: MAJOR** (Rule O structural gap surfaces here at scale)

External-facing strategy doc (`Report Production/00-Framing/`) — 32 KB / 276 lines. v2 refreshed 18 Jun 2026 deep night. Verified 0 Jesuit refs ✅. **12 RESILINK/LIFE-CCA/HORIZON CL5 refs — HIGH scrub scope needed vs Task #104/#105 completion**. Doc is the strategic-output synthesis of the four-document competitive-positioning workstream — 7 ranked angles + 9-report editorial spine + war-games narrative architecture + Foundation positioning narrative.

**Key structural finding (relevant to Rule O across the framing register):** DIFFERENTIATION_ANGLES has 12 refs of two classes: (a) **EU-call leverage columns** for each of the 7 angles explaining how each serves LIFE-RESILINK Sep 2026 + HORIZON CL5-2027-07 D3-26/D3-28 bid pathways; (b) **report-timing refs** (SB-01 lands before LIFE-RESILINK 22 Sep submission). Both are STRATEGIC-INTERNAL prose ("why we build these reports") not published-external prose. **The same class as REPORTS_FRAMING_KB §0 instrumentation rule** — internal strategy documenting the EU-funding-instrument frame. But EDITORIAL_CALENDAR got fully scrubbed to 0 refs (external-facing), while this strategy doc didn't. **Task #104/#105 scrub was applied inconsistently across the framing register**.

**Root cause**: `Report Production/00-Framing/` folder contains a mix of (a) external-facing docs meant to be shared/published (REPORTS_FRAMING_KB v-public, EDITORIAL_CALENDAR public, About_SSI_Index) + (b) internal-strategy docs documenting HOW reports get planned/positioned (this doc + DATA_BRIDGE + COMPETITIVE_SCRAPE_KB + COMPETITIVE_SCORING_MATRIX). Task #104/#105 scrub was applied without differentiating classes. **Structural filing issue at framing-register level.**

| # | Finding | Severity |
|---|---|---|
| DA.1 | 12 LIFE-RESILINK/LIFE-CCA/HORIZON CL5 refs across §1 (uniqueness-EU-leverage scoring), §2 per-angle "EU-call leverage" columns, §3 timing notes. **Task #104/#105 external-audience scrub NOT applied** to this doc. **Structural inconsistency vs EDITORIAL_CALENDAR** which is external-facing sister doc and IS fully scrubbed | CRITICAL (structural — Rule O consistency at framing-register scale) |
| DA.2 | Header self-declares purpose: "the strategic output of the four-document workstream" + "produces the SSI Index positioning narrative that frames every report in the pipeline". **This is meta-strategic-frame document, not a shippable report**. If it's internal, it should carry an "INTERNAL — DO NOT PUBLISH" banner at doc top. Absence of banner + external-facing folder placement + no scrub = ambiguity | MAJOR (structural — doc-class disambiguation) |
| DA.3 | 4 refs to "39 OECD" cohort — 0 refs to post-Wave-4 796,121 substation actuals. Cohort scale drift, same class | MAJOR |
| DA.4 | 0 Wave 2/3/4 / Convention #78/#79 refs. Point-in-time doc (18 Jun 2026, per doc-class self-declaration) | MAJOR (per doc-class refresh cadence) |
| DA.5 | Structure sound: §1 ranked angles (7 angles) + §2 per-angle treatment + §3 editorial spine + §4 war-games narrative architecture + §5 positioning narrative + §6 co-publication + §7 risks/counterarguments + §8 open items. **Structure matches REPORTS_FRAMING_KB §7 + editorial-calendar spine** — cross-doc coherence intact | OK (coherence) |
| DA.6 | Header stamps v2 + "refreshed 18 Jun 2026 deep night. Incorporates conceptual scaffolding...compute force with distributed-compute grey-zone resilience layer, no-silo principle, Rule L Reader-Inference Discipline, and war-games narrative architecture". Well-versioned + clear scope on what changed v1 → v2 | OK |
| DA.7 | Angle 7 (Compute-4IR Integration) is white-space per Doc 1 §6 finding "0/35 (0%) institutions publish it as one analytical surface". Positioning claim is strongly supported. Ok | OK |
| DA.8 | §6 co-publication + citation network strategy exists but no explicit mapping to Foundation timeline (Foundation establishment 2027-2028 per About_SSI_Index.md). Verify coherence | MINOR |

**Refresh recommendation**: v2 → v3 refresh with structural decision point. (i) **Operator decision required — Rule O scope across framing register**: (a) fully scrub RESILINK/LIFE-CCA/HORIZON CL5 for consistency with EDITORIAL_CALENDAR; (b) split `00-Framing/` into `-Internal/` + `-External/` subfolders; (c) add "INTERNAL — DO NOT PUBLISH" banners on strategy docs; (ii) cohort scale drift (4 refs 39 OECD → add post-Wave-4 796,121 anchor); (iii) v3 header stamp + refresh note. **DA.1 is the biggest single Rule O finding across the audit set — resolution decision needed before any further scrub work.**

---

### T1.7 — COMPETITIVE_SCORING_MATRIX.md (Phase 6) — **overall severity: MINOR**

External-facing scoring matrix (`Report Production/00-Framing/`) — 28 KB / 450 lines. v1 authored 18 Jun 2026 evening. **Cleanest external-facing doc after LITERATURE_EVIDENCE_REPORT** — 0 Jesuit refs ✅, **0 RESILINK/LIFE-CCA/HORIZON CL5 refs** ✅ (Task #104/#105 scrub complete OR doc never had them — verify). 36×12 scoring matrix (35 competitor institutions + SSI Index) with 12 scoring variables + cohort distribution + cluster analysis + empty-quadrant identification.

| # | Finding | Severity |
|---|---|---|
| CSM.1 | 0 Jesuit + 0 RESILINK/LIFE-CCA/HORIZON CL5 refs — cleanest scrub state in framing register. Either fully scrubbed OR doc was authored purely as competitive-analysis without EU-funding-leverage columns. Either way ✅ | OK |
| CSM.2 | 4 refs to "39 OECD" / cohort — same class as DA.3 stale cohort scale | MAJOR (cohort drift) |
| CSM.3 | Point-in-time doc (18 Jun 2026). Structure sound: 12-variable methodology + 36×12 matrix + distribution + cluster + empty-quadrant + Differentiation Distance metric + strategic implications. **This is peer-reviewable competitive-landscape analytical output** — could be published standalone as academic contribution (composite-indicator methodology applied to policy-research institutional landscape) | OK |
| CSM.4 | Doc references SSI Index at "v4.2" throughout. Post-v4.23 methodology cohort would need "v4.23" or "v4.2 (v4.23 data cohort)" refresh — but this is intra-methodology-version refresh so LOW severity | MINOR |
| CSM.5 | §7 strategic implications for SSI Index positioning + §8 differentiation angles preview + §9 open items + Doc 3 handoff. Cross-doc coherence with DIFFERENTIATION_ANGLES intact. **Doc 2 → Doc 3 → Doc 4 chain audit-defensible** | OK |
| CSM.6 | Competitor scoring uses June 2026 institutional data. **Institutional landscape churns rapidly** — new publications, org-chart changes, funding-round events over the past 5 weeks may have shifted scoring for individual institutions. Suggest quarterly re-scan of top-10 changes as maintenance discipline | MINOR |
| CSM.7 | §6 Composite "Differentiation Distance" metric — verify metric definition still holds against SSI Index v4.23 cohort scale + methodology (11 modifiers vs 8 counted earlier). Metric shape stability at cohort expansion | MAJOR (methodology stability at cohort scale-up) |

**Refresh recommendation**: v1 → v1.1 refresh (mostly maintenance). (i) cohort scale drift updates (CSM.2); (ii) v4.2 → v4.2 (v4.23 data cohort) intra-version disambiguation (CSM.4); (iii) quarterly re-scan of top-10 institutional changes (CSM.6); (iv) Differentiation Distance metric shape verification vs current cohort (CSM.7). **Lowest-effort refresh in Phase 6**.

---

### T1.8 — COMPETITIVE_SCRAPE_KB.md (Phase 6) — **overall severity: MAJOR** (institutional-data staleness at rapid-churn timescale)

External-facing per-institution profiles (`Report Production/00-Framing/`) — 50 KB / 858 lines. v1 authored 18 Jun 2026 evening. Verified 0 Jesuit refs ✅. **1 RESILINK ref** at §6 empty-quadrant identification (line 787) — used as ILLUSTRATIVE ref to European HPC innovation consortium ecosystem, not as strategic pathway. Same DA.2-class structural ambiguity but at 1 ref rather than 12 refs. Per-institution scrape covers 4 clusters × 10-5 institutions = 35 institutions.

| # | Finding | Severity |
|---|---|---|
| SK.1 | 1 RESILINK ref at line 787 — "European HPC + edge-AI innovation in this space sits within the consortium ecosystem (ETP4HPC + EuroHPC JU + EIC Seal of Excellence + ETP4HPC Disruptive Innovation Award Feb 2026 — public via the LIFE-RESILINK Teaser)". Contextually the ref is illustrative empty-quadrant support (Angle 7 Compute-4IR white space). **Same Rule O-scope structural question as DA.1 but at smaller scale**. Coherent with DIFFERENTIATION_ANGLES §2 Angle 7 usage — either both scrub or both preserve | MAJOR (Rule O consistency with DA) |
| SK.2 | 1 ref to "39 OECD" / cohort — same cohort scale drift class | MAJOR |
| SK.3 | Header: "v1 — authored 18 Jun 2026 evening. Source basis: 5-angle deep-research web scrape (June 2026) + cohort baseline knowledge. Every claim flagged '[verified]' (web-search-confirmed) or '[baseline]' (well-known institutional fact, not specifically reverified) or '[not verified for 2024-2026]'". **Provenance discipline is exemplary** — every institutional claim carries verification-tier flag. This is the same class as LITERATURE_EVIDENCE_REPORT provenance discipline | OK (leading example — provenance) |
| SK.4 | **Institutional-data staleness at rapid-churn timescale**: 35 institutions × 12 variables × 5 weeks since scrape = ~2,100 data points that may have shifted since June scrape. EIES, Bruegel, CEPS, IISS, CSIS, SIPRI, RUSI, IFRI, ECFR, Chatham House etc all publish monthly-to-weekly. Refresh cadence needed | MAJOR (institutional-data freshness) |
| SK.5 | 4-cluster taxonomy: Cluster A Brussels EU policy (10) + Cluster B Atlantic security (10) + Cluster C national foreign-affairs (10) + Cluster D hybrid/grey-zone/critical-infrastructure specialists (5). Coherent with REPORTS_FRAMING_KB §1 EIES anchor structural archetype. Cross-doc coherence intact | OK |
| SK.6 | §7 citations register — verify each citation URL still live at retrieval. Institutional web pages get restructured, papers get moved. Provenance re-verification | MAJOR (URL-freshness) |
| SK.7 | Empty-quadrant identification (§6) is the analytical CORE that feeds Doc 2 (scoring matrix) → Doc 3 (differentiation angles) → Doc 4 (data bridge). If Doc 1's scrape has drifted, the whole downstream chain drifts. **Refresh discipline required for the DOC 1 tier** to keep Doc 2/3/4 audit-defensible | MAJOR (upstream freshness cascade) |
| SK.8 | Cross-refs at header cite Doc 2/3/4 correctly. Sibling chain intact. Anchoring discipline correct | OK |

**Refresh recommendation**: v1 → v1.1 quarterly refresh cadence. (i) quarterly top-10 competitor re-scan (SK.4 SK.7); (ii) URL-freshness verification pass (SK.6); (iii) cohort scale drift updates (SK.2); (iv) Rule O consistency decision cascaded from DA.1 (SK.1); (v) v1.1 header stamp. **Institutional-data-scrape docs need shorter refresh cadence than methodology docs** — codify quarterly discipline in HOUSEKEEPING.md Trigger #15 candidate.

### T1a.4 — Per-country Formula Constructs (Phase 7) — **overall severity: MAJOR structural** (cohort-scope coherence gap surfaces)

Structural sample of the per-country FC cohort. Discovery: FC layer has two distinct cohort states.

**v4.2 W1-W10 Substation FC cohort — COMPLETE 39/39**: All 39 OECD countries (through Türkiye rename) carry a `SSI_v4_2_W1_W10_Substation_Formula_Construct_<Country>_v2.html` at ~63 KB each. Sizes uniformly narrow-range (62-64 KB) confirms template-cloned pattern. Spot-check: Italy v2 = 62,495 bytes; Poland v2 = 63,591 bytes; Norway v2 = 63,747 bytes. Poland-specific place-name refs (Polska/Warszawa/PSE/gmina): 6 hits. Zero Italy-template leakage (0 Mezzogiorno/Italia/Terna/Italian refs in Poland or Norway) — country-name substitution discipline complete.

**v4.2 Complete FC cohort — PARTIAL 1/39 (Italy-only)**: Only `SSI_v4_2_Complete_Formula_Construct_Italy_v3.html` exists at v4.2 mathematical-spine vintage. **No other country has a v4.2 Complete FC**. The mathematical-spine + master-equation + modifier-registry + §14 R1-R7 ESG framework consolidation has NOT been extended cohort-wide.

**v4.0.2 Complete FC cohort — LEGACY 22/39**: 22 countries carry legacy `SSI_v4_0_2_Complete_Formula_Construct_<Country>.html` at ~130 KB each (Italy, France, UK, Estonia, Lithuania, Sweden legacy, Switzerland, etc.). These are SUPERSEDED by v4.2 pipeline but not retired — coherent with Convention #56 visibly-honest degradation ("old versions preserved for audit, not silently overwritten") per repo CLAUDE.md line 41.

| # | Finding | Severity |
|---|---|---|
| PC.1 | **Structural gap**: v4.2 mathematical-spine FC (Complete Formula Construct) exists only for Italy (Italy_v3). Yet Methodological Foundations PDF §1 abstract claims "OECD-capable" framework calibrated on Italian pilot + extendable to 39-country cohort. **The extension has happened at the W1-W10 governance-gate layer (39/39) but NOT at the mathematical-spine layer (1/39)**. Cohort-scope coherence gap | CRITICAL (structural — cohort scope) |
| PC.2 | All 39 per-country v4.2 W1-W10 FCs inherit the Italy v2 template — including the header-body **5/2/3 + 6/1/3 mesh drift** (W10.2, W10.3). **The mesh drift compounds across 39 files** — 39x the inconsistency, all pointing back to the Italy v2 template's incomplete Convention #6 §5.6 resolution application. **Cohort-scale drift** | CRITICAL (drift compounds cohort-wide) |
| PC.3 | Per-country FC customization is MINIMAL (Poland: 6 place-name refs; Norway: 37 place-name refs) vs Italy pilot which is deeply calibrated. This means **the per-country FCs don't yet carry per-country regulatory anchors** — no per-country R6c flood zones (PGRA equivalents), R6e winter climate profiles, R10_just energy-poverty proxies, or ISPRA-analogue seismic zones. Methodological Foundations §1 promised "per-country regulatory anchors (ISPRA / ARERA / ISTAT / Terna for Italy) replace cleanly with national equivalents for cohort expansion" — but per-country FCs don't yet expose this | MAJOR (per-country regulatory-anchor documentation gap) |
| PC.4 | 39 v4.2 W1-W10 FCs × header-body mesh drift = single-source refresh strategy: fix Italy v2 template's mesh drift first, then regenerate 38 per-country FCs from the fixed template via automation. **Auto-regen script needed as part of refresh plan** | MAJOR (refresh strategy — automation dependency) |
| PC.5 | Legacy v4.0.2 Complete FCs (22/39): audit-defensible per Convention #56 visibly-honest degradation. Should NOT be refreshed — should remain as-is as legacy audit-trail. Verify no external references cite legacy v4.0.2 FCs as current | OK (retired properly) |
| PC.6 | The Complete FC v4.2 extension to 38 countries beyond Italy is a **~4,750 pages of documentation work** (assuming ~125-page Italy v3 × 38 countries with per-country regulatory anchors — R6c/R6d/R6e/R8/R9/R10 sources per country, per-jurisdiction R3 calibration tables, per-country event battery). **Substantial engineering commitment** — potentially larger than the codebase v4.23 gap-closure workstream itself | MAJOR (scope of missing work) |
| PC.7 | The disparity is understandable given Wave 2/3/4 focus was CODEBASE cohort expansion (39-country data ingestion + methodology enforcement), not DOCUMENTATION cohort expansion. But now that codebase is at TERMINAL (39/39 v4.23), doc layer needs to catch up. Verify against publication strategy timeline: paper anchor (Methodological Foundations PDF) currently Italy-pilot scoped; when do per-country Complete FCs become an LP-DD requirement? | MAJOR (documentation-cadence vs codebase-cadence alignment) |
| PC.8 | Per-country FC filename convention: `SSI_v4_2_W1_W10_Substation_Formula_Construct_<Country>_v2.html`. Country name embedded with mix: some use ISO country name ("Poland"), some use compound ("New Zealand", "Costa Rica", "United Kingdom", "United States"), one uses local-language ("Türkiye"). **Filename convention drift** — should canonicalize (either all ISO alpha-2 or all English exonym) | MINOR (filename hygiene) |
| PC.9 | Cross-doc coherence with CONVENTIONS.md Trigger #6 (cohort-replication procedure — "Author a per-country V4_2_IMPLEMENTATION_ARCHITECTURE_<Country>.md"): each country should have its own architecture memo AND per-page audit sidecars. **Verify existence** — likely partial | MAJOR (Trigger #6 discipline verify) |
| PC.10 | Test files at `_audit-snapshot/tests/foundational_documents_index.py` + `_audit-snapshot/tests/foundational_documents_registry.json` may catalogue expected per-country FC file locations (per CONVENTIONS.md #14 sentinel). Verify these sentinels are green against the current per-country cohort. If some countries have missing files, sentinel would flag | MAJOR (sentinel state verify) |

**Refresh recommendation**: v2 → v2.1 mechanical cohort-refresh + STRUCTURAL DECISION on v4.2 Complete FC cohort expansion. **Two-tier refresh strategy**:

- **Tier A — Mechanical (achievable now)**: (i) fix Italy W1-W10 v2 template mesh drift (W10.2, W10.3); (ii) build auto-regen script that regenerates 38 per-country FCs from the fixed template with per-country place-name substitution + per-country regulatory anchor stubs; (iii) v2 → v2.1 header bump across all 39 files.

- **Tier B — Structural decision (operator-scoped)**: (iv) extend v4.2 Complete FC (mathematical spine) to remaining 38 countries — MAJOR engineering commitment (~4,750 documentation pages estimated); or (v) declare Italy v4.2 Complete FC as the canonical mathematical-spine reference with per-country DELTA sidecars documenting only country-specific regulatory anchor substitutions (~10-20 pages per country, ~600 pages total); or (vi) defer until Foundation-establishment timeline (2027-2028) with per-country FCs authored as part of Foundation charter documentation.

**PC.1 + PC.2 + PC.6 make this the most significant cohort-scope structural finding in the entire audit.**

### T2.5 — SSI_Dashboard_Knowledge_Base_v19.md (Phase 8) — **overall severity: MAJOR** (working-memory doc frozen at ship-close)

Internal working-memory / knowledge-base doc (SSI Index root) — 344 KB / 4,169 lines. G1 Jesuit-scrub not applicable (0 refs). 0 RESILINK refs. Well-versioned (v19 with explicit "v18 preserved unmodified as historical record" audit-trail discipline). Last updated 18 Jun 2026 for the v4.2 ship — **frozen at ship-close, never refreshed through Jul 2026 landings**.

| # | Finding | Severity |
|---|---|---|
| KB.1 | Last Updated: 2026-06-18. Header: "SSI v4.2 LIVE IN PRODUCTION + 39 OECD countries + monthly automation pipeline + Türkiye rename". Ship-close state. **34 days ago** (5 weeks). Since then: R7 SFDR PAI Phase 4a-4e (16 Jul), Convention #78 BINDING (16 Jul), Convention #79 candidate (18 Jul), Wave 4 TERMINAL (21 Jul), Discipline #37/#38/#39 candidate, 5-band Extreme Phase 2A/B/C (25 Jun). **Frozen doc** | MAJOR (working-memory stale) |
| KB.2 | §1 Architecture Overview line 154 area: **"23 country dashboards"** — but current cohort is 39. Same cohort-scale drift + this doc claims to be maintained working memory. Working-memory drift is worse than reference-doc drift because reader relies on it as CURRENT ground truth | MAJOR |
| KB.3 | Last section is §52 V4.2 Live Ship 18 Jun 2026. Last line says "Next: § 53 = reports framework v1 (RF-1 once operator + Claude scope it)". **§53 was never added** despite RF-1 completing (Task #2 completed). Post-June-2026 work stream not codified in KB | MAJOR |
| KB.4 | Version discipline is EXEMPLARY: header records v10 through v19 accumulating changelog; v18 preserved unmodified for historical record; §52 explicitly notes "No KPI counts were rewritten across §1–§51 — those reflect the v4.0.2 production state up to and including 22 May 2026. From §52 onward, v4.2 is the canonical methodology." **This versioning discipline is the model for how ALL working docs should preserve audit trail during methodology-version transitions**. Back-port to CONVENTIONS.md as new Convention | OK (leading example) |
| KB.5 | KB uses "Wave" terminology at §35 (Waves 1-2 cleanup) + §36 (Waves 3-5 shared helper) + §37 (Wave 6 CI gates) — these are SESSION-based clusters from March-April 2026. **But CLAUDE.md ⭐ block uses "Wave" for country-onboarding cohorts** (Wave 1 = original 15 countries, Wave 2 = 13 Wave-2 countries, Wave 3 = 9 Wave-3 countries, Wave 4 = 9 Wave-4 countries). **Terminology collision** — same "Wave" word means different things at KB vs CLAUDE.md registers. Reader can be confused | MAJOR (terminology coherence) |
| KB.6 | Cross-refs at KB tail cite `V4_2_LIVE_SHIP_CLOSURE_2026-06-18.md` (canonical SoT), HOUSEKEEPING.md Trigger #14, FC Italy v3 footer, DSR closure memo. **Cross-doc anchoring solid** at ship-close, but not maintained through Jul 2026 | OK for June, MAJOR through July |
| KB.7 | KB references "7 v4.2 methodology briefs need 'in-production-since 18 Jun 2026' stamp (deferred to future quiet-window pass)" in outstanding items list. **Quiet-window never came** through Jul 2026. Verify | MAJOR |
| KB.8 | KB references "Heat days / ice days analytic fix (task #133 in_progress)" — Task #133 in current session list is "Doc cascade #7 — Class A 5-band methodology cascade" and marked COMPLETED. Task-number references at KB layer may not correspond to current task-list numbers. Task-numbering register split | MINOR (cross-register task refs) |
| KB.9 | §22 "Adding a New Country — Checklist" — verify against actual Wave 2/3/4 onboarding procedures. Trigger #6 in HOUSEKEEPING.md has more current procedure. Coherence check | MAJOR (procedure freshness) |
| KB.10 | KB v19 → v20 refresh would be substantial: at least 20+ new sections needed (§53 SB-01 ship, §54 SB-01 findings register, §55 Phase 2A/B/C 5-band, §56 v4.3 gap audit, §57 Canada P1, §58 Norway P2, §59 Mexico P3, §60 Austria P4, §61 Greenland P5, §62 v4.23 rename cascade, §63 R6_seismic + R7_cyber fixes, §64+ per-country Wave 2, §75+ per-country Wave 3, §85+ per-country Wave 4, §95 R7 SFDR PAI Phase 4a-4e, §96 Convention #78 BINDING, §97 Convention #79 candidate, §98 Wave 4 TERMINAL closure, §99 Denmark alias-map, etc.). **Substantial refresh work** | MAJOR (refresh-scope large) |

**Refresh recommendation**: **v19 → v20 substantial refresh needed**. Roughly-scoped: (i) update §1 architecture cohort count 23 → 39; (ii) fix "Wave" terminology collision (KB §35-#37 session-Waves vs CLAUDE.md country-onboarding Waves); (iii) add ~20+ new sections covering post-June-2026 landings; (iv) Task-numbering cross-register mapping (KB #133 vs current task list); (v) v20 header bump preserving v19 audit trail per KB's own excellent versioning discipline (KB.4). **Working memory freshness is essential for cross-session Claude reads** — CLAUDE.md itself references KB v19 for institutional-memory-scale narrative. **Priority: HIGH** but scope is LARGE.

### T2.6 — AUDIT_v4_0_2_PRE_v4_2_FOUNDATION.md (Phase 9) — **overall severity: OK** (historical baseline — do not refresh)

Internal audit memo (SSI Index root) — 70 KB / 1068 lines. Dated 8 June 2026 with explicit purpose: "Validate v4.0.2 as a solid foundation before any v4.2 work commences. The audit gates v4.2." Verified 0 Jesuit refs ✅ + 0 RESILINK refs. **This is a point-in-time historical audit that served its purpose** — v4.2 work commenced + landed + shipped following this audit's clearance verdict. It should NOT be refreshed.

| # | Finding | Severity |
|---|---|---|
| PVF.1 | Doc self-declares "IN PROGRESS — deep code-walk" in header (line 4). But tail closes with "Audit completed in-session 8 June 2026". Header vs tail disagreement — but tail is authoritative | MINOR (header cleanup only) |
| PVF.2 | Structure sound: §0 Framing + §0.1 Audit discipline + §0.2 Findings notation + §1-§6 L1-L6 layer findings + §7 Synthesis. Each finding cites file:line references. Reproducible. Excellent audit discipline | OK |
| PVF.3 | Explicit companion refs: `AUDIT_v4_0_2_FINDINGS_MATRIX.xlsx` + `PHASE_1_IMPLEMENTATION_PLAN.md`. Cross-doc anchoring correct | OK |
| PVF.4 | Copyright footer: "© 2026 Altinium Invest, SRL. Audit memo for internal use." Explicit internal-only marker. G1 Jesuit-scrub doesn't apply per author's own internal-use declaration | OK (internal marker exemplary) |
| PVF.5 | Verdict framework (CARRY-FORWARD / REFACTOR-BEFORE-v4.2 / OUT-OF-SCOPE-FOR-v4.2) preserved for audit trail. All verdicts remain historically valid | OK |
| PVF.6 | Header status marker "IN PROGRESS" is misleading if reader arrives fresh. Change to "SUPERSEDED — audit complete, v4.2 landed, this doc preserved for audit trail" would clarify | MINOR (header hygiene) |

**Refresh recommendation**: **Do NOT refresh substantively**. This is a historical audit doc that served its purpose. Two micro-cleanups: (i) fix header "IN PROGRESS" → "SUPERSEDED / audit-complete" (PVF.1 + PVF.6); (ii) add explicit "This is a historical audit — v4.2 has been landed; see CLAUDE.md ⭐ block for current state" note at doc top. Otherwise, preserve as-is per Convention #56 visibly-honest degradation. Same class as v4.0.2 Complete FCs (PC.5).

_(Phase 9 complete — 12 foundational docs read + 3 per-country FC tier structural sample; Phase 10 — coherence matrix + refresh plan synthesis below)_

---

## Phase 10 — Coherence matrix + refresh plan synthesis

Total findings logged: **~140 across 12 docs + structural cohort sample**. Below synthesises them into cross-doc coherence issues + a prioritized refresh plan.

### Coherence matrix — cross-doc issues surfaced

| Coherence issue | Docs affected | Severity | Resolution |
|---|---|---|---|
| **CX.1 — Truth-source ambiguity** (CLAUDE.md vs AUDIT_BASELINE.md) | AUDIT_BASELINE (self-declared canonical, 5 wks stale) vs CLAUDE.md (fresh rolling anchor) | CRITICAL | Designate CLAUDE.md ⭐ block as canonical rolling anchor; either refresh AUDIT_BASELINE.md to v2 addendum or retire self-declaration |
| **CX.2 — Convention register split ambiguity** (SSI Index vs SSI-ENN) | About_SSI_Index, METHODOLOGY_DISCIPLINES, CONVENTIONS, FC v3, Methodological Foundations PDF | MAJOR | Codify `SSI Index Convention #X` vs `SSI-ENN Convention #Y` reference format as new SSI Index Convention #15; DATA_BRIDGE is the leading example (DB.3) — back-port |
| **CX.3 — Jesuit terminology scrub incomplete** (Global Rule G1) | METHODOLOGY_DISCIPLINES (26 refs), REPORTS_FRAMING_KB (7 refs); LITERATURE_EVIDENCE_REPORT/PDF exempted (0 refs pre-Rule-N codification) | CRITICAL | Single-commit scrub sweep across `Report Production/00-Framing/`; internal docs preserve |
| **CX.4 — Post-June-2026 landings missing across foundational cohort** (Wave 2/3/4, Conv #78 BINDING, #79 candidate, R7 SFDR PAI Phase 4a-e, Discipline #37/#38/#39, 5-band Extreme) | 8 of 12 docs: README, About, AUDIT_BASELINE, METHODOLOGY_DISCIPLINES, HOUSEKEEPING, CONVENTIONS, FC v3, W1-W10 v2, Methodological Foundations PDF, KB v19 | MAJOR | Single-commit multi-doc refresh once operator confirms scope + CX.2 register format |
| **CX.5 — Cohort scale drift** (Italy 4,293 vs 51,910; total 174,046 vs 796,121; countries 23 vs 39) | Every doc except EDITORIAL_CALENDAR + DATA_BRIDGE | MAJOR | Global sed-replace pass with disambiguation footnote pattern (About A.2) |
| **CX.6 — Rule O scope ambiguity — LIFE-RESILINK/HORIZON CL5** (12 refs in DIFFERENTIATION_ANGLES, 4 in Methodological Foundations PDF, 2 in DATA_BRIDGE, 1 in COMPETITIVE_SCRAPE_KB; scrubbed in EDITORIAL_CALENDAR/SCORING_MATRIX) | 5 docs | CRITICAL (structural — inconsistent scrub application) | Operator decision required: full scrub OR `00-Framing/` folder split into `-Internal/` + `-External/` OR "INTERNAL — DO NOT PUBLISH" banners on strategy docs |
| **CX.7 — v4.2 mathematical-spine cohort scope gap** (Complete FC = 1/39 vs W1-W10 FC = 39/39) | FC v3, per-country FC cohort, Methodological Foundations PDF | CRITICAL (cohort-scope) | Structural decision — extend Complete FC cohort-wide (~4,750 pages) OR canonical Italian anchor + per-country delta sidecars (~600 pages) OR defer to Foundation 2027-2028 |
| **CX.8 — Header-body 5/2/3 + 6/1/3 mesh drift** (Convention #6 §5.6 resolution incomplete in body text) | W1-W10 FC v2 (Italy + 38 country clones — inherited via template), FC v3, Methodological Foundations PDF | MAJOR | Fix Italy W1-W10 v2 template body; regenerate 38 per-country FCs via automation; refresh FC v3 §5.6 mesh mentions |
| **CX.9 — Master equation display shape drift** (FC v3 line 396 shows v4.0.2 multiplicative-only; v4.2 additive R6c_flood not integrated into master equation display) | FC v3, Methodological Foundations PDF | CRITICAL (mathematical spine) | FC v3 §5 master equation refresh with additive R6c_flood term; propagate to PDF §1 abstract |
| **CX.10 — Terminology collision "Wave"** (KB §35-#37 session-Waves vs CLAUDE.md country-onboarding Waves) | KB v19, CLAUDE.md | MAJOR | Rename either KB Waves → "Sessions 35-37" OR CLAUDE.md Waves → "Country Wave 1/2/3/4" |
| **CX.11 — Task-numbering cross-register** (KB v19 task #133 ≠ current task list #133) | KB v19, current task list | MINOR | Cross-register mapping table in KB v20 |
| **CX.12 — Version-marker discipline inconsistent** (some docs point-in-time, some rolling; some declare status, some don't) | README (no date), FC v3 (LP-1..12 ship-anchored), KB v19 (versioned-preservation), AUDIT_BASELINE (no addenda since 13 Jun) | MAJOR | Adopt KB v19 versioned-preservation discipline as convention across working-memory docs |
| **CX.13 — Filename convention drift** (per-country FC filenames mix ISO/exonym/local-language) | 39 per-country W1-W10 FCs | MINOR | Canonicalize to ISO alpha-2 or English exonym |

### Prioritized refresh queue

**P0 — Ship-blocking** (must land before external publication activity):

1. **CX.3 Jesuit scrub** in METHODOLOGY_DISCIPLINES.md + REPORTS_FRAMING_KB.md — operator directive 22 Jul 2026 explicit
2. **CX.6 Rule O scope decision** (LIFE-RESILINK/HORIZON CL5) — required before Methodological Foundations PDF submission to arXiv/SSRN
3. **Methodological Foundations PDF v1 → v2** — pre-submission refresh (MF.1 5/1/1/3 + MF.5 5-band Extreme + MF.9 submission status verify + MF.10 author attribution)
4. **AUDIT_BASELINE.md v1 → v2** (Tier 3 critical drift; self-declared canonical) — either refresh with post-June-2026 addendum or retire self-declaration
5. **README.md full rewrite** — highest-visibility public-facing repo README, v4.0.2 snapshot

**P1 — High priority** (within 2-3 weeks):

6. **KB v19 → v20 substantial refresh** — working-memory freshness essential (KB.1-KB.10)
7. **HOUSEKEEPING.md + CONVENTIONS.md refresh** — post-June-2026 landings + Convention #14→#15+ register extension (HK.1-#10 + CV.1-#10)
8. **About_SSI_Index.md v1 → v2** — cohort count + Convention register + 9-commitment structure preserved
9. **FC v3 v3 → v3.1** — master equation drift + 5-band Extreme + R7 dual-axis + Discipline #36 (FC.1, FC.4, FC.5, FC.6)
10. **CX.2 Convention register format** codified as new SSI Index Convention #15 (register-split reference format)

**P2 — Structural decisions** (operator-scoped):

11. **CX.7 per-country Complete FC cohort scope** — extend to 38 countries, canonical + delta sidecars, or defer to Foundation
12. **CX.8 5/2/3 + 6/1/3 mesh cohort-wide fix** — Italy template fix + auto-regen script for 38 per-country FCs
13. **CX.10 "Wave" terminology collision** — KB rename or CLAUDE.md rename

**P3 — Maintenance cycle** (monthly/quarterly cadence):

14. **COMPETITIVE_SCRAPE_KB quarterly re-scan** (institutional-data churn) — SK.4, SK.7; codify as HOUSEKEEPING.md Trigger #15
15. **LITERATURE_EVIDENCE_REPORT quarterly literature scan** — LER.6 "ahead of curve" gap freshness
16. **URL freshness sweep across cited-source registers** — LER.7, SK.6

**Do-not-refresh (historical audit trail preservation)**:

- **AUDIT_v4_0_2_PRE_v4_2_FOUNDATION.md** — served its purpose; preserve as historical baseline (PVF.6 header micro-cleanup only)
- **v4.0.2 Complete FC cohort (22/39)** — legacy per Convention #56 visibly-honest degradation (PC.5)

### Recommended refresh sequencing

**Option 1 — Big bang (single major refresh event, 1-2 weeks)**: Freeze doc-writing work; commit CX.1 through CX.13 in a single 15-doc refresh sprint. **Highest cross-doc coherence guarantee** — no partial states. **Risk**: sprint-scope large + operator decisions on CX.6/CX.7 gate the whole thing.

**Option 2 — Phased (recommended)**: (a) Week 1 — operator decisions on CX.6 + CX.7; (b) Week 2 — CX.3 Jesuit scrub + CX.5 cohort scale global pass; (c) Week 3 — Methodological Foundations PDF v2 + README rewrite + AUDIT_BASELINE.md v2 (P0 items 3-5); (d) Week 4 — KB v20 + HOUSEKEEPING/CONVENTIONS refresh + About v2 (P1 items 6-8); (e) Week 5 — FC v3 v3.1 + CX.2 Convention register format codified (P1 items 9-10); (f) Weeks 6+ — P2/P3 structural + maintenance items.

**Option 3 — Just-in-time (per publication event)**: Only refresh docs when they're needed for a specific external event (e.g. Methodological Foundations PDF for arXiv submission; README for Foundation launch). **Low velocity, but lowest coordination overhead**. Risk: cross-doc drift compounds indefinitely.

**Recommendation**: **Option 2 phased approach**. Preserves operator decisions on structural items (CX.6/#7) as gates; sequences P0 → P1 → P2/P3 so highest-visibility drift closes first.

---

## Audit summary

**Read pass**: 12 foundational docs + 3-doc per-country FC structural sample. **Findings**: ~140 across 13 coherence themes. **Global Rule G1** (Jesuit scrub external-facing) locked per operator directive 22 Jul 2026. **Four-tier maintenance-state pattern** empirically confirmed: fresh (§8bis + LITERATURE_EVIDENCE_REPORT + EDITORIAL_CALENDAR); structurally sound content-stale (About + METHODOLOGY_DISCIPLINES + HOUSEKEEPING + CONVENTIONS + FC v3); critical drift (AUDIT_BASELINE + README); cohort-scope structural gap (per-country Complete FCs 1/39). **Preservation-appropriate historical docs** (AUDIT_v4_0_2 + v4.0.2 Complete FCs 22/39) recommended NOT to refresh.

**Task #459 audit-read pass complete.** Refresh plan (Option 2 phased) awaits operator selection.

---

## Operator decisions locked — 22 Jul 2026 (post-audit)

- **(a) Big bang with discipline** (rejected Option 2 phased; selected Option 1 big-bang variant) — all ~20 foundational docs refreshed in coordinated single-sprint sequence with tracked execution log
- **(b) Full scrub** — CX.3 Jesuit scrub external-facing docs + CX.6 Rule O RESILINK/LIFE-CCA/HORIZON CL5 scrub, both applied consistently across `Report Production/00-Framing/`; internal working docs preserve terminology
- **(c) Extend + canonical delta** — canonical Italy FC v3 stays as mathematical spine anchor + 38 per-country delta sidecars (~10-20 pages each) documenting only country-specific regulatory anchor substitutions

**Execution tracker**: `docs/audits/foundational_docs_refresh_20260722.md` (sibling refresh log).

---

*Findings register maintained by sandbox audit — 22 July 2026, complete. Refresh execution log tracks post-audit implementation.*
