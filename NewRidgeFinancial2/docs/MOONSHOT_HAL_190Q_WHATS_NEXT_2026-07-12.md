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
Proceed with **Phase 2: Structured Deliverables** to enforce JSON/bullet output for procedural queries, converting narrative prose into actionable steps and raising the deliverable rate from ~25% to >70%.

## 0. Operator Intent (verbatim: next)

## 1. Recommended NEXT (name, why now, effort, REAL files, validation gate)

**Phase 2: Structured Deliverables (JSON/Bullet Enforcement)**

**Why now:** Phase 1 fixed constraint parsing and rubric scoring, but the gateway still returns verbose paragraphs for "how to" / "steps" queries. The 190Q eval shows deliverable failures stem from lack of schema enforcement, not model capability. This is the highest-leverage remaining fix to reach operational readiness (>70% deliverable rate).

**Effort:** Medium (2–3 days). Prompt engineering + schema validation + frontend renderer.

**REAL files:**
- `NewRidgeFinancial2/nr2_hal_gateway.py`: Add `is_deliverable_request()` intent detector (keywords: "steps", "procedure", "path", "how to", "checklist"); branch `evaluate_query()` to inject `format: json` with schema `{"steps": ["string"], "caution": "string", "reference": "string"}`; implement JSON validation with markdown bullet fallback.
- `NewRidgeFinancial2/site/hal-agent.js`: Add `renderStructuredDeliverable()` to parse JSON steps into `<ol>` or bullet list; handle legacy prose fallback.
- `NewRidgeFinancial2/site/apex-narratives.js`: Update narrative display to prefer structured blocks over plain text when `deliverable: true` metadata present.

**Validation gate:** Run 50-question 190Q subset containing explicit procedural queries; verify deliverable rate >70% and zero JSON parsing crashes. Spot-check that "caution" field appears for write-intent procedures (soft-blocked).

## 2. Runner-ups (2–3, why not now)

1. **Phase 3: Streaming / TTFT UX Polish** — SSE already exists in `evaluate_query_stream()`; Phase 2 structural fixes impact quality metrics more directly than perceived latency. Defer until deliverable rate target is hit.
2. **Phase 4: CARC Whitelist Hardening** — Phase 1 already refuses unknown CARC codes; remaining work is expansion of `_KNOWN_CAS_CODES` mapping. Lower priority than structural output formatting.
3. **Dual-model load (8B + 32B)** — Requires significant VRAM reconfiguration and inference routing; consult only after single-model quality baseline (Phase 2) is stable.

## 3. What NOT to redo

- Post-generation sentence caps / plain-language strip (completed in Phase 1 via `apply_response_constraints`)
- Write-intent SoftDent/QB preflight refusal (completed)
- Short-ask `num_predict` latency caps (completed)
- Rubric recalibration for read-only variants (completed in `scripts/hal_eval_scoring.py`)
- Empty payroll/AP ≠ $0 validation (completed)

## 4. Acceptance criteria

- [ ] `is_deliverable_request()` correctly flags 90%+ of 190Q procedural queries (manual audit of 20 samples).
- [ ] Gateway returns valid JSON or markdown bullet list; no unformatted prose for "steps" queries.
- [ ] `hal-agent.js` renders steps as numbered list with caution callout box.
- [ ] JSON parse failure triggers graceful fallback to markdown bullets (not raw text dump).
- [ ] Eval script reports deliverable rate ≥70% on procedural subset.
- [ ] No regression on read-only OK rate (remains ≥95%).

## 5. Executive Summary (5 bullets)

- Phase 1 fixed *how much* HAL says; Phase 2 fixes *how* it presents action items (bullets/JSON vs. paragraphs).
- Targets the 74% "deliverable absence" failure mode in 190Q where staff receives narrative instead of checklists.
- Uses existing Ollama JSON mode with lightweight schema validation in the gateway; no model retraining required.
- Frontend change is additive: new renderer for structured data, maintaining backward compatibility with legacy prose responses.
- Unblocks Phase 3 (latency polish) by ensuring streamed tokens arrive in a structured format rather than mid-sentence markdown.

## 6. Approval checklist

- [ ] Schema definition approved (steps/caution/reference fields).
- [ ] Intent detection keywords reviewed for false positives (e.g., "step" in "step therapy" vs. "next steps").
- [ ] Frontend `renderStructuredDeliverable()` implemented in `hal-agent.js`.
- [ ] Fallback logic tested: simulate Ollama JSON failure → verify bullet list output.
- [ ] Eval rubric updated to detect structured deliverables (regex for `\d\.` bullets or JSON blocks).
- [ ] Operator sign-off to proceed with implementation (CONSULT ONLY — no code applied yet).