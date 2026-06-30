"""Public web research for HAL — practice operations reference (sanitized, no PHI)."""

from __future__ import annotations

import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html import unescape
from typing import Any

USER_AGENT = "NewRidgeFinancial-HAL-Research/1.0"
MAX_QUERY_LEN = 320
MAX_RESULTS = 8
TIMEOUT_SEC = 25

# Do not send patient identifiers, amounts, or account numbers to the web.
_BLOCKED_PATTERNS = (
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"\b\d{9,}\b"),
    re.compile(r"\$\s?\d"),
    re.compile(r"\bpatient\b", re.I),
    re.compile(r"\bmember\s*id\b", re.I),
    re.compile(r"\bdate\s+of\s+birth\b", re.I),
    re.compile(r"\bdob\b", re.I),
)

_RESULT_LINK_RE = re.compile(
    r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
    re.I | re.S,
)
_RESULT_SNIPPET_RE = re.compile(
    r'class="result__snippet"[^>]*>(.*?)</(?:a|td|div)>',
    re.I | re.S,
)
_TAG_RE = re.compile(r"<[^>]+>")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _strip_tags(html: str) -> str:
    return unescape(_TAG_RE.sub(" ", html or "")).strip()


def sanitize_query(query: str) -> tuple[str, list[str]]:
    text = " ".join((query or "").split())
    warnings: list[str] = []
    if not text:
        return "", warnings
    for pattern in _BLOCKED_PATTERNS:
        if pattern.search(text):
            warnings.append("Removed sensitive or patient-specific terms before web lookup.")
            text = pattern.sub(" ", text)
    text = " ".join(text.split())
    if len(text) > MAX_QUERY_LEN:
        text = text[:MAX_QUERY_LEN].rstrip()
        warnings.append("Query truncated for web lookup.")
    return text, warnings


def enrich_query(query: str) -> str:
    """Add light domain context without over-narrowing every lookup to accounting."""
    lower = query.lower()
    parts = [query]
    hints: list[str] = []

    if any(token in lower for token in ("claim", "insurance", "payer", "denial", "narrative", "eob", "era", "prior auth")):
        hints.append("dental insurance billing")
    if any(token in lower for token in ("softdent", "carestream", "sensei", "dentrix", "eaglesoft", "open dental")):
        hints.append("dental practice management software")
    if "quickbooks" in lower:
        hints.append("dental practice bookkeeping")
    if any(token in lower for token in ("hipaa", "osha", "compliance", "regulation")):
        hints.append("dental office compliance")
    if any(token in lower for token in ("cdt", "procedure code", "coding", "fee schedule")):
        hints.append("dental procedure coding")
    if any(token in lower for token in ("staff", "hygienist", "scheduling", "front desk", "hiring")):
        hints.append("dental office operations")
    if any(
        token in lower
        for token in (
            "accounting",
            "reconcil",
            "production",
            "collections",
            "daysheet",
            "ebitda",
            "p&l",
            "profit",
            "ledger",
            "month-end",
            "month end",
            "close",
            "a/r",
            "receivable",
            "cash basis",
            "accrual",
        )
    ):
        if "softdent" in lower and "quickbooks" not in lower:
            hints.append("QuickBooks reconciliation")
        elif "quickbooks" in lower and "softdent" not in lower:
            hints.append("SoftDent production collections")
        hints.append("dental practice accounting")

    practice_markers = (
        "dental",
        "practice",
        "clinic",
        "ortho",
        "hygiene",
        "dentist",
        "office manager",
    )
    if hints and not any(marker in lower for marker in practice_markers):
        hints.append("dental practice")

    for hint in hints:
        if hint.lower() not in lower:
            parts.append(hint)

    return " ".join(dict.fromkeys(" ".join(parts).split()))


def enrich_accounting_query(query: str) -> str:
    """Backward-compatible alias."""
    return enrich_query(query)


def _parse_duckduckgo_html(html: str, limit: int) -> list[dict[str, str]]:
    links = _RESULT_LINK_RE.findall(html)
    snippets = _RESULT_SNIPPET_RE.findall(html)
    results: list[dict[str, str]] = []
    for idx, (url, title_html) in enumerate(links):
        if len(results) >= limit:
            break
        title = _strip_tags(title_html)
        snippet = _strip_tags(snippets[idx]) if idx < len(snippets) else ""
        if not title:
            continue
        results.append({"title": title, "snippet": snippet, "url": unescape(url)})
    return results


def research(query: str, *, max_results: int = MAX_RESULTS, enrich: bool = True) -> dict[str, Any]:
    safe, warnings = sanitize_query(query)
    if not safe:
        return {
            "ok": False,
            "error": "empty_or_blocked_query",
            "query": "",
            "results": [],
            "warnings": warnings,
            "fetchedAt": _utc_now(),
            "policy": "public_docs_only_no_phi",
        }

    lookup = enrich_query(safe) if enrich else safe
    limit = max(1, min(int(max_results or MAX_RESULTS), MAX_RESULTS))
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(lookup)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SEC) as response:
            html = response.read().decode("utf-8", errors="replace")
        results = _parse_duckduckgo_html(html, limit)
        return {
            "ok": bool(results),
            "query": lookup,
            "originalQuery": safe,
            "results": results,
            "warnings": warnings,
            "fetchedAt": _utc_now(),
            "policy": "public_docs_only_no_phi",
            "source": "duckduckgo_html",
        }
    except urllib.error.URLError as exc:
        return {
            "ok": False,
            "error": str(exc.reason if hasattr(exc, "reason") else exc),
            "query": lookup,
            "originalQuery": safe,
            "results": [],
            "warnings": warnings,
            "fetchedAt": _utc_now(),
            "policy": "public_docs_only_no_phi",
        }
