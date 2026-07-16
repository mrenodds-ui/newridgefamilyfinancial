"""OPS helper — ingest ERA-835 files from the wired inbox.

Drop real payer 835/EDI/TXT into any of:
  app_data\\nr2\\office\\era_inbox\\drop
  C:\\SoftDentFinancialExports\\era
  C:\\SoftDentReportExports\\era
  (or NR2_ERA835_INBOX)

Then:
  python scripts/run_era_inbox_ingest_ops.py

Read-only SoftDent. Empty inbox ≠ $0 — never invent remittance.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "NewRidgeFinancial2"))

from nr2_era_inbox import era_suggestions, ingest_era_inbox, scan_era_inbox  # noqa: E402


def main() -> int:
    scan = scan_era_inbox(ensure_dirs=True)
    print("=== SCAN ===")
    print(json.dumps(scan, indent=2, default=str))
    if scan.get("empty"):
        print("\nInbox empty — drop real ERA 835 files first. Empty != $0.")
        print("Drop paths:")
        for root in scan.get("roots") or []:
            print(f"  - {root}")
        return 0
    result = ingest_era_inbox(ensure_dirs=True)
    print("\n=== INGEST ===")
    print(json.dumps(result, indent=2, default=str))
    sug = era_suggestions(limit=10)
    print("\n=== SUGGESTIONS (QB manual — no SoftDent write-back) ===")
    print(json.dumps(sug, indent=2, default=str))
    ingested = int(result.get("ingested") or 0)
    rows = int(result.get("rowsInserted") or 0)
    if ingested <= 0 or rows <= 0:
        print("\nWarning: files detected but no rows inserted — check file format.")
        return 1
    print("\nOK — ERA inbox ingested (proposal only; no SoftDent write-back).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
