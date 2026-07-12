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

# Never send SoftDent hotkeys / clicks to these (AMD Adrenalin steals focus on this PC).
_FOCUS_BLOCKLIST_SUBSTR = (
    "amd software",
    "adrenalin",
    "radeonsoftware",
    "radeon software",
    "intel® graphics",
    "intel graphics",
)


def _softdent_pids() -> set[int]:
    """PIDs for SDWIN.EXE only."""
    import subprocess

    out: set[int] = set()
    try:
        raw = subprocess.check_output(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "(Get-Process -Name SDWIN -ErrorAction SilentlyContinue).Id",
            ],
            text=True,
            timeout=15,
        )
    except Exception:
        return out
    for tok in raw.split():
        try:
            out.add(int(tok))
        except ValueError:
            continue
    return out


def _window_pid(hwnd: int) -> int | None:
    import win32process

    try:
        _, pid = win32process.GetWindowThreadProcessId(int(hwnd))
        return int(pid)
    except Exception:
        return None


def _is_blocked_focus_title(title: str) -> bool:
    lower = (title or "").strip().lower()
    return any(s in lower for s in _FOCUS_BLOCKLIST_SUBSTR)


def _minimize_focus_thieves() -> int:
    """Do NOT touch AMD windows (minimizing/activating can launch Adrenalin).

    SoftDent Reports must not use Alt+R — AMD Instant Replay steals that chord.
    Return 0 always; callers rely on SoftDent-only foreground + F10 menus.
    """
    return 0


def _force_foreground(hwnd: int) -> bool:
    """Reliable foreground activation (AttachThreadInput) for SoftDent only."""
    import ctypes
    import win32con
    import win32gui
    import win32process

    hwnd = int(hwnd)
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    except Exception:
        pass
    try:
        fg = win32gui.GetForegroundWindow()
        if fg == hwnd:
            return True
        # Never steal focus from / interact with AMD — wait and retry SoftDent only.
        fg_title = ""
        try:
            fg_title = win32gui.GetWindowText(fg) or ""
        except Exception:
            pass
        if _is_blocked_focus_title(fg_title):
            logger.warning("Foreground is focus thief %r — activating SoftDent without touching it", fg_title)
        cur_tid = win32process.GetWindowThreadProcessId(fg)[0] if fg else 0
        tgt_tid = win32process.GetWindowThreadProcessId(hwnd)[0]
        attached = False
        if cur_tid and tgt_tid and cur_tid != tgt_tid:
            attached = bool(ctypes.windll.user32.AttachThreadInput(cur_tid, tgt_tid, True))
        try:
            win32gui.BringWindowToTop(hwnd)
            win32gui.SetForegroundWindow(hwnd)
        finally:
            if attached:
                ctypes.windll.user32.AttachThreadInput(cur_tid, tgt_tid, False)
        return win32gui.GetForegroundWindow() == hwnd
    except Exception:
        try:
            win32gui.SetForegroundWindow(hwnd)
            return win32gui.GetForegroundWindow() == hwnd
        except Exception:
            return False


def _assert_softdent_foreground(hwnd: int | None = None) -> int:
    """Ensure SoftDent owns keyboard focus; refuse if AMD/other thief is foreground."""
    import win32gui

    target = int(hwnd or _main_softdent_hwnd())
    _force_foreground(target)
    time.sleep(0.15)
    fg = win32gui.GetForegroundWindow()
    fg_title = win32gui.GetWindowText(fg) or ""
    if _is_blocked_focus_title(fg_title):
        raise RuntimeError(
            f"Refusing SoftDent keys — AMD/other thief owns foreground: {fg_title!r}. "
            "Close or leave AMD alone; do not Alt+R (AMD Instant Replay)."
        )
    fg_pid = _window_pid(fg)
    sd_pids = _softdent_pids()
    if sd_pids and fg_pid is not None and fg_pid not in sd_pids and fg != target:
        raise RuntimeError(
            f"Refusing SoftDent keys — foreground not SoftDent: {fg_title!r}"
        )
    return target


def _send_softdent_keys(keys: str, *, pause: float = 0.05, hwnd: int | None = None) -> None:
    """Type keys only while a SoftDent window is foreground. Never sends Escape."""
    from pywinauto.keyboard import send_keys

    if "{ESC}" in keys.upper() or "{ESCAPE}" in keys.upper():
        raise RuntimeError("Escape is forbidden — it prompts SoftDent to close")
    _assert_softdent_foreground(hwnd)
    send_keys(keys, pause=pause)


def _desktop_dialogs() -> Iterable[Any]:
    """SoftDent-owned #32770 dialogs only (never AMD / other apps)."""
    from pywinauto import Desktop

    pids = _softdent_pids()
    for w in Desktop(backend="win32").windows():
        try:
            if not w.is_visible() or w.class_name() != "#32770":
                continue
            title = (w.window_text() or "").strip()
            if _is_blocked_focus_title(title):
                continue
            pid = _window_pid(w.handle)
            if pids and pid not in pids:
                continue
            yield w
        except Exception:
            continue


def find_dialog(title: str):
    for w in _desktop_dialogs():
        if w.window_text() == title:
            return w
    return None


_PRINTER_TITLE_HINTS = (
    "print",
    "printer",
    "printing",
    "spooler",
    "default printer",
    "cannot print",
    "unable to print",
    "printer offline",
    "printer not",
    "no printers",
    "select printer",
)


def _dialog_text_blob(dlg) -> str:
    """Title + static labels for printer-detection (best-effort)."""
    parts: list[str] = []
    try:
        parts.append(dlg.window_text() or "")
    except Exception:
        pass
    try:
        for c in dlg.descendants():
            try:
                cls = (c.class_name() or "").lower()
                if cls in {"static", "button"} or "static" in cls:
                    t = (c.window_text() or "").strip()
                    if t:
                        parts.append(t)
            except Exception:
                continue
    except Exception:
        pass
    return " ".join(parts).lower()


def _is_printer_dialog(dlg) -> bool:
    blob = _dialog_text_blob(dlg)
    if not blob:
        return False
    return any(h in blob for h in _PRINTER_TITLE_HINTS)


def cancel_printer_dialogs(*, max_rounds: int = 8) -> int:
    """Cancel SoftDent/Windows printer prompts when default printer is off.

    Prefer Cancel / Alt+C / keyboard — never Escape on SoftDent main (quit).
    Call this while waiting for Output Options / Report Setup / Save.
    """
    from pywinauto import Application, Desktop

    cancelled = 0
    pids = _softdent_pids()
    for _ in range(max_rounds):
        hit = False
        candidates = []
        # SoftDent-owned dialogs
        candidates.extend(list(_desktop_dialogs()))
        # Also common top-level print dialogs (may not be SoftDent PID)
        try:
            for w in Desktop(backend="win32").windows():
                try:
                    if not w.is_visible() or w.class_name() != "#32770":
                        continue
                    title = (w.window_text() or "").strip()
                    if _is_blocked_focus_title(title):
                        continue
                    if title in {"Output Options", "Report Setup", "Select File Name", "SoftDent Login"}:
                        continue
                    if _is_printer_dialog(w) or any(h in title.lower() for h in _PRINTER_TITLE_HINTS):
                        candidates.append(w)
                except Exception:
                    continue
        except Exception:
            pass

        seen: set[int] = set()
        for w in candidates:
            try:
                h = int(w.handle)
            except Exception:
                continue
            if h in seen:
                continue
            seen.add(h)
            title = ""
            try:
                title = (w.window_text() or "").strip()
            except Exception:
                pass
            if title in {"Output Options", "Report Setup", "Select File Name", "SoftDent Login"}:
                continue
            if title == "SoftDent" and not _is_printer_dialog(w):
                # Generic SoftDent alert — leave for dismiss_softdent_alerts (Enter/OK)
                continue
            if not (_is_printer_dialog(w) or any(h in title.lower() for h in _PRINTER_TITLE_HINTS)):
                continue
            try:
                _force_foreground(h)
                time.sleep(0.15)
                # Try Cancel button first (keyboard Alt+C often works on #32770)
                canceled_this = False
                try:
                    app = Application(backend="win32").connect(handle=h)
                    dlg = app.window(handle=h)
                    for name in ("Cancel", "&Cancel", "No", "&No", "Close"):
                        for b in dlg.descendants(class_name="Button"):
                            if b.window_text().replace("&", "") == name.replace("&", ""):
                                # Prefer keyboard: focus Cancel then Enter / Alt+C
                                try:
                                    b.set_focus()
                                    _send_softdent_keys("{ENTER}", hwnd=h)
                                except Exception:
                                    _send_softdent_keys("%c", hwnd=h)
                                canceled_this = True
                                break
                        if canceled_this:
                            break
                except Exception:
                    pass
                if not canceled_this:
                    # SoftDent print prompt often has Cancel as non-default — Alt+C
                    try:
                        _send_softdent_keys("%c", hwnd=h)
                        canceled_this = True
                    except Exception:
                        pass
                if canceled_this:
                    cancelled += 1
                    hit = True
                    logger.info("Cancelled printer dialog title=%r", title)
                    time.sleep(0.4)
                    break
            except Exception as exc:
                logger.warning("Printer dialog cancel failed: %s", type(exc).__name__)
                continue
        if not hit:
            break
    return cancelled


def dismiss_softdent_alerts(*, max_rounds: int = 6) -> int:
    """Dismiss SoftDent message boxes with Enter (keyboard only). Never Escape.

    Printer/offline prompts are cancelled separately via cancel_printer_dialogs().
    """
    cancelled_printers = cancel_printer_dialogs(max_rounds=max(2, max_rounds // 2))
    dismissed = cancelled_printers
    pids = _softdent_pids()
    for _ in range(max_rounds):
        hit = False
        # Always clear printer prompts first
        if cancel_printer_dialogs(max_rounds=2):
            hit = True
            dismissed += 1
            continue
        for w in list(_desktop_dialogs()):
            title = (w.window_text() or "").strip()
            if title == "SoftDent Login":
                continue
            if _is_printer_dialog(w):
                continue  # handled by cancel_printer_dialogs
            if title not in {"SoftDent", ""}:
                continue
            pid = _window_pid(w.handle)
            if pids and pid not in pids:
                continue
            try:
                if not _force_foreground(w.handle):
                    continue
                time.sleep(0.15)
                # Default button is OK — Enter confirms. Never Escape (quit prompt).
                _send_softdent_keys("{ENTER}", hwnd=int(w.handle))
                dismissed += 1
                hit = True
                time.sleep(0.3)
                break
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
    """Main SoftDent frame owned by SDWIN — never AMD / Login dialog."""
    import win32gui
    import win32process

    pids = _softdent_pids()
    if not pids:
        raise RuntimeError("SoftDent (SDWIN) is not running")

    candidates: list[tuple[int, str, str]] = []

    def _cb(hwnd, _):
        try:
            if not win32gui.IsWindowVisible(hwnd):
                return True
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if int(pid) not in pids:
                return True
            title = win32gui.GetWindowText(hwnd) or ""
            cls = win32gui.GetClassName(hwnd) or ""
            if _is_blocked_focus_title(title):
                return True
            if "login" in title.lower():
                return True
            candidates.append((int(hwnd), title, cls))
        except Exception:
            pass
        return True

    win32gui.EnumWindows(_cb, None)
    for hwnd, title, cls in candidates:
        if "SoftDent Software" in title or "SOFTDENT" in cls.upper():
            return hwnd
    if candidates:
        return candidates[0][0]
    raise RuntimeError("SoftDent main window not found (SDWIN running but no main UI)")


def _keyboard_activate_dialog(dlg) -> None:
    """Bring a SoftDent dialog to foreground for keyboard input (no mouse)."""
    _force_foreground(int(dlg.handle))
    time.sleep(0.15)
    _assert_softdent_foreground(int(dlg.handle))


def _keyboard_press_ok(hwnd: int | None = None) -> None:
    """Press default OK via Enter (keyboard only)."""
    _send_softdent_keys("{ENTER}", hwnd=hwnd)


def _focus_main():
    """Focus SoftDent main frame for keyboard menus. No Escape. No mouse clicks."""
    import win32gui

    hwnd = _main_softdent_hwnd()
    if not _force_foreground(hwnd):
        time.sleep(0.25)
        _force_foreground(hwnd)
    _assert_softdent_foreground(hwnd)
    # set_focus via win32 only — avoid click_input (can hit AMD/other windows)
    try:
        from pywinauto import Application

        Application(backend="win32").connect(handle=hwnd).window(handle=hwnd).set_focus()
    except Exception:
        pass
    time.sleep(0.25)
    dismiss_softdent_alerts()
    # Re-assert SoftDent after dismissing alerts (never Escape — Escape asks to close).
    _assert_softdent_foreground(hwnd)
    return hwnd


def _open_report_via_keys(keys_after_reports_accounting: str) -> None:
    """Open SoftDent report via keyboard only.

    IMPORTANT: Do NOT send Alt+R — AMD Adrenalin Instant Replay steals Alt+R and
    launches/focuses AMD Software. Use F10 (menu bar) then R for Reports.
    Never send Escape after Sign On (SoftDent quit prompt).
    """
    _focus_main()
    # F10 = menu bar (SoftDent-owned). Then R=Reports, A=Accounting, then report keys.
    _send_softdent_keys("{F10}")
    time.sleep(0.35)
    _send_softdent_keys("r")
    time.sleep(0.35)
    _send_softdent_keys("a")
    time.sleep(0.35)
    for ch in keys_after_reports_accounting:
        if ch.isspace():
            continue
        _send_softdent_keys(ch)
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
    """Drive Output Options → Report Setup → Save with keyboard only (no Escape)."""
    from pywinauto import Application

    dismiss_softdent_alerts()
    cancel_printer_dialogs()
    out = None
    for _ in range(40):
        cancel_printer_dialogs(max_rounds=2)
        out = find_dialog("Output Options")
        if out:
            break
        time.sleep(0.25)
    if not out:
        raise RuntimeError("Output Options dialog did not appear")

    _keyboard_activate_dialog(out)
    # SoftDent Output Options: Excel radio often accelerated with E, then Enter=OK.
    _send_softdent_keys("e", hwnd=int(out.handle))
    time.sleep(0.2)
    _keyboard_press_ok(hwnd=int(out.handle))
    time.sleep(1.0)
    cancel_printer_dialogs()

    setup = None
    for _ in range(50):
        cancel_printer_dialogs(max_rounds=2)
        dismiss_softdent_alerts(max_rounds=2)
        setup = find_dialog("Report Setup")
        if setup:
            break
        time.sleep(0.25)
    if not setup:
        raise RuntimeError("Report Setup dialog did not appear")

    _keyboard_activate_dialog(setup)
    app_s = Application(backend="win32").connect(handle=setup.handle)
    d_s = app_s.window(handle=setup.handle)
    edits = d_s.descendants(class_name="Edit")
    if len(edits) < 3:
        raise RuntimeError("Report Setup missing date edits")
    start_txt = start.strftime("%m/%d/%y")
    end_txt = end.strftime("%m/%d/%y")
    # Prefer set_edit_text (no mouse); fields are SoftDent-owned.
    edits[1].set_edit_text(start_txt)
    edits[2].set_edit_text(end_txt)
    if len(edits) > 3:
        edits[3].set_edit_text("999")  # all providers
    time.sleep(0.2)
    _keyboard_press_ok(hwnd=int(setup.handle))
    time.sleep(1.0)
    dismiss_softdent_alerts()

    save = None
    for _ in range(50):
        cancel_printer_dialogs(max_rounds=2)
        dismiss_softdent_alerts(max_rounds=2)
        save = find_dialog("Select File Name")
        if save:
            break
        time.sleep(0.25)
    if not save:
        raise RuntimeError("Select File Name dialog did not appear")

    short_path = rf"{EXPORT_ROOT_SHORT}\{short_stem}"
    _keyboard_activate_dialog(save)
    app_save = Application(backend="win32").connect(handle=save.handle)
    d_save = app_save.window(handle=save.handle)
    edits = d_save.descendants(class_name="Edit")
    edits[0].set_edit_text(short_path)
    time.sleep(0.2)
    _keyboard_press_ok(hwnd=int(save.handle))
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
            # Recover without Escape (Escape prompts SoftDent to close).
            try:
                dismiss_softdent_alerts()
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
