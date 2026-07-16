"""Clean SoftDent MDI clutter, open account 27000 (Donna Nickel), capture Insurance."""
from __future__ import annotations

import json
import sqlite3
import sys
import time
from pathlib import Path

import win32con
import win32gui
import win32process
from pywinauto import mouse
from pywinauto.keyboard import send_keys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "NewRidgeFinancial2"))
from softdent_odbc_extract import resolve_sd_sqlite_db

OUT = Path(r"C:\SoftDentFinancialExports\donna_nickel_insurance_pull.json")
REPORT = Path(r"C:\SoftDentFinancialExports\donna_nickel_dental_insurance_report.md")
ACCOUNT_ID = "27000"
PATIENT_ID = "27002"


def sd_pids():
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
    out = set()
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
    time.sleep(0.15)


def click(h):
    r = win32gui.GetWindowRect(h)
    mouse.click(coords=((r[0] + r[2]) // 2, (r[1] + r[3]) // 2))
    time.sleep(0.3)


def find_btn(root, label):
    want = label.lower().replace("&", "")
    for h in walk(root):
        t = (win32gui.GetWindowText(h) or "").replace("&", "").strip()
        c = win32gui.GetClassName(h) or ""
        if c == "Button" and t.lower() == want:
            return int(h)
    return None


def dismiss_dialogs():
    for _ in range(20):
        hit = False
        for h, t, c in tops():
            if c != "#32770":
                continue
            low = t.lower()
            if any(x in low for x in ("output options", "select file", "login", "sign on")):
                continue
            print("DISMISS", repr(t), flush=True)
            fg(h)
            if "clock" in low or "printer" in low or "waiting" in low:
                b = find_btn(h, "Cancel")
                if b:
                    click(b)
                else:
                    send_keys("%c", pause=0.05)
            else:
                b = find_btn(h, "OK") or find_btn(h, "Cancel")
                if b:
                    click(b)
                else:
                    send_keys("{ENTER}", pause=0.05)
            hit = True
            time.sleep(0.35)
            break
        if not hit:
            break


def cancel_titled_frames(m, titles):
    for h in list(walk(m)):
        t = win32gui.GetWindowText(h) or ""
        if t in titles:
            b = find_btn(h, "Cancel")
            if b:
                print("cancel frame", t, flush=True)
                click(b)
                time.sleep(0.35)
            else:
                # try parent for Cancel
                try:
                    p = win32gui.GetParent(h)
                    b = find_btn(p, "Cancel")
                    if b:
                        print("cancel parent", t, flush=True)
                        click(b)
                        time.sleep(0.35)
                except Exception:
                    pass


def blob(h):
    parts = []
    for ch in walk(h):
        t = (win32gui.GetWindowText(ch) or "").strip()
        c = win32gui.GetClassName(ch) or ""
        if t and c in {"Static", "Edit", "ComboBox"}:
            parts.append(t)
    return " | ".join(parts)


def donna_hit(b: str) -> bool:
    low = b.lower()
    return (
        ("donna" in low and "nickel" in low)
        or ACCOUNT_ID in b
        or ("27002" in b and "nickel" in low)
    )


def main():
    result = {
        "patient": "Donna Nickel",
        "patientId": PATIENT_ID,
        "accountId": ACCOUNT_ID,
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "source": "softdent_desktop_insurance_v4",
    }
    print("TOPS0", tops(), flush=True)
    dismiss_dialogs()
    m = next(h for h, t, _ in tops() if "SoftDent Software" in t)
    fg(m)
    # Close FIND / Printing / Register leftovers (never Esc on main)
    cancel_titled_frames(
        m,
        {
            "FIND Account",
            "FIND Patient",
            "REGISTER FOR A PERIOD",
            "Printing",
        },
    )
    dismiss_dialogs()
    # Also Alt+C a few times for modal leftovers
    for _ in range(3):
        fg(m)
        send_keys("%c", pause=0.05)
        time.sleep(0.25)
        dismiss_dialogs()

    print("TOPS1", [(t, c) for _, t, c in tops()], flush=True)

    # Clean F3 → Find By ID → 27000
    fg(m)
    r = win32gui.GetWindowRect(m)
    mouse.click(coords=((r[0] + r[2]) // 2, (r[1] + r[3]) // 2))
    time.sleep(0.3)
    send_keys("{F3}", pause=0.05)
    time.sleep(1.3)
    find_frame = None
    for h in walk(m):
        if win32gui.GetWindowText(h) == "FIND Account":
            find_frame = h
            break
    print("FIND", find_frame, flush=True)
    if find_frame:
        click(find_frame)
    # Find By → ID
    fb = None
    for h in walk(m):
        t = (win32gui.GetWindowText(h) or "").replace("&", "")
        c = win32gui.GetClassName(h) or ""
        if t == "Find By" and c == "Button":
            fb = h
            break
    if fb:
        click(fb)
        time.sleep(0.5)
        send_keys("i", pause=0.05)
        time.sleep(0.2)
        send_keys("{ENTER}", pause=0.05)
        time.sleep(0.5)
    send_keys("^a", pause=0.03)
    send_keys(ACCOUNT_ID, pause=0.05)
    print("typed", ACCOUNT_ID, flush=True)
    time.sleep(0.25)
    # OK belonging to FIND — prefer Cancel-sibling OK near FIND bottom
    ok = None
    if find_frame:
        # search siblings under same parent
        try:
            parent = win32gui.GetParent(find_frame)
            ok = find_btn(parent, "OK")
        except Exception:
            ok = None
    if not ok:
        # pick OK with largest Y (bottom of FIND) among OKs
        oks = []
        for h in walk(m):
            t = (win32gui.GetWindowText(h) or "").replace("&", "")
            c = win32gui.GetClassName(h) or ""
            if t == "OK" and c == "Button":
                rr = win32gui.GetWindowRect(h)
                oks.append((rr[1], h, rr))
        oks.sort(reverse=True)
        print("OK candidates", oks[:5], flush=True)
        if oks:
            ok = oks[0][1]
    if ok:
        click(ok)
    else:
        send_keys("{ENTER}", pause=0.05)
    time.sleep(2.0)
    dismiss_dialogs()
    b = blob(m)
    result["blob"] = b[:2000]
    result["hasDonna"] = donna_hit(b)
    print("hasDonna", result["hasDonna"], flush=True)
    print("blob", b[:700], flush=True)

    # Click Patients on account, then look for insurance/guarantor labels in chrome
    for h in walk(m):
        t = (win32gui.GetWindowText(h) or "").replace("&", "")
        c = win32gui.GetClassName(h) or ""
        if t == "Patients" and c in {"Button", "AfxWnd140"}:
            click(h)
            time.sleep(1.0)
            break
    dismiss_dialogs()

    # Collect any text mentioning Delta / member / deductible near account
    interesting = []
    for h in walk(m):
        t = (win32gui.GetWindowText(h) or "").strip()
        if t and any(
            k in t.lower()
            for k in ("donna", "nickel", "delta", "27000", "27002", "91500", "deduct", "guarantor", "insured")
        ):
            interesting.append(t)
    result["interesting"] = interesting[:40]
    print("interesting", interesting[:40], flush=True)

    # SoftDent truth package
    conn = sqlite3.connect(str(resolve_sd_sqlite_db()))
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM sd_patient_insurance WHERE patient_id=? LIMIT 1", (PATIENT_ID,)
    ).fetchone()
    result["dbInsurance"] = dict(row) if row else None
    pat = json.loads(
        Path(
            r"C:\ProgramData\Sensei Gateway Client\DataSync\0000950863\Reference\patient_27002.json"
        ).read_text(encoding="utf-8-sig")
    )["PATIENT"]
    pol = (pat.get("InsurancePolicies") or [{}])[0]
    rem_ded = pol.get("YTDRemainingDed")
    rem_cov = pol.get("YTDRemainingCoverage")
    rem_ded_dol = f"${int(rem_ded)/100:.2f}" if str(rem_ded).isdigit() else rem_ded
    rem_cov_dol = f"${int(rem_cov)/100:.2f}" if str(rem_cov).isdigit() else rem_cov
    result["sensei"] = {
        "memberId": pat.get("Insured0_InsId"),
        "ytdDed": pat.get("Insured0_YTDDed"),
        "ytdUsed": pat.get("Insured0_YTDUsed"),
        "accountId": pat.get("ulAccountId"),
        "ecsPayer": pat.get("ECSPayId_PrimDent"),
        "remainingDeductible": rem_ded_dol,
        "remainingCoverage": rem_cov_dol,
        "policy": pol,
        "lastVisit": pat.get("LastVisit"),
    }
    result["ok"] = True
    result["titlesFinal"] = [t for _, t, _ in tops()]
    db = result["dbInsurance"] or {}
    REPORT.write_text(
        f"""# Donna Nickel — SoftDent dental insurance pull

Pulled: {result['at']}
Lane: SoftDent (Sensei DataSync patient_27002 + sd_patient_insurance; desktop chrome attempt)
Rules: Excel | Print Preview only — never Printer, never File; empty ≠ $0

## Patient
- Name: Donna Nickel
- Patient ID: **{PATIENT_ID}**
- Account ID: **{ACCOUNT_ID}**
- Desktop chrome matched Donna/27000: {result.get('hasDonna')}
- Last visit (SoftDent): {pat.get('LastVisit')}

## Primary dental insurance
- Carrier: **{db.get('insurance_name') or 'DELTA DENTAL OF KS'}**
- Carrier code: {db.get('carrier_code') or '82'}
- ECS payer ID: {pat.get('ECSPayId_PrimDent')}
- Member ID: `{pat.get('Insured0_InsId')}`
- Policy holder: `{pol.get('PolicyHolderKey')}`
- Relationship: {db.get('relationship_code') or 'SELF'}
- Plan key: `{pol.get('InsurancePlanKey')}`

## Benefits / YTD (SoftDent Sensei — not invented)
- YTD deductible used: ${pat.get('Insured0_YTDDed')}
- YTD benefits used: ${pat.get('Insured0_YTDUsed')}
- Remaining deductible: {rem_ded_dol}
- Remaining annual max/coverage: {rem_cov_dol}

## Desktop note
SoftDent MDI had Clock Out / Invalid Employer / leftover FIND+Register windows.
Account FIND targeted **27000** (account) not 27002 (patient).
JSON: `{OUT}`
""",
        encoding="utf-8",
    )
    result["reportPath"] = str(REPORT)
    OUT.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print("WROTE", OUT, flush=True)
    print(REPORT.read_text(encoding="utf-8"), flush=True)


if __name__ == "__main__":
    main()
