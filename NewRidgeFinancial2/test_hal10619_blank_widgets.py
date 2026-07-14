"""hal-10619 — blank all Apex page widgets (empty stages)."""

from __future__ import annotations

import os
import unittest

from apex_backend import APEX_PAGES, BUILD_ID, build_apex_widgets, _WIDGETS_CACHE


class Hal10619BlankWidgetsTests(unittest.TestCase):
    def test_build_id(self) -> None:
        self.assertEqual(BUILD_ID, "hal-10619")

    def test_blank_flag_empties_every_page(self) -> None:
        prev = os.environ.get("NR2_APEX_BLANK_WIDGETS")
        os.environ["NR2_APEX_BLANK_WIDGETS"] = "1"
        try:
            _WIDGETS_CACHE.clear()
            for page in APEX_PAGES:
                out = build_apex_widgets(page, _fill=True)
                self.assertEqual(out.get("buildId"), "hal-10619", page)
                self.assertTrue(out.get("blankWidgets"), page)
                self.assertEqual(out.get("widgets"), [], page)
                layout = out.get("mosaicLayout") or {}
                self.assertEqual(layout.get("mode"), "empty", page)
                self.assertEqual(layout.get("bands") or [], [], page)
            ops = build_apex_widgets("softdent", sub="ops", _fill=True)
            self.assertEqual(ops.get("widgets"), [])
            self.assertTrue(ops.get("blankWidgets"))
        finally:
            if prev is None:
                os.environ.pop("NR2_APEX_BLANK_WIDGETS", None)
            else:
                os.environ["NR2_APEX_BLANK_WIDGETS"] = prev
            _WIDGETS_CACHE.clear()


if __name__ == "__main__":
    unittest.main()
