# Moonshot AI — What's Next (Preview Optical / Excel Money) (CONSULT ONLY)

**Date:** 2026-07-17
**Model:** `kimi-k2.5`
**Key:** OPENROUTER_API_KEY
**Script:** `scripts/run_moonshot_whats_next_after_preview_optical_excel_money_consult.py`
**Apply:** Operator must say continue / approve before Cursor applies.

## Operator request (verbatim)

> next

---

# Verdict
WAIT / ATTENDED — SoftDent Excel Carestream enablement is the only honest path; document the hold state and preserve existing money-beam truth while blocking GUI automation attempts.

## 0. Operator Intent (verbatim)
next

## 1. Recommended NEXT (name, why now, effort, REAL files, validation gate)
**WAIT / ATTENDED — SoftDent Excel Carestream Enablement Protocol**
- **Why now:** Collections morning bundle refresh is actively blocked (Excel greyed 2026-07-17). This is the sole blocker preventing update of collections truth while aging+register remain valid. ERA inbox contains zero real 835 files (README.txt placeholder only). Trellis withBenefits is externally time-gated to ~2026-07-20. No code can un-grey SoftDent exports.
- **Effort:** ATTENDED OPS ONLY (Carestream support ticket + operator GUI action). Cursor scope is documentation of the blocked state, preservation of prior money-beam truth, and protocol for post-enablement validation.
- **REAL files:** 
  - `C:\SoftDentReportExports\` (existing, stale exports from prior clickable-Excel state)
  - `morning_bundle` partial (2/3 OK: aging+register OK, collections FAILED)
  - Live claims dataset (150 claims, $52,270 outstanding — current truth source)
- **Validation gate:** Carestream confirms Excel Output Options un-greyed → Operator manual export to `C:\SoftDentReportExports\` → NR2 ingest detects new collections file → `morningBundle.ok` collections flips true → Collections money-beam refreshes from live extract (not Preview optical).

## 2. Ordered backlog AFTER #1 (2–4)
2) **ERA real .835 ingest** — awaiting real remittance files in `C:\Users\mreno\newridgefamilyfinancial\app_data\nr2\office\era_inbox\drop\` (currently `README.txt` placeholder only; empty ≠ $0). Ingest wired but idle.
3) **WAIT — Trellis withBenefits** — hold until ~2026-07-20 1AM/2AM for ClearCoverage nightly scrape completion. Chip currently "Status-only."
4) **Claims-to-QB Gap Analysis** — code reconciliation dashboard for $26,129 delta ($78,399 QuickBooks vs $52,270 SoftDent) using live 150-claim dataset; secondary to unblocking primary extract path.

## 3. Why this beats the other candidates now
- **ERA ingest impossible:** Live audit confirms `realFileCount: 0`, `placeholderCount: 1`. No 835 remittance exists to ingest; "empty_not_zero" honesty prevents inventing dollars.
- **Trellis externally gated:** withBenefits dependency is ClearCoverage scrape schedule (~2026-07-20); Cursor cannot accelerate third-party data availability.
- **Claims gap analysis valuable but secondary:** While the $26K QB/SoftDent delta is real, it is diagnostic only; it does not unblock the critical path collections refresh required for period-close hygiene.
- **SoftDent Excel is the root blocker:** All other money-beam paths (Aging, Register) remain functional from stale-but-valid extracts. Only Collections requires the attended Excel enablement to resume live extracts.

## 4. What NOT to redo
- Do **not** code SoftDent GUI automation or "un-grey" logic (Excel block is intentional Carestream-side; Cursor cannot override).
- Do **not** recommend Print Preview as money-beam substitute (optical fallback only; violates HARD TRUTH against inventing Preview dollars).
- Do **not** flip `forceCloseAvailable` to true (period close integrity requires `false`; supervised pilot Day 2/30).
- Do **not** invent ERA 835 files, withBenefits data, or SoftDent export paths.
- Do **not** re-document UI polish (status: CLOSED).

## 5. Acceptance criteria
- [ ] Carestream/operator support ticket opened for Excel Output Options enablement on Aging + Collections reports.
- [ ] Document signed: "SoftDent Excel Grey State Protocol" explicitly preserving prior `morningBundle.ok` collections truth and warning against Preview-as-money.
- [ ] Validation path confirmed: `C:\SoftDentReportExports\` writable and monitored by NR2 ingest service.
- [ ] Post-enablement test: Collections report exports successfully → NR2 ingest → `morningBundle.ok` all 3 reports true.
- [ ] Zero Cursor commits attempting to "fix" SoftDent grey state via code or registry hacks.

## 6. Executive Summary (5 bullets)
- SoftDent Excel Output Options remain intentionally grey (confirmed live 2026-07-17), blocking collections report extract.
- Money-beam truth preserved from prior successful extracts ($52,270 SoftDent claims; $78,399 QB) — stale but valid; empty ERA inbox confirms no remittance to reconcile.
- Critical path is ATTENDED OPS ONLY: Carestream must enable Excel exports; Cursor documents hold state and preserves data integrity protocols.
- Pilot shadow clock continues (Day 2 of 30); no force-close available or required.
- All alternative ingest paths (ERA 835, Trellis withBenefits) are resource-constrained (empty or time-gated), making SoftDent Excel enablement the sole unblockable priority.

## 7. Approval Checklist
- [ ] Operator acknowledges: No code solution exists for grey Excel; resolution requires Carestream/operator attended action.
- [ ] Operator acknowledges: Print Preview is optical fallback, not a money-beam source for OCR/dollars.
- [ ] Operator confirms: ERA inbox `C:\...\era_inbox\drop\` contains no hidden 835 files (only `README.txt`).
- [ ] Pilot integrity confirmed: `forceCloseAvailable` remains `false`; shadow clock continues.
- [ ] PHI compliance verified: Claims data references use initials+hash; no full names or SSNs in logs.
