# Moonshot AI — What's Next After HAL 190Q Phase 1 (CONSULT ONLY)

**Date:** 2026-07-12  
**Model:** kimi-k2.5  
**Key:** OPENROUTER_API_KEY  
**Status:** ok  
**Build:** hal-10561 + hal-local:32b  
**Prior applied:** Phase 1 (`325d24a`) + Phase 2 (`f225b2b`) + Phase 3 (`faa3113`)  
**Script:** `scripts/run_moonshot_hal_190q_whats_next.py`  
**Apply:** DO NOT APPLY until operator approves.

## Operator request (verbatim)

> next

---

# Verdict
Execute a live 190Q subset re-run to measure Phase 1–3 lift before committing engineering cycles to Phase 4.

## 0. Operator Intent (verbatim: next)

## 1. Recommended NEXT (name, why now, effort, REAL files, validation gate)
**Name:** 190Q Phase 1–3 Validation Re-run (Subset)  
**Why now:** Three consecutive constraint, structure, and latency fixes just shipped; we must validate actual quality/read-only/deliverable rate improvement on R9700 hardware before building Phase 4 (CARC whitelist hardening). If Phase 1–3 already lifted quality to ≥75% and read-only OK to ≥90%, Phase 4 priority drops; if metrics are still poor, we target Phase 4 with fresh failure logs rather than speculative code. Measurement is higher-leverage than additional engineering while the baseline is unverified.  
**Effort:** Low (ops/eval only; zero code changes).  
**REAL files:**  
- `scripts/run_moonshot_hal_190q_eval.py` (execution harness)  
- `scripts/hal_eval_scoring.py` (scoring rubric calibrated in Phase 1)  
- `NewRidgeFinancial2/apex_hal_cache_warm_pack.py` (ensure warm state before eval)  
- `NewRidgeFinancial2/nr2_hal_gateway.py` (read-only for config verification)  

**Validation gate:**  
- Run n=50 subset through `run_moonshot_hal_190q_eval.py`.  
- Compare against baseline `HAL_190Q_EVAL_2026-07-12.json` (26.3% quality, 25% read-only OK, 53s avg latency).  
- Success = quality ≥75%, read-only OK ≥90%, avg TTFT <2s, full response <45s.  
- Deliver comparison table to operator; go/no-go on Phase 4 depends on read-only OK <90% or quality <75%.

## 2. Runner-ups (2–3, why not now)
1. **Phase 4: CARC Whitelist Hardening (known-code briefs)** — Important for sparse known-code briefs, but blocked until we confirm Phase 1–3 compliance fixes didn’t already resolve the refusal patterns; building whitelist on unvalidated base risks wasted effort if the model now correctly refuses unknown codes but still fails on known-code formatting.  
2. **Apex Orchestrator Path Streaming** — Convert orchestrator JSON aggregate to progressive SSE; Phase 3 already delivered perceived TTFT wins for chat, and further latency work is lower ROI than confirming baseline quality metrics.  
3. **Full 190Q Re-run (n=190)** — Higher statistical confidence but 4× compute/RAM time on R9700; defer full run until subset proves directional improvement and no regressions.

## 3. What NOT to redo
- Do not re-apply Phase 1 (post-generation sentence constraints, write/CARC/empty≠$0 preflight, rubric recalibration).  
- Do not re-apply Phase 2 (JSON schema deliverables → numbered markdown + UI).  
- Do not re-apply Phase 3 (SSE typing/ttft meta, `X-Accel-Buffering: no`, DesktopBridge streaming, fake-typewriter skip).  
- Do not modify CARC handling logic (Phase 4) or add new HAL/Apex features until measurement validates current state.

## 4. Acceptance criteria
- Subset eval JSON generated with new timestamp (e.g., `HAL_190Q_EVAL_2026-07-13_subset.json`).  
- `hal_eval_scoring.py` reports: quality pass %, read-only OK %, deliverable rate, avg end-to-end latency, TTFT p50/p95.  
- Side-by-side comparison vs baseline (26.3% / 25% / 53s) posted for operator review.  
- Explicit go/no-go decision recorded for Phase 4 based on read-only OK rate threshold (<90% triggers Phase 4; ≥90% deprioritizes).

## 5. Executive Summary (5 bullets)
- Phases 1–3 (constraints, structured deliverables, streaming UX) just landed on `hal-local:32b` R9700.  
- Unknown if fixes moved the 190Q baseline (26.3% quality, 25% read-only OK) to production-ready levels.  
- Proposed next step is empirical measurement using existing harness, not additional code commits.  
- Outcome directly gates Phase 4 (CARC whitelist) engineering priority and resource allocation.  
- Low-risk, high-information validation that prevents over-engineering against an already-fixed baseline.

## 6. Approval checklist
- [ ] Operator confirms subset size (recommend n=50 for speed, or full n=190 if cluster idle).  
- [ ] Confirm `hal-local:32b` is warm (execute `apex_hal_cache_warm_pack.py` preflight).  
- [ ] Confirm baseline JSON `HAL_190Q_EVAL_2026-07-12.json` archived for comparison.  
- [ ] Review comparison table before proceeding to Phase 4 or stopping.