"""Shared pytest defaults so app startup validation matches local test expectations."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("APP_AUTH_SESSION_SECRET", "unit-test-session-secret-not-for-production")

_FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def canonical_softdent_dashboard(monkeypatch):
    """Pin SoftDent dashboard rows to a committed deterministic fixture.

    The live import directory (``app/data/imports/softdent``) is mutable and can be
    rewritten by other tests in the same session (e.g. SoftDent import / route smoke
    checks). Tests that assert exact aggregate facts must read this canonical fixture
    instead of the shared on-disk snapshot so they stay deterministic regardless of
    test ordering. This does not introduce synthetic A/R, demo KPIs, or fake totals;
    it mirrors the canonical dashboard snapshot only.
    """

    import app.services as services

    rows = json.loads(
        (_FIXTURES_DIR / "softdent_dashboard_canonical.json").read_text(encoding="utf-8")
    )
    monkeypatch.setattr(services, "load_softdent_dashboard_rows", lambda: [dict(row) for row in rows])
    return rows
