# Moonshot AI — What's Next After HAL This-Patient Shortcut (CONSULT ONLY)

**Date:** 2026-07-16
**Model:** `kimi-k2.5`
**Key:** OPENROUTER_API_KEY
**Script:** `scripts/run_moonshot_whats_next_after_hal_this_patient_consult.py`
**Shipped:** `17ba77e`
**Apply:** DO NOT APPLY until operator approves.

## Operator request (verbatim)

> continue

---

# Verdict
Ship the **Desk Smoke Extension: Patient-Context Beam Proof** to close the `deskSmokeCoversThisPatient: false` gap and harden the Mon–Thu → dossier → HAL this-patient → Force Close path before supervised phase graduation.

## 0. Operator Intent (verbatim)
continue

## 1. Recommended NEXT (name, why now, effort, REAL files, validation gate)
**Name:** NR2-12044-DESK-SMOKE-PATIENT-CONTEXT-BEAM-PROOF  
**Why now:**  
- LIVE AUDIT explicitly flags `deskSmokeCoversThisPatient: false` despite `thisPatientShortcut: true` being live.  
- The pilot is in **shadow** phase (`systemOfRecord: false`); beam integrity for patient-context money reads must be proven before supervised/cutover.  
- `deskSmokeForceClose: true` capability exists but lacks coverage for the new 17ba77e shortcut path.  
- Risk of unmonitored HAL session drift or unbound patient queries escaping the smoke perimeter.  

**Effort:** Small (1 dev-day). Extends existing `desk_smoke.py` assertions; no new UI.  

**REAL files:**  
- `NewRidgeFinancial2/desk_smoke.py` — add `assert_this_patient_shortcut_binding()` and `assert_force_close_beam_hash()`  
- `NewRidgeFinancial2/hal_session_store.py` — expose `get_bound_patient(session_id)` for smoke probe  
- `NewRidgeFinancial2/patient_dossier.py` — verify `query_refers_to_bound_patient` returns consistent hash under smoke  
- `NewRidgeFinancial2/nr2_http_server.py` — instrument `/health/smoke` to report `thisPatientShortcutCovered` bool  
- `NewRidgeFinancial2/nr2-optical-hal` — confirm optical SUMMARIZE tool logs session-bound PHI initials  

**Validation gate:**  
- `deskSmokeLast.forceCloseAvailable: true` (engaged)  
- `deskSmokeCoversThisPatient: true` (LIVE AUDIT marker flip)  
- Beam hash consistency across Mon–Thu list → dossier → HAL reply → Force Close cycle  
- Zero red lasers; `emptyNotZero` invariant holds through patient-context switches  

## 2. Why this beats the other candidates now
- **SoftDent/Trellis tomorrow eligibility (#2):** Operational batch helper. Useful, but the audit shows current patient features are live yet **unsmoked**. Shadow-phase protocol prioritizes beam proof over new batch workflows.  
- **Classic Apex 2B widget (#3):** Optional legacy support. Mon–Thu list already functional (`appointmentsRange` counts 28/27/31/30). Introduces new UI surface area when current priority is hardening existing surfaces.  
- **Raw audit marker flip (#4):** Insufficient alone; the marker must be earned by actual smoke coverage (this package).  

## 3. Runner-ups (2–3)
1. **SoftDent/Trellis Tomorrow Eligibility Worklist Hardening** — Next sprint after beam proof; leverages existing nightly helpers to pre-verify insurance before morning huddle.  
2. **Audit Marker Auto-Flip + Dashboard Widget** — Cosmetic; defer until smoke coverage proves the marker should stay green.  

## 4. What NOT to redo
- Mon–Thu appointment list rendering (shipped 873b4c6)  
- Mini-dossier clinical notes/estimates (shipped 4039bf4)  
- HAL patient-context bind/auto-summarize (shipped 2cd6959)  
- "this patient" shortcut logic (shipped 17ba77e)  
- Claims integration (shipped 16197d2)  
- Provider filters (shipped 2310d0d)  

## 5. Acceptance criteria
- [ ] `desk_smoke.py` asserts that a bound patient session survives the Mon–Thu → dossier → HAL → Force Close cycle without PHI leakage.  
- [ ] `deskSmokeCoversThisPatient` flips to `true` in LIVE AUDIT.  
- [ ] `forceCloseAvailable` reports `true` and generates a valid beam hash matching `lastBeamHash`.  
- [ ] Unbound patient query returns `policy:patient-summary-unbound` and is logged in smoke trail.  
- [ ] SoftDent READ-ONLY invariant enforced; empty balance fields explicitly checked `!== $0`.  
- [ ] PHI displayed as hash/initials only in smoke logs.  

## 6. Executive Summary (5 bullets)
- **Gap:** LIVE AUDIT shows patient-context shortcut is live but not smoke-covered (`deskSmokeCoversThisPatient: false`).  
- **Risk:** Shadow phase requires beam proof for all money-adjacent patient reads before supervised graduation.  
- **Scope:** Extend `desk_smoke.py` to traverse OM Mon–Thu → dossier → HAL this-patient → Force Close; validate session binding and hash consistency.  
- **Impact:** Enables safe promotion to `systemOfRecord: true` by closing the final unsmoked path in the patient track.  
- **Constraint Respect:** Uses only real NR2 paths; no SoftDent writes; maintains `empty ≠ $0` and PHI hashing.  

## 7. Approval Checklist
- [ ] Architect (Moonshot AI) reviewed LIVE AUDIT markers and confirmed gap.  
- [ ] Dev lead confirmed `desk_smoke.py` extension points exist for session-bound assertions.  
- [ ] Compliance confirmed PHI hash/initials acceptable in smoke logs.  
- [ ] QA confirmed Force Close beam hash can be captured in staging.  
- [ ] Operator ("continue") intent acknowledged: proceed with beam hardening, not new features.
