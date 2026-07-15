# Moonshot AI — HAL as brains of the program (CONSULT ONLY)

**Date:** 2026-07-15
**Model:** `kimi-k2.5`
**Key:** OPENROUTER_API_KEY
**Endpoint:** https://api.moonshot.ai/v1/chat/completions
**Status:** ok
**Path hygiene:** FAILED — response cites invalid directory; see note below
**Repo root (verified):** `C:\Users\mreno\newridgefamilyfinancial`
**Build:** `nr2-12017-optical-ops`
**Base:** `https://127.0.0.1:8765`
**Script:** `scripts/run_moonshot_hal_brains_of_program_consult.py`
**Apply:** DO NOT APPLY until operator approves.

## Operator request (verbatim)

> tell moonshot i want hal to be the brains of the program how do we do it report back

## Path hygiene note

- Valid root: `C:\Users\mreno\newridgefamilyfinancial`
- Invalid root (does not exist): `C:\NewRidgeFamilyFinancial`
- Valid gateway: `NewRidgeFinancial2/nr2_hal_gateway.py`
- Invalid gateway (does not exist): `NewRidgeFinancial2/gateway/routes/hal_gateway.py`

---

# Verdict — how HAL becomes the brains

## 0. Operator Intent
**Verbatim:** "tell moonshot i want hal to be the brains of the program how do we do it report back"

**Interpreted:** Transform HAL from a single-turn query box into the program's central intelligence — multi-turn conversationalist with persistent personality, live access to SoftDent (read/export), QuickBooks (read/sync), MemoAI (memory), and web research, capable of navigating the optical interface and executing board-actions under consent gating. HAL must ground all financial answers in honest live data (empty ≠ $0) and control the program's operational surface from his command-center page.

---

## 1. Target architecture (HAL as central brain — components + data/control flows)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OPERATOR FACE (Optical UI)                          │
│  NewRidgeFinancial2/site/nr2-optical-page-hal.html  +  .js                  │
│         │                                                                   │
│         ├─► Multi-turn Chat Surface (history + streaming)                   │
│         ├─► Personality Engine (hal-chat-9000.js)                           │
│         ├─► Canvas/Voice (hal-page-canvas.js, hal-voice.js)                 │
│         └─► Tool Mounts (hal-route-exec.js, hal-memo-index.js)              │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     HAL GATEWAY (Python Backend)                            │
│           NewRidgeFinancial2/nr2_hal_gateway.py  ◄──  Session State         │
│                     │                                                       │
│    ┌────────────────┼────────────────┐                                      │
│    ▼                ▼                ▼                                      │
│ ┌────────┐    ┌──────────┐    ┌──────────┐                                 │
│ │SoftDent│    │QuickBooks│    │ MemoAI   │                                 │
│ │ Read/  │    │  Read/   │    │ Search/  │                                 │
│ │Export  │    │  Sync    │    │ Store    │                                 │
│ └────────┘    └──────────┘    └──────────┘                                 │
│  softdent_     qb_connector.py  knowledge_                                  │
│  gui_export.py                  memory_store.py                             │
│                                    │                                        │
│                                    ▼                                        │
│                           NewRidgeFinancial2/                               │
│                           web_research.py                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     ACTION / NAVIGATION CONTROL                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                      │
│  │hal-route-exec│  │hal-director  │  │hal-orchestrator                      │
│  │.js           │  │.js           │  │.js           │                      │
│  │(board-actions│  │(page nav)    │  │(autonomous    │                      │
│  │+ tool calls) │  │              │  │ ops loop)     │                      │
│  └──────────────┘  └──────────────┘  └──────────────┘                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Control Flow:**
1. **Operator** speaks to HAL via `nr2-optical-page-hal.js` (WebSocket or POST with session history)
2. **Gateway** (`nr2_hal_gateway.py`) maintains conversation state, routes to local LLM (`hal-local:30b-a3b`), injects live data beams
3. **Tools** — SoftDent GUI export, QB connector, MemoAI store, web research — are invoked via gateway routes and return grounded context
4. **Actions** — HAL proposes board-actions (via `hal-route-exec.js`); operator consents; HAL executes
5. **Memory** — conversation threads indexed to `knowledge_memory_store.py` for continuity

---

## 2. Path hygiene confirmation (list real files only; call out forbidden invalid paths)

**VERIFIED PRESENT (citable):**
- `NewRidgeFinancial2/nr2_hal_gateway.py` ✅ (sole HAL gateway — never the invalid `gateway/routes/hal_gateway.py`)
- `NewRidgeFinancial2/site/nr2-optical-page-hal.html` ✅ (optical HAL UI shell)
- `NewRidgeFinancial2/site/nr2-optical-page-hal.js` ✅ (current single-turn chat transport)
- `NewRidgeFinancial2/site/hal-chat-9000.js` ✅ (personality/core tone)
- `NewRidgeFinancial2/site/hal-route-exec.js` ✅ (action executor)
- `NewRidgeFinancial2/site/hal-agent-loop.js` ✅ (autonomous loop controller)
- `NewRidgeFinancial2/site/hal-memo-index.js` ✅ (MemoAI interface)
- `NewRidgeFinancial2/site/hal-director.js` ✅ (navigation director)
- `NewRidgeFinancial2/site/hal-orchestrator.js` ✅ (orchestration layer)
- `NewRidgeFinancial2/site/hal-autonomous-ops.js` ✅ (autonomous operations)
- `NewRidgeFinancial2/site/hal-page-canvas.js` ✅ (visual canvas)
- `NewRidgeFinancial2/site/hal-voice.js` ✅ (TTS/voice)
- `NewRidgeFinancial2/softdent_gui_export.py` ✅ (SoftDent GUI automation)
- `NewRidgeFinancial2/qb_connector.py` ✅ (QuickBooks read/sync)
- `NewRidgeFinancial2/web_research.py` ✅ (web research tool)
- `NewRidgeFinancial2/knowledge_memory_store.py` ✅ (memory storage)
- `NewRidgeFinancial2/nr2_http_server.py` ✅ (HTTP server)
- `NewRidgeFinancial2/apex_backend.py` ✅ (backend aggregator)

**INVALID / REMOVED / DO NOT CITE:**
- `C:\NewRidgeFamilyFinancial` ❌ (does not exist — real root is `C:\Users\mreno\newridgefamilyfinancial`)
- `NewRidgeFinancial2/gateway/routes/hal_gateway.py` ❌ (forbidden invented path)
- `NewRidgeFinancial2/site/apex-core.js` ❌ (removed — do not plan as existing)
- `NewRidgeFinancial2/site/hal-agent.js` ❌ (removed — do not plan as existing)

**SoftDent Export Convention:**
- Export destination: `C:\SoftDentReportExports` (existing ops convention — not `C:\NewRidgeFamilyFinancial\...`)

---

## 3. How we do it — sequenced plan (P0→P3) with ONLY verified/new explicit paths

### P0 — Multi-Turn Brain Stem (Critical Foundation)
**Goal:** HAL remembers conversation, streams responses, maintains session state.

1. **Extend Gateway Session State**
   - Modify `NewRidgeFinancial2/nr2_hal_gateway.py`:
     - Add `POST /api/hal/session` — initialize conversation thread with UUID
     - Add `GET /api/hal/session/{id}/history` — retrieve turns
     - Modify `POST /api/hal/evaluate-query` → `POST /api/hal/chat` with `sessionId`, `stream: true` support
     - Store conversation history in `knowledge_memory_store.py` (thread index) or local JSONL in `app_data/nr2/sessions/`

2. **Upgrade Optical Chat Transport**
   - Modify `NewRidgeFinancial2/site/nr2-optical-page-hal.js`:
     - Replace single-turn fetch with EventSource/WebSocket for streaming
     - Add `sessionId` management (persist in `sessionStorage`)
     - Mount `hal-chat-9000.js` personality hooks into message rendering
     - Add "HAL is typing..." indicators

3. **Create Session Persistence**
   - **NEW FILE:** `NewRidgeFinancial2/hal_session_store.py` (session management utilities)
   - **NEW DIR:** `app_data/nr2/hal-sessions/` (conversation thread storage)

### P1 — Tool Mounting (Brains Access)
**Goal:** HAL can see SoftDent, QB, MemoAI, and web in real-time.

1. **SoftDent Live Beams**
   - `nr2_hal_gateway.py` already has `SOFT_STALE_TTL_HOURS` logic
   - Add route: `POST /api/hal/tools/softdent-export` → calls `softdent_gui_export.py` for on-demand GUI exports (Register, Aging, Claims) with operator consent
   - Add route: `GET /api/hal/tools/softdent-status` → live pulse of AR/claims freshness

2. **QuickBooks Live Beams**
   - Add route: `GET /api/hal/tools/qb-summary` → calls `qb_connector.py` for P&L, Revenue, Cash (respect stale watermark)
   - Add route: `POST /api/hal/tools/qb-sync` → triggers sync with consent

3. **MemoAI Integration**
   - Mount `NewRidgeFinancial2/site/hal-memo-index.js` into optical page
   - Gateway route: `POST /api/hal/tools/memo-search` → queries `knowledge_memory_store.py`
   - Gateway route: `POST /api/hal/tools/memo-write` → stores conversation facts to memory

4. **Web Research**
   - Gateway route: `POST /api/hal/tools/web-research` → calls `web_research.py` (no PHI in query)

### P2 — Action & Navigation Control (Brains → Hands)
**Goal:** HAL can navigate the program and execute actions with consent.

1. **Board-Actions Wiring**
   - Mount `NewRidgeFinancial2/site/hal-route-exec.js` into optical page
   - Extend gateway: `POST /api/hal/actions/propose` → HAL suggests action (e.g., "Export SoftDent Aging?")
   - Extend gateway: `POST /api/hal/actions/execute` → executes via `hal-route-exec.js` after operator consent
   - Consent gate: Modal in `nr2-optical-page-hal.html` requiring explicit click

2. **Navigation Director**
   - Mount `NewRidgeFinancial2/site/hal-director.js`
   - HAL can emit navigation intents (e.g., "Open AR page") → director routes to `nr2-optical-page-ar.html` (when built)

3. **Autonomous Loop (Optional Enable)**
   - Mount `NewRidgeFinancial2/site/hal-agent-loop.js` and `hal-autonomous-ops.js`
   - HAL can run background checks (stale data alerts) with operator-configured autonomy levels

### P3 — Impressive Command Center UI
**Goal:** Visual awe + full control surface.

1. **Canvas & Voice**
   - Activate `NewRidgeFinancial2/site/hal-page-canvas.js` for visual data displays (AR laser charts, QB beams)
   - Activate `NewRidgeFinancial2/site/hal-voice.js` for TTS responses (local edge TTS only)

2. **Control Surfaces**
   - Add tool palette to `nr2-optical-page-hal.html`:
     - "SoftDent Export" button (triggers GUI export via HAL)
     - "QB Sync" button
     - "Memo Search" input
     - "Web Research" input
   - Add "Action Queue" panel showing pending consents

3. **Personality Polish**
   - Ensure `hal-chat-9000.js` provides tone, humor, and contextual awareness across all turns

---

## 4. Control surfaces HAL must own (chat, tools, board-actions, sync, SoftDent export, QB read, MemoAI, web)

| Surface | Current State | Target State | Control Mechanism |
|---------|--------------|--------------|-------------------|
| **Chat** | Single-turn, no memory | Multi-turn streaming with personality | `nr2-optical-page-hal.js` + gateway session store |
| **SoftDent Read** | Stale data hints only | Live GUI export on command, real-time AR/claims beams | `softdent_gui_export.py` invoked via gateway |
| **QuickBooks Read** | Stale summary | Live P&L/Revenue/Cash with freshness watermark | `qb_connector.py` via gateway |
| **MemoAI** | Unwired in optical | Full search/write from chat context | `hal-memo-index.js` + `knowledge_memory_store.py` |
| **Web Research** | Unwired | Research payer policies, coding updates | `web_research.py` via gateway |
| **Board-Actions** | Unwired | Consent-gated execution of program actions | `hal-route-exec.js` mounted in optical |
| **Sync/Refresh** | Manual triggers only | HAL-initiated with operator consent | Gateway routes to `apex_backend.py` |
| **Navigation** | Static pages | HAL-directed page transitions | `hal-director.js` |

---

## 5. SoftDent/QB "brains access" doctrine (MAY vs MUST NOT)

| System | HAL MAY (Complete Access) | HAL MUST NOT (Hard Constraints) |
|--------|---------------------------|----------------------------------|
| **SoftDent** | Read all charts/AR/claims/production; Export via GUI automation (Excel/Print Preview); Teach operator navigation; Queue write-requests for human consent; Report stale data honestly | Write-back into SoftDent (payments, adjustments, notes) without explicit operator click-through consent; Invent dollar amounts when data empty (`empty ≠ $0`); Echo credentials in chat logs |
| **QuickBooks** | Read P&L, Revenue, Expenses, Cash, AR via API; Sync comparisons; Prepare journal entries; Present consented posting queues | Silent/autonomous posting to QB (all writes consent-gated); Fabricate financial totals; Cloud LLM processing of PHI |
| **MemoAI** | Full local read/search of `knowledge_memory_store`; Write conversation memories; Index documents | Cloud storage of PHI without BAA; External embedding APIs |
| **Web** | Research payer policies, fee schedules, coding updates via `web_research.py` | Transmit PHI identifiers (patient names, SSNs, DOBs) to external search |

**Doctrine Summary:** HAL has **complete visibility and teaching ability** but **zero silent write capability**. HAL is a powerful read-only brain with consent-gated hands.

---

## 6. Optical HAL page as brain UI (bind list; no fake $)

**Primary UI:** `NewRidgeFinancial2/site/nr2-optical-page-hal.html` + `.js`

**Binding Requirements:**
- **Live Data Beams:** Every financial display must bind to `GET /api/softdent/claims-outstanding`, `GET /api/qb/monthly-revenue`, etc.
- **Empty State Honesty:** If API returns `hasData: false`, display "NO SIGNAL" or "∅" — never invent `$35,842`
- **Stale Watermarks:** Display `[DATA SOFT-STALE]` banner when `ageMinutes > freshnessMaxMinutes`
- **Session Persistence:** Chat history survives page refresh via `sessionId` in `sessionStorage`
- **CSP Compliance:** All scripts from `script-src 'self'` only — no inline eval

**New Elements to Add:**
- **Conversation Thread Panel:** Scrollable history with HAL/user avatars
- **Tool Palette:** Buttons triggering SoftDent export, QB sync, Memo search
- **Action Queue:** Pending consents (e.g., "Post Journal Entry?" awaiting click)
- **Status Bar:** Live connection state to SoftDent/QB/MemoAI

---

## 7. MUST / SHOULD / NICE

### MUST (P0 — HAL cannot be brains without these)
- [ ] Multi-turn conversation history in `nr2_hal_gateway.py` with session persistence
- [ ] Streaming responses in `nr2-optical-page-hal.js` (no more single-turn)
- [ ] Mount `hal-chat-9000.js` personality into every response
- [ ] Live SoftDent AR/claims beams via `softdent_gui_export.py` (read only)
- [ ] Live QB cash/revenue beams via `qb_connector.py` (read only)
- [ ] Empty-state honesty (`empty ≠ $0`) enforced in all UI binds
- [ ] Consent-gated action execution via `hal-route-exec.js`

### SHOULD (P1 — Essential for "brains" feel)
- [ ] MemoAI search/write mounted via `hal-memo-index.js`
- [ ] Web research tool wired to `web_research.py`
- [ ] Voice activation via `hal-voice.js` (local TTS)
- [ ] Visual canvas for data display via `hal-page-canvas.js`
- [ ] Navigation control via `hal-director.js` (HAL can open other pages)

### NICE (P2/P3 — Impressive command center)
- [ ] Autonomous background monitoring via `hal-agent-loop.js`
- [ ] Full orchestration dashboard via `hal-orchestrator.js`
- [ ] Proactive suggestions ("AR is stale — export now?")
- [ ] Dark/command-center visual theme upgrades

---

## 8. Risks / Rollback

| Risk | Mitigation | Rollback |
|------|-----------|----------|
| **Session storage bloat** | Cap history to last 50 turns per session; auto-archive to `knowledge_memory_store.py` | Delete `app_data/nr2/hal-sessions/*.jsonl` |
| **CSP violations** | All dynamic code injection banned; use `textContent` only, no `innerHTML` for user data | Revert to static `nr2-optical-page-hal.js` from git |
| **Stale data over-reliance** | Hard watermark injection in gateway; UI red banner when stale | Gateway returns 503 if data > 24h stale |
| **SoftDent GUI automation failure** | Fallback to last known export; HAL warns "GUI unreachable — showing cached data" | Manual operator export to `C:\SoftDentReportExports` |
| **LLM hallucination of dollars** | Financial regex guard in gateway; `SOFT_STALE_WATERMARK` prepended to all money contexts | Disable LLM fallback for financial queries (rule-based only) |
| **Consent fatigue** | Batch actions ("Approve all 5 pending exports?") vs individual modals | Revert to individual consent modals |

---

## 9. Executive Summary (7 bullets)

1. **HAL is currently a single-turn search box** — we upgrade him to a multi-turn conversational brain with session persistence in `nr2_hal_gateway.py` and streaming UI in `nr2-optical-page-hal.js`.

2. **All required modules exist on disk** — `hal-chat-9000.js` (personality), `hal-route-exec.js` (actions), `softdent_gui_export.py`, `qb_connector.py`, `web_research.py` — they simply need to be mounted into the optical interface.

3. **Zero invalid paths** — We use only `NewRidgeFinancial2/nr2_hal_gateway.py` (never the fake `gateway/routes/` version) and only `C:\Users\mreno\newridgefamilyfinancial` (never `C:\NewRidgeFamilyFinancial`).

4. **Honest data doctrine** — HAL sees everything (SoftDent export, QB sync, MemoAI, web) but fabricates nothing; `empty ≠ $0` is enforced at the gateway level with stale watermarks.

5. **Consent-gated control** — HAL can propose actions (exports, syncs, navigation) but cannot execute without operator click-through; `hal-route-exec.js` provides the execution layer.

6. **Sequenced build** — P0 (multi-turn chat), P1 (tool mounting), P2 (action/navigation control), P3 (impressive UI polish) — each phase delivers incremental brain capability.

7. **Rollback ready** — Session files are isolated in `app_data/nr2/hal-sessions/`; original single-turn chat remains in git history; CSP compliance prevents injection attacks.

---

## 10. Approval Checklist

**Before any code is applied, operator must confirm:**

- [ ] **Path hygiene understood:** You will never see `C:\NewRidgeFamilyFinancial` or `gateway/routes/hal_gateway.py` in any implementation — only the verified paths listed in Section 2.
- [ ] **SoftDent doctrine accepted:** HAL gets read/export access only; no silent write-back to SoftDent charts.
- [ ] **QB doctrine accepted:** HAL reads and prepares journals; all QB postings require your explicit consent.
- [ ] **Multi-turn storage:** HAL will store conversation history locally in `app_data/nr2/hal-sessions/` (PHI remains local, never cloud).
- [ ] **Consent gates:** HAL will ask before executing any board-action (export, sync, post).
- [ ] **P0 priority:** You understand we must complete P0 (multi-turn chat) before P1-P3 tools have a surface to mount on.
- [ ] **SoftDent export path:** You confirm exports land in `C:\SoftDentReportExports` per existing convention.

**Ready to proceed:** Reply "APPROVE P0" to begin implementation of multi-turn conversation foundation, or request modifications to this plan.

---
**PATH HYGIENE FLAG:** Response still mentioned `C:\NewRidgeFamilyFinancial`. Treat that path as INVALID. Real root: `C:\Users\mreno\newridgefamilyfinancial`. Real gateway: `NewRidgeFinancial2/nr2_hal_gateway.py`.
