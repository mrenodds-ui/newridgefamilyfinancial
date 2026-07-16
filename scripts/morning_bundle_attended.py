#!/usr/bin/env python3
"""Attended SoftDent morning money bundle (aging + register + collections).

Operator must enable SoftDent Output Options Excel before money-beam ingest.
Excel or Print Preview only — never Printer, never File. empty ≠ $0.

Usage:
  python scripts/morning_bundle_attended.py --probe-only
  python scripts/morning_bundle_attended.py --yes
  python scripts/morning_bundle_attended.py --yes --refresh-close
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NR2 = REPO / "NewRidgeFinancial2"
OUT = REPO / ".local_logs"
OUT.mkdir(parents=True, exist_ok=True)

if str(NR2) not in sys.path:
    sys.path.insert(0, str(NR2))

RUNBOOK = NR2 / "docs" / "runbooks" / "softdent_excel_enablement_nr2.md"


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _print_gate(bundle: dict) -> None:
    gate = bundle.get("excelEnablementGate")
    if gate:
        print("\n--- EXCEL ENABLEMENT GATE ---")
        print(gate)
        print(f"\nRunbook: {RUNBOOK}")
    if bundle.get("excelDisabled"):
        print("\nSoftDent Output Options: Excel appears DISABLED (greyed).")
        print("Print Preview may succeed but money beams stay attest_only.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--days", type=int, default=30, help="Report period days (default 30)")
    ap.add_argument("--probe-only", action="store_true", help="Check gate only; do not launch SoftDent")
    ap.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
    ap.add_argument(
        "--refresh-close",
        action="store_true",
        help="After successful Excel aging export, run shadow period-close attest (--auto)",
    )
    args = ap.parse_args()

    from hal_brain_tools import SOFTDENT_EXCEL_ENABLEMENT_RUNBOOK, softdent_export_morning_bundle

    print("NR2 attended morning bundle")
    print(f"Runbook: {SOFTDENT_EXCEL_ENABLEMENT_RUNBOOK}")
    print("Schedule: 9:00 PM local night-before for next business day money beams.")
    print("Rules: Excel or Print Preview only - never Printer - never File - empty != $0\n")

    if args.probe_only:
        from daily_closeout import last_close_record, period_close_status
        from hal_brain_tools import beam_desk_proof

        status = period_close_status()
        mb = status.get("morningBundle") if isinstance(status.get("morningBundle"), dict) else {}
        proof = beam_desk_proof()
        last = last_close_record() or {}
        export_blob = last.get("export") if isinstance(last.get("export"), dict) else None
        out = {
            "morningBundle": mb or None,
            "periodClose": status.get("status"),
            "deskProof": proof.get("deskProof"),
            "drift": proof.get("drift"),
            "lastCloseHadExport": bool(export_blob),
            "lastCloseSoftdent": last.get("softdentDisplay"),
            "liveSoftdent": (proof.get("live") or {}).get("softdent", {}).get("display")
            if isinstance(proof.get("live"), dict)
            else None,
            "excelEnablementRunbook": str(RUNBOOK).replace("\\", "/"),
        }
        if not mb:
            out["note"] = (
                "Last period close was attest-only (no SoftDent GUI export on record). "
                "Confirm Excel enabled per runbook, then run without --probe-only."
            )
        print(json.dumps(out, indent=2, default=str))
        if mb.get("excelEnablementGate"):
            _print_gate(mb)
            return 2
        if mb and not mb.get("ok"):
            return 1
        return 0

    if not args.yes:
        print("Before continuing:")
        print("  1) Close/minimize Chrome Claim Management / NR2 Optical Claims")
        print("  2) SoftDent signed on (COMPUTE) and foreground")
        print("  3) Output Options → Excel enabled (not greyed)")
        print("  4) Select File Name uses SoftDent's own Documents folder — never invent paths")
        try:
            answer = input("\nProceed with attended morning bundle? [y/N]: ").strip().lower()
        except EOFError:
            answer = "n"
        if answer not in ("y", "yes"):
            print("Aborted.")
            return 1

    print(f"\nStarting bundle at {_utc_stamp()} …")
    result = softdent_export_morning_bundle(days=max(1, int(args.days)))
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_path = OUT / f"morning_bundle_attended_{stamp}.json"
    log_path.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote log: {log_path}")

    _print_gate(result)
    print("\n--- SUMMARY ---")
    print(json.dumps(
        {
            "ok": result.get("ok"),
            "agingOk": result.get("agingOk"),
            "failed": result.get("failed"),
            "paths": result.get("paths"),
            "excelDisabled": result.get("excelDisabled"),
            "fallback": result.get("fallback"),
            "emptyNotZero": result.get("emptyNotZero", True),
        },
        indent=2,
    ))

    if not result.get("ok"):
        print("\nBundle did not pass money-beam gate (aging Excel required).")
        return 2

    if args.refresh_close:
        print("\nRefreshing shadow period-close beam snapshot …")
        from daily_closeout import run_period_close

        close = run_period_close(actor="morning_bundle_attended", auto=True, pull_softdent=False)
        print(json.dumps(
            {
                "ok": close.get("ok"),
                "status": close.get("status"),
                "dataBeamHash": close.get("dataBeamHash"),
                "softdentDisplay": close.get("softdentDisplay"),
                "qbDisplay": close.get("qbDisplay"),
            },
            indent=2,
        ))
        if not close.get("ok"):
            return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
