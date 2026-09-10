from pathlib import Path

import pandas as pd

from standardize import (
    standardize_casualty_categories,
    standardize_missing_codes,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "casualties"
    / "dft-road-casualty-statistics-casualty-last-5-years.csv"
)

STAGING_DIR = PROJECT_ROOT / "data" / "staging"

OUTPUT_FILE = STAGING_DIR / "casualties_cleaned.csv"


def clean_casualty_data():

    print("Loading casualty dataset...")

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
        subset=[
            "collision_index",
            "casualty_reference",
        ]
    ).sum()

    print(
        f"Duplicate casualty records found: "
        f"{duplicate_count:,}"
    )

    df = df.drop_duplicates(
        subset=[
            "collision_index",
            "casualty_reference",
        ],
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
        "casualty_reference",
        "age_of_casualty",
        "casualty_imd_decile",
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

    df = standardize_missing_codes(df)

    # -----------------------------
    # Standardize categorical fields
    # -----------------------------

    df = standardize_casualty_categories(df)

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

    print("\nCasualty cleaning completed successfully.")

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
    clean_casualty_data()