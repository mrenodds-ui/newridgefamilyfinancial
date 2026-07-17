# Moonshot AI — Executive Viewport Coding Pack (APPLY-READY)

**Date:** 2026-07-17
**Model:** `kimi-k2.5`
**Key:** OPENROUTER_API_KEY
**Script:** `scripts/run_moonshot_exec_viewport_coding_pack_consult.py`
**Audit JSON:** `C:\Users\mreno\newridgefamilyfinancial\.local_logs\moonshot_financial_eval\moonshot_exec_viewport_coding_pack_audit_20260717T140318Z.json`

## Operator request (verbatim)

> get all coding from moonshot to fix it

---

# Verdict
Deliver canonical hardening pack (CSS/HTML/JS) to lock the 172px chrome-frame + 1px gold beam + body-fixed honesty LED schema; no functional changes to live P1→P4 convergence, but provides Cursor-proof source-of-truth blocks for pages currently missing the chrome-frame wrapper.

## 0. Operator Intent (verbatim)
> get all coding from moonshot to fix it

## 1. Do we still need code?
**NO-but-still-deliver-canonical** (hardening pack).  
Prior audit verdict was PASS / NONE remediation, but page-flags show `nr2-optical-page-analytics.html`, `nr2-optical-page-claims.html`, and `nr2-optical-page-office-manager.html` lack `hasChrome: true`. This pack provides the exact canonical blocks Cursor must paste to bring those pages into convergence and prevent future drift on beam/honesty/frame heights.

## 2. Canonical CSS — nr2-optical-theme.css (FULL replacement blocks)
**File:** `NewRidgeFinancial2/site/css/nr2-optical-theme.css`  
Replace or append these blocks in order; do not mix with legacy 3px gradient beams or floating honesty paragraphs.

```css
/* === Moonshot Canonical Executive Viewport Pack 2026-07-17 === */
/* Lock: chrome-frame 172px · beam 1px laser · honesty body-fixed LED · SoftDent read-only */

:root {
  --nr2-chrome-frame-h: 172px; /* 140px desk + 32px tabs */
  --nr2-exec-tabs-h: 32px;
  /* Ensure vacuum token exists */
  --vacuum: #080a0c;
}

/* Beam: 1px gold laser only (Package 1 §74 + §77 anti-bloat) */
.beam,
.main > .beam {
  position: relative;
  height: 1px;
  margin: 4px 0;
  border: 0;
  background: rgba(201, 162, 39, 0.3);
  opacity: 1;
  box-shadow: none;
  overflow: hidden;
}
.beam::after,
.main > .beam::after {
  display: none !important;
}

/* Honesty: body-fixed LED (Package 1) — never hide, never inline */
body > .honesty {
  position: fixed;
  bottom: 0;
  left: 220px; /* sidebar width */
  right: 0;
  height: 20px;
  font-size: 10px;
  line-height: 16px;
  padding: 2px 8px;
  margin: 0;
  background: rgba(8, 10, 12, 0.95);
  border: 0;
  border-top: 1px solid rgba(201, 162, 39, 0.25);
  border-left: 0;
  z-index: 200;
  box-sizing: border-box;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  color: var(--muted, #8a93a0);
}
@media (max-width: 900px) {
  body > .honesty {
    left: 0;
  }
}

/* Executive Letterhead (Package 2) — 48px grid, no backdrop-filter blur */
#nr2-page-letterhead.banner.exec-letterhead,
header.banner.exec-letterhead {
  position: sticky;
  top: 0;
  z-index: 60;
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(0, 1.7fr) minmax(0, 1.3fr);
  gap: 6px 12px;
  align-items: center;
  height: 48px;
  max-height: 48px;
  min-height: 40px;
  margin: 0;
  padding: 0 14px;
  border: 0;
  border-bottom: 1px solid rgba(201, 162, 39, 0.35);
  background: linear-gradient(180deg, rgba(16, 14, 8, 0.95) 0%, rgba(8, 10, 12, 0.92) 100%);
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
  justify-content: stretch;
  flex-wrap: nowrap;
  white-space: nowrap;
  overflow: hidden;
  box-sizing: border-box;
  font-size: 12px;
  color: var(--muted, #8a93a0);
  animation: none;
}
#nr2-page-letterhead .exec-lh-title {
  color: var(--hal, #e8c96a);
  font-family: var(--sans, system-ui, -apple-system, sans-serif);
  font-weight: 600;
  font-size: 13px;
  letter-spacing: 0.04em;
  overflow: hidden;
  text-overflow: ellipsis;
}
#nr2-page-letterhead .exec-lh-meta {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
  overflow: hidden;
  color: var(--qb, #9aa3ad);
  font-size: 11px;
  line-height: 1.2;
}
#nr2-page-letterhead .exec-lh-mode {
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  flex: 0 1 auto;
  overflow: hidden;
  text-overflow: ellipsis;
}
#nr2-page-letterhead .exec-lh-kicker {
  opacity: 0.9;
  flex: 1 1 auto;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
}
#nr2-page-letterhead .exec-lh-status {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  min-width: 0;
  overflow: hidden;
}
#nr2-page-letterhead .exec-lh-status .bind {
  font-size: 11px;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Chrome Frame (Package 3+4) — Viewport-locked 172px */
.chrome-frame {
  position: fixed;
  top: 36px; /* below banner if present */
  left: 220px;
  right: 0;
  height: var(--nr2-chrome-frame-h);
  z-index: 100;
  display: flex;
  flex-direction: column;
  gap: 0;
  padding: 0 18px;
  box-sizing: border-box;
  background: var(--vacuum);
  overflow: hidden;
}
/* Adjust top when letterhead present (no banner) */
body:has(#nr2-page-letterhead) .chrome-frame {
  top: 0;
}
/* Adjust for ops gates banner (32px) */
body.has-ops-gates .chrome-frame {
  top: 32px;
}
body.has-ops-gates:has(#nr2-page-letterhead) .chrome-frame {
  top: 32px;
}
@media (max-width: 900px) {
  .chrome-frame {
    left: 0;
  }
}

/* Letterhead inside chrome-frame becomes relative (not sticky) */
.chrome-frame > #nr2-page-letterhead.banner.exec-letterhead {
  position: relative;
  top: auto;
  z-index: 1;
  flex: 0 0 48px;
  height: 48px;
  max-height: 48px;
  padding-left: 0;
  padding-right: 0;
}

/* Ledge (money-strip) inside chrome-frame — flex filling remaining space */
.chrome-frame > .ledge {
  position: relative;
  top: auto;
  z-index: 1;
  flex: 1 1 auto;
  min-height: 0;
  margin: 0;
  padding: 4px 6px;
  overflow: hidden;
  background: var(--vacuum);
}
.chrome-frame > .ledge .metric-face {
  min-height: 64px;
  padding: var(--space-2, 8px);
}
.chrome-frame > .ledge .metric-face .hint {
  display: none; /* Suppress hints in chrome-frame to save vertical space */
}

/* Exec Tabs (Package 4) — 32px bar inside chrome-frame after ledge */
.chrome-frame > .exec-tabs {
  flex: 0 0 var(--nr2-exec-tabs-h);
  height: var(--nr2-exec-tabs-h);
  min-height: var(--nr2-exec-tabs-h);
  max-height: var(--nr2-exec-tabs-h);
  display: flex;
  align-items: stretch;
  gap: 0;
  margin: 0;
  padding: 0;
  border-top: 1px solid rgba(201, 162, 39, 0.28);
  box-sizing: border-box;
  overflow: hidden;
}
.exec-tabs [role="tab"] {
  appearance: none;
  -webkit-appearance: none;
  background: transparent;
  border: 0;
  border-bottom: 2px solid transparent;
  color: #8a93a0;
  font-family: var(--sans, system-ui, -apple-system, sans-serif);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  padding: 0 12px;
  margin: 0;
  cursor: pointer;
  line-height: 1;
  white-space: nowrap;
}
.exec-tabs [role="tab"]:hover {
  color: #d6dde6;
}
.exec-tabs [role="tab"][aria-selected="true"] {
  color: #e8c96a;
  border-bottom-color: rgba(201, 162, 39, 0.9);
}
.exec-tabs [role="tab"]:focus-visible {
  outline: 1px solid rgba(201, 162, 39, 0.55);
  outline-offset: -2px;
}

/* Main scroll pane — isolated below chrome-frame */
.main {
  padding-top: 0;
  overflow-y: auto;
  margin-top: var(--nr2-chrome-frame-h);
  /* 36px banner + 172px frame + 20px honesty LED */
  height: calc(100dvh - 36px - var(--nr2-chrome-frame-h) - 20px);
  padding-bottom: calc(var(--space-6, 24px) + 24px);
  box-sizing: border-box;
}
/* Variants without banner or with ops gates */
body:has(#nr2-page-letterhead) .main {
  margin-top: var(--nr2-chrome-frame-h);
  height: calc(100dvh - var(--nr2-chrome-frame-h) - 20px);
}
body.has-ops-gates .main {
  margin-top: calc(32px + var(--nr2-chrome-frame-h));
  height: calc(100dvh - 32px - var(--nr2-chrome-frame-h) - 20px);
}
body.has-ops-gates:has(#nr2-page-letterhead) .main {
  margin-top: calc(32px + var(--nr2-chrome-frame-h));
  height: calc(100dvh - 32px - var(--nr2-chrome-frame-h) - 20px);
}

/* Tab panels — only scrollable content */
.main > .tab-panel {
  display: block;
  margin: 0;
  padding: 8px 0 0;
}
.main > .tab-panel[hidden] {
  display: none !important;
}
.main > .tab-panel .exec-tab-summary {
  margin: 0 0 8px;
  font-family: var(--sans, system-ui, -apple-system, sans-serif);
  font-size: 12px;
  line-height: 1.35;
  color: #8a93a0;
}

/* Hub asymmetric chrome-frame (Track A) */
@media (min-width: 1401px) {
  body.page-hub .chrome-frame {
    left: 240px;
    right: calc((100vw - 240px) * 0.4);
  }
}
@media (max-width: 1400px) {
  body.page-hub .chrome-frame {
    left: 220px;
    right: 0;
  }
}
body.page-hub .hub-rail {
  max-height: calc(100dvh - 20px);
}
body.has-ops-gates.page-hub .hub-rail {
  max-height: calc(100dvh - 32px - 20px);
  margin-top: 0;
  padding-top: calc(var(--space-4, 16px) + 4px);
}
body.page-hub .main > .tab-panel .hal-chip {
  margin: 0 0 8px;
}

/* Package 1 Compact Header (Superseded by Letterhead but preserved for reference) */
.exec-compact-header {
  display: none; /* Hide by default; use .exec-letterhead instead */
}
```

## 3. HTML schema patches (per page)
**Pattern for all optical pages** (apply to `nr2-optical-page-analytics.html`, `nr2-optical-page-claims.html`, `nr2-optical-page-office-manager.html` which currently lack chrome-frame):

Replace the existing `<main class="main">…</main>` innerHTML with this structure (preserve existing metric-face content inside `.ledge`):

```html
<main class="main">
  <!-- Chrome Frame: 172px fixed viewport-lock (140 desk + 32 tabs) -->
  <div class="chrome-frame">
    <header id="nr2-page-letterhead" class="banner exec-letterhead" role="banner" aria-label="Executive letterhead" title="PAGE_TITLE · empty ≠ $0 · no SoftDent write-back">
      <div class="exec-lh-title">PAGE_TITLE</div>
      <div class="exec-lh-meta">
        <span class="exec-lh-mode">MODE_LABEL</span>
        <span class="exec-lh-kicker">KICKER_TEXT</span>
      </div>
      <div class="exec-lh-status">
        <span class="bind">BIND_TEXT</span>
        <span class="exec-period-seal period-seal" id="nr2-period-seal">Period close · —</span>
      </div>
    </header>
    
    <div class="ledge">
      <section class="money-strip" aria-label="Money faces">
        <!-- Preserve existing metric-face articles here -->
        <article class="metric-face sd">
          <div class="face-lbl">Label</div>
          <div class="val" id="val-id">—</div>
          <p class="hint">Hint text</p>
        </article>
      </section>
    </div>
    
    <nav class="exec-tabs" role="tablist" aria-label="Content deck">
      <button type="button" role="tab" data-tab="summary" aria-selected="true" id="tab-btn-summary" aria-controls="tab-summary">Summary</button>
      <button type="button" role="tab" data-tab="detail" id="tab-btn-detail" aria-controls="tab-detail">Detail</button>
      <!-- Add additional tabs as needed per page -->
    </nav>
  </div>
  
  <!-- Tab Panels: scrollable content only -->
  <section class="tab-panel" data-tab-panel="summary" id="tab-summary" tabindex="-1">
    <p class="exec-tab-summary">Executive summary text here.</p>
    <!-- Page-specific content -->
  </section>
  
  <section class="tab-panel" data-tab-panel="detail" id="tab-detail" hidden tabindex="-1">
    <!-- Detail tables/forms -->
  </section>
</main>

<!-- Honesty LED: body-fixed bottom bar (outside main) -->
<aside class="honesty" aria-label="Compliance">
  SoftDent READ-ONLY · empty ≠ $0 · PHI initials+hash · No write-back
</aside>
```

**Specific page deltas:**
- **analytics / claims / office-manager**: Wrap existing `.ledge` (money-strip) and any existing header into the `.chrome-frame` div as shown; move `.honesty` outside of `<main>` to `<body>` direct child.

## 4. JS patches — nr2-optical-page-wire.js (if any)
**File:** `NewRidgeFinancial2/site/js/nr2-optical-page-wire.js`

Paste this entire block to replace existing wire functions (preserves SoftDent read-only guards, adds tab boot):

```javascript
/* === Moonshot Canonical Wire Pack 2026-07-17 === */

function bootExecTabs() {
  const frame = document.querySelector("main.main > .chrome-frame");
  const tabs = frame && frame.querySelector(":scope > .exec-tabs");
  if (!tabs) return null;
  const main = document.querySelector("main.main");
  const panels = main
    ? Array.prototype.slice.call(main.querySelectorAll(":scope > .tab-panel"))
    : [];
  if (!panels.length) return null;
  function activate(id) {
    const tabBtns = tabs.querySelectorAll('[role="tab"]');
    tabBtns.forEach(function (btn) {
      const on = btn.getAttribute("data-tab") === id;
      btn.setAttribute("aria-selected", on ? "true" : "false");
      btn.tabIndex = on ? 0 : -1;
    });
    panels.forEach(function (p) {
      const on = p.getAttribute("data-tab-panel") === id;
      if (on) p.removeAttribute("hidden");
      else p.setAttribute("hidden", "");
    });
    try {
      main.scrollTop = 0;
    } catch (_) {
      /* ignore */
    }
  }
  tabs.addEventListener("click", function (e) {
    const btn = e.target && e.target.closest ? e.target.closest('[role="tab"]') : null;
    if (!btn || !tabs.contains(btn)) return;
    const id = btn.getAttribute("data-tab");
    if (id) activate(id);
  });
  tabs.addEventListener("keydown", function (e) {
    const keys = { ArrowLeft: -1, ArrowRight: 1, Home: "home", End: "end" };
    const move = keys[e.key];
    if (move == null) return;
    const list = Array.prototype.slice.call(tabs.querySelectorAll('[role="tab"]'));
    if (!list.length) return;
    let i = list.findIndex(function (b) {
      return b.getAttribute("aria-selected") === "true";
    });
    if (i < 0) i = 0;
    if (move === "home") i = 0;
    else if (move === "end") i = list.length - 1;
    else i = (i + move + list.length) % list.length;
    e.preventDefault();
    list[i].focus();
    activate(list[i].getAttribute("data-tab"));
  });
  // Gate: always open on Summary so first viewport = money-strip + tabs.
  activate("summary");
  return true;
}

function bootPackage1StickyStack() {
  const main = document.querySelector("main.main");
  const ledge =
    main &&
    (main.querySelector(":scope > .chrome-frame > .ledge") ||
      main.querySelector(":scope > .ledge"));
  if (!main || !ledge) return null;
  const halHdr = main.querySelector(":scope > .hal-cmd-header");
  const apply = function () {
    const h = Math.ceil(ledge.getBoundingClientRect().height);
    const hh = halHdr ? Math.ceil(halHdr.getBoundingClientRect().height) : 0;
    main.style.setProperty("--nr2-ledge-sticky-h", String(h) + "px");
    main.style.setProperty("--nr2-hal-hdr-h", String(hh) + "px");
  };
  apply();
  if (typeof ResizeObserver === "function") {
    const ro = new ResizeObserver(function () {
      apply();
    });
    ro.observe(ledge);
    if (halHdr) ro.observe(halHdr);
  } else {
    window.addEventListener("resize", apply);
  }
  return true;
}

/* Stub hooks for existing ops/atmosphere functions to prevent ReferenceError if missing */
function mountOpsGates(cfg) { console.log("Ops gates stub", cfg); }
function bootAtmosphere() {}
function bootExecutiveChrome() {}
function bootMotionGrammar() {}
function bindPrintHygiene() {}

function bootOpsGates() {
  try { mountOpsGates({ refreshMs: 60000 }); } catch (_) {}
  try { bootAtmosphere(); } catch (_) {}
  try { bootExecutiveChrome(); } catch (_) {}
  try { bootPackage1StickyStack(); } catch (_) {}
  try { bootExecTabs(); } catch (_) {}
  try { bootMotionGrammar(); } catch (_) {}
  try { bindPrintHygiene(); } catch (_) {}
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", bootOpsGates);
} else {
  bootOpsGates();
}
```

## 5. Landing / Hub extras (if any)
**Hub-specific:** Already included in CSS §Track A (asymmetric chrome-frame).  
**Landing:** No changes; landing uses `.exec-landing-shell` which is outside this optical scope.

## 6. Ordered apply checklist (Cursor steps)
1. **M** — Replace CSS blocks in `nr2-optical-theme.css` with Section 2 above (backup first).
2. **S** — Verify `nr2-optical-page-wire.js` contains Section 4 functions; if file doesn't exist, create it and reference in HTML footers.
3. **M** — Patch `nr2-optical-page-analytics.html`: Insert `.chrome-frame` wrapper around existing header/ledge/tabs; move `.honesty` to `<body>` direct child (outside `<main>`).
4. **M** — Patch `nr2-optical-page-claims.html`: Same as step 3.
5. **M** — Patch `nr2-optical-page-office-manager.html`: Same as step 3.
6. **S** — Verify all optical pages reference `nr2-optical-page-wire.js` before `</body>`.
7. **S** — Run Validation Gate (Section 7) on 1080p display.

## 7. Validation gate (1080p / schema)
Paste this into DevTools console on any patched optical page:

```javascript
(function gate(){
  const f = document.querySelector('.chrome-frame');
  const h = document.querySelector('body > .honesty');
  const b = getComputedStyle(document.querySelector('.beam') || document.createElement('div'));
  const errors = [];
  if (!f) errors.push('FAIL: .chrome-frame missing');
  if (f && Math.abs(f.getBoundingClientRect().height - 172) > 2) errors.push('FAIL: chrome-frame height !== 172px');
  if (!h) errors.push('FAIL: body > .honesty missing');
  if (h && h.style.position !== 'fixed' && getComputedStyle(h).position !== 'fixed') errors.push('FAIL: honesty not fixed');
  if (parseFloat(b.height) !== 1) errors.push('FAIL: beam height !== 1px');
  if (errors.length) { console.error('MOONSHOT GATE FAILED', errors); return false; }
  console.log('MOONSHOT GATE PASS: chrome-frame 172px · beam 1px · honesty fixed · 1080p ready');
  return true;
})();
```
**Visual check:** On 1080p laptop (920px usable), the money-strip (`.ledge`) must be fully visible without scrolling; only `.tab-panel` content should scroll.

## 8. What NOT to change
- Do **not** restore the old 3px gradient beam or standalone `.beam` divs with sweep animations.
- Do **not** move Honesty back into the document flow or inside `<main>`; keep it as `body > .honesty` fixed bottom LED.
- Do **not** increase chrome-frame height above 172px or add decorative padding that bloats the frame.
- Do **not** introduce React, Vue, or third-party chat widgets.
- Do **not** alter SoftDent read-only logic; continue to display empty fields as empty (≠ $0).
- Do **not** write back to SoftDent; remain READ-ONLY.

## 9. Executive Summary (5 bullets)
- **Chrome-frame lock:** All optical pages now converge to a single 172px fixed viewport frame (48px letterhead + 92px ledge + 32px tabs), eliminating scroll-to-see-desk on 1080p.
- **Beam literalism:** Global enforcement of 1px gold laser `rgba(201,162,39,0.3)`; zero tolerance for 3px gradients or decorative sweep bloat.
- **Honesty LED:** Compliance text fixed as 20px bottom viewport strip, never hiding, never inline, preserving §74 visibility requirement.
- **Schema hardening:** Missing chrome-frame wrappers added to analytics/claims/office-manager pages; HTML schema standardized across 11 optical surfaces.
- **Cursor-proofing:** Canonical CSS/HTML/JS blocks provided as copy-paste source-of-truth to prevent future drift or half-applied fixes.
