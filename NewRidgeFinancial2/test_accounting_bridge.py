"""Tests for Python accounting bridge and SQLite posting queue."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from accounting_bridge import (
    draft_journal_payload,
    enqueue_journal_posting,
    export_approved_posting_queue_csv,
    list_posting_queue,
    review_posting_queue_entry,
)
from accounting_tools import get_chart_of_accounts, is_period_open


class AccountingBridgeTests(unittest.TestCase):
    def test_chart_of_accounts_matches_legacy_codes(self) -> None:
        coa = get_chart_of_accounts()
        self.assertEqual(coa["1310"], "Prepaid Insurance")
        self.assertEqual(coa["4000"], "Patient Service Revenue")

    def test_draft_prepaid_insurance_balances(self) -> None:
        draft = draft_journal_payload(description="Prepaid insurance payment", period="2025-05", amount=1200)
        self.assertEqual(draft["transactionType"], "prepaid_insurance")
        self.assertTrue(draft["validation"]["balanced"])
        self.assertEqual(draft["validation"]["debitTotal"], 1200)
        self.assertEqual(draft["lines"][0]["accountCode"], "1310")

    def test_closed_period_flags_validation_issue(self) -> None:
        draft = draft_journal_payload(description="Depreciation", period="2025-01", amount=500)
        self.assertFalse(is_period_open("2025-01"))
        self.assertIn("Accounting period is closed.", draft["validation"]["issues"])

    def test_posting_queue_enqueue_and_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "nr2.sqlite3"
            result = enqueue_journal_posting(
                db_path,
                description="Prepaid insurance payment",
                period="2026-06",
                amount=980.5,
                actor="unittest",
            )
            self.assertEqual(result["draftStatus"], "enqueued")
            queue_id = result["queueEntry"]["queueId"]
            listed = list_posting_queue(db_path, limit=10)
            self.assertEqual(listed["metrics"]["pendingReview"], 1)
            self.assertEqual(listed["items"][0]["queueId"], queue_id)
            reviewed = review_posting_queue_entry(
                db_path,
                queue_id=queue_id,
                action="approved",
                reviewer_actor="Controller",
                review_note="Ready for manual QB entry",
            )
            self.assertEqual(reviewed["status"], "approved")
            self.assertEqual(reviewed["reviewerActor"], "Controller")
            exported = export_approved_posting_queue_csv(db_path)
            self.assertEqual(exported["entryCount"], 1)
            self.assertIn("1310", exported["csv"])
            self.assertIn("Prepaid Insurance", exported["csv"])

    def test_posting_queue_rejects_closed_period(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "nr2.sqlite3"
            with self.assertRaises(ValueError):
                enqueue_journal_posting(
                    db_path,
                    description="Depreciation",
                    period="2025-01",
                    amount=500,
                )


if __name__ == "__main__":
    unittest.main()
