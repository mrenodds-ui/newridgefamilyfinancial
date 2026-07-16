# Sensei/ODBC appt_time extract — APPLIED

**Date:** 2026-07-16  
**Consults:** `MOONSHOT_WHATS_NEXT_AFTER_OM_SCHEDULE_ENRICH_2026-07-16.md`,  
`MOONSHOT_WHATS_NEXT_AFTER_DESK_SMOKE_THIS_PATIENT_2026-07-16.md`  
**Operator:** continue with all

## Shipped

| Item | Where |
|------|--------|
| ODBC discovery includes `appt_time` candidates | `scripts/discover_softdent_odbc_schema.py` |
| Suggested + `.env.example` appointments query includes `ApptTime` | same + `.env.example` |
| Sensei backfill: patient+date when unique empty row | `backfill_appt_times_from_sensei` |
| ODBC map accepts `StartTime` | `_populate_from_odbc` |
| Sensei fixture asserts `09:30` | `test_softdent_odbc_extract.py` |
| Dossier appointments use `appt_time` when present | `patient_dossier.py` |
| Desk smoke `mon_thu_appt_time` (≥50% HH:MM when slots exist) | `desk_smoke.py` |

## Note

Live Sensei lane already populated most Mon–Thu times; this closes ODBC/discovery + orphan matching gaps and keeps smoke honest (empty ≠ invent `09:00`).
