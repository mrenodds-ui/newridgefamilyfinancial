"""Moonshot AI — Fix paid claims still appearing on Claims page outstanding list.

Operator: ask moonshot how to fix claims that have already been paid that should
not be on the claims list — separate from claims still out waiting to be paid.
CONSULT ONLY — report.
"""

from __future__ import annotations

import json
import os
import sqlite3
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

OPERATOR_REQUEST_VERBATIM = (
    "ask moonshot ai how to fix claims that have already been paid that should "
    "not be on the claims list in claims page from the claims that are still out "
    "and waiting to be paid how to fix. report"
)

SYSTEM = """You are Moonshot AI — principal architect for NewRidgeFinancial2 (NR2).
CONSULT ONLY — DO NOT APPLY CODE. Produce a REPORT the office can act on.

Operator problem (verbatim intent):
Claims page still shows claims that SoftDent staff know are ALREADY PAID.
Those paid claims must be removed from the outstanding list so only claims
still waiting for payment remain.

CURRENT CODE (real paths — do not invent):
- Claims list API: `nr2_softdent_daily.claims_outstanding` →
  `GET /api/softdent/claims-outstanding`
- Optical UI: `site/nr2-optical-page-claims.js` / `.html`
- Open-status SQL filter on `sd_claims` (drops PAID/CLOSED/DENIED/COMPLETE…)
- Second filter: `_filter_unpaid_claim_rows` +
  `softdent_operational_pipeline.claim_is_unpaid_on_txn` using SoftDent
  Trans-for-a-Period XLS (insurance pay code family `2` / write-offs)
- Claim ids are often `TXN-YYYYMMDD-MRN` or `DS-…` synthesized from ledger/daysheet
- Empty ≠ $0; SoftDent READ-ONLY; Output Options Excel OR Print Preview only
  (never Printer, never File)

LIVE AUDIT facts will be attached. Known gaps from prior engineering:
- TXN settlement filter already drops some paid DS rows, but leftover rows
  often stay `Pending Review` with no TXN settlement match
- TXN XLS window can lag (ends before today) so recent insurance payments
  never suppress the claim
- Many payers still generic `Insurance`
- ERA inbox / SoftDent Claims Aging report may be better truth for
  “still outstanding” than stale synthesized sd_claims status

YOUR JOB: Recommend THE concrete fix package to separate paid vs still-out
claims on the Claims page, with ordered backlog. Prefer REAL
NewRidgeFinancial2/ files. Prefer SoftDent Excel/Preview truth over inventing
dollars or statuses.

OUTPUT (strict markdown):
# Verdict (one sentence)
## 0. Operator Intent (verbatim)
## 1. Root cause diagnosis (what makes paid claims still appear — cite LIVE AUDIT)
## 2. Recommended FIX package (name, why now, effort, REAL files under
   NewRidgeFinancial2/, operator SoftDent pulls if needed, validation gate)
## 3. How paid vs still-waiting should be decided (truth order / rules —
   empty ≠ $0; never invent paid)
## 4. Ordered backlog AFTER #1 (2–4)
## 5. What NOT to do
## 6. Acceptance criteria (Claims page must show only still-out)
## 7. Executive Summary (5 bullets)
## 8. Approval Checklist
DO NOT APPLY CODE. Never invent SoftDent Select File Name paths or $0 from empty.
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


def filter_audit() -> dict:
    sys.path.insert(0, str(NR2))
    try:
        from softdent_odbc_extract import resolve_sd_sqlite_db
        from softdent_operational_pipeline import (
            claim_is_unpaid_on_txn,
            load_txn_settlement_context,
            resolve_softdent_transactions_xls_path,
        )
        from nr2_softdent_daily import (
            _filter_unpaid_claim_rows,
            _patient_name_to_id_index,
            _resolve_claim_patient_id,
        )
    except Exception as exc:  # noqa: BLE001
        return {"error": type(exc).__name__, "msg": str(exc)[:400]}

    db = resolve_sd_sqlite_db()
    txn_path = resolve_softdent_transactions_xls_path()
    try:
        txs, idx = load_txn_settlement_context()
    except Exception as exc:  # noqa: BLE001
        return {"error": "txn_load_failed", "msg": str(exc)[:400]}

    dates = sorted(
        {str(r.get("reportDate") or "")[:10] for r in txs if r.get("reportDate")}
    )
    open_where = """
        COALESCE(claim_amount, 0) > 0
          AND UPPER(TRIM(COALESCE(claim_status, ''))) NOT IN (
            'PAID', 'CLOSED', 'DENIED', 'COMPLETE', 'COMPLETED',
            'DONE', 'SETTLED', 'CANCELLED', 'CANCELED', 'VOID', 'VOIDED',
            'DENIED-FINAL'
          )
          AND UPPER(TRIM(COALESCE(claim_status, ''))) NOT LIKE 'PAID%'
          AND UPPER(TRIM(COALESCE(claim_status, ''))) NOT LIKE '%COMPLETE%'
    """
    if not db or not Path(db).is_file():
        return {
            "db": str(db),
            "txnPath": str(txn_path) if txn_path else None,
            "txnRows": len(txs),
            "error": "sd_sqlite_missing",
        }

    conn = sqlite3.connect(str(db))
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT claim_id, patient_name, payer, service_date, claim_amount, claim_status "
            "FROM sd_claims WHERE " + open_where
        )
        cands = list(cur.fetchall())
        name_to_id = _patient_name_to_id_index(conn)
        kept = _filter_unpaid_claim_rows(
            cands, name_to_id=name_to_id, transactions=txs, settlement_index=idx
        )
        dropped_samples = []
        for row in cands:
            claim_id, patient, payer, service_date, amount, status = row
            pid = _resolve_claim_patient_id(
                str(claim_id or ""), str(patient or ""), name_to_id
            )
            unpaid = claim_is_unpaid_on_txn(
                patient_id=pid,
                service_date=str(service_date or ""),
                claim_id=str(claim_id or ""),
                claim_status=str(status or ""),
                transactions=txs,
                settlement_index=idx,
            )
            if not unpaid and len(dropped_samples) < 6:
                dropped_samples.append(
                    {
                        "claimId": claim_id,
                        "patientId": pid,
                        "serviceDate": service_date,
                        "amount": amount,
                        "status": status,
                        "payer": payer,
                    }
                )
        kept_samples = []
        for row in kept[:8]:
            claim_id, patient, payer, service_date, amount, status = row
            pid = _resolve_claim_patient_id(
                str(claim_id or ""), str(patient or ""), name_to_id
            )
            kept_samples.append(
                {
                    "claimId": claim_id,
                    "patientId": pid,
                    "serviceDate": service_date,
                    "amount": amount,
                    "status": status,
                    "payer": payer,
                    "txnSettlementMatch": False,
                }
            )
        id_prefix = {}
        for row in kept:
            cid = str(row[0] or "")
            pref = cid.split("-", 1)[0] if cid else "?"
            id_prefix[pref] = id_prefix.get(pref, 0) + 1
        return {
            "db": str(db),
            "txnPath": str(txn_path) if txn_path else None,
            "txnRows": len(txs),
            "settlementAccounts": len(idx),
            "txnDateMin": dates[0] if dates else None,
            "txnDateMax": dates[-1] if dates else None,
            "candidateOpenStatusCount": len(cands),
            "afterTxnFilterCount": len(kept),
            "droppedAsPaidByTxn": len(cands) - len(kept),
            "keptIdPrefixes": id_prefix,
            "sampleDroppedAsPaid": dropped_samples,
            "sampleStillShownAsOutstanding": kept_samples,
            "note": (
                "All open sd_claims candidates currently claim_status=Pending Review; "
                "TXN filter is the only paid suppressor today."
            ),
        }
    finally:
        conn.close()


def live_audit() -> dict:
    build = {}
    try:
        build = json.loads((NR2 / "nr2-build.json").read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        build = {"error": str(exc)}
    claims = get_json("/api/softdent/claims-outstanding?limit=8", 30)
    era = get_json("/api/apex/hal/era-inbox/status", 20)
    smoke = get_json("/api/health/desk-smoke?run=0", 15)
    return {
        "repoRoot": str(REPO),
        "nr2Root": str(NR2),
        "build": build,
        "todayLocalHint": "2026-07-16",
        "codeSurfaces": {
            "claimsOutstanding": "NewRidgeFinancial2/nr2_softdent_daily.py::claims_outstanding",
            "txnUnpaidFilter": (
                "NewRidgeFinancial2/softdent_operational_pipeline.py::claim_is_unpaid_on_txn"
            ),
            "claimsPageJs": "NewRidgeFinancial2/site/nr2-optical-page-claims.js",
            "bridge": "NewRidgeFinancial2/softdent_outstanding_claims_bridge.py",
            "eraInbox": "NewRidgeFinancial2/nr2_era_inbox.py",
        },
        "docsPresent": {
            "claimsPageListApplied": (
                DOCS / "MOONSHOT_CLAIMS_PAGE_LIST_DOSSIER_APPLIED_2026-07-16.md"
            ).is_file(),
            "outstandingBridgeApplied": (
                DOCS / "MOONSHOT_OUTSTANDING_CLAIMS_BRIDGE_HAL10580_APPLIED_2026-07-13.md"
            ).is_file(),
            "p1FinancialIntelApplied": (
                DOCS / "MOONSHOT_P1_FINANCIAL_INTEL_APPLIED_2026-07-16.md"
            ).is_file(),
        },
        "live": {
            "claimsOutstandingApi": {
                "hasData": claims.get("hasData") if isinstance(claims, dict) else None,
                "count": claims.get("count") if isinstance(claims, dict) else None,
                "totalOutstanding": (
                    claims.get("totalOutstanding") if isinstance(claims, dict) else None
                ),
                "source": claims.get("source") if isinstance(claims, dict) else None,
                "sample": (claims.get("claims") or [])[:6]
                if isinstance(claims, dict)
                else [],
                "error": claims.get("error") if isinstance(claims, dict) else None,
            },
            "eraInboxStatus": {
                "ok": era.get("ok") if isinstance(era, dict) else None,
                "chipStatus": era.get("chipStatus") if isinstance(era, dict) else None,
                "count": era.get("count") if isinstance(era, dict) else None,
                "error": era.get("error") or era.get("msg")
                if isinstance(era, dict)
                else None,
            },
            "deskSmokeLast": {
                "status": smoke.get("status") if isinstance(smoke, dict) else None,
                "deskProof": smoke.get("deskProof") if isinstance(smoke, dict) else None,
            },
        },
        "paidVsOutstandingFilterAudit": filter_audit(),
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
    audit_path = OUT / f"moonshot_claims_paid_vs_outstanding_audit_{DATE}.json"
    audit_path.write_text(json.dumps(audit, indent=2)[:400000], encoding="utf-8")
    print("Audit", audit_path, flush=True)

    user = (
        f"OPERATOR REQUEST (verbatim):\n{OPERATOR_REQUEST_VERBATIM}\n\n"
        f"LIVE AUDIT:\n```json\n{json.dumps(audit, indent=2)[:120000]}\n```\n\n"
        "Diagnose why paid claims still appear and prescribe THE fix so Claims page "
        "lists only still-out / waiting-to-be-paid claims. Markdown REPORT only. "
        "CONSULT ONLY."
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
            os.getenv("OPENROUTER_X_TITLE")
            or "NR2 Claims Paid vs Outstanding Fix Consult"
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
    raw_path = OUT / f"moonshot_claims_paid_vs_outstanding_{stamp}.json"
    md_path = DOCS / f"MOONSHOT_CLAIMS_PAID_VS_OUTSTANDING_FIX_{DATE}.md"
    raw_path.write_text(json.dumps(raw, indent=2)[:500000], encoding="utf-8")
    header = (
        f"# Moonshot AI — Claims Paid vs Outstanding Fix (CONSULT ONLY)\n\n"
        f"**Date:** {DATE}\n"
        f"**Model:** `{model}`\n"
        f"**Key:** {key_name}\n"
        f"**Script:** `scripts/run_moonshot_claims_paid_vs_outstanding_consult.py`\n"
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
