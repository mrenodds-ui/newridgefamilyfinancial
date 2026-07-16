"""Moonshot AI — Optical pages too tall / must scroll; want high-executive
first-viewport polish even if schema/HTML structure must change.

CONSULT ONLY — operator: ask moonshot ai that the pages are too big and i have
to scroll, i want a highly polished executive look even if the schema has to
change. have him look at other financial pages and report
"""

from __future__ import annotations

import json
import os
import re
import ssl
import sys
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / ".local_logs" / "moonshot_financial_eval"
DOCS = REPO / "NewRidgeFinancial2" / "docs"
NR2 = REPO / "NewRidgeFinancial2"
SITE = NR2 / "site"
OUT.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)
DATE = datetime.now(timezone.utc).strftime("%Y-%m-%d")

CTX = ssl._create_unverified_context()
BASE = os.getenv("NR2_BROWSER", "https://127.0.0.1:8765").rstrip("/")

OPERATOR_REQUEST_VERBATIM = (
    "ask moonshot ai that the pages are too big and i have to scroll, i want a "
    "highly polished executive look even if the schema has to change. have him "
    "look at other financial pages and report"
)

SYSTEM = """You are Moonshot AI — principal visual/product designer for NewRidgeFinancial2 (NR2).
CONSULT ONLY — DO NOT APPLY CODE.

Operator said (verbatim): ask moonshot ai that the pages are too big and i have
to scroll, i want a highly polished executive look even if the schema has to
change. have him look at other financial pages and report

PROBLEM: Optical suite pages feel too tall — operator must scroll to see the
full executive desk. They want a HIGHLY POLISHED EXECUTIVE look that fits the
first viewport (or nearly) — SCHEMA / HTML structure MAY CHANGE if needed
(still static HTML+JS — NO React rewrite).

ALREADY SHIPPED (do not redo as new polish layers):
P1–P10 functional polish, V1–V6 instrument glass, E1–E4 high-executive
letterhead/currency/desk surface, Claims honesty, desk-smoke faces.

HARD CONSTRAINTS:
- SoftDent READ-ONLY; empty ≠ $0; PHI initials+hash
- No SoftDent write-back; no third-party chat embeds
- Static HTML+JS only — NO React/Vite rewrite
- Keep SD / QB / HAL tokens; avoid purple gradients, cream+terracotta, broadsheet
- Honesty / ops gates / Force Close must remain executive-visible (status LEDs)
- Prefer REAL NewRidgeFinancial2/site paths; never invent files

YOUR JOB:
1) Diagnose WHY pages force scroll (chrome stack: banner, letterhead, crumb,
   eyebrow, h1, kicker, beam, honesty, ledge/money-strip, ops bar, page body)
2) Compare optical pages vs OTHER financial surfaces in the audit (landing,
   hub, classic Apex/financial HTML if present) — which feel denser/boardroom
3) Page-by-page scroll risk score (1–5) with REAL files
4) Ordered packages to reach high-executive FIRST-VIEWPORT fit (schema change OK)
5) Pick THE single best FIRST package to apply now
6) Concrete HTML/CSS/JS moves — what to collapse, tab, sticky, or demote below fold

OUTPUT (strict markdown):
# Verdict (one sentence — THE next package)
## 0. Operator Intent (verbatim)
## 1. Why pages force scroll (stack diagnosis)
## 2. Cross-page comparison (optical vs other financial pages in audit)
## 3. Page-by-page scroll risk (table: page | score 1–5 | above-fold waste | REAL files)
## 4. Ordered packages (1..N) for high-executive first-viewport fit
Each: name, why, REAL files, concrete schema/CSS moves, effort S/M/L, validation gate
## 5. Recommended FIRST package (apply now)
## 6. What NOT to change
## 7. Anti-patterns (executive traps + AI-slop + fake density)
## 8. Acceptance criteria (first viewport / scroll budget)
## 9. Executive Summary (5 bullets)
## 10. Approval Checklist
DO NOT APPLY CODE. Never invent file paths.
"""


def _load_dotenv() -> None:
    for path in (REPO / ".env", NR2 / ".env"):
        if not path.is_file():
            continue
        try:
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                name, _, val = line.partition("=")
                name = name.strip()
                val = val.strip().strip("'").strip('"')
                if name and val and not os.getenv(name):
                    os.environ[name] = val
        except OSError:
            pass


def resolve_api_and_endpoint() -> tuple[str, str, str]:
    _load_dotenv()
    candidates = (
        ("MOONSHOT_API_KEY", os.getenv("MOONSHOT_API_KEY", "").strip()),
        ("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY", "").strip()),
        ("KIMI_K2_API_KEY", os.getenv("KIMI_K2_API_KEY", "").strip()),
    )
    key_name, api_key = "", ""
    for name, val in candidates:
        if val and len(val) >= 20:
            key_name, api_key = name, val
            break
    if not api_key:
        for name, val in candidates:
            if val:
                key_name, api_key = name, val
                break
    if (api_key or "").startswith("sk-nv") or key_name == "MOONSHOT_API_KEY":
        base = (
            os.getenv("MOONSHOT_API_BASE") or "https://api.moonshot.ai/v1/chat/completions"
        ).strip()
    elif key_name == "OPENROUTER_API_KEY":
        base = "https://openrouter.ai/api/v1/chat/completions"
    else:
        base = (
            os.getenv("MOONSHOT_API_BASE")
            or os.getenv("KIMI_K2_BASE_URL")
            or "https://openrouter.ai/api/v1/chat/completions"
        ).strip()
    if not base.endswith("/chat/completions"):
        base = base.rstrip("/") + "/chat/completions"
    return key_name, api_key, base


def extract_message_content(raw: dict) -> str:
    try:
        choices = raw.get("choices") or []
        if not choices:
            return ""
        msg = (choices[0] or {}).get("message") or {}
        content = msg.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    parts.append(str(block.get("text") or ""))
                elif isinstance(block, str):
                    parts.append(block)
            return "\n".join(p for p in parts if p)
        return str(content or "")
    except Exception:
        return ""


class _TagCounter(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: dict[str, int] = {}
        self.classes: dict[str, int] = {}
        self.h1 = 0
        self.sections = 0
        self.articles = 0
        self.buttons = 0
        self.tables = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        t = tag.lower()
        self.tags[t] = self.tags.get(t, 0) + 1
        if t == "h1":
            self.h1 += 1
        if t == "section":
            self.sections += 1
        if t == "article":
            self.articles += 1
        if t == "button":
            self.buttons += 1
        if t == "table":
            self.tables += 1
        attr = dict(attrs)
        cls = str(attr.get("class") or "")
        for c in cls.split():
            self.classes[c] = self.classes.get(c, 0) + 1


def _page_audit(path: Path) -> dict:
    if not path.is_file():
        return {"path": path.name, "exists": False}
    text = path.read_text(encoding="utf-8", errors="replace")
    parser = _TagCounter()
    try:
        parser.feed(text)
    except Exception as exc:  # noqa: BLE001
        return {"path": path.name, "exists": True, "parseError": str(exc)[:120]}
    markers = [
        "exec-letterhead",
        "exec-practice-header",
        "mode-eyebrow",
        "type-staff",
        "kicker",
        "honesty",
        "money-strip",
        "metric-face",
        "ledge",
        "atmosphere",
        "nr2-crumb",
        "banner",
        "ops-gates",
        "nr2-ops-gates",
        "shell",
        "main",
        "beam",
        "om-claims",
        "hal-cmd",
    ]
    hits = {m: (m in text) for m in markers}
    # rough chrome density heuristic
    chrome_hits = sum(
        1
        for k in (
            "exec-letterhead",
            "mode-eyebrow",
            "type-staff",
            "kicker",
            "honesty",
            "money-strip",
            "banner",
            "beam",
        )
        if hits.get(k)
    )
    return {
        "path": path.name,
        "exists": True,
        "bytes": len(text.encode("utf-8", "replace")),
        "lines": text.count("\n") + 1,
        "h1": parser.h1,
        "sections": parser.sections,
        "articles": parser.articles,
        "buttons": parser.buttons,
        "tables": parser.tables,
        "markerHits": hits,
        "chromeStackScore": chrome_hits,
        "classTop": sorted(parser.classes.items(), key=lambda kv: -kv[1])[:18],
        "head": text[:900],
    }


def _theme_viewport_bits() -> dict:
    theme = SITE / "nr2-optical-theme.css"
    if not theme.is_file():
        return {"exists": False}
    text = theme.read_text(encoding="utf-8", errors="replace")
    needles = [
        "100vh",
        "100dvh",
        "overflow-y",
        "overflow: auto",
        "min-height",
        ".shell",
        ".main",
        "exec-letterhead",
        "money-strip",
        "ops-gates",
        "nr2-crumb",
        "clamp(",
        "@media",
    ]
    hits = {n: (n in text) for n in needles}
    # extract a few size-ish rules
    snippets = {}
    for pat, key in (
        (r"\.shell\s*\{[^}]+\}", "shellRule"),
        (r"\.main\s*\{[^}]+\}", "mainRule"),
        (r"\.exec-letterhead[^{]*\{[^}]+\}", "letterheadRule"),
        (r"\.money-strip[^{]*\{[^}]+\}", "moneyStripRule"),
    ):
        m = re.search(pat, text, re.S)
        if m:
            snippets[key] = m.group(0)[:400]
    return {
        "exists": True,
        "bytes": len(text.encode("utf-8", "replace")),
        "hits": hits,
        "snippets": snippets,
    }


def live_audit() -> dict:
    optical = sorted(SITE.glob("nr2-optical*.html"))
    # other financial-ish HTML in site (non-optical)
    other = sorted(
        p
        for p in SITE.glob("*.html")
        if not p.name.startswith("nr2-optical")
        and any(
            k in p.name.lower()
            for k in (
                "financial",
                "apex",
                "claims",
                "ar",
                "dashboard",
                "close",
                "money",
                "period",
                "office",
                "hal",
                "bench",
            )
        )
    )
    # also sample a few well-known non-optical pages if present
    extras = []
    for name in (
        "index.html",
        "apex.html",
        "financial.html",
        "claims.html",
        "period-close.html",
        "office-manager.html",
        "hal.html",
    ):
        p = SITE / name
        if p.is_file() and p not in other:
            extras.append(p)
    other = sorted(set(other + extras), key=lambda p: p.name)[:16]

    return {
        "repoRoot": str(REPO),
        "operatorAsk": OPERATOR_REQUEST_VERBATIM,
        "viewportTarget": {
            "goal": "highly polished executive first viewport; minimize forced scroll",
            "schemaChangeAllowed": True,
            "noReact": True,
            "typicalDesk": "1080p–1440p laptop / CFO desk",
        },
        "theme": _theme_viewport_bits(),
        "opticalPages": [_page_audit(p) for p in optical],
        "otherFinancialPages": [_page_audit(p) for p in other],
        "priorExecutiveConsult": "MOONSHOT_HIGH_EXECUTIVE_LOOK_2026-07-16.md (E1–E4 shipped)",
        "note": (
            "Operator reports pages too big / must scroll after letterhead + money-strip "
            "+ honesty + ops chrome stacked. Schema may change."
        ),
    }


def chat(system: str, user: str, api_key: str, base_url: str) -> tuple[str, dict]:
    if "openrouter.ai" in (base_url or "").lower():
        model = str(
            os.getenv("MOONSHOT_MODEL")
            or os.getenv("KIMI_K2_MODEL")
            or "moonshotai/kimi-k2.5"
        ).strip()
    else:
        model = str(os.getenv("MOONSHOT_MODEL") or "kimi-k2.5").strip()
    body = {
        "model": model,
        "temperature": 1,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        base_url,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/mrenodds-ui/newridgefamilyfinancial",
            "X-Title": "NR2 Moonshot executive no-scroll viewport",
        },
    )
    with urllib.request.urlopen(req, context=CTX, timeout=180) as r:
        raw = json.loads(r.read().decode("utf-8", "replace"))
    return extract_message_content(raw), {"model": model, "rawKeys": list(raw.keys())}


def main() -> int:
    print("RESOLVE_API…", flush=True)
    key_name, api_key, base = resolve_api_and_endpoint()
    if not api_key:
        print("NO_API_KEY: set OPENROUTER_API_KEY or MOONSHOT_API_KEY", file=sys.stderr)
        return 2
    print("AUDIT…", flush=True)
    audit = live_audit()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (OUT / f"moonshot_executive_no_scroll_audit_{stamp}.json").write_text(
        json.dumps(audit, indent=2), encoding="utf-8"
    )
    user = (
        "LIVE AUDIT JSON follows. Pages force scroll; operator wants high-executive "
        "first-viewport polish; schema/HTML structure MAY change (no React).\n\n"
        + json.dumps(audit, indent=2)[:95000]
    )
    print(f"CHAT… endpoint={base[:48]}… payload_chars={len(user)}", flush=True)
    try:
        content, meta = chat(SYSTEM, user, api_key, base)
    except Exception as exc:  # noqa: BLE001
        print(f"CHAT_FAIL: {exc}", file=sys.stderr)
        return 1
    if not content.strip():
        print("EMPTY_RESPONSE", file=sys.stderr)
        return 1
    report = DOCS / f"MOONSHOT_EXECUTIVE_NO_SCROLL_VIEWPORT_{DATE}.md"
    header = (
        f"# Moonshot AI — Executive No-Scroll Viewport (CONSULT ONLY)\n\n"
        f"**Date:** {DATE}\n"
        f"**Model:** `{meta.get('model')}`\n"
        f"**Key:** {key_name}\n"
        f"**Script:** `scripts/run_moonshot_executive_no_scroll_viewport_consult.py`\n"
        f"**Apply:** Operator must say continue / approve before Cursor applies.\n\n"
        f"## Operator request (verbatim)\n\n"
        f"> {OPERATOR_REQUEST_VERBATIM}\n\n"
        f"---\n\n"
    )
    report.write_text(header + content.strip() + "\n", encoding="utf-8")
    (OUT / f"moonshot_executive_no_scroll_{stamp}.json").write_text(
        json.dumps({"meta": meta, "content": content}, indent=2), encoding="utf-8"
    )
    print(report)
    print("---")
    try:
        print(content[:6500])
    except UnicodeEncodeError:
        print(content[:6500].encode("ascii", "replace").decode("ascii"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
