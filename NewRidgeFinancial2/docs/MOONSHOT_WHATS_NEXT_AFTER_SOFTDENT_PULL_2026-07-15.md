# Moonshot AI — What's Next After SoftDent Morning Auto-Pull (CONSULT ONLY)

**Date:** 2026-07-15
**Model:** `kimi-k2.5`
**Key:** OPENROUTER_API_KEY
**Status:** ok
**Repo root:** `C:\Users\mreno\newridgefamilyfinancial`
**Prior:** `cde7ef0` SoftDent morning auto-pull · `nr2-12030`
**Script:** `scripts/run_moonshot_whats_next_after_softdent_pull_consult.py`
**Apply:** DO NOT APPLY until operator approves.

## Operator request (verbatim)

> next

---

# Verdict
Harden the SoftDent GUI Excel export paths for aging/register/collections to prevent morning auto-pull stalls and secure the daily rhythm.

## 0. Operator Intent (verbatim)
next

## 1. Recommended NEXT (name, why now, effort, REAL files/ops, validation gate)
**Package:** SoftDent GUI Export Ops Hardening (Aging/Register/Collections Save Reliability)

**Why now:** The morning auto-pull (`nr2-12030-period-close-softdent-pull`) just shipped and depends entirely on unattended SoftDent Excel exports. LIVE AUDIT shows today's pull succeeded (`softdentTotal: $7,714`, `guiRunning: true`), but GUI automation fragility (dialog timing, save-path resolution, "Save As" confirmation handling) remains a single-point-of-failure. Without hardening, a transient Windows dialog focus issue or path resolution lag will break the 08:30 daily rhythm. OPS/reliability takes precedence over UX features until the automated path is bulletproof.

**Effort:** Medium (4–6 hours) — robust wait loops, Save As dialog handle validation, temp file cleanup, retry with exponential backoff, circuit breaker.

**REAL files/ops:**
- `C:\Users\mreno\newridgefamilyfinancial\NewRidgeFinancial2\softdent_gui_driver.py` (or equivalent export orchestrator) — hardened dialog automation, explicit Save As path injection, explicit "Save" button trigger verification
- `C:\Users\mreno\newridgefamilyfinancial\NewRidgeFinancial2\daily_closeout.py` — pre-flight GUI readiness probe (process up, window responsive), post-export file existence/size validation
- `C:\Users\mreno\newridgefamilyfinancial\app_data\nr2\softdent\staging\` — ensure writable, clean temp files pre-export to avoid "file in use" conflicts
- `C:\Users\mreno\newridgefamilyfinancial\NewRidgeFinancial2\nr2_scheduler.py` — circuit breaker: abort `pull_softdent` after 3 retries, log `guiExport: false`, continue with attest-only to avoid infinite stall
- Windows Event Log (application) — monitor for "Save As" dialog timeouts or accessibility API failures

**Validation gate:**
- 3 consecutive mornings of unattended auto-pull with zero manual intervention.
- JSONL log shows `exportSuccess: true`, `fileSizeBytes > 0`, and `savePath` inside SoftDent's native folder (never `SoftDentReportExports`) for all three reports (aging, register, collections).
- Simulated failure test: kill SoftDent process mid-export → scheduler catches exception, logs `guiExport: false`, completes attest-only close with `emptyNotZero: true`, and does not invent $0.

## 2. Why this beats the other candidates now
- **Force Close optical control (Opt 2)** is UX polish for rare manual overrides; it doesn't prevent the daily auto-pull from failing.
- **BlueNote alert on stall (Opt 3)** detects failure but doesn't prevent it; hardening is preventive medicine.
- **Formal beamHash desk proof (Opt 4)** is audit hygiene, but the hash is meaningless if the export fails to generate data in the first place.
- **Quiet fallback (Opt 6)** is a safety net we will implement *inside* this package as a circuit breaker, but the primary goal is to harden the success path, not optimize the failure path.
- **Main interferometer beam-touch (Opt 5)** is already covered by the shipped optical beam bind (`2d195e5`).

## 3. Runner-ups (2–3)
1. **HAL Force Close optical control** (OM / Pages Hub — laser-gated, JSONL attest) — valuable for human-in-the-loop edge cases after daily rhythm is hardened.
2. **Formal beamHash desk proof** (HAL chat + optical AR/QB cite identical hash on live 8765) — critical for audit trust once data flow is mechanically reliable.
3. **Quiet SoftDent auto-pull fallback** (attest-only mode when GUI unreachable) — will be partially delivered as the circuit breaker inside the recommended package; full quiet-mode polish can follow if needed.

## 4. What NOT to redo
- SoftDent morning auto-pull orchestration (scheduler tick logic)
- Period-close attest logic (beamHash generation, JSONL structure)
- Money-beam optical bind (headline provenance on subpages)
- Consent-free SoftDent export HAL teaching
- `SoftDentReportExports` path hygiene (Select File Name routing)
- Money honesty rules (`emptyNotZero`, never invent $0)
- BlueNote chrome filter logic
- Laser `softGap` unification

## 5. Acceptance criteria
- [ ] Aging, Register, and Collections exports complete via GUI automation without human dialog interaction on 3 consecutive mornings.
- [ ] Export files land in SoftDent's native working folder (path hygiene preserved; never `SoftDentReportExports`) with deterministic naming pattern.
- [ ] Retry logic (3 attempts, 30s/60s/120s backoff) handles transient "Save As" dialog delays without operator click.
- [ ] Scheduler logs distinguish `exportStatus: success`, `exportStatus: retrying`, and `exportStatus: failed_gui_unreachable`.
- [ ] If GUI is unreachable or export fails after retries, scheduler falls back to attest-only with `guiExport: false` and preserves `emptyNotZero` (no $0 invention).
- [ ] No regression: existing manual export via HAL Pages still functions with consent-free path.

## 6. Executive Summary (5 bullets)
- Morning auto-pull is live but exposed to GUI fragility (dialog focus, path resolution, save confirmation timing).
- Hardening the Excel export path ensures the 08:30 scheduler tick survives real-world Windows desktop variance and SoftDent UI state changes.
- Target hardening: aging, register, and collections reports save reliably to SoftDent's folder with retry logic and file validation.
- Includes circuit breaker to prevent infinite stall on GUI crash, falling back to attest-only with clear logging.
- Defers Force Close UX and beamHash desk proof until the daily money-read rhythm is mechanically bulletproof.

## 7. Approval Checklist
- [ ] Operator confirms GUI export fragility is higher operational risk than missing Force Close control.
- [ ] SoftDent desktop environment specs provided (screen resolution, scaling, SoftDent version, Windows build) for dialog automation tuning.
- [ ] Fallback plan acknowledged: if hardening fails in shadow testing, revert to manual pull with BlueNote alert until next sprint.
- [ ] JSONL log review process defined for monitoring export reliability (`exportSuccess` rate, `fileSizeBytes` histogram).
- [ ] Circuit breaker threshold agreed (3 retries, 5-minute max wait before fallback).
