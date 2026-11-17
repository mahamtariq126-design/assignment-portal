# ==========================================================================
#  start_receiver.ps1 - start the local test-report receiver on port 8000.
#
#  The first time, it creates a random secret token in .receiver_token and
#  prints it. Copy that token into the GitHub secret REPORT_TOKEN.
#  Keep this window OPEN during the demonstration.
# ==========================================================================
Set-Location (Split-Path -Parent $PSScriptRoot)
$py = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) { Write-Host "Run .\scripts\setup.ps1 first." -ForegroundColor Red; exit 1 }

if (-not (Test-Path ".receiver_token")) {
    $token = & $py -c "import secrets; print(secrets.token_urlsafe(32))"
    [System.IO.File]::WriteAllText((Join-Path (Get-Location) ".receiver_token"), $token.Trim())
    Write-Host "A new secret token was created and saved in .receiver_token" -ForegroundColor Green
}
$token = (Get-Content ".receiver_token" -Raw).Trim()

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Yellow
Write-Host " YOUR REPORT TOKEN (put this in GitHub secret REPORT_TOKEN):" -ForegroundColor Yellow
Write-Host " $token" -ForegroundColor White
Write-Host "==================================================================" -ForegroundColor Yellow
Write-Host ""
& $py receiver.py --port 8000
