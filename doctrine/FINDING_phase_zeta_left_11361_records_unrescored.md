# FINDING — Phase ζ left 11,361 records unrescored, and the register saw it

**Date** 21 September 2026
**Found** by following one row of the conformance register after ζ/η landed
**Severity** published scores computed under a retired modifier — §7.2

---

## 1 · How it surfaced

Re-running the conformance register after ζ/η closed four rows. One that did
not close reads:

> `R7_cyber + R7_cyber_v2` · *mutual exclusivity* · **both reproduce as applied
> on 574 sampled assets** · BLOCKING

alongside `R7_cyber` · *retired* · **0.0% applied**, which now conforms.

Those look contradictory. **They are not**, and the first hypothesis here was
wrong. `conformance.py:437–457` classifies every sampled asset into one of four
mutually exclusive shapes — v1 alone, v2 alone, both, none reproduce — and
reports each as a separate row. v1-alone is 0.0%; v2-alone is 81.8%; *both* is
574 assets. Different buckets, not competing measurements.

The real question is why **any** asset still reproduces with both applied,
when ζ rescored the estate and `compute_modifier_terms` skips the retired v1.

## 2 · The measurement

Against the pre-ζ snapshot, restricted to the 543,546 records carrying the
retired `R7_cyber` key:

| | records | |
|---|---:|---:|
| `R_median` moved in ζ | 532,185 | 97.9% |
| **`R_median` unchanged** | **11,361** | **2.1%** |

A second hypothesis — that the unchanged ones simply hold `R7_cyber = 1.0`, so
removing it changes nothing — was tested and **refuted**:

| | n | min | p50 | max | exactly 1.0 |
|---|---:|---:|---:|---:|---:|
| unchanged | 11,361 | 0.9670 | **1.0112** | 1.0460 | **4** (0.0%) |
| moved | 532,185 | 0.9310 | 1.0189 | 1.0856 | 5,096 (1.0%) |

Only four are neutral. The median unchanged record carries 1.0112, so dropping
the modifier *should* have moved it by about 1.1%. It did not.

**So those 11,361 records were not rescored.** Their published `R_median` was
computed while the retired v1 was still in the chain, and it still is.

By country: turkey 4,001, uk 3,998, france 862, canada 736, germany 603,
italy 337, norway 291, sweden 160, portugal 100, spain 76.

Turkey is the sharp case: 4,001 of its 4,031 records — effectively the whole
national fleet.

## 3 · The mechanism

`merge_and_rescore` rescores only where an ingestion input changed:

```python
needs_rescore = has_seismic or has_climate or has_socio
...
else:
    updated_subs.append(sub)          # untouched
```

A record that no ingestion stage matched is appended unchanged. That is
reasonable when a rescore would be a no-op — and it is exactly wrong when the
*modifier chain itself* has changed underneath, as it did at the v4.24 cutover.

> **A rescore gated on input change cannot deliver a methodology change. The
> gate asks whether the inputs moved; a retirement moves the function.**

## 4 · What this means for what was landed

Commit `866f3fc0` says ζ applied the v4.24 R7 retirement across the estate.
That is true of 97.9% of the affected records and **not true of 11,361 of
them**. The estate is now in two states at once: most scores computed without
v1, and 11,361 computed with it.

This does not change the band-migration measurement materially — those records
did not move, so they contributed nothing to the 80,474 band changes — but it
does mean the cohort is not internally consistent, and any cross-country
comparison involving turkey is comparing a fleet scored under the old chain
against fleets scored under the new one.

## 5 · Remedy, not yet designed

The records need a rescore that is **not** gated on input change. Options, in
increasing order of blast radius:

1. a targeted pass over records whose `modifiers` carry a retired key,
   recomputing `R_median` from the stored components and the surviving chain;
2. a `--force-rescore` flag on the merge, mirroring `--force-rewrite` on the
   migration enrichment;
3. re-running ζ with ingestion forced to report every record as changed.

(1) is narrowest and is probably right, but it writes published records, and
the register already carries `published record / write paths` as BLOCKING with
22 unsanctioned writers. **A repair script is the twenty-third.** That tension
should be resolved deliberately rather than by adding one more.

## 6 · The register found this, not the session

The row was in the register before ζ ran and it is still open now. Reading the
BLOCKING rows first would have predicted this failure mode: a retired modifier
still reproducing as applied is exactly what an input-gated rescore leaves
behind.

Two hypotheses were formed and refuted before the measurement stood — that the
register contradicted itself, and that the unmoved records were neutral. Both
took a minute to test. The register's row was right the whole time.
