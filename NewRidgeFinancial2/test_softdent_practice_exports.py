"""Tests for SoftDent practice widget exports and collections diagnostics."""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from softdent_dashboard_period_sync import diagnose_collections_gap
from softdent_practice_exports import _aggregate_new_patients, _aggregate_treatment_plans, sync_practice_exports


class SoftdentPracticeExportsTests(unittest.TestCase):
    @patch("softdent_dashboard_period_sync._bridge_rows_by_period", return_value={})
    def test_diagnose_collections_gap_no_issues_without_data(self, _bridge) -> None:
        diagnostic = diagnose_collections_gap(None, ["2099-01"])
        self.assertEqual(diagnostic["issues"], [])

    def test_practice_exports_from_analytics_tables(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "analytics.sqlite3"
            dest = Path(tmp) / "softdent"
            dest.mkdir()
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE new_patient_counts (year_month TEXT, new_patient_count INTEGER)")
            conn.execute("INSERT INTO new_patient_counts VALUES ('2026-06', 12)")
            conn.execute(
                """
                CREATE TABLE treatment_plan_summary (
                    year_month TEXT,
                    presented REAL,
                    accepted REAL,
                    amount REAL
                )
                """
            )
            conn.execute("INSERT INTO treatment_plan_summary VALUES ('2026-06', 20, 15, 45000)")
            conn.commit()
            conn.close()

            conn = sqlite3.connect(db_path)
            try:
                np_rows = _aggregate_new_patients(conn, ["2026-06"])
                self.assertEqual(np_rows[0]["Count"], 12)
                tp_rows = _aggregate_treatment_plans(conn, ["2026-06"])
                self.assertEqual(tp_rows[0]["Presented"], 20.0)
            finally:
                conn.close()

            result = sync_practice_exports(db_path=db_path, destination=dest)
            self.assertTrue(result["ok"])
            self.assertIn("softdent_new_patients.csv", result["written"])
            self.assertIn("treatment_plan_summary.csv", result["written"])
            self.assertIn("case_acceptance.csv", result["written"])


if __name__ == "__main__":
    unittest.main()
