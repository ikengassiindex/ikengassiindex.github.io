# RECOMMENDATION — project direction, written as project manager

**Date** 21 September 2026
**Asked** knowing the purpose of the index, what do you recommend and why
**Purpose taken as given** the SSI Index is a non-profit foundation instrument
whose role is to support policy decision-making on anti-maladaptation and
infrastructure resilience

---

## 1 · The structural finding of the day, stated once

Today looked like a sequence of unrelated defects. It is one.

**The measured layer is real and good.** 622,104 substations from
OpenStreetMap. GHSL catchment population per asset, 99.4% coverage, 80–95%
distinct values per country. INGV and GEM seismic PGA. CMIP6 trajectories.
NIVA net migration, now honestly sourced. Voltage, operator, geometry. This is
a genuine public-data asset and nobody else has assembled it.

**The composite score chain is substantially synthetic.** `graph_topology`
reproduces from the MD5 of the substation name across eight countries.
`R3_C_mult` is SHA-1 jitter over a regional value. Six v4.2 modifiers are a
country baseline plus hash jitter. Component `I` correlates with its own
metrics at r = +0.064. Band labels mean different things in different
countries. 11,361 records still carry a retired modifier.

> **The inputs are measured. The number on top of them is largely
> manufactured. And they are published as one object.**

For an instrument whose purpose is policy decision support, that is the wrong
way round: the composite carries the most authority when cited and has the
least evidence behind it.

### 1.1 The label that should say so does not

`confidence_tier` reads medium on 78.6% of records and high on 8.0%.
To its credit it is not naive — the code carries a guard added after about
78,500 records were published as high-confidence *"on the strength of a
simulation that never happened"*, and 12.7% now read `None`, correctly
declared absent.

But it measures **Monte Carlo interval width** — the precision of the
simulation — not the provenance of the inputs. A record whose criticality
multiplier is a hash produces a perfectly tight interval and reads *medium*.
The one field a policymaker would use to calibrate trust answers a different
question than the one they are asking.

---

## 2 · The risk that should drive the plan

Not that the index is wrong. It is mostly right about the things it measures.

**The risk is a single discovered hash.** One policymaker, referee or LIFE
reviewer tracing one cited number to `md5(substation_name)`. That event
damages the foundation, the grant consortium and the paper programme
simultaneously, and it is not recoverable by explanation afterwards.

It is also now **findable**: today's doctrine is committed to a public
repository. That is the right call and consistent with the openness
decision — protection comes from IP registration, not from withholding — but
it means the defects are discoverable by anyone who reads carefully. The
choice is no longer whether this becomes known. It is whether it becomes known
as *"they declared it"* or as *"someone found it"*.

> **Credibility is the index's only asset. A declared limitation costs
> almost nothing. A discovered one costs everything.**

---

## 3 · Recommendation, in order

### 3.1 Publish the measured layer distinctly from the derived layer — first

Per-field provenance tier on every published field: measured / regional /
derived / synthetic. The markers already exist in fragments — thirteen
record-level `_*` keys, `_catchment_population_source`,
`_migration_score_source` — but there is no systematic split, so a reader
cannot tell which half of a record is evidence.

This is mostly schema and presentation, not new data, and it does the most for
the purpose: **a policymaker can use the measured layer today** — where the
assets are, how many people each serves, what hazard each faces — while the
composite is repaired. It also converts every finding in this folder from an
exposure into a disclosure.

### 3.2 Then repair the chain in consequence order, starting with R3

Per `RECOMMENDATION_R3_C_mult_alpha_to_omega.md`: derive it in the engine from
GHSL catchment population, drop the load term that has 37 records of data,
source or declare every constant, pin the formula to what is computed, prove
it with a 100% reproduction row.

R3 first because it is first in the chain, because the data to do it properly
already exists, and because **doing one modifier completely creates the
template for the other eleven.**

### 3.3 Close the 22 unsanctioned writers

Every defect found today traces to the same root: many hands write published
records. Until one writer owns the payload, each repair is provisional and
this day repeats. This is the least visible and most valuable work available.

### 3.4 Use the conformance ratchet as the plan

Do not write a roadmap. The BLOCKING list is already a measured, prioritised
defect register, it predicted today's work three days early, and the ratchet
now prevents regression. Work the rows; re-pin as they close.

### 3.5 Split the paper programme by layer

Papers that cite the **measured layer** proceed — the seismic screening paper
is exactly this shape and is the right thing to be publishing now. Papers that
cite the **composite score** pause until 3.2 lands.

The mosaic paper's instinct to report its own defects is right and should be
kept. But it currently reports two, and the register holds eleven BLOCKING. A
paper that discloses two of eleven is more dangerous than one that discloses
none, because it claims completeness.

---

## 4 · What I would not do

**Do not re-render the foundational documents yet.** A render reprints
composite figures with the same typographic authority as measured ones, and
pins a formula that matches no implementation. Render after 3.1 and 3.2.

**Do not fix R3 alone and consider the index repaired.** One sound plank in a
floor of twelve is worse than none if it raises apparent credibility without
raising actual credibility. 3.1 is what makes 3.2 safe to do incrementally.

**Do not add a repair script.** It becomes the twenty-third writer and makes
3.3 harder. Repairs belong in the engine.

---

## 5 · Why this order, in one paragraph

The purpose is policy decision support. That makes *usable now* and
*defensible under scrutiny* the two things that matter, and 3.1 delivers both
immediately at low cost: the measured layer is genuinely good and can stand on
its own the day it is labelled as such. Everything after that is repair, and
repair is safest when the thing being repaired has already been declared
imperfect. Doing 3.1 last — repairing quietly and disclosing when finished —
is the sequence that carries the discovered-hash risk for the entire duration
of the work.

---

*This recommendation is about direction and does not settle any of it. The
four open questions in the R3 recommendation, the write-path decision, and the
paper-programme split are all operator decisions.*
