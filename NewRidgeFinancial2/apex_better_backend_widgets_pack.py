"""
NR2 Apex — Better Backend Widgets Pack (Moonshot MUST items).
Emit denser widget types without KPI sprawl.

Honesty constraints:
- Never invents dollar amounts.
- empty ≠ $0 (DEF-001).
- Maps live FE contracts via minimal adaptation layer.
"""

from __future__ import annotations

from typing import Any


def _parse_money(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "").replace("$", "")
    if not text or text in {"—", "-", "N/A", "n/a"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _initials(name: str) -> str:
    parts = str(name).strip().split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[-1][0]}".upper()
    if parts:
        return parts[0][:2].upper()
    return "—"


def _iso_to_display(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        from datetime import datetime

        d = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
        return d.strftime("%b %d")
    except Exception:
        return str(iso)[:10]


def _dashboard_rows(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    """Same SoftDent dashboard path as build_collection_bullet (live honesty)."""
    sd = bundle.get("softdent") if isinstance(bundle.get("softdent"), dict) else {}
    dash = sd.get("dashboard") if isinstance(sd.get("dashboard"), dict) else {}
    rows = dash.get("rows")
    if isinstance(rows, list):
        return [r for r in rows if isinstance(r, dict)]
    if isinstance(dash.get("data"), list):
        return [r for r in dash["data"] if isinstance(r, dict)]
    return []


def build_tax_planning_data_table(bundle: dict[str, Any]) -> dict[str, Any] | None:
    """
    MUST: Tax Planning Data-Table for taxes page (main or planning).
    Emits dense table replacing KPI tiles for planning items.
    """
    plan: dict[str, Any] = {}
    try:
        from tax_engine import build_tax_plan_from_bundle

        plan = build_tax_plan_from_bundle(bundle) or {}
    except Exception:
        plan = {}

    items: list[dict[str, Any]] = []

    # K-1 / Owner pass-through items
    bridge = plan.get("bridgeLines") if isinstance(plan.get("bridgeLines"), list) else []
    for b in bridge:
        if not isinstance(b, dict):
            continue
        line = str(b.get("line") or "")
        amt = _parse_money(b.get("amount"))
        items.append(
            {
                "Item": line or "Owner distribution",
                "Type": "Pass-through",
                "Status": "Mapped" if line else "Unmapped",
                "Impact": amt,
                "Due": "Year-end",
            }
        )

    # Quarterly estimates (live tax_engine: period/federal/kansas/due)
    quarterly = plan.get("quarterlyEstimates") if isinstance(plan.get("quarterlyEstimates"), list) else []
    for q in quarterly:
        if not isinstance(q, dict):
            continue
        quarter = str(q.get("quarter") or q.get("period") or "Q?")
        fed = _parse_money(q.get("federal") or q.get("amount") or q.get("estimatedTax"))
        ks = _parse_money(q.get("kansas"))
        amt = None
        if fed is not None or ks is not None:
            amt = float(fed or 0.0) + float(ks or 0.0)
        due = q.get("dueDate") or q.get("deadline") or q.get("due")
        due_disp = str(due) if due else "TBD"
        if due and "-" in str(due) and len(str(due)) >= 8:
            due_disp = _iso_to_display(str(due))
        items.append(
            {
                "Item": f"Est. Tax {quarter}",
                "Type": "1040-ES",
                "Status": str(q.get("status") or ("Due" if amt is not None else "TBD")),
                "Impact": amt,
                "Due": due_disp,
            }
        )

    # Officer W-2 modeling (live: modeledOfficerW2 scalar; optional officerW2s list)
    w2s = plan.get("officerW2s") if isinstance(plan.get("officerW2s"), list) else []
    for w in w2s:
        if not isinstance(w, dict):
            continue
        name = str(w.get("officer") or w.get("name") or "Officer")
        wages = _parse_money(w.get("wages") or w.get("w2Wages"))
        items.append(
            {
                "Item": f"W-2 {_initials(name)}",
                "Type": "Officer comp",
                "Status": "Modeled",
                "Impact": wages,
                "Due": "Jan 31",
            }
        )
    if not w2s:
        modeled = _parse_money(plan.get("modeledOfficerW2"))
        if modeled is not None:
            items.append(
                {
                    "Item": "W-2 Officer",
                    "Type": "Officer comp",
                    "Status": "Modeled",
                    "Impact": modeled,
                    "Due": "Jan 31",
                }
            )

    if not items:
        return {
            "id": "tax-planning-table",
            "type": "data-table",
            "label": "Tax Planning Items",
            "size": "l",
            "status": "empty",
            "emptyMessage": "Import QuickBooks and SoftDent to populate planning items.",
            "hint": "Tax planning requires book data and tax_engine mapping.",
            "columns": ["Item", "Type", "Status", "Impact", "Due"],
            "rows": [],
        }

    return {
        "id": "tax-planning-table",
        "type": "data-table",
        "label": "Tax Planning Items",
        "size": "l",
        "status": "ok",
        "columns": ["Item", "Type", "Status", "Impact", "Due"],
        "rows": items,
        "hint": f"{len(items)} planning items from tax_engine — CPA review required.",
        "collapseWhenEmpty": False,
    }


def build_collections_radial_gauge(
    bundle: dict[str, Any], reports: dict[str, Any] | None = None
) -> dict[str, Any] | None:
    """
    MUST: Collections Radial-Gauge for financial/ar pages.
    Adapted to live radial-gauge contract via mode flag.
    """
    reports = reports if isinstance(reports, dict) else {}
    rows = reports.get("productionCollectionsRows") or reports.get("financialRows") or []
    if not isinstance(rows, list):
        rows = []
    if not rows and isinstance(bundle.get("financial"), dict):
        fin_rows = bundle["financial"].get("rows") or []
        if isinstance(fin_rows, list):
            rows = fin_rows
    # Live SoftDent dashboard (same source as build_collection_bullet)
    if not rows:
        rows = _dashboard_rows(bundle)

    chosen = None
    for row in reversed(rows):
        if not isinstance(row, dict):
            continue
        prod = _parse_money(row.get("production") or row.get("Production"))
        if prod is None or prod <= 0:
            continue
        if row.get("collectionsReported") is False or row.get("collectionsPending") is True:
            continue
        if "collections" not in row and "Collections" not in row:
            continue
        coll = _parse_money(row.get("collections") or row.get("Collections"))
        if coll is None:
            continue
        chosen = (prod, coll, row.get("period") or row.get("year_month"))
        break

    if not chosen:
        return {
            "id": "collections-gauge",
            "type": "radial-gauge",
            "label": "Collection Efficiency",
            "size": "m",
            "status": "empty",
            "emptyMessage": "Collections pending or production not reported",
            "hint": "Ratio appears when both production and collections are finalized.",
            "data": {
                "due": None,
                "pctScheduled": None,
                "scheduled": None,
                "contacted": None,
                "mode": "collections",
                "target": 98,
                "emptyMessage": "Collections pending or production not reported",
            },
        }

    prod, coll, period = chosen
    ratio_pct = round((coll / prod) * 100, 1)

    return {
        "id": "collections-gauge",
        "type": "radial-gauge",
        "label": "Collection Efficiency",
        "size": "m",
        "status": "ok",
        "hint": f"Collections ÷ production for {period or 'period'} — target 98%.",
        "data": {
            "due": 100.0,
            "pctScheduled": ratio_pct,
            "scheduled": coll,
            "contacted": prod,
            "mode": "collections",
            "target": 98,
            "period": period,
        },
    }


def build_system_health_status_matrix(bundle: dict[str, Any]) -> dict[str, Any]:
    """
    MUST: System Health Status-Matrix for office-manager.
    Maps SoftDent/QB/Claims/HAL into live status-matrix patients contract.
    """
    diag = bundle.get("diagnostics") if isinstance(bundle.get("diagnostics"), dict) else {}
    summary = diag.get("summary") if isinstance(diag.get("summary"), dict) else {}
    datasets = diag.get("datasets") if isinstance(diag.get("datasets"), list) else []
    meta = bundle.get("import_meta") if isinstance(bundle.get("import_meta"), dict) else {}

    def _tone_from_dataset_status(st: str) -> str:
        s = str(st or "").lower()
        if s in {"connected", "ok", "ready", "fresh"}:
            return "verified"
        if s in {"partial", "stale", "pending"}:
            return "pending"
        if s in {"missing", "error", "failed"}:
            return "failed"
        return "unknown"

    by_key: dict[str, str] = {}
    for item in datasets:
        if not isinstance(item, dict):
            continue
        key = str(item.get("key") or item.get("dataset") or item.get("name") or "").lower()
        if not key:
            continue
        by_key[key] = _tone_from_dataset_status(str(item.get("status") or ""))

    def _pick(*needles: str) -> str:
        for needle in needles:
            for key, tone in by_key.items():
                if needle in key:
                    return tone
        return "unknown"

    sd_status = _pick("softdent", "dentrix", "sd_")
    qb_status = _pick("quickbooks", "qb_", "qbo")
    claims_status = _pick("claim")

    # Fallback when datasets missing: summary counts only
    if sd_status == "unknown" and qb_status == "unknown":
        connected = summary.get("connected")
        missing = summary.get("missing")
        stale = summary.get("stale")
        if isinstance(connected, int) and connected > 0:
            sd_status = "verified"
            qb_status = "verified"
        if isinstance(missing, int) and missing > 0:
            sd_status = "failed" if sd_status == "unknown" else sd_status
        if isinstance(stale, int) and stale > 0:
            qb_status = "pending" if qb_status == "verified" else qb_status

    claims_meta = meta.get("claims") if isinstance(meta.get("claims"), dict) else {}
    claims_last = claims_meta.get("lastRun") or claims_meta.get("lastSuccess")
    if claims_status == "unknown":
        claims_stale = claims_meta.get("stale") or (claims_last is None)
        claims_status = "verified" if claims_last and not claims_stale else "pending" if claims_stale else "unknown"

    hal_status = "verified"

    patients = [
        {
            "hash": "SoftDent",
            "elig": sd_status,
            "ben": "ok" if sd_status == "verified" else None,
            "breakdown": None,
        },
        {"hash": "QuickBooks", "elig": qb_status, "ben": None, "breakdown": None},
        {"hash": "Claims", "elig": claims_status, "ben": None, "breakdown": None},
        {"hash": "HAL", "elig": hal_status, "ben": None, "breakdown": None},
    ]

    all_empty = all(p["elig"] == "unknown" for p in patients)

    return {
        "id": "system-health-matrix",
        "type": "status-matrix",
        "label": "System Health",
        "size": "m",
        "status": "empty" if all_empty else "ok",
        "emptyMessage": "System diagnostics unavailable — refresh imports.",
        "hint": "Import freshness: ●Active ○Stale ◉Error",
        "data": {
            "patients": patients,
            "headers": ["System", "Import", "Sync", "Status"],
            "emptyMessage": "System diagnostics unavailable",
        },
    }
