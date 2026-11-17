"""
scripts/send_report.py - POST the JSON test report to your local receiver.

Used by the GitHub Actions workflow (and usable locally for testing).

    python scripts/send_report.py reports/testreport.json

Configuration (environment variables, set from GitHub repository secrets):
    REPORT_RECEIVER_URL  e.g. https://random-words.trycloudflare.com
                         ("/report" is added automatically if missing)
    REPORT_TOKEN         the same secret token your receiver.py uses

Behaviour:
    * If REPORT_RECEIVER_URL is not set -> prints a notice and exits 0 (skipped).
    * Retries 3 times (the tunnel may be slow to wake up).
    * On final failure prints a GitHub "::warning::" and exits 0, so a delivery
      problem never hides the real test result. Use --strict to exit 1 instead.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request


def build_url(base):
    base = base.strip().rstrip("/")
    return base if base.endswith("/report") else base + "/report"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    strict = "--strict" in sys.argv
    path = args[0] if args else os.path.join("reports", "testreport.json")

    url = os.environ.get("REPORT_RECEIVER_URL", "").strip()
    token = os.environ.get("REPORT_TOKEN", "").strip()

    if not url:
        print("REPORT_RECEIVER_URL is not configured - skipping delivery to local receiver.")
        return 0
    if not token:
        print("::warning::REPORT_TOKEN secret is empty - the receiver will reject the report.")
    if not os.path.exists(path):
        print(f"::error::Report file not found: {path}")
        return 1 if strict else 0

    with open(path, "rb") as fh:
        body = fh.read()
    try:
        summary = json.loads(body)
        print(f"Sending report: {summary.get('overall_result')} "
              f"({summary.get('summary', {}).get('passed')} passed / "
              f"{summary.get('summary', {}).get('failed')} failed)")
    except json.JSONDecodeError:
        print("::error::Report file is not valid JSON")
        return 1 if strict else 0

    target = build_url(url)
    print("Target: <REPORT_RECEIVER_URL secret>/report")   # never print the secret URL

    last_error = ""
    for attempt in range(1, 4):
        req = urllib.request.Request(
            target, data=body, method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
                "User-Agent": "github-actions-test-report-sender/1.0",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                reply = resp.read().decode("utf-8", "replace")
                print(f"Attempt {attempt}: HTTP {resp.status} -> {reply}")
                print("Report delivered to local receiver successfully.")
                return 0
        except urllib.error.HTTPError as err:
            last_error = f"HTTP {err.code}: {err.read().decode('utf-8', 'replace')[:300]}"
            if err.code in (400, 401, 404, 413, 422):      # retrying will not help
                break
        except (urllib.error.URLError, TimeoutError, OSError) as err:
            last_error = str(err)
        print(f"Attempt {attempt} failed: {last_error}")
        time.sleep(3 * attempt)

    print(f"::warning::Could not deliver report to local receiver: {last_error}. "
          "Is receiver.py running, is the Cloudflare tunnel running, and is the "
          "REPORT_RECEIVER_URL secret set to the CURRENT tunnel URL?")
    return 1 if strict else 0


if __name__ == "__main__":
    sys.exit(main())
