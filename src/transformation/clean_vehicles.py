from pathlib import Path

import pandas as pd

from standardize import (
    standardize_missing_codes,
    standardize_vehicle_categories,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "vehicles"
    / "dft-road-casualty-statistics-vehicle-last-5-years.csv"
)

STAGING_DIR = PROJECT_ROOT / "data" / "staging"

OUTPUT_FILE = STAGING_DIR / "vehicles_cleaned.csv"


def clean_vehicle_data():

    print("Loading vehicle dataset...")

    df = pd.read_csv(
        RAW_FILE,
        low_memory=False,
    )

    original_rows = len(df)

    print(f"Rows loaded: {original_rows:,}")

    # -----------------------------
    # Duplicate check
    # -----------------------------

    duplicate_count = df.duplicated(
        subset=["collision_index", "vehicle_reference"]
    ).sum()

    print(f"Duplicate vehicle records found: {duplicate_count:,}")

    df = df.drop_duplicates(
        subset=["collision_index", "vehicle_reference"],
        keep="first",
    )

    # -----------------------------
    # Convert identifier columns
    # -----------------------------

    df["collision_index"] = df["collision_index"].astype("string")

    # -----------------------------
    # Convert numeric fields
    # -----------------------------

    numeric_columns = [
        "collision_year",
        "vehicle_reference",
        "age_of_driver",
        "age_of_vehicle",
        "engine_capacity_cc",
        "driver_imd_decile",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    # -----------------------------
    # Replace DfT missing codes
    # -----------------------------

    missing_code_columns = [
        "vehicle_type",
        "sex_of_driver",
        "age_of_driver",
        "age_band_of_driver",
        "propulsion_code",
        "age_of_vehicle",
    ]

    for column in missing_code_columns:
        if column in df.columns:
            df[column] = df[column].replace(-1, pd.NA)

    # -----------------------------
    # Standardize categorical fields
    # -----------------------------

    df = standardize_vehicle_categories(df)

    # -----------------------------
    # Save cleaned dataset
    # -----------------------------

    STAGING_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\nVehicle cleaning completed successfully.")

    print(f"Original rows : {original_rows:,}")
    print(f"Final rows    : {len(df):,}")
    print(
        f"Rows removed  : "
        f"{original_rows - len(df):,}"
    )

    print("\nOutput file:")
    print(OUTPUT_FILE)

    return df


if __name__ == "__main__":
    clean_vehicle_data()