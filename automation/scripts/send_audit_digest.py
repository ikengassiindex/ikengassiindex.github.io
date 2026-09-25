#!/usr/bin/env python3
"""
Stage 7e — Microsoft Graph email digest sender (KB §49.10).

Reads the latest runtime-audit-{ISO}.json report produced by
`runtime_audit.py`, renders an HTML digest, and posts it via
Microsoft Graph /sendMail to ssi_index@ikenga.eu (same channel
already used by scripts/archive-and-email.py for monthly bundles).

Auth: client-credentials OAuth2 flow against Entra ID, identical
secret set:

    AZURE_TENANT_ID
    AZURE_CLIENT_ID
    AZURE_CLIENT_SECRET
    GRAPH_SENDER_UPN     (the licensed mailbox; defaults to
                          ssi_index@ikenga.eu)

Exit code: 0 on success; 1 if the send fails. The harness can choose
to ignore the exit code (we don't want a bad email channel to mark
the audit run itself as failed).

Invocation:

    python3 send_audit_digest.py audit/_logs/runtime-audit-2026-05-25.json
    python3 send_audit_digest.py --latest audit/_logs/

Behaviour:
    · If `critical_count == 0 and warning_count == 0`, no email is sent
      (the digest is signal-only, not heartbeat — heartbeat is the
      workflow's GitHub Actions run history).
    · Recipients default to ssi_index@ikenga.eu; override with
      `--to` (comma-separated) or env `AUDIT_DIGEST_TO`.
"""
from __future__ import annotations
import argparse, base64, datetime, json, os, sys
from pathlib import Path
import urllib.request, urllib.parse, urllib.error

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
TOKEN_URL  = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
DEFAULT_TO = "ssi_index@ikenga.eu"


def get_token() -> str:
    tenant = os.environ["AZURE_TENANT_ID"]
    client = os.environ["AZURE_CLIENT_ID"]
    secret = os.environ["AZURE_CLIENT_SECRET"]
    data = urllib.parse.urlencode({
        "client_id":     client,
        "scope":         "https://graph.microsoft.com/.default",
        "client_secret": secret,
        "grant_type":    "client_credentials",
    }).encode()
    req = urllib.request.Request(
        TOKEN_URL.format(tenant=tenant),
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())["access_token"]


def latest_report(log_dir: Path) -> Path:
    candidates = sorted(log_dir.glob("runtime-audit-*.json"))
    if not candidates:
        raise FileNotFoundError(f"No runtime-audit-*.json in {log_dir}")
    return candidates[-1]


def severity_badge(count: int, kind: str) -> str:
    if count == 0:
        return f'<span style="color:#7a7a7a">0 {kind}</span>'
    if kind == "critical":
        color = "#b91c1c"
    elif kind == "warning":
        color = "#b45309"
    else:
        color = "#1f2937"
    return f'<span style="color:{color};font-weight:600">{count} {kind}</span>'


def render_html(run_data: dict, repo_slug: str, run_url: str | None) -> str:
    started = run_data.get("started_at", "")[:19].replace("T", " ")
    total   = run_data.get("total_findings", 0)
    crit    = run_data.get("critical_count", 0)
    warn    = run_data.get("warning_count", 0)
    n       = run_data.get("countries_scanned", 0)

    # Per-country rows, critical first
    rows = []
    for r in sorted(run_data.get("per_country", []),
                    key=lambda x: (-x["summary"].get("critical", 0),
                                   -x["summary"].get("warning", 0),
                                   x["slug"])):
        if r.get("pre_launch"):
            status = '⏸ <span style="color:#6b7280">pre-launch</span>'
        elif r["summary"].get("critical", 0) > 0:
            status = '<span style="color:#b91c1c;font-weight:600">✗ critical</span>'
        elif r["summary"].get("warning", 0) > 0:
            status = '<span style="color:#b45309">⚠ warning</span>'
        else:
            status = '<span style="color:#15803d">✓ clean</span>'

        # First critical finding becomes the row's "top issue"
        top_label = "—"
        for pg, payload in r.get("pages", {}).items():
            for f in payload.get("findings", []):
                if f.get("severity") == "critical":
                    top_label = f"{pg.replace('.html','')}: {f['label']}"
                    break
            if top_label != "—":
                break
        if top_label == "—":
            for f in r.get("schema_findings", []):
                if f.get("severity") == "critical":
                    top_label = f"schema: {f['label']}"
                    break
        if top_label == "—" and r["summary"].get("warning", 0):
            top_label = "(warnings only — see JSON report)"

        rows.append(
            f"<tr style=\"border-bottom:1px solid #e5e7eb\">"
            f"<td style=\"padding:6px 10px;font-family:ui-monospace,monospace\">{r['slug']}</td>"
            f"<td style=\"padding:6px 10px\">{status}</td>"
            f"<td style=\"padding:6px 10px;text-align:right\">{r['summary'].get('critical', 0)}</td>"
            f"<td style=\"padding:6px 10px;text-align:right\">{r['summary'].get('warning', 0)}</td>"
            f"<td style=\"padding:6px 10px;color:#374151\">{top_label}</td>"
            f"</tr>"
        )

    run_link = ""
    if run_url:
        run_link = (
            f'<p style="margin:8px 0 0;font-size:13px;color:#374151">'
            f'Full JSON report attached as workflow artifact · '
            f'<a href="{run_url}" style="color:#1d4ed8">view run</a></p>'
        )

    return f"""<!doctype html>
<html><body style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;color:#111;max-width:780px;margin:0 auto;padding:18px">
  <div style="border-bottom:2px solid #111;padding-bottom:10px;margin-bottom:14px">
    <h2 style="margin:0;font-size:20px">SSI Index — Stage 7e Runtime Audit</h2>
    <p style="margin:4px 0 0;color:#4b5563;font-size:13px">{started} UTC · {repo_slug} · KB §49.10</p>
  </div>

  <p style="margin:0 0 12px">
    Scanned <strong>{n}</strong> countries ·
    {severity_badge(crit, 'critical')} ·
    {severity_badge(warn, 'warning')} ·
    {total} total findings.
  </p>

  <table style="width:100%;border-collapse:collapse;font-size:14px;margin-top:8px">
    <thead style="background:#f3f4f6">
      <tr>
        <th style="text-align:left;padding:8px 10px">Country</th>
        <th style="text-align:left;padding:8px 10px">Status</th>
        <th style="text-align:right;padding:8px 10px">Critical</th>
        <th style="text-align:right;padding:8px 10px">Warning</th>
        <th style="text-align:left;padding:8px 10px">Top finding</th>
      </tr>
    </thead>
    <tbody>{''.join(rows)}</tbody>
  </table>

  {run_link}

  <hr style="border:none;border-top:1px solid #e5e7eb;margin:18px 0">
  <p style="font-size:12px;color:#6b7280;margin:0">
    Automated digest from <code>.github/workflows/runtime-audit.yml</code> ·
    Suppress by setting workflow input <code>send_email=false</code>.
  </p>
</body></html>
"""


def make_attachment(report_path: Path) -> dict:
    content = report_path.read_bytes()
    b64 = base64.b64encode(content).decode("ascii")
    return {
        "@odata.type": "#microsoft.graph.fileAttachment",
        "name": report_path.name,
        "contentType": "application/json",
        "contentBytes": b64,
    }


def send_via_graph(token: str, sender: str, recipients: list[str],
                   subject: str, html: str, attachment: dict | None) -> int:
    payload = {
        "message": {
            "subject": subject,
            "body": {"contentType": "HTML", "content": html},
            "toRecipients": [
                {"emailAddress": {"address": r.strip()}}
                for r in recipients if r.strip()
            ],
        },
        "saveToSentItems": True,
    }
    if attachment:
        payload["message"]["attachments"] = [attachment]

    url = f"{GRAPH_BASE}/users/{urllib.parse.quote(sender)}/sendMail"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type":  "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"[send_audit_digest] sendMail → {resp.status}")
            return 0
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:500]
        print(f"[send_audit_digest] sendMail FAILED {e.code}: {body}", file=sys.stderr)
        return 1


def main():
    p = argparse.ArgumentParser()
    p.add_argument("report", nargs="?",
                   help="Path to runtime-audit-*.json (omit when --latest used)")
    p.add_argument("--latest", metavar="LOG_DIR",
                   help="Pick the most recent report in this directory")
    p.add_argument("--to", default=os.environ.get("AUDIT_DIGEST_TO", DEFAULT_TO),
                   help="Comma-separated recipients")
    p.add_argument("--always-send", action="store_true",
                   help="Send email even with zero findings (default: skip)")
    p.add_argument("--attach", action="store_true", default=True,
                   help="Attach the JSON report (default: on)")
    p.add_argument("--repo-slug", default=os.environ.get(
                       "GITHUB_REPOSITORY", "ikengassiindex/ikengassiindex.github.io"))
    p.add_argument("--run-url", default=os.environ.get("RUNTIME_AUDIT_RUN_URL"))
    args = p.parse_args()

    if args.latest:
        report_path = latest_report(Path(args.latest))
    elif args.report:
        report_path = Path(args.report)
    else:
        print("error: provide a report path or --latest LOG_DIR", file=sys.stderr)
        sys.exit(2)

    data = json.loads(report_path.read_text())
    crit = data.get("critical_count", 0)
    warn = data.get("warning_count", 0)

    if crit == 0 and warn == 0 and not args.always_send:
        print("[send_audit_digest] no findings — skipping email")
        sys.exit(0)

    sender = os.environ.get("GRAPH_SENDER_UPN", DEFAULT_TO)
    recipients = [r for r in args.to.split(",") if r.strip()]

    subject_prefix = "✗" if crit else "⚠"
    subject = (
        f"[SSI Audit] {subject_prefix} {crit} critical · {warn} warnings "
        f"({data.get('countries_scanned', '?')} countries) — "
        f"{data.get('started_at', '')[:10]}"
    )
    html = render_html(data, args.repo_slug, args.run_url)
    attachment = make_attachment(report_path) if args.attach else None

    token = get_token()
    rc = send_via_graph(token, sender, recipients, subject, html, attachment)
    sys.exit(rc)


if __name__ == "__main__":
    main()
