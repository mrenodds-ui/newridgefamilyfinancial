"""SoftDent daily operational widgets from sd_* tables (hal-10071)."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Any

from softdent_practice_exports import NEW_PATIENT_PROCEDURE_CODES
from softdent_odbc_extract import resolve_sd_sqlite_db, table_row_counts

NEW_PATIENT_CODES = NEW_PATIENT_PROCEDURE_CODES


def _utc_now_month() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cur.fetchone() is not None


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    if not _table_exists(conn, table):
        return set()
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    return {str(r[1] or "") for r in cur.fetchall()}


def _format_appt_time(raw: Any) -> str:
    """Return HH:MM (or short Sensei time) when real; otherwise '—' (never invent 09:00)."""
    text = str(raw or "").strip()
    if not text or text in {"—", "-", "n/a", "N/A", "null", "None"}:
        return "—"
    # SoftDent / Sensei often store HH:MM or HH:MM:SS or 0830
    digits = "".join(ch for ch in text if ch.isdigit())
    if ":" in text:
        parts = text.replace(".", ":").split(":")
        try:
            hh = int(parts[0])
            mm = int(parts[1]) if len(parts) > 1 else 0
            if 0 <= hh <= 23 and 0 <= mm <= 59:
                return f"{hh:02d}:{mm:02d}"
        except ValueError:
            pass
    if len(digits) >= 3 and len(digits) <= 4:
        padded = digits.zfill(4)
        try:
            hh = int(padded[:2])
            mm = int(padded[2:4])
            if 0 <= hh <= 23 and 0 <= mm <= 59:
                return f"{hh:02d}:{mm:02d}"
        except ValueError:
            pass
    # Keep short non-numeric labels only if they look like times (e.g. 8:30 AM)
    if len(text) <= 12 and any(ch.isdigit() for ch in text):
        return text[:12]
    return "—"


def _same_day_ada_map(
    conn: sqlite3.Connection,
    dates: list[str],
) -> dict[tuple[str, str], list[str]]:
    """patient_id + appt/proc date → distinct ADA codes (SoftDent READ-ONLY)."""
    out: dict[tuple[str, str], list[str]] = {}
    if not dates or not _table_exists(conn, "sd_procedures"):
        return out
    try:
        from softdent_treatment_planning import normalize_ada_code
    except Exception:  # noqa: BLE001
        def normalize_ada_code(raw: Any) -> str:  # type: ignore[misc]
            return str(raw or "").strip().upper()

    placeholders = ",".join("?" * len(dates))
    cur = conn.cursor()
    cur.execute(
        f"""
        SELECT patient_id, substr(replace(proc_date, '/', '-'), 1, 10) AS d, ada_code
        FROM sd_procedures
        WHERE substr(replace(proc_date, '/', '-'), 1, 10) IN ({placeholders})
          AND COALESCE(patient_id, '') != ''
          AND COALESCE(ada_code, '') != ''
        ORDER BY proc_date, ada_code
        """,
        list(dates),
    )
    for row in cur.fetchall():
        pid = str(row[0] or "").strip()
        day = str(row[1] or "").strip()[:10]
        ada = normalize_ada_code(row[2])
        if not pid or not day or not ada or ada in {"0", "0000", "D0000"}:
            continue
        key = (pid, day)
        bucket = out.setdefault(key, [])
        if ada not in bucket:
            bucket.append(ada)
    return out


def _open_db():
    db_path = resolve_sd_sqlite_db()
    if not db_path or not db_path.is_file():
        return None, db_path
    return sqlite3.connect(db_path), db_path


def _conn_has_operational_data(conn: sqlite3.Connection) -> bool:
    for table in ("sd_procedures", "sd_payments", "sd_patients", "sd_claims"):
        if not _table_exists(conn, table):
            continue
        cur = conn.cursor()
        # Table names are fixed literals above (not user input).
        cur.execute("SELECT COUNT(*) FROM " + table)
        if int(cur.fetchone()[0] or 0) > 0:
            return True
    for table in ("daysheet_totals", "production_by_provider", "transactions", "writeoff_totals", "production_by_ada"):
        if not _table_exists(conn, table):
            continue
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM " + table)
        if int(cur.fetchone()[0] or 0) > 0:
            return True
    return False


def _connect():
    conn, db_path = _open_db()
    if not conn:
        return None, db_path
    if not _conn_has_operational_data(conn):
        conn.close()
        return None, db_path
    return conn, db_path


def _collections_from_daysheet_totals(conn: sqlite3.Connection, *, limit: int) -> list[tuple[str, float]]:
    if not _table_exists(conn, "daysheet_totals"):
        return []
    cur = conn.cursor()
    cur.execute(
        """
        SELECT year_month, SUM(COALESCE(collections, 0))
        FROM daysheet_totals
        WHERE COALESCE(collections, 0) > 0
        GROUP BY year_month
        ORDER BY year_month
        """
    )
    rows = [(str(period), float(total or 0)) for period, total in cur.fetchall() if period]
    return rows[-limit:]


def _provider_production_from_analytics(conn: sqlite3.Connection, *, limit: int) -> list[dict[str, Any]]:
    if not _table_exists(conn, "production_by_provider"):
        return []
    cur = conn.cursor()
    cur.execute(
        """
        SELECT COALESCE(provider_name, provider_label, provider_id), SUM(COALESCE(gross_production, 0)) AS total
        FROM production_by_provider
        WHERE COALESCE(gross_production, 0) > 0
        GROUP BY COALESCE(provider_name, provider_label, provider_id)
        ORDER BY total DESC
        LIMIT ?
        """,
        (limit,),
    )
    providers: list[dict[str, Any]] = []
    for label, total in cur.fetchall():
        providers.append({"providerCode": str(label or "").strip() or "unknown", "production": round(float(total or 0), 2)})
    return providers


def collections_daily(*, limit: int = 30) -> dict[str, Any]:
    conn, db_path = _open_db()
    if not conn:
        return {"hasData": False, "points": [], "labels": [], "values": []}
    try:
        cur = conn.cursor()
        rows: list[tuple[str, float]] = []
        source = "sd_payments"
        if _table_exists(conn, "sd_payments"):
            cur.execute(
                """
                SELECT payment_date, SUM(COALESCE(amount, 0))
                FROM sd_payments
                WHERE payment_date IS NOT NULL AND payment_date != '' AND COALESCE(amount, 0) > 0
                GROUP BY payment_date
                ORDER BY payment_date
                """
            )
            rows = [(str(day), float(total or 0)) for day, total in cur.fetchall() if day]
        if not rows:
            rows = _collections_from_daysheet_totals(conn, limit=limit)
            source = "daysheet_totals"
    finally:
        conn.close()
    trimmed = rows[-limit:]
    return {
        "hasData": bool(trimmed),
        "labels": [day for day, _ in trimmed],
        "values": [round(total, 2) for _, total in trimmed],
        "points": [{"date": day, "collections": round(total, 2)} for day, total in trimmed],
        "source": source,
        "dbPath": str(db_path),
    }


def new_patients_mtd(*, period: str | None = None) -> dict[str, Any]:
    period = (period or _utc_now_month())[:7]
    conn, db_path = _connect()
    if not conn:
        return {"hasData": False, "count": 0, "period": period}
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT COUNT(DISTINCT patient_id)
            FROM sd_patients
            WHERE substr(COALESCE(first_visit_date, ''), 1, 7) = ?
            """,
            (period,),
        )
        count = int(cur.fetchone()[0] or 0)
        if count <= 0:
            cur.execute(
                """
                SELECT COUNT(DISTINCT patient_id)
                FROM sd_procedures
                WHERE substr(proc_date, 1, 7) = ?
                  AND ada_code IN ({codes})
                """.format(codes=",".join("?" for _ in NEW_PATIENT_CODES)),
                (period, *NEW_PATIENT_CODES),
            )
            count = int(cur.fetchone()[0] or 0)
    finally:
        conn.close()
    return {"hasData": count > 0, "count": count, "period": period, "source": "sd_patients", "dbPath": str(db_path)}


def appointments_snapshot(*, limit: int = 12) -> dict[str, Any]:
    conn, db_path = _open_db()
    if not conn:
        return {"hasData": False, "appointments": []}
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT appt_date, patient_id, provider_code, status
            FROM sd_appointments
            ORDER BY appt_date DESC
            LIMIT ?
            """,
            (limit,),
        )
        appointments = [
            {
                "date": str(row[0] or ""),
                "patientId": str(row[1] or ""),
                "provider": str(row[2] or ""),
                "status": str(row[3] or ""),
            }
            for row in cur.fetchall()
        ]
        source = "sd_appointments"
        if not appointments:
            cur.execute(
                """
                SELECT proc_date, patient_id, provider_code, 'seen'
                FROM sd_procedures
                WHERE COALESCE(patient_id, '') != '' AND COALESCE(proc_date, '') != ''
                GROUP BY proc_date, patient_id, provider_code
                ORDER BY proc_date DESC
                LIMIT ?
                """,
                (limit,),
            )
            appointments = [
                {
                    "date": str(row[0] or ""),
                    "patientId": str(row[1] or ""),
                    "provider": str(row[2] or ""),
                    "status": str(row[3] or ""),
                }
                for row in cur.fetchall()
            ]
            if appointments:
                source = "sd_procedures"
    finally:
        conn.close()
    return {"hasData": bool(appointments), "appointments": appointments, "source": source, "dbPath": str(db_path)}


def _hash_patient_id(patient_id: str) -> str:
    """PHI-safe 4-char hash for OM widgets (Moonshot OM-A0)."""
    import hashlib

    raw = str(patient_id or "").strip()
    if not raw:
        return "——"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:4].upper()


def _normalize_appt_status(raw: str) -> str:
    r = str(raw or "").lower()
    if any(x in r for x in ("cancel", "no show", "noshow", "broken")):
        return "open"
    if any(x in r for x in ("complete", "seen", "checkout", "checked out")):
        return "completed"
    if any(x in r for x in ("checkin", "check-in", "here", "arrived")):
        return "checked-in"
    if "block" in r:
        return "blocked"
    return "booked"


def appointments_today_snapshot(*, target_date: str | None = None) -> dict[str, Any]:
    """Today's SoftDent appointments grouped for OM operatory board (read-only).

    Uses real sd_appointments columns (appt_date, patient_id, provider_code, status)
    via softdent_practice_exports._build_operatory_from_sd_appointments — no invented
    operatory/time schema. Patient display is hashed (PHI-safe).
    """
    from datetime import date

    from softdent_practice_exports import _build_operatory_from_sd_appointments

    target = (target_date or date.today().isoformat())[:10]
    conn, db_path = _open_db()
    if not conn:
        return {
            "hasData": False,
            "operatories": [],
            "date": target,
            "count": 0,
            "source": "none",
        }
    try:
        chairs = _build_operatory_from_sd_appointments(conn, schedule_date=target, days_window=0)
        if not chairs:
            return {
                "hasData": False,
                "operatories": [],
                "date": target,
                "count": 0,
                "source": "sd_appointments",
                "dbPath": str(db_path),
                "emptyMessage": "No SoftDent appointments for today — run SoftDent sync.",
            }
        chosen_day = str(chairs[0].get("scheduleDate") or target)[:10]
        operatories: list[dict[str, Any]] = []
        total = 0
        for chair in chairs[:8]:
            slots_out: list[dict[str, Any]] = []
            for slot in (chair.get("slots") or [])[:12]:
                if not isinstance(slot, dict):
                    continue
                patient_raw = str(slot.get("patient") or "").strip()
                status = _normalize_appt_status(str(slot.get("procedure") or slot.get("tone") or ""))
                # procedure field holds status label from builder; tone is visual
                if slot.get("tone") == "ok":
                    status = "checked-in"
                slots_out.append(
                    {
                        "time": str(slot.get("time") or "—")[:5],
                        "status": status,
                        "patientHash": _hash_patient_id(patient_raw) if patient_raw else None,
                        "provider": str(chair.get("name") or ""),
                    }
                )
                total += 1
            operatories.append({"name": str(chair.get("name") or "Op—"), "slots": slots_out})
        return {
            "hasData": total > 0,
            "operatories": operatories,
            "date": chosen_day,
            "count": total,
            "source": "sd_appointments",
            "dbPath": str(db_path),
        }
    finally:
        conn.close()


def _initials_from_name(raw_name: str) -> str:
    parts = [x for x in str(raw_name or "").split() if x]
    letters = "".join(p[0] for p in parts[:2] if p).upper()
    return f"{letters or 'P'}—"


def _normalize_patient_name_key(name: str | None) -> str:
    from softdent_odbc_extract import _normalize_patient_name_key as normalize_key

    return normalize_key(name)


def _patient_name_to_id_index(conn: sqlite3.Connection) -> dict[str, str]:
    """Map normalized name keys and exact lower names → patient_id."""
    out: dict[str, str] = {}
    if not _table_exists(conn, "sd_patients"):
        return out
    cur = conn.cursor()
    cur.execute("SELECT patient_id, patient_name FROM sd_patients")
    for pid, pname in cur.fetchall():
        patient_id = str(pid or "").strip()
        raw = str(pname or "").strip()
        if not patient_id or not raw:
            continue
        norm = _normalize_patient_name_key(raw)
        if norm and norm not in out:
            out[norm] = patient_id
        exact = raw.lower()
        if exact not in out:
            out[exact] = patient_id
    return out


def _lookup_patient_id(name_index: dict[str, str], patient_name: str) -> str:
    raw = str(patient_name or "").strip()
    if not raw or not name_index:
        return ""
    hit = name_index.get(_normalize_patient_name_key(raw))
    if hit:
        return hit
    return name_index.get(raw.lower(), "")


def appointments_range_snapshot(
    start_iso: str,
    days: int = 4,
    *,
    provider_filter: str | None = None,
) -> dict[str, Any]:
    """Multi-day appointment list for OM (Mon–Thu). SoftDent read-only.

    Staff OM may render full patientName; hash/initials remain for handoff/logs.
    Time: real appt_time when column/data exists; otherwise honest '—'.
    ADA: same-day sd_procedures join into procedureHint / adaCodes (empty → '—').
    """
    from datetime import datetime, timedelta

    conn, db_path = _open_db()
    if not conn:
        return {
            "hasData": False,
            "days": [],
            "source": "none",
            "dbPath": str(db_path) if db_path else None,
            "apptTimeColumn": False,
            "emptyNotZero": True,
        }

    try:
        if not _table_exists(conn, "sd_appointments"):
            return {
                "hasData": False,
                "days": [],
                "source": "none",
                "dbPath": str(db_path),
                "apptTimeColumn": False,
                "emptyNotZero": True,
                "emptyMessage": "sd_appointments table missing — run SoftDent extract.",
            }

        # Ensure appt_time exists on older caches (honest NULL until next extract fills it).
        appt_cols = _table_columns(conn, "sd_appointments")
        if "appt_time" not in appt_cols:
            try:
                conn.execute("ALTER TABLE sd_appointments ADD COLUMN appt_time TEXT")
                conn.commit()
                appt_cols = _table_columns(conn, "sd_appointments")
            except Exception:
                pass

        start_raw = str(start_iso or "")[:10]
        try:
            start_dt = datetime.fromisoformat(start_raw)
        except ValueError:
            return {
                "hasData": False,
                "days": [],
                "source": "none",
                "error": "invalid start date",
                "apptTimeColumn": "appt_time" in appt_cols,
                "emptyNotZero": True,
            }

        day_count = max(1, min(int(days or 4), 14))
        dates = [(start_dt + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(day_count)]
        placeholders = ",".join("?" * len(dates))
        has_appt_time = "appt_time" in appt_cols
        time_select = "a.appt_time" if has_appt_time else "NULL AS appt_time"

        sql = f"""
        SELECT a.appt_date, a.patient_id, a.provider_code, a.status, p.patient_name, {time_select}
        FROM sd_appointments a
        LEFT JOIN sd_patients p ON a.patient_id = p.patient_id
        WHERE substr(replace(a.appt_date, '/', '-'), 1, 10) IN ({placeholders})
        ORDER BY a.appt_date, a.provider_code
        """
        params: list[Any] = list(dates)
        if provider_filter:
            sql = sql.replace(
                f"WHERE substr(replace(a.appt_date, '/', '-'), 1, 10) IN ({placeholders})",
                f"WHERE substr(replace(a.appt_date, '/', '-'), 1, 10) IN ({placeholders})"
                " AND COALESCE(a.provider_code,'') = ?",
            )
            params.append(str(provider_filter))

        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        ada_map = _same_day_ada_map(conn, dates)

        days_out: list[dict[str, Any]] = []
        for d in dates:
            day_rows = [r for r in rows if str(r[0] or "")[:10].replace("/", "-") == d]
            slots: list[dict[str, Any]] = []
            for r in day_rows:
                patient_raw = str(r[4] or "").strip()
                pid = str(r[1] or "")
                adas = list(ada_map.get((pid, d), [])[:8])
                procedure_hint = ", ".join(adas) if adas else "—"
                time_disp = _format_appt_time(r[5] if len(r) > 5 else None)
                slots.append(
                    {
                        "patientId": pid,
                        "patientHash": _hash_patient_id(pid),
                        "initials": _initials_from_name(patient_raw) if patient_raw else "P—",
                        # Full name for staff OM lists; hash/initials for handoff/logs.
                        "patientName": patient_raw or None,
                        "provider": str(r[2] or "") or "—",
                        "status": _normalize_appt_status(str(r[3] or "")),
                        "time": time_disp,
                        "timeMissing": time_disp == "—",
                        "procedureHint": procedure_hint,
                        "adaCodes": adas,
                    }
                )
            # Provider then time — supports OM provider section headers without inventing operatory.
            def _slot_sort_key(s: dict[str, Any]) -> tuple:
                t = str(s.get("time") or "—")
                return (str(s.get("provider") or ""), t == "—", t)

            slots.sort(key=_slot_sort_key)
            days_out.append(
                {
                    "date": d,
                    "dayName": datetime.fromisoformat(d).strftime("%a"),
                    "slots": slots,
                    "count": len(slots),
                    "emptyMessage": f"No SoftDent appointments for {d}." if not slots else "",
                }
            )

        return {
            "hasData": any(d["count"] > 0 for d in days_out),
            "days": days_out,
            "dateRange": f"{dates[0]} to {dates[-1]}",
            "source": "sd_appointments",
            "dbPath": str(db_path),
            "apptTimeColumn": has_appt_time,
            "emptyNotZero": True,
            "nextPatient": _next_patient_hint(days_out),
            "emptyMessage": "No appointments found for Mon–Thu — verify SoftDent sync.",
        }
    finally:
        conn.close()


def _next_patient_hint(days_out: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Earliest upcoming timed slot for today (local ISO date) — SoftDent READ-ONLY."""
    from datetime import date, datetime

    today = date.today().isoformat()
    now_hm = datetime.now().strftime("%H:%M")
    today_day = next((d for d in days_out if str(d.get("date") or "")[:10] == today), None)
    if not today_day:
        return None
    candidates: list[dict[str, Any]] = []
    for slot in today_day.get("slots") or []:
        if not isinstance(slot, dict):
            continue
        t = str(slot.get("time") or "—")
        if t == "—" or slot.get("timeMissing"):
            continue
        if t >= now_hm:
            candidates.append(slot)
    candidates.sort(key=lambda s: str(s.get("time") or "99:99"))
    pick = candidates[0] if candidates else None
    if not pick:
        # All timed slots already passed — surface last timed slot as context only
        timed = [
            s
            for s in (today_day.get("slots") or [])
            if isinstance(s, dict) and str(s.get("time") or "—") != "—"
        ]
        timed.sort(key=lambda s: str(s.get("time") or ""))
        if not timed:
            return {"ok": True, "available": False, "reason": "no_timed_slots_today"}
        pick = timed[-1]
        return {
            "ok": True,
            "available": True,
            "past": True,
            "date": today,
            "time": pick.get("time"),
            "patientHash": pick.get("patientHash"),
            "initials": pick.get("initials"),
            "patientName": pick.get("patientName"),
            "provider": pick.get("provider"),
            "adaCodes": pick.get("adaCodes") or [],
            "patientId": pick.get("patientId"),
        }
    return {
        "ok": True,
        "available": True,
        "past": False,
        "date": today,
        "time": pick.get("time"),
        "patientHash": pick.get("patientHash"),
        "initials": pick.get("initials"),
        "patientName": pick.get("patientName"),
        "provider": pick.get("provider"),
        "adaCodes": pick.get("adaCodes") or [],
        "patientId": pick.get("patientId"),
    }


def monday_of_week_iso(ref_iso: str | None = None) -> str:
    """ISO date for Monday of the week containing ref (default: today)."""
    from datetime import date, datetime, timedelta

    if ref_iso:
        try:
            d = datetime.fromisoformat(str(ref_iso)[:10]).date()
        except ValueError:
            d = date.today()
    else:
        d = date.today()
    monday = d - timedelta(days=d.weekday())
    return monday.isoformat()


def provider_utilization_last_7d() -> dict[str, Any]:
    """Appointment counts by provider for the last 7 calendar days (read-only)."""
    from datetime import date, timedelta

    end = date.today()
    start = end - timedelta(days=6)
    conn, db_path = _open_db()
    if not conn:
        return {
            "hasData": False,
            "providers": [],
            "days": 7,
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
        }
    try:
        if not _table_exists(conn, "sd_appointments"):
            return {
                "hasData": False,
                "providers": [],
                "days": 7,
                "startDate": start.isoformat(),
                "endDate": end.isoformat(),
                "dbPath": str(db_path),
            }
        cur = conn.cursor()
        cur.execute(
            """
            SELECT COALESCE(provider_code, 'unassigned') AS provider,
                   COUNT(*) AS appt_count
            FROM sd_appointments
            WHERE substr(replace(appt_date, '/', '-'), 1, 10) >= ?
              AND substr(replace(appt_date, '/', '-'), 1, 10) <= ?
            GROUP BY COALESCE(provider_code, 'unassigned')
            ORDER BY appt_count DESC
            LIMIT 12
            """,
            (start.isoformat(), end.isoformat()),
        )
        providers = [
            {"providerCode": str(row[0] or "unassigned"), "appointments": int(row[1] or 0)}
            for row in cur.fetchall()
        ]
    finally:
        conn.close()
    return {
        "hasData": bool(providers),
        "providers": providers,
        "days": 7,
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "source": "sd_appointments",
        "dbPath": str(db_path),
    }


def _resolve_claim_patient_id(
    claim_id: str,
    patient_name: str,
    name_to_id: dict[str, str],
) -> str:
    """Prefer MRN embedded in TXN-/DS- claim ids for SoftDent ledger settlement."""
    try:
        from softdent_operational_pipeline import patient_id_from_claim_id

        from_claim = patient_id_from_claim_id(str(claim_id or ""))
        if from_claim:
            return from_claim
    except Exception:
        pass
    return _lookup_patient_id(name_to_id, str(patient_name or "").strip())


def _filter_unpaid_claim_rows(
    rows: list[tuple[Any, ...]],
    *,
    name_to_id: dict[str, str],
    transactions: list[dict[str, Any]] | None = None,
    settlement_index: dict[str, set[str]] | None = None,
) -> list[tuple[Any, ...]]:
    """Drop paid/settled rows using full SoftDent TXN ledger (not stale DS status)."""
    if not rows:
        return []
    try:
        from softdent_operational_pipeline import claim_is_unpaid_on_txn
    except Exception:
        return rows
    txs = transactions
    idx = settlement_index
    if txs is None or idx is None:
        try:
            from softdent_operational_pipeline import load_txn_settlement_context

            txs, idx = load_txn_settlement_context()
        except Exception:
            txs, idx = None, None
    kept: list[tuple[Any, ...]] = []
    for claim_id, patient, payer, service_date, amount, status in rows:
        patient_raw = str(patient or "").strip()
        patient_id = _resolve_claim_patient_id(str(claim_id or ""), patient_raw, name_to_id)
        if claim_is_unpaid_on_txn(
            patient_id=patient_id,
            service_date=str(service_date or ""),
            claim_id=str(claim_id or ""),
            claim_status=str(status or ""),
            transactions=txs,
            settlement_index=idx,
        ):
            kept.append((claim_id, patient, payer, service_date, amount, status))
    return kept


def claims_outstanding(*, limit: int = 10) -> dict[str, Any]:
    """Open SoftDent claims sample + full outstanding total (empty ≠ $0).

    ``limit`` caps the returned claim *list* only — totalOutstanding/count
    always cover the full open set so UI dollars are not understated.

    When ``sd_patients`` exists, resolve ``patientId`` / hash / initials via
    patient_name lookup so Claims page can open mini dossier on click.

    Re-checks each row against SoftDent Trans-for-a-Period so stale daysheet
    (DS-) rows with insurance pay on/after DOS do not appear as unpaid.
    """
    conn, db_path = _connect()
    if not conn:
        return {
            "hasData": False,
            "claims": [],
            "totalOutstanding": None,
            "count": 0,
            "sampleWithPatientId": 0,
            "honesty": "empty != $0",
        }
    try:
        cur = conn.cursor()
        source = "sd_claims"
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
        total = None
        count = 0
        generic_payer_count = 0
        txn_ctx: tuple[list[dict[str, Any]], dict[str, set[str]]] | None = None
        if _table_exists(conn, "sd_claims"):
            cur.execute(
                """
                SELECT claim_id, patient_name, payer, service_date, claim_amount, claim_status
                FROM sd_claims
                WHERE """
                + open_where
                + """
                ORDER BY claim_amount DESC
                """
            )
            candidate_rows = list(cur.fetchall())
            name_to_id = _patient_name_to_id_index(conn)
            try:
                from softdent_operational_pipeline import load_txn_settlement_context

                txn_ctx = load_txn_settlement_context()
            except Exception:
                txn_ctx = None
            rows = _filter_unpaid_claim_rows(
                candidate_rows,
                name_to_id=name_to_id,
                transactions=txn_ctx[0] if txn_ctx else None,
                settlement_index=txn_ctx[1] if txn_ctx else None,
            )
            count = len(rows)
            total = round(sum(float(r[4] or 0) for r in rows), 2) if rows else 0.0
            generic_payer_count = sum(
                1 for r in rows if _generic_payer_label(str(r[2] or ""))
            )
            rows = rows[: max(1, int(limit))]
        else:
            rows = []
            name_to_id = {}
            generic_payer_count = 0

        if not rows and _table_exists(conn, "outstanding_claims"):
            source = "outstanding_claims"
            cur.execute(
                """
                SELECT COUNT(*), SUM(COALESCE(claim_amount, 0))
                FROM outstanding_claims
                WHERE COALESCE(claim_amount, 0) > 0
                """
            )
            row = cur.fetchone() or (0, None)
            count = int(row[0] or 0)
            if row[1] is not None:
                total = round(float(row[1]), 2)
            cur.execute(
                """
                SELECT claim_id, patient_name, payer, service_date, claim_amount, claim_status
                FROM outstanding_claims
                WHERE COALESCE(claim_amount, 0) > 0
                ORDER BY claim_amount DESC
                LIMIT ?
                """,
                (max(1, int(limit)),),
            )
            rows = cur.fetchall()
            name_to_id = _patient_name_to_id_index(conn) if rows else {}
            generic_payer_count = sum(
                1 for r in rows if _generic_payer_label(str(r[2] or ""))
            )

        claims = []
        with_patient_id = 0
        try:
            from patient_dossier import name_hash as _name_hash
        except Exception:
            _name_hash = None  # type: ignore[assignment,misc]
        for claim_id, patient, payer, service_date, amount, status in rows:
            patient_raw = str(patient or "").strip()
            patient_id = _resolve_claim_patient_id(str(claim_id or ""), patient_raw, name_to_id)
            if patient_id:
                with_patient_id += 1
            entry: dict[str, Any] = {
                "claimId": str(claim_id or ""),
                "patientName": patient_raw,
                "payer": str(payer or ""),
                "serviceDate": str(service_date or ""),
                "amount": round(float(amount or 0), 2),
                "status": str(status or ""),
                "initials": _initials_from_name(patient_raw) if patient_raw else "P—",
            }
            if patient_raw and _name_hash:
                entry["nameHash"] = _name_hash(patient_raw)
            if patient_id:
                entry["patientId"] = patient_id
                entry["patientHash"] = _hash_patient_id(patient_id)
            else:
                entry["patientId"] = None
                entry["patientHash"] = None
            claims.append(entry)
    finally:
        conn.close()
    payer_stats = {
        "generic": int(generic_payer_count),
        "named": max(0, int(count) - int(generic_payer_count)),
        "total": int(count),
    }
    return {
        "hasData": count > 0 or bool(claims),
        "claims": claims,
        "totalOutstanding": total,
        "count": count,
        "sampleLimit": max(1, int(limit)),
        "sampleWithPatientId": with_patient_id if rows else 0,
        "payerStats": payer_stats,
        "source": source,
        "dbPath": str(db_path),
        "honesty": "empty != $0",
        "sourceNote": (
            "sd_claims may be SoftDent Trans-for-a-Period estimates when SoftDent "
            "Outstanding Claims by Patient Excel is greyed (empty ≠ $0)."
        ),
    }


def _generic_payer_label(payer: str) -> bool:
    return str(payer or "").strip().lower() in {"", "insurance", "unknown", "n/a", "-", "—"}


def _claim_age_days(service_date: str) -> int | None:
    text = str(service_date or "").strip()[:10]
    if len(text) < 10:
        return None
    try:
        dos = datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        return None
    return max(0, (datetime.now(timezone.utc).date() - dos).days)


def _procedure_lines_for_claim(
    *,
    patient_id: str,
    service_date: str,
    patient_name: str = "",
) -> list[dict[str, Any]]:
    """SoftDent Trans-for-a-Period lines for patient+DOS (READ-ONLY)."""
    pid = str(patient_id or "").strip()
    dos = str(service_date or "").strip()[:10]
    if not dos:
        return []
    try:
        from softdent_operational_pipeline import (
            INSURANCE_PAYMENT_CODES,
            INSURANCE_WRITEOFF_CODES,
            load_softdent_transactions_xls,
            _account_stem,
        )
    except Exception:
        return []
    try:
        txs = load_softdent_transactions_xls()
    except Exception:
        return []
    stem = _account_stem(pid) if pid else ""
    name_key = str(patient_name or "").strip().casefold()
    lines: list[dict[str, Any]] = []
    for row in txs:
        if str(row.get("reportDate") or "")[:10] != dos:
            continue
        row_pid = str(row.get("patientId") or "").strip()
        row_name = str(row.get("patientName") or "").strip().casefold()
        if pid and row_pid == pid:
            pass
        elif stem and _account_stem(row_pid) == stem:
            pass
        elif name_key and row_name == name_key:
            pass
        else:
            continue
        code = str(row.get("code") or "").strip()
        base = code.split(".")[0] if code else ""
        production = row.get("production")
        try:
            prod_f = float(production) if production not in (None, "") else None
        except (TypeError, ValueError):
            prod_f = None
        kind = "procedure"
        if base in INSURANCE_PAYMENT_CODES or base == "2":
            kind = "insurance_payment"
        elif base in INSURANCE_WRITEOFF_CODES:
            kind = "insurance_writeoff"
        elif prod_f in (None, 0):
            kind = "other"
        lines.append(
            {
                "code": code,
                "kind": kind,
                "production": round(prod_f, 2) if prod_f not in (None, 0) else None,
                "providerId": str(row.get("providerId") or ""),
                "patientId": row_pid,
            }
        )
    return lines


def _build_claim_review_checklist(
    *,
    claim: dict[str, Any],
    procedures: list[dict[str, Any]],
    age_days: int | None,
) -> dict[str, Any]:
    payer = str(claim.get("payer") or "")
    named_payer = not _generic_payer_label(payer)
    has_patient = bool(str(claim.get("patientId") or "").strip())
    proc_lines = [p for p in procedures if p.get("kind") == "procedure"]
    pay_lines = [p for p in procedures if p.get("kind") == "insurance_payment"]
    wo_lines = [p for p in procedures if p.get("kind") == "insurance_writeoff"]
    status = str(claim.get("status") or "").strip().lower()
    unpaid = status not in {"paid", "closed", "complete", "completed", "denied", "settled"}
    items = [
        {
            "id": "unpaid",
            "label": "Claim still unpaid (not paid/completed)",
            "ok": unpaid,
            "detail": str(claim.get("status") or "—"),
        },
        {
            "id": "named_payer",
            "label": "Named SoftDent payer (not generic Insurance)",
            "ok": named_payer,
            "detail": payer or "empty",
        },
        {
            "id": "patient_join",
            "label": "Patient id joined for dossier",
            "ok": has_patient,
            "detail": str(claim.get("patientId") or "missing"),
        },
        {
            "id": "procedures",
            "label": "SoftDent procedure lines on DOS",
            "ok": bool(proc_lines),
            "detail": f"{len(proc_lines)} line(s)" if proc_lines else "none on SoftDent TXN",
        },
        {
            "id": "no_same_day_settlement",
            "label": "No SoftDent pay/write-off on DOS",
            "ok": not pay_lines and not wo_lines,
            "detail": (
                f"pay={len(pay_lines)} writeoff={len(wo_lines)}"
                if (pay_lines or wo_lines)
                else "clear"
            ),
        },
        {
            "id": "age_action",
            "label": "Age action band",
            "ok": age_days is not None and age_days <= 90,
            "detail": (
                f"{age_days}d · follow up now"
                if age_days is not None and age_days > 90
                else (f"{age_days}d" if age_days is not None else "unknown DOS")
            ),
        },
    ]
    gaps = [i["label"] for i in items if not i.get("ok")]
    return {
        "items": items,
        "ready": len(gaps) == 0,
        "gaps": gaps,
        "gapCount": len(gaps),
    }


def _build_claim_review_narrative(
    *,
    claim: dict[str, Any],
    checklist: dict[str, Any],
    age_days: int | None,
    procedures: list[dict[str, Any]],
) -> dict[str, Any]:
    patient = str(claim.get("patientName") or "Patient").strip() or "Patient"
    payer = str(claim.get("payer") or "Insurance").strip() or "Insurance"
    dos = str(claim.get("serviceDate") or "—")[:10]
    amount = claim.get("amount")
    try:
        amount_txt = f"${float(amount):,.2f}" if amount not in (None, "") else "amount unknown"
    except (TypeError, ValueError):
        amount_txt = "amount unknown"
    age_txt = f"{age_days} days old" if age_days is not None else "age unknown"
    if age_days is None:
        action = "Confirm SoftDent DOS, then review payer status in SoftDent (READ-ONLY)."
    elif age_days <= 30:
        action = "Monitor — still in 0–30 day band; verify submission if not already sent."
    elif age_days <= 60:
        action = "Follow up with payer — claim is in the 31–60 day band."
    elif age_days <= 90:
        action = "Escalate follow-up — claim is in the 61–90 day band."
    else:
        action = "Priority follow-up — claim is over 90 days; call payer or resubmit path in SoftDent."
    proc_codes = [
        str(p.get("code") or "")
        for p in procedures
        if p.get("kind") == "procedure" and p.get("code")
    ]
    proc_bit = (", ".join(proc_codes[:6]) + ("…" if len(proc_codes) > 6 else "")) if proc_codes else "no SoftDent procedure lines on file"
    gaps = checklist.get("gaps") if isinstance(checklist.get("gaps"), list) else []
    gap_bit = (" Gaps: " + "; ".join(str(g) for g in gaps[:4]) + ".") if gaps else " Preflight clear."
    text = (
        f"{patient} · unpaid SoftDent claim for {payer} · DOS {dos} · {amount_txt} · {age_txt}. "
        f"Billed codes: {proc_bit}. Next: {action}{gap_bit} "
        "SoftDent READ-ONLY · empty ≠ $0."
    )
    phone = (
        f"{patient} | claim {claim.get('claimId') or '—'} | {payer} | "
        f"DOS {dos} | {amount_txt} | {claim.get('status') or '—'}"
    )
    return {
        "text": text,
        "nextAction": action,
        "phoneCopy": phone,
        "source": "deterministic-softdent-claim-review",
        "honesty": "empty != $0; SoftDent READ-ONLY; not SoftDent Outstanding Claims Excel",
    }


def claim_review(*, claim_id: str = "", claim: dict[str, Any] | None = None) -> dict[str, Any]:
    """SoftDent claim click review: narrative + preflight + DOS procedure lines.

    Unpaid-only. SoftDent READ-ONLY. empty ≠ $0.
    """
    body = claim if isinstance(claim, dict) else {}
    cid = str(claim_id or body.get("claimId") or body.get("claim_id") or "").strip()
    out: dict[str, Any] = {
        "ok": False,
        "hasData": False,
        "claimId": cid,
        "honesty": "empty != $0",
        "readOnly": True,
        "softdentWriteBack": False,
    }
    claim_row: dict[str, Any] | None = None
    if body.get("patientName") or body.get("amount") is not None or body.get("serviceDate"):
        claim_row = {
            "claimId": cid or str(body.get("claimId") or ""),
            "patientName": str(body.get("patientName") or "").strip(),
            "payer": str(body.get("payer") or "").strip(),
            "serviceDate": str(body.get("serviceDate") or "")[:10],
            "amount": body.get("amount"),
            "status": str(body.get("status") or "").strip(),
            "patientId": str(body.get("patientId") or "").strip() or None,
            "patientHash": body.get("patientHash"),
            "initials": body.get("initials"),
        }
    conn, db_path = _connect()
    if conn and cid:
        try:
            if _table_exists(conn, "sd_claims"):
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT claim_id, patient_name, payer, service_date, claim_amount, claim_status
                    FROM sd_claims
                    WHERE claim_id = ?
                    LIMIT 1
                    """,
                    (cid,),
                )
                hit = cur.fetchone()
                if hit:
                    claim_row = {
                        "claimId": str(hit[0] or ""),
                        "patientName": str(hit[1] or "").strip(),
                        "payer": str(hit[2] or "").strip(),
                        "serviceDate": str(hit[3] or "")[:10],
                        "amount": round(float(hit[4] or 0), 2) if hit[4] is not None else None,
                        "status": str(hit[5] or "").strip(),
                        "patientId": (claim_row or {}).get("patientId"),
                        "patientHash": (claim_row or {}).get("patientHash"),
                        "initials": (claim_row or {}).get("initials")
                        or _initials_from_name(str(hit[1] or "")),
                    }
                    # Name → patient_id join when missing (Last, First ↔ First Last).
                    if not claim_row.get("patientId") and _table_exists(conn, "sd_patients"):
                        name_index = _patient_name_to_id_index(conn)
                        pid = _lookup_patient_id(
                            name_index, str(claim_row.get("patientName") or "")
                        )
                        if pid:
                            claim_row["patientId"] = pid
                            claim_row["patientHash"] = _hash_patient_id(pid)
        finally:
            conn.close()
        out["dbPath"] = str(db_path)

    if not claim_row or not str(claim_row.get("claimId") or cid):
        out["error"] = "claim_not_found"
        out["emptyMessage"] = "SoftDent claim not found — empty ≠ $0"
        return out

    # TXN claim ids embed MRN: TXN-YYYYMMDD-{patientId}
    if not claim_row.get("patientId"):
        parts = str(claim_row.get("claimId") or "").split("-")
        if len(parts) >= 3 and parts[0].upper() == "TXN" and parts[-1].isdigit():
            claim_row["patientId"] = parts[-1]
            claim_row["patientHash"] = _hash_patient_id(parts[-1])

    status = str(claim_row.get("status") or "").strip().lower()
    if status in {"paid", "closed", "complete", "completed", "denied", "settled"}:
        out["error"] = "claim_not_unpaid"
        out["claim"] = claim_row
        out["emptyMessage"] = "Claim is paid/completed — not shown for unpaid review · empty ≠ $0"
        return out

    age_days = _claim_age_days(str(claim_row.get("serviceDate") or ""))
    mrn = str(claim_row.get("patientId") or "").strip()
    # SoftDent TXN MRN may differ from sd_patients id — also try claim id tail
    procedures = _procedure_lines_for_claim(
        patient_id=mrn,
        service_date=str(claim_row.get("serviceDate") or ""),
        patient_name=str(claim_row.get("patientName") or ""),
    )
    if not procedures and str(claim_row.get("claimId") or "").upper().startswith("TXN-"):
        tail = str(claim_row.get("claimId") or "").split("-")[-1]
        if tail and tail != mrn:
            procedures = _procedure_lines_for_claim(
                patient_id=tail,
                service_date=str(claim_row.get("serviceDate") or ""),
                patient_name=str(claim_row.get("patientName") or ""),
            )
            if procedures and not claim_row.get("patientId"):
                claim_row["patientId"] = tail
                claim_row["patientHash"] = _hash_patient_id(tail)

    checklist = _build_claim_review_checklist(
        claim=claim_row, procedures=procedures, age_days=age_days
    )
    narrative = _build_claim_review_narrative(
        claim=claim_row,
        checklist=checklist,
        age_days=age_days,
        procedures=procedures,
    )
    out.update(
        {
            "ok": True,
            "hasData": True,
            "claim": claim_row,
            "ageDays": age_days,
            "procedures": procedures,
            "procedureCount": len(procedures),
            "checklist": checklist,
            "narrative": narrative,
            "source": "softdent-claim-review",
        }
    )
    return out


def provider_production(*, limit: int = 8) -> dict[str, Any]:
    conn, db_path = _open_db()
    if not conn:
        return {"hasData": False, "providers": []}
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT provider_code, SUM(COALESCE(production, 0)) AS total
            FROM sd_procedures
            WHERE COALESCE(production, 0) > 0
            GROUP BY provider_code
            ORDER BY total DESC
            LIMIT ?
            """,
            (limit,),
        )
        providers = [
            {"providerCode": str(code or ""), "production": round(float(total or 0), 2)}
            for code, total in cur.fetchall()
        ]
        source = "sd_procedures"
        if not providers:
            providers = _provider_production_from_analytics(conn, limit=limit)
            source = "production_by_provider"
    finally:
        conn.close()
    grand = round(sum(item["production"] for item in providers), 2)
    return {"hasData": bool(providers), "providers": providers, "total": grand, "source": source, "dbPath": str(db_path)}


def adjustment_log(*, limit: int = 10) -> dict[str, Any]:
    conn, db_path = _open_db()
    if not conn:
        return {"hasData": False, "adjustments": []}
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT adj_date, patient_id, ada_code, amount, description
            FROM sd_adjustments
            ORDER BY adj_date DESC
            LIMIT ?
            """,
            (limit,),
        )
        adjustments = [
            {
                "date": str(row[0] or ""),
                "patientId": str(row[1] or ""),
                "code": str(row[2] or ""),
                "amount": round(float(row[3] or 0), 2),
                "description": str(row[4] or ""),
            }
            for row in cur.fetchall()
        ]
        source = "sd_adjustments"
        if not adjustments and _table_exists(conn, "writeoff_totals"):
            cur.execute(
                """
                SELECT report_date, writeoff_type, amount
                FROM writeoff_totals
                WHERE COALESCE(amount, 0) != 0
                ORDER BY report_date DESC
                LIMIT ?
                """,
                (limit,),
            )
            for report_date, writeoff_type, amount in cur.fetchall():
                adjustments.append(
                    {
                        "date": str(report_date or ""),
                        "patientId": "",
                        "code": str(writeoff_type or "writeoff"),
                        "amount": round(abs(float(amount or 0)), 2),
                        "description": str(writeoff_type or "Write-off"),
                    }
                )
            source = "writeoff_totals"
    finally:
        conn.close()
    return {"hasData": bool(adjustments), "adjustments": adjustments, "source": source, "dbPath": str(db_path)}


def patient_retention(*, months: int = 6) -> dict[str, Any]:
    conn, db_path = _connect()
    if not conn:
        return {"hasData": False, "activePatients": 0, "returningRatePct": None}
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(DISTINCT patient_id) FROM sd_patients")
        active = int(cur.fetchone()[0] or 0)
        cur.execute(
            """
            SELECT COUNT(DISTINCT patient_id)
            FROM sd_appointments
            WHERE appt_date >= date('now', ?)
            """,
            (f"-{months * 30} days",),
        )
        recent = int(cur.fetchone()[0] or 0)
    finally:
        conn.close()
    rate = round((recent / active) * 100, 1) if active > 0 else None
    return {
        "hasData": active > 0,
        "activePatients": active,
        "recentVisits": recent,
        "returningRatePct": rate,
        "windowMonths": months,
        "source": "sd_patients+sd_appointments",
        "dbPath": str(db_path),
    }


def operatory_grid() -> dict[str, Any]:
    """Operatory chair grid from export file or sd_appointments-derived schedule."""
    from import_loader import softdent_import_dir
    from softdent_practice_exports import (
        _aggregate_operatory_from_db,
        _build_operatory_from_sd_appointments,
        _read_operatory_chairs_file,
    )

    op_path = softdent_import_dir() / "operatory_schedule.json"
    if op_path.is_file():
        chairs = _read_operatory_chairs_file(op_path)
        if chairs:
            return {
                "hasData": True,
                "operatoryChairs": chairs,
                "source": "operatory_schedule.json",
                "sourcePath": str(op_path),
            }

    conn, db_path = _open_db()
    if not conn:
        return {"hasData": False, "operatoryChairs": []}
    try:
        chairs = _aggregate_operatory_from_db(conn)
        if not chairs:
            chairs = _build_operatory_from_sd_appointments(conn)
        source = "analytics-db" if chairs else "none"
        if chairs and not op_path.is_file():
            source = "sd_appointments"
    finally:
        conn.close()
    return {
        "hasData": bool(chairs),
        "operatoryChairs": chairs or [],
        "source": source,
        "dbPath": str(db_path),
    }


def production_daily(*, limit: int = 30) -> dict[str, Any]:
    """Daily production series — sd_procedures with daysheet_totals fallback."""
    conn, db_path = _open_db()
    if not conn:
        return {"hasData": False, "points": [], "labels": [], "values": []}
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT proc_date, SUM(COALESCE(production, 0))
            FROM sd_procedures
            WHERE proc_date IS NOT NULL AND proc_date != '' AND COALESCE(production, 0) > 0
            GROUP BY proc_date
            ORDER BY proc_date
            """
        )
        rows = [(str(day), float(total or 0)) for day, total in cur.fetchall() if day]
        source = "sd_procedures"
        if not rows and _table_exists(conn, "daysheet_totals"):
            cur.execute(
                """
                SELECT year_month, SUM(COALESCE(gross_production, net_production, 0))
                FROM daysheet_totals
                WHERE COALESCE(gross_production, net_production, 0) > 0
                GROUP BY year_month
                ORDER BY year_month
                """
            )
            rows = [(str(period), float(total or 0)) for period, total in cur.fetchall() if period]
            source = "daysheet_totals"
    finally:
        conn.close()
    trimmed = rows[-limit:]
    return {
        "hasData": bool(trimmed),
        "labels": [day for day, _ in trimmed],
        "values": [round(total, 2) for _, total in trimmed],
        "points": [{"date": day, "production": round(total, 2)} for day, total in trimmed],
        "source": source,
        "dbPath": str(db_path),
    }


def _parse_ar_money(value: Any) -> float | None:
    raw = str(value or "").replace("$", "").replace(",", "").strip()
    if not raw or raw in {"—", "-", "N/A", "na", "null"}:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _normalize_ar_bucket_label(label: str) -> str:
    low = label.strip().lower().replace("–", "-")
    if low in {"current", "0-30", "net 30", "current balance"}:
        return "0-30"
    if low in {"31-60", "30-60"} or low.startswith("31") or "31-60" in low:
        return "31-60"
    if low in {"61-90", "60-90"} or low.startswith("61") or "61-90" in low:
        return "61-90"
    if low in {"90+", "91+", "90-plus", "120+"} or low.startswith("90") or low.startswith("120"):
        return "90+"
    return label.strip() or "Unknown"


def ar_aging() -> dict[str, Any]:
    """SoftDent A/R bucket totals from import cache CSV (empty ≠ $0 · read-only)."""
    import csv
    from pathlib import Path

    from import_loader import softdent_import_dir

    empty: dict[str, Any] = {
        "hasData": False,
        "buckets": [],
        "source": "softdent_ar_aging.csv",
        "honesty": "empty != $0",
    }
    candidates = [
        softdent_import_dir() / "softdent_ar_aging.csv",
        softdent_import_dir() / "softdent_ar_aging.json",
    ]
    path: Path | None = next((p for p in candidates if p.is_file()), None)
    if path is None:
        empty["error"] = "missing"
        return empty

    buckets: list[dict[str, Any]] = []
    try:
        if path.suffix.lower() == ".json":
            import json

            payload = json.loads(path.read_text(encoding="utf-8-sig"))
            rows = payload if isinstance(payload, list) else (payload.get("rows") if isinstance(payload, dict) else [])
            for row in rows if isinstance(rows, list) else []:
                if not isinstance(row, dict):
                    continue
                amt = _parse_ar_money(row.get("Balance") or row.get("balance") or row.get("amount"))
                if amt is None:
                    continue
                label = _normalize_ar_bucket_label(str(row.get("Bucket") or row.get("bucket") or "Unknown"))
                buckets.append({"bucket": label, "amount": round(amt, 2)})
        else:
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                for row in reader:
                    if not isinstance(row, dict):
                        continue
                    amt = _parse_ar_money(row.get("Balance") or row.get("balance") or row.get("Amount"))
                    if amt is None:
                        continue
                    label = _normalize_ar_bucket_label(str(row.get("Bucket") or row.get("bucket") or "Unknown"))
                    buckets.append({"bucket": label, "amount": round(amt, 2)})
    except Exception as exc:
        empty["error"] = str(exc)
        return empty

    if not buckets:
        empty["error"] = "empty_file"
        empty["path"] = str(path)
        return empty

    # Merge duplicate labels (Current + 0-30) without inventing missing buckets.
    merged: dict[str, float] = {}
    order: list[str] = []
    for item in buckets:
        key = str(item["bucket"])
        if key not in merged:
            order.append(key)
            merged[key] = 0.0
        merged[key] += float(item["amount"])
    preferred = ["0-30", "31-60", "61-90", "90+"]
    ordered = [b for b in preferred if b in merged] + [b for b in order if b not in preferred]
    out_buckets = [{"bucket": b, "amount": round(merged[b], 2)} for b in ordered]
    total = round(sum(merged.values()), 2)
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    age_hours = round((datetime.now(timezone.utc) - mtime).total_seconds() / 3600.0, 2)
    stale = age_hours > 24.0
    return {
        "hasData": True,
        "buckets": out_buckets,
        "total": total,
        "source": path.name,
        "path": str(path),
        "mtime": mtime.replace(microsecond=0).isoformat(),
        "ageHours": age_hours,
        "stale": stale,
        "honesty": "empty != $0",
    }
