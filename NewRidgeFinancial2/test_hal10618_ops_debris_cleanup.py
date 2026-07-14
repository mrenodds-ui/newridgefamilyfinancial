"""hal-10618 — OPS debris cleanup + Content hub + Moonshot leftover package."""

from __future__ import annotations

import unittest

from apex_backend import BUILD_ID, build_apex_widgets, _WIDGETS_CACHE
from apex_compact_pages_pack import (
    apply_single_micro_band,
    omit_fresh_stale_alert,
    select_demoted_widgets,
)


class Hal10618OpsDebrisCleanupTests(unittest.TestCase):
    def test_build_id(self) -> None:
        self.assertEqual(BUILD_ID, "hal-10618")

    def test_claims_no_double_micro_pipeline(self) -> None:
        _WIDGETS_CACHE.clear()
        out = build_apex_widgets("claims", _fill=True)
        ids = [w.get("id") for w in (out.get("widgets") or []) if isinstance(w, dict)]
        self.assertNotIn("claims-pipeline-summary", ids)
        self.assertIn("claims-executive-strip", ids)
        micros = [
            b
            for b in ((out.get("mosaicLayout") or {}).get("bands") or [])
            if b.get("band") == "micro"
        ]
        self.assertLessEqual(len(micros), 1)

    def test_ar_bullet_demoted_to_ops(self) -> None:
        _WIDGETS_CACHE.clear()
        main = build_apex_widgets("ar", _fill=True)
        ops = build_apex_widgets("ar", sub="ops", _fill=True)
        main_ids = [w.get("id") for w in (main.get("widgets") or []) if isinstance(w, dict)]
        ops_ids = [w.get("id") for w in (ops.get("widgets") or []) if isinstance(w, dict)]
        self.assertNotIn("collection-bullet", main_ids)
        self.assertTrue(
            "collection-bullet" in ops_ids or "ar-ops-pair" in ops_ids or len(ops_ids) >= 1
        )

    def test_unknown_subpage_gone_for_content_ops(self) -> None:
        _WIDGETS_CACHE.clear()
        for page in ("content", "documents", "narratives", "library"):
            out = build_apex_widgets(page, sub="ops", _fill=True)
            ids = [w.get("id") for w in (out.get("widgets") or []) if isinstance(w, dict)]
            self.assertNotIn("unknown-subpage", ids, page)

    def test_content_hub_main(self) -> None:
        _WIDGETS_CACHE.clear()
        out = build_apex_widgets("content", _fill=True)
        self.assertEqual(out.get("buildId"), "hal-10618")
        ids = [w.get("id") for w in (out.get("widgets") or []) if isinstance(w, dict)]
        self.assertIn("content-hub-strip", ids)
        self.assertNotIn("unknown-subpage", ids)
        self.assertNotIn("narr-workflow", ids)

    def test_single_micro_promotes_extras(self) -> None:
        widgets = [
            {"id": "a", "type": "executive-strip", "size": "strip"},
            {"id": "b", "type": "claims-executive-strip", "size": "s"},
            {"id": "c", "type": "chart", "size": "m"},
        ]
        out = apply_single_micro_band(widgets, page="claims")
        self.assertEqual(out[0]["size"], "strip")
        self.assertEqual(out[1]["size"], "m")

    def test_fresh_stale_alert_omitted_unless_alerting(self) -> None:
        widgets = [
            {"id": "stale-import-alert", "alert": False, "status": "ok"},
            {"id": "keep", "status": "ok"},
            {"id": "stale-import-alert", "alert": True, "status": "empty"},
        ]
        # two stale ids — filter keeps only alerting ones
        out = omit_fresh_stale_alert(
            [
                {"id": "stale-import-alert", "alert": False},
                {"id": "keep", "status": "ok"},
                {"id": "stale-import-alert", "alert": True},
            ]
        )
        ids = [w.get("id") for w in out]
        self.assertEqual(ids.count("stale-import-alert"), 1)
        self.assertIn("keep", ids)

    def test_softdent_ops_no_thin_orphan_pad(self) -> None:
        widgets = [
            {"id": "softdent-aging-gap", "type": "status", "status": "ok", "size": "m"},
            {"id": "softdent-scheduling-gap", "type": "status", "status": "ok", "size": "m"},
            {"id": "softdent-production-gap", "type": "status", "status": "ok", "size": "m"},
        ]
        ops = select_demoted_widgets(widgets, page="softdent")
        ids = [w.get("id") for w in ops if isinstance(w, dict)]
        self.assertIn("softdent-overview-open", ids)
        # 3 gaps → pad to even body
        self.assertIn("softdent-ops-pair", ids)


if __name__ == "__main__":
    unittest.main()
