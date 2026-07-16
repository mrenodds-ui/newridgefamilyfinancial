#!/usr/bin/env python3
"""Refresh shadow period-close beam snapshot to match live money beams.

Use when VERIFY BEAM shows MISMATCH because imports refreshed since last close
(e.g. SoftDent AR $7,714 → $60,411). Does not pull SoftDent GUI unless --pull-softdent.

Usage:
  python scripts/refresh_period_close_beam.py
  python scripts/refresh_period_close_beam.py --status
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NR2 = REPO / "NewRidgeFinancial2"
if str(NR2) not in sys.path:
    sys.path.insert(0, str(NR2))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--status", action="store_true", help="Show beam-verify + period close status only")
    ap.add_argument("--pull-softdent", action="store_true", help="Include SoftDent GUI morning bundle pull")
    args = ap.parse_args()

    from hal_brain_tools import beam_desk_proof

    proof = beam_desk_proof()
    if args.status:
        print(json.dumps(proof, indent=2, default=str))
        return 0 if proof.get("deskProof") == "MATCH" else 1

    if proof.get("deskProof") == "MATCH":
        print(json.dumps({"ok": True, "deskProof": "MATCH", "note": "No refresh needed."}, indent=2))
        return 0

    print("Before refresh:")
    print(json.dumps(
        {
            "deskProof": proof.get("deskProof"),
            "drift": proof.get("drift"),
            "refreshCloseSuggested": proof.get("refreshCloseSuggested"),
        },
        indent=2,
        default=str,
    ))

    from daily_closeout import run_period_close

    result = run_period_close(
        actor="refresh_period_close_beam",
        auto=True,
        pull_softdent=bool(args.pull_softdent),
    )
    after = beam_desk_proof()
    out = {
        "ok": bool(result.get("ok")) and after.get("deskProof") == "MATCH",
        "close": {
            "status": result.get("status"),
            "dataBeamHash": result.get("dataBeamHash"),
            "softdentDisplay": result.get("softdentDisplay"),
            "qbDisplay": result.get("qbDisplay"),
        },
        "deskProof": after.get("deskProof"),
        "drift": after.get("drift"),
        "emptyNotZero": True,
    }
    print(json.dumps(out, indent=2, default=str))
    return 0 if out["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
