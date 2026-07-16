# ERA first-drop path — APPLIED (fixture smoke + ops wiring)

**Date:** 2026-07-16  
**Moonshot:** `MOONSHOT_WHATS_NEXT_AFTER_TRELLIS_1AM_2AM_2026-07-16.md` → ERA inbox first 835  
**Commits context:** SoftDent morning bundle deferred · Trellis 1 AM / 2 AM scheduled

## Shipped

| Item | Status |
|------|--------|
| Fix `scripts/run_era_inbox_ingest_ops.py` → `nr2_era_inbox` (was broken `apex_era835_pack`) | Done |
| Drop runbook `docs/runbooks/era_835_inbox_drop_nr2.md` | Done |
| Fixture path smoke in `test_nr2_era_inbox.py` (isolated `NR2_ERA835_INBOX`) | Done |
| Live inbox directories ensured | Done |

## Live honesty

- **No real payer 835** found under SoftDent/export/OneDrive roots at apply time.
- Ops gate `era_inbox` stays **YELLOW** until a **real** 835 is dropped and ingested.
- Fixture dollars are **not** treated as remittance truth (empty ≠ `$0`).

## Operator next (to flip GREEN)

1. Drop a real payer `.835` / `.edi` into `app_data/nr2/office/era_inbox/drop` (or `C:\SoftDentFinancialExports\era`).
2. Run `python scripts/run_era_inbox_ingest_ops.py`.
3. Confirm `era_inbox` GREEN via `python scripts/nr2_ops_gates_checklist.py`.
4. Approve any suggestions in QuickBooks manually — no SoftDent write-back.

## What was NOT done

- Did not invent remittance rows or post to SoftDent/QB.
- Did not flip `forceCloseAvailable`.
- Did not resume SoftDent morning bundle (operator deferred).
