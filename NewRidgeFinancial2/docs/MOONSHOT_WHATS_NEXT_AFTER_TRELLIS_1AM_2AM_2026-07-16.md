# Moonshot AI — What's Next After Trellis 1AM/2AM (CONSULT ONLY)

**Date:** 2026-07-16
**Model:** `kimi-k2.5`
**Key:** OPENROUTER_API_KEY
**Script:** `scripts/run_moonshot_whats_next_after_trellis_1am_2am_consult.py`
**Closed:** `d3bb9f3` Trellis 1AM + SoftDent never-Printer · `9849c2e` withBenefits 2AM
**Apply:** Operator must say continue / approve before Cursor applies.

## Operator request (verbatim)

> ask moonshot what is next and report

---

# Verdict
Prioritize **ERA inbox first 835 drop + ingest smoke test** to unblock the cash-posting pipeline while the operator defers the SoftDent morning bundle.

## 0. Operator Intent (verbatim)
ask moonshot what is next and report

## 1. Recommended NEXT (name, why now, effort, REAL files under NewRidgeFinancial2/, validation gate)
**Name:** ERA Ingest Path – First 835 Drop & Smoke  
**Why now:** The ERA inbox gate is YELLOW (inbox=0) and represents the cash-application side of the revenue cycle. With the SoftDent production pull deferred by the operator, this is the highest-value parallel track that validates end-to-end money flow without requiring SoftDent write-back or attended Excel sessions. It prepares the reconciliation layer for when Trellis withBenefits data arrives Mon 1 AM.  
**Effort:** 1–2 hours attended for the first drop and parse; then automated.  
**REAL files under NewRidgeFinancial2/:**
- `scripts/ingest_835.py` (or equivalent EDI parser already in repo)
- `app_data/nr2/office/era_inbox/drop/` (per opsGatesLatest suggestion)
- `app_data/nr2/db/` for persistence validation
- `scripts/ops_gates.py` for status flip verification  
**Validation gate:** Successfully parse ≥1 real 835 file, extract PLB/PatientName, match to the existing Trellis patient list (or desk-proof patient set), and flip `opsGatesLatest.era_inbox.status` from YELLOW to GREEN with `inbox≥1`.

## 2. Ordered backlog AFTER #1 (2–4)
2. **Pilot shadowDays / Cutover Clock Hygiene** – Set `shadowDays=0` to start the ≥30-day cutover countdown; unblocks the eventual go-live calendar without touching SoftDent.  
3. **Claims outstanding patient-join fix** – Polish `sampleWithPatientId=0` logic in the claims scrubber so it is ready to reconcile against the morning bundle when the operator later approves it.  
4. **SoftDent attended morning bundle Excel re-run** – Resume the deferred #1 only when the operator is available; this remains the final money-beam blocker but is intentionally sequenced after parallel paths are green.

## 3. Why this beats the other candidates now
- **Beats #1 (SoftDent bundle):** The operator explicitly deferred the attended morning bundle; insisting on it now violates intent. ERA is fully parallelizable cash-flow infrastructure that does not compete for operator attention.  
- **Beats #2 (Claims fix):** Claims fix optimizes outbound billing; ERA enables inbound cash posting. An empty inbox is a harder blocker than a sampling edge-case in claims.  
- **Beats #4 (Wait passive):** Waiting until Mon 1 AM produces zero validation; the ERA drop exercises the ingest pipeline, optical recognition, and PHI-handling (initials+hash) immediately.  
- **Beats #5 (QB AP/payroll):** The live audit marks QB datasets as optional/stale; ERA is revenue-critical and unblocks the period-close reconciliation.  
- **Beats #6 (Shadow days):** Clock hygiene is procedural; ERA is operational cash validation that proves the system can receive payer data.

## 4. What NOT to redo
- Do **not** re-argue the Trellis 1 AM pull / 2 AM proof schedule (already locked in commit `9849c2e`).  
- Do **not** flip `forceCloseAvailable` to true solely because `beam_desk_proof` is GREEN (remains laser-gated per constraints).  
- Do **not** attempt SoftDent write-back, printer automation, or invent new Excel drop directories (SoftDent remains Excel|Print Preview only).  
- Do **not** build invented React frontends; rely on existing Python scripts and optical JS paths.

## 5. Acceptance criteria
- [ ] One real 835 file is dropped into `app_data/nr2/office/era_inbox/drop/`  
- [ ] `python scripts/ingest_835.py` executes without exception and respects PHI initials+hash masking  
- [ ] Database shows `era_inbox` row count ≥1 and PLB segment parsed  
- [ ] `opsGatesLatest.era_inbox` flips from YELLOW to GREEN with `inbox>0` and `suggestions>0`  
- [ ] Cross-validation: At least one ERA patient matches the Trellis patient list (or desk-proof set) to prove join logic

## 6. Executive Summary (5 bullets)
- Operator deferred the SoftDent morning bundle; the system has a parallel cash-path gap (ERA inbox empty).  
- ERA 835 ingest is revenue-critical, read-only (no SoftDent write), and executable immediately without attended Excel sessions.  
- First drop validates the EDI parser, optical recognition layer, and PHI-handling without risk of regression (inbox is currently empty).  
- Success unblocks the “cash side” to complement the “charge side” (Trellis/SoftDent) when they converge after Mon 1 AM.  
- Risk is low: if parsing fails, simply remove the file and reset the inbox counter; no production money data is corrupted.

## 7. Approval Checklist
- [ ] Operator confirms availability of a sample 835 file (or requests one from the payer).  
- [ ] Backup/snapshot of `app_data/nr2/office/era_inbox/` verified (empty baseline preserved).  
- [ ] `scripts/ingest_835.py` reviewed for PHI compliance (initials+hash, no full names logged).  
- [ ] Target drop time scheduled (suggest immediate, before the Trellis 1 AM Mon scrape).  
- [ ] Rollback plan documented: delete dropped file and reset inbox counter if validation fails.
