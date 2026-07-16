# Executive No-Scroll Viewport — Package 4 APPLIED

**Date:** 2026-07-16  
**Consult:** `MOONSHOT_EXECUTIVE_NO_SCROLL_VIEWPORT_2026-07-16.md`  
**Scope:** Package 4 Tabbed Content Deck (Packages 1–3 preserved)  
**Effort posture:** Moonshot L (6–8 hrs across pages)

## Concrete moves (Moonshot §4 Package 4)

| Move | Status |
|------|--------|
| Insert `.exec-tabs` immediately after `.ledge` | PASS — inside `.chrome-frame` on all 10 optical pages |
| Wrap heavy sections in `.tab-panel` | PASS — Claims / HAL / AR / Analytics / OM / SoftDent; Summary-only on ledge pages |
| Vanilla JS `display: none / block` toggle | PASS — `bootExecTabs()` in `nr2-optical-page-wire.js` (hidden attr + CSS) |
| Default **Summary** tab | PASS — always activates `summary` on boot |
| First viewport = money-strip + tabs | PASS — chrome-frame height **172px** (140 desk + 32 tabs) |

## Tab map

| Page | Tabs |
|------|------|
| Claims | Summary · Outstanding |
| HAL | Summary · Command |
| A/R | Summary · Detail |
| Analytics | Summary · MTD Metrics · Gates & Recall |
| Office Manager | Summary · This Week · Trellis Tomorrow |
| SoftDent | Summary · PHI Sample |
| Content / Narratives / QB / Taxes | Summary only |

## Validation gate

| Check | Result (Claims @ 1920×1080) |
|-------|------------------------------|
| Static schema (10 pages + theme + wire) | **PASS** (`pass_static: true`) |
| Money-strip + tab bar in first viewport | **PASS** |
| Outstanding (heavy) hidden until tab select | **PASS** (`outstandingHidden: true`) |
| Frame locked on main scroll | **PASS** (`frameLockedOnScroll: true`) |
| HTTP Claims | **PASS** |

## Files

- All `site/nr2-optical-page-*.html`
- `site/nr2-optical-theme.css` (`--nr2-chrome-frame-h: 172px`, `.exec-tabs`, `.tab-panel`)
- `site/nr2-optical-page-wire.js` (`bootExecTabs`)
- Apply helper: `scripts/apply_package4_tabbed_deck.py`
- Gate: `scripts/run_package4_viewport_gate.py` → `docs/_p4_gate_runs/`
- Backups: `docs/_p4_backups_2026-07-16/`

## Honesty / tokens

- Body honesty LED unchanged (Package 1)
- `.sd` / `.qb` / `.hal` faces retained on ledges
- empty ≠ $0 copy preserved in Summary blurbs
