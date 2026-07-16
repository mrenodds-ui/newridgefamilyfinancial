"""Tests for nr2_softdent_daily (hal-10071)."""

from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from softdent_odbc_extract import ensure_sd_schema
from nr2_softdent_daily import (
    claim_review,
    claims_outstanding,
    collections_daily,
    new_patients_mtd,
    provider_production,
)


def _seed_db(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    ensure_sd_schema(conn)
    conn.execute(
        "INSERT OR REPLACE INTO sd_payments (practice_id, patient_id, payment_date, amount, payer, method, extracted_at) VALUES ('', '1001', '2026-06-15', 85.0, '', 'Visa', 't')"
    )
    conn.execute(
        "INSERT OR REPLACE INTO sd_patients (patient_id, patient_name, first_visit_date, last_visit_date, practice_id, extracted_at) VALUES ('1001', 'Jane', '2026-06-01', '2026-06-15', '', 't')"
    )
    conn.execute(
        "INSERT OR REPLACE INTO sd_claims (claim_id, patient_name, payer, service_date, claim_amount, claim_status, practice_id, extracted_at) VALUES ('CLM-1', 'Jane', 'Delta', '2026-06-10', 420.0, 'Ready', '', 't')"
    )
    conn.execute(
        """
        INSERT OR REPLACE INTO sd_procedures
        (practice_id, patient_id, proc_date, ada_code, tooth, surface, provider_code, description, production, extracted_at)
        VALUES ('', '1001', '2026-06-15', '1110', '', '', 'DR1', 'Prophy', 120.0, 't')
        """
    )
    conn.commit()
    conn.close()


class Nr2SoftdentDailyTests(unittest.TestCase):
    def test_collections_daily(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "analytics.sqlite3"
            _seed_db(db_path)
            with patch("nr2_softdent_daily.resolve_sd_sqlite_db", return_value=db_path):
                result = collections_daily()
            self.assertTrue(result["hasData"])
            self.assertEqual(result["values"][-1], 85.0)

    def test_new_patients_mtd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "analytics.sqlite3"
            _seed_db(db_path)
            with patch("nr2_softdent_daily.resolve_sd_sqlite_db", return_value=db_path):
                result = new_patients_mtd(period="2026-06")
            self.assertTrue(result["hasData"])
            self.assertEqual(result["count"], 1)

    def test_claims_outstanding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "analytics.sqlite3"
            _seed_db(db_path)
            with patch("nr2_softdent_daily.resolve_sd_sqlite_db", return_value=db_path):
                result = claims_outstanding()
            self.assertTrue(result["hasData"])
            self.assertEqual(result["claims"][0]["claimId"], "CLM-1")
            self.assertEqual(result["claims"][0]["patientId"], "1001")
            self.assertEqual(result["sampleWithPatientId"], 1)

    def test_claims_outstanding_name_join_last_first(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "analytics.sqlite3"
            _seed_db(db_path)
            conn = sqlite3.connect(db_path)
            conn.execute(
                "INSERT OR REPLACE INTO sd_patients "
                "(patient_id, patient_name, first_visit_date, last_visit_date, practice_id, extracted_at) "
                "VALUES ('2002', 'Jane Doe', '2026-06-01', '2026-06-15', '', 't')"
            )
            conn.execute(
                "INSERT OR REPLACE INTO sd_claims "
                "(claim_id, patient_name, payer, service_date, claim_amount, claim_status, practice_id, extracted_at) "
                "VALUES ('CLM-2', 'Doe, Jane', 'Delta', '2026-06-11', 310.0, 'Ready', '', 't')"
            )
            conn.commit()
            conn.close()
            with patch("nr2_softdent_daily.resolve_sd_sqlite_db", return_value=db_path):
                result = claims_outstanding(limit=10)
            by_id = {c["claimId"]: c for c in result["claims"]}
            self.assertEqual(by_id["CLM-2"]["patientId"], "2002")
            self.assertGreaterEqual(result["sampleWithPatientId"], 2)

    def test_claim_review_narrative_and_checklist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "analytics.sqlite3"
            _seed_db(db_path)
            with patch("nr2_softdent_daily.resolve_sd_sqlite_db", return_value=db_path):
                with patch(
                    "nr2_softdent_daily._procedure_lines_for_claim",
                    return_value=[
                        {
                            "code": "1110",
                            "kind": "procedure",
                            "production": 120.0,
                            "providerId": "1",
                            "patientId": "1001",
                        }
                    ],
                ):
                    result = claim_review(claim_id="CLM-1")
            self.assertTrue(result.get("ok"))
            self.assertTrue(result.get("hasData"))
            self.assertIn("narrative", result)
            self.assertTrue(str((result.get("narrative") or {}).get("text") or ""))
            self.assertIn("checklist", result)
            items = ((result.get("checklist") or {}).get("items")) or []
            self.assertTrue(any(i.get("id") == "unpaid" and i.get("ok") for i in items))
            self.assertEqual(len(result.get("procedures") or []), 1)

    def test_claim_review_rejects_paid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "analytics.sqlite3"
            _seed_db(db_path)
            conn = sqlite3.connect(db_path)
            conn.execute(
                "UPDATE sd_claims SET claim_status='Paid' WHERE claim_id='CLM-1'"
            )
            conn.commit()
            conn.close()
            with patch("nr2_softdent_daily.resolve_sd_sqlite_db", return_value=db_path):
                result = claim_review(claim_id="CLM-1")
            self.assertFalse(result.get("ok"))
            self.assertEqual(result.get("error"), "claim_not_unpaid")

    def test_provider_production(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "analytics.sqlite3"
            _seed_db(db_path)
            with patch("nr2_softdent_daily.resolve_sd_sqlite_db", return_value=db_path):
                result = provider_production()
            self.assertTrue(result["hasData"])
            self.assertEqual(result["providers"][0]["providerCode"], "DR1")


    def test_collections_daily_daysheet_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "analytics.sqlite3"
            conn = sqlite3.connect(db_path)
            conn.execute(
                """
                CREATE TABLE daysheet_totals (
                    year_month TEXT, gross_production REAL, net_production REAL,
                    collections REAL, new_patients INTEGER
                )
                """
            )
            conn.execute(
                "INSERT INTO daysheet_totals (year_month, collections) VALUES ('2026-06', 500.0)"
            )
            conn.commit()
            conn.close()
            with patch("nr2_softdent_daily.resolve_sd_sqlite_db", return_value=db_path):
                result = collections_daily()
            self.assertTrue(result["hasData"])
            self.assertEqual(result["source"], "daysheet_totals")


if __name__ == "__main__":
    unittest.main()
