"""NR2-12150 — paid vs outstanding suppress cascade (empty ≠ $0)."""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from nr2_claims_paid_suppress import (
    claim_is_still_outstanding,
    claim_is_unpaid_per_aging,
    claim_is_unpaid_per_era,
    claim_is_unpaid_per_staff,
    mark_staff_verified_paid,
    parse_claims_aging_export,
)


class ClaimsPaidSuppressTests(unittest.TestCase):
    def test_staff_hide_suppresses_claim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            hide = Path(tmp) / "hide.jsonl"
            with patch("nr2_claims_paid_suppress.staff_verified_paid_path", return_value=hide):
                self.assertTrue(claim_is_unpaid_per_staff(claim_id="TXN-1"))
                out = mark_staff_verified_paid(claim_id="TXN-1", actor="Tester")
                self.assertTrue(out.get("ok"))
                self.assertFalse(claim_is_unpaid_per_staff(claim_id="TXN-1"))
                self.assertTrue(claim_is_unpaid_per_staff(claim_id="TXN-2"))

    def test_era_requires_explicit_paid_gt_zero(self) -> None:
        era = {
            "active": True,
            "claimIds": {"CLM-9"},
            "tuples": {"smith jane|2026-07-01|100.00"},
        }
        self.assertFalse(
            claim_is_unpaid_per_era(claim_id="CLM-9", era_index=era)
        )
        self.assertFalse(
            claim_is_unpaid_per_era(
                patient_name="Smith, Jane",
                service_date="2026-07-01",
                amount=100,
                era_index=era,
            )
        )
        # Inactive / empty ERA never invents paid
        self.assertTrue(
            claim_is_unpaid_per_era(claim_id="CLM-9", era_index={"active": False})
        )

    def test_aging_absent_when_active_means_paid(self) -> None:
        aging = {
            "active": True,
            "claimIds": {"KEEP-1"},
            "tuples": {"doe john|2026-06-01|50.00"},
        }
        self.assertTrue(
            claim_is_unpaid_per_aging(claim_id="KEEP-1", aging_index=aging)
        )
        self.assertFalse(
            claim_is_unpaid_per_aging(claim_id="GONE-2", aging_index=aging)
        )
        # Missing aging must not invent paid
        self.assertTrue(
            claim_is_unpaid_per_aging(
                claim_id="GONE-2", aging_index={"active": False}
            )
        )

    def test_parse_claims_aging_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "claims_aging_20260716.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                w = csv.writer(handle)
                w.writerow(["Patient", "Claim #", "Service Date", "Amount", "Payer"])
                w.writerow(["Bernett, Jeffery", "C-100", "05/28/2026", "$137.00", "DELTA"])
                w.writerow(["Total", "", "", "$137.00", ""])
            parsed = parse_claims_aging_export(path)
            self.assertTrue(parsed.get("ok"))
            self.assertTrue(parsed.get("active"))
            self.assertIn("C-100", parsed.get("claimIds") or [])

    def test_cascade_order_txn_then_staff(self) -> None:
        transactions = [
            {
                "patientId": "1080404",
                "patientName": "Bernett, Jeffery Adam",
                "code": "1110",
                "description": "Prophy",
                "production": 137.0,
                "reportDate": "2026-05-28",
            },
            {
                "patientId": "1080404",
                "patientName": "Bernett, Jeffery Adam",
                "code": "2",
                "description": "Insurance Check Payment",
                "production": None,
                "reportDate": "2026-05-28",
            },
        ]
        keep, reason = claim_is_still_outstanding(
            claim_id="DS-20260528-1080404-1110-3",
            patient_id="1080404",
            patient_name="Bernett, Jeffery Adam",
            service_date="2026-05-28",
            amount=137,
            claim_status="Pending Review",
            transactions=transactions,
            era_index={"active": False},
            aging_index={"active": False},
            staff_ids=set(),
        )
        self.assertFalse(keep)
        self.assertEqual(reason, "txn")

        keep2, reason2 = claim_is_still_outstanding(
            claim_id="TXN-OPEN-1",
            patient_id="999",
            patient_name="Open, Still",
            service_date="2026-07-01",
            amount=200,
            claim_status="Pending Review",
            transactions=[],
            era_index={"active": False},
            aging_index={"active": False},
            staff_ids={"TXN-OPEN-1"},
        )
        self.assertFalse(keep2)
        self.assertEqual(reason2, "staff")


if __name__ == "__main__":
    unittest.main()
