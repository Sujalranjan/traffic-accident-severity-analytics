"""Reusable dashboard analytics for accident severity views."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


REQUIRED_COLUMNS = {"accident_id", "accident_date", "hour", "weekday", "severity"}
OPTIONAL_COLUMNS = {
    "weather_condition",
    "road_type",
    "road_surface_condition",
    "casualty_count",
    "vehicle_count",
    "latitude",
    "longitude",
}
SEVERITY_ORDER = ["Fatal", "Serious", "Slight", "Unknown"]
WEEKDAY_ORDER = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
SEVERITY_LABELS = {
    "1": "Fatal",
    "2": "Serious",
    "3": "Slight",
    "fatal": "Fatal",
    "serious": "Serious",
    "slight": "Slight",
}


@dataclass(frozen=True)
class DataContractStatus:
    """Validation result for the dashboard analytics input contract."""

    is_valid: bool
    missing_required: tuple[str, ...]
    available_optional: tuple[str, ...]


def validate_contract(data: pd.DataFrame) -> DataContractStatus:
    """Check whether a dataframe satisfies the dashboard analytics contract."""

    missing = tuple(sorted(REQUIRED_COLUMNS.difference(data.columns)))
    available_optional = tuple(sorted(OPTIONAL_COLUMNS.intersection(data.columns)))
    return DataContractStatus(
        is_valid=not missing,
        missing_required=missing,
        available_optional=available_optional,
    )


def prepare_dashboard_data(data: pd.DataFrame) -> pd.DataFrame:
    """Normalize mart-ready data for charts without mutating source records."""

    prepared = data.copy()
    status = validate_contract(prepared)
    if not status.is_valid:
        missing = ", ".join(status.missing_required)
        raise ValueError(f"Missing required dashboard analytics columns: {missing}")

    prepared["accident_date"] = pd.to_datetime(prepared["accident_date"], errors="coerce")
    prepared["hour"] = pd.to_numeric(prepared["hour"], errors="coerce").astype("Int64")
    prepared["severity"] = prepared["severity"].map(_normalize_severity)
    prepared["weekday"] = prepared["weekday"].map(_normalize_weekday)

    for column in ("casualty_count", "vehicle_count"):
        if column in prepared.columns:
            prepared[column] = pd.to_numeric(prepared[column], errors="coerce").fillna(0)

    for column in ("weather_condition", "road_type", "road_surface_condition"):
        if column in prepared.columns:
            prepared[column] = prepared[column].fillna("Unknown").astype(str).str.strip()
            prepared.loc[prepared[column].eq(""), column] = "Unknown"

    return prepared


def filter_dashboard_data(
    data: pd.DataFrame,
    *,
    severity: list[str] | None = None,
    weather: list[str] | None = None,
    road_type: list[str] | None = None,
    start_date: pd.Timestamp | None = None,
    end_date: pd.Timestamp | None = None,
    hour_range: tuple[int, int] | None = None,
) -> pd.DataFrame:
    """Apply dashboard filters while gracefully ignoring unavailable dimensions."""

    filtered = data.copy()

    if severity:
        filtered = filtered[filtered["severity"].isin(severity)]
    if weather and "weather_condition" in filtered.columns:
        filtered = filtered[filtered["weather_condition"].isin(weather)]
    if road_type and "road_type" in filtered.columns:
        filtered = filtered[filtered["road_type"].isin(road_type)]
    if start_date is not None:
        filtered = filtered[filtered["accident_date"] >= pd.Timestamp(start_date)]
    if end_date is not None:
        filtered = filtered[filtered["accident_date"] <= pd.Timestamp(end_date)]
    if hour_range is not None:
        start_hour, end_hour = hour_range
        filtered = filtered[filtered["hour"].between(start_hour, end_hour)]

    return filtered


def compute_kpis(data: pd.DataFrame) -> dict[str, float | int]:
    """Compute top-level dashboard KPI values."""

    total_accidents = int(data["accident_id"].nunique())
    severity_counts = data["severity"].value_counts()
    total_casualties = (
        int(data["casualty_count"].sum()) if "casualty_count" in data.columns else 0
    )

    return {
        "total_accidents": total_accidents,
        "fatal_accidents": int(severity_counts.get("Fatal", 0)),
        "serious_accidents": int(severity_counts.get("Serious", 0)),
        "slight_accidents": int(severity_counts.get("Slight", 0)),
        "total_casualties": total_casualties,
        "avg_casualties_per_accident": round(
            total_casualties / total_accidents, 2
        )
        if total_accidents
        else 0,
    }


def severity_distribution(data: pd.DataFrame) -> pd.DataFrame:
    """Return accident counts by severity."""

    return _count_by_column(data, "severity", order=SEVERITY_ORDER)


def accidents_by_hour(data: pd.DataFrame) -> pd.DataFrame:
    """Return accident counts for each hour of day."""

    counts = _count_by_column(data.dropna(subset=["hour"]), "hour")
    if counts.empty:
        return pd.DataFrame({"hour": range(24), "accidents": [0] * 24})
    all_hours = pd.DataFrame({"hour": range(24)})
    return all_hours.merge(counts, on="hour", how="left").fillna({"accidents": 0})


def accidents_by_weekday(data: pd.DataFrame) -> pd.DataFrame:
    """Return accident counts by weekday in calendar order."""

    return _count_by_column(data, "weekday", order=WEEKDAY_ORDER)


def breakdown_by_dimension(data: pd.DataFrame, column: str, *, limit: int = 10) -> pd.DataFrame:
    """Return a ranked count breakdown for an optional dashboard dimension."""

    if column not in data.columns:
        return pd.DataFrame({column: [], "accidents": []})
    grouped = _count_by_column(data, column)
    return grouped.head(limit)


def casualty_rate_by_dimension(
    data: pd.DataFrame, column: str, *, limit: int = 10
) -> pd.DataFrame:
    """Return accident count, casualties, and average casualties for a dimension."""

    if column not in data.columns or "casualty_count" not in data.columns:
        return pd.DataFrame(
            {column: [], "accidents": [], "casualties": [], "avg_casualties": []}
        )

    grouped = (
        data.groupby(column, dropna=False)
        .agg(accidents=("accident_id", "nunique"), casualties=("casualty_count", "sum"))
        .reset_index()
    )
    grouped["avg_casualties"] = (
        grouped["casualties"] / grouped["accidents"].replace(0, pd.NA)
    ).fillna(0)
    return grouped.sort_values(
        ["avg_casualties", "accidents"], ascending=[False, False]
    ).head(limit)


def available_filter_values(data: pd.DataFrame, column: str) -> list[str]:
    """Return sorted non-empty values for a dashboard filter."""

    if column not in data.columns:
        return []
    values = data[column].dropna().astype(str).str.strip()
    return sorted(value for value in values.unique() if value)


def _count_by_column(
    data: pd.DataFrame, column: str, *, order: list[str] | None = None
) -> pd.DataFrame:
    counts = (
        data.groupby(column, dropna=False)["accident_id"]
        .nunique()
        .reset_index(name="accidents")
    )

    if order is None:
        return counts.sort_values("accidents", ascending=False).reset_index(drop=True)

    order_frame = pd.DataFrame({column: order})
    return (
        order_frame.merge(counts, on=column, how="left")
        .fillna({"accidents": 0})
        .astype({"accidents": int})
    )


def _normalize_severity(value: object) -> str:
    if pd.isna(value):
        return "Unknown"
    normalized = str(value).strip()
    return SEVERITY_LABELS.get(normalized.lower(), normalized.title() or "Unknown")


def _normalize_weekday(value: object) -> str:
    if pd.isna(value):
        return "Unknown"
    normalized = str(value).strip()
    if normalized.isdigit():
        index = int(normalized)
        if 1 <= index <= 7:
            return WEEKDAY_ORDER[index - 1]
    return normalized.title() or "Unknown"
