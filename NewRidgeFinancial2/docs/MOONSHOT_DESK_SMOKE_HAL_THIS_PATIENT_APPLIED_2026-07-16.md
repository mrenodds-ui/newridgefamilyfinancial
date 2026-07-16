# HAL Desk Smoke / This-Patient — APPLIED

**Date:** 2026-07-16  
**Consult backlog #2:** `MOONSHOT_WHATS_NEXT_SOFTDENT_STOP_TRELLIS_WAIT_2026-07-16.md`  
**Operator:** NEXT  
**SoftDent STOP:** still active — no SoftDent GUI / morning_bundle

## Diagnosis

`/api/health/desk-smoke` was returning **HTTP 503** whenever `ok=false`. Live payload was complete: only failure is honest **`beam_desk_proof` MISMATCH** (close SoftDent `$53,117` vs live `$52,270`). **`this_patient_shortcut` already covered=true**. Treating RED as transport death hid fiduciary drift.

## Shipped

| Change | Path |
|--------|------|
| Smoke HTTP 200 when checks ran; 503 only if runner produced no checks | `nr2_http_server.py` |
| Drift + this-patient bit in smoke face paint | `nr2-optical-page-wire.js` |
| Desk smoke face + RUN SMOKE on Claims | `nr2-optical-page-claims.html` / `.js` |
| Desk smoke face + RUN SMOKE on HAL | `nr2-optical-page-hal.html` / `.js` |
| Hub paints honest RED last-smoke | `nr2-optical-pages-hub.js` |

## Validation

- Live smoke returns **HTTP 200** with `ok=false` · `status=RED` · `deskProof=MISMATCH`  
- `thisPatientShortcutCovered=true`  
- `forceCloseAvailable` stays false (lasers green)  
- Claims → Ask HAL about this claim still seeds `nr2.hal.patientContext` (initials+hash)  
- No SoftDent write-back · empty ≠ $0 · no invented MATCH

## Not done

- Re-attesting period-close to force MATCH (would mask real beam drift; SoftDent STOP blocks attended money-bundle refresh)
- Trellis withBenefits invent (wait Mon 2026-07-20)
