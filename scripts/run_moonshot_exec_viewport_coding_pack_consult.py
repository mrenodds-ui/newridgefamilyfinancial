"""Moonshot AI — Deliver ALL coding to lock executive no-scroll viewport.

Operator: get all coding from moonshot to fix it.
Prior audit said PASS with NONE — operator still wants concrete APPLY-READY
CSS/HTML/JS so Cursor can paste/apply without inventing.
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
AUDIT_MD = DOCS / "MOONSHOT_EXEC_VIEWPORT_DID_WE_FUCK_UP_2026-07-17.md"

OPERATOR_REQUEST_VERBATIM = "get all coding from moonshot to fix it"

SYSTEM = """You are Moonshot AI — principal visual/product designer + implementer for NR2.
You MAY and MUST deliver APPLY-READY code. Cursor will paste it.

Operator said (verbatim): get all coding from moonshot to fix it

CONTEXT:
- Your Packages 1–4 report already exists.
- Your forensic audit said PASS / NONE remediation.
- Operator still wants ALL coding from you — the complete canonical CSS/HTML/JS
  patches that lock the executive desk so Cursor cannot invent or half-apply.

HARD CONSTRAINTS:
- SoftDent READ-ONLY; empty ≠ $0; PHI initials+hash; no SoftDent write-back
- No React rewrite; no third-party chat embeds
- Honesty stays body-fixed LED (or ≤48px header) — never hide
- Beam = 1px gold laser only — never restore 3px gradient/sweep
- Chrome-frame stays ≤172px with tabs (140 desk + 32 tabs)
- REAL paths only under NewRidgeFinancial2/site/

YOUR JOB:
1) Deliver COMPLETE apply-ready coding for the live end-state (P1→P4 converged).
2) If truly nothing is broken, still deliver a CANONICAL hardening pack:
   - Exact CSS block for chrome-frame / letterhead / honesty / beam / tabs / main
   - Any HTML schema fixes still missing on any page
   - JS for bootExecTabs if needed
   - Optional 1080p pixel-ruler gate snippet
3) Prefer FULL replacement CSS blocks (copy-paste) over vague advice.
4) Mark each file path. Use fenced code blocks with language tags.
5) Order patches 1..N. Effort S/M/L. Validation gate each.

OUTPUT (strict markdown):
# Verdict (one sentence — coding pack name)
## 0. Operator Intent (verbatim)
## 1. Do we still need code? (YES — hardening / YES — fix X / NO-but-still-deliver-canonical)
## 2. Canonical CSS — nr2-optical-theme.css (FULL replacement blocks)
## 3. HTML schema patches (per page or shared pattern) — FULL snippets
## 4. JS patches — nr2-optical-page-wire.js (if any)
## 5. Landing / Hub extras (if any)
## 6. Ordered apply checklist (Cursor steps)
## 7. Validation gate (1080p / schema)
## 8. What NOT to change
## 9. Executive Summary (5 bullets)

RULES FOR CODE:
- Every CSS rule must include selectors + full declarations.
- Do not say “adjust as needed” — give exact values.
- If a section is unchanged vs live, say UNCHANGED and paste the live-correct block anyway so Cursor has one source of truth.
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
    candidates = (
        ("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY", "").strip()),
        ("MOONSHOT_API_KEY", os.getenv("MOONSHOT_API_KEY", "").strip()),
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


def css_slice(css: str, start_pat: str, end_pat: str | None = None, lim: int = 4500) -> str:
    m = re.search(start_pat, css)
    if not m:
        return ""
    start = m.start()
    if end_pat:
        m2 = re.search(end_pat, css[m.end() :])
        end = m.end() + (m2.start() if m2 else lim)
    else:
        end = start + lim
    return css[start:end]


def live_pack() -> dict:
    css = (SITE / "nr2-optical-theme.css").read_text(encoding="utf-8", errors="replace")
    wire = (SITE / "nr2-optical-page-wire.js").read_text(encoding="utf-8", errors="replace")
    pages = {}
    for p in sorted(SITE.glob("nr2-optical-page-*.html")) + [
        SITE / "nr2-optical-pages-hub.html",
        SITE / "nr2-optical-beam-touch-mockup.html",
    ]:
        if not p.is_file():
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        # head + chrome-frame opening for schema reference
        head = t[:1200]
        frame = ""
        fm = re.search(r'<div class="chrome-frame">[\s\S]{0,2200}</nav>\s*</div>', t)
        if fm:
            frame = fm.group(0)
        pages[p.name] = {
            "bytes": len(t.encode("utf-8", "replace")),
            "head": head,
            "chromeFrameSnippet": frame[:1800],
            "hasHonesty": 'class="honesty"' in t,
            "cacheBust": "moonshot-exact-p1-p4" in t,
        }
    # wire boots
    boot = ""
    for name in ("bootExecTabs", "bootExecutiveChrome", "bootPackage1StickyStack"):
        m = re.search(
            rf"function {name}\(\) \{{[\s\S]{{0,2500}}\n  \}}",
            wire,
        )
        if m:
            boot += m.group(0) + "\n\n"
    return {
        "operatorAsk": OPERATOR_REQUEST_VERBATIM,
        "priorAuditVerdict": "PASS / NONE remediation (but operator wants coding anyway)",
        "originalConsultExcerpt": (
            CONSULT.read_text(encoding="utf-8", errors="replace")[:8000]
            if CONSULT.is_file()
            else "MISSING"
        ),
        "fuckupAuditExcerpt": (
            AUDIT_MD.read_text(encoding="utf-8", errors="replace")[:5000]
            if AUDIT_MD.is_file()
            else "MISSING"
        ),
        "liveThemeBlocks": {
            "letterhead": css_slice(
                css, r"/\* Moonshot Package 2", r"/\* =====|\.exec-period-seal"
            ),
            "chromeFrame": css_slice(
                css,
                r"/\* Moonshot Package 3\+4",
                r"/\* Exact Moonshot Package 1|\.exec-compact-header",
            ),
            "compactHonestyBeam": css_slice(
                css,
                r"/\* Exact Moonshot Package 1",
                r"\.main h1 \{",
            ),
            "globalBeam": css_slice(
                css,
                r"/\* Moonshot Package 1 §4",
                r"@keyframes flow",
            ),
        },
        "liveWireBoots": boot[:6000],
        "pages": pages,
        "instruction": (
            "Deliver COMPLETE apply-ready coding packs. Even if PASS, give "
            "canonical CSS/HTML/JS blocks Cursor must apply as source of truth."
        ),
    }


def chat(system: str, user: str, api_key: str, base_url: str) -> tuple[str, dict]:
    if "openrouter.ai" in (base_url or "").lower() and not (api_key or "").startswith("sk-nv"):
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
            "X-Title": "NR2 Moonshot exec viewport coding pack",
        },
    )
    with urllib.request.urlopen(req, context=CTX, timeout=300) as r:
        raw = json.loads(r.read().decode("utf-8", "replace"))
    return extract_message_content(raw), {"model": model}


def main() -> int:
    print("RESOLVE_API…", flush=True)
    key_name, api_key, base = resolve_api_and_endpoint()
    if not api_key:
        print("NO_API_KEY", file=sys.stderr)
        return 2
    print("PACK…", flush=True)
    pack = live_pack()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    audit_path = OUT / f"moonshot_exec_viewport_coding_pack_audit_{stamp}.json"
    # keep JSON lean for chat — pages heads only for 3 samples + schema flags
    lean = {
        **{k: v for k, v in pack.items() if k != "pages"},
        "pageFlags": {
            n: {
                "hasHonesty": d["hasHonesty"],
                "cacheBust": d["cacheBust"],
                "hasChrome": bool(d.get("chromeFrameSnippet")),
                "bytes": d["bytes"],
            }
            for n, d in pack["pages"].items()
        },
        "sampleChromeFrames": {
            n: pack["pages"][n]["chromeFrameSnippet"]
            for n in (
                "nr2-optical-page-ar.html",
                "nr2-optical-page-hal.html",
                "nr2-optical-page-claims.html",
                "nr2-optical-pages-hub.html",
            )
            if n in pack["pages"]
        },
    }
    audit_path.write_text(json.dumps(pack, indent=2)[:200000], encoding="utf-8")
    user = (
        "Operator wants ALL coding from you to fix/lock the executive viewport. "
        "Deliver apply-ready CSS/HTML/JS. LIVE pack JSON follows.\n\n"
        + json.dumps(lean, indent=2)[:95000]
    )
    print(f"CHAT… {base[:40]}… key={key_name} chars={len(user)}", flush=True)
    try:
        content, meta = chat(SYSTEM, user, api_key, base)
    except Exception as exc:  # noqa: BLE001
        detail = str(exc)
        if hasattr(exc, "read"):
            try:
                detail = exc.read().decode("utf-8", "replace")[:800]
            except Exception:
                pass
        print(f"CHAT_FAIL: {exc}\n{detail}", file=sys.stderr)
        return 1
    if not content.strip():
        print("EMPTY", file=sys.stderr)
        return 1
    report = DOCS / f"MOONSHOT_EXEC_VIEWPORT_CODING_PACK_{DATE}.md"
    header = (
        f"# Moonshot AI — Executive Viewport Coding Pack (APPLY-READY)\n\n"
        f"**Date:** {DATE}\n"
        f"**Model:** `{meta.get('model')}`\n"
        f"**Key:** {key_name}\n"
        f"**Script:** `scripts/run_moonshot_exec_viewport_coding_pack_consult.py`\n"
        f"**Audit JSON:** `{audit_path}`\n\n"
        f"## Operator request (verbatim)\n\n"
        f"> {OPERATOR_REQUEST_VERBATIM}\n\n"
        f"---\n\n"
    )
    report.write_text(header + content.strip() + "\n", encoding="utf-8")
    print(f"REPORT_OK {report}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
