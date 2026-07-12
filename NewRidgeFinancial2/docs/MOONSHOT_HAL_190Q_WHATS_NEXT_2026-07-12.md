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
Apply Phase 2 Structured Deliverables (JSON/bullet schema enforcement) to `nr2_hal_gateway.py` and `hal-agent.js` to close the deliverable gap on "steps/paths" queries identified in 190Q, confirming this remains the correct next step after Phase 1 stabilization.

## 0. Operator Intent (verbatim)
next

## 1. Recommended NEXT (name, why now, effort, REAL files, validation gate)
**Phase 2: Structured Deliverables (JSON/Bullet Schema Enforcement)**

**Why now:** Phase 1 fixed post-generation constraints and rubric scoring, raising offline quality ~50→181 and local-policy hit rates to ~25 queries. The remaining 190Q failures cluster on "steps/path/procedure" queries returning narrative prose instead of actionable, machine-readable structures. Enforcing schema now capitalizes on the constraint layer shipped in Phase 1 without requiring a second model or infrastructure changes.

**Effort:** Low–Medium (2–3 days). Additive prompt-path logic; no model swap.

**REAL files:**
- `NewRidgeFinancial2/nr2_hal_gateway.py`: Add `is_deliverable_request()` intent classifier (keywords: "steps", "path", "how do I", "procedure"); branch `evaluate_query()` to inject `format: json` with schema `{"steps": [], "caution": "", "references": []}`; implement markdown-bullet fallback on JSON parse failure; retain Phase 1 sentence caps.
- `NewRidgeFinancial2/site/hal-agent.js`: Add renderer for structured deliverables (bulleted steps + caution box) to prevent UI from flattening JSON into wall-of-text; respect existing SSE stream handlers.

**Validation gate:** Re-run 190Q subset (n=30) filtered for explicit deliverable intent; achieve >70% structured output rate (bullets or JSON); zero regression on read-only compliance (maintain 100% pass on SoftDent/QB write-blocks); latency delta <10% vs. Phase 1 baseline.

## 2. Runner-ups (2–3, why not now)
- **Phase 3 Streaming TTFT UX polish:** SSE infrastructure exists, but perceived latency optimization is lower priority than functional deliverable quality. Defer until Phase 2 proves structured output does not increase token overhead beyond acceptable limits.
- **Phase 4 CARC whitelist hardening:** Phase 1 already implemented unknown CARC refusal; remaining work is whitelist expansion for known codes, which is data maintenance rather than architecture. Schedule after deliverable schema is stable.
- **Live 190Q full re-run:** This is an evaluation action, not a code package. Execute only after Phase 2 is applied and validated to avoid confounding quality metrics.

## 3. What NOT to redo
- Do not re-implement sentence-limit caps, plain-language stripping, or post-generation validation (Phase 1 completed).
- Do not re-tune rubric scoring for read-only compliance (Phase 1 completed).
- Do not re-implement SoftDent/QB write-intent preflight or empty≠$0 guards (Phase 1 completed).
- Do not introduce a second 8B sidecar model (out of scope; R9700 load sufficient with `hal-local:32b` + `num_predict` caps).

## 4. Acceptance criteria
- [ ] Deliverable intent detection triggers on keywords "steps", "path", "how do I", "procedure", "checklist" with <5% false-positive rate on narrative queries.
- [ ] Schema enforcement produces valid JSON or clean markdown bullets (fallback) for 100% of triggered queries.
- [ ] 190Q deliverable-specific subset (n≥30) shows >70% structured pass rate (previously ~0% in raw eval).
- [ ] Zero hallucinated dollar amounts, CARC meanings, or PHI in structured outputs (maintain Phase 1 honesty constraints).
- [ ] `hal-agent.js` renders structured responses as distinct UI components (bulleted list + caution callout) rather than concatenated text.
- [ ] Unit tests added: `test_nr2_hal_deliverable_schema.py` (validate JSON schema compliance) and `test_hal_agent_render.py` (validate UI component separation).
- [ ] No regression in overall 190Q quality score vs. Phase 1 baseline (maintain >180 offline score).

## 5. Executive Summary (5 bullets)
- **Phase 1 stabilized:** Post-gen sentence caps, write-intent preflight, and rubric recalibration applied; offline re-score shows 3.6× quality improvement and 100% read-only compliance on blocked writes.
- **Gap identified:** 190Q queries requesting "steps" or "paths" still receive narrative paragraphs instead of actionable bullets/JSON, failing deliverable criteria despite correct content.
- **Next package:** Phase 2 adds intent detection and schema enforcement to `nr2_hal_gateway.py`, with `hal-agent.js` rendering support, converting prose into structured deliverables without model changes.
- **Risk profile:** Low; additive to existing constraint layer; fallback to markdown ensures graceful degradation if JSON generation fails.
- **Success metric:** >70% structured deliverable rate on targeted 190Q subset while maintaining Phase 1 latency and compliance standards.

## 6. Approval checklist
- [ ] Operator confirms "proceed" to Phase 2 (acknowledges Phase 1 is stable in production).
- [ ] Confirm 190Q subset test cases tagged with `intent:deliverable` are extracted for validation gate.
- [ ] Confirm `hal-agent.js` UI component library supports bulleted lists and caution callouts (or approve lightweight CSS additions).
- [ ] Confirm fallback to markdown bullets is acceptable if strict JSON mode increases TTFT >20%.
- [ ] Confirm no immediate hotfixes required for Phase 1 (stable at 325d24a).