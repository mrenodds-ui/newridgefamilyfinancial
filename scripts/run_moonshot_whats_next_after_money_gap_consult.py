"""Moonshot — What's next after money-gap optical honesty (CONSULT ONLY).

Operator: next
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
OUT.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)
DATE = datetime.now(timezone.utc).strftime("%Y-%m-%d")

CTX = ssl._create_unverified_context()
BASE = os.getenv("NR2_BROWSER", "https://127.0.0.1:8765").rstrip("/")

OPERATOR_REQUEST_VERBATIM = "next"

SYSTEM = """You are Moonshot AI — principal architect for NewRidgeFinancial2 (NR2).
CONSULT ONLY — DO NOT APPLY CODE.

Operator said (verbatim): next

HARD FACTS:
- Money-gap optical honesty APPLIED (1f2f76b): metricGapHonesty on money-beams; hub/HAL/
  nr2-optical-page-money-gap.html show SoftDent AR vs QB revenue as Different Metrics —
  Not Auto-Reconciled; no Reconcile CTA; empty ≠ $0. Do NOT redo.
- SoftDent Excel GREY = intentional extract block. Hold protocol already documented.
  Do NOT pick SoftDent Excel GUI un-grey as Cursor code. Carestream/operator attended only.
  Resume phrase when ready: Excel is clickable — run morning bundle
- SoftDent operator HARD STOP still active until explicit resume SoftDent / lift SoftDent stop.
- ERA drop SOP ready; live inbox realFileCount=0 (README placeholder). Empty ≠ $0. No fake 835.
- Trellis withBenefits WAIT ~2026-07-20. forceClose false. Shadow Day early (~2 of 30).
- NR2 is SoftDent+QB financial overlay — not a full cloud PMS replacement.

YOUR JOB: Pick THE single best NEXT Cursor can APPLY NOW in code/docs, OR honest WAIT/ATTENDED.
Prefer product value from LIVE AUDIT. Do not recommend Preview-as-money or SoftDent write-back.
If every productive Cursor path is blocked on external/attended inputs, recommend WAIT clearly.

CANDIDATES (pick ONE #1):
1) WAIT/ATTENDED — SoftDent Excel Carestream (hold already documented; SoftDent hard stop)
2) WAIT — real ERA .835 from payer (SOP ready; no file yet)
3) WAIT — Trellis withBenefits ~2026-07-20
4) Supervised-pilot prep docs/workflows for Day 30 approach (no forceClose flip; shadow early)
5) Something else ONLY from LIVE AUDIT — real NewRidgeFinancial2/ paths — must not redo money-gap,
   Excel hold, ERA SOP, or invent reconcile/Preview money

HARD CONSTRAINTS:
- SoftDent READ-ONLY; empty ≠ $0; PHI initials+hash; never Printer/File
- No Preview money invent; no fake 835/withBenefits; no forceClose flip; no React/chat embeds
- Do not touch SoftDent GUI while hard stop is active

OUTPUT (strict markdown):
# Verdict (one sentence)
## 0. Operator Intent (verbatim)
## 1. Recommended NEXT (name, why now, effort, REAL files, validation gate)
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


def get_json(path: str, timeout: int = 12):
    try:
        with urllib.request.urlopen(BASE + path, context=CTX, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:  # noqa: BLE001
        return {"error": type(e).__name__, "msg": str(e)[:240]}


def live_audit() -> dict:
    am = get_json("/api/trellis/am-proof")
    claims = get_json("/api/softdent/claims-outstanding?limit=5")
    era = get_json("/api/apex/hal/era-inbox/status")
    beams = get_json("/api/hal/tools/money-beams")
    pcs = get_json("/api/hal/tools/period-close-status")
    ready = get_json("/api/import-readiness")
    app = get_json("/api/app-info")
    mb = pcs.get("morningBundle") if isinstance(pcs, dict) else None
    pilot = app.get("pilot") if isinstance(app, dict) else None
    era_drop = REPO / "app_data" / "nr2" / "office" / "era_inbox" / "drop"
    era_files = (
        sorted(p.name for p in era_drop.iterdir() if p.is_file())[:12] if era_drop.is_dir() else []
    )
    sd = (beams.get("softdent") or {}) if isinstance(beams, dict) else {}
    qb = (beams.get("quickbooks") or {}) if isinstance(beams, dict) else {}
    gap = beams.get("metricGapHonesty") if isinstance(beams, dict) else None
    return {
        "justApplied": "1f2f76b money-gap optical honesty (metricGapHonesty + money-gap page)",
        "appliedDoc": "NewRidgeFinancial2/docs/MOONSHOT_MONEY_GAP_OPTICAL_HONESTY_APPLIED_2026-07-17.md",
        "softdentExcelGreyHold": True,
        "softdentOperatorHardStop": True,
        "holdProtocol": "NewRidgeFinancial2/docs/runbooks/softdent_excel_grey_hold_protocol_nr2.md",
        "eraRunbook": "NewRidgeFinancial2/docs/runbooks/era_835_inbox_drop_nr2.md",
        "moneyGapPage": "NewRidgeFinancial2/site/nr2-optical-page-money-gap.html",
        "trellisAm": {
            "passed": am.get("passed"),
            "chipStatus": am.get("chipStatus"),
            "withBenefits": am.get("withBenefits"),
        },
        "trellisWaitUntil": "~2026-07-20",
        "morningBundle": {
            "ok": (mb or {}).get("ok") if isinstance(mb, dict) else mb,
            "failed": (mb or {}).get("failed") if isinstance(mb, dict) else None,
            "okCount": (mb or {}).get("okCount") if isinstance(mb, dict) else None,
        },
        "moneyBeams": {
            "ok": beams.get("ok") if isinstance(beams, dict) else None,
            "softdent": sd.get("display") if isinstance(sd, dict) else None,
            "quickbooks": qb.get("display") if isinstance(qb, dict) else None,
            "metricGapHonesty": gap,
        },
        "claims": {
            "count": claims.get("count"),
            "totalOutstanding": claims.get("totalOutstanding"),
            "error": claims.get("error"),
        },
        "eraInbox": era if isinstance(era, dict) else {"raw": str(era)[:200]},
        "eraDropFiles": era_files,
        "pilot": pilot,
        "importBlocking": ready.get("blocking") if isinstance(ready, dict) else None,
        "resumePhrases": {
            "softdentExcel": "Excel is clickable — run morning bundle",
            "era": "ERA 835 dropped — verify GREEN",
            "softDentHardStop": "resume SoftDent / lift SoftDent stop",
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
            "X-Title": "NR2 Moonshot next after money-gap honesty",
        },
    )
    with urllib.request.urlopen(req, context=CTX, timeout=240) as r:
        raw = json.loads(r.read().decode("utf-8", "replace"))
    return extract_message_content(raw), {"model": model, "rawKeys": list(raw.keys())}


def main() -> int:
    print("RESOLVE_API…", flush=True)
    key_name, api_key, base = resolve_api_and_endpoint()
    if not api_key:
        print("NO_API_KEY", file=sys.stderr)
        return 2
    print("AUDIT…", flush=True)
    audit = live_audit()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (OUT / f"moonshot_whats_next_after_money_gap_audit_{stamp}.json").write_text(
        json.dumps(audit, indent=2, default=str), encoding="utf-8"
    )
    user = (
        "LIVE AUDIT. Money-gap honesty done (1f2f76b). Pick Cursor-apply NEXT or honest WAIT.\n\n"
        + json.dumps(audit, indent=2, default=str)[:90000]
    )
    print(f"CHAT… endpoint={base[:48]}…", flush=True)
    try:
        content, meta = chat(SYSTEM, user, api_key, base)
    except Exception as exc:  # noqa: BLE001
        print(f"CHAT_FAIL: {exc}", file=sys.stderr)
        return 1
    if not content.strip():
        print("EMPTY_RESPONSE", file=sys.stderr)
        return 1
    report = DOCS / f"MOONSHOT_WHATS_NEXT_AFTER_MONEY_GAP_{DATE}.md"
    header = (
        f"# Moonshot AI — What's Next After Money-Gap Optical Honesty (CONSULT ONLY)\n\n"
        f"**Date:** {DATE}\n"
        f"**Model:** `{meta.get('model')}`\n"
        f"**Key:** {key_name}\n"
        f"**Script:** `scripts/run_moonshot_whats_next_after_money_gap_consult.py`\n"
        f"**Prior APPLIED:** `MOONSHOT_MONEY_GAP_OPTICAL_HONESTY_APPLIED_2026-07-17.md` (`1f2f76b`)\n"
        f"**Apply:** Operator must say continue / approve before Cursor applies.\n\n"
        f"## Operator request (verbatim)\n\n"
        f"> {OPERATOR_REQUEST_VERBATIM}\n\n"
        f"---\n\n"
    )
    report.write_text(header + content.strip() + "\n", encoding="utf-8")
    print(report)
    print("---")
    try:
        print(content[:7000])
    except UnicodeEncodeError:
        print(content[:7000].encode("ascii", "replace").decode("ascii"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
