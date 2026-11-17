# Screenshot evidence checklist

Shortcut: **Win + Shift + S**. Save as PNG with these names. ☐ = to do.

## Setup & portal
- ☐ `S2-project-open-in-vscode.png` — VS Code Explorer with the project folders
- ☐ `S3a-portal-home.png` — portal home page (hero + form)
- ☐ `S3b-valid-submission-success.png` — green check popup / success banner
- ☐ `S3c-missing-regno-error.png` — red "Registration number is required."
- ☐ `S3d-invalid-url-error.png` — red URL error (e.g. `ftp://…`)
- ☐ `S3e-data-after-restart.png` — submissions + total still there after restarting `app.py`
- ☐ `S3f-mobile-view.png` — browser DevTools (F12 → phone icon) mobile layout

## GitHub setup
- ☐ `S5-empty-repo-created.png`
- ☐ `S6a-git-push-terminal.png` — `git push -u origin main` output
- ☐ `S6b-repo-files-on-github.png`
- ☐ `S7-repository-secrets.png` — secret **names** listed (values hidden)
- ☐ `S8a-receiver-running.png` — Terminal A "Receiver is RUNNING"
- ☐ `S8b-tunnel-url.png` — Terminal B with the trycloudflare URL
- ☐ `S8c-check-delivery-success.png`

## Demo A — PASS
- ☐ `A1-tests-pass-local.png` — `62 passed`, exit code 0
- ☐ `A2-actions-run-green.png` — Actions list with green run (event: push)
- ☐ `A3-step5-individual-results.png` — expanded step 5 `[PASS ]` list
- ☐ `A4-run-summary-and-artifact.png` — Summary table + Artifacts section
- ☐ `A5-step7-delivered.png` — step 7 log `HTTP 200 ... delivered`
- ☐ `A6-receiver-pass-and-json.png` — Terminal A PASS box + `received_reports\testreport.json` open in VS Code

## Demo B — FAIL
- ☐ `B1-defect-diff.png` — `git diff` showing the changed line
- ☐ `B2-tests-fail-local.png` — `6 failed, 56 passed`, exit code 1
- ☐ `B3-feature-branch-push.png` — `git push -u origin feature/demo-defect`
- ☐ `B4-pull-request-created.png`
- ☐ `B5-actions-two-red-runs.png` — red push + red pull_request runs
- ☐ `B6-failed-step-log.png` — step 4/5 showing `test_02…` and `assert 302 == 400`
- ☐ `B7-pr-checks-failed.png` — PR "Some checks were not successful"
- ☐ `B8-receiver-fail-and-json.png` — Terminal A FAIL box + JSON with `"overall_result": "FAIL"`

## Demo C — FIX
- ☐ `C1-fix-and-tests-pass-local.png`
- ☐ `C2-actions-green-again.png`
- ☐ `C3-pr-checks-passed.png` — "All checks have passed"
- ☐ `C4-pr-merged.png`
- ☐ `C5-main-push-run-green.png`
- ☐ `C6-receiver-pass-updated.png` — Terminal A PASS + updated JSON (new run_id / commit)
- ☐ `C7-reports-history-folder.png` — `received_reports\reports_history` with PASS/FAIL files

## Pull
- ☐ `P1-git-pull-output.png`
- ☐ `P2-git-log-after-pull.png`
- ☐ `P3-actions-history-pass-fail-pass.png` — Actions list showing all runs (none deleted)

## Bonus (if done)
- ☐ `X1-pages-deploy-run.png` — "Deploy GitHub Pages" run green
- ☐ `X2-pages-site-live.png` — the `https://YOUR-USERNAME.github.io/assignment-portal/` page
- ☐ `X3-email-pass.png` and `X4-email-fail.png`
