"""hal-10615 — omit chronic empty widgets and keep Ops zero-scroll compact."""

from __future__ import annotations

import unittest

from apex_backend import BUILD_ID, build_apex_widgets
from apex_compact_pages_pack import (
    OMIT_UNTIL_SOURCE_IDS,
    PAGE_OPS_KEEP,
    omit_until_source_widgets,
    select_demoted_widgets,
)


class Hal10615OmitEmptyCompactTests(unittest.TestCase):
    def test_build_id(self) -> None:
        self.assertEqual(BUILD_ID, "hal-10616")

    def test_omit_chronic_empty_ids(self) -> None:
        widgets = [
            {"id": "claims-era-gauge", "type": "claims-era-gauge", "status": "empty"},
            {"id": "denial-pareto", "type": "pareto-chart", "status": "empty"},
            {"id": "claims-executive-strip", "type": "claims-executive-strip", "status": "ok"},
            {"id": "warming-bridge", "type": "status", "status": "empty"},
        ]
        out = omit_until_source_widgets(widgets, page="claims")
        ids = [w.get("id") for w in out if isinstance(w, dict)]
        self.assertEqual(ids, ["claims-executive-strip"])
        for bad in OMIT_UNTIL_SOURCE_IDS & {"claims-era-gauge", "denial-pareto", "warming-bridge"}:
            self.assertNotIn(bad, ids)

    def test_softdent_ops_is_capped(self) -> None:
        keep = PAGE_OPS_KEEP["softdent"]
        widgets = [{"id": wid, "type": "status", "status": "ok", "label": wid} for wid in keep]
        widgets += [
            {"id": "softdent-gold-payment-pipeline", "type": "status", "status": "warn", "label": "Gold"},
            {"id": "softdent-print-preview-audit", "type": "status", "status": "ok", "label": "Preview"},
            {"id": "softdent-patient-dossier", "type": "patient-dossier-card", "status": "warn"},
        ]
        ops = select_demoted_widgets(widgets, page="softdent")
        ids = [w.get("id") for w in ops if isinstance(w, dict)]
        self.assertIn("softdent-overview-open", ids)
        self.assertTrue(any(i in keep for i in ids))
        self.assertNotIn("softdent-gold-payment-pipeline", ids)
        self.assertNotIn("softdent-print-preview-audit", ids)
        self.assertNotIn("softdent-ops-more-omitted", ids)

    def test_claims_main_omits_empty_source_widgets(self) -> None:
        out = build_apex_widgets("claims", _fill=True)
        ids = [w.get("id") for w in (out.get("widgets") or []) if isinstance(w, dict)]
        for bad in ("claims-era-gauge", "denial-pareto", "verification-matrix", "warming-bridge"):
            self.assertNotIn(bad, ids)

    def test_softdent_ops_count_bounded(self) -> None:
        out = build_apex_widgets("softdent", sub="ops", _fill=True)
        widgets = [w for w in (out.get("widgets") or []) if isinstance(w, dict)]
        from apex_compact_pages_pack import MAX_OPS_VIEWPORT_WIDGETS

        self.assertLessEqual(len(widgets), MAX_OPS_VIEWPORT_WIDGETS)


if __name__ == "__main__":
    unittest.main()
