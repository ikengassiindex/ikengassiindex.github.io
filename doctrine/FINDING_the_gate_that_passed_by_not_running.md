# FINDING — the gate that passed by not running

**Date** 25 September 2026
**Occasion** A substation-to-province join for Italy's C metrics. 346 records
carried no province. Recovering the key from their coordinates showed 266 of
them were not in Italy.
**Measured on** all 39 jurisdictions, 622,104 published records, against
Eurostat GISCO 2024 boundaries at 1:1 million, EPSG:4326.
**Status** measurement and repair of the instrument. No published score was
changed. No record was deleted.

## The result

**3,535 substations are filed under a state they are not in.**

```
  germany 1,946   france 554   spain 403   italy 266   us 243   portugal 40
  canada 14   sweden 13   japan 12   uk 10   austria 7   mexico 6   belgium 4
  turkey 3   latvia 2   netherlands 1   poland 1   slovenia 1   chile 1
```

Germany holds 616 French and 604 Austrian substations. France holds 309
German. Spain holds 221 French and 181 Portuguese; Portugal holds 40 Spanish.
The United States holds 161 Canadian and 82 Mexican. The errors are
bidirectional across every land border, which is the signature of a
bounding-box overshoot at ingestion rather than a mistake in any one direction.

Not counted as misfiled, and stated so the number means something: 567 records
in a state's own dependent territories (Puerto Rico 538, Guam 25, US Virgin
Islands 4); 35 in microstates and enclaves whose distribution grid is
integrated with the surrounding country — San Marino, Andorra, Monaco, Ceuta
and Melilla, kept by operator decision; 11 in areas whose boundary is itself
contested, flagged and not adjudicated; and 1,204 offshore within 5 km of
their own coast, median 0.12 km, which is what coastline simplification looks
like.

## Seven mechanisms, each individually reasonable

Discipline #36 exists to catch precisely this. It has a docstring, a
regression history, a per-country tolerance file with written rationale, and
in June 2026 it removed 22,358 substations cohort-wide. It reported all 39
countries clean on the morning of 25 September.

**1. It had no runner.** `check_cross_border.py` was absent from
`scripts/preflight.sh`. The orchestrator ran D#3, 16, 17, 18, 19, 20, 21, 26,
27, 28, 29 and 30. Not 36. Nothing had ever called it.

**2. It failed open.** `shapely` was not installed. The gate caught the
`ImportError`, marked every country SKIPPED, counted skipped as
not-violating, printed `Countries violating: 0` and exited 0:

```
  Countries checked:  39
  Countries skipped:  39
  Countries violating (5.0% outside): 0
  EXIT=0
```

A green light manufactured by a missing dependency. §7.8 says a check that
cannot be RUN is not a check; this one ran, produced output and passed.

**3. The orchestrator defaults to lenient, and every landing takes the
default.** In lenient mode a child gate that finds a hard failure still
reports `✓ PASS`. Run against a slug that does not exist, eleven of twelve
gates passed it; D#17 printed `1 fails` and `✓ PASS` on consecutive lines.
`land_edition_offset_fix.sh` records in its own commit text that the deploy
"would have aborted on fail". In lenient mode it would not. §7.9.

**4. It asked the wrong question.** The test was *is this point inside my own
polygon?* It never asked *is it inside somebody else's?* Membership, not
exclusivity. A substation inside both Italy's polygon and Slovenia's passes.

**5. The tolerance was wide enough to hold a foreign province.** Italy's
configured boundary tolerance is 5.0 km, fifty times the cadastral default,
with a rationale about Ligurian cliffs and Alpine ridges. 345 of Italy's 346
outliers sat within 5 km; the maximum was 5.002. The surviving set is exactly
the set the tolerance admits. Goriška, Savoie, Klagenfurt-Villach and Ticino
all lie within 5 km of the Italian border.

**6. The evidence was discarded where it was needed.** `is_inside_country`
returns `(True, distance)` for tolerated points, and the caller records
`max_dist` only for points it classifies as outside. Every country printed
`Max km 0.0` while 346 Italian records sat between 0 and 5.002 km beyond the
border. The one number that would have exposed this is dropped precisely for
the records that carry it.

**7. The geometry itself was unverified.** `{country}/bounds.json` has no
recorded provenance and is wrong in both directions at once:

```
  slovenia/bounds.json     +33.9%   27,136 km² against a true 20,269
  netherlands/bounds.json  +11.2%
  ireland/bounds.json       +4.2%   reaches north
  france/bounds.json       under-inclusive — invented 3,149 false positives
  norway/bounds.json       under-inclusive — invented   652
  denmark/bounds.json      under-inclusive — invented   216
  portugal/bounds.json     under-inclusive — invented   166
  uk/bounds.json           under-inclusive — invented 1,085
  japan/bounds.json        under-inclusive — invented   107
  greenland/bounds.json    under-inclusive — invented    31
  australia/bounds.json    over-inclusive  — concealed   82
  us/bounds.json           over-inclusive  — concealed  103
```

An over-large polygon hides contamination; an under-large one invents it.
Both were happening simultaneously, in different countries, because nothing
ever compared `bounds.json` to an authority. Greenland's 79% SEVERE — the
case the June audit escalated and then silenced with a tolerance — was 31 of
34 a bad polygon.

## The repair

`scripts/ssi_boundary_source.py` is now the single answer to *what is this
country's polygon and who says so*: GISCO NUTS 2024 for the 26 NUTS
countries, GISCO CNTR 2024 for the other 13 and for every neighbour on earth.
`bounds.json` is not used. A country it cannot resolve is named, not
substituted.

`scripts/check_cross_border_v2.py` makes two independent assertions —
containment, reported with distance for every outlier whether tolerated or
not, and **exclusivity**, which carries no tolerance because no distance makes
being inside another country acceptable. It fails closed: a country that
cannot be evaluated is a failure.

It is wired into `preflight.sh` with `--strict` hardcoded, so D#36 blocks
regardless of the orchestrator's mode. Verified both ways: czechia passes and
authorises deploy; italy fails with `266 substations inside another state` and
exits 1.

`data/quarantine/cross_border_20260925.csv` carries all 5,356 outliers with
substation_id, coordinates, verdict, the state that contains them and their
distance from their own border. It is a manifest. Nothing is deleted here —
Pin 8.

## The resolution, and what the audit changed about it

The operator's instruction was to reassign the 3,535 to the correct fleet,
auditing for duplicates first. The audit changed the answer.

Matching each record against the receiving country's fleet by position:

```
  already present in the destination   3,203
  genuinely new to the destination       323

  match separation:  median 0.04 m
                     2,204 of 2,345 within one metre
                     548 sharing an identical name as well as a position
```

Germany receives 313 France-filed records and all 313 already exist in
Germany. Portugal receives 181 from Spain and all 181 are already there.
Korea 12 of 12, Sweden 3 of 3. These are not neighbouring substations; they
are the same substation, ingested twice — once correctly into its own country
and once into the neighbour by bounding-box overshoot.

**Reassigning them would have manufactured 3,203 duplicate assets.** So the
duplicated are removed from the fleet that should never have held them, and
only the genuinely new are reassigned:

```
  remove     3,197      reassign   342
```

The duplicate threshold is 50 m — three orders of magnitude above the median
match, far below any plausible spacing of distinct substations. The fifteen
records between 50 and 150 m are treated as new and reassigned, because
reassignment is recoverable and removal is less so. Also removed: eight
records whose containing state has no fleet in this cohort (BY, PE, RU, SY),
and the four that had no explanation rather than a rationalised one.

`scripts/ssi_resolve_cross_border.py` performs it, and writes
`data/quarantine/cross_border_resolution_20260925.csv` — every record, its
action, its destination and the reason, whether or not anything is written.

## The lenient default, measured then repaired

Mechanism 3 said the orchestrator defaults to lenient and every landing takes
the default. Measuring before changing it, as it should be: running each child
gate with `--strict` across the cohort, **three** would newly block —
required-files, line-geometry and R3-variance. Not fifty.

And one of those three is advisory by design: preflight's own comment says D#29
is "a health metric pre-flight, not a deploy blocker, until pipeline-layer
cleanup completes". That is a legitimate, written exemption. The defect was
never that some gates are advisory. It is that **all** gates were advisory
because nobody passed a flag.

So the repair separates the two. `--strict` is now the default. `--lenient` is
an explicit, named opt-out that prints a banner and **authorises nothing** —
it exits 1 even with no failures, because a run that enforced nothing cannot
authorise a deploy. Gates that genuinely should not block are named in an
`is_advisory` list with the reason written beside them, and report `⚠ WARN`
rather than `✗ FAIL`.

Verified: czechia passes and authorises; italy fails six gates — D#30, D#17,
D#19, D#26, D#27 and D#36 — every one of which was previously swallowed;
`--lenient` refuses to authorise.

## What enforcing immediately exposed — and one more gate that was not checking

The first full-cohort run with enforcement on found five further failures.
None is a regression; all were present that morning and invisible.

**Two gates could not read the six largest fleets.** D#17 (substation schema)
and D#27 (sub-dict completeness) both loaded `ssi-data.json` directly and read
`data["substations"]`. Convention #79 sharded countries keep no such key in the
manifest, so both gates got an empty list and reported failure — for france,
germany, italy, poland, spain and uk. **419,000 substations, 67 per cent of the
estate, had never been schema-checked.** `scripts/validate_schema.py` had used
the sharding-aware reader all along; these two had not.

Routing both through `scripts/_ssi_data_shard_reader.load_ssi_data` changes the
result in opposite directions, which is how you know it is a real fix:

```
                  before (sharding-blind)          after
  D#17      33 checked, 6 phantom FAILs      39 checked, 2 real FAILs, 5 WARNs
  D#27      33 PASS, 6 FAIL                  39 PASS, 0 FAIL
```

D#27's six failures were entirely the blindness. D#17's six phantoms resolve to
two genuine defects that had never been visible: italy and spain both carry
`socio_economic.rd_pct_gdp` with three unique values across 117 and 65 regions.
Five further countries carry the field not at all.

**Other disclosures from the same run**, recorded and not repaired here:
D#30 — 24 countries with missing files. D#14/15/56 — ireland has 413
substations, 32.3 per cent of its fleet, with R7_cyber outside the registry
range [0.99, 1.05], `IE_100116` at 0.965; new-zealand 27; spain 818 outside its
own bounds. D#26 — 14 countries failing map aesthetic. D#28 — never completed:
it reads every `grid-geo.json`, hundreds of megabytes, and stalled past 900
seconds. A gate nobody can afford to run is a gate nobody runs, which is the
likeliest reason preflight was only ever invoked per-slug.

## What is not established

Whether the 342 reassigned records should carry their existing scores into
their new fleet. Removing them changes fleet sizes, P5/P95
anchors and therefore published bands in Germany, France, Spain, Italy and the
United States simultaneously — a Class M event under §4, and one that
interacts with the component-C work in flight.

Four records remain unexplained rather than resolved: a Japanese substation
268.9 km offshore, `ふくしま絆` at 21.8 km, and two Australian at ~5.5 km, one
of which is at Mildura — inland on the Murray, where no coastline explanation
exists. They are flagged, not rationalised.

The lenient default and its consequences for the other eleven gates are named
here and not repaired. That is a larger change than this finding, and it
should be measured before it is made.
