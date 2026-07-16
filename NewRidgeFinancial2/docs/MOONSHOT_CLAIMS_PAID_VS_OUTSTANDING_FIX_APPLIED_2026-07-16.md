# NR2-12150 Claims Paid vs Outstanding Fix — APPLIED

**Date:** 2026-07-16  
**Consult:** `MOONSHOT_CLAIMS_PAID_VS_OUTSTANDING_FIX_2026-07-16.md`  
**Operator:** proceed  
**Package:** ERA–Aging hybrid suppression + staff Force Close (local hide)

## Shipped

| Piece | Path |
|-------|------|
| Suppress cascade module | `nr2_claims_paid_suppress.py` |
| Claims API filter + `paidSuppress` meta | `nr2_softdent_daily.py` (`_filter_unpaid_claim_rows`, `claims_outstanding`) |
| ERA paid keys helper | `nr2_era_inbox.paid_claim_keys_from_era` |
| Staff action `staff_verified_paid` | `hal_employee_workflows.py` |
| Force-close API | `POST /api/softdent/claims-force-close` |
| Claims page UI | `site/nr2-optical-page-claims.js` / `.html` |
| Unit tests | `test_nr2_claims_paid_suppress.py` |
| Build stamp | `nr2-12150-claims-paid-suppress` |

## Truth order (paid hide)

1. **TXN** — SoftDent Trans-for-a-Period insurance pay (`2`) / write-off  
2. **ERA** — explicit `paid > 0` in 835 segments only (empty ≠ `$0`)  
3. **Claims Aging Excel** — only when a non-empty export is present; absent from pending list ⇒ hide  
4. **Staff verified paid** — local JSONL hide under `app_data/nr2/ops/claims_staff_verified_paid.jsonl` (no SoftDent write-back)

Missing ERA or Claims Aging **does not** invent paid.

## Operator pulls

1. SoftDent → Reports → Accounting → **Trans for a Period** → **Excel** (through today)  
2. SoftDent → Reports → Insurance → **Claims Aging** (or Outstanding Claims by Patient) → **Excel**  
   Save as `C:\SoftDentReportExports\claims_aging_YYYYMMDD.xls`  
3. Optional: drop ERA `.835` into the ERA inbox for automatic paid keys  
4. For known-paid leftovers: Claims dossier → **Force close (staff verified paid)**

## Validation

```text
python -m unittest test_nr2_claims_paid_suppress test_softdent_operational_pipeline -v
GET /api/softdent/claims-outstanding?limit=5  → paidSuppress meta present
```

## Constraints honored

- SoftDent READ-ONLY (no write-back)  
- empty ≠ `$0`  
- Output Options Excel or Print Preview only for SoftDent pulls (never Printer/File)
