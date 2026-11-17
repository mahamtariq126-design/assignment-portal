# Verification report (honest status)

Build environment: Linux, Python 3.13, Flask 3.1.3, pytest 9.1.1, on 17 Nov 2026.
**Nothing here was run on your Windows PC or on GitHub.** Windows and GitHub steps need you.

Legend:
* ✅ **Implemented and tested** in the build environment
* 🟡 **Implemented, not tested** (could not be run in the build environment)
* 👤 **Requires your GitHub account / manual setup**

| Requirement | Status | Evidence / note |
|---|---|---|
| Portal implemented | ✅ | `app.py`, `validation.py`, `database.py`, template, CSS, JS |
| Portal locally executed | ✅ | Ran `python app.py`; GET / → 200; real browser (headless Chrome) screenshots of desktop, mobile, error and success states in `docs/preview/` |
| Valid submission verified | ✅ | Real HTTP POST → 302 + saved; test_01 passes |
| Missing registration number verified | ✅ | Real HTTP POST → 400, not saved; test_02 passes |
| Invalid URL verified | ✅ | Real HTTP POST (`ftp://…`) → 400, not saved; test_03 + 9 URL-format tests pass |
| Data persists after restart | ✅ | Stopped and restarted the server process: total stayed 2; persistence test passes |
| Automated tests executed | ✅ | `python -m pytest` → **62 passed**, exit code 0 |
| Passing tests verified | ✅ | as above; JSON report `overall_result: PASS` |
| Failing test behaviour verified | ✅ | `demo_defect.py break` → **6 failed, 56 passed**, exit code **1**, report `FAIL` with failure messages; `fix` → 62 passed again |
| GitHub Actions workflow prepared | ✅ / 👤 | `ci.yml` parsed and checked with **actionlint 1.7.12: no problems**. Steps simulated locally with GitHub env vars. **Not yet run on GitHub** — happens on your first push |
| Push trigger configured | ✅ / 👤 | `on.push.branches: ["**"]` |
| Pull request trigger configured | ✅ / 👤 | `on.pull_request.branches: [main]` |
| Local JSON receiver implemented | ✅ | 12 receiver tests (token 401, bad JSON 400, invalid report 422, PASS & FAIL saved, overwrite + history); also ran `receiver.py` as a real process and delivered FAIL then PASS reports with `send_report.py` |
| Tunnel configuration prepared | 🟡 / 👤 | Scripts + docs for Cloudflare quick tunnel. `cloudflared` could not be run here (no internet access to Cloudflare from the build environment) |
| Remote report delivery (GitHub → tunnel → PC) | **❌ NOT verified** 👤 | Only local delivery was verified. Verify yourself with `check_delivery.ps1 -Url <tunnel>` and then a real push |
| Windows PowerShell scripts | 🟡 | Written ASCII-only with CRLF for PowerShell 5.1; not executed (no Windows here) |
| Git push/clone/pull + post-merge hook | ✅ | Simulated with a local bare remote: push, clone, pull → hook ran the tests ("All tests passed after pull") |
| GitHub Pages prepared | 🟡 / 👤 | `pages.yml` (actionlint clean) + `site/`; needs `ENABLE_PAGES=true` and Pages source = GitHub Actions. No URL exists until you deploy |
| E-mail reporting prepared | 🟡 / 👤 | Message building tested (HTML + JSON attachment); skip-without-secrets tested. **No e-mail was sent** — needs your SMTP secrets |
| ZIP generated | ✅ | `assignment-portal.zip` |
| README completed | ✅ | `README.md` |
| Lab guide completed | ✅ | `LAB_GUIDE.md` (+ `docs/`) |

No GitHub runs, screenshots of GitHub, report deliveries over the internet, e-mails or Pages
URLs are claimed. `docs/sample_testreport_SAMPLE.json` is clearly marked as a **sample**.
