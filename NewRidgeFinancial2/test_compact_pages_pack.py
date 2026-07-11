"""Tests for Moonshot compact professional pages pack."""

from __future__ import annotations

import unittest

from apex_compact_pages_pack import (
    apply_collapse_empty_all,
    claims_pipeline_summary_widget,
    collapse_empty_large,
    normalize_first_viewport,
)


class CollapseEmptyTests(unittest.TestCase):
    def test_empty_large_collapses(self) -> None:
        w = {"id": "x", "size": "xl", "status": "empty", "label": "X"}
        out = collapse_empty_large(w)
        self.assertEqual(out["size"], "strip")
        self.assertTrue(out["compact"])

    def test_loading_not_collapsed(self) -> None:
        w = {"id": "x", "size": "xl", "status": "loading"}
        self.assertEqual(collapse_empty_large(w)["size"], "xl")

    def test_skeleton_flag_not_collapsed(self) -> None:
        w = {"id": "x", "size": "full", "status": "empty", "isSkeleton": True}
        self.assertEqual(collapse_empty_large(w)["size"], "full")

    def test_populated_unchanged(self) -> None:
        w = {"id": "x", "size": "l", "status": "ok"}
        self.assertEqual(collapse_empty_large(w)["size"], "l")

    def test_opt_out(self) -> None:
        w = {"id": "x", "size": "l", "status": "empty", "collapseWhenEmpty": False}
        self.assertEqual(collapse_empty_large(w)["size"], "l")

    def test_apply_all(self) -> None:
        widgets = [
            {"id": "a", "size": "xl", "status": "empty"},
            {"id": "b", "size": "m", "status": "ok"},
        ]
        out = apply_collapse_empty_all(widgets)
        self.assertEqual(out[0]["size"], "strip")
        self.assertEqual(out[1]["size"], "m")


class FirstViewportTests(unittest.TestCase):
    def test_hal_chat_stays_l(self) -> None:
        widgets = [
            {"id": "h", "type": "kpi", "size": "s", "status": "ok"},
            {"id": "hal-ask", "type": "hal-chat", "size": "m", "status": "ok"},
            {"id": "x", "type": "chart", "size": "xl", "status": "ok"},
        ]
        out = normalize_first_viewport(widgets, page="hal")
        self.assertEqual(out[1]["size"], "l")
        self.assertEqual(out[2]["size"], "m")  # second large demoted after chat took the l slot

    def test_xl_demoted_above_fold(self) -> None:
        widgets = [{"id": f"w{i}", "type": "chart", "size": "xl", "status": "ok"} for i in range(3)]
        out = normalize_first_viewport(widgets, page="financial")
        self.assertEqual(out[0]["size"], "l")
        self.assertEqual(out[1]["size"], "m")


class ClaimsPipelineTests(unittest.TestCase):
    def test_summary_pills(self) -> None:
        w = claims_pipeline_summary_widget(
            {"submitted": 2, "pendingReview": 1, "eraMatched": 0, "denied": 3, "paid": 4},
            available=True,
        )
        self.assertEqual(w["id"], "claims-pipeline-summary")
        self.assertEqual(w["size"], "s")
        self.assertEqual(w["navHash"], "claims/kanban")
        self.assertEqual(len(w["pills"]), 4)


if __name__ == "__main__":
    unittest.main()
