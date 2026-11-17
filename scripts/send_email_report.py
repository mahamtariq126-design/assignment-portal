"""
scripts/send_email_report.py - OPTIONAL bonus: e-mail the test report.

All settings come from environment variables (GitHub repository secrets).
NOTHING is hard-coded. If the settings are missing, the script prints a notice
and exits 0, so the workflow keeps working without e-mail.

Required secrets:
    SMTP_SERVER     e.g. smtp.gmail.com
    SMTP_PORT       587 (STARTTLS) or 465 (SSL)
    SMTP_USERNAME   e.g. your.name@gmail.com
    SMTP_PASSWORD   for Gmail: a 16-character "App password" (NOT your normal password)
    EMAIL_TO        where to send the report (comma-separated for several)
Optional:
    EMAIL_FROM      defaults to SMTP_USERNAME

    python scripts/send_email_report.py reports/testreport.json
"""

import html
import json
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage


def build_message(report, sender, recipients):
    s = report["summary"]
    result = report["overall_result"]
    subject = (f"[{result}] {report['repository']} @ {report['branch']} "
               f"({s['passed']}/{s['total']} passed) - commit {report['commit_sha'][:7]}")

    text_lines = [
        f"Overall status : {result}",
        f"Repository     : {report['repository']}",
        f"Branch         : {report['branch']}",
        f"Commit SHA     : {report['commit_sha']}",
        f"Run ID         : {report['run_id']}",
        f"Run URL        : {report.get('run_url', '')}",
        f"Timestamp      : {report['execution_timestamp']}",
        f"Total / Passed / Failed : {s['total']} / {s['passed']} / {s['failed']}",
        "",
        "Individual test results:",
    ]
    rows = []
    for t in report["tests"]:
        text_lines.append(f"  [{t['status'].upper():7}] {t['name']}")
        if t.get("failure_message"):
            text_lines.append(f"            {t['failure_message']}")
        color = "#12b981" if t["status"] == "passed" else ("#e5484d" if t["status"] in ("failed", "error") else "#888")
        rows.append(
            f"<tr><td style='padding:6px 10px;border-bottom:1px solid #eee'>{html.escape(t['name'])}</td>"
            f"<td style='padding:6px 10px;border-bottom:1px solid #eee;color:{color};font-weight:700'>{t['status'].upper()}</td>"
            f"<td style='padding:6px 10px;border-bottom:1px solid #eee;color:#a3242a'>{html.escape(t.get('failure_message') or '')}</td></tr>"
        )

    banner = "#12b981" if result == "PASS" else "#e5484d"
    html_body = f"""
    <div style="font-family:Segoe UI,Arial,sans-serif;max-width:760px">
      <div style="background:{banner};color:#fff;padding:16px 20px;border-radius:10px 10px 0 0">
        <h2 style="margin:0">Test run {result}</h2>
        <div>{html.escape(report['repository'])} &middot; {html.escape(report['branch'])}</div>
      </div>
      <div style="border:1px solid #e5e5e5;border-top:0;padding:16px 20px;border-radius:0 0 10px 10px">
        <p><b>Commit:</b> <code>{html.escape(report['commit_sha'])}</code><br>
           <b>Run ID:</b> {html.escape(str(report['run_id']))}<br>
           <b>Timestamp:</b> {html.escape(report['execution_timestamp'])}<br>
           <b>Total:</b> {s['total']} &nbsp; <b>Passed:</b> {s['passed']} &nbsp; <b>Failed:</b> {s['failed']}</p>
        <p><a href="{html.escape(report.get('run_url', ''))}">Open the GitHub Actions run</a></p>
        <table style="border-collapse:collapse;width:100%;font-size:14px">
          <tr style="background:#f3f5fc"><th align="left" style="padding:6px 10px">Test</th>
          <th align="left" style="padding:6px 10px">Status</th><th align="left" style="padding:6px 10px">Failure message</th></tr>
          {''.join(rows)}
        </table>
      </div>
    </div>"""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.set_content("\n".join(text_lines))
    msg.add_alternative(html_body, subtype="html")
    msg.add_attachment(json.dumps(report, indent=2).encode("utf-8"),
                       maintype="application", subtype="json", filename="testreport.json")
    return msg


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join("reports", "testreport.json")
    env = os.environ
    server = env.get("SMTP_SERVER", "").strip()
    user = env.get("SMTP_USERNAME", "").strip()
    password = env.get("SMTP_PASSWORD", "")
    to = [a.strip() for a in env.get("EMAIL_TO", "").split(",") if a.strip()]

    if not (server and user and password and to):
        print("E-mail secrets not configured (SMTP_SERVER/SMTP_USERNAME/SMTP_PASSWORD/EMAIL_TO) "
              "- skipping e-mail report.")
        return 0
    if not os.path.exists(path):
        print(f"::warning::Report not found at {path}; no e-mail sent.")
        return 0

    with open(path, encoding="utf-8") as fh:
        report = json.load(fh)
    port = int(env.get("SMTP_PORT", "587") or 587)
    msg = build_message(report, env.get("EMAIL_FROM", "").strip() or user, to)

    try:
        context = ssl.create_default_context()
        if port == 465:
            with smtplib.SMTP_SSL(server, port, context=context, timeout=30) as smtp:
                smtp.login(user, password)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(server, port, timeout=30) as smtp:
                smtp.starttls(context=context)
                smtp.login(user, password)
                smtp.send_message(msg)
        print(f"E-mail report sent to {len(to)} recipient(s).")
    except (smtplib.SMTPException, OSError) as exc:
        print(f"::warning::E-mail could not be sent: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
