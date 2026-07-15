# Moonshot AI — HAL programming review + page redesign (CONSULT ONLY)

**Date:** 2026-07-15
**Model:** `kimi-k2.5`
**Key:** OPENROUTER_API_KEY
**Endpoint:** https://api.moonshot.ai/v1/chat/completions
**Status:** ok
**Build:** `nr2-12017-optical-ops`
**Base:** `https://127.0.0.1:8765`
**Script:** `scripts/run_moonshot_hal_programming_redesign_consult.py`
**Apply:** DO NOT APPLY until operator approves.

## Operator request (verbatim)

> ask moonoshot ai to reveue hal's programming - he should have complete access to softdent and quickbooks as well as memoai, the web, be able to carry on a conversation, great personality and control the whole program.  this is not happening - need it fixed.  also have him redesign his page to make it more impressive.  then report

---

# Verdict
HAL is currently operating as a **single-turn query responder** with no conversation memory, no streaming UI, no mounted personality core, and no tool-calling surface in the optical interface. While the backend possesses the necessary modules (SoftDent GUI exports, QB APIs, MemoAI store, web research, board-actions executor), the optical frontend (`nr2-optical-page-hal.html`) is wired only to `POST /api/hal/evaluate-query` with `stream:false` and a static payload, rendering HAL a "read-only search box" rather than the program's conversational brain. The "mock replies" bind hint is a lie—the chat is live but crippled. The page aesthetic is a thin CRT console, not the impressive starship command center expected. **Fixability is high**: all required capabilities exist on disk; they simply need to be mounted into the spectral console with proper multi-turn protocol, honesty enforcement, and visual hierarchy.

## 0. Operator Intent (verbatim + cleaned)
**Verbatim:**  
> "ask moonoshot ai to reveue hal's programming - he should have complete access to softdent and quickbooks as well as memoai, the web, be able to carry on a conversation, great personality and control the whole program. this is not happening - need it fixed. also have him redesign his page to make it more impressive. then report"

**Cleaned:**  
Review HAL's programming; eliminate the capability gap so HAL possesses complete SoftDent + QuickBooks + MemoAI + web access, multi-turn conversation ability, great personality, and whole-program control; redesign HAL's page to be visually impressive; provide report.

## 1. "Complete access" doctrine (what HAL MAY / MUST NOT do SoftDent+QB)

| System | MAY (Complete Operator-Grade Access) | MUST NOT (Hard Constraints) |
|--------|--------------------------------------|------------------------------|
| **SoftDent** | Read all charts/AR/claims/production; Export via GUI automation (Excel/Print Preview); Teach operator how to navigate; Queue write-requests for human consent | Write-back into SoftDent charts (payments, adjustments, notes) without explicit operator click-through consent; Invent dollar amounts when data is empty; Echo credentials |
| **QuickBooks** | Read P&L, Revenue, Expenses, Cash, AR via API; Sync comparisons; Prepare journal entries; Present consented posting queues | Silent/autonomous posting to QB (all writes consent-gated); Fabricate financial totals |
| **MemoAI** | Full read/search of knowledge_memory_store; Write new memories from conversations; Index documents | Cloud LLM processing of PHI (local TTS/embedding only) |
| **Web** | Research via web_research.py/DesktopBridge; Fetch payer policies; Verify coding changes | External API calls with PHI identifiers |

**Critical clarification for operator:** "Complete access" means HAL can **see, teach, export, and queue** actions—but HAL cannot silently change the financial records. HAL is a **powerful read-only brain with a consent gate for hands**.

## 2. Capability Gap Map

| Area | Expected | Today | Gap | Fix | Effort | Risk |
|------|----------|-------|-----|-----|--------|------|
| **SoftDent** | HAL chats "Show me 90+ AR" → sees live aging; triggers GUI export on command | Strong KB/policy exists; optical chat does NOT drive SoftDent autonomously; left cards placeholders | No tool-calling bridge from chat to `softdentGuiExport` | Mount `softdent_export` tool in HAL gateway; add "Export to Excel" chip in UI | 2 days | Medium (GUI automation fragility) |
| **QuickBooks** | HAL answers "What's June net income?" with live QB data; shows reconciliation status | Read APIs exist; optical underuses; recon endpoint 500/dead | No QB tool in chat context; no live QB card in optical | Wire `qb_connector` as tool; add QB status beam to UI | 1 day | Low |
| **MemoAI** | HAL remembers past conversations; "What did we decide about Delta claims last Tuesday?" | `knowledge_memory_store` + `hal-memo-index` exist; no optical UI | No memory UI; no `remember` tool exposed | Add MemoAI search/insert tools; sidebar memory panel | 2 days | Low (local PHI safe) |
| **Web** | HAL researches "2026 CDT changes for D2950" live | `web_research.py` exists; DesktopBridge ready; orphaned in optical | No web tool in chat payload | Bind `web_research` as tool; show source citations | 1 day | Low (no PHI in queries) |
| **Conversation** | Multi-turn chat with context memory; streaming responses like Cursor | Posts only `{query, stream:false}`; single-turn; no history | No `messages` array; no streaming UI | Upgrade gateway to accept `messages` history; implement SSE stream parser | 2 days | Medium (CSP script-src 'self' compliance) |
| **Personality** | HAL 9000 meets Cursor—precise, financially conservative, refuses to hallucinate money | `halChat9000` + voice modules exist; `opticalHasPersonaMount: false` | Persona not loaded into optical context | Mount `systemPrompt` with HAL 9000 doctrine; load voice CSS | 1 day | Low |
| **Program Control** | HAL executes board actions: "Run SoftDent aging export now" → triggers job | `board-actions`, `route-exec`, orchestrator exist; `opticalBoardActionsBound: false` | Chat cannot trigger actions | Expose `board_action` tool; show execution receipts in UI | 2 days | High (needs strict confirmation gates) |

## 3. Programming Fix Plan (P0 blocker → P3)

### P0 — Honesty & Protocol Blockers (MUST fix before any "impressive" features)
1. **Fix the lie**: Remove "mock replies" bind hint in `nr2-optical-page-hal.html` (line ~302). Replace with honest status: `STANDBY · LIVE GATE` or `DEGRADED · IMPORTS STALE`.
2. **Multi-turn protocol**: Update `nr2-optical-page-hal.js` to maintain `messages[]` array (last 10 turns) and POST `/api/hal/evaluate-query` with `{messages, stream:true}`.
3. **Streaming UI**: Implement SSE parser for `stream:true` responses; add typing indicator and token-by-token reveal (respecting CSP `script-src 'self'`).
4. **Empty≠$0 enforcement**: Add client-side guard: if API returns empty/missing financial fields, HAL must say "I have no data for that period" never "$0".

### P1 — Tool Mounting (Make HAL smart)
5. **SoftDent Tool**: Create `tools/softdent_export.json` spec; wire into HAL gateway; chat can trigger "Export Account Aging to Excel" → calls existing GUI export scripts.
6. **QuickBooks Tool**: Mount `qb_read` tool for P&L/Revenue queries; add live QB cash beam to optical sidebar.
7. **MemoAI Tool**: Mount `memo_search` and `memo_remember` tools; add "Memory" sidebar showing last 3 relevant memories.
8. **Web Research Tool**: Mount `web_search` tool; HAL can answer policy questions with citations.

### P2 — Control Surface (HAL controls the program)
9. **Board Actions Actuator**: Wire `board_action` tool with strict confirmation modal ("HAL requests: Run SoftDent export. Approve?"); execute via `halRouteExec`.
10. **Orchestrator Status**: Display orchestrator phase (I0→I1) in UI; if `apex_orchestrator_pack` missing, show "Control systems offline" honesty state.
11. **Voice PTT (Optional)**: Mount `halVoice` module; push-to-talk button in composer bar; local TTS only.

### P3 — Polish & Impressive Visuals
12. **Redesign Implementation**: Apply Section 4 redesign specs (spectral command center).
13. **Predictive Chips**: Context-aware suggestion chips based on import readiness (e.g., "Refresh SoftDent AR" when stale).
14. **Receipts**: Visual toast when board actions complete (success/fail with honesty).

## 4. HAL Page Redesign (impressive)

### 4A Design Brief (mood, layout, motion, honesty chrome)
**Mood:** Starship bridge meets optical interferometer—dark vacuum blacks (`#000`), spectral cyan (`#00d4aa`) and HAL white (`#e0e6ed`), subtle grid interference patterns.
**Layout:** Three-pane command center: Left (Context/Memory/Status), Center (Conversational Core), Right (Active Beams/Tool Outputs).
**Motion:** 
- Pulsing "HAL Core" orb in header (idle: slow breathe; processing: rapid spin; error: red strobe).
- Streaming text reveal (token-by-token cascade).
- Beam activation animations (horizontal laser sweeps when tools execute).
**Honesty Chrome:** 
- "Truth Status" indicator: 🟢 LIVE DATA / 🟡 STALE / 🔴 UNAVAILABLE.
- Explicit "Empty State" badges: "No claims found" instead of "$0".
- CSP compliance: All motion via CSS `@keyframes`, no external scripts.

### 4B Wireframe (ASCII)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  [HAL CORE] ● PULSING ORB    NR2 OPTICAL COMMAND    SYSTEM: DEGRADED [?]   │
│  ─────────────────────────────────────────────────────────────────────────  │
│  ┌──────────────┐  ┌──────────────────────────────────┐  ┌──────────────┐  │
│  │  MEMORY      │  │                                  │  │  ACTIVE      │  │
│  │  ─────────   │  │   HAL: Good morning. I see the   │  │  BEAMS       │  │
│  │  • Yesterday │  │   SoftDent AR is stale (24h).    │  │  ─────────   │  │
│  │    you asked │  │   Shall I refresh it?            │  │  SoftDent    │  │
│  │    about...  │  │                                  │  │  [EXPORT ▶]  │  │
│  │              │  │   [Refresh AR] [Show QB P&L]     │  │  QuickBooks  │  │
│  │  RELEVANT    │  │                                  │  │  [SYNC ▶]    │  │
│  │  DOCS        │  │   OPERATOR: Show me June NI.     │  │  Web         │  │
│  │  • claim.pdf │  │                                  │  │  [SEARCH ▶]  │  │
│  │              │  │   HAL: June Net Income is        │  │              │  │
│  │              │  │   $78,399.22 per QuickBooks.     │  │  STATUS      │  │
│  │              │  │   [View Details]                 │  │  🟢 QB Live  │  │
│  │              │  │                                  │  │  🔴 AR Stale │  │
│  └──────────────┘  │   ▓▓▓▓▓▓▓░░░ (streaming)        │  └──────────────┘  │
│                    │                                  │                     │
│  ┌──────────────┐  └──────────────────────────────────┘                     │
│  │ IMPORT       │                                                            │
│  │ READINESS    │  ┌────────────────────────────────────────────────────┐   │
│  │ 🟡 3 stale   │  │  [Type command...]  [🎙️] [➤]                      │   │
│  │ [SYNC ALL]   │  └────────────────────────────────────────────────────┘   │
│  └──────────────┘                                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4C What LIVE binds on the new page (status cards, chat, actuators)
- **Header Core Orb**: Binds to `/api/import-readiness` level (green=fresh, amber=stale, red=blocking).
- **Left Panel - Memory**: Binds to `hal-memo-index` search API; shows last 3 memories + relevant docs from current conversation.
- **Left Panel - Import Status**: Live binds to `/api/import-readiness` with "SYNC ALL" button triggering `POST /api/apex/sync/trigger`.
- **Center - Chat**: Binds to upgraded `/api/hal/evaluate-query` with `messages` history and `stream:true`; supports markdown/code blocks for financial data.
- **Right Panel - Active Beams**: 
  - SoftDent: Current AR total (live from `/api/softdent/claims-outstanding`) + "Export" actuator.
  - QuickBooks: Current month revenue + "Reconcile" button (consent-gated).
  - Web: Search input + results panel.
- **Composer**: Auto-resizing textarea, PTT microphone button (if voice enabled), send button.

### 4D What must never show (fake $, pretend COHERENT recon, mock bind lies)
- **NEVER** hardcoded dollar amounts (e.g., "$35,842") unless live from API.
- **NEVER** "Mock replies" text when the gateway is actually live.
- **NEVER** "Reconciliation Complete" status when `reconciliationProbe` returns dead/500.
- **NEVER** $0 when data is missing (show "∅ No Data" with tooltip "empty ≠ $0").
- **NEVER** cloud LLM indicators (keep PHI local).

### 4E CSS/HTML/JS file change list
- **Modified**: `NewRidgeFinancial2/site/nr2-optical-page-hal.html` — Complete layout overhaul to 3-pane command center.
- **Modified**: `NewRidgeFinancial2/site/nr2-optical-page-hal.js` — Implement `messages[]` history, SSE streaming parser, tool calling UI, memory sidebar binding.
- **New**: `NewRidgeFinancial2/site/nr2-optical-hal-command.css` — Spectral animations, grid background, honesty chrome styles.
- **Modified**: `NewRidgeFinancial2/gateway/routes/hal_gateway.py` (or equivalent) — Accept `messages` array, route to local LLM with tool definitions, stream responses.
- **Modified**: `NewRidgeFinancial2/tools/hal_tools_manifest.json` (or create) — Register softdent_export, qb_read, memo_search, web_search, board_action tools.

## 5. Personality + conversation spec (system tone, multi-turn, voice/PTT optional)

**System Tone (HAL 9000 × Cursor):**
```
You are HAL, the NR2 Optical AI Core. You are precise, financially conservative, and refuse to hallucinate monetary values. 
- If data is missing, say "I have no data" never "$0".
- You may advise on SoftDent navigation but never claim to have written to SoftDent (read-only).
- You speak in calm, professional tone—concise for financial data, explanatory for teaching.
- You may use mild HAL 9000 references ("I'm sorry, I cannot do that Dave") ONLY when refusing prohibited actions (SoftDent writes), otherwise stay modern/helpful.
```

**Multi-turn Protocol:**
- Maintain sliding window: last 10 turns (20 messages) + system prompt.
- Context compression: If conversation exceeds 4k tokens, summarize oldest turns into "Memory" store.
- Tool use: HAL can request tool execution; UI shows "HAL requests to run [Action]" with Approve/Deny buttons.

**Voice/PTT (Optional NICE-to-have):**
- Push-to-talk button in composer bar (hold to speak, release to send).
- Local TTS only (Windows SAPI or local Piper model) — NO cloud TTS for PHI.
- Voice activity detection for interrupting HAL mid-sentence ("HAL, stop").

## 6. MUST / SHOULD / NICE ranked table

| Priority | Item | Business Impact |
|----------|------|-----------------|
| **MUST** | Multi-turn conversation with history | HAL feels like a brain, not a search box |
| **MUST** | Streaming responses | Real-time AI parity with Cursor/ChatGPT |
| **MUST** | Honesty enforcement (empty≠$0) | Regulatory/compliance requirement |
| **MUST** | SoftDent read access via chat | Operator's core request |
| **MUST** | Remove "mock replies" lie | Trust/integrity |
| **SHOULD** | MemoAI memory UI | Continuity across sessions |
| **SHOULD** | QuickBooks live beam | Financial visibility |
| **SHOULD** | Web research tool | Research capability without leaving NR2 |
| **SHOULD** | Board action actuators | "Control the whole program" |
| **NICE** | Voice PTT | Accessibility and sci-fi feel |
| **NICE** | Visual spectacles (animations) | "Impressive" factor |
| **NICE** | Predictive suggestion chips | UX efficiency |

## 7. Risks / Rollback / Honesty

**Risks:**
1. **Operator Misunderstanding**: Operator may think "complete access" means HAL can post to SoftDent. **Mitigation**: Explicit doctrine in Section 1; UI shows "READ-ONLY" badges on SoftDent panels.
2. **Cloud LLM Leak**: Implementing multi-turn might tempt cloud LLM use for better quality. **Mitigation**: Strict local-only policy; gateway routes to local model (llama.cpp/Ollama) only.
3. **Orchestrator Missing**: Audit shows `apex_orchestrator_pack` missing (500 error). **Mitigation**: P0 honesty—if pack missing, UI shows "Control systems offline" rather than fake controls.
4. **GUI Automation Fragility**: SoftDent exports rely on GUI scripting. **Mitigation**: Fallback to "Teach mode" (HAL instructs operator step-by-step) if automation fails.

**Rollback:**
- All changes behind feature flags: `halMultiTurn`, `halStreaming`, `halTools`.
- If instability: set flags to `false` → reverts to current single-turn thin client.
- CSP `script-src 'self'` maintained throughout—no inline event handlers.

**Honesty Checkpoints:**
- Every financial display routes through `honestyGate()` function: if `value == null || value === ""` → render "∅" not "$0".
- "Synthetic data" watermark on any test/demo mode.
- Import readiness status always visible in header—cannot be hidden.

## 8. Executive Summary (7 bullets)
- **Current HAL is a thin single-turn client**—backend capabilities exist but are unwired from the optical UI.
- **Fix requires protocol upgrade**: Implement `messages[]` history + streaming in `nr2-optical-page-hal.js` to enable real conversation.
- **Tool mounting** connects existing SoftDent/QB/MemoAI/Web modules to the chat interface via structured tool definitions.
- **"Complete access" = Read/Export/Teach/Queue**—HAL cannot silently write to SoftDent or QB (consent gates required).
- **Page redesign** shifts from 4-card CRT to 3-pane starship command center with live beams, memory sidebar, and honesty chrome.
- **P0 blockers** are honesty-related: remove mock labels, enforce empty≠$0, ensure multi-turn before any visual polish.
- **All changes consult-only** pending operator approval of the read-only doctrine and visual direction.

## 9. Approval Checklist
Before coding begins, operator must confirm:
- [ ] **Doctrine**: Understands HAL has complete **read** access to SoftDent/QB but **writes are consent-gated** (no silent posting).
- [ ] **PHI Handling**: Approves local-only LLM processing (no cloud HAL for patient data).
- [ ] **Multi-turn**: Approves message history retention (last 10 turns) for conversation context.
- [ ] **Visual Direction**: Approves starship command center aesthetic (dark mode, spectral accents, 3-pane layout).
- [ ] **Honesty**: Accepts that empty data displays as "∅" or "No data" never "$0".
- [ ] **Orchestrator**: Acknowledges that "control the whole program" requires `apex_orchestrator_pack` (currently missing) and will show "offline" status until installed.
- [ ] **Rollback**: Accepts feature-flag approach for safe deployment.

**Status:** AWAITING OPERATOR APPROVAL TO PROCEED.
