from __future__ import annotations

from typing import Any

from app.hal.widget_supervisor import (
    HAL9000Supervisor,
    PipelineExecutionRecord,
    QuickBooksMetrics,
    QuickBooksOnlineConfig,
    SoftDentMetrics,
    SoftDentOdbcConfig,
    WidgetApiConfig,
)


class SequencedExtractor:
    def __init__(self, values: list[Any], config: object) -> None:
        self._values = list(values)
        self.config = config

    def extract(self) -> Any:
        if not self._values:
            raise RuntimeError("no more sequenced extractor values")
        value = self._values.pop(0)
        if isinstance(value, Exception):
            raise value
        return value


class RecordingPublisher:
    def __init__(self, config: WidgetApiConfig) -> None:
        self.config = config
        self.payloads: list[dict[str, Any]] = []

    def publish(self, payload) -> dict[str, Any]:
        body = payload.to_dict()
        self.payloads.append(body)
        return {
            "status_code": 202,
            "ack": {
                "accepted": True,
                "endpoint": self.config.endpoint_url(),
                "run_id": body["run_id"],
            },
        }


def _quickbooks_metrics() -> QuickBooksMetrics:
    return QuickBooksMetrics(
        revenue_total=155000.0,
        expense_total=93000.0,
        net_income=62000.0,
        accounts_receivable_total=18400.0,
        accounts_payable_total=12850.0,
        source_reported_at="2026-06-23T12:00:00Z",
    )


def _softdent_metrics() -> SoftDentMetrics:
    return SoftDentMetrics(
        production_total=171500.0,
        collections_total=149250.0,
        patient_balance_total=9100.0,
        insurance_balance_total=12600.0,
        patient_count=642,
        provider_count=7,
        unsubmitted_claim_count=9,
        outstanding_claim_count=34,
        outstanding_claim_amount=22110.0,
        source_reported_at="2026-06-23T12:05:00Z",
    )


def _quickbooks_config() -> QuickBooksOnlineConfig:
    return QuickBooksOnlineConfig(
        client_id="client-id",
        client_secret="client-secret",
        realm_id="realm-id",
        access_token="access-token",
    )


def _softdent_config() -> SoftDentOdbcConfig:
    return SoftDentOdbcConfig(connection_string="Driver={ODBC Driver};Server=softdent")


def _widget_api_config() -> WidgetApiConfig:
    return WidgetApiConfig(base_url="https://dashboard.internal")


def test_hal9000_supervisor_runs_cycle_and_publishes_unified_widget_payload():
    publisher = RecordingPublisher(_widget_api_config())
    hal = HAL9000Supervisor(
        SequencedExtractor([_quickbooks_metrics()], _quickbooks_config()),
        SequencedExtractor([_softdent_metrics()], _softdent_config()),
        publisher,
    )

    snapshot = hal.run_cycle()

    assert snapshot["manager"] == "HAL 9000"
    assert snapshot["jobs"]["quickbooks_extract"]["status"] == "SUCCESS"
    assert snapshot["jobs"]["softdent_extract"]["status"] == "SUCCESS"
    assert snapshot["jobs"]["widget_publish"]["status"] == "SUCCESS"
    assert publisher.payloads
    payload = publisher.payloads[0]
    assert payload["manager"] == "HAL 9000"
    assert payload["widgets"]["practice_financial_overview"]["metrics"]["monthly_revenue"] == 155000.0
    assert payload["widgets"]["practice_financial_overview"]["metrics"]["collection_rate"] == 87.03
    assert payload["widgets"]["accounts_payable_automation"]["metrics"]["open_bills_total"] == 12850.0
    assert payload["widgets"]["smart_claims_and_receivables"]["metrics"]["outstanding_claim_count"] == 34
    assert payload["sources"]["quickbooks_online"]["last_status"] == "SUCCESS"
    assert payload["sources"]["softdent"]["last_status"] == "SUCCESS"


def test_hal9000_supervisor_alerts_and_keeps_cached_snapshot_when_quickbooks_fails():
    publisher = RecordingPublisher(_widget_api_config())
    alerts: list[tuple[str, PipelineExecutionRecord]] = []

    hal = HAL9000Supervisor(
        SequencedExtractor([_quickbooks_metrics(), RuntimeError("QuickBooks API timeout")], _quickbooks_config()),
        SequencedExtractor([_softdent_metrics(), _softdent_metrics()], _softdent_config()),
        publisher,
        alert_handler=lambda message, record: alerts.append((message, record)),
    )

    hal.run_cycle()
    snapshot = hal.run_cycle()

    assert snapshot["jobs"]["quickbooks_extract"]["status"] == "FAILED"
    assert snapshot["jobs"]["quickbooks_extract"]["failure_count"] == 1
    assert alerts
    assert "QuickBooks API timeout" in alerts[0][0]
    degraded_payload = publisher.payloads[-1]
    assert degraded_payload["sources"]["quickbooks_online"]["last_status"] == "FAILED"
    assert degraded_payload["sources"]["quickbooks_online"]["cached_data_available"] is True
    assert degraded_payload["widgets"]["practice_financial_overview"]["status"] == "DEGRADED"


def test_hal9000_supervisor_updates_intervals_and_runtime_configuration():
    publisher = RecordingPublisher(_widget_api_config())
    hal = HAL9000Supervisor(
        SequencedExtractor([_quickbooks_metrics()], _quickbooks_config()),
        SequencedExtractor([_softdent_metrics()], _softdent_config()),
        publisher,
        publish_interval_seconds=300.0,
    )

    hal.update_configuration(
        quickbooks={"report_end": "2026-06-30"},
        widget_api={"endpoint_path": "/api/widgets/custom-update"},
        intervals={"widget_publish": 45.0},
    )

    assert hal.quickbooks_extractor.config.report_end == "2026-06-30"
    assert hal.publisher.config.endpoint_path == "/api/widgets/custom-update"
    assert hal.jobs["widget_publish"].interval_seconds == 45.0