"""SoftDent master report list — DB first; Sign On + UI Excel only when DB cannot supply.

The master program (NR2 / HAL / daily pull) uses this catalog to know:
1. Prefer SoftDent database / ODBC / Sensei / sd_* when rows exist.
2. For reports marked guiRequiredWhenMissing, SoftDent Sign On + UI Excel export
   is the only recovery path — never invent dollars.
3. verify_master_reports() audits catalog completeness, DB reachability, and inbox files.
"""

from __future__ import annotations

import json
import logging
from datetime import date
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

MASTER_PATH = Path(__file__).resolve().parent / "softdent_master_reports.json"
EXPORT_ROOT = Path(r"C:\SoftDentReportExports")
MENU_MAP_PATH = Path(__file__).resolve().parent / "softdent_gui_menu_map.json"


def load_master_reports(path: Path | None = None) -> dict[str, Any]:
    target = path or MASTER_PATH
    if not target.is_file():
        raise FileNotFoundError(f"SoftDent master reports missing: {target}")
    return json.loads(target.read_text(encoding="utf-8-sig"))


def master_report_ids(*, required_only: bool = False) -> list[str]:
    catalog = load_master_reports()
    order = list(catalog.get("masterOrder") or [])
    reports = catalog.get("reports") or {}
    out: list[str] = []
    for rid in order:
        meta = reports.get(rid) or {}
        if required_only and not bool(meta.get("requiredForFinancialClose", True)):
            continue
        out.append(rid)
    return out


def gui_export_ids_required() -> list[str]:
    """GUI catalog ids that SoftDent can file-export (Excel) for automated pull."""
    catalog = load_master_reports()
    reports = catalog.get("reports") or {}
    out: list[str] = []
    for rid in catalog.get("masterOrder") or []:
        meta = reports.get(rid) or {}
        if not bool(meta.get("guiRequiredWhenMissing")):
            continue
        if meta.get("outputMode") == "print_preview" or bool(meta.get("visualReadRequired")):
            # Print Preview–only: no automated Excel file ingest
            if not bool(meta.get("excelExport")):
                continue
        if bool(meta.get("excelExport")) is False and meta.get("outputMode") == "print_preview":
            continue
        gid = str(meta.get("guiExportId") or "").strip()
        if gid and bool(meta.get("excelExport", True)):
            out.append(gid)
    return out


def print_preview_report_ids() -> list[str]:
    """Reports that SoftDent only shows via Print Preview (visual read; no Excel file)."""
    catalog = load_master_reports()
    out: list[str] = []
    for rid in catalog.get("masterOrder") or []:
        meta = (catalog.get("reports") or {}).get(rid) or {}
        if meta.get("outputMode") == "print_preview" or (
            bool(meta.get("visualReadRequired")) and not bool(meta.get("excelExport"))
        ):
            out.append(rid)
    return out


def format_master_reports_hal_reply() -> str:
    catalog = load_master_reports()
    lines = [
        "SoftDent master retrieval: prefer database / ODBC / Sensei / sd_* when available.",
        "If that info cannot be reached by the database, Sign On and use SoftDent UI.",
        "Excel-capable reports: click Excel then Enter and NR2 parses the file (e.g. Register Productions/Collections/Ins Plan/Regular).",
        "Print Preview–only reports (no Excel): SoftDent pops Print Preview — visually read the figures; do not invent dollars.",
        "Master reports:",
    ]
    for rid in catalog.get("masterOrder") or []:
        meta = (catalog.get("reports") or {}).get(rid) or {}
        src = meta.get("preferredSource")
        label = meta.get("label") or rid
        mode = meta.get("outputMode") or src
        if src == "database":
            lines.append(f"- {rid}: {label} (DB/Sensei preferred).")
        elif mode == "print_preview" or bool(meta.get("visualReadRequired")):
            path = meta.get("guiMenuPath") or "SoftDent UI"
            lines.append(
                f"- {rid}: {label} — Print Preview only → open in SoftDent and visually read ({path})."
            )
        else:
            path = meta.get("guiMenuPath") or meta.get("guiWin32Path") or "SoftDent UI"
            lines.append(f"- {rid}: {label} — Excel GUI when missing → {path}.")
    return " ".join(lines)


def _inbox_matches(patterns: list[str], *, inbox: Path) -> list[str]:
    if not inbox.is_dir():
        return []
    found: list[str] = []
    for pat in patterns:
        for hit in sorted(inbox.glob(pat)):
            if hit.is_file():
                found.append(hit.name)
    return found


def _db_table_counts() -> dict[str, Any]:
    info: dict[str, Any] = {
        "ok": False,
        "dbPath": None,
        "odbcConfigured": False,
        "tables": {},
        "error": None,
    }
    try:
        from softdent_odbc_extract import odbc_configured, resolve_sd_sqlite_db

        info["odbcConfigured"] = bool(odbc_configured())
        db = resolve_sd_sqlite_db()
        info["dbPath"] = str(db) if db else None
        if not db or not db.is_file():
            info["error"] = "sd_sqlite_missing"
            return info
        import sqlite3

        con = sqlite3.connect(str(db))
        try:
            cur = con.cursor()
            for name in (
                "sd_providers",
                "sd_patients",
                "sd_procedures",
                "sd_appointments",
                "sd_claims",
                "sd_payments",
                "sd_adjustments",
                "sd_patient_insurance",
            ):
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {name}")
                    info["tables"][name] = int(cur.fetchone()[0])
                except Exception:
                    info["tables"][name] = None
        finally:
            con.close()
        info["ok"] = any(isinstance(v, int) and v > 0 for v in info["tables"].values())
    except Exception as exc:  # noqa: BLE001
        info["error"] = f"{type(exc).__name__}:{exc}"
    return info


def verify_master_reports(
    *,
    start: date | None = None,
    end: date | None = None,
    inbox: Path | None = None,
    require_inbox_files: bool = False,
) -> dict[str, Any]:
    """Verify master catalog integrity + DB/inbox coverage (no SoftDent UI clicks)."""
    catalog = load_master_reports()
    inbox_root = inbox or Path(str(catalog.get("exportInbox") or EXPORT_ROOT))
    menu: dict[str, Any] = {}
    if MENU_MAP_PATH.is_file():
        menu = json.loads(MENU_MAP_PATH.read_text(encoding="utf-8-sig"))
    menu_reports = menu.get("reports") or {}

    db = _db_table_counts()
    items: dict[str, Any] = {}
    missing_gui: list[str] = []
    missing_db: list[str] = []
    catalog_gaps: list[str] = []

    for rid in catalog.get("masterOrder") or []:
        meta = (catalog.get("reports") or {}).get(rid)
        if not isinstance(meta, dict):
            catalog_gaps.append(rid)
            continue
        entry: dict[str, Any] = {
            "id": rid,
            "label": meta.get("label"),
            "preferredSource": meta.get("preferredSource"),
            "guiRequiredWhenMissing": bool(meta.get("guiRequiredWhenMissing")),
            "requiredForFinancialClose": bool(meta.get("requiredForFinancialClose", True)),
            "ok": False,
            "sourceSatisfied": None,
            "nextStep": None,
        }
        if meta.get("preferredSource") == "database":
            tables = list(meta.get("dbTables") or [])
            counts = {t: (db.get("tables") or {}).get(t) for t in tables}
            entry["dbCounts"] = counts
            populated = any(isinstance(v, int) and v > 0 for v in counts.values())
            entry["ok"] = populated
            entry["sourceSatisfied"] = "database" if populated else None
            if not populated:
                missing_db.append(rid)
                entry["nextStep"] = (
                    "Run SoftDent ODBC/Sensei extract (softdent_odbc_extract). "
                    "If still empty and a GUI export exists for the needed facts, Sign On + UI Excel."
                )
        else:
            gid = str(meta.get("guiExportId") or "").strip()
            entry["guiExportId"] = gid or None
            entry["guiMenuPath"] = meta.get("guiMenuPath")
            entry["outputMode"] = meta.get("outputMode")
            entry["excelExport"] = bool(meta.get("excelExport"))
            entry["visualReadRequired"] = bool(meta.get("visualReadRequired"))
            if gid and gid not in menu_reports and bool(meta.get("excelExport")):
                catalog_gaps.append(f"menu_map_missing:{gid}")
                entry["nextStep"] = f"Add {gid} to softdent_gui_menu_map.json"

            # Print Preview–only: SoftDent has no Excel file — visual read, not inbox ingest
            if meta.get("outputMode") == "print_preview" or (
                bool(meta.get("visualReadRequired")) and not bool(meta.get("excelExport"))
            ):
                entry["ok"] = True
                entry["sourceSatisfied"] = "print_preview_visual_read"
                entry["nextStep"] = (
                    "SoftDent Print Preview only (no Excel). Sign On → open "
                    f"{meta.get('guiMenuPath') or rid} → Print Preview and visually read "
                    "the figures. Do not invent dollars. Prefer Register Excel when it "
                    "already has production/collections/Ins Plan."
                )
                items[rid] = entry
                continue

            patterns = list(meta.get("canonicalPatterns") or [])
            # Prefer period-specific register when dates given
            if start and end and gid == "register":
                patterns = [
                    f"register_for_period_{start.isoformat()}_{end.isoformat()}.xls",
                    f"register_for_period_{start.isoformat()}_{end.isoformat()}.csv",
                    *patterns,
                ]
            hits = _inbox_matches(patterns, inbox=inbox_root)
            entry["inboxHits"] = hits[:12]
            entry["inboxHitCount"] = len(hits)
            # Optional DB assist note
            assist_tables = list(meta.get("dbTables") or [])
            if assist_tables:
                counts = {t: (db.get("tables") or {}).get(t) for t in assist_tables}
                entry["dbAssistCounts"] = counts
                if any(isinstance(v, int) and v > 0 for v in counts.values()):
                    entry["dbAssistOk"] = True
            if hits:
                entry["ok"] = True
                entry["sourceSatisfied"] = "gui_inbox"
            elif entry.get("dbAssistOk") and not require_inbox_files:
                entry["ok"] = True
                entry["sourceSatisfied"] = "database_assist"
            else:
                missing_gui.append(rid)
                entry["nextStep"] = (
                    "SoftDent Sign On + UI Excel export required "
                    f"({meta.get('guiMenuPath') or meta.get('guiWin32Path')}). "
                    "Click Excel then Enter; save under C:\\SoftDentReportExports."
                )
                if require_inbox_files:
                    entry["ok"] = False
                else:
                    # Catalog/menu wiring ok even if file not yet pulled
                    entry["ok"] = bool(gid and gid in menu_reports) or bool(meta.get("guiWin32Path"))
                    entry["pendingPull"] = True
        items[rid] = entry

    required_ids = [
        rid
        for rid, e in items.items()
        if e.get("requiredForFinancialClose")
    ]
    required_ok = all(bool(items[rid].get("ok")) for rid in required_ids) if required_ids else False
    # Stricter: required GUI reports must not be pending when require_inbox_files
    if require_inbox_files:
        required_ok = all(
            bool(items[rid].get("ok")) and not items[rid].get("pendingPull")
            for rid in required_ids
        )

    result = {
        "ok": required_ok and not catalog_gaps,
        "version": catalog.get("version"),
        "doctrine": catalog.get("doctrine"),
        "inbox": str(inbox_root),
        "period": {
            "start": start.isoformat() if start else None,
            "end": end.isoformat() if end else None,
        },
        "database": db,
        "reports": items,
        "missingGuiPulls": missing_gui,
        "missingDb": missing_db,
        "catalogGaps": catalog_gaps,
        "printPreviewOnly": print_preview_report_ids(),
        "guiExportIds": gui_export_ids_required(),
        "halSummary": format_master_reports_hal_reply(),
    }
    return result


def main() -> int:
    import argparse
    from datetime import date as date_cls

    today = date_cls.today()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default=f"{today.year:04d}-{today.month:02d}-01")
    parser.add_argument("--end", default=today.isoformat())
    parser.add_argument("--require-inbox", action="store_true")
    args = parser.parse_args()
    result = verify_master_reports(
        start=date_cls.fromisoformat(args.start),
        end=date_cls.fromisoformat(args.end),
        require_inbox_files=bool(args.require_inbox),
    )
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
