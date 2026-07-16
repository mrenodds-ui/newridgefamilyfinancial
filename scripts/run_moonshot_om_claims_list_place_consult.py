"""Moonshot AI — place claims list on Office Manager like Mon–Thu patients + full names.

Operator: ask moonshot ai how to place claims like he did with patients under the
office manger page. can he do it with claims like the patient list. also, i need
the patient names not their initials on the lists. report
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

OPERATOR_REQUEST_VERBATIM = (
    "ask moonshot ai how to place claims like he did with patients under the "
    "office manger page. can he do it with claims like the patient list. also, "
    "i need the patient names not their initials on the lists. report"
)

LIVE_FACTS = """
CURRENT NR2 STATE (2026-07-16) — ground recommendations here:

WHAT ALREADY SHIPPED (patient list pattern to mirror):
- Optical OM: site/nr2-optical-page-office-manager.html/.js
  section #om-weekly-schedule "This Week · Mon – Thu"
- Fetches GET /api/softdent/appointments-range?days=4
- Board UI currently paints initials + short hash only
  (JS comment: "Board stays initials + hash (PHI). Full name only in dossier panel.")
- Click row → mini dossier (#wk-dossier) shows patientName + claims sample
- Applied doc: MOONSHOT_OM_MON_THU_PATIENT_LIST_PLACE_APPLIED_2026-07-16.md
- Trellis tomorrow huddle on same OM page also board = initials + hash

CLAIMS BACKEND ALREADY EXISTS (reuse, do not invent):
- nr2_softdent_daily.claims_outstanding(limit=…)
  returns claims[] with claimId, patientName (FULL string from sd_claims),
  payer, serviceDate, amount, status + totalOutstanding + count
- GET /api/softdent/claims-outstanding?limit=N (cap 500)
- GET /api/claims/aging-summary (counts-only over30)
- Optical Claims page (nr2-optical-page-claims.js) already hits claims-outstanding
  for metric strip — NOT a patient-style list on Office Manager

WHAT IS MISSING ON OM:
- No #om-claims / outstanding-claims list section on office-manager.html
- Claims optical page shows metrics, not an OM-style day/patient list
- Operator wants claims PLACED ON OM like the Mon–Thu patient list

OPERATOR PHI OVERRIDE (explicit this consult):
- Operator now says: "i need the patient names not their initials on the lists"
- Prior policy was board = initials+hash; full name behind click/dossier
- API appointments-range ALREADY returns patientName on each slot
- claims_outstanding ALREADY returns patientName full
- UI deliberately hides names on OM board today — operator wants that changed
  for BOTH schedule list AND (new) claims list

CONSTRAINTS STILL IN FORCE:
- SoftDent READ-ONLY; empty ≠ $0; no fake $0
- CONSULT ONLY — do not apply until operator approves
- Prefer optical OM page (same surface as patient list) over inventing React
- Do not invent SoftDent Excel paths or forceClose flips

OPERATOR INTENT INTERPRETATION:
1) Can we place a claims list on Office Manager the same way as the patient list? YES/NO + how
2) Mirror the placement pattern (section + fetch + render + refresh)
3) Show FULL patient names on lists (schedule + claims), not initials
4) "report" = consult markdown only
"""

SYSTEM = """You are Moonshot AI — NR2 Office Manager / SoftDent claims+schedule architect.

Operator (verbatim):
> ask moonshot ai how to place claims like he did with patients under the office
> manger page. can he do it with claims like the patient list. also, i need the
> patient names not their initials on the lists. report

Answer in plain operator language. Be decisive and coding-concrete.

GOALS:
1. Answer YES/NO: can claims be placed on Office Manager like the Mon–Thu patient list?
2. Tell HOW — mirror the shipped optical OM patient-list pattern (section + API + render).
3. Prefer REUSING GET /api/softdent/claims-outstanding + claims_outstanding —
   do not invent a second SoftDent claims query path.
4. Address FULL PATIENT NAMES on lists (schedule Mon–Thu AND claims):
   operator override vs prior initials+hash board policy.
   Recommend safe staff-only display (names on OM lists) without leaking to
   public/logs/spoken briefings if those stay PHI-safe.
5. CONSULT ONLY — DO NOT APPLY code. Wait for approve / proceed.
6. SoftDent READ-ONLY. empty ≠ $0. Rank MUST / SHOULD / NICE.
   Paste-ready file sketches + validation steps.

OUTPUT (strict markdown):
# Verdict — Place claims list on Office Manager (+ full names)
## 0. Operator Intent (verbatim)
## 1. Current State (patient list shipped vs claims gap vs name display)
## 2. Can claims be done like the patient list? (YES/NO + why)
## 3. Recommended Placement Design (optical OM)
## 4. Full patient names (not initials) — policy + coding change
## 5. Coding Plan (files · endpoints · UI wire · refresh)
## 6. MUST / SHOULD / NICE table
## 7. PHI + SoftDent honesty rules (staff OM vs board/logs)
## 8. Validation checklist
## 9. Executive Summary (5 bullets)
## 10. Approval Checklist
DO NOT APPLY until operator says approve / proceed.
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

    live = {
        "operatorAsk": OPERATOR_REQUEST_VERBATIM,
        "patientListShipped": {
            "htmlSection": "#om-weekly-schedule",
            "api": "/api/softdent/appointments-range?days=4",
            "boardUiToday": "initials + hash only; patientName in API unused on board",
            "appliedDoc": "MOONSHOT_OM_MON_THU_PATIENT_LIST_PLACE_APPLIED_2026-07-16.md",
        },
        "claimsApiExists": {
            "path": "/api/softdent/claims-outstanding",
            "helper": "claims_outstanding",
            "fields": [
                "claimId",
                "patientName",
                "payer",
                "serviceDate",
                "amount",
                "status",
            ],
            "alreadyUsedBy": "nr2-optical-page-claims.js (metrics strip only)",
            "onOfficeManager": False,
        },
        "opticalOmPage": {
            "html": "NewRidgeFinancial2/site/nr2-optical-page-office-manager.html",
            "js": "NewRidgeFinancial2/site/nr2-optical-page-office-manager.js",
            "currentSections": [
                "money-strip",
                "om-weekly-schedule (patients Mon-Thu)",
                "om-trellis-tomorrow (initials+hash)",
            ],
        },
        "nameOverride": {
            "operatorWants": "full patient names on lists, not initials",
            "apiAlreadyHasNames": True,
            "uiHidesNamesOnBoard": True,
        },
        "question": (
            "Place claims on OM like patient list? How? And show full names "
            "on schedule + claims lists?"
        ),
    }

    user = (
        f"OPERATOR REQUEST (verbatim):\n{OPERATOR_REQUEST_VERBATIM}\n\n"
        f"LIVE FACTS:\n{LIVE_FACTS}\n\n"
        f"LIVE CONTEXT JSON:\n```json\n{json.dumps(live, indent=2)}\n```\n\n"
        "Recommend concrete placement of outstanding claims on Office Manager "
        "mirroring the Mon–Thu patient list, PLUS switching list display from "
        "initials to full patient names. Reuse claims-outstanding. "
        "Markdown REPORT only. CONSULT ONLY — do not apply."
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
            os.getenv("OPENROUTER_X_TITLE") or "NR2 OM Claims List Place + Full Names"
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
    raw_path = OUT / f"moonshot_om_claims_list_place_{stamp}.json"
    md_path = DOCS / f"MOONSHOT_OM_CLAIMS_LIST_PLACE_{DATE}.md"
    raw_path.write_text(json.dumps(raw, indent=2)[:500000], encoding="utf-8")

    header = (
        f"# Moonshot AI — Place Claims List on Office Manager + Full Names "
        f"(CONSULT ONLY)\n\n"
        f"**Date:** {DATE}\n"
        f"**Model:** `{model}`\n"
        f"**Key:** {key_name}\n"
        f"**Script:** `scripts/run_moonshot_om_claims_list_place_consult.py`\n"
        f"**Apply:** DO NOT APPLY until operator approves.\n\n"
        f"## Operator request (verbatim)\n\n"
        f"> {OPERATOR_REQUEST_VERBATIM}\n\n"
        f"---\n\n"
    )
    md_path.write_text(header + text.strip() + "\n", encoding="utf-8")
    print("Wrote", md_path, flush=True)
    print("Raw", raw_path, flush=True)
    sys.stdout.buffer.write((text[:6000] + "\n").encode("utf-8", "replace"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
