# Moonshot AI — Claims Pro Presentation APPLIED

**Date:** 2026-07-10  
**Build:** **hal-10410**  
**Consult:** `MOONSHOT_CLAIMS_PRO_PRESENTATION_CONSULT_2026-07-10.md`  
**Operator:** “can you do both?” → Option A dual mode (dense table default + kanban toggle)

## What shipped

1. **Aging Exposure** (`claims-aging-exposure`) — one 30/60/90 matrix replaces three full-width shelves. Click a column → filters the workbench. Legacy HAL IDs `claims-aging-30/60/90` resolve via `aliasIds`.
2. **Executive strip** + **Critical actions** — compact KPIs and click-to-filter queues.
3. **Claims Workbench** (`type: claims-workbench`, id still `claims-kanban-board`) — **Table** default + **Kanban** toggle. Same SoftDent read-only data; NR2 row/card actions only.
4. HAL: `set_claims_view`, aging alias focus also filters workbench; table/kanban voice commands.

## Honest constraints preserved

- No invented dollars / claim IDs / patients
- SoftDent read-only (no write-back)
- Empty states when Age/Days or claims import missing

## Files

- `apex_claims_narratives_pack.py` — exposure / critical / strip / workbench widgets
- `apex_backend.py` — `_claims_widgets` layout + HAL board-actions + `BUILD_ID`
- `site/apex-core.js` — renderers, dual-view wiring, alias focus
- `site/apex-bridge.css` — pro layout styles
- `nr2-build.json` / `site/nr2-build.json` / `site/index.html` → **hal-10410**

## Rollback

Revert to prior Claims layout (three shelves + kanban-only) from pre-`hal-10410` commit; restore `BUILD_ID` / asset query strings.
