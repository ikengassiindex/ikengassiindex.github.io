#!/usr/bin/env python3
"""
SSI Intelligence — Archive Previous Edition as PDF & Email
Uses Playwright to capture each country's intelligence page as PDF,
then sends all PDFs as email attachments via SMTP.

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
COUNTRIES = ["france", "italy", "uk", "us", "germany", "spain", "switzerland", "austria"]
PDF_DIR = Path("archive_pdfs")


def capture_pdfs():
    """Use Playwright to capture each intelligence page as PDF."""
    from playwright.sync_api import sync_playwright

    PDF_DIR.mkdir(exist_ok=True)

    # Read edition info for filename
    config_path = Path("intelligence/edition-config.json")
    config = json.load(open(config_path, "r", encoding="utf-8"))
    edition_key = config.get("active_edition_key", "unknown")
    edition_num = config.get("current_edition", 0)
    edition_label = f"{edition_num:03d}"

    pdfs = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for country in COUNTRIES:
            url = f"{BASE_URL}/{country}/intelligence.html"
            print(f"  Capturing {country}: {url}")
            try:
                page = browser.new_page()
                page.goto(url, wait_until="networkidle", timeout=60000)
                # Wait for SSI_EDITION to populate (max 10s)
                page.wait_for_function("window.SSI_CONFIG_READY === true", timeout=10000)
                # Additional wait for charts/maps to render
                page.wait_for_timeout(3000)

                filename = f"SSI_Intelligence_Ed{edition_label}_{country.upper()}_{edition_key}.pdf"
                pdf_path = PDF_DIR / filename
                page.pdf(
                    path=str(pdf_path),
                    format="A4",
                    print_background=True,
                    margin={"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"}
                )
                pdfs.append(pdf_path)
                print(f"    Saved: {filename} ({pdf_path.stat().st_size / 1024:.0f} KB)")
                page.close()
            except Exception as e:
                print(f"    ERROR capturing {country}: {e}")
        browser.close()

    return pdfs, edition_label, edition_key


def send_email(pdfs, edition_label, edition_key):
    """Send PDFs as email attachments via SMTP."""
    smtp_server = os.environ.get("SMTP_SERVER", "")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASSWORD", "")
    recipient = os.environ.get("ARCHIVE_EMAIL", "ssi_index@ikenga.eu")

    if not smtp_server or not smtp_user or not smtp_pass:
        print("WARNING: SMTP not configured — skipping email.")
        print("  Set SMTP_SERVER, SMTP_USER, SMTP_PASSWORD secrets in GitHub.")
        return False

    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = recipient
    msg["Subject"] = f"SSI Intelligence Archive — Edition {edition_label} ({edition_key})"

    body = (
        f"SSI Monthly Intelligence — Edition {edition_label}\n"
        f"Period: {edition_key}\n"
        f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        f"Attached: {len(pdfs)} country intelligence reports (PDF).\n"
        f"Countries: {\", \".join(c.upper() for c in COUNTRIES)}\n\n"
        f"This is an automated archive from the SSI Dashboard.\n"
        f"https://ikengassiindex.github.io\n"
    )
    msg.attach(MIMEText(body, "plain"))

    for pdf_path in pdfs:
        with open(pdf_path, "rb") as f:
            part = MIMEBase("application", "pdf")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={pdf_path.name}")
        msg.attach(part)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        print(f"Email sent to {recipient} with {len(pdfs)} PDFs")
        return True
    except Exception as e:
        print(f"ERROR sending email: {e}")
        return False


def main():
    print("=== SSI Intelligence Edition Archiver ===")

    # Check if there is a previous edition to archive
    prev_key_file = Path("prev_edition_key.txt")
    if not prev_key_file.exists():
        print("No previous edition to archive (first run). Skipping.")
        return

    print("Step 1: Capturing PDFs...")
    pdfs, edition_label, edition_key = capture_pdfs()

    if not pdfs:
        print("No PDFs captured. Aborting email.")
        return

    print(f"Step 2: Emailing {len(pdfs)} PDFs...")
    send_email(pdfs, edition_label, edition_key)

    print("=== Archive complete ===")


if __name__ == "__main__":
    main()
