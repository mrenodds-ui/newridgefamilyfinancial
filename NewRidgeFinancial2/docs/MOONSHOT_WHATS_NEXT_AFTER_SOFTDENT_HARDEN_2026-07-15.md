# Moonshot AI — What's Next After SoftDent Export Hardening (CONSULT ONLY)

**Date:** 2026-07-15
**Model:** `kimi-k2.5`
**Key:** OPENROUTER_API_KEY
**Status:** ok
**Repo root:** `C:\Users\mreno\newridgefamilyfinancial`
**Prior:** `1e13fd0` SoftDent export harden · `45ea727` landing beams
**Script:** `scripts/run_moonshot_whats_next_after_softdent_harden_consult.py`
**Apply:** DO NOT APPLY until operator approves.

## Operator request (verbatim)

> next

---

# Verdict
**HAL Force Close optical control (OM / Pages Hub — laser-gated, JSONL attest)** — the missing safety valve now that shadow mode began today and `forceCloseExists: false` leaves the desk without override if auto-close stalls on red lasers or scheduler hangs.

## 0. Operator Intent (verbatim)
next

## 1. Recommended NEXT (name, why now, effort, REAL files/ops, validation gate)
**Package:** HAL Force Close Optical Control (Laser-Gated Manual Period-Close)

**Why now:** LIVE AUDIT shows `forceCloseExists: false` while `pilot.phase: "shadow"` began today (`shadowStartedAt: "2026-07-15T21:10:23+00:00"`). SoftDent export hardening (`nr2-12033`) prevents GUI stalls from blocking the close, but it does not handle red alignment lasers or scheduler deadlocks. Without Force Close, a red laser tomorrow morning blocks the desk until engineering intervenes. Shadow mode requires an OM-controlled escape hatch.

**Effort:** Medium (5–7 hours) — optical page scaffold, gateway endpoint, laser-gated UI state machine, JSONL attest append-only log, role enforcement.

**REAL files/ops:**
- `C:\Users\mreno\newridgefamilyfinancial\site\nr2-optical-page-force-close.html` — OM UI; button active only when `laserClear: false` OR `periodCloseStatus.status: "stalled"`; displays `lastBeamHash` for desk verification
- `C:\Users\mreno\newridgefamilyfinancial\NewRidgeFinancial2\nr2_hal_gateway.py` — `POST /api/period-close/force` handler; requires `role: office_manager`; validates `laserOverride` boolean; delegates to `daily_closeout.force_close_with_attest(laser_override=True/False)`
- `C:\Users\mreno\newridgefamilyfinancial\NewRidgeFinancial2\daily_closeout.py` — `force_close_with_attest()`; beams money fresh, writes `force_close_log.jsonl` row with `beamHash`, `actor`, `laserOverride`, `shadowMode: true`, `systemOfRecord: false`
- `C:\Users\mreno\newridgefamilyfinancial\app_data\nr2\ops\force_close_log.jsonl` — immutable attest ledger (separate from daily close log to distinguish manual vs auto)
- `C:\Users\mreno\newridgefamilyfinancial\site\nr2-optical-page-office-manager.html` — surface Force Close status widget (amber when available, green when used, red when lasers block even manual)
- Windows Task Scheduler (inspection only): verify `nr2_scheduler.py` morning tick does not collide with Force Close CLI (mutex via lockfile)

**Validation gate:**
- **Laser-block test:** Temporarily mark QB AP dataset stale >24h to trigger red laser; OM opens Pages Hub Force Close page, sees active override button, clicks, receives fresh beamHash `abc123…`, log row appears in `force_close_log.jsonl` with `laserOverride: true`, `systemOfRecord: false`.
- **Stall-recovery test:** Kill SoftDent process during morning tick; scheduler marks close `stalled`; OM uses Force Close UI to complete attest-only close; no duplicate JSONL rows in `daily_close_log.jsonl` (Force Close writes to separate attest log).

## 2. Why this beats the other candidates now
| Candidate | Why Force Close wins |
|-----------|---------------------|
| **Formal beamHash desk proof** | Audit consistency is important, but Force Close is operational survival. Beam proof is a “verify” feature; Force Close is an “unblock” feature. Shadow mode without unblock is unacceptable risk. |
| **BlueNote alert on attest_only** | Alerting is reactive noise. Force Close is proactive control. The desk needs to *act*, not just *know*, when close stalls. |
| **Expand SoftDent pull to register+collections** | Premature scope expansion before the current aging-only path proves stable through a weekend. Force Close hardens the existing surface area first. |
| **QB sync consent UX** | QB datasets are optional/stale per LIVE AUDIT (`quickbooks.ap`, `quickbooks.payroll`). Period-close is required daily; QB consent is not blocking ops. |
| **Desk smoke script** | Smoke tests are diagnostics; Force Close is the fix for the failure mode it would detect. Build the fix, then automate the check. |

## 3. Runner-ups (2–3)
1. **Formal beamHash desk proof across HAL chat + optical pages** — After Force Close ships, add a “Verify Beam” button on optical pages that echoes the HAL chat hash and proves both views share the same import digest (prevents “two versions of the truth” in shadow mode).
2. **BlueNote alert when period-close uses attest_only / laser-blocks / stalls** — Wire BlueNote to tail `daily_close_log.jsonl` and `force_close_log.jsonl`; announce when fallback modes trigger so staff know money beams are running on cached/stale data.
3. **Expand morning SoftDent pull to aging+register+collections** — Once Force Close proves the safety net works, broaden the auto-pull scope to include register and collections reports (same Excel export hardening pattern, new report IDs).

## 4. What NOT to redo
- SoftDent GUI export retries + min-bytes validation (`1e13fd0` — just shipped)
- Period-close attest-only fallback on GUI failure (`db112a5` — just shipped)
- Morning SoftDent aging auto-pull (`cde7ef0` — just shipped)
- Money-beams on main landing + LIVE demotion (`45ea727` — just shipped)
- Period-close status surface on Hub (`23f68df` — just shipped)
- Optical SoftDent/QB beam bind (prior today)
- Consent-free SoftDent export (prior today)
- Path hygiene (`C:\Users\mreno\newridgefamilyfinancial` enforcement)
- Money honesty (`empty ≠ $0` doctrine)
- BlueNote-only announce filtering

## 5. Acceptance criteria
- [ ] OM with `role: office_manager` sees Force Close action on Pages Hub only when `laserClear: false` OR `status: "stalled"` (laser-gated visibility).
- [ ] Force Close performs fresh money-beam read (not cached), generates new `beamHash`, appends to `force_close_log.jsonl` with fields: `timestamp`, `actor`, `beamHash`, `laserOverride` (bool), `shadowMode` (bool), `systemOfRecord` (bool, always false until cutover).
- [ ] HAL chat cites Force Close status when answering “Did we close today?” (distinguish auto vs manual).
- [ ] No write-backs to SoftDent or QB during Force Close (attest-only, same as export-failure fallback).
- [ ] Path hygiene: all new assets under `C:\Users\mreno\newridgefamilyfinancial`; no `C:\NewRidgeFamilyFinancial` references.
- [ ] CLI `force_close.py` continues to work (back-compat), but optical page is the blessed path for OM.

## 6. Executive Summary (5 bullets)
- **Shadow mode began today** (`shadowStartedAt: 2026-07-15T21:10:23Z`) with `forceCloseExists: false`, creating an operational single-point-of-failure if morning auto-close stalls.
- **Force Close is the safety valve**: laser-gated UI control allowing OM to complete period-close manually when red lasers or scheduler hangs block automation.
- **Attest-only, never write-back**: Force Close uses the same beam-grounded, empty≠$0 logic as the export-hardening fallback, appending to a separate `force_close_log.jsonl` for audit distinction.
- **Real paths only**: optical page at `site/nr2-optical-page-force-close.html`, gateway endpoint in `nr2_hal_gateway.py`, logs in `app_data/nr2/ops/`.
- **Validation via deliberate laser block**: temporarily stale QB data triggers red laser, OM exercises Force Close, verifies JSONL row with `laserOverride: true`, confirms desk remains unblocked.

## 7. Approval Checklist
- [ ] Force Close UI does **not** appear when `laserClear: true` and `status: "completed"` (prevents accidental manual override during healthy auto-close).
- [ ] `force_close_log.jsonl` is append-only; no truncation or mutation by application code (immutability for compliance).
- [ ] `systemOfRecord` flag remains `false` during Force Close (shadow mode persists; no premature cutover).
- [ ] Role enforcement strict: `office_manager` capability required; `read_financial` alone insufficient.
- [ ] Path hygiene verified: zero references to `C:\NewRidgeFamilyFinancial`; all ops under `C:\Users\mreno\newridgefamilyfinancial`.
- [ ] BlueNote announce filter updated to include Force Close events (if BlueNote ship is concurrent).
