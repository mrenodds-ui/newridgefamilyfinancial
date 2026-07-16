"""Moonshot AI — how to place Mon–Thu scheduled patient list on Office Manager.

Operator: ask moonshot ai how to place a list of patient in the office manager
page who are schedule for Monday thur Thurday everyday and report
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
    "ask moonshot ai how to place a list of patient in the office manager page "
    "who are schedule for Monday thur Thurday everyday and report"
)

LIVE_FACTS = """
CURRENT NR2 STATE (2026-07-16) — ground recommendations here:

BACKEND ALREADY EXISTS (reuse, do not reinvent):
- nr2_softdent_daily.appointments_range_snapshot(start_iso, days=4)
  docstring: "Multi-day appointment list for OM (Mon–Thu). PHI-safe hashes."
- nr2_softdent_daily.monday_of_week_iso() → Monday of current week
- GET /api/softdent/appointments-range?start=<YYYY-MM-DD>&days=4&provider=
  in nr2_http_server.py (returns days[] with date, dayName, slots[], count)
- Slot fields: patientId, patientHash, initials, provider, status, time="—"
  (SoftDent sd_appointments has NO appt_time — honest dash)
- Also: GET /api/softdent/appointments-today (single day / operatory board)

WHAT IS MISSING / STRIPPED:
- apex_missing_widgets_pack.py is GONE (clean-slate; only .pyc left).
  Prior applied build hal-10495 had build_weekly_schedule_list /
  "This Week's Schedule (Mon–Thu)" widget — NOT in source now.
- Grep finds NO build_weekly_schedule_list / schedule-list renderer in live JS.
- Optical OM page (site/nr2-optical-page-office-manager.html + .js) only shows
  SoftDent TODAY count via /api/softdent/appointments-today — NO patient list UI.
- Classic Apex OM widgets still call append_office_manager_missing which imports
  the missing pack (no-op / except pass).

PRIOR CONSULT (do not ignore; update for optical + stripped pack):
- docs/MOONSHOT_OM_MON_THU_PATIENTS_HAL_CONSULT_2026-07-11.md
- docs/MOONSHOT_OM_MON_THU_PATIENTS_HAL_APPLIED_2026-07-11.md
  claimed widget + prefetch; operator now asks again → list not visible on OM.

OFFICE HOURS CONTEXT:
- Practice works Mon–Thu (not Fri–Sun primary schedule days).
- SoftDent READ-ONLY. empty ≠ $0. PHI local-only; prefer hash/initials on board.

OPERATOR INTENT INTERPRETATION:
- "place a list of patient" = visible patient schedule list ON Office Manager page
- "Monday thur Thursday everyday" = Mon–Thu of the current week (refresh daily /
  every page load), not a static one-time dump
- "report" = consult report only; DO NOT APPLY code until operator approves
"""

SYSTEM = """You are Moonshot AI — NR2 Office Manager / SoftDent schedule architect.

Operator (verbatim):
> ask moonshot ai how to place a list of patient in the office manager page who
> are schedule for Monday thur Thurday everyday and report

Answer in plain operator language. Be decisive and coding-concrete.

GOALS:
1. Tell HOW to place a Mon–Thu scheduled patient LIST on the Office Manager page
   so staff see it every day (current week Mon–Thu).
2. Prefer REUSING existing GET /api/softdent/appointments-range +
   appointments_range_snapshot — do not invent a second SoftDent query path.
3. Cover BOTH surfaces if relevant:
   A) Optical OM page: nr2-optical-page-office-manager.html/.js (currently count-only)
   B) Classic Apex OM widget board (pack stripped — restore or replace cleanly)
4. CONSULT ONLY — DO NOT APPLY code. Wait for approve / proceed.
5. SoftDent READ-ONLY. empty ≠ $0. No fake times. PHI: hash/initials on list;
   full name only behind staff-gated patient context if needed.
6. Rank MUST / SHOULD / NICE. Paste-ready file sketches + validation steps.

OUTPUT (strict markdown):
# Verdict — Place Mon–Thu patient list on Office Manager
## 0. Operator Intent (verbatim)
## 1. Current State (what already exists vs what is missing on OM)
## 2. Recommended Placement Design
### 2A Optical OM page (nr2-optical-page-office-manager.*)
### 2B Classic Apex OM widgets (if still used)
## 3. Coding Plan (files · endpoints · UI wire · everyday refresh)
## 4. MUST / SHOULD / NICE table
## 5. PHI + SoftDent honesty rules
## 6. Validation checklist (how operator verifies list appears)
## 7. Executive Summary (5 bullets)
## 8. Approval Checklist
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
        "apiExists": {
            "path": "/api/softdent/appointments-range",
            "helper": "appointments_range_snapshot + monday_of_week_iso",
            "defaultDays": 4,
        },
        "opticalOmPage": {
            "html": "NewRidgeFinancial2/site/nr2-optical-page-office-manager.html",
            "js": "NewRidgeFinancial2/site/nr2-optical-page-office-manager.js",
            "current": "SoftDent today COUNT only — no patient list UI",
        },
        "stripped": {
            "apex_missing_widgets_pack.py": "missing (pyc only)",
            "build_weekly_schedule_list": "not in source",
        },
        "priorAppliedDoc": "MOONSHOT_OM_MON_THU_PATIENTS_HAL_APPLIED_2026-07-11.md",
        "question": "How do we PLACE the Mon–Thu patient list on OM so it shows every day?",
    }

    user = (
        f"OPERATOR REQUEST (verbatim):\n{OPERATOR_REQUEST_VERBATIM}\n\n"
        f"LIVE FACTS:\n{LIVE_FACTS}\n\n"
        f"LIVE CONTEXT JSON:\n```json\n{json.dumps(live, indent=2)}\n```\n\n"
        "Recommend the concrete placement + coding plan to show Mon–Thu scheduled "
        "patients on Office Manager every day. Reuse appointments-range. "
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
            os.getenv("OPENROUTER_X_TITLE") or "NR2 OM Mon-Thu Patient List Place"
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
    raw_path = OUT / f"moonshot_om_mon_thu_patient_list_place_{stamp}.json"
    md_path = DOCS / f"MOONSHOT_OM_MON_THU_PATIENT_LIST_PLACE_{DATE}.md"
    raw_path.write_text(json.dumps(raw, indent=2)[:500000], encoding="utf-8")

    header = (
        f"# Moonshot AI — Place Mon–Thu Patient List on Office Manager (CONSULT ONLY)\n\n"
        f"**Date:** {DATE}\n"
        f"**Model:** `{model}`\n"
        f"**Key:** {key_name}\n"
        f"**Script:** `scripts/run_moonshot_om_mon_thu_patient_list_place_consult.py`\n"
        f"**Apply:** DO NOT APPLY until operator approves.\n\n"
        f"## Operator request (verbatim)\n\n"
        f"> {OPERATOR_REQUEST_VERBATIM}\n\n"
        f"---\n\n"
    )
    md_path.write_text(header + text.strip() + "\n", encoding="utf-8")
    print("Wrote", md_path, flush=True)
    print("Raw", raw_path, flush=True)
    sys.stdout.buffer.write((text[:5000] + "\n").encode("utf-8", "replace"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
