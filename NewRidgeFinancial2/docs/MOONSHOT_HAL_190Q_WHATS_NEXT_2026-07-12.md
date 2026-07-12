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
Deploy **Phase 3 — Streaming TTFT UX Polish** to cut perceived latency to <2 s time-to-first-token and enable progressive word-by-word render, completing the latency-perception stack after Phase 1 constraints and Phase 2 structured deliverables.

## 0. Operator Intent (verbatim)
next

## 1. Recommended NEXT (name, why now, effort, REAL files, validation gate)

**Phase 3 — Streaming TTFT UX Polish**

- **Why now:** Phase 1 capped short-ask `num_predict` and Phase 2 added SSE aggregation for deliverables, yet the 190Q baseline still averaged ~53 s because the client waits for full frames and the gateway buffers too aggressively. This is the last major 190Q blocker before a re-run can credibly claim victory on latency.
- **Effort:** Medium (2–3 days). Server-side flush tuning plus client-side progressive render; no new infrastructure.
- **REAL files:**
  - `NewRidgeFinancial2/nr2_hal_gateway.py` — `evaluate_query_sse_frames`: switch from sentence-level aggregation to token-level flush with `flush=True` on first non-empty chunk; respect `num_predict` caps already in place.
  - `NewRidgeFinancial2/site/hal-core.js` — Add `streamBuffer` to paint tokens as they arrive instead of waiting for `</frame>`; implement `typewriter` CSS class for progressive reveal.
  - `NewRidgeFinancial2/site/hal-agent.js` — `renderStructuredDeliverable`: populate `<ol>` incrementally as JSON steps stream in (append `<li>` per token chunk rather than full re-render).
  - `NewRidgeFinancial2/site/apex-core.js` — Skeleton “HAL is typing…” placeholder that disappears on first token, satisfying TTFT perception.
- **Validation gate:**
  1. Short ask (“What is ERA?”) TTFT ≤ 2 s (R9700 local, warm model).
  2. Deliverable ask (“Steps to reconcile deposits”) shows first numbered step within 3 s and subsequent steps appear progressively without “chunky” jumps.
  3. 190Q subset (n=20) perceived latency mean drops from 53 s to <15 s (measure via `scripts/run_moonshot_hal_190q_eval.py` timer).

## 2. Runner-ups (2–3, why not now)

1. **Phase 4 — CARC Whitelist Hardening**  
   *Why not now:* Unknown CARC codes already hard-refuse per Phase 1; adding briefs for known codes is additive polish, whereas latency is the active pain point blocking staff workflows.

2. **Live 190Q Full Re-run**  
   *Why not now:* Measurement is premature. Run the eval **after** Phase 3 lands so the TTFT fix is captured in the quality/latency metrics; otherwise we re-measure the same 53 s baseline.

3. **Apex Narrative Batch Auto-Commit**  
   *Why not now:* REC-008 (RECENTLY SHIPPED) already covers batch narratives; further changes risk destabilizing the just-delivered ERA pipeline before HAL UX is sealed.

## 3. What NOT to redo

- Do **not** re-implement JSON schema / numbered markdown normalization (Phase 2 just shipped this).
- Do **not** re-implement sentence-cap regex or `num_predict` short-ask caps (Phase 1).
- Do **not** load a second 8 B model beside `hal-local:32b`; Q4_K_M on R9700 is sufficient with streaming tweaks.
- Do **not** invent new file paths (e.g., `hal_stream_utils.py`); keep changes inside the listed real paths.

## 4. Acceptance criteria

- [ ] Gateway SSE emits first token chunk within 2 s for queries with `num_predict ≤ 64`.
- [ ] Client renders text progressively (word-by-word) without waiting for full sentence/frame boundaries.
- [ ] Deliverable steps stream into the numbered list as JSON tokens arrive; final DOM matches Phase 2 structure.
- [ ] No regression on Phase 2 deliverable rate (>70 %) or Phase 1 constraint compliance (sentence caps).
- [ ] 190Q subset latency metric improves ≥ 50 % vs. pre-Phase‑3 baseline.

## 5. Executive Summary (5 bullets)

- Phase 1 enforced brevity and Phase 2 enforced structure; latency is the remaining 190Q blocker.
- Phase 3 keeps existing SSE plumbing but switches to token-level flush and progressive client render.
- Targets <2 s TTFT for short asks and smooth streaming for long deliverables on R9700.
- Touches only confirmed real paths: `nr2_hal_gateway.py`, `hal-core.js`, `hal-agent.js`, `apex-core.js`.
- Sets the stage for a credible full 190Q re-run that can declare the HAL 190Q fix complete.

## 6. Approval checklist

- [ ] Operator confirms <2 s TTFT target is acceptable for `hal-local:32b` Q4_K_M on R9700.
- [ ] UI/UX approves progressive “typewriter” render over current aggregate-then-fade behavior.
- [ ] No new file creation required (all edits within existing repo paths).
- [ ] Ready to execute 190Q subset re-run immediately after commit to validate latency lift.