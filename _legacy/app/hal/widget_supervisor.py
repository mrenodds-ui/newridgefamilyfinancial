from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
import logging
import os
import time
from typing import Any, Callable, Mapping
from uuid import uuid4

import requests
from requests import Response, Session
from requests_oauthlib import OAuth2Session

try:
    import pyodbc
except ImportError:  # pragma: no cover - exercised in environments without ODBC access
    pyodbc = None


logger = logging.getLogger(__name__)

DEFAULT_SOFTDENT_LEDGER_QUERY = """
SELECT
    COALESCE(SUM(CASE WHEN transaction_type = 'PRODUCTION' THEN amount ELSE 0 END), 0) AS production_total,
    COALESCE(SUM(CASE WHEN transaction_type = 'COLLECTION' THEN amount ELSE 0 END), 0) AS collections_total,
    COALESCE(SUM(patient_balance), 0) AS patient_balance_total,
    COALESCE(SUM(insurance_balance), 0) AS insurance_balance_total,
    COUNT(DISTINCT patient_id) AS patient_count
FROM billing_ledger
WHERE posted_at >= ? AND posted_at <= ?;
""".strip()

DEFAULT_SOFTDENT_CLAIMS_QUERY = """
SELECT
    COALESCE(SUM(CASE WHEN claim_status = 'UNSUBMITTED' THEN 1 ELSE 0 END), 0) AS unsubmitted_claim_count,
    COALESCE(SUM(CASE WHEN claim_status = 'OUTSTANDING' THEN 1 ELSE 0 END), 0) AS outstanding_claim_count,
    COALESCE(SUM(CASE WHEN claim_status = 'OUTSTANDING' THEN claim_amount ELSE 0 END), 0) AS outstanding_claim_amount
FROM insurance_claim
WHERE service_date >= ? AND service_date <= ?;
""".strip()

DEFAULT_SOFTDENT_PROVIDER_QUERY = """
SELECT
    COUNT(DISTINCT provider_id) AS provider_count
FROM billing_ledger
WHERE posted_at >= ? AND posted_at <= ?;
""".strip()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_float(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        normalized = value.replace(",", "").strip()
        if not normalized:
            return 0.0
        try:
            return float(normalized)
        except ValueError:
            return 0.0
    return 0.0


def _coerce_int(value: Any) -> int:
    return int(round(_coerce_float(value)))


def _normalize_endpoint_path(value: str) -> str:
    path = value.strip() or "/api/widgets/update"
    return path if path.startswith("/") else f"/{path}"


def _default_report_window() -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).date().isoformat()
    end = now.date().isoformat()
    return start, end


class PipelineStatus(str, Enum):
    IDLE = "IDLE"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


@dataclass(slots=True)
class QuickBooksOnlineConfig:
    client_id: str
    client_secret: str
    realm_id: str
    access_token: str
    refresh_token: str | None = None
    token_url: str = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
    api_base_url: str = "https://quickbooks.api.intuit.com"
    report_start: str | None = None
    report_end: str | None = None
    minor_version: str = "75"
    timeout_seconds: float = 20.0

    def token_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "access_token": self.access_token,
            "token_type": "Bearer",
        }
        if self.refresh_token:
            payload["refresh_token"] = self.refresh_token
        return payload


@dataclass(slots=True)
class SoftDentOdbcConfig:
    connection_string: str
    ledger_query: str = DEFAULT_SOFTDENT_LEDGER_QUERY
    claims_query: str = DEFAULT_SOFTDENT_CLAIMS_QUERY
    provider_query: str = DEFAULT_SOFTDENT_PROVIDER_QUERY
    report_start: str | None = None
    report_end: str | None = None
    timeout_seconds: float = 20.0


@dataclass(slots=True)
class WidgetApiConfig:
    base_url: str
    endpoint_path: str = "/api/widgets/update"
    api_key: str | None = None
    api_key_header: str = "X-API-Key"
    timeout_seconds: float = 15.0

    def endpoint_url(self) -> str:
        return f"{self.base_url.rstrip('/')}" + _normalize_endpoint_path(self.endpoint_path)


@dataclass(slots=True)
class QuickBooksMetrics:
    revenue_total: float
    expense_total: float
    net_income: float
    accounts_receivable_total: float
    accounts_payable_total: float
    source_reported_at: str


@dataclass(slots=True)
class SoftDentMetrics:
    production_total: float
    collections_total: float
    patient_balance_total: float
    insurance_balance_total: float
    patient_count: int
    provider_count: int
    unsubmitted_claim_count: int
    outstanding_claim_count: int
    outstanding_claim_amount: float
    source_reported_at: str


@dataclass(slots=True)
class PipelineExecutionRecord:
    job_name: str
    status: str = PipelineStatus.IDLE.value
    started_at: str | None = None
    finished_at: str | None = None
    last_success_at: str | None = None
    duration_seconds: float | None = None
    error: str | None = None
    summary: str | None = None
    run_count: int = 0
    success_count: int = 0
    failure_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class PipelineJob:
    name: str
    handler: Callable[[], Any]
    interval_seconds: float
    record: PipelineExecutionRecord
    next_run_monotonic: float = 0.0


@dataclass(slots=True)
class UnifiedWidgetPayload:
    manager: str
    run_id: str
    generated_at: str
    widgets: dict[str, dict[str, Any]]
    sources: dict[str, dict[str, Any]]
    jobs: dict[str, dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "manager": self.manager,
            "run_id": self.run_id,
            "generated_at": self.generated_at,
            "widgets": self.widgets,
            "sources": self.sources,
            "jobs": self.jobs,
        }


class QuickBooksOnlineExtractor:
    def __init__(
        self,
        config: QuickBooksOnlineConfig,
        *,
        session_factory: Callable[..., OAuth2Session] = OAuth2Session,
        token_updater: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self.config = config
        self._session_factory = session_factory
        self._token_updater = token_updater

    def extract(self) -> QuickBooksMetrics:
        session = self._build_session()
        profit_and_loss = self._get_report(session, "ProfitAndLoss")
        balance_sheet = self._get_report(session, "BalanceSheet")
        profit_loss_totals = _collect_quickbooks_report_totals(profit_and_loss)
        balance_sheet_totals = _collect_quickbooks_report_totals(balance_sheet)

        revenue_total = _lookup_first_report_total(profit_loss_totals, "Total Income", "Income")
        expense_total = _lookup_first_report_total(profit_loss_totals, "Total Expenses", "Expenses")
        net_income = _lookup_first_report_total(profit_loss_totals, "Net Income", "Net Income (Loss)")
        if net_income == 0.0 and (revenue_total or expense_total):
            net_income = revenue_total - expense_total

        return QuickBooksMetrics(
            revenue_total=revenue_total,
            expense_total=expense_total,
            net_income=net_income,
            accounts_receivable_total=_lookup_first_report_total(
                balance_sheet_totals,
                "Accounts Receivable",
                "Total Accounts Receivable",
            ),
            accounts_payable_total=_lookup_first_report_total(
                balance_sheet_totals,
                "Accounts Payable",
                "Total Accounts Payable",
            ),
            source_reported_at=_utc_now_iso(),
        )

    def _build_session(self) -> OAuth2Session:
        return self._session_factory(
            client_id=self.config.client_id,
            token=self.config.token_payload(),
            auto_refresh_url=self.config.token_url,
            auto_refresh_kwargs={
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
            },
            token_updater=self._token_updater,
        )

    def _get_report(self, session: OAuth2Session, report_name: str) -> dict[str, Any]:
        params = {
            "minorversion": self.config.minor_version,
            "accounting_method": "Accrual",
        }
        report_start, report_end = _resolve_report_window(self.config.report_start, self.config.report_end)
        params["start_date"] = report_start
        params["end_date"] = report_end
        response = session.get(
            f"{self.config.api_base_url.rstrip('/')}/v3/company/{self.config.realm_id}/reports/{report_name}",
            params=params,
            headers={"Accept": "application/json"},
            timeout=self.config.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise RuntimeError(f"QuickBooks Online {report_name} response was not a JSON object")
        return payload


class SoftDentOdbcExtractor:
    def __init__(
        self,
        config: SoftDentOdbcConfig,
        *,
        connect_func: Callable[..., Any] | None = None,
    ) -> None:
        self.config = config
        self._connect_func = connect_func or (pyodbc.connect if pyodbc is not None else None)

    def extract(self) -> SoftDentMetrics:
        if self._connect_func is None:
            raise RuntimeError("pyodbc is required for SoftDent extraction but is not installed in this environment")
        if not self.config.connection_string.strip():
            raise ValueError("SoftDent ODBC connection string is required")

        report_start, report_end = _resolve_report_window(self.config.report_start, self.config.report_end)
        params = (report_start, report_end)

        with self._connect_func(self.config.connection_string, timeout=self.config.timeout_seconds) as connection:
            ledger_row = _fetch_single_row(connection, self.config.ledger_query, params)
            claims_row = _fetch_single_row(connection, self.config.claims_query, params)
            provider_row = _fetch_single_row(connection, self.config.provider_query, params)

        return SoftDentMetrics(
            production_total=_coerce_float(ledger_row.get("production_total")),
            collections_total=_coerce_float(ledger_row.get("collections_total")),
            patient_balance_total=_coerce_float(ledger_row.get("patient_balance_total")),
            insurance_balance_total=_coerce_float(ledger_row.get("insurance_balance_total")),
            patient_count=_coerce_int(ledger_row.get("patient_count")),
            provider_count=_coerce_int(provider_row.get("provider_count")),
            unsubmitted_claim_count=_coerce_int(claims_row.get("unsubmitted_claim_count")),
            outstanding_claim_count=_coerce_int(claims_row.get("outstanding_claim_count")),
            outstanding_claim_amount=_coerce_float(claims_row.get("outstanding_claim_amount")),
            source_reported_at=_utc_now_iso(),
        )


class WidgetApiPublisher:
    def __init__(self, config: WidgetApiConfig, *, session: Session | None = None) -> None:
        self.config = config
        self._session = session or requests.Session()

    def publish(self, payload: UnifiedWidgetPayload | Mapping[str, Any]) -> dict[str, Any]:
        body = payload.to_dict() if isinstance(payload, UnifiedWidgetPayload) else dict(payload)
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers[self.config.api_key_header] = self.config.api_key

        response = self._session.post(
            self.config.endpoint_url(),
            json=body,
            headers=headers,
            timeout=self.config.timeout_seconds,
        )
        response.raise_for_status()
        return {
            "status_code": response.status_code,
            "ack": _safe_response_json(response),
        }


class HAL9000Supervisor:
    manager_name = "HAL 9000"

    def __init__(
        self,
        quickbooks_extractor: QuickBooksOnlineExtractor | Any,
        softdent_extractor: SoftDentOdbcExtractor | Any,
        publisher: WidgetApiPublisher | Any,
        *,
        quickbooks_interval_seconds: float = 900.0,
        softdent_interval_seconds: float = 900.0,
        publish_interval_seconds: float = 300.0,
        alert_handler: Callable[[str, PipelineExecutionRecord], None] | None = None,
    ) -> None:
        self.quickbooks_extractor = quickbooks_extractor
        self.softdent_extractor = softdent_extractor
        self.publisher = publisher
        self._alert_handler = alert_handler or self._default_alert_handler
        self._latest_quickbooks: QuickBooksMetrics | None = None
        self._latest_softdent: SoftDentMetrics | None = None
        self._last_published_payload: UnifiedWidgetPayload | None = None
        self._last_publish_ack: dict[str, Any] | None = None
        self.jobs: dict[str, PipelineJob] = {}
        self.initialize_jobs(
            quickbooks_interval_seconds=quickbooks_interval_seconds,
            softdent_interval_seconds=softdent_interval_seconds,
            publish_interval_seconds=publish_interval_seconds,
        )

    def initialize_jobs(
        self,
        *,
        quickbooks_interval_seconds: float,
        softdent_interval_seconds: float,
        publish_interval_seconds: float,
    ) -> None:
        self.jobs.clear()
        self.register_job("quickbooks_extract", self._run_quickbooks_extract, interval_seconds=quickbooks_interval_seconds)
        self.register_job("softdent_extract", self._run_softdent_extract, interval_seconds=softdent_interval_seconds)
        self.register_job("widget_publish", self._run_widget_publish, interval_seconds=publish_interval_seconds)

    def register_job(self, name: str, handler: Callable[[], Any], *, interval_seconds: float) -> None:
        self.jobs[name] = PipelineJob(
            name=name,
            handler=handler,
            interval_seconds=float(interval_seconds),
            record=PipelineExecutionRecord(job_name=name),
        )

    def run_cycle(self) -> dict[str, Any]:
        for name in ("quickbooks_extract", "softdent_extract", "widget_publish"):
            self._run_job(name)
        return self.get_status_snapshot()

    def run_pending(self, *, now_monotonic: float | None = None) -> dict[str, Any]:
        current = time.monotonic() if now_monotonic is None else now_monotonic
        for job in self.jobs.values():
            if current >= job.next_run_monotonic:
                self._run_job(job.name, now_monotonic=current)
        return self.get_status_snapshot()

    def update_pipeline_interval(self, job_name: str, interval_seconds: float) -> None:
        job = self.jobs.get(job_name)
        if job is None:
            raise KeyError(f"Unknown HAL 9000 pipeline job: {job_name}")
        job.interval_seconds = float(interval_seconds)

    def update_configuration(
        self,
        *,
        quickbooks: dict[str, Any] | None = None,
        softdent: dict[str, Any] | None = None,
        widget_api: dict[str, Any] | None = None,
        intervals: dict[str, float] | None = None,
    ) -> None:
        if quickbooks:
            _apply_overrides(self.quickbooks_extractor.config, quickbooks, config_name="quickbooks")
        if softdent:
            _apply_overrides(self.softdent_extractor.config, softdent, config_name="softdent")
        if widget_api:
            _apply_overrides(self.publisher.config, widget_api, config_name="widget_api")
        if intervals:
            for job_name, seconds in intervals.items():
                self.update_pipeline_interval(job_name, seconds)

    def get_status_snapshot(self) -> dict[str, Any]:
        return {
            "manager": self.manager_name,
            "generated_at": _utc_now_iso(),
            "jobs": {name: job.record.to_dict() for name, job in self.jobs.items()},
            "has_quickbooks_snapshot": self._latest_quickbooks is not None,
            "has_softdent_snapshot": self._latest_softdent is not None,
            "last_publish_ack": self._last_publish_ack,
        }

    def _run_job(self, name: str, *, now_monotonic: float | None = None) -> Any:
        job = self.jobs[name]
        record = job.record
        record.run_count += 1
        record.started_at = _utc_now_iso()
        record.error = None
        start_perf = time.perf_counter()

        try:
            result = job.handler()
        except Exception as exc:
            record.status = PipelineStatus.FAILED.value
            record.failure_count += 1
            record.summary = f"{name} failed"
            record.error = str(exc)
            self._finalize_job_record(job, record, start_perf, now_monotonic=now_monotonic)
            self._emit_alert(f"HAL 9000 detected a {name} failure: {exc}", record)
            return None

        record.status = PipelineStatus.SUCCESS.value
        record.success_count += 1
        record.last_success_at = _utc_now_iso()
        record.summary = _build_result_summary(name, result)
        self._finalize_job_record(job, record, start_perf, now_monotonic=now_monotonic)
        return result

    def _finalize_job_record(
        self,
        job: PipelineJob,
        record: PipelineExecutionRecord,
        start_perf: float,
        *,
        now_monotonic: float | None,
    ) -> None:
        record.finished_at = _utc_now_iso()
        record.duration_seconds = round(time.perf_counter() - start_perf, 6)
        base_time = time.monotonic() if now_monotonic is None else now_monotonic
        job.next_run_monotonic = base_time + job.interval_seconds

    def _run_quickbooks_extract(self) -> QuickBooksMetrics:
        metrics = self.quickbooks_extractor.extract()
        self._latest_quickbooks = metrics
        return metrics

    def _run_softdent_extract(self) -> SoftDentMetrics:
        metrics = self.softdent_extractor.extract()
        self._latest_softdent = metrics
        return metrics

    def _run_widget_publish(self) -> dict[str, Any]:
        payload = self._build_unified_payload()
        ack = self.publisher.publish(payload)
        self._last_published_payload = payload
        self._last_publish_ack = ack
        return ack

    def _build_unified_payload(self) -> UnifiedWidgetPayload:
        if self._latest_quickbooks is None and self._latest_softdent is None:
            raise RuntimeError("HAL 9000 cannot publish widgets before at least one source extract succeeds")

        quickbooks = self._latest_quickbooks
        softdent = self._latest_softdent
        collection_rate = None
        if softdent is not None and softdent.production_total > 0:
            collection_rate = round((softdent.collections_total / softdent.production_total) * 100, 2)
        total_ar = None
        if softdent is not None:
            total_ar = round(softdent.patient_balance_total + softdent.insurance_balance_total, 2)

        widgets = {
            "practice_financial_overview": {
                "title": "Practice Financial Overview",
                "status": _merge_widget_status(self.jobs["quickbooks_extract"].record.status, self.jobs["softdent_extract"].record.status),
                "metrics": {
                    "monthly_revenue": quickbooks.revenue_total if quickbooks else None,
                    "monthly_net_income": quickbooks.net_income if quickbooks else None,
                    "production_total": softdent.production_total if softdent else None,
                    "collections_total": softdent.collections_total if softdent else None,
                    "collection_rate": collection_rate,
                },
            },
            "accounts_payable_automation": {
                "title": "Accounts Payable Automation",
                "status": self.jobs["quickbooks_extract"].record.status,
                "metrics": {
                    "open_bills_total": quickbooks.accounts_payable_total if quickbooks else None,
                    "expense_total": quickbooks.expense_total if quickbooks else None,
                },
            },
            "smart_claims_and_receivables": {
                "title": "Smart Claims & Receivables",
                "status": self.jobs["softdent_extract"].record.status,
                "metrics": {
                    "outstanding_claim_count": softdent.outstanding_claim_count if softdent else None,
                    "outstanding_claim_amount": softdent.outstanding_claim_amount if softdent else None,
                    "unsubmitted_claim_count": softdent.unsubmitted_claim_count if softdent else None,
                    "accounts_receivable_total": total_ar,
                },
            },
            "care_delivery_performance": {
                "title": "Care Delivery Performance",
                "status": self.jobs["softdent_extract"].record.status,
                "metrics": {
                    "provider_count": softdent.provider_count if softdent else None,
                    "patient_count": softdent.patient_count if softdent else None,
                    "patient_balance_total": softdent.patient_balance_total if softdent else None,
                },
            },
        }

        return UnifiedWidgetPayload(
            manager=self.manager_name,
            run_id=uuid4().hex,
            generated_at=_utc_now_iso(),
            widgets=widgets,
            sources={
                "quickbooks_online": self._source_status_payload("quickbooks_extract", quickbooks),
                "softdent": self._source_status_payload("softdent_extract", softdent),
            },
            jobs={name: job.record.to_dict() for name, job in self.jobs.items()},
        )

    def _source_status_payload(self, job_name: str, snapshot: QuickBooksMetrics | SoftDentMetrics | None) -> dict[str, Any]:
        record = self.jobs[job_name].record
        return {
            "last_status": record.status,
            "last_success_at": record.last_success_at,
            "last_finished_at": record.finished_at,
            "last_error": record.error,
            "cached_data_available": snapshot is not None,
            "snapshot": asdict(snapshot) if snapshot is not None else None,
        }

    @staticmethod
    def _default_alert_handler(message: str, record: PipelineExecutionRecord) -> None:
        logger.error("%s [job=%s status=%s error=%s]", message, record.job_name, record.status, record.error)

    def _emit_alert(self, message: str, record: PipelineExecutionRecord) -> None:
        self._alert_handler(message, record)


def build_hal9000_supervisor_from_env(
    *,
    alert_handler: Callable[[str, PipelineExecutionRecord], None] | None = None,
) -> HAL9000Supervisor:
    quickbooks_config = QuickBooksOnlineConfig(
        client_id=_required_env("QBO_CLIENT_ID"),
        client_secret=_required_env("QBO_CLIENT_SECRET"),
        realm_id=_required_env("QBO_REALM_ID"),
        access_token=_required_env("QBO_ACCESS_TOKEN"),
        refresh_token=os.getenv("QBO_REFRESH_TOKEN") or None,
        report_start=os.getenv("QBO_REPORT_START") or None,
        report_end=os.getenv("QBO_REPORT_END") or None,
    )
    softdent_config = SoftDentOdbcConfig(
        connection_string=_required_env("SOFTDENT_ODBC_CONNECTION_STRING"),
        report_start=os.getenv("SOFTDENT_REPORT_START") or None,
        report_end=os.getenv("SOFTDENT_REPORT_END") or None,
    )
    widget_api_config = WidgetApiConfig(
        base_url=os.getenv("WIDGET_API_BASE_URL", "http://127.0.0.1:8095"),
        endpoint_path=os.getenv("WIDGET_API_ENDPOINT_PATH", "/api/widgets/update"),
        api_key=os.getenv("WIDGET_API_KEY") or None,
        api_key_header=os.getenv("WIDGET_API_KEY_HEADER", "X-API-Key"),
    )

    return HAL9000Supervisor(
        QuickBooksOnlineExtractor(quickbooks_config),
        SoftDentOdbcExtractor(softdent_config),
        WidgetApiPublisher(widget_api_config),
        quickbooks_interval_seconds=float(os.getenv("HAL_QBO_INTERVAL_SECONDS", "900")),
        softdent_interval_seconds=float(os.getenv("HAL_SOFTDENT_INTERVAL_SECONDS", "900")),
        publish_interval_seconds=float(os.getenv("HAL_WIDGET_PUBLISH_INTERVAL_SECONDS", "300")),
        alert_handler=alert_handler,
    )


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Environment variable {name} is required for HAL 9000 widget supervision")
    return value


def _resolve_report_window(start_date: str | None, end_date: str | None) -> tuple[str, str]:
    default_start, default_end = _default_report_window()
    return start_date or default_start, end_date or default_end


def _apply_overrides(config: object, overrides: Mapping[str, Any], *, config_name: str) -> None:
    for field_name, value in overrides.items():
        if not hasattr(config, field_name):
            raise ValueError(f"Unknown {config_name} configuration field: {field_name}")
        setattr(config, field_name, value)


def _fetch_single_row(connection: Any, query: str, params: tuple[str, str]) -> dict[str, Any]:
    cursor = connection.cursor()
    row = cursor.execute(query, *params).fetchone()
    if row is None:
        return {}
    columns = [column[0] for column in cursor.description or []]
    values = list(row)
    return dict(zip(columns, values, strict=False))


def _safe_response_json(response: Response) -> dict[str, Any] | str:
    try:
        payload = response.json()
    except ValueError:
        return response.text
    return payload if isinstance(payload, dict) else {"payload": payload}


def _build_result_summary(job_name: str, result: Any) -> str:
    if isinstance(result, QuickBooksMetrics):
        return f"QuickBooks revenue={result.revenue_total:.2f} net_income={result.net_income:.2f}"
    if isinstance(result, SoftDentMetrics):
        return f"SoftDent production={result.production_total:.2f} claims={result.outstanding_claim_count}"
    if isinstance(result, dict) and "status_code" in result:
        return f"Widget payload published with status {result['status_code']}"
    return f"{job_name} completed"


def _merge_widget_status(*statuses: str) -> str:
    return PipelineStatus.SUCCESS.value if all(status == PipelineStatus.SUCCESS.value for status in statuses) else "DEGRADED"


def _collect_quickbooks_report_totals(payload: Mapping[str, Any]) -> dict[str, float]:
    totals: dict[str, float] = {}
    rows = payload.get("Rows")
    _visit_quickbooks_rows(rows, totals)
    return totals


def _visit_quickbooks_rows(node: Any, totals: dict[str, float]) -> None:
    if isinstance(node, Mapping):
        if "Row" in node:
            _visit_quickbooks_rows(node.get("Row"), totals)
        if "Rows" in node:
            _visit_quickbooks_rows(node.get("Rows"), totals)

        if "Header" in node or "Summary" in node:
            label = _quickbooks_row_label(node)
            amount = _quickbooks_row_amount(node)
            if label and amount is not None:
                totals[label] = amount
        return

    if isinstance(node, list):
        for item in node:
            _visit_quickbooks_rows(item, totals)


def _quickbooks_row_label(row: Mapping[str, Any]) -> str | None:
    for section_name in ("Header", "Summary"):
        section = row.get(section_name)
        if isinstance(section, Mapping):
            col_data = section.get("ColData")
            label = _quickbooks_label_from_coldata(col_data)
            if label:
                return label
    return None


def _quickbooks_row_amount(row: Mapping[str, Any]) -> float | None:
    for section_name in ("Summary", "Header"):
        section = row.get(section_name)
        if isinstance(section, Mapping):
            amount = _quickbooks_amount_from_coldata(section.get("ColData"))
            if amount is not None:
                return amount
    return None


def _quickbooks_label_from_coldata(col_data: Any) -> str | None:
    if not isinstance(col_data, list):
        return None
    for item in col_data:
        if isinstance(item, Mapping):
            label = str(item.get("value") or "").strip()
            if label:
                return label
    return None


def _quickbooks_amount_from_coldata(col_data: Any) -> float | None:
    if not isinstance(col_data, list):
        return None
    for item in reversed(col_data):
        if not isinstance(item, Mapping):
            continue
        value = item.get("value")
        if value in (None, ""):
            continue
        amount = _coerce_float(value)
        if amount != 0.0 or str(value).strip() in {"0", "0.0", "0.00"}:
            return amount
    return None


def _lookup_first_report_total(totals: Mapping[str, float], *candidates: str) -> float:
    lowered_totals = {key.casefold(): value for key, value in totals.items()}
    for candidate in candidates:
        if candidate.casefold() in lowered_totals:
            return lowered_totals[candidate.casefold()]
    return 0.0


__all__ = [
    "HAL9000Supervisor",
    "PipelineExecutionRecord",
    "PipelineStatus",
    "QuickBooksMetrics",
    "QuickBooksOnlineConfig",
    "QuickBooksOnlineExtractor",
    "SoftDentMetrics",
    "SoftDentOdbcConfig",
    "SoftDentOdbcExtractor",
    "UnifiedWidgetPayload",
    "WidgetApiConfig",
    "WidgetApiPublisher",
    "build_hal9000_supervisor_from_env",
]