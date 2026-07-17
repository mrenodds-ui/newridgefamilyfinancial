# Moonshot AI — What's Next After SoftDent Grey-Excel Universal Pull Block (CONSULT ONLY)

**Date:** 2026-07-17
**Model:** `kimi-k2.5`
**Key:** OPENROUTER_API_KEY
**Script:** `scripts/run_moonshot_whats_next_after_softdent_grey_excel_universal_consult.py`
**Apply:** Operator must say continue / approve before Cursor applies.

## Operator request (verbatim)

> next

---

# Verdict
SoftDent Excel enablement ATTENDED OPS is the mandatory next step to unblock the failed collections component and restore extractable data flows.

## 0. Operator Intent (verbatim)
next

## 1. Recommended NEXT (name, why now, effort, REAL files, validation gate)
**Name:** SoftDent Excel Enablement ATTENDED OPS  
**Why now:** Morning bundle Track B reports collections as failed because SoftDent Output Options Excel is greyed across all reports (universal block). Current money-beams ($52,270 SoftDent) rely on prior aging+register extracts when Excel was clickable; collections refresh is blocked. Preview is optical-only and must never feed money-beams. Without attended intervention, the financial close remains incomplete and stale.  
**Effort:** Attended operator action (Carestream/SoftDent support contact); zero code changes unless Excel becomes clickable.  
**REAL files:**  
- `NewRidgeFinancial2/docs/runbooks/softdent_excel_enablement_nr2.md` (runbook)  
- `NewRidgeFinancial2/docs/MOONSHOT_OPS_SOFTDENT_EXCEL_ENABLEMENT_BLOCKED_2026-07-17.md` (blocker log)  
**Validation gate:**  
1. Carestream/operator confirms Excel Output Option is clickable (not grey) on Collection Summary and Account Aging.  
2. Operator executes `morning_bundle_attended --yes --refresh-close` and collections status flips from `failed` to `ok`.  
3. Fresh Excel extracts ingest without overwriting prior money-beam truth with Preview data.

## 2. Ordered backlog AFTER #1 (2–4)
1. **ERA real first remittance .835 ingest** — once payer drops real 835 file into `C:\Users\mreno\newridgefamilyfinancial\app_data\nr2\office\era_inbox\drop` (currently only `README.txt` placeholder; empty ≠ $0).  
2. **Trellis withBenefits verification** — await ~2026-07-20 1AM/2AM ClearCoverage nightly scrape; validate AM proof chip transitions from `awaiting` to `passed`.  
3. **Pilot shadow Day 30 readiness** — continue shadow monitoring (Day 2 of 30 elapsed); prepare supervised phase attestation materials (blocked until minShadowDays satisfied).

## 3. Why this beats the other candidates now
- **Beats ERA ingest (Candidate 2):** ERA inbox is staged but empty of real 835 files (`realFileCount: 0`, `placeholderCount: 1`). Ingesting now would process only `README.txt`; no remittance dollars exist to extract.  
- **Beats WAIT Trellis (Candidate 3):** Trellis is explicitly time-gated until 2026-07-20. Waiting does not resolve the active failure state (collections blocked) and leaves money-beams stale.  
- **Beats "Something else" (Candidate 4):** Any other implementation would be scope creep while the primary financial data extraction pipeline is severed. SoftDent Excel grey is the root cause of the current operational impairment; fixing it unblocks the critical path.

## 4. What NOT to redo
- Do **not** reapply viewport P1–4, Hub, morning bundle Track B logic, collections excel-greyed harden, claims honesty, HAL desk smoke, pilot shadow docs, or SoftDent grey-Excel docs (already applied through commit `8084d2b`).  
- Do **not** attempt SoftDent GUI Excel export while Excel remains greyed (Preview optical-only; never Printer/File).  
- Do **not** invent withBenefits or remittance dollars from empty inboxes.  
- Do **not** flip `forceCloseAvailable` to `true` (shadow Day 2 of 30; 28 days remaining).  
- Do **not** reskin UI or add React/third-party chat embeds.

## 5. Acceptance criteria
- [ ] Carestream/SoftDent support restores Excel Output Option (no longer greyed) on Collection Summary and Account Aging reports.  
- [ ] Operator generates fresh Excel extracts (`.xlsx`) from SoftDent, confirming the gate is open.  
- [ ] `morning_bundle_attended --yes --refresh-close` executes successfully with collections status `ok`.  
- [ ] Money-beams update with refreshed collections data without overwriting prior truth with Preview optical data.  
- [ ] Blocker doc updated with resolution timestamp and Carestream ticket reference.

## 6. Executive Summary (5 bullets)
- SoftDent Excel greyed universally blocks all extractable report pulls, causing collections to fail in the morning bundle.  
- Money-beams currently rely on stale prior extracts; Preview optical-only cannot be used for financial data.  
- Carestream/operator attended intervention is required to restore Excel Output Option—no code workaround exists.  
- ERA and Trellis pipelines remain blocked by external dependencies (absence of 835 files, pending 2026-07-20 scrape).  
- System maintains read-only honesty: empty ERA inbox ≠ $0, Preview optical-only ≠ extractable data, forceClose remains false.

## 7. Approval Checklist
- [ ] Operator acknowledges Excel un-grey is ATTENDED OPS (Carestream/SoftDent support), not a Cursor code fix.  
- [ ] Carestream support ticket opened or callback scheduled with reference to runbook `softdent_excel_enablement_nr2.md`.  
- [ ] Blocker doc `MOONSHOT_OPS_SOFTDENT_EXCEL_ENABLEMENT_BLOCKED_2026-07-17.md` updated with current timestamp and operator notes.  
- [ ] No attempt to use Print Preview as a data source for money-beams.  
- [ ] `forceCloseAvailable` remains `false` (pilot shadow Day 2 of 30).  
- [ ] ERA inbox integrity preserved: `README.txt` remains placeholder only; no synthetic 835 files created.
