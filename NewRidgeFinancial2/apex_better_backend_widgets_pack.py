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


# ---------------------------------------------------------------------------
# Moonshot SHOULD wave — continuation after MUST (hal-10567)
# Gap-fill: action-list (hal), collection-task-list (ar main),
# ai-insight (narratives), patient-dossier-card (softdent)
# ---------------------------------------------------------------------------


def _section_rows(bundle: dict[str, Any], system: str, key: str) -> list[dict[str, Any]]:
    root = bundle.get(system) if isinstance(bundle.get(system), dict) else {}
    if not isinstance(root, dict):
        return []
    block = root.get(key)
    if isinstance(block, list):
        return [r for r in block if isinstance(r, dict)]
    if isinstance(block, dict):
        rows = block.get("rows")
        if isinstance(rows, list):
            return [r for r in rows if isinstance(r, dict)]
        data = block.get("data")
        if isinstance(data, list):
            return [r for r in data if isinstance(r, dict)]
    return []


def _patient_initials(name: str) -> str:
    return _initials(name)


def _load_local_json(key: str) -> dict[str, Any] | None:
    try:
        import json

        from document_sync import NR2_DATA_DIR
        from local_store import LocalStore

        raw = LocalStore(NR2_DATA_DIR).get(key)
        if not raw:
            return None
        payload = json.loads(raw) if isinstance(raw, str) else raw
        return payload if isinstance(payload, dict) else None
    except Exception:
        return None


def build_hal_action_list(bundle: dict[str, Any]) -> dict[str, Any]:
    """HAL recommended actions (action-list). Rule-backed; no invented $."""
    items: list[dict[str, Any]] = []
    diag = bundle.get("diagnostics") if isinstance(bundle.get("diagnostics"), dict) else {}
    summary = diag.get("summary") if isinstance(diag.get("summary"), dict) else {}
    missing = summary.get("missing") or 0
    stale = summary.get("stale") or 0
    try:
        missing = int(missing)
    except (TypeError, ValueError):
        missing = 0
    try:
        stale = int(stale)
    except (TypeError, ValueError):
        stale = 0

    if missing:
        items.append(
            {
                "id": "hal-act-missing-imports",
                "label": f"Reconnect {missing} missing data source(s)",
                "payer": "System",
                "status": "alert",
                "amount": None,
                "serviceDate": "",
            }
        )
    if stale:
        items.append(
            {
                "id": "hal-act-stale-imports",
                "label": f"Refresh {stale} stale dataset(s)",
                "payer": "System",
                "status": "warning",
                "amount": None,
                "serviceDate": "",
            }
        )

    try:
        from apex_structured_insight_pack import load_last_insight

        insight = load_last_insight() or {}
        audit = insight.get("efficiency_audit") if isinstance(insight, dict) else None
        if isinstance(audit, dict) and audit.get("flag"):
            items.append(
                {
                    "id": "hal-act-efficiency",
                    "label": f"Efficiency alert: {audit.get('message', 'Review payroll vs production')}",
                    "payer": "Practice",
                    "status": "review",
                    "amount": audit.get("variance_dollars"),
                    "serviceDate": str(audit.get("period") or ""),
                }
            )
    except Exception:
        pass

    tax = bundle.get("taxes") if isinstance(bundle.get("taxes"), dict) else {}
    if tax.get("next_deadline"):
        items.append(
            {
                "id": "hal-act-filing",
                "label": f"Upcoming filing: {tax.get('next_deadline')}",
                "payer": "IRS/KDOR",
                "status": "scheduled",
                "amount": None,
                "serviceDate": str(tax.get("due_date") or ""),
            }
        )

    status = "ok" if items else "empty"
    return {
        "id": "hal-recommended-actions",
        "type": "action-list",
        "label": "Recommended Actions",
        "size": "m",
        "status": status,
        "emptyMessage": "No active recommendations — imports healthy and filings on track.",
        "hint": "Rule-backed HAL prompts (no LLM inference).",
        "data": {
            "items": items,
            "count": len(items),
            "emptyMessage": "No active recommendations — imports healthy and filings on track.",
        },
    }


def build_ar_main_collection_task_list(bundle: dict[str, Any]) -> dict[str, Any]:
    """A/R MAIN page collection-task-list. Seeds from aging/denied; PHI = initials."""
    seeds: list[dict[str, Any]] = []
    notes: list[dict[str, Any]] = []

    try:
        from apex_claims_narratives_pack import build_aging_buckets, normalize_claim_row

        rows = (
            _section_rows(bundle, "softdent", "claims")
            or _section_rows(bundle, "softdent", "claimStatus")
            or []
        )
        aging = build_aging_buckets(rows)
        for bucket_key in ("90", "60", "30"):
            tiles = (aging.get("buckets") or {}).get(bucket_key) or []
            if not isinstance(tiles, list):
                continue
            for tile in tiles[:20]:
                if not isinstance(tile, dict):
                    continue
                seeds.append(
                    {
                        "claimId": tile.get("claimId"),
                        "patientInitials": _patient_initials(str(tile.get("patientName") or "")),
                        "ageDays": tile.get("ageDays"),
                        "bucket": bucket_key,
                        "billedAmount": tile.get("billedAmount"),
                    }
                )
        for row in rows:
            tile = normalize_claim_row(row)
            if not tile:
                continue
            if str(tile.get("status") or "").lower() in ("denied", "rejected"):
                seeds.append(
                    {
                        "claimId": tile.get("claimId"),
                        "patientInitials": _patient_initials(str(tile.get("patientName") or "")),
                        "ageDays": tile.get("ageDays"),
                        "bucket": tile.get("bucket") or "denied",
                        "billedAmount": tile.get("billedAmount"),
                    }
                )
        seen: set[Any] = set()
        deduped: list[dict[str, Any]] = []
        for s in seeds:
            cid = s.get("claimId")
            if cid and cid not in seen:
                seen.add(cid)
                deduped.append(s)
        seeds = deduped[:40]
    except Exception:
        seeds = []

    try:
        from nr2_local_db import list_collection_notes

        notes = list_collection_notes(limit=100)
        if not isinstance(notes, list):
            notes = []
    except Exception:
        notes = []

    has_data = bool(seeds) or bool(notes)
    return {
        "id": "ar-collection-task-list",
        "type": "collection-task-list",
        "label": "Collections Workbench",
        "size": "full",
        "status": "ok" if has_data else "empty",
        "emptyMessage": "No aged claims or local notes — import SoftDent A/R and claims to populate.",
        "seeds": seeds,
        "notes": notes,
        "hint": "Seeds from 30/60/90+ buckets and denied claims. PHI = initials only.",
    }


def build_narratives_ai_insight(bundle: dict[str, Any]) -> dict[str, Any]:
    """Narratives page ai-insight — rule-backed variance; no invented $."""
    state = _load_local_json("nr2:v2:narratives") or {}
    drafts = state.get("drafts") if isinstance(state.get("drafts"), list) else []
    draft_text = str(state.get("draftText") or "").strip()
    clinical = _section_rows(bundle, "softdent", "clinicalNotes") or []

    draft_count = len(drafts) + (1 if draft_text else 0)
    clinical_count = len(clinical)

    if draft_count == 0 and clinical_count > 0:
        explanation = f"{clinical_count} clinical note(s) available but no narrative drafts started."
        widget_type = "alert-banner"
        cta_label = "Start draft from clinical notes"
        cta_route = "narratives"
        data: dict[str, Any] = {"severity": "info", "message": explanation}
    elif draft_count > 0 and clinical_count == 0:
        explanation = f"{draft_count} draft(s) saved without recent clinical notes import."
        widget_type = "alert-banner"
        cta_label = "Import SoftDent clinical notes"
        cta_route = "softdent"
        data = {"severity": "warning", "message": explanation}
    elif draft_count > 0 and clinical_count > 0:
        explanation = f"Workflow active: {draft_count} draft(s), {clinical_count} note(s) available."
        widget_type = "kpi-card"
        cta_label = "Review drafts"
        cta_route = "narratives"
        data = {
            "value": draft_count,
            "unit": "count",
            "trend_direction": f"{clinical_count} notes",
        }
    else:
        explanation = "No narrative drafts or clinical notes found."
        widget_type = "alert-banner"
        cta_label = "Import clinical data"
        cta_route = "softdent"
        data = {"severity": "info", "message": explanation}

    insight = {
        "widget_type": widget_type,
        "confidence": "high",
        "explanation": explanation,
        "source_refs": ["nr2:v2:narratives", "softdent:clinicalNotes"],
        "data": data,
        "action_cta": {"label": cta_label, "route": cta_route},
    }

    return {
        "id": "narratives-ai-insight",
        "type": "ai-insight",
        "label": "Narrative Insight",
        "size": "l",
        "status": "ok",
        "insight": insight,
        "hint": "Rule-backed variance (no LLM). source_refs required for audit.",
    }


def build_softdent_patient_dossier(bundle: dict[str, Any]) -> dict[str, Any]:
    """SoftDent page patient-dossier-card — honest empty until patient selected."""
    empty_msg = "Select a patient from the schedule (Mon–Thu) to load dossier."
    selected = (
        bundle.get("selectedPatient") if isinstance(bundle.get("selectedPatient"), dict) else None
    )
    if selected:
        demo = selected.get("demographics") if isinstance(selected.get("demographics"), dict) else {}
        payload = {
            "patientHash": selected.get("patientHash") or demo.get("nameHash") or "——",
            "initials": selected.get("initials") or demo.get("initials") or "P—",
            "primaryCarrier": selected.get("primaryCarrier") or demo.get("primaryCarrier"),
            "openClaims": selected.get("openClaims"),
            "lastVisit": selected.get("lastVisit") or demo.get("lastVisit") or "unknown",
            "accountBalance": selected.get("accountBalance") or "unavailable",
            "hasClinicalNotes": selected.get("hasClinicalNotes"),
            "emptyMessage": None,
        }
        st = "ok"
    else:
        # Live FE: empty message shows when status=empty and patientHash falsy
        payload = {
            "patientHash": None,
            "initials": None,
            "primaryCarrier": None,
            "openClaims": None,
            "lastVisit": None,
            "accountBalance": None,
            "hasClinicalNotes": None,
            "emptyMessage": empty_msg,
        }
        st = "empty"

    return {
        "id": "softdent-patient-dossier",
        "type": "patient-dossier-card",
        "label": "Patient Dossier",
        "size": "l",
        "status": st,
        "data": payload,
        "hint": "PHI-safe hashes/initials · empty until patient selected.",
    }


# ---------------------------------------------------------------------------
# Moonshot NEXT after TXN XLS ingest — TXN ledger surface (hal-10569)
# Read-only data-table from SoftDentFinancialExports/tx_parsed JSONL
# ---------------------------------------------------------------------------

_LEDGER_COLUMNS = ["Date", "Account", "Patient", "Provider", "Procedure", "Amount", "Flag"]


def build_transaction_ledger_table(
    bundle: dict[str, Any] | None = None,
    *,
    page: str = "softdent",
    account_num: str | int | None = None,
    patient_name: str | None = None,
    date_range: Any = None,
    limit: int = 40,
) -> dict[str, Any]:
    """
    TXN ledger data-table for SoftDent / Office Manager.
    Source: tx_parsed JSONL (read-only). empty ≠ $0.
    """
    del bundle  # reserved; ledger is file-backed, not import-bundle
    try:
        from softdent_transaction_extract import query_account_transactions
    except Exception:
        return {
            "id": f"{page}-transaction-ledger",
            "type": "data-table",
            "label": "Account Transaction Ledger",
            "size": "full",
            "status": "empty",
            "emptyMessage": "Transaction extract unavailable.",
            "columns": list(_LEDGER_COLUMNS),
            "rows": [],
            "hint": "SoftDent TXN Excel ingest required.",
        }

    # Default mosaic: recent rows (no filter). Filtered when account/patient/date set.
    filtered = any(
        [
            account_num not in (None, ""),
            str(patient_name or "").strip(),
            date_range not in (None, ""),
        ]
    )
    result = query_account_transactions(
        account_num=account_num if filtered else None,
        patient_name=patient_name if filtered else None,
        date_range=date_range if filtered else None,
        limit=max(1, int(limit)),
    )

    if not result.get("ok") and result.get("reason") == "data not yet exported":
        return {
            "id": f"{page}-transaction-ledger",
            "type": "data-table",
            "label": "Account Transaction Ledger",
            "size": "full",
            "status": "empty",
            "emptyMessage": "No transactions found — ingest SoftDent Trans-for-Period Excel first.",
            "columns": list(_LEDGER_COLUMNS),
            "rows": [],
            "emptyState": True,
            "hint": r"Pull TXN*.xls → C:\SoftDentReportExports then ingest to tx_parsed\.",
        }

    matches = list(result.get("matches") or [])
    if not filtered and matches:
        # Unfiltered mosaic: newest-first sample already limited by query
        pass
    elif filtered and not matches:
        return {
            "id": f"{page}-transaction-ledger",
            "type": "data-table",
            "label": "Account Transaction Ledger",
            "size": "full",
            "status": "empty",
            "emptyMessage": "No transactions found",
            "columns": list(_LEDGER_COLUMNS),
            "rows": [],
            "emptyState": True,
            "hint": "No matching rows for the requested account/patient/date filter.",
            "filters": result.get("filters") or {},
        }

    rows: list[dict[str, Any]] = []
    for rec in matches:
        amt = rec.get("amount")
        rows.append(
            {
                "Date": rec.get("date") or "-",
                "Account": rec.get("account_num") or "-",
                "Patient": (rec.get("patient_name") or "").strip() or "-",
                "Provider": rec.get("provider") or "-",
                "Procedure": rec.get("procedure") or "-",
                # Keep null as null so FE shows empty (never invent $0)
                "Amount": amt if isinstance(amt, (int, float)) else None,
                "Flag": rec.get("note_flag") or "",
            }
        )

    hint = (
        f"{len(rows)} row(s) from SoftDent TXN Excel JSONL (read-only; empty != $0)."
        if rows
        else "No transactions found."
    )
    if filtered:
        hint += f" Filters: {result.get('filters') or {}}."

    return {
        "id": f"{page}-transaction-ledger",
        "type": "data-table",
        "label": "Account Transaction Ledger",
        "size": "full",
        "status": "ok" if rows else "empty",
        "emptyMessage": "No transactions found",
        "columns": list(_LEDGER_COLUMNS),
        "rows": rows,
        "emptyState": not bool(rows),
        "hint": hint,
        "filters": result.get("filters") or {},
        "matchCount": int(result.get("matchCount") or len(rows)),
    }
