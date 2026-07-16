"""Moonshot AI — How can optical pages look less sterile / more highly polished?

CONSULT ONLY — operator: ask moonshot ai how these pages can look less sterile
and more higly polished
"""

from __future__ import annotations

import json
import os
import ssl
import sys
import urllib.request
from datetime import datetime, timezone
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
    "ask moonshot ai how these pages can look less sterile and more higly polished"
)

SYSTEM = """You are Moonshot AI — principal visual/product designer for NewRidgeFinancial2 (NR2).
CONSULT ONLY — DO NOT APPLY CODE.

Operator said (verbatim): ask moonshot ai how these pages can look less sterile
and more higly polished

CONTEXT — Functional polish Packages 1–9 already shipped on main. The pages now
feel OPS-correct but visually STERILE (dark mono, metric strips, honesty chrome,
sparse atmosphere). Operator wants the NEXT step toward \"highly polished\" LOOK —
warmth, depth, composition — WITHOUT sacrificing money honesty.

ALREADY SHIPPED (do not redo as functional packages):
1 Ops gates · 2 PHI glass · 3 Wayfinding · 4 Loading/empty honesty · 5 Tablet touch
6 Motion grammar · 7 Focus/a11y · 8 Soft/hard fail retry · 9 Print + PHI redaction
Commits include: df0b075, 4658f91, b36bd7a, 578248f, d34acd5, f8bce2d, 6a06940,
a6b63e4, 29cd975

HARD CONSTRAINTS:
- SoftDent READ-ONLY; empty ≠ $0 must stay readable (never pretty away NO SIGNAL)
- Board PHI initials+hash; no SoftDent write-back; no third-party chat embeds
- Static HTML+JS — NO React/Vite rewrite
- Keep SoftDent / QB / HAL color tokens (evolve, don't discard)
- Avoid AI design clichés: purple-on-white, cream+terracotta serif, broadsheet hairlines
- Cards only when they hold interaction; first viewport = one composition
- Prefer REAL paths under NewRidgeFinancial2/site/

YOUR JOB:
1) Diagnose WHY the pages feel sterile (specific CSS/HTML patterns from audit)
2) Prescribe ordered VISUAL polish packages that add atmosphere + hierarchy
   without breaking honesty chrome
3) Pick THE single best FIRST visual package to apply next
4) Give concrete CSS/token moves (spacing, type, texture, light) — not vague \"make nicer\"

OUTPUT (strict markdown):
# Verdict (one sentence — THE first anti-sterile package)
## 0. Operator Intent (verbatim)
## 1. Why it feels sterile now (specific patterns + REAL files)
## 2. Highly-polished target look (3–5 sensory principles for NR2 optical)
## 3. Ordered visual polish packages (1..N)
Each: name, why, REAL files, concrete CSS/JS moves, effort S/M/L, validation gate
## 4. Recommended FIRST package (apply now)
## 5. What NOT to change (honesty / PHI / ops gates)
## 6. Anti-patterns (sterile traps + AI-slop traps)
## 7. Acceptance criteria for \"no longer sterile\"
## 8. Executive Summary (5 bullets)
## 9. Approval Checklist
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
    base = (
        os.getenv("MOONSHOT_API_BASE") or os.getenv("KIMI_K2_BASE_URL") or ""
    ).strip()
    if not base:
        if key_name == "MOONSHOT_API_KEY" or (api_key or "").startswith("sk-nv"):
            base = "https://api.moonshot.ai/v1/chat/completions"
        else:
            base = "https://openrouter.ai/api/v1/chat/completions"
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


def get_json(path: str, timeout: int = 40):
    try:
        with urllib.request.urlopen(BASE + path, context=CTX, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:  # noqa: BLE001
        return {"error": type(e).__name__, "msg": str(e)[:240]}


def _file_bytes(path: Path) -> int | None:
    try:
        return int(path.stat().st_size)
    except OSError:
        return None


def _head(path: Path, limit: int = 3500) -> dict:
    if not path.is_file():
        return {"path": str(path), "exists": False}
    text = path.read_text(encoding="utf-8", errors="replace")
    return {
        "path": path.name,
        "exists": True,
        "bytes": len(text.encode("utf-8", "replace")),
        "head": text[:limit],
    }


def _snippet(path: Path, needles: list[str]) -> dict:
    if not path.is_file():
        return {"path": str(path), "exists": False}
    text = path.read_text(encoding="utf-8", errors="replace")
    return {
        "path": path.name,
        "exists": True,
        "bytes": len(text.encode("utf-8", "replace")),
        "hits": {n: (n in text) for n in needles},
    }


def live_audit() -> dict:
    theme = SITE / "nr2-optical-theme.css"
    wire = SITE / "nr2-optical-page-wire.js"
    claims_html = SITE / "nr2-optical-page-claims.html"
    ar_html = SITE / "nr2-optical-page-ar.html"
    om_html = SITE / "nr2-optical-page-office-manager.html"
    hal_html = SITE / "nr2-optical-page-hal.html"
    landing = SITE / "nr2-optical-beam-touch-mockup.html"
    hub = SITE / "nr2-optical-pages-hub.html"
    smoke = get_json("/api/health/desk-smoke?run=0", 25)
    app = get_json("/api/app-info", 25)
    return {
        "repoRoot": str(REPO),
        "operatorAsk": OPERATOR_REQUEST_VERBATIM,
        "shippedFunctionalPolish": [
            "P1 ops gates",
            "P2 PHI glass",
            "P3 wayfinding",
            "P4 loading/empty",
            "P5 tablet touch",
            "P6 motion",
            "P7 focus/a11y",
            "P8 soft/hard fail",
            "P9 print PHI redact",
        ],
        "visualMarkers": {
            "theme": _snippet(
                theme,
                [
                    "--hal",
                    "--sd",
                    "--qb",
                    "font-family",
                    "gradient",
                    "background",
                    "nr2-motion",
                    "money-strip",
                    "metric-face",
                    "beam",
                    "max-width: 1180px",
                    "@media print",
                ],
            ),
            "wire": _snippet(
                wire,
                [
                    "bootMotionGrammar",
                    "bindPrintHygiene",
                    "showPageError",
                    "trapFocus",
                    "mountOpsGates",
                ],
            ),
        },
        "pageHeads": {
            "themeCss": _head(theme, 4500),
            "claimsHtml": _head(claims_html, 2800),
            "arHtml": _head(ar_html, 2200),
            "omHtml": _head(om_html, 2200),
            "halHtml": _head(hal_html, 2200),
            "landingHtml": _head(landing, 2800),
            "hubHtml": _head(hub, 2200),
        },
        "pageInventory": {
            "html": sorted(p.name for p in SITE.glob("nr2-optical*.html")),
            "jsBytes": {
                p.name: _file_bytes(p) for p in sorted(SITE.glob("nr2-optical*.js"))
            },
            "themeBytes": _file_bytes(theme),
        },
        "live": {
            "deskSmoke": smoke,
            "appInfoPilot": (app or {}).get("pilot") if isinstance(app, dict) else None,
            "buildId": (app or {}).get("buildId") if isinstance(app, dict) else None,
        },
    }


def chat(system: str, user: str, api_key: str, base_url: str) -> tuple[str, dict]:
    if "moonshot" in (base_url or "").lower():
        model = str(os.getenv("MOONSHOT_MODEL") or "kimi-k2.5").strip()
    else:
        model = str(
            os.getenv("MOONSHOT_MODEL") or os.getenv("KIMI_K2_MODEL") or "moonshotai/kimi-k2"
        ).strip()
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
            "X-Title": "NR2 Moonshot less-sterile polish consult",
        },
    )
    with urllib.request.urlopen(req, context=CTX, timeout=180) as r:
        raw = json.loads(r.read().decode("utf-8", "replace"))
    return extract_message_content(raw), {"model": model, "rawKeys": list(raw.keys())}


def main() -> int:
    key_name, api_key, base = resolve_api_and_endpoint()
    if not api_key:
        print("NO_API_KEY: set OPENROUTER_API_KEY or MOONSHOT_API_KEY", file=sys.stderr)
        return 2
    audit = live_audit()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (OUT / f"moonshot_less_sterile_polish_audit_{stamp}.json").write_text(
        json.dumps(audit, indent=2), encoding="utf-8"
    )
    user = (
        "LIVE AUDIT JSON follows. Diagnose sterile look and prescribe visual polish "
        "packages so NR2 optical pages feel highly polished — not clinical/sterile.\n\n"
        + json.dumps(audit, indent=2)[:120000]
    )
    try:
        content, meta = chat(SYSTEM, user, api_key, base)
    except Exception as exc:  # noqa: BLE001
        print(f"CHAT_FAIL: {exc}", file=sys.stderr)
        return 1
    if not content.strip():
        print("EMPTY_RESPONSE", file=sys.stderr)
        return 1
    report = DOCS / f"MOONSHOT_LESS_STERILE_POLISH_{DATE}.md"
    header = (
        f"# Moonshot AI — Less Sterile / Highly Polished Look (CONSULT ONLY)\n\n"
        f"**Date:** {DATE}\n"
        f"**Model:** `{meta.get('model')}`\n"
        f"**Key:** {key_name}\n"
        f"**Script:** `scripts/run_moonshot_less_sterile_polish_consult.py`\n"
        f"**Apply:** Operator must say continue / approve before Cursor applies.\n\n"
        f"## Operator request (verbatim)\n\n"
        f"> {OPERATOR_REQUEST_VERBATIM}\n\n"
        f"---\n\n"
    )
    report.write_text(header + content.strip() + "\n", encoding="utf-8")
    (OUT / f"moonshot_less_sterile_polish_{stamp}.json").write_text(
        json.dumps({"meta": meta, "content": content}, indent=2), encoding="utf-8"
    )
    print(report)
    print("---")
    try:
        print(content[:5000])
    except UnicodeEncodeError:
        print(content[:5000].encode("ascii", "replace").decode("ascii"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
