# Push & Pull guide — 15 commands, each explained

Run everything in VS Code's PowerShell terminal inside the project folder.
Replace `YOUR-USERNAME`.

### 1. Git configuration (once per computer)
```powershell
git config --global user.name "Your Full Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
```
Your name/e-mail are written into every commit. The last line makes new repos start on `main`.

### 2. Initialize the local repository
```powershell
git init
```
Creates the hidden `.git` folder — the folder is now a Git repository.

### 3. Connect the GitHub remote
```powershell
git remote add origin https://github.com/YOUR-USERNAME/assignment-portal.git
git remote -v
```
`origin` is a nickname for your GitHub repo URL. `-v` shows it.

### 4. Create / name the main branch
```powershell
git branch -M main
```
Renames the current branch to `main` (safe even if it is already `main`).

### 5. Add files
```powershell
git status
git add .
```
`status` shows changed files. `add .` stages everything (except what `.gitignore` excludes:
`.venv`, database, reports, `.receiver_token`).

### 6. Commit
```powershell
git commit -m "Initial commit: assignment portal, tests and CI pipeline"
```
Saves a snapshot locally with a message. Nothing goes to GitHub yet.

### 7. Push to GitHub
```powershell
git push -u origin main
```
Uploads commits to GitHub. `-u` remembers that local `main` ↔ `origin/main`, so later you can
just type `git push` / `git pull`. **This triggers the `push` workflow.**

### 8. Clone the repository
```powershell
cd C:\Labs
git clone https://github.com/YOUR-USERNAME/assignment-portal.git assignment-portal-clone
cd assignment-portal-clone
```
Downloads a complete copy (all history) into a new folder.

### 9. Pull updated changes
```powershell
git pull
```
= `git fetch` (download new commits) + `git merge` (combine them into your branch).
**Does not trigger anything on GitHub.**

### 10. Create a feature branch
```powershell
git checkout -b feature/demo-defect
```
Creates a new branch and switches to it. Work here doesn't affect `main`.
(Newer equivalent: `git switch -c feature/demo-defect`.)

### 11. Push the feature branch
```powershell
git push -u origin feature/demo-defect
```
Creates the branch on GitHub. **Triggers a `push` run** (our workflow listens to all branches).

### 12. Create a pull request
On GitHub: yellow banner **Compare & pull request** (or **Pull requests → New pull request**,
base `main` ← compare `feature/demo-defect`) → title + description → **Create pull request**.
Optional CLI: `gh pr create --base main --head feature/demo-defect --title "Demo" --body "Demo"`.
**Triggers a `pull_request` run.** Every new push to that branch updates the PR and triggers again.

### 13. Check automated PR tests
On the PR page, scroll to the checks box: **"CI - Tests and Reports / Run pytest and deliver
report (pull_request)"** → **Details** to open the log. Red ✗ = failing, green ✔ = passing.
Also visible in the **Actions** tab (filter: *Event → pull_request*).

### 14. Merge the pull request
When checks are green: **Merge pull request** → **Confirm merge** → (optional) **Delete branch**.
Merging creates a commit on `main` → **triggers a `push` run on main** (and Pages, if enabled).

### 15. Pull the latest main locally
```powershell
git checkout main
git pull origin main
git log --oneline -5
```
Your local `main` now contains the merged work.

---

## push vs pull vs pull request vs triggers

| | What it is | Direction / place | Starts GitHub Actions? |
|---|---|---|---|
| `git push` | Git command | your PC → GitHub | **Yes**, `on: push` |
| `git pull` | Git command (`fetch`+`merge`) | GitHub → your PC | **No** |
| Pull request | GitHub feature: "please merge branch X into main", with review + checks | on github.com | **Yes**, `on: pull_request` (opened, new commits, reopened) |
| `push` trigger | workflow runs for the pushed commit | GitHub runner | — |
| `pull_request` trigger | workflow runs for the *merge result* of PR branch + `main` | GitHub runner | — |

❗ A local `git pull` **never** triggers a `pull_request` workflow. The word "pull" in
"pull request" means "please pull my changes into main" — it's a request on GitHub, not the command.

### Optional: run tests after every `git pull` (local only)
```powershell
.\scripts\install_git_hooks.ps1     # sets: git config core.hooksPath .githooks
```
`.githooks/post-merge` runs pytest on **your PC** after a pull that merged new commits.
It is not GitHub Actions and it doesn't run when Git says "Already up to date."
