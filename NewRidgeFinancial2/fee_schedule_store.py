"""Office fee-schedule CDT lookup — cite schedule + amount; never invent dollars."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

NR2_ROOT = Path(__file__).resolve().parent
FEE_SCHEDULE_PATH = NR2_ROOT / "data" / "fee_schedule.json"

CDT_RE = re.compile(r"\b(D\d{4}(?:\.\d{1,2})?)\b", re.IGNORECASE)
FEE_QUERY_RE = re.compile(
    r"\b(fee\s*schedule|allowed\s*amount|allowed\s*fee|contracted\s*fee|ucr|"
    r"practice\s*amount|co-?45|underpay(?:ment)?|fee\s*for)\b",
    re.IGNORECASE,
)
TOKEN_RE = re.compile(r"[a-z0-9]{2,}")


def _tokenize(text: str) -> set[str]:
    return set(TOKEN_RE.findall(str(text or "").lower()))


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip().lower())


@lru_cache(maxsize=1)
def load_fee_schedule() -> dict[str, Any]:
    if not FEE_SCHEDULE_PATH.is_file():
        return {"version": 0, "schedules": [], "carrierIndex": [], "codes": {}}
    try:
        data = json.loads(FEE_SCHEDULE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"version": 0, "schedules": [], "carrierIndex": [], "codes": {}}
    if not isinstance(data, dict):
        return {"version": 0, "schedules": [], "carrierIndex": [], "codes": {}}
    data.setdefault("schedules", [])
    data.setdefault("carrierIndex", [])
    data.setdefault("codes", {})
    return data


def fee_schedule_summary() -> dict[str, Any]:
    data = load_fee_schedule()
    codes = data.get("codes") or {}
    return {
        "ok": True,
        "version": data.get("version"),
        "importedAt": data.get("importedAt"),
        "source": data.get("source"),
        "sheet": data.get("sheet"),
        "scheduleCount": len(data.get("schedules") or []),
        "carrierIndexCount": len(data.get("carrierIndex") or []),
        "codeCount": len(codes) if isinstance(codes, dict) else 0,
        "path": str(FEE_SCHEDULE_PATH),
    }


def extract_cdt_codes(query: str) -> list[str]:
    found = [m.group(1).upper() for m in CDT_RE.finditer(str(query or ""))]
    # normalize D2740.1 → D2740 when base exists; keep as-is otherwise
    out: list[str] = []
    seen: set[str] = set()
    for code in found:
        base = code.split(".", 1)[0]
        pick = base if base not in seen else code
        if pick not in seen:
            seen.add(pick)
            out.append(pick)
    return out


def query_wants_fee_lookup(query: str) -> bool:
    q = str(query or "")
    if extract_cdt_codes(q):
        return True
    return bool(FEE_QUERY_RE.search(q))


def _score_schedule(query: str, query_tokens: set[str], schedule: dict[str, Any]) -> int:
    name = str(schedule.get("name") or "")
    aliases = [str(a) for a in (schedule.get("aliases") or [])]
    haystack = " ".join([name, " ".join(aliases), str(schedule.get("id") or "")]).lower()
    s_tokens = _tokenize(haystack)
    score = len(query_tokens & s_tokens)
    q_norm = _norm(query)
    name_n = _norm(name)
    if q_norm and q_norm == name_n:
        score += 14
    elif q_norm and (q_norm in name_n or name_n in q_norm):
        score += 8
    for alias in aliases:
        a_n = _norm(alias)
        if q_norm and q_norm == a_n:
            score += 12
        elif q_norm and len(a_n) >= 4 and a_n in q_norm:
            score += 5
        elif any(t in a_n for t in query_tokens if len(t) >= 4):
            score += 2
    # Prefer practice amount only when explicitly asked
    sid = str(schedule.get("id") or "")
    if sid == "practice_amount":
        if re.search(r"\b(practice\s*amount|ucr|office\s*fee)\b", query, re.I):
            score += 10
        else:
            score -= 3
    return score


def resolve_schedules(query: str, *, limit: int = 3) -> list[dict[str, Any]]:
    """Resolve fee-schedule columns from payer/schedule text in the query."""
    data = load_fee_schedule()
    schedules = [s for s in (data.get("schedules") or []) if isinstance(s, dict)]
    q = str(query or "").strip()
    if not q:
        return []
    q_tokens = _tokenize(q)
    # Strip CDT codes from scoring so D2740 doesn't dilute payer match
    q_for_score = CDT_RE.sub(" ", q)
    q_tokens = _tokenize(q_for_score) or q_tokens

    scored: list[tuple[int, dict[str, Any]]] = []
    for schedule in schedules:
        score = _score_schedule(q_for_score, q_tokens, schedule)
        if score > 0:
            scored.append((score, schedule))

    # Carrier index boost: map insurance company → schedule id
    for row in data.get("carrierIndex") or []:
        if not isinstance(row, dict):
            continue
        company = str(row.get("insuranceCompany") or "")
        fee_name = str(row.get("feeSchedule") or "")
        resolved = str(row.get("resolvedScheduleId") or "")
        c_tokens = _tokenize(f"{company} {fee_name}")
        overlap = len(q_tokens & c_tokens)
        if overlap <= 0 and not (
            _norm(company) and (_norm(company) in _norm(q_for_score) or _norm(q_for_score) in _norm(company))
        ):
            continue
        boost = overlap * 2
        if _norm(company) and _norm(company) in _norm(q_for_score):
            boost += 6
        if not resolved:
            continue
        for schedule in schedules:
            if str(schedule.get("id")) == resolved:
                scored.append((boost + 4, schedule))
                break

    # Dedupe by schedule id, keep best score
    best: dict[str, tuple[int, dict[str, Any]]] = {}
    for score, schedule in scored:
        sid = str(schedule.get("id") or "")
        if not sid:
            continue
        prev = best.get(sid)
        if prev is None or score > prev[0]:
            best[sid] = (score, schedule)
    ranked = sorted(best.values(), key=lambda pair: pair[0], reverse=True)
    if not ranked:
        return []
    top_score = ranked[0][0]
    # When a clear payer/schedule match exists, drop weak "Dental"-token noise.
    min_keep = max(3, top_score - 2) if top_score >= 6 else 1
    tight = [(score, s) for score, s in ranked if score >= min_keep]
    return [s for _, s in tight[: max(1, int(limit))]]


def lookup_cdt(
    code: str,
    payer_or_schedule: str = "",
    *,
    schedule_limit: int = 3,
) -> dict[str, Any]:
    """Look up one CDT code; optionally filter/rank by payer or schedule name."""
    data = load_fee_schedule()
    codes = data.get("codes") if isinstance(data.get("codes"), dict) else {}
    cdt = str(code or "").strip().upper()
    if "." in cdt:
        cdt = cdt.split(".", 1)[0]
    row = codes.get(cdt)
    if not isinstance(row, dict):
        return {
            "ok": False,
            "code": cdt,
            "error": "CDT code not found in office fee schedule export",
            "amounts": [],
        }

    amounts_map = row.get("amounts") if isinstance(row.get("amounts"), dict) else {}
    schedules = {str(s.get("id")): s for s in (data.get("schedules") or []) if isinstance(s, dict)}
    hint = str(payer_or_schedule or "").strip()
    resolved = resolve_schedules(hint, limit=schedule_limit) if hint else []

    amount_rows: list[dict[str, Any]] = []
    if resolved:
        for schedule in resolved:
            sid = str(schedule.get("id") or "")
            if sid not in amounts_map:
                continue
            amount_rows.append(
                {
                    "scheduleId": sid,
                    "scheduleName": schedule.get("name") or sid,
                    "amount": amounts_map[sid],
                    "adjustedAmount": (row.get("adjustedAmounts") or {}).get(sid)
                    if isinstance(row.get("adjustedAmounts"), dict)
                    else None,
                }
            )
    if not amount_rows:
        # Return all known schedule amounts (capped) when no payer match
        for sid, amount in amounts_map.items():
            schedule = schedules.get(sid) or {"id": sid, "name": sid}
            amount_rows.append(
                {
                    "scheduleId": sid,
                    "scheduleName": schedule.get("name") or sid,
                    "amount": amount,
                    "adjustedAmount": (row.get("adjustedAmounts") or {}).get(sid)
                    if isinstance(row.get("adjustedAmounts"), dict)
                    else None,
                }
            )
        # Prefer non-practice first when dumping all
        amount_rows.sort(key=lambda r: (0 if r["scheduleId"] != "practice_amount" else 1, str(r["scheduleName"])))
        amount_rows = amount_rows[: max(1, int(schedule_limit) + 1)]

    return {
        "ok": True,
        "code": cdt,
        "category": row.get("category") or "",
        "sourceSheet": data.get("sheet") or "Data - Main 2025",
        "resolvedSchedules": [{"id": s.get("id"), "name": s.get("name")} for s in resolved],
        "amounts": amount_rows,
    }


def lookup_fees(query: str, *, limit: int = 3, schedule_limit: int = 3) -> list[dict[str, Any]]:
    codes = extract_cdt_codes(query)
    if not codes:
        # Schedule-only query: return resolved schedules without amounts
        schedules = resolve_schedules(query, limit=schedule_limit)
        if not schedules:
            return []
        return [
            {
                "ok": True,
                "code": "",
                "category": "",
                "sourceSheet": load_fee_schedule().get("sheet") or "",
                "resolvedSchedules": [{"id": s.get("id"), "name": s.get("name")} for s in schedules],
                "amounts": [],
                "note": "No CDT code in query — resolved fee schedule name(s) only. Ask with a D#### code for amounts.",
            }
        ]
    hint = CDT_RE.sub(" ", str(query or "")).strip()
    results = [lookup_cdt(code, hint, schedule_limit=schedule_limit) for code in codes[: max(1, int(limit))]]
    return results


def _fmt_money(val: Any) -> str:
    if val is None or val == "":
        return "—"
    try:
        num = float(val)
    except (TypeError, ValueError):
        return str(val)
    if abs(num - round(num)) < 1e-9:
        return f"${int(round(num))}"
    return f"${num:,.2f}"


def format_fee_hits(hits: list[dict[str, Any]]) -> str:
    if not hits:
        return ""
    lines = [
        "Fee schedule matches (office workbook amounts — cite schedule name; verify on EOB for member-specific allowed):"
    ]
    for hit in hits:
        if not hit.get("ok") and hit.get("code"):
            lines.append(f"- {hit.get('code')}: not found in fee schedule export.")
            continue
        code = str(hit.get("code") or "").strip()
        category = str(hit.get("category") or "").strip()
        note = str(hit.get("note") or "").strip()
        if code:
            head = f"- {code}"
            if category:
                head += f" ({category})"
            lines.append(head + ":")
        elif hit.get("resolvedSchedules"):
            lines.append("- Schedule resolution (no CDT in query):")
        for amt in hit.get("amounts") or []:
            name = amt.get("scheduleName") or amt.get("scheduleId")
            piece = f"  • {name}: {_fmt_money(amt.get('amount'))}"
            adj = amt.get("adjustedAmount")
            if adj is not None and adj != "" and adj != amt.get("amount"):
                piece += f" (adjusted sheet: {_fmt_money(adj)})"
            lines.append(piece)
        for sched in hit.get("resolvedSchedules") or []:
            if code and hit.get("amounts"):
                break
            lines.append(f"  • {sched.get('name') or sched.get('id')}")
        if note:
            lines.append(f"  • {note}")
    lines.append("Source: office Fee Schedule Spreadsheet (Data - Main 2025). Do not invent amounts not listed above.")
    return "\n".join(lines)
