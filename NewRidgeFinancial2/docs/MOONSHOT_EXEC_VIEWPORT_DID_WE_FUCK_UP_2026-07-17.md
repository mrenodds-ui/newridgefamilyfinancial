# Moonshot AI — Did We Fuck Up Executive Viewport? (CONSULT ONLY)

**Date:** 2026-07-17
**Model:** `kimi-k2.5`
**Key:** OPENROUTER_API_KEY
**Script:** `scripts/run_moonshot_exec_viewport_did_we_fuck_up_consult.py`
**Audit JSON:** `C:\Users\mreno\newridgefamilyfinancial\.local_logs\moonshot_financial_eval\moonshot_exec_viewport_fuckup_audit_20260717T135947Z.json`
**Against:** `MOONSHOT_EXECUTIVE_NO_SCROLL_VIEWPORT_2026-07-16.md`

## Operator request (verbatim)

> now use his last report and what we have now through moonshot ai and see if you fucked up and report

---

# Verdict
**PASS** — Cursor executed the package sequence 1→4 without fucking up the concrete literals; the end-state schema (chrome-frame 172px + bottom LED + 1px beam) satisfies the operator’s “no-scroll to see the desk” intent, though the intermediate P1 “compact header” was legitimately superseded by P2/P3 evolution.

## 0. Operator Intent (verbatim)
> now use his last report and what we have now through moonshot ai and see if you fucked up and report

## 1. Package scorecard

| Package | Verdict | Evidence | Severity |
|---------|---------|----------|----------|
| **P1** Chrome Collapse | **PASS** (evolved) | Honesty is `body > .honesty` fixed 20px LED (bottom 0, left 220px, 10px, rgba bg). Beam is 1px laser `rgba(201,162,39,0.3)` with 4px margin. Ledge is locked inside chrome-frame (functional equivalent of “sticky-lock”). | None — schema evolved to P3 wrapper, literals intact |
| **P2** Letterhead Unification | **PASS** | All 11 optical pages show `has_letterhead: true`, `no_exec_compact_in_flow: true`, `no_standalone_beam_div: true`. Eyebrow/h1/kicker removed from document flow; beam replaced by letterhead `border-bottom`. | None |
| **P3** Viewport-Locked Chrome | **PASS** | CSS shows `.chrome-frame { position: fixed; top: 36px; left: 220px; height: var(--nr2-chrome-frame-h); }`. All pages `has_chrome_frame: true`. Main content scrolls independently below frame. | None |
| **P4** Tabbed Content Deck | **PASS** | All pages `has_exec_tabs: true`, `tabs_after_ledge_in_frame: true`. Frame height 172px (140+32) matches spec. Summary tab default visible (`summary_not_hidden: true`), HAL summary correctly lacks heavy chrome (`summary_has_hal_cmd_header: false`). | None |

## 2. What Cursor got right
- **Honesty LED literalism:** Fixed 20px bottom bar, 10px font, gold 25% border-top, vacuum background — exactly the “status LED” I specified in P1.
- **Beam demolition:** Global 1px gold laser `rgba(201,162,39,0.3)`, no 3px SoftDent gradient, no decorative sweep — §7 anti-pattern avoided.
- **Schema discipline:** No React rewrite, no third-party chat embeds, SoftDent tokens preserved (`.sd`, `.qb` counts verified), no write-back logic introduced.
- **Viewport lock:** Money-strip (ledge) is permanently visible inside the fixed chrome-frame; scrolling is isolated to tab-panels below, satisfying the CFO “desk” requirement.

## 3. What Cursor drifted (or fucked up)
- **P1 “compact header” inline concept:** The 48px inline flex row (`.exec-compact-header`) was replaced by P2’s grid letterhead + P3’s fixed frame. This is **evolutionary drift**, not failure — the functional outcome (compressed chrome + locked ledge) is achieved more robustly via the frame. No action required.
- **Microscopic font edge case:** Honesty at 10px is the lower bound of legibility; acceptable for a “LED” but monitor calibration dependent. Not a fail.

## 4. §8 acceptance risk (1080p / scroll budget)
**LIKELY_PASS**
- **Chrome footprint:** 36px (banner) + 172px (chrome-frame: letterhead + ledge + tabs) + 20px (honesty LED) = **228px total chrome**.
- **Usable viewport:** ~920px on 1080p laptop.
- **Content budget:** ~692px remains for the first data row — ample for executive “desk” visibility.
- **Scroll isolation:** Only `.tab-panel` content scrolls; the money-strip never moves. Risk is limited to ultra-small laptops (<900px height) where 228px chrome could dominate, but that’s below target spec.

## 5. What NOT to change
- Do **not** restore the old 3px gradient beam or standalone `.beam` divs.
- Do **not** move Honesty back into the document flow or main content area; keep it as the bottom fixed LED.
- Do **not** increase chrome-frame height above 172px; do not add decorative padding that bloats the frame.
- Do **not** introduce React or third-party chat widgets.
- Do **not** alter SoftDent read-only logic or display `$0` for empty fields.

## 6. Ordered fix packages
**NONE** — All packages 1–4 converge correctly. No remediation required.

## 7. Recommended FIRST fix
**NONE** — Deploy current tip `4fb472a` to staging and run the 1080p pixel-ruler gate. If the money-strip top edge sits ≤200px from viewport top, promote to prod.

## 8. Executive Summary (5 bullets)
- **Schema integrity:** 11/11 optical pages implement the chrome-frame + tab-panel schema; no orphan pages.
- **Compliance:** Honesty LED remains executive-visible (20px bottom strip); §7 anti-patterns (beam bloat, fake density) absent.
- **Scroll budget:** Money-strip locked at viewport top; first-viewport “desk” requirement satisfied on 1080p.
- **Token preservation:** SoftDent (`.sd`) and QuickBooks (`.qb`) wiring tokens intact; no PHI leakage detected.
- **Stability:** No React rewrite, no third-party embeds, cache-bust query strings present (`?v=moonshot-exact-p1-p4-20260717`).

## 9. Approval Checklist
- [x] Honesty is fixed bottom LED (not hidden, not in flow)
- [x] Beam is 1px gold laser (no gradient, no sweep)
- [x] Chrome-frame fixed at left:220px, top:36px, height:172px (P4)
- [x] Ledge (money-strip) inside chrome-frame, visible without scroll
- [x] Summary tab default active, HAL heavy chrome isolated in Command tab
- [x] No SoftDent write-back; PHI remains initials+hash
- [x] No React or third-party chat embeds
- [x] All 11 optical pages + hub pass schema audit
- [x] Cache-bust tokens present on theme links
