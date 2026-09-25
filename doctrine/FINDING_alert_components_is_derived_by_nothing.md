# FINDING — `alert_components` is derived by nothing

**Date** 24 September 2026
**Occasion** Deciding where `automation/` sits in the public/private boundary.
**Status** Measured across all 39 countries, 622,104 records.
**Reach** Public. This one is on the site.

## What it is

`alert_components` lists the component codes — C, E, F, P, S, T — that are
flagged on a substation. It drives the alerts panel, and it is consumed by
`map.js` and `intelligence-sections.js`. A reader looking at a substation sees
this field, or sees nothing.

## What computes it

Nothing.

- **29 ingestion modules** write it as a hardcoded empty list: `"alert_components": []`
- **No scoring module computes it.** Not `engine.py`, not `modifier_registry.py`, not anything under `scoring/` or `enrichment/`.
- The only code that has ever populated it is `automation/scripts/apply_parity_patches.py`, described in its own docstring as *"a one-time migration, NOT a recurring hotpatch"*.

The derivation itself is documented — in markdown, in
`automation/audit/patches/greece.md`:

```python
def _alert_components_for(s):
    """List of component codes above their alert threshold."""
    out = []
    for code, val in (s.get("components") or {}).items():
        if val > 0.75:
            out.append(code)
    return out
```

A threshold of 0.75, applied once, by hand, in 2026. It exists as prose in a
patch note and as values frozen in published records. It exists nowhere as
code that runs.

## What that costs, measured

All 39 countries, 622,104 records:

| | |
|---|---:|
| records carrying the key | 619,492 (99.6%) |
| records with a **non-empty** value | **18,932 (3.0%)** |
| countries at **exactly zero** | **19 of 39** |
| records in those countries | **467,848 — 75.2% of the estate** |

The four largest countries in the index are all at zero:

```
france     168,894 records    0.0%
germany    108,016 records    0.0%
us          73,859 records    0.0%
italy       41,662 records    0.0%
```

392,431 records between them. Their alerts panels are empty, have always been
empty, and are empty not because those substations have no flagged components
but because no code ever looked.

Where it is populated, the coverage is arbitrary — australia 61.7 per cent,
turkey 61.5, estonia 30.4, new-zealand 29.7, uk 4.2 — reflecting which
ingestion generation last touched the country rather than anything about the
assets.

## The one-shot did not even hold

Of the six countries `apply_parity_patches.py` was written to patch:

```
australia   61.7%        denmark   0.0%
greece      20.7%        us        0.0%
chile       12.8%
ireland      6.3%
```

**Two of the six are at zero.** Either the patch never applied there, or a
later regeneration overwrote it. Nothing recorded which, because nothing
watches this field.

## Why the R3 write will not fix it, and will not break it

`score_substation` was run against a published Greek record and its key set
compared before and after:

```
before : 56 keys, alert_components present
after  : 58 keys
LOST   : nothing
GAINED : _r3_pop_med, _scoring_fingerprint
```

The rescore preserves the field faithfully. That is the problem in miniature:
the value is carried forward perfectly and re-derived never. A frozen
derivation propagates undisturbed through every subsequent operation, which is
exactly what makes it hard to notice.

## The shape of this

This is the same defect as the name-hash fills, arriving from the other
direction. There, a value was fabricated and published. Here, a value is
*absent* and published — as an empty list, which renders as "no alerts" rather
than as "not computed". Constitution §7.5: no silent absence. An empty list and
an unmeasured field look identical to a reader, and only one of them is honest.

It is also the fourth thing found this session that is preserved by everything
and produced by nothing: the record-level `version` field (seven spellings,
four eras), `W1`–`W10` (specified in 39 reference docs, consumed by the ENN
adapter, computed nowhere), `meta.n_substations` (stale in six countries), and
now this.

## What would close it

Either derive it in the scoring path, where every rescore refreshes it — the
formula is already written in a patch note and wants only a home — or remove
the field and the panel, so the site stops implying an answer it does not have.
Both are honest. Carrying an empty list on 467,848 published records is not.

Not proposed here, and not part of the R3 write. Recorded so the next person to
open the alerts panel and see nothing knows why.

## Related

- `DESIGN_the_public_private_boundary.md`
- `FINDING_the_name_hash_reaches_past_components.md`
- `FINDING_R_base_is_hash_or_zero.md`
- `DESIGN_the_rescore_only_path_and_what_stamps_a_record.md`
