# ==========================================================================
#  check_delivery.ps1 - BEFORE the demo, prove that the receiver and the
#  tunnel work, by sending your latest LOCAL test report through them.
#
#  Usage:
#    .\scripts\check_delivery.ps1                                   # direct to localhost
#    .\scripts\check_delivery.ps1 -Url https://xxxx.trycloudflare.com   # through the tunnel
# ==========================================================================
param([string]$Url = "http://127.0.0.1:8000")
Set-Location (Split-Path -Parent $PSScriptRoot)
$py = ".\.venv\Scripts\python.exe"
if (-not (Test-Path ".receiver_token")) { Write-Host "Start the receiver first: .\scripts\start_receiver.ps1" -ForegroundColor Red; exit 1 }
if (-not (Test-Path "reports\testreport.json")) {
    Write-Host "No local report yet - running tests to create one..." -ForegroundColor Cyan
    & $py -m pytest -q | Out-Null
}

Write-Host "1) Health check: $Url/health" -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "$($Url.TrimEnd('/'))/health" -TimeoutSec 20
    Write-Host "   OK -> $($health | ConvertTo-Json -Compress)" -ForegroundColor Green
} catch {
    Write-Host "   FAILED: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Is the receiver running? Is the tunnel running? Is the URL current?"
    exit 1
}

Write-Host "2) Sending reports\testreport.json with the secret token..." -ForegroundColor Cyan
$env:REPORT_RECEIVER_URL = $Url
$env:REPORT_TOKEN = (Get-Content ".receiver_token" -Raw).Trim()
& $py scripts\send_report.py reports\testreport.json --strict
$code = $LASTEXITCODE
Remove-Item Env:\REPORT_RECEIVER_URL, Env:\REPORT_TOKEN
if ($code -eq 0) {
    Write-Host "SUCCESS - check the receiver window and received_reports\testreport.json" -ForegroundColor Green
} else {
    Write-Host "Delivery FAILED - see the message above." -ForegroundColor Red
}
exit $code
