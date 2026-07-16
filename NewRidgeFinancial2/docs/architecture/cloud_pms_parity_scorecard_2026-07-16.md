# Cloud PMS parity scorecard — baseline 2026-07-16

**Review cadence:** Quarterly (or after major NR2 build)  
**Build:** `nr2-12073-excel-gate-all-next`  
**Source matrix:** [MOONSHOT_CLOUD_PMS_PARITY_2026-07-16.md](../MOONSHOT_CLOUD_PMS_PARITY_2026-07-16.md)

Legend: **LIVE** · **PARTIAL** · **BLOCKED** (operator) · **NEVER** (by design) · **MISSING**

---

## Pillar scorecard

| # | Pillar | NR2 status | Cloud analog | Notes |
|---|--------|------------|--------------|-------|
| 1 | Scheduling + online booking | **NEVER** | Curve/Ascend scheduler | SoftDent clinical SOR; no write-back |
| 2 | Clinical charting / imaging / eRx | **NEVER** | Ascend chart | Stays in SoftDent |
| 3 | Treatment planning / case presentation | **NEVER** | Jarvis case presentation | No clinical write path |
| 4 | Insurance / claims / ERA / ledger | **PARTIAL** | Ascend claims + ERA | Claims page LIVE; ERA inbox LIVE; no claim submit |
| 5 | Patient engagement | **PARTIAL** | Lighthouse 360 | Financial recall CSV bridge; no NR2 SMS embed |
| 6 | Reporting / analytics / KPIs | **PARTIAL** | Jarvis huddle | Analytics page LIVE; morning bundle **BLOCKED** (Excel gate) |
| 7 | Integrated payments | **NEVER** | Curve Pay | QB + SoftDent Pay outside NR2 |
| 8 | Multi-location / DSO | **PARTIAL** | Enterprise rollup | Single office today; financial consolidation path documented |
| 9 | Browser / mobile anywhere | **PARTIAL** | Cloud login | LAN HAL hub; VPN optional |
| 10 | Auto updates / backup | **PARTIAL** | Cloud backup | NR2 build updates; SoftDent on-prem backup |

---

## Operational metrics (P1 exit)

| Metric | Target | Baseline 2026-07-16 | Measure |
|--------|--------|---------------------|---------|
| Morning bundle success | ≥95% weekdays | **BLOCKED** (`morningBundle.ok=false`) | `importReadiness.periodClose.morningBundle` |
| Money beam freshness | &lt;24h | **LIVE** (beams fresh) | `importReadiness` lasers |
| Desk smoke MATCH | ≥95% | **LIVE** (after beam refresh) | `/api/health/desk-smoke` |
| Trellis withBenefits | &gt;0 clinic days | **AWAITING** scrape | `prove_trellis_withbenefits_am.py` |
| Claims payer batch | &lt;2 min | **LIVE** (export + filters) | Staff timed test |
| Morning huddle time | &lt;5 min | **LIVE** (analytics page) | `/nr2-optical-page-analytics.html` |
| HAL money honesty | 0 invented $ | **LIVE** | Beam + emptyNotZero policy |
| Shadow days | ≥30 pre-cutover | **IN PROGRESS** | `pilot.shadowDaysElapsed` |

---

## Shipped augmentation packages (reference)

| Sprint | Package | Commit area |
|--------|---------|-------------|
| P0 | Beam drift, morning bundle CLI, desk smoke | `ba4cb2a`, scripts |
| P1 | ERA inbox, analytics huddle, claims ERA | `5128dd2`, `35c6f3c` |
| P1 | TXN ledger filter, Trellis AM proof, payer backfill | `0495f3c`, `72c7108` |
| P1 | Hygiene recall tile | `84bd62b` |
| P2 | Financial recall Lighthouse CSV | `71ed811` |
| P3 | Architecture + cutover + this scorecard | (this doc set) |

---

## Next quarterly actions

1. Re-run Moonshot parity consult or update this table manually.
2. Record morning bundle success rate after Excel enablement.
3. Log Trellis AM proof streak (3 weekdays).
4. Operator sign cutover attestation only when [nr2_cutover_to_sor.md](../runbooks/nr2_cutover_to_sor.md) gates pass.

---

## Sign-off (operator)

| Role | Name | Date | Notes |
|------|------|------|-------|
| Owner / dentist | | | |
| Office manager | | | |
| IT / NR2 operator | | | |

Baseline recorded **2026-07-16** — shadow SOR remains `false` until cutover ceremony.
