"""Moonshot AI — HAL programming review + impressive page redesign (CONSULT ONLY).

Operator: ask moonshot ai to review HAL's programming — he should have complete
access to SoftDent and QuickBooks as well as MemoAI, the web, be able to carry
on a conversation, great personality and control the whole program. this is not
happening — need it fixed. also have him redesign his page to make it more
impressive. then report.
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
    "ask moonoshot ai to reveue hal's programming - he should have complete "
    "access to softdent and quickbooks as well as memoai, the web, be able to "
    "carry on a conversation, great personality and control the whole program.  "
    "this is not happening - need it fixed.  also have him redesign his page to "
    "make it more impressive.  then report"
)

SYSTEM = """You are Moonshot AI (kimi-k2 class) — principal HAL architect + UI
designer for NewRidgeFinancial2 (NR2). CONSULT ONLY — DO NOT APPLY CODE.

Operator (verbatim spelling preserved):
> ask moonoshot ai to reveue hail's programming - he should have complete access
> to softdent and quickbooks as well as memoai, the web, be able to carry on a
> conversation, great personality and control the whole program. this is not
> happening - need it fixed. also have him redesign his page to make it more
> impressive. then report

Interpret intent (fix typos): REVIEW HAL's programming; FIX the gap so HAL has
complete SoftDent + QuickBooks + MemoAI + web + multi-turn conversation + great
personality + whole-program control; REDESIGN HAL's page to be impressive; REPORT.

HARD CONSTRAINTS (never violate):
- SoftDent financial writes from HAL remain FORBIDDEN (read / teach / export /
  consent-queue only). "Complete SoftDent access" means complete *operator-grade
  read + GUI export + KB + navigation*, NOT write-back into SoftDent charts.
- QuickBooks posts remain consent-gated. Complete QB access = full read APIs +
  sync + consented journal push — not silent posting.
- empty ≠ $0. Never invent dollars. PHI stays local. Cloud LLM denied for HAL.
- Optical clean-slate: current live face is nr2-optical-page-hal.html + .js
  (CSP script-src 'self'). Legacy apex-core.js / hAL-agent.js are REMOVED.
- Prefer re-wiring EXISTING modules (hal-page*.js, board-actions, MemoAI store,
  web_research.py, voice, chat-9000 persona) into the optical page over inventing
  a brand-new agent framework.

CURRENT STATE (trust AUDIT JSON + file excerpts over assumptions):
Build: nr2-12017-optical-ops · optical HAL page is LIVE but thin.
What operator EXPECTS vs what is REAL:
1) SoftDent — Strong policy/KB/import read + GUI export *scripts*; HAL chat does
   NOT autonomously drive SoftDent; optical left cards mostly placeholders.
2) QuickBooks — Read APIs exist; optical underuses; recon endpoint historically
   DEAD/UNAVAILABLE; no chat "control QB day-to-day."
3) MemoAI — knowledge_memory_store + hal-memo-index exist; optical chat does not
   expose remember / search UI.
4) Web — web_research.py / DesktopBridge exist; optical evaluate-query has NO
   first-class web tool; orphaned HalAgent path.
5) Conversation — gateway accepts `messages` + stream; optical posts ONLY
   `{query, stream:false}` → single-turn. No streaming UI.
6) Personality — HAL 9000 / Cursor-parity / voice modules exist on disk but are
   NOT mounted on optical spectral console.
7) Program control — board-actions + route-exec + orchestrator exist in backend;
   optical underuses (cards say HAL but do not drive the bench).
8) Page look — CRT spectral console + 4 stub cards is thematic but thin / not
   impressive as a command center. Bind hint still says "mock replies" while chat
   is actually live-wired.

YOUR JOB:
A) Gap-by-gap programming fix plan (P0–P3) that makes HAL *feel and act* like the
   program's brain WITHIN honesty constraints.
B) Explicit redefine of "complete access" so SoftDent/QB write doctrine is clear
   (operator misunderstanding risk).
C) Redesign HAL's optical page to be IMPRESSIVE — starship / spectral command center
   aesthetic matching optical landing, WITHOUT fake money or theater that lies.
D) Concrete files, APIs, acceptance tests. CONSULT ONLY.

OUTPUT (strict markdown):
# Verdict (one paragraph — why HAL is not meeting the ask + fixability)
## 0. Operator Intent (verbatim + cleaned)
## 1. "Complete access" doctrine (what HAL MAY / MUST NOT do SoftDent+QB)
## 2. Capability Gap Map
Table: Area | Expected | Today | Gap | Fix | Effort | Risk
Cover SoftDent, QuickBooks, MemoAI, Web, Conversation, Personality, Program control
## 3. Programming Fix Plan (P0 blocker → P3)
Concrete tasks with files + routes (prefer existing)
## 4. HAL Page Redesign (impressive)
### 4A Design brief (mood, layout, motion, honesty chrome)
### 4B Wireframe (ASCII or section list)
### 4C What LIVE binds on the new page (status cards, chat, actuators)
### 4D What must never show (fake $, pretend COHERENT recon, mock bind lies)
### 4E CSS/HTML/JS file change list
## 5. Personality + conversation spec (system tone, multi-turn, voice/PTT optional)
## 6. MUST / SHOULD / NICE ranked table
## 7. Risks / Rollback / Honesty
## 8. Executive Summary (7 bullets)
## 9. Approval Checklist
DO NOT APPLY CODE.
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


def get_json(path: str, timeout: int = 45):
    try:
        with urllib.request.urlopen(BASE + path, context=CTX, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:  # noqa: BLE001
        return {"error": type(e).__name__, "msg": str(e)[:240]}


def _exists(rel: str) -> bool:
    return (REPO / rel).is_file()


def _head(rel: str, max_chars: int = 2800) -> str:
    path = REPO / rel
    if not path.is_file():
        return "(missing)"
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n... [{len(text) - max_chars} chars truncated]"


def build_audit() -> dict:
    build = {}
    try:
        build = json.loads((NR2 / "nr2-build.json").read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        build = {"error": str(exc)}

    files = {
        "opticalHalHtml": _exists("NewRidgeFinancial2/site/nr2-optical-page-hal.html"),
        "opticalHalJs": _exists("NewRidgeFinancial2/site/nr2-optical-page-hal.js"),
        "halPageJs": _exists("NewRidgeFinancial2/site/hal-page.js"),
        "halPageCanvas": _exists("NewRidgeFinancial2/site/hal-page-canvas.js"),
        "halChat9000": _exists("NewRidgeFinancial2/site/hal-chat-9000.js"),
        "halVoice": _exists("NewRidgeFinancial2/site/hal-voice.js"),
        "halRouteExec": _exists("NewRidgeFinancial2/site/hal-route-exec.js"),
        "halMemoIndex": _exists("NewRidgeFinancial2/site/hal-memo-index.js"),
        "halAgentJs": _exists("NewRidgeFinancial2/site/hal-agent.js"),
        "apexCoreJs": _exists("NewRidgeFinancial2/site/apex-core.js"),
        "webResearchPy": _exists("NewRidgeFinancial2/web_research.py"),
        "knowledgeMemory": _exists("NewRidgeFinancial2/knowledge_memory_store.py"),
        "halGateway": _exists("NewRidgeFinancial2/nr2_hal_gateway.py"),
        "softdentGuiExport": _exists("NewRidgeFinancial2/softdent_gui_export.py"),
        "qbConnector": _exists("NewRidgeFinancial2/qb_connector.py"),
    }

    optical_js = (SITE / "nr2-optical-page-hal.js").read_text(
        encoding="utf-8", errors="replace"
    ) if (SITE / "nr2-optical-page-hal.js").is_file() else ""
    optical_html = (SITE / "nr2-optical-page-hal.html").read_text(
        encoding="utf-8", errors="replace"
    ) if (SITE / "nr2-optical-page-hal.html").is_file() else ""

    code_signals = {
        "opticalPostsMessagesHistory": '"messages"' in optical_js,
        "opticalStreamTrue": '"stream": true' in optical_js or "stream: true" in optical_js,
        "opticalPostsQueryOnly": '{"query": queryOut, "stream": false}' in optical_js
        or "{ query: queryOut, stream: false }" in optical_js,
        "opticalMentionsMockReplies": "mock replies" in optical_html.lower(),
        "opticalHasPersonaMount": "hal-chat-9000" in optical_html
        or "hal-voice" in optical_html,
        "opticalBoardActionsBound": "board-actions" in optical_js,
        "opticalMemoUi": "memo" in optical_js.lower() or "remember" in optical_js.lower(),
        "opticalWebResearch": "web_research" in optical_js or "webResearch" in optical_js,
    }

    live = {
        "appInfo": get_json("/api/app-info", 20),
        "halStatus": get_json("/api/apex/hal/status", 30),
        "importReadiness": get_json("/api/import-readiness", 45),
        "claimsOutstanding": get_json("/api/softdent/claims-outstanding?limit=1", 45),
        "qbRevenue": get_json("/api/qb/monthly-revenue", 45),
        "browserSession": get_json("/api/browser-session", 20),
    }
    # recon may 500 — capture honestly
    live["reconciliationProbe"] = get_json("/api/apex/hal/reconciliation", 20)

    return {
        "build": build,
        "base": BASE,
        "operatorAsk": OPERATOR_REQUEST_VERBATIM,
        "filesPresent": files,
        "opticalCodeSignals": code_signals,
        "liveApis": live,
        "priorMoonshot": {
            "totalFunctionability": "MOONSHOT_TOTAL_FUNCTIONABILITY_2026-07-15.md (~23%)",
            "pageRecsBlocked": "MOONSHOT_HAL_PAGE_RECOMMENDATIONS_BLOCKED_2026-07-14.md",
            "chatboxBetter": "MOONSHOT_HAL_CHATBOX_BETTER_CONSULT_2026-07-11.md",
            "aiPmUpgrade": "MOONSHOT_AI_PROGRAM_MANAGER_UPGRADE_*",
        },
        "orphanedButPresentModules": [
            "site/hal-page.js",
            "site/hal-page-canvas.js",
            "site/hal-chat-9000.js",
            "site/hal-voice.js",
            "site/hal-route-exec.js",
            "site/hal-agent-loop.js",
            "site/hal-memo-index.js",
            "site/hal-cursor-parity.js",
            "web_research.py",
            "knowledge_memory_store.py",
        ],
        "removedCriticalForControlFeeling": [
            "site/apex-core.js",
            "site/hal-agent.js",
        ],
    }


def main() -> int:
    key_name, api_key, base_url = resolve_api_and_endpoint()
    if not api_key:
        blocker = DOCS / f"MOONSHOT_HAL_PROGRAMMING_REDESIGN_BLOCKED_{DATE}.md"
        blocker.write_text(
            "# Moonshot AI — HAL programming + redesign (BLOCKED)\n\n"
            f"**Date:** {DATE}\n"
            "**Status:** no API key in this environment\n\n"
            "## Operator request (verbatim)\n\n"
            f"> {OPERATOR_REQUEST_VERBATIM}\n\n"
            "## Blocker\n"
            "Neither `MOONSHOT_API_KEY` nor `OPENROUTER_API_KEY` / "
            "`KIMI_K2_API_KEY` is set.\n\n"
            "## Unblock (local)\n"
            "```bat\n"
            "cd /d C:\\Users\\mreno\\newridgefamilyfinancial\n"
            "python scripts\\run_moonshot_hal_programming_redesign_consult.py\n"
            "```\n",
            encoding="utf-8",
        )
        print("No API key", file=sys.stderr)
        print("Wrote", blocker)
        return 1

    if (api_key or "").startswith("sk-nv") or "moonshot.ai" in (base_url or "").lower():
        model = str(os.getenv("MOONSHOT_MODEL") or "kimi-k2.5").strip()
    else:
        model = str(
            os.getenv("MOONSHOT_MODEL")
            or os.getenv("KIMI_K2_MODEL")
            or "moonshotai/kimi-k2.5"
        ).strip()
    print(f"Using {key_name} @ {base_url} model={model}", flush=True)

    audit = build_audit()
    print("Audit built; live APIs probed.", flush=True)

    excerpts = []
    for name, lim in (
        ("MOONSHOT_TOTAL_FUNCTIONABILITY_2026-07-15.md", 3500),
        ("MOONSHOT_OPTICAL_LANDING_HAL_CHAT_2026-07-15.md", 2000),
        ("MOONSHOT_HAL_CHATBOX_BETTER_CONSULT_2026-07-11.md", 1800),
        ("MOONSHOT_HAL_VOICE_REPORT_CONSULT_2026-07-11.md", 1200),
    ):
        path = DOCS / name
        if path.is_file():
            excerpts.append(
                f"### {name}\n"
                f"{path.read_text(encoding='utf-8', errors='replace')[:lim]}"
            )

    file_excerpts = "\n\n".join(
        [
            f"### FILE: NewRidgeFinancial2/site/nr2-optical-page-hal.html\n"
            f"```html\n{_head('NewRidgeFinancial2/site/nr2-optical-page-hal.html', 3500)}\n```",
            f"### FILE: NewRidgeFinancial2/site/nr2-optical-page-hal.js\n"
            f"```js\n{_head('NewRidgeFinancial2/site/nr2-optical-page-hal.js', 3500)}\n```",
            f"### FILE: NewRidgeFinancial2/nr2-build.json\n"
            f"```json\n{_head('NewRidgeFinancial2/nr2-build.json', 800)}\n```",
        ]
    )

    user = (
        f"OPERATOR REQUEST (verbatim):\n{OPERATOR_REQUEST_VERBATIM}\n\n"
        f"LIVE CAPABILITY AUDIT JSON:\n```json\n"
        f"{json.dumps(audit, indent=2, default=str)[:32000]}\n```\n\n"
        f"CURRENT OPTICAL HAL FILES:\n{file_excerpts}\n\n"
        + (
            "PRIOR MOONSHOT EXCERPTS:\n" + "\n\n".join(excerpts)
            if excerpts
            else ""
        )
        + "\n\nReturn the markdown report only. CONSULT ONLY — do not apply code."
    )

    body = {
        "model": model,
        "temperature": 1 if "moonshot" in (base_url or "").lower() else 0.3,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
        "max_tokens": 12000,
    }
    url = base_url.rstrip("/")
    if not url.endswith("/chat/completions"):
        url = url + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if "openrouter" in url.lower():
        headers["HTTP-Referer"] = "https://github.com/NewRidgeFamilyFinancial"
        headers["X-Title"] = "NR2 HAL Programming + Redesign Consult"

    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=750) as resp:
            raw = json.loads(resp.read().decode("utf-8", "replace"))
        text = extract_message_content(raw) or ""
        status = "ok"
    except Exception as exc:  # noqa: BLE001
        print(f"Moonshot call failed: {exc}", file=sys.stderr)
        raw = {"error": str(exc)}
        text = f"Moonshot call failed: {exc}"
        status = "error"

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw_path = OUT / f"moonshot_hal_programming_redesign_{stamp}.json"
    md_path = DOCS / f"MOONSHOT_HAL_PROGRAMMING_REDESIGN_CONSULT_{DATE}.md"
    out_copy = OUT / f"MOONSHOT_HAL_PROGRAMMING_REDESIGN_CONSULT_{DATE}.md"
    raw_path.write_text(json.dumps(raw, indent=2)[:500000], encoding="utf-8")
    (OUT / f"moonshot_hal_programming_audit_{stamp}.json").write_text(
        json.dumps(audit, indent=2, default=str)[:200000], encoding="utf-8"
    )

    header = (
        f"# Moonshot AI — HAL programming review + page redesign (CONSULT ONLY)\n\n"
        f"**Date:** {DATE}\n"
        f"**Model:** `{model}`\n"
        f"**Key:** {key_name}\n"
        f"**Endpoint:** {url}\n"
        f"**Status:** {status}\n"
        f"**Build:** `{audit.get('build', {}).get('BUILD_ID', '?')}`\n"
        f"**Base:** `{BASE}`\n"
        f"**Script:** `scripts/run_moonshot_hal_programming_redesign_consult.py`\n"
        f"**Apply:** DO NOT APPLY until operator approves.\n\n"
        f"## Operator request (verbatim)\n\n"
        f"> {OPERATOR_REQUEST_VERBATIM}\n\n"
        f"---\n\n"
    )
    doc = header + (text.strip() or "_(empty Moonshot response)_") + "\n"
    md_path.write_text(doc, encoding="utf-8")
    out_copy.write_text(doc, encoding="utf-8")
    print("Wrote", md_path)
    print("Raw", raw_path)
    print("Status", status, "chars", len(text))
    return 0 if status == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
