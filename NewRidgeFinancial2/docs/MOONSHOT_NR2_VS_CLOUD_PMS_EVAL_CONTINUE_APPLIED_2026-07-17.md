# NR2 vs Cloud PMS Evaluation — Continue APPLIED (Excel hold + ERA P0-C)

**Date:** 2026-07-17  
**Consult:** `MOONSHOT_NR2_VS_CLOUD_DENTAL_PMS_EVALUATION_2026-07-17.md`  
**Operator:** continue

## What was done

| P0 item | Result |
|---------|--------|
| SoftDent Excel enablement (P0-A) | **Still blocked** — re-probe Account Aging Output Options: Excel `enabled=false`. Cancelled (never Printer). No morning bundle. |
| Collections “Cursor code fix” (P0-B) | **Skipped** — root cause is SoftDent Excel grey, not NR2 invent/OCR. |
| ERA 835 drop process (P0-C) | **Applied docs** — hardened `docs/runbooks/era_835_inbox_drop_nr2.md` (top-payer setup, realFileCount gate, SoftDent Excel parallel note). |
| SoftDent Excel Grey Hold Protocol | **Added** — `docs/runbooks/softdent_excel_grey_hold_protocol_nr2.md` |

## Live checks

- SoftDent signed on; Excel still grey (intentional pull block).
- Prior money beams / partial morningBundle left intact.
- ERA inbox still awaits a **real** payer `.835` (README placeholder ≠ remittance).

## Operator next

1. Carestream: un-grey SoftDent Excel → say **Excel is clickable — run morning bundle**  
2. Drop a real ERA `.835` into `app_data/nr2/office/era_inbox/drop` → ingest per ERA runbook  
3. Wait Trellis withBenefits ~2026-07-20 · continue shadow Day X of 30  

## What was NOT done

- SoftDent write-back · Preview money invent · synthetic 835 as live remittance · forceClose flip · cloud PMS replacement
