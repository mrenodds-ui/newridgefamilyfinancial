"""Period-close OPS desk alerts via HAL hub (BlueNote has no programmatic send).

Fires when close is stalled/blocked, completes with attest_only, Force Close runs,
or lasers stay red past a short stall window.
Cites JSONL / readiness only — empty ≠ $0 · no SoftDent write-back.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
OPS_DIR = REPO_ROOT / "app_data" / "nr2" / "ops"
NOTIFY_STATE_PATH = OPS_DIR / "period_close_notify_state.json"

# Desk copy must stay short (hub popup + voice clip).
_KIND_LINES = {
    "stalled": "Period close stalled. Use Force Close on Pages Hub.",
    "blocked": "Period close blocked by lasers. SoftDent aging pull via Force Close.",
    "attest_only": "Period close attest-only. SoftDent GUI export failed — beams may be stale.",
    "force_close": "Force Close completed. Check Pages Hub / Office Manager.",
    "force_close_start": "Force Close started on the desk. Check Pages Hub / Office Manager.",
    "laser_stall": "Lasers red past stall window. Force Close on Pages Hub if SoftDent aging is stale.",
}

# Per-kind throttle window (seconds). Exact-key dedupe still applies.
_THROTTLE_SEC = {
    "stalled": 300,
    "blocked": 300,
    "attest_only": 300,
    "force_close": 120,
    "force_close_start": 60,
    "laser_stall": 300,
}


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _parse_iso(raw: str | None) -> datetime | None:
    text = str(raw or "").strip()
    if not text:
        return None
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _ensure_ops() -> None:
    OPS_DIR.mkdir(parents=True, exist_ok=True)


def _read_state() -> dict[str, Any]:
    _ensure_ops()
    if not NOTIFY_STATE_PATH.is_file():
        return {"lastKeys": [], "lastByKind": {}, "laserRedSince": None}
    try:
        raw = json.loads(NOTIFY_STATE_PATH.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {"lastKeys": [], "lastByKind": {}}
    except Exception:
        return {"lastKeys": [], "lastByKind": {}}


def _write_state(state: dict[str, Any]) -> None:
    _ensure_ops()
    NOTIFY_STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def classify_period_close_trouble(result: dict[str, Any] | None) -> str | None:
    """Return trouble kind: stalled | blocked | force_close | attest_only — else None."""
    if not isinstance(result, dict):
        return None
    status = str(result.get("status") or "").lower()
    if status == "stalled":
        return "stalled"
    if status == "blocked":
        return "blocked"
    if result.get("forceCloseStarted"):
        return "force_close_start"
    if result.get("forceClose") or result.get("force_close"):
        return "force_close"
    if status == "completed" and str(result.get("fallback") or "").lower() == "attest_only":
        return "attest_only"
    return None


def notify_dedupe_key(kind: str, result: dict[str, Any]) -> str:
    stamp = str(result.get("completedAt") or result.get("startedAt") or result.get("timestamp") or "")[
        :19
    ]
    beam = str(result.get("beamHash") or "")[:12]
    return f"{kind}|{stamp}|{beam}|{result.get('actor') or ''}"


def period_close_trouble_line(kind: str, result: dict[str, Any] | None = None) -> str:
    base = _KIND_LINES.get(kind) or f"Period close trouble: {kind}."
    result = result if isinstance(result, dict) else {}
    beam = str(result.get("beamHash") or "").strip()
    actor = str(result.get("actor") or "").strip()
    bits = [base]
    if kind in ("force_close", "force_close_start") and result.get("laserOverride"):
        bits.append("Laser override.")
    if kind == "force_close" and str(result.get("fallback") or "").lower() == "attest_only":
        bits.append("Attest-only SoftDent pull failed.")
    if actor and kind in ("force_close", "force_close_start"):
        bits.append(f"Actor {actor}.")
    if beam:
        bits.append(f"Hash {beam[:8]}.")
    return " ".join(bits)


def _throttled(kind: str, state: dict[str, Any]) -> bool:
    if os.environ.get("NR2_PERIOD_CLOSE_OPS_NOTIFY_TEST", "").strip().lower() in (
        "1",
        "true",
        "yes",
    ):
        return False
    window = int(_THROTTLE_SEC.get(kind, 300))
    last_by = state.get("lastByKind") if isinstance(state.get("lastByKind"), dict) else {}
    last_at = _parse_iso(str((last_by or {}).get(kind) or ""))
    if not last_at:
        return False
    age = (datetime.now(timezone.utc) - last_at.astimezone(timezone.utc)).total_seconds()
    return age < window


def notify_period_close_trouble(
    result: dict[str, Any] | None,
    *,
    speak: bool = True,
    store: Any | None = None,
    kind: str | None = None,
) -> dict[str, Any]:
    """HAL hub office alert + optional DB alert. No BlueNote network send exists."""
    resolved = kind or classify_period_close_trouble(result)
    if not resolved:
        return {"ok": True, "skipped": True, "reason": "not_trouble"}

    if os.environ.get("NR2_PERIOD_CLOSE_OPS_NOTIFY", "1").strip().lower() in (
        "0",
        "false",
        "no",
        "off",
    ):
        return {"ok": True, "skipped": True, "reason": "disabled"}

    assert isinstance(result, dict)
    key = notify_dedupe_key(resolved, result)
    state = _read_state()
    keys = [str(k) for k in (state.get("lastKeys") or []) if k]
    if key in keys:
        return {"ok": True, "skipped": True, "reason": "deduped", "key": key, "kind": resolved}
    if _throttled(resolved, state):
        return {"ok": True, "skipped": True, "reason": "throttled", "kind": resolved}

    line = period_close_trouble_line(resolved, result)
    hub: dict[str, Any] = {"ok": False}
    alert: dict[str, Any] | None = None

    try:
        from hal_hub import process_pending, submit_inbound

        submit_inbound(
            "HAL Close",
            ["Office Manager", "all"],
            line,
            speak=bool(speak),
            role="hal",
            type_="period_close_ops",
        )
        hub = process_pending()
        hub["ok"] = True
        hub["line"] = line
    except Exception as exc:  # noqa: BLE001
        hub = {"ok": False, "error": str(exc)[:240]}

    if store is not None:
        try:
            from hal_alerts import create_alert

            conn = store._connect() if hasattr(store, "_connect") else None
            if conn is not None:
                titles = {
                    "stalled": "Period close stalled",
                    "blocked": "Period close blocked",
                    "attest_only": "Period close attest-only",
                    "force_close": "Force Close",
                    "force_close_start": "Force Close started",
                    "laser_stall": "Lasers stalled red",
                }
                title = titles.get(resolved, "Period close trouble")
                alert = create_alert(
                    conn,
                    alert_type="period_close",
                    severity="high" if resolved in ("stalled", "blocked", "laser_stall") else "medium",
                    title=title,
                    body=line,
                    meta={
                        "kind": resolved,
                        "status": result.get("status"),
                        "fallback": result.get("fallback"),
                        "beamHash": result.get("beamHash"),
                        "laserOverride": result.get("laserOverride"),
                        "actor": result.get("actor"),
                        "emptyNotZero": True,
                        "systemOfRecord": False,
                    },
                )
        except Exception as exc:  # noqa: BLE001
            alert = {"ok": False, "error": str(exc)[:240]}

    last_by = dict(state.get("lastByKind") or {})
    last_by[resolved] = _iso_now()
    keys = ([key] + keys)[:20]
    _write_state(
        {
            **state,
            "lastKeys": keys,
            "lastByKind": last_by,
            "lastKind": resolved,
            "lastAt": _iso_now(),
            "lastLine": line,
        }
    )
    return {
        "ok": bool(hub.get("ok")),
        "kind": resolved,
        "key": key,
        "line": line,
        "hub": hub,
        "alert": alert,
        "emptyNotZero": True,
        "channel": "hal_hub",
    }


def notify_force_close_started(
    *,
    actor: str,
    laser_override: bool = False,
    store: Any | None = None,
    speak: bool = True,
) -> dict[str, Any]:
    """Immediate Force Close initiation alert (before close completes)."""
    return notify_period_close_trouble(
        {
            "status": "started",
            "forceClose": True,
            "forceCloseStarted": True,
            "actor": actor,
            "laserOverride": bool(laser_override),
            "startedAt": _iso_now(),
            "timestamp": _iso_now(),
            "emptyNotZero": True,
        },
        speak=speak,
        store=store,
        kind="force_close_start",
    )


def maybe_notify_laser_stall(
    readiness: dict[str, Any] | None,
    *,
    stall_seconds: int | None = None,
    store: Any | None = None,
    speak: bool = True,
) -> dict[str, Any]:
    """Alert when lasers stay red/blocking past stall window (default 5 minutes)."""
    ready = readiness if isinstance(readiness, dict) else {}
    lasers = ready.get("alignmentLasers") if isinstance(ready.get("alignmentLasers"), dict) else {}
    blocking = ready.get("blocking") if isinstance(ready.get("blocking"), list) else []
    red = bool(lasers.get("red") is True or blocking)
    state = _read_state()
    now = datetime.now(timezone.utc)

    if not red:
        if state.get("laserRedSince"):
            state = {**state, "laserRedSince": None}
            _write_state(state)
        return {"ok": True, "skipped": True, "reason": "lasers_clear"}

    since_raw = state.get("laserRedSince")
    since = _parse_iso(str(since_raw or ""))
    if since is None:
        state = {**state, "laserRedSince": _iso_now()}
        _write_state(state)
        return {"ok": True, "skipped": True, "reason": "laser_red_armed", "laserRedSince": state["laserRedSince"]}

    window = stall_seconds
    if window is None:
        try:
            window = int(os.environ.get("NR2_LASER_STALL_NOTIFY_SEC", "300"))
        except ValueError:
            window = 300
    age = (now - since.astimezone(timezone.utc)).total_seconds()
    if age < max(30, int(window)):
        return {
            "ok": True,
            "skipped": True,
            "reason": "laser_red_waiting",
            "ageSec": int(age),
            "needSec": int(window),
        }

    return notify_period_close_trouble(
        {
            "status": "stalled",
            "actor": "laser-stall-monitor",
            "startedAt": since.isoformat(),
            "completedAt": _iso_now(),
            "timestamp": _iso_now(),
            "laserClear": False,
            "emptyNotZero": True,
        },
        speak=speak,
        store=store,
        kind="laser_stall",
    )
