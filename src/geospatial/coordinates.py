"""
Coordinate validation for UK DfT collision records.

Validates latitude and longitude without removing source rows.
Rejected rows are flagged with a clear reason for downstream logging.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

LATITUDE_MIN = -90.0
LATITUDE_MAX = 90.0
LONGITUDE_MIN = -180.0
LONGITUDE_MAX = 180.0

REQUIRED_COLUMNS = ("collision_index", "latitude", "longitude")


@dataclass(frozen=True)
class CoordinateValidationResult:
    """Validation outcome for a single collision record."""

    collision_index: str
    latitude: float | None
    longitude: float | None
    is_valid: bool
    rejection_reason: str | None


def prepare_coordinate_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Safely coerce latitude and longitude to numeric values.

    Source rows are preserved; invalid strings become NaN.
    """
    if "collision_index" not in df.columns:
        raise ValueError("DataFrame must contain a 'collision_index' column.")

    prepared = df.copy()
    prepared["latitude"] = pd.to_numeric(prepared["latitude"], errors="coerce")
    prepared["longitude"] = pd.to_numeric(prepared["longitude"], errors="coerce")
    return prepared


def validate_coordinates(row: pd.Series) -> CoordinateValidationResult:
    """
    Validate latitude and longitude for one collision record.

    Returns a result object instead of dropping or mutating the source row.
    """
    collision_index = str(row["collision_index"])
    latitude = row.get("latitude")
    longitude = row.get("longitude")

    if pd.isna(latitude) or pd.isna(longitude):
        return CoordinateValidationResult(
            collision_index=collision_index,
            latitude=None if pd.isna(latitude) else float(latitude),
            longitude=None if pd.isna(longitude) else float(longitude),
            is_valid=False,
            rejection_reason="missing_coordinates",
        )

    latitude = float(latitude)
    longitude = float(longitude)

    if not LATITUDE_MIN <= latitude <= LATITUDE_MAX:
        return CoordinateValidationResult(
            collision_index=collision_index,
            latitude=latitude,
            longitude=longitude,
            is_valid=False,
            rejection_reason="latitude_out_of_range",
        )

    if not LONGITUDE_MIN <= longitude <= LONGITUDE_MAX:
        return CoordinateValidationResult(
            collision_index=collision_index,
            latitude=latitude,
            longitude=longitude,
            is_valid=False,
            rejection_reason="longitude_out_of_range",
        )

    return CoordinateValidationResult(
        collision_index=collision_index,
        latitude=latitude,
        longitude=longitude,
        is_valid=True,
        rejection_reason=None,
    )


def validate_coordinates_batch(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split a collision DataFrame into valid and rejected coordinate sets.

    The original DataFrame is not modified. Rejected rows include
    ``rejection_reason`` and are retained for audit logging.
    """
    prepared = prepare_coordinate_columns(df)
    valid_rows: list[dict] = []
    rejected_rows: list[dict] = []

    for _, row in prepared.iterrows():
        result = validate_coordinates(row)
        row_dict = row.to_dict()
        row_dict["is_valid_coordinate"] = result.is_valid
        row_dict["rejection_reason"] = result.rejection_reason

        if result.is_valid:
            valid_rows.append(row_dict)
        else:
            rejected_rows.append(row_dict)

    valid_df = pd.DataFrame(valid_rows) if valid_rows else prepared.iloc[0:0].copy()
    rejected_df = (
        pd.DataFrame(rejected_rows) if rejected_rows else prepared.iloc[0:0].copy()
    )
    return valid_df, rejected_df


def summarize_coordinate_validation(
    df: pd.DataFrame,
) -> dict[str, int | dict[str, int]]:
    """Return counts useful for pipeline logging and Airflow tasks."""
    valid_df, rejected_df = validate_coordinates_batch(df)
    reason_counts: dict[str, int] = {}

    if not rejected_df.empty and "rejection_reason" in rejected_df.columns:
        reason_counts = (
            rejected_df["rejection_reason"].value_counts().astype(int).to_dict()
        )

    return {
        "rows_processed": len(df),
        "valid_rows": len(valid_df),
        "rejected_rows": len(rejected_df),
        "rejection_counts": reason_counts,
    }
