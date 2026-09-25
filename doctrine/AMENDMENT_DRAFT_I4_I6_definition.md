# Amendment draft — the computation of I4 (RTN density) and I6 (Sub density)

**For flag-officer signature.** Drafted under SSI_FOUNDATION_BIBLE §8: a change
requiring a new value + provenance pin + evidence tier is doctrine, not a Class M
code fix. Nothing has been written to the register.
**Date:** 30 August 2026. **Evidence tier:** Tier 0 — measured on the live
france register and its OSM line geometry.

---

## 1. What the construct fixes, and what it leaves open

`SSI_v4_2_Complete_Formula_Construct_Italy_v3.html` §02/§03/§04 fixes:

    I4 RTN density   intra-weight 0.12   global 0.030   Method B, INVERTED
    I6 Sub density   intra-weight 0.12   global 0.030   Method B, INVERTED
    Inversion: N'(x) = N(P5 + P95 − x), "because higher density = better
    resilience"

It does **not** define how the density is computed at a substation. That is the
gap this amendment closes.

## 2. The two candidate definitions, measured

France: 168,894 substations, 274,201 OSM line features, 295,763 km of line.

**Definition A — local.** Density in the substation's own neighbourhood: line-km
and substation count within a 3×3 block of 0.1° cells (~33 km across).

    I4  min 0.00   p25 275.17   med 425.00   p75 589.83   max 2,829.02  line-km
    I6  min 1      p25 249      med 582      p75 1,179    max 4,183     substations

**Definition B — regional.** A NUTS-3 statistic joined to every substation in the
region: line-km and substations per 1,000 km² of region.

    I4  min 83.01  p25 241.65  med 346.80  p75 416.76   max 1,469.91  km/1000km²
    I6  min 13.45  p25 155.53  med 241.61  p75 551.46   max 1,644.59  subs/1000km²

**They are not interchangeable.** Spearman rank correlation between them:

    I4   0.7038
    I6   0.6743

Roughly a third of the fleet ordering differs. Since these metrics are inverted
and feed R_base at 0.060 combined, the choice changes which substations the index
calls resilient.

## 3. What separates them

**A varies per substation.** It measures local network redundancy — which is
what the construct's own inversion rationale describes ("higher density = better
resilience"). It uses information we hold and would otherwise discard.

**B is constant within a region.** Every substation in a NUTS-3 receives the
same I4 and I6. That is a legitimate Convention #7 documented proxy, and it is
what most other metrics in the register will have to be. But it removes all
within-region discrimination from two metrics where we can afford better.

Under the provenance sweep, A would classify as UNESTABLISHED-but-derived with a
recorded source; B would classify as REGION_CONST.

**Recommendation: A.** It is the more faithful reading of a per-substation
metric, and it is the only one of the two that uses the geometry we already
have. But this is a doctrine call and the recommendation is not the decision.

## 4. A limitation that must be declared either way

"RTN" is the national **transmission** network. The OSM line records carry only
an id and a polyline —

    {'i': 80000000, 'p': [[lon, lat], ...]}

— with **no voltage attribute**. We therefore cannot separate transmission from
distribution lines. What is computable is *OSM power-line density*, not RTN
density.

Under Convention #7 that is acceptable **only if declared as a documented
proxy**, with the substitution named on the record and in the methodology. It
must not be published as "RTN density" without that declaration. This is the
exact failure mode the last two days have been spent removing, and it would be
a poor outcome to reintroduce it at the first honest metric.

France's 295,763 km against RTE's ~106,000 km of transmission indicates the OSM
set mixes both tiers, which confirms the concern rather than allaying it.

## 5. What is requested

Pin one of:

  **A** — local 3×3-cell density, per substation, declared as an OSM power-line
      proxy for RTN
  **B** — regional per-km² density, declared as a Convention #7 documented proxy
  **A with a voltage filter** — deferred until line voltage is re-ingested from
      Overpass, which would make it RTN density in fact and not by proxy

and confirm the cell size for A (0.1°, ~11 km, giving a ~33 km neighbourhood) or
substitute a stated radius.

On signature the derivation lands with a provenance marker naming this
amendment, the definition, and the proxy declaration — and the fills for I4 and
I6 come out of `enrich_esg_gaps.py` in the same commit, per the Step 2 rule that
removal and real derivation land together.
