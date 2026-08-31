import pandas as pd
import pytest

from dashboard.analytics import (
    accidents_by_hour,
    accidents_by_weekday,
    breakdown_by_dimension,
    casualty_rate_by_dimension,
    compute_kpis,
    filter_dashboard_data,
    prepare_dashboard_data,
    severity_distribution,
    validate_contract,
)


def sample_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "accident_id": ["A1", "A2", "A3", "A4"],
            "accident_date": ["2023-01-02", "2023-01-02", "2023-01-03", "2023-01-04"],
            "hour": [8, 8, 17, 21],
            "weekday": ["Monday", "Monday", "Tuesday", "Wednesday"],
            "severity": ["1", "Serious", "3", "Slight"],
            "weather_condition": ["Rain", "Clear", "Rain", "Fog"],
            "road_type": ["A road", "B road", "A road", "Motorway"],
            "casualty_count": [2, 1, 3, 1],
        }
    )


def test_validate_contract_reports_missing_required_columns() -> None:
    status = validate_contract(pd.DataFrame({"accident_id": ["A1"]}))

    assert not status.is_valid
    assert status.missing_required == ("accident_date", "hour", "severity", "weekday")


def test_prepare_dashboard_data_normalizes_types_and_severity() -> None:
    prepared = prepare_dashboard_data(sample_data())

    assert str(prepared["accident_date"].dtype).startswith("datetime64")
    assert prepared["severity"].tolist() == ["Fatal", "Serious", "Slight", "Slight"]
    assert prepared["weekday"].tolist() == ["Monday", "Monday", "Tuesday", "Wednesday"]


def test_prepare_dashboard_data_raises_for_missing_required_columns() -> None:
    with pytest.raises(ValueError, match="Missing required dashboard analytics columns"):
        prepare_dashboard_data(pd.DataFrame({"accident_id": ["A1"]}))


def test_compute_kpis_counts_accidents_and_casualties() -> None:
    prepared = prepare_dashboard_data(sample_data())

    metrics = compute_kpis(prepared)

    assert metrics["total_accidents"] == 4
    assert metrics["fatal_accidents"] == 1
    assert metrics["serious_accidents"] == 1
    assert metrics["slight_accidents"] == 2
    assert metrics["total_casualties"] == 7
    assert metrics["avg_casualties_per_accident"] == 1.75


def test_severity_distribution_uses_expected_order() -> None:
    prepared = prepare_dashboard_data(sample_data())

    result = severity_distribution(prepared)

    assert result["severity"].tolist() == ["Fatal", "Serious", "Slight", "Unknown"]
    assert result["accidents"].tolist() == [1, 1, 2, 0]


def test_accidents_by_hour_includes_all_hours() -> None:
    prepared = prepare_dashboard_data(sample_data())

    result = accidents_by_hour(prepared)

    assert len(result) == 24
    assert result.loc[result["hour"].eq(8), "accidents"].item() == 2
    assert result.loc[result["hour"].eq(17), "accidents"].item() == 1


def test_accidents_by_weekday_uses_calendar_order() -> None:
    prepared = prepare_dashboard_data(sample_data())

    result = accidents_by_weekday(prepared)

    assert result["weekday"].head(3).tolist() == ["Monday", "Tuesday", "Wednesday"]
    assert result["accidents"].head(3).tolist() == [2, 1, 1]


def test_breakdown_and_casualty_rate_by_dimension() -> None:
    prepared = prepare_dashboard_data(sample_data())

    weather = breakdown_by_dimension(prepared, "weather_condition")
    road_rates = casualty_rate_by_dimension(prepared, "road_type")

    assert weather.iloc[0]["weather_condition"] == "Rain"
    assert weather.iloc[0]["accidents"] == 2
    assert road_rates.iloc[0]["road_type"] == "A road"
    assert road_rates.iloc[0]["avg_casualties"] == 2.5


def test_filter_dashboard_data_applies_available_dimensions() -> None:
    prepared = prepare_dashboard_data(sample_data())

    filtered = filter_dashboard_data(
        prepared,
        severity=["Slight"],
        weather=["Rain"],
        hour_range=(0, 18),
    )

    assert filtered["accident_id"].tolist() == ["A3"]
