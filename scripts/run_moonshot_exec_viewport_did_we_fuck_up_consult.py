"""Moonshot AI — Did we fuck up the executive no-scroll viewport?

Compare ORIGINAL consult (Packages 1–4) vs LIVE optical files after exact restart.
CONSULT ONLY — no code apply.
"""

from __future__ import annotations

import json
import os
import re
import ssl
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / ".local_logs" / "moonshot_financial_eval"
DOCS = REPO / "NewRidgeFinancial2" / "docs"
SITE = REPO / "NewRidgeFinancial2" / "site"
OUT.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)
DATE = datetime.now(timezone.utc).strftime("%Y-%m-%d")

CTX = ssl._create_unverified_context()
BASE = os.getenv("NR2_BROWSER", "https://127.0.0.1:8765").rstrip("/")

CONSULT = DOCS / "MOONSHOT_EXECUTIVE_NO_SCROLL_VIEWPORT_2026-07-16.md"
RESTART = DOCS / "MOONSHOT_EXECUTIVE_NO_SCROLL_VIEWPORT_EXACT_RESTART_2026-07-17.md"

OPERATOR_REQUEST_VERBATIM = (
    "now use his last report and what we have now through moonshot ai and see "
    "if you fucked up and report"
)

SYSTEM = """You are Moonshot AI — principal visual/product designer for NR2 Optical.
CONSULT ONLY — DO NOT APPLY CODE. Be blunt and forensic.

Operator said (verbatim): now use his last report and what we have now through
moonshot ai and see if you fucked up and report

CONTEXT:
- Your LAST report was MOONSHOT_EXECUTIVE_NO_SCROLL_VIEWPORT (Packages 1–4).
- Cursor claims they restarted and implemented Packages 1→4 exactly, then committed.
- Your job: compare YOUR report's concrete moves vs LIVE audit evidence.
- Say clearly: PASS / PARTIAL / FUCKED UP — and WHY with REAL file evidence.

HARD CONSTRAINTS (do not soften):
- SoftDent READ-ONLY; empty ≠ $0; PHI initials+hash; no SoftDent write-back
- No third-party chat embeds; no React rewrite
- Honesty must remain executive-visible (bottom LED or ≤48px header)
- §7 anti-patterns: no decorative beam bloat, no fake density, no microscopic fonts

SCORE each Package 1–4:
- PASS = concrete moves present and match your literals / intent
- DRIFT = mostly there but wrong numbers, wrong placement, or leftover anti-patterns
- FAIL = missing or inverted vs your report

Also score §8 acceptance criteria (1080p first viewport / scroll budget) as
LIKELY_PASS / RISK / FAIL based on schema+CSS evidence (you have no live pixels).

OUTPUT (strict markdown):
# Verdict (one sentence — PASS / PARTIAL / FUCKED UP)
## 0. Operator Intent (verbatim)
## 1. Package scorecard (table: Package | PASS/DRIFT/FAIL | evidence | severity)
## 2. What Cursor got right
## 3. What Cursor fucked up (or drifted) — concrete diffs vs YOUR report
## 4. §8 acceptance risk (1080p / scroll budget)
## 5. What NOT to change
## 6. Ordered fix packages (only if FAIL/DRIFT) — REAL files, concrete moves, effort
## 7. Recommended FIRST fix (or NONE if PASS)
## 8. Executive Summary (5 bullets)
## 9. Approval Checklist
"""


def _load_dotenv() -> None:
    for path in (REPO / ".env", REPO / "NewRidgeFinancial2" / ".env"):
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
    # Prefer OpenRouter when MOONSHOT_API_KEY is a stub / too short (common on this desk).
    candidates = (
        ("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY", "").strip()),
        ("KIMI_K2_API_KEY", os.getenv("KIMI_K2_API_KEY", "").strip()),
        ("MOONSHOT_API_KEY", os.getenv("MOONSHOT_API_KEY", "").strip()),
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
    # Desk quirk: OPENROUTER_API_KEY often holds a Moonshot sk-nv* key — route by prefix.
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
            or "https://api.moonshot.ai/v1/chat/completions"
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


def get_json(path: str, timeout: int = 8):
    try:
        with urllib.request.urlopen(BASE + path, context=CTX, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:  # noqa: BLE001
        return {"error": type(e).__name__, "msg": str(e)[:240]}


def http_status(path: str, timeout: int = 8) -> dict:
    url = BASE + "/" + path.lstrip("/")
    try:
        with urllib.request.urlopen(url, context=CTX, timeout=timeout) as r:
            return {"url": url, "status": r.status, "ok": 200 <= r.status < 300}
    except Exception as e:  # noqa: BLE001
        return {"url": url, "status": None, "ok": False, "error": str(e)[:200]}


def theme_audit(css: str) -> dict:
    return {
        "P1_beam_1px_laser": bool(
            re.search(
                r"\.beam\s*\{[^}]*height:\s*1px[^}]*"
                r"background:\s*rgba\(\s*201,\s*162,\s*39,\s*0\.3",
                css,
                re.S,
            )
        ),
        "P1_beam_no_3px_gradient": not bool(
            re.search(r"\.beam\s*\{[^}]*height:\s*3px", css, re.S)
        ),
        "P1_beam_no_sweep": "beam-sweep" not in css,
        "P1_honesty_fixed_led": bool(
            re.search(
                r"body\s*>\s*\.honesty\s*\{[^}]*position:\s*fixed[^}]*"
                r"bottom:\s*0[^}]*left:\s*220px[^}]*height:\s*20px[^}]*"
                r"font-size:\s*10px",
                css,
                re.S,
            )
        ),
        "P1_compact_header_12": ".exec-compact-header" in css
        and bool(
            re.search(
                r"\.exec-compact-header \.mode-eyebrow[\s\S]{0,200}font-size:\s*12px",
                css,
            )
        ),
        "P1_main_height_banner_honesty": "calc(100dvh - 36px - 20px)" in css
        or "var(--nr2-chrome-frame-h)" in css,
        "P2_letterhead_48": bool(
            re.search(
                r"#nr2-page-letterhead\.banner\.exec-letterhead[\s\S]{0,400}height:\s*48px",
                css,
            )
        ),
        "P2_letterhead_gold_border": "border-bottom: 1px solid rgba(201, 162, 39, 0.35)"
        in css,
        "P3_chrome_frame_fixed": bool(
            re.search(
                r"\.chrome-frame\s*\{[^}]*position:\s*fixed[^}]*left:\s*220px",
                css,
                re.S,
            )
        ),
        "P3_chrome_height_140_or_172": "--nr2-chrome-frame-h: 172px" in css
        or re.search(r"\.chrome-frame\s*\{[^}]*height:\s*140px", css, re.S),
        "P4_exec_tabs_in_frame": ".chrome-frame > .exec-tabs" in css,
        "P4_tab_panel_hidden": ".main > .tab-panel[hidden]" in css,
        "hub_chrome_parity": "body.page-hub .chrome-frame" in css,
        "snippets": {
            "chromeFrame": (
                m.group(0)[:350]
                if (
                    m := re.search(r"\.chrome-frame\s*\{[^}]+\}", css, re.S)
                )
                else None
            ),
            "beam": (
                m.group(0)[:280]
                if (m := re.search(r"(?:/\*[^*]*\*/\s*)?\.beam\s*\{[^}]+\}", css, re.S))
                else None
            ),
            "honesty": (
                m.group(0)[:280]
                if (m := re.search(r"body\s*>\s*\.honesty\s*\{[^}]+\}", css, re.S))
                else None
            ),
        },
    }


def page_audit(path: Path) -> dict:
    t = path.read_text(encoding="utf-8", errors="replace")
    main_m = re.search(r'<main class="main">(.*?)</main>', t, re.S)
    main = main_m.group(1) if main_m else ""
    frame_m = re.search(
        r'<div class="chrome-frame">(.*?)</div>\s*\n\s*<div class="tab-panel"',
        t,
        re.S,
    )
    frame = frame_m.group(1) if frame_m else ""
    ledge_idx = frame.find('class="ledge"')
    tabs_idx = frame.find('class="exec-tabs"')
    letterhead_idx = frame.find("exec-letterhead")
    summary = re.search(
        r'data-tab-panel="summary"[^>]*>(.*?)</div>\s*<div class="tab-panel"',
        t,
        re.S,
    )
    summary_html = summary.group(1) if summary else ""
    return {
        "page": path.name,
        "bytes": len(t.encode("utf-8", "replace")),
        "cacheBust": "moonshot-exact-p1-p4" in t or "moonshot-exec-viewport" in t,
        "has_chrome_frame": 'class="chrome-frame"' in t,
        "has_letterhead": "exec-letterhead" in t,
        "has_ledge": 'class="ledge"' in t,
        "has_exec_tabs": 'class="exec-tabs"' in t,
        "has_summary_tab": 'data-tab="summary"' in t,
        "has_tab_panel": 'class="tab-panel"' in t,
        "honesty_body_led": bool(
            re.search(r"</main>[\s\S]*?<div class=\"honesty\"", t)
        ),
        "honesty_not_in_main": '<div class="honesty"' not in main,
        "no_exec_compact_in_flow": "exec-compact-header" not in main,
        "no_standalone_beam_div": not bool(
            re.search(r'<div class="beam"', main)
        ),
        "tabs_after_ledge_in_frame": bool(frame_m)
        and 0 <= ledge_idx < tabs_idx
        and letterhead_idx >= 0
        and letterhead_idx < ledge_idx,
        "summary_not_hidden": not bool(
            re.search(r'data-tab-panel="summary"[^>]*\bhidden\b', t)
        ),
        "summary_has_hal_cmd_header": "hal-cmd-header" in summary_html,
        "summary_len": len(summary_html),
        "kids0_chrome": main.lstrip().startswith('<div class="chrome-frame">'),
        "sd_tokens": len(re.findall(r'\bclass="[^"]*\bsd\b', main)),
        "qb_tokens": len(re.findall(r'\bclass="[^"]*\bqb\b', main)),
    }


def wire_audit(js: str) -> dict:
    return {
        "bootExecTabs": "function bootExecTabs" in js and "bootExecTabs()" in js,
        "default_summary": 'activate("summary")' in js,
        "bootExecutiveChrome": "function bootExecutiveChrome" in js,
    }


def live_audit() -> dict:
    css = (SITE / "nr2-optical-theme.css").read_text(encoding="utf-8", errors="replace")
    js = (SITE / "nr2-optical-page-wire.js").read_text(encoding="utf-8", errors="replace")
    pages = sorted(SITE.glob("nr2-optical-page-*.html"))
    page_rows = [page_audit(p) for p in pages]
    schema_fail = [
        r["page"]
        for r in page_rows
        if not (
            r["has_chrome_frame"]
            and r["has_letterhead"]
            and r["has_ledge"]
            and r["has_exec_tabs"]
            and r["tabs_after_ledge_in_frame"]
            and r["honesty_body_led"]
            and r["kids0_chrome"]
        )
    ]
    theme = theme_audit(css)
    theme_fail = [k for k, v in theme.items() if k.startswith("P") and v is False]
    consult_text = (
        CONSULT.read_text(encoding="utf-8", errors="replace")[:9000]
        if CONSULT.is_file()
        else "MISSING"
    )
    restart_text = (
        RESTART.read_text(encoding="utf-8", errors="replace")[:8000]
        if RESTART.is_file()
        else "MISSING"
    )
    return {
        "repoRoot": str(REPO),
        "operatorAsk": OPERATOR_REQUEST_VERBATIM,
        "gitTip": "4fb472a claimed exact Packages 1-4 restart",
        "yourOriginalConsultPath": str(CONSULT.name),
        "yourOriginalConsultExcerpt": consult_text,
        "cursorRestartNote": restart_text,
        "themeChecks": theme,
        "themeFailKeys": theme_fail,
        "wireChecks": wire_audit(js),
        "pages": page_rows,
        "schemaFailPages": schema_fail,
        "hub": page_audit(SITE / "nr2-optical-pages-hub.html")
        if (SITE / "nr2-optical-pages-hub.html").is_file()
        else None,
        "landingHonesty": "class=\"honesty\""
        in (SITE / "nr2-optical-beam-touch-mockup.html").read_text(
            encoding="utf-8", errors="replace"
        )
        if (SITE / "nr2-optical-beam-touch-mockup.html").is_file()
        else False,
        "http": {
            "claims": http_status("nr2-optical-page-claims.html"),
            "hal": http_status("nr2-optical-page-hal.html"),
            "ar": http_status("nr2-optical-page-ar.html"),
            "hub": http_status("nr2-optical-pages-hub.html"),
        },
        "liveBeams": get_json("/api/money-beams", 8),
        "moonshotPackageTargets": {
            "P1": [
                "ledge first (evolved: inside chrome-frame after letterhead)",
                "honesty body fixed 20px LED",
                "beam 1px gold laser rgba(201,162,39,0.3)",
                "compact header OR letterhead successor",
            ],
            "P2": [
                "exec-letterhead 3-col ≤48px",
                "delete flow eyebrow/h1/kicker",
                "beam as letterhead border-bottom",
            ],
            "P3": [
                "chrome-frame fixed top/left220/height140",
                "letterhead+ledge inside frame",
                "main scrolls below frame",
                "honesty kept as P1 body LED (applied conflict resolution)",
            ],
            "P4": [
                "exec-tabs after ledge",
                "heavy content in tab-panels",
                "default Summary thin",
                "frame 172 = 140+32",
            ],
        },
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
            "X-Title": "NR2 Moonshot exec viewport fuck-up audit",
        },
    )
    with urllib.request.urlopen(req, context=CTX, timeout=240) as r:
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
    audit_path = OUT / f"moonshot_exec_viewport_fuckup_audit_{stamp}.json"
    audit_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(
        f"AUDIT_OK schema_fail={audit['schemaFailPages']} theme_fail={audit['themeFailKeys']}",
        flush=True,
    )
    user = (
        "FORENSIC AUDIT: Your original Packages 1–4 report vs LIVE optical files "
        "after Cursor's 'exact restart'. Decide PASS / PARTIAL / FUCKED UP.\n\n"
        + json.dumps(audit, indent=2)[:110000]
    )
    print(f"CHAT… endpoint={base[:48]}… key={key_name} payload_chars={len(user)}", flush=True)
    try:
        content, meta = chat(SYSTEM, user, api_key, base)
    except Exception as exc:  # noqa: BLE001
        err = str(exc)
        if hasattr(exc, "read"):
            try:
                err = exc.read().decode("utf-8", "replace")[:800]
            except Exception:
                pass
        print(f"CHAT_FAIL: {exc}\n{err}", file=sys.stderr)
        return 1
    if not content.strip():
        print("EMPTY_RESPONSE", file=sys.stderr)
        return 1
    report = DOCS / f"MOONSHOT_EXEC_VIEWPORT_DID_WE_FUCK_UP_{DATE}.md"
    header = (
        f"# Moonshot AI — Did We Fuck Up Executive Viewport? (CONSULT ONLY)\n\n"
        f"**Date:** {DATE}\n"
        f"**Model:** `{meta.get('model')}`\n"
        f"**Key:** {key_name}\n"
        f"**Script:** `scripts/run_moonshot_exec_viewport_did_we_fuck_up_consult.py`\n"
        f"**Audit JSON:** `{audit_path}`\n"
        f"**Against:** `{CONSULT.name}`\n\n"
        f"## Operator request (verbatim)\n\n"
        f"> {OPERATOR_REQUEST_VERBATIM}\n\n"
        f"---\n\n"
    )
    report.write_text(header + content.strip() + "\n", encoding="utf-8")
    print(f"REPORT_OK {report}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
