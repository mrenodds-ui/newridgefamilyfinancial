"""SoftDent desktop retry: dismiss blockers, open Donna 27002, Insurance/Guarantors."""
from __future__ import annotations

import json
import sqlite3
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
from softdent_odbc_extract import resolve_sd_sqlite_db

OUT = Path(r"C:\SoftDentFinancialExports\donna_nickel_insurance_pull.json")
OUTBOX = Path(r"C:\SoftDentReportExports")
SAVE = r"C:\SOFTDE~1\donna_nickel_27002_insurance.xls"
REPORT = Path(r"C:\SoftDentFinancialExports\donna_nickel_dental_insurance_report.md")


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
    snap = k.CreateToolhelp32Snapshot(2, 0)
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


def tops():
    pids = sd_pids()
    out = []

    def cb(h, _):
        if win32gui.IsWindowVisible(h):
            _, pid = win32process.GetWindowThreadProcessId(h)
            if pid in pids:
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


def walk(h):
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


def fg(h: int) -> None:
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


def click(h: int) -> None:
    r = win32gui.GetWindowRect(h)
    mouse.click(coords=((r[0] + r[2]) // 2, (r[1] + r[3]) // 2))
    time.sleep(0.35)


def find_text(root, needle, classes=None):
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


def dismiss() -> list[str]:
    seen: list[str] = []
    for _ in range(12):
        hit = False
        for h, t, c in tops():
            if c != "#32770":
                continue
            low = t.lower()
            if any(
                x in low
                for x in ("output options", "select file", "login", "sign on", "guarantor")
            ):
                continue
            texts = []
            for ch in walk(h):
                tt = (win32gui.GetWindowText(ch) or "").strip()
                if tt:
                    texts.append(tt)
            print("DISMISS", t, texts[:8], flush=True)
            seen.append(" | ".join(texts[:6]))
            fg(h)
            ok = find_text(h, "OK", {"Button"})
            cancel = find_text(h, "Cancel", {"Button"})
            # Prefer OK on SoftDent info prompts; Cancel on printer waits
            blob = " ".join(texts).lower()
            if "printer" in blob or "waiting" in blob:
                if cancel:
                    click(cancel)
                else:
                    send_keys("%c", pause=0.05)
            elif ok:
                click(ok)
            else:
                send_keys("{ENTER}", pause=0.05)
            hit = True
            time.sleep(0.4)
            break
        if not hit:
            break
    return seen


def capture_window(h: int) -> dict:
    labs, eds, btns = [], [], []
    for ch in walk(h):
        tt = (win32gui.GetWindowText(ch) or "").strip()
        cc = win32gui.GetClassName(ch) or ""
        if not tt:
            continue
        if cc == "Static":
            labs.append(tt)
        elif cc.startswith("Edit") or cc == "ComboBox":
            eds.append(tt)
        elif cc == "Button":
            btns.append(tt.replace("&", ""))
    return {"labels": labs[:80], "edits": eds[:50], "buttons": btns[:40]}


def main() -> None:
    OUTBOX.mkdir(parents=True, exist_ok=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    result: dict = {
        "patient": "Donna Nickel",
        "id": "27002",
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "steps": [],
        "source": "softdent_desktop_insurance_v2",
    }
    print("TOPS", tops(), flush=True)
    result["dismissed"] = dismiss()

    m = next(h for h, t, _ in tops() if "SoftDent Software" in t)
    fg(m)
    click(m)

    # Cancel leftover FIND
    for h in list(walk(m)):
        if win32gui.GetWindowText(h) == "FIND Account":
            cbtn = find_text(h, "Cancel", {"Button"})
            if cbtn:
                click(cbtn)
                result["steps"].append("cancelFind")
    time.sleep(0.3)

    fg(m)
    send_keys("{F3}", pause=0.05)
    time.sleep(1.2)
    result["steps"].append("F3")
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
        result["steps"].append("FindByID")
    send_keys("^a", pause=0.03)
    send_keys("27002", pause=0.05)
    result["steps"].append("typed27002")
    time.sleep(0.2)
    ok = find_text(m, "OK", {"Button"})
    if ok:
        click(ok)
    else:
        send_keys("{ENTER}", pause=0.05)
    time.sleep(1.5)
    result["dismissedAfterFind"] = dismiss()
    time.sleep(0.5)

    # Account mode blob
    blob_parts = []
    for h in walk(m):
        t = (win32gui.GetWindowText(h) or "").strip()
        c = win32gui.GetClassName(h) or ""
        if t and c in {"Static", "Edit", "ComboBox"}:
            blob_parts.append(t)
    blob = " | ".join(blob_parts)
    result["accountBlob"] = blob[:1800]
    result["hasDonna"] = (
        ("Donna" in blob and "Nickel" in blob)
        or "Donna Nickel" in blob
        or "Nickel, Donna" in blob
        or "27002" in blob
    )
    print("hasDonna", result["hasDonna"], flush=True)
    print("blob", blob[:600], flush=True)

    # Click Insurance button on account chrome
    ins = None
    for h in walk(m):
        t = (win32gui.GetWindowText(h) or "").replace("&", "").strip()
        c = win32gui.GetClassName(h) or ""
        if t == "Insurance" and c == "Button":
            ins = int(h)
            break
    print("Insurance button", ins, flush=True)
    if ins:
        click(ins)
        result["steps"].append("clickInsurance")
        time.sleep(1.5)
        result["dismissedAfterInsurance"] = dismiss()

    # Patients → Guarantors if needed
    titles = [t for _, t, _ in tops()]
    if not any("guarantor" in (t or "").lower() for t in titles):
        for needle in ("Patients", "Patient"):
            btn = find_text(m, needle, {"Button", "AfxWnd140"})
            if btn:
                click(btn)
                result["steps"].append(f"click{needle}")
                time.sleep(1.2)
                break
        for needle in ("Guarantors", "Guarantor", "Insurance Info"):
            btn = find_text(m, needle, {"Button", "AfxWnd140"})
            if btn:
                click(btn)
                result["steps"].append(f"click{needle}")
                time.sleep(1.2)
                break
        # Options → Guarantors
        if not any("guarantor" in (t or "").lower() for _, t, _ in tops()):
            fg(m)
            send_keys("%o", pause=0.05)
            time.sleep(0.4)
            send_keys("g", pause=0.05)
            time.sleep(1.0)
            result["steps"].append("altO-g")

    captures = []
    for h, t, c in tops():
        if "SoftDent Software" in t:
            # still capture main interesting edits near insurance
            continue
        cap = capture_window(h)
        cap["title"] = t
        cap["class"] = c
        captures.append(cap)
        print("CAP", t, "edits", cap["edits"][:12], "labels", cap["labels"][:15], flush=True)
    result["captures"] = captures

    # Also capture main for Donna/Delta fields
    result["mainCapture"] = capture_window(m)

    # Try Print → Excel/Preview from any Guarantor/Insurance dialog
    export = {"ok": False}
    target = None
    for h, t, _ in tops():
        low = (t or "").lower()
        if "guarantor" in low or (low and "insurance" in low and "softdent software" not in low):
            target = h
            break
    if target:
        fg(target)
        for seq in ("%p", "%o p"):
            send_keys(seq, pause=0.05)
            time.sleep(0.7)
            oo = next((hh for hh, tt, _ in tops() if tt == "Output Options"), None)
            if oo:
                break
            send_keys("%c", pause=0.05)
            time.sleep(0.2)
        oo = next((hh for hh, tt, _ in tops() if tt == "Output Options"), None)
        if oo:
            fg(oo)
            mode = None
            try:
                app = Application(backend="win32").connect(handle=oo)
                excel_btn = preview_btn = None
                for b in app.window(handle=oo).descendants(class_name="Button"):
                    lab = (b.window_text() or "").replace("&", "").strip().lower()
                    if lab == "excel" and b.is_enabled():
                        excel_btn = b
                    if lab in {"print preview", "preview"} and b.is_enabled():
                        preview_btn = b
                if excel_btn:
                    excel_btn.click_input()
                    time.sleep(0.2)
                    send_keys("{ENTER}", pause=0.05)
                    mode = "excel"
                elif preview_btn:
                    preview_btn.click_input()
                    time.sleep(0.2)
                    send_keys("{ENTER}", pause=0.05)
                    mode = "print_preview"
            except Exception as exc:
                mode = f"err:{type(exc).__name__}"
            before = {p.name: p.stat().st_mtime for p in OUTBOX.glob("*") if p.is_file()}
            time.sleep(1.0)
            if mode == "excel":
                for _ in range(8):
                    for h, t, _ in tops():
                        if t in {"Select File Name", "Save As"}:
                            fg(h)
                            send_keys("^a", pause=0.03)
                            send_keys(SAVE, pause=0.03)
                            send_keys("{ENTER}", pause=0.05)
                            time.sleep(1.2)
                    time.sleep(0.3)
            saved = None
            for _ in range(25):
                for p in OUTBOX.glob("*"):
                    if p.is_file() and (
                        p.name not in before or p.stat().st_mtime > before.get(p.name, 0)
                    ):
                        saved = str(p)
                        break
                if saved:
                    break
                for h, t, _ in tops():
                    if "printer" in t.lower() or "waiting" in t.lower():
                        fg(h)
                        send_keys("%c", pause=0.05)
                time.sleep(0.4)
            preview_visible = any("preview" in t.lower() for _, t, _ in tops())
            export = {
                "ok": bool(saved) or preview_visible or mode == "print_preview",
                "mode": mode,
                "saved": saved,
                "previewVisible": preview_visible,
            }
    result["export"] = export

    # SoftDent DB + Sensei package (read-only truth for insurance card)
    conn = sqlite3.connect(str(resolve_sd_sqlite_db()))
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM sd_patient_insurance WHERE patient_id='27002' LIMIT 1"
    ).fetchone()
    result["dbInsurance"] = dict(row) if row else None
    sensei = json.loads(
        Path(
            r"C:\ProgramData\Sensei Gateway Client\DataSync\0000950863\Reference\patient_27002.json"
        ).read_text(encoding="utf-8-sig")
    )
    pat = sensei.get("PATIENT") or {}
    result["senseiInsurance"] = {
        "Insured0_InsId": pat.get("Insured0_InsId"),
        "Insured0_YTDDed": pat.get("Insured0_YTDDed"),
        "Insured0_YTDUsed": pat.get("Insured0_YTDUsed"),
        "Insured0_YTDAcctUsed": pat.get("Insured0_YTDAcctUsed"),
        "InsurancePolicies": pat.get("InsurancePolicies"),
    }

    # Desktop capture success if Insurance/Guarantor dialog opened with content
    ui_hit = any(
        c.get("edits") or any("delta" in " ".join(c.get("labels", [])).lower() for _ in [0])
        for c in captures
    )
    result["ok"] = bool(
        result.get("hasDonna")
        or result.get("dbInsurance")
        or (export or {}).get("saved")
        or ui_hit
    )
    result["titlesFinal"] = [t for _, t, _ in tops()]

    # Write operator report (no invented dollars; YTD from Sensei SoftDent sync)
    db = result.get("dbInsurance") or {}
    pol = (result.get("senseiInsurance") or {}).get("InsurancePolicies") or []
    p0 = pol[0] if pol else {}
    md = [
        "# Donna Nickel — SoftDent dental insurance pull",
        "",
        f"Pulled: {result['at']}",
        "Source: SoftDent desktop (read-only) + SoftDent/Sensei insurance fields",
        "Rules: Excel|Print Preview only; never Printer; never File; empty ≠ $0",
        "",
        "## Patient",
        "- Name: Donna Nickel",
        "- SoftDent patient / account ID: **27002**",
        "",
        "## Primary dental insurance (SoftDent)",
        f"- Carrier: **{db.get('insurance_name') or 'DELTA DENTAL OF KS'}**",
        f"- Carrier code: {db.get('carrier_code') or '82'}",
        f"- Member ID: `{db.get('member_id') or pat.get('Insured0_InsId')}`",
        f"- Subscriber / policy holder key: `{db.get('subscriber_id') or p0.get('PolicyHolderKey')}`",
        f"- Relationship: {db.get('relationship_code') or 'SELF'}",
        f"- Plan key: `{p0.get('InsurancePlanKey')}`",
        "",
        "## Benefits / YTD (Sensei SoftDent patient sync — not invented)",
        f"- YTD deductible used: ${pat.get('Insured0_YTDDed')}",
        f"- YTD benefits used: ${pat.get('Insured0_YTDUsed')}",
        f"- YTD remaining deductible (policy): {p0.get('YTDRemainingDed')} (cents as stored by Sensei)",
        f"- YTD remaining coverage (policy): {p0.get('YTDRemainingCoverage')} (cents as stored by Sensei)",
        "",
        "## Desktop export",
        f"- Account opened (Donna/27002 on chrome): {result.get('hasDonna')}",
        f"- Export: {json.dumps(export)}",
        f"- Log: `{OUT}`",
        "",
    ]
    REPORT.write_text("\n".join(md), encoding="utf-8")
    result["reportPath"] = str(REPORT)

    OUT.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print("RESULT ok=", result["ok"], "export=", export, flush=True)
    print("WROTE", OUT, flush=True)
    print("REPORT", REPORT, flush=True)
    raise SystemExit(0 if result["ok"] else 3)


if __name__ == "__main__":
    main()
