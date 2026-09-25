# NOTE — the workflows must move before the untrack, not after

Measured 24 September 2026, after `scripts/`, `tests/`, `doctrine/`, `data/`
and `audit/` were extracted with their history into the private repository
`ikengassiindex/ssi-pipeline` (415 commits, 797 files, 204 MB, from a 6.43 GB
public repo).

The obvious next step — untracking those paths from the public repo, as
`archive/` and `_v4.0.2.backup/` were untracked earlier the same day — would
break six of seven workflows. Recording why, because the order is not
optional and the failure modes are not all loud.

---

## 1. Every workflow references `scripts/`

| workflow | trigger | commits? | on untrack |
|---|---|---|---|
| `validate.yml` | push: `*/ssi-data.json`, `doctrine/**` | no | fails |
| `validate-schemas.yml` | push: `*/ssi-data.json`, `*/*.html`, `nav.js` | no | fails |
| `test.yml` | push: `scripts/pipeline/**`, `tests/**` | no | **never fires again** |
| `runtime-audit.yml` | Mondays 06:00 UTC | no | fails |
| `pipeline-enrichment.yml` | Thursdays 06:00 UTC | **yes** | fails |
| `monthly-refresh.yml` | Thursdays 10:00 UTC | **yes** | fails |
| `esg-refresh.yml` | Thursdays 11:00 UTC | **yes** | fails |

`test.yml` is the dangerous one. Its trigger paths cease to exist in the
public repo, so it does not fail — it stops, with no run to look at. That is
the same shape as `monthly-refresh.yml`'s `git add -A -- archive/` silently
adding nothing once `archive/` was gitignored, caught earlier today only
because the operator asked whether the change would affect the site.

## 2. The soonest breakage is a push, not a schedule

`validate.yml` and `validate-schemas.yml` fire on any push touching
`*/ssi-data.json`. **The R3 write is exactly such a push.** The schedules
(Monday 06:00, Thursday 06:00/10:00/11:00) are the slower clock.

## 3. Pin 13 is correct

Exactly three workflows `git commit` and `git push`, and they are the three
the pin names. `runtime-audit.yml` is schedule-driven but read-only, which is
why the count is three and not four.

## 4. The split, and the one part that does not divide cleanly

  * **The three derivations + `runtime-audit`** are schedule-driven. They move
    to `ssi-pipeline`, check out the public repo for its data, run, and push
    results back. Needs a write credential — Pin 9, the operator's to create.
  * **`test.yml`** moves unchanged and triggers on private pushes.
  * **`validate.yml` and `validate-schemas.yml`** must stay triggered by
    pushes to the public repo, because that is what they validate, while
    their code would be private.

That last pair carries a decision: **a public repository's Actions logs are
public.** Running the validators in the public repo with code pulled from
private publishes their output — paths, tracebacks, whatever they print —
which partly undoes the split. The alternatives are to keep a small set of
validation scripts public, or to have the public workflow signal the private
one and give up the inline pass/fail. Unresolved; operator decision.

## 5. Order

  1. Migrate the workflows (this note's §4), with the credential in place.
  2. Verify one scheduled run and one push-triggered run succeed from the
     new arrangement.
  3. Only then untrack `scripts/`, `tests/`, `doctrine/`, `data/`, `audit/`
     from the public repo, with the same run-time verification guard that
     `land_20260924_BR.sh` used.

Nothing is broken today. The public repo is unchanged and every workflow
still runs; the private repo holds a copy, not yet a replacement.
