"""SoftDent GUI export helpers — unit tests (no live SoftDent required)."""

from __future__ import annotations

import unittest
from datetime import date
from unittest import mock

from softdent_gui_export import run_safe_period_exports


class SoftDentGuiExportTests(unittest.TestCase):
    def test_run_safe_period_exports_never_returns_password(self):
        with mock.patch("softdent_gui_export.export_register_for_period", return_value=__import__("pathlib").Path(r"C:\SoftDentReportExports\register.xls")):
            with mock.patch("softdent_gui_export.export_collections_for_period", side_effect=RuntimeError("skip")):
                with mock.patch(
                    "softdent_signon.softdent_signon_status",
                    return_value={"ok": True, "user": "Dr", "passwordConfigured": True},
                ):
                    with mock.patch(
                        "softdent_signon.ensure_softdent_signed_on",
                        return_value={"ok": True, "signedOn": True, "steps": ["already_signed_on_main_window"]},
                    ):
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
        self.assertNotIn("1966", blob)
        self.assertNotIn("password", blob.lower().replace("passwordconfigured", ""))
        self.assertTrue((result.get("signOn") or {}).get("passwordConfigured"))


if __name__ == "__main__":
    unittest.main()
