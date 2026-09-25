# REGISTER — credentials, where they live, and when they die

**Opened** 24 September 2026
**Why** Every credential in this estate fails the same way: silently. A token
lapses, the thing it authenticated stops, and the only trace is a log line
nobody reads. Four such dates were discovered in a single afternoon, none of
them written down anywhere.

This register is the write-down. It carries no values — only names, locations
and dates.

---

## The credentials

| name | where | expires | what stops if it lapses |
|---|---|---|---|
| `PUBLIC_REPO_TOKEN` | `ssi-pipeline` secret | **30 Jun 2027** | every private workflow's push to the public repo |
| `CDS_API_KEY` | `ssi-pipeline` secret | *unknown — see below* | Copernicus climate retrieval (ERA5 / CERRA) |
| `AZURE_TENANT_ID` | `ssi-pipeline` secret | n/a — an identifier | — |
| `AZURE_CLIENT_ID` | `ssi-pipeline` secret | n/a — an identifier | — |
| `AZURE_CLIENT_SECRET` | `ssi-pipeline` secret, from Entra secret "ssi-pipeline 2026-09" | **~24 Sep 2028** | the Graph email digest |
| `AZURE_CLIENT_SECRET` | `ikengassiindex.github.io` secret, from Entra secret "SSI GitHub Actions" | **19 Mar 2028** | the public repo's digest, until its workflows retire |
| — | Entra secret "SSI Campaign April 2026" | **26 Sep 2026** | nothing found. Deliberately allowed to lapse; see below |

Entra app: **SSI Dashboard Mailer**, `cc698bd4-894a-4823-b2c7-c9f4f8f6b338`,
tenant `fba82a8a-b0f6-427b-b5d5-7472ff9fe230` (IKENGA SL / ikenga.eu). Graph
permission `Mail.Send`, type **Application**, admin consent granted.

## The two identifiers are not secrets

Tenant ID is published by Microsoft for any domain — it is readable from
`login.microsoftonline.com/ikenga.eu/v2.0/.well-known/openid-configuration`
without authentication. Client ID is an identifier on a settings page. Only the
client secret is a secret, and it is visible exactly once, at creation.

## "SSI Campaign April 2026" is being allowed to die

It expires 26 September 2026 and **nothing in the estate was found to use it**.
The only code paths that authenticate with a client secret are
`scripts/archive-and-email.py` and `automation/scripts/send_audit_digest.py`,
both of which read `AZURE_CLIENT_SECRET` from the environment — which on GitHub
is the secret named "SSI GitHub Actions". The outreach mailer does not touch
this app at all: `Media/outreach/daily_sender.py` uses
`msal.PublicClientApplication` with a Microsoft first-party client ID and the
device-code flow, and says so in its own comment.

A client secret cannot be extended. Azure has no renew — a replacement is
created and the old one retired. Letting this one lapse is therefore a
measurement: if something breaks on 26 September, we learn what used it, which
is more than we know now.

## What is still unknown

**The Copernicus token has no recorded expiry.** It is an ECMWF Data Stores
Personal Access Token, held in the live `.env` as `EWDS_API_KEY` — named for
the Early Warning Data Store because that is the portal it came from, though it
authenticates against the Climate Data Store too, verified 24 September. Its
expiry is on the profile page at `cds.climate.copernicus.eu` and belongs in the
table above.

## How to check, rather than assume

`ssi-pipeline` carries **Credential check**, dispatch-only. It probes each
credential three times — with rubbish, with nothing, then with the real value —
and discards its own result if either control is accepted. Run it after any
credential change, and before relying on one.

Verified 24 September 2026, run #2, 33 seconds:

```
CDS_API_KEY authenticates              (profile and retrieve)
PUBLIC_REPO_TOKEN authenticates
Graph client credentials authenticate
```

## Why this register exists at all

The previous credential validator in the estate — `ssi_enn_v30/scheduler/
validate_credentials.py` — reported "token valid" for the placeholder string
`PASTE_YOUR_TOKEN_HERE`, for sixteen letter z's, and for the single character
`z`, because it probed a public catalogue endpoint that answers 200 without
authentication. It had never been able to fail. See
`DOCTRINE_a_check_must_read_the_artefact.md` and
`FINDING_the_conformance_register_reads_the_engine_against_itself.md`.

A date in a table is a weaker instrument than a check that runs. But a date
nobody wrote down is not an instrument at all.
