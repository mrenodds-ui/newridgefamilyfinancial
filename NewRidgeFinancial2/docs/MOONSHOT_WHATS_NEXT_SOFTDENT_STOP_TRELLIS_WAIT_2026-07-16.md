# Moonshot AI — What's Next (SoftDent STOP + Trellis Wait) (CONSULT ONLY)

**Date:** 2026-07-16
**Model:** `kimi-k2.5`
**Key:** OPENROUTER_API_KEY
**Script:** `scripts/run_moonshot_whats_next_softdent_stop_trellis_wait_consult.py`
**Apply:** Operator must say continue / approve before Cursor applies.

## Operator request (verbatim)

> next

---

# Verdict
Implement **Claims workflow honesty** (age buckets, payer backfill, ERA inbox gap UX, and paid-suppress staff toggle) — it is the only high-value package unblocked by the SoftDent STOP and Trellis wait, with live data (150 claims, $52.7k outstanding) validating immediate utility.

## 0. Operator Intent (verbatim)
next

## 1. Recommended NEXT (name, why now, effort, REAL files, validation gate)
**Name:** Claims Workflow Honesty (Payer Backfill + ERA Gap UX + Paid-Suppress Toggle)

**Why now:**  
- Live audit shows **150 claims** ($52,270 outstanding) with **74 generic vs 76 named payers** (backfill opportunity).  
- ERA inbox is **staged** (1 file: `README.txt`) with `gapCode: ERA835_PENDING` — infrastructure exists but needs honesty UX ("Empty ≠ $0").  
- `paidSuppress` shows **4 staff-hidden claims** vs **154 candidate open statuses** (UX discrepancy to surface).  
- Requires **zero SoftDent GUI** (read-only file drops) and **zero Trellis withBenefits** (eligibility frozen until 2026-07-20).  

**Effort:** 1–2 sessions (UI polish on existing HAL endpoints; no new scrapers).

**REAL files:**  
- Claims data: `/api/apex/hal/claims` (63653 bytes, live)  
- ERA inbox: `C:\Users\mreno\newridgefamilyfinancial\app_data\nr2\office\era_inbox\drop\README.txt`  
- Payer mappings: `app_data/nr2/payer_backfill.json` (to be created from generic→named stats)  
- Suppress config: `paidSuppress` block in live audit (staffDropped: 4)

**Validation gate:**  
- Claims dashboard renders 150 rows with age buckets (0-30, 31-60, 61-90, 90+).  
- Payer column shows named insurers where mapped, generic codes where unmapped.  
- ERA inbox chip reads "1 file(s) in inbox — Empty ≠ $0" (honesty).  
- Paid-suppress panel toggles "Staff Hidden (4)" without 503 errors.

## 2. Ordered backlog AFTER #1 (2–4)
2. **HAL desk smoke / this-patient** — Fix HTTP 503 on `deskSmoke` endpoint, then implement patient-specific claim view (read-only, no SoftDent write-back).  
3. **Pilot / shadow clock documentation** — Document `periodClose.morningBundle` null state and `forceClose: false` logic; prepare runbook for when SoftDent STOP lifts.  
4. **WAIT — SoftDent resume & Trellis benefits** — Blocked until operator lifts `.cursor/rules/softdent-agent-stop-now.mdc` and 2026-07-20 2AM Trellis scrape populates `withBenefits > 0`.

## 3. Why this beats the other candidates now
- **Beats #4 (WAIT):** Live claims data exists NOW; we do not need SoftDent GUI or Trellis benefits to render honest aging and payer gaps.  
- **Beats #2 (HAL desk smoke):** Currently returns HTTP 503; fixing it is troubleshooting, not product work. Claims endpoint is already live (63653 bytes).  
- **Beats #3 (Pilot docs):** Documentation-only is lower priority than fixing the $52k outstanding claims visibility and ERA gap honesty.

## 4. What NOT to redo
- **Do not** build SoftDent `morning_bundle_attended.py` or Excel report pulls (STOP active).  
- **Do not** invent `withBenefits` or fake Trellis eligibility data (wait for 2026-07-20 scrape).  
- **Do not** flip `forceCloseAvailable` to `true` (morningBundle is null; optical gate must stay RED).  
- **Do not** add React components or third-party chat embeds (vanilla JS/HTML only per constraints).

## 5. Acceptance criteria
- [ ] Claims UI loads 150 claims without 503/404.  
- [ ] Age buckets calculate correctly from `txnDateMax: 2026-07-12` baseline.  
- [ ] Payer backfill mapping reduces "generic" count from 74 toward 0 as mappings are added.  
- [ ] ERA inbox displays `chipLabel: "1 file(s) in inbox"` with `honesty: "empty_not_zero"` warning.  
- [ ] Paid-suppress toggle exposes/hides the 4 staff-dropped claims without affecting totals (empty ≠ $0).  
- [ ] No mutations attempt SoftDent write-back (read-only enforced).

## 6. Executive Summary (5 bullets)
- **SoftDent STOP blocks GUI automation**, but file-based claims and ERA ingestion remain available (read-only).  
- **Live audit validates 150 claims** ($52,270 outstanding) with immediate payer-name gaps and aging transparency needs.  
- **Trellis eligibility is frozen** (status-only until 2026-07-20 2AM); no withBenefits work can proceed honestly.  
- **ERA inbox is staged** (README.txt placeholder) and ready for 835 drop UX; gap honesty prevents "$0 assumption" bugs.  
- **Claims workflow is the only unblocked high-value work** that respects both the SoftDent STOP and Trellis wait constraints.

## 7. Approval Checklist
- [ ] Operator confirms no SoftDent GUI automation will be generated in this package.  
- [ ] Operator confirms Trellis `withBenefits` will remain 0 (no invented data).  
- [ ] Operator verifies `forceClose` stays `false` (no optical gate flip).  
- [ ] Operator accepts that ERA inbox currently contains only README.txt (empty ≠ $0).  
- [ ] Operator approves read-only access to `C:\SoftDentReportExports\` for claims aging data only.
