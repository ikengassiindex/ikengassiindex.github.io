# FINDING — the published site is 4.9 GB against a 1 GB limit, and 30.8% of every record is not for the browser

**Status:** measured. Nothing decided, nothing changed.
**Date:** 11 September 2026
**Instrument:** `scripts/measure_record_field_weight.py`

---

## 1. Where the estate stands

| | |
|---|---|
| tracked content (= what GitHub Pages publishes) | **4.9 GB** |
| GitHub Pages published-site limit | **1 GB, hard** |
| enforcement today | **none — site live and current** |

Verified live on 11 September: `HTTP/2 206`,
`content-range: bytes 0-1023/63655236`, `last-modified` sixteen minutes after
the morning's commit. Pages is deploying and serving current content.

Deployment health is fine. Two of the last eight builds show `X`; both are
`conclusion: cancelled`, `build: success`, `deploy: cancelled` — superseded by
a newer push, which is correct behaviour. We pushed eight times that morning.

## 2. Storage and bandwidth are in completely different states

**Bandwidth is not the problem today.** The shards compress 9.1× in practice —
`uk/ssi-data-substations-01.json` is 63,655,236 bytes raw and GitHub serves it
`content-encoding: gzip` at 7,000,058 bytes.

`country-renderer.js` fetches **all** of a country's shards in parallel and
concatenates them, so the per-visit payload is the whole country:

| | files | over the wire | visits per 100 GB |
|---|---|---|---|
| france | 11 | 57.5 MB | 1,779 |
| germany | 10 | 37.7 MB | 2,719 |
| us | 7 | 25.6 MB | 4,007 |
| uk | 5 | 21.0 MB | 4,868 |

Against a 100 GB/month soft limit that is adequate for a specialist audience
and is a hard ceiling on attention: one well-received paper could consume a
month on France alone.

**Storage is the problem and compression cannot touch it.** The limit is on
the deployed site, not the transfer.

Of the 4.9 GB, the website itself — every HTML page, all JS and CSS — is
**5.5 MB**. The rest is data and records. `archive/` is **1.2 GB**, grows ~95 MB
every month via `monthly-refresh`, and is referenced by **zero** served HTML or
JS. A quarter of the published site is fetched by nobody.

## 3. GoDaddy was considered and is disqualified

The company already pays for GoDaddy hosting, so the question was reasonable.
Their published cPanel limits:

| | |
|---|---|
| disk | 25 / 50 / 75 / 100 GB by plan |
| inodes | 250,000 (the estate uses 6,085) |
| **I/O** | **10,240 KB/sec — 10 MB/s, every plan** |
| CPU / RAM | 1–2 cores, 512 MB – 2 GB |
| concurrent entry processes | 20–50 |

**Disk — the number that made it attractive — is the one constraint that was
never binding.** The binding one is I/O.

Serving one France visitor means reading 524 MB from disk to gzip it: **52
seconds of the entire hosting account's I/O for a single page view.** With
pre-compressed files stored on disk, still ~6 seconds. If ikenga.eu shares the
account, an SSI Index visitor degrades the company's own website.

It would also trade a global CDN for a single origin. The live headers show
`via: varnish`, `x-served-by: cache-mad2200116-MAD` — GitHub fronts Pages with
Fastly and a Madrid edge served the test request.

And it would break something harder to price: today **every published byte is
a committed byte**, because the site *is* the repository. FTP deployment severs
that unless rebuilt through CI, and the three bots that push to `main` would
all need reworking with credentials the assistant must never handle. For an
index whose proposition is auditability, that is a cost in the column that
matters most.

**Conclusion: do not migrate to shared cPanel hosting.** If Pages becomes
untenable, the shape that fits is object storage behind a CDN — Cloudflare R2
or Backblaze B2 — with CI publishing from git so the commit-to-published-byte
link survives. To be priced, not decided.

## 4. Splitting audit from display — what is actually safe

A published substation record averages **3,192 bytes**. Measured three ways:

| | share |
|---|---|
| used by the page | **69.2%** |
| not on the page, but read by the estate's own pipeline | **27.9%** |
| read by neither | **2.9%** |

### The trap, and it is the whole point of this section

The first measurement said 28 top-level keys — **30.8% of every record** — are
never named in any served JS or HTML. It is tempting to read that as dead
weight.

**It is not. 21 of those 28 keys are read by the estate's own Python and
workflows.** `osm_type` by 68 consumers, `operator` by 42, `P_critical` by 34,
`R_unclipped` by 32, `alert_flag` by 32, `component_alert` by 33. These are
live inputs to ingestion merges, validators and derivations.

"Not used by the renderer" does not mean "dead". Deleting on the strength of
the display measurement alone would have broken twenty-one fields' worth of
pipeline consumers, and the breakage would have surfaced weeks later inside a
bot run.

### The second guard

A name-based reference scan is only meaningful if nothing reads records
dynamically. Checked: no served code calls `Object.keys`, `for..in`,
`Object.entries`, spread or `JSON.stringify` over a substation record. Every
field reaching the page is named in source.

**If that ever stops being true, the display column becomes worthless and no
split is safe without reading the code first.** The instrument re-checks it on
every run and says so.

### The only safe shape

**Subtractive is unsafe; additive is safe.**

- the full record stays canonical, unchanged, and remains what the pipeline,
  the validators and any external researcher read
- a **derived** slim view is generated from it and is what the browser fetches
- nothing is ever deleted from the record of truth

That is a **30.8% reduction in per-visit bandwidth** with no risk to display
and no loss of auditability — France from 57.5 MB to about 40 MB.

## 5. What the split does not solve, stated plainly

Publishing both representations **increases** storage. The split helps
bandwidth and hurts the limit that is actually breached.

It only helps storage if the full records are kept in git but **not
published** — which the current setup cannot express. Pages builds from the
branch root, and `.nojekyll` is present, so a Jekyll `exclude:` list is
unavailable. That would require moving Pages to Actions-based deployment
(`actions/upload-pages-artifact`) publishing a curated subset.

Even then the arithmetic does not close:

| | |
|---|---|
| slim records, 69.2% of 2.0 GB | ~1.4 GB |
| pages, JS, CSS | 5 MB |
| **published total** | **~1.4 GB against a 1 GB limit** |

Better than 4.9 GB. Still over.

Closing the remaining gap means changing *when* the browser fetches detail,
not just *what* — a map needs an id, a position, a score and a band; the rest
could load when a substation is clicked. That is an architecture change to how
the site loads data, and it is the operator's decision.

## 6. The order that makes sense, none of it decided

1. **Actions-based publishing of a curated subset.** 4.9 GB → ~2 GB. Nothing
   moves, nothing is deleted, no credentials, no change to how the page loads.
   Largest gain for the least risk. Changes the live deployment mechanism, so
   it needs a quiet window.
2. **`archive/` out of the published set.** 1.2 GB, referenced by nothing, and
   it is the entire growth curve. Subsumed by (1) if (1) happens.
3. **The derived slim view.** −30.8% bandwidth, additive, safe.
4. **Lazy detail loading.** Closes the gap. Architecture. Operator's call.
5. **Object storage + CDN.** Only if Pages becomes untenable.

Doing nothing remains defensible: the limit is unenforced, the site is
current, and GitHub's documented first move is an email rather than a
cut-off. The gap widens ~95 MB a month.

## 7. Sources

- GitHub Pages limits — https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
- GoDaddy cPanel resource limits — https://www.godaddy.com/help/resource-limits-12001
