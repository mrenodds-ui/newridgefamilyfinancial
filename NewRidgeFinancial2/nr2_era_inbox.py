"""ERA-835 inbox scan/ingest (local — replaces removed apex_era835_pack).

Read-only: no SoftDent write-back. empty ≠ $0 — never invent remittance dollars.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GAP_ERA835_PENDING = "ERA835_PENDING"

_REPO = Path(__file__).resolve().parents[1]
_OFFICE = _REPO / "app_data" / "nr2" / "office"
_DEFAULT_MANIFEST = _OFFICE / "era_inbox" / "ingest_manifest.jsonl"
_DEFAULT_PROCESSED = _OFFICE / "era_inbox" / "processed"


def _manifest_path() -> Path:
    env_inbox = str(os.environ.get("NR2_ERA835_INBOX") or "").strip()
    if env_inbox:
        return Path(env_inbox).expanduser() / "ingest_manifest.jsonl"
    return _DEFAULT_MANIFEST


def _processed_dir() -> Path:
    env_inbox = str(os.environ.get("NR2_ERA835_INBOX") or "").strip()
    if env_inbox:
        return Path(env_inbox).expanduser() / "processed"
    return _DEFAULT_PROCESSED


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def era_inbox_roots() -> list[Path]:
    roots = [
        Path(r"C:\SoftDentFinancialExports\era"),
        Path(r"C:\SoftDentReportExports\era"),
        _OFFICE / "era_inbox" / "drop",
    ]
    env_inbox = str(os.environ.get("NR2_ERA835_INBOX") or "").strip()
    if env_inbox:
        roots.insert(0, Path(env_inbox).expanduser())
    out: list[Path] = []
    seen: set[str] = set()
    for p in roots:
        key = str(p).lower()
        if key not in seen:
            seen.add(key)
            out.append(p)
    return out


def ensure_era_inbox_dirs() -> list[str]:
    created: list[str] = []
    for root in era_inbox_roots():
        if not root.is_dir():
            root.mkdir(parents=True, exist_ok=True)
            created.append(str(root))
    manifest = _manifest_path()
    processed = _processed_dir()
    manifest.parent.mkdir(parents=True, exist_ok=True)
    processed.mkdir(parents=True, exist_ok=True)
    return created


def _is_era_placeholder(name: str) -> bool:
    """README / keep files are staged drops, not remittance — empty ≠ $0."""
    n = str(name or "").strip().lower()
    if not n:
        return True
    if n in (".gitkeep", "placeholder.txt", "readme", "readme.txt", "readme.md"):
        return True
    if n.startswith("readme"):
        return True
    return False


def _is_era_candidate_name(name: str) -> bool:
    n = str(name or "").strip().lower()
    if not n:
        return False
    if n.endswith(".835") or n.endswith(".edi"):
        return True
    if "era" in n:
        return True
    if n.endswith(".txt"):
        return True
    return False


def _list_era_files() -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    for root in era_inbox_roots():
        if not root.is_dir():
            continue
        for path in sorted(root.iterdir()):
            if not path.is_file():
                continue
            if not _is_era_candidate_name(path.name):
                continue
            try:
                st = path.stat()
            except OSError:
                continue
            placeholder = _is_era_placeholder(path.name)
            files.append(
                {
                    "name": path.name,
                    "path": str(path),
                    "root": str(root),
                    "sizeBytes": int(st.st_size),
                    "modifiedAt": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc)
                    .replace(microsecond=0)
                    .isoformat(),
                    "placeholder": placeholder,
                    "real835": not placeholder
                    and (
                        path.name.lower().endswith(".835")
                        or path.name.lower().endswith(".edi")
                        or ("era" in path.name.lower() and not placeholder)
                    ),
                }
            )
    return files


def scan_era_inbox(*, ensure_dirs: bool = False) -> dict[str, Any]:
    if ensure_dirs:
        ensure_era_inbox_dirs()
    roots = [str(p) for p in era_inbox_roots()]
    existing = [str(p) for p in era_inbox_roots() if p.is_dir()]
    files = _list_era_files()
    placeholders = [f for f in files if f.get("placeholder")]
    remits = [f for f in files if not f.get("placeholder")]
    empty = len(remits) == 0
    if empty and not placeholders:
        chip_status = "awaiting"
        chip_label = "Awaiting first 835 drop — Empty ≠ $0"
    elif empty and placeholders:
        chip_status = "staged"
        chip_label = (
            f"{len(placeholders)} file(s) in inbox — Empty ≠ $0 "
            "(placeholder only · no 835 remittance)"
        )
    else:
        chip_status = "staged"
        chip_label = f"{len(remits)} file(s) in inbox — Empty ≠ $0"
    return {
        "ok": True,
        "empty": empty,
        "honesty": "empty_not_zero",
        "chipStatus": chip_status,
        "chipLabel": chip_label,
        "fileCount": len(files),
        "realFileCount": len(remits),
        "placeholderCount": len(placeholders),
        "files": files[:50],
        "roots": roots,
        "existingRoots": existing,
        "candidateRoots": roots,
        "readOnly": True,
        "writeBack": False,
        "softDentWriteBack": False,
        "at": _utc_now(),
    }


def era_inbox_status(*, ensure_dirs: bool = False) -> dict[str, Any]:
    inbox = scan_era_inbox(ensure_dirs=ensure_dirs)
    gap = assess_era835_gap()
    return {
        "ok": True,
        "emptyNotZero": True,
        "inbox": inbox,
        "fileCount": inbox.get("fileCount") or 0,
        "realFileCount": inbox.get("realFileCount") or 0,
        "placeholderCount": inbox.get("placeholderCount") or 0,
        "empty": bool(inbox.get("empty")),
        "chipStatus": inbox.get("chipStatus"),
        "chipLabel": inbox.get("chipLabel"),
        "files": inbox.get("files") or [],
        "gap": gap,
        "honesty": "empty_not_zero",
        "readOnly": True,
        "writeBack": False,
        "softDentWriteBack": False,
        "at": _utc_now(),
    }


def _read_manifest_rows() -> list[dict[str, Any]]:
    manifest = _manifest_path()
    if not manifest.is_file():
        return []
    rows: list[dict[str, Any]] = []
    try:
        for line in manifest.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
                if isinstance(row, dict):
                    rows.append(row)
            except json.JSONDecodeError:
                continue
    except OSError:
        return []
    return rows


def assess_era835_gap() -> dict[str, Any]:
    inbox = scan_era_inbox(ensure_dirs=False)
    rows = _read_manifest_rows()
    file_count = int(inbox.get("fileCount") or 0)
    pending = file_count > 0 or not rows
    latest = rows[-1] if rows else {}
    gap_code = GAP_ERA835_PENDING if pending else None
    return {
        "ok": True,
        "gapCode": gap_code,
        "pending": pending,
        "rowCount": len(rows),
        "fileCount": file_count,
        "latest": latest if isinstance(latest, dict) else {},
        "fixHint": (
            "Drop payer 835/EDI files into era inbox; use Refresh Inbox ingest. "
            "Empty ≠ $0 — never invent remittance."
            if pending
            else None
        ),
        "emptyNotZero": True,
    }


def era835_enabled() -> bool:
    return True


def era835_status() -> dict[str, Any]:
    gap = assess_era835_gap()
    inbox = scan_era_inbox(ensure_dirs=False)
    return {
        "ok": True,
        "enabled": True,
        "gapCode": gap.get("gapCode"),
        "pending": gap.get("pending"),
        "fileCount": inbox.get("fileCount") or 0,
        "ingestedCount": gap.get("rowCount") or 0,
        "chipLabel": inbox.get("chipLabel"),
        "emptyNotZero": True,
    }


def discover_era_candidates(*, limit: int | None = None) -> dict[str, Any]:
    inbox = scan_era_inbox(ensure_dirs=True)
    candidates = inbox.get("files") or []
    if limit is not None:
        candidates = candidates[: max(0, int(limit))]
    return {
        "ok": True,
        "candidates": candidates,
        "candidateCount": len(candidates),
        "fileCount": inbox.get("fileCount") or 0,
        "chipLabel": inbox.get("chipLabel"),
        "scannedRoots": inbox.get("existingRoots") or [],
        "roots": inbox.get("existingRoots") or [],
        "emptyNotZero": True,
    }


def list_era835_payments(*, limit: int = 50) -> list[dict[str, Any]]:
    rows = _read_manifest_rows()
    cap = max(1, min(int(limit), 200))
    return rows[-cap:]


def ingest_era835_to_unified(
    *,
    content: str,
    filename: str | None = None,
) -> dict[str, Any]:
    text = str(content or "").strip()
    if not text:
        return {
            "ok": False,
            "error": "empty_content",
            "gap": GAP_ERA835_PENDING,
            "emptyNotZero": True,
        }
    from era835_parser import parse_835_text, summarize_835_for_hal

    parsed = parse_835_text(text)
    summary = summarize_835_for_hal(parsed)
    claim_count = int(summary.get("claimCount") or 0)
    entry = {
        "at": _utc_now(),
        "sourceFile": filename or "upload.835",
        "claimCount": claim_count,
        "totalPaid": summary.get("totalPaid"),
        "payerName": summary.get("payerName"),
        "writeBack": False,
        "softDentWriteBack": False,
        "emptyNotZero": True,
    }
    _manifest_path().parent.mkdir(parents=True, exist_ok=True)
    with _manifest_path().open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, default=str) + "\n")
    return {
        "ok": True,
        "rowsInserted": max(claim_count, 1),
        "summary": summary,
        "writeBack": False,
        "softDentWriteBack": False,
        "emptyNotZero": True,
        "at": _utc_now(),
    }


def era835_widget(bundle: dict[str, Any] | None = None) -> dict[str, Any]:
    inbox = scan_era_inbox(ensure_dirs=False)
    gap = assess_era835_gap()
    _ = bundle
    return {
        "id": "era835-inbox",
        "title": "ERA-835 inbox",
        "chipStatus": inbox.get("chipStatus"),
        "chipLabel": inbox.get("chipLabel"),
        "fileCount": inbox.get("fileCount") or 0,
        "gapCode": gap.get("gapCode"),
        "pending": gap.get("pending"),
        "emptyNotZero": True,
        "readOnly": True,
    }


def era_suggestions(*, limit: int = 50) -> dict[str, Any]:
    """Read-only ERA remittance suggestions for manual QuickBooks approval."""
    cap = max(1, min(int(limit), 200))
    rows = _read_manifest_rows()[-cap:]
    suggestions: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        suggestions.append(
            {
                "at": row.get("at"),
                "payerName": row.get("payerName"),
                "totalPaid": row.get("totalPaid"),
                "claimCount": row.get("claimCount"),
                "sourceFile": row.get("sourceFile"),
                "status": "suggest_qb_manual",
                "writeBack": False,
                "softDentWriteBack": False,
                "emptyNotZero": True,
            }
        )
    gap = assess_era835_gap()
    return {
        "ok": True,
        "suggestions": suggestions,
        "count": len(suggestions),
        "pending": bool(gap.get("pending")),
        "gapCode": gap.get("gapCode"),
        "readOnly": True,
        "writeBack": False,
        "softDentWriteBack": False,
        "note": "Operator approves in QuickBooks manually — no auto-post.",
        "emptyNotZero": True,
        "at": _utc_now(),
    }


def ingest_era_inbox(*, ensure_dirs: bool = False, limit: int | None = None) -> dict[str, Any]:
    if ensure_dirs:
        ensure_era_inbox_dirs()
    inbox = scan_era_inbox(ensure_dirs=False)
    files = inbox.get("files") or []
    if limit is not None:
        files = files[: max(0, int(limit))]
    if not files:
        return {
            "ok": True,
            "ingested": 0,
            "rowsInserted": 0,
            "empty": True,
            "chipStatus": "awaiting",
            "chipLabel": "Awaiting first 835 drop",
            "honesty": "empty_not_zero",
            "writeBack": False,
            "softDentWriteBack": False,
            "at": _utc_now(),
        }

    from era835_parser import parse_835_text, summarize_835_for_hal

    ingested = 0
    rows_inserted = 0
    errors: list[str] = []
    for meta in files:
        path = Path(str(meta.get("path") or ""))
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            errors.append(f"{path.name}:{exc}"[:120])
            continue
        parsed = parse_835_text(content)
        summary = summarize_835_for_hal(parsed)
        claim_count = int(summary.get("claimCount") or 0)
        entry = {
            "at": _utc_now(),
            "sourceFile": path.name,
            "sourcePath": str(path),
            "claimCount": claim_count,
            "totalPaid": summary.get("totalPaid"),
            "payerName": summary.get("payerName"),
            "writeBack": False,
            "softDentWriteBack": False,
            "emptyNotZero": True,
        }
        with _manifest_path().open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, default=str) + "\n")
        ingested += 1
        rows_inserted += max(claim_count, 1)
        try:
            dest = _processed_dir() / path.name
            _processed_dir().mkdir(parents=True, exist_ok=True)
            if not dest.exists():
                dest.write_bytes(path.read_bytes())
        except OSError:
            pass

    chip_label = "Awaiting first 835 drop" if ingested == 0 else f"Ingested {ingested} file(s)"
    return {
        "ok": ingested > 0 or not errors,
        "ingested": ingested,
        "rowsInserted": rows_inserted,
        "empty": ingested == 0,
        "chipStatus": "ready" if ingested else "awaiting",
        "chipLabel": chip_label,
        "errors": errors[:8] or None,
        "writeBack": False,
        "softDentWriteBack": False,
        "honesty": "empty_not_zero",
        "at": _utc_now(),
    }


def paid_claim_keys_from_era() -> dict[str, Any]:
    """Paid claim keys for Claims outstanding suppress (NR2-12150). empty ≠ $0."""
    from nr2_claims_paid_suppress import paid_claim_keys_from_era as _keys

    return _keys()
