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
Implement Phase 2 Structured Deliverables next—enforcing JSON/bullet output for action-oriented queries (steps, paths, procedures) in `nr2_hal_gateway.py` to raise the deliverable rate from ~25% to >70% while reusing Phase 1’s constraint engine.

## 0. Operator Intent (verbatim)
next

## 1. Recommended NEXT (name, why now, effort, REAL files, validation gate)
**Phase 2: Structured Deliverables (Action-Query Schema Enforcement)**  
**Why now:** Phase 1 fixed validation and rubric scoring; the remaining P1 blocker from the 190Q consult is unstructured prose for “how to” / “steps” / “path” queries. Staff cannot act on narrative walls— they need bulleted steps or JSON decision trees. This is additive to the existing `clean_gateway_text` pipeline and leverages the Phase 1 `num_predict` caps to keep JSON generation fast.  
**Effort:** Medium (2–3 days)  
**REAL files:**  
- `NewRidgeFinancial2/nr2_hal_gateway.py`: Add `is_deliverable_request()` intent detector (keywords: steps, path, procedure, how to); branch `evaluate_query()` to inject `format: json` with schema `{"steps": [...], "caution": "...", "read_only": bool}`; add markdown-list fallback if JSON parse fails.  
- `scripts/hal_eval_scoring.py`: Update `_needs_deliverable` regex to align with gateway intent detection; ensure deliverable scoring accepts bulleted lists or valid JSON arrays as compliant.  
- `NewRidgeFinancial2/site/hal-core.js` (minor): Render `steps` arrays as collapsible `<ol>` or JSON tree without page reload (optional polish).  

**Validation gate:**  
- Run 190Q subset (n=50) filtered for explicit “steps/path” queries; deliverable rate must hit ≥70% and zero false-positive refusals on legitimate action asks.  
- Confirm no regression on Phase 1 sentence caps (all outputs ≤ constraint limit).

## 2. Runner-ups (2–3, why not now)
1. **Phase 3 Streaming / TTFT UX Polish** — SSE already exists; perceived latency is acceptable after Phase 1 short-ask `num_predict` caps. Lower ROI than fixing output structure that blocks staff workflows.  
2. **Phase 4 CARC Whitelist Hardening** — Partially completed in Phase 1 (unknown CARC refuse); remaining work is low-volume edge-case tuning compared to the broad impact of structured deliverables.  
3. **ERA 835 Depth Expansion (REC-005)** — 190Q issues are HAL response-quality problems, not ERA parsing gaps; defer until HAL operational quality is >85%.

## 3. What NOT to redo
- Post-generation sentence caps / plain-language strip (Phase 1 complete).  
- Write-intent SoftDent/QB preflight or empty≠$0 logic (Phase 1 complete).  
- Rubric recalibration for read-only variants (Phase 1 complete).  
- Unknown CARC/CAS hard refuse (Phase 1 complete).  
- Loading a second 8B model (explicitly excluded).  
- Inventing file trees outside `NewRidgeFinancial2/` or `scripts/` (e.g., no `src/hal/`, `lib/nr2/`).  
- GitHub/PR as the primary package (keep local additive fixes).

## 4. Acceptance criteria
- [ ] `is_deliverable_request` detects ≥90% of step/path queries with <5% false-positive rate on informational asks.  
- [ ] Gateway returns valid JSON or markdown bullets for all flagged deliverable queries; narrative prose rejected/regenerated.  
- [ ] `scripts/run_moonshot_hal_190q_eval.py` shows deliverable rate ≥70% on the 190Q action-query subset.  
- [ ] Phase 1 unit tests (`test_nr2_hal_local_policy`, `test_hal_eval_scoring`) still pass.  
- [ ] No hallucinated dollar amounts, CARC meanings, or PHI in structured outputs (inherits Phase 1 “no invention” policy).

## 5. Executive Summary (5 bullets)
- Phase 1 constraint enforcement and rubric fixes are live; the next quality bottleneck is unstructured prose for operational “how-to” queries.  
- Phase 2 adds an intent detector and schema wrapper to `nr2_hal_gateway.py`, forcing bulleted or JSON steps instead of walls of text.  
- Validation uses the existing 190Q corpus to prove staff can now act on HAL outputs without manual reformatting.  
- Keeps the “no invention” policy: structured outputs are strictly read-only unless explicit consent/write-paths are implemented later.  
- Positions the codebase for Phase 3 (streaming polish) only after staff confirm the new formats are usable.

## 6. Approval checklist
- [ ] Review keyword list for `is_deliverable_request` (avoid over-triggering on “step” as in “step ladder” or “step rate”).  
- [ ] Confirm JSON schema choice (`steps`, `caution`, `read_only`) vs alternative `actions`/`paths` naming.  
- [ ] Approve markdown fallback strategy when Ollama JSON mode fails (graceful degradation).  
- [ ] Verify 20-question manual spot-check passes deliverable formatting.  
- [ ] Schedule offline re-score of full 190Q after Phase 2 merge to measure composite quality lift.