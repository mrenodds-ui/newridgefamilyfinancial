"""Moonshot — What's next after SoftDent grey-Excel universal pull-block truth (CONSULT ONLY).

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

HARD SOFTDENT TRUTH (operator + Carestream Help — do not contradict):
- SoftDent Output Options Excel greyed = SoftDent INTENTIONALLY blocking extractable data pulls.
- That gate can apply ACROSS ALL SoftDent reports that use Output Options (not just collections).
- When Excel is grey: ONLY Print Preview for optical/visual reading. Never invent dollars from Preview.
- Never Printer, never SoftDent File. Money-beam Excel ingest waits until SoftDent re-enables Excel.
- Carestream SoftDent Help: Running Reports always hits Output Options; Excel is an Output Option when
  SoftDent offers it (registers, account lists, recall, user-selected, etc.).
- Live probe 2026-07-17: Excel greyed on Account Aging AND Collection Summary; quitting Excel did not
  un-grey. Attended morning_bundle refresh BLOCKED. Prior morningBundle.ok=true (aging+register Excel
  from earlier when Excel was clickable) still the money-beam truth — do not overwrite with Preview.
- Runbook: NewRidgeFinancial2/docs/runbooks/softdent_excel_enablement_nr2.md (commits through 8084d2b).

ALREADY APPLIED (do not redo):
- Viewport P1–4 + Hub; morning bundle Track B; collections excel-greyed harden; claims honesty;
  HAL desk smoke; pilot shadow Day X of 30 hygiene; SoftDent grey-Excel optical-only docs.

OTHER GATES:
- Trellis withBenefits WAIT until ~2026-07-20 1AM/2AM — do not invent ClearCoverage benefits.
- ERA inbox: README placeholder only (empty ≠ $0) until real .835 arrives.
- forceCloseAvailable stays false; shadow Day ~2 of 30.
- UI polish CLOSED — no reskin.

YOUR JOB: Pick THE single best NEXT. SoftDent Excel un-grey is ATTENDED OPS (Carestream/operator),
not Cursor code. Prefer the best implementable package OR honest WAIT / ATTENDED OPS.

CANDIDATES (pick ONE #1):
1) SoftDent Excel enablement ATTENDED OPS — operator/Carestream make Excel clickable on Output Options
   (any report), then morning_bundle_attended --yes --refresh-close. Document-only unless Excel becomes
   clickable in this session.
2) ERA real first remittance .835 ingest — blocked if no payer file.
3) WAIT — Trellis withBenefits until ~2026-07-20.
4) Something else ONLY from LIVE AUDIT — real NewRidgeFinancial2/ paths (no SoftDent GUI spam while Excel grey).

HARD CONSTRAINTS:
- SoftDent READ-ONLY; empty ≠ $0; PHI initials+hash
- Do not SoftDent GUI Excel export while grey (Preview optical only; never Printer/File)
- Do not invent withBenefits or remittance dollars
- Do not flip forceCloseAvailable true
- No React; no third-party chat embeds

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


def get_json(path: str, timeout: int = 10):
    try:
        with urllib.request.urlopen(BASE + path, context=CTX, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:  # noqa: BLE001
        return {"error": type(e).__name__, "msg": str(e)[:240]}


def live_audit() -> dict:
    am = get_json("/api/trellis/am-proof", 12)
    claims = get_json("/api/softdent/claims-outstanding?limit=5", 12)
    era = get_json("/api/apex/hal/era-inbox/status", 12)
    beams = get_json("/api/hal/tools/money-beams", 12)
    pcs = get_json("/api/hal/tools/period-close-status", 12)
    ready = get_json("/api/import-readiness", 12)
    app = get_json("/api/app-info", 12)
    pilot = app.get("pilot") if isinstance(app, dict) else None
    mb = pcs.get("morningBundle") if isinstance(pcs, dict) else None
    era_drop = REPO / "app_data" / "nr2" / "office" / "era_inbox" / "drop"
    era_files = []
    if era_drop.is_dir():
        era_files = sorted(p.name for p in era_drop.iterdir() if p.is_file())[:12]
    return {
        "softdentExcelGreyed": True,
        "softdentExcelGreyMeaning": (
            "SoftDent intentionally blocks extractable pulls across Output Options reports; "
            "Print Preview optical-only until SoftDent re-enables Excel"
        ),
        "excelEnablementRunbook": "NewRidgeFinancial2/docs/runbooks/softdent_excel_enablement_nr2.md",
        "excelBlockedDoc": "NewRidgeFinancial2/docs/MOONSHOT_OPS_SOFTDENT_EXCEL_ENABLEMENT_BLOCKED_2026-07-17.md",
        "carestreamHelp": {
            "runningReports": "https://help.carestreamdental.com/rh/web/server/SoftDent/projects_responsive/DE1055_SD_Wkbk/Running_Reports.htm",
            "note": "Output Options on every report run; Excel when SoftDent offers it",
        },
        "serverUp": True,
        "trellisAmProof": {
            "ok": am.get("ok"),
            "passed": am.get("passed"),
            "chipStatus": am.get("chipStatus"),
            "chipLabel": am.get("chipLabel"),
            "withBenefits": am.get("withBenefits"),
        },
        "trellisWaitUntil": "~2026-07-20 1AM verify / 2AM proof",
        "periodClose": {
            "status": pcs.get("status"),
            "morningBundle": {
                "ok": (mb or {}).get("ok") if isinstance(mb, dict) else mb,
                "failed": (mb or {}).get("failed") if isinstance(mb, dict) else None,
                "okCount": (mb or {}).get("okCount") if isinstance(mb, dict) else None,
            },
            "forceClose": pcs.get("forceClose"),
        },
        "moneyBeams": {
            "ok": beams.get("ok"),
            "softdent": (beams.get("softdent") or {}).get("display")
            if isinstance(beams.get("softdent"), dict)
            else None,
            "quickbooks": (beams.get("quickbooks") or {}).get("display")
            if isinstance(beams.get("quickbooks"), dict)
            else None,
        },
        "importBlocking": ready.get("blocking") if isinstance(ready, dict) else None,
        "claims": {
            "hasData": claims.get("hasData"),
            "count": claims.get("count"),
            "totalOutstanding": claims.get("totalOutstanding"),
            "error": claims.get("error"),
        },
        "eraInbox": era if isinstance(era, dict) else {"raw": str(era)[:200]},
        "eraDropFiles": era_files,
        "pilot": pilot,
        "appliedAlready": [
            "viewport P1-4 + hub",
            "morning bundle Track B (prior Excel when clickable)",
            "collections excel-greyed harden",
            "claims honesty",
            "HAL desk smoke",
            "pilot shadow Day X of 30",
            "SoftDent grey-Excel universal pull-block docs 8084d2b",
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
            "X-Title": "NR2 Moonshot next SoftDent grey Excel universal",
        },
    )
    with urllib.request.urlopen(req, context=CTX, timeout=120) as r:
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
    (OUT / f"moonshot_whats_next_softdent_grey_excel_audit_{stamp}.json").write_text(
        json.dumps(audit, indent=2), encoding="utf-8"
    )
    user = (
        "LIVE AUDIT follows. SoftDent Excel grey = universal pull block; Preview optical only. "
        "Pick implementable NEXT or honest ATTENDED OPS / WAIT.\n\n"
        + json.dumps(audit, indent=2)[:90000]
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
    report = DOCS / f"MOONSHOT_WHATS_NEXT_AFTER_SOFTDENT_GREY_EXCEL_UNIVERSAL_{DATE}.md"
    header = (
        f"# Moonshot AI — What's Next After SoftDent Grey-Excel Universal Pull Block (CONSULT ONLY)\n\n"
        f"**Date:** {DATE}\n"
        f"**Model:** `{meta.get('model')}`\n"
        f"**Key:** {key_name}\n"
        f"**Script:** `scripts/run_moonshot_whats_next_after_softdent_grey_excel_universal_consult.py`\n"
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
