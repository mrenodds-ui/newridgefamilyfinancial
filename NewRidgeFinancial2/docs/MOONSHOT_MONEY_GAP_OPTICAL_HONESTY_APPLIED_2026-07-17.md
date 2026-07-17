# Claims↔QB Money-Gap Optical Honesty — APPLIED

**Date:** 2026-07-17  
**Consult:** `MOONSHOT_WHATS_NEXT_AFTER_PMS_EVAL_CONTINUE_2026-07-17.md`  
**Operator:** approve

## What was done

| Surface | Change |
|---------|--------|
| `hal_brain_tools.money_beam_attestation` | Added `metricGapHonesty` (labels SoftDent AR outstanding vs QB monthly revenue; `notAutoReconciled` / `noReconcileCta`; raw \|Δ\| when both live; empty ≠ $0). Prompt block cites METRIC GAP honesty. |
| Hub Variance face | Relabeled **Metric gap · not reconciled**; paints via `paintMetricGapHonesty`. |
| HAL Active beams | Added Metric gap face (no Reconcile CTA). |
| New page | `nr2-optical-page-money-gap.html` + `.js` — three faces + honesty chip. |
| Nav / routes | Metric Gap in optical nav; `money-gap` / `metric-gap` / `gap` → page. |
| Tests | `test_hal_money_beam_attestation` metric-gap cases; optical route resolve. |

## Live validation (2026-07-17)

```text
SoftDent AR outstanding: $52,270
QuickBooks monthly revenue: $78,399
raw |Δ|: $26,129.22
label: Different Metrics — Not Auto-Reconciled
bothLive: true · notAutoReconciled: true · no Reconcile CTA
```

Unit tests: `python -m unittest test_hal_money_beam_attestation` → OK.

## Acceptance (consult)

- [x] Optical surfaces show SoftDent AR + QB revenue + raw delta with **Different Metrics — Not Auto-Reconciled**
- [x] No Reconcile CTA / no auto-reconcile claim
- [x] Empty ≠ $0 · ERA awaiting real 835 noted on money-gap page
- [x] SoftDent Excel grey-hold untouched (no SoftDent GUI)
- [x] forceClose / supervised cutover not mentioned on page

## What was NOT done

- SoftDent Excel / morning_bundle · invent ERA 835 · Trellis withBenefits invent · SoftDent write-back · invent reconcile action

## Operator next

1. Carestream: un-grey SoftDent Excel → **Excel is clickable — run morning bundle**
2. Drop real ERA `.835` → ingest per ERA runbook
3. Wait Trellis withBenefits ~2026-07-20 · shadow clock continues
