# ==========================================================================
#  run_portal.ps1 - start the Flask portal and open it in your browser.
#  Stop the server with Ctrl+C.
# ==========================================================================
Set-Location (Split-Path -Parent $PSScriptRoot)
$py = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) { Write-Host "Run .\scripts\setup.ps1 first." -ForegroundColor Red; exit 1 }

Write-Host "Starting the Assignment Submission Portal at http://127.0.0.1:5000 ..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C in this window to stop it." -ForegroundColor Cyan
Start-Job -ScriptBlock { Start-Sleep -Seconds 2; Start-Process "http://127.0.0.1:5000" } | Out-Null
& $py app.py
