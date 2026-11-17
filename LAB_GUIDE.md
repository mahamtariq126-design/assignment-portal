# LAB GUIDE — DevOps Mid Lab, step by step (beginner friendly)

This guide takes you from "I just downloaded a ZIP" to "my instructor has seen a
passing run, a failing run and a fixed run, with reports arriving on my laptop".

Every step has: **What to do · Where to click · Command · Expected output ·
Screenshot · What to say to the instructor.**

> **Conventions**
> * Commands are for **Windows PowerShell** inside **VS Code** (Terminal → New Terminal).
> * Replace `YOUR-USERNAME` with your GitHub username and `assignment-portal` with your repo name if different.
> * Lines starting with `#` are comments — you don't need to type them.
> * Screenshot names like `A1-tests-pass-local.png` match `docs/SCREENSHOT_CHECKLIST.md`.

---

## STEP 1 — What is in this project and why

| Part | File(s) | Why it exists |
|---|---|---|
| Web portal | `app.py`, `validation.py`, `database.py`, `templates/index.html`, `static/` | The Flask app students use to submit assignment links. SQLite file `instance/portal.db` keeps the data after restart. |
| Automated tests | `tests/` (62 tests) | Prove the portal works: valid submission saved, missing reg. number rejected, invalid URL rejected, persistence, etc. |
| JSON test report | `conftest.py` | A small pytest plugin that writes `reports/testreport.json` with repo, branch, commit, run ID, every test's status and failure message. |
| CI/CD pipeline | `.github/workflows/ci.yml` | GitHub Actions: runs the tests on every push and every PR to `main`, shows results, uploads the report, sends it to your PC, fails the job on test failure. |
| Report receiver | `receiver.py` | Small web server on **your** PC. Accepts the report (only with the secret token) and saves `received_reports/testreport.json`. |
| Tunnel | `scripts/start_tunnel.ps1` (Cloudflare) | GitHub's computers can't see your `localhost`; the tunnel gives your receiver a temporary public HTTPS address. |
| Demo helpers | `scripts/demo_defect.py` | Introduces / removes one deliberate bug for the FAIL demo. |
| Bonus | `.github/workflows/pages.yml`, `site/`, `scripts/send_email_report.py` | GitHub Pages deploy (only after tests pass on main) and e-mail reports. |

**Say to instructor:** "This is a Flask + SQLite portal with a pytest suite. A
GitHub Actions pipeline tests every push and pull request, produces a JSON report,
uploads it as an artifact and delivers it to my laptop through a Cloudflare tunnel."

---

## STEP 2 — Extract the ZIP and open it in VS Code

1. Right-click `assignment-portal.zip` → **Extract All…** → choose `C:\Labs` → **Extract**.
   You now have `C:\Labs\assignment-portal\` (make sure you don't get a double folder like `assignment-portal\assignment-portal`).
2. Open **VS Code** → **File → Open Folder…** → select `C:\Labs\assignment-portal` → **Select Folder** → if asked, click **Yes, I trust the authors**.
3. Open a terminal: menu **Terminal → New Terminal**. Make sure it says `PS C:\Labs\assignment-portal>`.
4. Allow PowerShell scripts (one time) and un-block the downloaded files:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
# answer Y if asked
Get-ChildItem -Recurse | Unblock-File
```

**Why:** Windows blocks scripts that came from the internet. `RemoteSigned` + `Unblock-File` lets *your* project scripts run.

**Expected output:** nothing (no error) — that means it worked.

**Screenshot:** `S2-project-open-in-vscode.png` (Explorer panel showing the folders).

**Say:** "I extracted the project and opened it in VS Code; the integrated terminal runs PowerShell in the project folder."

---

## STEP 3 — Install dependencies and run the portal

```powershell
.\scripts\setup.ps1
```

What it does: finds Python → creates a virtual environment `.venv` → installs Flask and pytest from `requirements.txt` → runs the tests once.

**Expected output (end):**
```
62 passed in ...s
SETUP COMPLETE - all tests passed.
```

Start the portal:

```powershell
.\scripts\run_portal.ps1
```

Your browser opens **http://127.0.0.1:5000**. (If not, open it yourself.)
Leave this terminal running. To stop the portal later: click the terminal and press **Ctrl + C**.

Try it:
1. Fill all four fields with a real-looking link (e.g. `https://github.com/you/lab`) → **Submit assignment** → green check animation, the submission appears under *Recent submissions* with date/time; total count increases.
2. Leave **Registration number** empty → red message *"Registration number is required."* Nothing saved.
3. Type `ftp://abc.com` or `hello` as URL → red URL message. Nothing saved.
4. Stop the portal (Ctrl+C) and start it again → your earlier submission is still there (SQLite file `instance\portal.db`).

> Tip: the browser checks fields while you type (JavaScript), but the **server** checks again — that's the real protection, and the tests check the server.

**Screenshots:** `S3a-portal-home.png`, `S3b-valid-submission-success.png`, `S3c-missing-regno-error.png`, `S3d-invalid-url-error.png`, `S3e-data-after-restart.png`.

**Say:** "Validation happens on the server in `validation.py`. Valid data is stored in SQLite, so it survives a restart. Invalid data returns HTTP 400 and is never written."

---

## STEP 4 — Run the automated tests

Open a **second** terminal (click the **+** in the terminal panel) and run:

```powershell
.\scripts\run_tests.ps1
```

(or the plain command: `.\.venv\Scripts\python.exe -m pytest`)

**Expected output:** each test listed with `PASSED`, then

```
= JSON test report written to reports/testreport.json  ->  PASS (62 passed, 0 failed, 0 skipped, 62 total) =
62 passed in ...
...
pytest exit code: 0   (0 = all passed, 1 = some tests failed)
```

Open `reports\testreport.json` in VS Code to see the machine-readable report.

The three required tests are:
* `test_01_valid_submission_is_saved_and_displayed`
* `test_02_missing_registration_number_is_rejected`
* `test_03_invalid_url_is_rejected`

Each test uses its **own temporary database** (pytest `tmp_path`), so your real data is never touched.

**Screenshot:** `A1-tests-pass-local.png`.

**Say:** "pytest uses Flask's test client to send real requests to the app. Each test gets an isolated temporary SQLite database. A failing test makes pytest exit with code 1, which is what makes GitHub Actions fail."

---

## STEP 5 — Create your GitHub repository

1. Go to **https://github.com** and sign in.
2. Top-right **+** → **New repository**.
3. **Repository name:** `assignment-portal`
4. Visibility: **Public** (needed for the free GitHub Pages bonus; Private also works for everything else).
5. **Do NOT** tick "Add a README", ".gitignore" or "license" (the project already has them).
6. Click **Create repository**. Keep this page open — you need its URL:
   `https://github.com/YOUR-USERNAME/assignment-portal.git`

**Screenshot:** `S5-empty-repo-created.png`.

**Say:** "I created an empty remote repository on GitHub; my local project will be pushed into it."

---

## STEP 6 — Push the project to GitHub

Run these one by one in the project folder (stop the portal first or use the second terminal):

```powershell
# 1. Tell Git who you are (once per computer)
git config --global user.name "Your Full Name"
git config --global user.email "you@example.com"

# 2. Make this folder a Git repository
git init

# 3. Name the main branch "main"
git branch -M main

# 4. Stage all files (the .gitignore keeps .venv, database and secrets OUT)
git add .

# 5. Save a snapshot (commit)
git commit -m "Initial commit: assignment portal, tests and CI pipeline"

# 6. Connect to GitHub (paste YOUR repo URL)
git remote add origin https://github.com/YOUR-USERNAME/assignment-portal.git

# 7. Upload to GitHub and remember the link between local main and origin/main
git push -u origin main
```

The first push opens a **browser login window** (Git Credential Manager) — click **Sign in with your browser** → **Authorize**.

**Expected output:** `* [new branch]      main -> main` and `branch 'main' set up to track 'origin/main'`.

Refresh your GitHub page → your files are there. Click the **Actions** tab → a run called *"Initial commit…"* starts automatically (push trigger).

> At this moment the receiver/tunnel aren't set up yet, so step 7 of the workflow prints *"REPORT_RECEIVER_URL is not configured - skipping"*. That's expected. The run should still be green.

**Screenshots:** `S6a-git-push-terminal.png`, `S6b-repo-files-on-github.png`, `S6c-first-actions-run.png`.

**Say:** "`git push` uploads my local commits to GitHub. Because the workflow has an `on: push` trigger for all branches, GitHub Actions started a test run automatically."

---

## STEP 7 — Repository secrets (GitHub Actions configuration)

The workflow file is already in `.github/workflows/ci.yml`; GitHub reads it automatically — nothing to "install". You only add **secrets** (private values the workflow can read but nobody can see).

First get your token: in VS Code terminal run

```powershell
.\scripts\start_receiver.ps1
```

It prints `YOUR REPORT TOKEN ...` followed by a long random string. **Copy it.** (Leave the receiver running — it's needed in Step 8 anyway.)

On GitHub: **your repo → Settings → Secrets and variables → Actions → New repository secret**

| Name | Value |
|---|---|
| `REPORT_TOKEN` | the token printed by `start_receiver.ps1` (also stored in `.receiver_token`) |
| `REPORT_RECEIVER_URL` | the Cloudflare URL from Step 8, e.g. `https://abc-def-ghi.trycloudflare.com` |

Add `REPORT_TOKEN` now; add `REPORT_RECEIVER_URL` after Step 8.

Optional bonus secrets (e-mail) and variable (`ENABLE_PAGES`) → see `docs/BONUS_PAGES_EMAIL.md`.

**Screenshot:** `S7-repository-secrets.png` (shows secret *names* only — values are hidden, which is the point).

**Say:** "Secrets are encrypted by GitHub and injected into the job as environment variables. The token is never in the code; the receiver rejects any request without it."

---

## STEP 8 — Run the local receiver and Cloudflare Tunnel

You need **two terminals kept open** during the whole demo.

### 8.1 Install cloudflared (one time)

```powershell
winget install --id Cloudflare.cloudflared -e
```

Then **close VS Code completely and open it again** (so the new program is on PATH). Check:

```powershell
cloudflared --version
```

Expected: `cloudflared version 202x.x.x ...`

> If `winget` is missing: download `cloudflared-windows-amd64.msi` from
> https://github.com/cloudflare/cloudflared/releases/latest , install it, reopen VS Code.

### 8.2 Terminal A — receiver

```powershell
.\scripts\start_receiver.ps1
```

Expected:
```
  GitHub Actions Test Report Receiver is RUNNING
  Listening on : http://127.0.0.1:8000
  ...
```

### 8.3 Terminal B — tunnel

```powershell
.\scripts\start_tunnel.ps1
```

Wait ~10 seconds. Look for a box containing a URL like:

```
https://plain-words-random-name.trycloudflare.com
```

Copy it → GitHub → **Settings → Secrets and variables → Actions** → create (or **update**) `REPORT_RECEIVER_URL` with that URL.

> ⚠️ The quick-tunnel URL **changes every time** you restart the tunnel. If you restart it, update the secret.
> Don't let the laptop sleep during the demo (Settings → System → Power → Screen and sleep → *Never* while plugged in).

### 8.4 Terminal C — prove it works before the demo

```powershell
.\scripts\check_delivery.ps1 -Url https://plain-words-random-name.trycloudflare.com
```

Expected: `1) Health check ... OK` then `HTTP 200` and `SUCCESS`. Terminal A shows a **NEW TEST REPORT RECEIVED** box, and `received_reports\testreport.json` appears.

This request travelled: your PC → internet → Cloudflare → tunnel → your receiver — the same path GitHub will use.

**Screenshots:** `S8a-receiver-running.png`, `S8b-tunnel-url.png`, `S8c-check-delivery-success.png`.

**Say:** "GitHub's runner is a different computer, so `localhost` there is not my laptop. cloudflared opens an outbound connection to Cloudflare and gives me a public HTTPS URL that forwards to `127.0.0.1:8000`. The workflow posts the report to that URL with a bearer token."

---

## STEP 9 — DEMO A: passing run

Receiver and tunnel running (Step 8), both secrets set.

```powershell
.\scripts\run_tests.ps1
```
All pass locally. Now make a small harmless change so there is something to push — e.g. open `README.md` and add a line `Demo A - passing run` at the bottom, save, then:

```powershell
git add .
git commit -m "Demo A: passing run"
git push
```

On GitHub: **Actions** tab → click the run **"Demo A: passing run"** → job **Run pytest and deliver report**.
* Green ✔ on every step.
* Expand **5. Show individual test results** → each test `[PASS ]`.
* Scroll the run page → **Summary** shows a table of all tests; **Artifacts** shows `testreport-run…` (download it).
* Expand **7. Deliver report…** → `HTTP 200 ... Report delivered`.

On your PC: Terminal A shows `Result : PASS [OK]`. Open `received_reports\testreport.json` — check `overall_result: "PASS"` and that `commit_sha` matches the commit on GitHub.

**Screenshots:** `A1`–`A6` in `docs/SCREENSHOT_CHECKLIST.md`.

**Say:** "The push triggered the workflow; all 62 tests passed; the job uploaded the JSON as an artifact and delivered the same JSON to my laptop."

---

## STEP 10 — DEMO B: introduce a defect → failing run

We use a **feature branch + pull request**, so you also demonstrate the PR trigger and `main` stays clean.

```powershell
# create and switch to a new branch
git checkout -b feature/demo-defect

# introduce ONE deliberate bug (disables the "registration number required" check)
.\.venv\Scripts\python.exe scripts\demo_defect.py break

# see exactly what changed
git diff

# prove locally that the tests catch it
.\scripts\run_tests.ps1
```

Expected locally: `6 failed, 56 passed`, including
`FAILED tests/test_portal.py::test_02_missing_registration_number_is_rejected` with message
`AssertionError: Missing registration number must be rejected (HTTP 400) assert 302 == 400`.

(Optional: run the portal and submit with an empty registration number — it is now wrongly accepted.)

Push the defective branch:

```powershell
git add validation.py
git commit -m "Demo B: deliberate defect - registration number no longer required"
git push -u origin feature/demo-defect
```

**Open a pull request:** GitHub shows a yellow bar *"feature/demo-defect had recent pushes"* → **Compare & pull request** → base: `main`, compare: `feature/demo-defect` → title "Demo B/C: defect and fix" → **Create pull request**.

Now you will see **two** runs in Actions:
1. event **push** (because you pushed a branch),
2. event **pull_request** (because a PR targeting `main` was opened).

Both turn **red ✗**. Open one:
* Step **4. Run automated tests** is red; the log shows the failing tests.
* Step **5** lists `[FAIL ] test_02_missing_registration_number_is_rejected` with the message; red **annotations** appear at the top of the run.
* Steps 6 & 7 still ran (they use `if: !cancelled()`), so the **FAIL report was uploaded and delivered**.
* The PR page shows **"Some checks were not successful"**.

On your PC: Terminal A shows `Result : FAIL [X]` and the failed test names; `received_reports\testreport.json` has `"overall_result": "FAIL"`.

**Do not delete this run** — it is your evidence.

**Say:** "I removed the registration-number check. Test 2 sends a form with no registration number and expects HTTP 400; it got 302 (saved), so pytest exited with code 1, GitHub marked the job failed, and the PR shows failing checks. The failure report still reached my laptop because the reporting steps run even after a failure."

---

## STEP 11 — DEMO C: fix the defect → passing again

```powershell
.\.venv\Scripts\python.exe scripts\demo_defect.py fix
.\scripts\run_tests.ps1           # 62 passed again
git add validation.py
git commit -m "Demo C: fix - restore registration number validation"
git push
```

(`git push` without arguments works because `-u` linked the branch earlier.)

GitHub: new **push** and **pull_request** runs on the same PR turn **green ✔**. The PR shows **All checks have passed** → click **Merge pull request** → **Confirm merge**.
Merging creates a new commit on `main`, which triggers one more **push** run on `main` (green).

PC: Terminal A shows `PASS`; `received_reports\testreport.json` is overwritten with the latest PASS report. Old reports stay in `received_reports\reports_history\` (`..._PASS.json`, `..._FAIL.json`, ...) — evidence of all three runs.

**Say:** "Restoring the check made all tests pass again; the PR became mergeable; after merging, main was tested again and the latest report on my laptop was updated to PASS."

---

## STEP 12 — Demonstrate pulling changes

Your local `main` doesn't yet contain the merge you did on GitHub. Pull it:

```powershell
git checkout main
git pull origin main
git log --oneline -5
```

Expected: `Fast-forward` / `Updating abc123..def456`, and the log shows the merge commit.

**Second demo — pull a change made on GitHub's website:**
1. On GitHub open `README.md` → pencil ✏️ icon → add a line → **Commit changes…** → *Commit directly to the main branch* → **Commit changes**. (This is a push on GitHub's side → a CI run starts.)
2. Locally: `git pull` → the new line appears in VS Code.

**Optional — clone (fresh copy) demo:**
```powershell
cd C:\Labs
git clone https://github.com/YOUR-USERNAME/assignment-portal.git assignment-portal-clone
cd assignment-portal-clone
git log --oneline -3
cd ..\assignment-portal
```

**Optional — run tests automatically after every pull (local hook):**
```powershell
.\scripts\install_git_hooks.ps1
```
After that, every `git pull` that brings new commits prints `[post-merge hook] ... running tests locally`.

### The important differences (memorize this)

| Thing | Where it runs | What it does | Triggers GitHub Actions? |
|---|---|---|---|
| `git push` | your PC → GitHub | uploads your commits | **Yes** – `push` event (our workflow: any branch) |
| `git pull` | GitHub → your PC | downloads + merges commits (`fetch` + `merge`) | **No.** Nothing happens on GitHub. (Optional local hook can run tests on your PC.) |
| GitHub **pull request** | github.com | a *request* to merge one branch into another, with review and checks | **Yes** – `pull_request` event when opened/updated (ours: PRs targeting `main`) |
| Actions **push trigger** (`on: push`) | GitHub runner | tests the commit you pushed | — |
| Actions **pull_request trigger** (`on: pull_request`) | GitHub runner | tests what `main` *would become* if the PR were merged | — |

A `git pull` and a "pull request" only share a word. **A local `git pull` never triggers a `pull_request` workflow.**

**Screenshots:** `S12a-git-pull-output.png`, `S12b-git-log-after-pull.png`.

---

## STEP 13 — Screenshots and final submission

Use `docs/SCREENSHOT_CHECKLIST.md` (tick each one). Windows: **Win + Shift + S** → drag → paste into Paint/Word or the snipping tool saves it.

Suggested submission folder:
```
DevOps_MidLab_<RegNo>/
  screenshots/  (all PNGs, named as in the checklist)
  reports/      (received_reports/reports_history/*.json  - PASS, FAIL, PASS)
  repo-link.txt (https://github.com/YOUR-USERNAME/assignment-portal)
  (optional) pages-link.txt
```

Final checks:
* Actions tab shows a **green**, a **red** and a **green** run — none deleted.
* The PR page shows the red check commit and the green check commit.
* `received_reports\reports_history` contains FAIL and PASS JSON files.

**Say:** "Here's the run history: pass, deliberate fail, fix. Each run produced a JSON report that's attached as an artifact and was also delivered to my laptop."

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `running scripts is disabled on this system` | Step 2 commands (`Set-ExecutionPolicy ...`, `Unblock-File`). |
| `python` opens Microsoft Store | Install Python from python.org with **Add to PATH**, or `setup.ps1` will use `py`. |
| `cloudflared` not recognized | Close and reopen VS Code after installing. |
| Step 7 log: `HTTP 401` | `REPORT_TOKEN` secret ≠ contents of `.receiver_token`. Copy again. |
| Step 7 log: `HTTP 404`/`530`/`Could not resolve host` | Tunnel stopped or URL changed → restart tunnel, update `REPORT_RECEIVER_URL`, click **Re-run jobs**. |
| Step 7 log: `skipping` | `REPORT_RECEIVER_URL` secret not set (or PR came from a fork — forks get no secrets). |
| `git push` rejected (`fetch first`) | `git pull --rebase origin main` then `git push`. |
| Port 5000/8000 busy | `$env:PORT=5050; .\.venv\Scripts\python.exe app.py` or `receiver.py --port 8001` (then tunnel to 8001). |
| Want to re-send a report | On the run page → **Re-run jobs** → **Re-run all jobs**. |
