"""Moonshot AI — how do we make HAL the brains of the program? (CONSULT ONLY).

Operator: tell moonshot i want hal to be the brains of the program how do we
do it report back.

PATH RULES (critical — prior consult invented invalid directories):
- Repo root is ONLY:
  C:\\Users\\mreno\\newridgefamilyfinancial
  NEVER C:\\NewRidgeFamilyFinancial (does not exist).
- HAL gateway is:
  NewRidgeFinancial2/nr2_hal_gateway.py
  NEVER NewRidgeFinancial2/gateway/routes/hal_gateway.py (does not exist).
- Cite only files that appear in VERIFIED_PATHS / LIVE AUDIT.
"""

from __future__ import annotations

import json
import os
import ssl
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Absolute repo root — do not invent alternates
REPO = Path(r"C:\Users\mreno\newridgefamilyfinancial")
if not REPO.is_dir():
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
    "tell moonshot i want hal to be the brains of the program how do we do it "
    "report back"
)

# Only these roots/files are valid — Moonshot must not invent others
VERIFIED_PATHS = {
    "repoRoot": str(REPO),
    "invalidRootsDoNotUse": [r"C:\NewRidgeFamilyFinancial"],
    "halGateway": "NewRidgeFinancial2/nr2_hal_gateway.py",
    "invalidGatewayDoNotUse": ["NewRidgeFinancial2/gateway/routes/hal_gateway.py"],
    "httpServer": "NewRidgeFinancial2/nr2_http_server.py",
    "apexBackend": "NewRidgeFinancial2/apex_backend.py",
    "opticalHalHtml": "NewRidgeFinancial2/site/nr2-optical-page-hal.html",
    "opticalHalJs": "NewRidgeFinancial2/site/nr2-optical-page-hal.js",
    "halPageJs": "NewRidgeFinancial2/site/hal-page.js",
    "halPageCanvas": "NewRidgeFinancial2/site/hal-page-canvas.js",
    "halChat9000": "NewRidgeFinancial2/site/hal-chat-9000.js",
    "halVoice": "NewRidgeFinancial2/site/hal-voice.js",
    "halRouteExec": "NewRidgeFinancial2/site/hal-route-exec.js",
    "halAgentLoop": "NewRidgeFinancial2/site/hal-agent-loop.js",
    "halMemoIndex": "NewRidgeFinancial2/site/hal-memo-index.js",
    "halDirector": "NewRidgeFinancial2/site/hal-director.js",
    "halOrchestrator": "NewRidgeFinancial2/site/hal-orchestrator.js",
    "halAutonomousOps": "NewRidgeFinancial2/site/hal-autonomous-ops.js",
    "webResearch": "NewRidgeFinancial2/web_research.py",
    "knowledgeMemory": "NewRidgeFinancial2/knowledge_memory_store.py",
    "softdentGuiExport": "NewRidgeFinancial2/softdent_gui_export.py",
    "qbConnector": "NewRidgeFinancial2/qb_connector.py",
    "buildJson": "NewRidgeFinancial2/nr2-build.json",
    "priorConsult": (
        "NewRidgeFinancial2/docs/MOONSHOT_HAL_PROGRAMMING_REDESIGN_CONSULT_2026-07-15.md"
    ),
    "totalFunctionability": (
        "NewRidgeFinancial2/docs/MOONSHOT_TOTAL_FUNCTIONABILITY_2026-07-15.md"
    ),
    "missingDoNotCite": [
        "NewRidgeFinancial2/site/apex-core.js",
        "NewRidgeFinancial2/site/hal-agent.js",
        "NewRidgeFinancial2/gateway/routes/hal_gateway.py",
    ],
}

SYSTEM = """You are Moonshot AI (kimi-k2 class) — principal architect for
NewRidgeFinancial2 (NR2). CONSULT ONLY — DO NOT APPLY CODE.

Operator (verbatim):
> tell moonshot i want hal to be the brains of the program how do we do it
> report back

Intent: Make HAL the **brains of the whole program** — central intelligence that
sees SoftDent + QuickBooks + MemoAI + web, converses multi-turn with strong
personality, and steers the optical program (navigation, ops, tools) within
honesty rules. Produce a concrete HOW plan and report.

CRITICAL PATH HYGIENE (operator complaint — you previously invented invalid dirs):
1) Repo root is ONLY the verified absolute path in AUDIT.repoRoot.
   NEVER write C:\\NewRidgeFamilyFinancial — that path DOES NOT EXIST.
2) HAL gateway file is ONLY NewRidgeFinancial2/nr2_hal_gateway.py.
   NEVER invent NewRidgeFinancial2/gateway/routes/hal_gateway.py.
3) Cite ONLY paths listed in AUDIT.verifiedPathsPresent (True) or VERIFIED_PATHS.
   If a path is missing/False, say UNAVAILABLE — do not invent replacements with
   made-up folder names. Prefer "create NEW file under NewRidgeFinancial2/site/
   or NewRidgeFinancial2/" with an explicit new name.
4) SoftDent export folder if mentioned: C:\\SoftDentReportExports (existing ops
   convention) — do not invent other SoftDent data roots unless in AUDIT.

HARD PRODUCT CONSTRAINTS:
- SoftDent: complete operator-grade READ + GUI Excel/Preview export + teach +
  consent-queue only. NO silent SoftDent write-back.
- QuickBooks: full READ + sync + consent journal push. NO silent posting.
- empty ≠ $0. PHI local. Cloud HAL denied. CSP script-src 'self'.
- Optical clean-slate: live face is nr2-optical-page-hal.html/.js.
  apex-core.js and hal-agent.js are REMOVED — do not plan as if they exist.
- Prefer remounting EXISTING modules (hal-route-exec, board-actions, MemoAI,
  web_research, chat-9000 persona, agent-loop) INTO the optical HAL page.

"BRAINS OF THE PROGRAM" definition for this consult:
HAL is the single operator-facing intelligence that:
1) Holds multi-turn conversation + personality
2) Grounds answers in live SoftDent/QB/import-readiness (honest)
3) Uses MemoAI + web as tools
4) Can navigate and trigger program actions (board-actions / route-exec) with
   consent where needed
5) Owns the impressive HAL command-center page as its home
NOT: silent SoftDent/QB tyrant; NOT: duplicate Apex SPA restore for its own sake

Prior redesign consult already mapped gaps (single-turn optical, unwired tools,
thin CRT page). This consult must answer HOW to make HAL the brains — architecture
and sequenced build — not repeat "there is a gap" without a HOW.

OUTPUT (strict markdown):
# Verdict — how HAL becomes the brains
## 0. Operator Intent
## 1. Target architecture (HAL as central brain — components + data/control flows)
## 2. Path hygiene confirmation (list real files only; call out forbidden invalid paths)
## 3. How we do it — sequenced plan (P0→P3) with ONLY verified/new explicit paths
## 4. Control surfaces HAL must own (chat, tools, board-actions, sync, SoftDent export, QB read, MemoAI, web)
## 5. SoftDent/QB "brains access" doctrine (MAY vs MUST NOT)
## 6. Optical HAL page as brain UI (bind list; no fake $)
## 7. MUST / SHOULD / NICE
## 8. Risks / Rollback
## 9. Executive Summary (7 bullets)
## 10. Approval Checklist
DO NOT APPLY CODE. DO NOT invent directories.
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


def _head(rel: str, max_chars: int = 2400) -> str:
    path = REPO / rel
    if not path.is_file():
        return f"(MISSING — do not invent this path: {rel})"
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n... [{len(text) - max_chars} chars truncated]"


def build_audit() -> dict:
    present = {}
    for key, rel in VERIFIED_PATHS.items():
        if key in ("repoRoot", "invalidRootsDoNotUse", "invalidGatewayDoNotUse", "missingDoNotCite"):
            continue
        if isinstance(rel, str) and not rel.startswith("C:"):
            present[rel] = (REPO / rel).is_file()

    for bad in VERIFIED_PATHS["missingDoNotCite"]:
        present[bad] = (REPO / bad).is_file()

    build = {}
    try:
        build = json.loads((NR2 / "nr2-build.json").read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        build = {"error": str(exc)}

    optical_js = ""
    js_path = SITE / "nr2-optical-page-hal.js"
    if js_path.is_file():
        optical_js = js_path.read_text(encoding="utf-8", errors="replace")

    return {
        "repoRoot": str(REPO),
        "repoRootExists": REPO.is_dir(),
        "invalidRoot_C_NewRidgeFamilyFinancial_exists": Path(
            r"C:\NewRidgeFamilyFinancial"
        ).exists(),
        "operatorAsk": OPERATOR_REQUEST_VERBATIM,
        "build": build,
        "base": BASE,
        "verifiedPathsPresent": present,
        "verifiedPathsManifest": VERIFIED_PATHS,
        "opticalSignals": {
            "postsMessagesHistory": '"messages"' in optical_js,
            "streamTrue": "stream: true" in optical_js or '"stream": true' in optical_js,
            "queryOnlySingleTurn": "stream: false" in optical_js
            or '"stream": false' in optical_js,
            "boardActionsInOpticalJs": "board-actions" in optical_js,
            "memoInOpticalJs": "memo" in optical_js.lower(),
            "webInOpticalJs": "web_research" in optical_js or "webResearch" in optical_js,
        },
        "liveApis": {
            "appInfo": get_json("/api/app-info", 20),
            "halStatus": get_json("/api/apex/hal/status", 30),
            "importReadiness": get_json("/api/import-readiness", 45),
            "claimsOutstanding": get_json("/api/softdent/claims-outstanding?limit=1", 45),
            "qbRevenue": get_json("/api/qb/monthly-revenue", 45),
            "browserSession": get_json("/api/browser-session", 20),
        },
        "pathComplaint": (
            "Operator said prior advice used invalid directory names. "
            "Confirmed: C:\\NewRidgeFamilyFinancial does NOT exist. "
            "Confirmed: NewRidgeFinancial2/gateway/routes/hal_gateway.py does NOT exist. "
            "Real gateway: NewRidgeFinancial2/nr2_hal_gateway.py. "
            "Real root: C:\\Users\\mreno\\newridgefamilyfinancial"
        ),
    }


def main() -> int:
    key_name, api_key, base_url = resolve_api_and_endpoint()
    if not api_key:
        blocker = DOCS / f"MOONSHOT_HAL_BRAINS_OF_PROGRAM_BLOCKED_{DATE}.md"
        blocker.write_text(
            "# Moonshot AI — HAL brains of program (BLOCKED)\n\n"
            f"**Date:** {DATE}\n"
            f"**Repo root:** `{REPO}`\n"
            "**Status:** no API key\n\n"
            f"> {OPERATOR_REQUEST_VERBATIM}\n\n"
            "Set MOONSHOT_API_KEY / OPENROUTER_API_KEY and rerun:\n"
            f"`python {REPO / 'scripts' / 'run_moonshot_hal_brains_of_program_consult.py'}`\n",
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
    print(f"Repo root: {REPO}", flush=True)

    audit = build_audit()
    print("Audit built.", flush=True)

    excerpts = []
    for name, lim in (
        ("MOONSHOT_HAL_PROGRAMMING_REDESIGN_CONSULT_2026-07-15.md", 4000),
        ("MOONSHOT_TOTAL_FUNCTIONABILITY_2026-07-15.md", 2500),
    ):
        path = DOCS / name
        if path.is_file():
            excerpts.append(
                f"### {name}\n"
                f"{path.read_text(encoding='utf-8', errors='replace')[:lim]}"
            )

    file_excerpts = "\n\n".join(
        [
            f"### FILE: NewRidgeFinancial2/nr2_hal_gateway.py\n"
            f"```python\n{_head('NewRidgeFinancial2/nr2_hal_gateway.py', 2800)}\n```",
            f"### FILE: NewRidgeFinancial2/site/nr2-optical-page-hal.js\n"
            f"```js\n{_head('NewRidgeFinancial2/site/nr2-optical-page-hal.js', 2800)}\n```",
            f"### FILE: NewRidgeFinancial2/site/nr2-optical-page-hal.html\n"
            f"```html\n{_head('NewRidgeFinancial2/site/nr2-optical-page-hal.html', 2200)}\n```",
            f"### FILE: NewRidgeFinancial2/nr2-build.json\n"
            f"```json\n{_head('NewRidgeFinancial2/nr2-build.json', 600)}\n```",
        ]
    )

    user = (
        f"OPERATOR REQUEST (verbatim):\n{OPERATOR_REQUEST_VERBATIM}\n\n"
        f"PATH HYGIENE (must obey):\n"
        f"- Real repo root: {REPO}\n"
        f"- Invalid root (MISSING): C:\\NewRidgeFamilyFinancial\n"
        f"- Real HAL gateway: NewRidgeFinancial2/nr2_hal_gateway.py\n"
        f"- Invalid gateway (MISSING): NewRidgeFinancial2/gateway/routes/hal_gateway.py\n\n"
        f"LIVE AUDIT JSON:\n```json\n"
        f"{json.dumps(audit, indent=2, default=str)[:30000]}\n```\n\n"
        f"VERIFIED FILE EXCERPTS:\n{file_excerpts}\n\n"
        + (
            "PRIOR CONSULT EXCERPTS (path errors in prior Moonshot text — ignore invented paths):\n"
            + "\n\n".join(excerpts)
            if excerpts
            else ""
        )
        + "\n\nReturn markdown only. CONSULT ONLY. Real paths only."
    )

    body = {
        "model": model,
        "temperature": 1 if "moonshot" in (base_url or "").lower() else 0.25,
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
        headers["X-Title"] = "NR2 HAL Brains Of Program Consult"

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

    # Fail closed if Moonshot invents bad paths again
    banned = (
        r"C:\NewRidgeFamilyFinancial",
        "C:/NewRidgeFamilyFinancial",
        "gateway/routes/hal_gateway",
    )
    hygiene = "ok"
    for b in banned:
        if b.lower() in text.lower():
            hygiene = "FAILED — response cites invalid directory; see note below"
            text += (
                "\n\n---\n**PATH HYGIENE FLAG:** Response still mentioned "
                f"`{b}`. Treat that path as INVALID. Real root: "
                f"`{REPO}`. Real gateway: `NewRidgeFinancial2/nr2_hal_gateway.py`.\n"
            )
            break

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw_path = OUT / f"moonshot_hal_brains_of_program_{stamp}.json"
    md_path = DOCS / f"MOONSHOT_HAL_BRAINS_OF_PROGRAM_CONSULT_{DATE}.md"
    out_copy = OUT / f"MOONSHOT_HAL_BRAINS_OF_PROGRAM_CONSULT_{DATE}.md"
    raw_path.write_text(json.dumps(raw, indent=2)[:500000], encoding="utf-8")
    (OUT / f"moonshot_hal_brains_audit_{stamp}.json").write_text(
        json.dumps(audit, indent=2, default=str)[:200000], encoding="utf-8"
    )

    header = (
        f"# Moonshot AI — HAL as brains of the program (CONSULT ONLY)\n\n"
        f"**Date:** {DATE}\n"
        f"**Model:** `{model}`\n"
        f"**Key:** {key_name}\n"
        f"**Endpoint:** {url}\n"
        f"**Status:** {status}\n"
        f"**Path hygiene:** {hygiene}\n"
        f"**Repo root (verified):** `{REPO}`\n"
        f"**Build:** `{audit.get('build', {}).get('BUILD_ID', '?')}`\n"
        f"**Base:** `{BASE}`\n"
        f"**Script:** `scripts/run_moonshot_hal_brains_of_program_consult.py`\n"
        f"**Apply:** DO NOT APPLY until operator approves.\n\n"
        f"## Operator request (verbatim)\n\n"
        f"> {OPERATOR_REQUEST_VERBATIM}\n\n"
        f"## Path hygiene note\n\n"
        f"- Valid root: `{REPO}`\n"
        f"- Invalid root (does not exist): `C:\\NewRidgeFamilyFinancial`\n"
        f"- Valid gateway: `NewRidgeFinancial2/nr2_hal_gateway.py`\n"
        f"- Invalid gateway (does not exist): "
        f"`NewRidgeFinancial2/gateway/routes/hal_gateway.py`\n\n"
        f"---\n\n"
    )
    doc = header + (text.strip() or "_(empty Moonshot response)_") + "\n"
    md_path.write_text(doc, encoding="utf-8")
    out_copy.write_text(doc, encoding="utf-8")
    print("Wrote", md_path)
    print("Status", status, "hygiene", hygiene, "chars", len(text))
    return 0 if status == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
