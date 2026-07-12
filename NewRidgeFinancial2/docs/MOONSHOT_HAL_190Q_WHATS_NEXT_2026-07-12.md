# Moonshot AI — What's Next After HAL 190Q Phase 1 (CONSULT ONLY)

**Date:** 2026-07-12  
**Model:** kimi-k2.5  
**Key:** OPENROUTER_API_KEY  
**Status:** ok  
**Build:** hal-10561 + hal-local:32b  
**Prior applied:** Phase 1 (`325d24a`) + Phase 2 (`f225b2b`)  
**Script:** `scripts/run_moonshot_hal_190q_whats_next.py`  
**Apply:** DO NOT APPLY until operator approves.

## Operator request (verbatim)

> next

---

# Verdict
Apply Phase 3: Streaming / TTFT UX polish to cut perceived latency from ~53s to <2s TTFT via true SSE streaming with progressive UI render, building on the Phase 2 SSE foundation.

## 0. Operator Intent (verbatim)
next

## 1. Recommended NEXT (name, why now, effort, REAL files, validation gate)
**Phase 3: Streaming / TTFT UX Polish**

**Why now:** Phases 1–2 fixed quality (26% → target 85%+) and deliverable structure, but the 190Q baseline shows 53s average latency—unacceptable for interactive staff workflows. Phase 2 added SSE aggregation for deliverables; Phase 3 completes the loop by enabling true token/chunk streaming to drive TTFT under 2 seconds. This is the last major UX blocker before production release.

**Effort:** Medium (3–4 days). Extends existing SSE plumbing; no model changes.

**REAL files:**
- `NewRidgeFinancial2/nr2_hal_gateway.py`: `evaluate_query_stream()` — replace blocking `requests.post` with `stream=True` iterator; buffer partial JSON for schema validation without breaking TTFT; emit `data: {"chunk": "..."}` frames immediately on first token.
- `NewRidgeFinancial2/site/hal-core.js`: `streamHalReply()` — refactor from “wait-for-full-SSE” to progressive `MarkdownIt` incremental render; maintain Phase 2 list-preservation logic during streaming.
- `NewRidgeFinancial2/site/hal-agent.js`: `handleStreamChunk()` — accumulate steps/caution JSON fields progressively; flush to DOM per chunk to avoid 50s blank screen.
- `NewRidgeFinancial2/site/apex-core.js`: Connection watchdog — detect stalled streams (>5s gap) and fallback to non-streaming path.

**Validation gate:**
1. Synthetic latency test: 20 warm queries → 90th percentile TTFT < 2s.
2. 190Q subset (n=30) run: deliverable rate ≥ Phase 2 baseline (no regression), perceived latency (staff stopwatch) < 3s median.
3. UI inspection: numbered steps render progressively without “jump” or list corruption.

## 2. Runner-ups (2–3, why not now)
- **Phase 4: CARC whitelist hardening** — Defers known-code briefs and deep CARC ontology. Not now because latency UX is the current production blocker; CARC accuracy is already “acceptable” via Phase 1 unknown-code refusal.
- **Live full 190Q re-run** — Measurement is premature. Re-run only after Phase 3 lands to capture final latency/quality metrics; otherwise you’re benchmarking a known-slow path.
- **SoftDent write-back atomicity** — REC-005/009 context suggests inbox export is working; write-back risks are mitigated by Phase 1 preflight. Lower priority than TTFT.

## 3. What NOT to redo
- Phase 1 constraints (sentence caps, plain-language strip, empty ≠ $0) — already applied 325d24a.
- Phase 2 structured deliverables (JSON schema, numbered markdown, SSE aggregate) — already applied f225b2b; do not strip or replace, only stream-enable.
- CARC “unknown” hard refusal — already in Phase 1; do not reimplement.
- QB payroll/AP CSV export — REC-009 shipped; no delta needed.

## 4. Acceptance criteria
- [ ] TTFT (time to first token/chunk) < 2 seconds on warm `hal-local:32b` (R9700).
- [ ] Full response completes without truncation; Phase 2 JSON schema deliverables parse correctly when streamed.
- [ ] UI renders markdown lists progressively (no “flash of unformatted text” or list collapse).
- [ ] Fallback to non-streaming path functional if Ollama stream fails mid-generation.
- [ ] No regression on `test_nr2_hal_local_policy.py` or `test_hal_eval_scoring.py`.

## 5. Executive Summary (5 bullets)
- Phase 1+2 are live; quality and deliverable structure are now enforced, but 53s latency remains the primary adoption blocker.
- Phase 3 targets <2s TTFT by completing the SSE streaming pipeline started in Phase 2 (aggregation → progressive render).
- Work is localized to gateway streaming iterator and client-side incremental markdown parser; no model retraining or schema changes.
- Validation requires warm-cache TTFT testing and a 190Q subset to confirm zero regression on deliverable rate.
- After Phase 3 ships, conduct live 190Q full re-run to certify production readiness; defer Phase 4 (CARC depth) if metrics meet targets.

## 6. Approval checklist
- [ ] Confirm Ollama `/api/chat` with `stream: true` and `format: json` simultaneously supported on `hal-local:32b` Q4_K_M.
- [ ] Verify R9700 network buffers can sustain 50 concurrent SSE connections without TTFT degradation.
- [ ] Staff UX sign-off on progressive list rendering (no “jitter” during numbered step display).