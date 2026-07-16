"""Financial recall export for Lighthouse bridge (board-safe · read-only · no SMS embed)."""

from __future__ import annotations

import csv
import io
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
_OFFICE = _REPO / "app_data" / "nr2" / "office"
_CONFIG_PATH = _OFFICE / "lighthouse_config.yaml"
_CONFIG_EXAMPLE = _OFFICE / "lighthouse_config.yaml.example"

_DEFAULTS: dict[str, Any] = {
    "financialRecall": {
        "minBalance": 100.0,
        "minMonthsSinceVisit": 6,
        "maxRows": 200,
    },
    "lighthouse": {"enabled": False},
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_lighthouse_config() -> dict[str, Any]:
    path = _CONFIG_PATH if _CONFIG_PATH.is_file() else _CONFIG_EXAMPLE
    if not path.is_file():
        return dict(_DEFAULTS)
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        return dict(_DEFAULTS)
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except OSError:
        return dict(_DEFAULTS)
    if not isinstance(payload, dict):
        return dict(_DEFAULTS)
    merged = dict(_DEFAULTS)
    fr = payload.get("financialRecall")
    if isinstance(fr, dict):
        merged["financialRecall"] = {**merged["financialRecall"], **fr}
    lh = payload.get("lighthouse")
    if isinstance(lh, dict):
        merged["lighthouse"] = {**merged.get("lighthouse", {}), **lh}
    return merged


def balance_band(amount: float | None) -> str:
    if amount is None:
        return "—"
    value = float(amount)
    if value < 100:
        return "$0-99"
    if value < 250:
        return "$100-249"
    if value < 500:
        return "$250-499"
    return "$500+"


def months_since_visit(last_visit: str, *, today: date | None = None) -> int | None:
    text = str(last_visit or "").strip()[:10]
    if len(text) < 10:
        return None
    try:
        visit = datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        return None
    ref = today or datetime.now(timezone.utc).date()
    return max(0, (ref.year - visit.year) * 12 + (ref.month - visit.month))


def financial_recall_candidates(
    *,
    min_balance: float | None = None,
    min_months_since_visit: int | None = None,
    max_rows: int | None = None,
) -> dict[str, Any]:
    """Patients with open claim balance and stale last visit (initials+hash · no full names in export)."""
    cfg = load_lighthouse_config().get("financialRecall") or {}
    min_bal = float(min_balance if min_balance is not None else cfg.get("minBalance") or 100.0)
    min_months = int(
        min_months_since_visit
        if min_months_since_visit is not None
        else cfg.get("minMonthsSinceVisit") or 6
    )
    cap = max(1, min(int(max_rows if max_rows is not None else cfg.get("maxRows") or 200), 500))

    from nr2_softdent_daily import (
        _connect,
        _filter_unpaid_claim_rows,
        _hash_patient_id,
        _initials_from_name,
        _patient_name_to_id_index,
        _resolve_claim_patient_id,
    )

    try:
        from patient_dossier import name_hash as _name_hash
    except Exception:
        _name_hash = None  # type: ignore[assignment,misc]

    conn, db_path = _connect()
    if not conn:
        return {
            "ok": False,
            "hasData": False,
            "candidates": [],
            "count": 0,
            "config": {"minBalance": min_bal, "minMonthsSinceVisit": min_months, "maxRows": cap},
            "emptyNotZero": True,
            "readOnly": True,
            "error": "analytics_db_missing",
        }

    open_where = """
        COALESCE(claim_amount, 0) > 0
          AND UPPER(TRIM(COALESCE(claim_status, ''))) NOT IN (
            'PAID', 'CLOSED', 'DENIED', 'COMPLETE', 'COMPLETED',
            'DONE', 'SETTLED', 'CANCELLED', 'CANCELED', 'VOID', 'VOIDED',
            'DENIED-FINAL'
          )
          AND UPPER(TRIM(COALESCE(claim_status, ''))) NOT LIKE 'PAID%'
          AND UPPER(TRIM(COALESCE(claim_status, ''))) NOT LIKE '%COMPLETE%'
    """
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT claim_id, patient_name, payer, service_date, claim_amount, claim_status
            FROM sd_claims
            WHERE """
            + open_where
        )
        raw_rows = list(cur.fetchall())
        name_to_id = _patient_name_to_id_index(conn)
        rows = _filter_unpaid_claim_rows(raw_rows, name_to_id=name_to_id)

        by_patient: dict[str, dict[str, Any]] = {}
        for claim_id, patient, _payer, service_date, amount, _status in rows:
            patient_raw = str(patient or "").strip()
            patient_id = _resolve_claim_patient_id(str(claim_id or ""), patient_raw, name_to_id)
            if not patient_id:
                continue
            amt = round(float(amount or 0), 2)
            if amt <= 0:
                continue
            bucket = by_patient.get(patient_id)
            if not bucket:
                bucket = {
                    "patientId": patient_id,
                    "patientName": patient_raw,
                    "balance": 0.0,
                    "claimCount": 0,
                }
                by_patient[patient_id] = bucket
            bucket["balance"] = round(float(bucket["balance"]) + amt, 2)
            bucket["claimCount"] = int(bucket["claimCount"]) + 1
            dos = str(service_date or "")[:10]
            if dos and (not bucket.get("latestServiceDate") or dos > bucket["latestServiceDate"]):
                bucket["latestServiceDate"] = dos

        last_visit_by_id: dict[str, str] = {}
        if by_patient:
            placeholders = ",".join("?" for _ in by_patient)
            cur.execute(
                f"SELECT patient_id, last_visit_date FROM sd_patients WHERE patient_id IN ({placeholders})",
                tuple(by_patient.keys()),
            )
            for pid, last_visit in cur.fetchall():
                last_visit_by_id[str(pid or "")] = str(last_visit or "")

        candidates: list[dict[str, Any]] = []
        for patient_id, bucket in by_patient.items():
            balance = float(bucket.get("balance") or 0)
            if balance < min_bal:
                continue
            last_visit = last_visit_by_id.get(patient_id, "")
            months = months_since_visit(last_visit)
            if months is None or months < min_months:
                continue
            patient_name = str(bucket.get("patientName") or "")
            row = {
                "initials": _initials_from_name(patient_name) if patient_name else "P—",
                "nameHash": _name_hash(patient_name) if patient_name and _name_hash else "——",
                "patientHash": _hash_patient_id(patient_id),
                "phoneLast4": "—",
                "balanceBand": balance_band(balance),
                "balance": balance,
                "lastVisit": last_visit or "—",
                "monthsSinceVisit": months,
                "claimCount": int(bucket.get("claimCount") or 0),
                "emptyNotZero": True,
            }
            candidates.append(row)

        candidates.sort(
            key=lambda r: (-float(r.get("balance") or 0), -int(r.get("monthsSinceVisit") or 0))
        )
        candidates = candidates[:cap]
    finally:
        conn.close()

    return {
        "ok": True,
        "hasData": bool(candidates),
        "candidates": candidates,
        "count": len(candidates),
        "config": {"minBalance": min_bal, "minMonthsSinceVisit": min_months, "maxRows": cap},
        "dbPath": str(db_path) if db_path else None,
        "emptyNotZero": True,
        "readOnly": True,
        "writeBack": False,
        "softDentWriteBack": False,
        "note": "Board-safe export for Lighthouse import — no NR2 SMS/chat embed.",
        "at": _utc_now(),
    }


def financial_recall_csv(*, candidates: list[dict[str, Any]] | None = None, **kwargs: Any) -> str:
    payload = (
        {"candidates": candidates}
        if candidates is not None
        else financial_recall_candidates(**kwargs)
    )
    rows = list(payload.get("candidates") or [])
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(
        ["initials", "nameHash", "patientHash", "phoneLast4", "balanceBand", "lastVisit", "monthsSinceVisit"]
    )
    for row in rows:
        writer.writerow(
            [
                row.get("initials") or "P—",
                row.get("nameHash") or "——",
                row.get("patientHash") or "——",
                row.get("phoneLast4") or "—",
                row.get("balanceBand") or "—",
                row.get("lastVisit") or "—",
                row.get("monthsSinceVisit") if row.get("monthsSinceVisit") is not None else "",
            ]
        )
    return buffer.getvalue()


def format_financial_recall_hal_reply(query: str = "") -> str:
    _ = query
    result = financial_recall_candidates()
    count = int(result.get("count") or 0)
    cfg = result.get("config") or {}
    lines = [
        "Financial recall export (read-only · board initials+hash · no Lighthouse embed).",
        (
            f"Candidates: {count} · min balance ${cfg.get('minBalance')} · "
            f"min months since visit {cfg.get('minMonthsSinceVisit')}."
        ),
        "GET /api/nr2/financial-recall — JSON · GET /api/nr2/financial-recall/export.csv — staff CSV.",
        "Copy lighthouse_config.yaml.example → lighthouse_config.yaml to tune thresholds locally.",
        "Empty ≠ $0 — phone last-4 only when Sensei/ODBC phone is wired; otherwise —.",
    ]
    if count:
        for row in list(result.get("candidates") or [])[:5]:
            lines.append(
                f"- {row.get('initials')} · #{row.get('patientHash')} · "
                f"{row.get('balanceBand')} · last visit {row.get('lastVisit')}"
            )
        if count > 5:
            lines.append(f"… and {count - 5} more in export.")
    else:
        lines.append("No recall rows match filters yet — check sd_claims + sd_patients last_visit_date.")
    return "\n".join(lines)
