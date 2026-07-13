"""Probabilistic InsCo × ADA paid/write-off estimates from ledger + coverage.

Uses ``sd_account_transactions`` (SoftDent codes ``2``=ins pay, ``51``/``52``=write-off)
plus ``sd_patient_insurance`` primary carrier. Does **not** invent SoftDent write-back
or Ins Plan Register dollars.

Confidence tiers (honest):
- ``exact`` — only one production ADA in lookback → no allocation guess
- ``inferred`` — 2–3 ADAs, dollars split proportional to billed (labeled inferred)
- ``low`` — 4+ ADAs in lookback (high ambiguity; stored but not published as credible)
- ``insufficient`` — below sample floors (not published)

Payment-analysis CSV lines (hal-10400) remain the gold path when available.
"""

from __future__ import annotations

import json
import os
import sqlite3
import statistics
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from softdent_treatment_planning import normalize_ada_code, resolve_analytics_db, resolve_exports_dir

# SoftDent transactional codes
INS_PAYMENT_CODES = frozenset({"2"})
INS_WRITEOFF_CODES = frozenset({"51", "52"})
NON_PRODUCTION_CODES = frozenset(
    {
        "2",
        "3",
        "11",
        "12",
        "17",
        "48",
        "51",
        "52",
        "60",
        "61",
        "99",
        "8888",
    }
)

# Credibility floors — how much data pushes report trustworthiness
CREDIBILITY = {
    # Minimum exact events to publish a cell as "usable estimate"
    "exact_publish_n": 10,
    # Preferred exact N for "high credibility" badge
    "exact_high_n": 30,
    # Inferred (2–3 ADA) publish floor — higher because allocation invents splits
    "inferred_publish_n": 30,
    # Preferred inferred N
    "inferred_high_n": 75,
    # Low-confidence (4+ ADA) never published as credible; kept for diagnostics only
    "low_never_publish": True,
    # Lookback: production charges within this many days before pay/write-off
    "lookback_days": 45,
    # Recommended history window for a practice-wide matrix
    "recommended_history_months": 24,
    # Rough events needed for a useful top-carrier × hygiene-code matrix
    "target_exact_cells_n10": 50,
    "target_exact_cells_n30": 20,
    "honesty": (
        "Ledger 51/2 rows have no ADA — exact cells require single-ADA lookback. "
        "Inferred cells allocate proportionally (invented splits). "
        "Gold path remains SoftDent payment-line / ERA ingest when available. "
        "empty != $0."
    ),
}

GENERIC_PAYERS = frozenset({"", "insurance", "ins", "payer", "carrier", "unknown", "n/a", "-"})


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_probabilistic_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS insco_ada_probabilistic_estimates (
            insurance_company TEXT NOT NULL,
            ada_code TEXT NOT NULL,
            tier TEXT NOT NULL,
            sample_size INTEGER NOT NULL DEFAULT 0,
            paid_avg REAL,
            paid_median REAL,
            write_off_avg REAL,
            write_off_median REAL,
            billed_avg REAL,
            credibility TEXT NOT NULL,
            period_start TEXT,
            period_end TEXT,
            lookback_days INTEGER,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (insurance_company, ada_code, tier)
        );
        CREATE INDEX IF NOT EXISTS idx_insco_ada_prob_cred
            ON insco_ada_probabilistic_estimates(credibility, sample_size);
        CREATE TABLE IF NOT EXISTS insco_ada_probabilistic_meta (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        """
    )


def _load_primary_insurance_map(conn: sqlite3.Connection) -> dict[str, str]:
    out: dict[str, str] = {}
    if not _table_exists(conn, "sd_patient_insurance"):
        return out
    rows = conn.execute(
        """
        SELECT patient_id, insurance_name, priority
        FROM sd_patient_insurance
        WHERE insurance_name IS NOT NULL AND TRIM(insurance_name) != ''
        ORDER BY priority ASC
        """
    ).fetchall()
    for patient_id, name, _priority in rows:
        pid = str(patient_id or "").strip()
        carrier = str(name or "").strip()
        if not pid or not carrier:
            continue
        if carrier.lower() in GENERIC_PAYERS:
            continue
        if pid not in out:
            out[pid] = carrier
    return out


def _carrier_for_account(account_num: str, ins_map: dict[str, str]) -> str | None:
    acct = str(account_num or "").strip()
    if not acct:
        return None
    if acct in ins_map:
        return ins_map[acct]
    if len(acct) > 1:
        family = acct[:-1] + "0"
        if family in ins_map:
            return ins_map[family]
        if acct[:-1] in ins_map:
            return ins_map[acct[:-1]]
    return None


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
        (name,),
    ).fetchone()
    return bool(row)


def _event_tier(ada_count: int) -> str:
    if ada_count <= 0:
        return "none"
    if ada_count == 1:
        return "exact"
    if ada_count <= 3:
        return "inferred"
    return "low"


def _credibility_label(tier: str, n: int) -> str:
    if tier == "exact":
        if n >= int(CREDIBILITY["exact_high_n"]):
            return "high"
        if n >= int(CREDIBILITY["exact_publish_n"]):
            return "usable"
        return "insufficient"
    if tier == "inferred":
        if n >= int(CREDIBILITY["inferred_high_n"]):
            return "usable_inferred"
        if n >= int(CREDIBILITY["inferred_publish_n"]):
            return "weak_inferred"
        return "insufficient"
    return "insufficient"


def _mean(vals: list[float]) -> float | None:
    return round(statistics.fmean(vals), 2) if vals else None


def _median(vals: list[float]) -> float | None:
    return round(float(statistics.median(vals)), 2) if vals else None


def build_insco_ada_probabilistic_estimates(
    conn: sqlite3.Connection,
    *,
    period_start: str | None = None,
    period_end: str | None = None,
    lookback_days: int | None = None,
) -> dict[str, Any]:
    """Rebuild InsCo×ADA probabilistic table from ledger + coverage."""
    ensure_probabilistic_schema(conn)
    lookback = int(lookback_days if lookback_days is not None else CREDIBILITY["lookback_days"])
    end = period_end or date.today().isoformat()
    if period_start:
        start = period_start
    else:
        months = int(CREDIBILITY["recommended_history_months"])
        end_d = date.fromisoformat(end[:10])
        # approx months
        start_d = end_d - timedelta(days=30 * months)
        start = start_d.isoformat()

    result: dict[str, Any] = {
        "ok": False,
        "periodStart": start,
        "periodEnd": end,
        "lookbackDays": lookback,
        "credibilityRules": dict(CREDIBILITY),
        "eventTiers": {},
        "publishedCells": 0,
        "totalCells": 0,
        "warnings": [],
    }
    if not _table_exists(conn, "sd_account_transactions"):
        result["warnings"].append("sd_account_transactions missing")
        return result

    ins_map = _load_primary_insurance_map(conn)
    if not ins_map:
        result["warnings"].append("sd_patient_insurance empty — run Sensei/ODBC insurance populate first")
        return result

    rows = conn.execute(
        """
        SELECT account_num, service_date, procedure,
               COALESCE(prod, 0) + COALESCE(charges, 0),
               COALESCE(prod_adj, 0) + COALESCE(pay_adj, 0),
               COALESCE(cash, 0) + COALESCE("check", 0) + COALESCE(credit, 0)
        FROM sd_account_transactions
        WHERE service_date >= ? AND service_date <= ?
        ORDER BY account_num, service_date, row_number
        """,
        (start, end),
    ).fetchall()

    by_acct: dict[str, list[tuple[str, str, float, float, float]]] = defaultdict(list)
    for account_num, service_date, procedure, billed, adj, paid in rows:
        by_acct[str(account_num or "").strip()].append(
            (
                str(service_date or "")[:10],
                str(procedure or "").strip(),
                float(billed or 0),
                float(adj or 0),
                float(paid or 0),
            )
        )

    # (carrier, ada, tier) -> lists
    paid_samples: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    wo_samples: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    billed_samples: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    tier_counts: dict[str, int] = defaultdict(int)
    carrier_miss = 0
    carrier_hit = 0

    for acct, txs in by_acct.items():
        carrier = _carrier_for_account(acct, ins_map)
        for svc_date, proc, _billed, adj, paid in txs:
            if proc not in INS_PAYMENT_CODES and proc not in INS_WRITEOFF_CODES:
                continue
            if not carrier:
                carrier_miss += 1
                continue
            carrier_hit += 1
            try:
                event_day = date.fromisoformat(svc_date)
            except ValueError:
                continue
            window_start = event_day - timedelta(days=lookback)
            look: list[tuple[str, float]] = []
            for d2, p2, b2, _a2, _pay2 in txs:
                if p2 in NON_PRODUCTION_CODES or b2 <= 0:
                    continue
                try:
                    charge_day = date.fromisoformat(d2)
                except ValueError:
                    continue
                if window_start <= charge_day <= event_day:
                    ada = normalize_ada_code(p2) or p2
                    if ada:
                        look.append((ada, b2))
            # collapse duplicate ADA in window (sum billed)
            by_ada: dict[str, float] = defaultdict(float)
            for ada, b2 in look:
                by_ada[ada] += b2
            look_list = list(by_ada.items())
            tier = _event_tier(len(look_list))
            tier_counts[tier] += 1
            if tier in {"none"} or not look_list:
                continue
            total_b = sum(b for _, b in look_list)
            if total_b <= 0:
                continue
            wo_amt = abs(adj) if proc in INS_WRITEOFF_CODES else 0.0
            pay_amt = paid if proc in INS_PAYMENT_CODES else 0.0
            for ada, b2 in look_list:
                share = b2 / total_b
                key = (carrier, ada, tier)
                if pay_amt:
                    paid_samples[key].append(pay_amt * share)
                if wo_amt:
                    wo_samples[key].append(wo_amt * share)
                billed_samples[key].append(b2 * share)

    updated_at = _utc_now()
    conn.execute("DELETE FROM insco_ada_probabilistic_estimates")
    published = 0
    total_cells = 0
    keys = set(paid_samples) | set(wo_samples) | set(billed_samples)
    for carrier, ada, tier in sorted(keys):
        pays = paid_samples.get((carrier, ada, tier), [])
        wos = wo_samples.get((carrier, ada, tier), [])
        bills = billed_samples.get((carrier, ada, tier), [])
        n = max(len(pays), len(wos), len(bills))
        if n <= 0:
            continue
        total_cells += 1
        cred = _credibility_label(tier, n)
        # Never publish low-tier as credible rows in the published sense —
        # still store for diagnostics with credibility=insufficient
        if tier == "low":
            cred = "insufficient"
        if cred != "insufficient":
            published += 1
        conn.execute(
            """
            INSERT INTO insco_ada_probabilistic_estimates (
                insurance_company, ada_code, tier, sample_size,
                paid_avg, paid_median, write_off_avg, write_off_median, billed_avg,
                credibility, period_start, period_end, lookback_days, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                carrier,
                ada,
                tier,
                n,
                _mean(pays),
                _median(pays),
                _mean(wos),
                _median(wos),
                _mean(bills),
                cred,
                start,
                end,
                lookback,
                updated_at,
            ),
        )

    meta = {
        "updated_at": updated_at,
        "period_start": start,
        "period_end": end,
        "lookback_days": str(lookback),
        "carrier_hit_events": str(carrier_hit),
        "carrier_miss_events": str(carrier_miss),
        "insurance_map_size": str(len(ins_map)),
        "published_cells": str(published),
        "total_cells": str(total_cells),
        "event_tiers": json.dumps(dict(tier_counts)),
        "credibility_rules": json.dumps(CREDIBILITY),
    }
    for key, value in meta.items():
        conn.execute(
            "INSERT OR REPLACE INTO insco_ada_probabilistic_meta (key, value) VALUES (?, ?)",
            (key, value),
        )
    conn.commit()

    result.update(
        {
            "ok": True,
            "eventTiers": dict(tier_counts),
            "publishedCells": published,
            "totalCells": total_cells,
            "carrierHitEvents": carrier_hit,
            "carrierMissEvents": carrier_miss,
            "insuranceMapSize": len(ins_map),
        }
    )
    return result


def lookup_probabilistic_estimate(
    *,
    payer: str,
    ada_code: str,
    db_path: Path | None = None,
    prefer_exact: bool = True,
    include_inferred: bool = False,
) -> dict[str, Any] | None:
    """Lookup InsCo×ADA estimate. Default: exact tier only (usable/high).

    Inferred cells return None unless ``include_inferred=True`` (staff opt-in).
    Insufficient / low never returned as dollars (empty != $0).
    """
    target = Path(db_path) if db_path else resolve_analytics_db()
    if not target or not target.is_file():
        return None
    payer_l = str(payer or "").strip().lower()
    ada = normalize_ada_code(ada_code) or str(ada_code or "").strip().upper()
    if not payer_l or not ada:
        return None
    conn = sqlite3.connect(f"file:{target}?mode=ro", uri=True)
    try:
        ensure_probabilistic_schema(conn)
        tiers: tuple[str, ...]
        if include_inferred:
            tiers = ("exact", "inferred") if prefer_exact else ("inferred", "exact")
        else:
            tiers = ("exact",)
        for tier in tiers:
            row = conn.execute(
                """
                SELECT insurance_company, ada_code, tier, sample_size,
                       paid_avg, paid_median, write_off_avg, write_off_median,
                       billed_avg, credibility, period_start, period_end
                FROM insco_ada_probabilistic_estimates
                WHERE lower(insurance_company) LIKE ?
                  AND ada_code = ?
                  AND tier = ?
                  AND credibility != 'insufficient'
                ORDER BY sample_size DESC
                LIMIT 1
                """,
                (f"%{payer_l}%", ada, tier),
            ).fetchone()
            if row:
                keys = (
                    "insurance_company",
                    "ada_code",
                    "tier",
                    "sample_size",
                    "paid_avg",
                    "paid_median",
                    "write_off_avg",
                    "write_off_median",
                    "billed_avg",
                    "credibility",
                    "period_start",
                    "period_end",
                )
                return dict(zip(keys, row))
    finally:
        conn.close()
    return None


def parse_probabilistic_estimate_query(query: str) -> dict[str, Any] | None:
    """Parse staff queries like 'How much does Delta pay for D1110?' / inferred opt-in."""
    import re

    q = str(query or "").strip()
    if not q:
        return None
    ql = q.lower()
    include_inferred = bool(
        re.search(
            r"\b(include\s+inferred|show\s+(uncertain|inferred)|inferred\s+ok|"
            r"uncertain\s+estimates?\s+ok)\b",
            ql,
        )
    )
    # Status / report health
    if re.search(
        r"\b("
        r"insco\s*[×x]?\s*ada\s+(status|report|estimates?|data)|"
        r"probabilistic\s+(insco|ada|estimate|report|status)|"
        r"ledger\s+based\s+(insco|ada|estimate)|"
        r"credibility\s+(badge|report|status)|"
        r"insco\s+ada\s+estimate\s+status"
        r")\b",
        ql,
    ):
        return {"kind": "status", "includeInferred": include_inferred}

    # "what does X typically pay for D#### / ####"
    m = re.search(
        r"(?:how\s+much\s+(?:will|does|did)\s+)?"
        r"(.+?)\s+(?:typically\s+)?(?:pay|paid|pays|allow|write[\s-]?off)"
        r".{0,40}?\b(?:for|on)\s+(D?\d{3,5})\b",
        q,
        re.IGNORECASE,
    )
    if not m:
        m = re.search(
            r"\b(delta(?:\s+dental)?(?:\s+of\s+\w+)?|metlife|cigna|bcbs(?:\s+of\s+\w+)?|"
            r"guardian|aetna|united\s*concordia)\b.{0,60}\b(D?\d{3,5})\b",
            q,
            re.IGNORECASE,
        )
    if not m:
        return None
    payer = str(m.group(1) or "").strip(" ?.,")
    ada = normalize_ada_code(m.group(2))
    # Strip leading filler from payer capture
    payer = re.sub(
        r"^(?:how\s+much\s+(?:will|does|did)\s+)?",
        "",
        payer,
        flags=re.IGNORECASE,
    ).strip()
    if not payer or not ada:
        return None
    return {
        "kind": "lookup",
        "payer": payer,
        "adaCode": ada,
        "includeInferred": include_inferred,
    }


def credibility_badge(credibility: str | None, tier: str | None = None) -> dict[str, str]:
    cred = str(credibility or "").strip().lower()
    if cred == "high":
        return {"badge": "high", "tone": "ok", "label": "High (n>=30) — budgeting OK"}
    if cred == "usable":
        return {"badge": "usable", "tone": "warn", "label": "Usable (n>=10) — negotiation ballpark"}
    if cred in {"usable_inferred", "weak_inferred"} or str(tier or "") == "inferred":
        return {
            "badge": "inferred",
            "tone": "danger",
            "label": "Inferred — proportional split; never quote to patient",
        }
    return {"badge": "insufficient", "tone": "warn", "label": "Insufficient data (empty != $0)"}


def format_probabilistic_estimate_reply(
    est: dict[str, Any] | None,
    *,
    payer: str,
    ada: str,
    include_inferred: bool = False,
) -> str:
    if not est:
        extra = (
            " Pass include-inferred / say 'show uncertain estimates' only for directional sense."
            if not include_inferred
            else ""
        )
        return (
            f"Insufficient data for {payer or 'that payer'} x {ada or 'that ADA'} "
            f"(exact usable needs n>={CREDIBILITY['exact_publish_n']}). "
            f"empty != $0 -- not a $0 estimate.{extra}"
        )
    badge = credibility_badge(str(est.get("credibility") or ""), str(est.get("tier") or ""))
    paid = est.get("paid_median") if est.get("paid_median") is not None else est.get("paid_avg")
    wo = est.get("write_off_median") if est.get("write_off_median") is not None else est.get("write_off_avg")
    n = est.get("sample_size")
    lines = [
        f"InsCo x ADA ledger estimate (HAL-10582/83) · badge=`{badge['badge']}` · {badge['label']}.",
        f"{est.get('insurance_company')} x {est.get('ada_code')}: "
        f"typical Ins paid ~${float(paid or 0):,.2f}, write-off ~${float(wo or 0):,.2f} "
        f"(n={n}, tier={est.get('tier')}, credibility={est.get('credibility')}).",
        "Estimate from ledger codes 2/51 + coverage -- not a contractual guarantee / not gold payment lines.",
    ]
    if str(est.get("tier")) == "inferred":
        lines.append(
            "WARNING: inferred proportional allocation across multi-ADA visits "
            "(invented splits). Do not quote to patients."
        )
    return "\n".join(lines)


def format_probabilistic_status_reply(status: dict[str, Any] | None = None) -> str:
    st = status if isinstance(status, dict) else probabilistic_report_status()
    pub = int(st.get("publishedCells") or 0)
    high = int(st.get("highCredibilityCells") or 0)
    total = int(st.get("totalCells") or 0)
    return (
        f"InsCo x ADA probabilistic report status: published={pub} "
        f"(high={high}) · stored cells={total}. "
        f"Default HAL shows exact usable+ only; inferred requires opt-in. "
        f"Gold payment lines still separate (hal-10400). empty != $0."
    )


def list_published_estimate_rows(
    *,
    db_path: Path | None = None,
    include_inferred: bool = False,
    limit: int = 40,
) -> list[dict[str, Any]]:
    target = Path(db_path) if db_path else resolve_analytics_db()
    if not target or not target.is_file():
        return []
    conn = sqlite3.connect(f"file:{target}?mode=ro", uri=True)
    try:
        ensure_probabilistic_schema(conn)
        if include_inferred:
            where = "credibility != 'insufficient' AND tier IN ('exact','inferred')"
        else:
            where = "credibility IN ('high','usable') AND tier = 'exact'"
        rows = conn.execute(
            f"""
            SELECT insurance_company, ada_code, tier, sample_size,
                   paid_median, paid_avg, write_off_median, write_off_avg, credibility
            FROM insco_ada_probabilistic_estimates
            WHERE {where}
            ORDER BY
              CASE credibility WHEN 'high' THEN 0 WHEN 'usable' THEN 1 ELSE 2 END,
              sample_size DESC
            LIMIT ?
            """,
            (max(1, int(limit)),),
        ).fetchall()
        out: list[dict[str, Any]] = []
        for r in rows:
            badge = credibility_badge(str(r[8]), str(r[2]))
            out.append(
                {
                    "insuranceCompany": r[0],
                    "adaCode": r[1],
                    "tier": r[2],
                    "sampleSize": r[3],
                    "paidMedian": r[4] if r[4] is not None else r[5],
                    "writeOffMedian": r[6] if r[6] is not None else r[7],
                    "credibility": r[8],
                    "badge": badge["badge"],
                    "badgeLabel": badge["label"],
                    "tone": badge["tone"],
                }
            )
        return out
    finally:
        conn.close()


def insco_ada_estimate_widget(*, include_inferred: bool = False) -> dict[str, Any]:
    """SoftDent page status widget — exact usable+ by default."""
    st = probabilistic_report_status()
    rows = list_published_estimate_rows(include_inferred=False, limit=12)
    pub = int(st.get("publishedCells") or 0)
    high = int(st.get("highCredibilityCells") or 0)
    if pub <= 0:
        status = "empty"
        message = "No credible InsCo x ADA ledger estimates yet — run probabilistic rebuild / sync."
    elif high > 0:
        status = "ok"
        message = f"InsCo x ADA estimates · published={pub} · high={high} · default=exact only"
    else:
        status = "ok"
        message = f"InsCo x ADA estimates · published={pub} · high=0 · usable exact only (amber)"
    return {
        "id": "softdent-insco-ada-estimates",
        "type": "status",
        "label": "InsCo x ADA Estimates (HAL-10583)",
        "size": "full",
        "status": status,
        "message": message,
        "hint": (
            "Ledger 2/51 + coverage · exact usable+ shown · inferred hidden until "
            "'show uncertain estimates'. Not contractual / not payment-line gold path. empty != $0."
        ),
        "publishedCells": pub,
        "highCredibilityCells": high,
        "includeInferredDefault": False,
        "topExact": rows,
        "halChips": [
            {"label": "InsCo x ADA estimate status", "query": "InsCo ADA estimate status"},
            {
                "label": "Delta KS pay for D1110?",
                "query": "How much does Delta Dental of KS typically pay for D1110?",
            },
            {
                "label": "Show uncertain estimates",
                "query": "Show uncertain estimates: how much does Delta Dental of KS pay for D1110?",
            },
        ],
        "honesty": CREDIBILITY.get("honesty"),
        "inferredOptIn": bool(include_inferred),
    }


def log_inferred_view_audit(*, payer: str, ada: str, source: str = "hal") -> None:
    """Best-effort audit when staff opts into inferred estimates."""
    try:
        root = resolve_exports_dir()
        root.mkdir(parents=True, exist_ok=True)
        path = root / "insco_ada_inferred_view_audit.jsonl"
        line = json.dumps(
            {
                "at": _utc_now(),
                "source": source,
                "payer": payer,
                "ada": ada,
                "warning": (
                    "User viewed inferred InsCo×ADA estimate — invented proportional split warning acknowledged."
                ),
            },
            ensure_ascii=True,
        )
        with path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
    except Exception:
        pass


def export_probabilistic_report(
    *,
    db_path: Path | None = None,
    dest: Path | None = None,
) -> dict[str, Any]:
    """Write JSON + markdown summary of published cells + credibility guidance."""
    target = Path(db_path) if db_path else resolve_analytics_db()
    out_dir = Path(dest) if dest else resolve_exports_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    result: dict[str, Any] = {"ok": False, "jsonPath": None, "mdPath": None}
    if not target or not target.is_file():
        result["error"] = "analytics_db_missing"
        return result

    conn = sqlite3.connect(f"file:{target}?mode=ro", uri=True)
    try:
        ensure_probabilistic_schema(conn)
        meta = {
            str(k): str(v)
            for k, v in conn.execute("SELECT key, value FROM insco_ada_probabilistic_meta").fetchall()
        }
        rows = conn.execute(
            """
            SELECT insurance_company, ada_code, tier, sample_size,
                   paid_avg, paid_median, write_off_avg, write_off_median,
                   billed_avg, credibility
            FROM insco_ada_probabilistic_estimates
            WHERE credibility != 'insufficient'
            ORDER BY
              CASE credibility
                WHEN 'high' THEN 0
                WHEN 'usable' THEN 1
                WHEN 'usable_inferred' THEN 2
                ELSE 3
              END,
              sample_size DESC,
              insurance_company,
              ada_code
            """
        ).fetchall()
        published = [
            {
                "insuranceCompany": r[0],
                "adaCode": r[1],
                "tier": r[2],
                "sampleSize": r[3],
                "paidAvg": r[4],
                "paidMedian": r[5],
                "writeOffAvg": r[6],
                "writeOffMedian": r[7],
                "billedAvg": r[8],
                "credibility": r[9],
            }
            for r in rows
        ]
        # diagnostics counts
        tier_cred = conn.execute(
            """
            SELECT tier, credibility, COUNT(*), SUM(sample_size)
            FROM insco_ada_probabilistic_estimates
            GROUP BY 1, 2
            ORDER BY 1, 2
            """
        ).fetchall()
    finally:
        conn.close()

    payload = {
        "ok": True,
        "def": "HAL-10582",
        "checkedAt": _utc_now(),
        "meta": meta,
        "credibilityRules": CREDIBILITY,
        "howMuchDataForCredibility": {
            "exact_usable": f"≥{CREDIBILITY['exact_publish_n']} single-ADA pay/write-off events per InsCo×ADA",
            "exact_high": f"≥{CREDIBILITY['exact_high_n']} exact events (preferred)",
            "inferred_usable": (
                f"≥{CREDIBILITY['inferred_publish_n']} multi-ADA (2–3) events; always labeled inferred"
            ),
            "inferred_stronger": f"≥{CREDIBILITY['inferred_high_n']} inferred events",
            "history_window": f"~{CREDIBILITY['recommended_history_months']} months of account TX recommended",
            "coverage": "Primary insurance on most active accounts (Sensei/ODBC sd_patient_insurance)",
            "matrix_goal": (
                f"~{CREDIBILITY['target_exact_cells_n10']} exact cells at n≥10 "
                f"(or ~{CREDIBILITY['target_exact_cells_n30']} at n≥30) for a useful top-code report"
            ),
            "gold_path": "SoftDent Insurance Payment Analysis / ERA SVC still required for contractual line truth",
        },
        "tierCredibilityCounts": [
            {"tier": a, "credibility": b, "cells": c, "sampleSum": d} for a, b, c, d in tier_cred
        ],
        "publishedCells": published,
        "publishedCount": len(published),
        "honesty": CREDIBILITY["honesty"],
    }

    stamp = date.today().isoformat()
    json_path = out_dir / f"insco_ada_probabilistic_report_{stamp}.json"
    md_path = out_dir / f"insco_ada_probabilistic_report_{stamp}.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        f"# InsCo × ADA Probabilistic Report ({stamp})",
        "",
        f"Published cells: **{len(published)}** (credibility ≠ insufficient).",
        "",
        "## How much data for credibility",
        "",
        f"- **Exact usable:** ≥{CREDIBILITY['exact_publish_n']} single-ADA events per InsCo×ADA",
        f"- **Exact high:** ≥{CREDIBILITY['exact_high_n']} exact events",
        f"- **Inferred usable:** ≥{CREDIBILITY['inferred_publish_n']} events (2–3 ADAs; labeled)",
        f"- **Inferred stronger:** ≥{CREDIBILITY['inferred_high_n']} inferred events",
        f"- **History:** ~{CREDIBILITY['recommended_history_months']} months of SoftDent account TX",
        f"- **Coverage:** primary payer on active accounts (`sd_patient_insurance`)",
        f"- **Matrix goal:** ~{CREDIBILITY['target_exact_cells_n10']} exact cells at n≥10",
        "",
        "## Honesty",
        "",
        CREDIBILITY["honesty"],
        "",
        "## Top published cells",
        "",
        "| Carrier | ADA | Tier | Cred | n | Paid med | WO med |",
        "|---|---|---|---|---:|---:|---:|",
    ]
    for row in published[:40]:
        lines.append(
            f"| {row['insuranceCompany']} | {row['adaCode']} | {row['tier']} | "
            f"{row['credibility']} | {row['sampleSize']} | "
            f"{row['paidMedian'] if row['paidMedian'] is not None else row['paidAvg']} | "
            f"{row['writeOffMedian'] if row['writeOffMedian'] is not None else row['writeOffAvg']} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Also drop a stable inbox copy when possible
    try:
        from import_loader import softdent_import_dir

        inbox = softdent_import_dir()
        inbox.mkdir(parents=True, exist_ok=True)
        stable = inbox / "softdent_insco_ada_probabilistic.json"
        stable.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        result["inboxPath"] = str(stable)
    except Exception as exc:  # noqa: BLE001
        result["inboxError"] = f"{type(exc).__name__}:{exc}"

    result.update({"ok": True, "jsonPath": str(json_path), "mdPath": str(md_path), "publishedCount": len(published)})
    return result


def run_insco_ada_probabilistic_report(
    *,
    db_path: Path | None = None,
    period_start: str | None = None,
    period_end: str | None = None,
) -> dict[str, Any]:
    target = Path(db_path) if db_path else resolve_analytics_db()
    out: dict[str, Any] = {"ok": False, "dbPath": str(target) if target else None}
    if not target or not target.is_file():
        out["error"] = "analytics_db_missing"
        return out
    conn = sqlite3.connect(str(target))
    try:
        build = build_insco_ada_probabilistic_estimates(
            conn, period_start=period_start, period_end=period_end
        )
        out["build"] = build
    finally:
        conn.close()
    export = export_probabilistic_report(db_path=target)
    out["export"] = export
    out["ok"] = bool(build.get("ok")) and bool(export.get("ok"))
    return out


def probabilistic_report_status(db_path: Path | None = None) -> dict[str, Any]:
    target = Path(db_path) if db_path else resolve_analytics_db()
    status: dict[str, Any] = {
        "ok": False,
        "dbPath": str(target) if target else None,
        "publishedCells": 0,
        "highCredibilityCells": 0,
        "credibilityRules": CREDIBILITY,
    }
    if not target or not target.is_file():
        status["error"] = "analytics_db_missing"
        return status
    conn = sqlite3.connect(f"file:{target}?mode=ro", uri=True)
    try:
        ensure_probabilistic_schema(conn)
        status["publishedCells"] = int(
            conn.execute(
                "SELECT COUNT(*) FROM insco_ada_probabilistic_estimates WHERE credibility != 'insufficient'"
            ).fetchone()[0]
            or 0
        )
        status["highCredibilityCells"] = int(
            conn.execute(
                "SELECT COUNT(*) FROM insco_ada_probabilistic_estimates WHERE credibility = 'high'"
            ).fetchone()[0]
            or 0
        )
        status["totalCells"] = int(
            conn.execute("SELECT COUNT(*) FROM insco_ada_probabilistic_estimates").fetchone()[0] or 0
        )
        meta = {
            str(k): str(v)
            for k, v in conn.execute("SELECT key, value FROM insco_ada_probabilistic_meta").fetchall()
        }
        status["meta"] = meta
        status["ok"] = status["publishedCells"] >= 0
    finally:
        conn.close()
    return status


if __name__ == "__main__":
    print(json.dumps(run_insco_ada_probabilistic_report(), indent=2, default=str))
