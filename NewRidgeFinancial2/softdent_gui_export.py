"""SoftDent GUI report export helpers (read-only; no SoftDent write-back).

For SoftDent data that cannot be reached via ODBC/database extract, Sign On and use
the SoftDent UI to export reports (Register / Collections / daysheet), then ingest.

Drives SDWIN menus to export Register / Collections reports into
C:\\SoftDentReportExports. Credentials are never handled here — use softdent_signon.
"""

from __future__ import annotations

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
        # Common when SoftDent is elevated differently — click taskbar via ShowWindow then retry.
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


def _complete_output_setup_and_save(
    *,
    start: date,
    end: date,
    short_stem: str,
    dest_root: Path,
    canonical_name: str,
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
    if MIRROR_ROOT.is_dir():
        try:
            shutil.copy2(produced, MIRROR_ROOT / canonical.name)
            shutil.copy2(produced, MIRROR_ROOT / produced.name)
        except OSError as exc:
            logger.warning("SoftDent export mirror copy failed: %s", type(exc).__name__)
    return canonical


def export_register_for_period(
    *,
    start: date,
    end: date,
    dest_root: Path | None = None,
) -> Path:
    """Reports → Accounting → Registers → Period → Excel."""
    dest = dest_root or EXPORT_ROOT
    _open_report_via_keys("rp")
    stem = f"REG{start.year % 100:02d}{start.month:02d}"
    canonical = f"register_for_period_{start.isoformat()}_{end.isoformat()}.xls"
    return _complete_output_setup_and_save(
        start=start,
        end=end,
        short_stem=stem,
        dest_root=dest,
        canonical_name=canonical,
    )


def export_collections_for_period(
    *,
    start: date,
    end: date,
    dest_root: Path | None = None,
    menu_keys: str | None = None,
) -> Path:
    """Reports → Accounting → Collections (keys configurable).

    Default keys after Accounting: env SOFTDENT_COLLECTIONS_MENU_KEYS or 'c'.
    SoftDent menus vary by version — set the env if 'c' is wrong.
    """
    dest = dest_root or EXPORT_ROOT
    keys = (menu_keys or str(os.environ.get("SOFTDENT_COLLECTIONS_MENU_KEYS") or "c")).strip() or "c"
    _open_report_via_keys(keys)
    stem = f"COL{start.year % 100:02d}{start.month:02d}"
    canonical = f"collections_for_period_{start.isoformat()}_{end.isoformat()}.xls"
    return _complete_output_setup_and_save(
        start=start,
        end=end,
        short_stem=stem,
        dest_root=dest,
        canonical_name=canonical,
    )


def run_safe_period_exports(
    *,
    start: date | None = None,
    end: date | None = None,
    do_register: bool = True,
    do_collections: bool = True,
    ensure_signon: bool = True,
) -> dict[str, Any]:
    """Sign-on assist (optional) + Register/Collections exports. Never returns password."""
    today = date.today()
    start = start or date(today.year, today.month, 1)
    end = end or today
    result: dict[str, Any] = {
        "ok": False,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "signOn": None,
        "registerPath": None,
        "collectionsPath": None,
        "errors": [],
    }
    if ensure_signon:
        try:
            from softdent_signon import ensure_softdent_signed_on, softdent_signon_status

            status = softdent_signon_status()
            assist = ensure_softdent_signed_on(timeout_s=15.0, force_change_login=False)
            result["signOn"] = {
                "user": status.get("user"),
                "passwordConfigured": bool(status.get("passwordConfigured")),
                "signedOn": bool(assist.get("signedOn")),
                "assistOk": bool(assist.get("ok")),
                "steps": assist.get("steps"),
                "error": assist.get("error"),
            }
        except Exception as exc:  # noqa: BLE001
            result["errors"].append(f"signon:{type(exc).__name__}")
            result["signOn"] = {"ok": False, "error": type(exc).__name__}

    if do_register:
        try:
            path = export_register_for_period(start=start, end=end)
            result["registerPath"] = str(path)
        except Exception as exc:  # noqa: BLE001
            result["errors"].append(f"register:{type(exc).__name__}:{exc}")
            logger.warning("Register export failed: %s", type(exc).__name__)

    if do_collections:
        try:
            path = export_collections_for_period(start=start, end=end)
            result["collectionsPath"] = str(path)
        except Exception as exc:  # noqa: BLE001
            result["errors"].append(f"collections:{type(exc).__name__}:{exc}")
            logger.warning("Collections export failed: %s", type(exc).__name__)

    result["ok"] = bool(result.get("registerPath") or result.get("collectionsPath"))
    return result
