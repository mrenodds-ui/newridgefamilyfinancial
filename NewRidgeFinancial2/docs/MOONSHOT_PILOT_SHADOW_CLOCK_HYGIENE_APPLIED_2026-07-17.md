# Pilot shadow clock hygiene / day-count visibility — APPLIED

**Date:** 2026-07-17  
**Consult:** `MOONSHOT_WHATS_NEXT_AFTER_COLLECTIONS_EXCEL_GREYED_2026-07-17.md`  
**Operator:** continue

## What changed

| Surface | Change |
|---------|--------|
| `nr2_pilot.py` | UTC **calendar**-day elapsed (not incomplete 24h floor); `shadowDaysRemaining`, `shadowClockLabel` (`Day X of 30`), `shadowRemainingLabel`, `shadowEligible`; `forceCloseAvailable` hard `false` on pilot payload |
| `nr2-optical-page-wire.js` | SHADOW ops gate shows `Day X of 30 · N left` (text, not color-alone); title carries remaining + forceClose=false |
| `test_nr2_pilot.py` | Calendar-day + clock-label coverage |

## Live proof (after NR2 restart)

`GET /api/app-info` → `pilot`:

- `shadowDaysElapsed`: **2** (started `2026-07-15T21:10:23+00:00`)
- `shadowDaysRemaining`: **28**
- `shadowClockLabel`: **Day 2 of 30**
- `shadowRemainingLabel`: **28 days until eligible**
- `forceCloseAvailable`: **false**
- `systemOfRecord`: **false**

Ops gates poll `/api/app-info` every 60s on optical pages (`mountOpsGates`).

## What was NOT done

- Did not flip `forceCloseAvailable` / `systemOfRecord`
- Did not SoftDent GUI / invent Trellis `withBenefits` / invent ERA 835
- Moonshot’s invented paths (`desk_view.py`, `phase_gate.py`) were remapped to real `nr2_pilot.py` + `nr2-optical-page-wire.js`
