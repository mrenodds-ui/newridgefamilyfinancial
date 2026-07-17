# SoftDent Excel Grey — Hold Protocol (NR2)

**Date:** 2026-07-17  
**Source:** `MOONSHOT_NR2_VS_CLOUD_DENTAL_PMS_EVALUATION_2026-07-17.md` P0-A  
**Status:** HOLD active (Excel greyed live on Output Options)

## SoftDent meaning

When **Excel** is grey on SoftDent **Output Options**, SoftDent is **intentionally blocking extractable data pulls**. That gate can apply across **all** SoftDent reports that use Output Options.

| Allowed | Forbidden |
|---------|-----------|
| **Print Preview** — optical / visual read only | Printer |
| Wait for SoftDent/Carestream to re-enable Excel | SoftDent **File** |
| Keep prior Excel money-beam truth | Invent dollars from Preview / OCR |
| | Re-run morning bundle expecting new Excel drops |

## NR2 money path (when Excel is clickable again)

1. SoftDent Output Options → **Excel** → Setup → Select File Name under `C:\SoftDentReportExports`
2. SoftDent may open temp `SDWIN*` in Excel → SaveCopyAs into `C:\SoftDentReportExports`
3. Then:  
   `.\.venv\Scripts\python.exe scripts/morning_bundle_attended.py --yes --refresh-close`

## Hold rules (now)

1. Do **not** SoftDent-GUI spam Output Options OK while Printer is default.
2. Do **not** treat Print Preview as money-beam ingest.
3. Preserve prior `morningBundle` aging+register Excel truth until a fresh Excel extract succeeds.
4. Collections may remain in `failed[]` while Excel is grey — honest, empty ≠ `$0`.
5. `forceCloseAvailable` stays laser-gated false.

## Resume phrase for Cursor

Say: **Excel is clickable — run morning bundle**

## Related

- Runbook: `docs/runbooks/softdent_excel_enablement_nr2.md`
- Blocked probes: `docs/MOONSHOT_OPS_SOFTDENT_EXCEL_ENABLEMENT_BLOCKED_2026-07-17.md`
- Carestream Help: Output Options on every report run — [Running Reports](https://help.carestreamdental.com/rh/web/server/SoftDent/projects_responsive/DE1055_SD_Wkbk/Running_Reports.htm)
