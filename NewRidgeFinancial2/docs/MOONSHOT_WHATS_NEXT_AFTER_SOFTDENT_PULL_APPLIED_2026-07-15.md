# Moonshot AI — SoftDent GUI Export Hardening (APPLIED)

**Date:** 2026-07-15  
**Build:** `nr2-12031-softdent-export-harden`  
**Consult:** `MOONSHOT_WHATS_NEXT_AFTER_SOFTDENT_PULL_2026-07-15.md`  
**Operator:** approve

## What shipped

1. **`softdent_gui_export.export_report_by_id`** — preflight SoftDent running, up to 3 attempts with 2s/5s/10s backoff, `prepare_softdent_for_next_report` between tries, cancel stale/printer dialogs on fail, min-bytes validation (`EXPORT_MIN_BYTES=64`)
2. **`daily_closeout.run_period_close`** — SoftDent pull failure no longer stalls: `fallback=attest_only`, `guiExport=false`, still completes beam-grounded close (empty ≠ $0)
3. **`hal_brain_tools.softdent_export`** — returns `fileSizeBytes` on success

## SoftDent doctrine

- Write-back **FORBIDDEN**
- Select File Name keeps SoftDent's folder — never SoftDentReportExports / `C:\SOFTDE~1`
- Excel / Print Preview only

## Real paths

- `NewRidgeFinancial2/softdent_gui_export.py`
- `NewRidgeFinancial2/daily_closeout.py`
- `NewRidgeFinancial2/hal_brain_tools.py`
- `NewRidgeFinancial2/test_softdent_gui_export.py`
- `NewRidgeFinancial2/test_portal_ops.py`

## Validation

- Unit: tiny-file refuse, retry-then-success, attest-only fallback on GUI fail
- Morning tick: GUI down → completed close with `fallback=attest_only` (not stalled)

## Not done (runner-ups)

- HAL Force Close optical control  
- Formal beamHash desk proof across HAL + optical  
