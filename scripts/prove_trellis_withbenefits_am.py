"""Prove Trellis ClearCoverage withBenefits > 0 after 1:00 AM scrape (2:00 AM check).

Usage (Mon–Thu after 1:00 AM Trellis --same-day --verify; Task Scheduler at 2:00 AM):
  python scripts/prove_trellis_withbenefits_am.py
  python scripts/prove_trellis_withbenefits_am.py --date 2026-07-17

Exit 0 when withBenefits > 0; exit 2 when still status-only; exit 1 on hard error.
Counts only — never invent deductible / $0. SoftDent READ-ONLY.
"""

from __future__ import annotations

import argparse
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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--date", help="YYYY-MM-DD schedule date to prove")
    args = ap.parse_args()

    from nr2_trellis_nightly import trellis_am_benefits_proof

    payload = trellis_am_benefits_proof(target_date=args.date)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = OUT / f"trellis_withbenefits_am_proof_{stamp}.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"Wrote {out_path}", flush=True)

    if payload.get("passed"):
        return 0
    if any((r or {}).get("ok") for r in payload.get("candidates") or []):
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
