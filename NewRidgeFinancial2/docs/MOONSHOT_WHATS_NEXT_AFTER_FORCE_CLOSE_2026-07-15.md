# Moonshot AI — What's Next After Force Close Optical (CONSULT ONLY)

**Date:** 2026-07-15
**Model:** `kimi-k2.5`
**Key:** OPENROUTER_API_KEY
**Status:** ok
**Repo root:** `C:\Users\mreno\newridgefamilyfinancial`
**Prior:** `8a468c1` Force Close · `23f85a9` docs
**Script:** `scripts/run_moonshot_whats_next_after_force_close_consult.py`
**Apply:** DO NOT APPLY until operator approves.

## Operator request (verbatim)

> next

---

# Verdict: BlueNote alert integration for attest_only fallback, laser stall, and Force Close events (shadow-mode operational visibility).

## 0. Operator Intent (verbatim)
next

## 1. Recommended NEXT (name, why now, effort, REAL files/ops, validation gate)

**Package:** BlueNote Ops Alert Integration (Attest-Only / Stall / Force Close)

**Why now:** LIVE AUDIT shows `pilot.phase: "shadow"` began today (`shadowStartedAt: "2026-07-15T21:10:23+00:00"`) with `systemOfRecord: false`. The desk is now flying without historical safety nets. While Force Close shipped (`forceCloseLogExists: true`), the desk currently discovers attest-only fallbacks, laser stalls, or Force Close interventions only by checking logs or noticing missing data. In shadow mode, these events require immediate human awareness—attest-only means SoftDent data is stale/missing (data truth degradation), and Force Close indicates system stress. BlueNote alerts provide the real-time operational visibility required for safe shadow operations.

**Effort:** Low-Medium (3–4 hours) — webhook dispatch to existing BlueNote endpoint, context-rich message formatting, throttling/de-duplication (5-min windows), role-aware routing (OM vs Admin).

**REAL files/ops:**
- `C:\Users\mreno\newridgefamilyfinancial\NewRidgeFinancial2\daily_closeout.py` — dispatch `bluenote_alert()` on `fallback="attest_only"` in `run_period_close()`; include `beamHash`, `period`, `softdentDisplay`, `laserClear` status
- `C:\Users\mreno\newridgefamilyfinancial\NewRidgeFinancial2\nr2_http_server.py` — dispatch alert on `POST /api/period-close/force` initiation (include `actor`, `laserOverride`, `reason`); dispatch on laser state transition to `red` / `blockingCount > 0` for >5 minutes
- `C:\Users\mreno\newridgefamilyfinancial\NewRidgeFinancial2\nr2_hal_gateway.py` (if separate from http_server) — alert injection point for HAL-triggered close failures
- `C:\Users\mreno\newridgefamilyfinancial\app_data\nr2\config\bluenote_webhook.json` — endpoint URL, secret, throttle config (e.g., max 1 alert per event type per 5 min)
- `C:\Users\mreno\newridgefamilyfinancial\NewRidgeFinancial2\test_portal_ops.py` — mock BlueNote receiver to verify payload schema

**Validation gate:**
1. Induce SoftDent GUI export failure (block file output) → confirm close completes with `fallback="attest_only"` → verify BlueNote receives alert with correct `beamHash`, `period`, and `softdentDisplay: "Financial data unavailable for that source"` (empty≠$0 compliance)
2. Induce laser block (mock `alignmentLasers.red: true`) → verify stall alert fires after 5-min threshold
3. Trigger Force Close via optical page → verify immediate alert with `laserOverride` flag and `actor: "optical-om"`

## 2. Why this beats the other candidates now

- **vs. Formal beamHash desk proof:** Hash verification is integrity hygiene, but the desk currently has no automated way to know when data truth is compromised (attest-only) or when manual intervention occurs (Force Close). Alerting is prerequisite to trusting the hash; without knowing a Force Close happened, citing the hash is meaningless context.
- **vs. Expand morning SoftDent pull:** More data coverage is valuable, but expanding the pull surface area while in shadow mode without alerting on failures increases risk. If the expanded pull fails silently, the desk assumes coverage that doesn't exist. Alert infrastructure must precede data expansion.
- **vs. QB sync consent UX:** QB datasets are currently stale (optional) but not blocking. Data truth issues in SoftDent (required) are blocking and silent if attest-only fallback triggers without alert.
- **vs. Desk smoke script:** Scripts are reactive validation tools; BlueNote alerts are proactive operational signals required for real-time decision-making during shadow mode.

## 3. Runner-ups (2–3)

1. **Formal beamHash desk proof across HAL chat + optical pages** — Ensure HAL cites identical `beamHash` as optical AR/QB pages on live 8765. Prevents hash drift confusion. Deferred because alerting on data quality events takes precedence over verifying citation consistency during shadow mode.
2. **Expand morning SoftDent pull to aging+register+collections** — Hardened export path exists; expand coverage to complete AR picture. Deferred until alert infrastructure confirms current pulls succeed/fail visibly.
3. **Desk smoke script: close status + money-beams + Force Close availability + hash identity** — Automated health check for daily standup. Deferred because BlueNote alerts provide continuous monitoring vs. point-in-time scripts.

## 4. What NOT to redo

- Force Close optical control (shipped in nr2-12034)
- SoftDent export retries/attest-only fallback (shipped in nr2-12031)
- Morning SoftDent aging auto-pull (shipped)
- Money-beam optical/landing bind (shipped)
- Period-close hub surface (shipped)
- Consent-free SoftDent export (shipped)
- Path hygiene (C:\Users\mreno\newridgefamilyfinancial only)
- Money honesty (empty ≠ $0)
- BlueNote chrome filter (shipped)

## 5. Acceptance criteria

- [ ] BlueNote webhook fires within 30 seconds of `attest_only` fallback triggered in `daily_closeout.py`
- [ ] Alert payload includes: `eventType` (attest_only|force_close|laser_stall), `period`, `beamHash`, `actor`, `laserClear` (boolean), `systemOfRecord` (false), `timestampISO`, `haltUrl` (link to optical status page)
- [ ] Throttling: max 1 alert per `eventType` per 5-minute window to prevent spam during flapping
- [ ] Force Close alert fires immediately on API call initiation (before completion), with `laserOverride` boolean
- [ ] Laser stall alert fires only after lasers red/blocking for >5 minutes (prevents noise on brief import hiccups)
- [ ] No PII in alert payload (use patient counts, not names; use beamHash for correlation)
- [ ] Test mode: `BLUENOTE_TEST_MODE=true` routes alerts to test channel without throttling

## 6. Executive Summary (5 bullets)

- **Shadow mode requires eyes:** With `systemOfRecord: false` active as of today, the desk cannot afford to miss silent data degradations (attest-only) or manual overrides (Force Close).
- **Silent failures are the risk:** The attest-only fallback saves the close from stalling but hides SoftDent data absence; without alerting, the desk operates on stale AR until someone checks logs.
- **BlueNote is the existing nerve:** Leverage the already-integrated BlueNote channel (used for prior "BlueNote-only announce") rather than building new notification surface.
- **Low effort, high safety:** 3–4 hours to instrument three critical events (attest-only, Force Close, laser stall) with throttling prevents alert fatigue while ensuring operational awareness.
- **Enables future expansion:** Once alerting proves reliable, expanding morning pulls (aging+register+collections) is safe; without it, expansion adds unmonitored complexity.

## 7. Approval Checklist

- [ ] Confirm BlueNote webhook URL and auth secret available in env/config
- [ ] Confirm event throttle timing (5 min proposed) acceptable to OM desk
- [ ] Confirm "no PII in alerts" policy acceptable (hashes and counts only)
- [ ] Verify `forceCloseLogExists: true` in LIVE AUDIT means endpoint is ready to trigger alerts
- [ ] Acknowledge runner-ups (beamHash proof, expand pull) are explicitly deferred, not cancelled
