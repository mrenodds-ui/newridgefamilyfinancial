# Executive No-Scroll Viewport — Package 3 APPLIED

**Date:** 2026-07-16  
**Consult:** `MOONSHOT_EXECUTIVE_NO_SCROLL_VIEWPORT_2026-07-16.md`  
**Scope:** Package 3 Viewport-Locked Chrome only (Packages 1–2 preserved; Package 4 not started)  
**Effort posture:** Moonshot S (1–2 hrs)

## Concrete moves (Moonshot §4 Package 3)

| Move | Status |
|------|--------|
| `.chrome-frame { position: fixed; top: 36px; left: 220px; right: 0; height: 140px; z-index: 100; background: var(--vacuum) }` | PASS — measured fixed · left 220 · height 140 · z 100; `top: 32px` with ops-gates (no body banner after P2; Moonshot 36px assumed old banner) |
| Move eyebrow/h1/kicker/beam/ledge inside `.chrome-frame` | PASS — Package 2 letterhead (title/meta/status = eyebrow/h1/kicker + gold border beam) + `.ledge` inside frame on all 10 pages |
| Honesty in chrome-frame | **Kept as Package 1 body LED** (20px fixed bottom) so frame stays 140px money desk; still executive-visible |
| `.main` `margin-top: 140px` · height subtracts chrome | PASS — with ops: `margin-top: 172px` (32+140), height `888px` @ 1080p |

## Validation gate

| Check | Result (Claims @ 1920×1080) |
|-------|------------------------------|
| Frame stays locked on main scroll | **PASS** (`locked: true` after scrollTop 500) |
| Scroll only moves content below strip | **PASS** (`canScroll: true`; letterhead+ledge tops unchanged) |
| Kids0 = `chrome-frame` | PASS |
| Honesty LED still visible | PASS (fixed bottom) |

## Wire / nav

- Ops gates insert **before** `.shell` (not after in-frame banner)  
- Crumb + excel chip insert **after** `.chrome-frame` (scrollable)  
- Error rail after `.chrome-frame`  

## Files

- All `site/nr2-optical-page-*.html`  
- `site/nr2-optical-theme.css`  
- `site/nr2-optical-page-wire.js` · `site/nr2-optical-nav.js`  
- Backups: `docs/_p3_backups_2026-07-16/`  

## Not done

- Package 4 Tabbed Content Deck  
