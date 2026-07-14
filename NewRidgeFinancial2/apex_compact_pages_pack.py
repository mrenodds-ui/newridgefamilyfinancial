"""NR2 Apex compact + zero-scroll + KPI density — Moonshot helpers.

CONSULTS:
- MOONSHOT_COMPACT_PAGES_DETAILED_PLAN_2026-07-11.md
- MOONSHOT_ZERO_SCROLL_WIDGETS_CONSULT_2026-07-11.md (hal-10561)
- MOONSHOT_KPI_DENSITY_FIX_CONSULT_2026-07-12.md (hal-10562)

Claims: pipeline summary on main + kanban subpage (zero-scroll: no board on Overview).
HAL: no sole-l exemption — chat is a capped tile; full audit via Full Log strip.
KPI: ≤4 visible KPI tiles above fold; empty KPIs omit (never $0 pad).
"""

from __future__ import annotations

from typing import Any

# Moonshot Fibonacci zero-scroll height tiers (px)
MAX_PRIMARY_PX = 320
MAX_SECONDARY_PX = 240
MAX_MICRO_PX = 80
TABLE_ROW_CAP = 5
TABLE_ROW_CAP_HARD = 7
# Moonshot KPI density (hal-10562)
KPI_BUDGET_ABOVE_FOLD = 4
# First-viewport keep sets (hal-10612) — overflow → #{page}/ops

PAGE_FIRST_VIEW_KEEP: dict[str, frozenset[str]] = {
    "financial": frozenset(
        {
            "financial-command-strip",
            "financial-dual-trend",
            "provider-hbar",
            "collections-gauge",
            "bridge-errors",
            "ar-aging-chart",
        }
    ),
    "claims": frozenset(
        {
            "claims-executive-strip",
            "claims-aging-exposure",
            "claims-pipeline-summary",
            "claims-top-critical",
            "claims-open-kanban",
        }
    ),
    "hal": frozenset(
        {
            "hal-import-health",
            "hal-mosaic-prod",
            "hal-mosaic-coll",
            "hal-ask",
            "hal-recommended-actions",
            "hal-ai-insight",
            "hal-full-log",
        }
    ),
    "taxes": frozenset(
        {
            "taxes-period-scrubber",
            "tax-year-status",
            "tax-core-strip",
            "tax-open-planning",
            "tax-disclaimer",
            "tax-bridge-waterfall",
        }
    ),
    "softdent": frozenset(
        {
            "sd-vitals-strip",
            "collections-gauge",
            "softdent-visual-ledger-recon",
            "softdent-gold-csv-drop-ops",
            "sd-prod-trend",
            "softdent-tp-estimate-chips",
        }
    ),
    "ar": frozenset(
        {
            "ar-vitals-strip",
            "ar-aging-chart",
            "collection-bullet",
            "collections-gauge",
            "ar-collection-task-list",
            "ar-follow-up",
        }
    ),
    "quickbooks": frozenset(
        {
            "qb-vitals-strip",
            "qb-net-profit-gap",
            "qb-payroll-gap",
            "qb-expense-hbar",
            "qb-ap-aging",
        }
    ),
    "office-manager": frozenset(
        {
            "om-vitals-strip",
            "om-daily-huddle",
            "operatory-util-trend",
            "om-priorities",
            "om-open-operatory",
        }
    ),
}

# Ops subpages stay zero-scroll: only these demoted ids surface (hal-10615).
PAGE_OPS_KEEP: dict[str, frozenset[str]] = {
    "softdent": frozenset(
        {
            "softdent-collections-gap",
            "softdent-outstanding-claims-bridge",
            "softdent-aging-gap",
            "softdent-production-gap",
            "softdent-account-tx-coverage",
            "softdent-transaction-ledger",
            "stale-import-alert",
            "v-patient-aging",
        }
    ),
    "claims": frozenset(
        {
            "claims-risk-analytics",
            "eob-posting-backlog",
            "clinical-signoff-queue",
            "claim-status-lanes",
            "claims-open-kanban",
        }
    ),
    "financial": frozenset(
        {
            "ebitda-station",
            "expense-treemap",
            "revenue-composition",
            "deep-audit-status",
            "reconciliation-status",
            "bridge-errors",
        }
    ),
    "hal": frozenset(
        {
            "hal-full-log",
            "hal-recommended-actions",
            "hal-ai-insight",
            "stale-import-alert",
            "import-health-timeline",
        }
    ),
}

# Chronic empty until SoftDent source lands — omit (do not scroll empty tiles).
# warming-bridge stays for cold stub only; final payloads omit it via omit_until_source.
OMIT_UNTIL_SOURCE_IDS = frozenset(
    {
        "claims-era-gauge",
        "denial-pareto",
        "verification-matrix",
        "gold-csv-ticket-ops",
        "import-cache-kpi",
        "import-health-monitor",
        "ins-patient-split",
        "preauth-aging-lanes",
        "payer-change-alerts",
        "warming-bridge",
        "kpi-data-pending",
    }
)

# Always keep on parent even if not in page keep set
_ALWAYS_KEEP_IDS = frozenset(
    {
        # warming-bridge removed (hal-10615) — omit until fill done
    }
)


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


def omit_until_source_widgets(widgets: list[Any], *, page: str = "", sub: str = "") -> list[Any]:
    """Drop chronic empty SoftDent-source widgets so pages do not scroll blanks (hal-10615)."""
    del page, sub  # reserved for future page-scoped exceptions
    if not isinstance(widgets, list):
        return widgets
    out: list[Any] = []
    for w in widgets:
        if not isinstance(w, dict):
            out.append(w)
            continue
        wid = str(w.get("id") or "")
        status = str(w.get("status") or "").lower()
        if wid in OMIT_UNTIL_SOURCE_IDS:
            # Omit while empty / warming. Show only when real status arrives (ok/warn with data).
            if status in {"empty", "awaiting-migration", "warming", ""}:
                continue
            if status == "warn" and wid in {
                "import-cache-kpi",
                "import-health-monitor",
                "gold-csv-ticket-ops",
            }:
                # Still no source file — keep ops quiet until CSV/ERA exists
                if not w.get("paymentLines") and not w.get("value") and not w.get("rows"):
                    continue
        out.append(w)
    return out


def compact_widget_sizes(widgets: list[Any], *, page: str = "", sub: str = "") -> list[Any]:
    """Force denser sizes on remaining tiles (zero-scroll stage)."""
    if not isinstance(widgets, list):
        return widgets
    out: list[Any] = []
    for i, w in enumerate(widgets):
        if not isinstance(w, dict):
            out.append(w)
            continue
        item = dict(w)
        size = str(item.get("size") or "").lower()
        wtype = str(item.get("type") or "")
        item["compact"] = True
        if size in {"xl", "full", "large"}:
            item["size"] = "m" if i > 0 else "l"
        elif size == "l" and i > 0:
            item["size"] = "m"
        if wtype in {"status", "executive-strip", "claims-executive-strip", "financial-command-strip"}:
            item["size"] = "strip" if size != "s" else size
            item.setdefault("maxHeight", MAX_MICRO_PX)
        elif str(item.get("size") or "") in {"s", "strip", "xs"}:
            item.setdefault("maxHeight", MAX_MICRO_PX)
        elif str(item.get("size") or "") == "m":
            item.setdefault("maxHeight", MAX_SECONDARY_PX)
        else:
            item.setdefault("maxHeight", MAX_PRIMARY_PX)
        out.append(item)
    return out


def is_empty_kpi(widget: dict[str, Any]) -> bool:
    """True when a KPI tile has no import-backed value (empty ≠ $0)."""
    if not isinstance(widget, dict):
        return False
    if str(widget.get("type") or "") != "kpi":
        return False
    if widget.get("keepEmpty") is True:
        return False
    status = str(widget.get("status") or "").lower()
    if status in {"empty", "awaiting-migration"}:
        return True
    return widget.get("value") is None or widget.get("value") == ""


def build_kpi_micro_strip(
    strip_id: str,
    label: str,
    pills: list[dict[str, Any]],
    *,
    hint: str = "",
    nav_hash: str | None = None,
    max_pills: int = KPI_BUDGET_ABOVE_FOLD,
) -> dict[str, Any]:
    """Pack up to 4 KPI pills into one executive-strip (counts as 1 mosaic slot)."""
    cleaned: list[dict[str, Any]] = []
    for p in pills[: max(1, int(max_pills))]:
        if not isinstance(p, dict):
            continue
        pill = dict(p)
        if "empty" not in pill:
            pill["empty"] = pill.get("value") is None or pill.get("value") == ""
        cleaned.append(pill)
    any_data = any(not p.get("empty") for p in cleaned)
    out: dict[str, Any] = {
        "id": strip_id,
        "type": "executive-strip",
        "label": label,
        "size": "strip",
        "compact": True,
        "maxHeight": MAX_MICRO_PX,
        "pills": cleaned,
        "status": "ok" if any_data else "empty",
        "emptyMessage": "Import data pending — empty stays empty (not $0).",
        "hint": hint or "KPI micro-strip · ≤4 pills · never invents dollars.",
        "collapseWhenEmpty": True,
        "kpiBudgetExempt": True,
        "aliasIds": [str(p.get("id") or "") for p in cleaned if p.get("id")],
    }
    if nav_hash:
        out["navHash"] = nav_hash
    return out


def pending_modules_chip(omitted_labels: list[str]) -> dict[str, Any] | None:
    """One composite status chip for multiple omitted empty KPIs."""
    labels = [str(x).strip() for x in omitted_labels if str(x).strip()]
    if not labels:
        return None
    n = len(labels)
    preview = ", ".join(labels[:3])
    if n > 3:
        preview += f" +{n - 3} more"
    return {
        "id": "kpi-data-pending",
        "type": "status",
        "label": "Data Pending",
        "size": "strip",
        "compact": True,
        "maxHeight": MAX_MICRO_PX,
        "status": "empty",
        "message": f"{n} module(s) pending",
        "hint": f"Omitted empty KPIs (not $0): {preview}",
        "collapseWhenEmpty": True,
        "kpiBudgetExempt": True,
    }


def apply_kpi_density_contract(
    widgets: list[Any],
    *,
    page: str = "",
    sub: str = "",
    budget: int = KPI_BUDGET_ABOVE_FOLD,
) -> list[Any]:
    """Omit empty KPIs; enforce ≤budget standalone KPI tiles on parent pages.

    Executive-strips / command strips are exempt (already packed). Subpages keep
    planning detail KPIs. Honesty: never pad empty with $0.
    """
    if not isinstance(widgets, list):
        return widgets
    is_subpage = bool(str(sub or "").strip())
    cap = max(0, int(budget))
    out: list[Any] = []
    omitted: list[str] = []
    kpi_kept = 0
    pending_inserted = False

    for w in widgets:
        if not isinstance(w, dict):
            out.append(w)
            continue
        item = dict(w)
        wtype = str(item.get("type") or "")
        if wtype == "kpi" and is_empty_kpi(item) and item.get("omitWhenEmpty") is not False:
            # Default: omit empty KPI mosaic slots
            if item.get("omitWhenEmpty") is True or item.get("collapseWhenEmpty") is not False:
                omitted.append(str(item.get("label") or item.get("id") or "KPI"))
                continue
        if wtype == "kpi" and not is_subpage and item.get("kpiBudgetExempt") is not True:
            if kpi_kept >= cap:
                if is_empty_kpi(item):
                    omitted.append(str(item.get("label") or item.get("id") or "KPI"))
                    continue
                # Excess populated KPIs → demote to micro strip chip (still visible, not tile flood)
                item["size"] = "xs"
                item["compact"] = True
                item["maxHeight"] = MAX_MICRO_PX
                item["kpiOverBudget"] = True
                item["hint"] = (
                    str(item.get("hint") or "")
                    + f" · Over KPI budget (>{cap}); demoted micro."
                ).strip(" ·")
            else:
                kpi_kept += 1
                item.setdefault("size", "s")
                item.setdefault("maxHeight", MAX_MICRO_PX)
        item["kpiDensity"] = True
        out.append(item)

    if omitted and not is_subpage and not pending_inserted:
        chip = pending_modules_chip(omitted)
        if chip:
            # Place after first strip/command if present, else at front
            insert_at = 0
            for i, x in enumerate(out):
                if isinstance(x, dict) and str(x.get("type") or "") in {
                    "financial-command-strip",
                    "executive-strip",
                    "claims-executive-strip",
                    "import-freshness",
                    "import-health",
                    "status",
                }:
                    insert_at = i + 1
            out.insert(insert_at, chip)

    return out


def apply_collapse_empty_all(widgets: list[Any], *, page: str = "") -> list[Any]:
    out: list[Any] = []
    # Exempt strips and analysis/gap surfaces from empty-omit (hal-10611)
    exempt_if_empty = {
        "financial-command-strip",
        "claims-executive-strip",
        "status",
        "import-freshness",
        "import-health",
        "analysis",
        "gap",
    }
    for w in widgets:
        if isinstance(w, dict):
            wid = str(w.get("id") or "")
            if wid in OMIT_UNTIL_SOURCE_IDS and str(w.get("status") or "").lower() in {
                "empty",
                "awaiting-migration",
                "warming",
                "",
            }:
                continue
            # Financial + claims + all pages: omit non-strip empty widgets (hal-10615)
            wtype = str(w.get("type") or "")
            if w.get("status") == "empty" and wtype not in exempt_if_empty:
                continue
            if page == "financial":
                if w.get("status") == "empty" and wtype not in exempt_if_empty:
                    continue
            out.append(collapse_empty_large(w))
        else:
            out.append(w)
    return out


def normalize_first_viewport(widgets: list[Any], *, page: str = "") -> list[Any]:
    """Cap first-viewport sizes: no xl above fold; at most one l in first six.

    Zero-scroll (hal-10561): HAL sole-l exemption REMOVED — chat follows same rules.
    """
    if not isinstance(widgets, list):
        return widgets
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

        if i < 6:
            if size == "xl":
                item["size"] = "l" if large_seen == 0 else "m"
                size = item["size"]
            if size in {"l", "large", "full"}:
                if size == "full" and wtype not in {"claims-workbench", "claims-kanban"}:
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
                elif size == "full" and wtype in {"claims-workbench", "claims-kanban"}:
                    # Main-page boards must not remain full; subpage may keep full.
                    item["size"] = "m"
        out.append(item)
    return out


def _tier_for_size(size: str, wtype: str) -> str:
    s = str(size or "").lower()
    t = str(wtype or "").lower()
    if s in {"strip", "xs"} or t in {
        "status",
        "kpi",
        "bullet",
        "credit-float",
        "financial-command-strip",
        "claims-executive-strip",
        "executive-strip",
    }:
        return "micro"
    if s in {"s"}:
        return "micro"
    if s in {"m"} or t in {"hal-chat", "ai-insight"}:
        return "secondary"
    if s in {"l", "large"}:
        return "primary"
    # xl/full → treat as primary then demote in apply_zero_scroll
    return "primary"


def apply_zero_scroll_contract(widgets: list[Any], *, page: str = "", sub: str = "") -> list[Any]:
    """Moonshot zero-scroll: hard height tiers, row caps, no HAL sole-l, no main kanban.

    Subpages (e.g. claims/kanban) may keep taller boards with internal scroll.
    """
    if not isinstance(widgets, list):
        return widgets
    page_key = str(page or "").strip().lower()
    sub_key = str(sub or "").strip().lower()
    is_subpage = bool(sub_key)
    out: list[Any] = []
    primary_seen = 0

    for w in widgets:
        if not isinstance(w, dict):
            out.append(w)
            continue
        item = dict(w)
        wtype = str(item.get("type") or "")
        wid = str(item.get("id") or "")
        size = str(item.get("size") or "").lower()

        # Claims Overview: never emit full workbench/kanban (subpage only)
        if (
            page_key == "claims"
            and not is_subpage
            and wtype in {"claims-workbench", "claims-kanban"}
        ):
            item["size"] = "s"
            item["compact"] = True
            item["rowCap"] = TABLE_ROW_CAP
            item["maxHeight"] = MAX_PRIMARY_PX
            item["hint"] = (
                str(item.get("hint") or "")
                + " · Open #claims/kanban for full board (zero-scroll)."
            ).strip(" ·")
            item["navHash"] = item.get("navHash") or "claims/kanban"

        # HAL: chat is a capped secondary tile — no sole-l / no 100vh fill
        if wtype == "hal-chat" or wid == "hal-ask":
            item["size"] = "m"
            item["compact"] = True
            item["maxHeight"] = MAX_PRIMARY_PX
            item["hint"] = "HAL command tile · capped for zero-scroll (no sole-l)."

        # Demote monuments on parent pages
        if not is_subpage:
            if size in {"xl", "full", "large"}:
                if primary_seen == 0 and wtype not in {
                    "claims-workbench",
                    "claims-kanban",
                    "hal-chat",
                }:
                    item["size"] = "l"
                    primary_seen += 1
                else:
                    item["size"] = "m"
            elif size == "l":
                if primary_seen >= 1:
                    item["size"] = "m"
                else:
                    primary_seen += 1

        size = str(item.get("size") or "").lower()
        tier = _tier_for_size(size, wtype)
        if "maxHeight" not in item or not isinstance(item.get("maxHeight"), int):
            if tier == "micro":
                item["maxHeight"] = MAX_MICRO_PX
            elif tier == "secondary":
                item["maxHeight"] = MAX_SECONDARY_PX
            else:
                item["maxHeight"] = MAX_PRIMARY_PX

        # Table / list row caps (main pages hard; subpages keep higher if already set)
        if not is_subpage:
            if wtype in {
                "claims-workbench",
                "claims-kanban",
                "claims-critical-actions",
                "data-table",
                "collection-task-list",
                "era-matching-table",
                "schedule-list",
            }:
                cap = item.get("rowCap")
                if not isinstance(cap, int) or cap > TABLE_ROW_CAP_HARD:
                    item["rowCap"] = TABLE_ROW_CAP
            # Critical claims list: Top 5
            if wid in {"claims-critical-actions", "claims-top-critical"} or wtype == "claims-critical-actions":
                item["rowCap"] = TABLE_ROW_CAP
                item["maxHeight"] = MAX_PRIMARY_PX
                item["size"] = item.get("size") if item.get("size") in {"s", "m", "l"} else "m"

        # Subpage boards: internal scroll allowed; still emit maxHeight for CSS clamp
        if is_subpage and wtype in {"claims-workbench", "claims-kanban"}:
            item.setdefault("maxHeight", 720)
            item.setdefault("rowCap", 50)
            item["internalScroll"] = True

        item["zeroScroll"] = True
        out.append(item)

    # HAL: ensure Full Log affordance after chat/posture
    if page_key == "hal" and not is_subpage:
        has_full_log = any(
            isinstance(x, dict) and str(x.get("id") or "") == "hal-full-log"
            for x in out
        )
        if not has_full_log:
            insert_at = 0
            for i, x in enumerate(out):
                if isinstance(x, dict) and str(x.get("type") or "") == "hal-chat":
                    insert_at = i + 1
                    break
            out.insert(
                insert_at,
                {
                    "id": "hal-full-log",
                    "type": "status",
                    "label": "Full Log",
                    "size": "strip",
                    "compact": True,
                    "status": "ok",
                    "message": "Open full HAL audit / message history",
                    "hint": "Zero-scroll: audit trail lives behind Full Log (not sole-l).",
                    "maxHeight": MAX_MICRO_PX,
                    "halAction": "open_hal_full_log",
                    "halActionLabel": "Full Log",
                    "zeroScroll": True,
                },
            )

    return out


def claims_pipeline_summary_widget(counts: dict[str, Any] | None, *, available: bool) -> dict[str, Any]:
    """Claims mode: summary strip + Open Kanban (not clipped board)."""
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
        "maxHeight": MAX_MICRO_PX,
        "zeroScroll": True,
        "pills": pills,
        "status": "ok" if has else "empty",
        "emptyMessage": "Import SoftDent claims — then open Kanban for the full board",
        "hint": "Zero-scroll pipeline · full workbench on #claims/kanban.",
        "navHash": "claims/kanban",
        "halAction": "open_claims_kanban",
        "halActionLabel": "Open Kanban",
        "aliasIds": ["claims-kanban-board"],
    }


def claims_top_critical_widget(rows: list[Any] | None, *, available: bool) -> dict[str, Any]:
    """Main Claims: Top 5 critical claims ≤320px (Moonshot page map)."""
    raw = [r for r in (rows or []) if isinstance(r, dict)]
    top = raw[:TABLE_ROW_CAP]
    has = available and len(top) > 0
    return {
        "id": "claims-top-critical",
        "type": "claims-critical-actions",
        "label": "Top 5 Critical Claims",
        "size": "m",
        "compact": True,
        "rowCap": TABLE_ROW_CAP,
        "maxHeight": MAX_PRIMARY_PX,
        "zeroScroll": True,
        "rows": top,
        "status": "ok" if has else "empty",
        "emptyMessage": "No critical claims in import — empty stays empty.",
        "hint": "Zero-scroll Top 5 · full board on #claims/kanban.",
        "navHash": "claims/kanban",
    }


def open_detail_strip(*, page: str, sub: str, label: str, message: str) -> dict[str, Any]:
    return {
        "id": f"{page}-{sub}-open",
        "type": "status",
        "label": label,
        "size": "strip",
        "compact": True,
        "maxHeight": MAX_MICRO_PX,
        "zeroScroll": True,
        "status": "ok",
        "message": message,
        "hint": f"Open #{page}/{sub}",
        "navHash": f"{page}/{sub}",
    }


def _is_always_keep(wid: str) -> bool:
    if wid in _ALWAYS_KEEP_IDS:
        return True
    if wid.endswith("-open"):
        return True
    return False


def partition_first_viewport(
    widgets: list[Any],
    *,
    page: str,
    sub: str = "",
) -> list[Any]:
    """Keep ~6 first-viewport widgets; demote the rest to #{page}/ops.

    Parent pages only. Subpages (including ops) are untouched. SoftDent Gold CSV
    drop OPS stays on main when listed in PAGE_FIRST_VIEW_KEEP.
    """
    if not isinstance(widgets, list):
        return widgets
    page_key = str(page or "").strip().lower()
    if str(sub or "").strip():
        return widgets
    keep_set = PAGE_FIRST_VIEW_KEEP.get(page_key)
    if not keep_set:
        return widgets

    kept: list[Any] = []
    demoted_labels: list[str] = []
    for w in widgets:
        if not isinstance(w, dict):
            kept.append(w)
            continue
        wid = str(w.get("id") or "")
        if wid in keep_set or _is_always_keep(wid):
            kept.append(w)
            continue
        demoted_labels.append(str(w.get("label") or wid or "widget"))

    if not demoted_labels:
        return kept

    n = len(demoted_labels)
    preview = ", ".join(demoted_labels[:4])
    if n > 4:
        preview += f" +{n - 4} more"
    ops = open_detail_strip(
        page=page_key,
        sub="ops",
        label="More Ops",
        message=f"{n} widget(s) moved to Ops — {preview}",
    )
    # Prefer after command/executive strip if present
    insert_at = len(kept)
    for i, x in enumerate(kept):
        if isinstance(x, dict) and str(x.get("type") or "") in {
            "financial-command-strip",
            "claims-executive-strip",
            "executive-strip",
        }:
            insert_at = i + 1
            break
    kept.insert(insert_at, ops)
    return kept


def select_demoted_widgets(widgets: list[Any], *, page: str) -> list[Any]:
    """Build #{page}/ops payload: demoted keep-set for zero-scroll Ops (hal-10615)."""
    if not isinstance(widgets, list):
        return []
    page_key = str(page or "").strip().lower()
    keep_set = PAGE_FIRST_VIEW_KEEP.get(page_key, frozenset())
    ops_keep = PAGE_OPS_KEEP.get(page_key)
    out: list[Any] = [
        {
            "id": f"{page_key}-overview-open",
            "type": "status",
            "label": "Back to Overview",
            "size": "strip",
            "compact": True,
            "maxHeight": MAX_MICRO_PX,
            "zeroScroll": True,
            "status": "ok",
            "message": f"Overview keeps the zero-scroll set · #{page_key}",
            "hint": f"Open #{page_key}",
            "navHash": page_key,
        }
    ]

    skipped_ops = 0
    for w in widgets:
        if not isinstance(w, dict):
            continue
        wid = str(w.get("id") or "")
        if wid in keep_set or _is_always_keep(wid):
            continue
        if wid in OMIT_UNTIL_SOURCE_IDS and str(w.get("status") or "").lower() in {
            "empty",
            "awaiting-migration",
            "warming",
            "",
        }:
            continue
        if ops_keep is not None and wid not in ops_keep:
            skipped_ops += 1
            continue
        out.append(w)
    if skipped_ops:
        out.append(
            {
                "id": f"{page_key}-ops-more-omitted",
                "type": "status",
                "label": "Compact Ops",
                "size": "strip",
                "compact": True,
                "maxHeight": MAX_MICRO_PX,
                "zeroScroll": True,
                "status": "ok",
                "message": f"{skipped_ops} optional SoftDent/ops tile(s) hidden for zero-scroll",
                "hint": "Ask HAL for gold/ERA/print-preview playbooks when needed.",
            }
        )
    if len(out) == 1:
        out.append(
            {
                "id": f"{page_key}-ops-empty",
                "type": "status",
                "label": "Ops",
                "size": "strip",
                "compact": True,
                "status": "empty",
                "message": "No demoted widgets for this page right now.",
                "emptyMessage": "Nothing to show in Ops — empty stays empty.",
                "maxHeight": MAX_MICRO_PX,
                "zeroScroll": True,
            }
        )
    return out
