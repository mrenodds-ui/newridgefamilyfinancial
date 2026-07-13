"""InsCo x ADA pay/write-off % with +/- variance from 5yr ledger pairing.

Pairs SoftDent production ADA codes with nearby transaction codes:
- ``2``  = insurance payment
- ``51``/``52`` = insurance write-off

Uses ``sd_patient_insurance`` primary carrier. Episode model: production charge(s)
then following pay/write-off rows on the same account until the next production
cluster or the forward window expires.

Reports (per InsCo x ADA):
- paid_pct mean/median and +/- 1 SD
- write_off_pct mean/median and +/- 1 SD
- sample size + tier (exact vs inferred)

Honesty: empty != $0; proportional multi-ADA splits are labeled inferred;
not SoftDent contractual line truth; no SoftDent write-back.
"""

from __future__ import annotations

import json
import sqlite3
import statistics
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from softdent_insco_ada_probabilistic import (
    GENERIC_PAYERS,
    INS_PAYMENT_CODES,
    INS_WRITEOFF_CODES,
    NON_PRODUCTION_CODES,
    _carrier_for_account,
    _load_primary_insurance_map,
    _table_exists,
    _utc_now,
)
from softdent_treatment_planning import normalize_ada_code, resolve_analytics_db, resolve_exports_dir

DEFAULT_YEARS = 5
FORWARD_DAYS = 60
MIN_PUBLISH_N = 10
HIGH_N = 30


def ensure_pct_variance_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS insco_ada_pct_variance (
            insurance_company TEXT NOT NULL,
            ada_code TEXT NOT NULL,
            tier TEXT NOT NULL,
            sample_size INTEGER NOT NULL DEFAULT 0,
            billed_avg REAL,
            paid_avg REAL,
            write_off_avg REAL,
            paid_pct_mean REAL,
            paid_pct_median REAL,
            paid_pct_stdev REAL,
            paid_pct_minus REAL,
            paid_pct_plus REAL,
            write_off_pct_mean REAL,
            write_off_pct_median REAL,
            write_off_pct_stdev REAL,
            write_off_pct_minus REAL,
            write_off_pct_plus REAL,
            credibility TEXT NOT NULL,
            period_start TEXT,
            period_end TEXT,
            forward_days INTEGER,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (insurance_company, ada_code, tier)
        );
        CREATE TABLE IF NOT EXISTS insco_ada_pct_variance_meta (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        """
    )


def _norm_ada(raw: str) -> str:
    text = str(raw or "").strip()
    if not text:
        return ""
    # SoftDent often stores 3-digit CDTs (220 -> D0220)
    if text.isdigit() and len(text) == 3:
        return f"D{int(text):04d}"
    return normalize_ada_code(text) or text


def _publishable_pct(paid_pct: float | None, wo_pct: float | None) -> bool:
    """Reject nonsense ratios when pay/WO is not tied to the charge (empty != invent)."""
    for val in (paid_pct, wo_pct):
        if val is None:
            continue
        if val < -5 or val > 120:
            return False
    return True


def _mean(vals: list[float]) -> float | None:
    return round(statistics.fmean(vals), 4) if vals else None


def _median(vals: list[float]) -> float | None:
    return round(float(statistics.median(vals)), 4) if vals else None


def _stdev(vals: list[float]) -> float | None:
    if len(vals) < 2:
        return 0.0 if vals else None
    return round(statistics.pstdev(vals), 4)


def _pct(part: float, whole: float) -> float | None:
    if whole <= 0:
        return None
    return round(100.0 * part / whole, 4)


def _credibility(tier: str, n: int) -> str:
    if tier == "exact":
        if n >= HIGH_N:
            return "high"
        if n >= MIN_PUBLISH_N:
            return "usable"
        return "insufficient"
    if tier == "inferred":
        if n >= HIGH_N:
            return "usable_inferred"
        if n >= MIN_PUBLISH_N:
            return "weak_inferred"
        return "insufficient"
    return "insufficient"


def _parse_day(raw: str) -> date | None:
    try:
        return date.fromisoformat(str(raw or "")[:10])
    except ValueError:
        return None


def build_insco_ada_pct_variance(
    conn: sqlite3.Connection,
    *,
    years: int = DEFAULT_YEARS,
    period_end: str | None = None,
    forward_days: int = FORWARD_DAYS,
) -> dict[str, Any]:
    """Rebuild InsCo x ADA pay%/write-off% with +/- stdev from 5yr episode pairing."""
    ensure_pct_variance_schema(conn)
    end = period_end or date.today().isoformat()
    end_d = date.fromisoformat(end[:10])
    start_d = end_d - timedelta(days=365 * max(1, int(years)))
    start = start_d.isoformat()
    fwd = max(1, int(forward_days))

    out: dict[str, Any] = {
        "ok": False,
        "periodStart": start,
        "periodEnd": end,
        "years": years,
        "forwardDays": fwd,
        "warnings": [],
        "episodeTiers": {},
        "publishedCells": 0,
        "totalCells": 0,
    }
    if not _table_exists(conn, "sd_account_transactions"):
        out["warnings"].append("sd_account_transactions missing")
        return out

    ins_map = _load_primary_insurance_map(conn)
    if not ins_map:
        out["warnings"].append("sd_patient_insurance empty")
        return out

    rows = conn.execute(
        """
        SELECT account_num, service_date, procedure, row_number,
               COALESCE(prod, 0) + COALESCE(charges, 0),
               COALESCE(prod_adj, 0) + COALESCE(pay_adj, 0),
               COALESCE(cash, 0) + COALESCE("check", 0) + COALESCE(credit, 0)
        FROM sd_account_transactions
        WHERE service_date >= ? AND service_date <= ?
        ORDER BY account_num, service_date, row_number
        """,
        (start, end),
    ).fetchall()

    by_acct: dict[str, list[tuple[str, str, int, float, float, float]]] = defaultdict(list)
    for account_num, service_date, procedure, row_number, billed, adj, paid in rows:
        by_acct[str(account_num or "").strip()].append(
            (
                str(service_date or "")[:10],
                str(procedure or "").strip(),
                int(row_number or 0),
                float(billed or 0),
                float(adj or 0),
                float(paid or 0),
            )
        )

    # samples[(carrier, ada, tier)] -> lists
    billed_s: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    paid_s: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    wo_s: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    pay_pct_s: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    wo_pct_s: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    tier_counts: dict[str, int] = defaultdict(int)
    carrier_hit = 0
    carrier_miss = 0
    episodes = 0

    for acct, txs in by_acct.items():
        carrier = _carrier_for_account(acct, ins_map)
        if not carrier or carrier.lower() in GENERIC_PAYERS:
            # still count miss only when money events exist
            if any(p in INS_PAYMENT_CODES or p in INS_WRITEOFF_CODES for _, p, _, _, _, _ in txs):
                carrier_miss += 1
            continue
        carrier_hit += 1

        i = 0
        n = len(txs)
        while i < n:
            d, proc, _rn, billed, _adj, _paid = txs[i]
            day = _parse_day(d)
            if day is None or proc in NON_PRODUCTION_CODES or billed <= 0:
                i += 1
                continue

            # Collect contiguous production cluster (same day or within 1 day)
            prods: list[tuple[str, float]] = []
            j = i
            cluster_end = day
            while j < n:
                d2, p2, _r2, b2, _a2, _pay2 = txs[j]
                day2 = _parse_day(d2)
                if day2 is None:
                    break
                if p2 in NON_PRODUCTION_CODES:
                    # stop cluster at first settlement row
                    if p2 in INS_PAYMENT_CODES or p2 in INS_WRITEOFF_CODES:
                        break
                    j += 1
                    continue
                if b2 <= 0:
                    j += 1
                    continue
                if (day2 - cluster_end).days > 1 and prods:
                    break
                if (day2 - day).days > 1 and not prods:
                    break
                ada = _norm_ada(p2)
                if ada:
                    prods.append((ada, b2))
                    cluster_end = day2
                j += 1

            if not prods:
                i += 1
                continue

            # Forward window: accumulate code 2 / 51 after cluster until next production or fwd days
            paid_amt = 0.0
            wo_amt = 0.0
            k = j
            window_end = cluster_end + timedelta(days=fwd)
            while k < n:
                d3, p3, _r3, b3, a3, pay3 = txs[k]
                day3 = _parse_day(d3)
                if day3 is None or day3 > window_end:
                    break
                if p3 not in NON_PRODUCTION_CODES and b3 > 0:
                    # next production episode starts
                    break
                if p3 in INS_PAYMENT_CODES and pay3:
                    paid_amt += float(pay3)
                if p3 in INS_WRITEOFF_CODES and a3:
                    wo_amt += abs(float(a3))
                k += 1

            if paid_amt <= 0 and wo_amt <= 0:
                i = j
                continue

            # Collapse duplicate ADAs in cluster
            by_ada: dict[str, float] = defaultdict(float)
            for ada, b in prods:
                by_ada[ada] += b
            ada_list = list(by_ada.items())
            total_b = sum(b for _, b in ada_list)
            if total_b <= 0:
                i = j
                continue

            # Skip episodes where settlement dwarfs billed (mis-paired lump payment)
            if total_b > 0 and (paid_amt + wo_amt) > total_b * 1.25:
                tier_counts["skipped_overpay"] = tier_counts.get("skipped_overpay", 0) + 1
                i = max(j, k if k > j else j)
                continue

            tier = "exact" if len(ada_list) == 1 else "inferred"
            tier_counts[tier] += 1
            episodes += 1

            for ada, b in ada_list:
                share = b / total_b
                alloc_paid = paid_amt * share
                alloc_wo = wo_amt * share
                key = (carrier, ada, tier)
                billed_s[key].append(b)
                if alloc_paid:
                    paid_s[key].append(alloc_paid)
                    pp = _pct(alloc_paid, b)
                    if pp is not None:
                        pay_pct_s[key].append(pp)
                if alloc_wo:
                    wo_s[key].append(alloc_wo)
                    wp = _pct(alloc_wo, b)
                    if wp is not None:
                        wo_pct_s[key].append(wp)

            i = max(j, k if k > j else j)

    updated_at = _utc_now()
    conn.execute("DELETE FROM insco_ada_pct_variance")
    keys = set(billed_s) | set(paid_s) | set(wo_s)
    published = 0
    total_cells = 0
    for carrier, ada, tier in sorted(keys):
        bills = billed_s.get((carrier, ada, tier), [])
        pays = paid_s.get((carrier, ada, tier), [])
        wos = wo_s.get((carrier, ada, tier), [])
        pps = pay_pct_s.get((carrier, ada, tier), [])
        wps = wo_pct_s.get((carrier, ada, tier), [])
        n = max(len(bills), len(pays), len(wos), len(pps), len(wps))
        if n <= 0:
            continue
        total_cells += 1
        pay_mean = _mean(pps)
        pay_sd = _stdev(pps) or 0.0
        wo_mean = _mean(wps)
        wo_sd = _stdev(wps) or 0.0
        pay_med = _median(pps)
        wo_med = _median(wps)
        cred = _credibility(tier, n)
        if not _publishable_pct(pay_med, wo_med):
            cred = "insufficient"
        if cred in {"high", "usable", "usable_inferred", "weak_inferred"}:
            published += 1
        conn.execute(
            """
            INSERT INTO insco_ada_pct_variance (
                insurance_company, ada_code, tier, sample_size,
                billed_avg, paid_avg, write_off_avg,
                paid_pct_mean, paid_pct_median, paid_pct_stdev, paid_pct_minus, paid_pct_plus,
                write_off_pct_mean, write_off_pct_median, write_off_pct_stdev,
                write_off_pct_minus, write_off_pct_plus,
                credibility, period_start, period_end, forward_days, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                carrier,
                ada,
                tier,
                n,
                _mean(bills),
                _mean(pays),
                _mean(wos),
                pay_mean,
                pay_med,
                pay_sd,
                None if pay_mean is None else round(pay_mean - pay_sd, 4),
                None if pay_mean is None else round(pay_mean + pay_sd, 4),
                wo_mean,
                wo_med,
                wo_sd,
                None if wo_mean is None else round(wo_mean - wo_sd, 4),
                None if wo_mean is None else round(wo_mean + wo_sd, 4),
                cred,
                start,
                end,
                fwd,
                updated_at,
            ),
        )

    meta = {
        "updated_at": updated_at,
        "period_start": start,
        "period_end": end,
        "years": str(years),
        "forward_days": str(fwd),
        "episodes": str(episodes),
        "episode_tiers": json.dumps(dict(tier_counts)),
        "carrier_accounts_hit": str(carrier_hit),
        "published_cells": str(published),
        "total_cells": str(total_cells),
        "min_publish_n": str(MIN_PUBLISH_N),
        "high_n": str(HIGH_N),
        "honesty": (
            "Code 2=Ins pay, 51=write-off paired after production ADAs within forward window. "
            "Multi-ADA episodes allocate 2/51 by billed share (inferred). "
            "+/- is 1 population stdev of percentages. empty != $0."
        ),
    }
    for key, value in meta.items():
        conn.execute(
            "INSERT OR REPLACE INTO insco_ada_pct_variance_meta (key, value) VALUES (?, ?)",
            (key, value),
        )
    conn.commit()
    out.update(
        {
            "ok": True,
            "episodeTiers": dict(tier_counts),
            "episodes": episodes,
            "publishedCells": published,
            "totalCells": total_cells,
            "carrierAccountsHit": carrier_hit,
        }
    )
    return out


def list_pct_variance_rows(
    *,
    db_path: Path | None = None,
    include_inferred: bool = True,
    min_n: int = MIN_PUBLISH_N,
    limit: int = 200,
) -> list[dict[str, Any]]:
    target = Path(db_path) if db_path else resolve_analytics_db()
    if not target or not target.is_file():
        return []
    conn = sqlite3.connect(f"file:{target}?mode=ro", uri=True)
    try:
        ensure_pct_variance_schema(conn)
        if include_inferred:
            where = "sample_size >= ? AND credibility != 'insufficient'"
        else:
            where = "sample_size >= ? AND tier = 'exact' AND credibility IN ('high','usable')"
        rows = conn.execute(
            f"""
            SELECT insurance_company, ada_code, tier, sample_size,
                   billed_avg, paid_avg, write_off_avg,
                   paid_pct_mean, paid_pct_median, paid_pct_stdev, paid_pct_minus, paid_pct_plus,
                   write_off_pct_mean, write_off_pct_median, write_off_pct_stdev,
                   write_off_pct_minus, write_off_pct_plus, credibility
            FROM insco_ada_pct_variance
            WHERE {where}
            ORDER BY
              CASE credibility WHEN 'high' THEN 0 WHEN 'usable' THEN 1
                   WHEN 'usable_inferred' THEN 2 ELSE 3 END,
              sample_size DESC
            LIMIT ?
            """,
            (max(1, int(min_n)), max(1, int(limit))),
        ).fetchall()
        out = []
        for r in rows:
            out.append(
                {
                    "insuranceCompany": r[0],
                    "adaCode": r[1],
                    "tier": r[2],
                    "sampleSize": r[3],
                    "billedAvg": r[4],
                    "paidAvg": r[5],
                    "writeOffAvg": r[6],
                    "paidPctMean": r[7],
                    "paidPctMedian": r[8],
                    "paidPctStdev": r[9],
                    "paidPctMinus": r[10],
                    "paidPctPlus": r[11],
                    "writeOffPctMean": r[12],
                    "writeOffPctMedian": r[13],
                    "writeOffPctStdev": r[14],
                    "writeOffPctMinus": r[15],
                    "writeOffPctPlus": r[16],
                    "credibility": r[17],
                }
            )
        return out
    finally:
        conn.close()


def lookup_pct_variance(
    *,
    payer: str,
    ada_code: str,
    include_inferred: bool = False,
    db_path: Path | None = None,
) -> dict[str, Any] | None:
    target = Path(db_path) if db_path else resolve_analytics_db()
    if not target or not target.is_file():
        return None
    carrier = str(payer or "").strip().upper()
    ada = _norm_ada(ada_code)
    if not carrier or not ada:
        return None
    rows = list_pct_variance_rows(
        db_path=target,
        include_inferred=include_inferred,
        min_n=1,
        limit=500,
    )
    hits = [
        r
        for r in rows
        if str(r.get("insuranceCompany") or "").upper() == carrier
        and str(r.get("adaCode") or "").upper() == ada.upper()
    ]
    if not hits and include_inferred:
        hits = [
            r
            for r in list_pct_variance_rows(
                db_path=target, include_inferred=True, min_n=1, limit=500
            )
            if str(r.get("insuranceCompany") or "").upper() == carrier
            and str(r.get("adaCode") or "").upper() == ada.upper()
        ]
    if not hits:
        return None
    # Prefer exact then high credibility
    hits.sort(
        key=lambda r: (
            0 if r.get("tier") == "exact" else 1,
            0 if r.get("credibility") == "high" else 1,
            -(int(r.get("sampleSize") or 0)),
        )
    )
    return hits[0]


def pct_variance_status(*, db_path: Path | None = None) -> dict[str, Any]:
    target = Path(db_path) if db_path else resolve_analytics_db()
    out: dict[str, Any] = {"ok": False, "dbPath": str(target) if target else None}
    if not target or not target.is_file():
        out["error"] = "analytics_db_missing"
        return out
    conn = sqlite3.connect(f"file:{target}?mode=ro", uri=True)
    try:
        ensure_pct_variance_schema(conn)
        meta = {
            str(k): str(v)
            for k, v in conn.execute("SELECT key, value FROM insco_ada_pct_variance_meta").fetchall()
        }
        exact_n = conn.execute(
            """
            SELECT COUNT(*) FROM insco_ada_pct_variance
            WHERE tier='exact' AND credibility IN ('high','usable') AND sample_size >= ?
            """,
            (MIN_PUBLISH_N,),
        ).fetchone()[0]
        all_n = conn.execute(
            """
            SELECT COUNT(*) FROM insco_ada_pct_variance
            WHERE credibility != 'insufficient' AND sample_size >= ?
            """,
            (MIN_PUBLISH_N,),
        ).fetchone()[0]
    finally:
        conn.close()
    out.update(
        {
            "ok": True,
            "def": "HAL-10584",
            "periodStart": meta.get("period_start"),
            "periodEnd": meta.get("period_end"),
            "years": meta.get("years"),
            "episodes": int(meta.get("episodes") or 0),
            "exactPublished": int(exact_n or 0),
            "allPublishedIncludingInferred": int(all_n or 0),
            "updatedAt": meta.get("updated_at"),
            "honesty": meta.get("honesty"),
        }
    )
    return out


def format_pct_variance_status_reply(st: dict[str, Any]) -> str:
    if not st.get("ok"):
        return f"InsCo×ADA % variance unavailable ({st.get('error') or 'unknown'})."
    return (
        f"InsCo×ADA pay/WO % (HAL-10584): {st.get('years')}yr "
        f"{st.get('periodStart')}..{st.get('periodEnd')}; "
        f"exact cells {st.get('exactPublished')}; "
        f"incl. inferred {st.get('allPublishedIncludingInferred')}; "
        f"episodes {st.get('episodes')}. "
        "Code 2=pay, 51=WO; +/- is 1 SD. empty≠$0."
    )


def format_pct_variance_reply(
    row: dict[str, Any] | None,
    *,
    payer: str = "",
    ada: str = "",
) -> str:
    if not row:
        return (
            f"No publishable pay/WO % for {payer or '?'} × {ada or '?'} "
            "(need n≥10 exact with sane ratios; empty≠$0)."
        )
    return (
        f"{row['insuranceCompany']} × {row['adaCode']} ({row['tier']}, {row['credibility']}, "
        f"n={row['sampleSize']}): "
        f"pay {row.get('paidPctMedian')}% +/-{row.get('paidPctStdev')} "
        f"(mean {row.get('paidPctMean')}% [{row.get('paidPctMinus')}..{row.get('paidPctPlus')}]); "
        f"write-off {row.get('writeOffPctMedian')}% +/-{row.get('writeOffPctStdev')} "
        f"(mean {row.get('writeOffPctMean')}% [{row.get('writeOffPctMinus')}..{row.get('writeOffPctPlus')}]). "
        "From SoftDent code 2/51 next to production ADAs over 5yr history."
    )


def export_pct_variance_report(
    *,
    db_path: Path | None = None,
    dest: Path | None = None,
) -> dict[str, Any]:
    target = Path(db_path) if db_path else resolve_analytics_db()
    out_dir = Path(dest) if dest else resolve_exports_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    result: dict[str, Any] = {"ok": False}
    if not target or not target.is_file():
        result["error"] = "analytics_db_missing"
        return result

    conn = sqlite3.connect(f"file:{target}?mode=ro", uri=True)
    try:
        ensure_pct_variance_schema(conn)
        meta = {
            str(k): str(v)
            for k, v in conn.execute("SELECT key, value FROM insco_ada_pct_variance_meta").fetchall()
        }
    finally:
        conn.close()

    exact_rows = list_pct_variance_rows(db_path=target, include_inferred=False, limit=500)
    all_rows = list_pct_variance_rows(db_path=target, include_inferred=True, limit=500)
    payload = {
        "ok": True,
        "def": "HAL-10584",
        "checkedAt": _utc_now(),
        "meta": meta,
        "method": {
            "historyYears": DEFAULT_YEARS,
            "softDentCodes": {"payment": "2", "writeOff": "51/52"},
            "pairing": (
                "Production ADA cluster, then forward codes 2 and 51 within "
                f"{FORWARD_DAYS} days (or until next production)."
            ),
            "percentages": "paid_pct = allocated_pay / billed * 100; write_off_pct = allocated_wo / billed * 100",
            "variance": "+/- 1 population stdev of per-episode percentages",
            "exact": "single ADA in production cluster",
            "inferred": "multi-ADA cluster: 2/51 allocated by billed share",
            "minN": MIN_PUBLISH_N,
        },
        "exactPublished": exact_rows,
        "exactCount": len(exact_rows),
        "allPublishedIncludingInferred": all_rows,
        "allCount": len(all_rows),
        "honesty": meta.get("honesty"),
    }
    stamp = date.today().isoformat()
    json_path = out_dir / f"insco_ada_pct_variance_report_{stamp}.json"
    md_path = out_dir / f"insco_ada_pct_variance_report_{stamp}.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        f"# InsCo x ADA Pay/Write-off % +/- Variance ({stamp})",
        "",
        f"History: **{meta.get('years', DEFAULT_YEARS)} years** "
        f"({meta.get('period_start')} .. {meta.get('period_end')}).",
        f"Episodes: {meta.get('episodes')} · exact published: **{len(exact_rows)}** · "
        f"incl. inferred: **{len(all_rows)}**.",
        "",
        "## Method",
        "",
        "- SoftDent code **2** = Ins payment; code **51** = write-off",
        "- Pair each production ADA with following 2/51 on same account (forward window)",
        "- Report pay% and write-off% of billed, with **+/- 1 SD**",
        "- Exact = one ADA in visit cluster; inferred = multi-ADA proportional split",
        "- empty != $0; not contractual guarantee",
        "",
        "## Top exact cells",
        "",
        "| Carrier | ADA | n | Pay% med | Pay% +/- | WO% med | WO% +/- | Cred |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in exact_rows[:50]:
        pay_pm = row.get("paidPctStdev")
        wo_pm = row.get("writeOffPctStdev")
        lines.append(
            f"| {row['insuranceCompany']} | {row['adaCode']} | {row['sampleSize']} | "
            f"{row.get('paidPctMedian')} | +/-{pay_pm} | "
            f"{row.get('writeOffPctMedian')} | +/-{wo_pm} | {row['credibility']} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    try:
        from import_loader import softdent_import_dir

        inbox = softdent_import_dir()
        inbox.mkdir(parents=True, exist_ok=True)
        stable = inbox / "softdent_insco_ada_pct_variance.json"
        stable.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        result["inboxPath"] = str(stable)
    except Exception as exc:  # noqa: BLE001
        result["inboxError"] = f"{type(exc).__name__}:{exc}"

    result.update(
        {
            "ok": True,
            "jsonPath": str(json_path),
            "mdPath": str(md_path),
            "exactCount": len(exact_rows),
            "allCount": len(all_rows),
        }
    )
    return result


def run_insco_ada_pct_variance_report(
    *,
    db_path: Path | None = None,
    years: int = DEFAULT_YEARS,
) -> dict[str, Any]:
    target = Path(db_path) if db_path else resolve_analytics_db()
    out: dict[str, Any] = {"ok": False, "dbPath": str(target) if target else None}
    if not target or not target.is_file():
        out["error"] = "analytics_db_missing"
        return out
    conn = sqlite3.connect(str(target))
    try:
        build = build_insco_ada_pct_variance(conn, years=years)
        out["build"] = build
    finally:
        conn.close()
    export = export_pct_variance_report(db_path=target)
    out["export"] = export
    out["ok"] = bool(build.get("ok")) and bool(export.get("ok"))
    return out


if __name__ == "__main__":
    print(json.dumps(run_insco_ada_pct_variance_report(), indent=2, default=str))
