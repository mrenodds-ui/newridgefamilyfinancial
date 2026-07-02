#!/usr/bin/env python3
"""Exit 0 when NR2 direct-first import bundle has dashboard + A/R rows."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from import_loader import load_import_bundle  # noqa: E402


def main() -> int:
    bundle = load_import_bundle(sync=False, deep=False)
    softdent = bundle.get("softdent") or {}
    summary = {
        "importMode": bundle.get("importMode"),
        "dashboardRows": len(((softdent.get("dashboard") or {}).get("rows") or [])),
        "claimsRows": len(((softdent.get("claims") or {}).get("rows") or [])),
        "arRows": len(((softdent.get("ar") or {}).get("rows") or [])),
    }
    print(json.dumps(summary))
    return 0 if summary["dashboardRows"] > 0 and summary["arRows"] > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
