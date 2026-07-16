# HAL Trellis dental insurance verification (Mon–Thu)

## What HAL learned
SoftDent schedule → Vyne Trellis **Add Patient → Verify → ClearCoverage** for Mon–Thu chairs.

## Schedule
| Lane | When | What |
|------|------|------|
| SoftDent GUI money pulls | **9:00 PM** night-before | Aging / register / collections (Excel\|Preview only) |
| APScheduler `nr2-trellis-verify` | Mon–Thu **22:00** local (while NR2 runs) | Build **next clinical day** worklist + pending |
| Windows Task Scheduler | Mon–Thu **1:00 AM** interactive | Headed Playwright Verify + report pull (`--force --verify --same-day`) for **today's** chairs |
| Windows Task Scheduler | Mon–Thu **2:00 AM** interactive | AM withBenefits proof (`prove_trellis_withbenefits_am.py`) |

Thu night worklist targets **Monday**. Mon–Wed night worklists target the next calendar day. The **1:00 AM** pull uses `--same-day` so Monday 1 AM verifies Monday chairs (using the worklist built Thu night).

## Credentials
Gitignored `.env.vyne.local`:
```
VYNE_AUTOMATION_USERNAME=…
VYNE_AUTOMATION_PASSWORD=…   # Wichita only — never Emporia
```

## Enable UI verify in APScheduler
Set user/process env `NR2_TRELLIS_VERIFY=1` (Task Scheduler script already passes `--verify`).

## Manual
```powershell
.\.venv\Scripts\python.exe scripts\run_trellis_nightly_verify.py --force
.\.venv\Scripts\python.exe scripts\run_trellis_nightly_verify.py --force --verify --same-day
# or
POST /api/scheduler/insurance-verify-run  {"force": true, "runVerify": true}
```

Install Task Scheduler:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\install_trellis_nightly_verify_task.ps1
```

## Outputs
`app_data/nr2/vyne_pulls/tomorrow_trellis_{add_worklist,pending_batch,verify_results}_YYYY-MM-DD.json`

After headed `--verify`, also:
`app_data/nr2/vyne_pulls/trellis_eligibility_report_YYYY-MM-DD.html`  
(full ClearCoverage benefits: deductible, annual max, Preventive/Basic/Major/Ortho services + expanded ADA codes/%)

Rebuild report only:
```powershell
.\.venv\Scripts\python.exe NewRidgeFinancial2\scripts\build_trellis_eligibility_report.py --date YYYY-MM-DD --open
```

Status-only rows (Eligible but no `benefits.scrapeOk`) are **re-queued** on the next `--verify` so ClearCoverage can be scraped. To force a full re-scrape of everyone:
```powershell
$env:NR2_TRELLIS_FORCE_BENEFITS=1
.\.venv\Scripts\python.exe scripts\run_trellis_nightly_verify.py --force --verify --same-day
```

Batch log (streamed): `app_data/nr2/vyne_pulls/trellis_verify_batch_YYYY-MM-DD.log`

## HAL chat
Ask: “nightly Trellis verify” / “1am Trellis report” / “insurance verification” → `policy:trellis-nightly-verify`.
