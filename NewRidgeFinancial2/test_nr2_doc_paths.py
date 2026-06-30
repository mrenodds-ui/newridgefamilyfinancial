"""Guard against stale import-cache paths in active NR2 documentation."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NR2_ROOT = REPO_ROOT / "NewRidgeFinancial2"

STALE_PATH = re.compile(r"app/data/imports", re.IGNORECASE)

# Active NR2 docs that must describe document-inbox paths only.
DOC_FILES = [
    REPO_ROOT / "README.md",
    NR2_ROOT / "README.md",
    NR2_ROOT / "import-automation" / "README.md",
    REPO_ROOT / "docs" / "schedule_softdent_bridge_sync.md",
]

# Lines that may mention the legacy path when explaining migration.
ALLOWED_LINE_PATTERNS = (
    re.compile(r"legacy\s+`?app/data/imports", re.IGNORECASE),
    re.compile(r"migrat", re.IGNORECASE),
    re.compile(r"retired", re.IGNORECASE),
    re.compile(r"first sync", re.IGNORECASE),
)


def _line_allowed(line: str) -> bool:
    return any(pattern.search(line) for pattern in ALLOWED_LINE_PATTERNS)


class Nr2DocPathTests(unittest.TestCase):
    def test_active_docs_do_not_reference_legacy_import_cache(self) -> None:
        violations: list[str] = []
        for path in DOC_FILES:
            self.assertTrue(path.is_file(), f"missing doc file: {path}")
            for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if STALE_PATH.search(line) and not _line_allowed(line):
                    violations.append(f"{path.relative_to(REPO_ROOT)}:{line_no}: {line.strip()}")
        self.assertEqual(violations, [], "stale app/data/imports references:\n" + "\n".join(violations))

    def test_import_manifest_uses_document_inbox_cache(self) -> None:
        manifest = (NR2_ROOT / "import-manifest.json").read_text(encoding="utf-8")
        self.assertIn("app_data/nr2/document_inbox/softdent", manifest)
        self.assertIn("app_data/nr2/document_inbox/quickbooks", manifest)
        self.assertNotIn("app/data/imports", manifest)


if __name__ == "__main__":
    unittest.main()
