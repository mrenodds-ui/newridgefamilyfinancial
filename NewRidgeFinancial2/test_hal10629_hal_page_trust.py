"""hal-10629 — HAL trust pack: Sync CTA, owner logs, history range, Ops checklist."""

from __future__ import annotations

import unittest

from apex_backend import BUILD_ID, _WIDGETS_CACHE, build_apex_widgets
from apex_program_improve_pack import _save_json
from apex_subpages_wave5_pack import (
    STORE_KEY_HAL_HISTORY,
    append_hal_history_entry,
    build_hal_history,
    build_hal_ops,
    build_hal_system_logs,
)


class Hal10629HalPageTrustTests(unittest.TestCase):
    def test_build_id(self) -> None:
        self.assertEqual(BUILD_ID, "hal-10629")

    def test_chat_sync_cta_when_missing(self) -> None:
        _WIDGETS_CACHE.clear()
        # Force fill with empty reports/bundle via direct builder path
        from apex_backend import _hal_widgets

        widgets = _hal_widgets(
            {},
            {
                "diagnostics": {
                    "summary": {
                        "connected": 1,
                        "partial": 1,
                        "missing": 3,
                        "stale": 0,
                        "total": 10,
                    }
                }
            },
        )
        ids = [w.get("id") for w in widgets]
        self.assertIn("hal-sync-cta", ids)
        self.assertIn("hal-ask", ids)
        cta = next(w for w in widgets if w.get("id") == "hal-sync-cta")
        self.assertTrue(cta.get("syncImports"))
        self.assertEqual(cta.get("badge"), "warn")

    def test_history_range_filters(self) -> None:
        _save_json(STORE_KEY_HAL_HISTORY, {"entries": []})
        append_hal_history_entry("operator", "What is import health?")
        append_hal_history_entry("system", "Sync & review missing imports requested from HAL.")
        widgets = build_hal_history({}, {})
        feed = next(w for w in widgets if w.get("type") == "hal-history-feed")
        self.assertIn("today", feed.get("filters") or [])
        self.assertIn("week", feed.get("filters") or [])
        entries = feed.get("entries") or []
        self.assertTrue(any(e.get("range") == "today" for e in entries))
        self.assertTrue(any(e.get("role") == "system" for e in entries))

    def test_system_logs_owner_filters(self) -> None:
        bundle = {
            "diagnostics": {
                "summary": {"connected": 1, "partial": 0, "missing": 2, "stale": 0, "total": 4},
                "datasets": [
                    {
                        "datasetKey": "softdent.ar",
                        "status": "missing",
                        "severity": "critical",
                        "automated": True,
                        "rowCount": 0,
                        "detail": "Dataset file not found.",
                        "gapCode": "SOFTDENT_AR_MISSING",
                    },
                    {
                        "datasetKey": "quickbooks.revenue",
                        "status": "missing",
                        "severity": "critical",
                        "automated": True,
                        "rowCount": 0,
                        "detail": "Revenue export missing.",
                        "gapCode": "QB_REVENUE_MISSING",
                    },
                ],
            }
        }
        widgets = build_hal_system_logs({}, bundle)
        console = next(w for w in widgets if w.get("type") == "hal-sys-console")
        self.assertIn("softdent", console.get("ownerFilters") or [])
        lines = console.get("lines") or []
        self.assertTrue(any(ln.get("owner") == "softdent" for ln in lines))
        self.assertTrue(any(ln.get("owner") == "quickbooks" for ln in lines))
        self.assertTrue(any(ln.get("gapCode") for ln in lines))

    def test_ops_checklist_and_rail(self) -> None:
        bundle = {
            "diagnostics": {
                "summary": {"connected": 1, "partial": 0, "missing": 2, "stale": 0, "total": 5},
                "datasets": [
                    {
                        "datasetKey": "softdent.claims",
                        "status": "missing",
                        "severity": "critical",
                        "automated": True,
                        "rowCount": 0,
                    }
                ],
            }
        }
        widgets = build_hal_ops({}, bundle)
        types = [w.get("type") for w in widgets]
        self.assertIn("hal-sub-strip", types)
        self.assertIn("status", types)
        self.assertIn("hal-chat", types)
        checklist = next(w for w in widgets if w.get("id") == "hal-ops-checklist")
        self.assertTrue(checklist.get("syncImports"))
        self.assertTrue(checklist.get("checks"))


if __name__ == "__main__":
    unittest.main()
