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
Apply **Phase 3 — Streaming TTFT UX Polish** (perceived-latency reduction via progressive SSE token streaming and skeletal UI states) to address the remaining ~53s average response blocker before any full 190Q re-run.

## 0. Operator Intent (verbatim)
next

## 1. Recommended NEXT (name, why now, effort, REAL files, validation gate)
**Name:** Phase 3 — Streaming TTFT UX Polish (Perceived Latency Mitigation)  
**Why now:** Phase 1 (constraints) and Phase 2 (structured deliverables) are live; the 190Q report identified ~53s average latency as the primary UX blocker for staff workflows. True token-by-token streaming with skeletal loading states will drop TTFT under 2s—required for production release—without loading a second 8B model on the R9700.  
**Effort:** Medium (3–4 days) — modifies gateway streaming loop and client progressive renderer.  
**REAL files:**  
- `NewRidgeFinancial2/nr2_hal_gateway.py` — refactor `evaluate_query_stream` to emit SSE frames on first token arrival (not after full generation); add `stream_options` seeding for deterministic low-latency path.  
- `NewRidgeFinancial2/site/hal-core.js` — add `startStreamingState()` skeletal placeholder and `appendTokenChunk()` progressive markdown renderer.  
- `NewRidgeFinancial2/site/hal-agent.js` — manage streaming lifecycle flags (`isStreaming`, `abortController`).  
- `NewRidgeFinancial2/site/app.js` — TTFT timer, early bubble render, shimmer CSS hooks.  
**Validation gate:** TTFT <2s measured from POST to first SSE `data:` frame on hal-local:32b Q4_K_M; 190Q subset (n=20) shows >80% “perceived latency acceptable” with no regression in Phase 2 numbered-list formatting.

## 2. Runner-ups (2–3, why not now)
1. **Live Full 190Q Re-run** — *Why not now:* Measurement should follow the latency fix; re-running now would only re-confirm the 53s baseline. Execute after Phase 3 to validate the complete stack.  
2. **Phase 4 — CARC Whitelist Hardening** — *Why not now:* Current unknown-code refusal works (Phase 1); sparse known-code briefs are lower leverage than TTFT. Batch with future ERA 835 depth work.  
3. **REC-010 Voice Context Carry Optimization** — *Why not now:* Enhancement territory; 190Q blocker is text latency, not voice continuity.

## 3. What NOT to redo
- Do **not** re-apply Phase 1 sentence-cap/plain-language filters or Phase 2 JSON schema/deliverable logic—already live at `325d24a` and `f225b2b`.  
- Do **not** implement SoftDent write-back or QB ledger invention—policy remains read-only/empty≠$0 per Phase 1.  
- Do **not** load a sidecar 8B model beside hal-local:32b—R9700 VRAM optimization prefers single-model streaming tuning.

## 4. Acceptance criteria
- TTFT (time to first token) ≤2 seconds on R9700 + hal-local:32b Q4_K_M for short asks (≤2 sentences).  
- UI renders skeletal/shimmer state immediately on submit, then progressive text (no “blank wait → full dump”).  
- Deliverable queries (steps/caution) still render numbered lists correctly while streaming.  
- 190Q subset (n=20) re-run shows ≥80% “perceived latency acceptable” rubric scores.  
- No increase in false-positive CARC invention or PHI leakage vs. Phase 1 baseline.

## 5. Executive Summary (5 bullets)
- Phase 1 and 2 addressed quality and formatting; latency (~53s avg) is the last major 190Q blocker.  
- Phase 3 switches SSE from aggregate-then-emit (Phase 2) to true token streaming with skeletal UI masking.  
- Targets TTFT <2s without adding a second model, optimizing hal-local:32b Q4_K_M on R9700.  
- Client-side progressive rendering ensures staff see immediate feedback, improving perceived performance even if total generation time remains >10s for complex queries.  
- Validation via TTFT timer and 190Q subset precedes the optional full 190Q re-run.

## 6. Approval checklist
- [ ] Confirm Ollama version on R9700 supports low-latency `stream` with `options` seed/temperature for deterministic TTFT.  
- [ ] Verify client SSE parser handles partial markdown chunks without breaking Phase 2 numbered-list aggregation.  
- [ ] Staging environment available for TTFT measurement (stopwatch + network tab).  
- [ ] Operator accepts 3–4 day effort window vs. immediate measurement.  
- [ ] Backup commit `f225b2b` tagged before gateway streaming loop modifications.