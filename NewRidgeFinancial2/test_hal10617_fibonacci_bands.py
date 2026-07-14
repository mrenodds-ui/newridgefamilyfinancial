"""hal-10619 — Fibonacci band packing so widgets fit edge-to-edge on all pages."""

from __future__ import annotations

import unittest

from apex_backend import BUILD_ID, build_apex_widgets, _WIDGETS_CACHE
from apex_compact_pages_pack import pack_fibonacci_bands


class Hal10617FibonacciBandsTests(unittest.TestCase):
    def test_build_id(self) -> None:
        self.assertEqual(BUILD_ID, "hal-10619")

    def test_pack_strip_then_pairs(self) -> None:
        widgets = [
            {"id": "a-strip", "type": "executive-strip", "size": "strip", "status": "ok"},
            {"id": "b-m", "type": "chart", "size": "m", "status": "ok"},
            {"id": "c-m", "type": "chart", "size": "m", "status": "ok"},
            {"id": "d-m", "type": "chart", "size": "m", "status": "ok"},
            {"id": "e-m", "type": "chart", "size": "m", "status": "ok"},
        ]
        out, layout = pack_fibonacci_bands(widgets, page="financial")
        bands = layout.get("bands") or []
        self.assertEqual(bands[0]["band"], "micro")
        self.assertEqual(bands[0]["tiles"][0]["tileClass"], "tile-100")
        self.assertEqual(bands[1]["band"], "secondary")
        self.assertEqual([t["tileClass"] for t in bands[1]["tiles"]], ["tile-50", "tile-50"])
        self.assertEqual(bands[2]["band"], "secondary")
        self.assertEqual([t["tileClass"] for t in bands[2]["tiles"]], ["tile-50", "tile-50"])
        by_id = {w["id"]: w for w in out if isinstance(w, dict)}
        self.assertEqual(by_id["b-m"]["tileClass"], "tile-50")
        self.assertEqual(by_id["a-strip"]["band"], "micro")

    def test_hal_chat_owns_primary(self) -> None:
        widgets = [
            {"id": "hal-import-health", "type": "status", "size": "strip", "status": "ok"},
            {"id": "hal-ask", "type": "hal-chat", "size": "l", "status": "ok"},
            {"id": "hal-recommended-actions", "type": "action-list", "size": "m", "status": "ok"},
        ]
        _out, layout = pack_fibonacci_bands(widgets, page="hal")
        kinds = [b["band"] for b in (layout.get("bands") or [])]
        self.assertIn("primary", kinds)
        primary = next(b for b in layout["bands"] if b["band"] == "primary")
        self.assertEqual(primary["tiles"][0]["id"], "hal-ask")
        self.assertEqual(primary["height"], 320)

    def test_all_pages_emit_mosaic_layout(self) -> None:
        _WIDGETS_CACHE.clear()
        pages = (
            "financial",
            "taxes",
            "softdent",
            "claims",
            "ar",
            "quickbooks",
            "office-manager",
            "hal",
        )
        for page in pages:
            payload = build_apex_widgets(page, _fill=True)
            self.assertEqual(payload.get("buildId"), "hal-10619", page)
            layout = payload.get("mosaicLayout") or {}
            self.assertEqual(layout.get("mode"), "fibonacci", page)
            bands = layout.get("bands") or []
            self.assertGreaterEqual(len(bands), 1, page)
            widgets = payload.get("widgets") or []
            tiled = [w for w in widgets if isinstance(w, dict) and w.get("tileClass")]
            self.assertGreaterEqual(len(tiled), 1, page)
            # Paired bands must be edge-to-edge (50/50 or 33/33/33), not orphan gaps.
            for band in bands:
                tiles = band.get("tiles") or []
                if len(tiles) == 2:
                    self.assertEqual({t.get("tileClass") for t in tiles}, {"tile-50"}, page)
                if len(tiles) == 3:
                    self.assertEqual({t.get("tileClass") for t in tiles}, {"tile-33"}, page)

    def test_ops_also_banded(self) -> None:
        _WIDGETS_CACHE.clear()
        payload = build_apex_widgets("softdent", sub="ops", _fill=True)
        layout = payload.get("mosaicLayout") or {}
        self.assertEqual(layout.get("mode"), "fibonacci")
        self.assertGreaterEqual(len(layout.get("bands") or []), 1)


if __name__ == "__main__":
    unittest.main()
