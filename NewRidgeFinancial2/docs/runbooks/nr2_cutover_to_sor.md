# NR2 cutover to system of record

**Date:** 2026-07-16  
**Applies when:** Shadow financial overlay has run ≥30 days with honest money beams and desk smoke MATCH.

`systemOfRecord` remains **`false`** until operator attestation. Force Close alone does **not** flip SOR.

---

## Phases

| Phase | `pilot.phase` | `systemOfRecord` | Operator intent |
|-------|---------------|------------------|-----------------|
| 1 Shadow | `shadow` | `false` | Parallel validate NR2 money vs SoftDent/QB; no posting export |
| 2 Supervised | `supervised` | `false` | Staff uses NR2 huddle daily; posting bulk review allowed; export still gated |
| 3 Cutover | `cutover` | `true` | Signed attestation; approved posting export enabled |

State file: `app_data/nr2/pilot_phase.json`  
Attestation file: `app_data/nr2/pilot_cutover.json`

---

## Preconditions (all required before supervised)

| Check | Command / route | Gate |
|-------|-----------------|------|
| Morning bundle | `python scripts/morning_bundle_attended.py` | `periodClose.morningBundle.ok === true` |
| Desk smoke | `python scripts/desk_ops_smoke.py` | `deskProof: MATCH` |
| Money beam freshness | `GET /api/import-readiness` | SD + QB beams &lt;24h |
| Beam drift | `python scripts/refresh_period_close_beam.py` if MISMATCH | VERIFY BEAM MATCH on hub |
| Trellis AM proof | `python scripts/prove_trellis_withbenefits_am.py` | 3 consecutive weekdays `withBenefits > 0` |
| Claims workflow | Claims page payer batch + phone CSV | Staff timed &lt;2 min without SoftDent Insurance UI |

---

## Phase 1 → 2 (shadow → supervised)

1. Confirm `GET /api/app-info` → `pilot.shadowDaysElapsed >= 30` (or operator documents exception in writing).
2. Run `python scripts/validate_supervised_pilot.py` (or repo cutover readiness checks).
3. Set phase:
   - Env: `NR2_PILOT_PHASE=supervised`, **or**
   - Update `app_data/nr2/pilot_phase.json` via approved admin tooling.
4. Verify `pilot.supervisedStartedAt` is stamped.

**Do not** set `systemOfRecord=true` in this phase.

---

## Phase 2 → 3 (supervised → cutover)

1. Confirm `pilot.supervisedDaysElapsed >= 30`.
2. Operator signs attestation (name, date, witness) stored in `app_data/nr2/pilot_cutover.json`:
   ```json
   {
     "signed_by": "Operator Name",
     "signed_at_utc": "2026-08-15T14:00:00+00:00",
     "witness": "optional",
     "note": "NR2 financial SOR cutover after shadow+supervised validation"
   }
   ```
3. Set `NR2_PILOT_PHASE=cutover` or `phase: cutover` in pilot state.
4. Confirm `GET /api/app-info` → `pilot.systemOfRecord === true`.

---

## `forceCloseAvailable` (laser gates)

From `nr2-optical-page-wire.js` — Force Close is **not** the same as SOR cutover:

- Available when period-close is `stalled` / `blocked` **or** import lasers are RED.
- Requires real money data — **GREEN desk smoke alone is insufficient** if morning bundle failed.
- After cutover, posting queue export still follows `nr2_pilot.check_posting_gate`.

---

## Rollback

If post-cutover drift is discovered:

1. Set `NR2_PILOT_PHASE=supervised` (or `shadow`) immediately.
2. Do **not** delete attestation file — append rollback note with timestamp.
3. Re-run `refresh_period_close_beam.py` and attended morning bundle.
4. Document incident in ops log; clinical work stays in SoftDent.

---

## Quick reference

```powershell
# Status
curl http://127.0.0.1:8765/api/app-info | jq .pilot

# Desk smoke
python scripts/desk_ops_smoke.py

# AM Trellis proof
python scripts/prove_trellis_withbenefits_am.py

# Morning bundle (attended)
python scripts/morning_bundle_attended.py --probe-only
python scripts/morning_bundle_attended.py --yes --refresh-close
```

---

## Related

- [hybrid_pms_overlay.md](../architecture/hybrid_pms_overlay.md)
- [softdent_excel_enablement_nr2.md](./softdent_excel_enablement_nr2.md)
- `NewRidgeFinancial2/nr2_pilot.py` — `pilot_info()`, `check_posting_gate()`
