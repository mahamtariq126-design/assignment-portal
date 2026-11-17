# Demonstration script: A (pass) → B (fail) → C (fix)

**Before you start:** portal works locally, repo pushed, secrets set, receiver (Terminal A) and
tunnel (Terminal B) running, `check_delivery.ps1` succeeded. (LAB_GUIDE Steps 3–8.)

---

## DEMO A — passing run
```powershell
.\scripts\run_tests.ps1                 # 62 passed locally
# make a harmless edit, e.g. add "Demo A" at the end of README.md, save
git add .
git commit -m "Demo A: passing run"
git push
```
Show: Actions → run "Demo A: passing run" → green; step 5 list of `[PASS ]` tests; Summary table;
Artifacts; step 7 `HTTP 200`; Terminal A box `PASS`; `received_reports\testreport.json`.

---

## DEMO B — failing run (one deliberate, reversible defect)

**The defect:** `validation.py` line marked `# REG-REQUIRED-CHECK`

```diff
     if not reg_no:
-        errors["registration_number"] = "Registration number is required."  # REG-REQUIRED-CHECK
+        pass  # DEFECT (demo): registration number check disabled  # REG-REQUIRED-CHECK
```
Effect: an empty registration number is accepted and saved.

```powershell
git checkout -b feature/demo-defect
.\.venv\Scripts\python.exe scripts\demo_defect.py break     # or edit the line by hand
git diff
.\scripts\run_tests.ps1                                     # 6 failed, 56 passed
git add validation.py
git commit -m "Demo B: deliberate defect - registration number no longer required"
git push -u origin feature/demo-defect
```
Then create the PR (base `main` ← `feature/demo-defect`).

Tests that catch it (actually observed when this project was built):
```
FAILED tests/test_portal.py::test_02_missing_registration_number_is_rejected
FAILED tests/test_portal.py::test_each_missing_field_is_rejected[registration_number-...]
FAILED tests/test_portal.py::test_field_missing_from_request_entirely_is_rejected
FAILED tests/test_portal.py::test_whitespace_only_registration_number_is_rejected
FAILED tests/test_validation.py::test_missing_registration_number_produces_error
FAILED tests/test_validation.py::test_empty_form_reports_all_four_fields
```
Main message: `AssertionError: Missing registration number must be rejected (HTTP 400) — assert 302 == 400`

Show: red push run + red pull_request run; red step 4; failed tests in step 5 and annotations;
artifact still uploaded; step 7 delivered; PR "Some checks were not successful";
Terminal A box `FAIL`; JSON `"overall_result": "FAIL"` with `failure_message`.

---

## DEMO C — fix
```powershell
.\.venv\Scripts\python.exe scripts\demo_defect.py fix
.\scripts\run_tests.ps1                 # 62 passed
git add validation.py
git commit -m "Demo C: fix - restore registration number validation"
git push
```
Show: new green runs on the PR → **Merge pull request** → green push run on `main` →
Terminal A `PASS` → `received_reports\testreport.json` updated; history folder holds FAIL and PASS copies.
Then `git checkout main` + `git pull origin main` (pull demonstration).

---

## Alternative (simpler, no branch)
Do B and C directly on `main` (`break` → commit → `git push`; `fix` → commit → `git push`).
Works the same for the push trigger, but you won't demonstrate the PR trigger.

## Never
* Don't delete the failed run or force-push over it — it is your evidence.
* If something went wrong with delivery, use **Re-run jobs** instead of new commits.
