"""hal-10612 — Demote surplus widgets to #{page}/ops for zero-scroll overviews."""

from __future__ import annotations

import unittest

from apex_backend import BUILD_ID, build_apex_widgets
from apex_compact_pages_pack import PAGE_FIRST_VIEW_KEEP, partition_first_viewport, select_demoted_widgets


class Hal10612DemoteOpsTests(unittest.TestCase):
    def test_build_id(self) -> None:
        self.assertEqual(BUILD_ID, "hal-10619")

    def test_partition_keeps_only_allowlist(self) -> None:
        widgets = [
            {"id": "financial-command-strip", "type": "financial-command-strip", "label": "Cmd"},
            {"id": "ebitda-station", "type": "ebitda-station", "label": "EBITDA"},
            {"id": "expense-treemap", "type": "treemap", "label": "Expenses"},
            {"id": "financial-dual-trend", "type": "dual-axis-trend", "label": "Trend"},
        ]
        out = partition_first_viewport(widgets, page="financial")
        ids = [w.get("id") for w in out if isinstance(w, dict)]
        self.assertIn("financial-command-strip", ids)
        self.assertIn("financial-dual-trend", ids)
        self.assertNotIn("ebitda-station", ids)
        self.assertNotIn("expense-treemap", ids)
        self.assertIn("financial-ops-open", ids)

    def test_ops_subpage_has_demoted_ids(self) -> None:
        widgets = [
            {"id": "financial-command-strip", "type": "financial-command-strip"},
            {"id": "ebitda-station", "type": "ebitda-station", "label": "EBITDA"},
        ]
        ops = select_demoted_widgets(widgets, page="financial")
        ids = [w.get("id") for w in ops if isinstance(w, dict)]
        self.assertIn("ebitda-station", ids)
        self.assertNotIn("financial-command-strip", ids)
        self.assertIn("financial-overview-open", ids)

    def test_financial_main_is_bounded(self) -> None:
        out = build_apex_widgets("financial", _fill=True)
        widgets = [w for w in (out.get("widgets") or []) if isinstance(w, dict)]
        ids = [w.get("id") for w in widgets]
        # Soft bound: keep set + affordances (ops strip, pending, warming)
        self.assertLessEqual(len(widgets), len(PAGE_FIRST_VIEW_KEEP["financial"]) + 4)
        for demoted in ("ebitda-station", "expense-treemap", "revenue-composition", "deep-audit-status"):
            if demoted in ids:
                self.fail(f"{demoted} should be demoted off financial overview")
        if any(i not in {"warming-bridge"} and not str(i).endswith("-open") for i in ids):
            self.assertIn("financial-ops-open", ids)

    def test_claims_main_demotes_risk_and_queues(self) -> None:
        out = build_apex_widgets("claims", _fill=True)
        ids = [w.get("id") for w in (out.get("widgets") or []) if isinstance(w, dict)]
        for demoted in (
            "claims-risk-analytics",
            "eob-posting-backlog",
            "clinical-signoff-queue",
            "claim-status-lanes",
            "ins-patient-split",
        ):
            self.assertNotIn(demoted, ids)
        if "warming-bridge" not in ids:
            self.assertIn("claims-ops-open", ids)

    def test_taxes_demotes_guidance_and_variance(self) -> None:
        out = build_apex_widgets("taxes", _fill=True)
        ids = [w.get("id") for w in (out.get("widgets") or []) if isinstance(w, dict)]
        self.assertNotIn("c0-import-guidance", ids)
        self.assertNotIn("ebitda-variance-bar", ids)

    def test_financial_ops_subpage_exists(self) -> None:
        out = build_apex_widgets("financial", sub="ops", _fill=True)
        self.assertEqual(out.get("sub"), "ops")
        ids = [w.get("id") for w in (out.get("widgets") or []) if isinstance(w, dict)]
        self.assertIn("financial-overview-open", ids)
        # At least one demoted surface when pack is populated
        self.assertTrue(any(i not in {"financial-overview-open", "financial-ops-empty"} for i in ids) or "financial-ops-empty" in ids)

    def test_empty_not_padded_to_zero(self) -> None:
        widgets = [
            {"id": "ebitda-station", "type": "ebitda-station", "status": "empty", "value": None, "label": "EBITDA"},
        ]
        ops = select_demoted_widgets(widgets, page="financial")
        gap = next((w for w in ops if isinstance(w, dict) and w.get("id") == "ebitda-station"), None)
        self.assertIsNotNone(gap)
        self.assertNotEqual(gap.get("value"), 0)
        self.assertNotEqual(gap.get("value"), "$0")


if __name__ == "__main__":
    unittest.main()
