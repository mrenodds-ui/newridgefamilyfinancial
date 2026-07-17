"""Moonshot — What's next after collections Excel-greyed harden (CONSULT ONLY).

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

CONTEXT (hard facts — do not contradict):
- SoftDent agent hard-stop was LIFTED. SoftDent GUI allowed under read-only Excel|Preview rules.
- Viewport Packages 1–4 + Hub parity APPLIED on main.
- Ops Track B morning_bundle APPLIED: periodClose.morningBundle.ok=true, failed=["collections"],
  aging+register Excel paths under C:\\SoftDentReportExports, money beams LIVE
  SoftDent ~$52,270 / QB ~$78,399. forceClose stays laser-gated false.
- Collections leftover CLOSED honestly (commit 77dbc45): Collection Summary Excel radio is
  GREYED on SoftDent Output Options → Print Preview only; never Printer/File; no collections
  .xls money ingest while SoftDent keeps Excel disabled. Doc:
  MOONSHOT_OPS_COLLECTIONS_EXCEL_GREYED_2026-07-17.md
- LIVE probe this session: SoftDent also greys Excel on Account Aging Output Options —
  SoftDent-side enablement issue (runbook softdent_excel_enablement_nr2.md), not inventable in NR2.
- Already APPLIED (do not redo): Claims workflow honesty, HAL desk smoke / this-patient,
  Pilot shadow clock (shadowDaysElapsed starts at 0; need ≥30), ERA first-drop path wiring
  (real 835 still pending — README placeholder empty ≠ $0).
- Trellis AM: passed=false / chip awaiting; withBenefits must WAIT until next scrape
  ~2026-07-20 1AM verify / 2AM proof. Do NOT invent ClearCoverage benefits.
- UI polish P1–P10 / V1–V6 / E1–E4 CLOSED — no reskin.

YOUR JOB: Pick THE single best NEXT package Cursor can APPLY NOW (or the single honest WAIT
if nothing else is implementable without SoftDent Excel re-enable or Trellis scrape).
Prefer REAL product/ops work from LIVE AUDIT. Ordered backlog 2–4 after #1.

CANDIDATES (pick ONE #1):
1) SoftDent Excel enablement ops package — operator SoftDent feature/license path so Excel
   radios become clickable again; then attended morning_bundle re-run (aging Excel required).
   Code-only if there is a real NR2 gap; otherwise this is ATTENDED OPS (document + gate).
2) ERA real first remittance drop — ingest a real .835 (not README); empty ≠ $0 until then.
3) Pilot shadow clock hygiene / day-count visibility on optical desk (no forceClose flip).
4) WAIT — Trellis withBenefits until 2026-07-20 (only if truly the highest-value honest next).
5) Something else justified ONLY from LIVE AUDIT — real NewRidgeFinancial2/ paths.

HARD CONSTRAINTS:
- SoftDent READ-ONLY forever; empty ≠ $0; PHI initials+hash
- Output Options Excel OR Print Preview only — never Printer, never File
- No React; no third-party chat embeds; do not flip forceCloseAvailable true
- Do NOT invent ClearCoverage withBenefits
- Do NOT invent SoftDent Excel drops or dollar totals from Preview
- Prefer not to spam SoftDent GUI until Excel is clickable (print-risk)

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
    desk = get_json("/api/health/desk-smoke", 20)
    pilot_path = REPO / "app_data" / "nr2" / "pilot_phase.json"
    pilot = {}
    if pilot_path.is_file():
        try:
            pilot = json.loads(pilot_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            pilot = {"error": f"{type(exc).__name__}:{exc}"[:160]}
    mb = pcs.get("morningBundle") if isinstance(pcs, dict) else None
    return {
        "softdentHardStop": False,
        "softdentExcelGreyedLive": True,
        "collectionsExcelGreyedDoc": "NewRidgeFinancial2/docs/MOONSHOT_OPS_COLLECTIONS_EXCEL_GREYED_2026-07-17.md",
        "excelEnablementRunbook": "NewRidgeFinancial2/docs/runbooks/softdent_excel_enablement_nr2.md",
        "lastCommitHint": "77dbc45 SoftDent Output Options greyed Excel → Print Preview",
        "serverUp": True,
        "trellisTasks": {
            "nightly1am": "NR2 Trellis Nightly Insurance Verify 1AM Mon-Thu next ~2026-07-20 1:00",
            "proof2am": "NR2 Trellis AM withBenefits Proof 2AM Mon-Thu next ~2026-07-20 2:00",
        },
        "trellisAmProof": {
            "ok": am.get("ok"),
            "passed": am.get("passed"),
            "chipStatus": am.get("chipStatus"),
            "chipLabel": am.get("chipLabel"),
            "candidates": am.get("candidates"),
            "withBenefits": am.get("withBenefits"),
            "error": am.get("error"),
        },
        "periodClose": {
            "status": pcs.get("status"),
            "morningBundle": {
                "ok": (mb or {}).get("ok") if isinstance(mb, dict) else mb,
                "failed": (mb or {}).get("failed") if isinstance(mb, dict) else None,
                "okCount": (mb or {}).get("okCount") if isinstance(mb, dict) else None,
                "excelDisabled": (mb or {}).get("excelDisabled") if isinstance(mb, dict) else None,
            },
            "forceClose": pcs.get("forceClose"),
            "error": pcs.get("error"),
        },
        "moneyBeams": {
            "ok": beams.get("ok"),
            "softdent": (beams.get("softdent") or {}).get("display")
            if isinstance(beams.get("softdent"), dict)
            else None,
            "quickbooks": (beams.get("quickbooks") or {}).get("display")
            if isinstance(beams.get("quickbooks"), dict)
            else None,
            "emptyNotZero": beams.get("emptyNotZero"),
            "error": beams.get("error"),
        },
        "importLasers": (ready.get("alignmentLasers") if isinstance(ready, dict) else None),
        "importBlocking": ready.get("blocking") if isinstance(ready, dict) else None,
        "claims": {
            "hasData": claims.get("hasData"),
            "count": claims.get("count"),
            "totalOutstanding": claims.get("totalOutstanding"),
            "payerStats": claims.get("payerStats"),
            "paidSuppress": claims.get("paidSuppress"),
            "error": claims.get("error"),
        },
        "eraInbox": era if isinstance(era, dict) else {"raw": str(era)[:200]},
        "deskSmoke": {
            k: desk.get(k)
            for k in ("ok", "status", "match", "error", "msg", "forceCloseAvailable")
            if isinstance(desk, dict) and k in desk
        }
        or desk,
        "pilotPhase": pilot,
        "appliedAlready": [
            "viewport P1-4 + hub parity",
            "morning bundle Track B",
            "collections excel-greyed harden 77dbc45",
            "claims workflow honesty",
            "HAL desk smoke / this-patient",
            "pilot shadow clock",
            "ERA first-drop path (placeholder README)",
        ],
        "claimsJsBytes": (SITE / "nr2-optical-page-claims.js").stat().st_size
        if (SITE / "nr2-optical-page-claims.js").is_file()
        else None,
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
            "X-Title": "NR2 Moonshot next after collections excel greyed",
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
    (OUT / f"moonshot_whats_next_after_collections_excel_greyed_audit_{stamp}.json").write_text(
        json.dumps(audit, indent=2), encoding="utf-8"
    )
    user = (
        "LIVE AUDIT follows. Collections Excel-greyed harden done. SoftDent Excel radios "
        "greyed live. Trellis wait until ~2026-07-20. Pick implementable NEXT now.\n\n"
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
    report = DOCS / f"MOONSHOT_WHATS_NEXT_AFTER_COLLECTIONS_EXCEL_GREYED_{DATE}.md"
    header = (
        f"# Moonshot AI — What's Next After Collections Excel-Greyed (CONSULT ONLY)\n\n"
        f"**Date:** {DATE}\n"
        f"**Model:** `{meta.get('model')}`\n"
        f"**Key:** {key_name}\n"
        f"**Script:** `scripts/run_moonshot_whats_next_after_collections_excel_greyed_consult.py`\n"
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
