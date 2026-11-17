# GitHub setup — repository, secrets and variables

## 1. Create the repository
GitHub → **+** (top right) → **New repository** → name `assignment-portal` → **Public** →
leave *Add README / .gitignore / license* **unticked** → **Create repository**.

## 2. First push
See `PUSH_PULL_GUIDE.md` commands 1–7. On the first `git push` a browser window asks you to
sign in (Git Credential Manager). Approve it.

## 3. Check that Actions is enabled
Repo → **Actions** tab. If you see *"Workflows aren't being run on this repository"*, click
**I understand my workflows, go ahead and enable them**.
(Settings → Actions → General → *Allow all actions and reusable workflows* is the default.)

## 4. Repository secrets
Repo → **Settings** → left menu **Secrets and variables** → **Actions** → tab **Secrets** →
**New repository secret**.

| Secret | Required? | Value |
|---|---|---|
| `REPORT_TOKEN` | yes (for delivery) | printed by `.\scripts\start_receiver.ps1`; also in the file `.receiver_token` |
| `REPORT_RECEIVER_URL` | yes (for delivery) | the tunnel URL, e.g. `https://xxx-yyy.trycloudflare.com` (`/report` is added automatically) |
| `SMTP_SERVER` | e-mail bonus | `smtp.gmail.com` |
| `SMTP_PORT` | e-mail bonus | `587` |
| `SMTP_USERNAME` | e-mail bonus | your Gmail address |
| `SMTP_PASSWORD` | e-mail bonus | a Gmail **App password** (16 chars) – never your real password |
| `EMAIL_TO` | e-mail bonus | recipient(s), comma separated |
| `EMAIL_FROM` | optional | defaults to `SMTP_USERNAME` |

To change a secret later: click its name → **Update secret**.

Optional — with the GitHub CLI (`winget install GitHub.cli`, then `gh auth login`):
```powershell
gh secret set REPORT_TOKEN --body (Get-Content .receiver_token -Raw).Trim()
gh secret set REPORT_RECEIVER_URL --body "https://xxx-yyy.trycloudflare.com"
```

## 5. Repository variable (Pages bonus only)
Same page → tab **Variables** → **New repository variable** → Name `ENABLE_PAGES`, Value `true`.
And **Settings → Pages → Build and deployment → Source: GitHub Actions**.

## 6. (Optional) protect main
Settings → Branches → **Add branch ruleset** (or classic rule) for `main` →
*Require status checks to pass* → choose **Run pytest and deliver report**.
Then a red PR cannot be merged — a nice extra to show.

## Notes
* Secrets are **not** given to workflows triggered by pull requests from **forks**. Our PRs come
  from branches in your own repo, so they work.
* Secret values are masked (`***`) in logs.
