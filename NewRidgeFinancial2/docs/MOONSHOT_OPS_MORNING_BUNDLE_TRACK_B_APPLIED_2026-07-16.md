# Ops Track B — Morning Bundle Resuscitation APPLIED

**Date:** 2026-07-16 (evening)  
**Plan:** Next after Viewport Package 4 → **Track B**  
**Consults:** `MOONSHOT_WHATS_NEXT_AFTER_POLISH_P10_2026-07-16.md`, `MOONSHOT_OPS_MORNING_BUNDLE_RESUSCITATION_2026-07-16.md`

## Result

| Gate | Status |
|------|--------|
| NR2 live on `:8765` (no WinError 10061) | **PASS** |
| `money-beams` / AR / claims / excel-probe HTTP 200 | **PASS** |
| SoftDent attended aging + register Excel → `C:\SoftDentReportExports` | **PASS** |
| Collections Excel | **FAIL** (Output Options radio scan / Printer latch under 64-bit pywinauto) — best-effort |
| `periodClose.morningBundle.ok` | **PASS** (`okCount=2`, failed=`[collections]`) |
| Optical **BUNDLE** gate | **GREEN** |
| `forceCloseAvailable` remains laser-gated (false while lasers green) | **PASS** |
| empty ≠ $0 | **PASS** |

## What was broken / fixed

1. **Wrong Python:** Hermes venv lacked `pywinauto` — use repo `.venv\Scripts\python.exe`.  
2. **Aging drop miss:** Select File Name OK without waiting / Excel-on-temp fallback — hardened in `softdent_gui_export.py` (poll, overwrite confirm, SDWIN SaveCopyAs).  
3. **BUNDLE stayed RED after successful export:** `morning_bundle_attended --refresh-close` attested without persisting `export` onto the close log; `merge_period_close_into_readiness` omitted `morningBundle`.  
   - `run_period_close(..., export_result=…)`  
   - attended script passes export into refresh-close  
   - readiness overlay includes `periodClose.morningBundle`

## Evidence

- Attended log: `.local_logs/morning_bundle_attended_2026-07-17.json` (`ok=true`, `agingOk=true`)  
- Paths: `C:\SoftDentReportExports\account_aging.xls`, `register_for_period_2026-06-16_2026-07-16.xls`  
- Live: `GET /api/import-readiness` → `periodClose.morningBundle.ok=true` → BUNDLE GREEN  
- SoftDent signed on via `ensure_softdent_ready_for_gui_export` (COMPUTE)

## Remaining (honest)

- Collections still RED in `failed[]` until Output Options Excel selection is reliable on 64-bit Python (or 32-bit SoftDent automation env).  
- Prefer `.\.venv\Scripts\python.exe scripts/morning_bundle_attended.py --yes --refresh-close` for future runs (not Hermes `python`).  
- Trellis AM `passed=false` (awaiting nightly ClearCoverage) — separate backlog item.
