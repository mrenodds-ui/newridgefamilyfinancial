#!/usr/bin/env python3
"""Feed SoftDent InsCo + office Insurance.xlsx into HAL payer reference + learned memories."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
NR2 = ROOT / "NewRidgeFinancial2"
sys.path.insert(0, str(NR2))

PAYER_PATH = NR2 / "data" / "payer_reference.json"
INSCO_MD = ROOT / "docs" / "hal_knowledge" / "NEW_RIDGE_SOFTDENT_INSURANCES.md"
OFFICE_JSON = ROOT / "docs" / "hal_knowledge" / "new_ridge_office_insurance_fee.json"
LEARNED_PATH = ROOT / "app_data" / "nr2" / "learned_memories.jsonl"
SENSEI_REF = Path(r"C:\ProgramData\Sensei Gateway Client\DataSync\0000950863\Reference")

STAMP = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
MAX_TEXT = 1900

MUST_NOT = [
    "guardrails",
    "runtime_status",
    "source_availability",
    "external_submission_policy",
]


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", str(text or "").lower()).strip("-")
    return (s[:56] or "payer").strip("-")


def load_insco_from_sensei() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not SENSEI_REF.is_dir():
        return rows
    for path in sorted(SENSEI_REF.glob("insco_*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
        except Exception:
            continue
        ins = data.get("INSURCO") if isinstance(data, dict) else None
        if not isinstance(ins, dict):
            continue
        name = str(ins.get("Name") or "").strip()
        if not name:
            continue
        inactive = str(ins.get("Inactive") or "").lower() in {"true", "1", "yes"}
        if inactive:
            continue
        ecs = str(ins.get("ECSPayorId") or "").strip()
        sid = str(ins.get("Id") or "").strip()
        rows.append(
            {
                "name": name,
                "softdentId": sid,
                "ecsPayorId": ecs if ecs and ecs not in {"00004", "—", "-"} else "",
                "phone": str(ins.get("Phone") or "").strip(),
            }
        )
    return rows


def load_office_contacts() -> list[dict[str, Any]]:
    if not OFFICE_JSON.is_file():
        return []
    data = json.loads(OFFICE_JSON.read_text(encoding="utf-8"))
    rows = data.get("insuranceContacts") or []
    return [r for r in rows if isinstance(r, dict)]


def make_payer_entry(
    *,
    name: str,
    aliases: list[str],
    payer_ids: list[str],
    notes: str,
    source_tag: str,
) -> dict[str, Any]:
    clean_ids = []
    seen = set()
    for pid in payer_ids:
        p = str(pid or "").strip()
        if not p or p in {"00004", "—", "-"}:
            continue
        key = p.upper()
        if key in seen:
            continue
        seen.add(key)
        clean_ids.append(p)
    clean_aliases = []
    for a in aliases:
        a = str(a or "").strip()
        if not a:
            continue
        if a.casefold() == name.casefold():
            continue
        if a.casefold() not in {x.casefold() for x in clean_aliases}:
            clean_aliases.append(a)
    return {
        "id": f"nr2-{slugify(name)}",
        "name": name,
        "aliases": clean_aliases[:12],
        "payerIds": clean_ids[:8],
        "type": "dental_ppo",
        "narrativeNotes": notes[:400],
        "commonDenialCodes": [],
        "eligibilityNotes": "Verify on ID card and clearinghouse; office contacts in Insurance.xlsx / SoftDent InsCo.",
        "source": source_tag,
    }


def merge_into_payer_reference(insco: list[dict], office: list[dict]) -> tuple[int, int]:
    data = json.loads(PAYER_PATH.read_text(encoding="utf-8"))
    existing = list(data.get("payers") or [])
    by_id = {str(p.get("id")): p for p in existing if isinstance(p, dict) and p.get("id")}
    # also index by upper name
    by_name = {str(p.get("name") or "").casefold(): p for p in existing if isinstance(p, dict)}

    added = 0
    updated = 0

    # SoftDent InsCo first
    for row in insco:
        name = row["name"]
        entry = make_payer_entry(
            name=name.title() if name.isupper() else name,
            aliases=[name, f"softdent {row.get('softdentId')}"],
            payer_ids=[row.get("ecsPayorId") or "", name],
            notes=(
                f"SoftDent InsCo id {row.get('softdentId')}. "
                f"ECS payer id {row.get('ecsPayorId') or 'n/a'}. "
                "New Ridge accepted/on-file carrier from Sensei DataSync."
            ),
            source_tag="softdent-insco-sensei",
        )
        # keep SoftDent ALL-CAPS as alias; display name nicer
        display = name
        entry["name"] = display
        key = display.casefold()
        if key in by_name:
            cur = by_name[key]
            # merge ids/aliases
            ids = list(cur.get("payerIds") or [])
            for pid in entry["payerIds"]:
                if pid not in ids:
                    ids.append(pid)
            aliases = list(cur.get("aliases") or [])
            for a in entry["aliases"]:
                if a.casefold() not in {x.casefold() for x in aliases}:
                    aliases.append(a)
            cur["payerIds"] = ids[:10]
            cur["aliases"] = aliases[:16]
            if not cur.get("narrativeNotes"):
                cur["narrativeNotes"] = entry["narrativeNotes"]
            cur["source"] = cur.get("source") or entry["source"]
            updated += 1
        elif entry["id"] in by_id:
            updated += 1
        else:
            existing.append(entry)
            by_id[entry["id"]] = entry
            by_name[key] = entry
            added += 1

    # Office workbook — richer contacts; merge onto SoftDent carrier name
    for row in office:
        carrier = str(row.get("carrierSoftDent") or "").strip()
        company = str(row.get("company") or "").strip()
        if not carrier and not company:
            continue
        name = carrier or company
        eid = str(row.get("vyneOrEclaimId") or "").strip()
        ephone = str(row.get("eligibilityPhone") or "").strip()
        cphone = str(row.get("claimPhone") or "").strip()
        notes = (
            f"Office Insurance.xlsx: {company or name}. "
            f"Eligibility {ephone or 'n/a'}; claim phone {cphone or 'n/a'}. "
            f"Vyne/e-claim {eid or 'n/a'}. SoftDent carrier label: {carrier or 'n/a'}."
        )
        aliases = [a for a in [company, carrier] if a]
        entry = make_payer_entry(
            name=name,
            aliases=aliases,
            payer_ids=[eid, carrier, company],
            notes=notes,
            source_tag="office-insurance-xlsx",
        )
        key = name.casefold()
        # also try company name match
        cur = by_name.get(key) or by_name.get(company.casefold())
        if cur:
            ids = list(cur.get("payerIds") or [])
            for pid in entry["payerIds"]:
                if pid and pid not in ids:
                    ids.append(pid)
            aliases2 = list(cur.get("aliases") or [])
            for a in entry["aliases"]:
                if a.casefold() not in {x.casefold() for x in aliases2}:
                    aliases2.append(a)
            cur["payerIds"] = ids[:10]
            cur["aliases"] = aliases2[:16]
            # prefer office contact notes when richer
            if ephone or cphone or eid:
                cur["narrativeNotes"] = notes[:400]
                cur["eligibilityNotes"] = (
                    f"Eligibility phone {ephone or 'see card'}; claim phone {cphone or 'see card'}."
                )
            updated += 1
        else:
            existing.append(entry)
            by_id[entry["id"]] = entry
            by_name[key] = entry
            added += 1

    data["payers"] = existing
    data["updatedAt"] = STAMP
    data["version"] = int(data.get("version") or 1) + 1
    data["sourceNote"] = (
        "Curated NR2 payer reference plus New Ridge SoftDent InsCo (Sensei) and office Insurance.xlsx contacts. "
        "Not member-specific benefits. Verify eligibility via 270/271 or clearinghouse; confirm payer ID on card."
    )
    PAYER_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    # clear cache if loaded
    try:
        from payer_reference_store import load_payer_reference

        load_payer_reference.cache_clear()
    except Exception:
        pass
    return added, updated


def chunk_lines(lines: list[str], *, prefix: str, max_chars: int = MAX_TEXT) -> list[str]:
    chunks: list[str] = []
    buf = prefix
    for line in lines:
        piece = line if line.endswith("\n") else line + "\n"
        if len(buf) + len(piece) > max_chars and buf != prefix:
            chunks.append(buf.strip())
            buf = prefix
        buf += piece
    if buf.strip() and buf.strip() != prefix.strip():
        chunks.append(buf.strip())
    return chunks


def build_memory_rows(insco: list[dict], office: list[dict]) -> list[dict]:
    rows: list[dict] = []

    def mem(mid: str, text: str, notes: str = "") -> dict:
        return {
            "id": mid,
            "category": "insurance_narratives",
            "text": text[:MAX_TEXT],
            "source": "SoftDent InsCo Sensei + Insurance.xlsx feed",
            "created_at": STAMP,
            "last_verified_at": STAMP,
            "confidence": "high",
            "scope": "insurance_narratives",
            "staleness_rule": "verify_monthly",
            "sensitivity_level": "internal_safe",
            "status": "approved",
            "must_not_override": MUST_NOT,
            "notes": notes,
        }

    # Overview
    rows.append(
        mem(
            "nr2-dental-insurance-master-overview",
            "New Ridge dental insurance master for HAL: SoftDent InsCo from Sensei DataSync "
            f"({len(insco)} active companies) plus office Insurance.xlsx contacts ({len(office)} rows). "
            "Use SoftDent carrier names for claim routing; use workbook phones/websites for eligibility and claim follow-up. "
            "Not member benefits — always verify on card / 270-271. Fee schedules are in the Fee Schedule Spreadsheet index.",
        )
    )

    # SoftDent full list in chunks
    insco_names = [r["name"] for r in sorted(insco, key=lambda x: x["name"].casefold())]
    name_lines = [f"- {n}" for n in insco_names]
    chunks: list[str] = []
    buf_lines: list[str] = []
    header_len = len("New Ridge SoftDent InsCo active dental carriers (Sensei). Part 99/99. Names:\n")
    for line in name_lines:
        trial = "\n".join(buf_lines + [line])
        if header_len + len(trial) > MAX_TEXT and buf_lines:
            chunks.append("\n".join(buf_lines))
            buf_lines = [line]
        else:
            buf_lines.append(line)
    if buf_lines:
        chunks.append("\n".join(buf_lines))
    total = max(1, len(chunks))
    for i, body in enumerate(chunks, start=1):
        rows.append(
            mem(
                f"nr2-softdent-insco-list-{i:02d}",
                f"New Ridge SoftDent InsCo active dental carriers (Sensei). Part {i}/{total}. Names:\n{body}",
                notes=f"InsCo list chunk {i}/{total}",
            )
        )

    # SoftDent with ECS ids (compact)
    ecs_lines = [
        f"- {r['name']} (SoftDent {r['softdentId']}; ECS {r['ecsPayorId'] or 'n/a'})"
        for r in sorted(insco, key=lambda x: x["name"].casefold())
    ]
    ecs_chunks: list[str] = []
    buf_lines = []
    header = "New Ridge SoftDent InsCo with ECS payer IDs. Part {i}/{t}:\n"
    for line in ecs_lines:
        trial = "\n".join(buf_lines + [line])
        if len(header.format(i=99, t=99)) + len(trial) > MAX_TEXT and buf_lines:
            ecs_chunks.append("\n".join(buf_lines))
            buf_lines = [line]
        else:
            buf_lines.append(line)
    if buf_lines:
        ecs_chunks.append("\n".join(buf_lines))
    for i, body in enumerate(ecs_chunks, start=1):
        rows.append(
            mem(
                f"nr2-softdent-insco-ecs-{i:02d}",
                f"New Ridge SoftDent InsCo with ECS payer IDs. Part {i}/{len(ecs_chunks)}:\n{body}",
            )
        )

    # Office contacts — one memory per carrier (compact)
    for row in office:
        company = str(row.get("company") or "").strip()
        carrier = str(row.get("carrierSoftDent") or "").strip()
        if not company and not carrier:
            continue
        mid = f"nr2-ins-contact-{slugify(carrier or company)}"
        eid = str(row.get("vyneOrEclaimId") or "").strip() or "n/a"
        ephone = str(row.get("eligibilityPhone") or "").strip() or "n/a"
        cphone = str(row.get("claimPhone") or "").strip() or "n/a"
        addr = str(row.get("claimMailingAddress") or "").strip()
        best = str(row.get("verificationBestSource") or "").strip()
        text = (
            f"New Ridge insurance contact — {company or carrier}. SoftDent carrier: {carrier or 'n/a'}. "
            f"Vyne/e-claim ID: {eid}. Eligibility phone: {ephone}. Claim phone: {cphone}."
        )
        if addr:
            text += f" Claim mail: {addr}."
        if best:
            text += f" Best verification: {best}."
        text += " Not member benefits; verify card/clearinghouse before submit."
        rows.append(mem(mid, text, notes="per-carrier office contact"))

    # Kansas / high-volume highlight
    rows.append(
        mem(
            "nr2-dental-insurance-kansas-priority",
            "New Ridge Kansas-priority dental carriers from SoftDent/office lists: DELTA DENTAL OF KS (ECS/Vyne often CDKS1 or "
            "72004 — confirm on card), BCBS OF KS, BCBS OF KANSAS CITY, CIGNA DENTAL, METLIFE DENTAL, GUARDIAN LIFE, "
            "PRINCIPAL LIFE, AETNA, HUMANA DENTAL, UNITED HEALTHCARE / UNITED CONCORDIA, CENTENE ENVOLVE KS / DentaQuest "
            "government lines, AMERITAS, GEHA, CAREINGTON. Use Insurance.xlsx for phones and Fee Schedule Spreadsheet for "
            "allowed amounts by schedule name.",
        )
    )
    return rows


def upsert_learned(rows: list[dict]) -> tuple[int, int]:
    prefix_ids = {
        "nr2-dental-insurance-master-overview",
        "nr2-dental-insurance-kansas-priority",
    }
    replace_prefixes = (
        "nr2-softdent-insco-list-",
        "nr2-softdent-insco-ecs-",
        "nr2-ins-contact-",
    )
    kept: list[str] = []
    if LEARNED_PATH.is_file():
        for line in LEARNED_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                kept.append(line)
                continue
            mid = str(obj.get("id") or "")
            if mid in prefix_ids or mid.startswith(replace_prefixes):
                continue
            kept.append(line)

    LEARNED_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LEARNED_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        for line in kept:
            handle.write(line + "\n")
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return len(rows), len(kept)


def main() -> int:
    insco = load_insco_from_sensei()
    office = load_office_contacts()
    if not insco and INSCO_MD.is_file():
        print("Sensei InsCo unavailable; continuing with office workbook only")
    print(f"SoftDent InsCo: {len(insco)}")
    print(f"Office contacts: {len(office)}")

    added, updated = merge_into_payer_reference(insco, office)
    print(f"payer_reference.json: +{added} added, ~{updated} merged/updated")

    mem_rows = build_memory_rows(insco, office)
    written, kept = upsert_learned(mem_rows)
    print(f"learned_memories: wrote {written} insurance memories (kept {kept} other lines)")

    from knowledge_memory_store import load_approved_memories, write_browser_memo_index_js

    target = write_browser_memo_index_js()
    total = len(load_approved_memories())
    payers = json.loads(PAYER_PATH.read_text(encoding="utf-8")).get("payers") or []
    print(f"payer_reference count: {len(payers)}")
    print(f"indexable memories: {total}")
    print(f"browser index: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
