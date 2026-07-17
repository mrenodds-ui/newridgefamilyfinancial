# Moonshot AI — What's Next After Money-Gap Optical Honesty (CONSULT ONLY)

**Date:** 2026-07-17
**Model:** `kimi-k2.5`
**Key:** OPENROUTER_API_KEY
**Script:** `scripts/run_moonshot_whats_next_after_money_gap_consult.py`
**Prior APPLIED:** `MOONSHOT_MONEY_GAP_OPTICAL_HONESTY_APPLIED_2026-07-17.md` (`1f2f76b`)
**Apply:** Operator must say continue / approve before Cursor applies.

## Operator request (verbatim)

> next

---

# Verdict
Apply **Supervised-pilot prep docs/workflows for Day 30 approach** (Candidate #4) — the only unblocked Cursor path that requires no external files, no SoftDent GUI access, and no date-gated dependencies while respecting the shadow-phase constraints.

## 0. Operator Intent (verbatim)
next

## 1. Recommended NEXT (name, why now, effort, REAL files, validation gate)
**Name:** Supervised-pilot prep docs/workflows for Day 30 approach  
**Why now:**  
- LIVE AUDIT confirms Shadow Day 2/30 with `shadowEligible: false` and `forceCloseAvailable: false`.  
- All other productive paths are externally blocked: SoftDent GUI (operator hard stop), ERA inbox (realFileCount=0), and Trellis (date-locked ~2026-07-20).  
- Preparing runbooks, checklists, and attestation templates now prevents last-minute gaps when the 30-day shadow clock expires, without violating the “no forceClose flip” rule.

**Effort:** Low (documentation-only; no code touching production data).  
**REAL files:** None required (creates `docs/runbooks/supervised_pilot_transition_nr2.md` and `docs/checklists/day_30_attestation_readiness.md`).  
**Validation gate:**  
- [ ] Docs reviewed by operator for alignment with SoftDent+QB overlay model (no PMS replacement claims).  
- [ ] Confirm `forceClose` remains `false` in `pilot.json` (no flip).  
- [ ] Confirm no SoftDent write-back protocols introduced.

## 2. Ordered backlog AFTER #1 (2–4)
2. **WAIT/ATTENDED — SoftDent Excel Carestream** (Blocked until operator explicitly resumes/lifts hard stop; attended only per hold protocol).  
3. **WAIT — real ERA .835 from payer** (Blocked until `realFileCount > 0`; SOP ready but inbox contains only README placeholder).  
4. **WAIT — Trellis withBenefits** (Blocked until ~2026-07-20; chipStatus awaiting).

## 3. Why this beats the other candidates now
- **#1 (SoftDent Excel):** Explicitly blocked by `softdentOperatorHardStop: true`. Cursor cannot apply GUI-un-grey code; Carestream/operator must attend.  
- **#2 (ERA):** `realFileCount: 0` means zero productive work possible; inventing fake 835s violates “empty ≠ $0” and “no fake 835” constraints.  
- **#3 (Trellis):** Date-gated (~2026-07-20); no Cursor action can accelerate the payer API timeline.  
- **#5 (Other live audit):** While “collections” failed in the morning bundle, remediation likely requires SoftDent write-back or reconciliation logic, both prohibited. Speculative coding risks violating “no Preview money” and “no SoftDent write-back” rules.  
- **#4:** Uses the LIVE AUDIT state (Day 2/30) to create value immediately without external inputs, unblocking future operator decisions.

## 4. What NOT to redo
- **Money-gap optical honesty** (commit `1f2f76b` already applied; do not re-render `nr2-optical-page-money-gap.html` or modify `metricGapHonesty`).  
- **SoftDent Excel grey hold protocol** (already documented at `docs/runbooks/softdent_excel_grey_hold_protocol_nr2.md`; do not generate GUI automation to un-grey).  
- **ERA 835 SOP** (already documented at `docs/runbooks/era_835_inbox_drop_nr2.md`).  
- **Auto-reconcile logic or Reconcile CTA** (prohibited by money-gap honesty; delta $26,129.22 must remain labeled “Different Metrics — Not Auto-Reconciled”).  
- **Preview-as-money, fake 835/withBenefits, or forceClose flip** (strictly prohibited).

## 5. Acceptance criteria
- [ ] Draft runbook exists: `docs/runbooks/supervised_pilot_transition_nr2.md` covering Day 30 entry criteria (shadowDaysElapsed ≥ 30, attestation signature, cutover attestation).  
- [ ] Draft checklist exists: `docs/checklists/day_30_attestation_readiness.md` with PHI-handling confirmations (initials+hash, no Printer/File).  
- [ ] `pilot.json` (or equivalent config) shows `forceClose: false` unchanged.  
- [ ] No new React components or chat embeds introduced.  
- [ ] No SoftDent write-back API endpoints created.  
- [ ] Documentation references current LIVE AUDIT data: 150 claims, $52,270 AR, $78,399 QB revenue, shadow clock Day 2.

## 6. Executive Summary (5 bullets)
- **Money-gap honesty live:** SoftDent AR ($52,270) vs QB Revenue ($78,399) displayed as different metrics with no auto-reconcile CTA; delta $26,129 acknowledged.  
- **SoftDent hard stop active:** Operator lock prevents Excel GUI automation; Carestream attendance required to lift.  
- **ERA inbox empty:** Only README placeholder present (realFileCount=0); awaiting payer 835 drops to trigger ingest.  
- **Trellis withBenefits date-locked:** ~2026-07-20 earliest availability; forceClose remains false.  
- **Shadow Day 2/30:** Only viable Cursor work is supervised-pilot documentation prep; all mutation paths blocked by external dependencies or hard stops.

## 7. Approval Checklist
- [ ] Operator confirms SoftDent hard stop is still active (no premature GUI code).  
- [ ] No fake 835 or withBenefits mock data invented in docs.  
- [ ] No `forceClose` flag flipped to `true` in any config.  
- [ ] No re-application of money-gap optical honesty (1f2f76b).  
- [ ] Output is docs-only; no executable code touching SoftDent or ERA ingestion logic.
