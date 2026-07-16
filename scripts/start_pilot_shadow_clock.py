"""Start (or resume) the NR2 pilot shadow-day clock.

Moonshot cutover hygiene: stamp pilot.shadow_started_at so shadowDaysElapsed
counts toward the ≥30-day shadow gate. Does NOT flip systemOfRecord.

Usage:
  python scripts/start_pilot_shadow_clock.py
  python scripts/start_pilot_shadow_clock.py --from-period-close
  python scripts/start_pilot_shadow_clock.py --at 2026-07-15T21:10:23+00:00

SoftDent write-back forbidden. empty ≠ $0.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NR2 = REPO / "NewRidgeFinancial2"
sys.path.insert(0, str(NR2))


def _period_close_shadow_started() -> str | None:
    """Prefer honest stamp already recorded on period-close / import readiness."""
    candidates = [
        REPO / "app_data" / "nr2" / "ops" / "period_close_state.json",
        REPO / "app_data" / "nr2" / "period_close_state.json",
        REPO / "app_data" / "nr2" / "office" / "period_close_state.json",
    ]
    for path in candidates:
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        for key in ("shadowStartedAt", "shadow_started_at"):
            val = data.get(key)
            if val:
                return str(val)
        ops = data.get("operationContext") or data.get("periodClose") or {}
        if isinstance(ops, dict):
            val = ops.get("shadowStartedAt") or ops.get("shadow_started_at")
            if val:
                return str(val)
    # Fall back: daily closeout / local store blob if present
    try:
        from local_store import LocalStore

        store = LocalStore(REPO / "app_data" / "nr2")
        blob = store.read_json("period_close_status.json") or {}
        if isinstance(blob, dict):
            val = blob.get("shadowStartedAt") or blob.get("shadow_started_at")
            if val:
                return str(val)
    except Exception:
        pass
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--from-period-close",
        action="store_true",
        help="Use period-close shadowStartedAt when present (default if no --at)",
    )
    ap.add_argument("--at", help="ISO-8601 UTC stamp for shadow_started_at")
    ap.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing shadow_started_at",
    )
    args = ap.parse_args()

    from nr2_pilot import ensure_phase_started, load_pilot_state, pilot_info, save_pilot_state

    state = load_pilot_state()
    existing = state.get("shadow_started_at")
    if existing and not args.force:
        info = pilot_info()
        print(
            f"Shadow clock already running: started={existing} "
            f"days={info.get('shadowDaysElapsed')} phase={info.get('phase')} "
            f"systemOfRecord={info.get('systemOfRecord')}"
        )
        return 0

    stamp = str(args.at or "").strip() or None
    if not stamp and (args.from_period_close or not args.at):
        stamp = _period_close_shadow_started()
    if stamp:
        state["phase"] = "shadow"
        state["shadow_started_at"] = stamp
        state["note"] = (
            "Shadow clock started for ≥30-day cutover hygiene. "
            "systemOfRecord stays false until operator attestation."
        )
        save_pilot_state(state)
    else:
        ensure_phase_started("shadow")

    info = pilot_info()
    print(json.dumps(info, indent=2))
    print(
        f"\nOK — shadowDaysElapsed={info.get('shadowDaysElapsed')} "
        f"(need >={info.get('minShadowDays')} before supervised). "
        f"systemOfRecord={info.get('systemOfRecord')} (must stay false)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
