"""Tests for SoftDent Excel probe snapshot reader."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from softdent_excel_probe import (
    format_excel_probe_hal_reply,
    latest_excel_probe_snapshot,
    query_touches_excel_probe,
)


class SoftDentExcelProbeTests(unittest.TestCase):
    def test_query_touches_excel_probe(self) -> None:
        self.assertTrue(query_touches_excel_probe("why is excel greyed in SoftDent"))
        self.assertTrue(query_touches_excel_probe("run excel probe for morning bundle"))
        self.assertFalse(query_touches_excel_probe("pull account transactions excel"))

    def test_latest_probe_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            snap = latest_excel_probe_snapshot(log_dir=Path(tmp))
        self.assertTrue(snap.get("ok"))
        self.assertFalse(snap.get("hasProbe"))
        self.assertIsNone(snap.get("excelAvailable"))

    def test_latest_probe_reads_newest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old = root / "softdent_excel_output_options_probe_old.json"
            new = root / "softdent_excel_output_options_probe_new.json"
            old.write_text(
                json.dumps({"ok": True, "excelAvailable": False, "at": "old"}),
                encoding="utf-8",
            )
            new.write_text(
                json.dumps({"ok": True, "excelAvailable": True, "at": "new"}),
                encoding="utf-8",
            )
            snap = latest_excel_probe_snapshot(log_dir=root)
        self.assertTrue(snap.get("hasProbe"))
        self.assertTrue(snap.get("excelAvailable"))
        self.assertEqual(snap.get("at"), "new")

    def test_hal_reply_mentions_runbook(self) -> None:
        text = format_excel_probe_hal_reply("excel probe")
        self.assertIn("softdent_excel_enablement_nr2.md", text)
        self.assertIn("empty", text.lower())


if __name__ == "__main__":
    unittest.main()
