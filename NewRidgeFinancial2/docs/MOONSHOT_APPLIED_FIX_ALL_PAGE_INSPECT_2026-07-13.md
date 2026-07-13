# Moonshot AI — Fix-All Page Inspect (APPLIED)

**Date:** 2026-07-13  
**Build:** `hal-10608`  
**Consult:** `MOONSHOT_FIX_ALL_PAGE_INSPECT_2026-07-13.md`  
**Operator:** `proceed`  
**Prior:** page-smoke 429/warming repairs (`4aca8b2`)

## Summary

Applied the **verifiable** MUST/SHOULD pieces from Moonshot’s fix-all consult. Rejected fictional patch targets (`library_indexer.py`, `widget_resolver.py`, invented SoftDent SQL). Did **not** invent Gold CSV or ERA dollars.

## Shipped (code)

| Item | Path / change |
|------|----------------|
| MUST schema skew | `site/nr2-build.json` + `nr2-build.json` → `schemaVersion`/`BUILD_ID`/`assetVersion` = `hal-10608` |
| OPS-A/R (code path) | `import_sync` builds `softdent_ar_aging.csv` from newer of SoftDent `account_aging.csv` vs `account_aging.jsonl` (live buckets e.g. Current/$42,965.29) |
| Direct pipeline | `import_direct_pipeline.build_ar_pipeline_dataset` same CSV fallback |
| Patient context | `build_apex_widgets(..., patient_id=)` + `/api/apex/widgets/<page>?patient_id=` hydrates `selectedPatient` via `build_patient_dossier` |
| SoftDent dossier | `gapCode=NO_PATIENT_CONTEXT` when empty |
| OM dossier cards | Use `bundle.selectedPatient` for dossier/eligibility/TP/claims/notes |
| HAL actions | Recommend Gold CSV + ERA 835 when readiness gaps present |
| Library honesty | `lib-storage` empty → `gapCode=LIBRARY_NOT_INDEXED` |
| Tests | `test_fix_all_page_inspect_applied.py` |

## Live check

- Account aging CSV maps to AR rows (example Total **$49,111.03**) — empty ≠ $0  
- Pytest: `test_fix_all_page_inspect_applied` + SHOULD/cache coherence → **passed**  
- Restart NR2 required to serve new `nr2-build.json` / import path in the running process

## Explicitly not done (still OPS / honest-empty)

| Issue | Why |
|-------|-----|
| Gold CSV (`GOLD_CSV_MISSING`) | Carestream ticket / real SoftDent line export — do not invent |
| ERA 835 | Clearinghouse enrollment + file drop |
| Denial/preauth/payer-change empties | Honest zero-volume until data exists |
| Library indexer invent | No real `library_indexer.py`; keep `LIBRARY_NOT_INDEXED` until intake indexes docs |
| Fictional treatment-plan SQL | Real builders already empty-honest without inventing tables |

## Acceptance vs consult

1. app-info schema → `hal-10608` after restart  
2. SoftDent A/R can refresh from Account Aging CSV (not invent)  
3. `?patient_id=` can populate dossier widgets when SoftDent patient extract has that id  
4. HAL recommended actions no longer blank when Gold/ERA gaps exist  
5. Gold/ERA widgets remain honest gaps until OPS completes  

## Honesty

empty ≠ $0 · inventedGold=false · softDentWriteBack=false
