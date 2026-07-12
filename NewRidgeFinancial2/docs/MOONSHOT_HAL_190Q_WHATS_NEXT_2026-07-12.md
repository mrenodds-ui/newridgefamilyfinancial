# Moonshot AI — What's Next After HAL 190Q Phase 1 (CONSULT ONLY)

**Date:** 2026-07-12  
**Model:** kimi-k2.5  
**Key:** OPENROUTER_API_KEY  
**Status:** ok  
**Build:** hal-10561 + hal-local:32b  
**Prior applied:** `MOONSHOT_HAL_190Q_FIX_PHASE1_APPLIED_2026-07-12.md`  
**Script:** `scripts/run_moonshot_hal_190q_whats_next.py`  
**Apply:** DO NOT APPLY until operator approves.

## Operator request (verbatim)

> next

---

# Verdict
Phase 2 (Structured Deliverables) remains the correct next package; enforce JSON schema or bulleted output for step-oriented queries in the gateway to raise deliverable rates above 70% before any live 190Q re-run.

## 0. Operator Intent (verbatim)
next

## 1. Recommended NEXT (name, why now, effort, REAL files, validation gate)
**Phase 2: Structured Deliverables (JSON/Bullet Enforcement)**  
- **Why now**: Phase 1 fixed constraints and scoring alignment, but ~75% of quality failures on action-oriented queries still stem from narrative prose instead of machine-readable steps. Raising deliverable rates to >70% is required before a meaningful live 190Q re-run can validate end-to-end quality.  
- **Effort**: Medium (prompt engineering + JSON mode toggle + fallback logic).  
- **REAL files**:  
  - `NewRidgeFinancial2/nr2_hal_gateway.py`: Add `is_deliverable_request()` helper to detect intent keywords ("steps", "path", "how to", "procedure", "checklist"); modify `evaluate_query()` to inject `format: json` with schema `{"steps": [], "caution": "", "references": []}` when intent is detected; implement markdown bullet fallback if JSON parse fails.  
  - `scripts/run_moonshot_hal_190q_eval.py`: Add deliverable-rate metric capture to validate the gate.  
- **Validation gate**: Run 50-question subset containing explicit "provide steps" queries; deliverable rate must exceed 70% (bulleted or JSON) with zero hallucinated file paths.

## 2. Runner-ups (2–3, why not now)
1. **Phase 3 (Streaming TTFT Polish)** — SSE infrastructure already exists; perceived latency gains are lower priority than structural deliverable quality. Apply only after Phase 2 proves deliverable rates are stable.  
2. **Phase 4 (CARC Whitelist Hardening)** — Partially addressed in Phase 1’s "unknown CARC refuse" logic; additional whitelist expansion yields diminishing returns compared to schema enforcement.  
3. **Live 190Q Re-run** — Do not execute until Phase 2 is applied; re-running now would waste operator review cycles on known deliverable-format failures that Phase 2 is designed to eliminate.

## 3. What NOT to redo
- Post-generation sentence caps or plain-language stripping (already in `nr2_hal_gateway.py`).  
- Write-intent SoftDent/QB preflight or empty ≠ $0 logic (already blocking inventively).  
- Rubric recalibration for read-only variants (already fixed in `scripts/hal_eval_scoring.py`).  
- CARC unknown-code refusal logic (already hardened in Phase 1).  
- GitHub/PR process as the primary work package (focus remains on local additive gateway fixes).

## 4. Acceptance criteria
- [ ] `is_deliverable_request()` correctly flags >90% of step-oriented queries in unit tests.  
- [ ] JSON schema output renders for flagged queries with `"steps"` array present and non-empty.  
- [ ] Fallback to markdown bullets occurs within 500ms if JSON parsing fails (no blank responses).  
- [ ] Deliverable rate on 50-question test set ≥70%.  
- [ ] No invented file paths (validation confirms only `NewRidgeFinancial2/nr2_hal_gateway.py` and `scripts/run_moonshot_hal_190q_eval.py` are touched).  
- [ ] Existing Phase 1 tests (`test_nr2_hal_local_policy.py`, `test_hal_eval_scoring.py`) continue to pass.

## 5. Executive Summary (5 bullets)
- Phase 2 is the highest-yield remaining fix: it converts narrative prose into actionable, machine-readable steps.  
- Implementation is localized entirely to `nr2_hal_gateway.py` (detection + JSON mode) and the eval script (metric capture).  
- Success unblocks the live 190Q re-run by ensuring staff receive structured answers rather than essays.  
- Risk is low: additive feature with graceful markdown fallback; no breaking changes to existing SSE or preflight logic.  
- Deferred work (Phase 3 streaming polish, Phase 4 CARC expansion) remains queued behind this package.

## 6. Approval checklist
- [ ] Confirm operator wants to proceed with Phase 2 (Structured Deliverables) as described.  
- [ ] Confirm real file scope limited to `NewRidgeFinancial2/nr2_hal_gateway.py` and `scripts/run_moonshot_hal_190q_eval.py`.  
- [ ] Confirm no SoftDent write-back or dollar invention is introduced (read-only constraints preserved).  
- [ ] Confirm Phase 3 (streaming UX) and live 190Q re-run remain blocked until Phase 2 validation gate passes.