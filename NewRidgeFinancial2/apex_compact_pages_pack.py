"""NR2 Apex compact professional pages — Moonshot plan Phases 2–4 helpers.

CONSULT: MOONSHOT_COMPACT_PAGES_DETAILED_PLAN_2026-07-11.md
VALIDATION: MOONSHOT_COMPACT_PAGES_PLAN_VALIDATION_2026-07-11.md

Claims mode (operator proceed): pipeline summary strip + kanban subpage.
HAL mode: sole `l` chat instrument.
"""

from __future__ import annotations

from typing import Any


def collapse_empty_large(widget: dict[str, Any]) -> dict[str, Any]:
    """Empty l/xl/full → strip. Skip loading/skeleton (Moonshot R3)."""
    if not isinstance(widget, dict):
        return widget
    if widget.get("isSkeleton") is True:
        return widget
    status = str(widget.get("status") or "").lower()
    if status in {"loading", "skeleton", "warming"}:
        return widget
    if status != "empty":
        return widget
    size = str(widget.get("size") or "")
    if size not in {"l", "xl", "full", "large"}:
        return widget
    if widget.get("collapseWhenEmpty") is False:
        return widget
    out = dict(widget)
    out["collapseWhenEmpty"] = True
    out["size"] = "strip"
    out["compact"] = True
    return out


def apply_collapse_empty_all(widgets: list[Any]) -> list[Any]:
    out: list[Any] = []
    for w in widgets:
        if isinstance(w, dict):
            out.append(collapse_empty_large(w))
        else:
            out.append(w)
    return out


def normalize_first_viewport(widgets: list[Any], *, page: str = "") -> list[Any]:
    """Cap first-viewport sizes: no xl above fold; at most one l in first six.

    HAL chat may be the sole `l` on the HAL page (Moonshot R1 exemption).
    """
    if not isinstance(widgets, list):
        return widgets
    page_key = str(page or "").strip().lower()
    large_seen = 0
    out: list[Any] = []
    for i, w in enumerate(widgets):
        if not isinstance(w, dict):
            out.append(w)
            continue
        item = dict(w)
        size = str(item.get("size") or "").lower()
        wtype = str(item.get("type") or "")
        wid = str(item.get("id") or "")

        # HAL exemption: keep chat as sole l
        if page_key == "hal" and wtype == "hal-chat":
            item["size"] = "l"
            out.append(item)
            large_seen += 1
            continue

        if i < 6:
            if size == "xl":
                item["size"] = "l" if large_seen == 0 else "m"
                size = item["size"]
            if size in {"l", "large", "full"}:
                # Tall full shelves → strip when early; keep one primary l/chart
                if size == "full" and wtype not in {"claims-workbench", "claims-kanban"}:
                    # Prefer strip for status/import shelves
                    if wtype in {
                        "status",
                        "import-freshness",
                        "import-health",
                        "financial-command-strip",
                        "claims-executive-strip",
                        "executive-strip",
                    } or wid.endswith("-strip"):
                        item["size"] = "strip"
                    elif large_seen >= 1:
                        item["size"] = "m"
                    else:
                        item["size"] = "l"
                        large_seen += 1
                elif size in {"l", "large"}:
                    if large_seen >= 1:
                        item["size"] = "m"
                    else:
                        large_seen += 1
        out.append(item)
    return out


def claims_pipeline_summary_widget(counts: dict[str, Any] | None, *, available: bool) -> dict[str, Any]:
    """Phase 3/4 Claims mode: summary strip + Open Kanban (not clipped board)."""
    c = counts if isinstance(counts, dict) else {}
    try:
        from apex_claims_narratives_pack import KANBAN_COLUMNS, KANBAN_LABELS

        keys = list(KANBAN_COLUMNS)
        labels = dict(KANBAN_LABELS)
    except Exception:
        keys = ["pending", "submitted", "denied", "paid"]
        labels = {k: k.title() for k in keys}

    pills: list[dict[str, Any]] = []
    for key in keys[:4]:
        pills.append(
            {
                "id": key,
                "label": str(labels.get(key) or key).title(),
                "value": int(c.get(key) or 0),
                "empty": not available,
            }
        )
    has = available and any(int(p.get("value") or 0) > 0 for p in pills)
    return {
        "id": "claims-pipeline-summary",
        "type": "claims-executive-strip",
        "label": "Claims Pipeline",
        "size": "s",
        "compact": True,
        "pills": pills,
        "status": "ok" if has else "empty",
        "emptyMessage": "Import SoftDent claims — then open Kanban for the full board",
        "hint": "Compact pipeline counts · full workbench on #claims/kanban (Moonshot compact plan).",
        "navHash": "claims/kanban",
        "halAction": "open_claims_kanban",
        "halActionLabel": "Open Kanban",
        "aliasIds": ["claims-kanban-board"],
    }


def open_detail_strip(*, page: str, sub: str, label: str, message: str) -> dict[str, Any]:
    return {
        "id": f"{page}-{sub}-open",
        "type": "status",
        "label": label,
        "size": "strip",
        "compact": True,
        "status": "ok",
        "message": message,
        "hint": f"Open #{page}/{sub}",
        "navHash": f"{page}/{sub}",
    }
