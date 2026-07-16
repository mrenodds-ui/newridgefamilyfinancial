# Moonshot AI — Place Mon–Thu Patient List on Office Manager (CONSULT ONLY)

**Date:** 2026-07-16
**Model:** `kimi-k2.5`
**Key:** OPENROUTER_API_KEY
**Script:** `scripts/run_moonshot_om_mon_thu_patient_list_place_consult.py`
**Apply:** DO NOT APPLY until operator approves.

## Operator request (verbatim)

> ask moonshot ai how to place a list of patient in the office manager page who are schedule for Monday thur Thurday everyday and report

---

# Verdict — Place Mon–Thu patient list on Office Manager

## 0. Operator Intent (verbatim)
> ask moonshot ai how to place a list of patient in the office manager page who are schedule for Monday thur Thurday everyday and report

**Interpretation:** Build a visible, daily-refreshing Mon–Thu patient schedule list on the OM page using existing SoftDent read-only data. Reuse current API; do not duplicate query logic. Provide consult-only roadmap; await approval before coding.

---

## 1. Current State (what already exists vs what is missing on OM)

| Component | Status | Gap |
|-----------|--------|-----|
| **Backend** | `appointments_range_snapshot(start_iso, days=4)` + `/api/softdent/appointments-range` live and PHI-safe (hash/initials) | None |
| **Optical OM page** | `nr2-optical-page-office-manager.html/.js` exists; only renders SoftDent **Today** count via `/api/softdent/appointments-today` | **Missing:** Mon–Thu list UI |
| **Classic Apex OM** | `apex_missing_widgets_pack.py` stripped (only `.pyc`); `build_weekly_schedule_list` gone; `append_office_manager_missing` no-ops | **Missing:** Entire widget layer; requires restore or replacement |
| **Data honesty** | API returns `time="—"` (SoftDent has no appt_time) | Must preserve; no fake timestamps |

---

## 2. Recommended Placement Design

### 2A Optical OM page (nr2-optical-page-office-manager.*) — **PRIMARY TARGET**
Add a “This Week (Mon–Thu)” card/table beneath the existing Today count.  
- **Why:** Page is already loaded by staff; no missing Python pack to restore; pure JS/HTML change.  
- **Layout:** 4-column grid (Mon Tue Wed Thu) or compact vertical list grouped by day.  
- **Row fields:** `initials` + `patientHash` (e.g., “AB • #a7f3”), `provider`, `status`, honest dash for time.

### 2B Classic Apex OM widgets (if still used) — **SECONDARY / OPTIONAL**
If staff still rely on the Apex dashboard board:  
- Re-create `build_weekly_schedule_list()` in a **new** small module (e.g., `nr2_om_weekly_widget.py`) instead of restoring the bulky missing pack.  
- Hook into `append_office_manager_missing` only if the import succeeds (defensive).  
- **Risk:** Adds Python surface area; Optical page is cleaner. Recommend **2A first**, add 2B only if explicit request.

---

## 3. Coding Plan (files · endpoints · UI wire · everyday refresh)

### Files to Touch
```
NewRidgeFinancial2/site/nr2-optical-page-office-manager.html  (add container)
NewRidgeFinancial2/site/nr2-optical-page-office-manager.js    (fetch + render)
```

### JS Logic Sketch (pseudo-code)
```javascript
// 1. Compute Monday of current week (ISO)
const monday = getMondayIso(new Date()); // reuse nr2_softdent_daily logic client-side or server-inject

// 2. Fetch (reuse existing endpoint)
fetch(`/api/softdent/appointments-range?start=${monday}&days=4&provider=`)
  .then(r => r.json()) // [{date, dayName, slots:[{patientHash, initials, provider, status, time}], count}, ...]

// 3. Render
//    - 4 columns (Mon-Thu)
//    - Each slot: <span class="phi-initials">{initials}</span> <span class="phi-hash">#{shortHash}</span>
//    - Status badge (Scheduled, Completed, Cancelled)
//    - Time column shows "—" (honest empty)

// 4. Refresh trigger
//    - Run on DOMContentLoaded
//    - Optional: soft polling every 5 min (if page stays open)
```

### HTML Wire
```html
<section id="om-weekly-schedule" class="om-card">
  <h3>This Week: Mon – Thu <span id="wk-range-label"></span></h3>
  <div class="wk-days-grid">
    <!-- JS injects 4 day-columns here -->
  </div>
  <p class="phi-note">Patient IDs hashed. Full name requires patient context click.</p>
</section>
```

### Everyday Refresh Mechanics
- **Monday calculation:** Use existing `monday_of_week_iso()` server-side; pass as meta tag or small inline script var in HTML, or compute client-side from `new Date()` (local browser time).  
- **Stale data guard:** Include `data-fetched-at` timestamp; if >30 min, show subtle “Refresh” button.

---

## 4. MUST / SHOULD / NICE table

| Priority | Item | Rationale |
|----------|------|-----------|
| **MUST** | Reuse `GET /api/softdent/appointments-range` with `days=4` | Avoids second SoftDent query path; honors existing PHI contract |
| **MUST** | Display only `initials` + `patientHash` on OM board | HIPAA minimum necessary; full name only behind staff-gated patient view |
| **MUST** | Render `time="—"` honestly | SoftDent has no appt_time; empty ≠ $0 |
| **MUST** | Mon–Thu = current week (Monday-based) | Operator intent “everyday” implies rolling current week |
| **SHOULD** | Implement on **Optical OM page** first | Lowest risk; no missing Python pack to recreate |
| **SHOULD** | Group by day (Mon/Tue/Wed/Thu) with subtle divider | Scannable for front desk |
| **SHOULD** | Provider filter dropdown (optional query param) | Staff can narrow to specific doctor/hygienist |
| **NICE** | “Today” highlighting border on current day column | Visual anchor |
| **NICE** | Click patientHash → open patient context (gated) | Workflow continuity without exposing PHI on board |
| **NICE** | Print-friendly CSS @media print | Front desk can print Mon–Thu list for backup |

---

## 5. PHI + SoftDent honesty rules

1. **Hash/Initials only:** Board shows `initials` (e.g., “JD”) and truncated `patientHash` (e.g., “#8f2a”). Full name requires navigation to patient record (staff auth gate).  
2. **No synthetic data:** If slot empty, show “—” or “No appt”. Never fabricate times.  
3. **Read-only:** UI is display-only; no POST/PUT through this widget.  
4. **Local-only:** API already returns PHI-safe hashes; keep it that way.

---

## 6. Validation checklist (how operator verifies list appears)

- [ ] Open Office Manager page → Network tab shows `appointments-range?start=2026-07-13&days=4` (assuming Monday 2026-07-13) returning HTTP 200 with JSON days array.  
- [ ] Visual: Four day-columns present (Mon Tue Wed Thu) with current week dates in headers.  
- [ ] Content: Each scheduled slot shows initials (e.g., “MS”) and hash fragment, **not** full surname.  
- [ ] Honesty: Time column displays “—” (em-dash) for every row; no fake 9:00 AM stamps.  
- [ ] Empty state: Days with zero appointments show “No appointments” or collapsed section (not error).  
- [ ] Monday rollover: Change system date to next Monday (or manipulate `start=` param manually) → list updates to new week.  
- [ ] No 500 errors in console; no “apex_missing_widgets_pack” import errors (because we avoided Classic Apex path for now).  

---

## 7. Executive Summary (5 bullets)

- **Use what exists:** The `/api/softdent/appointments-range` endpoint already delivers Mon–Thu data with PHI-safe hashes; no new SoftDent queries needed.  
- **Target Optical page:** Enhance `nr2-optical-page-office-manager.js` to fetch the 4-day range and render a compact 4-column schedule beneath the Today count.  
- **Classic Apex is optional:** Only restore the missing widget pack if staff explicitly require the old dashboard; otherwise skip to reduce tech debt.  
- **PHI safe by design:** Surface only initials + hash; full names stay behind patient-context gates.  
- **Consult-only now:** Awaiting operator “approve / proceed” before file edits; implementation time ~45 min once approved.

---

## 8. Approval Checklist

**DO NOT APPLY** until operator confirms:

- [ ] **Placement:** Proceed with Optical OM page (Option 2A) **only**, or also restore Classic Apex widget (Option 2B)?  
- [ ] **PHI Level:** Is initials + hash sufficient for the board, or do you require a “click to reveal full name” interaction?  
- [ ] **Provider Filter:** Include dropdown to filter by provider/hygienist, or show all providers Mon–Thu?  
- [ ] **Default View:** Show all 4 days expanded, or collapse future days (show Today expanded, Tue–Thu collapsed)?  
- [ ] **Test Week:** Confirm current week start date for validation (e.g., “Test with week of 2026-07-13”).  

**Reply:** “Approve / proceed with 2A only” (or specify choices) to begin implementation.
