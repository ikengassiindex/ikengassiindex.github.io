#!/usr/bin/env python3
"""
SSI Monthly Archive — Intelligence + ESG Report Pages
Captures each country's Intelligence and ESG report pages as PDF and HTML,
emails them as attachments via Microsoft Graph API (OAuth2), and saves
them to archive/ folder in the repo.

Environment variables required:
  AZURE_TENANT_ID     — Microsoft 365 tenant ID
  AZURE_CLIENT_ID     — Azure AD app registration client ID
  AZURE_CLIENT_SECRET — Azure AD app registration client secret
  MAIL_SENDER         — Sending mailbox (e.g. ssi_index@ikenga.eu)
  ARCHIVE_EMAIL       — Recipient (default: ssi_index@ikenga.eu)
"""
import json
import os
import sys
import time
import random
import base64
import traceback
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime

BASE_URL = "https://ikengassiindex.github.io"

# ── Retry defaults — applied to transient Playwright + Graph API calls ──
RETRY_MAX_ATTEMPTS = 3
RETRY_BASE_DELAY = 2.0  # seconds; exponential: 2s, 4s, 8s with jitter

# ── Structured run log — written as JSON artifact so the workflow can
# surface capture/email health without scraping stdout. ──
RUN_LOG = {
    "started_at": datetime.utcnow().isoformat() + "Z",
    "finished_at": None,
    "edition_key": None,
    "edition_label": None,
    "countries_total": 0,
    "countries_skipped_pre_launch": [],
    "captures": [],   # list of {country, page, url, status, attempts, error?}
    "email": None,    # {status, attempts, recipient, attachments, skipped?, error?}
    "preflight": {},  # {missing_rotation: [...], warnings: [...]}
}


def retry_with_backoff(label, fn, max_attempts=RETRY_MAX_ATTEMPTS,
                       base_delay=RETRY_BASE_DELAY, retry_on=(Exception,)):
    """Call fn() with exponential backoff + jitter. Returns (result, attempts, error).

    - label      : short string used in log lines (e.g. "graph-token")
    - fn         : zero-arg callable
    - retry_on   : tuple of exception classes that should trigger a retry

    Non-retryable exceptions propagate immediately. On exhausted retries the
    last exception is returned in the tuple rather than raised, so the caller
    can decide to continue, skip, or abort.
    """
    last_exc = None
    for attempt in range(1, max_attempts + 1):
        try:
            result = fn()
            return result, attempt, None
        except retry_on as e:
            last_exc = e
            if attempt >= max_attempts:
                print(f"    [{label}] attempt {attempt}/{max_attempts} FAILED — giving up: {e}")
                break
            delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 1)
            print(f"    [{label}] attempt {attempt}/{max_attempts} failed: {e}. Retrying in {delay:.1f}s…")
            time.sleep(delay)
    return None, max_attempts, last_exc

# ── Single source of truth: intelligence/countries.json ──
# Loaded at module import so any downstream script referencing COUNTRIES
# or FIRST_REFRESH sees a single authoritative copy. The workflow YAML
# reads the same file via a tiny python shim (see monthly-refresh.yml).
_COUNTRIES_JSON = Path(__file__).resolve().parent.parent / "intelligence" / "countries.json"
with _COUNTRIES_JSON.open("r", encoding="utf-8") as _fh:
    _COUNTRIES_CONF = json.load(_fh)
COUNTRIES = list(_COUNTRIES_CONF["slugs"])
FIRST_REFRESH = dict(_COUNTRIES_CONF["first_refresh"])
ARCHIVE_BUNDLES = dict(_COUNTRIES_CONF.get("archive_bundles", {}))
ARCHIVE_DIR = Path("archive")

# Pages to capture per country
PAGES = [
    {"slug": "intelligence", "file": "intelligence.html", "label": "Intelligence"},
    {"slug": "esg-report",   "file": "esg-report.html",   "label": "ESG_Report"},
]

# Graph API attachment size limit: 3 MB per attachment for direct attach,
# larger files need upload session. We'll skip files > 3 MB.
MAX_ATTACHMENT_BYTES = 3 * 1024 * 1024

# KB §91.D — Graph API rejects sendMail payloads over ~35 MB with
# HTTP 400 ErrorMessageSizeExceeded (April 2026 incident: 44.5 MB / 84 atts).
# When the candidate attachment set (after base64 expansion) exceeds this
# soft cap, we drop the PDFs and keep the HTML snapshots only. Rationale:
# HTMLs are the canonical archive (live in the repo under archive/<YYYY-MM>/);
# PDFs are convenience and remain available as workflow artifacts even when
# dropped from the email. Cap is 28 MB to leave headroom for base64 + JSON
# envelope + the ~4/3 expansion factor over the raw bytes already counted.
MAX_TOTAL_EMAIL_BYTES = 28 * 1024 * 1024


def get_graph_token():
    """Acquire an OAuth2 access token using client credentials flow."""
    tenant_id = os.environ.get("AZURE_TENANT_ID", "")
    client_id = os.environ.get("AZURE_CLIENT_ID", "")
    client_secret = os.environ.get("AZURE_CLIENT_SECRET", "")

    if not tenant_id or not client_id or not client_secret:
        print("WARNING: Azure OAuth not configured — skipping email.")
        print("  Set AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET")
        print("  in GitHub repository secrets.")
        return None

    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials",
    }).encode("utf-8")

    req = urllib.request.Request(token_url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    def _do_token_request():
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    body, attempts, err = retry_with_backoff("graph-token", _do_token_request)
    if err is not None:
        print(f"  ERROR acquiring token after {attempts} attempts: {err}")
        return None
    token = body.get("access_token")
    if token:
        print(f"  OAuth2 token acquired successfully (attempt {attempts})")
        return token
    print(f"  ERROR: No access_token in response: {body}")
    return None


def send_email_graph(files, edition_label, edition_key):
    """Send archive files as email attachments via Microsoft Graph API."""
    token = get_graph_token()
    if not token:
        return False

    sender = os.environ.get("MAIL_SENDER", "ssi_index@ikenga.eu")
    recipient = os.environ.get("ARCHIVE_EMAIL", "ssi_index@ikenga.eu")

    pdfs = [f for f in files if f.suffix == ".pdf"]
    htmls = [f for f in files if f.suffix == ".html"]

    # KB §91.D — Drop-PDFs-if-too-large policy. Estimate raw bytes first
    # (base64 expands ~4/3). If the full set would breach the Graph soft
    # cap, drop PDFs and keep HTMLs only. HTMLs are the canonical archive;
    # PDFs are still captured under archive/<YYYY-MM>/ and re-uploaded as a
    # workflow artifact, so nothing is lost — only un-emailed.
    raw_total = sum(f.stat().st_size for f in files)
    b64_estimate = int(raw_total * 4 / 3)
    pdfs_dropped_for_size = False
    if b64_estimate > MAX_TOTAL_EMAIL_BYTES and pdfs:
        pdfs_dropped_for_size = True
        candidate_files = htmls
        print(
            f"  Email payload would be ~{b64_estimate/1024/1024:.1f} MB > "
            f"{MAX_TOTAL_EMAIL_BYTES/1024/1024:.0f} MB cap — dropping "
            f"{len(pdfs)} PDF(s), keeping {len(htmls)} HTML(s) only "
            f"(PDFs remain in archive/ + workflow artifact)"
        )
    else:
        candidate_files = list(files)

    # Build attachments array
    attachments = []
    skipped = 0
    for file_path in candidate_files:
        file_bytes = file_path.read_bytes()
        if len(file_bytes) > MAX_ATTACHMENT_BYTES:
            print(f"    SKIP attachment {file_path.name} ({len(file_bytes)/1024:.0f} KB > 3 MB limit)")
            skipped += 1
            continue

        content_type = "application/pdf" if file_path.suffix == ".pdf" else "text/html"
        attachments.append({
            "@odata.type": "#microsoft.graph.fileAttachment",
            "name": file_path.name,
            "contentType": content_type,
            "contentBytes": base64.b64encode(file_bytes).decode("ascii"),
        })

    if pdfs_dropped_for_size:
        attached_summary = (
            f"Attached: {len(attachments)} HTML snapshot(s) "
            f"— PDFs omitted (email size cap); PDFs remain in repo under "
            f"archive/{edition_key}/ and in the workflow run artifact"
        )
    else:
        attached_summary = (
            f"Attached: {len(attachments)} files ({len(pdfs)} PDFs + {len(htmls)} HTMLs)"
            f"{f' — {skipped} skipped (>3 MB)' if skipped else ''}"
        )

    body_text = (
        f"SSI Monthly Archive — Edition {edition_label}\n"
        f"Period: {edition_key}\n"
        f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        f"{attached_summary}\n"
        f"Pages: Intelligence + ESG Report per country\n"
        f"Countries: {', '.join(c.upper() for c in COUNTRIES)}\n\n"
        f"Save these files to:\n"
        f"  OneDrive > SSI Index Monthly intelligence and ESG Report pages\n\n"
        f"This is an automated archive from the SSI Dashboard.\n"
        f"https://ikengassiindex.github.io\n"
    )

    # Build the Graph API sendMail payload
    mail_payload = {
        "message": {
            "subject": (
                f"SSI Monthly Archive — Edition {edition_label} ({edition_key}) "
                f"— {len(pdfs)} PDFs + {len(htmls)} HTMLs"
            ),
            "body": {
                "contentType": "Text",
                "content": body_text,
            },
            "toRecipients": [
                {"emailAddress": {"address": recipient}}
            ],
            "attachments": attachments,
        },
        "saveToSentItems": "true",
    }

    # POST to Graph API
    graph_url = f"https://graph.microsoft.com/v1.0/users/{sender}/sendMail"
    payload_bytes = json.dumps(mail_payload).encode("utf-8")

    req = urllib.request.Request(graph_url, data=payload_bytes, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")

    # 4xx client errors (bad payload, auth) are not retryable; 5xx + network
    # blips are. We wrap urlopen so only retryable exceptions bubble back
    # into retry_with_backoff.
    def _do_send_mail():
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return {"status": resp.status, "terminal_error": None}
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            if 400 <= e.code < 500:
                # Terminal — return it so retry_with_backoff treats success.
                return {"status": e.code, "terminal_error": f"HTTP {e.code} — {body[:500]}"}
            # 5xx — raise as retryable
            raise RuntimeError(f"HTTP {e.code} — {body[:500]}")

    result, attempts, err = retry_with_backoff(
        "graph-sendmail", _do_send_mail,
        retry_on=(RuntimeError, urllib.error.URLError, TimeoutError),
    )
    RUN_LOG["email"] = {
        "status": None,
        "attempts": attempts,
        "recipient": recipient,
        "attachments": len(attachments),
        "skipped": skipped,
        "pdfs_dropped_for_size": pdfs_dropped_for_size,
        "raw_total_bytes": raw_total,
        "b64_estimate_bytes": b64_estimate,
    }
    if err is not None:
        RUN_LOG["email"]["status"] = "failed"
        RUN_LOG["email"]["error"] = str(err)
        print(f"  ERROR sending email after {attempts} attempts: {err}")
        return False
    if result.get("terminal_error"):
        RUN_LOG["email"]["status"] = "failed"
        RUN_LOG["email"]["error"] = result["terminal_error"]
        print(f"  ERROR sending email (terminal): {result['terminal_error']}")
        return False
    status = result["status"]
    if status == 202:
        print(f"  Email sent to {recipient} with {len(attachments)} attachments (HTTP 202 Accepted, attempt {attempts})")
        RUN_LOG["email"]["status"] = "sent"
        return True
    print(f"  Unexpected response: HTTP {status}")
    RUN_LOG["email"]["status"] = "unexpected"
    RUN_LOG["email"]["error"] = f"HTTP {status}"
    return False


def preflight_rotation_check():
    """Before we spend 5 min driving Playwright, check that every country past
    its FIRST_REFRESH gate has a rotation entry in edition-config.json.

    Returns a dict with {missing: [...], warnings: [...]}. Not fatal — the
    loader already tolerates missing rotation, but surfacing it here makes
    the monthly workflow loud about silent drift.
    """
    result = {"missing_rotation": [], "warnings": []}
    config_path = Path("intelligence/edition-config.json")
    if not config_path.exists():
        result["warnings"].append("edition-config.json not found — cannot preflight.")
        return result
    try:
        config = json.load(open(config_path, "r", encoding="utf-8"))
    except Exception as e:
        result["warnings"].append(f"edition-config.json parse error: {e}")
        return result

    key = config.get("active_edition_key")
    if not key:
        result["warnings"].append("No active_edition_key set (pre-launch).")
        return result

    rotation = (config.get("rotation") or {}).get(key) or {}
    rotation_countries = rotation.get("countries") or {}
    current_ym = datetime.utcnow().strftime("%Y-%m")

    for country in COUNTRIES:
        first_ym = FIRST_REFRESH.get(country)
        if first_ym and current_ym < first_ym:
            continue  # pre-launch — don't care yet
        if country not in rotation_countries:
            result["missing_rotation"].append(country)

    if result["missing_rotation"]:
        print(f"  PRE-FLIGHT WARNING: {len(result['missing_rotation'])} country(ies) past FIRST_REFRESH lack a rotation entry:")
        for c in result["missing_rotation"]:
            print(f"    - {c}")
    else:
        print("  Pre-flight OK: all active countries have a rotation entry.")
    return result


def capture_pages():
    """Use Playwright to capture each country's pages as PDF and HTML."""
    from playwright.sync_api import sync_playwright

    # Read edition info for filename
    config_path = Path("intelligence/edition-config.json")
    config = json.load(open(config_path, "r", encoding="utf-8"))
    edition_key = config.get("active_edition_key") or datetime.utcnow().strftime("%Y-%m")
    edition_num = config.get("current_edition", 0)
    edition_label = f"{edition_num:03d}"
    RUN_LOG["edition_key"] = edition_key
    RUN_LOG["edition_label"] = edition_label

    # Create archive folder: archive/YYYY-MM/
    month_dir = ARCHIVE_DIR / edition_key
    month_dir.mkdir(parents=True, exist_ok=True)

    files = []
    with sync_playwright() as p:
        browser = p.chromium.launch()

        current_ym = datetime.utcnow().strftime("%Y-%m")
        for country in COUNTRIES:
            first_ym = FIRST_REFRESH.get(country)
            if first_ym and current_ym < first_ym:
                print(f"  SKIP {country}: first automated refresh {first_ym} (current {current_ym})")
                RUN_LOG["countries_skipped_pre_launch"].append(country)
                continue
            for page_def in PAGES:
                url = f"{BASE_URL}/{country}/{page_def['file']}"
                name_base = f"SSI_{page_def['label']}_Ed{edition_label}_{country.upper()}_{edition_key}"
                print(f"  Capturing {country}/{page_def['slug']}: {url}")
                capture_entry = {
                    "country": country,
                    "page": page_def["slug"],
                    "url": url,
                    "status": "pending",
                    "attempts": 0,
                }

                page = None
                try:
                    page = browser.new_page()

                    # Retry page.goto — covers network blips and GitHub Pages
                    # cold-cache timeouts. Downstream rendering waits don't
                    # need retry since they already have soft fallbacks.
                    def _do_goto(p=page, u=url):
                        p.goto(u, wait_until="networkidle", timeout=60000)
                        return True

                    _, attempts, goto_err = retry_with_backoff(
                        f"goto:{country}/{page_def['slug']}", _do_goto,
                    )
                    capture_entry["attempts"] = attempts
                    if goto_err is not None:
                        raise goto_err

                    # Wait for data to load
                    if page_def["slug"] == "intelligence":
                        try:
                            page.wait_for_function(
                                "window.SSI_CONFIG_READY === true", timeout=10000
                            )
                        except Exception:
                            pass  # Config may not be active yet (pre-launch)
                    else:
                        # ESG report: wait for KPI grid to render
                        try:
                            page.wait_for_selector("#kpiGrid .kpi-card", timeout=15000)
                        except Exception:
                            pass

                    # Extra wait for charts/maps to render
                    page.wait_for_timeout(3000)

                    # --- PDF ---
                    pdf_path = month_dir / f"{name_base}.pdf"
                    page.pdf(
                        path=str(pdf_path),
                        format="A4",
                        print_background=True,
                        margin={"top": "10mm", "bottom": "10mm",
                                "left": "10mm", "right": "10mm"},
                    )
                    files.append(pdf_path)
                    print(f"    PDF: {pdf_path.name} ({pdf_path.stat().st_size / 1024:.0f} KB)")

                    # --- HTML ---
                    html_path = month_dir / f"{name_base}.html"
                    html_content = page.content()
                    html_path.write_text(html_content, encoding="utf-8")
                    files.append(html_path)
                    print(f"    HTML: {html_path.name} ({html_path.stat().st_size / 1024:.0f} KB)")

                    capture_entry["status"] = "ok"
                    capture_entry["pdf_bytes"] = pdf_path.stat().st_size
                    capture_entry["html_bytes"] = html_path.stat().st_size
                except Exception as e:
                    print(f"    ERROR capturing {country}/{page_def['slug']}: {e}")
                    capture_entry["status"] = "failed"
                    capture_entry["error"] = str(e)
                finally:
                    if page is not None:
                        try:
                            page.close()
                        except Exception:
                            pass
                    RUN_LOG["captures"].append(capture_entry)

        browser.close()

    return files, edition_label, edition_key, month_dir


def write_run_log():
    """Persist RUN_LOG as a JSON artifact the workflow uploads."""
    RUN_LOG["finished_at"] = datetime.utcnow().isoformat() + "Z"
    log_dir = ARCHIVE_DIR / "_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    key = RUN_LOG.get("edition_key") or datetime.utcnow().strftime("%Y-%m")
    log_path = log_dir / f"run-{key}.json"
    try:
        with log_path.open("w", encoding="utf-8") as fh:
            json.dump(RUN_LOG, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        print(f"  Run log written: {log_path}")
    except Exception as e:
        print(f"  WARNING: failed to write run log: {e}")


def main():
    print("=== SSI Monthly Archive — Intelligence + ESG Report ===")
    print(f"Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"Countries: {len(COUNTRIES)}")
    print(f"Pages per country: {len(PAGES)} (Intelligence + ESG Report)")
    RUN_LOG["countries_total"] = len(COUNTRIES)
    print()

    print("Step 0: Pre-flight rotation check…")
    RUN_LOG["preflight"] = preflight_rotation_check()
    print()

    try:
        print("Step 1: Capturing pages as PDF + HTML...")
        files, edition_label, edition_key, month_dir = capture_pages()

        if not files:
            print("No files captured. Aborting.")
            return

        pdfs = [f for f in files if f.suffix == ".pdf"]
        htmls = [f for f in files if f.suffix == ".html"]
        print(f"\nCaptured: {len(pdfs)} PDFs + {len(htmls)} HTMLs in {month_dir}/")

        print(f"\nStep 2: Emailing {len(files)} files to ssi_index@ikenga.eu via Graph API...")
        send_email_graph(files, edition_label, edition_key)

        # Files in archive/ will be committed by the workflow
        print(f"\nStep 3: Archive files ready in {month_dir}/ for git commit")
        print("=== Archive complete ===")
    except Exception as e:
        print(f"FATAL: {e}")
        print(traceback.format_exc())
        RUN_LOG["fatal_error"] = str(e)
        raise
    finally:
        write_run_log()


if __name__ == "__main__":
    main()
