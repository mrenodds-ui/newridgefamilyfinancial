# Moonshot AI — Less Sterile / Highly Polished Look (CONSULT ONLY)

**Date:** 2026-07-16
**Model:** `kimi-k2.5`
**Key:** OPENROUTER_API_KEY
**Script:** `scripts/run_moonshot_less_sterile_polish_consult.py`
**Apply:** Operator must say continue / approve before Cursor applies.

## Operator request (verbatim)

> ask moonshot ai how these pages can look less sterile and more higly polished

---

# Verdict
Apply **Package 1: Instrument Glass & Z-Depth** — replace flat dark panels with layered optical-glass surfaces, subtle volumetric shadows, and atmospheric beam lighting to transform the clinical void into a precision optical instrument without obscuring honesty chrome.

## 0. Operator Intent (verbatim)
ask moonshot ai how these pages can look less sterile and more higly polished

## 1. Why it feels sterile now (specific patterns + REAL files)

**The "Darkroom Void" Problem:**
- **Flat color fields**: `nr2-optical-theme.css` uses `--vacuum: #050607` as solid fill on `html, body` with only a subtle radial gradient (line ~88). Every container sits on the same z-plane creating a 2D CAD drawing feel.
- **Wireframe borders**: `.nr2-ops-gate`, `.metric-face`, and `.phi-card` all use `border: 1px solid #2a3340` (identical stroke weight/color everywhere) creating a technical schematic aesthetic.
- **Zero-radius rigidity**: `--radius-none: 0` applied universally makes the UI feel like laser-cut sheet metal rather than precision optics.
- **Monotonous spacing**: Rigid `--space-1: 6px` to `--space-6: 40px` scale creates mathematical but not optical rhythm. The `money-strip` uses `gap` that feels like a spreadsheet.
- **Typography flattening**: All labels forced into `var(--mono)` with `letter-spacing: 0.06em` and `text-transform: uppercase` creates a "hospital instrument" sterility (visible in `.nr2-ops-gates` and `.face-lbl`).
- **Underutilized beams**: The `.beam` div in `nr2-optical-page-claims.html` (line ~35) is decorative but doesn't cast light or shadow on surrounding surfaces.
- **Floating island layout**: `max-width: 1180px` centered with `margin: auto` in `.shell` disconnects the UI from viewport edges like a specimen on a slide.

**Specific sterile markers in audit:**
- `background: var(--vacuum)` on 12+ container types
- `border-bottom: 1px solid #2a2410` on banners (harsh horizontal rules)
- `.metric-face` containers with identical padding and no elevation differentiation
- No `box-shadow` usage except for error pulses (ops-gates red alert)

## 2. Highly-polished target look (3–5 sensory principles for NR2 optical)

1. **Optical Instrument Materiality**: Glass that refracts, brushed metal that reflects, laser beams that illuminate surfaces they touch — moving from "dark mode IDE" to "Leica rangefinder viewfinder."
2. **Volumetric Depth without Skeuomorphism**: Z-layers achieved through shadow diffusion (soft ambient occlusion under metric faces) rather than bevels or gradients implying 3D buttons.
3. **Chromatic Warmth in Darkness**: Strategic use of `--qb: #ffaa00` (amber) and `--sd: #00d4aa` (cyan) as light sources that cast subtle glow on surrounding dark surfaces, not just as text colors.
4. **Typographic Contrast**: Sharp distinction between "staff" (human-readable) and "laser" (machine data) — evolve from "all caps mono" to "sentence-case sans for staff, tabular mono for data."
5. **Atmospheric Honesty**: The honesty banners become integrated light strips (like status LEDs on high-end audio equipment) rather than appended warning labels.

## 3. Ordered visual polish packages (1..N)

### Package 1: Instrument Glass & Z-Depth (Apply First)
**Why**: Addresses the immediate "flatness" without changing HTML structure. Leverages existing PHI glass patterns but applies them architecturally.

**REAL files**: `nr2-optical-theme.css`, `nr2-optical-page-wire.js`

**Concrete CSS/JS moves**:
- Replace `.metric-face` solid backgrounds with:
  ```css
  background: linear-gradient(180deg, rgba(14,20,28,0.85) 0%, rgba(10,14,20,0.65) 100%);
  backdrop-filter: blur(12px) saturate(120%);
  border: 1px solid rgba(255,255,255,0.08);
  box-shadow: 
    0 1px 2px rgba(0,0,0,0.4),
    0 12px 24px -8px rgba(0,0,0,0.6),
    inset 0 1px 0 rgba(255,255,255,0.05);
  ```
- Add `.atmosphere` class to shell: subtle animated grain texture (SVG noise filter) at 3% opacity on `--vacuum` backgrounds to prevent "digital void" feel.
- Elevate `.banner` to `position: sticky` with `backdrop-filter: blur(8px)` and `border-bottom: 1px solid rgba(0,212,170,0.15)` (SoftDent glow) when live.
- Transform `.beam` from div to pseudo-element with `box-shadow: 0 0 20px 2px var(--sd), 0 0 40px 8px rgba(0,212,170,0.2)` creating actual light cast on adjacent cards.

**Effort**: M (CSS heavy, minimal JS)
**Validation gate**: Empty states remain high-contrast readable; no glass effect reduces text contrast below WCAG 4.5:1.

---

### Package 2: Chromatic Architecture
**Why**: Breaks the monochrome dominance using existing tokens as light sources rather than paint.

**REAL files**: `nr2-optical-theme.css`, all page HTMLs

**Concrete moves**:
- Introduce `--glow-sd: 0 0 20px rgba(0,212,170,0.3)` and apply to active `.metric-face.sd` on hover.
- Change `.banner.live` border to animate subtle green glow pulse (already defined in ops gates but never applied to banner).
- Use `--qb` amber as "warmth injection" in `.kicker` text and hover states (currently muted gray).
- Add CSS custom property `--optical-warmth: 1` (default) to `:root`, create `@media (prefers-color-scheme: dark)` override that slightly shifts vacuum toward `#080a0c` (warmer black).

**Effort**: S
**Validation gate**: PHI initials remain clearly visible against all new glow effects.

---

### Package 3: Typographic Orchestration
**Why**: The "all caps mono" is the biggest sterile signal. Evolve to "Swiss International" precision without losing machine readability.

**REAL files**: `nr2-optical-theme.css`

**Concrete moves**:
- Replace `.type-staff` with `font-weight: 450` (variable font if supported, fallback 400) and `letter-spacing: -0.01em` for headlines only.
- Change `.face-lbl` from `font-family: var(--mono)` to `var(--sans)` with `font-size: 13px`, `text-transform: none`, `letter-spacing: 0.02em`, `color: var(--muted)` — creates human/machine hierarchy.
- Increase `.mode-eyebrow` size to `12px` with `font-weight: 600` and `color: var(--qb)` — establishes page location with warmth.
- Create `.val` (money face) optical sizing: `font-size: clamp(24px, 3vw, 32px)` with `font-feature-settings: "tnum" "ss01"` for refined numerals.

**Effort**: S
**Validation gate**: Money values remain tabular-aligned across all metric faces.

---

### Package 4: Compositional Asymmetry
**Why**: The 220px/1fr grid is rigidly symmetrical. Optical instruments have asymmetric viewfinders.

**REAL files**: `nr2-optical-page-claims.html`, `nr2-optical-page-ar.html`, `nr2-optical-pages-hub.html`

**Concrete moves**:
- On hub page: Change `.shell` to `grid-template-columns: 240px 1.2fr 0.8fr` when viewport >1400px, placing HAL core off-center.
- Full-bleed `.money-strip` on mobile: `margin: 0 -14px`, `padding: 0 14px`, `background: linear-gradient(90deg, transparent, rgba(0,212,170,0.03), transparent)`.
- Introduce `.ledge` class for secondary actions: small raised platform effect under primary metric faces (uses existing `--space-3` but with shadow).

**Effort**: M (requires HTML grid changes)
**Validation gate**: Touch targets remain >=44px; no horizontal scroll on tablet.

---

### Package 5: Motion Grammar Enhancement
**Why**: Existing motion is functional (loading, errors). Add "mechanical precision" motion for polish.

**REAL files**: `nr2-optical-page-wire.js`, `nr2-optical-theme.css`

**Concrete moves**:
- Add `transition: transform 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94), box-shadow 0.3s ease` to `.metric-face`.
- On data refresh: `.metric-face` receives temporary `transform: translateY(-2px)` with increased shadow (physical lift) rather than just opacity pulse.
- Beam animation: CSS `@keyframes beam-sweep` that moves a subtle highlight across the beam element every 8s (ambient life signal).

**Effort**: L (JS coordination with data updates)
**Validation gate**: Respects `prefers-reduced-motion`; no animation on print.

---

### Package 6: Print & PHI Material Honesty
**Why**: The print redaction (P9) can look "patched on." Integrate it as a feature of the optical system.

**REAL files**: `nr2-optical-theme.css` (@media print)

**Concrete moves**:
- Print styles: Instead of removing backgrounds, convert to high-contrast light mode with PHI hash as actual "redacted" black bars (visual honesty).
- Ensure glass effects render as solid whites in print (graceful degradation).

**Effort**: S
**Validation gate**: P9 requirements maintained.

## 4. Recommended FIRST package (apply now)
**Package 1: Instrument Glass & Z-Depth**

Start here because it requires no HTML structural changes (reduces regression risk), immediately addresses the "sterile void" complaint, and actually enhances honesty by making the UI feel like a physical instrument with transparent, inspectable surfaces (glass metaphor aligns with PHI transparency). The backdrop-filter approach is already prototyped in `.phi-card` but needs to be elevated to the architectural level.

**Immediate first three commits**:
1. **Glass metric faces**: Apply backdrop-filter and layered shadows to `.metric-face` in theme CSS.
2. **Atmospheric beam lighting**: Enhance `.beam` with glow effects that cast on adjacent surfaces.
3. **Grain texture**: Add SVG noise overlay to `--vacuum` backgrounds to kill the "digital flatness."

## 5. What NOT to change (honesty / PHI / ops gates)
- **Empty ≠ $0 representation**: Keep the em-dash (—) or "NO SIGNAL" treatments high-contrast; do not dim or "beautify" missing data into subtle gray.
- **Ops gate visibility**: Red/yellow/green status must remain high-saturation and prominent; do not "tuck" them into glass layers where they become decorative.
- **PHI initials+hash**: The `.phi-initials` masking must remain sharp and machine-readable; do not blur or glass-morph the actual text.
- **Banner honesty text**: The "empty ≠ $0 · no SoftDent write-back" strings must remain fully opaque and readable; can change font treatment but not contrast.
- **Force Close red alert**: When `.tone-red` pulses, it must remain jarring and visible; polish should not domesticate emergency signals.
- **SoftDent/QB/HAL color tokens**: Do not shift hues; only evolve how they emit light (glow vs flat fill).

## 6. Anti-patterns (sterile traps + AI-slop traps)
- **The Purple Gradient Trap**: Do not introduce blue-purple gradients "for depth" — this is generic AI-assistant visual language.
- **Cream + Terracotta**: Avoid warm beige backgrounds or rust-colored accents to "add warmth" — cliché financial wellness aesthetic, breaks the optical instrument metaphor.
- **Broadsheet Hairlines**: Avoid 0.5px lines and extreme serif fonts (Tiempos, etc.) for "editorial polish" — inappropriate for medical billing precision.
- **Soft UI / Neumorphism**: Do not use inset shadows and rounded blobs to make "friendly" buttons — sterile becomes infantilizing.
- **Glassmorphism Overload**: Do not apply blur to text containers — only to structural surfaces. Text must remain on solid or near-solid backgrounds.
- **Rounded Everything**: Avoid border-radius >4px on data containers; keeps the "machine" feel honest.
- **Drop Shadow Spam**: Avoid large diffuse shadows on every element; use only directional ambient occlusion (shadows implying light source from top-left beam).

## 7. Acceptance criteria for "no longer sterile"
- [ ] A user can describe the interface as feeling like "high-end optical equipment" rather than "a database admin panel."
- [ ] The metric faces cast subtle shadows on the background (evidence of Z-depth).
- [ ] The beam element visibly illuminates adjacent card edges with its respective color (SD green or QB amber).
- [ ] Typography has clear "human/staff" vs "machine/data" hierarchy without relying solely on ALL CAPS.
- [ ] The empty state (—) feels like "intentional signal absence" rather than "missing design asset."
- [ ] On tablet, the glass surfaces show subtle parallax/lift on scroll (if implemented in P5).
- [ ] Honesty banners remain the highest contrast element on the page (safety over beauty).

## 8. Executive Summary (5 bullets)
- **Diagnosis**: The pages feel sterile due to flat dark voids, uniform wireframe borders, and all-caps mono typography creating a "hospital instrument" rather than "precision optical bench" aesthetic.
- **Solution**: Apply **Instrument Glass & Z-Depth** (Package 1) to transform flat panels into layered glass surfaces with volumetric shadows and atmospheric lighting.
- **Key Move**: Replace solid `#050607` backgrounds with subtle grain texture and `backdrop-filter` blur on metric faces, while enhancing the `.beam` element to cast actual colored light.
- **Constraint Respect**: All changes use existing HAL/SD/QB color tokens, maintain high-contrast for empty states, and do not obscure PHI hashes or ops gate alerts.
- **Outcome**: NR2 Optical evolves from clinical dark mode to a cohesive "lens and light" instrument interface that feels expensive, precise, and honest.

## 9. Approval Checklist
- [ ] Operator confirms "glass" metaphor aligns with PHI transparency values.
- [ ] Design team verifies no purple gradients or cream serifs introduced.
- [ ] Dev team confirms `backdrop-filter` performance acceptable on target tablets (P5 touch targets).
- [ ] Compliance confirms empty ≠ $0 indicators remain WCAG AAA contrast.
- [ ] QA confirms print styles (P9) degrade gracefully from glass effects.
- [ ] Accessibility confirms reduced-motion preference disables beam animations.
