"""SoftDent Sign On credential resolver (no secret values in assertions)."""

from __future__ import annotations

import os
import unittest
from unittest import mock

from softdent_signon import (
    ENV_PASSWORD,
    ENV_USER,
    resolve_softdent_signon_credentials,
    softdent_signon_status,
)


class SoftDentSignOnTests(unittest.TestCase):
    def test_status_reports_configured_without_leaking_password(self):
        with mock.patch.dict(
            os.environ,
            {ENV_USER: "Dr", ENV_PASSWORD: "test-secret-not-real"},
            clear=False,
        ):
            status = softdent_signon_status()
            creds = resolve_softdent_signon_credentials()
        self.assertTrue(status.get("ok"))
        self.assertEqual(status.get("user"), "Dr")
        self.assertTrue(status.get("passwordConfigured"))
        self.assertNotIn("password", status)
        self.assertNotIn("test-secret-not-real", str(status))
        self.assertTrue(creds.get("ok"))

    def test_missing_password_is_not_ok(self):
        with mock.patch.dict(os.environ, {ENV_USER: "Dr", ENV_PASSWORD: ""}, clear=False):
            os.environ.pop(ENV_PASSWORD, None)
            os.environ.pop("SOFTDENT_GUI_PASSWORD", None)
            with mock.patch("softdent_signon.load_softdent_signon_env_files", return_value=[]):
                status = softdent_signon_status()
        self.assertFalse(status.get("ok"))
        self.assertFalse(status.get("passwordConfigured"))

    def test_hal_reply_mentions_env_keys_not_password(self):
        with mock.patch.dict(
            os.environ,
            {ENV_USER: "Dr", ENV_PASSWORD: "test-secret-not-real"},
            clear=False,
        ):
            from softdent_signon import format_softdent_signon_hal_reply

            text = format_softdent_signon_hal_reply()
        self.assertIn("SOFTDENT_SIGNON_USER", text)
        self.assertIn("SOFTDENT_SIGNON_PASSWORD", text)
        self.assertIn("environment", text.lower())
        self.assertNotIn("test-secret-not-real", text)

    def test_local_policy_signon(self):
        from nr2_hal_gateway import try_local_policy_reply

        with mock.patch.dict(
            os.environ,
            {ENV_USER: "Dr", ENV_PASSWORD: "test-secret-not-real"},
            clear=False,
        ):
            hit = try_local_policy_reply("Where is the SoftDent Sign On password?")
        self.assertIsNotNone(hit)
        self.assertEqual(hit.get("intent"), "policy:softdent-signon-env")
        self.assertIn("SOFTDENT_SIGNON_PASSWORD", hit.get("text") or "")
        self.assertNotIn("test-secret-not-real", hit.get("text") or "")

    def test_hal_reply_includes_ui_only_data_doctrine(self):
        from softdent_signon import SOFTDENT_DATA_ACCESS_DOCTRINE, format_softdent_signon_hal_reply

        text = format_softdent_signon_hal_reply(
            {
                "user": "Dr",
                "passwordConfigured": True,
            }
        )
        self.assertIn("cannot be reached by the database", text)
        self.assertIn("Sign On", text)
        self.assertIn("UI", text)
        self.assertIn(SOFTDENT_DATA_ACCESS_DOCTRINE[:40], text)

    def test_local_policy_ui_only_data_path(self):
        from nr2_hal_gateway import try_local_policy_reply
        from softdent_signon import SOFTDENT_DATA_ACCESS_DOCTRINE

        with mock.patch.dict(
            os.environ,
            {ENV_USER: "Dr", ENV_PASSWORD: "test-secret-not-real"},
            clear=False,
        ):
            hit = try_local_policy_reply(
                "How do I get SoftDent data that cannot be reached by the database?"
            )
        self.assertIsNotNone(hit)
        self.assertEqual(hit.get("intent"), "policy:softdent-signon-env")
        self.assertIn("cannot be reached by the database", hit.get("text") or "")
        self.assertIn("UI", hit.get("text") or "")
        self.assertNotIn("test-secret-not-real", hit.get("text") or "")
        self.assertIn("Sign On", SOFTDENT_DATA_ACCESS_DOCTRINE)


if __name__ == "__main__":
    unittest.main()
