"""
Data quality checks for cleaned traffic accident datasets.

This module applies validation rules to cleaned DataFrames.
It does not modify or delete records.
"""

from pathlib import Path

import pandas as pd

from src.validation.validation_rules import (
    COLLISION_RULES,
    VEHICLE_RULES,
    CASUALTY_RULES,
    VALID_COLLISION_SEVERITIES,
    VALID_CASUALTY_SEVERITIES,
    LATITUDE_MIN,
    LATITUDE_MAX,
    LONGITUDE_MIN,
    LONGITUDE_MAX,
    MIN_NON_NEGATIVE_VALUE,
    MIN_REFERENCE_VALUE,
)


# ---------------------------------------------------------
# Generic helper
# ---------------------------------------------------------

def check_column_exists(df, column):
    """Return True if the required column exists."""
    return column in df.columns


# ---------------------------------------------------------
# Collision quality checks
# ---------------------------------------------------------

def validate_collisions(df):
    """
    Validate cleaned collision records.

    Returns:
        DataFrame containing one boolean column per validation rule.
    """

    results = pd.DataFrame(index=df.index)

    # Collision ID
    results["collision_index_not_null"] = (
        df["collision_index"].notna()
        & df["collision_index"].astype(str).str.strip().ne("")
    )

    # Latitude
    results["latitude_valid"] = (
        df["latitude"].notna()
        & df["latitude"].between(
            LATITUDE_MIN,
            LATITUDE_MAX,
        )
    )

    # Longitude
    results["longitude_valid"] = (
        df["longitude"].notna()
        & df["longitude"].between(
            LONGITUDE_MIN,
            LONGITUDE_MAX,
        )
    )

    # Date
    results["date_valid"] = (
        pd.to_datetime(
            df["date"],
            errors="coerce",
        ).notna()
    )

    # Collision severity
    results["severity_valid"] = (
        df["collision_severity"].isin(
            VALID_COLLISION_SEVERITIES
        )
    )

    # Number of vehicles
    results["number_of_vehicles_valid"] = (
        df["number_of_vehicles"].notna()
        & (
            df["number_of_vehicles"]
            >= MIN_NON_NEGATIVE_VALUE
        )
    )

    # Number of casualties
    results["number_of_casualties_valid"] = (
        df["number_of_casualties"].notna()
        & (
            df["number_of_casualties"]
            >= MIN_NON_NEGATIVE_VALUE
        )
    )

    return results


# ---------------------------------------------------------
# Vehicle quality checks
# ---------------------------------------------------------

def validate_vehicles(df):
    """
    Validate cleaned vehicle records.
    """

    results = pd.DataFrame(index=df.index)

    # Collision ID
    results["collision_index_not_null"] = (
        df["collision_index"].notna()
        & df["collision_index"].astype(str).str.strip().ne("")
    )

    # Vehicle reference
    results["vehicle_reference_valid"] = (
        df["vehicle_reference"].notna()
        & (
            df["vehicle_reference"]
            >= MIN_REFERENCE_VALUE
        )
    )

    # Driver age
    # Missing age is allowed because it can represent
    # unavailable source information.
    results["age_of_driver_valid"] = (
        df["age_of_driver"].isna()
        | (
            df["age_of_driver"]
            >= MIN_NON_NEGATIVE_VALUE
        )
    )

    # Vehicle age
    results["age_of_vehicle_valid"] = (
        df["age_of_vehicle"].isna()
        | (
            df["age_of_vehicle"]
            >= MIN_NON_NEGATIVE_VALUE
        )
    )

    return results


# ---------------------------------------------------------
# Casualty quality checks
# ---------------------------------------------------------

def validate_casualties(df):
    """
    Validate cleaned casualty records.
    """

    results = pd.DataFrame(index=df.index)

    # Collision ID
    results["collision_index_not_null"] = (
        df["collision_index"].notna()
        & df["collision_index"].astype(str).str.strip().ne("")
    )

    # Casualty reference
    results["casualty_reference_valid"] = (
        df["casualty_reference"].notna()
        & (
            df["casualty_reference"]
            >= MIN_REFERENCE_VALUE
        )
    )

    # Casualty age
    results["age_of_casualty_valid"] = (
        df["age_of_casualty"].isna()
        | (
            df["age_of_casualty"]
            >= MIN_NON_NEGATIVE_VALUE
        )
    )

    # Casualty severity
    results["casualty_severity_valid"] = (
        df["casualty_severity"].isin(
            VALID_CASUALTY_SEVERITIES
        )
    )

    return results


# ---------------------------------------------------------
# Quality summary
# ---------------------------------------------------------

def generate_quality_summary(results):
    """
    Generate a summary of validation results.
    """

    summary = []

    total_records = len(results)

    for rule in results.columns:

        failed = (~results[rule]).sum()
        passed = results[rule].sum()

        summary.append(
            {
                "rule": rule,
                "total_records": total_records,
                "passed": int(passed),
                "failed": int(failed),
                "pass_rate_percent": round(
                    (passed / total_records * 100)
                    if total_records > 0
                    else 0,
                    2,
                ),
            }
        )

    return pd.DataFrame(summary)


# ---------------------------------------------------------
# Overall validity
# ---------------------------------------------------------

def get_valid_records(results):
    """
    A record is valid only when it passes every rule.
    """

    return results.all(axis=1)


def get_rejected_records(results):
    """
    Return a boolean mask identifying records
    that failed at least one validation rule.
    """

    return ~get_valid_records(results)