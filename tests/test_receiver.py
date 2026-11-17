"""
tests/test_receiver.py - tests for the local report receiver (receiver.py)
and the sender script (scripts/send_report.py).

A real HTTP server is started on a random free port on 127.0.0.1, then real
HTTP requests are sent to it. This proves the receiver + sender work together
LOCALLY. (Delivery from GitHub through the internet tunnel can only be proven
on your own computer during the demo.)
"""

import json
import os
import subprocess
import sys
import threading
import urllib.error
import urllib.request

import pytest

import receiver

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN = "unit-test-token-123"


def sample_report(result="PASS"):
    failed = 0 if result == "PASS" else 1
    tests = [{"name": "test_a", "status": "passed"}]
    if failed:
        tests.append({"name": "test_b", "status": "failed", "failure_message": "AssertionError"})
    return {
        "repository": "student/assignment-portal",
        "branch": "main",
        "commit_sha": "abc123def456",
        "run_id": "123456789",
        "execution_timestamp": "2026-11-17T06:00:00+00:00",
        "summary": {"total": len(tests), "passed": 1, "failed": failed},
        "overall_result": result,
        "tests": tests,
    }


@pytest.fixture
def server(tmp_path):
    output = tmp_path / "testreport.json"
    srv = receiver.make_server("127.0.0.1", 0, TOKEN, str(output), quiet=True)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{srv.server_address[1]}", output
    srv.shutdown()
    srv.server_close()


def post(url, body, headers=None):
    data = body if isinstance(body, bytes) else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method="POST",
                                 headers={"Content-Type": "application/json", **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read())


def test_health_check(server):
    base, _ = server
    with urllib.request.urlopen(base + "/health", timeout=5) as resp:
        assert json.loads(resp.read())["status"] == "ok"


@pytest.mark.parametrize("result", ["PASS", "FAIL"])
def test_valid_report_is_saved(server, result):
    base, output = server
    status, body = post(base + "/report", sample_report(result), {"Authorization": f"Bearer {TOKEN}"})
    assert status == 200 and body["overall_result"] == result
    assert json.loads(output.read_text(encoding="utf-8"))["overall_result"] == result


def test_new_report_overwrites_previous(server):
    base, output = server
    post(base + "/report", sample_report("FAIL"), {"X-Report-Token": TOKEN})
    post(base + "/report", sample_report("PASS"), {"X-Report-Token": TOKEN})
    assert json.loads(output.read_text(encoding="utf-8"))["overall_result"] == "PASS"
    history = list((output.parent / "reports_history").iterdir())
    assert len(history) == 2


@pytest.mark.parametrize("headers", [{}, {"Authorization": "Bearer wrong"}, {"X-Report-Token": ""}])
def test_missing_or_wrong_token_is_rejected(server, headers):
    base, output = server
    status, _ = post(base + "/report", sample_report(), headers)
    assert status == 401
    assert not output.exists()


def test_invalid_json_is_rejected(server):
    base, output = server
    status, _ = post(base + "/report", b"{not json", {"X-Report-Token": TOKEN})
    assert status == 400
    assert not output.exists()


def test_report_missing_fields_is_rejected(server):
    base, output = server
    bad = sample_report()
    del bad["commit_sha"]
    bad["overall_result"] = "MAYBE"
    status, body = post(base + "/report", bad, {"X-Report-Token": TOKEN})
    assert status == 422
    assert any("commit_sha" in p for p in body["problems"])
    assert not output.exists()


def test_inconsistent_report_is_rejected():
    bad = sample_report("PASS")
    bad["summary"]["failed"] = 1
    assert receiver.validate_report(bad)


def test_send_report_script_delivers_to_receiver(server, tmp_path):
    """Run scripts/send_report.py exactly like the GitHub workflow does."""
    base, output = server
    report_file = tmp_path / "local_report.json"
    report_file.write_text(json.dumps(sample_report("FAIL")), encoding="utf-8")
    env = dict(os.environ, REPORT_RECEIVER_URL=base, REPORT_TOKEN=TOKEN)
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "send_report.py"), str(report_file)],
        env=env, capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "delivered" in proc.stdout.lower()
    assert json.loads(output.read_text(encoding="utf-8"))["overall_result"] == "FAIL"


def test_send_report_script_skips_cleanly_without_url(tmp_path):
    report_file = tmp_path / "r.json"
    report_file.write_text(json.dumps(sample_report()), encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k not in ("REPORT_RECEIVER_URL", "REPORT_TOKEN")}
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "send_report.py"), str(report_file)],
        env=env, capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0
    assert "skipping" in proc.stdout.lower()
