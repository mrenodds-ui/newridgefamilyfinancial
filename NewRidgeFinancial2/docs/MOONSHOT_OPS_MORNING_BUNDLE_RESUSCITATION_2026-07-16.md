# Ops Package — Morning Bundle Resuscitation (PARTIAL — SoftDent stop)

**Date:** 2026-07-16  
**Consult:** `MOONSHOT_WHATS_NEXT_AFTER_POLISH_P10_2026-07-16.md`  
**Operator:** PROCEED EXACTLY AND DO NOT DEVIATE  
**SoftDent rule:** `.cursor/rules/softdent-agent-stop-now.mdc` — **active hard stop**

## What was done (exact consult lane, non-SoftDent)

| Step | Result |
|------|--------|
| Resuscitate NR2 on `https://127.0.0.1:8765/` | **DONE** — `scripts/start_nr2_browser.ps1 -NoBrowser -SkipModelWarmup -SkipValidation` (PID listen on 8765) |
| `import-readiness` HTTP 200 | **DONE** — lasers green · `emptyNotZero=true` · blocking=[] |
| `money-beams` HTTP 200 | **DONE** — `/api/hal/tools/money-beams` · SoftDent `$52,270` · QB `$78,399` · `importStale=false` |
| `claimsOutstanding` / `arAging` HTTP 200 | **DONE** — hasData true · AR total `$44,068.69` · claims count 150 |
| `trellis/am-proof` HTTP 200 | **DONE** — ok=true |
| `softdent/excel-probe` HTTP 200 | **DONE** — `excelAvailable=true` · Print Preview present · last probe cancelled (never File/Printer OK) |
| `forceCloseAvailable` stays false | **HONORED** — lasers green · period-close `status=completed` · wire only enables Force Close when lasers red / stalled / blocked |
| SoftDent attended Excel / `morning_bundle_attended.py` | **BLOCKED** by SoftDent STOP NOW rule |

## Consult validation gate status

1. Morning-bundle / money endpoints respond (no WinError 10061) — **PASS** after server start  
2. SoftDent Excel / Print Preview export path — **NOT RUN** (SoftDent hard stop)  
3. `forceCloseAvailable` remains false — **PASS**  
4. empty ≠ $0 / PHI initials+hash — **PASS** on live beams (`emptyNotZero=true`)

## Remaining exact next step (blocked until SoftDent stop lifted)

`periodClose.morningBundle` is still **null** → optical BUNDLE gate stays **RED** (“No morning bundle signal”).

Once the operator says **resume SoftDent** / **lift SoftDent stop**:

1. Confirm SoftDent signed on (`COMPUTE` / env override).  
2. Run attended: `python scripts/morning_bundle_attended.py --yes --refresh-close` (Excel or Print Preview only — never File, never Printer).  
3. Re-probe: `morningBundle.ok=true` (or honest fail) · BUNDLE gate updates · `forceCloseAvailable` still false unless lasers go red.

## What was NOT done (by design under SoftDent stop)

- No SoftDent launch / GUI automation / Output Options clicks  
- No `morning_bundle_attended.py`  
- No `probe_softdent_excel_output_options.py` re-run  
- No invent Excel drops / Select File Name paths  
- No flip of `forceCloseAvailable` / pilot attestation
