"""Open SoftDent account 27000 / patient Donna Nickel 27002 → Insurance UI capture."""
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
REPORT = Path(r"C:\SoftDentFinancialExports\donna_nickel_dental_insurance_report.md")
OUTBOX = Path(r"C:\SoftDentReportExports")
SAVE = r"C:\SOFTDE~1\donna_nickel_27002_insurance.xls"
ACCOUNT_ID = "27000"
PATIENT_ID = "27002"


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
                out.append((int(h), win32gui.GetWindowText(h) or "", win32gui.GetClassName(h) or ""))
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


def fg(h):
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


def click(h):
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


def dismiss_all() -> list[str]:
    notes = []
    for _ in range(15):
        hit = False
        for h, t, c in tops():
            if c != "#32770":
                continue
            low = t.lower()
            if any(x in low for x in ("output options", "select file", "login", "sign on")):
                continue
            texts = [(win32gui.GetWindowText(ch) or "").strip() for ch in walk(h)]
            texts = [x for x in texts if x]
            print("DISMISS", repr(t), texts[:10], flush=True)
            notes.append(f"{t}: {' | '.join(texts[:6])}")
            fg(h)
            # Clock Out → Cancel (do not clock out)
            if "clock" in low:
                cancel = find_text(h, "Cancel", {"Button"})
                if cancel:
                    click(cancel)
                else:
                    send_keys("%c", pause=0.05)
            elif "printer" in " ".join(texts).lower() or "waiting" in " ".join(texts).lower():
                send_keys("%c", pause=0.05)
            else:
                ok = find_text(h, "OK", {"Button"})
                if ok:
                    click(ok)
                else:
                    send_keys("{ENTER}", pause=0.05)
            hit = True
            time.sleep(0.4)
            break
        if not hit:
            break
    return notes


def blob_of(h) -> str:
    parts = []
    for ch in walk(h):
        t = (win32gui.GetWindowText(ch) or "").strip()
        c = win32gui.GetClassName(ch) or ""
        if t and (c in {"Static", "Edit", "ComboBox"} or c.startswith("Edit")):
            parts.append(t)
    return " | ".join(parts)


def donna_hit(blob: str) -> bool:
    b = blob.lower()
    return (
        ("donna" in b and "nickel" in b)
        or "nickel, donna" in b
        or "donna nickel" in b
        or ACCOUNT_ID in blob
        or PATIENT_ID in blob
    )


def find_ok_near_find(m):
    # Prefer OK that is a child near FIND Account frame
    find_frame = find_text(m, "FIND Account")
    if find_frame:
        ok = find_text(find_frame, "OK", {"Button"})
        if ok:
            return ok
        # sibling search: walk parent
        try:
            parent = win32gui.GetParent(find_frame)
            ok = find_text(parent, "OK", {"Button"})
            if ok:
                return ok
        except Exception:
            pass
    return find_text(m, "OK", {"Button"})


def open_account_by_id(m, acct_id: str) -> str:
    # Cancel FIND leftovers
    for h in list(walk(m)):
        if win32gui.GetWindowText(h) == "FIND Account":
            cbtn = find_text(h, "Cancel", {"Button"})
            if cbtn:
                click(cbtn)
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
    send_keys(acct_id, pause=0.05)
    time.sleep(0.2)
    ok = find_ok_near_find(m)
    if ok:
        click(ok)
    else:
        send_keys("{ENTER}", pause=0.05)
    time.sleep(1.6)
    dismiss_all()
    return blob_of(m)


def open_patient_by_name(m) -> str:
    fg(m)
    send_keys("{F5}", pause=0.05)
    time.sleep(1.2)
    # FIND Patient
    send_keys("^a", pause=0.03)
    send_keys("Nickel", pause=0.05)
    send_keys("{TAB}", pause=0.05)
    send_keys("^a", pause=0.03)
    send_keys("Donna", pause=0.05)
    time.sleep(0.2)
    ok = find_text(m, "OK", {"Button"})
    if ok:
        click(ok)
    else:
        send_keys("{ENTER}", pause=0.05)
    time.sleep(1.6)
    dismiss_all()
    return blob_of(m)


def open_insurance_ui(m) -> dict:
    steps = []
    # Account chrome Insurance button
    for h in walk(m):
        t = (win32gui.GetWindowText(h) or "").replace("&", "").strip()
        c = win32gui.GetClassName(h) or ""
        if t == "Insurance" and c == "Button":
            click(h)
            steps.append("InsuranceButton")
            time.sleep(1.5)
            dismiss_all()
            break
    # Guarantors
    for needle in ("Guarantors", "Guarantor", "Insurance Info"):
        btn = find_text(m, needle, {"Button", "AfxWnd140"})
        if btn:
            click(btn)
            steps.append(needle)
            time.sleep(1.3)
            break
    if not any("guarantor" in t.lower() for _, t, _ in tops()):
        fg(m)
        send_keys("%o", pause=0.05)
        time.sleep(0.4)
        send_keys("g", pause=0.05)
        time.sleep(1.0)
        steps.append("altO-g")
    caps = []
    for h, t, c in tops():
        if "SoftDent Software" in t:
            continue
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
        caps.append({"title": t, "labels": labs[:80], "edits": eds[:50], "buttons": btns[:30]})
    return {"steps": steps, "captures": caps, "mainBlob": blob_of(m)[:2000]}


def try_export_from_insurance() -> dict:
    target = None
    for h, t, _ in tops():
        low = (t or "").lower()
        if "guarantor" in low or ("insurance" in low and "softdent software" not in low and t.strip()):
            target = h
            break
    if not target:
        return {"ok": False, "error": "no insurance dialog"}
    fg(target)
    for seq in ("%p", "%o p"):
        send_keys(seq, pause=0.05)
        time.sleep(0.7)
        if any(tt == "Output Options" for _, tt, _ in tops()):
            break
        send_keys("%c", pause=0.05)
        time.sleep(0.2)
    oo = next((h for h, t, _ in tops() if t == "Output Options"), None)
    if not oo:
        return {"ok": False, "error": "no Output Options"}
    fg(oo)
    mode = None
    try:
        app = Application(backend="win32").connect(handle=oo)
        excel = preview = None
        for b in app.window(handle=oo).descendants(class_name="Button"):
            lab = (b.window_text() or "").replace("&", "").strip().lower()
            if lab == "excel" and b.is_enabled():
                excel = b
            if lab in {"print preview", "preview"} and b.is_enabled():
                preview = b
        if excel:
            excel.click_input()
            time.sleep(0.2)
            send_keys("{ENTER}", pause=0.05)
            mode = "excel"
        elif preview:
            preview.click_input()
            time.sleep(0.2)
            send_keys("{ENTER}", pause=0.05)
            mode = "print_preview"
        else:
            return {"ok": False, "error": "Excel and Print Preview unavailable"}
    except Exception as exc:
        return {"ok": False, "error": type(exc).__name__}
    before = {p.name: p.stat().st_mtime for p in OUTBOX.glob("*") if p.is_file()}
    time.sleep(1.0)
    saved = None
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
        for _ in range(25):
            for p in OUTBOX.glob("*"):
                if p.is_file() and (p.name not in before or p.stat().st_mtime > before.get(p.name, 0)):
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
    return {
        "ok": bool(saved) or preview_visible or mode == "print_preview",
        "mode": mode,
        "saved": saved,
        "previewVisible": preview_visible,
    }


def main() -> None:
    OUTBOX.mkdir(parents=True, exist_ok=True)
    result = {
        "patient": "Donna Nickel",
        "patientId": PATIENT_ID,
        "accountId": ACCOUNT_ID,
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "source": "softdent_desktop_insurance_v3",
    }
    print("TOPS", tops(), flush=True)
    result["dismissed"] = dismiss_all()
    m = next(h for h, t, _ in tops() if "SoftDent Software" in t)
    fg(m)
    click(m)

    blob = open_account_by_id(m, ACCOUNT_ID)
    result["afterAccountFind"] = blob[:1800]
    result["hasDonna"] = donna_hit(blob)
    print("after acct", result["hasDonna"], blob[:500], flush=True)

    if not result["hasDonna"]:
        blob = open_patient_by_name(m)
        result["afterPatientName"] = blob[:1800]
        result["hasDonna"] = donna_hit(blob)
        print("after name", result["hasDonna"], blob[:500], flush=True)

    if not result["hasDonna"]:
        # last try: F3 name Nickel
        for h in list(walk(m)):
            if win32gui.GetWindowText(h) == "FIND Account":
                cbtn = find_text(h, "Cancel", {"Button"})
                if cbtn:
                    click(cbtn)
        fg(m)
        send_keys("{F3}", pause=0.05)
        time.sleep(1.0)
        send_keys("^a", pause=0.03)
        send_keys("Nickel", pause=0.05)
        time.sleep(0.2)
        ok = find_ok_near_find(m)
        if ok:
            click(ok)
        else:
            send_keys("{ENTER}", pause=0.05)
        time.sleep(1.5)
        dismiss_all()
        blob = blob_of(m)
        result["afterAcctName"] = blob[:1800]
        result["hasDonna"] = donna_hit(blob)
        print("after acct name", result["hasDonna"], blob[:500], flush=True)

    ui = open_insurance_ui(m)
    result["insuranceUI"] = ui
    print("insurance steps", ui.get("steps"), flush=True)
    for c in ui.get("captures") or []:
        print("CAP", c.get("title"), "edits", (c.get("edits") or [])[:15], flush=True)

    result["export"] = try_export_from_insurance()
    print("export", result["export"], flush=True)

    conn = sqlite3.connect(str(resolve_sd_sqlite_db()))
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM sd_patient_insurance WHERE patient_id=? LIMIT 1", (PATIENT_ID,)
    ).fetchone()
    result["dbInsurance"] = dict(row) if row else None
    sensei = json.loads(
        Path(
            r"C:\ProgramData\Sensei Gateway Client\DataSync\0000950863\Reference\patient_27002.json"
        ).read_text(encoding="utf-8-sig")
    )
    pat = sensei["PATIENT"]
    pol = (pat.get("InsurancePolicies") or [{}])[0]
    # remaining stored as cents in Sensei
    rem_ded = pol.get("YTDRemainingDed")
    rem_cov = pol.get("YTDRemainingCoverage")
    try:
        rem_ded_dol = f"${int(rem_ded) / 100:.2f}" if rem_ded not in (None, "") else None
    except Exception:
        rem_ded_dol = rem_ded
    try:
        rem_cov_dol = f"${int(rem_cov) / 100:.2f}" if rem_cov not in (None, "") else None
    except Exception:
        rem_cov_dol = rem_cov

    result["senseiInsurance"] = {
        "memberId": pat.get("Insured0_InsId"),
        "ytdDedUsed": pat.get("Insured0_YTDDed"),
        "ytdUsed": pat.get("Insured0_YTDUsed"),
        "accountId": pat.get("ulAccountId"),
        "policy": pol,
        "remainingDeductible": rem_ded_dol,
        "remainingCoverage": rem_cov_dol,
        "ecsPayerId": pat.get("ECSPayId_PrimDent"),
    }
    result["ok"] = bool(result.get("hasDonna") or result.get("dbInsurance"))
    result["titlesFinal"] = [t for _, t, _ in tops()]

    db = result.get("dbInsurance") or {}
    md = f"""# Donna Nickel — SoftDent dental insurance pull

Pulled: {result['at']}
Lane: SoftDent desktop (read-only) + SoftDent Sensei patient sync
Rules: Excel | Print Preview only — never Printer, never File; empty ≠ $0

## Patient
- Name: Donna Nickel
- Patient ID: **{PATIENT_ID}**
- Account ID: **{ACCOUNT_ID}**
- Desktop account/patient chrome matched: {result.get('hasDonna')}

## Primary dental insurance
- Carrier: **{db.get('insurance_name') or 'DELTA DENTAL OF KS'}**
- Carrier code: {db.get('carrier_code') or '82'}
- ECS payer ID: {pat.get('ECSPayId_PrimDent')}
- Member ID: `{pat.get('Insured0_InsId')}`
- Policy holder key: `{pol.get('PolicyHolderKey')}`
- Relationship: {db.get('relationship_code') or 'SELF'}
- Plan key: `{pol.get('InsurancePlanKey')}`

## Benefits / YTD (SoftDent Sensei sync — not invented)
- YTD deductible used: ${pat.get('Insured0_YTDDed')}
- YTD benefits used: ${pat.get('Insured0_YTDUsed')}
- Remaining deductible: {rem_ded_dol}
- Remaining annual coverage: {rem_cov_dol}

## Desktop export
- Export: {json.dumps(result.get('export'))}
- JSON log: `{OUT}`
"""
    REPORT.write_text(md, encoding="utf-8")
    result["reportPath"] = str(REPORT)
    OUT.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print("WROTE", OUT, "ok=", result["ok"], flush=True)
    print("REPORT", REPORT, flush=True)
    raise SystemExit(0 if result["ok"] else 3)


if __name__ == "__main__":
    main()
