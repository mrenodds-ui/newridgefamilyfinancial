# Executive No-Scroll Viewport — Hub Parity (Track A) APPLIED

**Date:** 2026-07-16  
**Consult:** `MOONSHOT_EXECUTIVE_NO_SCROLL_VIEWPORT_2026-07-16.md`  
**Plan:** Next after Viewport Package 4 → **Track A**  
**Scope:** Alignment Hub chrome parity with Packages 2–4; Landing left as-is (already viewport-fit)

## Concrete moves

| Move | Status |
|------|--------|
| Hub: `#nr2-page-letterhead` + `.chrome-frame` + `.ledge` money strip | PASS |
| Hub: `.exec-tabs` after ledge (Summary · Bench) | PASS |
| Hub: heavy `.align-bench` in Bench tab; default Summary | PASS |
| Hub: honesty body LED (Package 1) | PASS |
| Hub asymmetric: chrome-frame spans main column only (rail visible) | PASS — @1920 left 240 · right before rail |
| Landing chrome-frame retrofit | **Skipped** — already `overflow: hidden` + `exec-landing-ledge` money faces |

## Validation (Hub @ 1920×1080)

| Check | Result |
|-------|--------|
| Static schema + theme + landing checks | **PASS** |
| Money-strip + tabs in first viewport | **PASS** |
| Bench panel hidden until tab select | **PASS** |
| Frame locked on main scroll | **PASS** |
| HTTP hub | **PASS** |

## Files

- `site/nr2-optical-pages-hub.html`
- `site/nr2-optical-theme.css` (hub chrome-frame left/right rules)
- Gate: `scripts/run_viewport_hub_parity_gate.py` → `docs/_viewport_hub_gate_runs/`
- Backups: `docs/_viewport_hub_backups_2026-07-16/`

## Not done (per plan)

- Track B ops / morning_bundle resuscitation (await operator)
- Re-applying E1–E4
