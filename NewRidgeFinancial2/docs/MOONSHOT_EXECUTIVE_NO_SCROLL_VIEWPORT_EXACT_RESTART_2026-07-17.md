# Executive No-Scroll Viewport — Exact Restart (Packages 1→4)

**Date:** 2026-07-17  
**Consult:** `MOONSHOT_EXECUTIVE_NO_SCROLL_VIEWPORT_2026-07-16.md`  
**Operator request:** start over from the beginning and implement Moonshot’s report exactly.

## Method

1. Backed up live site → `docs/_moonshot_exact_restart_2026-07-17/`
2. Replayed applied package commits in order onto optical site files:
   - Package 1 complete → `a903357`
   - Package 2 → `2be2bc0`
   - Package 3 → `96be875`
   - Package 4 → `d5918bc`
   - Hub parity → `5a33f69`
3. Corrected Package 1 / §7 drift left in later package trees:
   - Global `.beam` restored to **1px gold laser** (`rgba(201,162,39,0.3)` · no sweep / no 3px SoftDent gradient)
4. Package 4 density: HAL **Summary** = single summary line; heavy HAL chrome lives in **Command**
5. Landing honesty LED restored (Package 1 / §8)
6. Cache-bust: `?v=moonshot-exact-p1-p4-20260717` on optical HTML theme links
7. `money-gap` kept (post-P4 page already on chrome-frame + tabs schema)

## End-state schema (all `nr2-optical-page-*.html`)

```
<main>
  <div class="chrome-frame">
    <header class="banner exec-letterhead">…</header>   <!-- P2 ≤48px; beam = border-bottom -->
    <div class="ledge">…money strip…</div>              <!-- P1/P3 locked desk -->
    <nav class="exec-tabs">…Summary default…</nav>      <!-- P4 -->
  </div>
  <div class="tab-panel" data-tab-panel="summary">…</div>
  …other tab-panels…
</main>
<div class="honesty">…</div>   <!-- P1 body LED; not hidden -->
```

## CSS literals (consult)

| Package | Rule | Live |
|---------|------|------|
| 1 | `.beam` 1px · `rgba(201,162,39,0.3)` · margin 4px 0 | PASS |
| 1 | `body > .honesty` fixed · bottom 0 · left 220px · height 20px · 10px | PASS |
| 1 | `.exec-compact-header` inline 12px (kept for P1 gate / fallback) | PASS |
| 2 | letterhead ≤48px · gold `border-bottom` replaces beam div | PASS |
| 3 | `.chrome-frame` fixed · left 220px · desk 140px | PASS (base 140; see P4) |
| 4 | tabs after ledge · frame **172px** (140+32) | PASS |

## Gates

- `scripts/run_package4_viewport_gate.py` → `pass_static: true`
- `scripts/run_viewport_hub_parity_gate.py` → `pass_static: true`

## SoftDent

Untouched (operator hard stop still active).
