"""Streamlit page implementation for accident severity insights."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.analytics import (
    accidents_by_hour,
    accidents_by_weekday,
    available_filter_values,
    breakdown_by_dimension,
    casualty_rate_by_dimension,
    compute_kpis,
    filter_dashboard_data,
    prepare_dashboard_data,
    severity_distribution,
    validate_contract,
)
from dashboard.components.charts import (
    casualty_rate_bar,
    dimension_bar,
    hourly_line,
    severity_bar,
    weekday_bar,
)
from dashboard.components.kpi_cards import render_kpi_cards
from dashboard.data_access import load_dashboard_data


def render_page() -> None:
    st.set_page_config(
        page_title="Traffic Accident Analytics",
        layout="wide",
    )
    st.title("Traffic Accident Severity Analytics")

    source = st.sidebar.radio(
        "Data source",
        ["auto", "csv", "database"],
        format_func={"auto": "Auto", "csv": "CSV", "database": "PostgreSQL"}.get,
    )

    try:
        raw_data, source_label = load_dashboard_data(source)  # type: ignore[arg-type]
    except Exception as exc:
        _render_missing_data_state(exc)
        return

    contract = validate_contract(raw_data)
    if not contract.is_valid:
        st.error(
            "Dashboard analytics data is missing required columns: "
            + ", ".join(contract.missing_required)
        )
        st.stop()

    data = prepare_dashboard_data(raw_data)
    st.caption(f"Loaded from {source_label}")

    filtered = _render_filters(data)
    if filtered.empty:
        st.info("No accidents match the selected filters.")
        return

    render_kpi_cards(compute_kpis(filtered))
    st.divider()

    top_left, top_right = st.columns(2)
    with top_left:
        st.subheader("Severity Distribution")
        st.plotly_chart(
            severity_bar(severity_distribution(filtered)),
            width="stretch",
        )
    with top_right:
        st.subheader("Accidents by Hour")
        st.plotly_chart(hourly_line(accidents_by_hour(filtered)), width="stretch")

    bottom_left, bottom_right = st.columns(2)
    with bottom_left:
        st.subheader("Accidents by Weekday")
        st.plotly_chart(
            weekday_bar(accidents_by_weekday(filtered)),
            width="stretch",
        )
    with bottom_right:
        _render_optional_breakdown(
            filtered,
            column="weather_condition",
            label="Weather condition",
            title="Weather Impact",
        )

    extra_left, extra_right = st.columns(2)
    with extra_left:
        _render_optional_breakdown(
            filtered,
            column="road_type",
            label="Road type",
            title="Road Type Breakdown",
        )
    with extra_right:
        _render_casualty_rate(filtered)


def _render_filters(data: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")

    severity = st.sidebar.multiselect(
        "Severity",
        options=available_filter_values(data, "severity"),
        default=available_filter_values(data, "severity"),
    )

    weather = st.sidebar.multiselect(
        "Weather",
        options=available_filter_values(data, "weather_condition"),
        default=available_filter_values(data, "weather_condition"),
        disabled="weather_condition" not in data.columns,
    )

    road_type = st.sidebar.multiselect(
        "Road type",
        options=available_filter_values(data, "road_type"),
        default=available_filter_values(data, "road_type"),
        disabled="road_type" not in data.columns,
    )

    min_date = data["accident_date"].dropna().min()
    max_date = data["accident_date"].dropna().max()
    if pd.notna(min_date) and pd.notna(max_date):
        date_range = st.sidebar.date_input(
            "Date range",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date(),
        )
    else:
        date_range = None

    hour_range = st.sidebar.slider("Hour range", 0, 23, (0, 23))

    start_date = end_date = None
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])

    return filter_dashboard_data(
        data,
        severity=severity,
        weather=weather,
        road_type=road_type,
        start_date=start_date,
        end_date=end_date,
        hour_range=hour_range,
    )


def _render_optional_breakdown(
    data: pd.DataFrame, *, column: str, label: str, title: str
) -> None:
    st.subheader(title)
    breakdown = breakdown_by_dimension(data, column)
    if breakdown.empty:
        st.info(f"{label} is not available in the dashboard analytics dataset.")
        return
    st.plotly_chart(
        dimension_bar(breakdown, column, label),
        width="stretch",
    )


def _render_casualty_rate(data: pd.DataFrame) -> None:
    st.subheader("Casualty Rate by Road Type")
    rates = casualty_rate_by_dimension(data, "road_type")
    if rates.empty:
        st.info("Casualty counts or road type data are not available yet.")
        return
    st.plotly_chart(
        casualty_rate_bar(rates, "road_type", "Road type"),
        width="stretch",
    )


def _render_missing_data_state(error: Exception) -> None:
    st.title("Traffic Accident Severity Analytics")
    st.warning(str(error))
    st.markdown(
        """
        Expected dashboard analytics input:

        - Required: `accident_id`, `accident_date`, `hour`, `weekday`, `severity`
        - Optional: `weather_condition`, `road_type`, `road_surface_condition`,
          `casualty_count`, `vehicle_count`, `latitude`, `longitude`

        Place the mart export at `data/processed/dashboard_analytics.csv`, or set
        `DATABASE_URL` and `DASHBOARD_ANALYTICS_TABLE` for PostgreSQL.
        """
    )
