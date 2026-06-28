import app.services as services


def _kpi_value(payload: list[dict], name: str):
    for item in payload:
        if item.get("name") == name:
            return item.get("value")
    return None


def test_get_kpi_data_does_not_synthesize_ar_from_production_minus_collections(monkeypatch):
    monkeypatch.setattr(
        services,
        "build_softdent_snapshot",
        lambda: {
            "available": True,
            "period": "2026-06",
            "provider_count": 1,
            "totals": {"production": 5000.0, "collections": 1000.0},
        },
    )
    monkeypatch.setattr(services, "load_softdent_ar_rows", lambda: [])

    payload = services.get_kpi_data()

    assert _kpi_value(payload, "production") == 5000.0
    assert _kpi_value(payload, "collections") == 1000.0
    assert _kpi_value(payload, "ar") is None


def test_get_kpi_data_returns_none_ar_when_softdent_ar_export_missing(monkeypatch):
    monkeypatch.setattr(
        services,
        "build_softdent_snapshot",
        lambda: {
            "available": True,
            "period": "2026-06",
            "provider_count": 2,
            "totals": {"production": 1200.0, "collections": 900.0},
        },
    )
    monkeypatch.setattr(services, "load_softdent_ar_rows", lambda: [])

    payload = services.get_kpi_data()

    assert _kpi_value(payload, "ar") is None
    assert _kpi_value(payload, "ar") != 300.0


def test_get_kpi_data_returns_empty_list_when_softdent_snapshot_unavailable(monkeypatch):
    monkeypatch.setattr(services, "build_softdent_snapshot", lambda: {"available": False})

    payload = services.get_kpi_data()

    assert payload == []


def test_get_kpi_data_uses_explicit_softdent_ar_when_present(monkeypatch):
    monkeypatch.setattr(
        services,
        "build_softdent_snapshot",
        lambda: {
            "available": True,
            "period": "2026-06",
            "provider_count": 1,
            "totals": {"production": 5000.0, "collections": 1000.0},
        },
    )
    monkeypatch.setattr(
        services,
        "load_softdent_ar_rows",
        lambda: [
            {
                "total_ar": 4321.5,
                "current_balance": 1000.0,
                "balance_30": 500.0,
                "balance_60": 0.0,
                "balance_90": 0.0,
            }
        ],
    )

    payload = services.get_kpi_data()

    assert _kpi_value(payload, "ar") == 4321.5


def test_get_kpi_data_sparse_snapshot_keeps_ar_unavailable(monkeypatch):
    monkeypatch.setattr(
        services,
        "build_softdent_snapshot",
        lambda: {
            "available": True,
        },
    )
    monkeypatch.setattr(services, "load_softdent_ar_rows", lambda: [])

    payload = services.get_kpi_data()

    assert payload == [
        {"name": "production", "value": 0.0},
        {"name": "collections", "value": 0.0},
        {"name": "ar", "value": None},
        {"name": "collection_ratio", "value": 0.0},
        {"name": "provider_count", "value": 0},
        {"name": "period", "value": "unknown"},
    ]
