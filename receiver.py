"""
receiver.py - Local HTTP receiver for GitHub Actions test reports.

Runs on YOUR Windows computer. GitHub Actions POSTs the JSON test report to it
(through a Cloudflare Tunnel, because GitHub's servers cannot reach your
"localhost" directly). Each valid report is saved as received_reports/testreport.json,
overwriting the previous one. A copy is also kept in reports_history/ so you
have evidence of the PASS, FAIL and FIXED runs.

Endpoints
  GET  /health  -> {"status": "ok"}                      (no token needed)
  POST /report  -> save a report                          (token REQUIRED)

Security
  The request must carry the secret token in ONE of these headers:
      Authorization: Bearer <token>
      X-Report-Token: <token>
  The token is read from (first match wins):
      --token argument  ->  REPORT_TOKEN environment variable  ->  .receiver_token file

Usage (PowerShell)
  python receiver.py                     # listens on http://127.0.0.1:8000
  python receiver.py --port 8000 --output testreport.json
"""

import argparse
import hmac
import json
import os
import sys
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAX_BODY_BYTES = 2 * 1024 * 1024          # 2 MB is far more than any report needs
VALID_RESULTS = {"PASS", "FAIL"}
VALID_STATUSES = {"passed", "failed", "error", "skipped"}
REQUIRED_TEXT_FIELDS = ("repository", "branch", "commit_sha", "execution_timestamp")

_write_lock = threading.Lock()


# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #
def validate_report(data):
    """Return a list of problems. An empty list means the report is valid."""
    problems = []
    if not isinstance(data, dict):
        return ["Report must be a JSON object."]

    for field in REQUIRED_TEXT_FIELDS:
        if not isinstance(data.get(field), str) or not data.get(field).strip():
            problems.append(f"'{field}' is required and must be a non-empty string.")

    if not isinstance(data.get("run_id"), (str, int)) or str(data.get("run_id")).strip() == "":
        problems.append("'run_id' is required.")

    if data.get("overall_result") not in VALID_RESULTS:
        problems.append("'overall_result' must be 'PASS' or 'FAIL'.")

    summary = data.get("summary")
    if not isinstance(summary, dict):
        problems.append("'summary' object is required.")
    else:
        for key in ("total", "passed", "failed"):
            value = summary.get(key)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                problems.append(f"'summary.{key}' must be a non-negative integer.")

    tests = data.get("tests")
    if not isinstance(tests, list):
        problems.append("'tests' must be a list.")
    else:
        for i, test in enumerate(tests):
            if not isinstance(test, dict) or not isinstance(test.get("name"), str):
                problems.append(f"tests[{i}] must be an object with a 'name'.")
            elif test.get("status") not in VALID_STATUSES:
                problems.append(f"tests[{i}].status must be one of {sorted(VALID_STATUSES)}.")
        if isinstance(summary, dict) and isinstance(summary.get("total"), int):
            if summary["total"] != len(tests):
                problems.append("'summary.total' does not match the number of tests.")

    if not problems and isinstance(summary, dict):
        if summary["passed"] + summary["failed"] > summary["total"]:
            problems.append("'summary.passed' + 'summary.failed' cannot exceed 'summary.total'.")
        if data["overall_result"] == "PASS" and summary["failed"] > 0:
            problems.append("'overall_result' is PASS but 'summary.failed' > 0.")

    return problems


# --------------------------------------------------------------------------- #
# Saving
# --------------------------------------------------------------------------- #
def save_report(data, output_path):
    """Atomically overwrite output_path and keep a history copy. Returns history path."""
    output_path = os.path.abspath(output_path)
    out_dir = os.path.dirname(output_path)
    os.makedirs(out_dir, exist_ok=True)
    payload = json.dumps(data, indent=2)

    with _write_lock:
        tmp_path = output_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as fh:
            fh.write(payload)
        os.replace(tmp_path, output_path)          # overwrite in one step

        history_dir = os.path.join(out_dir, "reports_history")
        os.makedirs(history_dir, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        safe_run = "".join(c for c in str(data.get("run_id")) if c.isalnum()) or "run"
        history_path = os.path.join(
            history_dir, f"testreport_{stamp}_run{safe_run}_{data['overall_result']}.json"
        )
        with open(history_path, "w", encoding="utf-8") as fh:
            fh.write(payload)
    return history_path


def log_report(data, output_path, history_path):
    s = data["summary"]
    bar = "=" * 66
    icon = "PASS  [OK]" if data["overall_result"] == "PASS" else "FAIL  [X]"
    lines = [
        "",
        bar,
        f"  NEW TEST REPORT RECEIVED   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        bar,
        f"  Result      : {icon}",
        f"  Repository  : {data.get('repository')}",
        f"  Branch      : {data.get('branch')}",
        f"  Commit      : {str(data.get('commit_sha'))[:12]}",
        f"  Run ID      : {data.get('run_id')}   (event: {data.get('event', '?')})",
        f"  Tests       : {s['total']} total | {s['passed']} passed | {s['failed']} failed",
    ]
    failing = [t for t in data["tests"] if t.get("status") in ("failed", "error")]
    if failing:
        lines.append("  Failed tests:")
        for t in failing:
            lines.append(f"    - {t['name']}")
            if t.get("failure_message"):
                first_line = str(t["failure_message"]).strip().splitlines()[0]
                lines.append(f"        {first_line[:150]}")
    lines += [
        f"  Saved to    : {os.path.abspath(output_path)}",
        f"  History copy: {history_path}",
        bar,
        "",
    ]
    print("\n".join(lines), flush=True)


# --------------------------------------------------------------------------- #
# HTTP server
# --------------------------------------------------------------------------- #
def make_handler(token, output_path, quiet=False):
    class ReportHandler(BaseHTTPRequestHandler):
        server_version = "LabReportReceiver/1.0"

        def log_message(self, fmt, *args):            # concise access log
            if not quiet:
                sys.stdout.write("[%s] %s - %s\n" % (
                    datetime.now().strftime("%H:%M:%S"), self.address_string(), fmt % args))

        def _send_json(self, status, body):
            raw = json.dumps(body).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def _token_ok(self):
            supplied = self.headers.get("X-Report-Token", "")
            auth = self.headers.get("Authorization", "")
            if auth.lower().startswith("bearer "):
                supplied = auth[7:].strip()
            return bool(supplied) and hmac.compare_digest(
                supplied.encode("utf-8"), token.encode("utf-8"))

        def do_GET(self):
            if self.path.split("?")[0] in ("/", "/health"):
                return self._send_json(200, {"status": "ok", "service": "test-report-receiver"})
            return self._send_json(404, {"error": "Not found"})

        def do_POST(self):
            if self.path.split("?")[0] != "/report":
                return self._send_json(404, {"error": "Not found. POST reports to /report"})

            if not self._token_ok():
                if not quiet:
                    print("  !! Rejected report: missing or wrong token", flush=True)
                return self._send_json(401, {"error": "Unauthorized: missing or invalid token"})

            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                return self._send_json(400, {"error": "Invalid Content-Length"})
            if length <= 0:
                return self._send_json(400, {"error": "Empty body"})
            if length > MAX_BODY_BYTES:
                return self._send_json(413, {"error": "Report too large"})

            raw = self.rfile.read(length)
            try:
                data = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                return self._send_json(400, {"error": f"Body is not valid JSON: {exc}"})

            problems = validate_report(data)
            if problems:
                if not quiet:
                    print(f"  !! Rejected invalid report: {problems}", flush=True)
                return self._send_json(422, {"error": "Invalid report", "problems": problems})

            history_path = save_report(data, output_path)
            if not quiet:
                log_report(data, output_path, history_path)
            return self._send_json(200, {
                "status": "saved",
                "overall_result": data["overall_result"],
                "saved_to": os.path.basename(output_path),
            })

    return ReportHandler


def make_server(host, port, token, output_path, quiet=False):
    if not token:
        raise ValueError("A secret token is required.")
    return ThreadingHTTPServer((host, port), make_handler(token, output_path, quiet))


def load_token(cli_token):
    if cli_token:
        return cli_token.strip()
    if os.environ.get("REPORT_TOKEN"):
        return os.environ["REPORT_TOKEN"].strip()
    token_file = os.path.join(BASE_DIR, ".receiver_token")
    if os.path.exists(token_file):
        with open(token_file, encoding="utf-8-sig") as fh:
            return fh.read().strip()
    return ""


def main(argv=None):
    parser = argparse.ArgumentParser(description="Receive GitHub Actions test reports.")
    parser.add_argument("--host", default="127.0.0.1", help="Interface to listen on (default 127.0.0.1)")
    parser.add_argument("--port", type=int, default=int(os.environ.get("RECEIVER_PORT", "8000")))
    parser.add_argument("--output", default=os.path.join(BASE_DIR, "received_reports", "testreport.json"),
                        help="Where to save the report (default received_reports/testreport.json)")
    parser.add_argument("--token", default=None, help="Secret token (else REPORT_TOKEN env or .receiver_token file)")
    args = parser.parse_args(argv)

    token = load_token(args.token)
    if not token:
        print("ERROR: no secret token configured.\n"
              "Run  .\\scripts\\start_receiver.ps1  (it creates one), or set $env:REPORT_TOKEN.",
              file=sys.stderr)
        return 2

    server = make_server(args.host, args.port, token, args.output)
    print("=" * 66)
    print("  GitHub Actions Test Report Receiver is RUNNING")
    print(f"  Listening on : http://{args.host}:{args.port}")
    print(f"  Report URL   : http://{args.host}:{args.port}/report   (POST)")
    print(f"  Health check : http://{args.host}:{args.port}/health")
    print(f"  Saves to     : {os.path.abspath(args.output)}")
    print(f"  Token        : {token[:4]}...{token[-4:]}  ({len(token)} chars)")
    print("  Press Ctrl+C to stop.")
    print("=" * 66, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nReceiver stopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
