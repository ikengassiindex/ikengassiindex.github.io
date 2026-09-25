# FINDING — the registration gate guards four buttons, and the code is served verbatim

Measured 24 September 2026, in response to a request to stop unrestricted
access to the working code and "full OECD datasets" on the public website.
Nothing built. No change proposed to the public site, which Pin 1 protects.

---

## 1. What the gate is

`nav.js` defines `showRegistrationGate()`, `isRegistered()` and
`requireRegistration(cb)`. The gate is wired — `data-sections.js` calls
`safeRequireRegistration` at lines 310, 416, 454 and 487, once before each of
the four "Download" cards on every country's `data.html`.

That is its entire reach. Four buttons.

All four generate PDFs **in the browser**, with jsPDF and jspdf-autotable
loaded from cdnjs, from the `ssi-data.json` that `country-renderer.js` has
already fetched unconditionally to render the page. The visitor is holding
the data before the modal is drawn. The gate stands between them and a
re-presentation of what they already have.

It is defeated by `localStorage.setItem('ssi-registered','1')`, by requesting
`ssi-data.json` directly, by any client that is not a browser, or by cloning
the repository.

## 2. What is actually open

`.nojekyll` is present at the repository root, so GitHub Pages serves every
tracked file verbatim with no exclusion rules.

  * 330 `.py` files under `scripts/`, including
    `scripts/pipeline/scoring/engine.py` — which `france/data.html` line 212
    names in prose: "The SSI v4.2 canonical scoring engine is
    `scripts/pipeline/scoring/engine.py`".
  * 75 published data files totalling 2.00 GB of `ssi-data.json`.
  * `tests/`, `doctrine/`, `master documents` renderings, audit reports.

The repository is public. Removing a file from the working tree does not
remove it from history, and history is served over the same public remote.

**Therefore no change to the website can restrict the code or the data.** The
gate is a lead-capture form that resembles a door. It has never been an
access control and nothing on a static site can be one.

## 3. Replacing the form with an email address

Proposed: replace the registration modal with a request to write to
`ssi_index@ikenga.eu` (already the site's contact address, 1,467 `mailto:`
occurrences).

  * As access control it changes nothing, because there was none.
  * It removes the only thing the gate does produce, which is a lead list.
  * It is nevertheless worth doing, for a reason unrelated to access.

The current form transmits email, organisation, organisation type, role,
country and page path **in a URL query string**, via
`new Image().src = SSI_REGISTRATION_ENDPOINT + '?' + params`, to a Google
Apps Script endpoint. Query strings are written to server logs, referrer
headers and browser history. The gate then sets `ssi-registered` and opens
whether or not that request succeeded, so capture is unverified in both
directions — the visitor is admitted without confirmation, and the operator
cannot know a submission was lost.

The modal states the data is "handled by Altinium Invest S.r.L." on a site
operated by Ikenga, with no privacy notice, no stated lawful basis and no
retention period. The controller is EU-resident.

A `mailto:` removes a third-party transfer and a query-string disclosure of
personal data. That is a real improvement in data protection posture. It
should not be described internally as a security measure, because it is not.

## 4. The premise may not hold

**There is no OECD dataset on the site.**

One file in the repository is OECD-named:
`scripts/pipeline/data/korea/oecd_national_socioeconomic.csv` — 198 bytes,
two lines, one data row, for Korea. Its own `_data_source` column reads
`P15-C World Bank Open Data (gdppe:wb; unemp:wb; elder:default)`. It is
misnamed.

Every other OECD reference on the site is editorial: "OECD Context Card",
"OECD Context Card — SAIDI Benchmarking", "OECD peers", "OECD countries",
"OECD DSO observatory". Benchmarking narrative, not redistributed data.

If a request was made to stop publishing "full OECD datasets", either it
points at something this measurement did not find, or the requester has read
benchmarking prose as redistribution. That must be established before
anything is built.

On OECD's own licensing: search results indicate open-by-default since July
2024 and CC BY 4.0. **The terms page did not render and has not been read**,
so this is recorded as unverified per §7.6 and must not be relied on.

Incidental: the Korea file carries `migration_score: 0.5`. It is an INPUT
file, so the 21 September cohort repair did not reach it. If that ingestion
path ever runs it would re-seed the value that
`tests/test_migration_score_niva.py` invariant (7) exists to forbid.

## 5. Where the real third-party exposure would be

Not OECD. If anywhere, `scripts/pipeline/data/*/_osm_cache/` (OpenStreetMap,
ODbL, which carries share-alike obligations a derived database can trigger)
and `scripts/pipeline/data/cross-cutting/gshm-2023-1.tif` (GEM Global
Seismic Hazard Map, 164.8 MB).

Both appear in `.gitignore` — lines 39-40 for `*.tif`, line 77 for
`_osm_cache/` — so they are probably on disk but untracked, and therefore not
served. **Unconfirmed**: this measurement cannot run git (Pin 6). The
operator command `SSI Index/measure_public_surface.sh` settles it.

## 6. The question that decides the remedy

Who asked, and on what basis. The three plausible answers have three
different remedies and none of them is a website form.

  * **OECD** — open-by-default; and nothing of theirs is being redistributed.
    A request on that basis would deserve scrutiny before compliance.
  * **A LIFE-RESILINK consortium partner** — the concern is IP in the working
    code. The remedy is repository visibility: a private pipeline repo and a
    public site repo. Not a form.
  * **A journal or reviewer** — a confidentiality question, different again.

## 7. The cost, stated plainly

The index exists to support policy decision-making on anti-maladaptation and
infrastructure resilience. The journal programme is live and recovering from
a rejection. An email-request wall makes the work non-reproducible in
practice for reviewers at the moment reproducibility matters most, and the
public code is currently the strongest reproducibility claim the project has.

Restriction has a price here. It may still be the right call — but it should
be paid knowingly and not as a reflex.

## 8. Where the line actually is

`ssi-data.json` cannot be gated by any means. The browser must fetch it to
render the site, so any visitor's browser holds it. That is a property of the
architecture, not a policy choice, and it should be published deliberately
rather than half-guarded.

The pipeline is the only place a real choice exists. Splitting it into a
private repository, and publishing the site plus a tagged methodology
snapshot, is the single change that would do anything at all.

Pin 1 protects the design of the public site. Removing the modal is a
behaviour change there and needs the operator's word either way.
