"""Pull remaining SoftDent Trans-for-a-Period year chunks (2017H2, 2019-2026YTD)."""
from __future__ import annotations

import json
import shutil
import sys
import time
from collections import Counter
from datetime import date
from pathlib import Path

import win32con
import win32gui
from pywinauto import Application
from pywinauto.keyboard import send_keys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "NewRidgeFinancial2"))

from softdent_gui_export import (  # noqa: E402
    EXPORT_ROOT_SHORT,
    _escape_pywinauto_keys,
    _excel_sdwin_workbook_open,
    _main_softdent_hwnd,
    _open_accounting_report,
    _save_excel_sdwin_copy,
    cancel_printer_dialogs,
    dismiss_softdent_alerts,
    find_dialog,
)
from softdent_signon import ensure_softdent_signed_on  # noqa: E402

DEST = Path(r"C:\SoftDentReportExports")
TEMP = Path(r"C:\Users\mreno\AppData\Local\Temp")
LOG = Path(r"C:\SoftDentFinancialExports\softdent_account_tx_year_chunks.json")


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
    time.sleep(0.3)


def titles() -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []

    def cb(h, _):
        if win32gui.IsWindowVisible(h):
            t = win32gui.GetWindowText(h) or ""
            if t:
                out.append((int(h), t))
        return True

    win32gui.EnumWindows(cb, None)
    return out


def dismiss_alerts() -> None:
    for h, t in titles():
        if t.strip() == "SoftDent":
            fg(h)
            send_keys("{ENTER}", pause=0.05)
            time.sleep(0.35)


def verify(path: Path, start: date) -> dict:
    text = path.read_text("latin-1", errors="ignore").splitlines()
    years: Counter[int] = Counter()
    for ln in text[12:]:
        part = ln.split(",", 1)[0].strip().strip('"')
        if len(part) >= 8 and part[2] == "/" and part[5] == "/":
            yy = int(part[-2:])
            years[2000 + yy if yy < 50 else 1900 + yy] += 1
    return {
        "rangeHeader": text[2] if len(text) > 2 else "",
        "rows": sum(years.values()),
        "years": dict(sorted(years.items())),
        "yearMin": min(years) if years else None,
        "yearMax": max(years) if years else None,
        "ok": bool(years.get(start.year, 0) > 0 or (years and start.year in years)),
    }


def export_year(start: date, end: date, stem: str) -> dict:
    out = DEST / f"{stem}.xls"
    if out.is_file() and out.stat().st_size > 100_000:
        meta = verify(out, start)
        if meta.get("ok"):
            print("SKIP", stem, meta, flush=True)
            return {"ok": True, "skipped": True, "stem": stem, "saved": str(out), **meta}

    dismiss_softdent_alerts()
    cancel_printer_dialogs()
    fg(_main_softdent_hwnd())
    print("OPEN", start, end, stem, flush=True)
    _open_accounting_report("transactions", "t")
    oo = find_dialog("Output Options")
    if not oo:
        return {"ok": False, "error": "no Output Options", "stem": stem}

    oh = int(oo.handle)
    fg(oh)
    dlg = Application(backend="win32").connect(handle=oh).window(handle=oh)
    for b in dlg.descendants(class_name="Button"):
        if (b.window_text() or "").replace("&", "").strip().lower() == "excel":
            b.click()
            time.sleep(0.35)
            break
    else:
        return {"ok": False, "error": "no Excel", "stem": stem}
    for b in dlg.descendants(class_name="Button"):
        if (b.window_text() or "").replace("&", "").strip().lower() == "ok":
            b.click()
            break
    else:
        send_keys("{ENTER}", pause=0.05)
    time.sleep(1.0)

    setup = find_dialog("Transactions For A Period")
    if not setup:
        return {"ok": False, "error": "no setup", "stem": stem}
    sh = int(setup.handle)
    fg(sh)
    w = Application(backend="win32").connect(handle=sh).window(handle=sh)
    edits = w.descendants(class_name="Edit")
    edits[1].set_edit_text(start.strftime("%m/%d/%Y"))
    edits[2].set_edit_text(end.strftime("%m/%d/%Y"))
    edits[3].set_edit_text("1")
    print("fields", edits[1].window_text(), edits[2].window_text(), flush=True)
    for b in w.descendants(class_name="Button"):
        if (b.window_text() or "").replace("&", "").strip().lower() == "ok":
            b.click()
            break
    print("setup OK", flush=True)

    t0 = time.time()
    save_done = False
    best: Path | None = None
    for i in range(200):
        dismiss_alerts()
        save_h = next((h for h, t in titles() if t in {"Select File Name", "Save As"}), None)
        if save_h and not save_done:
            fg(save_h)
            short = rf"{EXPORT_ROOT_SHORT}\{stem}"
            send_keys("^a", pause=0.03)
            send_keys(_escape_pywinauto_keys(short), pause=0.03)
            send_keys("{ENTER}", pause=0.05)
            print("save", short, flush=True)
            save_done = True
            time.sleep(1.5)
            for h, t in titles():
                if t.strip() == "SoftDent" or "replace" in t.lower():
                    fg(h)
                    send_keys("{ENTER}", pause=0.05)

        printing = any(t == "Print File" for _, t in titles())
        cands = []
        for p in list(DEST.glob(f"{stem}.*")) + list(TEMP.glob("SDWIN*")):
            try:
                if p.is_file() and p.stat().st_mtime >= t0 - 3 and p.stat().st_size > 100_000:
                    cands.append(p)
            except OSError:
                continue
        if cands:
            best = max(cands, key=lambda p: (p.stat().st_mtime, p.stat().st_size))

        excel_open = False
        if printing or (best and best.stat().st_size > 200_000) or i > 15:
            try:
                excel_open = bool(_excel_sdwin_workbook_open())
            except Exception as exc:
                print("excel probe", type(exc).__name__, flush=True)
                excel_open = False

        if excel_open and not printing:
            try:
                copied = _save_excel_sdwin_copy(out)
                if copied and copied.is_file() and copied.stat().st_size > 100_000:
                    best = copied
                    print("SaveCopyAs", copied.stat().st_size, flush=True)
                    break
            except Exception as exc:
                print("SaveCopyAs", type(exc).__name__, flush=True)

        if i % 10 == 0:
            sz = best.stat().st_size if best else 0
            print(i, "print", printing, "MB", round(sz / 1e6, 2), flush=True)

        if best and not printing and best.stat().st_size > 100_000 and i > 8:
            break
        time.sleep(2)

    if not best or not best.is_file():
        return {"ok": False, "error": "no output", "stem": stem}

    if best.resolve() != out.resolve():
        shutil.copy2(best, out)
    shutil.copy2(out, DEST / f"transactions_for_period_{start.isoformat()}_{end.isoformat()}.xls")
    meta = verify(out, start)
    result = {"ok": meta.get("ok"), "stem": stem, "saved": str(out), "bytes": out.stat().st_size, **meta}
    print("CHUNK", json.dumps(result, indent=2), flush=True)
    return result


def main() -> None:
    today = date.today()
    chunks = [
        (date(2017, 6, 29), date(2017, 12, 31), "TXN2017H2"),
        (date(2019, 1, 1), date(2019, 12, 31), "TXN2019"),
        (date(2020, 1, 1), date(2020, 12, 31), "TXN2020"),
        (date(2021, 1, 1), date(2021, 12, 31), "TXN2021"),
        (date(2022, 1, 1), date(2022, 12, 31), "TXN2022"),
        (date(2023, 1, 1), date(2023, 12, 31), "TXN2023"),
        (date(2024, 1, 1), date(2024, 12, 31), "TXN2024"),
        (date(2025, 1, 1), date(2025, 12, 31), "TXN2025"),
        (date(today.year, 1, 1), today, f"TXN{today.year}YTD"),
    ]
    assist = ensure_softdent_signed_on(timeout_s=30.0)
    if not assist.get("ok") and not assist.get("signedOn"):
        fg(next(h for h, t in titles() if "login" in t.lower()))
        send_keys("^a{BACKSPACE}", pause=0.03)
        send_keys("COMPUTE", pause=0.04)
        send_keys("{TAB}", pause=0.05)
        send_keys("^a{BACKSPACE}", pause=0.03)
        send_keys("computer", pause=0.04)
        send_keys("{ENTER}", pause=0.05)
        time.sleep(2)
        dismiss_alerts()

    results = [{"ok": True, "skipped": True, "stem": "TXN2018", "saved": str(DEST / "TXN2018.xls")}]
    if (DEST / "TXN2018.xls").is_file():
        results[0].update(verify(DEST / "TXN2018.xls", date(2018, 1, 1)))

    for start, end, stem in chunks:
        try:
            results.append(export_year(start, end, stem))
        except Exception as exc:
            print("FAIL", stem, type(exc).__name__, exc, flush=True)
            results.append({"ok": False, "stem": stem, "error": str(exc)})
        time.sleep(1.5)

    summary = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "ok": all(r.get("ok") for r in results),
        "chunks": results,
        "okCount": sum(1 for r in results if r.get("ok")),
        "failCount": sum(1 for r in results if not r.get("ok")),
    }
    LOG.parent.mkdir(parents=True, exist_ok=True)
    LOG.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("SUMMARY", json.dumps({"ok": summary["ok"], "okCount": summary["okCount"], "failCount": summary["failCount"]}, indent=2), flush=True)
    raise SystemExit(0 if summary["ok"] else 4)


if __name__ == "__main__":
    main()
