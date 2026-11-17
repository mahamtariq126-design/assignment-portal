# Local receiver + Cloudflare Tunnel

## Why a tunnel?
GitHub Actions runs on a computer in GitHub's data centre. On that computer, `localhost`
means *that* computer — not your laptop. Your laptop is also behind a home/university router,
so the internet can't reach it directly.

**Cloudflare quick tunnel** (`cloudflared`) solves this: your laptop opens an *outgoing*
connection to Cloudflare, and Cloudflare gives you a random public HTTPS address
(`https://xxx.trycloudflare.com`) that forwards to `http://127.0.0.1:8000` on your laptop.
No account, no router changes, free.

```
GitHub runner --HTTPS POST /report--> xxx.trycloudflare.com --> cloudflared (your PC) --> receiver.py :8000 --> received_reports\testreport.json
```

## Install (once)
```powershell
winget install --id Cloudflare.cloudflared -e
```
Close and reopen VS Code, then `cloudflared --version`.
Alternative: download the `.msi` from https://github.com/cloudflare/cloudflared/releases/latest.

## Run (every demo session) — keep both windows open

**Terminal A – receiver**
```powershell
.\scripts\start_receiver.ps1
```
* creates `.receiver_token` the first time and prints the token → GitHub secret `REPORT_TOKEN`
* listens on `http://127.0.0.1:8000` (`/health`, `POST /report`)

**Terminal B – tunnel**
```powershell
.\scripts\start_tunnel.ps1
# same as: cloudflared tunnel --url http://127.0.0.1:8000
```
Copy the `https://….trycloudflare.com` URL → GitHub secret `REPORT_RECEIVER_URL`.

**Terminal C – self-test**
```powershell
.\scripts\check_delivery.ps1 -Url https://xxx.trycloudflare.com
```

## How the workflow sends the report
Step 7 of `ci.yml`:
```yaml
env:
  REPORT_RECEIVER_URL: ${{ secrets.REPORT_RECEIVER_URL }}
  REPORT_TOKEN: ${{ secrets.REPORT_TOKEN }}
run: python scripts/send_report.py reports/testreport.json
```
`send_report.py` POSTs the JSON to `<URL>/report` with `Authorization: Bearer <token>`,
retries 3×, and prints a warning (without failing the job) if your PC is unreachable — so a
delivery problem never hides the real test result.

## What the receiver does
* Rejects requests without the correct token → **401**
* Rejects non-JSON → **400**; rejects JSON missing required fields / inconsistent counts → **422**
* Accepts both `PASS` and `FAIL` reports → **200**
* Overwrites `received_reports\testreport.json` (atomic write) and keeps a copy in
  `received_reports\reports_history\testreport_<time>_run<id>_<PASS|FAIL>.json`
* Prints a clear box in the terminal for each report

## Keeping it alive during the demo
* Don't close Terminal A or B. Don't press Ctrl+C in them.
* Disable sleep while plugged in (Settings → System → Power).
* The quick-tunnel URL changes every restart → update the secret, then on GitHub **Re-run jobs**.
* Quick tunnels are for testing/demos (no uptime guarantee). For a permanent URL, use a named
  tunnel with your own domain (`cloudflared tunnel login` / `create` / `route dns`) — not needed for this lab.

## Alternative relays
If Cloudflare is blocked on your network: `ngrok http 8000` (free account + authtoken) gives a
similar `https://….ngrok-free.app` URL — put that in `REPORT_RECEIVER_URL` instead.
