"""Continue SoftDent Trans for a Period → Excel (Feb 2026), scan Donna Nickel."""
from __future__ import annotations

import json
import time
from pathlib import Path

import win32con
import win32gui
from pywinauto import Application, mouse
from pywinauto.keyboard import send_keys

DEST = Path(r"C:\SoftDentReportExports")
LOG = Path(r"C:\SoftDentFinancialExports\softdent_account_tx_excel_validation.json")


def titles():
    out = []

    def cb(h, _):
        if win32gui.IsWindowVisible(h):
            t = win32gui.GetWindowText(h) or ""
            if t:
                out.append((int(h), t, win32gui.GetClassName(h)))
        return True

    win32gui.EnumWindows(cb, None)
    return out


def fg(h: int) -> None:
    try:
        win32gui.ShowWindow(h, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(h)
    except Exception:
        send_keys("%")
        time.sleep(0.05)
        try:
            win32gui.SetForegroundWindow(h)
        except Exception:
            pass
    time.sleep(0.25)


def cancel_print() -> int:
    n = 0
    for h, t, _ in titles():
        low = t.lower()
        if low in {"print", "printing"} or "printer" in low or "waiting" in low:
            fg(h)
            send_keys("%c", pause=0.05)
            time.sleep(0.4)
            n += 1
    return n


def click_button(dlg, label: str) -> bool:
    want = label.lower()
    for b in dlg.descendants(class_name="Button"):
        lab = (b.window_text() or "").replace("&", "").strip().lower()
        if lab == want:
            r = b.rectangle()
            mouse.click(coords=((r.left + r.right) // 2, (r.top + r.bottom) // 2))
            time.sleep(0.3)
            return True
    return False


def main() -> None:
    before = {p.name: p.stat().st_mtime for p in DEST.glob("*") if p.is_file()}
    print("tops", [(t, c) for _, t, c in titles() if "Soft" in t or c == "#32770"], flush=True)
    cancel_print()

    main_h = next(h for h, t, _ in titles() if "SoftDent Software" in t)
    fg(main_h)
    send_keys("{F10}", pause=0.05)
    time.sleep(0.45)
    send_keys("r", pause=0.05)
    time.sleep(0.4)
    send_keys("a", pause=0.05)
    time.sleep(0.45)
    send_keys("t", pause=0.05)
    time.sleep(1.2)

    oo = next((h for h, t, _ in titles() if t == "Output Options"), None)
    if not oo:
        try:
            app = Application(backend="win32").connect(handle=main_h)
            app.window(handle=main_h).menu_select("Reports->Accounting->Trans for a Period")
            time.sleep(1.0)
        except Exception as exc:
            print("menu_select", type(exc).__name__, flush=True)
        oo = next((h for h, t, _ in titles() if t == "Output Options"), None)
    print("Output Options", oo, flush=True)
    if not oo:
        raise SystemExit(2)

    fg(oo)
    app = Application(backend="win32").connect(handle=oo)
    dlg = app.window(handle=oo)
    btns = [(b.window_text() or "").replace("&", "").strip() for b in dlg.descendants(class_name="Button")]
    print("buttons", btns, flush=True)
    if not click_button(dlg, "excel"):
        send_keys("e", pause=0.05)
    time.sleep(0.25)
    if not click_button(dlg, "ok"):
        send_keys("{ENTER}", pause=0.05)
    time.sleep(1.5)
    cancel_print()

    setup = next((h for h, t, _ in titles() if "Transactions For A Period" in t), None)
    print("setup", setup, flush=True)
    if not setup:
        raise SystemExit(3)

    fg(setup)
    app = Application(backend="win32").connect(handle=setup)
    w = app.window(handle=setup)
    edits = w.descendants(class_name="Edit")
    # title, start, end, format
    if len(edits) >= 4:
        if "TRANSACTION" not in (edits[0].window_text() or "").upper():
            edits[0].set_edit_text("TRANSACTIONS FOR A PERIOD")
        edits[1].set_edit_text("02/01/2026")
        edits[2].set_edit_text("02/28/2026")
        edits[3].set_edit_text("1")
    print("Feb 2026 format=1", flush=True)
    if not click_button(w, "ok"):
        send_keys("%o", pause=0.05)
    time.sleep(1.0)

    save = None
    for i in range(100):
        cancel_print()
        ts = titles()
        setup_now = next((h for h, t, _ in ts if "Transactions For A Period" in t), None)
        save = next((h for h, t, _ in ts if t in ("Select File Name", "Save As")), None)
        dlg32770 = [t for _, t, c in ts if c == "#32770"]
        print(i, "setup", bool(setup_now), "save", save, "dlg", dlg32770, flush=True)
        if save:
            break
        if not setup_now and not save:
            time.sleep(6)
            ts = titles()
            save = next((h for h, t, _ in ts if t in ("Select File Name", "Save As")), None)
            break
        time.sleep(0.5)

    if save:
        fg(save)
        send_keys("^a", pause=0.03)
        send_keys(r"C:\SOFTDE~1\TXN260201", pause=0.03)
        app = Application(backend="win32").connect(handle=save)
        if not click_button(app.window(handle=save), "ok"):
            send_keys("{ENTER}", pause=0.05)
        print("save dialog OK", flush=True)
        time.sleep(12)

    produced = None
    for p in sorted(DEST.glob("*"), key=lambda x: x.stat().st_mtime if x.is_file() else 0, reverse=True):
        if p.is_file() and (p.name not in before or p.stat().st_mtime > before.get(p.name, 0)):
            produced = p
            break
    if not produced:
        for p in Path(r"C:\SoftDent").glob("*.xls*"):
            if p.stat().st_mtime > time.time() - 600:
                produced = p
                break

    result = json.loads(LOG.read_text(encoding="utf-8")) if LOG.is_file() else {}
    result.setdefault("learnedFromWeb", {})
    result.setdefault("validatedLive", {})
    result["validatedLive"].update(
        {
            "excelButtonPresent": "Excel" in btns,
            "outputOptionButtons": btns,
            "saved": str(produced) if produced else None,
            "continuedAt": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "range": "02/01/2026-02/28/2026",
            "format": "1 List Each Transaction Separately",
        }
    )
    result["ok"] = bool(produced)
    result["at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    if produced:
        raw = produced.read_bytes().decode("latin-1", errors="ignore")
        low = raw.lower()
        lines = [ln.strip() for ln in raw.splitlines() if "nickel" in ln.lower()]
        donna = [ln for ln in lines if "donna" in ln.lower()]
        result.update(
            {
                "bytes": produced.stat().st_size,
                "nickelMentions": low.count("nickel"),
                "hasDonnaNickel": bool(donna) or ("donna" in low and "nickel" in low),
                "sampleNickelLines": lines[:20],
                "donnaLines": donna[:12],
            }
        )
        print("nickel", result["nickelMentions"], "donna", result["hasDonnaNickel"], flush=True)
        for ln in (donna or lines)[:15]:
            print("HIT", ln[:180], flush=True)

    LOG.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("RESULT ok=", result["ok"], "saved=", produced, flush=True)
    print("WROTE", LOG, flush=True)
    raise SystemExit(0 if produced else 4)


if __name__ == "__main__":
    main()
