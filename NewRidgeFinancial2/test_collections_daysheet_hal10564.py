"""Moonshot DEF-001 Collections/Daysheet after Phase 5 (hal-10564)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from apex_backend import BUILD_ID, resolve_hal_board_actions
from apex_financial_console_pack import build_revenue_composition
from apex_softdent_hardening_pack import (
    GAP_COLLECTIONS_PENDING,
    assess_collections_gap,
    collections_gap_widget,
    format_collections_gap_reply,
    scan_collections_export_inbox,
)
from nr2_hal_gateway import try_local_policy_reply

# ERA enrich may upgrade pending → ERA_835_AVAILABLE when live 835s exist
_PENDING_CODES = {GAP_COLLECTIONS_PENDING, "ERA_835_AVAILABLE"}


def _bundle_pending() -> dict:
    return {
        "softdent": {
            "dashboard": {
                "rows": [
                    {
                        "period": "2026-07",
                        "production": 50000,
                        "collectionsPending": True,
                        "insurance": 0,
                        "patient": 0,
                    }
                ]
            }
        },
        "diagnostics": {"summary": {"connected": 3, "total": 5, "missing": 2}},
        "loadedAt": "2026-07-12T12:00:00Z",
    }


class CollectionsDaysheetHal10564Tests(unittest.TestCase):
    def test_build_id(self):
        self.assertEqual(BUILD_ID, "hal-10564")

    def test_inbox_scan_finds_collections_named_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Collections_202607.csv").write_text("a,b\n1,2\n", encoding="utf-8")
            with mock.patch.dict(
                "os.environ",
                {"SOFTDENT_REPORT_EXPORTS": str(root), "NR2_SOFTDENT_EXPORT_SOURCE": ""},
                clear=False,
            ):
                inbox = scan_collections_export_inbox(limit=8)
            self.assertGreaterEqual(inbox.get("matchCount") or 0, 1)
            self.assertTrue(inbox.get("hasCollectionsLikeFile"))
            self.assertTrue(any(m.get("name") == "Collections_202607.csv" for m in inbox.get("matches") or []))

    def test_gap_includes_export_inbox(self):
        gap = assess_collections_gap(_bundle_pending())
        self.assertIn(gap.get("gapCode"), _PENDING_CODES)
        self.assertFalse(gap.get("healthy"))
        self.assertIn("exportInbox", gap)
        self.assertIsNone(gap.get("collections"))
        text = format_collections_gap_reply(gap)
        self.assertIn("DEF-001", text)
        self.assertIn("SoftDentReportExports", text)
        self.assertIn("Export inbox:", text)

    def test_revenue_composition_period_aware_empty(self):
        w = build_revenue_composition(_bundle_pending())
        self.assertEqual(w.get("status"), "empty")
        self.assertIn(w.get("gapCode"), _PENDING_CODES)
        msg = str(w.get("emptyMessage") or "")
        self.assertIn("2026-07", msg)
        self.assertRegex(msg.lower().replace("≠", "not "), r"empty|pending|gap")
        self.assertIn("SoftDentReportExports", msg)

    def test_financial_gap_strip_contract(self):
        rev = build_revenue_composition(_bundle_pending())
        gap_w = collections_gap_widget(_bundle_pending())
        self.assertEqual(rev.get("status"), "empty")
        self.assertEqual(gap_w.get("status"), "empty")
        self.assertEqual(gap_w.get("id"), "softdent-collections-gap")
        self.assertEqual(rev.get("def"), "DEF-001")

    def test_hal_board_revenue_composition_empty(self):
        with mock.patch(
            "apex_backend._load_reports_and_bundle",
            return_value=({}, _bundle_pending(), None),
        ):
            r = resolve_hal_board_actions(
                {"query": "why is revenue composition empty?", "page": "hal"}
            )
        self.assertTrue(r.get("handled"))
        reply = str(r.get("reply") or "")
        self.assertIn("DEF-001", reply)
        actions = r.get("actions") or []
        self.assertTrue(any(a.get("widgetId") == "revenue-composition" for a in actions))

    def test_local_policy_def001(self):
        with mock.patch(
            "apex_backend._load_reports_and_bundle",
            return_value=({}, _bundle_pending(), None),
        ):
            hit = try_local_policy_reply("Why is revenue composition empty?")
        self.assertIsNotNone(hit)
        self.assertEqual(hit.get("intent"), "policy:def-001-collections")
        self.assertIn("DEF-001", hit.get("text") or "")


if __name__ == "__main__":
    unittest.main()
