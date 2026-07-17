"""Moonshot — What's next after PMS eval continue (Excel hold + ERA SOP) (CONSULT ONLY).

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
- NR2 is a financial overlay on SoftDent+QB — not a full PMS (see MOONSHOT_NR2_VS_CLOUD_DENTAL_PMS_EVALUATION_2026-07-17.md).
- SoftDent Excel GREY = intentional extract block across Output Options reports. Preview optical-only.
  Hold protocol APPLIED: softdent_excel_grey_hold_protocol_nr2.md. Do NOT pick SoftDent Excel GUI
  un-grey as a Cursor code package. Operator/Carestream attended only.
- ERA drop SOP hardened (P0-C). Live inbox still realFileCount=0 (README placeholder). Empty ≠ $0.
- Trellis withBenefits WAIT ~2026-07-20. forceClose false. Shadow Day ~2 of 30.
- Continue APPLIED f9ad6da: hold protocol + ERA runbook + PMS eval report. Do not redo.

YOUR JOB: Pick THE single best NEXT Cursor can APPLY NOW in code/docs, OR honest WAIT/ATTENDED.
Prefer product value from LIVE AUDIT. Do not recommend Preview-as-money or SoftDent write-back.

CANDIDATES (pick ONE #1):
1) WAIT/ATTENDED — SoftDent Excel Carestream (hold already documented)
2) WAIT — real ERA .835 from payer (SOP ready; no file yet)
3) WAIT — Trellis withBenefits ~2026-07-20
4) Claims↔QB money-gap optical honesty package — surface SoftDent AR vs QB revenue delta with
   empty≠$0 labeling (LIVE AUDIT ~$52,270 vs ~$78,399) without inventing reconciliation
5) Supervised-pilot prep docs/workflows for Day 30 (no forceClose flip)
6) Something else ONLY from LIVE AUDIT — real NewRidgeFinancial2/ paths

HARD CONSTRAINTS:
- SoftDent READ-ONLY; empty ≠ $0; PHI initials+hash; never Printer/File
- No Preview money invent; no fake 835/withBenefits; no forceClose flip; no React/chat embeds

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
    era_files = sorted(p.name for p in era_drop.iterdir() if p.is_file())[:12] if era_drop.is_dir() else []
    sd = (beams.get("softdent") or {}) if isinstance(beams, dict) else {}
    qb = (beams.get("quickbooks") or {}) if isinstance(beams, dict) else {}
    gap = None
    try:
        if isinstance(sd, dict) and isinstance(qb, dict):
            a = float(sd.get("totalOutstanding") or 0)
            b = float(qb.get("monthlyRevenue") or 0)
            gap = {"softdentAR": a, "qbRevenue": b, "rawDelta": round(b - a, 2), "note": "different metrics — not auto-reconcile"}
    except Exception:
        gap = None
    return {
        "justApplied": "f9ad6da SoftDent Excel hold + ERA SOP + PMS eval report",
        "softdentExcelGreyHold": True,
        "holdProtocol": "NewRidgeFinancial2/docs/runbooks/softdent_excel_grey_hold_protocol_nr2.md",
        "eraRunbook": "NewRidgeFinancial2/docs/runbooks/era_835_inbox_drop_nr2.md",
        "pmsEval": "NewRidgeFinancial2/docs/MOONSHOT_NR2_VS_CLOUD_DENTAL_PMS_EVALUATION_2026-07-17.md",
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
            "ok": beams.get("ok"),
            "softdent": sd.get("display") if isinstance(sd, dict) else None,
            "quickbooks": qb.get("display") if isinstance(qb, dict) else None,
            "metricGapNote": gap,
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
        "opticalMoneyPages": [
            "nr2-optical-page-quickbooks.html",
            "nr2-optical-page-softdent.html",
            "nr2-optical-page-ar.html",
            "nr2-optical-page-office-manager.html",
        ],
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
            "X-Title": "NR2 Moonshot next after PMS eval continue",
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
    (OUT / f"moonshot_whats_next_after_pms_eval_continue_audit_{stamp}.json").write_text(
        json.dumps(audit, indent=2, default=str), encoding="utf-8"
    )
    user = (
        "LIVE AUDIT. Excel hold + ERA SOP done. Pick Cursor-apply NEXT or honest WAIT.\n\n"
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
    report = DOCS / f"MOONSHOT_WHATS_NEXT_AFTER_PMS_EVAL_CONTINUE_{DATE}.md"
    header = (
        f"# Moonshot AI — What's Next After PMS Eval Continue (CONSULT ONLY)\n\n"
        f"**Date:** {DATE}\n"
        f"**Model:** `{meta.get('model')}`\n"
        f"**Key:** {key_name}\n"
        f"**Script:** `scripts/run_moonshot_whats_next_after_pms_eval_continue_consult.py`\n"
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
