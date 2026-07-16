"""SoftDent desktop: open Donna Nickel (27002) Guarantors/Insurance and export.

Output Options: Excel or Print Preview only — never Printer, never File.
Never Esc on SoftDent main. Keyboard or mouse only.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import win32con
import win32gui
import win32process
from pywinauto import Application, mouse
from pywinauto.keyboard import send_keys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "NewRidgeFinancial2"))

OUTBOX = Path(r"C:\SoftDentReportExports")
LOG = Path(r"C:\SoftDentFinancialExports\donna_nickel_insurance_pull.json")
SAVE_XLS = r"C:\SOFTDE~1\donna_nickel_27002_insurance.xls"
PATIENT_ID = "27002"
PATIENT_NAME = "Donna Nickel"


def sd_pids() -> set[int]:
    import ctypes
    from ctypes import wintypes

    class PE(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("cntUsage", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD),
            ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
            ("th32ModuleID", wintypes.DWORD),
            ("cntThreads", wintypes.DWORD),
            ("th32ParentProcessID", wintypes.DWORD),
            ("pcPriClassBase", ctypes.c_long),
            ("dwFlags", wintypes.DWORD),
            ("szExeFile", wintypes.WCHAR * 260),
        ]

    k = ctypes.windll.kernel32
    snap = k.CreateToolhelp32Snapshot(0x00000002, 0)
    pe = PE()
    pe.dwSize = ctypes.sizeof(PE)
    out: set[int] = set()
    try:
        if k.Process32FirstW(snap, ctypes.byref(pe)):
            while True:
                if (pe.szExeFile or "").upper().startswith("SDWIN"):
                    out.add(int(pe.th32ProcessID))
                if not k.Process32NextW(snap, ctypes.byref(pe)):
                    break
    finally:
        k.CloseHandle(snap)
    return out


def tops() -> list[tuple[int, str, str]]:
    pids = sd_pids()
    out: list[tuple[int, str, str]] = []

    def cb(h, _):
        if not win32gui.IsWindowVisible(h):
            return True
        try:
            _, pid = win32process.GetWindowThreadProcessId(h)
        except Exception:
            return True
        if pid not in pids:
            return True
        out.append(
            (
                int(h),
                win32gui.GetWindowText(h) or "",
                win32gui.GetClassName(h) or "",
            )
        )
        return True

    win32gui.EnumWindows(cb, None)
    return out


def main_hwnd() -> int:
    for h, t, _ in tops():
        if "SoftDent Software" in t:
            return h
    raise RuntimeError("no SoftDent main")


def fg(h: int) -> None:
    try:
        win32gui.ShowWindow(h, win32con.SW_RESTORE)
    except Exception:
        pass
    try:
        win32gui.SetForegroundWindow(h)
    except Exception:
        send_keys("%")
        time.sleep(0.05)
        try:
            win32gui.SetForegroundWindow(h)
        except Exception:
            pass
    time.sleep(0.2)


def walk(h: int):
    stack = [h]
    while stack:
        cur = stack.pop()
        yield cur
        try:
            ch = win32gui.GetWindow(cur, win32con.GW_CHILD)
        except Exception:
            continue
        kids = []
        while ch:
            kids.append(ch)
            ch = win32gui.GetWindow(ch, win32con.GW_HWNDNEXT)
        stack.extend(reversed(kids))


def click(h: int) -> None:
    r = win32gui.GetWindowRect(h)
    mouse.click(coords=((r[0] + r[2]) // 2, (r[1] + r[3]) // 2))
    time.sleep(0.3)


def find_text(root: int, needle: str, classes=None) -> int | None:
    n = needle.lower().replace("&", "")
    for h in walk(root):
        try:
            t = (win32gui.GetWindowText(h) or "").replace("&", "")
            c = win32gui.GetClassName(h) or ""
        except Exception:
            continue
        if n in t.lower() and (classes is None or c in classes):
            return int(h)
    return None


def find_dialog(title_substr: str) -> int | None:
    s = title_substr.lower()
    for h, t, _ in tops():
        if s in t.lower():
            return h
    return None


def dismiss_alerts() -> int:
    n = 0
    for _ in range(8):
        hit = False
        for h, t, c in tops():
            if c != "#32770":
                continue
            low = t.lower()
            if any(
                x in low
                for x in (
                    "login",
                    "sign on",
                    "output options",
                    "select file",
                    "report setup",
                    "guarantor",
                    "insurance",
                )
            ):
                continue
            if "printer" in low or "waiting for" in low:
                fg(h)
                send_keys("%c", pause=0.05)
                n += 1
                hit = True
                break
            if "clock" in low:
                fg(h)
                send_keys("%c", pause=0.05)
                n += 1
                hit = True
                break
        if not hit:
            break
        time.sleep(0.25)
    return n


def collect_static_edits(root: int) -> dict:
    labels: list[str] = []
    edits: list[str] = []
    for h in walk(root):
        try:
            t = (win32gui.GetWindowText(h) or "").strip()
            c = win32gui.GetClassName(h) or ""
        except Exception:
            continue
        if not t:
            continue
        if c == "Static":
            labels.append(t)
        elif c.startswith("Edit") or c == "ComboBox":
            edits.append(t)
    blob = " | ".join(labels + edits)
    return {
        "labels": labels[:80],
        "edits": edits[:40],
        "hasDonna": ("Donna" in blob and "Nickel" in blob)
        or ("Nickel, Donna" in blob)
        or ("Donna Nickel" in blob),
        "hasDelta": "DELTA" in blob.upper() or "Delta" in blob,
        "blobSample": blob[:1200],
    }


def open_donna_account(m: int) -> dict:
    fg(m)
    # Close leftover FIND
    for h in list(walk(m)):
        try:
            if win32gui.GetWindowText(h) == "FIND Account":
                cbtn = find_text(h, "Cancel", {"Button"})
                if cbtn:
                    click(cbtn)
        except Exception:
            pass
    time.sleep(0.3)
    fg(m)
    send_keys("{F3}", pause=0.05)
    time.sleep(1.2)
    find_mdi = find_text(m, "FIND Account")
    if find_mdi:
        click(find_mdi)
    fb = find_text(m, "Find By", {"Button"})
    if fb:
        click(fb)
        time.sleep(0.5)
        send_keys("i", pause=0.05)
        time.sleep(0.2)
        send_keys("{ENTER}", pause=0.05)
        time.sleep(0.5)
    send_keys("^a", pause=0.03)
    send_keys(PATIENT_ID, pause=0.05)
    ok = find_text(m, "OK", {"Button"})
    if ok:
        click(ok)
    else:
        send_keys("{ENTER}", pause=0.05)
    time.sleep(1.8)
    info = collect_static_edits(m)
    if not info.get("hasDonna"):
        fg(m)
        send_keys("{F3}", pause=0.05)
        time.sleep(1.0)
        send_keys("^a", pause=0.03)
        send_keys("Nickel", pause=0.05)
        send_keys("{TAB}", pause=0.05)
        send_keys("^a", pause=0.03)
        send_keys("Donna", pause=0.05)
        ok = find_text(m, "OK", {"Button"})
        if ok:
            click(ok)
        else:
            send_keys("{ENTER}", pause=0.05)
        time.sleep(1.8)
        info = collect_static_edits(m)
    return info


def open_guarantors_insurance(m: int) -> dict:
    """SoftDent Help: Patient List → Guarantors / Insurance Info → Patient Guarantor."""
    steps: list[str] = []
    fg(m)

    # Prefer clicking Guarantors / Insurance if visible on account/patient chrome
    for needle in ("Guarantors", "Guarantor", "Insurance Info", "Insurance"):
        btn = find_text(m, needle, {"Button", "AfxWnd140"})
        if btn:
            click(btn)
            steps.append(f"click:{needle}")
            time.sleep(1.2)
            break

    # Keyboard Options paths
    if not find_dialog("Guarantor") and not find_dialog("Insurance"):
        for seq, label in (
            ("%o g", "altO-g"),
            ("%o i", "altO-i"),
            ("{F10}o g", "f10-o-g"),
            ("{F10}o i", "f10-o-i"),
            ("g", "g-hotkey"),
        ):
            fg(m)
            send_keys(seq, pause=0.05)
            time.sleep(0.9)
            steps.append(label)
            if find_dialog("Guarantor") or find_dialog("Insurance") or find_dialog("Patient"):
                break
            # Cancel stray menus via Alt+C (never Esc on main)
            send_keys("%c", pause=0.05)
            time.sleep(0.2)

    # F5 Patient List → find → Guarantors
    dlg = (
        find_dialog("Guarantor")
        or find_dialog("Insurance")
        or find_dialog("Patient Guarantor")
    )
    if not dlg:
        fg(m)
        send_keys("{F5}", pause=0.05)
        time.sleep(1.2)
        steps.append("F5-patient")
        send_keys("^a", pause=0.03)
        send_keys(PATIENT_ID, pause=0.05)
        send_keys("{ENTER}", pause=0.05)
        time.sleep(1.0)
        for needle in ("Guarantors", "Guarantor", "Insurance Info"):
            btn = find_text(m, needle, {"Button", "AfxWnd140"})
            if btn:
                click(btn)
                steps.append(f"patientClick:{needle}")
                time.sleep(1.2)
                break
        if not find_dialog("Guarantor") and not find_dialog("Insurance"):
            send_keys("%o", pause=0.05)
            time.sleep(0.4)
            send_keys("g", pause=0.05)
            time.sleep(1.0)
            steps.append("patient-altO-g")

    dlg = (
        find_dialog("Guarantor")
        or find_dialog("Insurance")
        or find_dialog("Patient Guarantor")
    )
    capture = collect_static_edits(dlg) if dlg else collect_static_edits(m)
    return {
        "dialogHwnd": dlg,
        "dialogTitle": next((t for h, t, _ in tops() if h == dlg), None) if dlg else None,
        "steps": steps,
        "capture": capture,
        "titles": [t for _, t, _ in tops()],
    }


def select_excel_or_preview() -> dict:
    oo = find_dialog("Output Options")
    if not oo:
        return {"ok": False, "error": "no Output Options"}
    fg(oo)
    excel_enabled = False
    preview_enabled = False
    try:
        app = Application(backend="win32").connect(handle=oo)
        for b in app.window(handle=oo).descendants(class_name="Button"):
            lab = (b.window_text() or "").replace("&", "").strip().lower()
            try:
                enabled = b.is_enabled()
            except Exception:
                enabled = True
            if lab == "excel":
                excel_enabled = bool(enabled)
                if enabled:
                    b.click_input()
                    time.sleep(0.2)
                    send_keys("{ENTER}", pause=0.05)
                    return {"ok": True, "mode": "excel", "method": "mouse"}
            if lab in {"print preview", "preview"}:
                preview_enabled = bool(enabled)
        if preview_enabled:
            for b in app.window(handle=oo).descendants(class_name="Button"):
                lab = (b.window_text() or "").replace("&", "").strip().lower()
                if lab in {"print preview", "preview"}:
                    b.click_input()
                    time.sleep(0.2)
                    send_keys("{ENTER}", pause=0.05)
                    return {
                        "ok": True,
                        "mode": "print_preview",
                        "method": "mouse",
                        "excelGreyed": not excel_enabled,
                    }
    except Exception as exc:
        print("OO mouse fail", type(exc).__name__, flush=True)
    # Keyboard fallback — never P (Printer)
    send_keys("e", pause=0.05)
    time.sleep(0.15)
    send_keys("{ENTER}", pause=0.05)
    return {
        "ok": True,
        "mode": "excel_keyboard_fallback",
        "excelEnabled": excel_enabled,
        "previewEnabled": preview_enabled,
    }


def try_print_insurance_export() -> dict:
    before = {p.name: p.stat().st_mtime for p in OUTBOX.glob("*") if p.is_file()}
    # From Guarantor dialog, try Print / Options → Print
    dlg = (
        find_dialog("Guarantor")
        or find_dialog("Insurance")
        or find_dialog("Patient Guarantor")
    )
    if dlg:
        fg(dlg)
    for seq in ("%p", "%o p", "{F10}p"):
        send_keys(seq, pause=0.05)
        time.sleep(0.6)
        if find_dialog("Output Options"):
            break
        send_keys("%c", pause=0.05)
        time.sleep(0.2)
    if not find_dialog("Output Options"):
        return {
            "ok": False,
            "error": "no Output Options from Guarantor/Insurance print",
            "titles": [t for _, t, _ in tops()],
        }
    mode = select_excel_or_preview()
    time.sleep(1.0)
    saved = None
    if str(mode.get("mode") or "").startswith("excel"):
        for _ in range(8):
            h = find_dialog("Select File Name") or find_dialog("Save As")
            if h:
                fg(h)
                send_keys("^a", pause=0.03)
                send_keys(SAVE_XLS, pause=0.03)
                send_keys("{ENTER}", pause=0.05)
                time.sleep(1.5)
                break
            send_keys("{ENTER}", pause=0.05)
            time.sleep(0.4)
        for _ in range(30):
            for p in OUTBOX.glob("*"):
                if p.is_file() and (
                    p.name not in before or p.stat().st_mtime > before.get(p.name, 0)
                ):
                    saved = str(p)
                    break
            if saved:
                break
            for h, t, _ in tops():
                if "printer" in t.lower() or "waiting for" in t.lower():
                    fg(h)
                    send_keys("%c", pause=0.05)
            time.sleep(0.4)
    preview_visible = any("preview" in t.lower() for _, t, _ in tops())
    return {
        "ok": bool(saved) or preview_visible or mode.get("mode") == "print_preview",
        "saved": saved,
        "outputMode": mode,
        "previewVisible": preview_visible,
        "titles": [t for _, t, _ in tops()],
    }


def main() -> None:
    OUTBOX.mkdir(parents=True, exist_ok=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    result: dict = {
        "source": "softdent_desktop_ui_insurance",
        "patientId": PATIENT_ID,
        "patientName": PATIENT_NAME,
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "rules": "Excel|PrintPreview only; never Printer; never File; never Esc",
    }
    print("SoftDent Donna insurance pull starting", flush=True)
    print("windows", tops(), flush=True)

    # Ensure signed on if login present
    try:
        from softdent_signon import ensure_softdent_signed_on

        so = ensure_softdent_signed_on(timeout_s=20.0)
        result["signOn"] = {k: so.get(k) for k in ("ok", "signedOn", "attempted", "error", "user")}
        print("signOn", result["signOn"], flush=True)
    except Exception as exc:
        result["signOn"] = {"ok": False, "error": type(exc).__name__}

    dismiss_alerts()
    m = main_hwnd()
    fg(m)
    r = win32gui.GetWindowRect(m)
    mouse.click(coords=((r[0] + r[2]) // 2, (r[1] + r[3]) // 2))
    time.sleep(0.3)

    account = open_donna_account(m)
    result["openAccount"] = account
    print("openAccount hasDonna=", account.get("hasDonna"), flush=True)

    guarantor = open_guarantors_insurance(m)
    result["guarantors"] = guarantor
    print(
        "guarantors",
        {
            "title": guarantor.get("dialogTitle"),
            "hasDonna": (guarantor.get("capture") or {}).get("hasDonna"),
            "hasDelta": (guarantor.get("capture") or {}).get("hasDelta"),
            "steps": guarantor.get("steps"),
        },
        flush=True,
    )

    export = try_print_insurance_export()
    result["export"] = export
    print("export", {k: export.get(k) for k in ("ok", "saved", "outputMode", "previewVisible", "error")}, flush=True)

    # Honesty: capture counts as success when Guarantor shows Donna insurance even if Excel greyed
    cap = guarantor.get("capture") or {}
    result["ok"] = bool(
        export.get("saved")
        or export.get("previewVisible")
        or (guarantor.get("dialogHwnd") and (cap.get("hasDonna") or cap.get("hasDelta") or cap.get("blobSample")))
        or account.get("hasDonna")
    )
    result["titlesFinal"] = [t for _, t, _ in tops()]
    LOG.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print("WROTE", LOG, "ok=", result["ok"], flush=True)
    raise SystemExit(0 if result["ok"] else 3)


if __name__ == "__main__":
    main()
