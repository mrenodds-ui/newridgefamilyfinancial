# Ops — Collections Output Options (Excel greyed → Print Preview)

**Date:** 2026-07-17  
**Lane:** Track B leftover (collections in `morningBundle.failed[]`)  
**SoftDent:** signed on · Output Options probed live

## Verdict

Collection Summary **Excel radio is greyed** (`IsWindowEnabled=False`). Automation must use **Print Preview only** — never Printer, never File. No collections `.xls` money-beam ingest while SoftDent keeps Excel disabled on that report.

Live probe (collections Output Options):

| Control | Enabled | Checked |
|---------|---------|---------|
| Printer | yes | **yes (default)** |
| Print Preview | yes | no |
| File | yes | no |
| Excel | **no** | no |

Aging Output Options on the same session also showed Excel greyed (SoftDent-side enablement — not an NR2 invent). Prior Excel drops under `C:\SoftDentReportExports` and `periodClose.morningBundle.ok=true` (aging+register) remain the money-beam truth until SoftDent Excel is clickable again.

## Code harden (`softdent_gui_export.py`)

1. **EnumChildWindows** radio scan when 64-bit pywinauto fails on 32-bit SoftDent.
2. Detect **Excel enabled=False** → raise `SoftDentExcelDisabledError` → Print Preview fallback (existing `hal_brain_tools.softdent_export` path).
3. **Refuse Enter** unless Printer is known OFF and Excel/Preview is known ON.
4. Removed blind HOME/DOWN/SPACE walk (was selecting Printer first).

## Attested results (2026-07-17)

| Report | Result |
|--------|--------|
| collections | `ok=true` · `outputMode=print_preview` · `excelDisabled=true` · `moneyBeamIngest=false` |
| register (re-probe in full bundle) | Preview OK · Excel greyed this session |
| aging (re-probe in full bundle) | Excel greyed → Preview failed open (Date Wizard) · **did not overwrite** prior good `morningBundle` |

`periodClose.morningBundle` after cleanup: still **`ok=true`**, `failed=["collections"]`, prior Excel paths for aging+register intact. Money beams live SoftDent `$52,270` / QB `$78,399`.

## Operator next (SoftDent Excel enablement)

Follow `docs/runbooks/softdent_excel_enablement_nr2.md` — make Excel clickable on Output Options (Carestream/office IT). Then re-run:

```text
.\.venv\Scripts\python.exe scripts/morning_bundle_attended.py --yes --refresh-close
```

Until then: collections stays best-effort Preview / honest `failed:["collections"]` for Excel ingest · empty ≠ `$0`.
