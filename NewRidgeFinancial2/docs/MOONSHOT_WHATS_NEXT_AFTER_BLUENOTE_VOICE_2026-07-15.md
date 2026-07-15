# Moonshot AI — What's Next After BlueNote Voice + Money Honesty Stack (CONSULT ONLY)

**Date:** 2026-07-15
**Model:** `kimi-k2.5`
**Key:** OPENROUTER_API_KEY
**Status:** ok
**Repo root:** `C:\Users\mreno\newridgefamilyfinancial`
**Prior:** `b3e7ed2` short cues · `cec10bc` refresh timeout · money honesty live
**Script:** `scripts/run_moonshot_whats_next_after_bluenote_voice_consult.py`
**Apply:** DO NOT APPLY until operator approves.

## Operator request (verbatim)

> next

---

# Verdict
Close the daily money operations loop by establishing the import-readiness period-close OPS workflow—automating pulls → beam refresh → HAL citation to eliminate the `activeOperation: null` state and ensure the shadow pilot has a trustworthy, repeatable daily financial close.

## 0. Operator Intent (verbatim)
next

## 1. Recommended NEXT (name, why now, effort, REAL files/ops, validation gate)
**Package:** Import-readiness / period close daily OPS loop (pulls → beams → HAL cite)  
**Why now:** Money beams are now honest (`nr2-12023`) and refresh-period is fail-fast, yet the LIVE AUDIT shows `activeOperation: null` and `syncState: idle`. Without a closed operational loop, the 17 connected sources risk staleness the moment manual exports stop. This is an OPS blocker (data truth requires rhythm, not just wiring).  
**Effort:** Medium (3–4 hours)—state machine for daily close, scheduled SoftDent/QB pull consent, HAL summary citation.  
**REAL files/ops:**
- `C:\Users\mreno\newridgefamilyfinancial\NewRidgeFinancial2\nr2_period_close_ops.py` — new orchestrator (PULL → VALIDATE → BEAM → COMMIT)
- `C:\Users\mreno\newridgefamilyfinancial\NewRidgeFinancial2\nr2_hal_gateway.py` — add `period_close_status` tool so HAL can cite "Daily close completed at 08:15; SoftDent $7,714 confirmed"
- `C:\Users\mreno\newridgefamilyfinancial\app_data\nr2\ops\daily_close_log.jsonl` — immutable audit trail of each close
- `C:\Users\mreno\newridgefamilyfinancial\NewRidgeFinancial2\softdent_gui_export.py` — hardened trigger for aging/register pull (consent-gated, no write-back)
- Windows Task Scheduler or `nr2_scheduler.py` trigger at 07:00 local time
**Validation gate:**  
- `activeOperation` transitions `null` → `"daily_close"` → `"completed"` visible in `/api/import-readiness`  
- HAL chat query "Did we close yesterday?" returns deterministic citation from `daily_close_log.jsonl` (not hallucination)  
- Post-close beam hash matches pre-close hash + delta; `moneyGrounded=true` on summary  
- Zero 504 STALLED during automated refresh (honest timeout already shipped)

## 2. Why this beats the other candidates now
- **Candidate 1 (Bind subpage):** Important, but CODE/wiring; the beams are already honest. Without the OPS loop (Candidate 6), bound pages would show stale data tomorrow. Rhythm precedes display.  
- **Candidate 2 (Export hardening):** Included as a sub-task within the OPS loop (aging/register pull); over-rotating on Excel reliability now distracts from closing the end-to-end daily cycle.  
- **Candidate 5 (BlueNote watcher):** Recent ships (`b3e7ed2`, `4f57df6`) already addressed voice chrome and cue length; reliability is monitoring, not the critical path.  
- **Candidate 4 (Token streaming):** SSE frames are functioning; SSL adapter fix is speculative optimization.  
- **Candidate 3 (Consent UX polish):** Board-actions navigate is already shipped (`164fb4c`); polish is low-ROI vs. operational null state.

## 3. Runner-ups (2–3)
1. **Bind next optical SoftDent/QB bench subpage (Candidate 1)** — Immediate follow-up after OPS loop is proven; wires real beams into the AR/Revenue HTML shells currently showing mocks.  
2. **SoftDent GUI export ops hardening (Candidate 2)** — Required for reliable aging/register pulls within the daily loop, but should be tackled as a hardening task *inside* the period-close package, not as a standalone.  
3. **BlueNote watcher reliability (Candidate 5)** — If the daily OPS loop generates alerts (e.g., "Close failed"), BlueNote must deliver them; schedule this immediately after loop closure.

## 4. What NOT to redo
- Money honesty gate (beam-grounded $; empty≠$0) — shipped `9ce16a7`
- BlueNote chrome/filter/speak rules — shipped `4f57df6`, `b3e7ed2`
- Recon UNAVAILABLE honesty — shipped `2a86f5e`
- Board-actions navigate — shipped `164fb4c`
- SoftDent refresh-period timeout/fail-fast — shipped `cec10bc`
- Short cue openers — shipped `b3e7ed2`

## 5. Acceptance criteria
- [ ] Daily OPS loop executes automatically at 07:00 (or on manual trigger) without GUI hang
- [ ] `activeOperation` field in `/api/import-readiness` reflects `"daily_close"` during execution and `"completed"` with timestamp after success
- [ ] HAL can answer "What was yesterday's close?" with a deterministic, beam-grounded reply citing `daily_close_log.jsonl`
- [ ] Post-loop SoftDent and QB beams update to fresh hashes within 5 minutes of export completion
- [ ] If SoftDent GUI export fails, loop enters `"stalled"` state with honest 504/UNAVAILABLE (no phantom data)
- [ ] Zero write-back to SoftDent; Excel/Print Preview only

## 6. Executive Summary (5 bullets)
- **Operational Gap:** Honest beams exist (`$7,714` / `$78,399`) but `activeOperation: null` reveals no automated rhythm to keep them fresh.
- **Shadow Pilot Risk:** Without a daily close loop, the system cannot graduate from "shadow" to "supervised" because data integrity depends on manual exports.
- **Package Scope:** Automates the PULL (SoftDent/QB export consent) → BEAM (refresh-period with timeout) → CITE (HAL daily summary) cycle.
- **Validation:** HAL chat provides deterministic daily close attestation; `importReadiness` shows `completed` operation context.
- **Path Hygiene:** Uses only `C:\Users\mreno\newridgefamilyfinancial\NewRidgeFinancial2\nr2_hal_gateway.py` and `app_data\nr2\ops\`; no invented routes.

## 7. Approval Checklist
- [ ] Operator confirms daily close time (default 07:00 local) and SoftDent/QB export consent authority
- [ ] `nr2-12023-refresh-period-timeout` confirmed stable on main (no regression in honest 504)
- [ ] HAL gateway has `read_financial` + `override_import` capabilities for period-close citation
- [ ] Pilot phase remains `"shadow"` (no system-of-record cutover until 30-day shadow elapsed)
- [ ] SoftDent write-back remains FORBIDDEN in export script (Excel/Print Preview only)
