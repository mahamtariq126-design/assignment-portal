# ==========================================================================
#  install_git_hooks.ps1 - OPTIONAL: run the tests automatically on YOUR
#  computer after every "git pull" that brings in new commits.
#  (This is a LOCAL convenience. It does NOT trigger GitHub Actions.)
# ==========================================================================
Set-Location (Split-Path -Parent $PSScriptRoot)
git config core.hooksPath .githooks
if ($LASTEXITCODE -eq 0) {
    Write-Host "Git hooks enabled: .githooks/post-merge will run pytest after each git pull." -ForegroundColor Green
    Write-Host "To disable:  git config --unset core.hooksPath"
}
