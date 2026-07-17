# Moonshot AI — What's Next After Shadow Clock Hygiene (CONSULT ONLY)

**Date:** 2026-07-17
**Model:** `kimi-k2.5`
**Key:** OPENROUTER_API_KEY
**Script:** `scripts/run_moonshot_whats_next_after_shadow_clock_hygiene_consult.py`
**Apply:** Operator must say continue / approve before Cursor applies.

## Operator request (verbatim)

> next

---

# Verdict
Execute SoftDent Excel enablement attended ops to unblock collections money-beam, then refresh morning bundle.

## 0. Operator Intent (verbatim)
next

## 1. Recommended NEXT (name, why now, effort, REAL files, validation gate)
**Name:** SoftDent Excel Enablement — ATTENDED OPS  
**Why now:** LIVE AUDIT shows `morningBundle.ok=true` but `failed=["collections"]`; collections Excel path is hard-blocked by `softdentExcelGreyedLive=true` (Output Options radio greyed). This is the sole red laser preventing clean period close. Aging and register money-beams are live ($52,270/$78,399), but collections cannot ingest without Excel output. Shadow clock hygiene (Day 2 of 30) demands we fix known blockers immediately rather than wait for orthogonal data feeds.  
**Effort:** Operator-led configuration (1–2 hours with Carestream/IT); zero code unless Excel becomes clickable and parsing fails.  
**REAL files:**  
- Runbook: `NewRidgeFinancial2/docs/runbooks/softdent_excel_enablement_nr2.md`  
- SoftDent executable on operator workstation (Carestream client)  
- Target drop: `C:\SoftDentReportExports\` (existing root confirmed live)  
**Validation gate:**  
1. Operator confirms Excel radio is clickable in SoftDent Output Options (Aging, Collections, Register).  
2. Operator exports Collections report to Excel (not Print/Preview) without error.  
3. Execute `morning_bundle_attended --yes --refresh-close` → `failed=[]` (collections resolved).  
4. HAL desk shows collections money-beam green with dollars matching `claims.totalOutstanding` ($52,270).  

## 2. Ordered backlog AFTER #1 (2–4)
2. **ERA first-drop ingest** — await payer 835 file drop into `C:\Users\mreno\newridgefamilyfinancial\app_data\nr2\office\era_inbox\drop` (real `.835`, not README placeholder), then POST `/api/apex/hal/era-inbox/ingest` with mutation auth; validate remittance dollars against claims.  
3. **Trellis withBenefits validation** — await ~2026-07-20 1AM/2AM scrape, verify `chipStatus` moves from "awaiting" to "ok" with benefits payload; validate coverage against SoftDent patient records.  
4. **Shadow Day 30 attestation prep** — draft cutover documentation and attestation template (no execution) as shadow eligibility approaches; maintain `forceCloseAvailable=false`.

## 3. Why this beats the other candidates now
- **ERA drop (#2)** is blocked on external payer; inbox shows `realFileCount=0` (only README placeholder). Waiting is indeterminate and does not fix the collections failure polluting shadow metrics.  
- **WAIT (#3)** for Trellis leaves the period close dirty for 3+ days; shadow clock hygiene requires fixing the known Excel blocker now, not waiting for an orthogonal eligibility scrape.  
- **No other LIVE AUDIT gap** justifies code work; import lasers are green (`blockingCount: 0`), UI polish is closed, and shadow clock visibility is already applied (91a7b9e).

## 4. What NOT to redo
- Do **not** re-implement shadow clock visibility (Day X of 30 already live).  
- Do **not** flip `forceCloseAvailable` to true (shadow eligibility is 28 days away).  
- Do **not** invent ClearCoverage `withBenefits` data before ~2026-07-20 scrape.  
- Do **not** interact with SoftDent GUI until Excel is clickable (avoid print risk).  
- Do **not** treat empty ERA inbox as $0 or invent remittance.

## 5. Acceptance criteria
- [ ] Operator confirms Excel radio is no longer greyed in SoftDent Output Options (Aging, Collections, Register).  
- [ ] Operator exports Collections to Excel (not Print/Preview) without error.  
- [ ] `morning_bundle_attended --yes --refresh-close` executes with `failed=[]` (collections resolved).  
- [ ] Collections money-beam ingests real dollars matching `claims.totalOutstanding` ($52,270).  
- [ ] HAL desk shows green chip for collections; `periodClose.status` remains completed with `forceCloseAvailable=false`.

## 6. Executive Summary (5 bullets)
- Shadow Day 2 of 30 hygiene is live; `forceCloseAvailable` correctly false; 28 days remain until eligibility.  
- Only blocker is collections Excel export (greyed radio); aging/register beams are live and honest.  
- Attended ops required to enable SoftDent Excel; no code alternative exists for Carestream licensing/UI lock.  
- Post-enablement, automated morning bundle will close the period cleanly and unblock collections money-beam.  
- ERA and Trellis remain queued behind external dependencies (payer files, nightly scrape); do not invent data.

## 7. Approval Checklist
- [ ] Operator acknowledges SoftDent Excel enablement runbook and schedules Carestream/IT window.  
- [ ] Confirm no 835 files are expected before 2026-07-20 (payer schedule).  
- [ ] Confirm Trellis wait is acceptable until ~2026-07-20 1AM/2AM.  
- [ ] Shadow clock metrics accepted as-is (Day 2 of 30); no forced close.  
- [ ] Read-only SoftDent constraint acknowledged (no write-back to SoftDent; Preview-only until Excel enabled).
