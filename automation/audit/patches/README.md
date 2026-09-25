# Option 3 — Schema parity patches (KB §49.11)

Round-2 sweep on 2026-05-22 surfaced **8 warning-level findings across
6 actionable countries** (plus Greenland, which is pre-launch scaffold
data and is now downgraded to info-level by the audit harness).

Each `{slug}.md` in this folder is a paste-ready patch spec for that
country's `scoring-XX/publish.py` (or whichever script emits the
country's `ssi-data.json`). The specs are deliberately written as
prose+code-snippet checklists rather than as `.patch` files because
the publish.py files are not in this repo — they live in per-country
scoring repos that vary in structure.

## Country summary

| Country | File              | Missing fields                                        | Priority |
|---------|-------------------|-------------------------------------------------------|----------|
| chile   | `chile.md`        | regions[] structurally broken + 2 substation fields   | **HIGH** |
| denmark | `denmark.md`      | markov 20yr horizon entirely absent                   | **HIGH** |
| australia | `australia.md`  | substation.climate_trajectory, confidence_tier        | medium   |
| ireland | `ireland.md`      | substation.climate_trajectory                         | medium   |
| greece  | `greece.md`       | substation.alert_components, version                  | medium   |
| us      | `us.md`           | substation.internal_id                                | low      |

## Verification flow per country

After applying the patch:

1. Re-run that country's pipeline: `python3 score-country.py` (or
   equivalent — exact CLI varies per scoring repo).
2. Diff the new `ssi-data.json` against the previous one — confirm
   only the expected keys changed.
3. Deploy via the country's existing deploy script.
4. Wait for Monday's Stage 7e cron (or trigger manually:
   `gh workflow run runtime-audit.yml -f countries={slug} -f always_send=true`).
5. Confirm the tracking issue and email digest show this country
   as ✓ clean.

## Closure criteria

Option 3 is closed when:
- All 6 countries' patches are merged and deployed.
- A Stage 7e cron run shows ≤ 0 critical / ≤ 0 warning findings
  across the entire fleet.
- The "Runtime audit — open findings" tracking issue auto-closes.

If a country's `scoring-XX` repo doesn't exist yet (some legacy OECD
countries may not have been migrated to the per-country pipeline
convention), document that as a separate "scoring repo migration"
task and skip the patch until the migration lands.
