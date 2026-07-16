"""Tests for board-safe financial recall export (P2.2)."""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from nr2_financial_recall import (
    balance_band,
    financial_recall_candidates,
    financial_recall_csv,
    format_financial_recall_hal_reply,
    months_since_visit,
)
from softdent_odbc_extract import ensure_sd_schema


def _seed_recall_db(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    ensure_sd_schema(conn)
    conn.execute(
        """
        INSERT OR REPLACE INTO sd_patients
        (patient_id, patient_name, first_visit_date, last_visit_date, practice_id, extracted_at)
        VALUES ('1001', 'Jane Doe', '2024-01-01', '2025-12-01', '', 't')
        """
    )
    conn.execute(
        """
        INSERT OR REPLACE INTO sd_claims
        (claim_id, patient_name, payer, service_date, claim_amount, claim_status, practice_id, extracted_at)
        VALUES ('CLM-1', 'Jane Doe', 'Delta', '2026-01-15', 420.0, 'Pending Review', '', 't')
        """
    )
    conn.commit()
    conn.close()


class Nr2FinancialRecallTests(unittest.TestCase):
    def test_balance_band_and_months(self) -> None:
        self.assertEqual(balance_band(50), "$0-99")
        self.assertEqual(balance_band(420), "$250-499")
        self.assertEqual(months_since_visit("2025-12-01", today=__import__("datetime").date(2026, 7, 16)), 7)

    def test_financial_recall_candidates_filters(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "analytics.sqlite3"
            _seed_recall_db(db_path)
            with patch("nr2_softdent_daily._connect", return_value=(sqlite3.connect(db_path), db_path)):
                with patch(
                    "nr2_softdent_daily._filter_unpaid_claim_rows",
                    side_effect=lambda rows, **_: rows,
                ):
                    result = financial_recall_candidates(
                        min_balance=100.0,
                        min_months_since_visit=6,
                        max_rows=10,
                    )
            self.assertTrue(result.get("ok"))
            self.assertEqual(result.get("count"), 1)
            row = (result.get("candidates") or [])[0]
            self.assertEqual(row.get("initials"), "JD—")
            self.assertEqual(row.get("balanceBand"), "$250-499")
            self.assertTrue(result.get("emptyNotZero"))

    def test_csv_and_hal_reply(self) -> None:
        with patch(
            "nr2_financial_recall.financial_recall_candidates",
            return_value={
                "ok": True,
                "count": 1,
                "config": {"minBalance": 100, "minMonthsSinceVisit": 6},
                "candidates": [
                    {
                        "initials": "JD—",
                        "nameHash": "ABCD",
                        "patientHash": "1A2B",
                        "phoneLast4": "—",
                        "balanceBand": "$250-499",
                        "lastVisit": "2025-12-01",
                        "monthsSinceVisit": 7,
                    }
                ],
            },
        ):
            csv_text = financial_recall_csv()
            self.assertIn("initials,nameHash,patientHash", csv_text)
            self.assertIn("JD—", csv_text)
            reply = format_financial_recall_hal_reply("financial recall export")
            self.assertIn("Financial recall export", reply)
            self.assertIn("JD—", reply)


if __name__ == "__main__":
    unittest.main()
