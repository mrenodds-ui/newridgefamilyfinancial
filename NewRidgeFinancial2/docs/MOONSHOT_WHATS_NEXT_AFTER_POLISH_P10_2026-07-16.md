# Moonshot AI — What's Next After Polish P10 + Executive E1–E4 (CONSULT ONLY)

**Date:** 2026-07-16
**Model:** `kimi-k2.5`
**Key:** OPENROUTER_API_KEY
**Script:** `scripts/run_moonshot_whats_next_after_polish_p10_consult.py`
**Apply:** Operator must say continue / approve before Cursor applies.

## Operator request (verbatim)

> next

---

# Verdict
Fix the dead data layer: **Ops—attended morning_bundle / SoftDent Excel enablement** is RED (connection refused); all product lanes are blocked until the beam bus feeds again.

## 0. Operator Intent (verbatim)
next

## 1. Recommended NEXT
**Name:** Ops Package—Morning Bundle Resuscitation & SoftDent Excel Enablement  
**Why now:** Live audit shows 100% backend refusal (WinError 10061) on `morningBundle`, `moneyBeams`, `trellisAm`, `claimsOutstanding`, and `arAging`. The UI polish (P1–P10/V1–V6/E1–E4) is complete but the system is “glass”—beautiful surface with no data underneath. Without `morning_bundle` returning 200, Trellis AM proofs, Claims aging buckets, and HAL desk smoke cannot hydrate. This is the critical-path blocker.  
**Effort:** M–L (Medium to Large). Likely service startup/port alignment, but may require TLS/certificate or firewall triage if the refusal is external.  
**Real files:**  
- Frontend consumer: `nr2-optical-page-office-manager.js` (44,171 bytes)  
- SoftDent bridge: `nr2-optical-page-softdent.js` (8,466 bytes)  
- Beam bus transport: `nr2-optical-nav.js` (10,978 bytes) and `nr2-optical-page-wire.js` (60,658 bytes)  
**Validation gate:**  
1. `morningBundle` endpoint returns HTTP 200 with valid JSON payload (no URLError).  
2. SoftDent “Export to Excel” triggers browser download/print-preview (never File dialog, never direct printer) using existing `nr2-print-redacted` hygiene.  
3. `forceCloseAvailable` remains `false` (no pilot attestation yet).  
4. Board PHI displays initials+hash only; empty fields render as empty (not $0).

## 2. Ordered backlog AFTER #1
1. **Trellis withBenefits AM proof** – Once `morningBundle` feeds, validate that Trellis nightly scrape and AM eligibility proof render correctly; monitor for hash mismatch.  
2. **Claims workflow: age buckets + payer backfill** – Enable Claims page (`nr2-optical-page-claims.js`, 63,653 bytes) to consume live `claimsOutstanding` and `arAging` streams; implement paid-suppress honesty filters.  
3. **Pilot / shadow clock / force-close attestation path** – Procedural package: define cutover checklist that eventually flips `forceCloseAvailable` true (only after #1 and #2 are green in production).  
4. **HAL desk smoke / this-patient lane** – Final product polish: contextual HAL queries against live SoftDent read-only cache (safe because data layer is now stable).

## 3. Why this beats the other candidates now
- **Trellis/Claims/HAL (candidates 2, 3, 4):** All require the `morningBundle` pipe to be open. Attempting them now results in empty-state logic that cannot be validated.  
- **Pilot/shadow clock (candidate 5):** Is procedural; you cannot attest to pilot readiness while all data endpoints refuse connections.  
- **New polish layer (candidate 6):** Explicitly excluded by operator (“UI polish roadmaps are exhausted”). No concrete UX gap exists—the gap is functional (dead wire).  
- **Something else:** No other path unblocks the entire product surface; this is the root-cause fix.

## 4. What NOT to redo
- Do not revisit P1–P10 functional polish (ops gates, PHI glass, breadcrumbs, loading, tablet, motion, focus/a11y, soft-fail, print redaction, sessionStorage beam bus).  
- Do not revisit V1–V6 instrument glass or E1–E4 high-executive letterhead/currency emboss/desk surface.  
- Do not add new CSS themes or re-skin SoftDent; keep existing `nr2-optical-theme.css` (56,448 bytes) usage.

## 5. Acceptance criteria
- [ ] `morningBundle`, `moneyBeams`, `trellisAm`, `claimsOutstanding`, `arAging` endpoints respond 200 OK with valid JSON (no WinError 10061).  
- [ ] SoftDent page exports via Excel or Print Preview only; “File” and “Printer” commands are intercepted/disabled per existing `bindPrintHygiene`.  
- [ ] PHI in SoftDent board view shows initials + hash; null balances render as empty strings, never `$0`.  
- [ ] `forceCloseAvailable` flag remains `false` in config; no pilot attestation code is merged.  
- [ ] No new dependencies or React rewrites introduced; remains vanilla JS/CSS.

## 6. Executive Summary (5 bullets)
- **All backends are dark:** Every critical endpoint (`morningBundle`, `moneyBeams`, etc.) is refusing connections (WinError 10061).  
- **UI is complete but inert:** P1–P10, V1–V6, E1–E4 shipped; the system looks production-ready but has no data pulse.  
- **Morning bundle is the heart:** It feeds the beam bus; without it, HAL, Trellis, and Claims are starved.  
- **SoftDent Excel is trapped:** The export path cannot be validated while the connection is dead; fixing ops unblocks the read-only Excel/Print Preview workflow.  
- **Risk of skipping:** Any product work done now would be “theater”—polishing logic against mock data that cannot be trusted for pilot attestation.

## 7. Approval Checklist
- [ ] Confirm `morningBundle` service port/process is defined (expected localhost or internal IP).  
- [ ] Verify SoftDent integration remains read-only (no write-back API calls).  
- [ ] Confirm `forceCloseAvailable` toggle is protected behind pilot attestation gate (do not flip early).  
- [ ] Ensure no file paths are invented during implementation (use existing `nr2-optical-*.js/css` inventory only).  
- [ ] Validate that Excel export uses browser-native download or print preview (never `File` dialog or `Select File Name` directory prompts).
