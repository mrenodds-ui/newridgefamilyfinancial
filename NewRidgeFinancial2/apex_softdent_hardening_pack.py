"""
Phase I2 — SoftDent Collections/Daysheet honesty (DEF-001).

Centralizes collections-gap detection so widgets, import health, and HAL
share one gap code — never invent collections dollars.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

# Stable gap codes for UI / HAL / tests
GAP_OK = "OK"
GAP_COLLECTIONS_PENDING = "COLLECTIONS_PENDING"
GAP_COLLECTIONS_UNREPORTED = "COLLECTIONS_UNREPORTED"  # reported=false (past period)
GAP_DAYSHEET_ZERO = "COLLECTIONS_ZERO_ON_DAYSHEET"
GAP_REGISTER_ONLY = "REGISTER_ONLY"  # production without collections key
GAP_NO_PERIOD = "NO_PERIOD_ROW"
GAP_COLLECTIONS_FORMAT_REQUIRED = "COLLECTIONS_FORMAT_REQUIRED"  # files present but wrong period/split
GAP_DAYSHEET_WITHOUT_SPLIT = "DAYSHEET_WITHOUT_SPLIT"  # period from daysheet; Collections export needed
GAP_COLLECTIONS_EXPORT_REQUIRED = "COLLECTIONS_EXPORT_REQUIRED"  # ops synonym for format/split gap

FIX_HINT = (
    "Import SoftDent daysheet / complete Register for a Period, then Sync "
    "(or ask HAL: refresh SoftDent period). Empty ≠ $0."
)
FORMAT_HINT = (
    "Inbox has DaySheet/Collections-named files, but they are not a usable "
    "insurance/patient split for the open period. Export SoftDent → Reports → "
    "Accounting → Register for a Period (open month) or Collections/Daysheet "
    r"with a real Ins/Patient split to C:\SoftDentReportExports, then Sync. Empty ≠ $0."
)
SPLIT_HINT = (
    "Collections export required for ins/patient split. SoftDent → Reports → "
    "Accounting → Collections (or Register for a Period with Ins Plan / Regular "
    r"Collections) → C:\SoftDentReportExports, then Sync. Empty ≠ $0."
)

# SoftDent export inbox roots (same family as import_sync upstream)
_EXPORT_INBOX_CANDIDATES = (
    r"C:\SoftDentReportExports",
    r"C:\SoftDent\softdentexportreports",
    r"C:\SoftDentFinancialExports",
)

_COLLECTIONS_NAME_RE = re.compile(
    r"(?i)(collections|daysheet|register.?for.?(?:a.?)?period|col[_-]?\d{6})",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def scan_collections_export_inbox(*, limit: int = 12) -> dict[str, Any]:
    """List recent Collections/Daysheet/Register files in SoftDent export folders.

    Does not invent dollars — only filesystem presence for DEF-001 ops guidance.
    """
    import os
    from pathlib import Path

    roots: list[Path] = []
    for env_key in ("SOFTDENT_REPORT_EXPORTS", "NR2_SOFTDENT_EXPORT_SOURCE"):
        raw = str(os.environ.get(env_key) or "").strip()
        if raw:
            roots.append(Path(raw))
    for cand in _EXPORT_INBOX_CANDIDATES:
        roots.append(Path(cand))

    seen: set[str] = set()
    matches: list[dict[str, Any]] = []
    scanned_roots: list[str] = []
    for root in roots:
        try:
            resolved = str(root.resolve()) if root.exists() else str(root)
        except OSError:
            resolved = str(root)
        if resolved in seen:
            continue
        seen.add(resolved)
        if not root.is_dir():
            scanned_roots.append(f"{resolved} (missing)")
            continue
        scanned_roots.append(resolved)
        try:
            files = sorted(
                [p for p in root.iterdir() if p.is_file()],
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
        except OSError:
            continue
        for path in files[:80]:
            name = path.name
            if not _COLLECTIONS_NAME_RE.search(name):
                continue
            try:
                st = path.stat()
                mtime = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat()
                size = int(st.st_size)
            except OSError:
                mtime = None
                size = None
            matches.append(
                {
                    "name": name,
                    "path": str(path),
                    "mtime": mtime,
                    "sizeBytes": size,
                    "kind": (
                        "collections"
                        if re.search(r"(?i)collections", name)
                        else "daysheet"
                        if re.search(r"(?i)daysheet", name)
                        else "register"
                    ),
                }
            )
            if len(matches) >= max(1, int(limit)):
                break
        if len(matches) >= max(1, int(limit)):
            break

    return {
        "ok": True,
        "roots": scanned_roots,
        "matches": matches,
        "matchCount": len(matches),
        "hasCollectionsLikeFile": any(m.get("kind") == "collections" for m in matches),
        "hasDaysheetLikeFile": any(m.get("kind") == "daysheet" for m in matches),
        "hasRegisterLikeFile": any(m.get("kind") == "register" for m in matches),
        "hint": (
            "Export SoftDent Collections/Daysheet (Reports → Accounting) to "
            r"C:\SoftDentReportExports as CSV, then Sync / Refresh SoftDent period."
            if not matches
            else "Matching export file(s) found — Sync / Refresh SoftDent period if dashboard still pending."
        ),
        "checkedAt": _utc_now(),
    }


def _latest_period_from_bundle(bundle: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(bundle, dict):
        return None
    try:
        from apex_backend import _dashboard_rows, _latest_period_row

        return _latest_period_row(_dashboard_rows(bundle))
    except Exception:
        softdent = bundle.get("softdent") if isinstance(bundle.get("softdent"), dict) else {}
        dash = softdent.get("dashboard") if isinstance(softdent.get("dashboard"), dict) else {}
        rows = dash.get("rows") if isinstance(dash.get("rows"), list) else []
        for row in reversed(rows):
            if isinstance(row, dict) and (row.get("period") or row.get("year_month")):
                return row
        return None


def classify_daysheet_inbox_periods(matches: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Best-effort period labels from daysheet CSV/JSONL names and content (no $ invent)."""
    from pathlib import Path

    items = matches if isinstance(matches, list) else []
    periods: list[str] = []
    notes: list[str] = []
    for item in items[:8]:
        if not isinstance(item, dict):
            continue
        path = Path(str(item.get("path") or ""))
        name = str(item.get("name") or path.name)
        found: set[str] = set()
        for m in re.finditer(r"(20\d{2})[-_/]?(\d{2})", name):
            found.add(f"{m.group(1)}-{m.group(2)}")
        if path.is_file() and path.suffix.lower() in {".csv", ".jsonl", ".txt"}:
            try:
                text = path.read_text(encoding="utf-8-sig", errors="ignore")[:8000]
            except OSError:
                text = ""
            for m in re.finditer(
                r"(?i)\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
                r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|"
                r"Dec(?:ember)?)\s+(\d{1,2}),?\s+(20\d{2})\b",
                text,
            ):
                mon = {
                    "jan": "01",
                    "january": "01",
                    "feb": "02",
                    "february": "02",
                    "mar": "03",
                    "march": "03",
                    "apr": "04",
                    "april": "04",
                    "may": "05",
                    "jun": "06",
                    "june": "06",
                    "jul": "07",
                    "july": "07",
                    "aug": "08",
                    "august": "08",
                    "sep": "09",
                    "sept": "09",
                    "september": "09",
                    "oct": "10",
                    "october": "10",
                    "nov": "11",
                    "november": "11",
                    "dec": "12",
                    "december": "12",
                }.get(m.group(1).lower())
                if mon:
                    found.add(f"{m.group(3)}-{mon}")
            for m in re.finditer(r"\b(20\d{2})[-/](\d{2})[-/](\d{2})\b", text):
                found.add(f"{m.group(1)}-{m.group(2)}")
            for m in re.finditer(r"\b(\d{1,2})/(\d{1,2})/(20\d{2})\b", text):
                found.add(f"{m.group(3)}-{int(m.group(1)):02d}")
        if found:
            periods.extend(sorted(found))
            notes.append(f"{name}: periods={','.join(sorted(found))}")
        else:
            notes.append(f"{name}: period unknown (DaySheet presence ≠ open-month Collections)")
    return {"periods": sorted(set(periods)), "notes": notes[:8]}


def assess_collections_gap(bundle: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Single source of truth for DEF-001 Collections/Daysheet gap.

    Returns gapCode, period, flags, fixHint, issues[] — never invents $.
    """
    latest = _latest_period_from_bundle(bundle)
    period = str((latest or {}).get("period") or (latest or {}).get("year_month") or "") or None
    issues: list[str] = []
    gap = GAP_NO_PERIOD
    pending = False
    reported: bool | None = None
    has_collections_key = False
    format_required = False
    daysheet_without_split = False
    production = None
    collections = None

    if latest:
        pending = bool(latest.get("collectionsPending"))
        format_required = bool(latest.get("collectionsFormatRequired"))
        daysheet_without_split = bool(latest.get("daysheetWithoutSplit"))
        if "collectionsReported" in latest:
            reported = bool(latest.get("collectionsReported"))
        has_collections_key = "collections" in latest
        try:
            production = float(latest.get("production")) if latest.get("production") is not None else None
        except (TypeError, ValueError):
            production = None
        try:
            collections = float(latest.get("collections")) if has_collections_key else None
        except (TypeError, ValueError):
            collections = None
        try:
            ins = float(latest.get("insurance") or 0)
        except (TypeError, ValueError):
            ins = 0.0
        try:
            pat = float(latest.get("patient") or 0)
        except (TypeError, ValueError):
            pat = 0.0
        if (
            has_collections_key
            and collections
            and collections > 0
            and ins <= 0
            and pat > 0
            and abs(pat - collections) < 0.02
        ):
            format_required = True

        if daysheet_without_split and pending:
            gap = GAP_DAYSHEET_WITHOUT_SPLIT
            issues.append(
                f"{period or 'latest'}: daysheetWithoutSplit — period row from daysheet "
                "but Collections export required for ins/patient split."
            )
        elif format_required and not pending:
            gap = GAP_COLLECTIONS_FORMAT_REQUIRED
            issues.append(
                f"{period or 'latest'}: collections total may exist but insurance/patient split "
                "is missing or all-patient dump — Collections format required."
            )
        elif pending:
            gap = GAP_COLLECTIONS_PENDING
            issues.append(
                f"{period or 'latest'}: collectionsPending — daysheet/collections not reported for this period."
            )
        elif reported is False:
            gap = GAP_COLLECTIONS_UNREPORTED
            issues.append(
                f"{period or 'latest'}: collectionsReported=false — SoftDent closed period without collections."
            )
        elif production and production > 0 and not has_collections_key:
            gap = GAP_REGISTER_ONLY
            issues.append(
                f"{period or 'latest'}: production present without collections key (register-only view)."
            )
        elif (
            has_collections_key
            and collections is not None
            and collections <= 0
            and production
            and production > 0
        ):
            gap = GAP_DAYSHEET_ZERO
            issues.append(
                f"{period or 'latest'}: daysheet/collections present but collections are zero — rerun final daysheet."
            )
        else:
            gap = GAP_OK

    # Optional analytics-db diagnosis (extra issues; does not override gap from bundle)
    try:
        from softdent_dashboard_period_sync import diagnose_collections_gap, resolve_analytics_db

        diag = diagnose_collections_gap(resolve_analytics_db())
        for issue in (diag.get("issues") or [])[:8]:
            if issue not in issues:
                issues.append(str(issue))
    except Exception:
        pass

    healthy = gap == GAP_OK
    export_required = gap in {
        GAP_COLLECTIONS_FORMAT_REQUIRED,
        GAP_DAYSHEET_WITHOUT_SPLIT,
        GAP_COLLECTIONS_EXPORT_REQUIRED,
    } or format_required or daysheet_without_split
    if export_required and gap == GAP_COLLECTIONS_PENDING and daysheet_without_split:
        gap = GAP_DAYSHEET_WITHOUT_SPLIT
    fix_hint = None
    if not healthy:
        if gap == GAP_DAYSHEET_WITHOUT_SPLIT or daysheet_without_split:
            fix_hint = SPLIT_HINT
        elif format_required or gap == GAP_COLLECTIONS_FORMAT_REQUIRED:
            fix_hint = FORMAT_HINT
        else:
            fix_hint = FIX_HINT
    result = {
        "ok": True,
        "gapCode": gap,
        "collectionsGapCode": (
            GAP_COLLECTIONS_EXPORT_REQUIRED
            if export_required and gap != GAP_OK
            else gap
        ),  # SoftDent daysheet code before ERA enrich
        "healthy": healthy,
        "period": period,
        "collectionsPending": pending,
        "collectionsReported": reported,
        "collectionsFormatRequired": format_required or gap == GAP_COLLECTIONS_FORMAT_REQUIRED,
        "daysheetWithoutSplit": daysheet_without_split or gap == GAP_DAYSHEET_WITHOUT_SPLIT,
        "collectionsExportRequired": export_required and gap != GAP_OK,
        "hasCollectionsKey": has_collections_key,
        "production": production,
        "collections": collections if gap == GAP_OK else None,  # never surface unverified $ as truth
        "honesty": "empty_not_zero" if not healthy else "reported",
        "fixHint": fix_hint,
        "issues": issues[:12],
        "def": "DEF-001",
        "checkedAt": _utc_now(),
    }
    # Ops inbox scan — file presence + period classify; never invents dollars
    try:
        inbox = scan_collections_export_inbox()
        classified = classify_daysheet_inbox_periods(inbox.get("matches") or [])
        open_period = (period or datetime.now(timezone.utc).strftime("%Y-%m"))[:7]
        covers = open_period in set(classified.get("periods") or [])
        classified["coversOpenMonth"] = covers
        result["exportInbox"] = {
            "matchCount": inbox.get("matchCount"),
            "hasCollectionsLikeFile": inbox.get("hasCollectionsLikeFile"),
            "hasDaysheetLikeFile": inbox.get("hasDaysheetLikeFile"),
            "hasRegisterLikeFile": inbox.get("hasRegisterLikeFile"),
            "matches": (inbox.get("matches") or [])[:6],
            "hint": inbox.get("hint"),
            "roots": inbox.get("roots"),
            "classifiedPeriods": classified.get("periods"),
            "coversOpenMonth": covers,
            "classifyNotes": classified.get("notes"),
        }
        if not healthy and not inbox.get("matchCount"):
            issues.append("No Collections/Daysheet-named files in SoftDent export inbox.")
            result["issues"] = issues[:12]
            result["fixHint"] = (
                f"{FIX_HINT} Export inbox empty — drop Collections/Daysheet CSV into "
                r"C:\SoftDentReportExports, then Sync."
            )
        elif not healthy and inbox.get("matchCount"):
            names = ", ".join(str(m.get("name")) for m in (inbox.get("matches") or [])[:3] if m.get("name"))
            if not covers:
                # Files exist but do not cover open month → format/period required
                # Keep DAYSHEET_WITHOUT_SPLIT when the period row already signals that state.
                if result.get("gapCode") != GAP_DAYSHEET_WITHOUT_SPLIT:
                    result["gapCode"] = GAP_COLLECTIONS_FORMAT_REQUIRED
                    result["collectionsGapCode"] = GAP_COLLECTIONS_EXPORT_REQUIRED
                    result["collectionsFormatRequired"] = True
                    result["collectionsExportRequired"] = True
                    result["fixHint"] = FORMAT_HINT
                issues.append(
                    f"Export inbox has {names}, but classified periods "
                    f"{classified.get('periods') or []} do not cover open month {open_period}."
                )
                for note in (classified.get("notes") or [])[:3]:
                    issues.append(str(note))
            else:
                issues.append(
                    f"Export inbox has matching file(s) for {open_period}: {names}. "
                    "Refresh SoftDent period if dashboard still pending."
                )
            result["issues"] = issues[:12]
    except Exception:
        pass
    # Phase S1 — ERA aggregate proposal when collections still empty
    try:
        from apex_softdent_era_pack import enrich_collections_gap_with_era

        result = enrich_collections_gap_with_era(result)
    except Exception:
        pass
    return result


def collections_gap_widget(bundle: dict[str, Any] | None = None) -> dict[str, Any]:
    gap = assess_collections_gap(bundle)
    healthy = bool(gap.get("healthy"))
    code = str(gap.get("gapCode") or GAP_NO_PERIOD)
    period = gap.get("period") or "—"
    if healthy:
        return {
            "id": "softdent-collections-gap",
            "type": "status",
            "label": "Collections Gap (DEF-001)",
            "size": "full",
            "status": "ok",
            "message": f"Collections reported · {period}",
            "hint": "SoftDent period has reported collections — revenue split may populate.",
            "gapCode": code,
            "gap": gap,
        }
    return {
        "id": "softdent-collections-gap",
        "type": "status",
        "label": "Collections Gap (DEF-001)",
        "size": "full",
        "status": "empty",
        "message": f"{code} · {period}",
        "emptyMessage": code,
        "hint": gap.get("fixHint") or FIX_HINT,
        "gapCode": code,
        "gap": gap,
        "halChips": [
            {"label": "Collections gap", "query": "Why are collections empty?"},
            {"label": "Refresh SoftDent period", "query": "Refresh SoftDent period imports"},
            {"label": "Sync imports", "query": "Sync imports and populate the widgets"},
        ],
    }


def enrich_widget_with_collections_gap(widget: dict[str, Any], gap: dict[str, Any] | None) -> dict[str, Any]:
    """Stamp gapCode / fixHint onto empty collection-related widgets."""
    if not isinstance(widget, dict) or not isinstance(gap, dict):
        return widget
    if gap.get("healthy"):
        return widget
    out = dict(widget)
    if out.get("status") == "empty" or out.get("value") is None:
        out.setdefault("gapCode", gap.get("gapCode"))
        out.setdefault("def", "DEF-001")
        hint = str(out.get("hint") or "")
        fix = str(gap.get("fixHint") or FIX_HINT)
        if "daysheet" not in hint.lower() and "pending" not in hint.lower():
            out["hint"] = f"{hint} · {fix}".strip(" ·") if hint else fix
        out.setdefault("emptyMessage", out.get("emptyMessage") or str(gap.get("gapCode")))
    return out


def import_health_collections_alert(bundle: dict[str, Any] | None = None) -> dict[str, Any] | None:
    gap = assess_collections_gap(bundle)
    if gap.get("healthy"):
        return None
    return {
        "id": "def-001-collections-gap",
        "severity": "warn",
        "message": f"DEF-001 {gap.get('gapCode')}: SoftDent collections/daysheet gap ({gap.get('period') or 'latest'})",
        "hint": gap.get("fixHint") or FIX_HINT,
        "halQuery": "Why are collections empty?",
        "gapCode": gap.get("gapCode"),
        "pending": gap.get("issues") or [],
    }


def format_collections_gap_reply(gap: dict[str, Any] | None = None) -> str:
    g = gap if isinstance(gap, dict) else {}
    if g.get("healthy"):
        return (
            f"Collections look reported for period `{g.get('period') or 'latest'}` "
            f"(gapCode={g.get('gapCode')}). Revenue split can populate from import — not invented."
        )
    issues = g.get("issues") if isinstance(g.get("issues"), list) else []
    lines = [
        f"DEF-001 SoftDent collections gap: `{g.get('gapCode')}` · period `{g.get('period') or '—'}`.",
        f"collectionsGapCode=`{g.get('collectionsGapCode') or g.get('gapCode')}`.",
        "Honesty: empty Collections / revenue-composition is not $0.",
        str(g.get("fixHint") or FIX_HINT),
        "Ops: SoftDent → Reports → Accounting → Collections or Daysheet (or Register for a Period) "
        r"→ CSV to C:\SoftDentReportExports → Sync / ask HAL to refresh SoftDent period.",
    ]
    inbox = g.get("exportInbox") if isinstance(g.get("exportInbox"), dict) else {}
    if inbox:
        lines.append(
            f"Export inbox: {inbox.get('matchCount') or 0} Collections/Daysheet/Register-like file(s)."
        )
        if inbox.get("classifiedPeriods") is not None:
            lines.append(
                f"Classified file periods: {inbox.get('classifiedPeriods') or []} · "
                f"covers open month={inbox.get('coversOpenMonth')}."
            )
        hint = inbox.get("hint")
        if hint:
            lines.append(str(hint))
    for issue in issues[:5]:
        lines.append(f"- {issue}")
    return "\n".join(lines)
