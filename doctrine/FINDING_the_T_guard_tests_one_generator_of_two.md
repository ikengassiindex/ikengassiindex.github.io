# FINDING — component T is already landed, and the guard that landed it tests one generator of two

**Date** 25 September 2026
**Status** Measured. Read-only. Nothing derived, nothing written to any record.
**Item** `PLAN_OF_WORK.md` D2 — *"T — land the derivation."*
**Outcome** **D2 is already complete.** What it should say instead is below.

---

## 1. D2 was done before it was planned

    cced85da   components.T, derived — and this time the inputs were checked first
    213f2edb   Italy's T component is a measurement now, not a hash of its name
    124b1624   Revert "Italy's T component is a measurement now, not a hash of its name"

`components.T` carries `_component_T_source` on **21 of 39** jurisdictions:
australia, austria, chile, colombia, costa-rica, estonia, finland, greece,
hungary, ireland, israel, korea, latvia, lithuania, new-zealand, norway,
poland, slovakia, slovenia, sweden, turkey.

A dry run of `ssi_derive_component_T.py --all` today reports **42,244 derived,
median Δ +0.0000, p95 |Δ| 0.0000, ΔR_base +0.0000 on every one of them.** The
derivation is idempotent because it has already been applied. And `213f2edb`
shows Italy's T was landed and then **reverted** — the estate had already caught
what this finding re-measures.

`PLAN_OF_WORK.md` D2 said *"instrument written … decide which, then land."* It
was written, decided and landed. The plan item was wrong.

## 2. What the guard refuses, and it is right to

14 jurisdictions are REFUSED — belgium, canada, czechia, france, germany,
iceland, italy, japan, luxembourg, netherlands, portugal, spain, uk, us —
on one of two grounds: the transition block is a name hash, or a sub-metric is
degenerate (one distinct value). 4 more (denmark, greenland, mexico,
switzerland) have no transition block at all.

Measured independently today, over 90,000 values in the 11 jurisdictions
`enrich_esg_gaps.DER_NATIONAL` covers:

    reproduced from vary(typed national constant, substation NAME)

    country       DER_ratio   DER_variability   EV_load_ratio
    canada           98.0%            97.7%           100.0%
    france           95.3%            95.6%           100.0%
    germany          95.2%            94.8%           100.0%
    italy            94.6%            94.8%           100.0%
    japan            95.1%            94.9%           100.0%
    portugal         95.3%            94.7%           100.0%
    spain            95.3%            95.5%           100.0%
    us               95.1%            94.3%           100.0%
    uk               90.3%            90.5%            95.4%
    sweden           37.2%            38.2%            39.8%
    switzerland       0.0%             0.0%             0.0%   (block absent)

    OVERALL   81,528 of 90,000 = 90.59%

`EV_load_ratio` reproduces at **100.0%** in seven jurisdictions.

### The citations make it worse, not better

`enrich_esg_gaps.py:127-143` carries the national bases under these headers:

> *"DER penetration from IRENA Renewable Capacity Statistics 2024"*
> *"EV_load_ratio = EV charging load / substation capacity (IEA Global EV
> Outlook 2024)"*
> `'italy': {'DER_ratio': 0.61, ...}  # GSE solar+wind`
> `'portugal': {'DER_ratio': 0.58, ...}  # DGEG solar boom`

A national constant with a real citation is a **defensible Convention #7
documented proxy**. What is published is that constant multiplied by
`(1 + (md5(name) − 0.5) × 2 × spread)`. The jitter manufactures asset-level
resolution the cited source does not have, and it is the jitter, not the
constant, that is the defect. §7.2.

## 3. The guard is incomplete: this estate has TWO hash generators

`ssi_derive_component_T.py`'s guard tests correlation against
`enrich_esg_gaps.stable_hash(name)` and refuses at r = 1.000. That catches the
first generator:

    vary(base, name, spread) = base × (1 + (md5(f"{name}:42") − 0.5) × 2 × spread)

It does not catch the second, in `score-country.py:85-89` and `:187-189`:

    seed    = substation_id + name
    det_var(seed + 'dr', ref['der_ratio'], 0.25)      → DER_ratio
    det_var(seed + 'dv', 0.55,             0.20)      → DER_variability
    det_var(seed + 'ev', ref['ev_share'],  0.30)      → EV_load_ratio

Different seed, so r against `stable_hash(name)` is ~0 and the guard passes.

**Test.** `DER_variability` is the one sub-metric whose base is a country
constant (`0.55`), so it can be reproduced without knowing a per-region table.
Over jurisdictions the guard **passed**:

    chile        96.2%      ireland      97.8%      norway       89.4%
    slovenia     79.0%      hungary      71.0%      slovakia     58.9%
    israel       56.0%

Those are not weak correlations. They are the second generator, in jurisdictions
whose `components.T` is already published.

`DER_ratio` and `EV_load_ratio` reproduce far lower in the same test only
because their bases are per-region rather than per-country, and this test solved
a single base per country. That is a limit of the test, not evidence of realness.

**Passing the guard does not mean the input is real.** It means the input is not
generator one.

## 4. What D2 should say

| | |
|---|---|
| ~~land the derivation~~ | **done — `cced85da`, 21 jurisdictions** |
| D2a | **extend the guard to the second generator** — `det_var(substation_id + name + suffix, base, pct)`. Until it exists, no T country's inputs have been cleared. |
| D2b | **re-examine the 21 landed jurisdictions** under the extended guard. At least seven show the second generator on `DER_variability`. `components.T` may have to be withdrawn where it fails. |
| D2c | the real acquisition — per-unit DER capacity and consumption. **This is D1.** T is not a separate acquisition; it shares S1's. |

Component T is 0.05 of the composite. The guard gap is not worth 0.05 — it is
worth whatever else in this estate was cleared by a guard that tests one
generator of two.

## 5. The process defect that produced a wrong plan item

This is the fourth item in `PLAN_OF_WORK.md` written as pending that the estate
had already settled:

1. S1, T1, E2, S2, S3, I7, I9 — *"no acquisition designed"*; all implemented in
   `france-pipeline/scoring/ssi_scorer.py`.
2. V — recorded as SAIDI; the construct defines severity-weighted voltage dips.
3. T's inputs — called *"on 87.4% of the cohort"*;
   `ssi_derive_component_T.py`'s own docstring already states they are a name
   hash and names the jurisdictions.
4. D2 itself — already landed in `cced85da`.

`AUDIT_what_the_estate_already_holds_for_the_sixteen_metrics.md` audited the
**records** and the **pipeline code**. It did not audit the **git history**, and
three of the four above are visible in one `git log --grep`.

> **RULE. Before an item enters a plan as pending, `git log --grep` it and read
> the whole docstring of any instrument it names. An estate that has run for
> months has usually tried the obvious thing already.**

## Re-derive

    python3 scripts/ssi_derive_component_T.py --all --dry-run
    git log --oneline --all -- scripts/ssi_derive_component_T.py
    grep -n "DER_NATIONAL" -A 14 scripts/enrich_esg_gaps.py
    sed -n '85,89p;185,190p' scripts/score-country.py
