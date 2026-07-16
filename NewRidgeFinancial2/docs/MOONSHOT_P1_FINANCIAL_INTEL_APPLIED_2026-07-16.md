# P1 Financial Intelligence — APPLIED 2026-07-16

## Shipped

| Package | Files |
|---------|-------|
| ERA inbox local module (replaces removed apex pack) | `NewRidgeFinancial2/nr2_era_inbox.py` |
| Route wiring | `apex_backend.py`, `softdent_practice_exports.py`, `nr2_hal_gateway.py`, `softdent_gold_era_settlement_hal10608.py` |
| Claims ERA tile | `site/nr2-optical-page-claims.js` → `GET /api/apex/hal/era-inbox/status` |
| Analytics / morning huddle page | `site/nr2-optical-page-analytics.html`, `nr2-optical-page-analytics.js` |
| Nav + hub link | `nr2-optical-nav.js`, `nr2-optical-pages-hub.html`, `nr2-optical-pages-hub.js` |
| Tests | `test_nr2_era_inbox.py` |

## Validation

- `pytest test_nr2_era_inbox.py` — PASS
- In-process `era_inbox_status()` — `chipStatus=awaiting`, `emptyNotZero=true`
- **Restart NR2 server** to load `nr2_era_inbox` on HTTP routes (live server may still show old `apex_era835_pack` error until restart)

## Operator next

1. Restart NR2 browser/workstation server
2. Open `/nr2-optical-page-analytics.html` for morning huddle
3. Claims page ERA tile should show inbox chip (not UNAVAILABLE)
4. P0.1 still pending: attended SoftDent Excel morning bundle when ready

## P1 backlog remaining

- Trellis AM proof scheduled task verification (`prove_trellis_withbenefits_am.py`)
- ERA ingest with real 835 drop
- QB AP/payroll CSV drop (optional)
