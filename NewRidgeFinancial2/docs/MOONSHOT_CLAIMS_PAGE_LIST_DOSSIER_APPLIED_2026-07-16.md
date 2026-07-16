# Claims List on Claims Page + Click Context — APPLIED

**Date:** 2026-07-16  
**Prior:** `MOONSHOT_OM_CLAIMS_LIST_PLACE_APPLIED_2026-07-16.md` (OM placement)  
**Operator:** prefer Claims page · click claim like schedule

## Shipped

| Item | Where |
|------|--------|
| Outstanding claims list + side panel | `site/nr2-optical-page-claims.html` |
| Fetch, oldest-first, click → dossier | `site/nr2-optical-page-claims.js` |
| `patientId` / hash via name join | `nr2_softdent_daily.claims_outstanding` |
| Removed claims block from OM | `nr2-optical-page-office-manager.html/.js` |
| List + dossier layout CSS | `nr2-optical-theme.css` (`.om-claims-body.has-dossier`) |

## Behavior

1. Open **Claims** page → Outstanding Claims table (full names).
2. Click a row → claim fields + SoftDent mini dossier (when name joins to `sd_patients`).
3. **Ask HAL about this patient** when patient id resolved.
4. OM keeps Mon–Thu schedule with full names; no claims list there.

## Honesty

- SoftDent read-only · empty ≠ $0
- Name join may miss → claim-only panel (no invent patient id)
