# ==========================================================================
#  run_tests.ps1 - run pytest, then print each test result from the
#  generated JSON report (reports\testreport.json).
# ==========================================================================
Set-Location (Split-Path -Parent $PSScriptRoot)
$py = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) { Write-Host "Run .\scripts\setup.ps1 first." -ForegroundColor Red; exit 1 }

& $py -m pytest
$exitCode = $LASTEXITCODE
Write-Host ""
& $py scripts\show_report.py reports\testreport.json
Write-Host ""
Write-Host "pytest exit code: $exitCode   (0 = all passed, 1 = some tests failed)" -ForegroundColor Cyan
exit $exitCode
