# Executive No-Scroll Viewport — Package 1 APPLIED (M effort 2–3 hrs)

**Date:** 2026-07-16  
**Consult:** `MOONSHOT_EXECUTIVE_NO_SCROLL_VIEWPORT_2026-07-16.md`  
**Effort:** Moonshot **M (2–3 hrs)** — backups → exact CSS → §8 sticky stack → all-page 1080p → all-page 1440p → paced re-verify loop  
**Scope:** Package 1 only (Packages 2–4 **not** started)

## §10 Backup (done)

| File | Backup |
|------|--------|
| `nr2-optical-theme.css` | `docs/_p1_backups_2026-07-16/nr2-optical-theme.css.bak` |
| `nr2-optical-page-ar.html` (pilot) | `docs/_p1_backups_2026-07-16/nr2-optical-page-ar.html.bak` |

## Concrete moves (Moonshot §4)

| Move | Evidence |
|------|----------|
| `.ledge` first child of `<main>` | Static schema 10/10 + browser `kids0=ledge` |
| `.honesty` at end of `<body>` (fixed LED) | Schema + measured `position:fixed`, 20px, 10px, bottom LED |
| `.exec-compact-header` inline 12px / 48px row | Measured `compactH=48` all pages |
| `.beam` 1px gold laser | Measured `beamH=1` |
| `.ledge` sticky top 0 | `ledgeStickyOk=true` |
| `.main` height `calc(100dvh - 36px - 20px)` (+ letterhead/ops variants) | Theme + live `mainHeight` |
| §8 header+strip stable | Sticky ledge + compact (+ HAL cmd header) + beam via `--nr2-ledge-sticky-h` ResizeObserver |
| Crumb not between strip and title | Inserts after `.beam` / compact |

## Anti-pattern controls (§7)

- Reduced `.main > .ledge` glass signature pad (density)  
- Compact header `nowrap` / hard 48px (no wrap bloat)  
- Honesty remains visible LED (not tooltip)  
- No React / no renames / no purple-cream palette drift  

## Validation gate evidence

### Static (`scripts/run_package1_viewport_gate.py`)

- Latest: `docs/_p1_gate_runs/p1_gate_latest.json`  
- `pass_static: true` (theme concrete moves + schema + HTTP 200)

### 1080p 1920×1080 (`p1_browser_1080_full.json`)

- **allPass: true** (9 pages in file + AR pilot CDP pass)  
- Criteria: ledge in view, compact 48, beam 1, honesty fixed LED, empty≠`$0`, CLS shift 0 on honesty text update, sticky stack OK  

### 1440p 2560×1440 (`p1_browser_1440_full.json`)

- **allPass: true** (10/10 `deskPass`)  
- Criteria: ledge+compact fully visible; first content section below beam starts in viewport without scroll  

### Paced M-effort loop

- Shell loop every **25 minutes × 6 ticks (~2.5 hours)** re-runs static gate  
- Sentinel: `AGENT_LOOP_TICK_p1gate`  
- On each tick: confirm `pass_static`; Package 1 fixes only; never start Packages 2–4  

## §10 Approval checklist

- [x] 1080p primary target used  
- [x] Backups taken  
- [x] Package 1 CSS applied  
- [x] HTML schema on all optical pages (pilot AR first historically; full matrix re-verified)  
- [x] Visual/measure: money-strip visible; sticky scroll budget  
- [x] SoftDent tokens / empty ≠ `$0`  
- [x] Honesty ≥10px bottom LED  
- [ ] Operator sign-off on 1px laser beam  
- [x] Packages 2–4 held until Package 1 sign-off  

## Files touched this M-effort pass

- `site/nr2-optical-theme.css` — sticky stack, ledge density, height budget  
- `site/nr2-optical-nav.js` — crumb after beam  
- `site/nr2-optical-page-wire.js` — `--nr2-ledge-sticky-h` / `--nr2-hal-hdr-h`  
- `scripts/run_package1_viewport_gate.py` — static gate runner  
- `docs/_p1_gate_runs/*` — evidence artifacts  
- `docs/_p1_backups_2026-07-16/*` — §10 backups  

## Not done

- Package 2 / 3 / 4  
- Operator laser-beam sign-off (awaiting you)
