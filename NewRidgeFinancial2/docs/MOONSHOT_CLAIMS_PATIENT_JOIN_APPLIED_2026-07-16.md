# Claims outstanding Sensei patient-join — APPLIED

**Date:** 2026-07-16  
**Moonshot backlog:** after shadow clock → claims `sampleWithPatientId` / dossier join  
**File:** `NewRidgeFinancial2/nr2_softdent_daily.py`

## Root cause

TXN-/DS- claim ids embed SoftDent **chart MRNs** (e.g. `1430001`) that usually are **not** Sensei `sd_patients.patient_id` UniqueIDs (e.g. `580292`).  
Old resolver returned the chart MRN as `patientId`, so dossier joins failed even when `sampleWithPatientId` looked non-zero.

## Fix

1. Prefer chart MRN **only when** it exists in `sd_patients`.
2. Else resolve Sensei id via improved name-key lookup (`Last, First Middle`, multi-word last).
3. Keep chart MRN for Trans-for-a-Period unpaid settlement separately.
4. `sampleWithPatientId` counts Sensei-resolvable ids only.

## Live validation (this workstation)

`claims_outstanding(limit=20)` → `sampleWithPatientId=20/20` with Sensei ids (e.g. Briscoe → `580292`).

## Tests

`test_nr2_softdent_daily.py` — includes `test_claims_outstanding_txn_chart_prefers_sensei_name`.
