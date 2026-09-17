# FINDING — 70 per cent of the archive is the output of one fixed defect

**Date** 17 September 2026
**Measured on** `archive/` in the deployed repository.
**Status** measurement and a recommendation. Nothing was deleted; deletion is the
operator's.

---

## What is in there

`archive/` is **1.2 GB across 2,141 files**, PDF and HTML intelligence reports in
month folders.

| folder | size | editions held |
|---|---:|---|
| 2026-03 | 66 MB | Ed001–Ed002 |
| **2026-04** | **448 MB** | **Ed003–Ed013 — eleven** |
| **2026-05** | **371 MB** | **Ed014–Ed021 — eight** |
| 2026-06 | 93 MB | Ed022 |
| 2026-07 | 94 MB | Ed024 |
| 2026-08 | 97 MB | Ed026 |

April and May hold **nineteen editions between them**. Every other month holds
one.

## Why, and it is already on the record

This is not a backfill of historical editions, which was my first reading and was
wrong. `scripts/update-edition.py` states it in its own comment:

> "every manual run bumped the edition. The archive records the damage: 11
> editions in April 2026 and 8 in May against one per month due, carrying
> current_edition to 26 while the true monthly count was 6."

The defect is FIXED — the edition is now derived from an epoch rather than
incremented per run. **The 819 MB it produced is still being served.**

## The three numbers that matter

1. **Genuine growth is ~95 MB per month.** June, July and August are 93, 94 and
   97 MB — one edition each, 39 jurisdictions, PDF and HTML. That is 1.14 GB a
   year, against GitHub Pages' 1 GB limit for the published site.
2. **819 MB of the 1.2 GB is the defect's output** — 68 per cent. Seventeen
   editions that were never due.
3. **Nothing served references `archive/`.** Checked directly: no HTML, JS or
   JSON outside the folder itself links into it. The single grep hit is a
   coincidental string inside an OSM cache blob, not a link.

## Two things noticed in passing

**Ed023 and Ed025 exist nowhere in the estate.** June, July and August archived
Ed022, Ed024, Ed026 — the counter advances by two per month while one edition is
archived. Either an edition is generated and discarded each month, or something
still double-increments. `scripts/check_edition_offset.py` exists and may already
cover this; it was not run as part of this finding.

**The retention script would prune nothing.** `scripts/archive-retention.py`
defaults to keeping 12 months and only six exist. Its own docstring says it is
"not wired into the monthly workflow on purpose — retention policy should be a
deliberate human decision, run manually when git repo weight warrants it."

## Recommendation

**Prune 2026-04 and 2026-05, which frees 819 MB from the served site and loses
nothing that was ever due.** Those editions are the output of a defect, not
issues of a publication. `archive-retention.py --keep-months 4 --apply` reaches
2026-05 but also takes 2026-03, which holds the two genuine early editions; the
safer form is to remove the two folders directly, and either way the operator
executes it.

This does NOT shrink the repository. Git history retains every byte, and
reclaiming that needs a history rewrite on a 3.6 GB repo — a separate and
genuinely dangerous decision. What it does is cut the PUBLISHED site by 819 MB,
which is the constraint that actually binds: `FINDING_delivery_and_payload.md`
records tracked content at 4.9 GB against a 1 GB Pages limit that is currently
unenforced.

It also does not stop the ~95 MB monthly growth. That is the delivery decision,
still open, and this finding does not pre-empt it — it removes the part that was
never supposed to be there, so the decision is about 95 MB a month rather than
about 1.2 GB of accumulated noise.
