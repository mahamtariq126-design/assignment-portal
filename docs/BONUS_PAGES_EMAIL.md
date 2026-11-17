# Bonus: GitHub Pages + e-mail reports

## A. GitHub Pages (static demo)

**Important:** GitHub Pages only serves static files (HTML, CSS, JS). It **cannot run Python,
Flask or SQLite**. So Pages hosts `site/` — a front-end demo with the same design; it validates in
the browser and stores demo submissions in the browser only. The real portal runs with `python app.py`.

### How the safety gate works (`.github/workflows/pages.yml`)
* Triggered by `workflow_run` when **"CI - Tests and Reports" completes**
* Job runs only if: `ENABLE_PAGES == 'true'` **and** CI conclusion is `success` **and** the CI
  event was `push` **and** the branch is `main`
* Re-runs pytest on the exact commit before deploying
* → failed runs, feature branches and PR runs never publish

### Enable it
1. Repository must be **Public** (free accounts).
2. **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. **Settings → Secrets and variables → Actions → Variables → New repository variable**:
   `ENABLE_PAGES` = `true`.
4. Push any commit to `main` (or merge a PR). After CI is green, Actions shows
   **"Deploy GitHub Pages (after tests pass)"**.

### Where is the URL?
* In that run: the **deploy** job box shows the link (environment `github-pages`).
* Or **Settings → Pages** → "Your site is live at …"
* Usually: `https://YOUR-USERNAME.github.io/assignment-portal/`

The page header shows a badge "Latest CI: PASS – 62/62 tests passed – commit abc1234" read from the
deployed `testreport.json`.

Demo idea: during Demo B (red), point out that **no** Pages deployment happened.

## B. E-mail reports

`scripts/send_email_report.py` runs in step 8 of `ci.yml` after **both** passing and failing runs.
If the secrets are missing it prints "skipping" and does nothing.

E-mail contains: subject `[PASS|FAIL] repo @ branch (x/y passed) - commit abc1234`, commit SHA,
overall status, total/passed/failed, every test with status and failure message, link to the run,
and the JSON attached.

### Gmail setup
1. Turn on **2-Step Verification** for your Google account.
2. Google Account → Security → **App passwords** (search "App passwords") → create one named
   "GitHub Actions" → copy the 16-character password.
3. Add repository secrets:

| Secret | Value |
|---|---|
| `SMTP_SERVER` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USERNAME` | `you@gmail.com` |
| `SMTP_PASSWORD` | the 16-char App password |
| `EMAIL_TO` | `you@gmail.com` (or instructor, comma-separated) |

Outlook/Office365: `smtp.office365.com`, port `587` (your institution may block SMTP AUTH).

**Never** put passwords in code or commit them. They live only in GitHub Secrets.
