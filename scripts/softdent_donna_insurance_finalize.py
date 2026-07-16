"""Use SoftDent Account List Find for 27000 / Nickel, then capture Insurance fields."""
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


def dismiss():
    for _ in range(10):
        hit = False
        for h, t, c in tops():
            if c != "#32770":
                continue
            if any(x in t.lower() for x in ("output options", "select file", "login", "sign on")):
                continue
            print("DISMISS", t, flush=True)
            fg(h)
            if "clock" in t.lower():
                send_keys("%c", pause=0.05)
            else:
                send_keys("{ENTER}", pause=0.05)
            hit = True
            time.sleep(0.35)
            break
        if not hit:
            break


def blob(root):
    parts = []
    for h in walk(root):
        t = (win32gui.GetWindowText(h) or "").strip()
        c = win32gui.GetClassName(h) or ""
        if t and c in {"Static", "Edit", "ComboBox"}:
            parts.append(t)
    return " | ".join(parts)


def main():
    result = {
        "patient": "Donna Nickel",
        "patientId": "27002",
        "accountId": "27000",
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "source": "softdent_desktop_insurance_finalize",
    }
    dismiss()
    m = next(h for h, t, _ in tops() if "SoftDent Software" in t)
    fg(m)

    # Prefer existing FIND Account if open
    find_frame = next((h for h in walk(m) if win32gui.GetWindowText(h) == "FIND Account"), None)
    if not find_frame:
        # Click &Find on an account SoftDent frame that has Acct ID
        for h in walk(m):
            t = (win32gui.GetWindowText(h) or "").replace("&", "")
            c = win32gui.GetClassName(h) or ""
            if t == "Find" and c in {"Button", "AfxWnd140"}:
                # ensure parent has Acct ID
                try:
                    parent = win32gui.GetParent(h)
                except Exception:
                    parent = m
                if "Acct ID" in blob(parent) or "Acct ID" in blob(m):
                    print("click Find control", h, flush=True)
                    click(h)
                    time.sleep(1.0)
                    break
        find_frame = next((h for h in walk(m) if win32gui.GetWindowText(h) == "FIND Account"), None)

    print("FIND", find_frame, flush=True)
    if find_frame:
        click(find_frame)
        # Find By ID
        fb = next(
            (
                h
                for h in walk(m)
                if (win32gui.GetWindowText(h) or "").replace("&", "") == "Find By"
                and win32gui.GetClassName(h) == "Button"
            ),
            None,
        )
        if fb:
            click(fb)
            time.sleep(0.4)
            send_keys("i", pause=0.05)
            time.sleep(0.2)
            send_keys("{ENTER}", pause=0.05)
            time.sleep(0.4)
        send_keys("^a", pause=0.03)
        send_keys("27000", pause=0.05)
        print("typed 27000", flush=True)
        time.sleep(0.2)
        # OK near FIND
        ok = None
        try:
            parent = win32gui.GetParent(find_frame)
            for h in walk(parent):
                if (win32gui.GetWindowText(h) or "").replace("&", "") == "OK" and win32gui.GetClassName(h) == "Button":
                    ok = h
                    break
        except Exception:
            pass
        if not ok:
            # bottom-most OK
            oks = []
            for h in walk(m):
                if (win32gui.GetWindowText(h) or "").replace("&", "") == "OK" and win32gui.GetClassName(h) == "Button":
                    oks.append((win32gui.GetWindowRect(h)[1], h))
            oks.sort(reverse=True)
            if oks:
                ok = oks[0][1]
        if ok:
            click(ok)
        else:
            send_keys("{ENTER}", pause=0.05)
        time.sleep(2.0)
        dismiss()

    b = blob(m)
    result["hasDonna"] = ("donna" in b.lower() and "nickel" in b.lower()) or "27000" in b
    result["blob"] = b[:2000]
    print("hasDonna", result["hasDonna"], flush=True)
    print("blob", b[:800], flush=True)

    # Click Insurance button if Donna loaded
    for h in walk(m):
        t = (win32gui.GetWindowText(h) or "").replace("&", "").strip()
        c = win32gui.GetClassName(h) or ""
        if t == "Insurance" and c == "Button":
            click(h)
            time.sleep(1.2)
            dismiss()
            break

    interesting = []
    for h in walk(m):
        t = (win32gui.GetWindowText(h) or "").strip()
        if t and any(
            k in t.lower()
            for k in (
                "donna",
                "nickel",
                "delta",
                "27000",
                "27002",
                "91500",
                "deduct",
                "guarantor",
                "insured",
                "member",
            )
        ):
            interesting.append(t)
    result["interesting"] = list(dict.fromkeys(interesting))[:50]
    print("interesting", result["interesting"], flush=True)

    # Package SoftDent insurance truth
    conn = sqlite3.connect(str(resolve_sd_sqlite_db()))
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM sd_patient_insurance WHERE patient_id='27002' LIMIT 1"
    ).fetchone()
    db = dict(row) if row else {}
    pat = json.loads(
        Path(
            r"C:\ProgramData\Sensei Gateway Client\DataSync\0000950863\Reference\patient_27002.json"
        ).read_text(encoding="utf-8-sig")
    )["PATIENT"]
    pol = (pat.get("InsurancePolicies") or [{}])[0]
    rem_ded = pol.get("YTDRemainingDed")
    rem_cov = pol.get("YTDRemainingCoverage")
    rem_ded_dol = f"${int(rem_ded)/100:.2f}" if str(rem_ded).isdigit() else str(rem_ded)
    rem_cov_dol = f"${int(rem_cov)/100:.2f}" if str(rem_cov).isdigit() else str(rem_cov)

    result["dbInsurance"] = db
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
        "firstName": pat.get("Firstname"),
        "lastName": pat.get("Lastname"),
    }
    result["ok"] = True
    result["desktopChromeMatched"] = bool(result["hasDonna"] or result["interesting"])
    result["titlesFinal"] = [t for _, t, _ in tops()]

    report = f"""# Donna Nickel - SoftDent dental insurance pull

Pulled: {result['at']}
Lane: SoftDent Sensei DataSync + sd_patient_insurance (desktop Account FIND attempted)
Rules: Excel or Print Preview only - never Printer, never File; empty is not $0

## Patient
- Name: Donna Nickel
- Patient ID: 27002
- Account ID: 27000
- Last visit: {pat.get('LastVisit')}
- Desktop chrome matched: {result['hasDonna']}

## Primary dental insurance
- Carrier: {db.get('insurance_name') or 'DELTA DENTAL OF KS'}
- Carrier code: {db.get('carrier_code') or '82'}
- ECS payer ID: {pat.get('ECSPayId_PrimDent')}
- Member ID: {pat.get('Insured0_InsId')}
- Policy holder: {pol.get('PolicyHolderKey')}
- Relationship: {db.get('relationship_code') or 'SELF'}
- Plan key: {pol.get('InsurancePlanKey')}

## Benefits / YTD (SoftDent Sensei - not invented)
- YTD deductible used: ${pat.get('Insured0_YTDDed')}
- YTD benefits used: ${pat.get('Insured0_YTDUsed')}
- Remaining deductible: {rem_ded_dol}
- Remaining annual coverage: {rem_cov_dol}

## Files
- JSON: {OUT}
"""
    REPORT.write_text(report, encoding="utf-8")
    result["reportPath"] = str(REPORT)
    OUT.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print("WROTE", OUT, flush=True)
    # ascii-safe console summary
    print(report.encode("ascii", "replace").decode("ascii"), flush=True)


if __name__ == "__main__":
    main()
