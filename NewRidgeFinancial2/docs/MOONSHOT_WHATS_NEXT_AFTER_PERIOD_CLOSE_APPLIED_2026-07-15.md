# Moonshot AI — Optical Bench Money-Beam Binding (APPLIED)

**Date:** 2026-07-15  
**Build:** `nr2-12028-optical-beam-bind`  
**Consult:** `MOONSHOT_WHATS_NEXT_AFTER_PERIOD_CLOSE_2026-07-15.md`  
**Operator:** approve

## What shipped

Optical SoftDent/QB money headlines now cite the same live beams HAL uses:

1. **`nr2-optical-page-wire.js`** — `getMoneyBeams`, `honestyMoney`, `applyBeamHeadline`, `beamProvenanceLine`
2. **A/R / SoftDent / QB pages** — SoftDent AR + QB monthly revenue headlines prefer `/api/hal/tools/money-beams`
3. **Laser honesty** — red `alignmentLasers` / `importStale` → `STALE / ∅` or `NO SIGNAL` on headlines (never invent `$0`)
4. **Provenance** — banner/hints include `beamHash` + timestamp (+ period-close when present)
5. **API** — `GET /api/hal/tools/money-beams` now injects `_get_import_readiness()` into attestation

Real paths (not invent invented `templates/optical/`):

- `site/nr2-optical-page-ar.{html,js}`
- `site/nr2-optical-page-softdent.{html,js}`
- `site/nr2-optical-page-quickbooks.{html,js}`
- `site/nr2-optical-page-wire.js`
- `nr2_http_server.py`

## SoftDent doctrine

- Write-back still **FORBIDDEN**
- empty ≠ $0
- Domain APIs still feed buckets / production / cash / NI (beams attest SoftDent claims + QB monthly revenue)

## Validation

- Beams endpoint returns SoftDent `$7,714` / QB `$78,399` with readiness-aware `importStale`
- Optical pages show beamHash provenance in banner/hints when LIVE
- When lasers red, SoftDent/QB headlines suppress dollars

## Not done (runner-ups)

- SoftDent GUI Excel path hardening  
- BlueNote alerts on stalled period-close  
- Force Close optical control  
