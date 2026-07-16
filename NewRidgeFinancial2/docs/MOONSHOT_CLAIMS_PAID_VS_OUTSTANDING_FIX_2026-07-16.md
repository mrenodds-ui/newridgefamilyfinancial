# Moonshot AI — Claims Paid vs Outstanding Fix (CONSULT ONLY)

**Date:** 2026-07-16
**Model:** `kimi-k2.5`
**Key:** OPENROUTER_API_KEY
**Script:** `scripts/run_moonshot_claims_paid_vs_outstanding_consult.py`
**Apply:** Operator must say continue / approve before Cursor applies.

## Operator request (verbatim)

> ask moonshot ai how to fix claims that have already been paid that should not be on the claims list in claims page from the claims that are still out and waiting to be paid how to fix. report

---

# Verdict
The Claims page lists paid claims because the sole suppression logic—matching against the lagging “Transactions for a Period” Excel window—misses payments outside the 2026-01-02 → 2026-07-12 date range and fails to settle legacy January 2026 TXN rows that staff know are closed, requiring an ERA‑Aging hybrid filter and a manual Force‑Close gate to achieve zero false‑outstanding inventory.

## 0. Operator Intent (verbatim)
“ask moonshot ai how to fix claims that have already been paid that should not be on the claims list in claims page from the claims that are still out and waiting to be paid how to fix.”

## 1. Root cause diagnosis (what makes paid claims still appear — cite LIVE AUDIT)
**Primary failure:** The pipeline relies exclusively on `softdent_operational_pipeline.claim_is_unpaid_on_txn` (the TXN filter) to drop paid rows.  
- **LIVE AUDIT evidence:** `txnDateMax` = 2026‑07‑12, while `todayLocalHint` = 2026‑07‑16. Insurance payments posted between 2026‑07‑13 and today physically cannot appear in the TXN extract, so recently paid claims survive the filter and render as “Pending Review.”  
- **Legacy orphan rows:** The audit lists eight January 2026 TXN claims (e.g., `TXN-20260107-67201`) with `txnSettlementMatch: false`. These rows carry `status: "Pending Review"` in `sd_claims` yet have no counterpart in the TXN settlement set, causing the code to keep them as outstanding despite staff knowledge that they are paid.  
- **Single‑source risk:** `note` field confirms: *“TXN filter is the only paid suppressor today.”* When the TXN file lags or lacks a match key, the system has no fallback truth to hide the claim.

## 2. Recommended FIX package (name, why now, effort, REAL files under NewRidgeFinancial2/, operator SoftDent pulls if needed, validation gate)
**Package name:** NR2‑12150 “ERA‑Aging Hybrid Suppression + Force‑Close Gate”  
**Why now:** The TXN lag (4 days behind) and the 60‑day‑old orphan January rows are creating a “deskProof: RED” mismatch; without secondary truth, the outstanding list is unreliable for collections work.  
**Effort:** 2 sprints (1 for ERA bridge, 1 for Aging ingestion + UI gate).  
**REAL files to touch:**
- `NewRidgeFinancial2/nr2_era_inbox.py` – consume already‑staged ERA 835 data to emit a `paid_claim_ids` list.  
- `NewRidgeFinancial2/softdent_operational_pipeline.py` – extend `claim_is_unpaid_on_txn` with `claim_is_unpaid_per_era()`; return `False` (paid) if claim ID or patient‑date‑amount tuple matches an ERA payment.  
- `NewRidgeFinancial2/softdent_outstanding_claims_bridge.py` – add `claim_is_unpaid_per_aging()` lookup against the SoftDent Claims Aging Excel (see operator pull below).  
- `NewRidgeFinancial2/nr2_softdent_daily.py` – in `claims_outstanding`, apply filters in cascade: TXN → ERA → Aging; survivors flow to the optical page.  
- `NewRidgeFinancial2/site/nr2-optical-page-claims.js` – add “Force Close (Staff Verified Paid)” button gated by `nr2-12073-excel-gate-all-next` approval workflow; posts to a new `staff_verified_paid` queue rather than writing to SoftDent.

**Operator SoftDent pulls required:**
1. **ERA 835** – already staged per `eraInboxStatus.ok: true`; no new pull.  
2. **Claims Aging Report** – SoftDent → Reports → Insurance → Claims Aging → **Output Options → Excel** (never Printer, never File). Save to `C:\SoftDentReportExports\claims_aging_YYYYMMDD.xls`. This provides the ground‑truth “Insurance Pending” list; any claim *not* appearing in the Aging report as outstanding is treated as paid/closed.

**Validation gate:**  
- **Morning Bundle Excel Enablement Gate** (`nr2-12073`): Operator must approve the attended morning bundle after verifying that the new ERA + Aging columns appear in the preview.  
- **Laser‑gated Force Close**: Staff may hide a claim only after checking both ERA and Aging columns; the action is logged, not synced back to SoftDent (respecting READ‑ONLY constraint).

## 3. How paid vs still‑waiting should be decided (truth order / rules — empty ≠ $0; never invent paid)
1. **TXN Settlement (insurance pay code family 2)** – If the claim row matches a payment in the TXN XLS, it is **paid** (existing logic).  
2. **ERA 835 (nr2_era_inbox.py)** – If the claim appears in the ERA inbox with a paid or zero‑balance indicator, it is **paid**. Empty ERA amount ≠ $0; we only mark paid when the ERA explicitly states payment or adjustment.  
3. **SoftDent Claims Aging Excel** – If the claim is *absent* from the Aging report’s “Insurance Pending” list, it is **paid** (SoftDent has removed it from the outstanding queue).  
4. **Staff Force‑Close** – If a staff member confirms via the UI that the claim is paid (e.g., check cashed but not yet in ERA), it is **paid**; the claim is suppressed from the page and logged for audit.  
5. **Default** – If none of the above assert payment, the claim remains **still‑waiting** and displays on the Claims page.

*Constraint checks:*  
- Never write status back to SoftDent (READ‑ONLY).  
- Never synthesize a $0 payment; empty cells are treated as “unknown,” not “paid.”

## 4. Ordered backlog AFTER #1 (2–4)
2. **TXN Date Window Auto‑Expander** – Modify `claim_is_unpaid_on_txn` to dynamically set the TXN end date to `todayLocalHint` minus 1 day, eliminating the 4‑day lag; requires no new files, only `softdent_operational_pipeline.py` logic change.  
3. **Payer Name Enrichment** – Replace generic `"Insurance"` labels (seen in 6 of 6 sampled claims) with specific payer names from the ERA or Aging files to improve matching accuracy; touches `softdent_outstanding_claims_bridge.py`.  
4. **Desk Smoke Reconciliation Report** – Build a weekly diff between `claims_outstanding` API output and the Claims Aging Excel to auto‑detect future mismatches before they hit the RED state; new file `NewRidgeFinancial2/nr2_desk_smoke_recon.py`.

## 5. What NOT to do
- **Do not** update `sd_claims` status to “Closed” or “Paid” – SoftDent is READ‑ONLY and write‑back is forbidden.  
- **Do not** assume empty payment fields equal $0; treat missing data as “unverified,” not “paid.”  
- **Do not** use SoftDent Print Preview data as a machine‑readable source; only Excel exports may be parsed.  
- **Do not** auto‑suppress claims based solely on age (e.g., >90 days) without financial evidence from TXN, ERA, or Aging.  
- **Do not** invent synthetic claim IDs or payment amounts to force a match.

## 6. Acceptance criteria (Claims page must show only still‑out)
- [ ] API `GET /api/softdent/claims-outstanding` returns zero claims that SoftDent staff can verify as already paid.  
- [ ] All 154 currently listed claims are re‑audited: each must be either (a) confirmed still‑waiting with ERA/Aging evidence, or (b) suppressed via the new filters or Force‑Close gate.  
- [ ] `deskSmokeLast.status` transitions from `RED` to `GREEN` with `deskProof: MATCH`.  
- [ ] Claims page displays an “Evidence” column showing which truth source (TXN, ERA, Aging, or Staff) determined the outstanding status.  
- [ ] No claim older than the TXN window max (2026‑07‑12) remains on the list unless it is genuinely awaiting payment per ERA or Aging.

## 7. Executive Summary (5 bullets)
- **Problem:** The Claims page shows 154 “Pending Review” rows, including staff‑known paid claims, because the pipeline relies on a single, lagging TXN Excel file (last date 2026‑07‑12) that cannot see recent payments or settle old orphan rows.  
- **Impact:** Collections staff waste time chasing money already received, and the “deskProof” status is RED, blocking financial close.  
- **Solution:** Deploy a three‑layer suppression engine—TXN (existing) + ERA inbox (staged) + SoftDent Claims Aging Excel (operator pull)—plus a laser‑gated Force Close button for manual verification.  
- **Constraint Compliance:** Zero writes to SoftDent; all payment truths derive from Excel exports or ERA 835; empty fields are never interpreted as $0.  
- **Outcome:** A Claims page that accurately reflects only insurance dollars still in flight, validated by dual financial sources and staff attestation.

## 8. Approval Checklist
- [ ] Engineering lead reviews `nr2_era_inbox.py` schema to ensure ERA claim keys map to `TXN-…` and `DS-…` IDs.  
- [ ] Office manager confirms ability to export Claims Aging to Excel (Output Options → Excel) on demand.  
- [ ] Compliance sign‑off that Force Close audit logs satisfy “no write‑back” policy.  
- [ ] Operator schedules morning bundle with `excelEnablementGate` to test ERA + Aging ingestion in staging.  
- [ ] Desk smoke test executed: compare post‑deploy API list to SoftDent Claims Aging Preview; mismatch count must be zero before prod release.
