# FINDING — the foundational documents are a month behind the doctrine

**Date** 21 September 2026
**Measured on** `SSI Index/master documents/`, file times and content.
**Status** measurement only.
**Asked** whether the foundational documents need a refresh after the
21 September amendment. They did before it.

---

## Measured

    SSI_FOUNDATION_judgement.yaml           17 Sep 16:14   (now 21 Sep)
    SSI_FOUNDATION_BIBLE.md / .html         21 Aug 17:46   ← one month behind
    SSI_FOUNDATION_evidence.yaml            31 Aug 20:26
    SSI_FOUNDATION_gaps.json                17 Sep 13:24   ← 3 h before the amendment
    Italy/SSI_FORMULA_CONSTRUCT_ITALY.md    17 Sep 13:32   ← 3 h before the amendment

43 country package directories, each carrying a Construct and an Appendix in
both `.md` and `.html`.

## Confirmed by content, not only by timestamp

The rendered Italy construct still carries the text the 17 September amendment
replaced, and none of the text that replaced it:

    "wherever that is so"                                 2 occurrences
    "no verifiable provenance in the deployed pipeline"  61 occurrences
    "30 DISTINCT VALUES"                                  0
    "substation_name, 0.015"                              0

So the projections state the pre-amendment doctrine. Under Pin 16 documents are
projections and are never hand-edited, which makes this a render debt rather
than an error — but a reader of the Italy construct today is reading doctrine
that the judgement file superseded four days ago, and will not know it.

## Size of the debt

- **43 country packages** × Construct + Appendix × `.md` + `.html` — stale
  against the 17 September amendment and now the 21 September one.
- **`SSI_FOUNDATION_BIBLE.md` / `.html`** — 21 August, a month behind, and it
  is the document the Order of Battle and the §7 prohibitions are read from.
  Whether the BIBLE is a projection of the judgement file or a separately
  authored constitution is NOT established here and should be, before anyone
  re-renders over it.
- **`SSI_FOUNDATION_gaps.json`** and **`evidence.yaml`** — both predate the
  amendment.

## Why it was not cleared as it accrued

Deliberately, and correctly, under Pin 16: *project* comes after *derive*, and
render once and last. The R7 work stopped at the pin because the derivation is
still an open decision, so the render was never due. The 21 September amendment
changes no value either.

The debt is therefore real but not urgent — with one exception. The judgement
file now says three things about R7 and the modifier composition that the
published constructs contradict, and those constructs are the artefacts the
per-country packages are built from. If any package is sent to a third party
before the re-render, it carries superseded doctrine under the estate's own
letterhead.

## What clearing it needs

- A determination on the BIBLE's status first. Re-rendering a hand-authored
  constitution from a template would destroy it.
- Then `SSI_FOUNDATION_render2.py` per country. Pin 16: render one country and
  read it before looping 43.
- The renderer measures the repository as it goes, so it should run after any
  derivation, not before — which means it waits on the R7 and R_base decisions
  rather than being scheduled now.

---

## UPDATE, 21 September 2026 — two questions answered, and the debt is not what it looked like

### 1. The BIBLE is NOT a projection. Settled by measurement.

The open question above — *"whether the BIBLE is a projection of the judgement
file or a separately authored constitution is NOT established here and should
be, before anyone re-renders over it"* — is now closed.

`SSI_FOUNDATION_render2.py` writes exactly three things:
`SSI_FORMULA_CONSTRUCT_<SUFFIX>.{md,html}`,
`SSI_FORMULA_APPENDIX_<SUFFIX>.{md,html}` and `SSI_FOUNDATION_gaps.json`.

Wider than that: **not one `.py` file in either tree so much as contains the
string "BIBLE".** Nothing in the estate can generate it.

So the operator's position — that the BIBLE should be a separately authored
constitution — is not only the right one, it is the only one the tooling
permits. Two consequences:

- **A re-render cannot harm the BIBLE.** That risk is retired.
- **The BIBLE's one-month staleness is NOT render debt.** It is an *authoring*
  debt on a hand-written constitution, and it belongs to the flag officer. No
  renderer will ever discharge it. The two debts in this document have
  different owners and should stop being counted together.

### 2. The re-render is not a refresh. It would surface 31 blocking gaps.

Measured by dry-rendering into a scratch directory, writing nothing:

    python3 SSI_FOUNDATION_render2.py <repo> --country italy --out <scratch>

Against the committed Italy construct, the fresh render moves **six change-log
rows from `- | ✅` to `⛔ GAP | ⚠️ no evidence tier (8.3)`** — I4, I6, I5, I3,
and others dated 12 and 17 September. At MASTER, 31 blocking gaps:

    21  declared MUST in the taxonomy; neither rendered nor gapped
     6  no evidence tier (8.3)
     2  no provenance pin (8.2); no evidence tier (8.3)
     1  not in registry; no provenance pin (8.2); no evidence tier (8.3)
     1  not declared

    by section: slot_commercial_axes 10 · change_log 9 · slot_esg_reports 5
                e2_beta_decomposition 4 · slot_market_coupling 2
                derived_composites 1

**Why now and not on 17 September.** `SSI_FOUNDATION_render2.py` was modified
**18 September 05:17**, after the Italy render of 17 September 13:32. The §8.3
evidence-tier gate on change-log entries is newer than the last render. It is
not a regression: **it is a new gate correctly firing on pre-existing entries
that never carried an evidence tier**, and nothing has re-rendered since, so the
non-compliance has been invisible.

### 3. What this changes about the decision

The committed projections currently print **✅ on entries the current gate
scores ⛔**. They assert a compliance the doctrine no longer grants. Measured
against §7.5 — no silent absence — the *stale* documents are the dishonest
state and the re-rendered ones, gaps and all, are the honest one.

That inverts the instinct to supply the missing evidence tiers first and render
clean. Rendering clean would mean nine change-log entries acquiring evidence
tiers in a hurry, and an evidence tier is a **judgement**, not a field to be
filled so a gate goes quiet. Under §7.8 a gap that is shown is not a red
sentinel; a gap that is hidden by not rendering is worse.

**Recommendation: render, let the 31 gaps print, and treat supplying the
evidence tiers as declared follow-on work with the flag officer's signature on
each.** The alternative — hold the render until the tiers exist — keeps a false
✅ in 43 packages for as long as that takes.

### 4. Not resolved here

- Whether the estate-wide count is 31 per package or varies. Only Italy and
  MASTER were dry-rendered; both returned 31.
- **Pin 16 versus §8.5.** Pin 16 says render ONCE and LAST; §8.5 requires a
  re-render in the same change as an amendment. When amendments arrive in a
  series — three in September — the two cannot both be honoured. Today's
  composition-pin amendment landed without a re-render, so §8.5 is already
  unmet. Which rule yields is doctrine, and it is the flag officer's to say.
