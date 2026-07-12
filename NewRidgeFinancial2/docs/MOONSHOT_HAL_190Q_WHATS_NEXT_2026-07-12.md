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
Apply **Phase 3: Streaming / TTFT UX Polish**—the latency perception layer that makes the 32B model feel interactive despite 50s+ wall-clock time.

## 0. Operator Intent (verbatim)  
`next`

## 1. Recommended NEXT  
**Phase 3: Streaming / TTFT UX Polish**  
- **Why now:** Phase 1 fixed response constraints and Phase 2 added structured deliverables, but the gateway still buffers the entire 32B completion before emitting SSE frames. Staff perceive the 50s+ wait as “frozen.” Phase 3 unblocks the UX without buying new hardware.  
- **Effort:** Medium (3–4 days). Server-side token streaming is already partially wired; needs progressive client render, abort handling, and a “thinking…” heartbeat.  
- **REAL files:**  
  - `NewRidgeFinancial2/nr2_hal_gateway.py` – `evaluate_query_stream()`: enable Ollama `stream=true` end-to-end, flush tokens every 2–4 chars, add `X-Accel-Buffering: no` header, implement `abort_id` query param to cancel pending generation.  
  - `NewRidgeFinancial2/site/hal-core.js` – `streamChat()`: switch from fetch-then-render to `EventSource` incremental DOM insertion, add early skeleton loader (blinking cursor/“HAL is typing”), and token-per-50ms throttle to avoid layout thrash.  
  - `NewRidgeFinancial2/site/hal-agent.js` – `finalizeReply()`: accept partial JSON fragments during streaming, render numbered steps as they arrive (progressive disclosure), and surface an abort button if TTFT >2s.  
  - `NewRidgeFinancial2/site/app.js` – Add `hal-streaming` CSS state class for opacity fade-in per token chunk; keep scroll-anchor on user viewport.  
- **Validation gate:**  
  1. TTFT ≤2s perceived (first token hits browser ≤2s after POST).  
  2. Smooth 20–30 tok/s visible render without jank on R9700.  
  3. Abort button cancels Ollama request within 500ms and halts SSE without page reload.  
  4. 190Q subset (n=20) still passes quality/read-only gates from Phase 1+2 (no regression).

## 2. Runner-ups  
- **Phase 4: CARC Whitelist Hardening** – Currently HAL refuses unknown CARC codes (good) but offers sparse briefs for *known* codes. Defer until Phase 3 lands because structured deliverables (Phase 2) already reduced CARC hallucinations; staff can wait 1 week for deeper ERA-835 lookup integration.  
- **Live 190Q Full Re-run** – Do not schedule until Phase 3 is applied; current latency makes the re-run painful to execute and masks UX fixes in the metrics.  
- **Second 8B Model Side-car** – Hardware budget and context-window sharding complexity exceed “local additive fix” mandate; revisit only if Phase 3 fails to meet TTFT target.

## 3. What NOT to redo  
- Do not re-implement Phase 1 constraints (sentence caps, empty≠$0) or Phase 2 JSON schema deliverables—they are shipped.  
- Do not prioritize GitHub/PR automation over local HAL gateway fixes; this package stays in-repo.  
- Do not add SoftDent write-back or QB ledger invention; policy remains read-only/consent-based.

## 4. Acceptance Criteria  
- [ ] `curl -N` against `/evaluate_query_stream` shows first byte in <2s for a 10-token warm prompt.  
- [ ] Browser DevTools Network panel: TTFB ≤2s, subsequent chunks every 50–150ms.  
- [ ] Client renders partial markdown (numbered steps) incrementally without duplicate keys.  
- [ ] Abort signal propagates to Ollama `/api/generate` cancellation (no zombie processes on R9700).  
- [ ] `scripts/run_moonshot_hal_190q_eval.py` subset (n=50) shows quality ≥85%, read-only OK = 100%, deliverable rate ≥70% (maintain Phase 1+2 gains).

## 5. Executive Summary  
- **Phase 1+2 stabilized correctness; Phase 3 stabilizes perceived speed.**  
- **Goal:** Make 32B feel like 8B by streaming tokens and rendering steps as they arrive.  
- **Risk:** Low—additive to existing SSE path, rollback is header/config toggle.  
- **Leverage:** High—53s average drops to <2s perceived TTFT, unlocking staff adoption.  
- **Blocker cleared:** Phase 2 SSE aggregation already buffers deliverables; Phase 3 just flushes earlier.

## 6. Approval Checklist  
- [ ] Operator confirms “proceed Phase 3” or equivalent.  
- [ ] R9700 Ollama `stream=true` verified working on `hal-local:32b` (no JSON mode conflict).  
- [ ] UI/UX window allocated for `hal-core.js` progressive render refactor (3 days).  
- [ ] Abort/cancellation test case added to `test_nr2_hal_local_policy.py`.  
- [ ] No new external dependencies (keep vanilla JS/EventSource).