# DOCTRINE — a check must read the artefact, not its description

**Registered** 17 September 2026, from ten failures found in a single session.
**Status** standing. This is not a finding about one defect; it is the shape
every one of those ten took.

---

## The shape

A check is written. It runs. It reports nothing wrong. Nobody looks again,
because a passing check is evidence of health — and it is not. In every case
below the check was **structurally incapable** of reporting the defect it was
built for, and its silence was read as a clean estate.

**The single sentence, if nothing else here is remembered:**

> **"No findings" is a result to be tested, not believed.**

## The ten

Recorded with the specific mechanism, because the abstraction is easy to nod at
and the mechanisms are what recur.

**1. The implementation pointer answered from prose.** The pointer rule matched
text. A dict key in the engine's Monte-Carlo sigma table (`"I1": 0.20,`) and a
line of module docstring (`I3 = IRI_current / 0.30`) both matched; the actual
write, `m["I3"] = round(v, 4)`, could not, because of the `m[` before the
line-start anchor. Not one of the 40 published documents ever named a line that
computes a metric. *Where the question is about code, parse the code.*

**2. A conformance check whose input could never take its failing value.** The
register has always carried an `implementation pointer` row firing on `not
resolved`. The old rule always resolved *something* — a sigma-table key if
nothing better. The check never fired once in its entire life. *A guard whose
input cannot take the failing value is not a guard.*

**3. A case-insensitive test for a case defect.** Denmark's four documents were
named lowercase where 38 others were uppercase. The verification asserted
`os.path.exists()` on the uppercase name, which returns True for a lowercase
file on macOS. *A test blind in the dimension it inspects cannot inspect it.*

**4. A paper verified against the specification instead of the estate.** The I4
decision paper checked the thresholds in the drafts' *proposed* table and assumed
the derivation used them. It had not. Two of five reported "errors" — the UK and
the US — were not errors in the published metric at all, and the scale was
175,265 substations against an actual 44,790.

**5. Three checks silenced by a swallowed programming error.** `SHARD_KEY` was
referenced by three new checks and defined nowhere in that module. Every
reference raised `NameError` inside `except Exception: continue`. All three
reported no rows and read as passes — checks written to catch checks that cannot
fire, which could not fire. *Catch data faults only. A `NameError` is a fault in
your file and must never read as "nothing found".*

**6. Half the surface: the unsharded fallback.** An abstention check read
`substations_shards` directly. Both abstaining countries are unsharded, so the
row silently never fired.

**7. Absence reported without opening the file where the answer lives.** The
register reported I4's abstention rule "undeclared". It is declared — in
`scripts/i4_transmission_thresholds.json`, under `_needs_pin`, with a
per-country basis tested against OSM. Two of three possible locations were
checked and absence was concluded from the two.

**8. One country generalised to the estate.** `components.I` was reported at
**8.1 per cent** of records in conversation and in two committed documents. That
is Poland's figure. Estate-wide it is **87.4 per cent** — and coverage runs from
Austria at 5.0 to France, Germany and Italy at 100. *Name the population inside
the sentence, not in the paragraph above it.*

**9. The gate built for the defect, blind to it.** `check_provenance_citations_
resolve.py` exists to prove every cited document exists, and its docstring names
*this exact citation* — `AMENDMENT_DRAFT_I4_definition.md`, "45 entries across 37
countries pointing one character wrong". The manifest was repaired; the records
were not; the gate reads only the manifest. It reported **"all 5 cited documents
resolve"** and exited 0 while 37 countries' published records cited a file that
exists nowhere. *A gate that reads half the surface will certify the half it
reads.*

**10. The fix for 9 repeated 6.** Extending that gate to the record level, the
first version read `substations_shards` — and only 6 of 39 countries are sharded,
so it looked at no records at all in the other 33 and reported 6 dangling where
37 dangle. **The same blind spot, twice, in one day, by the same hand.**

## The taxonomy

| shape | instances |
|---|---|
| Read the description, not the thing | 1, 4, 7, 9 |
| Input cannot take the failing value | 2 |
| Blind in the dimension inspected | 3 |
| Error swallowed, absence reads as pass | 5 |
| Half the surface enumerated | 6, 9, 10 |
| One place generalised to all places | 8 |

Eight of the ten were found only because something *else* looked wrong first.
That is the uncomfortable number: the detection rate of looking directly was
close to zero, and the detection rate of pulling a thread that felt wrong was
close to one.

## The rules that follow

1. **Read the artefact.** A specification, a docstring, a draft, a filename or a
   register entry describing the thing is not the thing. Where they can disagree,
   they have.
2. **Prove the check can fail.** Before trusting a green result, make the defect
   and watch it go red. A check that has never once fired is a thing to test
   deliberately, not evidence of health.
3. **A check that flags all of its inputs, or none of them, is not
   discriminating.** The provenance-citation check earns its place because it
   passes three registered documents and flags two drafts and one missing file.
4. **Catch narrow exceptions around measurement.** `except (OSError, ValueError)`
   for data faults. Never `except Exception` — it converts your own bugs into
   silence that looks like health.
5. **Enumerate the surface before writing the check.** Sharded and unsharded.
   Manifest and record. Both encodings of a sentinel — `kv` absent and `kv = 0`
   mean the same thing and are written differently in different countries.
6. **Name the population inside the claim.** "8.1 per cent, measured on Poland"
   is a fact. "8.1 per cent" is an error waiting to be quoted.
7. **State the sampling.** Where a check reads a head, a first shard or 200
   records, the output says so, so nobody reads it as a census.

## What is mechanised, and what is still only written here

Rules 3, 4, 5 and 7 are now enforced in code: the conformance register's
provenance-citation, declared-blocked-found-on-records and
coefficients-outside-doctrine rows; narrowed exception handling in the three
record-level helpers; the sharded/unsharded fallback; and the sampling statement
carried in each row's note.

**Rules 1, 2 and 6 are not mechanisable and rest on the reader.** They are the
three that produced eight of the ten failures.
