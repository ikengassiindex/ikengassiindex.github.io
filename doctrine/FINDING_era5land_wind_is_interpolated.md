# Finding — ERA5-Land's wind carries no information ERA5 does not already have

Raised 2026-09-10, on the operator's question: should the 0.1° route be tried
for the sake of understanding it? It was the right question. The answer cost
two searches instead of 250 GB and two weeks.

---

## 1. What was proposed, and why it is now withdrawn

I2's measured field at 0.25° is close to a regional constant: 168,780 French
substations map onto 1,138 distinct grid cells, and the UK's whole fleet spans
6.2 m/s from P5 to P95 (CV 0.066). I attributed that to the resolution choice
and said the 0.1° ERA5-Land route would recover the local exposure differences
I2 exists to capture.

**That attribution was wrong.** ERA5-Land does not resolve wind at 0.1°.

## 2. The mechanism, from two sources

ERA5-Land is a land-surface rerun driven by atmospheric forcing taken from
ERA5. Its documentation states the forcing is interpolated from ~31 km to
~9 km, and that local adjustments are applied to **relative humidity, air
temperature and surface pressure**. Wind is not in that list.

A second source states it directly: winds in ERA5-Land "are only forcing
fields, which means they are nothing but the data from ERA5 interpolated at the
higher resolution of 0.1 degrees (vs. the original 0.25 degrees)", and that
only soil and surface parameters benefit from the finer grid.

So ERA5-Land 10 m wind is ERA5 10 m wind, resampled. Sampling it at 0.1° yields
6.25x as many distinct cell values carrying the same 31 km structure.

There is a further reason not to use it: published work reports a systematic
under-representation of ERA5 10 m wind speeds in ERA5-Land, enough to undermine
wind-energy studies. Not merely no gain — a documented bias.

## 3. What this settles, and what it does not

**Settles.** The hourly ERA5-Land option is withdrawn. It would have cost
~250 GB and about two weeks to obtain the same wind field, resampled and biased
low. It would also have produced a HIGHER apparent spread between substations —
more distinct cell values — which would have looked like an improvement and
been an artefact of interpolation. That is the outcome worth naming: the
experiment would have appeared to succeed.

**Settles.** The gust route was correct, and for a reason I had not identified.
ERA5 single levels at 0.25° is the native resolution of the wind field. Nothing
inside the ERA5 family resolves it more finely.

**Does not settle.** Whether I2 is worth populating. The low between-substation
variation is real and is not a defect of our source choice — it is the
resolution of ERA5's wind. Any I2 built on ERA5 will separate 31 km cells
rather than substations, whatever threshold is pinned.

## 4. The only route to genuinely finer wind

Outside the ERA5 family:

    CERRA        regional reanalysis, 5.5 km, EUROPE ONLY. Genuinely
                 higher-resolution atmosphere, not interpolation. Would cover
                 perhaps 25 of the 39 jurisdictions and leave the rest on
                 ERA5 — a resolution inconsistency inside one metric, which
                 is worse than a uniform coarse one unless declared per
                 country.
    national     Wind atlases exist for several jurisdictions at 1 km or
    atlases      finer. Under the national-primary discipline this is the
                 doctrinally preferred route and the most expensive: a
                 different source, licence and ingestion path per country.

Neither is a small change, and neither is proposed here.

## 5. Recommendation

Pin a threshold on the gust field and publish I2 with the resolution declared
as INTRINSIC to the source rather than as a choice — or leave I2 unpopulated at
0.629 coverage. Those are the two honest options today. The third, a finer wind
source, is a project, not a step.

The declaration, if I2 is populated, must say: this metric separates 31 km grid
cells, not individual substations; two substations 20 km apart will commonly
carry the same value; and that limit is ERA5's, not a decision that could have
been made better.
