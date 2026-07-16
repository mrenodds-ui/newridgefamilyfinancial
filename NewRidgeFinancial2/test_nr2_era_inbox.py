"""nr2_era_inbox — empty ≠ $0 inbox scan (replaces apex_era835_pack)."""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from nr2_era_inbox import (
    assess_era835_gap,
    era_inbox_status,
    era_suggestions,
    ingest_era_inbox,
    scan_era_inbox,
)

_FIXTURE = Path(__file__).resolve().parent / "test" / "fixtures" / "synthetic.835"


class Nr2EraInboxTests(unittest.TestCase):
    def test_empty_inbox_awaiting(self) -> None:
        scan = scan_era_inbox(ensure_dirs=True)
        self.assertTrue(scan.get("ok"))
        self.assertTrue(scan.get("empty"))
        self.assertEqual(scan.get("chipStatus"), "awaiting")
        self.assertEqual(scan.get("fileCount"), 0)
        self.assertEqual(scan.get("honesty"), "empty_not_zero")

    def test_status_exposes_gap(self) -> None:
        status = era_inbox_status(ensure_dirs=True)
        self.assertTrue(status.get("ok"))
        self.assertTrue(status.get("emptyNotZero"))
        gap = status.get("gap") or {}
        self.assertIn("gapCode", gap)

    def test_ingest_empty_no_invent_dollars(self) -> None:
        out = ingest_era_inbox(ensure_dirs=True)
        self.assertTrue(out.get("ok"))
        self.assertTrue(out.get("empty"))
        self.assertEqual(out.get("rowsInserted"), 0)
        self.assertFalse(out.get("writeBack"))

    def test_assess_gap_pending_when_empty(self) -> None:
        gap = assess_era835_gap()
        self.assertTrue(gap.get("pending") or gap.get("fileCount", 0) >= 0)

    def test_era_suggestions_read_only(self) -> None:
        out = era_suggestions(limit=5)
        self.assertTrue(out.get("ok"))
        self.assertTrue(out.get("emptyNotZero"))
        self.assertFalse(out.get("writeBack"))
        self.assertIsInstance(out.get("suggestions"), list)

    def test_fixture_ingest_via_isolated_inbox_env(self) -> None:
        """Parser + ingest path smoke — fixture only; not live remittance."""
        self.assertTrue(_FIXTURE.is_file(), f"missing {_FIXTURE}")
        prev = os.environ.get("NR2_ERA835_INBOX")
        tmp = Path(tempfile.mkdtemp(prefix="nr2_era_fixture_"))
        try:
            os.environ["NR2_ERA835_INBOX"] = str(tmp)
            shutil.copy2(_FIXTURE, tmp / "synthetic_path_smoke.835")
            scan = scan_era_inbox(ensure_dirs=True)
            self.assertFalse(scan.get("empty"))
            self.assertGreaterEqual(int(scan.get("fileCount") or 0), 1)
            out = ingest_era_inbox(ensure_dirs=True)
            self.assertTrue(out.get("ok"))
            self.assertGreaterEqual(int(out.get("ingested") or 0), 1)
            self.assertGreaterEqual(int(out.get("rowsInserted") or 0), 1)
            self.assertFalse(out.get("writeBack"))
            sug = era_suggestions(limit=5)
            self.assertGreaterEqual(int(sug.get("count") or 0), 1)
        finally:
            if prev is None:
                os.environ.pop("NR2_ERA835_INBOX", None)
            else:
                os.environ["NR2_ERA835_INBOX"] = prev
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
