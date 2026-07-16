"""Build SoftDent claims and clinical notes from live daysheet pipeline output."""

from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from import_sync import (
    SAMPLE_PATIENT_MARKERS,
    SOFTDENT_FINANCIAL_EXPORTS,
    _find_newest,
    _is_sample_claims,
    _is_sample_clinical,
    _softdent_direct_read_roots,
)

INSURANCE_WRITEOFF_CODES = frozenset({"51", "52"})
INSURANCE_PAYMENT_CODES = frozenset({"2"})
PATIENT_PAYMENT_CODES = frozenset({"11", "12", "17", "48", "60", "61"})
SKIP_CLINICAL_CODES = frozenset({"2", "11", "12", "17", "48", "60", "61"})
# SoftDent claim statuses that are not active / outstanding (Claims page).
INACTIVE_CLAIM_STATUSES = frozenset(
    {
        "paid",
        "closed",
        "complete",
        "completed",
        "denied",
        "denied-final",
        "done",
        "settled",
        "cancelled",
        "canceled",
        "void",
        "voided",
    }
)
ACCOUNT_NAME_MARKERS = (" account",)


def is_active_claim_status(status: str) -> bool:
    """True when SoftDent claim status is still open / active (not paid/completed)."""
    normalized = str(status or "").strip().lower()
    if not normalized:
        return True
    if normalized in INACTIVE_CLAIM_STATUSES:
        return False
    if normalized.startswith("paid") or normalized.startswith("closed"):
        return False
    if "complete" in normalized:
        return False
    return True


def resolve_daysheet_jsonl_path() -> Path | None:
    candidates: list[Path] = []
    for root in _softdent_direct_read_roots():
        found = _find_newest(root, ("daysheet.jsonl",))
        if found:
            candidates.append(found)
    direct = SOFTDENT_FINANCIAL_EXPORTS / "daysheet.jsonl"
    if direct.is_file():
        candidates.append(direct)
    if not candidates:
        return None
    return max(candidates, key=lambda item: item.stat().st_mtime)


def _parse_report_date(raw: str) -> str:
    text = str(raw or "").strip()
    if not text:
        return ""
    for fmt in ("%B %d, %Y", "%b %d, %Y", "%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    return text


def _money_value(raw: str) -> float | None:
    text = str(raw or "").strip()
    if not text or text in {"-", "—"}:
        return None
    cleaned = text.replace("$", "").replace(",", "").replace("(", "-").replace(")", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def _transaction_amount(cells: list[str], code: str) -> float | None:
    """Resolve production/payment/write-off amount from SoftDent daysheet row cells."""
    production = _money_value(cells[7] if len(cells) > 7 else "")
    if production not in (None, 0):
        return production
    normalized = str(code or "").strip()
    if normalized in INSURANCE_PAYMENT_CODES:
        return _money_value(cells[11] if len(cells) > 11 else "")
    if normalized in INSURANCE_WRITEOFF_CODES:
        writeoff = _money_value(cells[9] if len(cells) > 9 else "")
        return abs(writeoff) if writeoff is not None else None
    fallback = _money_value(cells[11] if len(cells) > 11 else "")
    if fallback not in (None, 0):
        return fallback
    adj = _money_value(cells[9] if len(cells) > 9 else "")
    return abs(adj) if adj is not None else None


def _is_account_name(name: str) -> bool:
    lowered = name.strip().lower()
    return any(marker in lowered for marker in ACCOUNT_NAME_MARKERS)


def _normalize_patient_name(name: str) -> str:
    return re.sub(r"\s+", " ", str(name or "").strip())


def _iter_daysheet_transactions(formatted_rows: list[list[Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    report_date = ""

    for raw in formatted_rows or []:
        cells = [str(cell or "").strip() for cell in raw]
        while len(cells) < 15:
            cells.append("")

        joined = " ".join(part for part in cells if part).strip()
        if not joined:
            continue

        if cells[0] == "Daysheet" or cells[6] == "Daysheet":
            continue
        if cells[1] == "ID" and cells[2] == "Name":
            continue

        maybe_date = _parse_report_date(cells[0]) or _parse_report_date(cells[2]) or _parse_report_date(cells[6])
        if maybe_date and re.search(r"\d{4}", maybe_date):
            report_date = maybe_date
            continue

        patient_id = cells[1]
        patient_name = _normalize_patient_name(cells[2])
        code = cells[5]
        description = cells[6]
        production = _transaction_amount(cells, code)
        transaction_note = cells[14]

        if patient_id and patient_name and not _is_account_name(patient_name):
            if code or description or production not in (None, 0):
                if current:
                    rows.append(current)
                current = {
                    "reportDate": report_date,
                    "patientId": patient_id,
                    "patientName": patient_name,
                    "providerId": cells[4] or "",
                    "code": code,
                    "description": description,
                    "production": production,
                    "transactionNote": transaction_note,
                    "detailLines": [],
                }
                continue

        if current and not patient_id and not patient_name:
            detail = description or transaction_note
            if detail:
                current["detailLines"].append(detail)
            continue

        if current:
            rows.append(current)
            current = None

    if current:
        rows.append(current)
    return rows


_DAYSHEET_TX_CACHE: dict[str, dict[str, Any]] = {}


def _load_daysheet_transactions(path: Path) -> list[dict[str, Any]]:
    """Parse daysheet JSONL once per path+mtime (claims + clinical share the same file)."""
    cache_key = str(path)
    try:
        st = path.stat()
        mtime = float(st.st_mtime)
        size = int(st.st_size)
    except OSError:
        mtime = 0.0
        size = 0
    hit = _DAYSHEET_TX_CACHE.get(cache_key)
    if hit and hit.get("mtime") == mtime and hit.get("size") == size:
        rows = hit.get("rows")
        return rows if isinstance(rows, list) else []

    transactions: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            normalized = payload.get("normalized") if isinstance(payload, dict) else None
            report_date = ""
            if isinstance(normalized, dict):
                report_date = str(normalized.get("report_date") or "").strip()
            raw_row = payload.get("raw_row") if isinstance(payload, dict) else None
            formatted_rows = raw_row.get("formatted_report_rows") if isinstance(raw_row, dict) else None
            if not isinstance(formatted_rows, list):
                continue
            for row in _iter_daysheet_transactions(formatted_rows):
                if report_date and not row.get("reportDate"):
                    row["reportDate"] = report_date
                transactions.append(row)
    _DAYSHEET_TX_CACHE[cache_key] = {"mtime": mtime, "size": size, "rows": transactions}
    return transactions


def _clinical_note_text(row: dict[str, Any]) -> str:
    parts = [str(row.get("description") or "").strip()]
    parts.extend(str(item).strip() for item in row.get("detailLines") or [] if str(item).strip())
    note = str(row.get("transactionNote") or "").strip()
    if note:
        parts.append(note)
    return " ".join(part for part in parts if part).strip()


def build_clinical_notes_rows(transactions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    notes: list[dict[str, Any]] = []
    for idx, row in enumerate(transactions):
        code = str(row.get("code") or "").strip()
        if not code or code in SKIP_CLINICAL_CODES:
            continue
        if code in INSURANCE_WRITEOFF_CODES or code in INSURANCE_PAYMENT_CODES:
            continue
        patient = _normalize_patient_name(str(row.get("patientName") or ""))
        if not patient or patient.lower() in SAMPLE_PATIENT_MARKERS or _is_account_name(patient):
            continue
        note_text = _clinical_note_text(row)
        if not note_text:
            continue
        notes.append(
            {
                "PatientName": patient,
                "MRN": str(row.get("patientId") or ""),
                "NoteDate": str(row.get("reportDate") or ""),
                "Provider": f"Dr {row.get('providerId')}" if row.get("providerId") else "",
                "Procedure": str(row.get("description") or code),
                "ClinicalNote": note_text,
            }
        )
        if len(notes) >= 250:
            break
    return notes


def _code_is_insurance_payment(code: str) -> bool:
    """SoftDent insurance check payment codes only (not ADA 2xxx procedures)."""
    text = str(code or "").strip()
    if not text:
        return False
    base = text.split(".")[0]
    # Exact SoftDent payment family: 2, 2.01, … — never startswith("2") (ADA 2110/2740…).
    return base == "2"


def _code_is_insurance_writeoff(code: str) -> bool:
    text = str(code or "").strip()
    if not text:
        return False
    base = text.split(".")[0]
    return base in INSURANCE_WRITEOFF_CODES


def _account_stem(patient_id: str) -> str:
    """SoftDent account family stem (patient IDs share a prefix within an account)."""
    pid = str(patient_id or "").strip()
    if pid.isdigit() and len(pid) > 4:
        return pid[:-2]
    return pid


def _build_settlement_date_index(transactions: list[dict[str, Any]]) -> dict[str, set[str]]:
    """Account-stem → SoftDent dates with insurance payment or contractual write-off."""
    out: dict[str, set[str]] = {}
    for row in transactions:
        code = str(row.get("code") or "").strip()
        if not (_code_is_insurance_payment(code) or _code_is_insurance_writeoff(code)):
            continue
        report_date = str(row.get("reportDate") or "").strip()
        if not report_date:
            continue
        stem = _account_stem(str(row.get("patientId") or ""))
        if not stem:
            continue
        out.setdefault(stem, set()).add(report_date)
    return out


_TXN_SETTLEMENT_CACHE: dict[str, Any] = {}


def patient_id_from_claim_id(claim_id: str) -> str:
    """Extract SoftDent MRN from TXN-/DS- derived claim ids."""
    parts = str(claim_id or "").strip().split("-")
    if len(parts) >= 3 and parts[0] in ("TXN", "DS"):
        return str(parts[2] or "").strip()
    return ""


def load_txn_settlement_context() -> tuple[list[dict[str, Any]], dict[str, set[str]]]:
    """Cached SoftDent Trans-for-a-Period rows + account settlement index."""
    path = resolve_softdent_transactions_xls_path()
    cache_key = str(path) if path else ""
    try:
        mtime = float(path.stat().st_mtime) if path and path.is_file() else 0.0
    except OSError:
        mtime = 0.0
    hit = _TXN_SETTLEMENT_CACHE.get(cache_key)
    if hit and hit.get("mtime") == mtime:
        txs = hit.get("transactions")
        idx = hit.get("index")
        if isinstance(txs, list) and isinstance(idx, dict):
            return txs, idx
    transactions = load_softdent_transactions_xls(path)
    index = _build_settlement_date_index(transactions)
    _TXN_SETTLEMENT_CACHE[cache_key] = {
        "mtime": mtime,
        "transactions": transactions,
        "index": index,
    }
    return transactions, index


def claim_is_unpaid_on_txn(
    *,
    patient_id: str = "",
    service_date: str = "",
    claim_id: str = "",
    claim_status: str = "",
    transactions: list[dict[str, Any]] | None = None,
    settlement_index: dict[str, set[str]] | None = None,
) -> bool:
    """True when SoftDent TXN ledger still shows no insurance pay/write-off on/after DOS."""
    if claim_status and not is_active_claim_status(claim_status):
        return False
    pid = str(patient_id or "").strip() or patient_id_from_claim_id(claim_id)
    dos = str(service_date or "").strip()[:10]
    if not pid or not dos:
        return True
    txs = transactions
    idx = settlement_index
    if txs is None or idx is None:
        txs, idx = load_txn_settlement_context()
    if not txs:
        return True
    status = _claim_status_for_patient_day(pid, dos, txs, settlement_index=idx)
    return is_active_claim_status(status)


def _claim_status_for_patient_day(
    patient_id: str,
    report_date: str,
    transactions: list[dict[str, Any]],
    *,
    settlement_index: dict[str, set[str]] | None = None,
) -> str:
    """Active vs settled for SoftDent patient+DOS (Paid/Denied are not unpaid/active)."""
    same_day = [
        row
        for row in transactions
        if str(row.get("patientId") or "") == patient_id and str(row.get("reportDate") or "") == report_date
    ]
    codes = {str(row.get("code") or "").strip() for row in same_day}
    if any(_code_is_insurance_payment(c) for c in codes):
        return "Paid"
    if any(_code_is_insurance_writeoff(c) for c in codes):
        return "Denied"
    index = settlement_index
    if index is None:
        index = _build_settlement_date_index(transactions)
    stem = _account_stem(patient_id)
    for settle_date in index.get(stem, ()):
        if settle_date >= report_date:
            # SoftDent insurance pay or write-off on/after DOS ⇒ claim is paid/completed.
            return "Paid"
    return "Pending Review"


@lru_cache(maxsize=1)
def _sd_claims_payer_index() -> dict[str, str]:
    """Best-effort patient/date → real Payer from sd_claims when ODBC/CSV populated it."""
    try:
        from softdent_odbc_extract import resolve_sd_sqlite_db
    except ImportError:
        return {}
    db_path = resolve_sd_sqlite_db()
    if not db_path or not Path(db_path).is_file():
        return {}
    out: dict[str, str] = {}
    try:
        conn = sqlite3.connect(str(db_path))
        try:
            cur = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='sd_claims'"
            )
            if not cur.fetchone():
                return {}
            rows = conn.execute(
                "SELECT patient_name, service_date, payer FROM sd_claims "
                "WHERE payer IS NOT NULL AND TRIM(payer) != ''"
            ).fetchall()
        finally:
            conn.close()
    except sqlite3.Error:
        return {}
    for patient_name, service_date, payer in rows:
        label = str(payer or "").strip()
        if not label or label.lower() in {"insurance", "unknown", "n/a", "-"}:
            continue
        name_key = _normalize_patient_name(str(patient_name or "")).casefold()
        date_key = str(service_date or "").strip()[:10]
        if name_key:
            out.setdefault(f"name|{name_key}", label)
        if name_key and date_key:
            out[f"name_date|{name_key}|{date_key}"] = label
    return out


def _resolve_claim_payer(patient_name: str, report_date: str) -> str:
    """Prefer a named payer from sd_claims; daysheet alone has no carrier column."""
    index = _sd_claims_payer_index()
    if not index:
        return "Insurance"
    name_key = _normalize_patient_name(patient_name).casefold()
    date_key = str(report_date or "").strip()[:10]
    if name_key and date_key:
        hit = index.get(f"name_date|{name_key}|{date_key}")
        if hit:
            return hit
    if name_key:
        hit = index.get(f"name|{name_key}")
        if hit:
            return hit
    return "Insurance"


def build_claims_rows(
    transactions: list[dict[str, Any]],
    *,
    claim_id_prefix: str = "DS",
    awaiting_reason: str = "Awaiting insurance response.",
    unpaid_only: bool = True,
) -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []
    seen: set[str] = set()
    prefix = str(claim_id_prefix or "DS").strip().upper() or "DS"
    settlement_index = _build_settlement_date_index(transactions)
    for idx, row in enumerate(transactions):
        code = str(row.get("code") or "").strip()
        if not code or code in INSURANCE_PAYMENT_CODES or code in INSURANCE_WRITEOFF_CODES:
            continue
        if code in SKIP_CLINICAL_CODES:
            continue
        # Never treat SoftDent ADA 2xxx as insurance payment codes here.
        base = code.split(".")[0]
        if base in INSURANCE_PAYMENT_CODES or base in INSURANCE_WRITEOFF_CODES:
            continue
        production = row.get("production")
        if production in (None, 0):
            continue
        patient = _normalize_patient_name(str(row.get("patientName") or ""))
        patient_id = str(row.get("patientId") or "")
        report_date = str(row.get("reportDate") or "")
        if not patient or not patient_id or not report_date:
            continue
        if patient.lower() in SAMPLE_PATIENT_MARKERS or _is_account_name(patient):
            continue
        claim_key = f"{patient_id}|{report_date}|{code}|{row.get('description') or ''}"
        if claim_key in seen:
            continue
        seen.add(claim_key)
        status = _claim_status_for_patient_day(
            patient_id,
            report_date,
            transactions,
            settlement_index=settlement_index,
        )
        if unpaid_only and not is_active_claim_status(status):
            continue
        claim_id = f"{prefix}-{report_date.replace('-', '')}-{patient_id}-{code}-{idx + 1}"
        claims.append(
            {
                "PatientName": patient,
                "MRN": patient_id,
                "ClaimId": claim_id,
                "ClaimStatus": status,
                "Payer": _resolve_claim_payer(patient, report_date),
                "Procedure": str(row.get("description") or code),
                "ServiceDate": report_date,
                "DenialReason": "Derived from SoftDent insurance activity."
                if status == "Denied"
                else ("Insurance payment posted." if status == "Paid" else awaiting_reason),
                "ClaimAmount": f"{float(production):.2f}",
            }
        )
        # SoftDent outstanding claims can exceed a single daysheet; do not cap
        # derived rows at 150 (that falsely froze the Claims page near ~60).
    return claims


def resolve_softdent_transactions_xls_path() -> Path | None:
    """Newest SoftDent Trans-for-a-Period Excel under report/export roots."""
    patterns = (
        "transactions_for_period*.xls",
        "transactions_for_period*.xlsx",
        "TXN*.XLS",
        "TXN*.xls",
    )
    candidates: list[Path] = []
    roots = list(_softdent_direct_read_roots())
    report_root = Path(r"C:\SoftDentReportExports")
    if report_root.is_dir():
        roots.append(report_root)
    for root in roots:
        if not root.is_dir():
            continue
        for pattern in patterns:
            try:
                candidates.extend(p for p in root.glob(pattern) if p.is_file())
            except OSError:
                continue
    if not candidates:
        return None
    return max(candidates, key=lambda item: item.stat().st_mtime)


def _code_token(raw: Any) -> str:
    text = str(raw or "").strip()
    if not text:
        return ""
    try:
        value = float(text)
        if abs(value - int(value)) < 1e-9:
            return str(int(value))
        return f"{value:.2f}".rstrip("0").rstrip(".")
    except ValueError:
        return text


def load_softdent_transactions_xls(path: Path | None = None) -> list[dict[str, Any]]:
    """Load SoftDent Trans-for-a-Period Excel into daysheet-shaped transaction rows."""
    path = path or resolve_softdent_transactions_xls_path()
    if not path or not path.is_file():
        return []
    try:
        import xlrd
    except ImportError:
        return []
    try:
        book = xlrd.open_workbook(str(path))
        sheet = book.sheet_by_index(0)
    except Exception:
        return []

    header_row = None
    for row_idx in range(min(40, sheet.nrows)):
        labels = [str(sheet.cell_value(row_idx, col) or "").strip().lower() for col in range(min(16, sheet.ncols))]
        if "date" in labels and "code" in labels and any(label in {"prod", "name", "id"} for label in labels):
            header_row = row_idx
            break
    if header_row is None:
        return []

    rows: list[dict[str, Any]] = []
    for row_idx in range(header_row + 1, sheet.nrows):
        date_cell = sheet.cell_value(row_idx, 0)
        if date_cell in ("", None):
            continue
        if isinstance(date_cell, (int, float)):
            try:
                report_date = datetime(*xlrd.xldate_as_tuple(float(date_cell), book.datemode)).date().isoformat()
            except Exception:
                continue
        else:
            report_date = _parse_report_date(str(date_cell))
            if not report_date:
                continue
        try:
            patient_id = str(int(float(sheet.cell_value(row_idx, 1))))
        except (TypeError, ValueError):
            patient_id = str(sheet.cell_value(row_idx, 1) or "").strip()
        patient_name = _normalize_patient_name(str(sheet.cell_value(row_idx, 2) or ""))
        provider = sheet.cell_value(row_idx, 4)
        try:
            provider_id = str(int(float(provider))) if provider not in ("", None) else ""
        except (TypeError, ValueError):
            provider_id = str(provider or "").strip()
        code = _code_token(sheet.cell_value(row_idx, 5))
        production_raw = sheet.cell_value(row_idx, 7)
        try:
            production = float(production_raw) if production_raw not in ("", None) else None
        except (TypeError, ValueError):
            production = None
        if not patient_id or not patient_name:
            continue
        rows.append(
            {
                "reportDate": report_date,
                "patientId": patient_id,
                "patientName": patient_name,
                "providerId": provider_id,
                "code": code,
                "description": code,
                "production": production,
                "detailLines": [],
                "transactionNote": "",
            }
        )
    return rows


def build_transactions_claims_dataset(path: Path | None = None) -> dict[str, Any] | None:
    """SoftDent Trans-for-a-Period Excel → open claims (broader than single-day daysheet).

    SoftDent Outstanding Claims by Patient has Excel greyed on this office build, so NR2
    rebuilds an open-claim working set from SoftDent desktop Trans-for-a-Period Excel:
    one row per patient+service-date with production and no same-day insurance pay/write-off.
    """
    path = path or resolve_softdent_transactions_xls_path()
    if not path or not path.is_file():
        return None
    transactions = load_softdent_transactions_xls(path)
    if not transactions:
        return None
    line_rows = build_claims_rows(
        transactions,
        claim_id_prefix="TXN",
        unpaid_only=True,
        awaiting_reason=(
            "SoftDent Trans-for-a-Period: production with no SoftDent insurance "
            "payment/write-off on or after DOS (Outstanding Claims Excel greyed)."
        ),
    )
    # Roll up procedure lines → SoftDent-like claim batches (patient + DOS).
    # Active only — drop Paid / Completed / Denied / Closed.
    buckets: dict[str, dict[str, Any]] = {}
    for row in line_rows:
        status = str(row.get("ClaimStatus") or "").strip()
        if not is_active_claim_status(status):
            continue
        patient_id = str(row.get("MRN") or "").strip()
        service_date = str(row.get("ServiceDate") or "").strip()
        if not patient_id or not service_date:
            continue
        key = f"{patient_id}|{service_date}"
        amount = 0.0
        try:
            amount = float(str(row.get("ClaimAmount") or "0").replace(",", "").replace("$", ""))
        except ValueError:
            amount = 0.0
        hit = buckets.get(key)
        if not hit:
            buckets[key] = {
                "PatientName": row.get("PatientName") or "",
                "MRN": patient_id,
                "ClaimId": f"TXN-{service_date.replace('-', '')}-{patient_id}",
                "ClaimStatus": "Pending Review",
                "Payer": row.get("Payer") or "Insurance",
                "Procedure": str(row.get("Procedure") or ""),
                "ServiceDate": service_date,
                "DenialReason": row.get("DenialReason") or "",
                "ClaimAmount": amount,
                "_codes": [str(row.get("Procedure") or "")],
            }
            continue
        hit["ClaimAmount"] = float(hit.get("ClaimAmount") or 0) + amount
        code = str(row.get("Procedure") or "").strip()
        if code and code not in hit["_codes"]:
            hit["_codes"].append(code)

    open_rows: list[dict[str, Any]] = []
    for hit in buckets.values():
        if not is_active_claim_status(str(hit.get("ClaimStatus") or "")):
            continue
        codes = [c for c in (hit.pop("_codes", []) or []) if c]
        if codes:
            hit["Procedure"] = ", ".join(codes[:8]) + ("…" if len(codes) > 8 else "")
        hit["ClaimAmount"] = f"{float(hit.get('ClaimAmount') or 0):.2f}"
        hit["ClaimStatus"] = "Pending Review"
        open_rows.append(hit)
    open_rows.sort(key=lambda item: (str(item.get("ServiceDate") or ""), str(item.get("PatientName") or "")))
    if not open_rows or _is_sample_claims(open_rows):
        return None
    return {
        "sourceFile": "softdent_claims_export.csv",
        "sourcePath": str(path),
        "modifiedAt": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(),
        "rows": open_rows,
        "readSource": "direct",
        "sourceKind": "pipeline-softdent-transactions",
        "transactionCount": len(transactions),
        "lineClaimCount": len(line_rows),
        "honesty": (
            "SoftDent desktop Trans-for-a-Period Excel estimate — not SoftDent "
            "Outstanding Claims by Patient (Excel greyed on that report)."
        ),
    }


def build_procedures_rows(transactions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    procedures: list[dict[str, Any]] = []
    for row in transactions:
        code = str(row.get("code") or "").strip()
        if not code or code in INSURANCE_PAYMENT_CODES or code in INSURANCE_WRITEOFF_CODES:
            continue
        if code in SKIP_CLINICAL_CODES:
            continue
        production = row.get("production")
        if production in (None, 0):
            continue
        patient = _normalize_patient_name(str(row.get("patientName") or ""))
        patient_id = str(row.get("patientId") or "")
        report_date = str(row.get("reportDate") or "")
        if not patient_id or not report_date:
            continue
        if patient.lower() in SAMPLE_PATIENT_MARKERS or _is_account_name(patient):
            continue
        procedures.append(
            {
                "PatientName": patient,
                "MRN": patient_id,
                "Date": report_date,
                "Code": code,
                "Tooth": str(row.get("tooth") or ""),
                "Surface": str(row.get("surface") or ""),
                "Description": str(row.get("description") or code),
                "Provider": str(row.get("providerId") or ""),
                "Production": f"{float(production):.2f}",
            }
        )
        if len(procedures) >= 500:
            break
    return procedures


def build_daysheet_procedures_dataset(path: Path | None = None) -> dict[str, Any] | None:
    path = path or resolve_daysheet_jsonl_path()
    if not path or not path.is_file():
        return None
    rows = build_procedures_rows(_load_daysheet_transactions(path))
    if not rows:
        return None
    return {
        "sourceFile": "softdent_procedures_export.csv",
        "sourcePath": str(path),
        "modifiedAt": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(),
        "rows": rows,
        "readSource": "direct",
        "sourceKind": "pipeline-daysheet",
    }


def build_daysheet_clinical_dataset(path: Path | None = None) -> dict[str, Any] | None:
    path = path or resolve_daysheet_jsonl_path()
    if not path or not path.is_file():
        return None
    rows = build_clinical_notes_rows(_load_daysheet_transactions(path))
    if not rows or _is_sample_clinical(rows):
        return None
    return {
        "sourceFile": "softdent_clinical_notes_data.json",
        "sourcePath": str(path),
        "modifiedAt": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(),
        "rows": rows,
        "readSource": "direct",
        "sourceKind": "pipeline-daysheet",
    }


def build_daysheet_claim_status_dataset(path: Path | None = None) -> dict[str, Any] | None:
    path = path or resolve_daysheet_jsonl_path()
    if not path or not path.is_file():
        return None
    rows = build_claims_rows(_load_daysheet_transactions(path))
    if not rows or _is_sample_claims(rows):
        return None
    status_rows = [
        {
            "ClaimId": row.get("ClaimId"),
            "Status": row.get("ClaimStatus"),
            "Payer": row.get("Payer"),
            "ServiceDate": row.get("ServiceDate"),
            "Amount": row.get("ClaimAmount"),
            "DenialReason": row.get("DenialReason"),
            "PatientName": row.get("PatientName"),
            "Procedure": row.get("Procedure"),
        }
        for row in rows
    ]
    return {
        "sourceFile": "softdent_claim_status_export.csv",
        "sourcePath": str(path),
        "modifiedAt": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(),
        "rows": status_rows,
        "readSource": "direct",
        "sourceKind": "pipeline-daysheet",
    }


def build_daysheet_claims_dataset(path: Path | None = None) -> dict[str, Any] | None:
    path = path or resolve_daysheet_jsonl_path()
    if not path or not path.is_file():
        return None
    rows = build_claims_rows(_load_daysheet_transactions(path))
    if not rows or _is_sample_claims(rows):
        return None
    return {
        "sourceFile": "softdent_claims_export.csv",
        "sourcePath": str(path),
        "modifiedAt": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(),
        "rows": rows,
        "readSource": "direct",
        "sourceKind": "pipeline-daysheet",
    }
