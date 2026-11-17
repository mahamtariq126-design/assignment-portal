# ==========================================================================
#  setup.ps1 - one-time setup on Windows.
#  Creates a virtual environment (.venv), installs Flask + pytest,
#  then runs the test suite once to prove everything works.
#
#  Run from the project folder:   .\scripts\setup.ps1
# ==========================================================================
Set-Location (Split-Path -Parent $PSScriptRoot)

Write-Host ""
Write-Host "=== Step 1/4: Finding Python ===" -ForegroundColor Cyan
$basePython = $null
foreach ($candidate in @("python", "py")) {
    if (Get-Command $candidate -ErrorAction SilentlyContinue) {
        $version = & $candidate --version 2>&1
        if ($LASTEXITCODE -eq 0 -and "$version" -match "Python 3\.(\d+)") {
            if ([int]$Matches[1] -ge 9) { $basePython = $candidate; break }
        }
    }
}
if (-not $basePython) {
    Write-Host "Python 3.9+ was not found. Install it from https://www.python.org/downloads/ and tick 'Add python.exe to PATH'." -ForegroundColor Red
    exit 1
}
Write-Host "Using: $basePython ($(& $basePython --version 2>&1))"

Write-Host ""
Write-Host "=== Step 2/4: Creating virtual environment .venv ===" -ForegroundColor Cyan
if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    & $basePython -m venv .venv
    if ($LASTEXITCODE -ne 0) { Write-Host "Could not create .venv" -ForegroundColor Red; exit 1 }
} else {
    Write-Host ".venv already exists - reusing it."
}
$py = ".\.venv\Scripts\python.exe"

Write-Host ""
Write-Host "=== Step 3/4: Installing dependencies (Flask, pytest) ===" -ForegroundColor Cyan
& $py -m pip install --upgrade pip --quiet
& $py -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { Write-Host "pip install failed - check your internet connection." -ForegroundColor Red; exit 1 }

Write-Host ""
Write-Host "=== Step 4/4: Running the automated tests ===" -ForegroundColor Cyan
& $py -m pytest -q
$testExit = $LASTEXITCODE

Write-Host ""
if ($testExit -eq 0) {
    Write-Host "SETUP COMPLETE - all tests passed." -ForegroundColor Green
} else {
    Write-Host "Setup finished, but some tests FAILED (exit code $testExit)." -ForegroundColor Yellow
}
Write-Host "Next: .\scripts\run_portal.ps1   (opens the portal at http://127.0.0.1:5000)"
exit $testExit
