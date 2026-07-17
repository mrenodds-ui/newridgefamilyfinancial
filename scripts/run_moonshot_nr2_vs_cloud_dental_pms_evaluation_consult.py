"""Moonshot — Full NR2 program evaluation vs popular cloud dental PMS (CONSULT ONLY).

Operator: evaluate whole program vs cloud dental PMS; gaps; close-the-gap report.
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
    "have moonshot ai evaluate the whole program for all issues and compare it to "
    "popular cloud based dental practice management systems and what can be done to "
    "close the gap and report"
)

SYSTEM = """You are Moonshot AI — principal architect evaluating NewRidgeFinancial2 (NR2).

CONSULT / EVALUATION REPORT ONLY — DO NOT APPLY CODE. DO NOT invent file paths.

## What NR2 IS (hard)
NR2 is a **financial / ops overlay** on an existing on-prem SoftDent (Carestream) + QuickBooks practice —
static HTML/JS optical desk + local Python HAL APIs on loopback. It is NOT a full replacement PMS.
Hard rules: SoftDent READ-ONLY (no write-back); empty ≠ $0; SoftDent Output Options Excel OR Print Preview
only (never Printer/File); Excel grey = SoftDent intentional extract block across reports (Preview optical-only);
board PHI initials+hash; no third-party chat embeds.

## Popular cloud dental PMS to compare against (use public product knowledge)
Compare NR2+SoftDent hybrid posture against these categories (not a vendor sales pitch):
1) Dentrix Ascend (Henry Schein) — cloud PMS
2) Carestream Sensei Cloud / cloud SoftDent migration path
3) Curve Dental — cloud PMS
4) Planet DDS Denticon — cloud multi-location
5) Open Dental (cloud-hosted / eConnector patterns) — open API culture
6) Orthotrac / specialty clouds as secondary reference if relevant
7) Adjacent cloud stacks often paired with PMS: Weave, Dental Intelligence, RevenueWell, Pearl AI (analytics/engagement)

## Your job
Produce a BOARD-READY evaluation report:

1. **Program health** — what works, what's broken/blocked, honesty risks (from LIVE AUDIT).
2. **Capability map** — NR2 vs typical cloud PMS across: scheduling, charting/clinical, imaging,
   billing/claims/ERA, patient engagement, reporting/analytics, multi-location, mobile, integrations,
   security/compliance posture, AI assistance.
3. **Gap analysis** — where NR2+SoftDent is behind cloud PMS; where NR2 is ahead (fiduciary overlay,
   SoftDent/QB money beams, HAL desk, empty≠$0 honesty, local control).
4. **Close-the-gap roadmap** — prioritized packages NR2 can do WITHOUT becoming a full PMS and WITHOUT
   SoftDent write-back. Separate: (A) Attended SoftDent Excel enablement, (B) NR2 product packages,
   (C) External waits (Trellis, ERA 835, Carestream), (D) Explicitly OUT OF SCOPE (replace SoftDent clinical).
5. **Issues inventory** — concrete defects/blockers from LIVE AUDIT (Excel grey, collections failed,
   Trellis awaiting, ERA placeholder, shadow Day X/30, forceClose false, etc.).

## Output format (strict markdown)
# Executive Verdict (3–5 sentences)
## 0. Operator Intent (verbatim)
## 1. NR2 Program Identity (what it is / is not)
## 2. Live Issues Inventory (severity · evidence · impact)
## 3. Capability Scorecard vs Cloud PMS (table: Capability | Cloud PMS norm | NR2+SoftDent | Gap)
## 4. Where NR2 Is Ahead
## 5. Close-the-Gap Roadmap (P0/P1/P2 · effort · owner: Cursor vs Operator vs Vendor)
## 6. What NOT To Do (anti-patterns)
## 7. 90-Day Recommended Sequence
## 8. Acceptance Gates for "gap closing"
## 9. Approval Checklist

Be blunt and fiduciary. Prefer LIVE AUDIT facts over marketing. Never invent SoftDent write-back,
Preview money dollars, withBenefits, or fake 835s.
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
            return {"http": r.status, "data": json.loads(r.read().decode("utf-8", "replace"))}
    except Exception as e:  # noqa: BLE001
        return {"http": None, "error": type(e).__name__, "msg": str(e)[:240]}


def slim(d: dict, keys: list[str]) -> dict:
    data = d.get("data") if isinstance(d, dict) else None
    if not isinstance(data, dict):
        return {"http": d.get("http"), "error": d.get("error"), "msg": d.get("msg")}
    out = {"http": d.get("http")}
    for k in keys:
        if k in data:
            out[k] = data[k]
    return out


def live_audit() -> dict:
    ready = get_json("/api/import-readiness")
    beams = get_json("/api/hal/tools/money-beams")
    pcs = get_json("/api/hal/tools/period-close-status")
    am = get_json("/api/trellis/am-proof")
    claims = get_json("/api/softdent/claims-outstanding?limit=5")
    era = get_json("/api/apex/hal/era-inbox/status")
    app = get_json("/api/app-info")
    desk = get_json("/api/health/desk-smoke", 20)

    pages = sorted(p.name for p in SITE.glob("nr2-optical-page-*.html"))
    js = sorted(p.name for p in SITE.glob("nr2-optical-page-*.js"))
    hub = sorted(p.name for p in SITE.glob("nr2-optical-pages-hub*"))
    landing = sorted(p.name for p in SITE.glob("nr2-optical-beam*"))
    nr2_py = sorted(p.name for p in NR2.glob("nr2_*.py"))
    runbooks = sorted(p.name for p in (NR2 / "docs" / "runbooks").glob("*.md")) if (NR2 / "docs" / "runbooks").is_dir() else []

    era_drop = REPO / "app_data" / "nr2" / "office" / "era_inbox" / "drop"
    era_files = sorted(p.name for p in era_drop.iterdir() if p.is_file())[:20] if era_drop.is_dir() else []

    pilot = None
    if isinstance(app.get("data"), dict):
        pilot = app["data"].get("pilot")

    mb = None
    if isinstance(pcs.get("data"), dict):
        mb = pcs["data"].get("morningBundle")

    return {
        "program": {
            "name": "NewRidgeFinancial2",
            "identity": "financial/ops overlay on SoftDent+QuickBooks — not a full PMS",
            "stack": "static HTML/JS optical desk + local Python HAL/HTTPS loopback",
            "hardRules": [
                "SoftDent READ-ONLY no write-back",
                "empty != $0",
                "Output Options Excel|Print Preview only — never Printer/File",
                "Excel grey = SoftDent intentional extract block (Preview optical-only)",
                "PHI initials+hash",
                "no third-party chat embeds",
            ],
        },
        "inventory": {
            "opticalPages": pages,
            "opticalJs": js,
            "hubLanding": hub + landing,
            "nr2PyModules": nr2_py,
            "runbooks": runbooks[:30],
        },
        "live": {
            "importReadiness": slim(
                ready, ["ok", "blocking", "alignmentLasers", "summary", "completeness"]
            ),
            "moneyBeams": slim(
                beams, ["ok", "softdent", "quickbooks", "emptyNotZero", "importStale", "beamHash"]
            ),
            "periodClose": {
                "http": pcs.get("http"),
                "status": (pcs.get("data") or {}).get("status") if isinstance(pcs.get("data"), dict) else None,
                "forceClose": (pcs.get("data") or {}).get("forceClose") if isinstance(pcs.get("data"), dict) else None,
                "morningBundle": mb,
            },
            "trellisAm": slim(am, ["ok", "passed", "chipStatus", "chipLabel", "withBenefits", "candidates"]),
            "claims": slim(
                claims,
                ["hasData", "count", "totalOutstanding", "payerStats", "paidSuppress", "error"],
            ),
            "eraInbox": era.get("data") if isinstance(era.get("data"), dict) else era,
            "eraDropFiles": era_files,
            "pilot": pilot,
            "deskSmoke": desk.get("data") if isinstance(desk.get("data"), dict) else desk,
        },
        "knownBlockers": {
            "softdentExcelGreyedLive": True,
            "collectionsMorningBundleFailed": True,
            "trellisWithBenefitsWaitUntil": "~2026-07-20",
            "eraReal835Pending": True,
            "previewNotMoneyBeam": True,
        },
        "recentAppliedThemes": [
            "viewport no-scroll packages + hub parity",
            "morning bundle Track B (partial collections)",
            "claims honesty / paid suppress",
            "HAL desk smoke / this-patient",
            "pilot shadow Day X of 30",
            "SoftDent grey-Excel universal pull-block documentation",
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
            "X-Title": "NR2 Moonshot full program vs cloud dental PMS",
        },
    )
    with urllib.request.urlopen(req, context=CTX, timeout=300) as r:
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
    audit_path = OUT / f"moonshot_nr2_vs_cloud_pms_audit_{stamp}.json"
    audit_path.write_text(json.dumps(audit, indent=2, default=str), encoding="utf-8")
    print(f"AUDIT_WRITTEN {audit_path}", flush=True)
    user = (
        "FULL PROGRAM EVALUATION. LIVE AUDIT JSON follows. Compare NR2+SoftDent hybrid to popular "
        "cloud dental PMS; list all issues; close-the-gap roadmap; board-ready report.\n\n"
        + json.dumps(audit, indent=2, default=str)[:100000]
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
    report = DOCS / f"MOONSHOT_NR2_VS_CLOUD_DENTAL_PMS_EVALUATION_{DATE}.md"
    header = (
        f"# Moonshot AI — NR2 Full Program Evaluation vs Cloud Dental PMS (CONSULT ONLY)\n\n"
        f"**Date:** {DATE}\n"
        f"**Model:** `{meta.get('model')}`\n"
        f"**Key:** {key_name}\n"
        f"**Script:** `scripts/run_moonshot_nr2_vs_cloud_dental_pms_evaluation_consult.py`\n"
        f"**Audit JSON:** `{audit_path.as_posix()}`\n"
        f"**Apply:** Consult/report only — operator must say continue / approve before any implementation.\n\n"
        f"## Operator request (verbatim)\n\n"
        f"> {OPERATOR_REQUEST_VERBATIM}\n\n"
        f"---\n\n"
    )
    report.write_text(header + content.strip() + "\n", encoding="utf-8")
    print(report)
    print("---")
    try:
        print(content[:9000])
    except UnicodeEncodeError:
        print(content[:9000].encode("ascii", "replace").decode("ascii"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
