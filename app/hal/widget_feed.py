from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Mapping


_WIDGET_FEED_LOCK = Lock()
_LATEST_WIDGET_FEED: dict[str, Any] | None = None


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _require_mapping(value: object, *, field_name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError(f"Widget update payload field {field_name} must be a JSON object")
    return dict(value)


def record_widget_feed(payload: Mapping[str, Any]) -> dict[str, Any]:
    manager = str(payload.get("manager") or "").strip()
    if not manager:
        raise ValueError("Widget update payload must include manager")

    widgets = _require_mapping(payload.get("widgets"), field_name="widgets")
    if not widgets:
        raise ValueError("Widget update payload must include at least one widget")

    normalized = {
        "manager": manager,
        "run_id": str(payload.get("run_id") or "").strip() or None,
        "generated_at": str(payload.get("generated_at") or "").strip() or _utc_now_iso(),
        "received_at": _utc_now_iso(),
        "widgets": deepcopy(widgets),
        "sources": deepcopy(_require_mapping(payload.get("sources"), field_name="sources")),
        "jobs": deepcopy(_require_mapping(payload.get("jobs"), field_name="jobs")),
    }

    with _WIDGET_FEED_LOCK:
        global _LATEST_WIDGET_FEED
        _LATEST_WIDGET_FEED = normalized

    return deepcopy(normalized)


def get_widget_feed() -> dict[str, Any] | None:
    with _WIDGET_FEED_LOCK:
        if _LATEST_WIDGET_FEED is None:
            return None
        return deepcopy(_LATEST_WIDGET_FEED)


def clear_widget_feed() -> None:
    with _WIDGET_FEED_LOCK:
        global _LATEST_WIDGET_FEED
        _LATEST_WIDGET_FEED = None


__all__ = ["clear_widget_feed", "get_widget_feed", "record_widget_feed"]