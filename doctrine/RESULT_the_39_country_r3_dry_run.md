# RESULT — the 39-country R3 dry run, the step-6 gate

Run 24 September 2026, 4,510 seconds. Nothing written.

`DESIGN_the_rescore_only_path_and_what_stamps_a_record.md` §5 step 6:
"Measure. 39 dry runs, read before anything is written... if the dry run says
the estate moves more than the R3 re-derivation and the seed can account for,
the answer is to stop and find out why, not to write."

This is that reading. Fingerprint `75f33c4b2a42`, cohort pop_med 27,513 from
618,251 measured catchments.

---

## 1. Headline

38 of 39 countries completed. **turkey failed outright**, so 4,031 records
were not measured at all (§3).

| | countries | records | moved | bands vs published |
|---|---:|---:|---:|---:|
| attributable | 33 | 219,474 | 131,621 | 31,255 (**14.2%**) |
| stale-baseline | 5 | 398,599 | 349,155 | 96,226 (**24.1%**) |
| **total** | **38** | **618,073** | **480,776 (77.8%)** | **127,481 (20.6%)** |

R3 written on 614,221 records; removed under Convention #56 on 3,788.

The 14-country sample taken before the sweep predicted 20.0% band movement.
The estate figure is 20.6%. The sample was representative, which is worth
recording because it was chosen for size and not for representativeness.

## 2. The two halves are different, and must not be merged

The five stale-baseline countries — france, germany, us, italy, japan — move
almost twice as much as the other 33 (24.1% against 14.2%) and hold 64% of
the estate. Their published `mult_product` does not reproduce from their own
modifiers, so their movement is the re-derivation PLUS accumulated drift and
**cannot be attributed**.

That is not a caveat on the headline; it is the reason there is no single
headline. 20.6% is an average over two populations that differ in kind.

## 3. turkey failed: KeyError 'substation_id'

`merge_and_rescore` does `sid = sub["substation_id"]` unconditionally. Turkey
holds 4,001 records with one (`TR-TR-0001` style) and **30 without**. The
missing-id records carry `osm_id`, real names ("Yunus TM"), coordinates, and
`version: None` — the same 30 the version scan found on 24 September.

Thirty records stopped a country of 4,031 from being measured, because the
access is a subscript and not a `.get`. A record without an id should be
reported and skipped, not raise.

**turkey must be fixed before any write.** A staged write that silently omits
one country leaves the estate at two methodology vintages with nothing on the
records to say which is which — the defect the fingerprint exists to prevent.

## 4. 283 records carry a catchment population of exactly zero

Reconciling the removal count: 3,569 records have no catchment population,
3,788 lost their R3. The difference is 283 records whose population is present
and **equal to 0** (none are negative), less 64 that had no R3_C_mult to lose.

    us 148 · australia 66 · canada 60 · norway 5 · new-zealand 1 ·
    mexico 1 · iceland 1 · chile 1

`compute_r3` rejects them correctly — a zero catchment is not a catchment.
But a zero stored as a measured population is the same class as the 373
records published at `R_median == 0`: a value that reads as measured and is
not. GHSL has no zero-population cell that a substation can sit in; a
zero here is a join that failed and was recorded as a number.

## 5. What moved most, and why the big countries moved least per record

    country        recs     moved   max|d|   bands vs published
    france      168,894   143,686   0.1212   40,703  (24.1%)
    germany     108,016    91,209   0.0986   21,409  (19.8%)
    us           73,859    67,246   0.1697   23,775  (32.2%)
    uk           59,744    57,277   0.2479   10,741  (18.0%)
    italy        41,662    40,968   0.1585    8,817  (21.2%)

The largest countries show the SMALLEST maximum delta (germany 0.0986,
czechia 0.0944) while small countries reach 0.33 (canada, iceland, finland).
That is the sigmoid behaving as designed: a dense country's catchments cluster
near the cohort median, so R3 lands near 1.0; a sparse country's spread across
the curve. It is a property of the derivation, not an artefact.

## 6. Recommendation

Not a single estate-wide write.

  1. **Fix turkey first.** Make the id access defensive and decide what the
     30 records are (§3, and
     `FINDING_three_countries_carry_two_ingestion_generations.md`).
  2. **Write the 33 attributable countries**, one at a time, running
     `scripts/normalise_bands_per_country.py` after each, per the operator's
     24 September decision. 14.2% band movement, explainable by a named
     change.
  3. **Hold the five stale-baseline countries.** Writing them publishes a
     24.1% band movement that cannot be attributed to the re-derivation, on
     64% of the estate. Their baseline has to be reproduced first — that is
     its own task and it predates this one.
  4. The 283 zero-population records and the 373 zero-`R_median` records are
     the same question and should be settled together, separately from this.

## 7. What this measurement does NOT establish

The movement is real and the derivation is correct. It says nothing about
whether the inputs are.

`FINDING_R_base_is_hash_or_zero.md` establishes that `R_base` is an MD5 of
the substation's own name on 77.5% of records and exactly zero on 12.6% —
verified independently on 24 September at 78,558 records with no components
and 78,663 with `R_base_median == 0`. The bands moving here are, for most
records, bands over fabricated components.

That does not argue against the write. Correcting R3 and making the chain
reproducible is a prerequisite for anything else. It argues against quoting
20.6% as a resilience finding, in a paper or on the site, without that
qualification attached.
