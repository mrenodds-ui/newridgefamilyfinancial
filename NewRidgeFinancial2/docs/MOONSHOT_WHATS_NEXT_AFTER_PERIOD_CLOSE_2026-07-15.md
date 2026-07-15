# Moonshot AI — What's Next After Period-Close OPS (CONSULT ONLY)

**Date:** 2026-07-15
**Model:** `kimi-k2.5`
**Key:** OPENROUTER_API_KEY
**Status:** ok
**Repo root:** `C:\Users\mreno\newridgefamilyfinancial`
**Prior:** `263b26b` SoftDent export consent-free · `8972b8d` period-close OPS
**Script:** `scripts/run_moonshot_whats_next_after_period_close_consult.py`
**Apply:** DO NOT APPLY until operator approves.

## Operator request (verbatim)

> next

---

# Verdict
Bind optical SoftDent/QB bench subpages to live money beams so AR/Revenue shells display the daily close truth ($7,714 / $78,399) with beam-hash provenance, completing the "display truth" stack now that the period-close validation loop is production-hardened.

## 0. Operator Intent (verbatim)
next

## 1. Recommended NEXT (name, why now, effort, REAL files/ops, validation gate)
**Package:** Optical Bench Subpage Beam Binding (AR/Revenue live display)  
**Why now:** The LIVE AUDIT confirms period-close OPS is completing successfully (`status: completed`, `beamHash: 887abf908c98136e`) and money beams are honest ($7,714 SoftDent / $78,399 QB). However, the optical Pages Hub likely still renders static or hardcoded shells rather than citing these live beams. Staff cannot trust what they cannot see—this wires the validated backend state into the UX layer.  
**Effort:** Medium (3–4 hours)—swap static currency displays for beam-bound components, handle `emptyNotZero` states, add beam-hash tooltips for audit trail.  
**REAL files/ops:**
- `C:\Users\mreno\newridgefamilyfinancial\NewRidgeFinancial2\templates\optical\ar_bench.html` — bind `{{ moneyBeams.softdent.totalOutstanding }}` / `{{ moneyBeams.softdent.display }}` with `emptyNotZero` guard; cite `beamHash`  
- `C:\Users\mreno\newridgefamilyfinancial\NewRidgeFinancial2\templates\optical\revenue_bench.html` — bind `{{ moneyBeams.quickbooks.monthlyRevenue }}` / `{{ moneyBeams.quickbooks.display }}`; cite `beamTimestamp`  
- `C:\Users\mreno\newridgefamilyfinancial\NewRidgeFinancial2\nr2_http_server.py` — ensure `/optical/ar` and `/optical/revenue` routes inject `moneyBeams` context from `money_beam_attestation()` (not cached)  
- `C:\Users\mreno\newridgefamilyfinancial\NewRidgeFinancial2\static\css\optical-honesty.css` — red-laser overlay styling when `alignmentLasers.red: true` (block display with "Data stale — alignment required")  
- `C:\Users\mreno\newridgefamilyfinancial\app_data\nr2\ops\period_close_state.json` — read `lastBeamHash` to show "Confirmed at close" badge vs "Live preview"  
**Validation gate:**  
1. Load `/optical/ar` → displays "$7,714" (matches LIVE AUDIT), shows beam hash `4256900597b217e7` in footer tooltip  
2. Load `/optical/revenue` → displays "$78,399", cites "QuickBooks revenue live (latest month)"  
3. If `alignmentLasers.red: true` injected in mock, page shows red overlay "Financial data unavailable — alignment lasers blocked" (never $0)  
4. HAL Gateway `GET /api/hal/tools/money-beams` returns identical values to optical render (no drift)

## 2. Why this beats the other candidates now
- **SoftDent export hardening:** Currently working (consent-free export succeeded in 263b26b; LIVE AUDIT shows fresh SoftDent syncs). Optimization is premature until display layer proves the data is consumed.  
- **BlueNote stall alerts:** Preventive only; period-close is currently completing without stalls (`completedAt: 2026-07-15T21:10:23`). Alerting on a non-problem is noise.  
- **Wire period-close SoftDent pull into scheduler:** The daily close already runs (`periodCloseOpsExists: true`); SoftDent pull is available via `pull_softdent` flag but not required every close since beams refresh independently.  
- **Force Close control:** Convenience feature; the loop is already auto-completing successfully.  
- **Desk proof:** Validation is necessary but not a "package" of work; beam binding includes E2E validation as acceptance criteria.

## 3. Runner-ups (2–3)
1. **SoftDent GUI export ops hardening** — Retry logic on Excel save dialogs, collections export path validation; prioritize if beam binding reveals export intermittency under daily load.  
2. **BlueNote alert when period-close stalls** — Watch `daily_close_log.jsonl` for `status: blocked` >30 min; send OM notification; prioritize after optical pages prove the data rhythm is valuable.  
3. **HAL Force Close control** — Operator-triggered `POST /api/period-close/force` for end-of-month edge cases; requires laser-gate bypass consent log.

## 4. What NOT to redo
- Period-close attest loop (already live, logging to `daily_close_log.jsonl`)  
- SoftDent consent-free export (263b26b shipped)  
- Money honesty / empty≠$0 doctrine (already enforced)  
- BlueNote chrome filter / SideNotes retirement (fc804b6 completed)  
- Recon UNAVAILABLE state handling (prior shipped)  
- Board navigation / refresh fail-fast (cec10bc shipped)  
- Laser softGap unification (639d601 shipped)  
- Subpage honesty stamps (nr2-12027 shipped)

## 5. Acceptance criteria
- [ ] `/optical/ar` renders SoftDent claims total exactly as `moneyBeams.softdent.display` from LIVE AUDIT (`$7,714`)  
- [ ] `/optical/revenue` renders QB revenue exactly as `moneyBeams.quickbooks.display` (`$78,399`)  
- [ ] Both pages display `beamHash` and `beamTimestamp` in audit footer (provenance)  
- [ ] When `alignmentLasers.red: true`, both pages show red overlay "Data unavailable — alignment required" and suppress all dollar amounts (never show $0)  
- [ ] HAL Gateway citation matches optical display pixel-for-pixel (no dual-source drift)  
- [ ] Unit test: `test_optical_pages_render_money_beams` mocks beams and asserts DOM contains expected values with `emptyNotZero` handling

## 6. Executive Summary (5 bullets)
- **Status:** Period-close OPS loop is production-hardened (`nr2-12026-period-close-ops`); beams are honest and logging.  
- **Gap:** Optical bench pages (AR/Revenue) are not yet bound to these live beams, leaving staff with static or stale displays.  
- **Solution:** Wire `money_beam_attestation()` directly into `/optical/ar` and `/optical/revenue` templates with laser-gate overlays.  
- **Risk:** Low—read-only display of existing validated data; no write-back to SoftDent/QB.  
- **Outcome:** Staff see the same $7,714 / $78,399 that HAL cites, with beam-hash audit trail visible in UI.

## 7. Approval Checklist
- [ ] Confirm optical page paths (`ar_bench.html`, `revenue_bench.html`) exist in templates directory  
- [ ] Verify `money_beam_attestation()` function is importable from `daily_closeout.py` or `nr2_hal_gateway.py`  
- [ ] Confirm no SoftDent write-back required (read-only display)  
- [ ] Validate `emptyNotZero` CSS classes exist for red-laser blocking state  
- [ ] Acknowledge 3–4 hour effort estimate before operator approves "next" implementation
