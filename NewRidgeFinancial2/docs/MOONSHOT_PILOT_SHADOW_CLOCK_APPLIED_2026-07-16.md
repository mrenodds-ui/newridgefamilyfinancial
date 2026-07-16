# Pilot shadow clock — APPLIED

**Date:** 2026-07-16  
**Moonshot backlog:** after ERA first-drop (blocked on real 835) → pilot shadowDays hygiene  
**Script:** `scripts/start_pilot_shadow_clock.py`

## What changed

| Item | Value |
|------|--------|
| `app_data/nr2/pilot_phase.json` | `phase=shadow`, `shadow_started_at` stamped |
| Source stamp | Period-close `ops/period_close_state.json` → `2026-07-15T21:10:23+00:00` |
| `shadowDaysElapsed` | `0` (counts up each UTC day; need ≥30) |
| `systemOfRecord` | **false** (unchanged — cutover attestation still required) |

## Ops gate

`pilot_shadow` stays **YELLOW** until `shadowDaysElapsed ≥ 30`. That is expected.

## Re-run

```powershell
python scripts/start_pilot_shadow_clock.py --from-period-close
# overwrite only if needed:
python scripts/start_pilot_shadow_clock.py --from-period-close --force
```

## What was NOT done

- Did not set `systemOfRecord=true` or phase `supervised`/`cutover`.
- Did not skip SoftDent morning bundle or invent ERA remittance.
- Did not flip `forceCloseAvailable`.
