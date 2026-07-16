# Executive No-Scroll Viewport — Package 1 APPLIED

**Date:** 2026-07-16  
**Consult:** `MOONSHOT_EXECUTIVE_NO_SCROLL_VIEWPORT_2026-07-16.md`  
**Operator:** proceed exactly as moonshot ordered · no deviate  
**Scope:** Package 1 Chrome Collapse Protocol only (Packages 2–4 not applied)

## Shipped

| Item | Path / behavior |
|------|-----------------|
| Theme collapse CSS | `nr2-optical-theme.css` — `.exec-compact-header`, laser `.beam`, `body > .honesty` LED, sticky `.main > .ledge`, `.main` height `calc(100dvh - 36px - 20px)` (+ ops-gates 68px variant) |
| HTML schema (10 pages) | All `nr2-optical-page-*.html` — `.ledge` first child of `<main>`; eyebrow/h1/kicker in `.exec-compact-header`; honesty moved to `body` (fixed bottom LED) |
| HAL extra chrome | `nr2-optical-page-hal.html` — `.hal-cmd-header` kept after compact header, before beam |
| Crumb placement | `nr2-optical-nav.js` — crumb inserts after `.ledge` so money-strip stays first child |
| Excel probe chip | `nr2-optical-page-wire.js` — anchors after `.beam` / `.exec-compact-header` (not under fixed honesty LED) |
| Motion grammar | Theme motion selectors include `.ledge` + `.exec-compact-header` |

## Validation gate (Moonshot §4 / §8)

- Money-strip (`.ledge`) is first in `<main>` and sticky — first viewport shows the desk without scrolling past letterhead stack.
- Honesty visible as 20px bottom LED (`body > .honesty`, left 220px).
- Scroll budget: content below the strip scrolls inside `.main`; strip stays sticky.
- Tokens unchanged: `.sd` / `.qb` / `.hal` / `.exec-currency` retained; empty ≠ `$0` unchanged.
- No React rewrite · no file renames · no Packages 2–4.

## Not done (out of scope)

- Package 2 Executive Letterhead Unification  
- Package 3 Viewport-Locked Chrome frame  
- Package 4 Tabbed Content Deck  
- Hub / beam-touch mockup (not in Package 1 REAL files list)
