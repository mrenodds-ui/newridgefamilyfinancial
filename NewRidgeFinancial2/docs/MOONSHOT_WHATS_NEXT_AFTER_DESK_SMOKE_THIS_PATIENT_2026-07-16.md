# Moonshot AI — What's Next After Desk Smoke This-Patient (CONSULT ONLY)

**Date:** 2026-07-16
**Model:** `kimi-k2.5`
**Key:** OPENROUTER_API_KEY
**Script:** `scripts/run_moonshot_whats_next_after_desk_smoke_this_patient_consult.py`
**Shipped:** `daa7ba2`
**Apply:** Operator said continue with all — Cursor may apply #1 then backlog in order.

## Operator request (verbatim)

> continue with all

---

# Verdict
**Ship Sensei/ODBC `appt_time` extract now** to replace "—" placeholders with real HH:MM on the Mon–Thu OM board, completing the data pipeline initiated in bc0c8ff.

## 0. Operator Intent (verbatim)
continue with all

## 1. Recommended NEXT (name, why now, effort, REAL files, validation gate)
**Package:** NR2-12060-SENSEI-APPT-TIME-EXTRACT  
**Why now:** The LIVE AUDIT confirms `apptTimeInDaily: true` and `odbcMentionsApptTime: true`, yet `timeSamples` shows 12 consecutive "—" tokens. The UI migration (bc0c8ff) is live but data-starved. This is the critical path to make the Mon–Thu board operationally useful for huddles.  
**Effort:** Small–Medium (single ODBC field mapping + transform).  
**REAL files to touch:**
- `softdent_odbc_extract.py` – add `appt_time` to the SELECT/投影 for the appointments query (likely `SELECT appt_time FROM schedule...` or equivalent SoftDent column).
- `nr2_softdent_daily.py` – ensure `appt_time` is parsed from ODBC result, cast to `HH:MM`, and merged into the daily JSON beam.
- `desk_smoke.py` – extend smoke test to assert `appt_time` is non-null and matches regex `\d{2}:\d{2}` for today’s appointments.
**Validation gate:** Run desk smoke; verify OM board renders "09:00" instead of "—" for at least one confirmed appointment; no PHI leakage in logs (hash/initials only).

## 2. Why this beats the other candidates now
- **Candidate #2 (Tomorrow-insurance worklist):** Depends on the board being readable. If times are "—", the morning huddle cannot sequence the day.
- **Candidate #3 (Provider/operatory grouping):** Cosmetic polish that should happen after the underlying data is complete.
- **Candidate #4 (Apex 2B widget):** Legacy compatibility is optional; the current board is the primary interface.
- **Data completion vs. new features:** The audit shows fresh SoftDent syncs (17 connected sources, level=fresh). The data is available in the DB; we just need to extract the column.

## 3. Ordered backlog AFTER #1 (2–4 items operator can "continue with all")
1. **NR2-12070-TRELLIS-MORNING-HUDDLE** – SoftDent/Trellis tomorrow-insurance worklist surface (eligibility & estimate alerts for next-day patients). Builds on the now-functional appt_time slots.
2. **NR2-12080-OM-BOARD-POLISH** – Provider/operatory grouping + print CSS for the Mon–Thu board. UI-only once data is solid.
3. **NR2-12090-HAL-SHORTCUT-HARDEN** – Edge-case hardening for the HAL this-patient shortcut (RBAC edge cases, empty-state handling) if desk smoke finds gaps.
4. **NR2-12100-APEX-2B-WIDGET** (Optional) – Classic weekly widget for legacy users only if requested post-shadow.

## 4. What NOT to redo
- Do not rebuild the Mon–Thu shell or ADA UI (already shipped in f1e8ccb/bc0c8ff).
- Do not reimplement this-patient shortcut or desk smoke binding (shipped daa7ba2/17ba77e).
- Do not modify Trellis nightly stagger logic (shipped c7da9de).
- Do not create new integration directories; stay in existing `softdent_odbc_extract.py` and `nr2_softdent_daily.py` patterns.

## 5. Acceptance criteria
- [ ] `appointmentsRange.timeSamples` in LIVE AUDIT shows at least 80% populated HH:MM strings (e.g., "08:30", "14:15") instead of "—".
- [ ] `softdent_odbc_extract.py` query includes the time column without breaking existing patient hash/initials projection.
- [ ] `desk_smoke.py` asserts `appt_time` presence and format for today's appointments.
- [ ] OM board renders times in local office timezone (no UTC drift).
- [ ] No SoftDent write operations; read-only constraint preserved.
- [ ] PHI compliance: logs show only hashed patient IDs, never full names with times.

## 6. Executive Summary (5 bullets)
- **The Mon–Thu board is data-blind:** UI shipped but times show "—" because ODBC extract omits the `appt_time` column.
- **One field unlocks operational value:** Adding the time extract completes the daily beam and enables sequence-aware huddles.
- **Risk is low:** SoftDent schema for appointment times is stable; this is a projection addition, not a transform.
- **Validation is automated:** Extend existing desk smoke to enforce the field presence, preventing regression.
- **Backlog is sequenced:** Insurance worklist (#2) and UI polish (#3) wait for this data foundation; legacy widget (#4) remains optional.

## 7. Approval Checklist
- [ ] Confirm `softdent_odbc_extract.py` path exists in repo and is the correct ODBC wrapper.
- [ ] Confirm SoftDent column name for appointment time (e.g., `appt_time`, `start_time`, `apt_time`) with DBA or existing schema doc.
- [ ] Verify no PII in the new column extract (time only, no patient name).
- [ ] Staging environment shows real times on Mon–Thu board before prod deploy.
- [ ] Desk smoke GREEN post-deploy.
