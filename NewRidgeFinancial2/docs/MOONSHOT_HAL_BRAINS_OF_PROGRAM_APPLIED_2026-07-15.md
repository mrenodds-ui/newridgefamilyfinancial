# Moonshot AI — HAL as brains of the program (APPLIED)

**Date:** 2026-07-15  
**Source consult:** `MOONSHOT_HAL_BRAINS_OF_PROGRAM_CONSULT_2026-07-15.md`  
**Build:** `nr2-12018-hal-brains`  
**Repo root:** `C:\Users\mreno\newridgefamilyfinancial`  
**Status:** Applied exactly to Moonshot P0→P3 plan (consult paths only).

## Operator request

> proceed exactly as moonshot ai and do not deviate

## Path hygiene (honored)

| Valid | Invalid (not used) |
|-------|-------------------|
| `C:\Users\mreno\newridgefamilyfinancial` | `C:\NewRidgeFamilyFinancial` |
| `NewRidgeFinancial2/nr2_hal_gateway.py` | `NewRidgeFinancial2/gateway/routes/hal_gateway.py` |
| SoftDent exports → `C:\SoftDentReportExports` | — |

## What shipped (by Moonshot phase)

### P0 — Multi-turn brain stem
- **NEW** `NewRidgeFinancial2/hal_session_store.py`
- **NEW DIR** `app_data/nr2/hal-sessions/`
- `POST /api/hal/session` — create thread UUID
- `GET /api/hal/session/<id>/history` — retrieve turns (cap 50)
- `POST /api/hal/chat` — multi-turn with `messages`, HAL 9000 system prompt, `stream:true` → SSE via `evaluate_query_sse_frames`
- Optical chat uses `/api/hal/chat` (not single-turn evaluate-query only)
- Mounted `hal-chat-9000.js` persona into chat systemPrompt
- Typing indicator + streaming token reveal in `nr2-optical-page-hal.js`
- Session id persisted in `sessionStorage`

### P1 — Tool mounting
- **NEW** `NewRidgeFinancial2/hal_brain_tools.py`
- `GET /api/hal/tools/softdent-status`
- `POST /api/hal/tools/softdent-export` (requires `consent:true` → `softdent_gui_export.py`)
- `GET /api/hal/tools/qb-summary`
- `POST /api/hal/tools/qb-sync` (requires `consent:true` → `qb_connector.sync_read_only`)
- `POST /api/hal/tools/memo-search` / `memo-write`
- `POST /api/hal/tools/web-research` (`web_research.py`, PHI sanitize)
- Mounted `hal-memo-index.js` on optical page

### P2 — Action / navigation control
- `POST /api/hal/actions/propose`
- `GET /api/hal/actions/pending`
- `POST /api/hal/actions/execute` (requires `consent:true`)
- Consent modal in optical HTML
- Mounted `hal-route-exec.js`, `hal-director.js`, `hal-agent-loop.js`, `hal-autonomous-ops.js`, `hal-orchestrator.js`

### P3 — Command center UI
- **NEW** `NewRidgeFinancial2/site/nr2-optical-hal-command.css`
- Rewrote `nr2-optical-page-hal.html` — 3-pane command center (Memory | Chat | Beams/Tools/Queue)
- Rewrote `nr2-optical-page-hal.js` — beams bind, tool palette, consent queue, voice toggle
- Mounted `hal-page-canvas.js`, `hal-voice.js`
- Honesty: live SoftDent/QB beams show `NO SIGNAL` / empty-not-zero — never fake dollars
- Removed “mock replies” bind lie

## Doctrine (unchanged hard rules)

- SoftDent: read / Excel GUI export / teach / consent-queue only — **no silent write-back**
- QuickBooks: read / sync / consented prep only — **no silent posting**
- empty ≠ $0
- Cloud HAL still denied

## Files touched

- `NewRidgeFinancial2/hal_session_store.py` (new)
- `NewRidgeFinancial2/hal_brain_tools.py` (new)
- `NewRidgeFinancial2/nr2_http_server.py` (routes)
- `NewRidgeFinancial2/nr2_browser_security.py` (read exempts)
- `NewRidgeFinancial2/site/nr2-optical-page-hal.html`
- `NewRidgeFinancial2/site/nr2-optical-page-hal.js`
- `NewRidgeFinancial2/site/nr2-optical-hal-command.css` (new)
- `NewRidgeFinancial2/nr2-build.json` → `nr2-12018-hal-brains`
- `app_data/nr2/hal-sessions/.gitkeep`

## Validation smoke (local)

```
python -c "from hal_session_store import create_session; ..."
→ session create + turns ok; softdent_status live; qb_summary live; memo_search hits
nr2_http_server.py AST parse ok; routes present
```

## How to use

1. Restart NR2 browser app so routes load.
2. Open HAL page (optical HAL AI Core).
3. Chat is multi-turn streaming.
4. SoftDent Export / QB Sync open consent modal before running.
5. Memo / Web tools on the right palette.

## Rollback

- Revert listed files to pre-`nr2-12018-hal-brains`.
- Delete `app_data/nr2/hal-sessions/*.jsonl` if session bloat.
