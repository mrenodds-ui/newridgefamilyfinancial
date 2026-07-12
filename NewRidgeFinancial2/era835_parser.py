"""ERA/835 parse and fuzzy claim matching — Moonshot Phase 9 + REC-005 depth.

Loop 2100 (CLP) + Loop 2110 (SVC) with claim- and service-line CAS (CARC)
and LQ remark codes (RARC). Empty ≠ $0; no invented dollars; patient names
only when present on the EDI (staff-visible); never invent PHI.
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any


def _parse_money(value: Any) -> float:
    raw = str(value or "").replace("$", "").replace(",", "").strip()
    try:
        return float(raw) if raw else 0.0
    except ValueError:
        return 0.0


def _extract_cas_codes(fields: list[str]) -> list[dict[str, Any]]:
    """Parse CAS*GROUP*REASON*AMOUNT*… triples into structured rows + CO-45 labels."""
    out: list[dict[str, Any]] = []
    if len(fields) < 3:
        return out
    group = str(fields[1] or "").strip().upper()
    i = 2
    while i < len(fields):
        reason = str(fields[i] or "").strip()
        amount = _parse_money(fields[i + 1] if i + 1 < len(fields) else 0)
        if group and reason and (reason.isdigit() or re.fullmatch(r"[A-Z0-9]+", reason)):
            code = f"{group}-{reason}"
            out.append(
                {
                    "code": code,
                    "group": group,
                    "reason": reason,
                    "amount": amount if amount else None,
                }
            )
        i += 2
    return out


def _extract_proc(proc_raw: str) -> str:
    raw = str(proc_raw or "")
    m = re.search(r"([A-Z]?\d{4,5})", raw)
    if m:
        return m.group(1)[:12]
    cleaned = raw.replace("AD:", "").replace("HC:", "").replace("WK:", "").strip()
    return cleaned[:12]


def _new_claim_segment(fields: list[str]) -> dict[str, Any]:
    return {
        "claimId": fields[1] if len(fields) > 1 else "",
        "status": fields[2] if len(fields) > 2 else "",
        "charged": _parse_money(fields[3] if len(fields) > 3 else 0),
        "paid": _parse_money(fields[4] if len(fields) > 4 else 0),
        "patientName": "",
        "serviceDate": "",
        "casCodes": [],
        "casDetails": [],
        "rarcCodes": [],
        "denialCode": None,
        "denialFlag": False,
        "serviceLines": [],
        "_currentLine": None,
    }


def _finalize_segment(seg: dict[str, Any]) -> dict[str, Any]:
    line = seg.pop("_currentLine", None)
    if isinstance(line, dict):
        lines = seg.setdefault("serviceLines", [])
        if isinstance(lines, list):
            lines.append(line)
    codes = seg.get("casCodes") if isinstance(seg.get("casCodes"), list) else []
    # Roll up service-line CAS into claim-level lists when missing
    for sl in seg.get("serviceLines") or []:
        if not isinstance(sl, dict):
            continue
        for c in sl.get("casCodes") or []:
            if c not in codes:
                codes.append(c)
        for r in sl.get("rarcCodes") or []:
            rlist = seg.setdefault("rarcCodes", [])
            if isinstance(rlist, list) and r not in rlist:
                rlist.append(r)
    seg["casCodes"] = codes
    if not seg.get("denialCode") and codes:
        seg["denialCode"] = codes[0]
    # Denial-ish when status is denied (4) or any CO/OA/PI adjustment present with unpaid gap
    status = str(seg.get("status") or "").strip()
    charged = float(seg.get("charged") or 0)
    paid = float(seg.get("paid") or 0)
    has_adj = bool(codes)
    seg["denialFlag"] = status in {"4", "22", "23"} or (has_adj and paid + 0.005 < charged)
    return seg


def parse_835_text(content: str) -> dict[str, Any]:
    """Parse X12 835 or plain-text ERA extract into payment segments.

    REC-005 depth: Loop 2100 CLP + Loop 2110 SVC with claim/service CAS (CARC)
    and LQ remark codes (RARC). Each segment exposes ``serviceLines``,
    ``casCodes`` / ``casDetails``, ``rarcCodes``, ``denialCode``, ``denialFlag``.
    """
    text = str(content or "")
    segments: list[dict[str, Any]] = []
    if "~" in text or text.startswith("ISA") or "CLP*" in text:
        parts = [p.strip() for p in re.split(r"~|\n", text) if p.strip()]
        current: dict[str, Any] | None = None
        for part in parts:
            fields = part.split("*")
            tag = fields[0] if fields else ""
            if tag == "CLP" or part.startswith("CLP"):
                if current:
                    segments.append(_finalize_segment(current))
                current = _new_claim_segment(fields)
            elif current is None:
                continue
            elif tag == "CAS" or part.startswith("CAS"):
                details = _extract_cas_codes(fields)
                line = current.get("_currentLine")
                target = line if isinstance(line, dict) else current
                for d in details:
                    code = str(d.get("code") or "")
                    if not code:
                        continue
                    codes = target.setdefault("casCodes", [])
                    if isinstance(codes, list) and code not in codes:
                        codes.append(code)
                    det = target.setdefault("casDetails", [])
                    if isinstance(det, list):
                        det.append(d)
                    if not target.get("denialCode"):
                        target["denialCode"] = code
                    if not current.get("denialCode"):
                        current["denialCode"] = code
            elif tag == "SVC" or part.startswith("SVC"):
                prev = current.get("_currentLine")
                if isinstance(prev, dict):
                    lines = current.setdefault("serviceLines", [])
                    if isinstance(lines, list):
                        lines.append(prev)
                proc = _extract_proc(fields[1] if len(fields) > 1 else "")
                charged = _parse_money(fields[2] if len(fields) > 2 else 0)
                paid = _parse_money(fields[3] if len(fields) > 3 else 0)
                current["_currentLine"] = {
                    "procedureCode": proc,
                    "charged": charged,
                    "paid": paid,
                    "casCodes": [],
                    "casDetails": [],
                    "rarcCodes": [],
                    "denialCode": None,
                }
            elif tag == "LQ" or part.startswith("LQ"):
                # LQ*HE*N59 → RARC N59 (remark); keep code only, no free-text invention
                qualifier = str(fields[1] or "").strip().upper() if len(fields) > 1 else ""
                remark = str(fields[2] or "").strip().upper() if len(fields) > 2 else ""
                if remark:
                    code = remark if qualifier in {"", "HE", "RX", "AA"} else f"{qualifier}-{remark}"
                    line = current.get("_currentLine")
                    target = line if isinstance(line, dict) else current
                    rlist = target.setdefault("rarcCodes", [])
                    if isinstance(rlist, list) and code not in rlist:
                        rlist.append(code[:24])
            elif tag == "NM1" or part.startswith("NM1"):
                if len(fields) > 3 and fields[1] == "QC":
                    current["patientName"] = " ".join(fields[3:5]).strip()
            elif tag == "DTM" or part.startswith("DTM"):
                if len(fields) > 2 and fields[1] == "472":
                    current["serviceDate"] = fields[2]
                    line = current.get("_currentLine")
                    if isinstance(line, dict) and not line.get("serviceDate"):
                        line["serviceDate"] = fields[2]
        if current:
            segments.append(_finalize_segment(current))
    else:
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            m_amt = re.search(r"(?:paid|payment|amount)[:\s]+\$?([\d,.]+)", line, re.I)
            m_clm = re.search(r"(?:claim|clm)[#:\s]+([A-Z0-9-]+)", line, re.I)
            m_pat = re.search(r"(?:patient|member)[:\s]+(.+?)(?:\||$)", line, re.I)
            m_dt = re.search(r"(\d{4}[-/]?\d{2}[-/]?\d{2})", line)
            m_cas = re.search(r"\b([A-Z]{2})-(\d{1,3})\b", line)
            m_proc = re.search(r"\b([A-Z]?\d{4,5})\b", line)
            if m_amt or m_clm:
                seg = {
                    "claimId": m_clm.group(1) if m_clm else "",
                    "paid": _parse_money(m_amt.group(1) if m_amt else 0),
                    "patientName": m_pat.group(1).strip() if m_pat else "",
                    "serviceDate": m_dt.group(1) if m_dt else "",
                    "status": "paid",
                    "charged": 0.0,
                    "casCodes": [],
                    "casDetails": [],
                    "rarcCodes": [],
                    "denialCode": None,
                    "denialFlag": False,
                    "serviceLines": [],
                }
                if m_cas:
                    code = f"{m_cas.group(1)}-{m_cas.group(2)}"
                    seg["casCodes"] = [code]
                    seg["denialCode"] = code
                    seg["denialFlag"] = True
                if m_proc:
                    seg["serviceLines"] = [
                        {
                            "procedureCode": m_proc.group(1),
                            "charged": 0.0,
                            "paid": seg["paid"],
                            "casCodes": list(seg["casCodes"]),
                            "casDetails": [],
                            "rarcCodes": [],
                            "denialCode": seg.get("denialCode"),
                        }
                    ]
                segments.append(seg)
    return {
        "ok": True,
        "segments": segments,
        "count": len(segments),
        "rec005Depth": True,
    }


def summarize_835_for_hal(parsed: dict[str, Any] | None = None, *, content: str = "") -> dict[str, Any]:
    """Structured remittance summary for HAL — no invented dollars or denial reasons.

    Omits patient names from the summary text (claim IDs + codes + amounts only).
    """
    data = parsed if isinstance(parsed, dict) else parse_835_text(content)
    segments = data.get("segments") if isinstance(data.get("segments"), list) else []
    lines_out: list[str] = []
    claim_summaries: list[dict[str, Any]] = []
    total_paid = 0.0
    total_charged = 0.0
    denial_count = 0
    for seg in segments:
        if not isinstance(seg, dict):
            continue
        cid = str(seg.get("claimId") or "—")
        charged = float(seg.get("charged") or 0)
        paid = float(seg.get("paid") or 0)
        total_charged += charged
        total_paid += paid
        cas = [str(c) for c in (seg.get("casCodes") or []) if c]
        rarc = [str(c) for c in (seg.get("rarcCodes") or []) if c]
        if seg.get("denialFlag") or cas:
            denial_count += 1
        svc_bits: list[str] = []
        for sl in seg.get("serviceLines") or []:
            if not isinstance(sl, dict):
                continue
            proc = str(sl.get("procedureCode") or "—")
            sl_paid = sl.get("paid")
            sl_chg = sl.get("charged")
            sl_cas = ",".join(str(c) for c in (sl.get("casCodes") or []) if c) or "none"
            sl_rarc = ",".join(str(c) for c in (sl.get("rarcCodes") or []) if c)
            bit = f"{proc} paid={sl_paid if sl_paid is not None else 'missing'} charged={sl_chg if sl_chg is not None else 'missing'} CAS={sl_cas}"
            if sl_rarc:
                bit += f" RARC={sl_rarc}"
            svc_bits.append(bit)
        row = (
            f"Claim {cid}: charged={charged if charged else 'missing'} paid={paid if paid else 'missing'}"
            f" CAS={','.join(cas) if cas else 'none'}"
            f" RARC={','.join(rarc) if rarc else 'none'}"
            f" denialFlag={bool(seg.get('denialFlag'))}"
        )
        if svc_bits:
            row += " | lines: " + "; ".join(svc_bits)
        lines_out.append(row)
        claim_summaries.append(
            {
                "claimId": cid,
                "charged": charged if charged else None,
                "paid": paid if paid else None,
                "casCodes": cas,
                "rarcCodes": rarc,
                "denialCode": seg.get("denialCode"),
                "denialFlag": bool(seg.get("denialFlag")),
                "serviceLineCount": len(seg.get("serviceLines") or []),
                "serviceLines": [
                    {
                        "procedureCode": sl.get("procedureCode"),
                        "charged": sl.get("charged"),
                        "paid": sl.get("paid"),
                        "casCodes": list(sl.get("casCodes") or []),
                        "rarcCodes": list(sl.get("rarcCodes") or []),
                        "denialCode": sl.get("denialCode"),
                    }
                    for sl in (seg.get("serviceLines") or [])
                    if isinstance(sl, dict)
                ],
            }
        )
    summary_text = (
        f"ERA 835 depth summary: claims={len(segments)} denials_or_adj={denial_count} "
        f"total_charged={total_charged if total_charged else 'missing'} "
        f"total_paid={total_paid if total_paid else 'missing'}. "
        "Amounts only when present on the file — empty ≠ $0.\n"
        + ("\n".join(lines_out) if lines_out else "(no CLP segments)")
    )
    return {
        "ok": True,
        "claimCount": len(segments),
        "denialOrAdjustmentCount": denial_count,
        "totalCharged": total_charged if total_charged else None,
        "totalPaid": total_paid if total_paid else None,
        "claims": claim_summaries,
        "summaryText": summary_text,
        "phiNote": "Patient names omitted from HAL remittance summary.",
    }


def _name_score(a: str, b: str) -> float:
    a_norm = re.sub(r"\s+", " ", str(a or "").lower()).strip()
    b_norm = re.sub(r"\s+", " ", str(b or "").lower()).strip()
    if not a_norm or not b_norm:
        return 0.0
    return SequenceMatcher(None, a_norm, b_norm).ratio()


def fuzzy_match_claims(
    segments: list[dict[str, Any]],
    claim_rows: list[dict[str, Any]],
    *,
    min_confidence: float = 0.55,
) -> list[dict[str, Any]]:
    """Match ERA segments to open claim rows with confidence scoring."""
    matches: list[dict[str, Any]] = []
    for seg in segments:
        seg_claim = str(seg.get("claimId") or "").strip()
        seg_patient = str(seg.get("patientName") or "")
        seg_paid = _parse_money(seg.get("paid"))
        best: dict[str, Any] | None = None
        best_score = 0.0
        for row in claim_rows:
            row_claim = str(row.get("Claim") or row.get("claim") or row.get("ClaimId") or row.get("id") or "")
            row_patient = str(row.get("Patient") or row.get("patient") or row.get("Name") or "")
            row_amt = _parse_money(row.get("Amount") or row.get("Balance") or row.get("Paid"))
            score = 0.0
            if seg_claim and row_claim and seg_claim.upper() == row_claim.upper():
                score = 0.98
            else:
                name_s = _name_score(seg_patient, row_patient)
                amt_s = 1.0 if seg_paid and row_amt and abs(seg_paid - row_amt) < 0.02 else 0.0
                if seg_paid and row_amt and abs(seg_paid - row_amt) / max(seg_paid, row_amt, 1) < 0.05:
                    amt_s = 0.85
                score = max(name_s * 0.6 + amt_s * 0.4, name_s, amt_s)
            if score > best_score:
                best_score = score
                best = {
                    "claimId": row_claim,
                    "patientName": row_patient,
                    "confidence": round(best_score, 3),
                    "paidAmount": seg_paid,
                    "segment": seg,
                }
        if best and best_score >= min_confidence:
            best["confidence"] = round(best_score, 3)
            matches.append(best)
        else:
            matches.append(
                {
                    "claimId": "",
                    "confidence": round(best_score, 3) if best else 0.0,
                    "paidAmount": seg_paid,
                    "segment": seg,
                    "status": "review",
                }
            )
    return matches
