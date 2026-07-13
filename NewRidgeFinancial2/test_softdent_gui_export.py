"""SoftDent GUI export helpers — unit tests (no live SoftDent required)."""

from __future__ import annotations

import unittest
from datetime import date
from pathlib import Path
from unittest import mock

from softdent_gui_export import (
    load_menu_map,
    resolve_menu_keys,
    run_catalog_exports,
    run_safe_period_exports,
    softdent_report_preview_visible,
)


class SoftDentGuiExportTests(unittest.TestCase):
    def test_menu_map_phase1_ids(self):
        catalog = load_menu_map()
        self.assertEqual(catalog.get("version"), 1)
        order = catalog.get("phase1_order") or []
        for rid in ("register", "collections", "transactions", "daysheet", "aging"):
            self.assertIn(rid, order)
            self.assertIn(rid, catalog["reports"])
            keys = resolve_menu_keys(catalog["reports"][rid])
            self.assertTrue(keys)

    def test_print_preview_mdi_and_page_rule(self):
        self.assertTrue(
            softdent_report_preview_visible(
                ["CS SoftDent Software v19.1.4 - [INSURANCE INCOME REPORT]"]
            )
        )
        self.assertFalse(softdent_report_preview_visible(["Sorting Report"]))
        self.assertFalse(softdent_report_preview_visible(["CS SoftDent Software v19.1.4"]))
        note = (load_menu_map().get("notes") or [])[4]
        self.assertIn("PageDown", note)
        ipa = load_menu_map()["reports"]["insurance_payment_analysis"]
        self.assertEqual(ipa.get("outputMode"), "print_preview_only")
        self.assertFalse(ipa.get("excelExport"))

    def test_run_safe_period_exports_never_returns_password(self):
        with mock.patch(
            "softdent_gui_export.export_report_by_id",
            return_value=Path(r"C:\SoftDentReportExports\register.xls"),
        ):
            with mock.patch(
                "softdent_signon.softdent_signon_status",
                return_value={"ok": True, "user": "Dr", "passwordConfigured": True},
            ):
                with mock.patch(
                    "softdent_signon.ensure_softdent_signed_on",
                    return_value={
                        "ok": True,
                        "signedOn": True,
                        "steps": ["already_signed_on_main_window"],
                    },
                ):
                    with mock.patch("softdent_gui_export.softdent_main_running", return_value=True):
                        result = run_safe_period_exports(
                            start=date(2026, 7, 1),
                            end=date(2026, 7, 12),
                            do_register=True,
                            do_collections=True,
                            ensure_signon=True,
                        )
        blob = str(result)
        self.assertTrue(result.get("ok"))
        self.assertIn("registerPath", result)
        self.assertNotIn("password", blob.lower().replace("passwordconfigured", ""))
        self.assertTrue((result.get("signOn") or {}).get("passwordConfigured"))

    def test_catalog_dry_run(self):
        result = run_catalog_exports(
            start=date(2026, 7, 1),
            end=date(2026, 7, 12),
            report_ids=["register", "aging"],
            ensure_signon=False,
            dry_run=True,
        )
        self.assertTrue(result.get("ok"))
        self.assertTrue(result["reports"]["register"].get("dryRun"))
        self.assertTrue(result["reports"]["aging"].get("dryRun"))


if __name__ == "__main__":
    unittest.main()
