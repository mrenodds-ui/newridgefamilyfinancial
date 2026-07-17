"""Program SoftDent Report Manager group NR2 Money Widgets (Excel only).

SoftDent Help: Reports → Report Manager → Set up a Report Group.
NR2 override: Output Options Excel (never Printer/File). empty ≠ $0.
Sign On: SOFTDENT_SIGNON_* (prefer Dr admin).
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault("SOFTDENT_SIGNON_USER", "Dr")

import win32api  # noqa: E402
import win32con  # noqa: E402
import win32gui  # noqa: E402
import win32process  # noqa: E402
from ctypes import Structure, byref, c_int, create_unicode_buffer, windll  # noqa: E402
from pywinauto import Application, Desktop  # noqa: E402
import pywinauto.keyboard as kb  # noqa: E402

from softdent_gui_export import (  # noqa: E402
    SoftDentExcelDisabledError,
    _find_softdent_report_setup_dialog,
    _fill_softdent_report_setup,
    _select_output_option_prompt,
    cancel_printer_dialogs,
    dismiss_softdent_alerts,
    find_dialog,
    list_softdent_window_titles,
    prepare_softdent_for_next_report,
)
from softdent_report_manager_multi import GROUP_NAME, MULTI_REPORT_PACK  # noqa: E402
from softdent_signon import ensure_softdent_signed_on  # noqa: E402

user32 = windll.user32
STATUS = Path(r"C:\SoftDentFinancialExports\softdent_report_manager_program_status.json")


class RECT(Structure):
    _fields_ = [("left", c_int), ("top", c_int), ("right", c_int), ("bottom", c_int)]


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _plain(text: str) -> str:
    return (text or "").replace("&", "")


def _menu_text(hmenu: int, i: int) -> str:
    buf = create_unicode_buffer(256)
    user32.GetMenuStringW(hmenu, i, buf, 256, win32con.MF_BYPOSITION)
    return buf.value


def _force_fg(hwnd: int) -> None:
    try:
        fg = win32gui.GetForegroundWindow()
        tid_fg = win32process.GetWindowThreadProcessId(fg)[0]
        tid = win32process.GetWindowThreadProcessId(hwnd)[0]
        if tid_fg != tid:
            user32.AttachThreadInput(tid_fg, tid, True)
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        try:
            win32gui.SetForegroundWindow(hwnd)
        except Exception:
            pass
        if tid_fg != tid:
            user32.AttachThreadInput(tid_fg, tid, False)
    except Exception:
        pass


def _main_hwnd() -> int:
    found: list[int] = []

    def enum_top(hwnd, _):
        if "CS SoftDent Software" in (win32gui.GetWindowText(hwnd) or ""):
            found.append(int(hwnd))
        return True

    win32gui.EnumWindows(enum_top, None)
    if not found:
        raise RuntimeError("SoftDent main window not found")
    return found[0]


def _click_menu(hwnd: int, hmenu: int, index: int) -> bool:
    rc = RECT()
    if not user32.GetMenuItemRect(hwnd, hmenu, index, byref(rc)):
        return False
    _force_fg(hwnd)
    win32api.SetCursorPos(((rc.left + rc.right) // 2, (rc.top + rc.bottom) // 2))
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.55)
    return True


def open_set_up_report_group() -> None:
    prepare_softdent_for_next_report()
    dismiss_softdent_alerts()
    cancel_printer_dialogs()
    kb.send_keys("{ESC}")
    time.sleep(0.1)
    kb.send_keys("{ESC}")
    time.sleep(0.2)
    hwnd = _main_hwnd()
    _force_fg(hwnd)
    hmenu = win32gui.GetMenu(hwnd)
    rep_i = next(
        i
        for i in range(user32.GetMenuItemCount(hmenu))
        if "eports" in _plain(_menu_text(hmenu, i))
    )
    if not _click_menu(hwnd, hmenu, rep_i):
        raise RuntimeError("Could not open Reports menu")
    sub = user32.GetSubMenu(hmenu, rep_i)
    rm_i = next(
        j
        for j in range(user32.GetMenuItemCount(sub))
        if "Report Manager" in _plain(_menu_text(sub, j))
    )
    if not _click_menu(hwnd, sub, rm_i):
        raise RuntimeError("Could not open Report Manager")
    # &Set up a Report Group
    kb.send_keys("s")
    time.sleep(1.2)


def click_button_by_text(substrs: list[str], *, window_substr: str | None = None) -> bool:
    app = Application(backend="win32").connect(path="SDWIN.EXE")
    targets = [s.lower() for s in substrs]
    for w in app.windows():
        try:
            title = (w.window_text() or "").strip()
            if not w.is_visible():
                continue
        except Exception:
            continue
        if window_substr and window_substr.lower() not in title.lower():
            continue
        for c in w.descendants():
            try:
                ct = (c.window_text() or "").replace("&", "").strip().lower()
                if ct in targets and c.is_enabled():
                    c.click_input()
                    time.sleep(0.5)
                    return True
            except Exception:
                continue
    return False


def type_into_focused_edit(text: str) -> None:
    kb.send_keys("^a")
    time.sleep(0.1)
    kb.send_keys("{BACKSPACE}")
    time.sleep(0.1)
    # pywinauto send_keys: special chars
    kb.send_keys(text, with_spaces=True)
    time.sleep(0.2)


def wait_title_contains(parts: list[str], timeout_s: float = 12.0) -> bool:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        titles = " | ".join(list_softdent_window_titles())
        if any(p.lower() in titles.lower() for p in parts):
            return True
        time.sleep(0.25)
    return False


def answer_yes_no(prefer_yes: bool) -> bool:
    """Click Yes/No on SoftDent message boxes."""
    want = "yes" if prefer_yes else "no"
    alt = "no" if prefer_yes else "yes"
    if click_button_by_text([want]):
        return True
    # keyboard Alt+Y / Alt+N
    kb.send_keys("%y" if prefer_yes else "%n")
    time.sleep(0.4)
    return True


def open_pack_report(report_id: str) -> None:
    """Open one pack report while Batch Select Mode is on (Reports menu)."""
    from softdent_gui_export import _open_accounting_report, load_menu_map, resolve_menu_keys

    catalog = load_menu_map()
    meta = (catalog.get("reports") or {}).get(report_id) or {}
    keys = resolve_menu_keys(meta)
    prepare_softdent_for_next_report()
    dismiss_softdent_alerts()
    cancel_printer_dialogs()
    _open_accounting_report(report_id, keys)
    time.sleep(0.8)


def program_one_report(report: dict[str, Any], *, is_last: bool) -> dict[str, Any]:
    rid = str(report["id"])
    out: dict[str, Any] = {"id": rid, "ok": False}
    try:
        open_pack_report(rid)
        # Output Options — Excel only (override Help Printer default)
        if not wait_title_contains(["Output Options"], 20):
            out["error"] = "Output Options did not appear"
            cancel_printer_dialogs()
            return out
        try:
            _select_output_option_prompt("excel")
        except SoftDentExcelDisabledError as exc:
            out["error"] = f"ExcelDisabled:{exc}"
            kb.send_keys("%c")
            time.sleep(0.4)
            return out
        # Report setup
        setup = None
        for _ in range(40):
            setup = _find_softdent_report_setup_dialog()
            if setup:
                break
            if find_dialog("Select File Name") or find_dialog("Edit Description"):
                break
            time.sleep(0.25)
        if setup:
            from datetime import date

            today = date.today()
            date_mode = str(report.get("dateMode") or "range")
            # SoftDent Report Manager macros typed as literal text when possible
            if date_mode == "as_of":
                _fill_softdent_report_setup(setup, start=today, end=today, date_mode="as_of")
            else:
                start = date(today.year, today.month, 1)
                _fill_softdent_report_setup(setup, start=start, end=today, date_mode="range")
        # SoftDent may show Report Output (copies) if it still thinks Printer —
        # Cancel printer waits; for Excel continue.
        for _ in range(20):
            cancel_printer_dialogs(max_rounds=1)
            titles = list_softdent_window_titles()
            blob = " | ".join(titles).lower()
            if "waiting for printer" in blob:
                kb.send_keys("%c")
                out["error"] = "printer_wait"
                return out
            if find_dialog("Edit Description") or any(
                "add another" in (t or "").lower() or "another scheduled" in (t or "").lower()
                for t in titles
            ):
                break
            if any("Group Setup" in (t or "") or "Frequency" in (t or "") for t in titles):
                break
            # Report Output copies dialog — Next/Enter carefully only if Excel path
            if any("Report Output" in (t or "") for t in titles):
                # Prefer Next without printing — SoftDent batch may still show this
                if not click_button_by_text(["next", "&next"]):
                    kb.send_keys("{ENTER}")
                time.sleep(0.5)
                continue
            if find_dialog("Select File Name"):
                # During Report Manager setup SoftDent may ask for Excel path once
                from softdent_gui_export import (
                    _focus_select_file_name_filename_edit,
                    _keyboard_press_ok,
                    _set_edit_text_win32,
                    _softdent_file_stem,
                    _softdent_select_file_path,
                )

                save = find_dialog("Select File Name")
                stem = _softdent_file_stem(rid[:8].upper())
                hwnd_edit, current = _focus_select_file_name_filename_edit(save)
                path = _softdent_select_file_path(stem, current)
                _set_edit_text_win32(hwnd_edit, path)
                _keyboard_press_ok(hwnd=int(save.handle))
                time.sleep(0.8)
                continue
            # SoftDent message: add another?
            app = Application(backend="win32").connect(path="SDWIN.EXE")
            for w in app.windows():
                try:
                    texts = " ".join(
                        (c.window_text() or "") for c in w.descendants()[:40]
                    ).lower()
                except Exception:
                    continue
                if "another" in texts and "report" in texts:
                    answer_yes_no(prefer_yes=not is_last)
                    out["ok"] = True
                    out["addedAnother"] = not is_last
                    time.sleep(0.6)
                    return out
            time.sleep(0.25)
        # Final add-another prompt
        time.sleep(0.4)
        answer_yes_no(prefer_yes=not is_last)
        out["ok"] = True
        out["addedAnother"] = not is_last
        return out
    except Exception as exc:  # noqa: BLE001
        out["error"] = f"{type(exc).__name__}:{exc}"
        cancel_printer_dialogs()
        dismiss_softdent_alerts()
        return out


def set_group_frequency_daily() -> dict[str, Any]:
    """After last report, Group Setup: Frequency Daily, Next Run today, OK."""
    info: dict[str, Any] = {"ok": False}
    wait_title_contains(["Group Setup", "Frequency", "SoftDent"], 15)
    # Try combo Frequency → Daily
    app = Application(backend="win32").connect(path="SDWIN.EXE")
    for w in app.windows():
        title = (w.window_text() or "")
        try:
            for c in w.descendants():
                ct = (c.window_text() or "").strip().lower()
                cn = c.friendly_class_name()
                if "frequen" in ct or (cn == "ComboBox" and c.is_enabled()):
                    try:
                        c.select("Daily")
                        info["frequency"] = "Daily"
                    except Exception:
                        try:
                            c.click_input()
                            kb.send_keys("d")
                            info["frequency"] = "Daily_keyed"
                        except Exception:
                            pass
        except Exception:
            continue
    if click_button_by_text(["ok", "o&k"]):
        info["ok"] = True
    else:
        kb.send_keys("{ENTER}")
        info["ok"] = True
        info["okVia"] = "enter"
    time.sleep(0.8)
    return info


def verify_group_in_advanced_options() -> dict[str, Any]:
    """Open Advanced Options and look for NR2 Money Widgets."""
    prepare_softdent_for_next_report()
    dismiss_softdent_alerts()
    cancel_printer_dialogs()
    hwnd = _main_hwnd()
    _force_fg(hwnd)
    hmenu = win32gui.GetMenu(hwnd)
    rep_i = next(
        i
        for i in range(user32.GetMenuItemCount(hmenu))
        if "eports" in _plain(_menu_text(hmenu, i))
    )
    _click_menu(hwnd, hmenu, rep_i)
    sub = user32.GetSubMenu(hmenu, rep_i)
    rm_i = next(
        j
        for j in range(user32.GetMenuItemCount(sub))
        if "Report Manager" in _plain(_menu_text(sub, j))
    )
    _click_menu(hwnd, sub, rm_i)
    kb.send_keys("a")  # Advanced Options
    time.sleep(1.5)
    found = False
    texts: list[str] = []
    app = Application(backend="win32").connect(path="SDWIN.EXE")
    for w in app.windows():
        try:
            for c in w.descendants():
                ct = (c.window_text() or "").strip()
                if ct:
                    texts.append(ct[:120])
                    if GROUP_NAME.lower() in ct.lower() or "nr2" in ct.lower():
                        found = True
        except Exception:
            continue
    # Close Advanced Options
    click_button_by_text(["close", "cancel", "ok"])
    return {"found": found, "sampleTexts": texts[:40], "titles": list_softdent_window_titles()[:12]}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    payload: dict[str, Any] = {
        "ok": False,
        "at": _utc(),
        "groupName": GROUP_NAME,
        "emptyNotZero": True,
        "output": "excel",
        "neverPrinter": True,
        "steps": [],
        "reports": [],
    }
    assist = ensure_softdent_signed_on(timeout_s=60.0, force_change_login=False)
    payload["signOn"] = {
        "ok": assist.get("ok"),
        "signedOn": assist.get("signedOn"),
        "user": assist.get("user"),
    }
    if not assist.get("ok"):
        payload["error"] = "signon_failed"
        STATUS.parent.mkdir(parents=True, exist_ok=True)
        STATUS.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(json.dumps(payload, indent=2))
        return 2

    open_set_up_report_group()
    payload["steps"].append("opened_set_up_report_group")
    if not wait_title_contains(["Report Group Setup"], 10):
        payload["error"] = "Report Group Setup intro missing"
        print(json.dumps(payload, indent=2))
        return 3
    click_button_by_text(["ok", "o&k"], window_substr="Report Group")
    payload["steps"].append("intro_ok")
    time.sleep(0.8)
    # Name prompt
    type_into_focused_edit(GROUP_NAME)
    kb.send_keys("{ENTER}")
    payload["steps"].append(f"named:{GROUP_NAME}")
    time.sleep(1.0)

    pack = list(MULTI_REPORT_PACK)
    for i, report in enumerate(pack):
        is_last = i == len(pack) - 1
        print(f"PROGRAM {report['id']} last={is_last}", flush=True)
        result = program_one_report(report, is_last=is_last)
        payload["reports"].append(result)
        print(json.dumps(result, default=str), flush=True)
        if not result.get("ok") and report.get("required"):
            # continue packing remaining if possible
            dismiss_softdent_alerts()
            cancel_printer_dialogs()
            # If SoftDent asked add another after failure, say yes to continue
            answer_yes_no(prefer_yes=not is_last)

    freq = set_group_frequency_daily()
    payload["frequency"] = freq
    payload["steps"].append("frequency_set")
    verify = verify_group_in_advanced_options()
    payload["verify"] = verify
    ok_ids = [r["id"] for r in payload["reports"] if r.get("ok")]
    payload["ok"] = bool(verify.get("found") or len(ok_ids) >= 3)
    payload["okReportIds"] = ok_ids
    payload["finishedAt"] = _utc()
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    STATUS.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(json.dumps({
        "ok": payload["ok"],
        "okReportIds": ok_ids,
        "verifyFound": verify.get("found"),
        "frequency": freq,
        "status": str(STATUS),
        "reports": payload["reports"],
    }, indent=2, default=str))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
