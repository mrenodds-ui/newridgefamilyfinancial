# P0 Foundation — APPLIED 2026-07-16

## Shipped

| Item | Path |
|------|------|
| Beam drift diagnostics | `NewRidgeFinancial2/hal_brain_tools.py` (`beam_desk_proof` drift + `refreshCloseSuggested`) |
| Desk smoke drift hint | `NewRidgeFinancial2/desk_smoke.py` |
| VERIFY BEAM UI drift | `NewRidgeFinancial2/site/nr2-optical-page-wire.js` |
| Attended morning bundle CLI | `scripts/morning_bundle_attended.py` |
| Period-close beam refresh | `scripts/refresh_period_close_beam.py` |
| Desk smoke scheduled task installer | `scripts/install_desk_smoke_scheduled_task.ps1` |
| Unit test | `NewRidgeFinancial2/test_desk_smoke.py::test_beam_desk_proof_reports_drift` |

## Live validation (2026-07-16)

- `refresh_period_close_beam.py` synced close snapshot: SD $7,714 → $60,411 drift resolved
- `desk_ops_smoke.py --no-http` → **GREEN** · `deskProof=MATCH`
- `patientAttestEligible=true`

## Operator next (P0.1 attended)

1. Confirm SoftDent Output Options → **Excel** not greyed (`docs/runbooks/softdent_excel_enablement_nr2.md`)
2. Run: `python scripts/morning_bundle_attended.py` (interactive) or `--yes --refresh-close` after Excel enabled
3. Optional: `powershell scripts/install_desk_smoke_scheduled_task.ps1` for 5-min smoke log

## P1 next

Analytics page · Trellis AM proof schedule · claims ERA tile (see `NR2_CLOUD_PMS_AUGMENTATION_PLAN_2026-07-16.md`)
