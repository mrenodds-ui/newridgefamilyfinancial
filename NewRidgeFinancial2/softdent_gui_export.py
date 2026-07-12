"""SoftDent GUI report export helpers (read-only; no SoftDent write-back).

For SoftDent data that cannot be reached via ODBC/database extract, Sign On and use
the SoftDent UI to export reports (Register / Collections / daysheet / aging / trans),
then ingest.

Drives SDWIN menus into C:\\SoftDentReportExports. Credentials are never handled
here — use softdent_signon. Menu keys come from softdent_gui_menu_map.json.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import time
from datetime import date
from pathlib import Path
from typing import Any, Iterable

logger = logging.getLogger(__name__)

EXPORT_ROOT = Path(r"C:\SoftDentReportExports")
EXPORT_ROOT_SHORT = r"C:\SOFTDE~1"  # SoftDent save dialog rejects some long paths
MIRROR_ROOT = Path(r"C:\SoftDent\softdentexportreports")
STATUS_ROOT = Path(r"C:\SoftDentFinancialExports")
MENU_MAP_PATH = Path(__file__).resolve().parent / "softdent_gui_menu_map.json"

PHASE1_IDS = ("register", "collections", "transactions", "daysheet", "aging")


def _desktop_dialogs() -> Iterable[Any]:
    from pywinauto import Desktop

    for w in Desktop(backend="win32").windows():
        try:
            if w.is_visible() and w.class_name() == "#32770":
                yield w
        except Exception:
            continue


def find_dialog(title: str):
    for w in _desktop_dialogs():
        if w.window_text() == title:
            return w
    return None


def dismiss_softdent_alerts(*, max_rounds: int = 6) -> int:
    """Click OK/Cancel on SoftDent message boxes. Returns dismiss count."""
    from pywinauto import Application

    dismissed = 0
    for _ in range(max_rounds):
        hit = False
        for w in list(_desktop_dialogs()):
            title = (w.window_text() or "").strip()
            if title not in {"SoftDent", ""}:
                continue
            try:
                app = Application(backend="win32").connect(handle=w.handle)
                dlg = app.window(handle=w.handle)
                for name in ("OK", "&OK", "Cancel", "&Cancel", "Close"):
                    try:
                        btn = dlg.child_window(title=name, class_name="Button")
                        if btn.exists(timeout=0.15):
                            btn.click_input()
                            dismissed += 1
                            hit = True
                            time.sleep(0.25)
                            break
                    except Exception:
                        continue
            except Exception:
                continue
        if not hit:
            break
    return dismissed


def softdent_main_running() -> bool:
    try:
        _main_softdent_hwnd()
        return True
    except Exception:
        return False


def _main_softdent_hwnd() -> int:
    from pywinauto.findwindows import find_windows
    import win32gui

    hwnds = find_windows(title_re=r".*SoftDent.*", backend="win32")
    if not hwnds:
        raise RuntimeError("SoftDent (SDWIN) is not running")
    for h in hwnds:
        cls = win32gui.GetClassName(h)
        title = win32gui.GetWindowText(h)
        if "SOFTDENT" in cls.upper() or "SoftDent Software" in title:
            return int(h)
    return int(hwnds[0])


def _click_named_button(dlg, name: str) -> None:
    from pywinauto import Application

    app = Application(backend="win32").connect(handle=dlg.handle)
    d = app.window(handle=dlg.handle)
    want = name.replace("&", "")
    for b in d.descendants(class_name="Button"):
        if b.window_text().replace("&", "") == want:
            b.click_input()
            return
    raise RuntimeError(f"Button not found: {name}")


def _focus_main():
    from pywinauto import Application
    from pywinauto.keyboard import send_keys
    import win32con
    import win32gui

    hwnd = _main_softdent_hwnd()
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    except Exception:
        pass
    try:
        win32gui.SetForegroundWindow(hwnd)
    except Exception:
        try:
            win32gui.BringWindowToTop(hwnd)
            win32gui.SetForegroundWindow(hwnd)
        except Exception:
            pass
    app = Application(backend="win32").connect(handle=hwnd)
    win = app.window(handle=hwnd)
    try:
        win.set_focus()
    except Exception:
        try:
            win.click_input()
        except Exception:
            pass
    time.sleep(0.35)
    dismiss_softdent_alerts()
    send_keys("{ESC}{ESC}")
    time.sleep(0.2)
    return win


def _open_report_via_keys(keys_after_reports_accounting: str) -> None:
    """Alt+R, A, then caller keys (e.g. 'rp' = Registers→Period, 'c' = Collections)."""
    from pywinauto.keyboard import send_keys

    _focus_main()
    send_keys("%r")
    time.sleep(0.4)
    send_keys("a")
    time.sleep(0.4)
    for ch in keys_after_reports_accounting:
        if ch.isspace():
            continue
        send_keys(ch)
        time.sleep(0.35)
    time.sleep(0.8)


def load_menu_map(path: Path | None = None) -> dict[str, Any]:
    map_path = path or MENU_MAP_PATH
    if not map_path.is_file():
        raise FileNotFoundError(f"SoftDent GUI menu map missing: {map_path}")
    return json.loads(map_path.read_text(encoding="utf-8-sig"))


def resolve_menu_keys(report: dict[str, Any], override: str | None = None) -> str:
    if override and str(override).strip():
        return str(override).strip()
    env_name = str(report.get("menu_keys_env") or "").strip()
    if env_name:
        env_val = str(os.environ.get(env_name) or "").strip()
        if env_val:
            return env_val
    keys = str(report.get("menu_keys") or "").strip()
    if not keys:
        raise RuntimeError(f"No menu_keys for report {report.get('id')}")
    return keys


def _format_stem(template: str, start: date, end: date) -> str:
    return (
        template.replace("{yy}", f"{start.year % 100:02d}")
        .replace("{mm}", f"{start.month:02d}")
        .replace("{dd}", f"{end.day:02d}")
        .replace("{end_yy}", f"{end.year % 100:02d}")
        .replace("{end_mm}", f"{end.month:02d}")
        .replace("{end_dd}", f"{end.day:02d}")
    )


def _format_canonical(template: str, start: date, end: date) -> str:
    return (
        template.replace("{start}", start.isoformat())
        .replace("{end}", end.isoformat())
        .replace("{yy}", f"{start.year % 100:02d}")
        .replace("{mm}", f"{start.month:02d}")
        .replace("{dd}", f"{end.day:02d}")
    )


def _complete_output_setup_and_save(
    *,
    start: date,
    end: date,
    short_stem: str,
    dest_root: Path,
    canonical_name: str,
    also_copy_as: list[str] | None = None,
) -> Path:
    from pywinauto import Application

    dismiss_softdent_alerts()
    out = None
    for _ in range(40):
        out = find_dialog("Output Options")
        if out:
            break
        time.sleep(0.25)
    if not out:
        raise RuntimeError("Output Options dialog did not appear")

    app_out = Application(backend="win32").connect(handle=out.handle)
    d_out = app_out.window(handle=out.handle)
    excel_btns = [b for b in d_out.descendants(class_name="Button") if "Excel" in b.window_text()]
    if not excel_btns:
        raise RuntimeError("Excel output option not found")
    excel_btns[0].click_input()
    time.sleep(0.2)
    _click_named_button(out, "OK")
    time.sleep(1.0)

    setup = None
    for _ in range(50):
        setup = find_dialog("Report Setup")
        if setup:
            break
        time.sleep(0.25)
    if not setup:
        raise RuntimeError("Report Setup dialog did not appear")

    app_s = Application(backend="win32").connect(handle=setup.handle)
    d_s = app_s.window(handle=setup.handle)
    edits = d_s.descendants(class_name="Edit")
    if len(edits) < 3:
        raise RuntimeError("Report Setup missing date edits")
    start_txt = start.strftime("%m/%d/%y")
    end_txt = end.strftime("%m/%d/%y")
    edits[1].set_edit_text(start_txt)
    edits[2].set_edit_text(end_txt)
    if len(edits) > 3:
        edits[3].set_edit_text("999")  # all providers
    time.sleep(0.2)
    ok = [b for b in d_s.descendants(class_name="Button") if b.window_text().replace("&", "") == "OK"][0]
    ok.click_input()
    time.sleep(1.0)
    dismiss_softdent_alerts()

    save = None
    for _ in range(50):
        dismiss_softdent_alerts()
        save = find_dialog("Select File Name")
        if save:
            break
        time.sleep(0.25)
    if not save:
        raise RuntimeError("Select File Name dialog did not appear")

    short_path = rf"{EXPORT_ROOT_SHORT}\{short_stem}"
    app_save = Application(backend="win32").connect(handle=save.handle)
    d_save = app_save.window(handle=save.handle)
    edits = d_save.descendants(class_name="Edit")
    edits[0].set_edit_text(short_path)
    time.sleep(0.2)
    ok = [b for b in d_save.descendants(class_name="Button") if b.window_text().replace("&", "") == "OK"][0]
    ok.click_input()
    time.sleep(3.0)
    dismiss_softdent_alerts()

    dest_root.mkdir(parents=True, exist_ok=True)
    produced = dest_root / f"{short_stem}.XLS"
    if not produced.is_file():
        for cand in dest_root.glob(f"{short_stem}.*"):
            produced = cand
            break
    if not produced.is_file():
        raise RuntimeError(f"Expected export not found under {dest_root} ({short_stem}.*)")

    canonical = dest_root / canonical_name
    shutil.copy2(produced, canonical)
    for extra in also_copy_as or []:
        try:
            shutil.copy2(produced, dest_root / extra)
        except OSError as exc:
            logger.warning("SoftDent extra copy %s failed: %s", extra, type(exc).__name__)
    if MIRROR_ROOT.is_dir():
        try:
            shutil.copy2(produced, MIRROR_ROOT / canonical.name)
            shutil.copy2(produced, MIRROR_ROOT / produced.name)
            for extra in also_copy_as or []:
                shutil.copy2(produced, MIRROR_ROOT / extra)
        except OSError as exc:
            logger.warning("SoftDent export mirror copy failed: %s", type(exc).__name__)
    return canonical


def export_report_by_id(
    report_id: str,
    *,
    start: date,
    end: date,
    dest_root: Path | None = None,
    menu_keys: str | None = None,
    menu_map: dict[str, Any] | None = None,
) -> Path:
    """Export one catalog report by id using softdent_gui_menu_map.json."""
    catalog = menu_map or load_menu_map()
    reports = catalog.get("reports") or {}
    report = reports.get(report_id)
    if not isinstance(report, dict):
        raise KeyError(f"Unknown SoftDent GUI report id: {report_id}")

    dest = dest_root or EXPORT_ROOT
    date_mode = str(report.get("date_mode") or "range")
    use_start, use_end = start, end
    if date_mode == "as_of":
        use_start = end
        use_end = end

    keys = resolve_menu_keys(report, menu_keys)
    _open_report_via_keys(keys)
    stem = _format_stem(str(report.get("short_stem_template") or "RPT"), use_start, use_end)
    canonical = _format_canonical(
        str(report.get("canonical_template") or f"{report_id}.xls"),
        use_start,
        use_end,
    )
    also = [str(x) for x in (report.get("also_copy_as") or []) if str(x).strip()]
    return _complete_output_setup_and_save(
        start=use_start,
        end=use_end,
        short_stem=stem,
        dest_root=dest,
        canonical_name=canonical,
        also_copy_as=also,
    )


def export_register_for_period(
    *,
    start: date,
    end: date,
    dest_root: Path | None = None,
) -> Path:
    """Reports → Accounting → Registers → Period → Excel."""
    return export_report_by_id("register", start=start, end=end, dest_root=dest_root)


def export_collections_for_period(
    *,
    start: date,
    end: date,
    dest_root: Path | None = None,
    menu_keys: str | None = None,
) -> Path:
    """Reports → Accounting → Collections (keys configurable)."""
    return export_report_by_id(
        "collections",
        start=start,
        end=end,
        dest_root=dest_root,
        menu_keys=menu_keys,
    )


def export_transactions_for_period(
    *,
    start: date,
    end: date,
    dest_root: Path | None = None,
    menu_keys: str | None = None,
) -> Path:
    return export_report_by_id(
        "transactions",
        start=start,
        end=end,
        dest_root=dest_root,
        menu_keys=menu_keys,
    )


def export_daysheet(
    *,
    start: date,
    end: date,
    dest_root: Path | None = None,
    menu_keys: str | None = None,
) -> Path:
    return export_report_by_id(
        "daysheet",
        start=start,
        end=end,
        dest_root=dest_root,
        menu_keys=menu_keys,
    )


def export_account_aging(
    *,
    as_of: date | None = None,
    dest_root: Path | None = None,
    menu_keys: str | None = None,
) -> Path:
    day = as_of or date.today()
    return export_report_by_id(
        "aging",
        start=day,
        end=day,
        dest_root=dest_root,
        menu_keys=menu_keys,
    )


def run_catalog_exports(
    *,
    start: date | None = None,
    end: date | None = None,
    report_ids: list[str] | None = None,
    ensure_signon: bool = True,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Run Phase-1 (or selected) SoftDent GUI exports. Never returns password."""
    today = date.today()
    start = start or date(today.year, today.month, 1)
    end = end or today
    catalog = load_menu_map()
    order = list(report_ids or catalog.get("phase1_order") or PHASE1_IDS)
    reports_meta = catalog.get("reports") or {}

    result: dict[str, Any] = {
        "ok": False,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "dryRun": bool(dry_run),
        "signOn": None,
        "reports": {},
        "errors": [],
        "requiredFailed": [],
    }

    if ensure_signon and not dry_run:
        try:
            from softdent_signon import ensure_softdent_signed_on, softdent_signon_status

            status = softdent_signon_status()
            assist = ensure_softdent_signed_on(timeout_s=60.0, force_change_login=False)
            result["signOn"] = {
                "user": status.get("user"),
                "passwordConfigured": bool(status.get("passwordConfigured")),
                "signedOn": bool(assist.get("signedOn")),
                "assistOk": bool(assist.get("ok")),
                "steps": assist.get("steps"),
                "error": assist.get("error"),
            }
            if not assist.get("ok") and not softdent_main_running():
                result["errors"].append("signon: SoftDent not signed on / not running")
        except Exception as exc:  # noqa: BLE001
            result["errors"].append(f"signon:{type(exc).__name__}")
            result["signOn"] = {"ok": False, "error": type(exc).__name__}

    for rid in order:
        meta = reports_meta.get(rid) if isinstance(reports_meta.get(rid), dict) else {}
        required = bool(meta.get("required", rid in PHASE1_IDS))
        entry: dict[str, Any] = {
            "id": rid,
            "required": required,
            "ok": False,
            "path": None,
            "menuKeys": resolve_menu_keys(meta) if meta else None,
            "label": meta.get("label"),
        }
        if dry_run:
            entry["ok"] = True
            entry["dryRun"] = True
            result["reports"][rid] = entry
            continue
        try:
            if not softdent_main_running():
                raise RuntimeError("SoftDent main window not available")
            path = export_report_by_id(rid, start=start, end=end, menu_map=catalog)
            entry["ok"] = True
            entry["path"] = str(path)
        except Exception as exc:  # noqa: BLE001
            msg = f"{rid}:{type(exc).__name__}:{exc}"
            entry["error"] = msg
            result["errors"].append(msg)
            if required:
                result["requiredFailed"].append(rid)
            logger.warning("SoftDent GUI export %s failed: %s", rid, type(exc).__name__)
            # Clear stuck dialogs before next report
            try:
                from pywinauto.keyboard import send_keys

                dismiss_softdent_alerts()
                send_keys("{ESC}{ESC}{ESC}")
            except Exception:
                pass
        result["reports"][rid] = entry

    required_ok = all(
        (result["reports"].get(rid) or {}).get("ok")
        for rid in order
        if bool((reports_meta.get(rid) or {}).get("required", rid in PHASE1_IDS))
    )
    any_ok = any(bool(v.get("ok") and v.get("path")) for v in result["reports"].values())
    result["ok"] = bool(required_ok) if not dry_run else True
    if dry_run:
        result["ok"] = True
    elif not required_ok and any_ok:
        # Partial: register alone may still be useful; ok stays False when required failed
        result["partialOk"] = True
    return result


def run_safe_period_exports(
    *,
    start: date | None = None,
    end: date | None = None,
    do_register: bool = True,
    do_collections: bool = True,
    ensure_signon: bool = True,
) -> dict[str, Any]:
    """Backward-compatible Register/Collections-only wrapper."""
    ids: list[str] = []
    if do_register:
        ids.append("register")
    if do_collections:
        ids.append("collections")
    full = run_catalog_exports(
        start=start,
        end=end,
        report_ids=ids or ["register"],
        ensure_signon=ensure_signon,
    )
    return {
        "ok": bool(full.get("ok") or full.get("partialOk")),
        "start": full.get("start"),
        "end": full.get("end"),
        "signOn": full.get("signOn"),
        "registerPath": (full.get("reports") or {}).get("register", {}).get("path"),
        "collectionsPath": (full.get("reports") or {}).get("collections", {}).get("path"),
        "errors": full.get("errors") or [],
    }
