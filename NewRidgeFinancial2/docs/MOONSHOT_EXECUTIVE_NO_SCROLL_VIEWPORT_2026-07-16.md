# Moonshot AI — Executive No-Scroll Viewport (CONSULT ONLY)

**Date:** 2026-07-16
**Model:** `kimi-k2.5`
**Key:** OPENROUTER_API_KEY
**Script:** `scripts/run_moonshot_executive_no_scroll_viewport_consult.py`
**Apply:** Operator must say continue / approve before Cursor applies.

## Operator request (verbatim)

> ask moonshot ai that the pages are too big and i have to scroll, i want a highly polished executive look even if the schema has to change. have him look at other financial pages and report

---

# Verdict
Apply **Package 1: Chrome Collapse Protocol** immediately—compress the eyebrow/h1/kicker/beam/honesty stack into a single 48‑px executive header bar, convert Honesty to a bottom‑edge status LED, and sticky‑lock the money‑strip so the first viewport shows the full executive desk on 1080 p without React or file renames.

## 0. Operator Intent (verbatim)
ask moonshot ai that the pages are too big and i have to scroll, i want a highly polished executive look even if the schema has to change. have him look at other financial pages and report

## 1. Why pages force scroll (stack diagnosis)
The optical pages suffer from **vertical chrome inflation**: every page renders a full “letterhead” stack in the document flow before any data appears.

**Measured stack (≈ 220‑260 px before ledge):**
1. **Banner** (≈ 28 px) – top compliance strip  
2. **Mode eyebrow** (≈ 18 px) – tiny muted label  
3. **H1 type‑staff** (≈ 42 px) – large page title  
4. **Kicker** (≈ 20 px) – descriptive sentence  
5. **Beam** (≈ 24 px) – decorative gradient rule  
6. **Honesty** (≈ 34 px) – compliance paragraph  
7. **Ledge / money‑strip** (≈ 90‑120 px) – the actual executive currency faces  

Because `.main { overflow-y: auto }` wraps **all** of the above, the browser treats the chrome as scrollable content. On a 1080 p laptop (≈ 920 px usable after OS chrome), the money‑strip starts at ~260 px and often pushes the first data row below the fold, forcing the CFO to scroll to see the “desk.”

## 2. Cross‑page comparison (optical vs other financial pages in audit)
| Surface | Chrome density | Fold behavior | Executive feel |
|---------|----------------|---------------|----------------|
| **Optical suite** (analytics, AR, claims, HAL, etc.) | High (score 6‑7). Stacked typographic headers + decorative beam + compliance block. | **Forced scroll** to reach money‑strip on 1080 p. | “Document” feel; reads like a scrollable report rather than a dense Bloomberg‑style terminal. |
| **Beam‑touch mockup** (landing) | Medium (score 4). Uses `.exec‑landing‑shell` with `flex: 1 1 auto` and `overflow: hidden`. | Landing fits viewport; bench is self‑contained. | Closer to the desired “optical bench” density, but not applied to interior pages. |
| **index.html** | Minimal (score 1). Bare redirect. | Instant. | Not applicable. |

**Benchmark:** Professional financial terminals (Refinitiv, Bloomberg, SAP Fiori “Overview” pages) use **≤ 80 px of locked chrome** and **sticky KPI strips**; everything else scrolls inside a contained pane. NR2 optical pages currently use ~3× that vertical budget.

## 3. Page‑by‑page scroll risk (table: page | score 1–5 | above‑fold waste | REAL files)

| Page | Risk (1‑5) | Above‑fold waste | REAL files |
|------|------------|------------------|------------|
| nr2‑optical‑page‑analytics.html | **5** | eyebrow + h1 + kicker + beam + honesty + ledge padding | `nr2-optical-page-analytics.html` |
| nr2‑optical‑page‑ar.html | **5** | Same stack | `nr2-optical-page-ar.html` |
| nr2‑optical‑page‑claims.html | **5** | Same + filter bar (adds 30 px) | `nr2-optical-page-claims.html` |
| nr2‑optical‑page‑content.html | **5** | Same stack | `nr2-optical-page-content.html` |
| nr2‑optical‑page‑hal.html | **5** | Same + `.hal‑cmd‑header` (extra 40 px) | `nr2-optical-page-hal.html`, `nr2-optical-hal-command.css` |
| nr2‑optical‑page‑narratives.html | **5** | Same stack | `nr2-optical-page-narratives.html` |
| nr2‑optical‑page‑office‑manager.html | **5** | Same stack | `nr2-optical-page-office-manager.html` |
| nr2‑optical‑page‑quickbooks.html | **5** | Same stack | `nr2-optical-page-quickbooks.html` |
| nr2‑optical‑page‑softdent.html | **5** | Same stack | `nr2-optical-page-softdent.html` |
| nr2‑optical‑page‑taxes.html | **5** | Same stack | `nr2-optical-page-taxes.html` |
| nr2‑optical‑pages‑hub.html | **4** | h1 + kicker + beam + honesty (no eyebrow, slightly tighter) | `nr2-optical-pages-hub.html` |
| nr2‑optical‑beam‑touch‑mockup.html | **3** | Uses `.exec‑landing‑ledge` + flex layout; scroll is optional | `nr2-optical-beam-touch-mockup.html` |

## 4. Ordered packages (1..N) for high‑executive first‑viewport fit

### Package 1: Chrome Collapse Protocol (RECOMMENDED FIRST)
**Why:** Delivers the “ Bloomberg terminal” density immediately by collapsing six separate blocks into one compact header line and locking the money‑strip. Keeps all compliance (Honesty becomes a 20 px bottom LED).  
**REAL files:** `nr2-optical-theme.css`, all `nr2-optical-page-*.html`  
**Concrete moves:**
- **Schema change:** Reorder `<main>` so `.ledge` (money‑strip) is **first child**; move `.honesty` to the end of `<body>` (fixed bottom bar).
- **CSS collapse:**  
  - `.mode‑eyebrow`, `.type‑staff`, `.kicker` → `display: inline; font-size: 12px; line-height: 1; margin: 0;` inside a new `.exec‑compact‑header` flex row.  
  - `.beam` → `height: 1px; background: rgba(201,162,39,0.3); margin: 4px 0;` (laser line, not a gradient block).  
  - `.honesty` → `position: fixed; bottom: 0; left: 220px; right: 0; height: 20px; font-size: 10px; padding: 2px 8px; background: rgba(8,10,12,0.95); border-top: 1px solid rgba(201,162,39,0.25); z-index: 200;` (status LED).  
  - `.ledge` → `position: sticky; top: 0; z-index: 50; background: var(--vacuum);`  
  - `.main` → `padding-top: 0; overflow-y: auto; height: calc(100dvh - 36px - 20px);` (subtract banner + honesty footer).  
**Effort:** M (2‑3 hrs)  
**Validation gate:** Open any optical page on 1080 p; money‑strip must be visible without scroll; scrolling only affects content below the strip.

### Package 2: Executive Letterhead Unification
**Why:** Replace the disjointed banner + eyebrow + h1 with the existing (unused) `.exec‑letterhead` grid defined in the theme, gaining a single 40 px bar that contains mode, title, and status.  
**REAL files:** `nr2-optical-theme.css`, all `nr2-optical-page-*.html`  
**Concrete moves:**
- Wrap banner content + eyebrow + h1 into `.exec‑letterhead` (3‑column grid: title / meta / status).  
- Delete `.mode‑eyebrow`, `.type‑staff`, `.kicker` from flow; map their text into the letterhead cells.  
- Move `.beam` to `border‑bottom` of the letterhead (1 px gold fade).  
**Effort:** M (3‑4 hrs)  
**Validation gate:** Pixel‑measure letterhead ≤ 48 px; no text wraps on 1280 px width.

### Package 3: Viewport‑Locked Chrome (Fixed Pane)
**Why:** Guarantees first‑viewport fit by treating the header as a fixed frame, independent of content scrolling.  
**REAL files:** `nr2-optical-theme.css`  
**Concrete moves:**
- Add `.chrome‑frame { position: fixed; top: 36px; left: 220px; right: 0; height: 140px; z-index: 100; background: var(--vacuum); }`  
- Move eyebrow, h1, kicker, beam, honesty, ledge inside `.chrome‑frame`.  
- `.main` → `margin-top: 140px; height: calc(100dvh - 36px - 140px); overflow-y: auto;`  
**Effort:** S (1‑2 hrs)  
**Validation gate:** Scroll wheel only moves the white area below the money‑strip; header stays visually locked.

### Package 4: Tabbed Content Deck (Density Layer)
**Why:** For pages with heavy content (claims table, HAL tools), keep the money‑strip permanently visible while the rest of the body lives inside tab panels that don’t impact initial viewport height.  
**REAL files:** `nr2-optical-page-claims.html`, `nr2-optical-page-hal.html`, etc.  
**Concrete moves:**
- Insert `.exec‑tabs` bar immediately after `.ledge`.  
- Wrap page‑specific sections (tables, tool rows) in `.tab‑panel` with `display: none / block` toggled by vanilla JS.  
- Default to “Summary” tab (empty or single metric row) so first viewport never exceeds money‑strip + tabs.  
**Effort:** L (6‑8 hrs across all pages)  
**Validation gate:** 1080 p viewport shows money‑strip + tab bar; no scroll until user selects a tab containing a long list.

## 5. Recommended FIRST package (apply now)
**Package 1: Chrome Collapse Protocol**  
It satisfies the operator’s “schema may change” permission without a React rewrite, hits the 1080 p first‑viewport target immediately, and preserves all hard constraints (Honesty remains visible as a bottom LED, SD/QB/HAL tokens stay on the faces).

## 6. What NOT to change
- **SoftDent logic:** Remain READ‑ONLY; never display `$0` for empty fields; keep PHI as initials+hash.  
- **Token classes:** Keep `.sd`, `.qb`, `.hal`, `.exec‑currency` on metric faces (required for wiring).  
- **Color palette:** No purple gradients, no cream/terracotta, no broadsheet newspaper aesthetic.  
- **Honesty visibility:** Do not hide the compliance block; compress it to a status LED or bottom bar.  
- **File paths:** Do not rename `nr2-optical-theme.css` or the page files; edits must be in‑place.  
- **No external chat embeds:** HAL remains local/command‑style only.

## 7. Anti‑patterns (executive traps + AI‑slop + fake density)
- **Glassmorphism padding:** Adding `backdrop‑filter` blur that increases margins to “look premium”—wastes pixels.  
- **Microscopic fonts:** Shrinking text below 11 px to force fit; executive desks need legible 12‑13 px currency values.  
- **Fake density:** Replacing the honesty block with a hidden tooltip—violates the “executive‑visible status LED” constraint.  
- **Decorative beam bloat:** Keeping the 24 px gradient beam as a “brand element” instead of collapsing it to a 1 px laser line.  
- **Sidebar expansion:** Adding breadcrumbs or extra nav items to “solve” wayfinding—adds more chrome, exacerbating scroll.  
- **React rewrite:** Suggesting Next.js/Vite “for better layout”—explicitly forbidden by static‑HTML constraint.

## 8. Acceptance criteria (first viewport / scroll budget)
- **1080 p (1920×1080, 100 % zoom):**  
  - Money‑strip (`.ledge`) fully visible within first viewport.  
  - No scroll required to view first row of data or primary action buttons.  
  - Honesty statement visible as a bottom‑edge LED or within the 48 px header; never hidden behind scroll.  
- **1440 p (2560×1440):**  
  - Full “executive desk” (header + money‑strip + first content section) visible without scroll.  
- **Scroll budget:**  
  - Only content **below** the money‑strip may scroll.  
  - Header + money‑strip must remain visually stable (sticky or fixed) during scroll operations.  
- **Performance:**  
  - No layout shift (CLS ≈ 0) when compliance text updates in the Honesty bar.

## 9. Executive Summary (5 bullets)
- **Root cause:** Six separate typographic blocks (eyebrow, h1, kicker, beam, honesty, ledge) stack vertically before data, consuming 260 px of precious 1080 p real estate.  
- **Immediate fix:** Collapse the six blocks into one 48‑px compact header and sticky‑lock the money‑strip (Package 1).  
- **Compliance preserved:** Honesty moves to a 20‑px bottom LED rather than a paragraph, satisfying “executive‑visible” without stealing viewport.  
- **No rebuild required:** Pure CSS + HTML reordering inside existing static files; React/Vite stay banned.  
- **Result:** Optical pages achieve Bloomberg‑terminal density—CFO sees full desk on first paint, scrolls only for detail lists.

## 10. Approval Checklist
- [ ] Operator confirms 1080 p laptop is primary target (CFO desk).  
- [ ] Backup `nr2-optical-theme.css` and one page (e.g., `nr2-optical-page-ar.html`) before editing.  
- [ ] Package 1 CSS changes applied to theme file.  
- [ ] HTML schema reordered on pilot page (move `.ledge` first, `.honesty` to bottom).  
- [ ] Visual regression check: money‑strip visible without scroll; no purple/cream colors introduced.  
- [ ] SoftDent tokens (`.sd`) still render on faces; empty values show `∅` not `$0`.  
- [ ] Honesty text legible (≥ 10 px) and visible in first viewport (bottom LED or header).  
- [ ] Operator sign‑off on “laser line” beam (1 px) vs. original gradient beam.  
- [ ] Merge to trunk only after pilot page passes acceptance criteria in Section 8.
