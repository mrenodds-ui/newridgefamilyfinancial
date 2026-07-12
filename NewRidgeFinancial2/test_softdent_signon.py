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


if __name__ == "__main__":
    unittest.main()
