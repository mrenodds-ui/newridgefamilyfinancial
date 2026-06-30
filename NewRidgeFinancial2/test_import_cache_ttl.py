"""Tests for import cache retention and dataset checksum fingerprints."""

from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

import import_cache_ttl as ttl


class ImportCacheTtlTests(unittest.TestCase):
    def test_sha256_file_stable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.csv"
            path.write_text("period,production\n2026-06,100\n", encoding="utf-8")
            first = ttl.sha256_file(path)
            second = ttl.sha256_file(path)
            self.assertIsNotNone(first)
            self.assertEqual(first, second)

    def test_purge_expired_ocr_files_removes_old_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp)
            old_file = archive / "old-invoice.pdf"
            new_file = archive / "new-invoice.pdf"
            old_file.write_bytes(b"old")
            new_file.write_bytes(b"new")
            old_ts = (datetime.now(timezone.utc) - timedelta(days=30)).timestamp()
            new_ts = datetime.now(timezone.utc).timestamp()
            import os

            os.utime(old_file, (old_ts, old_ts))
            os.utime(new_file, (new_ts, new_ts))

            with mock.patch.object(ttl, "_ocr_archive_dirs", return_value=[archive]):
                removed = ttl.purge_expired_ocr_files()
            self.assertIn("old-invoice.pdf", removed)
            self.assertFalse(old_file.exists())
            self.assertTrue(new_file.exists())

    def test_collect_dataset_checksums_hashes_newest_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            softdent = Path(tmp) / "softdent"
            quickbooks = Path(tmp) / "quickbooks"
            softdent.mkdir()
            quickbooks.mkdir()
            dashboard = softdent / "softdent_dashboard_data.json"
            dashboard.write_text('[{"period":"2026-06","production":100}]', encoding="utf-8")
            revenue = quickbooks / "quickbooks_revenue.csv"
            revenue.write_text("Period,TotalIncome\n2026-06,5000\n", encoding="utf-8")

            checksums = ttl.collect_dataset_checksums(softdent, quickbooks)
            self.assertIn("softdent.dashboard", checksums)
            self.assertIn("quickbooks.revenue", checksums)
            self.assertEqual(checksums["softdent.dashboard"]["sourceFile"], dashboard.name)
            self.assertEqual(checksums["softdent.dashboard"]["sha256"], ttl.sha256_file(dashboard))

    def test_write_manifest_persists_dataset_checksums(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = Path(tmp) / "import_cache_manifest.json"
            with mock.patch.object(ttl, "manifest_path", return_value=manifest_path):
                ttl.write_manifest(
                    synced_at=datetime.now(timezone.utc).isoformat(),
                    periods={"softdent": ["2026-06"], "quickbooks": ["2026-06"]},
                    dataset_checksums={
                        "softdent.dashboard": {
                            "sourceFile": "softdent_dashboard_data.json",
                            "sha256": "abc123",
                        }
                    },
                )
                loaded = ttl.load_manifest()
            self.assertIsNotNone(loaded)
            assert loaded is not None
            self.assertEqual(loaded["datasetChecksums"]["softdent.dashboard"]["sha256"], "abc123")


if __name__ == "__main__":
    unittest.main()
