"""Moonshot AI — What's next after Trellis 1AM/2AM schedule + SoftDent never-Printer.

Operator: ask moonshot what is next and report
Closed: d3bb9f3 Trellis 1AM + SoftDent never-Printer all reports;
  9849c2e withBenefits AM proof 2AM; 8460abf SoftDent C: Select File Name force.
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

OPERATOR_REQUEST_VERBATIM = "ask moonshot what is next and report"

SYSTEM = """You are Moonshot AI — principal architect for NewRidgeFinancial2 (NR2).
CONSULT ONLY — DO NOT APPLY CODE.

Operator said (verbatim): ask moonshot what is next and report

JUST CLOSED on main:
- d3bb9f3: Trellis headed report pull moved to Mon–Thu **1:00 AM** (--same-day);
  SoftDent catalog enforces Excel|Print Preview only (never Printer/File) for ALL reports;
  Select File Name forced to C:\\SoftDent\\softdentexportreports
- 9849c2e: Trellis withBenefits AM proof moved to Mon–Thu **2:00 AM**
- excel_probe GREEN (excelAvailable=true); beam_desk_proof GREEN MATCH
- Operator SKIPPED attended SoftDent morning bundle for now (morningBundle still RED)
- Trellis still status-only / withBenefits=0 until 1 AM scrape lands (next Mon 7/20 if today is Thu afternoon)

CONSTRAINTS:
- SoftDent READ-ONLY; empty ≠ $0; board PHI initials+hash
- SoftDent Output Options: Excel OR Print Preview only — NEVER File, NEVER Printer (all reports)
- Do NOT invent SoftDent Excel drops or Select File Name directories
- Do NOT flip forceCloseAvailable on MATCH/GREEN alone
- Do NOT re-argue Trellis 10:10 PM schedule (now 1 AM pull / 2 AM proof)
- SoftDent morning bundle is operator-deferred — do not insist it is the only #1 if LIVE AUDIT shows a better parallel track
- Prefer REAL NewRidgeFinancial2/ Python + optical JS paths (no invented React)

YOUR JOB: Pick THE single best NEXT package + ordered backlog (2–4) given operator deferred SoftDent bundle.

CANDIDATES (pick ONE as #1 from LIVE AUDIT):
1) SoftDent attended morning bundle Excel re-run (operator deferred — only if still hard-critical)
2) Claims outstanding patient-join fix (sampleWithPatientId=0 polish) while money path waits
3) ERA inbox first real 835 drop + ingest path smoke (inbox empty)
4) Wait for Mon 1 AM Trellis scrape + Tue 2 AM withBenefits proof streak (passive)
5) Optional QB AP/payroll staff CSV drop
6) Pilot shadowDays / cutover clock hygiene (shadowDays unset)
7) Something else justified ONLY from LIVE AUDIT — real paths

OUTPUT (strict markdown):
# Verdict (one sentence)
## 0. Operator Intent (verbatim)
## 1. Recommended NEXT (name, why now, effort, REAL files under NewRidgeFinancial2/, validation gate)
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


def live_audit() -> dict:
    build = {}
    try:
        build = json.loads((NR2 / "nr2-build.json").read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        build = {"error": str(exc)}
    smoke = get_json("/api/health/desk-smoke?run=0", 20)
    tr = get_json("/api/trellis/tomorrow-insurance", 20)
    elig = get_json("/api/trellis/eligibility-report?date=2026-07-20", 20)
    am = get_json("/api/trellis/am-proof", 20)
    pc = get_json("/api/hal/tools/period-close-status", 20)
    ready = get_json("/api/import-readiness", 30)
    gates_path = sorted(OUT.glob("nr2_ops_gates_*.json"))
    gates = {}
    if gates_path:
        try:
            gates = json.loads(gates_path[-1].read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            gates = {"error": str(exc)[:200]}
    return {
        "repoRoot": str(REPO),
        "nr2Root": str(NR2),
        "build": build,
        "commitHint": "9849c2e withBenefits 2AM · d3bb9f3 Trellis 1AM + SoftDent never-Printer",
        "operatorDeferred": ["attended SoftDent morning_bundle Excel re-run"],
        "scheduleNow": {
            "softdentMoneyPull": "9:00 PM night-before",
            "trellisWorklist": "~10:00 PM APScheduler next clinical day",
            "trellisReportPull": "1:00 AM Mon-Thu --same-day --verify",
            "trellisAmProof": "2:00 AM Mon-Thu prove_trellis_withbenefits_am.py",
        },
        "closedDocs": {
            "trellisRunbook": (NR2 / "docs" / "TRELLIS_NIGHTLY_INSURANCE_VERIFY.md").is_file(),
            "excelRunbook": (
                NR2 / "docs" / "runbooks" / "softdent_excel_enablement_nr2.md"
            ).is_file(),
            "hybridOverlay": (
                NR2 / "docs" / "architecture" / "hybrid_pms_overlay.md"
            ).is_file(),
            "trellisAmProofScript": (
                REPO / "scripts" / "prove_trellis_withbenefits_am.py"
            ).is_file(),
            "opsGatesScript": (REPO / "scripts" / "nr2_ops_gates_checklist.py").is_file(),
        },
        "opsGatesLatest": gates,
        "live": {
            "deskSmokeLast": {
                "ok": smoke.get("ok") if isinstance(smoke, dict) else None,
                "status": smoke.get("status") if isinstance(smoke, dict) else None,
                "deskProof": smoke.get("deskProof") if isinstance(smoke, dict) else None,
                "forceCloseAvailable": (
                    smoke.get("forceCloseAvailable") if isinstance(smoke, dict) else None
                ),
                "morningConfidence": (
                    smoke.get("morningConfidence") if isinstance(smoke, dict) else None
                ),
            },
            "trellisTomorrow": {
                "ok": tr.get("ok") if isinstance(tr, dict) else None,
                "hasData": tr.get("hasData") if isinstance(tr, dict) else None,
                "total": tr.get("total") if isinstance(tr, dict) else None,
            },
            "eligibilityReport": {
                "ok": elig.get("ok") if isinstance(elig, dict) else None,
                "hasReport": elig.get("hasReport") if isinstance(elig, dict) else None,
                "patients": elig.get("patients") if isinstance(elig, dict) else None,
                "withBenefits": elig.get("withBenefits") if isinstance(elig, dict) else None,
                "statusOnly": elig.get("statusOnly") if isinstance(elig, dict) else None,
            },
            "trellisAmProof": {
                "ok": am.get("ok") if isinstance(am, dict) else None,
                "passed": am.get("passed") if isinstance(am, dict) else None,
                "chipStatus": am.get("chipStatus") if isinstance(am, dict) else None,
                "chipLabel": am.get("chipLabel") if isinstance(am, dict) else None,
            },
            "periodCloseStatus": {
                "ok": pc.get("ok") if isinstance(pc, dict) else None,
                "status": pc.get("status") if isinstance(pc, dict) else None,
                "morningBundle": pc.get("morningBundle") if isinstance(pc, dict) else None,
            },
            "importReadiness": {
                "ok": ready.get("ok") if isinstance(ready, dict) else None,
                "level": ready.get("level") if isinstance(ready, dict) else None,
                "datasetGaps": (
                    (ready.get("datasetGaps") or [])[:6] if isinstance(ready, dict) else []
                ),
            },
        },
    }


def main() -> int:
    key_name, api_key, base_url = resolve_api_and_endpoint()
    if not api_key:
        print("No API key", file=sys.stderr)
        return 1
    if (api_key or "").startswith("sk-nv") or key_name == "MOONSHOT_API_KEY":
        model = str(os.getenv("MOONSHOT_MODEL") or "kimi-k2.5").strip()
    elif "moonshot.ai" in (base_url or "").lower():
        model = str(os.getenv("MOONSHOT_MODEL") or "kimi-k2.5").strip()
    else:
        model = str(
            os.getenv("MOONSHOT_MODEL")
            or os.getenv("KIMI_K2_MODEL")
            or "moonshotai/kimi-k2.5"
        ).strip()
    print(f"Using {key_name} @ {base_url} model={model}", flush=True)

    audit = live_audit()
    user = (
        f"OPERATOR REQUEST (verbatim):\n{OPERATOR_REQUEST_VERBATIM}\n\n"
        f"LIVE AUDIT:\n```json\n{json.dumps(audit, indent=2)[:120000]}\n```\n\n"
        "Pick THE next package + ordered backlog. Markdown REPORT only. CONSULT ONLY."
    )
    body = {
        "model": model,
        "temperature": 1,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if "openrouter.ai" in base_url:
        headers["HTTP-Referer"] = (
            os.getenv("OPENROUTER_HTTP_REFERER") or "https://127.0.0.1:8765/"
        )
        headers["X-Title"] = (
            os.getenv("OPENROUTER_X_TITLE") or "NR2 Whats Next After Trellis 1AM/2AM"
        )

    req = urllib.request.Request(
        base_url,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=700, context=CTX) as resp:
            raw = json.loads(resp.read().decode("utf-8", "replace"))
    except Exception as exc:  # noqa: BLE001
        print(f"Moonshot call failed: {exc}", file=sys.stderr)
        return 2

    text = extract_message_content(raw) or ""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw_path = OUT / f"moonshot_whats_next_after_trellis_1am_2am_{stamp}.json"
    md_path = DOCS / f"MOONSHOT_WHATS_NEXT_AFTER_TRELLIS_1AM_2AM_{DATE}.md"
    raw_path.write_text(json.dumps(raw, indent=2)[:500000], encoding="utf-8")
    header = (
        f"# Moonshot AI — What's Next After Trellis 1AM/2AM (CONSULT ONLY)\n\n"
        f"**Date:** {DATE}\n"
        f"**Model:** `{model}`\n"
        f"**Key:** {key_name}\n"
        f"**Script:** `scripts/run_moonshot_whats_next_after_trellis_1am_2am_consult.py`\n"
        f"**Closed:** `d3bb9f3` Trellis 1AM + SoftDent never-Printer · "
        f"`9849c2e` withBenefits 2AM\n"
        f"**Apply:** Operator must say continue / approve before Cursor applies.\n\n"
        f"## Operator request (verbatim)\n\n"
        f"> {OPERATOR_REQUEST_VERBATIM}\n\n"
        f"---\n\n"
    )
    md_path.write_text(header + text.strip() + "\n", encoding="utf-8")
    print("Wrote", md_path, flush=True)
    print("Raw", raw_path, flush=True)
    sys.stdout.buffer.write((text[:8000] + "\n").encode("utf-8", "replace"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
