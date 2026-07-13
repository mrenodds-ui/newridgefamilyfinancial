"""SoftDent full product knowledge base — program-readable + HAL formatter.

Built from Carestream SoftDent Online Help (OH_DE1010 CHM) via
`scripts/build_softdent_product_kb.py` + office doctrine / NR2 automation ids.

Automation subsets remain authoritative in:
  - softdent_gui_menu_map.json
  - softdent_master_reports.json
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

KB_PATH = Path(__file__).resolve().parent / "softdent_product_kb.json"


@lru_cache(maxsize=1)
def load_softdent_product_kb(path: str | None = None) -> dict[str, Any]:
    target = Path(path) if path else KB_PATH
    if not target.is_file():
        raise FileNotFoundError(f"SoftDent product KB missing: {target}")
    return json.loads(target.read_text(encoding="utf-8-sig"))


def clear_softdent_product_kb_cache() -> None:
    load_softdent_product_kb.cache_clear()


def product_kb_summary() -> dict[str, Any]:
    kb = load_softdent_product_kb()
    cats = (kb.get("reportCatalog") or {}).get("categories") or {}
    cat_counts = {
        name: int((meta or {}).get("reportCount") or 0)
        for name, meta in cats.items()
        if name != "overview" and isinstance(meta, dict)
    }
    return {
        "version": kb.get("version"),
        "built": kb.get("built"),
        "tocEntryCount": ((kb.get("helpToc") or {}).get("entryCount")),
        "reportCountParsed": ((kb.get("reportCatalog") or {}).get("reportCountParsed")),
        "categoryCounts": cat_counts,
        "moduleCount": len(kb.get("productModules") or []),
        "guiExportIds": list(((kb.get("nr2Automation") or {}).get("guiExportIds") or [])),
        "helpUrlBase": kb.get("helpUrlBase"),
        "localHelpChm": ((kb.get("officeDoctrine") or {}).get("localHelpChm")),
    }


def lookup_report(query: str, *, limit: int = 12) -> list[dict[str, Any]]:
    """Keyword match against Help report catalog (name + description)."""
    q = str(query or "").strip().lower()
    if not q:
        return []
    tokens = [t for t in re.split(r"[^a-z0-9]+", q) if len(t) >= 3]
    if not tokens:
        tokens = [q]
    kb = load_softdent_product_kb()
    scored: list[tuple[int, dict[str, Any]]] = []
    for rep in (kb.get("reportCatalog") or {}).get("allReports") or []:
        blob = f"{rep.get('name','')} {rep.get('description','')} {rep.get('category','')}".lower()
        score = sum(1 for t in tokens if t in blob)
        if score:
            if rep.get("nr2GuiId"):
                score += 2
            scored.append((score, rep))
    scored.sort(key=lambda x: (-x[0], str(x[1].get("name") or "")))
    return [r for _, r in scored[: max(1, int(limit))]]


def lookup_help_topics(query: str, *, limit: int = 15) -> list[dict[str, Any]]:
    """Keyword match against SoftDent Online Help TOC."""
    q = str(query or "").strip().lower()
    if not q:
        return []
    tokens = [t for t in re.split(r"[^a-z0-9]+", q) if len(t) >= 3]
    if not tokens:
        tokens = [q]
    kb = load_softdent_product_kb()
    scored: list[tuple[int, dict[str, Any]]] = []
    for ent in (kb.get("helpToc") or {}).get("entries") or []:
        name = str(ent.get("name") or "")
        blob = name.lower()
        score = sum(1 for t in tokens if t in blob)
        if score:
            scored.append((score, ent))
    scored.sort(key=lambda x: (-x[0], str(x[1].get("name") or "")))
    return [e for _, e in scored[: max(1, int(limit))]]


def format_softdent_product_kb_hal_reply(query: str = "") -> str:
    """Compact HAL reply: product map + matching reports/topics for the query."""
    kb = load_softdent_product_kb()
    doctrine = kb.get("officeDoctrine") or {}
    summary = product_kb_summary()
    modules = kb.get("productModules") or []
    cat_bits = ", ".join(
        f"{name} ({n})" for name, n in (summary.get("categoryCounts") or {}).items() if n
    )
    lines = [
        "SOFTDENT FULL PRODUCT KB (Carestream SoftDent Online Help OH_DE1010 + this office):",
        f"Build {doctrine.get('practiceBuild') or 'SoftDent desktop'}.",
        f"Help TOC topics indexed: {summary.get('tocEntryCount')}; "
        f"report rows cataloged: {summary.get('reportCountParsed')} across thirteen Reports menu categories"
        + (f" [{cat_bits}]." if cat_bits else "."),
        "Product modules: "
        + "; ".join(str(m.get("label") or m.get("id")) for m in modules)
        + ".",
        "Output Options doctrine: Excel or Print Preview only — never Printer; empty ≠ $0; "
        "period-close $ from desktop Excel; ops detail may use Sensei/sd_*/ODBC.",
        f"In SoftDent press F1 / Help → SoftDent Help. Local CHM: {doctrine.get('localHelpChm')}. "
        f"Online: {kb.get('helpUrlBase')}. Support: {doctrine.get('supportPortal')}.",
        "NR2 automates a subset (softdent_gui_menu_map.json / softdent_master_reports.json) — "
        "full product ≠ full automation.",
    ]
    q = str(query or "").strip()
    if q:
        hits = lookup_report(q, limit=8)
        if hits:
            lines.append("Matching SoftDent reports:")
            for h in hits:
                nr2 = f" [NR2 gui:{h.get('nr2GuiId')}]" if h.get("nr2GuiId") else ""
                lines.append(
                    f"- {h.get('category')}: {h.get('name')} — "
                    f"{(h.get('description') or '')[:160]}{nr2}"
                )
        topics = lookup_help_topics(q, limit=8)
        if topics:
            lines.append("Matching SoftDent Help TOC topics:")
            for t in topics:
                url = t.get("helpUrl") or t.get("local") or ""
                lines.append(f"- {t.get('name')}" + (f" → {url}" if url else ""))
        if not hits and not topics:
            lines.append(
                "No specific report/TOC keyword hit — ask for a SoftDent menu/report name "
                "(e.g. Daysheet, Account Aging, Charting, ERA) or open F1 Help."
            )
    keys = kb.get("keystrokes") or {}
    if keys:
        key_bits = ", ".join(f"{k}={v}" for k, v in list(keys.items())[:8])
        lines.append(f"Keystrokes: {key_bits}.")
    return " ".join(lines)


def query_touches_softdent_product(query: str) -> bool:
    """True when the user asks about SoftDent product features / Help / full menus."""
    q = str(query or "").lower()
    if re.search(
        r"\b("
        r"softdent\s+(product|help|manual|feature|module|menu|toc|everything|entire|reports?|catalog)|"
        r"(learn|what\s+is|how\s+does|tell\s+me\s+about|describe)\s+(the\s+)?softdent|"
        r"soft\s*dent\s+(charting|scheduling|treatment\s*plan|era|eclaim|e-?claim|"
        r"imaging|report\s*manager|audit\s*trail|trojan|kiosk|voice|practice\s+management)|"
        r"(list|all)\s+(softdent\s+)?(reports|menus|modules|features)|"
        r"carestream\s+(softdent|help)|"
        r"thirteen\s+categor|"
        r"over\s+200\s+reports|"
        r"help\s*→\s*softdent|soft\s*dent\s+help|f1\s+softdent|"
        r"softdent\s+help\s+catalog|product\s+help\s+catalog"
        r")\b",
        q,
    ):
        return True
    if "softdent" in q and re.search(
        r"\b(charting|treatment plan|report manager|audit trail|trojan|"
        r"practice (summary|management)|receivables|capitation|ortho|lab case|"
        r"what (can|does) softdent|full (product|manual|catalog)|help catalog|"
        r"report(s)? (are|in|exist|available))\b",
        q,
    ):
        return True
    return False


def format_softdent_product_kb_brief() -> str:
    s = product_kb_summary()
    return (
        f"SoftDent product KB v{s.get('version')} ({s.get('built')}): "
        f"{s.get('tocEntryCount')} Help TOC topics, "
        f"{s.get('reportCountParsed')} cataloged reports, "
        f"{s.get('moduleCount')} product modules. "
        "Load via softdent_product_kb /api/apex/hal/softdent-kb."
    )


if __name__ == "__main__":
    import sys

    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Account Aging"
    print(format_softdent_product_kb_brief())
    print(format_softdent_product_kb_hal_reply(q))
