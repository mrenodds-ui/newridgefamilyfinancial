"""Moonshot AI — Full program upgrade audit (8B/30B orchestrator + SoftDent/QB automation).

CONSULT ONLY. Operator request VERBATIM. Await approval before applying code.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / ".local_logs" / "moonshot_financial_eval"
DOCS = REPO / "NewRidgeFinancial2" / "docs"
OUT.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)
DATE = datetime.now(timezone.utc).strftime("%Y-%m-%d")

HELPER = (
    REPO
    / "_archive"
    / "2026-07-10"
    / ".local_logs"
    / "moonshot_financial_eval"
    / "_run_moonshot_eval.py"
)
sys.path.insert(0, str(HELPER.parent))
from _run_moonshot_eval import extract_message_content, resolve_api_and_endpoint  # noqa: E402

OPERATOR_REQUEST_VERBATIM = """
You are an expert senior full-stack engineer, data architect, and AI systems integrator specializing in dental practice management software. 
I need you to audit, refactor, and massively upgrade my self-built dental practice financial dashboard. This dashboard is running in Chrome and integrates with SoftDent (via exports) and QuickBooks. It uses local/API-connected 8B and 30B LLMs. 
Currently, the SoftDent and QuickBooks integration is only partially functional via manual exports. I want this system to become fully functional, highly polished, beautifully organized, and driven by my AI models acting as the core "program manager."
Please evaluate my existing codebase and provide the complete, production-ready code to achieve the following:
### 1. AI Models as Program Manager (8B & 30B Integration)
* Establish a clear hierarchy: Use the 8B model for fast, real-time widget data parsing, text summaries, and UI UI-routing triggers. Use the 30B model for deep financial forecasting, cross-referencing SoftDent ledger data with QuickBooks, and generating monthly practice health audits.
* Build an "AI Orchestrator" middleware layer that routes user queries or data updates to the correct model.
* Implement structured JSON outputs from the LLMs so the dashboard widgets can read and render the AI's insights dynamically without breaking the UI.
### 2. Full SoftDent & QuickBooks Data Automation
* Build robust, fault-tolerant parsers for SoftDent and QuickBooks CSV/Excel exports.
* Map SoftDent data (production, collection, case acceptance, patient aging, scheduling metrics) and QuickBooks data (expenses, payroll, net profit, accounts payable) into a unified local database/state management system (e.g.,
""".strip()

SYSTEM = """You are Moonshot AI (kimi-k2 class) — senior NR2 Apex + HAL architect for
NewRidge Family Financial (Kansas dental S-corp; SoftDent + QuickBooks imports;
local HTTPS starship-bridge; Ollama GPU lanes chat8b + escalate30b).

CRITICAL CONSTRAINTS:
1. Answer the OPERATOR REQUEST VERBATIM again (RE-AUDIT #2). The operator message was CUT OFF
   mid-sentence at "unified local database/state management system (e.g.," — note truncation,
   assume SQLite/NR2 app_data as unified store. Deliver a complete consult for sections 1–2
   against the LIVE codebase NOW (build hal-10480), not earlier states.
2. ALREADY SHIPPED — do NOT rebuild:
   - MUST I0–I4 (hal-10471..10475): orchestrator shell (flag default OFF), structured insights,
     DEF-001 Collections honesty, nr2_unified.db, integration gates
   - SHOULD S0–S3 (hal-10479): QB payroll/AP + SSN redact, ERA aggregates + ERA_835_AVAILABLE,
     proactive health monitor CLI, orchestrator opt-in GA docs (default still OFF)
   - NICE N0 (hal-10480): insight SSE (/api/apex/hal/insight-stream) + 5s poll fallback
3. CONSULT ONLY — DO NOT APPLY code. Paste-ready sketches labeled CONSULT ONLY. Wait for approve.
4. Ground EVERY recommendation in LIVE FACTS + attached excerpts. Evolve NR2 packs; no rewrite;
   no SoftDent write-back; never invent dollars; PHI local; empty ≠ $0.
5. Map CURRENT (post MUST+SHOULD+N0) vs TARGET. Rank ONLY remaining gaps MUST/SHOULD/NICE
   with S/M/L effort and next-wave phases. Call out whether flipping NR2_AI_ORCHESTRATOR
   default ON is the remaining product decision.
6. End with APPROVAL CHECKLIST for next work only.

OUTPUT FORMAT (strict markdown):
# Verdict — AI Program Manager re-audit #2 (post MUST+SHOULD+N0)
## 0. Operator Intent (quote; note truncation; consult-only re-run)
## 1. Current Architecture Audit (what exists at hal-10480)
### 1A Model lanes & orchestrator (flag still OFF)
### 1B SoftDent + DEF-001 + ERA aggregates
### 1C QuickBooks payroll/AP + expenses
### 1D Unified DB + practice_health_snapshot
### 1E Structured insights + SSE widget binding
## 2. Gap Map — REMAINING only
Table: Area | Status | Gap | Effort | Depends on
## 3. Target Architecture (next wave only)
## 4. Coding Plan — Phase T0..Tn (CONSULT ONLY sketches for remaining work)
## 5. MUST / SHOULD / NICE ranked table (remaining)
## 6. Risks, PHI, SoftDent honesty, Rollback
## 7. Approval Checklist (next wave only)
DO NOT APPLY until operator says approve / proceed.
"""


def _truncate(text: str, max_lines: int) -> str:
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text
    return "\n".join(lines[:max_lines]) + f"\n... [{len(lines) - max_lines} lines truncated]"


def _extract_lines(path: Path, start_marker: str, end_marker: str | None, max_lines: int) -> str:
    if not path.is_file():
        return "(missing)"
    text = path.read_text(encoding="utf-8", errors="replace")
    start = text.find(start_marker)
    if start < 0:
        return f"(marker not found: {start_marker[:60]})"
    if end_marker:
        end = text.find(end_marker, start + len(start_marker))
        chunk = text[start : (end if end > start else start + 14000)]
    else:
        chunk = text[start : start + 14000]
    return _truncate(chunk, max_lines)


CONTEXT_FILES: list[tuple[str, int]] = [
    ("NewRidgeFinancial2/nr2-build.json", 12),
    ("NewRidgeFinancial2/docs/MOONSHOT_AI_PM_PHASE_N0_APPLIED_2026-07-11.md", 50),
    ("NewRidgeFinancial2/docs/MOONSHOT_AI_PM_PHASE_S3_APPLIED_2026-07-11.md", 60),
    ("NewRidgeFinancial2/docs/MOONSHOT_AI_PM_PHASE_S0_APPLIED_2026-07-11.md", 40),
    ("NewRidgeFinancial2/docs/MOONSHOT_AI_PM_PHASE_I4_APPLIED_2026-07-11.md", 40),
    ("NewRidgeFinancial2/docs/MOONSHOT_AI_PROGRAM_MANAGER_UPGRADE_REAUDIT_2026-07-11.md", 50),
    ("NewRidgeFinancial2/site/data/hal-models.json", 60),
]


def build_context() -> str:
    parts: list[str] = []
    for rel, max_lines in CONTEXT_FILES:
        path = REPO / rel
        if not path.is_file():
            parts.append(f"### FILE: {rel}\n(missing)")
            continue
        body = _truncate(path.read_text(encoding="utf-8", errors="replace"), max_lines)
        ext = path.suffix.lstrip(".") or "txt"
        parts.append(f"### FILE: {rel}\n```{ext}\n{body}\n```")

    for rel, max_lines in (
        ("NewRidgeFinancial2/apex_orchestrator_pack.py", 70),
        ("NewRidgeFinancial2/apex_qb_payroll_pack.py", 60),
        ("NewRidgeFinancial2/apex_softdent_era_pack.py", 50),
        ("NewRidgeFinancial2/apex_health_monitor_pack.py", 50),
        ("NewRidgeFinancial2/apex_insight_sse_pack.py", 60),
        ("NewRidgeFinancial2/apex_unified_db_pack.py", 70),
    ):
        path = REPO / rel
        if path.is_file():
            parts.append(
                f"### FILE: {rel}\n```python\n"
                + _truncate(path.read_text(encoding="utf-8", errors="replace"), max_lines)
                + "\n```"
            )

    parts.append(
        """### LIVE FACTS (hal-10480 — RE-AUDIT #2 after MUST+SHOULD+N0)
- Epoch: NR2 Apex starship bridge (local HTTPS Chrome). SoftDent + QuickBooks import-backed.
- MUST I0–I4 + SHOULD S0–S3 + NICE N0 SHIPPED on builds through hal-10480.
- Orchestrator flag NR2_AI_ORCHESTRATOR still default OFF (opt-in burn-in docs exist).
- SoftDent: DEF-001 honesty; ERA aggregates in nr2_unified; ERA_835_AVAILABLE proposal only.
- QuickBooks: expenses + payroll/AP ingest paths (SSN redact); missing export → pending ≠ $0.
- Unified: nr2_unified.db with SoftDent periods, QB expenses/payroll/AP, ERA aggregates, snapshot view.
- Insights: structured JSON schemas + PHI reject; SSE stream + 5s poll for hal-ai-insight.
- Proactive monitor CLI exists; requires orchestrator flag ON to run deep lane.
- Operator request (verbatim) re-submitted. CONSULT ONLY — remaining gaps only.
- Hard rules: never invent $; PHI local; empty widgets stay empty; no SoftDent write-back.
"""
    )
    return "\n\n".join(parts)


def main() -> int:
    key_name, api_key, base_url = resolve_api_and_endpoint()
    if not api_key:
        print("No Moonshot/OpenRouter API key.", file=sys.stderr)
        return 1

    if "moonshot" in (base_url or "").lower():
        model = str(os.getenv("MOONSHOT_MODEL") or "kimi-k2.5").strip()
    else:
        model = str(
            os.getenv("MOONSHOT_MODEL") or os.getenv("KIMI_K2_MODEL") or "moonshotai/kimi-k2"
        ).strip()

    print(f"Using {key_name} @ {base_url} model={model}")
    user = (
        "OPERATOR REQUEST (VERBATIM — do not rewrite) — RE-RUN #2 after MUST+SHOULD+N0:\n\n"
        f"{OPERATOR_REQUEST_VERBATIM}\n\n"
        "NOTE: Same truncated operator message. MUST I0–I4, SHOULD S0–S3, and NICE N0 "
        "(insight SSE) are already shipped on hal-10480. Re-audit ONLY remaining gaps. "
        "CONSULT ONLY — do not apply. Wait for approval.\n\n"
        "## Codebase context\n\n"
        + build_context()
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
        "temperature": 1.0,
        "max_tokens": 16000,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    if "openrouter" in base_url.lower():
        headers["HTTP-Referer"] = "https://github.com/NewRidgeFamilyFinancial"
        headers["X-Title"] = "NR2 AI Program Manager Upgrade Consult"

    print("Calling Moonshot AI (consult only — will not apply)...")
    req = urllib.request.Request(
        base_url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=3600) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        content = extract_message_content(body)
        status = "ok"
    except urllib.error.HTTPError as exc:
        content = f"HTTP {exc.code}: {exc.read().decode('utf-8', errors='replace')[:4000]}"
        status = f"HTTP {exc.code}"
    except Exception as exc:
        content = str(exc)
        status = "error"

    header = (
        f"# Moonshot AI — AI Program Manager Upgrade RE-AUDIT #2 (CONSULT ONLY)\n\n"
        f"**Date:** {DATE}  \n"
        f"**Model:** {model}  \n"
        f"**Key:** {key_name}  \n"
        f"**Endpoint:** {base_url}  \n"
        f"**Status:** {status}  \n"
        f"**Build reviewed:** hal-10480 (post MUST+SHOULD+N0)  \n"
        f"**Prior:** `MOONSHOT_AI_PROGRAM_MANAGER_UPGRADE_REAUDIT_2026-07-11.md`  \n"
        f"**Script:** `scripts/run_moonshot_ai_program_manager_upgrade_consult.py`  \n"
        f"**Apply:** DO NOT APPLY / DO NOT CODE until operator approves.\n\n"
        f"## Operator request (verbatim)\n\n"
        f"> {OPERATOR_REQUEST_VERBATIM}\n\n"
        f"---\n\n"
    )
    full = header + (content or "(empty)")
    out_file = OUT / f"MOONSHOT_AI_PROGRAM_MANAGER_UPGRADE_REAUDIT2_{DATE}.md"
    doc_file = DOCS / f"MOONSHOT_AI_PROGRAM_MANAGER_UPGRADE_REAUDIT2_{DATE}.md"
    out_file.write_text(full, encoding="utf-8")
    doc_file.write_text(full, encoding="utf-8")
    print(out_file)
    print(doc_file)
    print(f"chars={len(content or '')} status={status}")
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
