"""Moonshot AI — What's next after polish Package 10 + executive E1–E4.

CONSULT ONLY — operator said: next
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

OPERATOR_REQUEST_VERBATIM = "next"

SYSTEM = """You are Moonshot AI — principal architect for NewRidgeFinancial2 (NR2).
CONSULT ONLY — DO NOT APPLY CODE.

Operator said (verbatim): next

JUST CLOSED on main (156f116 Package 10 beam bus):
Functional polish COMPLETE: P1–P10 (ops gates, PHI glass, breadcrumbs, loading,
tablet, motion, focus/a11y, soft-fail, print redaction, sessionStorage beam bus).
Visual COMPLETE: less-sterile V1–V6 instrument glass (dd8883c) + high-executive
E1–E4 (84a0b74) letterhead, currency emboss, desk surface, Landing/HAL/Hub convergence.

UI polish roadmaps are exhausted. Operator wants THE single best NEXT package —
may be ops/data, SoftDent, Trellis, Claims workflow, HAL, or a NEW polish layer
ONLY if live audit proves a real remaining gap (not re-skin).

HARD CONSTRAINTS:
- SoftDent READ-ONLY; empty ≠ $0; board PHI initials+hash
- SoftDent Output Options: Excel OR Print Preview only — NEVER File, NEVER Printer
- No SoftDent write-back; no third-party chat embeds; no React rewrite
- Do NOT flip forceCloseAvailable true until pilot cutover attestation
- Do NOT invent SoftDent Excel drops or Select File Name directories
- Do NOT redo P1–P10, V1–V6, E1–E4

YOUR JOB: Pick THE single best NEXT package + ordered backlog (2–4).

CANDIDATE LANES (pick ONE as #1 from LIVE AUDIT — justify with real paths):
1) Ops: attended morning_bundle / SoftDent Excel enablement (if still RED)
2) Trellis: withBenefits AM proof / nightly scrape monitoring
3) Claims workflow: age buckets, payer backfill, ERA inbox, paid-suppress honesty
4) HAL: desk smoke / this-patient / SoftDent teach lane
5) Pilot / shadow clock / force-close attestation path
6) NEW polish layer ONLY if audit shows concrete remaining UX gap vs acceptance
7) Something else justified ONLY from LIVE AUDIT — real NewRidgeFinancial2/ paths

OUTPUT (strict markdown):
# Verdict (one sentence)
## 0. Operator Intent (verbatim)
## 1. Recommended NEXT (name, why now, effort S/M/L, REAL files, validation gate)
## 2. Ordered backlog AFTER #1 (2–4)
## 3. Why this beats the other candidates now
## 4. What NOT to redo
## 5. Acceptance criteria
## 6. Executive Summary (5 bullets)
## 7. Approval Checklist
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


def get_json(path: str, timeout: int = 8):
    try:
        with urllib.request.urlopen(BASE + path, context=CTX, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:  # noqa: BLE001
        return {"error": type(e).__name__, "msg": str(e)[:240]}


def _snippet(path: Path, needles: list[str], head: int = 0) -> dict:
    if not path.is_file():
        return {"path": str(path), "exists": False}
    text = path.read_text(encoding="utf-8", errors="replace")
    out = {
        "path": path.name,
        "exists": True,
        "bytes": len(text.encode("utf-8", "replace")),
        "hits": {n: (n in text) for n in needles},
    }
    if head > 0:
        out["head"] = text[:head]
    return out


def live_audit() -> dict:
    theme = SITE / "nr2-optical-theme.css"
    wire = SITE / "nr2-optical-page-wire.js"
    nav = SITE / "nr2-optical-nav.js"
    live = {
        "importReadiness": get_json("/api/import-readiness", 10),
        "moneyBeams": get_json("/api/money-beams", 10),
        "morningBundle": get_json("/api/morning-bundle/status", 10),
        "trellisAm": get_json("/api/trellis/am-proof", 10),
        "pilotShadow": get_json("/api/pilot-shadow/status", 10),
        "claimsOutstanding": get_json("/api/softdent/claims-outstanding?limit=5", 12),
        "arAging": get_json("/api/softdent/ar-aging", 10),
    }
    # Compact live errors / key flags only
    live_compact = {}
    for k, v in live.items():
        if not isinstance(v, dict):
            live_compact[k] = v
            continue
        if v.get("error"):
            live_compact[k] = {"error": v.get("error"), "msg": v.get("msg")}
            continue
        slim = {}
        for key in (
            "ok",
            "hasData",
            "importStale",
            "forceCloseAvailable",
            "withBenefits",
            "status",
            "days",
            "shadowDay",
            "bundleOk",
            "excelEnablementGate",
            "lasers",
            "count",
            "totalOutstanding",
            "total",
            "beamHash",
            "stale",
            "message",
            "reason",
        ):
            if key in v:
                slim[key] = v[key]
        # nested common shapes
        for nest in ("morningBundle", "trellis", "pilotShadow", "gates", "summary"):
            if nest in v and isinstance(v[nest], dict):
                slim[nest] = {
                    nk: v[nest][nk]
                    for nk in list(v[nest].keys())[:12]
                    if nk
                    in (
                        "ok",
                        "status",
                        "withBenefits",
                        "days",
                        "shadowDay",
                        "excelEnablementGate",
                        "forceCloseAvailable",
                        "message",
                        "reason",
                        "red",
                        "yellow",
                        "green",
                    )
                    or True
                }
                # keep slim nests small
                slim[nest] = dict(list(slim[nest].items())[:16])
        live_compact[k] = slim or {"keys": list(v.keys())[:20]}

    return {
        "repoRoot": str(REPO),
        "operatorAsk": OPERATOR_REQUEST_VERBATIM,
        "justClosed": {
            "commit": "156f116",
            "package": "P10 beam bus",
            "alsoShipped": [
                "P1–P9 functional polish",
                "V1–V6 instrument glass (dd8883c)",
                "E1–E4 high executive (84a0b74)",
            ],
        },
        "sharedMarkers": {
            "nav": _snippet(
                nav,
                [
                    "persistBeamState",
                    "restoreBeamState",
                    "bindBeamBusScroll",
                    "nr2.optical.beamBus",
                    "focusPageHeading",
                ],
            ),
            "wire": _snippet(
                wire,
                [
                    "setErrorState",
                    "bindPrintHygiene",
                    "trapFocus",
                    "bootAtmosphere",
                    "exec-letterhead",
                ],
            ),
            "theme": _snippet(
                theme,
                [
                    "exec-letterhead",
                    "exec-desk-surface",
                    "exec-currency",
                    "beam-sweep",
                    "@media print",
                    "nr2-print-redacted",
                    "prefers-reduced-motion",
                ],
            ),
        },
        "liveCompact": live_compact,
        "siteInventory": {
            "html": sorted(p.name for p in SITE.glob("nr2-optical*.html")),
            "jsBytes": {
                p.name: p.stat().st_size
                for p in sorted(SITE.glob("nr2-optical*.js"))
                if p.is_file()
            },
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
            "X-Title": "NR2 Moonshot whats-next after polish P10",
        },
    )
    with urllib.request.urlopen(req, context=CTX, timeout=120) as r:
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
    (OUT / f"moonshot_whats_next_after_polish_p10_audit_{stamp}.json").write_text(
        json.dumps(audit, indent=2), encoding="utf-8"
    )
    user = (
        "LIVE AUDIT JSON follows. UI polish P1–P10 + V1–V6 + E1–E4 just closed. "
        "Pick THE single best NEXT package (ops or product — not a re-skin).\n\n"
        + json.dumps(audit, indent=2)[:90000]
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
    report = DOCS / f"MOONSHOT_WHATS_NEXT_AFTER_POLISH_P10_{DATE}.md"
    header = (
        f"# Moonshot AI — What's Next After Polish P10 + Executive E1–E4 (CONSULT ONLY)\n\n"
        f"**Date:** {DATE}\n"
        f"**Model:** `{meta.get('model')}`\n"
        f"**Key:** {key_name}\n"
        f"**Script:** `scripts/run_moonshot_whats_next_after_polish_p10_consult.py`\n"
        f"**Apply:** Operator must say continue / approve before Cursor applies.\n\n"
        f"## Operator request (verbatim)\n\n"
        f"> {OPERATOR_REQUEST_VERBATIM}\n\n"
        f"---\n\n"
    )
    report.write_text(header + content.strip() + "\n", encoding="utf-8")
    (OUT / f"moonshot_whats_next_after_polish_p10_{stamp}.json").write_text(
        json.dumps({"meta": meta, "content": content}, indent=2), encoding="utf-8"
    )
    print(report)
    print("---")
    try:
        print(content[:6000])
    except UnicodeEncodeError:
        print(content[:6000].encode("ascii", "replace").decode("ascii"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
