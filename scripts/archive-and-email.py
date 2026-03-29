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
import base64
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime

BASE_URL = "https://ikengassiindex.github.io"
COUNTRIES = ["france", "italy", "uk", "us", "germany", "spain",
             "switzerland", "austria", "canada", "japan", "australia", "chile",
             "denmark", "norway", "finland", "poland", "sweden", "mexico"]
ARCHIVE_DIR = Path("archive")

# Pages to capture per country
PAGES = [
    {"slug": "intelligence", "file": "intelligence.html", "label": "Intelligence"},
    {"slug": "esg-report",   "file": "esg-report.html",   "label": "ESG_Report"},
]

# Graph API attachment size limit: 3 MB per attachment for direct attach,
# larger files need upload session. We'll skip files > 3 MB.
MAX_ATTACHMENT_BYTES = 3 * 1024 * 1024


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

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            token = body.get("access_token")
            if token:
                print("  OAuth2 token acquired successfully")
                return token
            else:
                print(f"  ERROR: No access_token in response: {body}")
                return None
    except Exception as e:
        print(f"  ERROR acquiring token: {e}")
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

    # Build attachments array
    attachments = []
    skipped = 0
    for file_path in files:
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

    body_text = (
        f"SSI Monthly Archive — Edition {edition_label}\n"
        f"Period: {edition_key}\n"
        f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        f"Attached: {len(attachments)} files ({len(pdfs)} PDFs + {len(htmls)} HTMLs)"
        f"{f' — {skipped} skipped (>3 MB)' if skipped else ''}\n"
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

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            status = resp.status
            if status == 202:
                print(f"  Email sent to {recipient} with {len(attachments)} attachments (HTTP 202 Accepted)")
                return True
            else:
                print(f"  Unexpected response: HTTP {status}")
                return False
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"  ERROR sending email: HTTP {e.code} — {error_body[:500]}")
        return False
    except Exception as e:
        print(f"  ERROR sending email: {e}")
        return False


def capture_pages():
    """Use Playwright to capture each country's pages as PDF and HTML."""
    from playwright.sync_api import sync_playwright

    # Read edition info for filename
    config_path = Path("intelligence/edition-config.json")
    config = json.load(open(config_path, "r", encoding="utf-8"))
    edition_key = config.get("active_edition_key") or datetime.utcnow().strftime("%Y-%m")
    edition_num = config.get("current_edition", 0)
    edition_label = f"{edition_num:03d}"

    # Create archive folder: archive/YYYY-MM/
    month_dir = ARCHIVE_DIR / edition_key
    month_dir.mkdir(parents=True, exist_ok=True)

    files = []
    with sync_playwright() as p:
        browser = p.chromium.launch()

        for country in COUNTRIES:
            for page_def in PAGES:
                url = f"{BASE_URL}/{country}/{page_def['file']}"
                name_base = f"SSI_{page_def['label']}_Ed{edition_label}_{country.upper()}_{edition_key}"
                print(f"  Capturing {country}/{page_def['slug']}: {url}")

                try:
                    page = browser.new_page()
                    page.goto(url, wait_until="networkidle", timeout=60000)

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

                    page.close()
                except Exception as e:
                    print(f"    ERROR capturing {country}/{page_def['slug']}: {e}")

        browser.close()

    return files, edition_label, edition_key, month_dir


def main():
    print("=== SSI Monthly Archive — Intelligence + ESG Report ===")
    print(f"Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"Countries: {len(COUNTRIES)}")
    print(f"Pages per country: {len(PAGES)} (Intelligence + ESG Report)")
    print()

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


if __name__ == "__main__":
    main()
