from pathlib import Path

import pandas as pd

from standardize import (
    standardize_categories,
    standardize_coordinates,
    standardize_date,
    standardize_missing_codes,
    standardize_time,
)


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "collisions"
    / "dft-road-casualty-statistics-collision-last-5-years.csv"
)

STAGING_DIR = PROJECT_ROOT / "data" / "staging"

OUTPUT_FILE = STAGING_DIR / "collisions_cleaned.csv"


# ---------------------------------------------------------
# Main cleaning function
# ---------------------------------------------------------

def clean_collision_data() -> pd.DataFrame:

    print("Loading collision dataset...")

    df = pd.read_csv(
        RAW_FILE,
        low_memory=False
    )

    original_rows = len(df)

    print(f"Rows loaded: {original_rows:,}")

    # -----------------------------------------------------
    # 1. Remove duplicate collision records
    # -----------------------------------------------------

    duplicate_count = df.duplicated(
        subset=["collision_index"]
    ).sum()

    print(f"Duplicate collisions found: {duplicate_count:,}")

    df = df.drop_duplicates(
        subset=["collision_index"],
        keep="first"
    )

    # -----------------------------------------------------
    # 2. Standardize date
    # -----------------------------------------------------

    df = standardize_date(df)

    invalid_dates = df["date"].isna().sum()

    print(f"Invalid dates after conversion: {invalid_dates:,}")

    # -----------------------------------------------------
    # 3. Standardize time
    # -----------------------------------------------------

    df = standardize_time(df)

    invalid_times = df["time"].isna().sum()

    print(f"Invalid times after conversion: {invalid_times:,}")

    # -----------------------------------------------------
    # 4. Clean latitude and longitude
    # -----------------------------------------------------

    df = standardize_coordinates(df)

    missing_coordinates = (
        df["latitude"].isna()
        | df["longitude"].isna()
    ).sum()

    print(
        f"Records with missing/invalid coordinates: "
        f"{missing_coordinates:,}"
    )

    # -----------------------------------------------------
    # 5. Convert DfT missing codes
    # -----------------------------------------------------

    df = standardize_missing_codes(df)

    # -----------------------------------------------------
    # 6. Convert categorical codes to readable labels
    # -----------------------------------------------------

    df = standardize_categories(df)

    # -----------------------------------------------------
    # 7. Standardize numeric datatypes
    # -----------------------------------------------------

    numeric_columns = [
        "collision_year",
        "number_of_vehicles",
        "number_of_casualties",
        "speed_limit",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # -----------------------------------------------------
    # 8. Save cleaned dataset
    # -----------------------------------------------------

    STAGING_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    print("\nCleaning completed successfully.")

    print(f"Original rows : {original_rows:,}")
    print(f"Final rows    : {len(df):,}")
    print(f"Rows removed  : {original_rows - len(df):,}")

    print(f"\nOutput file:")
    print(OUTPUT_FILE)

    return df


# ---------------------------------------------------------
# Script entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    clean_collision_data()