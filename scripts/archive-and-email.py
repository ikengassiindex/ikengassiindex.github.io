#!/usr/bin/env python3
"""
SSI Monthly Archive — Intelligence + ESG Report Pages
Captures each country's Intelligence and ESG report pages as PDF and HTML,
emails them as attachments, and saves them to archive/ folder in the repo.

Environment variables required:
  SMTP_SERVER   — SMTP host (e.g. smtp.ikenga.eu)
  SMTP_PORT     — SMTP port (default 587)
  SMTP_USER     — SMTP username
  SMTP_PASSWORD — SMTP password
  ARCHIVE_EMAIL — Recipient (default: ssi_index@ikenga.eu)
"""
import json
import os
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from pathlib import Path
from datetime import datetime

BASE_URL = "https://ikengassiindex.github.io"
COUNTRIES = ["france", "italy", "uk", "us", "germany", "spain",
             "switzerland", "austria", "canada", "japan", "australia", "chile"]
ARCHIVE_DIR = Path("archive")

# Pages to capture per country
PAGES = [
    {"slug": "intelligence", "file": "intelligence.html", "label": "Intelligence"},
    {"slug": "esg-report",   "file": "esg-report.html",   "label": "ESG_Report"},
]


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


def send_email(files, edition_label, edition_key):
    """Send archive files as email attachments via SMTP."""
    smtp_server = os.environ.get("SMTP_SERVER", "")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASSWORD", "")
    recipient = os.environ.get("ARCHIVE_EMAIL", "ssi_index@ikenga.eu")

    if not smtp_server or not smtp_user or not smtp_pass:
        print("WARNING: SMTP not configured — skipping email.")
        print("  Set SMTP_SERVER, SMTP_USER, SMTP_PASSWORD secrets in GitHub.")
        return False

    # Separate PDFs and HTMLs
    pdfs = [f for f in files if f.suffix == ".pdf"]
    htmls = [f for f in files if f.suffix == ".html"]

    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = recipient
    msg["Subject"] = (
        f"SSI Monthly Archive — Edition {edition_label} ({edition_key}) "
        f"— {len(pdfs)} PDFs + {len(htmls)} HTMLs"
    )

    body = (
        f"SSI Monthly Archive — Edition {edition_label}\n"
        f"Period: {edition_key}\n"
        f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        f"Attached: {len(pdfs)} PDF files + {len(htmls)} HTML files\n"
        f"Pages: Intelligence + ESG Report per country\n"
        f"Countries: {', '.join(c.upper() for c in COUNTRIES)}\n\n"
        f"Save these files to:\n"
        f"  OneDrive > SSI Index Monthly intelligence and ESG Report pages\n\n"
        f"This is an automated archive from the SSI Dashboard.\n"
        f"https://ikengassiindex.github.io\n"
    )
    msg.attach(MIMEText(body, "plain"))

    for file_path in files:
        with open(file_path, "rb") as f:
            if file_path.suffix == ".pdf":
                part = MIMEBase("application", "pdf")
            else:
                part = MIMEBase("text", "html")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={file_path.name}")
        msg.attach(part)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        print(f"Email sent to {recipient} with {len(files)} attachments")
        return True
    except Exception as e:
        print(f"ERROR sending email: {e}")
        return False


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

    print(f"\nStep 2: Emailing {len(files)} files to ssi_index@ikenga.eu...")
    send_email(files, edition_label, edition_key)

    # Files in archive/ will be committed by the workflow
    print(f"\nStep 3: Archive files ready in {month_dir}/ for git commit")
    print("=== Archive complete ===")


if __name__ == "__main__":
    main()
