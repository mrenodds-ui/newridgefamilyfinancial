"""Full InsCo × ADA catalog matrix (HAL-10586).

Surfaces **every** spine cell — including honest ``insufficient`` — so
"every code analyzed" is visible. Joins $ and %+/- tables from the unified
spine; also lists the 5yr ledger CDT universe.

Honesty: empty != $0; insufficient cells never become $0.00.
No SoftDent write-back. Gold path unchanged.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import date
from pathlib import Path
from typing import Any

from softdent_insco_ada_spine import (
    CREDIBILITY,
    DEFAULT_YEARS,
    normalize_cdt,
    _table_exists,
    _utc_now,
)
from softdent_treatment_planning import resolve_analytics_db, resolve_exports_dir

DEF_ID = "HAL-10586"


def catalog_matrix_status(*, db_path: Path | None = None) -> dict[str, Any]:
    target = Path(db_path) if db_path else resolve_analytics_db()
    out: dict[str, Any] = {"ok": False, "def": DEF_ID, "dbPath": str(target) if target else None}
    if not target or not target.is_file():
        out["error"] = "analytics_db_missing"
        return out
    conn = sqlite3.connect(f"file:{target}?mode=ro", uri=True)
    try:
        if not _table_exists(conn, "insco_ada_probabilistic_estimates"):
            out["error"] = "spine_tables_missing"
            return out
        total = int(
            conn.execute("SELECT COUNT(*) FROM insco_ada_probabilistic_estimates").fetchone()[0]
            or 0
        )
        exact_usable = int(
            conn.execute(
                """
                SELECT COUNT(*) FROM insco_ada_probabilistic_estimates
                WHERE tier='exact' AND credibility IN ('high','usable')
                """
            ).fetchone()[0]
            or 0
        )
        published = int(
            conn.execute(
                """
                SELECT COUNT(*) FROM insco_ada_probabilistic_estimates
                WHERE credibility != 'insufficient'
                """
            ).fetchone()[0]
            or 0
        )
        insufficient = int(
            conn.execute(
                """
                SELECT COUNT(*) FROM insco_ada_probabilistic_estimates
                WHERE credibility = 'insufficient'
                """
            ).fetchone()[0]
            or 0
        )
        distinct_ada = int(
            conn.execute(
                "SELECT COUNT(DISTINCT ada_code) FROM insco_ada_probabilistic_estimates"
            ).fetchone()[0]
            or 0
        )
        carriers = int(
            conn.execute(
                "SELECT COUNT(DISTINCT insurance_company) FROM insco_ada_probabilistic_estimates"
            ).fetchone()[0]
            or 0
        )
        meta = {}
        if _table_exists(conn, "insco_ada_probabilistic_meta"):
            meta = {
                str(k): str(v)
                for k, v in conn.execute(
                    "SELECT key, value FROM insco_ada_probabilistic_meta"
                ).fetchall()
            }
    finally:
        conn.close()

    universe = list_ledger_cdt_universe(db_path=target)
    out.update(
        {
            "ok": True,
            "totalCells": total,
            "publishedCells": published,
            "insufficientCells": insufficient,
            "exactUsableCells": exact_usable,
            "distinctAdaInSpine": distinct_ada,
            "carriers": carriers,
            "ledgerCdtUniverse": len(universe),
            "periodStart": meta.get("period_start"),
            "periodEnd": meta.get("period_end"),
            "spineEpisodes": int(meta.get("spine_episodes") or 0),
            "updatedAt": meta.get("updated_at"),
            "honesty": CREDIBILITY.get("honesty"),
        }
    )
    return out


def list_ledger_cdt_universe(*, db_path: Path | None = None) -> list[str]:
    target = Path(db_path) if db_path else resolve_analytics_db()
    if not target or not target.is_file():
        return []
    conn = sqlite3.connect(f"file:{target}?mode=ro", uri=True)
    try:
        if not _table_exists(conn, "sd_account_transactions"):
            return []
        rows = conn.execute(
            """
            SELECT DISTINCT procedure FROM sd_account_transactions
            WHERE service_date >= date('now', ?)
            """,
            (f"-{DEFAULT_YEARS * 365} days",),
        ).fetchall()
    finally:
        conn.close()
    out: set[str] = set()
    for (proc,) in rows:
        cdt = normalize_cdt(proc)
        if cdt:
            out.add(cdt)
    return sorted(out)


def list_catalog_matrix_rows(
    *,
    db_path: Path | None = None,
    include_insufficient: bool = True,
    include_inferred: bool = True,
    credibility: str | None = None,
    payer: str | None = None,
    ada: str | None = None,
    limit: int = 5000,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """All spine InsCo×ADA cells with $ + % (insufficient included by default)."""
    target = Path(db_path) if db_path else resolve_analytics_db()
    if not target or not target.is_file():
        return []
    conn = sqlite3.connect(f"file:{target}?mode=ro", uri=True)
    try:
        if not _table_exists(conn, "insco_ada_probabilistic_estimates"):
            return []
        has_pct = _table_exists(conn, "insco_ada_pct_variance")
        where = ["1=1"]
        params: list[Any] = []
        if not include_insufficient:
            where.append("d.credibility != 'insufficient'")
        if not include_inferred:
            where.append("d.tier = 'exact'")
        if credibility:
            where.append("d.credibility = ?")
            params.append(str(credibility).strip())
        if payer:
            where.append("lower(d.insurance_company) LIKE ?")
            params.append(f"%{str(payer).strip().lower()}%")
        if ada:
            cdt = normalize_cdt(ada) or str(ada).strip().upper()
            where.append("d.ada_code = ?")
            params.append(cdt)
        params.extend([max(1, int(limit)), max(0, int(offset))])

        if has_pct:
            sql = f"""
                SELECT
                  d.insurance_company, d.ada_code, d.tier, d.sample_size, d.credibility,
                  d.paid_median, d.paid_avg, d.write_off_median, d.write_off_avg, d.billed_avg,
                  d.period_start, d.period_end, d.updated_at,
                  p.paid_pct_median, p.paid_pct_stdev, p.paid_pct_minus, p.paid_pct_plus,
                  p.write_off_pct_median, p.write_off_pct_stdev,
                  p.write_off_pct_minus, p.write_off_pct_plus
                FROM insco_ada_probabilistic_estimates d
                LEFT JOIN insco_ada_pct_variance p
                  ON p.insurance_company = d.insurance_company
                 AND p.ada_code = d.ada_code
                 AND p.tier = d.tier
                WHERE {" AND ".join(where)}
                ORDER BY
                  CASE d.credibility
                    WHEN 'high' THEN 0 WHEN 'usable' THEN 1
                    WHEN 'usable_inferred' THEN 2 WHEN 'weak_inferred' THEN 3
                    ELSE 4 END,
                  d.sample_size DESC,
                  d.insurance_company, d.ada_code
                LIMIT ? OFFSET ?
            """
        else:
            sql = f"""
                SELECT
                  d.insurance_company, d.ada_code, d.tier, d.sample_size, d.credibility,
                  d.paid_median, d.paid_avg, d.write_off_median, d.write_off_avg, d.billed_avg,
                  d.period_start, d.period_end, d.updated_at,
                  NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
                FROM insco_ada_probabilistic_estimates d
                WHERE {" AND ".join(where)}
                ORDER BY d.sample_size DESC
                LIMIT ? OFFSET ?
            """
        rows = conn.execute(sql, params).fetchall()
    finally:
        conn.close()

    out: list[dict[str, Any]] = []
    for r in rows:
        cred = str(r[4] or "")
        paid = r[5] if r[5] is not None else r[6]
        wo = r[7] if r[7] is not None else r[8]
        # Honesty: insufficient → null dollars, never coerce to 0
        if cred == "insufficient":
            paid_out = None if paid is None else paid  # keep real samples if present
            # Still show amounts when n>0 but below publish floor — amounts are real history
            # Only invent-null when sample truly empty
            if int(r[3] or 0) <= 0:
                paid_out = None
                wo_out = None
            else:
                paid_out = paid
                wo_out = wo
        else:
            paid_out = paid
            wo_out = wo
        out.append(
            {
                "insuranceCompany": r[0],
                "adaCode": r[1],
                "tier": r[2],
                "sampleSize": r[3],
                "credibility": cred,
                "badge": _badge(cred, str(r[2] or "")),
                "paidMedian": paid_out,
                "writeOffMedian": wo_out,
                "billedAvg": r[9],
                "periodStart": r[10],
                "periodEnd": r[11],
                "updatedAt": r[12],
                "paidPctMedian": r[13],
                "paidPctStdev": r[14],
                "paidPctMinus": r[15],
                "paidPctPlus": r[16],
                "writeOffPctMedian": r[17],
                "writeOffPctStdev": r[18],
                "writeOffPctMinus": r[19],
                "writeOffPctPlus": r[20],
                "source": "ledger_episode_5yr",
                "emptyIsNotZero": True,
            }
        )
    return out


def _badge(cred: str, tier: str) -> dict[str, str]:
    if cred == "high":
        return {"badge": "high", "label": "High (n≥30 exact)", "tone": "ok"}
    if cred == "usable":
        return {"badge": "usable", "label": "Usable (n≥10 exact)", "tone": "warn"}
    if "inferred" in cred:
        return {"badge": "inferred", "label": f"Inferred ({tier})", "tone": "danger"}
    return {"badge": "insufficient", "label": "Insufficient (empty != $0)", "tone": "muted"}


def uncovered_ledger_cdts(*, db_path: Path | None = None) -> list[str]:
    """CDTs seen in 5yr ledger with zero spine cells (analyzed as production but no 2/51)."""
    target = Path(db_path) if db_path else resolve_analytics_db()
    universe = set(list_ledger_cdt_universe(db_path=target))
    if not universe or not target or not target.is_file():
        return []
    conn = sqlite3.connect(f"file:{target}?mode=ro", uri=True)
    try:
        if not _table_exists(conn, "insco_ada_probabilistic_estimates"):
            return sorted(universe)
        present = {
            str(r[0])
            for r in conn.execute(
                "SELECT DISTINCT ada_code FROM insco_ada_probabilistic_estimates"
            ).fetchall()
        }
    finally:
        conn.close()
    return sorted(universe - present)


def export_catalog_matrix_report(
    *,
    db_path: Path | None = None,
    dest: Path | None = None,
) -> dict[str, Any]:
    target = Path(db_path) if db_path else resolve_analytics_db()
    out_dir = Path(dest) if dest else resolve_exports_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    st = catalog_matrix_status(db_path=target)
    rows = list_catalog_matrix_rows(
        db_path=target, include_insufficient=True, include_inferred=True, limit=10000
    )
    universe = list_ledger_cdt_universe(db_path=target)
    uncovered = uncovered_ledger_cdts(db_path=target)
    payload = {
        "ok": bool(st.get("ok")),
        "def": DEF_ID,
        "checkedAt": _utc_now(),
        "status": st,
        "method": {
            "spine": "softdent_insco_ada_spine (HAL-10585)",
            "includesInsufficient": True,
            "emptyIsNotZero": True,
            "joins": "insco_ada_probabilistic_estimates LEFT JOIN insco_ada_pct_variance",
        },
        "cellCount": len(rows),
        "ledgerCdtUniverse": universe,
        "ledgerCdtUniverseCount": len(universe),
        "uncoveredLedgerCdts": uncovered,
        "uncoveredCount": len(uncovered),
        "cells": rows,
        "honesty": st.get("honesty"),
    }
    stamp = date.today().isoformat()
    json_path = out_dir / f"insco_ada_catalog_matrix_{stamp}.json"
    md_path = out_dir / f"insco_ada_catalog_matrix_{stamp}.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        f"# InsCo × ADA Full Catalog Matrix ({stamp})",
        "",
        f"**{DEF_ID}** · cells **{len(rows)}** · exact usable **{st.get('exactUsableCells')}** · "
        f"insufficient **{st.get('insufficientCells')}** · ledger CDT universe **{len(universe)}** · "
        f"uncovered (no 2/51 yet) **{len(uncovered)}**.",
        "",
        "Insufficient cells are listed honestly — empty != $0.",
        "",
        "## Top exact usable+",
        "",
        "| Carrier | ADA | n | Pay$ | WO$ | Pay% +/- | Cred |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    exact = [r for r in rows if r.get("tier") == "exact" and r.get("credibility") in {"high", "usable"}]
    for row in exact[:40]:
        pct = row.get("paidPctMedian")
        sd = row.get("paidPctStdev")
        pct_s = f"{pct} +/-{sd}" if pct is not None else "—"
        lines.append(
            f"| {row['insuranceCompany']} | {row['adaCode']} | {row['sampleSize']} | "
            f"{row.get('paidMedian')} | {row.get('writeOffMedian')} | {pct_s} | "
            f"{row['credibility']} |"
        )
    lines.extend(
        [
            "",
            "## Uncovered ledger CDTs (seen in TX, no spine settlement cell)",
            "",
            ", ".join(uncovered[:80]) + (" …" if len(uncovered) > 80 else ""),
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")

    result: dict[str, Any] = {
        "ok": True,
        "jsonPath": str(json_path),
        "mdPath": str(md_path),
        "cellCount": len(rows),
        "exactUsable": st.get("exactUsableCells"),
        "insufficient": st.get("insufficientCells"),
        "ledgerCdtUniverse": len(universe),
        "uncovered": len(uncovered),
    }
    try:
        from import_loader import softdent_import_dir

        inbox = softdent_import_dir()
        inbox.mkdir(parents=True, exist_ok=True)
        stable = inbox / "softdent_insco_ada_catalog_matrix.json"
        # Slim inbox copy (no full 2k+ cells blob) — status + samples
        slim = {
            "ok": True,
            "def": DEF_ID,
            "status": st,
            "exactSample": exact[:25],
            "insufficientSample": [r for r in rows if r.get("credibility") == "insufficient"][:15],
            "uncoveredLedgerCdts": uncovered[:60],
            "fullReport": str(json_path),
            "honesty": st.get("honesty"),
        }
        stable.write_text(json.dumps(slim, indent=2), encoding="utf-8")
        result["inboxPath"] = str(stable)
    except Exception as exc:  # noqa: BLE001
        result["inboxError"] = f"{type(exc).__name__}:{exc}"
    return result


def run_insco_ada_catalog_matrix_report(*, db_path: Path | None = None) -> dict[str, Any]:
    target = Path(db_path) if db_path else resolve_analytics_db()
    st = catalog_matrix_status(db_path=target)
    export = export_catalog_matrix_report(db_path=target)
    return {
        "ok": bool(st.get("ok")) and bool(export.get("ok")),
        "def": DEF_ID,
        "status": st,
        "export": export,
    }


def format_catalog_status_reply(st: dict[str, Any] | None = None) -> str:
    s = st if isinstance(st, dict) else catalog_matrix_status()
    if not s.get("ok"):
        return f"InsCo×ADA catalog unavailable ({s.get('error') or 'unknown'})."
    return (
        f"InsCo×ADA full catalog ({DEF_ID}): cells={s.get('totalCells')} "
        f"(exact usable={s.get('exactUsableCells')}, published={s.get('publishedCells')}, "
        f"insufficient={s.get('insufficientCells')}); "
        f"spine ADAs={s.get('distinctAdaInSpine')}; "
        f"ledger CDT universe={s.get('ledgerCdtUniverse')}; "
        f"episodes={s.get('spineEpisodes')}. "
        "Insufficient listed honestly — empty != $0."
    )


def insco_ada_catalog_widget() -> dict[str, Any]:
    st = catalog_matrix_status()
    exact = list_catalog_matrix_rows(
        include_insufficient=False, include_inferred=False, limit=8
    )
    insuff = list_catalog_matrix_rows(
        include_insufficient=True,
        include_inferred=True,
        credibility="insufficient",
        limit=5,
    )
    uncovered = uncovered_ledger_cdts()[:12]
    total = int(st.get("totalCells") or 0)
    if total <= 0:
        status = "empty"
        message = "Catalog empty — run InsCo×ADA spine rebuild / Sync."
    else:
        status = "ok"
        message = (
            f"Catalog · cells={total} · exact usable={st.get('exactUsableCells')} · "
            f"insufficient={st.get('insufficientCells')} · ledger CDTs={st.get('ledgerCdtUniverse')}"
        )
    return {
        "id": "softdent-insco-ada-catalog",
        "type": "status",
        "label": "InsCo × ADA Full Catalog (HAL-10586)",
        "size": "full",
        "status": status,
        "message": message,
        "hint": (
            "All spine cells including insufficient (empty != $0). "
            "Exact usable+ highlighted; uncovered ledger CDTs listed separately."
        ),
        "totalCells": total,
        "exactUsableCells": st.get("exactUsableCells"),
        "insufficientCells": st.get("insufficientCells"),
        "ledgerCdtUniverse": st.get("ledgerCdtUniverse"),
        "topExact": exact,
        "insufficientSample": [
            {
                "insuranceCompany": r["insuranceCompany"],
                "adaCode": r["adaCode"],
                "sampleSize": r["sampleSize"],
                "credibility": r["credibility"],
            }
            for r in insuff
        ],
        "uncoveredCdts": uncovered,
        "halChips": [
            {"label": "InsCo ADA catalog status", "query": "InsCo ADA catalog matrix status"},
            {
                "label": "Show insufficient cells",
                "query": "Show InsCo ADA catalog insufficient cells",
            },
            {
                "label": "Uncovered ledger CDTs?",
                "query": "Which ledger CDTs have no InsCo ADA spine settlement?",
            },
        ],
        "honesty": CREDIBILITY.get("honesty"),
        "def": DEF_ID,
    }


if __name__ == "__main__":
    print(json.dumps(run_insco_ada_catalog_matrix_report(), indent=2, default=str)[:4000])
