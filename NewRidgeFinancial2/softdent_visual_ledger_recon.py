"""HAL-10592 / HON-002 — Visual-audit × ledger spine reconciliation.

Compare SoftDent Print Preview Insurance Income last-page aggregates
(HAL-10590) to SoftDent ledger code-2 insurance payment sums for the same
period. Flag variance only — never invent gold payment lines, never SoftDent
write-back. empty != $0 (HAL-10591 honesty gate).
"""

from __future__ import annotations

import json
import re
import sqlite3
from datetime import date, datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from softdent_gold_payment_pipeline import audit_gold_payment_pipeline
from softdent_insco_ada_spine import INS_PAYMENT_CODES, table_exists
from softdent_print_preview_audit import list_print_preview_audits
from softdent_treatment_planning import resolve_analytics_db, resolve_exports_dir
from ui_honesty_policy import (
    SOURCE_LEDGER_SPINE,
    SOURCE_PRINT_PREVIEW_VISUAL,
    enforce_empty_not_zero,
    is_empty_money,
    parse_money_or_empty,
)

DEF_ID = "HAL-10592"
PACKAGE_BUILD_ID = "hal-10592"

VARIANCE_THRESHOLD_ABSOLUTE = 5.00
VARIANCE_THRESHOLD_PERCENT = 5.0
SOURCE_LEDGER_CODE2 = "ledger_code2_period_sum"


class ReconciliationResult(str, Enum):
    MATCH = "MATCH"
    VARIANCE_WITHIN_TOLERANCE = "VARIANCE_WITHIN_TOLERANCE"
    VARIANCE_EXCEEDS_THRESHOLD = "VARIANCE_EXCEEDS_THRESHOLD"
    INSUFFICIENT_VISUAL = "INSUFFICIENT_VISUAL"
    INSUFFICIENT_LEDGER = "INSUFFICIENT_LEDGER"
    HONESTY_HALT = "HONESTY_HALT"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_date_range(raw: str | None) -> tuple[str | None, str | None]:
    """Parse visual-audit dateRange into (start, end) ISO dates (inclusive)."""
    text = str(raw or "").strip()
    if not text:
        return None, None

    # YYYY-MM (calendar month)
    m = re.fullmatch(r"(\d{4})-(\d{2})", text)
    if m:
        from calendar import monthrange

        y, mo = int(m.group(1)), int(m.group(2))
        start = date(y, mo, 1)
        end = date(y, mo, monthrange(y, mo)[1])
        return start.isoformat(), end.isoformat()

    # YYYY-MM-DD..YYYY-MM-DD or with / or " to "
    m2 = re.search(
        r"(\d{4}-\d{2}-\d{2})\s*(?:\.\.|/|–|—|to)\s*(\d{4}-\d{2}-\d{2})",
        text,
        re.I,
    )
    if m2:
        return m2.group(1), m2.group(2)

    # single day
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return text, text

    return None, None


def sum_ledger_code2_payments(
    *,
    period_start: str,
    period_end: str,
    db_path: Path | None = None,
) -> dict[str, Any]:
    """Sum SoftDent code-2 insurance payment amounts in period (not gold lines)."""
    out: dict[str, Any] = {
        "ok": False,
        "ledgerTotal": None,
        "rowCount": 0,
        "periodStart": period_start,
        "periodEnd": period_end,
        "sourceTag": SOURCE_LEDGER_CODE2,
        "emptyIsNotZero": True,
        "message": None,
    }
    path = Path(db_path) if db_path else resolve_analytics_db()
    if path is None or not Path(path).is_file():
        out["message"] = "Analytics DB missing — ledger sum unavailable (empty != $0)"
        return out
    conn = sqlite3.connect(str(path))
    try:
        if not table_exists(conn, "sd_account_transactions"):
            out["message"] = "sd_account_transactions missing — empty != $0"
            return out
        codes = sorted(INS_PAYMENT_CODES)
        placeholders = ",".join("?" for _ in codes)
        rows = conn.execute(
            f"""
            SELECT COUNT(*),
                   SUM(
                     COALESCE(cash, 0) + COALESCE("check", 0) + COALESCE(credit, 0)
                   )
            FROM sd_account_transactions
            WHERE service_date >= ? AND service_date <= ?
              AND TRIM(procedure) IN ({placeholders})
            """,
            (period_start, period_end, *codes),
        ).fetchone()
        count = int((rows or (0, None))[0] or 0)
        total_raw = (rows or (0, None))[1]
        out["rowCount"] = count
        if count == 0 or total_raw is None:
            # No rows → insufficient, not $0.00
            out["ledgerTotal"] = None
            out["message"] = (
                f"No SoftDent code-2 payment rows in {period_start}..{period_end} "
                "(empty != $0)"
            )
            out["ok"] = True
            return out
        out["ledgerTotal"] = float(total_raw)
        out["ok"] = True
        out["message"] = (
            f"Ledger code-2 sum {out['ledgerTotal']:,.2f} from {count} row(s) "
            f"({period_start}..{period_end})"
        )
        return out
    finally:
        conn.close()


def classify_variance(
    visual: float | None,
    ledger: float | None,
    *,
    abs_threshold: float = VARIANCE_THRESHOLD_ABSOLUTE,
    pct_threshold: float = VARIANCE_THRESHOLD_PERCENT,
) -> dict[str, Any]:
    """Classify visual vs ledger delta with HON-001 honesty gates."""
    result: dict[str, Any] = {
        "visualTotal": visual,
        "ledgerTotal": ledger,
        "delta": None,
        "deltaAbs": None,
        "deltaPct": None,
        "thresholdAbsolute": abs_threshold,
        "thresholdPercent": pct_threshold,
        "thresholdViolated": False,
        "honestyCheckPassed": True,
        "result": ReconciliationResult.HONESTY_HALT.value,
        "emptyIsNotZero": True,
        "triggersGoldIngest": False,
        "def": DEF_ID,
    }

    # Honesty: null must never be treated as 0 for math
    if is_empty_money(visual):
        result["result"] = ReconciliationResult.INSUFFICIENT_VISUAL.value
        result["honestyCheckPassed"] = True
        result["message"] = "Visual audit total missing — exclude from compare (empty != $0)"
        return result
    if is_empty_money(ledger):
        result["result"] = ReconciliationResult.INSUFFICIENT_LEDGER.value
        result["honestyCheckPassed"] = True
        result["message"] = "Ledger code-2 sum missing — exclude from compare (empty != $0)"
        return result

    v = parse_money_or_empty(visual)
    l = parse_money_or_empty(ledger)
    if v is None or l is None:
        result["result"] = ReconciliationResult.HONESTY_HALT.value
        result["honestyCheckPassed"] = False
        result["message"] = "Honesty halt — refused to coerce empty to $0.00 for reconciliation"
        return result

    delta = v - l
    delta_abs = abs(delta)
    base = max(abs(v), abs(l), 0.01)
    delta_pct = (delta_abs / base) * 100.0
    result["delta"] = round(delta, 2)
    result["deltaAbs"] = round(delta_abs, 2)
    result["deltaPct"] = round(delta_pct, 4)

    within_abs = delta_abs <= float(abs_threshold)
    within_pct = delta_pct <= float(pct_threshold)
    if delta_abs < 0.005:
        result["result"] = ReconciliationResult.MATCH.value
        result["thresholdViolated"] = False
        result["message"] = "Visual audit matches ledger code-2 sum"
    elif within_abs or within_pct:
        result["result"] = ReconciliationResult.VARIANCE_WITHIN_TOLERANCE.value
        result["thresholdViolated"] = False
        result["message"] = (
            f"Variance ${delta_abs:,.2f} ({delta_pct:.2f}%) within tolerance "
            f"(${abs_threshold:,.2f} or {pct_threshold}%)"
        )
    else:
        result["result"] = ReconciliationResult.VARIANCE_EXCEEDS_THRESHOLD.value
        result["thresholdViolated"] = True
        result["message"] = (
            f"Variance ${delta_abs:,.2f} ({delta_pct:.2f}%) exceeds threshold — "
            "flag only; do not invent gold lines"
        )
    return result


def reconcile_visual_vs_ledger(
    *,
    period: str | None = None,
    dest: Path | None = None,
    db_path: Path | None = None,
    abs_threshold: float = VARIANCE_THRESHOLD_ABSOLUTE,
    pct_threshold: float = VARIANCE_THRESHOLD_PERCENT,
) -> dict[str, Any]:
    """Reconcile latest matching Print Preview visual audit to ledger code-2 sum."""
    gold = audit_gold_payment_pipeline()
    audits = list_print_preview_audits(dest=dest, limit=50)
    rows = list(audits.get("rows") or [])

    # Prefer InsuranceIncome rows; fall back to any with dateRange
    candidates = [
        r
        for r in rows
        if isinstance(r, dict)
        and str(r.get("reportType") or "") in {"InsuranceIncome", ""}
    ] or [r for r in rows if isinstance(r, dict)]

    selected: dict[str, Any] | None = None
    period_start = period_end = None
    period_key = str(period or "").strip() or None

    for row in reversed(candidates):
        dr = str(row.get("dateRange") or "")
        start, end = parse_date_range(dr)
        if period_key:
            # Match YYYY-MM or exact range containing period key
            if period_key in {dr, (start or "")[:7], start, f"{start}..{end}"}:
                selected = row
                period_start, period_end = start, end
                break
            if start and end and len(period_key) == 7 and start.startswith(period_key):
                selected = row
                period_start, period_end = start, end
                break
        else:
            if start and end:
                selected = row
                period_start, period_end = start, end
                break
            if selected is None:
                selected = row

    visual_raw = (selected or {}).get("lastPageAggregateTotal") if selected else None
    visual_honesty = enforce_empty_not_zero(
        visual_raw, source_tag=SOURCE_PRINT_PREVIEW_VISUAL
    )

    out: dict[str, Any] = {
        "ok": True,
        "def": DEF_ID,
        "packageBuildId": PACKAGE_BUILD_ID,
        "period": period_key or (f"{period_start}..{period_end}" if period_start else None),
        "periodStart": period_start,
        "periodEnd": period_end,
        "visualAudit": selected,
        "visualTotal": visual_honesty.get("value"),
        "visualDisplay": visual_honesty.get("display"),
        "visualBadge": visual_honesty.get("badge"),
        "ledger": None,
        "ledgerTotal": None,
        "ledgerDisplay": "—",
        "comparison": None,
        "gapCode": gold.get("gapCode"),
        "paymentLines": int(gold.get("paymentLines") or 0),
        "triggersGoldIngest": False,
        "emptyIsNotZero": True,
        "honesty": (
            "Visual audit vs ledger code-2 sum only — flag variance; "
            "never invent gold payment lines; empty != $0"
        ),
        "checkedAt": _utc_now(),
    }

    if not selected:
        out["comparison"] = classify_variance(None, None)
        out["comparison"]["result"] = ReconciliationResult.INSUFFICIENT_VISUAL.value
        out["comparison"]["message"] = "No Print Preview visual audit recorded yet"
        out["ok"] = True
        return out

    if not period_start or not period_end:
        out["comparison"] = classify_variance(
            visual_honesty.get("value"), None, abs_threshold=abs_threshold, pct_threshold=pct_threshold
        )
        out["comparison"]["result"] = ReconciliationResult.INSUFFICIENT_VISUAL.value
        out["comparison"]["message"] = (
            "Visual audit lacks parseable dateRange — cannot align ledger period "
            "(empty != $0)"
        )
        return out

    if is_empty_money(visual_raw):
        out["comparison"] = classify_variance(
            None, None, abs_threshold=abs_threshold, pct_threshold=pct_threshold
        )
        return out

    ledger = sum_ledger_code2_payments(
        period_start=period_start, period_end=period_end, db_path=db_path
    )
    out["ledger"] = ledger
    ledger_total = ledger.get("ledgerTotal")
    ledger_honesty = enforce_empty_not_zero(
        ledger_total, source_tag=SOURCE_LEDGER_SPINE
    )
    out["ledgerTotal"] = ledger_honesty.get("value")
    out["ledgerDisplay"] = ledger_honesty.get("display")

    comparison = classify_variance(
        visual_honesty.get("value"),
        ledger_honesty.get("value"),
        abs_threshold=abs_threshold,
        pct_threshold=pct_threshold,
    )
    out["comparison"] = comparison
    out["thresholdViolated"] = bool(comparison.get("thresholdViolated"))
    out["result"] = comparison.get("result")
    return out


def run_ops_10592_visual_ledger_recon(
    *,
    period: str | None = None,
    dest: Path | None = None,
    db_path: Path | None = None,
) -> dict[str, Any]:
    """OPS runner: status snapshot only — never mutates SoftDent or gold tables."""
    recon = reconcile_visual_vs_ledger(period=period, dest=dest, db_path=db_path)
    try:
        exports = Path(dest) if dest else resolve_exports_dir()
        exports.mkdir(parents=True, exist_ok=True)
        path = exports / f"visual_ledger_recon_{datetime.now(timezone.utc).date().isoformat()}.json"
        path.write_text(json.dumps(recon, indent=2, default=str), encoding="utf-8")
        recon["jsonPath"] = str(path)
    except Exception as exc:  # noqa: BLE001
        recon["exportError"] = f"{type(exc).__name__}:{exc}"
    return recon


def format_visual_ledger_recon_reply(result: dict[str, Any] | None = None) -> str:
    r = result if isinstance(result, dict) else reconcile_visual_vs_ledger()
    cmp_ = r.get("comparison") if isinstance(r.get("comparison"), dict) else {}
    v_disp = r.get("visualDisplay") or "—"
    if r.get("visualBadge") == "visual" and r.get("visualTotal") is not None:
        v_disp = f"[visual] {v_disp}"
    l_disp = r.get("ledgerDisplay") or "—"
    return (
        f"Visual×ledger recon ({DEF_ID}): result={cmp_.get('result') or r.get('result')}; "
        f"period={r.get('period')}; visual={v_disp}; ledger={l_disp}; "
        f"delta={cmp_.get('delta')}; thresholdViolated={cmp_.get('thresholdViolated')}; "
        f"gapCode={r.get('gapCode')}; paymentLines={r.get('paymentLines')}. "
        "Flag only — does not create gold lines. empty != $0."
    )


def visual_ledger_recon_widget() -> dict[str, Any]:
    r = reconcile_visual_vs_ledger()
    cmp_ = r.get("comparison") if isinstance(r.get("comparison"), dict) else {}
    result_code = str(cmp_.get("result") or r.get("result") or "")
    if result_code == ReconciliationResult.MATCH.value:
        status, tone = "ok", "ok"
    elif result_code == ReconciliationResult.VARIANCE_WITHIN_TOLERANCE.value:
        status, tone = "ok", "warn"
    elif result_code == ReconciliationResult.VARIANCE_EXCEEDS_THRESHOLD.value:
        status, tone = "warn", "danger"
    else:
        status, tone = "empty", "warn"
    message = str(cmp_.get("message") or r.get("honesty") or "No comparison yet")
    return {
        "id": "softdent-visual-ledger-recon",
        "type": "status",
        "label": "Visual×Ledger Variance (HAL-10592)",
        "size": "full",
        "status": status,
        "tone": tone,
        "message": message,
        "hint": (
            "Compares Print Preview Insurance Income last-page total to SoftDent "
            "ledger code-2 payment sum for the same period. Alert only."
        ),
        "result": result_code,
        "period": r.get("period"),
        "visualTotal": r.get("visualTotal"),
        "visualDisplay": r.get("visualDisplay"),
        "visualBadge": r.get("visualBadge"),
        "ledgerTotal": r.get("ledgerTotal"),
        "ledgerDisplay": r.get("ledgerDisplay"),
        "delta": cmp_.get("delta"),
        "thresholdViolated": cmp_.get("thresholdViolated"),
        "gapCode": r.get("gapCode"),
        "paymentLines": r.get("paymentLines"),
        "confirmation": (
            "Variance flag only; no payment lines will be created"
        ),
        "halChips": [
            {"label": "Visual ledger recon status", "query": "visual ledger reconciliation status"},
            {
                "label": "What is visual vs ledger variance?",
                "query": "What does visual audit vs ledger reconciliation mean?",
            },
        ],
        "honesty": r.get("honesty"),
        "emptyIsNotZero": True,
        "def": DEF_ID,
        "packageBuildId": PACKAGE_BUILD_ID,
        "triggersGoldIngest": False,
    }


if __name__ == "__main__":
    print(json.dumps(run_ops_10592_visual_ledger_recon(), indent=2, default=str)[:5000])
