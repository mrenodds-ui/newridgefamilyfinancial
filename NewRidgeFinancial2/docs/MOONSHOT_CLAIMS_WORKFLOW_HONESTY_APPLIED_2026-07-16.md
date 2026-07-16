# Claims Workflow Honesty — APPLIED

**Date:** 2026-07-16  
**Consult:** `MOONSHOT_WHATS_NEXT_SOFTDENT_STOP_TRELLIS_WAIT_2026-07-16.md`  
**Operator:** PROCEED  
**SoftDent:** STOP remains active — no SoftDent GUI / morning_bundle

## Shipped

| Item | Path / behavior |
|------|-----------------|
| ERA placeholder honesty | `nr2_era_inbox.py` — README ≠ remittance; chip `… — Empty ≠ $0 (placeholder only)` |
| Age buckets | `claims_outstanding` → `ageBuckets` + Claims UI strip |
| Staff-hidden toggle | `?includeStaffHidden=1` → `staffHiddenClaims`; unpaid totals unchanged |
| Paid-suppress panel | Claims UI shows TXN/ERA/Aging/Staff counts |
| Payer backfill snapshot | `app_data/nr2/payer_backfill.json` (stats only; Backfill button still Sensei/ODBC) |
| Optical UI | `nr2-optical-page-claims.html` / `.js` / theme CSS |

## Live validation (local)

- Outstanding count **150** · total **$52,270** · empty ≠ $0  
- Age buckets: 0-30 **79** · 31-60 **13** · 61-90 **15** · 90+ **43**  
- Staff-hidden rows: **4** (toggle only; totals stay 150 / $52,270)  
- ERA: `realFileCount=0` · `placeholderCount=1` · chip includes Empty ≠ $0  
- `forceClose` untouched · SoftDent write-back false · no Trellis invent

## Not done (blocked / out of scope)

- SoftDent morning_bundle attended (STOP)  
- Invented withBenefits (Trellis wait until 2026-07-20)  
- Inventing named payer mappings (Backfill payers remains operator/API action)
