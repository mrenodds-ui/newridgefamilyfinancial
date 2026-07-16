"""Tests for period-close OPS trouble notifications (HAL hub lane)."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


def test_classify_period_close_trouble():
    from period_close_ops_notify import classify_period_close_trouble

    assert classify_period_close_trouble({"status": "stalled"}) == "stalled"
    assert classify_period_close_trouble({"status": "blocked"}) == "blocked"
    assert (
        classify_period_close_trouble({"status": "completed", "fallback": "attest_only"})
        == "attest_only"
    )
    assert (
        classify_period_close_trouble({"status": "completed", "forceClose": True, "beamHash": "abc"})
        == "force_close"
    )
    assert classify_period_close_trouble({"forceCloseStarted": True, "status": "started"}) == "force_close_start"
    assert classify_period_close_trouble({"status": "completed"}) is None
    assert classify_period_close_trouble({"status": "running"}) is None


def test_notify_period_close_trouble_hub_and_dedupe(tmp_path, monkeypatch):
    import period_close_ops_notify as n

    monkeypatch.setattr(n, "OPS_DIR", tmp_path)
    monkeypatch.setattr(n, "NOTIFY_STATE_PATH", tmp_path / "period_close_notify_state.json")

    calls = {"inbound": 0, "process": 0}

    def fake_submit(*_a, **_k):
        calls["inbound"] += 1
        return {"id": "x"}

    def fake_process():
        calls["process"] += 1
        return {"ok": True, "processed": 1}

    monkeypatch.setattr("hal_hub.submit_inbound", fake_submit)
    monkeypatch.setattr("hal_hub.process_pending", fake_process)

    result = {
        "status": "blocked",
        "completedAt": "2026-07-15T23:10:00+00:00",
        "beamHash": "abcd1234ffff",
        "actor": "scheduler",
    }
    first = n.notify_period_close_trouble(result, speak=False, store=None)
    assert first["ok"] is True
    assert first["kind"] == "blocked"
    assert first.get("channel") == "hal_hub"
    assert calls["inbound"] == 1
    assert "Force Close" in first["line"] or "lasers" in first["line"].lower()

    second = n.notify_period_close_trouble(result, speak=False, store=None)
    assert second.get("skipped") is True
    assert second.get("reason") == "deduped"
    assert calls["inbound"] == 1

    state = json.loads(Path(tmp_path / "period_close_notify_state.json").read_text(encoding="utf-8"))
    assert state.get("lastKind") == "blocked"


def test_notify_attest_only(tmp_path, monkeypatch):
    import period_close_ops_notify as n

    monkeypatch.setattr(n, "OPS_DIR", tmp_path)
    monkeypatch.setattr(n, "NOTIFY_STATE_PATH", tmp_path / "period_close_notify_state.json")
    monkeypatch.setattr("hal_hub.submit_inbound", lambda *a, **k: {"id": "y"})
    monkeypatch.setattr("hal_hub.process_pending", lambda: {"ok": True, "processed": 1})

    out = n.notify_period_close_trouble(
        {
            "status": "completed",
            "fallback": "attest_only",
            "completedAt": "2026-07-15T23:11:00+00:00",
            "beamHash": "beefcafe0001",
            "actor": "scheduler",
        },
        speak=False,
    )
    assert out["kind"] == "attest_only"
    assert "attest-only" in out["line"].lower() or "attest" in out["line"].lower()


def test_notify_force_close_started(tmp_path, monkeypatch):
    import period_close_ops_notify as n

    monkeypatch.setattr(n, "OPS_DIR", tmp_path)
    monkeypatch.setattr(n, "NOTIFY_STATE_PATH", tmp_path / "period_close_notify_state.json")
    monkeypatch.setattr("hal_hub.submit_inbound", lambda *a, **k: {"id": "z"})
    monkeypatch.setattr("hal_hub.process_pending", lambda: {"ok": True, "processed": 1})

    out = n.notify_force_close_started(actor="optical-om", laser_override=True, speak=False)
    assert out["kind"] == "force_close_start"
    assert "Force Close" in out["line"]
    assert "Laser override" in out["line"]
    assert "optical-om" in out["line"]


def test_maybe_notify_laser_stall_waits_then_fires(tmp_path, monkeypatch):
    import period_close_ops_notify as n

    monkeypatch.setattr(n, "OPS_DIR", tmp_path)
    monkeypatch.setattr(n, "NOTIFY_STATE_PATH", tmp_path / "period_close_notify_state.json")
    monkeypatch.setattr("hal_hub.submit_inbound", lambda *a, **k: {"id": "l"})
    monkeypatch.setattr("hal_hub.process_pending", lambda: {"ok": True, "processed": 1})

    ready = {"alignmentLasers": {"red": True}, "blocking": [{"datasetKey": "softdent.ar"}]}
    first = n.maybe_notify_laser_stall(ready, stall_seconds=300, speak=False)
    assert first.get("skipped") is True
    assert first.get("reason") == "laser_red_armed"

    state = json.loads((tmp_path / "period_close_notify_state.json").read_text(encoding="utf-8"))
    old = (datetime.now(timezone.utc) - timedelta(seconds=400)).replace(microsecond=0).isoformat()
    state["laserRedSince"] = old
    (tmp_path / "period_close_notify_state.json").write_text(json.dumps(state), encoding="utf-8")

    second = n.maybe_notify_laser_stall(ready, stall_seconds=300, speak=False)
    assert second.get("skipped") is not True
    assert second.get("kind") == "laser_stall"
    assert "Force Close" in second["line"]

    clear = n.maybe_notify_laser_stall(
        {"alignmentLasers": {"red": False}, "blocking": []},
        stall_seconds=300,
        speak=False,
    )
    assert clear.get("reason") == "lasers_clear"
