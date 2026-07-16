# Moonshot AI — Place Claims List on Office Manager + Full Names (CONSULT ONLY)

**Date:** 2026-07-16
**Model:** `kimi-k2.5`
**Key:** OPENROUTER_API_KEY
**Script:** `scripts/run_moonshot_om_claims_list_place_consult.py`
**Apply:** DO NOT APPLY until operator approves.

## Operator request (verbatim)

> ask moonshot ai how to place claims like he did with patients under the office manger page. can he do it with claims like the patient list. also, i need the patient names not their initials on the lists. report

---

# Verdict — Place claims list on Office Manager (+ full names)

## 0. Operator Intent (verbatim)
> "ask moonshot ai how to place claims like he did with patients under the office manger page. can he do it with claims like the patient list. also, i need the patient names not their initials on the lists. report"

## 1. Current State (patient list shipped vs claims gap vs name display)
- **Shipped on OM**: `#om-weekly-schedule` section fetches `GET /api/softdent/appointments-range?days=4` and renders Mon–Thu patient rows as **initials + short hash** (e.g., "AB#3f7a") despite API returning `patientName`.
- **Gap on OM**: No `#om-claims` section exists. The claims optical page (`nr2-optical-page-claims.js`) only pulls `/api/softdent/claims-outstanding` for a metrics strip (counts/dollars), not a patient-style list.
- **Name suppression**: Current board policy hides full names to keep PHI off shoulder-surfable displays. Operator now explicitly overrides this for the Office Manager view (staff-only).

## 2. Can claims be done like the patient list? (YES/NO + why)
**YES.**  
The existing `claims_outstanding` helper already returns full `patientName`, `payer`, `serviceDate`, `amount`, `status`. You can mirror the patient-list fetch/render/refresh pattern exactly:
- Same optical OM surface (`nr2-optical-page-office-manager.html/.js`).
- Same section-based DOM insertion (`#om-claims-outstanding`).
- Same polling/visibility refresh logic.
- Reuse `GET /api/softdent/claims-outstanding?limit=200` (do not invent a second query).

## 3. Recommended Placement Design (optical OM)
**Location**: Immediately below `#om-weekly-schedule` in the OM grid.  
**Layout**: Twin-column table matching the patient list density but with claims headers:
```
Patient Name | Payer | Service Date | Amount | Status | Age (days)
```
**Behavior**:
- Click row → mini dossier panel (reuse `#wk-dossier` pattern) showing claim detail + patient contact.
- Auto-refresh every 60s + `visibilitychange` resume (identical to patient list).
- Sort by `serviceDate` DESC (newest claims on top) or by `amount` DESC; default to age (oldest first) so staff chase money.

## 4. Full patient names (not initials) — policy + coding change
**Operator override**: Office Manager is staff-only (authenticated, behind desk). Full names are authorized here; initials+hash stays only on public/board projections if ever mirrored elsewhere.

**Code change required**:
- **Patient list**: Change render line in `nr2-optical-page-office-manager.js` from `renderInitialsHash(slot)` to `slot.patientName`.
- **Claims list**: Use `claim.patientName` directly; never hash.
- **Logs**: Continue to log by `patientId` or `claimId` only; keep `patientName` out of server logs even if shown on screen.

## 5. Coding Plan (files · endpoints · UI wire · refresh)
**Files to touch** (paste-ready sketches):

**A. HTML** (`NewRidgeFinancial2/site/nr2-optical-page-office-manager.html`)  
Insert after `#om-weekly-schedule`:
```html
<section id="om-claims-outstanding" class="om-panel">
  <h3 class="om-panel-title">Outstanding Claims · Top 200</h3>
  <div class="om-table-wrap">
    <table class="om-data-table" id="claims-table">
      <thead>
        <tr>
          <th>Patient Name</th>
          <th>Payer</th>
          <th>Service Date</th>
          <th>Amount</th>
          <th>Status</th>
          <th>Age (days)</th>
        </tr>
      </thead>
      <tbody id="claims-tbody"><!-- JS fills --></tbody>
    </table>
  </div>
  <div id="claims-summary" class="om-micro-stat"></div>
</section>
```

**B. JS additions** (`nr2-optical-page-office-manager.js`):
```javascript
// Add to init()
async function loadClaimsOutstanding() {
  const limit = 200;
  const res = await fetch(`/api/softdent/claims-outstanding?limit=${limit}`);
  if (!res.ok) return;
  const data = await res.json(); // {claims:[], totalOutstanding, count}
  renderClaimsList(data.claims);
  document.getElementById('claims-summary').textContent = 
    `${data.count} claims · $${(data.totalOutstanding/100).toFixed(2)} total`;
}

function renderClaimsList(claims) {
  const tbody = document.getElementById('claims-tbody');
  tbody.innerHTML = '';
  claims.forEach(c => {
    const age = Math.floor((Date.now() - new Date(c.serviceDate)) / 86400000);
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="phi-name">${c.patientName}</td>
      <td>${c.payer}</td>
      <td>${c.serviceDate}</td>
      <td class="num">${c.amount != null ? '$'+c.amount.toFixed(2) : '-'}</td>
      <td><span class="badge status-${c.status}">${c.status}</span></td>
      <td class="num">${age}</td>
    `;
    tr.onclick = () => openClaimDossier(c); // reuse dossier panel or new mini-panel
    tbody.appendChild(tr);
  });
}

// Wire refresh identical to patient list (60s interval + visibilitychange)
```

**C. CSS reuse** (existing `.om-data-table` classes handle zebra striping; add `.phi-name { font-weight: 500; }` if desired).

**Endpoint**: `GET /api/softdent/claims-outstanding?limit=200` (existing, READ-ONLY).  
**No new backend code required** unless you want server-side sorting by age.

## 6. MUST / SHOULD / NICE table
| Priority | Item | Rationale |
|----------|------|-----------|
| **MUST** | Reuse `GET /api/softdent/claims-outstanding` | Do not invent second SoftDent path; honor READ-ONLY. |
| **MUST** | Show full `patientName` on OM lists (both schedule & claims) | Operator override explicit; staff-only surface. |
| **MUST** | Keep `empty ≠ $0` display logic | If `amount` is null/undefined, render "-" not "$0.00". |
| **MUST** | Section ID `#om-claims-outstanding` | Consistent with `#om-weekly-schedule` naming. |
| **SHOULD** | Default sort by age DESC (oldest first) | Staff work oldest claims first (cash flow). |
| **SHOULD** | Cap at 200 rows client-side or API param | SoftDent helper supports `limit`; keeps render fast. |
| **NICE** | Row click opens mini dossier like patient list | Reuse `#wk-dossier` DOM or clone pattern. |
| **NICE** | Color badges for status (Pending, Denied, Paid) | Visual triage; reuse existing badge CSS. |

## 7. PHI + SoftDent honesty rules (staff OM vs board/logs)
- **Staff OM only**: Full names render only inside authenticated Office Manager HTML. If you later mirror this list to a hallway board, revert to initials+hash or redact.
- **Logs**: Server logs must continue to record `patientId`/`claimId`, never `patientName`. The API returns the name, but access logs should not echo query parameters that contain names (they don't here).
- **SoftDent READ-ONLY**: Confirmed. We are selecting from `claims_outstanding`; no inserts/updates.
- **Empty handling**: If SoftDent returns a claim with `amount: null`, display "-" or "Pending". Do not coerce to `$0.00`.

## 8. Validation checklist
- [ ] `nr2-optical-page-office-manager.html` contains `#om-claims-outstanding` section.
- [ ] JS fetches `/api/softdent/claims-outstanding?limit=200` and populates `#claims-tbody`.
- [ ] Patient list rows now show `patientName` (full string) not initials+hash.
- [ ] Claims list rows show `patientName` (full string).
- [ ] Null amounts render as "-" not "$0.00".
- [ ] Refresh interval (60s) and `visibilitychange` listener active for claims section.
- [ ] Clicking a claim row opens detail panel (or logs selection) without page reload.
- [ ] Server logs verify no `patientName` values written to disk.

## 9. Executive Summary (5 bullets)
- **YES**, claims can be placed on Office Manager using the exact same optical pattern as the Mon–Thu patient list.
- **Reuse** the existing `GET /api/softdent/claims-outstanding` endpoint; no new SoftDent queries needed.
- **Add** section `#om-claims-outstanding` with a table rendering `patientName`, `payer`, `serviceDate`, `amount`, `status`, and age.
- **Switch** both the schedule list and the new claims list to display **full patient names** (operator PHI override for staff-only OM).
- **Honor** READ-ONLY, empty≠$0, and keep `patientName` out of logs even while showing it on screen.

## 10. Approval Checklist
**DO NOT APPLY until you reply "approve / proceed".**  
Reply with:
- [ ] "Approve claims placement on OM"  
- [ ] "Approve full names on lists" (schedule + claims)  
- [ ] Preferred default sort: `serviceDate` DESC vs age (oldest first)  
- [ ] Row limit cap (suggest 200)  

Once approved, I will generate the exact diff patches for the two OM files and the validation script.
