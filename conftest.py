"""
conftest.py - project-wide pytest configuration + a small custom pytest PLUGIN
that writes a real, machine-readable JSON test report.

Why a custom plugin (instead of a third-party package)?
  * zero extra dependencies, works the same on Windows, Linux and GitHub Actions;
  * the report contains EXACTLY the fields the lab asks for.

How it works (pytest "hooks"):
  pytest_runtest_logreport  -> called for setup / call / teardown of every test;
                               we record the outcome + failure message.
  pytest_collectreport      -> records import/collection errors (e.g. a syntax error).
  pytest_sessionfinish      -> called once at the very end; we write the JSON file.

Output file: reports/testreport.json  (change with env var TEST_REPORT_PATH)

Nothing here changes pytest's exit status: if any test fails, pytest still
exits with a non-zero code, which is what makes the GitHub Actions job fail.
"""

import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone

_results = {}          # nodeid -> result dict (keeps insertion order)
_collect_errors = []   # collection errors
_start_time = time.time()


def _git(*args):
    """Best-effort local git lookup (used when not running on GitHub Actions)."""
    try:
        out = subprocess.run(
            ["git", *args], capture_output=True, text=True, timeout=5,
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        return out.stdout.strip() if out.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def _metadata():
    """Collect repository / branch / commit / run information.

    On GitHub Actions these come from environment variables that the runner
    sets automatically (GITHUB_*) or that our workflow sets (REPORT_*).
    Locally we fall back to git commands.
    """
    env = os.environ
    on_ci = env.get("GITHUB_ACTIONS") == "true"
    server = env.get("GITHUB_SERVER_URL", "https://github.com")
    repo = env.get("GITHUB_REPOSITORY") or os.path.basename(
        _git("rev-parse", "--show-toplevel") or os.getcwd()
    )
    run_id = env.get("GITHUB_RUN_ID", "local")
    return {
        "repository": repo,
        "branch": env.get("REPORT_BRANCH") or env.get("GITHUB_HEAD_REF")
                  or env.get("GITHUB_REF_NAME") or _git("rev-parse", "--abbrev-ref", "HEAD") or "unknown",
        "commit_sha": env.get("REPORT_COMMIT_SHA") or env.get("GITHUB_SHA")
                      or _git("rev-parse", "HEAD") or "unknown",
        "tested_sha": env.get("GITHUB_SHA") or _git("rev-parse", "HEAD") or "unknown",
        "run_id": run_id,
        "run_number": env.get("GITHUB_RUN_NUMBER", ""),
        "run_attempt": env.get("GITHUB_RUN_ATTEMPT", ""),
        "workflow": env.get("GITHUB_WORKFLOW", ""),
        "event": env.get("GITHUB_EVENT_NAME", "local"),
        "actor": env.get("GITHUB_ACTOR", ""),
        "run_url": f"{server}/{repo}/actions/runs/{run_id}" if on_ci else "",
        "environment": "github-actions" if on_ci else "local",
        "python_version": platform.python_version(),
        "platform": platform.platform(),
    }


def _short_message(report):
    crash = getattr(report.longrepr, "reprcrash", None)
    if crash is not None and getattr(crash, "message", None):
        return crash.message
    text = str(report.longrepr or "")
    return text.strip().splitlines()[-1] if text.strip() else ""


def pytest_runtest_logreport(report):
    entry = _results.setdefault(report.nodeid, {
        "name": report.nodeid.split("::", 1)[-1],
        "nodeid": report.nodeid,
        "status": "passed",
        "duration_seconds": 0.0,
        "failure_message": None,
        "failure_details": None,
    })
    entry["duration_seconds"] = round(entry["duration_seconds"] + report.duration, 4)

    if report.when == "call":
        if report.passed:
            entry["status"] = "passed"
        elif report.failed:
            entry["status"] = "failed"
        elif report.skipped:
            entry["status"] = "skipped"
    elif report.failed:                      # setup or teardown blew up
        entry["status"] = "error"
    elif report.skipped and report.when == "setup":
        entry["status"] = "skipped"

    if report.failed:
        entry["failure_message"] = f"[{report.when}] {_short_message(report)}"
        entry["failure_details"] = (report.longreprtext or "")[-4000:]


def pytest_collectreport(report):
    if report.failed:
        _collect_errors.append({
            "name": f"COLLECTION ERROR: {report.nodeid or 'session'}",
            "nodeid": report.nodeid,
            "status": "error",
            "duration_seconds": 0.0,
            "failure_message": _short_message(report),
            "failure_details": (report.longreprtext or "")[-4000:],
        })


def pytest_sessionfinish(session, exitstatus):
    # Worker processes / --collect-only runs should not write a report.
    if session.config.getoption("collectonly"):
        return

    tests = _collect_errors + list(_results.values())
    passed = sum(t["status"] == "passed" for t in tests)
    failed = sum(t["status"] in ("failed", "error") for t in tests)
    errors = sum(t["status"] == "error" for t in tests)
    skipped = sum(t["status"] == "skipped" for t in tests)
    exit_code = int(exitstatus)

    overall = "PASS" if (failed == 0 and exit_code == 0 and passed > 0) else "FAIL"

    report = {
        "report_type": "pytest-json-report",
        "report_version": 1,
        "generated_by": "conftest.py custom pytest plugin (real test execution)",
        **_metadata(),
        "execution_timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "summary": {
            "total": len(tests),
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "skipped": skipped,
            "duration_seconds": round(time.time() - _start_time, 3),
        },
        "overall_result": overall,
        "pytest_exit_status": exit_code,
        "tests": tests,
    }

    path = os.environ.get("TEST_REPORT_PATH", os.path.join("reports", "testreport.json"))
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)

    tr = session.config.pluginmanager.get_plugin("terminalreporter")
    line = (f"JSON test report written to {path}  ->  {overall} "
            f"({passed} passed, {failed} failed, {skipped} skipped, {len(tests)} total)")
    if tr is not None:
        tr.write_sep("=", line)
    else:
        print(line, file=sys.stderr)
