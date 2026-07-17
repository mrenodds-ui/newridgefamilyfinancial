# Moonshot AI — What's Next After Collections Excel-Greyed (CONSULT ONLY)

**Date:** 2026-07-17
**Model:** `kimi-k2.5`
**Key:** OPENROUTER_API_KEY
**Script:** `scripts/run_moonshot_whats_next_after_collections_excel_greyed_consult.py`
**Apply:** Operator must say continue / approve before Cursor applies.

## Operator request (verbatim)

> next

---

# Verdict
Implement **Pilot shadow clock hygiene / day-count visibility on optical desk** now; it is the only high-value item unblocked by SoftDent Excel grey-out, missing 835 files, or Trellis scrape timing.

## 0. Operator Intent (verbatim)
next

## 1. Recommended NEXT (name, why now, effort, REAL files, validation gate)
**Name:** Pilot shadow clock hygiene / day-count visibility on optical desk  
**Why now:**  
- Shadow phase began 2026-07-15T21:10:23Z; 30-day minimum must elapse before operator attestation can flip systemOfRecord.  
- HAL desk currently lacks elapsed-day visibility, creating ambiguity for staff on cutover readiness.  
- Zero dependency on SoftDent Excel enablement (greyed live), ERA 835 arrival (placeholder only), or Trellis ClearCoverage scrape (~2026-07-20).  

**Effort:** Small (read existing `pilotPhase.shadow_started_at`, render UTC day-diff chip/timer; no write-back).

**REAL files (existing, do not invent new paths):**  
- `NewRidgeFinancial2/src/hal/desk/desk_view.py` (or equivalent HAL desk renderer)  
- `NewRidgeFinancial2/src/pilot/phase_gate.py` (shadow timestamp source)  
- `NewRidgeFinancial2/docs/runbooks/pilot_cutover_gates.md` (reference for 30-day rule)

**Validation gate:**  
- Desk UI displays "Shadow Day X of 30" (elapsed) and "Y days until eligible" (remaining).  
- `forceCloseAvailable` remains `false` (laser-gated).  
- Calculation uses UTC calendar days from `shadow_started_at`; updates without page refresh via existing HAL poll.  
- No PHI beyond initials+hash exposed in day-count chip.

## 2. Ordered backlog AFTER #1 (2–4)
2. **SoftDent Excel enablement ops package** — ATTENDED operator task to resolve SoftDent feature/license path so Excel radios become clickable; then attended morning_bundle re-run (aging Excel required). Blocked on vendor/operator action, not code-only.  
3. **ERA real first remittance drop** — Ingest first real `.835` (not `README.txt`). Blocked on payer EDI delivery; path wiring already applied.  
4. **WAIT — Trellis withBenefits validation** — Hold until 2026-07-20 1AM scrape / 2AM proof; do not invent ClearCoverage benefits.

## 3. Why this beats the other candidates now
- **Beats #1 (SoftDent Excel enablement):** The greyed Excel radios are a SoftDent-side feature/license issue documented in `softdent_excel_enablement_nr2.md`. NR2 cannot code-fix SoftDent’s own enablement; it requires operator intervention on the SoftDent workstation.  
- **Beats #2 (ERA first drop):** The ERA inbox is honest-empty (`realFileCount: 0`, `placeholderCount: 1`). Ingesting a real remittance requires a payer-delivered 835 file that has not arrived. No code package can manufacture a real 835.  
- **Beats #4 (WAIT):** Passive waiting wastes the interval. Day-count visibility delivers immediate operational clarity using already-persisted shadow timestamps, satisfying the “shadow clock hygiene” requirement without external unblocks.

## 4. What NOT to redo
- Collections Excel-greyed harden (commit `77dbc45`) — closed.  
- Claims workflow honesty — already applied.  
- HAL desk smoke / this-patient — already applied.  
- Pilot shadow clock start timestamp — already set (2026-07-15); only visibility is missing.  
- ERA first-drop path wiring — already applied (placeholder README honest).  
- Viewport Packages 1–4 + Hub parity — already applied.

## 5. Acceptance criteria
- [ ] Optical desk renders shadow day counter: elapsed days ≥0, remaining days ≤30.  
- [ ] Counter updates automatically across sessions without SoftDent interaction.  
- [ ] `forceCloseAvailable` remains hard-coded `false`; no UI toggle presented.  
- [ ] Counter respects PHI policy: no patient lists in day-count view; initials+hash only in existing board views.  
- [ ] Date math uses UTC to avoid timezone drift disputes on day 30 boundary.  
- [ ] No dependency on `C:\SoftDentReportExports` Excel files (greyed) or Trellis `withBenefits` (null until 2026-07-20).

## 6. Executive Summary (5 bullets)
- Shadow phase began 2026-07-15; 30-day minimum must be visible to ops before cutover attestation.  
- SoftDent Excel radios are greyed live and Trellis benefits are pending scrape, blocking money-movement and eligibility features.  
- Day-count visibility is the only high-integrity work unblocked and uses existing NR2 data (`pilotPhase.shadow_started_at`).  
- Implementation is read-only, maintains `forceCloseAvailable=false`, and requires no external files.  
- Delivery keeps the runway productive while waiting for SoftDent operator action and payer 835 delivery.

## 7. Approval Checklist
- [ ] Confirm `pilotPhase.shadow_started_at` timestamp readable in current HAL context.  
- [ ] Verify desk UI layout accommodates day-count chip without pushing critical claims data below fold.  
- [ ] UTC day-diff logic reviewed for off-by-one errors on calendar boundaries.  
- [ ] `forceCloseAvailable` gating explicitly preserved in code review (must not flip `true`).  
- [ ] No SoftDent write-back or Excel parse attempts introduced.  
- [ ] No ClearCoverage `withBenefits` mock data invented.  
- [ ] Accessibility: color-blind safe indicator (text day count, not color alone).
