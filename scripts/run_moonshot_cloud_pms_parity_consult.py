"""Moonshot AI — Can NR2 augment to function comparably to cloud PMS (Curve / HSOne / Ascend)?

Operator: with what I have now and cloud-PMS research, can I augment my program to
function comparably to Curve, Henry Schein, Dentrix cloud systems?
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
    "with what i have now and the information you just got, can i augment my program "
    "to function comparitily to these cloud based programs"
)

CLOUD_PMS_RESEARCH = """
## Curve Dental (Curve Hero / SuperHero)
- 100% cloud-native PMS: scheduling, charting, imaging, billing, claims, recare, perio,
  e-prescribe, Curve Pay, Curve Forms, Curve GRO patient engagement, Curve Mobile, Insights, RCM
- Docs: curvedental.zendesk.com/hc/en-us (Quick Guides by module); in-app Curve Community + Ask CurveAI
- Training: 8-session Boot Camp; no single PDF master manual

## Henry Schein One / Dentrix Ascend
- Dentrix Ascend = cloud-native PMS (not desktop Dentrix in cloud)
- Modules: Schedule, Chart/Quick Exam, Imaging PACS, Insurance/Claims/Ledger, Power Reports,
  Online Booking, Eligibility Essentials/Pro, Voice Notes, AI detection
- Docs: hsps.pro/DentrixAscend/Help/ (public web help); learn.dentrixascend.com Academy;
  Customer Portal henryscheinone.my.site.com (gated Learning Center)
- Legacy Dentrix/Easy Dental/Enterprise = server-based, separate PDF Resource Centers

## Henry Schein add-ons (cloud, PMS-agnostic)
- Lighthouse 360: reminders, recall, two-way texting, online booking, forms, reviews (lh360.com)
  Integrates with SoftDent among 17+ PMS platforms
- Jarvis Analytics: cloud BI dashboard — Calendar, Dashboard, Morning Huddle, Treatment Miner,
  Hygiene Recall, 50+ KPIs; integrates with 12+ PMS including Dentrix Ascend
- Jarvis PDF manual: jarvisuniversity.com; help at hsps.pro/Jarvis/Help/

## Cloud PMS common capability pillars
1) Scheduling + online self-booking
2) Clinical charting + perio + imaging + notes + eRx
3) Treatment planning + case presentation
4) Insurance eligibility + claims + ERA + ledger
5) Patient engagement (text/email/reminders/forms/portal)
6) Reporting/analytics/KPI dashboards
7) Payments (integrated processing)
8) Multi-location/DSO admin + role permissions
9) Anywhere browser/mobile access
10) Automated updates + cloud backup + HIPAA security
"""

SYSTEM = """You are Moonshot AI — principal architect for NewRidgeFinancial2 (NR2).
CONSULT ONLY — DO NOT APPLY CODE.

The operator asks whether NR2 can be AUGMENTED (not replaced) to function COMPARABLY
to cloud dental PMS products: Curve Hero, Henry Schein One / Dentrix Ascend, and related
cloud layers (Lighthouse 360, Jarvis Analytics).

NR2 IS NOT A PMS. It is a financial/ops overlay on:
- SoftDent desktop (READ-ONLY via GUI pulls + imports; write-back FORBIDDEN)
- QuickBooks (revenue/AP/payroll imports)
- HAL (local AI assistant, policy KB, automation orchestration)
- Optical interferometer UI (desk-facing chrome)
- Trellis eligibility scrape, ERA inbox, period-close shadow mode

HARD CONSTRAINTS (never recommend violating):
- SoftDent write-back FORBIDDEN
- empty ≠ $0 (never show $0 when data missing)
- SoftDent Output Options: Excel OR Print Preview only — NEVER Printer, NEVER File
- No invented SoftDent paths or fake exports
- No third-party chat embeds (Tawk, PushEngage, etc.) on NR2 pages
- PHI: board-ready initials+hash; fiduciary surface
- NR2 is shadow period-close (systemOfRecord=false) until cutover attestation
- packsAllowed=false; nr2-11000-clean cutover removed apex packs / unified_db contracts

YOUR JOB:
1) Define what "comparably" means for NR2 vs full cloud PMS (honest scope).
2) Build a CAPABILITY PARITY MATRIX: Curve/Ascend pillar vs NR2 today vs augmentable vs never (without replacing SoftDent).
3) Identify NR2's UNIQUE advantages over cloud PMS (money honesty, SoftDent+QB bridge, HAL, period-close laser).
4) Recommend a phased AUGMENTATION strategy (P0–P3) with REAL NewRidgeFinancial2/ file paths.
5) Say what NOT to build (waste / wrong layer).
6) Give verdict: YES partial parity achievable / NO full PMS parity / hybrid recommendation.

OUTPUT (strict markdown):
# Verdict (one sentence — can NR2 augment to comparable function?)
## 0. Operator Intent (verbatim)
## 1. What "comparable" means for NR2 (scope boundary)
## 2. Capability parity matrix (10 pillars × NR2 today / gap / augment path)
## 3. What NR2 already beats cloud PMS at
## 4. Recommended augmentation strategy (phased P0–P3, REAL files, validation gates)
## 5. What NOT to build (stay in lane)
## 6. Hybrid architecture recommendation (NR2 + SoftDent + optional Lighthouse/Jarvis?)
## 7. Executive Summary (5 bullets)
## 8. Approval Checklist
DO NOT APPLY CODE. Real paths only.
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

    optical_pages = sorted(p.name for p in SITE.glob("nr2-optical*.html"))
    api_surface = []
    apex = NR2 / "apex_backend.py"
    if apex.is_file():
        txt = apex.read_text(encoding="utf-8", errors="replace")
        for needle in (
            "/api/softdent/",
            "/api/qb/",
            "/api/hal/",
            "/api/apex/hal/",
            "/api/import-readiness",
            "/api/health/",
        ):
            hits = [line.strip() for line in txt.splitlines() if needle in line and "@app." in line]
            api_surface.append({"prefix": needle, "routeCount": len(hits), "sample": hits[:4]})

    return {
        "repoRoot": str(REPO),
        "build": build,
        "opticalPages": optical_pages,
        "pilot": get_json("/api/app-info", 25),
        "importReadiness": get_json("/api/import-readiness", 40),
        "moneyBeams": get_json("/api/hal/tools/money-beams", 40),
        "deskSmoke": get_json("/api/health/desk-smoke?run=0", 20),
        "claimsOutstanding": {
            "summary": get_json("/api/softdent/claims-outstanding", 40),
            "count": len(
                (get_json("/api/softdent/claims-outstanding", 40) or {}).get("claims") or []
            ),
        },
        "qbRevenue": get_json("/api/qb/monthly-revenue", 20),
        "softdentReportPullPolicy": get_json("/api/apex/hal/softdent-report-pull", 30),
        "collectionsGap": get_json("/api/apex/hal/collections-gap", 15),
        "unifiedSnapshot": get_json("/api/apex/unified/snapshot", 15),
        "apiSurfaceSample": api_surface,
        "nr2Architecture": {
            "role": "financial_ops_overlay_not_pms",
            "softdentMode": "read_only_gui_pulls_and_imports",
            "quickbooksMode": "csv_cache_import",
            "halMode": "local_policy_kb_automation",
            "uiMode": "optical_interferometer_desk",
            "periodClose": "shadow_systemOfRecord_false",
            "cloudHal": "disabled_pending_baa",
        },
    }


def main() -> int:
    key_name, api_key, base_url = resolve_api_and_endpoint()
    if not api_key:
        print("No API key", file=sys.stderr)
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

    audit = live_audit()
    prior = []
    for name, lim in (
        ("MOONSHOT_TOTAL_FUNCTIONABILITY_2026-07-15.md", 3000),
        ("MOONSHOT_PROGRAM_AFTER_MORNING_BUNDLE_2026-07-16.md", 2500),
        ("MOONSHOT_WHATS_NEXT_AFTER_NR2_12073_2026-07-16.md", 2000),
    ):
        path = DOCS / name
        if path.is_file():
            prior.append(f"### {name}\n{path.read_text(encoding='utf-8', errors='replace')[:lim]}")

    user = (
        f"OPERATOR REQUEST (verbatim): {OPERATOR_REQUEST_VERBATIM}\n\n"
        f"CLOUD PMS COMPETITIVE RESEARCH (Curve / Henry Schein / Dentrix Ascend):\n"
        f"{CLOUD_PMS_RESEARCH}\n\n"
        f"LIVE NR2 AUDIT:\n```json\n{json.dumps(audit, indent=2, default=str)[:36000]}\n```\n\n"
        + ("PRIOR NR2 MOONSHOT DOCS:\n" + "\n\n".join(prior) if prior else "")
        + "\n\nCan NR2 be augmented to function comparably? Return markdown REPORT only. CONSULT ONLY."
    )

    body = {
        "model": model,
        "temperature": 1 if "moonshot" in (base_url or "").lower() else 0.3,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
        "max_tokens": 8000,
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
        headers["X-Title"] = "NR2 Cloud PMS Parity Consult"

    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=700, context=CTX) as resp:
            raw = json.loads(resp.read().decode("utf-8", "replace"))
        text = extract_message_content(raw) or ""
        status = "ok"
    except Exception as exc:  # noqa: BLE001
        print(f"Moonshot call failed: {exc}", flush=True)
        raw = {"error": str(exc)}
        text = f"Moonshot call failed: {exc}"
        status = "error"

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (OUT / f"moonshot_cloud_pms_parity_{stamp}.json").write_text(
        json.dumps(raw, indent=2)[:400000], encoding="utf-8"
    )
    (OUT / f"moonshot_cloud_pms_parity_audit_{stamp}.json").write_text(
        json.dumps(audit, indent=2, default=str)[:250000], encoding="utf-8"
    )

    header = (
        f"# Moonshot AI — Cloud PMS Parity Augmentation (CONSULT ONLY)\n\n"
        f"**Date:** {DATE}\n"
        f"**Model:** `{model}`\n"
        f"**Key:** {key_name}\n"
        f"**Status:** {status}\n"
        f"**Repo root:** `{REPO}`\n"
        f"**Build:** `nr2-12073-excel-gate-all-next`\n"
        f"**Script:** `scripts/run_moonshot_cloud_pms_parity_consult.py`\n"
        f"**Apply:** DO NOT APPLY until operator approves.\n\n"
        f"## Operator request (verbatim)\n\n> {OPERATOR_REQUEST_VERBATIM}\n\n---\n\n"
    )
    md = header + (text.strip() or "_(empty)_") + "\n"
    md_path = DOCS / f"MOONSHOT_CLOUD_PMS_PARITY_{DATE}.md"
    md_path.write_text(md, encoding="utf-8")
    (OUT / md_path.name).write_text(md, encoding="utf-8")
    print("Wrote", md_path)
    print("Status", status, "chars", len(text))
    return 0 if status == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
