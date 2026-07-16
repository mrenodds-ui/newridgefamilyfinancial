"""NR2 ops gate checklist — what's green vs blocking close/cutover.

Read-only. SoftDent GUI not launched. empty ≠ $0.

Usage:
  python scripts/nr2_ops_gates_checklist.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NR2 = REPO / "NewRidgeFinancial2"
OUT = REPO / ".local_logs" / "moonshot_financial_eval"
OUT.mkdir(parents=True, exist_ok=True)

if str(NR2) not in sys.path:
    sys.path.insert(0, str(NR2))


def _gate(name: str, status: str, detail: str, next_cmd: str = "") -> dict:
    return {"name": name, "status": status, "detail": detail, "next": next_cmd}


def main() -> int:
    gates: list[dict] = []

    # 1 Excel probe
    try:
        from softdent_excel_probe import latest_excel_probe_snapshot

        ep = latest_excel_probe_snapshot()
        if ep.get("excelAvailable") is True:
            gates.append(
                _gate(
                    "excel_probe",
                    "GREEN",
                    f"excelAvailable=true · at {ep.get('at') or ep.get('fileMtime') or '—'}",
                    "python scripts/morning_bundle_attended.py --yes --refresh-close",
                )
            )
        elif not ep.get("hasProbe"):
            gates.append(
                _gate(
                    "excel_probe",
                    "RED",
                    "No attended probe on record",
                    "python scripts/probe_softdent_excel_output_options.py",
                )
            )
        else:
            gates.append(
                _gate(
                    "excel_probe",
                    "RED",
                    "excelAvailable=false — Output Options Excel still blocked",
                    "Follow docs/runbooks/softdent_excel_enablement_nr2.md",
                )
            )
    except Exception as exc:  # noqa: BLE001
        gates.append(_gate("excel_probe", "FAULT", str(exc)[:120]))

    # 2 Morning bundle
    try:
        from daily_closeout import period_close_status

        status = period_close_status()
        mb = status.get("morningBundle") if isinstance(status.get("morningBundle"), dict) else {}
        if mb.get("ok"):
            gates.append(
                _gate(
                    "morning_bundle",
                    "GREEN",
                    f"ok · status={status.get('status')}",
                )
            )
        elif mb.get("fallback"):
            gates.append(
                _gate(
                    "morning_bundle",
                    "RED",
                    f"fallback={mb.get('fallback')} · attest_only until Excel exports land",
                    "python scripts/morning_bundle_attended.py --yes --refresh-close",
                )
            )
        else:
            gates.append(
                _gate(
                    "morning_bundle",
                    "RED",
                    str(mb.get("error") or mb.get("detail") or "morningBundle not ok"),
                    "python scripts/morning_bundle_attended.py --probe-only",
                )
            )
    except Exception as exc:  # noqa: BLE001
        gates.append(_gate("morning_bundle", "FAULT", str(exc)[:120]))

    # 3 Desk smoke / beam proof
    try:
        from hal_brain_tools import beam_desk_proof

        proof = beam_desk_proof()
        desk = str(proof.get("deskProof") or "").upper()
        if desk == "MATCH":
            gates.append(_gate("beam_desk_proof", "GREEN", "MATCH"))
        else:
            gates.append(
                _gate(
                    "beam_desk_proof",
                    "RED" if desk else "YELLOW",
                    desk or "NO SIGNAL",
                    "python scripts/refresh_period_close_beam.py",
                )
            )
    except Exception as exc:  # noqa: BLE001
        gates.append(_gate("beam_desk_proof", "FAULT", str(exc)[:120]))

    # 4 Trellis AM proof
    try:
        from nr2_trellis_nightly import trellis_am_benefits_proof

        am = trellis_am_benefits_proof()
        if am.get("passed"):
            gates.append(
                _gate(
                    "trellis_am_proof",
                    "GREEN",
                    str(am.get("chipLabel") or "withBenefits > 0"),
                )
            )
        else:
            gates.append(
                _gate(
                    "trellis_am_proof",
                    "YELLOW",
                    str(am.get("chipLabel") or "awaiting nightly ClearCoverage scrape"),
                    "powershell -File scripts/install_trellis_am_proof_task.ps1",
                )
            )
    except Exception as exc:  # noqa: BLE001
        gates.append(_gate("trellis_am_proof", "FAULT", str(exc)[:120]))

    # 5 Pilot / shadow SOR
    try:
        from nr2_pilot import pilot_info

        pilot = pilot_info()
        days = pilot.get("shadowDaysElapsed")
        min_days = pilot.get("minShadowDays") or 30
        phase = pilot.get("phase") or "shadow"
        sor = bool(pilot.get("systemOfRecord"))
        if sor:
            gates.append(
                _gate(
                    "pilot_shadow",
                    "GREEN",
                    f"phase={phase} · systemOfRecord=true",
                )
            )
        elif isinstance(days, int) and days >= int(min_days):
            gates.append(
                _gate(
                    "pilot_shadow",
                    "YELLOW",
                    f"phase={phase} · shadowDays={days} (≥{min_days}) · still systemOfRecord=false",
                    "See docs/runbooks/nr2_cutover_to_sor.md",
                )
            )
        else:
            gates.append(
                _gate(
                    "pilot_shadow",
                    "YELLOW",
                    f"phase={phase} · shadowDays={days} · need ≥{min_days} before cutover",
                )
            )
    except Exception as exc:  # noqa: BLE001
        gates.append(_gate("pilot_shadow", "FAULT", str(exc)[:120]))

    # 6 ERA suggestions (informational)
    try:
        from nr2_era_inbox import era_suggestions, era_inbox_status

        inbox = era_inbox_status(ensure_dirs=False)
        sug = era_suggestions(limit=5)
        gates.append(
            _gate(
                "era_inbox",
                "GREEN" if int(inbox.get("fileCount") or 0) or int(sug.get("count") or 0) else "YELLOW",
                f"inbox={inbox.get('fileCount') or 0} · suggestions={sug.get('count') or 0} · {inbox.get('chipLabel') or '—'}",
                r"Drop real 835 into app_data\nr2\office\era_inbox\drop (or C:\SoftDentFinancialExports\era) then python scripts/run_era_inbox_ingest_ops.py — see docs/runbooks/era_835_inbox_drop_nr2.md",
            )
        )
    except Exception as exc:  # noqa: BLE001
        gates.append(_gate("era_inbox", "FAULT", str(exc)[:120]))

    red = sum(1 for g in gates if g["status"] == "RED")
    yellow = sum(1 for g in gates if g["status"] == "YELLOW")
    green = sum(1 for g in gates if g["status"] == "GREEN")
    payload = {
        "at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "summary": {"green": green, "yellow": yellow, "red": red},
        "gates": gates,
        "blockingNext": next((g for g in gates if g["status"] == "RED"), None),
        "note": "Read-only checklist · SoftDent write-back forbidden · empty ≠ $0",
    }
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = OUT / f"nr2_ops_gates_{stamp}.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"Wrote {out_path}", flush=True)

    # Exit: 0 all green; 1 any red; 2 yellow-only
    if red:
        return 1
    if yellow:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
