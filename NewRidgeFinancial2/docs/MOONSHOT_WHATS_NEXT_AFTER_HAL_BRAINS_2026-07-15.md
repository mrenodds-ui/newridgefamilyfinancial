# Moonshot AI — What's Next After HAL Brains (CONSULT ONLY)

**Date:** 2026-07-15
**Model:** `kimi-k2.5`
**Key:** OPENROUTER_API_KEY
**Status:** ok
**Path hygiene:** mentions `gateway/routes/hal_gateway` (verify as forbid-list only)
**Repo root:** `C:\Users\mreno\newridgefamilyfinancial`
**Prior:** `28738a9` / `nr2-12018-hal-brains`
**Script:** `scripts/run_moonshot_whats_next_after_hal_brains_consult.py`
**Apply:** DO NOT APPLY until operator approves.

## Operator request (verbatim)

> next

---

# Verdict
Browser smoke + fix: prove multi-turn `/api/hal/chat` + tools + consent on live 8765, resolving the 404/403 route failures that currently block HAL from being reachable despite the nr2-12018-hal-brains build being present on disk.

## 0. Operator Intent (verbatim)
next

## 1. Recommended NEXT (name, why now, effort, REAL files/ops, validation gate)
**Package:** Browser smoke + route-fix for HAL brains P0–P3 live viability  
**Why now:** The LIVE AUDIT shows the nr2-12018-hal-brains build files exist (`hal_session_store.py`, `hal_brain_tools.py`), yet the actual endpoints return `HTTP 404` (`softdentStatus`, `qbSummary`, `actionsPending`) and `HTTP 403` (`sessionCreate`). HAL cannot be the "brains of the program" if the operator cannot create a session or invoke tools. This is the critical path blocker before any daily-ops value can be realized.  
**Effort:** Low–Medium (likely missing route registration in `nr2_http_server.py` or stale server process; 1–2 hours to smoke, diagnose, and patch).  
**REAL files/ops:**
- `C:\Users\mreno\newridgefamilyfinancial\NewRidgeFinancial2\nr2_http_server.py` — verify `POST /api/hal/session`, `POST /api/hal/chat`, `GET /api/hal/tools/softdent-status`, `GET /api/hal/tools/qb-summary`, and consent-gated `POST` routes are registered and not returning 403/404.
- `C:\Users\mreno\newridgefamilyfinancial\NewRidgeFinancial2\hal_session_store.py` — ensure file-I/O permissions allow session creation in `app_data/nr2/hal-sessions/`.
- `C:\Users\mreno\newridgefamilyfinancial\NewRidgeFinancial2\hal_brain_tools.py` — verify tool handlers are imported and bound.
- `C:\Users\mreno\newridgefamilyfinancial\NewRidgeFinancial2\site\nr2-optical-page-hal.html` + `.js` — confirm browser is targeting the correct `/api/hal/*` paths (not legacy `/api/apex/hal/*`).
- `C:\Users\mreno\newridgefamilyfinancial\app_data\nr2\hal-sessions\` — validate writeable and sessions persist.
**Validation gate:**
- `curl -X POST http://192.168.50.244:8765/api/hal/session` returns `200` with JSON `{session_id: "<uuid>"}` (currently 403).
- `curl -N -X POST http://192.168.50.244:8765/api/hal/chat -H "Content-Type: application/json" -d '{"session_id":"<uuid>","messages":[{"role":"user","content":"ping"}],"stream":true}'` returns SSE stream with tokens (currently 404).
- `curl http://192.168.50.244:8765/api/hal/tools/softdent-status` returns JSON status (currently 404).
- Browser optical page opens consent modal on gated tool invocation (e.g., SoftDent export) and completes without error.

## 2. Why this beats the other candidates now
- **HAL money honesty (Candidate 2):** Cannot harden money honesty if the chat endpoint is unreachable (404). Wiring must precede data-integrity enforcement.
- **SoftDent GUI export (Candidate 3):** Depends on `hal_brain_tools.py` routes being live; currently 404. Export is useless if the consent gate cannot be triggered.
- **Reconciliation honesty (Candidate 5):** Recon remains dead per prior context, but HAL is the new primary interface. If HAL is unreachable, fixing recon does not unblock daily ops.
- **Optical subpage binding (Candidate 4):** Subpages are secondary to the HAL command center; HAL must work first.
- **Board-actions navigate (Candidate 6):** Depends on session and actions endpoints (currently 403/404).

## 3. Runner-ups (2–3)
1. **HAL money honesty gate hardening (Candidate 2)** — Implement strict "empty ≠ $0" enforcement and beam-verification in `hal_brain_tools.py` and chat context to prevent HAL from inventing currency. *Run this immediately after smoke-fix confirms endpoints are reachable.*
2. **Kill/cure reconciliation honesty (Candidate 5)** — Replace the dead `apex_reconciliation_pack` (500/UNAVAILABLE) with an honest "NO SIGNAL" beam or repair the reconciliation query. *Important for functionability %, but HAL is the new ops surface.*
3. **SoftDent GUI export end-to-end (Candidate 3)** — Wire the consent-gated `POST /api/hal/tools/softdent-export` through to `softdent_gui_export.py`, trigger Excel export, and auto-import refresh. *High daily-ops value, but blocked by current 404 on tool routes.*

## 4. What NOT to redo
- **HAL brains P0–P3 greenfield:** The consult specified the architecture; the code files exist. Do not rewrite the session store or tool design—just wire them so they respond 200 instead of 404/403.
- **SoftDent write-back:** Remains forbidden; this package is read/export only.
- **Fake currency on shells:** Do not populate empty beams with `$0` or mock values; maintain `empty ≠ $0` honesty.
- **Invalid paths:** Do not create `C:\NewRidgeFamilyFinancial` or `NewRidgeFinancial2/gateway/routes/hal_gateway.py`. Stay under `C:\Users\mreno\newridgefamilyfinancial` and use `NewRidgeFinancial2/nr2_hal_gateway.py` only if needed for routing (currently not present; use `nr2_http_server.py`).
- **Restore deleted apex-core as primary:** HAL is the primary interface; do not revert to legacy Apex SPA.

## 5. Acceptance criteria
- [ ] Live `POST /api/hal/session` returns 200 with valid UUID (not 403).
- [ ] Live `POST /api/hal/chat` accepts multi-turn JSON and streams SSE tokens end-to-end (not 404).
- [ ] Live `GET /api/hal/tools/softdent-status` and `qb-summary` return current data or honest empty-state (not 404).
- [ ] Consent modal renders in browser when invoking gated tools (export/sync) and proceeds only after operator confirmation.
- [ ] Session files (`.jsonl`) appear in `app_data/nr2/hal-sessions/` after chat turns.
- [ ] Asset version reported by live app advances from `nr2-12017-optical-ops` to `nr2-12018-hal-brains` (or server restart confirms new routes loaded).

## 6. Executive Summary (5 bullets)
- **HAL is shipped but unreachable:** Build nr2-12018-hal-brains files exist, yet LIVE AUDIT shows 404/403 on critical `/api/hal/*` endpoints, rendering HAL non-functional.
- **Wiring blocker over data blocker:** Without route registration or server restart to load new routes, no HAL-dependent feature (chat, tools, consent) can operate; this is the priority CODE fix.
- **Unblocks entire P0–P3 investment:** Fixing smoke test failures activates the multi-turn chat, session memory, SoftDent/QB tool palette, and consent gating already developed.
- **Prerequisite for honesty hardening:** Money honesty enforcement (Candidate 2) requires a working chat endpoint to validate against; smoke test must pass first.
- **Low risk, high leverage:** Likely requires adding route handlers to `nr2_http_server.py` or restarting the Python process to pick up new imports—minimal code change, maximal functionability gain.

## 7. Approval Checklist
- [ ] Confirm smoke test plan targets the specific failing endpoints from LIVE AUDIT (`sessionCreate`, `softdentStatus`, `qbSummary`, `actionsPending`).
- [ ] Verify target files exist under `C:\Users\mreno\newridgefamilyfinancial\NewRidgeFinancial2\` (not invalid root).
- [ ] Ensure no `gateway/routes/` path pollution; route directly in `nr2_http_server.py` or `nr2_hal_gateway.py` at valid root only.
- [ ] Validate that 403 on session is not a CSP `script-src` issue in `nr2_browser_security.py` (check exemptions).
- [ ] Confirm acceptance criteria are measurable via browser dev tools and `curl` against `http://192.168.50.244:8765`.
