"""
scripts/show_report.py - print each individual test result from the JSON report
and, on GitHub Actions, also write a nice table to the run's "Summary" page.

    python scripts/show_report.py reports/testreport.json
"""

import json
import os
import sys

ICONS = {"passed": "PASS", "failed": "FAIL", "error": "ERROR", "skipped": "SKIP"}
MD_ICONS = {"passed": "✅ passed", "failed": "❌ failed", "error": "💥 error", "skipped": "⏭️ skipped"}


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join("reports", "testreport.json")
    if not os.path.exists(path):
        print(f"::error::No report found at {path} (did pytest crash before finishing?)")
        return 1
    with open(path, encoding="utf-8") as fh:
        r = json.load(fh)
    s = r["summary"]

    print("=" * 78)
    print(f" OVERALL RESULT : {r['overall_result']}")
    print(f" Repository     : {r['repository']}")
    print(f" Branch         : {r['branch']}")
    print(f" Commit SHA     : {r['commit_sha']}")
    print(f" Run ID         : {r['run_id']}")
    print(f" Timestamp      : {r['execution_timestamp']}")
    print(f" Totals         : {s['total']} total | {s['passed']} passed | "
          f"{s['failed']} failed | {s.get('skipped', 0)} skipped")
    print("=" * 78)
    for t in r["tests"]:
        print(f" [{ICONS.get(t['status'], t['status']):5}] {t['name']}")
        if t.get("failure_message"):
            print(f"         -> {t['failure_message']}")
            if os.environ.get("GITHUB_ACTIONS") == "true":
                # GitHub annotation: newlines must be encoded as %0A
                msg = t["failure_message"].replace("%", "%25").replace("\r", "").replace("\n", "%0A")
                print(f"::error title=Test failed: {t['name']}::{msg}")
    print("=" * 78)

    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        emoji = "✅" if r["overall_result"] == "PASS" else "❌"
        lines = [
            f"## {emoji} Test report: {r['overall_result']}",
            "",
            "| Repository | Branch | Commit | Run ID | Timestamp (UTC) |",
            "|---|---|---|---|---|",
            f"| {r['repository']} | {r['branch']} | `{r['commit_sha'][:10]}` | {r['run_id']} | {r['execution_timestamp']} |",
            "",
            f"**Total:** {s['total']} &nbsp; **Passed:** {s['passed']} &nbsp; **Failed:** {s['failed']} &nbsp; **Skipped:** {s.get('skipped', 0)}",
            "",
            "| # | Test | Status | Failure message |",
            "|---|---|---|---|",
        ]
        for i, t in enumerate(r["tests"], 1):
            msg = (t.get("failure_message") or "").replace("|", "\\|").replace("\n", " ")[:200]
            lines.append(f"| {i} | `{t['name']}` | {MD_ICONS.get(t['status'], t['status'])} | {msg} |")
        with open(summary_file, "a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
