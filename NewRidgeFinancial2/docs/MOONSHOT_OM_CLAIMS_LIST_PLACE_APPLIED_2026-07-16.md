# OM Claims List + Full Names — APPLIED

**Date:** 2026-07-16  
**Consult:** `MOONSHOT_OM_CLAIMS_LIST_PLACE_2026-07-16.md`  
**Operator:** proceed

## Shipped

| Item | Where |
|------|--------|
| Outstanding claims section | `#om-claims-outstanding` in `site/nr2-optical-page-office-manager.html` |
| Fetch + render (oldest first, cap 200) | `GET /api/softdent/claims-outstanding?limit=200` in `nr2-optical-page-office-manager.js` |
| Full patient names on Mon–Thu schedule | Slot + next-hint use `patientName` (hash stays in tooltip) |
| Full names on claims table | `claim.patientName` column |
| `nextPatient.patientName` | `nr2_softdent_daily.py` next-hint payload |
| Claims table CSS + print | `site/nr2-optical-theme.css` |

## Honesty

- SoftDent read-only; empty ≠ $0 (null/zero amounts render as —)
- Staff OM shows full names; logs/HAL handoff still use hash/id
- `sd_claims` has no `patient_id` — claim row click highlights + summarizes; dossier still via schedule click
- Trellis huddle still initials+hash until that API ships `patientName`

## How to try

1. Hard-refresh Office Manager.
2. Confirm Mon–Thu rows show full names (not initials · hash).
3. Scroll to **Outstanding Claims** — names, payer, service, amount, status, age; oldest first.
4. Click a claim row → summary line updates; Refresh reloads.
