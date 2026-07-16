"""Exit 0 when latest attended SoftDent Excel probe reports excelAvailable=true.

Usage:
  python scripts/prove_excel_ready.py

Exit codes:
  0 — excelAvailable is true (morning bundle may proceed per runbook)
  2 — no probe on record yet (run probe_softdent_excel_output_options.py)
  1 — probe exists but Excel still blocked
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NR2 = REPO / "NewRidgeFinancial2"

if str(NR2) not in sys.path:
    sys.path.insert(0, str(NR2))


def main() -> int:
    from softdent_excel_probe import latest_excel_probe_snapshot

    snap = latest_excel_probe_snapshot()
    print(json.dumps(snap, indent=2))
    if snap.get("excelAvailable") is True:
        return 0
    if not snap.get("hasProbe"):
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
