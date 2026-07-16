"""NR2-12150 — Hide paid claims from Claims page outstanding list.

Cascade (SoftDent READ-ONLY; empty ≠ $0 — never invent paid):
  1) TXN Trans-for-a-Period insurance pay / write-off
  2) ERA-835 paid segments (explicit paid > 0 only)
  3) SoftDent Claims Aging Excel pending list (only when non-empty export exists)
  4) Staff-verified-paid local hide (no SoftDent write-back)

Absence of ERA/Aging evidence is NOT treated as paid.
"""

from __future__ import annotations

import csv
import json
import os
import re
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
OPS_DIR = REPO_ROOT / "app_data" / "nr2" / "ops"
STAFF_HIDE_PATH = OPS_DIR / "claims_staff_verified_paid.jsonl"
DEFAULT_EXPORTS = Path(r"C:\SoftDentReportExports")
DEFAULT_FINANCIAL = Path(r"C:\SoftDentFinancialExports")

_ERA_PAID_STATUSES = frozenset({"1", "2", "3", "19", "25"})


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _ensure_ops() -> None:
    OPS_DIR.mkdir(parents=True, exist_ok=True)


def _parse_money(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    raw = str(value).replace("$", "").replace(",", "").replace("(", "-").replace(")", "").strip()
    if not raw or raw in {".", "-", "—"}:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _norm_name(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", " ", str(value or "").strip().lower())
    return re.sub(r"\s+", " ", text).strip()


def _norm_date(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if len(text) >= 10 and text[4] == "-" and text[7] == "-":
        return text[:10]
    for fmt in ("%Y%m%d", "%m/%d/%Y", "%m/%d/%y", "%Y/%m/%d", "%m-%d-%Y"):
        try:
            return datetime.strptime(text[:10] if fmt != "%Y%m%d" else text[:8], fmt).date().isoformat()
        except ValueError:
            continue
    return text[:10]


def _amount_key(amount: Any) -> str:
    money = _parse_money(amount)
    if money is None:
        return ""
    return f"{round(money, 2):.2f}"


def _tuple_key(patient_name: str, service_date: str, amount: Any) -> str:
    name = _norm_name(patient_name)
    dos = _norm_date(service_date)
    amt = _amount_key(amount)
    if not name or not dos or not amt:
        return ""
    return f"{name}|{dos}|{amt}"


# --- Staff verified paid (local hide) ---------------------------------


def staff_verified_paid_path() -> Path:
    env = str(os.environ.get("NR2_CLAIMS_STAFF_HIDE") or "").strip()
    if env:
        return Path(env).expanduser()
    return STAFF_HIDE_PATH


def load_staff_verified_paid_ids() -> set[str]:
    path = staff_verified_paid_path()
    if not path.is_file():
        return set()
    out: set[str] = set()
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(row, dict):
                continue
            if row.get("undone"):
                continue
            cid = str(row.get("claimId") or row.get("claim_id") or "").strip()
            if cid:
                out.add(cid)
    except OSError:
        return set()
    return out


def claim_is_unpaid_per_staff(
    *,
    claim_id: str = "",
    staff_ids: set[str] | None = None,
) -> bool:
    """False when staff locally verified paid (hide from outstanding)."""
    cid = str(claim_id or "").strip()
    if not cid:
        return True
    ids = staff_ids if staff_ids is not None else load_staff_verified_paid_ids()
    return cid not in ids


def mark_staff_verified_paid(
    *,
    claim_id: str,
    patient_id: str = "",
    patient_name: str = "",
    service_date: str = "",
    amount: Any = None,
    actor: str = "Staff",
    note: str = "",
) -> dict[str, Any]:
    """Append local staff-verified-paid hide (no SoftDent write-back)."""
    cid = str(claim_id or "").strip()
    if not cid:
        return {"ok": False, "error": "claim_id_required", "writeBack": False}
    _ensure_ops()
    path = staff_verified_paid_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "at": _utc_now(),
        "claimId": cid,
        "patientId": str(patient_id or "").strip(),
        "patientName": str(patient_name or "").strip(),
        "serviceDate": _norm_date(service_date),
        "amount": _parse_money(amount),
        "actor": str(actor or "Staff").strip()[:80] or "Staff",
        "note": str(note or "").strip()[:500],
        "writeBack": False,
        "softDentWriteBack": False,
        "emptyNotZero": True,
        "reason": "staff_verified_paid",
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, default=str) + "\n")
    return {
        "ok": True,
        "claimId": cid,
        "hidden": True,
        "entry": entry,
        "writeBack": False,
        "softDentWriteBack": False,
        "honesty": "empty != $0; SoftDent READ-ONLY; local hide only",
    }


# --- ERA paid keys ----------------------------------------------------


def _era_file_candidates() -> list[Path]:
    files: list[Path] = []
    try:
        from nr2_era_inbox import _processed_dir, era_inbox_roots

        roots = list(era_inbox_roots()) + [_processed_dir()]
    except Exception:
        roots = [
            Path(r"C:\SoftDentReportExports\era"),
            Path(r"C:\SoftDentFinancialExports\era"),
            REPO_ROOT / "app_data" / "nr2" / "office" / "era_inbox" / "drop",
            REPO_ROOT / "app_data" / "nr2" / "office" / "era_inbox" / "processed",
        ]
    for root in roots:
        if not root or not Path(root).is_dir():
            continue
        try:
            for path in Path(root).iterdir():
                if not path.is_file():
                    continue
                name = path.name.lower()
                if name.endswith((".835", ".edi", ".txt")) or "era" in name:
                    files.append(path)
        except OSError:
            continue
    return files


@lru_cache(maxsize=1)
def _era_paid_index_cached(mtime_sig: str) -> dict[str, Any]:
    _ = mtime_sig
    claim_ids: set[str] = set()
    tuples: set[str] = set()
    segment_count = 0
    paid_segment_count = 0
    try:
        from era835_parser import parse_835_text
    except Exception:
        return {
            "claimIds": claim_ids,
            "tuples": tuples,
            "segmentCount": 0,
            "paidSegmentCount": 0,
            "active": False,
        }
    for path in _era_file_candidates():
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if not text.strip():
            continue
        try:
            parsed = parse_835_text(text)
        except Exception:
            continue
        for seg in parsed.get("segments") or []:
            if not isinstance(seg, dict):
                continue
            segment_count += 1
            paid = _parse_money(seg.get("paid"))
            status = str(seg.get("status") or "").strip()
            # Explicit payment only — empty/missing paid ≠ $0 and does not suppress.
            if paid is None or paid <= 0:
                continue
            if status and status not in _ERA_PAID_STATUSES and status in {"4", "22", "23"}:
                continue
            paid_segment_count += 1
            cid = str(seg.get("claimId") or "").strip()
            if cid:
                claim_ids.add(cid)
                claim_ids.add(cid.upper())
            tkey = _tuple_key(
                str(seg.get("patientName") or ""),
                str(seg.get("serviceDate") or ""),
                paid,
            )
            if tkey:
                tuples.add(tkey)
            # Also index by charged amount when present (claim billed vs paid).
            charged = _parse_money(seg.get("charged"))
            if charged is not None and charged > 0:
                t2 = _tuple_key(
                    str(seg.get("patientName") or ""),
                    str(seg.get("serviceDate") or ""),
                    charged,
                )
                if t2:
                    tuples.add(t2)
    return {
        "claimIds": claim_ids,
        "tuples": tuples,
        "segmentCount": segment_count,
        "paidSegmentCount": paid_segment_count,
        "active": paid_segment_count > 0,
    }


def load_era_paid_index() -> dict[str, Any]:
    files = _era_file_candidates()
    sig_parts = []
    for path in sorted(files, key=lambda p: str(p).lower())[:80]:
        try:
            st = path.stat()
            sig_parts.append(f"{path}:{int(st.st_mtime)}:{int(st.st_size)}")
        except OSError:
            continue
    return _era_paid_index_cached("|".join(sig_parts))


def claim_is_unpaid_per_era(
    *,
    claim_id: str = "",
    patient_name: str = "",
    service_date: str = "",
    amount: Any = None,
    era_index: dict[str, Any] | None = None,
) -> bool:
    """False when ERA shows explicit paid > 0 for this claim/tuple."""
    idx = era_index if isinstance(era_index, dict) else load_era_paid_index()
    if not idx.get("active"):
        return True
    cid = str(claim_id or "").strip()
    claim_ids = idx.get("claimIds") or set()
    if cid and (cid in claim_ids or cid.upper() in claim_ids):
        return False
    tkey = _tuple_key(patient_name, service_date, amount)
    tuples = idx.get("tuples") or set()
    if tkey and tkey in tuples:
        return False
    return True


def paid_claim_keys_from_era() -> dict[str, Any]:
    idx = load_era_paid_index()
    return {
        "ok": True,
        "active": bool(idx.get("active")),
        "claimIds": sorted(idx.get("claimIds") or []),
        "tupleCount": len(idx.get("tuples") or []),
        "segmentCount": int(idx.get("segmentCount") or 0),
        "paidSegmentCount": int(idx.get("paidSegmentCount") or 0),
        "emptyNotZero": True,
        "writeBack": False,
    }


# --- Claims Aging Excel -----------------------------------------------


def find_claims_aging_export(*, roots: list[Path] | None = None) -> Path | None:
    """Locate SoftDent Claims Aging / Outstanding Claims-by-patient Excel."""
    search_roots = roots or [DEFAULT_EXPORTS, DEFAULT_FINANCIAL]
    try:
        from import_loader import softdent_import_dir

        search_roots.append(softdent_import_dir())
    except Exception:
        pass
    # Explicit Claims Aging / Outstanding-by-Patient only.
    # Never use softdent_claims_export.csv (sd_claims ingest source) — absence
    # there must not invent "paid".
    patterns = (
        "claims_aging*.xls",
        "claims_aging*.xlsx",
        "claims_aging*.csv",
        "outstanding_claims_by_patient*.xls",
        "outstanding_claims_by_patient*.xlsx",
        "outstanding_claims_by_patient*.csv",
        "*Claims*Aging*.xls",
        "*Claims*Aging*.xlsx",
        "*Claims*Aging*.csv",
    )
    # Never confuse Account Aging totals or claims ingest CSV with Claims Aging.
    skip = {
        "account_aging.csv",
        "account_aging.xls",
        "account_aging.xlsx",
        "softdent_ar_aging.csv",
        "softdent_ar_aging.jsonl",
        "softdent_claims_export.csv",
    }
    found: list[Path] = []
    for root in search_roots:
        if not root or not Path(root).is_dir():
            continue
        root_p = Path(root)
        for pat in patterns:
            try:
                for path in root_p.glob(pat):
                    if path.is_file() and path.name.lower() not in skip:
                        found.append(path)
            except OSError:
                continue
    if not found:
        return None
    return max(found, key=lambda p: p.stat().st_mtime)


def _sheet_rows_from_path(path: Path) -> list[list[str]]:
    suffix = path.suffix.lower()
    if suffix in {".csv", ".txt"}:
        try:
            text = path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            return []
        return [[str(c).strip() for c in row] for row in csv.reader(text.splitlines())]
    try:
        import xlrd
    except ImportError:
        # Fallback: SoftDent sometimes writes HTML-as-xls / tab text.
        try:
            text = path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            return []
        if "<table" in text.lower():
            cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", text, flags=re.I | re.S)
            # Best-effort: not used unless header heuristics succeed downstream.
            return [[re.sub(r"<[^>]+>", "", c).strip() for c in cells]]
        return [[str(c).strip() for c in row] for row in csv.reader(text.splitlines())]
    try:
        book = xlrd.open_workbook(str(path))
        sheet = book.sheet_by_index(0)
    except Exception:
        return []
    rows: list[list[str]] = []
    for r in range(sheet.nrows):
        cells: list[str] = []
        for c in range(sheet.ncols):
            val = sheet.cell_value(r, c)
            if isinstance(val, float):
                try:
                    if abs(val - int(val)) < 1e-9:
                        cells.append(str(int(val)))
                    else:
                        cells.append(str(val))
                except Exception:
                    cells.append(str(val))
            else:
                cells.append(str(val or "").strip())
        rows.append(cells)
    return rows


def parse_claims_aging_export(path: Path | str) -> dict[str, Any]:
    """Parse SoftDent Claims Aging / outstanding-by-patient into pending keys.

    empty ≠ $0: missing/unparseable file → ok=False, active=False (do not suppress).
    """
    target = Path(path)
    result: dict[str, Any] = {
        "ok": False,
        "active": False,
        "path": str(target),
        "sourceKind": "claims_aging",
        "rowCount": 0,
        "claimIds": [],
        "tuples": [],
        "honesty": "empty != $0",
    }
    if not target.is_file():
        result["error"] = "missing"
        return result
    rows = _sheet_rows_from_path(target)
    if not rows:
        result["error"] = "empty_or_unreadable"
        return result

    header_idx = None
    header_map: dict[str, int] = {}
    for i, row in enumerate(rows[:60]):
        labels = [str(c or "").strip().lower() for c in row]
        joined = " ".join(labels)
        has_patient = any("patient" in x or x == "name" for x in labels)
        has_amount = any(
            x in {"amount", "claim amount", "bal", "balance", "ins amt", "fee"} or "amount" in x
            for x in labels
        )
        has_date = any(
            x in {"date", "dos", "service date", "svc date"} or "date" in x for x in labels
        )
        has_claim = any("claim" in x for x in labels)
        if (has_patient and has_amount and has_date) or (has_claim and has_amount):
            header_idx = i
            for col, label in enumerate(labels):
                if label:
                    header_map[label] = col
            break
    if header_idx is None:
        result["error"] = "header_not_found"
        return result

    def _col(*names: str) -> int | None:
        for name in names:
            if name in header_map:
                return header_map[name]
            for key, idx in header_map.items():
                if name in key:
                    return idx
        return None

    i_claim = _col("claim #", "claim id", "claim no", "claim number", "claim")
    i_patient = _col("patient", "patient name", "name", "acct name")
    i_date = _col("service date", "svc date", "dos", "date")
    i_amount = _col("claim amount", "amount", "balance", "ins amt", "fee", "charges")

    claim_ids: set[str] = set()
    tuples: set[str] = set()
    for row in rows[header_idx + 1 :]:
        if not row or all(not str(c).strip() for c in row):
            continue
        def _cell(idx: int | None) -> str:
            if idx is None or idx >= len(row):
                return ""
            return str(row[idx] or "").strip()

        cid = _cell(i_claim)
        patient = _cell(i_patient)
        dos = _norm_date(_cell(i_date))
        amount = _parse_money(_cell(i_amount))
        # Skip footer/total lines
        low = " ".join(str(c).lower() for c in row)
        if "total" in low and not patient and not cid:
            continue
        if amount is None or amount <= 0:
            continue
        if cid:
            claim_ids.add(cid)
            claim_ids.add(cid.upper())
        tkey = _tuple_key(patient, dos, amount)
        if tkey:
            tuples.add(tkey)
    result["rowCount"] = len(tuples) + len(claim_ids)
    result["claimIds"] = sorted(claim_ids)
    result["tuples"] = sorted(tuples)
    result["ok"] = bool(tuples or claim_ids)
    result["active"] = bool(tuples or claim_ids)
    if not result["active"]:
        result["error"] = "no_pending_rows"
    return result


@lru_cache(maxsize=4)
def _claims_aging_index_cached(path_sig: str) -> dict[str, Any]:
    if not path_sig or "|" not in path_sig:
        return {"active": False, "claimIds": set(), "tuples": set(), "path": None, "rowCount": 0}
    path_str, _mtime = path_sig.split("|", 1)
    parsed = parse_claims_aging_export(path_str)
    return {
        "active": bool(parsed.get("active")),
        "claimIds": set(parsed.get("claimIds") or []),
        "tuples": set(parsed.get("tuples") or []),
        "path": parsed.get("path"),
        "rowCount": int(parsed.get("rowCount") or 0),
        "ok": bool(parsed.get("ok")),
        "error": parsed.get("error"),
    }


def load_claims_aging_index() -> dict[str, Any]:
    path = find_claims_aging_export()
    if not path:
        return {"active": False, "claimIds": set(), "tuples": set(), "path": None, "rowCount": 0}
    try:
        mtime = int(path.stat().st_mtime)
    except OSError:
        mtime = 0
    return _claims_aging_index_cached(f"{path}|{mtime}")


def claim_is_unpaid_per_aging(
    *,
    claim_id: str = "",
    patient_name: str = "",
    service_date: str = "",
    amount: Any = None,
    aging_index: dict[str, Any] | None = None,
) -> bool:
    """False when Claims Aging export is active and claim is absent from pending list.

    If aging export is missing/empty → True (keep; do not invent paid).
    """
    idx = aging_index if isinstance(aging_index, dict) else load_claims_aging_index()
    if not idx.get("active"):
        return True
    cid = str(claim_id or "").strip()
    claim_ids = idx.get("claimIds") or set()
    tuples = idx.get("tuples") or set()
    if cid and (cid in claim_ids or cid.upper() in claim_ids):
        return True
    tkey = _tuple_key(patient_name, service_date, amount)
    if tkey and tkey in tuples:
        return True
    # Active aging list and no match ⇒ SoftDent no longer shows as pending.
    if cid or tkey:
        return False
    return True


# --- Cascade orchestrator ---------------------------------------------


def claim_is_still_outstanding(
    *,
    claim_id: str = "",
    patient_id: str = "",
    patient_name: str = "",
    service_date: str = "",
    amount: Any = None,
    claim_status: str = "",
    transactions: list[dict[str, Any]] | None = None,
    settlement_index: dict[str, set[str]] | None = None,
    era_index: dict[str, Any] | None = None,
    aging_index: dict[str, Any] | None = None,
    staff_ids: set[str] | None = None,
) -> tuple[bool, str]:
    """Return (keep_on_list, evidence). evidence is still_waiting or suppress reason."""
    try:
        from softdent_operational_pipeline import claim_is_unpaid_on_txn
    except Exception:
        claim_is_unpaid_on_txn = None  # type: ignore[assignment]

    if claim_is_unpaid_on_txn is not None:
        unpaid_txn = claim_is_unpaid_on_txn(
            patient_id=patient_id,
            service_date=service_date,
            claim_id=claim_id,
            claim_status=claim_status,
            transactions=transactions,
            settlement_index=settlement_index,
        )
        if not unpaid_txn:
            return False, "txn"

    if not claim_is_unpaid_per_era(
        claim_id=claim_id,
        patient_name=patient_name,
        service_date=service_date,
        amount=amount,
        era_index=era_index,
    ):
        return False, "era"

    if not claim_is_unpaid_per_aging(
        claim_id=claim_id,
        patient_name=patient_name,
        service_date=service_date,
        amount=amount,
        aging_index=aging_index,
    ):
        return False, "aging"

    if not claim_is_unpaid_per_staff(claim_id=claim_id, staff_ids=staff_ids):
        return False, "staff"

    return True, "still_waiting"


def load_suppress_context() -> dict[str, Any]:
    """Load ERA/Aging/Staff indexes once per claims_outstanding call."""
    era = load_era_paid_index()
    aging = load_claims_aging_index()
    staff = load_staff_verified_paid_ids()
    txn_date_max = None
    txn_path = None
    try:
        from softdent_operational_pipeline import (
            load_txn_settlement_context,
            resolve_softdent_transactions_xls_path,
        )

        txn_path_obj = resolve_softdent_transactions_xls_path()
        txn_path = str(txn_path_obj) if txn_path_obj else None
        txs, _idx = load_txn_settlement_context()
        dates = sorted(
            {str(r.get("reportDate") or "")[:10] for r in txs if r.get("reportDate")}
        )
        txn_date_max = dates[-1] if dates else None
    except Exception:
        pass
    return {
        "era": era,
        "aging": aging,
        "staffIds": staff,
        "txnPath": txn_path,
        "txnDateMax": txn_date_max,
    }
