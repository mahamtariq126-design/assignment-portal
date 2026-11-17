# 🎓 Assignment Submission Portal — DevOps Mid Lab

A premium university assignment-submission portal (**Flask + SQLite + HTML/CSS/JS**) with a
complete **CI pipeline**: pytest → JSON report → GitHub Actions artifact → automatic delivery
to your own computer through a **Cloudflare Tunnel**, plus optional **GitHub Pages** and **e-mail** reports.

> 👉 **Beginners: start with [`LAB_GUIDE.md`](LAB_GUIDE.md)** — every step with copy-paste commands.

![CI](../../actions/workflows/ci.yml/badge.svg)

---

## Quick start (Windows PowerShell, in VS Code)

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned   # once
Get-ChildItem -Recurse | Unblock-File                                  # once, after unzipping
.\scripts\setup.ps1        # venv + dependencies + run tests
.\scripts\run_portal.ps1   # http://127.0.0.1:5000
.\scripts\run_tests.ps1    # run tests and print every result
```

## Features

* Four required fields: full name, registration number, assignment title, submission URL
* Server-side validation (`validation.py`): all fields required, registration-number format,
  strict `http://` / `https://` URL check; clear red error messages; HTTP 400 on invalid input
* Valid submissions stored in SQLite (`instance/portal.db`) → survive restarts
* List of submissions with local date & time, and a total count
* Premium responsive UI: gradient hero, glassmorphism, floating orbs, animated buttons,
  focus effects, animated success check + confetti; mobile/tablet/desktop
* No file uploads (links only)

## Project structure

```
assignment-portal/
├── app.py                  Flask routes (/, /submit, /health)
├── validation.py           all validation rules
├── database.py             SQLite helper
├── templates/index.html    page template
├── static/css/style.css    design
├── static/js/app.js        animations + live validation
├── static/img/crest.svg    university crest
├── conftest.py             custom pytest plugin -> reports/testreport.json
├── pytest.ini
├── tests/
│   ├── conftest.py         fixtures (isolated temp databases)
│   ├── test_portal.py      end-to-end tests with Flask test client
│   ├── test_validation.py  unit tests
│   └── test_receiver.py    receiver + sender tests (real local HTTP)
├── receiver.py             local HTTP receiver (token-protected)
├── scripts/
│   ├── setup.ps1  run_portal.ps1  run_tests.ps1
│   ├── start_receiver.ps1  start_tunnel.ps1  check_delivery.ps1
│   ├── install_git_hooks.ps1
│   ├── show_report.py      prints results + GitHub job summary
│   ├── send_report.py      POSTs report to receiver (used by CI)
│   ├── send_email_report.py  optional e-mail
│   └── demo_defect.py      break / fix for the failing-run demo
├── .github/workflows/
│   ├── ci.yml              tests on every push + PRs to main
│   └── pages.yml           optional Pages deploy after green main
├── .githooks/post-merge    optional: run tests after git pull
├── site/                   static demo for GitHub Pages
├── docs/                   setup, push/pull, demo, screenshots, tunnel, bonus, SAMPLE report
├── LAB_GUIDE.md            ⭐ the beginner walkthrough
└── VERIFICATION_REPORT.md  what was tested and what needs your GitHub account
```

## The pipeline (`.github/workflows/ci.yml`)

Triggers: `push` to **any** branch, `pull_request` targeting **main**, manual `workflow_dispatch`.

1. Checkout → 2. Python 3.12 → 3. `pip install -r requirements.txt` → 4. `python -m pytest`
5. Print each test result + job-summary table → 6. Upload `testreport.json` artifact
7. POST the report to your receiver via `REPORT_RECEIVER_URL` + `REPORT_TOKEN` secrets
8. Optional e-mail → 9. Fail the job if `overall_result` is `FAIL`

Steps 5–8 run with `if: ${{ !cancelled() }}`, so **failing** runs still upload and deliver their report.

## Report format

See [`docs/sample_testreport_SAMPLE.json`](docs/sample_testreport_SAMPLE.json) (**sample only — not real results**).
Fields: repository, branch, commit_sha, run_id, execution_timestamp, tests[name, status,
failure_message], summary{total, passed, failed}, overall_result.

## Documentation

| File | Content |
|---|---|
| [LAB_GUIDE.md](LAB_GUIDE.md) | Steps 1–13, beginner walkthrough |
| [docs/GITHUB_SETUP.md](docs/GITHUB_SETUP.md) | Repo, secrets, variables |
| [docs/PUSH_PULL_GUIDE.md](docs/PUSH_PULL_GUIDE.md) | All 15 Git commands explained; push vs pull vs PR |
| [docs/TUNNEL_SETUP.md](docs/TUNNEL_SETUP.md) | Receiver + Cloudflare Tunnel |
| [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md) | Demo A (pass), B (fail), C (fix) |
| [docs/SCREENSHOT_CHECKLIST.md](docs/SCREENSHOT_CHECKLIST.md) | Exact screenshots to capture |
| [docs/BONUS_PAGES_EMAIL.md](docs/BONUS_PAGES_EMAIL.md) | GitHub Pages + e-mail reports |
| [VERIFICATION_REPORT.md](VERIFICATION_REPORT.md) | Honest status of every requirement |

Automatic report delivery verification.

Automatic report delivery verification.
