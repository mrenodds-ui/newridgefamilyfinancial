# Executive No-Scroll Viewport — Package 1 APPLIED (gate evidence)

**Date:** 2026-07-16  
**Consult:** `MOONSHOT_EXECUTIVE_NO_SCROLL_VIEWPORT_2026-07-16.md`  
**Scope:** Package 1 Chrome Collapse Protocol **only** (Packages 2–4 not started)  
**Effort posture:** Moonshot M (2–3 hrs) — schema audit → CSS exactness → pilot AR → Claims/SoftDent/HAL fold measures → height budget fix

## Concrete moves (Moonshot §4) — checklist

| Move | Status |
|------|--------|
| `.ledge` first child of `<main>` on all `nr2-optical-page-*.html` | PASS (10/10; crumb injects *after* ledge) |
| `.honesty` moved to `body` (not in main) | PASS |
| `.exec-compact-header` wraps eyebrow / h1 / kicker · inline 12px · **height 48px** | PASS (measured) |
| `.beam` laser · height 1px · `rgba(201,162,39,0.3)` · margin 4px 0 | PASS (measured 1px) |
| `body > .honesty` fixed bottom LED · left 220px · height 20px · font 10px · z-index 200 | PASS (measured) |
| `.main > .ledge` sticky · top 0 · z-index 50 · background `var(--vacuum)` | PASS (sticky holds at shell top after scroll) |
| `.main` `padding-top: 0` · `overflow-y: auto` · height subtracts banner + honesty | PASS (+ letterhead/ops variants below) |

## What NOT to change (Moonshot §6) — spot check

- SoftDent tokens `.sd` present on SoftDent/Claims faces  
- Empty shows `empty (not zero)` / `∅` — not `$0`  
- No file renames · no React · no Packages 2–4  
- Honesty remains visible (bottom LED), not hidden

## Validation gate (Moonshot §4 / §8) — live 1920×1080 @ 100% zoom

Server: `https://127.0.0.1:8765` · CDP `Emulation.setDeviceMetricsOverride` 1920×1080

| Page | Ledge in first viewport | Sticky holds | Honesty LED | Compact 48px / beam 1px | Notes |
|------|-------------------------|--------------|-------------|-------------------------|-------|
| **AR** (pilot) | PASS | PASS | PASS | PASS | `canScroll=false` (full desk fits) |
| **SoftDent** | PASS | — | PASS | PASS | `emptyZero=false` · `.sd` tokens live |
| **Claims** | PASS | PASS (scroll 400 → ledge top stays at shell) | PASS | PASS | RUN SMOKE + filters in first viewport; list scrolls below strip |
| **HAL** | PASS | PASS | PASS | PASS | RUN SMOKE in view; chat body scrolls below strip |

### Height budget fix (Package 1 only)

Prior E1 injects `#nr2-exec-letterhead` (48px) under the banner. Moonshot’s `calc(100dvh - 36px - 20px)` alone left `.main` overflowing the honesty LED.

Applied variants in `nr2-optical-theme.css`:

- `body:has(#nr2-exec-letterhead) .main` → `calc(100dvh - 36px - 48px - 20px)`
- `body.has-ops-gates:has(#nr2-exec-letterhead) .main` → `calc(100dvh - 116px - 20px)`
- Matching `.shell` `min-height` subtracts the same chrome + 20px honesty

Claims remeasure after fix: `mainHeightCss=944px` (= 1080 − 116 − 20).

### Cascade fix

Later `.main .kicker` rules were re-inflating the compact row. Added higher-specificity `.main > .exec-compact-header …` resets; compact row forced `height/max-height: 48px` · `flex-wrap: nowrap`.

## Approval checklist (Moonshot §10)

- [x] 1080p primary target used for gate  
- [x] Package 1 CSS in theme  
- [x] HTML schema on all optical pages (pilot AR measured first in this pass)  
- [x] Visual: money-strip visible without scroll; no purple/cream introduced  
- [x] SoftDent tokens / empty ≠ `$0`  
- [x] Honesty ≥ 10px bottom LED visible in first viewport  
- [ ] Operator sign-off on 1px laser beam (awaiting you)  
- [ ] Packages 2–4 — **not applied** until you approve Package 1

## Not done

- Package 2 Executive Letterhead Unification  
- Package 3 Viewport-Locked Chrome frame  
- Package 4 Tabbed Content Deck  
- Hub / beam-touch mockup (outside Package 1 REAL files)
