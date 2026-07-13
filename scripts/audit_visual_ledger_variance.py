#!/usr/bin/env python3
"""HAL-10592 — CLI visual-audit × ledger variance report."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NR2 = ROOT / "NewRidgeFinancial2"
if str(NR2) not in sys.path:
    sys.path.insert(0, str(NR2))

from softdent_visual_ledger_recon import (  # noqa: E402
    format_visual_ledger_recon_reply,
    run_ops_10592_visual_ledger_recon,
)


def main() -> int:
    period = sys.argv[1] if len(sys.argv) > 1 else None
    result = run_ops_10592_visual_ledger_recon(period=period)
    print(format_visual_ledger_recon_reply(result))
    print(json.dumps(result, indent=2, default=str)[:8000])
    cmp_ = result.get("comparison") if isinstance(result.get("comparison"), dict) else {}
    if cmp_.get("thresholdViolated"):
        return 2
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
