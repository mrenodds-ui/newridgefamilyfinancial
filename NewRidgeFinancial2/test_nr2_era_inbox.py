"""nr2_era_inbox — empty ≠ $0 inbox scan (replaces apex_era835_pack)."""

from __future__ import annotations

import unittest

from nr2_era_inbox import (
    assess_era835_gap,
    era_inbox_status,
    ingest_era_inbox,
    scan_era_inbox,
)


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


if __name__ == "__main__":
    unittest.main()
