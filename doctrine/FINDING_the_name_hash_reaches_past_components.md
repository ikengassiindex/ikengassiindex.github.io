# FINDING — the name hash reaches past `components`

**Date** 17 September 2026
**Measured on** the deployed tree, all 39 countries, **622,104 substations, every
shard**. Full census.
**Status** measurement only. Nothing published was changed.
**How** exact bit-for-bit reproduction, not correlation. `~/circ/verify_synth.py`
and `~/circ/verify_mods.py` recompute the fill and compare to the published value.

---

## What was already known

`FINDING_what_the_components_fill_costs.md` (17 September 2026) records that
`components.*` is filled by `enrich_esg_gaps` from `vary(0.35, name + '_' + K, 0.30)`
— a hash of the substation's name — on 543,546 records, and that the real
metric-derived value is published alongside as `_I_from_metrics`.

That was treated as a fact about `components`. It is a fact about the script.

## What this adds

The same generator governs six more published fields. `vary` is

    stable_hash(name) = int(md5(f"{name}:42").hexdigest()[:8], 16) / 0xFFFFFFFF
    vary(base, name, spread) = round(base * (1 + (stable_hash(name) - 0.5) * 2 * spread), 4)

Reproduced exactly against the deployed payload:

    field                   base   spread   reproduced           of present   share
    ------------------------------------------------------------------------------
    modifiers.R4_F_topo     0.98    0.03      483,018            543,546      88.9%
    modifiers.R6_restoration 1.02   0.03      483,028            543,546      88.9%
    modifiers.R7_cyber      1.02    0.015     483,058            543,546      88.9%
    modifiers.R6_seismic    1.00    0.03      216,022            597,557      36.2%
    socio_economic.E2_local 0.95    0.12       65,102            540,927      12.0%
    graph_topology.BC_percentile  per-country 0.25   488,378     539,625      90.5%
    graph_topology.degree         per-country 0.30   493,485     543,546      90.8%
    graph_topology.cluster_coeff  0.015  0.40  489,137           536,340      91.2%

483,018 records is **77.6% of the whole estate of 622,104**.

Seven countries reproduce at 100.0% on the modifier block — france, germany,
italy, japan, portugal, spain, us — with uk at 95.7%. Those eight are the eight
largest countries in the estate.

`R4_F_topo` deserves a note of its own. `engine.py:318` computes a real
`F_topo = base(degree) * (1 + 0.10*BC + 0.15*is_bridge)`, and on 78% of the estate
**that function is not what produced the published value**: the published value is
`vary(0.98, name, 0.03)`, which lands in [0.9506, 1.0094] and matches the observed
range exactly. So the published R4 is a name hash around a constant, computed from
a topology that is itself a name hash, by a code path that did not run.

## The dead branch

    gt['is_bridge'] = 1 if gt['degree'] <= 2 and vary(0, name + '_bridge') > 0.7 else 0

`vary(0, ...)` is `0.0` for every input. The condition is never true. **The bridge
fill cannot write a 1.** `is_bridge = 1` appears on 11,243 records across 23
countries, and on none of the seven countries the fill reached completely.

This also explains the mixed typing on the field. Re-counted across the full
census rather than the first shard of each country:

    int:0        496,425   79.8%     fill path
    absent        78,558   12.6%
    bool:False    35,878    5.8%     not the fill
    bool:True     10,990    1.8%     not the fill
    int:1            253    0.0%     UNEXPLAINED

The integers are the fill's output and the booleans are what the fill did not
reach. The 253 `int:1` records are not accounted for: the fill cannot write a 1,
and they are not booleans, so some third writer produced them. That is open.

## What is fair to say, and what is not

**Fair.** The fills are gated `if not sub.get(field)`, so they never overwrite
real pipeline output — Convention #56 visibly-honest degradation, working as
designed. The mechanism is disclosed in doctrine for `components`. Seismic PGA and
the socio-economic baselines in the same script use national reference tables with
genuine location logic, and are a documented proxy under Convention #7.

**Not fair.** The script's docstring states: *"All values are based on published
institutional data, NOT synthetic random numbers."* For `graph_topology` that is
false — `GRAPH_TOPO_DEFAULTS` is a per-country constant and the only per-asset
input is an MD5 of the name, which carries no spatial or structural information.
For the R4/R6/R7 modifier defaults it is false in the same way.

**Not established.** The records that do not reproduce are simply not from this
generator. Whether they are measured is a separate question. Do not read
"9.5% did not reproduce" as "9.5% is real".

## Why this matters now, beyond bookkeeping

**It lands on the R7_cyber_v2 cutover, which is the open decision.**
`R7_cyber` v1 is `vary(1.02, name, 0.015)` on 88.9% of the records carrying it.
The v1 to v2 substitution is therefore not a methodology refinement replacing one
estimate with a better estimate. It replaces a **name hash** with CRA Article 14 +
NIS2 Article 21 register-anchored data. The measured cost of completing the
cutover — 31,726 band changes, 5.1%, Critical +12.2% — was being weighed as a
restatement of published scores. It should be weighed as the retirement of a
placeholder.

**It bounds what the index can currently claim.** Component I, component C/V/E/S/T,
R4, R6_restoration, R7 v1 and the whole topology block are hash fills on most of
the estate. `I1`-`I6` and `_I_from_metrics` are real and derived from primary
sources. The gap between those two statements is the honest description of the
index today.

## Queued, not done

- Whether `R4_F_topo`, `R6_restoration` and `R6_seismic` get the `_from_source`
  treatment `components.I` got — publish the real one alongside, swap on coverage.
- Whether the `is_bridge` dead branch is fixed or the field is withdrawn. It
  cannot be fixed by unblocking the branch alone: there is no bridge data to put
  in it.
- The `enrich_esg_gaps.py` docstring, which currently asserts something untrue of
  the fields above.
- Whether `graph_topology` should be withdrawn from the published payload
  entirely, since it is the field an adversary would most want and the one the
  estate has least right to publish.
