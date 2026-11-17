# ==========================================================================
#  start_tunnel.ps1 - expose the local receiver to the internet with a free
#  Cloudflare "quick tunnel".
#
#  Usage:  .\scripts\start_tunnel.ps1            (receiver on port 8000)
#          .\scripts\start_tunnel.ps1 -Port 8001
#
#  Look for a line like:
#     https://some-random-words.trycloudflare.com
#  Put that URL into the GitHub secret REPORT_RECEIVER_URL.
#  The URL CHANGES every time you restart this script -> update the secret.
#  Keep this window OPEN during the demonstration.
# ==========================================================================
param([int]$Port = 8000)
if (-not (Get-Command cloudflared -ErrorAction SilentlyContinue)) {
    Write-Host "cloudflared is not installed (or this window was opened before installing it)." -ForegroundColor Red
    Write-Host "Install it with:   winget install --id Cloudflare.cloudflared -e" -ForegroundColor Yellow
    Write-Host "Then CLOSE and REOPEN the terminal and run this script again."
    exit 1
}
Write-Host "Starting Cloudflare quick tunnel -> http://127.0.0.1:$Port" -ForegroundColor Cyan
Write-Host "Copy the https://....trycloudflare.com URL printed below into the GitHub secret REPORT_RECEIVER_URL." -ForegroundColor Yellow
Write-Host ""
cloudflared tunnel --url "http://127.0.0.1:$Port"
