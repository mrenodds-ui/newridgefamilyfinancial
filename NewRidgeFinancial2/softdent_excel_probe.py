"""Read-only SoftDent Excel Output Options probe snapshots (money-beam gate)."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
_PROBE_LOG_DIR = _REPO / ".local_logs" / "moonshot_financial_eval"
_PROBE_SCRIPT = _REPO / "scripts" / "probe_softdent_excel_output_options.py"
_RUNBOOK = (
    Path(__file__).resolve().parent / "docs" / "runbooks" / "softdent_excel_enablement_nr2.md"
)


def resolve_excel_probe_log_dir() -> Path:
    return _PROBE_LOG_DIR


def latest_excel_probe_snapshot(*, log_dir: Path | None = None) -> dict[str, Any]:
    """Newest attended probe JSON; honest empty when never run."""
    root = Path(log_dir) if log_dir else resolve_excel_probe_log_dir()
    result: dict[str, Any] = {
        "ok": True,
        "hasProbe": False,
        "excelAvailable": None,
        "emptyNotZero": True,
        "probeScript": str(_PROBE_SCRIPT).replace("\\", "/"),
        "runbook": str(_RUNBOOK).replace("\\", "/"),
        "note": (
            "Attended probe only — never OK into Printer/File. "
            "Run scripts/probe_softdent_excel_output_options.py with SoftDent signed on."
        ),
    }
    if not root.is_dir():
        result["logDir"] = str(root)
        return result
    files = sorted(
        root.glob("softdent_excel_output_options_probe_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not files:
        result["logDir"] = str(root)
        return result
    path = files[0]
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        result["hasProbe"] = False
        result["error"] = f"read_failed:{type(exc).__name__}:{exc}"
        result["path"] = str(path)
        return result
    if not isinstance(payload, dict):
        result["error"] = "invalid_probe_shape"
        result["path"] = str(path)
        return result
    result.update(
        {
            "hasProbe": True,
            "path": str(path),
            "at": payload.get("at"),
            "excelAvailable": bool(payload.get("excelAvailable")),
            "excelPresent": payload.get("excelPresent"),
            "excelEnabledPywinauto": payload.get("excelEnabledPywinauto"),
            "excelCheckedAfterClick": payload.get("excelCheckedAfterClick"),
            "printPreviewPresent": payload.get("printPreviewPresent"),
            "radios": payload.get("radios"),
            "probeOk": bool(payload.get("ok")),
            "probeError": payload.get("error"),
            "probeNote": payload.get("note"),
        }
    )
    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        result["fileMtime"] = mtime.replace(microsecond=0).isoformat()
    except OSError:
        pass
    return result


def format_excel_probe_hal_reply(query: str = "") -> str:
    snap = latest_excel_probe_snapshot()
    lines = [
        "SoftDent Excel Output Options probe (money-beam gate · READ-ONLY).",
        f"Runbook: `{snap.get('runbook') or 'softdent_excel_enablement_nr2.md'}`.",
        "Rules: Excel or Print Preview only — never Printer, never File · empty ≠ $0.",
    ]
    if not snap.get("hasProbe"):
        lines.append(
            "NO PROBE on record — run `python scripts/probe_softdent_excel_output_options.py` "
            "with SoftDent signed on (Account Aging → Output Options → cancel after inspect)."
        )
        return " ".join(lines)
    avail = snap.get("excelAvailable")
    lines.append(
        f"Latest probe: excelAvailable=`{avail}` · at=`{snap.get('at') or snap.get('fileMtime') or '—'}`."
    )
    if avail is True:
        lines.append(
            "Excel radio accepted click — attended morning bundle may proceed per runbook "
            "(scripts/morning_bundle_attended.py --yes)."
        )
    elif avail is False:
        lines.append(
            "Excel still blocked — Carestream/driver/licensing or greyed Output Options. "
            "Do not invent Select File Name paths; fix SoftDent Excel enablement first."
        )
    err = snap.get("probeError")
    if err:
        lines.append(f"Probe fault: `{str(err)[:120]}`.")
    return " ".join(lines)


def query_touches_excel_probe(raw: str) -> bool:
    q = str(raw or "").lower()
    if not q.strip():
        return False
    return bool(
        re.search(
            r"\b("
            r"excel\s+(grey|gray|greyed|disabled|blocked|probe|available)|"
            r"output\s+options.{0,40}excel|"
            r"excel\s+probe|"
            r"money\s+beam.{0,30}excel|"
            r"morning\s+bundle.{0,30}excel|"
            r"why\s+is\s+excel"
            r")\b",
            q,
        )
    )
