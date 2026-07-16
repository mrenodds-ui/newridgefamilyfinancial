"""Attended SoftDent Excel Output Options root-cause probe (READ-ONLY).

Opens Account Aging → Output Options, inspects Excel/Preview/File/Printer radios,
cancels without OK into File/Printer. Never invents Select File Name paths.
Never Esc SoftDent main.

Usage:
  python scripts/probe_softdent_excel_output_options.py
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NR2 = REPO / "NewRidgeFinancial2"
OUT = REPO / ".local_logs" / "moonshot_financial_eval"
OUT.mkdir(parents=True, exist_ok=True)

if str(NR2) not in sys.path:
    sys.path.insert(0, str(NR2))


def _inspect_output_options() -> dict:
    from pywinauto import Application

    from softdent_gui_export import (
        SoftDentExcelDisabledError,
        _force_foreground,
        _keyboard_cancel_dialog,
        _keyboard_activate_dialog,
        _open_accounting_report,
        cancel_printer_dialogs,
        ensure_softdent_ready_for_gui_export,
        find_dialog,
        load_menu_map,
        prepare_softdent_for_next_report,
        resolve_menu_keys,
    )

    ensure = ensure_softdent_ready_for_gui_export(timeout_s=60.0)
    prepare_softdent_for_next_report()
    catalog = load_menu_map()
    report = (catalog.get("reports") or {}).get("aging") or {}
    keys = resolve_menu_keys(report)
    _open_accounting_report("aging", keys)

    out = None
    for _ in range(50):
        cancel_printer_dialogs(max_rounds=2)
        out = find_dialog("Output Options")
        if out:
            break
        time.sleep(0.25)
    if not out:
        return {
            "ok": False,
            "excelAvailable": False,
            "error": "output_options_missing",
            "ensure": ensure,
        }

    _keyboard_activate_dialog(out)
    hwnd = int(out.handle)
    _force_foreground(hwnd)
    time.sleep(0.2)

    radios: list[dict] = []
    excel_btn = None
    preview_btn = None
    try:
        app = Application(backend="win32").connect(handle=out.handle)
        dlg = app.window(handle=out.handle)
        for b in dlg.descendants(class_name="Button"):
            label = (b.window_text() or "").replace("&", "").strip()
            if not label:
                continue
            lab = label.lower()
            enabled = None
            checked = None
            try:
                enabled = bool(b.is_enabled())
            except Exception:
                enabled = None
            try:
                if hasattr(b, "get_toggle_state"):
                    checked = int(b.get_toggle_state()) == 1
            except Exception:
                pass
            try:
                import win32gui

                state = int(win32gui.SendMessage(int(b.handle), 0x00F0, 0, 0))
                if state in (0, 1, 2):
                    checked = state == 1
            except Exception:
                pass
            row = {
                "label": label,
                "enabled_pywinauto": enabled,
                "checked": checked,
            }
            radios.append(row)
            if lab == "excel":
                excel_btn = b
            elif "preview" in lab:
                preview_btn = b
    except Exception as exc:  # noqa: BLE001
        _keyboard_cancel_dialog(hwnd)
        return {
            "ok": False,
            "excelAvailable": False,
            "error": f"radio_scan_failed:{type(exc).__name__}:{exc}"[:400],
            "ensure": ensure,
        }

    # SoftDent 32-bit often reports is_enabled()=False under 64-bit Python — still try BM click.
    excel_clickable = False
    excel_checked_after = None
    if excel_btn is not None:
        try:
            import win32gui

            child = int(excel_btn.handle)
            win32gui.SendMessage(child, 0x00F1, 1, 0)  # BM_SETCHECK
            time.sleep(0.05)
            win32gui.SendMessage(child, 0x00F5, 0, 0)  # BM_CLICK
            time.sleep(0.15)
            state = int(win32gui.SendMessage(child, 0x00F0, 0, 0))
            excel_checked_after = state == 1
            excel_clickable = excel_checked_after is True
        except Exception as exc:  # noqa: BLE001
            excel_clickable = False
            excel_checked_after = f"error:{type(exc).__name__}"

    preview_present = preview_btn is not None
    # Cancel — never OK into Printer/File; probe only.
    try:
        _keyboard_cancel_dialog(hwnd)
    except Exception:
        pass
    time.sleep(0.3)
    cancel_printer_dialogs(max_rounds=3)

    excel_row = next((r for r in radios if r["label"].lower() == "excel"), None)
    # excelAvailable = SoftDent accepted Excel radio check (even if pywinauto said disabled)
    excel_available = bool(excel_clickable)
    return {
        "ok": True,
        "excelAvailable": excel_available,
        "excelPresent": excel_row is not None,
        "excelEnabledPywinauto": (excel_row or {}).get("enabled_pywinauto"),
        "excelCheckedAfterClick": excel_checked_after,
        "printPreviewPresent": preview_present,
        "radios": radios,
        "note": (
            "Probe only — cancelled Output Options; never File/Printer OK. "
            "If excelAvailable=true, SoftDent accepts Excel radio despite greyed is_enabled. "
            "If false, SoftDent/Carestream feature still blocks Excel. empty ≠ $0."
        ),
        "ensure": ensure,
        "runbook": "NewRidgeFinancial2/docs/runbooks/softdent_excel_enablement_nr2.md",
    }


def main() -> int:
    try:
        result = _inspect_output_options()
    except Exception as exc:  # noqa: BLE001
        result = {
            "ok": False,
            "excelAvailable": False,
            "error": f"{type(exc).__name__}:{exc}"[:600],
        }
    result["at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = OUT / f"softdent_excel_output_options_probe_{stamp}.json"
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(f"Wrote {path}", flush=True)
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
